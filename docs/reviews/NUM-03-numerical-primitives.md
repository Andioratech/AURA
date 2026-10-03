# NUM-03 Intermediate Review — Special-Function Primitives

**Date:** 2026-10-03 · **Disposition:** Intermediate software checks PASS; NUM-03 remains ACTIVE

## Reviewed scope

This review covers isolated binary64 spherical Bessel/Legendre and Gauss-Legendre routines, the stationary sound-hard sphere coefficient and Hasegawa source factors in `src/aura/fields/numerical.py`, and the separate truncated plane-wave/rigid-sphere reference in `src/aura/fields/_plane_sphere_reference.py`. The reference is a verification fixture using an independent source geometry; it reuses the checked special-function kernels. It is not the Hasegawa field solver, and no piston/sphere coupled air field was evaluated.

## Evidence

- 195 focused numerical-primitive tests pass in ENV-1.0.
- Spherical `j_n` is compared with a separately evaluated 160-digit Decimal power series for orders 0–12 at four positive arguments, including one above the oscillatory-region start requirement.
- Recurrence/derivative identities are checked for `j_n` and `y_n`; Legendre parity and derivative finite differences are checked independently.
- Gauss-Legendre nodes integrate polynomial moments through degree `2N-1` for orders 1–9; the stationary sphere coefficient enforces its modal zero-normal-velocity condition for orders 0–15 at `ka=11.45` and matches a separate 160-digit Decimal coefficient reference for orders 0–16 at the frozen air `ka` (including stationary `n=1`). This is coefficient-level reference evidence, not yet a sampled exact plane-wave scattering comparison.
- The `n=0` and `n=1` piston source factors are checked against a separate composite Simpson integration of their closed-form integrands; an undersized local workspace is rejected before quadrature starts.
- A non-gating quadrature-sensitivity diagnostic evaluated source factors through order 24 at both ends of the contract gap range, using the DEC-002 sphere radius 25 mm, piston radius 10 mm, `f=25.23 kHz`, and `c=346 m/s`. For orders 0–16, the largest successive relative changes for quadrature orders 16→32, 32→64, and 64→128 were respectively `1.21e-14`, `1.43e-14`, and `6.30e-15` at `H=0.1 mm`, and `3.29e-15`, `3.71e-15`, and `5.04e-16` at `H=30 mm`. At the near endpoint, `|f_24|=25.36` while `|f_16|=0.0110`; the corresponding stationary coefficient-weighted magnitudes were `1.72e-10` and `1.08e-5`. These are unweighted source-factor and coefficient diagnostics only; no field sum, truncation acceptance, or physical result follows.
- The separate plane-wave/rigid-sphere reference evaluates the truncated partial-wave expansion in the `exp(-iwt)` convention and returns pressure, velocity and pressure gradient. Four tests check zero normal gradient on the sphere at three orientations, the Euler pressure/velocity relation, the small-sphere incident-wave limit, and workspace rejection before special-function allocation. This establishes reference-code behavior in those checks, not agreement with an experimental field or the not-yet-built Hasegawa evaluator.
- An initial combined test run exposed that importing this reference at test-collection time invalidated NUM-02's assertion that preflight does not import a field backend. The test now imports it only when its reference cases execute; the combined preflight/numerical/reference set then passed 228 tests.
- Full local Quality passed on this intermediate change: hash-locked dependency install, editable install, `pip check`, ENV-1.0, Ruff, required-document checks, diff check and 1,623 tests. The published parent `958189e` has remote Quality PASS; the reference change still requires its own remote run after publication.
- NUM-02 preflight v1.1 binds quadrature order and maximum Bessel argument in both workload and calibration, and includes node/weight plus recurrence scratch. A cross-component regression confirms the solver-free preflight inventory covers the source helper's local peak estimate for the matched test dimensions.
- Invalid domains raise `InvalidInputError`; an unrepresentable outgoing solution raises `NumericalDomainError` rather than returning an infinite value.
- Ruff and `git diff --check` pass for the intermediate change.

## Limits and open verification

These checks establish neither Hasegawa-series convergence nor accuracy at the frozen `ka`, `kR`, and gap range. The quadrature diagnostic does not establish a field truncation tolerance. Source normalization, complex Hankel coefficient conditioning in the coupled series, comparing Hasegawa output against the plane-wave reference, full summed-field boundary behavior, P3 overlap, piston Rayleigh field agreement, and measured air data remain open. The coupled evaluator, actual live-array memory audit, preflight gate, and diagnostic pilot remain required before NUM-03 can close.
