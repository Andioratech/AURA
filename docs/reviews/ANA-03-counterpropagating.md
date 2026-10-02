# ANA-03 — Counterpropagating-Wave Artifact Review

**Date:** 2026-10-02 · **Decision:** ANA-03 DONE; ANA-04 READY · **Role:** implementation self-review

## Delivered scope and checks

The [task record](../work-items/ANA-03.md) delivers the opposing-wave kernel, the frozen B-04 fixture and independent combined-identity oracle, node/phase/signed-flux checks, a Python example, export/render scripts and a reviewed diagnostic plot. [COUNTERPROPAGATING-1.0](../research/counterpropagating-kernel.md) defines the medium, geometry, amplitude/time convention and numerical admission. Both source plans are validated before field evaluation; vectors and gradients are retained through cancellation.

At published source `8b2b01a4ed14b9ca861bfedac3ececb65a93b3c7`, the clean rerun passed 60 focused tests across eight configurations / 157 observations. Maximum normalized discrepancy was 9.020562075e-16, below the unchanged 4.547473509e-13 threshold. Independent reference precision, elementary-function assumptions, literal tables, limiting/symmetry cases and deliberate errors passed. [The numerical report](../benchmarks/B04-counterpropagating-verification.md) provides all observable metrics, memory/encoding observations, artifact identities and retained development corrections.

Full local Quality passed 1,223 tests in 16.01 s; [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37044324608) passed 1,223 tests in 21.68 s. Core ENV-1.0 locks are unchanged. The optional Matplotlib renderer has a separate hashed lock and observed environment; it does not participate in the numerical oracle or solver. The report source/environment observations are stable. Owner Git identity was verified and private AI instructions remain untracked.

## Gate boundary and next task

ANA-03's bounded numerical acceptance is met. This implementation self-review closes the task, not P3, physical model validation or an externally reviewed scientific claim. Zero net flux in the ideal standing field does not imply zero force on an object; body interaction has not been calculated. Actual water properties, finite radiators/walls, losses, streaming, heating, particles, larger bodies and microgravity remain unvalidated.

RUN-1.0 remains diagnostic-only. Before ANA-07, physical driver admission must satisfy FIELD-1.0 input/index/gradient/provenance/checker and post-audit requirements. JUnit and the retained software report are not scientific run bundles. The P3 recorded campaign and later replay remain open.

**Next:** ANA-04 verifies two sources in different directions, vector interference, cancellation and allowed symmetries. It must freeze its own implementation record before extending the exact-opposite API. ANA-05 spreading and ANA-06 balance work retain their dependencies. No new owner choice is required for ANA-04 within the approved plan.

Closure documentation and the compact figure receive a separate full local workflow, owner-identity commit and exact remote CI check before delivery.
