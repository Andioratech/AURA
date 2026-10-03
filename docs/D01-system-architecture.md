# AURA-D01: System Architecture

**Version:** 1.4 · **Status:** BASELINE · **Date:** 2026-10-03

## Purpose and hypothesis

AURA investigates whether controlled ultrasonic fields can apply object-specific acoustic radiation forces that keep the acceleration of free bodies near a prescribed vector within a limited domain. The working hypothesis is conditional and falsifiable: closed-loop control may achieve a sufficiently common target acceleration for selected objects after adjusting the force on each object. Failure to identify a viable domain or a quantitative limit is an acceptable scientific outcome.

Acoustic pseudogravity means mechanically induced acceleration. Acoustic forces depend on field, material, geometry and boundary conditions, whereas gravitational acceleration couples universally to mass. AURA does not claim to generate gravity.

Water is the first numerical-workflow qualification domain, followed by the air numerical-field gate selected for the intended validation route under [DEC-005](decisions/DEC-005-air-validation-route.md) and ordered by [DEC-006](decisions/DEC-006-water-qualification-before-air-route.md). The air field/force reference is the bounded DEC-002 single-transducer, 50 mm sphere case; it is not an acceleration trial. Only after the air field gate passes does the initial downstream force, dynamics and control path proceed in air. Water qualification does not validate the air case or its physical force model. Greater masses, larger objects and other geometries remain explicit research objectives under [DEC-004](decisions/DEC-004-staged-mass-and-size-expansion.md); each needs an applicable model and independent evidence.

## System loop

The computational digital twin consists of:

1. **Scenario orchestrator:** loads chamber geometry, medium, transducer array, bodies, residual gravity, target acceleration, solver, seeds and resource limits.
2. **Acoustic field solver:** computes complex pressure and, where required, time-dependent fields. Fidelity options include analytical superposition, propagators, k-space/FDTD and local FEM/BEM or hybrid methods.
3. **Force and torque model:** maps fields and scattering properties to force and torque while recording equations and validity regime.
4. **Rigid-body dynamics:** advances position, velocity, orientation and angular velocity. Deformable bodies and tissue models are outside the initial scope.
5. **Virtual sensors:** generate configurable observations and noise (for example, camera, depth, event, IMU or direct-state reference sensors).
6. **State estimator:** estimates 3D state and later may identify unknown object properties.
7. **Deterministic controller:** initially PID, LQR or MPC. Learning methods are optional future tools, never replacements for physical checks.
8. **Array optimizer:** maps target forces to element phases and amplitudes subject to power, pressure, thermal and hardware limits.
9. **Scientific recorder:** stores exact inputs, software/environment identity, outputs, metrics and failure reason.
10. **Independent MCLF:** checks the scenario before execution and the result after execution. It must not reuse the simulator implementation blindly.

## Physical model outline

For a homogeneous linear medium, the ideal wave equation is d2p/dt2 = c2 nabla2 p; harmonic steady state gives nabla2 p + k2 p = 0, k = 2 pi f/c. A fast array approximation may use p(r) = sum_i H_i(r,f) A_i exp(j phi_i). Each run must state whether this model includes attenuation, boundaries, reflections, coupling and nonlinear effects.

Object translation follows m r_ddot = F_ac + F_gravity + F_disturbance. Rotation follows I omega_dot + omega cross (I omega) = tau_ac + tau_disturbance. The control objective is to reduce a declared acceleration error over a declared time window; instantaneous noisy acceleration is not an acceptance measure.

The characteristic size ratio ka = 2 pi a/lambda informs model choice. Rayleigh/Gor'kov approximations are limited to suitable small-particle regimes; transition and large-object regimes require appropriate scattering, boundary or volume methods. A model must declare its regime and limitations.

## Fidelity ladder

| Level | Purpose | Exit evidence |
|---|---|---|
| L0 | Units, dimensions, finite values, geometry and resource preflight | Known-invalid inputs are rejected |
| L1 | Analytical waves and idealized sources | Closed-form cases reproduced |
| L2 | Fast array superposition/propagator | Interference and simple array cases verified |
| L3 | Force and torque models | Model-specific benchmark and validity checks |
| L4 | Rigid-body dynamics and deterministic control | Stable closed-loop reference case |
| L5 | Sensors, noise, estimation and parameter sweeps | Robustness and uncertainty results |
| L6 | Local high-fidelity or independent solver confirmation | Converged result independently reproduced |

Advance only when the prior gate is supported by evidence. A numerically stable visualization is not validation.

## Software boundaries

Scenario, field, force, dynamics, control, MCLF and evidence modules communicate through versioned SI data contracts. Solvers return arrays with coordinates, units, precision, boundary metadata and convergence diagnostics. Force models identify the exact equation and applicable regime. Experiment definitions remain independent of compute backend.

## Initial research campaign

P2/P3 foundations are complete. P4 first audits the water numerical-workflow evidence and closes any bounded qualification gap, then verifies the selected air source/sphere field against P3 and independent references. An air P4 PASS routes initial P5 onward through air-domain models; force, dynamics, prescribed acceleration, robustness and any microgravity case keep their own gates. The SRC-W03 water-particle measurement remains exploratory and is not silently converted into field-solver verification, an air model or physical validation. Do not combine controller or AI development with force-model work. See [DEC-003](decisions/DEC-003-nonblocking-foundation-work.md), [DEC-005](decisions/DEC-005-air-validation-route.md), [DEC-006](decisions/DEC-006-water-qualification-before-air-route.md) and [PLAN-01 v1.5](PLAN-01-project-execution-plan.md).

## Scale-up boundary

The [scale progression track](planning/11-scale-progression.md) separately investigates increased mass, dimensions and geometric complexity, including the retained water-particle evidence track. Research can proceed alongside the air route. Each numerical candidate must pass the applicable model, field, force/torque, dynamics, resource and independent-evidence gates. Software interfaces must support explicit body geometry and model capabilities without treating all objects as small particles.

A proposed 5 m cubic station is a future study question. It requires array aperture and power budgets, acoustic attenuation, chamber modes, spatial acceleration uniformity, thermal and safety analyses, body-specific coupling and an independent feasibility review. No human-scale feasibility is inferred from point-particle simulations.

## Risks

Primary risks are misuse of a force approximation outside its regime, confusing electrical and acoustic power, unmodeled boundaries or resonances, inadequate numerical convergence, optimizer exploiting model error, false confidence from correlated solvers, compute/memory exhaustion, and claims exceeding the evidence. D02, D05, D06 and D09 define controls.
