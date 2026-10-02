# AURA-D07: Experiments, Data and Reproducibility

**Version:** 1.0 · **Status:** DRAFT · **Date:** 2026-10-01

## Identity

An experiment defines a question, hypothesis, observable, protocol and versioned configuration space. A run is one execution. Assign stable IDs such as EXP-YYYY-NNNN and RUN-YYYYMMDD-<short-hash>; IDs do not encode mutable results.

## Run manifest

Required fields: schema version; experiment/run IDs; hypothesis and observables; UTC timestamp; source revision; clean/dirty state; configuration and data hashes; environment lock and platform; solver/model/regime; precision; seed; requested resources; input references; output paths/checksums; metrics; convergence; MCLF pre/post verdict; failure code and operator notes.

## Layout and formats

Store small human-authored configs under examples or experiments. A run writes under results/<experiment-id>/<run-id>/ with manifest, logs, metrics, report, plots and references to raw fields. Use documented JSON/YAML for manifests/configuration and a suitable self-describing array format for large data. Never overwrite a run directory.

Large outputs are not committed to Git by default. Retain raw data for claim-critical and accepted results, include checksums and access location, and document retention decisions. Remove secrets and personal data.

## Evidence bundle

An evidence bundle contains the immutable manifest, configuration, code revision, environment, MCLF report, logs, metrics, convergence/benchmark analysis, source references and all necessary compact data or durable data references. INVALIDATED runs cannot be promoted. ALERT and INDETERMINATE items require an explicit limitation note.

## Reproduction

Provide one command or documented workflow that verifies hashes, reconstructs the environment and replays a selected run. If exact bitwise replay is not portable, define metric tolerances and explain backend nondeterminism.
