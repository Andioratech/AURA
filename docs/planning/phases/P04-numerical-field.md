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


### Mode-eight far-gap interval enclosure — 2026-10-05

To check gap dependence, the mode-8 exact global majorant and interval enclosure were repeated at `H=29.9 mm` (`D=54.9 mm`). The phase interval is reduced by `8π`, appropriate to this configuration. The exact global M4 majorant is `4.01545929178745133730198730836`; the 128-cell interval M4 bound is `0.00838114275077458596704327728133`, about 479.11× tighter. The N=8192 coefficient-only Simpson bound is `1.03388196162001837572773240103e-24 m^2`. Exact same-gap containment, upward rounding, phase/configuration metadata, Simpson factor and stdout checks pass. The corrected interval script replays byte-identically in both system CPython 3.13.5 and project ENV-1.0 / CPython 3.12.14. Global-bound JSON/stdout SHA-256 `483feaa206e6a9b4bf9ad3e0d4f80eed03be1c7e3fda227047eaab8254271708` / `9f743a67482979ad977e81feb7b77225d6c67300b24a671d5b4e41b5b1c7ba54`; interval JSON/stdout SHA-256 `dec67be2e4a35fa164823ecdf064dd1d1e8192edb22af59e2c3f6f2020781b1e` / `41696900251874b66422bcdd84e6c64d19f3d6caa05f1cae62aedb83c6b36610`. The mismatched-metadata interrupted attempt 01 is preserved in `NUM03-SIMPSON-INTERVAL-MODE8-FAR-GAP-SETUP-FAIL-20261005-01.txt`; corrected attempt 02 is the only accepted result.

This is one more diagnostic point at one mode and does not establish behavior between gaps or across modes, propagate to field observables, close arithmetic/reference uncertainty or validate an experiment. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, repeat this bounded method at an intermediate declared gap (10 mm) with a freshly computed same-gap comparator; do not interpolate across the 300-gap program from these points.


### Mode-eight intermediate-gap interval enclosure — 2026-10-05

At `H=10 mm` (`D=35 mm`), mode-8 global M4 is `175.126150564895092633901624593`. With 128 equal `u` cells and phase reduced by `6π`, the interval M4 bound is `0.334296573356726281404978833314`, about 523.86× tighter than the exact same-gap global majorant. The N=8192 coefficient-only Simpson bound is `4.12381947548811302396529301995e-23 m^2`. Exact mode/gap/phase metadata, containment, outward decimals, Simpson factor and JSON/stdout checks pass. The corrected attempt replays byte-identically using both system CPython 3.13.5 and project CPython 3.12.14. Global JSON/stdout SHA-256 `61fef042b51ec3f90230cca58462f0df0bf7ea3be2318f4153535d06b80a3cac` / `94292c0de88a11816718f5f46d783e1b36676e0895e7579db433d0ac57dcacba`; interval JSON/stdout SHA-256 `10fb3ad3bba800906053b3f610d931f1a5a9d665d7061e444bd82c58e7746a13` / `8efde8bd2d3e6f2f72ebb73c26758794a578506fe8e52db073f499332eee7b50`.

Across the three tested gaps, the n=8 interval certificate is substantially tighter than its same-gap global triangle majorant. These are only three conditional coefficient bounds; this does not establish the 300-gap range, modes 0–512, field-error propagation, complete numerical uncertainty or physical validity. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, evaluate the remaining selected checkpoint `H=20 mm` with an independently constructed same-gap majorant before discussing any wider campaign.


### Mode-eight interval enclosure at 20 mm — 2026-10-05

At `H=20 mm` (`D=45 mm`), the exact same-gap global M4 majorant is `19.7577657519269811574998952868`. With 128 equal `u` cells and phase reduced by `6π`, the interval bound is `0.0340021711315774712400633620069`, about 581.07× tighter. The N=8192 coefficient-only Simpson bound is `4.19444369750245796465838098405e-24 m^2`. Exact configuration, phase, containment, upward-rounding, Simpson-factor and JSON/stdout checks pass. Replay in project CPython 3.12.14 is byte-identical to the original system CPython 3.13.5 run. Global JSON/stdout SHA-256 `7c7c998731e0c94a2e20284ee5b02ac063c597c351a30503f29ecc94e37c690b` / `0a3e60686c9c2c13966f93ee3d32ff2437eb6ea656c798f4cdc4328871bc6cc4`; interval JSON/stdout SHA-256 `efbb64a51ed36b37ac430eae5bd6332cb6ab3cb3e883e5efa7404e05a1e44f25` / `931b1cfd04ae3d7f7faac8d7563a77ea8a5c2a2f1a7883bc8d728a1259c64f48`.

For mode 8 at the four selected gaps `0.1, 10, 20, 29.9 mm`, the 128-cell intervals are all substantially tighter than the corresponding exact same-gap global triangle majorants. This is not uniform coverage between those gaps, across modes, or over the full accepted field domain. It remains a source-coefficient quadrature estimate, not a P4 pass or physical validation. NUM-03 stays ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next assess the computational cost and interval widths needed to extend mode 8 over all 300 declared gap samples; do not infer full-domain or all-mode validity from the four selected checkpoints.
# NUM-03 continuation checkpoint — 2026-10-05

The Simpson quadrature-remainder investigation now has exact-rational global derivative majorants for source modes 0–7 at the 0.1 mm gap, plus a 128-cell outward-rounded fixed-point interval enclosure for mode 8 at all 300 discrete P1.3 gaps from 0.1 to 30.0 mm in 0.1 mm steps. An independent exact-rational same-gap comparator contains all 300 mode-8 bounds. Their interval M4 bounds are 166.08–308.32 times tighter than the comparator; the N=8192 coefficient-only remainder bounds range from `2.0443e-24` to `2.5272e-21 m^2`. These are coefficient-integral remainder bounds only. No arbitrary-gap coverage, all-mode coverage, propagation into field observables, total arithmetic/reference uncertainty, or physical validation follows. The interval route is wider than the earlier exact-rational checkpoint values and that difference is recorded.

NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 remains BLOCKED. No tolerance or gate changes. Next, check mode 9 at the minimum gap against a fresh exact global comparator, then assess whether extending the interval route to additional modes is worthwhile before any field propagation. See [NUM-03](../../work-items/NUM-03.md), the [field-error protocol](../../research/NUM-03-field-error-protocol.md), and its [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 mode-by-mode remainder continuation — 2026-10-05

Outward-rounded fixed-point interval enclosures now cover the mode-8, mode-9, mode-10, and mode-11 source-coefficient Simpson remainders at each of the 300 P1.3 gap samples. Exact-rational, same-gap global derivative majorants independently contain every result. Their tightening factors over the global majorants are 166.08–308.32× (n=8), 216.56–493.41× (n=9), 211.00–746.12× (n=10), and 201.48–887.15× (n=11). Five-point cross-version replays and exact formula/outward-rounding audits pass. The largest N=8192 coefficient-only remainder at the minimum gap increases from `2.5272e-21 m^2` to `6.8089e-19 m^2` over n=8–11. This does not establish an all-mode sum, gap continuity, field-observable error or physical validity; the method's higher-order usefulness remains open. NUM-03 stays ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, evaluate n=12 at four selected gaps, then decide whether to continue the campaign. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=12 continuation — 2026-10-05

The n=12 source-coefficient Simpson remainder is now enclosed over all 300 sampled gaps and contained by exact-rational same-gap global derivative majorants. The global-to-interval tightening is 192.45–1003.87×. Its N=8192 coefficient-only remainder bound spans `5.1395e-18 m^2` at 0.1 mm to `1.0827e-22 m^2` at 30.0 mm. Exact formula, outward rounding, gap sequence, containment and five-point cross-version replay checks passed. The preserved first attempt lacked an inverse-k cache entry at `k^-13`; the corrected range includes it. This remains coefficient-only for n=12 and does not establish an all-mode sum or field accuracy. NUM-03 stays ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next screen n=13 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=13 continuation — 2026-10-05

Mode 13 has an outward-rounded coefficient Simpson-remainder enclosure at all 300 discrete P1.3 gaps. Exact-rational same-gap global bounds contain every interval result; their ratio is 184.58–1004.21×. At N=8192 the coefficient-only remainder bound ranges from `4.0807e-17 m^2` at 0.1 mm to `4.8541e-22 m^2` at 30.0 mm. Exact factor/gap/rounding audits and a five-gap cross-version replay pass. Two failed comparator setups were preserved before the corrected script validated all rows. This remains one coefficient and one quadrature remainder term, with no all-mode or field-observable result. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=14 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=14 continuation — 2026-10-05

Mode 14 has a checked coefficient Simpson-remainder enclosure at all 300 discrete P1.3 gaps. Exact-rational same-gap global comparators contain every interval result; tightening factors span 177.95–986.85×. The N=8192 coefficient-only upper bound is `3.3976e-16 m^2` at 0.1 mm and `2.2807e-21 m^2` at 30.0 mm. Exact formula, gap sequence, outward display and five-case cross-version replay checks passed. No field sum, total error or physical result follows. NUM-03 remains ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next, screen n=15 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=15 continuation — 2026-10-05

Mode 15 has an outward-rounded coefficient Simpson-remainder enclosure at all 300 discrete P1.3 gaps. Its exact-rational same-gap global comparators contain every result, with tightening factors from 172.44× to 955.62×. The N=8192 coefficient-only remainder ranges from `2.9601e-15 m^2` (0.1 mm) to `1.1202e-20 m^2` (30.0 mm). Exact gap/factor/display audits and five-point cross-version replay passed. This does not provide an all-mode or field-observable error bound. NUM-03 remains ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next, screen mode 16 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=16 continuation — 2026-10-05

Mode 16's source-coefficient Simpson remainder is enclosed at all 300 P1.3 gaps. Exact global same-gap containment, rational gap sequence, N=8192 factor, outward displays, and cross-version replay passed. The global/interval ratio is 167.90–924.50×; the coefficient-only remainder spans `2.6938e-14 m^2` at 0.1 mm to `5.6807e-20 m^2` at 30 mm. The run took about 10 minutes on one core and 17 MB RSS, a diagnostic workload measure only. No total field error or physical validation follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=17 at four gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=17 continuation — 2026-10-05

Mode 17's coefficient remainder is enclosed at all 300 discrete P1.3 gaps and contained by exact-rational same-gap global bounds. Tightening is 164.18–894.95×; the N=8192 coefficient-only remainder ranges from `2.5566e-13 m^2` at 0.1 mm to `2.9710e-19 m^2` at 30 mm. Exact sequence, formula, upward display and cross-version replay audits passed. The run took about 10.5 minutes on one core with 17–18 MB RSS. This remains an isolated coefficient term and supports no field-accuracy claim. NUM-03 ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next, screen n=18 at four gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).
