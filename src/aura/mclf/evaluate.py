"""Pure L0 auditing of declarations; never invokes a solver or reads artifacts."""

from __future__ import annotations

import json
import math
from itertools import islice

from jsonschema import Draft202012Validator

from aura.errors import InvalidInputError
from aura.schema import validate_document
from aura.schema.definitions import document_schema
from aura.schema.quantities import MAX_BYTES, check_json_tree, pointer

from .reports import AuditReport, Check, Finding
from .rules import RULES

_SCHEMAS = {
    kind: Draft202012Validator(document_schema(kind))
    for kind in ("scenario", "run_manifest", "field_result", "force_result")
}


def _route(path: str, validator: str = "", code: str = "") -> str:
    parts = path.split("/")
    if validator == "required":
        return "R-002"
    if code == "NONFINITE":
        return "R-004"
    if "unit" in parts:
        return "R-003"
    if any(name in parts for name in ("conventions", "amplitude_convention", "phasor_convention")):
        return "R-007"
    if validator in ("minItems", "maxItems") or any(
        name in parts
        for name in (
            "frame",
            "shape",
            "orientation",
            "normal",
            "coordinates",
            "pressure",
            "velocity",
        )
    ):
        return "R-006"
    if validator in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
        return "R-005"
    if code == "INCONSISTENT":
        if any(name in parts for name in ("elements", "bodies", "patch_sha256")) and not any(
            name in parts for name in ("pressure_amplitude", "position")
        ):
            return "R-008"
        return "R-005"
    return "R-001"


def evaluate_scenario(
    scenario: dict,
    *,
    report_id: str,
    run_id: str,
    stage: str,
    result: dict | None = None,
    manifest: dict | None = None,
) -> AuditReport:
    """Audit metadata with explicit stage/identity. All model coverage is unknown today."""
    if stage not in ("pre", "post"):
        raise InvalidInputError("AUDIT_STAGE", "/stage", "Expected pre or post.")
    findings = {rule.id: [] for rule in RULES}
    blocked: set[str] = set()

    def add(rule, code, path, message, verdict="INVALIDATED"):
        if len(path) > 512:
            path = ""
            message = "Diagnostic path exceeds 512 characters. " + message
        if len(message) > 512:
            message = message[:512] + " [truncated]"
        finding = Finding(verdict, code, path, message)
        if finding in findings[rule]:
            return
        if len(findings[rule]) >= 64:
            # Fail closed if diagnostic volume prevents a complete report.
            limit = Finding("INVALIDATED", "AUDIT_LIMIT", "", "More than 64 findings for one rule.")
            findings[rule][-1] = limit
            return
        findings[rule].append(finding)

    def inspect(data, kind, base):
        try:
            check_json_tree(data)
        except InvalidInputError as exc:
            add(_route(exc.path, code=exc.code), exc.code, base + exc.path, exc.message)
            blocked.add(base)
            return False
        if type(data) is not dict:
            add("R-001", "INPUT_TYPE", base, "Expected a document object.")
            blocked.add(base)
            return False
        if len(json.dumps(data, ensure_ascii=True, allow_nan=False).encode("utf-8")) > MAX_BYTES:
            add("R-001", "INPUT_LIMIT", base, "Document exceeds 1 MiB after JSON encoding.")
            blocked.add(base)
            return False
        errors = list(islice(_SCHEMAS[kind].iter_errors(data), 65))
        if len(errors) > 64:
            add(
                "R-001",
                "AUDIT_LIMIT",
                base,
                "Schema error count exceeds 64; diagnostic is incomplete.",
            )
            errors = errors[:64]
        for error in errors:
            path = base
            for part in error.absolute_path:
                path = pointer(path, part)
            if error.validator == "required":
                # jsonschema yields one error per missing field. Preserve each field.
                missing = [key for key in error.validator_value if key not in error.instance]
                for key in missing:
                    add("R-002", "MISSING_FIELD", pointer(path, key), "Required field is missing.")
            else:
                add(_route(path, error.validator), "SCHEMA_INVALID", path, error.message)
        if errors:
            blocked.add(base)
            return False
        # Preserve FND-02's date and semantic contracts too. The checks below collect
        # independent scenario cross-field findings instead of stopping at the first.
        try:
            validate_document(data)
        except InvalidInputError as exc:
            add(_route(exc.path, code=exc.code), exc.code, base + exc.path, exc.message)
        return True

    scenario_ok = inspect(scenario, "scenario", "/scenario")
    manifest_ok = manifest is not None and inspect(manifest, "run_manifest", "/manifest")
    result_ok = False
    if result is not None:
        kind = result.get("document_type") if type(result) is dict else None
        if type(kind) is str and kind in ("field_result", "force_result"):
            result_ok = inspect(result, kind, "/result")
        else:
            add(
                "R-001",
                "RESULT_TYPE",
                "/result/document_type",
                "Expected field_result or force_result.",
            )
            blocked.add("/result")

    if scenario_ok:

        def unique(items, path):
            ids = [item["id"] for item in items]
            if len(set(ids)) != len(ids):
                add("R-008", "DUPLICATE_ID", path, "Collection identifiers must be unique.")

        unique(scenario["bodies"], "/scenario/bodies")
        unique(scenario["sources"]["elements"], "/scenario/sources/elements")
        for index, body in enumerate(scenario["bodies"]):
            path = f"/scenario/bodies/{index}/initial_state/orientation/value"
            if abs(math.hypot(*body["initial_state"]["orientation"]["value"]) - 1) > 1e-12:
                add("R-006", "UNIT_NORM", path, "Quaternion norm violates CONV-1.0.")
        for index, source in enumerate(scenario["sources"]["elements"]):
            path = f"/scenario/sources/elements/{index}"
            if source["model"] != "ideal_spherical_wave" and abs(
                math.hypot(*source["normal"]["value"]) - 1
            ) > 1e-12:
                add(
                    "R-006",
                    "UNIT_NORM",
                    path + "/normal/value",
                    "Source normal is not unit length.",
                )
            if source["pressure_amplitude"]["value"] > source["pressure_limit"]["value"]:
                add(
                    "R-005",
                    "SOURCE_LIMIT",
                    path + "/pressure_amplitude",
                    "Declared pressure limit exceeded.",
                )
        window = scenario["target"]["window"]
        if window["end"]["value"] <= window["start"]["value"]:
            add("R-005", "TIME_WINDOW", "/scenario/target/window", "End must be after start.")
        origin, size = scenario["domain"]["origin"]["value"], scenario["domain"]["size"]["value"]
        upper = [float(a) + float(b) for a, b in zip(origin, size)]
        if not all(math.isfinite(b) and b > a for a, b in zip(origin, upper)):
            add(
                "R-005",
                "DOMAIN_RANGE",
                "/scenario/domain",
                "Domain bounds overflow or lose their extent.",
            )
        else:
            for index, body in enumerate(scenario["bodies"]):
                if not all(
                    a <= p <= b
                    for a, p, b in zip(origin, body["initial_state"]["position"]["value"], upper)
                ):
                    add(
                        "R-005",
                        "DOMAIN_CENTER",
                        f"/scenario/bodies/{index}/initial_state/position",
                        "Body center is outside the domain; full body clearance is not checked.",
                    )

    if manifest_ok:
        if manifest["id"] != run_id:
            add("R-008", "RUN_ID", "/manifest/id", "Manifest and audit run IDs differ.")
        if scenario_ok:
            if manifest["scenario_id"] != scenario["id"]:
                add(
                    "R-008", "SCENARIO_ID", "/manifest/scenario_id", "Manifest scenario ID differs."
                )
            if manifest["solver"] != scenario["solver"]:
                add(
                    "R-008",
                    "SOLVER_IDENTITY",
                    "/manifest/solver",
                    "Declared solver specifications differ.",
                )
        add(
            "R-008",
            "HASH_UNCHECKED",
            "/manifest",
            "Declared digests/source identities are not authenticated.",
            "INDETERMINATE",
        )
        if stage == "post" and manifest["execution_status"] != "completed":
            add(
                "R-010",
                "EXECUTION_INCOMPLETE",
                "/manifest/execution_status",
                "Execution is not completed.",
            )
    elif manifest is None:
        add(
            "R-008",
            "MANIFEST_ABSENT",
            "/manifest",
            "No cross-record source/configuration evidence supplied.",
            "INDETERMINATE",
        )

    add(
        "R-009",
        "MODEL_UNCOVERED",
        "/scenario/solver",
        "No reviewed scientific model capability is registered; geometry metadata grants no coverage.",
        "INDETERMINATE",
    )
    if result_ok:
        if result["run_id"] != run_id:
            add("R-008", "RUN_ID", "/result/run_id", "Result and audit run IDs differ.")
        if result["document_type"] == "field_result":
            add(
                "R-004",
                "EXTERNAL_SAMPLES_UNCHECKED",
                "/result",
                "External sample numbers have not been read.",
                "INDETERMINATE",
            )
            add(
                "R-010",
                "ARTIFACTS_UNCHECKED",
                "/result",
                "Array references do not establish output completeness.",
                "INDETERMINATE",
            )
            if scenario_ok:
                for key in ("model_id", "model_version"):
                    if result[key] != scenario["solver"][key]:
                        add(
                            "R-008",
                            "MODEL_IDENTITY",
                            f"/result/{key}",
                            "Field model differs from scenario solver.",
                        )
        else:
            if scenario_ok and result["body_id"] not in {body["id"] for body in scenario["bodies"]}:
                add("R-008", "BODY_ID", "/result/body_id", "Result names an absent body.")
            if result["validity"] != "ACCEPTED":
                add(
                    "R-010",
                    "INHERITED_VERDICT",
                    "/result/validity",
                    "Preserved supplied result limitation.",
                    result["validity"],
                )
    if stage == "post" and result is None:
        add("R-010", "RESULT_MISSING", "/result", "Post-audit requires a result.")
    elif result is not None and not result_ok:
        add(
            "R-010",
            "RESULT_INVALID",
            "/result",
            "Supplied result cannot satisfy its record contract.",
        )
    if stage == "pre" and result is not None:
        add("R-010", "STAGE_MISMATCH", "/result", "Use post stage when supplying a result.")
    elif stage == "pre":
        add(
            "R-010",
            "PRE_ONLY",
            "/result",
            "Pre-stage does not request outputs; no postcheck is claimed.",
            "ACCEPTED",
        )

    for rule in RULES:
        if blocked:
            add(
                rule.id,
                "CHECK_INCOMPLETE",
                "",
                "Malformed records prevent a complete check: " + ", ".join(sorted(blocked)),
                "INDETERMINATE",
            )
        if not findings[rule.id]:
            add(
                rule.id,
                "CHECK_PASSED",
                "",
                "Available declarations pass this rule's limited predicate.",
                "ACCEPTED",
            )
    return AuditReport(
        report_id, run_id, stage, tuple(Check(rule.id, tuple(findings[rule.id])) for rule in RULES)
    )
