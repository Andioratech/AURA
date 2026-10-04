# Next Main Task — Qualify NUM-03 Reference Uncertainty

**Prepared:** 2026-10-05 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Current published source revision:** `bbf666660344315325e3bd47dea8240ecbb487be` (GitHub Quality [37236915200](https://github.com/Andioratech/AURA/actions/runs/37236915200) passed) · **Targeted diagnostic revision:** same · **Local diagnostic environment:** ENV-1.0 / CPython 3.12.14

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

The evidence audit and the comparison method that can be fixed without inventing a requirement are recorded in the [NUM-03 field-error protocol basis](../research/NUM-03-field-error-protocol.md). A numeric pass/fail budget is not currently derivable: P1.3 supplies figure-derived force values, not a field-accuracy requirement or measured field reference. Preserve that distinction and continue bounded qualification of reference/error sources. Do not begin broad NUM-04 until the listed preconditions are satisfied. Keep complex pressure, vector particle velocity and pressure gradient separate; use fixed coordinates, SI absolute-error summaries, no phase fitting, and report each uncertainty source separately.

Do not infer force, acceleration, hardware performance or gravity equivalence from the field bounds. A future arbitrary-gap claim needs its own bound or validated interpolation method.

DEC-007 selected a field-only numerical budget and deferred force/acceleration budgets; it did not select a tolerance. Do not borrow the unrelated 2% simple-wave proposal or infer a threshold from the computed tail bound. Retain the [NUM-01 method fallback](../research/NUM-01-method-comparison.md) if the chosen requirement cannot be supported by the current series or resource envelope.

## Latest bounded reference check — 2026-10-05

The exact next step is no longer to draft comparison metrics; the protocol basis already records those. A 300-digit Decimal direct Rayleigh-disk/modal comparison was run at `H=29.9 mm`, order512, using radial rules128/256 on the same 111-point set (37 angles and three radii). Same-order overlap with the public field is about `1.2e-13` for pressure and `6.4e-14` for velocity/gradient. The paired R128/R256 difference is reported around `10^-235`, without analysis that would make it a quadrature error bound. This is one finite grid at one gap and does not establish reference uncertainty for all 300 gaps. See the [protocol basis](../research/NUM-03-field-error-protocol.md), [review](../reviews/NUM-03-coupled-kernel-review.md), and [task record](../work-items/NUM-03.md). The metadata SHA-256 is `a8fad79b6caea510e504ea222df6c41e68f6a2cad86527cf141ef4e7a5493908`; generated artifacts and failure records are local-only.

Continue with a bounded investigation of a reference/quadrature uncertainty method that can be independently justified for the frozen sampled domain. Preserve the failed/mislabeled attempts. Do not begin broad NUM-04, invent a field tolerance, change order/domain, or treat a tiny paired difference as proof of accuracy. If the uncertainty method cannot be supported within the declared model and resource limits, document the failure and revisit the NUM-01 fallback without promoting P4.
