# Next Main Task — Freeze the NUM-03 Field-Error Protocol

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Solver revision:** `f8302cb` (GitHub Quality [37184239104](https://github.com/Andioratech/AURA/actions/runs/37184239104) passed) · **Documentation base before this update:** `3159dfe`

## Current implementation and bounded run

The published Scenario 1.1 Hasegawa adapter keeps Scenario 1.0 unchanged, binds one gap and one ordered chunk of up to 256 samples, retains order cap 512 and domain `a<=r<d`, and requires exact-source/ENV-1.0 NUM-02 calibration before evaluation. The exact-context profile covers one gap, one point and order512 only. Its bounded run has an integrity-verified immutable bundle and an `INDETERMINATE` science verdict; it is not an accuracy or physical-validation pass. Details remain in the [NUM-03 task](../work-items/NUM-03.md) and [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md).

## New modal-tail evidence

Exact-rational candidate bounds cover the ideal-model mathematical order>512 tail for all polar angles and every accepted radius `a<=r<d` at each of the 300 approved P1.3 gap samples, from 0.1 to 30.0 mm in 0.1 mm steps. The source is the conjugated Hasegawa piston series with a stationary sound-hard sphere. These bounds cover the experimental curve's fixed sample gaps; they do not establish a result for arbitrary gap values between them.

| Gap | Potential bound (`|v0|/k`) | Potential-gradient bound (`|v0|`) |
|---:|---:|---:|
| 0.1 mm | `1.809131951558e-16` | `3.737215120957e-14` |
| 10.0 mm | `8.356869464251e-9` | `1.726403422131e-6` |
| 20.0 mm | `1.470307004326e-5` | `3.037578442583e-3` |
| 29.9 mm (largest) | `9.794870592449e-4` | `2.023664973981e-1` |
| 30.0 mm | `8.120926582880e-4` | `1.677821185822e-1` |

The exact-rational sweep checks all 300 geometries; its largest candidate bounds occur at 29.9 mm, so do not assume a monotone increase to the final sample. The full rows are in ignored local `results/research/NUM03-MODAL-TAIL-FOUR-GAP-CANDIDATES-20261004-01/300-gap-sample-candidates/`. Metadata SHA-256 `7654cf9108854caf79a0e414685435ec14a1f48ab03d6dd1fa93e6260bf91e6e`; script/output SHA-256 `ae528997de62fcc78ed78764ac1734bd0f482a9792097b091e4e071fea2894b8` / `19932fe246c6037dda69944c202f79a713c16814a4fc33df2e7cb54f185cf17a`. A repeated execution produced byte-identical output. A separately coded exact-`Fraction` implementation of the four checkpoint cases encloses those prior outputs; all derivations are by the same working agent, not external peer review.

The bounds concern mathematical truncation in the ideal model only; they do not include floating-point error, source-integration error, reference uncertainty or physical-model discrepancy. The 29.9 mm gradient bound is broad and establishes no accuracy threshold. No numerical tolerance has been adopted, so P4 remains `INDETERMINATE`. Preserve the 512 cap, `a<=r<d`, the failed P600/order1600 attempt, and the nonmonotone finite-order evidence.

## Next authorized work

1. Derive a target-specific basis for the field-error requirement and reference uncertainty for the approved 300-point P1.3 gap set. The figure-derived force measurements have no pointwise uncertainty, so do not invent a percentage tolerance.
2. Keep complex pressure, vector particle velocity and pressure gradient separate; freeze deterministic field samples, at least three harmonic truncations, independent quadrature/precision checks, acceptance/stopping rule and workload-specific resource cap.
3. Use fixed-grid norms and maximum absolute local error in SI units, without phase fitting or singular relative errors at nodes. Report modal truncation, floating-point and reference numerical uncertainty separately.
4. Keep NUM-04 BLOCKED until those inputs are recorded. Do not infer force, acceleration, hardware performance or gravity equivalence from the field bounds. A future arbitrary-gap claim needs its own bound or validated interpolation method.

DEC-007 selected a field-only numerical budget and deferred force/acceleration budgets; it did not select a tolerance. Do not borrow the unrelated 2% simple-wave proposal or infer a threshold from the computed tail bound. Retain the [NUM-01 method fallback](../research/NUM-01-method-comparison.md) if the chosen requirement cannot be supported by the current series or resource envelope.
