# NUM-03 Exact-Sphere CBIE Direct-Azimuth Refinement Review

**Status:** finite quadrature sensitivity; no acceptance gate or physical validation. **Date:** 2026-10-08 UTC.

## Protocol and reproducibility

Harness commit `dd7f813e17c365ed720ea5d89836e084475b41b7` adds a clean-source ENV-1.0 sweep holding meridian order at 256 per active interval and image azimuth count at 2,048, while varying direct azimuth counts 1,024/2,048/4,096. It evaluates the same centered-monopole rigid-plane Neumann trace on an exact sphere (`a=25 mm`, plane gap `0.1 mm`, `f=25,230 Hz`, `c=346 m/s`) at 120°, 135°, 175° and 179°. Each of the 12 configurations ran twice, and the recorded repeat checksums match. Every CBIE residual exactly reconstructs from its separately recorded jump and direct/image layer terms.

The ignored artifact `results/diagnostics/bem-exact-sphere-cbie-direct-azimuth-refinement-20261008.json` has SHA-256 `82fe8d2e62d856bc4e5eafa611bd8979937970726ad6d16ce61b0e2497a1dd6e`. It binds clean source `dd7f813e17c365ed720ea5d89836e084475b41b7`, script SHA-256 `f91bbfea7c662ff06606b18c683cf2cc03e85f8b0f22e111175d767228b9d733`, ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`, platform/runtime metadata, environment verification, per-case checksums and timings, and peak RSS `775208` platform units. The slowest individual repeat took `9.7478 s`. Local Quality passed all 1,834 tests in `1,246.37 s`; GitHub Quality run [37705091852](https://github.com/Andioratech/AURA/actions/runs/37705091852) passed for the exact harness commit. No matrix or solver was allocated.

## Results

Normalized CBIE residual magnitude by boundary-pressure magnitude:

| Angle | Direct 1,024 | Direct 2,048 | Direct 4,096 |
| --- | ---: | ---: | ---: |
| 120° | 2.97909417e-5 | 2.98491831e-5 | 2.98492847e-5 |
| 135° | 1.91373519e-5 | 1.91461021e-5 | 1.91461093e-5 |
| 175° | 1.77870311e-6 | 1.77867336e-6 | 1.77867281e-6 |
| 179° | 3.79206446e-6 | 3.79206446e-6 | 3.79206446e-6 |

At each adjacent refinement, the magnitude of the direct single-layer change, normalized by `|p(x)|`, is:

| Angle | 1,024→2,048 | 2,048→4,096 |
| --- | ---: | ---: |
| 120° | 5.93525e-8 | 1.03533e-10 |
| 135° | 8.48272e-9 | 7.04892e-12 |
| 175° | 5.76970e-11 | 1.05837e-12 |
| 179° | 0 | 0 |

The corresponding direct double-layer changes are smaller for every listed comparison. The residual changes from direct 2,048 to 4,096 are `1.0160e-10`, `7.2712e-12`, `5.4567e-13` and approximately `4e-17` at 120°, 135°, 175° and 179°, respectively. At 120°/135° the residual magnitude increases across these direct-count levels, while its change becomes much smaller at the highest level. This pattern is finite-grid sensitivity; it is not proof of convergence or an error bound.

## Limits and next step

For the tested geometry, trace, meridian rule and four points, the direct single-layer term changes much less from 2,048 to 4,096 than from 1,024 to 2,048. That observation does not characterize unsampled locations, separate meridian error, qualify a discretized operator, or establish a universal resolution. The order-256 CBIE residual at 120° remains about `2.98e-5`; the residual is an identity diagnostic and is not a field-accuracy tolerance.

NUM-03 remains ACTIVE/INDETERMINATE; the qualification plan is DRAFT, BEM preflight is unauthorized, and Hasegawa remains the selected P4 backend. No force, acceleration, physical validation or gravity equivalence follows.

**Next bounded task:** isolate meridian-order sensitivity using orders 256/384/512 per active interval, while fixing direct azimuth count at 4,096 and image azimuth count at 2,048 for the same four angles and exact configuration. Preserve layer values, residuals, repeat checksums, timings and failures. Treat all differences as finite sensitivity; do not select a universal tolerance or allocate a matrix.
