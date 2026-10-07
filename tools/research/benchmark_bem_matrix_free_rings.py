"""Calibrate bounded off-diagonal direct ring kernels without storing a matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from aura.fields._bem_axisymmetric import (
    integrate_helmholtz_ring_green_gradient_zero_mode,
    integrate_helmholtz_ring_green_zero_mode,
)
from aura.fields._bem_mesh import estimate_bem_dense_workspace, sphere_meridian_quadrature

ROOT = Path(__file__).resolve().parents[2]
LOCK_FILES = (
    Path("requirements/environment-linux-py312.json"),
    Path("requirements/core-linux-py312.lock"),
    Path("requirements/dev-linux-py312.lock"),
)
RAM_CAP_BYTES = 16 * 1024**2
DEFAULT_WALL_TIME_CAP_SECONDS = 120.0
AZIMUTH_SAMPLES = 256
SPHERE_RADIUS_M = 0.017
SPHERE_CENTER_HEIGHT_M = 2.0 * SPHERE_RADIUS_M
SIZE_PARAMETER_KA = 2.3
WAVE_NUMBER_RAD_M = SIZE_PARAMETER_KA / SPHERE_RADIUS_M
MERIDIAN_LEVELS = ((4, 4), (8, 4), (16, 4))


def run_git(*arguments: str) -> str:
    result = subprocess.run(
        ("git", *arguments), cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def require_clean_source() -> str:
    if run_git("status", "--porcelain", "--untracked-files=normal"):
        raise RuntimeError("Calibration requires a clean source worktree.")
    return run_git("rev-parse", "HEAD")


def verify_environment() -> dict:
    result = subprocess.run(
        (sys.executable, str(ROOT / "scripts/verify_environment.py")),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def environment_lock_identity() -> dict[str, str]:
    entries = {}
    aggregate = hashlib.sha256()
    for relative_path in LOCK_FILES:
        contents = (ROOT / relative_path).read_bytes()
        digest = hashlib.sha256(contents).hexdigest()
        entries[relative_path.as_posix()] = digest
        aggregate.update(relative_path.as_posix().encode("utf-8") + b"\0")
        aggregate.update(bytes.fromhex(digest))
    return {"aggregate_sha256": aggregate.hexdigest(), "files": entries}


def available_ram_bytes() -> int:
    mem_available_kib = None
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        if line.startswith("MemAvailable:"):
            mem_available_kib = int(line.split()[1])
            break
    if mem_available_kib is None:
        raise RuntimeError("Cannot determine currently available RAM from /proc/meminfo.")
    available = mem_available_kib * 1024
    limit_path, current_path = Path("/sys/fs/cgroup/memory.max"), Path("/sys/fs/cgroup/memory.current")
    if limit_path.is_file() and current_path.is_file():
        limit = limit_path.read_text(encoding="ascii").strip()
        if limit != "max":
            cgroup_available = max(0, int(limit) - int(current_path.read_text(encoding="ascii")))
            available = min(available, cgroup_available)
    return available


def output_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT / "results" / "diagnostics"):
        raise ValueError("Output must be stored under results/diagnostics/.")
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite an existing calibration artifact: {path}")
    return path


def digest_value(digest, value: complex) -> None:
    digest.update(value.real.hex().encode("ascii"))
    digest.update(b"\0")
    digest.update(value.imag.hex().encode("ascii"))
    digest.update(b"\n")


def run_level(panels: int, order_per_panel: int, wall_time_cap_seconds: float) -> dict:
    quadrature = sphere_meridian_quadrature(
        SPHERE_RADIUS_M, panels=panels, order_per_panel=order_per_panel
    )
    meridian = tuple(
        (
            SPHERE_RADIUS_M * math.sin(theta),
            SPHERE_CENTER_HEIGHT_M + SPHERE_RADIUS_M * math.cos(theta),
            weight,
        )
        for theta, weight in quadrature
    )
    node_count = len(meridian)
    expected_pairs = node_count * (node_count - 1)
    repeats = []
    reference_checksum = None

    for repeat_index in range(3):
        digest = hashlib.sha256()
        pair_count = 0
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        for target_index, (field_radius, field_height, _) in enumerate(meridian):
            for source_index, (source_radius, source_height, surface_weight) in enumerate(meridian):
                if source_index == target_index:
                    continue
                scalar = integrate_helmholtz_ring_green_zero_mode(
                    field_radius,
                    field_height,
                    source_radius,
                    source_height,
                    wave_number_rad_m=WAVE_NUMBER_RAD_M,
                    azimuth_samples=AZIMUTH_SAMPLES,
                ) * surface_weight
                field_gradient, source_gradient = integrate_helmholtz_ring_green_gradient_zero_mode(
                    field_radius,
                    field_height,
                    source_radius,
                    source_height,
                    wave_number_rad_m=WAVE_NUMBER_RAD_M,
                    azimuth_samples=AZIMUTH_SAMPLES,
                )
                for value in (
                    scalar,
                    field_gradient[0] * surface_weight,
                    field_gradient[1] * surface_weight,
                    source_gradient[0] * surface_weight,
                    source_gradient[1] * surface_weight,
                ):
                    digest_value(digest, value)
                pair_count += 1
                if time.perf_counter() - wall_start > wall_time_cap_seconds:
                    raise TimeoutError(
                        f"N={node_count} repeat {repeat_index + 1} exceeded its "
                        f"{wall_time_cap_seconds:g} s wall-time cap after {pair_count} pairs."
                    )
        wall_seconds = time.perf_counter() - wall_start
        cpu_seconds = time.process_time() - cpu_start
        checksum = digest.hexdigest()
        if reference_checksum is None:
            reference_checksum = checksum
        elif checksum != reference_checksum:
            raise RuntimeError(f"Repeated N={node_count} kernel output checksum changed.")
        if pair_count != expected_pairs:
            raise RuntimeError(f"Expected {expected_pairs} off-diagonal pairs, observed {pair_count}.")
        repeats.append({"repeat": repeat_index + 1, "wall_time_s": wall_seconds, "cpu_time_s": cpu_seconds})

    wall_values = [item["wall_time_s"] for item in repeats]
    cpu_values = [item["cpu_time_s"] for item in repeats]
    return {
        "panels": panels,
        "order_per_panel": order_per_panel,
        "node_count": node_count,
        "meridian_pair_count": expected_pairs,
        "singular_diagonal_pairs_skipped": node_count,
        "azimuth_samples_per_ring_pair": AZIMUTH_SAMPLES,
        "ring_kernel_families": ["single_layer_scalar", "field_and_source_first_gradients"],
        "repeat_records": repeats,
        "median_wall_time_s": statistics.median(wall_values),
        "maximum_wall_time_s": max(wall_values),
        "median_cpu_time_s": statistics.median(cpu_values),
        "kernel_output_sha256": reference_checksum,
        "matrix_allocated": False,
    }


def write_record(path: Path, record: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="new JSON path under results/diagnostics/")
    parser.add_argument(
        "--wall-time-cap-seconds", type=float, default=DEFAULT_WALL_TIME_CAP_SECONDS
    )
    args = parser.parse_args(argv)
    destination = output_path(args.output)
    if not math.isfinite(args.wall_time_cap_seconds) or args.wall_time_cap_seconds <= 0:
        parser.error("--wall-time-cap-seconds must be finite and positive")

    record = {
        "contract": "BEM-MATRIX-FREE-RING-CALIBRATION-1.0",
        "status": "RUNNING",
        "created_utc": datetime.now(UTC).isoformat(),
        "source_revision": None,
        "source_clean": False,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment_lock": environment_lock_identity(),
        "environment_verification": None,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "available_ram_bytes_at_start": None,
        },
        "configuration": {
            "sphere_radius_m": SPHERE_RADIUS_M,
            "sphere_center_height_m": SPHERE_CENTER_HEIGHT_M,
            "size_parameter_ka": SIZE_PARAMETER_KA,
            "wave_number_rad_m": WAVE_NUMBER_RAD_M,
            "azimuth_samples": AZIMUTH_SAMPLES,
            "levels": [
                {"panels": panels, "order_per_panel": order}
                for panels, order in MERIDIAN_LEVELS
            ],
            "repeats_per_level": 3,
            "wall_time_cap_per_repeat_s": args.wall_time_cap_seconds,
            "ram_cap_bytes": RAM_CAP_BYTES,
        },
        "scope": (
            "Direct free-space single-layer scalar and field/source first-gradient ring kernels "
            "for off-diagonal exact-sphere meridian pairs only. The singular diagonal, Maue and "
            "other hypersingular terms, image kernels, matrix assembly, linear solve and field "
            "accuracy are excluded. This timing does not authorize solver execution."
        ),
        "levels": [],
    }
    try:
        record["source_revision"] = require_clean_source()
        record["source_clean"] = True
        record["environment_verification"] = verify_environment()
        available = available_ram_bytes()
        record["runtime"]["available_ram_bytes_at_start"] = available
        record["preflight"] = [
            estimate_bem_dense_workspace(
                panels=panels,
                order_per_panel=order,
                ram_cap_bytes=RAM_CAP_BYTES,
                available_ram_bytes=available,
            )
            for panels, order in MERIDIAN_LEVELS
        ]
        for panels, order in MERIDIAN_LEVELS:
            record["levels"].append(run_level(panels, order, args.wall_time_cap_seconds))
        record["status"] = "COMPLETED"
    except KeyboardInterrupt as exc:
        record["status"] = "FAILED"
        record["failure"] = {
            "type": type(exc).__name__,
            "message": "Calibration interrupted by operator.",
        }
    except Exception as exc:  # noqa: BLE001 - Preserve any failed calibration as an artifact.
        record["status"] = "FAILED"
        record["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    artifact_sha256 = write_record(destination, record)
    print(json.dumps({"status": record["status"], "output": str(destination), "sha256": artifact_sha256}))
    return 0 if record["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
