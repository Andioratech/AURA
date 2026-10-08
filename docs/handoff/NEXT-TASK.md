# Next Task — Bound and Resource-Check the Modal Reference

## Latest completed step — 2026-10-08

The DRAFT modal derivation and review plan is in [the modal reference plan](../research/NUM-03-exact-sphere-modal-reference-plan.md). It derives the manufactured trace coefficients, diagonal direct-sphere layer eigenvalues, and separate reflected `K`/`V` formulas by projecting each source mode on the mirrored sphere. A one-off order-80 calculation at 179° matches the recorded image `K`/`V` values within `3.74e-15`/`1.83e-14 Pa`; the direct-layer differences are `7.19e-7`/`7.86e-7 Pa`. Two deterministic replays are byte-identical. A new analytical absolute-majorant route gives preliminary tail estimates for either image layer of `2.13e-1`, `4.28e-6`, and `7.21e-11 Pa` after cutoffs 48, 64, and 80. Its finite sums still need outward-rounded evaluation and independent review, so these estimates do not yet select a cutoff or establish numerical convergence. The reflected layer formulas do not require a separate-center translation matrix or source-ring traversal.

At the 0.1 mm plane gap, the two sphere surfaces are 0.2 mm apart. The raw kernel ratio is `a/R_min=0.9920634921...`, while the weighted image-mode estimate decays near `0.4940555239...` apart from order factors. The new candidate majorant uses power-series bounds for `j_n`, the exact finite formula for `h_n^(1)`, and `|P_n|<=1`; a geometric envelope closes the remaining tail above mode 2000. Next independently check every inequality, evaluate the finite majorants with outward rounding, prove the stated ratio cap for all orders beyond 2000, and estimate CPU/RAM for at least three cutoffs. Keep the exact combined image identity separate from layer-by-layer verification.

The owner should review the DRAFT plan before modal code is written. This review is not P2 exit or authorization to start the simulation core.

## Next bounded work item

1. Independently review the image `K` and `V` formulas from the outgoing addition theorem, confirming mirrored density parity, reflected normal, `i` factors, area factor, and derivative sign.
2. Check the candidate image-layer majorant line by line, including the `j_n` power-series envelope, `j'_n` recurrence, finite Hankel sum, Legendre bound, `n=0` handling, and `R_min` choice.
3. Recompute the finite majorants with outward rounding; analytically verify the adjacent-term ratio is below `0.495` for every integer `n>=2000`. Preserve the current ordinary-float screen as a preliminary calculation, not certified evidence.
4. Estimate runtime and memory for at least three nested cutoffs at 179°. Keep direct `K`, direct `V`, image `K`, and image `V` separate, and do not treat a last-term difference or the 0.494 estimate as a bound.
5. Update the DRAFT with the independent check and resource result, then present the complete plan for owner review before coding. Do not allocate a matrix or begin a solver/core.

## Scope and current gate

The starting case is the manufactured exact-sphere trace (`a=25 mm`, `g=0.1 mm`, `f=25,230 Hz`, `c=346 m/s`) at 179°, then 120°/135°/175° if the bound supports them. This is numerical cross-verification only. NUM-03 stays ACTIVE/INDETERMINATE; P4 is unpassed, the reference plan DRAFT and BEM preflight unauthorized.
