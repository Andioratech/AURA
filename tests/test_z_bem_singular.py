import cmath
import math

import pytest

from aura.errors import InvalidInputError
from aura.fields._bem_axisymmetric import (
    integrate_helmholtz_ring_green_gradient_zero_mode,
    integrate_helmholtz_ring_green_zero_mode,
    integrate_neumann_ring_burton_miller_terms_zero_mode,
)
from aura.fields._bem_singular import (
    integrate_cauchy_principal_value_panel,
    integrate_direct_sphere_maue_panel,
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
@pytest.mark.parametrize(
    "field_theta",
    [1.1, math.radians(120.0), math.radians(135.0)],
    ids=["existing-angle", "120-deg", "135-deg"],
)
def test_singular_panel_subtraction_matches_exact_sphere_hypersingular_modes(
    degree, field_theta
):
    radius = 0.017
    kr = 2.3
    wave_number = kr / radius
    clearance = radius
    field_pressure = 1.0 if degree == 0 else math.cos(field_theta)

    def density(theta):
        return 1.0 if degree == 0 else math.cos(theta)

    def tangent_derivative(theta):
        return 0.0 if degree == 0 else -math.sin(theta) / radius

    def numerical_surface_integral(order):
        return integrate_direct_sphere_maue_panel(
            radius,
            clearance,
            field_theta,
            0.0,
            math.pi,
            density,
            tangent_derivative,
            wave_number_rad_m=wave_number,
            azimuth_samples=1_024,
            meridian_order=order,
        )

    j0 = math.sin(kr) / kr
    j1 = math.sin(kr) / (kr * kr) - math.cos(kr) / kr
    j0_prime = -j1
    j1_prime = j0 - 2.0 * j1 / kr
    h0 = -1j * cmath.exp(1j * kr) / kr
    h1 = -cmath.exp(1j * kr) * (kr + 1j) / (kr * kr)
    h0_prime = -h1
    h1_prime = h0 - 2.0 * h1 / kr
    # Kreuzer (2024), Eq. 6, for G=exp(i*k*r)/(4*pi*r); DOI 10.1016/j.enganabound.2024.105883.
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


@pytest.mark.parametrize(
    ("field_theta", "left", "right", "meridian_order"),
    [
        (0.0, 0.0, math.pi, 16),
        (math.pi / 2.0, 0.0, math.pi / 2.0, 16),
        (1.1, 0.0, math.pi, 1),
    ],
)
def test_direct_sphere_maue_panel_rejects_poles_joins_and_invalid_order(
    field_theta, left, right, meridian_order
):
    with pytest.raises(InvalidInputError):
        integrate_direct_sphere_maue_panel(
            0.017,
            0.001,
            field_theta,
            left,
            right,
            lambda _: 1.0,
            lambda _: 0.0,
            wave_number_rad_m=2.3 / 0.017,
            azimuth_samples=16,
            meridian_order=meridian_order,
        )


@pytest.mark.parametrize("degree", [0, 1])
@pytest.mark.parametrize("field_theta", [math.radians(120.0), math.radians(135.0)])
def test_cbie_layer_panel_subtraction_matches_exact_sphere_modes(degree, field_theta):
    """Check direct single/double layers after explicit logarithmic subtraction."""
    from aura.fields.numerical import gauss_legendre_rule

    radius = 0.017
    kr = 2.3
    wave_number = kr / radius
    center_height = 2.0 * radius
    field = (
        radius * math.sin(field_theta), 0.0,
        center_height + radius * math.cos(field_theta),
    )
    field_mode = 1.0 if degree == 0 else math.cos(field_theta)
    singular_arclength = radius * field_theta
    log_scale = 8.0 * radius

    def mode(theta):
        return 1.0 if degree == 0 else math.cos(theta)

    def integrate_layers(meridian_order):
        nodes, weights = gauss_legendre_rule(meridian_order)
        single_remainder = []
        double_remainder = []
        for lower, upper in ((0.0, field_theta), (field_theta, math.pi)):
            midpoint = 0.5 * (lower + upper)
            half_width = 0.5 * (upper - lower)
            for node, weight in zip(nodes, weights, strict=True):
                theta = midpoint + half_width * node
                sine, cosine = math.sin(theta), math.cos(theta)
                source_radius = radius * sine
                source_height = center_height + radius * cosine
                source_normal = (-sine, -cosine)
                density = mode(theta)
                offset = theta - field_theta
                logarithm = math.log(log_scale / abs(radius * offset))
                _, source_gradient = integrate_helmholtz_ring_green_gradient_zero_mode(
                    field[0], field[2], source_radius, source_height,
                    wave_number_rad_m=wave_number, azimuth_samples=1_024,
                )
                normal_terms = tuple(
                    component * normal
                    for component, normal in zip(source_gradient, source_normal, strict=True)
                )
                source_normal_derivative = complex(
                    math.fsum(value.real for value in normal_terms),
                    math.fsum(value.imag for value in normal_terms),
                )
                green = integrate_helmholtz_ring_green_zero_mode(
                    field[0], field[2], source_radius, source_height,
                    wave_number_rad_m=wave_number, azimuth_samples=1_024,
                )
                surface_weight = half_width * weight * radius * source_radius
                single_remainder.append(
                    surface_weight * density * green
                    - half_width * weight * radius * density * logarithm / (2.0 * math.pi)
                )
                double_remainder.append(
                    surface_weight * density * source_normal_derivative
                    - half_width * weight * density * logarithm / (4.0 * math.pi)
                )

        single_log = integrate_logarithmic_panel(
            lambda arclength: mode(arclength / radius) / (2.0 * math.pi),
            0.0, math.pi * radius, singular_arclength,
            log_scale=log_scale, order=meridian_order,
        )
        double_log = integrate_logarithmic_panel(
            lambda arclength: mode(arclength / radius) / (4.0 * math.pi * radius),
            0.0, math.pi * radius, singular_arclength,
            log_scale=log_scale, order=meridian_order,
        )
        return (
            math.fsum(value.real for value in single_remainder)
            + 1j * math.fsum(value.imag for value in single_remainder)
            + single_log,
            math.fsum(value.real for value in double_remainder)
            + 1j * math.fsum(value.imag for value in double_remainder)
            + double_log,
        )

    j0 = math.sin(kr) / kr
    j1 = math.sin(kr) / kr**2 - math.cos(kr) / kr
    j_values = (j0, j1)
    h0 = -1j * cmath.exp(1j * kr) / kr
    h1 = -cmath.exp(1j * kr) * (kr + 1j) / kr**2
    h_values = (h0, h1)
    h_derivatives = (-h1, h0 - 2.0 * h1 / kr)
    exact_single = 1j * wave_number * radius**2 * j_values[degree] * h_values[degree]
    # AURA's source normal points into the sphere, opposite to Kreuzer's Eq. 5.
    exact_double = -(0.5 + 1j * wave_number**2 * radius**2 * h_derivatives[degree] * j_values[degree])
    exact = (field_mode * exact_single, field_mode * exact_double)

    coarse = integrate_layers(16)
    intermediate = integrate_layers(32)
    refined = integrate_layers(64)
    for actual, expected, previous, earlier in zip(
        refined, exact, intermediate, coarse, strict=True
    ):
        assert abs(actual - expected) < abs(previous - expected)
        assert abs(actual - expected) < abs(earlier - expected) / 2.0
        assert actual == pytest.approx(expected, rel=3e-4, abs=3e-5)

    outgoing_trace = h_values[degree] * field_mode
    outgoing_radial_derivative = wave_number * h_derivatives[degree]

    def cbie_residual(layers):
        single_layer, double_layer = layers
        # AURA's normal points into the sphere, opposite to the reference normal.
        source_normal_derivative = -outgoing_radial_derivative
        return (
            0.5 * outgoing_trace
            + h_values[degree] * double_layer
            - source_normal_derivative * single_layer
        )

    residuals = tuple(cbie_residual(layers) for layers in (coarse, intermediate, refined))
    residual_scale = max(abs(outgoing_trace), 1e-30)
    assert abs(residuals[1]) < abs(residuals[0])
    assert abs(residuals[2]) < abs(residuals[1])
    assert abs(residuals[2]) / residual_scale < 5e-5


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
