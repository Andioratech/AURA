"""Versioned structural validation; not a model or evidence acceptance gate."""

from .canonical import canonical_document_bytes, canonical_json_bytes
from .identity import (
    ScenarioIdentity,
    document_sha256,
    scenario_identity,
    verify_manifest_configuration,
)
from .io import dumps_document, load_document, loads_document
from .models import (
    Body,
    Experiment,
    FieldResult,
    ForceResult,
    MclfReport,
    Medium,
    RunManifest,
    Scenario,
    SolverSpec,
    TransducerArray,
    validate_document,
)
from .quantities import canonical_quantity

__all__ = [
    "Body",
    "Experiment",
    "FieldResult",
    "ForceResult",
    "MclfReport",
    "Medium",
    "RunManifest",
    "Scenario",
    "ScenarioIdentity",
    "SolverSpec",
    "TransducerArray",
    "canonical_document_bytes",
    "canonical_json_bytes",
    "canonical_quantity",
    "document_sha256",
    "dumps_document",
    "load_document",
    "loads_document",
    "scenario_identity",
    "validate_document",
    "verify_manifest_configuration",
]
