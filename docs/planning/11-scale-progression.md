# 11 — Progression to Greater Masses and Larger Bodies

**Status:** Planned research track · **Authorities:** [DEC-004](../decisions/DEC-004-staged-mass-and-size-expansion.md), [DEC-005](../decisions/DEC-005-air-validation-route.md)

## Objective and relationship to the first campaign

AURA investigates controlled acoustic forcing and prescribed acceleration across explicitly selected body domains. Under DEC-006, the existing water-like analytical workflow is qualified first, followed by air field verification against the DEC-002 sphere benchmark. If air P4 passes, initial force/dynamics/control development proceeds in air. Small-particle water measurements remain a separate exploratory evidence campaign and do not validate the air route. Greater masses, larger dimensions and other shapes remain part of the research objective, with each step allowed to succeed, fail or remain unresolved.

The initial P2–P9 sequence builds reusable infrastructure and evidence for its first domain. Subsequent campaigns repeat the applicable model, numerical, force, dynamics, control and independent-evidence gates. Completion of one particle demonstrator does not close the overall scale question.

Air is the selected medium for the intended validation route; the water reference remains independent evidence for its own arrangement. A change of medium, enclosure or gravity environment is an explicit experiment dimension. Neither reference establishes support for the other domain or for larger bodies without the corresponding model and evidence.

## Progression dimensions

| Track | Controlled research change | Required gate question |
|---|---|---|
| S0 — Initial particles | One bounded particle/material/water configuration | Are the field, force and motion calculations verified and appropriately compared with measurements? |
| S1 — Greater mass | Increase mass through a sourced material or geometry change, documenting all accompanying property changes | Can the selected model and admissible actuation support the registered force/acceleration demand? |
| S2 — Larger dimensions | Increase body dimensions relative to wavelength, source and chamber while explicitly specifying material | Does the original approximation remain applicable, or is a new scattering/body-field model required and independently checked? |
| S3 — Other geometries | Introduce a specified shape, orientation and inertia description | Can force, torque, rotational behavior and relevant loading distribution be predicted and checked? |
| S4 — Supported operating domain | Compare reviewed body cases under bounded target, duration and environment conditions | What mass/size/shape combinations are supported, excluded for this target, outside the model or unresolved? |

These tracks are research dimensions, not guaranteed consecutive size classes. Mass is not a proxy for geometric size. Changing density/material at fixed dimensions can also change acoustic properties; record those changes rather than calling the comparison a pure mass effect. Do not assign gram, kilogram or centimeter targets before the candidate dossier establishes the question and evidence requirements.

## SC-01 — Register candidate mass, size and shape campaigns

**Initial state:** READY for research. **Inputs:** DEC-004, existing benchmark records and LIT-01 inventory when available.

1. List at least one candidate for greater mass and one for larger dimensions, with shape/material and medium clearly specified. Values may remain unresolved during this research task.
2. Search primary references for force/torque or acceleration evidence in each candidate regime; apply the source-verification procedure in [02](02-research-and-sources.md).
3. Record changed and held-fixed quantities, measurement gaps, source/array assumptions and candidate independent checks.
4. Prioritize a bounded next case by scientific information gained, applicability and compute/data availability. Keep rejected candidates and reasons.

**Artifacts:** `docs/research/scale-candidates.md`; parameter/source comparison; proposed next-case question. **Exit:** candidates and unknowns are reviewable without claiming feasibility. **Failure route:** F-02; finish with explicit evidence gaps and continue foundations.

## SC-02 — Establish whether a model change is needed

**Predecessor:** SC-01; use LIT-03/D04 methods as applicable to the candidate rather than assuming the particle equations apply.

1. Define the candidate's dimensions, wavelength relation, material response, source/body/wall separation and relevant approximation assumptions.
2. Review the required body-field interaction, force, torque and motion equations in primary literature. Select a suitable scattering, boundary or volume method only when justified by the question.
3. Define an overlap comparison where old and new approximations are both applicable, if such a domain exists. If none exists, identify separate independent benchmarks.
4. Specify the new model's inputs, supported outputs, error/uncertainty budget and compute preflight; record which earlier evidence remains reusable.

**Artifacts:** model-change decision; equation/applicability register; benchmark protocol; backend resource proposal. **Exit:** the new model has a defined verification route and no inherited unsupported validity. **Failure route:** D-03/D-04/F-03; retain the candidate as INDETERMINATE or select another justified case.

## SC-03 — Verify and compare the larger-body force calculation

**Predecessor:** SC-02 and applicable foundation/field gates for this candidate. No dependency on a favorable H-ACCEL result for a smaller particle is imposed.

1. Implement/configure the selected body geometry and model through the common interfaces; reject unsupported models and body types explicitly.
2. Verify field/body interaction, net force, available torque and any loading diagnostic required by the claim against independent calculations.
3. Complete observable convergence, boundary/control-volume checks and matched reference comparison under P3–P5/D06 rules.
4. Preserve the old benchmark unchanged. If data are incomplete, distinguish verified computation from incomplete model validation.

**Artifacts:** reviewed geometry/model adapter; reference fixtures; convergence/resource reports; candidate force gate. **Exit:** only the documented in-domain capability is promoted. **Failure route:** F-03/F-04/F-06/F-08; no artificial expansion of the particle model's range.

## SC-04 — Test force demand, acceleration and rotational behavior

**Predecessor:** SC-03 with required candidate force evidence gates satisfied, plus applicable P6–P7 gates or a recorded bounded subphase decision.

1. Register initial state, target acceleration, duration, workspace, body mass/inertia and complete force/torque accounting.
2. Reapply the necessary-condition screen before control tuning. Review pressure/power/thermal and actuator constraints with sources or explicit hypothetical labels.
3. Compare force availability, actual net acceleration, trajectory and orientation under the frozen protocol. Report spatial loading where the claim requires it; net acceleration alone does not close that question.
4. Keep desired, realized and admissible actuator demands distinct. Stop a target-specific attempt when a reviewed exclusion applies.

**Artifacts:** candidate dynamics/control evidence and target outcome; constraint/uncertainty report. **Exit:** the result states exactly what this mass/geometry can or cannot do under the tested assumptions. **Failure route:** D-07/D-08/F-07; distinguish controller failure from a physical/model-specific exclusion.

## SC-05 — Publish limits across the investigated scales

**Predecessor:** SC-04 outcome, or a reviewed earlier exclusion/indeterminate finding sufficient for a scoped limits report.

1. Map investigated mass, dimensions, shape/material, frequency, actuation, target/time window and gravity environment with evidence links.
2. Apply the relevant P8 attacks and P9 independent confirmation to claim-critical boundaries and favorable cases.
3. Label unsampled, outside-model, unresolved, supported and excluded-for-target cases separately. Do not infer a universal maximum mass from a finite unsuccessful search.
4. Record the next candidate, required model/data change or justified stop for the affected branch. An initial small-particle failure does not automatically refute a distinct larger-body hypothesis, and a success does not establish it.

**Artifacts:** scale-domain map; independent review; bounded claims and next-case decision. **Exit:** the scale question has a traceable restricted answer or an explicit unresolved boundary. **Failure route:** D-15/F-08/F-11; keep uncertainty and disagreement visible.

## Software consequences from the beginning

FND-02 must keep the canonical `Body` concept separate from the initial sphere model: geometry type/parameters, material properties, mass/inertia provenance and supported-model capabilities are explicit. A scalar radius is sufficient only for body models that declare that representation. Unsupported larger objects are rejected rather than converted silently into particles.

The first release implements its selected particle case. Future geometry/scattering/force adapters reuse scenario identity, resource preflight, runs, independent audits, comparison and reporting. See [03](03-software-build-map.md). This plans extensibility without requiring every solver before the first verified case.
