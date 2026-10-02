# P2 — Units, Schemas and Independent Input Checks

**Maps to:** P2.1–P2.8; D02/D03/D07/D08

## Entry condition

Current active implementation phase. Existing helpers and nine tests are starting artifacts, not P2 completion.

## Working contract

Use [00](../00-execution-protocol.md), the [task template](../templates/task-record.md), [software map](../03-software-build-map.md) and [acceptance matrix](../04-benchmarks-and-acceptance.md). Paths below are planned artifacts; package paths are relative to `src/aura/` unless prefixed otherwise. Each task uses the frozen domain from its dependencies and must declare its own primary observable, tolerance derivation and compute cap before execution. A predecessor marked DONE does not substitute for a required phase PASS.

## FND-01 — Freeze coordinate, SI and amplitude conventions

**Current state:** DONE — [review and artifacts](../../work-items/FND-01.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** Current baseline, code inventory and owner direction; no new physical run required.

**Steps**

1. Inventory current helper interfaces and check the existing docstrings against D02/D03.
2. Write explicit external value/unit representation, canonical SI, +Z frame, radius/diameter distinction and time/angle units.
3. Select and document one harmonic sign convention, pressure peak/RMS conversions, attenuation convention and translation rules for sources using another convention.
4. List independently calculable reference values and ambiguities; resolve these in the contract before adding numerical models.

**Required artifacts:** `docs/research/si-and-conventions.md`; equation records for existing helpers; proposed fixture table.

**Acceptance / decision:** Equivalent physical inputs have one unambiguous internal representation; no scientific property receives an undocumented default.

**If unsuccessful:** F-01; correct the convention contract before dependent code.

## FND-02 — Implement versioned scenario and evidence schemas

**Current state:** DONE — [implementation and review](../../work-items/FND-02.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-01

**Steps**

1. Define required Medium, Body, SourceArray, Scenario, SolverSpec, Experiment and RunManifest fields from D07/D08; distinguish research unknowns from executable inputs.
2. Implement strict JSON/YAML parsing, schema version handling and cross-field checks with explicit decisions for unknown/duplicate keys and boolean numeric inputs.
3. Specify vectors, array ordering, units, coordinates, source normalization, model identifier, regime metadata and typed result records.
4. Create minimal valid manufactured examples and invalid examples with missing, inconsistent and unsupported fields.

**Required artifacts:** `schema/models.py`, `schema/io.py`, `schema/quantities.py`; schema specification; compact fixtures.

**Acceptance / decision:** Valid examples parse; each malformed or incomplete executable input fails with its intended field and code; unsafe YAML constructs are rejected.

**If unsuccessful:** F-01; preserve backward compatibility or add an explicit schema migration.

## FND-03 — Extend safe SI calculations and conversion boundaries

**Current state:** DONE — [implementation and arithmetic verification](../../work-items/FND-03.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-02

**Steps**

1. Retain the existing wavelength/k/ka/intensity helpers and map their scientific domain to equation records.
2. Implement only the conversions and pure dimensioned quantities needed by the current contract; add RMS/peak and attenuation conversion if selected.
3. Define behavior for nonfinite inputs, zeros, signed physical quantities, overflow/underflow and unsupported units.
4. Compare with separately computed values and equivalent-unit cases; keep progressive-wave intensity restricted to that declared regime.

**Required artifacts:** Updated `units.py`; quantity parsing; `tests/unit/test_units.py` or existing equivalent; independent fixture provenance.

**Acceptance / decision:** B-01 passes including edge cases; finite inputs that overflow cannot silently become accepted nonfinite scientific outputs.

**If unsuccessful:** F-01/F-03; fix arithmetic or domain, never generalize a restricted formula.

## FND-04 — Implement stable MCLF L0 rules and typed errors

**Current state:** DONE — [implementation and audit verification](../../work-items/FND-04.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-03

**Steps**

1. Draft R-001…R-010: schema/version, presence, units, finite input/output, permitted ranges, shape/frame, amplitude convention, source/config identity, declared model coverage and result completeness.
2. For each rule record predicate, assumptions, severity, tolerance source, affected fields and expected diagnostic.
3. Implement aggregate decision logic preserving INVALIDATED, ALERT and INDETERMINATE; distinguish hard domain violation from lack of coverage.
4. Expose machine-readable and human-readable reports; do not reuse a solver success flag as an audit.

**Required artifacts:** `errors.py`, `mclf/rules.py`, `mclf/evaluate.py`; versioned rule register; report schema.

**Acceptance / decision:** Each rule has accepted/rejected/uncovered examples as applicable, and combined-rule severity cannot hide a hard failure.

**If unsuccessful:** F-01/F-03; reconcile rule meanings with D02 before proceeding.

## FND-05 — Build independent known-answer and invalid-input verification

**Current state:** DONE — [verification and limitations](../../work-items/FND-05.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-04

**Steps**

1. Turn the hand/reference table into compact tests; avoid deriving expected outputs through the implementation under test.
2. Cover radius/diameter and pressure convention mistakes, invalid vectors, changed hashes, unsupported versions and omitted required physics.
3. Verify that rejected input never invokes an allocation/solver hook.
4. Map these checks to FR-001/002/009 and report uncovered cases.

**Required artifacts:** Unit/integration checks; B-01/B-02 report; initial traceability record.

**Acceptance / decision:** Every specified rejection has a specific diagnostic; a known-valid case survives serialization and audit unchanged.

**If unsuccessful:** F-01/F-10; fix the implementation or explicit contract, not expected values to match a bug.

## FND-06 — Expose configuration validation through the CLI

**Current state:** DONE — [CLI implementation and verification](../../work-items/FND-06.md). **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-05

**Steps**

1. Preserve `aura status` and add the documented `validate-config` command with human and machine output.
2. Translate typed errors to stable nonzero exit codes and name any unavailable capability honestly.
3. Document install and validation examples with manufactured values clearly labeled.
4. Exercise valid, invalid and missing-file CLI cases from a clean environment.

**Required artifacts:** `cli.py`; CLI usage document; example scenario; integration checks.

**Acceptance / decision:** Users can validate a complete scenario without importing any future solver; command failures are visible to scripts and humans.

**If unsuccessful:** F-01/F-10; no success output after validation failure.

## FND-07 — Freeze canonical serialization and immutable hash identity

**Current state:** READY; FND-06 is complete. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-06

**Steps**

1. Specify canonical ordering, encoding, normalized SI values, finite-number policy, precision and schema version in hashed representations.
2. Separate paths/timestamps that should not affect physical input identity from actual scenario content; record both identities where needed.
3. Implement config/data/environment hash functions and the RunManifest model without overwriting run artifacts.
4. Test reordering equivalence, physical-input changes, tampering and round-trip behavior.

**Required artifacts:** Serialization/hash code; manifest schema; canonical fixtures; B-02 identity report.

**Acceptance / decision:** Equivalent canonical inputs hash equally; changed scientific inputs and altered data are detected; hashes are not used as proof of scientific equivalence.

**If unsuccessful:** F-09; version the canonicalization change and preserve old identities.

## FND-08 — Lock the development environment and close P2

**Initial state:** BLOCKED by predecessors / applicable gates. **Owner role:** research implementer; phase review by the roles in [00](../00-execution-protocol.md).

**Inputs / predecessors:** FND-07

**Steps**

1. Review current dependency compatibility/licenses for the small CPU core and necessary next-step numerical tools; record optional extras separately.
2. Create a reproducible environment lock/snapshot and install it in a fresh Python environment.
3. Complete the full CI checks, relative links and P2 evidence review; update D03 mapping and capability inventory.
4. Record P2 PASS or exact unresolved conditions, then enable RUN-01 and the P3 cards only on the permitted gate.

**Required artifacts:** Environment lock/decision; P2 gate review; updated examples and traceability.

**Acceptance / decision:** A fresh environment reproduces P2 checks; all required contracts are reviewable and CI passes.

**If unsuccessful:** F-10/F-11; document dependency or review gaps without pretending P2 is complete.

## Phase exit review

Canonical input contracts, independent known-answer checks, R-001…R-010 definitions, deterministic serialization and a reproducible development environment are reviewed. All required invalid inputs fail before allocation.

Before starting RUN-01/P3, give the owner the requested plain-language explanation of the simulation system/core: components, inputs, outputs, first verification cases and limits. This communication checkpoint was requested on 2026-10-02 and does not add a scientific approval gate.

Use [the gate template](../templates/gate-review.md), attach the actual artifact/run/CI links, and update [the board](../10-work-board.md). Keep experimental validation and software verification distinct.
