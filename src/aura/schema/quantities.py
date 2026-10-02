"""Canonical SI schema primitives and finite JSON-tree checks."""

from __future__ import annotations

import math

from aura.errors import InvalidInputError

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
