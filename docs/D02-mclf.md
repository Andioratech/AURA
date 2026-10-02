# AURA-D02: Mathematical Bounds and Limits Framework (MCLF)

**Version:** 1.0 · **Status:** DRAFT · **Date:** 2026-10-01

## Role

The MCLF independently audits simulator inputs and outputs against dimensions, invariants, model domains, conditional physical bounds, convergence and independent references. It must be capable of rejecting results and must not assume AURA works. It does not replace experimental validation or declare a concept impossible merely because a parameter sweep found no solution.

## Verdicts

| Verdict | Meaning | Required action |
|---|---|---|
| ACCEPTED | Available checks pass within a validated domain | May proceed to the next evidence gate; not definitive truth |
| ALERT | A conditional bound, sensitivity or diagnostic needs explanation | Preserve the run and block strong claims |
| INVALIDATED | Fundamental condition, mathematical consistency or minimum evidence requirement fails | Do not use the run as scientific evidence |
| INDETERMINATE | Available checks do not cover this regime | Obtain an independent, better-suited model |

Invalidating a simulation does not falsify AURA. Falsifying a physical claim requires a defined hypothesis and domain plus evidence sufficient to exclude it.

## Check levels

- **L0, mathematical sanity:** SI dimensions, finite values, valid signs/ranges, normalization and unit conversions.
- **L1, invariants:** energy and momentum balances, symmetries and boundary conditions where defined.
- **L2, model regime:** consistency of frequency, object size, amplitude, viscosity, distance, geometry and steady/transient assumptions with each approximation.
- **L3, numerical evidence:** observable convergence under mesh/time-step refinement and solver tolerance changes.
- **L4, independent comparison:** analytical, published or separately implemented solver reference.
- **L5, uncertainty:** sensitivity, parameter uncertainty, Monte Carlo and adversarial perturbations where appropriate.

## Minimum physical quantities

Record frequency f, angular frequency omega, pressure amplitude/RMS convention, density rho, sound speed c, intensity I, wavelength lambda, wave number k, power P, object dimensions/material/density and the applicable field regime. For a harmonic plane progressive wave, intensity relates to pressure through the declared RMS or peak convention; mixed conventions invalidate derived comparisons. Attenuation must identify its coefficient convention and propagation distance.

The dimensionless size parameter ka = 2 pi a/lambda is a model-selection indicator, not a complete validity test. Geometry, material contrast, proximity to sources/boundaries, viscosity and resonances also matter.

## Bounds and their scope

For an idealized incident progressive wave and a defined intercepted acoustic power, momentum transfer gives an order-of-magnitude force estimate F approximately kappa P_intercepted/c, with kappa near 1 for ideal absorption and up to 2 for ideal normal reflection. This is a **conditional** check. Do not apply it as a universal theorem to standing waves, resonant cavities, multiple sources, stored field energy, or unspecified control volumes. In such cases define the control surface and account for all momentum fluxes and sources.

For static holding, mechanical power F dot v can be zero while force is nonzero; therefore a power-only argument cannot bound static force. Diffraction, source aperture, attenuation and array power constrain achievable fields but need geometry-specific calculations. A required acceleration a* implies net force m a* for the selected body's center of mass, but says nothing by itself about uniform loading across an extended body.

## Invalidation rules

Rules are identified R-001 onward and versioned. At minimum invalidate: non-finite required values; dimensional mismatch; impossible schema/range; unreported units; violated declared conservation balance beyond its justified numerical tolerance; use outside a hard model domain; failed required convergence; and mismatch between manifest and result hashes. Conditional-bound excess triggers ALERT unless the assumptions establish a hard contradiction. Out-of-domain checks return INDETERMINATE.

Every rule stores ID, severity, predicate, assumptions, tolerance derivation, affected variables, evidence and software version. Tolerances are benchmark-specific; no universal 2% tolerance is implied.

## Data contract

Input includes schema version, experiment/run IDs, units, medium, source configuration, bodies, model equations/regimes, solver/discretization, boundary conditions, precision and resource estimate. Output includes pressure/field data references, force/torque, dynamics, energy/momentum accounting where applicable, convergence series, uncertainty, environment, commit, seed and checksums. Missing data yields a named diagnostic, not a guessed default.

## Anomaly protocol

Freeze exact configuration, commit, seed, environment and outputs; reproduce the run; tighten resolution and tolerances; independently compute control-volume balances; use a second formulation/solver; isolate the term with controlled A/B cases; classify the exceeded bound as hard or conditional; and only then propose a new physical hypothesis. Retain all attempts and failures.

## Decision logic

1. Schema, dimensional, finite-value, hash or hard-invariant failure: INVALIDATED.
2. Required convergence failure: INVALIDATED.
3. Conditional-bound exceedance or unresolved sensitivity: ALERT.
4. Checks do not cover the regime: INDETERMINATE.
5. All checks for this gate pass: ACCEPTED.

The report includes each rule outcome and its assumptions. Passing checks means only that available checks found no disqualifying issue.

## Initial acceptance and roadmap

The first MCLF release should implement pure, unit-aware functions for wavelength, wave number, intensity conventions, ka and the conditional momentum estimate; document R-001 through R-010; include known-answer cases; and emit machine-readable and human-readable reports. Integrate it before and after simulation. Do not promote an INVALIDATED run into an evidence bundle.
