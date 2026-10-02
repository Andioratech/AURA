# AURA Scientific Research Project

<p align="center">
  <img src="assets/andiora-logo-no-slogan.svg" alt="Andiora Research" width="420">
</p>

**Adaptive Ultrasonic Regulated Acceleration (AURA)** is a proposed computational research program to study whether controlled acoustic radiation forces can produce a prescribed acceleration for selected free bodies within a defined operating domain.

> AURA studies mechanically induced **acoustic pseudogravity**. It does not create a gravitational field, reproduce universal gravitational coupling, or alter spacetime.

The work is explicitly falsifiable. A scientifically useful outcome may be a supported operating region, a quantified limit, or evidence that a stated hypothesis fails within its tested domain. Feasibility is not assumed.

## Research question

Can an actively controlled ultrasonic field, together with state estimation and closed-loop control, maintain a declared acceleration target for specified bodies in a bounded environment, while satisfying independently checked physical constraints and numerical validation criteria?

Answers must be scoped to the tested objects, materials, geometry, medium, frequency range, field regime, solver fidelity, uncertainty, and time interval. Results for small particles do not establish performance for macroscopic or human bodies.

Small particles in water are the first implementation campaign. The research objective explicitly includes greater masses, larger objects and other geometries through a [staged scale progression plan](docs/planning/11-scale-progression.md). Each new domain requires an appropriate physical model and independent evidence before its performance can be claimed.

## Scientific approach

1. **Define the model and domain.** State the governing equations, approximations, boundary conditions, units, assumptions, and intended observables.
2. **Check physical plausibility independently.** The Mathematical Bounds and Limits Framework (MCLF) evaluates dimensions, invariants, model validity, conditional bounds, and evidence sufficiency without reusing the simulator blindly.
3. **Verify numerical implementations.** Compare with analytical and published benchmarks, perform observable-based convergence studies, and use an independent method for claim-critical results.
4. **Run reproducible experiments.** Version experiment definitions; identify each run by its exact inputs, code revision, environment, seeds, outputs, and checksums.
5. **Limit claims to evidence.** Separate software verification, model validation, simulation results, and physical measurements. Do not infer hardware or human-scale feasibility from a simulation outside its validated domain.

## Project maturity

This repository contains an owner-approved English development baseline (D00-D09 and PLAN-01) and a software scaffold. The supporting procedures G01-G05 remain DRAFT. It does not yet contain a validated acoustic solver, an experimentally demonstrated system, or evidence that AURA achieves its research objective. Baseline approval controls the research process; it does not establish physical feasibility or validate a model.

## Repository structure

| Path | Purpose |
|---|---|
| docs/ | Controlled scientific, numerical, and software specifications (D00-D09) |
| guides/ | Procedures for contribution, experiments, anomaly handling, reproduction, and review (G01-G05) |
| src/aura/ | Python package scaffold; research solvers are not yet implemented |
| tests/ | Starting point for software and scientific verification cases |
| examples/ | Versioned experiment configurations |
| data/ | Data provenance and retention policy |
| results/ | Run output policy; generated results are excluded from Git |
| references/source_documents/ | Unmodified source PDFs and checksums |
| assets/ | README and project identity assets |

## Start here

- [D00: Document control and scientific baseline](docs/D00-document-control.md)
- [D01: System architecture](docs/D01-system-architecture.md)
- [D02: Mathematical Bounds and Limits Framework](docs/D02-mclf.md)
- [PLAN-01: Phase-gated master work plan](docs/PLAN-01-project-execution-plan.md)
- [Detailed simulator and falsification plan](docs/planning/README.md)
- [DEC-001: P0 baseline approval](docs/decisions/DEC-001-p0-baseline-approval.md)
- [P1.1: Published benchmark candidate dossier](docs/benchmarks/P1.1-benchmark-candidates.md)
- [G01: Contributor workflow](guides/G01-contributor-workflow.md)

The full document register and precedence rules are maintained in D00. Physical-law and SI definitions take precedence over project specifications; conflicts must be investigated and versioned rather than resolved silently.

## Reproducibility and evidence

Every scientific run is expected to record its experiment and run IDs, source revision, configuration and data hashes, solver and validity regime, numerical precision, random seeds, environment, resource estimates, outputs, metrics, convergence results, and MCLF verdict. An INVALIDATED run cannot be promoted as evidence. An ALERT or INDETERMINATE result requires explicit limitations and follow-up.

Large datasets and generated outputs should not be committed to Git by default. See D07 for run manifests and evidence bundles, and D05 for compute and storage policy.

## Language, references, and reuse

Maintained project documentation is in English. Original Spanish source PDFs are preserved, unchanged, under references/source_documents; the English specifications consolidate and review their technical content. Scientific references and claims must be traceable to primary literature and used only within their documented assumptions.

No project license or publication citation has been approved. Until one is selected, do not assume permission for reuse outside this repository.
