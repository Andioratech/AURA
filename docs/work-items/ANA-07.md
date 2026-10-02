# ANA-07 — Reproducible Analytical Field Campaign

**State:** ACTIVE · **Started:** 2026-10-02 · **Depends on:** ANA-06, RUN-01 · **Phase:** P3

## Question and scope

Can the frozen B-03…B-06 analytical field cases be executed through an immutable recorder that saves all required field components, reconstructs them during read-only checking, and binds them to their exact inputs and software environment?

This task connects existing closed-form field functions to recorded runs. It does not add a PDE backend, body scattering, force, motion, control, or physical transducer. The result can verify software against the frozen mathematical references only; it cannot establish agreement with measured water, particle motion, larger-object behavior, or microgravity performance.

Authority: D00, D02, D04, D06–D08, DEC-003/004, ANA-REF-1.0, FIELD-1.0, RUN-1.0, ANA-06 and the P03 phase card. The owner approved this bounded implementation on 2026-10-02 after a plain-language explanation of the recorder/core boundary.

## Frozen architecture

1. Preserve `RUN-1.0` lifecycle receipts as a separate backward-compatible driver. Admit analytical execution by a named, versioned driver in both executor and checker; keep the diagnostic and analytical limitation/status fields distinct.
2. Bind the exact sample list and finite observation box through the already hash-bound `Experiment.protocol` artifact. Define a strict versioned `FIELD-REQUEST-1.0` record with `contract`, immutable `case_id`, `box_min_m`, `box_max_m`, and ordered `coordinates_m`. Reject extra fields, unsupported versions, duplicate case IDs where matrix identity is assembled, malformed triples, nonfinite values, and `N` outside 1…256 before field allocation. The request is input, not a tolerance or mesh parameter.
3. For the first adapter, admit only the existing schema-1.0 `ideal_plane_wave` source records. Map their declared positions, normals, phases, peak amplitudes and common array frequency directly to `PlaneWave`; enforce explicit homogeneous medium and zero material loss. Admit at most two sources and require all source, box, sample, phase-conditioning and resource checks before evaluation. No source normalization or body coupling is allowed.
4. Do not widen `FieldResult` schema 1.0. Store its coordinates, pressure and velocity references as separate hashed component files. Store the required pressure-gradient component in a strict `FIELD-INDEX-1.0` companion with `run_id`, `field_result_id`, `field_result_sha256` and a complete artifact reference (`uri`, `sha256`, unit, logical shape and dtype). The checker reconstructs `FieldSamples` from exactly four bounded, hash-verified files and cross-checks FieldResult, index, scenario frequency, source/request identity and sample ordering.
5. Preflight the bounded workload before allocating/evaluating: `N<=256`, `M<=2`, one CPU worker, no GPU, explicit no-randomness, current ANA-REF-1.0 workspace estimate, <=16 MiB total run bundle, and <=30 s per-run cap. Any uncalibrated or unmet resource requirement fails closed and is retained under the RUN lifecycle rules.
6. Record execution success independently from numerical comparison, model coverage, MCLF status and experimental validation. A recorded field is never labeled physically accepted. Checker success means recorded bytes and links agree; it does not rerun the physics or authenticate the publisher.

## Source-family boundary

The current schema-1.0 source contract admits ideal plane waves and circular pistons; it has no spherical point-source input. ANA-07 may execute plane-source cases only until a versioned, explicit spherical-source input contract is added. Do not encode a spherical source as a piston or plane wave, and do not add unused dummy transducers to make a schema pass. The B-06 campaign, full P3 matrix and P3 gate remain open until a legitimate source-to-Scenario binding is reviewed and admitted. This is a scoped implementation dependency, not a physical-data blocker.

## Frozen comparisons and work sequence

The numeric references, independent derivations and normalized `2048 * 2^-52` comparison budget remain those of [ANA-REF-1.0](../benchmarks/B03-B06-analytical-protocols.md); this task must not recalculate, loosen or reinterpret them. The recorder begins with a bounded B-03…B-05 plane-source slice. B-06 is added only after its input contract exists. Negative, rejection, corruption and replay cases are retained separately from successful matrix cases and do not become scientific configurations.

1. Add and review this task record and exact input/output contracts before code changes.
2. Implement the bounded plane-source adapter, recorder artifacts, and independent checker reconstruction. Keep the existing diagnostic fixtures and behavior unchanged.
3. Add an independent metrics/post-audit layer over the frozen references. The first increment supports only B03-01 at the origin, reporting normalized maximum and RMS errors for pressure, velocity, pressure gradient and derived mean intensity. Extend the frozen case mapping across B-03/B-04/B-05 before claiming matrix coverage. Include actual SI scales, failed points, mean flux and the applicable model-local ANA-06 energy ledger; never upgrade physical status.
4. Admit and review the spherical input/source binding as a separately versioned extension. Then execute the frozen B-03…B-06 matrix through the recorder, retaining failures and resource observations.
5. Reproduce the preselected case from stored inputs, generate plots from checked machine-readable metrics, compare plot data to those metrics, and assemble the P3 gate review. If any required family or post-audit is unavailable or fails its frozen criterion, P3 stays open and no P4 solver is promoted.

## Acceptance and failure routes

Task acceptance requires every selected recorded case to pass input admission, immutable bundle checks, independent field-component comparisons, the relevant model-local post-audit and a fresh reproduction. All failures, warnings and uncovered domains remain visible. Full numerical/model validation and experimental water comparison remain `INDETERMINATE` absent matched independent measurements and uncertainty evidence.

- Unsupported source/schema or model domain: F-03; no relabeling or fallback.
- Field mismatch, sign or phase error: F-01/F-04; preserve the original run and compare every failed component.
- Resource cap or preflight failure: F-05; retain the typed reason and do not silently enlarge caps.
- Bundle/index/provenance/reproduction mismatch: F-09/F-11; reject promotion and inspect bytes/source identity.
- Two consecutive failures from the same cause require a root-cause record before a third feature attempt.

## Traceability and delivery

- Equations: EQ-006…EQ-010 as applicable; exact case mapping is in ANA-REF-1.0.
- Primary source and regime: [analytical source review](../research/analytical-source-review.md), [plane-wave contract](../research/plane-wave-kernel.md), [spherical-wave contract](../research/spherical-wave-kernel.md).
- Code targets: initial recorder in `src/aura/runs/analytic.py`, `execute.py`, `check.py`; independent metrics/post-audits in future `src/aura/analysis/` modules.
- Evidence outputs: immutable ignored run bundles; machine-readable metrics; plots; numerical report; artifact review; P3 gate review; refreshed board, traceability, capability README and continuity checkpoint.
- Before every incremental commit: full current local Quality, exact latest remote CI, staged/private diff review, `git diff --check`, internal links, and owner identity. After each push verify Quality for that exact commit. Generated results, local instructions and `.codegraph/` remain outside Git.

## Initial status

**Active; the bounded plane recorder and its scope correction are published in `4d35bf4` and `0fa1114`.** The driver admits one B-03 source or two B-04/B-05 sources, binds the hash-frozen sample request, writes four component records plus FieldResult/FIELD-INDEX, and verifies the bundle without re-evaluating the equations. Seven synthetic lifecycle integration cases exercise one-source recording, two-source standing-wave/interference preservation, component tamper rejection, wrong post-scope rejection, unsupported-piston refusal and out-of-box request rejection. Their provenance is deliberately mocked, so they are not scientific runs or P3 evidence.

The clean-source smoke bundle `RUN-20261002-b1e2f315f5b94c099f8fc56c5ed1596e` (manifest SHA-256 `edc3a71b1149cbf4cad5f18a4bd517921a9bec8518b3a79aafde9f2c61be637f`) is integrity verified. The first independent recorded comparison now covers **B03-01 only**, at the origin, against the unchanged ANA-REF-1.0 criterion `2048 × 2^-52`. Pressure, three velocity components, three gradient components and three derived mean-intensity components all pass; maximum and RMS normalized errors are zero for these exact origin values. The mean intensity is `(1.3333333333333334e-6, 0, 0) W/m²`. The ignored local report is `results/verification/ANA-07/ANA07-METRICS-B03-01-0fa1114.json`; its digest is recorded in the matching sidecar and the report binds the analyzer source checksum. This is a manufactured analytic software comparison in the declared homogeneous, lossless ideal-plane model, not measured water, physical validation, or P3 closure. Other B-03 points, B-04/B-05 recorded comparisons, post-audits, source-family admission and full campaign remain open. Local focused lifecycle suite: 136 passed; complete current Quality and exact remote CI must be run for the implementation increment before publishing it. The owner identity is configured as `JuanFelipeLH <felipelamos2003@gmail.com>`.

The first clean-source B-03-01 smoke execution on that commit completed in 1.18 s and stored all six field outputs, but its `audit-post.json` and API summary incorrectly reused the diagnostic-only scope. The following implementation change makes both scopes driver-specific and rejects the preserved old bundle with `RUN_AUDIT`. Run ID: `RUN-20261002-631952b161ab4ae2887087c2ffcba739`; manifest SHA-256: `154b0395d6813179fc45cc17b3e6447e78b6d772bdf7890d7f93e4e162cdda6b`; ignored local bundle: `results/verification/ANA-07/RUN-ANA07-SMOKE-4d35bf4/`. This was an integration attempt only, not a numeric comparison, scientific result or P3 evidence. It remains unchanged; repeat the smoke execution after publishing the correction.

## Published-source outcome

Commit [`84da8ce53c54c95f2dc6fbd22cb083441fe8821b`](https://github.com/Andioratech/AURA/commit/84da8ce53c54c95f2dc6fbd22cb083441fe8821b) adds the initial recorded metric comparison. Full local Quality passed with Ruff and 1,375 tests; exact [GitHub Quality run 37061247229](https://github.com/Andioratech/AURA/actions/runs/37061247229) passed. For run `RUN-20261002-b1e2f315f5b94c099f8fc56c5ed1596e`, the independent B03-01 origin comparison returned integrity `VERIFIED` and numerical `PASS`. The report and digest are kept outside Git at `results/verification/ANA-07/ANA07-METRICS-B03-01-0fa1114.json` and its `.sha256` sidecar; report SHA-256 `8d82d05f0388cede89fb7508c159f3781544f1442cfee93ecb6da461afad7984`, analyzer source SHA-256 `52d8324f3b1a202c745d281c77ddeb87eca976d8f7c530032a5c40b07206f405`. The exact zero residual applies only to the frozen origin values of this one manufactured case. Next: extend the immutable mapping and metric checks over the other admitted B-03/B-04/B-05 recorder cases, then build the model-local post-audits. The B-06 source-input decision remains a separate required branch before the complete P3 campaign.

## Preserved software-test failure

Before the broader family comparison was added, two focused test attempts failed at the B03-01 test assertion only. Root cause: the report correctly represents intensity as a list of three-component vectors, one vector per sample, while the regression assertion first expected a flat vector and then used `pytest.approx` on a nested list (unsupported by pytest). No numerical criterion, reference value, recorded run bundle or scientific interpretation failed. The assertion will compare its selected sample vector directly; the next test attempt follows this root-cause record. These test-only failures are not field-run evidence.
