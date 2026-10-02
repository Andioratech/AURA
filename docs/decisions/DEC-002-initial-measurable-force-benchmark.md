# DEC-002: Initial Measurable Force Benchmark

**Status:** APPROVED FOR P1 DESIGN · **Date:** 2026-10-02 · **Owner:** AURA project owner

## Decision

The owner approved the published 50 mm expanded-polystyrene sphere force measurement in air by Andrade, Bernassau, and Adamowski (2016) as AURA's first measurable force-model check. This approval is limited to the bounded starting case described below. It does not approve a solver implementation, a P1 PASS, or a claim that AURA's microgravity objective is feasible.

The initial comparison will concern the published axial acoustic radiation force on a 50 mm, 1.46 g sphere as the gap to one ultrasonic transducer changes. The study reports a 20 mm radiating face, 25,230 Hz frequency and 15 µm face-displacement amplitude; force was measured with an electronic scale. The paper separately demonstrates levitation of the sphere with three transducers, but the approved initial observable is the single-transducer force-versus-gap curve.

## Rationale and evidence

The case uses air and a centimeter-scale body, and its force observable was measured directly. That makes it a better first measured anchor for AURA's force model than the previously considered liquid/microparticle cases. The published numerical force curve is contextual evidence; validation must compare AURA with the experimental measurements, not merely reproduce the paper's finite-element result.

Primary source: M. A. B. Andrade, A. L. Bernassau, and J. C. Adamowski, “Acoustic levitation of a large solid sphere,” *Applied Physics Letters* 109, 044101 (2016), [DOI: 10.1063/1.4959862](https://doi.org/10.1063/1.4959862); author/institution [full-text record](https://researchportal.hw.ac.uk/en/publications/acoustic-levitation-of-a-large-solid-sphere/).

## Limits

- The sphere's diameter is 50 mm but its mass is only 1.46 g; it does not represent a dense or heavy body.
- The first observable tests one axial force component from one source over the reported gap range. It does not validate an array, force/torque control, a chosen acceleration vector, long-duration stability, or operation in microgravity.
- The experimental curve is published as a figure. The pointwise measurement uncertainty and digitization uncertainty must be checked before a quantitative acceptance rule can be frozen.
- No result from this case may be extrapolated to other materials, masses, body shapes, media, source configurations or acceleration targets without new justification and evidence.

## Required work before P1 PASS

1. Recover and independently review the measured Fig. 5 force points and gap convention.
2. Record all source-reported measurement uncertainty and added figure-digitization uncertainty.
3. Predeclare the curve-comparison, numerical-error and stop/indeterminate rules; do not invent a percentage tolerance.
4. Complete the experiment definition and resource preflight under P1.4–P1.7.
5. Obtain the P1 exit decision; solver implementation remains gated by the later P2–P5 phases.

## Benchmark evolution

The owner also directed that later project steps search for additional options suited to their advancing capability. The phased-array restoring-force work of Inoue et al. (2019), [DOI: 10.1121/1.5087130](https://doi.org/10.1121/1.5087130), is recorded as a candidate for a later array/stability gate, not as an approved follow-on benchmark. AURA must identify a new measured or independently validated case when the target body, acceleration objective, array behavior or microgravity claim changes.

The accepted plan update and preserved prior plan are [PLAN-01 v1.1](../PLAN-01-project-execution-plan.md) and [archived PLAN-01 v1.0](../archive/PLAN-01-v1.0-project-execution-plan.md).
