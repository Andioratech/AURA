"""Numerical primitives for the bounded Hasegawa exterior-field backend.

This module does not yet evaluate the coupled piston/sphere field. Its routines
provide binary64 spherical Bessel values and derivatives for that implementation.
"""

from __future__ import annotations

import math
import sys

from aura.errors import InvalidInputError, NumericalDomainError


def _finite(value: float, path: str) -> float:
    if not math.isfinite(value):
        raise NumericalDomainError(
            "NUMERIC_RANGE", path, "Spherical Bessel recurrence is not representable in binary64."
        )
    return value


def spherical_bessel_jy(order: int, x: float) -> tuple[float, float, float, float]:
    """Return ``j_n, y_n, j'_n, y'_n`` for real ``x > 0``.

    ``j_n`` uses a downward Miller recurrence normalized by the analytic
    ``j_0``/``j_1`` pair. ``y_n`` uses its stable upward recurrence. No external
    numerical package or silent precision fallback is used.
    """
    if type(order) is not int or order < 0:
        raise InvalidInputError("BESSEL_ORDER", "/order", "Expected a nonnegative integer order.")
    if type(x) not in (int, float) or type(x) is bool or not math.isfinite(x) or x <= 0:
        raise InvalidInputError("BESSEL_ARGUMENT", "/x", "Expected a finite positive argument.")
    x = float(x)
    if order > 4096:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/order", "Order exceeds the bounded recurrence limit.")

    return tuple(component[order] for component in _spherical_sequences(order, float(x)))


def _spherical_sequences(
    max_order: int, x: float
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    """Build the four real sequences once for a shared argument."""
    # Miller's start must exceed both the requested order and the oscillatory region.
    margin = max(32, int(math.sqrt(40 * (max_order + 1))))
    start = max(max_order + 1 + margin, math.ceil(x) + margin)
    if start > 8192:
        raise InvalidInputError(
            "BESSEL_WORK_RANGE", "/x", "The bounded Miller recurrence workspace would be exceeded."
        )
    values = [0.0] * (start + 2)
    values[start] = 1.0
    for n in range(start, 0, -1):
        if max(abs(values[n]), abs(values[n + 1])) > 1e200:
            for index in range(n, start + 2):
                values[index] *= 1e-200
        values[n - 1] = ((2 * n + 1) / x) * values[n] - values[n + 1]
        _finite(values[n - 1], "/j_recurrence")

    j0 = math.sin(x) / x
    j1 = math.sin(x) / (x * x) - math.cos(x) / x
    norm = max(abs(values[0]), abs(values[1]))
    if norm == 0 or not math.isfinite(norm):
        raise NumericalDomainError("BESSEL_NORMALIZATION", "/x", "Miller normalization failed.")
    normalized_zero, normalized_one = values[0] / norm, values[1] / norm
    denom = normalized_zero * normalized_zero + normalized_one * normalized_one
    scale = (
        (normalized_zero * j0 + normalized_one * j1) / denom
    ) / norm
    _finite(scale, "/j_normalization")
    y0 = -math.cos(x) / x
    y1 = -math.cos(x) / (x * x) - math.sin(x) / x
    y_values = [y0, y1]
    for n in range(1, max_order + 1):
        next_value = ((2 * n + 1) / x) * y_values[n] - y_values[n - 1]
        y_values.append(_finite(next_value, "/y_n"))

    j_values = tuple(_finite(values[n] * scale, f"/j_{n}") for n in range(max_order + 2))
    j_derivatives = tuple(
        _finite((n / x) * j_values[n] - j_values[n + 1], f"/j_{n}_derivative")
        for n in range(max_order + 1)
    )
    y_derivatives = tuple(
        _finite((n / x) * y_values[n] - y_values[n + 1], f"/y_{n}_derivative")
        for n in range(max_order + 1)
    )
    return (
        j_values[: max_order + 1],
        tuple(y_values[: max_order + 1]),
        j_derivatives,
        y_derivatives,
    )


def spherical_legendre(order: int, cosine: float) -> tuple[float, float]:
    """Return ``P_n(mu)`` and ``dP_n/dmu`` using the three-term recurrence."""
    if type(order) is not int or order < 0:
        raise InvalidInputError("LEGENDRE_ORDER", "/order", "Expected a nonnegative integer order.")
    if type(cosine) not in (int, float) or type(cosine) is bool or not math.isfinite(cosine):
        raise InvalidInputError("LEGENDRE_ARGUMENT", "/cosine", "Expected a finite scalar.")
    if not -1 <= cosine <= 1:
        raise InvalidInputError("LEGENDRE_DOMAIN", "/cosine", "Expected a value in [-1, 1].")
    if order == 0:
        return 1.0, 0.0
    p0, p1 = 1.0, float(cosine)
    d0, d1 = 0.0, 1.0
    for n in range(1, order):
        factor = 2 * n + 1
        p_next = _finite((factor * cosine * p1 - n * p0) / (n + 1), "/P_n")
        d_next = _finite(
            (factor * (p1 + cosine * d1) - n * d0) / (n + 1), "/dP_n"
        )
        p0, p1 = p1, p_next
        d0, d1 = d1, d_next
    return p1, d1


def gauss_legendre_rule(order: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return symmetric Gauss-Legendre nodes and weights on ``[-1, 1]``."""
    if type(order) is not int or not 1 <= order <= 512:
        raise InvalidInputError("QUADRATURE_ORDER", "/order", "Expected an order from 1 through 512.")
    nodes = [0.0] * order
    weights = [0.0] * order
    for index in range((order + 1) // 2):
        root = math.cos(math.pi * (index + 0.75) / (order + 0.5))
        for _ in range(100):
            polynomial, derivative = spherical_legendre(order, root)
            correction = polynomial / derivative
            root -= correction
            if abs(correction) <= 4 * sys.float_info.epsilon * max(1.0, abs(root)):
                break
        else:
            raise NumericalDomainError(
                "QUADRATURE_ROOT", f"/nodes/{index}", "Legendre root iteration did not converge."
            )
        _, derivative = spherical_legendre(order, root)
        weight = 2 / ((1 - root * root) * derivative * derivative)
        if not math.isfinite(root) or not math.isfinite(weight) or weight <= 0:
            raise NumericalDomainError(
                "QUADRATURE_RANGE", f"/nodes/{index}", "Quadrature node or weight is invalid."
            )
        mirror = order - 1 - index
        nodes[index], nodes[mirror] = -root, root
        weights[index] = weights[mirror] = weight
    return tuple(nodes), tuple(weights)


def stationary_sphere_coefficient(order: int, ka: float) -> complex:
    """Return the stationary sound-hard outgoing coefficient ``-j'_n/h'_n``."""
    _, _, j_derivative, y_derivative = spherical_bessel_jy(order, ka)
    denominator = complex(j_derivative, y_derivative)
    if math.hypot(j_derivative, y_derivative) == 0:
        raise NumericalDomainError(
            "SPHERE_COEFFICIENT", "/ka", "Outgoing Hankel derivative is zero."
        )
    try:
        result = complex(-j_derivative, 0.0) / denominator
    except ZeroDivisionError as exc:
        raise NumericalDomainError(
            "SPHERE_COEFFICIENT", "/ka", "Outgoing Hankel derivative is zero."
        ) from exc
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError(
            "SPHERE_COEFFICIENT", "/ka", "Scattering coefficient is not finite."
        )
    return result


def source_diffraction_coefficients(
    max_order: int,
    *,
    wave_number_rad_m: float,
    sphere_center_distance_m: float,
    piston_radius_m: float,
    quadrature_order: int,
    workspace_bytes: int,
) -> tuple[complex, ...]:
    """Integrate Hasegawa's piston diffraction factors ``f_n`` with ``h_n^(1)``.

    This returns source factors only. A caller must resource-preflight the full
    field workload before invoking it; ``workspace_bytes`` provides an additional
    local allocation guard and is not a substitute for that preflight.
    The integral is the conjugate of Hasegawa et al. (1985), Eq. 2, for the
    project ``exp(-iwt)`` convention.
    """
    if type(max_order) is not int or max_order < 0 or max_order > 4096:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/max_order", "Expected an order from 0 through 4096.")
    for name, value in (
        ("wave_number_rad_m", wave_number_rad_m),
        ("sphere_center_distance_m", sphere_center_distance_m),
        ("piston_radius_m", piston_radius_m),
    ):
        if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value) or value <= 0:
            raise InvalidInputError("SOURCE_GEOMETRY", f"/{name}", "Expected a finite positive value.")
    if type(quadrature_order) is not int or not 1 <= quadrature_order <= 512:
        raise InvalidInputError("QUADRATURE_ORDER", "/quadrature_order", "Expected an order from 1 through 512.")
    if type(workspace_bytes) is not int or workspace_bytes < 0:
        raise InvalidInputError("FIELD_RESOURCE", "/workspace_bytes", "Expected a nonnegative byte cap.")

    k, r0, radius = float(wave_number_rad_m), float(sphere_center_distance_m), float(piston_radius_m)
    r1 = math.hypot(r0, radius)
    lower, upper = _finite(k * r0, "/kr0"), _finite(k * r1, "/kr1")
    width = _finite(upper - lower, "/integration_width")
    if width <= 0:
        raise NumericalDomainError(
            "SOURCE_INTEGRATION_RANGE", "/piston_radius_m", "The integration interval is not representable."
        )
    margin = max(32, int(math.sqrt(40 * (max_order + 1))))
    bessel_start = max(max_order + 1 + margin, math.ceil(upper) + margin)
    if bessel_start > 8192:
        raise InvalidInputError(
            "BESSEL_WORK_RANGE", "/wave_number_rad_m",
            "The bounded Miller recurrence workspace would be exceeded.",
        )
    estimated = _source_workspace_estimate(max_order + 1, quadrature_order, bessel_start)
    if workspace_bytes < estimated:
        raise InvalidInputError(
            "FIELD_RESOURCE", "/workspace_bytes",
            f"Need at least {estimated} bytes for source coefficients; received {workspace_bytes}.",
        )

    nodes, weights = gauss_legendre_rule(quadrature_order)
    midpoint, half_width = lower + width / 2, width / 2
    coefficients = [0j] * (max_order + 1)
    corrections = [0j] * (max_order + 1)
    for node, weight in zip(nodes, weights, strict=True):
        argument = _finite(midpoint + half_width * node, "/quadrature_argument")
        j_values, y_values, _, _ = _spherical_sequences(max_order, argument)
        cosine = lower / argument
        legendre_previous, legendre_current = 1.0, cosine
        quadrature_scale = half_width * weight * argument
        for order in range(max_order + 1):
            if order == 0:
                polynomial = legendre_previous
            elif order == 1:
                polynomial = legendre_current
            else:
                next_value = (
                    (2 * order - 1) * cosine * legendre_current
                    - (order - 1) * legendre_previous
                ) / order
                legendre_previous, legendre_current = legendre_current, _finite(
                    next_value, "/source_legendre"
                )
                polynomial = legendre_current
            contribution = quadrature_scale * complex(j_values[order], y_values[order]) * polynomial
            adjusted = contribution - corrections[order]
            updated = coefficients[order] + adjusted
            corrections[order] = (updated - coefficients[order]) - adjusted
            coefficients[order] = complex(
                _finite(updated.real, f"/f_{order}/real"),
                _finite(updated.imag, f"/f_{order}/imag"),
            )
    return tuple(coefficients)


def _source_workspace_estimate(order_count: int, quadrature_order: int, bessel_start: int) -> int:
    """Conservative local Python-object estimate; NUM-02 adds process headroom."""
    pointer_bytes = sys.getsizeof((None,)) - sys.getsizeof(())
    list_header, tuple_header = sys.getsizeof([]), sys.getsizeof(())
    float_bytes, complex_bytes = sys.getsizeof(0.0), sys.getsizeof(0j)

    def list_bytes(count: int, item_bytes: int) -> int:
        return list_header + count * (pointer_bytes + item_bytes)

    def tuple_bytes(count: int, item_bytes: int) -> int:
        return tuple_header + count * (pointer_bytes + item_bytes)

    # Includes two recurrence work vectors, returned/copy Bessel vectors, two
    # compensated complex sums, the returned coefficient tuple, and rule vectors.
    return (
        4096
        + 2 * list_bytes(bessel_start + 2, float_bytes)
        + 2 * list_bytes(quadrature_order, float_bytes)
        + 5 * tuple_bytes(order_count + 1, float_bytes)
        + 2 * list_bytes(order_count, complex_bytes)
        + tuple_bytes(order_count, complex_bytes)
        + 2 * tuple_bytes(quadrature_order, float_bytes)
    )
