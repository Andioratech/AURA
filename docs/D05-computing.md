# AURA-D05: Computing Resources and Environments

**Version:** 1.0 · **Status:** BASELINE · **Date:** 2026-10-01

## Policy

Use a CPU-first local profile for analytical and fast-model development. High-fidelity workloads run only after a preflight estimates memory, storage and time, and identifies a compatible execution tier. GPU availability never changes the scientific experiment definition.

## Resource preflight

Before a solver reserves memory, estimate mesh/field dimensions, scalar or complex precision, number of time steps, temporary arrays, output volume, expected runtime and available memory/disk. Include solver overhead and safety headroom; source-document hardware examples are not portable guarantees. Reject or require explicit smaller-domain/refined-subproblem strategy when a configured limit is exceeded.

Every run records requested and observed CPU/GPU, RAM, storage, operating system, runtime and backend. Unexpected out-of-memory termination is a failed run with its partial outputs retained and identified.

## Execution tiers

1. **Local CPU:** schemas, MCLF, analytical cases, fast fields and small rigid-body runs.
2. **Local GPU:** only tested compatible kernels; record device, driver and precision.
3. **Remote CPU/GPU:** immutable environment and transfer checksums; no silent parameter changes to fit a queue.
4. **High-performance computing:** MPI or distributed workflows only after profiling shows they are needed and a reproducibility plan exists.

## Environments and storage

Pin direct dependencies and record transitive environment lock, compiler, platform and accelerator libraries. Review candidate tool versions at implementation time rather than relying on dated snapshots in the source PDF. Keep small configurations and metadata in Git; keep large raw fields outside Git with immutable identifiers, checksums, retention owner and access path. Do not commit credentials or licensed external datasets.

## Escalation

Escalate a workload only when its scientific gate is ready, the local preflight demonstrates the need, the remote environment is documented, and outputs can be reproduced or independently checked.
