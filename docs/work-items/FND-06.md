# FND-06 — Configuration Validation Command

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Depends on:** FND-05

## Question and scope

Can a user inspect a complete scenario through the installed command, receive a readable or machine-readable explanation, and distinguish structural correctness from missing scientific evidence without invoking a solver?

Starting revision: `de87a375aedfd5e69a698fe6414fb2e4b3696588`. Authority: D00, D02, D03 FR-001/002/009 and D08; predecessor [FND-05](FND-05.md). Reuse schema 1.0 and L0-1.0 without changing physical equations, tolerances or accepted inputs. Preserve `aura status`; add `aura validate-config <path> [--json]` for scenario files only. No run, preflight, solver, hash-authentication or evidence-publication capability is introduced.

## Frozen interface and acceptance

- Accept the existing strict JSON/YAML/YML file formats. Require a Scenario record; reject other supported evidence/document types as `DOCUMENT_TYPE`. Do not auto-convert units or insert missing physical values.
- Read and validate the file, then invoke the real pre-stage evaluator and explicit acceptance gate. Keep `schema_status` distinct from the audit verdict. An ordinary valid fixture currently has VALID schema and INDETERMINATE audit.
- Exit codes: 0 for status/help or a future fully accepted configuration audit; 1 for invalid input/audit; 2 for command usage; 3 for ALERT/INDETERMINATE evidence; 4 for input filesystem failure. No current real configuration can reach audit ACCEPTED because scientific model coverage is unimplemented. Code 3 must not be described as a malformed configuration or a stop on unrelated foundation work.
- In JSON mode, emit exactly one versioned object to stdout for completed validation attempts, including failures: command, input path, schema status, verdict, nested audit or null, structured error or null, exit code, explicit scope and no-simulation flag. Human diagnostics go to stdout for code 0 and stderr for nonzero validation outcomes. Standard argparse help/usage remains text (including with `--json`).
- Use explicit local placeholder audit/run identifiers required by the existing report schema, labeled as configuration checks with no scientific run or reusable provenance. Do not manufacture an actual RunManifest or create output files.
- Preserve structured error codes/paths, escape untrusted text in human output and retain all audit findings. A parser failure stops before audit; no partial report is presented as a completed audit.

Expected outcomes are exact exit codes, statuses, named paths, parseable JSON, separate streams, unchanged input files and absent solver/run imports. Test valid/invalid/missing-file cases through subprocesses, both supported serialization formats and the 22 FND-05 fault classes. Unit checks cover filesystem errors, wrong document type, argument handling and typed audit gates. Test code-0/ALERT/INVALIDATED mappings with explicitly manufactured reports; these are branch checks, not actual capability evidence.

CPU-only software checks; no scientific experiment, allocation or solver run. Target the full suite below 30 seconds; investigate above 60 seconds. Use a fresh Python 3.12 virtual environment for installed-command checks outside the checkout, with core dependencies only. FND-08 still owns environment locking. Complete local Quality on final content, relative links, staged/identity review and exact remote CI before delivery.

## Results and decision

Delivered [CLI implementation](../../src/aura/cli.py), [CLI tests](../../tests/test_cli.py), [CLI-1.0 usage and output contract](../cli-usage.md), updated examples/README and [requirement mapping](../planning/09-requirement-traceability.md). The existing manufactured scenario is reused unchanged. No dependency, schema, equation or numerical tolerance changed.

1. The first focused suite passed **83 CLI tests**. Ruff reported three test-code issues: one import ordering issue and two missing explicit `check=False` arguments on subprocess calls. These were corrected. No test failure occurred in the recorded executions.
2. Review separated the human validation verdict from `Audit: NOT_RUN` when parsing fails, so rejected input cannot look like a completed audit. The existing malformed-input test now asserts both labels. Three additional human-output gate-branch checks brought CLI coverage to **86 cases** (85 new plus the original status check).
3. The complete suite passed **661 tests in approximately 11.6 seconds** on Linux/Python 3.12.14; Ruff passed. The 22 FND-05 faults fail with their specified codes/paths in JSON and YAML and do not reach the auditor. The real valid fixture remains schema VALID / audit INDETERMINATE / exit 3; no actual configuration was accepted as scientific evidence.
4. A new Python 3.12.14 virtual environment was created with `venv`, then installed with `python -m pip install /tmp/AURA-final` without development extras. After the final CLI wording change, the project wheel was rebuilt/reinstalled with `--no-deps` before checks. This was a noneditable install, with `aura.cli` loaded from site-packages; its source bytes matched the reviewed source. Neither pytest nor Ruff was installed in that environment.
5. From a separate temporary directory, the installed `aura` executable passed **18 validation checks**: valid/invalid/missing input × JSON/YAML/YML × human/JSON output. Actual return codes were 3/1/4 respectively; reports and streams were checked. `aura status` also passed. Tests use only manufactured input and no scientific runs. Temporary environment/test paths are local details, not evidence IDs or a portable environment lock.
6. File-preservation checks, a subprocess import guard against future field/force/dynamics/run/preflight modules, malformed parser inputs, escaping, usage errors, supported record-type rejection and typed gate branches passed. Fully ACCEPTED/ALERT/INVALIDATED audit branch tests use clearly synthetic reports; they do not establish current model coverage.

Artifact self-review: CLI behavior matches D08's visible-failure contract and D02's distinction between invalidity and missing evidence. JSON carries separate schema/audit states; no acceptance override or production runner was added. This is implementation review, not independent scientific validation. The complete local Quality workflow, links and exact-commit remote CI are delivery checks reported with the commit.

**FND-06 is DONE; FND-07 is READY.** Next: canonical serialization and verifiable content identity. P2 remains ACTIVE, with environment locking/review still owned by FND-08. The owner's requested explanation remains before RUN-01/P3 and the simulation system/core.
