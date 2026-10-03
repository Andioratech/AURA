from __future__ import annotations

import pytest

from aura.errors import IntegrityError
from aura.runs import reproduce as reproduce_run


def _components(value=b"same"):
    from aura.runs.reproduce import FIELD_BYTES

    return {name: value for name in FIELD_BYTES}


def test_replay_reports_field_and_metric_reproducibility_separately():
    from aura.runs.reproduce import _comparison

    metrics = {"pressure": {"E_max": 0.0, "E_rms": 0.0, "components_compared": 1,
                            "criterion": "PASS"}}
    reference_run = {
        "protocol": "ANA-REF-1.0", "case_id": "B03-AXIAL",
        "numerical_comparison": "PASS", "tolerance_normalized": 1e-12,
        "reference_sources": {"fixture": "f" * 64}, "metrics": metrics,
    }
    parent_content = _components()
    replay_content = _components()
    parent_content["field-request.json"] = b'{"case_id":"B03-AXIAL"}'
    replay_content["field-pressure.json"] = b"different bytes"

    result = _comparison(
        parent_content, replay_content,
        {"reference_available": True, "parent": reference_run, "replay": reference_run},
    )

    assert result["bitwise_field_artifacts"]["status"] == "FAIL"
    assert result["bitwise_field_artifacts"]["artifacts"]["field-pressure.json"]["equal"] is False
    assert result["metric_reproducibility"]["status"] == "PASS"
    assert result["reference_comparison"]["status"] == "PASS"


def test_unavailable_reference_remains_indeterminate():
    from aura.runs.reproduce import _comparison

    content = _components()
    content["field-request.json"] = b'{"case_id":"UNKNOWN"}'
    result = _comparison(
        content, _components(),
        {"reference_available": False, "reason": "Case is not in ANA-REF-1.0."},
    )

    assert result["bitwise_field_artifacts"]["status"] == "PASS"
    assert result["metric_reproducibility"]["status"] == "INDETERMINATE"
    assert result["reference_comparison"]["status"] == "INDETERMINATE"
    assert result["reference_comparison"]["reason"] == "Case is not in ANA-REF-1.0."


def test_report_index_hashes_human_and_machine_records(tmp_path):
    from aura.runs.manifest import decode, digest, read_bytes
    from aura.runs.reproduce import _write_report

    report_dir = tmp_path / "report"
    report = {
        "contract": "RUN-REPLAY-REPORT-1.0",
        "replay_protocol": "RUN-REPLAY-1.0",
        "parent": {"run_id": "RUN-PARENT", "manifest_sha256": "a" * 64},
        "replay": {"run_id": "RUN-REPLAY", "manifest_sha256": "b" * 64},
        "source_revision": "c" * 40,
        "bitwise_field_artifacts": {"status": "PASS"},
        "metric_reproducibility": {"status": "PASS"},
        "reference_comparison": {"status": "PASS"},
        "scientific_verdict": "INDETERMINATE",
        "physical_validation": "NOT_ESTABLISHED",
        "limitations": ["Software repeatability is not physical validation."],
    }

    index = _write_report(report_dir, report)

    assert [item["uri"] for item in index["files"]] == [
        "replay-report.json", "replay-report.md",
    ]
    for ref in index["files"]:
        assert digest(read_bytes(report_dir / ref["uri"])) == ref["sha256"]
    stored_index = decode(read_bytes(report_dir / "artifact-index.json"))
    assert stored_index["contract"] == "RUN-REPLAY-INDEX-1.0"
    assert "physical validation" in read_bytes(report_dir / "replay-report.md").decode().lower()
    with pytest.raises(IntegrityError, match="RUN_REPORT_EXISTS"):
        _write_report(report_dir, report)


def test_reproduce_refuses_unverified_or_invalidated_parent(tmp_path, monkeypatch):
    import importlib

    reproduce_module = importlib.import_module("aura.runs.reproduce")
    monkeypatch.setattr(
        reproduce_module, "check_run",
        lambda _folder: {"integrity": "VERIFIED", "execution_status": "failed"},
    )

    with pytest.raises(IntegrityError, match="RUN_REPLAY_PARENT"):
        reproduce_run(tmp_path / "not-a-run")


def test_env_profile_allows_recorded_host_runtime_variation_but_not_python_drift():
    import copy

    from aura.runs.reproduce import _environment_comparison

    expected = {
        "errors": [],
        "profile": "ENV-1.0",
        "installed": {"aura-science": "0.1.0"},
        "input_sha256": {"dev-lock": "a" * 64},
        "runtime": {
            "python": "3.12.14", "implementation": "CPython", "system": "Linux",
            "machine": "x86_64", "libc": ["glibc", "2.43"],
            "platform": "Linux-old-kernel", "python_build": ["main", "recorded build"],
        },
    }
    observed = copy.deepcopy(expected)
    observed["runtime"].update(
        libc=["glibc", "2.41"], platform="Linux-new-kernel",
        python_build=["main", "fresh build"],
    )

    result = _environment_comparison(expected, observed)

    assert result["status"] == "PASS"
    assert result["differences"]["libc"]["recorded"] == ["glibc", "2.43"]
    assert result["differences"]["libc"]["replayed"] == ["glibc", "2.41"]
    observed["runtime"]["python"] = "3.12.15"
    with pytest.raises(IntegrityError, match="RUN_REPLAY_ENVIRONMENT"):
        _environment_comparison(expected, observed)


def test_replay_and_report_paths_cannot_overlap(tmp_path):
    from aura.runs.reproduce import _overlaps

    parent = tmp_path / "parent"
    replay = parent / "child"
    report = tmp_path / "report"
    assert _overlaps(parent, replay)
    assert not _overlaps(parent, report)


def test_replay_command_accepts_only_declared_completed_run_exit():
    import importlib
    from types import SimpleNamespace

    module = importlib.import_module("aura.runs.reproduce")
    original = module.subprocess.run
    module.subprocess.run = lambda *_args, **_kwargs: SimpleNamespace(
        returncode=3, stderr="", stdout='{"execution_status":"completed"}',
    )
    try:
        assert module._command(["aura", "run"], allowed_returncodes=(0, 3)).startswith("{")
        with pytest.raises(IntegrityError, match="RUN_REPLAY_COMMAND"):
            module._command(["aura", "check"])
    finally:
        module.subprocess.run = original


def test_cli_exposes_replay_report_options(monkeypatch, capsys):
    import aura.runs
    from aura.cli import main

    monkeypatch.setattr(
        aura.runs, "reproduce",
        lambda path, output, report_dir: {
            "path": path, "output": output, "report_dir": report_dir, "exit_code": 0,
        },
    )

    code = main(["reproduce", "run-dir", "--output", "new-run", "--report-dir", "report", "--json"])
    import json

    result = json.loads(capsys.readouterr().out)
    assert code == 0
    assert result["path"] == "run-dir"
    assert result["output"] == "new-run"
    assert result["report_dir"] == "report"
