# NUM-03 — Implement the Selected Air Field Backend

**State:** ACTIVE · **Prepared:** 2026-10-03 · **Phase:** P4 numerical field

## Question and scope

Implement the selected Hasegawa stationary sound-hard sphere field series for the frozen NUM-01 air case. This task is field-only numerical software verification. It does not implement acoustic force, motion, acceleration, feedback control, gravity equivalence, or experimental validation.

## Inputs and predecessors

- NUM-02 resource estimator: DONE; no production runtime calibration exists.
- NUM-01 field contract and P3 overlap cases: DONE.
- The requested explanation checkpoint was delivered before backend implementation.

## Delivered intermediate component

`src/aura/fields/numerical.py` provides binary64 spherical Bessel/Legendre values and derivatives, Gauss-Legendre nodes/weights, the stationary sound-hard sphere coefficient, and Hasegawa source factors `f_n` using the conjugated Eq. 2 integrand. A source-factor formula error in the first implementation was caught by direct inspection of the primary paper; the original incorrect Simpson self-comparison and its sensitivity outputs are preserved as failed evidence in the [review](../reviews/NUM-03-numerical-primitives.md). Corrected `f_0` and `f_1` checks use both composite Simpson quadrature and the paper's Eq. 4 closed forms. A later order-96 Miller-normalization overflow was corrected with scaled normalization and checked against the independent Decimal series. A new four-case scalar axial regression compares the Hasegawa source expansion with exact Rayleigh-disk pressure at both gap endpoints and both sphere poles; it does not validate the full piston-only field or prescribe a production truncation tolerance. `src/aura/fields/_plane_sphere_reference.py` separately evaluates the truncated plane-wave/rigid-sphere partial-wave reference for pressure, velocity and pressure gradient under FIELD-1.0's phasor convention. It shares the checked special-function kernels but not the Hasegawa piston source integral. No coupled piston/sphere evaluator exists and no air-case field data has been produced.

The focused tests compare Bessel values against separate high-precision Decimal series through order 96, test derivative/recurrence identities, check Legendre parity and finite differences, verify Gauss-Legendre polynomial moments and stationary-sphere modal boundary cancellation, compare the stationary-sphere coefficient through order 16 against a separate high-precision reference at the frozen air `ka`, compare the first two source factors with independent Simpson quadrature and Hasegawa's Eq. 4 closed forms, compare scalar axial source pressure with the Rayleigh disk integral at both gap endpoints and both sphere poles, and exercise invalid-domain/workspace and unrepresentable-output failures. The plane-wave/rigid-sphere reference has separate boundary, phasor, small-sphere-limit and resource-gate tests. Non-gating diagnostics record source-integral quadrature sensitivity; neither they nor the axial normalization test set a field truncation tolerance. A cross-component test confirms NUM-02's solver-free workspace estimate covers the source-factor helper's local peak estimate when given matched order, quadrature and Bessel-argument dimensions. These are component checks only; the Hasegawa evaluator has not yet been compared with the plane-wave reference, and its series stability remains open.

## Remaining steps

1. Compare the separate plane-wave partial-wave field reference and the Hasegawa evaluator at common exterior points, including stationary `n=1`; the reference and coefficient-level Decimal checks now exist, but the coupled evaluator and comparison remain open.
2. Add the preflight-approved, chunked field evaluator and typed diagnostics without changing the frozen `FieldSamples` normalization.
3. Verify phasor mapping, boundary behavior, piston-only Rayleigh/P3/exact-sphere comparisons, then gap and order behavior.
4. Extend the estimator from source-factor to the coupled field evaluator's actual live arrays; keep runtime readiness INDETERMINATE until an exact-revision/ENV-1.0 bounded calibration exists.
5. Preserve nonconvergent and rejected cases; do not declare NUM-03 DONE until the coupled pilot returns fields with explicit convergence/failure diagnostics.

## Acceptance and disposition

**Acceptance not yet evaluated.** The current intermediate component passes its focused tests, but all NUM-03 coupled-backend deliverables and the pilot comparison remain open. No production or diagnostic air solver run has been made.

## Failure and change control

If special-function scaling, boundary normalization, independent comparisons, or conservative resource bounds fail, preserve the evidence and reopen NUM-01's documented method comparison. Do not silently change the air source, sphere, medium, phasor, gap range, arithmetic, or acceptance rules.
