# ANA-01 — Field Contract Artifact Review

**Date:** 2026-10-02 · **Decision:** ANA-01 DONE; ANA-02 READY · **Review role:** implementation self-review

This is a bounded artifact review under the execution protocol. It is not independent scientific approval, P3 PASS or experimental validation. The owner already authorized continuation and received the core/system explanation at P2 exit.

## Reviewed evidence

Implementation revision: [`c22f4859703611d5ed6c300acb8ce89a3a8cb411`](https://github.com/Andioratech/AURA/commit/c22f4859703611d5ed6c300acb8ce89a3a8cb411).

| Acceptance item | Delivered evidence | Outcome / boundary |
|---|---|---|
| Explicit pressure, velocity and gradient outputs | [FIELD-1.0](../research/analytical-field-contract.md), [types](../../src/aura/fields/types.py) | Positive frequency, full chamber vectors, SI units, dimensions, peak phasors and complex encoding fixed; container checks representation only |
| Sampling and exclusions | FIELD-1.0 and [ANA-REF-1.0](../benchmarks/B03-B06-analytical-protocols.md) | Ordered points, duplicated positions retained, 256-sample cap, fixed observation box; source exclusion is the future driver's responsibility |
| Independent reference matrix | B-03…B-06 tables and mandatory variants | Quarter-turn/rational values, real-time sign, rotations, cancellation, unequal sources, radial spreading and reactive velocity specified; solver comparisons NOT_RUN |
| Equation provenance and assumptions | [Source review](../research/analytical-source-review.md), [equations v1.2](../registers/equations.md) | Primary equations/locators read; positive/negative time-sign conversion and project derivations documented; no force model selected |
| Error/resource budget | ANA-REF-1.0 and FIELD-1.0 | Frozen conditional rounding budget, independent high-precision oracle requirement and numerical path audit for ANA-02; bounded CPU/sample/source/output campaign; no solver resource measurement claimed |
| Recorder extension specified | FIELD-1.0 admission checklist | Required component/index/result links, manifest identity, checker changes, source-model contracts and scientific status policy specified; RUN-1.0 still diagnostic-only |
| Representation verification | [122 new tests](../../tests/test_field_types.py) | Positive/negative shapes, numbers, units, metadata, mutation isolation, round trips, sample limits and extreme finite encodings passed |
| Whole-project regression and delivery | Full local Quality; [exact GitHub Quality](https://github.com/Andioratech/AURA/actions/runs/37037149159) | 1,033 tests passed locally in 19.84 s and remotely in 16.92 s; installation, environment, lint and required documents also passed |

Internal maintained-document link inspection found no broken file targets (475 docs/guide links inspected, plus README links). Effective author and committer were both the owner's configured identity. No new dependency, lock change, private AI instruction, machine configuration or generated scientific data was included.

## Failures and adjustments retained

[The task record](../work-items/ANA-01.md) preserves the initial serializer lint finding and the later test-block insertion error (121 passes / 1 NameError). Both were corrected and followed by the complete successful workflow. No scientific run was attempted and no numerical failure was hidden by changing a field tolerance. During protocol review, before any field implementation, the rounding allowance was made explicit through operation/phase/product bounds; its backend assumptions still require verification in ANA-02.

## Limits and next action

The container can hold physically inconsistent values: it is not a physical audit. Component JSON records lack provenance until the future adapter links them to a real FieldResult, run and verified hashes. The proposed gradient companion and driver policy remain to be implemented with the owning analytical models; schema 1.0 has not silently gained a gradient field.

No acoustic field solver, physical run, force/trajectory, actual water comparison, microgravity result or larger-body prediction was produced. The B-06 ideal source is a mathematical reference; no hardware source has been chosen. Scientific model coverage stays INDETERMINATE and P3 stays open. Missing experimental data continues on the separate research track under DEC-003; DEC-004's scale-expansion objective is preserved.

**Next:** ANA-02 implements and checks the progressive plane-wave pressure/velocity/gradient pair, prepares an independent high-precision oracle and verifies the frozen numerical-budget assumptions. Follow FIELD-1.0 for any admitted recorder integration. Do not begin standing-wave, body-force or control implementation by treating this artifact review as their completed gate.

The separate closure commit updates the board and is subject to another complete local workflow and exact remote CI check. No owner decision is required for ANA-02 within this approved scope.
