"""Exact-axisymmetric geometry and quadrature data for boundary integration."""

from __future__ import annotations

import math

from aura.errors import InvalidInputError, NumericalDomainError

MAX_BEM_MERIDIAN_NODES = 65_536
MAX_BEM_RESOURCE_BYTES = (1 << 63) - 1
BEM_COMPLEX_ELEMENT_BYTES = 64
BEM_DENSE_OPERATOR_ARRAYS = 4
BEM_SOLVER_VECTOR_COUNT = 21
BEM_FIXED_WORKSPACE_BYTES = 65_536
BEM_RAM_HEADROOM_FACTOR = 2


def sphere_meridian_quadrature(
    radius_m: float,
    *,
    panels: int,
    order_per_panel: int,
) -> tuple[tuple[float, float], ...]:
    """Return composite Gauss nodes and meridian surface weights for a sphere.

    Each pair is ``(theta, weight)`` with ``theta`` in ``[0, pi]`` and the
    weight equal to ``a**2 * sin(theta) * dtheta`` in square metres. The
    azimuthal integral is deliberately excluded: a zero-mode ring kernel
    already integrates over source azimuth. Panel edges and nodes describe
    the exact sphere parameterization and do not approximate it with facets.

    This is geometry quadrature only. It neither chooses a boundary unknown
    basis nor assembles or solves an integral equation.
    """
    if (type(radius_m) not in (int, float) or type(radius_m) is bool
            or not math.isfinite(radius_m) or radius_m <= 0.0):
        raise InvalidInputError("BEM_SPHERE_RADIUS", "/radius_m", "Expected a finite positive radius in metres.")
    if type(panels) is not int or not 1 <= panels <= MAX_BEM_MERIDIAN_NODES:
        raise InvalidInputError(
            "BEM_MERIDIAN_PANELS", "/panels", "Expected a positive bounded panel count."
        )
    if type(order_per_panel) is not int or not 1 <= order_per_panel <= 512:
        raise InvalidInputError(
            "BEM_MERIDIAN_ORDER", "/order_per_panel", "Expected Gauss order from 1 through 512."
        )
    node_count = panels * order_per_panel
    if node_count > MAX_BEM_MERIDIAN_NODES:
        raise InvalidInputError(
            "BEM_MERIDIAN_WORK", "/order_per_panel",
            f"Composite rule exceeds {MAX_BEM_MERIDIAN_NODES} nodes.",
        )

    radius_squared = float(radius_m) * float(radius_m)
    if not math.isfinite(radius_squared) or radius_squared == 0.0:
        raise NumericalDomainError(
            "BEM_MERIDIAN_RANGE", "/radius_m", "Squared sphere radius is outside binary64 range."
        )

    from aura.fields.numerical import gauss_legendre_rule

    nodes, weights = gauss_legendre_rule(order_per_panel)
    result: list[tuple[float, float]] = []
    for panel_index in range(panels):
        left = math.pi * panel_index / panels
        right = math.pi * (panel_index + 1) / panels
        midpoint = 0.5 * (left + right)
        half_width = 0.5 * (right - left)
        for node, weight in zip(nodes, weights, strict=True):
            theta = midpoint + half_width * node
            surface_weight = radius_squared * math.sin(theta) * half_width * weight
            if not math.isfinite(surface_weight) or surface_weight <= 0.0:
                raise NumericalDomainError(
                    "BEM_MERIDIAN_RANGE", "/radius_m",
                    "Sphere surface weight is outside positive binary64 range.",
                )
            result.append((theta, surface_weight))
    return tuple(result)


def estimate_bem_dense_workspace(
    *,
    panels: int,
    order_per_panel: int,
    ram_cap_bytes: int,
    available_ram_bytes: int,
) -> dict[str, int | str | bool | None]:
    """Estimate candidate dense-BEM workspace without allocating solver data.

    The estimate reserves four complex dense arrays, 21 complex solver vectors,
    fixed workspace, and a RAM headroom multiplier. It is a planning contract,
    not a runtime calibration or authorization to assemble a matrix.
    """
    if type(panels) is not int or not 1 <= panels <= MAX_BEM_MERIDIAN_NODES:
        raise InvalidInputError(
            "BEM_MERIDIAN_PANELS", "/panels", "Expected a positive bounded panel count."
        )
    if type(order_per_panel) is not int or not 1 <= order_per_panel <= 512:
        raise InvalidInputError(
            "BEM_MERIDIAN_ORDER", "/order_per_panel", "Expected Gauss order from 1 through 512."
        )
    if type(ram_cap_bytes) is not int or not 0 <= ram_cap_bytes <= MAX_BEM_RESOURCE_BYTES:
        raise InvalidInputError(
            "BEM_RESOURCE_CAP", "/ram_cap_bytes", "Expected a bounded nonnegative RAM cap."
        )
    if type(available_ram_bytes) is not int or not 0 <= available_ram_bytes <= MAX_BEM_RESOURCE_BYTES:
        raise InvalidInputError(
            "BEM_RESOURCE_AVAILABLE", "/available_ram_bytes",
            "Expected a bounded nonnegative available-RAM value.",
        )

    nodes = panels * order_per_panel
    if nodes > MAX_BEM_MERIDIAN_NODES:
        raise InvalidInputError(
            "BEM_MERIDIAN_WORK", "/order_per_panel",
            f"Composite rule exceeds {MAX_BEM_MERIDIAN_NODES} nodes.",
        )
    pairs = nodes * nodes
    operator_entries = BEM_DENSE_OPERATOR_ARRAYS * pairs
    raw_bytes = (
        operator_entries * BEM_COMPLEX_ELEMENT_BYTES
        + BEM_SOLVER_VECTOR_COUNT * nodes * BEM_COMPLEX_ELEMENT_BYTES
        + BEM_FIXED_WORKSPACE_BYTES
    )
    estimated_ram = BEM_RAM_HEADROOM_FACTOR * raw_bytes
    if estimated_ram > MAX_BEM_RESOURCE_BYTES:
        raise InvalidInputError(
            "BEM_RESOURCE_RANGE", "/panels", "BEM workspace estimate exceeds the supported integer range."
        )

    limiting_cap = min(ram_cap_bytes, available_ram_bytes)
    rejected = estimated_ram > limiting_cap
    return {
        "contract": "BEM-DENSE-WORKSPACE-1.0",
        "status": "REJECTED" if rejected else "INDETERMINATE",
        "reason": "RESOURCE_BUDGET_EXCEEDED" if rejected else "BEM_RUNTIME_UNCALIBRATED",
        "panels": panels,
        "order_per_panel": order_per_panel,
        "node_count": nodes,
        "meridian_pair_count": pairs,
        "operator_entry_count": operator_entries,
        "estimated_ram_bytes": estimated_ram,
        "ram_cap_bytes": ram_cap_bytes,
        "available_ram_bytes": available_ram_bytes,
        "runtime_estimate_seconds": None,
        "execution_authorized": False,
    }
