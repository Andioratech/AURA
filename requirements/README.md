# Reviewed Python Environment — ENV-1.0

**Reviewed:** 2026-10-02 · **Task:** [FND-08](../docs/work-items/FND-08.md)

## Supported profile and installation

The verified development target is **CPython 3.12.14, Linux x86_64, glibc >= 2.28**. CI uses Ubuntu 24.04. The package metadata permits Python >= 3.10, but this lock certifies only the stated target: for example, the selected rpds-py requires Python >= 3.11. Other Python versions, architectures and operating systems need their own reviewed artifacts and checks.

From the repository root with that interpreter available:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip --isolated install --index-url https://pypi.org/simple --require-hashes --only-binary=:all: -r requirements/dev-linux-py312.lock
python -m pip --isolated install --no-index --no-deps --no-build-isolation -e '.[dev]'
python -m pip check
python scripts/verify_environment.py
ruff check .
pytest
```

The first command installs all 16 direct/transitive/tool distributions from hashed wheels, including the pinned installer and build tools. The second builds only the local editable project with those tools; it neither resolves dependencies nor downloads an isolated build environment. See pip's [secure installation guidance](https://pip.pypa.io/en/stable/topics/secure-installs/) and the [setuptools backend](https://setuptools.pypa.io/en/latest/build_meta.html). Do not replace this sequence with an unbounded upgrade or `pip install -e '.[dev]'` when reproducing the profile.

The [inventory](environment-linux-py312.json) records exact filenames, SHA-256, sizes, original PyPI release metadata/URLs, compatibility and license information. Every selected wheel's bytes and size were compared with its official release record; none was yanked. The [core lock](core-linux-py312.lock) contains seven runtime dependencies. The [development lock](dev-linux-py312.lock) includes it and adds nine tools/dependencies. No downloaded binaries are stored in Git.

`verify_environment.py` checks lock/inventory agreement, exact installed distributions (including this project's version), interpreter, implementation, platform and minimum libc. Repeated metadata for the same normalized name/version (editable source and installed metadata) is collapsed; conflicting versions fail. Its JSON output records interpreter build/compiler, host platform, package versions and lock/inventory hashes. Exit 1 means the profile failed verification. It does not authenticate the interpreter binary, inspect installed package bytes, establish source revision identity, or create a RunManifest. Hash-enforced installation verifies the downloaded wheels; binding a source/environment snapshot to an actual run belongs to RUN-01.

## Core-only runtime

Build the project wheel in the locked development environment, then install the core lock and project wheel in a separate fresh environment:

```bash
python -m pip wheel --no-index --no-deps --no-build-isolation . --wheel-dir /tmp/aura-project-wheel
python3.12 -m venv /tmp/aura-core
/tmp/aura-core/bin/python -m pip --isolated install --index-url https://pypi.org/simple --require-hashes --only-binary=:all: -r requirements/core-linux-py312.lock
/tmp/aura-core/bin/python -m pip --isolated install --no-index --no-deps /tmp/aura-project-wheel/aura_science-0.1.0-py3-none-any.whl
/tmp/aura-core/bin/python -m pip check
/tmp/aura-core/bin/aura status
```

Choose fresh output directories. This smaller environment contains seven runtime distributions, the project and the interpreter's bootstrap pip. It deliberately excludes pytest/Ruff/build tools and is not the full development profile checked by `verify_environment.py`. Record the actual bootstrap installer and locally built project-wheel hash with an installation result; the project wheel is identified by its source revision/build environment, not a third-party PyPI lock entry.

## Compatibility and license review

| Selected distribution | Version | Upstream declared license |
|---|---|---|
| attrs | 26.1.0 | MIT |
| jsonschema | 4.26.0 | MIT |
| jsonschema-specifications | 2025.9.1 | MIT |
| PyYAML | 6.0.3 | MIT |
| referencing | 0.37.0 | MIT |
| rpds-py | 2026.6.3 | MIT |
| typing-extensions | 4.16.0 | PSF-2.0 |
| iniconfig | 2.3.0 | MIT |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pip | 26.2.1 | MIT |
| pluggy | 1.6.0 | MIT |
| Pygments | 2.21.0 | BSD-2-Clause |
| pytest | 9.1.1 | MIT |
| Ruff | 0.16.10 | MIT |
| setuptools | 84.0.0 | MIT |
| wheel | 0.48.0 | MIT |

These declarations come from the exact wheel metadata; the inventory links each primary release record and lists inspected notice files. Bundled components, especially pip/setuptools, carry additional notices. Keep the full distribution notices; this table is not a complete redistribution legal review or a license grant for AURA (project status remains UNLICENSED). Dependency markers were reviewed for Linux/Python 3.12 and `pip check` verifies the installed closure.

Numerical tools remain **optional candidates, not installed dependencies**. Official metadata for [NumPy 2.5.3](https://pypi.org/pypi/numpy/2.5.3/json) and [SciPy 1.18.1](https://pypi.org/pypi/scipy/1.18.1/json) permits Python >= 3.12; SciPy requires NumPy >= 2.0.0, < 2.8. Their selected binary artifacts, bundled numerical libraries/licenses, precision behavior and actual compatibility must be reviewed when ANA/NUM requires them. Metadata compatibility alone does not verify a numerical method. No GPU/backend package is justified in P2.

## CI and update policy

CI pins official [checkout](https://github.com/actions/checkout) v7.0.1 and [setup-python](https://github.com/actions/setup-python) v7.0.0 by commit, both using Node 24, and requests Python 3.12.14 explicitly. Ubuntu 24.04 is an OS label, **not an immutable hosted image**. Kernel, glibc, interpreter build and runner images can differ and are recorded. Bootstrap pip and the supplied interpreter remain external installation prerequisites; these locks do not promise a bit-identical machine or indefinite upstream download availability.

A reviewed change must update exact pins, selected artifacts, provenance/license review and affected profile identifier, then repeat fresh development/core installs, dependency consistency, environment verification, negative hash rejection and full local/remote CI. Preserve failures. Do not regenerate locks automatically during normal CI. Store an external wheel archive with the same digests when durable/offline availability is needed; `--no-index --find-links <archive>` can replace the index while retaining mandatory hashes.

## Optional B-04 figure renderer

`render-b04-linux-py312.lock` pins the separately reviewed Matplotlib 3.10.8 renderer and its resolved wheels for Linux x86_64 / CPython 3.12. It is not part of ENV-1.0 or required by the solver, CLI, tests or Quality workflow. Install only into a separate environment. The renderer reads exported values; it does not produce the independent mathematical reference. The [ANA-03 record](../docs/work-items/ANA-03.md) defines its scope and output publication policy.

```sh
python3.12 -m venv /tmp/aura-b04-render
/tmp/aura-b04-render/bin/python -m pip --isolated install --index-url https://pypi.org/simple --require-hashes --only-binary=:all: -r requirements/render-b04-linux-py312.lock
/tmp/aura-b04-render/bin/python -m pip check
# Export using the locked AURA development environment first:
python scripts/export_standing_wave.py /tmp/b04-data.json
/tmp/aura-b04-render/bin/python scripts/plot_standing_wave.py /tmp/b04-data.json /tmp/b04.png
```

Use unused output paths; both scripts refuse overwrite. Source/fixture identity is embedded in the export and figure. Retain the input hash, renderer lock, observed package/interpreter information and output hash with the verification report.
