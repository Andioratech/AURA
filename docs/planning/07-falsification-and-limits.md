# 07 — Adversarial Campaign and Mathematical Limits

## Purpose and interpretation

The campaign is designed to disprove the registered H statements where evidence warrants it. It must also detect a wrong implementation, a wrong physical model or an inconclusive experiment. These outcomes are different. A failed simulation does not by itself refute AURA.

Every attack below receives a frozen experiment protocol with parameter domain, constraints, target/time window, expected diagnostic, numerical/uncertainty budget, run cap and an interpretation rule. Record negative outcomes and favorable anomalies with equal care.

## Attack catalogue

| ID | Attack | What to vary or remove | Evidence to inspect | Interpretation / next route |
|---|---|---|---|---|
| A-01 | No actuation | Zero source drive with consistent baseline loads | Radiation force, flow, trajectory | Nonzero acoustic contribution exposes leakage/implementation error |
| A-02 | Convention trap | Equivalent peak/RMS inputs; phase and coordinate transformations | Equivalent physical observables | Disagreement returns to FND-01/F-01 |
| A-03 | Contrast limit | Source-justified ideal contrast-matching limit | Leading-order radiation response | Tests selected approximation only; not universal thermoviscous cancellation |
| A-04 | Shrink the particle | Radius through justified viscous/thermal/stochastic scales | Domain indicators, motion mechanism and uncertainty | Reveals required model change or limited controllability |
| A-05 | Let the water move | Add justified streaming/bulk flow to the same radiation case | Per-force ledger, relative/absolute motion | Separates particle forcing from advection |
| A-06 | Approach a wall | Wall distance and boundary model | Drag/force changes, domain checks | Unsupported near-wall success stays INDETERMINATE |
| A-07 | Remove gravity consistently | Earth vs ideal zero vs sourced residual acceleration | Body/fluid balance and target error | Measures conditional environmental sensitivity |
| A-08 | Force a real actuator budget | Total/per-element limits, phase resolution and slew | Realized action, saturation, error | Identifies constraint failure or hypothetical unconstrained result |
| A-09 | Lose observation quality | Latency, rate, noise, bias and dropouts | Stability/error under held-out disturbances | Distinguishes oracle-state success from observable control |
| A-10 | Change material | Sourced density/compressibility contrast within frozen set | Force sign/magnitude and tracking | Tests scope of material-specific tuning |
| A-11 | Demand longer acceleration | Increase duration with fixed workspace and limits | Velocity growth, drag demand, exit time | Exposes finite-duration/workspace limitations |
| A-12 | Detune resonance | Frequency and wall-property uncertainty | Field gradients, power accounting and force | Detects fragile tuning and omitted damping |
| A-13 | Refine numerics | Mesh, gradient scheme, time step, precision, boundary size | Physical observable convergence | Numerical artifact if success disappears |
| A-14 | Defeat the optimizer | Multiple frozen starts and an independent constrained formulation | Witness, residual and certificate type | Failure to find a solution is not certified exclusion |
| A-15 | Break calibration circularity | Hold out particles, positions or conditions from amplitude calibration | Out-of-sample prediction and uncertainty | Reveals fitted agreement that lacks predictive evidence |
| A-16 | Expose omitted interactions | Increase concentration or add a second particle only in a new scoped study | Scattering/flow coupling and control interference | Single-particle result cannot support collective claim |
| A-17 | Pressure/temperature limits | Sourced drive/thermal envelopes and duration | Limits, temperature/property changes and applicability | Unsupported linear regime invalidates extrapolated success |
| A-18 | Independent implementation | Aligned case with separately derived model/numerics | Agreement, shared assumptions and discrepancy | Strengthens or limits the claim; not a substitute for measurements |

A-16 is conditional expansion, not mandatory multi-particle solver construction for the first release. The other attacks apply wherever their variables belong to the chosen domain; record justified non-applicability instead of silently skipping.

## Cheap necessary-condition screen before expensive control

### L-01 — Geometry and duration

For a declared constant target acceleration and initial state in an inertial frame, integrate the target trajectory `x_target(t) = x0 + v0*t + 0.5*a_target*t^2`. This is a kinematic identity for that target, not an acoustic model. Include body clearance and any allowed tracking-error tube when comparing with the workspace. Determine the earliest unavoidable boundary exit. A finite chamber cannot support arbitrary duration for every nonzero acceleration target from a fixed initial state.

**Certificate task:** derive the component/domain inequality for the actual geometry; state whether the conclusion applies to exact tracking or a bounded error tube; include uncertain initial state. If acceleration reversals or coordinate-frame changes are allowed, analyze that different target explicitly.

### L-02 — Force demand in the declared dynamics

Derive required acoustic force from the complete selected motion equation, including drag, fluid flow, gravity/buoyancy and any retained inertial/history terms. In the elementary constant-mass model, rearranging Newton's equation gives `F_required = m*a_target - sum(F_other)`. That algebra is not permission to omit water loads or assume it covers every unsteady-fluid model.

**Certificate task:** compare required demand over the entire trajectory to a justified admissible-force set with uncertainty. Evaluate duration dependence and fluid-relative speed; initial force sufficiency alone cannot establish sustained acceleration.

### L-03 — Reachability and numerical certificates

- An actual admissible actuation/trajectory with checked residuals is a feasibility witness for that modeled case.
- A finite sample of feasible forces is generally an inner sample of the reachable set. Failure to hit a target does not establish that it is unreachable.
- A justified outer approximation can support exclusion if the required force lies outside it after accounting for numerical and model uncertainty.
- A convex relaxation can certify infeasibility only if it is a valid relaxation containing all admissible original solutions and its numerical certificate is checked. Relaxation feasibility need not establish physical feasibility.
- Local Jacobian rank or singular values diagnose local authority; they do not prove global controllability.

**Certificate task:** record set construction, assumptions, solver tolerance, independent certificate check, and whether the conclusion is local/global, nominal/robust and model/physical. No such certificate is implemented today.

### L-04 — Conservation and power scope

Use a declared control volume and account for incoming/outgoing momentum, sources, walls, fluid and stored-field effects as required by the chosen model. Follow [D02](../D02-mclf.md). Do not promote a progressive-wave momentum-transfer estimate to a universal cavity/standing-field bound. A missing term invalidates the purported proof, not the physical hypothesis.

### L-05 — Approximation boundaries

Derive quantitative applicability tests from the selected equations and error budget. Record ka, viscous/thermal length ratios, relevant Reynolds/amplitude parameters, wall separation and observation time scales where used. A regime failure means the approximation cannot decide that case; research a suitable model before making a physical impossibility claim.

## Adversarial study design

1. Define nominal case and target, train/tune on separate cases, then freeze the evaluation protocol.
2. Enumerate uncertainty intervals/distributions from evidence. Where distributions are unknown, use justified intervals and scenario sensitivity instead of invented Gaussian noise.
3. Start with limiting cases and one-factor perturbations. Add selected interactions when a mechanism justifies them.
4. Freeze sample design, seed streams, run/compute caps, primary statistic and confidence calculation before the campaign.
5. Retain scheduled, completed, invalidated, timed-out and failed cases in the study denominator and index.
6. Re-run the most damaging and most favorable cases with numerical refinement and a separate formulation where claim-critical.
7. Publish a map distinguishing supported, refuted-for-target, outside-model and unresolved regions. Do not interpolate unsampled success/failure boundaries without a justified method.

## What counts as breaking a claim

A reproducible counterexample can refute a universal statement over a domain only if the case is inside that domain and the model/evidence can decide it. A bound excluding the entire admissible set can refute a target-existence statement for that model/domain. A finite unsuccessful sweep or one unstable controller cannot prove global impossibility. Conversely, one favorable nominal run cannot establish robustness or physical feasibility.

Close with the [claim template](templates/claim-record.md): exact quantifiers, supporting/contradicting evidence, unresolved model uncertainty and the smallest warranted statement.
