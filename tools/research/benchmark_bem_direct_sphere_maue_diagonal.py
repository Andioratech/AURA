"""Calibrate the complete direct-sphere Maue self-panel action without a matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from aura.fields._bem_mesh import estimate_bem_dense_workspace, sphere_meridian_quadrature
from aura.fields._bem_singular import integrate_direct_sphere_maue_panel

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
PLANE_GAP_M = SPHERE_RADIUS_M
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
    files = {}
    aggregate = hashlib.sha256()
    for relative_path in LOCK_FILES:
        digest = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        files[relative_path.as_posix()] = digest
        aggregate.update(relative_path.as_posix().encode("utf-8") + b"\0")
        aggregate.update(bytes.fromhex(digest))
    return {"aggregate_sha256": aggregate.hexdigest(), "files": files}


def available_ram_bytes() -> int:
    available_kib = None
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        if line.startswith("MemAvailable:"):
            available_kib = int(line.split()[1])
            break
    if available_kib is None:
        raise RuntimeError("Cannot determine available RAM from /proc/meminfo.")
    available = available_kib * 1024
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


def digest_value(digest, mode: int, node_index: int, value: complex) -> None:
    value = complex(value)
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ArithmeticError("Direct sphere self-panel action returned a non-finite value.")
    digest.update(f"{mode}:{node_index}:".encode("ascii"))
    digest.update(value.real.hex().encode("ascii"))
    digest.update(b"\0")
    digest.update(value.imag.hex().encode("ascii"))
    digest.update(b"\n")


def evaluate_self_panels(
    panels: int,
    *,
    meridian_order: int,
    azimuth_samples: int,
    digest,
    wall_start: float | None = None,
    wall_time_cap_seconds: float = DEFAULT_WALL_TIME_CAP_SECONDS,
) -> int:
    quadrature = sphere_meridian_quadrature(
        SPHERE_RADIUS_M, panels=panels, order_per_panel=ORDER_PER_PANEL
    )
    expected_actions = len(quadrature) * 2
    action_count = 0

    for node_index, (field_theta, _surface_weight) in enumerate(quadrature):
        panel_index = node_index // ORDER_PER_PANEL
        left = math.pi * panel_index / panels
        right = math.pi * (panel_index + 1) / panels
        for mode in (0, 1):
            pressure = lambda theta, n=mode: 1.0 if n == 0 else math.cos(theta)
            tangent = lambda theta, n=mode: 0.0 if n == 0 else -math.sin(theta) / SPHERE_RADIUS_M
            value = integrate_direct_sphere_maue_panel(
                SPHERE_RADIUS_M,
                PLANE_GAP_M,
                field_theta,
                left,
                right,
                pressure,
                tangent,
                wave_number_rad_m=WAVE_NUMBER_RAD_M,
                azimuth_samples=azimuth_samples,
                meridian_order=meridian_order,
            )
            digest_value(digest, mode, node_index, value)
            action_count += 1
            if wall_start is not None and time.perf_counter() - wall_start > wall_time_cap_seconds:
                raise TimeoutError(
                    f"N={len(quadrature)} exceeded its {wall_time_cap_seconds:g} s repeat cap "
                    f"after {action_count} self-panel actions."
                )

    if action_count != expected_actions:
        raise RuntimeError(f"Expected {expected_actions} self-panel actions; observed {action_count}.")
    return action_count


def run_level(
    panels: int,
    *,
    meridian_order: int = ORDER_PER_PANEL,
    azimuth_samples: int = AZIMUTH_SAMPLES,
    wall_time_cap_seconds: float = DEFAULT_WALL_TIME_CAP_SECONDS,
) -> dict:
    if type(panels) is not int or panels < 1:
        raise ValueError("panels must be a positive integer")
    if type(meridian_order) is not int or not 2 <= meridian_order <= 256:
        raise ValueError("meridian_order must be from 2 through 256")
    if type(azimuth_samples) is not int or azimuth_samples < 4:
        raise ValueError("azimuth_samples must be at least four")
    if not math.isfinite(wall_time_cap_seconds) or wall_time_cap_seconds <= 0:
        raise ValueError("wall_time_cap_seconds must be finite and positive")

    repeats = []
    expected_actions = panels * ORDER_PER_PANEL * 2
    reference_checksum = None
    for repeat_index in range(REPEATS):
        digest = hashlib.sha256()
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        action_count = evaluate_self_panels(
            panels,
            meridian_order=meridian_order,
            azimuth_samples=azimuth_samples,
            digest=digest,
            wall_start=wall_start,
            wall_time_cap_seconds=wall_time_cap_seconds,
        )
        wall_seconds = time.perf_counter() - wall_start
        cpu_seconds = time.process_time() - cpu_start
        checksum = digest.hexdigest()
        if reference_checksum is None:
            reference_checksum = checksum
        elif checksum != reference_checksum:
            raise RuntimeError(f"Repeated N={panels * ORDER_PER_PANEL} output checksum changed.")
        if action_count != expected_actions:
            raise RuntimeError(f"Expected {expected_actions} actions, observed {action_count}.")
        repeats.append(
            {"repeat": repeat_index + 1, "wall_time_s": wall_seconds, "cpu_time_s": cpu_seconds}
        )

    wall_values = [entry["wall_time_s"] for entry in repeats]
    cpu_values = [entry["cpu_time_s"] for entry in repeats]
    return {
        "panels": panels,
        "order_per_panel": ORDER_PER_PANEL,
        "node_count": panels * ORDER_PER_PANEL,
        "self_panel_action_count_per_repeat": expected_actions,
        "self_panel_kernel": "direct_free_space_maue_with_cauchy_log_product_integration",
        "density_modes": [0, 1],
        "azimuth_samples": azimuth_samples,
        "meridian_residual_order": meridian_order,
        "repeat_records": repeats,
        "median_wall_time_s": statistics.median(wall_values),
        "maximum_wall_time_s": max(wall_values),
        "median_cpu_time_s": statistics.median(cpu_values),
        "self_panel_output_sha256": reference_checksum,
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
        "contract": "BEM-DIRECT-SPHERE-MAUE-SELF-PANEL-CALIBRATION-1.0",
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
            "process_peak_rss_bytes": None,
        },
        "configuration": {
            "sphere_radius_m": SPHERE_RADIUS_M,
            "plane_gap_m": PLANE_GAP_M,
            "size_parameter_ka": SIZE_PARAMETER_KA,
            "wave_number_rad_m": WAVE_NUMBER_RAD_M,
            "pressure_modes": [0, 1],
            "panels": list(PANEL_LEVELS),
            "gauss_nodes_per_panel": ORDER_PER_PANEL,
            "azimuth_samples": AZIMUTH_SAMPLES,
            "meridian_residual_order": ORDER_PER_PANEL,
            "repeats_per_level": REPEATS,
            "wall_time_cap_per_repeat_s": args.wall_time_cap_seconds,
            "ram_cap_bytes": RAM_CAP_BYTES,
        },
        "scope": (
            "Times all direct free-space singular Maue self-panel contributions at candidate composite "
            "GL4 collocation nodes for exact zonal pressure modes n=0 and n=1. Each call includes the "
            "regularized direct-ring residual and analytically restored Cauchy/log terms. It excludes "
            "off-diagonal panels, plane-image contributions, BIE jump terms, a full operator row, matrix "
            "assembly, linear solve, field accuracy and physical validation. The mesh-sized geometry list "
            "is streamed through actions; no dense matrix is allocated and the measurement does not "
            "authorize solver execution."
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
        for panels in PANEL_LEVELS:
            record["levels"].append(run_level(panels, wall_time_cap_seconds=args.wall_time_cap_seconds))
        peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        record["runtime"]["process_peak_rss_bytes"] = int(peak_rss * 1024)
        record["status"] = "COMPLETED"
    except KeyboardInterrupt:
        record["status"] = "FAILED"
        record["failure"] = {"type": "KeyboardInterrupt", "message": "Calibration interrupted by operator."}
    except Exception as exc:  # noqa: BLE001 - Preserve calibration failures in the artifact.
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
