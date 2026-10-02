# Progressive Plane-Wave Kernel

**Contract:** PLANE-WAVE-1.0 · **Date:** 2026-10-02 · **Owner:** [ANA-02](../work-items/ANA-02.md)

## Derivation and scientific scope

Use the primary source locators and sign conversion in [ANA-01's source review](analytical-source-review.md), EQ-006/007/009 and [FIELD-1.0](analytical-field-contract.md). With `p_hat=A exp(i theta)`, `theta=k n dot(x-x_ref)+phi`, direct differentiation gives `grad(p_hat)=i k n p_hat`. Linear Euler under `exp(-i omega t)` then gives `v_hat=grad(p_hat)/(i omega rho)=n p_hat/(rho c)`. The real pressure is `A cos(theta-omega t)`; the period integral of pressure times velocity gives `I=n A^2/(2 rho c)` for this one ideal wave.

The numerical implementation uses spatial sine/cosine, while known quarter-turn answers and a separate Decimal series reference check the result. Agreement verifies this ideal formula on the declared inputs. It does not validate measured water properties, finite radiators, tank walls, nonlinear amplitudes, streaming, body forces or microgravity. Larger-object research remains DEC-004's separate campaign.

## Public API and explicit inputs

`PlaneWave` is a frozen, keyword-only specification. Every field is required:

| Attribute | Meaning |
|---|---|
| `density_kg_m3`, `sound_speed_m_s`, `frequency_hz` | Positive homogeneous fluid coefficients and single frequency |
| `peak_pressure_pa` | Nonnegative incident pressure amplitude at the phase-reference point |
| `direction` | Three real chamber components; unit norm within 4 binary64 epsilons; never renormalized |
| `reference_m` | Three real chamber coordinates of the phase reference, not a transducer surface |
| `phase_rad` | Source phase with the negative harmonic time convention |
| `dynamic_viscosity_pa_s`, `amplitude_attenuation_per_m` | Explicit ideal zeros; nonzero loss is unsupported |

`evaluate_plane_wave(wave, coordinates_m, *, box_min_m, box_max_m, workspace_bytes)` returns FieldSamples. All sampling inputs are explicit; one to 256 positions, finite three-component vectors, strict lower<upper box bounds, inclusive sample membership. The box does not impose boundary conditions. Direction and source reference are copied to tuples; sampling order/duplicates remain unchanged. The output frequency is the specification's frequency.

`mean_intensity_w_m2(field)` computes `Re(p conj(v))/2` componentwise and returns ordered real chamber vectors. It uses both stored fields and does not infer force, source power, body speed or model validity. It is the harmonic flux calculation, not permission to extend the existing pressure-only progressive-wave helper to a standing field.

Invalid types/ranges/geometry are typed InvalidInputError failures; unrepresentable arithmetic raises NumericalDomainError. A positive numeric input alone is not proof of the linear-acoustic approximation; applicability beyond the manufactured B-03 cases requires separate review. Returned samples lack run provenance until the required FIELD-1.0 adapter exists.

## Numerical admission and bounded work

Before trig evaluation/complex output allocation, validate all samples and their phase arguments. Require each final argument `abs(theta)<=4*pi` and each conditioning sum `abs(phi)+sum(abs(k*n_j*x_j)+abs(k*n_j*x_ref_j))<=8*pi`. This rejects cancellation between huge phase-reference coordinates; modulo reduction is not a remedy for already lost input precision. These are implementation limits, not physical propagation limits. Tiny nonzero products rounded to zero and overflowing intermediate quantities are rejected explicitly rather than emitted as a plausible field. Representable subnormals are allowed, but the B-03 relative-rounding budget is claimed only for its ordinary-scale inputs.

Check a positive integer `workspace_bytes` against `4096*N+4096` before creating sampled output. At N=256 the estimate is 1,052,672 bytes, within the verification caller's 2 MiB budget. This bounds incremental kernel work; it is not a whole-process RAM cap or operating-system sandbox. Source and small input validation are necessarily earlier. No filesystem, GPU, thread pool, source-count loop, mesh or time stepping is involved. Whole-run RSS/disk/wall preflight remains mandatory when a physical recorder driver is admitted.

The shared arithmetic helper uses frexp/ldexp scaling: exponent bookkeeping is exact, each factor multiplication/division rounds once in the tested ordinary domain. Wave number has four factor operations; each phase term has three plus coordinate subtraction; the three-term sum and phase addition have three additions. Counting input conversion and pi rounding still leaves fewer than 32 dependent rounded operations on these paths. Pressure multiplies amplitude by sine/cosine; velocity and gradient use at most four further scaled factors. Unit direction is checked rather than repaired. At most three two-product flux components are evaluated, with each half-product formed separately to avoid avoidable intermediate overflow. These bounds fit the conditional ANA-REF-1.0 allocation; they do not prove libm accuracy or support arbitrary subnormal/large-coordinate cases.

## Independent oracle and benchmark report

The test-only oracle uses decimal scalar pairs, not the production complex-field evaluator, vector/scale helpers or math.sin/cos. Pi follows Machin's identity `pi=16 atan(1/5)-4 atan(1/239)`; the identity can be checked by repeated tangent addition with the branch chosen in (3,4). Each arctangent uses its alternating power series, with the first omitted term bounding truncation. Sine/cosine use factorial power series with 256-iteration caps; after terms decrease, the first omitted term bounds the alternating remainder. At |theta|<=4*pi the transient term growth is bounded and the 60/80-digit precision comparison exposes precision-sensitive outcomes. Reference results must agree to 45 decimal places at the common ordinary scales before binary64 conversion; 60-digit truncation targets use a further 8-digit guard margin. This is an independently implemented arithmetic route, not an independent physical model or interval-proof library.

Two comparisons remain distinct: (1) intended decimal/rational fixture inputs with high-precision pi, which include binary64 input/phase rounding in the measured field error; (2) exact Decimal.from_float of the actual binary64 trig argument, which isolates the platform sine/cosine error and checks ANA-REF-1.0's <=4e assumption. The [Python Decimal documentation](https://docs.python.org/3.12/library/decimal.html) specifies exact float conversion and local precision contexts; [the math documentation](https://docs.python.org/3.12/library/math.html) identifies the platform math-library basis. The project uses the locked ENV-1.0 interpreter; consulting these docs does not update that lock.

Fixtures carry explicit case IDs and inputs, including known zero-drive and direction/rotation/translation variants. Numerical tests record all sample/component errors and per-case maximum/RMS values via pytest's JUnit properties. A clean-source test report can be reproduced with `pytest tests/test_plane_wave.py -o junit_family=xunit1 --junitxml=<unused-local-path>`. JUnit is a software verification report, not a RunManifest or scientific evidence bundle. Record its digest, exact source/fixture identity and environment with the review; do not promote it to P3 PASS. Physical run admission, gradient-index linking and independent post-audits remain required before ANA-07's recorded campaign.

## Minimal Python example

This evaluates a manufactured field in memory. It creates no recorded scientific run or validation verdict. The explicit lossless inputs and observation box are part of this example, not physical defaults.

```python
from aura.fields import PlaneWave, evaluate_plane_wave, mean_intensity_w_m2

wave = PlaneWave(
    density_kg_m3=1000, sound_speed_m_s=1500, frequency_hz=1_000_000,
    peak_pressure_pa=2, direction=(1, 0, 0), reference_m=(0, 0, 0),
    phase_rad=0, dynamic_viscosity_pa_s=0, amplitude_attenuation_per_m=0,
)
field = evaluate_plane_wave(
    wave, [(0, 0, 0), (0.000375, 0, 0)],
    box_min_m=(-0.0015, -0.0015, -0.0015),
    box_max_m=(0.0015, 0.0015, 0.0015), workspace_bytes=2 * 1024**2,
)
print(field.pressure_pa)
print(mean_intensity_w_m2(field))
```
