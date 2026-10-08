"""Zero-azimuthal-mode ring integrals for the rigid half-space kernel."""

from __future__ import annotations

import math

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields._bem_green import (
    _free_space_mixed_normal_derivative,
    neumann_half_space_green,
)

MAX_BEM_AZIMUTH_SAMPLES = 65_536


def _nonnegative(value: float, path: str) -> float:
    if type(value) not in (int, float) or type(value) is bool or not math.isfinite(value) or value < 0:
        raise InvalidInputError("BEM_RING_GEOMETRY", path, "Expected a finite nonnegative length in metres.")
    return float(value)


def _compensated_add(total: complex, correction: complex, term: complex) -> tuple[complex, complex]:
    adjusted = term - correction
    updated = total + adjusted
    return updated, (updated - total) - adjusted


def _unit_normal_rz(value: tuple[float, float], path: str) -> tuple[float, float]:
    if type(value) not in (tuple, list) or len(value) != 2:
        raise InvalidInputError("BEM_RING_NORMAL", path, "Expected a unit (radial, height) normal.")
    if any(type(x) not in (int, float) or type(x) is bool or not math.isfinite(x) for x in value):
        raise InvalidInputError("BEM_RING_NORMAL", path, "Expected finite real normal components.")
    normal = (float(value[0]), float(value[1]))
    if not math.isclose(math.hypot(*normal), 1.0, rel_tol=0.0, abs_tol=64 * math.ulp(1.0)):
        raise InvalidInputError("BEM_RING_NORMAL", path, "Expected a unit (radial, height) normal.")
    return normal


def _complete_elliptic_k_from_complementary_modulus(value: float) -> float:
    """Return Legendre K using Gauss's AGM, with the complement as input."""
    arithmetic, geometric = 1.0, value
    for _ in range(64):
        next_arithmetic = 0.5 * (arithmetic + geometric)
        next_geometric = math.sqrt(arithmetic * geometric)
        arithmetic, geometric = next_arithmetic, next_geometric
        if arithmetic - geometric <= 2 * math.ulp(arithmetic):
            return math.pi / (2 * (0.5 * (arithmetic + geometric)))
    raise NumericalDomainError("BEM_ELLIPTIC_AGM", "/geometry", "AGM iteration did not converge.")


def _complete_elliptic_k_e_and_derivatives(
    parameter: float, complementary_modulus: float
) -> tuple[float, float, float, float]:
    """Return K, E, dK/dm and d²K/dm² for Legendre parameter m."""
    if (not math.isfinite(parameter) or not 0.0 <= parameter <= 1.0
            or not math.isfinite(complementary_modulus) or complementary_modulus <= 0.0):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Elliptic parameter is outside its stable range.")
    if parameter < 1e-4:
        coefficient = 1.0
        power = 1.0
        k_sum = 1.0
        e_sum = 1.0
        k_first = 0.0
        k_second = 0.0
        for order in range(1, 9):
            coefficient *= ((2 * order - 1) / (2 * order)) ** 2
            power *= parameter
            k_sum += coefficient * power
            e_sum += coefficient * power / (1 - 2 * order)
            k_first += order * coefficient * power / parameter if parameter else (
                coefficient if order == 1 else 0.0
            )
            k_second += order * (order - 1) * coefficient * power / (parameter * parameter) if parameter else (
                2 * coefficient if order == 2 else 0.0
            )
        scale = math.pi / 2.0
        return scale * k_sum, scale * e_sum, scale * k_first, scale * k_second

    arithmetic, geometric = 1.0, complementary_modulus
    correction = 0.5 * parameter
    factor = 1.0
    for _ in range(64):
        cn = 0.5 * (arithmetic - geometric)
        if cn == 0.0:
            break
        correction += factor * cn * cn
        factor *= 2.0
        arithmetic, geometric = 0.5 * (arithmetic + geometric), math.sqrt(arithmetic * geometric)
        if arithmetic - geometric <= 2 * math.ulp(arithmetic):
            break
    else:
        raise NumericalDomainError("BEM_ELLIPTIC_AGM", "/geometry", "AGM iteration did not converge.")
    elliptic_k = math.pi / (2.0 * arithmetic)
    elliptic_e = elliptic_k * (1.0 - correction)
    one_minus_parameter = complementary_modulus * complementary_modulus
    elliptic_k_first = (elliptic_e / one_minus_parameter - elliptic_k) / (2.0 * parameter)
    elliptic_e_first = (elliptic_e - elliptic_k) / (2.0 * parameter)
    numerator = elliptic_e / one_minus_parameter - elliptic_k
    numerator_first = (
        elliptic_e_first / one_minus_parameter
        + elliptic_e / one_minus_parameter**2
        - elliptic_k_first
    )
    elliptic_k_second = numerator_first / (2.0 * parameter) - numerator / (2.0 * parameter**2)
    return elliptic_k, elliptic_e, elliptic_k_first, elliptic_k_second


def integrate_laplace_ring_mixed_normal_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    field_normal_rz: tuple[float, float],
    source_radius_m: float,
    source_height_m: float,
    source_normal_rz: tuple[float, float],
) -> float:
    """Return the exact azimuth integral of the static mixed-normal kernel.

    This evaluates ``d_n_field d_n_source (1/(4*pi*R))`` by differentiating
    the elliptic-integral ring potential. It excludes the meridional surface
    Jacobian and does not regularize coincident rings.
    """
    rf = _nonnegative(field_radius_m, "/field_radius_m")
    zf = _nonnegative(field_height_m, "/field_height_m")
    rs = _nonnegative(source_radius_m, "/source_radius_m")
    zs = _nonnegative(source_height_m, "/source_height_m")
    nfr, nfz = _unit_normal_rz(field_normal_rz, "/field_normal_rz")
    nsr, nsz = _unit_normal_rz(source_normal_rz, "/source_normal_rz")
    d = zf - zs
    separation = math.hypot(rf - rs, d)
    if separation == 0.0:
        raise InvalidInputError(
            "BEM_RING_SINGULAR", "/source_radius_m",
            "Coincident meridional rings have a singular Laplace mixed-normal integral.",
        )

    p = rf + rs
    a = p * p + d * d
    b = 4.0 * rf * rs
    scale = math.sqrt(a)
    parameter = b / a
    complementary_modulus = separation / scale
    if (not math.isfinite(parameter) or not 0.0 <= parameter <= 1.0
            or complementary_modulus == 0.0 or complementary_modulus > 1.0):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Elliptic parameter is outside its stable range.")
    elliptic_k, _, k_first, k_second = _complete_elliptic_k_e_and_derivatives(
        parameter, complementary_modulus
    )

    complement_square = separation * separation
    complement_first = (2.0 * (rf - rs), 2.0 * d, -2.0 * (rf - rs), -2.0 * d)
    a_first = (2.0 * p, 2.0 * d, 2.0 * p, -2.0 * d)
    a_second = [[0.0] * 4 for _ in range(4)]
    for i, j in ((0, 0), (0, 2), (2, 0), (2, 2), (1, 1), (3, 3)):
        a_second[i][j] = 2.0
    a_second[1][3] = a_second[3][1] = -2.0
    complement_second = [[0.0] * 4 for _ in range(4)]
    for i, j in ((0, 0), (2, 2), (1, 1), (3, 3)):
        complement_second[i][j] = 2.0
    complement_second[0][2] = complement_second[2][0] = -2.0
    complement_second[1][3] = complement_second[3][1] = -2.0
    t_first = tuple(
        complement_first[i] / a - complement_square * a_first[i] / a**2
        for i in range(4)
    )
    t_second = [[
        complement_second[i][j] / a
        - (complement_first[i] * a_first[j] + complement_first[j] * a_first[i]
           + complement_square * a_second[i][j]) / a**2
        + 2.0 * complement_square * a_first[i] * a_first[j] / a**3
        for j in range(4)
    ] for i in range(4)]
    s_first = tuple(a_first[i] / (2.0 * scale) for i in range(4))
    s_second = [[
        a_second[i][j] / (2.0 * scale) - a_first[i] * a_first[j] / (4.0 * scale**3)
        for j in range(4)
    ] for i in range(4)]

    hessian = [[
        (k_second * t_first[i] * t_first[j] / scale
         - k_first * t_second[i][j] / scale
         + k_first * (t_first[i] * s_first[j] + t_first[j] * s_first[i]) / scale**2
         - elliptic_k * s_second[i][j] / scale**2
         + 2.0 * elliptic_k * s_first[i] * s_first[j] / scale**3) / math.pi
        for j in range(4)
    ] for i in range(4)]
    result = (
        nfr * nsr * hessian[0][2]
        + nfr * nsz * hessian[0][3]
        + nfz * nsr * hessian[1][2]
        + nfz * nsz * hessian[1][3]
    )
    if not math.isfinite(result):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Mixed-normal ring integral is outside binary64 range.")
    return result


def integrate_laplace_ring_green_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    source_radius_m: float,
    source_height_m: float,
) -> float:
    """Return the exact azimuth integral of ``1/(4*pi*R)`` for two rings.

    This is the static singular part of the free-space Helmholtz ring kernel.
    It analytically handles the azimuth integral only; coincident meridional
    rings remain logarithmically singular and are rejected for separate
    meridional singular treatment.
    """
    field_radius = _nonnegative(field_radius_m, "/field_radius_m")
    field_height = _nonnegative(field_height_m, "/field_height_m")
    source_radius = _nonnegative(source_radius_m, "/source_radius_m")
    source_height = _nonnegative(source_height_m, "/source_height_m")
    vertical_separation = field_height - source_height
    meridional_separation = math.hypot(field_radius - source_radius, vertical_separation)
    if meridional_separation == 0.0:
        raise InvalidInputError(
            "BEM_RING_SINGULAR", "/source_radius_m",
            "Coincident meridional rings have a logarithmically singular Laplace integral.",
        )
    radius_sum = field_radius + source_radius
    scale = math.hypot(radius_sum, vertical_separation)
    if not math.isfinite(scale) or scale == 0.0:
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Ring separation is outside binary64 range.")
    complementary_modulus = meridional_separation / scale
    if complementary_modulus == 0.0 or complementary_modulus > 1.0:
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Elliptic modulus is outside its stable range.")
    elliptic_k = _complete_elliptic_k_from_complementary_modulus(complementary_modulus)
    result = elliptic_k / (math.pi * scale)
    if not math.isfinite(result):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Laplace ring integral is outside binary64 range.")
    return result


def integrate_laplace_ring_green_gradient_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    source_radius_m: float,
    source_height_m: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return the exact ring integrals of the static field/source gradients.

    The returned tuples are ``(radial, height)`` derivatives of the scalar
    ring potential with respect to the field and source meridian coordinates.
    The coincident meridional pair is rejected because its scalar ring
    potential is logarithmically singular.
    """
    rf = _nonnegative(field_radius_m, "/field_radius_m")
    zf = _nonnegative(field_height_m, "/field_height_m")
    rs = _nonnegative(source_radius_m, "/source_radius_m")
    zs = _nonnegative(source_height_m, "/source_height_m")
    d = zf - zs
    separation = math.hypot(rf - rs, d)
    if separation == 0.0:
        raise InvalidInputError(
            "BEM_RING_SINGULAR", "/source_radius_m",
            "Coincident meridional rings have a logarithmically singular Laplace integral.",
        )
    if rf == 0.0 or rs == 0.0:
        distance = math.hypot(rf - rs, d)
        inverse_cube = 1.0 / (2.0 * distance**3)
        return (
            (0.0 if rf == 0.0 else -rf * inverse_cube, -d * inverse_cube),
            (0.0 if rs == 0.0 else -rs * inverse_cube, d * inverse_cube),
        )
    p = rf + rs
    a = p * p + d * d
    b = 4.0 * rf * rs
    scale = math.sqrt(a)
    parameter = b / a
    complementary_modulus = separation / scale
    if (not math.isfinite(parameter) or not 0.0 <= parameter <= 1.0
            or complementary_modulus == 0.0 or complementary_modulus > 1.0):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Elliptic parameter is outside its stable range.")
    elliptic_k, _, k_first, _ = _complete_elliptic_k_e_and_derivatives(
        parameter, complementary_modulus
    )
    a_first = (2.0 * p, 2.0 * d, 2.0 * p, -2.0 * d)
    complement_square = separation * separation
    complement_first = (2.0 * (rf - rs), 2.0 * d, -2.0 * (rf - rs), -2.0 * d)
    t_first = tuple(
        complement_first[i] / a - complement_square * a_first[i] / a**2
        for i in range(4)
    )
    s_first = tuple(a_first[i] / (2.0 * scale) for i in range(4))
    gradient = tuple(
        (-k_first * t_first[i] / scale - elliptic_k * s_first[i] / scale**2) / math.pi
        for i in range(4)
    )
    if not all(math.isfinite(component) for component in gradient):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Ring gradient is outside binary64 range.")
    return (gradient[0], gradient[1]), (gradient[2], gradient[3])


def integrate_laplace_ring_green_cos_moment_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    source_radius_m: float,
    source_height_m: float,
) -> tuple[float, float]:
    """Return ``integral(cos(phi) G_L dphi)`` and its field-height derivative.

    The exact elliptic expression supplies the static azimuthal cosine moment
    needed by axisymmetric Maue terms. Coincident meridional rings retain the
    logarithmic scalar singularity and are rejected.
    """
    rf = _nonnegative(field_radius_m, "/field_radius_m")
    zf = _nonnegative(field_height_m, "/field_height_m")
    rs = _nonnegative(source_radius_m, "/source_radius_m")
    zs = _nonnegative(source_height_m, "/source_height_m")
    d = zf - zs
    separation = math.hypot(rf - rs, d)
    if separation == 0.0:
        raise InvalidInputError(
            "BEM_RING_SINGULAR", "/source_radius_m",
            "Coincident meridional rings have a logarithmically singular Laplace integral.",
        )
    if rf == 0.0 or rs == 0.0:
        return 0.0, 0.0
    p = rf + rs
    a = p * p + d * d
    scale = math.sqrt(a)
    complementary_modulus = separation / scale
    parameter = 1.0 - complementary_modulus * complementary_modulus
    elliptic_k, elliptic_e, k_first, _ = _complete_elliptic_k_e_and_derivatives(
        parameter, complementary_modulus
    )
    if parameter < 1e-4:
        coefficients = [1.0]
        for order in range(1, 9):
            coefficients.append(
                coefficients[-1] * ((2 * order - 1) / (2 * order)) ** 2
            )
        moment = math.fsum(
            2.0 * order / (2 * order - 1) * coefficients[order] * parameter ** (order - 1)
            for order in range(1, 9)
        ) - 0.5 * math.fsum(
            coefficients[order] * parameter**order for order in range(9)
        )
        moment_first = math.fsum(
            (order - 1) * 2.0 * order / (2 * order - 1)
            * coefficients[order] * parameter ** (order - 2)
            for order in range(2, 9)
        ) - 0.5 * math.fsum(
            order * coefficients[order] * parameter ** (order - 1)
            for order in range(1, 9)
        )
    else:
        elliptic_e_first = (elliptic_e - elliptic_k) / (2.0 * parameter)
        numerator = 2.0 * (elliptic_k - elliptic_e) / parameter - elliptic_k
        numerator_first = (
            2.0 * ((k_first - elliptic_e_first) * parameter - (elliptic_k - elliptic_e))
            / parameter**2
            - k_first
        )
        moment = numerator / math.pi
        moment_first = numerator_first / math.pi
    m_field_height = -2.0 * d / a + 2.0 * separation * separation * d / a**2
    result = moment / scale
    derivative = moment_first * m_field_height / scale - moment * d / scale**3
    if not math.isfinite(result) or not math.isfinite(derivative):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Cosine ring moment is outside binary64 range.")
    return result, derivative


def integrate_helmholtz_ring_green_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    source_radius_m: float,
    source_height_m: float,
    *,
    wave_number_rad_m: float,
    azimuth_samples: int,
) -> complex:
    """Integrate the direct Helmholtz Green ring after static singularity split.

    The Laplace `1/(4*pi*R)` contribution is evaluated with the elliptic AGM
    formula. Only `(exp(i*k*R)-1)/(4*pi*R)` is midpoint-integrated. This
    improves near-diagonal treatment of the scalar ring kernel but does not
    regularize derivative kernels or integrate the meridional diagonal.
    """
    field_radius = _nonnegative(field_radius_m, "/field_radius_m")
    field_height = _nonnegative(field_height_m, "/field_height_m")
    source_radius = _nonnegative(source_radius_m, "/source_radius_m")
    source_height = _nonnegative(source_height_m, "/source_height_m")
    if type(azimuth_samples) is not int or not 4 <= azimuth_samples <= MAX_BEM_AZIMUTH_SAMPLES:
        raise InvalidInputError("BEM_RING_QUADRATURE", "/azimuth_samples", "Azimuth count is outside its supported range.")
    if type(wave_number_rad_m) not in (int, float) or type(wave_number_rad_m) is bool:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")
    wave_number = float(wave_number_rad_m)
    if not math.isfinite(wave_number) or wave_number <= 0.0:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")

    laplace_part = integrate_laplace_ring_green_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    total = 0j
    correction = 0j
    weight = 2.0 * math.pi / azimuth_samples
    for index in range(azimuth_samples):
        angle = 2.0 * math.pi * (index + 0.5) / azimuth_samples
        radius = math.sqrt(
            (field_radius - source_radius) ** 2
            + 4.0 * field_radius * source_radius * math.sin(0.5 * angle) ** 2
            + (field_height - source_height) ** 2
        )
        phase = wave_number * radius
        if not math.isfinite(phase):
            raise NumericalDomainError("BEM_RING_RANGE", "/wave_number_rad_m", "Kernel phase is outside binary64 range.")
        # Stable forms of cos(phase)-1 and sin(phase) avoid cancellation near R=0.
        residual = complex(
            -2.0 * math.sin(0.5 * phase) ** 2,
            math.sin(phase),
        ) / (4.0 * math.pi * radius)
        total, correction = _compensated_add(total, correction, weight * residual)
    result = complex(laplace_part, 0.0) + total
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Helmholtz ring integral is outside binary64 range.")
    return result


def integrate_helmholtz_ring_green_gradient_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    source_radius_m: float,
    source_height_m: float,
    *,
    wave_number_rad_m: float,
    azimuth_samples: int,
) -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    """Integrate direct Helmholtz ring gradients with static subtraction.

    Exact elliptic derivatives supply the static Laplace gradients. Midpoint
    quadrature evaluates only the smooth dynamic residual. The result excludes
    the meridional surface Jacobian and does not treat a coincident ring pair.
    """
    field_radius = _nonnegative(field_radius_m, "/field_radius_m")
    field_height = _nonnegative(field_height_m, "/field_height_m")
    source_radius = _nonnegative(source_radius_m, "/source_radius_m")
    source_height = _nonnegative(source_height_m, "/source_height_m")
    if type(azimuth_samples) is not int or not 4 <= azimuth_samples <= MAX_BEM_AZIMUTH_SAMPLES:
        raise InvalidInputError("BEM_RING_QUADRATURE", "/azimuth_samples", "Azimuth count is outside its supported range.")
    if type(wave_number_rad_m) not in (int, float) or type(wave_number_rad_m) is bool:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")
    wave_number = float(wave_number_rad_m)
    if not math.isfinite(wave_number) or wave_number <= 0.0:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")

    static_field, static_source = integrate_laplace_ring_green_gradient_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    field_residual = [0j, 0j]
    field_correction = [0j, 0j]
    source_residual = [0j, 0j]
    source_correction = [0j, 0j]
    weight = 2.0 * math.pi / azimuth_samples
    for index in range(azimuth_samples):
        angle = 2.0 * math.pi * (index + 0.5) / azimuth_samples
        cosine, sine = math.cos(angle), math.sin(angle)
        displacement = (
            field_radius - source_radius * cosine,
            -source_radius * sine,
            field_height - source_height,
        )
        radius = math.hypot(*displacement)
        phase = wave_number * radius
        if not math.isfinite(phase):
            raise NumericalDomainError("BEM_RING_RANGE", "/wave_number_rad_m", "Kernel phase is outside binary64 range.")
        residual_factor = complex(
            2.0 * math.sin(0.5 * phase) ** 2 - phase * math.sin(phase),
            phase * math.cos(phase) - math.sin(phase),
        ) / (4.0 * math.pi * radius**3)
        field_vectors = (displacement[0], displacement[2])
        source_vectors = (
            -displacement[0] * cosine - displacement[1] * sine,
            -displacement[2],
        )
        for axis in range(2):
            field_term = weight * residual_factor * field_vectors[axis]
            adjusted = field_term - field_correction[axis]
            updated = field_residual[axis] + adjusted
            field_correction[axis] = (updated - field_residual[axis]) - adjusted
            field_residual[axis] = updated
            source_term = weight * residual_factor * source_vectors[axis]
            adjusted = source_term - source_correction[axis]
            updated = source_residual[axis] + adjusted
            source_correction[axis] = (updated - source_residual[axis]) - adjusted
            source_residual[axis] = updated
    field_gradient = tuple(complex(static_field[i]) + field_residual[i] for i in range(2))
    source_gradient = tuple(complex(static_source[i]) + source_residual[i] for i in range(2))
    if not all(math.isfinite(x.real) and math.isfinite(x.imag) for x in (*field_gradient, *source_gradient)):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Helmholtz ring gradient is outside binary64 range.")
    return field_gradient, source_gradient


def _integrate_helmholtz_ring_green_and_gradient_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    source_radius_m: float,
    source_height_m: float,
    *,
    wave_number_rad_m: float,
    azimuth_samples: int,
) -> tuple[complex, tuple[complex, complex], tuple[complex, complex]]:
    """Evaluate scalar and gradient ring kernels in one azimuthal pass.

    This is an arithmetic-sharing primitive for the bounded CBIE research
    action. The static Laplace pieces remain the same elliptic evaluations as
    the separate routines above; only the midpoint loop is shared.
    """
    field_radius = _nonnegative(field_radius_m, "/field_radius_m")
    field_height = _nonnegative(field_height_m, "/field_height_m")
    source_radius = _nonnegative(source_radius_m, "/source_radius_m")
    source_height = _nonnegative(source_height_m, "/source_height_m")
    if type(azimuth_samples) is not int or not 4 <= azimuth_samples <= MAX_BEM_AZIMUTH_SAMPLES:
        raise InvalidInputError("BEM_RING_QUADRATURE", "/azimuth_samples", "Azimuth count is outside its supported range.")
    if type(wave_number_rad_m) not in (int, float) or type(wave_number_rad_m) is bool:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")
    wave_number = float(wave_number_rad_m)
    if not math.isfinite(wave_number) or wave_number <= 0.0:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")

    laplace_scalar = integrate_laplace_ring_green_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    static_field, static_source = integrate_laplace_ring_green_gradient_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    scalar_total = 0j
    scalar_correction = 0j
    field_residual = [0j, 0j]
    field_correction = [0j, 0j]
    source_residual = [0j, 0j]
    source_correction = [0j, 0j]
    weight = 2.0 * math.pi / azimuth_samples
    for index in range(azimuth_samples):
        angle = 2.0 * math.pi * (index + 0.5) / azimuth_samples
        cosine, sine = math.cos(angle), math.sin(angle)
        displacement = (
            field_radius - source_radius * cosine,
            -source_radius * sine,
            field_height - source_height,
        )
        radius = math.hypot(*displacement)
        phase = wave_number * radius
        if not math.isfinite(phase):
            raise NumericalDomainError("BEM_RING_RANGE", "/wave_number_rad_m", "Kernel phase is outside binary64 range.")
        sine_half_squared = math.sin(0.5 * phase) ** 2
        sine_phase = math.sin(phase)
        cosine_phase = math.cos(phase)
        scalar_residual = complex(-2.0 * sine_half_squared, sine_phase) / (4.0 * math.pi * radius)
        scalar_total, scalar_correction = _compensated_add(
            scalar_total, scalar_correction, weight * scalar_residual
        )
        gradient_factor = complex(
            2.0 * sine_half_squared - phase * sine_phase,
            phase * cosine_phase - sine_phase,
        ) / (4.0 * math.pi * radius**3)
        field_vectors = (displacement[0], displacement[2])
        source_vectors = (
            -displacement[0] * cosine - displacement[1] * sine,
            -displacement[2],
        )
        for axis in range(2):
            field_term = weight * gradient_factor * field_vectors[axis]
            adjusted = field_term - field_correction[axis]
            updated = field_residual[axis] + adjusted
            field_correction[axis] = (updated - field_residual[axis]) - adjusted
            field_residual[axis] = updated
            source_term = weight * gradient_factor * source_vectors[axis]
            adjusted = source_term - source_correction[axis]
            updated = source_residual[axis] + adjusted
            source_correction[axis] = (updated - source_residual[axis]) - adjusted
            source_residual[axis] = updated

    scalar = complex(laplace_scalar, 0.0) + scalar_total
    field_gradient = tuple(complex(static_field[i]) + field_residual[i] for i in range(2))
    source_gradient = tuple(complex(static_source[i]) + source_residual[i] for i in range(2))
    if not all(math.isfinite(value.real) and math.isfinite(value.imag) for value in (scalar, *field_gradient, *source_gradient)):
        raise NumericalDomainError("BEM_RING_RANGE", "/geometry", "Helmholtz ring integral is outside binary64 range.")
    return scalar, field_gradient, source_gradient


def _integrate_ring_image_mixed_normal(
    field_radius: float,
    field_height: float,
    field_normal: tuple[float, float, float],
    source_radius: float,
    source_height: float,
    source_normal_rz: tuple[float, float],
    pressure: complex,
    wave_number: float,
    samples: int,
    rule: str,
    split_multiple: float,
) -> complex:
    """Integrate the image mixed-normal kernel with a periodic or split rule."""
    image_separation = math.hypot(field_radius - source_radius, field_height + source_height)
    if rule == "midpoint" or field_radius == 0.0 or source_radius == 0.0:
        cutoff = math.pi
    else:
        angular_scale = image_separation / math.sqrt(field_radius * source_radius)
        cutoff = min(math.pi, split_multiple * angular_scale)

    intervals = ((-math.pi, math.pi),) if cutoff == math.pi else (
        (-math.pi, -cutoff), (-cutoff, cutoff), (cutoff, math.pi)
    )
    total = 0j
    correction = 0j
    for lower, upper in intervals:
        width = (upper - lower) / samples
        for index in range(samples):
            angle = lower + (index + 0.5) * width
            cosine, sine = math.cos(angle), math.sin(angle)
            field = (field_radius, 0.0, field_height)
            source = (source_radius * cosine, source_radius * sine, -source_height)
            image_normal = (
                source_normal_rz[0] * cosine,
                source_normal_rz[0] * sine,
                -source_normal_rz[1],
            )
            term = pressure * _free_space_mixed_normal_derivative(
                field, source, field_normal, image_normal, wave_number
            )
            total, correction = _compensated_add(total, correction, width * term)
    if not math.isfinite(total.real) or not math.isfinite(total.imag):
        raise NumericalDomainError("BEM_RING_RANGE", "/azimuth_samples", "Image ring integral is outside binary64 range.")
    return total


def _cross(left: tuple[float, float, float], right: tuple[complex, complex, complex]):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def integrate_neumann_ring_burton_miller_terms_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    field_normal_rz: tuple[float, float],
    source_radius_m: float,
    source_height_m: float,
    source_normal_rz: tuple[float, float],
    *,
    pressure_pa: complex,
    pressure_tangent_derivative_pa_m: complex,
    wave_number_rad_m: float,
    azimuth_samples: int,
    image_quadrature: str = "midpoint",
    image_split_multiple: float = 8.0,
) -> tuple[complex, complex]:
    """Integrate separated-ring Burton–Miller hypersingular contributions.

    Returns `(direct_maue, image_mixed_normal)` as unweighted azimuth
    integrals. The direct singular kernel is written with the Maue tangential
    identity; the smooth but potentially near-singular plane-image term uses
    the direct mixed-normal derivative. Pressure and its meridional tangent
    derivative are prescribed at the source ring. The surface Jacobian
    `source_radius_m * ds` is excluded. This is a ring kernel only: it does
    not evaluate the singular meridional integral, jump terms, or a BIE.
    """
    field_radius = _nonnegative(field_radius_m, "/field_radius_m")
    field_height = _nonnegative(field_height_m, "/field_height_m")
    source_radius = _nonnegative(source_radius_m, "/source_radius_m")
    source_height = _nonnegative(source_height_m, "/source_height_m")
    npr, npz = _unit_normal_rz(field_normal_rz, "/field_normal_rz")
    nsr, nsz = _unit_normal_rz(source_normal_rz, "/source_normal_rz")
    if field_radius == source_radius and field_height == source_height:
        raise InvalidInputError(
            "BEM_RING_SINGULAR", "/source_radius_m",
            "The direct diagonal needs meridional singular quadrature.",
        )
    if type(azimuth_samples) is not int or not 4 <= azimuth_samples <= MAX_BEM_AZIMUTH_SAMPLES:
        raise InvalidInputError("BEM_RING_QUADRATURE", "/azimuth_samples", "Azimuth count is outside its supported range.")
    if image_quadrature not in ("midpoint", "gap_scaled"):
        raise InvalidInputError("BEM_RING_QUADRATURE", "/image_quadrature", "Expected 'midpoint' or 'gap_scaled'.")
    if (type(image_split_multiple) not in (int, float) or type(image_split_multiple) is bool
            or not math.isfinite(image_split_multiple) or image_split_multiple <= 0):
        raise InvalidInputError(
            "BEM_RING_QUADRATURE", "/image_split_multiple", "Expected a finite positive angular-scale multiplier."
        )
    if type(wave_number_rad_m) not in (int, float) or type(wave_number_rad_m) is bool:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")
    for path, value in (
        ("/pressure_pa", pressure_pa),
        ("/pressure_tangent_derivative_pa_m", pressure_tangent_derivative_pa_m),
    ):
        if type(value) not in (int, float, complex) or type(value) is bool:
            raise InvalidInputError("BEM_RING_DENSITY", path, "Expected a finite real or complex value.")
        if not math.isfinite(complex(value).real) or not math.isfinite(complex(value).imag):
            raise InvalidInputError("BEM_RING_DENSITY", path, "Expected a finite real or complex value.")
    k = float(wave_number_rad_m)
    if not math.isfinite(k) or k <= 0:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")

    static_green = integrate_laplace_ring_green_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    static_cosine_green, static_cosine_height_gradient = integrate_laplace_ring_green_cos_moment_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    _, static_source_gradient = integrate_laplace_ring_green_gradient_zero_mode(
        field_radius, field_height, source_radius, source_height
    )
    static_direct = (
        k * k * complex(pressure_pa)
        * (npr * nsr * static_cosine_green + npz * nsz * static_green)
        + complex(pressure_tangent_derivative_pa_m)
        * (npr * static_cosine_height_gradient + npz * static_source_gradient[0])
    )
    direct_residual = 0j
    direct_correction = 0j
    weight = 2.0 * math.pi / azimuth_samples
    field_normal = (npr, 0.0, npz)
    for index in range(azimuth_samples):
        angle = 2.0 * math.pi * (index + 0.5) / azimuth_samples
        cosine, sine = math.cos(angle), math.sin(angle)
        field = (field_radius, 0.0, field_height)
        source = (source_radius * cosine, source_radius * sine, source_height)
        source_normal = (nsr * cosine, nsr * sine, nsz)
        displacement = tuple(a - b for a, b in zip(field, source, strict=True))
        radius = math.hypot(*displacement)
        phase = k * radius
        if not math.isfinite(phase):
            raise NumericalDomainError("BEM_RING_RANGE", "/wave_number_rad_m", "Kernel phase is outside binary64 range.")
        green_residual = complex(
            -2.0 * math.sin(0.5 * phase) ** 2,
            math.sin(phase),
        ) / (4.0 * math.pi * radius)
        gradient_residual_factor = complex(
            2.0 * math.sin(0.5 * phase) ** 2 - phase * math.sin(phase),
            phase * math.cos(phase) - math.sin(phase),
        ) / (4.0 * math.pi * radius**3)
        gradient_residual = tuple(gradient_residual_factor * value for value in displacement)

        # Axisymmetric pressure has only the meridional tangential derivative.
        source_tangent = (-nsz * cosine, -nsz * sine, nsr)
        grad_pressure = tuple(pressure_tangent_derivative_pa_m * x for x in source_tangent)
        direct_tangent_product = sum(
            a * b for a, b in zip(
                _cross(field_normal, gradient_residual),
                _cross(source_normal, grad_pressure),
                strict=True,
            )
        )
        normal_dot = npr * nsr * cosine + npz * nsz
        direct_maue_residual = (
            k * k * normal_dot * pressure_pa * green_residual + direct_tangent_product
        )

        direct_residual, direct_correction = _compensated_add(
            direct_residual, direct_correction, weight * direct_maue_residual
        )

    image_total = _integrate_ring_image_mixed_normal(
        field_radius,
        field_height,
        field_normal,
        source_radius,
        source_height,
        (nsr, nsz),
        complex(pressure_pa),
        k,
        azimuth_samples,
        image_quadrature,
        float(image_split_multiple),
    )
    result = (static_direct + direct_residual, image_total)
    if any(not math.isfinite(value.real) or not math.isfinite(value.imag) for value in result):
        raise NumericalDomainError("BEM_RING_RANGE", "/azimuth_samples", "Ring operator term is outside binary64 range.")
    return result


def integrate_neumann_ring_zero_mode(
    field_radius_m: float,
    field_height_m: float,
    source_radius_m: float,
    source_height_m: float,
    *,
    wave_number_rad_m: float,
    azimuth_samples: int,
) -> tuple[complex, tuple[complex, complex], tuple[complex, complex]]:
    """Midpoint-trapezoid integral of G_N around a circular source ring.

    Returns the unweighted azimuth integral of the Green function, then its
    field `(radial, height)` and source `(radial, height)` derivatives. The
    source-surface Jacobian `source_radius_m * ds` is deliberately excluded.
    The caller controls azimuth refinement; this routine makes no quadrature
    error or convergence claim. Meridionally coincident rings are rejected
    because the direct kernel is singular there.
    """
    field_radius = _nonnegative(field_radius_m, "/field_radius_m")
    field_height = _nonnegative(field_height_m, "/field_height_m")
    source_radius = _nonnegative(source_radius_m, "/source_radius_m")
    source_height = _nonnegative(source_height_m, "/source_height_m")
    if field_radius == source_radius and field_height == source_height:
        raise InvalidInputError("BEM_RING_SINGULAR", "/source_radius_m", "Coincident rings require singular treatment.")
    if type(azimuth_samples) is not int or not 4 <= azimuth_samples <= MAX_BEM_AZIMUTH_SAMPLES:
        raise InvalidInputError(
            "BEM_RING_QUADRATURE", "/azimuth_samples",
            f"Expected an integer from 4 through {MAX_BEM_AZIMUTH_SAMPLES}.",
        )
    if type(wave_number_rad_m) not in (int, float) or type(wave_number_rad_m) is bool:
        raise InvalidInputError("BEM_WAVE_NUMBER", "/wave_number_rad_m", "Expected a finite positive wave number.")

    totals = [0j] * 5
    corrections = [0j] * 5
    weight = 2.0 * math.pi / azimuth_samples
    for index in range(azimuth_samples):
        angle = 2.0 * math.pi * (index + 0.5) / azimuth_samples
        cosine = math.cos(angle)
        sine = math.sin(angle)
        kernel, grad_field, grad_source = neumann_half_space_green(
            (field_radius, 0.0, field_height),
            (source_radius * cosine, source_radius * sine, source_height),
            wave_number_rad_m=wave_number_rad_m,
        )
        terms = (
            kernel,
            grad_field[0],
            grad_field[2],
            grad_source[0] * cosine + grad_source[1] * sine,
            grad_source[2],
        )
        for component, term in enumerate(terms):
            totals[component], corrections[component] = _compensated_add(
                totals[component], corrections[component], term
            )

    result = (
        weight * totals[0],
        (weight * totals[1], weight * totals[2]),
        (weight * totals[3], weight * totals[4]),
    )
    if any(not math.isfinite(component.real) or not math.isfinite(component.imag)
           for value_group in (result[0:1], result[1], result[2]) for component in value_group):
        raise NumericalDomainError("BEM_RING_RANGE", "/azimuth_samples", "Ring integral is outside binary64 range.")
    return result
