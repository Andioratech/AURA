"""Time isolated BEM singular-panel correction primitives, without a matrix."""

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

from aura.fields._bem_mesh import estimate_bem_dense_workspace
from aura.fields._bem_singular import (
    integrate_cauchy_principal_value_panel,
    integrate_logarithmic_panel,
)

ROOT = Path(__file__).resolve().parents[2]
LOCK_FILES = (
    Path("requirements/environment-linux-py312.json"),
    Path("requirements/core-linux-py312.lock"),
    Path("requirements/dev-linux-py312.lock"),
)
RAM_CAP_BYTES = 16 * 1024**2
DEFAULT_WALL_TIME_CAP_SECONDS = 120.0
SPHERE_RADIUS_M = 0.017
SPHERE_CENTER_HEIGHT_M = 2.0 * SPHERE_RADIUS_M
SIZE_PARAMETER_KA = 2.3
WAVE_NUMBER_RAD_M = SIZE_PARAMETER_KA / SPHERE_RADIUS_M
ORDER_PER_PANEL = 4
PANEL_LEVELS = (4, 8, 16)
REPEATS = 3


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


def environment_lock_identity() -> dict[str, dict[str, str] | str]:
    entries = {}
    aggregate = hashlib.sha256()
    for relative_path in LOCK_FILES:
        digest = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
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
    limit_path = Path("/sys/fs/cgroup/memory.max")
    current_path = Path("/sys/fs/cgroup/memory.current")
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
    value = complex(value)
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ArithmeticError("Singular-panel primitive returned a non-finite value.")
    digest.update(value.real.hex().encode("ascii"))
    digest.update(b"\0")
    digest.update(value.imag.hex().encode("ascii"))
    digest.update(b"\n")


def evaluate_corrections(panels: int, order: int, digest) -> int:
    from aura.fields.numerical import gauss_legendre_rule

    nodes, _weights = gauss_legendre_rule(ORDER_PER_PANEL)
    correction_count = 0
    panel_width = math.pi / panels
    for panel_index in range(panels):
        left = panel_index * panel_width
        right = (panel_index + 1) * panel_width
        midpoint, half_width = 0.5 * (left + right), 0.5 * (right - left)
        for node in nodes:
            theta = midpoint + half_width * node
            log_scale = 8.0 * math.sin(theta)
            for degree in (0, 1):
                tangent = 0.0 if degree == 0 else -math.sin(theta) / SPHERE_RADIUS_M

                def pressure_at(position: float, mode: int = degree) -> float:
                    return 1.0 if mode == 0 else math.cos(position)

                def pressure_slope(position: float, mode: int = degree) -> float:
                    return 0.0 if mode == 0 else -math.sin(position)

                cauchy = integrate_cauchy_principal_value_panel(
                    lambda _, value=tangent: value,
                    left,
                    right,
                    theta,
                    order=order,
                )
                logarithmic = integrate_logarithmic_panel(
                    lambda position: (
                        SPHERE_RADIUS_M
                        * WAVE_NUMBER_RAD_M**2
                        * pressure_at(position)
                        / (2.0 * math.pi)
                    ),
                    left,
                    right,
                    theta,
                    log_scale=log_scale,
                    density_derivative=(
                        None
                        if degree == 0
                        else lambda position: (
                            SPHERE_RADIUS_M
                            * WAVE_NUMBER_RAD_M**2
                            * pressure_slope(position)
                            / (2.0 * math.pi)
                        )
                    ),
                    order=order,
                )
                digest_value(digest, cauchy)
                digest_value(digest, logarithmic)
                correction_count += 1
    return correction_count


def run_level(panels: int, order: int, wall_time_cap_seconds: float) -> dict:
    if type(panels) is not int or panels < 1:
        raise ValueError("panels must be a positive integer")
    if type(order) is not int or not 2 <= order <= 256:
        raise ValueError("order must be an integer from 2 through 256")
    if not math.isfinite(wall_time_cap_seconds) or wall_time_cap_seconds <= 0:
        raise ValueError("wall_time_cap_seconds must be finite and positive")
    repeats = []
    reference_checksum = None
    expected_corrections = panels * ORDER_PER_PANEL * 2
    for repeat_index in range(REPEATS):
        digest = hashlib.sha256()
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        correction_count = evaluate_corrections(panels, order, digest)
        wall_seconds = time.perf_counter() - wall_start
        cpu_seconds = time.process_time() - cpu_start
        if wall_seconds > wall_time_cap_seconds:
            raise TimeoutError(
                f"N={panels * ORDER_PER_PANEL} repeat {repeat_index + 1} exceeded its "
                f"{wall_time_cap_seconds:g} s wall-time cap."
            )
        checksum = digest.hexdigest()
        if reference_checksum is None:
            reference_checksum = checksum
        elif checksum != reference_checksum:
            raise RuntimeError(f"Repeated N={panels * ORDER_PER_PANEL} correction checksum changed.")
        if correction_count != expected_corrections:
            raise RuntimeError(
                f"Expected {expected_corrections} correction cases, observed {correction_count}."
            )
        repeats.append(
            {"repeat": repeat_index + 1, "wall_time_s": wall_seconds, "cpu_time_s": cpu_seconds}
        )

    wall_values = [item["wall_time_s"] for item in repeats]
    cpu_values = [item["cpu_time_s"] for item in repeats]
    return {
        "panels": panels,
        "order_per_panel": ORDER_PER_PANEL,
        "node_count": panels * ORDER_PER_PANEL,
        "singular_correction_cases": expected_corrections,
        "singular_primitive_families": [
            "cauchy_principal_value_panel",
            "logarithmic_panel",
        ],
        "density_modes": [0, 1],
        "primitive_quadrature_order": order,
        "repeat_records": repeats,
        "median_wall_time_s": statistics.median(wall_values),
        "maximum_wall_time_s": max(wall_values),
        "median_cpu_time_s": statistics.median(cpu_values),
        "correction_output_sha256": reference_checksum,
        "matrix_allocated": False,
    }


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
        "contract": "BEM-SINGULAR-PANEL-PRIMITIVE-CALIBRATION-1.0",
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
            "meridian_parameter": "theta in radians",
            "panels": list(PANEL_LEVELS),
            "gauss_nodes_per_panel": ORDER_PER_PANEL,
            "density_modes": [0, 1],
            "primitive_orders": list(PANEL_LEVELS),
            "repeats_per_level": REPEATS,
            "wall_time_cap_per_repeat_s": args.wall_time_cap_seconds,
            "ram_cap_bytes": RAM_CAP_BYTES,
        },
        "scope": (
            "Times only the existing one-dimensional Cauchy principal-value and logarithmic "
            "product-integration primitives on each candidate GL4 collocation node's containing "
            "meridian panel, for n=0 and n=1 exact-sphere pressure modes. It excludes the "
            "regularized direct ring-kernel residual, non-singular panels, image terms, a complete "
            "diagonal operator action, matrix assembly, solve, field accuracy and physical validation. "
            "This component microbenchmark does not estimate solver runtime or authorize execution."
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
                order_per_panel=ORDER_PER_PANEL,
                ram_cap_bytes=RAM_CAP_BYTES,
                available_ram_bytes=available,
            )
            for panels in PANEL_LEVELS
        ]
        for panels, primitive_order in zip(PANEL_LEVELS, PANEL_LEVELS, strict=True):
            record["levels"].append(
                run_level(panels, primitive_order, args.wall_time_cap_seconds)
            )
        record["status"] = "COMPLETED"
    except KeyboardInterrupt as exc:
        record["status"] = "FAILED"
        record["failure"] = {"type": type(exc).__name__, "message": "Calibration interrupted by operator."}
    except Exception as exc:  # noqa: BLE001 - Preserve any failed calibration as an artifact.
        record["status"] = "FAILED"
        record["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    destination.write_bytes(encoded)
    artifact_sha256 = hashlib.sha256(encoded).hexdigest()
    print(json.dumps({"status": record["status"], "output": str(destination), "sha256": artifact_sha256}))
    return 0 if record["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
