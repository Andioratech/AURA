# Next Main Task — NUM-03 Thin-Shell Field Qualification

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Source revision:** `e0ae436` (GitHub Quality [37173682267](https://github.com/Andioratech/AURA/actions/runs/37173682267) passed)

## Immediate task

Qualify the selected air field model at the declared minimum source-to-sphere gap, `H=0.1 mm`, for the frozen 50 mm sphere, 25.23 kHz source and centered geometry. This is software verification of pressure, velocity and pressure gradient in the existing `a<=r<d` domain. It does not assess force, motion, acceleration, experiment or gravity equivalence.

First freeze a finite observation set, increasing modal orders, and separate quadrature settings using the recorded NUM-02 resource model and prior NUM-03 diagnostics. The public evaluator's tested minimum-gap order sequence reaches 500; this is evidence for a bounded diagnostic sequence, not a production order or convergence declaration. Runtime has no matching exact-revision calibration, so the CLI must remain INDETERMINATE and authorize no production execution. Any exploratory calculation must be separately identified, time-limited and retain rejection/failure evidence.

Then compare the public Hasegawa evaluator against a separately projected Rayleigh incident field followed by the stationary sound-hard sphere modal sum at sphere-surface, mid-gap and outer-shell samples. Keep precision, modal truncation and disk/surface quadrature changes separate. Include an order-18 control and the high-order sequence indicated by the predeclared minimum-gap order study. Record metrics separately for pressure, velocity and gradient, plus script/config/code/environment/output hashes. Existing shared special-function and sphere-response primitives mean this remains a partial mathematical overlap, not a fully independent accepted reference.

## Exit limits and following work

A selected-grid match or small order change is not a remainder bound, continuous coverage, solver convergence or P4 PASS. Preserve nonmonotone and rejected configurations. NUM-03 remains ACTIVE until full gap/order/surface verification, public run-path integration, live-array resource reconciliation, bounded chunks, immutable run diagnostics, exact-revision ENV-1.0 runtime calibration and a bounded pilot are addressed. See [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and [P4 plan](../planning/phases/P04-numerical-field.md).
