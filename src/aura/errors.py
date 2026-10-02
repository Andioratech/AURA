"""Structured input errors; scientific verdicts are a separate contract."""

from __future__ import annotations


class InvalidInputError(ValueError):
    """An invalid document with a stable code and JSON-pointer field path."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code} at {path or '/'}: {message}")

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


class NumericalDomainError(InvalidInputError):
    """Valid finite operands have a result outside the supported numeric range."""


class MclfInvalidationError(InvalidInputError):
    """A required acceptance gate failed because an audit is INVALIDATED."""


class IncompleteEvidenceError(InvalidInputError):
    """A required acceptance gate lacks an explained or covered result."""
