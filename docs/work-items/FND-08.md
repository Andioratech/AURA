# FND-08 — Locked Development Environment and P2 Review

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Depends on:** FND-07

## Question and scope

Can a fresh CPU environment reproduce the foundation checks with explicitly pinned interpreter/dependency artifacts, and is the P2 evidence complete enough to begin the planned run lifecycle?

Starting revision: `67f5c91dcc411cc8aab629afc918566b8db7370f`. Authority: D00, D05–D08 and the P2 exit checklist. Preserve scientific contracts and separate software gate PASS from model/experimental acceptance. Read the FND-01…07 evidence and existing G01–G05 procedures; do not imply their DRAFT status changed.

## Protocol fixed before execution

- Freeze CPython 3.12.14 / Linux x86_64 as the tested foundation profile. Retain the previously tested runtime/test package versions, review their current release metadata and licenses, and pin their transitive wheel digests. Build tooling is explicitly selected and verified: pip 26.2.1, setuptools 84.0.0 and wheel 0.48.0. Other interpreters/platforms remain outside this profile; the project metadata's broader Python range does not certify them.
- Keep the runtime install small. NumPy/SciPy remain reviewed candidates for later numerical tasks, not dependencies installed in P2 without an implementation need. No GPU/remote numerical backend is introduced.
- Store separate core and development requirement locks with SHA-256 for every selected wheel and an artifact/provenance inventory. Download from the official package index, compare actual wheel bytes with release metadata, inspect wheel licenses/compatibility metadata and preserve exact filenames/URLs. Do not commit wheels or generated environments.
- Install with mandatory hashes and binary distributions; install the local project with no dependency resolution and no isolated unpinned build environment. Verify installed package versions and dependency consistency. New tooling must detect altered/missing/unexpected package versions and inconsistent lock/inventory entries rather than silently refreshing pins.
- Pin the CI interpreter patch, runner OS label and official action revisions. The host kernel, C library and interpreter build are recorded, not claimed identical across machines. This is a reproducible Python package profile, not a bit-identical operating-system image.
- Exercise a completely new virtual environment, full lint/tests/document checks and installed CLI behavior; include a deliberately incorrect wheel hash to prove rejection. Use a second clean core-only installation to check the smaller runtime path. Keep any failed attempts in this record.
- Review every P2 exit criterion with actual artifacts and unresolved scope. Review role is implementation/artifact self-review, not an independent scientific reviewer or invented owner approval. Independent scientific review remains assigned to the later gates that require it.
- Give the owner the requested plain-Spanish explanation of the simulation system/core at this exit, before implementing RUN-01/P3. This task does not build the run lifecycle or field/force/dynamics solvers.

Primary observables: exact pinned distribution set/versions, installation/hash-rejection outcomes, full test count, CLI exit/status and requirement/gate mapping. No numerical tolerance change. CPU-only software checks; cap each installation at ten minutes and investigate full tests above sixty seconds. No scientific run, measurement or physical hypothesis comparison.

## Planned delivery (frozen before execution)

First deliver the locked environment/CI and its actual remote result. Then close the documented P2 gate only after reviewing that evidence and rerunning final CI. FND-08/P2 status and eligible next task remain pending until the checks are complete.

## Environment implementation and observations

Delivered [ENV-1.0 installation and dependency review](../../requirements/README.md), seven core plus nine development/tool pins, exact artifact inventory, explicit build requirements, interpreter pin, installed-profile checker, and CI action/interpreter/OS pins. Existing runtime and test versions are retained. Numerical candidates remain uninstalled. The checker distinguishes repeated editable metadata from conflicting package versions; it does not inspect installed package bytes or certify an operating-system image.

Observed on a fresh CPython 3.12.14 environment, Linux x86_64 / glibc 2.43, Clang 22.1.3 interpreter build (2026-08-25):

- All 16 selected wheels match their official PyPI size/SHA-256 records and support the target interpreter. Core and development installs complete; `pip check` reports no broken requirements. Full development profile inspection returns no errors.
- A separate core-only environment installs the locally built `aura-science` wheel with seven runtime distributions and bootstrap pip 25.0.1, without the development extras. The inspected project wheel has SHA-256 `a458d8cac2c252ac30102c2f51a11b0cf594de4e29edcf0b0777ef45c8e9d1d1`; this is an intermediate dirty-source packaging check against the stated starting revision and this task's changes, not an accepted scientific run or a promise of bit-identical wheel rebuilding.
- Both installed CLIs were exercised outside the checkout: status exits 0, manufactured structurally valid scenario exits 3 (INDETERMINATE), empty scenario exits 1 and missing file exits 4. All eight expected outcomes matched. No simulation executed.
- An isolated download request for the actual attrs wheel using an intentionally all-zero expected SHA-256 fails with pip exit 1 and the hash-mismatch diagnostic. The reviewed lock was not altered.
- New checker tests cover lock consistency, changed/missing/extra packages, unsupported interpreter/platform/libc, malformed/includes/duplicate pins, changed inventory versions/hashes/scopes, duplicate inventory and conflicting versus repeated editable metadata. Final counts and the P2 decision follow in the gate review after exact remote CI evidence.

### Failed attempts and corrections

1. The initial one-off wheel-notice inspection incorrectly treated a ZIP directory entry (`pyyaml-6.0.3.dist-info/licenses/`) as a nonempty license file. It stopped with an assertion before writing the inventory. The inspection was corrected to exclude directory entries; code modules under directories named `licenses` were also excluded from the notice inventory. This was inspection tooling failure, not an incompatible dependency.
2. The initial installed-profile checker rejected the same local editable package listed once through site-packages metadata and once through source egg-info. Both were version 0.1.0. It now collapses identical normalized name/version records and rejects conflicting versions; two explicit regression checks preserve that distinction.
3. The first Ruff check found an import-order error in the new script; the import grouping was corrected.
4. Parsing the edited workflow locally caught an unquoted `:all:` argument in a YAML plain scalar, before publication. That command now uses a YAML block scalar. The complete parsed workflow is rerun after correction; no failing workflow is knowingly committed.

These are software setup/verification observations. No physical model, experimental uncertainty, tolerance, scientific claim, baseline approval or G01–G05 procedure status was changed.


## Final artifact review and result

The complete corrected local workflow passed **784 tests** (about 12.4 s), Ruff, hashed dependency installation, local project build, `pip check`, installed-profile verification and required-document checks. Relative Markdown file destinations resolve. The original baseline remote CI was successful before the environment commit. Commit `ff09fb182f191ed35bc7b92f6d0076ed28585cb4` then passed [GitHub Quality run 37030255717](https://github.com/Andioratech/AURA/actions/runs/37030255717), including **784 tests in 16.44 s** and the same profile check on Ubuntu 24.04 / glibc 2.39 / GCC 13.3.0. No unresolved environment failure remains in the tested profile.

[The P2 gate review](../reviews/P2-foundation-exit.md) maps every exit criterion to evidence and records the implementation self-review, separate scientific statuses, exact lock digests and integration limits. **FND-08 is DONE and P2 PASS within its software foundation scope. RUN-01 is READY; ANA-01 still depends on RUN-01.** Full local CI is repeated after these closure edits; exact closure-commit remote CI is confirmed and linked in the delivery message. The requested simulator/core explanation is delivered at this checkpoint before RUN-01/P3 implementation. No simulation lifecycle or physical solver was implemented in this task.
