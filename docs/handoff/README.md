# Project Continuity — Start Here

**Current checkpoint — 2026-10-07:** The BEM fallback now has a bounded exact-sphere meridian quadrature primitive, covered by 9 focused and 1,803 full-workflow passing tests. The first workflow attempt exposed and corrected two preflight import failures. Start with [current state](CURRENT-STATE.md), then follow [next task](NEXT-TASK.md); the Hasegawa P4 backend remains selected and NUM-03 remains INDETERMINATE.


**NUM-03 mirror-mode remainder bound — 2026-10-07:** For a centered monopole and the fixed sphere case (`a=25 mm`, `gap=0.1 mm`, `f=25,230 Hz`, `c=346 m/s`), the exact image Green expansion tail after order `N` is bounded by `B_N=[1/(12D)] exp(z+x²/(2(2N+5))) q^(N+1)/(1-q)`, with `D=2(a+gap)`, `q=a/D`, `x=k_upper a`, `z=k_upper D`, and `k_upper=(44/7)f/c`. The derivation uses DLMF §§10.53.1, 10.49(i), 10.60(i), and the real-angle Legendre bound. Rational inputs and outward-rounded Decimal evaluation give `B_48=9.09943933485362e-5 m^-1`, `B_64=1.11397254106508e-9 m^-1`, and `B_80=1.44903668349673e-14 m^-1`. At order 80, the independently evaluated binary64 series differs from the exact image Green value by `2.91e-15 m^-1` at 120° and `2.93e-15 m^-1` at 135°. The analytic bound is uniform over real surface angles for this configuration and every nonnegative cutoff; it does not bound floating-point evaluation, quadrature, a matrix solve, other parameter values, or physical behavior. Focused test: 2 passed. Local-only record `NUM03-BEM-MIRROR-TAIL-BOUND-20261007-01`, SHA-256 `cfb893fddc06e1f084fa0d26c65e98e50eeb25a52499c64be17cc5505cbadef2`. No solver matrix or core was started.

**Updated:** 2026-10-07.

For the direct free-space sphere control (`a=17 mm`, `ka=2.3`, sphere-center height `2a`), the singular-panel single- and double-layer operators and the combined CBIE were checked for zonal outgoing modes `n=0,1` at `theta=120°` and `135°`. The reference eigenvalues are Kreuzer (2024), Eqs. (1), (4)–(5), [DOI 10.1016/j.enganabound.2024.105883](https://doi.org/10.1016/j.enganabound.2024.105883), with printed kernel `G=exp(i k r)/(4 pi r)`. Mapping the paper's sphere-outward normal to AURA's normal into the sphere gives the explicit identity `0.5 phi + K_AURA(phi) - V(d phi/dn_AURA)=0`; the half-jump is kept separate from the principal-value layer. Meridian Gauss orders 16/32/64 and 1,024 ring azimuth samples use explicit logarithmic subtraction/restoration. All four cases show decreasing CBIE residuals across refinement; order-64 residuals normalized by the boundary-mode amplitude are `2.02e-9` and `2.59e-8` at 120° (`n=0,1`), and `1.14e-8` and `1.35e-8` at 135° (`n=0,1`). The individual layer eigenvalue comparisons pass, and the singular test file passes 20/20. An initial combined harness double-applied the angular `P1` factor to the normal derivative; the failed screen is retained locally (SHA-256 `1196458d1b57efc12f6b01c75bf98f78e7f0158657a87e8fa3b91b52c5d0fa8c`) and no threshold was relaxed. Local component record SHA-256 `a9a3eb2e508d5c17453cda2637f0633be5501787f13ad10656044f073cdf4602`. The full local Quality workflow passes all 1,792 tests, including locked installation, editable installation, `pip check`, ENV-1.0, Ruff, required-document checks and `git diff --check`. This is a finite-grid direct free-space control only; it does not validate image terms, a complete half-space BIE, a matrix, general geometry or AURA's physical field.

**Independent off-equator image CBIE check — 2026-10-06:** On a `25 mm` sphere with a `0.1 mm` plane gap, a unit monopole at the sphere center and field angles `120°`/`135°`, the image-layer contribution `K_image(phi) - V_image(dphi/dn_AURA)` was evaluated by ring reduction and independent pointwise full-surface quadrature. For these boundary traces from the Neumann half-space Green function, both routes match the exact image-source value `-G(x, y_image)`; the largest absolute route-to-reference discrepancy is `6.3e-15`, and the largest layer-component disagreement between routes is `5.7e-14`. The compared grid uses meridian Gauss order 64, ring azimuth counts 1,024/2,048 and full-surface azimuth count 4,096; the established `2e-8` relative / `1e-5` absolute screen remains unchanged. Local record SHA-256 `cb798d870406424f1e07629d100bea6ee617b9e14e9875b81bee920fe6630cd5`. This verifies the smooth image CBIE component only; it is not a complete half-space solve, a general quadrature error bound or physical validation.

**Independent mirror-mode CBIE cancellation check — 2026-10-06:** The regular expansion of the reflected monopole was tested at `a=25 mm`, `gap=0.1 mm`, `f=25,230 Hz`, `c=346 m/s`, and `theta=120°`/`135°`. Combining [DLMF §10.60(i), Eqs. 10.60.1–2](https://dlmf.nist.gov/10.60) gives `G_image = i k/(4 pi) sum_n (2n+1) j_n(ka) h_n^(1)(kD) (-1)^n P_n(cos(theta))`, with `D=2(a+gap)` and `a<D`. Kreuzer's exact sphere layer eigenvalues (2024, Eqs. 4–5, [DOI 10.1016/j.enganabound.2024.105883](https://doi.org/10.1016/j.enganabound.2024.105883)) show each regular mode's direct CBIE response equals its boundary trace; the independently checked image contribution is `-G_image`. At cutoff `N=48`, the modal pressure differs from the exact image Green value by `2.48e-15` (`120°`) and `5.09e-15` (`135°`); each mode's direct-response/trace discrepancy is at most `2.84e-16`, and the direct-plus-image CBIE cancellation residuals are `2.34e-15` and `5.06e-15`. At `N=32`, image-pressure differences are `8.38e-10` and `7.48e-10`; these finite truncation comparisons are not a general remainder bound. Local record SHA-256 `b20886ce69b76977242cf5e1b035247ab46abd555d5b772a4fd28d6615d63179`. This verifies an analytic modal decomposition for this geometry and frequency only; it is not a discretized half-space solve or physical validation.

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
