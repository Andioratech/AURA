"""Read-only integrity checks for RUN-1.0 bundles; never scientific acceptance or replay."""

import re
from pathlib import Path

from aura import __version__
from aura.schema import (
    Experiment,
    RunManifest,
    Scenario,
    loads_document,
    verify_manifest_configuration,
)

from . import analytic
from .execute import DRIVERS, LIMITATION, VERSION
from .manifest import decode, digest, fail, read_bytes, safe_file, verified_bytes
from .provenance import LOCK_NAMES

INPUT_NAMES = {"scenario.json", "experiment.json", "protocol.md", "source.json",
               "environment.json", "preflight.json", *LOCK_NAMES}


def check_run(folder, *, expected_sha256=None):
    folder = Path(folder)
    if folder.is_symlink() or not folder.is_dir():
        fail("RUN_PATH", "Expected a local run directory, not a symlink.")
    if expected_sha256 is not None and re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        fail("DIGEST_FORMAT", "Expected 64 lowercase hexadecimal digits.")
    safe_file(folder, "manifest.json")
    terminal = (folder / "manifest.json").exists()
    name = "manifest.json" if terminal else "running.json"
    raw = read_bytes(safe_file(folder, name))
    manifest = loads_document(raw)
    if not isinstance(manifest, RunManifest):
        fail("DOCUMENT_TYPE", "Expected a RunManifest.")
    data = manifest.to_dict()
    actual = digest(raw)
    if expected_sha256 is not None and (not terminal or expected_sha256 != actual):
        fail("HASH_MISMATCH", "Manifest differs from the separately retained digest.")
    if terminal:
        if not (folder / "manifest.sha256").exists():
            fail("RUN_INCOMPLETE", "Final manifest has no completion checksum; preserve the bundle.")
        sidecar = read_bytes(safe_file(folder, "manifest.sha256"), 65)
        if sidecar != (actual + "\n").encode():
            fail("HASH_MISMATCH", "Manifest checksum differs.")
    elif data["execution_status"] != "running":
        fail("RUN_STATE", "Initial manifest must record running state.")
    refs = [*data["inputs"], *data["outputs"], data["mclf_pre"].get("report", {})]
    if terminal:
        refs.append(data["mclf_post"].get("report", {}))
    names = [ref.get("uri") for ref in refs]
    if len(names) != len(set(names)):
        fail("RUN_REFERENCE", "Duplicate artifact references.")
    content = {ref["uri"]: verified_bytes(folder, ref) for ref in refs}
    scenario, experiment = loads_document(content["scenario.json"]), loads_document(content["experiment.json"])
    if not isinstance(scenario, Scenario) or not isinstance(experiment, Experiment):
        fail("DOCUMENT_TYPE", "Stored scenario/experiment has the wrong document type.")
    verify_manifest_configuration(manifest, scenario, experiment=experiment)
    exp = experiment.to_dict()
    protocol_uri = exp["protocol"]["uri"]
    if type(protocol_uri) is not str or Path(protocol_uri).name != protocol_uri or protocol_uri in ("", ".", ".."):
        fail("RUN_PROTOCOL", "Stored protocol reference must be one local filename.")
    expected_inputs = (INPUT_NAMES - {"protocol.md"}) | {protocol_uri}
    if {ref["uri"] for ref in data["inputs"]} != expected_inputs:
        fail("RUN_INPUTS", "The required RUN-1.0 input set is incomplete or changed.")
    if digest(content[protocol_uri]) != exp["protocol"]["sha256"]:
        fail("HASH_MISMATCH", "Stored protocol differs from the experiment.")
    if data["observables"] != [exp["primary_observable"]["name"]]:
        fail("IDENTITY_MISMATCH", "Recorded observable differs from the experiment.")
    source, env = decode(content["source.json"]), decode(content["environment.json"])
    if {key: source[key] for key in ("revision", "dirty", "patch_sha256")} != data["source"]:
        fail("IDENTITY_MISMATCH", "Source snapshot and manifest differ.")
    if source["dirty"] or not source["package_files_sha256"]:
        fail("RUN_SOURCE", "This lifecycle requires a recorded clean source inventory.")
    lock = data["environment"]["lock"]
    if lock != {"uri": "dev-linux-py312.lock", "sha256": digest(content["dev-linux-py312.lock"])}:
        fail("HASH_MISMATCH", "Environment lock reference differs.")
    if env["errors"] or env["input_sha256"] != {
        name: digest(content[name]) for name in LOCK_NAMES
    } or data["environment"]["platform"] != env["runtime"]["platform"]:
        fail("RUN_ENVIRONMENT", "Environment snapshot and lock bytes disagree.")
    inventory = decode(content["environment-linux-py312.json"])
    versions = {item["name"]: item["version"] for item in inventory["artifacts"]}
    versions["aura-science"] = __version__
    if env["profile"] != inventory["profile"] or env["installed"] != versions or any(
        env["runtime"][key] != inventory[key]
        for key in ("python", "implementation", "system", "machine")
    ):
        fail("RUN_ENVIRONMENT", "Recorded installed profile disagrees with its inventory.")
    pre = decode(content["audit-pre.json"])
    if pre["stage"] != "pre" or pre["report"]["run_id"] != data["id"] or (
        pre["report"]["verdict"] != data["mclf_pre"]["verdict"]
    ) or pre["report"]["verdict"] != "INDETERMINATE":
        fail("RUN_AUDIT", "Pre-audit identity or diagnostic verdict differs.")
    if DRIVERS.get(data["solver"]["model_id"]) != data["solver"]["model_version"]:
        fail("RUN_MODEL", "Unrecognized recorded diagnostic model.")
    analytical = analytic.is_analytical_driver(data["solver"]["model_id"])
    request = None
    if analytical:
        request = analytic.parse_request(content[protocol_uri])
        analytic.check_preflight(decode(content["preflight.json"]), scenario, request)
        if sum(len(value) for value in content.values()) > 16 * 1024**2:
            fail("RUN_RESOURCE", "Analytical bundle inputs/artifacts exceed the 16 MiB cap.")
    scope = analytic.scope_for(data["solver"]["model_id"]) if analytical else LIMITATION
    if not terminal:
        return {"lifecycle_version": VERSION, "run_id": data["id"], "integrity": "INCOMPLETE",
                "execution_status": "running", "verdict": "INDETERMINATE", "exit_code": 3,
                "scope": "Initial artifacts verified; completion/liveness is unknown. " + scope}
    state = data["execution_status"]
    if state not in ("completed", "failed", "aborted"):
        fail("RUN_STATE", "Final manifest must have a terminal execution state.")
    running = loads_document(content["running.json"]).to_dict()
    mutable = {"execution_status", "outputs", "metrics", "mclf_post", "failure_code"}
    if running["execution_status"] != "running" or any(
        running[key] != value for key, value in data.items() if key not in mutable
    ):
        fail("IDENTITY_MISMATCH", "Initial and final run identities differ.")
    post, usage = decode(content["audit-post.json"]), decode(content["execution.json"])
    verdict = "INDETERMINATE" if state == "completed" else "INVALIDATED"
    if post["audit_version"] != "RUN-POST-1.0" or post["run_id"] != data["id"] or (
        post["verdict"] != verdict or data["mclf_post"]["verdict"] != verdict
    ) or post["execution_status"] != state or usage["execution_status"] != state or (
        usage["run_id"] != data["id"] or usage["lifecycle_version"] != VERSION
    ):
        fail("RUN_AUDIT", "Final execution/audit identity or verdict differs.")
    expected_limitations = [
        "Lifecycle integrity postcheck only; independent numerical comparison and physical-result audits are unavailable."
        if analytical else
        "Lifecycle postcheck only; physical-result L0/L1-L5 checks unavailable."
    ]
    if post["scope"] != scope or post["limitations"] != expected_limitations or (
        post["pre_verdict"] != data["mclf_pre"]["verdict"]
    ) or (
        post["artifact_check"] != ("PASS" if state == "completed" else "NOT_ESTABLISHED")
    ) or post["physical_result"] != "NOT_REQUESTED" or usage["seed_used"] is not False:
        fail("RUN_AUDIT", "Diagnostic audit scope or seed-use policy differs.")
    if data["metrics"] != [{"name": "runtime_s", "value": usage["elapsed_s"], "unit": "s",
                           "definition": "Recorder interval through driver/input checks; excludes final publication."}]:
        fail("RUN_METRICS", "Manifest metric differs from the recorded execution interval.")
    if (usage["error"] is None) != (state == "completed") or (
        usage["error"] is not None and usage["error"]["code"] != data["failure_code"]
    ):
        fail("RUN_STATE", "Failure record and manifest disagree.")
    analytical_outputs = {ref["uri"] for ref in data["outputs"]}
    if analytical:
        required = {"execution.json", "running.json"}
        allowed = analytic.OUTPUT_NAMES | required
        if not required <= analytical_outputs or not analytical_outputs <= allowed or (
            state == "completed" and analytical_outputs != allowed
        ):
            fail("FIELD_OUTPUTS", "Analytical run output index is incomplete or changed.")
        driver_id = data["solver"]["model_id"]
        if usage["scope"] != analytic.scope_for(driver_id) or usage["backend"] != "analytic-closed-form" or (
            usage["run_policy"] != analytic.run_policy_for(driver_id) or (
                usage["expected_driver_outputs"] != sorted(analytic.OUTPUT_NAMES)
            )
        ):
            fail("RUN_SCOPE", "Analytical driver provenance or scope differs.")
    if state == "completed" and analytical:
        analytic.check_field_outputs(
            data["id"], scenario.to_dict(), request,
            [ref for ref in data["outputs"] if ref["uri"] in analytic.OUTPUT_NAMES],
            {name: decode(content[name]) for name in analytic.OUTPUT_NAMES},
        )
    elif state == "completed":
        receipt = decode(content["receipt.json"])
        if receipt != {"diagnostic_version": VERSION, "scenario_id": data["scenario_id"],
                       "physical_simulation": False, "scope": LIMITATION}:
            fail("RUN_RECEIPT", "Unexpected diagnostic receipt.")
    allowed = {*names, "manifest.json", "manifest.sha256"}
    if {path.name for path in folder.iterdir()} != allowed:
        fail("RUN_EXTRA_FILES", "Bundle contains unindexed or missing files.")
    if analytical and sum(path.stat().st_size for path in folder.iterdir()) > 16 * 1024**2:
        fail("RUN_RESOURCE", "Analytical run bundle exceeds the 16 MiB cap.")
    return {"lifecycle_version": VERSION, "run_id": data["id"], "integrity": "VERIFIED",
            "execution_status": state, "verdict": verdict, "manifest_sha256": actual,
            "exit_code": 3 if state == "completed" else 1,
            "scope": "Recorded bytes and links verified; not source replay or publisher authentication. " + scope}
