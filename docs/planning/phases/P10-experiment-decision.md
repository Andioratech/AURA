# P10 — Measurable Experimental Design and Decision

**Maps to:** P10.1–P10.7; D05/D06/D07/D09; G05

## Entry condition

P9 provides a reviewed bounded result, including a useful negative/inconclusive result where an experiment could distinguish models. Planning does not authorize purchase, construction or operation.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## EXP-01 — Select the smallest experiment that could change the conclusion

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** IND-05

**Steps**

1. Identify the exact unresolved physical claim and competing predictions from the evidence review.
2. Choose a water particle/material and geometry whose observable can distinguish those predictions.
3. Include no-drive controls, source calibration, an independent validation observation and a reference/control condition.
4. Explain how a ground experiment informs the eventual microgravity case and what it cannot establish.

**Required artifacts:** Experimental question and design alternatives; discrimination analysis.

**Acceptance / decision:** The proposed observation is informative about the bounded claim and is not merely a visually appealing demonstration.

**If unsuccessful:** D-01/D-12/F-02; revise observable/geometry or recommend NO-GO.

## EXP-02 — Design measurement, calibration and uncertainty analysis

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** EXP-01

**Steps**

1. Specify measurement hardware capabilities as requirements before choosing products; derive needed spatial/time/force resolution.
2. Define calibration, repetitions, reference controls, sample selection and analysis protocol before data collection.
3. Build a sourced uncertainty budget and assess whether it can distinguish predictions; separate calibration and validation data.
4. Write data schemas, timestamps, acquisition provenance and retention requirements.

**Required artifacts:** Measurement protocol; uncertainty/discrimination budget; data/analysis plan.

**Acceptance / decision:** Measurement uncertainty is small enough for the specified decision or the design explicitly fails that requirement.

**If unsuccessful:** F-02/F-08; revise the experiment or retain an inconclusive expectation.

## EXP-03 — Estimate resources and review the actual hardware risks

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** EXP-02

**Steps**

1. Estimate transducer/chamber/measurement requirements, acoustic versus electrical power, thermal behavior, compute and sourced cost.
2. Assess exposure, cavitation/heating and equipment/institutional requirements relevant to the proposed apparatus with qualified expertise.
3. Identify procurement, facilities, operator competence and review dependencies without making purchases.
4. Define explicit operating/stop limits and unresolved hardware assumptions in the design.

**Required artifacts:** Sourced design/resource dossier; applicable risk and review records; budget proposal.

**Acceptance / decision:** A qualified reviewer can assess the concrete apparatus and constraints; hypothetical simulator limits are not treated as hardware specifications.

**If unsuccessful:** F-03/F-05/F-11; revise or hold the specific design.

## EXP-04 — Review the design and record GO, REVISE or NO-GO

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** EXP-03

**Steps**

1. Present the complete design, discrimination capability, uncertainties, cost and applicable review findings.
2. Record actual owner and qualified domain-expert review and any conditions.
3. If GO, define the separate authorized execution scope; if REVISE, assign exact tasks; if NO-GO, retain the evidence-backed reason.
4. Keep microgravity hardware or human-scale expansion outside this decision unless independently proposed and reviewed.

**Required artifacts:** Signed/attributed decision record and next-stage scope.

**Acceptance / decision:** A real review decides the concrete proposal; absence of a response is not authorization.

**If unsuccessful:** F-11; keep the review pending while independent documentation/reproduction tasks continue.

## EXP-05 — Close the planning-to-evidence chain and hand off

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** EXP-04

**Steps**

1. Link research question → equations → code → tests → runs → uncertainty/limits → independent review → experiment decision.
2. Document remaining unknowns, rejected paths, costs and the next permitted work item.
3. Archive obsolete planning revisions without losing failures or changing past conclusions.
4. Provide a plain-language outcome explaining what is known, what failed and what would change the decision.

**Required artifacts:** P10 gate review; complete evidence/decision index; next-stage handoff.

**Acceptance / decision:** The project can continue, revise its goal or stop with a defensible bounded result and reproducible record.

**If unsuccessful:** F-09/F-11; repair missing provenance or explicitly retain an unresolved outcome.

## Phase exit review

One experiment can distinguish the stated alternatives with a justified measurement budget and reviewed constraints; record GO, REVISE or NO-GO with actual owner/domain-expert review.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
