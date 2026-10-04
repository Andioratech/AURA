# Next Main Task — NUM-03 Public Run-Path Integration

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Validated source revision:** `7b0923d` (GitHub Quality [37180838930](https://github.com/Andioratech/AURA/actions/runs/37180838930) passed)

## Completed discrete-grid verification

The direct Decimal Rayleigh-disk-to-modal implementation overlaps the public evaluator at matched orders18–500 over 37 angles, three radial shells and gaps0.1/10/20/30 mm (444 locations per order). Maximum normalized absolute differences are about `1.5e-13` pressure and `5.3e-13` velocity/pressure gradient. A separate order512 comparison over all 444 points also agrees near the same numerical scale. These are mathematical cross-formulation checks for finite sums, not validation against a physical reference.

At 300 Decimal digits, a direct order1200 calculation compared with order512 over the full sampled grid gives the following outer-shell differences. Velocity/gradient use the norm of both nonzero axisymmetric Cartesian components and are normalized by the order1200 grid maximum:

| Gap | Outer-shell `r/d` | Pressure | Velocity | Pressure gradient |
|---:|---:|---:|---:|---:|
| 0.1 mm | `0.999960` | `0` | `<1e-18` | `<1e-18` |
| 10 mm | `0.997143` | `4.67e-13` | `1.96e-11` | `1.96e-11` |
| 20 mm | `0.995556` | `4.97e-10` | `1.21e-8` | `1.21e-8` |
| 30 mm | `0.994545` | `3.46e-8` | `1.14e-6` | `1.14e-6` |

At the 30 mm outer shell, direct order1200 differs from order1600 by `9.33e-16` pressure and about `9.05e-14` in velocity/gradient; source radial rules128/256/512 agree at displayed precision through order1600. These finite-grid comparisons are not rigorous tail/error bounds, and no field tolerance has been set. The public evaluator remains capped at512; do not claim the complete declared field domain has passed.

NUM-02 was evaluated for a hypothetical workload of 4 gaps ×111 points, quadrature order256, maximum Bessel argument25.1, chunk size64 and baseline RSS zero. Hypothetical RAM is `1,005,568 B` at order512, `1,450,112 B` at1000, and `1,994,496 B` at1600; disk is `946,176 B`. Every report remains `INDETERMINATE`, with no wall-time estimate, because there is no matching exact-revision production calibration. These values are estimator outputs, not production solver measurements.

The order-extension and all-gap artifacts, hashes and preserved invalid attempts are documented in the [NUM-03 coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md); the generated files remain ignored in `results/diagnostics/`.

## Immediate next work

Integrate the coupled Hasegawa evaluator into the public run lifecycle. Use the frozen air scenario and exact dimensions to create a Hasegawa run request; bind it to NUM-02 workload preflight, reject before field allocation when preflight is incomplete or resources exceed caps, evaluate one bounded point chunk at a time, and produce immutable configuration/code/environment/seed/output provenance with checksums. Add a diagnostic-only policy that preserves failed runs and never reports field software verification as model validation. Exercise the missing-calibration refusal path; do not execute a production workload while the exact clean revision lacks ENV-1.0 runtime calibration.

Keep `max_order` explicit and retain the current public cap512 during this integration. Before changing the cap or declaring P4 acceptance, review a field-accuracy tolerance for pressure, velocity and pressure gradient across the full domain. If the integration reveals that the public model or resource contract needs a change, preserve the evidence and consult the documented NUM-01 fallback. No force, dynamics, acceleration, control or gravity-equivalence work belongs to NUM-03.

See [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and the [P4 plan](../planning/phases/P04-numerical-field.md).
