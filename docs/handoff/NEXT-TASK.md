# Next Task — Composite Meridian Subdivision Sensitivity

## Latest completed bounded task — 2026-10-08

The clean ENV-1.0 sweep varied only the meridian cutoff multiplier (6/8/10) at fixed meridian order 256, direct/image azimuth counts 4,096/2,048, and four angles. All 12 configurations completed twice with matching checksums; every CBIE residual reconstructs exactly from the recorded jump and layer terms.

Normalized residual magnitudes by factor 6/8/10 are: 120° `2.98492847e-5 / 2.98492847e-5 / 2.98492847e-5`; 135° `1.91461093e-5 / 1.91461093e-5 / 1.91461093e-5`; 175° `1.54520966e-6 / 1.77867281e-6 / 1.67805151e-6`; 179° `2.68706567e-6 / 3.79206446e-6 / 4.70253724e-6`. At 120° and 135° all factors produce the same clipped single interval and identical values. At 175° and 179° direct layer terms change with the cutoff; the image terms change much less. This is finite quadrature sensitivity for one configuration, not evidence that any factor is accurate or sufficient.

Artifact `results/diagnostics/bem-exact-sphere-cbie-partition-sensitivity-20261008.json` has SHA-256 `0504b92b7eced8dd3db87c225c08baa530869fca216e12b2487543ed6133dfb8`, source `f02a4b1b6ad6880b6d3b9a7f5d5ea5e06e18a808`, script SHA-256 `ea0834f554bc18969e869c5badc3ab1d5bea3848d042a0b96d3c349e4a7e8ac1`, and ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`. Local Quality passed 1,838 tests in 1,328.03 s. Exact CI run [37721237477](https://github.com/Andioratech/AURA/actions/runs/37721237477) validates the source commit; the [review](../reviews/NUM03-BEM-exact-sphere-cbie-partition-sensitivity.md) contains the complete comparison and limitations.

## Next bounded task

At fixed cutoff factor 8, direct/image azimuth counts 4,096/2,048 and maximum supported meridian order 256, compare composite subdivisions 1/2/4 of each active meridian interval. Record active-panel counts, layer terms, residuals, repeats/checksums, timings and failures under clean source and ENV-1.0. Keep the singular-panel order cap at 256. Treat differences as finite quadrature sensitivity only; do not choose an accuracy threshold, infer an error bound, allocate a matrix or start a solver. NUM-03 remains ACTIVE/INDETERMINATE, plan DRAFT, P4 unpassed and BEM preflight unauthorized; Hasegawa remains the selected P4 method.
