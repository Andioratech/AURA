"""Measure a matrix-free exact-sphere image action against its monopole identity."""

from __future__ import annotations

import argparse
import cmath
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
from pathlib import Path

from aura.fields._bem_axisymmetric import (
    integrate_helmholtz_ring_green_gradient_zero_mode,
    integrate_helmholtz_ring_green_zero_mode,
)
from aura.fields._bem_green import _free_space_term, neumann_half_space_green
from aura.fields._bem_mesh import sphere_meridian_quadrature

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
MERIDIAN_NODE_COUNTS = (16, 32, 64)
RING_AZIMUTH_COUNTS = (32, 64, 128)
DIRECT_REFERENCE_AZIMUTH_COUNT = 2_048
REPEATS = 2
WALL_TIME_CAP_SECONDS = 120.0


def _git(*args: str) -> str:
    return subprocess.run(("git", *args), cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def source_revision() -> str:
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
        raise ArithmeticError("Non-finite complex result.")
    return f"{value.real.hex()}:{value.imag.hex()}"


def _target(theta_degrees: float) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    theta = math.radians(theta_degrees)
    center_height = SPHERE_RADIUS_M + PLANE_GAP_M
    return (
        (SPHERE_RADIUS_M * math.sin(theta), 0.0, center_height + SPHERE_RADIUS_M * math.cos(theta)),
        (-math.sin(theta), 0.0, -math.cos(theta)),
    )


def _ring_action(field: tuple[float, float, float], field_normal: tuple[float, float, float],
                 theta: float, meridian_weight: float, *, azimuth_samples: int,
                 route: str) -> tuple[complex, complex]:
    """Return one meridian node's weighted image K and V contributions."""
    source_radius = SPHERE_RADIUS_M * math.sin(theta)
    source_height = PLANE_GAP_M + SPHERE_RADIUS_M * (1.0 + math.cos(theta))
    source = (source_radius, 0.0, source_height)
    source_normal_rz = (-math.sin(theta), -math.cos(theta))
    pressure, gradient, _ = neumann_half_space_green(
        source, (0.0, 0.0, SPHERE_RADIUS_M + PLANE_GAP_M),
        wave_number_rad_m=WAVE_NUMBER_RAD_M,
    )
    normal_derivative = source_normal_rz[0] * gradient[0] + source_normal_rz[1] * gradient[2]
    if route == "static_subtracted_ring":
        # Translate the image ring from z=-source_height to z=0. The
        # physical-source derivative retains the reflection chain-rule sign.
        translated_field_height = field[2] + source_height
        green = integrate_helmholtz_ring_green_zero_mode(
            field[0], translated_field_height, source_radius, 0.0,
            wave_number_rad_m=WAVE_NUMBER_RAD_M, azimuth_samples=azimuth_samples,
        )
        _, source_gradient = integrate_helmholtz_ring_green_gradient_zero_mode(
            field[0], translated_field_height, source_radius, 0.0,
            wave_number_rad_m=WAVE_NUMBER_RAD_M, azimuth_samples=azimuth_samples,
        )
        source_normal_derivative = (
            source_normal_rz[0] * source_gradient[0]
            - source_normal_rz[1] * source_gradient[1]
        )
    elif route == "pointwise_midpoint":
        green_terms = []
        derivative_terms = []
        step = 2.0 * math.pi / azimuth_samples
        for index in range(azimuth_samples):
            phi = (index + 0.5) * step
            cosine, sine = math.cos(phi), math.sin(phi)
            image_point = (source_radius * cosine, source_radius * sine, -source_height)
            image_normal = (source_normal_rz[0] * cosine,
                            source_normal_rz[0] * sine, -source_normal_rz[1])
            green_value, field_gradient = _free_space_term(field, image_point, WAVE_NUMBER_RAD_M)
            green_terms.append(green_value * step)
            derivative_terms.append(-sum(n * g for n, g in zip(image_normal, field_gradient, strict=True)) * step)
        green = complex(math.fsum(v.real for v in green_terms), math.fsum(v.imag for v in green_terms))
        source_normal_derivative = complex(
            math.fsum(v.real for v in derivative_terms), math.fsum(v.imag for v in derivative_terms)
        )
    else:
        raise ValueError(f"Unknown ring route: {route}")
    surface_factor = meridian_weight
    return pressure * source_normal_derivative * surface_factor, normal_derivative * green * surface_factor


def image_action(theta_degrees: float, node_count: int, *, azimuth_samples: int,
                 route: str) -> dict:
    field, field_normal = _target(theta_degrees)
    quadrature = sphere_meridian_quadrature(
        SPHERE_RADIUS_M, panels=node_count // 4, order_per_panel=4
    )
    double_terms, single_terms = [], []
    for theta, weight in quadrature:
        double, single = _ring_action(
            field, field_normal, theta, weight,
            azimuth_samples=azimuth_samples, route=route,
        )
        double_terms.append(double)
        single_terms.append(single)
    double_layer = complex(math.fsum(v.real for v in double_terms), math.fsum(v.imag for v in double_terms))
    single_layer = complex(math.fsum(v.real for v in single_terms), math.fsum(v.imag for v in single_terms))
    image_action_value = double_layer - single_layer
    image_source = (0.0, 0.0, -(SPHERE_RADIUS_M + PLANE_GAP_M))
    distance = math.dist(field, image_source)
    reference = -cmath.exp(1j * WAVE_NUMBER_RAD_M * distance) / (4.0 * math.pi * distance)
    return {
        "double_layer": _encode(double_layer),
        "single_layer": _encode(single_layer),
        "image_action": _encode(image_action_value),
        "analytic_reflected_monopole": _encode(reference),
        "absolute_complex_difference": abs(image_action_value - reference),
        "relative_complex_difference": abs(image_action_value - reference) / abs(reference),
    }


def _measure(theta_degrees: float, node_count: int, route: str, azimuth_samples: int) -> dict:
    values, timings = [], []
    for _ in range(REPEATS):
        started = time.perf_counter()
        result = image_action(theta_degrees, node_count, azimuth_samples=azimuth_samples, route=route)
        elapsed = time.perf_counter() - started
        if elapsed > WALL_TIME_CAP_SECONDS:
            raise TimeoutError(f"Case exceeded {WALL_TIME_CAP_SECONDS}s wall-time cap.")
        values.append(result)
        timings.append(elapsed)
    encodings = [json.dumps(item, sort_keys=True, allow_nan=False) for item in values]
    if len(set(encodings)) != 1:
        raise RuntimeError("Repeated action values differ for identical inputs.")
    return {
        "theta_degrees": theta_degrees,
        "meridian_nodes": node_count,
        "meridian_panels": node_count // 4,
        "meridian_order": 4,
        "ring_route": route,
        "azimuth_samples": azimuth_samples,
        **values[-1],
        "repeat_checksum_sha256": hashlib.sha256("\n".join(encodings).encode()).hexdigest(),
        "repeat_wall_times_s": timings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="new JSON path under results/diagnostics/")
    args = parser.parse_args(argv)
    destination = output_path(args.output)
    record = {
        "contract": "BEM-EXACT-SPHERE-IMAGE-ACTION-1.0",
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
        "configuration": {"sphere_radius_m": SPHERE_RADIUS_M, "plane_gap_m": PLANE_GAP_M,
                          "frequency_hz": FREQUENCY_HZ, "sound_speed_m_s": SOUND_SPEED_M_S,
                          "wave_number_rad_m": WAVE_NUMBER_RAD_M,
                          "collocation_angles_degrees": COLLOCATION_ANGLES_DEGREES,
                          "meridian_node_counts": MERIDIAN_NODE_COUNTS,
                          "ring_azimuth_counts": RING_AZIMUTH_COUNTS,
                          "direct_reference_azimuth_count": DIRECT_REFERENCE_AZIMUTH_COUNT,
                          "repeats": REPEATS, "wall_time_cap_seconds_per_case": WALL_TIME_CAP_SECONDS},
        "scope": ("Matrix-free image contribution K_image - V_image on a fixed exact sphere for the centered "
                  "Neumann half-space monopole trace. The two ring routes share the Helmholtz physics and "
                  "geometry but differ in ring integration: elliptic static subtraction versus direct "
                  "pointwise midpoint. The analytic reflected-monopole identity is the comparison reference. "
                  "This is numerical verification of this idealized formulation, not experimental validation, "
                  "a general gravity field, a force/acceleration result, an assembled matrix, or a solver."),
        "cases": [], "matrix_allocated": False,
        "preflight": {"status": "INDETERMINATE", "execution_authorized": False},
    }
    try:
        record["source_revision"] = source_revision()
        record["source_clean"] = True
        env = subprocess.run((sys.executable, str(ROOT / "scripts/verify_environment.py")), cwd=ROOT,
                             check=True, capture_output=True, text=True)
        record["environment_verification"] = json.loads(env.stdout)
        for theta in COLLOCATION_ANGLES_DEGREES:
            for nodes in MERIDIAN_NODE_COUNTS:
                for count in RING_AZIMUTH_COUNTS:
                    record["cases"].append(_measure(theta, nodes, "static_subtracted_ring", count))
                # Pointwise route is a high-resolution cross-check at each level.
                record["cases"].append(_measure(theta, nodes, "pointwise_midpoint", DIRECT_REFERENCE_AZIMUTH_COUNT))
        record["runtime"]["peak_rss_platform_units"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        record["status"] = "COMPLETED"
    except Exception as exc:  # noqa: BLE001 - Preserve any failed benchmark as an artifact.
        record["status"] = "FAILED"
        record["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    destination.write_bytes(payload)
    print(json.dumps({"status": record["status"], "output": destination.as_posix(),
                      "sha256": hashlib.sha256(payload).hexdigest(),
                      "cases": len(record["cases"]), "source_revision": record["source_revision"]}, sort_keys=True))
    return 0 if record["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
