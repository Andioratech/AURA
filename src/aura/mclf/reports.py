"""Immutable audit outcomes with a compatible core record and detailed findings."""

import json
from dataclasses import asdict, dataclass

from aura import __version__
from aura.errors import IncompleteEvidenceError, InvalidInputError, MclfInvalidationError
from aura.schema import MclfReport

from .rules import PRECEDENCE, REGISTRY_VERSION, RULES


def aggregate(verdicts) -> str:
    """Apply D02 ordering without accepting an empty or unknown evaluation."""
    values = tuple(verdicts)
    if any(type(value) is not str or value not in PRECEDENCE for value in values):
        raise InvalidInputError("VERDICT", "/verdict", "Unknown verdict.")
    return next((value for value in PRECEDENCE if value in values), "INDETERMINATE")


@dataclass(frozen=True)
class Finding:
    verdict: str
    code: str
    path: str
    message: str

    def __post_init__(self):
        aggregate((self.verdict,))
        if any(type(value) is not str for value in (self.code, self.path, self.message)):
            raise InvalidInputError("FINDING_TYPE", "/findings", "Finding fields must be strings.")


@dataclass(frozen=True)
class Check:
    rule_id: str
    findings: tuple[Finding, ...]

    def __post_init__(self):
        if type(self.findings) is not tuple or any(
            type(item) is not Finding for item in self.findings
        ):
            raise InvalidInputError(
                "FINDING_TYPE", "/findings", "Expected an immutable tuple of findings."
            )

    @property
    def verdict(self) -> str:
        return aggregate(item.verdict for item in self.findings)


@dataclass(frozen=True)
class AuditReport:
    id: str
    run_id: str
    stage: str
    checks: tuple[Check, ...]

    def __post_init__(self):
        if type(self.checks) is not tuple or any(type(item) is not Check for item in self.checks):
            raise InvalidInputError("RULE_SET", "/checks", "Expected an immutable tuple of checks.")
        if self.stage not in ("pre", "post"):
            raise InvalidInputError("AUDIT_STAGE", "/stage", "Expected pre or post.")
        if tuple(check.rule_id for check in self.checks) != tuple(rule.id for rule in RULES):
            raise InvalidInputError("RULE_SET", "/checks", "Expected all ten unique ordered rules.")
        self.to_record()  # Validate IDs and the backward-compatible report core.

    @property
    def verdict(self) -> str:
        return aggregate(check.verdict for check in self.checks)

    def to_record(self) -> MclfReport:
        return MclfReport(
            {
                "document_type": "mclf_report",
                "schema_version": "1.0",
                "id": self.id,
                "run_id": self.run_id,
                "level": "L0",
                "verdict": self.verdict,
                "checks": [
                    {
                        "rule_id": check.rule_id,
                        "verdict": check.verdict,
                        "message": " | ".join(
                            f"{item.code} at {item.path or '/'}: {item.message}"
                            for item in check.findings
                        )
                        or "No coverage.",
                        "assumptions": [
                            f"Registry {REGISTRY_VERSION}; stage {self.stage}.",
                            *rule.assumptions,
                            rule.tolerance,
                        ],
                    }
                    for rule, check in zip(RULES, self.checks)
                ],
                "limitations": [
                    "L0 only; no physical, numerical-convergence or experimental validation.",
                    "No scientific model capability is registered; no solver is called.",
                    "External samples, content hashes and source/environment identities are not authenticated.",
                    "The detailed envelope preserves rule predicates, field paths and software version.",
                ],
            }
        )

    def to_dict(self) -> dict:
        return {
            "audit_version": REGISTRY_VERSION,
            "software_version": __version__,
            "stage": self.stage,
            "report": self.to_record().to_dict(),
            "rules": [
                {**asdict(rule), "fields": list(rule.fields), "assumptions": list(rule.assumptions)}
                for rule in RULES
            ],
            "findings": [
                {
                    "rule_id": check.rule_id,
                    "verdict": check.verdict,
                    "items": [asdict(item) for item in check.findings],
                }
                for check in self.checks
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, allow_nan=False) + "\n"

    def require_accepted(self) -> None:
        """Explicit acceptance gate, not a condition for unrelated foundation work."""
        if self.verdict == "INVALIDATED":
            raise MclfInvalidationError(
                "MCLF_INVALIDATED", "/verdict", "Audit invalidated; preserve its findings."
            )
        if self.verdict != "ACCEPTED":
            raise IncompleteEvidenceError(
                "MCLF_" + self.verdict,
                "/verdict",
                "Audit cannot satisfy a required acceptance gate.",
            )

    def to_text(self) -> str:
        lines = [f"{REGISTRY_VERSION} | {self.stage} | {self.verdict}"]
        for check in self.checks:
            lines.append(f"{check.rule_id}: {check.verdict}")
            for item in check.findings:
                lines.append(f"  {item.code} {json.dumps(item.path)}: {json.dumps(item.message)}")
        lines.append("Scope: L0 declarations only; not scientific acceptance.")
        return "\n".join(lines) + "\n"
