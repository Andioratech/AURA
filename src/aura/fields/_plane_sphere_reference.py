"""Plane-wave partial-wave reference for a stationary rigid sphere.

This independent-source reference is intended for software comparisons with
the piston/sphere series. It is not the Hasegawa evaluator or a force model.
The modal pressure is ``(2n+1)i**n [j_n(kr) + b_n h_n^(1)(kr)]P_n(mu)``,
where ``b_n = -j'_n(ka)/h_n^(1)'(ka)`` enforces zero radial velocity.
"""

from __future__ import annotations

import math
import sys

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields.numerical import _spherical_sequences
from aura.fields.types import MAX_SAMPLES, FieldSamples
from aura.units import wave_number_rad_m as compute_wave_number_rad_m

MAX_REFERENCE_ORDER = 256


def _finite(value: float, path: str) -> float:
    if not math.isfinite(value):
        raise NumericalDomainError("NUMERIC_RANGE", path, "Reference field is not representable.")
    return value


def _real(value: object, path: str) -> float:
    if type(value) not in (int, float) or type(value) is bool:
        raise InvalidInputError("REFERENCE_INPUT", path, "Expected a finite real value.")
    try:
        result = float(value)
    except OverflowError as exc:
        raise InvalidInputError("REFERENCE_INPUT", path, "Value exceeds binary64 range.") from exc
    if not math.isfinite(result):
        raise InvalidInputError("REFERENCE_INPUT", path, "Expected a finite real value.")
    return result


def _positive(value: object, path: str) -> float:
    result = _real(value, path)
    if result <= 0:
        raise InvalidInputError("REFERENCE_INPUT", path, "Expected a finite positive value.")
    return result


def _nonnegative(value: object, path: str) -> float:
    result = _real(value, path)
    if result < 0:
        raise InvalidInputError("REFERENCE_INPUT", path, "Expected a finite nonnegative value.")
    return result


def _workspace_estimate(order_count: int, bessel_start: int, sample_count: int) -> int:
    pointer_bytes = sys.getsizeof((None,)) - sys.getsizeof(())
    list_header = sys.getsizeof([])
    tuple_header = sys.getsizeof(())
    float_bytes = sys.getsizeof(0.0)
    complex_bytes = sys.getsizeof(0j)

    def vector_bytes(count: int, item_bytes: int) -> int:
        return tuple_header + count * (pointer_bytes + item_bytes)

    recurrence_bytes = 2 * (list_header + (bessel_start + 2) * (pointer_bytes + float_bytes))
    order_bytes = 8 * vector_bytes(order_count, complex_bytes)
    order_bytes += 2 * vector_bytes(order_count, float_bytes)
    output_bytes = sample_count * 2048 + 4096
    return recurrence_bytes + order_bytes + output_bytes


def _legendre_sequences(order: int, cosine: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
    values = [1.0]
    derivatives = [0.0]
    if order == 0:
        return (1.0,), (0.0,)
    values.append(cosine)
    derivatives.append(1.0)
    for n in range(1, order):
        factor = 2 * n + 1
        value = (factor * cosine * values[n] - n * values[n - 1]) / (n + 1)
        derivative = (
            factor * (values[n] + cosine * derivatives[n]) - n * derivatives[n - 1]
        ) / (n + 1)
        values.append(_finite(value, "/legendre"))
        derivatives.append(_finite(derivative, "/legendre_derivative"))
    return tuple(values), tuple(derivatives)


def _complex_sum(terms: list[complex], path: str) -> complex:
    try:
        result = complex(math.fsum(term.real for term in terms), math.fsum(term.imag for term in terms))
    except (OverflowError, ValueError) as exc:
        raise NumericalDomainError("NUMERIC_RANGE", path, "Reference field sum is not representable.") from exc
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError("NUMERIC_RANGE", path, "Reference field sum is not representable.")
    return result


def evaluate_plane_wave_rigid_sphere_reference(
    coordinates_m,
    *,
    density_kg_m3: float,
    sound_speed_m_s: float,
    frequency_hz: float,
    peak_pressure_pa: float,
    sphere_radius_m: float,
    max_order: int,
    workspace_bytes: int,
) -> FieldSamples:
    """Evaluate the truncated +z plane-wave series for a centered rigid sphere.

    The sphere is stationary, the fluid is homogeneous/lossless/linear, and
    the phasor convention is exp(-iwt). Coordinates may lie on or outside the
    sphere. The caller supplies truncation and a workspace cap; this local
    guard does not replace matching NUM-02 preflight. The routine never
    selects an order or declares convergence. The
    boundary branch follows Hasegawa et al. (1985), Eqs. 1–20, stationary sphere
    (doi:10.1250/ast.6.9).
    """
    density = _positive(density_kg_m3, "/density_kg_m3")
    sound_speed = _positive(sound_speed_m_s, "/sound_speed_m_s")
    frequency = _positive(frequency_hz, "/frequency_hz")
    pressure_amplitude = _nonnegative(peak_pressure_pa, "/peak_pressure_pa")
    sphere_radius = _positive(sphere_radius_m, "/sphere_radius_m")
    wave_number = compute_wave_number_rad_m(sound_speed, frequency)
    if type(max_order) is not int or not 0 <= max_order <= MAX_REFERENCE_ORDER:
        raise InvalidInputError(
            "REFERENCE_ORDER", "/max_order", f"Expected an integer from 0 through {MAX_REFERENCE_ORDER}."
        )
    if type(workspace_bytes) is not int or workspace_bytes < 0:
        raise InvalidInputError("FIELD_RESOURCE", "/workspace_bytes", "Expected a nonnegative byte cap.")
    if type(coordinates_m) not in (list, tuple) or not 1 <= len(coordinates_m) <= MAX_SAMPLES:
        raise InvalidInputError("FIELD_SHAPE", "/coordinates_m", "Expected 1 to 256 sample rows.")

    points = []
    maximum_argument = _finite(wave_number * sphere_radius, "/sphere_argument")
    for index, row in enumerate(coordinates_m):
        if type(row) not in (list, tuple) or len(row) != 3:
            raise InvalidInputError("FIELD_SHAPE", f"/coordinates_m/{index}", "Expected three coordinates.")
        point = []
        for axis, value in enumerate(row):
            try:
                point.append(_real(value, f"/coordinates_m/{index}/{axis}"))
            except InvalidInputError as exc:
                raise InvalidInputError(
                    "FIELD_COORDINATE", f"/coordinates_m/{index}/{axis}", "Expected a finite coordinate."
                ) from exc
        radius = math.hypot(*point)
        if not math.isfinite(radius) or radius < sphere_radius:
            raise InvalidInputError(
                "FIELD_EXCLUSION", f"/coordinates_m/{index}", "Sample must lie on or outside the sphere."
            )
        maximum_argument = max(maximum_argument, _finite(wave_number * radius, f"/coordinates_m/{index}/argument"))
        points.append(tuple(point))

    margin = max(32, int(math.sqrt(40 * (max_order + 1))))
    bessel_start = max(max_order + 1 + margin, math.ceil(maximum_argument) + margin)
    if bessel_start > 8192:
        raise InvalidInputError("BESSEL_WORK_RANGE", "/wave_number_rad_m", "Reference Bessel workspace is too large.")
    required = _workspace_estimate(max_order + 1, bessel_start, len(points))
    if workspace_bytes < required:
        raise InvalidInputError(
            "FIELD_RESOURCE", "/workspace_bytes",
            f"Need at least {required} bytes for the reference field; received {workspace_bytes}.",
        )

    _, _, sphere_j_derivatives, sphere_y_derivatives = _spherical_sequences(
        max_order, wave_number * sphere_radius
    )
    coefficients = []
    for order, (j_derivative, y_derivative) in enumerate(
        zip(sphere_j_derivatives, sphere_y_derivatives, strict=True)
    ):
        denominator = complex(j_derivative, y_derivative)
        if abs(denominator) == 0:
            raise NumericalDomainError(
                "SPHERE_COEFFICIENT", f"/orders/{order}", "Outgoing Hankel derivative is zero."
            )
        coefficient = complex(-j_derivative, 0.0) / denominator
        if not math.isfinite(coefficient.real) or not math.isfinite(coefficient.imag):
            raise NumericalDomainError(
                "SPHERE_COEFFICIENT", f"/orders/{order}", "Scattering coefficient is not finite."
            )
        coefficients.append(coefficient)

    omega = _finite(2 * math.pi * frequency, "/omega")
    impedance_denominator = _finite(density * omega, "/density_omega")
    pressure_values = []
    velocity_values = []
    gradient_values = []
    for point_index, point in enumerate(points):
        radius = math.hypot(*point)
        argument = _finite(wave_number * radius, f"/coordinates_m/{point_index}/argument")
        cosine = point[2] / radius
        legendre, legendre_derivatives = _legendre_sequences(max_order, cosine)
        j_values, y_values, j_derivatives, y_derivatives = _spherical_sequences(max_order, argument)
        e_r = tuple(component / radius for component in point)
        pressure_terms = []
        gradient_terms = [[] for _ in range(3)]
        for order in range(max_order + 1):
            outgoing = complex(j_values[order], y_values[order])
            outgoing_derivative = complex(j_derivatives[order], y_derivatives[order])
            radial_value = complex(j_values[order], 0.0) + coefficients[order] * outgoing
            radial_derivative = complex(j_derivatives[order], 0.0) + (
                coefficients[order] * outgoing_derivative
            )
            phase = (1j) ** order
            weight = pressure_amplitude * (2 * order + 1) * phase
            pressure_terms.append(weight * radial_value * legendre[order])
            radial_term = weight * wave_number * radial_derivative * legendre[order]
            angular_term = weight * radial_value * legendre_derivatives[order] / radius
            for axis in range(3):
                gradient_terms[axis].append(
                    radial_term * e_r[axis]
                    + angular_term * ((1.0 if axis == 2 else 0.0) - cosine * e_r[axis])
                )

        pressure = _complex_sum(pressure_terms, f"/pressure/{point_index}")
        gradient = tuple(
            _complex_sum(gradient_terms[axis], f"/gradient/{point_index}/{axis}")
            for axis in range(3)
        )
        velocity = tuple(
            _finite_complex(value / complex(0.0, impedance_denominator), f"/velocity/{point_index}/{axis}")
            for axis, value in enumerate(gradient)
        )
        pressure_values.append(pressure)
        gradient_values.append(gradient)
        velocity_values.append(velocity)
        del (
            e_r, gradient_terms, j_derivatives, j_values, legendre, legendre_derivatives,
            pressure_terms, y_derivatives, y_values,
        )

    return FieldSamples(
        frequency_hz=frequency,
        coordinates_m=tuple(points),
        pressure_pa=tuple(pressure_values),
        velocity_m_s=tuple(velocity_values),
        pressure_gradient_pa_m=tuple(gradient_values),
    )


def _finite_complex(value: complex, path: str) -> complex:
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise NumericalDomainError("NUMERIC_RANGE", path, "Reference field is not representable.")
    return value
