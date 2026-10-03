"""Independent identities for numerical kernels; not field-model validation."""

import math
from decimal import Decimal, localcontext

import pytest

from aura.errors import InvalidInputError, NumericalDomainError


@pytest.fixture
def kernels():
    from aura.fields.numerical import spherical_bessel_jy, spherical_legendre

    return spherical_bessel_jy, spherical_legendre


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


@pytest.mark.parametrize("order", range(8))
@pytest.mark.parametrize("x", (0.25, 1.0, 4.5, 12.0))
def test_spherical_bessel_recurrence_and_derivative_identities(order, x, kernels):
    spherical_bessel_jy, _ = kernels
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
    spherical_bessel_jy, _ = kernels
    actual = spherical_bessel_jy(order, x)[0]
    expected = float(_decimal_spherical_j(order, x))
    assert actual == pytest.approx(expected, rel=2e-13, abs=2e-15)


@pytest.mark.parametrize("order", range(12))
@pytest.mark.parametrize("cosine", (-1.0, -0.6, 0.0, 0.4, 1.0))
def test_legendre_derivative_matches_finite_difference_and_parity(order, cosine, kernels):
    _, spherical_legendre = kernels
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
    spherical_bessel_jy, _ = kernels
    with pytest.raises(InvalidInputError, match=code):
        spherical_bessel_jy(order, x)


def test_bessel_fails_typed_when_outgoing_solution_exceeds_binary64(kernels):
    spherical_bessel_jy, _ = kernels
    with pytest.raises(NumericalDomainError, match="NUMERIC_RANGE"):
        spherical_bessel_jy(512, 0.01)


def test_bessel_bounds_miller_workspace_before_allocation(kernels):
    spherical_bessel_jy, _ = kernels
    with pytest.raises(InvalidInputError, match="BESSEL_WORK_RANGE"):
        spherical_bessel_jy(0, 1e9)
