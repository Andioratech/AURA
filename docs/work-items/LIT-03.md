# LIT-03 — Review Small-Particle Force Equations and Domain

**State:** DONE — bounded literature model comparison; implementation contract remains pending · **Opened/completed:** 2026-10-03 · **Responsible role:** research implementer · **Phase:** P1

## Identity and authority

- **Authority:** D00 v1.3, PLAN-01 v1.3, D01-D09, DEC-001 through DEC-004, and LIT-03 in [P01](../planning/phases/P01-evidence.md).
- **Predecessors:** LIT-02 [water reference selection](../benchmarks/water-reference-selection.md).
- **Question:** Which published small-sphere radiation-force equations and regimes are candidate formulations for the SRC-W03 exploratory MQ1 domain, and what prevents an implementation choice from being frozen?
- **Outputs:** [Model-selection and applicability review](../research/particle-model-selection.md); EQ-013–015 in the [equation register](../registers/equations.md); unknowns and continuity updates.

## Bounded work contract

Reviewed Settnes & Bruus (2012), Karlsen & Bruus (2015), and the SRC-W03 measurement description using primary full text and exact equation/section/table locators. Compared ideal-fluid, viscous and thermoviscous sphere formulations. Calculated `λ`, `ka`, `δs/a`, and an explicitly cross-source thermal-layer screen in SI from cited values. Defined amplitude/perturbation and wall-clearance checks symbolically where matched inputs are unavailable. No code, executable force model, physical run, tolerance, hardware choice or validation claim is within this task.

## Checks and outcome

- For SRC-W03 MQ1, source inputs give `λ ≈ 771.65 µm`, `ka ≈ 0.00240–0.04136` over the listed measured size means, and `δs/a ≈ 1.29–0.075`; the viscous boundary layer is comparable to the smallest particle radius. Therefore a small-`ka` assumption does not justify an inviscid-only force model.
- A thermal-layer screening value `δt ≈ 0.155 µm` was derived from Karlsen & Bruus Table II values at 300 K. It is deliberately not treated as an exact SRC-W03 25 °C input; matched particle/fluid thermal properties remain open.
- SRC-W01 Settnes–Bruus is retained as a viscous comparator with arbitrary `δs/a` within its small-particle/long-wavelength derivation. SRC-W02 Karlsen–Bruus is the preferred candidate formulation for a future isolated radiation-force implementation because it includes viscous and thermal particle scattering with no fixed ordering between particle and boundary-layer lengths. The inviscid theory is retained only as an ideal limit.
- The result does not cover external channel streaming, finite channel boundaries, calibration dependence, or the measured velocity as a direct force. No single executable force model is frozen until material properties, matched field calibration and separate streaming/wall effects are reviewed.
- Independent checks are planned but not run: limits and symmetry, dimensional consistency, and direct surrounding-surface momentum flux under a frozen domain. No tolerance or test ID was invented.

**Outcome:** LIT-03 is DONE as a source-grounded model/applicability review. It does not authorize implementation; P1 remains open. LIT-04 is READY to quantify competing streaming, wall, thermal and other terms and refine the calibration/holdout plan. No failed result was removed, and no physical parameter was silently changed. ANA-07's P3 phase decision remains separately pending.
