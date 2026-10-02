# Equation and Convention Register

**Register version:** 1.0 · **Date:** 2026-10-02

This register records current algebra and representation choices. Source review, implementation verification and experimental validation are distinct statuses. No force model or simulator is validated by this table.

## Shared reference

SRC-E01: M. Settnes and H. Bruus, *Physical Review E* 85, 016327 (2012), [DOI](https://doi.org/10.1103/PhysRevE.85.016327), [author-hosted text](https://bruus-lab.dk/TMF/publications/Bruus/Bruus_101.pdf). Metadata and relevant locators were read on 2026-10-02: Eq. (6), linear fluid equations; Eq. (8), harmonic convention; Eq. (9)/(11), time averaging; Sec. III after Eq. (16), bulk inviscid wave equation. No force coefficient from this article is implemented in this work item.

| ID | Equation / units | Source and assumptions | Current implementation / independent check |
|---|---|---|---|
| EQ-001 | `lambda = c/f`, m | Insert a single-frequency traveling-wave ansatz into SRC-E01's homogeneous bulk wave equation; positive c and f, lossless phase-speed interpretation | `aura.units.wavelength_m`; B01-01, B01-02 |
| EQ-002 | `k = 2*pi*f/c = 2*pi/lambda`, rad/m | Same ansatz and one full phase turn over a wavelength; fixed harmonic convention | `aura.units.wave_number_rad_m`; B01-03 |
| EQ-003 | `ka = k*a`, dimensionless | Definition using spherical radius a; indicator only, not an applicability proof | `aura.units.size_parameter_ka`; B01-04; unrelated geometries need their own length definition |
| EQ-004 | `I = p_rms^2/(rho*c)`, W/m² | From SRC-E01 Eq. (6) in an inviscid homogeneous progressive plane wave: velocity in phase with pressure and amplitude ratio 1/(rho*c); average pressure times velocity with Eq. (11) | `aura.units.plane_progressive_wave_intensity_w_m2`; B01-05; not a cavity/standing-wave conversion |
| EQ-005 | `q_rms = abs(q_hat)/sqrt(2)` | Integrate squared real sinusoid over one period using SRC-E01 Eq. (8)/(9); peak complex phasor, zero mean | Conversion planned for FND-03; B01-06 |
| CONV-001 | `Re(q_hat*exp(-i*omega*t))` | SRC-E01 Eq. (8); source-phase sign and amplitude convention chosen for the project | Frozen in CONV-1.0; field implementation later |
| CONV-002 | `A(x)/A(0) = exp(-alpha_amp*x)` | Project definition of amplitude attenuation; the factor two for squared-amplitude decay follows algebraically | Validation of convention in FND-02; conversion work in FND-03 |

## Implementation status and limitations

EQ-001–EQ-004 already have basic tests. Their numerical-domain edge cases are incomplete and are assigned to FND-03. New externally serialized inputs must follow CONV-1.0; algebraic agreement alone cannot establish model applicability or experimental agreement. The [fixture specification](../research/foundation-reference-values.md) contains manufactured values, tolerances and anticipated invalid-input outcomes.
