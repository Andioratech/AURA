"""Bounded ideal plane and spherical incident fields; no body or force model."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from aura.errors import InvalidInputError, NumericalDomainError
from aura.units import (
    _finite_scalar,
    _nonnegative_finite,
    _positive_finite,
    _scaled_ratio,
    wave_number_rad_m,
)

from .types import MAX_SAMPLES, FieldSamples

MODEL_VERSION = "PLANE-WAVE-1.0"
PAIR_MODEL_VERSION = "COUNTERPROPAGATING-1.0"
TWO_WAVE_MODEL_VERSION = "TWO-PLANE-WAVES-1.0"
SPHERICAL_MODEL_VERSION = "SPHERICAL-WAVE-1.0"


def _vector(value, name):
    if type(value) not in (list, tuple) or len(value) != 3:
        raise InvalidInputError("FIELD_SHAPE", "/" + name, "Expected three real components.")
    return tuple(_finite_scalar(f"{name}/{i}", item) for i, item in enumerate(value))


def _finite_result(value, name):
    if not math.isfinite(value):
        raise NumericalDomainError("NUMERIC_RANGE", "/" + name, "Arithmetic is not finite.")
    return value


@dataclass(frozen=True, kw_only=True)
class PlaneWave:
    """Explicit homogeneous, stationary, lossless plane-wave specification in SI."""

    density_kg_m3: float
    sound_speed_m_s: float
    frequency_hz: float
    peak_pressure_pa: float
    direction: tuple[float, float, float]
    reference_m: tuple[float, float, float]
    phase_rad: float
    dynamic_viscosity_pa_s: float
    amplitude_attenuation_per_m: float

    def __post_init__(self):
        for name in ("density_kg_m3", "sound_speed_m_s", "frequency_hz"):
            object.__setattr__(self, name, _positive_finite(name, getattr(self, name)))
        for name in ("peak_pressure_pa", "dynamic_viscosity_pa_s", "amplitude_attenuation_per_m"):
            object.__setattr__(self, name, _nonnegative_finite(name, getattr(self, name)))
        for name in ("dynamic_viscosity_pa_s", "amplitude_attenuation_per_m"):
            if getattr(self, name) != 0:
                raise InvalidInputError(
                    "FIELD_MODEL", "/" + name, "Only explicit zero loss is supported."
                )
        object.__setattr__(self, "phase_rad", _finite_scalar("phase_rad", self.phase_rad))
        object.__setattr__(self, "direction", _vector(self.direction, "direction"))
        object.__setattr__(self, "reference_m", _vector(self.reference_m, "reference_m"))
        if abs(math.hypot(*self.direction) - 1) > 4 * sys.float_info.epsilon:
            raise InvalidInputError(
                "FIELD_DIRECTION", "/direction", "Expected a unit direction; no normalization."
            )
        # Validate the derived scalar range even for a zero-drive specification.
        wave_number_rad_m(self.sound_speed_m_s, self.frequency_hz)
        _scaled_ratio("impedance", (self.density_kg_m3, self.sound_speed_m_s))


def evaluate_plane_wave(
    wave: PlaneWave, coordinates_m, *, box_min_m, box_max_m, workspace_bytes: int
) -> FieldSamples:
    """Evaluate EQ-007 after all geometry/resource/phase checks, preserving order."""
    prepared = _prepare_plane_wave(
        wave,
        coordinates_m,
        box_min_m=box_min_m,
        box_max_m=box_max_m,
        workspace_bytes=workspace_bytes,
    )
    return _evaluate_prepared(wave, *prepared)


def _prepare_plane_wave(wave, coordinates_m, *, box_min_m, box_max_m, workspace_bytes):
    """Validate a complete source plan without trig or complex field allocation."""
    if type(wave) is not PlaneWave:
        raise InvalidInputError("FIELD_SPEC", "/wave", "Expected an explicit PlaneWave.")
    if type(coordinates_m) not in (list, tuple) or not 1 <= len(coordinates_m) <= MAX_SAMPLES:
        raise InvalidInputError("FIELD_SHAPE", "/coordinates_m", "Expected 1 to 256 sample rows.")
    count = len(coordinates_m)
    if type(workspace_bytes) is not int or workspace_bytes < 4096 * count + 4096:
        raise InvalidInputError(
            "FIELD_RESOURCE", "/workspace_bytes", "Insufficient incremental workspace budget."
        )
    lower, upper = _vector(box_min_m, "box_min_m"), _vector(box_max_m, "box_max_m")
    if any(lo >= hi for lo, hi in zip(lower, upper)):
        raise InvalidInputError(
            "FIELD_DOMAIN", "/box_max_m", "Each upper bound must exceed its lower bound."
        )
    positions = tuple(_vector(row, f"coordinates_m/{i}") for i, row in enumerate(coordinates_m))
    k = wave_number_rad_m(wave.sound_speed_m_s, wave.frequency_hz)
    phases = []
    for index, point in enumerate(positions):
        path = f"coordinates_m/{index}"
        if any(x < lo or x > hi for x, lo, hi in zip(point, lower, upper)):
            raise InvalidInputError(
                "FIELD_DOMAIN", "/" + path, "Sample lies outside the observation box."
            )
        terms = []
        condition = abs(wave.phase_rad)
        for x, ref, direction in zip(point, wave.reference_m, wave.direction):
            delta = _finite_result(x - ref, path)
            terms.append(_scaled_ratio(path, (k, direction, delta)))
            condition += abs(_scaled_ratio(path, (k, direction, x)))
            condition += abs(_scaled_ratio(path, (k, direction, ref)))
        phase = ((terms[0] + terms[1]) + terms[2]) + wave.phase_rad
        if not math.isfinite(condition) or condition > 8 * math.pi or abs(phase) > 4 * math.pi:
            raise NumericalDomainError(
                "FIELD_PHASE_RANGE",
                "/" + path,
                "Phase or coordinate conditioning exceeds the admitted range.",
            )
        phases.append(phase)

    return positions, k, phases


def _evaluate_prepared(wave, positions, k, phases):
    pressures, velocities, gradients = [], [], []
    for phase in phases:
        pressure = complex(
            _scaled_ratio("pressure/real", (wave.peak_pressure_pa, math.cos(phase))),
            _scaled_ratio("pressure/imag", (wave.peak_pressure_pa, math.sin(phase))),
        )
        velocities.append(
            tuple(
                complex(
                    _scaled_ratio(
                        "velocity/real",
                        (n, pressure.real),
                        (wave.density_kg_m3, wave.sound_speed_m_s),
                    ),
                    _scaled_ratio(
                        "velocity/imag",
                        (n, pressure.imag),
                        (wave.density_kg_m3, wave.sound_speed_m_s),
                    ),
                )
                for n in wave.direction
            )
        )
        gradients.append(
            tuple(
                complex(
                    _scaled_ratio("pressure_gradient/real", (-k, n, pressure.imag)),
                    _scaled_ratio("pressure_gradient/imag", (k, n, pressure.real)),
                )
                for n in wave.direction
            )
        )
        pressures.append(pressure)
    return FieldSamples(
        frequency_hz=wave.frequency_hz,
        coordinates_m=positions,
        pressure_pa=pressures,
        velocity_m_s=velocities,
        pressure_gradient_pa_m=gradients,
    )


def evaluate_counterpropagating_pair(
    forward: PlaneWave,
    backward: PlaneWave,
    coordinates_m,
    *,
    box_min_m,
    box_max_m,
    workspace_bytes: int,
) -> FieldSamples:
    """Sum two compatible opposing waves after validating both complete plans."""
    _validate_pair_specs(forward, backward)
    if backward.direction != tuple(-n for n in forward.direction):
        raise InvalidInputError(
            "FIELD_DIRECTION", "/backward/direction", "Expected exactly opposite directions."
        )
    return evaluate_plane_wave_pair(
        forward,
        backward,
        coordinates_m,
        box_min_m=box_min_m,
        box_max_m=box_max_m,
        workspace_bytes=workspace_bytes,
    )


def _validate_pair_specs(forward, backward):
    if type(forward) is not PlaneWave or type(backward) is not PlaneWave:
        raise InvalidInputError("FIELD_SPEC", "/waves", "Expected two explicit PlaneWave objects.")
    for name in ("density_kg_m3", "sound_speed_m_s", "frequency_hz"):
        if getattr(forward, name) != getattr(backward, name):
            raise InvalidInputError(
                "FIELD_MODEL", "/" + name, "Both sources must share the medium and frequency."
            )


def evaluate_plane_wave_pair(
    first_wave: PlaneWave,
    second_wave: PlaneWave,
    coordinates_m,
    *,
    box_min_m,
    box_max_m,
    workspace_bytes: int,
) -> FieldSamples:
    """Sum two coherent waves in one medium after complete input preflight."""
    _validate_pair_specs(first_wave, second_wave)
    if type(coordinates_m) not in (list, tuple) or not 1 <= len(coordinates_m) <= MAX_SAMPLES:
        raise InvalidInputError("FIELD_SHAPE", "/coordinates_m", "Expected 1 to 256 sample rows.")
    if type(workspace_bytes) is not int or workspace_bytes < 4096 * len(coordinates_m) + 8192:
        raise InvalidInputError(
            "FIELD_RESOURCE", "/workspace_bytes", "Insufficient pair workspace budget."
        )
    options = {"box_min_m": box_min_m, "box_max_m": box_max_m, "workspace_bytes": workspace_bytes}
    first_plan = _prepare_plane_wave(first_wave, coordinates_m, **options)
    second_plan = _prepare_plane_wave(second_wave, first_plan[0], **options)
    first = _evaluate_prepared(first_wave, *first_plan)
    second = _evaluate_prepared(second_wave, *second_plan)

    def add(a, b):
        return complex(
            _finite_result(a.real + b.real, "superposition/real"),
            _finite_result(a.imag + b.imag, "superposition/imag"),
        )

    def vectors(a, b):
        return tuple(
            tuple(add(x, y) for x, y in zip(row_a, row_b, strict=True))
            for row_a, row_b in zip(a, b, strict=True)
        )

    return FieldSamples(
        frequency_hz=first_wave.frequency_hz,
        coordinates_m=first.coordinates_m,
        pressure_pa=tuple(
            add(a, b) for a, b in zip(first.pressure_pa, second.pressure_pa, strict=True)
        ),
        velocity_m_s=vectors(first.velocity_m_s, second.velocity_m_s),
        pressure_gradient_pa_m=vectors(first.pressure_gradient_pa_m, second.pressure_gradient_pa_m),
    )


def mean_intensity_w_m2(field: FieldSamples) -> tuple[tuple[float, float, float], ...]:
    """EQ-009 harmonic energy flux from both phasors; not force or source power."""
    if type(field) is not FieldSamples:
        raise InvalidInputError("FIELD_SPEC", "/field", "Expected FieldSamples.")
    result = []
    for pressure, velocity in zip(field.pressure_pa, field.velocity_m_s):
        result.append(
            tuple(
                _finite_result(
                    _scaled_ratio("intensity", (pressure.real, component.real), (2.0,))
                    + _scaled_ratio("intensity", (pressure.imag, component.imag), (2.0,)),
                    "intensity",
                )
                for component in velocity
            )
        )
    return tuple(result)


@dataclass(frozen=True, kw_only=True)
class SphericalWave:
    """Ideal outgoing radial field, normalized on an explicit reference sphere."""

    density_kg_m3: float
    sound_speed_m_s: float
    frequency_hz: float
    peak_pressure_pa: float
    center_m: tuple[float, float, float]
    reference_radius_m: float
    minimum_radius_m: float
    phase_rad: float
    dynamic_viscosity_pa_s: float
    amplitude_attenuation_per_m: float

    def __post_init__(self):
        for name in (
            "density_kg_m3",
            "sound_speed_m_s",
            "frequency_hz",
            "reference_radius_m",
            "minimum_radius_m",
        ):
            object.__setattr__(self, name, _positive_finite(name, getattr(self, name)))
        for name in ("peak_pressure_pa", "dynamic_viscosity_pa_s", "amplitude_attenuation_per_m"):
            object.__setattr__(self, name, _nonnegative_finite(name, getattr(self, name)))
        for name in ("dynamic_viscosity_pa_s", "amplitude_attenuation_per_m"):
            if getattr(self, name) != 0:
                raise InvalidInputError(
                    "FIELD_MODEL", "/" + name, "Only explicit zero loss is supported."
                )
        if self.reference_radius_m < self.minimum_radius_m:
            raise InvalidInputError(
                "FIELD_DOMAIN", "/reference_radius_m", "Reference sphere is inside exclusion."
            )
        object.__setattr__(self, "center_m", _vector(self.center_m, "center_m"))
        object.__setattr__(self, "phase_rad", _finite_scalar("phase_rad", self.phase_rad))
        wave_number_rad_m(self.sound_speed_m_s, self.frequency_hz)
        _scaled_ratio("impedance", (self.density_kg_m3, self.sound_speed_m_s))


def evaluate_spherical_wave(
    wave: SphericalWave, coordinates_m, *, box_min_m, box_max_m, workspace_bytes: int
) -> FieldSamples:
    """Evaluate EQ-010 with full reactive velocity after complete domain preflight."""
    if type(wave) is not SphericalWave:
        raise InvalidInputError("FIELD_SPEC", "/wave", "Expected an explicit SphericalWave.")
    if type(coordinates_m) not in (list, tuple) or not 1 <= len(coordinates_m) <= MAX_SAMPLES:
        raise InvalidInputError("FIELD_SHAPE", "/coordinates_m", "Expected 1 to 256 sample rows.")
    if type(workspace_bytes) is not int or workspace_bytes < 4096 * len(coordinates_m) + 4096:
        raise InvalidInputError(
            "FIELD_RESOURCE", "/workspace_bytes", "Insufficient incremental workspace budget."
        )
    lower, upper = _vector(box_min_m, "box_min_m"), _vector(box_max_m, "box_max_m")
    if any(lo >= hi for lo, hi in zip(lower, upper)):
        raise InvalidInputError(
            "FIELD_DOMAIN", "/box_max_m", "Each upper bound must exceed its lower bound."
        )
    positions = tuple(_vector(row, f"coordinates_m/{i}") for i, row in enumerate(coordinates_m))
    k = wave_number_rad_m(wave.sound_speed_m_s, wave.frequency_hz)
    plans = []
    for index, point in enumerate(positions):
        path = f"coordinates_m/{index}"
        if any(x < lo or x > hi for x, lo, hi in zip(point, lower, upper)):
            raise InvalidInputError(
                "FIELD_DOMAIN", "/" + path, "Sample lies outside the observation box."
            )
        delta = tuple(_finite_result(x - c, path) for x, c in zip(point, wave.center_m))
        radius = _finite_result(math.hypot(*delta), path)
        if radius < wave.minimum_radius_m:
            raise InvalidInputError(
                "FIELD_EXCLUSION", "/" + path, "Sample lies inside the excluded source region."
            )
        coordinate_scale = _finite_result(math.hypot(*point) + math.hypot(*wave.center_m), path)
        conditioning = _scaled_ratio(path, (coordinate_scale,), (radius,))
        if conditioning > 8:
            raise NumericalDomainError(
                "FIELD_GEOMETRY_RANGE", "/" + path, "Radial coordinate cancellation exceeds limit."
            )
        phase = _finite_result(
            _scaled_ratio(path, (k, radius - wave.reference_radius_m)) + wave.phase_rad, path
        )
        condition = abs(wave.phase_rad) + abs(_scaled_ratio(path, (k, wave.reference_radius_m)))
        for x, center in zip(point, wave.center_m):
            condition += abs(_scaled_ratio(path, (k, x)))
            condition += abs(_scaled_ratio(path, (k, center)))
        if not math.isfinite(condition) or condition > 8 * math.pi or abs(phase) > 4 * math.pi:
            raise NumericalDomainError(
                "FIELD_PHASE_RANGE", "/" + path, "Phase conditioning exceeds the admitted range."
            )
        direction = tuple(_scaled_ratio(path, (d,), (radius,)) for d in delta)
        plans.append((radius, direction, phase))
    return _evaluate_spherical_prepared(wave, positions, k, plans)


def _evaluate_spherical_prepared(wave, positions, k, plans):
    pressures, velocities, gradients = [], [], []
    impedance_factors = (wave.density_kg_m3, wave.sound_speed_m_s)
    for radius, direction, phase in plans:
        pressure = complex(
            _scaled_ratio(
                "pressure/real",
                (wave.peak_pressure_pa, wave.reference_radius_m, math.cos(phase)),
                (radius,),
            ),
            _scaled_ratio(
                "pressure/imag",
                (wave.peak_pressure_pa, wave.reference_radius_m, math.sin(phase)),
                (radius,),
            ),
        )
        vs, gs = [], []
        for n in direction:
            vs.append(
                complex(
                    _finite_result(
                        _scaled_ratio("velocity/real", (n, pressure.real), impedance_factors)
                        - _scaled_ratio(
                            "velocity/reactive", (n, pressure.imag), (*impedance_factors, k, radius)
                        ),
                        "velocity/real",
                    ),
                    _finite_result(
                        _scaled_ratio("velocity/imag", (n, pressure.imag), impedance_factors)
                        + _scaled_ratio(
                            "velocity/reactive", (n, pressure.real), (*impedance_factors, k, radius)
                        ),
                        "velocity/imag",
                    ),
                )
            )
            gs.append(
                complex(
                    _finite_result(
                        -_scaled_ratio("pressure_gradient/radial", (n, pressure.real), (radius,))
                        - _scaled_ratio("pressure_gradient/real", (k, n, pressure.imag)),
                        "pressure_gradient/real",
                    ),
                    _finite_result(
                        _scaled_ratio("pressure_gradient/imag", (k, n, pressure.real))
                        - _scaled_ratio("pressure_gradient/radial", (n, pressure.imag), (radius,)),
                        "pressure_gradient/imag",
                    ),
                )
            )
        pressures.append(pressure)
        velocities.append(tuple(vs))
        gradients.append(tuple(gs))
    return FieldSamples(
        frequency_hz=wave.frequency_hz,
        coordinates_m=positions,
        pressure_pa=pressures,
        velocity_m_s=velocities,
        pressure_gradient_pa_m=gradients,
    )
