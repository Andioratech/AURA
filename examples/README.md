# Example Experiments

Store versioned, fully specified experiment configurations here. Each example must state SI units, assumptions, model regime, observable, seed, resource limits and expected checks. Do not describe an example as validated until D06 evidence exists.

## Implemented schema example

[`schema/manufactured-scenario.json`](schema/manufactured-scenario.json) is a complete manufactured input for schema 1.0 and the [configuration-validation CLI](../docs/cli-usage.md). It is not an experiment or a measured operating point. Run `aura validate-config examples/schema/manufactured-scenario.json --json` from the repository root after installation. Expected outcome: schema VALID, audit INDETERMINATE, exit code 3. No solver or scientific run is invoked.
