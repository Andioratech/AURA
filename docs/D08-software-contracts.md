# AURA-D08: Software Architecture and Contracts

**Version:** 1.1 · **Status:** BASELINE · **Date:** 2026-10-03

## Proposed package boundaries

The Python package is organized around schema/configuration, units and properties, field solvers, force models, rigid-body dynamics, control, MCLF, preflight, run management and evidence reporting. Each module has a narrow interface and can be tested without importing unrelated solvers.

## Canonical data

Use explicit SI values and units in serialized inputs. Canonical objects include Medium, TransducerArray, Body, Scenario, SolverSpec, Experiment, RunManifest, FieldResult, ForceResult and MclfReport. Every result declares coordinates, shape, units, precision, model version and provenance. Schema changes are versioned and migrated explicitly.

## Interfaces

- Scenario validation is pure and runs before resource allocation.
- Solver receives validated scenario plus resource/backend context and returns a result with diagnostics.
- Force model receives field and object properties, and returns force/torque plus validity status.
- Dynamics receives forces and initial state and returns sampled state with integration metadata.
- MCLF accepts versioned evidence records and returns per-rule outcomes.
- Run manager writes immutable manifests and content hashes.

No solver may silently supply missing physical parameters or units.

## Dependencies and CLI

Keep the core CPU install small. High-fidelity and accelerator libraries are optional extras. Candidate dependencies require license and compatibility review. Provide commands conceptually equivalent to validate-config, preflight, run, check, compare and reproduce; every command returns a nonzero code for failed validation or required gate failure.

`aura preflight <scenario> --workload <json> [--calibration <json>] [--output-dir <path>] [--json]` implements the NUM-02 AIR-SERIES-PREFLIGHT-1.1 contract. The strict workload declares harmonic order, Gauss-Legendre quadrature order and maximum dimensionless Bessel argument; its calibration must match these numerical dimensions, solver version, exact clean source revision and ENV-1.0 digest. The estimator includes node/weight and Miller recurrence workspace in RAM, and checks its bounded RAM/disk estimates against declared and currently available resources. Missing, stale or dimension-mismatched calibration is INDETERMINATE (exit 3); an exceeded cap is REJECTED (exit 1); a matching estimate within caps is BUDGETS_WITHIN_CAPS (exit 0). Exit 0 means only that this estimate fits its recorded budgets. It never imports or runs a numerical field solver and always reports `execution_authorized: false`. It is not a hard real-time guarantee or evidence of solver accuracy, convergence, or physical validity. See the [CLI contract](cli-usage.md) and [NUM-02](work-items/NUM-02.md).

## Errors and testing

Use typed errors for invalid input, unsupported regime, resource rejection, solver nonconvergence, MCLF invalidation and incomplete evidence. Preserve enough diagnostics for investigation. Unit, integration, benchmark and regression cases map to requirement IDs. Tests must not convert ALERT or INDETERMINATE to ACCEPTED through defaults.

## AI boundary

Machine learning may support optimization, perception or surrogate modeling after deterministic baselines exist. It cannot be the authority for physical laws, validity verdicts or scientific claims. Record model version, training data and uncertainty for learned components.
