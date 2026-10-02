# Task Record Template

Copy to `docs/work-items/<task-id>.md` when the task begins. Replace every placeholder or record NOT_APPLICABLE with a reason. Unknown scientific inputs must link to a resolution task; implementation that requires them waits or uses a separately labeled manufactured verification case.

## Identity and authority

- Task ID / phase / parent PLAN-01 work package:
- State / opened date / responsible person or role:
- Applicable D documents, rules, equations and decision records:
- Predecessor artifacts and versions / required gate decisions:
- One-sentence question and intended bounded output:

## Scientific and implementation contract

- Hypothesis/prediction and quantifiers:
- Falsification or rejection condition:
- Body/material, medium/state, geometry, source/frequency/drive, boundary conditions:
- Frame, gravity/environment, initial state, time window and observation definition:
- Equations, assumptions, model regime, omitted terms and their justification:
- Primary observable: formula, units, sample/window/filter and normalization:
- Reference/independent expected value and exact source locator:
- Acceptance rule/tolerance and derivation; uncertainty/correlation assumptions:
- Input/output schema versions and example fixtures:
- Exact implementation/documentation paths and interface changes:
- Required positive, negative, limiting and independent checks:
- Resource estimate, RAM/disk/wall-time/run-count caps and stop condition:
- Non-goals and parked ideas:

## Execution checklist

- [ ] Confirm dependency and gate evidence.
- [ ] Freeze the protocol/configuration before computation.
- [ ] Implement only named artifacts.
- [ ] Run meaningful checks and preserve failures.
- [ ] Record source, environment, data identity and relevant run IDs.
- [ ] Complete full current CI before commit; inspect diff and owner identity.
- [ ] Verify the exact commit's remote CI after authorized push.
- [ ] Update traceability, limitations and the board.

## Outcome

Expected versus observed result; measured values and uncertainty; actual artifact/commit/run/CI links; invalidated/failed attempts; anomaly or branch IDs; interpretation bounded to the evidence; unresolved conditions; reviewer/date; DONE or named remaining work; next eligible task.
