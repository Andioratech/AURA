# RUN-01 — Immutable Execution Lifecycle

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Depends on:** FND-08 and P2 PASS

## Question and scope

Can one bounded execution retain its actual input, protocol, source/environment identity, outcomes and failures without overwriting an earlier record?

Starting revision: `879751077cc6267740cc42dfa8336e1caa36ca0e`. Authority: D00, D02, D03 FR-002/009/010/011, D05–D08, DEC-003 and the P2 review. The owner received the requested system/core briefing at P2 exit and directed continuation. This task implements the recorder and an explicitly synthetic diagnostic; analytical acoustic fields remain ANA-01 onward.

## Frozen implementation protocol

- Reuse schema 1.0 Scenario, Experiment and RunManifest plus FND-07 identity primitives. Require a supplied versioned experiment and an accessible local protocol whose actual bytes match its declared digest; never generate an experiment ID from a successful outcome. Generate a UUID-based run ID before execution.
- Offer only registered versioned software diagnostic drivers initially: normal receipt and deliberate exception. Both have a fixed, separately documented software protocol, no field/force result and no randomness. Require an explicit seed value or explicit no-randomness choice. Reject unsupported models before output allocation.
- Preserve existing L0 prechecks. An INVALIDATED or ALERT precheck blocks execution. Permit INDETERMINATE only for the registered software diagnostic under DEC-003, with a mandatory explicit exploratory limitation in the receipt and manifest. No caller-controlled scientific-acceptance override. Future analytical drivers require their own reviewed execution policy.
- Postcheck actual stored input/output hashes and run/experiment/configuration links. Store a separately identified lifecycle post-audit: integrity failures invalidate; missing physical-model coverage remains INDETERMINATE. This post-audit is not the existing L0 physical-result evaluator, does not forge a FieldResult, and does not change R-001…R-010 or pretend a software receipt is acoustic evidence.
- Support clean Git checkouts and the verified ENV-1.0 development profile initially. Determine source from the executing package; reject a dirty/missing checkout or unexpected environment before allocation. Record actual commit, package source-file digests, complete package/runtime profile and every lock input. Dirty snapshot/replay support stays RUN-02 rather than supplying an unverifiable patch digest.
- Bound documents and source/environment inspection. Preflight a small fixed CPU-only workload and storage budget against requested RAM/disk/time and available local resources before creating the run directory. Record the estimate, precision, expected outputs, no-randomness policy, elapsed time, process peak RSS and output byte count. This is a diagnostic workload estimate, not a PDE resource model or a hard operating-system sandbox.
- Never reuse an existing output directory, including an empty one or symlink. Publish each file without replacement using a same-directory temporary file, fsync and exclusive atomic publication. Preserve an initial running manifest separately from the final manifest. Finalization never rewrites the initial state or input snapshots.
- Retain diagnostic partial output, typed failure and an aborted record for catchable interruption. If termination/storage failure prevents finalization, preserve the running record/partial files; read-only checking reports incomplete and never invents completion or resumes into the same directory.
- `aura run` exposes the bounded diagnostic; `aura check` reads and verifies a recorded bundle. Preserve existing validate-config behavior. Separate execution status, integrity result and scientific verdict. A completed but scientifically INDETERMINATE diagnostic returns exit 3; invalid data/integrity and execution failure remain nonzero. No replay, plotting, evidence promotion or physical solver is implemented here.

## Verification and delivery

Freeze exact assertions: valid diagnostic completes with verifiable hashes and unresolved scientific status; invalid input/protocol/model/resources/source/environment never reaches allocation/driver; reused directories remain unchanged; deliberate exception and interruption retain identity and partial output; altered/missing/traversing/symlinked bundle files fail inspection; incomplete finalization remains visible. Use known fixtures and independent byte hashes, not physical tolerances. Full suite target < 60 s; investigate slower execution. Installation cap ten minutes. Keep all failed attempts and scope limitations.

Deliver implementation/tests/contracts first with complete local and exact remote CI. Exercise the published clean-source CLI in real fresh run directories, including the negative diagnostic, then record the actual evidence and close the task in a separate verified documentation commit. No owner scientific decision or independent physical review is inferred from software success.

## Implementation and verification before publication

Delivered `runs/manifest.py`, `provenance.py`, `execute.py`, `check.py`, lazy CLI `run`/`check` dispatch, [RUN-1.0 contract](../research/run-lifecycle.md) and two [frozen software examples](../../examples/runs/README.md). Schema 1.0 and L0-1.0 are unchanged. The post-audit is explicitly a separate lifecycle envelope; it does not masquerade as a physical MclfReport. Source is observed from the executing checkout; dirty and core-only installed-wheel execution are explicitly unsupported rather than populated with invented provenance.

The first focused lifecycle suite passed **64 cases**. Additional real-boundary rejection/CLI checks brought the lifecycle plus existing CLI suite to **204 passed**; an intermediate full suite passed **902 tests in 15.53 s**. Final review added nine further consistency/provenance/interrupt cases; the resulting focused lifecycle suite passed **127 tests in 4.40 s**. The tests explicitly label mocked source/environment observations as test-only. Actual published clean-source executions are still required below; synthetic observations are not accepted provenance.

Coverage includes all 22 existing input-fault classes in both JSON and YAML before observation/allocation; missing/changed protocol, wrong configuration identity, unsupported driver/version, explicit seed policy, insufficient RAM/disk/time, source/environment refusal, original input preservation, completed/failed/aborted states, partial output, SIGTERM handler restoration, finalization/storage failure, existing/empty/file/symlink output refusal, concurrent exclusive file publication, FIFO rejection, indexed file alteration/removal/symlink substitution, path traversal, independent manifest anchors and rehashed contradictory state/audit/metric/environment records. No physical test or numerical tolerance is introduced.

### Preserved development findings

Initial lint identified import ordering in the new modules/tests and the broad driver-exception handler. Import grouping was corrected. The handler intentionally records every ordinary executor exception; its narrowly located lint exception documents that failure-retention boundary, while final publication errors still propagate and leave the initial record/partial files intact. All executed functional test suites passed; negative diagnostic outcomes are deliberately asserted, not discarded failures.

Artifact self-review also tightened tracked-source inventory, environment-observation timeouts, preallocation interruption reporting, final checksum absence, cross-record metrics/audit/profile consistency and process CPU metadata before publication. The protocol and scientific tolerances were not weakened. Full local CI and exact remote CI must pass for the implementation commit, followed by the actual clean-source CLI checks and separate closure review.


## Published execution evidence and decision

Implementation commit `5c62bb53ac6a1ef83b51f680d8ad4849fdee74b9` passed full local Quality with **911 tests in 15.59 s** and [exact GitHub Quality](https://github.com/Andioratech/AURA/actions/runs/37033919639) with **911 tests in 12.02 s**. No new dependency or lock version was needed. Maintained documentation file links resolve.

Two actual installed-CLI executions from that clean source produced the frozen receipt and deliberate-failure outcomes. Both passed read-only integrity checking against separately retained manifest digests; both refused directory reuse without changing any file; an altered copy was rejected. Independent `sha256sum` matched both recorded manifest digests. [The artifact review](../reviews/RUN-01-lifecycle.md) records exact experiment/run IDs, checksums, local retention, resource observations and limits. The failure run remains failed and its lifecycle verdict INVALIDATED; retaining it correctly does not promote it into scientific evidence.

**RUN-01 is DONE within the minimal diagnostic recorder scope; ANA-01 is READY.** Actual analytical driver admission, outputs and resource estimates must be frozen in ANA-01 and integrated as their P3 models are implemented. Dirty-source execution, environment reconstruction/replay and scientific model acceptance remain unavailable. This closure documentation is delivered in a separate commit after another full local workflow and exact remote CI confirmation; no additional owner decision is required to continue the approved analytical foundation.
