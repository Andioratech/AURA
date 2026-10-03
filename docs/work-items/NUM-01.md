# NUM-01 — Air Field Method and Contract

**State:** DONE · **Prepared:** 2026-10-03 · **Phase:** P4 numerical field

## Question

Define one numerical field method for the DEC-002 air source/sphere case, with boundary conditions, conventions, observables, independent discriminating references, domain and a bounded preflight handoff.

## Inputs and predecessors

- NUM-W01 bounded water-like workflow qualification: DONE; its scope does not validate air.
- DEC-005 air domain and Hasegawa method selection.
- DEC-006 ordering of water qualification, then air P4; P5 onward routes through air only after an air P4 PASS.
- ANA-07/FIELD-1.0 conventions and the approved DEC-002 source/sphere parameters.

## Decision and artifacts

The contract is recorded in [Air Field Solver Contract for P4](../research/air-field-solver-contract.md), with method alternatives and recovery path in [NUM-01 Method Comparison](../research/NUM-01-method-comparison.md).

The selected method is numerical evaluation of Hasegawa et al.'s centered circular-piston/rigid-sphere spherical-harmonic series in homogeneous, lossless air. The field boundary uses a stationary sound-hard sphere at every order. The translating-sphere `n=1` branch is excluded. The request/output mapping follows FIELD-1.0 and returns pressure, fluid velocity and pressure gradient. The contract fixes the air case and full 0.1–30 mm gap interval while explicitly retaining the ideal-baffle, coaxial, rigid-sphere and single-frequency assumptions.

Independent checks are piston-only Rayleigh-disk quadrature, P3 overlap, exact plane-wave rigid-sphere partial waves, sphere-boundary checks, and at least three harmonic-order levels with pressure/velocity/gradient tracked separately. Numerical tolerances and convergence stopping rules remain for NUM-04 to derive and freeze before production runs. NUM-02 must bound the actual series memory/runtime before allocation; the paper's sample computations do not establish cost or convergence at AURA geometry.

## Acceptance and disposition

Method, physical branch, source normalization, interface observables, domain, exclusions, discriminating checks and failure route are documented. This completes NUM-01's method/contract deliverable for progression to NUM-02 pre-allocation resource-estimator work. It does **not** demonstrate that the series is stable, convergent, resource-feasible, accurate against measurements, or scientifically validated. The NUM-02 resource audit is a hard prerequisite to any solver-field allocation or production evaluation.

## Failure and change control

If special-function stability, conservative resource estimation, or independent verification cannot be achieved within declared caps, preserve the attempted estimates/results and reopen the documented axisymmetric BEM and mapped-grid high-order FD alternatives under this same physical case. Do not change the air medium, geometry, boundary conditions, arithmetic, tolerances or claims silently.
