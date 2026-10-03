# NUM-02 — Air-Series Resource Preflight Review

**Date:** 2026-10-03 · **Scope:** Software-contract review only · **Status:** PASS for estimator implementation; production runtime calibration NOT AVAILABLE

## Result

NUM-02 delivers a pure resource estimator and `aura preflight` for `AIR-SERIES-WORKLOAD-1.0`. The CLI validates a versioned scenario, explicit gap/point/order dimensions and a bounded point-chunk size; it checks calculated RAM and output-disk requirements against scenario caps and current Linux availability. Runtime is calculated only from coefficient-preparation and per-point field rates in a calibration record bound to the requested solver model/version, exact clean source revision and ENV-1.0 digest. A missing or mismatched calibration yields INDETERMINATE. A matched estimate within caps yields `BUDGETS_WITHIN_CAPS`, which means only that its estimates fit; every report has `execution_authorized: false`.

The estimator uses the NUM-01 single-order recurrence count, six complex and two real live order vectors, one retained output chunk and its JSON workspace, platform-measured Python object sizes, a 2× incremental-memory headroom factor, and 2× process high-water RSS. Disk counts every requested point, per-chunk metadata and a fixed index allowance. Workload products/sums and runtime products reject overflow. CLI workload/calibration JSON is bounded to 1 MiB and rejects duplicate object keys and non-finite JSON constants. No solver module is imported or called.

## Verification

- Ruff passed on the implementation and focused test files.
- `pytest -q tests/test_preflight.py tests/test_cli.py`: 110 passed.
- Full repository Quality: locked ENV-1.0 dependency install, editable install, `pip check`, environment verifier, Ruff, required-document checks, and 1,419 tests passed.
- Tests cover dimension/workspace formulas, chunk accounting, each declared/current RAM and disk rejection path, missing and stale calibration, solver/version/digest mismatch, invalid and oversized JSON, arithmetic overflow, and absence of numerical solver imports.
- The valid-calibration CLI fixture injects an explicit test environment and synthetic rates to test contract binding. It is not a production timing measurement and is not evidence for a real solver's cost.

## Boundary and next dependency

There is no NUM-03 backend to time, so no production calibration exists and wall-time readiness remains INDETERMINATE. The estimator cannot establish convergence, series stability, pressure/velocity/gradient accuracy, force, motion or experimental validity. A future bounded diagnostic calibration must have its own immutable identity and explicit wall-time cap; it cannot be represented as a production budget PASS. NUM-03 solver/core construction is a separate milestone and must receive the requested plain-language checkpoint before implementation.
