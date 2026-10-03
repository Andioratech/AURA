# RUN-02 Artifact Review — Replay, Comparison and Report

**Date:** 2026-10-03 · **Decision:** PASS for the bounded committed-source analytical replay contract · **Role:** implementation self-review; not independent scientific or physical validation.

Reviewed artifacts: [RUN-02 implementation](../work-items/RUN-02.md), [RUN-REPLAY-1.0 lifecycle contract](../research/run-lifecycle.md), [CLI guide](../cli-usage.md), and [implementation](../../src/aura/runs/reproduce.py). Authority: D00, D05–D08, ANA-07 and ENV-1.0. No baseline equation, numerical tolerance, scientific claim, or phase gate changed.

## Acceptance evidence

| Criterion | Evidence | Finding and scope |
|---|---|---|
| Parent bundle is checked before replay | B03-AXIAL parent check with retained manifest digest 078a184f794d840f463db5160018b56ba5894dc79efb8ed1a62d6ecf53b65129 | Integrity VERIFIED; execution completed; scientific verdict INDETERMINATE |
| Recorded source and environment are reconstructed | Detached worktree at 260c73064dec57093339c033b3f0ad5273204c28; fresh venv from exact SHA-256 locked ENV-1.0 dependencies | Source/package/lock hashes and interpreter/dependency profile match. Host snapshot differs in glibc 2.43 vs 2.41, kernel/platform and Python build; D05 permits these differences within the profile, and the report records them |
| Field values reproduce | Parent compared against final replay RUN-20261003-6be0ee4c106a4e4d965474df709c5683, manifest SHA-256 c52fd82ea6bbef12ccc940b2f9fd4b0b111ff79c985b91fa5c82077edeec43be | Coordinates, pressure, velocity and pressure-gradient bytes all match exactly |
| Metric and reference checks are source-bound | Analyzer and reference calculations ran in the new venv from the recorded source worktree | Four ANA-07 metric records match exactly; B03-AXIAL passes ANA-REF-1.0's existing frozen criterion. Analyzer, reference module and fixture hashes are in the replay report |
| Human and machine reports bind both runs | Local results/replays/.../RUN02-B03-AXIAL-v3-report/ | Markdown, JSON and artifact index contain the run IDs and manifest hashes; report file checksums are recorded in the task record |
| Invalid or changed parents do not produce replay output | CLI test mutates stored scenario bytes and verifies nonzero HASH_MISMATCH; invalidated/failed-parent tests refuse replay | Original bundle remains unchanged; no replay directory is allocated on rejected input |
| Caller changes are excluded | Successful replay was initiated from a checkout containing unrelated uncommitted project documentation | Child run records only the recorded commit; no caller diff or local guidance entered the run |
| Required local Quality workflow | Locked dependency installation, editable installation, pip check, ENV-1.0 verifier, Ruff, pytest and required-document checks | Initial complete pass: ENV, lint and document checks passed; 1,395 tests passed in 17.68 s. Final continuity pass: the same workflow passed with 1,395 tests in 18.86 s; `git diff --check` and changed-Markdown relative-target check also passed |

The first replay attempt stopped before field execution because an initial check incorrectly required the host runtime snapshot to be identical. Its checksummed record is retained at results/replays/RUN-20261002-e85e4a5922ab4bfa9571dfa90f1037c1/attempt-1-failure.json. Replay v1 completed with identical fields, but the analyzer ran from the caller checkout; that metric report is retained and excluded from acceptance in replay-v1-review.json. Final replay v3 reran the analyzer in the recorded source worktree and supersedes both earlier reports. A first focused test attempt also hit the host's low available-memory reading; fixtures now use a documented synthetic budget while production resource preflight remains unchanged.

## Limits and decision

RUN-02 is DONE for this bounded software scope. The command admits only completed, integrity-verified analytical field bundles with a locally available recorded commit and ENV-1.0 profile. It does not replay dirty patches or alternate interpreters/backends. Field arrays and ANA-07 metrics require exact equality; no cross-run tolerance is inferred. A missing reference stays INDETERMINATE. Every replay remains a software artifact: the child run's scientific verdict remains INDETERMINATE and physical validation remains NOT ESTABLISHED.

Generated runs, reports and failed attempts remain in ignored results/ and are not committed. The working changes have not been committed or pushed. The owner's recorded NUM-01 route choice remains the next consequential project decision before numerical backend/core work.
