"""High-precision, observable-weighted check of the Hasegawa piston series."""

import math
from decimal import Decimal, localcontext

import pytest


def _sin_cos(x, precision):
    """Decimal Taylor reference for the modest positive arguments in this case."""
    with localcontext() as context:
        context.prec = precision + 24
        x = Decimal(str(x))
        x2 = x * x
        sine_term, cosine_term = x, Decimal(1)
        sine, cosine = sine_term, cosine_term
        for index in range(1, 1000):
            sine_term *= -x2 / (Decimal(2 * index) * (2 * index + 1))
            cosine_term *= -x2 / (Decimal(2 * index - 1) * (2 * index))
            sine += sine_term
            cosine += cosine_term
            if max(abs(sine_term), abs(cosine_term)) < Decimal(1).scaleb(-(precision + 12)):
                break
        context.prec = precision
        return +sine, +cosine


def _hankel_zero(argument, sine, cosine):
    return sine / argument, -cosine / argument


def _hankel_one(argument, sine, cosine):
    return (
        sine / (argument * argument) - cosine / argument,
        -cosine / (argument * argument) - sine / argument,
    )


def _source_factors(max_order, k, center_distance, piston_radius, precision):
    """Conjugated Hasegawa Eqs. (2)-(4), using the recurrence in Eq. (3)."""
    with localcontext() as context:
        context.prec = precision
        k = Decimal(str(k))
        center_distance = Decimal(str(center_distance))
        piston_radius = Decimal(str(piston_radius))
        # Match the geometry construction used by the binary64 kernel exactly.
        upper_radius = Decimal(
            str(math.hypot(float(center_distance), float(piston_radius)))
        )
        lower_argument, upper_argument = k * center_distance, k * upper_radius
        lower_sine, lower_cosine = _sin_cos(lower_argument, precision)
        upper_sine, upper_cosine = _sin_cos(upper_argument, precision)

        h_lower = _hankel_zero(lower_argument, lower_sine, lower_cosine)
        h_upper = _hankel_zero(upper_argument, upper_sine, upper_cosine)
        h_upper_next = _hankel_one(upper_argument, upper_sine, upper_cosine)
        factors = [
            (lower_cosine - upper_cosine, lower_sine - upper_sine),
            (
                -lower_argument * (h_upper[0] - h_lower[0]),
                -lower_argument * (h_upper[1] - h_lower[1]),
            ),
        ]
        hankel = [h_upper, h_upper_next]
        ratio = center_distance / upper_radius
        previous_legendre, legendre = Decimal(1), ratio

        for order in range(2, max_order + 1):
            previous_hankel, current_hankel = hankel[order - 2], hankel[order - 1]
            previous_previous_legendre = previous_legendre
            next_legendre = (
                Decimal(2 * order - 1) * ratio * legendre
                - Decimal(order - 1) * previous_legendre
            ) / Decimal(order)
            hankel_order_minus_one = current_hankel
            difference = next_legendre - previous_previous_legendre
            factors.append(
                (
                    -factors[order - 2][0]
                    - upper_argument * hankel_order_minus_one[0] * difference,
                    -factors[order - 2][1]
                    - upper_argument * hankel_order_minus_one[1] * difference,
                )
            )
            next_hankel = (
                Decimal(2 * order - 1) / upper_argument * current_hankel[0]
                - previous_hankel[0],
                Decimal(2 * order - 1) / upper_argument * current_hankel[1]
                - previous_hankel[1],
            )
            hankel.append(next_hankel)
            previous_legendre, legendre = legendre, next_legendre
        return factors


def _spherical_j(order, argument, precision):
    """Independent Decimal power series for j_n at the fixed ka=11.45."""
    with localcontext() as context:
        context.prec = precision
        argument = Decimal(str(argument))
        denominator = Decimal(1)
        for index in range(1, order + 1):
            denominator *= 2 * index + 1
        term = Decimal(1)
        series = term
        for index in range(1, 1000):
            term *= -(argument * argument) / (
                Decimal(2 * index) * (2 * order + 2 * index + 1)
            )
            series += term
            if abs(term) < Decimal(1).scaleb(-(precision - 16)):
                break
        return argument**order * series / denominator


def test_decimal_source_recurrence_matches_integral_and_axial_derivative_tail():
    """Resolve whether the order-253 derivative residual is tail or roundoff."""
    from aura.fields.numerical import source_diffraction_coefficients

    speed, frequency = 346.0, 25230.0
    wavenumber = 2 * math.pi * frequency / speed
    piston_radius, sphere_radius, gap = 0.01, 0.025, 0.0001
    center_distance = sphere_radius + gap
    max_order, precision = 300, 180

    factors = _source_factors(
        max_order, wavenumber, center_distance, piston_radius, precision
    )
    quadrature_factors = source_diffraction_coefficients(
        24,
        wave_number_rad_m=wavenumber,
        sphere_center_distance_m=center_distance,
        piston_radius_m=piston_radius,
        quadrature_order=128,
        workspace_bytes=80_000_000,
    )
    for order in (0, 1, 2, 8, 16, 24):
        reference = complex(float(factors[order][0]), float(factors[order][1]))
        assert reference == pytest.approx(quadrature_factors[order], rel=2e-12, abs=2e-13)

    ka = wavenumber * sphere_radius
    regular = [_spherical_j(order, ka, precision) for order in range(max_order + 2)]
    weighted_terms = []
    for order, factor in enumerate(factors):
        derivative = Decimal(order) * regular[order] / Decimal(str(ka)) - regular[order + 1]
        scale = Decimal(2 * order + 1) * derivative
        weighted_terms.append((factor[0] * scale, factor[1] * scale))

    k_decimal = Decimal(str(wavenumber))
    radius_decimal = Decimal(str(piston_radius))
    reference_errors = {}
    for z_value, sign in ((gap, -1), (gap + 2 * sphere_radius, 1)):
        z = Decimal(str(z_value))
        rayleigh_radius = (z * z + radius_decimal * radius_decimal).sqrt()
        axial_sine, axial_cosine = _sin_cos(k_decimal * z, precision)
        rayleigh_sine, rayleigh_cosine = _sin_cos(k_decimal * rayleigh_radius, precision)
        expected = (
            z / rayleigh_radius * rayleigh_cosine - axial_cosine,
            z / rayleigh_radius * rayleigh_sine - axial_sine,
        )
        total = (Decimal(0), Decimal(0))
        relative_by_order = {}
        for order, term in enumerate(weighted_terms):
            parity = -1 if sign > 0 and order % 2 else 1
            total = total[0] + parity * term[0], total[1] + parity * term[1]
            if order in (253, 280, 300):
                # At the front pole P_n(-1) cancels the (-1)^n series factor;
                # at the rear pole the series retains that modal parity.
                signed_total = (sign * total[0], sign * total[1])
                predicted = (-signed_total[1], signed_total[0])
                difference = (
                    predicted[0] - expected[0],
                    predicted[1] - expected[1],
                )
                expected_magnitude = (expected[0] ** 2 + expected[1] ** 2).sqrt()
                relative_by_order[order] = (
                    difference[0] ** 2 + difference[1] ** 2
                ).sqrt() / expected_magnitude
        reference_errors[z_value] = relative_by_order

    # The 2e-11 value is exploratory, not a production acceptance threshold.
    for errors in reference_errors.values():
        assert errors[253] > Decimal("2e-11")
        assert errors[280] < Decimal("2e-11")
        assert errors[300] < Decimal("1e-11")
