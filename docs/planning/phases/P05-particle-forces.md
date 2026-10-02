# P5 — In-Domain Particle Forces and Water Evidence

**Maps to:** P5.1–P5.7; D02/D04/D06/D09

## Entry condition

P4 PASS and LIT-03 equation review. No small-particle force model may be used to reproduce the large air sphere.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## FOR-01 — Freeze the force-model contract and regime checks

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-07, LIT-03

**Steps**

1. Choose the formulation already justified by the water regime dossier, including assumptions on particle shape/material and field components.
2. Record equations/coefficient sources, needed pressure/velocity/gradient interpolation and defined torque coverage.
3. Specify model-domain predicates, including what is a hard contradiction and what requires further evidence; establish the selected error budget.

**Required artifacts:** Force-model protocol; `mclf/regimes.py` design; coefficient/assumption records.

**Acceptance / decision:** Required input fields and validity decisions are explicit; no arbitrary universal ka cutoff substitutes for source review.

**If unsuccessful:** D-02/D-03/F-03; select a justified branch or keep the case uncovered.

## FOR-02 — Implement one particle-force model and typed results

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-01

**Steps**

1. Implement source-reviewed coefficients and the declared radiation-force formulation in one small module.
2. Return force, frame, units, applicable torque or explicit unsupported status, gradients used and model provenance.
3. Reject missing field components/outside-domain queries; keep model verdict separate from successful execution.

**Required artifacts:** `forces/particle.py`, `forces/types.py`; model unit checks and example.

**Acceptance / decision:** Independent known inputs produce expected units/signs; unsupported cases are never accepted by default.

**If unsuccessful:** F-01/F-03; trace coefficients and convention before adding complexity.

## FOR-03 — Challenge signs, limits and conservative gradients

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-02

**Steps**

1. Freeze B-08 cases for zeros, symmetries, material-contrast limits and amplitude scaling within the chosen approximation.
2. Where a conservative potential is justified, independently differentiate it and compare force; do not assume all viscous/traveling-wave forces are conservative.
3. Verify gradient/interpolation convergence separately from pressure convergence and record cancellation near force zeros.

**Required artifacts:** B-08 tests and independent derivation; sign/limit report.

**Acceptance / decision:** Every applicable limit passes its derived tolerance, including force direction and restricted potential consistency.

**If unsuccessful:** F-01/F-04/F-06; diagnose before comparing measurements.

## FOR-04 — Compare the force against an independent model reference

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-03

**Steps**

1. Choose a published analytic/numerical force case with matching assumptions and independent expected values.
2. Map coefficients and phasor/amplitude conventions and freeze a full comparison range.
3. Run refinement for the actual force observable, retaining all cases and domain rejections.

**Required artifacts:** Force-reference mapping, manifests, convergence and comparison report.

**Acceptance / decision:** The independent mathematical reference and numerical evidence support the implementation within its domain.

**If unsuccessful:** F-04/F-08; align definitions and isolate model versus implementation discrepancy.

## FOR-05 — Prepare and execute the matched water measurement comparison

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-04, LIT-02

**Steps**

1. Complete B-09 input/calibration mapping and separate independent evaluation data from amplitude fitting.
2. If the measurement is velocity/trajectory rather than force, register the required fluid/dynamics terms and defer its actual comparison to MOT-08; do not convert velocity to force through unvalidated assumptions.
3. For available direct force data, run the frozen protocol over all selected points and separate numerical, measurement and reading uncertainties.
4. Produce PASS/FAIL/INDETERMINATE only according to the predeclared rule and evidence completeness.

**Required artifacts:** Water reference protocol, residual plots when applicable, uncertainty/gap report and comparison status.

**Acceptance / decision:** No circular calibration or unqualified velocity-to-force inference; missing data are explicit. A protocol alone does not count as completed experimental validation.

**If unsuccessful:** D-01/D-11/F-02/F-08; continue independent model checks without promoting a claim.

## FOR-06 — Resolve viscosity, thermal and streaming branches

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-05, LIT-04

**Steps**

1. Use the omitted-effects budget to decide which corrections are mandatory for the selected particle and metric.
2. Implement only the required viscous/thermoviscous or streaming reference branch, with its own equations and primary source checks.
3. Compare models in an overlap domain and test whether omitted terms change sign, magnitude or motion interpretation beyond the budget.
4. If the needed branch cannot be validated, record an explicit scope limit and stop promotion of the affected water claim.

**Required artifacts:** Conditional `forces/viscous.py`, `forces/thermoviscous.py`, `fluid/streaming.py`; overlap report and decision.

**Acceptance / decision:** All retained and omitted effects have reviewed applicability; simpler-model success is not generalized across the branch.

**If unsuccessful:** D-02/D-05/F-03/F-08; refine model or narrow a new experiment.

## FOR-07 — Audit force accounting and conditional limits

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-06

**Steps**

1. Define the applicable momentum/energy accounting and available control surfaces for the selected model.
2. Implement independent diagnostics with source/wall/fluid terms where required and document unavailable balances.
3. Inject a known inconsistent result or convention to confirm that evidence cannot be promoted.
4. Ensure a standing-field result is not rejected solely by a progressive-wave power estimate.

**Required artifacts:** MCLF force rules/balances; counterexample checks; per-force evidence report.

**Acceptance / decision:** Hard failures invalidate evidence; conditional exceedances and uncovered regimes retain their correct distinct verdicts.

**If unsuccessful:** F-06; review the alleged bound and independent balance.

## FOR-08 — Review the force-model gate and evidence dependencies

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-07

**Steps**

1. Assemble model/force verification, numerical convergence, water comparison state and omitted-effects evidence.
2. Record whether P5 can PASS its required reference gate; identify any trajectory-based measurement that still requires a staged coupled validation decision.
3. If the baseline gate cannot be met without coupled dynamics, prepare a concrete decision on a bounded coupled verification/validation subphase; do not silently authorize later control.
4. Update D09 claim status and the board with the exact permitted next work.

**Required artifacts:** P5 gate review; force evidence bundle; any required coupled-validation decision proposal.

**Acceptance / decision:** The gate distinguishes verified force code from validated physical response; no pending measurement is marked passed.

**If unsuccessful:** D-11/F-11; preserve INDETERMINATE and continue eligible design work until the gate or reviewed subphase permits execution.

## Phase exit review

Selected force/torque outputs have independently verified signs, units, numerical behavior and applicability, and the required matched reference comparison is reviewed. Missing water measurement uncertainty keeps formal validation INDETERMINATE; do not convert that to a downstream claim-gate PASS.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
