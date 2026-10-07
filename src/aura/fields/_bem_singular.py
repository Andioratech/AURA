"""One-dimensional product-integration primitives for BEM panel kernels."""

from __future__ import annotations

import math
from collections.abc import Callable

from aura.errors import InvalidInputError, NumericalDomainError


def _panel_inputs(
    density: Callable[[float], float | complex],
    left: float,
    right: float,
    singular_point: float,
    order: int,
    *,
    allow_endpoint: bool = False,
) -> tuple[complex, tuple[float, ...], tuple[float, ...]]:
    if not callable(density):
        raise InvalidInputError("BEM_PANEL_DENSITY", "/density", "Expected a callable density.")
    for path, value in (
        ("/left", left),
        ("/right", right),
        ("/singular_point", singular_point),
    ):
        if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value):
            raise InvalidInputError("BEM_PANEL_RANGE", path, "Expected a finite real coordinate.")
    interior = left < singular_point < right
    endpoint = allow_endpoint and singular_point in (left, right)
    if not (interior or endpoint):
        raise InvalidInputError(
            "BEM_PANEL_RANGE",
            "/singular_point",
            "Expected a strictly interior point unless this singularity supports endpoints.",
        )
    if type(order) is not int or not 2 <= order <= 256:
        raise InvalidInputError("BEM_PANEL_ORDER", "/order", "Expected quadrature order from 2 through 256.")
    try:
        value = complex(density(float(singular_point)))
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise InvalidInputError("BEM_PANEL_DENSITY", "/density", "Density evaluation failed.") from exc
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise InvalidInputError("BEM_PANEL_DENSITY", "/density", "Density must be finite.")
    from aura.fields.numerical import gauss_legendre_rule

    nodes, weights = gauss_legendre_rule(order)
    return value, nodes, weights


def _split_gauss_integral(
    function: Callable[[float], complex],
    left: float,
    singular_point: float,
    right: float,
    nodes: tuple[float, ...],
    weights: tuple[float, ...],
) -> complex:
    real_terms: list[float] = []
    imag_terms: list[float] = []
    for panel_left, panel_right in ((left, singular_point), (singular_point, right)):
        if panel_left == panel_right:
            continue
        midpoint = 0.5 * (panel_left + panel_right)
        half_width = 0.5 * (panel_right - panel_left)
        for node, weight in zip(nodes, weights, strict=True):
            position = midpoint + half_width * node
            value = half_width * weight * function(position)
            real_terms.append(value.real)
            imag_terms.append(value.imag)
    result = complex(math.fsum(real_terms), math.fsum(imag_terms))
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError("BEM_PANEL_RANGE", "/panel", "Panel integral is outside binary64 range.")
    return result


def _density_slope(
    derivative: Callable[[float], float | complex] | None,
    singular_point: float,
) -> complex:
    if derivative is None:
        return 0j
    if not callable(derivative):
        raise InvalidInputError("BEM_PANEL_DENSITY", "/density_derivative", "Expected a callable derivative.")
    try:
        value = complex(derivative(singular_point))
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise InvalidInputError(
            "BEM_PANEL_DENSITY", "/density_derivative", "Density derivative evaluation failed."
        ) from exc
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise InvalidInputError("BEM_PANEL_DENSITY", "/density_derivative", "Derivative must be finite.")
    return value


def integrate_cauchy_principal_value_panel(
    density: Callable[[float], float | complex],
    left: float,
    right: float,
    singular_point: float,
    *,
    density_derivative: Callable[[float], float | complex] | None = None,
    order: int = 32,
) -> complex:
    """Integrate ``density(s)/(2*pi*(s-singular_point))`` in principal value.

    The constant density at the collocation point is integrated analytically;
    when supplied, its linear Taylor term is integrated analytically too.
    Gauss-Legendre quadrature sees only the regular density remainder.
    One-sided endpoint collocation is rejected; both sides of a join must be
    combined in this interval so their principal values are taken together.
    """
    density_at_point, nodes, weights = _panel_inputs(
        density, left, right, singular_point, order
    )
    slope = _density_slope(density_derivative, float(singular_point))
    density_value = lambda position: complex(density(position))
    regular = _split_gauss_integral(
        lambda position: (
            density_value(position) - density_at_point - slope * (position - singular_point)
        ) / (position - singular_point),
        float(left),
        float(singular_point),
        float(right),
        nodes,
        weights,
    )
    jump_log = math.log((right - singular_point) / (singular_point - left))
    result = (regular + density_at_point * jump_log + slope * (right - left)) / (2.0 * math.pi)
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError("BEM_PANEL_RANGE", "/panel", "Panel integral is outside binary64 range.")
    return result


def integrate_logarithmic_panel(
    density: Callable[[float], float | complex],
    left: float,
    right: float,
    singular_point: float,
    *,
    log_scale: float,
    density_derivative: Callable[[float], float | complex] | None = None,
    order: int = 32,
) -> complex:
    """Integrate ``density(s)*log(log_scale/abs(s-singular_point))``.

    The constant-density logarithm is integrated exactly; when supplied, the
    linear Taylor term is integrated exactly too. ``log_scale`` must be
    expressed in the same coordinate units as the panel. Endpoint singularities
    are supported because the logarithm is integrable there.
    """
    density_at_point, nodes, weights = _panel_inputs(
        density, left, right, singular_point, order, allow_endpoint=True
    )
    slope = _density_slope(density_derivative, float(singular_point))
    if (type(log_scale) not in (int, float) or type(log_scale) is bool
            or not math.isfinite(log_scale) or log_scale <= 0.0):
        raise InvalidInputError("BEM_PANEL_SCALE", "/log_scale", "Expected a finite positive length scale.")

    def primitive(offset: float) -> float:
        if offset == 0.0:
            return 0.0
        return offset * (math.log(log_scale / abs(offset)) + 1.0)

    def first_moment_primitive(offset: float) -> float:
        if offset == 0.0:
            return 0.0
        return 0.5 * offset**2 * math.log(log_scale / abs(offset)) + 0.25 * offset**2

    density_value = lambda position: complex(density(position))
    regular = _split_gauss_integral(
        lambda position: (
            density_value(position) - density_at_point - slope * (position - singular_point)
        )
        * math.log(log_scale / abs(position - singular_point)),
        float(left),
        float(singular_point),
        float(right),
        nodes,
        weights,
    )
    constant_part = density_at_point * (
        primitive(float(right) - float(singular_point))
        - primitive(float(left) - float(singular_point))
    )
    linear_part = slope * (
        first_moment_primitive(float(right) - float(singular_point))
        - first_moment_primitive(float(left) - float(singular_point))
    )
    result = regular + constant_part + linear_part
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError("BEM_PANEL_RANGE", "/panel", "Panel integral is outside binary64 range.")
    return result


def integrate_direct_sphere_maue_panel(
    sphere_radius_m: float,
    plane_gap_m: float,
    field_theta_rad: float,
    panel_left_theta_rad: float,
    panel_right_theta_rad: float,
    pressure: Callable[[float], float | complex],
    pressure_tangent_derivative: Callable[[float], float | complex],
    *,
    wave_number_rad_m: float,
    azimuth_samples: int,
    meridian_order: int,
) -> complex:
    """Integrate one direct Maue sphere panel with its singular corrections.

    The sphere uses AURA's inward normal and an axisymmetric pressure trace.
    The direct zero-mode ring kernel is evaluated only away from the field
    point; its Cauchy and logarithmic terms are subtracted before Gauss
    quadrature and restored with the panel product-integration primitives.
    The image term, Burton--Miller jump, other panels, and any matrix are
    outside this function.
    """
    for path, value in (
        ("/sphere_radius_m", sphere_radius_m),
        ("/plane_gap_m", plane_gap_m),
        ("/field_theta_rad", field_theta_rad),
        ("/panel_left_theta_rad", panel_left_theta_rad),
        ("/panel_right_theta_rad", panel_right_theta_rad),
        ("/wave_number_rad_m", wave_number_rad_m),
    ):
        if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value):
            raise InvalidInputError("BEM_PANEL_RANGE", path, "Expected a finite real value.")
    if sphere_radius_m <= 0.0 or plane_gap_m < 0.0 or wave_number_rad_m <= 0.0:
        raise InvalidInputError("BEM_PANEL_RANGE", "/geometry", "Radius and wave number must be positive; plane gap nonnegative.")
    if not (
        0.0 <= panel_left_theta_rad < field_theta_rad < panel_right_theta_rad <= math.pi
    ):
        raise InvalidInputError(
            "BEM_PANEL_RANGE", "/field_theta_rad", "Collocation must lie strictly inside a polar panel."
        )
    if not callable(pressure) or not callable(pressure_tangent_derivative):
        raise InvalidInputError("BEM_PANEL_DENSITY", "/pressure", "Expected pressure and tangent callables.")
    if type(azimuth_samples) is not int or azimuth_samples < 4:
        raise InvalidInputError("BEM_PANEL_ORDER", "/azimuth_samples", "Expected at least four azimuth samples.")
    if type(meridian_order) is not int or not 2 <= meridian_order <= 256:
        raise InvalidInputError("BEM_PANEL_ORDER", "/meridian_order", "Expected order from 2 through 256.")

    field_pressure = complex(pressure(field_theta_rad))
    field_tangent = complex(pressure_tangent_derivative(field_theta_rad))
    if not all(math.isfinite(value) for value in (
        field_pressure.real, field_pressure.imag, field_tangent.real, field_tangent.imag
    )):
        raise InvalidInputError("BEM_PANEL_DENSITY", "/pressure", "Trace values must be finite.")

    from aura.fields._bem_axisymmetric import integrate_neumann_ring_burton_miller_terms_zero_mode
    from aura.fields.numerical import gauss_legendre_rule

    radius = float(sphere_radius_m)
    plane_gap = float(plane_gap_m)
    theta_f = float(field_theta_rad)
    wave_number = float(wave_number_rad_m)
    sin_f, cos_f = math.sin(theta_f), math.cos(theta_f)
    field_radius = radius * sin_f
    field_height = plane_gap + radius * (1.0 + cos_f)
    field_normal = (-sin_f, -cos_f)
    cauchy_coefficient = field_tangent
    logarithmic_coefficient = radius * wave_number**2 * field_pressure / (2.0 * math.pi)
    logarithmic_scale = 8.0 * sin_f
    nodes, weights = gauss_legendre_rule(meridian_order)
    real_terms: list[float] = []
    imag_terms: list[float] = []

    for lower, upper in ((float(panel_left_theta_rad), theta_f), (theta_f, float(panel_right_theta_rad))):
        midpoint = 0.5 * (lower + upper)
        half_width = 0.5 * (upper - lower)
        for node, weight in zip(nodes, weights, strict=True):
            theta = midpoint + half_width * node
            source_radius = radius * math.sin(theta)
            source_height = plane_gap + radius * (1.0 + math.cos(theta))
            source_normal = (-math.sin(theta), -math.cos(theta))
            direct, _ = integrate_neumann_ring_burton_miller_terms_zero_mode(
                field_radius,
                field_height,
                field_normal,
                source_radius,
                source_height,
                source_normal,
                pressure_pa=pressure(theta),
                pressure_tangent_derivative_pa_m=pressure_tangent_derivative(theta),
                wave_number_rad_m=wave_number,
                azimuth_samples=azimuth_samples,
            )
            offset = theta - theta_f
            weighted_ring = source_radius * radius * direct
            remainder = (
                weighted_ring
                - cauchy_coefficient / (2.0 * math.pi * offset)
                - logarithmic_coefficient * math.log(logarithmic_scale / abs(offset))
            )
            value = half_width * weight * remainder
            real_terms.append(value.real)
            imag_terms.append(value.imag)

    principal_value = integrate_cauchy_principal_value_panel(
        lambda _: cauchy_coefficient,
        float(panel_left_theta_rad),
        float(panel_right_theta_rad),
        theta_f,
        order=meridian_order,
    )
    logarithm = logarithmic_coefficient * integrate_logarithmic_panel(
        lambda _: 1.0,
        float(panel_left_theta_rad),
        float(panel_right_theta_rad),
        theta_f,
        log_scale=logarithmic_scale,
        order=meridian_order,
    )
    result = complex(math.fsum(real_terms), math.fsum(imag_terms)) + principal_value + logarithm
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError("BEM_PANEL_RANGE", "/panel", "Direct sphere Maue panel is outside binary64 range.")
    return result
