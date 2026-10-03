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
    denom = values[0] * values[0] + values[1] * values[1]
    if denom == 0 or not math.isfinite(denom):
        raise NumericalDomainError("BESSEL_NORMALIZATION", "/x", "Miller normalization failed.")
    scale = (values[0] * j0 + values[1] * j1) / denom
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
