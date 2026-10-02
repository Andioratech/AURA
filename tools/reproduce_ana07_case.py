"""Replay one frozen ANA-07 run and compare its stored field components byte for byte."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from aura.analysis.ana07_metrics import analyze_recorded_case
from aura.runs import check_run, execute, provenance
from aura.runs.manifest import decode, digest

ROOT = Path(__file__).resolve().parents[1]
FIELD_ARTIFACTS = (
    "field-coordinates.json",
    "field-pressure.json",
    "field-velocity.json",
    "field-pressure-gradient.json",
)


def _source_identity() -> dict:
    return provenance.source_snapshot()


def _require_clean_checkout() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    if status.strip():
        raise RuntimeError("Reproduction requires a clean source checkout")


def _manifest(folder: Path) -> dict:
    return decode((folder / "manifest.json").read_bytes())


def reproduce(original_folder, campaign_index_path, output_folder) -> dict:
    original = Path(original_folder)
    campaign_index_path = Path(campaign_index_path)
    output = Path(output_folder)
    _require_clean_checkout()
    if output.exists():
        raise FileExistsError(f"Refusing to replace an existing reproduction: {output}")
    original_check = check_run(original)
    if original_check["integrity"] != "VERIFIED" or original_check["execution_status"] != "completed":
        raise ValueError("The original run must be completed and integrity verified")
    original_manifest = _manifest(original)
    index_raw = campaign_index_path.read_bytes()
    index_sha256 = digest(index_raw)
    if index_sha256 != Path(str(campaign_index_path) + ".sha256").read_text().strip():
        raise ValueError("Campaign index checksum differs from its sidecar")
    campaign_index = decode(index_raw)
    original_source = decode((original / "source.json").read_bytes())
    current_source = _source_identity()
    if original_source["dirty"] or current_source["dirty"] or (
        original_source["package_files_sha256"] != current_source["package_files_sha256"]
    ):
        raise ValueError("Application source files differ from the original run")

    original_metrics = analyze_recorded_case(
        original, expected_manifest_sha256=original_check["manifest_sha256"]
    )
    indexed_cases = [
        item for item in campaign_index["case_outcomes"]
        if item["case_id"] == original_metrics["case_id"]
        and item["run_id"] == original_check["run_id"]
        and item["manifest_sha256"] == original_check["manifest_sha256"]
    ]
    if len(indexed_cases) != 1:
        raise ValueError("Original run does not match exactly one outcome in the campaign index")
    source_report_ref = indexed_cases[0]
    source_report_path = campaign_index_path.parent / "reports" / (
        original_metrics["case_id"] + ".json"
    )
    source_report_raw = source_report_path.read_bytes()
    source_report_sha256 = digest(source_report_raw)
    if source_report_sha256 != source_report_ref["report_sha256"] or (
        source_report_sha256 != Path(str(source_report_path) + ".sha256").read_text().strip()
    ):
        raise ValueError("Frozen comparison report differs from the indexed report digest")
    indexed_metrics = decode(source_report_raw)
    if indexed_metrics["metrics"] != original_metrics["metrics"] or (
        indexed_metrics["reference_sources"] != original_metrics["reference_sources"]
    ):
        raise ValueError("Original analysis no longer matches its frozen report or references")
    output.mkdir(parents=True)
    replay = execute(
        original / "scenario.json",
        original / "experiment.json",
        output=output / "bundle",
        seed=None,
    )
    replay_check = check_run(output / "bundle", expected_sha256=replay.get("manifest_sha256"))
    if replay["execution_status"] != "completed" or replay_check["integrity"] != "VERIFIED":
        raise RuntimeError("Replay did not complete with verified bundle integrity")
    replay_manifest = _manifest(output / "bundle")
    replay_metrics = analyze_recorded_case(
        output / "bundle", expected_manifest_sha256=replay["manifest_sha256"]
    )

    input_names = ("scenario.json", "experiment.json", "field-request.json")
    input_hashes = {}
    for name in input_names:
        first = digest((original / name).read_bytes())
        second = digest((output / "bundle" / name).read_bytes())
        input_hashes[name] = {"original": first, "replay": second, "identical": first == second}
    field_hashes = {}
    for name in FIELD_ARTIFACTS:
        first = next(ref["sha256"] for ref in original_manifest["outputs"] if ref["uri"] == name)
        second = next(ref["sha256"] for ref in replay_manifest["outputs"] if ref["uri"] == name)
        field_hashes[name] = {"original": first, "replay": second, "identical": first == second}
    metrics_identical = original_metrics["metrics"] == replay_metrics["metrics"]
    fields_identical = all(item["identical"] for item in field_hashes.values())
    inputs_identical = all(item["identical"] for item in input_hashes.values())
    report = {
        "contract": "ANA-07-REPRODUCTION-1.0",
        "protocol": "ANA-REF-1.0",
        "case_id": original_metrics["case_id"],
        "sample_count": original_metrics["sample_count"],
        "original_run_id": original_check["run_id"],
        "replay_run_id": replay_check["run_id"],
        "original_revision": original_source["revision"],
        "replay_revision": current_source["revision"],
        "application_source_identical": True,
        "original_manifest_sha256": original_check["manifest_sha256"],
        "replay_manifest_sha256": replay_check["manifest_sha256"],
        "campaign_index_sha256": index_sha256,
        "original_metrics_report_sha256": source_report_sha256,
        "inputs": input_hashes,
        "field_artifacts": field_hashes,
        "numerical_metrics_identical": metrics_identical,
        "original_metrics": original_metrics["metrics"],
        "replay_metrics": replay_metrics["metrics"],
        "reproduction": "PASS" if inputs_identical and fields_identical and metrics_identical else "FAIL",
        "physical_validation": "NOT_ESTABLISHED",
        "limitations": [
            "Reproduction checks deterministic analytic plane or outgoing spherical-field software and frozen inputs only.",
            "No measured water, physical radiator, body coupling, force, motion or microgravity result.",
        ],
    }
    raw = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    (output / "reproduction.json").write_bytes(raw)
    (output / "reproduction.json.sha256").write_text(digest(raw) + "\n", encoding="ascii")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_folder", type=Path, help="Original completed run bundle")
    parser.add_argument("campaign_index", type=Path, help="Frozen campaign index anchoring the original report")
    parser.add_argument("output_folder", type=Path, help="New local reproduction folder")
    args = parser.parse_args(argv)
    report = reproduce(args.original_folder, args.campaign_index, args.output_folder)
    print(json.dumps({
        "case_id": report["case_id"],
        "original_run_id": report["original_run_id"],
        "replay_run_id": report["replay_run_id"],
        "reproduction": report["reproduction"],
        "physical_validation": report["physical_validation"],
        "report_path": str(args.output_folder / "reproduction.json"),
    }, sort_keys=True))
    return 0 if report["reproduction"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
