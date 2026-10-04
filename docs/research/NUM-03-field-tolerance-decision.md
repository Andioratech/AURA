# NUM-03 Field-Tolerance Decision Brief

**Prepared:** 2026-10-04 · **Status:** DEC-007 recorded; no numerical tolerance is adopted

## Owner decision recorded

The owner agreed to a **field-only numerical error budget** for pressure, particle velocity and pressure gradient in air P4. Force/acceleration accuracy will be budgeted separately in the applicable later phases. [DEC-007](../decisions/DEC-007-p4-field-only-error-budget.md) records the decision.

No percentage or numerical threshold was selected. The decision does not change any current numerical or physical assumptions.

## Evidence and limits

- D03 says initial numeric tolerances remain proposals until derived from a named benchmark, discretization study and measurement/model uncertainty. D04 rejects universal resolution rules and requires convergence of the observable. D06 requires each benchmark to freeze its own observable, tolerance, uncertainty, refinement protocol and stopping rule before execution; its proposed 2% simple-wave target is not a project-wide tolerance.
- The benchmark plan B-07 already requires a frozen sample set, complex phase handling without unregistered phase fitting, an absolute scale near nodes, at least three refinement levels, and separate pressure and derivative observables. The Hasegawa solver contract requires pressure, velocity and pressure-gradient checks separately and says no universal percentage is adopted.
- Hasegawa et al. derive an infinite spherical-harmonic series for the ideal baffled-piston/rigid-sphere model. Their paper's sample computations do not establish an error tolerance or convergence result for AURA's declared geometry; the project contract already records that limitation ([primary paper](https://doi.org/10.1250/ast.6.9)).
- The existing direct/public comparison agrees at matched order on 444 sampled locations, but both formulations evaluate the same stated physical model and the comparison is not a bound. Order-512 versus finite higher-order sums changes by as much as `1.14e-6` in the sampled outer-shell velocity/gradient norm at the 30 mm gap. These sparse finite-order observations have no accepted threshold or tail bound.
- The new order-512 air diagnostic is one point at the 0.1 mm gap. Its bundle verifies, but its science verdict is INDETERMINATE and it has no independent field reference. It cannot determine a tolerance.
- A focused direct-modal comparison at order 512 on 37 angles at the 30 mm outer shell shows P300/P600 differences below `1.2e-287` for pressure and `4.9e-179` for velocity/gradient. Radial Gauss-Legendre rules 128/256/512 also produce paired finite-grid differences below `1.8e-205`. These checks support arithmetic and quadrature stability only for that sampled shell; common-formulation error and modal-tail uncertainty remain open. The separate order-512/order-1200 finite-sum change there reaches `1.14e-6` in velocity/gradient, so the production truncation may dominate the observed numerical sensitivity. See the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md) for exact hashes and limitations.
- Roache's Grid Convergence Index and Celik et al.'s uncertainty procedure concern grid/discretization refinement in CFD. They support reporting observable-specific convergence uncertainty, but their formulas do not automatically apply to AURA's harmonic-truncation sequence; use would require a justified mapping and evidence of an appropriate convergence regime ([Roache 1994](https://doi.org/10.1115/1.2910291), [Celik et al. 2008](https://doi.org/10.1115/1.2960953)).

## Next method task

Before the next broad convergence campaign, determine whether the separately implemented high-precision coupled calculation can provide an uncertainty-characterized reference across the frozen air domain. Its quadrature, arithmetic and modal-truncation errors must be assessed separately; agreement between implementations at a matched finite order is not a tail bound. Preserve the published force measurement uncertainty and physical-model uncertainty as separate, out-of-scope terms for this numerical P4 budget.

Once reference uncertainty is characterized, freeze: complex-pressure, vector-velocity and vector-pressure-gradient metrics; a deterministic sample set; at least three harmonic truncations; independent quadrature/precision checks; benchmark-specific acceptance and stopping rules; and the resource cap. Use both a fixed-grid norm and a maximum absolute local error in SI units, without phase fitting, so nodes do not make the relative error singular. Report truncation, floating-point and reference numerical uncertainties separately. Do not fit a convergence rate or pass a threshold if the sequence is nonmonotone or outside an evidenced asymptotic regime.

If the reference uncertainty or an explicitly scoped field-use requirement cannot be justified, retain `INDETERMINATE`; do not select a percentage from the order-512 diagnostic, the source proposal's 2% simple-wave target, or the current highest-order difference. Any later force or acceleration budget must account for sensitivity to pressure, velocity and gradient errors while remaining distinct from field verification.

## Consequences

DEC-007 keeps the order-512 cap, the `a <= r < d` domain and all current evidence unchanged. A future field-only P4 pass would support only the declared ideal air-field model and tested domain. It would not validate acoustic force, acceleration, gravity equivalence, hardware behavior, water, or larger bodies. NUM-03 remains ACTIVE; broad NUM-04 convergence runs remain blocked until reference uncertainty, observable metrics, acceptance rule, refinement protocol and resource cap are frozen.
