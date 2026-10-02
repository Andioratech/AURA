# ANA-05 — Ideal Spherical Spreading

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Owner role:** research implementer

## Authority and scope

Starting revision: `7a913bece6b9c4ecf926819487fc41f0aa853a86`. ANA-04 is DONE; P2 is PASS. Apply D00, D02, D04–D09, FIELD-1.0, ANA-REF-1.0, EQ-006/009/010 and DEC-003/004. Verify the ideal outgoing spherical field's distance dependence and full reactive velocity. This is an incident-field kernel, not a finite physical radiator, water measurement, force model or microgravity result. RUN-1.0 remains diagnostic-only; P3 remains open. Larger objects and masses retain their separate model/evidence gates.

## Frozen protocol before execution

- Implement [SPHERICAL-WAVE-1.0](../research/spherical-wave-kernel.md) with explicit center, reference radius and excluded minimum radius; no guessed defaults, attenuation or far-field shortcut. Validate all geometry and phase plans before trigonometry. Reject source point and r<r_min even at zero drive.
- Five fixed configurations / 16 observations: AXIAL at r_ref, 2r_ref, 3r_ref on +x; DIRECTIONS at r_ref on -x, +y, -z and (3/5,4/5,0); COMMON-PHASE uses AXIAL with pi/2 phase; TRANSLATED shifts center and AXIAL points by (0,lambda/8,0); ZERO uses AXIAL with zero pressure. rho=1000 kg/m³, c=1500 m/s, f=1 MHz, P_ref=2 Pa, r_ref=r_min=lambda/4=0.000375 m, origin center, zero phase/loss unless modified. Box [-lambda,lambda]^3. Combined B-03…B-06 recorded matrix remains 11+8+8+5=32 configurations; no sweep.
- Independent Decimal reference: real radial amplitude differentiation, Euler velocity and independently simplified period-integral flux; no production imports or binary trig. Require 60/80-digit agreement to 45 normalized decimal places; separately verify every literal B06-01…03 value and radial vector signs.
- Keep frozen 2048e tolerance and B-06 scales from ANA-REF-1.0, including nonzero scales at zero drive. Record per-component maximum/RMS errors. Compare actual sine/cosine arguments independently within 4e and radius hypot calls within 2e relative error. Audit <=32 dependent ordinary-scale rounded operations, bounded coordinate cancellation and phase conditioning; no numerical guarantee for every admitted extreme input.
- Verify reference normalization, 1/r pressure and 1/r² radial flux, translation/rotation/common phase, Euler consistency, exact zero, order/duplicates, min-radius neighboring floats and invalid source/box/phase/loss/resource inputs. Deliberately omitted reactive velocity, wrong radial direction, missing amplitude spreading and inverse-distance flux must fail. Formal source/control-surface balance auditing remains ANA-06.
- N<=256, one source, one CPU, no GPU/randomness; workspace integer >=4096*N+4096. Measure N=256 evaluation/serialization, enforce encoded bytes<=32768+1024*N. Focused suite <10 s, full suite <60 s, clean-source timeout 30 s; scientific bundle <=16 MiB. Preserve failures and write root cause after repeated same-cause failures. No dependency change.
- Full current local Quality before every owner commit; inspect current remote CI, identity, staged diff and private-file exclusion. Push and check exact remote CI. Verify from clean published source with immutable ID/checksums and unchanged before/after source/environment. JUnit/sample records are software verification, not D07 RunManifests.

## Acceptance and handoff

Required: explicit model/source review, API/example, independent B-06 fixture/oracle/tests, numeric/resource report and artifact review. Close only when frozen comparisons, mandatory negative checks and complete CI pass. ANA-06 then becomes READY. P3, physical recorder admission and experimental validation remain open.

## Preserved development failure and protocol amendment A1

The first B-03…B-06 development execution recorded 5 failures / 311 passes in 1.42 s. All five have one root cause: the decimal oblique boundary point (0.000225,0.0003,0), intended at r_min, has binary64 hypot 0.00037499999999999995, below binary64 r_min=0.000375. The specified strict exclusion correctly rejects it. This is an input-boundary representation conflict, not evidence to relax exclusion or numerical tolerance. Original fixture, complete log and JUnit are retained as `aura-ana05-fixture-original.json`, `aura-ana05-development-01.log/xml` in the eventual immutable report.

Before rerunning, amendment A1 moves only the positive oblique comparison and memory sample to twice that radius: (0.00045,0.0006,0). DIRECTIONS still has four observations; the oblique expected field is now compared to AXIAL row 2. The original oblique boundary input becomes an explicit rejection regression. The three required B-06 radial table points and -x/+y checks remain unchanged. Five configurations / 16 observations, equations, tolerances, resource limits and strict exclusion are unchanged. This documents the changed fixture and its geometric reason; the failed attempt remains evidence.

The amended B-03…B-06 development rerun passed 317 tests in 1.49 s; log/JUnit `aura-ana05-development-02.log/xml` are retained. An additional reference-sphere reparameterization and inclusive-box-face regression was then added before full Quality. Tolerance and exclusion behavior remain unchanged.

## Published-source outcome

Implementation `951af42b3c06b577590f493d55185079db468b1e` passed full local Quality (1,351 tests in 16.56 s) and [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37051894964) (1,351 in 21.05 s). Clean-source verification passed 63 checks in 0.24 s. Immutable report `VERIFY-ANA05-9bfc7d4be81e468e9c4b7ac407ae61d1` retains matching before/after source/environment observations, raw samples, all component errors, resource measurements, checksums and the failed/amended development history.

[The numerical report](../benchmarks/B06-spherical-verification.md) and [artifact review](../reviews/ANA-05-spherical.md) close ANA-05 and make ANA-06 READY. P3, physical recorder admission and experimental validation remain open. Closure has a separate full Quality/owner-commit/remote-CI delivery.
