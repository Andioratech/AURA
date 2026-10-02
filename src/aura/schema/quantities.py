"""Canonical SI schema primitives and finite JSON-tree checks."""

from __future__ import annotations

import math

from aura.errors import InvalidInputError
from aura.units import _finite_scalar, _scaled_ratio

MAX_BYTES = 1024 * 1024
MAX_DEPTH = 64
MAX_NODES = 100_000
SI_UNITS = (
    "1",
    "m",
    "kg",
    "s",
    "Hz",
    "rad",
    "Pa",
    "m/s",
    "m/s^2",
    "rad/s",
    "kg/m^3",
    "Pa*s",
    "1/Pa",
    "K",
    "N",
    "N*m",
    "W",
    "W/m^2",
    "kg*m^2",
    "1/m",
)

# (Canonical unit, numerator, denominator). Prefix powers use exact integer factors.
_CONVERSIONS = {unit: (unit, 1.0, 1.0) for unit in SI_UNITS}
_CONVERSIONS.update(
    {
        "um": ("m", 1.0, 1_000_000.0),
        "mm": ("m", 1.0, 1000.0),
        "cm": ("m", 1.0, 100.0),
        "mg": ("kg", 1.0, 1_000_000.0),
        "g": ("kg", 1.0, 1000.0),
        "us": ("s", 1.0, 1_000_000.0),
        "ms": ("s", 1.0, 1000.0),
        "kHz": ("Hz", 1000.0, 1.0),
        "MHz": ("Hz", 1_000_000.0, 1.0),
        "kPa": ("Pa", 1000.0, 1.0),
        "MPa": ("Pa", 1_000_000.0, 1.0),
        "deg": ("rad", math.pi, 180.0),
    }
)


def pointer(parent: str, key: str | int) -> str:
    token = str(key).replace("~", "~0").replace("/", "~1")
    return f"{parent}/{token}"


def check_json_tree(value: object) -> None:
    """Reject non-JSON data, excessive nesting and nonrepresentable numbers."""
    stack = [(value, "", 0)]
    seen = 0
    while stack:
        item, path, depth = stack.pop()
        seen += 1
        if depth > MAX_DEPTH or seen > MAX_NODES:
            raise InvalidInputError("INPUT_LIMIT", path, "Document exceeds structural limits")
        if type(item) in (int, float):
            try:
                finite = math.isfinite(float(item))
            except OverflowError:
                finite = False
            if not finite:
                raise InvalidInputError("NONFINITE", path, "Number must be finite in binary64")
        elif type(item) is dict:
            if len(item) > MAX_NODES:
                raise InvalidInputError("INPUT_LIMIT", path, "Object exceeds structural limits")
            if any(type(key) is not str for key in item):
                raise InvalidInputError("KEY_TYPE", path, "Object keys must be strings")
            stack.extend((child, pointer(path, key), depth + 1) for key, child in item.items())
        elif type(item) is list:
            if len(item) > MAX_NODES:
                raise InvalidInputError("INPUT_LIMIT", path, "Array exceeds structural limits")
            stack.extend((child, pointer(path, i), depth + 1) for i, child in enumerate(item))
        elif item is not None and type(item) not in (str, bool):
            raise InvalidInputError("VALUE_TYPE", path, "Only JSON-compatible values are allowed")


def quantity(
    unit: str, *, size: int | None = None, positive: bool = False, nonnegative: bool = False
) -> dict:
    """A canonical quantity; alternate-unit conversion is a later boundary."""
    number: dict = {"type": "number"}
    if positive:
        number["exclusiveMinimum"] = 0
    elif nonnegative:
        number["minimum"] = 0
    value = (
        number
        if size is None
        else {
            "type": "array",
            "items": number,
            "minItems": size,
            "maxItems": size,
        }
    )
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["value", "unit"],
        "properties": {"value": value, "unit": {"const": unit}},
    }


def canonical_quantity(
    data: dict, *, expected_unit: str, size: int | None = None, path: str = ""
) -> dict:
    """Explicitly convert one scalar/vector to SI; never infer its physical range.

    The document reader remains canonical-only. Callers must retain raw input
    provenance and validate the complete scenario after replacing a quantity.
    """
    # Tree errors must also retain the caller's enclosing field path.
    try:
        check_json_tree(data)
    except InvalidInputError as exc:
        raise type(exc)(exc.code, path + exc.path, exc.message) from exc
    if type(data) is not dict or set(data) != {"value", "unit"}:
        raise InvalidInputError("SCHEMA_INVALID", path, "Expected exactly value and unit fields.")
    if type(expected_unit) is not str or expected_unit not in SI_UNITS:
        raise InvalidInputError(
            "UNIT_UNSUPPORTED", pointer(path, "unit"), "Expected unit must be canonical SI."
        )
    unit = data["unit"]
    if type(unit) is not str or unit not in _CONVERSIONS:
        raise InvalidInputError(
            "UNIT_UNSUPPORTED", pointer(path, "unit"), "Unsupported unit spelling."
        )
    canonical, numerator, denominator = _CONVERSIONS[unit]
    if canonical != expected_unit:
        raise InvalidInputError(
            "UNIT_MISMATCH", pointer(path, "unit"), "Unit does not match the required quantity."
        )
    values = data["value"]
    if size is not None:
        if type(size) is not int or not 1 <= size <= MAX_NODES:
            raise InvalidInputError(
                "SCHEMA_INVALID", pointer(path, "value"), "Invalid requested vector size."
            )
        if type(values) is not list or len(values) != size:
            raise InvalidInputError(
                "SCHEMA_INVALID", pointer(path, "value"), "Vector has the wrong shape."
            )
    else:
        values = [values]
    converted = []
    for index, value in enumerate(values):
        field = (
            pointer(pointer(path, "value"), index) if size is not None else pointer(path, "value")
        )
        try:
            number = _finite_scalar("value", value)
            converted.append(_scaled_ratio("value", (number, numerator), (denominator,)))
        except InvalidInputError as exc:
            raise type(exc)(exc.code, field, exc.message) from exc
    return {"value": converted if size is not None else converted[0], "unit": canonical}
