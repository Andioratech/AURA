# NUM-03 Field-Tolerance Decision Brief

**Prepared:** 2026-10-04 · **Status:** Decision basis only; no numerical tolerance is adopted

## Decision requested

For the air P4 gate, should AURA accept a **field-only numerical error budget** for pressure, particle velocity and pressure gradient, derived from independent reference uncertainty and observable convergence, with force/acceleration accuracy budgeted separately in later phases? This is the recommended route and preserves DEC-006's sequence: air field verification first, then air force and dynamics work only after the applicable field gate. The alternative is to hold P4 tolerance selection until a downstream force/acceleration accuracy target can allocate an error budget backward; that would defer the air field gate until the downstream target is defined.

This request concerns how the field-gate tolerance is justified. It does not ask to approve a particular percentage or to change any current numerical or physical assumptions.

## Evidence and limits

- D03 says initial numeric tolerances remain proposals until derived from a named benchmark, discretization study and measurement/model uncertainty. D04 rejects universal resolution rules and requires convergence of the observable. D06 requires each benchmark to freeze its own observable, tolerance, uncertainty, refinement protocol and stopping rule before execution; its proposed 2% simple-wave target is not a project-wide tolerance.
- The benchmark plan B-07 already requires a frozen sample set, complex phase handling without unregistered phase fitting, an absolute scale near nodes, at least three refinement levels, and separate pressure and derivative observables. The Hasegawa solver contract requires pressure, velocity and pressure-gradient checks separately and says no universal percentage is adopted.
- Hasegawa et al. derive an infinite spherical-harmonic series for the ideal baffled-piston/rigid-sphere model. Their paper's sample computations do not establish an error tolerance or convergence result for AURA's declared geometry; the project contract already records that limitation ([primary paper](https://doi.org/10.1250/ast.6.9)).
- The existing direct/public comparison agrees at matched order on 444 sampled locations, but both formulations evaluate the same stated physical model and the comparison is not a bound. Order-512 versus finite higher-order sums changes by as much as `1.14e-6` in the sampled outer-shell velocity/gradient norm at the 30 mm gap. These sparse finite-order observations have no accepted threshold or tail bound.
- The new order-512 air diagnostic is one point at the 0.1 mm gap. Its bundle verifies, but its science verdict is INDETERMINATE and it has no independent field reference. It cannot determine a tolerance.
- Roache's Grid Convergence Index and Celik et al.'s uncertainty procedure concern grid/discretization refinement in CFD. They support reporting observable-specific convergence uncertainty, but their formulas do not automatically apply to AURA's harmonic-truncation sequence; use would require a justified mapping and evidence of an appropriate convergence regime ([Roache 1994](https://doi.org/10.1115/1.2910291), [Celik et al. 2008](https://doi.org/10.1115/1.2960953)).

## Recommended method after the decision

Keep P4's numerical field gate separate from later force and acceleration validation. Before the next convergence campaign, predeclare a matched reference and its uncertainty, field sample set over the declared domain, at least three harmonic truncations, and separate complex-pressure, vector-velocity and vector-pressure-gradient error summaries. Include both a norm over the fixed sample set and an absolute local error criterion so that near-zero reference values do not make relative error singular. Report observed order behavior and keep truncation, floating-point, reference, parameter and measurement/model uncertainty separate. Do not fit a convergence rate or call a threshold passed if the sequence is nonmonotone or outside an evidenced asymptotic regime.

The numerical budget should be justified against the reference's numerical uncertainty and a predeclared use requirement. If no suitable reference uncertainty or downstream use requirement can be established, retain `INDETERMINATE`; do not select a percentage from the order-512 diagnostic, the source proposal's 2% simple-wave target, or the current highest-order difference. Any later force or acceleration budget must include sensitivity to pressure, velocity and gradient errors and remain distinct from field verification.

## Consequences

Either route keeps the order-512 cap, the `a <= r < d` domain and all current evidence unchanged. A field-only P4 pass would support only the declared ideal air-field model and tested domain. It would not validate acoustic force, acceleration, gravity equivalence, hardware behavior, water, or larger bodies. NUM-03 remains ACTIVE; NUM-04 remains blocked until its observable, tolerance and refinement protocol are frozen.
