# NUM-03 Field-Error Protocol Basis

**Status:** DRAFT — comparison method specified; numeric acceptance budget not justified
**Prepared:** 2026-10-04 · **Decision basis:** DEC-006, DEC-007; D00, D03–D07

## Purpose and boundary

This record separates a reproducible comparison method from the numerical requirement that would turn the comparison into a pass/fail gate. It applies only to the ideal homogeneous, lossless, linear air-field model in the [P4 solver contract](air-field-solver-contract.md): the 25.230 kHz baffled piston and stationary sound-hard sphere, gap samples `0.1–30.0 mm` at `0.1 mm` intervals, and the accepted source-series domain `a <= r < d`. It does not validate the experiment, material properties, measured source amplitude, acoustic force, acceleration, or gravity-like response.

## Evidence audit

The approved P1.3 gap coordinates identify 300 measurement conditions for an axial **force** curve. The retained values are digitized from a plot, have no pointwise measurement uncertainty, and are not field observations. The air solver contract supplies an ideal mathematical field model and analytical checks, but no application-derived pressure, velocity, or pressure-gradient error requirement. DEC-007 deliberately keeps later force and acceleration budgets separate.

Consequently, neither the P1.3 plot-reading spread, the source's proposed 2% simple-wave target, the order-512 tail estimate, nor finite-order agreement supplies a defensible acceptance threshold for these three complex field observables. The tail estimate is a bound on one error source, not a target. The source's field is also not an independent measured reference. Choosing a percentage now would add an assumption not present in the approved record.

## Comparison method that can be fixed now

For every frozen sample set and gap, compare each truncation with a separately implemented, higher-precision evaluation of the same stated model. Use the same coordinates and source normalization. Do not fit a phase shift. Keep these observables distinct:

- complex pressure, with residual magnitude in Pa;
- complex Cartesian particle velocity, with vector residual norm in m/s;
- complex Cartesian pressure gradient, with vector residual norm in Pa/m.

For each observable `X`, report the maximum absolute local error and a weighted RMS absolute error over a coordinate set whose points and weights are frozen before execution. Report the full complex component residuals as well as those summaries. Use a protocol-declared absolute scale for near-zero interpretation; do not divide by a local reference value near a node. Keep errors grouped by gap so that large- and small-gap cases cannot mask one another.

Keep the following contributions separate: (1) the order-greater-than-512 mathematical tail bound, (2) floating-point sensitivity, (3) source-integral/quadrature sensitivity, and (4) uncertainty in the finite-precision reference evaluation. A conservative sum may be reported only where each contribution has a defensible bound and dependency assumptions are stated. The current exact-rational candidate bounds address only (1). Existing Decimal and cross-formulation comparisons are finite-grid sensitivity evidence, not rigorous bounds on (2)–(4), and were not produced by an external reviewer.

The 300 prescribed gap values are the comparison conditions; no interpolation claim is implied between them. Any finite spatial set supports a claim only at those coordinates. The existing all-angle/all-radius modal-tail bound is separate mathematical coverage and does not make a finite field-value comparison exhaustive.

## Preconditions for a numerical acceptance budget

Before a numeric threshold or broad NUM-04 run can be frozen, the record needs all of the following:

1. A field-specific accuracy requirement tied either to a named downstream use or to a justified numerical-verification objective. Do not back-derive it from a force or acceleration target that DEC-007 deferred.
2. A deterministic coordinate set and weights for each field observable, including coverage of both sphere-near and outer-shell regions and a statement of what is not covered.
3. At least three declared harmonic truncations within the existing order-512 cap, with all observed increments retained. Nonmonotone increments must not be converted into a fitted convergence rate.
4. Independent quadrature and precision checks on the same coordinates, plus a reference uncertainty method that is credible for the full selected domain.
5. A stopping/acceptance rule that compares the separately reported numerical contributions with the justified requirement, and a workload-specific RAM, storage, and wall-time cap.

The four-gap Decimal checks, sparse finite-order diagnostics, and exact-context one-point run do not yet satisfy these prerequisites across the 300-gap benchmark. No broad convergence, boundary-sensitivity, or force calculation is authorized by this draft.

## Current disposition

**Numeric field tolerance: not established. P4: INDETERMINATE. NUM-03: ACTIVE. NUM-04: BLOCKED.** Continue only bounded work that can qualify the reference/error sources or improve the protocol without implying acceptance. If no field-use requirement or credible full-domain reference can be supplied from the approved scope, retain the indeterminate outcome and record the unmet gate; do not manufacture a number to advance the phase.

## Bounded 29.9 mm reference-sensitivity check — 2026-10-05

A 300-digit Decimal direct Rayleigh-disk/modal evaluation was completed at the sampled gap with the largest candidate modal-tail bounds, `H=29.9 mm`, at modal order 512. It used 37 angles (5° through 185° in 5° increments) and three radii about the sphere center (`a`, `a+H/2`, and `a+0.99H`), for 111 paired locations. The density was `1.18 kg/m³`, sound speed `346 m/s`, frequency `25,230 Hz`, piston radius `10 mm`, and sphere radius `25 mm`. Chudnovsky arithmetic supplied pi. Two direct source integrations used Gauss–Legendre radial rules 128 and 256.

At the same 111 coordinates and order 512, the Decimal direct calculation and public evaluator's normalized maximum differences were `1.1989151141414599e-13` for pressure and `6.428369600122808e-14` / `6.426741197042954e-14` for velocity / pressure gradient. This is finite-grid, same-model, same-order cross-formulation agreement; it does not measure truncation, establish a reference uncertainty, or validate the model physically.

The computed R128/R256 paired differences were reported near `10^-235` after 300-digit field evaluation. That number is retained as the output of the finite arithmetic comparison, but no rounding analysis or rigorous quadrature remainder supports interpreting it as an error estimate. In particular, it cannot establish quadrature accuracy or a total reference uncertainty. The two methods may share errors, cover only one gap and 111 points, and are not a measured field reference. Do not use the tiny paired difference as a pass criterion or to launch broad NUM-04.

The successful diagnostic and comparison JSON files, scripts, logs, hashes, and failed attempts remain local under ignored `results/diagnostics/`. The summary metadata SHA-256 is `a8fad79b6caea510e504ea222df6c41e68f6a2cad86527cf141ef4e7a5493908`; the paired-comparison JSON SHA-256 is `ce6201f808d672a03e7bb4b55e4db01a0bc3ddb110aeb6d0d5ea518bfcd20ff8`. An earlier pair of scripts labeled 29.9 mm actually ran at 30 mm because a later assignment overrode the gap; those attempts are preserved with their actual 30 mm metadata and excluded from this result. Summary-harness failures are also preserved. The corrected run metadata explicitly asserts `gap_m=0.0299`, both radial-rule orders, density, order, and all 111 coordinates.

This bounded check does not complete the reference-uncertainty method. Continue by investigating a quadrature/reference route whose uncertainty is independently justified over the frozen comparison domain; keep the current sample comparison exploratory, NUM-03 ACTIVE / INDETERMINATE, and NUM-04 BLOCKED. No tolerance, solver-domain change, force result, or physical-validation claim follows.

### Three-level radial-rule refinement at the same gap — 2026-10-05

A third 300-digit evaluation added radial Gauss–Legendre order 64 to the same order 512 field comparison, retaining rules128 and256 and the exact same 111 coordinates at `H=29.9 mm`. The computed maximum differences between rules 64/128, normalized by the higher-rule grid maxima, were `6.2342e-67` for pressure and `2.0721e-65` for both velocity and pressure gradient. For rules 128/256, they were `6.3686e-237`, `2.1221e-235`, and `2.1221e-235`, respectively. These are recorded finite outputs from one same-family quadrature refinement; the roughly 170-order drop does not itself bound the integral error, account for shared arithmetic/model error, or certify the 111-point grid.

The three-rule metadata SHA-256 is `14ff3d006184b112c6242eecb7f2d11e7ee053baae8aca279fd58d97e3b5a41b`; it binds 17 local scripts, JSON outputs and logs, each checksum-verified. The radial64 run completed in 54.48 s on ENV-1.0. A deterministic comparison summary was generated twice and matched byte-for-byte. This remains one gap and one finite spatial set. A genuinely independent quadrature/reference uncertainty method over the full frozen domain is still missing; NUM-03 remains ACTIVE / INDETERMINATE and NUM-04 remains BLOCKED.

## Cross-family quadrature checks at four fixed gaps — 2026-10-05

To test whether the very close Gauss–Legendre 128/256 values alone were informative, the direct source integral was also evaluated with composite Simpson quadrature in the squared-radius variable `u=(r/R)^2`. The gap, 37 angles, three sphere-centered radii, 111-point grid, Decimal precision (300 digits), ideal model and modal order (512) were held fixed. Simpson weights/nodes passed a separate Decimal check of symmetry, positivity and polynomial moments 0–3 through 8192 panels with absolute moment residuals below `1e-285`; this verifies rule construction, not its field-integral remainder. A checker failure on `0**0` is preserved with the corrected rerun.

At the difficult 29.9 mm sample, Simpson panel counts 128, 256, 512, 1024, 2048, 4096 and 8192 were compared with Gauss–Legendre orders256 and512. At 0.1 mm, orders 256/512 and Simpson panel counts2048,4096,8192 and16384 were compared. The same Gauss–Legendre 256/512 and Simpson 2048/4096/8192 comparison was then run at the interior gaps 10 and 20 mm. Each gap uses radii `a`, `a+H/2`, and `a+0.99H`. Maximum differences are normalized by the higher-rule grid maximum; velocity and pressure-gradient ratios coincide to displayed precision because they are linearly related in this harmonic field.

| Gap | GL256 vs GL512 (velocity/gradient) | Last Simpson doubling (velocity/gradient) | Highest Simpson vs GL512 (velocity/gradient) |
|---:|---:|---:|---:|
| 29.9 mm | `5.47e-293` | 4096→8192: `1.486e-6` | 8192 vs GL512: `9.916e-8` |
| 0.1 mm | `3.95e-292` | 8192→16384: `5.857e-4` | 16384 vs GL512: `3.926e-5` |
| 10 mm | `4.70e-292` | 4096→8192: `8.392e-5` | 8192 vs GL512: `5.626e-6` |
| 20 mm | `4.70e-292` | 4096→8192: `7.096e-6` | 8192 vs GL512: `4.740e-7` |

At 29.9 mm, pressure differences for the last Simpson doubling and highest Simpson-vs-GL512 comparison are `5.354e-8` and `3.572e-9`; at 0.1 mm they are `5.727e-6` and `3.838e-7`. At 10 mm the corresponding pressure values are `2.142e-6` and `1.435e-7`; at 20 mm they are `2.899e-7` and `1.936e-8`. At all four fixed gaps the late Simpson adjacent-level change drops by about a factor of 16 when panels double, consistent with fourth-order asymptotic behavior. The difference from GL512 is also close to a conditional Richardson residual based on that assumption. This is useful numerical consistency evidence, not a proof of an asymptotic remainder or a quadrature error bound.

The result changes the interpretation of the earlier same-family checks: near-identical GL256/512 values did not by themselves qualify the source integral, because they can conceal shared error. A distinct quadrature family approaches the high-order Gauss–Legendre result at four tested gaps. Residuals and runtime increase at the tighter 0.1 mm case; this confirms the need to retain gap-specific resources and uncertainty. Four gaps with 111 coordinates each do not establish uncertainty for all 300 gap samples or unsampled field coordinates. Both computations target the same ideal model and can share arithmetic, recurrence, modal-tail and physical-model errors.

The 29.9 mm metadata SHA-256 is `45b5aba0748f817996c89f6f042400336c7ceb987be257adc36b65ec990b22d8` (79 bound artifact files). The 0.1 mm metadata SHA-256 is `265051700d7dcdb6e7b10e1434deef42491fc440335d0c665ec53d63668e2145` (39 bound artifact files). Both manifests were rechecked against every recorded file checksum. Keep P4 INDETERMINATE, NUM-03 ACTIVE and NUM-04 BLOCKED; do not adopt a tolerance, call this a full-domain reference, or imply physical validation.

The 10 mm metadata SHA-256 is `fba7d53d167a1d7797ae4e984ca09f32c87aad5711883dd1b00f2edcd9946d5c` (28 artifacts); the 20 mm metadata SHA-256 is `816746ed70c9181d2e1aa984d852561e8c1ec7f9269f602c9fdbc360253fec40` (25 artifacts). These manifests were checksum-verified. The corrected 10 mm summary attempt follows a preserved assertion/name failure; no field JSON was altered.

### Comparison-summary label correction — 2026-10-05

A post-publication audit found that the 10 and 20 mm comparison JSON summaries retained a copied classification string saying “0.1 mm,” although their bound field records and `configuration.gap_m` values were `0.01` and `0.02` m. The error was in descriptive metadata only; all comparison payloads were checked unchanged against corrected, independently rerun summaries. The original mislabeled files remain preserved. Their corrected replacements now include the configured gap in the label, and each corrected JSON and stdout reproduced byte-for-byte on a second run.

The 10 mm label-correction manifest SHA-256 is `5b819768c82fb8cf6dd522cd7066b4cae58159dac7f69d3373941055b304cd2b`; the 20 mm manifest SHA-256 is `022904402ab1f386830576799d6c473a898fe76dd60686ed239f9deb0105376f`. They bind the corrected scripts and outputs and record the prior summary hashes. Two post-generation validation harness attempts are also preserved: one asserted `10` rather than the correctly formatted `10.00`, and another omitted its `Decimal` import. Neither changed numerical data; the passing correction rerun verifies the label against the configuration numerically. This repair changes traceability only, not the four-gap scientific interpretation or any gate.

## Candidate composite-Simpson remainder route — 2026-10-05

The composite Simpson theorem gives, for even panel count `N` and `g` with a continuous fourth derivative on `[0,1]`, `|integral(g)-S_N(g)| <= max|g^(4)|/(180 N^4)`. This is the standard error formula in [NIST DLMF §3.5(ii), Eq. 3.5.8](https://dlmf.nist.gov/3.5.E8). Apply it separately to real and imaginary parts of a complex modal integrand.

For the direct source-modal radial rule used in the diagnostics, `x` is the uniformly spaced Simpson coordinate on `[-1,1]`, and `u=(x+1)/2` is squared source radius. The code's prefactor and coordinate map satisfy `(R^2/4) integral_{-1}^1 q((x+1)/2) dx = (R^2/2) integral_0^1 q(u) du`. An exact-`Fraction` check with `q(u)=u^4` confirmed the map and remainder factor at 2, 4, 8, 16 and 32 panels; after the `R^2/2` prefactor, the error magnitude equals `R^2/(15 N^4)` for this test polynomial. The corrected check metadata SHA-256 is `6fc6b84c2ae4b4d1341c84d47d218f9e7779a6e91d3edd45a2b8c50cefcde1bc` (six bound artifacts); summary SHA-256 is `a7e6b97ef2d1d902fdf8a15d9117311f0fd92fdad18db1125b65b34ac69005f7`. An earlier summary omitted the derivative mark in its prose formula; that report-assembly defect is preserved, and the corrected attempt retained identical rational test values.

This supplies a theorem and a verified coordinate factor, but not a full AURA quadrature bound. For each source mode `n`, the required integrand is proportional to `q_n(u;D)=P_n(-D/s) h_n^(1)(ks)`, with `s=sqrt(D^2+R^2 u)` in the project's `exp(-iwt)` convention. A useful certified field bound would require outward-enclosed maxima of the fourth derivatives of both components for all 512 retained modes and all 300 approved gap samples, then propagate them through the pressure, velocity and pressure-gradient modal factors over the declared radius/angle domain. The enclosure arithmetic and special-function/recurrence rounding must also be bounded separately.

A first exact-rational majorant now covers only mode `n=0` of the source coefficient at `H=0.1 mm`. Since `P_0=1` and `h_0^(1)(ks)=-i exp(iks)/(ks)`, elementary differentiation with `s>=D=a+H` gives `max_u |d^4q_0/du^4| <= 0.138000671955546614706827784474` using rational bounds on `k`. After the complex-component factor and the `R^2/2` coefficient prefactor, the resulting absolute Simpson coefficient-error upper bound at 8192 panels is `1.70235026020878865342936918492e-23 m^2`; at 2048 panels it is `4.35801666613449895277918511338e-21 m^2`. The values shown are upward-rounded decimal displays; attempt 01 is preserved because its nearest-rounded displays were not guaranteed to remain above the exact fractions. The corrected attempt 02 keeps those exact fractions, rounds every decimal display upward, and verifies each display is no smaller than its exact rational value. Metadata SHA-256 is `5f4af5033a7a1264868e13f0bf56263bb42c2a0840cfee831c86d7d837659a3a` (five bound artifacts), and the exact summary SHA-256 is `4f232bb9ec2712ce29250b99a975be3fe86c604276b0f93007b19b74b71b411f`.

This bound is for one source coefficient mode and one gap only. It is not propagated to any field observable, does not cover `n>0`, the other 299 approved gaps, Gauss–Legendre/reference uncertainty, or implementation rounding. No full derivative maxima, propagated field bound, or useful total tightness result is established. The theorem and this mode-zero demonstration therefore do not qualify the reference, set a tolerance, or change NUM-03/NUM-04 status.

A second exact-rational prototype covers source mode `n=1` at the same `H=0.1 mm`. NIST DLMF §10.49(i), Eqs. 10.49.1 and 10.49.6 give `h_1^(1)(z)=-exp(iz)(z+i)/z^2`; with `P_1(-D/s)=-D/s`, the source integrand becomes `q_1=D exp(iks)[1/(k s^2)+i/(k^2 s^3)]`. Leibniz bounds on each exponential/Laurent term, followed by the same exact chain-rule envelope, give `max_u |q_1^(4)| <= 0.207482139764438138107653472730`, versus `0.138000671955546614706827784474` for mode zero; the exact-rational ratio is `1.50348644556798390340844903367`. The mode-1 coefficient Simpson remainder bound at 8192 panels is `2.55946054183304415606263602743e-23 m^2`. Decimal displays are rounded upward and checked against exact fractions. Metadata SHA-256 `847adbbe6f03491b9bd208b3808ab957f24f669db78792ef033f29c2b77a2928`; output SHA-256 `79697b14568b0f9b6bd20869e7111fa81937e2309ebc41695f7eb9716c70cf17`.

The mode-1 calculation is also coefficient-only at one gap. Its triangle-inequality envelope is a prototype, not evidence that the method stays tight at higher orders. It does not cover the other gaps, propagate into any field observable, or bound reference/evaluator/physical-model error. No tolerance or NUM-03/NUM-04 status change follows.
