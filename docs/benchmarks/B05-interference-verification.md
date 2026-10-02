# B-05 — Coherent Two-Wave Numerical Verification

**Date:** 2026-10-02 · **Comparison:** PASS for the bounded kernel matrix · **Physical validation:** INDETERMINATE

Protocol: [ANA-REF-1.0](B03-B06-analytical-protocols.md), [TWO-PLANE-WAVES-1.0](../research/two-wave-kernel.md). Implementation source: [`6bd45bdec28f37f6e00512664ff9510f68e6f818`](https://github.com/Andioratech/AURA/commit/6bd45bdec28f37f6e00512664ff9510f68e6f818). These are numerical software checks, not physical recorder runs, experimental data or a completed P3 campaign.

## Domain, matrix and reference

Two coherent prescribed incident plane waves at 1 MHz in an unbounded homogeneous, stationary, linear, inviscid and lossless fluid. Manufactured rho=1000 kg/m³, c=1500 m/s, wavelength=0.0015 m; explicit peak amplitudes 0, 2 or 4 Pa. Cube observation box [-0.0015,0.0015] m on each axis. Harmonic time convention exp(-i omega t); flux averaged over one period. No walls, finite radiator, body interaction, heating, streaming, motion or gravity response is represented. The coefficients are not a measured water-state calibration.

The [frozen fixture](../../tests/fixtures/fields/B05-interference.json) supplies **eight configurations / 32 observations**. Four samples each cover the axial B-05 table, a proper rotated copy, a common pi/2 phase, common translation by (lambda/8,lambda/8,0), oblique nonorthogonal directions, unequal amplitudes with differing phases, zero drive and the single-source limit. Unit checks separately exercise different reference parameterizations, neighboring binary64 node coordinates, parallel/opposite limits, invalid inputs and a 256-sample resource case. These are fixed tests, not an adaptive search or geometry-wide accuracy certificate.

The [test oracle](../../tests/interference_reference.py) uses independently implemented Decimal trigonometric series and real pressure derivatives, derives velocity through linear Euler, and evaluates flux from the exact period-integral cosine-difference formula. It never calls production field/unit helpers or binary trigonometry. Production adds complex source fields and calculates Re(p*conj(v))/2. The oracle shares only the independent B-03 constant/series primitives. A 60/80-digit comparison agrees to 45 normalized decimal places, and all literal B-05 table values independently check both routes. This arithmetic independence is not an independent physical-model or external-review claim.

## Executed checks and numerical error

The published clean-source rerun passed **65 B-05 tests in 0.32 s**. Full local Quality passed **1,288 tests in 16.30 s**; [exact GitHub Quality](https://github.com/Andioratech/AURA/actions/runs/37046825752) passed **1,288 tests in 13.99 s**, including installation, locked-environment checks, lint and required documents. The existing single-wave and counterpropagating regression suites still pass. No dependency or environment lock changed.

Errors use the complex absolute component difference, or real flux difference, divided by C, C/Z, k*C or C²/(2Z), with C the sum of source peak amplitudes and the original 2 Pa fallback at zero drive. This matrix uses C=2, 4 or 6 Pa. The threshold is the unchanged **4.547473508864641e-13** (2048e). Pooled RMS below includes all observations/components rather than averaging case RMS values.

| Observable | Components compared | Maximum normalized error | Pooled RMS normalized error |
|---|---:|---:|---:|
| Pressure | 32 | 3.140184917e-16 | 1.022108517e-16 |
| Velocity | 96 | 2.246035278e-16 | 5.109598536e-17 |
| Pressure Gradient | 96 | 2.013953969e-16 | 4.888796983e-17 |
| Intensity | 96 | 7.940933881e-17 | 2.472333858e-17 |

Display values are rounded; JUnit retains every component error, scale, maximum and RMS. The actual-argument sine/cosine maximum absolute error was **5.1079145521690476e-17**, below the separate **8.881784197001252e-16** (4e) allowance. These results apply to selected ordinary-scale inputs and the observed platform, not all floating-point arguments or percentage physical accuracy.

## What the cancellation and interference tests establish

For the base +x / +y pair, equal 2 Pa amplitudes and zero phase:

| Observation | Analytical pressure phasor | Analytical fluid velocity phasor (µm/s) | Analytical mean flux (µW/m²) | Observed comparison |
|---|---|---|---|---|
| Origin | 4 Pa | (1.333333, 1.333333, 0) | (2.666667, 2.666667, 0) | PASS within frozen component scales |
| (0, lambda/2, 0) | 0 Pa | (1.333333, -1.333333, 0) | (0, 0, 0) | PASS; nonzero velocity/gradient survive serialization |

Rounded table values illustrate the separately frozen exact reference. The raw serialized fields retain finite numerical residuals rather than clipping them to zero. The second point demonstrates why pressure cancellation cannot erase the rest of the field. It does not establish the force on an object placed there.

At the origin, summing only the two independent source fluxes would give (1.333333,1.333333,0) µW/m², missing the coherent cross term. The incorrect route fails the unchanged tolerance. Deliberately averaging source pressure, summing scalar speed magnitudes, dropping vectors at the pressure node or rotating only sample positions also fails the field comparison. These are expected rejection outcomes, not discarded failed physical experiments.

Interchanging source order preserves the field. The proper cube-preserving rotation transforms vectors and preserves pressure; common translation and properly compensated distinct reference changes preserve the represented field. A common phase multiplies complex fields and leaves mean flux unchanged. The parallel, opposite, zero and single-source limits recover their stated references. The exact-opposite API still rejects crossed directions; general two-wave evaluation has its own explicit API. Invalid second-source input is rejected before either source evaluation, even at zero drive.

## Resource observations and development record

At 256 samples, evaluation plus JSON encoding used **510179 bytes** peak traced Python allocation against **1,056,768 bytes** admitted incremental workspace. Encoded components used **61436 bytes** against **294,912 bytes**. Trace-enabled elapsed time was **0.190807 s**; whole test-process peak RSS was **35377152 bytes**, including interpreter and imports. One CPU process, no GPU and no randomness were used. These observations do not validate future physical recorder/PDE budgets.

The first development B-03/B-04/B-05 execution passed 255 checks in 1.31 s. First-pass lint, functional tests and complete local Quality passed; no numerical failure, hidden retry, tolerance relaxation or fixture adjustment occurred. The development log/JUnit remains indexed with the published report and is labeled separately from clean-source verification.

## Retained reproducibility record

Verification ID: `VERIFY-ANA04-0a7258c2aa2047dc9d3f78cea8176144`.

Ignored local path: `results/verification/ANA-04/VERIFY-ANA04-0a7258c2aa2047dc9d3f78cea8176144/`, retained in the executing checkout and mirrored to the shared workspace. It contains the source/environment observations, all three ENV-1.0 locks, frozen fixture/protocol/contract/task copies, independent oracle and metric-helper source, JUnit/logs, actual field component artifacts and vector flux in `samples.json`, development checks and the report-assembly script. Source/environment observations before and after agreed. All indexed file digests were independently recomputed and matched.

| Artifact | SHA-256 |
|---|---|
| `verification.json` | `ecc673365ddf1e13eb8a7b192dcaaf0eed2e245243343280443a527acfe7dbd9` |
| `benchmark.xml` | `9863836328f49547ce33256112b1601d6849e81ca5aeda284261bf96d7b04c6e` |
| `B05-interference.json` | `61af0cc1d3b28f400808c7b987df931aaa4eccb470c16bcbb70ab7b9d874b0c9` |
| `samples.json` | `8443c6a6dff54a25b69201612952052c71d7fe95e7dfda2dd8f89baf0fa3ba33` |

`verification.sha256` separately retains the index digest. Raw generated outputs stay outside Git. On the exact source and locked environment reproduce the numerical checks with `pytest tests/test_interference.py -o junit_family=xunit1 --junitxml=<unused-path>`. Observational timing/RSS/timestamps may differ; the frozen comparisons must pass. Archived bundles and recorder replay retain their RUN-02 owner.

The index labels this as a software-verification report, not a D07 RunManifest or accepted scientific run. [The artifact review](../reviews/ANA-04-interference.md) closes ANA-04 and opens ANA-05. P3 remains open for spreading, independent balances, FIELD-1.0 physical driver/provenance/gradient admission and the recorded campaign. Model applicability to actual water, particles, larger masses, other geometries and microgravity remains unvalidated under the existing research gates.
