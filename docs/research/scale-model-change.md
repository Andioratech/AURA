# SC-02 — Model Change for the Large Rigid-Body Candidate

**Prepared:** 2026-10-03 · **Status:** literature-based model-change decision; no implementation selected or authorized · **Candidate domain:** Inoue et al. (2019) air / 40 kHz / approximately 50-mm EPS octahedron, for applicability analysis only

## Decision

The small-sphere particle-force formulations reviewed in LIT-03 are not transferable to the approximately 50-mm, `ka ≈ 18.5` octahedron case. The wavelength is reported as 8.5 mm; the characteristic ratio `50 mm / 8.5 mm ≈ 5.9` is based on the octahedron's diagonal and is descriptive rather than a shape-independent `ka`. The scattering body materially changes the field, and the target is non-spherical. A surface-resolved rigid-body scattering formulation that returns both net force and torque is therefore required for this candidate class.

The published boundary-element method (BEM) of Inoue et al. is a **candidate formulation for a separately reviewed future model contract**, not an AURA model selection or validation. Its primary source derives the scattered pressure with a Kirchhoff–Helmholtz boundary integral, discretizes the body and array, then integrates time-averaged radiation loading over the body surface to obtain force and moment (Eqs. 1–13). The authors report sound-hard boundary, neglect of air viscosity, neglect of re-reflection at the transducers, constant transducer amplitudes during phase optimization, and finite stable-region behavior. The study observed force-model discrepancy for its sphere and did not directly measure octahedron torque. The boundary impedance assumption alone is sufficient to prevent treating it as a validated EPS model.

This review applies only to studying a rigid, acoustically scattering body with dimensions comparable to or larger than wavelength. Under later [DEC-005](../decisions/DEC-005-air-validation-route.md), AURA selected air for its intended validation route; that does not change this review's candidate-only status, select a material or operating point, or authorize a simulation implementation. The water-particle evidence campaign remains separate.

## Why the particle model does not transfer

LIT-03 reviewed small-sphere viscous and thermoviscous expressions whose derivations assume the sphere is small relative to wavelength and encode sphere-specific material response. Their use of a background field without body-resolved scattering does not represent the published octahedron case: Inoue et al. explicitly show that field with and without the body differs substantially, especially for the octahedron. A scalar-radius/Gor'kov particle model also has no representation for orientation-dependent torque on a faceted body.

The necessary model change is at least: (1) solve incident-plus-scattered pressure on the declared body boundary; (2) use a boundary condition justified for the selected material/medium; (3) compute force and moment with a consistent time-averaged momentum or radiation-stress balance; (4) resolve body pose and orientation; and (5) include losses or explicitly limit claims to the lossless/inviscid model. This does not imply that one BEM implementation is sufficient for water, lossy materials, near walls, close source coupling or moving-body transients.

## Candidate formulation and source boundary

Inoue et al. (2019), [journal DOI](https://doi.org/10.1121/1.5087130), [open author preprint](https://arxiv.org/abs/1708.05988) derive the scattered field and sound-hard boundary integral in Eqs. (8)–(11), with discrete force and torque in Eqs. (12)–(13). Their continuous formulation expresses force as a time-averaged surface integral of acoustic Lagrangian and momentum-flux terms (Eq. 1), with torque obtained from the lever arm about the center of mass (Eq. 6). The paper's static restoring/stability calculation linearizes generalized force around a levitation equilibrium (Eqs. 14–16); it is not an arbitrary prescribed-acceleration trajectory solver.

Potential independent sphere references include exact partial-wave calculations for rigid or elastic spheres under declared incident fields. Silva et al., [“Exact computations of the acoustic radiation force on a sphere using the translational addition theorem”](https://arxiv.org/abs/1210.2116), describe arbitrary-beam sphere forces using partial-wave coefficients; Zhang et al., [“Radiation force of an arbitrary acoustic beam on an elastic sphere in a fluid”](https://pmc.ncbi.nlm.nih.gov/articles/PMC3574112/), provide an independent analytical sphere formulation. These can check a spherical BEM reduction only after aligning boundary condition, medium, incident field, amplitude convention and losses. A sphere check does not by itself validate a polyhedral body.

## Proposed verification and comparison protocol

No numerical tolerances or resource limits are frozen here. Before any later run:

1. Define an immutable sphere and octahedron geometry, material boundary condition, medium properties, incident field, array representation and exact quantity of interest. Preserve the published air case as a distinct reproduction target; do not reinterpret it as AURA evidence.
2. Check zero drive, rigid-body symmetries, force/torque sign conventions and rotation/translation covariance. A symmetric sphere under a symmetric incident field supplies a force/torque sanity case.
3. Refine body-surface discretization through at least three levels and track complex surface pressure, net force, net torque and the local generalized-force Jacobian. Freeze a tolerance from a measurement/reference uncertainty budget before evaluating acceptance. The paper reports a mesh study and force comparisons, but its reported mesh observation is not automatically an AURA tolerance.
4. Compare a spherical subcase independently against a partial-wave result under matched inviscid/sound-hard assumptions, first in any justified common small-`ka` domain and then at larger `ka`. Treat this as a verification overlap, not physical validation.
5. Compare force-displacement for the source's octahedron/sphere cases against digitized paper figures only as a reproduction check. The plotted measurement lacks a fully documented uncertainty package in the retained AURA record; digitization spread cannot substitute for that uncertainty, so formal measurement acceptance remains INDETERMINATE.
6. Audit force and torque with an independently derived momentum-flux surface enclosing the body, with the control surface, scattered field, time averaging and outer-boundary treatment declared. This check must not reuse the same discretized body-surface stress code.
7. Treat stability, open-loop field quality, and later closed-loop acceleration tracking as separate observables. The reported local restoring-force region and 50–144 s levitation durations in the paper do not show a predeclared acceleration target or robust gravity-like field.

## Overlap, limits and blocked branches

An overlap with a small-particle formula is defensible only for a rigid sphere and a matched ideal medium/field/boundary branch where both derivations apply. For example, a sound-hard sphere in an inviscid medium with `ka << 1` can support a bounded asymptotic-versus-partial-wave comparison. This is not a bridge from an EPS octahedron in air to the water thermoviscous particle case. If a shared boundary/material regime cannot be specified, use separate analytical references rather than claiming overlap.

| Proposed branch | Status | Reason / re-entry condition |
|---|---|---|
| BEM model contract for air EPS octahedron | CANDIDATE / INDETERMINATE | Requires surface-impedance evidence, measured geometry and full uncertainty; define a matched field case first. |
| Water rigid-body or deformable-object model | NOT SELECTED | Water medium, object material, geometry, boundary, streaming and thermal coupling differ; start from a separately scoped source review. |
| Numerical body-scattering implementation | NOT AUTHORIZED HERE | P3 PASS covers only the ideal analytical-software gate; the P4 backend/resource gates and applicable force-model contract remain open, and the simulation-core explanation checkpoint applies. |
| Acceleration or gravity-equivalence study | NOT READY | Requires force evidence, complete dynamics, target body/trajectory/time/workspace, actuator set and a separate operational definition/acceptance protocol. |

## Compute and data planning

The body mesh and number of transducers define a dense coupling problem in the published BEM style. No unprofiled RAM/time claim is made. A future backend proposal should bound body facets, source elements, matrix precision, factorization or iterative method, cache/temporary storage, convergence levels, worst-case runtime and peak memory before allocation; resource estimates must be verified against the actual selected method. Raw measured surface pressure, force sensor calibration, drive phase/amplitude records, specimen impedance and measurement uncertainty were not found in the retained sources.

## Records and claims

No equation-register status is promoted by this review. EQ-013–015 remain particle-model literature records, not rigid-body BEM validation. No software verification, model validation, measurement acceptance, experiment or novelty clearance is claimed. Reopen this decision if the candidate, medium, boundary material, array, operating frequency or output claim changes.
