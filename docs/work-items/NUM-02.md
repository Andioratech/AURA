# NUM-02 — Air Series Resource Preflight

**State:** DONE — software estimator delivered; matched runtime calibration remains unavailable pending NUM-03 · **Prepared:** 2026-10-03 · **Phase:** P4 numerical field

## Question

Can the selected air-series request be rejected before solver workspace allocation when its predicted RAM, output disk, or calibrated wall time exceeds the scenario's declared caps?

## Inputs and predecessors

- NUM-01 [air solver contract](../research/air-field-solver-contract.md): stationary rigid sphere, Hasegawa piston/sphere series, complex128, ordered chunked observations.
- Scenario resource caps: RAM bytes, disk bytes, and wall-time seconds.
- Workload dimensions: harmonic truncation `N`, number of gaps, observation points per gap, and bounded point-chunk size.
- Runtime calibration bound to the exact solver model/version and ENV-1.0 profile. Without matching calibration, the report must remain INDETERMINATE and production execution must be refused.

## Predeclared estimator model

The selected equations have one order recurrence for the piston diffraction coefficients and one order sum per observation point for the incident-plus-scattered field. The contract therefore counts `N+1` orders for each gap's coefficient preparation and each point's field evaluation. It does not assume that the paper's infinite series has converged at any chosen `N`.

The implementation will stream one point chunk at a time and budgets six live complex and two real per-order vectors, one output chunk, and its JSON serialization workspace. The implementation must either match this live-array inventory or revise the estimator before allocating solver arrays. Peak RAM includes the already-loaded process high-water mark with headroom. Disk includes the complete requested result and per-chunk metadata. It compares the estimate against scenario caps and current Linux cgroup/host RAM and the available bytes on the planned output filesystem. All multiplications and additions use checked integer arithmetic; overflow is a named rejection.

Wall time is estimated from measured coefficient-preparation and field-evaluation seconds per harmonic order from the same solver version, exact clean Git revision, and ENV-1.0 environment digest. Apply the declared safety multiplier from the calibration record. Missing, stale, or mismatched calibration is INDETERMINATE; a plausible-looking default rate is prohibited. Calibration estimates are predictions, not hard real-time guarantees. A budget-fit report never authorizes or starts execution.

## Required artifacts and acceptance

- Pure `aura.preflight` request validation and resource estimator.
- `aura preflight <scenario> --workload <request> [--calibration <record>] [--output-dir <path>] [--json]` with no solver import or field allocation.
- Reports containing dimensions, each RAM/disk/time estimate, declared caps, headroom, calibration identity, basis, status, and a named rejection reason.
- Tests for exact small formulas, dimension overflow, scenario and current-resource limits, each individual over-budget case, missing/stale calibration, and proof that the CLI does not import or start a field solver.

Acceptance requires every budget-fit report to fit the declared and currently available RAM/disk caps and to use calibration bound to the exact source/environment; deliberately oversized cases fail before allocation. Until the numerical solver exists and a calibration can be measured, wall-time status remains INDETERMINATE. This task does not produce a pressure field or demonstrate series stability, convergence, field accuracy, force, or experimental validation.

## Delivered result — 2026-10-03

Implemented `src/aura/preflight.py` and the `aura preflight` CLI. The estimator validates strict workload/calibration records, uses checked integer dimensions and memory/disk arithmetic, bounds the Hasegawa order workspace and one serialized point chunk, compares with scenario caps and current Linux RAM/free disk, and estimates wall time only for a matching calibration file, clean source revision, and ENV-1.0 digest. It returns `REJECTED`, `INDETERMINATE`, or `BUDGETS_WITHIN_CAPS`; all reports set `execution_authorized` false. CLI JSON is limited to 1 MiB and rejects duplicate keys and non-finite constants. Runtime-product overflow is a typed rejection.

Targeted verification: Ruff passed; `pytest -q tests/test_preflight.py tests/test_cli.py` passed 110 tests. Full repository Quality passed with the hash-locked ENV-1.0 install, editable install, `pip check`, environment verifier, Ruff, required-document checks, and 1,419 tests. These are software contract tests with an injected synthetic calibration fixture; no production calibration or field computation was produced. The CLI returns INDETERMINATE without a real matching calibration, as required. NUM-02 is complete as a pre-allocation estimator implementation; any actual NUM-03 diagnostic pilot still requires separately measured runtime evidence and must follow the phase checkpoint. See [NUM-02 review](../reviews/NUM-02-resource-preflight.md).

## Stop and recovery rules

If the source-derived workload count or live-array inventory cannot bound the selected implementation, stop before allocation and revise the numerical algorithm/preflight together. Preserve every failed estimate. If calibrated runtime uncertainty cannot be bounded, permit only a separately identified, explicitly time-limited diagnostic pilot after owner notice; do not label it production-ready or infer performance from it.
