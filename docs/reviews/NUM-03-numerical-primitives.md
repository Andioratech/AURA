# NUM-03 Intermediate Review — Special-Function Primitives

**Date:** 2026-10-03 · **Disposition:** Intermediate software checks PASS; NUM-03 remains ACTIVE

## Reviewed scope

This review covers only the isolated binary64 spherical Bessel/Legendre, Gauss-Legendre quadrature, and stationary sound-hard sphere coefficient routines in `src/aura/fields/numerical.py`. They are not the Hasegawa field solver and no coupled air field was evaluated.

## Evidence

- 177 focused tests pass in ENV-1.0.
- Spherical `j_n` is compared with a separately evaluated 160-digit Decimal power series for orders 0–12 at four positive arguments, including one above the oscillatory-region start requirement.
- Recurrence/derivative identities are checked for `j_n` and `y_n`; Legendre parity and derivative finite differences are checked independently.
- Gauss-Legendre nodes integrate polynomial moments through degree `2N-1` for orders 1–9; the stationary sphere coefficient enforces its modal zero-normal-velocity condition for orders 0–15 at `ka=11.45`.
- The `n=0` and `n=1` piston source factors are checked against a separate composite Simpson integration of their closed-form integrands; an undersized local workspace is rejected before quadrature starts.
- Invalid domains raise `InvalidInputError`; an unrepresentable outgoing solution raises `NumericalDomainError` rather than returning an infinite value.
- Ruff and `git diff --check` pass for the intermediate change.

## Limits and open verification

These checks establish neither Hasegawa-series convergence nor accuracy at the frozen `ka`, `kR`, and gap range. They do not test source normalization, higher-order source-integral sensitivity, complex Hankel coefficient conditioning in the coupled series, field outputs, the full summed-field sphere boundary behavior, P3 overlap, piston Rayleigh field agreement, or measured air data. The coupled evaluator, actual live-array memory audit, preflight gate, and diagnostic pilot remain required before NUM-03 can close.
