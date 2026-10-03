# P1 Research Gate Review — Draft

## Review identity

- **Gate:** P1 water evidence and model research
- **Date:** 2026-10-03
- **Scope:** documentary research design and source comparison completed through LIT-05; no physical target or experiment executed
- **Baseline:** D00 v1.3 / PLAN-01 v1.3
- **Checkout revision:** `9ee66f7b1fb79eff807c078c102aae17bab09db6`
- **Preparer:** research implementer; owner phase decision not recorded
- **Relevant decisions:** DEC-002, DEC-003, DEC-004

## Evidence table

| Criterion | Artifact | Finding | Threshold / decision basis | Limitation | Status |
|---|---|---|---|---|---|
| Bounded water reference with explicit observable and gaps | [LIT-02 selection](../benchmarks/water-reference-selection.md) | SRC-W03 retained as exploratory particle-velocity-field reference; ALT-W01 retained as an alternative; synthetic fixture separated | P1 selection requires a reproducible design or bounded fallback, while measurement acceptance remains separate | Raw acquisition data and full measurement uncertainty unavailable in reviewed sources | Met for design; measurement INDETERMINATE |
| Candidate equations and applicability reviewed | [LIT-03 model review](../research/particle-model-selection.md), equation register EQ-013–015 | Viscous and thermoviscous sphere candidates compared; no implementation law frozen | Domain and model limitations must be explicit before implementation | Matched amplitude, property uncertainty and coupled effects remain open | Met for research design |
| Competing effects and calibration dependence accounted for | [LIT-04 ledger](../research/fluid-and-omitted-effects.md) | Radiation, streaming/drag, walls, thermal, gravity, Brownian, concentration and inertia recorded | No effect silently omitted from future matched comparison | No coupled quantitative uncertainty budget; UNK-015 unresolved | Met for bounded ledger; model adequacy INDETERMINATE |
| Necessary limits and prior work bounded | [LIT-05 limit design](../research/limits-design.md), [prior-work register](../registers/prior-work.md) | Symbolic L-01…L-05 criteria and twenty primary-work comparisons recorded, including feedback/feedforward motion control, tested acceleration-shaped motion, material-dependent force modeling, phased-array particle transport, acceleration-inferred force measurement, stable-acceleration-limit experiments, Rayleigh-regime “gravitation-like” theory, solid-sphere force validation/steering, airborne manipulation and beat-driven trajectories | Inputs must be sourced/frozen before numeric exclusion; novelty and feasibility remain unclaimed; PW-09 is an unreviewed preprint, PW-10's force agreement is setup- and friction-dependent, PW-11/PW-13 are represented by limited publisher previews, and PW-20 by an embargoed thesis abstract | No body, target, duration, workspace or actuator set selected; literature search non-exhaustive | Met for research design |
| Matched physical water measurement acceptance | SRC-W03/ALT-W01 records; UNK-001, UNK-002, UNK-008 | No formal matched acceptance result | Requires raw/traceable measurement, uncertainty/correlation, and predeclared comparison rule | Required inputs unavailable in this checkout | INDETERMINATE |

## Separate statuses

- **Software CI/verification:** this is a documentation/research task; no software behavior changed. Document link, required-file and whitespace checks are run at handoff. No new CI result is claimed.
- **MCLF:** no new physical or model verdict; future target analysis requires a declared MCLF case.
- **Numerical convergence:** not applicable; no numerical field backend or new simulation run was used.
- **Experimental validation:** NOT ESTABLISHED. No AURA experiment was executed.
- **Reproduction:** primary literature was checked against publisher/repository records, but the selected water raw measurement package remains inaccessible/incomplete here.
- **D03 requirements:** P1 documentary deliverables do not satisfy downstream solver, force, dynamics, control or experimental requirements.
- **D09 claims:** no new success, novelty, pseudogravity or feasibility claim is promoted.

## Decision

**Task decision: DONE. P1 phase decision: INDETERMINATE / HOLD for formal measurement acceptance.** The research-design work has bounded artifacts and explicit follow-up paths. Formal water evidence is not sufficient for P1 PASS, and no owner decision is recorded here. Allowed next work is independent READY research such as SC-01 under DEC-004 and continued evidence retrieval. Do not infer P1 PASS, close the separate ANA-07/P3 owner decision, or start downstream force/dynamics implementation from this review.

## Record preservation

Open and contradictory evidence remains in UNK-002, UNK-008, UNK-015 and the water/effect records. This review does not alter or replace prior measurements, failed cases, or source limitations. Reopen the review if primary data or a matched measurement protocol becomes available.
