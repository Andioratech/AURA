# Next Main Task — Characterize the NUM-03 Reference Error

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Solver revision:** `f8302cb` (GitHub Quality [37184239104](https://github.com/Andioratech/AURA/actions/runs/37184239104) passed)

## Current implementation under review

Published commit `f8302cb` adds a versioned Scenario 1.1 piston displacement representation while keeping Scenario 1.0 records unchanged; a Hasegawa stationary piston/sphere adapter to `aura run`; exact-source/ENV-1.0 NUM-02 calibration gating; one ordered field chunk of at most 256 samples; immutable input, calibration, preflight, provenance and output hashes; and read-only bundle verification. GitHub Quality passed. Full local Quality passed: locked ENV-1.0 install, editable install, `pip check`, environment verification, Ruff, required-document checks, `git diff --check` and 1,667 tests.

The adapter supports one gap per run and one complete bounded chunk per request. It keeps the solver's 0–512 order cap and declared shell `a <= r < d`. The current source-factor implementation uses a recurrence rather than Gauss integration; NUM-02 retains the quadrature workspace as a conservative allowance and calibration dimension. It is not a solver accuracy parameter.

On clean revision `f8302cb` and ENV-1.0, a 48-sample timing record produced a calibration for one gap, one point, quadrature order 256, maximum Bessel argument 12.378996, and order up to 512. The profile uses maximum observed rates and a safety multiplier of 3.0. One bounded order-512/one-point diagnostic fit the NUM-02 caps, completed, and passed `aura check` integrity verification; its science verdict remains INDETERMINATE. Its local evidence pack is under ignored `results/num03-runtime-calibration/f8302cbf39cb06105c7602e946d66bdd2a0a9f33/`; artifact-index SHA-256: `b4b75b1b227b22fe0ef2fe0b5a0d6291c9119df77025c39237948a2daf5c630c`.

## Owner decision recorded

The owner selected a field-only P4 numerical budget, with force/acceleration accuracy handled later. [DEC-007](../decisions/DEC-007-p4-field-only-error-budget.md) records this direction. No numerical threshold was selected, and no physical assumptions changed.

The first bounded reference sensitivity check is recorded in the [NUM-03 coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md). At the 30 mm outer shell and order 512, P300 versus P600 arithmetic and radial Gauss-Legendre rules 128/256/512 produce extremely small paired differences across 37 angles, while the order-512 versus order-1200 finite-sum change reaches `1.14e-6` in velocity/gradient. These are not error bounds. The P600/order1600 extension exceeded a 300 s cap. Next, extend arithmetic/radial-rule checks across the other declared gaps and shells and assess modal-tail uncertainty. Then freeze pressure, particle-velocity and pressure-gradient metrics, sample set, reference-uncertainty treatment, at least three harmonic truncations, acceptance/stopping rule and resource cap. Do not begin broad convergence runs or declare P4 until the protocol is frozen. The current exact-context runtime profile does not establish that larger workloads fit.

## Scientific work still open

The order-512 versus direct order-1200 overlap changes on the sampled outer shell reach `1.14e-6` in velocity/pressure-gradient norm at the 30 mm gap. Extending the separate sum to order 1600 reduces the observed finite-sum difference but gives no tail bound. The matched-order direct/public overlaps are near roundoff across 444 discrete points, not independent physical validation. Continuous shell coverage, a predeclared tolerance for pressure/velocity/gradient, and complete resource and convergence evidence remain open. Do not change the order cap or claim P4 acceptance until these are reviewed. Keep the NUM-01 BEM/high-order-FD fallback available if the series cannot meet a justified error/resource bound.

No force, dynamics, acceleration, control, microgravity or gravity-equivalence work belongs to NUM-03. Preserve failed attempts and all limits described in [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and the [P4 phase plan](../planning/phases/P04-numerical-field.md).
