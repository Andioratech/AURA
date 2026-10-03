# 01 — Scientific Objective, Domain and Claim Contract

## Program objective and first operational question

The program investigates whether controlled acoustic forcing can produce a prescribed acceleration for selected bodies across explicitly investigated mass, size and geometry domains, toward microgravity operation. Under [DEC-006](../decisions/DEC-006-water-qualification-before-air-route.md), first reconcile water numerical-workflow evidence, then verify the air field route selected in [DEC-005](../decisions/DEC-005-air-validation-route.md) against the DEC-002 sphere/transducer reference. If air P4 passes, the initial force/dynamics/control route remains in air. The water-particle evidence remains a distinct research campaign and does not validate the air case. Greater masses and other body geometries remain explicit objectives under [DEC-004](../decisions/DEC-004-staged-mass-and-size-expansion.md); follow [11](11-scale-progression.md) for transitions.

The first operational question is:

For the DEC-002 sphere/transducer case in air, can an independently checked field and force model support a later, separately frozen acceleration-target trial in the owner-selected air validation medium? P4 first addresses only acoustic-field computation; force, body dynamics, target acceleration and gravity environment remain later gates.

The long-term environment is microgravity. Earth-gravity comparisons are development controls. Setting a gravity vector to zero is a modeled idealization; it is not evidence about a real flight environment. AURA remains an unvalidated hypothesis.

The hypothesis table and domain fields below describe the initial campaign. For each larger-body campaign, register new body/model-specific instances of these hypotheses, include torque/orientation/loading observables when required, and repeat the relevant evidence gates. Neither success nor failure of the initial particle case determines all other scales.

## Hypothesis hierarchy

| ID | Bounded statement to register | First discriminating result | May support |
|---|---|---|---|
| H-FIELD | The declared field model predicts pressure/velocity observables within its frozen numerical budget | Analytical comparison and convergence | Equation implementation only |
| H-FORCE | The declared domain-specific force model predicts its matched reference within justified uncertainty | Force or independently measured motion comparison with nuisance terms | Model validity in that domain |
| H-MOTION | Resolved trajectories agree with the selected force balance and available measurements | Time refinement, force accounting and held-out trajectories | Particle dynamics within stated assumptions |
| H-ACCEL | One admissible policy meets the target acceleration metric over the specified duration | Constrained closed-loop trial and independent replay | Conditional acceleration capability |
| H-ROBUST | H-ACCEL remains true under the registered uncertainty/disturbance set | Held-out perturbations and boundary cases | Bounded robustness, with sampling limits |
| H-LIMIT | A necessary condition excludes the registered target within a precisely defined model/domain | Reviewed analytical inequality or verified numerical certificate | Model/domain-specific impossibility or limitation |

Freeze the quantifiers: one particle versus every member of a material class; one initial state versus all declared states; an existing control policy versus all admissible policies. A failure of one controller does not refute existence of another.

## Domain record required before a physical claim

| Field | Required declaration | Current planning state |
|---|---|---|
| Medium | Air state/composition, temperature, density, sound speed, viscosity and attenuation; uncertainties and sources. Keep the water reference separately scoped. | Air selected for the initial numerical route and intended validation medium; actual air state remains to be sourced/frozen |
| Body | Material, geometry, size, density, compressibility and surface assumptions | P4/P5 field/force reference: 50 mm, 1.46 g EPS sphere from DEC-002; eventual acceleration-trial body is not selected |
| Concentration | One isolated particle or justified dilute ensemble; interaction assumptions | Start one particle |
| Chamber | Air volume, transducer face/baffle, sphere geometry/gap, outer radiation boundary | Use DEC-002 geometry for the P4 field route; idealized geometry and outer-boundary treatment must be stated in NUM-01 |
| Actuation | Frequency, phasor convention, source calibration, limits, bandwidth, total budget | Source-backed selection or explicit hypothetical scenario |
| Frames | Laboratory/chamber coordinates, +Z convention, medium flow, gravity vector | Must be frozen by FND-01 |
| Environment | Earth comparison, ideal zero gravity, or sourced residual acceleration/time series | Implement parameterized gravity in P6 |
| Target | Vector function, start/end, duration, spatial domain, initial state | Target contract in CTL-01 |
| Measurement | Raw state or virtual sensor; sampling and averaging definition | Define before evaluation |
| Uncertainty | Numerical, property, boundary, actuator, sensor and model-form terms | Separate register required |

Research-design records may contain unresolved fields and proceed independently. Executable scenarios may not silently substitute unknown physics.

## Acceleration is the central observable

Define `error_accel_rms` as the square root of the time average of the squared Euclidean norm of the difference between the registered target and resolved particle acceleration, using explicit quadrature weights and the declared evaluation window. State units m/s², sampling rate, filter/averaging operator, any transient exclusion, and why that exclusion answers the hypothesis. Freeze these before evaluation.

Record actual net acceleration and `F_acoustic/m` separately. When other forces contribute, the latter is a diagnostic and does not itself measure target tracking. A velocity or trapping success cannot replace an acceleration failure without registering a new question.

A reduced overdamped model can be appropriate for displacement/velocity predictions, but does not resolve inertial relaxation by itself. Before using it to assess an acceleration claim, MOT-01 must establish the relevant time-scale and observation contract or use a justified inertial model. For stochastic motion, do not define a pointwise acceleration by differencing ideal white noise; register a finite-time statistic and its measurement bandwidth.

## Required competing explanations

Account for radiation force, fluid drag, gravity/buoyancy under the selected frame, and fluid motion. Review wall corrections, streaming, viscous/thermal boundary layers, particle inertia, added-mass/history effects, Brownian motion, temperature drift and particle interactions where their scales make them relevant. Each omitted contribution needs an error/sensitivity justification relative to the metric, not merely a statement that the model is simple. See the primary source starting points in [02](02-research-and-sources.md).

Earth and zero-gravity cases must update the consistent fluid/body force balance. Removing gravity does not remove viscosity, walls or acoustic streaming.

## Water qualification and air validation route

P4 first audits whether existing water computations support the owner's reported numerical-workflow qualification; the recorded P3/replay and figure-extraction evidence must retain their exact, limited scopes. A gap triggers only a bounded water numerical comparison against an independent reference. Then the air field route uses [Andrade P1.3](../benchmarks/P1.3-andrade-force-curve-specification.md) geometry and analytic field checks because the source supplies no measured pressure map. An air P4 PASS directs initial P5/P6/P7 development to air. P5 may compare modeled force with the published air-sphere curve, but unresolved experimental uncertainty keeps formal acceptance INDETERMINATE. Neither route establishes prescribed acceleration or microgravity behavior, and neither medium transfers validation to the other.

## Scientific completion and outcomes

A positive result includes the complete domain, target/time window, all constraints, error/uncertainty, independent comparison and evidence status. A negative result identifies the failed statement, counterexample or violated necessary condition, and the range over which it holds. If the evidence cannot distinguish success from failure, report INDETERMINATE and specify the measurement or calculation that would resolve it.

Changing acceleration tracking to transport, separation or trapping is a possible later research decision, not automatic success for H-ACCEL. No outcome here establishes universal gravity-like loading, human-scale behavior or a hardware system.
