# Project Continuity — Start Here

**Updated:** 2026-10-06. The exact-source half-space CBIE sphere check at `theta=175°` has residuals `3.58965e-4`, `7.02808e-6`, `1.77906e-6` at meridian orders 64/128/256. A separate equatorial HBIE check has residuals `4.17641e-5`, `5.21520e-6`, `6.51563e-7` across direct azimuth counts 256/512/1,024; meridian orders 32/64/128 stabilize near `6.52e-7`. Wu et al. Eq. (14) gives `R_CBIE+(i/k)R_HBIE` for left-minus-right residuals. A transient assertion failure at the unapproved `1e-6` screen is preserved. The retained equatorial manufactured-field control stabilizes near `1.22e-6` under the tested refinements; this does not validate a general operator or AURA field. The corrected `theta=135°` HBIE control subtracts/restores only the constant collocation Cauchy density and gives residuals `7.12466e-6`, `1.93304e-6` and `6.35112e-7` at meridian orders 128/256/512. The earlier `0.374` prototype double-counted variable density and remains preserved as a failed implementation. Next test a second collocation angle and independently check the image term. Existing ring, panel and exact free-space sphere checks remain bounded component evidence, not error bounds or AURA field validation. Hasegawa remains selected for P4; NUM-03 stays ACTIVE / INDETERMINATE, its plan DRAFT, and the public matrix paused. See [kernel foundation](../research/NUM-03-bem-kernel-foundation.md), [current state](CURRENT-STATE.md), and [next task](NEXT-TASK.md).

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
