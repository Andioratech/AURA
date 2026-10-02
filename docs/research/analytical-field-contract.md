# Analytical Field Contract

**Contract:** FIELD-1.0 · **Date:** 2026-10-02 · **Owning task:** [ANA-01](../work-items/ANA-01.md)

## Scientific scope

The first analytical family is single-frequency linear acoustics in a stationary, homogeneous, unbounded, inviscid, lossless fluid. Density and sound speed are positive explicit inputs. Sources are ideal prescribed incident waves. Samples do not include scattering by bodies, reflections from walls, finite transducer apertures, viscous boundary layers, streaming, heating, cavitation or force. A standing pair is prescribed counterpropagation, not a solved resonant chamber.

Water-like manufactured parameters are a software reference, not measured water properties or evidence of microgravity performance. A body in a Scenario remains recorded context; it must be labeled uncoupled by an incident-field driver. Future larger-body campaigns retain DEC-004 and require their own scattering/force evidence.

## Mathematical convention and source definitions

Use CONV-1.0: `q(x,t) = Re(q_hat(x) exp(-i omega t))`, peak phasors, `omega = 2 pi f`, `k = omega/c`, `Z = rho c`. Vectors use right-handed chamber `[x,y,z]`. Under the inviscid restriction of SRC-E01 Eq. (6), project derivation gives:

```
grad(p_hat) = i omega rho v_hat
div(v_hat) = i omega p_hat / (rho c^2)
laplacian(p_hat) + k^2 p_hat = 0
```

For each ideal plane wave, `A >= 0` is peak pressure at its phase-reference point `x_ref`, `phi` is phase in radians, and `n` is a unit propagation direction:

```
p_j = A_j exp(i (k n_j dot (x - x_ref_j) + phi_j))
v_j = n_j p_j / Z
grad(p_j) = i k n_j p_j
```

Sum each scalar/vector component across sources without dividing by the source count or modifying input amplitudes. `x_ref` specifies phase; it is not a finite radiator surface. With equal, zero-phase waves in `+x` and `-x`, project algebra gives `p = 2 A cos(kx)`, `v_x = 2 i A sin(kx)/Z`, `grad_x(p) = -2 k A sin(kx)`.

The period-mean acoustic energy-flux vector is `I = Re(p_hat conj(v_hat))/2`, W/m², componentwise. Pressure squared alone does not specify this vector for arbitrary superpositions. The single progressive plane-wave helper remains restricted to its existing domain. These statements follow the linear equations and harmonic averaging reviewed in [the source record](analytical-source-review.md); no momentum-transfer or force bound follows from them alone.

For B-06 only, the selected reference is an ideal outgoing spherical wave in a punctured fluid domain. Let `r = |x - x_s|`, `n_r = (x - x_s)/r`, and specify reference radius `r_ref > 0` and peak pressure `P_ref` there:

```
p = P_ref (r_ref/r) exp(i (k (r-r_ref) + phi))
grad(p) = (i k - 1/r) p n_r
v = (p/Z) (1 + i/(k r)) n_r
```

Retain the reactive `i/(kr)` term; no far-field approximation is used in this case. The source point is excluded. `r_min` is an explicit computational exclusion, not proof that a real transducer is modeled correctly outside it. Spreading is not material attenuation. A constitutive attenuation model remains unselected.

## Sampling and in-memory output

`aura.fields.FieldSamples` is an immutable **unprovenanced data container**, not a scientific verdict or a standalone FieldResult. Construction validates representation only; it does not enforce Euler's equation, source exclusion or any model regime. A driver must enforce those constraints before returning it.

| Required attribute | Unit / logical shape | Representation |
|---|---|---|
| `frequency_hz` | Hz, scalar > 0 | binary64 |
| `coordinates_m` | m, `[N,3]` | binary64 |
| `pressure_pa` | Pa, `[N]` | complex128 |
| `velocity_m_s` | m/s, `[N,3]` | complex128 |
| `pressure_gradient_pa_m` | Pa/m, `[N,3]` | complex128; component `j` is partial derivative with respect to chamber coordinate `j` |

`1 <= N <= 256`. Accept only explicit list/tuple containers and finite built-in numeric components; reject booleans and string coercion. Copy into nested tuples. Complex components may have zero imaginary part. Preserve duplicates and ordering; no interpolation, hidden grid, unit conversion or coordinate transformation. Empty arrays, unequal sample counts and omitted vectors fail. No velocity gradient, Hessian, body velocity or force is implied by the pressure gradient.

Sampling is point evaluation in a closed finite observation box, not a boundary-value problem. Each benchmark fixes its sample list before execution. Drivers check membership and their own singular exclusion; off-grid interpolation and mesh convergence are not applicable to direct closed-form evaluation. The physical domain may be unbounded while the tested observation window is finite.

## Component artifacts and schema compatibility

`to_artifacts()` returns four JSON-compatible component records keyed `coordinates`, `pressure`, `velocity`, `pressure_gradient`. `from_artifacts()` accepts exactly those four and requires matching frequency and sample count. Each component has exactly:

```
contract: "FIELD-ARRAY-1.0"
quantity: its component key
frame: "chamber"
frequency_hz: positive number
unit: "m" | "Pa" | "m/s" | "Pa/m"  (fixed by quantity)
shape: [N,3] | [N]                 (fixed by quantity)
dtype: "float64" | "complex128"    (fixed by quantity)
phasor_convention: "exp(-iwt)"
amplitude_convention: "peak"
values: nested arrays
```

For complex records each logical scalar is encoded `[real, imaginary]`, both finite binary64 numbers. The trailing pair is encoding, not a logical vector axis; velocity's storage shape is `[N,3,2]` and its declared shape is `[N,3]`. Coordinates have no complex axis. Harmonic metadata on the coordinate record identifies the shared sample set; coordinates themselves do not oscillate. Returned dictionaries are fresh snapshots. The module performs no filesystem I/O. File readers must also enforce RUN's bounded regular-file, duplicate-key, hash and no-symlink rules before passing parsed records to this API.

Schema-1.0 `FieldResult` is preserved: coordinates `[N,3]` m/float64, pressure `[N]` Pa/complex128, velocity `[N,3]` m/s/complex128, all non-null for this family. Each reference points to its own component JSON file and hashes the entire raw file. Schema 1.0 cannot represent Pa/m or a gradient slot. The analytic adapter therefore must add a separately versioned `FIELD-INDEX-1.0` companion with exact `contract: "FIELD-INDEX-1.0"`, `run_id`, `field_result_id`, `field_result_sha256` and a `pressure_gradient` reference `{artifact:{uri,sha256},unit:"Pa/m",shape:[N,3],dtype:"complex128"}`. It must cross-check all four component records against FieldResult, index, Scenario frequency and frozen samples. The index is a proposed adapter record, not accepted by `aura run/check` yet. Do not silently broaden schema 1.0 or put gradients in diagnostics strings.

Existing schema fixtures with null velocity remain valid structural fixtures. They cannot satisfy FIELD-1.0. A successful container round trip says nothing about provenance or correct physical values.

## Required analytical driver admission (ANA-02 onward)

1. Version and whitelist each model and equation set in both executor **and checker**. Keep diagnostic behavior backward compatible. Freeze a separate run policy before extending RUN-1.0; unsupported fields/versions fail before allocation.
2. Bind a separate immutable sampling/protocol input to the Experiment and RunManifest hashes. Schema-1.0 solver parameters have no sampling list: do not overload a tolerance/mesh field. First plane cases may use existing plane-wave source inputs; a spherical source needs an explicit new input contract before ANA-05 integration, never a mislabeled plane wave/piston.
3. Validate positive homogeneous medium/frequency, explicit zero material loss, source geometry/direction, observation box, N/M caps, phasor convention and source exclusion. Reject hard contradictions and unsupported geometry. Uncoupled bodies and absent experimental coverage require explicit INDETERMINATE notes; do not turn L0's MODEL_UNCOVERED into acceptance by changing a model name.
4. Required outputs: four component files, schema-1.0 FieldResult, FIELD-INDEX-1.0, independent benchmark metrics, model-specific post-audit and all RUN provenance/preflight/manifest records. No adapter is admitted if `check` cannot reconstruct and cross-check that set.
5. Independently compare pressure, every velocity component and every pressure-gradient component against the frozen reference. Record normalized maximum and RMS errors, actual SI scales and every failed point. Check phase/direction, the Euler relation, expected mean flux and source validity. A residual computed from mutually dependent solver outputs alone is insufficient.
6. ANA-06 adds source/control-surface balances; pending balances and experimental/model uncertainties remain explicitly unavailable. Numerical benchmark comparison and scientific MCLF verdict are separate fields. Invalid, alert and uncovered outcomes retain their original meaning; no `ACCEPTED` physical claim arises from a completed calculation.
7. ANA-07 executes the full admitted matrix through the recorder, retaining every failed run and the exact source/environment/inputs. Do not close P3 with type tests or expected-value tables.

## Resource budget to implement before analytical execution

For the initial matrix: `N <= 256`, `M <= 2`, one CPU worker, no GPU, deterministic/no randomness, binary64/complex128. Coordinates plus seven complex scalars occupy `136 N` raw numeric bytes. Reserve at least `4096 N + 4096 M` bytes for Python containers, temporary component encoding and evaluation, then add measured interpreter/recorder baseline RSS with 2x headroom. This is a conservative starting estimate requiring calibration, not an observed solver memory result.

Allow at most 32 KiB metadata plus 1024 bytes per sample across all component files (288 KiB at the cap), each individual RUN file still <= 1 MiB. Preflight 16 MiB total bundle storage and a 30 s execution cap, plus environment/provenance overhead already checked by RUN. Calibrate actual serialization and RSS during ANA-02; oversized input fails before allocation, excess execution becomes a preserved failed run. The test matrix permits at most 32 configurations; no sweep, mesh or time stepping. A future larger model needs a separately reviewed estimate, not a silent increase.
