# P9 — Independent Confirmation and Scientific Release

**Maps to:** P9.1–P9.7; D05/D06/D07/D09

## Entry condition

P8 review selects exact claim-critical cases and independent-comparison question. Resource preflight and method availability are required.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## IND-01 — Choose an appropriately independent formulation

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ADV-07

**Steps**

1. List what the existing method assumes and which shared error could make its conclusion wrong.
2. Choose a separately derived analytical/scattering/finite-element/boundary/other formulation matched to the unresolved question, not merely a different library wrapper.
3. Review license/environment/cost and define an aligned small comparison case plus independence limitations.
4. Prepare exact equations/boundaries/observables and independent verification before expensive computation.

**Required artifacts:** Independent-method decision, shared-error matrix, resource preflight and frozen protocol.

**Acceptance / decision:** The proposed comparison can detect a named relevant failure and fits available resources.

**If unsuccessful:** D-04/D-15/F-05; choose a smaller claim-critical subproblem or record lack of independence.

## IND-02 — Implement or configure the independent comparison

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** IND-01

**Steps**

1. Implement/configure the selected method with separate derivation/reference checks and exact source/environment identity.
2. Run its own convergence and boundary studies, then compare aligned observables and uncertainty.
3. Include negative/boundary cases selected by P8; retain all disagreements.
4. Diagnose differences through controlled input/approximation changes without retuning the target evidence.

**Required artifacts:** Independent backend/adapter as needed; convergence data; B-17 comparison report.

**Acceptance / decision:** Agreement is supported by separate error budgets, or disagreement is documented and routed to claim review.

**If unsuccessful:** D-15/F-04/F-08; freeze affected claims until resolved or narrowed.

## IND-03 — Reproduce critical runs from a fresh environment

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** IND-02

**Steps**

1. Reconstruct committed source and recorded environment with immutable input/raw-data references.
2. Replay selected original and independent runs into new directories; verify hashes and allowed numerical reproducibility criteria.
3. Document hardware/backend differences and any missing artifact or access constraint.
4. Confirm reports can be regenerated from the bundle without private machine state.

**Required artifacts:** Reproduction logs/manifests and compact B-17 evidence bundle.

**Acceptance / decision:** An independently usable reproduction workflow exists; failed replay remains visible and blocks accepted use.

**If unsuccessful:** F-09/F-10; recover authentic inputs or mark evidence unreproducible.

## IND-04 — Obtain technical review and close bounded claims

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** IND-03

**Steps**

1. Assemble exact hypothesis/domain, sources, equations, numerical/measurement uncertainties and contradictory evidence.
2. Update the closest-prior-work comparison without claiming novelty from a limited search.
3. Request the required qualified independent review through the owner once the package is ready; do not fabricate reviewer identity or approval.
4. Resolve review comments and set D09 claim states with explicit supporting/contradicting run links.

**Required artifacts:** Independent review record; updated equation/claim/prior-work registers; response-to-review document.

**Acceptance / decision:** A real review is recorded and the final wording matches the weakest required evidence link.

**If unsuccessful:** F-08/F-11; preserve UNDER-REVIEW/LIMITED until the issue is resolved.

## IND-05 — Release the bounded research simulator and evidence package

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** IND-04

**Steps**

1. Check every D03 MUST row, capability documentation, examples, equation mapping, limitations and reproduction command.
2. Distinguish intermediate prototype from full bounded research release if any requirement remains incomplete.
3. Run complete CI and evidence-bundle integrity checks, then prepare the release/gate record under G05.
4. Record the exact positive, negative or inconclusive result and the experiment-design question for P10.

**Required artifacts:** P9 gate/release review; simulator usage guide; frozen evidence index and bounded scientific conclusion.

**Acceptance / decision:** Software and evidence are reproducible and accurately labeled; no unreviewed general-feasibility claim appears in the release.

**If unsuccessful:** F-09/F-10/F-11; close concrete missing items before release promotion.

## Phase exit review

Independent equations/implementation, convergence and replay support the narrowly stated outcome or explain disagreement; a real qualified review is recorded. Solver agreement alone is not experimental validation.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
