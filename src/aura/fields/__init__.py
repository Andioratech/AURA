"""Bounded analytical fields and representation; no body coupling or force model."""

from .analytic import (
    PlaneWave,
    evaluate_counterpropagating_pair,
    evaluate_plane_wave,
    evaluate_plane_wave_pair,
    mean_intensity_w_m2,
)
from .types import FieldSamples

__all__ = [
    "FieldSamples",
    "PlaneWave",
    "evaluate_counterpropagating_pair",
    "evaluate_plane_wave",
    "evaluate_plane_wave_pair",
    "mean_intensity_w_m2",
]
