# NUM-03 — Implement the Selected Air Field Backend

**State:** ACTIVE · **Prepared:** 2026-10-03 · **Phase:** P4 numerical field

## Question and scope

Implement the selected Hasegawa stationary sound-hard sphere field series for the frozen NUM-01 air case. This task is field-only numerical software verification. It does not implement acoustic force, motion, acceleration, feedback control, gravity equivalence, or experimental validation.

## Inputs and predecessors

- NUM-02 resource estimator: DONE; no production runtime calibration exists.
- NUM-01 field contract and P3 overlap cases: DONE.
- The requested explanation checkpoint was delivered before backend implementation.

## Delivered intermediate component

`src/aura/fields/numerical.py` currently provides binary64 spherical Bessel/Legendre values and derivatives, Gauss-Legendre nodes/weights, the stationary sound-hard sphere coefficient, and the Hasegawa source factors `f_n`. It uses a downward Miller recurrence for `j_n`, upward recurrence for `y_n`, and explicit typed domain/range errors. The Miller start accounts for both order and argument and has a fixed workspace guard. Source integration requires an explicit quadrature order and local workspace cap. No coupled-field evaluator exists and no air-case field data has been produced.

The focused tests compare Bessel values against a separate high-precision Decimal series, test derivative/recurrence identities, check Legendre parity and finite differences, verify Gauss-Legendre polynomial moments and stationary-sphere modal boundary cancellation, compare the first two source factors with separate Simpson integrals, and exercise invalid-domain/workspace and unrepresentable-output failures. A cross-component test confirms NUM-02's solver-free workspace estimate covers the source-factor helper's local peak estimate when given matched order, quadrature and Bessel-argument dimensions. These are component checks only; they do not demonstrate Hasegawa-series stability or convergence.

## Remaining steps

1. Compare stationary-sphere scattering against the separate exact plane-wave partial-wave oracle, including stationary `n=1`, and quantify source-integral sensitivity at higher orders.
2. Add the preflight-approved, chunked field evaluator and typed diagnostics without changing the frozen `FieldSamples` normalization.
3. Verify phasor mapping, boundary behavior, piston-only Rayleigh/P3/exact-sphere comparisons, then gap and order behavior.
4. Extend the estimator from source-factor to the coupled field evaluator's actual live arrays; keep runtime readiness INDETERMINATE until an exact-revision/ENV-1.0 bounded calibration exists.
5. Preserve nonconvergent and rejected cases; do not declare NUM-03 DONE until the coupled pilot returns fields with explicit convergence/failure diagnostics.

## Acceptance and disposition

**Acceptance not yet evaluated.** The current intermediate component passes its focused tests, but all NUM-03 coupled-backend deliverables and the pilot comparison remain open. No production or diagnostic air solver run has been made.

## Failure and change control

If special-function scaling, boundary normalization, independent comparisons, or conservative resource bounds fail, preserve the evidence and reopen NUM-01's documented method comparison. Do not silently change the air source, sphere, medium, phasor, gap range, arithmetic, or acceptance rules.
