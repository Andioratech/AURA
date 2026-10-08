"""Test composite meridian subdivisions at fixed per-panel CBIE order."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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

ROOT = Path(__file__).resolve().parents[2]
BASE_SCRIPT = ROOT / "tools/research/benchmark_bem_exact_sphere_combined_cbie.py"
COLLOCATION_ANGLES_DEGREES = (179.0,)
MERIDIAN_SPLIT_FACTOR = 8.0
MERIDIAN_SUBDIVISIONS = (10,)
MERIDIAN_ORDER = 256
DIRECT_AZIMUTH_SAMPLES = 4_096
IMAGE_AZIMUTH_SAMPLES = 2_048
REPEATS = 2
WALL_TIME_LIMIT_SECONDS = 120.0


def _base_module():
    spec = importlib.util.spec_from_file_location("combined_cbie_action", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load combined CBIE action from {BASE_SCRIPT}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _decode(value: str) -> complex:
    real, imaginary = value.split(":")
    return complex(float.fromhex(real), float.fromhex(imaginary))


def case_grid() -> tuple[tuple[float, int], ...]:
    return tuple(
        (theta, subdivisions)
        for theta in COLLOCATION_ANGLES_DEGREES
        for subdivisions in MERIDIAN_SUBDIVISIONS
    )


def measure_case(theta_degrees: float, subdivisions: int, *, repeats: int = REPEATS) -> dict:
    if theta_degrees not in COLLOCATION_ANGLES_DEGREES:
        raise ValueError("Collocation angle is not in the frozen set.")
    if type(subdivisions) is not int or subdivisions not in MERIDIAN_SUBDIVISIONS:
        raise ValueError("Meridian subdivision count is not in the frozen set.")
    if type(repeats) is not int or repeats < 2:
        raise ValueError("At least two repeats are required.")

    action = _base_module().evaluate_action
    values, timings = [], []
    for _ in range(repeats):
        started = time.perf_counter()
        value = action(
            theta_degrees,
            MERIDIAN_ORDER,
            direct_azimuth_samples=DIRECT_AZIMUTH_SAMPLES,
            image_azimuth_samples=IMAGE_AZIMUTH_SAMPLES,
            meridian_split_factor=MERIDIAN_SPLIT_FACTOR,
            meridian_subdivisions=subdivisions,
        )
        elapsed = time.perf_counter() - started
        if elapsed > WALL_TIME_LIMIT_SECONDS:
            raise TimeoutError(
                f"Case theta={theta_degrees}, subdivisions={subdivisions} exceeded "
                f"{WALL_TIME_LIMIT_SECONDS}s after evaluation."
            )
        values.append(value)
        timings.append(elapsed)

    encoded = [json.dumps(value, sort_keys=True, allow_nan=False) for value in values]
    if len(set(encoded)) != 1:
        raise RuntimeError(
            f"Repeated action values differ for theta={theta_degrees}, subdivisions={subdivisions}."
        )
    record = {
        "collocation_theta_degrees": theta_degrees,
        "meridian_split_factor": MERIDIAN_SPLIT_FACTOR,
        "meridian_subdivisions_per_active_interval": subdivisions,
        "meridian_order_per_active_subinterval": MERIDIAN_ORDER,
        "direct_azimuth_samples": DIRECT_AZIMUTH_SAMPLES,
        "image_azimuth_samples": IMAGE_AZIMUTH_SAMPLES,
        **values[-1],
        "repeat_checksum_sha256": hashlib.sha256("\n".join(encoded).encode()).hexdigest(),
        "repeat_wall_times_s": timings,
    }
    jump = _decode(record["jump_half_pressure"])
    direct_double = _decode(record["direct_double_layer"])
    image_double = _decode(record["image_double_layer"])
    direct_single = _decode(record["direct_single_layer"])
    image_single = _decode(record["image_single_layer"])
    residual = jump + direct_double + image_double - direct_single - image_single
    if residual != _decode(record["cbie_residual"]):
        raise ArithmeticError("Recorded CBIE terms do not reconstruct the residual.")
    if not math.isfinite(record["normalized_residual_by_boundary_pressure"]):
        raise ArithmeticError("Normalized CBIE residual is non-finite.")
    return record


def _output_path(value: str) -> Path:
    destination = (ROOT / value).resolve()
    if not destination.is_relative_to(ROOT / "results" / "diagnostics"):
        raise ValueError("Output must be stored under results/diagnostics/.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing result: {destination}")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="new JSON path under results/diagnostics/")
    args = parser.parse_args(argv)
    destination = _output_path(args.output)
    record = {
        "contract": "BEM-EXACT-SPHERE-CBIE-COMPOSITE-SUBDIVISION-1.0",
        "status": "RUNNING",
        "created_utc": datetime.now(UTC).isoformat(),
        "source_revision": None,
        "source_clean": False,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment_lock": None,
        "environment_verification": None,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "peak_rss_platform_units": None,
        },
        "configuration": {
            "sphere_radius_m": 0.025,
            "plane_gap_m": 0.0001,
            "frequency_hz": 25_230.0,
            "sound_speed_m_s": 346.0,
            "boundary_source": "centered monopole with rigid-plane Neumann image",
            "normal_convention": "AURA normal into the sphere",
            "collocation_angles_degrees": COLLOCATION_ANGLES_DEGREES,
            "meridian_split_factor": MERIDIAN_SPLIT_FACTOR,
            "meridian_subdivisions_per_active_interval": MERIDIAN_SUBDIVISIONS,
            "meridian_order_per_active_subinterval": MERIDIAN_ORDER,
            "direct_azimuth_samples": DIRECT_AZIMUTH_SAMPLES,
            "image_azimuth_samples": IMAGE_AZIMUTH_SAMPLES,
            "repeats": REPEATS,
            "wall_time_limit_seconds_per_case": WALL_TIME_LIMIT_SECONDS,
            "wall_time_limit_enforced_after_case": True,
        },
        "analytic_reference": "0 = 0.5*p(x) + K_direct[p] + K_image[p] - V_direct[q] - V_image[q]",
        "scope": (
            "Sensitivity to composite subdivisions of active meridian intervals in one streamed "
            "exact-sphere CBIE action. The cutoff multiplier, per-panel meridian order and direct/image "
            "azimuth counts are fixed. This is finite "
            "quadrature sensitivity, not an error bound, complete operator, matrix, solver, field "
            "acceptance, physical validation, force/acceleration result, or gravity equivalence."
        ),
        "cases": [],
        "matrix_allocated": False,
        "solver_started": False,
        "preflight": {"status": "INDETERMINATE", "execution_authorized": False},
    }
    try:
        base = _base_module()
        record["environment_lock"] = base.environment_identity()
        record["source_revision"] = base.require_clean_source()
        record["source_clean"] = True
        environment = subprocess.run(
            (sys.executable, str(ROOT / "scripts/verify_environment.py")),
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        record["environment_verification"] = json.loads(environment.stdout)
        for theta, subdivisions in case_grid():
            record["cases"].append(measure_case(theta, subdivisions))
        record["runtime"]["peak_rss_platform_units"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        record["status"] = "COMPLETED"
    except Exception as exc:  # noqa: BLE001 - Preserve every failed sweep as an artifact.
        record["status"] = "FAILED"
        record["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    destination.write_bytes(payload)
    print(json.dumps({
        "status": record["status"],
        "output": destination.as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "cases": len(record["cases"]),
        "source_revision": record["source_revision"],
    }, sort_keys=True))
    return 0 if record["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
