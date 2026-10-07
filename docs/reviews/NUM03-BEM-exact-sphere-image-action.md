# NUM-03 Exact-Sphere Image-Action Review

**Status:** bounded numerical verification; no acceptance gate or physical validation. **Date:** 2026-10-07.

## Protocol and reproducibility

Commit `39a358f1eb92d49d31182b47481e773ef316ef75` adds the matrix-free harness [benchmark_bem_exact_sphere_image_action.py](../../tools/research/benchmark_bem_exact_sphere_image_action.py) and regression tests. The clean ENV-1.0/CPython 3.12.14 run uses the exact sphere `a=25 mm`, plane gap `0.1 mm`, `f=25,230 Hz`, `c=346 m/s`, centered monopole trace, and collocation angles 120°, 135°, 175°, 179°. It evaluates `K_image`, `V_image` and `K_image - V_image` against `-G_free(x,y_image)` using composite GL4 meridian meshes. The result records all inputs, environment lock digests, source revision, repeat checksums, timings and peak RSS. No matrix or solver is allocated.

Primary diagnostic: `results/diagnostics/NUM03-BEM-EXACT-SPHERE-IMAGE-ACTION-20261007-01/qualification.json`, SHA-256 `611c8502e999e0ec6b29dea4ff802c699dbb1de925f99df53e2a2fb515279726`. It contains 48 cases (3 meridian sizes × 4 angles × 3 static-subtracted ring counts plus one 2,048-point direct-midpoint route per mesh/angle). All 48 repeated checksums match. The largest repeat took `0.754 s`; process peak RSS was `775208` platform units (KiB on this Linux runtime).

The static-subtracted route at ring azimuth counts 32/64/128 and the pointwise route at 2,048 produce image actions within `4.5e-15` absolute across matched cases. Thus ring azimuth refinement does not explain the remaining discrepancy in this sampled case set. This is cross-quadrature sensitivity for a shared kernel and geometry, not independent physical validation or an error bound.

## Meridian refinement evidence

The relative complex discrepancy from the analytic image action at the 128-sample static-subtracted ring route is:

| Collocation angle | N=16 | N=32 | N=64 |
| --- | ---: | ---: | ---: |
| 120° | 0.130737 | 0.000416227 | 8.84735e-7 |
| 135° | 0.148508 | 0.000411853 | 7.01965e-7 |
| 175° | 0.998289 | 0.491980 | 0.283793 |
| 179° | 1.17052 | 0.504686 | 0.243139 |

The lower-angle controls improve strongly, while N=64 remains poorly resolved near the plane. This is retained as an unresolved result, not suppressed by changing the geometry or threshold.

Two targeted extensions use the same committed action function and fixed geometry. Artifact `NUM03-BEM-EXACT-SPHERE-IMAGE-ACTION-20261007-02/refinement.json`, SHA-256 `c4150b150b99cee7758c1f86bac76e3a8784eea3ab33e88a6f9e297e2b0f86e5`, repeats angles 120°/135°/175°/179° at GL4 meridian N=128/256/512 and ring count 128. At N=512 the relative discrepancies are `1.23723e-14`, `1.76792e-14`, `1.44781e-4`, and `5.13753e-3`, respectively. Artifact `NUM03-BEM-EXACT-SPHERE-IMAGE-ACTION-20261007-03/near-plane-refinement.json`, SHA-256 `80a1f63c9d2c6d45ff466220753aeea1ec232ec48e380c1d2be1c706d28aeeec`, extends only 179° to N=1024/2048; discrepancies fall to `6.57601e-5` and `2.97957e-7`. Repeated values matched in all cases. These refinements establish strong observed convergence for this exact case, but they are finite-grid comparisons and no acceptance tolerance was specified.

## Limits and disposition

The evidence is scoped to one exact sphere, one centered monopole boundary trace, a rigid-plane Neumann image construction, the listed collocation angles, GL4 meridian panels and the specified ring quadratures. It does not validate the direct singular contribution, a complete BIE solve, the selected Hasegawa P4 backend, acoustic force or acceleration, a general gravity-like field, experimental behavior, water, other bodies or other frequencies. Hasegawa remains the selected P4 backend; BEM remains a candidate numerical reference route. NUM-03 stays ACTIVE/INDETERMINATE, the plan remains DRAFT, and the public matrix/preflight remains unauthorized.

**Completed follow-up:** the combined direct-plus-image action is recorded in [the review](NUM03-BEM-exact-sphere-combined-cbie.md).

**Next bounded task:** isolate direct/image azimuth-quadrature sensitivity in the completed combined CBIE action at fixed meridian order. Keep all components separate, use at least three ring-sample levels, and treat differences as finite sensitivity evidence only. Do not allocate a matrix or solve.
