# Next Main Task — NUM-03 High-Order Independent Reference

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Source revision:** `04a7482` (GitHub Quality [37175960904](https://github.com/Andioratech/AURA/actions/runs/37175960904) passed)

## Immediate task

The public Hasegawa evaluator changes by less than `3.4e-13` in velocity/gradient between orders 400 and 450 over 37 angles on each of the sphere-surface, mid-gap and outer-shell grids at `H=0.1 mm`; its changes from 450 to 500 remain at or below `1.92e-14`. This is sampled order stability only. A separate Rayleigh-surface modal comparison covers orders18/36, but surface and radial refinements are nonmonotone and public-evaluator discrepancies range `4.05e-6`–`3.57e-4`. The binary64/Decimal sample arithmetic difference is near `1e-14`, so sample arithmetic alone does not explain the observed gap.

The auxiliary binary64 spherical-Bessel path reaches order250 at `ka=11.45` and fails closed at order256 because `y_n` is outside its representable range. The public evaluator uses scaled terms through order500. Build or select an independent high-order stationary-sphere response and test it first against a bounded analytical control; assess arithmetic precision, modal truncation and quadrature separately. Then decide whether it can support a coupled minimum-gap overlap. If not, record the comparison as INDETERMINATE and revisit the NUM-01 fallback methods rather than treating public order stability as independent validation.

Keep this work within field verification for the frozen air case: 50 mm sphere, 25.23 kHz source, centered rigid-sphere geometry, and declared `a<=r<d` domain. Do not add force, motion, acceleration, feedback or gravity-equivalence claims. Any exploratory run must keep exact config/code/environment/output provenance. The NUM-02 runtime gate remains INDETERMINATE without a matching exact-revision ENV-1.0 calibration.

See [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and the [P4 plan](../planning/phases/P04-numerical-field.md).
