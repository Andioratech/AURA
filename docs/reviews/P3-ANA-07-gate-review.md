# P3 Gate Review — ANA-07 Bounded PASS

**Assessment date:** 2026-10-03 · **Gate:** P3 · **State:** PASS for declared analytical-software scope

This review was performed at the owner's request as a deterministic audit of the P3/ANA-07 evidence. It is an AI-assisted, non-independent review; it does not represent an external scientist or physical validation. On 2026-10-03, after receiving this bounded recommendation, the owner instructed: “mi decisión es continuar con el desarrollo.” That direction is recorded here as **PASS for the declared P3 analytical-software scope**, consistent with the recommendation. It authorizes progression to P4 planning/research only; it does not expand P3 evidence or validate physical behavior. No scientific scope, equation, input, tolerance, or run was changed.

## Review identity

| Field | Record |
|---|---|
| Scope | P3 analytical acoustic foundation; ANA-01 through ANA-07 and RUN-01 within their declared scopes |
| Baseline | D00 v1.3; P03 phase card; DEC-003 and DEC-004 |
| Current checkout revision | `9ee66f7b1fb79eff807c078c102aae17bab09db6` |
| Recorded campaign revision | `260c73064dec57093339c033b3f0ad5273204c28` |
| Fresh replay revisions | B03-AXIAL: `4e24c75d7fa941a5b586bc60b984a95c272d15c8`; B06-AXIAL: `1d6efb0b17fa95a95b36d8d1d769e8896981688f` |
| Preparer role | Research implementer |
| Reviewer role | Owner-directed deterministic evidence auditor (Codex); non-independent, no human qualification claimed |
| Owner instruction | User requests on 2026-10-03 to conduct the deterministic review and, after receiving the bounded PASS recommendation, continue project development; recorded outcome: bounded P3 PASS |
| Relevant decisions | DEC-001, DEC-003, DEC-004 |

## Review-policy basis

| Source | Requirement | Application to P3 |
|---|---|---|
| [Execution protocol](../planning/00-execution-protocol.md), “Review and ownership” | A qualified independent reviewer is needed where P9/P10 or the approved baseline explicitly requires one. | P3 is neither P9 nor P10. |
| [PLAN-01](../PLAN-01-project-execution-plan.md), §6 | Every phase boundary needs a recorded gate review, decision, reviewer/owner, date, and authorized next scope. | Requires an attributed decision; it does not say the reviewer must be independent. |
| [P03 phase card](../planning/phases/P03-analytical-fields.md) | The P3 exit is reproduced closed-form cases with quantified errors; its review refers to the execution protocol. | It does not add an independent-person requirement. |
| [D06](../D06-verification-validation.md), “Evidence record” | Accepted evidence includes a reviewer decision. | It does not specify an independent or human reviewer for P3. |
| [G05](../../guides/G05-release-review.md) | Independent review is required before a release. D00 records G01–G05 as DRAFT. | P3 is an internal phase gate, not a product/research release. |
| [ANA-07 task record](../work-items/ANA-07.md) | Step 7 had added a qualified independent reviewer as a task-specific condition. | This stricter local condition is not present in the P3 baseline. The owner has now asked for this deterministic assessment; the review is labelled non-independent and does not alter scientific criteria. |

Therefore, P3 does need an attributed gate decision, but the approved baseline does not require that decision to come from an external qualified reviewer. Independence is a useful bias-control for consequential claims and releases; it is not a universal substitute for predeclared checks, nor does it make the P3 evidence stronger by itself. This assessment does not satisfy the later independent-confirmation or release-review requirements.

## Evidence against the P3 exit criteria

| Criterion | Evidence and finding | Threshold or decision rule | Limits | Preparation status |
|---|---|---|---|---|
| Required analytic recorders execute the frozen B-03…B-06 campaign | [ANA-07 matrix report](../benchmarks/ANA-07-recorded-field-matrix.md): 32/32 configurations and 264/264 sample points completed; all integrity and frozen comparisons passed | ANA-REF-1.0 normalized error `2048 × 2^-52 = 4.547473508864641e-13`; unchanged | Homogeneous, stationary, linear, lossless ideal fields; no radiator, measured water, body coupling, force, motion, or physical validation | Evidence and owner-recorded decision: PASS within software scope |
| Field components and derived metrics match independent references | Matrix maximum normalized errors: pressure `9.020562075079397e-16`; velocity `7.940933880509066e-16`; gradient `7.599405318910162e-16`; mean intensity `1.5881867761018131e-16` | Frozen ANA-REF-1.0 tolerance above | Manufactured mathematical references; comparisons do not establish model validity | Evidence and owner-recorded decision: PASS within software scope |
| Run integrity and provenance are reproducible | [Artifact review](ANA-07-matrix-artifact-review.md) found 32 unique configurations, bound hashes, verified bundles, and no missing bundle or unexpected case. Fresh B03-AXIAL and B06-AXIAL reports match their original inputs, four field artifacts, and metrics exactly. | Exact input and artifact hashes plus frozen metrics | Local immutable evidence is ignored by Git and must be reviewed at the VM paths recorded in ANA-07 and the matrix report | Evidence reported PASS; reviewer should inspect the indexed bundle and both replay records |
| Model-local audit coverage is adequate for the declared incident-field scope | [ANA-06 report/review](../benchmarks/ANA-06-energy-balance-verification.md) and [ANA-07 sensitivity review](ANA-07-numerical-sensitivity-review.md) document four exact-source energy ledgers and per-case field/flux comparisons. The ledgers are separate supporting checks, not bundle-derived audits and do not apply to all 32 configurations. | P03 requires selected closed-form cases and their applicable balances; ANA-06 freezes one exact source setup for each B-03…B-06 family, while ANA-07 compares field components and flux for all 32 configurations. | No body-coupled field, momentum balance, force, or motion is available; no unsupported audit has been fabricated. The conclusion is limited to uncoupled ideal incident fields. | **Met for P3 scope:** no missing field-only audit applies to these recorded outputs. Body-level audits remain out of scope. |
| Numerical sensitivity and cancellation evidence is adequate | Sensitivity review covers 60/80-digit references, actual-argument math checks, kernel edge cases, and a one-ULP B04-EQUAL node probe. Both neighboring points pass the frozen tolerance. | Existing tests and unchanged frozen tolerance | Not an interval proof or bound for arbitrary inputs, platforms, geometries, solvers, or physical uncertainty | Evidence and owner-recorded decision: PASS for the tested software cases |
| Resource preflight and observed campaign cost stay within declared caps | Matrix report records maximum runtime `3.5012 s`, bundle size `111,491 bytes`, and RAM estimate `1,008,906,240 bytes` under the declared 4 GiB cap | ANA-07 contract caps | Measurements are for this environment and analytic recorder; they do not calibrate a numerical solver | Evidence reported within cap; no broader resource claim |
| Failures, warnings, and uncertainty remain visible | ANA-07 task, artifact review, and sensitivity review retain the earlier smoke-scope defect and rejected report-formatting attempt with their original records. ANA-05's earlier failed comparison remains documented in its task record. | D06/D07 preservation and provenance rules | Historical attempts are distinct from the successful frozen campaign | Records retained; reviewer should confirm relevant failure branches are adequately represented |
| Software quality checks are identified for the evidence revision | Full local Quality and exact-head remote Quality are recorded for campaign/replay source revisions; [Quality 37067239654](https://github.com/Andioratech/AURA/actions/runs/37067239654) passed for `1d6efb0`. Source, tests, workflow, and requirements are unchanged through `9ee66f7`. | Full workflow applies before committing; the run evidence must bind to the exact code revision. | No fresh CI is claimed for the current documentation-only checkout. The active `.venv` is unusable under user `aura`; this assessment used system Python 3.13.5 for read-only reanalysis. | **Met by recorded exact-source CI plus current deterministic artifact reanalysis.** A future commit still requires the full local workflow and current remote CI inspection. |

## Deterministic checks performed for this assessment

- Recomputed the SHA-256 of the matrix index and matched its retained sidecar: `d6352e8c929d22066c40dc55765f7334804a2d54d2ef10bb04fbc4c4166729d3`.
- Re-ran the current read-only ANA-07 analyzer across all 32 stored bundles. The checker verified each run manifest/input/output set; regenerated all 32 reports byte-for-byte equal to their saved reports and index hashes; all 32 returned integrity `VERIFIED` and numerical comparison `PASS` over 264 samples.
- Reproduced the global maxima from the index: pressure `9.020562075079397e-16`, velocity `7.940933880509066e-16`, gradient `7.599405318910162e-16`, and mean intensity `1.5881867761018131e-16`, all below `4.547473508864641e-13`.
- Rechecked both stored replay bundles with the read-only analyzer against their replay manifest hashes. B03-AXIAL and B06-AXIAL retain matching input hashes, all four field-artifact hashes, and comparison metrics; their report digests match the recorded values.
- Confirmed `physical_validation` remains `NOT_ESTABLISHED`. This review did not execute a physical experiment or promote a physical claim.

These are read-only checks over the immutable recorded bundles. They used system Python 3.13.5 because the checkout's `.venv` points into inaccessible `/root` storage. The original campaign and replay Quality evidence remains bound to the recorded CPython 3.12 source revisions; the reanalysis does not replace a fresh full Quality run.

## Separate scientific and software statuses

- **Software CI and verification:** ANA-07's recorded campaign and replay source revisions have passing local and exact remote Quality results as linked above. The 32-case campaign and both replays pass the recorded software criteria.
- **MCLF:** bundle integrity and input checks are recorded as verified. This does not constitute a higher-level physical MCLF acceptance; unsupported body-level rules remain outside the recorder's scope.
- **Numerical convergence and independent reference:** frozen analytic component comparisons pass. No discretized solver convergence result is claimed.
- **Experimental validation:** `NOT_ESTABLISHED`; no matched measurements or uncertainty evidence are present.
- **Reproduction:** B03-AXIAL and B06-AXIAL fresh replays pass exact recorded comparisons. Raw/indexed campaign data remain in the ignored local `results/` tree.
- **D03 completeness:** partial. Numerical backend, force/torque, dynamics, control and other MUST requirements remain open under their later gates.
- **D09 claims:** no general physical claim is promoted. No gravity generation, physical feasibility, water agreement, scale-up, or microgravity performance is established.

## Reviewer assessment and owner decision

The audit finds the P03 software-evidence criteria met within the declared ideal-field scope: the independent reference comparisons cover all frozen cases, one model-local balance is recorded for each analytical family, exact replay evidence is retained, and applicable resource/integrity checks pass. The ANA-06 ledgers are not generalized beyond their exact source configurations. No force, momentum-transfer, body-motion, experimental, or scale-up criterion is claimed as satisfied.

**Reviewer assessment:** PASS for P3 analytical software verification only. **Formal owner phase decision:** PASS, recorded from the owner's 2026-10-03 direction to continue development, limited to the recommendation's declared scope. ANA-07 is DONE for this bounded gate. Physical validation remains NOT ESTABLISHED. P4's NUM-01 may proceed because LIT-02 has supplied the exploratory SRC-W03 MQ1 geometry; its formal measurement benchmark status remains INDETERMINATE. This review does not select or implement a solver.

## Preservation and next trigger

The campaign index and local reproduction/sensitivity records remain immutable at the paths and hashes listed in the [ANA-07 record](../work-items/ANA-07.md) and [matrix report](../benchmarks/ANA-07-recorded-field-matrix.md). This assessment changes no run input, criterion, tolerance, or scientific claim.

## Follow-up checkout validation

After the initial read-only assessment, the VM's locked CPython 3.12.14 development environment was recreated. On 2026-10-03, the full local Quality workflow passed for the current workspace: hash-locked dependency installation, editable project installation, `pip check`, ENV-1.0 verification, Ruff, all 1,386 tests and the required-document checks. The run included a regression fix for same-size artifact rewrites on filesystems whose timestamp resolution does not expose the change; the new test and two-pass bounded hashing contract are documented in [content identity](../research/content-identity.md). This is software integrity evidence only and does not change the P3 scientific scope or recommendation. Remote CI inspected for the pre-change `HEAD` (`9ee66f7`) passed; no remote run exists yet for these uncommitted workspace changes.

At the time of this review, the next project task was NUM-01: compare candidate field methods for one explicitly exploratory domain, then present a bounded backend recommendation and its costs/limits before solver implementation. That comparison is now recorded in [the NUM-01 method decision brief](../research/NUM-01-method-comparison.md); the owner must choose the first solver/domain before implementation. The environment prerequisite for full local CI is satisfied. No numerical solver, force or motion implementation has started.
