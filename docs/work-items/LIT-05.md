# LIT-05 — Necessary Limits and Prior Work

**Status:** DONE as bounded research/design work · **Date:** 2026-10-03 · **Responsible role:** research implementer · **Baseline:** D00 v1.3 / PLAN-01 v1.3 · **Code revision:** `9ee66f7b1fb79eff807c078c102aae17bab09db6`

## Question and scope

Prepare necessary-condition analyses and compare primary prior work without choosing an acceleration target, body, hardware or actuator envelope. This work does not implement a solver, force or motion model and makes no physical feasibility or novelty claim.

## Method and outputs

- Prepared [L-01…L-05 symbolic limit design](../research/limits-design.md) from PLAN-01 and D02. It states the required immutable target inputs, kinematic workspace check, complete load-balance requirement, witness-versus-exclusion distinction, conditional momentum estimate and applicability indicators.
- Reviewed source-backed actuation information only where a declared experiment supplied it. Since AURA has no selected target or admissible actuator set, no numerical pressure/power feasibility screen was possible. Hypothetical budgets remain separate from hardware specifications.
- Compared nine primary-work records in the [prior-work register](../registers/prior-work.md), including measured forces across shapes, phased-array 3D manipulation, reduced-gravity droplet handling, microgravity biological trapping, closed-loop trajectory following and a Rayleigh-regime gravitation-like interpretation.
- Performed two scoped search cycles and focused follow-ups for closed-loop acoustic trajectory control and acoustic-gravitation terminology. Search boundaries and follow-up requirements are recorded; the search is not exhaustive and does not establish novelty.
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

**Focused novelty follow-up (2026-10-03):** a primary-source search for closed-loop acoustic trajectory control identified Matouš et al. (2019), now PW-08 in the prior-work register. This adds evidence that generic ultrasonic-array feedback positioning and reference-trajectory following are prior art. It does not change LIT-05's bounded status or make a novelty determination; the exact-target comparison remains open until AURA's body/domain/acceleration contract is selected.

**Terminology follow-up (2026-10-03):** a focused search identified Gires et al.'s arXiv preprint (PW-09), which explicitly interprets a Rayleigh-sphere radiation force as a “gravitation-like” apparent-buoyancy effect under an idealized infinite, inviscid-fluid model. The arXiv record lists no journal reference. The result is scoped to that theory and does not establish AURA's claim, field or novelty; the exact-target comparison remains open.

Open target inputs remain in UNK-004…UNK-013, especially body and material, gravity environment, target/time/workspace/observation and actuator constraints. UNK-002/UNK-008 preserve measurement and uncertainty gaps; UNK-015 preserves the particle-inertia discrepancy. SC-01 and SC-02 are complete under DEC-004. The owner recorded bounded P3 PASS on 2026-10-03; numerical field work is now gated by the unresolved NUM-01 P4 benchmark/domain choice, and formal measurement acceptance remains INDETERMINATE. Any transition to P4 or core simulation work must follow the work-board dependencies and the already-delivered explanation checkpoint.
