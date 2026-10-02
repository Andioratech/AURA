# 06 — Failure Recovery Playbooks

Use [G03](../../guides/G03-anomaly-handling.md). Each failed attempt keeps its inputs, source revision, environment, seed and outputs. After two failed cycles for the same cause, complete the [anomaly record](templates/anomaly-record.md) before more feature work. Continue unrelated eligible tasks.

## F-01 — Invalid input, units or conventions

**Trigger:** unknown units, nonfinite values, missing physical inputs, coordinate mismatch, radius/diameter ambiguity, or pressure RMS/peak conflict.

1. Stop before solver allocation; record the exact failing field and diagnostic code.
2. Reduce to the smallest scenario reproducing rejection or the incorrect accepted value.
3. Trace external quantity → canonical SI → model argument; inspect amplitude and phasor conventions.
4. Correct the parser/schema or the input with explicit provenance; add the independent negative/known-answer case.
5. Rerun P2 checks and downstream affected references. Re-entry requires an unambiguous canonical input and correct rejection behavior.

**Do not:** coerce unknown values to zero, remove validation, or silently replace units.

## F-02 — Reference or experimental data missing

**Trigger:** source inaccessible, incomplete parameter table, absent raw data or measurement uncertainty.

1. Record what is missing, why it affects the intended comparison, and tasks that can still proceed.
2. Inspect primary record, supplement, author repository and cited calibration source; keep search log.
3. After the research-cycle cap, retain INDETERMINATE and use the D-01 branch.
4. If extracting a figure is permitted/useful, preserve figure identity, calibration, sampling and reading sensitivity separately from measurement uncertainty.
5. Re-entry requires authoritative missing information or a different source with its own frozen protocol.

**Do not:** manufacture error bars, equate paper/solver agreement with independent measurement, or block unrelated foundations.

## F-03 — Domain or omitted-physics problem

**Trigger:** hard applicability condition fails, a new effect changes the result beyond the budget, or applicability is unknown.

1. Classify established hard violation versus lack of coverage: INVALIDATED evidence versus INDETERMINATE coverage per D02.
2. Plot the domain indicators and identify the responsible term/assumption.
3. Compare overlapping models where available without retuning the reference amplitude.
4. Select D-02/D-03/D-05/D-06: restrict scope in a new experiment or justify an added model.
5. Re-entry requires new equations, independent tests, resource review and matched benchmark evidence.

**Do not:** extrapolate a small-particle potential to a large sphere or explain a water measurement with an air benchmark.

## F-04 — Nonconvergence or unstable integration

**Trigger:** observable changes beyond its numerical budget, nonmonotonic refinement, solver divergence or invalid time-step behavior.

1. Preserve failed levels; inspect dimensions, boundaries, source normalization, stability and conditioning.
2. Compare a smaller analytical/manufactured case and separate mesh, time, integration tolerance and domain-size changes.
3. Measure physical-observable errors, not only algebraic solver residuals.
4. Use a justified precision change or refined subproblem within resource caps.
5. If two cycles fail, produce the root-cause report and evaluate a different formulation through NUM-01.

**Re-entry:** convergence evidence at the required levels and bounded boundary/time-sampling error. Until then, no hypothesis conclusion may rely on the unstable run.

## F-05 — RAM, time, disk or backend failure

**Trigger:** preflight rejects budget, allocation fails, timeout occurs, output cannot be retained, or backend unavailable.

1. Retain manifest/log and distinguish preflight rejection from incomplete execution.
2. Compare predicted vs actual cost and identify dominant arrays, temporaries, factorization, samples or output.
3. Profile a bounded pilot. Use chunking/caching/compression only with explicit accuracy and identity checks.
4. Prefer justified symmetry/subproblem when it preserves the intended question; otherwise register changed domain.
5. Escalate to an available documented compute tier only with source/environment/data reproduction and an explicit cost limit.

**Re-entry:** updated preflight and successful pilot; no hidden downsampling or physics change.

## F-06 — Conservation or favorable anomaly

**Trigger:** unexpected force/power relation, broken balance, implausible gain or better-than-reference performance.

1. Freeze inputs and all successful/failed outputs.
2. Recheck amplitude, units, control surface, stored energy, fluid/source/wall terms and sign conventions.
3. Identify whether the alleged bound is hard or conditional for this geometry.
4. Independently calculate the applicable balance and refine the observable.
5. Repeat with an independent formulation; keep the claim frozen until the discrepancy is explained.

**Re-entry:** full term accounting and reviewed numerical evidence. A standing-wave cavity must not be rejected using an unsupported universal `2P/c` bound.

## F-07 — Allocation/controller failure

**Trigger:** optimizer failure, saturation, delay instability, drift, wall exit or target error.

1. Compare open loop, exact-state control and realized actuator commands on the same case.
2. Test known feasible/infeasible toys and inspect scaling, singular directions, rate limits and starting points.
3. Check the necessary-condition screen and workspace/duration requirements before retuning.
4. Use only the predeclared training/tuning cases; hold final evaluation data fixed.
5. Classify controller failure, model failure, conditional target infeasibility or unknown. D-07/D-08 decide the next step.

**Re-entry:** corrected implementation or a new registered target/policy study. Exhausting a tuning budget is an inconclusive search, not a proof of physical impossibility.

## F-08 — Experimental or independent-model disagreement

**Trigger:** persistent difference outside the justified uncertainty/numerical budget.

1. Align geometry, medium/material properties, calibration, observable and time window.
2. Check whether both models share an approximation or the measurement was used for fitting.
3. Separate input, numerical and model-form discrepancies; perform one controlled A/B change at a time.
4. Compare a reduced overlap case with an independent known answer.
5. Retain both results and classify the claim LIMITED, REFUTED-IN-DOMAIN or UNDER-REVIEW as warranted.

**Re-entry:** discrepancy explained and independently checked, or a narrower claim/domain with a new decision record.

## F-09 — Seed, hash, replay or provenance failure

**Trigger:** unavailable source/environment, changed data, reused run directory, missing failed trials or unexplained backend difference.

1. Refuse evidence promotion and preserve suspect artifacts.
2. Compare stored input/environment/data hashes and command/seed streams.
3. Restore only from authenticated original records; never overwrite the old record to make hashes match.
4. Replay into a new run. Record allowed numerical reproducibility tolerance and backend differences.
5. If origin cannot be recovered, mark unreproducible and exclude from accepted claim evidence.

**Re-entry:** complete D07 manifest and independent successful replay.

## F-10 — CI or delivery failure

**Trigger:** installation, lint, tests, document checks or remote Actions fail.

1. Read the failing remote/local step and reproduce that environment/version.
2. Correct the underlying failure and inspect unintended changes. Do not weaken a rule merely to pass.
3. Run the complete workflow on the exact final content before committing, as required by local AGENTS.
4. Check staged diff, ignored files and effective author/committer. Commit with the existing owner identity only.
5. After push, verify the Actions run for that exact commit. Failed remote CI remains open work until corrected.

**Re-entry:** full local checks and remote run pass; document any environment discrepancy.

## F-11 — Required human review unavailable

**Trigger:** independent scientific review or hardware authorization required at a named gate is unavailable.

1. Assemble the exact evidence package and a concise list of decisions needed.
2. Record role/competence required and affected gate; never invent an approval or signature.
3. Continue documentation, reproductions and other eligible tasks.
4. Seek the owner decision only when the reviewable package is complete.

**Re-entry:** actual recorded review. Available code or a self-review cannot substitute for required independence.
