"""Focused checks for the truncated Hasegawa piston/rigid-sphere field."""

import math

import pytest


def _evaluate(points, *, order=80, workspace=2_000_000):
    from aura.fields.hasegawa import evaluate_hasegawa_piston_sphere_field

    return evaluate_hasegawa_piston_sphere_field(
        points,
        density_kg_m3=1.18,
        sound_speed_m_s=346.0,
        frequency_hz=25_230.0,
        piston_velocity_peak_m_s=1.0 + 0.25j,
        piston_radius_m=0.01,
        sphere_radius_m=0.025,
        sphere_center_distance_m=0.035,
        max_order=order,
        workspace_bytes=workspace,
    )


def test_coupled_field_matches_independent_unscaled_modal_sum():
    from aura.fields.numerical import (
        source_diffraction_coefficients,
        spherical_bessel_jy,
        spherical_legendre,
    )

    density, speed, frequency = 1.18, 346.0, 25_230.0
    omega = 2 * math.pi * frequency
    k = omega / speed
    radius, center, piston_radius = 0.025, 0.035, 0.01
    order = 36
    theta, azimuth = 0.73, 0.41
    radial = 0.030
    point = (
        radial * math.sin(theta) * math.cos(azimuth),
        radial * math.sin(theta) * math.sin(azimuth),
        center + radial * math.cos(theta),
    )
    factors = source_diffraction_coefficients(
        order, wave_number_rad_m=k, sphere_center_distance_m=center,
        piston_radius_m=piston_radius, quadrature_order=64, workspace_bytes=20_000_000,
    )
    phi = radial_derivative = theta_derivative = 0j
    cosine = math.cos(theta)
    for n, factor in enumerate(factors):
        j_a, _, jp_a, yp_a = spherical_bessel_jy(n, k * radius)
        del j_a
        coefficient = -jp_a / complex(jp_a, yp_a)
        j, y, jp, yp = spherical_bessel_jy(n, k * radial)
        total = complex(j, 0.0) + coefficient * complex(j, y)
        total_prime = complex(jp, 0.0) + coefficient * complex(jp, yp)
        legendre, derivative = spherical_legendre(n, cosine)
        weight = (2 * n + 1) * (-1) ** n * factor
        phi += weight * total * legendre / k
        radial_derivative += weight * total_prime * legendre
        theta_derivative -= weight * total * math.sin(theta) * derivative / k

    piston_velocity = 1.0 + 0.25j
    phi *= 1j * piston_velocity
    radial_derivative *= 1j * piston_velocity
    theta_derivative *= 1j * piston_velocity
    e_r = (math.sin(theta) * math.cos(azimuth), math.sin(theta) * math.sin(azimuth), math.cos(theta))
    e_theta = (math.cos(theta) * math.cos(azimuth), math.cos(theta) * math.sin(azimuth), -math.sin(theta))
    grad_phi = tuple(
        radial_derivative * er + theta_derivative / radial * et
        for er, et in zip(e_r, e_theta, strict=True)
    )
    expected_pressure = -1j * density * omega * phi
    expected_velocity = tuple(-value for value in grad_phi)
    expected_gradient = tuple(-1j * density * omega * value for value in grad_phi)

    actual = _evaluate([point], order=order)
    assert actual.pressure_pa[0] == pytest.approx(expected_pressure, rel=1e-10, abs=2e-12)
    assert actual.velocity_m_s[0] == pytest.approx(expected_velocity, rel=1e-10, abs=2e-12)
    assert actual.pressure_gradient_pa_m[0] == pytest.approx(expected_gradient, rel=1e-10, abs=2e-12)


def test_stationary_sphere_modal_kernel_overlaps_plane_wave_reference_including_n1():
    from aura.fields._plane_sphere_reference import evaluate_plane_wave_rigid_sphere_reference
    from aura.fields.hasegawa import _evaluate_stationary_sphere_modes

    density, speed, frequency, radius = 1.18, 346.0, 25_230.0, 0.025
    omega = 2 * math.pi * frequency
    k = omega / speed
    points = (
        (0.0, 0.0, radius),
        (radius * math.sqrt(3) / 2, 0.0, radius / 2),
        (0.0, 0.0, -radius),
    )
    # For exp(-iwt), p=-i*rho*omega*phi. A +z plane wave with
    # pressure amplitude rho*c therefore has phi amplitude i/k.
    phi_amplitude = 1j / k
    order = 32
    modal_potential = tuple(
        ((2 * n + 1) * phi_amplitude * 1j**n, 0)
        for n in range(order + 1)
    )
    prepared_points = tuple((point, point, math.hypot(*point)) for point in points)
    modal = _evaluate_stationary_sphere_modes(
        prepared_points,
        modal_potential_coefficients=modal_potential,
        density_kg_m3=density, sound_speed_m_s=speed, frequency_hz=frequency,
        sphere_radius_m=radius, max_order=order,
    )
    reference = evaluate_plane_wave_rigid_sphere_reference(
        points, density_kg_m3=density, sound_speed_m_s=speed,
        frequency_hz=frequency, peak_pressure_pa=density * speed,
        sphere_radius_m=radius, max_order=order, workspace_bytes=2_000_000,
    )
    for observed, expected in zip(modal.pressure_pa, reference.pressure_pa, strict=True):
        assert observed == pytest.approx(expected, rel=1e-10, abs=2e-10)
    for observed, expected in zip(modal.velocity_m_s, reference.velocity_m_s, strict=True):
        assert observed == pytest.approx(expected, rel=1e-10, abs=2e-10)
    for observed, expected in zip(modal.pressure_gradient_pa_m, reference.pressure_gradient_pa_m, strict=True):
        assert observed == pytest.approx(expected, rel=1e-10, abs=2e-10)


@pytest.mark.parametrize("sign", (-1, 1))
def test_coupled_field_satisfies_stationary_sphere_normal_velocity_at_poles(sign):
    from aura.fields.hasegawa import evaluate_hasegawa_piston_sphere_field

    center, radius = 0.0251, 0.025
    sample = (0.0, 0.0, center + sign * radius)
    field = evaluate_hasegawa_piston_sphere_field(
        [sample], density_kg_m3=1.18, sound_speed_m_s=346.0,
        frequency_hz=25_230.0, piston_velocity_peak_m_s=1.0,
        piston_radius_m=0.01, sphere_radius_m=radius,
        sphere_center_distance_m=center, max_order=100, workspace_bytes=1_000_000,
    )
    assert abs(field.velocity_m_s[0][2]) < 1e-14


def test_coupled_field_satisfies_sound_hard_boundary_off_axis():
    from aura.fields.hasegawa import evaluate_hasegawa_piston_sphere_field

    center, radius, theta = 0.0251, 0.025, math.radians(60)
    normal = (math.sin(theta), 0.0, math.cos(theta))
    sample = (radius * normal[0], 0.0, center + radius * normal[2])
    field = evaluate_hasegawa_piston_sphere_field(
        [sample], density_kg_m3=1.18, sound_speed_m_s=346.0,
        frequency_hz=25_230.0, piston_velocity_peak_m_s=1.0,
        piston_radius_m=0.01, sphere_radius_m=radius,
        sphere_center_distance_m=center, max_order=100, workspace_bytes=1_000_000,
    )
    normal_velocity = sum(
        component * direction
        for component, direction in zip(field.velocity_m_s[0], normal, strict=True)
    )
    assert abs(normal_velocity) < 1e-13


@pytest.mark.parametrize("sign", (-1, 1))
def test_minimum_gap_pole_pressure_is_stable_between_high_orders(sign):
    from aura.fields.hasegawa import evaluate_hasegawa_piston_sphere_field

    center, radius = 0.0251, 0.025
    sample = (0.0, 0.0, center + sign * radius)
    arguments = {
        "density_kg_m3": 1.18, "sound_speed_m_s": 346.0, "frequency_hz": 25_230.0,
        "piston_velocity_peak_m_s": 1.0, "piston_radius_m": 0.01,
        "sphere_radius_m": radius, "sphere_center_distance_m": center,
        "workspace_bytes": 2_000_000,
    }
    order_280 = evaluate_hasegawa_piston_sphere_field([sample], max_order=280, **arguments)
    order_300 = evaluate_hasegawa_piston_sphere_field([sample], max_order=300, **arguments)
    relative_change = abs(order_300.pressure_pa[0] - order_280.pressure_pa[0]) / abs(order_300.pressure_pa[0])
    # This is a recorded two-order diagnostic at the axial endpoints, not a
    # production tolerance or a bound over the full surface/gap domain.
    assert relative_change < 2e-11


def test_order_sequence_reports_changes_without_declaring_convergence():
    from aura.fields.hasegawa import evaluate_hasegawa_order_sequence

    sequence = evaluate_hasegawa_order_sequence(
        [(0.0, 0.0, 0.06)], orders=(12, 18, 24),
        density_kg_m3=1.18, sound_speed_m_s=346.0, frequency_hz=25_230.0,
        piston_velocity_peak_m_s=1.0, piston_radius_m=0.01,
        sphere_radius_m=0.025, sphere_center_distance_m=0.035,
        workspace_bytes=2_000_000,
    )
    assert tuple(comparison.order for comparison in sequence.comparisons) == (18, 24)
    assert all(comparison.max_relative_pressure_change >= 0 for comparison in sequence.comparisons)
    assert all(comparison.max_relative_velocity_change >= 0 for comparison in sequence.comparisons)
    assert all(comparison.max_relative_gradient_change >= 0 for comparison in sequence.comparisons)


def test_coupled_field_checks_resource_cap_before_scaled_source_work(monkeypatch):
    from aura.errors import InvalidInputError
    from aura.fields import hasegawa

    def forbidden(*args, **kwargs):
        raise AssertionError("Scaled source arrays must not be allocated before the workspace gate.")

    monkeypatch.setattr(hasegawa, "_scaled_source_diffraction_coefficients", forbidden)
    with pytest.raises(InvalidInputError, match="Need at least"):
        _evaluate([(0.0, 0.0, 0.06)], order=40, workspace=1)


def test_coupled_field_rejects_samples_outside_source_series_domain(monkeypatch):
    from aura.errors import InvalidInputError
    from aura.fields import hasegawa

    def forbidden(*args, **kwargs):
        raise AssertionError("Out-of-domain samples must fail before source arrays are constructed.")

    monkeypatch.setattr(hasegawa, "_scaled_source_diffraction_coefficients", forbidden)
    with pytest.raises(InvalidInputError, match="radius < sphere-center distance"):
        _evaluate([(0.0, 0.0, 0.071)], order=24)
