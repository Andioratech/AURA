"""AURA-C14N-1 exact numeric JSON encoding; independent of display serialization."""

import json
from decimal import Decimal

from aura.errors import InvalidInputError

from .models import ValidatedRecord, validate_document
from .quantities import MAX_BYTES, check_json_tree

CANONICAL_VERSION = "AURA-C14N-1"
MAX_CANONICAL_BYTES = 16 * 1024 * 1024


def _pieces(value):
    if value is None:
        yield "null"
    elif type(value) is bool:
        yield "true" if value else "false"
    elif type(value) is int:
        yield str(value)
    elif type(value) is float:
        if value == 0:
            yield "0"
        else:
            number = format(Decimal.from_float(value), "f")
            yield number.rstrip("0").rstrip(".") if "." in number else number
    elif type(value) is str:
        yield json.dumps(value, ensure_ascii=True)
    elif type(value) is list:
        yield "["
        for index, child in enumerate(value):
            if index:
                yield ","
            yield from _pieces(child)
        yield "]"
    else:  # check_json_tree has already restricted this case to a string-keyed dict.
        yield "{"
        for index, key in enumerate(sorted(value)):
            if index:
                yield ","
            yield json.dumps(key, ensure_ascii=True)
            yield ":"
            yield from _pieces(value[key])
        yield "}"


def canonical_json_bytes(value: object) -> bytes:
    """Encode a bounded JSON tree; this generic helper does not validate physics."""
    check_json_tree(value)
    if len(json.dumps(value, ensure_ascii=True, allow_nan=False).encode("ascii")) > MAX_BYTES:
        raise InvalidInputError("INPUT_LIMIT", "", "Input exceeds the 1 MiB JSON limit.")
    chunks, size = [], 0
    for piece in _pieces(value):
        chunk = piece.encode("ascii")
        size += len(chunk)
        if size > MAX_CANONICAL_BYTES:
            raise InvalidInputError("CANONICAL_LIMIT", "", "Canonical output exceeds 16 MiB.")
        chunks.append(chunk)
    return b"".join(chunks)


def canonical_document_bytes(record: ValidatedRecord) -> bytes:
    """Revalidate a typed snapshot, then encode all its fields including the version."""
    if not isinstance(record, ValidatedRecord):
        raise InvalidInputError("INPUT_TYPE", "", "Expected a validated record.")
    data = validate_document(record.to_dict()).to_dict()
    return canonical_json_bytes(data)
