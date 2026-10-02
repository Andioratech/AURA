"""Validated immutable snapshots, independent of scientific solver execution."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from jsonschema import Draft202012Validator, FormatChecker

from aura.errors import InvalidInputError

from .definitions import DEFINITIONS, VERSION, document_schema
from .quantities import MAX_BYTES, check_json_tree, pointer

_FORMATS = FormatChecker()


@_FORMATS.checks("date-time", raises=ValueError)
def _utc_timestamp(value: object) -> bool:
    # jsonschema's default date-time checker needs an optional dependency.
    # This contract is always checked, even in the minimal core installation.
    if not isinstance(value, str):
        return True  # The schema's type check supplies the type diagnostic.
    if not value.endswith("Z") or "T" not in value:
        return False
    datetime.fromisoformat(value[:-1] + "+00:00")
    return True


_VALIDATORS = {}
for _kind in DEFINITIONS:
    _schema = document_schema(_kind)
    Draft202012Validator.check_schema(_schema)
    _VALIDATORS[_kind] = Draft202012Validator(_schema, format_checker=_FORMATS)


def _require(condition: bool, path: str, message: str) -> None:
    if not condition:
        raise InvalidInputError("INCONSISTENT", path, message)


def _unit_vector(values: list, path: str) -> None:
    _require(abs(math.hypot(*values) - 1.0) <= 1e-12, path, "Expected unit norm within 1e-12.")


def _unique(items: list, path: str) -> None:
    ids = [item["id"] for item in items]
    _require(len(set(ids)) == len(ids), path, "Identifiers must be unique within this collection.")


def _window(data: dict, path: str) -> None:
    _require(data["end"]["value"] > data["start"]["value"], path, "End must be after start.")


def _cross_checks(kind: str, data: dict, path: str = "") -> None:
    if "provenance" in data:
        provenance = data["provenance"]
        _require(
            provenance["uncertainty_status"] != "reported"
            or provenance["uncertainty_reference"] is not None,
            path + "/provenance/uncertainty_reference",
            "Reported uncertainty needs a reference.",
        )
    if kind == "body":
        _unit_vector(
            data["initial_state"]["orientation"]["value"], path + "/initial_state/orientation/value"
        )
    elif kind == "transducer_array":
        _unique(data["elements"], path + "/elements")
        for index, element in enumerate(data["elements"]):
            base = f"{path}/elements/{index}"
            _unit_vector(element["normal"]["value"], base + "/normal/value")
            _require(
                element["pressure_amplitude"]["value"] <= element["pressure_limit"]["value"],
                base + "/pressure_amplitude",
                "Amplitude exceeds the declared source limit.",
            )
    elif kind == "scenario":
        _unique(data["bodies"], path + "/bodies")
        _cross_checks("medium", data["medium"], path + "/medium")
        _cross_checks("transducer_array", data["sources"], path + "/sources")
        _window(data["target"]["window"], path + "/target/window")
        for index, body in enumerate(data["bodies"]):
            _cross_checks("body", body, f"{path}/bodies/{index}")
        origin = data["domain"]["origin"]["value"]
        extent = data["domain"]["size"]["value"]
        upper = [float(a) + float(b) for a, b in zip(origin, extent)]
        _require(
            all(math.isfinite(v) and v > a for v, a in zip(upper, origin)),
            path + "/domain",
            "Domain bounds must remain finite and distinguishable.",
        )
        for index, body in enumerate(data["bodies"]):
            center = body["initial_state"]["position"]["value"]
            _require(
                all(a <= p <= b for a, p, b in zip(origin, center, upper)),
                f"{path}/bodies/{index}/initial_state/position",
                "Body center is outside domain.",
            )
    elif kind == "experiment":
        _window(data["primary_observable"]["window"], path + "/primary_observable/window")
    elif kind == "run_manifest":
        _require(
            data["source"]["dirty"] == (data["source"]["patch_sha256"] is not None),
            path + "/source/patch_sha256",
            "A dirty revision requires a patch digest; clean does not.",
        )
        failed = data["execution_status"] in ("failed", "aborted")
        _require(
            failed == (data["failure_code"] is not None),
            path + "/failure_code",
            "Failed or aborted runs require a failure code; other states use null.",
        )
        _require(
            data["execution_status"] != "completed" or bool(data["outputs"]),
            path + "/outputs",
            "Completed execution requires an output artifact reference.",
        )
    elif kind == "field_result":
        count = data["coordinates"]["shape"][0]
        for name, unit, shape, dtype in (
            ("coordinates", "m", [count, 3], "float64"),
            ("pressure", "Pa", [count], "complex128"),
            ("velocity", "m/s", [count, 3], "complex128"),
        ):
            sample = data[name]
            if sample is not None:
                _require(
                    (sample["unit"], sample["shape"], sample["dtype"]) == (unit, shape, dtype),
                    path + "/" + name,
                    "Sample units, dimensions or dtype are inconsistent.",
                )
    elif kind == "force_result":
        _require(
            (data["torque_status"] == "available") == (data["torque"] is not None),
            path + "/torque",
            "Torque availability must agree with its value.",
        )
    elif kind == "mclf_report":
        _require(
            data["verdict"] != "ACCEPTED"
            or all(check["verdict"] == "ACCEPTED" for check in data["checks"]),
            path + "/verdict",
            "An accepted report cannot contain a nonaccepted check.",
        )


def _validate(data: dict, expected_type: str | None = None) -> str:
    check_json_tree(data)
    if type(data) is not dict:
        raise InvalidInputError("INPUT_TYPE", "", "Expected an object document.")
    if data.get("schema_version") != VERSION:
        raise InvalidInputError("SCHEMA_VERSION", "/schema_version", "Expected schema version 1.0.")
    kind = data.get("document_type")
    if (
        type(kind) is not str
        or kind not in _VALIDATORS
        or (expected_type and kind != expected_type)
    ):
        raise InvalidInputError(
            "DOCUMENT_TYPE", "/document_type", "Unsupported or unexpected type."
        )
    # Also bound direct Python callers; serialized readers check byte size before parsing.
    if len(json.dumps(data, ensure_ascii=True, allow_nan=False).encode("utf-8")) > MAX_BYTES:
        raise InvalidInputError("INPUT_LIMIT", "", "Document exceeds 1 MiB after JSON encoding.")
    error = next(_VALIDATORS[kind].iter_errors(data), None)
    if error is not None:
        path = ""
        for part in error.absolute_path:
            path = pointer(path, part)
        if error.validator == "required":
            missing = next(name for name in error.validator_value if name not in error.instance)
            path = pointer(path, missing)
        code = "UNIT_MISMATCH" if path.endswith("/unit") else "SCHEMA_INVALID"
        raise InvalidInputError(code, path, error.message)
    _cross_checks(kind, data)
    return kind


@dataclass(frozen=True, init=False)
class ValidatedRecord:
    """Store isolated JSON, so callers cannot mutate a previously validated record."""

    _json: str
    document_type: ClassVar[str]

    def __init__(self, data: dict):
        _validate(data, self.document_type)
        object.__setattr__(self, "_json", json.dumps(data, ensure_ascii=True, allow_nan=False))

    def to_dict(self) -> dict:
        return json.loads(self._json)


class Medium(ValidatedRecord):
    document_type = "medium"


class Body(ValidatedRecord):
    document_type = "body"


class TransducerArray(ValidatedRecord):
    document_type = "transducer_array"


class SolverSpec(ValidatedRecord):
    document_type = "solver_spec"


class Scenario(ValidatedRecord):
    document_type = "scenario"


class Experiment(ValidatedRecord):
    document_type = "experiment"


class RunManifest(ValidatedRecord):
    document_type = "run_manifest"


class FieldResult(ValidatedRecord):
    document_type = "field_result"


class ForceResult(ValidatedRecord):
    document_type = "force_result"


class MclfReport(ValidatedRecord):
    document_type = "mclf_report"


_RECORDS = {
    cls.document_type: cls
    for cls in (
        Medium,
        Body,
        TransducerArray,
        SolverSpec,
        Scenario,
        Experiment,
        RunManifest,
        FieldResult,
        ForceResult,
        MclfReport,
    )
}


def validate_document(data: dict) -> ValidatedRecord:
    """Validate without running a solver or asserting physical validity."""
    kind = _validate(data)
    return _RECORDS[kind](data)
