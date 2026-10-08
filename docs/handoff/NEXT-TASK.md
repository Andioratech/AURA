# Next Task — Extend the 179° CBIE Sensitivity Check

## Latest completed step — 2026-10-08

The previously timed-out 179°/12-subdivision action has now completed twice under the existing 120 s per-action cap after a bounded optimization shared the scalar and gradient azimuthal ring traversal. Both repeats match, at 97.72 s and 99.67 s, with normalized CBIE residual `2.8084642545928237e-7`. The exact result is recorded in [the formal continuation review](../reviews/NUM03-BEM-exact-sphere-cbie-179deg-subdivision-12-optimized.md); the ignored artifact SHA-256 is `3c13638d383cda3909e7478abfad720a7e64efb4d7c3ee3f4dd30b35ebc69e4e`. The original timeout artifact remains unchanged.

The residual over subdivisions 1/2/4/8/10/12 is nonmonotone. Direct layer terms still change; image terms are near binary64 noise for the 10-to-12 comparison. This is finite quadrature sensitivity only. No convergence, error bound, field acceptance, physical validation or gravity equivalence follows. NUM-03 remains ACTIVE/INDETERMINATE; P4 is unpassed, the plan is DRAFT and BEM preflight is unauthorized. No matrix or solver was allocated.

## Next bounded action

Run the same 179° case at 14 subdivisions, keeping factor 8, per-panel order 256, direct/image azimuth counts 4,096/2,048, two repeats and the 120 s cap fixed. Use the composite-subdivision harness's `--subdivisions 14` option and a new output name under `results/diagnostics/`. The harness must preserve layer terms if an action exceeds the cap. Compare the direct and image layers separately and report elapsed time; do not infer convergence from a smaller residual. Stop this subdivision sequence if it exceeds the cap or adds no useful information relative to its cost, then define an independent verification task from the existing NUM-03 evidence.

## Reproduction and checkout

Start from the pushed `main` branch and use the repository's Linux `ENV-1.0` environment with CPython 3.12.14. The n=12 record was produced from source revision `98735b7730972928a0237b0911e97c331dbf484d`; full configuration, exact terms, artifact hash, validation and scientific limits are in the linked review. Generated diagnostics and private AI instructions are local-only and must not be staged.
