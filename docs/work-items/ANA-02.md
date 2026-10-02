# ANA-02 — Progressive Plane-Wave Kernel

**State:** ACTIVE · **Protocol frozen:** 2026-10-02 · **Owner role:** research implementer

## Authority, question and boundary

Starting revision: `d1786fab020c1b6c23386299cfaa9bbb53b1cccd`. ANA-01 is DONE and P2 is PASS. Apply D00, D02, D04–D09, FIELD-1.0, ANA-REF-1.0, EQ-006/007/009 and DEC-003/004. The question is whether a bounded single-wave kernel reproduces independently known pressure, fluid velocity, pressure gradient and period-mean flux.

This card implements the named kernel, B-03 fixtures/tests and maximum/RMS error report. No physical driver is admitted to `aura run` here. Tests are software verification executions, identified by commit, fixture hashes and CI/job identity; they are not D07 scientific run bundles. FIELD-1.0's input/index/provenance/checker admission requirements remain mandatory before the ANA-07 evidence campaign. RUN-1.0 remains diagnostic-only; kernel availability never makes a scenario scientifically accepted.

## Frozen implementation and numerical protocol

- Add `fields/analytic.py`: an explicit immutable plane-wave specification, direct evaluation at ordered chamber points, and pressure/velocity mean-flux calculation. Return FIELD-1.0. Do not implement source superposition, scattering, force, motion or control.
- Require positive rho/c/f, nonnegative peak amplitude, explicit phase/reference point/direction and explicit zero viscosity/attenuation. The model is stationary, homogeneous, linear, inviscid, lossless and unbounded. Finite boxes specify observation windows, not reflecting boundaries. No body/material/gravity response or transient startup is simulated.
- Freeze [the kernel contract and derivation](../research/plane-wave-kernel.md) before evaluation. Reject malformed/nonfinite input, non-unit direction, unsupported loss, more than 256 samples, points outside the explicit observation box, unrepresentable arithmetic and excessive phase/coordinate conditioning before producing field arrays. No automatic normalization, clipping, phase wrapping or guessed missing physical values.
- Execute every B-03 quarter-turn/direction/rotation/translation/phase/zero-drive requirement. Add a declared 33-point finite phase grid and bounded rounding-neighbor cases to test elementary functions and phase conditioning; no parameter search. Keep the total below ANA-REF-1.0's 32 configurations.
- Build the reference under tests using Decimal arithmetic at 60 and 80 digits, a independently derived pi through convergent arctangent series and bounded Taylor sine/cosine. It must not import production field or unit helpers. Check exact hand values separately. Compare 60/80-digit results and record truncation/rounding assumptions.
- Preserve the frozen `2048 * 2^-52` scale-normalized tolerance for complex field components and real flux; report both maxima and RMS. Verify the separate <=4e sine/cosine backend assumption at the actual bounded binary64 arguments. Audit the production arithmetic path against the frozen 32-operation/8pi-conditioning assumptions. No percentage experimental-accuracy claim follows.
- Add rejection, mutation and metamorphic tests. A wrong spatial sign, peak/RMS factor, direction, missing gradient or wrong real-time sign must be detectable by the fixtures. Keep the oracle independent of the production implementation.
- One CPU process, no GPU, no randomness, at most 256 points/evaluation; explicit workspace estimate `4096*N + 4096` bytes with a 2 MiB caller budget in verification, plus interpreter/test overhead. Bound the oracle to 256 iterations per series; benchmark tests <10 s, full suite <60 s. Preserve and investigate overruns; no unbounded precision search.
- No new dependency. Complete current local CI before every commit, confirm exact remote CI after push, then reproduce the benchmark tests from the published clean source and record the reviewed outcome in a separate commit.

## Expected artifact paths and review

`src/aura/fields/analytic.py`; `tests/fixtures/fields/B03-plane-wave.json`; `tests/plane_wave_reference.py`; `tests/test_plane_wave.py`; the kernel contract and a bounded B-03 numerical report/review. Existing schema and MCLF rules remain unchanged. Scientific uncertainty/model coverage remains INDETERMINATE; measurement and larger-body evidence retain their named LIT/FOR/SC owners.

Close ANA-02 only when its numerical comparisons and rejection checks actually pass and the published CI agrees. ANA-03 then becomes READY; P3 does not close until the recorder-based matrix, audits and evidence required by ANA-07 exist.

## Development verification before publication

The first focused numerical/rejection suite passed 128 tests in 0.18 s. Adding the maximum-size allocation/encoding check brought it to 129 passes in 0.31 s. Its development JUnit report `/tmp/aura-ana02-development-01.xml` retains all per-case component errors and resource observations; this is a dirty-tree development check, not the clean-source publication record. A further independent complex-vector flux case and the updated CLI status contract are included in final verification. No executed functional check failed and no acceptance threshold was changed.

The 11 frozen configurations include 59 observation points in total, plus separate maximum-size/resource and rejection checks. The initial comparisons were below the frozen 2048e budget; the maximum elementary-function error observed was below the separately required 4e bound. The final published-source numerical/resource values and retained report identity are recorded in the closure review.
