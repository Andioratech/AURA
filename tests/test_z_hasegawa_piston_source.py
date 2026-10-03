"""Independent Rayleigh-disk checks for the Hasegawa piston-only source series."""

import cmath
import math

import pytest


def _rayleigh_disk(rho, z, *, piston_radius, wavenumber, velocity, radial_intervals=512,
                  azimuth_count=512):
    """Integrate potential and its spatial gradient over a uniformly moving disk."""
    radial_step = piston_radius / radial_intervals
    azimuth_step = 2 * math.pi / azimuth_count
    totals = [[0.0, 0.0] for _ in range(3)]
    corrections = [[0.0, 0.0] for _ in range(3)]

    def add(index, value, weight):
        for component, part in enumerate((value.real * weight, value.imag * weight)):
            adjusted = part - corrections[index][component]
            updated = totals[index][component] + adjusted
            corrections[index][component] = (updated - totals[index][component]) - adjusted
            totals[index][component] = updated

    for radial_index in range(radial_intervals + 1):
        source_radius = radial_index * radial_step
        simpson_weight = (
            1 if radial_index in (0, radial_intervals)
            else 4 if radial_index % 2 else 2
        )
        radial_weight = simpson_weight * source_radius * radial_step / 3
        for azimuth_index in range(azimuth_count):
            azimuth = azimuth_index * azimuth_step
            delta_rho = rho - source_radius * math.cos(azimuth)
            delta_y = -source_radius * math.sin(azimuth)
            distance = math.hypot(math.hypot(delta_rho, delta_y), z)
            green = cmath.exp(1j * wavenumber * distance) / distance
            gradient_green = (
                green * (1j * wavenumber * distance - 1) / (distance * distance)
            )
            weight = velocity * radial_weight * azimuth_step / (2 * math.pi)
            add(0, green, weight)
            add(1, gradient_green * delta_rho, weight)
            add(2, gradient_green * z, weight)

    return tuple(complex(*components) for components in totals)


@pytest.mark.parametrize("gap", (0.0001, 0.03))
def test_hasegawa_piston_source_off_axis_field_matches_rayleigh(gap):
    from aura.fields.numerical import (
        source_diffraction_coefficients,
        spherical_bessel_jy,
        spherical_legendre,
    )

    density, speed, frequency = 1.18, 346.0, 25230.0
    omega = 2 * math.pi * frequency
    wavenumber = omega / speed
    piston_radius, sphere_radius, piston_velocity = 0.01, 0.025, 1.0
    center_distance = sphere_radius + gap
    theta = 2 * math.pi / 3
    rho = sphere_radius * math.sin(theta)
    z = center_distance + sphere_radius * math.cos(theta)
    max_order, quadrature_order = 240, 64
    factors = source_diffraction_coefficients(
        max_order,
        wave_number_rad_m=wavenumber,
        sphere_center_distance_m=center_distance,
        piston_radius_m=piston_radius,
        quadrature_order=quadrature_order,
        workspace_bytes=80_000_000,
    )

    potential_sum = radial_sum = angular_sum = 0j
    cosine = math.cos(theta)
    sine = math.sin(theta)
    for order, factor in enumerate(factors):
        bessel, _, derivative, _ = spherical_bessel_jy(order, wavenumber * sphere_radius)
        legendre, legendre_derivative = spherical_legendre(order, cosine)
        coefficient = (2 * order + 1) * (-1) ** order * factor
        potential_sum += coefficient * bessel * legendre
        radial_sum += coefficient * derivative * legendre
        angular_sum += coefficient * bessel * legendre_derivative

    potential = 1j * piston_velocity / wavenumber * potential_sum
    radial_derivative = 1j * piston_velocity * radial_sum
    angular_derivative = -1j * piston_velocity / wavenumber * sine * angular_sum
    gradient_rho = (
        sine * radial_derivative + cosine / sphere_radius * angular_derivative
    )
    gradient_z = (
        cosine * radial_derivative - sine / sphere_radius * angular_derivative
    )
    actual = (
        -1j * density * omega * potential,
        -gradient_rho,
        -gradient_z,
        -1j * density * omega * gradient_rho,
        -1j * density * omega * gradient_z,
    )

    rayleigh_potential, rayleigh_gradient_rho, rayleigh_gradient_z = _rayleigh_disk(
        rho,
        z,
        piston_radius=piston_radius,
        wavenumber=wavenumber,
        velocity=piston_velocity,
    )
    expected = (
        -1j * density * omega * rayleigh_potential,
        -rayleigh_gradient_rho,
        -rayleigh_gradient_z,
        -1j * density * omega * rayleigh_gradient_rho,
        -1j * density * omega * rayleigh_gradient_z,
    )
    for observed, reference in zip(actual, expected, strict=True):
        assert observed == pytest.approx(reference, rel=5e-9, abs=2e-10)
