# B-02 — Canonical and File Identity Verification

**Protocol:** AURA-C14N-1 / AURA-IDENTITY-1 · **Date:** 2026-10-02 · **Review:** implementer artifact review

## Question and method

Verify exact byte representation, content digests and declared configuration links under the frozen [FND-07 protocol](../work-items/FND-07.md). This extends [FND-05's structural B-02 report](B01-B02-foundation-verification.md), which explicitly left canonical identity pending. The [contract](../research/content-identity.md) specifies all exclusions, numeric policy, caps and failure behavior before claiming equivalence.

Expected canonical strings are hand-authored [golden fixtures](../../tests/fixtures/identity/README.md). The SolverSpec digest was independently obtained using `sha256sum` on the fixed preimage; raw-file cases use the known SHA-256 digests of empty bytes and `abc`. Tests compare exact bytes, digests and named errors, without a numeric tolerance. No physical operating point, measured data or scientific run is involved.

## Observed results

| Test group | Evidence | Outcome and scope |
|---|---|---|
| Golden text and full document digest | `test_identity.py::test_hand_authored_canonical_bytes`, independent solver digest case | Exact agreement, including Unicode escaping and type distinctions |
| Numeric policy | Exact encode/decode, decimal-context, nearby-float and large-integer cases | 1/1.0 and numeric zero unify; booleans, distinct adjacent numbers and large seed integers do not collapse |
| Round trip / ordering | JSON/YAML scenarios; recursively reversed object keys | Full and projected identities agree under key reordering; array order is retained |
| Changed input | 21 individual changes across medium, body, source, solver, domain, gravity, target and nested provenance | Both scenario digests change |
| Declared root exclusions | Scenario ID, resource cap, root provenance note | Full digest changes; conservative projection stays equal |
| Larger geometry and optional inertia | Additional manufactured box, order reversal and inertia addition | Identity captures the new declarations; no model applicability claim |
| Units and invalid input | Explicit length conversion, unknown version, malformed excluded metadata, nonfinite/tree/size cases | Full validation still required; no silent unit conversion or exclusion-based bypass |
| Manifest/experiment links | Known matching records plus changed IDs/solver/resources/config/claim/hypothesis | Matching declarations verified; mismatches retain exact error/path |
| Full versus projected config | Projection substituted for full manifest digest | Rejected with HASH_MISMATCH |
| Manifest metadata | Timestamp, lock location and seed changes | Manifest identity changes; scenario identity stays independent |
| File tampering | Changed byte, truncated file, newline addition and empty replacement | Rejected against retained `abc` digest |
| File limits and stability | Byte caps, chunk bounds, special files, symlink, read-time rewrite/replacement/growth/removal and descriptor cleanup | Bounded regular-file policy enforced; ordinary concurrent changes rejected |
| Scientific/evidence separation | Fresh L0 audit after configuration-only verification | INDETERMINATE and HASH_UNCHECKED remain; no external evidence or model coverage inferred |

The initial focused suite passed **97 tests**. Review added three cases for collection/geometry/inertia preservation, invalid excluded fields and large seed precision. The final focused suite passed **100 tests in approximately 1.7 seconds**. One initial export-order lint issue was corrected; no test failure occurred in the recorded executions. The complete suite and exact delivery CI are recorded in FND-07 and its delivery report.

## Decision and open integration

**B-02 canonical/configuration/file-integrity comparison: PASS within the tested contract.** The earlier structural checks remain in the full suite. This is exact software verification, not scientific model validation or an independently reviewed research result.

Environment-file byte verification is supported, but an environment has not been locked/recreated by this card. Hash agreement requires a trustworthy separately retained expected digest and does not establish publisher identity. Files may change after reading, and the checker is not an adversarial-filesystem security boundary.

RUN-01 still must store immutable manifests, bind every input/output to actual bytes, verify source/environment evidence and enforce pre/post checks in the real lifecycle. No run writer was added and no existing output could be overwritten by these APIs. FND-08 owns the remaining P2 environment and gate review; the owner's requested explanation remains before RUN-01/P3.

Reproduce with `pytest -q tests/test_identity.py tests/test_artifacts.py`, then the complete Quality workflow. The fixture README gives the independent hash command. Exact source revision and remote CI link are supplied with delivery; temporary file names are not scientific run IDs.
