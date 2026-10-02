# B-01/B-02 — Foundation Verification Report

**Protocol:** FND05-v1.0 · **Date:** 2026-10-02 · **Review:** implementer artifact review

## Question and evidence boundary

This report verifies the composition of the existing SI helpers, strict scenario readers, immutable snapshots, L0 evaluator and explicit acceptance gate. It follows the frozen [FND-05 protocol and failure log](../work-items/FND-05.md), [B01-v1.0 reference table](../research/foundation-reference-values.md), [schema 1.0](../research/schema-contract.md) and [L0-1.0 rules](../registers/mclf-l0-rules.md). The [equation register](../registers/equations.md) retains the earlier source review and physical restrictions; no new model or formula is selected here.

Fixtures are manufactured software inputs. The water-like example is not measured water, a hardware selection or a calibrated particle. Its temporary run/report identifiers and digest strings are not scientific run identities or authenticated evidence. The larger-box case checks representation and withheld model coverage; it does not extend a particle force model to larger bodies.

## Independent expected answers and criteria

The compact [numeric fixture](../../tests/fixtures/foundation/known-answers.json) is transcribed from the published hand-reference table, independently of production helper outputs. Its seven scalar cases use the existing relative 1e-12 and absolute 1e-15 tolerances. B01-07 uses exact equality for the declared 1 mm to 0.001 m conversion. Other checks compare exact diagnostics, dictionaries, labels and hook call counts. Existing FND-03 extreme-number cases retain their separate binary64-aware criteria.

The [rejection matrix](../../tests/fixtures/foundation/rejections.json) names 22 specific input faults, expected reader codes/paths and L0 rule findings. Tests do not obtain expected values by inspecting production schemas or calling a second production helper. The real schema and auditor do share structural definitions; this is software integration verification, not an independent mathematical formulation or scientific review.

## B-01 traceability

| Reference | Concrete check in `tests/` | Result and limit |
|---|---|---|
| B01-01…06, B01-08 | `test_foundation_verification.py::test_frozen_b01_answers` | Seven frozen numeric answers; ordinary-scale manufactured arithmetic only |
| B01-07 | `test_b01_07_equivalent_units_and_explicit_zero_survive_roundtrip` | Exact declared-unit equivalence and JSON/YAML round trip |
| B01-09 | Same round-trip check | Explicit zero gravity retained; no evidence of actual microgravity |
| B01-10 | `test_rejection_diagnostics_and_zero_hook_calls`; boolean/string density fixtures | Correct type diagnostic, INVALIDATED audit and no hook call |
| B01-11 | Same matrix; omitted temperature, gravity, solver, boundary and mass; unit/vector faults | Named missing/range/shape/convention failures; no inferred physics |
| B01-12 | Existing `test_units.py::test_unrepresentable_outputs_raise_structured_errors` and `test_fixed_extreme_intensity_grid_against_decimal_oracle` | Controlled numerical-domain errors; fixed 729-point arithmetic grid remains in the full suite |

**B-01 software comparison: PASS in the frozen arithmetic/representation scope.** This cannot establish acoustic model validity, attainable force or experimental agreement.

## B-02 and gate composition

The [integration tests](../../tests/test_foundation_verification.py) compose `load_document → evaluate_scenario → require_accepted → allocation hook → solver hook`. This composition lives **only in the test module**. Allocation/solver hooks are spies: no mesh, field array, solver or run directory is created.

| Check | Observed outcome | Scope |
|---|---|---|
| 22 faults through JSON and YAML | 44 exact reader failures; L0 INVALIDATED and expected finding for each | Both downstream hooks receive zero calls |
| Duplicate keys, NaN, numeric underflow, unsafe YAML tag and alias | Eight exact serialization failures | Neither hook called; executable YAML is not loaded |
| Valid scenario and explicit zero gravity | Same snapshot and same audit after JSON/YAML serialization | Overall INDETERMINATE for missing model/evidence coverage |
| Mutated dictionary returned by a snapshot | Stored scenario remains unchanged | No mutation of previously validated input |
| Gate deliberately bypassed in an isolated positive-control test | Both hooks reached, allocation first | Demonstrates that zero-call assertions are not caused by unreachable hooks; bypass never enters production |
| Direct nonfinite values | R-004 NONFINITE and typed gate rejection | Both hooks remain uncalled |
| Supplied INVALIDATED/ALERT/INDETERMINATE result | Status preserved and promotion hook not called | Hard failure or incomplete evidence remains visible |
| Supplied ACCEPTED result | Audit stays INDETERMINATE; promotion refused | Caller success label cannot supply missing model evidence |
| Malformed digest text | Explicit schema failure | Format validation only |
| Changed, well-formed digest text | HASH_UNCHECKED; acceptance refused | Content authentication is **not implemented or claimed** |
| Larger box with greater declared mass | Structural round trip succeeds; MODEL_UNCOVERED remains | Does not unlock a solver or infer applicability |

**B-02 structural/gate composition: PASS for these cases. B-02 identity benchmark: PENDING FND-07.** Key-order canonical hash equality, actual configuration/artifact tampering, environment/source authentication and immutable run storage are not verified by this card. RUN-01 must repeat the ordering checks on the actual execution lifecycle, including explicit treatment of exploratory inputs under DEC-003. This test harness is not a future execution-policy decision to forbid every exploratory model run.

Subsequent evidence: [FND-07's B-02 identity report](B02-content-identity.md) closes the canonical/configuration/file-integrity comparison. The statement above preserves FND-05's original scope; actual source/environment evidence binding and immutable run storage still require later integration.

## Limits exposed by verification

1. An explicit unsupported `diameter` key and an explicit `rms` convention are rejected. A positive diameter mislabeled as radius, or RMS data mislabeled as peak, can pass structural checks because the caller supplied the wrong meaning. Provenance/reference mapping must address these errors. The tests retain both the accepted declarations and their INDETERMINATE scientific status.
2. In the manufactured ordinary-scale ka calculation, substituting a 0.002 m diameter for a 0.001 m radius doubles ka. In the declared plane-progressive-wave toy only, treating a peak value of 2 Pa as an RMS value changes the intensity from 0.25 to 0.5 W/m² (rho=2 kg/m³, c=4 m/s). These checks illustrate the existing formulas' convention dependence, not a general wave-field or force relation.
3. The schema checks body centers, declared fields and some consistency conditions. It does not certify full-body clearance, material constitutive consistency, uncertainty, source feasibility or model validity. Increasing size/mass does not change that boundary.
4. Zero calls prove the order of the tested composition. A future caller can omit a gate; its real integration must be tested. No complete FR-002/FR-009 or P2 closure follows from this report.

## Reproduction and decision

Run `pytest -q tests/test_foundation_verification.py` in the development environment, then the complete Quality workflow in [08](../planning/08-reproducibility-and-ci.md). All inputs are committed fixtures or explicitly constructed dictionaries; there are no stochastic seeds, acquired data, external artifact reads or scientific runs. FND-08 will lock the environment, and the delivery message identifies the immutable source commit and exact remote CI run.

The focused suite passed **76 cases** after the preserved fixture correction in FND-05. Foundation verification enables FND-06's configuration-validation CLI. P2 remains ACTIVE and the owner's explanation checkpoint remains before RUN-01/P3.
