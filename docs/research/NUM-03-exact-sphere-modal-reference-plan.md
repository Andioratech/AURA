# NUM-03 Exact-Sphere Modal Reference Plan

**Status:** DRAFT — owner authorized bounded implementation on 2026-10-09; numerical claims remain exploratory
**Date:** 2026-10-08
**Scope:** One manufactured, axisymmetric Helmholtz trace on a rigid sphere above a Neumann plane
**Decision basis:** DEC-007, DEC-008; NUM-03 remains ACTIVE / INDETERMINATE

## 1. Purpose and boundary

This plan defines an independent spherical-harmonic calculation for the direct and plane-reflected contributions in the exact-sphere combined boundary-integral equation (CBIE) diagnostic. Its purpose is to determine whether the direct ring-quadrature layers and their cancellation can be checked by a method that does not traverse source azimuth rings.

The source amplitude is normalized to one Green-function strength. The formulas below therefore produce Green-function values in `m^-1`; multiplying by the benchmark's implicit `Q=1 Pa m` source normalization produces the reported `Pa`. All layer bounds scale by `|Q|`; they are not calibrations of a physical transducer.

The benchmark is a manufactured solution: a free-space monopole at the sphere center plus its same-sign mirror monopole. The sphere is a mathematical integration surface, not an obstacle that changes the manufactured field. This work checks numerical representations of that one ideal trace. It does not calculate a force or trajectory, validate a physical apparatus, establish field acceptance, or show that AURA produces gravity.

This is a reviewable derivation and implementation plan. It does not authorize a matrix, solve, BEM backend, or simulation core. Any modal implementation remains subject to the project's existing resource, reproducibility, and scientific review requirements.

## 2. Frozen case and conventions

| Quantity | Frozen value or convention |
|---|---|
| Sphere radius, `a` | `0.025 m` |
| Plane-to-sphere gap, `g` | `0.0001 m` |
| Sphere center height, `d=a+g` | `0.0251 m` |
| Center spacing to mirror source, `L=2d` | `0.0502 m` |
| Frequency | `25,230 Hz` |
| Sound speed | `346 m/s` |
| Wavenumber | `k=2 pi f/c` |
| Point-source normalization | Unit Green-function strength, interpreted as `Q=1 Pa m` so benchmark terms are reported in Pa; the Green function alone has units `m^-1` |
| Phasor and Green function | `exp(-i omega t)`; `G(R)=exp(+ikR)/(4 pi R)` |
| Collocation angles | First `179°`; then the already-used `120°`, `135°`, and `175°` cases |
| Sphere coordinates | `r=a`, polar angle `theta` measured from `+z`, azimuth `phi` |
| AURA source normal | Inward radial normal, `n_in=-e_r`; `q=partial_n_in p` |
| CBIE residual | `R=0.5 p + K_direct + K_image - V_direct - V_image` |

The point source in the upper sphere center and its reflected point below the plane are both used to form the trace on the upper sphere. The current benchmark code is the controlled geometry/convention record. The 14/16 subdivision review records its full source revision, environment, outputs, and scope.

## 3. Primary equations and derivation

The free-space outgoing addition theorem follows by combining the cosine and sine spherical-Bessel addition formulas in NIST DLMF Eqs. 10.60.1–10.60.2. For `r_< < r_>` it gives

`G(x,y) = i k sum_{n=0}^infinity (2n+1)/(4 pi) j_n(k r_<) h_n^(1)(k r_>) P_n(cos gamma)`.

The condition in DLMF is the smaller radial argument strictly below the larger one; it is not an unrestricted rearrangement at coincident radii. `h_n^(1)=j_n+i y_n` matches the project's `exp(+ikR)` Green function. Spherical-harmonic orthogonality and the addition-theorem normalization follow DLMF Eqs. 14.30.8–14.30.9; the spherical-Bessel Wronskian used for the jump check is DLMF Eq. 10.50.1.

### 3.1 Manufactured pressure and normal-derivative coefficients

Let `h_n=h_n^(1)`, and define `j_n=j_n(ka)`, `j'_n=j'_n(ka)`, `h_n=h_n^(1)(ka)`, and `h'_n=h_n^(1)'(ka)` when the argument is not shown. The direct monopole is `G_direct(r)=i k h_0^(1)(kr)/(4 pi)`. The mirror source lies on the negative axis, a distance `L` from the upper sphere center. Applying the outgoing addition theorem gives the following axisymmetric boundary-trace expansion:

`p(a,theta) = sum_n p_n P_n(cos theta)`,

`p_n = i k/(4 pi) delta_{n0} h_0^(1)(ka) + i k (2n+1)(-1)^n h_n^(1)(kL) j_n(ka)/(4 pi)`.

The factor `(-1)^n` is the Legendre parity for the source direction `-z`. Because the AURA normal points inward,

`q(a,theta) = sum_n q_n P_n(cos theta)`,

`q_n = -k [i k/(4 pi) delta_{n0} h_0^(1)'(ka) + i k (2n+1)(-1)^n h_n^(1)(kL) j_n'(ka)/(4 pi)]`.

These coefficients are derivatives of the manufactured field with respect to the physical sphere's inward radial normal. They are not the sound-hard scattering boundary condition.

### 3.2 Direct free-space layer eigenvalues

For an axisymmetric density mode `P_n(cos theta)` on one sphere, spherical-harmonic orthogonality diagonalizes the direct single-layer operator. With the project Green function and surface measure `dS=a^2 dOmega`, its eigenvalue is

`V_n = i k a^2 j_n(ka) h_n^(1)(ka)`.

The principal-value direct double-layer eigenvalue for the **outward** source normal is the average of its interior and exterior radial limits:

`K_out,n = i k^2 a^2/2 [j'_n(ka) h_n^(1)(ka) + j_n(ka) h_n^(1)'(ka)]`.

The AURA inward normal reverses this sign, so `K_in,n=-K_out,n`. Therefore the direct contributions for this trace are

`K_direct(theta) = sum_n K_in,n p_n P_n(cos theta)`,

`V_direct(theta) = sum_n V_n q_n P_n(cos theta)`.

The sign and factor-of-one-half are to be checked in the implementation against the existing exact `n=0` and `n=1` direct-sphere layer tests and the DLMF Wronskian. The `n=0` centered direct-monopole CBIE identity is a mandatory known-answer check before any comparison with ring quadrature.

### 3.3 Reflected layers: exact source-sphere projection

Reflecting a source-surface point across the plane maps the physical sphere onto a second sphere of radius `a`, centered at `C_im=(0,0,-d)`. The center-to-center distance is `L=2d`. The reflected scalar densities have Legendre parity `P_n(-mu)=(-1)^n P_n(mu)`; reflection maps the physical inward normal to the inward radial normal of the image sphere. After that mapping, the source-normal chain rule is represented by the inward radial derivative below.

For a field point on the upper sphere, define its coordinates relative to the image-sphere center:

`R(theta) = sqrt(a^2 sin^2(theta) + (L + a cos(theta))^2)`,

`mu_R(theta) = (L + a cos(theta))/R(theta)`,

`p_tilde_n=(-1)^n p_n`, and `q_tilde_n=(-1)^n q_n`.

The same outgoing addition theorem, now with source radius `a` and target distance `R>a`, plus spherical-harmonic orthogonality gives the separate image terms directly:

`K_image(theta) = sum_n [-i k^2 a^2 j'_n(ka) h_n^(1)(kR) P_n(mu_R)] p_tilde_n`,

`V_image(theta) = sum_n [ i k a^2 j_n(ka) h_n^(1)(kR) P_n(mu_R)] q_tilde_n`.

The minus in `K_image` is the inward derivative on the image source sphere. These formulas analytically integrate each source-surface mode and do not call the ring traversal. Before implementation, independently re-derive the signs and constants from the stated Green function and check n=0 against the existing reflected-monopole identity. Do not infer separate image-layer values by splitting only the known combined identity.

The minimum target distance from the image center is at the lower pole: `R_min=L-a=0.0252 m`, just larger than source radius `a=0.025 m`. The kernel-series radial condition is therefore satisfied for all frozen collocation points. Its raw geometric ratio `a/R_min=0.9920634921...` is close to one. The input modal density for `n>0` already contains the mirror point-source factor with ratio `a/L=0.4980079681...`; a large-order product estimate for the weighted image-layer terms consequently suggests a geometric factor near `(a/L)(a/R_min)=0.4940555239...`, apart from order-dependent polynomial factors. This is a resource-screening hypothesis, not a truncation-error bound. Derive a conservative tail bound for the actual weighted `K_image` and `V_image` series, including derivatives and all selected angles, before selecting a cutoff or claiming truncation control.

If no justified weighted tail bound or conservative resource envelope can be established, retain modal outputs only as finite-sum sensitivity and return an explicit `INDETERMINATE` status. The exact combined image identity remains a separate known-answer check and does not qualify each image layer.

### 3.4 Candidate absolute tail majorant

The following gives a conservative route to a mode-by-mode absolute bound for each image layer. The inequalities are evaluated with outward-rounded Decimal arithmetic in the retained local diagnostic. The derivation still needs independent review before using the bounds to select a cutoff.

For positive real `z`, the power series in DLMF Eq. 10.53.1 gives

`J_n(z) = z^n/(2n+1)!! * exp(z^2/[2(2n+3)])`,

as an upper bound on `|j_n(z)|`. This follows by taking absolute values term by term and using `(2n+2m+1)!! >= (2n+1)!!(2n+3)^m`. From the derivative recurrence in DLMF Eq. 10.51.2,

`|j'_n(z)| <= D_n(z) = (n/z) J_n(z) + J_(n+1)(z)`.

For real positive `z`, DLMF Eq. 10.49.6 is an exact finite expression for `h_n^(1)(z)`. Since `|exp(iz)|=1`, it implies

`H_n(z) = sum_(m=0)^n (n+m)!/[m!(n-m)!(2z)^m z] >= |h_n^(1)(z)|`.

For every image collocation angle, `R(theta) >= R_min=L-a`, `|P_n(mu_R)| <= 1`, and `H_n(z)` decreases with positive `z`, so `H_n(kR(theta)) <= H_n(kR_min)`. For every mode `n>=1`, both image-layer summands therefore have the same absolute majorant:

`B_n = k^3 a^2 (2n+1)/(4 pi) * H_n(kL) H_n(kR_min) J_n(ka) D_n(ka)`.

`B_n` has units `m^-1` for the unit Green function; `|Q| B_n` is in Pa under the stated benchmark normalization. The `n=0` image terms are evaluated separately, including the centered direct-monopole part of `p_0` and `q_0`; they are not part of the tail after a nonnegative cutoff. Summing `B_n` for `n>N` bounds the absolute tail of either `K_image` or `V_image` uniformly over all four frozen angles. This deliberately discards cancellations and the actual Legendre values.

To terminate the infinite bound, the finite Hankel sum also obeys `H_n(z) <= exp(z)(2n-1)!!/z^(n+1)`: index its terms backward from `m=n`; each successive ratio is at most `z/l`, so their sum is bounded by `exp(z)`. Substitution gives

`C_n = [k^3 a^2 exp(z_L+z_R)/(4 pi (2n+1) z_L z_R)] r^n exp(z_a^2/(2n+3)) d_n^+`,

where `z_a=ka`, `z_L=kL`, `z_R=kR_min`, `r=z_a^2/(z_L z_R)=a^2/[L(L-a)]`, and `d_n^+=n/z_a + z_a/(2n+3)`. This replaces the smaller exact derivative factor by a simpler upper bound. For `n>=2000`, `d_{n+1}^+/d_n^+ <= (n+1)/n + z_a^2/[n(2n+5)]`, while the remaining order factor `(2n+1)/(2n+3)` and exponential ratio are below one. At the frozen geometry this gives `C_(n+1)/C_n < r[1+1/2000+z_a^2/(2000*4005)] < 0.495` for every integer `n>=2000`. Thus the residual beyond mode 2000 is bounded by `C_2001/(1-0.495)`.

The finite Hankel majorant can be evaluated in linear time in the maximum order using its positive coefficient recurrence, initialized with `H_0(z)=1/z` and `H_1(z)=1/z+1/z^2`. The spherical-Bessel majorant uses the exact adjacent-order ratio from its closed form. An 80-digit outward-rounded Decimal replay through mode 2000 gives these absolute tail upper bounds for either image layer:

| Cutoff `N` | `sum_(n>N)^2000 B_n` upper bound | Coarse bound above mode 2000 |
|---:|---:|---:|
| 48 | `0.2127293581590253156501681 Pa` | `< 2.849e-598 Pa` |
| 64 | `4.274317711556059065154885e-6 Pa` | `< 2.849e-598 Pa` |
| 80 | `7.207744719959559718521768e-11 Pa` | `< 2.849e-598 Pa` |

These are upper bounds from the stated absolute majorants, not measured truncation errors or physical-source calibration. The ratio envelope is `0.4943106438736159212 < 0.495`; its algebraic bound applies to every integer order `n>=2000`. This supports a very small tail estimate for this one geometry, but does not select a cutoff or accuracy target. The directed-rounding calculator took 0.047 s in CPython 3.12.14; this is only the bound calculator's runtime, not the modal evaluator's runtime or memory estimate. The independent reviewer should check the inequalities, recurrence implementation, and source normalization before cutoff selection. A small image tail does not resolve the separate direct-layer discrepancy or validate the manufactured physical model.

Local ignored record: `results/diagnostics/NUM03-MODAL-TAIL-BOUND-20261008-01/`, source revision `960346a8d384ce0f8c654d9a50110b403a781bb5`; calculator SHA-256 `789cd00497e3154f11de362366d3c7e7286c11cd8d587e18bc0a8adc0e861ee9`, output SHA-256 `01db175cadf460fc0203e5fd82fd6b35288d25c5b1ecd6daf3a3086c377a5eb8`. The two retained output replays match byte-for-byte. The discarded first calculator attempt rounded several endpoints in unsafe directions; its limitation is recorded in `attempt-01-note.md` (SHA-256 `9aa2916406f5925294fd4dcd7864108d345f12bbebf2f3c1cfb0fa6dec7bc288`) and none of its values are used.

### 3.5 Preliminary direct-layer absolute tail majorants

The same inequalities also give a candidate bound for the direct layers. For `n>=1`, `|P_n(cos(theta))|<=1`, and the point-source trace coefficients obey `|p_n| <= k(2n+1) H_n(z_L) J_n(z_a)/(4 pi)` and `|q_n| <= k^2(2n+1) H_n(z_L) D_n(z_a)/(4 pi)`. The direct eigenvalue magnitudes are bounded by `k a^2 J_n(z_a) H_n(z_a)` for `V_n` and `k^2 a^2[J'_n H_n+J_n H'_n]/2` for `K_n`. Consequently the per-mode direct bounds implemented in `tools/research/modal_tail_bounds.py` are

`B_n^V = k^3 a^2(2n+1)/(4 pi) H_n(z_L) H_n(z_a) J_n(z_a) D_n(z_a)`,

`B_n^K = k^3 a^2(2n+1)/(8 pi) H_n(z_L) J_n(z_a) [D_n(z_a)H_n(z_a)+J_n(z_a)H'_n(z_a)]`.

They bound each direct layer uniformly over the four angles; the centered `n=0` source term is included in retained modes and does not enter a tail beyond any selected cutoff. Replacing each finite Hankel factor with the bound above gives coarse tails `C_n^V` and `C_n^K`. The implementation uses the following upper envelopes for `C_(n+1)/C_n` for every `n>=2000`, where `z_a=ka`:

`q_V = (a/L)[1+1/n+z_a^2/(n(2n+5))]`,

`q_K = (a/L)[(4n+5)/(4n+1)+z_a^2/((4n+1)(2n+5))]`.

At `n=2000`, both are below `0.498266`; the bracketed factors decrease for higher integer orders. The remaining direct tails use `C_2001/(1-q_K)` and `C_2001/(1-q_V)` respectively. The candidate implementation evaluates finite terms through order 2000 with 80-digit directed Decimal operations and adds these geometric remainders. The four-layer certificate is regenerated by the maintained evaluator and included in its immutable output record.

| Cutoff `N` | Direct `K` tail upper bound | Direct `V` tail upper bound | Each image-layer bound |
|---:|---:|---:|---:|
| 48 | `0.5850450561177712 Pa` | `0.2946309246985959 Pa` | `0.2127293581590254 Pa` |
| 64 | `1.336763456355083e-5 Pa` | `6.706388809072444e-6 Pa` | `4.274317711556060e-6 Pa` |
| 80 | `2.560823123768434e-10 Pa` | `1.282524282772518e-10 Pa` | `7.207744719959560e-11 Pa` |

These are **preliminary candidate mathematical tail bounds**, not yet independent proof review or a selected accuracy threshold. Directed arithmetic only controls rounding in the bound calculator; it does not bound the binary64 modal sums, ring quadrature, or model discrepancy. No cutoff is selected. The direct-layer ring/modal difference remains unresolved even though this candidate truncation bound is small at N=80.

### Exploratory one-angle formula check

A one-off ignored diagnostic evaluated the derived modal formulas through order 80 at 179° and compared each layer with the recorded order-14 ring-quadrature result. The two deterministic replays are byte-identical. Complex absolute differences are:

| Layer | Difference (Pa) |
|---|---:|
| Direct double layer | `7.1928484241e-7` |
| Direct single layer | `7.8572443543e-7` |
| Image double layer | `3.7423739198e-15` |
| Image single layer | `1.826181888997e-14` |

For this one case, the modal image values agree with the ring outputs to near binary64 precision, while the direct differences remain visible at a scale consistent with the previously observed direct-layer sensitivity. This is one finite cross-method comparison, not an error bound, convergence result or acceptance test. The record uses CPython 3.12.14 at source revision `10fe625c678040ffc124dbcaf45c876847b2b3d4`; the numerical module SHA-256 is `b487f36043d20c1e356fc25ea73e8a7b4487ed97ed4e8390fb96bfad4ef69fd1`. Its reference is the n=14 artifact from source `ca96183ee6782ef29207397f252848ce7fda4572`, SHA-256 `795b8dc3c4deea5a3a302a2dfd6a3d68607450db13ba6588072a9b40c1611c18`. The scratch worktree was dirty only from this documentation continuation; no source code was modified. Diagnostic script SHA-256 `eb9859bc992b7d6c552f4c32cc58e9d4f9abae2fa7886aec29190e742a0cf4d7`; identical replay JSON SHA-256 `87db38ffbbd62ec9ff3840ba1a59decf13f41c9536e4647641aff36e5258e3ae`. An initial scratch attempt omitted `1/(4 pi)` in mirror coefficients, and the next used the image-center angle for direct terms. Both bookkeeping errors were corrected before recording this result; their discarded outputs are described in the local diagnostic record and are not evidence.

## 4. Proposed implementation boundary

The owner authorized the bounded research-only implementation on 2026-10-09. The maintained evaluator is `tools/research/benchmark_bem_exact_sphere_modal_reference.py`; it has no import or call to direct/image ring quadrature routines. The remaining tail-proof and direct-layer uncertainty review does not select a cutoff or authorize a solver core. The ignored scratch formula checker above is only an equation check, not that evaluator. The maintained implementation may use a separately reviewed special-function implementation already present in the repository, but must not share quadrature nodes, ring traversal, or layer accumulation logic with the benchmark under test. It returns separate complex values for:

- direct `K` and direct `V`;
- image `K` and image `V`;
- half-pressure jump;
- reconstructed combined CBIE residual.

It must reject unsupported cutoffs, nonfinite intermediate values, invalid radius ordering, and workspace estimates above the fixed cap. Store no dense BEM matrix. Use stable complex summation and record the sum order; where cancellation is material, record the uncombined modal terms and a cancellation indicator.

## 5. Frozen verification sequence

| Stage | Check | Required comparison |
|---|---|---|
| A | Re-derive conventions and source location from the current Green and CBIE implementations | Written sign/normal table; no numerical result accepted until consistent |
| B | Direct diagonal layer modes `n=0,1` | Existing exact-sphere Maue/CBIE mode tests; separate `K`, `V`, and jump values |
| C | Modal pressure and `q` traces | Direct monopole formula plus mirror monopole closed form; selected angles and exact coordinates |
| D | Image combined identity | Reproduce the existing reflected-monopole identity at 120°, 135°, 175°, 179°; report complex absolute discrepancy |
| E | Separate image `K` and `V` modal projection sums | Compare with the existing ring benchmark at 179° first, then the other angles; compare each term, their difference, and truncation sequence separately |
| F | Full CBIE reconstruction | Compare all five terms and residual against the recorded exact-sphere CBIE result; residual cannot substitute for termwise agreement |
| G | Arithmetic/repeat check | Repeat with an independent arithmetic path or precision and exact deterministic metadata; retain discrepancies and failures |

Candidate modal truncations for planning are `N=8,16,32,48,64,80` for the point-source trace and weighted image-layer sums, reusing levels where the existing mirror-tail proof applies. The order-80 result above is the first comparison point, not a selected final cutoff. These are diagnostic checkpoints, not an acceptance threshold. The image-layer sequence must include at least three nested cutoffs and a documented weighted tail or an explicit `INDETERMINATE` outcome. No last-step difference alone is a tail bound.

Comparisons report each complex layer's absolute difference in Pa, the residual both absolute and normalized by `|p(x)|`, exact modal cutoff, observed last-term and tail status, arithmetic precision, repeated-value checksums, wall time and peak memory. Relative layer errors are supplementary only when a declared numerical floor prevents division near a zero.

## 6. Provenance and resource controls

Every run must record immutable run ID; exact Git revision; dirty-tree status; benchmark-script hash; lock/environment digest; Python and platform versions; exact `a,g,f,c,k`, angle, source coordinates, normal and phasor convention; modal cutoff and summation ordering; arithmetic precision; workspace estimate/cap; wall-time cap; outputs and SHA-256 checksums. Generated records stay under ignored `results/diagnostics/` unless a separate project decision authorizes otherwise.

### Exploratory evaluator-resource screen

The existing ignored one-angle formula checker was run in three fresh processes per inclusive cutoff, storing all modal terms and provenance. Median elapsed time including Python startup was `0.0669 s`, `0.0708 s`, and `0.0757 s` at `N=48`, `64`, and `80`; maximum process RSS was `19,836`, `19,944`, and `20,080 KiB`. This shows the frozen one-angle calculation is inexpensive at these orders in the current workstation environment. It is not a production evaluator guarantee: the checker shares the repository's spherical-Bessel helper, only covers 179°, does not run the full multi-angle protocol, and its RSS is dominated by interpreter/import overhead. The modal formulas themselves keep `O(N)` terms when retained for audit; recurrence-only summation can use `O(1)` working storage, but the plan currently requires term provenance.

The ignored resource record is `results/diagnostics/NUM03-MODAL-FORMULA-CHECK-20261008/resource-summary-repeats.json`, SHA-256 `1dfb0843b21281ac893a3b29dc8c0c2083a53af0e11b9457a2c1af0277ccc114`; source revision `a19035b0c438cf97fe30f2323a217978930543b8`. Three repeats per cutoff are preserved in that directory. These timings inform the plan only and do not replace the later clean-source preflight or runtime/memory measurement for maintained code.

Before execution, run the repository's exact resource preflight for the proposed cutoff and arithmetic. A 0.1 mm gap is the worst frozen geometry for the weighted image-layer series because it minimizes `R(theta)`; the raw kernel ratio is close to one, even though the source modal density is expected to reduce the weighted rate. Do not infer modal runtime from the prior ring-quadrature measurements or from the point-source expansion's `a/L` ratio alone. Stop before execution if the tail method, per-term workspace, memory cap, wall-time cap, or required environment cannot be stated and checked.

## 7. Stop, failure, and interpretation rules

- Preserve all failed derivations, cutoffs, overflow/nonfinite failures, and disagreements with their exact inputs and hashes.
- Do not tune a cutoff or arithmetic precision to minimize the residual.
- A modal cross-check and the existing ring quadrature share the manufactured Green function, physical constants, geometry, and boundary convention. Their agreement tests numerical representation; it does not validate the physical model or an experiment.
- Do not claim convergence until the separate terms and their truncation uncertainty are characterized. Cancellation in the CBIE can make its residual look small while a layer remains sensitive.
- Do not assign an accuracy tolerance based on the observed residual or current discrepancy.
- If the weighted image-layer tail is too slow or cannot be bounded without ambiguity, retain a documented partial outcome: direct layers checked separately, image combined identity checked, separate image layers unresolved. Reopen alternative reference choices rather than silently substituting correlated quadrature paths.
- NUM-03 stays ACTIVE / INDETERMINATE; P4 stays unpassed; this work does not authorize a solver core or establish physical validity.

## 8. Primary sources and repository evidence

1. NIST Digital Library of Mathematical Functions, [§10.60(i), Addition Theorems, Eqs. 10.60.1–10.60.2](https://dlmf.nist.gov/10.60): spherical-Bessel addition formulas and radial convergence condition. The outgoing Helmholtz formula above is obtained by combining these equations with `h_n^(1)=j_n+i y_n`.
2. NIST DLMF, [§14.30, Eqs. 14.30.8–14.30.9](https://dlmf.nist.gov/14.30): spherical-harmonic orthogonality and addition-theorem normalization used for axisymmetric projection.
3. NIST DLMF, [§10.50, Eq. 10.50.1](https://dlmf.nist.gov/10.50): spherical-Bessel Wronskian used to verify jump normalization.
4. NIST DLMF, [§10.53, Eq. 10.53.1](https://dlmf.nist.gov/10.53), [§10.51, Eq. 10.51.2](https://dlmf.nist.gov/10.51), [§10.49, Eq. 10.49.6](https://dlmf.nist.gov/10.49), and [§18.14, Eq. 18.14.1](https://dlmf.nist.gov/18.14): power series, derivative recurrence, exact finite Hankel formula and the `|P_n(x)|<=1` bound on `[-1,1]` used by the candidate absolute tail majorant.
5. Current implementation conventions: [`_bem_green.py`](../../src/aura/fields/_bem_green.py), [`benchmark_bem_exact_sphere_combined_cbie.py`](../../tools/research/benchmark_bem_exact_sphere_combined_cbie.py), and exact mode/identity regressions in [`test_z_bem_halfspace_integral_identity.py`](../../tests/test_z_bem_halfspace_integral_identity.py) and [`test_z_bem_singular.py`](../../tests/test_z_bem_singular.py). These are repository evidence and regression controls, not replacements for the primary mathematical sources.
6. Current finite-sensitivity result: [14/16 subdivision review](../reviews/NUM03-BEM-exact-sphere-cbie-179deg-subdivision-14-16.md).

The DLMF equations support the single-center outgoing expansion, both source-sphere projections, and the absolute-majorant route. The majorants have an outward-rounded local replay. The maintained evaluator now has a four-angle, three-cutoff record and a separate 100-digit Decimal check at 179°/N=80; see the [review report](../reviews/NUM03-modal-reference.md). The owner authorized implementation and numerical checking only. No cutoff is selected, the direct-layer tail is uncertified, NUM-03 remains INDETERMINATE, and no solver core is authorized.
