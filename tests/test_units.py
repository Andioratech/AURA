"""Known-answer checks for the initial SI calculation layer."""

import math

import pytest

from aura.units import (
    plane_progressive_wave_intensity_w_m2,
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
