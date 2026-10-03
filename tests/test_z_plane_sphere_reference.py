"""Independent-source plane-wave/rigid-sphere checks for the future P4 solver."""

import cmath
import math

import pytest

from aura.errors import InvalidInputError


def evaluate(points, *, radius=0.025, k=None, frequency=25230.0, order=20, workspace=10_000_000):
    from aura.fields._plane_sphere_reference import evaluate_plane_wave_rigid_sphere_reference

    sound_speed = 346.0 if k is None else 2 * math.pi * frequency / k
    return evaluate_plane_wave_rigid_sphere_reference(
        points,
        density_kg_m3=1.18,
        sound_speed_m_s=sound_speed,
        frequency_hz=frequency,
        peak_pressure_pa=1.0,
        sphere_radius_m=radius,
        max_order=order,
        workspace_bytes=workspace,
    )


def test_plane_wave_sphere_reference_enforces_rigid_boundary_and_phasor_relation():
    radius = 0.025
    directions = ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.6, 0.0, 0.8))
    points = [tuple(radius * component for component in direction) for direction in directions]
    result = evaluate(points, order=20)
    rho_omega = 1.18 * 2 * math.pi * 25230.0

    for point, gradient, velocity in zip(
        result.coordinates_m, result.pressure_gradient_pa_m, result.velocity_m_s, strict=True
    ):
        normal = tuple(component / radius for component in point)
        normal_gradient = sum(value * component for value, component in zip(gradient, normal, strict=True))
        assert abs(normal_gradient) <= 2e-11 * max(1.0, *(abs(value) for value in gradient))
        for grad_component, velocity_component in zip(gradient, velocity, strict=True):
            assert grad_component == pytest.approx(1j * rho_omega * velocity_component, rel=2e-15, abs=1e-13)


def test_small_rigid_sphere_limit_recovers_incident_plane_wave():
    point = (0.05, -0.02, 0.03)
    result = evaluate([point], radius=1e-6, k=10.0, frequency=1000.0, order=18)
    expected = cmath.exp(1j * 10.0 * point[2])
    assert result.pressure_pa[0] == pytest.approx(expected, rel=3e-14, abs=2e-15)
    expected_velocity = expected / (1.18 * 2 * math.pi * 1000 / 10)
    assert result.velocity_m_s[0] == pytest.approx((0j, 0j, expected_velocity), rel=3e-13, abs=2e-15)
    assert result.pressure_gradient_pa_m[0] == pytest.approx(
        (0j, 0j, 10j * expected), rel=3e-13, abs=2e-13
    )


def test_plane_wave_sphere_reference_rejects_workspace_before_special_functions(monkeypatch):
    import aura.fields._plane_sphere_reference as reference

    def forbidden(*args, **kwargs):
        raise AssertionError("Special-function arrays must not be allocated before the workspace gate.")

    monkeypatch.setattr(reference, "_spherical_sequences", forbidden)
    with pytest.raises(InvalidInputError, match="FIELD_RESOURCE"):
        evaluate([(0.025, 0.0, 0.0)], workspace=1)


def test_plane_wave_sphere_reference_rejects_points_inside_sphere():
    with pytest.raises(InvalidInputError, match="FIELD_EXCLUSION"):
        evaluate([(0.024, 0.0, 0.0)])
