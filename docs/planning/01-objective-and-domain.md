# 01 — Scientific Objective, Domain and Claim Contract

## Program objective and first operational question

The program investigates whether controlled acoustic forcing can produce a prescribed acceleration for selected bodies across explicitly investigated mass, size and geometry domains, toward microgravity operation. Small particles in water are the first campaign. Greater masses and larger or differently shaped objects are an explicit research objective under [DEC-004](../decisions/DEC-004-staged-mass-and-size-expansion.md); follow [11](11-scale-progression.md) to investigate each transition.

The first operational question is:

For a specified small particle suspended in water, can an admissible ultrasonic actuation policy make its resolved center-of-mass acceleration follow a predeclared vector over a finite interval and a bounded workspace, with an independently checked force/motion model and uncertainty budget?

The long-term environment is microgravity. Earth-gravity comparisons are development controls. Setting a gravity vector to zero is a modeled idealization; it is not evidence about a real flight environment. AURA remains an unvalidated hypothesis.

The hypothesis table and domain fields below describe the initial campaign. For each larger-body campaign, register new body/model-specific instances of these hypotheses, include torque/orientation/loading observables when required, and repeat the relevant evidence gates. Neither success nor failure of the initial particle case determines all other scales.

## Hypothesis hierarchy

| ID | Bounded statement to register | First discriminating result | May support |
|---|---|---|---|
| H-FIELD | The declared field model predicts pressure/velocity observables within its frozen numerical budget | Analytical comparison and convergence | Equation implementation only |
| H-FORCE | The declared particle force model predicts a matched water reference within justified uncertainty | Force or independently measured motion comparison with nuisance terms | Model validity in that domain |
| H-MOTION | Resolved trajectories agree with the selected force balance and available measurements | Time refinement, force accounting and held-out trajectories | Particle dynamics within stated assumptions |
| H-ACCEL | One admissible policy meets the target acceleration metric over the specified duration | Constrained closed-loop trial and independent replay | Conditional acceleration capability |
| H-ROBUST | H-ACCEL remains true under the registered uncertainty/disturbance set | Held-out perturbations and boundary cases | Bounded robustness, with sampling limits |
| H-LIMIT | A necessary condition excludes the registered target within a precisely defined model/domain | Reviewed analytical inequality or verified numerical certificate | Model/domain-specific impossibility or limitation |

Freeze the quantifiers: one particle versus every member of a material class; one initial state versus all declared states; an existing control policy versus all admissible policies. A failure of one controller does not refute existence of another.

## Domain record required before a physical claim

| Field | Required declaration | Current planning state |
|---|---|---|
| Medium | Water composition, temperature, density, sound speed, viscosity, compressibility, attenuation; uncertainties and sources | Water selected; properties depend on chosen reference |
| Particle | Material, radius distribution, shape, density, compressibility, surface assumptions | Small particles intended; numeric range/material selection in LIT-02 |
| Concentration | One isolated particle or justified dilute ensemble; interaction assumptions | Start one particle |
| Chamber | Dimensions, walls, impedance/no-slip assumptions, source arrangement | Select a simple reference geometry before P4 |
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

## Separate the air reference

Keep [Andrade P1.3](../benchmarks/P1.3-andrade-force-curve-specification.md) and its digitized data intact. It remains an exploratory air-sphere force reference; its experimental uncertainty is unresolved. Its large object regime cannot validate a small-particle water implementation. A matched air scattering backend would be separate, conditional work only if its scientific benefit justifies it. The water simulator need not implement that expensive backend merely to finish an unrelated benchmark.

## Scientific completion and outcomes

A positive result includes the complete domain, target/time window, all constraints, error/uncertainty, independent comparison and evidence status. A negative result identifies the failed statement, counterexample or violated necessary condition, and the range over which it holds. If the evidence cannot distinguish success from failure, report INDETERMINATE and specify the measurement or calculation that would resolve it.

Changing acceleration tracking to transport, separation or trapping is a possible later research decision, not automatic success for H-ACCEL. No outcome here establishes universal gravity-like loading, human-scale behavior or a hardware system.
