# P3 — Analytical Acoustic Foundation

**Maps to:** P3.1–P3.7; D02/D04/D06/D07

## Entry condition

P2 PASS and [RUN-01 complete](../../reviews/RUN-01-lifecycle.md); [ANA-01](../../reviews/ANA-01-field-contract.md) and [ANA-02](../../reviews/ANA-02-plane-wave.md) are complete in their reviewed scopes. [ANA-03](../../reviews/ANA-03-counterpropagating.md) is complete in its bounded counterpropagating scope; [ANA-04](../../reviews/ANA-04-interference.md) is complete for bounded two-wave interference; [ANA-05](../../reviews/ANA-05-spherical.md) is complete for ideal spherical spreading; [ANA-06](../../reviews/ANA-06-energy-balance.md) is complete for its frozen model-specific energy ledgers. ANA-07 is ACTIVE. Its first adapter records one-source B-03 and two-source B-04/B-05 plane cases; independent reference comparison, spherical-source input admission and the recorded full matrix remain outstanding. Analytical cases may proceed without conclusive P1 measurement uncertainty.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## ANA-01 — Specify field outputs and the analytic case matrix

**Current state:** DONE — [artifact review](../../reviews/ANA-01-field-contract.md), [task record](../../work-items/ANA-01.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-08, RUN-01

**Steps**

1. Freeze homogeneous/linear medium assumptions, phasor sign, source normalization and required pressure/velocity/gradient outputs.
2. Define sampling geometry, singular exclusions, units and shape conventions in FieldResult.
3. Create B-03…B-06 protocols with independent expected values, tolerance derivation and small resource caps.
4. Specify the analytical driver adapter, required artifact set, exploratory/model-coverage policy, physical post-audits and workload estimate needed to extend RUN-1.0 beyond software diagnostics. Implement each admitted driver with its owning analytical card before evidence runs.

**Required artifacts:** `fields/types.py`; analytic case protocols; equation-to-case register.

**Acceptance / decision:** Cases can be evaluated without guessing a field component or mixing real-time and phasor amplitudes.

**If unsuccessful:** F-01/F-03; resolve convention or unsupported observable.

## ANA-02 — Implement a progressive plane wave and its velocity

**Current state:** DONE — [artifact review](../../reviews/ANA-02-plane-wave.md), [task record](../../work-items/ANA-02.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-01

**Steps**

1. Derive the pressure/velocity pair in the chosen convention independently of code.
2. Implement field evaluation for one specified direction and extend through explicit coordinate rotation.
3. Check phase propagation, impedance relation in the selected regime and the separately defined intensity convention.

**Required artifacts:** `fields/analytic.py`; B-03 fixtures/tests; report with maximum and norm errors.

**Acceptance / decision:** The declared field observable meets its derived numerical tolerance at independent sample points and directions.

**If unsuccessful:** F-01/F-04; inspect sign and amplitude normalization first.

## ANA-03 — Construct a standing wave with correct flux accounting

**Current state:** DONE — [task record](../../work-items/ANA-03.md), [artifact review](../../reviews/ANA-03-counterpropagating.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-02

**Steps**

1. Superpose equal counterpropagating waves using the frozen phase convention.
2. Derive node/antinode and pressure/velocity phase relations; compute time-averaged flux using both fields.
3. Test phase-shifted and unbalanced waves, and show why local pressure squared alone does not represent net standing-wave intensity.

**Required artifacts:** B-04 protocol/checks; standing-wave field example and diagnostic plot.

**Acceptance / decision:** Independent node/phase and flux checks pass, including a nonzero-field zero-net-flux limiting case.

**If unsuccessful:** F-01/F-06; repair field/balance accounting before force work.

## ANA-04 — Verify two-source interference and allowed symmetries

**Current state:** DONE — [task record](../../work-items/ANA-04.md), [artifact review](../../reviews/ANA-04-interference.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-03

**Steps**

1. Freeze two source positions/phases and derive a few constructive/destructive sample values.
2. Implement superposition without hidden source renormalization.
3. Check coordinate transformations and only those symmetries preserved by source, domain and observable.

**Required artifacts:** B-05 examples, analytic calculations and regression checks.

**Acceptance / decision:** Expected cancellation/phase relations hold within a scale-aware tolerance near zeros.

**If unsuccessful:** F-01/F-04; inspect source geometry and complex representation.

## ANA-05 — Add only the needed spreading or attenuation reference

**Current state:** DONE — [task record](../../work-items/ANA-05.md), [artifact review](../../reviews/ANA-05-spherical.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-04

**Steps**

1. Choose a source spreading/attenuation model needed by the planned numerical comparison; cite its assumptions.
2. Exclude singular/invalid source regions and distinguish amplitude attenuation from intensity attenuation.
3. Compare independently derived distance ratios and flux where the control surface is meaningful.

**Required artifacts:** B-06 model record, examples and tests; explicit near/far-field limitations.

**Acceptance / decision:** The distance dependence and normalization match the selected reference; unsupported geometry is rejected or reported uncovered.

**If unsuccessful:** F-03/F-06; remove unsupported extrapolation and review the appropriate source model.

## ANA-06 — Add independent model-specific balance checks

**Current state:** DONE — [task record](../../work-items/ANA-06.md), [numerical report](../../benchmarks/ANA-06-energy-balance-verification.md), [artifact review](../../reviews/ANA-06-energy-balance.md). The four frozen model-specific ledgers pass their bounded error budget; missing terms stay INDETERMINATE. This does not close P3. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-05

**Steps**

1. Define surfaces, normal directions, flux and loss terms for each applicable analytical case.
2. Implement audit calculations with independent expressions/integration routes and appropriate absolute scales.
3. Exercise a deliberately inconsistent source/flux case and confirm it cannot receive accepted evidence status.

**Required artifacts:** `mclf/balances.py`; balance protocols and negative checks.

**Acceptance / decision:** Met for the frozen B-03/B-04/B-05 plane spheres and B-06 exterior shell; deliberately inconsistent flux/source terms fail, missing terms produce diagnostics instead of fabricated zeros. The result is a software numerical comparison only.

**If unsuccessful:** F-06; review control volume and source terms.

## ANA-07 — Publish P3 verification evidence and close the gate

**Current state:** ACTIVE — plane-field recorder is published and the first B03-01 recorded numeric comparison passes; remaining comparisons, audits and full campaign remain pending. See [ANA-07 task record](../../work-items/ANA-07.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-06

**Steps**

1. Implement and cross-check the versioned analytical field recorder and companion gradient index.
2. Admit an explicit spherical-source input bound to Scenario; do not represent it as a piston or plane wave.
3. Extend the initial B03-01 recorded comparison across admitted B-03/B-04/B-05 cases, then compare the complete admitted set with independent frozen references; report metrics, post-audits, precision/cancellation sensitivity and resource observations.
4. Reproduce a selected case and assemble the separate P3 gate review, including limitations and failures.

**Required artifacts:** `analysis/metrics.py` initial functions; plots/reports; P3 gate review; replay inputs for RUN-02.

**Acceptance / decision:** All selected analytic cases pass their predeclared checks; reproducibility and limitations are complete.

**If unsuccessful:** F-04/F-09/F-11; no numerical solver promotion before the required gate.

## Phase exit review

Selected closed-form cases pass independently derived tolerances, conventions and balances; reports include regime limits and reproducible manifests. These are verification results, not experimental validation.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
