# ANA-02 — Plane-Wave Artifact Review

**Date:** 2026-10-02 · **Decision:** ANA-02 DONE; ANA-03 READY · **Role:** implementation self-review

## Delivered scope and acceptance

The [task record](../work-items/ANA-02.md) implements the P3 card's single-wave evaluator, explicit rotation/direction handling, independent B-03 fixtures/tests and maximum/RMS error report. The derivation, medium restriction, amplitude/time convention, numeric admission, resource estimate and limitations are explicit in [PLANE-WAVE-1.0](../research/plane-wave-kernel.md). Pressure, fluid velocity and pressure gradient return the existing FIELD-1.0 container; mean flux uses both phasors.

At revision `540488c9de6d37984d36b82d7f2a195f07d82b74`, 130 focused checks passed from clean source. The [numerical report](../benchmarks/B03-plane-wave-verification.md) records the actual 11-case/59-point comparisons, raw report identities and resource measurements. Maximum normalized error across the four observables was 7.102587e-16, below the unchanged 4.547474e-13 budget; the independent backend and high-precision reference checks also passed. Known-wrong answers and invalid inputs were rejected. No functional test failure or tolerance adjustment occurred.

The complete local workflow passed 1,163 tests in 15.27 s; [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37041107704) passed 1,163 tests in 24.66 s. No new dependency or lock change was introduced. CLI status/README now distinguish the available Python kernel from diagnostic-only recorded runs. Author and committer use the owner's configured identity; private local instructions and generated reports stay outside Git.

## Acceptance boundary and handoff

This closes the bounded implementation/numerical verification card, not independent physical review, P3 PASS or a D09 supported scientific claim. The ideal formula is verified on manufactured input; actual water, finite transducers, boundaries, viscosity, heating, body force/motion and microgravity remain unvalidated. DEC-004's larger-mass/object objective is unchanged.

`aura run` does not execute this kernel yet. No physical driver was admitted in this card, and no JUnit report is presented as a RunManifest. Before ANA-07's evidence campaign, its adapter must satisfy every FIELD-1.0 input/index/result/checker/provenance and status requirement. A future maintainer must not add a model name to RUN-1.0's whitelist without that work. Recorded campaign/resource audits and replay stay open in the board's existing P3/RUN dependencies.

**Next:** ANA-03 constructs the equal counterpropagating pair, checks pressure nodes and fluid-velocity antinodes, and tests zero mean flux plus the prescribed phase-shifted/unequal-amplitude variants. Reuse the verified single-wave kernel and independent B-04 real identities; preserve every input amplitude when summing. P3's later tasks and physical validation remain separate gates.

Closure documentation is delivered in a second commit after another complete local workflow and exact remote CI confirmation. This artifact review needs no new owner decision within the approved scope.
