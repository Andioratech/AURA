# P4 — Water Qualification Followed by Air Field Verification

**NUM-03 near-neighbor image-ring qualification — 2026-10-07:** Harness v1.4 at clean revision `f86e181b51352646cb5d2f8fa95478f3c61bd38f` passed exact remote Quality run `37661190476` and completed under ENV-1.0 / CPython 3.12.14. It evaluated 548 pointwise image mixed-normal ring integrals for the fixed `a=25 mm`, `0.1 mm` gap, 25.23 kHz, 346 m/s case: three exploratory, 112 diagonal, three selected distinct and 430 directed first/second-neighbor GL4 pairs from N=16/32/64 meshes. The midpoint reference refinement (65,536→131,072) changed by at most `3.69e-16` relatively; midpoint 131,072 vs Gauss 128×8 differed by at most `1.65e-15`; Gauss 64×8 vs 128×8 by `2.49e-14`. For the N=64 mesh's worst adjacent case, candidate midpoint error was `6.01e-6` at azimuth N=64 and `3.73e-13` at N=128, while each fixed gap-scaled split had larger error at that case. The split remains non-uniform across cases. All 16,440 candidate repeat checksums are present; process peak RSS was `793812992` bytes. Artifact SHA-256 `6e0ca4bd7746395bafd3ba7c8c922dcc6dbc602062652b93ab42f64ea7b1fc33`. These are finite comparisons sharing kernel and geometry, not an error bound, full operator result, field acceptance or physical validation. No matrix/solver execution; preflight remains INDETERMINATE and unauthorized. Next prepare the design for a matrix-free exact-sphere image-action check against the analytic reflected-monopole reference; explain the operator/core milestone before implementation.

**NUM-03 diagonal image-ring sweep — 2026-10-07:** Clean ENV-1.0 harness v1.3 on revision `be728aad1e08a197bd058c1cace0e77d2cbceca3` evaluated 118 pointwise image mixed-normal ring integrals at `a=25 mm`, gap `0.1 mm`, `f=25,230 Hz`, `c=346 m/s`: all 112 diagonal GL4 node pairs for mesh sizes N=16/32/64, three selected distinct pairs and three exploratory pairs. It compared periodic midpoint/gap-scaled candidates against midpoint references at 65,536/131,072 samples and composite Gauss-Legendre at 16/32/64/128 panels of order 8. Across the 118 cases, midpoint 131,072 vs Gauss 128×8 differed by at most `1.57e-15` relatively; Gauss 64×8 to 128×8 differed by at most `2.49e-14`. For all diagonal pairs, midpoint N=256 differed from Gauss 128×8 by at most `3.53e-15` (mesh N=32); per-mesh maxima for N=16/32/64 were `1.30e-15`, `3.53e-15`, `1.31e-15`. At N=64, worst midpoint discrepancy was `6.93e-4`, versus `1.34e-5` for the best gap-scaled rule per pair; at N=128, midpoint's worst was `1.12e-8`, versus `3.35e-6` for the best split. The split can help coarse cases but is not uniformly superior. All 3,540 candidate repeat checksums are present; process peak RSS was `631181312` bytes. Local artifact `results/diagnostics/NUM03-BEM-NEAR-PLANE-IMAGE-RING-DIAGONAL-20261007-01/qualification.json`, SHA-256 `39eaed78aba5930b9299de74c2ccab36c22d59097cc34f88ff131da8ba3d711b`. This is finite quadrature sensitivity for the same pointwise kernel and geometry, not an error bound, full operator, matrix, solver result, field acceptance or physical validation. No matrix was allocated; preflight remains INDETERMINATE and unauthorized. Next scan the nearest off-diagonal GL4 ring pairs and their immediate neighbors across N=16/32/64, matrix-free. Hasegawa remains selected P4 backend; BEM remains a candidate numerical reference; NUM-03 ACTIVE/INDETERMINATE and plan DRAFT.


**NUM-03 cross-quadrature image-ring result — 2026-10-07:** Harness v1.2 at clean revision `8a4c71a09ded8522a22dd73f8ad1d638a8832adc` / ENV-1.0 compared the existing periodic midpoint and gap-scaled candidates with composite Gauss-Legendre pointwise integration for three exploratory pairs and the selected self/distinct pairs from GL4 meshes N=16/32/64. At `a=25 mm`, gap `0.1 mm`, 25.23 kHz, `c=346 m/s`, the 131,072-point midpoint result and 128-panel × 8-point Gauss-Legendre result differed by at most `7.85e-16` relatively across nine pairs; the 64×8 to 128×8 Gauss refinements differed by at most `2.45e-14`. For the three selected mesh self-pairs, midpoint N=256 was within `1.12e-15` relative of the finest Gauss result, while the best gap-scaled rule at N=256 ranged from `4.41e-8` to `8.14e-8`. Gap-scaled splitting helps at some coarse counts but is not uniformly better and is less accurate for these finer self-pair counts. Local artifact `results/diagnostics/NUM03-BEM-NEAR-PLANE-IMAGE-RING-CROSS-QUADRATURE-20261007-01/qualification.json`, SHA-256 `4619ca6021264ab9460529d270ca2ff1cc0597ca7f88cabf436a3dd8c139424c`; it records repeat checksums, exact geometry, script/lock identities, clean source and peak RSS `631181312` bytes. This is cross-quadrature sensitivity for a shared pointwise kernel and geometry, not an error bound, full surface operator, matrix, solver result or physical validation. No matrix was allocated; preflight remains INDETERMINATE and execution unauthorized. The next harness extension stated in this earlier checkpoint is completed in the diagonal-sweep record above. Hasegawa remains selected P4 backend; BEM is only a candidate reference route; NUM-03 remains ACTIVE / INDETERMINATE and its plan DRAFT.


**Latest BEM image quadrature — 2026-10-07:** Commit `b686ae5` passed remote Quality run `37633616948`; its clean ENV-1.0 run compared midpoint and gap-scaled image mixed-normal ring quadratures for three selected pairs at `a=25 mm`, gap `0.1 mm`, 25.23 kHz. References at 65,536 and 131,072 full-period midpoint samples differed by at most `4.09e-18` relatively. No rule was uniformly best: for the 175°/175.1° pair, gap-scaled N=16/L=6 improved on midpoint, while at N=128/L=6 it was worse; for 179°/179.1° at N=64, midpoint was much closer than gap-scaled L=6. This is finite pairwise quadrature sensitivity, not a bound or a surface-integrated field. Next check pairs selected from the candidate GL4 meshes. No matrix or field qualification; preflight remains INDETERMINATE.

**Latest BEM calibration — 2026-10-07:** The clean ENV-1.0 direct-sphere self-panel calibration at N=16/32/64 completed in max 0.516710/1.346565/2.567704 s per repeat with stable repeat checksums. It covers `a=17 mm`, gap `17 mm`, `ka=2.3`, GL4, 256 azimuth samples and modes 0/1. Commit `2113444` passed remote Quality run `37625384722`. The measured API includes a smooth image output that the harness discards; the tested case is not near-plane. No matrix was allocated. Preflight remains INDETERMINATE and unauthorized. Next qualify the image contribution at the frozen minimum clearance (`a=25 mm`, gap `0.1 mm`) with bounded refinements and an independent numerical route.

**Self-panel calibration harness preparation — 2026-10-07 (superseded):** Prepared the clean-source/ENV-1.0 timing harness for all direct-sphere singular self-panels on GL4 `N=16/32/64`, with modes 0/1, three repeats, checksums and a per-repeat cap. The following completed-calibration entry records the result. The timed ring API also computes a smooth image output that this direct-sphere benchmark discards. No matrix or solve was run.

**Direct-sphere singular action — 2026-10-07:** Implemented one bounded direct Maue panel integral with regularized ring residual and Cauchy/log product-integration corrections. Exact free-space sphere controls pass for zonal modes 0/1 at three angles and meridian orders 16/32/64; invalid poles, panel joins and order are rejected. This component does not include the plane image, jump term, panel assembly, matrix, solve or field qualification. Its candidate GL4 self-panel calibration is complete as recorded above. NUM-03 remains ACTIVE/INDETERMINATE and P4 is unpassed.

**BEM foundation update — 2026-10-07:** Exact sphere meridian quadrature is available and unit-checked for surface moments and symmetry; corrected full local Quality passes 1,803 tests after an initial run exposed and fixed an eager-import regression. Candidate basis/refinement and resource preflight remain open; no matrix or coupled field solve has run. This supports the DEC-007 fallback investigation, not a change to the selected Hasegawa P4 backend or a P4 pass.

**Candidate BEM preflight update — 2026-10-07:** A direct free-space exact-sphere screening discretization is documented as a candidate Nyström pressure trace with 4/8/16 composite GL4 panels (`N=16/32/64`). Its dimension-based dense-memory allowance peaks at 2,400,256 bytes before any matrix is allocated; a 16 MiB RAM cap is provisional pending implementation and available-memory checks. Runtime has not been calibrated. The near-plane image term is not covered. Keep solver plan DRAFT and P4/NUM-03 INDETERMINATE; next implement pre-allocation estimation and a bounded matrix-free runtime calibration.

**BEM preflight implementation — 2026-10-07:** `estimate_bem_dense_workspace` performs arithmetic-only dimension admission and rejects before any operator/geometry allocation when declared or available RAM is below its estimate. A fitting request remains INDETERMINATE because runtime calibration is absent. Nineteen focused mesh/preflight tests and full local Quality (1,813 tests in 1,085.79 s, plus install, ENV-1.0, Ruff, required-document and diff checks) pass. The next step is a clean-revision, ENV-1.0 matrix-free kernel calibration; no matrix or P4 pass follows.

**BEM calibration tooling — 2026-10-07:** Prepared a streaming off-diagonal direct-ring timing harness with a clean-source/ENV-1.0 gate, repeated checksums and a per-repeat stop. Ruff and CLI-help smoke checks pass; the harness has not been run and yields no resource calibration yet. It omits singular and hypersingular/image terms and the solve. Publish, verify remotely, then run this exact workload; retain `INDETERMINATE` for matrix allocation until full-operator runtime and memory are covered.

**BEM off-diagonal kernel calibration — 2026-10-07:** Exact clean commit `9204c98eaddacf532b4c87a8a6b64fb6b70164b1` passed remote Quality run `37562919561`; its ENV-1.0 timing artifact (`fda6c8a0f466340e50b090de2b838809c7770098fdec9780b9efb9aa4cec8ba4`) records three-repeat median/max times of 0.174820/0.197666 s (N=16), 0.797175/0.878167 s (N=32), and 2.975475/3.258054 s (N=64). This covers only off-diagonal direct scalar/first-gradient ring kernels. Preflight remains INDETERMINATE; no matrix or P4 pass follows. Source inspection confirms the separated-ring Maue/image routine rejects coincident pairs. Next calibrate its bounded off-diagonal workload, without singular product integration or assembly.

**BEM singular-panel primitive microcalibration — 2026-10-07:** Commit `f052002cbd9b911dd1c6d8632fd7f95efa32a4c9` passed remote Quality run `37575291950`. Isolated Cauchy/log product-integration primitives for N=16/32/64 measured median/max 0.001881/0.002543 s, 0.007229/0.007314 s, and 0.052164/0.052682 s. These primitives have no production BEM callers and the measurement excludes the regularized ring residual, so it is not a complete diagonal action. No matrix allocated; preflight remains INDETERMINATE. Next define and verify a complete matrix-free direct-sphere diagonal action before considering assembly.

**BEM separated-ring Maue calibration — 2026-10-07:** v1.1 commit `fe723931b8a6dab6e9f626a223a8491ffc98dcf2` passed exact remote Quality run `37570071393`. Combined off-diagonal direct scalar/gradient and separated-ring Maue/image kernels gave median/max wall times 0.674377/0.711091 s (N=16), 2.863510/2.957363 s (N=32), and 10.543530/10.638831 s (N=64). The diagonal product integral, near-plane image, assembly and solve remain excluded. Preflight is INDETERMINATE; no P4 or physical claim follows. Next review the singular-panel primitives and estimate isolated diagonal product-integration work without matrix allocation.


**NUM-03 mirror-mode remainder bound — 2026-10-07:** For a centered monopole and the fixed sphere case (`a=25 mm`, `gap=0.1 mm`, `f=25,230 Hz`, `c=346 m/s`), the exact image Green expansion tail after order `N` is bounded by `B_N=[1/(12D)] exp(z+x²/(2(2N+5))) q^(N+1)/(1-q)`, with `D=2(a+gap)`, `q=a/D`, `x=k_upper a`, `z=k_upper D`, and `k_upper=(44/7)f/c`. The derivation uses DLMF §§10.53.1, 10.49(i), 10.60(i), and the real-angle Legendre bound. Rational inputs and outward-rounded Decimal evaluation give `B_48=9.09943933485362e-5 m^-1`, `B_64=1.11397254106508e-9 m^-1`, and `B_80=1.44903668349673e-14 m^-1`. At order 80, the independently evaluated binary64 series differs from the exact image Green value by `2.91e-15 m^-1` at 120° and `2.93e-15 m^-1` at 135°. The analytic bound is uniform over real surface angles for this configuration and every nonnegative cutoff; it does not bound floating-point evaluation, quadrature, a matrix solve, other parameter values, or physical behavior. Focused test: 2 passed. Local-only record `NUM03-BEM-MIRROR-TAIL-BOUND-20261007-01`, SHA-256 `cfb893fddc06e1f084fa0d26c65e98e50eeb25a52499c64be17cc5505cbadef2`. No solver matrix or core was started.

## NUM-03 off-equator direct CBIE panel comparison — 2026-10-06

For the direct free-space sphere control (`a=17 mm`, `ka=2.3`, sphere-center height `2a`), the singular-panel single- and double-layer operators and the combined CBIE were checked for zonal outgoing modes `n=0,1` at `theta=120°` and `135°`. The reference eigenvalues are Kreuzer (2024), Eqs. (1), (4)–(5), [DOI 10.1016/j.enganabound.2024.105883](https://doi.org/10.1016/j.enganabound.2024.105883), with printed kernel `G=exp(i k r)/(4 pi r)`. Mapping the paper's sphere-outward normal to AURA's normal into the sphere gives the explicit identity `0.5 phi + K_AURA(phi) - V(d phi/dn_AURA)=0`; the half-jump is kept separate from the principal-value layer. Meridian Gauss orders 16/32/64 and 1,024 ring azimuth samples use explicit logarithmic subtraction/restoration. All four cases show decreasing CBIE residuals across refinement; order-64 residuals normalized by the boundary-mode amplitude are `2.02e-9` and `2.59e-8` at 120° (`n=0,1`), and `1.14e-8` and `1.35e-8` at 135° (`n=0,1`). The individual layer eigenvalue comparisons pass, and the singular test file passes 20/20. An initial combined harness double-applied the angular `P1` factor to the normal derivative; the failed screen is retained locally (SHA-256 `1196458d1b57efc12f6b01c75bf98f78e7f0158657a87e8fa3b91b52c5d0fa8c`) and no threshold was relaxed. Local component record SHA-256 `a9a3eb2e508d5c17453cda2637f0633be5501787f13ad10656044f073cdf4602`. The full local Quality workflow passes all 1,792 tests, including locked installation, editable installation, `pip check`, ENV-1.0, Ruff, required-document checks and `git diff --check`. This is a finite-grid direct free-space control only; it does not validate image terms, a complete half-space BIE, a matrix, general geometry or AURA's physical field.

**Independent off-equator image CBIE check — 2026-10-06:** On a `25 mm` sphere with a `0.1 mm` plane gap, a unit monopole at the sphere center and field angles `120°`/`135°`, the image-layer contribution `K_image(phi) - V_image(dphi/dn_AURA)` was evaluated by ring reduction and independent pointwise full-surface quadrature. For these boundary traces from the Neumann half-space Green function, both routes match the exact image-source value `-G(x, y_image)`; the largest absolute route-to-reference discrepancy is `6.3e-15`, and the largest layer-component disagreement between routes is `5.7e-14`. The compared grid uses meridian Gauss order 64, ring azimuth counts 1,024/2,048 and full-surface azimuth count 4,096; the established `2e-8` relative / `1e-5` absolute screen remains unchanged. Local record SHA-256 `cb798d870406424f1e07629d100bea6ee617b9e14e9875b81bee920fe6630cd5`. This verifies the smooth image CBIE component only; it is not a complete half-space solve, a general quadrature error bound or physical validation.

**Independent mirror-mode CBIE cancellation check — 2026-10-06:** The regular expansion of the reflected monopole was tested at `a=25 mm`, `gap=0.1 mm`, `f=25,230 Hz`, `c=346 m/s`, and `theta=120°`/`135°`. Combining [DLMF §10.60(i), Eqs. 10.60.1–2](https://dlmf.nist.gov/10.60) gives `G_image = i k/(4 pi) sum_n (2n+1) j_n(ka) h_n^(1)(kD) (-1)^n P_n(cos(theta))`, with `D=2(a+gap)` and `a<D`. Kreuzer's exact sphere layer eigenvalues (2024, Eqs. 4–5, [DOI 10.1016/j.enganabound.2024.105883](https://doi.org/10.1016/j.enganabound.2024.105883)) show each regular mode's direct CBIE response equals its boundary trace; the independently checked image contribution is `-G_image`. At cutoff `N=48`, the modal pressure differs from the exact image Green value by `2.48e-15` (`120°`) and `5.09e-15` (`135°`); each mode's direct-response/trace discrepancy is at most `2.84e-16`, and the direct-plus-image CBIE cancellation residuals are `2.34e-15` and `5.06e-15`. At `N=32`, image-pressure differences are `8.38e-10` and `7.48e-10`; these finite truncation comparisons are not a general remainder bound. Local record SHA-256 `b20886ce69b76977242cf5e1b035247ab46abd555d5b772a4fd28d6615d63179`. This verifies an analytic modal decomposition for this geometry and frequency only; it is not a discretized half-space solve or physical validation.

## NUM-03 off-equator direct hypersingular panel comparison — 2026-10-06

For the direct full-sphere control, the singular-panel Maue integral was compared with the exact hypersingular eigenvalue for zonal modes `n=0` and `n=1` at `theta=1.1`, `120°` and `135°`. All six mode-angle cases pass with meridian Gauss orders 16/32/64 and 1,024 azimuth samples after explicit Cauchy and logarithmic subtraction/restoration. The reference is Kreuzer (2024), Eq. (6), [DOI 10.1016/j.enganabound.2024.105883](https://doi.org/10.1016/j.enganabound.2024.105883), which gives `lambda_n(E)=i k^3 h_n^(1)'(k) j_n'(k)` on the unit sphere for `G=exp(i k r)/(4 pi r)` and `E=d^2G/(dn_x dn_y)`; the `a^2` radius factor follows dimensional scaling and is the form tested here. The paper states a different harmonic time convention elsewhere, so only the displayed kernel/operator convention is used, with sign checked against AURA's kernel. This is a direct free-space axisymmetric test only; it does not validate the plane image, full half-space BIE, non-axisymmetric modes, matrix or AURA field. Six focused cases pass; full local Quality passes all 1,788 tests in 918.53 s, including locked installation, editable installation, `pip check`, ENV-1.0, Ruff, required-document checks and `git diff --check`. Local record SHA-256 `5d0598e085021f27fcf9600fdcf9aaefbf830b7fd3565d602f0da024d5d89138`.

## NUM-03 off-equator direct singular-coefficient audit — 2026-10-06

At `theta=120°` and `135°`, the direct axisymmetric Maue ring term was probed at meridional offsets `1e-3`, `1e-4` and `1e-5 rad` for a 25-mm sphere, 0.1-mm gap, 25,230-Hz source and 8,192 azimuth samples. The normalized leading Cauchy coefficient approaches unity at the smallest offset (`1.00146+7.46e-5i` at 120°; `0.99854+0.00200i` at 135°). The logarithmic coefficient was estimated by differencing the Cauchy-subtracted remainder across the `1e-4`/`1e-5` offsets, which removes the finite remainder constant; it differs from the local `a k^2 p/(2 pi)` coefficient by 2.07% and 2.01%, respectively. The two focused regressions pass. This checks local finite-offset coefficients only; it does not validate the full singular-panel remainder, continuous BIE, solver or AURA field. Local record SHA-256 `e8a90aa93924b58de50b4de163bb6978c30b60e6762fc4a291436f19faef1a62`.

## NUM-03 independent full-surface image comparison — 2026-10-06

At `theta=120°` and `135°`, the exact-center-source sphere image contributions were compared in two routes: meridian-ring integration (Gauss-Legendre order 64, 2,048 image azimuth samples) and direct full-surface pointwise integration (the same meridian nodes and 4,096 azimuth samples). The independent route evaluates image Green, source-normal and field-normal derivatives pointwise and computes the mixed-normal term from a separately written Hessian projection. At each angle, image double-layer, single-layer, hypersingular and adjoint components, plus their Burton–Miller combination, pass the established `2e-8` relative / `1e-5` absolute regression screen. This is finite-grid verification of smooth image contributions only; it does not validate the direct singular terms, complete BIE or AURA field. An initial harness that applied pressure twice to the image hypersingular term was rejected and preserved locally; corrected record SHA-256 `b9813931a38109fa55c4583b39db5621f59db2f5ad2906483d4f3f58dafa1078` (failed harness SHA-256 `b955cae7ab2f0de05d3de898f77b61696e437600b325b949f823448ecb89158a`). Next independently audit the direct Cauchy/logarithmic singular remainders at both points before any matrix allocation.

## NUM-03 off-equator coupled-identity quadrature refinement — 2026-10-06

At meridian order 256, the matched off-equator exact-source half-space identity was refined over direct azimuth counts 512/1,024/2,048/4,096/8,192 (image counts twice as large), with direct and image magnitudes retained separately. At 8,192, normalized `(CBIE, HBIE, Burton–Miller)` residuals are `(1.07e-9, 7.91e-7, 9.69e-7)` at `theta=120°` and `(8.92e-10, 1.76e-6, 9.99e-7)` at `theta=135°`. Holding azimuth at 4,096 and raising meridian order from 256 to 512 reduces the 120° HBIE and combined residuals from `7.87e-7`/`9.58e-7` to `1.92e-7`/`2.28e-7`; at 135° they fall from `1.76e-6`/`1.00e-6` to `4.40e-7`/`2.52e-7`. The CBIE direct and image magnitudes are individually about 0.70 at 120° and 0.43 at 135°, while their total residuals are near `1e-9`, exposing strong cancellation. A strict monotonic rule is not applied to every total across every grid. All are finite-grid identity checks, not an error bound, solver qualification or physical result. Full component sequences are preserved locally (record SHA-256 `054de3d09d56fb43c5fbe1cb4d0e6d4fd71ea6d292db1722283d5eb97563ae78`). Next compare the matched off-equator identities with a separate full-surface integration route before any matrix work.

## NUM-03 off-equator image mixed-normal comparison — 2026-10-06

The off-equator half-space image mixed-normal surface contribution was compared with a separate full-surface pointwise angular integration at `theta=120°` and `135°`, for densities `1` and `cos(theta)` across gaps 0.1, 10, 20 and 29.9 mm. All 16 parameter cases pass. At the 0.1-mm gap, fixed meridian order 64 and ring azimuth counts 256/512/1,024 change the reduced integral by less than `1e-12` absolute; a separate 2,048-point full-surface angular route agrees under the existing `2e-8` relative / `1e-5` absolute regression comparison. This is finite-grid component evidence, not an error bound or field validation. An initial strict-monotonic screen failed at differences around `1e-14`, consistent with binary64 summation variation; it is preserved locally (record SHA-256 `7e6e41df7d485ce96906c492d5d4bde259812c9b67fe77486043c424fd3e8050`). Next refine matched CBIE/HBIE/Burton–Miller azimuth resolution at both off-equator angles with direct and image terms kept separate; do not allocate a matrix.

## NUM-03 off-equator CBIE/HBIE combination — 2026-10-06

At `theta=120°` and `135°`, the exact-source half-space sphere control now computes matched CBIE, HBIE and `R_CBIE+(i/k)R_HBIE` residuals using direct/image azimuth counts 1,024/2,048 and meridian orders 128/256/512. Finest normalized `(CBIE, HBIE, combined)` residuals are `(4.93785e-7, 2.94369e-7, 8.19984e-7)` at 120° and `(1.32259e-7, 6.35112e-7, 4.90509e-7)` at 135°. The HBIE sequences decrease; CBIE varies slightly nonmonotonically and the 120° combined residual rises at the finest order. This is finite-grid identity regression evidence only. An initial strict-monotonic screen failure and complete values are preserved locally (record SHA-256 `e637c55647a2c1d37b43f99162c2a2857785fcd4f2df5e5c1504babe9673188b`). Next independently compare the off-equator image contribution at both points and refine its azimuth integral; no matrix allocation or solver-core construction. The direct singular terms use the existing Cauchy/logarithmic product integration; image terms remain separately accumulated. The earlier strict-monotonic screen was not an approved scientific criterion and is recorded as a failed numerical screen, not discarded.

## NUM-03 half-space Burton–Miller sphere checkpoint — 2026-10-06

The exact-source half-space sphere control checks the equatorial HBIE and Burton–Miller identities. At direct/image azimuth counts 256/512, 512/1,024 and 1,024/2,048, fixed meridian order 64 gives HBIE residuals `4.17641e-5`, `5.21520e-6` and `6.51563e-7`, and combined residuals `7.81027e-5`, `9.75229e-6` and `1.21864e-6`. Meridian orders 32/64/128 at azimuth 1,024/2,048 give HBIE residuals `6.47423e-7`, `6.51563e-7`, `6.51681e-7`, and combined residuals `9.50697e-7`, `1.21864e-6`, `1.21872e-6`. Primary Eq. (14) gives the residual combination `R_CBIE+(i/k)R_HBIE`. The earlier `1e-6` screen was unapproved; regression cutoffs are not scientific tolerances. This one-point manufactured-field check is finite-grid evidence only. The first off-equator prototype double-counted variable Cauchy density after subtracting only the collocation value; its `0.374` residual is retained as a failed implementation. The corrected `theta=135°` control restores only the constant density and gives HBIE residuals `7.12466e-6`, `1.93304e-6` and `6.35112e-7` at meridian orders 128/256/512. This remains one finite-grid regression, not operator or field qualification. Next test another collocation angle and independently check the image term; do not start matrix work. NUM-03 remains ACTIVE / INDETERMINATE, Hasegawa remains selected and the public field matrix paused. See the [foundation note](../../research/NUM-03-bem-kernel-foundation.md), [task](../../work-items/NUM-03.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 half-space CBIE control — 2026-10-06

The direct-plus-image conventional boundary integral identity passes a one-point exact-source sphere control at `a=25 mm`, `H=0.1 mm`, and `theta=175°`. With fixed azimuth counts 512/1,024 and meridian Gauss orders 64/128/256, normalized residuals are `3.58965e-4`, `7.02808e-6`, and `1.77906e-6`. An earlier failure from inconsistent product-integration measures is retained in the local diagnostic record. This verifies one finite-grid CBIE case only; it does not qualify a general half-space operator, matrix, solver, piston coupling or AURA field. The subsequent HBIE and combined-equation checkpoint is recorded above.

## NUM-03 quadrature design update — 2026-10-06

The direct diagonal and the positive-gap image require separate numerical treatment. Static direct-ring scalar, cosine moment, first-gradient and mixed-normal integrals now have elliptic/AGM controls; the static direct Maue ring contribution is integrated analytically and only its dynamic residual is midpoint-integrated. The then-current 84 focused BEM tests passed, including an independent near-diagonal full-kernel comparison, exact degree-0/1 sphere modes for interior and polar collocation, and continuous piecewise-linear panel joins. Logarithmic endpoint tests match exact primitives within `2e-14`. The complete-sphere image-only contribution passes 32 direct-versus-axisymmetric comparisons over four clearances, four field angles and two smooth densities. The `0.1 mm`, `179°` case required higher meridian order after the first pair failed; the failure is preserved and the refinement criterion stayed fixed. These bounded checks do not bound error or qualify arbitrary panel geometry. A one-sided Cauchy endpoint diverges for nonzero density and stays rejected; general curved-panel endpoint behavior is open. The image-only gap-scaled split-midpoint alternative remains experimental; its four-gap/angle sweep shows selected minimum-gap gains but no general advantage or error bound. The combined direct-plus-image equation has since been checked; the current next step is to isolate azimuth-quadrature sensitivity at fixed meridian order. Hasegawa remains selected; NUM-03 is ACTIVE / INDETERMINATE and the public matrix remains paused. See the [foundation note](../../research/NUM-03-bem-kernel-foundation.md).

The diagonal asymptotic probe now isolates the Maue tangential term: `Δs * direct_ring` approaches `1/(2π r_f)`, or `1/(2π Δs)` after including the surface Jacobian. The nearest tested offset differs from the local coefficient by about 1.3%; this is not a panel quadrature result. Next implement a principal-value subtraction panel and verify its singular and regular pieces against exact sphere modes.

The static scalar ring has the separate weak-log asymptotic `r_s I_L≈(1/(2π))ln(8r_f/|Δs|)`, checked to about 0.11% at the closest sphere offset. The proposed analytic panel primitives are documented in the foundation note; collocation endpoints and curvature residuals remain unresolved.

The Cauchy/logarithmic panel helpers are implemented and verified against independent polynomial antiderivatives. Full-meridian sphere calculations for degrees 0 and 1 match exact hypersingular eigenvalues within `2e-4` relative for interior collocation and `3e-13` at the pole. A continuous piecewise-linear join matches the Cauchy antiderivative within `2e-14`; the logarithmic join is within `1.3e-10` absolute at order 256. Logarithmic outer endpoints for constant-plus-linear densities match exact primitives within `2e-14`. These checks cover only bounded direct free-space cases; they do not establish general curved-panel convergence, image terms, a mesh or the complete half-space equation. The next bounded task is independent image-operator qualification.

## NUM-03 fallback research update — 2026-10-05

The owner-authorized DEC-007 BEM reference fallback has a tested mixed-normal half-space kernel and separated zero-mode Burton–Miller ring contributions (direct Maue regularization; image mixed-normal derivative). Twenty-six focused tests pass, including free-space Maue identity controls and sphere-mode jump/coupling checks. The half-space image identity, image near-singular quadrature, mesh, solve, and field comparison remain open. Next define the direct-diagonal and image near-singular quadrature before any matrix; preflight the exact case before allocation. Hasegawa remains the selected P4 backend, NUM-03 remains ACTIVE / INDETERMINATE, and the public field matrix remains paused. Details: [kernel foundation](../../research/NUM-03-bem-kernel-foundation.md), [task](../../work-items/NUM-03.md), [review](../../reviews/NUM-03-coupled-kernel-review.md).

**Maps to:** P4.1–P4.7; D04/D05/D06/D08

## Entry condition

P3 PASS. LIT-02 supplies a bounded reference geometry or an explicitly exploratory verification domain. Complete solver-specific preflight before every run.

## Domain sequence

P4 first reconciles the reported prior water numerical comparisons with immutable run and reference artifacts. This is a software/numerical-workflow qualification, not formal validation of the SRC-W03 measurements. The current repository confirms bounded P3 analytical verification, exact RUN-02 replay, and reproducible extraction of figure-derived water profiles; it does not yet document a water-specific field-solver comparison against raw measured arrays. If the existing artifacts do not meet the frozen water qualification criteria, close the gap with the smallest independently checkable water numerical case before using the shared numerical workflow in air.

After the water qualification is recorded, P4 verifies the air field for the DEC-002 source/sphere case using the method selected in NUM-01. A PASS of the air field gate routes initial P5 onward through air. It does not validate the air force model or the published force measurements, whose uncertainty remains incomplete. No result transfers between media.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## NUM-W01 — Reconcile the existing water numerical qualification

**Initial state:** READY for evidence audit. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** ANA-07, RUN-02, LIT-02

**Steps**

1. Inventory owner-reported water calculations and match each to immutable run IDs, exact input/reference data, source, metrics, comparison method and checksums.
2. Separate generic analytical-software verification, data-extraction reproducibility, water-specific numerical verification and measurement/model validation.
3. Assess whether existing water artifacts meet a predeclared numerical comparison criterion. Do not use the SRC-W03 figure-derived profiles as raw data or invent measurement uncertainty.
4. Record PASS, FAIL or INDETERMINATE for the precise workflow capability and list any smallest missing comparison needed before the air leg.

**Required artifacts:** Water numerical qualification audit; artifact-to-claim map; any missing-evidence task proposal.

**Acceptance / decision:** Every accepted prior result maps to a reproducible artifact and an independent reference. A task record may be DONE while the physical water comparison remains INDETERMINATE.

**If unsuccessful:** D-01/F-02/F-09; preserve the gap and define only the smallest bounded water numerical comparison needed.

## NUM-W02 — Close a bounded water numerical gap if required

**Initial state:** CONDITIONAL — activate only if NUM-W01 finds the numerical-workflow criterion unsupported. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-W01; simulation-core explanation checkpoint; selected independent water reference and frozen observable.

**Steps**

1. Select a water field case with fully specified medium, geometry, boundary conditions and an analytical or independently computed reference; do not assume SRC-W03's coupled particle-velocity plots are a field-solver oracle.
2. Freeze the observable, numerical tolerance rationale, precision, resource caps and run protocol before execution.
3. Use the shared validated scenario/run/comparison workflow and preserve all attempts.
4. Compare with the independent reference and record convergence and limits; keep measurement/model validation separate.

**Required artifacts:** Water qualification benchmark specification, reproducible run bundle, comparison and bounded review.

**Acceptance / decision:** The numerical workflow reproduces the selected water reference within the predeclared numerical budget. This is not a pass for the SRC-W03 measurement comparison or air physics.

**If unsuccessful:** F-03/F-04/F-09; preserve the failure and hold transition to the air leg until diagnosed.

## NUM-01 — Choose one backend that answers the selected air question

**Current state:** NUM-01 DONE as a method/contract task; NUM-02 ACTIVE. After NUM-W01 (and NUM-W02 if needed), use the DEC-002 sphere/transducer case selected under [DEC-005](../../decisions/DEC-005-air-validation-route.md). NUM-01 records Hasegawa et al.'s centered baffled-piston/rigid-sphere spherical-harmonic series and its FIELD-1.0 interface in the [solver contract](../../research/air-field-solver-contract.md), subject to NUM-02 stability/resource/convergence preflight. P4 imposes a stationary sound-hard sphere boundary at every order; derive the special `n=1` coefficient from zero normal velocity and do not reuse the source's separate translating-sphere coefficient. P4 verifies field calculations only: no measured air pressure/velocity map exists, the later force comparison remains uncertainty-limited, and acceleration/gravity equivalence remain outside this gate. Prior-art examples do not establish convergence at AURA's source/body parameters. NUM-02 implements only conservative resource estimation and pre-allocation rejection; field arrays and the numerical solver remain gated on its completion. See [NUM-01](../../work-items/NUM-01.md) and [method comparison](../../research/NUM-01-method-comparison.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-W01; NUM-W02 if activated; ANA-07; LIT-02

**Steps**

1. Reproduce the selected primary-source series equations and explicitly map its phasor convention to FIELD-1.0; keep the stationary-sphere and translating-sphere coefficient branches separate.
2. Define source normalization, geometry, air property source, centered sphere boundary, output observables, supported gap range, arithmetic and all missing physics.
3. Predeclare independent piston-only Rayleigh, P3 plane-wave, exact plane-wave/sphere and harmonic-order checks. Do not claim measured-field validation when the benchmark supplies no field maps.

**Required artifacts:** Backend decision; `fields/numerical.py` interface specification; frozen solver-domain record.

**Acceptance / decision:** The method has a clear discriminating reference, implementable boundary conditions and bounded cost.

**If unsuccessful:** D-04/F-03; justify a changed formulation or new restricted experiment.

## NUM-02 — Implement resource preflight before allocation

**Initial state:** DONE — estimator software delivered. NUM-03 has a measured runtime profile for one exact bounded workload; it does not generalize to larger point counts, other gaps or Bessel arguments. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-01

**Steps**

1. Estimate declared gap/point/order dimensions, temporary order vectors, one streamed observation chunk, runtime calibration, and output size for the selected harmonic-series implementation.
2. Require explicit memory/disk/wall-time caps and safety headroom; record how estimates are obtained.
3. Implement rejection before allocating solver arrays and test deliberate over-budget scenarios.

**Required artifacts:** `preflight.py`; CLI preflight; resource fixtures and budget rejection checks; [NUM-02 review](../../reviews/NUM-02-resource-preflight.md).

**Acceptance / decision:** Oversized cases fail before solver allocation with named estimates and alternatives; no machine-specific assumption changes the physics. An estimate cannot be BUDGETS_WITHIN_CAPS without a calibration tied to the exact clean source revision and ENV-1.0 digest. The measured NUM-03 calibration is restricted to the workload recorded in the [task evidence](../../work-items/NUM-03.md); other contexts without a matching profile remain INDETERMINATE. A budget-fit report never authorizes or starts execution by itself.

**If unsuccessful:** F-05; refine cost model or select a scientifically justified smaller experiment.

## NUM-03 — Implement the selected field backend

**Latest owner-directed continuation — 2026-10-06:** The owner authorized the DEC-007 independent-reference fallback after receiving the requested BEM core explanation. A mixed-normal half-space kernel and zero-mode Burton–Miller ring components pass 26 focused checks, including free-space Maue identity controls and analytic sphere-mode jump/coupling checks. The direct Maue and smooth-but-near-singular image terms are kept separate. The image identity, near-singular quadrature, mesh, solve and P4 acceptance remain open. The exact-source half-space CBIE, HBIE and combined Burton–Miller sphere identity checks now pass bounded single-point regression tests. The combined residual stabilizes near `1.22e-6`; this is not an accuracy tolerance or field qualification. The off-equator Cauchy prototype showed its local singular coefficient approaching the prediction, but HBIE residual remained near 0.374 through meridian order 512 and azimuth refinement 512–4,096. The CBIE control decreased to `5.42416e-6` at order 512. Exact source snapshots and records are preserved locally; next isolate direct Maue, adjoint, jump, image and measure terms. No matrix work. Hasegawa remains the selected P4 method. See the [kernel foundation note](../../research/NUM-03-bem-kernel-foundation.md).

**Current state:** ACTIVE — isolated numerical kernels, the scaled coupled Hasegawa piston/stationary-sphere evaluator, run-level preflight adapter and immutable field bundle are recorded in [NUM-03](../../work-items/NUM-03.md) and the linked reviews. Under [DEC-007](../../decisions/DEC-007-p4-field-only-error-budget.md), P4 is field-only; no numerical tolerance has been adopted. The solver retains order cap 512 and domain `a<=r<d`. Exact-rational candidate bounds cover the mathematical order>512 tail at every angle and all accepted radii at each of the 300 P1.3 gap samples. A separate exact-`Fraction` implementation re-derives four checkpoints, and the 300-row sweep reruns byte-identically; this is same-agent evidence, not external review. The bounds do not cover arbitrary gaps between samples, arithmetic/reference uncertainty or physical-model discrepancy, and the broadest sampled gradient bound at 29.9 mm establishes no pass. New 300-digit direct Rayleigh-disk comparisons at fixed gaps 0.1, 10, 20 and 29.9 mm use the same 111-point grid at each gap. An independent composite-Simpson family approaches high-order Gauss–Legendre values as panels are refined, with late adjacent-level changes consistent with fourth-order behavior. Highest-Simpson versus Gauss–Legendre 512 normalized velocity/gradient differences range from `9.92e-8` at 29.9 mm to `3.93e-5` at 0.1 mm. These are finite-grid, conditional sensitivity results, not rigorous quadrature bounds or full-domain reference uncertainty. A candidate Simpson remainder route is documented, with exact-rational derivative majorants for source modes 0–7 at 0.1 mm only, with successive ratios increasing to about 102 by n=7; simple exponent regrouping does not tighten the bounds. Validated interval prototypes at modes 0, 6, 7 and 8 and H=0.1 mm tighten their one-cell derivative majorants about 2.2×, 174×, 304× and 380× using 128 u-subintervals; the n=8..19 interval bounds cover all 300 discrete P1.3 gaps and are contained by exact-rational global bounds. At n=20, interval and global upper bounds do not nest; their exact minimum per gap gives a combined coefficient-only bound. The combined N=8192 remainder peaks at `4.3490e-8 m^2` at 0.1 mm. Neither route covers intermediate gaps, field propagation or complete rounding/reference uncertainty. Four exact-context resource calibrations and all 12 candidate request preflights now pass on clean source `1682dcb`; maximum per-request estimate is 32.71 s, 59.05 MB RAM and 235,520 bytes disk, but execution remains unauthorized. Existing comparisons and the bounded one-gap/one-point run remain scientifically INDETERMINATE; the order1600 attempt exceeded its 300 s cap. The [NUM-03 field-error protocol basis](../../research/NUM-03-field-error-protocol.md) records comparison metrics and why current evidence cannot justify a numeric threshold: P1.3 provides figure-derived force readings, not a field-accuracy requirement or measured field reference. Next resolve reference/rounding uncertainty and benchmark-use criteria; do not run the field matrix while the plan is DRAFT or start broad NUM-04 until its prerequisites are supported. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-02

**Steps**

1. Implement the smallest domain and boundary case from the decision, using validated scenario/result contracts.
2. Report solver residuals, iterations, discretization, boundary and precision metadata; propagate typed failure.
3. Compare an initial bounded pilot with the matched P3 reference before adding geometry features.

**Required artifacts:** Numerical backend; pilot config/manifests; typed solver diagnostics. Intermediate kernel verification is tracked separately and does not satisfy these deliverables.

**Acceptance / decision:** The pilot returns correctly normalized fields and explicit convergence/failure diagnostics; initial comparisons justify refinement work.

**If unsuccessful:** F-01/F-04/F-05; reduce to the matched analytical case.

## NUM-04 — Measure observable convergence across three levels

**Initial state:** BLOCKED until the benchmark-specific observables, sample set, reference uncertainty, acceptance/stopping rule and resource cap are frozen under NUM-03/DEC-007. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-03

**Steps**

1. Freeze the physical primary observable, sample locations, refinement sequence and acceptance budget.
2. Run at least three discretization levels; record all outcomes and raw error estimates.
3. Study interpolation/gradient error when needed by downstream force and diagnose nonmonotonic trends instead of forcing an order fit.

**Required artifacts:** B-07 convergence protocol, manifests/table and observable plots.

**Acceptance / decision:** The field and required derivatives meet the declared numerical budget with a defensible convergence interpretation.

**If unsuccessful:** F-04; isolate discretization, conditioning and sample error.

## NUM-05 — Bound boundary and domain contamination

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-04

**Steps**

1. Vary domain extent, absorbing-layer parameters or boundary discretization separately from interior refinement as applicable.
2. Check the chosen wall/impedance model against an independent simple solution or published numerical benchmark.
3. Quantify the effect on the same primary observable and identify where the selected backend lacks coverage.

**Required artifacts:** Boundary/domain sensitivity report and qualified operating subdomain.

**Acceptance / decision:** Boundary effects are below the allocated error budget or their unresolved contribution is explicitly gate-blocking.

**If unsuccessful:** D-04/F-03/F-04; choose appropriate boundaries or restrict a new domain.

## NUM-06 — Reconcile cost, precision and reproducibility

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-05

**Steps**

1. Measure runtime, peak memory, actual output volume and solver iteration count for completed/failed pilots.
2. Compare to preflight and update its documented safety envelope; profile before considering GPU or remote execution.
3. Check precision sensitivity and complete RUN-02 replay for a representative numerical case.

**Required artifacts:** Resource report; environment/precision record; updated preflight; reproduction evidence.

**Acceptance / decision:** The next planned run fits a supported resource envelope and scientific changes are not hidden in backend selection.

**If unsuccessful:** F-05/F-09; retain failure and adjust execution method, not the claim.

## NUM-07 — Close the field solver gate

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** NUM-06, RUN-02

**Steps**

1. Review B-07, boundary limits, resource prediction, replay and requirement mapping.
2. Publish command usage and the model/geometry capability table with explicit unsupported cases.
3. Record P4 PASS or remaining gate conditions, then permit force-model implementation in the reviewed field domain.

**Required artifacts:** P4 gate review; backend guide; field evidence bundle and updated board.

**Acceptance / decision:** Every required reference/convergence/resource/replay item is present and no hard MCLF failure is promoted.

**If unsuccessful:** F-04/F-09/F-11; continue only work independent of the missing gate.

## Phase exit review

One fast backend reproduces reference observables, required refinements and boundary checks pass, predicted resource use is reconciled with measurements, and RUN-02 replay works.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.


### Interval enclosure comparison at modes 0 and 6 — 2026-10-05

The same exact-rational interval implementation was evaluated at 128 equal `u`-subintervals for modes `n=0` and `n=6`, at the same fixed gap `H=0.1 mm`. For n=0, the interval M4 upper bound is `0.0622085092956504108006773269057`, compared with its existing global exact majorant `0.138000671955546614706827784474` (about 2.22× tighter); its N=8192 coefficient-only Simpson bound is `7.67392437195990728690559839484e-24 m^2`. For n=6, interval M4 is `0.882659194556436413064051348714`, compared with the exact global majorant `153.969263574786446877579636640` (about 174.44× tighter); the N=8192 coefficient-only bound is `1.08883173410405704624188355970e-22 m^2`. Both scripts check their upward Decimal displays, the exact Simpson factor and stdout summary; exact enclosures are no larger than the corresponding global exact majorants. A separate replay of each produced byte-identical metadata and summary. Mode-0 JSON/stdout SHA-256: `b917445888e62320b3fed21f94dad08dc54e79fdd7aafb09cc16d1cffa70e92b` / `c68d933513478bb06f2817c61fe81951ab77b7cf59069a156a106ed78839e39d`. Mode-6 JSON/stdout SHA-256: `b93bfc43372b7ce121609dbfd428e658249a8d181c50bbfce2b702f591705a23` / `b8ab3aee66ebce804665b04350d8f773848d2793bae98b632f273d231acf8d5d`.

Together with n=7 (128-cell interval M4 `2.59240346635350815654859326849`, about 303.56× tighter than its global exact majorant), these checks support continuing the bounded method investigation. They do not establish bounds for intervening/higher modes, other gaps, field observables, total error or physics. NUM-03 remains ACTIVE/INDETERMINATE; no threshold or gate changes. Next, test n=8 with an exact global comparator and assess interval width and cost; keep one-gap/source-coefficient scope.


### Mode-eight interval enclosure — 2026-10-05

The exact-rational global generator was extended to `n=8`, reproducing all existing exact M4 comparators for modes 0–7. At `H=0.1 mm`, its global triangle majorant is `4352.61045638364039762934462173`; the n8/n7 ratio is `5.53092521993348178041230216197`. A 128-cell interval enclosure gives `M4 <= 11.4563625202142231837086521713`, about 379.93× tighter than that same-mode global majorant. The N=8192 coefficient-only Simpson bound is `1.41323527204383510553377879307e-21 m^2`. Exact containment, upward decimal, Simpson-factor and stdout checks passed; the interval script replayed byte-identically. Mode-8 global JSON/stdout SHA-256 `b10ea3ce5a9ea2acc0cd108431b7fd0b0e09a9e259993d61cfa4b6ad6fac1206` / `22c8e15dd76997b600a59368e6fed1dcfcb15d53d058251c0c09fa472356d0c1`. Corrected interval attempt 03 JSON/stdout SHA-256 `777d4d585b738557571369cbd753bb5d1d3652fd14fa8da98a2681ee48a12a77` / `4b46a60a034ccd081471b263673109453e77ab2dd32d51c4dfe511e0035c2bad`. The setup failures (syntax error and wrong dependency filename, both before any accepted result) remain preserved in `NUM03-SIMPSON-INTERVAL-MODE8-SETUP-FAIL-20261005-01.txt`. The diagnostic used system CPython 3.13.5; it is separate from the ENV-1.0 solver qualification.

This is still only one source coefficient and one fixed gap. No modal range through 512, field propagation, other gap, total rounding/reference budget or physical observation is certified. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED; no threshold or gate change follows. Next, assess gap dependence by testing a bounded far-gap case with an exact same-mode comparator and checking whether the chosen `u` partition still gives useful interval widths.


### Mode-eight far-gap interval enclosure — 2026-10-05

To check gap dependence, the mode-8 exact global majorant and interval enclosure were repeated at `H=29.9 mm` (`D=54.9 mm`). The phase interval is reduced by `8π`, appropriate to this configuration. The exact global M4 majorant is `4.01545929178745133730198730836`; the 128-cell interval M4 bound is `0.00838114275077458596704327728133`, about 479.11× tighter. The N=8192 coefficient-only Simpson bound is `1.03388196162001837572773240103e-24 m^2`. Exact same-gap containment, upward rounding, phase/configuration metadata, Simpson factor and stdout checks pass. The corrected interval script replays byte-identically in both system CPython 3.13.5 and project ENV-1.0 / CPython 3.12.14. Global-bound JSON/stdout SHA-256 `483feaa206e6a9b4bf9ad3e0d4f80eed03be1c7e3fda227047eaab8254271708` / `9f743a67482979ad977e81feb7b77225d6c67300b24a671d5b4e41b5b1c7ba54`; interval JSON/stdout SHA-256 `dec67be2e4a35fa164823ecdf064dd1d1e8192edb22af59e2c3f6f2020781b1e` / `41696900251874b66422bcdd84e6c64d19f3d6caa05f1cae62aedb83c6b36610`. The mismatched-metadata interrupted attempt 01 is preserved in `NUM03-SIMPSON-INTERVAL-MODE8-FAR-GAP-SETUP-FAIL-20261005-01.txt`; corrected attempt 02 is the only accepted result.

This is one more diagnostic point at one mode and does not establish behavior between gaps or across modes, propagate to field observables, close arithmetic/reference uncertainty or validate an experiment. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, repeat this bounded method at an intermediate declared gap (10 mm) with a freshly computed same-gap comparator; do not interpolate across the 300-gap program from these points.


### Mode-eight intermediate-gap interval enclosure — 2026-10-05

At `H=10 mm` (`D=35 mm`), mode-8 global M4 is `175.126150564895092633901624593`. With 128 equal `u` cells and phase reduced by `6π`, the interval M4 bound is `0.334296573356726281404978833314`, about 523.86× tighter than the exact same-gap global majorant. The N=8192 coefficient-only Simpson bound is `4.12381947548811302396529301995e-23 m^2`. Exact mode/gap/phase metadata, containment, outward decimals, Simpson factor and JSON/stdout checks pass. The corrected attempt replays byte-identically using both system CPython 3.13.5 and project CPython 3.12.14. Global JSON/stdout SHA-256 `61fef042b51ec3f90230cca58462f0df0bf7ea3be2318f4153535d06b80a3cac` / `94292c0de88a11816718f5f46d783e1b36676e0895e7579db433d0ac57dcacba`; interval JSON/stdout SHA-256 `10fb3ad3bba800906053b3f610d931f1a5a9d665d7061e444bd82c58e7746a13` / `8efde8bd2d3e6f2f72ebb73c26758794a578506fe8e52db073f499332eee7b50`.

Across the three tested gaps, the n=8 interval certificate is substantially tighter than its same-gap global triangle majorant. These are only three conditional coefficient bounds; this does not establish the 300-gap range, modes 0–512, field-error propagation, complete numerical uncertainty or physical validity. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, evaluate the remaining selected checkpoint `H=20 mm` with an independently constructed same-gap majorant before discussing any wider campaign.


### Mode-eight interval enclosure at 20 mm — 2026-10-05

At `H=20 mm` (`D=45 mm`), the exact same-gap global M4 majorant is `19.7577657519269811574998952868`. With 128 equal `u` cells and phase reduced by `6π`, the interval bound is `0.0340021711315774712400633620069`, about 581.07× tighter. The N=8192 coefficient-only Simpson bound is `4.19444369750245796465838098405e-24 m^2`. Exact configuration, phase, containment, upward-rounding, Simpson-factor and JSON/stdout checks pass. Replay in project CPython 3.12.14 is byte-identical to the original system CPython 3.13.5 run. Global JSON/stdout SHA-256 `7c7c998731e0c94a2e20284ee5b02ac063c597c351a30503f29ecc94e37c690b` / `0a3e60686c9c2c13966f93ee3d32ff2437eb6ea656c798f4cdc4328871bc6cc4`; interval JSON/stdout SHA-256 `efbb64a51ed36b37ac430eae5bd6332cb6ab3cb3e883e5efa7404e05a1e44f25` / `931b1cfd04ae3d7f7faac8d7563a77ea8a5c2a2f1a7883bc8d728a1259c64f48`.

For mode 8 at the four selected gaps `0.1, 10, 20, 29.9 mm`, the 128-cell intervals are all substantially tighter than the corresponding exact same-gap global triangle majorants. This is not uniform coverage between those gaps, across modes, or over the full accepted field domain. It remains a source-coefficient quadrature estimate, not a P4 pass or physical validation. NUM-03 stays ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next assess the computational cost and interval widths needed to extend mode 8 over all 300 declared gap samples; do not infer full-domain or all-mode validity from the four selected checkpoints.
# NUM-03 continuation checkpoint — 2026-10-05

The Simpson quadrature-remainder investigation now has exact-rational global derivative majorants for source modes 0–7 at the 0.1 mm gap, plus a 128-cell outward-rounded fixed-point interval enclosure for mode 8 at all 300 discrete P1.3 gaps from 0.1 to 30.0 mm in 0.1 mm steps. An independent exact-rational same-gap comparator contains all 300 mode-8 bounds. Their interval M4 bounds are 166.08–308.32 times tighter than the comparator; the N=8192 coefficient-only remainder bounds range from `2.0443e-24` to `2.5272e-21 m^2`. These are coefficient-integral remainder bounds only. No arbitrary-gap coverage, all-mode coverage, propagation into field observables, total arithmetic/reference uncertainty, or physical validation follows. The interval route is wider than the earlier exact-rational checkpoint values and that difference is recorded.

NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 remains BLOCKED. No tolerance or gate changes. Next, check mode 9 at the minimum gap against a fresh exact global comparator, then assess whether extending the interval route to additional modes is worthwhile before any field propagation. See [NUM-03](../../work-items/NUM-03.md), the [field-error protocol](../../research/NUM-03-field-error-protocol.md), and its [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 mode-by-mode remainder continuation — 2026-10-05

Outward-rounded fixed-point interval enclosures now cover the mode-8, mode-9, mode-10, and mode-11 source-coefficient Simpson remainders at each of the 300 P1.3 gap samples. Exact-rational, same-gap global derivative majorants independently contain every result. Their tightening factors over the global majorants are 166.08–308.32× (n=8), 216.56–493.41× (n=9), 211.00–746.12× (n=10), and 201.48–887.15× (n=11). Five-point cross-version replays and exact formula/outward-rounding audits pass. The largest N=8192 coefficient-only remainder at the minimum gap increases from `2.5272e-21 m^2` to `6.8089e-19 m^2` over n=8–11. This does not establish an all-mode sum, gap continuity, field-observable error or physical validity; the method's higher-order usefulness remains open. NUM-03 stays ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, evaluate n=12 at four selected gaps, then decide whether to continue the campaign. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=12 continuation — 2026-10-05

The n=12 source-coefficient Simpson remainder is now enclosed over all 300 sampled gaps and contained by exact-rational same-gap global derivative majorants. The global-to-interval tightening is 192.45–1003.87×. Its N=8192 coefficient-only remainder bound spans `5.1395e-18 m^2` at 0.1 mm to `1.0827e-22 m^2` at 30.0 mm. Exact formula, outward rounding, gap sequence, containment and five-point cross-version replay checks passed. The preserved first attempt lacked an inverse-k cache entry at `k^-13`; the corrected range includes it. This remains coefficient-only for n=12 and does not establish an all-mode sum or field accuracy. NUM-03 stays ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next screen n=13 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=13 continuation — 2026-10-05

Mode 13 has an outward-rounded coefficient Simpson-remainder enclosure at all 300 discrete P1.3 gaps. Exact-rational same-gap global bounds contain every interval result; their ratio is 184.58–1004.21×. At N=8192 the coefficient-only remainder bound ranges from `4.0807e-17 m^2` at 0.1 mm to `4.8541e-22 m^2` at 30.0 mm. Exact factor/gap/rounding audits and a five-gap cross-version replay pass. Two failed comparator setups were preserved before the corrected script validated all rows. This remains one coefficient and one quadrature remainder term, with no all-mode or field-observable result. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=14 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=14 continuation — 2026-10-05

Mode 14 has a checked coefficient Simpson-remainder enclosure at all 300 discrete P1.3 gaps. Exact-rational same-gap global comparators contain every interval result; tightening factors span 177.95–986.85×. The N=8192 coefficient-only upper bound is `3.3976e-16 m^2` at 0.1 mm and `2.2807e-21 m^2` at 30.0 mm. Exact formula, gap sequence, outward display and five-case cross-version replay checks passed. No field sum, total error or physical result follows. NUM-03 remains ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next, screen n=15 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=15 continuation — 2026-10-05

Mode 15 has an outward-rounded coefficient Simpson-remainder enclosure at all 300 discrete P1.3 gaps. Its exact-rational same-gap global comparators contain every result, with tightening factors from 172.44× to 955.62×. The N=8192 coefficient-only remainder ranges from `2.9601e-15 m^2` (0.1 mm) to `1.1202e-20 m^2` (30.0 mm). Exact gap/factor/display audits and five-point cross-version replay passed. This does not provide an all-mode or field-observable error bound. NUM-03 remains ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next, screen mode 16 at four representative gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=16 continuation — 2026-10-05

Mode 16's source-coefficient Simpson remainder is enclosed at all 300 P1.3 gaps. Exact global same-gap containment, rational gap sequence, N=8192 factor, outward displays, and cross-version replay passed. The global/interval ratio is 167.90–924.50×; the coefficient-only remainder spans `2.6938e-14 m^2` at 0.1 mm to `5.6807e-20 m^2` at 30 mm. The run took about 10 minutes on one core and 17 MB RSS, a diagnostic workload measure only. No total field error or physical validation follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=17 at four gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).

## NUM-03 n=17 continuation — 2026-10-05

Mode 17's coefficient remainder is enclosed at all 300 discrete P1.3 gaps and contained by exact-rational same-gap global bounds. Tightening is 164.18–894.95×; the N=8192 coefficient-only remainder ranges from `2.5566e-13 m^2` at 0.1 mm to `2.9710e-19 m^2` at 30 mm. Exact sequence, formula, upward display and cross-version replay audits passed. The run took about 10.5 minutes on one core with 17–18 MB RSS. This remains an isolated coefficient term and supports no field-accuracy claim. NUM-03 ACTIVE/INDETERMINATE; NUM-04 BLOCKED. Next, screen n=18 at four gaps. See the [task](../../work-items/NUM-03.md), [protocol](../../research/NUM-03-field-error-protocol.md), and [review](../../reviews/NUM-03-coupled-kernel-review.md).


## NUM-03 bounded coefficient-remainder continuation — 2026-10-05

Modes 8–18 now have 128-cell outward-rounded fixed-point interval enclosures at all 300 discrete P1.3 gaps, contained by exact-rational same-gap global comparators. For n=18, the coefficient-only N=8192 remainder spans `2.5561e-12 m^2` at 0.1 mm to `1.6003e-18 m^2` at 30 mm; exact gap, formula, decimal and containment audits pass, and five selected points replay across Python 3.12.14/3.13.5. This does not cover gap interpolation, other modes, field propagation, full error budget or physical behavior. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=19 at four representative gaps and assess the growing bound before another full sweep.

## NUM-03 n=19 coefficient remainder — 2026-10-05

The n=19 source-coefficient Simpson remainder is enclosed at all 300 discrete P1.3 gaps; all exact-rational same-gap global comparators contain the interval bounds, and formula, outward-display and five-point cross-version audits pass. Relative to n=18, the minimum-gap bound rises about 59× and the 30 mm bound about 5.6×; the global/interval ratio ranges from 27× to 840×. No interpolation, other modes, field propagation, total uncertainty or physical claim follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=20 at four representative gaps.


## NUM-03 n=20 combined coefficient bound — 2026-10-05

For n=20, the independently derived global M4 bound is tighter at 86 of the 300 P1.3 gaps; the 128-cell interval bound is tighter at 214. Both bounds are retained, and their exact minimum gives the combined coefficient-only N=8192 remainder, peaking at 4.3490e-8 m^2 at 0.1 mm. At that gap, refining the interval to 1,024 cells only reduces its M4 by about 0.43%, leaving it wider than the global bound. This is still one source coefficient; no field propagation, total uncertainty, tolerance or physical result follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=21 at four representative gaps.


## NUM-03 n=21 coefficient bounds — 2026-10-05

An exact-rational global source-coefficient Simpson bound covers all 300 discrete gaps; the 128-cell interval method was compared at four representative gaps only. The global bound is tighter at three of the four comparison points. The five-point interval replay matches across Python 3.12.14/3.13.5. This does not give a full-grid combined bound, field result, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=22 at four representative gaps.


## NUM-03 n=22 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers all 300 discrete P1.3 gaps for mode 22; its N=8192 coefficient-only remainder ranges from 5.4396e-6 m^2 at 0.1 mm to 1.3891e-12 m^2 at 30 mm. Four 128-cell interval checks are all wider than their same-gap global bounds, with global/interval ratios from 4.54e-7 to 0.00311. Five selected interval points replayed identically across CPython 3.12.14 and 3.13.5. The all-row formula/display audit passed after correcting and retaining harness errors. This is one coefficient, at discrete gaps only; no field propagation, total uncertainty, tolerance, or physical validation follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=23 at four representative gaps.


## NUM-03 n=23 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 23 at all 300 discrete P1.3 gaps; the N=8192 coefficient-only remainder ranges from 6.4324e-5 m^2 at 0.1 mm to 8.4578e-12 m^2 at 30 mm. Four 128-cell interval checks are all wider than their same-gap global upper bounds. Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5, and the all-row exact formula/display audit passed. This remains one source coefficient with no interpolation, field propagation, total uncertainty, tolerance, or physical result. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=24 at four representative gaps.


## NUM-03 n=24 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 24 at all 300 discrete P1.3 gaps; the N=8192 coefficient-only remainder ranges from 7.8813e-4 m^2 at 0.1 mm to 5.3002e-11 m^2 at 30 mm. Four 128-cell interval checks are all wider than their same-gap global upper bounds. Five selected interval points replayed identically across CPython 3.12.14 and 3.13.5; the exact formula/display audit passed after correcting and preserving a stale-mode assertion in the audit harness. This remains one source coefficient only, with no field propagation, total uncertainty, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=25 at four representative gaps.


## NUM-03 n=25 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 25 at all 300 discrete P1.3 gaps; the N=8192 coefficient-only remainder ranges from 9.9939e-3 m^2 at 0.1 mm to 3.4163e-10 m^2 at 30 mm. Four 128-cell interval checks are all wider than their same-gap global upper bounds. Five selected interval points replayed identically across CPython 3.12.14 and 3.13.5, and the exact formula/display audit passed on its first attempt. This remains one source coefficient, with no field propagation, total uncertainty, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=26 at four representative gaps.


## NUM-03 n=26 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 26 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only remainder ranges from 0.1310109 m^2 at 0.1 mm to 2.2635e-9 m^2 at 30 mm. Four 128-cell interval checks are all wider than their same-gap global upper bounds. Five selected interval points replayed identically across CPython 3.12.14 and 3.13.5; the all-row exact formula/display audit passed after correcting and preserving a stale-mode assertion in the audit harness. The minimum-gap number is a conservative bound for one coefficient, not an observed error or tolerance comparison. No field propagation or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=27 at four representative gaps.


## NUM-03 n=27 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 27 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only remainder ranges from 1.7737 m^2 at 0.1 mm to 1.5407e-8 m^2 at 30 mm. Four 128-cell interval enclosures are much wider than the matching global majorants, but this compares bound width only and does not measure actual error. Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, formula and upward-display audit passed. The result remains one coefficient only, without field propagation, total uncertainty, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=28 at four representative gaps.


## NUM-03 n=28 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 28 at all 300 discrete P1.3 gaps; the N=8192 coefficient-only remainder ranges from 24.7751 m^2 at 0.1 mm to 1.0767e-7 m^2 at 30 mm. Four interval enclosures are far wider than their matching global bounds. Large interval remainder values are enclosure widths, not actual errors. Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5, and the 300-row exact audit passed. This remains one source coefficient only, without field propagation, total uncertainty, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=29 at four representative gaps.


## NUM-03 n=29 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 29 at all 300 discrete P1.3 gaps; the N=8192 coefficient-only remainder ranges from 356.7267 m^2 at 0.1 mm to 7.7206e-7 m^2 at 30 mm. Four interval enclosures are far wider than their matching global upper bounds. Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; the exact 300-row audit passed. The growing upper bound is not an observed error trend. No field propagation, total uncertainty, tolerance, or physical validation is established. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=30 at four representative gaps.


## NUM-03 n=30 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 30 at all 300 discrete P1.3 gaps; the N=8192 coefficient-only remainder ranges from 5290.0478 m^2 at 0.1 mm to 5.6778e-6 m^2 at 30 mm. Four interval enclosures are far wider than the matching global bounds. Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; the exact 300-row audit passed. This is one source coefficient only: no field propagation, total uncertainty, tolerance or physical validation is established. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=31 at four representative gaps.

## NUM-03 n=31 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 31 at all 300 discrete P1.3 gaps. Its N=8192 coefficient-only remainder upper bound ranges from 80729.7932 m^2 at 0.1 mm to 4.2799e-5 m^2 at 30 mm; the minimum of the sampled bounds occurs at 30 mm. Four interval enclosures are much wider than their matching global bounds, a comparison of upper-bound widths only. Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; the corrected exact 300-row audit passed after retaining an initial verifier count error. This is one source coefficient only and does not establish actual error, field propagation, total uncertainty, a tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=32 at four representative gaps.

## NUM-03 n=32 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 32 at all 300 discrete P1.3 gaps. The N=8192 coefficient-only upper bound ranges from 1266843.2376 m^2 at 0.1 mm to 3.3052e-4 m^2 at 30 mm. A 128-cell interval enclosure also covers all 300 gaps and is wider than the matching global bound at every point; the all-grid interval took about 38 minutes because the script default selected all points. Its output metadata was corrected without changing numeric rows, then all coordinates, formulas, upward displays and the five-point CPython 3.12/3.13 replay were audited. This remains a one-coefficient result and establishes no actual error, field propagation, total uncertainty, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=33 at four representative gaps.

## NUM-03 n=33 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 33 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 20427175.765 m^2 at 0.1 mm to 0.002613732 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 5.60e-36–1.07e-31). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed on all 300 global rows. This is one source coefficient only and establishes no actual error, field propagation, total uncertainty, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=34 at four representative gaps.

## NUM-03 n=34 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 34 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 338210955.3064 m^2 at 0.1 mm to 0.0211549 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.31e-38–2.67e-34). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for the 300 global rows. This is one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=35 at four representative gaps.

## NUM-03 n=35 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 35 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 5746099429.443 m^2 at 0.1 mm to 0.1751664 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 3.05e-41–6.64e-37). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This is one source coefficient only and does not establish actual error, field propagation, total uncertainty, a tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=36 at four representative gaps.

## NUM-03 n=36 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 36 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 100113041055.6386 m^2 at 0.1 mm to 1.48315967 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 7.09e-44–1.64e-39). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This is one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=37 at four representative gaps.

## NUM-03 n=37 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 37 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 1787635314974.559 m^2 at 0.1 mm to 12.83620176 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.65e-46–4.06e-42). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This is one source coefficient only and establishes no actual error, field propagation, total uncertainty, tolerance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=38 at four representative gaps.

## NUM-03 n=38 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 38 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 32695544359386.566 m^2 at 0.1 mm to 113.5054456 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 3.84e-49–1.00e-44). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This is one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=39 at four representative gaps.

## NUM-03 n=39 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 39 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 612183120482627.537 m^2 at 0.1 mm to 1025.0721024 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 8.91e-52–2.46e-47). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=40 at four representative gaps.

## NUM-03 n=40 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 40 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 11728147991585962.293 m^2 at 0.1 mm to 9451.077968 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 2.07e-54–6.01e-50). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=41 at four representative gaps.

## NUM-03 n=41 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 41 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 229781348429398290 m^2 at 0.1 mm to 88927.18916 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 4.80e-57–1.47e-52). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=42 at four representative gaps.

## NUM-03 n=42 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 42 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 4601807645781298436.739 m^2 at 0.1 mm to 853603.7751 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.11e-59–3.57e-55). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=43 at four representative gaps.

## NUM-03 n=43 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 43 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 94160814766214248068 m^2 at 0.1 mm to 8355911.955 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 2.58e-62–8.67e-58). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=44 at four representative gaps.

## NUM-03 n=44 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 44 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 1967649836307743725961 m^2 at 0.1 mm to 83387151.115 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 5.97e-65–2.10e-60). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=45 at four representative gaps.

## NUM-03 n=45 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 45 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 41973646506864473646407 m^2 at 0.1 mm to 848064193.054 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.38e-67–5.08e-63). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. An initial cached-wavenumber range omitted exponent -46 and was corrected; the setup failure is retained locally. Next, screen n=46 at four representative gaps.

## NUM-03 n=46 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 46 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 913649189228407214913697 m^2 at 0.1 mm to 8787059430.437 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 3.19e-70–1.23e-65). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=47 at four representative gaps.

## NUM-03 n=47 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 47 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 20285490552266209485814811 m^2 at 0.1 mm to 92727551069.136 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 7.39e-73–2.95e-68). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=48 at four representative gaps.

## NUM-03 n=48 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 48 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 459230380070775813051682755 m^2 at 0.1 mm to 996307926026.046 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.71e-75–7.09e-71). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=49 at four representative gaps.

## NUM-03 n=49 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 49 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 10596357519338070710846455671 m^2 at 0.1 mm to 10896098052527.669 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 3.94e-78–1.70e-73). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=50 at four representative gaps.

## NUM-03 n=50 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 50 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 249121414946445767262063484269 m^2 at 0.1 mm to 121260070785386.562 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 9.11e-81–4.08e-76). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=51 at four representative gaps.

## NUM-03 n=51 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 51 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 5.96550189201492649644122794965e30 m^2 at 0.1 mm to 1372822469367359.032 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 2.10e-82–9.74e-78). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=52 at four representative gaps.

## NUM-03 n=52 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 52 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 1.45452948100406821859283792381e32 m^2 at 0.1 mm to 15806818660899298.186 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 4.85e-84–2.33e-79). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=53 at four representative gaps.

## NUM-03 n=53 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 53 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 3.60994608770357314674577561967e33 m^2 at 0.1 mm to 185052595001216932.211 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.12e-85–5.55e-81). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=54 at four representative gaps.

## NUM-03 n=54 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 54 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 9.11694269578450232608720581180e34 m^2 at 0.1 mm to 2202200029888118303 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 2.58e-87–1.32e-82). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=55 at four representative gaps.


## NUM-03 n=55 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 55 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 2.34228717387175587780385618755e36 m^2 at 0.1 mm to 26633150120938749038.8759390271 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 5.95e-89–3.14e-84). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=56 at four representative gaps.


## NUM-03 n=56 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 56 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 6.11997634842692645167743053830e37 m^2 at 0.1 mm to 327256851052929069463.374598739 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.37e-91–7.45e-87). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=57 at four representative gaps.


## NUM-03 n=57 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 57 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 1.62576703734198500044032055818e39 m^2 at 0.1 mm to 4084646431013794330622.05150534 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 3.16e-94–1.77e-89). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=58 at four representative gaps.


## NUM-03 n=58 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 58 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 4.38985259016262014891983390822e40 m^2 at 0.1 mm to 51775166048036482288492.9715322 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 7.28e-97–4.19e-92). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=59 at four representative gaps.


## NUM-03 n=59 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 59 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 1.20451532616340699487785239448e42 m^2 at 0.1 mm to 666337498837210235699308.599741 m^2 at 30 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval ratio 1.68e-99–9.91e-95). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=60 at four representative gaps.

## NUM-03 n=60 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 60 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 3.35765968263341350505025646694e43 m^2 at 0.1 mm to 8.70521837374114834293660535397e24 m^2 at 30.0 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval M4 ratio 3.86e-102–2.35e-97). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=61 at four representative gaps.

## NUM-03 n=61 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 61 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 9.50643021479327970950241131297e44 m^2 at 0.1 mm to 1.15421607131986575202835548850e26 m^2 at 30.0 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval M4 ratio 8.89e-105–5.54e-100). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. Two failed setup/audit attempts are retained locally and excluded; corrected attempt 09 passed. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=62 at four representative gaps.

## NUM-03 n=62 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 62 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 2.73308002540622841822507852644e46 m^2 at 0.1 mm to 1.55284571670357965875042498865e27 m^2 at 30.0 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval M4 ratio 2.05e-107–1.31e-102). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=63 at four representative gaps.

## NUM-03 n=63 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 63 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 7.97704426440337092407850608110e47 m^2 at 0.1 mm to 2.11942091566566865407668227967e28 m^2 at 30.0 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval M4 ratio 4.71e-110–3.08e-105). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. One premature audit invocation before the global output existed is retained locally and excluded; the completed rerun passed. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=64 at four representative gaps.

## NUM-03 n=64 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 64 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 2.36314294695257018763517373950e49 m^2 at 0.1 mm to 2.93406675116897783646368440715e29 m^2 at 30.0 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval M4 ratio 1.08e-112–7.26e-108). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=65 at four representative gaps.

## NUM-03 n=65 sampled-gap coefficient bounds — 2026-10-05

The exact-rational global triangle bound covers mode 65 at all 300 discrete P1.3 gaps; its N=8192 coefficient-only upper bound ranges from 7.10399516545257345321407531425e50 m^2 at 0.1 mm to 4.11912416258234820010840358135e30 m^2 at 30.0 mm. Four 128-cell interval comparisons are much wider than their matching global bounds (global/interval M4 ratio 2.49e-115–1.71e-110). Five selected interval points replayed byte-identically across CPython 3.12.14 and 3.13.5; exact gap, Simpson-factor and upward-display audits passed for all 300 global rows. A post-publication review corrected stale mode-60/n=61 comparator metadata; the exact n=65 comparisons were unchanged, and the strengthened audit now checks the corrected labels and values. This remains one source coefficient only: no actual-error, field-propagation, total-uncertainty, tolerance or physical conclusion follows. NUM-03 remains ACTIVE/INDETERMINATE and NUM-04 BLOCKED. Next, screen n=66 at four representative gaps.


## Owner-directed NUM-03 route update — 2026-10-05

By DEC-008, pause sequential mode-only coefficient screens after accepted n=65 evidence. The local n=66 global sweep passed an exact audit of its 300 discrete coordinates, Simpson factors and outward displays, but is not an accepted package; its four-gap interval run was interrupted without output and remains preserved locally. The next task is to review and complete the proposed field-reference qualification protocol before further computation. This task-order change does not pass P4 or change NUM-03's ACTIVE/INDETERMINATE status.


## NUM-03 reference-plan configuration audit — 2026-10-05

The order-overlap artifact family ends at 30.0 mm and uses `rho=1.204 kg/m^3`; it does not match the NUM-01 air contract. Separately, the 0.1/10/20/29.9-mm cross-quadrature artifacts use `rho=1.18 kg/m^3` and share a 37-angle, three-radius candidate point pattern. They do not supply three matched modal orders across those gaps. The plan proposes public-solver orders 256/384/512, with any reference-only tail above512 treated separately. Existing timing calibration reaches only `kr=12.38`; the candidate outer shell is about `kr=25.0162`. DEC-008 therefore requires a bounded worst-case calibration and resource estimate before a multi-gap matrix. No existing numbers were modified or combined. NUM-03 remains ACTIVE/INDETERMINATE; P4 remains unpassed.


## NUM-03 resource checkpoint — 2026-10-05

The outer-shell runtime calibration measured the candidate field radius on exact clean source `fccdff840e73f11ecbd9b43f80bfdf1a3dd377ab` and ENV-1.0. Its historical per-order preflights estimated 70.66/105.85/141.04 s, with 317.55 s serial total. A later request audit established that their exact `bessel_argument_max=25.016215925297676` omits the source-integration endpoint in the admission workload, which is `25.567073592698655`; those estimates remain preserved but do not pass exact workload matching. A new calibration and preflight at the admitted dimension are required before execution. NUM-03 is ACTIVE / INDETERMINATE, P4 is not passed, and NUM-04 remains BLOCKED. See the [qualification plan](../../research/NUM-03-reference-qualification-plan.md) and [NUM-03 task](../../work-items/NUM-03.md).

The requirement for a new calibration in this historical checkpoint was satisfied by the later per-gap resource audit below; it is retained as dated evidence of the earlier mismatch.


## NUM-03 matched reference-grid artifact audit — 2026-10-05

A follow-up audit established that the canonical-air high-precision quadrature artifacts already cover 0.1, 10, 20 and 29.9 mm at the same 111 ordered points per gap. GL256/512 and Simpson2048/4096/8192 all have matching rows; hashes for all 20 source files and their generating scripts agree with the comparison metadata. The 444 source rows occupy 7,507,747 bytes and comparison summaries 62,537 bytes. No timing metadata were recorded. The point generator uses Decimal `x=r sin(theta)`, `y=0`, `z=d+r cos(theta)`; casting x/z to binary64 for the public implementation leaves coordinate-rounding effects combined with implementation differences. These records are already-computed sensitivity evidence, not a quadrature remainder bound or an uncertainty-qualified reference. The accepted local audit is `results/num03-runtime-calibration/fccdff840e73f11ecbd9b43f80bfdf1a3dd377ab/reference-grid-artifact-audit.json` (SHA-256 `50cd28c998e298ad44e9a0afe5003ab9fde7e00968d43e4d0748a2f374586dca`).

The actionable next task is to freeze public binary64 requests at orders 256/384/512 on these audited rows and finish uncertainty accounting. Do not rerun or estimate resources for the existing quadrature family. NUM-03 remains ACTIVE / INDETERMINATE; the plan is DRAFT, P4 is not passed, and NUM-04 remains BLOCKED.


## NUM-03 request-admission boundary and calibration audit — 2026-10-05

The candidate request inputs use the audited Decimal point-generation rule and are locally serialized as 12 per-gap/order requests (four gaps × 111 points × orders 256/384/512). On conversion to binary64, 12/15/18/20 of the 37 exact `r=a` rows per gap produce a computed radius up to `6.94e-18 m` (two ULP) inside the represented sphere. The field evaluator already handles this with an eight-ULP tolerance and clamps the evaluation radius to `a`; run admission used a strict inequality. A narrow admission fix now applies the same tolerance and has a test that rejects a point materially inside the sphere. All 12 request payloads pass parsing and Scenario admission. Their inputs and preserved failed setup attempts are local in `results/num03-public-request-proposal/8ba37349383326d552047e5babe4edb41b46ad07/` (request-index SHA-256 `e7aa2c9309401d50dc3e3d685ffa6923f8408ab4c20bba8350a6f46adc898044`); this is not field output.

The admission calculation's maximum Bessel argument is `25.567073592698655`, from the source-integration endpoint `k*hypot(d,piston_radius)`. The preceding calibration binds only `25.016215925297676`, the outer sampled-field radius. Its accepted preflights therefore do not match the actual request dimension and cannot authorize execution. After publishing the admission correction, perform a fresh bounded calibration on the exact clean source revision at the admitted maximum argument and regenerate the NUM-02 preflights. The field matrix remains unrun; NUM-03 is ACTIVE / INDETERMINATE, P4 is not passed and NUM-04 remains BLOCKED.

## NUM-03 per-gap resource calibration and preflight audit — 2026-10-05

The admission correction is published on clean revision `1682dcbf15f1ba2e79511563639c68f9301c4d50`. Four gap-specific ENV-1.0 profiles completed 48 timing samples each (12 repetitions at orders 64, 128, 256 and 512 after warmups) and bind exact admitted Bessel dimensions: 0.1 mm / `12.378996060932124`, 10 mm / `16.6774235774195`, 20 mm / `21.12031967148223`, and 29.9 mm / `25.567073592698655`. The profile maximum coefficient rates range from `9.3467e-6` to `1.5938e-5 s/order`; maximum evaluator-residual rates range from `1.4151e-4` to `1.9128e-4 s/order/sample`. NUM-02 applies the declared 3.0 safety multiplier.

All 12 one-gap/order preflights match their request rows, calibration payload hashes, source revision, ENV-1.0 digest, quadrature order and exact Bessel dimension. Every report is `BUDGETS_WITHIN_CAPS` and retains `execution_authorized: false`. The maximum single-request estimate is 32.7052 s, 59,047,280 bytes RAM and 235,520 bytes disk, below its declared 300-s, 4-GiB and 16-MiB limits. The local audit SHA-256 is `b4c39a9b1290bc5a77b6e3bffa46525ae4cd9ee279a7bbe4c1a3f4006c77c121`; it also preserves the first audit-harness failure. Resource readiness for these proposed requests is therefore no longer the blocker. No solver matrix has run, and no field convergence, numerical-accuracy, P4 or physical result follows. Next resolve field-reference uncertainty and the intended use criterion under the draft protocol; keep DEC-008's execution condition intact.

## NUM-03 coordinate provenance alignment — 2026-10-05

A 444-row audit found 12 request coordinates at `theta=180°` that exactly reproduce from π truncated to 27 decimal places rather than the canonical Decimal/Chudnovsky generator. The corrected local proposal regenerates those 12 manifests; 36 repeated input rows change, all requests pass parsing/admission, and their preflight workload dimensions remain unchanged. The largest request-to-canonical coordinate component difference is `1.5262e-29 m`. Its field-output effect remains uncomputed. Local artifact-index SHA-256: `bc2243a68e33722342fc7fba69dbb2fd165c28cb7195c4c58cdb36c27d307673`. This resolves input provenance only; keep numerical reference uncertainty open, preserve the original inputs, and do not execute the matrix or change any gate.

## NUM-03 uncertainty coverage reconciliation — 2026-10-05

**Prior checkpoint, superseded by the continuation below:** Existing quadrature comparisons were finite-grid sensitivity evidence. At that point the coefficient bounds had not been propagated through field observables; the subsequent n=0/n=1 partial propagations are recorded below. The tail, arithmetic and field-use limitations remain open. The next action is now to assess the independent-reference fallback under DEC-007.
Existing quadrature comparisons are finite-grid sensitivity evidence, not a complete integral remainder. Simpson certificates end at n=65 and the exact-rational order>512 tail covers every angle and accepted radius at the 300 discrete P1.3 gaps, leaving retained n=66–512 without accepted quadrature bounds. Separate exact-rational propagations of the already-supported n=0 and n=1 coefficient remainders bound their pressure, velocity and gradient contributions at the 0.1 mm gap across all accepted radii and angles. These remain partial terms; the n=1 source JSON is unavailable locally, and the recorded upward decimal is used as an exact rational upper bound. The mode-separated values and independent replay are recorded in the [NUM-03 protocol](../../research/NUM-03-field-error-protocol.md) and local audit index `7dadc341e7568f862073560b649b7bcff9b90a98af0eb5aab7e2691f9d632610`. Mode trends cannot supply the missing uniform bound; further per-mode screens are paused by DEC-008. A candidate axisymmetric BEM reference protocol is prepared in the NUM-03 plan; it still requires owner explanation before any core construction and its own error/resource qualification. Hasegawa remains selected; NUM-03 remains ACTIVE / INDETERMINATE, and the solver matrix remains paused.


## Combined exact-sphere CBIE action — 2026-10-07

The streamed direct-plus-image action is committed at `9bf4d4926450004947fa9a84f86a32eb41d67007` and recorded in the [NUM-03 combined-action review](../../reviews/NUM03-BEM-exact-sphere-combined-cbie.md). Its clean ENV-1.0 run covers four collocation angles, three meridian orders, separate direct/image terms and two repeats per case. All 12 cases reproduce and the normalized identity residual decreases across meridian refinement at every angle. Final order-256 residuals range from `1.78e-6` to `2.74e-5`. Local Quality passes 1,830 tests; exact remote Quality run [37690318741](https://github.com/Andioratech/AURA/actions/runs/37690318741) passed. This is one manufactured boundary identity, not field acceptance or physical validation. NUM-03 remains ACTIVE/INDETERMINATE; the BEM preflight remains unauthorized. The first azimuth sweep found remaining direct-ring sensitivity at 120° and 135°; next extend direct azimuth counts with meridian order and image count fixed.


## Combined CBIE azimuth sensitivity — 2026-10-07

A clean ENV-1.0 36-case factorial sweep at meridian order 256 found image-layer changes below `6.0e-17 |p(x)|` across image counts 512/1,024/2,048 when direct count is fixed at 1,024. The direct single layer still changes at direct counts 256/512/1,024, most at 120°/135°. Their normalized CBIE residuals do not decrease monotonically with azimuth count. All two-repeat checksums match; artifact and exact scope are recorded in the [review](../../reviews/NUM03-BEM-exact-sphere-cbie-azimuth-sensitivity.md). This is numerical sensitivity only and does not choose a tolerance. Next extend direct counts 1,024/2,048/4,096 with meridian order and image count fixed. NUM-03 remains ACTIVE/INDETERMINATE and the matrix stays unauthorized.
## NUM-03 exact-sphere direct-azimuth refinement — 2026-10-08

The clean-source sweep on `dd7f813e17c365ed720ea5d89836e084475b41b7` fixed meridian order 256 and image azimuth count 2,048 while testing direct counts 1,024/2,048/4,096 at four collocation angles. All 12 cases completed twice with matching repeat checksums. The direct single-layer change from 2,048 to 4,096, normalized by boundary-pressure magnitude, is at most `1.0354e-10` over these points. This does not establish a quadrature bound or field accuracy; the order-256 CBIE residual remains about `2.985e-5` at 120°. Local Quality passed 1,834 tests and exact remote run [37705091852](https://github.com/Andioratech/AURA/actions/runs/37705091852) passed. Artifact SHA-256 `82fe8d2e62d856bc4e5eafa611bd8979937970726ad6d16ce61b0e2497a1dd6e`; details are in the [review](../../reviews/NUM03-BEM-exact-sphere-cbie-direct-azimuth-refinement.md). No matrix or solver was allocated. NUM-03 remains ACTIVE/INDETERMINATE, the qualification plan DRAFT and BEM preflight unauthorized. Next isolate meridian-order sensitivity at 256/384/512 with direct/image counts fixed at 4,096/2,048.
