# LIT-02 — Select a Water Measurement Reference or Bounded Fallback

**State:** DONE — bounded literature task; formal measurement benchmark INDETERMINATE · **Opened/completed:** 2026-10-03 · **Responsible role:** research implementer · **Phase:** P1

## Identity and authority

- **Authority:** D00 v1.3, PLAN-01 v1.3, D01-D09, DEC-001 through DEC-004, and LIT-02 in [P01](../planning/phases/P01-evidence.md).
- **Predecessors:** LIT-01 [evidence inventory](../research/evidence-inventory.md) and [unknowns register](../registers/unknowns.md).
- **Question:** Which primary water-particle measurement provides the most informative reproducible reference in the approved starting campaign, and what prevents formal acceptance?
- **Output:** [Reference-selection record and benchmark design](../benchmarks/water-reference-selection.md); updated evidence inventory, unknowns, phase card, board and handoff.

## Bounded work contract

Compared SRC-W03 (Barnkob et al., 2012) with ALT-W01 (Muller et al., 2013), using primary papers and author manuscripts. Compared observable, particle/fluid, geometry, calibration dependence, uncertainty reporting, data availability and reproduction burden. Search stopped after the prescribed two cycles. No data were digitized, acquired, or inferred; no physical run, model implementation, force calculation, tolerance, hardware choice or experimental-validation claim was made.

## Checks and outcome

- Selected the 25 °C, pure Milli-Q water, 1.940 MHz MQ1 measurement series in SRC-W03 as the preferred **exploratory** reference: it provides size-resolved spatial particle-velocity fields and the source reports 22 discrete measurement fields across its series.
- Retained ALT-W01 as the 3D alternative. Its public author manuscript reports bin means/SEM and an approximately 20% higher measured mean velocity than prediction, outside the stated combined 1σ uncertainty; this discrepancy is preserved and is not converted into an acceptance tolerance.
- Recorded calibration distinction between SRC-W03 Table IV(a) all-point fit and Table IV(b) endpoint method. Recorded ALT-W01 calibration dependence on five centerline trajectories for the 5.33 µm case and voltage scaling for the 0.537 µm condition.
- Confirmed the SRC-W03 supplement containing raw velocity fields, particle sizing and acquisition metadata is subscription-gated in the reviewed APS record; raw arrays were not found in the accessible ALT-W01 manuscript. Therefore formal measurement selection and acceptance remain INDETERMINATE.
- Added `SYN-WATER-01`, an exact manufactured data-ingestion fixture. It is not a water observation, model verification, experiment, or RUN-ID; it cannot validate physics.
- No owner scope choice is required. The unresolved data access/calibration/uncertainty gaps remain explicit and assigned below.

**Outcome:** LIT-02 is DONE as the bounded documentary/search task. Formal water measurement acceptance is not PASS and P1 remains open. LIT-03 is READY; it must review equations and applicability with exact primary-source locators before any particle-force implementation. ANA-07's formal P3 owner decision remains separately pending. No failed result was removed and no scientific parameter was invented.
