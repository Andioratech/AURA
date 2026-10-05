"""Lifecycle contract checks with manufactured runtime evidence only."""

import copy
import json
import math
import os
from pathlib import Path

import pytest

from aura.cli import main
from aura.errors import IncompleteEvidenceError, InvalidInputError
from aura.runs import check_run, execute, provenance
from aura.runs.hasegawa import DRIVER, VERSION, admit
from aura.runs.manifest import digest, encode
from aura.schema import Scenario, document_sha256

ROOT = Path(__file__).resolve().parents[1]
ENGINE = __import__("aura.runs.execute", fromlist=["execute"])


@pytest.fixture
def case(tmp_path):
    scenario = json.loads((ROOT / "examples/schema/manufactured-scenario.json").read_text())
    scenario["schema_version"] = "1.1"
    scenario["id"] = "TEST-HASEGAWA-SCENARIO"
    scenario["medium"].update(
        temperature={"value": 298.15, "unit": "K"},
        density={"value": 1.18, "unit": "kg/m^3"},
        sound_speed={"value": 346, "unit": "m/s"},
        dynamic_viscosity={"value": 0, "unit": "Pa*s"},
        amplitude_attenuation={"value": 0, "unit": "1/m"},
    )
    scenario["sources"]["frequency"] = {"value": 25230, "unit": "Hz"}
    source = scenario["sources"]["elements"][0]
    source.clear()
    source.update({
        "id": "PISTON-01", "position": {"value": [0, 0, 0], "unit": "m"},
        "normal": {"value": [0, 0, 1], "unit": "1"},
        "phase": {"value": 0, "unit": "rad"}, "model": "circular_piston",
        "aperture_radius": {"value": 0.01, "unit": "m"},
        "displacement_amplitude": {"value": 15e-6, "unit": "m"},
        "displacement_limit": {"value": 20e-6, "unit": "m"},
    })
    scenario["bodies"] = [scenario["bodies"][0]]
    body = scenario["bodies"][0]
    body["material"] = "rigid-sound-hard-reference"
    body["geometry"] = {"kind": "sphere", "radius": {"value": 0.025, "unit": "m"}}
    body["mass"] = {"value": 0.00146, "unit": "kg"}
    body["density"] = {"value": 22.3, "unit": "kg/m^3"}
    body["initial_state"]["position"] = {"value": [0, 0, 0.0251], "unit": "m"}
    body["initial_state"]["velocity"] = {"value": [0, 0, 0], "unit": "m/s"}
    scenario["domain"] = {
        "origin": {"value": [-0.05, -0.05, 0], "unit": "m"},
        "size": {"value": [0.1, 0.1, 0.1], "unit": "m"},
        "boundary_model": "analytic-window", "boundary_reference": "Diagnostic observation domain",
    }
    scenario["solver"].update(
        model_id=DRIVER, model_version=VERSION, equation_ids=["EQ-HASEGAWA-1985"],
        regime=["Stationary rigid sphere piston/sphere field diagnostic"], precision="complex128", parameters={},
    )
    scenario["resources"] = {
        "ram_bytes": 4 * 1024**3, "disk_bytes": 16 * 1024**2,
        "wall_time": {"value": 300, "unit": "s"},
    }
    gap = 0.0001
    distance = 0.025 + gap
    radius = 0.025
    theta = math.radians(120)
    point = [radius * math.sin(theta), 0, distance + radius * math.cos(theta)]
    request = {
        "contract": "HASEGAWA-FIELD-REQUEST-1.0", "case_id": "AIR-GAP-0P1MM-TEST",
        "gap_m": gap, "coordinates_m": [point], "max_order": 18,
        "quadrature_order": 256, "point_chunk_size": 1,
    }
    bound = admit(Scenario(scenario), request)
    protocol = encode(request)
    (tmp_path / "protocol.json").write_bytes(protocol)
    experiment = {
        "document_type": "experiment", "schema_version": "1.0", "id": "TEST-HASEGAWA-EXP",
        "scenario_id": scenario["id"], "scenario_sha256": document_sha256(Scenario(scenario)),
        "hypothesis": "Test-only software lifecycle fixture", "claim_id": "TEST-ONLY",
        "primary_observable": {"name": "complex_pressure", "unit": "Pa",
            "definition": "Serialized field sample for software lifecycle testing",
            "window": scenario["target"]["window"]},
        "acceptance_rule": "Bundle integrity only", "uncertainty_plan": "No physical claim",
        "protocol": {"uri": "protocol.json", "sha256": digest(protocol)},
        "provenance": scenario["provenance"],
    }
    scenario_path, experiment_path = tmp_path / "scenario.json", tmp_path / "experiment.json"
    scenario_path.write_bytes(encode(scenario))
    experiment_path.write_bytes(encode(experiment))
    output = tmp_path / "run"
    return scenario_path, experiment_path, output, scenario, request, bound


@pytest.fixture
def clean_environment(monkeypatch):
    source = {"revision": "a" * 40, "dirty": False, "patch_sha256": None,
              "package_files_sha256": {"src/aura/__init__.py": "b" * 64}}
    locks = {name: (ROOT / "requirements" / name).read_bytes() for name in provenance.LOCK_NAMES}
    inventory = json.loads(locks["environment-linux-py312.json"])
    environment = {
        "errors": [], "profile": inventory["profile"],
        "runtime": {"platform": "test-only", **{key: inventory[key] for key in
                   ("python", "implementation", "system", "machine")}},
        "installed": {"aura-science": "0.1.0", **{
            item["name"]: item["version"] for item in inventory["artifacts"]}},
        "input_sha256": {name: digest(data) for name, data in locks.items()},
    }
    monkeypatch.setattr(provenance, "capture", lambda: (copy.deepcopy(source), copy.deepcopy(environment), locks))
    original = os.sysconf
    monkeypatch.setattr(ENGINE.os, "sysconf", lambda name: (
        16 * 1024**3 // 4096 if name == "SC_AVPHYS_PAGES" else original(name)
    ))
    return source, environment, locks


def calibration_for(case, source, environment):
    _, _, _, _scenario, request, bound = case
    record = {
        "contract": "AIR-SERIES-CALIBRATION-1.1", "solver_model_id": DRIVER,
        "solver_model_version": VERSION, "source_revision": source["revision"],
        "environment_sha256": digest(encode(environment)), "quadrature_order": request["quadrature_order"],
        "bessel_argument_max": bound["maximum_argument"],
        "coefficient_seconds_per_order": 0.0001, "field_seconds_per_order": 0.0001,
        "safety_multiplier": 2,
    }
    return record


def test_missing_calibration_refuses_before_output_or_solver(case, clean_environment, monkeypatch):
    scenario, experiment, output, *_ = case
    from aura.fields import hasegawa as solver

    monkeypatch.setattr(solver, "evaluate_hasegawa_piston_sphere_field", lambda *a, **k: pytest.fail("solver called"))
    with pytest.raises(IncompleteEvidenceError, match="runtime calibration"):
        execute(scenario, experiment, output=output, seed=None)
    assert not output.exists()


def test_driver_admission_rejects_changed_frozen_medium_and_points(case):
    _, _, _, scenario, request, _ = case
    changed_medium = copy.deepcopy(scenario)
    changed_medium["medium"]["density"]["value"] = 1.2
    with pytest.raises(InvalidInputError, match="frozen 25 °C"):
        admit(Scenario(changed_medium), request)

    changed_domain = copy.deepcopy(scenario)
    changed_domain["domain"]["origin"]["value"][0] = -0.005
    changed_domain["domain"]["size"]["value"][0] = 0.01
    with pytest.raises(InvalidInputError, match="outside the declared Scenario domain"):
        admit(Scenario(changed_domain), request)


def test_driver_admission_accepts_binary64_roundoff_at_exact_sphere_surface(case):
    _, _, _, scenario, request, _ = case
    surface_request = copy.deepcopy(request)
    surface_request["coordinates_m"] = [[0.006470476127563019, 0.0, 0.049248145657226704]]
    assert admit(Scenario(scenario), surface_request)["radius_m"] == 0.025

    interior_request = copy.deepcopy(request)
    interior_request["coordinates_m"] = [[0.0, 0.0, 0.0251 + 0.025 - 1e-12]]
    with pytest.raises(InvalidInputError, match="on or outside the sphere"):
        admit(Scenario(scenario), interior_request)


def test_cli_reports_missing_calibration_as_indeterminate(case, clean_environment, tmp_path, capsys):
    scenario, experiment, output, *_ = case
    result = main([
        "run", str(scenario), "--experiment", str(experiment), "--output", str(output),
        "--no-randomness", "--json",
    ])
    report = json.loads(capsys.readouterr().out)
    assert result == 3
    assert report["error"]["code"] == "PREFLIGHT_CALIBRATION"
    assert not output.exists()


def test_calibrated_run_binds_workload_and_checks_immutable_bundle(case, clean_environment, tmp_path):
    scenario, experiment, output, *_ = case
    source, environment, _ = clean_environment
    calibration_path = tmp_path / "calibration.json"
    calibration_path.write_bytes(encode(calibration_for(case, source, environment)))
    result = execute(scenario, experiment, output=output, seed=None, calibration=calibration_path)
    assert result["execution_status"] == "completed"
    assert result["verdict"] == "INDETERMINATE"
    checked = check_run(output, expected_sha256=result["manifest_sha256"])
    assert checked["integrity"] == "VERIFIED"
    report = json.loads((output / "preflight.json").read_bytes())["num02_report"]
    assert report["status"] == "BUDGETS_WITHIN_CAPS"
    assert report["dimensions"]["total_chunks"] == 1
    from aura.fields.hasegawa import _workspace_estimate

    evaluator_workspace = _workspace_estimate(18, 1)
    assert report["components"]["incremental_ram_bytes"] >= evaluator_workspace


def test_exceeded_num02_cap_refuses_before_solver_or_output(case, clean_environment, tmp_path, monkeypatch):
    scenario_path, experiment_path, output, scenario, _request, _ = case
    source, environment, _ = clean_environment
    scenario["resources"]["ram_bytes"] = 1
    scenario_path.write_bytes(encode(scenario))
    experiment = json.loads(experiment_path.read_bytes())
    experiment["scenario_sha256"] = document_sha256(Scenario(scenario))
    experiment_path.write_bytes(encode(experiment))
    calibration_path = tmp_path / "calibration-over-cap.json"
    calibration_path.write_bytes(encode(calibration_for(case, source, environment)))
    from aura.fields import hasegawa as solver

    monkeypatch.setattr(solver, "evaluate_hasegawa_piston_sphere_field", lambda *a, **k: pytest.fail("solver called"))
    with pytest.raises(InvalidInputError, match="exceeds declared caps"):
        execute(scenario_path, experiment_path, output=output, seed=None, calibration=calibration_path)
    assert not output.exists()
