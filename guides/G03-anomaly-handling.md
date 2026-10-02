# G03: Anomaly and Failure Handling

**Status:** DRAFT

Diagnose in this order: units/signs/ranges; geometry and coordinates; model domain; discretization/convergence; boundary conditions; energy/momentum accounting; independent solver. Preserve the original run. Classify failures as input, resource, numerical, model-domain or scientific-evidence failures.

For a favorable anomaly, freeze hashes and seed, reproduce it, reduce to a minimal case, vary discretization, change method, seek an analytical explanation and obtain review before updating D09. An anomaly is not a discovery until alternative explanations are tested.
