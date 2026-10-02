# Example Experiments

Store versioned, fully specified experiment configurations here. Each example must state SI units, assumptions, model regime, observable, seed, resource limits and expected checks. Do not describe an example as validated until D06 evidence exists.

## Implemented schema example

[`schema/manufactured-scenario.json`](schema/manufactured-scenario.json) is a complete manufactured input for schema 1.0 and the [configuration-validation CLI](../docs/cli-usage.md). It is not an experiment or a measured operating point. Run `aura validate-config examples/schema/manufactured-scenario.json --json` from the repository root after installation. Expected outcome: schema VALID, audit INDETERMINATE, exit code 3. No solver or scientific run is invoked.

## ANA-06 energy balance

[`energy_balance.py`](energy_balance.py) runs three fixed ideal plane-wave closed-sphere checks and one ideal outgoing spherical-wave shell check. Run `uv run --extra dev python examples/energy_balance.py` from the repository root. The expected comparison is PASS for all four mathematical ledgers, with zero plane-sphere net flux and equal/opposite inner/outer spherical powers within the declared binary64 tolerance. This only checks the named numerical model and accounting; it does not establish force on an object, real-water calibration, experimental validity or microgravity performance.
