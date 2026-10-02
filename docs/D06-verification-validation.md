# AURA-D06: Verification and Validation

**Version:** 1.0 · **Status:** DRAFT · **Date:** 2026-10-01

Verification asks whether the equations are solved correctly. Validation asks whether the chosen model represents the physical question. Passing either alone is insufficient for a scientific claim.

## Evidence ladder

1. Unit/dimensional and limiting-case checks.
2. Analytical solutions (plane wave, point source where assumptions hold, interference, free-body dynamics).
3. Numerical convergence across at least three refinements for critical observables.
4. Published benchmark reproduction with matching geometry, material, frequency, boundary and observable.
5. Independent formulation/solver comparison.
6. Experimental comparison when a justified, safe experiment is available.

Record benchmark provenance and parameter mapping. Published figures digitized from plots have added uncertainty. Never claim exact reproduction when source parameters are missing.

## Acceptance

Each benchmark defines its own observable, tolerance, uncertainty, mesh/time-step protocol and stopping rule before running. The proposal's 2% simple-wave target is not a project-wide tolerance. Failed or nonconvergent cases remain in the record and block the relevant gate.

## Regression and robustness

Keep analytical known-answer cases as regression checks. Use dimensional metamorphic properties and symmetry only where assumptions warrant them. Sweep relevant parameters and quantify uncertainty; distinguish numerical variability from uncertain physical inputs. Report confidence intervals or distributions with their assumptions.

## Falsification

Pre-register a bounded hypothesis and observable. A negative result falsifies only that statement in the tested domain. Preserve failed configurations and distinguish model failure, numerical failure, and evidence against a physical hypothesis.

## Evidence record

Every accepted evidence item includes experiment and run IDs, commit, config and data hashes, solver/regime, convergence, MCLF verdict, benchmark mapping, uncertainty, limitations and reviewer decision.
