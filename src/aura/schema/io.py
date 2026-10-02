"""Bounded JSON/YAML readers with duplicate-key and unsafe-YAML rejection."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import yaml

from aura.errors import InvalidInputError

from .models import ValidatedRecord, validate_document
from .quantities import MAX_BYTES, MAX_DEPTH


def _pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInputError("DUPLICATE_KEY", "", f"Duplicate key: {key!r}.")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise InvalidInputError("NONFINITE", "", f"Nonfinite JSON constant: {value}.")


def _integer(value: str) -> int:
    if len(value.lstrip("+-0")) > 309:
        raise InvalidInputError("NONFINITE", "", "Integer exceeds finite binary64 range.")
    return int(value)


def _float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise InvalidInputError("NONFINITE", "", "Number overflows binary64.")
    if number == 0.0 and _nonzero_mantissa(value):
        raise InvalidInputError("NUMERIC_RANGE", "", "Nonzero number underflows binary64.")
    return number


def _nonzero_mantissa(value: str) -> bool:
    return any(digit in "123456789" for digit in value.lower().split("e", 1)[0])


class _StrictLoader(yaml.SafeLoader):
    def __init__(self, stream):
        super().__init__(stream)
        self._depth = 0

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise InvalidInputError("YAML_ALIAS", "", "YAML aliases are not supported.")
        self._depth += 1
        try:
            if self._depth > MAX_DEPTH:
                raise InvalidInputError("INPUT_LIMIT", "", "YAML nesting exceeds 64 levels.")
            return super().compose_node(parent, index)
        finally:
            self._depth -= 1

    def construct_mapping(self, node, deep=False):
        pairs = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if type(key) is not str:
                raise InvalidInputError("KEY_TYPE", "", "YAML mapping keys must be strings.")
            pairs.append((key, self.construct_object(value_node, deep=deep)))
        return _pairs(pairs)

    def construct_yaml_float(self, node):
        number = super().construct_yaml_float(node)
        if not math.isfinite(number):
            raise InvalidInputError("NONFINITE", "", "YAML number must be finite.")
        # SafeLoader also accepts base-60 numbers; disallow that ambiguous notation.
        spelling = node.value.replace("_", "")
        if ":" in spelling:
            raise InvalidInputError("NUMERIC_FORMAT", "", "Base-60 floats are unsupported.")
        if number == 0.0 and _nonzero_mantissa(spelling):
            raise InvalidInputError("NUMERIC_RANGE", "", "Nonzero number underflows binary64.")
        return number

    def construct_yaml_int(self, node):
        if re.fullmatch(r"[+-]?(0|[1-9][0-9]*)", node.value) is None:
            raise InvalidInputError(
                "NUMERIC_FORMAT", "", "Use decimal integers without leading zeros."
            )
        return _integer(node.value)


_StrictLoader.add_constructor("tag:yaml.org,2002:float", _StrictLoader.construct_yaml_float)
_StrictLoader.add_constructor("tag:yaml.org,2002:int", _StrictLoader.construct_yaml_int)


def loads_document(text: str | bytes, *, format: str = "json") -> ValidatedRecord:
    """Read exactly one document. Formats are explicit; no content guessing."""
    if not isinstance(text, (str, bytes)):
        raise InvalidInputError("INPUT_TYPE", "", "Expected UTF-8 text or bytes.")
    try:
        payload = text.encode("utf-8") if isinstance(text, str) else text
        if len(payload) > MAX_BYTES:
            raise InvalidInputError("INPUT_LIMIT", "", "Serialized input exceeds 1 MiB.")
        decoded = payload.decode("utf-8")
        if format == "json":
            data = json.loads(
                decoded,
                object_pairs_hook=_pairs,
                parse_constant=_constant,
                parse_float=_float,
                parse_int=_integer,
            )
        elif format in ("yaml", "yml"):
            data = yaml.load(decoded, Loader=_StrictLoader)
        else:
            raise InvalidInputError("FORMAT", "", "Expected json, yaml or yml.")
    except InvalidInputError:
        raise
    except (UnicodeError, ValueError, yaml.YAMLError) as exc:
        raise InvalidInputError("PARSE_ERROR", "", str(exc)) from exc
    except RecursionError as exc:
        raise InvalidInputError("INPUT_LIMIT", "", "Input nesting is too deep.") from exc
    return validate_document(data)


def load_document(path: str | Path) -> ValidatedRecord:
    """Read at most the byte limit plus one; filesystem errors retain their type."""
    path = Path(path)
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    return loads_document(data, format=path.suffix.lstrip(".").lower())


def dumps_document(record: ValidatedRecord, *, format: str = "json") -> str:
    """Serialize a validated snapshot; this is not the FND-07 canonical hash format."""
    if not isinstance(record, ValidatedRecord):
        raise InvalidInputError("INPUT_TYPE", "", "Expected a validated record.")
    data = record.to_dict()
    if format == "json":
        return json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    if format in ("yaml", "yml"):
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)
    raise InvalidInputError("FORMAT", "", "Expected json, yaml or yml.")
