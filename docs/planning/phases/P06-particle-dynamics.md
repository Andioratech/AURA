# P6 — Air-Sphere Dynamics and Gravity Cases

**Maps to:** P6.1–P6.7; D03/D04/D06/D07

## Entry condition

Air P4 and the P5 gate permit the declared air-sphere dynamics domain, or a specific coupled-validation subphase is recorded under PLAN-01 change control. Generic mathematical design may be prepared earlier; it does not bypass the scientific gate.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## MOT-01 — Select resolved versus reduced dynamics

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-08, LIT-04

**Steps**

1. Compare particle/fluid relaxation, acoustic averaging, controller/observation and target time scales using sourced parameters or explicit intervals.
2. Select inertial or reduced motion equations and review drag, added mass/history, buoyancy, streaming, wall and Brownian terms as applicable.
3. State which acceleration statistic can be resolved, including finite-window handling if stochastic terms are needed.
4. Freeze equations and scope before implementation; register any coupled-validation authorization required by the phase entry.

**Required artifacts:** Dynamics decision; time-scale table; equation and omitted-term records.

**Acceptance / decision:** The selected state/equations can answer the registered observable and all neglected terms have justified or explicitly unresolved impact.

**If unsuccessful:** D-05/D-06/F-03; change model before reporting acceleration.

## MOT-02 — Implement a complete and inspectable load ledger

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-01

**Steps**

1. Implement each declared load with explicit input/frame/unit/source identity and aggregate it without double counting.
2. Keep radiation force, drag relative to local fluid motion, gravity/buoyancy and selected disturbances separate in outputs.
3. Where unsteady-fluid dynamics changes the inertia equation, define the correct residual instead of blindly comparing to particle mass alone.
4. Test zero-source, zero-flow, zero-gravity and simple independent force combinations.

**Required artifacts:** `dynamics/loads.py`; per-term force output; ledger/residual checks.

**Acceptance / decision:** Every term in the chosen equation is observable in the report; omitted/unavailable terms cannot appear as silently zero.

**If unsuccessful:** F-01/F-03/F-06; isolate one load at a time.

## MOT-03 — Implement deterministic translation with analytic references

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-02

**Steps**

1. Implement integration for the chosen dynamics with explicit initial state, output times and solver tolerances.
2. Compare constant-force motion and linear-drag relaxation against separately derived solutions in their applicable regimes.
3. Check net acceleration from the equation against an independently resolved state derivative at appropriate time resolution.

**Required artifacts:** `dynamics/integrate.py`; B-11 translation cases and report.

**Acceptance / decision:** Position/velocity/acceleration observables pass independent checks; nonfinite states and solver failure propagate.

**If unsuccessful:** F-04; inspect time scale, stiffness and load convention.

## MOT-04 — Resolve time refinement and workspace events

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-03

**Steps**

1. Run at least three appropriate time-step/tolerance/output-sampling refinements of the primary motion observable.
2. Add chamber exit, wall clearance and model-domain events with preserved event time/state.
3. Separate actual integrator resolution from output sampling and acoustic/controller averaging.
4. Verify event location accuracy and terminate or label invalid continuing motion according to the frozen protocol.

**Required artifacts:** Time-refinement report; event tests; trajectory/boundary diagnostics.

**Acceptance / decision:** Reported accuracy includes event/time-sampling error; a particle cannot pass through a wall unnoticed.

**If unsuccessful:** F-04/F-07; refine events or the selected dynamical formulation.

## MOT-05 — Implement the declared rotational contract

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-04

**Steps**

1. Define angular state, orientation convention, inertia and supported torque model for the declared body.
2. For a symmetry-restricted spherical case, justify any zero-torque assumption from the selected physics; otherwise implement the reviewed torque model before claiming support.
3. Test zero/constant torque and orientation normalization with independent dynamics references.
4. State which body classes remain unsupported; do not expand to nonspherical particles without a model/benchmark decision.

**Required artifacts:** `dynamics/rotation.py`; torque-domain record; rotational B-11 tests and FR-004/005 mapping.

**Acceptance / decision:** Rigid-body rotational evolution is correct within the declared torque domain; translation-only success is not reported as full FR-005 completion.

**If unsuccessful:** F-03/F-04; review torque applicability or report the requirement incomplete.

## MOT-06 — Compare Earth, ideal zero and residual-gravity cases

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-05

**Steps**

1. Configure gravity as a vector/time signal in a declared reference frame; preserve all other physical inputs between control cases.
2. Update fluid/body gravitational terms consistently, including relevant buoyancy/pressure assumptions.
3. Run Earth and ideal zero cases; add a sourced residual signal or clearly labeled hypothetical disturbance design.
4. Report which differences arise from gravity versus changed flow/initial conditions.

**Required artifacts:** B-12 configurations, manifests and comparison; environment assumptions.

**Acceptance / decision:** Gravity can be changed without hidden viscosity/flow changes; ideal microgravity conclusions remain explicitly idealized.

**If unsuccessful:** D-13/F-03/F-08; correct frame/load inconsistencies.

## MOT-07 — Add stochastic motion only when required

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-06

**Steps**

1. Use the time-scale/error budget to decide whether Brownian effects are needed for the selected radius/window.
2. If needed, implement the reviewed stochastic equation with explicit integration interpretation and independent seed streams.
3. Verify ensemble reference statistics and step sensitivity with a predeclared sample count/interval rule.
4. If omitted, retain the quantitative omission justification and re-entry threshold.

**Required artifacts:** Conditional `dynamics/stochastic.py`; B-13 evidence or justified non-applicability record.

**Acceptance / decision:** No artificial pointwise white-noise acceleration is used; seeded replay and justified ensemble statistics exist where required.

**If unsuccessful:** F-03/F-04/F-09; revise observation/model interpretation.

## MOT-08 — Compare air-sphere motion, report and close P6

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-07, FOR-05

**Steps**

1. Execute an independent air-sphere trajectory reference only if its domain and uncertainty are adequate; otherwise retain the motion comparison as INDETERMINATE and complete only numerical dynamics verification.
2. Report x/v/acceleration, per-load terms, events and primary metric, distinguishing force-equivalent acceleration from resolved motion.
3. Complete the applicable P5 coupled-validation obligations before requesting P6/target-control promotion.
4. Bundle evidence, update requirements/claims and record the P6 review with exact permitted target-domain scope.

**Required artifacts:** B-10/B-11/B-12 reports as applicable; motion evidence bundle; P6 gate review.

**Acceptance / decision:** Model verification and required measurement decisions are explicit; unresolved validation blocks the affected claim gate.

**If unsuccessful:** F-02/F-08/F-11; prepare a narrower claim or additional evidence, not an automatic PASS.

## Phase exit review

Translation/rotation support for the declared body is verified, force accounting and step refinement are complete, gravity/flow assumptions are consistent, and the required matched motion evidence is reviewed. An acceleration claim cannot rely on unexamined overdamped dynamics.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
