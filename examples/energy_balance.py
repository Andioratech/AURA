"""Run the fixed, lossless ANA-06 energy-ledger examples."""

from __future__ import annotations

import json
import math
from dataclasses import replace

from aura.fields import (
    PlaneWave,
    SphericalWave,
    evaluate_counterpropagating_pair,
    evaluate_plane_wave,
    evaluate_plane_wave_pair,
    evaluate_spherical_wave,
)
from aura.mclf.balances import (
    SphereSurfaceQuadrature,
    audit_closed_sphere_energy_balance,
    audit_spherical_shell_energy_balance,
)

RHO_KG_M3 = 1000.0
SOUND_SPEED_M_S = 1500.0
FREQUENCY_HZ = 1_000_000.0
PEAK_PRESSURE_PA = 2.0
WAVELENGTH_M = SOUND_SPEED_M_S / FREQUENCY_HZ
IMPEDANCE_PA_S_M = RHO_KG_M3 * SOUND_SPEED_M_S
BOX = {"box_min_m": (-WAVELENGTH_M,) * 3, "box_max_m": (WAVELENGTH_M,) * 3}


def plane_wave(direction: tuple[int, int, int]) -> PlaneWave:
    return PlaneWave(
        density_kg_m3=RHO_KG_M3,
        sound_speed_m_s=SOUND_SPEED_M_S,
        frequency_hz=FREQUENCY_HZ,
        peak_pressure_pa=PEAK_PRESSURE_PA,
        direction=direction,
        reference_m=(0.0, 0.0, 0.0),
        phase_rad=0.0,
        dynamic_viscosity_pa_s=0.0,
        amplitude_attenuation_per_m=0.0,
    )


def sample_planes(waves: tuple[PlaneWave, ...], surface: SphereSurfaceQuadrature):
    options = {
        **BOX,
        "workspace_bytes": 4096 * 6 + (8192 if len(waves) == 2 else 4096),
    }
    if len(waves) == 1:
        return evaluate_plane_wave(waves[0], surface.coordinates_m, **options)
    if waves[1].direction == tuple(-axis for axis in waves[0].direction):
        return evaluate_counterpropagating_pair(waves[0], waves[1], surface.coordinates_m, **options)
    return evaluate_plane_wave_pair(waves[0], waves[1], surface.coordinates_m, **options)


def plane_audit(name: str, waves: tuple[PlaneWave, ...]) -> dict:
    surface = SphereSurfaceQuadrature(center_m=(0.0, 0.0, 0.0), radius_m=WAVELENGTH_M / 4)
    amplitude_sum_pa = math.fsum(wave.peak_pressure_pa for wave in waves)
    reference_power_w = (
        4 * math.pi * surface.radius_m**2 * amplitude_sum_pa**2 / (2 * IMPEDANCE_PA_S_M)
    )
    result = audit_closed_sphere_energy_balance(
        sample_planes(waves, surface),
        surface,
        internal_source_power_w=0.0,
        absorbed_power_w=0.0,
        reference_power_scale_w=reference_power_w,
    )
    return {"case": name, **result.to_dict()}


def spherical_shell_audit() -> dict:
    reference_radius_m = WAVELENGTH_M / 4
    wave = SphericalWave(
        density_kg_m3=RHO_KG_M3,
        sound_speed_m_s=SOUND_SPEED_M_S,
        frequency_hz=FREQUENCY_HZ,
        peak_pressure_pa=PEAK_PRESSURE_PA,
        center_m=(0.0, 0.0, 0.0),
        reference_radius_m=reference_radius_m,
        minimum_radius_m=reference_radius_m,
        phase_rad=0.0,
        dynamic_viscosity_pa_s=0.0,
        amplitude_attenuation_per_m=0.0,
    )
    inner = SphereSurfaceQuadrature(
        center_m=(0.0, 0.0, 0.0), radius_m=2 * reference_radius_m
    )
    outer = SphereSurfaceQuadrature(
        center_m=(0.0, 0.0, 0.0), radius_m=2.5 * reference_radius_m
    )
    options = {**BOX, "workspace_bytes": 4096 * 6 + 4096}
    inner_field = evaluate_spherical_wave(wave, inner.coordinates_m, **options)
    outer_field = evaluate_spherical_wave(wave, outer.coordinates_m, **options)
    reference_power_w = (
        4 * math.pi * reference_radius_m**2 * PEAK_PRESSURE_PA**2
        / (2 * IMPEDANCE_PA_S_M)
    )
    result = audit_spherical_shell_energy_balance(
        outer_field,
        outer,
        inner_field,
        inner,
        internal_source_power_w=0.0,
        absorbed_power_w=0.0,
        reference_power_scale_w=reference_power_w,
    )
    return {"case": "outgoing_spherical_shell", **result.to_dict()}


def main() -> None:
    first = plane_wave((1, 0, 0))
    cases = [
        plane_audit("progressive_plane", (first,)),
        plane_audit("equal_opposed_planes", (first, replace(first, direction=(-1, 0, 0)))),
        plane_audit("coherent_orthogonal_planes", (first, replace(first, direction=(0, 1, 0)))),
        spherical_shell_audit(),
    ]
    print(json.dumps({"scope": "ANA-06 model diagnostic only", "cases": cases}, indent=2))


if __name__ == "__main__":
    main()
