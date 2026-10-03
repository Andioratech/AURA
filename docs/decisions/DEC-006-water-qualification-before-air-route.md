# DEC-006: Water Qualification Before the Air Development Route

**Status:** RECORDED OWNER DECISION · **Date:** 2026-10-03 · **Supersedes:** DEC-005 only for phase ordering after the water qualification gate

## Context

The owner directed that AURA first use its water work to establish that the numerical workflow can produce reproducible values and compare them with reference data, then perform an equivalent numerical comparison in air. If the air numerical gate passes, the initial force, dynamics, control and robustness development should continue in air. Water and air are sequential qualification domains in one program, not independent projects.

Repository evidence limits how the first clause can be recorded. P2/P3 and RUN-02 provide bounded analytical-software and replay verification. The SRC-W03 work provides reproducible extraction of figure-derived water-particle velocity profiles, but not a field-solver comparison against raw measured arrays. The water measurement comparison remains formally INDETERMINATE. These artifacts do not establish that a water-specific numerical solver benchmark has already passed. The next water task must reconcile the owner's reported prior comparison with immutable run/reference artifacts and label its exact scope before that result is used as a gate.

## Decision

1. Treat the water domain as the first numerical-workflow qualification. Audit existing water calculations, reference inputs, run identities, comparison metrics and checksums. Accept prior work only for the scope directly supported by those artifacts; otherwise complete the smallest reproducible water numerical comparison that can be independently checked.
2. After the water qualification is recorded, repeat the applicable numerical-verification process for the air case. Keep P4 air tied to the DEC-002 50 mm EPS sphere and circular piston model selected in DEC-005/NUM-01, subject to preflight and independent checks.
3. A PASS of the air numerical field gate authorizes the initial downstream development path (P5 onward) to remain in air. It does not itself validate force, acceleration, an experiment, pseudogravity or gravity equivalence. The air force comparison may remain INDETERMINATE while published uncertainty is incomplete; preserve that status and continue only within the approved evidence limits.
4. Water evidence does not validate air, and air evidence does not validate water. Preserve water as the starting qualification and research campaign, and retain DEC-004's broader investigation of greater masses, larger bodies and other geometries.
5. If the water evidence cannot be reconciled, record the gap and run a bounded water qualification if needed. If the air numerical gate fails or is INDETERMINATE, hold air-dependent advancement and preserve the result; do not substitute a favorable water outcome for the air gate.

## Evidence and limits

The current repository records the following distinct evidence:

| Evidence | Supported conclusion | Not established |
|---|---|---|
| ANA-07 / owner-recorded P3 PASS | Bounded ideal analytical field software comparisons and fresh reproduction passed their frozen criteria | Water-specific numerical field solver, measured-field validation, force or motion |
| RUN-02 | Exact source-bound replay of its recorded analytical fields and metrics | New physical-domain validation |
| FIG-W03-MQ1 extraction | Reproducible digitization of six plotted 1D water particle-velocity profiles | Original measured arrays, complete uncertainty, or AURA solver agreement |
| SRC-W03 measurement comparison | Exploratory reference is documented | Formal measurement acceptance, force or acceleration validation |

Any water qualification result must point to the exact experiment/run/reference artifacts, inputs, code revision, environment, checksums, observable, independent comparison and limitations. Numerical software verification and model/measurement validation remain separate verdicts under D00-D09.

## Consequences

- PLAN-01 and P4 add a water qualification checkpoint before the already selected air field method.
- P5 and later initial development cards use the air route only after an air P4 PASS; they do not inherit a water force law.
- P5 must select and independently check an air-domain force formulation. The Andrade curve's missing uncertainty continues to limit formal validation.
- No solver or simulation-core implementation is authorized by this record alone. The required plain-Spanish component/input/output/verification/limit explanation remains due before implementation begins.
- This decision changes sequencing and domain routing only. It does not revise equations, benchmark tolerances, scientific requirements or claim states.
