"""Lifecycle fault injection; synthetic source observations are explicitly test-only."""

import copy
import importlib
import json
from pathlib import Path

import pytest

from aura.errors import IntegrityError, InvalidInputError
from aura.runs import check_run, execute, provenance
from aura.runs.manifest import digest, encode, publish, read_bytes
from aura.schema import Scenario, document_sha256

ROOT = Path(__file__).resolve().parents[1]
ENGINE = importlib.import_module("aura.runs.execute")


@pytest.fixture
def inputs(tmp_path):
    scenario = json.loads((ROOT / "examples/schema/manufactured-scenario.json").read_text())
    scenario["solver"].update(model_id="lifecycle-receipt", model_version="1.0",
                              equation_ids=["SOFTWARE-RUN-01"], regime=["Software diagnostic only"])
    scenario["resources"] = {"ram_bytes": 1024**3, "disk_bytes": 16 * 1024**2,
                             "wall_time": {"value": 30, "unit": "s"}}
    protocol = b"Frozen software lifecycle test; no physical hypothesis.\n"
    (tmp_path / "protocol.md").write_bytes(protocol)
    exp = {
        "document_type": "experiment", "schema_version": "1.0", "id": "EXP-TEST-ONLY",
        "scenario_id": scenario["id"], "scenario_sha256": document_sha256(Scenario(scenario)),
        "hypothesis": "Test-only recorder retains a receipt", "claim_id": "TEST-ONLY",
        "primary_observable": {"name": "receipt", "unit": "1", "definition": "Receipt exists",
                               "window": scenario["target"]["window"]},
        "acceptance_rule": "Exact software checks", "uncertainty_plan": "No physical result",
        "protocol": {"uri": "protocol.md", "sha256": digest(protocol)},
        "provenance": scenario["provenance"],
    }
    scenario_path, exp_path = tmp_path / "scenario.json", tmp_path / "experiment.json"
    scenario_path.write_bytes(encode(scenario)); exp_path.write_bytes(encode(exp))
    return scenario_path, exp_path, tmp_path / "run"


@pytest.fixture
def analytical_inputs(tmp_path):
    scenario = json.loads((ROOT / "examples/schema/manufactured-scenario.json").read_text())
    scenario["medium"]["dynamic_viscosity"]["value"] = 0
    scenario["bodies"][0]["initial_state"]["position"]["value"] = [0, 0, 0]
    scenario["domain"] = {
        "origin": {"value": [-0.0015, -0.0015, -0.0015], "unit": "m"},
        "size": {"value": [0.003, 0.003, 0.003], "unit": "m"},
        "boundary_model": "analytic-window",
        "boundary_reference": "Finite observation window; no wall solution",
    }
    scenario["sources"]["elements"][0].update(
        position={"value": [0, 0, 0], "unit": "m"},
        normal={"value": [1, 0, 0], "unit": "1"},
        model="ideal_plane_wave",
    )
    scenario["solver"].update(
        model_id="analytic-plane-field", model_version="1.0",
        equation_ids=["EQ-007"], regime=["Manufactured plane-wave field"],
        precision="complex128", parameters={},
    )
    scenario["resources"] = {
        "ram_bytes": 4 * 1024**3, "disk_bytes": 16 * 1024**2,
        "wall_time": {"value": 30, "unit": "s"},
    }
    request = {
        "contract": "FIELD-REQUEST-1.0", "case_id": "B03-01",
        "box_min_m": [-0.0015, -0.0015, -0.0015],
        "box_max_m": [0.0015, 0.0015, 0.0015],
        "coordinates_m": [[0, 0, 0], [0.000375, 0, 0]],
    }
    request_bytes = encode(request)
    (tmp_path / "field-request.json").write_bytes(request_bytes)
    exp = {
        "document_type": "experiment", "schema_version": "1.0", "id": "EXP-ANALYTIC-TEST",
        "scenario_id": scenario["id"],
        "scenario_sha256": document_sha256(Scenario(scenario)),
        "hypothesis": "Test-only recorder serializes a manufactured analytical field",
        "claim_id": "TEST-ONLY",
        "primary_observable": {
            "name": "incident_field", "unit": "Pa", "definition": "Recorded harmonic pressure field",
            "window": scenario["target"]["window"],
        },
        "acceptance_rule": "Integrity only; numerical comparison is separate",
        "uncertainty_plan": "No physical result",
        "protocol": {"uri": "field-request.json", "sha256": digest(request_bytes)},
        "provenance": scenario["provenance"],
    }
    scenario_path, exp_path = tmp_path / "scenario.json", tmp_path / "experiment.json"
    scenario_path.write_bytes(encode(scenario))
    exp_path.write_bytes(encode(exp))
    return scenario_path, exp_path, tmp_path / "run"


@pytest.fixture
def observed(monkeypatch):
    # Published clean-source CLI checks are performed separately at delivery.
    # Fault injection uses this synthetic observation, never scientific evidence.
    source = {"revision": "a" * 40, "dirty": False, "patch_sha256": None,
              "package_files_sha256": {"src/aura/__init__.py": "b" * 64}}
    locks = {name: (ROOT / "requirements" / name).read_bytes() for name in provenance.LOCK_NAMES}
    inventory = json.loads(locks["environment-linux-py312.json"])
    environment = {"errors": [], "profile": inventory["profile"],
                   "runtime": {"platform": "test-only", **{key: inventory[key] for key in
                               ("python", "implementation", "system", "machine")}},
                   "installed": {"aura-science": "0.1.0", **{
                       item["name"]: item["version"] for item in inventory["artifacts"]}},
                   "input_sha256": {name: digest(data) for name, data in locks.items()}}
    monkeypatch.setattr(provenance, "capture", lambda: (copy.deepcopy(source), copy.deepcopy(environment), locks))
    return source, environment, locks


def change_scenario(inputs, mutate):
    path, exp_path, _ = inputs
    data = json.loads(path.read_bytes()); mutate(data); path.write_bytes(encode(data))
    exp = json.loads(exp_path.read_bytes())
    exp["scenario_sha256"] = document_sha256(Scenario(data))
    exp_path.write_bytes(encode(exp))


def launch(inputs):
    scenario, experiment, output = inputs
    return execute(scenario, experiment, output=output, seed=None)


def test_completed_bundle_keeps_scientific_unknown(inputs, observed):
    before = [path.read_bytes() for path in inputs[:2]]
    result = launch(inputs)
    assert result["execution_status"] == "completed"
    assert result["exit_code"] == 3 and result["verdict"] == "INDETERMINATE"
    output = inputs[2]
    checked = check_run(output, expected_sha256=result["manifest_sha256"])
    assert checked["integrity"] == "VERIFIED" and checked["exit_code"] == 3
    assert [path.read_bytes() for path in inputs[:2]] == before
    manifest = json.loads((output / "manifest.json").read_bytes())
    running = json.loads((output / "running.json").read_bytes())
    assert running["execution_status"] == "running" and running["outputs"] == []
    assert manifest["source"]["revision"] == "a" * 40
    assert manifest["seed"] is None
    assert manifest["mclf_pre"]["verdict"] == manifest["mclf_post"]["verdict"] == "INDETERMINATE"
    for ref in [*manifest["inputs"], *manifest["outputs"]]:
        assert digest((output / ref["uri"]).read_bytes()) == ref["sha256"]


def test_analytical_field_run_is_immutable_and_checkable(analytical_inputs, observed):
    scenario, experiment, output = analytical_inputs
    result = execute(scenario, experiment, output=output, seed=None)
    assert (result["execution_status"], result["verdict"], result["exit_code"]) == (
        "completed", "INDETERMINATE", 3,
    )
    assert result["scope"].startswith("Analytical incident-field")
    checked = check_run(output, expected_sha256=result["manifest_sha256"])
    assert (checked["integrity"], checked["verdict"]) == ("VERIFIED", "INDETERMINATE")
    records = {
        "coordinates": json.loads((output / "field-coordinates.json").read_bytes()),
        "pressure": json.loads((output / "field-pressure.json").read_bytes()),
        "velocity": json.loads((output / "field-velocity.json").read_bytes()),
        "pressure_gradient": json.loads((output / "field-pressure-gradient.json").read_bytes()),
    }
    assert records["pressure"]["values"][0] == [2, 0]
    assert records["pressure"]["values"][1] == pytest.approx([0, 2], abs=1e-15)
    assert records["coordinates"]["values"] == [[0, 0, 0], [0.000375, 0, 0]]
    index = json.loads((output / "field-index.json").read_bytes())
    assert index["contract"] == "FIELD-INDEX-1.0"
    assert index["run_policy"] == "ANALYTIC-RUN-1.0"
    assert index["pressure_gradient"]["unit"] == "Pa/m"
    assert index["run_id"] == result["run_id"]
    audit = json.loads((output / "audit-post.json").read_bytes())
    assert audit["scope"].startswith("Analytical incident-field")


def test_analytical_check_rejects_component_tampering(analytical_inputs, observed):
    scenario, experiment, output = analytical_inputs
    execute(scenario, experiment, output=output, seed=None)
    component = output / "field-pressure-gradient.json"
    component.write_bytes(component.read_bytes() + b" ")
    with pytest.raises((InvalidInputError, OSError), match="HASH_MISMATCH"):
        check_run(output)


def test_analytical_check_rejects_diagnostic_only_post_scope(analytical_inputs, observed):
    scenario, experiment, output = analytical_inputs
    execute(scenario, experiment, output=output, seed=None)
    post_path = output / "audit-post.json"
    post = json.loads(post_path.read_bytes())
    post["scope"] = ENGINE.LIMITATION
    post_bytes = encode(post)
    post_path.write_bytes(post_bytes)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["mclf_post"]["report"]["sha256"] = digest(post_bytes)
    manifest_bytes = encode(manifest)
    manifest_path.write_bytes(manifest_bytes)
    (output / "manifest.sha256").write_text(digest(manifest_bytes) + "\n")
    with pytest.raises(IntegrityError, match="RUN_AUDIT"):
        check_run(output)


def test_two_source_analytical_run_preserves_interference(analytical_inputs, observed):
    scenario_path, experiment_path, output = analytical_inputs
    scenario = json.loads(scenario_path.read_bytes())
    second = copy.deepcopy(scenario["sources"]["elements"][0])
    second.update(id="EXAMPLE-SOURCE-02", normal={"value": [-1, 0, 0], "unit": "1"})
    scenario["sources"]["elements"].append(second)
    scenario["solver"]["equation_ids"] = ["EQ-008"]
    scenario_path.write_bytes(encode(scenario))
    experiment = json.loads(experiment_path.read_bytes())
    experiment["scenario_sha256"] = document_sha256(Scenario(scenario))
    experiment_path.write_bytes(encode(experiment))
    request_path = scenario_path.parent / "field-request.json"
    request = json.loads(request_path.read_bytes())
    request["case_id"] = "B04-01"
    request["coordinates_m"] = [[0, 0, 0], [0.000375, 0, 0]]
    request_bytes = encode(request)
    request_path.write_bytes(request_bytes)
    experiment["protocol"]["sha256"] = digest(request_bytes)
    experiment_path.write_bytes(encode(experiment))

    result = execute(scenario_path, experiment_path, output=output, seed=None)
    assert result["execution_status"] == "completed", result["error"]
    assert check_run(output)["integrity"] == "VERIFIED"
    pressure = json.loads((output / "field-pressure.json").read_bytes())["values"]
    velocity = json.loads((output / "field-velocity.json").read_bytes())["values"]
    assert pressure[0] == [4, 0]
    assert pressure[1] == pytest.approx([0, 0], abs=1e-15)
    assert velocity[1][0] == pytest.approx([0, 4 / 1_500_000], abs=1e-15)


def test_noncollinear_pair_uses_superposition_equation(analytical_inputs, observed):
    scenario_path, experiment_path, output = analytical_inputs
    scenario = json.loads(scenario_path.read_bytes())
    second = copy.deepcopy(scenario["sources"]["elements"][0])
    second.update(id="EXAMPLE-SOURCE-02", normal={"value": [0, 1, 0], "unit": "1"})
    scenario["sources"]["elements"].append(second)
    scenario["solver"]["equation_ids"] = ["EQ-008"]
    scenario_path.write_bytes(encode(scenario))
    experiment = json.loads(experiment_path.read_bytes())
    experiment["scenario_sha256"] = document_sha256(Scenario(scenario))
    experiment_path.write_bytes(encode(experiment))
    request_path = scenario_path.parent / "field-request.json"
    request = json.loads(request_path.read_bytes())
    request["case_id"] = "B05-01"
    request_bytes = encode(request)
    request_path.write_bytes(request_bytes)
    experiment["protocol"]["sha256"] = digest(request_bytes)
    experiment_path.write_bytes(encode(experiment))

    result = execute(scenario_path, experiment_path, output=output, seed=None)
    assert result["execution_status"] == "completed", result["error"]
    assert check_run(output)["integrity"] == "VERIFIED"
    pressure = json.loads((output / "field-pressure.json").read_bytes())["values"]
    velocity = json.loads((output / "field-velocity.json").read_bytes())["values"]
    assert pressure[0] == [4, 0]
    assert pressure[1] == pytest.approx([2, 2], abs=1e-15)
    assert velocity[1][0] == pytest.approx([0, 2 / 1_500_000], abs=1e-15)
    assert velocity[1][1] == pytest.approx([2 / 1_500_000, 0], abs=1e-15)


def test_analytical_driver_rejects_unadmitted_piston_before_provenance(analytical_inputs, monkeypatch):
    scenario_path, experiment_path, output = analytical_inputs
    scenario = json.loads(scenario_path.read_bytes())
    source = scenario["sources"]["elements"][0]
    source["model"] = "circular_piston"
    source["aperture_radius"] = {"value": 0.001, "unit": "m"}
    scenario_path.write_bytes(encode(scenario))
    experiment = json.loads(experiment_path.read_bytes())
    experiment["scenario_sha256"] = document_sha256(Scenario(scenario))
    experiment_path.write_bytes(encode(experiment))
    monkeypatch.setattr(provenance, "capture", lambda: pytest.fail("Reached source observation"))
    with pytest.raises(InvalidInputError, match="FIELD_MODEL"):
        execute(scenario_path, experiment_path, output=output, seed=None)
    assert not output.exists()


def test_analytical_request_rejects_outside_sample_before_provenance(analytical_inputs, monkeypatch):
    scenario_path, experiment_path, output = analytical_inputs
    request_path = scenario_path.parent / "field-request.json"
    request = json.loads(request_path.read_bytes())
    request["coordinates_m"][0] = [0.002, 0, 0]
    request_bytes = encode(request)
    request_path.write_bytes(request_bytes)
    experiment = json.loads(experiment_path.read_bytes())
    experiment["protocol"]["sha256"] = digest(request_bytes)
    experiment_path.write_bytes(encode(experiment))
    monkeypatch.setattr(provenance, "capture", lambda: pytest.fail("Reached source observation"))
    with pytest.raises(InvalidInputError, match="FIELD_DOMAIN"):
        execute(scenario_path, experiment_path, output=output, seed=None)
    assert not output.exists()


def test_deliberate_failure_retains_partial_output(inputs, observed):
    change_scenario(inputs, lambda data: data["solver"].update(model_id="lifecycle-failure"))
    result = launch(inputs)
    assert (result["execution_status"], result["exit_code"]) == ("failed", 1)
    assert result["error"]["code"] == "RUN_EXECUTION"
    assert (inputs[2] / "partial.json").exists()
    assert check_run(inputs[2])["integrity"] == "VERIFIED"
    assert check_run(inputs[2])["verdict"] == "INVALIDATED"


def test_interruption_retains_partial_output(inputs, observed, monkeypatch):
    def interrupted(config, emit):
        emit("partial.json", {"stage": "interrupted"})
        raise KeyboardInterrupt("injected interrupt")
    monkeypatch.setattr(ENGINE, "_driver", interrupted)
    result = launch(inputs)
    assert (result["execution_status"], result["exit_code"]) == ("aborted", 130)
    assert check_run(inputs[2])["execution_status"] == "aborted"


def test_existing_output_never_changes(inputs, observed):
    launch(inputs)
    snapshot = {p.name: p.read_bytes() for p in inputs[2].iterdir()}
    with pytest.raises(IntegrityError, match="RUN_EXISTS"):
        launch(inputs)
    assert snapshot == {p.name: p.read_bytes() for p in inputs[2].iterdir()}


@pytest.mark.parametrize("kind", ["empty", "file", "symlink", "dangling"])
def test_other_existing_outputs_rejected(inputs, observed, kind, tmp_path):
    out = inputs[2]
    if kind == "empty": out.mkdir()
    elif kind == "file": out.write_text("retained")
    else: out.symlink_to(tmp_path if kind == "symlink" else tmp_path / "missing")
    with pytest.raises(IntegrityError, match="RUN_EXISTS"):
        launch(inputs)


@pytest.mark.parametrize("field", ["ram_bytes", "disk_bytes", "wall_time"])
def test_resources_rejected_before_creation(inputs, observed, field, monkeypatch):
    def mutate(data):
        data["resources"][field] = {"value": 0.001, "unit": "s"} if field == "wall_time" else 1
    change_scenario(inputs, mutate)
    monkeypatch.setattr(ENGINE, "_driver", lambda *a: pytest.fail("Reached driver"))
    with pytest.raises(IntegrityError, match="RUN_RESOURCE"):
        launch(inputs)
    assert not inputs[2].exists()


@pytest.mark.parametrize("fault", ["schema", "model", "version", "protocol", "experiment", "seed"])
def test_invalid_inputs_do_not_capture_or_allocate(inputs, monkeypatch, fault):
    monkeypatch.setattr(provenance, "capture", lambda: pytest.fail("Reached source observation"))
    if fault == "schema": inputs[0].write_text('{}')
    elif fault in ("model", "version"):
        change_scenario(inputs, lambda d: d["solver"].update(
            {"model_id" if fault == "model" else "model_version": "unknown"}))
    elif fault == "protocol": (inputs[0].parent / "protocol.md").write_text("changed")
    elif fault == "experiment":
        data = json.loads(inputs[1].read_text()); data["scenario_sha256"] = "0" * 64
        inputs[1].write_bytes(encode(data))
    with pytest.raises(InvalidInputError):
        execute(inputs[0], inputs[1], output=inputs[2], seed=-1 if fault == "seed" else None)
    assert not inputs[2].exists()


@pytest.mark.parametrize("code", ["RUN_SOURCE", "RUN_DIRTY_SOURCE", "RUN_ENVIRONMENT"])
def test_provenance_failure_before_allocation(inputs, monkeypatch, code):
    def reject(): raise IntegrityError(code, "", "injected provenance failure")
    monkeypatch.setattr(provenance, "capture", reject)
    with pytest.raises(IntegrityError, match=code): launch(inputs)
    assert not inputs[2].exists()


def test_incomplete_finalization_is_visible(inputs, observed, monkeypatch):
    real = ENGINE.publish
    def failure(folder, name, data):
        if name == "manifest.json": raise OSError("injected disk failure")
        return real(folder, name, data)
    monkeypatch.setattr(ENGINE, "publish", failure)
    with pytest.raises(OSError): launch(inputs)
    original = {p.name: p.read_bytes() for p in inputs[2].iterdir()}
    assert check_run(inputs[2])["integrity"] == "INCOMPLETE"
    assert original == {p.name: p.read_bytes() for p in inputs[2].iterdir()}
    with pytest.raises(IntegrityError, match="RUN_EXISTS"): launch(inputs)


@pytest.mark.parametrize("name", ["scenario.json", "experiment.json", "protocol.md", "source.json",
                                  "environment.json", "receipt.json", "audit-pre.json",
                                  "audit-post.json", "running.json", "manifest.json", "manifest.sha256"])
@pytest.mark.parametrize("mutation", ["alter", "remove", "symlink"])
def test_bundle_corruption_is_detected(inputs, observed, name, mutation, tmp_path):
    launch(inputs)
    path = inputs[2] / name
    if mutation == "alter": path.write_bytes(path.read_bytes() + b" ")
    elif mutation == "remove": path.unlink()
    else:
        other = tmp_path / "replacement"; other.write_bytes(path.read_bytes())
        path.unlink(); path.symlink_to(other)
    # Removing the terminal manifest leaves an incomplete initial record, never completion.
    if name == "manifest.json" and mutation == "remove":
        assert check_run(inputs[2])["integrity"] == "INCOMPLETE"
    else:
        with pytest.raises((InvalidInputError, OSError)): check_run(inputs[2])


def test_manifest_external_anchor_detects_replaced_local_digest(inputs, observed):
    result = launch(inputs)
    path = inputs[2] / "manifest.json"
    data = json.loads(path.read_text()); data["operator_notes"] = "changed"
    path.write_bytes(encode(data))
    (inputs[2] / "manifest.sha256").write_text(digest(path.read_bytes()) + "\n")
    with pytest.raises(IntegrityError, match="HASH_MISMATCH"):
        check_run(inputs[2], expected_sha256=result["manifest_sha256"])


@pytest.mark.parametrize("uri", ["../outside", "/tmp/outside", "https://example.com", "a/b", "a\\b"])
def test_reference_traversal_rejected(inputs, observed, uri):
    launch(inputs)
    path = inputs[2] / "manifest.json"
    data = json.loads(path.read_text()); data["outputs"][0]["uri"] = uri
    path.write_bytes(encode(data)); (inputs[2] / "manifest.sha256").write_text(digest(path.read_bytes()) + "\n")
    with pytest.raises(IntegrityError, match="RUN_PATH"): check_run(inputs[2])


def test_exclusive_publication(tmp_path):
    publish(tmp_path, "record.json", b"first")
    with pytest.raises(FileExistsError): publish(tmp_path, "record.json", b"second")
    assert read_bytes(tmp_path / "record.json") == b"first"
    assert {p.name for p in tmp_path.iterdir()} == {"record.json"}


def test_fifo_rejected_without_waiting(tmp_path):
    import os
    path = tmp_path / "pipe"; os.mkfifo(path)
    with pytest.raises(IntegrityError, match="RUN_FILE_LIMIT"): read_bytes(path)


def test_driver_without_required_output_fails(inputs, observed, monkeypatch):
    monkeypatch.setattr(ENGINE, "_driver", lambda *a: None)
    result = launch(inputs)
    assert result["error"]["code"] == "RUN_OUTPUT_MISSING"
    assert check_run(inputs[2])["execution_status"] == "failed"


def test_changed_source_is_preserved_as_failure(inputs, observed, monkeypatch):
    original = provenance.capture
    calls = 0
    def capture():
        nonlocal calls
        calls += 1
        source, env, locks = original()
        if calls > 1: source["revision"] = "c" * 40
        return source, env, locks
    monkeypatch.setattr(provenance, "capture", capture)
    assert launch(inputs)["error"]["code"] == "RUN_SOURCE_CHANGED"
    assert check_run(inputs[2])["execution_status"] == "failed"


@pytest.mark.parametrize("format", ["json", "yaml"])
@pytest.mark.parametrize("case", json.loads(
    (ROOT / "tests/fixtures/foundation/rejections.json").read_text())["cases"],
    ids=lambda case: case["id"])
def test_known_input_faults_stop_before_allocation(inputs, monkeypatch, case, format):
    import yaml
    data = json.loads(inputs[0].read_text())
    parts = case["path"].strip("/").split("/"); parent = data
    for part in parts[:-1]: parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    if case.get("operation") == "remove": del parent[key]
    else: parent[key] = case["value"]
    path = inputs[0].with_suffix("." + format)
    path.write_text(json.dumps(data) if format == "json" else yaml.safe_dump(data))
    monkeypatch.setattr(provenance, "capture", lambda: pytest.fail("Invalid input reached capture"))
    with pytest.raises(InvalidInputError) as caught:
        execute(path, inputs[1], output=inputs[2], seed=None)
    assert caught.value.code == case["reader_code"]
    assert not inputs[2].exists()


@pytest.mark.parametrize("command", ["run", "check"])
def test_cli_json_success_retains_unknown(inputs, observed, capsys, command):
    from aura.cli import main
    if command == "run":
        args = ["run", str(inputs[0]), "--experiment", str(inputs[1]),
                "--output", str(inputs[2]), "--no-randomness", "--json"]
    else:
        launch(inputs); args = ["check", str(inputs[2]), "--json"]
    assert main(args) == 3
    captured = capsys.readouterr(); assert not captured.err
    result = json.loads(captured.out)
    assert result["verdict"] == "INDETERMINATE" and result["execution_status"] == "completed"


def test_cli_failure_and_existing_output(inputs, observed, capsys):
    from aura.cli import main
    change_scenario(inputs, lambda d: d["solver"].update(model_id="lifecycle-failure"))
    args = ["run", str(inputs[0]), "--experiment", str(inputs[1]), "--output", str(inputs[2]),
            "--seed", "0", "--json"]
    assert main(args) == 1
    assert json.loads(capsys.readouterr().out)["execution_status"] == "failed"
    assert main(args) == 1
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "RUN_EXISTS"


def test_cli_requires_explicit_seed_policy(inputs):
    from aura.cli import main
    with pytest.raises(SystemExit) as caught:
        main(["run", str(inputs[0]), "--experiment", str(inputs[1])])
    assert caught.value.code == 2 and not inputs[2].exists()


def test_cli_sigterm_is_recorded_and_handler_restored(inputs, observed, capsys, monkeypatch):
    import os
    import signal

    from aura.cli import main
    previous = signal.getsignal(signal.SIGTERM)
    def interrupt(config, emit):
        emit("partial.json", {"stage": "before_signal"})
        os.kill(os.getpid(), signal.SIGTERM)
    monkeypatch.setattr(ENGINE, "_driver", interrupt)
    assert main(["run", str(inputs[0]), "--experiment", str(inputs[1]), "--output", str(inputs[2]),
                 "--no-randomness", "--json"]) == 143
    assert json.loads(capsys.readouterr().out)["execution_status"] == "aborted"
    assert signal.getsignal(signal.SIGTERM) == previous
    assert check_run(inputs[2])["execution_status"] == "aborted"


def test_extra_unindexed_file_rejected(inputs, observed):
    launch(inputs); (inputs[2] / "extra.txt").write_text("unindexed")
    with pytest.raises(IntegrityError, match="RUN_EXTRA_FILES"): check_run(inputs[2])


def test_recorded_time_cap_failure(inputs, observed, monkeypatch):
    values = iter([0, 31, 32])
    monkeypatch.setattr(ENGINE.time, "monotonic", lambda: next(values))
    assert launch(inputs)["error"]["code"] == "RUN_TIME_LIMIT"
    assert check_run(inputs[2])["execution_status"] == "failed"


def test_atomic_publish_race_has_one_winner(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    def attempt(value):
        try: return publish(tmp_path, "one.json", value)["sha256"]
        except FileExistsError: return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, [b"first", b"second"]))
    assert sum(value is not None for value in results) == 1
    assert digest(read_bytes(tmp_path / "one.json")) in results


def test_source_observation_rejects_dirty_checkout(monkeypatch):
    def git(*args):
        if args[:2] == ("rev-parse", "--show-toplevel"): return str(provenance.SOURCE_ROOT).encode()
        if args[:2] == ("rev-parse", "HEAD"): return b"a" * 40
        return b" M changed.py\n"
    monkeypatch.setattr(provenance, "git", git)
    with pytest.raises(IntegrityError, match="RUN_DIRTY_SOURCE"): provenance.source_snapshot()


def test_source_observation_rejects_different_root(monkeypatch):
    monkeypatch.setattr(provenance, "git", lambda *a: b"/not-the-executing-package\n")
    with pytest.raises(IntegrityError, match="RUN_SOURCE"): provenance.source_snapshot()


@pytest.mark.parametrize("fault", ["post_pre", "post_scope", "metric", "environment"])
def test_consistency_rejects_rehashed_conflicting_records(inputs, observed, fault):
    launch(inputs); folder = inputs[2]
    manifest = json.loads((folder / "manifest.json").read_bytes())
    if fault in ("post_pre", "post_scope"):
        name = "audit-post.json"; value = json.loads((folder / name).read_bytes())
        value["pre_verdict" if fault == "post_pre" else "physical_result"] = "ACCEPTED"
        (folder / name).write_bytes(encode(value))
        manifest["mclf_post"]["report"]["sha256"] = digest((folder / name).read_bytes())
    elif fault == "metric": manifest["metrics"][0]["value"] += 1
    else:
        name = "environment.json"; value = json.loads((folder / name).read_bytes())
        value["installed"]["attrs"] = "unreviewed"
        (folder / name).write_bytes(encode(value))
        for ref in manifest["inputs"]:
            if ref["uri"] == name: ref["sha256"] = digest((folder / name).read_bytes())
    (folder / "manifest.json").write_bytes(encode(manifest))
    (folder / "manifest.sha256").write_text(digest((folder / "manifest.json").read_bytes()) + "\n")
    with pytest.raises(IntegrityError): check_run(folder)


def test_environment_observation_failure(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(provenance, "source_snapshot", dict)
    monkeypatch.setattr(provenance.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1))
    with pytest.raises(IntegrityError, match="RUN_ENVIRONMENT"): provenance.capture()


def test_git_observation_timeout_is_typed(monkeypatch):
    import subprocess
    def timeout(*args, **kwargs): raise subprocess.TimeoutExpired("git", 10)
    monkeypatch.setattr(provenance.subprocess, "run", timeout)
    with pytest.raises(IntegrityError, match="RUN_SOURCE"): provenance.git("status")


def test_cli_preallocation_interrupt_is_visible(inputs, monkeypatch, capsys):
    from aura.cli import main
    def interrupt(): raise KeyboardInterrupt()
    monkeypatch.setattr(provenance, "capture", interrupt)
    assert main(["run", str(inputs[0]), "--experiment", str(inputs[1]), "--output", str(inputs[2]),
                 "--no-randomness", "--json"]) == 130
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "RUN_INTERRUPTED"
    assert not inputs[2].exists()


def test_wrong_manifest_anchor_rejected(inputs, observed):
    launch(inputs)
    with pytest.raises(IntegrityError, match="HASH_MISMATCH"):
        check_run(inputs[2], expected_sha256="0" * 64)


def test_empty_directory_cannot_be_claimed_as_run(tmp_path):
    with pytest.raises(FileNotFoundError): check_run(tmp_path)


def test_b03_01_metrics_pass_for_integrity_checked_record(analytical_inputs, observed):
    from aura.analysis.ana07_metrics import TOLERANCE, analyze_b03_01

    scenario_path, experiment_path, output = analytical_inputs
    request_path = scenario_path.parent / "field-request.json"
    request = json.loads(request_path.read_bytes())
    request["coordinates_m"] = [[0, 0, 0]]
    request_bytes = encode(request)
    request_path.write_bytes(request_bytes)
    experiment = json.loads(experiment_path.read_bytes())
    experiment["protocol"]["sha256"] = digest(request_bytes)
    experiment_path.write_bytes(encode(experiment))

    execution = execute(scenario_path, experiment_path, output=output, seed=None)
    report = analyze_b03_01(output, expected_manifest_sha256=execution["manifest_sha256"])

    assert report["integrity"] == "VERIFIED"
    assert report["numerical_comparison"] == "PASS"
    assert report["physical_validation"] == "NOT_ESTABLISHED"
    assert report["tolerance_normalized"] == TOLERANCE
    assert report["metrics"]["pressure"]["E_max"] == pytest.approx(0, abs=1e-15)
    assert report["metrics"]["velocity"]["criterion"] == "PASS"
    assert report["mean_intensity_w_m2"] == pytest.approx([1 / 750_000, 0, 0])


def test_b03_01_reference_rejects_a_different_sample(analytical_inputs):
    from aura.analysis.ana07_metrics import _require_b03_01

    scenario = json.loads(analytical_inputs[0].read_bytes())
    request = {
        "contract": "FIELD-REQUEST-1.0",
        "case_id": "B03-01",
        "box_min_m": [-0.0015, -0.0015, -0.0015],
        "box_max_m": [0.0015, 0.0015, 0.0015],
        "coordinates_m": [[0.000375, 0, 0]],
    }
    with pytest.raises(ValueError, match="frozen only"):
        _require_b03_01(scenario, request)
