# Next Main Task — ANA-06

**Checkpoint:** after ANA-05, 2026-10-02 · **State:** READY, not started by this handoff

The authoritative scope is the [ANA-06 phase card](../planning/phases/P03-analytical-fields.md#ana-06--add-independent-model-specific-balance-checks) and [work board](../planning/10-work-board.md). This briefing expands the startup sequence; it does not preapprove new equations, tolerances, fixture changes or a scientific PASS.

## Question

Do the existing ideal field models satisfy the applicable independent energy/accounting checks, and can the audit detect deliberately inconsistent fields or missing terms? Explain this to the owner as checking that the simulator's energy accounts close within a justified numerical error.

## Read before implementation

1. D00, [D02](../D02-mclf.md), [D04](../D04-numerical-methods.md), [D06](../D06-verification-validation.md), [D07](../D07-experiments-data.md), [D08](../D08-software-contracts.md), and G01–G05 as applicable.
2. [FIELD-1.0](../research/analytical-field-contract.md), the four kernel contracts linked in CURRENT-STATE, [source review](../research/analytical-source-review.md) and [equation register](../registers/equations.md), especially EQ-006/009/010/011.
3. The four B-03…B-06 protocols and numerical reports; source implementation, test oracles and error metrics. Use CodeGraph first if the current checkout has an index; still inspect source and primary equations.
4. Existing L0 error/verdict conventions and [delivery rules](../planning/08-reproducibility-and-ci.md). Local operations paths are in the ignored handoff, not scientific configuration.

## Work sequence

1. Reconcile actual repository state and confirm ANA-05's review/evidence. Check for later work before creating duplicate tasks.
2. Create `docs/work-items/ANA-06.md` from the task template and set only the intended implementation card ACTIVE. Freeze question, observable, geometry, exact inputs, independent reference, output contract, numerical scales, resource caps and failure policy before execution.
3. Specify the audit separately for each supported model. Define the surface or volume, outward normals, source location and all applicable flux/source/loss terms. In the ideal lossless models, an explicit assumed zero loss differs from an unavailable physical loss measurement. Identify precisely which checks are undefined or uncovered.
4. Recheck the relevant primary equations and derive the reference route. A direct residual from outputs built with the same algebra is insufficient independence. Distinguish local Euler consistency, integrated energy accounting and momentum/force accounting; completing one does not imply the others.
5. Design finite, bounded reference cases using the existing frozen domains where applicable. Document quadrature/discretization error if integration is numerical; derive and freeze an appropriate tolerance. The B-03…B-06 pointwise 2048e budget is not automatically a surface-integration tolerance. Do not silently change the 32-configuration recorder allowance or existing fixtures.
6. Implement the smallest admitted audit in planned `src/aura/mclf/balances.py`, with explicit inputs/outputs, typed invalid inputs and scope-qualified diagnostics. Inspect the actual tree first: the path is planned at this checkpoint, not evidence of an existing module.
7. Add independent expected-value, orientation/sign, cancellation and deliberately inconsistent source/flux tests. Missing source, surface or other required terms must produce an explicit diagnostic, not fabricated zero or ACCEPTED evidence. Freeze the actual negative cases and their expected outcomes in the task record.
8. Preserve every attempt. If the same cause fails twice, write root-cause analysis before another feature retry. Use [F-06](../planning/06-failure-playbooks.md) for balance/control-volume problems and the other applicable recovery branches.
9. Execute the focused comparisons and complete current CI. Review exact staged content/identity; commit incrementally, push under the owner's existing authorization and verify exact remote CI. Produce clean-source, hashed evidence where the contract requires it.
10. Write the numerical and artifact reviews with actual error/resource results, negative outcomes and limits. Update board, phase card, register, requirement mapping, README and handoff. Mark ANA-06 DONE only when its criteria pass; ANA-07 becomes READY after that review.

## Required deliverables and gate

- Task record with frozen protocol and reviewed primary-source/derivation references.
- Explicit balance contract and applicable/uncovered model domains.
- Implemented audit, independent reference tests and deliberate failure tests.
- Report with expected versus actual values, error definitions/scales, resource observations, failed attempts and immutable evidence references.
- Artifact review, complete local CI, exact published CI and updated continuity records.

**Pass condition:** Defined balances close within their justified declared numerical budget; deliberately inconsistent cases fail and missing terms remain explicit. Model validation, experimental comparison and physical claim status stay separate.

## Scope and later work

ANA-06 does not authorize implementing forces, trajectories, a controller, a new high-fidelity backend or larger-body extrapolation. It must not turn the ideal complete-sphere power identity or a progressive-wave momentum estimate into a universal body-force bound.

ANA-07 remains downstream. Before its campaign, implement/review physical recorder admission, exact source and sampling inputs (including a genuine spherical source contract), FIELD-INDEX/gradient linking, checker reconstruction, provenance and post-audit requirements. Running existing diagnostic drivers or collecting JUnit cannot substitute for that campaign or close P3. Explain a material route change to the owner in plain Spanish when actual evidence requires it.
