# NUM-03 Exact-Sphere CBIE Meridian-Partition Sensitivity Review

**Status:** finite quadrature sensitivity; no acceptance gate or physical validation. **Date:** 2026-10-08 UTC.

## Protocol and reproducibility

Harness commit `f02a4b1b6ad6880b6d3b9a7f5d5ea5e06e18a808` adds an ENV-1.0 clean-source sweep of meridian cutoff multipliers 6/8/10 at fixed Gauss-Legendre order 256 per active subinterval and fixed direct/image azimuth counts 4,096/2,048. It evaluates the centered-monopole rigid-plane Neumann trace on the exact sphere (`a=25 mm`, gap `0.1 mm`, `f=25,230 Hz`, `c=346 m/s`) at 120°, 135°, 175° and 179°. All 12 cases completed twice with matching checksums; each residual exactly reconstructs from its separate jump and layer terms.

The ignored artifact `results/diagnostics/bem-exact-sphere-cbie-partition-sensitivity-20261008.json` has SHA-256 `0504b92b7eced8dd3db87c225c08baa530869fca216e12b2487543ed6133dfb8`. It binds source `f02a4b1b6ad6880b6d3b9a7f5d5ea5e06e18a808`, script SHA-256 `ea0834f554bc18969e869c5badc3ab1d5bea3848d042a0b96d3c349e4a7e8ac1`, ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`, runtime/environment data, individual term values, repeat checksums and timings, and peak RSS `775208` platform units. Slowest repeat: `11.7972 s`. Local Quality passed 1,838 tests in `1,328.03 s`. Exact GitHub Quality run [37721237477](https://github.com/Andioratech/AURA/actions/runs/37721237477) is associated with this source commit.

## Results

Normalized CBIE residual magnitude by boundary-pressure magnitude:

| Angle | Split factor 6 | Split factor 8 | Split factor 10 | Active subintervals |
| --- | ---: | ---: | ---: | ---: |
| 120° | 2.98492847e-5 | 2.98492847e-5 | 2.98492847e-5 | 1 / 1 / 1 |
| 135° | 1.91461093e-5 | 1.91461093e-5 | 1.91461093e-5 | 1 / 1 / 1 |
| 175° | 1.54520966e-6 | 1.77867281e-6 | 1.67805151e-6 | 2 / 2 / 2 |
| 179° | 2.68706567e-6 | 3.79206446e-6 | 4.70253724e-6 | 2 / 2 / 2 |

At 120° and 135°, all three factors clip to the same single active interval and produce identical binary64 terms. At 175° and 179°, there are two active intervals at every factor, but moving the cutoff changes their endpoints and the direct terms. Relative to factor 8 and normalized by `|p(x)|`, factor 6/10 changes the direct single layer by `2.25e-6 / 2.34e-6` and direct double layer by `1.10e-6 / 1.14e-6` at 175°. At 179° those changes are `3.39e-6 / 4.45e-6` for the direct single layer and `3.11e-6 / 4.08e-6` for the direct double layer. The corresponding image-layer changes are smaller in this case set: up to `2.84e-13 |p(x)|` for the image single layer and `1.46e-9 |p(x)|` for the image double layer.

## Limits and next step

This confirms sensitivity to the meridian cutoff at the near-plane points, especially 179°, and no sensitivity for the clipped one-panel cases at 120°/135° under these factors. It does not establish which factor is accurate, a quadrature error bound, field accuracy, or an acceptance tolerance. The order cap 256 is unchanged; no matrix or solver was allocated. NUM-03 remains ACTIVE/INDETERMINATE, its qualification plan DRAFT, BEM preflight unauthorized, and Hasegawa the selected P4 method.

**Next bounded task:** at fixed cutoff factor 8, direct/image azimuth counts 4,096/2,048, and maximum supported order 256, compare composite subdivisions 1/2/4 of each active meridian subinterval. Preserve the full-grid residual and each layer, active-panel counts, repeats/checksums, timings and failures. This is a quadrature-refinement comparison only; do not exceed the singular-panel cap, infer an error bound or field acceptance, or allocate a matrix.
