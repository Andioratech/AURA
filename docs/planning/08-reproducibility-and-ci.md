# 08 — Run Lifecycle, Reproducibility and Delivery

## Orthogonal states

A task state is READY/ACTIVE/REVIEW/DONE/BLOCKED. A run execution state is planned/running/completed/failed/aborted. MCLF reports ACCEPTED/ALERT/INVALIDATED/INDETERMINATE. A benchmark comparison reports PASS/FAIL/INDETERMINATE with its own scope. A phase gate reports PASS/FAIL/HOLD/INDETERMINATE. A D09 claim has its specified scientific state. Store these in separate fields; execution completion and green CI do not imply scientific validation.

## RUN-01 — Minimal immutable execution lifecycle

**Current state:** DONE — [implementation](../work-items/RUN-01.md), [artifact review](../reviews/RUN-01-lifecycle.md). The recorder supports the frozen software diagnostics; analytical adapter contracts/model admission follow ANA-01 and the owning P3 cards.

**Depends on:** FND-08 and P2 gate. **Complete before:** ANA-01 evidence runs.

1. Implement `runs/manifest.py` and `runs/execute.py` using the FND schemas and canonical input hashes.
2. Assign experiment IDs only to actual frozen protocols; create a new run ID before execution. Reject an existing output directory.
3. Record UTC start, source commit/dirty state, environment snapshot, platform/precision, input hashes, seeds, resource caps and expected outputs.
4. Validate and estimate the small analytical workload before allocation. Write a running manifest atomically; preserve failures and partial artifacts.
5. Finalize with execution state, errors, metrics, checks, hashes and log references; a result must not write over its inputs.
6. Expose minimal `run`, `check` and status capabilities; document exactly which are implemented.

**Artifacts:** manifest/lifecycle code; CLI tests for valid run, invalid scenario, deliberate solver exception, interruption recovery policy and existing-directory rejection; small synthetic example; D07 field mapping.

**Accept:** a deliberately failed run leaves an identifiable failure record; a successful run has verifiable input/output hashes and no missing identity fields. **Failure:** F-01/F-05/F-09; repair lifecycle before evidence production.

## RUN-02 — Replay, comparison and evidence reporting

**Depends on:** RUN-01 and ANA-07. **Complete before:** NUM-07/P4 exit.

1. Implement replay into a new run directory, environment verification and input/source/data checks.
2. Separate bitwise reproducibility from metric reproducibility; freeze backend-dependent tolerances from evidence.
3. Generate a human-readable report with run/domain/metric/check identities and a machine-readable artifact index.
4. Refuse promotion of INVALIDATED runs. Retain ALERT/INDETERMINATE notes and missing evidence.
5. Add CLI integration checks for changed config/data hashes, unavailable reference, dirty-source snapshot policy and nonzero failure exits.
6. Replay a selected analytical example from its recorded environment in a fresh environment.

**Artifacts:** reproduce/report modules, CLI docs and checks, replay report, compact example bundle. **Accept:** a fresh replay matches its predefined check; tampering is rejected. **Failure:** F-09/F-10; report unreproducible records without inventing metadata.

## Manifest and storage checklist

- Identity: schema version, experiment/run/claim IDs, UTC timestamps, parent experiment version and retry/branch relationship.
- Inputs: full canonical scenario, hypotheses/observables, config hash, data hashes and durable access references.
- Code: immutable commit, clean/dirty flag; if exploratory dirty work is allowed, retain patch hash and snapshot. Accepted claim evidence requires a reproducible source identity.
- Environment: lock/hash, interpreter/compiler/platform, CPU/GPU/driver when used, precision and seed stream mapping.
- Physics: equation IDs, fluid/material properties, model applicability, geometry, boundary/source and amplitude conventions.
- Execution: command, resource estimate/caps/actual usage, stop reason, failure diagnostics, partial output index.
- Evidence: metrics with definitions/units/windows, refinement series, uncertainty records, pre/post MCLF, benchmark comparison and review links.
- Retention: small Git metadata versus external/raw output location, checksums, access method and retention responsibility.

A failed large run is retained by identity and necessary diagnostics; retaining every redundant large array is not mandatory. Record explicit retention decisions and keep raw data needed for claim-critical reproduction. Never delete inconvenient failures from the study index.

## CI before every commit

Inspect `.github/workflows/quality.yml` at the time of work; the file itself is authoritative. The reviewed [ENV-1.0 profile](../../requirements/README.md) uses CPython 3.12.14, hashed dependency locks, a local editable build, installed-environment verification, Ruff, pytest and required-document checks. Reproduce the complete workflow on the final content after any last edit. In the activated development environment:

```bash
set -e
python -m pip --isolated install --index-url https://pypi.org/simple --require-hashes --only-binary=:all: -r requirements/dev-linux-py312.lock
python -m pip --isolated install --no-index --no-deps --no-build-isolation -e '.[dev]'
python -m pip check
python scripts/verify_environment.py
ruff check .
pytest
test -f docs/D00-document-control.md
test -f docs/PLAN-01-project-execution-plan.md
for id in 01 02 03 04 05 06 07 08 09; do
  test -n "$(find docs -maxdepth 1 -name "D${id}-*.md" -print -quit)"
done
for id in 01 02 03 04 05; do
  test -n "$(find guides -maxdepth 1 -name "G${id}-*.md" -print -quit)"
done
```

Use a virtual environment when the interpreter is externally managed; do not modify the managed interpreter. Read the latest remote CI result before committing. If the latest run failed, identify and locally resolve that failure in the proposed commit. A known historical failure does not prevent committing its verified fix; current content must pass all required local checks.

Also inspect relative Markdown links, planned-vs-existing command labels, the task dependency graph, staged diff and `git diff --check`. These documentation checks supplement CI; do not imply that the current workflow already enforces them automatically.

## Identity and publication

1. Work from the canonical Git checkout and inspect `git status`; record any alternate working copy explicitly. Do not assume a folder containing documents also contains Git history.
2. Check `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT`. Expected configured owner: JuanFelipeLH <felipelamos2003@gmail.com>. If missing/mismatched, stop before committing; never invent or override an identity.
3. Stage only intended public artifacts. Keep `AGENTS.md`, `.codegraph/`, machine-specific settings, secrets and generated run output untracked/ignored.
4. Inspect staged content, confirm complete local CI on that content, and commit in English using the configured owner identity.
5. After the authorized push, inspect the remote Actions run for that exact commit. Diagnose any failure with F-10 before declaring delivery complete.
6. Preserve published history. Record the commit and CI URL in the task's delivery report.

## Documentation completion at each phase

Update capability/status text, command examples, module interfaces, D03 traceability, D09 equation/claim register, benchmark results, limitations and next gate. All maintained repository text is English. User explanations may be Spanish. Do not mark phase or scientific claims complete by editing the tracker without evidence.
