"""Replay one verified analytical run in its recorded source and environment."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import venv
from pathlib import Path

from aura.errors import IntegrityError

from . import analytic
from .check import check_run
from .manifest import decode, digest, encode, fail, publish, read_bytes
from .provenance import LOCK_NAMES, SOURCE_ROOT

REPLAY_CONTRACT = "RUN-REPLAY-1.0"
FIELD_BYTES = (
    "field-coordinates.json",
    "field-pressure.json",
    "field-velocity.json",
    "field-pressure-gradient.json",
)
PIP_INSTALL_TIMEOUT_S = 900
COMMAND_TIMEOUT_S = 180
ANA07_COMPARE_SCRIPT = """
import json
import sys
from pathlib import Path

try:
    from aura.analysis.ana07_metrics import analyze_recorded_case, frozen_case
except ModuleNotFoundError:
    print(json.dumps({"reference_available": False, "reason": "Analyzer unavailable at recorded revision."}))
else:
    request = json.loads((Path(sys.argv[1]) / "field-request.json").read_bytes())
    try:
        frozen_case(request["case_id"])
    except ValueError:
        print(json.dumps({"reference_available": False, "reason": "Case is not in ANA-REF-1.0."}))
    else:
        print(json.dumps({
            "reference_available": True,
            "parent": analyze_recorded_case(sys.argv[1]),
            "replay": analyze_recorded_case(sys.argv[2]),
        }, allow_nan=False))
"""


def _command(args, *, cwd=None, env=None, timeout=COMMAND_TIMEOUT_S,
             allowed_returncodes=(0,)):
    try:
        result = subprocess.run(
            args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail("RUN_REPLAY_COMMAND", f"Replay command could not complete: {type(exc).__name__}.")
    if result.returncode not in allowed_returncodes:
        detail = (result.stderr or result.stdout).strip().replace("\n", " ")[:1024]
        fail("RUN_REPLAY_COMMAND", f"Replay command exited {result.returncode}: {detail}")
    return result.stdout


def _overlaps(first: Path, second: Path) -> bool:
    left, right = first.resolve(), second.resolve()
    return left == right or left.is_relative_to(right) or right.is_relative_to(left)


def _load_verified_content(folder: Path, expected_manifest_sha256: str) -> tuple[dict, dict[str, bytes]]:
    raw = read_bytes(folder / "manifest.json")
    if digest(raw) != expected_manifest_sha256:
        fail("HASH_MISMATCH", "Run manifest changed during replay preparation.")
    manifest = decode(raw)
    refs = [*manifest["inputs"], *manifest["outputs"]]
    refs.extend((manifest["mclf_pre"]["report"], manifest["mclf_post"]["report"]))
    content = {ref["uri"]: read_bytes(folder / ref["uri"]) for ref in refs}
    for ref in refs:
        if digest(content[ref["uri"]]) != ref["sha256"]:
            fail("HASH_MISMATCH", "Verified run changed during replay preparation.")
    return manifest, content


def _check_recorded_source(revision: str, source: dict, content: dict[str, bytes]) -> None:
    if type(revision) is not str or re.fullmatch(r"[0-9a-f]{40,64}", revision) is None:
        fail("RUN_REPLAY_SOURCE", "Recorded source revision is not a full Git object ID.")
    lock_hashes = decode(content["environment.json"])["input_sha256"]
    for name in LOCK_NAMES:
        if name not in content or digest(content[name]) != lock_hashes.get(name):
            fail("RUN_REPLAY_LOCK", "Recorded environment lock bytes do not match their identity.")
    try:
        _command(
            ["git", "-C", str(SOURCE_ROOT), "cat-file", "-e", revision + "^{commit}"],
            timeout=10,
        )
    except IntegrityError:
        fail("RUN_REPLAY_SOURCE", "The recorded source commit is not available locally.")


def _verify_snapshot(worktree: Path, source: dict, expected_environment: dict) -> None:
    observed = {}
    for path in sorted((worktree / "src/aura").rglob("*.py")):
        observed[str(path.relative_to(worktree))] = digest(read_bytes(path))
    if observed != source["package_files_sha256"]:
        fail("RUN_REPLAY_SOURCE", "Checked-out package files differ from the recorded source snapshot.")
    for name in LOCK_NAMES:
        if digest(read_bytes(worktree / "requirements" / name)) != (
            expected_environment["input_sha256"].get(name)
        ):
            fail("RUN_REPLAY_LOCK", "Checked-out source lock differs from the recorded environment.")


def _environment_comparison(expected: dict, observed: dict) -> dict:
    if observed["errors"] or any(observed.get(key) != expected.get(key) for key in (
        "profile", "installed", "input_sha256"
    )):
        fail("RUN_REPLAY_ENVIRONMENT", "Fresh environment differs from the recorded ENV-1.0 profile.")
    required_runtime = ("python", "implementation", "system", "machine")
    if any(observed["runtime"][key] != expected["runtime"][key] for key in required_runtime):
        fail("RUN_REPLAY_ENVIRONMENT", "Fresh environment does not match the ENV-1.0 runtime profile.")
    differences = {
        key: {"recorded": value, "replayed": observed["runtime"].get(key)}
        for key, value in expected["runtime"].items()
        if value != observed["runtime"].get(key)
    }
    return {
        "profile": "ENV-1.0", "status": "PASS", "differences": differences,
        "policy": "Python, implementation, OS, architecture, dependencies and locks must match; "
                  "kernel/build/platform snapshots may differ within ENV-1.0.",
    }


def _install_recorded_environment(worktree: Path, temporary: Path,
                                  expected: dict) -> tuple[Path, dict, dict]:
    environment_dir = temporary / "environment"
    venv.EnvBuilder(with_pip=True, clear=False).create(environment_dir)
    python = environment_dir / "bin/python"
    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["VIRTUAL_ENV"] = str(environment_dir)
    env["PATH"] = str(environment_dir / "bin") + os.pathsep + env.get("PATH", os.defpath)
    pip = [str(python), "-m", "pip", "--isolated"]
    _command(
        [*pip, "install", "--index-url", "https://pypi.org/simple", "--require-hashes",
         "--only-binary=:all:", "-r", str(worktree / "requirements/dev-linux-py312.lock")],
        env=env, timeout=PIP_INSTALL_TIMEOUT_S,
    )
    _command(
        [*pip, "install", "--no-index", "--no-deps", "--no-build-isolation", "-e", ".[dev]"],
        cwd=worktree,
        env=env,
        timeout=PIP_INSTALL_TIMEOUT_S,
    )
    _command([*pip, "check"], env=env, timeout=COMMAND_TIMEOUT_S)
    verification = _command(
        [str(python), str(worktree / "scripts/verify_environment.py")],
        cwd=worktree,
        env=env,
    )
    observed = json.loads(verification)
    runtime_comparison = _environment_comparison(expected, observed)
    return environment_dir / "bin/aura", env, runtime_comparison


def _comparison(parent_content: dict[str, bytes], replay_content: dict[str, bytes],
                reference_result: dict) -> dict:
    bitwise = {
        name: {
            "parent_sha256": digest(parent_content[name]),
            "replay_sha256": digest(replay_content[name]),
            "equal": parent_content[name] == replay_content[name],
        }
        for name in FIELD_BYTES
    }
    bitwise_status = "PASS" if all(item["equal"] for item in bitwise.values()) else "FAIL"
    reference = {"protocol": "ANA-REF-1.0", "status": "INDETERMINATE", "case_id": None}
    metric = {
        "status": "INDETERMINATE",
        "comparison": "Exact equality; no replay tolerance is defined.",
    }
    if reference_result["reference_available"]:
        left, right = reference_result["parent"], reference_result["replay"]
        reference = {
            "protocol": left["protocol"], "case_id": left["case_id"],
            "parent_status": left["numerical_comparison"],
            "replay_status": right["numerical_comparison"],
            "status": "PASS" if left["numerical_comparison"] == right["numerical_comparison"] == "PASS" else "FAIL",
            "tolerance_normalized": left["tolerance_normalized"],
            "reference_sources": left["reference_sources"],
            "physical_validation": "NOT_ESTABLISHED",
        }
        equal = left["metrics"] == right["metrics"]
        metric = {
            "status": "PASS" if equal else "FAIL",
            "comparison": "Exact equality of ANA-07 E_max, E_rms, component counts and criteria; no tolerance.",
            "parent_metrics": left["metrics"], "replay_metrics": right["metrics"],
        }
    else:
        reference["reason"] = reference_result["reason"]
    return {
        "bitwise_field_artifacts": {"status": bitwise_status, "artifacts": bitwise},
        "metric_reproducibility": metric,
        "reference_comparison": reference,
    }


def _report(parent: dict, replay: dict, checks: dict, output_dir: Path,
            runtime_comparison: dict) -> dict:
    return {
        "contract": "RUN-REPLAY-REPORT-1.0",
        "replay_protocol": REPLAY_CONTRACT,
        "parent": {"run_id": parent["id"], "manifest_sha256": digest(encode(parent))},
        "replay": {
            "run_id": replay["run_id"], "manifest_sha256": replay["manifest_sha256"],
            "directory": str(output_dir),
        },
        "source_revision": parent["source"]["revision"],
        "environment": {
            "profile": "ENV-1.0", "recreated_in_fresh_venv": True,
            "lock_sha256": parent["environment"]["lock"]["sha256"],
            "verification": "PASS", "runtime_comparison": runtime_comparison,
        },
        **checks,
        "execution_status": replay["execution_status"],
        "scientific_verdict": replay["verdict"],
        "physical_validation": "NOT_ESTABLISHED",
        "limitations": [
            "Replay uses the recorded source revision and lock-bound ENV-1.0 dependency profile.",
            "Host runtime snapshot differences permitted by ENV-1.0 are listed; field outputs are still compared exactly.",
            "Exact field-array and metric repeatability is software evidence, not model validation.",
            "Acoustic force, body motion and experimental behavior were not replayed or validated.",
        ],
    }


def _write_report(report_dir: Path, report: dict) -> dict:
    if report_dir.exists() or report_dir.is_symlink():
        fail("RUN_REPORT_EXISTS", "Replay report directory already exists; choose a new path.")
    report_dir.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir()
    json_bytes = encode(report)
    lines = [
        "# AURA Replay Report", "", f"Contract: {report['contract']}",
        f"Replay protocol: {report['replay_protocol']}",
        f"Parent run: {report['parent']['run_id']} ({report['parent']['manifest_sha256']})",
        f"Replay run: {report['replay']['run_id']} ({report['replay']['manifest_sha256']})",
        f"Source revision: {report['source_revision']}",
        "Environment: fresh ENV-1.0 virtual environment; verification PASS.",
        f"Bitwise field artifacts: **{report['bitwise_field_artifacts']['status']}**",
        f"Metric reproducibility: **{report['metric_reproducibility']['status']}**",
        f"ANA-REF comparison: **{report['reference_comparison']['status']}**",
        f"Scientific verdict: **{report['scientific_verdict']}**",
        f"Physical validation: **{report['physical_validation']}**", "",
        "## Limitations", "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    markdown = ("\n".join(lines)).encode("utf-8")
    json_ref = publish(report_dir, "replay-report.json", json_bytes)
    markdown_ref = publish(report_dir, "replay-report.md", markdown)
    index = {
        "contract": "RUN-REPLAY-INDEX-1.0",
        "parent": report["parent"], "replay": report["replay"],
        "files": [json_ref, markdown_ref],
    }
    publish(report_dir, "artifact-index.json", encode(index))
    return index


def reproduce(source_folder, *, output=None, report_dir=None) -> dict:
    """Re-execute a verified analytical bundle in a fresh, exact ENV-1.0 venv."""
    source_folder = Path(source_folder)
    checked = check_run(source_folder)
    if checked["integrity"] != "VERIFIED" or checked["execution_status"] != "completed":
        fail("RUN_REPLAY_PARENT", "Only completed, integrity-verified runs can be replayed.")
    parent, content = _load_verified_content(source_folder, checked["manifest_sha256"])
    if not analytic.is_analytical_driver(parent["solver"]["model_id"]):
        fail("RUN_REPLAY_MODEL", "RUN-REPLAY-1.0 admits only recorded analytical field runs.")
    source = decode(content["source.json"])
    expected_environment = decode(content["environment.json"])
    _check_recorded_source(source["revision"], source, content)
    default_root = SOURCE_ROOT / "results/replays" / parent["id"]
    output_dir = Path(output) if output is not None else default_root / os.urandom(8).hex()
    if output_dir.exists() or output_dir.is_symlink():
        fail("RUN_EXISTS", "Replay output already exists; choose a new directory.")
    output_dir = output_dir.absolute()
    report_path = Path(report_dir) if report_dir is not None else output_dir.with_name(
        output_dir.name + "-report"
    )
    if report_path.exists() or report_path.is_symlink():
        fail("RUN_REPORT_EXISTS", "Replay report directory already exists; choose a new path.")
    if _overlaps(output_dir, source_folder) or _overlaps(report_path, source_folder) or (
        _overlaps(output_dir, report_path)
    ):
        fail("RUN_REPLAY_PATH", "Parent, replay and report paths must not overlap.")

    protocol_name = decode(content["experiment.json"])["protocol"]["uri"]
    with tempfile.TemporaryDirectory(prefix="aura-replay-") as temporary_name:
        temporary = Path(temporary_name)
        worktree = temporary / "source"
        _command([
            "git", "-C", str(SOURCE_ROOT), "worktree", "add", "--detach",
            str(worktree), source["revision"],
        ])
        try:
            _verify_snapshot(worktree, source, expected_environment)
            executable, child_env, runtime_comparison = _install_recorded_environment(
                worktree, temporary, expected_environment
            )
            inputs = temporary / "inputs"
            inputs.mkdir()
            for name in ("scenario.json", "experiment.json"):
                (inputs / name).write_bytes(content[name])
            (inputs / protocol_name).write_bytes(content[protocol_name])
            command = [
                str(executable), "run", str(inputs / "scenario.json"),
                "--experiment", str(inputs / "experiment.json"), "--output",
                str(output_dir), "--json",
            ]
            command.append(
                "--no-randomness" if parent["seed"] is None else "--seed=" + str(parent["seed"])
            )
            stdout = _command(command, cwd=worktree, env=child_env, allowed_returncodes=(0, 3))
            execution = json.loads(stdout)
            if execution.get("execution_status") != "completed":
                fail("RUN_REPLAY_EXECUTION", "Fresh execution did not complete; retain its run record.")
            reference_result = json.loads(_command(
                [
                    str(executable.parent / "python"), "-c", ANA07_COMPARE_SCRIPT,
                    str(source_folder.absolute()), str(output_dir),
                ],
                cwd=worktree,
                env=child_env,
            ))
        finally:
            _command([
                "git", "-C", str(SOURCE_ROOT), "worktree", "remove", "--force", str(worktree),
            ])

    replay_checked = check_run(output_dir)
    if replay_checked["integrity"] != "VERIFIED" or replay_checked["execution_status"] != "completed":
        fail("RUN_REPLAY_OUTPUT", "Fresh replay output did not pass integrity inspection.")
    _, replay_content = _load_verified_content(output_dir, replay_checked["manifest_sha256"])
    if any(content[name] != replay_content[name] for name in (
        "scenario.json", "experiment.json", protocol_name, *LOCK_NAMES,
    )):
        fail("RUN_REPLAY_INPUTS", "Fresh replay input bytes differ from the selected parent run.")
    checks = _comparison(content, replay_content, reference_result)
    report = _report(parent, execution, checks, output_dir, runtime_comparison)
    index = _write_report(report_path, report)
    report["report_directory"] = str(report_path)
    report["artifact_index"] = index
    report["exit_code"] = 1 if checks["bitwise_field_artifacts"]["status"] == "FAIL" else (
        3 if checks["metric_reproducibility"]["status"] == "INDETERMINATE" else 0
    )
    return report
