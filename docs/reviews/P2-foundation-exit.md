# P2 Gate Review — Verified Software Foundations

## Review identity

**Gate:** P2 / FND-08 · **Date:** 2026-10-02 · **Decision:** PASS within the foundation scope below.

**Source reviewed:** `ff09fb182f191ed35bc7b92f6d0076ed28585cb4`, including FND-01…FND-08 artifacts. **Authority:** D00 v1.3, PLAN-01 v1.3, D02/D03/D05–D08, DEC-001/003/004. **Preparer/reviewer role:** implementation assistant performing artifact self-review against the frozen task protocols; no qualified independent scientific reviewer or new owner approval is represented by this record. Git author/committer identity is the configured repository owner; commit attribution is not scientific review attribution.

Domain: schema 1.0, CONV-1.0, L0-1.0, CLI-1.0, AURA-C14N-1/AURA-IDENTITY-1 and ENV-1.0 on CPython 3.12.14/Linux x86_64. Inputs are manufactured fixtures and known arithmetic/byte answers. No acoustic field, force, motion or control simulation, measured dataset, physical time interval or experimental result is reviewed here.

## Evidence against mandatory exit criteria

| Criterion | Artifact / observation | Threshold and derivation | Limit | Outcome |
|---|---|---|---|---|
| Unambiguous SI/frame/amplitude conventions | [FND-01](../work-items/FND-01.md), [CONV-1.0](../research/si-and-conventions.md), equation/reference tables | Explicit representation; no inferred physical quantities | Physical truth of user labels requires provenance | Met |
| Complete versioned input/evidence contracts | [FND-02](../work-items/FND-02.md), [schema contract](../research/schema-contract.md), strict JSON/YAML and immutable snapshots | Supported fields/types/units explicit; required missing fields reject | Geometry representation is not solver applicability or full clearance/material validation | Met |
| Dimensional calculations reproduce independent references | [FND-03](../work-items/FND-03.md), [B-01 report](../benchmarks/B01-B02-foundation-verification.md) | Frozen B01-v1.0 ordinary values: relative 1e-12 / absolute 1e-15; separately defined extreme/subnormal rules | Scalar arithmetic; no new force/power bound | Met |
| Known invalid cases reject with specific diagnostics before compute | [FND-05](../work-items/FND-05.md): 22 fault classes × JSON/YAML, serialization faults, zero downstream hook calls; [FND-06](../work-items/FND-06.md) CLI outcomes | Exact error codes/paths; zero allocation/solver hook calls; no silent defaults | Hooks are test-only; RUN-01 must repeat ordering on the real lifecycle | Met for the P2 input boundary |
| R-001…R-010 are reviewable and preserve adverse/unknown findings | [FND-04](../work-items/FND-04.md), [L0 rule register](../registers/mclf-l0-rules.md), severity/spoofing tests | Stable predicates, assumptions, tolerance sources and aggregate decision | Real model coverage and external evidence are still absent | Met |
| Valid examples serialize deterministically and changes are detected | [FND-07](../work-items/FND-07.md), [B-02 identity report](../benchmarks/B02-content-identity.md), golden bytes/independent digests | Exact byte/hash agreement; reordered keys agree; changed scientific content and altered files reject | Conservative identity is not proof of physical equivalence or publisher authenticity | Met |
| Fresh reproducible development profile and visible CLI failures | [FND-08](../work-items/FND-08.md), [ENV-1.0](../../requirements/README.md), checker tests | Exact 16 package versions/artifact digests, CPython 3.12.14; `pip check`; CLI 0/3/1/4; deliberate bad hash rejected | Seven-package core path also checked; bootstrap/host image are external prerequisites | Met |
| Complete local/remote CI and documentation review | [Exact source CI](https://github.com/Andioratech/AURA/actions/runs/37030255717), workflow, traceability and relative file links | All workflow steps pass; 784 tests, zero lint failures; links resolve | CI is software verification, not experimental acceptance | Met |

No numeric tolerance, baseline claim, physical hypothesis or missing-data rule changed to obtain this decision. The later production runner cannot inherit a claim that its gate ordering has already been tested.

## Separate statuses

- **Software:** PASS. Local complete workflow passed with **784 tests** (about 12.4 s); GitHub's exact source revision passed **784 tests in 16.44 s**, installation, dependency/profile verification, Ruff and required-document checks. The environment adds 23 checks to FND-07's 761. Local glibc 2.43 / Clang 22.1.3 and remote glibc 2.39 / GCC 13.3.0 both satisfy ENV-1.0; this is not a bit-identical host reproduction. The documentation closure commit must also pass full local and exact remote CI; its identifier is reported on delivery.
- **MCLF:** the real manufactured scenario remains **INDETERMINATE**, including MODEL_UNCOVERED and unverified evidence. No configuration has become scientifically ACCEPTED through this review. Synthetic test verdicts remain explicitly synthetic. Higher audit levels are unimplemented.
- **Numerical verification:** B-01 scalar and B-02 structural/identity comparisons PASS within their fixed contracts. No field solver or mesh/time convergence result exists; those gates remain ahead.
- **Experimental validation:** unresolved / INDETERMINATE where measurement uncertainty and domain evidence are missing. DEC-003 permits independent work; it does not establish measured agreement.
- **Reproduction:** fresh development and core-only installations and exact dependency artifacts are verified. Source/environment binding to immutable scientific runs, retention, replay and evidence export remain RUN-01/RUN-02. No experiment/run IDs were invented for software checks.
- **D03:** FR-001 has foundation evidence; FR-002/009/010 remain PARTIAL at the simulator integration boundary. FR-012 has a tested CPU development profile, without numerical backend equivalence. Field, force/torque, translation/rotation, targets/control, resource estimates, comparison and release bundles remain at their owning cards. See [current mapping](../planning/09-requirement-traceability.md); this is not a complete D03 release.
- **D09:** no hypothesis status is promoted; no gravity generation, achievable acceleration, hardware performance or microgravity result is established. Larger masses/bodies and other geometries remain explicit DEC-004 research objectives requiring justified models and independent evidence.

## Decision and permitted next work

**P2 PASS; FND-08 DONE. RUN-01 is READY. ANA-01 remains BLOCKED until RUN-01 is delivered.** This satisfies PLAN-01's P2 gate for known-invalid rejection, independent scalar answers, no silent defaults and deterministic valid serialization, plus the detailed plan's environment review. It does not waive later production integration, physical coverage, convergence or independent review.

Before RUN-01 implementation, explain the system/core to the owner as requested. The next delivery should build the immutable execution recorder: preserve inputs, actual code/environment identity, outcomes and errors; refuse output reuse; verify deliberately failed executions remain inspectable. Its exact execution policy must be frozen before implementation, including how exploratory analytical work can proceed under DEC-003 without relabeling an INDETERMINATE scientific verdict as ACCEPTED.

After that gate, ANA-01 fixes field outputs, assumptions and independently known cases; ANA-02…07 implement and verify simple wave fields. Force, motion and feedback follow their own gates. Greater object scales require separate applicability/evidence review, as in [scale progression](../planning/11-scale-progression.md). Independent scientific review remains unassigned for the later gates requiring it; no one is designated or impersonated here.

## Preservation and review triggers

All earlier failures remain in FND-01…08; this task preserves notice-inspection, editable-metadata, import-order and YAML-syntax failures plus the intentional hash rejection. The negative input fixtures remain in Git. Large/downloaded/generated artifacts and private assistant instructions remain outside Git.

| Environment input | SHA-256 |
|---|---|
| `core-linux-py312.lock` | `91d895b3097095874dc6b4848bce415983408c9daf123e1d7206e03ecf49af17` |
| `dev-linux-py312.lock` | `9e612df1f995778ad8f12e0980db5d760f26d8b3f284e38278f1055a19c7ae40` |
| `environment-linux-py312.json` | `4387feff712e60296c646f04217efc205e4e8b8c23412f9fed6e2b10836deb4e` |

Reopen affected criteria after contract/lock changes, new rejected-case regressions or unexplained local/remote disagreement. Use F-01/F-09/F-10/F-11 as applicable; retain the original observation and rerun full checks. G01–G05 remain DRAFT. The board records eligibility; task records preserve historical states instead of rewriting earlier conclusions.
