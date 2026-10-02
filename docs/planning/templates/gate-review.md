# Phase Gate Review Template

Copy into `docs/reviews/<phase>-<review-id>.md`. A phase checklist is not an approval; fill with actual evidence and attributed decisions.

## Review identity

Phase/gate ID; date; scope/domain; baseline/plan revision; source commit; preparer; reviewer role/person; relevant decision records.

## Evidence table

| Criterion from phase exit | Artifact/run/commit | Measured value or finding | Threshold and derivation | Uncertainty/limitations | Met / not met / indeterminate |
|---|---|---|---|---|---|
| One row per mandatory criterion | | | | | |

## Separate statuses

- Software CI and verification result, exact commit/run link:
- MCLF pre/post verdicts with unresolved rules:
- Numerical convergence and independent reference outcome:
- Experimental validation outcome and missing measurement evidence:
- Reproduction outcome and availability of raw/source data:
- D03 requirement completeness and unresolved MUST rows:
- D09 claim statuses and forbidden extrapolations:

## Decision

PASS / FAIL / HOLD / INDETERMINATE, with a concrete explanation. Name allowed next tasks and forbidden dependent claims. For FAIL/INDETERMINATE, reference a decision branch and recovery playbook, assign exact follow-up artifacts and re-entry condition. Record actual reviewer/owner decision where required; no response is not approval.

## Record preservation

Retained failed runs and negative evidence; artifact/manifest hashes; superseded documents; current limitations; board updates and next review trigger.
