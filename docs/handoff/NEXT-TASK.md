# Next Main Task — Establish a Tolerance Basis for NUM-03

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Published revision:** `30f4c21` (GitHub Quality [37184594681](https://github.com/Andioratech/AURA/actions/runs/37184594681) passed)

## Current implementation under review

Published commit `f8302cb` adds a versioned Scenario 1.1 piston displacement representation while keeping Scenario 1.0 records unchanged; a Hasegawa stationary piston/sphere adapter to `aura run`; exact-source/ENV-1.0 NUM-02 calibration gating; one ordered field chunk of at most 256 samples; immutable input, calibration, preflight, provenance and output hashes; and read-only bundle verification. GitHub Quality passed. Full local Quality passed: locked ENV-1.0 install, editable install, `pip check`, environment verification, Ruff, required-document checks, `git diff --check` and 1,667 tests.

The adapter supports one gap per run and one complete bounded chunk per request. It keeps the solver's 0–512 order cap and declared shell `a <= r < d`. The current source-factor implementation uses a recurrence rather than Gauss integration; NUM-02 retains the quadrature workspace as a conservative allowance and calibration dimension. It is not a solver accuracy parameter.

On clean revision `f8302cb` and ENV-1.0, a 48-sample timing record produced a calibration for one gap, one point, quadrature order 256, maximum Bessel argument 12.378996, and order up to 512. The profile uses maximum observed rates and a safety multiplier of 3.0. One bounded order-512/one-point diagnostic fit the NUM-02 caps, completed, and passed `aura check` integrity verification; its science verdict remains INDETERMINATE. Its local evidence pack is under ignored `results/num03-runtime-calibration/f8302cbf39cb06105c7602e946d66bdd2a0a9f33/`; artifact-index SHA-256: `b4b75b1b227b22fe0ef2fe0b5a0d6291c9119df77025c39237948a2daf5c630c`.

## Immediate next work

1. Establish a source-grounded basis for numerical tolerances on pressure, particle velocity and pressure gradient in the declared air field domain. Keep numerical consistency targets distinct from measurement uncertainty and downstream force requirements; no threshold has been frozen.
2. With a reviewed tolerance basis, design complete-domain convergence and boundary-contamination checks within the existing order-512 cap and resource limits. The current exact-context runtime profile is not evidence that larger workloads fit.

## Scientific work still open

The order-512 versus direct order-1200 overlap changes on the sampled outer shell reach `1.14e-6` in velocity/pressure-gradient norm at the 30 mm gap. Extending the separate sum to order 1600 reduces the observed finite-sum difference but gives no tail bound. The matched-order direct/public overlaps are near roundoff across 444 discrete points, not independent physical validation. Continuous shell coverage, a predeclared tolerance for pressure/velocity/gradient, and complete resource and convergence evidence remain open. Do not change the order cap or claim P4 acceptance until these are reviewed. Keep the NUM-01 BEM/high-order-FD fallback available if the series cannot meet a justified error/resource bound.

No force, dynamics, acceleration, control, microgravity or gravity-equivalence work belongs to NUM-03. Preserve failed attempts and all limits described in [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and the [P4 phase plan](../planning/phases/P04-numerical-field.md).
