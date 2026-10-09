"""Outward-rounded modal tail majorants for the frozen NUM-03 sphere case."""

from __future__ import annotations

from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, Context, Decimal

PRECISION = 80
_UP = Context(prec=PRECISION, rounding=ROUND_CEILING)
_DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR)
_NEAR = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN)
_PI_LOW = Decimal("3.14159265358979323846264338327950288419716939937510")
_PI_HIGH = Decimal("3.14159265358979323846264338327950288419716939937511")
_A = Decimal("0.025")
_GAP = Decimal("0.0001")
_FREQUENCY = Decimal(25230)
_SOUND_SPEED = Decimal(346)
_CENTER_DISTANCE = 2 * (_A + _GAP)
_R_MIN = _CENTER_DISTANCE - _A


def _add_up(left: Decimal, right: Decimal) -> Decimal:
    return _UP.add(left, right)


def _mul_up(left: Decimal, right: Decimal) -> Decimal:
    return _UP.multiply(left, right)


def _div_up(left: Decimal, right: Decimal) -> Decimal:
    return _UP.divide(left, right)


def _pow_up(value: Decimal, exponent: int) -> Decimal:
    result = Decimal(1)
    for _ in range(exponent):
        result = _mul_up(result, value)
    return result


def _exp_up(value: Decimal) -> Decimal:
    return _NEAR.exp(value).next_plus(_UP)


def _inputs() -> dict[str, Decimal]:
    k_low = _DOWN.divide(_DOWN.multiply(Decimal(2), _DOWN.multiply(_PI_LOW, _FREQUENCY)), _SOUND_SPEED)
    k_high = _div_up(_mul_up(_mul_up(Decimal(2), _PI_HIGH), _FREQUENCY), _SOUND_SPEED)
    return {
        "pi_low": _PI_LOW,
        "k_low": k_low,
        "k_high": k_high,
        "za_low": _DOWN.multiply(k_low, _A),
        "za_high": _mul_up(k_high, _A),
        "zl_low": _DOWN.multiply(k_low, _CENTER_DISTANCE),
        "zl_high": _mul_up(k_high, _CENTER_DISTANCE),
        "zr_low": _DOWN.multiply(k_low, _R_MIN),
        "zr_high": _mul_up(k_high, _R_MIN),
    }


def _hankel_majorants(maximum_order: int, z_lower: Decimal) -> list[Decimal]:
    inverse = _div_up(Decimal(1), z_lower)
    values = [inverse]
    if maximum_order == 0:
        return values
    values.append(_add_up(inverse, _mul_up(inverse, inverse)))
    for order in range(1, maximum_order):
        factor = _div_up(Decimal(2 * order + 1), z_lower)
        values.append(_add_up(_mul_up(factor, values[order]), values[order - 1]))
    return values


def _bessel_majorants(maximum_order: int, z_upper: Decimal) -> list[Decimal]:
    values = [_exp_up(_div_up(_mul_up(z_upper, z_upper), Decimal(6)))]
    for order in range(maximum_order):
        denominator = Decimal((2 * order + 3) * (2 * order + 5))
        exponent_lower = _DOWN.divide(_DOWN.multiply(z_upper, z_upper), denominator)
        ratio = _mul_up(
            _div_up(z_upper, Decimal(2 * order + 3)), _exp_up(-exponent_lower)
        )
        values.append(_mul_up(values[-1], ratio))
    return values


def _majorant_terms(order: int, bounds: dict[str, Decimal], hankel: dict[str, list[Decimal]],
                    regular: list[Decimal]) -> tuple[Decimal, Decimal, Decimal]:
    za = bounds["za_low"]
    j_derivative = _add_up(
        _mul_up(_div_up(Decimal(order), za), regular[order]), regular[order + 1]
    )
    k3 = _pow_up(bounds["k_high"], 3)
    a2 = _mul_up(_A, _A)
    four_pi_lower = _DOWN.multiply(Decimal(4), _PI_LOW)
    eight_pi_lower = _DOWN.multiply(Decimal(8), _PI_LOW)

    direct_v_prefactor = _div_up(
        _mul_up(_mul_up(k3, a2), Decimal(2 * order + 1)), four_pi_lower
    )
    direct_v = _mul_up(
        _mul_up(
            _mul_up(_mul_up(direct_v_prefactor, hankel["zl"][order]), hankel["za"][order]),
            regular[order],
        ),
        j_derivative,
    )

    hankel_derivative = _add_up(
        _mul_up(_div_up(Decimal(order), za), hankel["za"][order]), hankel["za"][order + 1]
    )
    direct_k_prefactor = _div_up(
        _mul_up(_mul_up(k3, a2), Decimal(2 * order + 1)), eight_pi_lower
    )
    direct_k = _mul_up(
        _mul_up(direct_k_prefactor, hankel["zl"][order]),
        _mul_up(
            regular[order],
            _add_up(
                _mul_up(j_derivative, hankel["za"][order]),
                _mul_up(regular[order], hankel_derivative),
            ),
        ),
    )

    image_prefactor = _div_up(
        _mul_up(_mul_up(k3, a2), Decimal(2 * order + 1)), four_pi_lower
    )
    image = _mul_up(
        _mul_up(
            _mul_up(_mul_up(image_prefactor, hankel["zl"][order]), hankel["zr"][order]),
            regular[order],
        ),
        j_derivative,
    )
    return direct_k, direct_v, image


def _direct_coarse(order: int, bounds: dict[str, Decimal]) -> tuple[Decimal, Decimal]:
    za = bounds["za_low"]
    za_high = bounds["za_high"]
    zl = bounds["zl_low"]
    k3 = _pow_up(bounds["k_high"], 3)
    a2 = _mul_up(_A, _A)
    ratio = _div_up(_A, _CENTER_DISTANCE)
    base = _div_up(
        _mul_up(_mul_up(k3, a2), _exp_up(_add_up(bounds["zl_high"], za_high))),
        _DOWN.multiply(
            _DOWN.multiply(_DOWN.multiply(Decimal(4), _PI_LOW), Decimal(2 * order + 1)),
            _DOWN.multiply(zl, za),
        ),
    )
    radial = _pow_up(ratio, order)
    exponential = _exp_up(_div_up(_mul_up(za_high, za_high), Decimal(2 * order + 3)))
    derivative = _add_up(
        _div_up(Decimal(order), za), _div_up(za_high, Decimal(2 * order + 3))
    )
    v = _mul_up(_mul_up(_mul_up(base, radial), exponential), derivative)
    hankel_derivative_ratio = _div_up(Decimal(3 * order + 1), za)
    k = _mul_up(
        _mul_up(_mul_up(base, radial), exponential),
        _div_up(_add_up(derivative, hankel_derivative_ratio), Decimal(2)),
    )
    return k, v


def _image_coarse(order: int, bounds: dict[str, Decimal]) -> Decimal:
    za_high = bounds["za_high"]
    zl = bounds["zl_low"]
    zr = bounds["zr_low"]
    k3 = _pow_up(bounds["k_high"], 3)
    a2 = _mul_up(_A, _A)
    base = _div_up(
        _mul_up(_mul_up(k3, a2), _exp_up(_add_up(bounds["zl_high"], bounds["zr_high"]))),
        _DOWN.multiply(
            _DOWN.multiply(_DOWN.multiply(Decimal(4), _PI_LOW), Decimal(2 * order + 1)),
            _DOWN.multiply(zl, zr),
        ),
    )
    ratio = _div_up(a2, _DOWN.multiply(_CENTER_DISTANCE, _R_MIN))
    radial = _pow_up(ratio, order)
    exponential = _exp_up(_div_up(_mul_up(za_high, za_high), Decimal(2 * order + 3)))
    derivative = _add_up(
        _div_up(Decimal(order), bounds["za_low"]),
        _div_up(za_high, Decimal(2 * order + 3)),
    )
    return _mul_up(_mul_up(_mul_up(base, radial), exponential), derivative)


def compute_modal_tail_bounds() -> dict:
    """Return 80-digit outward-rounded tails for each of the four layer sums."""
    bounds = _inputs()
    cutoff_list = (48, 64, 80)
    mode_limit = 2000
    hankel = {
        "zl": _hankel_majorants(mode_limit + 1, bounds["zl_low"]),
        "za": _hankel_majorants(mode_limit + 1, bounds["za_low"]),
        "zr": _hankel_majorants(mode_limit + 1, bounds["zr_low"]),
    }
    regular = _bessel_majorants(mode_limit + 1, bounds["za_high"])
    finite = {name: {} for name in ("direct_K", "direct_V", "image_KV")}
    for order in range(1, mode_limit + 1):
        direct_k, direct_v, image = _majorant_terms(order, bounds, hankel, regular)
        finite["direct_K"][order] = direct_k
        finite["direct_V"][order] = direct_v
        finite["image_KV"][order] = image

    direct_ratio = _div_up(_A, _CENTER_DISTANCE)
    za2 = _mul_up(bounds["za_high"], bounds["za_high"])
    direct_v_ratio = _mul_up(
        direct_ratio,
        _add_up(
            _add_up(Decimal(1), _div_up(Decimal(1), Decimal(mode_limit))),
            _div_up(za2, Decimal(mode_limit * (2 * mode_limit + 5))),
        ),
    )
    direct_k_ratio = _mul_up(
        direct_ratio,
        _add_up(
            _div_up(Decimal(4 * mode_limit + 5), Decimal(4 * mode_limit + 1)),
            _div_up(za2, Decimal((4 * mode_limit + 1) * (2 * mode_limit + 5))),
        ),
    )
    image_ratio = _div_up(_mul_up(_div_up(_A, _CENTER_DISTANCE), _div_up(_A, _R_MIN)), Decimal(1))
    image_ratio = _mul_up(
        image_ratio,
        _add_up(
            _add_up(Decimal(1), _div_up(Decimal(1), Decimal(mode_limit))),
            _div_up(za2, Decimal(mode_limit * (2 * mode_limit + 5))),
        ),
    )
    if max(direct_v_ratio, direct_k_ratio, image_ratio) >= Decimal("0.5"):
        raise ArithmeticError("An all-order geometric remainder ratio is not below one half.")

    direct_k_denominator = _DOWN.subtract(Decimal(1), direct_k_ratio)
    direct_v_denominator = _DOWN.subtract(Decimal(1), direct_v_ratio)
    image_denominator = _DOWN.subtract(Decimal(1), image_ratio)
    direct_k_after = _div_up(_direct_coarse(mode_limit + 1, bounds)[0], direct_k_denominator)
    direct_v_after = _div_up(_direct_coarse(mode_limit + 1, bounds)[1], direct_v_denominator)
    image_after = _div_up(_image_coarse(mode_limit + 1, bounds), image_denominator)
    result = {}
    for cutoff in cutoff_list:
        sums = {"direct_K": Decimal(0), "direct_V": Decimal(0), "image_KV": Decimal(0)}
        for order in range(cutoff + 1, mode_limit + 1):
            for name, value in sums.items():
                sums[name] = _add_up(value, finite[name][order])
        result[str(cutoff)] = {
            "direct_double_layer_upper_pa": str(_add_up(sums["direct_K"], direct_k_after)),
            "direct_single_layer_upper_pa": str(_add_up(sums["direct_V"], direct_v_after)),
            "image_double_layer_upper_pa": str(_add_up(sums["image_KV"], image_after)),
            "image_single_layer_upper_pa": str(_add_up(sums["image_KV"], image_after)),
        }
    return {
        "contract": "NUM03-MODAL-FOUR-LAYER-TAIL-BOUNDS-1.0",
        "status": "PRELIMINARY_OUTWARD_ROUNDED_CANDIDATE",
        "precision_decimal_digits": PRECISION,
        "finite_sum_through_order": mode_limit,
        "ratio_upper_n_ge_2000": {
            "direct_K": str(direct_k_ratio),
            "direct_V": str(direct_v_ratio),
            "image_K_and_V": str(image_ratio),
        },
        "coarse_tail_after_mode_2000_pa": {
            "direct_K": str(direct_k_after),
            "direct_V": str(direct_v_after),
            "image_K_and_V_each": str(image_after),
        },
        "cutoffs": result,
        "scope": "Uniform absolute term-tail bounds for the frozen geometry and Q=1 Pa m; no binary64 roundoff, model discrepancy, or experimental uncertainty bound.",
    }
