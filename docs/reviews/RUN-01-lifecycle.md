# RUN-01 Artifact Review — Diagnostic Recorder

**Date:** 2026-10-02 · **Decision:** PASS for the bounded software lifecycle · **Role:** implementation artifact self-review, not independent scientific review.

Reviewed source: `5c62bb53ac6a1ef83b51f680d8ad4849fdee74b9`. Authority: D00, D02/D03/D05–D08, PLAN-01, DEC-003 and [P2 PASS](P2-foundation-exit.md). The owner received the system/core explanation before implementation. No new scientific-scope approval is inferred.

## Acceptance evidence

| Criterion | Actual evidence | Finding / limit |
|---|---|---|
| Invalid input rejected before allocation | 22 inherited fault classes × JSON/YAML; real executor boundary tests, model/protocol/config/seed/resource/source/environment rejection | Exact expected failures; no directory/driver for rejected prerequisites |
| Inputs and actual source/environment retained | Published clean-source receipt and failure diagnostics below; ENV-1.0 checker; post-execution observation; stored protocol/config/source/lock hashes | Verified for clean editable Linux/CPython profile; dirty sources and wheel-source bundles remain unsupported |
| Successful execution has verifiable identity/output | Receipt run, external manifest anchor, `aura check`, independent `sha256sum` | Completed execution; INDETERMINATE scientific verdict; no physical solver result |
| Failed execution remains identifiable | Deliberate RuntimeError run with partial artifact, RUN_EXECUTION, terminal failed state | Failure is retained and inspectable; no promotion into scientific evidence |
| Interruption/incomplete publication remains visible | KeyboardInterrupt and actual SIGTERM delivery in isolated test scope; injected final-write failure | Aborted records retained where finalization succeeds; initial/partial records remain incomplete otherwise |
| Existing outputs cannot be reused | Both published runs refused a second invocation into the same directory; before/after file digests unchanged; exclusive-publication race test | No overwrite or resume policy; retries create a new run |
| Altered data rejected | Published receipt copied to a separate explicitly altered test directory; one appended byte yields HASH_MISMATCH with retained manifest anchor | Original remains unchanged; this copied corruption case is not another scientific run |
| Full delivery checks | [Exact implementation CI](https://github.com/Andioratech/AURA/actions/runs/37033919639); local full Quality and links | **911 tests** passed locally (15.59 s) and remotely (12.02 s); 127 new lifecycle tests; installation/profile/lint/docs passed |

The tests identify synthetic provenance used for fault injection. The two executions below use the actual committed checkout and installed environment, not those mocks. They were invoked through the installed CLI from outside the checkout.

## Actual diagnostic records

| Experiment | Run ID | Execution / audit | Manifest SHA-256 |
|---|---|---|---|
| EXP-2026-RUN01-RECEIPT | RUN-20261002-2810e7616c2d455fb206f21ed19d4111 | completed / INDETERMINATE; run/check exit 3 | `0b47e3cca46be911feb5e9bb631e94e938730377fe9dd526fab4c3a48afa2a10` |
| EXP-2026-RUN01-FAILURE | RUN-20261002-be468d20912a44fc8a7f3f434025454c | failed / INVALIDATED; run/check exit 1 | `69ab91007d84b8d88269e8fdfc2351a1d3065fc6503ca7c4ea7b06a539995a33` |

Both manifests record the reviewed source revision with `dirty: false`; `check` reports VERIFIED artifact integrity. Receipt recorder interval: approximately 0.104 s, observed process peak RSS 27,783,168 bytes. Deliberate failure interval: approximately 0.003 s, peak RSS 27,709,440 bytes. These are single software-diagnostic observations, not numerical performance benchmarks or physical simulation durations.

Generated bundles are retained locally under `results/<experiment-id>/<run-id>/`, with byte-identical copies in the shared project workspace. The supplementary stdout/check/reuse/corruption observations are retained locally in `results/RUN01-delivery-checks/`. Generated evidence stays excluded from Git; the compact IDs/digests and frozen examples are committed. Re-executing an example produces a new run ID/timestamp and therefore a new manifest hash; exact-byte replay is not claimed.

## Decision, scope and next gate

**RUN-01 DONE. ANA-01 READY.** The required minimal recorder acceptance is met: a successful diagnostic has actual verifiable provenance/output, and a deliberately failed diagnostic retains identifiable evidence. The real recorder enforces known-invalid rejection and no-overwrite behavior. The software task can close without asserting acoustic model coverage.

The first implementation is deliberately bounded to two diagnostic drivers because no scientific FieldResult contract/case implementation has yet passed P3. ANA-01 must specify the actual field output/adapter, applicability policy, expected artifacts and analytical resource estimates. ANA-02 and later cards integrate their reviewed model drivers and physical postchecks into the recorder before evidence production. A completed diagnostic does not approve any later field/force run automatically.

FR-002/009/010/011 now have scoped recorder evidence; full scientific integration, numerical resource estimates, replay, convergence and independent physical review remain open. The RUN-POST-1.0 lifecycle envelope is explicitly separate from L0-1.0 physical-result evaluation; all scientific statuses remain unresolved or invalidated as recorded. No physical equation/tolerance, D09 claim, experimental benchmark, larger-body goal or G01–G05 status changed.

Negative outcomes, lint findings and corrections remain in [the work record](../work-items/RUN-01.md). The documentation closure commit must repeat full local CI and obtain exact remote success; its identifier is reported at delivery. Reopen affected checks after identity, storage, model-admission or resource-policy changes. Use F-01/F-05/F-09/F-10 when the corresponding input/resource/integrity/delivery condition fails.
