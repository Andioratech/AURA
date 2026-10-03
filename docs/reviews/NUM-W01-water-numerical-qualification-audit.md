# NUM-W01 — Water Numerical-Workflow Qualification Audit

**Date:** 2026-10-03 · **Decision:** DONE; bounded software qualification PASS · **Role:** evidence reconciliation, not independent physical review

## Question

Do the committed water-related calculations and comparison artifacts demonstrate that AURA's existing numerical workflow can generate repeatable analytical field values and compare them with independently computed references, at a scope sufficient to proceed to the air P4 field case?

## Evidence reviewed

| Artifact | Finding | Scope limit |
|---|---|---|
| [P3 ANA-07 matrix](../benchmarks/ANA-07-recorded-field-matrix.md), [gate review](P3-ANA-07-gate-review.md) | 32 frozen ideal-field configurations and 264 sample comparisons pass ANA-REF-1.0; fresh B03/B06 reproductions retain exact fields and metrics | Homogeneous ideal analytical fields; no body, finite radiator, measured water field or numerical PDE solver |
| [ANA-06 report](../benchmarks/ANA-06-energy-balance-verification.md) and [review](ANA-06-energy-balance.md) | Four energy-ledger cases pass; their declared medium values are `rho=1000 kg/m³`, `c=1500 m/s`, `f=1 MHz`, with independent analytic/Decimal expectations | Manufactured water-like parameters in an ideal lossless fluid; not measured water-state values, scattering, force or a coupled water model |
| [RUN-02 replay](RUN-02-replay-report.md) | A recorded B03 analytical case reproduces all four field arrays byte-for-byte and its ANA-07 metrics exactly from the bound source/environment | Replay demonstrates software reproducibility, not a new physical-domain validation |
| [SRC-W03 extraction](FIG-W03-MQ1-profile-extraction.md) and [water-reference dossier](../benchmarks/water-reference-selection.md) | Six plotted 1D profiles are reproducibly digitized; independent parsers and raster checks agree on plotted marker locations | Source numerical arrays and complete measurement/calibration uncertainty remain unavailable; no AURA solver comparison was run |
| [SYN-WATER-01](../benchmarks/water-reference-selection.md#separate-synthetic-verification-case) | Exact manufactured data-path fixture is defined | It is not a physical water case or field-solver reference; no executable run was made for that documentary task |

## Finding

**Numerical-workflow qualification: PASS, narrowly scoped.** The project has reproducible analytical field calculations, independent frozen numerical references, exact replay, and ideal energy-ledger comparisons using water-like density and sound-speed inputs. This supports the owner's intended claim that the software can produce and compare repeatable numbers in a water-like ideal parameter setting.

**Water-specific field-solver verification: NOT ESTABLISHED.** No numerical field solver, water-specific discretized case, or comparison against SRC-W03 raw measurements is documented. The result above must not be described as validating a water propagation/scattering model or the physical water experiment.

**Physical water measurement validation: INDETERMINATE.** SRC-W03's selected particle-velocity observable combines acoustic radiation-force response and streaming. The reviewed raw arrays and complete uncertainty/covariance/calibration budget are unavailable. Figure digitization does not close that gap.

Under DEC-006, this audit satisfies the first water numerical-workflow qualification for the demonstrated software scope. NUM-W02 is not activated. Proceed to the air field method comparison and its solver explanation/preflight. Retain each air acceptance criterion separately; a water-like calculation cannot pass an air criterion.

## Re-entry conditions

Open a new water-specific numerical task if AURA later needs to claim a discretized water field solution, a water scattering calculation, or matched water measurement/model agreement. Require an independently traceable reference and a predeclared observable, comparison rule, uncertainty treatment, resource bound and run identity. Do not reuse this audit as evidence for those claims.
