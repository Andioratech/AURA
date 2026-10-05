# NUM-03 Reference Qualification Plan

**Status:** DRAFT · **Date:** 2026-10-05 · **Decision basis:** [DEC-007](../decisions/DEC-007-p4-field-only-error-budget.md), [DEC-008](../decisions/DEC-008-pause-mode-screening-reframe-num03.md)

## Purpose

Determine whether the existing separately implemented high-precision coupled-field calculation can provide a reproducible, uncertainty-characterized numerical reference for the frozen NUM-01 air model. This is numerical reference qualification, not physical validation and not a claim of acoustic pseudogravity.

## Candidate scope and sample set

- Retain the existing DEC-005/NUM-01 air case, geometry, medium and solver domain. Do not expand the domain or change the public order cap.
- Reuse the previously examined gap checkpoints `0.1`, `10`, `20`, and `29.9 mm`, with the existing 37-angle by three-radius spatial sample pattern. Before any execution, recover the exact point coordinates, row counts, source artifacts, hashes and configuration from the immutable local records. If they cannot be reconstructed exactly, stop and revise this plan before running.
- Assess complex pressure, the full particle-velocity vector, and pressure gradient as separate observables. Record pointwise absolute differences and the pre-existing field-specific norms; do not collapse them to one score.
- Do not interpret agreement at these checkpoints as coverage of intermediate gaps or the complete accepted domain.

## Reference and refinement design to freeze before execution

The existing evidence mentions modal orders 512, 800 and 1200, source radial rules 128, 256 and 512, and a 300-digit Decimal implementation. These are candidate levels, not yet an accepted matched refinement matrix. First verify that each level uses the same equations, sample coordinates, source convention and comparable boundary/domain treatment. Then freeze at least three comparable levels for each critical refinement that affects the reference, including modal truncation and source integration. Record arithmetic precision checks separately.

Use the production binary64 implementation and the high-precision direct coupled implementation as distinct numerical implementations of the same declared model. State shared equations and shared assumptions explicitly: this comparison can assess numerical implementation differences, but cannot validate the physical model or independent experimental truth.

Before execution, the protocol must specify:

1. Exact sample coordinates, grouping and deterministic row order.
2. Matched modal-order, source-integration and arithmetic-precision configurations, with a content hash for every input and output.
3. Pointwise and aggregate metrics for each field observable, including normalization rules and behavior near zero values.
4. How numerical-reference uncertainty is formed from discretization, modal-tail, quadrature and arithmetic evidence. A last-step difference alone is only an indicator, not an upper bound.
5. A resource estimate for the exact source revision and environment, a fixed resource cap, and a stop condition if the estimate is exceeded.
6. A decision rule that reports either a defensible uncertainty characterization or INDETERMINATE. Do not invent a field tolerance; derive one only from the benchmark-specific use requirement and justified reference uncertainty.

## Stop and outcome rules

- Stop before computation if the source artifacts, matched refinement levels, sample domain, metric definitions or resource cap cannot be frozen.
- Stop and retain an inconclusive result if any critical observable fails to show interpretable behavior across the required refinement levels, if the independent implementations disagree without explanation, or if numerical uncertainty cannot be bounded or characterized for the stated use.
- If reference behavior is reproducible and its uncertainty is characterized, report that result for owner review. It does not by itself pass P4; a separate benchmark-specific field-accuracy requirement and comparison protocol remain necessary.
- If this reference route cannot support the required uncertainty within its resource cap, follow DEC-007 and reassess the NUM-01 fallback comparison. Preserve all failed and inconclusive outputs.

## Deliverable

A reviewable reference-qualification report with immutable inputs/configuration, exact scope, per-observable refinement tables, uncertainty components and their status (bound, estimate, or unresolved), resource evidence, preserved failures, and a clear recommendation. NUM-03 stays ACTIVE/INDETERMINATE until its separate gate conditions are met.
