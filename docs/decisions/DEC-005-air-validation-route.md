# DEC-005: Air as the Intended Validation Medium and P4 Route

**Status:** RECORDED OWNER DECISION · **Date:** 2026-10-03 · **Owner:** AURA project owner

## Request and evidence

During the NUM-01 route choice, the owner stated that AURA should ultimately validate the idea in air. This resolves the medium/sequence conflict between DEC-002 and DEC-004 for the first numerical solver path. PLAN-01 §P4.1 requires the method to match the P1 benchmark; DEC-002 identifies the 50 mm expanded-polystyrene sphere and single-transducer force-versus-gap case in air. DEC-004 had placed small particles in water first in the implementation sequence.

The two evidence cases remain distinct. The approved air benchmark has a measured force curve but no retained pointwise experimental uncertainty; formal force acceptance remains INDETERMINATE. The SRC-W03/MQ1 water reference has figure-derived particle-velocity profiles but lacks original arrays and a complete measurement/calibration uncertainty budget; it also does not directly measure force or acceleration. Neither case establishes acoustic pseudogravity.

## Decision

1. Use air as the intended medium for AURA's eventual validation route and align P4 with the DEC-002 air benchmark rather than beginning P4 with the manufactured water eigenmode.
2. The first bounded P4 field question is limited to the declared air source/sphere geometry: a nominal 50 mm, 1.46 g expanded-polystyrene sphere, one nominal 25.23 kHz transducer with a 20 mm radiating face, and the published gap range. The field model's source boundary, sphere boundary, fluid properties and gaps must be frozen in NUM-01 before preflight or execution.
3. This updates DEC-004's implementation ordering only where it made water the first solver campaign. The water-particle research and evidence track remains in the project, as do greater-mass, larger-body and other-geometry investigations. Water results cannot validate or substitute for the air route, and air results cannot validate the water reference.
4. This decision selects a medium and route, not an acceleration target, final body for an acceleration trial, array/controller, air state, gravity environment, residual-gravity limit, target tolerance, solver backend, or hardware design. In particular, air does not by itself specify whether the eventual test occurs at Earth gravity or under a microgravity/residual-gravity condition.
5. P4 verifies field numerics only. It does not establish force-model validity, acceleration tracking, uniform response across bodies, gravity equivalence, feasibility, or a pseudogravity claim. The P1.3 force comparison remains INDETERMINATE unless suitable measurement uncertainty or independent evidence is obtained.

## Options considered

| Option | Scientific benefit | Limitation / consequence | Decision |
|---|---|---|---|
| Retain water as the first P4 solver | Directly serves the original tractable water campaign and permits a manufactured mode check | Does not match PLAN-01 §P4.1's P1 benchmark and cannot serve the owner's stated intended validation medium | Not selected for the first solver route; water evidence track retained |
| Align P4 with the air benchmark | Makes the numerical sequence relevant to the intended validation medium and preserves PLAN-01's benchmark-matching rule | Requires a sphere/source field formulation; published force uncertainty is incomplete; it does not yet define the acceleration claim | Selected |
| Defer or replace the domain | Avoids choosing a solver before required evidence is available | Delays numerical progress; a replacement requires a new bounded question and reference | Not selected; remains a recovery route if NUM-01 cannot establish a verifiable field domain |

## Consequences and re-entry

- PLAN-01 advances to v1.4; v1.3 is retained unchanged in `docs/archive/`.
- D01, the objective/domain contract, NUM-01, P04, the work board and continuity documents are aligned with this decision. D03 acceptance criteria, MCLF rules, uncertainty standards, equations and past results are unchanged.
- NUM-01 remains ACTIVE until one air-field method, boundary/source assumptions, discriminating references and interface contract are specified. NUM-02 resource preflight and NUM-03 field-core implementation remain gated behind that review.
- Before implementation of the numerical field core, the owner receives the required explanation of components, inputs, outputs, verification cases and limitations.
- Reconsider the selected route only if the air source/sphere field cannot be represented or independently verified within a defensible resource envelope, or if new owner direction changes the intended medium. Preserve all prior water and air evidence under their original scope.

## Subsequent NUM-01 disposition — 2026-10-03

Following this route decision, NUM-01 selected numerical evaluation of Hasegawa et al.'s 1985 centered baffled-piston/rigid-sphere harmonic series as the first P4 method, limited to the stationary sound-hard sphere branch. This is a method selection, not a claim that the series is convergent or resource-feasible at AURA parameters. NUM-02 must establish stability, truncation, convergence and resource bounds before any field-core implementation or run. If those checks fail, retain the evidence and reopen the method comparison; the owner-selected air route remains unchanged unless the field question itself cannot be verified.

This disposition selects the medium and method for P4 only. DEC-004 and the current P5/P6 cards still describe a water-particle starting campaign. Before crossing from the air P4 result into P5/P6, reconcile whether the initial force/dynamics sequence also moves to the DEC-002 air sphere or whether water remains the first force/dynamics campaign with its own field prerequisite. Do not silently use an air P4 field result as verification for water.

## Current sequencing clarification — DEC-006

[DEC-006](DEC-006-water-qualification-before-air-route.md) supersedes the preceding unresolved phase-order statement: first audit and qualify the existing water numerical workflow within the scope of its actual evidence, then execute the selected air P4 field route. If air P4 passes, initial P5 onward remains in air. DEC-005's air domain and Hasegawa method selection remain current. Its historical rejection of a water-first air-solver route does not reject the narrower water software-qualification step; no cross-medium physical validation is implied.
