# Current Research Checkpoint

**As of:** 2026-10-02 · **Last development delivery:** `a60c5417576299f9714cbc19860e05af967576b2` · **Main next task:** ANA-06

This checkpoint was written after ANA-05 and before ANA-06. Later documentation commits may contain this handoff itself. Reconcile it with actual history and the [live work board](../planning/10-work-board.md); do not treat this snapshot as an instruction to revert newer work.

## Objective and present boundary

Investigate whether controlled acoustic forcing can produce prescribed acceleration in a declared object/domain, toward microgravity applications. Small particles in water are the starting implementation campaign. Greater masses, larger objects and other geometries are explicit subsequent research objectives with their own model/evidence gates. Acoustic forcing does not create gravity. The hypothesis and feasibility remain unvalidated.

**P2 is PASS for foundations. P3 remains open.** The current code provides bounded ideal incident-field calculations, not a validated complete simulator. No force, object motion, controller, calibrated finite transducer, coupled wall/body field, physical attenuation model or demonstrated microgravity performance has been delivered.

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

Fourteen board tasks are DONE. ANA-06, LIT-01 and SC-01 are READY; ANA-06 is the selected continuation of the main implementation sequence. LIT/SC are separate evidence/scale tracks, not permission to skip P3. Other BLOCKED cards mostly await ordinary predecessors; the project is not globally blocked.

## Exact latest evidence

- Implementation: [`951af42b3c06b577590f493d55185079db468b1e`](https://github.com/Andioratech/AURA/commit/951af42b3c06b577590f493d55185079db468b1e), [Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37051894964): 1,351 tests in 21.05 s; full local Quality 1,351 in 16.56 s.
- Closure: [`a60c5417576299f9714cbc19860e05af967576b2`](https://github.com/Andioratech/AURA/commit/a60c5417576299f9714cbc19860e05af967576b2), [Quality PASS](https://github.com/Andioratech/AURA/actions/runs/37052282601): 1,351 in 21.51 s; full local Quality 1,351 in 16.37 s.
- Clean-source B-06 verification: 63 tests in 0.24 s; five configurations / 16 observations; maximum normalized error 2.759772071e-16 against unchanged 2048e = 4.547473509e-13.
- Immutable verification ID: `VERIFY-ANA05-9bfc7d4be81e468e9c4b7ac407ae61d1`. Local relative path: `results/verification/ANA-05/VERIFY-ANA05-9bfc7d4be81e468e9c4b7ac407ae61d1/` (ignored). Index SHA-256: `ddba4208d0f3054d7750f97695c6d062ae4311552ee03b5abf1189d5dda04b9e`.
- The report contains source/environment observations, locks, inputs, raw samples, per-component errors, logs and artifact hashes. It is **software verification**, not a D07 RunManifest or experimental data. Source/environment observations matched before and after. Local operations/transfer-pack records locate raw evidence unavailable from a plain clone.

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
- `src/aura/fields/analytic.py` exposes PlaneWave/SphericalWave and single/pair/spherical evaluators; `types.py` validates representation. `tests/*_reference.py` implements test-only independent calculations. Read their source before modifying them.
- `src/aura/runs/execute.py` and `check.py` admit software diagnostics only. Acoustic Python APIs are **not** available as physical `aura run` drivers. FIELD-INDEX-1.0, explicit spherical recorder inputs, checker/post-audit/provenance integration remain pending.
- [Equation register](../registers/equations.md), [requirement traceability](../planning/09-requirement-traceability.md), [environment](../../requirements/README.md) and [CLI guide](../cli-usage.md) identify existing versus planned capabilities.

## Unresolved gates

ANA-06 balances and ANA-07's recorded analytical campaign precede the P3 review. Numerical backend work, coupled forces, motion, control, adversarial studies and scale progression retain their planned dependencies. RUN-02 replay is still pending. Water measurement selection/uncertainty, physical source calibration, boundary/loss effects, suitable larger-body models and independent scientific review remain evidence work. Never fill a missing physical parameter or term with an invented value or a zero.
