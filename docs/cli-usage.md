# Command-Line Usage

**Interface:** CLI-1.1 · **Implemented by:** [FND-06](work-items/FND-06.md), [NUM-02](work-items/NUM-02.md)

The available commands are `status`, `validate-config`, air-series `preflight`, bounded software-diagnostic `run`/`check`, and analytical-run `reproduce`. The run commands are described in the [RUN lifecycle contract](research/run-lifecycle.md) and [examples](../examples/runs/README.md). The Hasegawa numerical field solver, physical simulation runs, general run-to-reference comparison and study-level evidence export remain planned. The configuration command reads a scenario and checks its declarations; it does not demonstrate that AURA works.

## Install and inspect

Use the [reviewed environment instructions](../requirements/README.md) for CPython 3.12.14 on Linux x86_64. They provide both the exact development installation and a smaller runtime installation from a locally built project wheel. After the development installation:

```bash
.venv/bin/aura status
.venv/bin/aura validate-config --help
```

Once installed, the `aura` executable works outside the checkout when passed an accessible configuration path. `python -m aura.cli` is an equivalent entry point under the same interpreter.

## Validate the manufactured example

```bash
.venv/bin/aura validate-config examples/schema/manufactured-scenario.json
.venv/bin/aura validate-config examples/schema/manufactured-scenario.json --json
```

The [example](../examples/schema/manufactured-scenario.json) contains manufactured water-like properties, a small sphere, declared sources, ideal zero gravity and a target. It is a software fixture, not measured water, a selected device, or a simulated physical result. Its values do not establish consistency of all material properties or model applicability. The [schema contract](research/schema-contract.md) defines every required field and supported geometry.

Both commands currently exit **3**. The file's structure is **VALID**, while the overall audit is **INDETERMINATE**: no reviewed scientific model capability is registered, and no authenticated run evidence was supplied. The report names those gaps. Code 3 is an unresolved acceptance gate; it does not mean the example's syntax is wrong, nor does it stop unrelated foundation work under DEC-003. There is no option to force scientific acceptance or silently omit these findings.

To inspect the expected result in a shell that uses `set -e`, capture the outcome explicitly:

```bash
validation_status=0
.venv/bin/aura validate-config examples/schema/manufactured-scenario.json --json || validation_status=$?
printf 'Validation exit code: %s\n' "$validation_status"
```

Keep the report and inspect `schema_status`, `verdict` and `error`; do not treat all nonzero codes as the same condition. No report file is written automatically. If redirecting output, use a separate destination and preserve the input file.

## Input behavior

- Accept one `.json`, `.yaml` or `.yml` file, through the existing bounded strict reader (1 MiB limit). The extension chooses the parser; content guessing is not supported.
- Require a complete version-1.0 Scenario, even though the underlying library also supports other record types. A valid Medium or RunManifest is not a scenario.
- Reject duplicate keys, unsupported versions, unknown fields, unsafe YAML constructs, nonfinite numbers, missing physics and invalid units/shapes/ranges according to the existing schema. Report the first reader failure and its path. The full L0 audit runs only after the reader accepts the scenario.
- Do not infer radius from diameter, convert units, normalize vectors, insert gravity or choose a model. Explicit conversion adapters remain separate library functions.
- Do not allocate solver resources, invoke a physical model, read external evidence artifacts, authenticate hashes, create a scientific run or modify the scenario. Higher audit levels and actual execution integration remain future work.

These checks cannot recognize every mislabeled physical value. The [B-01/B-02 report](benchmarks/B01-B02-foundation-verification.md) records the radius/diameter and peak/RMS coverage limits.

## Estimate an air-series workload

```bash
.venv/bin/aura preflight <scenario.json> --workload <air-workload.json> --output-dir <planned-run-directory> --json
```

The scenario supplies declared RAM, disk and wall-time caps. The workload is a strict `AIR-SERIES-WORKLOAD-1.1` JSON object with solver ID/version, number of gaps, points per gap, harmonic order, Gauss-Legendre quadrature order (1–512), maximum dimensionless Bessel argument, and point-chunk size (at most 256). The maximum argument bounds the Miller recurrence workspace. A calibration uses `AIR-SERIES-CALIBRATION-1.1` and must match both numerical dimensions as well as solver version, current clean source revision and ENV-1.0 environment digest. Input JSON is limited to 1 MiB, rejects duplicate keys and nonfinite values, and rejects unknown fields.

The report estimates retained harmonic-order vectors, Miller recurrence scratch, Gauss node/weight workspace, one streamed point chunk and its serialization, full requested output storage, and runtime from measured seconds per order at the matching quadrature and Bessel-argument dimensions plus the declared safety multiplier. It checks scenario limits and currently available Linux memory and free space at the planned output filesystem. `REJECTED` (exit 1) means a named budget was exceeded. `INDETERMINATE` (exit 3) means usable runtime calibration is missing, stale, or bound to another numerical dimension, so the run is not ready. `BUDGETS_WITHIN_CAPS` (exit 0) means only that the estimates fit the declared and observed resource limits for this exact calibration context. No outcome executes or authorizes a solver; `execution_authorized` is always false. Runtime remains INDETERMINATE until the numerical backend exists and can be calibrated. Estimates do not demonstrate field convergence, accuracy, force or experimental behavior. See [NUM-02](work-items/NUM-02.md) for the estimator basis and acceptance boundary.

## Replay a recorded analytical run

```bash
.venv/bin/aura reproduce results/<experiment-id>/<run-id> --json
```

The command verifies the original bundle and its recorded source/lock identities, checks out that exact source commit in a temporary detached worktree, creates a fresh ENV-1.0 virtual environment from the hash-pinned development lock, and runs the original experiment into a new immutable directory. The caller's dirty working-tree changes are not included. Runtime differences allowed by ENV-1.0 are listed in the report; the Python 3.12.14 Linux x86_64 dependency profile and lock hashes must match.

Replay currently admits completed analytical field runs only. It reports exact byte equality for coordinates, pressure, velocity and pressure-gradient arrays. ANA-07 metrics are compared for exact equality without a new tolerance. The independent ANA-REF-1.0 comparison keeps its own frozen tolerance. Missing reference cases remain INDETERMINATE. Replay reports do not change the parent or child run's scientific verdict and do not establish physical validation.

By default, the replay bundle and report directory are written under ignored results storage. Use --output and --report-dir to select unused paths. The report directory contains replay-report.json, replay-report.md and artifact-index.json. Do not commit generated runs or reports.

## Exit and stream contract

| Exit | Meaning | Example |
|---|---|---|
| 0 | Status/help completed, all required configuration audit checks accepted, or an exact replay and all applicable reproducibility comparisons passed | `aura status`; actual configuration ACCEPTED is unavailable in L0-1.0; a reproduced analytical run still has scientific verdict INDETERMINATE |
| 1 | Invalid input, failed run integrity/replay, or INVALIDATED audit | Changed parent bundle, unsupported profile or non-identical field arrays |
| 2 | Incorrect command usage | Missing path, unknown command/option |
| 3 | ALERT or INDETERMINATE audit, verified run with unresolved science, or replay without an admitted reference | Current manufactured scenario or a replay whose field arrays match but whose reference comparison is unavailable |
| 4 | Input filesystem failure; no scientific verdict | Missing file, permissions or other read failure |

Human validation output uses stdout for code 0 and stderr for nonzero outcomes. It includes schema status, validation verdict, whether the audit ran, diagnostics, per-rule findings and scope. Paths/messages are escaped to avoid interpreting embedded control characters as terminal instructions. `status` and help use stdout; usage errors use stderr.

For a parsed `validate-config ... --json` command, every expected validation or input-I/O outcome emits one JSON object to stdout and leaves stderr empty. **Argument errors and help retain argparse's plain text behavior**, including when `--json` appears. Scripts should check exit 2 before attempting to parse a validation report. Unexpected internal exceptions are not reclassified as successful or accepted input.

## JSON envelope

| Key | Meaning |
|---|---|
| `cli_schema_version` | `1.0`; separate from scenario and audit registry versions |
| `command`, `input` | `validate-config` and the supplied path, without rewriting it |
| `schema_status` | `VALID`, `INVALID`, or `NOT_CHECKED` for input-I/O failure |
| `verdict` | Command's validation verdict; invalid input is INVALIDATED; null if the file could not be inspected |
| `audit` | Full existing L0 report envelope, or null when schema/input validation prevented an audit |
| `error` | `{code, path, message}` or null; `path` is a JSON Pointer, with empty string for a document/file-level failure |
| `exit_code` | Same integer as the process return code |
| `simulation_executed` | Always false for this command |
| `scope` | Explicit limits, including placeholder audit identity |

The report's `CONFIG-CHECK-AUDIT` and `CONFIG-CHECK-NO-RUN` identifiers are local placeholders required by the existing L0 schema. They are not immutable run IDs, evidence provenance, or a substitute for a future RunManifest. Every invocation currently uses the same placeholders; do not use them to combine scientific evidence.

Schema errors retain their stable library codes (for example `SCHEMA_VERSION`, `UNIT_MISMATCH`, `SCHEMA_INVALID`). Required gate failures use `MCLF_INVALIDATED`, `MCLF_ALERT` or `MCLF_INDETERMINATE`. I/O failures use `FILE_NOT_FOUND`, `PERMISSION_DENIED` or `INPUT_IO`; their message text can vary by operating system. Argument-error prose and human report wording are not a machine API.

## Verification and next steps

[CLI tests](../tests/test_cli.py) cover the 22 known input-fault classes in JSON/YAML, explicit zero/missing fields through the established fixtures, independent output assertions, separate streams, subprocess exit codes, file preservation, parser/file failures and forbidden simulation imports. FND-06 also records an installation into a fresh Python 3.12 environment without development extras, exercised outside the repository.

[FND-07](work-items/FND-07.md) supplies separate canonical identity and bounded file-integrity library helpers. This configuration command does not call those file-verification APIs or authenticate run evidence. [FND-08](work-items/FND-08.md) delivers the reproducible environment and [P2 exit review](reviews/P2-foundation-exit.md). The owner received the requested plain-language system/core explanation at the P2 exit. RUN-01 implements the diagnostic recorder; analytical fields remain the next phase.
