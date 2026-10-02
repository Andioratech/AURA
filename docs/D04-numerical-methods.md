# AURA-D04: Numerical Methods and Solvers

**Version:** 1.0 · **Status:** DRAFT · **Date:** 2026-10-01

## Rule

There is no single AURA solver. Every run identifies governing equations, approximation, discretization, boundary conditions, numerical precision and validity domain. Fidelity comparison and observable convergence are part of the method.

## Model selection

The homogeneous linear wave equation and harmonic Helmholtz equation provide initial idealized models. Array superposition is suitable for fast fields when medium and propagation assumptions apply. Choose models by regime and observable:

| Regime / need | Candidate | Key limitation |
|---|---|---|
| Order-of-magnitude estimate | MCLF / analytical | Not a substitute for field solution |
| Homogeneous medium, simple array | Transfer functions / superposition | Limited scattering and boundary representation |
| Transient or moderate heterogeneity | k-space or FDTD | Stability, dispersion and memory must be checked |
| Complex harmonic scattering | BEM, FEM or T-matrix | Formulation and mesh validity must be documented |
| Large open domain | BEM/FMM, propagator or hybrid | Avoid unjustified full-volume cost |
| Claim-critical result | Independent method plus convergence | Independent methods must not share the same core error |

ka = 2 pi a/lambda guides particle-model choice but does not alone establish validity. Gor'kov-type potential is for appropriate small-particle conditions; transition and large-object cases require a suitable scattering model.

## Discretization and numerical controls

For volumetric methods, state minimum wavelength and points/elements per wavelength. There is no universal points-per-wavelength value: demonstrate convergence for the observable. Record linear/nonlinear tolerances, iterations, solver versions, precision, mesh/time step, PML or domain size, and residual boundary reflection. Use at least three refinement levels for key results. Refine the physical observable, not only algebraic residual.

Time steps must meet solver stability limits and resolve the highest relevant frequency. Define averaging windows for acceleration. Document multi-rate stepping when controller and acoustics operate on different time scales. float32/float64 and complex64/complex128 selection must be explicit.

## Boundary conditions

Use analytical solutions for Dirichlet/Neumann checks; record complex impedance and frequency for material walls; test PML thickness and reflection for open domains; use symmetry only when source, geometry and observable preserve it.

## Force and dynamics

Pressure/momentum estimates such as F approximately kappa P/c are conditional checks, not universal levitation laws. Select radiation-force formulations consistent with material, geometry, ka and field. Rigid translation and rotation equations must include all declared forces and torques, including gravity and disturbance terms.

## Methodological prohibitions

Do not extrapolate a particle model to a person; equate mean force with uniform body pressure; compare electrical input power with acoustic power without efficiency; substitute frequency for field amplitude/intensity; or call an externally forced acceleration gravity.

## Candidate software

The source proposal lists NumPy/SciPy, SymPy, Gmsh, FEniCSx, PETSc, k-Wave, JAX and ParaView. These are candidate tools only. D05 governs environment selection; current compatibility, license and availability must be reviewed when implementation begins.
