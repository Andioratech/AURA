"""Numerical primitives for the bounded Hasegawa exterior-field backend.

This module does not yet evaluate the coupled piston/sphere field. Its routines
provide binary64 spherical Bessel values and derivatives for that implementation.
"""

from __future__ import annotations

import math

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

    # Miller's start must exceed both the requested order and the oscillatory region.
    margin = max(32, int(math.sqrt(40 * (order + 1))))
    start = max(order + margin, math.ceil(x) + margin)
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
    jn = _finite(values[order] * scale, "/j_n")

    y0 = -math.cos(x) / x
    y1 = -math.cos(x) / (x * x) - math.sin(x) / x
    if order == 0:
        yn = y0
    elif order == 1:
        yn = y1
    else:
        previous, current = y0, y1
        for n in range(1, order):
            previous, current = current, ((2 * n + 1) / x) * current - previous
            _finite(current, "/y_n")
        yn = current

    if order == 0:
        j_next = j1
        y_next = y1
    else:
        j_previous = _finite(values[order - 1] * scale, "/j_n_minus_1")
        j_next = ((2 * order + 1) / x) * jn - j_previous
        y_previous = y0 if order == 1 else _spherical_y(order - 1, x, y0, y1)
        y_next = ((2 * order + 1) / x) * yn - y_previous
    j_derivative = _finite((order / x) * jn - j_next, "/j_derivative")
    y_derivative = _finite((order / x) * yn - y_next, "/y_derivative")
    return jn, _finite(yn, "/y_n"), j_derivative, y_derivative


def _spherical_y(order: int, x: float, y0: float, y1: float) -> float:
    """Return an already representable ``y_order`` by upward recurrence."""
    if order == 0:
        return y0
    previous, current = y0, y1
    for n in range(1, order):
        previous, current = current, ((2 * n + 1) / x) * current - previous
        _finite(current, "/y_n")
    return current


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
