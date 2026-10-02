# FND-03 — Safe SI Arithmetic and Explicit Conversion

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Depends on:** FND-02

## Question and acceptance fixed before implementation

Can the scalar foundation reproduce B01-v1.0 values, reject malformed operands, preserve representable answers despite extreme intermediate factors, and reject unrepresentable final results without changing physical equations?

Starting revision: `8edcef39c57000e4a735724ec0b4fbacdcfcd0df`. Governing contracts: D00/D02/D03/D08, CONV-1.0 and the equation register. No field/force model, material choice or physical simulation is authorized by this task.

## Frozen implementation scope

- Preserve public wavelength, wave-number, ka and progressive-plane-wave intensity APIs. Accept only built-in real integers/floats, excluding booleans/strings/null/complex and nonfinite values. Positive/nonnegative requirements remain explicit.
- Validate inputs before arithmetic. Use scaled product/quotient evaluation to avoid unnecessary intermediate overflow/underflow. A nonzero calculation that overflows or rounds to zero must raise a structured numerical-domain error, never return infinity/NaN/false zero. Finite subnormal results are permitted and tested with a separate rounding-aware criterion; no universal relative accuracy is promised there.
- Add explicit nonnegative single-sinusoid peak/RMS amplitude conversion, positive diameter-to-radius conversion and nonnegative amplitude/intensity attenuation-coefficient conversion. Do not introduce a standing-field intensity conversion or a generic force/power bound.
- Add an opt-in `canonical_quantity` adapter for scalar/fixed-vector value/unit objects. Support canonical SI identity and only these alternative spellings: `um`, `mm`, `cm`, `mg`, `g`, `us`, `ms`, `kHz`, `MHz`, `kPa`, `MPa`, `deg`. Unit/dimension and shape errors must identify the input path. Signed values and exact zeros are preserved where the quantity contract permits them; scenario validation still enforces physical ranges.
- The existing version-1.0 document reader stays strict about canonical SI. Conversion is explicit, returns a new quantity and never rewrites a scenario, changes radius semantics, normalizes directions or supplies physical defaults. No schema migration or new dependency is needed.

## Independent verification and resource cap

Use B01-v1.0's relative 1e-12 / absolute 1e-15 only for its manufactured normal-scale checks. Independently specified decimal and power-of-two extreme cases use relative 1e-12 with absolute zero; subnormal cases permit at most one binary64 unit in the last place. Structured error classes/codes/paths, zero handling, input immutability and schema behavior are exact checks.

Before implementation, preserve diagnostic outcomes from the old helpers, including finite-input false zero, infinity and intermediate overflow. Add regressions for those cases and independently compute selected extreme expected values using standard-library Decimal at high precision; do not derive expected answers by calling implementation utilities. Bound this work to CPU scalar tests (no meshes, external data, random search or scientific run allocation); target less than 10 seconds for the suite and stop to investigate if it exceeds 60 seconds. No performance claim follows from this development cap.

## Delivery gate

Close only after actual checks, reference review, dependency/limitation notes, full local Quality workflow and relative-link review are recorded. Inspect configured author/committer and staged contents; publish one focused implementation commit and confirm the exact remote CI. FND-04 becomes READY; P2 remains open.

## Delivered implementation and review

- [Numeric-domain and conversion contract](../research/numerical-domain-and-conversions.md): explicit input/result policies, API, sources, unit spellings and limitations.
- [Scalar helpers](../../src/aura/units.py): scaled arithmetic, strict operands, peak/RMS, diameter/radius and attenuation-convention adapters. [Quantity conversion](../../src/aura/schema/quantities.py) is opt-in; the document schema and physical formulas are unchanged.
- [Scalar tests](../../tests/test_units.py) and [conversion/integration tests](../../tests/test_quantity_conversion.py) preserve independent expected values and error paths. Equation register v1.1 records implementation status without altering equations or evidence claims.

Review role: implementation self-review against the frozen protocol and governing contracts. No independent qualified scientific review is claimed. No new library or physical-model dependency was added. BIPM's official SI Brochure v4.01, Chapter 3/Table 7 and Chapter 4/Table 8, was checked for conversion definitions; Python's official 3.12 math documentation was checked for binary exponent decomposition. Relevant locators and links are in the delivered contract.

## Preserved old behavior and corrected outcomes

The source at `8edcef39` was executed in isolation and compared with the new functions. These are manufactured scalar diagnostics, not experiment runs.

| Call / inputs | Old behavior | New behavior |
|---|---|---|
| Wavelength with boolean speed | Returns 1.0 | `NUMBER_TYPE` with operand path |
| Wavelength with string speed `"343"` | Returns 4.9 | `NUMBER_TYPE` with operand path |
| Wavelength 1e308 / 1e-308 | Infinity | `NUMERIC_RANGE` |
| Wavelength 1e-308 / 1e308 | False zero | `NUMERIC_RANGE` |
| Wave number with c = f = 1e308 | Infinity from an intermediate product | 6.283185307179586 |
| Intensity with p = rho = c = 1e200 | Raw `OverflowError` | 1.0 |
| Intensity with p = rho = c = 1e-200 | Raw `ZeroDivisionError` | 1.0 |
| Intensity with p = rho = 1e-200, c = 1 | False zero | 1e-200 |

The first expanded suite passed 365 cases. Additional zero-boundary, missing-temperature and independent-grid checks brought the final suite to **385 passed** in approximately **1.6 seconds**, inside the predeclared compute cap. This adds 272 test cases to the previous 113; the deterministic grid below is one of those cases and is not counted as 729 separate pytest items.

The independent grid compares all 9³ = **729** combinations of fixed extreme operands against 120-digit Decimal arithmetic. Outcome: **297 finite answers**, **432 expected numeric-range rejections**, **zero discrepancies**. The selection includes subnormal, normal and near-maximum magnitudes. These intentionally extreme numbers test arithmetic and do not describe proposed water/material conditions.

Full local Quality replay passed: editable development install, Ruff, all tests and required-document checks. Relative-link review checked **342 destinations with zero missing files**. Environment: Linux, Python 3.12.14, pytest 9.1.1, Ruff 0.16.10; runtime dependency pins remain jsonschema 4.26.0 and PyYAML 6.0.3. Execution on other Python versions and a fresh locked environment remain FND-08 work. The exact delivery revision and remote-CI result are identified by Git history and the delivery report; local success is not a remote result.

## B-01 traceability and acceptance

| Frozen fixture | Verification |
|---|---|
| B01-01…B01-06, B01-08 | `test_b01_and_conversion_known_answers`; original values and tolerances retained |
| B01-07 | `test_independently_specified_unit_factors`, explicit-adapter/schema integration |
| B01-09 | Explicit zero gravity survives `test_explicit_adapter_then_strict_scenario_validation` |
| B01-10 | Every scalar operand rejects booleans/strings with a named path; vector components do likewise |
| B01-11 | Missing-temperature, wrong-unit and wrong-vector-shape rejection cases |
| B01-12 | Structured result-range failures, representable extreme cases and Decimal grid |

**B-01 arithmetic scope passes. FND-03 is DONE; FND-04 is READY.** FND-05 still owns the broader foundation verification and audit/allocation checks. P2 is ACTIVE, not PASS. These results verify arithmetic and representation only: no force, motion, control, experimental comparison or scale-up claim is established. The next work is the independent L0 rule/report layer; it needs no new material or hardware decision from the owner.
