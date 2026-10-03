"""Conservative, solver-specific resource planning before numerical allocation."""

from __future__ import annotations

import math
import os
import re
import resource
import shutil
import sys
from pathlib import Path

from aura.errors import IncompleteEvidenceError, InvalidInputError

WORKLOAD_CONTRACT = "AIR-SERIES-WORKLOAD-1.1"
CALIBRATION_CONTRACT = "AIR-SERIES-CALIBRATION-1.1"
MAX_POINT_CHUNK = 256
MAX_QUADRATURE_ORDER = 512
MAX_BESSEL_START = 8192
MAX_PLAN_INTEGER = (1 << 63) - 1
ORDER_COMPLEX_VECTORS = 8
ORDER_REAL_VECTORS = 2
RAM_HEADROOM_FACTOR = 2
SERIALIZED_BYTES_PER_POINT = 2048
SERIALIZATION_FIXED_BYTES = 64 * 1024
SOURCE_REVISION = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _positive_integer(value, path: str, *, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum or value > MAX_PLAN_INTEGER:
        raise InvalidInputError(
            "PREFLIGHT_DIMENSION", path,
            f"Expected an integer from {minimum} through {MAX_PLAN_INTEGER}.",
        )
    return value


def _positive_finite(value, path: str) -> float:
    if type(value) not in (int, float) or type(value) is bool:
        raise InvalidInputError("PREFLIGHT_CALIBRATION", path, "Expected a finite positive number.")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise InvalidInputError("PREFLIGHT_CALIBRATION", path, "Expected a finite positive number.")
    return result


def _checked_product(*values: int, path: str) -> int:
    result = 1
    for value in values:
        if value and result > MAX_PLAN_INTEGER // value:
            raise InvalidInputError("PREFLIGHT_OVERFLOW", path, "Resource estimate exceeds 64-bit range.")
        result *= value
    return result


def _checked_sum(*values: int, path: str) -> int:
    result = sum(values)
    if result > MAX_PLAN_INTEGER:
        raise InvalidInputError("PREFLIGHT_OVERFLOW", path, "Resource estimate exceeds 64-bit range.")
    return result


def _runtime_product(orders: int, seconds_per_order: float, path: str) -> float:
    try:
        result = orders * seconds_per_order
    except OverflowError as exc:
        raise InvalidInputError(
            "PREFLIGHT_OVERFLOW", path, "Runtime estimate is outside finite range."
        ) from exc
    if not math.isfinite(result):
        raise InvalidInputError("PREFLIGHT_OVERFLOW", path, "Runtime estimate is outside finite range.")
    return result


def _workload(request: dict) -> dict:
    required = {
        "contract", "solver_model_id", "solver_model_version", "gap_count",
        "points_per_gap", "harmonic_order", "quadrature_order", "bessel_argument_max",
        "point_chunk_size",
    }
    if type(request) is not dict or set(request) != required:
        raise InvalidInputError(
            "PREFLIGHT_WORKLOAD", "/", "Workload must contain exactly the documented fields."
        )
    if request["contract"] != WORKLOAD_CONTRACT:
        raise InvalidInputError("PREFLIGHT_CONTRACT", "/contract", "Unsupported workload contract.")
    if type(request["solver_model_id"]) is not str or not request["solver_model_id"]:
        raise InvalidInputError("PREFLIGHT_MODEL", "/solver_model_id", "Model ID is required.")
    if type(request["solver_model_version"]) is not str or not request["solver_model_version"]:
        raise InvalidInputError("PREFLIGHT_MODEL", "/solver_model_version", "Model version is required.")
    gap_count = _positive_integer(request["gap_count"], "/gap_count")
    points_per_gap = _positive_integer(request["points_per_gap"], "/points_per_gap")
    harmonic_order = _positive_integer(request["harmonic_order"], "/harmonic_order", minimum=0)
    quadrature_order = _positive_integer(request["quadrature_order"], "/quadrature_order")
    if quadrature_order > MAX_QUADRATURE_ORDER:
        raise InvalidInputError(
            "PREFLIGHT_QUADRATURE", "/quadrature_order",
            f"Quadrature order must not exceed {MAX_QUADRATURE_ORDER}.",
        )
    bessel_argument_max = _positive_finite(request["bessel_argument_max"], "/bessel_argument_max")
    bessel_margin = max(32, int(math.sqrt(40 * (harmonic_order + 1))))
    bessel_start = max(harmonic_order + 1 + bessel_margin, math.ceil(bessel_argument_max) + bessel_margin)
    if bessel_start > MAX_BESSEL_START:
        raise InvalidInputError(
            "PREFLIGHT_BESSEL_WORK", "/bessel_argument_max",
            f"Derived Bessel recurrence workspace exceeds {MAX_BESSEL_START}.",
        )
    chunk_size = _positive_integer(request["point_chunk_size"], "/point_chunk_size")
    if chunk_size > min(points_per_gap, MAX_POINT_CHUNK):
        raise InvalidInputError(
            "PREFLIGHT_CHUNK", "/point_chunk_size",
            f"Chunk size must be between 1 and {min(points_per_gap, MAX_POINT_CHUNK)}.",
        )
    return {
        "solver_model_id": request["solver_model_id"],
        "solver_model_version": request["solver_model_version"],
        "gap_count": gap_count,
        "points_per_gap": points_per_gap,
        "harmonic_order": harmonic_order,
        "quadrature_order": quadrature_order,
        "bessel_argument_max": bessel_argument_max,
        "bessel_start": bessel_start,
        "point_chunk_size": chunk_size,
    }


def _calibration(record: dict | None, workload: dict, digest: str | None) -> dict | None:
    if record is None:
        return None
    required = {
        "contract", "solver_model_id", "solver_model_version", "source_revision",
        "environment_sha256", "quadrature_order", "bessel_argument_max",
        "coefficient_seconds_per_order", "field_seconds_per_order",
        "safety_multiplier",
    }
    if type(record) is not dict or set(record) != required:
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION", "/calibration",
            "Calibration must contain exactly the documented fields.",
        )
    if record["contract"] != CALIBRATION_CONTRACT:
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION", "/calibration/contract", "Unsupported calibration contract."
        )
    if (record["solver_model_id"], record["solver_model_version"]) != (
        workload["solver_model_id"], workload["solver_model_version"]
    ):
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION_MODEL", "/calibration/solver_model_id",
            "Calibration does not match the requested solver model and version.",
        )
    quadrature_order = _positive_integer(record["quadrature_order"], "/calibration/quadrature_order")
    if quadrature_order > MAX_QUADRATURE_ORDER or quadrature_order != workload["quadrature_order"]:
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION_DIMENSION", "/calibration/quadrature_order",
            "Calibration quadrature order must match the workload and supported range.",
        )
    bessel_argument_max = _positive_finite(
        record["bessel_argument_max"], "/calibration/bessel_argument_max"
    )
    if bessel_argument_max != workload["bessel_argument_max"]:
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION_DIMENSION", "/calibration/bessel_argument_max",
            "Calibration maximum Bessel argument must match the workload.",
        )
    if type(record["source_revision"]) is not str or not SOURCE_REVISION.fullmatch(
        record["source_revision"]
    ):
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION_ID", "/calibration/source_revision",
            "Expected a full 40-character source revision.",
        )
    for name in ("environment_sha256",):
        if type(record[name]) is not str or not SHA256.fullmatch(record[name]):
            raise InvalidInputError(
                "PREFLIGHT_CALIBRATION_ID", f"/calibration/{name}", "Expected a SHA-256 digest."
            )
    if type(digest) is not str or not SHA256.fullmatch(digest):
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION_ID", "/calibration/sha256",
            "Calibration file must be bound by its SHA-256 digest.",
        )
    coefficient_rate = _positive_finite(
        record["coefficient_seconds_per_order"], "/calibration/coefficient_seconds_per_order"
    )
    field_rate = _positive_finite(
        record["field_seconds_per_order"], "/calibration/field_seconds_per_order"
    )
    safety_multiplier = _positive_finite(record["safety_multiplier"], "/calibration/safety_multiplier")
    if safety_multiplier < 1:
        raise InvalidInputError(
            "PREFLIGHT_CALIBRATION", "/calibration/safety_multiplier",
            "Safety multiplier must be at least one.",
        )
    return {
        "source_revision": record["source_revision"],
        "environment_sha256": record["environment_sha256"],
        "quadrature_order": quadrature_order,
        "bessel_argument_max": bessel_argument_max,
        "calibration_sha256": digest,
        "coefficient_seconds_per_order": coefficient_rate,
        "field_seconds_per_order": field_rate,
        "safety_multiplier": safety_multiplier,
    }


def _scenario_resources(scenario: dict) -> dict:
    if type(scenario) is not dict or type(scenario.get("resources")) is not dict:
        raise InvalidInputError("PREFLIGHT_SCENARIO", "/resources", "Expected a validated scenario.")
    resources = scenario["resources"]
    try:
        ram = resources["ram_bytes"]
        disk = resources["disk_bytes"]
        wall = resources["wall_time"]["value"]
    except (KeyError, TypeError) as exc:
        raise InvalidInputError(
            "PREFLIGHT_SCENARIO", "/resources", "Scenario resource caps are incomplete."
        ) from exc
    return {
        "ram_bytes": _positive_integer(ram, "/resources/ram_bytes"),
        "disk_bytes": _positive_integer(disk, "/resources/disk_bytes"),
        "wall_time_s": _positive_finite(wall, "/resources/wall_time/value"),
    }


def _order_vector_bytes(order_count: int) -> int:
    pointer_bytes = sys.getsizeof((None,)) - sys.getsizeof(())
    list_header = sys.getsizeof([])
    complex_bytes = sys.getsizeof(0j)
    float_bytes = sys.getsizeof(0.0)
    complex_vector = list_header + order_count * (pointer_bytes + complex_bytes)
    real_vector = list_header + order_count * (pointer_bytes + float_bytes)
    return ORDER_COMPLEX_VECTORS * complex_vector + ORDER_REAL_VECTORS * real_vector


def _quadrature_workspace_bytes(quadrature_order: int) -> int:
    """Budget simultaneous Gauss node/weight lists and returned tuples."""
    pointer_bytes = sys.getsizeof((None,)) - sys.getsizeof(())
    list_header, tuple_header = sys.getsizeof([]), sys.getsizeof(())
    float_bytes = sys.getsizeof(0.0)
    list_vector = list_header + quadrature_order * (pointer_bytes + float_bytes)
    tuple_vector = tuple_header + quadrature_order * (pointer_bytes + float_bytes)
    return 2 * list_vector + 2 * tuple_vector


def _bessel_scratch_bytes(start_order: int) -> int:
    """Budget simultaneous Miller and upward-recurrence float lists."""
    pointer_bytes = sys.getsizeof((None,)) - sys.getsizeof(())
    list_header, float_bytes = sys.getsizeof([]), sys.getsizeof(0.0)
    one_vector = list_header + (start_order + 2) * (pointer_bytes + float_bytes)
    return 2 * one_vector


def _sample_object_bytes(point_count: int) -> int:
    pointer_bytes = sys.getsizeof((None,)) - sys.getsizeof(())
    tuple_header = sys.getsizeof(())
    float_bytes = sys.getsizeof(0.0)
    complex_bytes = sys.getsizeof(0j)
    coordinate_row = tuple_header + 3 * pointer_bytes + 3 * float_bytes
    vector_row = tuple_header + 3 * pointer_bytes + 3 * complex_bytes
    sample = coordinate_row + complex_bytes + 2 * vector_row
    outer = 4 * tuple_header + 4 * point_count * pointer_bytes
    return outer + point_count * sample


def _baseline_rss_bytes() -> int:
    if not sys.platform.startswith("linux"):
        raise InvalidInputError(
            "PREFLIGHT_PLATFORM", "/environment/platform",
            "NUM-02 RSS estimate currently supports the Linux ENV-1.0 profile only.",
        )
    peak_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return _checked_product(int(peak_kib), 1024, path="/ram_bytes/baseline")


def _available_ram_bytes() -> int:
    if not sys.platform.startswith("linux"):
        raise InvalidInputError(
            "PREFLIGHT_PLATFORM", "/environment/platform",
            "Available-memory estimate currently supports Linux ENV-1.0 only.",
        )
    try:
        maximum_text = Path("/sys/fs/cgroup/memory.max").read_text().strip()
        current = int(Path("/sys/fs/cgroup/memory.current").read_text().strip())
        if maximum_text != "max":
            maximum = int(maximum_text)
            if maximum > 0 and current >= 0:
                return max(0, maximum - current)
    except (OSError, ValueError):
        pass
    pages = int(os.sysconf("SC_AVPHYS_PAGES"))
    page_size = int(os.sysconf("SC_PAGE_SIZE"))
    return _checked_product(pages, page_size, path="/available_ram_bytes")


def _available_disk_bytes(output_dir: str | Path | None) -> int:
    path = Path.cwd() if output_dir is None else Path(output_dir)
    while not path.exists() and path != path.parent:
        path = path.parent
    if not path.is_dir():
        raise InvalidInputError(
            "PREFLIGHT_OUTPUT_PATH", "/output_dir", "Output location must resolve to a directory."
        )
    return int(shutil.disk_usage(path).free)


def estimate_air_series(
    scenario: dict,
    request: dict,
    calibration: dict | None = None,
    *,
    calibration_sha256: str | None = None,
    baseline_rss_bytes: int | None = None,
    available_ram_bytes: int | None = None,
    available_disk_bytes: int | None = None,
    output_dir: str | Path | None = None,
    current_source_revision: str | None = None,
    current_environment_sha256: str | None = None,
) -> dict:
    """Estimate a chunked Hasegawa workload; never imports or calls a field solver."""
    workload = _workload(request)
    limits = _scenario_resources(scenario)
    profile = _calibration(calibration, workload, calibration_sha256)
    calibration_matches = profile is not None and (
        profile["source_revision"] == current_source_revision
        and profile["environment_sha256"] == current_environment_sha256
    )
    gaps = workload["gap_count"]
    points_per_gap = workload["points_per_gap"]
    order_count = _checked_sum(workload["harmonic_order"], 1, path="/order_count")
    chunk_size = workload["point_chunk_size"]
    chunks_per_gap = (points_per_gap + chunk_size - 1) // chunk_size
    total_points = _checked_product(gaps, points_per_gap, path="/field_points")
    total_chunks = _checked_product(gaps, chunks_per_gap, path="/chunks")
    coefficient_orders = _checked_product(
        order_count, _checked_sum(gaps, 1, path="/coefficient_orders"),
        path="/coefficient_orders",
    )
    field_orders = _checked_product(order_count, total_points, path="/field_orders")

    baseline = _baseline_rss_bytes() if baseline_rss_bytes is None else _positive_integer(
        baseline_rss_bytes, "/ram_bytes/baseline", minimum=0
    )
    ram_available = _available_ram_bytes() if available_ram_bytes is None else _positive_integer(
        available_ram_bytes, "/ram_bytes/available", minimum=0
    )
    disk_available = _available_disk_bytes(output_dir) if available_disk_bytes is None else (
        _positive_integer(available_disk_bytes, "/disk_bytes/available", minimum=0)
    )
    order_workspace = _order_vector_bytes(order_count)
    quadrature_workspace = _quadrature_workspace_bytes(workload["quadrature_order"])
    bessel_scratch = _bessel_scratch_bytes(workload["bessel_start"])
    chunk_objects = _sample_object_bytes(chunk_size)
    chunk_serialization = _checked_product(
        chunk_size, SERIALIZED_BYTES_PER_POINT, path="/serialization_bytes"
    )
    incremental = _checked_sum(
        order_workspace, quadrature_workspace, bessel_scratch, chunk_objects, chunk_serialization,
        SERIALIZATION_FIXED_BYTES,
        path="/ram_bytes/incremental",
    )
    ram_headroom = _checked_product(
        RAM_HEADROOM_FACTOR, incremental, path="/ram_bytes/headroom"
    )
    estimated_ram = _checked_sum(
        _checked_product(2, baseline, path="/ram_bytes/baseline"),
        ram_headroom,
        path="/ram_bytes",
    )
    estimated_disk = _checked_sum(
        _checked_product(total_points, SERIALIZED_BYTES_PER_POINT, path="/disk_bytes/fields"),
        _checked_product(total_chunks, 4096, path="/disk_bytes/chunk_metadata"),
        4096,
        path="/disk_bytes",
    )

    estimated_wall = None
    if calibration_matches:
        assert profile is not None
        coefficient_s = _runtime_product(
            coefficient_orders, profile["coefficient_seconds_per_order"], "/wall_time_s/coefficient"
        )
        field_s = _runtime_product(
            field_orders, profile["field_seconds_per_order"], "/wall_time_s/field"
        )
        estimated_wall = _runtime_product(
            1, coefficient_s + field_s, "/wall_time_s/total"
        ) * profile["safety_multiplier"]
        if not math.isfinite(estimated_wall):
            raise InvalidInputError(
                "PREFLIGHT_OVERFLOW", "/wall_time_s", "Runtime estimate is outside finite range."
            )

    estimates = {
        "ram_bytes": estimated_ram,
        "disk_bytes": estimated_disk,
        "wall_time_s": estimated_wall,
    }
    violations = []
    if estimated_ram > limits["ram_bytes"]:
        violations.append("RAM_SCENARIO_CAP")
    if ram_headroom > ram_available:
        violations.append("RAM_CURRENTLY_AVAILABLE")
    if estimated_disk > limits["disk_bytes"]:
        violations.append("DISK_SCENARIO_CAP")
    if estimated_disk > disk_available:
        violations.append("DISK_CURRENTLY_AVAILABLE")
    if estimated_wall is not None and estimated_wall > limits["wall_time_s"]:
        violations.append("WALL_TIME_SCENARIO_CAP")
    if violations:
        status = "REJECTED"
        reason = "RESOURCE_BUDGET_EXCEEDED"
        exit_code = 1
    elif profile is None:
        status = "INDETERMINATE"
        reason = "RUNTIME_CALIBRATION_REQUIRED"
        exit_code = 3
    elif not calibration_matches:
        status = "INDETERMINATE"
        reason = "CALIBRATION_CONTEXT_MISMATCH"
        exit_code = 3
    else:
        status = "BUDGETS_WITHIN_CAPS"
        reason = None
        exit_code = 0

    return {
        "contract": "AIR-SERIES-PREFLIGHT-1.1",
        "solver_model_id": workload["solver_model_id"],
        "solver_model_version": workload["solver_model_version"],
        "status": status,
        "reason": reason,
        "violations": violations,
        "exit_code": exit_code,
        "execution_authorized": False,
        "dimensions": {
            "gap_count": gaps,
            "points_per_gap": points_per_gap,
            "total_points": total_points,
            "harmonic_order": workload["harmonic_order"],
            "quadrature_order": workload["quadrature_order"],
            "bessel_argument_max": workload["bessel_argument_max"],
            "bessel_start": workload["bessel_start"],
            "order_count": order_count,
            "point_chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "coefficient_order_updates": coefficient_orders,
            "field_order_updates": field_orders,
        },
        "estimates": estimates,
        "components": {
            "baseline_peak_rss_bytes": baseline,
            "incremental_ram_bytes": ram_headroom,
            "order_workspace_bytes": order_workspace,
            "quadrature_workspace_bytes": quadrature_workspace,
            "bessel_recurrence_scratch_bytes": bessel_scratch,
            "chunk_field_objects_bytes": chunk_objects,
            "chunk_serialization_bytes": chunk_serialization,
            "serialization_fixed_bytes": SERIALIZATION_FIXED_BYTES,
            "ram_headroom_factor": RAM_HEADROOM_FACTOR,
            "disk_bytes_per_point": SERIALIZED_BYTES_PER_POINT,
        },
        "limits": limits,
        "available": {"ram_bytes": ram_available, "disk_bytes": disk_available},
        "headroom": {
            "ram_bytes": limits["ram_bytes"] - estimated_ram,
            "disk_bytes": limits["disk_bytes"] - estimated_disk,
            "wall_time_s": (
                None if estimated_wall is None else limits["wall_time_s"] - estimated_wall
            ),
        },
        "calibration": profile,
        "calibration_context_match": calibration_matches,
        "basis": (
            "NUM-01 single-order recurrence and incident-plus-scattered order sum; coefficient-time "
            "calibration is bound to the declared Gauss-Legendre order. O(N) retained vectors plus "
            "explicit node/weight workspace, sequential chunks, platform-measured CPython object "
            "sizes, 2x RAM headroom. "
            "Runtime calibration is accepted only for an exact clean source revision and ENV-1.0 "
            "environment digest. Runtime is not a hard deadline; this report never launches a solver."
        ),
        "alternatives": [
            "Declare a smaller pre-registered point/gap subproblem without dropping required cases.",
            "Increase a resource cap only after reviewing the measured environment and preserving the same physics.",
        ],
    }


def require_ready(report: dict) -> None:
    """Require a finite resource estimate; this does not authorize solver execution."""
    if report.get("status") == "INDETERMINATE":
        raise IncompleteEvidenceError(
            "PREFLIGHT_CALIBRATION", "/calibration",
            "A matching measured runtime calibration is required before execution.",
        )
    if report.get("status") != "BUDGETS_WITHIN_CAPS":
        raise InvalidInputError(
            "PREFLIGHT_RESOURCE", "/resources", "Requested solver workload exceeds declared caps."
        )
