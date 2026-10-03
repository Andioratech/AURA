"""Numerical primitives for the bounded Hasegawa exterior-field backend.

This module does not yet evaluate the coupled piston/sphere field. Its routines
provide binary64 spherical Bessel values and derivatives for that implementation.
"""

from __future__ import annotations

import cmath
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

    ``j_n`` uses downward Miller recurrence normalized by the analytic
    ``j_0``/``j_1`` pair unless all requested orders are well inside the
    oscillatory region, where upward recurrence is stable. ``y_n`` uses upward
    recurrence. No external numerical package or silent precision fallback is
    used.
    """
    if type(order) is not int or order < 0:
        raise InvalidInputError("BESSEL_ORDER", "/order", "Expected a nonnegative integer order.")
    if type(x) not in (int, float) or type(x) is bool or not math.isfinite(x) or x <= 0:
        raise InvalidInputError("BESSEL_ARGUMENT", "/x", "Expected a finite positive argument.")
    x = float(x)
    if order > 4096:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/order", "Order exceeds the bounded recurrence limit.")
    if x > 8192:
        raise InvalidInputError(
            "BESSEL_WORK_RANGE", "/x", "The bounded Bessel recurrence workspace would be exceeded."
        )

    return tuple(component[order] for component in _spherical_sequences(order, float(x)))


def _spherical_sequences(
    max_order: int, x: float
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    """Build the four real sequences once for a shared argument."""
    j0 = math.sin(x) / x
    j1 = math.sin(x) / (x * x) - math.cos(x) / x
    if x > max_order + 64:
        # Upward recurrence is stable when every requested order is well inside
        # the oscillatory region; it avoids Miller normalization loss at large x.
        j_values = [j0, j1]
        for n in range(1, max_order + 1):
            next_value = ((2 * n + 1) / x) * j_values[n] - j_values[n - 1]
            j_values.append(_finite(next_value, f"/j_{n + 1}"))
    else:
        # Miller's start must exceed both the requested order and the oscillatory region.
        margin = max(32, int(math.sqrt(40 * (max_order + 1))))
        start = max(max_order + 1 + margin, math.ceil(x) + margin)
        if start > 8192:
            raise InvalidInputError(
                "BESSEL_WORK_RANGE", "/x",
                "The bounded Miller recurrence workspace would be exceeded.",
            )
        values = [0.0] * (start + 2)
        values[start] = 1.0
        for n in range(start, 0, -1):
            if max(abs(values[n]), abs(values[n + 1])) > 1e200:
                for index in range(n, start + 2):
                    values[index] *= 1e-200
            values[n - 1] = ((2 * n + 1) / x) * values[n] - values[n + 1]
            _finite(values[n - 1], "/j_recurrence")

        norm = max(abs(values[0]), abs(values[1]))
        if norm == 0 or not math.isfinite(norm):
            raise NumericalDomainError("BESSEL_NORMALIZATION", "/x", "Miller normalization failed.")
        normalized_zero, normalized_one = values[0] / norm, values[1] / norm
        denom = normalized_zero * normalized_zero + normalized_one * normalized_one
        scale = ((normalized_zero * j0 + normalized_one * j1) / denom) / norm
        _finite(scale, "/j_normalization")
        j_values = [_finite(values[n] * scale, f"/j_{n}") for n in range(max_order + 2)]

    y0 = -math.cos(x) / x
    y1 = -math.cos(x) / (x * x) - math.sin(x) / x
    y_values = [y0, y1]
    for n in range(1, max_order + 1):
        next_value = ((2 * n + 1) / x) * y_values[n] - y_values[n - 1]
        y_values.append(_finite(next_value, "/y_n"))

    j_values = tuple(j_values[: max_order + 2])
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


def _scaled_spherical_neumann(max_order: int, x: float) -> tuple[tuple[float, int], ...]:
    """Return ``y_n(x)`` as mantissa/base-2 exponent pairs through ``max_order``.

    It uses the recurrence in NIST DLMF 10.51.1, rescaled as needed to preserve
    each value's scale separately and avoid binary64 overflow:
    https://dlmf.nist.gov/10.51.E1
    """
    if type(max_order) is not int or not 0 <= max_order <= 4096:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/max_order", "Expected an order from 0 through 4096.")
    if type(x) not in (int, float) or type(x) is bool or not math.isfinite(x) or x <= 0:
        raise InvalidInputError("BESSEL_ARGUMENT", "/x", "Expected a finite positive argument.")
    x = float(x)
    if x > 8192:
        raise InvalidInputError(
            "BESSEL_WORK_RANGE", "/x", "The bounded Bessel recurrence workspace would be exceeded."
        )
    y_previous = _finite(-math.cos(x) / x, "/y_0")
    y_current = _finite(-math.cos(x) / (x * x) - math.sin(x) / x, "/y_1")
    initial_scale = max(abs(y_previous), abs(y_current))
    if initial_scale == 0:
        raise NumericalDomainError("BESSEL_NORMALIZATION", "/x", "Neumann scaling failed.")
    exponent = math.frexp(initial_scale)[1]
    y_previous = math.ldexp(y_previous, -exponent)
    y_current = math.ldexp(y_current, -exponent)
    values = [(y_previous, exponent)]
    if max_order == 0:
        return tuple(values)
    values.append((y_current, exponent))

    for order in range(1, max_order):
        factor = _finite((2 * order + 1) / x, "/y_recurrence_factor")
        next_value = _finite(factor * y_current - y_previous, f"/y_{order + 1}")
        pair_scale = max(abs(y_current), abs(next_value))
        if pair_scale and (pair_scale < 2.0**-400 or pair_scale > 2.0**400):
            shift = math.frexp(pair_scale)[1]
            y_current = math.ldexp(y_current, -shift)
            next_value = math.ldexp(next_value, -shift)
            exponent += shift
        values.append((next_value, exponent))
        y_previous, y_current = y_current, next_value
    return tuple(values)


def _scaled_complex(value: complex, exponent: int = 0) -> tuple[complex, int]:
    """Represent a complex value as a bounded mantissa times a power of two."""
    magnitude = max(abs(value.real), abs(value.imag))
    if magnitude == 0:
        return 0j, 0
    if not math.isfinite(magnitude):
        raise NumericalDomainError("NUMERIC_RANGE", "/scaled_value", "Scaled value is not finite.")
    _, shift = math.frexp(magnitude)
    return complex(math.ldexp(value.real, -shift), math.ldexp(value.imag, -shift)), exponent + shift


def _scaled_complex_add(
    left: tuple[complex, int], right: tuple[complex, int]
) -> tuple[complex, int]:
    left_mantissa, left_exponent = left
    right_mantissa, right_exponent = right
    if left_exponent < right_exponent:
        left_mantissa, right_mantissa = right_mantissa, left_mantissa
        left_exponent, right_exponent = right_exponent, left_exponent
    shift = right_exponent - left_exponent
    right_scaled = complex(
        math.ldexp(right_mantissa.real, shift),
        math.ldexp(right_mantissa.imag, shift),
    )
    return _scaled_complex(left_mantissa + right_scaled, left_exponent)


def _scaled_complex_multiply(
    left: tuple[complex, int], right: tuple[complex, int]
) -> tuple[complex, int]:
    return _scaled_complex(left[0] * right[0], left[1] + right[1])


def _scaled_complex_real(
    value: tuple[complex, int], factor: float
) -> tuple[complex, int]:
    if not math.isfinite(factor):
        raise NumericalDomainError("NUMERIC_RANGE", "/scaled_factor", "Scaled factor is not finite.")
    return _scaled_complex(value[0] * factor, value[1])


def _unscale_complex(value: tuple[complex, int], path: str) -> complex:
    try:
        result = complex(
            math.ldexp(value[0].real, value[1]),
            math.ldexp(value[0].imag, value[1]),
        )
    except OverflowError as exc:
        raise NumericalDomainError("NUMERIC_RANGE", path, "Weighted modal term exceeds binary64.") from exc
    return complex(_finite(result.real, path + "/real"), _finite(result.imag, path + "/imag"))


def _regular_bessel_scaled_values(max_order: int, x: float) -> tuple[tuple[complex, int], ...]:
    """Return scaled j_n(x), using direct low orders and a high-order series."""
    if type(max_order) is not int or not 0 <= max_order <= 513:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/max_order", "Expected order from 0 through 513.")
    if type(x) not in (int, float) or type(x) is bool or not math.isfinite(x) or x <= 0:
        raise InvalidInputError("BESSEL_ARGUMENT", "/x", "Expected a finite positive argument.")
    x = float(x)
    if x > 40.0:
        raise InvalidInputError(
            "BESSEL_ARGUMENT_RANGE", "/x", "Scaled regular series is bounded to x <= 40."
        )

    series_start = 0 if x <= 12.0 else max(48, math.ceil(x) + 32)
    direct_max_order = min(max_order, series_start - 1)
    direct_j = _spherical_sequences(direct_max_order, x)[0] if direct_max_order >= 0 else ()
    values = [_scaled_complex(complex(value, 0.0)) for value in direct_j]
    base = _scaled_complex(1 + 0j)
    for order in range(series_start):
        base = _scaled_complex_real(base, x / (2 * order + 3))

    for order in range(series_start, max_order + 1):
        term = total = 1.0
        for index in range(1, 100):
            term *= -(x * x) / (2 * index * (2 * order + 2 * index + 1))
            updated = total + term
            total = updated
            if abs(term) <= 2 * math.ulp(total):
                break
        else:
            raise NumericalDomainError(
                "BESSEL_SERIES", f"/j_{order}", "Scaled regular power series did not converge."
            )
        values.append(_scaled_complex_real(base, total))
        base = _scaled_complex_real(base, x / (2 * order + 3))
    return tuple(values)


def _scaled_source_diffraction_coefficients(
    max_order: int,
    *,
    wave_number_rad_m: float,
    sphere_center_distance_m: float,
    piston_radius_m: float,
) -> tuple[tuple[complex, int], ...]:
    """Return conjugated Hasegawa source factors as mantissa/exponent pairs."""
    if type(max_order) is not int or not 0 <= max_order <= 512:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/max_order", "Expected order from 0 through 512.")
    for name, value in (
        ("wave_number_rad_m", wave_number_rad_m),
        ("sphere_center_distance_m", sphere_center_distance_m),
        ("piston_radius_m", piston_radius_m),
    ):
        if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value) or value <= 0:
            raise InvalidInputError("SOURCE_GEOMETRY", f"/{name}", "Expected a finite positive value.")

    k = float(wave_number_rad_m)
    center_distance = float(sphere_center_distance_m)
    piston_radius = float(piston_radius_m)
    lower_argument = _finite(k * center_distance, "/kr0")
    upper_radius = math.hypot(center_distance, piston_radius)
    upper_argument = _finite(k * upper_radius, "/kr1")
    if lower_argument < 1.0 or upper_argument > 8192:
        raise InvalidInputError(
            "BESSEL_ARGUMENT_RANGE", "/sphere_center_distance_m", "Source arguments are outside the bounded regime."
        )

    lower_h0 = complex(math.sin(lower_argument) / lower_argument, -math.cos(lower_argument) / lower_argument)
    upper_h0 = complex(math.sin(upper_argument) / upper_argument, -math.cos(upper_argument) / upper_argument)
    upper_h1 = complex(
        math.sin(upper_argument) / upper_argument**2 - math.cos(upper_argument) / upper_argument,
        -math.cos(upper_argument) / upper_argument**2 - math.sin(upper_argument) / upper_argument,
    )
    factors = [
        _scaled_complex(cmath.exp(1j * lower_argument) - cmath.exp(1j * upper_argument)),
        _scaled_complex(-lower_argument * (upper_h0 - lower_h0)),
    ]
    legendre_ratio = center_distance / upper_radius
    legendre_previous, legendre_current = 1.0, legendre_ratio
    hankel_previous, hankel_current = _scaled_complex(upper_h0), _scaled_complex(upper_h1)

    for order in range(2, max_order + 1):
        next_legendre = (
            (2 * order - 1) * legendre_ratio * legendre_current
            - (order - 1) * legendre_previous
        ) / order
        legendre_difference = next_legendre - legendre_previous
        factors.append(
            _scaled_complex_add(
                _scaled_complex(-factors[order - 2][0], factors[order - 2][1]),
                _scaled_complex_real(
                    _scaled_complex_multiply(
                        hankel_current,
                        _scaled_complex(complex(legendre_difference, 0.0)),
                    ),
                    -upper_argument,
                ),
            )
        )
        hankel_next = _scaled_complex_add(
            _scaled_complex_real(hankel_current, (2 * order - 1) / upper_argument),
            _scaled_complex(-hankel_previous[0], hankel_previous[1]),
        )
        hankel_previous, hankel_current = hankel_current, hankel_next
        legendre_previous, legendre_current = legendre_current, next_legendre
    return tuple(factors[: max_order + 1])


def _scaled_axial_source_derivative_terms(
    max_order: int,
    *,
    wave_number_rad_m: float,
    sphere_center_distance_m: float,
    piston_radius_m: float,
    sphere_radius_m: float,
    side: str,
) -> tuple[complex, ...]:
    """Return piston-only axial d(Phi)/dz modal terms normalized by piston speed.

    The source factors use the conjugated Hasegawa Eqs. (2)-(4) recurrence and
    remain exponent-scaled; regular j_n and j'_n are combined before conversion
    to binary64. This is a bounded diagnostic for the frozen air ka <= 12 domain,
    not the coupled sphere field evaluator.
    """
    if type(max_order) is not int or not 0 <= max_order <= 512:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/max_order", "Expected order from 0 through 512.")
    if side not in ("front", "rear"):
        raise InvalidInputError("FIELD_SIDE", "/side", "Expected 'front' or 'rear'.")
    for name, value in (
        ("wave_number_rad_m", wave_number_rad_m),
        ("sphere_center_distance_m", sphere_center_distance_m),
        ("piston_radius_m", piston_radius_m),
        ("sphere_radius_m", sphere_radius_m),
    ):
        if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value) or value <= 0:
            raise InvalidInputError("SOURCE_GEOMETRY", f"/{name}", "Expected a finite positive value.")

    k = float(wave_number_rad_m)
    center_distance = float(sphere_center_distance_m)
    piston_radius = float(piston_radius_m)
    sphere_radius = float(sphere_radius_m)
    sphere_argument = k * sphere_radius
    if center_distance <= sphere_radius:
        raise InvalidInputError(
            "SOURCE_GEOMETRY", "/sphere_center_distance_m", "Sphere center must lie beyond its radius."
        )
    if not 1.0 <= sphere_argument <= 12.0:
        raise InvalidInputError(
            "BESSEL_ARGUMENT_RANGE", "/sphere_radius_m", "Scaled axial diagnostic requires 1 <= ka <= 12."
        )
    source_factors = _scaled_source_diffraction_coefficients(
        max_order,
        wave_number_rad_m=k,
        sphere_center_distance_m=center_distance,
        piston_radius_m=piston_radius,
    )

    regular_values = _regular_bessel_scaled_values(max_order + 1, sphere_argument)
    derivative_start = min(max_order, max(48, math.ceil(sphere_argument) + 24))
    _, _, regular_derivatives, _ = _spherical_sequences(derivative_start, sphere_argument)
    terms = []

    for order in range(max_order + 1):
        if order < derivative_start:
            derivative = _scaled_complex(complex(regular_derivatives[order], 0.0))
        else:
            derivative = _scaled_complex_add(
                _scaled_complex_real(regular_values[order], order / sphere_argument),
                _scaled_complex(-regular_values[order + 1][0], regular_values[order + 1][1]),
            )
        parity = -1 if side == "rear" and order % 2 else 1
        weighted = _scaled_complex_real(
            _scaled_complex_multiply(source_factors[order], derivative),
            parity * (2 * order + 1),
        )
        # d/dz reverses the radial direction at the piston-facing pole; i is
        # the source-series prefactor for unit piston velocity.
        axial_sign = -1 if side == "front" else 1
        rotated = complex(-axial_sign * weighted[0].imag, axial_sign * weighted[0].real)
        terms.append(_unscale_complex(_scaled_complex(rotated, weighted[1]), f"/terms/{order}"))
    return tuple(terms)


def _scaled_piston_source_field_terms(
    max_order: int,
    *,
    wave_number_rad_m: float,
    sphere_center_distance_m: float,
    piston_radius_m: float,
    field_radius_m: float,
    cosine: float,
) -> tuple[tuple[complex, complex, complex], ...]:
    """Return source-only potential and spherical-gradient terms per unit piston speed.

    ``field_radius_m`` is measured from the sphere center; ``cosine`` is the
    cosine of its polar angle relative to the piston axis.
    """
    if type(max_order) is not int or not 0 <= max_order <= 512:
        raise InvalidInputError("BESSEL_ORDER_RANGE", "/max_order", "Expected order from 0 through 512.")
    for name, value in (
        ("wave_number_rad_m", wave_number_rad_m),
        ("sphere_center_distance_m", sphere_center_distance_m),
        ("piston_radius_m", piston_radius_m),
        ("field_radius_m", field_radius_m),
    ):
        if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value) or value <= 0:
            raise InvalidInputError("FIELD_GEOMETRY", f"/{name}", "Expected a finite positive value.")
    if type(cosine) not in (int, float) or type(cosine) is bool or not math.isfinite(cosine) or not -1 <= cosine <= 1:
        raise InvalidInputError("FIELD_GEOMETRY", "/cosine", "Expected a finite value in [-1, 1].")

    k = float(wave_number_rad_m)
    field_argument = _finite(k * float(field_radius_m), "/field_argument")
    if not 1.0 <= field_argument <= 12.0:
        raise InvalidInputError(
            "BESSEL_ARGUMENT_RANGE", "/field_radius_m", "Scaled surface-field terms require 1 <= kr <= 12."
        )
    factors = _scaled_source_diffraction_coefficients(
        max_order,
        wave_number_rad_m=k,
        sphere_center_distance_m=sphere_center_distance_m,
        piston_radius_m=piston_radius_m,
    )
    regular = _regular_bessel_scaled_values(max_order + 1, field_argument)
    derivative_start = min(max_order, max(48, math.ceil(field_argument) + 24))
    _, _, derivatives, _ = _spherical_sequences(derivative_start, field_argument)
    sine = math.sqrt(max(0.0, 1.0 - float(cosine) ** 2))
    terms = []

    for order in range(max_order + 1):
        if order < derivative_start:
            radial_bessel_derivative = _scaled_complex(complex(derivatives[order], 0.0))
        else:
            radial_bessel_derivative = _scaled_complex_add(
                _scaled_complex_real(regular[order], order / field_argument),
                _scaled_complex(-regular[order + 1][0], regular[order + 1][1]),
            )
        polynomial, polynomial_derivative = spherical_legendre(order, float(cosine))
        coefficient = (2 * order + 1) * (-1 if order % 2 else 1)
        source = factors[order]
        potential = _scaled_complex_real(
            _scaled_complex_multiply(source, regular[order]), coefficient * polynomial / k
        )
        radial = _scaled_complex_real(
            _scaled_complex_multiply(source, radial_bessel_derivative), coefficient * polynomial
        )
        angular = _scaled_complex_real(
            _scaled_complex_multiply(source, regular[order]),
            -coefficient * sine * polynomial_derivative / k,
        )
        terms.append(
            (
                _unscale_complex(_scaled_complex(complex(-potential[0].imag, potential[0].real), potential[1]), f"/potential/{order}"),
                _unscale_complex(_scaled_complex(complex(-radial[0].imag, radial[0].real), radial[1]), f"/radial/{order}"),
                _unscale_complex(_scaled_complex(complex(-angular[0].imag, angular[0].real), angular[1]), f"/angular/{order}"),
            )
        )
    return tuple(terms)


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
