# MCLF L0 Rule Register

**Registry:** L0-1.0 · **Date:** 2026-10-02 · **Task:** FND-04 · **Scope:** declaration/metadata audit

Authority: [D02](../D02-mclf.md), [D08](../D08-software-contracts.md), [schema contract](../research/schema-contract.md), [CONV-1.0](../research/si-and-conventions.md). This register defines software policy; it adds no physical equation, performance threshold or model approval. The immutable executable register is [rules.py](../../src/aura/mclf/rules.py).

## Predicates and coverage

Every check reports its ID, outcome, code, affected field path and explanation. The detailed envelope carries the registry and software versions plus the rule predicates, default failure severity, assumptions, affected field patterns and tolerance definitions. The report preserves lower-priority findings alongside the aggregate.

| Rule | Predicate and affected data | Hard failure examples | Coverage limit |
|---|---|---|---|
| R-001 | Known scenario/manifest/field/force envelope, version, types and fields | Unsupported schema, unknown field, boolean physical number, unsafe Python tree | Structural schemas are shared with FND-02; this is not independent physical validation |
| R-002 | All fields required by the selected record are present | Missing gravity, medium temperature or required result field | Missing unsupported external evidence is reported separately, not invented |
| R-003 | Each declared unit matches the canonical field contract | Density written in an incompatible unit | Explicit FND-03 conversion happens before this audit; no automatic conversion |
| R-004 | Inline numbers fit finite binary64 | NaN/infinity or nonrepresentable integer in input or force output | External field samples are never read here; their finite-value check remains INDETERMINATE |
| R-005 | Required signs, ranges, source limits, time ordering and finite domain bounds hold | Negative density, exceeded declared pressure limit, reversed time window, out-of-domain body center | No material law, complete wall clearance, mass-volume relation or universal pressure limit is inferred |
| R-006 | Fixed vector/array shapes, frames and declared unit orientations agree | Wrong vector length/frame, nonunit quaternion/normal, mismatched sample dimensions | Only CONV-1.0 absolute norm tolerance 1e-12; all other representation checks exact |
| R-007 | Explicit CONV-1.0, peak amplitudes and exp(-iwt) phasors | Mixed RMS/peak or harmonic-sign labels | Does not reconstruct a waveform or repair phases |
| R-008 | Unique collection IDs and agreement of supplied run/scenario/body/field-model/solver links | Duplicate source ID, result for another run/body, mismatched field model or solver specification | Missing manifest and unauthenticated digests/source identity remain INDETERMINATE; hash verification is FND-07/lifecycle work |
| R-009 | A reviewed model capability covers the requested scenario | No hard physical-domain threshold is implemented at this step | Always INDETERMINATE today: no reviewed scientific model exists. No caller-supplied coverage override is accepted |
| R-010 | Selected stage has the required result and preserves adverse result/execution status | Missing/malformed post-result, failed execution, result supplied to a pre-audit, inherited INVALIDATED | Inherited ALERT/INDETERMINATE remain visible; external artifact completeness is unknown. A pre-audit passes only its no-output-requested condition |

Hard contract failures are INVALIDATED. Conditional concerns represented by a supplied force-result ALERT remain ALERT. Missing coverage is INDETERMINATE. An ACCEPTED rule means its stated limited predicate passed, not that the full domain is physically validated. With R-009 uncovered, the current evaluator cannot produce overall scientific ACCEPTED.

Force-model identity is distinct from the scenario's field-solver identity: only a field result must match that solver's model ID/version. Force results must name an existing body and the requested run; their model suitability remains R-009's unresolved coverage.

## Aggregation and incompleteness

Apply D02's order exactly: **INVALIDATED > ALERT > INDETERMINATE > ACCEPTED**. An empty outcome set is INDETERMINATE. Unknown verdict strings are rejected. AuditReport requires all ten ordered unique rules, and its generated immutable checks retain their findings. A hard failure cannot disappear behind an ALERT or unknown-model outcome.

Malformed records that prevent dependent checks receive explicit CHECK_INCOMPLETE findings; their other checks do not receive a guessed pass. Multiple schema and independent scenario cross-field failures are collected. A finite-number/tree failure stops inspection of that unsafe record and preserves the blocking diagnostic.

Per-record input remains bounded to 1 MiB of JSON representation with the existing tree depth/node guards. At most 64 schema errors and 64 findings per rule are retained; exceeding these limits invalidates the audit with AUDIT_LIMIT. Messages longer than 512 characters are marked truncated. Oversized diagnostic paths are represented at the document root with an explicit limit note. These are parser/report limits, not physical bounds. No file, hash, source revision or array content is authenticated by a matching string.

## API and report forms

```python
import json
from pathlib import Path
from aura.mclf import evaluate_scenario

scenario = json.loads(Path("examples/schema/manufactured-scenario.json").read_text())
report = evaluate_scenario(
    scenario,
    report_id="EXAMPLE-AUDIT-01",
    run_id="EXAMPLE-RUN-01",
    stage="pre",
)
assert report.verdict == "INDETERMINATE"
print(report.to_text())
```

`stage` is explicitly `pre` or `post`. Optional `result` is one field/force record; optional `manifest` is a run manifest. The evaluator is pure: it neither mutates the input nor allocates a solver, calls the scientific helpers, opens artifacts or invents a run identity. The example IDs above are manufactured labels, not scientific executions.

- `to_dict()` / `to_json()` return the detailed audit envelope, including assumptions, per-rule findings and version metadata.
- `to_text()` provides the same outcomes and paths for a human reader, with escaped diagnostic text.
- `to_record()` exports the existing version-1.0 MclfReport core. Preserve the detailed envelope alongside this core to retain all rule metadata and field diagnostics.
- `require_accepted()` is an explicit gate helper: INVALIDATED raises `MclfInvalidationError`; ALERT/INDETERMINATE raise `IncompleteEvidenceError`, with stable MCLF verdict codes. It does not block unrelated foundation work. A hand-constructed report is still a declaration; this helper does not authenticate who generated it.

The detailed envelope has `audit_version: L0-1.0`; it is not a new version of the general input document schema and is not loaded by the version-1.0 scenario reader. Report metadata is not cryptographic proof of who ran a checker. Run/commit/environment authentication belongs to FND-07/RUN-01. A supplied ACCEPTED force label cannot bypass R-009 or other checks. Higher L1–L5 checks remain unimplemented.

## Verification and next work

[FND-04](../work-items/FND-04.md) records exact tests, review, limitations and delivery. The [test suite](../../tests/test_mclf.py) covers all severity triples, each applicable rule branch, malformed input, record identity, missing and external results, adverse-label preservation, immutable serialization, diagnostic bounds and no-artifact/no-helper invocation. R-008/R-009 acceptance cannot be demonstrated where their required evidence is unavailable; those branches remain explicitly uncovered.

FND-05 integrates foundation verification and allocation-boundary checks; FND-06 exposes a CLI. These software tasks do not close a physical validation gate or prevent the authorized independent foundation work from continuing.
