# ANA-05 — Spherical Spreading Artifact Review

**Date:** 2026-10-02 · **Decision:** ANA-05 DONE; ANA-06 READY · **Role:** implementation self-review

## Acceptance and evidence

The [task record](../work-items/ANA-05.md) delivers the explicit immutable SphericalWave API, bounded outgoing field with full reactive velocity, source exclusion, input/resource/phase checks, independent B-06 references, mandatory literal comparisons, negative tests and a worked example. [SPHERICAL-WAVE-1.0](../research/spherical-wave-kernel.md) records primary source locators, convention conversion, derivation, geometry, numerical contract and near/far-field limitations.

At clean published source `951af42b3c06b577590f493d55185079db468b1e`, **63 checks passed in 0.24 s**. Five configurations / 16 observations satisfy the unchanged 2048e budget; maximum normalized discrepancy **2.759772071e-16** versus **4.547473509e-13**. Independent precision/backend checks, radial signs, normalization, distance ratios, transformation/reference invariances and mandatory rejection checks pass. Deliberately wrong spreading, reactive velocity, radial direction and flux rules fail as expected.

The first development attempt's five oblique-boundary failures are preserved. Documented amendment A1 moves the positive oblique sample away from the exclusion boundary and retains the original point as a strict rejection test. This was an explicit input correction after root-cause analysis; equations, tolerances, exclusion behavior and configuration count remain unchanged. [The B-06 report](../benchmarks/B06-spherical-verification.md) supplies failure history, per-observable maximum/RMS errors, resource observations and raw artifact hashes.

Full local Quality passed **1,351 tests in 16.56 s**; [exact remote Quality](https://github.com/Andioratech/AURA/actions/runs/37051894964) passed **1,351 in 21.05 s**. Source/environment observations match before/after the clean rerun. Resource observations fit the declared bounds. Dependencies and environment locks are unchanged. Owner Git identity and public staged files were checked; generated evidence and private instructions remain outside Git.

## Scientific boundary and handoff

ANA-05's numerical and artifact acceptance criteria are met. This self-review is not an external physical-model review or experimental validation. The incident field does not include a finite radiator, material loss, water calibration, source/body coupling, force, motion or gravity response. Initial particle work and the later larger-object/mass objective retain DEC-003/004 and independent model/evidence gates.

RUN-1.0 remains diagnostic-only. Spherical in-memory API availability does not admit a physical recorder driver or modify the Scenario source schema. Explicit source/sampling/index/gradient/provenance/checker/post-audit contracts remain required before ANA-07; retained JUnit and samples are not D07 RunManifests. P3 remains open.

**Next:** ANA-06 adds independent model-specific balances and distinguishes local field checks, integrated energy accounting and momentum/control-volume requirements. It must not turn the spherical power identity or a progressive-wave estimate into a universal force bound. ANA-07 then executes the admitted recorder campaign and reviews the full P3 gate. No owner decision is needed within this approved scope.

Closure documentation receives its own full local Quality, owner-identity/staged-diff checks, commit and exact remote CI confirmation before delivery.
