# 03 — Complete Software Construction Map

## Implementation rule

Paths below describe the construction target; consult the work board and task records for actual availability. FND-02 implements the schema boundary; FND-03 supplies safe arithmetic/conversions; FND-04 implements L0 audits, reports and typed gate failures; FND-05 verifies foundation composition; FND-06 exposes configuration checks through the CLI; FND-07 supplies canonical identity and bounded file-integrity helpers. Scientific solvers remain unimplemented. Preserve the working CLI and SI helpers. Build modules in the task order; optional branches are implemented only when the regime/evidence requires them. No notebook is the sole implementation of a scientific result.

Core remains CPU-first. FND-02 records the [initial schema dependency review](../research/schema-contract.md); FND-08 completes environment locking and compatibility review. NumPy/SciPy and array-storage libraries remain candidates. A new backend needs a documented need and decision. Keep optional expensive solvers behind extras and narrow adapters.

## Planned package inventory

| Path under `src/aura/` | Responsibility and interface | Owning tasks | Required independent/negative checks |
|---|---|---|---|
| `units.py` (existing) | SI calculations; explicit RMS/peak conversion boundary; return scalar values with documented domain | FND-01, FND-03 | Known values; nonfinite/sign/range; conversion round trip |
| `schema/quantities.py` | Parse external value/unit pairs; convert once to canonical SI; reject unsupported dimensions | FND-02, FND-03 | Unit mismatch, unknown unit, overflow, bool-as-number policy |
| `schema/models.py` | Medium, Body, SourceArray, Scenario, SolverSpec, Experiment, RunManifest; version and cross-field validation | FND-02 | Required fields; vectors/shapes; radius/diameter; incomplete inputs |
| `schema/io.py` | Strict JSON/YAML input and display serialization; prohibit executable YAML tags | FND-02 | Duplicate keys, nonfinite values, unknown fields |
| `schema/canonical.py` (implemented) | AURA-C14N-1 exact canonical bytes, separate from display serialization | FND-07 | Golden bytes, numeric/Unicode rules, caps and key-order equivalence |
| `schema/identity.py` (implemented) | Complete/projection digests and typed manifest/config/optional experiment link checks | FND-07 | Changed inputs/metadata, full versus projected digest, mismatched records |
| `artifacts.py` (implemented) | Bounded read-only SHA-256 over explicitly supplied local regular files | FND-07 | Known digests, tampering, caps, special files and ordinary read-time changes |
| `errors.py` | Input, numeric-domain, MCLF invalidation, incomplete-evidence and content-integrity errors implemented; solver resource/convergence errors remain planned | FND-02, FND-03, FND-04, FND-07 | Stable field/code diagnostics; CLI propagation; no false success |
| `mclf/rules.py` | Stable R-001…R-010 L0 registry, predicates, assumptions and tolerance references | FND-04 | Valid, invalid, boundary and uncovered regime cases |
| `mclf/evaluate.py` | Independent pre/post audit and per-rule verdict report | FND-04, FOR-07, ADV-06 | Severity precedence; no solver success override |
| `mclf/reports.py` (implemented) | Immutable detailed audit envelope, compatible core record, human text and explicit acceptance gate | FND-04 | Missing rules, inherited warnings, serialization, typed rejection |
| `mclf/balances.py` | Model-specific energy/momentum/symmetry checks, with defined control surface and terms | ANA-06, FOR-07 | Incomplete control volume; conditional-bound misuse |
| `mclf/regimes.py` | ka, viscosity/thermal scales, wall distance, amplitude and dynamics-domain evidence | FOR-01, MOT-01 | Hard violation vs insufficient evidence; no universal threshold |
| `preflight.py` | Estimate allocation, temporary arrays, iterations/output volume and caps before compute | NUM-02 | Deliberate budget rejection; actual/predicted comparison |
| `fields/types.py` | FieldResult, samples, coordinates, phasor convention, units and diagnostics | ANA-01 | Shape/axis/convention mismatch |
| `fields/analytic.py` | Closed-form progressive/standing/interference cases in frozen regimes | ANA-02…ANA-05 | Hand derivations, symmetry and limiting cases |
| `fields/numerical.py` | One selected fast propagation/discretization method with declared boundaries | NUM-01…NUM-06 | Three refinements; boundary/domain effects; manufactured/reference cases |
| `fields/transfer.py` | Source response basis for feasible field/force allocation; cache identity includes all physics | CTL-02 | Direct recomputation vs cached result; stale cache rejection |
| `forces/types.py` | ForceResult: radiation/other contributions, torque, frame, regime and provenance | FOR-02 | Missing contribution labels and invalid frame |
| `forces/particle.py` | Selected small-particle radiation model only | FOR-01…FOR-04 | Independent derivative/limit checks; forbidden large-body input |
| `forces/viscous.py` | Viscous correction branch when justified; explicit coefficient version | FOR-06 | Limit recovery and coefficient reference |
| `forces/thermoviscous.py` | Conditional refinement if omitted thermal effects affect the question | FOR-06 | Source equations, model overlap, material branch selection |
| `fluid/streaming.py` | Qualified analytical/reference streaming field first; numerical branch only if needed | FOR-06, MOT-02 | Wall/geometry applicability and benchmark comparison |
| `dynamics/loads.py` | Sum declared radiation, drag, gravity/buoyancy and selected disturbances without double counting | MOT-01, MOT-02 | Per-term force ledger; gravity-zero consistency |
| `dynamics/integrate.py` | Resolved inertial or justified reduced trajectory integration; collision/domain events | MOT-03, MOT-04 | Analytic force/drag relaxation; step refinement; event accuracy |
| `dynamics/rotation.py` | Rigid-body orientation/angular velocity with justified torque model | MOT-05 | Zero torque, constant torque, norm/invariant checks |
| `dynamics/stochastic.py` | Conditional Brownian/noise model with stated discretization and seed stream | MOT-07, ADV-03 | Ensemble moments, step dependence, replay; no noise derivative acceleration |
| `control/targets.py` | Target vector/time window, metric/filter contract and constraints | CTL-01 | Zero target; infeasible trajectory/workspace; window sensitivity |
| `control/reachability.py` | Necessary-condition tests and bounded force-set estimates with certificate type | CTL-02, ADV-01 | Known feasible/infeasible toys; no grid-search impossibility label |
| `control/allocation.py` | Bounded source amplitude/phase allocation with realized action report | CTL-03 | Saturation, phase wrapping, feasibility residual and multistart limits |
| `control/baseline.py` | One deterministic controller with actuator limits/anti-windup where applicable | CTL-04 | Open-loop baseline, saturation, delay and holdout |
| `sensors/virtual.py` | Exact-state reference then sampled noisy/delayed observation | CTL-05 | Units, latency, stale/dropout timestamps |
| `estimation/baseline.py` | Minimal estimator matched to observation; no oracle leakage | CTL-05 | Independent synthetic truth; held-out noise |
| `runs/manifest.py` (planned) | Durable run metadata/storage using existing RunManifest schema and FND-07 identity primitives; source/environment/output evidence binding | RUN-01 | Hash mismatch, missing identity and immutable output checks |
| `runs/execute.py` | Validate → preflight → run → checks → atomic finalize; keep failures | RUN-01, RUN-02 | Exception/interrupt/resume policy; never overwrite |
| `runs/reproduce.py` | Verify inputs/environment and replay a stored experiment into a new run | RUN-02, IND-03 | Hash mismatch, unavailable inputs, backend variation |
| `analysis/metrics.py` | D03 metrics with units, applicability, time weights and uncertainty | ANA-07, MOT-08, CTL-06 | Hand time series; zero denominator; missing window |
| `analysis/compare.py` | Reference mapping, residuals and uncertainty-aware comparison status | FOR-05, IND-02 | Mismatched domains; missing uncertainty; held-out calibration |
| `analysis/sweeps.py` | Predeclared finite design, budget accounting, seed mapping and failure denominator | ADV-02, ADV-03 | No omitted failures; deterministic scheduling |
| `analysis/limits.py` | Necessary-condition calculations and scoped certificate records | ADV-01, ADV-05 | Independent derivation; uncertainty direction of bounds |
| `reporting/evidence.py` | Markdown/JSON reports and bundle manifest with claim restrictions | RUN-02, IND-05 | INVALIDATED promotion refusal; incomplete evidence labels |
| `reporting/plots.py` | Field, trajectory, residual and limits plots with units/domain/error bars | ANA-07, MOT-08, ADV-06 | Data/plot consistency and source labels |
| `cli.py` (existing) | Implemented `status` and `validate-config` with stable exit codes and JSON output; remaining commands below are planned | FND-06, RUN-01, RUN-02 | CLI integration, failed checks return nonzero |

`RUN-01` and `RUN-02` are cross-cutting cards in [08](08-reproducibility-and-ci.md); finish the minimal run recorder before P3 evidence runs and expand replay/reporting before P4 closes.

## Interface contracts to freeze before implementation

1. Implemented FND-02 boundary: `schema.load_document(path) -> ValidatedRecord`, returning `Scenario` for a scenario envelope; `schema.validate_document(data)` handles a dictionary. Returns explicit canonical SI and provenance without solver allocation. The earlier proposed `load_scenario` name is superseded by this documented generic boundary.
2. `evaluate_preflight(scenario, resources) -> PreflightReport`: dimensions, estimates, budgets, decision and reason codes.
3. `solve_field(scenario, solver_context) -> FieldResult`: typed pressure/velocity samples, gradients if supported, coordinates, convention, solver/boundary diagnostics and output references.
4. `compute_force(field, body, context) -> ForceResult`: required field components and regime metadata; no silent interpolation/extrapolation outside samples.
5. `advance(state, loads, time_spec) -> TrajectoryResult`: time grid, state, per-term loads, acceleration definition and events; torque support may be explicitly unavailable until MOT-05.
6. `control(observation, target, constraints) -> Actuation`: desired and realized command, limit activity, solver/feasibility status.
7. `audit(evidence) -> MclfReport`: independent checks over recorded inputs/results; checker must not simply call the function being checked.
8. `execute(experiment) -> RunManifest`: final status plus durable artifacts; failed runs retain a manifest as far as storage permits.
9. `compare(run, reference, protocol) -> ComparisonReport`: mapping, error/uncertainty and PASS/FAIL/INDETERMINATE for that comparison only.

Names are proposed interface targets. Any renamed path must update this map and its task/test mapping in the same change.

## CLI construction order and availability

| Command contract | Input → output | First gate |
|---|---|---|
| `aura status` | Existing scaffold status → capability inventory | Implemented; updated with FND-06 |
| `aura validate-config <path> [--json]` | Versioned scenario → validation/MCLF report | Implemented FND-06; [CLI-1.0](../cli-usage.md); current valid fixture exits 3 for missing model coverage |
| `aura preflight <path>` | Valid scenario + explicit resource caps → allocation estimate | P4, basic form in RUN-01 |
| `aura run <experiment>` | Frozen experiment → immutable run directory | P3 minimal; P4 production lifecycle |
| `aura check <run>` | Saved artifacts → fresh independent audit | P3/P4 |
| `aura compare <run> <reference> --protocol <path>` | Two evidence records → qualified comparison | P5 |
| `aura reproduce <run>` | Source/env/hash record → new run and comparison | P4 |
| `aura sweep <design>` | Frozen bounded design → run index including failures | P8 |
| `aura report <run-or-study>` | Evidence index → Markdown/plots/bundle | P4/P8 |

Until a command is implemented and documented by its owning card, use the existing source interface and record the exact invocation; do not tell users these planned commands already run.

## Files beyond the package

- `experiments/<experiment-id>/`: frozen design, small configs and reference identities; no generated large fields.
- `tests/unit/`, `tests/integration/`, `tests/benchmarks/`: planned organization; move existing tests only when useful and preserve behavior.
- `tests/fixtures/`: compact manufactured/reference inputs and independently derived expected values with provenance.
- `docs/research/`, `docs/registers/`, `docs/work-items/`, `docs/reviews/`: evidence and decisions created when cards execute.
- `results/<experiment-id>/<run-id>/`: generated artifacts, excluded from Git per D07.
- `data/raw/` and durable external storage: licensed measurements and raw fields with hashes/access/retention records.

## Scope of the initial usable simulator

CLI plus documented configurations, pressure/velocity field plots, per-force and trajectory plots, comparison reports and the operating-limit map are required. A web application, animation engine, cloud service and AI controller are optional later product work. They do not resolve the scientific gates and are excluded from this construction sequence.

## Planned support for greater masses and larger objects

The initial particle implementation is one model behind the common `Body`, field, force and dynamics interfaces. FND-02 preserves explicit geometry/material/mass/inertia metadata and rejects unsupported schema geometries; it does not make every body an implicit point particle. It accepts declared model metadata without granting execution capability. FND-04 and subsequent model-dispatch tasks must reject unsupported body/model combinations before computation; no dispatch exists at FND-02.

SC-02–SC-03 in [11](11-scale-progression.md) select and verify the required later implementation: a geometry adapter, an appropriate scattering/body-field backend, force/torque evaluation and any loading diagnostics required by the candidate claim. Proposed locations are `geometry/`, `fields/scattering.py` and `forces/body.py`; these are planned, unimplemented components. Select the actual method and numerical library only after source review and resource preflight. Reuse the existing run/audit/reporting infrastructure while repeating the applicable model and evidence gates.
