# Exact-Sphere CBIE at 179° with Fourteen and Sixteen Meridian Subdivisions

**Date:** 2026-10-08 | **Source revision:** `ca96183ee6782ef29207397f252848ce7fda4572`

**14-subdivision artifact:** `results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-14-20261008.json`

**14-subdivision artifact SHA-256:** `795b8dc3c4deea5a3a302a2dfd6a3d68607450db13ba6588072a9b40c1611c18`

**16-subdivision artifact:** `results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-16-20261008.json`

**16-subdivision artifact SHA-256:** `d4ff8dc8e56e7b01b1a57baee94577b59e18001f01ea0a85bd28434fdc092ee5`

## Purpose and scope

This continuation holds the exact-sphere, centered-monopole rigid-plane Neumann trace and every quadrature setting fixed while increasing the number of subdivisions on the two active meridian intervals. It evaluates one streamed conventional boundary-integral identity (CBIE) at colatitude 179°. It does not assemble a matrix, solve for an unknown field, or use GPU acceleration.

These are repeatable numerical evaluations of one manufactured trace and parameter set. They are not physical observations, field acceptance, convergence proof, an error bound, force or acceleration results, physical validation, or evidence of gravity equivalence.

## Frozen setup and execution

Both clean ENV-1.0 runs use CPython 3.12.14 and source revision `ca96183ee6782ef29207397f252848ce7fda4572`. The sphere radius is 0.025 m, plane gap 0.0001 m, frequency 25,230 Hz and sound speed 346 m/s. The colatitude is 179°, with the AURA normal pointing into the sphere. The meridian split factor is 8, order is 256 per active subinterval, direct/image azimuth counts are 4,096/2,048, and each case has two repeats with a 120 s per-action cap. No setting or cap was changed between levels 10, 12, 14 and 16. The matrix was not allocated, the solver was not started, and BEM preflight remains unauthorized.

The 14-subdivision run completed in 85.224827/85.076849 s. The 16-subdivision run completed in 97.387466/97.798495 s. Each pair of repeat result objects matched exactly; the recorded residual reconstructs exactly from the jump and four layer terms at both levels. ENV-1.0 verification reported no errors.

| Subdivisions per active interval | Normalized residual `|R|/|p(x)|` | Repeat checksum SHA-256 |
|---:|---:|---|
| 10 | `3.161596044140457e-7` | `0676bd469644c002fbe284fb1f416c5a157e7a19f6c3b9fbc2d1ab649618139b` |
| 12 | `2.8084642545928237e-7` | `097204701b4bb9775a70cb8123320148a6326ec55757df035a847e87dd967ffb` |
| 14 | `2.366765464132597e-7` | `2031ded01226728e4c982258db46d9e24b011d382edf683914d4d2d3778a9b34` |
| 16 | `2.005146001492107e-7` | `d9b688c69efd8ddfee3c5cbb67e87e3624c55bb3fe42220a6743f6ca0f97f2eb` |

The latest two levels' encoded terms (`real:imaginary`, with binary64 hexadecimal components) are:

| Term | 14 subdivisions | 16 subdivisions |
|---|---|---|
| Half-pressure jump | `0x1.88cd41a66a1d4p+0:-0x1.6288f57b0efeep+1` | `0x1.88cd41a66a1d4p+0:-0x1.6288f57b0efeep+1` |
| Direct double layer | `0x1.af00e04102b40p+0:-0x1.fc4273fbd5970p-3` | `0x1.af00d5717bfbap+0:-0x1.fc41d7ddba7c0p-3` |
| Image double layer | `-0x1.489996679b774p-4:0x1.3dbf1af93255ap+1` | `-0x1.489996679b481p-4:0x1.3dbf1af932543p+1` |
| Direct single layer | `0x1.8ee31b6acf4a0p+0:-0x1.54a750f454380p-2` | `0x1.8ee32ada189e0p+0:-0x1.54a79c321d6c0p-2` |
| Image single layer | `0x1.94615edf8231fp+0:-0x1.9f90d43d704bep-3` | `0x1.94615edf82374p+0:-0x1.9f90d43d706b1p-3` |
| CBIE residual | `0x1.c6d433ba00000p-21:-0x1.4be70ede40000p-20` | `-0x1.8105ce1c00000p-21:0x1.194c4c3820000p-20` |

Between subdivisions 14 and 16, the direct double- and single-layer changes normalized by `|p(x)|` are `2.09973339215e-7` and `2.2901590961e-7`. The corresponding image-layer changes are `2.31058070926e-15` and `3.69666818478e-15`. The residual magnitude decreases from `2.366765464132597e-7` to `2.005146001492107e-7`, while the separately evaluated direct terms remain sensitive at a scale comparable to that residual. The identity subtracts and adds larger terms, so a smaller residual can result from cancellation without establishing that the individual terms have stabilized.

## Interpretation and next method

The residual magnitudes at 10/12/14/16 decrease across this short tail, but earlier subdivisions are nonmonotone. The direct layers continue to change appreciably, the image layers are at binary64-scale differences for this case, and logarithmic product-integral restoration remains fixed at order 256. This series therefore shows finite sensitivity and cancellation; it does not establish convergence or an error bound. Further subdivision of this same action is stopped because it would extend the same one-angle quadrature comparison without resolving the dominant direct-layer uncertainty.

The next bounded investigation is to design, derive, and independently check a spherical-harmonic/modal evaluation of the same manufactured sphere trace. It should calculate the direct and reflected-source contributions through a formulation separate from the current azimuthal ring traversal, state truncation and floating-point checks, reproduce the 179° case, and add selected other colatitudes only after the reference has been derived and checked. The existing reflected-monopole identity and exact-sphere mode tests are candidate starting references; their assumptions and source equations must be checked before use. Freeze equations, cutoffs, checks, and resource bounds in a reviewable plan before implementing the reference. This remains numerical cross-verification of an ideal trace, not physical validation.

NUM-03 remains **ACTIVE / INDETERMINATE**. P4 remains unpassed, the plan remains DRAFT, and BEM preflight remains unauthorized. No matrix, solver, or simulation core was started.

## Reproduction

With the repository's ENV-1.0 CPython 3.12.14 environment at clean revision `ca96183ee6782ef29207397f252848ce7fda4572`, reproduce either result with:

```bash
.venv/bin/python tools/research/benchmark_bem_exact_sphere_cbie_composite_subdivision.py \
  --output results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-14-20261008.json \
  --subdivisions 14

.venv/bin/python tools/research/benchmark_bem_exact_sphere_cbie_composite_subdivision.py \
  --output results/diagnostics/bem-exact-sphere-cbie-subdivision-179deg-16-20261008.json \
  --subdivisions 16
```

The artifacts are generated under an ignored results directory and remain local. Their hashes above identify the produced files; they are not committed.
