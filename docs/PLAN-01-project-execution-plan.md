# PLAN-01: AURA Phase-Gated Master Work Plan

**Version:** 1.0 · **Status:** BASELINE · **Owner:** AURA project owner · **Last updated:** 2026-10-01

## 1. Purpose

This plan converts the AURA proposal into a bounded sequence of scientific and software work. It is designed to prevent premature complexity, uncontrolled scope growth, and claims that exceed evidence. It defines order, deliverables, measurable exit gates, and rules for stopping or revising work.

This is a work-sequencing document. It does not approve a physical model, prove feasibility, alter D00-D09 requirements, or authorize hardware construction. If it conflicts with D00-D09 or an established physical law, the higher-precedence source governs and the plan must be updated.

## 2. Operating rules

1. **One active phase.** Work on the next phase starts only after the current phase's exit review is recorded as PASS. The owner may explicitly pause or reprioritize.
2. **One scientific question per work item.** Each issue or task has one question, one primary observable, a fixed domain, named artifacts, and a pass/fail/indeterminate condition.
3. **Freeze before compute.** Version the configuration, model, assumptions, primary metric, tolerance rationale, seed policy, and resource budget before the run.
4. **No hidden scope changes.** A changed equation, object class, regime, geometry, target, metric, solver fidelity, or hardware assumption requires a decision record and may require a new experiment ID.
5. **Fail closed.** An invalid input, failed preflight, hard MCLF violation, or unmet required convergence stops promotion. Preserve the failed run and diagnose before adding features.
6. **Use the simplest adequate model.** Increase fidelity only to resolve a stated uncertainty or answer a named question. Higher computational cost is not evidence of higher validity by itself.
7. **Maintain independence.** The MCLF and claim-critical comparisons must not simply duplicate the same implementation path being checked.
8. **No AI-driven scope expansion.** AI may help with code navigation, literature discovery, or editing. It may not silently add hypotheses, dependencies, physical models, or requirements.
9. **No calendar promises before estimates.** Establish effort and dates only after resource preflight and task decomposition. Sequence is controlled by gates, not speculative deadlines.
10. **Every outcome is reportable.** PASS, FAIL, ALERT, and INDETERMINATE are valid recorded outcomes; do not rerun only until a favorable answer appears.

## 3. Global completion conditions

An individual scientific result is complete only when:

- the question, domain, hypothesis, observable, and decision rule were fixed before the run;
- the run is reproducible from its immutable commit and manifest;
- all applicable MCLF rules are reported and none returns INVALIDATED;
- the primary observable has required convergence evidence or a justified non-grid method;
- comparison with the preselected analytical, published, or independent reference is complete;
- uncertainty, assumptions, numerical limitations, and failed cases are recorded;
- the conclusion is limited to the tested domain and reviewed under D09.

A project phase is complete only when every mandatory work package has an artifact, every phase gate is satisfied, unresolved exceptions are explicitly accepted by the owner, and the decision record identifies the next phase or a stop.

## 4. Phase map

| Phase | Name | Main exit evidence | Dependency |
|---|---|---|---|
| P0 | Repository, provenance, and governance | Clean structure, source inventory, controlled plan, owner-approved baseline | Current |
| P1 | Bounded scientific question and benchmark selection | Frozen domain, one benchmark, observable, decision rule | P0 |
| P2 | Units, schemas, and MCLF L0 | Validated SI contracts, dimensional checks, known-answer cases | P1 |
| P3 | Analytical acoustic foundation | Reproduced closed-form field cases with quantified errors | P2 |
| P4 | First numerical field solver | Solver verified against Phase 3 and resource-bounded | P3 |
| P5 | One regime-specific force/torque model | Published/analytical force benchmark reproduced in-domain | P4 |
| P6 | Rigid-body dynamics and numerical verification | Independent dynamics cases, convergence and balance checks | P5 |
| P7 | Deterministic closed-loop control | Frozen target case meets predeclared tracking/stability criteria | P6 |
| P8 | Robustness and uncertainty | Sensitivity, uncertainty, failures, and operating-domain map | P7 |
| P9 | Independent high-fidelity confirmation | Claim-critical result reproduced using independent formulation | P8 |
| P10 | Experimental feasibility decision | Reviewed design study with safety, cost, and evidence case | P9 |

Do not combine phases to save time. A phase may split into subphases only by a recorded decision that preserves the original gates.

## 4.1 Current phase tracker

| Phase | Status | Blocking condition / next action |
|---|---|---|
| P0 | PASS | Owner acceptance recorded in DEC-001; repository, source provenance, links, local quality checks, and remote CI passed |
| P1 | ACTIVE | P1.1 dossier is complete and awaits review; next score the three candidates under P1.2, without implementation |
| P2-P10 | BLOCKED | Advance only after the preceding phase receives a recorded PASS decision |

## 5. Phase details

### P0 — Repository, provenance, and governance

**Question:** Is the working baseline organized and controlled well enough to begin a bounded scientific study?

**Work packages**

- P0.1 Move source PDFs from the root into references/source_documents; preserve bytes and record filenames, page counts, and SHA-256 checksums.
- P0.2 Remove exact duplicate root assets only after comparing checksums; retain the required source asset in its canonical assets/ location.
- P0.3 Keep root limited to project entry points and tool configuration. Route specifications to docs/, procedures to guides/, original source files to references/source_documents/, implementation to src/, tests to tests/, inputs to examples/ or experiments/, and generated output to ignored results/.
- P0.4 Reconcile README, D00, source inventory, and project language/status statements.
- P0.5 Confirm commit identity policy, ignore rules for local AI guidance and CodeGraph data, and reproducible CodeGraph installation/configuration.
- P0.6 Review this plan and mark current documents DRAFT, REVIEW, or BASELINE honestly.

**Deliverables:** source-document inventory; clean root; consistent README/D00; approved plan; no unclassified files; local tools documented without committing machine-specific configuration.

**Exit gate:** all root files have a stated purpose or documented destination; source checksums match; internal links resolve; no untracked file is accidentally mistaken for a deliverable; owner accepts the scientific baseline and plan.

**Stop conditions:** missing provenance, conflicting claims with no decision, uncertain ownership/license, or unstable repository identity. Do not start solver implementation while these remain unresolved.

**Decision and evidence:** P0 PASS was recorded on 2026-10-01 after owner approval, source checksum verification, repository review, local quality checks, and successful remote CI. See [DEC-001](decisions/DEC-001-p0-baseline-approval.md). The accepted baseline is D00-D09 and this plan at commit `8cbd2e2e50a17e96299fd00dbba667b5c3b24ed4`; G01-G05 remain DRAFT. Baseline approval authorizes phase-gated research only; it does not mean a solver or benchmark has been validated.

### P1 — Bounded question and benchmark selection

**Question:** What is the smallest reproducible acoustic-force case that tests one scientifically meaningful AURA capability?

**Work packages**

- P1.1 Extract candidate benchmarks from primary literature. Record exact citation, DOI, equation/table/figure, source parameters, and known errata.
- P1.2 Score each candidate for parameter completeness, analytical/reference availability, regime match, implementability, and independence from planned code.
- P1.3 Select exactly one primary benchmark and one backup. The backup is not implemented unless the primary is unusable for a documented reason.
- P1.4 Freeze one body shape and material, medium state, source/array geometry, frequency, boundary assumptions, state variables, initial conditions, and the modeled gravity environment.
- P1.5 Define one primary observable and its units, sampling, averaging interval, and comparison formula. Secondary metrics are diagnostic only.
- P1.6 Define the falsification/stop condition, tolerance derivation, uncertainty sources, and allowable parameter range before computing.
- P1.7 Estimate CPU, RAM, storage, and wall time; reject a case that cannot be independently verified within available resources.

**Deliverables:** benchmark dossier; experiment definition; parameter/provenance table; observable and uncertainty specification; resource preflight; immutable EXP ID.

**Exit gate:** every required input is sourced or explicitly measured/assumed; an independent reference exists; the primary observable and pass/fail/indeterminate rule are reviewable; owner approves the frozen domain.

**Out of scope:** optimization, control, AI, multi-object claims, human-scale extrapolation, and physical prototype design.

### P2 — Units, schemas, and MCLF L0

**Question:** Can malformed, dimensionally inconsistent, or incomplete inputs be rejected before compute?

**Work packages**

- P2.1 Define canonical SI representations and pressure amplitude/RMS conventions.
- P2.2 Define versioned schemas for Medium, source/array, Body, Scenario, SolverSpec, Experiment, and RunManifest.
- P2.3 Require units or dimensioned quantities at external inputs; define explicit conversion boundaries.
- P2.4 Implement pure calculations for wavelength, wave number, and size parameter ka, with documented inputs and assumptions.
- P2.5 Implement finite-value, positivity/range, vector-shape, and dimensional consistency checks.
- P2.6 Create known-valid and known-invalid cases, including unit conversion and boundary values.
- P2.7 Implement stable rule IDs R-001 through R-010 with assumptions, severity, diagnostic, and tested predicate.
- P2.8 Define canonical serialization and content hashes; ensure ordering and float formatting are deterministic.

**Deliverables:** schemas; units module; MCLF L0 rule registry; known-answer case table; validation report format; requirement-to-check matrix.

**Exit gate:** all known invalid cases are rejected with specific diagnostics; valid examples serialize deterministically; dimensional calculations match independent hand-calculated references; no silent defaults fill missing scientific quantities.

**Out of scope:** acoustic PDE solver, force model, physical bounds beyond the implemented conditional checks.

### P3 — Analytical acoustic foundation

**Question:** Does the implementation reproduce a minimal set of closed-form acoustic fields under explicitly stated assumptions?

**Work packages**

- P3.1 Define the homogeneous, linear, lossless/attenuating model selected for the chosen benchmark.
- P3.2 Implement the simplest analytical field case required by the benchmark (for example a plane wave or a documented monopole approximation).
- P3.3 Add one-source amplitude/phase convention checks and unit tests for complex representation.
- P3.4 Add a two-source interference case with an analytical expected pattern.
- P3.5 Add a propagation/spreading case only where its far/near-field assumptions are met.
- P3.6 Validate limiting behavior, symmetry, and energy or intensity consistency where the control volume is well-defined.
- P3.7 Compare outputs against a separately computed reference; record precision and error decomposition.

**Deliverables:** analytical field module; independent derivation notebook or reviewable calculation; regression fixtures; short benchmark report.

**Exit gate:** each selected analytical case passes its predeclared error tolerance; results are stable under precision checks; all approximation limits are included in result metadata.

**Out of scope:** complicated boundaries, scattering by the target object, array optimization, and force calculation.

### P4 — First numerical field solver

**Question:** Can one numerical solver reproduce Phase 3 fields on a resource-bounded domain?

**Work packages**

- P4.1 Select one fast numerical method matched to the Phase 1 benchmark; justify why it answers the question.
- P4.2 Specify mesh/grid, boundary conditions, solver precision, tolerances, and resource estimate.
- P4.3 Implement input validation and preflight before allocating the numerical domain.
- P4.4 Compare the solver pointwise and through the primary field observable with Phase 3.
- P4.5 Run at least three grid or discretization levels for the observable; record actual convergence.
- P4.6 Test domain expansion or boundary/PML sensitivity if boundaries can contaminate results.
- P4.7 Record runtime and peak memory; update the approved resource envelope from observed measurements.

**Deliverables:** one numerical field backend; solver contract and metadata; convergence table; memory/runtime report.

**Exit gate:** predeclared field observable converges within its benchmark-specific tolerance; boundary effects are bounded; MCLF reports no hard violation; resource preflight predicts within a documented margin.

**Out of scope:** adding a second backend just for breadth; high-fidelity FEM/BEM unless the primary benchmark demonstrates the need.

### P5 — One regime-specific force and torque model

**Question:** Can one declared force model reproduce the selected benchmark within its stated validity domain?

**Work packages**

- P5.1 Select the force formulation from the frozen body size, ka, material, field and fluid assumptions.
- P5.2 Trace every equation and coefficient to a primary source and record the regime in D09.
- P5.3 Implement one force model; return forces/torques plus validity status and model provenance.
- P5.4 Compare with benchmark values across the benchmark's reported parameter points.
- P5.5 Perform dimensional, sign, symmetry, limiting-case, and conservation/momentum-flux checks where applicable.
- P5.6 Check conditional force estimates only when their assumptions match; disagreement triggers investigation, not an arbitrary pass threshold.
- P5.7 Generate a reproducible force-benchmark report and update the model's limitations.

**Deliverables:** one force model; equation traceability; benchmark reproduction report; validity-domain tests; updated MCLF checks.

**Exit gate:** benchmark-specific tolerance is met over the declared points; no tested point silently crosses the model regime; discrepancies and excluded regimes are explicit.

**Out of scope:** treating force as uniform body loading; extrapolating particle results to macroscopic bodies; combining incompatible force models.

### P6 — Rigid-body dynamics and numerical verification

**Question:** Given validated forces, does the rigid-body integrator solve the declared dynamics accurately?

**Work packages**

- P6.1 Define translational and rotational state, coordinate frames, inertia representation, and force/torque application points.
- P6.2 Implement one documented time integrator and a fixed-step reference configuration.
- P6.3 Verify free motion, constant force, constant torque, and gravity-only cases against analytical solutions.
- P6.4 Check integration order and observable convergence under time-step refinement.
- P6.5 Evaluate energy and momentum balances only for cases with defined system boundaries and known external inputs.
- P6.6 Validate acceleration metrics over an explicitly frozen averaging window.
- P6.7 Add run-manifest creation and MCLF post-check, including failure retention.

**Deliverables:** rigid-body dynamics module; analytical regression cases; time-step convergence report; manifest and run-output layout.

**Exit gate:** analytical state and metric errors meet predeclared tolerances; no unexplained balance drift; replay reproduces declared metrics from the same commit/configuration/seed.

**Out of scope:** deformable body, fluid-structure interaction, tissue, contact-rich mechanics, or stochastic disturbances unless they are the frozen benchmark question.

### P7 — Deterministic closed-loop control

**Question:** Can a deterministic controller maintain one declared acceleration target in one idealized validated case?

**Work packages**

- P7.1 Freeze target vector, body, target duration, control update rate, sensor state access, actuator limits, and acceptance window.
- P7.2 Establish the uncontrolled/open-loop baseline and quantify disturbances/model limitations.
- P7.3 Implement one deterministic baseline controller (PID first unless the frozen case justifies another).
- P7.4 Define saturation, anti-windup, update timing, and controller stability metric.
- P7.5 Measure target-acceleration error, position drift if relevant, actuator demand, stability and failure conditions.
- P7.6 Perform parameter sensitivity without selecting controller gains from the final evaluation case.
- P7.7 Repeat with fixed seeds/configuration and report performance distribution where stochasticity exists.

**Deliverables:** controller contract; open-loop and closed-loop run manifests; predeclared target metric report; controller stability and saturation analysis.

**Exit gate:** the target case meets its predeclared metric and stability criteria for the declared duration and limits; independent reproduction succeeds; no actuator constraint is omitted.

**Out of scope:** machine learning, reinforcement learning, online adaptation, and claims of body-independent acceleration.

### P8 — Robustness and uncertainty

**Question:** Over what bounded parameter region does the validated baseline remain reliable, and how uncertain is that region?

**Work packages**

- P8.1 Separate numerical, parameter, model-form, and measurement uncertainty.
- P8.2 Select one-at-a-time sensitivity parameters and justify ranges from sources or hardware specifications.
- P8.3 Freeze sweep design, sample count, random seed strategy, and statistics before execution.
- P8.4 Run local sensitivity first; expand to Monte Carlo only if sensitivity suggests meaningful interactions or distributions.
- P8.5 Track all failures, alerts, solver nonconvergence, and out-of-domain points.
- P8.6 Map the supported operating region with confidence/uncertainty, not a single best-case point.
- P8.7 Re-run boundary cases at higher resolution or by an independent formulation.

**Deliverables:** uncertainty register; sweep manifest set; sensitivity report; operating-domain map; retained failure catalogue.

**Exit gate:** all variability sources are classified; supported and unsupported regions are distinguished; the primary conclusion is robust to required numerical refinement and has uncertainty bounds.

**Out of scope:** unbounded optimization, cherry-picked best cases, extrapolation beyond sampled and justified ranges.

### P9 — Independent high-fidelity confirmation

**Question:** Does the claim-critical conclusion survive an independent physical/numerical formulation of appropriate fidelity?

**Work packages**

- P9.1 Identify the exact claim and determine what discrepancy an independent method must resolve.
- P9.2 Select an independent method with minimal shared implementation and a justified regime.
- P9.3 Define equivalence of inputs, observables, tolerances, and boundary assumptions before running.
- P9.4 Perform convergence and sensitivity in the independent method.
- P9.5 Compare methods and classify agreement, qualified disagreement, or unresolved regime.
- P9.6 Obtain independent technical review of assumptions and evidence.
- P9.7 Update D09 claim status and preserve both agreeing and disagreeing results.

**Deliverables:** method-independence statement; comparison protocol; convergence datasets/references; independent review; claim-level evidence bundle.

**Exit gate:** methods agree within a justified tolerance or the disagreement is resolved with a documented explanation; claim is limited to verified conditions; D09 is reviewed.

**Out of scope:** adding fidelity without a defined claim or unresolved uncertainty; treating solver agreement as experimental validation.

### P10 — Experimental feasibility decision

**Question:** Does existing evidence justify designing a physical experiment, and can it be performed safely and meaningfully?

**Work packages**

- P10.1 Review the complete simulation evidence and unresolved uncertainties.
- P10.2 Define one measurable experimental hypothesis and an observable that distinguishes competing models.
- P10.3 Design measurement geometry, calibration, control group, uncertainty budget, acoustic exposure assessment, and data provenance.
- P10.4 Estimate transducer count/aperture, acoustic power, electrical input, thermal load, chamber constraints, cost, and compute/analysis needs with sourced values.
- P10.5 Perform applicable safety, environmental, legal, and institutional review before any exposure or hardware operation.
- P10.6 Obtain owner and qualified domain-expert review of design and budget.
- P10.7 Record GO, REVISE, or NO-GO with evidence and explicitly bounded interpretation.

**Deliverables:** reviewable experimental design; measurement/uncertainty plan; sourced resource and safety assessment; signed decision record.

**Exit gate:** the experiment can discriminate the stated hypothesis, has adequate uncertainty and controls, is within approved safety/institutional limits, and receives explicit owner authorization.

**Out of scope:** procurement, construction, operation, human exposure, or 5 m station claims by this plan alone. These require separate authorization and applicable review.

## 6. Gate review template

At every phase boundary, record:

- phase and gate ID;
- artifacts and immutable commit;
- criteria evaluated, with measured values and source of each threshold;
- MCLF verdicts and open alerts;
- convergence/benchmark/uncertainty evidence;
- unresolved limitations and their impact;
- decision: PASS, FAIL, HOLD, or INDETERMINATE;
- owner/reviewer and date;
- authorized next phase and scope;
- explicit deferred questions.

PASS advances one phase only. FAIL returns named work items. HOLD waits for specified evidence or decision. INDETERMINATE requires a method better matched to the question; it is not treated as success.

## 7. Work item template

Every issue/task must contain all of the following before implementation:

1. Work item ID and phase.
2. One-sentence question.
3. Hypothesis/prediction and falsification condition.
4. Exact domain and versioned input configuration.
5. One primary observable, units, formula, and measurement/computation window.
6. Model equations, assumptions, validity regime, solver, precision, and boundary conditions.
7. Reference source and independent check.
8. Predeclared acceptance threshold with derivation and uncertainty.
9. Resource preflight and stop conditions.
10. Required output artifacts and manifest fields.
11. Explicit non-goals and deferred questions.
12. Gate and reviewer.

If any field cannot be completed, the item is a research-design task, not an implementation task.

## 8. Anti-drift controls

- Maintain a single phase board with statuses: BLOCKED, READY, ACTIVE, REVIEW, DONE. Only one work item may be ACTIVE per phase.
- New ideas go into a parking-lot section in the phase review; they do not enter current scope automatically.
- Do not add dependencies, solver backends, AI methods, extra body types, or new metrics without a question that requires them and an approved decision record.
- Do not optimize a result before the reference implementation passes its benchmark.
- Do not change benchmark inputs after seeing results without creating a new versioned experiment and retaining the prior one.
- Limit a work cycle to: design, implement, compare, report, review. Each cycle ends with an artifact and gate decision.
- If two consecutive work cycles fail for the same cause, stop feature work and produce a root-cause report before attempting another implementation.
- A project-wide conclusion requires at least one independent confirmation and a D09 claim review; a sweep alone cannot prove impossibility.

## 9. Parking lot — explicitly deferred

These are not current tasks and must not be started without a gate decision:

- human-scale or crewed use;
- a 5 m cubic station;
- hardware procurement or prototype construction;
- deformable bodies, tissues, fluid-structure interaction, and physiological response;
- machine-learning or reinforcement-learning controller;
- broad multi-object acceleration claims;
- multiple high-fidelity solvers in parallel;
- grant, patent, or publication claims of feasibility or novelty.

## 10. Change control

Changes to phase order, gates, primary observables, acceptance thresholds, model scope, or deferred-work boundaries require a change proposal with rationale, evidence, risks to prior results, D00/D03/D06/D09 impact, and owner decision. Increment the plan version and preserve the superseded plan. Routine task ordering within an approved phase does not require a plan version change.

## 11. Immediate next actions

1. Review the P1.1 dossier in `docs/benchmarks/P1.1-benchmark-candidates.md`; it documents three sources and deliberately selects no winner.
2. Complete P1.2 by scoring candidates against the criteria in this plan; keep scoring evidence traceable to each source.
3. Select one primary and one backup only in P1.3 after comparing the dossiers; obtain owner approval of the frozen domain at the P1 exit gate.
4. Do not start implementation before P1 PASS or implement acoustic propagation, radiation force, control, AI optimization, or high-fidelity solvers before the applicable gate.
