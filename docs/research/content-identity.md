# Canonical Serialization and Content Identity

**Contracts:** AURA-C14N-1 / AURA-IDENTITY-1 · **Date:** 2026-10-02 · **Task:** [FND-07](../work-items/FND-07.md)

Authority: D00, D07, D08 and [schema 1.0](schema-contract.md). These are content-integrity primitives. They do not establish scientific validity, authorship, trusted provenance, an installed environment, or reproducible simulation execution. No scientific run has been created by this task.

## Three distinct identities

| Identity | Includes | Deliberately excludes | Intended use |
|---|---|---|---|
| Full canonical document SHA-256 | Every validated field, including schema version, IDs, provenance and resources | JSON/YAML layout, object key order, numerically equal integer/float spelling and zero sign | Bind a manifest to the complete scenario; compare supported document content |
| Conservative scenario-input SHA-256 | Scenario fields except the three exact root exclusions below; includes nested IDs/provenance, material names, complete solver parameters, boundaries, gravity and target | Only root `/id`, `/resources`, `/provenance` | Compare the explicitly defined input projection; not a solver cache key or proof of physical equivalence |
| Raw file SHA-256 | Every byte, including whitespace and line endings | Filename, location, modification time | Check data and environment-lock files against independently retained expected digests |

All three must remain distinguishable. A provenance note or resource limit changes the full scenario identity even when the projection stays the same. Nested fields are not recursively discarded by their names: for example, a changed medium reference changes both identities. Equal projection hashes cannot justify ignoring resource budgets, model applicability or experiment protocols.

A manifest's timestamp or artifact URI changes the **manifest** document digest. It does not enter the scenario's input projection. Moving identical file bytes changes no raw file digest. Actual identity verification still checks the full scenario digest and relevant declared links.

## AURA-C14N-1 byte contract

1. Start with a finite JSON-compatible tree restricted by the existing reader limits: 1 MiB JSON input, depth 64 and 100,000 nodes. A typed document must pass its versioned schema and cross-field checks before encoding. The generic `canonical_json_bytes` helper checks JSON admissibility only, not a scientific schema.
2. Objects sort keys by Unicode code-point order. Arrays preserve order. Preserve strings exactly; do not normalize Unicode, trim text, resolve paths or rename identifiers. Use JSON string escaping with ASCII output (`ensure_ascii=True`), including lowercase hexadecimal escapes and surrogate-pair escaping for non-BMP characters. The resulting ASCII bytes are also valid UTF-8.
3. Encode null and booleans as JSON literals. Encode integers as exact base-10 integers; do not first convert them to float. Encode finite built-in floats as the exact decimal value of their binary64 representation, using fixed-point notation without rounding. Remove trailing fractional zeros and a resulting decimal point. Encode all numeric zeros as `0`. Thus `1` and `1.0` agree, while `true`, `"1"`, nearby floats and distinct large integers remain different.
4. Add no optional spaces, indentation, byte-order mark or trailing newline. Limit expanded canonical output to 16 MiB; reject excess with `CANONICAL_LIMIT`. Expansion can make a canonical payload larger than the ordinary reader's 1 MiB input cap; such payloads are hash encodings, not automatically reloadable configuration files. Keep normal display serialization for editable inputs and retain original bytes when spelling matters.
5. No unit conversion, numeric tolerance, approximate equality, vector normalization or model selection occurs during hashing. Scenario inputs must already be canonical SI under CONV-1.0. Explicit conversion APIs operate before full validation.

The float rule deliberately captures the value available to the program. For example, binary64 `0.1` encodes as `0.1000000000000000055511151231257827021181583404541015625`. It cannot recover precision lost while initially parsing a decimal literal. `Decimal.from_float` supplies the exact conversion; decimal arithmetic/context rounding is not used. [Python decimal documentation](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.from_float).

This is a project-specific encoding, **not** RFC 8785/JCS. Other encoders must implement these rules and pass the golden fixtures before being treated as compatible. Future encoding or projection changes need a new contract identifier and an explicit migration decision; never silently rehash historical evidence under a new rule.

## Hash preimages and field meanings

For complete documents, hash these bytes:

```text
AURA-C14N-1\ndocument\n<canonical-document-bytes>
```

For the scenario projection, use `AURA-C14N-1\nscenario-inputs\n<canonical-projection-bytes>`. Here `\n` means one LF byte; the examples do not imply a trailing LF. SHA-256 is computed through the standard library. [Python hashlib documentation](https://docs.python.org/3.12/library/hashlib.html).

`ScenarioIdentity` returns `identity_version`, `canonical_version`, `document_sha256` and `inputs_sha256` as a frozen record. `document_sha256(record)` also supports the existing Experiment and RunManifest snapshots. Schema version remains inside every document/projection preimage.

For records newly assembled under this contract:

- `RunManifest.configuration_sha256` and `Experiment.scenario_sha256` contain the **full document** digest, never the projection or the original JSON file's raw digest.
- Artifact `sha256` fields, including `environment.lock.sha256`, contain **plain SHA-256 of file bytes**, with no canonical prefix. Environment text is not silently sorted or normalized; semantically similar lockfiles can have different content identities.
- `RunManifest.source.revision` and `source.patch_sha256` retain their existing roles. Configuration verification does not inspect Git or a patch. FND-08/RUN-01 supply and verify actual source/environment evidence.

Schema 1.0 fields and accepted inputs are unchanged. This defines previously unauthenticated hash semantics; old manufactured fixture strings are retained as placeholders and are not evidence of migration or successful verification. No accepted scientific runs exist to migrate. A future incompatible hash contract requires an explicit version association for saved manifests; retaining only an unqualified digest is insufficient.

## APIs and limits

```python
from aura.schema import load_document, scenario_identity
from aura.artifacts import file_sha256, verify_file

scenario = load_document("examples/schema/manufactured-scenario.json")
identity = scenario_identity(scenario)
print(identity.to_dict())

# For an existing locally retained file; select its byte budget explicitly.
digest = file_sha256("environment.lock", max_bytes=1048576)
# Persist the expected digest independently before a later verification.
verify_file("environment.lock", digest, max_bytes=1048576)
```

The last two lines illustrate the API, not independent authentication when executed immediately together. Replacing a file and its expected digest together defeats ordinary checksum comparison. This project does not add signatures or a trusted publisher registry here.

`verify_manifest_configuration(manifest, scenario, experiment=None)` revalidates typed snapshots, then checks manifest scenario ID, full solver specification, resources and configuration digest. If an Experiment is supplied, also check experiment ID, scenario ID, claim ID, hypothesis and scenario digest. It returns the computed ScenarioIdentity or raises `IntegrityError` with a named path. It does not compare observable definitions/windows, read referenced protocols/data/locks, verify source revision, assess metrics, or grant a scientific verdict. Those evidence checks remain owned by the execution/comparison tasks.

`file_sha256(path, max_bytes=...)` and `verify_file(path, expected_sha256, max_bytes=...)` require an explicit nonnegative maximum-file-size cap. They use read-only nonblocking file descriptors, accept regular files (including symlinks to regular targets), read chunks of at most 64 KiB, perform two bounded passes, and reject excess bytes. Comparing both content digests catches same-size rewrites even when the filesystem's timestamp resolution leaves metadata unchanged; descriptor/path identity and metadata checks catch ordinary replacement, growth and change cases. The cap applies to each pass, so total bytes read are bounded by two passes plus the per-pass overflow check. This is not protection against a malicious filesystem or a guarantee about the file after the check. Byte limits do not impose a storage-speed or wall-time limit. The current backend requires `O_NONBLOCK`; unsupported platforms receive `PLATFORM_UNSUPPORTED`. Descriptor operations follow the [Python os contract](https://docs.python.org/3.12/library/os.html#os.open).

Errors include `HASH_MISMATCH`, `IDENTITY_MISMATCH`, `ARTIFACT_CHANGED`, `ARTIFACT_TYPE`, `ARTIFACT_LIMIT`, `DIGEST_FORMAT`, `BYTE_LIMIT`, `CANONICAL_LIMIT`, and existing schema/tree failures. `IntegrityError` inherits `InvalidInputError`. Missing/unreadable files retain standard `OSError` subclasses. No API fetches a URI, overwrites a file, creates a run directory or executes a solver.

## Integration boundary

L0 and `validate-config` continue to report unverified external evidence and missing model coverage. Computing a configuration checksum separately does not authenticate all fields/files mentioned in an audit. In particular, the evaluator does not accept a caller flag asserting that hashes were checked. RUN-01 will compose these primitives with actual immutable storage and fresh evidence reads; FND-08 still owns environment locking and the P2 review.

See the [B-02 report](../benchmarks/B02-content-identity.md) for exact fixtures, observed outcomes and open requirements.
