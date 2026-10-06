import cmath
import math
from decimal import ROUND_CEILING, Decimal, localcontext
from fractions import Fraction
from itertools import pairwise

import pytest

from aura.fields._bem_axisymmetric import (
    integrate_helmholtz_ring_green_gradient_zero_mode,
    integrate_helmholtz_ring_green_zero_mode,
    integrate_neumann_ring_burton_miller_terms_zero_mode,
)
from aura.fields._bem_green import _free_space_term, neumann_half_space_green
from aura.fields._bem_singular import (
    integrate_logarithmic_panel,
)


def _sphere_data(theta, radius, center_height, source, wave_number):
    sine, cosine = math.sin(theta), math.cos(theta)
    field = (radius * sine, 0.0, center_height + radius * cosine)
    normal_rz = (-sine, -cosine)
    pressure, gradient, _ = neumann_half_space_green(
        field, source, wave_number_rad_m=wave_number
    )
    normal_derivative = normal_rz[0] * gradient[0] + normal_rz[1] * gradient[2]
    return field, normal_rz, pressure, normal_derivative


def _mirror_mode_remainder_bound(cutoff_order):
    """Bound the exact image Green-series tail uniformly over real angles.

    This certificate is scoped to a=25 mm, gap=0.1 mm, f=25,230 Hz,
    c=346 m/s and a center monopole. It uses pi<22/7 for the wave-number
    upper bounds and pi>3 for the prefactor. Decimal operations round upward.
    """
    if type(cutoff_order) is not int or cutoff_order < 0:
        raise ValueError("Expected a nonnegative integer cutoff order.")

    frequency = Fraction(25_230)
    sound_speed = Fraction(346)
    radius = Fraction(25, 1_000)
    gap = Fraction(1, 10_000)
    center_distance = 2 * (radius + gap)
    if center_distance <= radius:
        raise ValueError("The source must lie strictly inside the expansion sphere.")

    # k < k_upper follows from pi < 22/7. q=a/D is exact and less than one.
    k_upper = 2 * Fraction(22, 7) * frequency / sound_speed
    x_upper = k_upper * radius
    z_upper = k_upper * center_distance
    ratio = radius / center_distance
    exponent = z_upper + x_upper**2 / (2 * (2 * cutoff_order + 5))

    def decimal_upper(value):
        with localcontext() as context:
            context.prec = 80
            context.rounding = ROUND_CEILING
            return Decimal(value.numerator) / Decimal(value.denominator)

    with localcontext() as context:
        context.prec = 80
        context.rounding = ROUND_CEILING
        # Decimal.exp is correctly rounded to nearest; next_plus gives a
        # strict decimal upper neighbor before the outward-rounded products.
        exponential_upper = decimal_upper(exponent).exp().next_plus()
        geometric_tail_upper = decimal_upper(ratio ** (cutoff_order + 1))
        geometric_sum_upper = decimal_upper(1 / (1 - ratio))
        # Since pi>3, 1/(4*pi*D) < 1/(12*D).
        prefactor_upper = decimal_upper(1 / (12 * center_distance))
        return (
            exponential_upper
            * geometric_tail_upper
            * geometric_sum_upper
            * prefactor_upper
        )


def _image_ring_integrals(
    field_radius,
    field_height,
    field_normal_rz,
    source_radius,
    source_height,
    source_normal_rz,
    wave_number,
    samples,
):
    """Return direct pointwise image-ring integrals of G and dG/dn_source."""
    field = (field_radius, 0.0, field_height)
    step = 2.0 * math.pi / samples
    green_terms = []
    normal_terms = []
    for index in range(samples):
        angle = (index + 0.5) * step
        cosine, sine = math.cos(angle), math.sin(angle)
        source_image = (source_radius * cosine, source_radius * sine, -source_height)
        image_normal = (
            source_normal_rz[0] * cosine,
            source_normal_rz[0] * sine,
            -source_normal_rz[1],
        )
        green, field_gradient = _free_space_term(field, source_image, wave_number)
        source_gradient = tuple(-component for component in field_gradient)
        green_terms.append(step * green)
        normal_derivative = sum(
            component * normal
            for component, normal in zip(source_gradient, image_normal, strict=True)
        )
        normal_terms.append(step * normal_derivative)
    green_integral = complex(
        math.fsum(term.real for term in green_terms),
        math.fsum(term.imag for term in green_terms),
    )
    normal_integral = complex(
        math.fsum(term.real for term in normal_terms),
        math.fsum(term.imag for term in normal_terms),
    )
    return green_integral, normal_integral


def _image_ring_field_normal_integral(
    field_radius,
    field_height,
    field_normal_rz,
    source_radius,
    source_height,
    wave_number,
    samples,
):
    """Return the independent azimuth integral of image dG/dn_field."""
    field = (field_radius, 0.0, field_height)
    field_normal = (field_normal_rz[0], 0.0, field_normal_rz[1])
    step = 2.0 * math.pi / samples
    real_terms = []
    imag_terms = []
    for index in range(samples):
        angle = (index + 0.5) * step
        source_image = (
            source_radius * math.cos(angle),
            source_radius * math.sin(angle),
            -source_height,
        )
        _, gradient = _free_space_term(field, source_image, wave_number)
        derivative = sum(
            component * normal
            for component, normal in zip(gradient, field_normal, strict=True)
        )
        real_terms.append(step * derivative.real)
        imag_terms.append(step * derivative.imag)
    return complex(math.fsum(real_terms), math.fsum(imag_terms))


def test_neumann_half_space_green_identity_on_curved_sphere_with_log_product_integration():
    """Check the full direct-plus-image CBIE without assembling a system matrix."""
    radius = 0.025
    gap = 0.0001
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    sphere_center_height = radius + gap
    field_theta = math.radians(175.0)
    field, _, field_pressure, _ = _sphere_data(
        field_theta,
        radius,
        sphere_center_height,
        (0.0, 0.0, sphere_center_height),
        wave_number,
    )
    source = (0.0, 0.0, sphere_center_height)
    singular_arclength = radius * field_theta
    log_scale = 8.0 * field[0]
    # Subdivide the meridian near the image-kernel peak. This is a quadrature
    # partition, not an error bound or a general near-singular rule.
    cutoff = 8.0 * field[2] / field[0]
    edges = (
        0.0,
        max(0.0, field_theta - cutoff),
        min(math.pi, field_theta + cutoff),
        math.pi,
    )

    def residual_at_order(order):
        from aura.fields.numerical import gauss_legendre_rule

        nodes, weights = gauss_legendre_rule(order)
        double_layer_remainder = []
        single_layer_remainder = []
        image_double_layer = []
        image_single_layer = []
        for lower, upper in pairwise(edges):
            if upper <= lower:
                continue
            midpoint = 0.5 * (lower + upper)
            half_width = 0.5 * (upper - lower)
            for node, weight in zip(nodes, weights, strict=True):
                theta = midpoint + half_width * node
                source_field, source_normal, pressure, normal_derivative = _sphere_data(
                    theta, radius, sphere_center_height, source, wave_number
                )
                source_radius, source_height = source_field[0], source_field[2]
                direct_green = integrate_helmholtz_ring_green_zero_mode(
                    field[0],
                    field[2],
                    source_radius,
                    source_height,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=512,
                )
                _, direct_source_gradient = integrate_helmholtz_ring_green_gradient_zero_mode(
                    field[0],
                    field[2],
                    source_radius,
                    source_height,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=512,
                )
                direct_double_layer = sum(
                    normal * derivative
                    for normal, derivative in zip(
                        source_normal, direct_source_gradient, strict=True
                    )
                )
                image_green, image_double = _image_ring_integrals(
                    field[0],
                    field[2],
                    (-math.sin(field_theta), -math.cos(field_theta)),
                    source_radius,
                    source_height,
                    source_normal,
                    wave_number,
                    1_024,
                )

                arclength = radius * theta
                logarithm = math.log(log_scale / abs(arclength - singular_arclength))
                surface_weight = half_width * weight * radius * source_radius
                double_layer_remainder.append(
                    surface_weight * pressure * direct_double_layer
                    - half_width * weight * pressure * logarithm / (4.0 * math.pi)
                )
                single_layer_remainder.append(
                    surface_weight * normal_derivative * direct_green
                    - half_width
                    * weight
                    * radius
                    * normal_derivative
                    * logarithm
                    / (2.0 * math.pi)
                )
                image_double_layer.append(
                    surface_weight * pressure * image_double
                )
                image_single_layer.append(
                    surface_weight * normal_derivative * image_green
                )

        double_layer_log = integrate_logarithmic_panel(
            lambda arclength: _sphere_data(
                arclength / radius,
                radius,
                sphere_center_height,
                source,
                wave_number,
            )[2]
            / (4.0 * math.pi * radius),
            0.0,
            math.pi * radius,
            singular_arclength,
            log_scale=log_scale,
            order=order,
        )
        single_layer_log = integrate_logarithmic_panel(
            lambda arclength: _sphere_data(
                arclength / radius,
                radius,
                sphere_center_height,
                source,
                wave_number,
            )[3]
            / (2.0 * math.pi),
            0.0,
            math.pi * radius,
            singular_arclength,
            log_scale=log_scale,
            order=order,
        )
        direct_double = complex(
            math.fsum(term.real for term in double_layer_remainder),
            math.fsum(term.imag for term in double_layer_remainder),
        ) + double_layer_log
        image_double = complex(
            math.fsum(term.real for term in image_double_layer),
            math.fsum(term.imag for term in image_double_layer),
        )
        direct_single = complex(
            math.fsum(term.real for term in single_layer_remainder),
            math.fsum(term.imag for term in single_layer_remainder),
        ) + single_layer_log
        image_single = complex(
            math.fsum(term.real for term in image_single_layer),
            math.fsum(term.imag for term in image_single_layer),
        )
        return 0.5 * field_pressure + direct_double + image_double - direct_single - image_single

    residuals = [abs(residual_at_order(order)) / abs(field_pressure) for order in (64, 128, 256)]
    assert residuals[1] < residuals[0] / 20.0, residuals
    assert residuals[2] < residuals[1] / 2.0, residuals
    assert residuals[2] < 4e-6, f"Normalized residuals at orders 64/128/256: {residuals!r}"


def test_neumann_half_space_hbie_identity_on_equatorial_sphere_point():
    """Check half-space H and Burton–Miller identities at the equator."""
    radius = 0.025
    gap = 0.0001
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    center_height = radius + gap
    field_theta = 0.5 * math.pi
    field = (radius, 0.0, center_height)
    field_normal_rz = (-1.0, 0.0)
    source_point = (0.0, 0.0, center_height)
    _, field_gradient, _ = neumann_half_space_green(
        field, source_point, wave_number_rad_m=wave_number
    )
    field_normal_derivative = -field_gradient[0]
    log_scale = 8.0 * radius
    singular_arclength = radius * field_theta

    def source_data(theta):
        sine, cosine = math.sin(theta), math.cos(theta)
        point = (radius * sine, 0.0, center_height + radius * cosine)
        normal_rz = (-sine, -cosine)
        pressure, gradient, _ = neumann_half_space_green(
            point, source_point, wave_number_rad_m=wave_number
        )
        normal_derivative = normal_rz[0] * gradient[0] + normal_rz[1] * gradient[2]
        tangent_derivative = cosine * gradient[0] - sine * gradient[2]
        return point, normal_rz, pressure, normal_derivative, tangent_derivative

    def residual(meridian_order, azimuth_samples):
        from aura.fields.numerical import gauss_legendre_rule

        nodes, weights = gauss_legendre_rule(meridian_order)
        direct_hypersingular = []
        direct_adjoint = []
        image_hypersingular = []
        image_adjoint = []
        direct_double_layer = []
        direct_single_layer = []
        image_double_layer = []
        image_single_layer = []
        # The equatorial split uses equal panels, so the leading constant-density
        # Cauchy term cancels pairwise; this special symmetry does not cover other points.
        for lower, upper in ((0.0, field_theta), (field_theta, math.pi)):
            midpoint = 0.5 * (lower + upper)
            half_width = 0.5 * (upper - lower)
            for node, weight in zip(nodes, weights, strict=True):
                theta = midpoint + half_width * node
                point, normal, pressure, normal_derivative, tangent_derivative = source_data(theta)
                source_radius, source_height = point[0], point[2]
                logarithm = math.log(
                    log_scale / abs(radius * theta - singular_arclength)
                )
                surface_weight = half_width * weight * radius * source_radius
                direct_maue, image_maue = integrate_neumann_ring_burton_miller_terms_zero_mode(
                    field[0],
                    field[2],
                    field_normal_rz,
                    source_radius,
                    source_height,
                    normal,
                    pressure_pa=pressure,
                    pressure_tangent_derivative_pa_m=tangent_derivative,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=azimuth_samples,
                )
                direct_field_gradient, direct_source_gradient = integrate_helmholtz_ring_green_gradient_zero_mode(
                    field[0],
                    field[2],
                    source_radius,
                    source_height,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=azimuth_samples,
                )
                direct_field_normal = -direct_field_gradient[0]
                direct_green = integrate_helmholtz_ring_green_zero_mode(
                    field[0],
                    field[2],
                    source_radius,
                    source_height,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=azimuth_samples,
                )
                direct_source_normal = sum(
                    component * normal_component
                    for component, normal_component in zip(
                        direct_source_gradient, normal, strict=True
                    )
                )
                image_green, image_source_normal = _image_ring_integrals(
                    field[0],
                    field[2],
                    field_normal_rz,
                    source_radius,
                    source_height,
                    normal,
                    wave_number,
                    2 * azimuth_samples,
                )
                image_field_normal = _image_ring_field_normal_integral(
                    field[0],
                    field[2],
                    field_normal_rz,
                    source_radius,
                    source_height,
                    wave_number,
                    2 * azimuth_samples,
                )

                # Subtract and restore the same logarithm under ds=a*dtheta.
                direct_hypersingular.append(
                    surface_weight * direct_maue
                    - half_width
                    * weight
                    * radius
                    * wave_number**2
                    * pressure
                    * logarithm
                    / (2.0 * math.pi)
                )
                direct_adjoint.append(
                    surface_weight * normal_derivative * direct_field_normal
                    - half_width * weight * normal_derivative * logarithm / (4.0 * math.pi)
                )
                image_hypersingular.append(surface_weight * image_maue)
                image_adjoint.append(
                    surface_weight * normal_derivative * image_field_normal
                )
                direct_double_layer.append(
                    surface_weight * pressure * direct_source_normal
                    - half_width * weight * pressure * logarithm / (4.0 * math.pi)
                )
                direct_single_layer.append(
                    surface_weight * normal_derivative * direct_green
                    - half_width
                    * weight
                    * radius
                    * normal_derivative
                    * logarithm
                    / (2.0 * math.pi)
                )
                image_double_layer.append(
                    surface_weight * pressure * image_source_normal
                )
                image_single_layer.append(
                    surface_weight * normal_derivative * image_green
                )

        hypersingular_log = integrate_logarithmic_panel(
            lambda arclength: wave_number**2
            * source_data(arclength / radius)[2]
            / (2.0 * math.pi),
            0.0,
            math.pi * radius,
            singular_arclength,
            log_scale=log_scale,
            order=meridian_order,
        )
        adjoint_log = integrate_logarithmic_panel(
            lambda arclength: source_data(arclength / radius)[3]
            / (4.0 * math.pi * radius),
            0.0,
            math.pi * radius,
            singular_arclength,
            log_scale=log_scale,
            order=meridian_order,
        )
        double_layer_log = integrate_logarithmic_panel(
            lambda arclength: source_data(arclength / radius)[2]
            / (4.0 * math.pi * radius),
            0.0,
            math.pi * radius,
            singular_arclength,
            log_scale=log_scale,
            order=meridian_order,
        )
        single_layer_log = integrate_logarithmic_panel(
            lambda arclength: source_data(arclength / radius)[3]
            / (2.0 * math.pi),
            0.0,
            math.pi * radius,
            singular_arclength,
            log_scale=log_scale,
            order=meridian_order,
        )
        hypersingular = (
            sum(direct_hypersingular)
            + hypersingular_log
            + sum(image_hypersingular)
        )
        adjoint = sum(direct_adjoint) + adjoint_log + sum(image_adjoint)
        hbie = 0.5 * field_normal_derivative + hypersingular - adjoint
        cbie = (
            0.5 * source_data(field_theta)[2]
            + sum(direct_double_layer)
            + double_layer_log
            + sum(image_double_layer)
            - sum(direct_single_layer)
            - single_layer_log
            - sum(image_single_layer)
        )
        # With residuals as left minus right, Wu et al. Eq. (14) is C + beta*H.
        burton_miller = cbie + (1j / wave_number) * hbie
        return cbie, hbie, burton_miller

    azimuth_results = [residual(64, count) for count in (256, 512, 1_024)]
    azimuth_residuals = [
        (
            abs(result[0]) / abs(source_data(field_theta)[2]),
            abs(result[1]) / abs(field_normal_derivative),
            abs(result[2]) / abs(source_data(field_theta)[2]),
        )
        for result in azimuth_results
    ]
    for residual_index, threshold in ((0, 4e-6), (1, 1e-6), (2, 4e-6)):
        values = [result[residual_index] for result in azimuth_residuals]
        assert values[1] < values[0] / 4.0, values
        assert values[2] < values[1] / 4.0, values
        assert values[2] < threshold, values
    meridian_results = [residual(order, 1_024) for order in (32, 64, 128)]
    meridian_residuals = [
        (
            abs(result[0]) / abs(source_data(field_theta)[2]),
            abs(result[1]) / abs(field_normal_derivative),
            abs(result[2]) / abs(source_data(field_theta)[2]),
        )
        for result in meridian_results
    ]
    for residual_index, threshold in ((0, 1e-6), (1, 1e-6), (2, 4e-6)):
        values = [result[residual_index] for result in meridian_residuals]
        assert abs(values[2] - values[1]) < abs(values[1] - values[0]), values
        assert values[2] < threshold, values


def _off_equator_hbie_residuals(
    field_theta_degrees, *, meridian_orders=(128, 256, 512), direct_azimuth_samples=1_024
):
    from aura.fields._bem_singular import integrate_cauchy_principal_value_panel
    from aura.fields.numerical import gauss_legendre_rule

    radius = 0.025
    gap = 0.0001
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    center_height = radius + gap
    field_theta = math.radians(field_theta_degrees)
    field = (
        radius * math.sin(field_theta), 0.0,
        center_height + radius * math.cos(field_theta),
    )
    field_normal = (-math.sin(field_theta), -math.cos(field_theta))
    source_point = (0.0, 0.0, center_height)
    _, field_gradient, _ = neumann_half_space_green(
        field, source_point, wave_number_rad_m=wave_number
    )
    field_q = field_normal[0] * field_gradient[0] + field_normal[1] * field_gradient[2]
    field_ps = (
        math.cos(field_theta) * field_gradient[0]
        - math.sin(field_theta) * field_gradient[2]
    )
    log_scale = 8.0 * radius
    singular_arclength = radius * field_theta

    def source_data(theta):
        sine, cosine = math.sin(theta), math.cos(theta)
        point = (radius * sine, 0.0, center_height + radius * cosine)
        normal = (-sine, -cosine)
        pressure, gradient, _ = neumann_half_space_green(
            point, source_point, wave_number_rad_m=wave_number
        )
        q = normal[0] * gradient[0] + normal[1] * gradient[2]
        ps = cosine * gradient[0] - sine * gradient[2]
        return point, normal, pressure, q, ps

    def evaluate_identities(meridian_order, azimuth_samples):
        nodes, weights = gauss_legendre_rule(meridian_order)
        direct_hypersingular = []
        image_hypersingular = []
        direct_adjoint = []
        image_adjoint = []
        direct_double_layer = []
        image_double_layer = []
        direct_single_layer = []
        image_single_layer = []
        for lower, upper in ((0.0, field_theta), (field_theta, math.pi)):
            midpoint = 0.5 * (lower + upper)
            half_width = 0.5 * (upper - lower)
            for node, weight in zip(nodes, weights, strict=True):
                theta = midpoint + half_width * node
                point, normal, pressure, q, ps = source_data(theta)
                source_radius, source_height = point[0], point[2]
                offset = theta - field_theta
                logarithm = math.log(log_scale / abs(radius * offset))
                surface_weight = half_width * weight * radius * source_radius
                direct_maue, image_maue = integrate_neumann_ring_burton_miller_terms_zero_mode(
                    field[0], field[2], field_normal, source_radius, source_height,
                    normal, pressure_pa=pressure,
                    pressure_tangent_derivative_pa_m=ps,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=azimuth_samples,
                )
                direct_field_gradient, _ = integrate_helmholtz_ring_green_gradient_zero_mode(
                    field[0], field[2], source_radius, source_height,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=azimuth_samples,
                )
                direct_field_normal = (
                    field_normal[0] * direct_field_gradient[0]
                    + field_normal[1] * direct_field_gradient[1]
                )
                image_field_normal = _image_ring_field_normal_integral(
                    field[0], field[2], field_normal, source_radius, source_height,
                    wave_number, 2 * azimuth_samples,
                )
                _, direct_source_gradient = integrate_helmholtz_ring_green_gradient_zero_mode(
                    field[0], field[2], source_radius, source_height,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=azimuth_samples,
                )
                direct_green = integrate_helmholtz_ring_green_zero_mode(
                    field[0], field[2], source_radius, source_height,
                    wave_number_rad_m=wave_number,
                    azimuth_samples=azimuth_samples,
                )
                direct_source_normal = sum(
                    component * normal_component
                    for component, normal_component in zip(
                        direct_source_gradient, normal, strict=True
                    )
                )
                image_green, image_source_normal = _image_ring_integrals(
                    field[0], field[2], field_normal, source_radius, source_height,
                    normal, wave_number, 2 * azimuth_samples,
                )
                direct_hypersingular.append(
                    surface_weight * direct_maue
                    - half_width * weight * field_ps / (2.0 * math.pi * offset)
                    - half_width * weight * radius * wave_number**2 * pressure
                    * logarithm / (2.0 * math.pi)
                )
                image_hypersingular.append(surface_weight * image_maue)
                direct_adjoint.append(
                    surface_weight * q * direct_field_normal
                    - half_width * weight * q * logarithm / (4.0 * math.pi)
                )
                image_adjoint.append(surface_weight * q * image_field_normal)
                direct_double_layer.append(
                    surface_weight * pressure * direct_source_normal
                    - half_width * weight * pressure * logarithm / (4.0 * math.pi)
                )
                image_double_layer.append(surface_weight * pressure * image_source_normal)
                direct_single_layer.append(
                    surface_weight * q * direct_green
                    - half_width * weight * radius * q * logarithm / (2.0 * math.pi)
                )
                image_single_layer.append(surface_weight * q * image_green)

        cauchy = integrate_cauchy_principal_value_panel(
            lambda _: field_ps,
            0.0, math.pi, field_theta, order=min(meridian_order, 256),
        )
        hypersingular_log = integrate_logarithmic_panel(
            lambda arclength: wave_number**2
            * source_data(arclength / radius)[2] / (2.0 * math.pi),
            0.0, math.pi * radius, singular_arclength,
            log_scale=log_scale, order=min(meridian_order, 256),
        )
        adjoint_log = integrate_logarithmic_panel(
            lambda arclength: source_data(arclength / radius)[3]
            / (4.0 * math.pi * radius),
            0.0, math.pi * radius, singular_arclength,
            log_scale=log_scale, order=min(meridian_order, 256),
        )
        double_layer_log = integrate_logarithmic_panel(
            lambda arclength: source_data(arclength / radius)[2]
            / (4.0 * math.pi * radius),
            0.0, math.pi * radius, singular_arclength,
            log_scale=log_scale, order=min(meridian_order, 256),
        )
        single_layer_log = integrate_logarithmic_panel(
            lambda arclength: source_data(arclength / radius)[3]
            / (2.0 * math.pi),
            0.0, math.pi * radius, singular_arclength,
            log_scale=log_scale, order=min(meridian_order, 256),
        )

        def compensated(values):
            return complex(
                math.fsum(value.real for value in values),
                math.fsum(value.imag for value in values),
            )

        cbie_direct = (
            0.5 * source_data(field_theta)[2]
            + compensated(direct_double_layer)
            + double_layer_log
            - compensated(direct_single_layer)
            - single_layer_log
        )
        cbie_image = compensated(image_double_layer) - compensated(image_single_layer)
        hbie_direct = (
            0.5 * field_q + compensated(direct_hypersingular) + cauchy
            + hypersingular_log - compensated(direct_adjoint) - adjoint_log
        )
        hbie_image = compensated(image_hypersingular) - compensated(image_adjoint)
        cbie = cbie_direct + cbie_image
        hbie = hbie_direct + hbie_image
        burton_miller_direct = cbie_direct + (1j / wave_number) * hbie_direct
        burton_miller_image = cbie_image + (1j / wave_number) * hbie_image
        burton_miller = burton_miller_direct + burton_miller_image
        return (
            cbie, hbie, burton_miller,
            cbie_direct, cbie_image, hbie_direct, hbie_image,
            burton_miller_direct, burton_miller_image,
        )

    # This local limit independently checks the singular coefficient and sign.
    local_ratios = []
    for delta in (math.radians(0.025), math.radians(0.0125), math.radians(0.00625)):
        theta = field_theta + delta
        point, normal, pressure, _, ps = source_data(theta)
        direct, _ = integrate_neumann_ring_burton_miller_terms_zero_mode(
            field[0], field[2], field_normal, point[0], point[2], normal,
            pressure_pa=pressure, pressure_tangent_derivative_pa_m=ps,
            wave_number_rad_m=wave_number, azimuth_samples=8192,
        )
        local_ratios.append(
            delta * radius * point[0] * direct / (field_ps / (2.0 * math.pi))
        )
    assert abs(local_ratios[-1] - 1.0) < abs(local_ratios[0] - 1.0), local_ratios
    assert abs(local_ratios[-1] - 1.0) < 0.03, local_ratios
    expected_constant_pv = field_ps * math.log((math.pi - field_theta) / field_theta) / (2.0 * math.pi)
    assert integrate_cauchy_principal_value_panel(
        lambda _: field_ps, 0.0, math.pi, field_theta, order=32
    ) == expected_constant_pv

    values = [
        evaluate_identities(order, direct_azimuth_samples)
        for order in meridian_orders
    ]
    cbie_scale = abs(source_data(field_theta)[2])
    residuals = [
        (
            abs(cbie) / cbie_scale,
            abs(hbie_value) / abs(field_q),
            abs(burton_miller) / cbie_scale,
            abs(cbie_direct) / cbie_scale,
            abs(cbie_image) / cbie_scale,
            abs(hbie_direct) / abs(field_q),
            abs(hbie_image) / abs(field_q),
            abs(burton_miller_direct) / cbie_scale,
            abs(burton_miller_image) / cbie_scale,
        )
        for (
            cbie, hbie_value, burton_miller,
            cbie_direct, cbie_image, hbie_direct, hbie_image,
            burton_miller_direct, burton_miller_image,
        ) in values
    ]
    if len(residuals) > 1:
        hbie_errors = [row[1] for row in residuals]
        assert all(right < left for left, right in pairwise(hbie_errors)), hbie_errors
    return residuals


@pytest.mark.parametrize("field_theta_degrees", [120.0, 135.0])
def test_off_equator_direct_cauchy_and_log_singular_coefficients(field_theta_degrees):
    """Check local direct Maue singular coefficients at two collocation angles."""
    radius = 0.025
    center_height = radius + 0.0001
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    field_theta = math.radians(field_theta_degrees)
    field = (
        radius * math.sin(field_theta), 0.0,
        center_height + radius * math.cos(field_theta),
    )
    field_normal = (-math.sin(field_theta), -math.cos(field_theta))
    source_point = (0.0, 0.0, center_height)
    _, field_gradient, _ = neumann_half_space_green(
        field, source_point, wave_number_rad_m=wave_number
    )
    field_tangent_derivative = (
        math.cos(field_theta) * field_gradient[0]
        - math.sin(field_theta) * field_gradient[2]
    )

    regularized = []
    predicted_log_coefficients = []
    cauchy_ratios = []
    offsets = (1.0e-3, 1.0e-4, 1.0e-5)
    for offset in offsets:
        theta = field_theta + offset
        source_radius = radius * math.sin(theta)
        source_height = center_height + radius * math.cos(theta)
        source_normal = (-math.sin(theta), -math.cos(theta))
        source = (source_radius, 0.0, source_height)
        pressure, source_gradient, _ = neumann_half_space_green(
            source, source_point, wave_number_rad_m=wave_number
        )
        source_tangent_derivative = (
            math.cos(theta) * source_gradient[0]
            - math.sin(theta) * source_gradient[2]
        )
        direct, _ = integrate_neumann_ring_burton_miller_terms_zero_mode(
            field[0], field[2], field_normal,
            source_radius, source_height, source_normal,
            pressure_pa=pressure,
            pressure_tangent_derivative_pa_m=source_tangent_derivative,
            wave_number_rad_m=wave_number,
            azimuth_samples=8_192,
        )
        weighted_direct = radius * source_radius * direct
        cauchy_ratios.append(
            weighted_direct * offset / (field_tangent_derivative / (2.0 * math.pi))
        )
        regularized.append(
            weighted_direct - field_tangent_derivative / (2.0 * math.pi * offset)
        )
        predicted_log_coefficients.append(radius * wave_number**2 * pressure / (2.0 * math.pi))

    assert abs(cauchy_ratios[-1] - 1.0) < abs(cauchy_ratios[0] - 1.0), cauchy_ratios
    assert abs(cauchy_ratios[-1] - 1.0) < 0.01, cauchy_ratios
    # Differencing across logarithmic scales removes the finite remainder
    # constant; the raw remainder/log ratio would therefore be biased.
    empirical_log_coefficient = (
        regularized[2] - regularized[1]
    ) / math.log(offsets[1] / offsets[2])
    assert empirical_log_coefficient == pytest.approx(
        predicted_log_coefficients[2], rel=0.04, abs=1e-7
    )


def _free_space_mixed_normal_hessian(field, source, field_normal, source_normal, wave_number):
    displacement = tuple(x - y for x, y in zip(field, source, strict=True))
    distance = math.sqrt(math.fsum(value * value for value in displacement))
    phase = cmath.exp(1j * wave_number * distance)
    coefficient = phase * complex(-1.0, wave_number * distance) / (4.0 * math.pi * distance**3)
    radial_derivative_over_distance = phase * (
        -wave_number**2 / distance**3
        - 3.0 * complex(-1.0, wave_number * distance) / distance**5
    ) / (4.0 * math.pi)
    normal_dot = math.fsum(a * b for a, b in zip(field_normal, source_normal, strict=True))
    field_projection = math.fsum(a * b for a, b in zip(field_normal, displacement, strict=True))
    source_projection = math.fsum(a * b for a, b in zip(source_normal, displacement, strict=True))
    return -coefficient * normal_dot - radial_derivative_over_distance * field_projection * source_projection


def _complex_dot(left, right):
    products = [a * b for a, b in zip(left, right, strict=True)]
    return complex(
        math.fsum(value.real for value in products),
        math.fsum(value.imag for value in products),
    )


@pytest.mark.parametrize("field_theta_degrees", [120.0, 135.0])
def test_off_equator_image_boundary_operators_match_independent_full_surface_integral(
    field_theta_degrees,
):
    """Compare image layers with surface quadrature and the exact image-source CBIE."""
    from aura.fields.numerical import gauss_legendre_rule

    radius = 0.025
    gap = 0.0001
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    center_height = radius + gap
    field_theta = math.radians(field_theta_degrees)
    field = (
        radius * math.sin(field_theta), 0.0,
        center_height + radius * math.cos(field_theta),
    )
    field_normal = (-math.sin(field_theta), 0.0, -math.cos(field_theta))
    source_point = (0.0, 0.0, center_height)
    nodes, weights = gauss_legendre_rule(64)

    ring_terms = [[], [], [], []]
    surface_terms = [[], [], [], []]
    ring_azimuth = 1_024
    surface_azimuth = 4_096
    image_azimuth_step = 2.0 * math.pi / surface_azimuth
    for node, weight in zip(nodes, weights, strict=True):
        theta = 0.5 * math.pi * (node + 1.0)
        point, normal_rz, pressure, normal_derivative = _sphere_data(
            theta, radius, center_height, source_point, wave_number
        )
        _, gradient, _ = neumann_half_space_green(
            point, source_point, wave_number_rad_m=wave_number
        )
        tangent_derivative = math.cos(theta) * gradient[0] - math.sin(theta) * gradient[2]
        source_radius, source_height = point[0], point[2]
        ring_weight = 0.5 * math.pi * weight * radius * source_radius
        _, image_maue = integrate_neumann_ring_burton_miller_terms_zero_mode(
            field[0], field[2], (field_normal[0], field_normal[2]),
            source_radius, source_height, normal_rz,
            pressure_pa=pressure,
            pressure_tangent_derivative_pa_m=tangent_derivative,
            wave_number_rad_m=wave_number,
            azimuth_samples=ring_azimuth,
        )
        image_green, image_source_normal = _image_ring_integrals(
            field[0], field[2], (field_normal[0], field_normal[2]),
            source_radius, source_height, normal_rz,
            wave_number, 2 * ring_azimuth,
        )
        image_field_normal = _image_ring_field_normal_integral(
            field[0], field[2], (field_normal[0], field_normal[2]),
            source_radius, source_height, wave_number, 2 * ring_azimuth,
        )
        ring_terms[0].append(ring_weight * pressure * image_source_normal)
        ring_terms[1].append(ring_weight * normal_derivative * image_green)
        # The Burton–Miller ring helper already applies the pressure density.
        ring_terms[2].append(ring_weight * image_maue)
        ring_terms[3].append(ring_weight * normal_derivative * image_field_normal)

        source_sine = math.sin(theta)
        surface_weight = 0.5 * math.pi * weight * radius**2 * source_sine
        for index in range(surface_azimuth):
            phi = (index + 0.5) * image_azimuth_step
            cosine_phi, sine_phi = math.cos(phi), math.sin(phi)
            image_point = (
                source_radius * cosine_phi,
                source_radius * sine_phi,
                -source_height,
            )
            image_normal = (
                normal_rz[0] * cosine_phi,
                normal_rz[0] * sine_phi,
                -normal_rz[1],
            )
            green, field_gradient = _free_space_term(field, image_point, wave_number)
            field_derivative = _complex_dot(field_normal, field_gradient)
            source_derivative = -_complex_dot(image_normal, field_gradient)
            mixed_normal = _free_space_mixed_normal_hessian(
                field, image_point, field_normal, image_normal, wave_number
            )
            angular_weight = surface_weight * image_azimuth_step
            surface_terms[0].append(angular_weight * pressure * source_derivative)
            surface_terms[1].append(angular_weight * normal_derivative * green)
            surface_terms[2].append(angular_weight * pressure * mixed_normal)
            surface_terms[3].append(angular_weight * normal_derivative * field_derivative)

    def compensated(terms):
        return complex(
            math.fsum(term.real for term in terms),
            math.fsum(term.imag for term in terms),
        )

    ring_values = tuple(compensated(terms) for terms in ring_terms)
    surface_values = tuple(compensated(terms) for terms in surface_terms)
    for label, ring_value, surface_value in zip(
        ("image double layer", "image single layer", "image hypersingular", "image adjoint"),
        ring_values,
        surface_values,
        strict=True,
    ):
        assert ring_value == pytest.approx(surface_value, rel=2e-8, abs=1e-5), (
            label, ring_values, surface_values
        )

    ring_cbie_image = ring_values[0] - ring_values[1]
    surface_cbie_image = surface_values[0] - surface_values[1]
    image_source = (0.0, 0.0, -center_height)
    image_distance = math.sqrt(
        math.fsum((coordinate - source) ** 2
                  for coordinate, source in zip(field, image_source, strict=True))
    )
    exact_image_source_pressure = cmath.exp(1j * wave_number * image_distance) / (
        4.0 * math.pi * image_distance
    )
    assert ring_cbie_image == pytest.approx(
        -exact_image_source_pressure, rel=2e-8, abs=1e-5
    )
    assert surface_cbie_image == pytest.approx(
        -exact_image_source_pressure, rel=2e-8, abs=1e-5
    )
    ring_hbie_image = ring_values[2] - ring_values[3]
    surface_hbie_image = surface_values[2] - surface_values[3]
    ring_bm_image = ring_cbie_image + (1j / wave_number) * ring_hbie_image
    surface_bm_image = surface_cbie_image + (1j / wave_number) * surface_hbie_image
    assert ring_bm_image == pytest.approx(surface_bm_image, rel=2e-8, abs=1e-5)


@pytest.mark.parametrize("field_theta_degrees", [120.0, 135.0])
def test_mirror_monopole_regular_modes_cancel_exact_image_cbie(field_theta_degrees):
    """Check the image addition theorem and direct-CBIE response mode by mode."""
    from aura.fields.numerical import spherical_bessel_jy

    radius = 0.025
    gap = 0.0001
    center_height = radius + gap
    mirror_distance = 2.0 * center_height
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    field_theta = math.radians(field_theta_degrees)
    field = (
        radius * math.sin(field_theta), 0.0,
        center_height + radius * math.cos(field_theta),
    )
    image_source = (0.0, 0.0, -center_height)
    image_distance = math.sqrt(
        math.fsum(
            (coordinate - source) ** 2
            for coordinate, source in zip(field, image_source, strict=True)
        )
    )
    exact_image_pressure = cmath.exp(1j * wave_number * image_distance) / (
        4.0 * math.pi * image_distance
    )

    cutoff_orders = (8, 16, 24, 32, 48, 64, 80)
    max_order = cutoff_orders[-1]
    legendre = [1.0, math.cos(field_theta)]
    for order in range(2, max_order + 1):
        legendre.append(
            ((2 * order - 1) * math.cos(field_theta) * legendre[-1]
             - (order - 1) * legendre[-2]) / order
        )

    regular_terms = []
    direct_cbie_terms = []
    for order in range(max_order + 1):
        j_surface, _, j_surface_prime, _ = spherical_bessel_jy(
            order, wave_number * radius
        )
        j_mirror, y_mirror, _, _ = spherical_bessel_jy(
            order, wave_number * mirror_distance
        )
        j_outgoing, y_outgoing, j_outgoing_prime, y_outgoing_prime = spherical_bessel_jy(
            order, wave_number * radius
        )
        h_mirror = complex(j_mirror, y_mirror)
        h_outgoing = complex(j_outgoing, y_outgoing)
        h_outgoing_prime = complex(j_outgoing_prime, y_outgoing_prime)
        # DLMF 10.60.1-2 combine into the outgoing Green expansion; the
        # mirror-source direction gives P_n(-cos(theta))=(-1)^n P_n(cos(theta)).
        angular_mode = (-1.0) ** order * legendre[order]
        coefficient = (
            1j * wave_number * (2 * order + 1) * h_mirror / (4.0 * math.pi)
        )
        trace = coefficient * j_surface * angular_mode
        source_normal_derivative = -coefficient * wave_number * j_surface_prime * angular_mode
        # Kreuzer (2024), Eqs. (4)-(5), for G=exp(i*k*r)/(4*pi*r);
        # AURA's inward source normal reverses the double-layer eigenvalue.
        single_layer_eigenvalue = (
            1j * wave_number * radius**2 * j_surface * h_outgoing
        )
        double_layer_eigenvalue_aura = -(
            0.5
            + 1j * wave_number**2 * radius**2 * h_outgoing_prime * j_surface
        )
        direct_cbie_response = (
            0.5 * trace
            + double_layer_eigenvalue_aura * trace
            - single_layer_eigenvalue * source_normal_derivative
        )
        regular_terms.append(trace)
        direct_cbie_terms.append(direct_cbie_response)

    assert max(
        abs(response - trace)
        for response, trace in zip(direct_cbie_terms, regular_terms, strict=True)
    ) < 5e-13

    def partial_sum(terms, order):
        return complex(
            math.fsum(value.real for value in terms[: order + 1]),
            math.fsum(value.imag for value in terms[: order + 1]),
        )

    errors = {
        order: abs(partial_sum(regular_terms, order) - exact_image_pressure)
        for order in cutoff_orders
    }
    remainder_bound = _mirror_mode_remainder_bound(80)
    direct_responses = {
        order: partial_sum(direct_cbie_terms, order)
        for order in cutoff_orders
    }
    assert errors[48] < errors[32]
    assert errors[48] < 1e-12
    assert errors[80] < 2.0 * float(remainder_bound)
    assert _mirror_mode_remainder_bound(64) > remainder_bound
    assert _mirror_mode_remainder_bound(48) > _mirror_mode_remainder_bound(64)
    # The independently integrated image contribution is -G_image at this point.
    assert abs(direct_responses[48] - exact_image_pressure) < 1e-12
    image_cbie_contribution = -exact_image_pressure
    assert abs(direct_responses[48] + image_cbie_contribution) < 1e-12


def test_neumann_half_space_hbie_identity_off_equator_at_135_degrees():
    """Check off-equator CBIE, HBIE and combined identities at 135 degrees."""
    residuals = _off_equator_hbie_residuals(135.0)
    expected = (1.3225926047676166e-7, 6.351118263974117e-7, 4.905087137967346e-7)
    assert all(
        math.isclose(actual, reference, rel_tol=0.02, abs_tol=0.0)
        for actual, reference in zip(residuals[-1][:3], expected, strict=True)
    ), residuals


def test_neumann_half_space_hbie_identity_off_equator_at_120_degrees():
    """Check off-equator CBIE, HBIE and combined identities at 120 degrees."""
    residuals = _off_equator_hbie_residuals(120.0)
    expected = (4.937849786500923e-7, 2.9436860283636453e-7, 8.199839373582927e-7)
    assert all(
        math.isclose(actual, reference, rel_tol=0.02, abs_tol=0.0)
        for actual, reference in zip(residuals[-1][:3], expected, strict=True)
    ), residuals


@pytest.mark.parametrize(
    ("angle", "expected_rows"),
    [
        (
            120.0,
            (
                (3.949694760669292e-6, 2.784420993735613e-6, 7.26738223859542e-6,
                 0.7017765978528487, 0.7017800768620652, 0.001320229313641898,
                 0.0013184259620687045, 0.7001600352317204, 0.7001658510963493),
                (4.93668826798954e-7, 5.376307466214797e-7, 5.999158568324642e-7,
                 0.7017796421507524, 0.7017800768620652, 0.0013179583527429988,
                 0.0013184259620687149, 0.7001659725677319, 0.7001658510963494),
                (6.175718068748198e-8, 7.519597408584152e-7, 8.712751864582464e-7,
                 0.7017800226086855, 0.7017800768620652, 0.0013176747317994995,
                 0.0013184259620687216, 0.7001667145728278, 0.7001658510963494),
                (7.776364042696666e-9, 7.867038301300109e-7, 9.579631353146122e-7,
                 0.7017800701634108, 0.7017800768620652, 0.0013176392688596496,
                 0.0013184259620687235, 0.7001668073370176, 0.7001658510963494),
                (1.0671904444316003e-9, 7.908166954354412e-7, 9.68750796797366e-7,
                 0.7017800761080029, 0.7017800768620652, 0.0013176351455070833,
                 0.0013184259620687194, 0.7001668185538669, 0.7001658510963494),
            ),
        ),
        (
            135.0,
            (
                (1.0555062268712306e-6, 3.488894600416531e-6, 3.0335306145697924e-6,
                 0.4342840011181034, 0.4342830672668493, 0.2175413889648748,
                 0.21754443764854314, 0.3112201223543772, 0.3112173752612869),
                (1.3212997321447874e-7, 1.933042821456014e-6, 1.2175761653207521e-6,
                 0.4342831844675028, 0.4342830672668493, 0.21754251624053425,
                 0.21754443764854314, 0.3112185896207854, 0.3112173752612869),
                (1.674909291668482e-8, 1.7807064009625795e-6, 1.0246370992182288e-6,
                 0.4342830824084701, 0.4342830672668493, 0.21754265713520807,
                 0.21754443764854317, 0.3112183980625059, 0.3112173752612869),
                (2.4231901699930135e-9, 1.7629679355230936e-6, 1.0020941454721342e-6,
                 0.43428306965176894, 0.4342830672668492, 0.21754267468320826,
                 0.21754443764854314, 0.31121837415451375, 0.31121737526128684),
                (8.91584219934213e-10, 1.7603346455588231e-6, 9.990576688036097e-7,
                 0.43428306805738, 0.4342830672668493, 0.21754267731390264,
                 0.21754443764854314, 0.3112183709193409, 0.3112173752612869),
            ),
        ),
    ],
)
def test_neumann_half_space_burton_miller_identity_off_equator_azimuth_refinement(
    angle, expected_rows
):
    """Check azimuth sensitivity and separate direct/image contributions."""
    actual_rows = [
        _off_equator_hbie_residuals(
            angle, meridian_orders=(256,), direct_azimuth_samples=count
        )[0]
        for count in (512, 1_024, 2_048, 4_096, 8_192)
    ]
    for actual, expected in zip(actual_rows, expected_rows, strict=True):
        assert all(
            math.isclose(value, reference, rel_tol=0.02, abs_tol=0.0)
            for value, reference in zip(actual, expected, strict=True)
        ), actual_rows


@pytest.mark.parametrize(
    ("angle", "expected"),
    [
        (
            120.0,
            (
                7.892578351213587e-9, 1.9156403853840462e-7, 2.283896164792989e-7,
                0.7017800700635318, 0.7017800768620654, 0.0013182344427522738,
                0.0013184259620688244, 0.7001660785299482, 0.7001658510963497,
            ),
        ),
        (
            135.0,
            (
                2.540759470737439e-9, 4.4020041011362665e-7, 2.5208797122025877e-7,
                0.4342830697562411, 0.4342830672668493, 0.21754399746011588,
                0.21754443764854306, 0.31121762669014175, 0.311217375261287,
            ),
        ),
    ],
)
def test_neumann_half_space_burton_miller_identity_off_equator_meridian_refinement(
    angle, expected
):
    """Check meridian refinement at fixed, high direct/image azimuth counts."""
    row = _off_equator_hbie_residuals(
        angle, meridian_orders=(512,), direct_azimuth_samples=4_096
    )[0]
    assert all(
        math.isclose(actual, reference, rel_tol=0.02, abs_tol=0.0)
        for actual, reference in zip(row, expected, strict=True)
    ), row
