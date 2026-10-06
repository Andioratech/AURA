import cmath
import math

import pytest

from aura.errors import InvalidInputError
from aura.fields._bem_axisymmetric import integrate_neumann_ring_burton_miller_terms_zero_mode
from aura.fields._bem_singular import (
    integrate_cauchy_principal_value_panel,
    integrate_logarithmic_panel,
)


def test_cauchy_panel_subtraction_matches_independent_polynomial_primitive():
    left, right, point = -1.0, 2.0, 0.3

    def density(position):
        return 1.0 + 2.0 * position + 0.5 * position**2

    def primitive(position):
        remainder = 1.0 + 2.0 * point + 0.5 * point**2
        return (
            0.25 * position**2
            + (2.0 + 0.5 * point) * position
            + remainder * math.log(abs(position - point))
        )

    expected = (primitive(right) - primitive(left)) / (2.0 * math.pi)
    actual = integrate_cauchy_principal_value_panel(
        density, left, right, point, order=16
    )
    assert actual == pytest.approx(expected, rel=2e-14, abs=2e-14)


def test_logarithmic_panel_subtraction_matches_independent_polynomial_primitive():
    left, right, point, scale = -1.0, 2.0, 0.3, 4.0

    def primitive(position):
        offset = position - point
        logarithm = math.log(scale / abs(offset)) if offset else 0.0
        zeroth = offset * (logarithm + 1.0)
        first = 0.5 * offset**2 * logarithm + 0.25 * offset**2 + point * zeroth
        return zeroth + 2.0 * first

    expected = primitive(right) - primitive(left)
    actual = integrate_logarithmic_panel(
        lambda position: 1.0 + 2.0 * position,
        left,
        right,
        point,
        log_scale=scale,
        density_derivative=lambda position: 2.0,
        order=64,
    )
    assert actual == pytest.approx(expected, rel=2e-13, abs=2e-13)

    without_slope = integrate_logarithmic_panel(
        lambda position: 1.0 + 2.0 * position,
        left,
        right,
        point,
        log_scale=scale,
        order=256,
    )
    assert without_slope == pytest.approx(expected, rel=2e-11, abs=2e-10)


def test_cauchy_panel_rejects_one_sided_endpoint_collocation():
    with pytest.raises(InvalidInputError, match="strictly interior"):
        integrate_cauchy_principal_value_panel(lambda position: position, -1.0, 1.0, -1.0)


@pytest.mark.parametrize("singular_point", [0.0, 1.3])
def test_logarithmic_panel_integrates_linear_density_at_outer_endpoint(singular_point):
    left, right, scale = 0.0, 1.3, 2.0

    def primitive(offset):
        if offset == 0.0:
            return 0.0, 0.0
        log_value = math.log(scale / abs(offset))
        return (
            offset * (log_value + 1.0),
            0.5 * offset**2 * log_value + 0.25 * offset**2,
        )

    constant_left, linear_left = primitive(left - singular_point)
    constant_right, linear_right = primitive(right - singular_point)
    expected = (constant_right - constant_left) + 2.0 * (linear_right - linear_left)
    actual = integrate_logarithmic_panel(
        lambda position: 1.0 + 2.0 * (position - singular_point),
        left,
        right,
        singular_point,
        log_scale=scale,
        density_derivative=lambda _: 2.0,
        order=8,
    )
    assert actual == pytest.approx(expected, rel=2e-14, abs=2e-14)


def test_logarithmic_panel_rejects_nonpositive_scale():
    with pytest.raises(InvalidInputError, match="positive length scale"):
        integrate_logarithmic_panel(lambda position: position, -1.0, 1.0, 0.0, log_scale=0.0)


def test_cauchy_panel_integrates_a_continuous_density_kink_at_a_panel_join():
    left, join, right = -0.7, 0.0, 1.3
    value_at_join = 2.4
    left_slope, right_slope = -1.7, 0.8

    def density(position):
        slope = left_slope if position < join else right_slope
        return value_at_join + slope * (position - join)

    expected = (
        left_slope * (join - left)
        + right_slope * (right - join)
        + value_at_join * math.log((right - join) / (join - left))
    ) / (2.0 * math.pi)
    actual = integrate_cauchy_principal_value_panel(
        density, left, right, join, order=8
    )
    assert actual == pytest.approx(expected, rel=2e-14, abs=2e-14)


def test_logarithmic_panel_integrates_a_continuous_density_kink_at_a_panel_join():
    left, join, right, scale = -0.7, 0.0, 1.3, 2.0
    value_at_join = 2.4
    left_slope, right_slope = -1.7, 0.8

    def density(position):
        slope = left_slope if position < join else right_slope
        return value_at_join + slope * (position - join)

    def constant_primitive(offset):
        return offset * (math.log(scale / abs(offset)) + 1.0) if offset else 0.0

    def linear_primitive(offset):
        return (
            0.5 * offset**2 * math.log(scale / abs(offset)) + 0.25 * offset**2
            if offset else 0.0
        )

    expected = value_at_join * (
        constant_primitive(right - join) - constant_primitive(left - join)
    )
    expected += left_slope * (
        linear_primitive(0.0) - linear_primitive(left - join)
    )
    expected += right_slope * (
        linear_primitive(right - join) - linear_primitive(0.0)
    )
    actual = integrate_logarithmic_panel(
        density, left, right, join, log_scale=scale, order=256
    )
    assert actual == pytest.approx(expected, rel=2e-10, abs=2e-10)


@pytest.mark.parametrize("degree", [0, 1])
def test_singular_panel_subtraction_matches_exact_sphere_hypersingular_modes(degree):
    radius = 0.017
    kr = 2.3
    wave_number = kr / radius
    field_theta = 1.1
    clearance = radius
    field_radius = radius * math.sin(field_theta)
    field_height = clearance + radius * (1.0 + math.cos(field_theta))
    field_normal = (-math.sin(field_theta), -math.cos(field_theta))
    field_pressure = 1.0 if degree == 0 else math.cos(field_theta)
    field_tangent_derivative = 0.0 if degree == 0 else -math.sin(field_theta) / radius
    cauchy_density = field_tangent_derivative
    logarithmic_density = radius * wave_number**2 * field_pressure / (2.0 * math.pi)
    logarithmic_scale = 8.0 * field_radius / radius

    def density(theta):
        return 1.0 if degree == 0 else math.cos(theta)

    def tangent_derivative(theta):
        return 0.0 if degree == 0 else -math.sin(theta) / radius

    def numerical_surface_integral(order):
        from aura.fields.numerical import gauss_legendre_rule

        nodes, weights = gauss_legendre_rule(order)

        def regularized(theta):
            source_radius = radius * math.sin(theta)
            source_height = clearance + radius * (1.0 + math.cos(theta))
            source_normal = (-math.sin(theta), -math.cos(theta))
            direct, _ = integrate_neumann_ring_burton_miller_terms_zero_mode(
                field_radius,
                field_height,
                field_normal,
                source_radius,
                source_height,
                source_normal,
                pressure_pa=density(theta),
                pressure_tangent_derivative_pa_m=tangent_derivative(theta),
                wave_number_rad_m=wave_number,
                azimuth_samples=1_024,
            )
            offset = theta - field_theta
            weighted_ring = source_radius * radius * direct
            return (
                weighted_ring
                - cauchy_density / (2.0 * math.pi * offset)
                - logarithmic_density * math.log(logarithmic_scale / abs(offset))
            )

        residual = 0j
        for panel_left, panel_right in ((0.0, field_theta), (field_theta, math.pi)):
            midpoint = 0.5 * (panel_left + panel_right)
            half_width = 0.5 * (panel_right - panel_left)
            residual += half_width * sum(
                weight * regularized(midpoint + half_width * node)
                for node, weight in zip(nodes, weights, strict=True)
            )
        principal_value = integrate_cauchy_principal_value_panel(
            lambda _: cauchy_density, 0.0, math.pi, field_theta, order=order
        )
        logarithm = logarithmic_density * integrate_logarithmic_panel(
            lambda _: 1.0,
            0.0,
            math.pi,
            field_theta,
            log_scale=logarithmic_scale,
            order=order,
        )
        return residual + principal_value + logarithm

    j0 = math.sin(kr) / kr
    j1 = math.sin(kr) / (kr * kr) - math.cos(kr) / kr
    j0_prime = -j1
    j1_prime = j0 - 2.0 * j1 / kr
    h0 = -1j * cmath.exp(1j * kr) / kr
    h1 = -cmath.exp(1j * kr) * (kr + 1j) / (kr * kr)
    h0_prime = -h1
    h1_prime = h0 - 2.0 * h1 / kr
    hypersingular_eigenvalue = 1j * wave_number**3 * radius**2 * (
        j0_prime * h0_prime if degree == 0 else j1_prime * h1_prime
    )
    exact = hypersingular_eigenvalue * field_pressure

    coarse = numerical_surface_integral(16)
    intermediate = numerical_surface_integral(32)
    refined = numerical_surface_integral(64)
    assert abs(intermediate - exact) < abs(coarse - exact) / 2.0
    assert abs(refined - exact) < abs(intermediate - exact) / 3.0
    assert refined == pytest.approx(exact, rel=2e-4, abs=2e-5)


@pytest.mark.parametrize("degree", [0, 1])
def test_polar_endpoint_collocation_matches_exact_sphere_hypersingular_mode(degree):
    from aura.fields.numerical import gauss_legendre_rule

    radius = 0.017
    kr = 2.3
    wave_number = kr / radius
    clearance = radius
    field_radius = 0.0
    field_height = clearance + 2.0 * radius
    field_normal = (0.0, -1.0)

    def integrate_meridian(order):
        nodes, weights = gauss_legendre_rule(order)
        total = 0j
        for node, weight in zip(nodes, weights, strict=True):
            theta = 0.5 * math.pi * (node + 1.0)
            source_radius = radius * math.sin(theta)
            source_height = clearance + radius * (1.0 + math.cos(theta))
            source_normal = (-math.sin(theta), -math.cos(theta))
            pressure = 1.0 if degree == 0 else math.cos(theta)
            tangent_derivative = 0.0 if degree == 0 else -math.sin(theta) / radius
            direct, _ = integrate_neumann_ring_burton_miller_terms_zero_mode(
                field_radius,
                field_height,
                field_normal,
                source_radius,
                source_height,
                source_normal,
                pressure_pa=pressure,
                pressure_tangent_derivative_pa_m=tangent_derivative,
                wave_number_rad_m=wave_number,
                azimuth_samples=512,
            )
            total += 0.5 * math.pi * weight * source_radius * radius * direct
        return total

    j0 = math.sin(kr) / kr
    j1 = math.sin(kr) / (kr * kr) - math.cos(kr) / kr
    j0_prime = -j1
    j1_prime = j0 - 2.0 * j1 / kr
    h0 = -1j * cmath.exp(1j * kr) / kr
    h1 = -cmath.exp(1j * kr) * (kr + 1j) / (kr * kr)
    h0_prime = -h1
    h1_prime = h0 - 2.0 * h1 / kr
    exact = 1j * wave_number**3 * radius**2 * (
        j0_prime * h0_prime if degree == 0 else j1_prime * h1_prime
    )

    for order in (32, 64):
        assert integrate_meridian(order) == pytest.approx(exact, rel=3e-13, abs=3e-12)
