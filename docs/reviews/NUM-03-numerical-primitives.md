# NUM-03 Intermediate Review — Special-Function Primitives

**Date:** 2026-10-03 · **Disposition:** Intermediate software checks PASS; NUM-03 remains ACTIVE

## Reviewed scope

This review covers only the isolated binary64 spherical Bessel and Legendre routines in `src/aura/fields/numerical.py`. The routines are not the Hasegawa field solver and no air geometry was evaluated.

## Evidence

- 149 focused tests pass in ENV-1.0.
- Spherical `j_n` is compared with a separately evaluated 160-digit Decimal power series for orders 0–12 at four positive arguments, including one above the oscillatory-region start requirement.
- Recurrence/derivative identities are checked for `j_n` and `y_n`; Legendre parity and derivative finite differences are checked independently.
- Invalid domains raise `InvalidInputError`; an unrepresentable outgoing solution raises `NumericalDomainError` rather than returning an infinite value.
- Ruff and `git diff --check` pass for the intermediate change.

## Limits and open verification

These checks establish neither Hasegawa-series convergence nor accuracy at the frozen `ka`, `kR`, and gap range. They do not test source normalization, complex Hankel coefficient conditioning, field outputs, sphere boundary behavior, P3 overlap, Rayleigh quadrature, or measured air data. The coupled evaluator, actual live-array memory audit, preflight gate, and diagnostic pilot remain required before NUM-03 can close.
