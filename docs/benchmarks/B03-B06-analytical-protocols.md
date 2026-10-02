# B-03…B-06 — Frozen Analytical Reference Protocols

**Version:** ANA-REF-1.0 · **Date:** 2026-10-02 · **Status:** reference protocol frozen; B-03 kernel verification in [ANA-02](../work-items/ANA-02.md) and B-04 in [ANA-03](../work-items/ANA-03.md); recorded P3 campaign not executed

Authority: D04/D06, [FIELD-1.0](../research/analytical-field-contract.md), [source review](../research/analytical-source-review.md). These are manufactured mathematical verification cases. They contain no experimental observations, physical-object result or AURA feasibility conclusion.

## Shared inputs and measurements

- Exact manufactured decimal inputs: `rho = 1000 kg/m^3`, `c = 1500 m/s`, `f = 1000000 Hz`, base peak pressure `A = 2 Pa`, zero viscosity and amplitude attenuation. These values do not constitute a selected experimental water state.
- `lambda = 0.0015 m`, `Z = 1500000 kg/(m^2 s)`, `k = 2 pi/lambda`. Observation box: each chamber coordinate in `[-lambda,lambda]`, inclusive. All unspecified coordinate components in the tables are explicitly zero.
- No bodies/walls are coupled; prescribed incident fields exist throughout the observation box, except the B-06 excluded source region. No initial-value solution or transient startup. Reconstructed real-time checks use `t = 0,T/4,T/2,3T/4`, `T = 1/f`; flux means an exact average over one period.
- Source reference points are `(0,0,0)`, phases zero unless specified below. Every source retains its own amplitude; there is no division by source count. Coordinates are evaluated directly; no interpolation or discretization error is claimed.
- Tables below show `p/A`, `Z v/A`, `grad(p)/(k A)` and `I/(A^2/(2 Z))`. Each vector contains chamber components. A literal zero is an expected component value, not permission to omit it. `i` means the imaginary unit; machine fixtures must use real/imaginary numeric pairs.

## B-03 — Progressive plane wave (ANA-02)

One source in `+x`, amplitude A. Quarter-turn phasors follow from exact sine/cosine values, independently of a future exponential implementation.

| ID | x/lambda | p/A | Z v/A | grad(p)/(k A) | Normalized flux |
|---|---:|---|---|---|---|
| B03-01 | 0 | 1 | (1,0,0) | (i,0,0) | (1,0,0) |
| B03-02 | 1/4 | i | (i,0,0) | (-1,0,0) | (1,0,0) |
| B03-03 | 1/2 | -1 | (-1,0,0) | (-i,0,0) | (1,0,0) |
| B03-04 | 3/4 | -i | (-i,0,0) | (1,0,0) | (1,0,0) |
| B03-05 | 1 | 1 | (1,0,0) | (i,0,0) | (1,0,0) |

Additional mandatory configurations:

1. Reverse direction to `-x` at x=lambda/4: p/A=-i, Z v/A=(i,0,0), gradient/(k A)=(-1,0,0), normalized flux=(-1,0,0).
2. Direction `(3/5,4/5,0)`, point `(5 lambda/12,0,0)`: p/A=i, Z v/A=(3i/5,4i/5,0), gradient/(k A)=(-3/5,-4/5,0). This tests more than an axis permutation.
3. Apply the proper rotation `(x,y,z) -> (y,z,x)` to all geometry and vectors; scalar pressure is unchanged. Translation by `(lambda/4,0,0)` of both source references and observation points is unchanged wherever the translated samples remain in the box. Rotating only the samples is not this symmetry.
4. Set source phase to pi/2 at its reference point: p/A=i. At that point real p/A at the four stated times is `(0,1,0,-1)`, checking the negative time sign.
5. Zero source amplitude: all physical outputs exactly zero. Use the original nonzero A as the error scale. Test invalid direction, frequency, medium, nonfinite input and unsupported loss before allocation; never normalize a malformed direction silently.

## B-04 — Counterpropagating waves (ANA-03)

Two sources, +x and -x, each amplitude A and phase zero. Independent real identities give p/A=2 cos(kx), Z v_x/A=2 i sin(kx), and gradient_x/(k A)=-2 sin(kx).

| ID | x/lambda | p/A | Z v/A | grad(p)/(k A) | Normalized flux |
|---|---:|---|---|---|---|
| B04-01 | 0 | 2 | (0,0,0) | (0,0,0) | (0,0,0) |
| B04-02 | 1/4 | 0 | (2i,0,0) | (-2,0,0) | (0,0,0) |
| B04-03 | 1/2 | -2 | (0,0,0) | (0,0,0) | (0,0,0) |
| B04-04 | 3/4 | 0 | (-2i,0,0) | (2,0,0) | (0,0,0) |

Mandatory variants: (a) at the origin, give the -x wave phase pi/2: p/A=1+i, Z v/A=(1-i,0,0), gradient/(k A)=(1+i,0,0), net flux zero; (b) +x amplitude 2A and -x amplitude A, zero phases: p/A=3, Z v/A=(1,0,0), gradient/(k A)=(i,0,0), normalized flux=(3,0,0). The independent flux reference is `(A_plus^2-A_minus^2)/(2 Z)`, not the pressure-squared helper. A pressure node with nonzero velocity must survive serialization and reporting.

## B-05 — Noncollinear interference (ANA-04)

Two waves in +x and +y, each amplitude A, reference points zero, phases zero. Differentiate the independent separated expression `p/A = cos(kx)+cos(ky)+i(sin(kx)+sin(ky))` to obtain the table; each velocity component belongs to its source direction.

| ID | (x,y)/lambda | p/A | Z v/A | grad(p)/(k A) | Normalized flux |
|---|---|---|---|---|---|
| B05-01 | (0,0) | 2 | (1,1,0) | (i,i,0) | (2,2,0) |
| B05-02 | (0,1/2) | 0 | (1,-1,0) | (i,-i,0) | (0,0,0) |
| B05-03 | (1/4,0) | 1+i | (i,1,0) | (-1,i,0) | (1,1,0) |
| B05-04 | (1/4,1/4) | 2i | (i,i,0) | (-1,-1,0) | (2,2,0) |

Mandatory variants: interchange source order without changing the field; apply the B-03 proper rotation; multiply both source phasors by i and require p/v/gradient to multiply by i while mean flux is unchanged. Deliberately summing scalar speeds or averaging the two source pressures must fail these cases. Cancellation does not authorize replacing velocity/gradient with zero.

## B-06 — Spherical spreading (ANA-05)

One ideal outgoing spherical reference centered at zero, `r_ref=lambda/4`, `P_ref=A`, phase zero; require `r >= r_min=lambda/4`. Three samples lie on +x, inside the observation box. This tests a spreading reference useful for later open-domain comparisons; it does not select a physical radiator or a dissipative medium.

| ID | r/r_ref | p/A | Z v_x/A | gradient_x/(k A) | Normalized radial flux |
|---|---:|---|---|---|---:|
| B06-01 | 1 | 1 | 1+2i/pi | -2/pi+i | 1 |
| B06-02 | 2 | i/2 | -1/(2pi)+i/2 | -1/2-i/(2pi) | 1/4 |
| B06-03 | 3 | -1/3 | -1/3-2i/(9pi) | 2/(9pi)-i/3 | 1/9 |

Other components are zero. Repeat B06-01 on -x and +y: pressure unchanged, vectors radial with corresponding sign/direction. Reject r=0 and r<r_min before evaluation. No near-field value is replaced by `v=p/Z`; B06-01 must expose the missing reactive component. `r_min` is a chosen exclusion for this experiment, not a transducer validity certificate.

Project derivation: differentiate `(r_ref/r) exp(i k(r-r_ref))`, then apply linear Euler's equation. Taking the real part of p times conjugate velocity cancels the imaginary reactive term, giving radial flux proportional to `1/r^2` for this exact ideal solution. The outward spherical surface power is `4 pi r_ref^2 A^2/(2Z)`, independent of radius; this is an energy-flux reference for ANA-06, not a universal acoustic-force bound. No absorbing coefficient or finite-piston approximation is introduced.

## Error budget frozen before solver implementation

Use binary64 epsilon `e = 2^-52`. Compare each complex component by its complex absolute difference; compare flux components as real values. Let `C` be the sum of source peak amplitudes (C=A, 2A or 3A here). The fixed nonzero scales are `S_p=C`, `S_v=C/Z`, `S_g=k C`, `S_I=C^2/(2Z)`. For the zero-drive case retain C=A. For B-06 use `S_p=A`, `S_v=(A/Z)(1+2/pi)`, `S_g=k A(1+2/pi)`, `S_I=A^2/(2Z)`, covering the admitted minimum radius conservatively. Never divide by a local reference that vanishes at a node.

For every quantity report `E_max=max(abs(actual-reference)/S)` and `E_rms=sqrt(mean((abs(actual-reference)/S)^2))`, over all declared samples/components. Require E_max <= `2048 e` (approximately 4.548e-13); E_rms is also reported and must not hide a failed component. Separately evaluate direction/phase and the typed rejections above. A flux comparison alone cannot pass a complex field.

Budget derivation for this fixed matrix (no mesh truncation or measurement uncertainty): assume round-to-nearest arithmetic with unit roundoff `u=e/2`, no overflow/underflow, at most 32 dependent rounded operations on an elementary argument/scale path, and elementary sine/cosine absolute error <=4e on the selected arguments. Accumulating 32 relative arithmetic errors gives `gamma_32 = 32u/(1-32u)`, approximately 16e. Require the sum of absolute phase contributions, including translated-reference subtraction, to be <=8 pi; the corresponding phase perturbation allowance is `8 pi gamma_32 < 403e`. Since sine/cosine are 1-Lipschitz, the complex phasor perturbation from argument error is bounded by that argument perturbation; add the two elementary-function component errors, source summation, scale/derivative arithmetic and reference conversion. A conservative component budget is 512e on the stated scales. The implementation must document its operation/argument bounds; this is an explicit numerical model, not a universal floating-point guarantee.

For flux, the product perturbation is bounded by the sum of the two component perturbations plus their product. With `b=512e`, the plane-family normalized bound is `2b+b^2` before product rounding. The spherical scale adds a factor `1+2/pi < 1.637`; even adding 64e for product/real-part/reference arithmetic gives `<1741e`. Round this analytical budget upward to the predeclared 2048e envelope for all reported quantities. This intentional margin is fixed before any field implementation or outcome exists.

ANA-02 must check the elementary-function assumption against an independent high-precision reference on these arguments and audit the operation/scale path before this budget can support evidence. If an assumption or tolerance fails, preserve the discrepancy and review the backend/error analysis before any new protocol version; do not tune the tolerance to the observed error.

Quarter-turn reference values are exact integers/rationals. For pi-dependent B-06 values and nontrivial geometry conversions, prepare >=40-decimal-digit references independently (document constant/precision and final binary64 rounding); do not call `fields/analytic.py` or its helpers to produce the oracle. The named budget applies only to this matrix, not arbitrary huge coordinates, near-singular evaluation, many sources, other precision or a percentage physical-accuracy claim.

## Execution, audit and stop rules

- **ANA-01:** freeze these tables and validate the output container only. All B-03…B-06 numerical comparisons remain NOT_RUN.
- **Owning ANA card:** publish exact input fixture, independent numeric oracle, model implementation and tests. Include all variants, a parameter-to-protocol mapping and immutable case IDs; do not replace an earlier failure with a successful configuration.
- **Recorder admission:** follow FIELD-1.0. At most 32 configurations, N<=256 and M<=2, one CPU/no GPU, no randomness, 16 MiB bundle allowance and 30 s execution cap per run; preflight RAM from the contract and measure actual usage. Stop on cap excess, nonfinite values, unavailable required component or unsupported source region. No adaptive sweep.
- **ANA-06/07:** independently check declared balances and emit stored reference errors, plots and reproducible manifests. Report execution success separately from numerical verification, MCLF status and experimental/model validation. No P3 PASS until the selected admitted cases actually run and meet their criteria.
- Sign/amplitude errors: F-01; unsupported model/geometry: F-03; numeric error: F-04; balance error: F-06; resource excess: F-05; provenance/reproduction failure: F-09/F-11. After two failures of one cause, write the root-cause record before a third attempt.
