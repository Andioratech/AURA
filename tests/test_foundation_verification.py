"""B-01/B-02 composition checks; hooks are test doubles, never a production runner."""

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

from aura import units
from aura.errors import IncompleteEvidenceError, InvalidInputError, MclfInvalidationError
from aura.mclf import AuditReport, evaluate_scenario
from aura.schema import canonical_quantity, dumps_document, load_document, loads_document

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/foundation"
REFERENCE = json.loads((FIXTURES / "known-answers.json").read_text())
REJECTIONS = json.loads((FIXTURES / "rejections.json").read_text())["cases"]
RUN = "EXAMPLE-FND05-RUN"


@pytest.fixture
def scenario():
    return json.loads((ROOT / "examples/schema/manufactured-scenario.json").read_text())


def audit(data, **kwargs):
    return evaluate_scenario(
        data, report_id="EXAMPLE-FND05-AUDIT", run_id=RUN, stage="pre", **kwargs
    )


def changed(scenario, case):
    data = deepcopy(scenario)
    parts = case["path"].strip("/").split("/")
    parent = data
    for key in parts[:-1]:
        parent = parent[int(key)] if isinstance(parent, list) else parent[key]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    if case.get("operation") == "remove":
        del parent[key]
    else:
        parent[key] = deepcopy(case["value"])
    return data


def encode(data, format):
    return json.dumps(data, allow_nan=False) if format == "json" else yaml.safe_dump(data)


def guarded_hooks(path, allocate, solve):
    """Test-only composition; RUN-01 must enforce this order in its real lifecycle."""
    record = load_document(path)
    report = audit(record.to_dict())
    report.require_accepted()
    context = allocate(record)
    return solve(record, context)


@pytest.mark.parametrize("case", REFERENCE["cases"], ids=lambda case: case["id"])
def test_frozen_b01_answers(case):
    actual = getattr(units, case["function"])(*case["args"])
    assert actual == pytest.approx(
        case["expected"], rel=REFERENCE["relative_tolerance"], abs=REFERENCE["absolute_tolerance"]
    )


@pytest.mark.parametrize("format", ["json", "yaml"])
def test_b01_07_equivalent_units_and_explicit_zero_survive_roundtrip(scenario, format):
    radius = canonical_quantity({"value": 1, "unit": "mm"}, expected_unit="m")
    assert radius == {"value": 0.001, "unit": "m"}
    assert canonical_quantity({"value": 0.001, "unit": "m"}, expected_unit="m") == radius
    scenario["bodies"][0]["geometry"]["radius"] = radius
    before = deepcopy(scenario)
    record = loads_document(encode(scenario, format), format=format)
    reloaded = loads_document(dumps_document(record, format=format), format=format)
    assert reloaded.to_dict() == before == scenario
    assert reloaded.to_dict()["gravity"] == {"value": [0, 0, 0], "unit": "m/s^2"}
    assert audit(reloaded.to_dict()).to_dict() == audit(before).to_dict()
    assert audit(before).verdict == "INDETERMINATE"


@pytest.mark.parametrize("case", REJECTIONS, ids=lambda case: case["id"])
@pytest.mark.parametrize("format", ["json", "yaml"])
def test_rejection_diagnostics_and_zero_hook_calls(scenario, case, format, tmp_path):
    data = changed(scenario, case)
    before = deepcopy(data)
    path = tmp_path / f"scenario.{format}"
    path.write_text(encode(data, format))
    allocate, solve = Mock(), Mock()
    with pytest.raises(InvalidInputError) as caught:
        guarded_hooks(path, allocate, solve)
    assert (caught.value.code, caught.value.path) == (
        case["reader_code"], case.get("diagnostic_path", case["path"])
    )
    allocate.assert_not_called()
    solve.assert_not_called()
    report = audit(data)
    assert report.verdict == "INVALIDATED"
    rule = next(check for check in report.checks if check.rule_id == case["rule"])
    assert any(
        (finding.code, finding.path, finding.verdict)
        == (
            case["audit_code"],
            "/scenario" + case.get("diagnostic_path", case["path"]),
            "INVALIDATED",
        )
        for finding in rule.findings
    )
    with pytest.raises(MclfInvalidationError) as gate:
        report.require_accepted()
        allocate(data)
        solve(data)
    assert (gate.value.code, gate.value.path) == ("MCLF_INVALIDATED", "/verdict")
    allocate.assert_not_called()
    solve.assert_not_called()
    assert data == before


@pytest.mark.parametrize("format", ["json", "yaml"])
def test_valid_snapshot_audit_and_gate_preserve_unknown_model(scenario, format, tmp_path):
    original = deepcopy(scenario)
    path = tmp_path / f"valid.{format}"
    path.write_text(encode(scenario, format))
    record = load_document(path)
    report = audit(record.to_dict())
    assert record.to_dict() == original
    assert report.to_dict() == audit(original).to_dict()
    assert report.verdict == "INDETERMINATE"
    allocate, solve = Mock(), Mock()
    with pytest.raises(IncompleteEvidenceError) as caught:
        guarded_hooks(path, allocate, solve)
    assert (caught.value.code, caught.value.path) == ("MCLF_INDETERMINATE", "/verdict")
    allocate.assert_not_called()
    solve.assert_not_called()
    exposed = record.to_dict()
    exposed["gravity"]["value"][2] = 9.80665
    assert record.to_dict() == original == scenario


def test_hook_positive_control_detects_a_deliberately_removed_gate(scenario, tmp_path, monkeypatch):
    # Sensitivity control only: this patch is never present in production or other tests.
    monkeypatch.setattr(AuditReport, "require_accepted", lambda self: None)
    path = tmp_path / "valid.json"
    path.write_text(encode(scenario, "json"))
    calls = Mock()
    calls.allocate.return_value = "test-context"
    calls.solve.return_value = "test-output"
    assert guarded_hooks(path, calls.allocate, calls.solve) == "test-output"
    assert [call[0] for call in calls.mock_calls] == ["allocate", "solve"]
    calls.allocate.assert_called_once()
    calls.solve.assert_called_once_with(calls.allocate.call_args.args[0], "test-context")


@pytest.mark.parametrize(
    "format,payload,code",
    [
        ("json", '{"schema_version":"1.0","schema_version":"2.0"}', "DUPLICATE_KEY"),
        ("yaml", "schema_version: '1.0'\nschema_version: '2.0'", "DUPLICATE_KEY"),
        ("json", '{"value": NaN}', "NONFINITE"),
        ("yaml", "value: .nan", "NONFINITE"),
        ("json", '{"value": 1e-999}', "NUMERIC_RANGE"),
        ("yaml", "value: 1.0e-999", "NUMERIC_RANGE"),
        ("yaml", '!!python/object/apply:builtins.str ["unsafe"]', "PARSE_ERROR"),
        ("yaml", "first: &x 1\nsecond: *x", "YAML_ALIAS"),
    ],
)
def test_ambiguous_or_unsafe_serialization_stops_hooks(format, payload, code, tmp_path):
    path = tmp_path / f"invalid.{format}"
    path.write_text(payload)
    allocate, solve = Mock(), Mock()
    with pytest.raises(InvalidInputError) as caught:
        guarded_hooks(path, allocate, solve)
    assert (caught.value.code, caught.value.path) == (code, "")
    allocate.assert_not_called()
    solve.assert_not_called()


def test_unlabeled_radius_and_pressure_mistakes_are_not_inferable(scenario):
    # The schema cannot know that a positive radius was copied from a diameter column.
    scenario["bodies"][0]["geometry"]["radius"]["value"] = 0.002
    record = loads_document(encode(scenario, "json"))
    assert record.to_dict()["bodies"][0]["geometry"]["radius"]["value"] == 0.002
    assert units.radius_from_diameter_m(0.002) == 0.001
    assert units.size_parameter_ka(0.002, 2) == pytest.approx(0.006283185307179586, rel=1e-12, abs=1e-15)
    assert units.size_parameter_ka(0.001, 2) == pytest.approx(0.003141592653589793, rel=1e-12, abs=1e-15)
    # For the frozen plane-progressive-wave toy only: peak=2 -> I=0.25; RMS=2 -> I=0.5.
    assert units.plane_progressive_wave_intensity_w_m2(
        units.sinusoid_peak_to_rms(2), 2, 4
    ) == pytest.approx(0.25, rel=1e-12, abs=1e-15)
    assert units.plane_progressive_wave_intensity_w_m2(2, 2, 4) == 0.5
    assert audit(record.to_dict()).verdict == "INDETERMINATE"


def manufactured_manifest(scenario):
    """Hand-authored declaration; the digest text does not identify actual bytes."""
    return {
        "document_type": "run_manifest", "schema_version": "1.0", "id": RUN,
        "experiment_id": "EXAMPLE-FND05-EXP", "scenario_id": scenario["id"],
        "claim_id": "EXAMPLE-FND05-CLAIM", "hypothesis": "Software checks only",
        "observables": ["hook_calls"], "timestamp_utc": "2026-10-02T00:00:00Z",
        "execution_status": "planned",
        "source": {"revision": "b" * 40, "dirty": False, "patch_sha256": None},
        "configuration_sha256": "a" * 64,
        "environment": {
            "lock": {"uri": "fixture://not-a-file", "sha256": "c" * 64}, "platform": "fixture"
        },
        "solver": deepcopy(scenario["solver"]), "seed": None,
        "resources": deepcopy(scenario["resources"]), "inputs": [], "outputs": [],
        "metrics": [], "convergence": [], "mclf_pre": {"status": "not_run"},
        "mclf_post": {"status": "not_run"}, "failure_code": None,
        "operator_notes": "Not an actual run or authenticated evidence",
    }


@pytest.mark.parametrize("digest", ["a" * 64, "d" * 64])
def test_changed_well_formed_hash_is_unchecked_and_cannot_open_gate(scenario, digest):
    manifest = manufactured_manifest(scenario)
    manifest["configuration_sha256"] = digest
    report = audit(scenario, manifest=manifest)
    rule = next(check for check in report.checks if check.rule_id == "R-008")
    assert any(
        (finding.code, finding.path, finding.verdict)
        == ("HASH_UNCHECKED", "/manifest", "INDETERMINATE") for finding in rule.findings
    )
    assert report.verdict == "INDETERMINATE"
    allocate, solve = Mock(), Mock()
    with pytest.raises(IncompleteEvidenceError, match="MCLF_INDETERMINATE"):
        report.require_accepted()
        allocate(scenario)
        solve(scenario)
    allocate.assert_not_called()
    solve.assert_not_called()


def test_malformed_hash_has_exact_diagnostic(scenario):
    manifest = manufactured_manifest(scenario)
    manifest["configuration_sha256"] = "not-a-sha256"
    with pytest.raises(InvalidInputError) as caught:
        loads_document(encode(manifest, "json"))
    assert (caught.value.code, caught.value.path) == ("SCHEMA_INVALID", "/configuration_sha256")
    report = audit(scenario, manifest=manifest)
    assert report.verdict == "INVALIDATED"
    assert any(
        (finding.code, finding.path) == ("SCHEMA_INVALID", "/manifest/configuration_sha256")
        for check in report.checks for finding in check.findings
    )


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_nonfinite_direct_input_blocks_gate(scenario, value):
    scenario["medium"]["density"]["value"] = value
    report = audit(scenario)
    assert any(
        check.rule_id == "R-004" and any(
            (finding.code, finding.path) == ("NONFINITE", "/scenario/medium/density/value")
            for finding in check.findings
        ) for check in report.checks
    )
    allocate, solve = Mock(), Mock()
    with pytest.raises(MclfInvalidationError, match="MCLF_INVALIDATED"):
        report.require_accepted()
        allocate(scenario)
        solve(scenario)
    allocate.assert_not_called()
    solve.assert_not_called()


@pytest.mark.parametrize(
    "supplied,expected,error_type",
    [
        ("INVALIDATED", "INVALIDATED", MclfInvalidationError),
        ("ALERT", "ALERT", IncompleteEvidenceError),
        ("INDETERMINATE", "INDETERMINATE", IncompleteEvidenceError),
        ("ACCEPTED", "INDETERMINATE", IncompleteEvidenceError),
    ],
)
def test_postcheck_cannot_promote_adverse_or_uncovered_result(scenario, supplied, expected, error_type):
    result = {
        "document_type": "force_result", "schema_version": "1.0",
        "id": "EXAMPLE-FND05-FORCE", "run_id": RUN,
        "body_id": scenario["bodies"][0]["id"], "frame": "chamber",
        "model_id": "fixture-force", "model_version": "0.0", "precision": "float64",
        "regime": ["Manufactured metadata, not a physical result"],
        "force": {"value": [0, 0, 0], "unit": "N"}, "torque": None,
        "torque_status": "unsupported", "validity": supplied,
        "provenance": deepcopy(scenario["provenance"]),
    }
    report = evaluate_scenario(
        scenario, report_id="EXAMPLE-FND05-POST", run_id=RUN, stage="post", result=result
    )
    assert report.verdict == expected
    promote = Mock()
    with pytest.raises(error_type) as caught:
        report.require_accepted()
        promote(result)
    assert (caught.value.code, caught.value.path) == ("MCLF_" + expected, "/verdict")
    promote.assert_not_called()
    assert result["validity"] == supplied


def test_larger_body_metadata_does_not_unlock_hooks(scenario, tmp_path):
    body = scenario["bodies"][0]
    body["geometry"] = {"kind": "box", "dimensions": {"value": [0.1, 0.2, 0.3], "unit": "m"}}
    body["mass"] = {"value": 6, "unit": "kg"}
    path = tmp_path / "box.json"
    path.write_text(encode(scenario, "json"))
    record = load_document(path)
    assert record.to_dict() == scenario
    report = audit(record.to_dict())
    assert report.verdict == "INDETERMINATE"
    assert any(
        finding.code == "MODEL_UNCOVERED"
        for check in report.checks for finding in check.findings
    )
    allocate, solve = Mock(), Mock()
    with pytest.raises(IncompleteEvidenceError, match="MCLF_INDETERMINATE"):
        guarded_hooks(path, allocate, solve)
    allocate.assert_not_called()
    solve.assert_not_called()
