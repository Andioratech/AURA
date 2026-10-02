# ANA-03 — Counterpropagating Waves

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Owner role:** research implementer

## Authority and boundary

Starting revision: `dabb12b7d07edbabd42a1e61faee727b54ed5d15`. ANA-02 is DONE; P2 is PASS. Apply D00, D02, D04–D09, FIELD-1.0, ANA-REF-1.0, EQ-006–009 and DEC-003/004. Implement and verify the ideal counterpropagating pair, including its diagnostic plot. This is a kernel verification card; RUN-1.0 remains diagnostic-only and P3 stays open. No body, force, motion, experimental validation or larger-object extrapolation is admitted.

## Frozen protocol before execution

- Follow [COUNTERPROPAGATING-1.0](../research/counterpropagating-kernel.md). Require two explicit PlaneWave specifications in the same ideal medium/frequency and exactly opposite directions. Validate both complete phase plans before any trig or field allocation. Sum pressure, vector velocity and gradient without amplitude averaging.
- Freeze eight B-04 configurations: EQUAL (129 points x=j*lambda/128, j=0..128); PHASE (negative wave phase pi/2, quarter-turn points); UNEQUAL (positive amplitude 4 Pa, negative 2 Pa, quarter turns); REVERSED (positive 2 Pa, negative 4 Pa, quarter turns); COMMON-PHASE (both pi/2, quarter turns); OBLIQUE (directions ±(0.6,0.8,0), quarter-turn x positions); ZERO (both zero, quarter turns); SINGLE (negative amplitude zero, quarter turns). All use the manufactured B-04 medium and observation box. Quarter turns are x/lambda=0,1/4,1/2,3/4. These eight configurations total 157 observations; no adaptive search.
- Independent Decimal oracle uses combined sine/cosine identities, not calls to the production superposition or field/unit helpers. Reuse only the independently implemented test series/constant primitives. Require 60/80-digit normalized agreement to 45 places and separate literal table anchors for equal, shifted and unequal cases.
- Keep ANA-REF-1.0's 2048e component tolerance and global nonzero amplitude scales; report maximum and RMS errors for all four observables. Check actual sine/cosine argument errors against the separate 4e limit. Detect wrong velocity sign, source averaging, missing gradient and a pressure-only flux shortcut.
- Test source order, translation, rotation/common phase, zero and single-source limits, input rejection and combined arithmetic overflow. Invalid second-source geometry/phase must fail before evaluating the first source.
- One CPU, no GPU/randomness, N<=256, two sources, incremental workspace `4096*N+8192` bytes; caller budget 2 MiB. Measure evaluation plus encoding, cap encoding at `32768+1024*N` bytes. B-04 focused tests <10 s, full suite <60 s. Preserve failures; after two same-cause failures record root cause before a third attempt.
- Keep core ENV-1.0 dependencies unchanged. A separate render-only environment may use pinned Matplotlib 3.10.8 (Python >=3.10, PSF license; [reviewed distribution](https://pypi.org/project/matplotlib/3.10.8/), [official documentation](https://matplotlib.org/3.10.8/)). Record resolved transitive packages, interpreter, installation artifacts and hashes. It reads exported numeric data and never supplies the numerical oracle.
- Retain generated raw reports/data locally with immutable ID/checksums. Explicit D05 publication exception: one reviewed diagnostic PNG <=500 KiB may be committed under docs/figures as the card's required compact illustration. Publish its source/fixture/data hashes and reproducible export/render scripts; raw arrays and environment observations remain ignored.
- Complete the full local workflow before every commit, inspect effective owner author/committer and staged diff, push and confirm exact remote CI. Then rerun from clean published source, capture source/environment before and after, and close with a separate evidence commit.

## Acceptance and handoff

Equal opposing waves must retain nonzero pressure/velocity with zero period-mean net flux. Phase-shifted and unequal inputs must satisfy the independent complex fields and signed flux, including pressure nodes with nonzero fluid velocity. Report these as numerical verification, not measurements. Close only with the executed B-04 report, plot and CI evidence. ANA-04 then becomes READY; physical driver admission, balances and ANA-07 remain pending.

## Development record

The first lint pass reported one unnecessary dict constructor (C408); it was changed to a literal without affecting equations. The first combined B-03/B-04 development numerical suite passed 189 tests in 0.82 s and is retained at `/tmp/aura-ana03-development-01.xml` and its companion log. No scientific acceptance threshold was adjusted. The first diagnostic render exposed an overlapping legend/footer; spacing was corrected before publication. Publication results follow in the closure report.

The diagnostic uses `scripts/export_standing_wave.py` in ENV-1.0 and `scripts/plot_standing_wave.py` in the isolated rendering environment. Both refuse to overwrite output. The export labels dirty-source development data explicitly. The plot displays the original frozen samples; unequal/shifted cases have four points and are not additional dense-grid numerical verifications.

The first full local workflow stopped at lint: the later export test had unsorted imports and omitted explicit subprocess check flags (I001/PLW1510). Its log is retained at `/tmp/aura-ana03-local-ci-01-failed.log`; no tests ran in that workflow. Imports were sorted and subprocess calls now state `check=False` because their return codes are asserted, including the expected overwrite rejection. The earlier C408 was a different lint cause. No numerical failure or threshold change occurred.

## Published-source outcome

Implementation `8b2b01a4ed14b9ca861bfedac3ececb65a93b3c7` passed full local Quality (1,223 tests, 16.01 s) and [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37044324608) (1,223 tests, 21.68 s). Clean-source verification passed 60 B-04 tests in 0.71 s. The retained report is `VERIFY-ANA03-85f7169fa9d84e9397e56d69d9e28e38`; source/environment observations before and after agreed.

[The numerical report](../benchmarks/B04-counterpropagating-verification.md) records every observable's maximum/RMS error, signed flux outcomes, resource usage, retained failures and artifact hashes. The required diagnostic figure is published under the frozen size exception; raw arrays/logs/environment observations remain ignored. [The artifact review](../reviews/ANA-03-counterpropagating.md) closes ANA-03 and opens ANA-04. P3 and physical validation remain open. Closure receives its own full CI and exact remote confirmation.
