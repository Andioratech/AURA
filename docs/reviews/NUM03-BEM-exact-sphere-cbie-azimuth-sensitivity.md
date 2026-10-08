# NUM-03 Exact-Sphere CBIE Azimuth Sensitivity Review

**Status:** finite quadrature sensitivity; no acceptance gate or physical validation. **Date:** 2026-10-07 UTC.

## Protocol and reproducibility

Harness commit `8c022a480af3d390bae67a83c2858e77280b9f81` passed GitHub Quality run [37697902330](https://github.com/Andioratech/AURA/actions/runs/37697902330). Its full local Quality run passed 1,832 tests in 1,242.99 s, alongside locked installation, editable installation, `pip check`, ENV-1.0, Ruff, required-document checks and `git diff --check`.

The clean ENV-1.0 sweep holds geometry and meridian order fixed (`N=256` per active interval) at `a=25 mm`, plane gap `0.1 mm`, `f=25,230 Hz`, `c=346 m/s`. It evaluates the centered-monopole rigid-plane Neumann trace at 120°, 135°, 175° and 179°. Direct azimuth counts are 256/512/1,024 and image counts 512/1,024/2,048 in a full factorial grid: 36 cases, each repeated twice. The jump, direct/image double layers, direct/image single layers and CBIE residual are recorded separately. No matrix or solver is allocated.

The ignored artifact `results/diagnostics/bem-exact-sphere-cbie-azimuth-sensitivity-20261007.json` has SHA-256 `099e65caa8120be1916f43c46e410db1855ec2e82267f6ccbc7bcbeac4b39d9f`. It records clean source `8c022a480af3d390bae67a83c2858e77280b9f81`, script SHA-256 `5f2f88570588af6d5e223911cbb2d4ded07fc25556724db2027e9907a00b59d1`, ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`, environment verification, two-repeat checksums, timings and peak RSS. All 36 repeated outputs matched. Maximum repeat wall time was 5.2881 s; the 120 s threshold is checked after each case completes, not an interrupting timeout.

## Results

With image count fixed at 2,048, normalized CBIE residuals across direct azimuth counts are:

| Angle | Direct 256 | Direct 512 | Direct 1,024 |
| --- | ---: | ---: | ---: |
| 120° | 1.91305e-6 | 2.74340e-5 | 2.97909e-5 |
| 135° | 1.17032e-5 | 1.86219e-5 | 1.91374e-5 |
| 175° | 1.78114e-6 | 1.77906e-6 | 1.77870e-6 |
| 179° | 3.79206429e-6 | 3.79206446e-6 | 3.79206446e-6 |

Increasing the direct ring count does not produce monotone residual reduction at 120° or 135°. The direct single-layer contribution changes most: from count 512 to 1,024 its absolute complex change, normalized by `|p(x)|`, is `2.40e-6` at 120° and `5.00e-7` at 135°. At 175° those changes are `6.91e-10`; at 179° they are `3.59e-15`. Direct double-layer changes are smaller at every angle.

At fixed direct count 1,024, varying image counts 512/1,024/2,048 changes each recorded image-layer contribution by less than `6.0e-17 |p(x)|` across these four angles. This is observed stability for the tested implementation, geometry and grid; it is not an image-quadrature error bound or proof of universal resolution.

## Limits and next step

This sweep distinguishes direct-ring count effects from image-ring count effects while holding the meridian rule fixed. It demonstrates that the direct single-layer ring integration at 120° and 135° still changes at the highest tested count, while the image terms are stable at the tested counts. The nonmonotone residuals are retained. No threshold, error bound, field acceptance, operator solve, force/acceleration result, physical validation, or gravity equivalence follows.

NUM-03 remains ACTIVE/INDETERMINATE; its qualification plan remains DRAFT, the BEM preflight remains unauthorized, and Hasegawa remains the selected P4 backend. No matrix or solver was started.

**Completed follow-up:** direct azimuth counts 1,024/2,048/4,096 were compared at fixed meridian order 256 and image count 2,048; see the [direct-refinement review](NUM03-BEM-exact-sphere-cbie-direct-azimuth-refinement.md).

**Next bounded task:** isolate meridian-order sensitivity at 256/384/512 while fixing direct/image counts at 4,096/2,048, across the same four angles. Preserve layer values, residuals, repeats and failures. Treat the comparison as finite sensitivity evidence and do not select a universal tolerance or allocate a matrix.
