"""Small SI calculations with explicit domains and input checks."""

from __future__ import annotations

import math

from aura.errors import InvalidInputError, NumericalDomainError


def _finite_scalar(name: str, value: float) -> float:
    if type(value) not in (int, float):
        raise InvalidInputError(
            "NUMBER_TYPE", f"/{name}", "Expected a real int or float, not coercion."
        )
    try:
        result = float(value)
    except OverflowError as exc:
        raise InvalidInputError(
            "NONFINITE", f"/{name}", "Operand exceeds finite binary64."
        ) from exc
    if not math.isfinite(result):
        raise InvalidInputError("NONFINITE", f"/{name}", "Operand must be finite in binary64.")
    return result


def _positive_finite(name: str, value: float) -> float:
    value = _finite_scalar(name, value)
    if value <= 0.0:
        raise InvalidInputError("VALUE_RANGE", f"/{name}", "Operand must be greater than zero.")
    return value


def _nonnegative_finite(name: str, value: float) -> float:
    value = _finite_scalar(name, value)
    if value < 0.0:
        raise InvalidInputError("VALUE_RANGE", f"/{name}", "Operand must be nonnegative.")
    return value


def _scaled_ratio(
    name: str, numerators: tuple[float, ...], denominators: tuple[float, ...] = ()
) -> float:
    """Evaluate checked finite factors without extreme intermediate products.

    Internal callers validate every operand, including nonzero denominators.
    Finite subnormals are allowed; overflow and a nonzero result rounded to zero
    fail explicitly. This does not guarantee correctly rounded multi-step algebra.
    """
    if any(value == 0.0 for value in numerators):
        sign = math.prod(math.copysign(1.0, value) for value in numerators + denominators)
        return math.copysign(0.0, sign)
    mantissa, exponent = 1.0, 0
    for factors, divide in ((numerators, False), (denominators, True)):
        for value in factors:
            fraction, power = math.frexp(value)
            mantissa = mantissa / fraction if divide else mantissa * fraction
            exponent += -power if divide else power
            mantissa, adjustment = math.frexp(mantissa)
            exponent += adjustment
    try:
        result = math.ldexp(mantissa, exponent)
    except OverflowError as exc:
        raise NumericalDomainError(
            "NUMERIC_RANGE", f"/{name}", "Result overflows binary64."
        ) from exc
    if not math.isfinite(result) or result == 0.0:
        raise NumericalDomainError(
            "NUMERIC_RANGE",
            f"/{name}",
            "Nonzero result is not finite or rounds to zero in binary64.",
        )
    return result


def wavelength_m(sound_speed_m_s: float, frequency_hz: float) -> float:
    """Return wavelength for a homogeneous medium and a positive frequency."""
    sound_speed_m_s = _positive_finite("sound_speed_m_s", sound_speed_m_s)
    frequency_hz = _positive_finite("frequency_hz", frequency_hz)
    return _scaled_ratio("wavelength_m", (sound_speed_m_s,), (frequency_hz,))


def wave_number_rad_m(sound_speed_m_s: float, frequency_hz: float) -> float:
    """Return the harmonic wave number, 2*pi/wavelength."""
    sound_speed_m_s = _positive_finite("sound_speed_m_s", sound_speed_m_s)
    frequency_hz = _positive_finite("frequency_hz", frequency_hz)
    return _scaled_ratio("wave_number_rad_m", (2.0, math.pi, frequency_hz), (sound_speed_m_s,))


def size_parameter_ka(radius_m: float, wavelength_m_value: float) -> float:
    """Return ka; this is a model-selection indicator, not a validity proof."""
    radius_m = _positive_finite("radius_m", radius_m)
    wavelength_m_value = _positive_finite("wavelength_m", wavelength_m_value)
    return _scaled_ratio("size_parameter_ka", (2.0, math.pi, radius_m), (wavelength_m_value,))


def plane_progressive_wave_intensity_w_m2(
    pressure_rms_pa: float,
    density_kg_m3: float,
    sound_speed_m_s: float,
) -> float:
    """Return I=p_rms^2/(rho*c) for a plane progressive wave in a fluid.

    This relation is not a general conversion for standing fields or cavities.
    The function name makes the assumed field regime part of the interface.
    """
    pressure_rms_pa = _nonnegative_finite("pressure_rms_pa", pressure_rms_pa)
    density_kg_m3 = _positive_finite("density_kg_m3", density_kg_m3)
    sound_speed_m_s = _positive_finite("sound_speed_m_s", sound_speed_m_s)
    return _scaled_ratio(
        "plane_progressive_wave_intensity_w_m2",
        (pressure_rms_pa, pressure_rms_pa),
        (density_kg_m3, sound_speed_m_s),
    )


def sinusoid_peak_to_rms(peak_amplitude: float) -> float:
    """Return RMS for a nonnegative peak magnitude of one zero-mean sinusoid."""
    peak_amplitude = _nonnegative_finite("peak_amplitude", peak_amplitude)
    return _scaled_ratio("sinusoid_peak_to_rms", (peak_amplitude,), (math.sqrt(2.0),))


def sinusoid_rms_to_peak(rms_amplitude: float) -> float:
    """Return peak magnitude for the RMS amplitude of one zero-mean sinusoid."""
    rms_amplitude = _nonnegative_finite("rms_amplitude", rms_amplitude)
    return _scaled_ratio("sinusoid_rms_to_peak", (rms_amplitude, math.sqrt(2.0)))


def radius_from_diameter_m(diameter_m: float) -> float:
    """Explicitly adapt a positive diameter in metres to a radius in metres."""
    diameter_m = _positive_finite("diameter_m", diameter_m)
    return _scaled_ratio("radius_from_diameter_m", (diameter_m,), (2.0,))


def amplitude_to_intensity_attenuation_per_m(amplitude_attenuation_per_m: float) -> float:
    """Convert exponential decay coefficients where intensity is proportional to A²."""
    alpha = _nonnegative_finite("amplitude_attenuation_per_m", amplitude_attenuation_per_m)
    return _scaled_ratio("amplitude_to_intensity_attenuation_per_m", (2.0, alpha))


def intensity_to_amplitude_attenuation_per_m(intensity_attenuation_per_m: float) -> float:
    """Invert the A² exponential-decay convention; not a decibel conversion."""
    alpha = _nonnegative_finite("intensity_attenuation_per_m", intensity_attenuation_per_m)
    return _scaled_ratio("intensity_to_amplitude_attenuation_per_m", (alpha,), (2.0,))
