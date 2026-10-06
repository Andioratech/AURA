import cmath
import math

import pytest

from aura.errors import InvalidInputError
from aura.fields._bem_green import (
    neumann_half_space_green,
    neumann_half_space_mixed_normal_derivative,
)


def test_rigid_plane_neumann_condition_and_reciprocity():
    k = 7.25
    source = (0.013, -0.021, 0.037)
    value, field_gradient, source_gradient = neumann_half_space_green(
        (0.006, 0.004, 0.0), source, wave_number_rad_m=k
    )
    reverse_value, reverse_field_gradient, _ = neumann_half_space_green(
        source, (0.006, 0.004, 0.0), wave_number_rad_m=k
    )

    assert field_gradient[2] == pytest.approx(0j, abs=2e-14)
    assert value == pytest.approx(reverse_value, rel=2e-15, abs=1e-15)
    assert source_gradient == pytest.approx(reverse_field_gradient, rel=2e-14, abs=2e-14)


def test_image_kernel_matches_independent_direct_plus_mirror_sum():
    field = (0.019, -0.008, 0.031)
    source = (-0.004, 0.011, 0.017)
    k = 12.5

    actual, _, _ = neumann_half_space_green(field, source, wave_number_rad_m=k)

    expected = 0j
    for image_z in (source[2], -source[2]):
        radius = math.dist(field, (source[0], source[1], image_z))
        expected += cmath.exp(1j * k * radius) / (4.0 * math.pi * radius)
    assert actual == pytest.approx(expected, rel=2e-15, abs=1e-15)


def test_field_gradient_matches_centered_difference():
    field = (0.02, -0.01, 0.04)
    source = (0.0, 0.0, 0.015)
    k = 18.0
    _, gradient, _ = neumann_half_space_green(field, source, wave_number_rad_m=k)
    step = 1e-7
    for axis in range(3):
        lower = list(field)
        upper = list(field)
        lower[axis] -= step
        upper[axis] += step
        p_lower = neumann_half_space_green(tuple(lower), source, wave_number_rad_m=k)[0]
        p_upper = neumann_half_space_green(tuple(upper), source, wave_number_rad_m=k)[0]
        finite_difference = (p_upper - p_lower) / (2.0 * step)
        assert gradient[axis] == pytest.approx(finite_difference, rel=2e-8, abs=2e-7)


def test_mixed_normal_derivative_matches_source_direction_difference():
    field = (0.031, 0.0, 0.047)
    source = (0.009, 0.012, 0.018)
    field_normal = (0.6, 0.0, 0.8)
    source_normal = (-0.8, 0.0, 0.6)
    k = 21.0
    step = 2e-7
    analytic = neumann_half_space_mixed_normal_derivative(
        field, source, field_normal, source_normal, wave_number_rad_m=k
    )

    def field_normal_gradient(source_point):
        _, gradient, _ = neumann_half_space_green(field, source_point, wave_number_rad_m=k)
        return sum(a * b for a, b in zip(field_normal, gradient, strict=True))

    lower = tuple(y - step * n for y, n in zip(source, source_normal, strict=True))
    upper = tuple(y + step * n for y, n in zip(source, source_normal, strict=True))
    numeric = (field_normal_gradient(upper) - field_normal_gradient(lower)) / (2 * step)
    assert analytic == pytest.approx(numeric, rel=2e-8, abs=2e-7)


def test_mixed_normal_derivative_satisfies_rigid_plane_limit():
    assert neumann_half_space_mixed_normal_derivative(
        (0.014, 0.0, 0.0), (0.006, 0.0, 0.023),
        (0.0, 0.0, 1.0), (0.6, 0.0, 0.8), wave_number_rad_m=13.0,
    ) == pytest.approx(0j, abs=2e-13)


@pytest.mark.parametrize(
    ("field_normal", "source_normal"),
    [((0.0, 0.0, 2.0), (0.0, 0.0, 1.0)), ((0.0, 0.0, 1.0), (1.0, 0.0, 1.0))],
)
def test_mixed_normal_derivative_rejects_nonunit_normals(field_normal, source_normal):
    with pytest.raises(InvalidInputError):
        neumann_half_space_mixed_normal_derivative(
            (0.01, 0.0, 0.02), (0.03, 0.0, 0.04),
            field_normal, source_normal, wave_number_rad_m=10.0,
        )


@pytest.mark.parametrize(
    ("field", "source", "wave_number"),
    [
        ((0.0, 0.0), (0.0, 0.0, 1.0), 1.0),
        ((0.0, 0.0, -1.0), (0.0, 0.0, 1.0), 1.0),
        ((0.0, 0.0, 1.0), (0.0, 0.0, 1.0), 1.0),
        ((0.0, 0.0, 1.0), (0.0, 0.0, 2.0), 0.0),
    ],
)
def test_kernel_rejects_invalid_geometry_or_wave_number(field, source, wave_number):
    with pytest.raises(InvalidInputError):
        neumann_half_space_green(field, source, wave_number_rad_m=wave_number)
