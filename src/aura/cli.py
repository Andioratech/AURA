"""Command-line entry point for the AURA research scaffold."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def _load_preflight_json(path: str) -> tuple[dict, str]:
    from aura.errors import InvalidInputError

    if "\x00" in path:
        raise InvalidInputError("INPUT_PATH", "", "Input path contains a null character.")
    with Path(path).open("rb") as stream:
        data = stream.read(1024 * 1024 + 1)
    if len(data) > 1024 * 1024:
        raise InvalidInputError("INPUT_LIMIT", "", "Preflight JSON exceeds the 1 MiB limit.")

    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InvalidInputError("DUPLICATE_KEY", f"/{key}", "Duplicate JSON key.")
            result[key] = value
        return result

    def reject_constant(value):
        raise InvalidInputError("NONFINITE_JSON", "", f"Non-finite JSON value {value} is not allowed.")

    try:
        record = json.loads(data, object_pairs_hook=object_pairs, parse_constant=reject_constant)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise InvalidInputError("INPUT_JSON", "", "Preflight input must be valid UTF-8 JSON.") from exc
    if type(record) is not dict:
        raise InvalidInputError("INPUT_JSON", "", "Preflight JSON root must be an object.")
    return record, hashlib.sha256(data).hexdigest()


def _preflight(args) -> int:
    from aura.errors import IncompleteEvidenceError, InvalidInputError
    from aura.preflight import estimate_air_series
    from aura.schema import Scenario, load_document

    try:
        if "\x00" in args.scenario:
            raise InvalidInputError("INPUT_PATH", "", "Input path contains a null character.")
        scenario = load_document(args.scenario)
        if not isinstance(scenario, Scenario):
            raise InvalidInputError("DOCUMENT_TYPE", "/document_type", "Expected a scenario.")
        workload, _ = _load_preflight_json(args.workload)
        calibration = None
        calibration_sha256 = None
        current_source_revision = None
        current_environment_sha256 = None
        if args.calibration is not None:
            calibration, calibration_sha256 = _load_preflight_json(args.calibration)
            from aura.runs.manifest import digest, encode
            from aura.runs.provenance import capture

            source, environment, _ = capture()
            current_source_revision = source["revision"]
            current_environment_sha256 = digest(encode(environment))
        report = estimate_air_series(
            scenario.to_dict(), workload, calibration,
            calibration_sha256=calibration_sha256,
            output_dir=args.output_dir,
            current_source_revision=current_source_revision,
            current_environment_sha256=current_environment_sha256,
        )
    except IncompleteEvidenceError as exc:
        report = {"status": "INDETERMINATE", "reason": exc.code, "error": exc.as_dict(), "exit_code": 3}
    except InvalidInputError as exc:
        report = {"status": "INVALID", "reason": exc.code, "error": exc.as_dict(), "exit_code": 1}
    except FileNotFoundError as exc:
        report = {
            "status": "INVALID", "reason": "FILE_NOT_FOUND",
            "error": {"code": "FILE_NOT_FOUND", "path": "", "message": str(exc)},
            "exit_code": 4,
        }
    except OSError as exc:
        report = {
            "status": "INVALID", "reason": "INPUT_IO",
            "error": {"code": "INPUT_IO", "path": "", "message": str(exc)},
            "exit_code": 4,
        }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))
    else:
        status = report["status"]
        lines = [f"Preflight: {status}"]
        if "estimates" in report:
            lines.append("Estimates: " + json.dumps(report["estimates"], sort_keys=True))
            lines.append("Limits: " + json.dumps(report["limits"], sort_keys=True))
        if report.get("reason"):
            lines.append(f"Reason: {report['reason']}")
        if report.get("error"):
            lines.append(json.dumps(report["error"], ensure_ascii=True))
        lines.append("No numerical field solver was imported or executed.")
        print("\n".join(lines), file=sys.stdout if report["exit_code"] == 0 else sys.stderr)
    return report["exit_code"]


def _validate_config(path: str) -> tuple[dict, str]:
    # Keep status/help independent of schema and scientific-model imports.
    from aura.errors import IncompleteEvidenceError, InvalidInputError, MclfInvalidationError
    from aura.mclf import evaluate_scenario
    from aura.schema import Scenario, load_document

    output = {
        "cli_schema_version": "1.0",
        "command": "validate-config",
        "input": path,
        "schema_status": "NOT_CHECKED",
        "verdict": None,
        "audit": None,
        "error": None,
        "exit_code": 0,
        "simulation_executed": False,
        "scope": (
            "Configuration checks only; no simulation, content-hash authentication or "
            "experimental validation. Audit IDs are local placeholders, not run provenance."
        ),
    }
    try:
        if "\x00" in path:
            raise InvalidInputError("INPUT_PATH", "", "Input path contains a null character.")
        record = load_document(path)
        if not isinstance(record, Scenario):
            raise InvalidInputError("DOCUMENT_TYPE", "/document_type", "Expected a scenario.")
    except InvalidInputError as exc:
        output.update(
            schema_status="INVALID", verdict="INVALIDATED", error=exc.as_dict(), exit_code=1
        )
        return output, ""
    except OSError as exc:
        code = (
            "FILE_NOT_FOUND" if isinstance(exc, FileNotFoundError)
            else "PERMISSION_DENIED" if isinstance(exc, PermissionError)
            else "INPUT_IO"
        )
        output.update(error={"code": code, "path": "", "message": str(exc)}, exit_code=4)
        return output, ""

    output["schema_status"] = "VALID"
    report = evaluate_scenario(
        record.to_dict(),
        report_id="CONFIG-CHECK-AUDIT",
        run_id="CONFIG-CHECK-NO-RUN",
        stage="pre",
    )
    output.update(verdict=report.verdict, audit=report.to_dict())
    try:
        report.require_accepted()
    except MclfInvalidationError as exc:
        output.update(error=exc.as_dict(), exit_code=1)
    except IncompleteEvidenceError as exc:
        output.update(error=exc.as_dict(), exit_code=3)
    return output, report.to_text()


def _emit_validation(output: dict, report_text: str, *, machine: bool) -> int:
    code = output["exit_code"]
    if machine:
        print(json.dumps(output, indent=2, ensure_ascii=True, allow_nan=False))
    else:
        lines = [
            f"Configuration: {json.dumps(output['input'])}",
            f"Schema: {output['schema_status']}",
            f"Validation: {output['verdict'] or 'NOT_CHECKED'}",
            f"Audit: {output['verdict'] if output['audit'] is not None else 'NOT_RUN'}",
        ]
        if output["schema_status"] == "VALID" and code == 3:
            lines.append("Input structure is valid; scientific acceptance remains unresolved.")
        if output["error"] is not None:
            error = output["error"]
            lines.append(
                f"{error['code']} at {json.dumps(error['path'])}: {json.dumps(error['message'])}"
            )
        if report_text:
            lines.append(report_text.rstrip())
        lines.extend([output["scope"], f"Exit code: {code}"])
        print("\n".join(lines), file=sys.stdout if code == 0 else sys.stderr)
    return code


def _lifecycle(args):
    import signal
    import threading

    from aura.errors import IncompleteEvidenceError, InvalidInputError
    from aura.runs import check_run, execute, reproduce

    class Terminated(KeyboardInterrupt):
        signal_number = signal.SIGTERM

    def terminate(signum, frame):
        raise Terminated("Termination requested")

    try:
        if args.command == "run":
            previous = None
            if threading.current_thread() is threading.main_thread():
                previous = signal.signal(signal.SIGTERM, terminate)
            try:
                output = execute(
                    args.path, args.experiment, output=args.output, seed=args.seed,
                    calibration=getattr(args, "calibration", None),
                )
            finally:
                if previous is not None:
                    signal.signal(signal.SIGTERM, previous)
        elif args.command == "check":
            output = check_run(args.path, expected_sha256=args.sha256)
        else:
            output = reproduce(args.path, output=args.output, report_dir=args.report_dir)
    except KeyboardInterrupt as exc:
        output = {"command": args.command, "error": {"code": "RUN_INTERRUPTED",
                  "message": "Interrupted before terminal publication; preserve any partial directory."},
                  "exit_code": 128 + getattr(exc, "signal_number", 2)}
    except IncompleteEvidenceError as exc:
        output = {"command": args.command, "error": exc.as_dict(), "exit_code": 3}
    except InvalidInputError as exc:
        output = {"command": args.command, "error": exc.as_dict(), "exit_code": 1}
    except OSError as exc:
        output = {"command": args.command, "error": {"code": "RUN_IO", "message": str(exc)},
                  "exit_code": 4}
    except (ValueError, KeyError, TypeError) as exc:
        if args.command not in ("check", "reproduce"):
            raise
        code = "RUN_RECORD" if args.command == "check" else "RUN_REPLAY_RECORD"
        output = {"command": args.command, "error": {"code": code, "message": str(exc)},
                  "exit_code": 1}
    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=True, allow_nan=False))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=True, allow_nan=False),
              file=sys.stdout if output["exit_code"] == 0 else sys.stderr)
    return output["exit_code"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aura", description="AURA scientific project tools")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="report implemented capabilities and limits")
    validation = commands.add_parser(
        "validate-config", help="inspect a scenario without running a simulation",
        description="Check scenario structure and L0 declarations; not physical validation.",
        allow_abbrev=False,
    )
    validation.add_argument("path", help="scenario file with .json, .yaml or .yml extension")
    validation.add_argument("--json", action="store_true", help="emit a JSON validation report")
    preflight = commands.add_parser(
        "preflight", help="estimate an air-series workload before solver allocation",
        allow_abbrev=False,
    )
    preflight.add_argument("scenario", help="validated scenario containing resource caps")
    preflight.add_argument("--workload", required=True, help="AIR-SERIES-WORKLOAD-1.1 JSON")
    preflight.add_argument("--calibration", help="matching AIR-SERIES-CALIBRATION-1.1 JSON")
    preflight.add_argument("--output-dir", help="existing directory planned for run artifacts")
    preflight.add_argument("--json", action="store_true", help="emit a structured estimate")
    run = commands.add_parser("run", help="record a bounded software diagnostic", allow_abbrev=False)
    run.add_argument("path", help="diagnostic scenario JSON/YAML")
    run.add_argument("--experiment", required=True, help="frozen experiment JSON/YAML")
    run.add_argument("--output", help="new directory; default results/<experiment>/<run-id>")
    run.add_argument("--calibration", help="exact-revision ENV-1.0 AIR-SERIES-CALIBRATION-1.1 JSON")
    seeds = run.add_mutually_exclusive_group(required=True)
    seeds.add_argument("--seed", type=int, help="explicit seed (unused by current diagnostics)")
    seeds.add_argument("--no-randomness", action="store_true", help="explicitly record a null seed")
    run.add_argument("--json", action="store_true", help="emit a structured execution result")
    check = commands.add_parser("check", help="inspect recorded bundle integrity", allow_abbrev=False)
    check.add_argument("path", help="recorded run directory")
    check.add_argument("--sha256", help="separately retained final manifest digest")
    check.add_argument("--json", action="store_true", help="emit a structured check result")
    replay = commands.add_parser(
        "reproduce", help="replay a verified analytical run in its recorded environment",
        allow_abbrev=False,
    )
    replay.add_argument("path", help="completed, verified run directory")
    replay.add_argument("--output", help="new run directory; default results/replays/<run-id>/<uuid>")
    replay.add_argument("--report-dir", help="new report directory; default adjacent to replay output")
    replay.add_argument("--json", action="store_true", help="emit a structured replay report")
    args = parser.parse_args(argv)
    if args.command == "preflight":
        return _preflight(args)
    if args.command in ("run", "check", "reproduce"):
        return _lifecycle(args)
    if args.command == "status":
        print(
            "AURA: single-wave and coherent two-wave kernels are available through Python; recorded runs remain "
            "software diagnostics. Air-series preflight estimates budgets only; no numerical solver is available. "
            "Physical validation is pending."
        )
        print("Available: strict scenario schemas, SI helpers, L0 audits, validate-config and air-series preflight.")
        print("Available: run/check for immutable software diagnostics; scientific verdicts remain unresolved.")
        return 0
    output, report_text = _validate_config(args.path)
    return _emit_validation(output, report_text, machine=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
