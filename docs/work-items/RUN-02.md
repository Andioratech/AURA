# RUN-02 — Replay, Comparison and Evidence Reporting

**State:** DONE · **Opened:** 2026-10-03 · **Completed:** 2026-10-03 · **Depends on:** RUN-01 and ANA-07 · **Required before:** NUM-07/P4 exit

## Authority and question

Authority: D00, D02–D09, PLAN-01, DEC-003, RUN-01, ANA-07 and G01–G05 as applicable. RUN-01 and ANA-07 are recorded DONE; the P3 owner decision is PASS for bounded analytical-software verification only. The work-board BLOCKED label was stale with respect to these delivered predecessors; RUN-02 is now eligible. This task asks whether a previously checked software/analytical run can be replayed into a fresh immutable run, compared under explicit frozen rules, and reported without promoting scientific status.

## Bounded contract

- Scientific hypothesis, body/material, medium, geometry, acoustic drive, boundary conditions, gravity and physical model: NOT_APPLICABLE to replay infrastructure. Replay reproduces a recorded software run; it cannot validate the acoustic model or physical behavior.
- Observable: exact input/protocol/source/environment identities, four field-array digests, and ANA-07 E_max/E_rms/component-count/criterion records. Field arrays and replay metrics require exact equality; the separately defined ANA-REF-1.0 oracle retains its frozen normalized tolerance.
- Rejection conditions: any unverifiable source bundle, input/data hash mismatch, unavailable required environment, forbidden source revision/policy mismatch, output-directory reuse, unsupported comparison, or invalidated record blocks replay/report promotion and preserves the original bundle.
- RUN-01 schema remains immutable unless a reviewed, versioned additive contract is required. Every replay creates a new run ID/directory; it never overwrites or resumes the selected run.
- Comparison states remain separate from execution and MCLF states: PASS/FAIL/INDETERMINATE. Bitwise equality and metric reproducibility are distinct. Missing reference yields INDETERMINATE, never an inferred pass.
- INVALIDATED evidence cannot be promoted. ALERT/INDETERMINATE and missing evidence remain visible in reports with scoped limitations.

## Frozen implementation and checks

1. RUN-REPLAY-1.0 verifies the parent bundle, checks out its recorded commit into a temporary detached worktree, verifies package/lock bytes, rebuilds ENV-1.0 from hashed dependencies, and executes the saved inputs into a new immutable run. Dirty caller changes are excluded; the exact parent revision must exist locally.
2. The fresh environment must pass ENV-1.0 with Python 3.12.14, CPython, Linux, x86_64, exact distribution inventory/locks and glibc >=2.28. Host build/kernel/platform snapshots are recorded and compared but may differ as allowed by D05.
3. The four field arrays compare byte-for-byte. ANA-07 normalized metrics compare by exact value; no cross-run numeric tolerance is defined. The reference comparison remains separate and uses only ANA-REF-1.0's frozen tolerance.
4. replay-report.json, replay-report.md and artifact-index.json bind the parent/replay run IDs and manifest digests without modifying RUN-1.0 bundles. INVALIDATED/failed/aborted runs are rejected; unresolved scientific and physical status remains explicit.
5. CLI checks cover changed bundle hashes, unavailable references, dirty caller-source isolation, existing output/report paths, structured nonzero failure, and the selected real analytical replay. Generated run bundles/reports stay outside Git.

Implementation paths are `src/aura/runs/reproduce.py`, RUN CLI dispatch, `tests/test_reproduce.py`, a tampered-parent integration case in `tests/test_runs.py`, `docs/research/run-lifecycle.md`, `docs/cli-usage.md`, and the planning/build maps. No solver dependency, numerical backend, force model, motion model, controller, or simulation-core implementation was added.

## Resources and stopping rules

Use ENV-1.0 and the bounded analytical case. Fresh package installation is hash-enforced and capped at 900 seconds per install operation; commands are capped at 180 seconds. Replay stops before field execution on a missing revision, source/lock mismatch or invalid environment. The original and new run bundles obey RUN-1.0's storage limits. Do not commit generated result arrays. Preserve failed attempts and reports with checksums and causes.

## Execution and delivery

- [x] Confirm RUN-01/ANA-07 dependency evidence and applicable baseline contracts.
- [x] Freeze replay/comparison/report protocol before implementation.
- [x] Implement only the named artifacts and versioned interface changes.
- [x] Run focused positive/negative integration checks and the complete local Quality workflow.
- [x] Record clean-source replay IDs/checksums and exact limitations.
- [x] Refresh board, research contract, continuity checkpoint and next-task briefing together.
- [ ] Before any commit, inspect remote CI, rerun full local CI against exact staged changes, inspect staged diff and verify effective owner author/committer.
- [ ] After any authorized push, verify exact remote CI.

## Outcome

The selected parent is RUN-20261002-e85e4a5922ab4bfa9571dfa90f1037c1, B03-AXIAL, manifest SHA-256 078a184f794d840f463db5160018b56ba5894dc79efb8ed1a62d6ecf53b65129, from source revision 260c73064dec57093339c033b3f0ad5273204c28. Final replay RUN-20261003-6be0ee4c106a4e4d965474df709c5683 has manifest SHA-256 c52fd82ea6bbef12ccc940b2f9fd4b0b111ff79c985b91fa5c82077edeec43be; all four field artifacts are byte-identical, all four ANA-07 metric records compare exactly, and both parent/replay comparisons pass ANA-REF-1.0. The metrics analyzer and frozen reference fixture ran inside the fresh environment from the same detached source worktree; their code/fixture hashes are in the report. The environment matched locked packages and interpreter profile. Its runtime snapshot differs in glibc (recorded 2.43, replay 2.41), kernel/platform and Python build; these differences are reported and permitted under ENV-1.0. Both run bundles independently pass aura check with their recorded manifest anchors and correctly remain scientifically INDETERMINATE / physically NOT ESTABLISHED.

Attempt 1 stopped before field execution because the first implementation incorrectly required identical host-runtime snapshots. Its preserved record is results/replays/RUN-20261002-e85e4a5922ab4bfa9571dfa90f1037c1/attempt-1-failure.json, SHA-256 80c9fce4dc1e28b471fd8a0f0c366c9b6d401b7c87b58571fc15ce7bd75a6a75. The corrected gate follows D05's actual ENV-1.0 constraints and makes permitted host differences visible. Replay v1 completed with identical field arrays, but its analyzer came from the caller checkout rather than the recorded revision; it is retained and excluded from acceptance in replay-v1-review.json (SHA-256 9de55d5ea11636602e9503d096ff68e8f3260ccae208b2a5ad81c63bf44cf044). The final v2 run binds ANA-07 metrics and reference hashes to the recorded source. A first lifecycle test run rejected 15 existing analytical cases because the host exposed only 858,857,472 bytes via SC_AVPHYS_PAGES while pytest's process high-water estimate exceeded that temporary amount; no scientific run was produced. Test fixtures now provide an explicit synthetic 16-GiB budget, while production preflight is unchanged. Focused verification passed 153 tests in 5.56 s; the seven replay/report tests also passed in that run.

The final report is retained under ignored results/replays; JSON SHA-256 5590a6276febe39b1604ebce7371bc969b150c84407dd430a77bec8c98ae2141, Markdown SHA-256 249a969ca95191fd8809750519cfda2dc60c4cf0770fc1768539f083c83074fd, index SHA-256 561e141323b5bd84da1a52e4b39611146fda1d285f27565a37fe8b619d2f9c2d. Generated outputs remain excluded from Git. Complete local Quality passed with ENV-1.0, Ruff, required-document checks and 1,395 tests in 17.68 s; the Markdown review itself was added after that run, so the final continuity edit is followed by another complete pass. See the [artifact review](../reviews/RUN-02-replay-report.md). This task is DONE at the artifact/worktree level; any future commit or push must separately satisfy remote CI, identity and delivery rules.
