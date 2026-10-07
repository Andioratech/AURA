"""Characterize near-plane image mixed-normal ring quadrature without a matrix."""

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

from aura.fields._bem_axisymmetric import _integrate_ring_image_mixed_normal
from aura.fields._bem_green import _free_space_mixed_normal_derivative
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
FIELD_SOURCE_ANGLES_DEGREES = ((175.0, 175.1), (175.0, 175.0), (179.0, 179.1))
CANDIDATE_AZIMUTH_COUNTS = (16, 32, 64, 128, 256, 512)
SPLIT_MULTIPLES = (2.0, 4.0, 6.0, 8.0)
REFERENCE_AZIMUTH_COUNTS = (65_536, 131_072)
REPEATS = 3
DEFAULT_WALL_TIME_CAP_SECONDS = 120.0


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


def environment_lock_identity() -> dict:
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
        raise FileExistsError(f"Refusing to overwrite an existing result: {path}")
    return path


def geometry(field_theta_degrees: float, source_theta_degrees: float) -> dict:
    field_theta = math.radians(field_theta_degrees)
    source_theta = math.radians(source_theta_degrees)
    radius = SPHERE_RADIUS_M
    gap = PLANE_GAP_M
    return {
        "field_radius_m": radius * math.sin(field_theta),
        "field_height_m": gap + radius * (1.0 + math.cos(field_theta)),
        "field_normal": (-math.sin(field_theta), 0.0, -math.cos(field_theta)),
        "source_radius_m": radius * math.sin(source_theta),
        "source_height_m": gap + radius * (1.0 + math.cos(source_theta)),
        "source_normal_rz": (-math.sin(source_theta), -math.cos(source_theta)),
        "field_theta_degrees": field_theta_degrees,
        "source_theta_degrees": source_theta_degrees,
    }


def candidate_mesh_pairs() -> tuple[dict, ...]:
    """Select the most localized self and distinct ring pairs at each GL4 level."""
    selected = []
    for node_count in (16, 32, 64):
        quadrature = sphere_meridian_quadrature(
            SPHERE_RADIUS_M,
            panels=node_count // 4,
            order_per_panel=4,
        )
        nodes = tuple(
            (
                theta,
                SPHERE_RADIUS_M * math.sin(theta),
                PLANE_GAP_M + SPHERE_RADIUS_M * (1.0 + math.cos(theta)),
            )
            for theta, _ in quadrature
        )

        def angular_scale(
            field_index: int, source_index: int, node_data=nodes
        ) -> float:
            _, field_radius, field_height = node_data[field_index]
            _, source_radius, source_height = node_data[source_index]
            return math.hypot(
                field_radius - source_radius,
                field_height + source_height,
            ) / math.sqrt(field_radius * source_radius)

        pair_groups = (
            (
                "minimum_angular_scale_self_pair",
                min((angular_scale(index, index), index, index) for index in range(node_count)),
            ),
            (
                "minimum_angular_scale_distinct_pair",
                min(
                    (angular_scale(field_index, source_index), field_index, source_index)
                    for field_index in range(node_count)
                    for source_index in range(field_index + 1, node_count)
                ),
            ),
        )
        for selection, (scale, field_index, source_index) in pair_groups:
            field_theta = math.degrees(nodes[field_index][0])
            source_theta = math.degrees(nodes[source_index][0])
            case = geometry(field_theta, source_theta)
            case["mesh_pair"] = {
                "selection": selection,
                "node_count": node_count,
                "panels": node_count // 4,
                "order_per_panel": 4,
                "field_node_index": field_index,
                "source_node_index": source_index,
                "field_theta_rad": nodes[field_index][0],
                "source_theta_rad": nodes[source_index][0],
                "angular_scale_rad": scale,
            }
            selected.append(case)
    return tuple(selected)


def split_image_ring(samples: int, rule: str, split_multiple: float, case: dict) -> complex:
    return _integrate_ring_image_mixed_normal(
        case["field_radius_m"],
        case["field_height_m"],
        case["field_normal"],
        case["source_radius_m"],
        case["source_height_m"],
        case["source_normal_rz"],
        1.0 + 0.0j,
        WAVE_NUMBER_RAD_M,
        samples,
        rule,
        split_multiple,
    )


def independent_midpoint_reference(samples: int, case: dict) -> complex:
    """Integrate pointwise with a full-period uniform midpoint sum and fsum."""
    step = 2.0 * math.pi / samples
    real_terms = []
    imag_terms = []
    field = (case["field_radius_m"], 0.0, case["field_height_m"])
    for index in range(samples):
        angle = -math.pi + (index + 0.5) * step
        cosine, sine = math.cos(angle), math.sin(angle)
        image_point = (
            case["source_radius_m"] * cosine,
            case["source_radius_m"] * sine,
            -case["source_height_m"],
        )
        image_normal = (
            case["source_normal_rz"][0] * cosine,
            case["source_normal_rz"][0] * sine,
            -case["source_normal_rz"][1],
        )
        value = _free_space_mixed_normal_derivative(
            field,
            image_point,
            case["field_normal"],
            image_normal,
            WAVE_NUMBER_RAD_M,
        ) * step
        real_terms.append(value.real)
        imag_terms.append(value.imag)
    return complex(math.fsum(real_terms), math.fsum(imag_terms))


def encode_value(value: complex) -> str:
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ArithmeticError("Image ring quadrature returned a non-finite result.")
    return f"{value.real.hex()}:{value.imag.hex()}"


def measure_case(case: dict, *, reference_counts=REFERENCE_AZIMUTH_COUNTS,
                 candidate_counts=CANDIDATE_AZIMUTH_COUNTS, split_multiples=SPLIT_MULTIPLES,
                 repeats=REPEATS, wall_time_cap_seconds=DEFAULT_WALL_TIME_CAP_SECONDS) -> dict:
    references = []
    reference_values = []
    for count in reference_counts:
        start = time.perf_counter()
        value = independent_midpoint_reference(count, case)
        elapsed = time.perf_counter() - start
        if elapsed > wall_time_cap_seconds:
            raise TimeoutError(f"{count}-sample independent reference exceeded its wall-time cap.")
        references.append({"azimuth_samples": count, "value": encode_value(value),
                           "wall_time_s": elapsed})
        reference_values.append(value)
    high_reference = reference_values[-1]
    lower_reference = reference_values[-2]
    reference_delta = abs(high_reference - lower_reference)
    results = []
    for count in candidate_counts:
        candidates = [{"rule": "midpoint", "split_multiple": None}]
        candidates.extend({"rule": "gap_scaled", "split_multiple": multiple}
                         for multiple in split_multiples)
        for candidate in candidates:
            repeat_values = []
            repeat_times = []
            for _ in range(repeats):
                start = time.perf_counter()
                value = split_image_ring(count, candidate["rule"],
                                         candidate["split_multiple"] or 8.0, case)
                elapsed = time.perf_counter() - start
                if elapsed > wall_time_cap_seconds:
                    raise TimeoutError(
                        f"{candidate['rule']} N={count} exceeded its wall-time cap."
                    )
                repeat_times.append(elapsed)
                repeat_values.append(encode_value(value))
            if len(set(repeat_values)) != 1:
                raise RuntimeError("Repeated image ring result changed within one configuration.")
            value = split_image_ring(count, candidate["rule"], candidate["split_multiple"] or 8.0, case)
            results.append({
                "azimuth_samples_per_interval": count,
                "rule": candidate["rule"],
                "split_multiple": candidate["split_multiple"],
                "value": encode_value(value),
                "absolute_difference_from_high_reference": abs(value - high_reference),
                "relative_difference_from_high_reference": (
                    abs(value - high_reference) / abs(high_reference) if high_reference else None
                ),
                "repeat_wall_times_s": repeat_times,
                "median_repeat_wall_time_s": statistics.median(repeat_times),
                "repeat_checksum": hashlib.sha256("\n".join(repeat_values).encode("ascii")).hexdigest(),
            })
    return {
        "field_theta_degrees": case["field_theta_degrees"],
        "source_theta_degrees": case["source_theta_degrees"],
        "mesh_pair": case.get("mesh_pair"),
        "image_separation_m": math.hypot(
            case["field_radius_m"] - case["source_radius_m"],
            case["field_height_m"] + case["source_height_m"],
        ),
        "reference_midpoint": references,
        "reference_pair_absolute_difference": reference_delta,
        "reference_pair_relative_difference": (
            reference_delta / abs(high_reference) if high_reference else None
        ),
        "candidate_results": results,
    }


def write_record(path: Path, record: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="new JSON path under results/diagnostics/")
    parser.add_argument("--wall-time-cap-seconds", type=float, default=DEFAULT_WALL_TIME_CAP_SECONDS)
    args = parser.parse_args(argv)
    destination = output_path(args.output)
    if not math.isfinite(args.wall_time_cap_seconds) or args.wall_time_cap_seconds <= 0:
        parser.error("--wall-time-cap-seconds must be finite and positive")

    record = {
        "contract": "BEM-NEAR-PLANE-IMAGE-RING-QUALIFICATION-1.1",
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
            "cpu_count": os.cpu_count(),
            "available_ram_bytes_at_start": None,
        },
        "configuration": {
            "sphere_radius_m": SPHERE_RADIUS_M,
            "plane_gap_m": PLANE_GAP_M,
            "frequency_hz": FREQUENCY_HZ,
            "sound_speed_m_s": SOUND_SPEED_M_S,
            "wave_number_rad_m": WAVE_NUMBER_RAD_M,
            "field_source_angles_degrees": FIELD_SOURCE_ANGLES_DEGREES,
            "candidate_mesh_nodes": [16, 32, 64],
            "candidate_mesh_selection": [
                "minimum_angular_scale_self_pair",
                "minimum_angular_scale_distinct_pair",
            ],
            "candidate_azimuth_counts_per_interval": CANDIDATE_AZIMUTH_COUNTS,
            "split_multiples": SPLIT_MULTIPLES,
            "reference_azimuth_counts": REFERENCE_AZIMUTH_COUNTS,
            "repeats_per_candidate": REPEATS,
            "wall_time_cap_seconds_per_reference_or_repeat": args.wall_time_cap_seconds,
        },
        "scope": (
            "Pointwise image mixed-normal ring integrals for three exploratory angle pairs and the most "
            "angularly localized self/distinct ring pairs from candidate GL4 meshes at N=16/32/64. "
            "The candidate uses the existing periodic midpoint and gap-scaled split rules; the comparison "
            "uses a full-period uniform midpoint sum at two larger sample counts with the pointwise kernel. "
            "This is finite-case quadrature sensitivity evidence, not an error bound, a surface integral, "
            "an assembled operator, solver runtime, field acceptance, or physical validation."
        ),
        "cases": [],
        "matrix_allocated": False,
        "preflight": {"status": "INDETERMINATE", "execution_authorized": False},
    }
    try:
        record["source_revision"] = require_clean_source()
        record["source_clean"] = True
        record["environment_verification"] = verify_environment()
        if record["environment_verification"]["errors"]:
            raise RuntimeError("ENV-1.0 verification did not pass.")
        record["runtime"]["available_ram_bytes_at_start"] = available_ram_bytes()
        start = time.perf_counter()
        planned_cases = [
            geometry(field_angle, source_angle)
            for field_angle, source_angle in FIELD_SOURCE_ANGLES_DEGREES
        ] + list(candidate_mesh_pairs())
        for case in planned_cases:
            measured = measure_case(case, wall_time_cap_seconds=args.wall_time_cap_seconds)
            for reference in measured["reference_midpoint"]:
                if reference["wall_time_s"] > args.wall_time_cap_seconds:
                    raise TimeoutError("Independent reference exceeded its wall-time cap.")
            if time.perf_counter() - start > len(planned_cases) * args.wall_time_cap_seconds:
                raise TimeoutError("Near-plane image qualification exceeded its total wall-time cap.")
            record["cases"].append(measured)
        record["runtime"]["available_ram_bytes_at_end"] = available_ram_bytes()
        record["runtime"]["process_peak_rss_bytes"] = (
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        )
        record["status"] = "COMPLETED"
    except (ArithmeticError, OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        record["status"] = "FAILED"
        record["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        digest = write_record(destination, record)
    print(json.dumps({"status": record["status"], "output": str(destination), "sha256": digest}))
    return 0 if record["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
