# ANA-04 — Two-Wave Interference Artifact Review

**Date:** 2026-10-02 · **Decision:** ANA-04 DONE; ANA-05 READY · **Role:** implementation self-review

## Delivered artifacts and acceptance

The [task record](../work-items/ANA-04.md) delivers a bounded two-wave API, B-05 input fixtures, independent real-sinusoid/Euler/cosine-difference calculations, literal reference checks, coordinate/phase/source-order regressions, typed rejections and a worked Python example. [TWO-PLANE-WAVES-1.0](../research/two-wave-kernel.md) freezes the model, derivation, explicit source references, phase convention, sampling geometry, numerical limits and remaining physical exclusions. The exact-opposite API preserves its previous restriction while sharing the same pair evaluation.

At published revision `6bd45bdec28f37f6e00512664ff9510f68e6f818`, 65 focused B-05 tests passed from clean source. Eight configurations / 32 observations meet the unchanged 2048e component budget; the largest normalized discrepancy is 3.140184917e-16 versus the 4.547473509e-13 limit. Precision/backend assumptions, every literal B-05 table component, allowed transformations and limiting cases pass. Pressure cancellation retains nonzero fluid velocity and gradient. Deliberately wrong scalar-speed, source-amplitude, node-vector, rotation and independent-flux shortcuts fail as required. [The numerical report](../benchmarks/B05-interference-verification.md) records all observable metrics, actual artifacts, hashes, memory observations and development history.

Full local Quality passed 1,288 tests in 16.30 s; [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37046825752) passed 1,288 tests in 13.99 s. The published-source rerun passed 65 checks in 0.32 s. Source/environment observations agree before and after. No dependencies, environment locks or acceptance tolerances changed. Owner Git identity was checked; private instructions and generated evidence remain outside Git.

## Review boundary and next task

ANA-04's implementation/numerical criteria are met. This self-review does not close P3, substitute for independent physical review or support a D09 feasibility claim. The models are ideal incident fields; force on an object, source calibration, real boundaries/losses, heating, streaming, particles, larger bodies and microgravity remain unvalidated. Zero pressure or zero mean flux does not mean zero force or absent field energy.

RUN-1.0 remains diagnostic-only. Physical kernel availability does not admit an acoustic driver to the recorder; FIELD-1.0 input/index/provenance/gradient/checker/post-audit requirements must be met before ANA-07. The retained JUnit and sampled fields are software verification artifacts, not scientific run bundles. The recorded P3 matrix and replay remain open.

**Next:** ANA-05 implements only the planned ideal outgoing spherical spreading reference, with explicit excluded source region and the full pressure/velocity relation. It must verify the frozen B-06 distance/phase/near-field terms before any physical source interpretation. ANA-06 balances and ANA-07 remain downstream gates. No new owner decision is required within this approved scope.

Closure documentation receives a separate full local workflow, staged-diff/identity review, owner commit and exact remote CI confirmation before delivery.
