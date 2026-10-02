# Counterpropagating Plane-Wave Kernel

**Contract:** COUNTERPROPAGATING-1.0 · **Date:** 2026-10-02 · **Owner:** [ANA-03](../work-items/ANA-03.md)

## Physical scope and independent derivation

Use EQ-006–009, [reviewed primary sources SRC-E01–E03](analytical-source-review.md), [FIELD-1.0](analytical-field-contract.md) and the [B-04 protocol](../benchmarks/B03-B06-analytical-protocols.md). The negative-time convention is `Re(q_hat exp(-i omega t))`. MIT Lecture 2 equations 2.24–2.25 use the opposite time sign, so conjugate their velocity convention; Lecture 3 equation 3.4 supplies the independent signed flux reference. These are prescribed incident fields in an infinite homogeneous, stationary, linear, inviscid, lossless fluid. An observation box is not a reflecting tank. There is no body coupling, boundary response, streaming, force, startup or gravity simulation.

For waves along n and -n, define `alpha_plus=phi_plus-k n dot(ref_plus)`, `alpha_minus=phi_minus+k n dot(ref_minus)`, `delta=(alpha_plus+alpha_minus)/2`, `xi=k n dot(x)+(alpha_plus-alpha_minus)/2`, `S=A_plus+A_minus`, `D=A_plus-A_minus`. Expanding real trigonometric identities gives:

- `p = exp(i delta) [S cos(xi) + i D sin(xi)]`.
- `v = n exp(i delta) [D cos(xi) + i S sin(xi)] / Z`.
- `grad(p) = n k exp(i delta) [-S sin(xi) + i D cos(xi)]`.
- `I = n (A_plus^2-A_minus^2)/(2 Z)` from the exact period average; cross terms have zero real contribution for exact opposite directions in the shared medium.

The production implementation sums separately evaluated source fields. The independent test reference evaluates these combined real identities with Decimal scalar pairs, bounded series and 60/80-digit precision. This checks a different arithmetic route, not a second physical model. Equal amplitudes give zero mean net energy transport, even where pressure or velocity oscillates. Zero net energy flux does not imply zero stored energy or establish force on an object. The pressure-only progressive-wave formula gives a false standing-wave flux at the pressure antinode and is tested as an intentional misuse.

## API and numeric admission

`evaluate_counterpropagating_pair(forward, backward, coordinates_m, *, box_min_m, box_max_m, workspace_bytes)` returns FIELD-1.0. Both inputs must be exact PlaneWave specifications with identical rho/c/f and exactly opposite direction components; source reference, phase and amplitude may differ. Either amplitude may be zero but neither input escapes validation. The name forward identifies the first supplied direction, not necessarily +x. No silent normalization or averaging.

All single-wave input/range rules from [PLANE-WAVE-1.0](plane-wave-kernel.md) apply. Before any trig or complex field allocation, validate both full phase plans, 1..256 coordinates, inclusive observation bounds and integer workspace >=4096*N+8192 bytes. Single-wave phase bounds remain |theta|<=4pi and conditioning sum<=8pi per source. The estimate bounds incremental Python work and encoding, not interpreter RSS. Combined real/imaginary sums must remain finite; cancellation to exact zero is allowed. Arithmetic failures are typed NumericalDomainError; invalid type/domain/medium/geometry failures are InvalidInputError. For noncollinear sources, use the separate [ANA-04 two-wave API](two-wave-kernel.md); the exact-opposite restriction of this API is preserved.

Each source retains the audited <32-operation argument path. Superposition adds one rounded real sum and one imaginary sum per component; the frozen ANA-REF-1.0 summation/product allowances cover this two-source case. Elementary-function accuracy is separately checked on every actual fixture argument. Tests use C=A_plus+A_minus (C=2 Pa when both zero), scales C, C/Z, k*C and C²/(2Z), preserving the frozen 2048e tolerance at cancellation nodes. No bound is claimed outside the specified numerical domain or for physical accuracy.

## Example

```python
from dataclasses import replace
from aura.fields import PlaneWave, evaluate_counterpropagating_pair, mean_intensity_w_m2

forward = PlaneWave(
    density_kg_m3=1000, sound_speed_m_s=1500, frequency_hz=1_000_000,
    peak_pressure_pa=2, direction=(1, 0, 0), reference_m=(0, 0, 0),
    phase_rad=0, dynamic_viscosity_pa_s=0, amplitude_attenuation_per_m=0,
)
backward = replace(forward, direction=(-1, 0, 0))
field = evaluate_counterpropagating_pair(
    forward, backward, [(0, 0, 0), (0.000375, 0, 0)],
    box_min_m=(-0.0015,) * 3, box_max_m=(0.0015,) * 3,
    workspace_bytes=2 * 1024**2,
)
print(field.pressure_pa)
print(field.velocity_m_s)
print(mean_intensity_w_m2(field))
```

This is an in-memory kernel example, not an admitted physical recorder run. FIELD-1.0 provenance/index/checker requirements remain open for the P3 campaign.
