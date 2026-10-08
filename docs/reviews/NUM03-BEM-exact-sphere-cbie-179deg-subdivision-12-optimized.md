# Exact-Sphere CBIE at 179° with Twelve Meridian Subdivisions

**Date:** 2026-10-08 | **Source revision:** `98735b7730972928a0237b0911e97c331dbf484d` | **Optimization revision:** `07a963c28358ba477005c1f7d730f4e69e1a5cbf`

**Run artifact:** `results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-12-optimized-20261008.json`
**Artifact SHA-256:** `3c13638d383cda3909e7478abfad720a7e64efb4d7c3ee3f4dd30b35ebc69e4e`

## Purpose and scope

The prior twelve-subdivision action exceeded the frozen 120 s per-action cap. This follow-up optimized repeated kernel work while preserving the same geometry, frequency, quadrature counts, meridian order, subdivision count and time cap. It evaluates one streamed direct-plus-image conventional boundary-integral identity (CBIE) for an exact sphere and centered-monopole Neumann half-space trace. It does not construct a matrix or solve for an unknown field.

The result is numerical verification for this manufactured boundary trace and configuration. It is not a physical observation, field acceptance, acceleration result, gravity equivalence, convergence proof or general error bound.

## Change and verification

The scalar Helmholtz ring Green function and its field/source gradients previously traversed the same azimuthal nodes in separate loops. Commit `07a963c` adds a combined internal routine that shares one midpoint pass and phase evaluation while retaining the exact elliptic Laplace contributions and compensated accumulation. The existing separate routines remain unchanged. Three focused comparisons cover separated, near-diagonal and zero-radius source geometries at 64, 512 and 4,096 azimuth samples; combined values agree with the separate routines within `2e-13` relative or `4e-15` absolute.

For the 179° single-subdivision timing check, the combined route took 1.963 s and the original separate route 2.771 s. The normalized residuals were `3.7920644567423997e-6` and `3.7920644567115703e-6`, respectively. This is about a 29% runtime reduction for that action and a residual difference of roughly `3.1e-17`; it is a performance/computational-equivalence check, not a new accuracy claim.

The clean ENV-1.0 twelve-subdivision run then completed both repeats under the unchanged 120 s cap:

| Repeat | Wall time | Normalized CBIE residual |
|---|---:|---:|
| 1 | 97.720954 s | `2.8084642545928237e-7` |
| 2 | 99.667248 s | `2.8084642545928237e-7` |

The two complete result objects match; their repeat checksum is `097204701b4bb9775a70cb8123320148a6326ec55757df035a847e87dd967ffb`. The measured jump, separate direct/image layers and residual are retained in the ignored JSON artifact. The recorded residual reconstructs exactly as `jump + direct_double + image_double - direct_single - image_single`.

For continuity when the ignored JSON is unavailable on another machine, the exact encoded complex terms are reproduced here (`real:imaginary`, each component in hexadecimal binary64 form):

| Term | Encoded value |
|---|---|
| Half-pressure jump | `0x1.88cd41a66a1d4p+0:-0x1.6288f57b0efeep+1` |
| Direct double layer | `0x1.af00d374e5efep+0:-0x1.fc41bb2c93b08p-3` |
| Image double layer | `-0x1.489996679b50bp-4:0x1.3dbf1af93254cp+1` |
| Direct single layer | `0x1.8ee32dafd9220p+0:-0x1.54a7aa052d200p-2` |
| Image single layer | `0x1.94615edf8236cp+0:-0x1.9f90d43d7066cp-3` |
| CBIE residual | `-0x1.0da8500a00000p-20:0x1.89fad8a980000p-20` |

The boundary pressure magnitude used for normalization is `6.332817962447841 Pa` under the declared unit centered-monopole trace.

At subdivisions 10 and 12, the residuals are `3.161596044140457e-7` and `2.8084642545928237e-7`. Between these levels, the normalized direct double- and single-layer changes are `1.69695338577e-8` and `1.84882665796e-8`; the image double- and single-layer changes are `1.88506055592e-15` and `2.49147956896e-15`. The optimized arithmetic is not bitwise identical to the earlier separate-loop implementation; the kernel comparisons bound the observed difference for their tested geometries, while the 10-to-12 trend remains finite sensitivity. Across levels 1/2/4/8/10/12, the residual remains nonmonotone. The unchanged order-256 logarithmic product-integral restoration and direct-layer sensitivity prevent interpreting this sequence as convergence.

Commit `07a963c` passed GitHub Quality run [37777323331](https://github.com/Andioratech/AURA/actions/runs/37777323331). Commit `98735b7` passed the complete local Quality workflow: locked dependency installation, editable installation, `pip check`, ENV-1.0 verification, Ruff, required-document checks and 1,846 tests. Its exact GitHub run is [37780768870](https://github.com/Andioratech/AURA/actions/runs/37780768870).

## Reproduction from the VM checkout

Use CPython 3.12.14 and the repository's `ENV-1.0` Linux lock profile. On a clean checkout of source revision `98735b7`, run:

```bash
.venv/bin/python tools/research/benchmark_bem_exact_sphere_cbie_composite_subdivision.py \
  --output results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-12-optimized-20261008.json
```

The environment fingerprint in the artifact is `9d32c7901e7b62bf3ada30cb02eeac736589a4556c42117ab0c9626151e34aec`. Its component lock hashes are: environment profile `4387feff712e60296c646f04217efc205e4e8b8c23412f9fed6e2b10836deb4e`, core lock `91d895b3097095874dc6b4848bce415983408c9daf123e1d7206e03ecf49af17`, and development lock `9e612df1f995778ad8f12e0980db5d760f26d8b3f284e38278f1055a19c7ae40`. Environment verification reported no errors.

The harness verifies clean source and environment identity, fixes factor 8, per-panel order 256, direct/image azimuth counts 4,096/2,048, two repeats and a 120 s cap per action, then refuses to overwrite an existing output. The generated results tree is ignored by Git. The artifact SHA-256 above allows an owner-held copy to be checked after transfer; the tracked test also reruns the two actions and verifies repeat equality and residual reconstruction.

## Project status and next step

NUM-03 remains **ACTIVE / INDETERMINATE**. P4 remains unpassed, its plan remains DRAFT, and BEM preflight remains unauthorized. No matrix, solver or simulation core was started. Preserve the original timeout artifact; its missing layer terms are not recreated or inferred.

The next bounded check is a 179° run at 14 subdivisions using the same settings and cap, through the harness's explicit subdivision option. Preserve both the new run and any timeout record. Compare the direct and image layers separately; stop subdivision escalation if the result is resource-limited or if the observed change cannot be distinguished usefully from the established finite sensitivity. No tolerance or convergence threshold is introduced by this review.
