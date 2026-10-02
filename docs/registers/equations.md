# Equation and Convention Register

**Register version:** 1.3 · **Date:** 2026-10-02

This register records current algebra and representation choices. Source review, implementation verification and experimental validation are distinct statuses. No force model or simulator is validated by this table.

## Shared reference

SRC-E01: M. Settnes and H. Bruus, *Physical Review E* 85, 016327 (2012), [DOI](https://doi.org/10.1103/PhysRevE.85.016327), [author-hosted text](https://bruus-lab.dk/TMF/publications/Bruus/Bruus_101.pdf). Metadata and relevant locators were read on 2026-10-02: Eq. (6), linear fluid equations; Eq. (8), harmonic convention; Eq. (9)/(11), time averaging; Sec. III after Eq. (16), bulk inviscid wave equation. No force coefficient from this article is implemented in this work item.

| ID | Equation / units | Source and assumptions | Current implementation / independent check |
|---|---|---|---|
| EQ-001 | `lambda = c/f`, m | Insert a single-frequency traveling-wave ansatz into SRC-E01's homogeneous bulk wave equation; positive c and f, lossless phase-speed interpretation | `aura.units.wavelength_m`; B01-01, B01-02 |
| EQ-002 | `k = 2*pi*f/c = 2*pi/lambda`, rad/m | Same ansatz and one full phase turn over a wavelength; fixed harmonic convention | `aura.units.wave_number_rad_m`; B01-03 |
| EQ-003 | `ka = k*a`, dimensionless | Definition using spherical radius a; indicator only, not an applicability proof | `aura.units.size_parameter_ka`; B01-04; unrelated geometries need their own length definition |
| EQ-004 | `I = p_rms^2/(rho*c)`, W/m² | From SRC-E01 Eq. (6) in an inviscid homogeneous progressive plane wave: velocity in phase with pressure and amplitude ratio 1/(rho*c); average pressure times velocity with Eq. (11) | `aura.units.plane_progressive_wave_intensity_w_m2`; B01-05; not a cavity/standing-wave conversion |
| EQ-005 | `q_rms = abs(q_hat)/sqrt(2)` | Integrate squared real sinusoid over one period using SRC-E01 Eq. (8)/(9); peak complex phasor, zero mean | `sinusoid_peak_to_rms` / `sinusoid_rms_to_peak` accept nonnegative amplitude magnitudes; B01-06 |
| CONV-001 | `Re(q_hat*exp(-i*omega*t))` | SRC-E01 Eq. (8); source-phase sign and amplitude convention chosen for the project | Frozen in CONV-1.0; field implementation later |
| CONV-002 | `A(x)/A(0) = exp(-alpha_amp*x)` | Project definition of amplitude attenuation; the factor two for squared-amplitude decay follows algebraically | `amplitude_to_intensity_attenuation_per_m` and its inverse implement the coefficient convention; not a loss model |

## Implementation status and limitations

FND-03 hardens EQ-001–EQ-004 and implements the explicit EQ-005/CONV-002 adapters without changing their equations or assumptions. The [numeric-domain contract](../research/numerical-domain-and-conversions.md) records the supported input/output range and conversion limitations. New externally serialized inputs must follow CONV-1.0; algebraic agreement alone cannot establish model applicability or experimental agreement. The [fixture specification](../research/foundation-reference-values.md) contains manufactured values, tolerances and rejection criteria; [FND-03](../work-items/FND-03.md) records their execution. This minor register revision updates implementation status, not scientific evidence.

## Analytical additions specified by ANA-01

The [dated source review](../research/analytical-source-review.md) identifies SRC-E02 (MIT Lecture 2, 14 September 2004) and SRC-E03 (Lecture 3, 16 September 2004), including the conversion from their positive time sign. [FIELD-1.0](../research/analytical-field-contract.md) defines every symbol, normalization, unit and exclusion; [ANA-REF-1.0](../benchmarks/B03-B06-analytical-protocols.md) supplies independent sample values, component scales, numerical budgets and stop rules. These additions do not change a previous run or baseline equation.

| ID | Equation / units | Source, restriction and derivation | Planned implementation / independent cases |
|---|---|---|---|
| EQ-006 | `grad(p)=i omega rho v`, Pa/m; `div(v)=i omega p/(rho c^2)`, 1/s | SRC-E01 Eq. (6), drop viscosity in homogeneous stationary ideal-fluid model, insert CONV-001 | Implemented Euler-consistent plane-wave pair in `fields/analytic.py`; B-03 independent derivatives/direction variants; general divergence audit pending |
| EQ-007 | `p=A exp(i(k n dot (x-x_ref)+phi))`, Pa; `v=n p/(rho c)`, m/s; `grad(p)=i k n p`, Pa/m | SRC-E02 Eqs. (2.15)–(2.18), conjugate time convention; project rotation/phase-reference definition | Implemented `evaluate_plane_wave`; B-03 exact quarter-turn values, Decimal oracle and rational non-axis direction |
| EQ-008 | Componentwise sum of p, v and grad(p); equal opposite pair `p=2A cos(kx)`, `v_x=2i A sin(kx)/(rho c)` | Linear superposition; SRC-E02 Eqs. (2.24)–(2.25) with converted convention; project vector generalization | ANA-03/04; B-04 nodes/unbalanced pair and B-05 noncollinear cancellation |
| EQ-009 | `I=Re(p conj(v))/2`, W/m² | SRC-E03 Eq. (3.4), or direct average of peak real harmonics; ideal acoustic energy flux, not body force | Implemented `mean_intensity_w_m2`; B-03 directed flux and synthetic complex-vector arithmetic; B-04/B-05 and balances pending |
| EQ-010 | `p=P_ref(r_ref/r) exp(i(k(r-r_ref)+phi))`; `grad(p)=(ik-1/r)p n_r`; `v=(p/(rho c))(1+i/(kr))n_r` | SRC-E03 Eqs. (3.11)–(3.14), converted convention; project normalization/differentiation; ideal outgoing spherical wave, explicit r_min>0 | ANA-05; B06-01…03 radial tables and exclusion checks |
| EQ-011 | `4 pi r^2 I_r=4 pi r_ref^2 P_ref^2/(2 rho c)`, W | Project multiplication of EQ-009/010, real reactive term cancels; complete outward sphere within ideal lossless solution | ANA-06; B-06 independent surface-power reference; no universal momentum/force bound |

**Current status:** ANA-02 implements the bounded EQ-007 pressure/velocity/gradient pair and EQ-009 harmonic flux. B-03 kernel tests compare with independent hand/Decimal references; see [the kernel contract](../research/plane-wave-kernel.md) and [ANA-02](../work-items/ANA-02.md). General equation residual/balance audits, B-04…B-06, physical recorder admission and the P3 campaign remain pending. `fields/types.py` still validates representation only. Neither software verification nor this register establishes material-model validation or experimental agreement.
