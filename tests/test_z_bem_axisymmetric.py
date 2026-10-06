import cmath
import math
from itertools import pairwise

import pytest

from aura.errors import InvalidInputError
from aura.fields._bem_axisymmetric import (
    _integrate_ring_image_mixed_normal,
    integrate_helmholtz_ring_green_gradient_zero_mode,
    integrate_helmholtz_ring_green_zero_mode,
    integrate_laplace_ring_green_cos_moment_zero_mode,
    integrate_laplace_ring_green_gradient_zero_mode,
    integrate_laplace_ring_green_zero_mode,
    integrate_laplace_ring_mixed_normal_zero_mode,
    integrate_neumann_ring_burton_miller_terms_zero_mode,
    integrate_neumann_ring_zero_mode,
)
from aura.fields._bem_green import (
    _free_space_mixed_normal_derivative,
    _free_space_term,
    neumann_half_space_green,
)


def test_zero_radius_source_ring_is_two_pi_times_point_green():
    field = (0.017, 0.0, 0.031)
    source_height = 0.012
    k = 9.0
    point, point_field_gradient, point_source_gradient = neumann_half_space_green(
        field, (0.0, 0.0, source_height), wave_number_rad_m=k
    )
    ring, field_gradient, source_gradient = integrate_neumann_ring_zero_mode(
        field[0], field[2], 0.0, source_height,
        wave_number_rad_m=k, azimuth_samples=64,
    )

    assert ring == pytest.approx(2 * math.pi * point, rel=3e-15, abs=2e-15)
    assert field_gradient[0] == pytest.approx(2 * math.pi * point_field_gradient[0], rel=3e-15, abs=2e-14)
    assert field_gradient[1] == pytest.approx(2 * math.pi * point_field_gradient[2], rel=3e-15, abs=2e-14)
    assert source_gradient[0] == pytest.approx(0j, abs=2e-14)
    assert source_gradient[1] == pytest.approx(2 * math.pi * point_source_gradient[2], rel=3e-15, abs=2e-14)


def test_laplace_ring_green_elliptic_form_matches_independent_azimuth_sum():
    field_radius, field_height = 0.023, 0.041
    source_radius, source_height = 0.006, 0.019
    expected = 0.0
    samples = 8192
    weight = 2 * math.pi / samples
    for index in range(samples):
        angle = -math.pi + (index + 0.5) * weight
        radius = math.sqrt(
            field_radius**2 + source_radius**2
            - 2 * field_radius * source_radius * math.cos(angle)
            + (field_height - source_height) ** 2
        )
        expected += weight / (4 * math.pi * radius)

    actual = integrate_laplace_ring_green_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    assert actual == pytest.approx(expected, rel=2e-15, abs=2e-15)


def test_laplace_ring_green_zero_radius_and_near_diagonal_limits():
    radius = 0.025
    height = 0.0002
    point_height = 0.0007
    actual = integrate_laplace_ring_green_zero_mode(0.0, height, 0.0, point_height)
    assert actual == pytest.approx(1 / (2 * abs(height - point_height)), rel=2e-15)

    separation_m = radius * math.radians(0.1)
    near_diagonal = integrate_laplace_ring_green_zero_mode(
        radius, 0.02, radius * math.cos(math.radians(0.1)),
        0.02 + separation_m,
    )
    assert math.isfinite(near_diagonal)
    assert near_diagonal > 0
    source_radius = radius * math.cos(math.radians(0.1))
    source_height = 0.02 + separation_m
    samples = 32_768
    weight = 2 * math.pi / samples
    angular_reference = 0.0
    for index in range(samples):
        angle = -math.pi + (index + 0.5) * weight
        distance = math.sqrt(
            radius**2 + source_radius**2 - 2 * radius * source_radius * math.cos(angle)
            + (0.02 - source_height) ** 2
        )
        angular_reference += weight / (4 * math.pi * distance)
    assert near_diagonal == pytest.approx(angular_reference, rel=5e-12, abs=2e-10)


def test_laplace_ring_green_rejects_meridional_diagonal():
    with pytest.raises(InvalidInputError, match="logarithmically singular"):
        integrate_laplace_ring_green_zero_mode(0.01, 0.02, 0.01, 0.02)


def test_laplace_ring_mixed_normal_elliptic_hessian_matches_pointwise_angular_sum():
    sphere_radius = 0.025
    gap = 0.0001
    field_theta = math.radians(175.0)
    source_theta = math.radians(175.1)
    args = (
        sphere_radius * math.sin(field_theta),
        gap + sphere_radius * (1.0 + math.cos(field_theta)),
        (-math.sin(field_theta), -math.cos(field_theta)),
        sphere_radius * math.sin(source_theta),
        gap + sphere_radius * (1.0 + math.cos(source_theta)),
        (-math.sin(source_theta), -math.cos(source_theta)),
    )
    exact_azimuth = integrate_laplace_ring_mixed_normal_zero_mode(*args)

    def independent_angular_sum(samples):
        field_radius, field_height, field_normal_rz, source_radius, source_height, source_normal_rz = args
        field = (field_radius, 0.0, field_height)
        field_normal = (field_normal_rz[0], 0.0, field_normal_rz[1])
        total = 0.0
        weight = 2.0 * math.pi / samples
        for index in range(samples):
            angle = 2.0 * math.pi * (index + 0.5) / samples
            cosine, sine = math.cos(angle), math.sin(angle)
            source = (source_radius * cosine, source_radius * sine, source_height)
            source_normal = (
                source_normal_rz[0] * cosine,
                source_normal_rz[0] * sine,
                source_normal_rz[1],
            )
            displacement = tuple(a - b for a, b in zip(field, source, strict=True))
            distance = math.hypot(*displacement)
            normal_dot = math.fsum(a * b for a, b in zip(field_normal, source_normal, strict=True))
            field_projection = math.fsum(a * b for a, b in zip(field_normal, displacement, strict=True))
            source_projection = math.fsum(a * b for a, b in zip(source_normal, displacement, strict=True))
            total += weight * (
                normal_dot / (4.0 * math.pi * distance**3)
                - 3.0 * field_projection * source_projection / (4.0 * math.pi * distance**5)
            )
        return total

    angular_32k = independent_angular_sum(32_768)
    angular_65k = independent_angular_sum(65_536)
    assert angular_32k == pytest.approx(angular_65k, rel=5e-14, abs=1e-3)
    assert exact_azimuth == pytest.approx(angular_65k, rel=3e-12, abs=1e-3)


def test_laplace_ring_cosine_moment_and_height_gradient_match_angular_sum():
    field_radius, field_height = 0.023, 0.041
    source_radius, source_height = 0.006, 0.019
    actual_moment, actual_height_gradient = integrate_laplace_ring_green_cos_moment_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    samples = 32_768
    moment = 0.0
    height_gradient = 0.0
    weight = 2.0 * math.pi / samples
    for index in range(samples):
        angle = 2.0 * math.pi * (index + 0.5) / samples
        cosine = math.cos(angle)
        distance = math.sqrt(
            (field_radius - source_radius * cosine) ** 2
            + (source_radius * math.sin(angle)) ** 2
            + (field_height - source_height) ** 2
        )
        moment += weight * cosine / (4.0 * math.pi * distance)
        height_gradient -= weight * cosine * (field_height - source_height) / (4.0 * math.pi * distance**3)
    assert actual_moment == pytest.approx(moment, rel=3e-14, abs=1e-14)
    assert actual_height_gradient == pytest.approx(height_gradient, rel=3e-13, abs=1e-12)

    axis_moment, axis_derivative = integrate_laplace_ring_green_cos_moment_zero_mode(
        0.0, field_height, 0.0, source_height
    )
    assert axis_moment == pytest.approx(0.0, abs=1e-15)
    assert axis_derivative == pytest.approx(0.0, abs=1e-15)


def test_surface_weighted_static_ring_has_logarithmic_local_asymptotic():
    sphere_radius = 0.025
    field_theta = math.radians(175.0)
    field_radius = sphere_radius * math.sin(field_theta)
    field_height = sphere_radius * (1.0 + math.cos(field_theta))
    relative_errors = []

    for offset_degrees in (0.1, 0.02, 0.01):
        source_theta = field_theta + math.radians(offset_degrees)
        source_radius = sphere_radius * math.sin(source_theta)
        source_height = sphere_radius * (1.0 + math.cos(source_theta))
        meridional_separation = sphere_radius * math.radians(offset_degrees)
        weighted_ring = source_radius * integrate_laplace_ring_green_zero_mode(
            field_radius, field_height, source_radius, source_height
        )
        leading_log = math.log(8.0 * field_radius / meridional_separation) / (2.0 * math.pi)
        relative_errors.append(abs(weighted_ring - leading_log) / leading_log)

    assert relative_errors[0] > relative_errors[1] > relative_errors[2]
    assert relative_errors[-1] < 0.002


@pytest.mark.parametrize(
    ("args",),
    [
        ((0.0, 0.02, (0.0, 1.0), 0.01, 0.01, (0.0, 1.0)),),
        ((0.02, 0.02, (1.0, 0.0), 0.0, 0.01, (0.0, 1.0)),),
    ],
)
def test_laplace_ring_mixed_normal_axis_limits(args):
    actual = integrate_laplace_ring_mixed_normal_zero_mode(*args)
    assert math.isfinite(actual)


def test_static_elliptic_derivatives_use_complementary_modulus_near_diagonal():
    radius = 0.01
    gap = 1e-12
    field_height = 0.02
    source_height = field_height + gap
    field_gradient, source_gradient = integrate_laplace_ring_green_gradient_zero_mode(
        radius, field_height, radius, source_height
    )
    mixed_normal = integrate_laplace_ring_mixed_normal_zero_mode(
        radius, field_height, (0.0, 1.0), radius, source_height, (0.0, 1.0)
    )

    # Leading logarithmic ring asymptotics as gap/radius tends to zero.
    gradient_scale = 1.0 / (2.0 * math.pi * radius * gap)
    mixed_scale = -1.0 / (2.0 * math.pi * radius * gap**2)
    assert field_gradient[1] == pytest.approx(gradient_scale, rel=1e-4)
    assert source_gradient[1] == pytest.approx(-gradient_scale, rel=1e-4)
    assert mixed_normal == pytest.approx(mixed_scale, rel=1e-4)


def test_ring_static_and_helmholtz_gradients_match_independent_angular_sums():
    sphere_radius = 0.025
    gap = 0.0001
    field_theta = math.radians(175.0)
    source_theta = math.radians(175.1)
    field_radius = sphere_radius * math.sin(field_theta)
    field_height = gap + sphere_radius * (1.0 + math.cos(field_theta))
    source_radius = sphere_radius * math.sin(source_theta)
    source_height = gap + sphere_radius * (1.0 + math.cos(source_theta))
    wave_number = 2.0 * math.pi * 25_230 / 346

    def angular_gradient(samples, *, dynamic):
        field = (field_radius, 0.0, field_height)
        field_total = [0j, 0j]
        source_total = [0j, 0j]
        weight = 2.0 * math.pi / samples
        for index in range(samples):
            angle = 2.0 * math.pi * (index + 0.5) / samples
            cosine, sine = math.cos(angle), math.sin(angle)
            source = (source_radius * cosine, source_radius * sine, source_height)
            displacement = tuple(a - b for a, b in zip(field, source, strict=True))
            distance = math.hypot(*displacement)
            if dynamic:
                _, gradient = _free_space_term(field, source, wave_number)
                field_gradient = (gradient[0], gradient[2])
                source_gradient = (
                    -gradient[0] * cosine - gradient[1] * sine,
                    -gradient[2],
                )
            else:
                factor = -1.0 / (4.0 * math.pi * distance**3)
                field_gradient = (factor * displacement[0], factor * displacement[2])
                source_gradient = (
                    -factor * (displacement[0] * cosine + displacement[1] * sine),
                    -factor * displacement[2],
                )
            for axis in range(2):
                field_total[axis] += weight * field_gradient[axis]
                source_total[axis] += weight * source_gradient[axis]
        return tuple(field_total), tuple(source_total)

    static_actual = integrate_laplace_ring_green_gradient_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    static_expected = angular_gradient(32_768, dynamic=False)
    assert static_actual[0] == pytest.approx(static_expected[0], rel=3e-12, abs=1e-4)
    assert static_actual[1] == pytest.approx(static_expected[1], rel=3e-12, abs=1e-4)

    helmholtz_actual = integrate_helmholtz_ring_green_gradient_zero_mode(
        field_radius, field_height, source_radius, source_height,
        # At 512 points the finite-grid difference remained about 5e-9; 1024
        # resolves this selected pair more closely but is not a global rule.
        wave_number_rad_m=wave_number, azimuth_samples=1024,
    )
    helmholtz_expected = angular_gradient(32_768, dynamic=True)
    assert helmholtz_actual[0] == pytest.approx(helmholtz_expected[0], rel=2e-11, abs=1e-4)
    assert helmholtz_actual[1] == pytest.approx(helmholtz_expected[1], rel=2e-11, abs=1e-4)


def test_helmholtz_ring_static_singularity_split_improves_near_diagonal_sum():
    sphere_radius = 0.025
    angular_offset = math.radians(0.1)
    field_radius = sphere_radius
    source_radius = sphere_radius * math.cos(angular_offset)
    field_height = 0.02
    source_height = field_height + sphere_radius * angular_offset
    wave_number = 2 * math.pi * 25_230 / 346

    def direct_midpoint(samples):
        total = 0j
        weight = 2 * math.pi / samples
        for index in range(samples):
            angle = 2 * math.pi * (index + 0.5) / samples
            distance = math.sqrt(
                (field_radius - source_radius) ** 2
                + 4 * field_radius * source_radius * math.sin(angle / 2) ** 2
                + (field_height - source_height) ** 2
            )
            total += weight * cmath.exp(1j * wave_number * distance) / (4 * math.pi * distance)
        return total

    reference = direct_midpoint(32_768)
    ordinary_64 = direct_midpoint(64)
    split_64 = integrate_helmholtz_ring_green_zero_mode(
        field_radius,
        field_height,
        source_radius,
        source_height,
        wave_number_rad_m=wave_number,
        azimuth_samples=64,
    )
    split_128 = integrate_helmholtz_ring_green_zero_mode(
        field_radius,
        field_height,
        source_radius,
        source_height,
        wave_number_rad_m=wave_number,
        azimuth_samples=128,
    )
    assert abs(split_64 - reference) < abs(ordinary_64 - reference) / 50
    assert abs(split_128 - reference) < abs(split_64 - reference)


def test_ring_green_matches_independent_direct_and_image_quadrature():
    field_radius, field_height = 0.021, 0.044
    source_radius, source_height = 0.008, 0.019
    k = 17.0
    count = 512

    actual = integrate_neumann_ring_zero_mode(
        field_radius, field_height, source_radius, source_height,
        wave_number_rad_m=k, azimuth_samples=count,
    )[0]

    # Independent scalar expression for the free-space source and its plane image.
    expected = 0j
    for index in range(count):
        angle = 2.0 * math.pi * (index + 0.5) / count
        x = field_radius - source_radius * math.cos(angle)
        y = -source_radius * math.sin(angle)
        for dz in (field_height - source_height, field_height + source_height):
            radius = math.sqrt(x * x + y * y + dz * dz)
            expected += cmath.exp(1j * k * radius) / (4.0 * math.pi * radius)
    expected *= 2.0 * math.pi / count
    assert actual == pytest.approx(expected, rel=3e-15, abs=2e-14)


def test_gap_scaled_image_ring_quadrature_exploratory_minimum_gap_case():
    sphere_radius = 0.025
    gap = 0.0001
    wave_number = 2 * math.pi * 25_230 / 346
    field_theta = math.radians(175.0)
    source_theta = math.radians(175.1)
    field_radius = sphere_radius * math.sin(field_theta)
    field_height = gap + sphere_radius * (1 + math.cos(field_theta))
    source_radius = sphere_radius * math.sin(source_theta)
    source_height = gap + sphere_radius * (1 + math.cos(source_theta))
    field_normal = (-math.sin(field_theta), 0.0, -math.cos(field_theta))
    source_normal_rz = (-math.sin(source_theta), -math.cos(source_theta))

    def independent_midpoint(samples):
        total = 0j
        weight = 2 * math.pi / samples
        for index in range(samples):
            angle = -math.pi + (index + 0.5) * weight
            cosine, sine = math.cos(angle), math.sin(angle)
            image_normal = (
                source_normal_rz[0] * cosine,
                source_normal_rz[0] * sine,
                -source_normal_rz[1],
            )
            total += weight * _free_space_mixed_normal_derivative(
                (field_radius, 0.0, field_height),
                (source_radius * cosine, source_radius * sine, -source_height),
                field_normal,
                image_normal,
                wave_number,
            )
        return total

    reference_65k = independent_midpoint(65_536)
    reference_131k = independent_midpoint(131_072)
    assert abs(reference_131k - reference_65k) < 5e-6

    def evaluate(samples, rule, split_multiple=8.0):
        return _integrate_ring_image_mixed_normal(
            field_radius,
            field_height,
            field_normal,
            source_radius,
            source_height,
            source_normal_rz,
            1.0 + 0j,
            wave_number,
            samples,
            rule,
            split_multiple,
        )

    midpoint_16 = evaluate(16, "midpoint")
    scaled_16 = evaluate(16, "gap_scaled", 2.0)
    assert abs(scaled_16 - reference_131k) < abs(midpoint_16 - reference_131k) / 1000

    midpoint_64 = evaluate(64, "midpoint")
    scaled_64 = evaluate(64, "gap_scaled", 6.0)
    assert abs(scaled_64 - reference_131k) < abs(midpoint_64 - reference_131k) / 1000

    # The scaled rule is not uniformly better: at this case and N=128 the
    # periodic midpoint rule is more accurate than the split rule with L=6.
    midpoint_128 = evaluate(128, "midpoint")
    scaled_128 = evaluate(128, "gap_scaled", 6.0)
    assert abs(scaled_128 - reference_131k) > 2 * abs(midpoint_128 - reference_131k)


def test_smooth_ring_integral_agrees_with_independent_composite_simpson():
    field_radius, field_height = 0.021, 0.044
    source_radius, source_height = 0.008, 0.019
    k = 17.0
    midpoint = integrate_neumann_ring_zero_mode(
        field_radius, field_height, source_radius, source_height,
        wave_number_rad_m=k, azimuth_samples=128,
    )[0]

    def direct_plus_image(angle):
        dx = field_radius - source_radius * math.cos(angle)
        dy = -source_radius * math.sin(angle)
        result = 0j
        for dz in (field_height - source_height, field_height + source_height):
            radius = math.sqrt(dx * dx + dy * dy + dz * dz)
            result += cmath.exp(1j * k * radius) / (4.0 * math.pi * radius)
        return result

    panels = 2048
    step = 2.0 * math.pi / panels
    simpson = direct_plus_image(0.0) + direct_plus_image(2.0 * math.pi)
    for index in range(1, panels):
        simpson += (4 if index % 2 else 2) * direct_plus_image(index * step)
    simpson *= step / 3.0

    assert midpoint == pytest.approx(simpson, rel=2e-13, abs=2e-13)


def test_ring_kernel_reciprocity_and_field_source_gradient_agreement():
    args = (0.026, 0.041, 0.009, 0.017)
    k = 23.0
    value, field_gradient, source_gradient = integrate_neumann_ring_zero_mode(
        *args, wave_number_rad_m=k, azimuth_samples=256
    )
    reverse, reverse_field_gradient, reverse_source_gradient = integrate_neumann_ring_zero_mode(
        args[2], args[3], args[0], args[1], wave_number_rad_m=k, azimuth_samples=256
    )

    assert value == pytest.approx(reverse, rel=2e-14, abs=2e-14)
    assert field_gradient == pytest.approx(reverse_source_gradient, rel=2e-13, abs=2e-12)
    assert source_gradient == pytest.approx(reverse_field_gradient, rel=2e-13, abs=2e-12)


def test_ring_integral_field_derivatives_match_centered_differences():
    args = [0.024, 0.043, 0.007, 0.016]
    k = 15.0
    step = 1e-7
    result = integrate_neumann_ring_zero_mode(*args, wave_number_rad_m=k, azimuth_samples=512)
    for parameter, derivative in ((0, result[1][0]), (1, result[1][1])):
        lower, upper = args.copy(), args.copy()
        lower[parameter] -= step
        upper[parameter] += step
        p_lower = integrate_neumann_ring_zero_mode(
            *lower, wave_number_rad_m=k, azimuth_samples=512
        )[0]
        p_upper = integrate_neumann_ring_zero_mode(
            *upper, wave_number_rad_m=k, azimuth_samples=512
        )[0]
        assert derivative == pytest.approx((p_upper - p_lower) / (2 * step), rel=2e-8, abs=2e-7)


def test_burton_miller_ring_terms_zero_radius_limit_and_image_separation():
    field = (0.021, 0.0, 0.044)
    source_height = 0.019
    k = 17.0
    pressure = 2.0 - 0.5j
    direct, image = integrate_neumann_ring_burton_miller_terms_zero_mode(
        field[0], field[2], (0.0, 1.0), 0.0, source_height, (0.0, 1.0),
        pressure_pa=pressure, pressure_tangent_derivative_pa_m=0j,
        wave_number_rad_m=k, azimuth_samples=64,
    )
    radius = math.dist(field, (0.0, 0.0, source_height))
    free_green = cmath.exp(1j * k * radius) / (4.0 * math.pi * radius)
    expected_direct = 2.0 * math.pi * (k * k) * pressure * free_green
    assert direct == pytest.approx(expected_direct, rel=4e-15, abs=2e-12)
    assert image != 0j


def test_maue_static_split_matches_independent_full_kernel_near_diagonal():
    sphere_radius = 0.025
    gap = 0.0001
    field_theta = math.radians(175.0)
    source_theta = math.radians(175.1)
    field_radius = sphere_radius * math.sin(field_theta)
    field_height = gap + sphere_radius * (1.0 + math.cos(field_theta))
    source_radius = sphere_radius * math.sin(source_theta)
    source_height = gap + sphere_radius * (1.0 + math.cos(source_theta))
    field_normal = (-math.sin(field_theta), 0.0, -math.cos(field_theta))
    source_normal_rz = (-math.sin(source_theta), -math.cos(source_theta))
    pressure = 1.2 - 0.3j
    pressure_tangent_derivative = 0.8 + 0.2j
    wave_number = 2.0 * math.pi * 25_230 / 346

    def independent_full_kernel(samples):
        total = 0j
        weight = 2.0 * math.pi / samples
        for index in range(samples):
            angle = 2.0 * math.pi * (index + 0.5) / samples
            cosine, sine = math.cos(angle), math.sin(angle)
            source_normal = (
                source_normal_rz[0] * cosine,
                source_normal_rz[0] * sine,
                source_normal_rz[1],
            )
            dx = field_radius - source_radius * cosine
            dy = -source_radius * sine
            dz = field_height - source_height
            radius = math.sqrt(dx * dx + dy * dy + dz * dz)
            green = cmath.exp(1j * wave_number * radius) / (4.0 * math.pi * radius)
            gradient_factor = green * (1j * wave_number - 1.0 / radius) / radius
            green_gradient = tuple(gradient_factor * value for value in (dx, dy, dz))
            source_tangent = (
                -source_normal_rz[1] * cosine,
                -source_normal_rz[1] * sine,
                source_normal_rz[0],
            )
            pressure_gradient = tuple(
                pressure_tangent_derivative * value for value in source_tangent
            )
            normal_dot = math.fsum(
                a * b for a, b in zip(field_normal, source_normal, strict=True)
            )
            field_cross_gradient = (
                field_normal[1] * green_gradient[2] - field_normal[2] * green_gradient[1],
                field_normal[2] * green_gradient[0] - field_normal[0] * green_gradient[2],
                field_normal[0] * green_gradient[1] - field_normal[1] * green_gradient[0],
            )
            source_cross_pressure = (
                source_normal[1] * pressure_gradient[2] - source_normal[2] * pressure_gradient[1],
                source_normal[2] * pressure_gradient[0] - source_normal[0] * pressure_gradient[2],
                source_normal[0] * pressure_gradient[1] - source_normal[1] * pressure_gradient[0],
            )
            tangential = sum(
                a * b for a, b in zip(
                    field_cross_gradient, source_cross_pressure, strict=True
                )
            )
            total += weight * (wave_number**2 * normal_dot * pressure * green + tangential)
        return total

    reference = independent_full_kernel(32_768)
    direct, _ = integrate_neumann_ring_burton_miller_terms_zero_mode(
        field_radius,
        field_height,
        (field_normal[0], field_normal[2]),
        source_radius,
        source_height,
        source_normal_rz,
        pressure_pa=pressure,
        pressure_tangent_derivative_pa_m=pressure_tangent_derivative,
        wave_number_rad_m=wave_number,
        azimuth_samples=1_024,
    )
    assert direct == pytest.approx(reference, rel=2e-11, abs=2e-4)


@pytest.mark.parametrize(
    ("gap", "field_angle_degrees", "degree"),
    [
        (0.0001, 175.0, 0),
        (0.0001, 179.0, 1),
        (0.0100, 170.0, 0),
        (0.0299, 179.0, 1),
    ],
)
def test_combined_direct_image_maue_ring_matches_independent_full_kernel(
    gap, field_angle_degrees, degree
):
    """Check the separated direct-Maue plus reflected-H kernel at sphere rings."""
    sphere_radius = 0.025
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    field_theta = math.radians(field_angle_degrees)
    source_theta = field_theta + math.radians(0.1)
    field_radius = sphere_radius * math.sin(field_theta)
    field_height = gap + sphere_radius * (1.0 + math.cos(field_theta))
    source_radius = sphere_radius * math.sin(source_theta)
    source_height = gap + sphere_radius * (1.0 + math.cos(source_theta))
    field_normal_rz = (-math.sin(field_theta), -math.cos(field_theta))
    source_normal_rz = (-math.sin(source_theta), -math.cos(source_theta))
    pressure = 1.0 if degree == 0 else math.cos(source_theta)
    pressure_tangent_derivative = (
        0.0 if degree == 0 else -math.sin(source_theta) / sphere_radius
    )

    direct, image = integrate_neumann_ring_burton_miller_terms_zero_mode(
        field_radius,
        field_height,
        field_normal_rz,
        source_radius,
        source_height,
        source_normal_rz,
        pressure_pa=pressure,
        pressure_tangent_derivative_pa_m=pressure_tangent_derivative,
        wave_number_rad_m=wave_number,
        azimuth_samples=1_024,
    )

    field = (field_radius, 0.0, field_height)
    field_normal = (field_normal_rz[0], 0.0, field_normal_rz[1])
    sample_count = 32_768
    angle_weight = 2.0 * math.pi / sample_count
    direct_terms = []
    image_terms = []
    for index in range(sample_count):
        angle = 2.0 * math.pi * (index + 0.5) / sample_count
        cosine, sine = math.cos(angle), math.sin(angle)
        source_normal = (
            source_normal_rz[0] * cosine,
            source_normal_rz[0] * sine,
            source_normal_rz[1],
        )
        source_tangent = (
            -source_normal_rz[1] * cosine,
            -source_normal_rz[1] * sine,
            source_normal_rz[0],
        )
        source = (source_radius * cosine, source_radius * sine, source_height)
        displacement = tuple(a - b for a, b in zip(field, source, strict=True))
        distance = math.hypot(*displacement)
        green = cmath.exp(1j * wave_number * distance) / (4.0 * math.pi * distance)
        gradient_factor = green * (1j * wave_number - 1.0 / distance) / distance
        green_gradient = tuple(gradient_factor * value for value in displacement)
        pressure_gradient = tuple(
            pressure_tangent_derivative * value for value in source_tangent
        )
        field_cross_gradient = (
            field_normal[1] * green_gradient[2] - field_normal[2] * green_gradient[1],
            field_normal[2] * green_gradient[0] - field_normal[0] * green_gradient[2],
            field_normal[0] * green_gradient[1] - field_normal[1] * green_gradient[0],
        )
        source_cross_pressure = (
            source_normal[1] * pressure_gradient[2] - source_normal[2] * pressure_gradient[1],
            source_normal[2] * pressure_gradient[0] - source_normal[0] * pressure_gradient[2],
            source_normal[0] * pressure_gradient[1] - source_normal[1] * pressure_gradient[0],
        )
        normal_dot = math.fsum(
            a * b for a, b in zip(field_normal, source_normal, strict=True)
        )
        direct_terms.append(
            angle_weight
            * (
                wave_number**2 * normal_dot * pressure * green
                + sum(a * b for a, b in zip(
                    field_cross_gradient, source_cross_pressure, strict=True
                ))
            )
        )

        image_normal = (source_normal[0], source_normal[1], -source_normal[2])
        image_terms.append(
            angle_weight
            * pressure
            * _free_space_mixed_normal_derivative(
                field,
                (source[0], source[1], -source[2]),
                field_normal,
                image_normal,
                wave_number,
            )
        )

    direct_reference = complex(
        math.fsum(term.real for term in direct_terms),
        math.fsum(term.imag for term in direct_terms),
    )
    image_reference = complex(
        math.fsum(term.real for term in image_terms),
        math.fsum(term.imag for term in image_terms),
    )
    assert direct == pytest.approx(direct_reference, rel=3e-10, abs=3e-4)
    assert image == pytest.approx(image_reference, rel=3e-10, abs=3e-4)
    assert direct + image == pytest.approx(
        direct_reference + image_reference, rel=3e-10, abs=6e-4
    )


def test_maue_tangential_ring_term_has_expected_local_cauchy_singularity():
    sphere_radius = 0.025
    field_theta = math.radians(175.0)
    field_radius = sphere_radius * math.sin(field_theta)
    field_height = sphere_radius * (1.0 + math.cos(field_theta))
    field_normal = (-math.sin(field_theta), -math.cos(field_theta))
    wave_number = 2.0 * math.pi * 25_230 / 346
    scaled_values = []

    for offset_degrees in (0.1, 0.05, 0.02):
        source_theta = field_theta + math.radians(offset_degrees)
        source_radius = sphere_radius * math.sin(source_theta)
        source_height = sphere_radius * (1.0 + math.cos(source_theta))
        source_normal = (-math.sin(source_theta), -math.cos(source_theta))
        meridional_separation = sphere_radius * math.radians(offset_degrees)
        direct, _ = integrate_neumann_ring_burton_miller_terms_zero_mode(
            field_radius,
            field_height,
            field_normal,
            source_radius,
            source_height,
            source_normal,
            pressure_pa=0j,
            pressure_tangent_derivative_pa_m=1.0 + 0j,
            wave_number_rad_m=wave_number,
            azimuth_samples=1_024,
        )
        scaled_values.append(meridional_separation * direct)

    leading_coefficient = 1.0 / (2.0 * math.pi * field_radius)
    assert scaled_values[-1].real == pytest.approx(leading_coefficient, rel=0.02)
    assert abs(scaled_values[-1].imag) < 0.01 * leading_coefficient
    assert abs(scaled_values[-1].real - leading_coefficient) < abs(
        scaled_values[0].real - leading_coefficient
    )


def test_burton_miller_ring_image_term_matches_independent_scalar_angular_sum():
    field_r, field_z = 0.024, 0.043
    source_r, source_z = 0.007, 0.016
    field_n = (0.6, 0.8)
    source_n = (-0.8, 0.6)
    pressure = 1.3 + 0.4j
    k = 15.0
    count = 128
    _, image = integrate_neumann_ring_burton_miller_terms_zero_mode(
        field_r, field_z, field_n, source_r, source_z, source_n,
        pressure_pa=pressure, pressure_tangent_derivative_pa_m=0.7 - 0.2j,
        wave_number_rad_m=k, azimuth_samples=count,
    )

    # Independent centered difference in the physical source-normal direction.
    step = 2e-7
    observed = 0j
    weight = 2.0 * math.pi / count
    n_field = (field_n[0], 0.0, field_n[1])
    for index in range(count):
        angle = 2 * math.pi * (index + 0.5) / count
        c, s = math.cos(angle), math.sin(angle)
        n_source = (source_n[0] * c, source_n[0] * s, source_n[1])
        base = (source_r * c, source_r * s, source_z)
        lower = tuple(x - step * n for x, n in zip(base, n_source, strict=True))
        upper = tuple(x + step * n for x, n in zip(base, n_source, strict=True))

        def field_normal_gradient(point):
            _, grad, _ = neumann_half_space_green(
                (field_r, 0.0, field_z), point, wave_number_rad_m=k
            )
            return sum(a * b for a, b in zip(n_field, grad, strict=True))

        def image_field_normal_gradient(point):
            # Differentiate the direct potential in the field-normal direction,
            # then remove it from the Neumann-kernel field-normal derivative.
            _, full_gradient, _ = neumann_half_space_green(
                (field_r, 0.0, field_z), point, wave_number_rad_m=k
            )
            displacement = tuple(a - b for a, b in zip((field_r, 0.0, field_z), point, strict=True))
            distance = math.dist((field_r, 0.0, field_z), point)
            factor = cmath.exp(1j * k * distance) * complex(-1.0, k * distance)
            direct_gradient = tuple(
                factor * d / (4.0 * math.pi * distance**3) for d in displacement
            )
            return sum(a * (b - c) for a, b, c in zip(n_field, full_gradient, direct_gradient, strict=True))

        observed += pressure * (
            image_field_normal_gradient(upper) - image_field_normal_gradient(lower)
        ) / (2 * step)
    observed *= weight
    assert image == pytest.approx(observed, rel=3e-7, abs=3e-5)


@pytest.mark.parametrize("degree", [0, 1])
@pytest.mark.parametrize("gap", [0.0001, 0.010, 0.020, 0.0299])
@pytest.mark.parametrize("field_angle_degrees", [120.0, 135.0, 150.0, 170.0, 175.0, 179.0])
def test_positive_gap_image_surface_integral_matches_independent_2d_quadrature(
    degree, gap, field_angle_degrees
):
    from aura.fields.numerical import gauss_legendre_rule

    sphere_radius = 0.025
    wave_number = 2.0 * math.pi * 25_230.0 / 346.0
    field_theta = math.radians(field_angle_degrees)
    field_radius = sphere_radius * math.sin(field_theta)
    field_height = gap + sphere_radius * (1.0 + math.cos(field_theta))
    field_normal = (-math.sin(field_theta), 0.0, -math.cos(field_theta))

    def axisymmetric_surface(order, azimuth_samples):
        nodes, weights = gauss_legendre_rule(order)
        result = 0j
        for node, weight in zip(nodes, weights, strict=True):
            theta = 0.5 * math.pi * (node + 1.0)
            sine, cosine = math.sin(theta), math.cos(theta)
            pressure = 1.0 if degree == 0 else cosine
            ring = _integrate_ring_image_mixed_normal(
                field_radius,
                field_height,
                field_normal,
                sphere_radius * sine,
                gap + sphere_radius * (1.0 + cosine),
                (-sine, -cosine),
                pressure + 0j,
                wave_number,
                azimuth_samples,
                "midpoint",
                8.0,
            )
            result += (
                0.5 * math.pi * weight * sphere_radius**2 * sine * ring
            )
        return result

    def direct_surface_split(order, azimuth_samples):
        # Integrate the complete reflected-source kernel on the sphere without
        # reducing the azimuth first. Split theta around the positive-gap peak.
        angular_scale = 2.0 * field_height / field_radius
        cutoff = 4.0 * angular_scale
        edges = (
            0.0,
            max(0.0, field_theta - cutoff),
            min(math.pi, field_theta + cutoff),
            math.pi,
        )
        nodes, weights = gauss_legendre_rule(order)
        azimuth_step = 2.0 * math.pi / azimuth_samples
        result = 0j
        for lower, upper in pairwise(edges):
            if upper <= lower:
                continue
            midpoint = 0.5 * (lower + upper)
            half_width = 0.5 * (upper - lower)
            for node, weight in zip(nodes, weights, strict=True):
                theta = midpoint + half_width * node
                theta_weight = half_width * weight
                sine, cosine = math.sin(theta), math.cos(theta)
                pressure = 1.0 if degree == 0 else cosine
                source_radius = sphere_radius * sine
                source_height = gap + sphere_radius * (1.0 + cosine)
                source_normal_r, source_normal_z = -sine, -cosine
                ring = 0j
                for index in range(azimuth_samples):
                    phi = (index + 0.5) * azimuth_step
                    cos_phi, sin_phi = math.cos(phi), math.sin(phi)
                    ring += azimuth_step * pressure * _free_space_mixed_normal_derivative(
                        (field_radius, 0.0, field_height),
                        (source_radius * cos_phi, source_radius * sin_phi, -source_height),
                        field_normal,
                        (
                            source_normal_r * cos_phi,
                            source_normal_r * sin_phi,
                            -source_normal_z,
                        ),
                        wave_number,
                    )
                result += (
                    theta_weight * sphere_radius**2 * sine * ring
                )
        return result

    if gap == 0.0001 and field_angle_degrees == 179.0:
        lower_order = direct_surface_split(256, 2_048)
        independent = direct_surface_split(512, 2_048)
        reduced = axisymmetric_surface(512, 1_024)
    elif gap == 0.0001 and field_angle_degrees >= 170.0:
        lower_order = direct_surface_split(128, 2_048)
        independent = direct_surface_split(256, 2_048)
        reduced = axisymmetric_surface(512, 1_024)
    elif gap == 0.0001 and field_angle_degrees in (120.0, 135.0):
        lower_order = axisymmetric_surface(64, 256)
        intermediate_order = axisymmetric_surface(64, 512)
        independent = direct_surface_split(64, 2_048)
        reduced = axisymmetric_surface(64, 1_024)
        # The independent route agrees to roundoff here, so strict monotonic
        # error reduction is not resolvable. Check successive azimuth stability.
        assert abs(intermediate_order - lower_order) < 1e-12
        assert abs(reduced - intermediate_order) < 1e-12
    else:
        lower_order = direct_surface_split(32, 256)
        independent = direct_surface_split(64, 512)
        reduced = axisymmetric_surface(64, 256)
    assert abs(independent - lower_order) / abs(independent) < 2e-5
    assert reduced == pytest.approx(independent, rel=2e-8, abs=1e-5)


def test_free_space_maue_identity_on_sphere_with_constant_density():
    # For constant density, the tangential-density term vanishes. The left
    # side is obtained from the exterior double-layer potential by the
    # divergence theorem and a radial Helmholtz solution in/out of the sphere.
    radius = 0.017
    kr = 2.3
    k = kr / radius
    j0 = math.sin(kr) / kr
    j0_prime = (kr * math.cos(kr) - math.sin(kr)) / (kr * kr)
    outgoing = cmath.exp(1j * kr) / radius
    outgoing_prime = cmath.exp(1j * kr) * (1j * kr - 1.0) / (radius * radius)

    # Match I(r)=integral_ball G(r,y)dV_y: inside -1/k^2 + A*j0(kr),
    # outside B*exp(ikr)/r. Continuity of I and dI/dr gives B.
    determinant = -j0 * outgoing_prime + outgoing * k * j0_prime
    exterior_volume_coefficient = -(k * j0_prime / (k * k)) / determinant
    lhs_hypersingular = -k * k * exterior_volume_coefficient * outgoing_prime

    # Surface integral of (n_P dot n_Q) G transforms with t=|P-Q|/a
    # into a/2 * integral_0^2 (1-t^2/2) exp(i*k*a*t) dt.
    phase = 1j * kr
    integral_exp = (cmath.exp(2 * phase) - 1) / phase
    integral_t2 = (
        cmath.exp(2 * phase) * (4 / phase - 4 / phase**2 + 2 / phase**3)
        - 2 / phase**3
    )
    surface_integral = radius / 2 * (integral_exp - integral_t2 / 2)
    rhs_maue = k * k * surface_integral
    assert lhs_hypersingular == pytest.approx(rhs_maue, rel=2e-13, abs=2e-11)


def test_free_space_maue_identity_on_sphere_with_degree_one_density():
    # p(Q)=cos(theta_Q) exercises the tangential-gradient term in Maue's
    # identity; the direct hypersingular side follows the l=1 sphere series.
    radius = 0.017
    kr = 2.3
    k = kr / radius
    j0 = math.sin(kr) / kr
    j1 = math.sin(kr) / (kr * kr) - math.cos(kr) / kr
    j1_prime = j0 - 2 * j1 / kr
    h0 = -1j * cmath.exp(1j * kr) / kr
    h1 = -cmath.exp(1j * kr) * (kr + 1j) / (kr * kr)
    h1_prime = h0 - 2 * h1 / kr
    lhs_hypersingular = 1j * k**3 * radius**2 * j1_prime * h1_prime

    # At the north pole, integrate the azimuth analytically and use
    # t=|P-Q|/a to make the Maue surface integrand a smooth 1-D function.
    panels = 4096
    step = 2 / panels
    weighted = 0j
    for index in range(panels + 1):
        t = index * step
        phase = kr * t
        oscillation = cmath.exp(1j * phase)
        mu = 1 - t * t / 2
        integrand = (
            k * k * radius / 2 * mu * mu * oscillation
            + oscillation * complex(-1, phase) * (1 - t * t / 4) / (2 * radius)
        )
        weight = 1 if index in (0, panels) else 4 if index % 2 else 2
        weighted += weight * integrand
    rhs_maue = step * weighted / 3
    assert lhs_hypersingular == pytest.approx(rhs_maue, rel=2e-12, abs=2e-10)


@pytest.mark.parametrize("degree", [0, 1])
def test_burton_miller_jump_and_coupling_match_exact_sphere_modes(degree):
    # Exact eigenvalues follow from the spherical addition theorem with
    # n_E directed out of the exterior fluid and into the rigid sphere.
    radius = 0.017
    kr = 2.3
    k = kr / radius
    j0 = math.sin(kr) / kr
    j1 = math.sin(kr) / (kr * kr) - math.cos(kr) / kr
    h0 = -1j * cmath.exp(1j * kr) / kr
    h1 = -cmath.exp(1j * kr) * (kr + 1j) / (kr * kr)
    if degree == 0:
        j, h = j0, h0
        j_prime, h_prime = -j1, -h1
    else:
        j, h = j1, h1
        j_prime = j0 - 2 * j1 / kr
        h_prime = h0 - 2 * h1 / kr

    # Single-layer V, principal double-layer K, hypersingular H, and
    # adjoint double-layer K' eigenvalues for the inward radial n_E.
    single = 1j * k * radius**2 * j * h
    double = 0.5 - 1j * k**2 * radius**2 * j_prime * h
    hyper = 1j * k**3 * radius**2 * j_prime * h_prime
    adjoint_double = -0.5 - 1j * k**2 * radius**2 * j * h_prime
    pressure = 1.0 + 0j
    normal_derivative = -k * h_prime / h * pressure

    assert (0.5 + double) * pressure == pytest.approx(
        single * normal_derivative, rel=3e-13, abs=3e-13
    )
    assert 0.5 * normal_derivative + hyper * pressure == pytest.approx(
        adjoint_double * normal_derivative, rel=3e-13, abs=3e-10
    )

    beta = 1j / k
    bm_left = (0.5 + double + beta * hyper) * pressure
    bm_right = (single + beta * adjoint_double - beta * 0.5) * normal_derivative
    assert bm_left == pytest.approx(bm_right, rel=4e-13, abs=4e-10)


@pytest.mark.parametrize(
    ("args", "count"),
    [
        ((0.01, 0.02, 0.01, 0.02), 64),
        ((-0.01, 0.02, 0.03, 0.04), 64),
        ((0.01, 0.02, 0.03, 0.04), 3),
        ((0.01, 0.02, 0.03, 0.04), 65_537),
    ],
)
def test_ring_integral_rejects_singular_geometry_and_invalid_quadrature(args, count):
    with pytest.raises(InvalidInputError):
        integrate_neumann_ring_zero_mode(*args, wave_number_rad_m=4.0, azimuth_samples=count)
