# ANA-04 — Two-Source Interference and Symmetries

**State:** ACTIVE · **Protocol frozen:** 2026-10-02 · **Owner role:** research implementer

## Authority, question and scope

Starting revision: `2dca7a9777af5aef0e532c22d1cb1e5c079d08dc`. ANA-03 is DONE; P2 is PASS. Apply D00, D02, D04–D09, FIELD-1.0, ANA-REF-1.0, EQ-006–009 and DEC-003/004. Does a bounded pair of coherent plane waves reproduce constructive/destructive fields and vector flux under allowed coordinate/source transformations?

Implement only the ANA-04 kernel, B-05 examples, independent calculations and regression checks. No physical recorder driver, spreading, body coupling, force, trajectory, control or experimental comparison is admitted. RUN-1.0 remains diagnostic-only; P3 remains open. Particles in water are the starting campaign; larger-object/mass and microgravity research retains its separate evidence gates.

## Frozen protocol before execution

- Follow [TWO-PLANE-WAVES-1.0](../research/two-wave-kernel.md). Add an explicit two-wave API accepting separately specified unit directions in one homogeneous ideal medium at one frequency. Reuse the bounded preparation/summation code. Preserve the existing exact-opposite API's restriction. Validate both full phase plans before trig/field evaluation. Never average source amplitudes or add scalar speed magnitudes.
- Eight B-05 configurations, four observations each: AXIAL (frozen B-05 table); ROTATED (proper permutation x,y,z -> y,z,x of both sources and samples); COMMON-PHASE (both phases pi/2); TRANSLATED (both references and samples shifted by (lambda/8,lambda/8,0)); OBLIQUE (directions (0.6,0.8,0) and (0,0.6,0.8), original samples); UNEQUAL-PHASE (first amplitude 4 Pa / phase pi/2, second amplitude 2 Pa / phase -pi/4); ZERO (both amplitudes zero); SINGLE (second amplitude zero). Base amplitudes 2 Pa, rho=1000 kg/m³, c=1500 m/s, f=1 MHz, zero losses, origin references and zero phases unless modified. The cube observation box is [-lambda,lambda]^3, lambda=0.0015 m. These eight configurations total 32 observations; no sweep.
- Independent Decimal reference expands two real sinusoids, differentiates them, obtains velocity through linear Euler and evaluates flux by the independent cosine phase-difference identity. No production field/unit/binary-trig calls. Require 60/80-digit agreement to 45 normalized decimal places. Independently check every literal B-05 table component in both oracle and production.
- Retain 2048e tolerance (e=2^-52), scales C, C/Z, k*C, C²/(2Z), C=sum amplitudes with 2 Pa fallback for zero drive. Report per-component errors and maxima/RMS. Check each actual binary64 sine/cosine argument against the separate 4e assumption. No local division by a vanishing node value.
- Test order, proper rotations, translation, common phase, distinct reference reparameterization, near-node rounding neighbors and the single/zero/parallel/opposite limits. Deliberate wrong pressure averaging, scalar-speed addition, canceled velocity/gradient, omitted interference flux and partial geometry rotation must fail the frozen comparisons.
- Test invalid source type, medium/frequency mismatch, geometry, nonfinite values, unsupported loss, resource bounds and excessive phase conditioning, including an invalid second source with zero drive. Reject before either evaluation. Preserve typed combined-overflow failures.
- One CPU, no GPU/randomness; N<=256, two sources, integer workspace >=4096*N+8192 bytes, 2 MiB caller budget. Measure N=256 evaluation/serialization and enforce encoded bytes<=32768+1024*N. Focused tests <10 s, full suite <60 s, clean-source rerun timeout 30 s. Preserve failures; after two of the same cause write root cause before retrying.
- No dependency change. Full local Quality before every commit, owner author/committer and staged-diff/private-file inspection, exact remote CI after push. Verify from clean published source with before/after source/environment observations and immutable report ID/checksums. JUnit is software verification, not a D07 RunManifest.

## Artifacts, acceptance and handoff

`fields/analytic.py`; `tests/fixtures/fields/B05-interference.json`; independent oracle/tests; kernel derivation/example and B-05 maximum/RMS report. Update equation and requirement traceability. Close only when the independent fields, node behavior, signed vector flux and required symmetry/negative tests actually pass, with unchanged tolerances and published CI evidence. ANA-05 then becomes READY; P3 and physical model validation remain open.

## Development verification

The first focused B-03/B-04/B-05 regression execution passed 255 tests in 1.31 s. Its actual log and JUnit are retained at `/tmp/aura-ana04-development-01.log` and `/tmp/aura-ana04-development-01.xml`. This is a dirty-tree software check, not the published-source verification report. All first-pass lint and functional checks passed; no equation, fixture or acceptance tolerance was adjusted to obtain a pass. The final full Quality workflow and clean published-source report follow before closure.
