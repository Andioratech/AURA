"""Rigid half-space Helmholtz Green function and first derivatives.

The kernel is a building block for the NUM-03 boundary-element reference. It
does not solve a boundary integral equation or establish a field result.
"""

from __future__ import annotations

import math

from aura.errors import InvalidInputError, NumericalDomainError


def _point(value: tuple[float, float, float], path: str) -> tuple[float, float, float]:
    if type(value) not in (tuple, list) or len(value) != 3:
        raise InvalidInputError("BEM_POINT", path, "Expected three finite Cartesian coordinates.")
    coordinates = []
    for axis, component in enumerate(value):
        if type(component) not in (int, float) or type(component) is bool or not math.isfinite(component):
            raise InvalidInputError("BEM_POINT", f"{path}/{axis}", "Expected a finite real coordinate.")
        coordinates.append(float(component))
    if coordinates[2] < 0.0:
        raise InvalidInputError("BEM_HALF_SPACE", path + "/2", "Point must lie on or above z=0.")
    return tuple(coordinates)


def _wave_number(value: float) -> float:
    if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value) or value <= 0.0:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")
    return float(value)


def _normal(value: tuple[float, float, float], path: str) -> tuple[float, float, float]:
    if type(value) not in (tuple, list) or len(value) != 3:
        raise InvalidInputError("BEM_NORMAL", path, "Expected a finite three-dimensional unit normal.")
    normal = []
    for axis, component in enumerate(value):
        if type(component) not in (int, float) or type(component) is bool or not math.isfinite(component):
            raise InvalidInputError("BEM_NORMAL", f"{path}/{axis}", "Expected a finite normal component.")
        normal.append(float(component))
    normal = tuple(normal)
    length = math.hypot(*normal)
    if not math.isclose(length, 1.0, rel_tol=0.0, abs_tol=64 * math.ulp(1.0)):
        raise InvalidInputError("BEM_NORMAL", path, "Expected a unit normal vector.")
    return normal


def _free_space_term(
    field: tuple[float, float, float],
    source: tuple[float, float, float],
    wave_number: float,
) -> tuple[complex, tuple[complex, complex, complex]]:
    displacement = tuple(x - y for x, y in zip(field, source, strict=True))
    radius = math.hypot(*displacement)
    if radius == 0.0:
        raise InvalidInputError("BEM_KERNEL_SINGULAR", "/field_point", "Green function is singular at its source.")
    phase = wave_number * radius
    if not math.isfinite(phase):
        raise NumericalDomainError("BEM_KERNEL_RANGE", "/wave_number_rad_m", "Kernel phase is not representable.")
    oscillation = complex(math.cos(phase), math.sin(phase))
    value = oscillation / (4.0 * math.pi * radius)
    radial_factor = oscillation * complex(-1.0, phase) / (4.0 * math.pi * radius**3)
    gradient = tuple(radial_factor * component for component in displacement)
    if not all(math.isfinite(component.real) and math.isfinite(component.imag) for component in (value, *gradient)):
        raise NumericalDomainError("BEM_KERNEL_RANGE", "/field_point", "Green function is outside binary64 range.")
    return value, gradient


def _free_space_mixed_normal_derivative(
    field: tuple[float, float, float],
    source: tuple[float, float, float],
    field_normal: tuple[float, float, float],
    source_normal: tuple[float, float, float],
    wave_number: float,
) -> complex:
    """Return d²G0/(dn_field dn_source) away from its diagonal."""
    displacement = tuple(x - y for x, y in zip(field, source, strict=True))
    radius = math.hypot(*displacement)
    if radius == 0.0:
        raise InvalidInputError("BEM_KERNEL_SINGULAR", "/field_point", "Mixed derivative is singular at its source.")
    phase = wave_number * radius
    if not math.isfinite(phase):
        raise NumericalDomainError("BEM_KERNEL_RANGE", "/wave_number_rad_m", "Kernel phase is not representable.")
    oscillation = complex(math.cos(phase), math.sin(phase))
    radial = oscillation * complex(-1.0, phase) / (4.0 * math.pi * radius**3)
    dyadic = oscillation * complex(3.0 - phase * phase, -3.0 * phase) / (4.0 * math.pi * radius**5)
    normal_dot = math.fsum(a * b for a, b in zip(field_normal, source_normal, strict=True))
    field_projection = math.fsum(a * b for a, b in zip(field_normal, displacement, strict=True))
    source_projection = math.fsum(a * b for a, b in zip(source_normal, displacement, strict=True))
    result = -(radial * normal_dot + dyadic * field_projection * source_projection)
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError("BEM_KERNEL_RANGE", "/field_point", "Mixed derivative is outside binary64 range.")
    return result


def neumann_half_space_green(
    field_point_m: tuple[float, float, float],
    source_point_m: tuple[float, float, float],
    *,
    wave_number_rad_m: float,
) -> tuple[complex, tuple[complex, complex, complex], tuple[complex, complex, complex]]:
    """Return G_N, grad_field G_N and grad_source G_N for z >= 0.

    Uses the image-source Green function for the plane z=0 with zero normal
    derivative. The outgoing convention is exp(-iwt), so the free-space kernel
    is exp(+ikr)/(4*pi*r). Coordinates are in metres and k is in rad/m.
    """
    field = _point(field_point_m, "/field_point_m")
    source = _point(source_point_m, "/source_point_m")
    wave_number = _wave_number(wave_number_rad_m)
    image = (source[0], source[1], -source[2])
    direct_value, direct_field_gradient = _free_space_term(field, source, wave_number)
    image_value, image_field_gradient = _free_space_term(field, image, wave_number)
    value = direct_value + image_value
    field_gradient = tuple(a + b for a, b in zip(direct_field_gradient, image_field_gradient, strict=True))
    # For the direct term, grad_source = -grad_field. Reflection of the image
    # source changes the sign of its z derivative by the chain rule.
    source_gradient = tuple(
        -direct_field_gradient[axis] - image_field_gradient[axis] * (1.0 if axis < 2 else -1.0)
        for axis in range(3)
    )
    return value, field_gradient, source_gradient


def neumann_half_space_mixed_normal_derivative(
    field_point_m: tuple[float, float, float],
    source_point_m: tuple[float, float, float],
    field_normal: tuple[float, float, float],
    source_normal: tuple[float, float, float],
    *,
    wave_number_rad_m: float,
) -> complex:
    """Return d²G_N/(dn_field dn_source), away from the direct diagonal.

    ``source_normal`` is the physical normal at the source. Its reflected
    image contribution is transformed by the reflection Jacobian.
    """
    field = _point(field_point_m, "/field_point_m")
    source = _point(source_point_m, "/source_point_m")
    n_field = _normal(field_normal, "/field_normal")
    n_source = _normal(source_normal, "/source_normal")
    wave_number = _wave_number(wave_number_rad_m)
    image = (source[0], source[1], -source[2])
    image_normal = (n_source[0], n_source[1], -n_source[2])
    direct = _free_space_mixed_normal_derivative(field, source, n_field, n_source, wave_number)
    reflected = _free_space_mixed_normal_derivative(field, image, n_field, image_normal, wave_number)
    value = direct + reflected
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise NumericalDomainError("BEM_KERNEL_RANGE", "/field_point_m", "Mixed derivative is outside binary64 range.")
    return value
