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

## Bounded 29.9 mm reference-sensitivity check — 2026-10-05

A 300-digit Decimal direct Rayleigh-disk/modal evaluation was completed at the sampled gap with the largest candidate modal-tail bounds, `H=29.9 mm`, at modal order 512. It used 37 angles (5° through 185° in 5° increments) and three radii about the sphere center (`a`, `a+H/2`, and `a+0.99H`), for 111 paired locations. The density was `1.18 kg/m³`, sound speed `346 m/s`, frequency `25,230 Hz`, piston radius `10 mm`, and sphere radius `25 mm`. Chudnovsky arithmetic supplied pi. Two direct source integrations used Gauss–Legendre radial rules 128 and 256.

At the same 111 coordinates and order 512, the Decimal direct calculation and public evaluator's normalized maximum differences were `1.1989151141414599e-13` for pressure and `6.428369600122808e-14` / `6.426741197042954e-14` for velocity / pressure gradient. This is finite-grid, same-model, same-order cross-formulation agreement; it does not measure truncation, establish a reference uncertainty, or validate the model physically.

The computed R128/R256 paired differences were reported near `10^-235` after 300-digit field evaluation. That number is retained as the output of the finite arithmetic comparison, but no rounding analysis or rigorous quadrature remainder supports interpreting it as an error estimate. In particular, it cannot establish quadrature accuracy or a total reference uncertainty. The two methods may share errors, cover only one gap and 111 points, and are not a measured field reference. Do not use the tiny paired difference as a pass criterion or to launch broad NUM-04.

The successful diagnostic and comparison JSON files, scripts, logs, hashes, and failed attempts remain local under ignored `results/diagnostics/`. The summary metadata SHA-256 is `a8fad79b6caea510e504ea222df6c41e68f6a2cad86527cf141ef4e7a5493908`; the paired-comparison JSON SHA-256 is `ce6201f808d672a03e7bb4b55e4db01a0bc3ddb110aeb6d0d5ea518bfcd20ff8`. An earlier pair of scripts labeled 29.9 mm actually ran at 30 mm because a later assignment overrode the gap; those attempts are preserved with their actual 30 mm metadata and excluded from this result. Summary-harness failures are also preserved. The corrected run metadata explicitly asserts `gap_m=0.0299`, both radial-rule orders, density, order, and all 111 coordinates.

This bounded check does not complete the reference-uncertainty method. Continue by investigating a quadrature/reference route whose uncertainty is independently justified over the frozen comparison domain; keep the current sample comparison exploratory, NUM-03 ACTIVE / INDETERMINATE, and NUM-04 BLOCKED. No tolerance, solver-domain change, force result, or physical-validation claim follows.

### Three-level radial-rule refinement at the same gap — 2026-10-05

A third 300-digit evaluation added radial Gauss–Legendre order 64 to the same order512 field comparison, retaining rules128 and256 and the exact same 111 coordinates at `H=29.9 mm`. The computed maximum differences between rules64/128, normalized by the higher-rule grid maxima, were `6.2342e-67` for pressure and `2.0721e-65` for both velocity and pressure gradient. For rules128/256, they were `6.3686e-237`, `2.1221e-235`, and `2.1221e-235`, respectively. These are recorded finite outputs from one same-family quadrature refinement; the roughly 170-order drop does not itself bound the integral error, account for shared arithmetic/model error, or certify the 111-point grid.

The three-rule metadata SHA-256 is `14ff3d006184b112c6242eecb7f2d11e7ee053baae8aca279fd58d97e3b5a41b`; it binds 17 local scripts, JSON outputs and logs, each checksum-verified. The radial64 run completed in 54.48 s on ENV-1.0. A deterministic comparison summary was generated twice and matched byte-for-byte. This remains one gap and one finite spatial set. A genuinely independent quadrature/reference uncertainty method over the full frozen domain is still missing; NUM-03 remains ACTIVE / INDETERMINATE and NUM-04 remains BLOCKED.
