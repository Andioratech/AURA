"""CLI output contracts and installed-module checks; no scientific solver runs."""

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from aura.cli import main

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "examples/schema/manufactured-scenario.json"
CASES = json.loads((ROOT / "tests/fixtures/foundation/rejections.json").read_text())["cases"]


def test_status_command(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["aura", "status"])
    assert main() == 0
    assert "solvers are not implemented yet" in capsys.readouterr().out


@pytest.fixture
def scenario():
    return json.loads(SCENARIO.read_text())


def write_input(tmp_path, data, format):
    path = tmp_path / ("scenario." + format)
    path.write_text(json.dumps(data) if format == "json" else yaml.safe_dump(data))
    return path


@pytest.mark.parametrize("format", ["json", "yaml", "yml"])
@pytest.mark.parametrize("machine", [False, True])
def test_valid_structure_retains_unknown_model(scenario, tmp_path, capsys, format, machine):
    path = write_input(tmp_path, scenario, format)
    original = path.read_bytes()
    files = set(tmp_path.iterdir())
    assert main(["validate-config", str(path), *(["--json"] if machine else [])]) == 3
    captured = capsys.readouterr()
    if machine:
        assert captured.err == ""
        output = json.loads(captured.out)
        assert output["cli_schema_version"] == "1.0"
        assert output["command"] == "validate-config"
        assert output["schema_status"] == "VALID"
        assert output["verdict"] == "INDETERMINATE"
        assert output["error"]["code"] == "MCLF_INDETERMINATE"
        assert output["exit_code"] == 3
        assert output["simulation_executed"] is False
        assert output["audit"]["report"]["run_id"] == "CONFIG-CHECK-NO-RUN"
        assert len(output["audit"]["report"]["checks"]) == 10
        assert "MODEL_UNCOVERED" in captured.out
    else:
        assert captured.out == ""
        assert "Schema: VALID" in captured.err
        assert "Audit: INDETERMINATE" in captured.err
        assert "Input structure is valid; scientific acceptance remains unresolved." in captured.err
        assert "MODEL_UNCOVERED" in captured.err
        assert "Exit code: 3" in captured.err
    assert path.read_bytes() == original
    assert set(tmp_path.iterdir()) == files


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
@pytest.mark.parametrize("format", ["json", "yaml"])
def test_fault_matrix_visible_to_scripts_before_audit(scenario, tmp_path, capsys, monkeypatch, case, format):
    import aura.mclf

    def forbidden(*args, **kwargs):
        pytest.fail("Malformed input reached the audit")

    monkeypatch.setattr(aura.mclf, "evaluate_scenario", forbidden)
    data = deepcopy(scenario)
    parts = case["path"].strip("/").split("/")
    parent = data
    for key in parts[:-1]:
        parent = parent[int(key)] if isinstance(parent, list) else parent[key]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    if case.get("operation") == "remove":
        del parent[key]
    else:
        parent[key] = case["value"]
    path = write_input(tmp_path, data, format)
    assert main(["validate-config", str(path), "--json"]) == 1
    captured = capsys.readouterr()
    assert captured.err == ""
    output = json.loads(captured.out)
    assert (output["error"]["code"], output["error"]["path"]) == (
        case["reader_code"], case.get("diagnostic_path", case["path"])
    )
    assert output["schema_status"] == "INVALID"
    assert output["verdict"] == "INVALIDATED"
    assert output["audit"] is None
    assert output["exit_code"] == 1


@pytest.mark.parametrize("machine", [False, True])
def test_missing_file_is_io_failure(tmp_path, capsys, machine):
    path = tmp_path / "absent.json"
    assert main(["validate-config", str(path), *(["--json"] if machine else [])]) == 4
    captured = capsys.readouterr()
    if machine:
        output = json.loads(captured.out)
        assert captured.err == ""
        assert output["error"]["code"] == "FILE_NOT_FOUND"
        assert output["schema_status"] == "NOT_CHECKED"
        assert output["verdict"] is None
        assert output["audit"] is None
        assert output["exit_code"] == 4
    else:
        assert captured.out == ""
        assert "FILE_NOT_FOUND" in captured.err
        assert "Audit: NOT_RUN" in captured.err


@pytest.mark.parametrize(
    "failure,code", [(PermissionError("denied"), "PERMISSION_DENIED"), (OSError("disk"), "INPUT_IO")]
)
def test_filesystem_errors_are_structured(monkeypatch, capsys, failure, code):
    import aura.schema

    def fail(path):
        raise failure

    monkeypatch.setattr(aura.schema, "load_document", fail)
    assert main(["validate-config", "file.json", "--json"]) == 4
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out)["error"]["code"] == code


def test_other_valid_document_type_is_not_a_scenario(scenario, tmp_path, capsys):
    data = {"document_type": "medium", "schema_version": "1.0", **scenario["medium"]}
    path = write_input(tmp_path, data, "json")
    assert main(["validate-config", str(path), "--json"]) == 1
    output = json.loads(capsys.readouterr().out)
    assert (output["error"]["code"], output["error"]["path"]) == ("DOCUMENT_TYPE", "/document_type")
    assert output["audit"] is None


@pytest.mark.parametrize(
    "suffix,payload,code",
    [
        ("json", b'{"x":1,"x":2}', "DUPLICATE_KEY"),
        ("json", b'{"x":NaN}', "NONFINITE"),
        ("json", b'{', "PARSE_ERROR"),
        ("json", b'\xff', "PARSE_ERROR"),
        ("yaml", b'!!python/object/apply:builtins.str ["unsafe"]', "PARSE_ERROR"),
        ("txt", b'{}', "FORMAT"),
        ("json", b' ' * (1024 * 1024 + 1), "INPUT_LIMIT"),
    ],
)
def test_parser_errors_are_json_not_success(tmp_path, capsys, suffix, payload, code):
    path = tmp_path / ("bad." + suffix)
    path.write_bytes(payload)
    assert main(["validate-config", str(path), "--json"]) == 1
    captured = capsys.readouterr()
    assert captured.err == ""
    output = json.loads(captured.out)
    assert output["error"]["code"] == code
    assert output["audit"] is None


def test_human_output_escapes_untrusted_control_characters(tmp_path, capsys):
    path = tmp_path / "bad\x1b[31m\n.json"
    path.write_text('{"bad\\u001b[31m\\n": 1, "bad\\u001b[31m\\n": 2}')
    assert main(["validate-config", str(path)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "\x1b" not in captured.err
    assert "\\u001b" in captured.err
    assert "DUPLICATE_KEY" in captured.err
    assert "Validation: INVALIDATED" in captured.err
    assert "Audit: NOT_RUN" in captured.err


def test_null_path_is_structured_for_programmatic_callers(capsys):
    assert main(["validate-config", "bad\x00.json", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "INPUT_PATH"


@pytest.mark.parametrize(
    "args",
    [[], ["run"], ["validate-config"], ["validate-config", "x.json", "--unknown", "--json"],
     ["status", "extra"], ["validate-config", "x.json", "--js"]],
)
def test_usage_errors_remain_text_and_exit_two(args, capsys):
    with pytest.raises(SystemExit) as caught:
        main(args)
    assert caught.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "usage:" in captured.err


@pytest.mark.parametrize("args", [["--help"], ["validate-config", "--help"]])
def test_help_exits_zero(args, capsys):
    with pytest.raises(SystemExit) as caught:
        main(args)
    assert caught.value.code == 0
    captured = capsys.readouterr()
    assert "usage:" in captured.out
    assert captured.err == ""


@pytest.mark.parametrize("verdict,code", [("ACCEPTED", 0), ("ALERT", 3), ("INVALIDATED", 1)])
@pytest.mark.parametrize("machine", [False, True])
def test_declared_audit_branches_map_to_exit_codes(monkeypatch, capsys, verdict, code, machine):
    # Synthetic reports check CLI branching only; real audits cannot be ACCEPTED yet.
    import aura.mclf
    from aura.mclf import RULES, AuditReport, Check, Finding

    report = AuditReport(
        "EXAMPLE-CLI-TEST", "EXAMPLE-CLI-NO-RUN", "pre",
        tuple(Check(rule.id, (Finding(verdict, "FIXTURE", "", "Test only"),)) for rule in RULES),
    )
    monkeypatch.setattr(aura.mclf, "evaluate_scenario", lambda *args, **kwargs: report)
    assert main(["validate-config", str(SCENARIO), *(["--json"] if machine else [])]) == code
    captured = capsys.readouterr()
    if machine:
        assert captured.err == ""
        output = json.loads(captured.out)
        assert output["schema_status"] == "VALID"
        assert output["verdict"] == verdict
        assert output["exit_code"] == code
        assert (output["error"] is None) == (code == 0)
    else:
        text = captured.out if code == 0 else captured.err
        assert (captured.err if code == 0 else captured.out) == ""
        assert "Schema: VALID" in text
        assert f"Audit: {verdict}" in text


@pytest.mark.parametrize("case,expected", [("valid", 3), ("invalid", 1), ("missing", 4)])
@pytest.mark.parametrize("machine", [False, True])
def test_module_command_from_another_directory(scenario, tmp_path, case, expected, machine):
    if case == "invalid":
        del scenario["gravity"]
    path = tmp_path / "missing.json" if case == "missing" else write_input(tmp_path, scenario, "json")
    result = subprocess.run(
        [sys.executable, "-m", "aura.cli", "validate-config", str(path), *(["--json"] if machine else [])],
        cwd=tmp_path, capture_output=True, text=True, timeout=15, check=False,
    )
    assert result.returncode == expected
    if machine:
        assert json.loads(result.stdout)["exit_code"] == expected
        assert result.stderr == ""
    else:
        assert result.stdout == ""
        assert f"Exit code: {expected}" in result.stderr


def test_validation_never_imports_future_solver_or_run_modules(tmp_path):
    script = """
import importlib.abc
import sys
class RejectSimulationImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(('aura.fields', 'aura.forces', 'aura.dynamics', 'aura.runs', 'aura.preflight')):
            raise AssertionError('Simulation import during validation: ' + fullname)
sys.meta_path.insert(0, RejectSimulationImports())
from aura.cli import main
raise SystemExit(main(['validate-config', sys.argv[1], '--json']))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(SCENARIO)],
        cwd=tmp_path, capture_output=True, text=True, timeout=15, check=False,
    )
    assert result.returncode == 3, result.stderr
    assert json.loads(result.stdout)["simulation_executed"] is False
