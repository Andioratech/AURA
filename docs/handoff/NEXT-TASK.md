# Next Task — Meridian Partition Sensitivity for the Exact-Sphere CBIE

## Latest completed bounded task — 2026-10-08

The clean-source ENV-1.0 sweep holds direct/image azimuth counts at 4,096/2,048 and varies Gauss-Legendre order per active meridian subinterval at 128/192/256. Four angles (120°, 135°, 175°, 179°) and two repeats per case give 12 completed cases with matching checksums; each CBIE residual exactly reconstructs from the stored jump and layer terms.

Normalized residual magnitudes across meridian orders 128/192/256 are: 120° `7.62797e-5 / 1.81146e-5 / 2.98493e-5`; 135° `1.87307e-5 / 2.99964e-5 / 1.91461e-5`; 175° `7.02808e-6 / 1.51359e-6 / 1.77867e-6`; 179° `1.02240e-5 / 4.45430e-6 / 3.79206e-6`. The result is nonmonotone at the first three angles. Direct single-layer changes also vary nonmonotonically, notably from order 192 to 256 at 135°. This is finite sensitivity for one configuration and sample set; it is not an error bound, convergence result, field acceptance or physical evidence.

Orders 384/512 were explicitly refused by the product-integration cap in `_bem_singular._panel_inputs` (maximum 256). Two rejected diagnostic attempts are preserved locally: `results/diagnostics/bem-exact-sphere-cbie-meridian-refinement-20261008.json`, SHA-256 `112e6701f056430eb1b96b749e8e84209b9d2239e7018d0fff7e5c77578a5b2e`, and `...-02.json`, SHA-256 `5409a4d331182dc4575602673a158d7f1ed49905dcfe43955cf84c112a0144c1`. The first hit an outdated explicit-level guard; the second reached and confirmed the singular-panel cap. Neither is discarded or treated as a physical failure.

The completed artifact `results/diagnostics/bem-exact-sphere-cbie-meridian-refinement-20261008-03.json` has SHA-256 `b5b89572df9300202524f41a654ac9c69b7389ce91d2b10f0e233eeb5fe36d5c`, source `d9141fd19df4592d63ec6ba2a2d6a64e96ee75ab`, script SHA-256 `8cfee6f530915964e7184fa7b7aa1b7a9f72782424615f8e374adb6ab40e2d18`, and ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`. Local Quality passed 1,836 tests in 1,124.40 s. Full values, failures and scope are in [the review](../reviews/NUM03-BEM-exact-sphere-cbie-meridian-refinement.md).

## Next bounded task

Test sensitivity to the fixed meridian partition by varying only the cutoff multiplier at 6/8/10, while keeping meridian order 256, direct azimuth count 4,096 and image azimuth count 2,048. Use the same geometry and angles. Record active-subinterval counts, separate layer terms, residuals, repeats/checksums, timings and failures under clean source and ENV-1.0. Treat differences as finite partition sensitivity only. Do not select a universal factor or order, change the product-integration cap, allocate a matrix or start a solver. NUM-03 remains ACTIVE/INDETERMINATE, its qualification plan DRAFT, P4 unpassed, and BEM preflight unauthorized; Hasegawa remains the selected P4 method.
