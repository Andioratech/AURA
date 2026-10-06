import math
from itertools import pairwise

from aura.fields._bem_axisymmetric import (
    integrate_helmholtz_ring_green_gradient_zero_mode,
    integrate_helmholtz_ring_green_zero_mode,
)
from aura.fields._bem_green import _free_space_term, neumann_half_space_green
from aura.fields._bem_singular import integrate_logarithmic_panel


def _sphere_data(theta, radius, center_height, source, wave_number):
    sine, cosine = math.sin(theta), math.cos(theta)
    field = (radius * sine, 0.0, center_height + radius * cosine)
    normal_rz = (-sine, -cosine)
    pressure, gradient, _ = neumann_half_space_green(
        field, source, wave_number_rad_m=wave_number
    )
    normal_derivative = normal_rz[0] * gradient[0] + normal_rz[1] * gradient[2]
    return field, normal_rz, pressure, normal_derivative


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
