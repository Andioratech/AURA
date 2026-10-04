# Next Main Task — Complete NUM-03 Run-Path Delivery

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Published base:** `410317f` (GitHub Quality [37182663256](https://github.com/Andioratech/AURA/actions/runs/37182663256) passed)

## Current implementation under review

The local working change adds a versioned Scenario 1.1 piston displacement representation while keeping Scenario 1.0 records unchanged; a Hasegawa stationary piston/sphere adapter to `aura run`; exact-source/ENV-1.0 NUM-02 calibration gating; one ordered field chunk of at most 256 samples; immutable input, calibration, preflight, provenance and output hashes; and read-only bundle verification. Missing calibration and over-cap tests refuse before solver evaluation and run-directory creation. Synthetic rates are used only inside tests. Full local Quality passes: locked ENV-1.0 install, editable install, `pip check`, environment verification, Ruff, required-document checks, `git diff --check` and 1,667 tests.

The adapter supports one gap per run and one complete bounded chunk per request. It keeps the solver's 0–512 order cap and declared shell `a <= r < d`. The current source-factor implementation uses a recurrence rather than Gauss integration; NUM-02 retains the quadrature workspace as a conservative allowance and calibration dimension. It is not a solver accuracy parameter. No production calibration or air field run exists.

## Immediate next work

1. Review all diffs, including the schema-version extension; confirm local-only instructions, credentials and generated outputs are excluded; inspect the staged diff; and verify the effective author and committer are JuanFelipeLH <felipelamos2003@gmail.com>.
2. Commit and push only with all required checks passing, then verify remote Quality for that exact revision.
3. On the clean published revision and ENV-1.0, measure and retain the Hasegawa coefficient/field runtime calibration. Run only a bounded, declared diagnostic request whose exact NUM-02 report fits the frozen scenario limits. Its result remains numerical software verification with an INDETERMINATE science verdict.

## Scientific work still open

The order512 versus direct order1200 overlap changes on the sampled outer shell reach `1.14e-6` in velocity/pressure-gradient norm at the 30 mm gap. Extending the separate sum to order1600 reduces the observed finite-sum difference but gives no tail bound. The matched-order direct/public overlaps are near roundoff across 444 discrete points, not independent physical validation. Continuous shell coverage, a predeclared tolerance for pressure/velocity/gradient, and complete resource and convergence evidence remain open. Do not change the order cap or claim P4 acceptance until these are reviewed. Keep the NUM-01 BEM/high-order-FD fallback available if the series cannot meet a justified error/resource bound.

No force, dynamics, acceleration, control, microgravity or gravity-equivalence work belongs to NUM-03. Preserve failed attempts and all limits described in [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and the [P4 phase plan](../planning/phases/P04-numerical-field.md).
