# Immutable Run Contract — RUN-1.0

**Implemented by:** [RUN-01](../work-items/RUN-01.md) · **Schema:** existing 1.0 · **Profile:** [ENV-1.0](../../requirements/README.md)

## Scope and execution policy

This lifecycle retains two bounded software diagnostics, `lifecycle-receipt` and `lifecycle-failure`, both version 1.0, float64 metadata, empty solver parameters and `SOFTWARE-RUN-01` procedure ID. Their [frozen protocols and examples](../../examples/runs/README.md) test success/failure retention. ANA-07 adds the separately versioned `ANALYTIC-RUN-1.0` plane driver and additive `ANALYTIC-RUN-1.1` spherical driver. The `analytic-plane-field` and `analytic-spherical-field` 1.0 adapters evaluate bounded ideal incident-field functions only; neither calculates body force or trajectory. No arbitrary plugin or callback is exposed.

Execution state, byte integrity, MCLF verdict and a software benchmark comparison are separate. The normal diagnostic completes with **INDETERMINATE** scientific status. A deliberately failed execution has **INVALIDATED** lifecycle post-audit and remains inspectable. Verifying that failure retention works is a software comparison PASS, not successful physics.

The strict scenario reader, experiment/configuration link and actual protocol digest are checked before allocation. Existing L0 pre-audit runs under the real new run ID; INVALIDATED and ALERT block execution. Registered software diagnostics and analytical plane/spherical-field runs may proceed with INDETERMINATE under DEC-003, each with its own fixed limitation. There is no acceptance override. These analytical drivers are not a new numerical solver or physical-result acceptance path.

### ANA-07 plane-field adapter — ANALYTIC-RUN-1.0

`analytic-plane-field` version 1.0 is admitted in both executor and checker. It requires solver precision `complex128`, empty parameters, and equation IDs matched to the frozen family: `EQ-007` for one `B03-*` source and `EQ-008` for two `B04-*` or `B05-*` sources. Source entries must explicitly be schema-1.0 `ideal_plane_wave` records. The homogeneous medium's dynamic viscosity and amplitude attenuation must both be explicit zero; density, sound speed, frequency, direction, peak amplitude, phase and phase-reference position come from the validated Scenario source records. No source is normalized, approximated as hardware, or coupled to the recorded body.

The hash-bound Experiment protocol is a bounded JSON `FIELD-REQUEST-1.0` record with exactly `contract`, `case_id`, `box_min_m`, `box_max_m`, and ordered `coordinates_m`. Its basename is retained exactly in the run bundle. The request box must equal the Scenario domain; `1 <= N <= 256`, `1 <= M <= 2`, and all source, phase and sample-domain checks precede field-array allocation. The runner calls only the existing closed-form one-wave or two-wave kernels. The seed is explicit no-randomness and is unused.

The run stores the four `FIELD-ARRAY-1.0` component records, schema-1.0 FieldResult, and a strict `FIELD-INDEX-1.0`. FieldResult references coordinates, pressure and velocity. The index records the exact FieldResult hash and run/result IDs plus the Pa/m pressure-gradient reference, shape and dtype. The read-only checker verifies hashes, exact output inventory, structural metadata, sample order/coordinates, Scenario frequency, source admission, result/index links and the recorded preflight; it reconstructs the immutable FieldSamples representation but does not re-evaluate the wave equation. Integrity verification is not the frozen-reference numerical comparison, MCLF acceptance, model validation or experimental evidence. The 32-case B-03…B-06 comparison is recorded in the [ANA-07 matrix report](../benchmarks/ANA-07-recorded-field-matrix.md); the additional [numerical sensitivity review](../reviews/ANA-07-numerical-sensitivity-review.md) records its scope and limits. The owner recorded bounded P3 PASS for this analytical-software evidence; physical validation remains NOT ESTABLISHED.

### ANA-07 spherical-field adapter — ANALYTIC-RUN-1.1

`analytic-spherical-field` version 1.0 admits exactly one explicit `ideal_spherical_wave` source for a frozen `B06-*` request and `EQ-010`. Its `SPHERICAL-WAVE-1.0` contract binds center, reference and minimum radii, phase and peak pressure at the reference radius; plane position/normal and piston aperture fields are forbidden. It requires `reference_radius >= minimum_radius > 0`, a pressure limit, homogeneous medium and explicit zero material loss. The full spherical source inputs are compared with the frozen ANA-REF-1.0 case by the independent analyzer. Plane and spherical drivers cannot be mixed or relabeled.

The spherical adapter uses the same bounded source-independent `FIELD-REQUEST-1.0`, component files, FieldResult and FIELD-INDEX shapes. It has its own run policy and scope. The full five-case B-06 extension passed in the 32-case recorded campaign; a fresh B06-AXIAL run reproduced the inputs, field artifacts and metrics. These remain software verification of the ideal outgoing-wave equation only; no physical radiator, scattering, body coupling, force or motion is represented.

### NUM-03 Hasegawa field adapter — HASEGAWA-FIELD-RUN-1.0

`hasegawa-piston-sphere-field` version 1.0 admits only a Scenario 1.1 record of the frozen 25.23 kHz coaxial 10 mm uniformly displaced baffled piston and stationary 25 mm sound-hard sphere, with `EQ-HASEGAWA-1985`, complex128 and no undeclared solver parameters. Scenario 1.0 remains valid for all existing records; its pressure-amplitude fields are not reinterpreted as piston displacement. The source's peak face displacement and phase are converted to complex face velocity under `exp(-iwt)` as `-i*omega*xi*exp(i*phase)`. This is the prescribed ideal source mapping, not transducer calibration.

Its hash-bound `HASEGAWA-FIELD-REQUEST-1.0` contains one gap, an ordered list of 1–256 Cartesian points, explicit order `0..512`, quadrature-order metadata and a point-chunk size equal to the request count. Every sample must satisfy `a <= r < d`, and the exact workload dimensions plus source/environment context enter the solver-free NUM-02 preflight. A matching calibration for the exact clean source revision and ENV-1.0 is required before output-directory creation or solver-array allocation. The recurrence evaluator does not perform Gauss-Legendre integration; the preflight retains that workspace as a conservative allowance and binds its dimension in the calibration record. Tests with synthetic calibration exercise software plumbing only.

The adapter uses the standard four field-component artifacts, FieldResult and FIELD-INDEX. A completed bundle checker verifies exact input/calibration hashes, reconstructs the NUM-02 report from the retained inputs, checks ordered coordinates and cross-links every output descriptor. It does not recalculate the field equation. Missing calibration and exceeded caps refuse before solver execution; a completed software run would still have INDETERMINATE scientific verdict and would not establish P4, measured-field agreement, force, motion or gravity equivalence. This run policy is not yet admitted by `reproduce`.

## Source and environment

`run` locates the checkout containing the executing package. It requires a real committed **clean** Git tree, including no untracked public files, and records its actual revision plus package source-file SHA-256 inventory. Source files must be tracked. It also executes ENV-1.0 verification using the current interpreter and retains the observed packages, interpreter/build/compiler/platform and the three exact lock/inventory files. A second source/environment observation after the driver must agree. A changed observation fails execution and retains the failure.

This initial recorder requires an editable development installation from the checkout. A core-only wheel installed elsewhere cannot supply this source contract. RUN-1.0 does not execute dirty-source patches or installed-wheel source bundles; RUN-02 replay uses the exact committed source revision recorded in the run. Ignored local instructions, CodeGraph, machine settings and generated outputs are not copied into run provenance. Clean Git plus observed bytes is ordinary reproducibility evidence, not adversarial process attestation or independent publisher authentication.

## Inputs, IDs and paths

Supply one Scenario, one Experiment and an explicit integer seed or explicit null/no-randomness choice. The experiment ID, question, observable, acceptance rule and protocol digest must already exist; the recorder does not manufacture these after execution. Protocol references must be a single local basename; URI schemes, absolute paths, directories and path traversal are rejected. Input documents/protocol and stored individual files have a 1 MiB limit and must be stable regular files; symlinks/FIFOs are rejected. Existing FND structural limits also apply.

A fresh UTC-date/UUID run ID is generated before execution. Default directory: `results/<experiment-id>/<run-id>/` under the source checkout. `--output` may select another unused local directory; inside the source checkout it must remain under `results/`. Existing directories, files and symlinks are never reused. The UUID provides identity, not physical randomness; diagnostics do not consume the recorded seed.

The stored `scenario.json` and `experiment.json` preserve the validated input content in the existing JSON representation. Their complete canonical identities bind the supplied content; raw whitespace/key ordering and original YAML spelling are not retained. The protocol file retains the exact supplied bytes under its declared local basename (`protocol.md` for diagnostics; commonly `field-request.json` for ANA-07). The original Experiment reference remains inspectable without remote resolution.

## Preflight and observed resources

Before directory reservation, the software diagnostic estimates:

- One sequential CPU worker, no GPU and zero field samples.
- RAM: the greater of 64 MiB and the current process peak RSS plus 16 MiB of headroom.
- Disk: 2 MiB plus four times the retained input/provenance payload size.
- Recorder wall time: a 1 s estimate, compared with the requested cap.

Compare RAM/disk estimates with both requested caps and available Linux memory/disk. Refuse insufficient budgets before the driver or output directory. The example requests 1 GiB RAM, 16 MiB disk and 30 s. These are diagnostic budgets, not measured solver requirements, calibration of a PDE cost model or operating-system hard limits. Small input validation/provenance observation happens before this allocation estimate.

The analytical policy instead fixes one worker, no GPU, `N<=256`, `M<=2`, no randomness, a 16 MiB bundle ceiling and 30 s cap. Its RAM estimate is twice the observed process peak RSS plus the frozen `4096*N + 4096*M` byte workspace allowance. Its disk preflight reserves the whole 16 MiB bundle allowance. These are bounded analytic-driver caps, not a calibrated PDE cost model; actual bundle bytes and elapsed execution are checked, and any excess is recorded as failure.

Record actual elapsed recorder time, process CPU time (excluding subprocess CPU), logical CPU count, fixed diagnostic backend/no-GPU use, Linux process peak RSS (including earlier imports/work), driver artifact bytes, expected output, explicit seed policy, terminal UTC timestamp and failure type/code/message. Check elapsed wall time after the bounded driver; no arbitrary or long-running solver is allowed by this implementation. Final publication time is excluded from `runtime_s`. Per-child/GPU accounting, numerical arrays, calibrated forecasts and hard workload timeouts remain later resource work.

## File layout and publication

| File | Content / role |
|---|---|
| `running.json` | Initial schema-1.0 manifest; published first and never rewritten |
| `scenario.json`, `experiment.json`, protocol basename | Frozen input records and exact protocol/request bytes |
| `source.json` | Actual clean revision and source inventory |
| `environment.json`, `*-linux-py312.lock`, `environment-linux-py312.json` | Observed environment and complete lock inputs |
| `preflight.json` | Estimate and scope |
| `audit-pre.json` | Unmodified L0 detailed pre-audit; evaluated before manifest construction |
| `receipt.json` or `partial.json` | Diagnostic receipt or retained partial progress |
| `field-*.json` | For an analytical run: four component files, schema-1.0 FieldResult and FIELD-INDEX-1.0 |
| `execution.json` | Structured execution log: terminal state, timing/resources, seed usage and error |
| `audit-post.json` | RUN-POST-1.0 lifecycle integrity/coverage audit |
| `manifest.json`, `manifest.sha256` | Final manifest and exact raw-file checksum; separately retain the checksum if needed |

Each file is written to a new same-directory temporary file, flushed/fsynced and published by exclusive hard link; an existing destination fails. Directory metadata is fsynced. This provides complete-file publication on the tested local Linux filesystem, without a whole-directory transaction or an adversarial-filesystem security guarantee. Output references include the preserved initial manifest. No file is replaced to update a state.

Once reserved, a failure during initialization/final storage can leave an incomplete directory; preserve it. After initialization, driver exceptions produce `failed`, KeyboardInterrupt produces `aborted`/exit 130, and the CLI maps SIGTERM to `aborted`/exit 143 during the guarded execution. The previous SIGTERM handler is restored. Termination before initialization, SIGKILL, machine failure or unusable storage may prevent a final manifest; an initial/partial record is never reclassified as completed. There is no automatic resume or rewrite. A retry uses a new run ID/directory.

## Lifecycle post-audit and check semantics

`audit-post.json` uses **RUN-POST-1.0**, a separate stored audit envelope. Its driver-specific `scope` and `limitations` are checked against the admitted policy; an analytical record mislabeled as a software diagnostic fails `check`. Its predicates are:

| Predicate | Outcome |
|---|---|
| Input/output bytes still match their stored references; source/environment observation agrees; required receipt exists; driver finishes within its wall cap | Software execution may complete |
| Driver failure, interruption, missing output, hash/source/environment mismatch or elapsed-cap failure | Failed/aborted state and INVALIDATED lifecycle verdict |
| Physical-result/model coverage | Always unavailable: a completed diagnostic remains INDETERMINATE |

This envelope occupies the manifest's artifact-backed `mclf_post` check-state slot with explicit scope. It is **not** a schema-1.0 `MclfReport`, does not use R-001…R-010 as new predicates, and does not alter the existing L0 evaluator's required FieldResult/ForceResult rules. Physical postchecks, balances, convergence and experimental comparisons remain unavailable. A receipt is never disguised as a FieldResult to obtain acceptance.

`check` is read-only. It verifies the final manifest checksum, every indexed local artifact, exact required input/output set, record identities, scenario/experiment/protocol links, preserved initial manifest, source/environment declarations, pre/post verdict links, terminal failure code and driver-specific artifacts. For analytical runs it also applies the checks described above, without recalculating the field or comparing it with ANA-REF. It rejects path traversal, symlinked referenced files, duplicate references and unindexed final files. Missing/corrupt records fail visibly. An initial record with verified inputs but no final manifest reports INCOMPLETE and unknown completion/liveness. A final manifest missing its checksum reports RUN_INCOMPLETE. No inspection resumes execution, consults remote references or authenticates the current checkout against an older run.

A checksum stored beside a file can detect accidental change but can also be replaced with it. `check --sha256 <retained-digest>` binds the manifest to a separately retained expected value. Without such a trust anchor, internal consistency is not independent proof of origin. RUN-02 reconstructs available committed source and its lock-bound ENV-1.0 profile; it does not authenticate a publisher or retrieve missing Git objects.

## CLI outcome contract

The run, check and reproduce commands support `--json` (one object on stdout; expected failures have an error record). Human mode emits the same readable JSON on stderr for nonzero outcomes. Existing `validate-config` and its interface version are unchanged.

| Exit | Meaning |
|---|---|
| 1 | Invalid input/model/resources/provenance/integrity, failed execution, or inspection of failed/aborted execution |
| 2 | CLI usage error, including omitted seed policy |
| 3 | Completed but scientifically INDETERMINATE diagnostic, verified completed diagnostic, or an incomplete initial bundle |
| 4 | Filesystem failure, including unavailable/unwritable evidence |
| 130 / 143 | Recorded interruption during `run` (SIGINT/KeyboardInterrupt or CLI SIGTERM) |

No physical acceptance/exit-0 run is available. Inspect `execution_status`, `integrity` when checking, `verdict`, `error` and `scope` separately. A failed source/environment prerequisite creates no execution record; an error after reservation preserves the available directory.

## RUN-02 replay, comparison and report contract

The CLI command is aura reproduce <run> with optional --output <new-run-directory>, --report-dir <new-report-directory> and --json options. It accepts only a completed, integrity-verified analytical field run. Failed or aborted records and any bundle with changed input, source, lock or output bytes are rejected before allocating a replay directory. Each replay receives a new RUN ID and immutable directory. The original bundle is never modified.

The command checks out the source commit recorded in the parent bundle in a temporary detached Git worktree. The caller's dirty or untracked working-tree changes are not copied or executed. The source commit must already exist locally, and its package-file digests and environment lock bytes must match the parent. The command creates a fresh virtual environment, installs only the hash-pinned ENV-1.0 development lock, installs the committed package without dependency resolution, and runs the profile verifier. Missing commit objects, registry access, compatible interpreter, or matching dependencies stop replay before solver execution.

ENV-1.0 requires CPython 3.12.14 on Linux x86_64 with the exact locked distribution versions and glibc at least 2.28. It records kernel, libc, Python build and platform details but does not freeze those host snapshots. Replay reports every runtime-snapshot difference; profile violations still reject execution. This follows the supported-profile contract in D05 and avoids treating a supported Debian host as incompatible solely because its kernel or glibc minor version differs from the recorded machine.

RUN-REPLAY-1.0 separates three results. The coordinates, pressure, velocity and pressure-gradient artifact bytes must match exactly. ANA-07 normalized E_max, E_rms, component counts and criteria must also be exactly equal between parent and replay; no cross-run numeric tolerance is defined. The independent ANA-REF-1.0 comparison retains its own frozen tolerance and PASS/FAIL status. When the stored case has no admitted reference, the bitwise result may still be reported, while metric and reference comparison remain INDETERMINATE. None of these software checks establishes physical model validity.

The ANA-07 comparison runs inside the new ENV-1.0 virtual environment from the same detached worktree as the replay. Its implementation, independent-reference module and frozen case fixture digests are recorded in the report. This prevents metrics from being silently computed by a different caller checkout.

The report directory contains replay-report.json, replay-report.md and artifact-index.json. The index binds the report files to the exact parent and replay RUN IDs and manifest hashes. Reports remain outside RUN-1.0 bundles because the original run record is immutable. Generated replay data and reports belong under ignored results storage and are not committed. The command returns zero when replay and applicable reproducibility checks pass, one for a failed integrity/execution/comparison check, and three when replay is complete but no reference permits a metric comparison.

This implementation replays only the recorded committed revision under ENV-1.0. Dirty-source patches, alternate interpreters, cross-backend tolerances, and runs outside the admitted analytical field drivers are unsupported and remain explicit limitations.

## D07 mapping and remaining gates

Existing RunManifest fields carry IDs, hypothesis/observable, start time, source/config identity, environment lock/platform, solver/precision, seed, requested caps, input/output references, runtime metric, pre/post states, failure code and notes. Referenced Experiment carries the complete observable definition/window, acceptance and uncertainty plan. Referenced source/environment/preflight/execution records carry detailed inventory, end time, estimates and observations. Physical declarations remain in the hashed Scenario. Convergence is an empty list because these software diagnostics calculate no physical approximation; it is not zero numerical error.

FR-002 ordering and FR-010 identity have real recorder integration for the bounded diagnostics and ANA-07 plane/spherical-field adapters. FR-009 has a preserved pre-audit plus scoped lifecycle postcheck; independent numerical field comparison is complete for the frozen B-03…B-06 cases and the owner recorded bounded P3 PASS. FR-011 has a diagnostic estimate and the bounded analytical estimate above. RUN-02 adds broader replay/evidence comparison. Physical forces, motion/control, independent scientific review, microgravity evidence and larger-object models remain at their own gates.

## Implementation references

The publication primitive follows [Python's `os.link`/`fsync` interfaces](https://docs.python.org/3.12/library/os.html) and Linux [`link(2)`](https://man7.org/linux/man-pages/man2/link.2.html), whose existing-destination behavior prevents replacement. The [Python signal contract](https://docs.python.org/3.12/library/signal.html) governs main-thread handler registration and explains why interruption can arrive between operations; the partial-record policy is therefore explicit rather than claiming an indivisible whole-run transaction. These are software implementation sources, not new physical equations.
