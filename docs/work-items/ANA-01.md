# ANA-01 — Analytical Field Contract and Reference Matrix

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Owner role:** research implementer

## Authority and question

Starting revision: `8b29b50d172491c0f645157bebd94d007fcd6bda`. P2 is PASS and RUN-01 is DONE within its diagnostic scope. Authority: D00, D02, D04–D09, CONV-1.0 and DEC-003/004. This is P3's output/reference design card, not an acoustic execution or a phase gate.

Can the next implementer evaluate B-03…B-06 without guessing signs, source amplitude, sample order, vector components, derivatives or acceptance scales?

## Frozen implementation protocol

- Freeze [FIELD-1.0](../research/analytical-field-contract.md), [B-03…B-06](../benchmarks/B03-B06-analytical-protocols.md) and the equation-to-case mapping before implementing a solver.
- Implement only `src/aura/fields/types.py`, its package export and representation tests. Require finite chamber coordinates, positive frequency, peak pressure, full fluid-velocity vector and pressure gradient. Snapshot caller arrays; retain sample order and repeated positions; reject missing, ragged, oversized or nonfinite data.
- Use binary64/complex128 and explicitly labeled SI artifacts with separate real/imaginary components. Preserve schema 1.0 and RUN-1.0. Document the required companion gradient record and future driver admission rather than making the diagnostic recorder execute physics.
- Limit the representation to 256 samples. No new dependency, solver, field evaluation, force, body motion, controller or experimental comparison is implemented in this task.
- Inspect primary bulk-fluid and wave references, reconcile their time convention and record exact locators. Stop source search when the selected pressure/velocity/gradient expressions and assumptions have independent derivations; unresolved hardware and measurement inputs stay in LIT/FOR/SC.
- The benchmark medium is manufactured, homogeneous and lossless, with water-like density/sound speed. There is no body or wall coupling, no gravity response and no transient startup. Observations are harmonic phasors and one-period mean flux. No experimental uncertainty is inferred from these values.
- Representation acceptance is exact structure/round-trip equality with typed rejection of invalid data. The separate future numerical error budget and finite sample matrix are frozen in the benchmark protocol; passing representation tests is not B-03…B-06 PASS.
- Verify hand tables by independent real trigonometric identities and differentiate their expressions on paper. Do not produce reference outputs by calling the future implementation.
- Run focused tests, then complete current local CI before each commit and exact remote CI after each push. Contract checks should finish within 10 s, complete suite within 60 s; investigate excess rather than silently widening caps. Use one CPU process, no GPU, no generated scientific output in Git.

## Planned review and delivery

Deliver the types, protocols, source/equation register and tests in one focused implementation commit. Then record actual checks, any development failures, reviewed limits and the next task in a separate closure commit. Source and environment are the committed checkout and ENV-1.0 development lock; no run IDs are issued because no scientific run occurs. No independent scientific approval is claimed by the implementer's artifact review.

ANA-02 becomes READY only after this artifact review. P3, physical model coverage and AURA feasibility remain unresolved.

## Development findings retained before publication

The first focused representation suite passed 114 tests. Lint identified a closure over a loop variable in the serializer; explicitly binding that value resolved the finding. During additional boundary-test insertion, a test block was temporarily placed in the wrong function: lint reported an undefined test variable and the focused run recorded 121 passes / 1 failure (NameError). The block was restored to its owning test; no implementation behavior, expected field value or acceptance tolerance was relaxed to address it.

The final focused suite contains 122 representation cases, including maximum sample count, extreme finite encodings, detached snapshots, invalid metadata/numbers/shapes, required complex pairs and refusal to interpret component records as schema-1.0 documents. Scientific case comparisons remain NOT_RUN. Full workflow and publication evidence are recorded in the subsequent artifact review.

## Outcome and handoff

Revision `c22f4859703611d5ed6c300acb8ce89a3a8cb411` delivered the named artifacts and passed the complete local workflow (1,033 tests, 19.84 s) and [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37037149159) (1,033 tests, 16.92 s). [The artifact review](../reviews/ANA-01-field-contract.md) closes this representation/reference specification card. No scientific run IDs exist for this task, and no B-03…B-06 solver comparison has passed yet.

ANA-01 is DONE and ANA-02 is READY. P3, model coverage, experimental comparison and scale-up evidence remain open. The next implementation is the single progressive plane wave with independently checked pressure, full fluid velocity and pressure gradient; no new owner decision is needed. Closure documentation receives its own complete local and exact remote CI checks before delivery.
