# P4 — Water Qualification Followed by Air Field Verification

**Maps to:** P4.1–P4.7; D04/D05/D06/D08

## Entry condition

P3 PASS. LIT-02 supplies a bounded reference geometry or an explicitly exploratory verification domain. Complete solver-specific preflight before every run.

## Domain sequence

P4 first reconciles the reported prior water numerical comparisons with immutable run and reference artifacts. This is a software/numerical-workflow qualification, not formal validation of the SRC-W03 measurements. The current repository confirms bounded P3 analytical verification, exact RUN-02 replay, and reproducible extraction of figure-derived water profiles; it does not yet document a water-specific field-solver comparison against raw measured arrays. If the existing artifacts do not meet the frozen water qualification criteria, close the gap with the smallest independently checkable water numerical case before using the shared numerical workflow in air.

After the water qualification is recorded, P4 verifies the air field for the DEC-002 source/sphere case using the method selected in NUM-01. A PASS of the air field gate routes initial P5 onward through air. It does not validate the air force model or the published force measurements, whose uncertainty remains incomplete. No result transfers between media.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## NUM-W01 — Reconcile the existing water numerical qualification

**Initial state:** READY for evidence audit. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-07, RUN-02, LIT-02

**Steps**

1. Inventory owner-reported water calculations and match each to immutable run IDs, exact input/reference data, source, metrics, comparison method and checksums.
2. Separate generic analytical-software verification, data-extraction reproducibility, water-specific numerical verification and measurement/model validation.
3. Assess whether existing water artifacts meet a predeclared numerical comparison criterion. Do not use the SRC-W03 figure-derived profiles as raw data or invent measurement uncertainty.
4. Record PASS, FAIL or INDETERMINATE for the precise workflow capability and list any smallest missing comparison needed before the air leg.

**Required artifacts:** Water numerical qualification audit; artifact-to-claim map; any missing-evidence task proposal.

**Acceptance / decision:** Every accepted prior result maps to a reproducible artifact and an independent reference. A task record may be DONE while the physical water comparison remains INDETERMINATE.

**If unsuccessful:** D-01/F-02/F-09; preserve the gap and define only the smallest bounded water numerical comparison needed.

## NUM-W02 — Close a bounded water numerical gap if required

**Initial state:** CONDITIONAL — activate only if NUM-W01 finds the numerical-workflow criterion unsupported. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-W01; simulation-core explanation checkpoint; selected independent water reference and frozen observable.

**Steps**

1. Select a water field case with fully specified medium, geometry, boundary conditions and an analytical or independently computed reference; do not assume SRC-W03's coupled particle-velocity plots are a field-solver oracle.
2. Freeze the observable, numerical tolerance rationale, precision, resource caps and run protocol before execution.
3. Use the shared validated scenario/run/comparison workflow and preserve all attempts.
4. Compare with the independent reference and record convergence and limits; keep measurement/model validation separate.

**Required artifacts:** Water qualification benchmark specification, reproducible run bundle, comparison and bounded review.

**Acceptance / decision:** The numerical workflow reproduces the selected water reference within the predeclared numerical budget. This is not a pass for the SRC-W03 measurement comparison or air physics.

**If unsuccessful:** F-03/F-04/F-09; preserve the failure and hold transition to the air leg until diagnosed.

## NUM-01 — Choose one backend that answers the selected air question

**Current state:** NUM-01 DONE as a method/contract task; NUM-02 ACTIVE. After NUM-W01 (and NUM-W02 if needed), use the DEC-002 sphere/transducer case selected under [DEC-005](../../decisions/DEC-005-air-validation-route.md). NUM-01 records Hasegawa et al.'s centered baffled-piston/rigid-sphere spherical-harmonic series and its FIELD-1.0 interface in the [solver contract](../../research/air-field-solver-contract.md), subject to NUM-02 stability/resource/convergence preflight. P4 imposes a stationary sound-hard sphere boundary at every order; derive the special `n=1` coefficient from zero normal velocity and do not reuse the source's separate translating-sphere coefficient. P4 verifies field calculations only: no measured air pressure/velocity map exists, the later force comparison remains uncertainty-limited, and acceleration/gravity equivalence remain outside this gate. Prior-art examples do not establish convergence at AURA's source/body parameters. NUM-02 implements only conservative resource estimation and pre-allocation rejection; field arrays and the numerical solver remain gated on its completion. See [NUM-01](../../work-items/NUM-01.md) and [method comparison](../../research/NUM-01-method-comparison.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-W01; NUM-W02 if activated; ANA-07; LIT-02

**Steps**

1. Reproduce the selected primary-source series equations and explicitly map its phasor convention to FIELD-1.0; keep the stationary-sphere and translating-sphere coefficient branches separate.
2. Define source normalization, geometry, air property source, centered sphere boundary, output observables, supported gap range, arithmetic and all missing physics.
3. Predeclare independent piston-only Rayleigh, P3 plane-wave, exact plane-wave/sphere and harmonic-order checks. Do not claim measured-field validation when the benchmark supplies no field maps.

**Required artifacts:** Backend decision; `fields/numerical.py` interface specification; frozen solver-domain record.

**Acceptance / decision:** The method has a clear discriminating reference, implementable boundary conditions and bounded cost.

**If unsuccessful:** D-04/F-03; justify a changed formulation or new restricted experiment.

## NUM-02 — Implement resource preflight before allocation

**Initial state:** DONE — estimator software delivered. NUM-03 has a measured runtime profile for one exact bounded workload; it does not generalize to larger point counts, other gaps or Bessel arguments. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-01

**Steps**

1. Estimate declared gap/point/order dimensions, temporary order vectors, one streamed observation chunk, runtime calibration, and output size for the selected harmonic-series implementation.
2. Require explicit memory/disk/wall-time caps and safety headroom; record how estimates are obtained.
3. Implement rejection before allocating solver arrays and test deliberate over-budget scenarios.

**Required artifacts:** `preflight.py`; CLI preflight; resource fixtures and budget rejection checks; [NUM-02 review](../../reviews/NUM-02-resource-preflight.md).

**Acceptance / decision:** Oversized cases fail before solver allocation with named estimates and alternatives; no machine-specific assumption changes the physics. An estimate cannot be BUDGETS_WITHIN_CAPS without a calibration tied to the exact clean source revision and ENV-1.0 digest. The measured NUM-03 calibration is restricted to the workload recorded in the [task evidence](../../work-items/NUM-03.md); other contexts without a matching profile remain INDETERMINATE. A budget-fit report never authorizes or starts execution by itself.

**If unsuccessful:** F-05; refine cost model or select a scientifically justified smaller experiment.

## NUM-03 — Implement the selected field backend

**Current state:** ACTIVE — isolated numerical kernels, the scaled coupled Hasegawa piston/stationary-sphere evaluator, run-level preflight adapter and immutable field bundle are recorded in [NUM-03](../../work-items/NUM-03.md) and the linked reviews. Under [DEC-007](../../decisions/DEC-007-p4-field-only-error-budget.md), P4 is field-only; no numerical tolerance has been adopted. The solver retains order cap 512 and domain `a<=r<d`. Exact-rational candidate bounds cover the mathematical order>512 tail at every angle and all accepted radii at each of the 300 P1.3 gap samples. A separate exact-`Fraction` implementation re-derives four checkpoints, and the 300-row sweep reruns byte-identically; this is same-agent evidence, not external review. The bounds do not cover arbitrary gaps between samples, arithmetic/reference uncertainty or physical-model discrepancy, and the broadest sampled gradient bound at 29.9 mm establishes no pass. New 300-digit direct Rayleigh-disk comparisons at fixed gaps 0.1, 10, 20 and 29.9 mm use the same 111-point grid at each gap. An independent composite-Simpson family approaches high-order Gauss–Legendre values as panels are refined, with late adjacent-level changes consistent with fourth-order behavior. Highest-Simpson versus Gauss–Legendre 512 normalized velocity/gradient differences range from `9.92e-8` at 29.9 mm to `3.93e-5` at 0.1 mm. These are finite-grid, conditional sensitivity results, not rigorous quadrature bounds or full-domain reference uncertainty. A candidate Simpson remainder route is documented, with exact-rational derivative majorants for source modes 0–7 at 0.1 mm only, with successive ratios increasing to about 102 by n=7; simple exponent regrouping does not tighten the bounds. Validated interval prototypes at modes 0, 6, 7 and 8 and H=0.1 mm tighten their one-cell derivative majorants about 2.2×, 174×, 304× and 380× using 128 u-subintervals; no mode n>=8 bounds, field propagation, or complete rounding budget exist. Existing comparisons and the bounded one-gap/one-point run remain scientifically INDETERMINATE; the order1600 attempt exceeded its 300 s cap. The [NUM-03 field-error protocol basis](../../research/NUM-03-field-error-protocol.md) records comparison metrics and why current evidence cannot justify a numeric threshold: P1.3 provides figure-derived force readings, not a field-accuracy requirement or measured field reference. Continue bounded error-source qualification; do not start broad NUM-04 until the protocol prerequisites are supported. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-02

**Steps**

1. Implement the smallest domain and boundary case from the decision, using validated scenario/result contracts.
2. Report solver residuals, iterations, discretization, boundary and precision metadata; propagate typed failure.
3. Compare an initial bounded pilot with the matched P3 reference before adding geometry features.

**Required artifacts:** Numerical backend; pilot config/manifests; typed solver diagnostics. Intermediate kernel verification is tracked separately and does not satisfy these deliverables.

**Acceptance / decision:** The pilot returns correctly normalized fields and explicit convergence/failure diagnostics; initial comparisons justify refinement work.

**If unsuccessful:** F-01/F-04/F-05; reduce to the matched analytical case.

## NUM-04 — Measure observable convergence across three levels

**Initial state:** BLOCKED until the benchmark-specific observables, sample set, reference uncertainty, acceptance/stopping rule and resource cap are frozen under NUM-03/DEC-007. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-03

**Steps**

1. Freeze the physical primary observable, sample locations, refinement sequence and acceptance budget.
2. Run at least three discretization levels; record all outcomes and raw error estimates.
3. Study interpolation/gradient error when needed by downstream force and diagnose nonmonotonic trends instead of forcing an order fit.

**Required artifacts:** B-07 convergence protocol, manifests/table and observable plots.

**Acceptance / decision:** The field and required derivatives meet the declared numerical budget with a defensible convergence interpretation.

**If unsuccessful:** F-04; isolate discretization, conditioning and sample error.

## NUM-05 — Bound boundary and domain contamination

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-04

**Steps**

1. Vary domain extent, absorbing-layer parameters or boundary discretization separately from interior refinement as applicable.
2. Check the chosen wall/impedance model against an independent simple solution or published numerical benchmark.
3. Quantify the effect on the same primary observable and identify where the selected backend lacks coverage.

**Required artifacts:** Boundary/domain sensitivity report and qualified operating subdomain.

**Acceptance / decision:** Boundary effects are below the allocated error budget or their unresolved contribution is explicitly gate-blocking.

**If unsuccessful:** D-04/F-03/F-04; choose appropriate boundaries or restrict a new domain.

## NUM-06 — Reconcile cost, precision and reproducibility

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-05

**Steps**

1. Measure runtime, peak memory, actual output volume and solver iteration count for completed/failed pilots.
2. Compare to preflight and update its documented safety envelope; profile before considering GPU or remote execution.
3. Check precision sensitivity and complete RUN-02 replay for a representative numerical case.

**Required artifacts:** Resource report; environment/precision record; updated preflight; reproduction evidence.

**Acceptance / decision:** The next planned run fits a supported resource envelope and scientific changes are not hidden in backend selection.

**If unsuccessful:** F-05/F-09; retain failure and adjust execution method, not the claim.

## NUM-07 — Close the field solver gate

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-06, RUN-02

**Steps**

1. Review B-07, boundary limits, resource prediction, replay and requirement mapping.
2. Publish command usage and the model/geometry capability table with explicit unsupported cases.
3. Record P4 PASS or remaining gate conditions, then permit force-model implementation in the reviewed field domain.

**Required artifacts:** P4 gate review; backend guide; field evidence bundle and updated board.

**Acceptance / decision:** Every required reference/convergence/resource/replay item is present and no hard MCLF failure is promoted.

**If unsuccessful:** F-04/F-09/F-11; continue only work independent of the missing gate.

## Phase exit review

One fast backend reproduces reference observables, required refinements and boundary checks pass, predicted resource use is reconciled with measurements, and RUN-02 replay works.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.


### Interval enclosure comparison at modes 0 and 6 — 2026-10-05

The same exact-rational interval implementation was evaluated at 128 equal `u`-subintervals for modes `n=0` and `n=6`, at the same fixed gap `H=0.1 mm`. For n=0, the interval M4 upper bound is `0.0622085092956504108006773269057`, compared with its existing global exact majorant `0.138000671955546614706827784474` (about 2.22× tighter); its N=8192 coefficient-only Simpson bound is `7.67392437195990728690559839484e-24 m^2`. For n=6, interval M4 is `0.882659194556436413064051348714`, compared with the exact global majorant `153.969263574786446877579636640` (about 174.44× tighter); the N=8192 coefficient-only bound is `1.08883173410405704624188355970e-22 m^2`. Both scripts check their upward Decimal displays, the exact Simpson factor and stdout summary; exact enclosures are no larger than the corresponding global exact majorants. A separate replay of each produced byte-identical metadata and summary. Mode-0 JSON/stdout SHA-256: `b917445888e62320b3fed21f94dad08dc54e79fdd7aafb09cc16d1cffa70e92b` / `c68d933513478bb06f2817c61fe81951ab77b7cf59069a156a106ed78839e39d`. Mode-6 JSON/stdout SHA-256: `b93bfc43372b7ce121609dbfd428e658249a8d181c50bbfce2b702f591705a23` / `b8ab3aee66ebce804665b04350d8f773848d2793bae98b632f273d231acf8d5d`.

Together with n=7 (128-cell interval M4 `2.59240346635350815654859326849`, about 303.56× tighter than its global exact majorant), these checks support continuing the bounded method investigation. They do not establish bounds for intervening/higher modes, other gaps, field observables, total error or physics. NUM-03 remains ACTIVE/INDETERMINATE; no threshold or gate changes. Next, test n=8 with an exact global comparator and assess interval width and cost; keep one-gap/source-coefficient scope.


### Mode-eight interval enclosure — 2026-10-05

The exact-rational global generator was extended to `n=8`, reproducing all existing exact M4 comparators for modes 0–7. At `H=0.1 mm`, its global triangle majorant is `4352.61045638364039762934462173`; the n8/n7 ratio is `5.53092521993348178041230216197`. A 128-cell interval enclosure gives `M4 <= 11.4563625202142231837086521713`, about 379.93× tighter than that same-mode global majorant. The N=8192 coefficient-only Simpson bound is `1.41323527204383510553377879307e-21 m^2`. Exact containment, upward decimal, Simpson-factor and stdout checks passed; the interval script replayed byte-identically. Mode-8 global JSON/stdout SHA-256 `b10ea3ce5a9ea2acc0cd108431b7fd0b0e09a9e259993d61cfa4b6ad6fac1206` / `22c8e15dd76997b600a59368e6fed1dcfcb15d53d058251c0c09fa472356d0c1`. Corrected interval attempt 03 JSON/stdout SHA-256 `777d4d585b738557571369cbd753bb5d1d3652fd14fa8da98a2681ee48a12a77` / `4b46a60a034ccd081471b263673109453e77ab2dd32d51c4dfe511e0035c2bad`. The setup failures (syntax error and wrong dependency filename, both before any accepted result) remain preserved in `NUM03-SIMPSON-INTERVAL-MODE8-SETUP-FAIL-20261005-01.txt`. The diagnostic used system CPython 3.13.5; it is separate from the ENV-1.0 solver qualification.

This is still only one source coefficient and one fixed gap. No modal range through 512, field propagation, other gap, total rounding/reference budget or physical observation is certified. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED; no threshold or gate change follows. Next, assess gap dependence by testing a bounded far-gap case with an exact same-mode comparator and checking whether the chosen `u` partition still gives useful interval widths.
