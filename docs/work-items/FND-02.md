# FND-02 — Strict Versioned Input and Evidence Schemas

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Depends on:** FND-01 / CONV-1.0

## Question and acceptance fixed before implementation

Can the schema boundary accept complete manufactured records and reject malformed, ambiguous or inconsistent inputs before any scientific solver runs?

Scope: Medium, TransducerArray, Body, SolverSpec, Scenario, Experiment and RunManifest records, plus structural field/force/audit result metadata. Model equations, material selection, force validity and scientific evidence promotion are outside this task. No simulation or experiment is launched.

Acceptance is exact rejection/acceptance with named field paths and error codes; no physical tolerance is chosen. CONV-1.0's 1e-12 norm tolerance applies to serialized unit orientations/directions only. Valid examples must round-trip JSON/YAML without input mutation. Unknown versions/fields, duplicate keys, nonfinite values, booleans as physical numbers, numeric strings, unsupported units, bad vector shapes, unsafe YAML tags, aliases and inconsistent cross-field identities/windows must be rejected. Typed snapshots must not expose mutable validated state.

## Design and resource bounds

- Use local JSON Schema Draft 2020-12 definitions and `jsonschema`; no remote schema retrieval. Use PyYAML SafeLoader with additional duplicate/key/alias/depth checks. Review their installed metadata/licenses and compatibility before closing the task.
- Freeze serialized schema version `1.0`; dimensional values use canonical SI only at this step. Unit conversion is FND-03, canonical hashes FND-07 and CLI validation FND-06.
- Limit a serialized input to 1 MiB, nesting depth to 64, and numeric values to finite binary64 representability. Reject oversized/deep inputs before validation. These are parser resource guards, not physical limitations.
- Preserve explicit object geometry and model IDs. Accepting geometry metadata does not grant solver capability. No physical defaults are supplied.
- Implement `schema/definitions.py`, `quantities.py`, `models.py`, `io.py` and narrow `errors.py`; add dependency pins, manufactured example, meaningful independent negative and integration checks, and schema documentation.
- Tests must use independently assembled valid/invalid records, not generate expected answers by calling the schema under test. Exercise a physically larger box record to confirm the representation is not hard-coded to particles.

## Delivery and limits

Record actual test counts, observed failures/corrections, environment/dependency identities, unsupported capabilities and review findings before DONE. Complete the full current CI and relative-link check before the commit; verify remote CI afterward. This task cannot close the P2 gate or establish physical/model validity.

## Implemented artifacts and scope review

- [Schema contract and dependency decision](../research/schema-contract.md), [strict reader](../../src/aura/schema/io.py), [declarative definitions](../../src/aura/schema/definitions.py), [typed snapshots and cross-checks](../../src/aura/schema/models.py), [SI/tree primitives](../../src/aura/schema/quantities.py) and [input errors](../../src/aura/errors.py).
- [Manufactured scenario](../../examples/schema/manufactured-scenario.json) and [104 schema checks](../../tests/test_schema.py), including ten record types in JSON/YAML, immutable snapshots, malformed input, resource limits, rejected ambiguous numbers, negative-run preservation and a larger box.
- README and construction map identify the implemented API. `load_document` / `validate_document` supersede the proposed `load_scenario` interface name. Capability dispatch remains unimplemented; no metadata acceptance authorizes execution.

Review role: implementation self-review against D07/D08 and the frozen protocol, with independently authored manufactured inputs. No independent scientific reviewer or experimental validation is claimed.

## Actual verification and preserved failures

Environment: Linux, Python 3.12.14, jsonschema 4.26.0, PyYAML 6.0.3, pytest 9.1.1 and Ruff 0.16.10. Direct runtime dependency versions, licenses and Python requirements were inspected in installed metadata; full environment locking is FND-08.

1. First suite: **98 passed, 1 failed**. A manifest dated February 31 was incorrectly accepted because jsonschema's default date-time checker had no optional format dependency installed. Fixed by registering a mandatory standard-library calendar check plus an explicit UTC spelling constraint. The negative test was retained unchanged. An initial import-order lint finding was also corrected.
2. Added fourteen parser/range, direction/quaternion boundary and identifier/digest spelling cases. Final local suite: **113 passed** (104 schema cases plus 9 existing checks), approximately 1.4 seconds in the reviewed environment. Review also tightened trailing-newline rejection and avoided dependence on a second numeric parser for extreme exponents. This verifies software behavior only.
3. Replayed every shell step of the current Quality workflow with Python 3.12: editable development install, Ruff, full pytest and required D00/PLAN-01/D01–D09/G01–G05 checks. All passed. The installed core supplies date checks without an optional format extra.
4. Whole-document relative-link review found four pre-existing paths broken by moving old plans into `docs/archive/`. Corrected only those navigation destinations; their scientific text/version was retained. Final review checked **320 relative links with zero missing destinations**.
5. FND-01 delivery `dac41fb06b85d377547c85f1046e67844c4751bf` already passed [remote Quality](https://github.com/Andioratech/AURA/actions/runs/37013899879). This task's exact delivery revision and remote CI outcome are identified by Git history and the delivery report; local success alone is not a remote result.

No simulation was executed, no EXP/RUN scientific identity was minted, and no measurement was produced. Tests exercise metadata references without claiming the referenced fixture artifacts exist. Invalid-date failure evidence is retained above and in its regression case.

## Acceptance and next branch

FND-02 is DONE as an input/metadata implementation task. FND-03 is READY to harden scalar arithmetic and add explicit conversions. The previously observed helper coercion/overflow gaps remain assigned there; these schema checks do not silently declare them fixed. FND-04 must implement model-coverage and audit decisions, FND-06 the CLI boundary and FND-07 identity verification/canonical hashes. Material consistency, physically admissible inertia, geometry clearance and model suitability require their applicable later checks. **P2 remains ACTIVE, not PASS.** No owner decision is needed to continue these independent foundations.
