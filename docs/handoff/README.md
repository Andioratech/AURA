# Project Continuity — Start Here

**Updated:** 2026-10-05. The latest bounded result is the 300-gap source-coefficient Simpson-remainder enclosure for modes 8–19 plus the combined n=20 and global n=21–32 coefficient bounds; n=32 also has full 300-gap interval enclosures; see [current state](CURRENT-STATE.md), [next task](NEXT-TASK.md), and the NUM-03 protocol/review linked there. This result remains coefficient-only and changes no science gate.

**Purpose:** Resume AURA from repository evidence without depending on a particular assistant, model or chat history.

This is a navigation and continuity layer. [D00](../D00-document-control.md) controls scientific precedence; [the work board](../planning/10-work-board.md) controls task status, with the linked reviews as evidence. This folder does not replace either. Maintained project text is English; explain results and decisions to the owner in plain Spanish.

## Reading order

| Order | Read | Establish before acting |
|---|---|---|
| 1 | [Current checkpoint](CURRENT-STATE.md) | What exists, what was verified, what remains unvalidated and the source revision |
| 2 | [D00](../D00-document-control.md), [decisions](CURRENT-STATE.md#decisions-that-must-survive-a-handoff) and [scale progression](../planning/11-scale-progression.md) | Approved scope and scientific limits |
| 3 | [Work board](../planning/10-work-board.md), [execution rules](../planning/00-execution-protocol.md), [phase card](../planning/phases/P01-evidence.md) | Current task, predecessors and acceptance gate |
| 4 | [Latest research-artifact review](../reviews/FIG-W03-MQ1-profile-extraction.md), [water-reference record](../benchmarks/water-reference-selection.md), and [RUN-02 replay review](../reviews/RUN-02-replay-report.md) | Recent data-access/extraction evidence, replay evidence, failed attempts and retained limitations |
| 5 | [Next task briefing](NEXT-TASK.md) and its linked contracts | The earliest READY work item after reconciling the board, gates and evidence |
| 6 | [Environment](../../requirements/README.md), [reproduction and CI](../planning/08-reproducibility-and-ci.md), [G01](../../guides/G01-contributor-workflow.md) | How to install, verify, commit and publish safely |

On the owner's machine, also read the **local, ignored** `AGENTS.md` and `AI-HANDOFF.md` if provided. They contain owner instructions and machine-specific checkout/evidence/dashboard locations. A clone of GitHub will not contain those files, the local dashboard or ignored raw reports. Ask for the local transfer pack only when those missing materials are required for the intended action; independent authorized work can continue under DEC-003.

## Startup reconciliation

Before edits, inspect the actual working directory, Git root, history, branch, remote, dirty files and configured identity. A `.git` directory alone does not prove the checkout contains published history. Preserve local changes; do not initialize a new history, reset files or overwrite a work copy to make it resemble this snapshot.

```sh
git rev-parse --show-toplevel
git rev-parse --verify HEAD
git status --short
git log -5 --oneline
git remote -v
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
```

Compare actual HEAD with the checkpoint revision and subsequent commits. If the repository has advanced, read the newer task records/reviews and update this checkpoint; do not roll back to its date. If the board, review and code disagree, record the mismatch and resolve the affected state from evidence before changing scientific status. Historical reports retain their original dates, counts and conclusions.

Read `.github/workflows/quality.yml` from the actual checkout and inspect the exact latest remote CI. Follow the current workflow before every commit, even for documentation-only changes. A past PASS is not a check of new changes. Follow the existing owner-identity restriction; never add an AI author, committer or co-author credit. No private instruction file, generated report, credential or navigation index belongs in a commit.

## Context confirmation

A newly joining collaborator should be able to state, with document links:

1. The objective and why particle work does not decide all future mass/size regimes.
2. The last completed task and the exact scope of its evidence.
3. Which phase gate is still open and why green CI does not close it.
4. The next main implementation task, its inputs, outputs, acceptance and failure branch.
5. Which checkout actually contains history and where the raw evidence can be found.
6. Which decisions require new evidence or owner intervention, and which routine work is already authorized.

If any answer is unknown, consult the linked source of truth. Never reconstruct approvals, results or parameter values from guesswork. Reading a handoff is not an instruction to begin a new task; follow the owner's current request.

## Maintaining continuity

At each completed task or material change:

- Update the task record and artifact review with actual results, failure history, limits and exact code/CI/evidence references.
- Update the board, phase card, requirement/equation traceability and README capability text.
- Refresh CURRENT-STATE and NEXT-TASK. Keep old evidence immutable; identify the new checkpoint's code revision and date.
- Refresh the local operations note if checkout, environment, service or evidence locations change. Keep it ignored.
- Refresh any transfer pack with a new immutable identifier and checksums. A Git bundle or archive is a snapshot, not a live synchronized replica.
- Verify internal links, status consistency, full current local CI, owner identity, intended staged files and exact remote CI before declaring delivery.

No scientific claim or gate is strengthened by the act of transferring context.
