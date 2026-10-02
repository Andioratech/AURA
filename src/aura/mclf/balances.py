"""Fixed-domain, peak-harmonic surface energy audits; not force or claim verdicts."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields import FieldSamples, mean_intensity_w_m2
from aura.units import _finite_scalar, _positive_finite, _scaled_ratio

ENERGY_BALANCE_VERSION = "ENERGY-BALANCE-1.0"
BALANCE_TOLERANCE = 8192 * sys.float_info.epsilon
_AXIS_NORMALS = (
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0),
)


def _finite_result(value: float, path: str) -> float:
    if not math.isfinite(value):
        raise NumericalDomainError("NUMERIC_RANGE", "/" + path, "Arithmetic is not finite.")
    return value


@dataclass(frozen=True, kw_only=True)
class SphereSurfaceQuadrature:
    """Immutable six-axis equal-area rule for the declared spherical surfaces."""

    center_m: tuple[float, float, float]
    radius_m: float

    def __post_init__(self) -> None:
        if type(self.center_m) not in (list, tuple) or len(self.center_m) != 3:
            raise InvalidInputError("BALANCE_SHAPE", "/center_m", "Expected three coordinates.")
        center = tuple(_finite_scalar(f"center_m/{i}", x) for i, x in enumerate(self.center_m))
        radius = _positive_finite("radius_m", self.radius_m)
        object.__setattr__(self, "center_m", center)
        object.__setattr__(self, "radius_m", radius)
        for i, normal in enumerate(_AXIS_NORMALS):
            for j in range(3):
                _finite_result(center[j] + radius * normal[j], f"surface/points/{i}/{j}")

    @property
    def normals(self) -> tuple[tuple[float, float, float], ...]:
        """Radial outward unit normals, ordered in antipodal pairs."""
        return _AXIS_NORMALS

    @property
    def coordinates_m(self) -> tuple[tuple[float, float, float], ...]:
        """The six axis endpoints; no angular interpolation is implied."""
        return tuple(
            tuple(
                _finite_result(c + self.radius_m * n, f"surface/points/{i}/{j}")
                for j, (c, n) in enumerate(zip(self.center_m, normal, strict=True))
            )
            for i, normal in enumerate(_AXIS_NORMALS)
        )

    @property
    def area_weights_m2(self) -> tuple[float, ...]:
        """Six equal weights whose sum is the declared complete sphere area."""
        weight = _scaled_ratio(
            "surface_area_weight_m2", (4.0, math.pi, self.radius_m, self.radius_m), (6.0,)
        )
        return (weight,) * len(_AXIS_NORMALS)

    @property
    def area_m2(self) -> float:
        return _finite_result(math.fsum(self.area_weights_m2), "surface/area_m2")


def integrate_sphere_flux_w(field: FieldSamples, surface: SphereSurfaceQuadrature) -> float:
    """Integrate sampled outward mean energy flux over a matching frozen sphere."""
    if type(field) is not FieldSamples:
        raise InvalidInputError("BALANCE_FIELD", "/field", "Expected FIELD-1.0 samples.")
    if type(surface) is not SphereSurfaceQuadrature:
        raise InvalidInputError("BALANCE_SURFACE", "/surface", "Expected a fixed sphere surface.")
    if field.coordinates_m != surface.coordinates_m:
        raise InvalidInputError(
            "BALANCE_SAMPLES",
            "/field/coordinates_m",
            "Field coordinates do not match this complete sphere rule.",
        )
    intensity = mean_intensity_w_m2(field)
    terms = []
    for i, (vector, normal, weight) in enumerate(
        zip(intensity, surface.normals, surface.area_weights_m2, strict=True)
    ):
        normal_flux = math.fsum(a * b for a, b in zip(vector, normal, strict=True))
        terms.append(_finite_result(weight * normal_flux, f"surface/{i}/power_w"))
    return _finite_result(math.fsum(terms), "surface/power_w")


@dataclass(frozen=True, kw_only=True)
class EnergyBalanceResult:
    """Scoped balance comparison; its state is not an overall MCLF verdict."""

    contract: str
    control_volume: str
    comparison: str
    boundary_power_w: tuple[float, ...]
    internal_source_power_w: float | None
    absorbed_power_w: float | None
    residual_power_w: float | None
    reference_scale_w: float
    tolerance_w: float
    normalized_error: float | None
    diagnostic: str | None

    def __post_init__(self) -> None:
        if self.contract != ENERGY_BALANCE_VERSION:
            raise InvalidInputError(
                "BALANCE_VERSION", "/contract", "Unknown energy-balance contract."
            )
        if self.control_volume not in ("closed_sphere", "spherical_shell"):
            raise InvalidInputError("BALANCE_TOPOLOGY", "/control_volume", "Unsupported volume.")
        if self.comparison not in ("PASS", "FAIL", "INDETERMINATE"):
            raise InvalidInputError("BALANCE_STATUS", "/comparison", "Unknown comparison state.")
        if type(self.boundary_power_w) is not tuple or not self.boundary_power_w:
            raise InvalidInputError(
                "BALANCE_SHAPE", "/boundary_power_w", "Expected boundary contributions."
            )
        for i, value in enumerate(self.boundary_power_w):
            _finite_scalar(f"boundary_power_w/{i}", value)
        if self.control_volume == "closed_sphere" and len(self.boundary_power_w) != 1:
            raise InvalidInputError(
                "BALANCE_SHAPE", "/boundary_power_w", "A sphere has one boundary."
            )
        if self.control_volume == "spherical_shell" and len(self.boundary_power_w) != 2:
            raise InvalidInputError(
                "BALANCE_SHAPE", "/boundary_power_w", "A shell has two boundaries."
            )
        _positive_finite("reference_scale_w", self.reference_scale_w)
        _positive_finite("tolerance_w", self.tolerance_w)
        source = _term("internal_source_power_w", self.internal_source_power_w)
        absorption = _term("absorbed_power_w", self.absorbed_power_w)
        if source is not None and source < 0 or absorption is not None and absorption < 0:
            raise InvalidInputError(
                "BALANCE_TERM_RANGE", "/", "Source and absorbed powers must be nonnegative."
            )
        expected_tolerance = _finite_result(
            BALANCE_TOLERANCE * self.reference_scale_w, "tolerance_w"
        )
        if self.tolerance_w != expected_tolerance:
            raise InvalidInputError(
                "BALANCE_RESULT", "/tolerance_w", "Stored threshold does not match contract."
            )
        missing_terms = source is None or absorption is None
        if self.comparison == "INDETERMINATE":
            if (
                not missing_terms
                or self.residual_power_w is not None
                or self.normalized_error is not None
                or not self.diagnostic
            ):
                raise InvalidInputError(
                    "BALANCE_RESULT",
                    "/",
                    "Unknown terms require a diagnostic and no residual verdict.",
                )
        else:
            if missing_terms:
                raise InvalidInputError(
                    "BALANCE_RESULT", "/comparison", "Missing terms cannot pass or fail."
                )
            residual = _finite_result(
                math.fsum((*self.boundary_power_w, absorption, -source)), "residual_power_w"
            )
            normalized = _finite_result(abs(residual) / self.reference_scale_w, "normalized_error")
            if (
                self.residual_power_w != residual
                or self.normalized_error != normalized
            ):
                raise InvalidInputError(
                    "BALANCE_RESULT", "/", "Stored residual metrics do not match terms."
                )
            expected = "PASS" if abs(residual) <= expected_tolerance else "FAIL"
            if self.comparison != expected or self.diagnostic is not None:
                raise InvalidInputError(
                    "BALANCE_RESULT", "/comparison", "Comparison does not match its residual."
                )

    def to_dict(self) -> dict:
        """Return a JSON-compatible, explicitly scoped diagnostic record."""
        return {
            "contract": self.contract,
            "control_volume": self.control_volume,
            "comparison": self.comparison,
            "boundary_power_w": list(self.boundary_power_w),
            "internal_source_power_w": self.internal_source_power_w,
            "absorbed_power_w": self.absorbed_power_w,
            "residual_power_w": self.residual_power_w,
            "reference_scale_w": self.reference_scale_w,
            "tolerance_w": self.tolerance_w,
            "normalized_error": self.normalized_error,
            "diagnostic": self.diagnostic,
            "limitations": [
                "Model-specific time-averaged energy comparison only; not force or physical validation."
            ],
        }


def _term(name: str, value: float | None) -> float | None:
    return None if value is None else _finite_scalar(name, value)


def _result(control_volume, boundaries, source, absorption, scale):
    scale = _positive_finite("reference_power_scale_w", scale)
    source = _term("internal_source_power_w", source)
    absorption = _term("absorbed_power_w", absorption)
    if source is not None and source < 0 or absorption is not None and absorption < 0:
        raise InvalidInputError(
            "BALANCE_TERM_RANGE", "/", "Source and absorbed powers must be nonnegative."
        )
    tolerance = _finite_result(BALANCE_TOLERANCE * scale, "tolerance_w")
    if source is None or absorption is None:
        missing = []
        if source is None:
            missing.append("internal source power")
        if absorption is None:
            missing.append("absorbed power")
        return EnergyBalanceResult(
            contract=ENERGY_BALANCE_VERSION,
            control_volume=control_volume,
            comparison="INDETERMINATE",
            boundary_power_w=tuple(boundaries),
            internal_source_power_w=source,
            absorbed_power_w=absorption,
            residual_power_w=None,
            reference_scale_w=scale,
            tolerance_w=tolerance,
            normalized_error=None,
            diagnostic="Missing explicit " + " and ".join(missing) + ".",
        )
    residual = _finite_result(math.fsum((*boundaries, absorption, -source)), "residual_power_w")
    normalized = _finite_result(abs(residual) / scale, "normalized_error")
    comparison = "PASS" if abs(residual) <= tolerance else "FAIL"
    return EnergyBalanceResult(
        contract=ENERGY_BALANCE_VERSION,
        control_volume=control_volume,
        comparison=comparison,
        boundary_power_w=tuple(boundaries),
        internal_source_power_w=source,
        absorbed_power_w=absorption,
        residual_power_w=residual,
        reference_scale_w=scale,
        tolerance_w=tolerance,
        normalized_error=normalized,
        diagnostic=None,
    )


def audit_closed_sphere_energy_balance(
    field: FieldSamples,
    surface: SphereSurfaceQuadrature,
    *,
    internal_source_power_w: float | None,
    absorbed_power_w: float | None,
    reference_power_scale_w: float,
) -> EnergyBalanceResult:
    """Audit one fixed closed-sphere control volume with every term explicit."""
    power = integrate_sphere_flux_w(field, surface)
    return _result(
        "closed_sphere",
        (power,),
        internal_source_power_w,
        absorbed_power_w,
        reference_power_scale_w,
    )


def audit_spherical_shell_energy_balance(
    outer_field: FieldSamples,
    outer_surface: SphereSurfaceQuadrature,
    inner_field: FieldSamples,
    inner_surface: SphereSurfaceQuadrature,
    *,
    internal_source_power_w: float | None,
    absorbed_power_w: float | None,
    reference_power_scale_w: float,
) -> EnergyBalanceResult:
    """Audit a concentric source-free shell; the inner normal points inward."""
    if (
        type(outer_surface) is not SphereSurfaceQuadrature
        or type(inner_surface) is not SphereSurfaceQuadrature
    ):
        raise InvalidInputError(
            "BALANCE_SURFACE", "/surfaces", "Expected two fixed sphere surfaces."
        )
    if (
        outer_surface.center_m != inner_surface.center_m
        or outer_surface.radius_m <= inner_surface.radius_m
    ):
        raise InvalidInputError(
            "BALANCE_TOPOLOGY",
            "/surfaces",
            "Shell requires concentric surfaces with outer radius greater than inner.",
        )
    if type(outer_field) is not FieldSamples or type(inner_field) is not FieldSamples:
        raise InvalidInputError(
            "BALANCE_FIELD", "/fields", "Expected FIELD-1.0 samples on both boundaries."
        )
    if outer_field.frequency_hz != inner_field.frequency_hz:
        raise InvalidInputError(
            "BALANCE_FREQUENCY", "/fields", "Shell boundary frequencies differ."
        )
    outward = integrate_sphere_flux_w(outer_field, outer_surface)
    inward_boundary = -integrate_sphere_flux_w(inner_field, inner_surface)
    return _result(
        "spherical_shell",
        (outward, inward_boundary),
        internal_source_power_w,
        absorbed_power_w,
        reference_power_scale_w,
    )
