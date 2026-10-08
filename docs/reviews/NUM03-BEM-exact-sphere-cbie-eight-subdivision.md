# Exact-Sphere CBIE Eight-Subdivision Sensitivity Review

**Date:** 2026-10-08
**Source commit:** `63a3be4776be927cde292b4c4a872a5a277abd4e`
**GitHub Quality:** [run 37733826037](https://github.com/Andioratech/AURA/actions/runs/37733826037)
**Local Quality:** 1,842 tests passed in 1,339.87 s
**Result artifact:** `results/diagnostics/bem-exact-sphere-cbie-composite-subdivision-8-20261008.json`
**Artifact SHA-256:** `d466ecb4da3b5b059adca08f70c814e35afa1029fd1e0c27362c772df0056262`
**Harness SHA-256:** `39dc0053893fe67966756ae0abc16210ba4f21df5e87b85678e203d98b9008d4`
**ENV-1.0 lock aggregate:** `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`

## Question

Does the nonmonotone finite-grid behavior at the 179° collocation point persist when the active meridian intervals use eight composite subdivisions?

## Frozen configuration and method

The configuration is the exact 25 mm sphere, rigid plane gap 0.1 mm, centered monopole at 25,230 Hz in sound speed 346 m/s, cutoff factor 8, Gauss-Legendre order 256 per composite subinterval and direct/image azimuth counts 4,096/2,048. Four angles (120°, 135°, 175°, 179°) are retained for context. Each action is repeated twice. The singular logarithmic product-integral restoration remains order 256 over the full meridian interval. No dense matrix or solver is allocated.

## Results

All four level-8 cases completed twice with matching checksums and exact reconstruction of the residual from the jump and separately recorded layer terms. Action times were 31.77–69.84 s, below the 120 s per-action cap. The four artifact rows are compared with immutable level-1/2/4 results:

| Angle | Normalized residual at subdivisions 1 / 2 / 4 / 8 |
|---:|---:|
| 120° | 2.98492847e-5 / 8.19021071e-6 / 1.95423785e-6 / 5.05170284e-7 |
| 135° | 1.91461093e-5 / 1.48604373e-6 / 2.55261494e-9 / 2.54920634e-9 |
| 175° | 1.77867281e-6 / 3.46755923e-7 / 2.95047705e-7 / 3.72120393e-8 |
| 179° | 3.79206446e-6 / 1.27476001e-6 / 2.90541893e-7 / 4.46046500e-7 |

At 179°, the normalized direct double- and single-layer changes from level 4 to 8 are `7.483e-8` and `8.130e-8`; image-layer changes are below `1e-15` in this run. At 135°, the level-4/8 direct and image terms are nearly unchanged, consistent with the nearly identical residuals. At 120° and 175°, the residual continues to decrease, while direct terms still shift.

## Interpretation and limits

The 179° increase from level 4 to level 8 is direct evidence that this residual sequence is not monotone across the tested levels. The result warns against treating residual reduction as convergence or as a field-error estimator. The sampled direct layer terms remain subdivision-sensitive, while the logarithmic singular contribution is restored using the same fixed order-256 rule. No observed value selects an adequate subdivision or error tolerance.

This is finite numerical evidence for one exact sphere, source trace, rigid-plane image, four collocation angles and stated quadrature setup in binary64. It tests no force, acceleration, acoustic pseudogravity, hardware, physical medium response or experimental result. Do not generalize beyond this numerical configuration.

NUM-03 remains ACTIVE/INDETERMINATE, qualification plan DRAFT, P4 unpassed and BEM preflight unauthorized. Hasegawa remains the selected P4 backend. Next isolate the 179° behavior at 10 composite subdivisions while retaining separate layer terms and the existing 1/2/4/8 artifacts. Do not tune toward a target residual. No matrix or solver.
