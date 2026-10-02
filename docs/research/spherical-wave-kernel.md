# Ideal Outgoing Spherical Wave

**Contract:** SPHERICAL-WAVE-1.0 · **Date:** 2026-10-02 · **Owner:** [ANA-05](../work-items/ANA-05.md)

## Reference, derivation and limits

Use [FIELD-1.0](analytical-field-contract.md), EQ-006/009/010 and [ANA-REF-1.0 B-06](../benchmarks/B03-B06-analytical-protocols.md). SRC-E03 is MIT 6.551J/HST.714J, *Lecture 3: Spherical Waves: Near & Far Field, Radiation Impedance, and Simple Sources*, 16 September 2004, [primary PDF](https://ocw.mit.edu/courses/6-551j-acoustics-of-speech-and-hearing-fall-2004/7056ab51d5cb75810bf976ee38ac8f30_lec_3_2004.pdf). Pages 2–3, Eqs. (3.8)–(3.15), rechecked on 2026-10-02, describe outgoing radial pressure and full velocity. Conjugate its positive harmonic time convention to AURA's negative convention. Source examples in air do not supply measured water properties. The [source review](analytical-source-review.md) also identifies linear Euler and harmonic averaging.

For r=|x-center|, n=(x-center)/r, Z=rho*c, k=2*pi*f/c and theta=k*(r-r_ref)+phi, define P=P_ref*r_ref/r. Project normalization and differentiation give:

```
p = P exp(i theta)
grad(p) = (-1/r + i k) p n
v = (p/Z)(1 + i/(k r)) n
I = Re(p conj(v))/2 = [P_ref²/(2 Z)] (r_ref/r)² n
```

The independent reference differentiates the real amplitude: dP/dr=-P/r, g_R=n*(-P*cos(theta)/r-k*P*sin(theta)), g_I=n*(-P*sin(theta)/r+k*P*cos(theta)); Euler gives v_R=g_I/(omega*rho), v_I=-g_R/(omega*rho). Independently averaging the real radial harmonics leaves P²/(2Z), since the quadrature term's period mean is zero. Constant power through a complete outward sphere follows after multiplying by 4*pi*r²; formal control-surface auditing belongs to ANA-06. This is not a universal force or momentum-transfer bound.

The medium is homogeneous, stationary, unbounded, linear, inviscid and lossless. All coefficients and peak pressure are prescribed manufactured inputs. No walls, physical radiator aperture, scattering, absorption, thermal effects, streaming, startup, force or body dynamics are modeled. The observation box is a sample window. Minimum radius is an explicit computational exclusion, not a transducer radius or a guarantee of physical validity. Geometric spreading differs from absorption: no exponential material loss is included. The exact reactive term is retained; the approximation v=p*n/Z requires kr>>1 and is not used. The frozen minimum kr=pi/2 is neither an asymptotically small nor an asymptotically large value. No claim about measured water, larger bodies or microgravity follows from these tests.

## Explicit API and numerical domain

`SphericalWave` is an immutable keyword-only specification: density_kg_m3, sound_speed_m_s, frequency_hz, peak_pressure_pa (at reference radius), center_m, reference_radius_m, minimum_radius_m, phase_rad, dynamic_viscosity_pa_s, amplitude_attenuation_per_m. No defaults. Positive medium/frequency/radii; reference_radius_m>=minimum_radius_m; nonnegative amplitude and explicit zero losses. The reference sphere belongs to the admitted model domain. No plane-wave or finite-piston schema is repurposed.

### Recorded input binding (ANA-07)

The recorder maps a single Scenario source with `model: ideal_spherical_wave` and `model_contract: SPHERICAL-WAVE-1.0` to this specification. The source uses explicit `center` (m), `reference_radius` (m), `minimum_radius` (m), phase and peak `pressure_amplitude` at the reference radius; its normal, plane reference position and piston aperture are absent. `reference_radius >= minimum_radius > 0`, pressure limit, zero loss, B-06 source identity, finite observation box and sample exclusion are checked before field evaluation. Solver `analytic-spherical-field` 1.0 declares EQ-010; `ANALYTIC-RUN-1.1` distinguishes this additive driver from the unchanged plane policy `ANALYTIC-RUN-1.0`. The source is an ideal mathematical model and does not describe a physical radiator.

`evaluate_spherical_wave(wave, coordinates_m, *, box_min_m, box_max_m, workspace_bytes)` returns FIELD-1.0 in the original sample order, retaining duplicates. Require exact SphericalWave type, 1..256 points, finite built-in numeric triples, a strictly ordered finite box with inclusive membership, and integer workspace>=4096*N+4096. Check every point before trig or complex output allocation. Reject r<r_min, including zero. Boundary comparison uses the computed binary64 norm without padding or silently moving samples.

Use checked differences and math.hypot for radius. Reject coordinate conditioning (|x|+|center|)/r>8, with Euclidean norms, to limit cancellation. Require |theta|<=4*pi and k*(sum_j(|x_j|+|center_j|)+r_ref)+|phi|<=8*pi. The latter conservatively bounds the radial phase path; do not wrap phases. Derived k and Z must be representable even at zero drive. Checked products/ratios and sums reject overflow or a nonzero product/ratio rounded to zero; exact cancellation and zero drive remain valid. These admission guards do not establish physical validity.

For the ordinary-scale frozen matrix, at most 32 dependent rounded operations cover coordinate differences/norm, k, radial difference/phase, amplitude scaling and either component's product/sum path. Power-of-two rescaling in checked products is exact in this range. Norm error is independently checked <=2e relative at actual arguments; sine/cosine <=4e absolute. The coordinate-cancellation guard bounds norm input amplification. Retain ANA-REF-1.0's conservative 512e component allowance and 2048e final budget including reactive factor 1+2/pi and flux products. Check actual fixture discrepancies independently; this budget is conditional, not a proof for extreme/subnormal inputs or physical accuracy.

The independent Decimal oracle uses guarded Machin pi and Taylor sine/cosine, Decimal square root, real spatial derivatives and Euler. Require 60/80-digit stability at 45 normalized decimal places and literal B-06 values. Production computes the complex formula and general p*conj(v) flux. Reuse only test arithmetic primitives, never production functions for expected values. Five configurations complete the 32-configuration P3 allowance; [documented amendment A1](../work-items/ANA-05.md) moves the oblique positive sample to 2*r_ref after a binary64 boundary exclusion, preserving the original input as a rejection test; invalid-input and metamorphic unit checks are not added recorder experiments.

## Minimal example

```python
from aura.fields import SphericalWave, evaluate_spherical_wave, mean_intensity_w_m2

wave = SphericalWave(
    density_kg_m3=1000, sound_speed_m_s=1500, frequency_hz=1_000_000,
    peak_pressure_pa=2, center_m=(0, 0, 0), reference_radius_m=0.000375,
    minimum_radius_m=0.000375, phase_rad=0,
    dynamic_viscosity_pa_s=0, amplitude_attenuation_per_m=0,
)
field = evaluate_spherical_wave(
    wave, [(0.000375, 0, 0), (0.00075, 0, 0), (0.001125, 0, 0)],
    box_min_m=(-0.0015,) * 3, box_max_m=(0.0015,) * 3,
    workspace_bytes=2 * 1024**2,
)
print([abs(p) for p in field.pressure_pa])  # approximately 2, 1, 2/3 Pa
print(mean_intensity_w_m2(field))
```

Pressure magnitudes halve at twice the radius and radial flux becomes one quarter. This in-memory example carries no run provenance. Physical source characterization, scattering, force, body dynamics and experimental checks remain outside the bounded recorder and at their own evidence gates.
