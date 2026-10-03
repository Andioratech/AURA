# Air Field Solver Contract for P4

**Status:** REVIEW · **Prepared:** 2026-10-03 · **Task:** NUM-01

## Question and scope

Can a numerical evaluation of Hasegawa et al.'s spherical-harmonic solution recover the complex harmonic field for a stationary, rigid sphere centered on the axis of a circular piston in an infinite rigid baffle, over the DEC-002 air geometry and declared 0.1–30 mm surface-gap interval?

This contract defines a field calculation and its verification domain. It does not define acoustic radiation force, body motion, target-acceleration tracking, gravity equivalence, or experimental validation. A P4 result is numerical verification only.

## Frozen reference case

| Quantity | Contract value |
|---|---|
| Medium | Homogeneous air at 25 °C; `rho = 1.18 kg/m³`, `c = 346 m/s`; lossless, linear, harmonic model |
| Frequency | `f = 25,230 Hz`; `omega = 2*pi*f`, `k = omega/c` |
| Source | Coaxial circular piston, radius `R = 10 mm`, mounted in an infinite rigid planar baffle; prescribed uniform face displacement amplitude `15 um` |
| Sphere | Centered, stationary, rigid sound-hard sphere, radius `a = 25 mm`; the 1.46 g EPS mass is recorded for benchmark identity but does not enter this field boundary condition |
| Separation | `H` is the axial distance from the piston face plane to the nearest sphere surface; declared sweep `0.1 mm <= H <= 30 mm`. The center-to-piston-plane distance is `a + H` |
| Geometry | Axisymmetric, source and sphere coaxial; evaluate only fluid points outside the sphere and outside the solid piston/baffle |
| Model | Single-frequency exterior field; no chamber walls, finite baffle, attenuation, thermal effects, nonlinear propagation, transducer loading, sphere elasticity, translation, or rotation |
| Arithmetic | Complex binary64 (`complex128`); no unreported precision fallback |

The face displacement gives a prescribed harmonic normal-velocity amplitude through the declared phasor convention (`v_n = -i*omega*xi` for positive displacement along the declared normal). The field solver must preserve this normalization in every output and diagnostic. The source condition is an idealized input from the published case, not a calibrated measurement of the actual transducer field.

## Numerical interface

The eventual numerical evaluator receives a validated field scenario, an immutable ordered list of Cartesian observation coordinates in metres, and a preflight-approved harmonic truncation/work plan. It must not choose missing medium/source/body values, resize the case silently, or allocate series workspaces before preflight accepts the request.

For each observation point, return the complex pressure in Pa, fluid particle velocity in m/s, and pressure gradient in Pa/m using the existing `FieldSamples`/FIELD-1.0 conventions: peak amplitudes, `exp(-iwt)`, chamber-frame coordinates, and complex128 values. Intermediate velocity potential may be retained as a solver diagnostic but is not a replacement for these canonical observables. Map the axisymmetric radial and axial components into the declared Cartesian frame, with an explicit on-axis limit.

Return solver diagnostics separately from field arrays: method/source citation and equation mapping, stationary-sphere boundary branch, truncation order, special-function/scaling strategy, precision, preflight estimate and caps, termination/convergence status, and any numerical warning. A failed or nonconverged evaluation is a typed failure and cannot emit a passing field artifact.

Each request remains bounded by the existing field-sample contract. A larger spatial map must use explicit ordered chunks with a shared immutable run identity; it must not bypass per-request limits or silently allocate a full gap-by-field tensor.

## Equation and convention mapping

The selected primary method is Hasegawa, Matsuzawa, Inoue and Yanagihara (1985), Eqs. 1–20, for a rigid sphere in the nearfield of a circular piston in an infinite baffle. Use the stationary sound-hard boundary condition at every spherical-harmonic order. The source paper's freely translating-sphere `n=1` coefficient is a different physical branch and must not be reused. The stationary `n=1` term is obtained from the same zero-normal-velocity boundary condition as the other orders.

Hasegawa et al. use `exp(+iwt)`, define the pressure as `p = rho*d(phi)/dt` (their Eq. 12), and use the velocity-potential convention `u = -grad(phi)` (consistent with their sphere-normal condition, Eq. 14). Conjugate the source series and source phasors to express the same real field under FIELD-1.0's `exp(-iwt)` convention. In project convention the implementation therefore uses `u = -grad(phi)`, `p = -i*rho*omega*phi`, and `grad(p) = -i*rho*omega*grad(phi)`. The source piston velocity amplitude must be mapped from its declared displacement amplitude with the same convention and normal orientation. A standalone derivation/sign test must verify this mapping before the coupled sphere case is accepted.

Primary source: T. Hasegawa et al., “Ultrasonic scattering by a rigid sphere in the nearfield of a circular piston,” *Journal of the Acoustical Society of Japan (E)* 6(1), 9–14 (1985), DOI [10.1250/ast.6.9](https://doi.org/10.1250/ast.6.9). The article's sample computations (`kR = 30`, `ka = 5`) do not establish convergence for this contract's geometry.

## Required verification sequence

1. **Convention and boundary checks:** verify dimensions, phasor/amplitude mapping, finite outputs and zero normal fluid velocity at the stationary sphere boundary for all retained orders, including `n=1`.
2. **Piston-only check:** compare the no-sphere limit with independent Rayleigh-disk quadrature at common points; also check axial and far-field limits. The quadrature implementation must not reuse the spherical-series evaluator.
3. **P3 overlap:** recover selected plane-wave/incident-field limits already covered by ANA-07 and compare pressure, velocity and pressure gradient with the frozen independent values.
4. **Rigid-sphere scattering check:** in the plane-wave limit, compare against the exact stationary rigid-sphere partial-wave solution at common exterior points. Keep this oracle separate from the piston/sphere series implementation.
5. **Coupled-series convergence:** compare at least three increasing harmonic truncations at predeclared points, including near-surface locations for both gap endpoints and representative interior gaps. Track complex pressure, velocity and pressure-gradient observables separately; do not infer derivative convergence from pressure convergence.
6. **Full declared gap coverage:** exercise the complete 0.1–30 mm interval without dropping the 0.1–1.9 mm region because the published FEM report did not cover it. The selected series' convergence there is AURA's own numerical question.

NUM-04 must freeze the primary observable, point set, three-level refinement sequence, numerical error budget and stopping rule before production runs. No universal percentage tolerance is adopted here. A favorable truncation is not selected after inspecting the desired field result.

## Resource and failure boundary

NUM-02 must derive pre-allocation estimates from the requested point count, truncation and all simultaneously live special-function/series arrays; include algorithm workspace, output arrays, runtime basis and safety headroom. The run must declare RAM, disk and wall-time caps. Unknown series scaling or an estimator that cannot conservatively bound work is a preflight failure, not permission to allocate and hope. Preserve rejected and failed configurations with their request identity and estimates.

The actual conditioning and cost at the AURA geometry are not yet established. In particular, the published examples do not bound cancellation or harmonic-tail behavior at `ka ~= 11.45`, `kR ~= 4.57`, or the minimum `H = 0.1 mm`. If preflight or independent checks show unstable or unbounded evaluation, retain the results and reopen the NUM-01 method comparison under the same physical contract.

## Explicit exclusions

This contract does not validate the foam sphere's acoustic material properties, measured transducer displacement, chamber reflections, published force curve, force integration, particle acceleration, closed-loop performance, acoustic power efficiency, scale-up, microgravity performance, or gravity equivalence. Those questions require later contracts and evidence. Water results remain a separate medium-specific qualification.
