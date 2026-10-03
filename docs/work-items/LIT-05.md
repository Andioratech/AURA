# LIT-05 — Necessary Limits and Prior Work

**Status:** DONE as bounded research/design work · **Date:** 2026-10-03 · **Responsible role:** research implementer · **Baseline:** D00 v1.3 / PLAN-01 v1.3 · **Code revision:** `9ee66f7b1fb79eff807c078c102aae17bab09db6`

## Question and scope

Prepare necessary-condition analyses and compare primary prior work without choosing an acceleration target, body, hardware or actuator envelope. This work does not implement a solver, force or motion model and makes no physical feasibility or novelty claim.

## Method and outputs

- Prepared [L-01…L-05 symbolic limit design](../research/limits-design.md) from PLAN-01 and D02. It states the required immutable target inputs, kinematic workspace check, complete load-balance requirement, witness-versus-exclusion distinction, conditional momentum estimate and applicability indicators.
- Reviewed source-backed actuation information only where a declared experiment supplied it. Since AURA has no selected target or admissible actuator set, no numerical pressure/power feasibility screen was possible. Hypothetical budgets remain separate from hardware specifications.
- Compared eighteen primary-work records in the [prior-work register](../registers/prior-work.md), including measured forces across shapes, phased-array manipulation, reduced-gravity and microgravity work, feedback/feedforward trajectory control, experimentally tested cosine-acceleration motion, material-dependent sphere-force calculations and phased-array particle transport.
- Performed two scoped search cycles and focused follow-ups for acoustic trajectory control, acoustic-gravitation terminology, solid-body force-model/steering prior art, beat-driven dynamics, prescribed-trajectory manipulation, material-dependent sphere forces and phased-array particle transport. Search boundaries and follow-up requirements are recorded; the search is not exhaustive and does not establish novelty.
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

**Solid-body force and steering follow-up (2026-10-03):** Ghanem et al. (PW-10) validate an arbitrary-beam scattering model against plate-supported lateral-force measurements on millimeter-scale solid spheres in water and demonstrate 2D steering on that plate. The full text reports overall angle discrepancy `21.8±32.4%` and inferred-force discrepancy `32.8±58.1%`; the more favorable force discrepancy `11.7±8.3%` applies only when friction-to-acoustic-force ratio is at most 0.6. Thus the abstract's average 22% angle agreement must not be quoted as a 22% force error. This work further rules out novelty claims for solid-sphere force modeling, forces comparable to weight, or 2D steering alone. Its surface-supported setup does not establish free 3D acceleration or gravity equivalence, and it does not resolve AURA's target-specific novelty.

**Free-body and larger-geometry follow-up (2026-10-03):** Recent primary publications include real-time midair manipulation of a super-wavelength object with paired vortex beams (PW-11) and feedforward levitation of a 98 mm, 0.608 g hemispherical shell in a bounded workspace using a large 1,494-element array (PW-12). These narrow novelty claims for free airborne manipulation, large geometric extent and shaped-body levitation. They do not demonstrate target acceleration histories, high-mass control or gravity equivalence; the second case especially shows that large dimensions do not imply large mass. PW-11's publisher preview limits the experiment detail available in this review. Exact-target novelty remains unresolved and the literature search is not exhaustive.

**Oscillatory-motion follow-up (2026-10-03):** Hou et al. (PW-13) report vertical vibration of levitated spheres at the beat frequency of slightly detuned opposing sound waves and compare position dynamics with calculated radiation force. This further narrows any novelty claim about acoustically induced time-varying motion, while leaving acceleration-target tracking, multi-axis trajectory acceptance and gravity-like response unestablished. Full protocol details are not exposed in the publisher preview available here; exact-target novelty remains unresolved.

**Beat-driven trajectory follow-up (2026-10-03):** Abdelaziz and Grier (PW-14) experimentally measured a 2 mm bead's one-axis trajectory in a standing-wave trap driven by a detuned transverse traveling wave, and compared phase-space trajectories qualitatively with an idealized model. Their Appendix A states the effect depends on gravity displacing the bead and predicts it would not occur in microgravity; this is a mechanism-specific prediction, not a microgravity test. Dynamic acoustic trajectory manipulation is therefore established in a different domain, while an acceleration-targeted microgravity result remains open.

**Prescribed-trajectory follow-up (2026-10-03):** Andrade et al. (PW-15) experimentally tested horizontal manipulation strategies including a cosine acceleration profile on a 2 mm glass sphere in air and presented MPC-derived model-based feedforward for path following. Zehnter et al. (PW-16) demonstrated real-time array actuation and model-based open-loop feedforward along several paths for levitated spheres, including the Mie regime. These results rule out generic claims to prescribed-motion generation or trajectory following as AURA novelty. Their experiments do not report a predeclared acceleration-error acceptance or gravity-equivalence test; PW-16 explicitly reports execution without camera feedback. AURA's exact target/domain comparison remains unresolved.

**Material-response follow-up (2026-10-03):** Wang et al. (PW-17) calculate how the sign and resonant magnitude of standing-wave radiation force on elastic core-shell spheres in water vary with shell density, acoustic properties and hollow ratio for `0 < ka < 0.7`. This is theoretical/numerical, regime-specific evidence supporting the need to freeze body properties before interpreting acceleration; it does not establish a universal response across objects or make an experimental AURA claim.

**Phased-array particle-transport follow-up (2026-10-03):** Dai et al. (PW-18) report an 8×8 ultrasonic array and experimental steering of particles into designated microchannels; their publisher abstract also identifies FEM pressure analysis and Schlieren focal-position checks. Full text was unavailable for this review, so no particle/medium parameters, tracking accuracy or feedback status are inferred. The work is a transport/trajectory precedent, not acceleration acceptance or gravity-equivalence evidence.

Open target inputs remain in UNK-004…UNK-013, especially body and material, gravity environment, target/time/workspace/observation and actuator constraints. UNK-002/UNK-008 preserve measurement and uncertainty gaps; UNK-015 preserves the particle-inertia discrepancy. SC-01 and SC-02 are complete under DEC-004. The owner recorded bounded P3 PASS on 2026-10-03; numerical field work is now gated by the unresolved NUM-01 P4 benchmark/domain choice, and formal measurement acceptance remains INDETERMINATE. Any transition to P4 or core simulation work must follow the work-board dependencies and the already-delivered explanation checkpoint.
