# AURA Scientific Project

**Adaptive Ultrasonic Regulated Acceleration (AURA)** is a computational research project studying whether controlled acoustic radiation forces can impose a prescribed acceleration on free bodies in a limited, reproducible domain. AURA investigates *acoustic pseudogravity*: mechanically induced acceleration that can reproduce selected kinematic effects. It does not create gravitational fields or spacetime curvature.

The project is designed to produce either a supported operating region or a quantified physical limit. A positive result is not assumed.

## Scientific status

This repository starts from the supplied Spanish baseline documents, reviewed and reorganized as English Markdown specifications. The documents describe a proposed research program, not completed software, experiments, or validated findings. Documents are marked `DRAFT` unless evidence and an explicit review decision promote them to `BASELINE`.

## Start here

1. Read [the document index](docs/D00-document-control.md).
2. Read [the system architecture](docs/D01-system-architecture.md) and [the MCLF specification](docs/D02-mclf.md).
3. Follow [G01, the contributor workflow](guides/G01-contributor-workflow.md) before changing scientific assumptions or code.

## Repository map

```text
docs/       Controlled scientific and engineering specifications (D00-D09)
guides/     Working procedures (G01-G05)
src/aura/   Python package scaffold
tests/      Test scaffold and future scientific validation cases
examples/   Versioned experiment configurations
data/       Data policy and directory placeholders; large data are not committed
results/    Run output policy and directory placeholder; generated results are not committed
```

## Current scope

The initial software scope is a CPU-first, reproducible simulation workflow: validated scenario inputs, a fast acoustic field model, explicitly regime-bounded force models, rigid-body dynamics, a deterministic controller, independent MCLF checks, and immutable run manifests. Hardware construction and human-scale claims are out of scope until scientific gates justify them.

## Document status and language

All maintained project documentation and repository metadata are in English. Source PDFs supplied for review were in Spanish and are not copied into this repository. See [the validation record](docs/D00-document-control.md#source-document-review) for the issues found and editorial decisions.

## License and citation

No license or publication citation has been selected. Do not assume permission to reuse this work outside the repository until the project owner chooses a license and citation metadata.
