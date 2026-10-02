# FND-04 — Versioned L0 Audit Rules and Reports

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Depends on:** FND-03

## Question and scope

Can a pure pre/post L0 audit explain malformed input, preserve failures and missing coverage, and aggregate all ten rule outcomes without promoting a supplied success label into scientific acceptance?

Starting revision: `2dd8ac3b6261feff77d92a60a28fcb68fb3c3610`. Authority: D00, D02's severity ordering, D03 FR-002/FR-009 and D08. This task implements `mclf/rules.py`, `mclf/evaluate.py`, immutable report types and a versioned rule register. It does not implement field/force solvers, resource allocation, artifact loading, hash authentication, higher MCLF levels or experimental validation.

## Frozen decisions before implementation

- R-001 structure/version; R-002 required data; R-003 canonical units; R-004 finite scalar values; R-005 ranges and cross-field limits; R-006 shape/frame/normalization; R-007 amplitude/harmonic conventions; R-008 declared identities; R-009 reviewed model coverage; R-010 result completeness and inherited limitations.
- Reuse the versioned schema definitions for structural contracts, with independent audit traversal/cross-checks. This is software separation from future solvers, not an independent physical derivation. No scientific helper or solver is invoked to issue a verdict.
- Preserve per-rule findings with code, field path and message. Reports carry registry/software version, assumptions, tolerance sources and scope; provide machine and human representations compatible with the existing MclfReport core schema.
- Aggregate exactly: INVALIDATED > ALERT > INDETERMINATE > ACCEPTED. Empty or uncovered evaluation cannot yield ACCEPTED. Do not discard a lower-priority finding when reporting the aggregate.
- Audit one scenario and optionally one field/force result plus one manifest. Pre-audits do not require results; post-audits do. The caller supplies report/run IDs and stage explicitly. Missing post-result data invalidates the selected postcheck; absent supporting identity evidence remains explicit.
- No reviewed scientific model exists yet. R-009 must report INDETERMINATE for current scenarios, even with valid geometry or a supplied ACCEPTED result. Do not add a caller-controlled coverage/success override. Whole scientific acceptance is therefore unavailable in this initial release.
- Referenced field samples and artifact digests cannot be verified at this step. Never mark their numeric/content checks passed by inspecting metadata alone. FND-07 and later artifact/model tasks own those checks.

## Verification and acceptance

Known outcomes are exact rule IDs, codes, paths and aggregate decisions. The only numeric tolerance is CONV-1.0's existing absolute 1e-12 for serialized unit directions/quaternions. Exercise each applicable accepted/rejected/uncovered branch, all severity combinations, missing/duplicate rules, malformed nested records, hard failures mixed with warnings/unknowns, post-result omissions and positive-label spoofing. Preserve any observed failures in this record.

CPU-only manufactured tests; no run/mesh allocation or actual scientific experiment. Target a full suite below 10 seconds; investigate above 60 seconds. Freeze no physical performance or measurement threshold. Complete local Quality, document links, staged/identity review and exact remote CI before delivery. Closing this card enables FND-05, not P2 PASS.

## Owner explanation checkpoint

On 2026-10-02 the owner requested notification before building the simulation system and project core. Explain the components, inputs, outputs, first verifiable cases and limitations at P2 exit, before RUN-01/P3 implementation. Foundation work continues in dependency order; no additional approval gate is invented by this reminder.

## Delivered artifacts and review

- [L0-1.0 register](../registers/mclf-l0-rules.md) and [executable rule metadata](../../src/aura/mclf/rules.py): ten predicates, affected fields, assumptions, tolerance source and default failure severity.
- [Pure evaluator](../../src/aura/mclf/evaluate.py): bounded structural inspection, scenario cross-checks, explicit identity/result coverage and preservation of adverse outcomes.
- [Immutable reports](../../src/aura/mclf/reports.py): detailed JSON/Python envelope, escaped human text, compatible MclfReport core and an explicit acceptance-gate helper. [Typed errors](../../src/aura/errors.py) distinguish invalidated audits from incomplete evidence.
- [Manufactured tests](../../tests/test_mclf.py): independent expected verdicts/paths, all 64 severity triples, multi-failure collection, missing/duplicate rules, metadata spoofing, record identity, external-field limitations, numeric/normalization checks, report limits and serialization.

Artifact review: implementation self-review against D02/D08 and the frozen protocol. Structural definitions and existing semantic validation are shared with FND-02; scenario cross-check collection is separate from scientific helpers. This is not an independent physical model or a qualified scientific review. No equation, domain threshold, schema version or dependency pin changed.

## Actual results and preserved observations

1. The first integrated audit suite passed **491 tests**. Review then made the detailed envelope strictly JSON-compatible (rule tuples become JSON lists), clarified the pre-only result predicate and added no-I/O/no-helper, norm-boundary, inline-result and date checks. That suite passed **496 tests**.
2. Explicit gate checks and their typed errors brought the final suite to **500 passed**, including **115 new audit cases** and the previous 385 checks, in approximately **1.9 seconds** on Linux/Python 3.12.14. pytest 9.1.1 and Ruff 0.16.10 were used. Two initial import-order lint findings were corrected; no test failure occurred in the recorded suites.
3. A valid manufactured pre-scenario yields R-001…R-007 ACCEPTED for their limited predicates, R-008 INDETERMINATE without a manifest, R-009 INDETERMINATE for missing model coverage, and R-010 ACCEPTED only for the pre-stage's no-output-requested condition. The aggregate remains **INDETERMINATE**.
4. A negative-density scenario combined with an ALERT result preserves the warning and uncovered-model finding while aggregating to **INVALIDATED**. A supplied ACCEPTED force result and completed manifest still cannot produce scientific acceptance. Hash strings and external array references remain unchecked evidence.
5. A larger box remains representable but does not gain reviewed model coverage. The audit reads no field artifacts and calls no wavelength, wave-number, ka or intensity helper; trap-based tests enforce this boundary.
6. Empty outcome sets remain INDETERMINATE; missing/duplicate/mutable rule containers and unknown verdicts are rejected. Overlarge inputs and excessive diagnostics fail closed. The explicit acceptance helper blocks INVALIDATED, ALERT and INDETERMINATE with named errors; hand-constructed labels are not authenticated evidence.

The complete local Quality workflow passed: editable development install, Ruff, 500 tests and required-document checks. Relative-link review checked **360 destinations with zero missing files**. The exact delivery revision and remote-CI result are reported with the commit; local success alone is not a remote result. No scientific run/experiment was executed and no adverse scientific result was discarded. The manufactured IDs and artifact references do not represent real runs or files.

## Acceptance and next branch

**FND-04 is DONE as an L0 software-audit task; FND-05 is READY.** FR-002/FR-009 have initial rule/report evidence, not complete simulator-level verification. FND-05 must consolidate the foundation checks and verify that rejected inputs cannot reach later allocation/execution boundaries. FND-07/RUN-01 handle authenticated identity, later model tasks supply reviewed applicability, and L1–L5 remain unimplemented.

P2 stays ACTIVE. Missing model/measurement evidence does not halt unrelated authorized foundation work under DEC-003. The owner's explanation checkpoint remains before the simulation lifecycle and field core begin.
