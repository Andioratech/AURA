"""Exact canonical fixtures, content integrity and conservative scenario identity."""

import json
import math
from copy import deepcopy
from dataclasses import FrozenInstanceError
from decimal import localcontext
from pathlib import Path

import pytest

from aura.errors import IntegrityError, InvalidInputError
from aura.mclf import evaluate_scenario
from aura.schema import (
    Experiment,
    RunManifest,
    Scenario,
    canonical_document_bytes,
    canonical_json_bytes,
    canonical_quantity,
    document_sha256,
    dumps_document,
    loads_document,
    scenario_identity,
    validate_document,
    verify_manifest_configuration,
)

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / "tests/fixtures/identity/canonical.json").read_text())


@pytest.fixture
def scenario():
    return Scenario(json.loads((ROOT / "examples/schema/manufactured-scenario.json").read_text()))


def mutate(record, path, value):
    data = record.to_dict()
    parts = path.split("/")[1:]
    parent = data
    for key in parts[:-1]:
        parent = parent[int(key)] if isinstance(parent, list) else parent[key]
    parent[int(parts[-1]) if isinstance(parent, list) else parts[-1]] = value
    return type(record)(data)


@pytest.fixture
def manifest(scenario):
    data = scenario.to_dict()
    return RunManifest({
        "document_type": "run_manifest", "schema_version": "1.0", "id": "EXAMPLE-ID-RUN",
        "experiment_id": "EXAMPLE-ID-EXP", "scenario_id": data["id"],
        "claim_id": "EXAMPLE-ID-CLAIM", "hypothesis": "Identity software test",
        "observables": ["position"], "timestamp_utc": "2026-10-02T00:00:00Z",
        "execution_status": "planned", "source": {"revision": "a" * 40, "dirty": False, "patch_sha256": None},
        "configuration_sha256": document_sha256(scenario),
        "environment": {"lock": {"uri": "fixture://not-a-lock", "sha256": "b" * 64}, "platform": "fixture"},
        "solver": data["solver"], "seed": None, "resources": data["resources"],
        "inputs": [], "outputs": [], "metrics": [], "convergence": [],
        "mclf_pre": {"status": "not_run"}, "mclf_post": {"status": "not_run"},
        "failure_code": None, "operator_notes": "Not a run; no authenticated source or environment",
    })


@pytest.fixture
def experiment(scenario, manifest):
    data = manifest.to_dict()
    return Experiment({
        "document_type": "experiment", "schema_version": "1.0", "id": data["experiment_id"],
        "scenario_id": data["scenario_id"], "scenario_sha256": data["configuration_sha256"],
        "hypothesis": data["hypothesis"], "claim_id": data["claim_id"],
        "primary_observable": {"name": "position", "unit": "m", "definition": "Fixture only",
                               "window": scenario.to_dict()["target"]["window"]},
        "acceptance_rule": "Exact identity", "uncertainty_plan": "Not a physical comparison",
        "protocol": {"uri": "fixture://not-a-protocol", "sha256": "c" * 64},
        "provenance": scenario.to_dict()["provenance"],
    })


@pytest.mark.parametrize("case", GOLDEN["cases"], ids=lambda case: case["name"])
def test_hand_authored_canonical_bytes(case):
    assert canonical_json_bytes(case["input"]) == case["canonical"].encode("ascii")


def test_document_digest_against_independent_sha256sum_fixture():
    record = validate_document(GOLDEN["solver"])
    assert canonical_document_bytes(record) == GOLDEN["solver_canonical"].encode("ascii")
    assert document_sha256(record) == GOLDEN["solver_document_sha256"]


@pytest.mark.parametrize("value", [1.0, -0.0, 0.1, 5e-324, 1e308, 9007199254740993])
def test_exact_numbers_survive_json_decode(value):
    encoded = canonical_json_bytes(value)
    assert canonical_json_bytes(json.loads(encoded)) == encoded
    assert json.loads(encoded) == value


def test_decimal_context_does_not_round_identity():
    with localcontext() as context:
        context.prec = 2
        assert canonical_json_bytes(0.1).decode() == GOLDEN["cases"][2]["canonical"]


def test_numeric_equivalence_is_exact_and_boolean_remains_distinct():
    assert canonical_json_bytes(1) == canonical_json_bytes(1.0) == b"1"
    assert canonical_json_bytes(0) == canonical_json_bytes(-0.0) == b"0"
    assert canonical_json_bytes(True) != canonical_json_bytes(1)
    assert canonical_json_bytes(9007199254740993) != canonical_json_bytes(9007199254740992.0)
    assert canonical_json_bytes(0.1) != canonical_json_bytes(math.nextafter(0.1, 1))


def test_array_and_unicode_semantics_are_not_rewritten():
    assert canonical_json_bytes([1, 2]) != canonical_json_bytes([2, 1])
    assert canonical_json_bytes("é") != canonical_json_bytes("e\u0301")


@pytest.mark.parametrize("value,code", [(float("nan"), "NONFINITE"), (float("inf"), "NONFINITE"),
                                      (10**400, "NONFINITE"), ({1: "a"}, "KEY_TYPE"),
                                      ((1, 2), "VALUE_TYPE")])
def test_invalid_canonical_values(value, code):
    with pytest.raises(InvalidInputError) as caught:
        canonical_json_bytes(value)
    assert caught.value.code == code


def test_input_depth_size_and_expansion_caps(monkeypatch):
    import aura.schema.canonical as module

    cyclic = []
    cyclic.append(cyclic)
    with pytest.raises(InvalidInputError, match="INPUT_LIMIT"):
        canonical_json_bytes(cyclic)
    with pytest.raises(InvalidInputError, match="INPUT_LIMIT"):
        canonical_json_bytes("x" * (1024 * 1024))
    monkeypatch.setattr(module, "MAX_CANONICAL_BYTES", 8)
    assert canonical_json_bytes("123456") == b'"123456"'
    with pytest.raises(InvalidInputError, match="CANONICAL_LIMIT"):
        canonical_json_bytes(0.1)


@pytest.mark.parametrize("format", ["json", "yaml"])
def test_scenario_roundtrip_and_key_order(scenario, format):
    def reverse(value):
        if type(value) is dict:
            return {key: reverse(value[key]) for key in reversed(value)}
        if type(value) is list:
            return [reverse(item) for item in value]
        return value

    reordered = Scenario(reverse(scenario.to_dict()))
    restored = loads_document(dumps_document(reordered, format=format), format=format)
    assert scenario_identity(restored) == scenario_identity(scenario)
    canonical = canonical_document_bytes(scenario)
    assert canonical_document_bytes(loads_document(canonical)) == canonical


@pytest.mark.parametrize("path,value", [
    ("/medium/density/value", 999), ("/medium/temperature/value", 301),
    ("/medium/dynamic_viscosity/value", 0.002), ("/medium/amplitude_attenuation/value", 0.5),
    ("/medium/sound_speed/value", 1501), ("/medium/compressibility/value", 1e-9),
    ("/bodies/0/mass/value", 1e-11), ("/bodies/0/geometry/radius/value", 2e-5),
    ("/bodies/0/material", "another material"), ("/bodies/0/initial_state/velocity/value", [1, 0, 0]),
    ("/sources/frequency/value", 2000000), ("/sources/elements/0/phase/value", 0.5),
    ("/sources/elements/0/pressure_amplitude/value", 3),
    ("/solver/model_version", "0.1"), ("/solver/parameters", {"max_iterations": 3}),
    ("/domain/boundary_model", "other-boundary"), ("/domain/size/value", [2, 2, 2]),
    ("/gravity/value", [0, 0, 1]), ("/target/acceleration/value", [0, 0, 0.002]),
    ("/target/window/end/value", 2), ("/medium/provenance/reference", "different source"),
])
def test_changed_inputs_change_both_identities(scenario, path, value):
    original = scenario_identity(scenario)
    changed = scenario_identity(mutate(scenario, path, value))
    assert original.document_sha256 != changed.document_sha256
    assert original.inputs_sha256 != changed.inputs_sha256


@pytest.mark.parametrize("path,value", [
    ("/id", "EXAMPLE-RENAMED"), ("/resources/ram_bytes", 2048),
    ("/provenance/reference", "/another/path/to/notes"),
])
def test_only_explicit_root_metadata_excluded_from_projection(scenario, path, value):
    original = scenario_identity(scenario)
    changed = scenario_identity(mutate(scenario, path, value))
    assert changed.document_sha256 != original.document_sha256
    assert changed.inputs_sha256 == original.inputs_sha256
    assert original.inputs_sha256 != original.document_sha256


def test_explicit_conversion_is_required_before_identity(scenario):
    data = scenario.to_dict()
    data["bodies"][0]["geometry"]["radius"] = {"value": 1, "unit": "mm"}
    with pytest.raises(InvalidInputError, match="UNIT_MISMATCH"):
        Scenario(data)
    data["bodies"][0]["geometry"]["radius"] = canonical_quantity(
        {"value": 1, "unit": "mm"}, expected_unit="m"
    )
    assert scenario_identity(Scenario(data)) == scenario_identity(
        mutate(scenario, "/bodies/0/geometry/radius/value", 0.001)
    )


def test_identity_isolated_and_frozen(scenario):
    before = scenario.to_dict()
    identity = scenario_identity(scenario)
    copy = identity.to_dict()
    copy["inputs_sha256"] = "f" * 64
    assert scenario.to_dict() == before
    assert identity.identity_version == "AURA-IDENTITY-1"
    with pytest.raises(FrozenInstanceError):
        identity.inputs_sha256 = "f" * 64


def test_manifest_and_experiment_links(scenario, manifest, experiment):
    before = deepcopy(manifest.to_dict())
    assert verify_manifest_configuration(manifest, scenario, experiment=experiment) == scenario_identity(scenario)
    assert manifest.to_dict() == before


@pytest.mark.parametrize("path,value,code", [
    ("/configuration_sha256", "0" * 64, "HASH_MISMATCH"),
    ("/scenario_id", "EXAMPLE-WRONG", "IDENTITY_MISMATCH"),
    ("/solver/model_version", "other", "IDENTITY_MISMATCH"),
    ("/resources/disk_bytes", 3, "IDENTITY_MISMATCH"),
])
def test_manifest_mismatch(scenario, manifest, path, value, code):
    with pytest.raises(IntegrityError) as caught:
        verify_manifest_configuration(mutate(manifest, path, value), scenario)
    assert caught.value.code == code
    expected_path = path if code == "HASH_MISMATCH" else "/" + path.split("/")[1]
    assert caught.value.path == expected_path


@pytest.mark.parametrize("path,value,code", [
    ("/id", "EXAMPLE-OTHER", "IDENTITY_MISMATCH"),
    ("/scenario_id", "EXAMPLE-OTHER", "IDENTITY_MISMATCH"),
    ("/claim_id", "EXAMPLE-OTHER", "IDENTITY_MISMATCH"),
    ("/hypothesis", "Different question", "IDENTITY_MISMATCH"),
    ("/scenario_sha256", "0" * 64, "HASH_MISMATCH"),
])
def test_experiment_mismatch(scenario, manifest, experiment, path, value, code):
    with pytest.raises(IntegrityError) as caught:
        verify_manifest_configuration(manifest, scenario, experiment=mutate(experiment, path, value))
    assert (caught.value.code, caught.value.path) == (code, "/experiment" + path)


def test_changed_config_and_projection_cannot_substitute_full_identity(scenario, manifest):
    changed = mutate(scenario, "/gravity/value", [0, 0, 1])
    with pytest.raises(IntegrityError, match="HASH_MISMATCH"):
        verify_manifest_configuration(manifest, changed)
    substituted = mutate(manifest, "/configuration_sha256", scenario_identity(scenario).inputs_sha256)
    with pytest.raises(IntegrityError, match="HASH_MISMATCH"):
        verify_manifest_configuration(substituted, scenario)


@pytest.mark.parametrize("path,value", [
    ("/timestamp_utc", "2026-10-03T00:00:00Z"), ("/environment/lock/uri", "/new/location"),
    ("/seed", 9007199254740993),
])
def test_manifest_metadata_changes_full_manifest_not_configuration(scenario, manifest, path, value):
    changed = mutate(manifest, path, value)
    assert document_sha256(changed) != document_sha256(manifest)
    assert verify_manifest_configuration(changed, scenario) == scenario_identity(scenario)


def test_verified_configuration_does_not_authenticate_other_evidence(scenario, manifest):
    verify_manifest_configuration(manifest, scenario)
    report = evaluate_scenario(
        scenario.to_dict(), manifest=manifest.to_dict(), report_id="EXAMPLE-ID-AUDIT",
        run_id=manifest.to_dict()["id"], stage="pre",
    )
    assert report.verdict == "INDETERMINATE"
    assert any(item.code == "HASH_UNCHECKED" for check in report.checks for item in check.findings)


def test_wrong_types_and_invalid_versions_cannot_bypass_validation(scenario, manifest):
    with pytest.raises(InvalidInputError, match="INPUT_TYPE"):
        document_sha256(scenario.to_dict())
    with pytest.raises(InvalidInputError, match="DOCUMENT_TYPE"):
        scenario_identity(manifest)
    with pytest.raises(InvalidInputError, match="DOCUMENT_TYPE"):
        verify_manifest_configuration(scenario, scenario)
    with pytest.raises(InvalidInputError, match="DOCUMENT_TYPE"):
        verify_manifest_configuration(manifest, scenario, experiment=scenario)
    with pytest.raises(InvalidInputError, match="SCHEMA_VERSION"):
        mutate(scenario, "/schema_version", "2.0")


def test_collection_order_and_optional_geometry_properties_are_preserved(scenario):
    data = scenario.to_dict()
    extra = deepcopy(data["bodies"][0])
    extra["id"] = "EXAMPLE-BOX"
    extra["geometry"] = {"kind": "box", "dimensions": {"value": [0.1, 0.2, 0.3], "unit": "m"}}
    extra["mass"] = {"value": 6, "unit": "kg"}
    data["bodies"].append(extra)
    initial = scenario_identity(Scenario(data))
    data["bodies"].reverse()
    assert scenario_identity(Scenario(data)).inputs_sha256 != initial.inputs_sha256
    data["bodies"].reverse()
    data["bodies"][1]["inertia"] = {"frame": "body", "unit": "kg*m^2", "value": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}
    assert scenario_identity(Scenario(data)).inputs_sha256 != initial.inputs_sha256


def test_invalid_excluded_fields_still_rejected(scenario):
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        mutate(scenario, "/resources/ram_bytes", -1)
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        mutate(scenario, "/id", "not a valid ID")


def test_seed_integer_precision_not_lost(manifest):
    first = mutate(manifest, "/seed", 9007199254740992)
    second = mutate(manifest, "/seed", 9007199254740993)
    assert document_sha256(first) != document_sha256(second)
    assert loads_document(canonical_document_bytes(second)).to_dict()["seed"] == 9007199254740993
