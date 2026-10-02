# FND-07 — Canonical Content Identity

**State:** DONE · **Protocol frozen:** 2026-10-02 · **Depends on:** FND-06

## Question and scope

Can equivalent supported representations have one deterministic content identity, while changed configuration or file content fails verification against a previously retained digest?

Starting revision: `569c3ae386144999d67ccf291ce0a4c3907ac20a`. Authority: D00, D02, D07, D08 and the P2 FND-07 card. Reuse schema 1.0 and the existing immutable RunManifest model. Implement pure canonical serialization and identity/link checks under `schema/`, plus bounded read-only file hashing. No simulation lifecycle, run allocation, manifest writer, source checkout verification or new CLI is introduced. RUN-01 still owns durable immutable run storage after the owner's explanation checkpoint.

## Frozen protocol

- Define AURA-C14N-1: sorted Unicode-code-point keys, retained array order and string content, ASCII-escaped JSON, no optional whitespace/newline, finite built-in numeric values. Integers remain exact; floats use their exact decimal value (`Decimal.from_float`, without arithmetic/context rounding), trim trailing fractional zeros and normalize signed zero to 0. Numerically equal integer/float values share an encoding; bool remains distinct. This is a project contract, not RFC 8785/JCS. Preserve original bytes separately when original spelling matters.
- Keep the existing 1 MiB input/tree limits; bound expanded canonical output to 16 MiB. No tolerance, unit conversion or approximate numeric equality during hashing. Validate full typed documents before computing document identity; only canonical SI enters scenario hashing.
- Domain-separate SHA-256 digests with `AURA-C14N-1\n<scope>\n` before canonical bytes. Freeze scopes `document` and `scenario-inputs`. Both include schema version. Raw files use plain SHA-256 over their bytes, with no prefix, so standard tools can reproduce artifact/environment-lock digests.
- Return a versioned immutable ScenarioIdentity with full document digest and conservative input-projection digest. The projection excludes **only** root `/id`, `/resources`, `/provenance`; nested IDs/material names/provenance, solver parameters, geometry, boundaries, gravity and target remain included. It is not a cache key, a proof of physical equivalence or a substitute for full configuration identity. Do not remove arbitrary nested fields by name.
- `RunManifest.configuration_sha256` and `Experiment.scenario_sha256` mean the full `document` digest under this contract for newly created records. Existing historical fixture digests were unauthenticated placeholders; do not rewrite them or claim migration of scientific runs. Existing artifact/environment `sha256` fields mean raw file bytes. No accepted scientific run exists to migrate.
- Verify manifest/scenario declared ID, complete solver specification, resource declaration and full configuration digest. Check experiment linkage separately only if supplied; no inferred metadata/defaults. A valid-looking digest is not authenticated until compared with actual content. Do not auto-resolve URIs or fetch files.
- File helpers require an explicit nonnegative byte cap, stream regular files in bounded chunks, reject special files, and detect ordinary concurrent changes with descriptor/path metadata plus byte count. A digest does not authenticate its publisher or prove the file cannot change later. Verification requires an independently retained expected digest.
- All helpers are read-only and create no run/artifact. Keep L0's HASH_UNCHECKED and the CLI's INDETERMINATE behavior until an actual evidence-reading integration is implemented. These primitives must not silently promote audit coverage.

## Verification fixed before implementation

Exact bytes/digests/codes only, no numerical tolerance. Use hand-authored canonical byte fixtures, standard SHA-256 known answers and independent `sha256sum` comparison on frozen literals; do not derive expected bytes through the encoder under test. Check key reorder, JSON/YAML round trip, integer/float/zero policy, distinct nearby numbers/large integers, Unicode, array order, all scenario input branches, explicit SI conversion before validation, config/manifest mismatch, changed/truncated/missing files, caps, special files and read-only behavior. Test common concurrent-change detection without claiming resistance to an adversarial filesystem.

CPU-only manufactured records and temporary files; no scientific runs. Target full suite below 30 seconds, investigate above 60 seconds. Source review: Python 3.12 documentation for [exact decimal conversion](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.from_float), [SHA-256](https://docs.python.org/3.12/library/hashlib.html), and [descriptor operations](https://docs.python.org/3.12/library/os.html#os.open), accessed 2026-10-02. No physical model is selected.

## Results and next gate

Delivered [encoding/identity contract](../research/content-identity.md), [canonical encoder](../../src/aura/schema/canonical.py), [typed identity/link checks](../../src/aura/schema/identity.py), [read-only artifact checks](../../src/aura/artifacts.py), [golden fixtures](../../tests/fixtures/identity/README.md) and [B-02 verification report](../benchmarks/B02-content-identity.md). Existing schema 1.0 and RunManifest fields are retained; no lifecycle or run writer was created.

The first focused run passed **97 tests**. Ruff found one unsorted `__all__` list, which was corrected. Review added collection/box/inertia, invalid excluded-field and large-seed checks: **100 focused tests passed in approximately 1.7 seconds**. The complete suite passed **761 tests in approximately 12.2 seconds** on Linux/Python 3.12.14. No test failure occurred in these recorded executions. No production equation, numeric tolerance or dependency changed.

The independently hashed hand-written solver fixture matched `ca3f7514c34fd66f9c140f92e0e307e5f1ca99cfd0e9122a3e530cb3fd908433`. JSON/YAML/key-reordered inputs retained identities; all 21 changed-input cases changed both digests. Three declared root metadata changes altered the full digest while retaining the conservative projection. File tampering, truncation and ordinary read-time changes were rejected with documented outcomes. Manifest/config mismatches could not substitute a projected digest for the full configuration digest.

Artifact self-review confirms bounded read-only behavior, exact expected bytes/codes, named exclusions, historical placeholder preservation and no automatic audit promotion. Canonical bytes can exceed the ordinary reader's cap after exact float expansion; this limit is documented and the display serializer remains separate. Hash integrity is not publisher authentication, full environment reproduction, a cache-equivalence certificate or physical validation. The test-only larger box establishes representation/identity behavior only.

**FND-07 is DONE; FND-08 is READY.** B-02 identity comparison passes within this contract; full FR-010 lifecycle/evidence reproduction remains incomplete. The complete local Quality workflow, links, owner/staged review and exact remote CI are delivery checks reported with the commit. P2 remains ACTIVE. Next work locks/reviews the environment and assembles the P2 gate evidence; the owner is to be briefed before RUN-01/P3.
