# Next Main Task — NUM-03 Full Shell/Gap and Run-Path Verification

**Prepared:** 2026-10-04 · **State:** NUM-W01, NUM-01 and NUM-02 DONE; NUM-03 ACTIVE · **Validated source revision:** `0c0c725` (GitHub Quality [37179378195](https://github.com/Andioratech/AURA/actions/runs/37179378195) passed)

## Completed diagnostic step

The direct Decimal Rayleigh-disk-to-modal implementation matches the public evaluator at the same orders 18–500 over 37 angles and three radial shells at each gap 0.1, 10, 20 and 30 mm. With source radial rule128, maximum normalized absolute same-order differences over all 444 points are `1.5e-13` in pressure and `5.3e-13` in velocity/pressure gradient. This is finite-order cross-formulation agreement, not convergence. Earlier one-point source-only potential checks agree with direct Rayleigh disk quadrature to about `7e-14` for orders 300–500; that disk quadrature's own radial/azimuth refinement difference is `5.2e-10`.

At the demanding 30 mm gap and `0.99H` outer shell, `r=54.7 mm`, `d=55 mm`, and `r/d≈0.9945`. Direct Decimal arithmetic at 300 digits with radial source rule256 was extended through order1600 at 37 polar angles. Normalized maximum differences against finite order1600 for orders 512/800/1000/1200/1400 are, respectively:

| Order | Pressure | Velocity | Pressure gradient |
|---:|---:|---:|---:|
| 512 | `3.457e-8` | `6.724e-7` | `6.724e-7` |
| 800 | `7.236e-12` | `2.260e-10` | `2.260e-10` |
| 1000 | `3.099e-13` | `6.799e-12` | `6.799e-12` |
| 1200 | `9.326e-16` | `9.047e-14` | `9.047e-14` |
| 1400 | `1.554e-16` | `3.685e-16` | `2.531e-16` |

Source radial rules128, 256 and512 give the same reported metrics through order1600. The 200-digit and 300-digit calculations also agree at their common tested orders through800. These finite-grid differences are not rigorous error/tail bounds, and no production truncation tolerance has been set. The public field evaluator still caps order at512, so do not infer production-domain resolution from the high-order diagnostic.

NUM-02's solver-free workload estimator was applied to 4 gaps ×111 points, quadrature order256, maximum Bessel argument25.1, chunk size64, and baseline RSS deliberately set to zero. Hypothetical RAM estimates are 1,005,568 bytes at order512, 1,268,096 at800, 1,450,112 at1000, 1,631,744 at1200 and 1,994,496 at1600; estimated disk remains 946,176 bytes. All reports remain `INDETERMINATE` with `wall_time_s=null` because no exact-revision production runtime calibration exists. These resource values follow NUM-02's linear workspace inventory and are not measurements from a production solver run. Diagnostic scripts and JSON outputs, including invalid report-generation attempts, are preserved in ignored `results/diagnostics/`; checksums and failure explanations are in the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md).

## Immediate next work

Complete shell/gap verification across the declared `0.1–30 mm` interval, explicitly checking the three radial shells and adequate angular sampling at the reviewed candidate order. Keep matched-order public overlap separate from order-sensitivity analysis. Then integrate the tested field calculation with the public NUM-02 preflight, bounded chunk lifecycle, immutable run manifest, and diagnostic-only run policy. Preserve every failed or rejected run. Do not run a production workload without a matching exact-source-revision ENV-1.0 calibration.

Before changing the public order cap or narrowing `a<=r<d`, review a stated field-accuracy tolerance and how it applies to pressure, particle velocity and pressure gradient over the entire requested domain. If resolution or conservative resources cannot be established, preserve that finding and assess NUM-01's documented independent-solver fallback.

Stay within the selected air field domain: 50 mm sphere, 25.23 kHz centered source, and `a<=r<d`. No force, dynamics, acceleration, control or gravity-equivalence work belongs to this step. See [NUM-03](../work-items/NUM-03.md), the [coupled-kernel review](../reviews/NUM-03-coupled-kernel-review.md), [NUM-02](../work-items/NUM-02.md), and the [P4 plan](../planning/phases/P04-numerical-field.md).
