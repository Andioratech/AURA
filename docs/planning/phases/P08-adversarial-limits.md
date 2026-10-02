# P8 — Uncertainty, Counterexamples and Operating Limits

**Maps to:** P8.1–P8.7; D02/D06/D09

## Entry condition

P7 gate or explicit review authorizes a bounded limitation study after a negative target result. Frozen nominal case, hypothesis quantifiers, uncertainty set and run budget are required.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## ADV-01 — Derive and audit necessary-condition limits

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** CTL-07

**Steps**

1. Execute L-01…L-05 from the falsification plan for the actual target/domain, documenting all assumptions.
2. Independently derive the key kinematic/force-set inequalities and the direction of uncertainty needed for a valid exclusion.
3. Verify any numerical certificate separately; classify local/global and nominal/robust statements.
4. Retain simple boundary counterexamples and known feasible controls to check the checker.

**Required artifacts:** `analysis/limits.py`; scoped limit/certificate records; B-15 independent checks.

**Acceptance / decision:** No unsuccessful search is presented as a proof; each exclusion covers the complete set it claims to exclude.

**If unsuccessful:** F-06/F-07/F-08; withdraw or narrow an unsupported certificate.

## ADV-02 — Freeze and run deterministic sensitivity attacks

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ADV-01

**Steps**

1. Select applicable A-01…A-18 attacks and justify omitted ones against the actual claim.
2. Freeze source-backed ranges, one-factor design, selected interactions, run caps and primary statistics.
3. Execute limiting/nominal cases first, then sensitive boundaries; retain invalidated, failed and timed-out records.
4. Identify candidate failure mechanisms and distinguish true domain boundaries from sparse sampling.

**Required artifacts:** `analysis/sweeps.py`; frozen attack design; complete run index and sensitivity report.

**Acceptance / decision:** Every planned case has a disposition; observed boundaries are labeled with sampling and model limits.

**If unsuccessful:** F-03/F-04/F-05; reduce a newly registered study or isolate the mechanism.

## ADV-03 — Quantify uncertainty and stochastic robustness where justified

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ADV-02

**Steps**

1. Separate uncertain parameter ranges, stochastic processes, numerical error and model-form alternatives.
2. Choose interval study or evidence-backed distributions; freeze sample count/seeds and the precision or interval calculation for the chosen statistic.
3. Execute reproducible sampling without changing distributions after observing failure.
4. Report uncertainty in success/failure estimates, tail coverage limitations and dependence assumptions.

**Required artifacts:** Uncertainty register; seeded campaign manifests; statistics and convergence/precision report.

**Acceptance / decision:** Probabilistic statements use justified distributions and finite-sample uncertainty; unknown distributions remain interval/sensitivity results.

**If unsuccessful:** F-03/F-09; correct statistical assumptions and preserve the prior study.

## ADV-04 — Stress the water and microgravity assumptions

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ADV-03

**Steps**

1. Compare consistent ideal/Earth/residual-gravity cases and fluid-flow/temperature/wall perturbations from the frozen design.
2. Challenge observation limits and radiation-versus-advection interpretation over the target interval.
3. Evaluate material/size changes only within the reviewed domain; register a new experiment for extensions.
4. Summarize which effects defeat the target or invalidate the model and what new evidence each requires.

**Required artifacts:** Environment/fluid robustness report; A-04…A-12/A-17 evidence and scope map.

**Acceptance / decision:** An idealized success is not generalized to a real microgravity platform or an untested particle class.

**If unsuccessful:** D-13/D-14/F-03/F-08; narrow claim or research the needed model.

## ADV-05 — Recheck the strongest positive and negative cases

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ADV-04

**Steps**

1. Select predeclared representative best/worst/boundary cases, including invalidated favorable results where informative.
2. Repeat at refined numerical settings and through independent calculations available at this phase.
3. Reduce each apparent contradiction to a minimal reproducible configuration.
4. Classify numerical failure, model-domain failure, controller limitation, observed target failure and certified exclusion separately.

**Required artifacts:** Adversarial replay bundle; counterexample/minimal-case records; prioritized P9 cases.

**Acceptance / decision:** Claim-critical contradictions survive the appropriate checks or are explicitly withdrawn as artifacts.

**If unsuccessful:** F-04/F-06/F-08/F-09; investigate before publishing a physical limit.

## ADV-06 — Publish a domain map with all evidence statuses

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ADV-05

**Steps**

1. Generate maps/plots from the full study index, with unknown/outside-domain and failure categories visible.
2. Show uncertainty and sample coverage; state any interpolation method and prevent unsupported extrapolation.
3. Run MCLF audits on inputs, outputs and aggregation; cross-check plots against raw metrics and failure counts.
4. Write bounded proposed claim updates and limitations in plain English.

**Required artifacts:** Operating-domain map; `reporting/plots.py`/evidence extensions; uncertainty and failure catalogue.

**Acceptance / decision:** A reader can trace every displayed region/point to evidence and see what was not decided.

**If unsuccessful:** F-09/F-10; repair provenance/aggregation without dropping inconvenient results.

## ADV-07 — Close robustness and select independent confirmation cases

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ADV-06

**Steps**

1. Review uncertainty assumptions, all attacks, retained failures and claim-critical boundaries.
2. Choose the smallest discriminating set for P9, including a negative or boundary case and a positive case if one exists.
3. Record P8 decision, remaining model limitations and which claims remain UNDER-REVIEW.

**Required artifacts:** P8 gate review; P9 case-selection protocol; updated D09 records.

**Acceptance / decision:** The independent study is driven by unresolved claim risk rather than only attractive results.

**If unsuccessful:** D-15/F-11; resolve review gaps or limit the proposed claim.

## Phase exit review

Numerical, input, measurement and model uncertainties are separated; all scheduled outcomes are indexed; supported, excluded-for-target, outside-model and unresolved regions are mapped with defensible scope.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
