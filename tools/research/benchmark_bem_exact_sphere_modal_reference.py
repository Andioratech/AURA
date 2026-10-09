"""Bounded modal reference for the frozen exact-sphere CBIE case.

This research-only calculation deliberately does not import or call BEM ring
quadrature. Its three cutoffs reuse the existing outward-rounded image-layer
tail certificate documented in the NUM-03 modal reference plan. That certificate
does not cover the direct-layer sums or binary64 evaluation error.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path

from aura.fields.numerical import _spherical_sequences

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "NUM03-EXACT-SPHERE-MODAL-REFERENCE-1.0"
SPHERE_RADIUS_M = 0.025
PLANE_GAP_M = 0.0001
FREQUENCY_HZ = 25_230.0
SOUND_SPEED_M_S = 346.0
WAVE_NUMBER_RAD_M = 2.0 * math.pi * FREQUENCY_HZ / SOUND_SPEED_M_S
CENTER_DISTANCE_M = SPHERE_RADIUS_M + PLANE_GAP_M
IMAGE_CENTER_DISTANCE_M = 2.0 * CENTER_DISTANCE_M
CUTOFFS = (48, 64, 80)
ANGLES_DEGREES = (120.0, 135.0, 175.0, 179.0)
WORKSPACE_ESTIMATE_BYTES = 1_048_576
WORKSPACE_CAP_BYTES = 8_388_608
TAIL_UPPER_PA = {
    48: "0.21272935815902531565016809912384618657363648816083184242212063935383269802469029",
    64: "0.0000042743177115560590651548847751467905071342067626553524839558858657755421211429605",
    80: "7.2077447199595597185217674229494542416715781328407104433288363705027387757198983E-11",
}


def _encode(value: complex) -> dict[str, str]:
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ArithmeticError("Modal calculation produced a non-finite complex value.")
    return {"real_hex": value.real.hex(), "imag_hex": value.imag.hex()}


def _sum_complex(terms: list[complex]) -> complex:
    return complex(math.fsum(value.real for value in terms), math.fsum(value.imag for value in terms))


def _legendre_values(cosine: float, maximum_order: int) -> tuple[float, ...]:
    values = [1.0]
    if maximum_order == 0:
        return tuple(values)
    values.append(cosine)
    for order in range(1, maximum_order):
        next_value = (
            (2 * order + 1) * cosine * values[-1] - order * values[-2]
        ) / (order + 1)
        if not math.isfinite(next_value):
            raise ArithmeticError("Legendre recurrence produced a non-finite value.")
        values.append(next_value)
    return tuple(values)


def _spherical_values(maximum_order: int, argument: float):
    """Build j, y and their derivatives once for one positive real argument."""
    return _spherical_sequences(maximum_order, argument)


def _parameters(theta_degrees: float) -> dict[str, float]:
    theta = math.radians(theta_degrees)
    radius = SPHERE_RADIUS_M
    image_distance = math.hypot(
        radius * math.sin(theta),
        IMAGE_CENTER_DISTANCE_M + radius * math.cos(theta),
    )
    image_cosine = (IMAGE_CENTER_DISTANCE_M + radius * math.cos(theta)) / image_distance
    return {
        "theta_rad": theta,
        "image_distance_m": image_distance,
        "image_cosine": image_cosine,
    }


def evaluate_modal(theta_degrees: float, cutoff: int) -> dict:
    """Evaluate four separate layers and the reconstructed CBIE at one angle."""
    if type(theta_degrees) not in (int, float) or not math.isfinite(theta_degrees):
        raise ValueError("Collocation angle must be a finite real number.")
    theta_degrees = float(theta_degrees)
    if theta_degrees not in ANGLES_DEGREES:
        raise ValueError("Angle is outside the four frozen collocation cases.")
    if type(cutoff) is not int or cutoff not in CUTOFFS:
        raise ValueError("Cutoff must be one of the reviewed nested orders 48, 64, or 80.")
    if WORKSPACE_ESTIMATE_BYTES > WORKSPACE_CAP_BYTES:
        raise MemoryError("The declared modal workspace exceeds its fixed cap.")

    radius = SPHERE_RADIUS_M
    wave_number = WAVE_NUMBER_RAD_M
    theta = math.radians(theta_degrees)
    parameters = _parameters(theta_degrees)
    image_distance = parameters["image_distance_m"]
    image_cosine = parameters["image_cosine"]
    order_count = cutoff + 1

    j_a, y_a, jp_a, yp_a = _spherical_values(cutoff + 1, wave_number * radius)
    j_l, y_l, _, _ = _spherical_values(cutoff + 1, wave_number * IMAGE_CENTER_DISTANCE_M)
    j_r, y_r, _, _ = _spherical_values(cutoff + 1, wave_number * image_distance)
    direct_legendre = _legendre_values(math.cos(theta), cutoff)
    image_legendre = _legendre_values(image_cosine, cutoff)
    h_a = tuple(complex(j_a[n], y_a[n]) for n in range(order_count + 1))
    hp_a = tuple(complex(jp_a[n], yp_a[n]) for n in range(order_count + 1))
    h_l = tuple(complex(j_l[n], y_l[n]) for n in range(order_count + 1))
    h_r = tuple(complex(j_r[n], y_r[n]) for n in range(order_count + 1))

    layers: dict[str, list[complex]] = {
        "direct_double_layer": [],
        "direct_single_layer": [],
        "image_double_layer": [],
        "image_single_layer": [],
    }
    pressure_trace_terms: list[complex] = []
    derivative_trace_terms: list[complex] = []
    modal_rows = []
    direct_h0 = h_a[0]
    direct_hp0 = hp_a[0]
    for order in range(order_count):
        parity = -1.0 if order % 2 else 1.0
        factor = 1j * wave_number * (2 * order + 1) / (4.0 * math.pi)
        pressure_mode = (
            1j * wave_number * direct_h0 / (4.0 * math.pi) if order == 0 else 0j
        ) + factor * parity * h_l[order] * j_a[order]
        inward_derivative_mode = (
            -1j * wave_number**2 * direct_hp0 / (4.0 * math.pi) if order == 0 else 0j
        ) - wave_number * factor * parity * h_l[order] * jp_a[order]
        pressure_trace_terms.append(pressure_mode * direct_legendre[order])
        derivative_trace_terms.append(inward_derivative_mode * direct_legendre[order])

        single_eigenvalue = 1j * wave_number * radius**2 * j_a[order] * h_a[order]
        double_inward_eigenvalue = -0.5j * wave_number**2 * radius**2 * (
            jp_a[order] * h_a[order] + j_a[order] * hp_a[order]
        )
        direct_double = (
            double_inward_eigenvalue * pressure_mode * direct_legendre[order]
        )
        direct_single = (
            single_eigenvalue * inward_derivative_mode * direct_legendre[order]
        )
        image_double = (
            -1j
            * wave_number**2
            * radius**2
            * jp_a[order]
            * h_r[order]
            * image_legendre[order]
            * parity
            * pressure_mode
        )
        image_single = (
            1j
            * wave_number
            * radius**2
            * j_a[order]
            * h_r[order]
            * image_legendre[order]
            * parity
            * inward_derivative_mode
        )
        row = {
            "order": order,
            "pressure_mode": _encode(pressure_mode),
            "inward_derivative_mode": _encode(inward_derivative_mode),
        }
        for name, value in (
            ("direct_double_layer", direct_double),
            ("direct_single_layer", direct_single),
            ("image_double_layer", image_double),
            ("image_single_layer", image_single),
        ):
            layers[name].append(value)
            row[name] = _encode(value)
        modal_rows.append(row)

    layer_values = {name: _sum_complex(terms) for name, terms in layers.items()}
    exact_point = (
        cmath.exp(1j * wave_number * radius) / (4.0 * math.pi * radius)
        + cmath.exp(1j * wave_number * image_distance) / (4.0 * math.pi * image_distance)
    )
    image_radial_cosine = (
        radius + IMAGE_CENTER_DISTANCE_M * math.cos(theta)
    ) / image_distance
    exact_inward_derivative = -(
        (1j * wave_number - 1.0 / radius)
        * cmath.exp(1j * wave_number * radius)
        / (4.0 * math.pi * radius)
        + (1j * wave_number - 1.0 / image_distance)
        * cmath.exp(1j * wave_number * image_distance)
        / (4.0 * math.pi * image_distance)
        * image_radial_cosine
    )
    modal_pressure = _sum_complex(pressure_trace_terms)
    modal_inward_derivative = _sum_complex(derivative_trace_terms)
    jump = 0.5 * exact_point
    residual = (
        jump
        + layer_values["direct_double_layer"]
        + layer_values["image_double_layer"]
        - layer_values["direct_single_layer"]
        - layer_values["image_single_layer"]
    )
    cancellation = {}
    for name, terms in layers.items():
        total_magnitude = abs(layer_values[name])
        cancellation[name] = (
            math.fsum(abs(term) for term in terms) / total_magnitude
            if total_magnitude
            else None
        )

    return {
        "angle_degrees": theta_degrees,
        "cutoff_inclusive": cutoff,
        "image_distance_m": image_distance,
        "image_cosine": image_cosine,
        "boundary_pressure": _encode(exact_point),
        "modal_boundary_pressure": _encode(modal_pressure),
        "modal_inward_normal_derivative": _encode(modal_inward_derivative),
        "pressure_trace_absolute_difference_pa": abs(modal_pressure - exact_point),
        "normal_derivative_trace_absolute_difference_pa_m": abs(
            modal_inward_derivative - exact_inward_derivative
        ),
        "half_pressure_jump": _encode(jump),
        "layers": {name: _encode(value) for name, value in layer_values.items()},
        "layer_term_l1_cancellation_ratio": cancellation,
        "cbie_residual": _encode(residual),
        "cbie_residual_absolute_pa": abs(residual),
        "cbie_residual_normalized_by_pressure": abs(residual) / abs(exact_point),
        "image_layer_tail_upper_pa_each": TAIL_UPPER_PA[cutoff],
        "direct_layer_tail_status": "FINITE_CUTOFF_SENSITIVITY_ONLY; NO CERTIFIED BOUND",
        "modal_rows": modal_rows,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_clean_source() -> str:
    status = subprocess.run(
        ("git", "status", "--porcelain", "--untracked-files=normal"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if status:
        raise RuntimeError("The immutable modal record requires a clean Git worktree.")
    return subprocess.run(
        ("git", "rev-parse", "HEAD"), cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _output_path(value: str) -> Path:
    destination = (ROOT / value).resolve()
    diagnostics_root = (ROOT / "results" / "diagnostics").resolve()
    if not destination.is_relative_to(diagnostics_root):
        raise ValueError("Output must stay under results/diagnostics/.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite an existing record: {destination}")
    return destination


def run_protocol() -> dict:
    started = time.perf_counter()
    source_revision = _require_clean_source()
    cases = [
        evaluate_modal(angle, cutoff)
        for cutoff in CUTOFFS
        for angle in ANGLES_DEGREES
    ]
    value_payload = json.dumps(cases, sort_keys=True, separators=(",", ":")).encode("utf-8")
    lock_files = (
        "requirements/environment-linux-py312.json",
        "requirements/core-linux-py312.lock",
        "requirements/dev-linux-py312.lock",
    )
    lock_hashes = {name: _sha256(ROOT / name) for name in lock_files}
    lock_digest = hashlib.sha256()
    for name, digest in lock_hashes.items():
        lock_digest.update(name.encode("utf-8") + b"\0" + bytes.fromhex(digest))
    return {
        "contract": CONTRACT,
        "status": "EXPLORATORY_NUMERICAL_REFERENCE",
        "source_revision": source_revision,
        "script_sha256": _sha256(Path(__file__).resolve()),
        "numerical_module_sha256": _sha256(ROOT / "src/aura/fields/numerical.py"),
        "environment_lock": {
            "aggregate_sha256": lock_digest.hexdigest(),
            "files": lock_hashes,
        },
        "environment": {
            "python": sys.version,
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "configuration": {
            "sphere_radius_m": SPHERE_RADIUS_M,
            "plane_gap_m": PLANE_GAP_M,
            "frequency_hz": FREQUENCY_HZ,
            "sound_speed_m_s": SOUND_SPEED_M_S,
            "wave_number_rad_m": WAVE_NUMBER_RAD_M,
            "center_distance_m": CENTER_DISTANCE_M,
            "image_center_distance_m": IMAGE_CENTER_DISTANCE_M,
            "source_strength_pa_m": 1.0,
            "source_normal": "inward radial normal; plane reflection maps it to image inward normal",
            "phasor_green": "exp(-i omega t); exp(+i k R)/(4 pi R)",
            "cutoffs_inclusive": list(CUTOFFS),
            "angles_degrees": list(ANGLES_DEGREES),
            "summation": "separate math.fsum real and imaginary components in increasing order",
            "workspace_estimate_bytes": WORKSPACE_ESTIMATE_BYTES,
            "workspace_cap_bytes": WORKSPACE_CAP_BYTES,
        },
        "tail_certificate": {
            "scope": "uniform bound for image K and image V separately, frozen geometry and Q=1 Pa m",
            "method": "80-digit outward-rounded analytic absolute majorant through mode 2000 plus ratio envelope",
            "ratio_envelope_upper_n_ge_2000": "0.49431064387361592119814519443240782414870655661183164396561687357918174722014202",
            "direct_layer_scope": "not covered",
            "arithmetic_error_scope": "not covered",
        },
        "cases": cases,
        "cases_sha256": hashlib.sha256(value_payload).hexdigest(),
        "wall_time_seconds": time.perf_counter() - started,
        "scope": (
            "Manufactured exact-sphere trace cross-check only. It is not a half-space solver, "
            "field acceptance, physical validation, force calculation, or gravity result."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        required=True,
        help="new JSON output path below results/diagnostics/",
    )
    arguments = parser.parse_args()
    destination = _output_path(arguments.output)
    record = run_protocol()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    destination.write_text(payload, encoding="utf-8")
    print(json.dumps({"output": destination.relative_to(ROOT).as_posix(), "sha256": _sha256(destination),
                      "cases_sha256": record["cases_sha256"], "wall_time_seconds": record["wall_time_seconds"]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
