# RUN-01 Software Diagnostic Protocol — Version 1.0

**Frozen:** 2026-10-02. These two experiments test the recorder, not AURA's physical hypothesis. No acoustic model, measurement or physical simulation is used.

## EXP-2026-RUN01-RECEIPT

Question: does a completed bounded diagnostic retain verifiable input, protocol, source, environment and output identities without becoming scientifically accepted?

Observable: a versioned receipt naming the supplied scenario, plus initial/final manifests and independent file checks. Exact acceptance: the receipt exists, every indexed file matches its digest, record links agree, inputs remain unchanged, execution is completed, and the scientific verdict remains INDETERMINATE. A missing receipt or integrity mismatch fails this software comparison. No numerical tolerance is involved.

## EXP-2026-RUN01-FAILURE

Question: does a deliberate executor exception retain its partial artifact and an identifiable failure record?

Observable: partial output plus terminal failed state and RUN_EXECUTION code. Exact acceptance: a deliberate RuntimeError is recorded, the partial output remains verifiable, execution is failed, the lifecycle post-audit is INVALIDATED and rerunning into the same directory is refused. Failure is the intended execution outcome; successful verification of that behavior is not scientific acceptance.

## Fixed domain and execution policy

The supplied scenarios inherit explicitly manufactured water-like/body/source declarations from the schema fixture. They are never evaluated by an acoustic solver. SOFTWARE-RUN-01 names this software procedure, not a physical equation. Scalar precision is recorded as float64; no physical arithmetic or field allocation occurs. The schema-required target/observable window is unused by this diagnostic and does not define a measured time interval.

Use the clean Git source and ENV-1.0 development profile. Each scenario declares 1 GiB RAM, 16 MiB disk and 30 s recorder wall time; preflight must fit the fixed diagnostic estimate and available local resources. Use an explicit null seed (`--no-randomness`); no random algorithm is used. UUID run identifiers are uniqueness metadata, not scientific sampling seeds.

Store the actual protocol bytes, exact supplied scenario/experiment, source revision/inventory and environment/lock files with every run. Preserve all failures, interruption evidence and original directories. Do not promote these diagnostic IDs into D09 physical evidence. Physical uncertainties, convergence and experimental comparison are not applicable to these software tests; they remain required for later scientific work.
