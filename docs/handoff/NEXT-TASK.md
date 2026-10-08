# Next Task — Design an Independent Modal Reference for the Exact-Sphere CBIE

## Latest completed step — 2026-10-08

Clean ENV-1.0 runs at 179° and 14/16 subdivisions completed twice under the unchanged 120 s per-action cap. Their normalized CBIE residuals are `2.366765464132597e-7` and `2.005146001492107e-7`; full terms, repeat hashes, artifact hashes and interpretation are in [the formal review](../reviews/NUM03-BEM-exact-sphere-cbie-179deg-subdivision-14-16.md). The corresponding direct-layer changes remain around `2.1–2.3e-7 |p(x)|`, while the image-layer changes are around `2–4e-15 |p(x)|`. Thus the residual decline does not show that the direct terms have stabilized. The earlier 10/12/14/16 residual sequence is finite and follows a nonmonotone sequence at lower levels; it is not convergence or an error bound.

Stop this subdivision sequence. NUM-03 remains ACTIVE/INDETERMINATE; P4 is unpassed, the plan is DRAFT and BEM preflight is unauthorized. No matrix, solver or simulation core was started. The existing runs are numerical evaluations of one manufactured trace, not field acceptance, physical validation or gravity equivalence.

## Next bounded work item

Prepare a reviewable derivation and method plan for an independent spherical-harmonic/modal evaluation of the same manufactured sphere trace:

1. Read D00 and the relevant D01-D09 guidance before changing any scientific/software contract; review the NUM-03 exact-sphere CBIE evidence, existing reflected-monopole identity, and exact-sphere mode references.
2. Identify primary-source equations for the direct sphere layers and the reflected-source expansion. Verify equation numbers, sign and normal conventions, source location relative to the sphere, convergence domain, and truncation assumptions.
3. Derive separate modal expressions for the direct and image contributions and their sum at the boundary. Keep the 179° configuration as the first frozen case and propose a small set of additional angles only where the derivation supports them.
4. Specify an independent implementation route that does not call the current ring integrator. Define cutoff selection, truncation checks, arithmetic checks, exact repeat/provenance metadata, comparison metrics for every layer, and resource limits. Do not invent an acceptance tolerance from the existing residuals.
5. Cross-check the derived reference against known exact-sphere mode cases and the reflected-monopole analytic identity before comparing with the current quadrature results. Preserve disagreement and failed derivations as evidence.
6. Submit the equations, assumptions, sample set, checks and expected outputs as a plan for review before implementation. This planning step is not the P2 exit or permission to start the simulation core.

If the modal derivation cannot independently represent both direct and image terms for this geometry, document the exact obstacle and compare alternative independent formulations already present in the repository. Do not resume subdivision escalation just to make the residual smaller.

## Reproduction and checkout

The 14/16 records were produced from source revision `ca96183ee6782ef29207397f252848ce7fda4572` using Linux `ENV-1.0` and CPython 3.12.14. See the linked review for complete configuration, exact terms, validation and limits. Generated diagnostics and private AI instructions are local-only and must not be staged.
