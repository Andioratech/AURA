# 09 — Requirements, Code and Evidence Traceability

This is the planned mapping for [D03](../D03-requirements.md). Replace planned references with actual paths/run IDs/review links as cards close. A row is not satisfied merely because a module name appears here.

| Requirement | Implementation and tasks | Planned verification evidence | Completion boundary |
|---|---|---|---|
| FR-001 versioned scenarios | Implemented `schema/models.py`, `schema/io.py`; FND-02; `cli.py` validation interface, FND-06 | [FND-05 B-02 structural report](../benchmarks/B01-B02-foundation-verification.md); schema/integration tests; [FND-06](../work-items/FND-06.md) installed JSON/YAML CLI checks | Verified for schema 1.0 supported geometries; no solver capability implied; canonical identity implemented in [FND-07](../work-items/FND-07.md) |
| FR-002 pre-allocation validation | Implemented `schema/quantities.py`, `mclf/rules.py`, evaluator and explicit gate; FND-03…FND-05 | [FND-05](../work-items/FND-05.md): 22 fault classes in both formats, exact diagnostics, no downstream hook calls | PARTIAL: test-only composition plus [RUN-01](../reviews/RUN-01-lifecycle.md) real diagnostic ordering verified; analytical integration and numerical resource preflight remain P3/NUM-02 |
| FR-003 fast field independent of FEM | Implemented `fields/types.py` and single/opposing-wave `fields/analytic.py`, [ANA-01](../work-items/ANA-01.md)/[ANA-02](../work-items/ANA-02.md)/[ANA-03](../work-items/ANA-03.md); `fields/numerical.py` planned | B-03/B-04 independent Decimal/hand comparisons and rejection checks; B-05…B-07 and recorded P3 evidence pending | PARTIAL: verified bounded single/opposing-wave kernels; noncollinear interference, recorded campaign and numerical backend remain open |
| FR-004 in-domain force/torque | `forces/*`, `mclf/regimes.py`; FOR-01…FOR-08 | B-08/B-09, regime rejection, torque reference when supported | Torque marked unsupported until justified; no automatic general completion from radial sphere force |
| FR-005 translation and rotation | `dynamics/integrate.py`, `rotation.py`; MOT-03…MOT-05 | B-11 and time refinement, force/torque ledger | Translation-only milestone does not close full requirement |
| FR-006 configured gravity | `dynamics/loads.py`; MOT-06 | B-12, consistent fluid/body Earth/zero/residual cases | No real microgravity claim from the zero setting alone |
| FR-007 acceleration target/error | `control/targets.py`, `analysis/metrics.py`; CTL-01, CTL-06 | B-14, hand time-series metric and realized acceleration | Explicit time window, sampling and constraints |
| FR-008 deterministic controller | `control/baseline.py`, allocation; CTL-03…CTL-07 | Open/closed loop, saturation, latency, held-out cases | Model/evidence gates remain applicable |
| FR-009 MCLF before/after | Implemented L0 `mclf/*` and diagnostic `runs/execute.py`; later scientific levels planned; FND-04, FOR-07, RUN-01, ADV-06 | [FND-04](../work-items/FND-04.md), [FND-05](../work-items/FND-05.md): pre/post verdicts, refusal to promote adverse/uncovered results, supplied success cannot establish acceptance | PARTIAL: L0 prechecks and RUN-01 lifecycle artifact postchecks verified for software diagnostics; physical result audits and higher levels remain open |
| FR-010 run identity | Existing RunManifest schema; implemented `schema/canonical.py`, `schema/identity.py`, `artifacts.py`, diagnostic `runs/manifest.py`, `runs/provenance.py`, `runs/check.py`; replay planned | [FND-07](../work-items/FND-07.md), [B-02 identity report](../benchmarks/B02-content-identity.md); [RUN-01 review](../reviews/RUN-01-lifecycle.md) verifies exception retention and actual identities; replay remains RUN-02 | PARTIAL: config/file integrity plus RUN-01 immutable storage and actual clean source/environment binding verified; dirty-source support, replay and scientific execution integration remain open |
| FR-011 compute estimate | RUN-01 fixed diagnostic preflight; planned `preflight.py` in NUM-02/NUM-06 | [RUN-01](../work-items/RUN-01.md) rejects insufficient RAM/disk/time before directory/driver allocation | PARTIAL: numerical workload estimates, calibration and hard workload timeouts remain pending |
| FR-012 compute/backend portability (SHOULD) | Implemented ENV-1.0 locks and `scripts/verify_environment.py`; later backend context in NUM-06/IND-03 | [FND-08](../work-items/FND-08.md): fresh core/dev installs, exact packages, local/remote CI and bad-hash rejection | PARTIAL: tested Linux x86_64 CPU development environment; no numerical backend portability/equivalence claim |
| FR-013 compare runs (SHOULD) | `analysis/compare.py`; FOR-05, IND-02 | Same observable/input mapping; mismatches rejected | Numeric comparison and limitation report available |
| FR-014 sweeps/Monte Carlo (SHOULD) | `analysis/sweeps.py`; ADV-02/ADV-03 | Fixed design/seeds, all-failure index, convergence of statistics where claimed | Monte Carlo distributions require evidence |
| FR-015 evidence bundle | `reporting/evidence.py`; RUN-02, IND-05 | Bundle hash check, fresh replay and review | Missing/raw evidence accessible with durable identity |

[FND-06](../work-items/FND-06.md) adds a user-facing interface for FR-001/002/009 foundation checks. `tests/test_cli.py` verifies the same 22 rejection classes, stable nonzero failures, missing-file handling, structured reports and unresolved model status. It preserves the partial FR-002/009 completion boundary above: no actual execution lifecycle or scientific coverage is supplied by a CLI wrapper.

[P2 gate review](../reviews/P2-foundation-exit.md) records foundation PASS. FND-08 adds actual installed-environment inspection and artifact locks as FR-010 prerequisites; RUN-01 now binds actual clean source/environment snapshots to durable software diagnostic records; analytical execution integration and replay remain ahead. This decision preserves every partial/unsupported boundary above and does not complete all D03 MUST requirements.

## D03 metric implementation register

| Metric | Owning task | Required definition before coding |
|---|---|---|
| `error_accel_rms` | CTL-01, CTL-06 | Vector norm, time quadrature, sample/filter/window, transient policy |
| `error_pos_rms` | MOT-08, CTL-06 | Target trajectory and frame; NOT_APPLICABLE when no position target exists |
| `force_residual` | MOT-02, MOT-08 | Complete chosen motion equation; retained fluid-inertia terms and independent comparison |
| `energy_balance_error` | ANA-06, FOR-07 | Control volume, stored/flux/loss/source terms and normalization |
| `momentum_balance_error` | FOR-07 | Surface/body/fluid/source/wall terms and numerical error budget |
| `grid_convergence_ratio` | NUM-04 | Refinement parameter, primary observable and non-asymptotic interpretation |
| `stability_margin` | CTL-04 | Controller/model-specific definition; not generic success percentage |
| `runtime_s`, `peak_ram_gb` | NUM-06 | Measurement tool, units, child-process accounting and platform |
| `peak_pressure_pa` | ANA-07, CTL-06 | Peak versus RMS, sample coverage and uncertainty from unsampled maxima |

Metrics that a model cannot supply are explicitly unavailable/NOT_APPLICABLE with justification; never fill them with zero. Required unavailable evidence blocks its gate.

## Release evidence checklist

- P2: FND-01…FND-08 and known-invalid fixture review.
- P3: ANA-01…ANA-07, RUN-01 and analytic reference reports.
- P4: NUM-01…NUM-07, RUN-02 and observed resource/convergence reports.
- P5: FOR-01…FOR-08 and scoped force-model/measurement comparison status.
- P6: MOT-01…MOT-08 and fluid/body dynamics review.
- P7: CTL-01…CTL-07 and frozen target tracking evaluation.
- P8: ADV-01…ADV-07, full failure catalogue and uncertainty map.
- P9: IND-01…IND-05, independent comparison/replay/review and bounded claims.
- P10: EXP-01…EXP-05, feasible measurement design and owner decision.

A prototype may ship documentation and code with explicit incomplete requirements. It cannot be described as the complete D03 research release while MUST rows remain unsatisfied without a reviewed baseline scope change.
