"""Versioned content digests and declared links; no run lifecycle or evidence promotion."""

import hashlib
from dataclasses import asdict, dataclass

from aura.errors import IntegrityError, InvalidInputError

from .canonical import CANONICAL_VERSION, canonical_document_bytes, canonical_json_bytes
from .models import Experiment, RunManifest, Scenario, ValidatedRecord

IDENTITY_VERSION = "AURA-IDENTITY-1"


def _digest(scope: str, content: bytes) -> str:
    return hashlib.sha256(f"{CANONICAL_VERSION}\n{scope}\n".encode("ascii") + content).hexdigest()


def document_sha256(record: ValidatedRecord) -> str:
    """Hash a complete canonical document with version and domain separation."""
    return _digest("document", canonical_document_bytes(record))


@dataclass(frozen=True)
class ScenarioIdentity:
    document_sha256: str
    inputs_sha256: str
    identity_version: str = IDENTITY_VERSION
    canonical_version: str = CANONICAL_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def scenario_identity(scenario: Scenario) -> ScenarioIdentity:
    """Exclude only root id/resources/provenance from the conservative input projection."""
    if not isinstance(scenario, Scenario):
        raise InvalidInputError("DOCUMENT_TYPE", "/document_type", "Expected a Scenario.")
    complete = document_sha256(scenario)  # Validates before any exclusions.
    projected = scenario.to_dict()
    for key in ("id", "resources", "provenance"):
        del projected[key]
    return ScenarioIdentity(complete, _digest("scenario-inputs", canonical_json_bytes(projected)))


def _equal(actual, expected, code, path, message):
    if actual != expected:
        raise IntegrityError(code, path, message)


def verify_manifest_configuration(
    manifest: RunManifest, scenario: Scenario, *, experiment: Experiment | None = None
) -> ScenarioIdentity:
    """Verify only supplied configuration/link declarations, not files or model validity."""
    if not isinstance(manifest, RunManifest):
        raise InvalidInputError("DOCUMENT_TYPE", "/document_type", "Expected a RunManifest.")
    identity = scenario_identity(scenario)
    # Revalidation also preserves current date/status/dirty-source contracts.
    data = RunManifest(manifest.to_dict()).to_dict()
    config = scenario.to_dict()
    for key, expected in (
        ("scenario_id", config["id"]), ("solver", config["solver"]),
        ("resources", config["resources"]),
    ):
        _equal(data[key], expected, "IDENTITY_MISMATCH", "/" + key, "Manifest and scenario differ.")
    _equal(
        data["configuration_sha256"], identity.document_sha256,
        "HASH_MISMATCH", "/configuration_sha256", "Full canonical configuration digest differs.",
    )
    if experiment is not None:
        if not isinstance(experiment, Experiment):
            raise InvalidInputError("DOCUMENT_TYPE", "/experiment", "Expected an Experiment.")
        exp = Experiment(experiment.to_dict()).to_dict()
        for key, expected in (
            ("id", data["experiment_id"]), ("scenario_id", config["id"]),
            ("claim_id", data["claim_id"]), ("hypothesis", data["hypothesis"]),
        ):
            _equal(exp[key], expected, "IDENTITY_MISMATCH", "/experiment/" + key,
                   "Experiment and manifest/scenario declarations differ.")
        _equal(exp["scenario_sha256"], identity.document_sha256, "HASH_MISMATCH",
               "/experiment/scenario_sha256", "Experiment configuration digest differs.")
    return identity
