"""Exact-axisymmetric geometry and quadrature data for boundary integration."""

from __future__ import annotations

import math

from aura.errors import InvalidInputError, NumericalDomainError

MAX_BEM_MERIDIAN_NODES = 65_536


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
