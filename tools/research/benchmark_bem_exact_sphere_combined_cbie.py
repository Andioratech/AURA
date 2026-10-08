"""Evaluate one matrix-free direct-plus-image CBIE action on an exact sphere."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

from aura.fields._bem_axisymmetric import (
    _integrate_helmholtz_ring_green_and_gradient_zero_mode,
)
from aura.fields._bem_green import neumann_half_space_green
from aura.fields._bem_singular import integrate_logarithmic_panel
from aura.fields.numerical import gauss_legendre_rule

ROOT = Path(__file__).resolve().parents[2]
LOCK_FILES = (
    Path("requirements/environment-linux-py312.json"),
    Path("requirements/core-linux-py312.lock"),
    Path("requirements/dev-linux-py312.lock"),
)
SPHERE_RADIUS_M = 0.025
PLANE_GAP_M = 0.0001
FREQUENCY_HZ = 25_230.0
SOUND_SPEED_M_S = 346.0
WAVE_NUMBER_RAD_M = 2.0 * math.pi * FREQUENCY_HZ / SOUND_SPEED_M_S
COLLOCATION_ANGLES_DEGREES = (120.0, 135.0, 175.0, 179.0)
MERIDIAN_ORDERS = (64, 128, 256)
DIRECT_AZIMUTH_SAMPLES = 512
IMAGE_AZIMUTH_SAMPLES = 1_024
REPEATS = 2
WALL_TIME_CAP_SECONDS = 120.0


def _git(*args: str) -> str:
    return subprocess.run(("git", *args), cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def require_clean_source() -> str:
    if _git("status", "--porcelain", "--untracked-files=normal"):
        raise RuntimeError("The benchmark requires a clean source worktree.")
    return _git("rev-parse", "HEAD")


def environment_identity() -> dict:
    files = {}
    aggregate = hashlib.sha256()
    for relative in LOCK_FILES:
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        files[relative.as_posix()] = digest
        aggregate.update(relative.as_posix().encode("utf-8") + b"\0")
        aggregate.update(bytes.fromhex(digest))
    return {"aggregate_sha256": aggregate.hexdigest(), "files": files}


def output_path(value: str) -> Path:
    destination = (ROOT / value).resolve()
    if not destination.is_relative_to(ROOT / "results" / "diagnostics"):
        raise ValueError("Output must be stored under results/diagnostics/.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing result: {destination}")
    return destination


def _encode(value: complex) -> str:
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ArithmeticError("CBIE action returned a non-finite complex value.")
    return f"{value.real.hex()}:{value.imag.hex()}"


def _sum_complex(values: list[complex]) -> complex:
    return complex(math.fsum(value.real for value in values), math.fsum(value.imag for value in values))


def _point(theta: float) -> tuple[float, float, float]:
    center_height = SPHERE_RADIUS_M + PLANE_GAP_M
    return (
        SPHERE_RADIUS_M * math.sin(theta),
        0.0,
        center_height + SPHERE_RADIUS_M * math.cos(theta),
    )


def _trace(theta: float) -> tuple[complex, complex]:
    point = _point(theta)
    normal_rz = (-math.sin(theta), -math.cos(theta))
    pressure, gradient, _ = neumann_half_space_green(
        point,
        (0.0, 0.0, SPHERE_RADIUS_M + PLANE_GAP_M),
        wave_number_rad_m=WAVE_NUMBER_RAD_M,
    )
    normal_derivative = normal_rz[0] * gradient[0] + normal_rz[1] * gradient[2]
    return pressure, normal_derivative


def _image_ring(field: tuple[float, float, float], theta: float, *, samples: int) -> tuple[complex, complex]:
    """Return image ring Green and physical source-normal derivative integrals."""
    source_radius = SPHERE_RADIUS_M * math.sin(theta)
    source_height = PLANE_GAP_M + SPHERE_RADIUS_M * (1.0 + math.cos(theta))
    normal_rz = (-math.sin(theta), -math.cos(theta))
    # Translate the image source upward to z=0. The derivative with respect
    # to the physical source retains the reflected-coordinate chain-rule sign.
    translated_field_height = field[2] + source_height
    green, _, image_source_gradient = _integrate_helmholtz_ring_green_and_gradient_zero_mode(
        field[0], translated_field_height, source_radius, 0.0,
        wave_number_rad_m=WAVE_NUMBER_RAD_M, azimuth_samples=samples,
    )
    source_normal_derivative = (
        normal_rz[0] * image_source_gradient[0]
        - normal_rz[1] * image_source_gradient[1]
    )
    return green, source_normal_derivative


def evaluate_action(theta_degrees: float, meridian_order: int, *,
                    direct_azimuth_samples: int = DIRECT_AZIMUTH_SAMPLES,
                    image_azimuth_samples: int = IMAGE_AZIMUTH_SAMPLES,
                    meridian_order_levels: tuple[int, ...] = MERIDIAN_ORDERS,
                    meridian_split_factor: float = 8.0,
                    meridian_subdivisions: int = 1) -> dict:
    """Return the CBIE jump, layer terms and residual at one sphere point."""
    if theta_degrees not in COLLOCATION_ANGLES_DEGREES:
        raise ValueError("Collocation angle is not in the frozen benchmark set.")
    if type(meridian_order) is not int or meridian_order not in meridian_order_levels:
        raise ValueError("Meridian order is not in the frozen benchmark set.")
    if type(direct_azimuth_samples) is not int or direct_azimuth_samples < 4:
        raise ValueError("Direct azimuth sample count must be an integer >=4.")
    if type(image_azimuth_samples) is not int or image_azimuth_samples < 4:
        raise ValueError("Image azimuth sample count must be an integer >=4.")
    if (type(meridian_split_factor) not in (int, float) or type(meridian_split_factor) is bool
            or not math.isfinite(meridian_split_factor) or meridian_split_factor <= 0):
        raise ValueError("Meridian split factor must be finite and positive.")
    if type(meridian_subdivisions) is not int or meridian_subdivisions < 1:
        raise ValueError("Meridian subdivisions must be a positive integer.")

    theta_field = math.radians(theta_degrees)
    field = _point(theta_field)
    field_pressure, _ = _trace(theta_field)
    field_radius = field[0]
    log_scale = 8.0 * field_radius
    singular_arclength = SPHERE_RADIUS_M * theta_field

    # This fixed geometric split follows the existing 175-degree CBIE
    # regression. It is a quadrature partition, not a universal error bound.
    cutoff = meridian_split_factor * field[2] / field_radius
    edges = (
        0.0,
        max(0.0, theta_field - cutoff),
        min(math.pi, theta_field + cutoff),
        math.pi,
    )
    nodes, weights = gauss_legendre_rule(meridian_order)
    direct_double_remainder: list[complex] = []
    direct_single_remainder: list[complex] = []
    image_double_terms: list[complex] = []
    image_single_terms: list[complex] = []

    active_panels = tuple(
        (lower, upper)
        for lower, upper in pairwise(edges)
        if upper > lower
    )
    for lower, upper in active_panels:
        for subdivision in range(meridian_subdivisions):
            sub_lower = (
                lower if subdivision == 0
                else lower + (upper - lower) * subdivision / meridian_subdivisions
            )
            sub_upper = (
                upper if subdivision + 1 == meridian_subdivisions
                else lower + (upper - lower) * (subdivision + 1) / meridian_subdivisions
            )
            midpoint = 0.5 * (sub_lower + sub_upper)
            half_width = 0.5 * (sub_upper - sub_lower)
            for node, weight in zip(nodes, weights, strict=True):
                theta = midpoint + half_width * node
                source = _point(theta)
                source_radius, source_height = source[0], source[2]
                source_normal = (-math.sin(theta), -math.cos(theta))
                pressure, normal_derivative = _trace(theta)
                direct_green, _, direct_source_gradient = _integrate_helmholtz_ring_green_and_gradient_zero_mode(
                    field_radius, field[2], source_radius, source_height,
                    wave_number_rad_m=WAVE_NUMBER_RAD_M,
                    azimuth_samples=direct_azimuth_samples,
                )
                direct_source_normal = (
                    source_normal[0] * direct_source_gradient[0]
                    + source_normal[1] * direct_source_gradient[1]
                )
                image_green, image_source_normal = _image_ring(
                    field, theta, samples=image_azimuth_samples
                )

                quadrature_weight = half_width * weight
                surface_weight = quadrature_weight * SPHERE_RADIUS_M * source_radius
                logarithm = math.log(
                    log_scale / abs(SPHERE_RADIUS_M * theta - singular_arclength)
                )
                direct_double_remainder.append(
                    surface_weight * pressure * direct_source_normal
                    - quadrature_weight * pressure * logarithm / (4.0 * math.pi)
                )
                direct_single_remainder.append(
                    surface_weight * normal_derivative * direct_green
                    - quadrature_weight * SPHERE_RADIUS_M * normal_derivative
                    * logarithm / (2.0 * math.pi)
                )
                image_double_terms.append(surface_weight * pressure * image_source_normal)
                image_single_terms.append(surface_weight * normal_derivative * image_green)

    direct_double_log = integrate_logarithmic_panel(
        lambda arclength: _trace(arclength / SPHERE_RADIUS_M)[0]
        / (4.0 * math.pi * SPHERE_RADIUS_M),
        0.0,
        math.pi * SPHERE_RADIUS_M,
        singular_arclength,
        log_scale=log_scale,
        order=meridian_order,
    )
    direct_single_log = integrate_logarithmic_panel(
        lambda arclength: _trace(arclength / SPHERE_RADIUS_M)[1] / (2.0 * math.pi),
        0.0,
        math.pi * SPHERE_RADIUS_M,
        singular_arclength,
        log_scale=log_scale,
        order=meridian_order,
    )
    direct_double = _sum_complex(direct_double_remainder) + direct_double_log
    direct_single = _sum_complex(direct_single_remainder) + direct_single_log
    image_double = _sum_complex(image_double_terms)
    image_single = _sum_complex(image_single_terms)
    jump = 0.5 * field_pressure
    residual = jump + direct_double + image_double - direct_single - image_single
    return {
        "jump_half_pressure": _encode(jump),
        "direct_double_layer": _encode(direct_double),
        "image_double_layer": _encode(image_double),
        "direct_single_layer": _encode(direct_single),
        "image_single_layer": _encode(image_single),
        "cbie_residual": _encode(residual),
        "boundary_pressure": _encode(field_pressure),
        "normalized_residual_by_boundary_pressure": abs(residual) / abs(field_pressure),
        "active_meridian_subintervals": len(active_panels),
        "meridian_subdivisions_per_active_interval": meridian_subdivisions,
        "evaluated_meridian_panels": len(active_panels) * meridian_subdivisions,
    }


def _measure(theta: float, order: int) -> dict:
    values, timings = [], []
    for _ in range(REPEATS):
        started = time.perf_counter()
        value = evaluate_action(theta, order)
        elapsed = time.perf_counter() - started
        if elapsed > WALL_TIME_CAP_SECONDS:
            raise TimeoutError(f"Case theta={theta}, order={order} exceeded {WALL_TIME_CAP_SECONDS}s.")
        values.append(value)
        timings.append(elapsed)
    encoded = [json.dumps(value, sort_keys=True, allow_nan=False) for value in values]
    if len(set(encoded)) != 1:
        raise RuntimeError(f"Repeated action values differ for theta={theta}, order={order}.")
    return {
        "collocation_theta_degrees": theta,
        "meridian_order_per_panel": order,
        "active_meridian_subintervals": values[-1]["active_meridian_subintervals"],
        "direct_azimuth_samples": DIRECT_AZIMUTH_SAMPLES,
        "image_azimuth_samples": IMAGE_AZIMUTH_SAMPLES,
        **values[-1],
        "repeat_checksum_sha256": hashlib.sha256("\n".join(encoded).encode()).hexdigest(),
        "repeat_wall_times_s": timings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="new JSON path under results/diagnostics/")
    args = parser.parse_args(argv)
    destination = output_path(args.output)
    record = {
        "contract": "BEM-EXACT-SPHERE-COMBINED-CBIE-ACTION-1.0",
        "status": "RUNNING",
        "created_utc": datetime.now(UTC).isoformat(),
        "source_revision": None,
        "source_clean": False,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment_lock": environment_identity(),
        "environment_verification": None,
        "runtime": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                    "platform": platform.platform(), "cpu_count": os.cpu_count(),
                    "peak_rss_platform_units": None},
        "configuration": {
            "sphere_radius_m": SPHERE_RADIUS_M,
            "plane_gap_m": PLANE_GAP_M,
            "frequency_hz": FREQUENCY_HZ,
            "sound_speed_m_s": SOUND_SPEED_M_S,
            "wave_number_rad_m": WAVE_NUMBER_RAD_M,
            "boundary_source": "centered monopole with rigid-plane Neumann image",
            "normal_convention": "AURA normal into the sphere",
            "collocation_angles_degrees": COLLOCATION_ANGLES_DEGREES,
            "meridian_orders": MERIDIAN_ORDERS,
            "meridian_panels": 3,
            "direct_azimuth_samples": DIRECT_AZIMUTH_SAMPLES,
            "image_azimuth_samples": IMAGE_AZIMUTH_SAMPLES,
            "repeats": REPEATS,
            "wall_time_cap_seconds_per_case": WALL_TIME_CAP_SECONDS,
        },
        "analytic_reference": "0 = 0.5*p(x) + K_direct[p] + K_image[p] - V_direct[q] - V_image[q]",
        "scope": ("One streamed boundary-operator action for the exact sphere and stated centered-monopole trace. "
                  "The direct logarithmic singularities are subtracted and restored by panel product integration; "
                  "the image terms are smooth and accumulated separately. This verifies one idealized CBIE identity, "
                  "not a full operator, matrix, solver, field acceptance, force, acceleration, physical validation, "
                  "or gravity equivalence."),
        "cases": [],
        "matrix_allocated": False,
        "solver_started": False,
        "preflight": {"status": "INDETERMINATE", "execution_authorized": False},
    }
    try:
        record["source_revision"] = require_clean_source()
        record["source_clean"] = True
        verified = subprocess.run(
            (sys.executable, str(ROOT / "scripts/verify_environment.py")),
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        record["environment_verification"] = json.loads(verified.stdout)
        for theta in COLLOCATION_ANGLES_DEGREES:
            for order in MERIDIAN_ORDERS:
                record["cases"].append(_measure(theta, order))
        record["runtime"]["peak_rss_platform_units"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        record["status"] = "COMPLETED"
    except Exception as exc:  # noqa: BLE001 - Preserve every failed action as an artifact.
        record["status"] = "FAILED"
        record["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    destination.write_bytes(payload)
    print(json.dumps({"status": record["status"], "output": destination.as_posix(),
                      "sha256": hashlib.sha256(payload).hexdigest(), "cases": len(record["cases"]),
                      "source_revision": record["source_revision"]}, sort_keys=True))
    return 0 if record["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
