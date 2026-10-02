"""Run the frozen ANA-REF-1.0 field recorder matrix into ignored results/."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from aura.analysis.ana07_metrics import (
    FAMILY_FIXTURES,
    _fixture,
    analyze_recorded_case,
    frozen_case,
)
from aura.runs import check_run, execute
from aura.runs.manifest import digest, encode
from aura.schema import Scenario, document_sha256

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "verification" / "ANA-07" / "ANA-07-MATRIX-ANA-REF-1.0"


def _source_wave(base_element: dict, wave: dict, index: int) -> dict:
    element = copy.deepcopy(base_element)
    element["id"] = "SOURCE-ANA07-" + str(index + 1)
    element["position"]["value"] = wave["reference_m"]
    element["normal"]["value"] = wave["direction"]
    element["phase"]["value"] = wave["phase_rad"]
    element["pressure_amplitude"]["value"] = wave["peak_pressure_pa"]
    element["model"] = "ideal_plane_wave"
    return element


def _spherical_source(base_element: dict, wave: dict) -> dict:
    element = copy.deepcopy(base_element)
    element.pop("position", None)
    element.pop("normal", None)
    element.update(
        model="ideal_spherical_wave",
        model_contract="SPHERICAL-WAVE-1.0",
        center={"value": wave["center_m"], "unit": "m"},
        reference_radius={"value": wave["reference_radius_m"], "unit": "m"},
        minimum_radius={"value": wave["minimum_radius_m"], "unit": "m"},
        phase={"value": wave["phase_rad"], "unit": "rad"},
        pressure_amplitude={"value": wave["peak_pressure_pa"], "unit": "Pa"},
    )
    return element


def _prepare(case_id: str, family: str, case: dict, base: dict) -> tuple[dict, dict, bytes]:
    scenario = copy.deepcopy(base)
    scenario["id"] = "SCENARIO-ANA07-" + case_id
    medium, sources = scenario["medium"], scenario["sources"]
    reference_waves = [case["wave"]] if family in ("B03", "B06") else (
        [case["forward"], case["backward"]] if family == "B04" else
        [case["first"], case["second"]]
    )
    primary = reference_waves[0]
    base_element = copy.deepcopy(sources["elements"][0])
    medium["density"]["value"] = primary["density_kg_m3"]
    medium["sound_speed"]["value"] = primary["sound_speed_m_s"]
    medium["dynamic_viscosity"]["value"] = primary["dynamic_viscosity_pa_s"]
    medium["amplitude_attenuation"]["value"] = primary["amplitude_attenuation_per_m"]
    sources["frequency"]["value"] = primary["frequency_hz"]
    sources["elements"] = []
    for index, wave in enumerate(reference_waves):
        element = (
            _spherical_source(base_element, wave) if family == "B06"
            else _source_wave(base_element, wave, index)
        )
        sources["elements"].append(element)
    low, high = case["box_min_m"], case["box_max_m"]
    scenario["domain"]["origin"]["value"] = low
    scenario["domain"]["size"]["value"] = [b - a for a, b in zip(low, high, strict=True)]
    scenario["bodies"][0]["initial_state"]["position"]["value"] = [0, 0, 0]
    spherical = family == "B06"
    scenario["solver"].update(
        model_id="analytic-spherical-field" if spherical else "analytic-plane-field",
        model_version="1.0",
        equation_ids=["EQ-010"] if spherical else (
            ["EQ-007"] if family == "B03" else ["EQ-008"]
        ),
        regime=["Manufactured ideal spherical-wave field; no body coupling"] if spherical else
            ["Manufactured ideal plane-wave field; no body coupling"],
        precision="complex128",
        parameters={},
    )
    scenario["resources"] = {
        "ram_bytes": 4 * 1024**3,
        "disk_bytes": 16 * 1024**2,
        "wall_time": {"value": 30, "unit": "s"},
    }
    request = {
        "contract": "FIELD-REQUEST-1.0",
        "case_id": case_id,
        "box_min_m": low,
        "box_max_m": high,
        "coordinates_m": case["coordinates_m"],
    }
    request_bytes = encode(request)
    experiment = {
        "document_type": "experiment",
        "schema_version": "1.0",
        "id": "EXP-ANA07-" + case_id,
        "scenario_id": scenario["id"],
        "scenario_sha256": document_sha256(Scenario(scenario)),
        "hypothesis": "Recorded manufactured field agrees with its frozen analytic reference",
        "claim_id": "ANA07-SOFTWARE-COMPARISON-ONLY",
        "primary_observable": {
            "name": "incident_field",
            "unit": "Pa",
            "definition": "Recorded ideal incident pressure, velocity and pressure gradient",
            "window": scenario["target"]["window"],
        },
        "acceptance_rule": "ANA-REF-1.0 component-wise normalized errors do not exceed 2048*2^-52",
        "uncertainty_plan": "Manufactured mathematical verification only; no experimental uncertainty claim",
        "protocol": {"uri": "field-request.json", "sha256": digest(request_bytes)},
        "provenance": scenario["provenance"],
    }
    return scenario, experiment, request_bytes


def _clean_source() -> str:
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("Campaign execution requires a clean Git source checkout")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def run_matrix(output: Path = DEFAULT_OUTPUT) -> dict:
    revision = _clean_source()
    if output.exists():
        raise FileExistsError(f"Refusing to replace an existing immutable campaign: {output}")
    output.mkdir(parents=True)
    (output / "runs").mkdir()
    (output / "reports").mkdir()
    base = json.loads((ROOT / "examples/schema/manufactured-scenario.json").read_text())
    case_records = []
    expected_samples = 0
    for family, fixture_name in FAMILY_FIXTURES.items():
        fixture, _ = _fixture(family)
        for reference_case in fixture["cases"]:
            case_id = reference_case["id"]
            _, case, fixture_sha256 = frozen_case(case_id)
            expected_samples += len(case["coordinates_m"])
            case_dir = output / "runs" / case_id
            case_dir.mkdir()
            scenario_path = case_dir / "scenario-input.json"
            experiment_path = case_dir / "experiment-input.json"
            request_path = case_dir / "field-request.json"
            bundle_path = case_dir / "bundle"
            record = {
                "case_id": case_id,
                "family": family,
                "fixture": fixture_name,
                "fixture_sha256": fixture_sha256,
            }
            try:
                scenario, experiment, request_bytes = _prepare(case_id, family, case, base)
                scenario_path.write_bytes(encode(scenario))
                experiment["protocol"]["uri"] = request_path.name
                request_path.write_bytes(request_bytes)
                experiment_path.write_bytes(encode(experiment))
                record.update(
                    request_sha256=digest(request_bytes),
                    scenario_sha256=digest(scenario_path.read_bytes()),
                    experiment_sha256=digest(experiment_path.read_bytes()),
                )
                run = execute(scenario_path, experiment_path, output=bundle_path, seed=None)
                record.update(
                    execution_status=run["execution_status"],
                    run_id=run.get("run_id"),
                    manifest_sha256=run.get("manifest_sha256"),
                    execution_error=run.get("error"),
                )
                checked = check_run(bundle_path, expected_sha256=run.get("manifest_sha256"))
                record.update(integrity=checked["integrity"], verdict=checked["verdict"])
                record["bundle_bytes"] = sum(
                    path.stat().st_size for path in bundle_path.iterdir() if path.is_file()
                )
                if run["execution_status"] == "completed" and checked["integrity"] == "VERIFIED":
                    report = analyze_recorded_case(
                        bundle_path, expected_manifest_sha256=run["manifest_sha256"]
                    )
                    report_path = output / "reports" / (case_id + ".json")
                    report_raw = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
                    report_path.write_bytes(report_raw)
                    (report_path.parent / (report_path.name + ".sha256")).write_text(
                        digest(report_raw) + "\n", encoding="ascii"
                    )
                    preflight = json.loads((bundle_path / "preflight.json").read_text())
                    execution = json.loads((bundle_path / "execution.json").read_text())
                    record.update(
                        numerical_comparison=report["numerical_comparison"],
                        report_sha256=digest(report_raw),
                        samples=report["sample_count"],
                        errors=report["metrics"],
                        runtime_s=execution["elapsed_s"],
                        ram_preflight_bytes=preflight["ram_bytes"],
                    )
                else:
                    record.update(numerical_comparison="NOT_RUN", failure=run.get("error"))
            except Exception as exc:  # noqa: BLE001 - preserve case failures and continue fixed matrix.
                record.update(
                    integrity=record.get("integrity", "NOT_ESTABLISHED"),
                    numerical_comparison="NOT_RUN",
                    failure={"type": type(exc).__name__, "message": str(exc)},
                )
            case_records.append(record)
    index = {
        "contract": "ANA-07-MATRIX-1.0",
        "protocol": "ANA-REF-1.0",
        "source_revision": revision,
        "campaign_runner_sha256": digest(Path(__file__).read_bytes()),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "configuration_count": len(case_records),
        "expected_sample_count": expected_samples,
        "sample_count_compared": sum(item.get("samples", 0) for item in case_records),
        "case_outcomes": case_records,
        "execution": "PASS" if len(case_records) == 32 and all(
            item.get("execution_status") == "completed" for item in case_records
        ) else "FAIL_OR_INCOMPLETE",
        "record_integrity": "PASS" if len(case_records) == 32 and all(
            item.get("integrity") == "VERIFIED" for item in case_records
        ) else "FAIL_OR_INCOMPLETE",
        "numerical_comparison": "PASS" if all(
            item["numerical_comparison"] == "PASS" for item in case_records
        ) else "FAIL_OR_INCOMPLETE",
        "physical_validation": "NOT_ESTABLISHED",
        "limits": [
            "This 32-configuration matrix covers frozen B-03/B-04/B-05 plane-wave and B-06 ideal spherical-wave cases.",
            "No measured water, physical radiator, body coupling, force, motion or microgravity result.",
        ],
    }
    raw = (json.dumps(index, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    (output / "index.json").write_bytes(raw)
    (output / "index.json.sha256").write_text(digest(raw) + "\n", encoding="ascii")
    return index


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run_matrix(args.output)
    print(json.dumps({
        "output": str(args.output),
        "source_revision": result["source_revision"],
        "configuration_count": result["configuration_count"],
        "expected_sample_count": result["expected_sample_count"],
        "sample_count_compared": result["sample_count_compared"],
        "execution": result["execution"],
        "record_integrity": result["record_integrity"],
        "numerical_comparison": result["numerical_comparison"],
        "physical_validation": result["physical_validation"],
    }, sort_keys=True))
    return 0 if result["numerical_comparison"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
