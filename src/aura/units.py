"""Small SI calculations with explicit domains and input checks."""

from __future__ import annotations

import math


def _positive_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and greater than zero")
    return value


def wavelength_m(sound_speed_m_s: float, frequency_hz: float) -> float:
    """Return wavelength for a homogeneous medium and a positive frequency."""
    sound_speed_m_s = _positive_finite("sound_speed_m_s", sound_speed_m_s)
    frequency_hz = _positive_finite("frequency_hz", frequency_hz)
    return sound_speed_m_s / frequency_hz


def wave_number_rad_m(sound_speed_m_s: float, frequency_hz: float) -> float:
    """Return the harmonic wave number, 2*pi/wavelength."""
    sound_speed_m_s = _positive_finite("sound_speed_m_s", sound_speed_m_s)
    frequency_hz = _positive_finite("frequency_hz", frequency_hz)
    return 2.0 * math.pi * frequency_hz / sound_speed_m_s


def size_parameter_ka(radius_m: float, wavelength_m_value: float) -> float:
    """Return ka; this is a model-selection indicator, not a validity proof."""
    radius_m = _positive_finite("radius_m", radius_m)
    wavelength_m_value = _positive_finite("wavelength_m", wavelength_m_value)
    return 2.0 * math.pi * radius_m / wavelength_m_value


def plane_progressive_wave_intensity_w_m2(
    pressure_rms_pa: float,
    density_kg_m3: float,
    sound_speed_m_s: float,
) -> float:
    """Return I=p_rms^2/(rho*c) for a plane progressive wave in a fluid.

    This relation is not a general conversion for standing fields or cavities.
    The function name makes the assumed field regime part of the interface.
    """
    pressure_rms_pa = float(pressure_rms_pa)
    if not math.isfinite(pressure_rms_pa) or pressure_rms_pa < 0.0:
        raise ValueError("pressure_rms_pa must be finite and non-negative")
    density_kg_m3 = _positive_finite("density_kg_m3", density_kg_m3)
    sound_speed_m_s = _positive_finite("sound_speed_m_s", sound_speed_m_s)
    return pressure_rms_pa**2 / (density_kg_m3 * sound_speed_m_s)
