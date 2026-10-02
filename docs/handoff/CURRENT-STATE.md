# Current Research Checkpoint

**As of:** 2026-10-02 · **Last development delivery:** `1d6efb0b17fa95a95b36d8d1d769e8896981688f` · **Main next task:** ANA-07

This checkpoint includes the ANA-07 plane and spherical recorders, full frozen matrix and a fresh spherical-case replay. Later documentation commits may contain this handoff itself. Reconcile it with actual history and the [live work board](../planning/10-work-board.md); do not treat this snapshot as an instruction to revert newer work.

## Objective and present boundary

Investigate whether controlled acoustic forcing can produce prescribed acceleration in a declared object/domain, toward microgravity applications. Small particles in water are the starting implementation campaign. Greater masses, larger objects and other geometries are explicit subsequent research objectives with their own model/evidence gates. Acoustic forcing does not create gravity. The hypothesis and feasibility remain unvalidated.

**P2 is PASS for foundations. P3 remains open.** The current code provides bounded ideal incident-field calculations and records plane and outgoing spherical fields, not a validated complete simulator. Its clean-source B-03/B-04/B-05/B-06 matrix passed all 32 configurations and 264 samples against independent frozen numerical criteria; fresh B03-AXIAL and B06-AXIAL reproductions matched their exact inputs, fields and metrics. This remains mathematical software verification in ideal lossless models. No force, object motion, controller, calibrated finite transducer, coupled wall/body field, physical attenuation model or demonstrated microgravity performance has been delivered. See the [matrix report](../benchmarks/ANA-07-recorded-field-matrix.md) and [artifact review](../reviews/ANA-07-matrix-artifact-review.md).

## Delivered work and where to inspect it

| Work | Delivered capability | Evidence entry |
|---|---|---|
| FND-01…FND-03 | SI/coordinate/phasor conventions, versioned input schemas, safe arithmetic and conversions | [FND-01](../work-items/FND-01.md), [FND-02](../work-items/FND-02.md), [FND-03](../work-items/FND-03.md) |
| FND-04…FND-07 | L0 checks, independent foundation verification, validation CLI and content identity | [FND-04](../work-items/FND-04.md), [FND-05](../work-items/FND-05.md), [FND-06](../work-items/FND-06.md), [FND-07](../work-items/FND-07.md) |
| FND-08 | Locked ENV-1.0 and P2 exit | [P2 PASS review](../reviews/P2-foundation-exit.md) |
| RUN-01 | Immutable diagnostic execution, failure retention, source/environment binding, `aura run/check` | [RUN-01 review](../reviews/RUN-01-lifecycle.md) |
| ANA-01 | FIELD-1.0 container and frozen B-03…B-06 references | [ANA-01 review](../reviews/ANA-01-field-contract.md) |
| ANA-02 | Single progressive plane-wave pressure, fluid velocity, gradient and flux | [B-03 report](../benchmarks/B03-plane-wave-verification.md) |
| ANA-03 | Opposing-wave pair, standing-field nodes and signed flux | [B-04 report](../benchmarks/B04-counterpropagating-verification.md) |
| ANA-04 | Two coherent plane waves, noncollinear interference and vector symmetries | [B-05 report](../benchmarks/B05-interference-verification.md) |
| ANA-05 | Outgoing spherical field with full reactive velocity and explicit source exclusion | [B-06 report](../benchmarks/B06-spherical-verification.md), [review](../reviews/ANA-05-spherical.md) |
| ANA-06 | Fixed-domain closed-sphere and spherical-shell energy ledgers | [ANA-06 report](../benchmarks/ANA-06-energy-balance-verification.md), [review](../reviews/ANA-06-energy-balance.md) |
| ANA-07 | Versioned plane/spherical recorder, 32 passing B-03…B-06 comparisons, two passing fresh reproductions, artifact and sensitivity reviews complete; independent P3 gate review remains | [ANA-07 task](../work-items/ANA-07.md) |

Fifteen board tasks are DONE. ANA-07 is ACTIVE; LIT-01 and SC-01 are READY. LIT/SC are separate evidence/scale tracks, not permission to skip P3. Other BLOCKED cards mostly await ordinary predecessors; the project is not globally blocked.

## Exact latest evidence

- **Current ANA-07 result:** [32-case matrix report](../benchmarks/ANA-07-recorded-field-matrix.md) and [artifact review](../reviews/ANA-07-matrix-artifact-review.md). Commit `260c73064dec57093339c033b3f0ad5273204c28`; exact Quality run [37066889054](https://github.com/Andioratech/AURA/actions/runs/37066889054) passed with 1,385 tests. All 32 configurations and 264 points passed; index SHA-256 `d6352e8c929d22066c40dc55765f7334804a2d54d2ef10bb04fbc4c4166729d3`.
- Fresh B06-AXIAL replay: local ignored report `results/verification/ANA-07/REPRO-B06-AXIAL-1d6efb0/reproduction.json`, SHA-256 `7cb53754a80cc6804af60085f9ed960250338ffdbaa1e80a701907bd1a2e6618`; all three inputs, four field artifacts and numerical metrics match. Replay-tool scope wording commit `1d6efb0b17fa95a95b36d8d1d769e8896981688f`; exact [Quality run 37067239654](https://github.com/Andioratech/AURA/actions/runs/37067239654) passed. No physical validation is established.
- Precision/cancellation review: the existing independent 60/80-digit and actual-argument math checks passed in Quality; an exploratory one-ULP probe on either side of the B04-EQUAL pressure node matched the Decimal reference within `9.1e-17` normalized error. Record SHA-256 `8f162f80184eb5828f8b746b6bb1f081bc0f828a95a8b6eee23ad471209ec426`; the review explains limits and why no plot was needed. The sole remaining ANA-07 step is the formal P3 review by an independent reviewer, currently unassigned.

- Implementation: [`951af42b3c06b577590f493d55185079db468b1e`](https://github.com/Andioratech/AURA/commit/951af42b3c06b577590f493d55185079db468b1e), [Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37051894964): 1,351 tests in 21.05 s; full local Quality 1,351 in 16.56 s.
- Closure: [`a60c5417576299f9714cbc19860e05af967576b2`](https://github.com/Andioratech/AURA/commit/a60c5417576299f9714cbc19860e05af967576b2), [Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37052282601): 1,351 in 21.51 s; full local Quality 1,351 in 16.37 s.
- Clean-source B-06 verification: 63 tests in 0.24 s; five configurations / 16 observations; maximum normalized error 2.759772071e-16 against unchanged 2048e = 4.547473509e-13.
- Immutable verification ID: `VERIFY-ANA05-9bfc7d4be81e468e9c4b7ac407ae61d1`. Local relative path: `results/verification/ANA-05/VERIFY-ANA05-9bfc7d4be81e468e9c4b7ac407ae61d1/` (ignored). Index SHA-256: `ddba4208d0f3054d7750f97695c6d062ae4311552ee03b5abf1189d5dda04b9e`.
- The report contains source/environment observations, locks, inputs, raw samples, per-component errors, logs and artifact hashes. It is **software verification**, not a D07 RunManifest or experimental data. Source/environment observations matched before and after. Local operations/transfer-pack records locate raw evidence unavailable from a plain clone.
- ANA-06 implementation: [`260464a9e7975b4380cc223546a5b26304e6d303`](https://github.com/Andioratech/AURA/commit/260464a9e7975b4380cc223546a5b26304e6d303), [exact Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37055310149): environment/lock checks, Ruff and 1,366 tests in 21.50 s; full local Quality passed Ruff and 1,366 in 17.70 s.
- ANA-06 checks three six-point antipodal plane-wave spheres and one two-boundary B-06 spherical shell. Clean-source focused verification passed 143 tests in 1.74 s; all four example ledgers PASS, with shell normalized residual 1.7141911890312011e-16 against 1.8189894035458565e-12. Immutable verification: `VERIFY-ANA06-6e3c0547cb364aef9d67e6518cc32b93`, ignored path `results/verification/ANA-06/VERIFY-ANA06-6e3c0547cb364aef9d67e6518cc32b93/`, index SHA-256 `beda8b9aca3d19525d10d3275ae91838dbe07f8c5f9c2a219a87a1bb670668f9`.
- ANA-07 published plane recorder: [`4d35bf4698db26adef2b80dd455d8b2d88c6194e`](https://github.com/Andioratech/AURA/commit/4d35bf4698db26adef2b80dd455d8b2d88c6194e), [exact Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37059818785); scope correction: [`0fa1114100a218b5dd36afb159285c02b318d838`](https://github.com/Andioratech/AURA/commit/0fa1114100a218b5dd36afb159285c02b318d838), [exact Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37060410743), 1,373 tests.
- Clean-source smoke bundle: `RUN-20261002-b1e2f315f5b94c099f8fc56c5ed1596e`, manifest SHA-256 `edc3a71b1149cbf4cad5f18a4bd517921a9bec8518b3a79aafde9f2c61be637f`, integrity `VERIFIED`, execution `completed`, verdict `INDETERMINATE`.
- Historical first comparison: B03-01 at the origin had zero normalized error for its exact reference values; its report remains in the ignored `results/verification/ANA-07/ANA07-METRICS-B03-01-0fa1114.json`. The historical 27-configuration result below is superseded by the current 32-configuration evidence at the top of this section.
- Generalized metrics and the matrix runner: [`17d2ad30250a675aa881f3c9bcfe631de6d2c687`](https://github.com/Andioratech/AURA/commit/17d2ad30250a675aa881f3c9bcfe631de6d2c687), [exact Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37062947897): full local Quality passed Ruff and 1,378 tests; remote Quality passed.
- Historical first clean-source B-03/B-04/B-05 matrix: 27 frozen configurations and 248 samples. Execution, output integrity and every numeric criterion passed. Maximum normalized errors: pressure `9.0206e-16`, velocity `7.9409e-16`, gradient `7.5994e-16`, mean intensity `1.5882e-16`; fixed tolerance `4.5475e-13`. Maximum runtime 3.745 s, largest bundle 111,490 bytes, highest RAM preflight estimate 1,008,906,240 bytes. The ignored index is `results/verification/ANA-07/PLANE-MATRIX-ANA-REF-1.0-17d2ad3/index.json`, SHA-256 `bae0d88a21a5eaf6c0fcd4c2795a9626a3516ed0ee620ae653de7476c416d748`. This historical result was superseded by the B-06-inclusive matrix above.
- Fresh reproduction utility: `tools/reproduce_ana07_case.py`. B03-AXIAL replay run `RUN-20261002-0b24dbe1337a458e858d847675c189d8` exactly matched its original inputs, four field artifacts and frozen metrics. The report is in ignored local results at `results/verification/ANA-07/REPRO-B03-AXIAL-4e24c75/reproduction.json`, SHA-256 `b457a09e11174d08971829d95ca7c94e6d02c37ff754964e4dcbea7b127c8018`. This checks deterministic analytic software only; physical validation remains unestablished.

These are historical observed results. Rerun the required checks for new work; never quote this count as a fresh test result.

## Failed attempt that must remain visible

ANA-05's first development attempt had five failures caused by the decimal oblique point (0.000225,0.0003,0) rounding just inside the minimum radius. Strict exclusion correctly rejected it. Documented amendment A1 moved the positive oblique comparison to twice the radius and retained the original point as a rejection regression. Equations, tolerances, exclusion behavior and matrix count were unchanged. Original fixture and failed log/JUnit are preserved. Those development attempts lack an exact captured dirty-source snapshot; the separate clean published-source report has exact provenance. See [ANA-05](../work-items/ANA-05.md).

## Decisions that must survive a handoff

| Decision | Meaning for continuing work |
|---|---|
| [DEC-001](../decisions/DEC-001-p0-baseline-approval.md) | Owner approved the development baseline and PLAN-01; approval is not physical validation. G01–G05 remain DRAFT. |
| [DEC-002](../decisions/DEC-002-initial-measurable-force-benchmark.md) | Published 50 mm sphere in air is a bounded, separately identified measurable reference. Measurement uncertainty remains incomplete. It is not the small-particle water domain. |
| [DEC-003](../decisions/DEC-003-nonblocking-foundation-work.md) | Missing measurements do not block independent foundations or analytical verification. Dependent experimental claims remain INDETERMINATE. |
| [DEC-004](../decisions/DEC-004-staged-mass-and-size-expansion.md) | Preserve the larger-mass/object objective. Every new regime requires an appropriate model and independent evidence; do not extrapolate a small-particle formula. |

The owner requests incremental commits, complete CI before each commit, exact remote CI after push, and plain-Spanish explanations at results/decisions/route changes. The requested explanation before entering the simulation core was already delivered at P2 exit; it is not an unfulfilled approval gate. The owner also requested an English local progress dashboard with Andiora branding, outside Git. Machine-specific details remain in the private operations note.

## Contracts and implementation landmarks

- [FIELD-1.0](../research/analytical-field-contract.md): peak phasors, exp(-i omega t), pressure, full fluid velocity and pressure gradient; immutable samples and explicit component artifacts.
- [ANA-REF-1.0](../benchmarks/B03-B06-analytical-protocols.md): independently derived expectations and frozen error scales. The five B-06 configurations complete the planned 11+8+8+5=32 analytical configurations; do not quietly expand it into a sweep.
- [Plane-wave](../research/plane-wave-kernel.md), [opposing-pair](../research/counterpropagating-kernel.md), [two-wave](../research/two-wave-kernel.md), [spherical](../research/spherical-wave-kernel.md) contracts declare geometry, losses, phase/resource limits and unsupported regimes.
- `src/aura/fields/analytic.py` exposes PlaneWave/SphericalWave and single/pair/spherical evaluators; `types.py` validates representation. Independent Decimal references for B-03/B-04/B-05 live in `src/aura/analysis/references.py`; the tests retain compatibility imports.
- `src/aura/runs/execute.py` and `check.py` admit software diagnostics and ideal plane-field recordings. They do not establish physical results. Explicit spherical recorder inputs and model post-audits remain pending.
- [Equation register](../registers/equations.md), [requirement traceability](../planning/09-requirement-traceability.md), [environment](../../requirements/README.md) and [CLI guide](../cli-usage.md) identify existing versus planned capabilities.

## Unresolved gates

ANA-07 still needs B-06 recorder implementation and five frozen recorded cases, remaining post-audits, plotted-data review and gate review before P3 can close. The versioned source binding is specified but not yet admitted by code. One fresh plane-case reproduction has passed; general RUN-02 replay remains pending. Numerical backend work, coupled forces, motion, control, adversarial studies and scale progression retain their planned dependencies. Water measurement selection/uncertainty, physical source calibration, boundary/loss effects, suitable larger-body models and independent scientific review remain evidence work. Never fill a missing physical parameter or term with an invented value or a zero. ANA-06's PASS is an energy-accounting comparison for four fixed ideal source cases; it supplies no momentum balance, body force or physical validation and its control-surface samples are not the ANA-07 run artifacts.
