# Two Coherent Plane Waves

**Contract:** TWO-PLANE-WAVES-1.0 · **Date:** 2026-10-02 · **Owner:** [ANA-04](../work-items/ANA-04.md)

## Equations, scope and independent flux derivation

Use EQ-006–009, [FIELD-1.0](analytical-field-contract.md), [ANA-REF-1.0 B-05](../benchmarks/B03-B06-analytical-protocols.md) and the [primary-source review](analytical-source-review.md). SRC-E01 Eq. (6) supplies linear Euler; SRC-E02 Eqs. (2.15)–(2.18) supply the progressive-wave relation with the documented time-sign conversion. The vector two-direction expressions below are project derivations by linearity, not a claimed experimental result from those sources.

With the negative harmonic time convention, define theta_j=k*n_j dot(x-ref_j)+phi_j, Z=rho*c and omega=2*pi*f. The independent real pressure decomposition is `p_R=A1*cos(theta1)+A2*cos(theta2)`, `p_I=A1*sin(theta1)+A2*sin(theta2)`. Differentiate each component to obtain `g_R=-k*sum(Aj*nj*sin(thetaj))`, `g_I=k*sum(Aj*nj*cos(thetaj))`. Linear Euler gives `v_R=g_I/(omega*rho)`, `v_I=-g_R/(omega*rho)`.

A direct period integral of pressure times each velocity component uses average(cos(theta1-omega*t)*cos(theta2-omega*t))=cos(theta1-theta2)/2. Therefore:

`I = [A1²*n1 + A2²*n2 + A1*A2*(n1+n2)*cos(theta1-theta2)]/(2*Z)`.

The cross term is required for coherent sources at this shared frequency. Summing only their separate intensities loses interference. For n2=-n1 the cross term vanishes, recovering the already verified B-04 limit. For perpendicular equal in-phase sources at the origin, each active flux component is twice the corresponding single-source value. For the B-05 pressure cancellation point, both velocity and gradient remain nonzero vectors although mean flux vanishes. Zero pressure or zero mean flux establishes no body force or absence of force.

Assumptions: prescribed incident fields in an unbounded homogeneous, stationary, linear, inviscid and lossless fluid, with explicit peak amplitudes and phase-reference positions. No walls/transducer shapes, scattering, absorption, streaming, startup, force, trajectory or gravity response are simulated. Observation boxes are sampling windows, not physical boundaries. The manufactured coefficients are verification inputs, not measured water properties. Applicability to particles, other materials/geometries, larger masses or microgravity requires separate models/evidence.

## API and preserved admission limits

`evaluate_plane_wave_pair(first_wave, second_wave, coordinates_m, *, box_min_m, box_max_m, workspace_bytes)` returns FIELD-1.0. Both sources are exact immutable PlaneWave specifications with identical density, sound speed and frequency. Directions are independently validated unit vectors. Parallel/opposite directions are admitted limits of this API; arbitrary source counts and mixed frequencies/media are not admitted. Each source retains its own amplitude, phase and reference point.

`evaluate_counterpropagating_pair` keeps its exact-opposite restriction and delegates to the same bounded pair evaluator. The single-wave API remains available. All samples and both complete phase plans are checked before trigonometry or complex field allocation. PLANE-WAVE-1.0 bounds remain 1..256 samples, inclusive finite box, |theta|<=4pi and per-source conditioning sum<=8pi. Require integer workspace >=4096*N+8192 bytes. Nonfinite combined components raise NumericalDomainError; exact cancellation is allowed. No normalization, clipping, phase wrapping or amplitude averaging occurs.

Each source retains the audited <32-operation argument path and one real/imaginary component addition from ANA-03; admitting a different direction adds no source-count or iteration growth. ANA-REF-1.0's existing two-source summation/product allowances therefore apply to the frozen B-05 matrix, conditional on ordinary-scale arithmetic and the independently checked <=4e sine/cosine error. The tolerance is 2048e on the global scales C, C/Z, k*C, C²/(2Z), C=A1+A2 or the original 2 Pa scale at zero drive. It does not certify all allowed numeric inputs or physical accuracy.

## Symmetry and reference independence

Source order changes no output. Under a proper rotation R of both directions, both reference points and every observation, pressure is unchanged and velocity/gradient/flux transform by R. The observation domain must also be transformed or preserved; the chosen axis permutation preserves the cube. Translating references and observations together preserves the field where translated samples remain admitted. Rotating only samples is not a symmetry. A common phase factor multiplies all complex fields, preserving mean flux.

Changing one reference by d while adding k*n dot(d) to that source phase represents the same wave. Tests check this separately for both sources. Near-node checks use fixed neighboring binary64 coordinates and global nonzero scales, not a fitted local percentage tolerance.

The test-only oracle uses Decimal real sine/cosine series, spatial differentiation and the independent cosine-difference flux expression, with no production imports. It reuses only B-03's independent constant/series primitives; 60/80-digit agreement and literal B-05 values check this numerical reference. Production uses separately evaluated complex fields and p*conj(v). Arithmetic-route agreement verifies the declared formula on selected inputs; it is not physical model validation or an independent external review.

## Minimal B-05 example

```python
from dataclasses import replace
from aura.fields import PlaneWave, evaluate_plane_wave_pair, mean_intensity_w_m2

first = PlaneWave(
    density_kg_m3=1000, sound_speed_m_s=1500, frequency_hz=1_000_000,
    peak_pressure_pa=2, direction=(1, 0, 0), reference_m=(0, 0, 0),
    phase_rad=0, dynamic_viscosity_pa_s=0, amplitude_attenuation_per_m=0,
)
second = replace(first, direction=(0, 1, 0))
field = evaluate_plane_wave_pair(
    first, second, [(0, 0, 0), (0, 0.00075, 0)],
    box_min_m=(-0.0015,) * 3, box_max_m=(0.0015,) * 3,
    workspace_bytes=2 * 1024**2,
)
print(field.pressure_pa)
print(field.velocity_m_s)
print(mean_intensity_w_m2(field))
```

The second point has nearly zero numerical pressure but retains opposing x/y fluid-velocity components. This example is an in-memory kernel call. Physical recorder admission, FIELD-1.0 gradient/provenance linking, balances and the complete P3 campaign remain pending.
