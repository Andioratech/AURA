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

The numerical workflow is first qualified against the existing water-like analytical evidence, then tested against the air field benchmark selected in [DEC-005](docs/decisions/DEC-005-air-validation-route.md) and sequenced in [DEC-006](docs/decisions/DEC-006-water-qualification-before-air-route.md). If air P4 passes, the initial force, dynamics and control path continues in air. Water and air remain one connected program with separate physics and evidence; neither domain validates the other. The research objective also includes greater masses, larger objects and other geometries through a [staged scale progression plan](docs/planning/11-scale-progression.md). Each new domain requires an appropriate physical model and independent evidence before its performance can be claimed.

## Scientific approach

1. **Define the model and domain.** State the governing equations, approximations, boundary conditions, units, assumptions, and intended observables.
2. **Check physical plausibility independently.** The Mathematical Bounds and Limits Framework (MCLF) evaluates dimensions, invariants, model validity, conditional bounds, and evidence sufficiency without reusing the simulator blindly.
3. **Verify numerical implementations.** Compare with analytical and published benchmarks, perform observable-based convergence studies, and use an independent method for claim-critical results.
4. **Run reproducible experiments.** Version experiment definitions; identify each run by its exact inputs, code revision, environment, seeds, outputs, and checksums.
5. **Limit claims to evidence.** Separate software verification, model validation, simulation results, and physical measurements. Do not infer hardware or human-scale feasibility from a simulation outside its validated domain.

## Project maturity

This repository contains an owner-approved English development baseline (D00-D09 and PLAN-01) and a software scaffold. The supporting procedures G01-G05 remain DRAFT. It does not yet contain a validated acoustic solver, an experimentally demonstrated system, or evidence that AURA achieves its research objective. Baseline approval controls the research process; it does not establish physical feasibility or validate a model.

Implemented foundations include a [versioned JSON/YAML input and evidence schema](docs/research/schema-contract.md) and [safe SI arithmetic with explicit conversions](docs/research/numerical-domain-and-conversions.md). [FND-01](docs/work-items/FND-01.md), [FND-02](docs/work-items/FND-02.md) and [FND-03](docs/work-items/FND-03.md) record the delivered work, verification and limitations. Accepting an input or passing an arithmetic check does not validate its physical model.

[FND-04](docs/work-items/FND-04.md) adds [ten L0 audit rules](docs/registers/mclf-l0-rules.md), structured diagnostics and human-readable reports. Missing model coverage and unverified external evidence remain explicit; a supplied success label cannot establish scientific acceptance. Higher audit levels and simulation solvers remain future work.

[FND-05](docs/work-items/FND-05.md) verifies reference answers, JSON/YAML rejection diagnostics and acceptance-gate behavior through instrumented test hooks. The [B-01/B-02 report](docs/benchmarks/B01-B02-foundation-verification.md) records that task's coverage and follow-up work; actual runner integration remains pending.

[FND-06](docs/work-items/FND-06.md) exposes these checks through `aura validate-config <path> [--json]`. The [CLI guide](docs/cli-usage.md) covers installation, diagnostics and exit codes. The manufactured example has valid structure and an INDETERMINATE scientific audit (exit 3); configuration checks do not run a simulation.

[FND-07](docs/work-items/FND-07.md) adds [canonical content identity](docs/research/content-identity.md), explicit manifest/configuration link checks and bounded local file-integrity checks. The [B-02 report](docs/benchmarks/B02-content-identity.md) verifies reordering equivalence and detection of changed content. RUN-01 adds diagnostic run storage and source/environment evidence binding; RUN-02 replays verified analytical runs from their recorded commit in a fresh ENV-1.0 environment. Exact software reproduction does not validate the physical model.

[FND-08](docs/work-items/FND-08.md) delivers the [locked Python environment](requirements/README.md), fresh-install checks and installed-profile verification. The [P2 exit review](docs/reviews/P2-foundation-exit.md) records **PASS for software foundations**, with 784 passing checks and separate unresolved scientific statuses. The analytical-field campaign is complete within its software scope; its deterministic P3 evidence assessment and owner decision record bounded P3 PASS. No physical simulation result is claimed.

[RUN-01](docs/work-items/RUN-01.md) adds an [immutable recorder](docs/research/run-lifecycle.md) and `aura run` / `aura check`. It preserves clean-source/environment identity, exact input/output hashes and failed/aborted executions. ANA-07 adds versioned plane-field and spherical-field policies, storing pressure, velocity, gradient and sample records with checked hashes and links. Its recorded matrix covers all 32 frozen B-03/B-04/B-05/B-06 configurations, with independent comparisons across 264 samples. Fresh B03-AXIAL and B06-AXIAL reproductions match all input hashes, field artifact hashes and frozen metrics. ANA-06 supplies separate energy-balance checks for four exact source definitions; these are not results rebuilt from ANA-07 run files. Artifact and sensitivity reviews are complete. The owner-recorded P3 PASS is limited to this analytical-software scope. P3's governing baseline does not require an independent reviewer. These are manufactured analytic software comparisons; they calculate no body force or motion and provide no physical validation. See the [matrix report](docs/benchmarks/ANA-07-recorded-field-matrix.md), [artifact review](docs/reviews/ANA-07-matrix-artifact-review.md), [sensitivity review](docs/reviews/ANA-07-numerical-sensitivity-review.md) and [P3 assessment](docs/reviews/P3-ANA-07-gate-review.md).

[ANA-01](docs/work-items/ANA-01.md) specifies [analytical field outputs](docs/research/analytical-field-contract.md) and [four independent reference protocols](docs/benchmarks/B03-B06-analytical-protocols.md). The immutable container carries pressure, full fluid velocity and pressure gradients with explicit units and conventions.

[NUM-01](docs/work-items/NUM-01.md) records the selected Hasegawa air piston/sphere method. [NUM-02](docs/work-items/NUM-02.md) implements `aura preflight` for the declared harmonic-series workload, including RAM/disk checks and an exact-source/environment runtime-calibration gate. NUM-03 now contains a first local coupled piston/sphere field kernel with narrow software checks; it is not integrated with run-level preflight or immutable execution, has no accepted convergence result, and has produced no accepted air-field evidence. Runtime remains INDETERMINATE without matching measured calibration. See the [preflight guide](docs/cli-usage.md#estimate-an-air-series-workload), [NUM-03 task](docs/work-items/NUM-03.md) and [interim kernel review](docs/reviews/NUM-03-coupled-kernel-review.md).

The [ANA-01 artifact review](docs/reviews/ANA-01-field-contract.md) records its 1,033 passing software checks. [ANA-02](docs/work-items/ANA-02.md) adds the [single progressive plane-wave kernel](docs/research/plane-wave-kernel.md), with independent B-03 numerical comparisons. [ANA-03](docs/work-items/ANA-03.md) adds the bounded counterpropagating-pair kernel. [ANA-04](docs/work-items/ANA-04.md) adds [coherent two-wave interference](docs/research/two-wave-kernel.md), including noncollinear directions. [ANA-05](docs/work-items/ANA-05.md) adds [ideal spherical spreading](docs/research/spherical-wave-kernel.md) with explicit source exclusion and full reactive velocity. ANA-07's 32-case B-03/B-04/B-05/B-06 matrix and fresh B03-AXIAL/B06-AXIAL reproductions pass their frozen software checks. Numerical sensitivity and artifact reviews are complete; the deterministic assessment and owner decision record bounded P3 PASS. Experimental validation remains NOT ESTABLISHED.

The [B-03 numerical report](docs/benchmarks/B03-plane-wave-verification.md) records 11 manufactured configurations, independent reference/error checks and 1,163 passing software tests. [ANA-02 is complete](docs/reviews/ANA-02-plane-wave.md); [ANA-03 is complete](docs/reviews/ANA-03-counterpropagating.md): its [B-04 report and diagnostic plot](docs/benchmarks/B04-counterpropagating-verification.md) cover eight opposing-wave configurations and 1,223 passing software tests. [ANA-04 is complete](docs/reviews/ANA-04-interference.md): its [B-05 report](docs/benchmarks/B05-interference-verification.md) covers eight coherent two-wave configurations and 1,288 passing software tests. [ANA-05 is complete](docs/reviews/ANA-05-spherical.md): its [B-06 report](docs/benchmarks/B06-spherical-verification.md) covers five spherical configurations and 1,351 passing software tests. [ANA-06 is complete for its frozen model-specific energy-ledger scope](docs/reviews/ANA-06-energy-balance.md): the [report](docs/benchmarks/ANA-06-energy-balance-verification.md) records four passing cases, independent expectations and negative tests. ANA-07's [full recorded matrix](docs/benchmarks/ANA-07-recorded-field-matrix.md) passes its frozen software-comparison criteria; the deterministic assessment and owner decision record bounded P3 PASS. Energy accounting is not momentum/force calculation and does not establish physical feasibility.

## Repository structure

| Path | Purpose |
|---|---|
| docs/ | Controlled scientific, numerical, and software specifications (D00-D09) |
| guides/ | Procedures for contribution, experiments, anomaly handling, reproduction, and review (G01-G05) |
| src/aura/ | Foundations, diagnostic recorder and bounded analytical plane and spherical kernels |
| tests/ | Starting point for software and scientific verification cases |
| examples/ | Versioned experiment configurations |
| data/ | Data provenance and retention policy |
| results/ | Run output policy; generated results are excluded from Git |
| references/source_documents/ | Unmodified source PDFs and checksums |
| assets/ | README and project identity assets |

## Start here

- [Resume the project: current checkpoint and next task](docs/handoff/README.md)

The current water-reference review retains Barnkob et al. (2012) as an exploratory small-particle velocity-field source; formal measurement acceptance remains INDETERMINATE because raw data and complete uncertainty inputs are unavailable in this checkout. See the [LIT-02 comparison and benchmark design](docs/benchmarks/water-reference-selection.md) and [current checkpoint](docs/handoff/CURRENT-STATE.md).

- [Install and validate a configuration](docs/cli-usage.md)
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
