# Next Task — Complete the Bounded Modal Reference Check

## Latest completed step — 2026-10-09

The owner authorized the bounded, research-only evaluator in the DRAFT plan. It reports four layer terms, all modal contributions, pressure and inward-normal derivative traces, cancellation, and combined residual for orders 48/64/80 and angles 120°/135°/175°/179°. It imports the existing special-function recurrence but no ring quadrature. A new 80-digit Decimal calculator gives preliminary candidate tail bounds for all four layers; its mathematical inequalities still need independent review, and it does not bound binary64 evaluation error.

Focused checks pass (12 modal cases across the frozen angles/cutoffs). GitHub Quality run [37940716094](https://github.com/Andioratech/AURA/actions/runs/37940716094) also passes on exact commit `10ca10eaf8b084667ec60426cfe37c9d5353a0e8` after correcting the hosted test import path; its full run took 27m55s. A separate 100-digit Decimal calculation at 179°/N=80 independently evaluates the special functions and four layer sums. Absolute differences from binary64 are `3.88e-16`, `7.37e-15`, `6.00e-15`, and `3.40e-15 Pa` for direct K, direct V, image K, and image V. The first Decimal attempt had a cosine quadrant-sign error; it is preserved with the corrected local record and is not used as evidence. The 179° comparison with the recorded ring case retains the previously observed direct-layer differences near `7.2e-7` and `7.9e-7 Pa`, while image-layer differences remain below `2e-14 Pa` at N=80.

The clean committed protocol was replayed with identical case payload SHA-256 `a17d1ad56c84c8508676415dcad3f6a0699ea5ed6aef268c135a855dc223f980`. At N=80 preliminary direct K/V tail bounds are `2.56e-10`/`1.28e-10 Pa`; each image-layer bound is `7.21e-11 Pa`. Remote Quality is complete. Next obtain independent mathematical review of all four majorants and the Decimal recurrence. If they hold, the direct modal truncation estimate is much smaller than the ring/modal difference, which narrows but does not resolve the cause. See the [formal review](../reviews/NUM03-modal-reference.md) for exact record hashes and limits. This remains cross-verification only; no cutoff is selected and NUM-03 stays ACTIVE/INDETERMINATE.

On 2026-10-09 the owner authorized the bounded research-only modal evaluator described in the DRAFT plan. This is not P2 exit, P4 approval, cutoff acceptance, or authorization to start the simulation core.

## Authorized bounded work

The evaluator is restricted to the frozen exact-sphere case and cutoffs 48/64/80. It reports direct `K`, direct `V`, image `K`, image `V`, the half-pressure jump, modal traces, termwise sums, cancellation indicators and the combined residual. Only the image-layer tails have the recorded analytical upper bound; direct-layer truncation remains finite-cutoff sensitivity. No matrix, solver or simulation core is in scope.

## Scope and current gate

The starting case is the manufactured exact-sphere trace (`a=25 mm`, `g=0.1 mm`, `f=25,230 Hz`, `c=346 m/s`) at 179°, then 120°/135°/175° if the bound supports them. This is numerical cross-verification only. NUM-03 stays ACTIVE/INDETERMINATE; P4 is unpassed, the reference plan DRAFT and BEM preflight unauthorized.
