# Next Main Task — Calibrate the NUM-03 Run Path

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Published revision:** `f8302cb` (GitHub Quality [37184239104](https://github.com/Andioratech/AURA/actions/runs/37184239104) passed)

## Current implementation under review

Published commit `f8302cb` adds a versioned Scenario 1.1 piston displacement representation while keeping Scenario 1.0 records unchanged; a Hasegawa stationary piston/sphere adapter to `aura run`; exact-source/ENV-1.0 NUM-02 calibration gating; one ordered field chunk of at most 256 samples; immutable input, calibration, preflight, provenance and output hashes; and read-only bundle verification. GitHub Quality passed. Full local Quality passed: locked ENV-1.0 install, editable install, `pip check`, environment verification, Ruff, required-document checks, `git diff --check` and 1,667 tests.

The adapter supports one gap per run and one complete bounded chunk per request. It keeps the solver's 0–512 order cap and declared shell `a <= r < d`. The current source-factor implementation uses a recurrence rather than Gauss integration; NUM-02 retains the quadrature workspace as a conservative allowance and calibration dimension. It is not a solver accuracy parameter. No production calibration or air field run exists.

## Immediate next work

1. Measure Hasegawa coefficient-preparation and field-evaluation seconds per harmonic order on this exact clean source revision and ENV-1.0. Bind the calibration file to commit `f8302cb`, environment digest, workload Bessel argument and the declared quadrature preflight dimension. Keep raw measurement data, timing method, repeated-run distribution and calibration artifact digest with the run record.
2. Run one bounded, declared diagnostic request only if its exact NUM-02 report fits the frozen scenario caps. The run's verdict stays INDETERMINATE and demonstrates software execution only.
3. Review a target-specific numerical tolerance for pressure, particle velocity and pressure gradient before full-domain convergence work or any P4 claim. Keep the order512 cap and declared domain unchanged until that review.

## Scientific work still open

The order512 versus direct order1200 overlap changes on the sampled outer shell reach `1.14e-6` in velocity/pressure-gradient norm at the 30 mm gap. Extending the separate sum to order1600 reduces the observed finite-sum difference but gives no tail bound. The matched-order direct/public overlaps are near roundoff across 444 discrete points, not independent physical validation. Continuous shell coverage, a predeclared tolerance for pressure/velocity/gradient, and complete resource and convergence evidence remain open. Do not change the order cap or claim P4 acceptance until these are reviewed. Keep the NUM-01 BEM/high-order-FD fallback available if the series cannot meet a justified error/resource bound.

No force, dynamics, acceleration, control, microgravity or gravity-equivalence work belongs to NUM-03. Preserve failed attempts and all limits described in [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and the [P4 phase plan](../planning/phases/P04-numerical-field.md).
