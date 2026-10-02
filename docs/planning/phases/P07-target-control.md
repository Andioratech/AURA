# P7 — Target Feasibility and Deterministic Control

**Maps to:** P7.1–P7.7; D02/D03/D06/D08

## Entry condition

Required P5 and P6 evidence gates pass for the declared model/target domain. No AI controller or unsupported real-microgravity claim.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## CTL-01 — Freeze the acceleration target and cheap necessary conditions

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** MOT-08, LIT-05

**Steps**

1. Specify target vector/function, finite duration, initial state, workspace clearance, metric tolerance and full evaluation window.
2. Derive L-01 workspace/time and L-02 load-demand checks; reject structurally impossible target cases before controller tuning.
3. Record hardware-backed versus hypothetical pressure/power/rate limits and uncertainty; do not use electrical power as acoustic power without conversion evidence.
4. Choose train/tune/evaluation cases and the intended target-success decision before running control.

**Required artifacts:** Target protocol; `control/targets.py`; necessary-condition report; holdout design.

**Acceptance / decision:** The target has a measurable decision rule and fits the stated necessary conditions or receives a scoped exclusion record.

**If unsuccessful:** D-07/D-10/D-12; prepare a new target decision if excluded.

## CTL-02 — Characterize attainable force and local authority

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** CTL-01

**Steps**

1. Build/verify source response or transfer basis with all geometry/frequency/model inputs in cache identity.
2. Compute constrained force samples and local sensitivities without mistaking them for the whole reachable set.
3. Implement known feasible/infeasible toy checks and any justified outer-bound certificate with independent verification.
4. Report weak directions, singular cases and unsupported target demands with the correct certificate type.

**Required artifacts:** `fields/transfer.py`, `control/reachability.py`; B-15 report; force-set plots.

**Acceptance / decision:** Feasible witness, sample-based unknown and certified exclusion are distinct outputs; stale caches and invalid constraints are detected.

**If unsuccessful:** D-07/D-08/F-07; resolve model/optimization evidence before tuning.

## CTL-03 — Implement bounded actuation allocation

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** CTL-02

**Steps**

1. Map desired field/force to element amplitude/phase using one reviewed deterministic bounded method.
2. Enforce per-element and aggregate limits, phase representation, rate limits and any frozen actuator dynamics.
3. Return requested versus realized actuation/force, solver status, saturation and residual; handle infeasible requests explicitly.
4. Verify direct recomputation of allocated fields and a predeclared finite set of starts/cases.

**Required artifacts:** `control/allocation.py`; allocation fixtures and constraint/error report.

**Acceptance / decision:** Every emitted command is admissible; solver failure or target mismatch is surfaced to control and evidence reports.

**If unsuccessful:** F-07; inspect scaling/constraints and avoid unbounded optimizer retries.

## CTL-04 — Implement one deterministic feedback controller

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** CTL-03

**Steps**

1. Choose the simplest controller suited to the registered dynamics, with gains/tuning protocol fixed on training cases.
2. Run open-loop and exact-state closed-loop baselines on matched initial conditions.
3. Handle saturation/rate limits and integrate the controller with explicit acoustic/dynamics/control update rates.
4. Define the applicable stability diagnostic and test adverse steps/delays within a bounded tuning budget.

**Required artifacts:** `control/baseline.py`; tuning record; open/closed-loop pilot and stability report.

**Acceptance / decision:** Controller behavior and stability diagnostic are reproducible; no retuning on final evaluation data.

**If unsuccessful:** D-08/F-07; diagnose reachability/implementation before choosing another policy.

## CTL-05 — Add realistic virtual observations and a minimal estimator

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** CTL-04

**Steps**

1. Specify sensor frame, cadence, latency, noise/bias and dropout behavior with sources or explicit hypothetical ranges.
2. Implement observation and estimator modules with timestamps and uncertainty; keep exact-state reference separately labeled.
3. Verify estimator on independent synthetic trajectories and held-out disturbances.
4. Ensure the controller only uses available observations and cannot access hidden truth except in the declared oracle benchmark.

**Required artifacts:** `sensors/virtual.py`, `estimation/baseline.py`; observation contract and checks.

**Acceptance / decision:** Latency/noise cannot be silently ignored; oracle and sensor-based outcomes are distinguishable and replayable.

**If unsuccessful:** F-01/F-07; adjust justified observation/model assumptions through a new protocol.

## CTL-06 — Run the frozen acceleration evaluation

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** CTL-05

**Steps**

1. Execute held-out target cases with fixed configuration, tuning, seeds and resource caps.
2. Calculate `error_accel_rms` with the registered window/weights; separately report position error when applicable, events and actuator utilization.
3. Recheck time resolution, sensor/filter sensitivity and actual net acceleration; retain all failures and wall exits.
4. Compare open-loop, oracle-state and sensor-based closed loop without selecting only favorable trials.

**Required artifacts:** B-14 run set; metric/constraint/residual plots and uncertainty-qualified comparison.

**Acceptance / decision:** Target outcome follows the original decision rule; velocity/trapping success does not replace failed acceleration tracking.

**If unsuccessful:** D-09/D-12/F-04/F-07; retain negative outcome and select the documented next branch.

## CTL-07 — Review bounded control and authorize robustness work

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** CTL-06

**Steps**

1. Audit requirement/metric mapping, model evidence, realized limits and independent replay.
2. State the smallest supported or failed target claim and all hypothetical hardware/environment assumptions.
3. Record P7 gate decision and frozen nominal cases/uncertainty domain for P8; a failed target may proceed to an explicitly reviewed limitation study instead of a success claim.

**Required artifacts:** P7 gate review; target evidence bundle; bounded claim draft and robustness handoff.

**Acceptance / decision:** The gate preserves the actual outcome and authorizes only the corresponding P8 scope.

**If unsuccessful:** D-07/D-11/D-12/F-11; resolve scope or evidence without relabeling failure.

## Phase exit review

A frozen target case has a reproducible open/closed-loop comparison, all actuator/observation constraints are included, and the acceleration outcome is reviewed. Negative or infeasible results are valid outputs; they do not meet a success gate unless the objective is formally revised.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
