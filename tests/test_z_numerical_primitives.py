"""Independent identities for numerical kernels; not field-model validation."""

import math
from decimal import Decimal, localcontext

import pytest

from aura.errors import InvalidInputError, NumericalDomainError


@pytest.fixture
def kernels():
    from aura.fields.numerical import (
        gauss_legendre_rule,
        source_diffraction_coefficients,
        spherical_bessel_jy,
        spherical_legendre,
        stationary_sphere_coefficient,
    )

    return (
        spherical_bessel_jy,
        spherical_legendre,
        gauss_legendre_rule,
        stationary_sphere_coefficient,
        source_diffraction_coefficients,
    )


def _decimal_spherical_j(order, argument):
    with localcontext() as context:
        context.prec = 160
        x = Decimal(str(argument))
        denominator = Decimal(1)
        for index in range(1, order + 1):
            denominator *= 2 * index + 1
        term = Decimal(1)
        series = term
        for index in range(1, 300):
            term *= -(x * x) / (Decimal(2 * index) * (2 * order + 2 * index + 1))
            series += term
            if abs(term) < Decimal("1e-90"):
                break
        return x**order * series / denominator


def _decimal_sin_cos(argument):
    with localcontext() as context:
        context.prec = 160
        x = Decimal(str(argument))
        x_squared = x * x
        sine_term, cosine_term = x, Decimal(1)
        sine, cosine = sine_term, cosine_term
        for index in range(1, 300):
            sine_term *= -x_squared / (Decimal(2 * index) * (2 * index + 1))
            cosine_term *= -x_squared / (Decimal(2 * index - 1) * (2 * index))
            sine += sine_term
            cosine += cosine_term
            if max(abs(sine_term), abs(cosine_term)) < Decimal("1e-150"):
                break
        return +sine, +cosine


def _decimal_spherical_y(order, argument):
    with localcontext() as context:
        context.prec = 160
        x = Decimal(str(argument))
        sine, cosine = _decimal_sin_cos(argument)
        values = [-cosine / x, -cosine / (x * x) - sine / x]
        for index in range(1, order + 1):
            values.append((Decimal(2 * index + 1) / x) * values[index] - values[index - 1])
        return +values[order]


def _decimal_stationary_sphere_coefficient(order, argument):
    with localcontext() as context:
        context.prec = 160
        x = Decimal(str(argument))
        j_value = _decimal_spherical_j(order, argument)
        j_next = _decimal_spherical_j(order + 1, argument)
        y_value = _decimal_spherical_y(order, argument)
        y_next = _decimal_spherical_y(order + 1, argument)
        j_derivative = Decimal(order) * j_value / x - j_next
        y_derivative = Decimal(order) * y_value / x - y_next
        denominator = j_derivative**2 + y_derivative**2
        return complex(
            float(-(j_derivative**2) / denominator),
            float((j_derivative * y_derivative) / denominator),
        )


@pytest.mark.parametrize("order", range(8))
@pytest.mark.parametrize("x", (0.25, 1.0, 4.5, 12.0))
def test_spherical_bessel_recurrence_and_derivative_identities(order, x, kernels):
    spherical_bessel_jy, _, _, _, _ = kernels
    jn, yn, j_derivative, y_derivative = spherical_bessel_jy(order, x)
    if order == 0:
        j_previous = math.sin(x) / x
        y_previous = -math.cos(x) / x
        j_next = math.sin(x) / (x * x) - math.cos(x) / x
        y_next = -math.cos(x) / (x * x) - math.sin(x) / x
        assert jn == pytest.approx(j_previous, rel=3e-14, abs=3e-15)
        assert yn == pytest.approx(y_previous, rel=3e-14, abs=3e-15)
    else:
        j_previous, y_previous, _, _ = spherical_bessel_jy(order - 1, x)
        j_next = (2 * order + 1) * jn / x - j_previous
        y_next = (2 * order + 1) * yn / x - y_previous
    assert j_derivative == pytest.approx(order * jn / x - j_next, rel=3e-14, abs=3e-15)
    assert y_derivative == pytest.approx(order * yn / x - y_next, rel=3e-14, abs=3e-15)


@pytest.mark.parametrize("order", range(13))
@pytest.mark.parametrize("x", (0.25, 4.5, 12.0, 100.0))
def test_miller_j_values_against_independent_decimal_series(order, x, kernels):
    spherical_bessel_jy, _, _, _, _ = kernels
    actual = spherical_bessel_jy(order, x)[0]
    expected = float(_decimal_spherical_j(order, x))
    assert actual == pytest.approx(expected, rel=2e-13, abs=2e-15)


@pytest.mark.parametrize("order", range(12))
@pytest.mark.parametrize("cosine", (-1.0, -0.6, 0.0, 0.4, 1.0))
def test_legendre_derivative_matches_finite_difference_and_parity(order, cosine, kernels):
    _, spherical_legendre, _, _, _ = kernels
    value, derivative = spherical_legendre(order, cosine)
    assert math.isfinite(value)
    assert math.isfinite(derivative)
    reflected, reflected_derivative = spherical_legendre(order, -cosine)
    assert reflected == pytest.approx((-1) ** order * value, abs=3e-14)
    assert reflected_derivative == pytest.approx((-1) ** (order + 1) * derivative, abs=3e-14)
    if abs(cosine) < 1:
        step = 1e-6
        left = spherical_legendre(order, cosine - step)[0]
        right = spherical_legendre(order, cosine + step)[0]
        assert derivative == pytest.approx((right - left) / (2 * step), abs=2e-8)


@pytest.mark.parametrize(
    "order,x,code",
    ((-1, 1.0, "BESSEL_ORDER"), (1.0, 1.0, "BESSEL_ORDER"), (0, 0.0, "BESSEL_ARGUMENT")),
)
def test_bessel_rejects_invalid_domain(order, x, code, kernels):
    spherical_bessel_jy, _, _, _, _ = kernels
    with pytest.raises(InvalidInputError, match=code):
        spherical_bessel_jy(order, x)


def test_bessel_fails_typed_when_outgoing_solution_exceeds_binary64(kernels):
    spherical_bessel_jy, _, _, _, _ = kernels
    with pytest.raises(NumericalDomainError, match="NUMERIC_RANGE"):
        spherical_bessel_jy(512, 0.01)


def test_bessel_bounds_miller_workspace_before_allocation(kernels):
    spherical_bessel_jy, _, _, _, _ = kernels
    with pytest.raises(InvalidInputError, match="BESSEL_WORK_RANGE"):
        spherical_bessel_jy(0, 1e9)


@pytest.mark.parametrize("order", range(1, 10))
def test_gauss_legendre_rule_integrates_polynomial_moments(order, kernels):
    _, _, gauss_legendre_rule, _, _ = kernels
    nodes, weights = gauss_legendre_rule(order)
    assert nodes == tuple(sorted(nodes))
    assert weights == pytest.approx(tuple(reversed(weights)), abs=2e-15)
    for degree in range(2 * order):
        observed = math.fsum(weight * node**degree for node, weight in zip(nodes, weights, strict=True))
        expected = 0.0 if degree % 2 else 2 / (degree + 1)
        assert observed == pytest.approx(expected, rel=2e-13, abs=2e-14)


@pytest.mark.parametrize("order", range(16))
def test_stationary_sphere_coefficient_enforces_zero_normal_velocity(order, kernels):
    spherical_bessel_jy, _, _, stationary_sphere_coefficient, _ = kernels
    _, _, j_derivative, y_derivative = spherical_bessel_jy(order, 11.45)
    coefficient = stationary_sphere_coefficient(order, 11.45)
    residual = complex(j_derivative, 0.0) + coefficient * complex(j_derivative, y_derivative)
    scale = math.hypot(j_derivative, y_derivative)
    assert abs(residual) <= 8 * math.ulp(scale)


@pytest.mark.parametrize("order", range(17))
def test_stationary_sphere_coefficient_matches_decimal_reference_at_air_ka(order, kernels):
    *_, stationary_sphere_coefficient, _ = kernels
    ka = 2 * math.pi * 25230 * 0.025 / 346
    expected = _decimal_stationary_sphere_coefficient(order, ka)
    actual = stationary_sphere_coefficient(order, ka)
    assert actual == pytest.approx(expected, rel=8e-14, abs=2e-15)


@pytest.mark.parametrize("order", (0, 1))
def test_low_order_source_factors_match_independent_simpson_quadrature(order, kernels):
    *_, source_diffraction_coefficients = kernels
    wavenumber, center_distance, radius = 1.0, 3.0, 0.7
    lower = wavenumber * center_distance
    upper = wavenumber * math.hypot(center_distance, radius)
    count = 4096
    step = (upper - lower) / count

    def integrand(argument):
        j0 = math.sin(argument) / argument
        y0 = -math.cos(argument) / argument
        if order == 0:
            polynomial = 1.0
            jn, yn = j0, y0
        else:
            polynomial = lower / argument
            jn = math.sin(argument) / argument**2 - math.cos(argument) / argument
            yn = -math.cos(argument) / argument**2 - math.sin(argument) / argument
        return 2 * complex(jn, yn) * polynomial / argument

    values = [integrand(lower + index * step) for index in range(count + 1)]
    reference = step / 3 * complex(
        math.fsum((1 if index in (0, count) else 4 if index % 2 else 2) * value.real
                  for index, value in enumerate(values)),
        math.fsum((1 if index in (0, count) else 4 if index % 2 else 2) * value.imag
                  for index, value in enumerate(values)),
    )
    observed = source_diffraction_coefficients(
        order,
        wave_number_rad_m=wavenumber,
        sphere_center_distance_m=center_distance,
        piston_radius_m=radius,
        quadrature_order=32,
        workspace_bytes=2_000_000,
    )[order]
    assert observed == pytest.approx(reference, rel=2e-12, abs=2e-14)


def test_source_coefficients_reject_workspace_before_quadrature(kernels, monkeypatch):
    *_, source_diffraction_coefficients = kernels
    import aura.fields.numerical as implementation

    def forbidden(*args, **kwargs):
        raise AssertionError("Quadrature must not start before workspace validation.")

    monkeypatch.setattr(implementation, "gauss_legendre_rule", forbidden)
    with pytest.raises(InvalidInputError, match="FIELD_RESOURCE"):
        source_diffraction_coefficients(
            0,
            wave_number_rad_m=1.0,
            sphere_center_distance_m=3.0,
            piston_radius_m=0.7,
            quadrature_order=32,
            workspace_bytes=1,
        )


def test_num02_workspace_covers_source_coefficient_live_arrays(kernels):
    from aura.fields.numerical import _source_workspace_estimate
    from aura.preflight import (
        SERIALIZATION_FIXED_BYTES,
        _bessel_scratch_bytes,
        _order_vector_bytes,
        _quadrature_workspace_bytes,
    )

    order_count, quadrature_order, argument_max = 5, 32, 10.0
    margin = max(32, int(math.sqrt(40 * order_count)))
    bessel_start = max(order_count + margin, math.ceil(argument_max) + margin)
    preflight_bytes = (
        _order_vector_bytes(order_count)
        + _quadrature_workspace_bytes(quadrature_order)
        + _bessel_scratch_bytes(bessel_start)
        + SERIALIZATION_FIXED_BYTES
    )
    local_bytes = _source_workspace_estimate(order_count, quadrature_order, bessel_start)
    assert preflight_bytes >= local_bytes
