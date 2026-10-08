# Next Task — 179° Composite Meridian Subdivision Check

## Latest completed bounded task — 2026-10-08

The clean ENV-1.0 sweep tested eight composite subdivisions at fixed cutoff factor 8, per-panel order 256, direct/image azimuth counts 4,096/2,048 and four angles. All four cases completed twice with matching checksums and exact residual reconstruction. The 1/2/4 results remain in the prior immutable artifact.

Normalized residuals at subdivision 8 are: 120° `5.05170284e-7`, 135° `2.54920634e-9`, 175° `3.72120393e-8`, and 179° `4.46046500e-7`. Compared with subdivision 4, the residual decreases at 120° and 175°, is essentially unchanged at 135°, and increases at 179° (`2.9054e-7` to `4.4605e-7`). At 179°, normalized direct double/single-layer changes from 4 to 8 subdivisions are `7.483e-8` and `8.130e-8`; image-layer changes are around `1e-15`. This shows why residual magnitude alone cannot establish convergence. The order-256 logarithmic restoration remains fixed over the full interval.

Artifact `results/diagnostics/bem-exact-sphere-cbie-composite-subdivision-8-20261008.json` has SHA-256 `d466ecb4da3b5b059adca08f70c814e35afa1029fd1e0c27362c772df0056262`, source `63a3be4776be927cde292b4c4a872a5a277abd4e`, script SHA-256 `39dc0053893fe67966756ae0abc16210ba4f21df5e87b85678e203d98b9008d4`, and ENV-1.0 lock aggregate `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`. Each action took 31.77–69.84 s. Local Quality passed 1,842 tests in 1,339.87 s. See [the review](../reviews/NUM03-BEM-exact-sphere-cbie-eight-subdivision.md) for complete values and limits.

## Next bounded task

At 179° only, test 10 composite subdivisions with factor 8, order 256 per panel and direct/image counts 4,096/2,048, using two repeated actions. Record separate layer terms, residual, timings and checksum under clean source and ENV-1.0. Compare against the immutable 1/2/4 and 8 artifacts; do not tune toward a target residual or claim convergence. Keep the full-interval logarithmic restoration at order 256. No matrix or solver; NUM-03 remains ACTIVE/INDETERMINATE, plan DRAFT, P4 unpassed and BEM preflight unauthorized; Hasegawa remains selected.
