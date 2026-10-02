# ANA-07 Recorded Field Matrix

**Protocol:** ANA-REF-1.0 · **Matrix contract:** ANA-07-MATRIX-1.0 · **Source:** `260c73064dec57093339c033b3f0ad5273204c28` · **Status:** software verification PASS; physical validation NOT ESTABLISHED

## Question and scope

This campaign checks whether the versioned AURA recorder preserves and checks the frozen ideal field cases B-03 through B-06. For each case, the recorder evaluates the declared field, stores coordinates, pressure, velocity, pressure gradient and run provenance, and the independent analyzer compares every stored component and derived time-mean intensity against its frozen Decimal reference.

It tests software against manufactured mathematical fields in the declared homogeneous, stationary, linear, lossless regimes. It does not test an acoustic radiator, measured water, body coupling, force, object motion, larger-object scaling or microgravity feasibility. `physical_validation` therefore remains `NOT_ESTABLISHED`.

## Frozen campaign result

All **32 of 32 configurations** completed, all 32 bundles passed read-only integrity checks, and every frozen numerical comparison passed. The campaign compared **264 sample points**: B-03, 11 configurations/59 points; B-04, 8/157; B-05, 8/32; and B-06, 5/16. The existing tolerance was unchanged at `2048 × 2^-52 = 4.547473508864641e-13` normalized error.

| Quantity | Largest normalized maximum error | Case | Largest normalized RMS error |
|---|---:|---|---:|
| Pressure | `9.020562075079397e-16` | B04-EQUAL | `4.898587196589413e-16` |
| Fluid velocity | `7.940933880509066e-16` | B04-EQUAL | `2.828200636599751e-16` |
| Pressure gradient | `7.599405318910162e-16` | B04-EQUAL | `2.8282006365997516e-16` |
| Mean intensity | `1.5881867761018131e-16` | B03-PHASE-GRID | `5.376037651160876e-17` |

The five B-06 cases—axial, directional, common phase, translated center and zero drive—each passed execution, bundle integrity and all four numerical criteria. Their largest maximum errors were `2.759772070643229e-16` in pressure, `1.6274214935057072e-16` in velocity, `1.2952055626919918e-16` in pressure gradient and `1.1911400820763599e-16` in mean intensity; all occurred in B06-DIRECTIONS.

## Independent fresh reproduction

`B06-AXIAL` was rerun from its stored Scenario, Experiment and request at source revision `1d6efb0b17fa95a95b36d8d1d769e8896981688f`. Its three input hashes, four field-artifact hashes and numerical metrics exactly match the original matrix run. The report is marked `PASS`, and the original and replay bundles both pass their recorded-integrity checks.

## Reproducibility anchors

- Campaign index: local ignored output `results/verification/ANA-07/ANA-07-MATRIX-ANA-REF-1.0-260c730/index.json`; SHA-256 `d6352e8c929d22066c40dc55765f7334804a2d54d2ef10bb04fbc4c4166729d3`.
- Fresh reproduction: local ignored output `results/verification/ANA-07/REPRO-B06-AXIAL-1d6efb0/reproduction.json`; SHA-256 `7cb53754a80cc6804af60085f9ed960250338ffdbaa1e80a701907bd1a2e6618`.
- Frozen fixture and reference source hashes, every input/output checksum, per-case error records, resource estimates and run manifests are retained in the indexed local campaign tree. Generated bundles remain outside Git.
- Maximum recorded runtime: `3.5012 s`; maximum bundle size: `111,491 bytes`; maximum RAM preflight estimate: `1,008,906,240 bytes` under the declared 4 GiB cap. These are observations of this campaign, not calibrated solver costs.
- Implementation commit: [`260c730`](https://github.com/Andioratech/AURA/commit/260c73064dec57093339c033b3f0ad5273204c28); exact [Quality run 37066889054](https://github.com/Andioratech/AURA/actions/runs/37066889054) passed with 1,385 tests. Spherical-replay wording correction: [`1d6efb0`](https://github.com/Andioratech/AURA/commit/1d6efb0b17fa95a95b36d8d1d769e8896981688f); exact [Quality run 37067239654](https://github.com/Andioratech/AURA/actions/runs/37067239654) passed.

## Interpretation and remaining gate

This result shows that the recorder and analytic field implementation agree with the independent frozen equations at the tested cases and samples within the existing software tolerance. It does not establish that the ideal models represent a physical source or an experiment. The independent artifact review, remaining precision/cancellation and model-local post-audits, plotted-data review, and formal P3 gate review remain required before ANA-07 can close. No force or motion calculation is promoted by this matrix.
