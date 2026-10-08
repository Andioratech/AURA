# Next Task — Meridian-Order Sensitivity for the Exact-Sphere CBIE

## Latest completed bounded task — 2026-10-08

Harness commit `dd7f813e17c365ed720ea5d89836e084475b41b7` adds a clean-source ENV-1.0 sweep of the exact-sphere centered-monopole rigid-plane CBIE. It holds meridian order at 256 per active interval and image azimuth count at 2,048, and varies direct azimuth counts 1,024/2,048/4,096 at 120°, 135°, 175° and 179°. All 12 cases completed twice; repeat checksums match and each recorded CBIE residual reconstructs exactly from its jump and layer terms.

At direct count 4,096, normalized residuals are `2.98492847e-5`, `1.91461093e-5`, `1.77867281e-6` and `3.79206446e-6`, respectively. From direct counts 2,048 to 4,096, direct single-layer changes normalized by `|p(x)|` are `1.03533e-10`, `7.04892e-12`, `1.05837e-12` and zero by binary64 representation. The residual change on that interval is `1.0160e-10`, `7.2712e-12`, `5.4567e-13` and about `4e-17`. These are finite sensitivities for one exact geometry, trace, meridian rule and four points, not an error bound, convergence proof, tolerance, field acceptance or physical result. The residual at 120° remains about `2.985e-5`; do not call it a field-error estimate.

The ignored result `results/diagnostics/bem-exact-sphere-cbie-direct-azimuth-refinement-20261008.json` has SHA-256 `82fe8d2e62d856bc4e5eafa611bd8979937970726ad6d16ce61b0e2497a1dd6e`, source `dd7f813e17c365ed720ea5d89836e084475b41b7`, script SHA-256 `f91bbfea7c662ff06606b18c683cf2cc03e85f8b0f22e111175d767228b9d733`, and ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`. Local Quality passed 1,834 tests in 1,246.37 s; exact GitHub Quality run [37705091852](https://github.com/Andioratech/AURA/actions/runs/37705091852) passed. Full values and limits are in [the review](../reviews/NUM03-BEM-exact-sphere-cbie-direct-azimuth-refinement.md).

## Next bounded task

Isolate meridian-order sensitivity at orders 256/384/512 per active interval, fixing direct azimuth count at 4,096 and image azimuth count at 2,048, over the same four angles and exact configuration. Record separate layer terms, residuals, repeats/checksums, timings and failures under a clean source revision and ENV-1.0. Treat changes as finite sensitivity only. Do not infer an error bound, select a universal tolerance, allocate a matrix, or start a solver. NUM-03 remains ACTIVE/INDETERMINATE, its qualification plan DRAFT, P4 unpassed, and BEM preflight unauthorized; Hasegawa remains the selected P4 method.
