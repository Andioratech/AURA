# DEC-001: P0 Baseline Approval

**Date:** 2026-10-01
**Decision owner:** AURA project owner
**Decision:** PASS
**Approved source revision:** `8cbd2e2e50a17e96299fd00dbba667b5c3b24ed4`

## Decision

The project owner explicitly approved the controlled scientific baseline and PLAN-01 in the project session on 2026-10-01. P0 is therefore accepted as PASS, and phase P1 is authorized to begin under the gates and scope limits in PLAN-01.

The approval applies to D00-D09 and PLAN-01 as development contracts and phase governance. It does not validate AURA's physical hypothesis, establish feasibility, select a benchmark, approve a numerical tolerance, or authorize hardware work. G01-G05 remain DRAFT pending their own procedural review.

## P0 evidence reviewed

- The three unmodified source PDFs are archived with page counts and SHA-256 digests; all three digests verify against `references/source_documents/SHA256SUMS`.
- The project root is limited to documented entry points and tool configuration; maintained specifications and procedures are organized under `docs/` and `guides/`.
- Relative Markdown links resolve, the required-document checks pass, Ruff passes, and the available test suite passes.
- CodeGraph 1.6.1 is installed and configured locally; its index and machine-specific client configuration remain excluded from Git.
- A fresh clone of the configured GitHub remote was clean. The configured Git author and committer matched the project owner's identity, and remote CI passed for the P0 validation update.

## Authorization and next action

Authorized next work item: P1.1, assemble a sourced dossier of two or three published benchmark candidates with parameters, observables, reported reference values, uncertainty, and missing data. No benchmark is selected by this decision. Continue to block solver implementation until the P1 exit gate is met.
