# Necessary-Limit Design for AURA Target Studies

**Prepared:** 2026-10-03 · **Work item:** LIT-05 · **Status:** reusable symbolic screen prepared; no target-specific exclusion evaluated

## Purpose and boundary

This record prepares the necessary-condition analyses in [planning 07](../planning/07-falsification-and-limits.md) for future declared target cases. It does not select body mass, shape, medium, acceleration, workspace, duration, gravity environment or actuator hardware. Those remain open in [UNK-005](../registers/unknowns.md), [UNK-010](../registers/unknowns.md), [UNK-011](../registers/unknowns.md) and [UNK-012](../registers/unknowns.md). The symbolic equations below are algebraic/kinematic screening tools, not current force predictions or proof that AURA can or cannot meet an unspecified target.

## Required target record before numerical screening

Freeze an immutable experiment identity and record: body/material/geometry and mass/inertia; medium and thermodynamic state; acoustic source and array geometry; operating frequency and bandwidth; field regime; source amplitude convention and traceable pressure/power calibration; enclosure and boundary conditions; initial state and frame; gravity/residual-acceleration history; target acceleration vector versus time; duration and workspace; observation operator, sampling, uncertainty and acceptance statistic; all retained loads; and the admissible actuator set. Every physical value needs a primary source or measured provenance. An assumption must be labeled and branched if it materially affects the result.

The owner-approved [DEC-004](../decisions/DEC-004-staged-mass-and-size-expansion.md) objective includes greater masses, larger dimensions and other shapes toward microgravity. The current record therefore does not set a particle-scale ceiling or convert a failure in one body domain into a project-wide exclusion.

## L-01 — Geometry and duration

For a registered constant target acceleration \(\mathbf a_*\) in an inertial frame, kinematics gives

\[\mathbf x_*(t)=\mathbf x_0+\mathbf v_0t+\tfrac12\mathbf a_*t^2.\]

For a time-varying target, integrate the declared \(\mathbf a_*(t)\) with the registered initial conditions. Compare the full trajectory and any allowed error tube with the actual admissible workspace \(\mathcal W\); derive the earliest boundary exit or clearance margin. State whether this is a point-body center-of-mass requirement or also constrains an extended object's orientation and clearance. No current numerical result exists because \(\mathbf x_0,\mathbf v_0,\mathbf a_*(t),T\) and \(\mathcal W\) are not selected.

## L-02 — Required force in the complete declared dynamics

For a constant-mass translational model only, rearranging Newton's law gives

\[\mathbf F_{\rm acoustic,req}(t)=m\mathbf a_*(t)-\sum_j\mathbf F_j(t),\]

where every non-acoustic term is explicit: fluid-relative drag, buoyancy/gravity, background or streaming flow, added-mass/history terms if retained, contact/external loads, and any other selected dynamics term. A motion model with variable mass, deformable body, or resolved fluid requires its own balance. Compare the complete time history with a justified admissible force set, including uncertainty and required torque/spatial-loading conditions for extended bodies. No target, force set or actuator envelope exists for a numerical comparison yet.

## L-03 — Reachability and certificate type

Keep three outcomes distinct: a checked feasible actuation/trajectory is a witness for that modeled case; a finite search with no witness is only an unsuccessful search; exclusion requires a justified outer bound or valid relaxation covering every admissible actuation, plus a checked numerical certificate and uncertainty direction. A sampled set or local Jacobian is not a global controllability proof. No AURA reachable-set solver or certified infeasibility analysis is implemented.

## L-04 — Conservation, momentum and power scope

For any momentum estimate, declare the control volume, all incident/outgoing flux surfaces, source and reflector forces, body/fluid/wall momentum, stored-field terms and averaging interval. The D02 estimate \(F\sim\kappa P_{\rm intercepted}/c\) applies only as a conditional order-of-magnitude check for a specified progressive plane-wave interception/reflection idealization with declared \(P_{\rm intercepted}\) and momentum coefficient. It is **not** a universal bound for standing waves, resonant cavities, multiple sources, a finite enclosure or an unspecified control volume. A power-only argument does not bound a static holding force because \(\mathbf F\cdot\mathbf v=0\) at zero velocity. No universal acoustic pseudogravity bound is asserted.

## L-05 — Approximation and observable boundaries

For each selected model, calculate or define with uncertainty the indicators that its derivation actually requires. The current particle literature review shows why this must be model-specific: for SRC-W03 MQ1, `ka` is small over the listed diameters while `delta_s/a` spans order-one to thin-layer values; wall clearance, thermoviscous properties, perturbation amplitude and the inertia-time discrepancy remain relevant. A new body/shape/medium/frequency needs new indicators. Record the actual observation window and its relation to acoustic, particle-relaxation, controller and measurement timescales. A failed applicability check means that approximation cannot decide the case; it is not itself proof that another physical model fails.

## Preconditions, order and stop rules

1. Finish the required P1 source/evidence dossier and keep formal measurement acceptance separate from model/software verification.
2. At the later target gate, freeze \(m,\mathbf a_*(t),T,\mathcal W\), environment, loads and actuator limits before running any target test.
3. Apply L-01/L-02 cheaply before allocation or controller tuning; apply L-03 only with a valid reachability construction; use L-04 only for its declared control volume; complete L-05 before interpreting an equation outside its domain.
4. If an input is absent, report `INDETERMINATE` for that analysis. Do not substitute zero, a guessed target, an unrelated material value or a widened tolerance. Retain negative, failed and invalidated cases with their original assumptions.

## Evidence status

This is a reusable analysis design only. It has no target inputs, solver, feasibility witness, exclusion certificate, hardware limit or claim of microgravity performance. The follow-on target is owned by CTL-01 after the preceding force/dynamics evidence gates; a scale-specific target proceeds under SC-04 and DEC-004.
