# 10 — Single Work Board and Execution Order

**Updated:** 2026-10-04. **Initial implementation inspected:** `aaf4aba7bff3774e645b3640784ebdcdbd14a7db`; completed work is linked below.

## First work cycle

1. FND-01 is complete: [CONV-1.0 and review](../work-items/FND-01.md) freeze the representation contract and record existing helper gaps.
2. FND-02…FND-07 are complete: [schemas](../work-items/FND-02.md), [safe arithmetic](../work-items/FND-03.md), [L0 audit rules and reports](../work-items/FND-04.md), [foundation integration verification](../work-items/FND-05.md), [configuration-validation CLI](../work-items/FND-06.md), [content identity](../work-items/FND-07.md). [FND-08](../work-items/FND-08.md) completes the locked environment; [P2 PASS review](../reviews/P2-foundation-exit.md) records the actual evidence and limits.
3. LIT-01…LIT-05 may proceed as the separate evidence track; missing measurements do not stop P2/P3.
4. The general system/core explanation was delivered at P2 exit. Before the selected numerical solver implementation, give the additional P4 explanation of components, inputs, outputs, checks and limits. RUN-01 is complete for software diagnostics; RUN-02 replay is DONE before P4 exit. These are explanation checkpoints, not approval gates.
5. Follow the remaining phase gates and decision tree. Do not start controller implementation before the required force/dynamics gates.

ANA-06 is DONE for its frozen, bounded closed-surface energy ledgers ([numerical report](../benchmarks/ANA-06-energy-balance-verification.md), [artifact review](../reviews/ANA-06-energy-balance.md)). ANA-07 is DONE for the bounded P3 software gate: all 32 recorded B-03/B-04/B-05/B-06 cases and 264 independent numerical comparisons pass; fresh B03-AXIAL and B06-AXIAL reproductions match their inputs, fields and metrics. See the [matrix report](../benchmarks/ANA-07-recorded-field-matrix.md), [artifact review](../reviews/ANA-07-matrix-artifact-review.md), [sensitivity review](../reviews/ANA-07-numerical-sensitivity-review.md) and [owner-recorded P3 PASS](../reviews/P3-ANA-07-gate-review.md). ANA-06's ledgers support four exact source definitions but are not reconstructed from ANA-07 bundle samples. The deterministic assessment is non-independent; the governing P3 baseline does not require an independent reviewer. The owner recorded PASS on 2026-10-03 for the declared analytical-software scope. This does not establish model or experimental validity. [ANA-05 is DONE](../reviews/ANA-05-spherical.md) for ideal spherical spreading, full reactive velocity and independent B-06 checks. [ANA-04 is DONE](../reviews/ANA-04-interference.md) for coherent two-wave superposition and independent B-05 cancellation/flux/symmetry checks. [ANA-03 is DONE](../reviews/ANA-03-counterpropagating.md) for the bounded opposing-wave kernel, independent B-04 comparisons and diagnostic plot. [ANA-02 is DONE](../reviews/ANA-02-plane-wave.md) for the bounded single-wave kernel and independent B-03 numerical tests. [ANA-01 is DONE](../reviews/ANA-01-field-contract.md) for the field representation and reference protocols. [RUN-01 is DONE](../reviews/RUN-01-lifecycle.md) for diagnostics; ANA-07 adds the analytic plane and spherical field policies. The owner received the requested explanation before implementation. P2 is PASS within its reviewed foundation scope. LIT-01…LIT-05 and SC-01/SC-02 are DONE as bounded documentary/research tasks. LIT-03 still does not authorize force implementation, LIT-04 does not close a coupled error budget, and LIT-05 does not close formal P1 measurement acceptance. Water measurement acceptance remains INDETERMINATE. SC-02 identifies a surface-resolved rigid-body model candidate but no validated implementation. UNK-016 records the unresolved operational acceleration-claim contract; the critique assessment's primary-source follow-up confirms the small-particle versus rigid-body force-model distinction and existing feedback-trajectory prior art without changing any gate. LIT-05 now also records prior work for solid-sphere force-model measurement, plate-supported steering, airborne levitation/manipulation and beat-driven acoustic trajectories; none demonstrates AURA's acceleration or gravity-equivalence criteria. One published beating-wave mechanism specifically relies on gravity-induced particle displacement and is predicted, not experimentally shown, to fail in microgravity. Only explicitly reviewed task records are DONE; scientific model validation remains pending. BLOCKED below means a normal dependency has not yet been delivered, not that the whole project must stop.

The critique cross-check also confirms `error_accel_rms` is already required by D01/D03; the assessment provides a parameterized acceptance template without adopting a target, threshold or claim level. Target-specific tolerance, acceleration observation uncertainty and any normalized `g_ref` report remain unfrozen in UNK-016/CTL-01. Add local, evidence-justified sensitivity checks in P4/P5 when their model inputs exist; retain integrated attack/holdout robustness for P8.

## Dependency and status table

| Task | Work item | Predecessors | Current state | Phase card |
|---|---|---|---|---|
| LIT-01 | Inventory the current evidence and unresolved decisions | Baseline available | DONE — [inventory](../research/evidence-inventory.md), [unknowns](../registers/unknowns.md) | [LIT](phases/P01-evidence.md) |
| LIT-02 | Select a measurable water reference or document the bounded fallback | LIT-01 | DONE — exploratory SRC-W03 selected; a tracked extractor reproduces six plotted 1D MQ1 profiles byte-for-byte, but raw arrays/measurement uncertainty remain unavailable and formal measurement is INDETERMINATE ([record](../benchmarks/water-reference-selection.md), [extraction review](../reviews/FIG-W03-MQ1-profile-extraction.md)) | [LIT](phases/P01-evidence.md) |
| LIT-03 | Review the actual force equations and their domain | LIT-02 | DONE — bounded candidate comparison; no implementation model frozen ([review](../research/particle-model-selection.md)) | [LIT](phases/P01-evidence.md) |
| LIT-04 | Identify fluid, wall, thermal and stochastic competing effects | LIT-03 | DONE — bounded effect ledger; coupled budget open ([record](../research/fluid-and-omitted-effects.md)) | [LIT](phases/P01-evidence.md) |
| LIT-05 | Prepare necessary-limit and prior-work investigations | LIT-04 | DONE — bounded twenty-three-record search covers force, scale and microgravity precedents plus feedback/feedforward motion control, experimentally tested acceleration-shaped movement, material-dependent sphere-force models, phased-array particle transport, acceleration-inferred force measurement, stable-acceleration-limit experiments, quantitatively reported droplet acceleration, theoretical trajectory-dependent acceleration limits and dual-frequency beat-dynamics theory; no novelty determination ([limits](../research/limits-design.md), [prior-work register](../registers/prior-work.md), [task record](../work-items/LIT-05.md), [P1 review draft](../reviews/P1-research-gate-review-draft.md)) | [LIT](phases/P01-evidence.md) |
| FND-01 | Freeze coordinate, SI and amplitude conventions | Baseline available | DONE — [record](../work-items/FND-01.md) | [FND](phases/P02-foundations.md) |
| FND-02 | Implement versioned scenario and evidence schemas | FND-01 | DONE — [record](../work-items/FND-02.md) | [FND](phases/P02-foundations.md) |
| FND-03 | Extend safe SI calculations and conversion boundaries | FND-02 | DONE — [record](../work-items/FND-03.md) | [FND](phases/P02-foundations.md) |
| FND-04 | Implement stable MCLF L0 rules and typed errors | FND-03 | DONE — [record](../work-items/FND-04.md) | [FND](phases/P02-foundations.md) |
| FND-05 | Build independent known-answer and invalid-input verification | FND-04 | DONE — [record](../work-items/FND-05.md) | [FND](phases/P02-foundations.md) |
| FND-06 | Expose configuration validation through the CLI | FND-05 | DONE — [record](../work-items/FND-06.md) | [FND](phases/P02-foundations.md) |
| FND-07 | Freeze canonical serialization and immutable hash identity | FND-06 | DONE — [record](../work-items/FND-07.md) | [FND](phases/P02-foundations.md) |
| FND-08 | Lock the development environment and close P2 | FND-07 | DONE — [record](../work-items/FND-08.md) | [FND](phases/P02-foundations.md) |
| ANA-01 | Specify field outputs and the analytic case matrix | FND-08, RUN-01 | DONE — [record](../work-items/ANA-01.md) | [ANA](phases/P03-analytical-fields.md) |
| ANA-02 | Implement a progressive plane wave and its velocity | ANA-01 | DONE — [record](../work-items/ANA-02.md) | [ANA](phases/P03-analytical-fields.md) |
| ANA-03 | Construct a standing wave with correct flux accounting | ANA-02 | DONE — [record](../work-items/ANA-03.md) | [ANA](phases/P03-analytical-fields.md) |
| ANA-04 | Verify two-source interference and allowed symmetries | ANA-03 | DONE — [record](../work-items/ANA-04.md) | [ANA](phases/P03-analytical-fields.md) |
| ANA-05 | Add only the needed spreading or attenuation reference | ANA-04 | DONE — [record](../work-items/ANA-05.md) | [ANA](phases/P03-analytical-fields.md) |
| ANA-06 | Add independent model-specific balance checks | ANA-05 | DONE — [report](../benchmarks/ANA-06-energy-balance-verification.md), [review](../reviews/ANA-06-energy-balance.md) | [ANA](phases/P03-analytical-fields.md) |
| ANA-07 | Publish P3 verification evidence and close the gate | ANA-06 | DONE — owner-recorded PASS for bounded analytical-software scope | [ANA](phases/P03-analytical-fields.md) |
| NUM-W01 | Reconcile the existing water numerical qualification | ANA-07, RUN-02, LIT-02 | DONE — bounded workflow PASS: ANA-07 has 32 ideal-field cases/264 independent reference samples; ANA-06 has four passing energy ledgers using water-like `rho=1000 kg/m³`, `c=1500 m/s`; RUN-02 exact replay passes. No water-specific field solver or physical measurement validation is established; SRC-W03 remains INDETERMINATE ([audit](../reviews/NUM-W01-water-numerical-qualification-audit.md), [task](../work-items/NUM-W01.md)) | [NUM](phases/P04-numerical-field.md) |
| NUM-W02 | Close a bounded water numerical gap if required | NUM-W01; core explanation; independent reference | NOT ACTIVATED — no additional water calculation is needed for the demonstrated software-workflow qualification; reopen only for a water-specific field-solver or physical-model claim | [NUM](phases/P04-numerical-field.md) |
| NUM-01 | Select the backend for the air field question | NUM-W01; NUM-W02 if activated; ANA-07, LIT-02 | DONE — method, stationary-sphere branch, FIELD-1.0 interface, input/domain assumptions, exclusions, discriminating checks and failure path are recorded; stability/convergence/resource feasibility remain unestablished and gate NUM-02/03 ([task](../work-items/NUM-01.md), [contract](../research/air-field-solver-contract.md), [comparison](../research/NUM-01-method-comparison.md)) | [NUM](phases/P04-numerical-field.md) |
| NUM-02 | Implement resource preflight before allocation | NUM-01 | DONE — solver-specific RAM/disk estimator, exact-context runtime-calibration gate, strict CLI and resource rejection tests. NUM-03 has a measured profile for its bounded one-gap/one-point order-512 diagnostic only; this is not a general runtime guarantee ([task](../work-items/NUM-02.md), [review](../reviews/NUM-02-resource-preflight.md)) | [NUM](phases/P04-numerical-field.md) |
| NUM-03 | Implement the selected field backend | NUM-02 | ACTIVE — the owner selected a field-only P4 error budget under [DEC-007](../decisions/DEC-007-p4-field-only-error-budget.md); no numeric threshold was adopted. Matched-order direct/public overlaps cover 444 discrete points across four gaps and three shells but are not convergence bounds. The `f8302cb` run adapter passed exact-revision remote Quality [37184239104](https://github.com/Andioratech/AURA/actions/runs/37184239104); its bounded one-point order-512 diagnostic is integrity-verified and scientifically INDETERMINATE. Next characterize uncertainty in the independent high-precision coupled reference, then freeze metrics, samples, refinements, acceptance/stopping rule and resource cap before broad runs. No P4 result exists; keep the 512 cap and model domain unchanged ([task](../work-items/NUM-03.md), [review](../reviews/NUM-03-coupled-kernel-review.md)) | [NUM](phases/P04-numerical-field.md) |
| NUM-04 | Measure observable convergence across three levels | NUM-03 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-05 | Bound boundary and domain contamination | NUM-04 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-06 | Reconcile cost, precision and reproducibility | NUM-05 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| NUM-07 | Close the field solver gate | NUM-06, RUN-02 | BLOCKED | [NUM](phases/P04-numerical-field.md) |
| FOR-01 | Freeze the air-sphere force-model contract and regime checks | NUM-07, DEC-002 | BLOCKED — air P4 PASS required; do not transfer LIT-03's water small-particle law to the 50 mm air sphere | [FOR](phases/P05-particle-forces.md) |
| FOR-02 | Implement one air-sphere force model and typed results | FOR-01 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-03 | Challenge signs, limits and conservative gradients | FOR-02 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-04 | Compare the force against an independent model reference | FOR-03 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-05 | Prepare and execute the matched air force comparison | FOR-04, DEC-002 | BLOCKED — preserve full measured range and distinguish numerical agreement from formal measurement validation; source uncertainty remains incomplete | [FOR](phases/P05-particle-forces.md) |
| FOR-06 | Resolve viscosity, thermal and streaming branches | FOR-05, LIT-04 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-07 | Audit force accounting and conditional limits | FOR-06 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| FOR-08 | Review the force-model gate and evidence dependencies | FOR-07 | BLOCKED | [FOR](phases/P05-particle-forces.md) |
| MOT-01 | Select resolved versus reduced dynamics | FOR-08, LIT-04 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-02 | Implement a complete and inspectable load ledger | MOT-01 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-03 | Implement deterministic translation with analytic references | MOT-02 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-04 | Resolve time refinement and workspace events | MOT-03 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-05 | Implement the declared rotational contract | MOT-04 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-06 | Compare Earth, ideal zero and residual-gravity cases | MOT-05 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-07 | Add stochastic motion only when required | MOT-06 | BLOCKED | [MOT](phases/P06-particle-dynamics.md) |
| MOT-08 | Compare air-sphere motion, report and close P6 | MOT-07, FOR-05 | BLOCKED — no trajectory validation is implied by the force-gap comparison | [MOT](phases/P06-particle-dynamics.md) |
| CTL-01 | Freeze the acceleration target and cheap necessary conditions | MOT-08, LIT-05 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-02 | Characterize attainable force and local authority | CTL-01 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-03 | Implement bounded actuation allocation | CTL-02 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-04 | Implement one deterministic feedback controller | CTL-03 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-05 | Add realistic virtual observations and a minimal estimator | CTL-04 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-06 | Run the frozen acceleration evaluation | CTL-05 | BLOCKED | [CTL](phases/P07-target-control.md) |
| CTL-07 | Review bounded control and authorize robustness work | CTL-06 | BLOCKED | [CTL](phases/P07-target-control.md) |
| ADV-01 | Derive and audit necessary-condition limits | CTL-07 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-02 | Freeze and run deterministic sensitivity attacks | ADV-01 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-03 | Quantify uncertainty and stochastic robustness where justified | ADV-02 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-04 | Stress the water and microgravity assumptions | ADV-03 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-05 | Recheck the strongest positive and negative cases | ADV-04 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-06 | Publish a domain map with all evidence statuses | ADV-05 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| ADV-07 | Close robustness and select independent confirmation cases | ADV-06 | BLOCKED | [ADV](phases/P08-adversarial-limits.md) |
| IND-01 | Choose an appropriately independent formulation | ADV-07 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-02 | Implement or configure the independent comparison | IND-01 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-03 | Reproduce critical runs from a fresh environment | IND-02 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-04 | Obtain technical review and close bounded claims | IND-03 | BLOCKED | [IND](phases/P09-independent-review.md) |
| IND-05 | Release the bounded research simulator and evidence package | IND-04 | BLOCKED | [IND](phases/P09-independent-review.md) |
| EXP-01 | Select the smallest experiment that could change the conclusion | IND-05 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-02 | Design measurement, calibration and uncertainty analysis | EXP-01 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-03 | Estimate resources and review the actual hardware risks | EXP-02 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-04 | Review the design and record GO, REVISE or NO-GO | EXP-03 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| EXP-05 | Close the planning-to-evidence chain and hand off | EXP-04 | BLOCKED | [EXP](phases/P10-experiment-decision.md) |
| RUN-01 | Immutable minimal run lifecycle | FND-08 and P2 PASS | DONE — [record](../work-items/RUN-01.md) | [Cross-cutting card](08-reproducibility-and-ci.md) |
| RUN-02 | Replay, comparison and evidence reporting | RUN-01, ANA-07 | DONE — exact source-bound replay, metric comparison, reports and local Quality; see [task record](../work-items/RUN-02.md) and [artifact review](../reviews/RUN-02-replay-report.md) | [Cross-cutting card](08-reproducibility-and-ci.md) |
| SC-01 | Register candidate mass, size and shape campaigns | DEC-004; LIT-01 inventory when available | DONE — [candidate dossier](../research/scale-candidates.md), [task record](../work-items/SC-01.md) | [Scale progression](11-scale-progression.md) |
| SC-02 | Establish whether a model change is needed | SC-01; relevant source/applicability review | DONE — [model-change review](../research/scale-model-change.md), [task record](../work-items/SC-02.md) | [Scale progression](11-scale-progression.md) |
| SC-03 | Verify and compare larger-body forces | SC-02 and candidate foundation/field gates | BLOCKED | [Scale progression](11-scale-progression.md) |
| SC-04 | Test acceleration and rotational behavior | SC-03 and candidate force/dynamics gates | BLOCKED | [Scale progression](11-scale-progression.md) |
| SC-05 | Publish limits across investigated scales | SC-04 outcome or reviewed earlier limitation | BLOCKED | [Scale progression](11-scale-progression.md) |

## Review queue and external dependencies

- NUM-W01 is DONE: existing records support a narrow analytical-software/replay qualification using ideal water-like inputs. They do not document a water-specific numerical field solver or validate SRC-W03 measurements. NUM-W02 is not activated for the current software-capability objective.
- NUM-01's air solver contract and NUM-02's estimator software are DONE. The requested NUM-03 construction checkpoint was delivered and the owner authorized continuation. NUM-03 has a bounded coupled kernel, focused component checks, a generic plane-wave overlap, and a nine-location coupled Rayleigh projection check across three gaps at one order. Direct Rayleigh-disk-to-modal comparison covers 444 locations at matched orders18–500 across four gaps and three radial shells; an additional order512/order1200 comparison includes both nonzero vector components. The largest sampled order change occurs at the 30 mm outer shell and is `1.14e-6` in velocity/gradient. A 300-digit extension through order1600 with radial source rules128/256/512 agrees at reported precision at that shell, but gives neither a tail bound nor an acceptance tolerance. The exact-context NUM-02 profile supports only a bounded one-gap/one-point order-512 diagnostic, whose immutable bundle verifies but whose science verdict is INDETERMINATE. Domain-wide resources, numerical tolerances and continuous convergence remain open. Only an air P4 PASS routes initial P5 onward through air; air P4 does not validate force, motion, water models or gravity equivalence.
- P5's measured force gap and P6's motion observables are different evidence. If a matched motion dataset is unavailable, retain that limitation and do not infer a trajectory pass from force data.
- IND-04 requires an actual independent qualified reviewer; prepare the complete package first and do not invent approval.
- EXP-04 requires actual owner/domain-expert review of the concrete design. No procurement or operation is authorized by this pack.
- Actuator hardware, particle material/radius, target magnitude/duration and experiment measurement choices are unresolved physical decisions with named tasks. Parameterized software and analytical verification can proceed before those values are fixed.

## Update rules

When a task changes state, record date, responsible role/person, evidence paths, commit, actual checks, open limitations and next branch in its work-item record. Update predecessor/gate references if a reviewed decision changes sequencing. A card with an INDETERMINATE research finding may be DONE as an investigation; its scientific comparison/gate remains INDETERMINATE.

## Parking list

Greater masses, larger objects and other body geometries belong to the planned SC track above. They are not excluded from the program. Exact candidate domains and numerical campaigns still need their own evidence review.

Human-scale use; arbitrary body-independent acceleration; a 5 m station; hardware procurement/operation; learning controllers; web/cloud product; multi-particle optimization without interaction evidence; multiple high-fidelity backends without a discriminating question. Add a proposal with scientific benefit and required gate before moving any into active scope.
