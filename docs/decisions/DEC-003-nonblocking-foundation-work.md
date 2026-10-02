# DEC-003: Continue Foundation Work While Benchmark Evidence Is Incomplete

**Status:** APPROVED BY PROJECT OWNER · **Date:** 2026-10-02 · **Owner:** AURA project owner

## Owner direction

The owner directed that AURA must not stop development solely because a published benchmark omits some data. Continue the other foundation and validation-preparation steps, record missing data and their effects, and search for better evidence as the project advances.

## Decision

1. Keep the Andrade et al. (2016) sphere-force case as the first measured reference. Its plotted curve may be used for exploratory comparisons at figure-reading resolution.
2. Do not invent the missing measurement uncertainty. A comparison based only on the published graph is formally **INDETERMINATE** for validation, even if the curves appear to agree.
3. Do not let that evidence gap block P2 unit/schema/MCLF foundation work or P3 analytical acoustic checks, because those tasks can be developed and checked without the missing scale accuracy.
4. Proceed through P4 solver work after the P2 and P3 checks. Before a solver run, freeze the solver-specific domain and complete D05 resource preflight. P5 force-model comparisons may be exploratory while the source uncertainty is missing, but cannot be presented as experimental validation.
5. Keep stronger claims gated: no claim that AURA works, no extrapolation to dense/heavy bodies, no array-control or prescribed-acceleration claim, and no microgravity-performance claim until the corresponding force, dynamics and control evidence gates are met.
6. Continue looking for source uncertainty or a better-specified measured case when useful. New evidence may upgrade the benchmark decision through a later decision record; it must not silently rewrite prior results.

## Scope and effect

This decision changes work sequencing and the handling of an incomplete reference; it does not alter physical equations, SI contracts, MCLF verdict meanings, benchmark inputs, or scientific acceptance criteria. P1 stays open as an evidence track. P2 is now the active foundation track. P1.7's detailed compute preflight moves to the point before P4 solver execution, when the numerical domain and solver are known.

The prior strict sequencing plan is preserved at [PLAN-01 v1.1](../archive/PLAN-01-v1.1-project-execution-plan.md). The current plan is [PLAN-01 v1.2](../PLAN-01-project-execution-plan.md).

## Next work

Start P2 with canonical SI conventions, the minimal input/run schemas, dimensional helper calculations and a versioned MCLF L0 rule table. Preserve explicit unknowns; do not silently substitute default values for missing scientific inputs.
