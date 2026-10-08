# Exact-Sphere CBIE 179°/12 Subdivision Timeout Record

**Date:** 2026-10-08
**Published source revision before attempt:** `0992cc853683f4b893ef2d1a9b0af81745793313`
**Attempt type:** focused local pytest on an uncommitted harness configuration
**Preserved failure artifact:** `results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-12-timeout-20261008.json`
**Artifact SHA-256:** `4feec4a30f119dfc543c8044c101df71e63674402118860c4eb6f0806345afeb`

## Attempt

The target was the 179° exact-sphere action with 12 composite subdivisions per active interval (24 evaluated panels), order 256 per panel, cutoff factor 8, direct/image azimuth counts 4,096/2,048, and two repeats under the existing 120 s per-action cap.

The focused test failed with `TimeoutError: Case theta=179.0, subdivisions=12 exceeded 120.0s after evaluation.` The first action returned after the cap; the harness raised before appending its result, so no direct or image layer values were retained. The second repeat did not begin. The focused pytest session took 125.96 s overall. The failure artifact binds the exact test/harness hashes, uncommitted diff hash and ENV-1.0 dependency lock hashes; it records that output terms are unavailable.

## Interpretation

This attempt establishes only that this VM execution did not fit the first n=12 action under the existing resource limit. It is not a numerical rejection of the CBIE identity, a physical outcome or evidence of divergence. Earlier immutable 1/2/4/8/10 results remain intact. The n=12 harness/test edits were restored; the checkout is at published `0992cc8`, and neither the resource cap nor scientific assumptions were changed.

The harness currently discards a computed action when its elapsed time exceeds the cap. Any future retry should first preserve over-cap outputs in a failed artifact, even when it must stop before the second repeat.

Further work awaits the owner's choice: optimize the same numerical action under the 120 s cap, explicitly revise that cap while retaining this failure, or stop this subdivision sequence and define a separate independent verification. NUM-03 remains ACTIVE/INDETERMINATE, plan DRAFT, P4 unpassed and BEM preflight unauthorized. No matrix or solver was allocated.
