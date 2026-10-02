"""Versioned L0 policy metadata; predicates are implemented in evaluate.py."""

from dataclasses import dataclass

REGISTRY_VERSION = "L0-1.0"
PRECEDENCE = ("INVALIDATED", "ALERT", "INDETERMINATE", "ACCEPTED")


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    predicate: str
    fields: tuple[str, ...]
    tolerance: str = "Exact contract check; no physical tolerance."
    assumptions: tuple[str, ...] = ("L0 representation only; not physical validation.",)
    failure: str = "INVALIDATED"


RULES = (
    Rule(
        "R-001",
        "Structure and version",
        "Known record type/version and no unknown keys or types.",
        ("/",),
    ),
    Rule("R-002", "Required data", "Every field required by the selected contract exists.", ("/",)),
    Rule(
        "R-003",
        "Canonical units",
        "Declared units match the selected scalar/vector contract.",
        ("*/unit",),
    ),
    Rule(
        "R-004",
        "Finite numbers",
        "Inline numbers are finite; external samples remain unchecked.",
        ("*/value",),
    ),
    Rule(
        "R-005",
        "Ranges and limits",
        "Declared positive ranges, time windows and source limits hold.",
        ("/scenario/target", "/scenario/sources", "/scenario/domain"),
    ),
    Rule(
        "R-006",
        "Shape and frame",
        "Required vector/array shape, frame and unit orientation hold.",
        ("*/frame", "*/shape", "*/orientation", "*/normal"),
        tolerance="Absolute norm tolerance 1e-12 from CONV-1.0; other checks exact.",
    ),
    Rule(
        "R-007",
        "Amplitude and harmonic convention",
        "CONV-1.0, peak and exp(-iwt) are explicit.",
        ("*/conventions", "*/amplitude_convention", "*/phasor_convention"),
    ),
    Rule(
        "R-008",
        "Declared identities",
        "Collection IDs are unique and supplied record links agree.",
        ("*/id", "*/run_id", "/manifest", "/scenario/solver"),
        assumptions=("Matching declarations do not authenticate hashes or files.",),
    ),
    Rule(
        "R-009",
        "Model coverage",
        "A reviewed scientific capability must cover the requested model.",
        ("/scenario/solver", "/scenario/bodies"),
        failure="INDETERMINATE",
        assumptions=("No reviewed scientific model capability is registered in FND-04.",),
    ),
    Rule(
        "R-010",
        "Result completeness",
        "Postchecks require a result and preserve its adverse verdict.",
        ("/result", "/manifest/execution_status"),
        assumptions=("Execution success and supplied ACCEPTED labels are not physical evidence.",),
    ),
)
