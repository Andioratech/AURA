# FND-01 — SI, Coordinates and Acoustic Conventions

**Contract:** CONV-1.0 · **Date:** 2026-10-02 · **Status:** Implementation contract reviewed against D02/D03/D08; no model-validation claim

## Quantity boundary

Serialized dimensional quantities use `{"value": 0.002, "unit": "m"}`. Three-component vectors use `{"value": [0.0, 0.0, 0.0], "unit": "m"}`. The scalar/vector shape belongs to the field contract. Bare dimensional numbers, booleans, numeric strings, null required values and nonfinite values are rejected. Project identifiers and labels are strings.

The version-1.0 schema accepts canonical SI spellings only. FND-03 supplies an [explicit conversion boundary](numerical-domain-and-conversions.md) for supported alternative units before schema validation. Unknown units are rejected, never inferred from magnitude. Canonical serialization/hashing is completed in FND-07; lexical differences between JSON numbers are not yet a scientific identity guarantee.

| Quantity | Canonical spelling | Constraint / distinction |
|---|---|---|
| Length, radius, diameter | `m` | Positive for finite body dimensions; radius and diameter have distinct field names |
| Mass | `kg` | Positive for a massive modeled body; provenance remains explicit |
| Time | `s` | Nonnegative elapsed time; evaluation end greater than start |
| Frequency | `Hz` | Positive temporal frequency; never substitute angular frequency |
| Angle, source phase | `rad` | Signed; do not silently wrap or convert degrees |
| Pressure amplitude | `Pa` | Nonnegative amplitude; signed instantaneous pressure is a different field |
| Velocity | `m/s` | Vector or speed as declared |
| Acceleration | `m/s^2` | Signed vector; includes explicitly chosen gravity |
| Density | `kg/m^3` | Positive |
| Dynamic viscosity | `Pa*s` | Nonnegative; zero is an explicit idealization needing later regime review |
| Compressibility | `1/Pa` | Positive when supplied/required by the model |
| Temperature | `K` | Positive absolute temperature; no implicit room temperature |
| Force / torque | `N` / `N*m` | Signed vectors in the declared frame |
| Power / intensity | `W` / `W/m^2` | Distinguish source acoustic, intercepted acoustic and electrical power |
| Moment of inertia | `kg*m^2` | Body-frame tensor; no inferred inertia for unsupported geometry |
| Amplitude attenuation coefficient | `1/m` | Defined by amplitude exponential decay, not intensity decay |
| Dimensionless quantities | `1` | No automatic equivalence between a generic scalar and a physical angle |

Unit names follow the [BIPM SI definitions](https://www.bipm.org/en/measurement-units/si-base-units). ASCII compound-unit spellings are AURA's serialization convention, not a new SI definition.

## Frames and body geometry

Use right-handed Cartesian coordinates and vector order `[x, y, z]`, with +Z the declared up direction. Positions, velocities, forces and target accelerations declare `frame: chamber`. Gravity is a required vector, including for ideal zero gravity; the reference value 9.80665 m/s² is never silently assigned. Initial body orientation uses a unit quaternion `[w, x, y, z]` mapping body coordinates into chamber coordinates; check its norm with absolute tolerance 1e-12 and reject, rather than silently normalize, a larger error. This tolerance is a serialization consistency check, not a physical acceptance tolerance.

The body contract carries an explicit geometry discriminator. Initial geometry records may describe a sphere by radius or a box by three dimensions; neither representation establishes that a solver supports it. Mass, material and dimensions have separate provenance. Mesh and other geometry types require a later versioned extension. The schema must never convert a box or larger body into a point particle. Model applicability and mass/material/geometric consistency remain separately reviewed checks.

## Harmonic convention

Represent a physical real harmonic quantity as `Re(q_hat(x) * exp(-i*omega*t))`, with peak complex amplitude `q_hat` and `omega = 2*pi*f`. A wave traveling along +x therefore has spatial factor `exp(+i*k*x)` under this time convention. Source phase is the argument of its peak phasor in radians. Complex values, when needed by result schemas, are explicit real/imaginary components with units; strings such as `"1+2j"` are not physical-number input.

For a single zero-mean sinusoid, `q_rms = abs(q_hat)/sqrt(2)` and peak-to-peak amplitude is `2*abs(q_hat)`. An adapter for an `exp(+i*omega*t)` source must conjugate all related phasors consistently; switching only the label is invalid. These conventions follow the harmonic and averaging definitions in Settnes and Bruus, Eq. (8)–(11), [primary article](https://doi.org/10.1103/PhysRevE.85.016327), [reviewed full text](https://bruus-lab.dk/TMF/publications/Bruus/Bruus_101.pdf).

## Intensity and attenuation

Keep the existing helper restricted to a plane progressive wave in the specified fluid: `I = p_rms^2/(rho*c)`. Its derivation and scope are EQ-004 in the [equation register](../registers/equations.md). Standing or mixed fields require pressure and fluid velocity for their energy-flux calculation; no general pressure-only conversion is introduced.

Define amplitude attenuation by `A(x) = A(0)*exp(-alpha_amp*x)` with nonnegative `alpha_amp` in 1/m. Squaring this definition gives the corresponding intensity decay coefficient `2*alpha_amp` where intensity is proportional to squared amplitude. A source's coefficient must state which convention it uses. Frequency-dependent loss laws require their own source and equation record; none is selected here.

## Review findings and implementation limits

The wavelength/k/ka/RMS-intensity helper equations match the selected restricted conventions. The historical coercion and range failures are preserved in the [FND-01 review](../work-items/FND-01.md). FND-02 rejects invalid serialized inputs, and [FND-03](../work-items/FND-03.md) now hardens the pure helpers and verifies the explicit conversions. Finite binary64 rounding and the formulas' physical applicability remain separate limitations.

This contract chooses representation, not material, frequency, radius, actuator power or a force model. Those physical choices remain explicit sourced or labeled manufactured inputs.
