import hashlib
import json
import sys
from pathlib import Path

import pytest

from aura.cli import main
from aura.errors import IncompleteEvidenceError, InvalidInputError
from aura.preflight import estimate_air_series, require_ready
from aura.runs.manifest import encode

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = json.loads((ROOT / "examples/schema/manufactured-scenario.json").read_text())


def workload(**changes):
    result = {
        "contract": "AIR-SERIES-WORKLOAD-1.1",
        "solver_model_id": "HASEGAWA-RIGID-SPHERE",
        "solver_model_version": "0.1",
        "gap_count": 2,
        "points_per_gap": 3,
        "harmonic_order": 4,
        "quadrature_order": 32,
        "bessel_argument_max": 10.0,
        "point_chunk_size": 2,
    }
    result.update(changes)
    return result


def calibration(**changes):
    result = {
        "contract": "AIR-SERIES-CALIBRATION-1.1",
        "solver_model_id": "HASEGAWA-RIGID-SPHERE",
        "solver_model_version": "0.1",
        "source_revision": "a" * 40,
        "environment_sha256": "b" * 64,
        "quadrature_order": 32,
        "bessel_argument_max": 10.0,
        "coefficient_seconds_per_order": 0.01,
        "field_seconds_per_order": 0.02,
        "safety_multiplier": 2,
    }
    result.update(changes)
    return result


def scenario(**caps):
    result = json.loads(json.dumps(SCENARIO))
    result["resources"].update(
        ram_bytes=8 * 1024**3,
        disk_bytes=2 * 1024**3,
        wall_time={"value": 3600, "unit": "s"},
    )
    result["resources"].update(caps)
    return result


def estimate(*args, **kwargs):
    kwargs.setdefault("available_ram_bytes", 8 * 1024**3)
    kwargs.setdefault("available_disk_bytes", 2 * 1024**3)
    if len(args) > 2 and args[2] is not None:
        kwargs.setdefault("current_source_revision", "a" * 40)
        kwargs.setdefault("current_environment_sha256", "b" * 64)
    return estimate_air_series(*args, **kwargs)


def test_estimate_counts_orders_chunks_ram_disk_and_calibrated_time():
    report = estimate(
        scenario(), workload(), calibration(), calibration_sha256="c" * 64,
        baseline_rss_bytes=1000,
    )

    assert report["status"] == "BUDGETS_WITHIN_CAPS"
    assert report["execution_authorized"] is False
    assert report["contract"] == "AIR-SERIES-PREFLIGHT-1.1"
    assert report["dimensions"] == {
        "gap_count": 2,
        "points_per_gap": 3,
        "total_points": 6,
        "harmonic_order": 4,
        "quadrature_order": 32,
        "bessel_argument_max": 10.0,
        "bessel_start": 42,
        "order_count": 5,
        "point_chunk_size": 2,
        "total_chunks": 4,
        "coefficient_order_updates": 15,
        "field_order_updates": 30,
    }
    assert report["estimates"]["wall_time_s"] == pytest.approx(1.5)
    assert report["estimates"]["disk_bytes"] == 6 * 2048 + 4 * 4096 + 4096
    assert report["estimates"]["ram_bytes"] > 2000
    assert report["calibration"]["calibration_sha256"] == "c" * 64
    assert report["components"]["quadrature_workspace_bytes"] > 0
    assert report["components"]["bessel_recurrence_scratch_bytes"] > 0
    require_ready(report)


def test_missing_runtime_calibration_is_indeterminate_and_cannot_execute():
    report = estimate(scenario(), workload(), baseline_rss_bytes=1000)
    assert report["status"] == "INDETERMINATE"
    assert report["reason"] == "RUNTIME_CALIBRATION_REQUIRED"
    assert report["estimates"]["wall_time_s"] is None
    with pytest.raises(IncompleteEvidenceError, match="calibration"):
        require_ready(report)


@pytest.mark.parametrize(
    "caps",
    [
        {"ram_bytes": 1},
        {"disk_bytes": 1},
        {"wall_time": {"value": 0.1, "unit": "s"}},
    ],
)
def test_any_individual_exceeded_cap_rejects(caps):
    report = estimate(
        scenario(**caps), workload(), calibration(), calibration_sha256="c" * 64,
        baseline_rss_bytes=1000,
    )
    assert report["status"] == "REJECTED"
    assert report["reason"] == "RESOURCE_BUDGET_EXCEEDED"
    with pytest.raises(InvalidInputError, match="exceeds declared caps"):
        require_ready(report)


@pytest.mark.parametrize(
    "available",
    [{"available_ram_bytes": 1}, {"available_disk_bytes": 1}],
)
def test_currently_available_resources_are_checked(available):
    report = estimate(
        scenario(), workload(), calibration(), calibration_sha256="c" * 64,
        baseline_rss_bytes=1000, **available,
    )
    assert report["status"] == "REJECTED"
    assert "CURRENTLY_AVAILABLE" in report["violations"][0]


@pytest.mark.parametrize(
    "changes,code",
    [
        ({"harmonic_order": True}, "PREFLIGHT_DIMENSION"),
        ({"quadrature_order": True}, "PREFLIGHT_DIMENSION"),
        ({"quadrature_order": 513}, "PREFLIGHT_QUADRATURE"),
        ({"bessel_argument_max": 1e9}, "PREFLIGHT_BESSEL_WORK"),
        ({"gap_count": 0}, "PREFLIGHT_DIMENSION"),
        ({"point_chunk_size": 257}, "PREFLIGHT_CHUNK"),
        ({"point_chunk_size": 4}, "PREFLIGHT_CHUNK"),
        ({"unexpected": 1}, "PREFLIGHT_WORKLOAD"),
    ],
)
def test_invalid_workload_rejected_before_estimation(changes, code):
    with pytest.raises(InvalidInputError) as caught:
        estimate(scenario(), workload(**changes), baseline_rss_bytes=1000)
    assert caught.value.code == code


def test_calibration_model_and_digest_must_match():
    with pytest.raises(InvalidInputError) as model_error:
        estimate(
            scenario(), workload(), calibration(solver_model_version="other"),
            calibration_sha256="c" * 64, baseline_rss_bytes=1000,
        )
    assert model_error.value.code == "PREFLIGHT_CALIBRATION_MODEL"
    with pytest.raises(InvalidInputError) as digest_error:
        estimate(
            scenario(), workload(), calibration(), calibration_sha256="bad",
            baseline_rss_bytes=1000,
        )
    assert digest_error.value.code == "PREFLIGHT_CALIBRATION_ID"


def test_calibration_quadrature_order_must_match_workload():
    with pytest.raises(InvalidInputError) as caught:
        estimate(
            scenario(), workload(), calibration(quadrature_order=64),
            calibration_sha256="c" * 64, baseline_rss_bytes=1000,
        )
    assert caught.value.code == "PREFLIGHT_CALIBRATION_DIMENSION"


def test_calibration_bessel_argument_must_match_workload():
    with pytest.raises(InvalidInputError) as caught:
        estimate(
            scenario(), workload(), calibration(bessel_argument_max=11.0),
            calibration_sha256="c" * 64, baseline_rss_bytes=1000,
        )
    assert caught.value.code == "PREFLIGHT_CALIBRATION_DIMENSION"


def test_stale_source_or_environment_calibration_is_indeterminate():
    report = estimate(
        scenario(), workload(), calibration(), calibration_sha256="c" * 64,
        baseline_rss_bytes=1000, current_source_revision="d" * 40,
    )
    assert report["status"] == "INDETERMINATE"
    assert report["reason"] == "CALIBRATION_CONTEXT_MISMATCH"
    assert report["estimates"]["wall_time_s"] is None
    assert report["calibration_context_match"] is False


def test_resource_integer_overflow_is_a_typed_rejection():
    with pytest.raises(InvalidInputError) as caught:
        estimate(
            scenario(), workload(gap_count=(1 << 63) - 1), baseline_rss_bytes=1000
        )
    assert caught.value.code == "PREFLIGHT_OVERFLOW"


def test_nonfinite_runtime_product_is_a_typed_rejection():
    with pytest.raises(InvalidInputError) as caught:
        estimate(
            scenario(), workload(),
            calibration(coefficient_seconds_per_order=1e308),
            calibration_sha256="c" * 64, baseline_rss_bytes=1000,
        )
    assert caught.value.code == "PREFLIGHT_OVERFLOW"


def test_preflight_does_not_import_a_field_backend():
    report = estimate(
        scenario(), workload(), calibration(), calibration_sha256="c" * 64,
        baseline_rss_bytes=1000,
    )
    assert report["status"] == "BUDGETS_WITHIN_CAPS"
    assert "aura.fields.numerical" not in sys.modules


def test_cli_reports_missing_calibration_without_running_a_solver(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr("aura.preflight._baseline_rss_bytes", lambda: 1000)
    monkeypatch.setattr("aura.preflight._available_ram_bytes", lambda: 8 * 1024**3)
    monkeypatch.setattr("aura.preflight._available_disk_bytes", lambda path: 2 * 1024**3)
    scenario_path = tmp_path / "scenario.json"
    workload_path = tmp_path / "workload.json"
    scenario_path.write_text(json.dumps(scenario()))
    workload_path.write_text(json.dumps(workload()))

    assert main([
        "preflight", str(scenario_path), "--workload", str(workload_path), "--json"
    ]) == 3
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "INDETERMINATE"
    assert output["reason"] == "RUNTIME_CALIBRATION_REQUIRED"
    assert "aura.fields.numerical" not in sys.modules


def test_cli_uses_and_binds_calibration_file(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr("aura.preflight._baseline_rss_bytes", lambda: 1000)
    monkeypatch.setattr("aura.preflight._available_ram_bytes", lambda: 8 * 1024**3)
    monkeypatch.setattr("aura.preflight._available_disk_bytes", lambda path: 2 * 1024**3)
    scenario_path = tmp_path / "scenario.json"
    workload_path = tmp_path / "workload.json"
    calibration_path = tmp_path / "calibration.json"
    scenario_path.write_text(json.dumps(scenario()))
    workload_path.write_text(json.dumps(workload()))
    environment = {"runtime": "test-env"}
    environment_sha256 = hashlib.sha256(encode(environment)).hexdigest()
    calibration_record = calibration(environment_sha256=environment_sha256)
    calibration_path.write_text(json.dumps(calibration_record))
    monkeypatch.setattr(
        "aura.runs.provenance.capture",
        lambda: ({"revision": "a" * 40}, environment, {}),
    )

    assert main([
        "preflight", str(scenario_path), "--workload", str(workload_path),
        "--calibration", str(calibration_path), "--json",
    ]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "BUDGETS_WITHIN_CAPS"
    assert output["execution_authorized"] is False
    assert output["calibration"]["calibration_sha256"] == __import__("hashlib").sha256(
        calibration_path.read_bytes()
    ).hexdigest()


@pytest.mark.parametrize(
    "payload,code",
    [
        (b'{"contract":"one","contract":"two"}', "DUPLICATE_KEY"),
        (b'{"value":NaN}', "NONFINITE_JSON"),
        (b"[]", "INPUT_JSON"),
        (b"[" * 1100 + b"0" + b"]" * 1100, "INPUT_JSON"),
    ],
)
def test_preflight_json_reader_rejects_ambiguous_documents(tmp_path, payload, code):
    from aura.cli import _load_preflight_json

    path = tmp_path / "request.json"
    path.write_bytes(payload)
    with pytest.raises(InvalidInputError) as caught:
        _load_preflight_json(str(path))
    assert caught.value.code == code


def test_preflight_json_reader_enforces_size_limit(tmp_path):
    from aura.cli import _load_preflight_json

    path = tmp_path / "oversized.json"
    path.write_bytes(b" " * (1024 * 1024 + 1))
    with pytest.raises(InvalidInputError) as caught:
        _load_preflight_json(str(path))
    assert caught.value.code == "INPUT_LIMIT"
