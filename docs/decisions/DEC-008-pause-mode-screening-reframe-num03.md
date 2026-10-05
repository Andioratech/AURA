# DEC-008: Pause Mode Screening and Reframe NUM-03

**Status:** RECORDED OWNER DIRECTION · **Date:** 2026-10-05 · **Owner:** AURA project owner

## Context

NUM-03 has accumulated exact-rational Simpson-remainder upper bounds for individual source coefficients through mode 65. Those bounds cover discrete gap samples but do not measure actual integration error, propagate into field observables, or establish total reference uncertainty. The mode-66 global sweep completed locally, while its interval comparison was interrupted before producing an output. No mode-66 result is accepted.

DEC-007 requires a benchmark-specific field reference, an uncertainty method, a frozen sample/refinement protocol, an acceptance basis, and a resource cap before broad convergence work. D06 requires convergence evidence on critical observables. Continuing one-mode-at-a-time coefficient screens has not met those field-level requirements.

## Decision

1. Pause further sequential mode-only Simpson-bound screens after the accepted mode-65 evidence. Preserve the mode-66 global output and the interrupted interval attempt as local diagnostics; do not represent them as an accepted package.
2. Reframe the next NUM-03 task as a bounded qualification of the existing high-precision coupled-field reference route. First prepare a reviewable protocol using the previously examined four-gap, 37-angle, three-radius sample pattern, with exact source artifacts and configurations recovered before any rerun.
3. The protocol must assess complex pressure, particle velocity, and pressure gradient separately; identify at least three comparable refinement levels for the critical observables; separate modal truncation, source-integration and arithmetic effects; document reference uncertainty and a resource cap; and define a stopping rule before computation.
4. Differences between finite calculations are discrepancy indicators, not error bounds unless a justified convergence model or a rigorous remainder argument supports that interpretation. If the reference uncertainty cannot be defensibly characterized, retain INDETERMINATE and use the NUM-01 fallback route described in DEC-007.
5. This direction changes task order only. It does not change the physical model, target domain, order cap, any prior result, or a numerical tolerance. NUM-03 remains ACTIVE/INDETERMINATE; P4 remains NOT PASSED; NUM-04 remains BLOCKED. This record does not authorize a broad run or a P4 claim.

## Next action

Prepare and review [the NUM-03 reference-qualification plan](../research/NUM-03-reference-qualification-plan.md). Execution must wait until the sample provenance, refinement configuration, uncertainty interpretation, resource estimate, and stop rule are reviewable under DEC-007 and D06.
