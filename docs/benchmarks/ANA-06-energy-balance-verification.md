# ANA-06 — Bounded Harmonic Energy-Balance Verification

**Date:** 2026-10-02 · **Comparison:** PASS for the frozen model matrix · **Physical validation:** INDETERMINATE

Implementation: [`260464a9e7975b4380cc223546a5b26304e6d303`](https://github.com/Andioratech/AURA/commit/260464a9e7975b4380cc223546a5b26304e6d303). Exact remote Quality: [run 37055310149](https://github.com/Andioratech/AURA/actions/runs/37055310149). The [contract](../research/energy-balance-audit.md), [task record](../work-items/ANA-06.md) and [artifact self-review](../reviews/ANA-06-energy-balance.md) describe the exact domain and decision. This is a numerical energy-accounting check, not a momentum/force result, physical validation or evidence of gravity generation.

## Frozen model and evaluated cases

One ideal homogeneous inviscid fluid, rho=1000 kg/m³, c=1500 m/s, f=1 MHz, wavelength 0.0015 m, impedance 1.5e6 Pa·s/m, zero modeled loss and peak phasors under `Re(q_hat exp(-i omega t))`. The cases reuse frozen B-03 through B-06 sources. They contain no finite transducer, object, walls, absorption, scattering, startup or measured water-state properties.

The post-audit integration uses the declared six exactly antipodal axis points and equal weights on each sphere. The rule is limited to the three inversion-symmetric plane cases and the isotropic radial spherical case. It claims no general quadrature accuracy for arbitrary fields or surfaces.

| Case | Control volume | Independently expected boundary power (W) | Observed boundary ledger (W) | Residual (W) | Normalized absolute residual | Result |
|---|---|---:|---:|---:|---:|---|
| B-03 single +x plane wave, peak 2 Pa | Closed sphere, R=lambda/4 | 0 | 0 | 0 | 0 | PASS |
| B-04 equal +x/-x waves, each peak 2 Pa | Closed sphere, R=lambda/4 | 0 | 0 | 0 | 0 | PASS |
| B-05 coherent +x/+y waves, each peak 2 Pa | Closed sphere, R=lambda/4 | 0 | 0 | 0 | 0 | PASS |
| B-06 outgoing spherical wave, peak 2 Pa | Shell, radii 0.00075 m and 0.0009375 m | Equal powers, `4*pi*r_ref^2*A^2/(2Z)` | +2.3561944901923453e-12; -2.3561944901923450e-12 | 4.0389678347315804e-28 | 1.7141911890312011e-16 | PASS |

Every row has explicit internal-source and absorbed-power terms set to 0 W by the frozen ideal mathematical model. This assumption does not state that real equipment has zero source/loss power. Each normalized residual is compared with the unchanged contract budget `8192*2^-52 = 1.8189894035458565e-12`; the shell row is over four orders of magnitude below that budget. A zero result in the plane cases follows independently from the stated antipodal symmetry and the lossless linear energy identity, not from a force estimate.

## Independent checks and attempts to break the audit

The plane cases compare the integrated production flux against independently specified Decimal pointwise vectors: uniform progressive flux for B-03, pointwise zero for the equal opposing B-04 pair, and the independent Decimal coherent-field oracle from `tests/interference_reference.py` for B-05. The complete-surface expectations are separately derived from the source-free period-mean energy identity and the fixed antipodal pairing. The shell powers are independently evaluated from the B-06 radial pressure/velocity identity and complete-sphere area in guarded Decimal arithmetic; the expected source-free shell residual is zero.

The tests require material corruption to fail: reversing sampled velocity makes the shell comparison FAIL; adding a 1e-12 W source term also makes it FAIL. Unknown source, unknown absorption, or both return INDETERMINATE with named missing terms and no residual verdict. Invalid geometry, sample/surface mismatch, differing shell frequencies and a forged inconsistent result state are rejected. Results are not attached to the overall MCLF acceptance state.

Full local Quality passed Ruff and **1,366 tests in 17.70 s**. The exact remote Quality run for the implementation commit passed environment/lock checks, Ruff and **1,366 tests in 21.50 s**. Clean-source verification of the exact published commit passed **143 focused energy/interference/spherical tests in 1.74 s**. The worked example returned PASS in all four frozen cases. Full-suite warnings are the existing `record_property` incompatibility with the project's xunit2 JUnit family; they are not failures.

During development, the first full-suite run caught an eager package re-export that violated the L0 configuration-validation import firewall (1,365 passed, one failed); the re-export was removed and the complete suite passed. The report also retains the first bad frequency-regression fixture, an environment inventory preflight using a temporary incomplete environment, and a report-assembly missing-directory error. Those causes were corrected without changing scientific assumptions, implementation thresholds or source cases. Exact attempts and outputs are kept in the ignored report bundle.

## Reproducible evidence and boundary

Verification ID: `VERIFY-ANA06-6e3c0547cb364aef9d67e6518cc32b93`.

The ignored local bundle is `results/verification/ANA-06/VERIFY-ANA06-6e3c0547cb364aef9d67e6518cc32b93/`. It contains before/after clean-source and ENV-1.0 captures, all three lock/profile files, the published source and tests, clean-source JUnit/log, four JSON result records, full local Quality attempts including the failed attempt, exact remote CI identity, development environment/report-preflight findings, and SHA-256 hashes. Source and environment captures match before and after. The report index SHA-256 is recorded in `verification.sha256`; all indexed artifacts were rechecked against `verification.json`. The bundle is under the 16 MiB cap. Outputs are software-verification artifacts, not D07 RunManifests.

ANA-06 establishes only that these explicit ideal-field energy ledgers close within their bounded arithmetic tolerance. It supplies no body momentum balance, acoustic force, real-water calibration, finite-source model, experiment or validation for particles, larger objects/masses or microgravity. P3 remains open until ANA-07 delivers and reviews its admitted recorded campaign.
