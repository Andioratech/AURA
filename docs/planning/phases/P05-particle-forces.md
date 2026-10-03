# P5 — Air-Sphere Force Model and Domain-Limited Evidence

**Maps to:** P5.1–P5.7; D02/D04/D06/D09

## Entry condition

Air P4 PASS and a source-reviewed force-model decision for the DEC-002 50 mm EPS sphere in air. LIT-03's water small-particle equations do not apply to this sphere by default and cannot be used to reproduce its force.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## FOR-01 — Freeze the force-model contract and regime checks

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-07, DEC-002 air benchmark

**Steps**

1. Choose a formulation justified for the air sphere's geometry, material, ka, near-field source geometry and available field components.
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

## FOR-05 — Prepare and execute the matched air force comparison

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-04, DEC-002 air benchmark

**Steps**

1. Complete B-10 source, geometry and input mapping; separate calibration from evaluation wherever the source permits.
2. Compare the declared air-sphere force observable over the frozen parameter range and preserve every point, including the 0.1–1.9 mm measurements that lie outside the source-reported FEM range.
3. Separate numerical, model-form, measurement and figure-reading uncertainty. Missing experimental uncertainty remains missing; do not infer it from digitization spread.
4. Produce PASS/FAIL/INDETERMINATE only according to the predeclared rule and evidence completeness.

**Required artifacts:** Air reference protocol, residual plots, coverage map, uncertainty/gap report and comparison status.

**Acceptance / decision:** No circular calibration or unsupported inference; missing data are explicit. Given the currently incomplete source uncertainty, numerical agreement alone may leave formal measurement validation INDETERMINATE.

**If unsuccessful:** D-01/D-11/F-02/F-08; continue independent model checks without promoting a claim.

## FOR-06 — Resolve viscosity, thermal and streaming branches

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FOR-05, LIT-04

**Steps**

1. Use the omitted-effects budget to decide which corrections are mandatory for the selected particle and metric.
2. Implement only the required viscous/thermoviscous or streaming reference branch, with its own equations and primary source checks.
3. Compare models in an overlap domain and test whether omitted terms change sign, magnitude or motion interpretation beyond the budget.
4. If the needed branch cannot be validated, record an explicit scope limit and stop promotion of the affected air-sphere claim.

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

1. Assemble model/force verification, numerical convergence, air comparison state and omitted-effects evidence.
2. Record whether P5 can PASS its required reference gate; identify any trajectory-based measurement that still requires a staged coupled validation decision.
3. If the baseline gate cannot be met without coupled dynamics, prepare a concrete decision on a bounded coupled verification/validation subphase; do not silently authorize later control.
4. Update D09 claim status and the board with the exact permitted next work.

**Required artifacts:** P5 gate review; force evidence bundle; any required coupled-validation decision proposal.

**Acceptance / decision:** The gate distinguishes verified force code from validated physical response; no pending measurement is marked passed.

**If unsuccessful:** D-11/F-11; preserve INDETERMINATE and continue eligible design work until the gate or reviewed subphase permits execution.

## Phase exit review

Selected force/torque outputs have independently verified signs, units, numerical behavior and applicability, and the matched air reference comparison is reviewed. Missing source measurement uncertainty may keep formal validation INDETERMINATE; do not convert numerical verification into a downstream physical-claim PASS.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
