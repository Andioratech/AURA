# NUM-03 Field-Error Protocol Basis

**Status:** DRAFT — comparison method specified; numeric acceptance budget not justified
**Prepared:** 2026-10-04 · **Decision basis:** DEC-006, DEC-007; D00, D03–D07

## Purpose and boundary

This record separates a reproducible comparison method from the numerical requirement that would turn the comparison into a pass/fail gate. It applies only to the ideal homogeneous, lossless, linear air-field model in the [P4 solver contract](air-field-solver-contract.md): the 25.230 kHz baffled piston and stationary sound-hard sphere, gap samples `0.1–30.0 mm` at `0.1 mm` intervals, and the accepted source-series domain `a <= r < d`. It does not validate the experiment, material properties, measured source amplitude, acoustic force, acceleration, or gravity-like response.

## Evidence audit

The approved P1.3 gap coordinates identify 300 measurement conditions for an axial **force** curve. The retained values are digitized from a plot, have no pointwise measurement uncertainty, and are not field observations. The air solver contract supplies an ideal mathematical field model and analytical checks, but no application-derived pressure, velocity, or pressure-gradient error requirement. DEC-007 deliberately keeps later force and acceleration budgets separate.

Consequently, neither the P1.3 plot-reading spread, the source's proposed 2% simple-wave target, the order-512 tail estimate, nor finite-order agreement supplies a defensible acceptance threshold for these three complex field observables. The tail estimate is a bound on one error source, not a target. The source's field is also not an independent measured reference. Choosing a percentage now would add an assumption not present in the approved record.

## Comparison method that can be fixed now

For every frozen sample set and gap, compare each truncation with a separately implemented, higher-precision evaluation of the same stated model. Use the same coordinates and source normalization. Do not fit a phase shift. Keep these observables distinct:

- complex pressure, with residual magnitude in Pa;
- complex Cartesian particle velocity, with vector residual norm in m/s;
- complex Cartesian pressure gradient, with vector residual norm in Pa/m.

For each observable `X`, report the maximum absolute local error and a weighted RMS absolute error over a coordinate set whose points and weights are frozen before execution. Report the full complex component residuals as well as those summaries. Use a protocol-declared absolute scale for near-zero interpretation; do not divide by a local reference value near a node. Keep errors grouped by gap so that large- and small-gap cases cannot mask one another.

Keep the following contributions separate: (1) the order-greater-than-512 mathematical tail bound, (2) floating-point sensitivity, (3) source-integral/quadrature sensitivity, and (4) uncertainty in the finite-precision reference evaluation. A conservative sum may be reported only where each contribution has a defensible bound and dependency assumptions are stated. The current exact-rational candidate bounds address only (1). Existing Decimal and cross-formulation comparisons are finite-grid sensitivity evidence, not rigorous bounds on (2)–(4), and were not produced by an external reviewer.

The 300 prescribed gap values are the comparison conditions; no interpolation claim is implied between them. Any finite spatial set supports a claim only at those coordinates. The existing all-angle/all-radius modal-tail bound is separate mathematical coverage and does not make a finite field-value comparison exhaustive.

## Preconditions for a numerical acceptance budget

Before a numeric threshold or broad NUM-04 run can be frozen, the record needs all of the following:

1. A field-specific accuracy requirement tied either to a named downstream use or to a justified numerical-verification objective. Do not back-derive it from a force or acceleration target that DEC-007 deferred.
2. A deterministic coordinate set and weights for each field observable, including coverage of both sphere-near and outer-shell regions and a statement of what is not covered.
3. At least three declared harmonic truncations within the existing order-512 cap, with all observed increments retained. Nonmonotone increments must not be converted into a fitted convergence rate.
4. Independent quadrature and precision checks on the same coordinates, plus a reference uncertainty method that is credible for the full selected domain.
5. A stopping/acceptance rule that compares the separately reported numerical contributions with the justified requirement, and a workload-specific RAM, storage, and wall-time cap.

The four-gap Decimal checks, sparse finite-order diagnostics, and exact-context one-point run do not yet satisfy these prerequisites across the 300-gap benchmark. No broad convergence, boundary-sensitivity, or force calculation is authorized by this draft.

## Current disposition

**Numeric field tolerance: not established. P4: INDETERMINATE. NUM-03: ACTIVE. NUM-04: BLOCKED.** Continue only bounded work that can qualify the reference/error sources or improve the protocol without implying acceptance. If no field-use requirement or credible full-domain reference can be supplied from the approved scope, retain the indeterminate outcome and record the unmet gate; do not manufacture a number to advance the phase.
