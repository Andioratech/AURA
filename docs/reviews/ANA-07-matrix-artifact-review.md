# ANA-07 Matrix Artifact Review

**Review scope:** ANA-07-MATRIX-1.0 bundles and independent comparison reports · **Source revision:** `260c73064dec57093339c033b3f0ad5273204c28` · **Disposition:** accepted for scoped software-verification evidence; P3 remains open

## Checks performed

- Confirmed the index binds 32 unique frozen configurations to the source revision and campaign-runner checksum.
- Confirmed all 32 executions completed, all bundles report `VERIFIED`, and all 32 independent reports return numerical `PASS`.
- Confirmed the matrix covers the exact frozen counts B-03/B-04/B-05/B-06 = 11/8/8/5 and compares 264 samples without changing the ANA-REF-1.0 tolerance.
- Confirmed the packaged B-06 fixture is byte-identical to `tests/fixtures/fields/B06-spherical.json`.
- Confirmed each report binds its manifest digest, output artifact checksums, exact frozen fixture checksum, metric-code checksum and independent-reference checksum.
- Confirmed the fresh B06-AXIAL replay is anchored to the campaign index and reproduces all three input hashes, four field hashes and numerical metrics exactly.
- Confirmed generated bundles, reports and campaign index remain in the ignored local `results/` tree rather than Git.
- Confirmed the implementation commit and replay-tool correction both passed exact-head GitHub Quality. Local full Quality passed with 1,385 tests, Ruff, environment verification, dependency checks and required-document checks.

## Findings and limits

No missing bundle, checksum mismatch, numerical criterion failure or unexpected case was found in the reviewed campaign. Numerical errors remain far below the frozen software tolerance. Resource estimates are conservative contract values; recorded duration and bundle size are observations for this environment only.

This review verifies the integrity and consistency of the retained software evidence. The checker does not authenticate the publisher or recalculate the equations. The manufactured fields are not measurements, and this review provides no independent physical validation, source calibration, body-force result, object-motion result or microgravity evidence.

ANA-07 remains **ACTIVE** until the remaining model-specific post-audits and precision/cancellation review are completed, any required plots are checked against the machine-readable metrics, and the formal P3 gate review is recorded.
