# ANA-06 — Energy-Balance Artifact Review

**Date:** 2026-10-02 · **Decision:** ANA-06 DONE; ANA-07 READY · **Role:** implementation self-review

## Acceptance evidence

The [ANA-06 task](../work-items/ANA-06.md) freezes a bounded ENERGY-BALANCE-1.0 comparison for three incident plane-wave control volumes and one source-free exterior spherical shell. [`mclf/balances.py`](../../src/aura/mclf/balances.py) checks the exact six-point spherical sample layout, outward normals, equal area weights, shell topology, compatible frequencies, complete field association, finite explicit terms and contract-consistent result state. Unknown ledger values remain INDETERMINATE. The API is kept outside top-level MCLF imports to preserve the existing configuration-validation firewall.

Independent expectations use the pointwise Decimal B-03/B-04 identities, the B-05 independent coherent-field oracle, and a guarded Decimal B-06 radial power calculation. Required negative cases fail when velocity orientation or the explicit source term is corrupted. Missing one or both required terms cannot receive PASS. No force or overall MCLF acceptance status is emitted.

The [ANA-06 numerical report](../benchmarks/ANA-06-energy-balance-verification.md) records the complete four-case ledger. Full local Quality passed Ruff and **1,366 tests in 17.70 s**. [Exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37055310149) passed environment/lock verification, Ruff and **1,366 tests in 21.50 s** for implementation `260464a9e7975b4380cc223546a5b26304e6d303`. Clean published-source verification of the three focused suites passed **143 tests in 1.74 s**. Source and ENV-1.0 records match before and after; retained file hashes were independently rechecked and the ignored bundle fits the 16 MiB cap.

Development failures remain in the ignored verification bundle and task record. The first full suite exposed the eager import firewall regression; it was fixed and the entire suite passed before committing. The initial frequency-regression fixture failed the topology guard before reaching its intended frequency check; it was corrected. A temporary environment missing three pinned packaging tools and an initial report-copy directory mistake were recorded and corrected. No equation, input, source case or tolerance was modified to produce the passing result.

## Scientific boundary and handoff

ANA-06 is complete for its frozen model-local energy-accounting scope. This review is an implementation self-review, not independent physical-model approval or experimental validation. A closed surface energy audit does not calculate momentum transfer, radiation force, body acceleration or gravity; the six-point rule is not valid by claim for arbitrary fields/surfaces. Source and absorption zeros are ideal-case assumptions, not apparatus measurements.

No real water, particle, larger mass/object, new geometry, physical transducer or microgravity claim is supported. P3 is **not closed**: the recorder/source/sampling/gradient/index/checker/provenance/post-audit campaign and its separate gate review belong to ANA-07. [The work board](../planning/10-work-board.md) moves ANA-07 to READY within the existing approved sequence.
