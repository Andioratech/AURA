# B-06 — Ideal Spherical Spreading Verification

**Date:** 2026-10-02 · **Comparison:** PASS within the amended frozen kernel matrix · **Physical validation:** INDETERMINATE

Protocol: [ANA-REF-1.0](B03-B06-analytical-protocols.md), [SPHERICAL-WAVE-1.0](../research/spherical-wave-kernel.md), [ANA-05 amendment A1](../work-items/ANA-05.md). Published implementation: [`951af42b3c06b577590f493d55185079db468b1e`](https://github.com/Andioratech/AURA/commit/951af42b3c06b577590f493d55185079db468b1e). These are software numerical checks, not physical recorder runs or the completed P3 campaign.

## Domain and independent reference

One ideal outgoing spherical incident wave at 1 MHz in a homogeneous, stationary, unbounded, linear, inviscid and lossless fluid. Manufactured rho=1000 kg/m³, c=1500 m/s, wavelength=0.0015 m, reference/minimum radius=0.000375 m, peak pressure 2 Pa at the reference sphere (0 Pa in the zero-drive case). The observation cube is [-0.0015,0.0015] m on each axis. Harmonic time is exp(-i omega t); flux is the exact one-period mean. No walls, finite radiator, body, absorption, heating, streaming, startup or gravity response is represented. These inputs are not measured water properties. The source-exclusion radius is computational, not a physical applicability certificate.

The [fixture](../../tests/fixtures/fields/B06-spherical.json) contains **five configurations / 16 observations**: three +x radial reference points, four alternate radial directions, common pi/2 phase, center/sample translation and zero drive. Amendment A1 places the oblique positive sample at 2*r_ref; the -x/+y/-z samples remain at r_ref. The total future B-03…B-06 recorder matrix stays at 32 configurations. Separate unit checks exercise representation boundaries, reparameterization of the reference sphere, input rejection and the 256-sample resource cap.

The [independent oracle](../../tests/spherical_reference.py) uses Decimal Machin pi, Taylor sine/cosine, square root, real radial amplitude differentiation and linear Euler for velocity. Flux uses the independently simplified real harmonic period integral. Production directly evaluates the complex field and general Re(p*conj(v))/2. No production field/unit/binary-trig function computes expected values. Agreement at 60/80 digits is better than 45 normalized decimal places. Every literal B06-01…03 component separately checks both oracle and production. These checks provide arithmetic-route independence, not independent experimental validation or external review.

## Executed checks and numerical errors

Clean published-source verification: **63 tests passed in 0.24 s**. Full local Quality: **1,351 passed in 16.56 s**. [Exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37051894964): **1,351 passed in 21.05 s**, including locked installation, environment checks, lint and required documents. Existing plane/interference tests remain passing. No dependency, lock, equation or acceptance tolerance changed.

Use the unchanged **2048e = 4.547473508864641e-13** threshold, e=2^-52. Complex fields use absolute complex-component error; flux uses real absolute error. The global scales are A, (A/Z)*(1+2/pi), k*A*(1+2/pi), A²/(2Z), retaining A=2 Pa at zero drive. Scales never divide by a vanishing local component. Pooled RMS uses all individual component errors, not averages of case RMS values.

| Observable | Components compared | Maximum normalized error | Pooled RMS normalized error |
|---|---:|---:|---:|
| Pressure | 16 | 2.759772071e-16 | 1.018718602e-16 |
| Velocity | 48 | 1.627421494e-16 | 3.761222530e-17 |
| Pressure Gradient | 48 | 1.295205563e-16 | 3.842841762e-17 |
| Intensity | 48 | 1.191140082e-16 | 2.125065471e-17 |

Actual-argument sine/cosine maximum absolute error: **1.6049165500381141e-31**, below 4e. Actual hypot maximum relative error: **6.1904478323605113e-17**, below 2e. JUnit retains every component error, SI scale and resource observation. Displayed values are rounded. The comparisons cover the specified ordinary-scale inputs and observed platform; they do not certify arbitrary floating-point inputs or physical accuracy.

## Distance dependence and attempts to break the calculation

| Radius | Pressure magnitude (Pa) | Radial flux relative to reference |
|---|---:|---:|
| r_ref | 2 | 1 |
| 2*r_ref | 1 | 1/4 |
| 3*r_ref | 2/3 | 1/9 |

All rows pass the frozen component comparisons, including the phase, full radial fluid velocity and pressure gradient. At the reference sphere kr=pi/2, the velocity retains its nonzero quadrature term; substituting only p*n/Z is detected as wrong. Omitting pressure spreading, reversing velocity direction or imposing inverse-distance flux also fails the unchanged comparison. These deliberately corrupted results are expected rejection tests, not discarded experimental failures.

Changing radial direction rotates velocity/gradient/flux while preserving the corresponding pressure. Common translation, common phase and correctly compensated reference-sphere changes obey their stated invariances. Zero drive preserves exact zero fields while still enforcing source and sample validity. Order and duplicates survive. Invalid types, nonfinite values, unsupported nonzero losses, excess sample counts, insufficient budgets, poor coordinate/phase conditioning and unrepresentable arithmetic are rejected explicitly. All source/sample geometry preflight checks precede field evaluation, including an invalid later sample at zero drive.

The source point and points inside r_min are rejected. An axial boundary sample is admitted; its adjacent smaller binary64 neighbor is rejected, without tolerance padding. This strict rule also explains the original oblique boundary failure below. No finite physical source model is inferred from the exclusion.

## Preserved failure, amendment and resources

The first development B-03…B-06 attempt produced **5 failures / 311 passes in 1.42 s**. All failures arose from the original decimal oblique boundary input (0.000225,0.0003,0): its binary64 radius is 0.00037499999999999995, just below the configured minimum 0.000375. The evaluator correctly rejected it under the previously specified strict comparison.

Before retrying, documented **amendment A1** moved the positive oblique comparison and memory sample to (0.00045,0.0006,0), at twice the intended radius. The original input remains a rejection regression. Mandatory axial B-06 tables and -x/+y points, matrix size, mathematical model, tolerances and resource limits are unchanged. The original fixture and full failed log/JUnit are retained alongside the corrected result. The amended regression run passed **317 tests in 1.49 s**. One further reference-sphere/box-face test was added before full CI, yielding 63 new tests and 1,351 total. Development logs are dirty-tree checks; they do not carry an exact captured dirty-source snapshot. The separate published-source verification below does carry an exact clean revision and environment.

At N=256, evaluation plus JSON encoding used **547012 bytes** peak traced Python allocation, below the **1,052,672-byte** incremental budget. Encoded components used **73724 bytes**, below **294,912 bytes**. Trace-enabled evaluation/encoding took **0.153849 s**. Whole test-process peak RSS was **35270656 bytes**, including interpreter/imports. One CPU process, no GPU/randomness. The retained bundle is below 16 MiB; this does not calibrate a future PDE or physical recorder workload.

## Reproducibility and remaining gates

Verification ID: `VERIFY-ANA05-9bfc7d4be81e468e9c4b7ac407ae61d1`.

Ignored local folder: `results/verification/ANA-05/VERIFY-ANA05-9bfc7d4be81e468e9c4b7ac407ae61d1/`, retained in the executing checkout and mirrored to the shared workspace. It includes exact source/environment observations, three ENV-1.0 lock files, fixture/protocol/kernel/task records, oracle/metric-helper/test source, clean-source JUnit/log, raw field component artifacts and vector flux in `samples.json`, development attempts/original fixture, full local CI, exact remote implementation CI and the report-assembly script. Before/after source and environment observations agree. All indexed SHA-256 digests were recomputed and matched.

| Artifact | SHA-256 |
|---|---|
| `verification.json` | `ddba4208d0f3054d7750f97695c6d062ae4311552ee03b5abf1189d5dda04b9e` |
| `benchmark.xml` | `c589f9ea257e451b5a60ddfa36e7f1c7404fa3acb615be2d0082fcdd9ba23bcf` |
| `B06-spherical.json` | `885735cb6057ea8c35e3d5e48abdecc62cb4869c558d87076125964b7b0c4d70` |
| `aura-ana05-fixture-original.json` | `9dce7a71943e6088ede5effe17b7764b1f4c3acbb6f01c7dbf3dcd533c7a92f2` |
| `samples.json` | `1e0561ddf250016a50d39efc2e30dc51307d5456522538f03c52a762ecf104d7` |

`verification.sha256` separately identifies the report index. Generated evidence stays outside Git. Reproduce numerical comparisons on the exact source and locked environment with `pytest tests/test_spherical_wave.py -o junit_family=xunit1 --junitxml=<unused-path>`. Observational timing/RSS/timestamps may differ. This report and samples are software verification artifacts, not D07 RunManifests; recorder replay remains separately owned.

[The implementation self-review](../reviews/ANA-05-spherical.md) closes ANA-05 and makes ANA-06 READY. Formal model-specific balances, physical recorder admission with explicit spherical input/gradient/index/checker contracts and the recorded campaign remain open. P3 is not closed. Actual water, particles, larger masses/objects, other geometries and microgravity retain their separate model and experimental gates. No acoustic force, gravity creation or feasibility claim follows from this result.
