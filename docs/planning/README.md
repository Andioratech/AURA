# AURA Simulator, Evidence and Falsification Execution Pack

**Version:** 1.1 · **Prepared:** 2026-10-02 · **Status:** Execution planning; scientific choices remain subject to their gates

## Intended result

Build a reproducible simulator that can investigate controlled acoustic forcing and prescribed acceleration for selected bodies, starting with small particles in water and explicitly researching greater masses, larger objects and other geometries. Prepare validation against measurements and actively seek counterexamples and physical or mathematical limitations while progressing toward an explicitly modeled microgravity environment. A supported restricted domain, a negative finding, or a documented evidence gap are all legitimate outcomes.

The particle campaign is the starting case. The required [scale progression track](11-scale-progression.md), recorded in [DEC-004](../decisions/DEC-004-staged-mass-and-size-expansion.md), keeps larger-body research within the project objective; each new regime needs its own applicable model and evidence.

This pack decomposes [PLAN-01](../PLAN-01-project-execution-plan.md); [D00](../D00-document-control.md) through D09 retain precedence. It supplies research tasks, implementation specifications, verification work, decision branches, failure recovery, and report templates. It does not claim that the planned software exists or that a numerical tolerance, particle size, actuator, or experimental design has already been approved.

## Start and follow

1. Read [execution rules](00-execution-protocol.md) and [scientific objective](01-objective-and-domain.md).
2. Open [the work board](10-work-board.md) and select the next READY task; completed tasks link their actual evidence. LIT-01 may proceed as a separate evidence task.
3. Open the linked phase card. Carry out its numbered steps and produce every named artifact.
4. Complete the [task record](templates/task-record.md), including input versions and acceptance criteria, before implementation.
5. If a decision is needed, follow [the decision tree](05-decision-tree.md). If an attempt fails, use [the matching recovery playbook](06-failure-playbooks.md).
6. Finish the card's checks, retain unsuccessful attempts, and record the result. Mark DONE only with artifact and review references.
7. At a phase exit, complete [the gate review](templates/gate-review.md). Continue only along the permitted dependency path.

The pack is intended to make the next action unambiguous. Research outcomes cannot be prescribed: an unresolved parameter becomes a named investigation or a bounded assumption, never a fabricated value. Routine implementation choices within an approved domain do not require repeated owner confirmation.

## Navigation

| Document | Use it to |
|---|---|
| [00 — Execution protocol](00-execution-protocol.md) | Run one task, handle unknowns, stop drift and close gates |
| [01 — Objective and domain](01-objective-and-domain.md) | Define what would support or refute the bounded idea |
| [02 — Research and source plan](02-research-and-sources.md) | Review primary sources, choose water benchmarks and fill equation records |
| [03 — Software construction map](03-software-build-map.md) | Identify every planned module, interface, command and implementation dependency |
| [04 — Verification and validation matrix](04-benchmarks-and-acceptance.md) | Freeze references, metrics, tolerances and independent checks |
| [05 — Decision tree](05-decision-tree.md) | Select the next branch based on evidence |
| [06 — Failure recovery](06-failure-playbooks.md) | Diagnose failures and decide when to stop retrying |
| [07 — Attempts to break the idea](07-falsification-and-limits.md) | Test adversarial cases and distinguish a limit from an optimizer failure |
| [08 — Reproduction and delivery](08-reproducibility-and-ci.md) | Preserve runs, environments, data, CI checks and owner commit identity |
| [09 — Requirement traceability](09-requirement-traceability.md) | Map D03 requirements to code, tasks, tests and evidence |
| [10 — Work board](10-work-board.md) | Find task order, current state and dependency gates |
| [11 — Scale progression](11-scale-progression.md) | Investigate greater masses, larger dimensions and other body geometries with explicit transition gates |
| [Phase cards](phases/P02-foundations.md) | Execute the individual work packages |
| [Templates](templates/task-record.md) | Create consistent task, experiment, gate, decision, anomaly and claim records |

## Delivery milestones

| Milestone | Required evidence | What may be said |
|---|---|---|
| M0 — Current scaffold | Existing unit helpers and CI, source documents | Foundational code exists; simulator absent |
| M1 — Safe and reproducible inputs | P2 gate | Invalid inputs are rejected before solver allocation |
| M2 — Verified acoustic field | P3 and P4 gates | Declared equations are solved correctly within measured numerical error |
| M3 — Particle response model | P5 and P6 gates, matched water evidence | Force/motion predictions have the explicitly recorded evidence status |
| M4 — Bounded acceleration trial | P7 gate and target contract | A specified target succeeds or fails in the declared model and time window |
| M5 — Limits map | P8 and P9 gates | A domain and its uncertainties/contradictions have been independently examined |
| M6 — Experiment decision | P10 gate | A specific experiment is worth revising, pursuing, or rejecting |

M3 cannot be called experimentally validated while its required water measurement evidence is incomplete. Exploratory work can continue under DEC-003, with no promotion of the affected claim. An air-sphere comparison is a separate reference and cannot supply missing water evidence.

## Pack completion versus project completion

This folder is the planning deliverable. Task checkboxes describe future work, not completed results. The simulator is complete for its first bounded research release only after P2–P9 evidence is traceable, all applicable MUST requirements are satisfied or formally scoped in a reviewed release, and a reproduction bundle exists. A smaller one-particle demonstrator is an intermediate milestone, not completion of all D03 requirements or of the larger-body research objective. SC-01–SC-05 track subsequent scale investigations and reuse the applicable phase gates for each candidate.
