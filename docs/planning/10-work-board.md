# 10 — Single Work Board and Execution Order

**Updated:** 2026-10-02. **Initial implementation inspected:** `aaf4aba7bff3774e645b3640784ebdcdbd14a7db`; completed work is linked below.

## First work cycle

1. FND-01 is complete: [CONV-1.0 and review](../work-items/FND-01.md) freeze the representation contract and record existing helper gaps.
2. FND-02 and FND-03 are complete: [schemas](../work-items/FND-02.md), [safe arithmetic and explicit conversions](../work-items/FND-03.md). Continue FND-04…FND-08 in dependency order; close P2 only with its actual evidence.
3. LIT-01…LIT-05 may proceed as the separate evidence track; missing measurements do not stop P2/P3.
4. Build RUN-01, then ANA-01…ANA-07. Complete RUN-02 before NUM-07 closes P4.
5. Follow the remaining phase gates and decision tree. Do not start controller implementation before the required force/dynamics gates.

FND-04 is the next READY implementation task. LIT-01 and SC-01 remain READY for research. Existing helpers/tests are PARTIAL evidence for P2; only explicitly reviewed task records are DONE. BLOCKED below means a normal dependency has not yet been delivered, not that the whole project must stop.

## Dependency and status table

| Task | Work item | Predecessors | Current state | Phase card |
|---|---|---|---|---|
| LIT-01 | Inventory the current evidence and unresolved decisions | Baseline available | READY | [LIT](phases/P01-evidence.md) |
| LIT-02 | Select a measurable water reference or document the bounded fallback | LIT-01 | BLOCKED | [LIT](phases/P01-evidence.md) |
| LIT-03 | Review the actual force equations and their domain | LIT-02 | BLOCKED | [LIT](phases/P01-evidence.md) |
| LIT-04 | Identify fluid, wall, thermal and stochastic competing effects | LIT-03 | BLOCKED | [LIT](phases/P01-evidence.md) |
| LIT-05 | Prepare necessary-limit and prior-work investigations | LIT-04 | BLOCKED | [LIT](phases/P01-evidence.md) |
| FND-01 | Freeze coordinate, SI and amplitude conventions | Baseline available | DONE — [record](../work-items/FND-01.md) | [FND](phases/P02-foundations.md) |
| FND-02 | Implement versioned scenario and evidence schemas | FND-01 | DONE — [record](../work-items/FND-02.md) | [FND](phases/P02-foundations.md) |
| FND-03 | Extend safe SI calculations and conversion boundaries | FND-02 | DONE — [record](../work-items/FND-03.md) | [FND](phases/P02-foundations.md) |
| FND-04 | Implement stable MCLF L0 rules and typed errors | FND-03 | READY | [FND](phases/P02-foundations.md) |
| FND-05 | Build independent known-answer and invalid-input verification | FND-04 | BLOCKED | [FND](phases/P02-foundations.md) |
| FND-06 | Expose configuration validation through the CLI | FND-05 | BLOCKED | [FND](phases/P02-foundations.md) |
| FND-07 | Freeze canonical serialization and immutable hash identity | FND-06 | BLOCKED | [FND](phases/P02-foundations.md) |
| FND-08 | Lock the development environment and close P2 | FND-07 | BLOCKED | [FND](phases/P02-foundations.md) |
| ANA-01 | Specify field outputs and the analytic case matrix | FND-08, RUN-01 | BLOCKED | [ANA](phases/P03-analytical-fields.md) |
| ANA-02 | Implement a progressive plane wave and its velocity | ANA-01 | BLOCKED | [ANA](phases/P03-analytical-fields.md) |
| ANA-03 | Construct a standing wave with correct flux accounting | ANA-02 | BLOCKED | [ANA](phases/P03-analytical-fields.md) |
| ANA-04 | Verify two-source interference and allowed symmetries | ANA-03 | BLOCKED | [ANA](phases/P03-analytical-fields.md) |
| ANA-05 | Add only the needed spreading or attenuation reference | ANA-04 | BLOCKED | [ANA](phases/P03-analytical-fields.md) |
| ANA-06 | Add independent model-specific balance checks | ANA-05 | BLOCKED | [ANA](phases/P03-analytical-fields.md) |
| ANA-07 | Publish P3 verification evidence and close the gate | ANA-06 | BLOCKED | [ANA](phases/P03-analytical-fields.md) |
| NUM-01 | Choose one backend that answers the selected question | ANA-07, LIT-02 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-02 | Implement resource preflight before allocation | NUM-01 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-03 | Implement the selected field backend | NUM-02 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-04 | Measure observable convergence across three levels | NUM-03 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-05 | Bound boundary and domain contamination | NUM-04 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-06 | Reconcile cost, precision and reproducibility | NUM-05 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-07 | Close the field solver gate | NUM-06, RUN-02 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| FOR-01 | Freeze the force-model contract and regime checks | NUM-07, LIT-03 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-02 | Implement one particle-force model and typed results | FOR-01 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-03 | Challenge signs, limits and conservative gradients | FOR-02 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-04 | Compare the force against an independent model reference | FOR-03 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-05 | Prepare and execute the matched water measurement comparison | FOR-04, LIT-02 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-06 | Resolve viscosity, thermal and streaming branches | FOR-05, LIT-04 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-07 | Audit force accounting and conditional limits | FOR-06 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-08 | Review the force-model gate and evidence dependencies | FOR-07 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| MOT-01 | Select resolved versus reduced dynamics | FOR-08, LIT-04 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-02 | Implement a complete and inspectable load ledger | MOT-01 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-03 | Implement deterministic translation with analytic references | MOT-02 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-04 | Resolve time refinement and workspace events | MOT-03 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-05 | Implement the declared rotational contract | MOT-04 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-06 | Compare Earth, ideal zero and residual-gravity cases | MOT-05 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-07 | Add stochastic motion only when required | MOT-06 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-08 | Compare water motion, report and close P6 | MOT-07, FOR-05 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| CTL-01 | Freeze the acceleration target and cheap necessary conditions | MOT-08, LIT-05 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-02 | Characterize attainable force and local authority | CTL-01 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-03 | Implement bounded actuation allocation | CTL-02 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-04 | Implement one deterministic feedback controller | CTL-03 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-05 | Add realistic virtual observations and a minimal estimator | CTL-04 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-06 | Run the frozen acceleration evaluation | CTL-05 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-07 | Review bounded control and authorize robustness work | CTL-06 | BLOCKED | [CTL](phases/P07-target-control.md) |
| ADV-01 | Derive and audit necessary-condition limits | CTL-07 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-02 | Freeze and run deterministic sensitivity attacks | ADV-01 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-03 | Quantify uncertainty and stochastic robustness where justified | ADV-02 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-04 | Stress the water and microgravity assumptions | ADV-03 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-05 | Recheck the strongest positive and negative cases | ADV-04 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-06 | Publish a domain map with all evidence statuses | ADV-05 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-07 | Close robustness and select independent confirmation cases | ADV-06 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| IND-01 | Choose an appropriately independent formulation | ADV-07 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-02 | Implement or configure the independent comparison | IND-01 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-03 | Reproduce critical runs from a fresh environment | IND-02 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-04 | Obtain technical review and close bounded claims | IND-03 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-05 | Release the bounded research simulator and evidence package | IND-04 | BLOCKED | [IND](phases/P09-independent-review.md) |
| EXP-01 | Select the smallest experiment that could change the conclusion | IND-05 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-02 | Design measurement, calibration and uncertainty analysis | EXP-01 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-03 | Estimate resources and review the actual hardware risks | EXP-02 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-04 | Review the design and record GO, REVISE or NO-GO | EXP-03 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-05 | Close the planning-to-evidence chain and hand off | EXP-04 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| RUN-01 | Immutable minimal run lifecycle | FND-08 and P2 PASS | BLOCKED | [Cross-cutting card](08-reproducibility-and-ci.md) |
| RUN-02 | Replay, comparison and evidence reporting | RUN-01, ANA-07 | BLOCKED | [Cross-cutting card](08-reproducibility-and-ci.md) |
| SC-01 | Register candidate mass, size and shape campaigns | DEC-004; LIT-01 inventory when available | READY for research | [Scale progression](11-scale-progression.md) |
| SC-02 | Establish whether a model change is needed | SC-01; relevant source/applicability review | BLOCKED | [Scale progression](11-scale-progression.md) |
| SC-03 | Verify and compare larger-body forces | SC-02 and candidate foundation/field gates | BLOCKED | [Scale progression](11-scale-progression.md) |
| SC-04 | Test acceleration and rotational behavior | SC-03 and candidate force/dynamics gates | BLOCKED | [Scale progression](11-scale-progression.md) |
| SC-05 | Publish limits across investigated scales | SC-04 outcome or reviewed earlier limitation | BLOCKED | [Scale progression](11-scale-progression.md) |

## Review queue and external dependencies

- P5 water-reference selection may reveal that validation must use measured motion rather than direct force. FOR-08 must then prepare a bounded coupled-validation subphase decision before bypassing the original force/dynamics gate. This is an explicit research branch, not a hidden dependency cycle.
- IND-04 requires an actual independent qualified reviewer; prepare the complete package first and do not invent approval.
- EXP-04 requires actual owner/domain-expert review of the concrete design. No procurement or operation is authorized by this pack.
- Actuator hardware, particle material/radius, target magnitude/duration and experiment measurement choices are unresolved physical decisions with named tasks. Parameterized software and analytical verification can proceed before those values are fixed.

## Update rules

When a task changes state, record date, responsible role/person, evidence paths, commit, actual checks, open limitations and next branch in its work-item record. Update predecessor/gate references if a reviewed decision changes sequencing. A card with an INDETERMINATE research finding may be DONE as an investigation; its scientific comparison/gate remains INDETERMINATE.

## Parking list

Greater masses, larger objects and other body geometries belong to the planned SC track above. They are not excluded from the program. Exact candidate domains and numerical campaigns still need their own evidence review.

Human-scale use; arbitrary body-independent acceleration; a 5 m station; hardware procurement/operation; learning controllers; web/cloud product; multi-particle optimization without interaction evidence; multiple high-fidelity backends without a discriminating question. Add a proposal with scientific benefit and required gate before moving any into active scope.
