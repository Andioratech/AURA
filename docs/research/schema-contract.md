# Initial Schema Contract — Versions 1.0 and Scenario 1.1

**State:** Scenario 1.0 implemented in FND-02; Scenario 1.1 extension added for NUM-03; no physical validation implied. **Date:** 2026-10-04.

Authority: [D07](../D07-experiments-data.md), [D08](../D08-software-contracts.md), [CONV-1.0](si-and-conventions.md). The executable field definitions are in [definitions.py](../../src/aura/schema/definitions.py); cross-field predicates are in [models.py](../../src/aura/schema/models.py). Changes to accepted fields require an explicit version/migration decision; readers never guess a version or silently discard fields.

## Envelope and records

Every standalone document requires `document_type`, `schema_version` and `id`. Existing records remain on immutable schema 1.0. Scenario 1.1 is an explicit, separately validated extension for the DEC-002 circular-piston air case; other document types remain at 1.0. Readers select the declared version and never guess or discard fields. Nested records omit the envelope. Identifiers are nonempty ASCII letters/digits with hyphens, underscores or dots; the first character is alphanumeric. Example IDs are parser fixtures, not registered experiments or actual scientific runs.

| Document type / Python type | Required content | Explicit optional or unavailable content |
|---|---|---|
| `medium` / `Medium` | Temperature, density, sound speed, viscosity, compressibility, amplitude attenuation and provenance | No material database defaults |
| `body` / `Body` | Material, discriminated geometry, mass, density, compressibility, position, velocity, orientation, angular velocity and provenance | Optional body-frame 3×3 inertia tensor; missing inertia cannot authorize rotation |
| `transducer_array` / `TransducerArray` | Frequency, peak amplitude convention, harmonic sign, element positions/unit normals, phases, source models and provenance | Scenario 1.0 requires pressure amplitude/limit for every source. Scenario 1.1 keeps those fields for ideal plane/spherical waves and gives a circular piston displacement amplitude/limit in metres; pressure and displacement amplitudes cannot be mixed. Circular piston requires aperture radius. |
| `solver_spec` / `SolverSpec` | Model ID/version, equation IDs, regime, precision and parameter object | Parameters currently permit iteration cap, tolerance, mesh spacing and time step only |
| `scenario` / `Scenario` | CONV-1.0, chamber frame, medium, bodies, sources, solver, domain/boundaries, explicit gravity, target/window, resources and provenance | No missing physics receives a default |
| `experiment` / `Experiment` | Scenario ID/digest, hypothesis/claim, primary observable/window/unit, acceptance rule, uncertainty plan, protocol reference and provenance | Unknown uncertainty is recorded; no measurement is synthesized |
| `run_manifest` / `RunManifest` | Experiment/scenario/claim identities, hypothesis/observables, UTC time, source/config/environment identity, solver, seed, resources, inputs/outputs, metrics, convergence, audit state and failure notes | Nullable seed, failure code and clean-tree patch digest; `not_run` audit is explicit |
| `field_result` / `FieldResult` | Model ID/version/regime, chamber coordinates, pressure artifact metadata, harmonic/peak conventions, diagnostics and provenance | Velocity may be null; arrays are external references |
| `force_result` / `ForceResult` | Run/body/model/version/regime, chamber force vector, float64 precision, validity and provenance | Torque null iff explicitly unsupported |
| `mclf_report` / `MclfReport` | Run identity, L0–L5 label, declared verdict, rule outcomes and limitations | This record stores an audit; it does not execute one |

All other fields are rejected. Sphere geometry requires a positive radius in metres; box geometry requires three positive side lengths. A box can represent a larger object without pretending that the particle solver supports it. Further geometry/material branches need explicit contracts.

## Quantities and cross-field checks

Dimensional values use `{"value": number, "unit": "canonical SI symbol"}`; vectors use fixed-length arrays. Bare numbers, numeric strings, booleans, null required values, incompatible units and nonfinite numbers fail. Canonical symbols and quantity shapes are defined in [quantities.py](../../src/aura/schema/quantities.py). FND-03 now provides an [opt-in quantity conversion API](numerical-domain-and-conversions.md); the version-1.0 reader itself remains canonical-only. Zero viscosity/attenuation, zero pressure amplitude and explicit zero gravity are representable idealizations, not assertions that such conditions are experimentally achieved.

Implemented cross-field checks:

- Source normals and orientation quaternions have unit norm within absolute 1e-12; no normalization occurs. Body/source IDs are unique within their collections.
- Pressure or displacement amplitudes cannot exceed their corresponding declared limits. End time must exceed start time.
- Body centers lie inside the declared box domain; domain upper bounds must remain finite and distinguishable from their origins.
- Reported uncertainty requires a reference. Unknown uncertainty remains unknown.
- Dirty source state requires a patch digest; clean state requires null. Failed/aborted executions require a failure code; other states require null. Completed executions require an output reference.
- UTC timestamps must use `YYYY-MM-DDTHH:MM:SS[.fraction]Z` and a valid calendar date/time. Leap seconds are not supported by this initial manifest format.
- Field coordinates have shape `[N,3]`, metres and float64; pressure has `[N]`, pascals and complex128; optional velocity has `[N,3]`, m/s and complex128.
- Available torque requires a three-component value in N*m. An ACCEPTED audit declaration cannot include a nonaccepted check.

## Reader behavior and resource limits

The reader accepts one UTF-8 JSON or YAML document, at most 1 MiB. Direct dictionary callers are bounded by their compact JSON encoding as well. Tree traversal permits at most 100,000 nodes and depth 64 (the YAML composer counts its root as one level). Limits protect parsing; they are unrelated to physical scale or solver RAM estimates.

Duplicate keys, unknown versions/types/fields, non-string mapping keys, YAML aliases/merge constructs, unsafe object tags and multiple documents are rejected. YAML integers must use decimal notation without leading zeros; base-60, octal and hexadecimal spellings are rejected. Quote YAML timestamps so they remain strings. JSON numeric literals and YAML numeric values that overflow binary64, or nonzero floating literals that underflow to zero, are rejected. Ordinary binary64 rounding is still present; a string is never silently converted to a number. Direct Python callers cannot recover information already lost before calling the validator.

`InvalidInputError` includes `code`, `path` and `message`, with `as_dict()` for machine use. Paths use JSON Pointer escaping. Schema and cross-field errors identify their affected field or container. Syntax, duplicate-key and parser-limit failures can have the empty document-root path because a valid tree does not yet exist. Codes include `INPUT_TYPE`, `SCHEMA_VERSION`, `DOCUMENT_TYPE`, `SCHEMA_INVALID`, `UNIT_MISMATCH`, `INCONSISTENT`, `NONFINITE`, `NUMERIC_RANGE`, `NUMERIC_FORMAT`, `KEY_TYPE`, `VALUE_TYPE`, `DUPLICATE_KEY`, `YAML_ALIAS`, `INPUT_LIMIT`, `PARSE_ERROR` and `FORMAT`. Filesystem errors retain their standard Python types.

## Available API

After installing the repository, run from its root:

```python
from aura.schema import Scenario, dumps_document, load_document, loads_document

record = load_document("examples/schema/manufactured-scenario.json")
assert isinstance(record, Scenario)
copy = loads_document(dumps_document(record, format="yaml"), format="yaml")
assert copy.to_dict() == record.to_dict()
```

`validate_document(dictionary)` chooses the typed record; direct constructors such as `Body(dictionary)` enforce their document type. `Scenario` accepts the declared 1.0 and 1.1 envelopes, with distinct version-specific source schemas; all other current records accept 1.0. Records store isolated serialized snapshots and return new dictionaries. Input dictionaries and returned copies cannot mutate validated state. Display serialization preserves values; [FND-07 canonical identity](content-identity.md) is a separate API. [FND-06 CLI validation](../cli-usage.md) implements `aura validate-config`; `aura status` remains available.

FND-07 defines full canonical configuration and raw artifact digest meanings without changing schema 1.0 fields. The existing RunManifest model remains an immutable in-memory snapshot; persistence and run creation are RUN-01. Configuration/link verification and bounded local file checks must be called explicitly. Merely parsing a digest string still does not authenticate content.

## What acceptance does not establish

This layer checks representation and selected consistency predicates. It does not verify referenced file existence/content/digests, cross-document identity links, equation applicability, solver availability, geometry wall clearance, mass-volume-density consistency, inertia symmetry/physical admissibility, material constitutive relations, resource feasibility or physical validity. A supplied model ID or ACCEPTED label is metadata, not proof or permission to run/promote evidence. Those checks belong to later MCLF, model, resource and run-management tasks; no simulation dispatch exists yet.

The manufactured water-like fixture is intentionally complete so code can progress without choosing experimental material, hardware or target performance. Its numbers are neither measurements nor the proposed experiment. The larger-box verification only establishes that the representation supports that geometry.

## Dependency decision

FND-02 adds the CPU-core libraries `jsonschema==4.26.0` (MIT, Python >=3.10) and `PyYAML==6.0.3` (MIT, Python >=3.8). Installed package metadata was inspected on Python 3.12.14. This meets the project's Python >=3.10 declaration at the metadata level; execution was verified on 3.12 only. Transitive/environment locking remains FND-08; the two direct pins do not constitute a reproducible environment lock.

The implementation uses local Draft 2020-12 schemas and explicit cross-field checks. JSON Schema alone does not guarantee date checking: the initial negative test exposed an optional-format dependency, so the project registers its own calendar check using Python's standard library. See the [official jsonschema validation documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/). YAML uses SafeLoader with additional duplicate, alias, depth and numeric guards; SafeLoader alone does not provide all of these policies. See the [official PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation).

Verification and observed failures are recorded in [FND-02](../work-items/FND-02.md). This layer cannot close P2 by itself.
