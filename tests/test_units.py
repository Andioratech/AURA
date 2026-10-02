"""Known-answer checks for the initial SI calculation layer."""

import math
from decimal import Decimal, localcontext
from itertools import product

import pytest

from aura.errors import InvalidInputError, NumericalDomainError
from aura.units import (
    amplitude_to_intensity_attenuation_per_m,
    intensity_to_amplitude_attenuation_per_m,
    plane_progressive_wave_intensity_w_m2,
    radius_from_diameter_m,
    sinusoid_peak_to_rms,
    sinusoid_rms_to_peak,
    size_parameter_ka,
    wave_number_rad_m,
    wavelength_m,
)


def test_wavelength_and_wave_number_known_answer():
    wavelength = wavelength_m(343.0, 70.0)
    assert wavelength == pytest.approx(4.9)
    assert wave_number_rad_m(343.0, 70.0) == pytest.approx(2.0 * math.pi / 4.9)


def test_large_sphere_size_parameter_is_not_small_particle_regime():
    wavelength = wavelength_m(346.0, 25_230.0)
    assert size_parameter_ka(0.025, wavelength) == pytest.approx(11.46, rel=2e-3)


def test_progressive_wave_intensity_uses_rms_pressure():
    assert plane_progressive_wave_intensity_w_m2(2.0, 1.2, 343.0) == pytest.approx(
        4.0 / (1.2 * 343.0)
    )


@pytest.mark.parametrize(
    ("function", "args"),
    [
        (wavelength_m, (0.0, 1000.0)),
        (wavelength_m, (343.0, float("nan"))),
        (wave_number_rad_m, (343.0, -1.0)),
        (size_parameter_ka, (0.0, 1.0)),
        (plane_progressive_wave_intensity_w_m2, (-1.0, 1.2, 343.0)),
    ],
)
def test_invalid_physical_inputs_are_rejected(function, args):
    with pytest.raises(ValueError):
        function(*args)


@pytest.mark.parametrize(
    "function,args,expected",
    [
        (wavelength_m, (343, 70), 4.9),
        (wavelength_m, (1500, 1_000_000), 0.0015),
        (wave_number_rad_m, (2, 1), 3.141592653589793),
        (size_parameter_ka, (0.5, 2), 1.5707963267948966),
        (plane_progressive_wave_intensity_w_m2, (2, 2, 4), 0.5),
        (sinusoid_peak_to_rms, (2,), 1.4142135623730951),
        (sinusoid_rms_to_peak, (1,), 1.4142135623730951),
        (radius_from_diameter_m, (0.002,), 0.001),
        (amplitude_to_intensity_attenuation_per_m, (0.25,), 0.5),
        (intensity_to_amplitude_attenuation_per_m, (0.5,), 0.25),
    ],
)
def test_b01_and_conversion_known_answers(function, args, expected):
    assert function(*args) == pytest.approx(expected, rel=1e-12, abs=1e-15)


OPERANDS = [
    (wavelength_m, (343, 70), 0, "sound_speed_m_s"),
    (wavelength_m, (343, 70), 1, "frequency_hz"),
    (wave_number_rad_m, (343, 70), 0, "sound_speed_m_s"),
    (wave_number_rad_m, (343, 70), 1, "frequency_hz"),
    (size_parameter_ka, (1, 2), 0, "radius_m"),
    (size_parameter_ka, (1, 2), 1, "wavelength_m"),
    (plane_progressive_wave_intensity_w_m2, (2, 2, 4), 0, "pressure_rms_pa"),
    (plane_progressive_wave_intensity_w_m2, (2, 2, 4), 1, "density_kg_m3"),
    (plane_progressive_wave_intensity_w_m2, (2, 2, 4), 2, "sound_speed_m_s"),
    (sinusoid_peak_to_rms, (2,), 0, "peak_amplitude"),
    (sinusoid_rms_to_peak, (2,), 0, "rms_amplitude"),
    (radius_from_diameter_m, (2,), 0, "diameter_m"),
    (amplitude_to_intensity_attenuation_per_m, (2,), 0, "amplitude_attenuation_per_m"),
    (intensity_to_amplitude_attenuation_per_m, (2,), 0, "intensity_attenuation_per_m"),
]


@pytest.mark.parametrize("function,args,index,name", OPERANDS)
@pytest.mark.parametrize(
    "value,code",
    [
        (True, "NUMBER_TYPE"),
        (False, "NUMBER_TYPE"),
        ("1", "NUMBER_TYPE"),
        (None, "NUMBER_TYPE"),
        (1 + 0j, "NUMBER_TYPE"),
        (float("nan"), "NONFINITE"),
        (float("inf"), "NONFINITE"),
        (float("-inf"), "NONFINITE"),
        (10**400, "NONFINITE"),
        (-1, "VALUE_RANGE"),
    ],
)
def test_every_operand_rejects_bad_numbers(function, args, index, name, value, code):
    args = list(args)
    args[index] = value
    with pytest.raises(InvalidInputError) as caught:
        function(*args)
    assert caught.value.code == code
    assert caught.value.path == "/" + name


@pytest.mark.parametrize(
    "function,args,expected",
    [
        (wavelength_m, (1e308, 1e308), 1),
        (wavelength_m, (1e-308, 1e-308), 1),
        (wave_number_rad_m, (1e308, 1e308), 6.283185307179586),
        (size_parameter_ka, (1e308, 1e308), 6.283185307179586),
        (plane_progressive_wave_intensity_w_m2, (1e200, 1e200, 1e200), 1),
        (plane_progressive_wave_intensity_w_m2, (1e-200, 1e-200, 1e-200), 1),
        (plane_progressive_wave_intensity_w_m2, (1e-200, 1e-200, 1), 1e-200),
        (plane_progressive_wave_intensity_w_m2, (1e154, 1e200, 1e108), 1),
        (plane_progressive_wave_intensity_w_m2, (2.0**900, 2.0**900, 2.0**900), 1),
        (plane_progressive_wave_intensity_w_m2, (2.0**-900, 2.0**-900, 2.0**-900), 1),
        (plane_progressive_wave_intensity_w_m2, (5e-324, 5e-324, 5e-324), 1),
    ],
)
def test_representable_results_survive_extreme_intermediates(function, args, expected):
    assert function(*args) == pytest.approx(expected, rel=1e-12, abs=0)


@pytest.mark.parametrize(
    "pressure,density,speed",
    [
        (1e200, 1e200, 1e-100),
        (1e-200, 1e-200, 1e100),
        (3.125e150, 2.5e125, 1.25e175),
        (7.25e-150, 2.125e-175, 3.75e-125),
    ],
)
def test_intensity_against_independent_decimal_arithmetic(pressure, density, speed):
    with localcontext() as context:
        context.prec = 100
        p, rho, c = map(Decimal.from_float, (pressure, density, speed))
        expected = float(p * p / (rho * c))
    assert plane_progressive_wave_intensity_w_m2(pressure, density, speed) == pytest.approx(
        expected, rel=1e-12, abs=0
    )


@pytest.mark.parametrize(
    "function,args",
    [
        (wavelength_m, (1e308, 1e-308)),
        (wavelength_m, (1e-308, 1e308)),
        (wave_number_rad_m, (1e-308, 1e308)),
        (wave_number_rad_m, (1e308, 5e-324)),
        (size_parameter_ka, (1e308, 1e-308)),
        (size_parameter_ka, (5e-324, 1e308)),
        (plane_progressive_wave_intensity_w_m2, (1e200, 1, 1)),
        (plane_progressive_wave_intensity_w_m2, (1e-200, 1, 1)),
        (sinusoid_rms_to_peak, (1.7976931348623157e308,)),
        (radius_from_diameter_m, (5e-324,)),
        (amplitude_to_intensity_attenuation_per_m, (1e308,)),
        (intensity_to_amplitude_attenuation_per_m, (5e-324,)),
    ],
)
def test_unrepresentable_outputs_raise_structured_errors(function, args):
    with pytest.raises(NumericalDomainError) as caught:
        function(*args)
    assert caught.value.code == "NUMERIC_RANGE"
    assert caught.value.path == "/" + function.__name__
    assert isinstance(caught.value, ValueError)  # Existing callers can retain this catch.


@pytest.mark.parametrize(
    "function,args",
    [
        (wavelength_m, (5e-324, 1)),
        (plane_progressive_wave_intensity_w_m2, (2.0**-537, 1, 1)),
        (radius_from_diameter_m, (1e-323,)),
        (sinusoid_peak_to_rms, (5e-324,)),
    ],
)
def test_subnormal_results_remain_nonzero_with_separate_tolerance(function, args):
    result = function(*args)
    assert result > 0
    assert abs(result - 5e-324) <= math.ulp(5e-324)


@pytest.mark.parametrize(
    "function",
    [
        sinusoid_peak_to_rms,
        sinusoid_rms_to_peak,
        amplitude_to_intensity_attenuation_per_m,
        intensity_to_amplitude_attenuation_per_m,
    ],
)
def test_exact_zero_amplitudes_and_attenuation(function):
    assert function(0) == 0


def test_zero_intensity_does_not_skip_denominator_validation():
    assert plane_progressive_wave_intensity_w_m2(0, 5e-324, 5e-324) == 0
    with pytest.raises(InvalidInputError, match="VALUE_RANGE"):
        plane_progressive_wave_intensity_w_m2(0, 0, 1)


@pytest.mark.parametrize("value", [0, 1e-200, 2, 1e200])
def test_conversion_inverse_checks_supplement_known_answers(value):
    assert sinusoid_peak_to_rms(sinusoid_rms_to_peak(value)) == pytest.approx(
        value, rel=1e-12, abs=0
    )
    assert (
        intensity_to_amplitude_attenuation_per_m(amplitude_to_intensity_attenuation_per_m(value))
        == value
    )


@pytest.mark.parametrize("function,args,index,name", OPERANDS[:6] + OPERANDS[7:9] + OPERANDS[11:12])
@pytest.mark.parametrize("zero", [0.0, -0.0])
def test_strictly_positive_operands_reject_both_zero_signs(function, args, index, name, zero):
    changed = list(args)
    changed[index] = zero
    with pytest.raises(InvalidInputError) as caught:
        function(*changed)
    assert caught.value.code == "VALUE_RANGE"
    assert caught.value.path == "/" + name


def test_fixed_extreme_intensity_grid_against_decimal_oracle():
    # Deterministic 9³ arithmetic checks; these are not physical operating points.
    values = [5e-324, 2.0**-900, 1e-200, 0.125, 1.0, 3.25, 1e200, 2.0**900, 1.7976931348623157e308]
    finite, rejected = 0, 0
    with localcontext() as context:
        context.prec = 120
        for args in product(values, repeat=3):
            pressure, density, speed = map(Decimal.from_float, args)
            expected = float(pressure * pressure / (density * speed))
            if not math.isfinite(expected) or expected == 0:
                with pytest.raises(NumericalDomainError):
                    plane_progressive_wave_intensity_w_m2(*args)
                rejected += 1
            else:
                actual = plane_progressive_wave_intensity_w_m2(*args)
                absolute = math.ulp(0.0) if expected < 2.2250738585072014e-308 else 0.0
                assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=absolute), args
                assert actual > 0
                finite += 1
    assert (finite, rejected) == (297, 432)
