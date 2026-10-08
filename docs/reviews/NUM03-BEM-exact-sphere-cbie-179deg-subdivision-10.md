# Exact-Sphere CBIE 179° Ten-Subdivision Sensitivity Review

**Date:** 2026-10-08
**Source commit:** `07b5eecc00cb54434c0ae86e0a5c69a6e55d578c`
**GitHub Quality:** [run 37738811988](https://github.com/Andioratech/AURA/actions/runs/37738811988)
**Local Quality:** 1,842 tests passed in 1,229.21 s
**Result artifact:** `results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-10-20261008.json`
**Artifact SHA-256:** `f9f864de24158ebcd80cc525abefe97103bf5e70b3b69aced2db179dbd18e2fe`
**Harness SHA-256:** `5e065b75c7f82e1eecdef4031af57c082b7bff5c0c62a8e0d8d0b98777627804`
**ENV-1.0 lock aggregate:** `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`

## Question and setup

This bounded follow-up checks the nonmonotone level-4/8 residual at the 179° collocation point. Geometry and source remain the exact 25 mm sphere, 0.1 mm rigid-plane gap, centered monopole at 25,230 Hz and sound speed 346 m/s. The meridian cutoff factor is 8, Gauss-Legendre order is 256 per composite panel, and direct/image ring azimuth counts are 4,096/2,048. Ten subdivisions produce 20 evaluated panels at this point. The logarithmic singular product-integral restoration remains at order 256 over the full interval. Two action repeats are recorded. No matrix or solver is allocated.

## Results

The normalized CBIE residual is `3.1615960441405e-7`; the two repeats have matching checksums and both residuals reconstruct exactly from the stored jump and four layer terms. Action times were 84.2242 s and 84.8890 s, below the 120 s per-action limit.

| Subdivisions | Normalized residual |
|---:|---:|
| 1 | 3.7920644571871e-6 |
| 2 | 1.2747600096359e-6 |
| 4 | 2.9054189257073e-7 |
| 8 | 4.4604649965014e-7 |
| 10 | 3.1615960441405e-7 |

From level 8 to level 10, changes normalized by boundary-pressure magnitude are `3.6610583e-7` for the direct double layer and `3.9923288e-7` for the direct single layer. Image double- and single-layer changes are `2.3074e-15` and `3.1412e-15`. Thus the direct terms remain sensitive, while the residual oscillates rather than decreasing steadily.

## Interpretation and limits

The sequence is nonmonotone across the tested subdivision counts. The level-10 residual is smaller than level 8 but larger than level 4; this pattern is consistent with cancellation among changing layer terms and cannot be used alone as an error estimate. The singular product-integral term has not been refined with the composite panels, so this test does not establish convergence of the complete action. No level or tolerance is selected as accurate.

This is numerical evidence for one idealized geometry, source, rigid-plane image and collocation point in binary64. It does not test acoustic force, acceleration, pseudogravity, field acceptance, hardware or experimental behavior.

NUM-03 remains ACTIVE/INDETERMINATE, qualification plan DRAFT, P4 unpassed and BEM preflight unauthorized. Hasegawa remains the selected P4 backend. The next bounded test is level 12 at the same 179° point and fixed settings, selected as a computationally bounded continuation, not to minimize residual. Preserve all previous artifacts. No matrix or solver.
