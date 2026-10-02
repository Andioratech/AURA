# Immutable Diagnostic Run Contract — RUN-1.0

**Implemented by:** [RUN-01](../work-items/RUN-01.md) · **Schema:** existing 1.0 · **Profile:** [ENV-1.0](../../requirements/README.md)

## Scope and execution policy

This lifecycle records **two bounded software diagnostics**, `lifecycle-receipt` and `lifecycle-failure`, both version 1.0, float64 metadata, empty solver parameters and `SOFTWARE-RUN-01` procedure ID. Their [frozen protocols and examples](../../examples/runs/README.md) test success/failure retention. They calculate no acoustic field, force or trajectory. The scenario's manufactured physical values are preserved but not evaluated. No plugin/callback/unsupported scientific model is exposed through the CLI.

Execution state, byte integrity, MCLF verdict and a software benchmark comparison are separate. The normal diagnostic completes with **INDETERMINATE** scientific status. A deliberately failed execution has **INVALIDATED** lifecycle post-audit and remains inspectable. Verifying that failure retention works is a software comparison PASS, not successful physics.

The strict scenario reader, experiment/configuration link and actual protocol digest are checked before allocation. Existing L0 pre-audit runs under the real new run ID; INVALIDATED and ALERT block execution. Only the registered diagnostics may proceed with INDETERMINATE, under DEC-003 and the fixed software-only limitation. There is no acceptance override. Registering analytical models in P3 requires an explicit applicability/execution-policy review.

## Source and environment

`run` locates the checkout containing the executing package. It requires a real committed **clean** Git tree, including no untracked public files, and records its actual revision plus package source-file SHA-256 inventory. Source files must be tracked. It also executes ENV-1.0 verification using the current interpreter and retains the observed packages, interpreter/build/compiler/platform and the three exact lock/inventory files. A second source/environment observation after the driver must agree. A changed observation fails execution and retains the failure.

This initial recorder requires an editable development installation from the checkout. A core-only wheel installed elsewhere cannot supply this source contract. Dirty-source patch/snapshot execution, installed-wheel source bundles and replay remain RUN-02. Ignored local instructions, CodeGraph, machine settings and generated outputs are not copied into run provenance. Clean Git plus observed bytes is ordinary reproducibility evidence, not adversarial process attestation or independent publisher authentication.

## Inputs, IDs and paths

Supply one Scenario, one Experiment and an explicit integer seed or explicit null/no-randomness choice. The experiment ID, question, observable, acceptance rule and protocol digest must already exist; the recorder does not manufacture these after execution. Protocol paths are local and relative to the supplied experiment; URI schemes and absolute protocol paths are rejected. Input documents/protocol and stored individual files have a 1 MiB limit and must be stable regular files; symlinks/FIFOs are rejected. Existing FND structural limits also apply.

A fresh UTC-date/UUID run ID is generated before execution. Default directory: `results/<experiment-id>/<run-id>/` under the source checkout. `--output` may select another unused local directory; inside the source checkout it must remain under `results/`. Existing directories, files and symlinks are never reused. The UUID provides identity, not physical randomness; diagnostics do not consume the recorded seed.

The stored `scenario.json` and `experiment.json` preserve the validated input content in the existing JSON representation. Their complete canonical identities bind the supplied content; raw whitespace/key ordering and original YAML spelling are not retained. `protocol.md` retains the exact supplied protocol bytes. Its copied name is local; the original experiment reference is preserved without attempting remote resolution on later inspection.

## Preflight and observed resources

Before directory reservation, the fixed diagnostic estimates:

- One sequential CPU worker, no GPU and zero field samples.
- RAM: the greater of 64 MiB and the current process peak RSS plus 16 MiB of headroom.
- Disk: 2 MiB plus four times the retained input/provenance payload size.
- Recorder wall time: a 1 s estimate, compared with the requested cap.

Compare RAM/disk estimates with both requested caps and available Linux memory/disk. Refuse insufficient budgets before the driver or output directory. The example requests 1 GiB RAM, 16 MiB disk and 30 s. These are diagnostic budgets, not measured solver requirements, calibration of a PDE cost model or operating-system hard limits. Small input validation/provenance observation happens before this allocation estimate.

Record actual elapsed recorder time, process CPU time (excluding subprocess CPU), logical CPU count, fixed diagnostic backend/no-GPU use, Linux process peak RSS (including earlier imports/work), driver artifact bytes, expected output, explicit seed policy, terminal UTC timestamp and failure type/code/message. Check elapsed wall time after the bounded driver; no arbitrary or long-running solver is allowed by this implementation. Final publication time is excluded from `runtime_s`. Per-child/GPU accounting, numerical arrays, calibrated forecasts and hard workload timeouts remain later resource work.

## File layout and publication

| File | Content / role |
|---|---|
| `running.json` | Initial schema-1.0 manifest; published first and never rewritten |
| `scenario.json`, `experiment.json`, `protocol.md` | Frozen input records and actual protocol bytes |
| `source.json` | Actual clean revision and source inventory |
| `environment.json`, `*-linux-py312.lock`, `environment-linux-py312.json` | Observed environment and complete lock inputs |
| `preflight.json` | Estimate and scope |
| `audit-pre.json` | Unmodified L0 detailed pre-audit; evaluated before manifest construction |
| `receipt.json` or `partial.json` | Diagnostic receipt or retained partial progress |
| `execution.json` | Structured execution log: terminal state, timing/resources, seed usage and error |
| `audit-post.json` | RUN-POST-1.0 lifecycle integrity/coverage audit |
| `manifest.json`, `manifest.sha256` | Final manifest and exact raw-file checksum; separately retain the checksum if needed |

Each file is written to a new same-directory temporary file, flushed/fsynced and published by exclusive hard link; an existing destination fails. Directory metadata is fsynced. This provides complete-file publication on the tested local Linux filesystem, without a whole-directory transaction or an adversarial-filesystem security guarantee. Output references include the preserved initial manifest. No file is replaced to update a state.

Once reserved, a failure during initialization/final storage can leave an incomplete directory; preserve it. After initialization, driver exceptions produce `failed`, KeyboardInterrupt produces `aborted`/exit 130, and the CLI maps SIGTERM to `aborted`/exit 143 during the guarded execution. The previous SIGTERM handler is restored. Termination before initialization, SIGKILL, machine failure or unusable storage may prevent a final manifest; an initial/partial record is never reclassified as completed. There is no automatic resume or rewrite. A retry uses a new run ID/directory.

## Lifecycle post-audit and check semantics

`audit-post.json` uses **RUN-POST-1.0**, a separate stored audit envelope. Its predicates are:

| Predicate | Outcome |
|---|---|
| Input/output bytes still match their stored references; source/environment observation agrees; required receipt exists; driver finishes within its wall cap | Software execution may complete |
| Driver failure, interruption, missing output, hash/source/environment mismatch or elapsed-cap failure | Failed/aborted state and INVALIDATED lifecycle verdict |
| Physical-result/model coverage | Always unavailable: a completed diagnostic remains INDETERMINATE |

This envelope occupies the manifest's artifact-backed `mclf_post` check-state slot with explicit scope. It is **not** a schema-1.0 `MclfReport`, does not use R-001…R-010 as new predicates, and does not alter the existing L0 evaluator's required FieldResult/ForceResult rules. Physical postchecks, balances, convergence and experimental comparisons remain unavailable. A receipt is never disguised as a FieldResult to obtain acceptance.

`check` is read-only. It verifies the final manifest checksum, every indexed local artifact, exact required input set, record identities, scenario/experiment/protocol links, preserved initial manifest, source/environment declarations, pre/post verdict links, terminal failure code and diagnostic receipt. It rejects path traversal, symlinked referenced files, duplicate references and unindexed final files. Missing/corrupt records fail visibly. An initial record with verified inputs but no final manifest reports INCOMPLETE and unknown completion/liveness. A final manifest missing its checksum reports RUN_INCOMPLETE. No inspection resumes execution, consults remote references or authenticates the current checkout against an older run.

A checksum stored beside a file can detect accidental change but can also be replaced with it. `check --sha256 <retained-digest>` binds the manifest to a separately retained expected value. Without such a trust anchor, internal consistency is not independent proof of origin. Archived source availability, environment reconstruction and actual replay remain RUN-02.

## CLI outcome contract

Both new commands support `--json` (one object on stdout; expected failures have an error record). Human mode emits the same readable JSON on stderr for nonzero outcomes. Existing `validate-config` and its interface version are unchanged.

| Exit | Meaning |
|---|---|
| 1 | Invalid input/model/resources/provenance/integrity, failed execution, or inspection of failed/aborted execution |
| 2 | CLI usage error, including omitted seed policy |
| 3 | Completed but scientifically INDETERMINATE diagnostic, verified completed diagnostic, or an incomplete initial bundle |
| 4 | Filesystem failure, including unavailable/unwritable evidence |
| 130 / 143 | Recorded interruption during `run` (SIGINT/KeyboardInterrupt or CLI SIGTERM) |

No physical acceptance/exit-0 run is available. Inspect `execution_status`, `integrity` when checking, `verdict`, `error` and `scope` separately. A failed source/environment prerequisite creates no execution record; an error after reservation preserves the available directory.

## D07 mapping and remaining gates

Existing RunManifest fields carry IDs, hypothesis/observable, start time, source/config identity, environment lock/platform, solver/precision, seed, requested caps, input/output references, runtime metric, pre/post states, failure code and notes. Referenced Experiment carries the complete observable definition/window, acceptance and uncertainty plan. Referenced source/environment/preflight/execution records carry detailed inventory, end time, estimates and observations. Physical declarations remain in the hashed Scenario. Convergence is an empty list because these software diagnostics calculate no physical approximation; it is not zero numerical error.

FR-002 ordering and FR-010 identity now have real recorder integration for the bounded diagnostics. FR-009 has preserved pre-audit plus a scoped lifecycle postcheck; scientific post-audit integration remains pending. FR-011 has only this diagnostic estimate. RUN-02 adds replay/evidence comparison; ANA-01 defines real field outputs and reference cases. Physical forces, motion/control, independent scientific review, microgravity evidence and larger-object models remain at their own gates.

## Implementation references

The publication primitive follows [Python's `os.link`/`fsync` interfaces](https://docs.python.org/3.12/library/os.html) and Linux [`link(2)`](https://man7.org/linux/man-pages/man2/link.2.html), whose existing-destination behavior prevents replacement. The [Python signal contract](https://docs.python.org/3.12/library/signal.html) governs main-thread handler registration and explains why interruption can arrive between operations; the partial-record policy is therefore explicit rather than claiming an indivisible whole-run transaction. These are software implementation sources, not new physical equations.
