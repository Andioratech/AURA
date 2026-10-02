"""Independent comparisons for recorded ANA-REF-1.0 B-03/B-04/B-05 cases."""

from __future__ import annotations

import argparse
import json
import math
from importlib.resources import files
from pathlib import Path

from aura.runs import check_run
from aura.runs.manifest import decode, digest

from . import references

PROTOCOL = "ANA-REF-1.0"
EPSILON = 2.0**-52
TOLERANCE = 2048 * EPSILON
FAMILY_FIXTURES = {
    "B03": "ANA-REF-1.0-B03.json",
    "B04": "ANA-REF-1.0-B04.json",
    "B05": "ANA-REF-1.0-B05.json",
}
CASE_ALIASES = {"B03-01": ("B03-AXIAL", 0)}
ORACLES = {"B03": references.reference_b03, "B04": references.reference_b04,
           "B05": references.reference_b05}


def _fixture(family: str) -> tuple[dict, bytes]:
    name = FAMILY_FIXTURES[family]
    raw = files("aura.analysis").joinpath("data", name).read_bytes()
    return json.loads(raw), raw


def frozen_case(case_id: str) -> tuple[str, dict, str]:
    """Return the exact case definition and frozen file hash for an admitted case ID."""
    family = case_id.split("-", 1)[0]
    if family not in FAMILY_FIXTURES:
        raise ValueError(f"Unsupported ANA-REF-1.0 recorded family: {family}")
    fixture, raw = _fixture(family)
    if fixture.get("protocol") != PROTOCOL:
        raise ValueError("Packaged comparison fixture has an unsupported protocol version")
    fixture_case_id = CASE_ALIASES.get(case_id, (case_id, None))[0]
    matches = [case for case in fixture["cases"] if case["id"] == fixture_case_id]
    if len(matches) != 1:
        raise ValueError(f"Case ID is not unique in its frozen reference fixture: {case_id}")
    case = json.loads(json.dumps(matches[0]))
    if case_id in CASE_ALIASES:
        point_index = CASE_ALIASES[case_id][1]
        case["id"] = case_id
        case["coordinates_m"] = [case["coordinates_m"][point_index]]
    return family, case, digest(raw)


def _qvalue(record: dict, key: str):
    return record[key]["value"]


def _scenario_wave(scenario: dict, element: dict) -> dict:
    medium = scenario["medium"]
    sources = scenario["sources"]
    return {
        "density_kg_m3": _qvalue(medium, "density"),
        "sound_speed_m_s": _qvalue(medium, "sound_speed"),
        "frequency_hz": _qvalue(sources, "frequency"),
        "peak_pressure_pa": _qvalue(element, "pressure_amplitude"),
        "direction": _qvalue(element, "normal"),
        "reference_m": _qvalue(element, "position"),
        "phase_rad": _qvalue(element, "phase"),
        "dynamic_viscosity_pa_s": _qvalue(medium, "dynamic_viscosity"),
        "amplitude_attenuation_per_m": _qvalue(medium, "amplitude_attenuation"),
    }


def _validate_case_inputs(family: str, case: dict, scenario: dict, request: dict) -> None:
    if request != {
        "contract": "FIELD-REQUEST-1.0",
        "case_id": case["id"],
        "box_min_m": case["box_min_m"],
        "box_max_m": case["box_max_m"],
        "coordinates_m": case["coordinates_m"],
    }:
        raise ValueError(f"Stored request differs from the frozen {case['id']} case")
    sources = scenario["sources"]
    if sources["amplitude_convention"] != "peak" or sources["phasor_convention"] != "exp(-iwt)":
        raise ValueError("Stored source convention differs from the frozen field protocol")
    if any(_qvalue(scenario["medium"], key) != 0 for key in (
        "dynamic_viscosity", "amplitude_attenuation"
    )):
        raise ValueError("The frozen plane-wave comparisons require explicit zero loss")
    reference_sources = [case["wave"]] if family == "B03" else (
        [case["forward"], case["backward"]] if family == "B04" else
        [case["first"], case["second"]]
    )
    elements = sources["elements"]
    if len(elements) != len(reference_sources):
        raise ValueError(f"Stored source count differs from frozen case {case['id']}")
    for element, reference in zip(elements, reference_sources, strict=True):
        if element["model"] != "ideal_plane_wave" or _scenario_wave(scenario, element) != reference:
            raise ValueError(f"Stored source inputs differ from frozen case {case['id']}")


def _as_complex(value) -> complex:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return complex(float(value[0]), float(value[1]))
    return complex(float(value), 0.0)


def _error(actual, expected, scale: float) -> float:
    return abs(actual - expected) / scale


def analyze_recorded_case(run_folder, *, expected_manifest_sha256: str | None = None) -> dict:
    """Check bundle integrity, exact frozen inputs, then compare every field component."""
    folder = Path(run_folder)
    checked = check_run(folder, expected_sha256=expected_manifest_sha256)
    if checked["integrity"] != "VERIFIED" or checked["execution_status"] != "completed":
        raise ValueError("Only completed, integrity-verified field bundles can be compared")
    scenario = decode((folder / "scenario.json").read_bytes())
    request = decode((folder / "field-request.json").read_bytes())
    family, case, fixture_sha256 = frozen_case(request["case_id"])
    _validate_case_inputs(family, case, scenario, request)
    fixture, _ = _fixture(family)
    if fixture.get("normalized_tolerance") != TOLERANCE:
        raise ValueError("Packaged fixture tolerance differs from ANA-REF-1.0")

    expected = ORACLES[family](case)
    scales = {name: float(expected["scales"][key]) for name, key in (
        ("pressure", "pressure"),
        ("velocity", "velocity"),
        ("pressure_gradient", "pressure_gradient"),
        ("mean_intensity", "intensity"),
    )}
    actual = {
        name: decode((folder / filename).read_bytes())["values"]
        for name, filename in (
            ("pressure", "field-pressure.json"),
            ("velocity", "field-velocity.json"),
            ("pressure_gradient", "field-pressure-gradient.json"),
        )
    }
    errors = {name: [] for name in ("pressure", "velocity", "pressure_gradient", "mean_intensity")}
    failed = []
    intensity_observed = []
    for point_index, (p, velocity_row) in enumerate(zip(
        actual["pressure"], actual["velocity"], strict=True
    )):
        for quantity in ("pressure", "velocity", "pressure_gradient"):
            reference_value = expected["pressure" if quantity == "pressure" else quantity][point_index]
            values = [reference_value] if quantity == "pressure" else reference_value
            observed = [actual[quantity][point_index]] if quantity == "pressure" else actual[quantity][point_index]
            for component, (value, target) in enumerate(zip(observed, values, strict=True)):
                component_error = _error(
                    _as_complex(value), _as_complex(target), scales[quantity]
                )
                errors[quantity].append(component_error)
                if component_error > TOLERANCE:
                    failed.append({"quantity": quantity, "sample": point_index,
                                   "component": component, "normalized_error": component_error})
        flux_at_point = []
        for axis, velocity_component in enumerate(velocity_row):
            p_phasor = _as_complex(p)
            v_phasor = _as_complex(velocity_component)
            flux_value = 0.5 * (p_phasor * v_phasor.conjugate()).real
            flux_at_point.append(flux_value)
            component_error = abs(
                flux_value - float(expected["intensity"][point_index][axis])
            ) / scales["mean_intensity"]
            errors["mean_intensity"].append(component_error)
            if component_error > TOLERANCE:
                failed.append({"quantity": "mean_intensity", "sample": point_index,
                               "component": axis, "normalized_error": component_error})
        intensity_observed.append(flux_at_point)

    metrics = {
        name: {
            "E_max": max(values),
            "E_rms": math.sqrt(sum(value * value for value in values) / len(values)),
            "components_compared": len(values),
            "criterion": "PASS" if max(values) <= TOLERANCE else "FAIL",
        }
        for name, values in errors.items()
    }
    output_refs = {
        ref["uri"]: ref["sha256"]
        for ref in decode((folder / "manifest.json").read_bytes())["outputs"]
    }
    source_checksums = {
        "metrics": digest(Path(__file__).read_bytes()),
        "independent_references": digest(Path(references.__file__).read_bytes()),
        "frozen_case_fixture": fixture_sha256,
    }
    return {
        "contract": "ANA-07-METRICS-1.0",
        "protocol": PROTOCOL,
        "case_id": case["id"],
        "family": family,
        "sample_count": len(case["coordinates_m"]),
        "run_id": checked["run_id"],
        "manifest_sha256": checked["manifest_sha256"],
        "output_sha256": output_refs,
        "integrity": "VERIFIED",
        "numerical_comparison": "PASS" if not failed else "FAIL",
        "tolerance_normalized": TOLERANCE,
        "epsilon_binary64": EPSILON,
        "reference_precision_decimal_digits": 60,
        "reference_method": "Independent Decimal trigonometric and Euler references; exact period-mean flux identities.",
        "reference_sources": source_checksums,
        "scales_si": scales,
        "metrics": metrics,
        "failed_components": failed,
        "mean_intensity_w_m2": intensity_observed,
        "physical_validation": "NOT_ESTABLISHED",
        "limitations": [
            "Manufactured ideal plane-wave fields in the exact homogeneous, lossless regimes of ANA-REF-1.0.",
            "No measured water, physical source, body coupling, force, motion, or microgravity result.",
        ],
    }


def analyze_b03_01(run_folder, *, expected_manifest_sha256: str | None = None) -> dict:
    """Compatibility entry point for the original B03-01 smoke report."""
    report = analyze_recorded_case(run_folder, expected_manifest_sha256=expected_manifest_sha256)
    if report["case_id"] != "B03-01":
        raise ValueError("Expected the B03-01 origin sample")
    return report


def write_report(run_folder, report_path, *, expected_manifest_sha256: str | None = None) -> dict:
    report = analyze_recorded_case(run_folder, expected_manifest_sha256=expected_manifest_sha256)
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    path.write_bytes(raw)
    Path(str(path) + ".sha256").write_text(digest(raw) + "\n", encoding="ascii")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compare a run with its frozen ANA-REF-1.0 case")
    parser.add_argument("run_folder", help="Completed analytical run bundle")
    parser.add_argument("report_path", help="Output JSON report path")
    parser.add_argument("--manifest-sha256", help="Expected manifest digest anchor")
    args = parser.parse_args(argv)
    report = write_report(
        args.run_folder, args.report_path, expected_manifest_sha256=args.manifest_sha256
    )
    print(json.dumps({
        "case_id": report["case_id"],
        "run_id": report["run_id"],
        "integrity": report["integrity"],
        "numerical_comparison": report["numerical_comparison"],
        "physical_validation": report["physical_validation"],
        "report_path": str(Path(args.report_path)),
    }, sort_keys=True))
    return 0 if report["numerical_comparison"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
