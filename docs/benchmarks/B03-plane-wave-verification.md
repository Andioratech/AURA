# B-03 — Progressive Plane-Wave Numerical Verification

**Date:** 2026-10-02 · **Comparison:** PASS for the bounded kernel tests · **Physical validation:** INDETERMINATE

Protocol: [ANA-REF-1.0](B03-B06-analytical-protocols.md), [PLANE-WAVE-1.0](../research/plane-wave-kernel.md). Source: [`540488c9de6d37984d36b82d7f2a195f07d82b74`](https://github.com/Andioratech/AURA/commit/540488c9de6d37984d36b82d7f2a195f07d82b74). This report concerns numerical software verification, not an experimentally validated acoustic system or a completed P3 scientific run bundle.

## Domain, references and actual execution

One prescribed progressive plane wave in a stationary, homogeneous, inviscid, lossless, unbounded fluid. Manufactured rho=1000 kg/m³, c=1500 m/s, f=1 MHz and peak amplitude 2 Pa (plus explicit zero drive); chamber observation box [-0.0015,0.0015] m on each axis. No body coupling, wall reflection, thermal/viscous response, startup, force, trajectory or gravity response is included.

The [frozen fixture](../../tests/fixtures/fields/B03-plane-wave.json) supplies 11 configurations / 59 observations: axial quarter turns, reversed direction, rational oblique direction, proper rotations, translated phase reference, phase offset, zero drive, a 33-point phase grid, the 4pi argument endpoint and rounding-neighbor points. Separate checks exercise invalid inputs, deliberate wrong answers and a 256-sample maximum workload.

The [independent reference](../../tests/plane_wave_reference.py) uses Decimal sine/cosine/arctangent series and independently differentiated real sinusoids, with no production field/unit/trigonometric calls. Results at 60 and 80 digits agreed to the required 45 decimal places on the normalized scales. Literal quarter-turn answers provide a separate check of both the oracle and production conventions. This arithmetic independence does not constitute independent experimental or physical-model evidence.

The actual clean-source rerun passed **130 tests in 0.26 s**. Full local Quality passed **1,163 tests in 15.27 s**; [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37041107704) passed **1,163 tests in 24.66 s**, including installation, environment verification, lint and required-document checks.

## Measured errors against the independent reference

For each complex component use `abs(actual-reference)/S`; flux uses real component differences. Global RMS pools all listed observations/components, not case averages. The predeclared maximum tolerance is **4.547473508864641e-13** (`2048 * 2^-52`), unchanged after implementation.

| Quantity | Fixed SI normalization S | Component count | Maximum normalized error | Pooled normalized RMS |
|---|---:|---:|---:|---:|
| Pressure | 2 Pa | 59 | 7.044814e-16 | 2.251943e-16 |
| Fluid velocity | 1.3333333333333334e-6 m/s | 177 | 7.102587e-16 | 1.347718e-16 |
| Pressure gradient | 8377.580409572782 Pa/m | 177 | 7.044814e-16 | 1.327009e-16 |
| Mean energy flux | 1.3333333333333334e-6 W/m² | 177 | 1.588187e-16 | 2.924089e-17 |

Values above are rounded for display; JUnit retains each case's actual scales, all component errors, maxima and RMS values. The zero-drive outputs were exactly zero. Trigonometric evaluation at the actual binary64 arguments had maximum absolute error **5.111426200034357e-17**, below the separate `4e = 8.881784197001252e-16` backend assumption. This checks those selected arguments on the observed platform; it is not a universal libm guarantee.

Reverse direction, rotations, translated coordinates, phase/time sign, pressure/velocity impedance and Euler consistency passed. Deliberately conjugated pressure, an erroneous RMS factor, reversed velocity and missing gradient exceeded the frozen budget as required. Invalid geometry/types/loss/samples/resources are rejected before trig and field allocation. Huge phase-reference cancellation and nonrepresentable arithmetic raise typed errors. These are intentional rejection outcomes, not discarded scientific failures.

## Resource observation

For the separate 256-point evaluation plus encoding: **471,333 bytes** peak traced Python allocation against the 1,052,672-byte incremental estimate; **52,220 bytes** combined component encoding against the 294,912-byte allowance; **0.09556 s** evaluation/encoding elapsed in this trace-enabled test. Whole test-process peak RSS was **35,479,552 bytes**, including interpreter/test imports; it is not incremental kernel memory. The frozen fixture maximum remains N=256, one CPU, no GPU, no randomness. These observations do not calibrate a full physical-run recorder, PDE solver or larger campaign.

## Retained software report identity

Verification ID: `VERIFY-ANA02-ab2d94ba14b14be388bc807b55d341d4`.

The ignored local folder is `results/verification/ANA-02/VERIFY-ANA02-ab2d94ba14b14be388bc807b55d341d4/`, retained with this checkout and the shared working copy. It contains the actual JUnit report/log, exact fixture/protocol/test copies, complete observed ENV-1.0 profile/locks, clean-source observation and local Quality log. Source/environment were observed before and after the test invocation and agreed. `verification.json` indexes raw-file digests and labels the report as software verification, not a RunManifest. No D07 scientific run ID, physical driver acceptance or model-validation verdict is fabricated.

| Artifact | SHA-256 |
|---|---|
| `verification.json` | `a7a14c617b7607bad0f30c84f50e73690b073f37e8d87f4da43ad201e9e568f8` |
| `benchmark.xml` | `f91af778ee10b8e0b0a9c379fda5b6c5721fe0b3933edae5c63d7b462eafd299` |
| `B03-plane-wave.json` | `a2272a84fcbaaca86a4dd73af9c76d9a05d30ff4a0316e4d0fcad2a776721f64` |

Independent `sha256sum` matched these retained digests. Generated report data stays out of Git; the committed fixtures and tests plus the locked environment reproduce the calculation. On the exact source revision run `pytest tests/test_plane_wave.py -o junit_family=xunit1 --junitxml=<unused-local-path>`. Timing/RSS and JUnit timestamps are observational, so regenerated report hashes need not match; the frozen numerical comparisons must pass. Archive reconstruction and recorder replay remain RUN-02.

## Interpretation and remaining gates

The ideal single-wave kernel meets its declared numerical checks on this matrix. No executed functional test failed and no tolerance was loosened. [The artifact review](../reviews/ANA-02-plane-wave.md) closes ANA-02 and opens ANA-03.

P3 remains open. Standing/interfering fields, source spreading, independent balances, physical driver admission with FIELD-1.0 provenance/gradient linking, and the complete recorded matrix remain mandatory before ANA-07 closes P3. Water measurements and applicability to real particles, larger masses, other objects and microgravity require their own models and evidence. Small numerical error here is not a physical-accuracy or feasibility claim.
