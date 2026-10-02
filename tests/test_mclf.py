"""Manufactured audit outcomes; no solver execution or physical evidence."""

import json
from copy import deepcopy
from dataclasses import FrozenInstanceError
from itertools import product
from pathlib import Path

import pytest

from aura.errors import IncompleteEvidenceError, InvalidInputError, MclfInvalidationError
from aura.mclf import AuditReport, Check, Finding, aggregate, evaluate_scenario

RUN = "EXAMPLE-RUN-AUDIT"
REPORT = "EXAMPLE-AUDIT-L0"


@pytest.fixture
def scenario():
    path = Path(__file__).resolve().parents[1] / "examples/schema/manufactured-scenario.json"
    return json.loads(path.read_text())


def force(scenario, verdict="ACCEPTED"):
    return {
        "document_type": "force_result",
        "schema_version": "1.0",
        "id": "EXAMPLE-FORCE",
        "run_id": RUN,
        "body_id": scenario["bodies"][0]["id"],
        "frame": "chamber",
        "model_id": "fixture-force",
        "model_version": "0.0",
        "precision": "float64",
        "regime": ["Manufactured metadata; not a physical result"],
        "force": {"value": [0, 0, 0], "unit": "N"},
        "torque": None,
        "torque_status": "unsupported",
        "validity": verdict,
        "provenance": deepcopy(scenario["provenance"]),
    }


def manifest(scenario):
    artifact = {"uri": "fixture://not-a-file", "sha256": "a" * 64}
    return {
        "document_type": "run_manifest",
        "schema_version": "1.0",
        "id": RUN,
        "experiment_id": "EXAMPLE-EXP",
        "scenario_id": scenario["id"],
        "claim_id": "EXAMPLE-CLAIM",
        "hypothesis": "Audit fixture only",
        "observables": ["force"],
        "timestamp_utc": "2026-10-02T00:00:00Z",
        "execution_status": "completed",
        "source": {"revision": "b" * 40, "dirty": False, "patch_sha256": None},
        "configuration_sha256": "a" * 64,
        "environment": {"lock": artifact, "platform": "fixture"},
        "solver": deepcopy(scenario["solver"]),
        "seed": None,
        "resources": deepcopy(scenario["resources"]),
        "inputs": [],
        "outputs": [artifact],
        "metrics": [],
        "convergence": [],
        "mclf_pre": {"status": "not_run"},
        "mclf_post": {"status": "not_run"},
        "failure_code": None,
        "operator_notes": "Fixture only",
    }


def field(scenario):
    artifact = {"uri": "fixture://not-a-file", "sha256": "a" * 64}
    return {
        "document_type": "field_result",
        "schema_version": "1.0",
        "id": "EXAMPLE-FIELD",
        "run_id": RUN,
        "frame": "chamber",
        "model_id": scenario["solver"]["model_id"],
        "model_version": scenario["solver"]["model_version"],
        "regime": ["Fixture only"],
        "coordinates": {"artifact": artifact, "unit": "m", "shape": [2, 3], "dtype": "float64"},
        "pressure": {"artifact": artifact, "unit": "Pa", "shape": [2], "dtype": "complex128"},
        "velocity": None,
        "phasor_convention": "exp(-iwt)",
        "amplitude_convention": "peak",
        "diagnostics": [],
        "provenance": deepcopy(scenario["provenance"]),
    }


def audit(scenario, **kwargs):
    return evaluate_scenario(
        scenario, report_id=REPORT, run_id=RUN, stage=kwargs.pop("stage", "pre"), **kwargs
    )


def check(report, rule):
    return next(item for item in report.checks if item.rule_id == rule)


def mutate(data, path, value):
    parts = path.split("/")[1:]
    for part in parts[:-1]:
        data = data[int(part)] if type(data) is list else data[part]
    data[int(parts[-1]) if type(data) is list else parts[-1]] = value


def test_valid_pre_audit_never_claims_unavailable_physics(scenario):
    before = deepcopy(scenario)
    report = audit(scenario)
    assert report.verdict == "INDETERMINATE"
    assert [item.rule_id for item in report.checks] == [f"R-{n:03d}" for n in range(1, 11)]
    assert all(check(report, f"R-{n:03d}").verdict == "ACCEPTED" for n in range(1, 8))
    assert check(report, "R-008").verdict == "INDETERMINATE"
    assert check(report, "R-009").verdict == "INDETERMINATE"
    assert check(report, "R-010").verdict == "ACCEPTED"
    assert scenario == before


@pytest.mark.parametrize(
    "verdicts", list(product(("ACCEPTED", "INDETERMINATE", "ALERT", "INVALIDATED"), repeat=3))
)
def test_complete_severity_matrix(verdicts):
    expected = (
        "INVALIDATED"
        if "INVALIDATED" in verdicts
        else "ALERT"
        if "ALERT" in verdicts
        else "INDETERMINATE"
        if "INDETERMINATE" in verdicts
        else "ACCEPTED"
    )
    assert aggregate(verdicts) == expected
    assert aggregate(reversed(verdicts)) == expected


def test_empty_or_unknown_verdicts_cannot_pass():
    assert aggregate(()) == "INDETERMINATE"
    for value in ("PASS", "accepted", None, True, {}):
        with pytest.raises(InvalidInputError, match="VERDICT"):
            aggregate((value,))


@pytest.mark.parametrize(
    "path,value,rule",
    [
        ("/schema_version", "2.0", "R-001"),
        ("/medium/density/value", True, "R-001"),
        ("/medium/density/unit", "g/cm^3", "R-003"),
        ("/medium/density/value", float("nan"), "R-004"),
        ("/medium/density/value", float("inf"), "R-004"),
        ("/medium/density/value", -1, "R-005"),
        ("/gravity/value", [0, 0], "R-006"),
        ("/frame", "body", "R-006"),
        ("/bodies/0/initial_state/orientation/value", [2, 0, 0, 0], "R-006"),
        ("/sources/elements/0/normal/value", [0, 0, 0], "R-006"),
        ("/sources/amplitude_convention", "rms", "R-007"),
        ("/sources/phasor_convention", "exp(+iwt)", "R-007"),
        ("/conventions", "unknown", "R-007"),
        ("/sources/elements/0/pressure_amplitude/value", 20, "R-005"),
        ("/target/window/end/value", 0, "R-005"),
    ],
)
def test_independent_expected_rule_and_path(scenario, path, value, rule):
    mutate(scenario, path, value)
    report = audit(scenario)
    assert report.verdict == "INVALIDATED"
    assert check(report, rule).verdict == "INVALIDATED"
    assert any(
        item.path == "/scenario" + path or item.path == "/scenario" + path.rsplit("/", 1)[0]
        for item in check(report, rule).findings
    )
    assert check(report, "R-009").verdict == "INDETERMINATE"


def test_all_missing_fields_are_named(scenario):
    del scenario["medium"]["temperature"]
    del scenario["gravity"]
    report = audit(scenario)
    paths = {item.path for item in check(report, "R-002").findings}
    assert {"/scenario/medium/temperature", "/scenario/gravity"} <= paths
    assert report.verdict == "INVALIDATED"


def test_multiple_semantic_failures_survive_one_report(scenario):
    scenario["bodies"][0]["initial_state"]["orientation"]["value"] = [2, 0, 0, 0]
    scenario["sources"]["elements"][0]["pressure_amplitude"]["value"] = 20
    scenario["target"]["window"]["start"]["value"] = 2
    scenario["bodies"].append(deepcopy(scenario["bodies"][0]))
    report = audit(scenario)
    for rule in ("R-005", "R-006", "R-008"):
        assert check(report, rule).verdict == "INVALIDATED"
    assert {item.code for item in check(report, "R-005").findings} >= {
        "TIME_WINDOW",
        "SOURCE_LIMIT",
    }


@pytest.mark.parametrize(
    "verdict,expected",
    [
        ("ACCEPTED", "INDETERMINATE"),
        ("ALERT", "ALERT"),
        ("INDETERMINATE", "INDETERMINATE"),
        ("INVALIDATED", "INVALIDATED"),
    ],
)
def test_post_result_labels_do_not_override_review(scenario, verdict, expected):
    report = audit(
        scenario, stage="post", result=force(scenario, verdict), manifest=manifest(scenario)
    )
    assert report.verdict == expected
    assert check(report, "R-009").verdict == "INDETERMINATE"
    assert check(report, "R-008").verdict == "INDETERMINATE"  # Digests not authenticated.


def test_hard_failure_preserves_warning_and_missing_coverage(scenario):
    result = force(scenario, "ALERT")
    scenario["medium"]["density"]["value"] = -1
    report = audit(scenario, stage="post", result=result)
    assert report.verdict == "INVALIDATED"
    assert check(report, "R-010").verdict == "ALERT"
    assert check(report, "R-009").verdict == "INDETERMINATE"
    assert "INHERITED_VERDICT" in report.to_json()


def test_missing_result_and_wrong_stage(scenario):
    assert check(audit(scenario, stage="post"), "R-010").verdict == "INVALIDATED"
    assert check(audit(scenario, result=force(scenario)), "R-010").verdict == "INVALIDATED"
    with pytest.raises(InvalidInputError, match="AUDIT_STAGE"):
        audit(scenario, stage="unknown")


@pytest.mark.parametrize(
    "record,path,value",
    [
        ("manifest", "/id", "OTHER"),
        ("manifest", "/scenario_id", "OTHER"),
        ("manifest", "/solver/model_id", "OTHER"),
        ("result", "/run_id", "OTHER"),
        ("result", "/body_id", "OTHER"),
    ],
)
def test_record_identity_mismatch(scenario, record, path, value):
    documents = {"manifest": manifest(scenario), "result": force(scenario)}
    mutate(documents[record], path, value)
    report = audit(scenario, stage="post", **documents)
    assert check(report, "R-008").verdict == "INVALIDATED"
    assert report.verdict == "INVALIDATED"


def test_duplicate_source_identity(scenario):
    scenario["sources"]["elements"].append(deepcopy(scenario["sources"]["elements"][0]))
    report = audit(scenario)
    assert check(report, "R-008").verdict == "INVALIDATED"


def test_failed_execution_is_retained(scenario):
    data = manifest(scenario)
    data["execution_status"] = "failed"
    data["failure_code"] = "EXAMPLE_FAILURE"
    report = audit(scenario, stage="post", result=force(scenario), manifest=data)
    assert check(report, "R-010").verdict == "INVALIDATED"
    assert "EXECUTION_INCOMPLETE" in report.to_text()
    assert data["failure_code"] == "EXAMPLE_FAILURE"


def test_external_fields_are_not_validated_by_metadata(scenario):
    report = audit(scenario, stage="post", result=field(scenario), manifest=manifest(scenario))
    assert report.verdict == "INDETERMINATE"
    assert check(report, "R-004").verdict == "INDETERMINATE"
    assert check(report, "R-010").verdict == "INDETERMINATE"
    assert "EXTERNAL_SAMPLES_UNCHECKED" in report.to_text()


def test_field_model_and_sample_shapes_are_checked(scenario):
    data = field(scenario)
    data["model_version"] = "other"
    assert check(audit(scenario, stage="post", result=data), "R-008").verdict == "INVALIDATED"
    data = field(scenario)
    data["pressure"]["shape"] = [3]
    assert check(audit(scenario, stage="post", result=data), "R-006").verdict == "INVALIDATED"


def test_reports_are_immutable_and_serializable(scenario):
    report = audit(scenario)
    with pytest.raises(FrozenInstanceError):
        report.stage = "post"
    with pytest.raises(FrozenInstanceError):
        report.checks[0].findings[0].message = "different"
    encoded = json.loads(report.to_json())
    assert encoded == report.to_dict()
    assert encoded["audit_version"] == "L0-1.0"
    assert encoded["report"] == report.to_record().to_dict()
    encoded["report"]["verdict"] = "ACCEPTED"
    assert report.verdict == "INDETERMINATE"
    assert "not scientific acceptance" in report.to_text()


def test_missing_duplicate_and_mutable_check_sets_fail(scenario):
    report = audit(scenario)
    for checks in (
        report.checks[:-1],
        report.checks[:-1] + (report.checks[0],),
        list(report.checks),
    ):
        with pytest.raises(InvalidInputError, match="RULE_SET"):
            AuditReport(REPORT, RUN, "pre", checks)
    with pytest.raises(InvalidInputError, match="FINDING_TYPE"):
        Check("R-001", [Finding("ACCEPTED", "TEST", "", "fixture")])


@pytest.mark.parametrize("value", [None, [], True, {"x": object()}])
def test_malformed_root_returns_failure_report(value):
    report = audit(value)
    assert report.verdict == "INVALIDATED"
    assert len(report.checks) == 10


def test_limits_and_cycles_fail_closed(scenario):
    oversized = deepcopy(scenario)
    oversized["provenance"]["reference"] = "x" * (1024 * 1024)
    assert audit(oversized).verdict == "INVALIDATED"
    cycle = {}
    cycle["self"] = cycle
    assert audit(cycle).verdict == "INVALIDATED"
    noisy = deepcopy(scenario)
    noisy["bodies"] = [{} for _ in range(100)]
    report = audit(noisy)
    assert report.verdict == "INVALIDATED"
    assert "AUDIT_LIMIT" in report.to_json()


def test_larger_geometry_cannot_gain_model_coverage(scenario):
    scenario["bodies"][0]["geometry"] = {
        "kind": "box",
        "dimensions": {"value": [0.1, 0.2, 0.3], "unit": "m"},
    }
    report = audit(scenario)
    assert report.verdict == "INDETERMINATE"
    assert check(report, "R-009").verdict == "INDETERMINATE"


def test_audit_does_not_call_scientific_helpers_or_open_artifacts(scenario, monkeypatch):
    from aura import units

    def forbidden(*args, **kwargs):
        pytest.fail("Audit attempted scientific helper execution or artifact I/O")

    for name in (
        "wavelength_m",
        "wave_number_rad_m",
        "size_parameter_ka",
        "plane_progressive_wave_intensity_w_m2",
    ):
        monkeypatch.setattr(units, name, forbidden)
    monkeypatch.setattr("builtins.open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    report = audit(scenario, stage="post", result=field(scenario), manifest=manifest(scenario))
    assert report.verdict == "INDETERMINATE"


@pytest.mark.parametrize("error,expected", [(5e-13, "ACCEPTED"), (2e-12, "INVALIDATED")])
def test_norm_boundary_and_no_silent_normalization(scenario, error, expected):
    original = 1 + error
    scenario["sources"]["elements"][0]["normal"]["value"][0] = original
    assert check(audit(scenario), "R-006").verdict == expected
    assert scenario["sources"]["elements"][0]["normal"]["value"][0] == original


def test_post_inline_nonfinite_output_invalidates(scenario):
    data = force(scenario)
    data["force"]["value"][1] = float("inf")
    report = audit(scenario, stage="post", result=data)
    assert check(report, "R-004").verdict == "INVALIDATED"
    assert any(item.path == "/result/force/value/1" for item in check(report, "R-004").findings)


def test_manifest_date_semantics_are_not_skipped(scenario):
    data = manifest(scenario)
    data["timestamp_utc"] = "2026-02-31T00:00:00Z"
    assert audit(scenario, manifest=data).verdict == "INVALIDATED"


@pytest.mark.parametrize(
    "verdict,error_type,code",
    [
        ("INVALIDATED", MclfInvalidationError, "MCLF_INVALIDATED"),
        ("ALERT", IncompleteEvidenceError, "MCLF_ALERT"),
        ("INDETERMINATE", IncompleteEvidenceError, "MCLF_INDETERMINATE"),
    ],
)
def test_explicit_acceptance_gate_uses_typed_errors(scenario, verdict, error_type, code):
    report = audit(scenario, stage="post", result=force(scenario, verdict))
    with pytest.raises(error_type) as caught:
        report.require_accepted()
    assert caught.value.code == code
    assert caught.value.path == "/verdict"


def test_declared_report_gate_is_not_an_authentication_mechanism():
    # Test the generic container's ACCEPTED branch with explicitly manufactured labels.
    # The real evaluator cannot emit this while its model registry is uncovered.
    checks = tuple(
        Check(f"R-{n:03d}", (Finding("ACCEPTED", "FIXTURE", "", "Manufactured label"),))
        for n in range(1, 11)
    )
    report = AuditReport(REPORT, RUN, "pre", checks)
    assert report.require_accepted() is None
