import math

import pytest

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields._bem_mesh import sphere_meridian_quadrature


def test_sphere_meridian_rule_reproduces_surface_moments_and_reflection_symmetry():
    radius = 0.025
    rows = sphere_meridian_quadrature(radius, panels=7, order_per_panel=16)

    area_without_azimuth = math.fsum(weight for _, weight in rows)
    first_axial_moment = math.fsum(weight * math.cos(theta) for theta, weight in rows)
    second_axial_moment = math.fsum(
        weight * math.cos(theta) ** 2 for theta, weight in rows
    )
    assert area_without_azimuth == pytest.approx(2.0 * radius**2, rel=2e-14, abs=1e-18)
    assert first_axial_moment == pytest.approx(0.0, abs=1e-18)
    assert second_axial_moment == pytest.approx(2.0 * radius**2 / 3.0, rel=2e-13, abs=1e-18)

    for (theta, weight), (reflected_theta, reflected_weight) in zip(
        rows, reversed(rows), strict=True
    ):
        assert theta + reflected_theta == pytest.approx(math.pi, abs=8 * math.ulp(math.pi))
        assert weight == pytest.approx(reflected_weight, rel=2e-13, abs=1e-18)


@pytest.mark.parametrize(
    ("radius", "panels", "order"),
    [
        (0.0, 1, 8),
        (math.nan, 1, 8),
        (True, 1, 8),
        (0.025, True, 8),
        (0.025, 1, 0),
        (0.025, 257, 256),
    ],
)
def test_sphere_meridian_rule_rejects_invalid_or_unbounded_inputs(radius, panels, order):
    with pytest.raises(InvalidInputError):
        sphere_meridian_quadrature(radius, panels=panels, order_per_panel=order)


@pytest.mark.parametrize("radius", [1e-200, 1e308])
def test_sphere_meridian_rule_rejects_nonrepresentable_surface_weights(radius):
    with pytest.raises(NumericalDomainError):
        sphere_meridian_quadrature(radius, panels=1, order_per_panel=2)
