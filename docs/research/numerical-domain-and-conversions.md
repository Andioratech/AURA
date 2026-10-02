# Scalar Numeric Domain and Explicit Conversion — FND-03

**Version:** 1.0 · **Date:** 2026-10-02 · **State:** Implemented arithmetic contract; no physical validation claim

This implements [CONV-1.0](si-and-conventions.md) and the [equation register](../registers/equations.md). The formulas and their physical assumptions are unchanged. Source code: [scalar helpers](../../src/aura/units.py), [quantity adapter](../../src/aura/schema/quantities.py), [typed errors](../../src/aura/errors.py).

## Numeric input and result policy

Public scalar helpers accept built-in `int` and `float` values only. Booleans, strings, null, complex values and other numeric classes require a separately reviewed adapter. Integers must fit the finite binary64 range; conversion can round large integers. This is ordinary binary64 arithmetic, not exact arbitrary-precision computation.

Speeds, frequencies, radii, wavelengths and diameters must be strictly positive. Peak/RMS amplitude magnitudes and attenuation coefficients may be zero but never negative. General quantity conversion preserves signed components; the full scenario schema subsequently enforces each field's physical range. Zero pressure does not bypass density/speed validation.

The four existing helpers retain their function names and arguments. Products and quotients are evaluated by separating binary mantissas and exponents, renormalizing each intermediate factor, and applying the final exponent once. This avoids unnecessary intermediate overflow or collapse to zero. It uses Python's documented [`frexp` and `ldexp`](https://docs.python.org/3.12/library/math.html#math.frexp); it does not use an acoustic solver or increase the floating-point precision.

| Outcome | Behavior |
|---|---|
| Invalid operand type | `InvalidInputError`, `NUMBER_TYPE`, operand path |
| Nonfinite or excessively large operand | `InvalidInputError`, `NONFINITE`, operand path |
| Violated positive/nonnegative requirement | `InvalidInputError`, `VALUE_RANGE`, operand path |
| Final overflow or a nonzero calculation rounded to zero | `NumericalDomainError`, `NUMERIC_RANGE`, result path |
| Exact zero allowed by the formula | Return zero; preserve conversion sign where represented |
| Finite nonzero subnormal result | Return it; accuracy needs a separate rounding-aware criterion |

`NumericalDomainError` inherits `InvalidInputError`, which inherits `ValueError`; earlier callers catching `ValueError` continue to catch these failures. Both expose code/path/message and `as_dict()`. Arithmetic result paths name the helper; the quantity adapter attaches the caller's enclosing JSON Pointer and vector index.

No accepted scalar result is infinity, NaN or an underflow-produced zero. Near binary64 range boundaries, ordinary rounding remains; these helpers do not promise correctly rounded multi-operation formulas, fixed relative error for subnormals, propagated uncertainty or arbitrary precision. A numeric-range rejection does not establish a physical impossibility or invalidate AURA's research hypothesis.

## Conversion coverage

`canonical_quantity(data, expected_unit=..., size=None, path="")` explicitly converts one `{value, unit}` object. Supply `size` for a vector of that exact length. It returns a fresh object and never changes the source data. The caller retains the raw input/provenance and validates the complete scenario after conversion.

| Accepted alternative spellings | Canonical unit | Multiplication factor |
|---|---|---|
| `um`, `mm`, `cm` | `m` | 10^-6, 10^-3, 10^-2 |
| `mg`, `g` | `kg` | 10^-6, 10^-3 |
| `us`, `ms` | `s` | 10^-6, 10^-3 |
| `kHz`, `MHz` | `Hz` | 10^3, 10^6 |
| `kPa`, `MPa` | `Pa` | 10^3, 10^6 |
| `deg` | `rad` | pi/180 |

Canonical units from CONV-1.0 also support identity conversion. Prefix factors, gram/kilogram handling and the degree definition were checked against BIPM's *SI Brochure*, 9th edition, version 4.01 (June 2026), Chapter 3/Table 7, the mass paragraph, and Chapter 4/Table 8, printed pages 138–140. [Official brochure](https://www.bipm.org/en/publications/si-brochure). `um`, `us` and `deg` are the project's explicit ASCII spellings. Other aliases, offset temperatures, logarithmic units, compound-unit simplification and arbitrary prefix parsing are unsupported.

An unknown spelling gives `UNIT_UNSUPPORTED`; a supported unit for a different quantity gives `UNIT_MISMATCH`. The expected unit must itself be canonical. Generic dimensionless numbers are not angles; angular frequency is not temporal frequency; the symbol `g` denotes grams in this adapter, never an inferred gravity acceleration. Invalid vector shapes give `SCHEMA_INVALID`.

The version-1.0 JSON/YAML reader remains strict: a millimetre quantity must be explicitly converted before schema acceptance. No automatic whole-scenario rewrite, radius/diameter reinterpretation, phase wrapping, model selection or physical default is introduced.

```python
from aura.schema import canonical_quantity
from aura.units import radius_from_diameter_m, sinusoid_peak_to_rms

length = canonical_quantity({"value": 1, "unit": "mm"}, expected_unit="m")
assert length == {"value": 0.001, "unit": "m"}
radius = radius_from_diameter_m(0.002)  # Explicit diameter in metres.
rms = sinusoid_peak_to_rms(2.0)  # Nonnegative peak magnitude, one zero-mean sinusoid.
```

## Acoustic and geometry adapters

- `sinusoid_peak_to_rms` and `sinusoid_rms_to_peak` implement EQ-005 in both directions. Their input is a nonnegative magnitude; they do not compute a phasor norm or handle an arbitrary waveform/DC component.
- `radius_from_diameter_m` divides a positive diameter by two. It does not reinterpret a serialized radius field or transform another geometry into a sphere.
- `amplitude_to_intensity_attenuation_per_m` and its inverse implement CONV-002's factor of two for exponential decay where intensity is proportional to amplitude squared. They do not select a medium loss model or interpret decibels.
- `plane_progressive_wave_intensity_w_m2` remains restricted to EQ-004's progressive-plane-wave fluid assumptions. No standing-wave/cavity conversion or universal force bound was added.

The selected harmonic and averaging source is already located and reviewed in the equation register. These adapters implement its declared conventions, not evidence of achievable force or acceleration at any scale.

## Verification scope

See [FND-03](../work-items/FND-03.md) for the preserved old failures, B01 mapping, test counts and delivery gate. Normal B01 cases retain their frozen tolerances; extreme cases use separately specified criteria. No measurement uncertainty or simulation acceptance threshold was selected by these software checks.
