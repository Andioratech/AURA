# LIT-04 — Identify Competing Fluid, Wall, Thermal and Stochastic Effects

**State:** DONE — bounded effect ledger and calibration design; coupled budget remains open · **Opened/completed:** 2026-10-03 · **Responsible role:** research implementer · **Phase:** P1

## Identity and authority

- **Authority:** D00 v1.3, PLAN-01 v1.3, D01-D09, DEC-001 through DEC-004, and LIT-04 in [P01](../planning/phases/P01-evidence.md).
- **Predecessors:** LIT-03 [model-selection review](../research/particle-model-selection.md); LIT-02 [reference selection](../benchmarks/water-reference-selection.md).
- **Question:** Which force, fluid, boundary, thermal, stochastic and inertial effects can alter the SRC-W03 MQ1 particle-velocity observable, and how does calibration constrain a fair comparison?
- **Outputs:** [Effect ledger and calibration-dependence diagram](../research/fluid-and-omitted-effects.md); updates to the [unknowns register](../registers/unknowns.md).

## Bounded work contract

Used source-reported MQ1 geometry, particle/fluid properties, equations, wall factors, particle statistics and measurement method. Derived explicitly conditional scales for gravity settling, Brownian diffusion and the stated particle-inertia timescale. Recorded unavailable raw/cycle/calibration data as gaps. No simulated trajectories, run, physical input repair, acceptance tolerance, executable model or experiment design was produced.

## Checks and outcome

- The primary observable is particle velocity with both radiation-force response and streaming advection; it cannot be interpreted as force without separate fluid flow and drag accounting.
- Wall drag factors, thermoviscous streaming estimates and optical sampling depth are source-reported, position-dependent effects, not generic constants.
- Calculated Stokes settling and Brownian scales from the explicit 25 °C MQ1 values, with assumptions and time dependence recorded. No unsupported comparison to inaccessible measured point values was made.
- Preserved a discrepancy: the SRC-W03 text states `rho_p a^2 / eta < 1 µs`; recomputation at its largest listed radius using its own material values gives approximately 30 µs. This remains small relative to the source's stated millisecond motion scale but exceeds the 1.94 MHz oscillation period. The validity of the periodic/terminal reduction for that endpoint remains unresolved.
- Documented calibration reuse in all-point fits versus endpoint fits, the Table V intermediate-size difference (0.294 versus the simple 0.25 size-squared prediction; no table uncertainty), and a requirement for independent fluid-flow data plus held-out fields/sizes before a later measurement comparison.
- No raw supplement was accessed, no missing term was treated as zero, and no tolerance was introduced.

## Post-task interpretation note

A subsequent audit of the timescale comparison preserves the arithmetic discrepancy but narrows its implication. SRC-W03 Eq. (11) is an algebraic cycle-averaged particle-drift relation, so `ρp a²/η > 1/f` alone does not show that its mean-motion approximation fails. For a separate isolated-sphere Newton-plus-Stokes transient, the derived relaxation time is `2ρp a²/(9η)`, approximately 6.77 µs at the listed mean radius of the largest particle, or 0.68% of a 1 ms interval. This does not quantify wall/unsteady-fluid errors or reconcile the paper's `<1 µs` arithmetic; UNK-015 remains open. The detailed derivation and assumptions are in the [effect ledger follow-up](../research/fluid-and-omitted-effects.md#follow-up-interpretation-of-the-particle-inertia-scale).

**Outcome:** LIT-04 is DONE as a bounded literature and scale ledger. Coupled term magnitudes and formal water validation remain open. LIT-05 is READY to prepare necessary-limit and prior-work investigations and the remaining P1 dossier. ANA-07's formal P3 owner decision remains separately pending.
