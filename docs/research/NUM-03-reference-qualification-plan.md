# NUM-03 Reference Qualification Plan

**Status:** DRAFT · **Date:** 2026-10-05 · **Decision basis:** [DEC-007](../decisions/DEC-007-p4-field-only-error-budget.md), [DEC-008](../decisions/DEC-008-pause-mode-screening-reframe-num03.md)

## Purpose

Determine whether the existing separately implemented high-precision coupled-field calculation can provide a reproducible, uncertainty-characterized numerical reference for the frozen NUM-01 air model. This is numerical reference qualification, not physical validation and not a claim of acoustic pseudogravity.

## Candidate scope and sample set

- Retain the existing DEC-005/NUM-01 air case, geometry, medium and solver domain. Do not expand the domain or change the public order cap.
- Treat the prior four-gap records as distinct candidate evidence, not as one matched refinement matrix. The order-overlap artifact `NUM03-RAYLEIGH-DISK-FOUR-GAP-THREE-SHELL-ORDER-OVERLAP-P300-20261004-01` uses gaps `0.1`, `10`, `20`, and `30.0 mm` and `rho=1.204 kg/m^3` (JSON SHA-256 `3642b2f31c92cc993bf41c2771a74d3e908d832c452c664705a495595586c90f`). The separate 29.9-mm cross-quadrature artifact `NUM03-RAYLEIGH-DISK-REFERENCE-SENSITIVITY-29p9mm-P300-N512-SIMPSON-GL256-COMPARISON-20261005-ATTEMPT-05` uses `rho=1.18 kg/m^3` (JSON SHA-256 `761f855735b84f828a5c1339fcecfbe0882bfd3075087eaf62fd796cf52de7aa`). These setups differ in both gap and medium density and must not be pooled as matched levels or directly compared as a single convergence sequence.
- The NUM-01 air contract fixes `rho=1.18 kg/m^3`. Before freezing any qualification sample set, audit every candidate artifact against the contract and record exact coordinates, row counts, source artifacts, hashes, gap, density, equations, source convention, quadrature, modal order, precision, and environment. Either exclude mismatched records from the matched matrix or classify them as non-comparable historical diagnostics; do not silently reinterpret or numerically rescale them. Any new matched reference calculation must use the frozen NUM-01 configuration.
- A separate four-gap cross-quadrature family does provide a coherent candidate spatial sample set at `0.1`, `10`, `20`, and `29.9 mm` under `rho=1.18 kg/m^3`. The four comparison records share `f=25,230 Hz`, `c=346 m/s`, piston radius `0.01 m`, sphere radius `0.025 m`, 300-digit arithmetic, order 512, the same 37 angles (`5°` through `185°` in `5°` steps), and three radii per gap following `r=a`, `a+H/2`, and `a+0.99H`. The local comparison JSON SHA-256 values are `04e4be278c5ff3ae0e84ea441dfaf1cf80a79705d360a41f5c52e040ec3cd05d` (0.1 mm), `c410ac95efdbd19dd29926735d4f1120815ded1cb97ad43a29c90fbbce666b67` (10 mm), `a242dba8a2a30ffbbff27e3c8896b7944447d1f5c1ec8a7f93191f59d3755ab2` (20 mm), and `ca8bc126d1204fc3a08d6bc6c98002046515bfb3d9d4ca0b72d02d42a2cd7622` (29.9 mm). This verifies a consistent candidate sampling schema, not accepted coverage or field accuracy. The records use different per-gap quadrature comparisons and do not provide three matched modal orders across all four gaps. The order-overlap family described above cannot fill that gap because it uses another density and a 30.0-mm endpoint.
- Before the plan freezes, reconcile this candidate set to the accepted NUM-01 domain and its exact point-generation convention, specify at least three comparable modal-order levels in the canonical air configuration, and verify each source artifact and refinement level. If those conditions or the resource cap cannot be established, stop and revise the plan before running.
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
- Stop before computation if candidate data mix different gap values, medium properties, equations, or sampling coordinates without an explicit, justified separation into comparable cases.
- Stop and retain an inconclusive result if any critical observable fails to show interpretable behavior across the required refinement levels, if the independent implementations disagree without explanation, or if numerical uncertainty cannot be bounded or characterized for the stated use.
- If reference behavior is reproducible and its uncertainty is characterized, report that result for owner review. It does not by itself pass P4; a separate benchmark-specific field-accuracy requirement and comparison protocol remain necessary.
- If this reference route cannot support the required uncertainty within its resource cap, follow DEC-007 and reassess the NUM-01 fallback comparison. Preserve all failed and inconclusive outputs.

## Deliverable

A reviewable reference-qualification report with immutable inputs/configuration, exact scope, per-observable refinement tables, uncertainty components and their status (bound, estimate, or unresolved), resource evidence, preserved failures, and a clear recommendation. NUM-03 stays ACTIVE/INDETERMINATE until its separate gate conditions are met.
