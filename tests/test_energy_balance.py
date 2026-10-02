"""ANA-06 bounded acoustic energy audits; comparison is not physical acceptance."""

import json
import math
from dataclasses import replace
from decimal import Decimal, localcontext

import pytest
from interference_reference import reference as independent_coherent_reference

from aura.errors import InvalidInputError
from aura.fields import (
    PlaneWave,
    SphericalWave,
    evaluate_counterpropagating_pair,
    evaluate_plane_wave,
    evaluate_plane_wave_pair,
    evaluate_spherical_wave,
)
from aura.mclf.balances import (
    BALANCE_TOLERANCE,
    ENERGY_BALANCE_VERSION,
    EnergyBalanceResult,
    SphereSurfaceQuadrature,
    audit_closed_sphere_energy_balance,
    audit_spherical_shell_energy_balance,
    integrate_sphere_flux_w,
)

RHO, SPEED, FREQUENCY = 1000.0, 1500.0, 1_000_000.0
LAMBDA = SPEED / FREQUENCY
Z = RHO * SPEED
BOX = {"box_min_m": (-LAMBDA,) * 3, "box_max_m": (LAMBDA,) * 3}


def plane(direction):
    return PlaneWave(
        density_kg_m3=RHO,
        sound_speed_m_s=SPEED,
        frequency_hz=FREQUENCY,
        peak_pressure_pa=2.0,
        direction=direction,
        reference_m=(0, 0, 0),
        phase_rad=0,
        dynamic_viscosity_pa_s=0,
        amplitude_attenuation_per_m=0,
    )


def sample_plane(waves, surface):
    options = {**BOX, "workspace_bytes": 4096 * 6 + (8192 if len(waves) == 2 else 4096)}
    if len(waves) == 1:
        return evaluate_plane_wave(waves[0], surface.coordinates_m, **options)
    if waves[1].direction == tuple(-x for x in waves[0].direction):
        return evaluate_counterpropagating_pair(
            waves[0], waves[1], surface.coordinates_m, **options
        )
    return evaluate_plane_wave_pair(waves[0], waves[1], surface.coordinates_m, **options)


def scale_for(radius, amplitude_sum):
    return 4 * math.pi * radius**2 * amplitude_sum**2 / (2 * Z)


@pytest.mark.parametrize("kind", ["progressive", "opposed", "coherent"])
def test_source_free_closed_sphere_balances_against_independent_zero(kind, record_property):
    surface = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=LAMBDA / 4)
    first = plane((1, 0, 0))
    if kind == "progressive":
        waves, amplitude_sum = (first,), 2.0
    elif kind == "opposed":
        waves, amplitude_sum = (first, replace(first, direction=(-1, 0, 0))), 4.0
    else:
        waves, amplitude_sum = (first, replace(first, direction=(0, 1, 0))), 4.0
    field = sample_plane(waves, surface)
    result = audit_closed_sphere_energy_balance(
        field,
        surface,
        internal_source_power_w=0.0,
        absorbed_power_w=0.0,
        reference_power_scale_w=scale_for(surface.radius_m, amplitude_sum),
    )
    record_property("model_case", kind)
    record_property("boundary_power_w", json.dumps(result.boundary_power_w))
    record_property("normalized_error", result.normalized_error)
    assert result.contract == ENERGY_BALANCE_VERSION
    assert result.comparison == "PASS"
    assert abs(result.residual_power_w) / result.reference_scale_w <= BALANCE_TOLERANCE
    if kind == "progressive":
        expected_flux = [(Decimal(4) / Decimal(3_000_000), Decimal(0), Decimal(0))] * 6
    elif kind == "opposed":
        expected_flux = [(Decimal(0), Decimal(0), Decimal(0))] * 6
    else:
        case = {
            "first": {
                "density_kg_m3": RHO,
                "sound_speed_m_s": SPEED,
                "frequency_hz": FREQUENCY,
                "peak_pressure_pa": 2,
                "direction": [1, 0, 0],
                "reference_m": [0, 0, 0],
                "phase_rad": 0,
                "dynamic_viscosity_pa_s": 0,
                "amplitude_attenuation_per_m": 0,
            },
            "second": {
                "density_kg_m3": RHO,
                "sound_speed_m_s": SPEED,
                "frequency_hz": FREQUENCY,
                "peak_pressure_pa": 2,
                "direction": [0, 1, 0],
                "reference_m": [0, 0, 0],
                "phase_rad": 0,
                "dynamic_viscosity_pa_s": 0,
                "amplitude_attenuation_per_m": 0,
            },
            "coordinates_m": surface.coordinates_m,
        }
        expected_flux = independent_coherent_reference(case)["intensity"]
    with localcontext() as context:
        context.prec = 90
        expected_boundary = sum(
            (
                Decimal.from_float(weight)
                * sum(value * Decimal.from_float(normal[j]) for j, value in enumerate(vector))
                for weight, vector, normal in zip(
                    surface.area_weights_m2, expected_flux, surface.normals, strict=True
                )
            ),
            Decimal(0),
        )
    assert (
        abs(result.boundary_power_w[0] - float(expected_boundary)) / result.reference_scale_w
        <= BALANCE_TOLERANCE
    )
    # Linear energy conservation and the fixed antipodal equal-area rule give zero independently.
    assert abs(result.residual_power_w) <= result.tolerance_w


def spherical_wave():
    return SphericalWave(
        density_kg_m3=RHO,
        sound_speed_m_s=SPEED,
        frequency_hz=FREQUENCY,
        peak_pressure_pa=2.0,
        center_m=(0, 0, 0),
        reference_radius_m=LAMBDA / 4,
        minimum_radius_m=LAMBDA / 4,
        phase_rad=0,
        dynamic_viscosity_pa_s=0,
        amplitude_attenuation_per_m=0,
    )


def sample_sphere(wave, surface):
    return evaluate_spherical_wave(
        wave,
        surface.coordinates_m,
        box_min_m=BOX["box_min_m"],
        box_max_m=BOX["box_max_m"],
        workspace_bytes=4096 * 6 + 4096,
    )


def independent_spherical_power(radius):
    with localcontext() as context:
        context.prec = 80
        pi = Decimal(
            "3.141592653589793238462643383279502884197169399375105820974944592307816406286"
        )
        reference_radius = Decimal("0.000375")
        amplitude, impedance = Decimal(2), Decimal(1500000)
        r = Decimal.from_float(radius)
        intensity = amplitude**2 * reference_radius**2 / (2 * impedance * r**2)
        area = 4 * pi * r**2
        return float(area * intensity)


def test_spherical_exterior_shell_keeps_power_constant_on_independent_radii(record_property):
    wave = spherical_wave()
    inner = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=2 * wave.reference_radius_m)
    outer = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=2.5 * wave.reference_radius_m)
    inner_field, outer_field = sample_sphere(wave, inner), sample_sphere(wave, outer)
    inner_expected = independent_spherical_power(inner.radius_m)
    outer_expected = independent_spherical_power(outer.radius_m)
    scale = independent_spherical_power(wave.reference_radius_m)
    assert abs(inner_expected - outer_expected) / scale <= 2e-15
    result = audit_spherical_shell_energy_balance(
        outer_field,
        outer,
        inner_field,
        inner,
        internal_source_power_w=0.0,
        absorbed_power_w=0.0,
        reference_power_scale_w=scale,
    )
    record_property("outward_shell_power_w", result.boundary_power_w[0])
    record_property("inward_shell_power_w", result.boundary_power_w[1])
    record_property("reference_power_w", scale)
    record_property("normalized_error", result.normalized_error)
    assert result.comparison == "PASS"
    for observed, expected in zip(
        result.boundary_power_w, (outer_expected, -inner_expected), strict=True
    ):
        assert abs(observed - expected) / scale <= BALANCE_TOLERANCE
    assert abs(result.residual_power_w) / scale <= BALANCE_TOLERANCE


@pytest.mark.parametrize("missing", ["source", "absorption", "both"])
def test_missing_power_term_is_indeterminate_and_never_zero_filled(missing):
    surface = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=LAMBDA / 4)
    field = sample_plane((plane((1, 0, 0)),), surface)
    terms = {"internal_source_power_w": 0.0, "absorbed_power_w": 0.0}
    if missing in ("source", "both"):
        terms["internal_source_power_w"] = None
    if missing in ("absorption", "both"):
        terms["absorbed_power_w"] = None
    result = audit_closed_sphere_energy_balance(
        field, surface, **terms, reference_power_scale_w=scale_for(surface.radius_m, 2.0)
    )
    assert result.comparison == "INDETERMINATE"
    assert result.residual_power_w is None
    expected_terms = {
        "source": ("internal source power",),
        "absorption": ("absorbed power",),
        "both": ("internal source power", "absorbed power"),
    }[missing]
    assert all(term in result.diagnostic for term in expected_terms)
    assert (result.internal_source_power_w is None) == (missing in ("source", "both"))
    assert (result.absorbed_power_w is None) == (missing in ("absorption", "both"))


def test_inconsistent_flux_and_unreported_source_cannot_pass():
    wave = spherical_wave()
    inner = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=0.00075)
    outer = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=0.0009375)
    inner_field, outer_field = sample_sphere(wave, inner), sample_sphere(wave, outer)
    flipped = replace(
        outer_field, velocity_m_s=[tuple(-v for v in row) for row in outer_field.velocity_m_s]
    )
    failed = audit_spherical_shell_energy_balance(
        flipped,
        outer,
        inner_field,
        inner,
        internal_source_power_w=0.0,
        absorbed_power_w=0.0,
        reference_power_scale_w=scale_for(wave.reference_radius_m, 2.0),
    )
    assert failed.comparison == "FAIL"
    assert failed.normalized_error > BALANCE_TOLERANCE
    injected_source = audit_spherical_shell_energy_balance(
        outer_field,
        outer,
        inner_field,
        inner,
        internal_source_power_w=1e-12,
        absorbed_power_w=0.0,
        reference_power_scale_w=scale_for(wave.reference_radius_m, 2.0),
    )
    assert injected_source.comparison == "FAIL"


def test_surface_completeness_geometry_and_sample_link_fail_closed():
    surface = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=LAMBDA / 4)
    field = sample_plane((plane((1, 0, 0)),), surface)
    with pytest.raises(InvalidInputError, match="BALANCE_SAMPLES"):
        integrate_sphere_flux_w(
            replace(field, coordinates_m=field.coordinates_m[:-1] + ((0, 0, 0),)), surface
        )
    with pytest.raises(InvalidInputError, match="BALANCE_SURFACE"):
        audit_spherical_shell_energy_balance(
            field,
            surface,
            field,
            None,
            internal_source_power_w=0.0,
            absorbed_power_w=0.0,
            reference_power_scale_w=scale_for(surface.radius_m, 2.0),
        )
    inner = SphereSurfaceQuadrature(center_m=(0.0001, 0, 0), radius_m=0.0002)
    with pytest.raises(InvalidInputError, match="BALANCE_TOPOLOGY"):
        audit_spherical_shell_energy_balance(
            field,
            surface,
            field,
            inner,
            internal_source_power_w=0.0,
            absorbed_power_w=0.0,
            reference_power_scale_w=scale_for(surface.radius_m, 2.0),
        )
    mismatched_frequency = replace(field, frequency_hz=2 * FREQUENCY)
    concentric_inner = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=0.0002)
    with pytest.raises(InvalidInputError, match="BALANCE_FREQUENCY"):
        audit_spherical_shell_energy_balance(
            field,
            surface,
            mismatched_frequency,
            concentric_inner,
            internal_source_power_w=0.0,
            absorbed_power_w=0.0,
            reference_power_scale_w=scale_for(surface.radius_m, 2.0),
        )
    with pytest.raises(InvalidInputError, match="BALANCE_TOPOLOGY"):
        audit_spherical_shell_energy_balance(
            field,
            surface,
            field,
            surface,
            internal_source_power_w=0.0,
            absorbed_power_w=0.0,
            reference_power_scale_w=scale_for(surface.radius_m, 2.0),
        )


@pytest.mark.parametrize(
    "center,radius", [([0, 0], 1), ([True, 0, 0], 1), ((0, 0, 0), 0), ((float("nan"), 0, 0), 1)]
)
def test_surface_specification_rejects_bad_geometry(center, radius):
    with pytest.raises(InvalidInputError):
        SphereSurfaceQuadrature(center_m=center, radius_m=radius)


def test_energy_balance_result_rejects_forged_inconsistent_state():
    with pytest.raises(InvalidInputError):
        EnergyBalanceResult(
            contract=ENERGY_BALANCE_VERSION,
            control_volume="closed_sphere",
            comparison="PASS",
            boundary_power_w=(0.0,),
            internal_source_power_w=None,
            absorbed_power_w=0.0,
            residual_power_w=None,
            reference_scale_w=1.0,
            tolerance_w=1e-10,
            normalized_error=None,
            diagnostic=None,
        )


def test_surface_weights_close_area_and_keep_exact_antipodal_normals():
    surface = SphereSurfaceQuadrature(center_m=(0, 0, 0), radius_m=LAMBDA / 4)
    expected = 4 * math.pi * surface.radius_m**2
    assert surface.area_m2 == math.fsum(surface.area_weights_m2)
    assert abs(surface.area_m2 - expected) / expected <= 4 * math.ulp(1.0)
    assert all(
        n == tuple(-x for x in opposite)
        for n, opposite in zip(surface.normals[::2], surface.normals[1::2], strict=True)
    )
    assert all(
        tuple(-x for x in a) == b
        for a, b in zip(surface.coordinates_m[::2], surface.coordinates_m[1::2], strict=True)
    )
