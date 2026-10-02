# Frozen Experiment Protocol Template

Create under `experiments/<experiment-id>/` only when a real experiment definition is ready. A planning task/benchmark label is not an assigned run ID. All runs reference an immutable protocol revision.

## Question, domain and competing outcomes

- Experiment ID / version / date / parent claim and task:
- Exact hypothesis with existential/universal and nominal/robust quantifiers:
- Competing model/explanation and outcome that would distinguish it:
- Body/material/size distribution, water composition/temperature/properties:
- Chamber/source configuration, amplitude convention, frequency and limits:
- Boundary/model/solver equations and applicability; omitted terms:
- Initial state, reference frame, gravity/residual environment, duration:
- Target function, workspace and evaluation window:

## Inputs and evidence

| Input | SI value/range | Source locator | Measured/fitted/assumed/manufactured | Uncertainty | Resolution task if unknown |
|---|---|---|---|---|---|
| Populate every needed physical/numerical input | | | | | |

- Calibration data and held-out evaluation data, with hashes:
- Reference observable and domain matching table:
- Independent checks and numerical refinement design (at least three critical levels):
- Primary metric, units, formula, sampling/filter and normalization:
- PASS/FAIL/INDETERMINATE rule and justified tolerance:
- Numerical/parameter/model/measurement/digitization uncertainty treatment:
- Seed stream map, study design, sample count and statistical assumptions:
- Resource estimate/caps, timeout, event/domain and anomaly stop rules:

## Execution and preservation

Exact command/interface, source/environment identity, immutable output layout, partial-failure retention, expected files, metadata/checksums, plotting conventions, comparison method and independent replay procedure.

## Freeze and change control

Reviewer/date and authorized scope; configuration/protocol hash; unresolved evidence restrictions. Changes after seeing outcomes create a new version/experiment as applicable and preserve prior values, reasons and results. Do not change the primary metric or tolerance retrospectively.
