"""Command-line entry point for the AURA research scaffold."""

from __future__ import annotations

import argparse
import json
import sys


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
    args = parser.parse_args(argv)
    if args.command == "status":
        print("AURA scaffold initialized; scientific solvers are not implemented yet.")
        print("Available: strict scenario schemas, SI helpers, L0 audits and validate-config.")
        print("Model coverage, authenticated run artifacts and simulation commands remain unavailable.")
        return 0
    output, report_text = _validate_config(args.path)
    return _emit_validation(output, report_text, machine=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
