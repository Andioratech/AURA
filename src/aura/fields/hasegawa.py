"""Bounded Hasegawa piston plus stationary sound-hard sphere field evaluator.

This is a truncated harmonic field calculation for the frozen NUM-01 air
geometry. It does not estimate force or select a converged truncation order.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from itertools import pairwise

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields.numerical import (
    _finite,
    _regular_bessel_scaled_values,
    _scaled_complex,
    _scaled_complex_add,
    _scaled_complex_multiply,
    _scaled_complex_real,
    _scaled_source_diffraction_coefficients,
    _scaled_spherical_neumann,
    _unscale_complex,
    spherical_legendre,
)
from aura.fields.types import MAX_SAMPLES, FieldSamples

MAX_HASEGAWA_ORDER = 512


@dataclass(frozen=True)
class HasegawaOrderComparison:
    """Observed change between two explicit modal truncations; not a bound."""

    previous_order: int
    order: int
    max_relative_pressure_change: float
    max_relative_velocity_change: float
    max_relative_gradient_change: float


@dataclass(frozen=True)
class HasegawaOrderSequence:
    """Fields and pointwise aggregate order changes for caller-selected orders."""

    fields: tuple[FieldSamples, ...]
    comparisons: tuple[HasegawaOrderComparison, ...]


def _scaled_divide(left: tuple[complex, int], right: tuple[complex, int]) -> tuple[complex, int]:
    if right[0] == 0j:
        raise NumericalDomainError("SPHERE_COEFFICIENT", "/sphere", "Scaled Hankel derivative is zero.")
    return _scaled_complex(left[0] / right[0], left[1] - right[1])


def _scaled_derivatives(max_order: int, x: float):
    regular = _regular_bessel_scaled_values(max_order + 1, x)
    neumann = _scaled_spherical_neumann(max_order + 1, x)
    derivatives = []
    for order in range(max_order + 1):
        regular_derivative = _scaled_complex_add(
            _scaled_complex_real(regular[order], order / x),
            _scaled_complex(-regular[order + 1][0], regular[order + 1][1]),
        )
        neumann_derivative = _scaled_complex_add(
            _scaled_complex_real(neumann[order], order / x),
            _scaled_complex(-neumann[order + 1][0], neumann[order + 1][1]),
        )
        derivatives.append((regular_derivative, neumann_derivative))
    return regular, neumann, tuple(derivatives)


def _hankel(value: tuple[complex, int], neumann: tuple[complex, int]) -> tuple[complex, int]:
    return _scaled_complex_add(value, _scaled_complex(1j * neumann[0], neumann[1]))


def _workspace_estimate(order: int, sample_count: int) -> int:
    # Includes retained modal sequences, one point's working arrays and output.
    # This is an intentional conservative pre-allocation gate, not NUM-02's
    # calibrated runtime estimate.
    return 65_536 + (order + 1) * 2_048 + sample_count * 1_536


def evaluate_hasegawa_piston_sphere_field(
    coordinates_m,
    *,
    density_kg_m3: float,
    sound_speed_m_s: float,
    frequency_hz: float,
    piston_velocity_peak_m_s: complex,
    piston_radius_m: float,
    sphere_radius_m: float,
    sphere_center_distance_m: float,
    max_order: int,
    workspace_bytes: int,
) -> FieldSamples:
    """Evaluate a caller-truncated piston/sphere field at Cartesian points.

    Geometry is axisymmetric: a baffled, uniformly moving circular piston is
    at ``z=0`` and the stationary rigid sphere center is at ``z=...distance``.
    The sphere surface is sound-hard, the air is homogeneous/lossless/linear,
    and phasors use exp(-iwt). Coordinates are in the exterior fluid, including
    the sphere surface. The caller must preflight its complete run and choose
    ``max_order``; this routine makes no convergence or physical-validation
    claim. Its local workspace gate runs before special-function allocations.
    """
    for name, value in (
        ("density_kg_m3", density_kg_m3), ("sound_speed_m_s", sound_speed_m_s),
        ("frequency_hz", frequency_hz), ("piston_radius_m", piston_radius_m),
        ("sphere_radius_m", sphere_radius_m),
        ("sphere_center_distance_m", sphere_center_distance_m),
    ):
        if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value) or value <= 0:
            raise InvalidInputError("FIELD_INPUT", f"/{name}", "Expected a finite positive scalar.")
    if type(piston_velocity_peak_m_s) not in (int, float, complex) or type(piston_velocity_peak_m_s) is bool:
        raise InvalidInputError("FIELD_INPUT", "/piston_velocity_peak_m_s", "Expected a finite complex amplitude.")
    velocity_amplitude = complex(piston_velocity_peak_m_s)
    if not math.isfinite(velocity_amplitude.real) or not math.isfinite(velocity_amplitude.imag):
        raise InvalidInputError("FIELD_INPUT", "/piston_velocity_peak_m_s", "Expected a finite complex amplitude.")
    if type(max_order) is not int or not 0 <= max_order <= MAX_HASEGAWA_ORDER:
        raise InvalidInputError("FIELD_ORDER", "/max_order", f"Expected an integer from 0 through {MAX_HASEGAWA_ORDER}.")
    if type(workspace_bytes) is not int or workspace_bytes < 0:
        raise InvalidInputError("FIELD_RESOURCE", "/workspace_bytes", "Expected a nonnegative byte cap.")
    if sphere_center_distance_m <= sphere_radius_m:
        raise InvalidInputError("FIELD_GEOMETRY", "/sphere_center_distance_m", "The sphere must clear the piston plane.")
    if type(coordinates_m) not in (list, tuple) or not 1 <= len(coordinates_m) <= MAX_SAMPLES:
        raise InvalidInputError("FIELD_SHAPE", "/coordinates_m", "Expected 1 to 256 sample rows.")

    points = []
    wave_number = 2 * math.pi * frequency_hz / sound_speed_m_s
    ka = _finite(wave_number * sphere_radius_m, "/ka")
    maximum_argument = ka
    for index, row in enumerate(coordinates_m):
        if type(row) not in (list, tuple) or len(row) != 3:
            raise InvalidInputError("FIELD_SHAPE", f"/coordinates_m/{index}", "Expected three coordinates.")
        point = []
        for axis, value in enumerate(row):
            if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value):
                raise InvalidInputError("FIELD_COORDINATE", f"/coordinates_m/{index}/{axis}", "Expected a finite coordinate.")
            point.append(float(value))
        if point[2] <= 0.0:
            raise InvalidInputError("FIELD_EXCLUSION", f"/coordinates_m/{index}", "Samples behind or on the piston/baffle plane are excluded.")
        relative = (point[0], point[1], point[2] - sphere_center_distance_m)
        radius = math.hypot(*relative)
        surface_roundoff = 8 * math.ulp(float(sphere_radius_m))
        if not math.isfinite(radius) or radius < sphere_radius_m - surface_roundoff:
            raise InvalidInputError("FIELD_EXCLUSION", f"/coordinates_m/{index}", "Sample must lie on or outside the sphere.")
        if abs(radius - sphere_radius_m) <= surface_roundoff:
            radius = float(sphere_radius_m)
        maximum_argument = max(maximum_argument, _finite(wave_number * radius, f"/coordinates_m/{index}/argument"))
        points.append((tuple(point), relative, radius))

    if maximum_argument > 40.0:
        raise InvalidInputError("FIELD_ARGUMENT_RANGE", "/coordinates_m", "The first coupled evaluator is bounded to kr <= 40.")
    required = _workspace_estimate(max_order, len(points))
    if workspace_bytes < required:
        raise InvalidInputError("FIELD_RESOURCE", "/workspace_bytes", f"Need at least {required} bytes; received {workspace_bytes}.")

    source = _scaled_source_diffraction_coefficients(
        max_order, wave_number_rad_m=wave_number,
        sphere_center_distance_m=sphere_center_distance_m, piston_radius_m=piston_radius_m,
    )
    _, _, sphere_derivatives = _scaled_derivatives(max_order, ka)
    omega = 2 * math.pi * frequency_hz
    prefactor = complex(0.0, 1.0) * velocity_amplitude
    pressures, velocities, pressure_gradients = [], [], []

    for point_index, (point, relative, radius) in enumerate(points):
        kr = wave_number * radius
        radial_regular, radial_neumann, radial_derivatives = _scaled_derivatives(max_order, kr)
        cosine = min(1.0, max(-1.0, relative[2] / radius))
        sine = math.sqrt(max(0.0, 1.0 - cosine * cosine))
        radial_terms, angular_terms, potential_terms = [], [], []
        for order in range(max_order + 1):
            at_surface_jp, at_surface_yp = sphere_derivatives[order]
            at_surface_hp = _scaled_complex_add(at_surface_jp, _scaled_complex(1j * at_surface_yp[0], at_surface_yp[1]))
            scattering = _scaled_complex_real(_scaled_divide(at_surface_jp, at_surface_hp), -1.0)
            scattered_value = _scaled_complex_multiply(scattering, _hankel(radial_regular[order], radial_neumann[order]))
            total_value = _scaled_complex_add(radial_regular[order], scattered_value)
            radial_jp, radial_yp = radial_derivatives[order]
            radial_hp = _scaled_complex_add(radial_jp, _scaled_complex(1j * radial_yp[0], radial_yp[1]))
            total_derivative = _scaled_complex_add(radial_jp, _scaled_complex_multiply(scattering, radial_hp))
            polynomial, polynomial_derivative = spherical_legendre(order, cosine)
            weight = (2 * order + 1) * (-1 if order % 2 else 1) * source[order][0]
            weight_scaled = (weight, source[order][1])
            potential_mode = _scaled_complex_real(
                _scaled_complex_multiply(weight_scaled, total_value), polynomial / wave_number
            )
            radial_mode = _scaled_complex_real(
                _scaled_complex_multiply(weight_scaled, total_derivative), polynomial
            )
            angular_mode = _scaled_complex_real(
                _scaled_complex_multiply(weight_scaled, total_value), -sine * polynomial_derivative / wave_number
            )
            potential_terms.append(_scaled_complex_multiply(potential_mode, _scaled_complex(prefactor)))
            radial_terms.append(_scaled_complex_multiply(radial_mode, _scaled_complex(prefactor)))
            angular_terms.append(_scaled_complex_multiply(angular_mode, _scaled_complex(prefactor)))

        potential = _sum_scaled(potential_terms, f"/potential/{point_index}")
        radial_gradient = _sum_scaled(radial_terms, f"/radial_gradient/{point_index}")
        angular_gradient = _sum_scaled(angular_terms, f"/angular_gradient/{point_index}")
        phi = _unscale_complex(potential, f"/potential/{point_index}")
        radial = _unscale_complex(radial_gradient, f"/radial_gradient/{point_index}")
        angular = _unscale_complex(angular_gradient, f"/angular_gradient/{point_index}") / radius
        ex, ey, ez = (component / radius for component in relative)
        if sine > 0.0:
            etheta = (
                cosine * relative[0] / (radius * sine),
                cosine * relative[1] / (radius * sine),
                -sine,
            )
        else:
            etheta = (0.0, 0.0, 0.0)
        grad_phi = tuple(radial * er + angular * et for er, et in zip((ex, ey, ez), etheta, strict=True))
        pressure = -1j * float(density_kg_m3) * omega * phi
        grad_pressure = tuple(-1j * float(density_kg_m3) * omega * component for component in grad_phi)
        particle_velocity = tuple(-component for component in grad_phi)
        if not all(math.isfinite(value.real) and math.isfinite(value.imag) for value in (pressure, *grad_pressure, *particle_velocity)):
            raise NumericalDomainError("NUMERIC_RANGE", f"/samples/{point_index}", "Field output is not representable.")
        pressures.append(pressure)
        velocities.append(particle_velocity)
        pressure_gradients.append(grad_pressure)

    return FieldSamples(
        frequency_hz=float(frequency_hz), coordinates_m=tuple(item[0] for item in points),
        pressure_pa=tuple(pressures), velocity_m_s=tuple(velocities),
        pressure_gradient_pa_m=tuple(pressure_gradients),
    )


def evaluate_hasegawa_order_sequence(
    coordinates_m,
    *,
    orders,
    density_kg_m3: float,
    sound_speed_m_s: float,
    frequency_hz: float,
    piston_velocity_peak_m_s: complex,
    piston_radius_m: float,
    sphere_radius_m: float,
    sphere_center_distance_m: float,
    workspace_bytes: int,
) -> HasegawaOrderSequence:
    """Evaluate explicit increasing orders and report observed field changes.

    The order list, not this function, defines the refinement sequence. The
    relative differences are diagnostics only: they are not remainder bounds,
    a convergence decision, or a production tolerance.
    """
    if type(orders) not in (list, tuple) or len(orders) < 2:
        raise InvalidInputError("FIELD_ORDER_SEQUENCE", "/orders", "Expected at least two explicit orders.")
    if any(type(order) is not int or not 0 <= order <= MAX_HASEGAWA_ORDER for order in orders):
        raise InvalidInputError("FIELD_ORDER_SEQUENCE", "/orders", "Orders must be integers from 0 through 512.")
    if any(right <= left for left, right in pairwise(orders)):
        raise InvalidInputError("FIELD_ORDER_SEQUENCE", "/orders", "Orders must be strictly increasing.")

    fields = tuple(
        evaluate_hasegawa_piston_sphere_field(
            coordinates_m,
            density_kg_m3=density_kg_m3,
            sound_speed_m_s=sound_speed_m_s,
            frequency_hz=frequency_hz,
            piston_velocity_peak_m_s=piston_velocity_peak_m_s,
            piston_radius_m=piston_radius_m,
            sphere_radius_m=sphere_radius_m,
            sphere_center_distance_m=sphere_center_distance_m,
            max_order=order,
            workspace_bytes=workspace_bytes,
        )
        for order in orders
    )
    comparisons = []
    for previous_order, order, previous, current in zip(
        orders[:-1], orders[1:], fields[:-1], fields[1:], strict=True
    ):
        comparisons.append(
            HasegawaOrderComparison(
                previous_order=previous_order,
                order=order,
                max_relative_pressure_change=_max_relative_change(previous.pressure_pa, current.pressure_pa),
                max_relative_velocity_change=_max_relative_change(previous.velocity_m_s, current.velocity_m_s),
                max_relative_gradient_change=_max_relative_change(
                    previous.pressure_gradient_pa_m, current.pressure_gradient_pa_m
                ),
            )
        )
    return HasegawaOrderSequence(fields=fields, comparisons=tuple(comparisons))


def _max_relative_change(previous, current) -> float:
    def flatten(values):
        for value in values:
            if isinstance(value, (tuple, list)):
                yield from flatten(value)
            else:
                yield complex(value)

    changes = []
    for left, right in zip(flatten(previous), flatten(current), strict=True):
        scale = max(abs(left), abs(right))
        if scale == 0.0:
            changes.append(0.0)
        else:
            changes.append(abs(left / scale - right / scale) / max(abs(left / scale), abs(right / scale), sys.float_info.min))
    return max(changes, default=0.0)


def _sum_scaled(values, path: str) -> tuple[complex, int]:
    total = (0j, 0)
    for value in values:
        total = _scaled_complex_add(total, value)
    if not math.isfinite(total[0].real) or not math.isfinite(total[0].imag):
        raise NumericalDomainError("NUMERIC_RANGE", path, "Scaled modal sum is not finite.")
    return total
