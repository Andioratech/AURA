# P1 — Water Evidence and Model Research

**Maps to:** P1.1–P1.7; D04/D06/D09; DEC-002/DEC-003

## Entry condition

May proceed alongside P2. Preserve the existing air benchmark and source-data limitations.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## LIT-01 — Inventory the current evidence and unresolved decisions

**Current state:** DONE — [task record](../../work-items/LIT-01.md), [evidence inventory](../../research/evidence-inventory.md) and [unknowns register](../../registers/unknowns.md). The inventory distinguishes software verification from physical validation, retains the air benchmark's uncertainty limit, and leaves water-model inputs unresolved. It does not close P1 or decide P3. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** Current baseline, code inventory and owner direction; no new physical run required.

**Steps**

1. Read existing benchmark and decision records; list which statements apply to the air sphere and which remain untested for water.
2. Create a gap register for particle/material, chamber, temperature, frequency, calibration, measured observable, uncertainty and microgravity assumptions.
3. Assign each gap a resolution task and affected gate; label all currently available code and evidence honestly.

**Required artifacts:** `docs/research/evidence-inventory.md`; `docs/registers/unknowns.md`; links to preserved air data.

**Acceptance / decision:** Every necessary unknown has an owner role and follow-up; no water validation is inferred from the air result.

**If unsuccessful:** F-02; continue FND-01 while evidence search proceeds.

## LIT-02 — Select a measurable water reference or document the bounded fallback

**Current state:** DONE as a bounded search and design task; formal measurement benchmark remains INDETERMINATE — [task record](../../work-items/LIT-02.md) and [selection record](../../benchmarks/water-reference-selection.md). SRC-W03 is the preferred exploratory reference; raw supplement access and measurement uncertainty remain unresolved. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** LIT-01

**Steps**

1. Review SRC-W03 and at least one alternative primary measurement relevant to the intended particle regime; extract all matching parameters and calibration dependence.
2. Compare force versus velocity/trajectory observables, data availability, uncertainty, geometry complexity and likely resource cost.
3. Select the most informative reproducible reference and freeze its matching table. If none is complete after the research cap, record an exploratory reference and a synthetic verification case with separate identities.
4. Specify the investigation needed to replace missing evidence. Prepare an owner choice only if material/target scope changes are needed.

**Required artifacts:** `docs/benchmarks/water-reference-selection.md`; candidate matrix; source/property records; benchmark design.

**Acceptance / decision:** Selection/rejection reasons and measurement limits are explicit; enough domain information exists for analytical/numerical verification. Formal measurement acceptance remains separate.

**If unsuccessful:** D-01/F-02; do not wait indefinitely or invent a tolerance.

## LIT-03 — Review the actual force equations and their domain

**Current state:** DONE as a literature model/applicability review — [task record](../../work-items/LIT-03.md), [model-selection review](../../research/particle-model-selection.md), and EQ-013–015 in the [equation register](../../registers/equations.md). Candidate equations and independent checks are recorded; no force implementation contract is frozen. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** LIT-02

**Steps**

1. Use SRC-W01/SRC-W02 and relevant primary work to extract equations, coefficients, conventions and assumptions with exact page/equation locators.
2. Calculate or symbolically define particle/wavelength, viscosity/thermal, amplitude and wall-distance indicators for the selected domain.
3. Compare candidate inviscid, viscous and thermoviscous models; choose the simplest justified one and name the trigger for each refinement.
4. Record a separate path for a large-object air-scattering model only if its value justifies that scope.

**Required artifacts:** `docs/research/particle-model-selection.md`; `docs/registers/equations.md`; applicability table.

**Acceptance / decision:** Every equation intended for FOR-01 has a primary source, symbol/unit mapping, stated assumptions and an independent reference plan.

**If unsuccessful:** D-02/D-03/F-03; use a smaller explicitly new domain or research the required model.

## LIT-04 — Identify fluid, wall, thermal and stochastic competing effects

**Current state:** DONE as a bounded effect ledger and calibration-dependence review — [task record](../../work-items/LIT-04.md), [fluid/omitted-effects record](../../research/fluid-and-omitted-effects.md), and [unknowns register](../../registers/unknowns.md). Coupled magnitudes and matched measurement acceptance remain open. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** LIT-03

**Steps**

1. Build the complete candidate force/motion ledger; distinguish radiation, streaming advection, drag, gravity/buoyancy and unsteady-fluid terms.
2. Estimate each potentially omitted contribution with sourced scales or explicit intervals; compare with the target observable budget.
3. Check whether available measurements calibrate pressure through the same particle motion used for evaluation.
4. Propose a fluid-motion reference and a calibration/holdout strategy; leave unsupported effects as named gaps.

**Required artifacts:** `docs/research/fluid-and-omitted-effects.md`; property/uncertainty register; calibration dependence diagram.

**Acceptance / decision:** Omissions have quantitative or explicit unresolved justification; no term is silently dropped because microgravity is modeled.

**If unsuccessful:** D-05/D-06/F-03; choose a qualified streaming/dynamics branch.

## LIT-05 — Prepare necessary-limit and prior-work investigations

**Current state:** DONE as bounded research/design work — [task record](../../work-items/LIT-05.md), [symbolic limit design](../../research/limits-design.md), [prior-work register](../../registers/prior-work.md), and [P1 review draft](../../reviews/P1-research-gate-review-draft.md). Formal P1 measurement acceptance remains INDETERMINATE. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** LIT-04

**Steps**

1. Review source-backed actuation constraints and the intended observation/duration requirements; separate hypothetical budgets from hardware specifications.
2. Draft the L-01…L-05 analyses and identify assumptions still required for a useful exclusion.
3. Record comparable prior acoustic manipulation work and exactly what the planned acceleration claim would add or fail to add.
4. Close the initial research dossier with unresolved inputs, next searches and eligible implementation tasks.

**Required artifacts:** `docs/research/limits-design.md`; `docs/registers/prior-work.md`; P1 research review.

**Acceptance / decision:** The dossier enables a discriminating force/motion study and a bounded feasibility question; novelty and physical success remain unclaimed.

**Finding:** No target-specific limit is calculable until the body, target, duration, workspace, complete loads and admissible actuator set are fixed. Primary prior art already includes acoustic force characterization, 3D phased-array manipulation, reduced-gravity droplet handling and microgravity sample trapping. Any distinct AURA question remains a candidate, not an established novelty claim.

**If unsuccessful:** D-07/D-11; continue eligible foundation work and record the missing evidence.

## Phase exit review

A bounded water question, parameter/source map, model-selection evidence and reference protocol exist. A missing measurement can close a research-design task with an explicit gap, but cannot close formal validation as PASS.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
