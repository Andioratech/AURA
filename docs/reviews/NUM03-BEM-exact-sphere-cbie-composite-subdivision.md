# Exact-Sphere CBIE Composite Meridian Subdivision Review

**Date:** 2026-10-08
**Source commit:** `989627f45ce8dce86cd6f61b7bcd9f2dcce23f25`
**GitHub Quality:** [run 37727290403](https://github.com/Andioratech/AURA/actions/runs/37727290403)
**Local Quality:** 1,842 tests passed in 1,334.40 s
**Result artifact:** `results/diagnostics/bem-exact-sphere-cbie-composite-subdivision-20261008.json`
**Artifact SHA-256:** `5eb49e948b1b1ff4de8259ea85a66676c31cdfff3976a9cfbc1ac26085798e14`
**Harness SHA-256:** `8627e68c60f4b53a43e8516b0bbee308fda98170012240c2ce85cba5a61a2592`
**ENV-1.0 lock aggregate:** `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`

## Question

How does the streamed exact-sphere CBIE action respond when each active meridian interval is subdivided 1, 2 or 4 times, while holding the cutoff factor, per-panel Gauss-Legendre order, azimuth counts, geometry and collocation angles fixed?

## Frozen configuration and method

The configuration uses a sphere radius of 25 mm, a rigid plane gap of 0.1 mm, a centered monopole at 25,230 Hz in sound speed 346 m/s, and the same four collocation angles (120°, 135°, 175°, 179°). The meridian cutoff factor is 8. Each active interval uses 256 Gauss-Legendre points per composite subinterval; direct and image ring integrations use 4,096 and 2,048 azimuth samples. Each case runs twice. No dense matrix or solver is created.

The parameter changes only the composite subdivision of the previously defined active intervals. The logarithmic singular terms are still restored by the same order-256 product-integration rule over the complete meridian interval. The comparison therefore refines the sampled regular-remainder contributions, but it does not refine every component of the action at once.

## Results

All 12 configurations completed. The two repeats of each configuration have identical checksums; every residual reconstructs exactly from the stored jump and four layer terms. Each action repeat took 4.89–42.61 s, under the 120 s per-action limit. Peak RSS is 775,208 platform units as reported by `resource.getrusage`.

| Collocation angle | Active intervals | Evaluated panels at 1/2/4 subdivisions | Normalized residual at 1/2/4 subdivisions |
|---:|---:|---:|---:|
| 120° | 1 | 1 / 2 / 4 | 2.98492847e-5 / 8.19021071e-6 / 1.95423785e-6 |
| 135° | 1 | 1 / 2 / 4 | 1.91461093e-5 / 1.48604373e-6 / 2.55261494e-9 |
| 175° | 2 | 2 / 4 / 8 | 1.77867281e-6 / 3.46755923e-7 / 2.95047705e-7 |
| 179° | 2 | 2 / 4 / 8 | 3.79206446e-6 / 1.27476001e-6 / 2.90541893e-7 |

The subdivision-1 terms and residuals match the prior factor-8 partition-sensitivity results bit for bit at all four angles. From subdivision 1 to 4, the observed residual drops at every angle. The 175° residual changes less from 2 to 4 than from 1 to 2. The image-layer changes are many orders smaller than changes in the direct double- and single-layer terms for these cases.

## Interpretation and limits

This is deterministic, finite-grid numerical sensitivity for one idealized exact sphere, centered-monopole trace, rigid-plane image construction, four angles, stated quadrature rules and binary64 arithmetic. The reductions show that the CBIE action depends on composite meridian sampling in this setup. They do not show that the residual is an error estimator, that subdivision 4 is sufficient, or that the action converges. In particular, cancellation can make the residual small while individual direct layer terms still change, and the logarithmic product-integration restoration remains at fixed order 256.

No force, acceleration, field acceptance, acoustic pseudogravity, hardware performance or physical validation is tested. Do not extrapolate these results beyond the stated geometry, source, medium and numerical domain. The artifact remains ignored local research output; it is not staged.

NUM-03 remains ACTIVE/INDETERMINATE, the qualification plan remains DRAFT, P4 is unpassed, and BEM preflight is unauthorized. Hasegawa remains the selected P4 backend. The next bounded calculation is eight subdivisions at the same four angles and fixed settings, reusing the immutable 1/2/4 artifact for comparison. No matrix or solver is to be allocated.
