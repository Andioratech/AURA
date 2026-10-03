# LIT-05 — Necessary Limits and Prior Work

**Status:** DONE as bounded research/design work · **Date:** 2026-10-03 · **Responsible role:** research implementer · **Baseline:** D00 v1.3 / PLAN-01 v1.3 · **Code revision:** `9ee66f7b1fb79eff807c078c102aae17bab09db6`

## Question and scope

Prepare necessary-condition analyses and compare primary prior work without choosing an acceleration target, body, hardware or actuator envelope. This work does not implement a solver, force or motion model and makes no physical feasibility or novelty claim.

## Method and outputs

- Prepared [L-01…L-05 symbolic limit design](../research/limits-design.md) from PLAN-01 and D02. It states the required immutable target inputs, kinematic workspace check, complete load-balance requirement, witness-versus-exclusion distinction, conditional momentum estimate and applicability indicators.
- Reviewed source-backed actuation information only where a declared experiment supplied it. Since AURA has no selected target or admissible actuator set, no numerical pressure/power feasibility screen was possible. Hypothetical budgets remain separate from hardware specifications.
- Compared seven primary-work records in the [prior-work register](../registers/prior-work.md), including measured forces across shapes, phased-array 3D manipulation, reduced-gravity droplet handling, and microgravity biological trapping.
- Performed two scoped search cycles. Search boundaries and follow-up requirements are recorded; the search is not exhaustive and does not establish novelty.
- Drafted [P1 research review](../reviews/P1-research-gate-review-draft.md). The task acceptance is met for research design, while the P1 phase's formal evidence/measurement acceptance remains INDETERMINATE.

## Findings

1. L-01 and L-02 cannot yield target-specific numbers before the owner-selected body, acceleration history, duration, workspace, environment and complete dynamics are fixed.
2. L-03 requires a checked feasible witness for a modeled success; failure of finite search alone cannot establish exclusion.
3. L-04's plane-wave momentum-transfer estimate remains conditional on its declared incident progressive-wave control volume and is not a universal standing-wave or resonator bound.
4. Prior art already covers acoustic force measurement, levitation, phased-array manipulation, reduced-gravity droplet transport and microgravity sample trapping. No broad novelty claim is warranted.
5. A useful candidate distinction is predictive, traceable acceleration tracking for an explicitly declared body and domain, with field quality, closed-loop performance and gravity-like generality assessed separately. No such AURA capability is demonstrated.

## Acceptance and validation

The required analysis and primary-source comparison artifacts exist, use explicit domain boundaries, and keep unknown values unresolved. Local document checks are recorded in the current handoff after completion. Formal P1 phase closure is **INDETERMINATE**, because the water measurement and uncertainty gaps remain, including UNK-002 and UNK-008. The artifact does not authorize force/dynamics implementation or a physical claim.

## Open inputs and next route

Open target inputs remain in UNK-004…UNK-013, especially body and material, gravity environment, target/time/workspace/observation and actuator constraints. UNK-002/UNK-008 preserve measurement and uncertainty gaps; UNK-015 preserves the particle-inertia discrepancy. SC-01 is the next independent READY research task under DEC-004. P3/ANA-07 still has a separate pending owner phase decision; numerical field work remains behind P3. Any transition to P4 or core simulation work must follow the work-board dependencies and the already-delivered explanation checkpoint.
