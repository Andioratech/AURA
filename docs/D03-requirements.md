# AURA-D03: Scientific and System Requirements

**Version:** 1.0 · **Status:** DRAFT · **Date:** 2026-10-01

## Scope and conventions

The initial system covers acoustic fields, force/torque, rigid-body dynamics, control, MCLF, compute preflight and reproducibility. It does not require hardware. SI is mandatory; +Z is the default up axis, but target acceleration is an arbitrary vector in m/s2. The standard gravity constant is 9.80665 m/s2 and is only a reference.

## Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | Load versioned YAML/JSON scenarios with geometry, medium, array, body, solver and target | MUST |
| FR-002 | Validate schema, units and ranges before allocating solver resources | MUST |
| FR-003 | Provide at least one fast acoustic field solver independent of FEM | MUST |
| FR-004 | Compute force/torque with an explicitly declared validity domain | MUST |
| FR-005 | Integrate rigid-body translation and rotation | MUST |
| FR-006 | Configure real/residual gravity, including ideal zero gravity | MUST |
| FR-007 | Declare vector target acceleration and measure its error | MUST |
| FR-008 | Provide a deterministic baseline controller before machine learning | MUST |
| FR-009 | Run MCLF preflight and postcheck; INVALIDATED results cannot be promoted | MUST |
| FR-010 | Record config, commit, environment, seed, metrics, logs and artifacts per run | MUST |
| FR-011 | Estimate RAM, storage and runtime before execution | MUST |
| FR-012 | Support local CPU, remote CPU and optional CUDA backends without changing experiment physics | SHOULD |
| FR-013 | Compare runs and quantify differences in declared metrics | SHOULD |
| FR-014 | Run reproducible parameter sweeps and Monte Carlo studies | SHOULD |
| FR-015 | Export an evidence bundle for human review | MUST |

## Non-functional requirements

Core functions on Linux x86_64 CPU without a GPU. Stochastic components require explicit seeds. A run must link to experiment ID, run ID, code, configuration and claim. Logs and reports are structured and human-readable. Invalid configuration, preflight budget excess and MCLF INVALIDATED halt evidence promotion. Numerical precision changes must be explicit. The product must not label a scenario suitable for humans based on numerical convergence alone.

## Required metrics

- error_accel_rms: RMS norm of target minus body acceleration over a specified stable window.
- error_pos_rms: position tracking error where tracking is defined.
- force_residual: residual between integrated force and mass times acceleration.
- energy_balance_error and momentum_balance_error: relative errors where the model supports a defined balance.
- grid_convergence_ratio: change in the primary observable under refinement.
- stability_margin: controller/solver-specific declared measure.
- runtime_s, peak_ram_gb, peak_pressure_pa.

Every metric requires units, sampling/window definition, formula and applicability.

## Development gates

G0 documentation; G1 MCLF and preflight; G2 analytical solver; G3 verified array model; G4 published benchmark reproduced; G5 deterministic closed-loop target case; G6 robustness and uncertainty; G7 independent high-fidelity confirmation; G8 experimental design only when justified by evidence. Gate decisions and evidence are versioned.

Initial numeric tolerances, including the source proposal's 2% simple-wave target, remain proposals until derived from a named benchmark, discretization study and measurement/model uncertainty.

## Traceability

Maintain an ID-to-test/evidence matrix. Every MUST requirement has a named validation method before implementation is considered complete. A missing test mapping is itself a release blocker.
