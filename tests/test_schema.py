"""Independent manufactured inputs; acceptance is structural, never physical proof."""

import json
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from aura.errors import InvalidInputError
from aura.schema import (
    Body,
    Scenario,
    dumps_document,
    load_document,
    loads_document,
    validate_document,
)
from aura.schema.quantities import MAX_BYTES, check_json_tree

FIXTURE = Path(__file__).resolve().parents[1] / "examples/schema/manufactured-scenario.json"


@pytest.fixture
def scenario():
    return json.loads(FIXTURE.read_text())


def envelope(kind, data):
    return {"document_type": kind, "schema_version": "1.0", **deepcopy(data)}


def records(scenario):
    """Build evidence metadata by hand, without reading schema definitions."""
    artifact = {"uri": "fixture://not-an-actual-output", "sha256": "a" * 64}
    provenance = deepcopy(scenario["provenance"])
    experiment = {
        "id": "EXAMPLE-EXP-01",
        "scenario_id": scenario["id"],
        "scenario_sha256": "b" * 64,
        "hypothesis": "Parser fixture survives serialization",
        "claim_id": "EXAMPLE-CLAIM-01",
        "primary_observable": {
            "name": "position",
            "unit": "m",
            "definition": "Fixture only",
            "window": deepcopy(scenario["target"]["window"]),
        },
        "acceptance_rule": "Exact structural equality",
        "uncertainty_plan": "No physical claim",
        "protocol": artifact,
        "provenance": provenance,
    }
    run = {
        "id": "EXAMPLE-RUN-01",
        "experiment_id": experiment["id"],
        "scenario_id": scenario["id"],
        "claim_id": experiment["claim_id"],
        "hypothesis": experiment["hypothesis"],
        "observables": ["position"],
        "timestamp_utc": "2026-10-02T12:00:00Z",
        "execution_status": "planned",
        "source": {"revision": "c" * 40, "dirty": False, "patch_sha256": None},
        "configuration_sha256": "b" * 64,
        "environment": {"lock": artifact, "platform": "Manufactured fixture"},
        "solver": deepcopy(scenario["solver"]),
        "seed": None,
        "resources": deepcopy(scenario["resources"]),
        "inputs": [],
        "outputs": [],
        "metrics": [],
        "convergence": [],
        "mclf_pre": {"status": "not_run"},
        "mclf_post": {"status": "not_run"},
        "failure_code": None,
        "operator_notes": "Metadata test, not a scientific run",
    }
    field = {
        "id": "EXAMPLE-FIELD-01",
        "run_id": run["id"],
        "frame": "chamber",
        "model_id": "fixture-only",
        "model_version": "0.0",
        "regime": ["Fixture only"],
        "coordinates": {"artifact": artifact, "unit": "m", "shape": [2, 3], "dtype": "float64"},
        "pressure": {"artifact": artifact, "unit": "Pa", "shape": [2], "dtype": "complex128"},
        "velocity": None,
        "phasor_convention": "exp(-iwt)",
        "amplitude_convention": "peak",
        "diagnostics": [],
        "provenance": provenance,
    }
    force = {
        "id": "EXAMPLE-FORCE-01",
        "run_id": run["id"],
        "body_id": scenario["bodies"][0]["id"],
        "frame": "chamber",
        "model_id": "fixture-only",
        "model_version": "0.0",
        "precision": "float64",
        "regime": ["Fixture only"],
        "force": {"value": [0, 0, 0], "unit": "N"},
        "torque": None,
        "torque_status": "unsupported",
        "validity": "INDETERMINATE",
        "provenance": provenance,
    }
    report = {
        "id": "EXAMPLE-AUDIT-01",
        "run_id": run["id"],
        "level": "L0",
        "verdict": "INDETERMINATE",
        "checks": [
            {
                "rule_id": "R-001",
                "verdict": "INDETERMINATE",
                "message": "Fixture only",
                "assumptions": [],
            }
        ],
        "limitations": ["No audit has been executed"],
    }
    return {
        "scenario": scenario,
        "medium": envelope("medium", scenario["medium"]),
        "body": envelope("body", scenario["bodies"][0]),
        "transducer_array": envelope("transducer_array", scenario["sources"]),
        "solver_spec": envelope("solver_spec", scenario["solver"]),
        "experiment": envelope("experiment", experiment),
        "run_manifest": envelope("run_manifest", run),
        "field_result": envelope("field_result", field),
        "force_result": envelope("force_result", force),
        "mclf_report": envelope("mclf_report", report),
    }


@pytest.mark.parametrize("format", ["json", "yaml"])
@pytest.mark.parametrize(
    "kind",
    [
        "scenario",
        "medium",
        "body",
        "transducer_array",
        "solver_spec",
        "experiment",
        "run_manifest",
        "field_result",
        "force_result",
        "mclf_report",
    ],
)
def test_all_record_roundtrips(scenario, format, kind):
    data = records(scenario)[kind]
    before = deepcopy(data)
    record = validate_document(data)
    assert loads_document(dumps_document(record, format=format), format=format).to_dict() == before
    assert data == before


def test_snapshot_isolated_and_immutable(scenario):
    record = Scenario(scenario)
    scenario["gravity"]["value"][0] = 9
    copy = record.to_dict()
    copy["gravity"]["value"][1] = 9
    assert record.to_dict()["gravity"]["value"] == [0, 0, 0]
    with pytest.raises(FrozenInstanceError):
        record._json = "{}"
    with pytest.raises(InvalidInputError, match="DOCUMENT_TYPE"):
        Body(scenario)


def test_larger_box_is_representable_without_granting_solver_support(scenario):
    body = scenario["bodies"][0]
    body["geometry"] = {"kind": "box", "dimensions": {"value": [0.01, 0.02, 0.03], "unit": "m"}}
    body["mass"]["value"] = 0.006
    result = validate_document(scenario).to_dict()
    assert result["bodies"][0]["geometry"]["kind"] == "box"
    assert result["solver"]["model_id"] == "fixture-only"


def replace(data, path, value):
    parts = path.strip("/").split("/")
    current = data
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    key = int(parts[-1]) if isinstance(current, list) else parts[-1]
    current[key] = value


@pytest.mark.parametrize(
    "path,value,code",
    [
        ("/schema_version", "2.0", "SCHEMA_VERSION"),
        ("/document_type", "unknown", "DOCUMENT_TYPE"),
        ("/id", "EXAMPLE\n", "SCHEMA_INVALID"),
        ("/medium/density/value", True, "SCHEMA_INVALID"),
        ("/medium/density/value", "1000", "SCHEMA_INVALID"),
        ("/medium/density/value", None, "SCHEMA_INVALID"),
        ("/medium/density/value", 0, "SCHEMA_INVALID"),
        ("/medium/density/value", -1, "SCHEMA_INVALID"),
        ("/medium/density/value", float("nan"), "NONFINITE"),
        ("/medium/density/value", float("inf"), "NONFINITE"),
        ("/medium/density/value", 10**400, "NONFINITE"),
        ("/medium/density/unit", "g/cm^3", "UNIT_MISMATCH"),
        ("/gravity/unit", "m/s", "UNIT_MISMATCH"),
        ("/gravity/value", [0, 0], "SCHEMA_INVALID"),
        ("/gravity/value/0", False, "SCHEMA_INVALID"),
        ("/frame", "body", "SCHEMA_INVALID"),
        ("/sources/phasor_convention", "exp(+iwt)", "SCHEMA_INVALID"),
        ("/sources/amplitude_convention", "rms", "SCHEMA_INVALID"),
        ("/sources/elements/0/normal/value", [2, 0, 0], "INCONSISTENT"),
        ("/bodies/0/initial_state/orientation/value", [0, 0, 0, 0], "INCONSISTENT"),
        ("/bodies/0/geometry/radius/value", -1, "SCHEMA_INVALID"),
        ("/bodies/0/geometry/kind", "mesh", "SCHEMA_INVALID"),
        ("/resources/ram_bytes", True, "SCHEMA_INVALID"),
    ],
)
def test_invalid_inputs_name_field_and_code(scenario, path, value, code):
    replace(scenario, path, value)
    with pytest.raises(InvalidInputError) as caught:
        validate_document(scenario)
    assert caught.value.code == code
    assert caught.value.path == path
    assert caught.value.as_dict()["path"] == path


@pytest.mark.parametrize(
    "path,value,error_path",
    [
        ("/target/window/end/value", 0.5, "/target/window"),
        (
            "/sources/elements/0/pressure_amplitude/value",
            11,
            "/sources/elements/0/pressure_amplitude",
        ),
        ("/bodies/0/initial_state/position/value", [2, 0, 0], "/bodies/0/initial_state/position"),
        ("/domain/size/value", [1e308, 1, 1], "/domain"),
        (
            "/medium/provenance/uncertainty_status",
            "reported",
            "/medium/provenance/uncertainty_reference",
        ),
    ],
)
def test_cross_field_rejections(scenario, path, value, error_path):
    scenario["target"]["window"]["start"]["value"] = 0.5
    if path == "/domain/size/value":
        scenario["domain"]["origin"]["value"][0] = 1e308
    replace(scenario, path, value)
    with pytest.raises(InvalidInputError) as caught:
        validate_document(scenario)
    assert caught.value.code == "INCONSISTENT"
    assert caught.value.path == error_path


@pytest.mark.parametrize("field", ["gravity", "medium", "resources"])
def test_no_implicit_physical_defaults(scenario, field):
    del scenario[field]
    with pytest.raises(InvalidInputError) as caught:
        validate_document(scenario)
    assert caught.value.path == "/" + field


@pytest.mark.parametrize("collection", ["bodies", "elements"])
def test_duplicate_identity(scenario, collection):
    items = scenario["bodies"] if collection == "bodies" else scenario["sources"]["elements"]
    items.append(deepcopy(items[0]))
    with pytest.raises(InvalidInputError, match="INCONSISTENT"):
        validate_document(scenario)


def test_unknown_fields_and_conditional_geometry(scenario):
    scenario["medium"]["unexpected"] = 0
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        validate_document(scenario)
    del scenario["medium"]["unexpected"]
    scenario["bodies"][0]["geometry"]["dimensions"] = {"value": [1, 1, 1], "unit": "m"}
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        validate_document(scenario)


def test_piston_aperture_required(scenario):
    source = scenario["sources"]["elements"][0]
    source["model"] = "circular_piston"
    with pytest.raises(InvalidInputError, match="aperture_radius"):
        validate_document(scenario)
    source["aperture_radius"] = {"value": 0.001, "unit": "m"}
    validate_document(scenario)


def test_scenario_11_circular_piston_uses_displacement_amplitude(scenario):
    source = scenario["sources"]["elements"][0]
    source.clear()
    source.update({
        "id": "PISTON-01",
        "position": {"value": [0, 0, 0], "unit": "m"},
        "normal": {"value": [0, 0, 1], "unit": "1"},
        "phase": {"value": 0, "unit": "rad"},
        "model": "circular_piston",
        "aperture_radius": {"value": 0.01, "unit": "m"},
        "displacement_amplitude": {"value": 15e-6, "unit": "m"},
        "displacement_limit": {"value": 20e-6, "unit": "m"},
    })
    scenario["schema_version"] = "1.1"
    validated = Scenario(scenario).to_dict()
    assert validated["sources"]["elements"][0]["displacement_amplitude"]["value"] == 15e-6
    assert "pressure_amplitude" not in validated["sources"]["elements"][0]

    source["pressure_amplitude"] = {"value": 1, "unit": "Pa"}
    source["pressure_limit"] = {"value": 2, "unit": "Pa"}
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        Scenario(scenario)


def test_versioned_spherical_source_contract(scenario):
    source = scenario["sources"]["elements"][0]
    source.pop("position")
    source.pop("normal")
    source.update(
        model="ideal_spherical_wave", model_contract="SPHERICAL-WAVE-1.0",
        center={"value": [0, 0, 0], "unit": "m"},
        reference_radius={"value": 0.000375, "unit": "m"},
        minimum_radius={"value": 0.000375, "unit": "m"},
    )
    validate_document(scenario)
    source["minimum_radius"]["value"] = 0.0005
    with pytest.raises(InvalidInputError, match="INCONSISTENT"):
        validate_document(scenario)
    source["minimum_radius"]["value"] = 0.000375
    source["model_contract"] = "SPHERICAL-WAVE-0.9"
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        validate_document(scenario)


@pytest.mark.parametrize(
    "kind,path,value",
    [
        ("run_manifest", "/source/dirty", True),
        ("run_manifest", "/execution_status", "failed"),
        ("run_manifest", "/execution_status", "completed"),
        ("run_manifest", "/failure_code", "UNEXPECTED"),
        ("run_manifest", "/timestamp_utc", "2026-02-31T12:00:00Z"),
        ("run_manifest", "/timestamp_utc", "2026-10-02T12:00:00+00:00"),
        ("run_manifest", "/configuration_sha256", "invalid"),
        ("run_manifest", "/configuration_sha256", "a" * 64 + "\n"),
        ("run_manifest", "/source/revision", "a" * 40 + "\n"),
        ("run_manifest", "/seed", True),
        ("field_result", "/pressure/shape", [3]),
        ("field_result", "/coordinates/unit", "Pa"),
        ("force_result", "/torque_status", "available"),
        ("mclf_report", "/verdict", "ACCEPTED"),
        ("mclf_report", "/checks/0/rule_id", "R-001\n"),
        ("experiment", "/primary_observable/window/start/value", 1),
    ],
)
def test_inconsistent_evidence_metadata(scenario, kind, path, value):
    data = records(scenario)[kind]
    replace(data, path, value)
    with pytest.raises(InvalidInputError):
        validate_document(data)


def test_failed_run_preserves_negative_result(scenario):
    data = records(scenario)["run_manifest"]
    data["execution_status"] = "failed"
    data["failure_code"] = "SOLVER_NOT_IMPLEMENTED"
    data["source"]["dirty"] = True
    data["source"]["patch_sha256"] = "d" * 64
    result = validate_document(data).to_dict()
    assert result["execution_status"] == "failed"
    assert result["mclf_post"] == {"status": "not_run"}


@pytest.mark.parametrize(
    "text,format,code",
    [
        ('{"id":1,"id":2}', "json", "DUPLICATE_KEY"),
        ('{"nested":{"id":1,"id":2}}', "json", "DUPLICATE_KEY"),
        ('{"x":NaN}', "json", "NONFINITE"),
        ('{"x":1e400}', "json", "NONFINITE"),
        ('{"x":1e-400}', "json", "NUMERIC_RANGE"),
        ('{"x":1} {"x":2}', "json", "PARSE_ERROR"),
        (b"\xff", "json", "PARSE_ERROR"),
        ("id: 1\nid: 2", "yaml", "DUPLICATE_KEY"),
        ("x: &value [1]\ny: *value", "yaml", "YAML_ALIAS"),
        ("x: !!python/object/apply:os.system ['echo unsafe']", "yaml", "PARSE_ERROR"),
        ("x: .nan", "yaml", "NONFINITE"),
        ("x: 1.0e-400", "yaml", "NUMERIC_RANGE"),
        ("x: 1\n---\nx: 2", "yaml", "PARSE_ERROR"),
        ("1: value", "yaml", "KEY_TYPE"),
        ("[]", "json", "INPUT_TYPE"),
        ("{}", "toml", "FORMAT"),
    ],
)
def test_strict_parsing(text, format, code):
    with pytest.raises(InvalidInputError) as caught:
        loads_document(text, format=format)
    assert caught.value.code == code


@pytest.mark.parametrize("format", ["json", "yaml"])
def test_resource_limits(format):
    with pytest.raises(InvalidInputError, match="INPUT_LIMIT"):
        loads_document(" " * (MAX_BYTES + 1), format=format)
    with pytest.raises(InvalidInputError, match="INPUT_LIMIT"):
        loads_document("[" * 70 + "0" + "]" * 70, format=format)


def test_python_tree_types_and_cycles():
    for value, code in [
        ({1: "x"}, "KEY_TYPE"),
        ({"x": (1, 2)}, "VALUE_TYPE"),
        ([0] * 100001, "INPUT_LIMIT"),
    ]:
        with pytest.raises(InvalidInputError, match=code):
            check_json_tree(value)
    cycle = []
    cycle.append(cycle)
    with pytest.raises(InvalidInputError, match="INPUT_LIMIT"):
        check_json_tree(cycle)


def test_file_reader_and_absent_file(tmp_path):
    assert isinstance(load_document(FIXTURE), Scenario)
    with pytest.raises(FileNotFoundError):
        load_document(tmp_path / "missing.json")
    path = tmp_path / "large.yaml"
    path.write_bytes(b" " * (MAX_BYTES + 1))
    with pytest.raises(InvalidInputError, match="INPUT_LIMIT"):
        load_document(path)


@pytest.mark.parametrize(
    "text,format,code",
    [
        ('{"x":' + "9" * 5000 + "}", "json", "NONFINITE"),
        ("x: " + "9" * 5000, "yaml", "NONFINITE"),
        ("x: 0100", "yaml", "NUMERIC_FORMAT"),
        ("x: 1:20", "yaml", "NUMERIC_FORMAT"),
        ("x: 1:20.0", "yaml", "NUMERIC_FORMAT"),
        ("x: 1.0e+400", "yaml", "NONFINITE"),
        ('{"x":1.0e-999999999999999999999999}', "json", "NUMERIC_RANGE"),
        ("x: 1.0e-999999999999999999999999", "yaml", "NUMERIC_RANGE"),
    ],
)
def test_numeric_parser_edge_cases(text, format, code):
    with pytest.raises(InvalidInputError) as caught:
        loads_document(text, format=format)
    assert caught.value.code == code


@pytest.mark.parametrize("kind", ["body", "transducer_array"])
def test_unit_vector_tolerance_boundary(scenario, kind):
    data = records(scenario)[kind]
    vector = (
        data["initial_state"]["orientation"]["value"]
        if kind == "body"
        else data["elements"][0]["normal"]["value"]
    )
    vector[0] = 1 + 5e-13
    assert validate_document(data).to_dict() == data  # No silent normalization.
    vector[0] = 1 + 2e-12
    with pytest.raises(InvalidInputError, match="INCONSISTENT"):
        validate_document(data)
