# 00 — Execution Protocol and Anti-Drift Rules

## Authority and current facts

Read [D00](../D00-document-control.md), the phase's relevant D documents, and G01–G05. [DEC-003](../decisions/DEC-003-nonblocking-foundation-work.md) permits foundation work while benchmark evidence remains incomplete. The original P1 benchmark remains a 50 mm sphere in air; the intended application discussed by the owner is small particles in water progressing toward microgravity. Keep those domains explicit and separate.

The code inventory was inspected at commit `aaf4aba7bff3774e645b3640784ebdcdbd14a7db`: CLI status, four SI helper functions, and nine passing tests. No field, force, motion or control solver is implemented. All other paths in this pack are planned unless marked existing.

## Execute a task

1. Select the earliest READY card in the [board](10-work-board.md). Set one ACTIVE implementation card; a separate bounded literature task may remain active.
2. Confirm dependency artifacts and their versions. A linked plan is not an implemented dependency.
3. Copy the [task template](templates/task-record.md) into `docs/work-items/<task-id>.md` when work starts. Populate the scientific question, domain, primary observable, code paths, tests, source equations, input/output types, resource cap, and decision condition.
4. For research tasks, define the search question and evidence stopping rule. For implementation tasks, resolve the applicable equation, interface and acceptance criteria first.
5. Derive the tolerance from the reference precision, discretization/error budget or measurement uncertainty. If it cannot be justified, implement infrastructure or mark the science exploratory; do not invent a PASS tolerance.
6. Implement the smallest slice named by the card. Update its equation-to-code-to-test mapping and documentation.
7. Run meaningful checks for the change and the complete CI sequence before every commit. Inspect the staged diff and owner identity. Follow [08](08-reproducibility-and-ci.md).
8. Produce a short report: expected result, actual result, evidence paths, failed attempts, limits, decision, next eligible task.
9. Move to REVIEW. A recorded gate review or artifact review closes the card as DONE; do not silently assume that green CI is a scientific review.

## Unknowns that do not halt unrelated work

| Unknown | Continue now | Dependent work that must wait |
|---|---|---|
| Particle material or radius | Schemas, dimension checks, parameterized analytical functions | A claim about a particular physical particle |
| Measured uncertainty | Source inventory, numerical verification, descriptive comparison | Formal experimental validation PASS |
| Suitable frequency/geometry | Analytical cases with labeled manufactured values; source comparison | The specific water benchmark or hardware claim |
| Actuator limits | Feasibility interface and symbolic/explicit hypothetical budget studies | Hardware-feasibility claim |
| Microgravity disturbances | Ideal zero-gravity model and parameterized disturbance inputs | Real platform performance claim |
| Independent reviewer | Assemble and reproduce the evidence bundle | Claim or release gate requiring that review |

Every placeholder has `status`, owner role, resolution task and affected gate. Physical input `null` is valid only in a research record; it is rejected by a run that needs the value. Manufactured examples are labeled and never presented as measured properties.

## Stops and retries

- Preserve the original configuration and outputs before debugging; create a new run for each attempt.
- After two consecutive cycles fail for the same cause, write a root-cause record before a third feature attempt.
- Research cycle: one stated question, a recorded query set, primary records inspected, evidence table, and gap conclusion. After two cycles with the same unavailable evidence, mark that comparison INDETERMINATE and continue tasks that do not need it.
- Solver runs need explicit RAM, disk, wall-time, iteration and refinement caps. No unbounded sweep or endless convergence loop.
- When a cap is exceeded, follow F-04 or F-05 in [06](06-failure-playbooks.md). Changing physics to fit a computer creates a new experiment; it is not a retry of the original one.
- New features go to a parking list attached to the task, with a scientific need and dependency. They do not enter current implementation automatically.

## Review and ownership

The implementer prepares evidence. A qualified independent reviewer is needed where P9/P10 or the baseline explicitly requires one; name and availability are currently unassigned. The project owner makes scientific scope, hardware expenditure and experiment-authorization decisions. Routine code structure, bug fixes and test corrections proceed within the approved task.

A phase review uses PASS, FAIL, HOLD or INDETERMINATE. A run has separate execution state, MCLF verdict, comparison outcome and claim status. Do not collapse these into one success flag. See [08](08-reproducibility-and-ci.md).

## Definition of a completed task

- Required artifacts exist and have references or hashes.
- Its intended checks have actual results, including negative cases.
- Equation/source and D03 traceability is updated.
- No unresolved issue has been hidden in a default or changed threshold.
- Known limits and applicable next branch are recorded.
- CI passes for the exact committed content, and the corresponding remote run passes after publication.

A planning document by itself satisfies a research-design card only; it does not satisfy a solver, measurement or validation card.
