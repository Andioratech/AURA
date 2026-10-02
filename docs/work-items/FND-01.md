# FND-01 — Convention Contract and Initial Code Review

**State:** DONE · **Date:** 2026-10-02 · **Role:** Implementation review; no independent physical review claimed

## Scope fixed before implementation

Parent work: P2.1 and P2.4; governing D02/D03/D08/D09; existing source inspected at `e4286b14f67c42f06f0948fd735bbe73327843f7`. Question: can every supported quantity, coordinate and pressure convention be interpreted unambiguously before field/force implementation?

This is a representation/source-review task, not a simulation. The primary criterion is complete convention/fixture coverage, including missing-input policy, geometry distinction and source-located equations. No physical performance threshold or unknown material input is assigned. Runtime scope: existing nine tests and bounded scalar diagnostics; no solver allocation, external data run, mesh or parameter sweep.

## Artifacts and decisions

- [CONV-1.0](../research/si-and-conventions.md): SI quantity objects, right-handed chamber coordinates, explicit gravity, geometry discriminator, peak/RMS and harmonic/attenuation conventions.
- [Equation register](../registers/equations.md): four existing helpers plus planned conversion conventions, primary source locators and domain limitations.
- [B01-v1.0 fixtures](../research/foundation-reference-values.md): independently derived values, numerical tolerance rationale and required rejection cases.

Reviewed these against D02's pressure/intensity restrictions, D03's SI/frame conventions, D08's no-default policy and DEC-004's larger-body objective. The review is an implementation self-review of definitions; it is not independent experimental validation or P2 PASS.

## Observed implementation gaps

Using the existing API in Python 3.12.14:

| Diagnostic | Observed result | Resolution task |
|---|---|---|
| `wavelength_m(True, 1)` | `1.0`; boolean silently treated as a speed | FND-03 helper strictness; FND-02 serialized boundary |
| `wavelength_m("343", 70)` | `4.9`; string silently converted | Same |
| `wavelength_m(1e308, 1e-308)` | `inf` | FND-03 numeric-result validation |
| Intensity with p = 1e200, rho = c = 1 | Raw `OverflowError` | FND-03 controlled numerical-domain diagnostic |

These observations are preserved rather than hidden by changing the inputs or tests. FND-02 may proceed because it implements a strict input contract independent of these helper coercions. Physical solvers remain unavailable. Existing test success does not cover the recorded gaps.

## Acceptance and next work

CONV-1.0 resolves the identified representational choices; the fixture/equation mappings exist and original helper limitations are explicit. FND-01 is closed as a design/review task. FND-02 is READY; P2 remains ACTIVE and its exit gate is incomplete. Full local CI and document-link review are required on the delivery commit, followed by the exact remote Actions check; commit/CI identity is available from Git history and the delivery report.
