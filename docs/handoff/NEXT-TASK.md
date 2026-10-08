# Next Task — Bound and Resource-Check the Modal Reference

## Latest completed step — 2026-10-08

The DRAFT modal derivation and review plan is in [the modal reference plan](../research/NUM-03-exact-sphere-modal-reference-plan.md). It derives the manufactured trace coefficients, diagonal direct-sphere layer eigenvalues, and separate reflected `K`/`V` formulas by projecting each source mode on the mirrored sphere. A one-off order-80 calculation at 179° matches the recorded image `K`/`V` values within `3.74e-15`/`1.83e-14 Pa`; the direct-layer differences are `7.19e-7`/`7.86e-7 Pa`. Two deterministic formula-check replays are byte-identical. An 80-digit outward-rounded absolute-majorant calculation bounds either image-layer tail after cutoffs 48/64/80 by `0.2127293582`, `4.274317712e-6`, and `7.207744720e-11 Pa`, plus `<2.849e-598 Pa` beyond mode 2000. This is a mathematical upper bound under the unit-source convention, pending independent review; it does not establish evaluator accuracy or physical validity. The reflected layer formulas do not require a separate-center translation matrix or source-ring traversal.

At the 0.1 mm plane gap, the two sphere surfaces are 0.2 mm apart. The raw kernel ratio is `a/R_min=0.9920634921...`, while the weighted image-mode factor is bounded by a geometric envelope below `0.495` after mode 2000. Next independently review the inequality chain and unit normalization, then estimate evaluator CPU/RAM for at least three cutoffs. Keep the exact combined image identity separate from layer-by-layer verification.

The owner should review the DRAFT plan before modal code is written. This review is not P2 exit or authorization to start the simulation core.

## Next bounded work item

1. Independently review the image `K` and `V` formulas from the outgoing addition theorem, confirming mirrored density parity, reflected normal, `i` factors, area factor, and derivative sign.
2. Independently review the image-layer majorant line by line, including the `j_n` power-series envelope, `j'_n` recurrence, finite Hankel sum, Legendre bound, `n=0` handling, `R_min` choice, and normalized source units. Reproduce the retained 80-digit Decimal result and ratio proof.
3. Estimate modal-evaluator runtime and memory for at least three nested cutoffs at 179°. Keep direct `K`, direct `V`, image `K`, and image `V` separate, and do not treat a last-term difference or the geometric factor alone as a bound.
4. Update the DRAFT with the independent review and resource result, then present the complete plan for owner review before implementing the maintained evaluator. Do not allocate a matrix or begin a solver/core.

## Scope and current gate

The starting case is the manufactured exact-sphere trace (`a=25 mm`, `g=0.1 mm`, `f=25,230 Hz`, `c=346 m/s`) at 179°, then 120°/135°/175° if the bound supports them. This is numerical cross-verification only. NUM-03 stays ACTIVE/INDETERMINATE; P4 is unpassed, the reference plan DRAFT and BEM preflight unauthorized.
