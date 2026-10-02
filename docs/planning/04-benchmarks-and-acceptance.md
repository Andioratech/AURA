# 04 — Verification, Validation and Acceptance Plan

## Protocol before every comparison

Create a benchmark record with: question, exact domain, source/equation, immutable reference data, independent expected value calculation, primary observable, coordinate/amplitude convention, numerical precision, acceptance rule and its derivation, uncertainty decomposition, compute cap and failure route. Assign experiment/run IDs when executed; benchmark labels below are planning IDs only.

Do not use a universal percent tolerance. For analytic code, derive absolute/relative tolerances from scale and numerical error analysis and probe cancellation/near-zero cases. For numerical fields, study the physical observable on at least three refinements. For measurements, include the reported calibration and uncertainty; an image-reading spread is a separate term.

## Required benchmark catalogue

| ID | Test and reference | Primary observable | Acceptance evidence | Owner |
|---|---|---|---|---|
| B-01 | SI dimensions and independent hand values | Wavelength, k, ka, conversion and intensity convention | Correct finite values and exact intended input rejection | FND-03, FND-05 |
| B-02 | Serialization and invalid scenarios | Hash equality under key reorder; diagnostic code | Explicit schema behavior including malicious/ambiguous input | FND-02, FND-07 |
| B-03 | Harmonic plane wave | Complex pressure/velocity and phase | Hand reference, direction and convention checks | ANA-02 |
| B-04 | Equal counterpropagating waves | Node/antinode positions, velocity phase, net intensity | Standing field energy with correct flux; no progressive-wave shortcut | ANA-03 |
| B-05 | Two-source interference and allowed symmetry | Complex field and selected symmetry residual | Phase cancellation and consistent coordinate transform | ANA-04 |
| B-06 | Source spreading/attenuation where applicable | Amplitude/flux vs distance | Exclude singular source and incompatible near-field regime | ANA-05 |
| B-07 | Numerical counterpart of B-03…B-06 | Primary field norm and boundary residual | Three refinements plus separate domain/boundary sensitivity | NUM-04, NUM-05 |
| B-08 | Small-particle force reference | Signed force and potential-gradient consistency when conservative | Source-matched regime, analytic sign/limit, independent derivative | FOR-03, FOR-04 |
| B-09 | Water measurement candidate, selected in LIT-02 | Declared measured force or particle velocity/trajectory | Matched conditions; calibration/validation split; known uncertainty | FOR-05, MOT-08 |
| B-10 | Existing Andrade air curve | Complete force-gap curve | Separate matching scattering model; current validation INDETERMINATE | Optional air branch only |
| B-11 | Pure deterministic motion references | x(t), v(t), a(t) or angular state | Independent constant-force and linear-drag relaxation solutions | MOT-03…MOT-05 |
| B-12 | Model-consistent gravity controls | Per-term force and motion difference | Earth/ideal/residual cases differ only by declared environmental terms | MOT-06 |
| B-13 | Stochastic branch, if needed | Ensemble mean/variance/finite-window metric | Predeclared sample count, interval and time-step behavior | MOT-07 |
| B-14 | Open versus closed loop | `error_accel_rms`, constraint activity and event time | Same evaluation case, frozen tuning and held-out conditions | CTL-04, CTL-06 |
| B-15 | Known feasibility toy and impossible target | Certificate/status vs independent reference | Distinguish witness, necessary bound, unknown and certified exclusion | CTL-02, ADV-01 |
| B-16 | Adversarial campaign | Worst cases, failures and supported domain | All scheduled outcomes retained; boundary cases independently rerun | ADV-02…ADV-06 |
| B-17 | Independent implementation | Same observable with aligned assumptions | Separate derivation/backend, convergence and uncertainty | IND-01…IND-03 |

## Field comparison details

Freeze sample coordinates and units. Compare amplitude and phase without an unregistered global phase fit; if phase gauge is physically arbitrary, define the invariant comparison before the run. Near nodes, use an absolute scale from the protocol instead of dividing by nearly zero reference values. Pressure convergence alone cannot establish force convergence where spatial gradients are required.

For three-level refinement, report the actual sequence, refinement parameter, observed error changes and whether an asymptotic trend exists. Nonmonotonic results require diagnosis, not an automatically fitted convergence order. Include geometry, interpolation, boundary and averaging effects when they contribute to the observable.

## Measurement comparison details

1. Map every input and observable from paper to scenario, including radius/diameter, frequency, temperature, pressure calibration, geometry and sensor window.
2. Freeze calibration data separately from evaluation data. If the same response determines amplitude, document the resulting conditional comparison and obtain held-out observables.
3. Report pointwise residuals across the entire selected domain and predeclared scalar summaries. Retain missing values and exclusion reasons.
4. Keep numerical, model-form, parameter, measurement and digitization terms separate. Combine only with justified dependence/correlation assumptions.
5. Establish the uncertainty decision rule before seeing the final comparison. Unknown measurement uncertainty yields INDETERMINATE for formal validation.
6. A significant disagreement may identify a wrong model or unmatched experiment. Diagnose those alternatives before reporting a hypothesis refutation.

## Test suite strategy

Small deterministic unit checks run in normal CI. CLI/lifecycle integration tests exercise failure propagation and retained manifests. Compact analytical benchmarks may enter CI once their independent expected values exist. Longer convergence, stochastic and independent-solver campaigns run by an explicit bounded workflow and publish immutable evidence references; do not silently omit them while claiming a release passed all scientific gates.

Test code must not compute its expected answer by calling the same formula/helper that it is intended to check. Use hand calculations, separately derived expressions, limiting behavior or independent reference data. Duplicating implementation code under a different filename does not establish independence.

## Gate outcomes

Numerical verification PASS, experimental comparison PASS, MCLF ACCEPTED, and D09 SUPPORTED-IN-DOMAIN are distinct decisions. Record the missing evidence explicitly. A verified model can be used for an exploratory target trial under DEC-003, but P5/P6/P7 claim gates cannot be silently promoted while their required evidence remains INDETERMINATE.
