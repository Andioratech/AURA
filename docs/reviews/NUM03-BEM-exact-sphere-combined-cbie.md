# NUM-03 Exact-Sphere Combined CBIE Action Review

**Status:** bounded numerical verification; no acceptance gate or physical validation. **Date:** 2026-10-07.

## Contract and implementation

Commit `9bf4d4926450004947fa9a84f86a32eb41d67007` adds [the streamed action harness](../../tools/research/benchmark_bem_exact_sphere_combined_cbie.py) and a repeat/decomposition test. The action evaluates one collocation point at a time on a sphere of radius `a=25 mm`, centered at height `a+0.1 mm` above a rigid plane. The source is a centered monopole at 25,230 Hz in a medium with sound speed 346 m/s. Boundary traces come from the implemented Neumann half-space Green function. The normal points into the sphere.

The recorded identity is

`0 = 0.5 p(x) + K_direct[p](x) + K_image[p](x) - V_direct[q](x) - V_image[q](x)`.

Direct logarithmic singular coefficients are subtracted from the ring-integrated direct kernels, the regular remainder is integrated over a partition with up to three intervals (one active interval at 120°/135° and two at 175°/179°), and the analytic logarithmic terms are restored with product integration. The image terms are integrated separately. The harness records the jump, both double-layer contributions, both single-layer contributions and the final residual. It allocates no matrix and starts no solver.

## Reproducibility and results

The clean ENV-1.0 run used meridian orders 64/128/256 per active interval, direct/image azimuth counts 512/1,024, four collocation angles (120°, 135°, 175°, 179°), and two repeats per case. All 12 cases completed; repeated values matched exactly. Normalized residuals by meridian order are:

| Angle | Order 64 | Order 128 | Order 256 |
| --- | ---: | ---: | ---: |
| 120° | 1.21140931e-3 | 7.63024028e-5 | 2.74340141e-5 |
| 135° | 2.54606574e-4 | 2.04985419e-5 | 1.86219050e-5 |
| 175° | 3.58964974e-4 | 7.02808204e-6 | 1.77905929e-6 |
| 179° | 7.93651103e-4 | 1.02240404e-5 | 3.79206446e-6 |

The residual decreased at each sampled refinement level for all four angles. No tolerance or pass threshold was defined. Maximum per-repeat wall time was about 2.33 s; the script's stated 120 s value is checked after each case completes and should be interpreted as a recorded stop threshold, not an interrupting timeout.

The ignored result `results/diagnostics/bem-exact-sphere-combined-cbie-20261007.json` has SHA-256 `82501e93f58c61947783ba052361242c79c18bfc8cb51aeeb9d6ada0286224c3`. It records source revision, clean-source status, script SHA-256 `0a7595a5197c8232f49974aaa5e34fcb6da3678b16dfd7b753a23b003d157356`, ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`, environment verification, per-case timings and repeat checksums. Generated results remain local and ignored.

Full local Quality passed: hash-locked dependency installation, editable installation, `pip check`, ENV-1.0, Ruff, required-document checks and 1,830 tests in 1,159.52 s. GitHub Quality for this code commit is run [37690318741](https://github.com/Andioratech/AURA/actions/runs/37690318741); it completed successfully.

## Limits and next step

This is a manufactured identity check for one ideal sphere, one centered-monopole trace, one rigid-plane Neumann Green function, four boundary points and the listed finite quadratures. It is not an error bound, converged operator row, field acceptance, BEM solve, selected-P4 comparison, force or acceleration result, physical validation, or gravity equivalence. Finite-grid residual reduction does not show that all quadrature components are resolved, which is why the next bounded task separates azimuth-count sensitivity from meridian refinement.

NUM-03 remains ACTIVE/INDETERMINATE, its qualification plan remains DRAFT, and BEM matrix allocation remains unauthorized. Hasegawa remains the selected P4 backend; BEM remains a candidate reference route.

**Next bounded task:** hold geometry and meridian order fixed and refine direct and image azimuth counts at 120°, 135°, 175° and 179°. Record layer contributions, residuals, repeat checksums, timings and any nonmonotone or failed outcome. Use this only as finite quadrature sensitivity evidence; do not set a universal tolerance or allocate a matrix.


The first full local suite run failed two preflight import-isolation tests because this new test imported the harness at collection time. The test now loads the harness only inside its own test function, after preflight tests execute. The focused preflight/BEM rerun passed 31 tests, and the subsequent exact-tree full run passed all 1,830 tests. This test-order failure is retained here; no production behavior or tolerance was changed.
