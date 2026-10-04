# DEC-007: Keep the P4 Field Error Budget Separate

**Status:** RECORDED OWNER DECISION · **Date:** 2026-10-04 · **Owner:** AURA project owner

## Request and evidence

NUM-03 needs a defensible field-accuracy criterion before a broad convergence campaign. The project documents require benchmark-specific observables, tolerance derivation, uncertainty and a stopping rule; they reject a universal percentage. The existing one-point order-512 air run is integrity-verified but scientifically INDETERMINATE. Separate high-precision modal comparisons agree with the public implementation at matched orders on finite sample grids, while order-512 versus order-1200 differences reach `1.14e-6` in sampled velocity and pressure-gradient norms at the 30 mm outer shell. Those finite sums are not tail bounds and do not establish convergence.

## Decision

1. Define the P4 numerical acceptance budget for the declared air field observables: complex pressure, particle velocity and pressure gradient. Assess each observable separately.
2. Keep acoustic force, body acceleration, trajectory and controller accuracy budgets for their later applicable gates. A P4 field result will not imply that those downstream quantities meet any accuracy target.
3. Derive any numerical threshold from the named air benchmark, an independently implemented reference with its numerical uncertainty, observable convergence, and an explicitly scoped use requirement. Do not select a universal percentage or reuse the source proposal's 2% simple-wave target.
4. Do not start the next broad convergence or boundary-sensitivity campaign until its sample set, reference-uncertainty method, refinement sequence, acceptance rule and resource cap are recorded. Preserve the current order cap, geometry, domain and evidence until reviewed.
5. If the available reference or numerical evidence cannot support a defensible threshold within the declared method and resource limits, retain INDETERMINATE and reopen the NUM-01 fallback comparison. Do not turn same-order agreement into a convergence or physical-validation claim.

## Options considered

| Option | Scientific benefit | Limitation / consequence | Decision |
|---|---|---|---|
| Set P4 field-only numerical criteria, with later budgets separate | Allows field verification to be assessed on its own observables before force or motion models are chosen | Still requires a defensible field reference, error analysis and use requirement before a number can be frozen | Selected |
| Wait for a downstream force/acceleration budget before defining field accuracy | Could allocate field error backward from a future application target | Delays the independent field gate and couples two different questions | Not selected |
| Adopt a generic percentage now | Easy to state and execute | Conflicts with D00/D03/D06; no evidence in the current diagnostic justifies it | Rejected |

## Consequences and re-entry

- This decision records the tolerance basis only. It adopts no numerical tolerance, does not revise D00-D09, equations, physical assumptions or claims, and does not pass P4.
- NUM-03 remains ACTIVE. The next task is to establish whether the separate high-precision coupled calculation can supply an uncertainty-characterized reference over the frozen air sample domain, then freeze the benchmark-specific comparison protocol before broad runs.
- Keep the `0.1–30 mm` gap scope, `a <= r < d` solver domain and order-512 public cap unchanged unless separate reviewed evidence and a new decision justify a change.
- Force, acceleration, dynamics, control and gravity-equivalence work remain outside NUM-03 and P4.

## Implementation follow-up — 2026-10-04

The [NUM-03 field-error protocol basis](../research/NUM-03-field-error-protocol.md) specifies comparison metrics that do not require an invented threshold and records the missing requirement/reference basis. P1.3 provides figure-derived force values, not a field measurement or field-accuracy requirement. This decision remains unchanged: no numeric field tolerance is adopted, P4 remains INDETERMINATE, and broad NUM-04 work remains blocked until the documented prerequisites are met.
