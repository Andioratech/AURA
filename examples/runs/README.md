# Software Lifecycle Examples

These are frozen software protocols, not physical experiments. Read [protocol v1.0](protocol.md) and the [run lifecycle contract](../../docs/research/run-lifecycle.md).

Install [ENV-1.0](../../requirements/README.md) in a **clean Git checkout**. `run` currently requires that checkout's executing source and complete development profile; a core-only wheel installation can use configuration checks but cannot supply this run-source contract.

```bash
aura run examples/runs/receipt-scenario.json --experiment examples/runs/receipt-experiment.json --no-randomness --json
aura run examples/runs/failure-scenario.json --experiment examples/runs/failure-experiment.json --no-randomness --json
```

Expected exits are **3** for the completed/scientifically INDETERMINATE receipt and **1** for the deliberate failed execution. Capture nonzero exits explicitly in automated shells; do not reinterpret them as scientific success. The response names the new run directory under `results/<experiment-id>/<run-id>/` and its final manifest digest. An optional `--output <new-directory>` selects a different unused directory.

```bash
aura check <run-directory> --sha256 <separately-retained-manifest-sha256> --json
```

Check returns 3 for a verified completed diagnostic and 1 for a verified failed/aborted diagnostic. Inspect `integrity` separately from `execution_status` and `verdict`. Running/unfinished bundles cannot establish completion. No command replays or overwrites an existing run.
