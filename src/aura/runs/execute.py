"""RUN-1.0: immutable recording of bounded software diagnostics, not physical solvers."""

import os
import resource
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from aura.mclf import evaluate_scenario
from aura.schema import (
    Experiment,
    RunManifest,
    Scenario,
    document_sha256,
    dumps_document,
    loads_document,
    verify_manifest_configuration,
)

from . import analytic, provenance
from .manifest import decode, digest, encode, fail, publish, read_bytes, verified_bytes

VERSION = "RUN-1.0"
DRIVERS = {
    "lifecycle-receipt": "1.0",
    "lifecycle-failure": "1.0",
    analytic.DRIVER: analytic.DRIVER_VERSION,
}
LIMITATION = "Software diagnostic only; no physical simulation or scientific acceptance."


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load(path, kind):
    path = Path(path)
    raw = read_bytes(path)
    record = loads_document(raw, format=path.suffix.lstrip(".").lower())
    if not isinstance(record, kind):
        fail("DOCUMENT_TYPE", f"Expected {kind.__name__}.")
    return record


def _preflight(config, payloads, output, field_estimate=None):
    parent = output.parent
    while not parent.exists():
        parent = parent.parent
    # Linux ru_maxrss is KiB and includes this process's earlier imports/work.
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    estimate = {
        "ram_bytes": max(64 * 1024**2, rss + 16 * 1024**2),
        "disk_bytes": 2 * 1024**2 + 4 * sum(len(item) for item in payloads.values()),
        "wall_time_s": 1.0,
        "cpu_workers": 1, "gpu": False, "field_samples": 0,
        "basis": "Fixed software receipt; host/process headroom, not a numerical solver model.",
    }
    caps = config["resources"]
    available_ram = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    if field_estimate is not None:
        estimate = field_estimate
    if estimate["ram_bytes"] > min(caps["ram_bytes"], available_ram) or (
        estimate["disk_bytes"] > min(caps["disk_bytes"], shutil.disk_usage(parent).free)
    ) or estimate["wall_time_s"] > caps["wall_time"]["value"]:
        fail("RUN_RESOURCE", "Requested or available resources do not cover this diagnostic.")
    return estimate


def _driver(config, emit):
    """Only these versioned, bounded diagnostics are exposed; no arbitrary plugin hook."""
    if config["solver"]["model_id"] == "lifecycle-failure":
        emit("partial.json", {"diagnostic_version": VERSION, "stage": "before_deliberate_failure"})
        raise RuntimeError("Deliberate lifecycle diagnostic failure")
    emit("receipt.json", {"diagnostic_version": VERSION, "scenario_id": config["id"],
                          "physical_simulation": False, "scope": LIMITATION})


def execute(scenario_path, experiment_path, *, output=None, seed):
    """Validate before allocating a new directory; retain failures once a run starts."""
    scenario = _load(scenario_path, Scenario)
    experiment = _load(experiment_path, Experiment)
    config, exp = scenario.to_dict(), experiment.to_dict()
    if seed is not None and (type(seed) is not int or seed < 0):
        fail("RUN_SEED", "Specify a nonnegative integer or explicit no-randomness null.")
    solver = config["solver"]
    model_id = solver["model_id"]
    analytical = model_id == analytic.DRIVER
    if DRIVERS.get(model_id) != solver["model_version"]:
        fail("RUN_MODEL", "Only a registered versioned run driver is available.")
    if not analytical and (
        solver["precision"] != "float64" or solver["parameters"]
        or solver["equation_ids"] != ["SOFTWARE-RUN-01"]
    ):
        fail("RUN_MODEL", "Only the registered version-1.0 software diagnostics use this policy.")
    if (exp["scenario_id"], exp["scenario_sha256"]) != (
        config["id"], document_sha256(scenario)
    ):
        fail("HASH_MISMATCH", "Experiment does not identify this exact scenario.")
    protocol_uri = exp["protocol"]["uri"]
    if ":" in protocol_uri or Path(protocol_uri).is_absolute() or Path(protocol_uri).name != protocol_uri:
        fail("RUN_PROTOCOL", "Use one local protocol filename relative to the experiment file.")
    protocol = read_bytes(Path(experiment_path).parent / protocol_uri)
    if digest(protocol) != exp["protocol"]["sha256"]:
        fail("HASH_MISMATCH", "Protocol bytes differ from the frozen experiment.")
    request = analytic.parse_request(protocol) if analytical else None
    field_estimate = None
    if analytical:
        field_estimate = analytic.preflight(scenario, request)
    run_id = "RUN-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + uuid.uuid4().hex
    pre = evaluate_scenario(config, report_id=run_id + "-PRE", run_id=run_id, stage="pre")
    if pre.verdict in ("INVALIDATED", "ALERT"):
        pre.require_accepted()
    source, environment, locks = provenance.capture()
    destination = Path(output) if output is not None else (
        provenance.SOURCE_ROOT / "results" / exp["id"] / run_id
    )
    if destination.exists() or destination.is_symlink():
        fail("RUN_EXISTS", "Output already exists; choose a new run directory.")
    if destination.resolve().is_relative_to(provenance.SOURCE_ROOT):
        relative = destination.resolve().relative_to(provenance.SOURCE_ROOT)
        # Prevent our own output from changing the recorded clean source tree.
        if not str(relative).startswith("results/"):
            fail("RUN_OUTPUT_LOCATION", "Outputs inside the checkout must be under results/.")
    payloads = {
        "scenario.json": dumps_document(scenario).encode(),
        "experiment.json": dumps_document(experiment).encode(),
        Path(protocol_uri).name: protocol, "source.json": encode(source),
        "environment.json": encode(environment), **locks,
    }
    estimate = _preflight(config, payloads, destination, field_estimate)
    payloads["preflight.json"] = encode(estimate)
    inputs = [{"uri": name, "sha256": digest(data)} for name, data in payloads.items()]
    manifest = {
        "document_type": "run_manifest", "schema_version": "1.0", "id": run_id,
        "experiment_id": exp["id"], "scenario_id": config["id"], "claim_id": exp["claim_id"],
        "hypothesis": exp["hypothesis"], "observables": [exp["primary_observable"]["name"]],
        "timestamp_utc": utc_now(), "execution_status": "running",
        "source": {key: source[key] for key in ("revision", "dirty", "patch_sha256")},
        "configuration_sha256": document_sha256(scenario),
        "environment": {"lock": {"uri": "dev-linux-py312.lock",
                                   "sha256": digest(locks["dev-linux-py312.lock"])},
                        "platform": environment["runtime"]["platform"]},
        "solver": solver, "seed": seed, "resources": config["resources"], "inputs": inputs,
        "outputs": [], "metrics": [], "convergence": [],
        "mclf_pre": {"status": "completed", "verdict": pre.verdict,
                     "report": {"uri": "audit-pre.json", "sha256": digest(encode(pre.to_dict()))}},
        "mclf_post": {"status": "not_run"}, "failure_code": None,
        "operator_notes": (analytic.SCOPE if analytical else LIMITATION)
        + " Exploratory permission: DEC-003; seed is recorded but unused.",
    }
    verify_manifest_configuration(RunManifest(manifest), scenario, experiment=experiment)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()  # Exclusive reservation; race with another creator fails.
    started = time.monotonic()
    cpu_started = time.process_time()
    running_ref = publish(destination, "running.json", encode(manifest))
    for name, data in payloads.items():
        publish(destination, name, data)
    publish(destination, "audit-pre.json", encode(pre.to_dict()))
    outputs = []
    error = None
    state, code = "completed", 3

    def emit(name, value):
        ref = publish(destination, name, encode(value))
        outputs.append(ref)
        return ref

    try:
        if analytical:
            analytic.execute_field(scenario, request, run_id, emit)
        else:
            _driver(config, emit)
        source_after, environment_after, locks_after = provenance.capture()
        if (source_after, environment_after, locks_after) != (source, environment, locks):
            fail("RUN_SOURCE_CHANGED", "Source changed during execution.")
        for ref in [*inputs, *outputs, manifest["mclf_pre"]["report"]]:
            verified_bytes(destination, ref)
        expected_outputs = analytic.OUTPUT_NAMES if analytical else {"receipt.json"}
        if {ref["uri"] for ref in outputs} != expected_outputs:
            fail("RUN_OUTPUT_MISSING", "Required driver outputs are absent or unexpected.")
        if analytical:
            stored = {name: decode(read_bytes(destination / name)) for name in analytic.OUTPUT_NAMES}
            analytic.check_field_outputs(run_id, config, request, outputs, stored)
            if sum(path.stat().st_size for path in destination.iterdir()) > 15 * 1024**2:
                fail("RUN_RESOURCE", "Analytical bundle crossed the reserved 16 MiB storage cap.")
        if time.monotonic() - started > config["resources"]["wall_time"]["value"]:
            fail("RUN_TIME_LIMIT", "Recorded execution exceeded its wall-time cap.")
    except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001 -- retain every driver failure
        state = "aborted" if isinstance(exc, KeyboardInterrupt) else "failed"
        code = 128 + getattr(exc, "signal_number", 2) if state == "aborted" else 1
        error = {"code": getattr(exc, "code", "RUN_INTERRUPTED" if state == "aborted" else "RUN_EXECUTION"),
                 "type": type(exc).__name__, "message": str(exc)[:1024]}
    # Failure to publish final evidence is deliberately not converted to success.
    # The original running record and any partial files remain available.
    elapsed = time.monotonic() - started
    usage = {"lifecycle_version": VERSION, "run_id": run_id, "finished_utc": utc_now(),
             "execution_status": state, "elapsed_s": elapsed, "error": error,
             "peak_process_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
             "process_cpu_time_s": time.process_time() - cpu_started,
             "logical_cpu_count": os.cpu_count(), "gpu_used": False,
             "driver_artifact_bytes": sum((destination / ref["uri"]).stat().st_size for ref in outputs),
             "expected_driver_outputs": sorted(analytic.OUTPUT_NAMES) if analytical else ["receipt.json"],
             "seed_used": False, "scope": analytic.SCOPE if analytical else LIMITATION,
             "backend": "analytic-closed-form" if analytical else "software-diagnostic",
             "run_policy": analytic.RUN_POLICY if analytical else "SOFTWARE-DIAGNOSTIC-1.0"}
    emit("execution.json", usage)
    post = {"audit_version": "RUN-POST-1.0", "run_id": run_id,
            "verdict": "INDETERMINATE" if state == "completed" else "INVALIDATED",
            "execution_status": state, "pre_verdict": pre.verdict,
            "artifact_check": "PASS" if state == "completed" else "NOT_ESTABLISHED",
            "physical_result": "NOT_REQUESTED", "scope": LIMITATION,
            "limitations": ["Lifecycle postcheck only; physical-result L0/L1-L5 checks unavailable."]}
    post_ref = publish(destination, "audit-post.json", encode(post))
    manifest.update(execution_status=state, outputs=outputs,
                    failure_code=None if error is None else error["code"],
                    metrics=[{"name": "runtime_s", "value": elapsed, "unit": "s",
                              "definition": "Recorder interval through driver/input checks; excludes final publication."}],
                    mclf_post={"status": "completed", "verdict": post["verdict"], "report": post_ref})
    manifest["outputs"].append(running_ref)
    final = RunManifest(manifest)
    ref = publish(destination, "manifest.json", encode(final.to_dict()))
    publish(destination, "manifest.sha256", (ref["sha256"] + "\n").encode())
    return {"lifecycle_version": VERSION, "run_id": run_id, "output": str(destination),
            "execution_status": state, "verdict": post["verdict"], "error": error,
            "manifest_sha256": ref["sha256"], "exit_code": code, "scope": LIMITATION}
