"""Frozen B03-01 comparison for one recorded ideal plane-wave sample.

This module is deliberately separate from the production field kernels. Its first
scope is only the B03-01 origin sample in ANA-REF-1.0; it is not a general solver
validator or an experimental/physical validation tool.
"""

from __future__ import annotations

import argparse
import json
import math
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from pathlib import Path

from aura.runs import check_run
from aura.runs.manifest import decode, digest

PROTOCOL = "ANA-REF-1.0"
CASE_ID = "B03-01"
EPSILON = 2.0**-52
TOLERANCE = 2048 * EPSILON


def _pi(digits: int = 60) -> Decimal:
    """Machin pi with Decimal arithmetic, independent of production trig helpers."""
    with localcontext() as context:
        context.prec = digits + 12

        def atan_inverse(denominator: int) -> Decimal:
            x = Decimal(1) / denominator
            power = total = x
            for index in range(1, 256):
                power = -power * x * x
                term = power / (2 * index + 1)
                total += term
                if abs(term) < Decimal(10) ** (-(digits + 8)):
                    return total
            raise ArithmeticError("Independent pi reference exceeded its iteration cap")

        context.rounding = ROUND_HALF_EVEN
        return 16 * atan_inverse(5) - 4 * atan_inverse(239)


def _read_json(folder: Path, name: str) -> dict:
    return decode((folder / name).read_bytes())


def _quantity_value(record: dict, key: str):
    return record[key]["value"]


def _require_b03_01(scenario: dict, request: dict) -> None:
    if request != {
        "contract": "FIELD-REQUEST-1.0",
        "case_id": CASE_ID,
        "box_min_m": [-0.0015, -0.0015, -0.0015],
        "box_max_m": [0.0015, 0.0015, 0.0015],
        "coordinates_m": [[0, 0, 0]],
    }:
        raise ValueError("This reference is frozen only for the B03-01 origin sample")
    medium = scenario["medium"]
    sources = scenario["sources"]
    elements = sources["elements"]
    if len(elements) != 1:
        raise ValueError("B03-01 requires exactly one ideal plane source")
    wave = elements[0]
    exact = (
        _quantity_value(medium, "density") == 1000
        and _quantity_value(medium, "sound_speed") == 1500
        and _quantity_value(medium, "dynamic_viscosity") == 0
        and _quantity_value(medium, "amplitude_attenuation") == 0
        and _quantity_value(sources, "frequency") == 1_000_000
        and _quantity_value(wave, "pressure_amplitude") == 2
        and _quantity_value(wave, "normal") == [1, 0, 0]
        and _quantity_value(wave, "position") == [0, 0, 0]
        and _quantity_value(wave, "phase") == 0
        and wave["model"] == "ideal_plane_wave"
        and sources["amplitude_convention"] == "peak"
        and sources["phasor_convention"] == "exp(-iwt)"
    )
    if not exact:
        raise ValueError("Stored Scenario does not match the frozen B03-01 reference inputs")


def _complex_error(actual: list[float], expected: complex, scale: float) -> float:
    return abs(complex(actual[0], actual[1]) - expected) / scale


def analyze_b03_01(run_folder, *, expected_manifest_sha256: str | None = None) -> dict:
    """Verify bundle integrity, then compare B03-01 fields with the frozen oracle."""
    folder = Path(run_folder)
    checked = check_run(folder, expected_sha256=expected_manifest_sha256)
    if checked["integrity"] != "VERIFIED" or checked["execution_status"] != "completed":
        raise ValueError("Only a completed, integrity-verified analytical bundle can be compared")
    scenario, request = _read_json(folder, "scenario.json"), _read_json(folder, "field-request.json")
    _require_b03_01(scenario, request)

    rho = Decimal(str(_quantity_value(scenario["medium"], "density")))
    speed = Decimal(str(_quantity_value(scenario["medium"], "sound_speed")))
    frequency = Decimal(str(_quantity_value(scenario["sources"], "frequency")))
    amplitude = Decimal(str(_quantity_value(scenario["sources"]["elements"][0], "pressure_amplitude")))
    with localcontext() as context:
        context.prec = 70
        omega = 2 * _pi() * frequency
        wave_number = omega / speed
        impedance = rho * speed
        velocity_scale = amplitude / impedance
        gradient_scale = wave_number * amplitude
        intensity_scale = amplitude**2 / (2 * impedance)
        expected_velocity = float(velocity_scale)
        expected_gradient = float(gradient_scale)
        expected_intensity = float(intensity_scale)

    pressure = _read_json(folder, "field-pressure.json")["values"]
    velocity = _read_json(folder, "field-velocity.json")["values"]
    gradient = _read_json(folder, "field-pressure-gradient.json")["values"]
    expected_scales = {
        "pressure_pa": float(amplitude),
        "velocity_m_s": expected_velocity,
        "pressure_gradient_pa_m": expected_gradient,
        "intensity_w_m2": expected_intensity,
    }
    pressure_errors = [_complex_error(row, complex(float(amplitude), 0), expected_scales["pressure_pa"])
                       for row in pressure]
    velocity_errors, gradient_errors, intensity_errors = [], [], []
    flux = []
    for p, velocity_row, gradient_row in zip(pressure, velocity, gradient, strict=True):
        for axis in range(3):
            expected_v = complex(expected_velocity, 0) if axis == 0 else 0j
            expected_g = complex(0, expected_gradient) if axis == 0 else 0j
            velocity_errors.append(_complex_error(velocity_row[axis], expected_v, expected_scales["velocity_m_s"]))
            gradient_errors.append(_complex_error(gradient_row[axis], expected_g, expected_scales["pressure_gradient_pa_m"]))
            p_phasor = complex(*p)
            v_phasor = complex(*velocity_row[axis])
            component_flux = 0.5 * (p_phasor * v_phasor.conjugate()).real
            flux.append(component_flux)
            expected_flux = expected_intensity if axis == 0 else 0.0
            intensity_errors.append(abs(component_flux - expected_flux) / expected_scales["intensity_w_m2"])

    groups = {
        "pressure": pressure_errors,
        "velocity": velocity_errors,
        "pressure_gradient": gradient_errors,
        "mean_intensity": intensity_errors,
    }
    summaries = {
        name: {
            "E_max": max(values),
            "E_rms": math.sqrt(sum(value * value for value in values) / len(values)),
            "components_compared": len(values),
            "criterion": "PASS" if max(values) <= TOLERANCE else "FAIL",
        }
        for name, values in groups.items()
    }
    outputs = {ref["uri"]: ref["sha256"] for ref in _read_json(folder, "manifest.json")["outputs"]}
    all_errors = [value for values in groups.values() for value in values]
    return {
        "contract": "ANA-07-METRICS-1.0",
        "protocol": PROTOCOL,
        "case_id": CASE_ID,
        "run_id": checked["run_id"],
        "manifest_sha256": checked["manifest_sha256"],
        "analysis_source_sha256": digest(Path(__file__).read_bytes()),
        "output_sha256": outputs,
        "integrity": "VERIFIED",
        "numerical_comparison": "PASS" if max(all_errors) <= TOLERANCE else "FAIL",
        "tolerance_normalized": TOLERANCE,
        "epsilon_binary64": EPSILON,
        "reference_method": "Machin pi in Decimal arithmetic; exact B03-01 origin phasors and plane-wave flux from ANA-REF-1.0",
        "reference_precision_decimal_digits": 70,
        "scales_si": expected_scales,
        "metrics": summaries,
        "mean_intensity_w_m2": [flux[axis] for axis in range(3)],
        "physical_validation": "NOT_ESTABLISHED",
        "limitations": [
            "One manufactured plane-wave sample in a declared homogeneous, lossless model.",
            "No measured water, physical source, body coupling, force, motion, or microgravity result.",
        ],
    }


def write_report(run_folder, report_path, *, expected_manifest_sha256: str | None = None) -> dict:
    report = analyze_b03_01(run_folder, expected_manifest_sha256=expected_manifest_sha256)
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    path.write_bytes(raw)
    Path(str(path) + ".sha256").write_text(digest(raw) + "\n", encoding="ascii")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compare the frozen ANA-REF-1.0 B03-01 sample")
    parser.add_argument("run_folder", help="Completed analytical run bundle")
    parser.add_argument("report_path", help="Output JSON report path")
    parser.add_argument("--manifest-sha256", help="Expected manifest digest anchor")
    args = parser.parse_args(argv)
    report = write_report(
        args.run_folder, args.report_path, expected_manifest_sha256=args.manifest_sha256
    )
    print(json.dumps({
        "run_id": report["run_id"],
        "integrity": report["integrity"],
        "numerical_comparison": report["numerical_comparison"],
        "physical_validation": report["physical_validation"],
        "report_path": str(Path(args.report_path)),
    }, sort_keys=True))
    return 0 if report["numerical_comparison"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
