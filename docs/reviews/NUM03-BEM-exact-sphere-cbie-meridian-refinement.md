# NUM-03 Exact-Sphere CBIE Meridian-Order Refinement Review

**Status:** finite quadrature sensitivity; no acceptance gate or physical validation. **Date:** 2026-10-08 UTC.

## Protocol and reproducibility

The clean-source ENV-1.0 sweep holds direct/image azimuth counts at 4,096/2,048 and varies Gauss-Legendre order per active meridian subinterval at 128/192/256. It evaluates the centered-monopole rigid-plane Neumann trace on the exact sphere (`a=25 mm`, gap `0.1 mm`, `f=25,230 Hz`, `c=346 m/s`) at 120°, 135°, 175° and 179°. All 12 cases completed twice with matching repeat checksums. Every residual reconstructs exactly from the separately recorded jump and direct/image double- and single-layer terms.

The implementation permits product-integration order only through 256 in `_bem_singular._panel_inputs`; 384/512 cannot be used without changing and separately qualifying that component. Two initial harness attempts are retained rather than hidden: the first (source `02cff1a5a449bf11e7648a4b0017238b6396bc7f`, artifact SHA-256 `112e6701f056430eb1b96b749e8e84209b9d2239e7018d0fff7e5c77578a5b2e`) completed the 120°/order-256 case, then hit the old benchmark's frozen level check at 384; the second (source `3b91359866f949171c312571ae61512ed3df5232`, artifact SHA-256 `5409a4d331182dc4575602673a158d7f1ed49905dcfe43955cf84c112a0144c1`) completed that same case, then was rejected by the explicit product-integration cap at 384. These are harness/contract failures, not physical outcomes. The corrected run uses supported orders only.

The completed ignored artifact `results/diagnostics/bem-exact-sphere-cbie-meridian-refinement-20261008-03.json` has SHA-256 `b5b89572df9300202524f41a654ac9c69b7389ce91d2b10f0e233eeb5fe36d5c`. It binds clean source `d9141fd19df4592d63ec6ba2a2d6a64e96ee75ab`, script SHA-256 `8cfee6f530915964e7184fa7b7aa1b7a9f72782424615f8e374adb6ab40e2d18`, ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`, runtime/environment metadata, case checksums/timings and peak RSS `775208` platform units. The slowest repeat took `9.4223 s`. Local Quality passed 1,836 tests in `1,124.40 s`; exact GitHub Quality run [37717168918](https://github.com/Andioratech/AURA/actions/runs/37717168918) passed for the harness source.

## Results

Normalized CBIE residual magnitude by boundary-pressure magnitude:

| Angle | Meridian 128 | Meridian 192 | Meridian 256 |
| --- | ---: | ---: | ---: |
| 120° | 7.62797e-5 | 1.81146e-5 | 2.98493e-5 |
| 135° | 1.87307e-5 | 2.99964e-5 | 1.91461e-5 |
| 175° | 7.02808e-6 | 1.51359e-6 | 1.77867e-6 |
| 179° | 1.02240e-5 | 4.45430e-6 | 3.79206e-6 |

The residual is nonmonotone across the tested orders at 120°, 135° and 175°. At 179° it decreases across this finite sequence. Direct single-layer changes normalized by `|p(x)|` are `9.64993e-5`, `1.24597e-5` at 120°; `1.10370e-5`, `5.00004e-5` at 135°; `5.72926e-6`, `1.80157e-7` at 175°; and `8.37028e-6`, `3.45002e-7` at 179° for 128→192 and 192→256, respectively. The layer changes themselves are nonmonotone too. Increasing the meridian order therefore does not uniformly reduce the residual or each layer difference in this tested range.

## Limits and next step

The observed behavior establishes unresolved meridian-rule sensitivity in this finite calculation. It does not establish a quadrature error bound, field accuracy, a universal order requirement, a pass/fail tolerance, or a physical result. The product-integration order cap of 256 remains in force; this sweep did not alter it. NUM-03 stays ACTIVE/INDETERMINATE, its qualification plan remains DRAFT, BEM preflight remains unauthorized, and Hasegawa remains the selected P4 backend. No matrix or solver was allocated.

**Next bounded task:** test the fixed meridian panel partition itself by varying only its cutoff multiplier at 6/8/10 while holding order 256 and direct/image azimuth counts 4,096/2,048 at the same four angles. Preserve active-subinterval counts, layer terms, residuals, repeats/checksums, timings and failures. Treat this as partition sensitivity only; do not select a universal factor or order, and do not allocate a matrix.
