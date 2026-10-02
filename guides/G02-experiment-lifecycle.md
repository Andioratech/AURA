# G02: Experiment Lifecycle

**Status:** DRAFT

1. Formulate a bounded question, hypothesis, observable and falsification condition.
2. Version the experiment definition and declare the model regime and assumptions.
3. Run MCLF and compute-resource preflight before launching a solver.
4. Execute with fixed configuration, seed and environment; preserve logs and failures.
5. Run post-checks, inspect convergence and compare with a reference or independent method.
6. Build an evidence bundle only when its gate criteria are met. Link resulting claims to exact run IDs.

An experiment can have many runs. Each run is immutable; corrections create a new run.
