# AURA-D00: Document Control and Scientific Baseline

**Version:** 1.4 · **Status:** BASELINE · **Date:** 2026-10-03 · **Owner:** Andiora Research

## Purpose

This is the entry point and document precedence policy for AURA. It identifies the source of truth for each topic, defines document states and versioning, and records the review of the supplied baseline materials.

## Baseline document register

| ID | Document | Source of truth |
|---|---|---|
| D00 | Document control | Precedence, status, versioning, project readiness |
| D01 | System architecture | Purpose, system components, fidelity ladder, conceptual roadmap |
| D02 | Mathematical Bounds and Limits Framework (MCLF) | Independent physical bounds, checks, invalidation |
| D03 | Scientific and system requirements | Verifiable capabilities and acceptance criteria |
| D04 | Numerical methods and solvers | Equations, model regimes, solver selection and discretization |
| D05 | Computing resources and environments | Resource budgets and execution tiers |
| D06 | Verification and validation | Benchmarks, convergence, uncertainty, evidence quality |
| D07 | Experiments, data and reproducibility | Experiment/run identity, manifests, retention and bundles |
| D08 | Software architecture and contracts | Modules, APIs, CLI, dependencies and error handling |
| D09 | Scientific register, claims and literature | Equation and claim traceability, sources, evidence and novelty |
| PLAN-01 | Project execution plan | Phase order, work packages, gates, stop rules and scope control; it cannot override D00-D09 |

Working procedures: G01 contributor workflow; G02 experiment lifecycle; G03 anomaly handling; G04 run reproduction; G05 release and review.

## Precedence

1. Physical laws, definitions and SI conventions.
2. D02 for validity checks and physical falsification criteria.
3. D03 for requirements and acceptance criteria.
4. D04 for model and solver choice.
5. D05 for execution constraints.
6. D06 for acceptable verification and validation evidence.
7. D07 for reproducibility and data handling.
8. D08 for software implementation contracts.
9. D09 for scientific interpretation and claims.

When a document conflicts with physical law or a primary source, do not resolve the conflict by choosing the newer document. Record an issue, freeze affected claims, review the evidence, and version the corrected baseline.

## Core vocabulary

- **AURA:** research system for adaptively regulated ultrasonic acceleration.
- **Acoustic pseudogravity:** prescribed acceleration produced by non-gravitational forces; it is not gravity generation.
- **MCLF:** independent Mathematical Bounds and Limits Framework that audits simulator inputs and outputs.
- **Experiment:** versioned scientific question, hypothesis, observables and protocol; it can have multiple runs.
- **Run:** one uniquely identified execution with fixed inputs, code revision, environment and seed.
- **Solver:** numerical implementation approximating a specified physical model.
- **Benchmark:** analytical, published or independently computed reference case.
- **Claim:** explicit scientific statement supported by traceable evidence.
- **Gate:** condition required before advancing to higher fidelity or cost.

## Document states and versions

`DRAFT` is editable and does not authorize scientific decisions. `REVIEW` is complete and awaiting technical review. `BASELINE` is approved as a development source of truth. `SUPERSEDED` is replaced but retained for traceability. `ARCHIVED` is historical and non-operational.

Use MAJOR.MINOR versions. Increase MAJOR when requirements, accepted equations, falsification criteria, data contracts or decisions could change prior results. Increase MINOR for clarifications or additions that do not change the interpretation of accepted runs.

## Baseline approval

On 2026-10-01, the project owner approved D00-D09 and PLAN-01 as the controlled development baseline. The decision is recorded in [DEC-001](decisions/DEC-001-p0-baseline-approval.md) against commit `8cbd2e2e50a17e96299fd00dbba667b5c3b24ed4`. On 2026-10-02, the owner approved the first measurable force-model benchmark and a staged search for later benchmarks; [DEC-002](decisions/DEC-002-initial-measurable-force-benchmark.md) records the scope. The owner later directed that missing evidence must not stop independent foundation work; [DEC-003](decisions/DEC-003-nonblocking-foundation-work.md) records the evidence limits and sequencing change. [DEC-004](decisions/DEC-004-staged-mass-and-size-expansion.md) records the broader water-particle and scale-progression research direction. [DEC-005](decisions/DEC-005-air-validation-route.md) records the owner-selected air validation medium and P4 route while preserving water as a separate evidence track. PLAN-01 v1.4 is current; v1.0–v1.3 are preserved in the archive. G01-G05 remain DRAFT pending procedure review. These directions authorize foundation work and a gated research scope; they do not validate AURA's hypothesis, establish feasibility, or permit claims beyond the available evidence.

## Progress while evidence is incomplete

An incomplete measurement source does not block work that does not depend on the missing information, such as units, schemas, dimensional checks and analytical field cases. The affected comparison remains EXPLORATORY or INDETERMINATE until its evidence gap is resolved. This permission does not bypass D02, D04-D09, resource preflight, convergence or claim review, and does not authorize a stronger scientific claim. See DEC-003 for the approved work sequence.

## Definition of ready

- D00-D09 and G01-G05 are available and versioned.
- SI units and coordinate conventions are fixed.
- Experiment schema and run manifest are defined.
- MCLF can perform dimensional sanity checks.
- An analytical benchmark is selected.
- Resource preflight estimates CPU, RAM, storage and runtime.
- Git review and automated quality checks are in place.

## Definition of done for a scientific result

A result is reproducible from an immutable commit and configuration, is not MCLF `INVALIDATED`, includes convergence evidence or a justified regime, is compared with an analytical/published/independent reference, states assumptions and uncertainty, and supports no claim stronger than its evidence.

## Source document review

Three supplied PDFs were inspected: the 74-page baseline, the 15-page architecture proposal and the 14-page MCLF proposal. The baseline contains D00-D09 and G01-G05 material, including duplicated full copies of D01 and D02. The two standalone proposals are earlier versions of those duplicated sections. Their technical content was consolidated into this English document set. Unmodified Spanish originals are retained under references/source_documents as source material; maintained specifications and procedures remain in English.

Review findings and resolutions:

1. **Status ambiguity:** the source calls the baseline operational while several requirements, thresholds and roadmap items remain proposals. The owner has approved D00-D09 as the controlled development baseline; the scientific hypothesis and feasibility remain unvalidated, and all procedures G01-G05 remain `DRAFT` pending their own review.
2. **Version drift:** the standalone architecture is v0.1, the MCLF is v0.1, and baseline copies are presented as v1.0. The English documents retain baseline IDs and v1.0 versions; the owner's approval establishes them as project development contracts, not as independently validated physics or demonstrated performance.
3. **Acceptance thresholds lack derivation:** proposed error thresholds (including 2% for simple wave cases) need benchmark-specific justification and must not be universal tolerances.
4. **Force bound scope:** `F <= kappa P/c`, with `kappa` up to 2, only applies under stated incident-wave and momentum-transfer assumptions. It must not be used as a universal bound for arbitrary standing fields, multiple sources, cavities or stored energy. D02 records it as conditional.
5. **Acceleration interpretation:** `F_ac = m a*` is a control objective for the selected object and interval, not proof that an extended body experiences uniform gravity-like loading. D01 makes that scope explicit.
6. **Hardware and human-scale implications:** the source discusses a 5 m station and agency proposals without validated scale-up evidence. They remain future research topics, not requirements or feasibility claims.
7. **Tool versions:** listed solver/library versions are dated snapshots. D05 requires a locked environment and current compatibility review before implementation; no version is treated as endorsed merely by appearing in the source.
8. **Bibliography:** references copied from the source proposal are leads, not a verified or exhaustive bibliography. D09 requires DOI/metadata and equation-level source checks before claims are accepted.

## Change control

Scientific changes require an issue or decision record stating affected IDs, rationale, evidence, consequences for existing runs and required version changes. Never silently edit a baseline equation or acceptance criterion.
