# Bounded Harmonic Energy-Balance Audit

**Contract:** ENERGY-BALANCE-1.0 · **Date:** 2026-10-02 · **Owner:** [ANA-06](../work-items/ANA-06.md)

## Physical identity and use

Start from FIELD-1.0's negative-time phasors, [SRC-E01](analytical-source-review.md) Eq. (6) and [SRC-E03](analytical-source-review.md) Eq. (3.4). In a homogeneous inviscid fluid away from sources and losses, the time-average of the linear momentum and continuity equations yields `div(I)=0`, `I=Re(p_hat*conj(v_hat))/2`. Integrating over a closed surface gives zero net outward energy flux for a source-free control volume. For the outgoing spherical reference, differentiating the full radial pressure and retaining its reactive velocity gives `I_r=A^2/(2Z)*(r_ref/r)^2`; the exact complete-sphere power is independent of radius. The B-06 derivation is in the [spherical-wave contract](spherical-wave-kernel.md).

The calculations apply only to the manufactured, steady, single-frequency, homogeneous, linear, inviscid, lossless incidents and explicit control volumes in [ANA-06](../work-items/ANA-06.md). Plane-wave phase references are mathematical phase origins; they are not source boundaries. The spherical shell's two radii both exceed the selected exclusion region. This audit accounts for acoustic energy flux. It does not calculate linear momentum flux, radiation force, body acceleration or gravity.

## Surface integral and explicit terms

For surface samples `j` with outward unit normal n_j and area weight w_j, calculate `P_surface = sum_j w_j*(I_j dot n_j)`. A closed sphere contributes its one outward power. A concentric spherical shell contributes outer power minus inner-sphere outward power. The frozen six-point axes and equal area weights are exactly antipodal, integrate area/first moments, and match the stated inversion-symmetric plane cases. Spherical radial intensity is constant on each selected sphere. Do not apply this rule to an arbitrary field or surface geometry; no general quadrature accuracy is claimed.

Use the explicit ledger `residual = sum(signed surface powers) + absorbed power - internal source power`. Supply source, absorption and a positive global reference scale explicitly. In the ideal cases these terms are declared zero as part of the mathematical model; this is not evidence that real apparatus has no losses. If any required value is unknown, return an `INDETERMINATE` diagnostic. Never replace missing evidence with zero. A `PASS` here is only a numerical model-specific balance comparison, not MCLF `ACCEPTED`, validation or experimental evidence.

The frozen comparison uses positive global power scales and the specific `8192*2^-52` budget derived in the task record. It is not a general-purpose cubature tolerance. Orientation, source/sink signs, sampling completeness and exact field/sample association are checked before evaluating the residual.

## Limits and continuation

Physical source power, real absorption, acoustic-to-mechanical momentum, body coupling, transient stored energy and arbitrary/multiply connected surfaces remain uncovered. Do not adapt the progressive-wave force estimate to interference or a resonant cavity. Larger bodies/masses and eventual microgravity research keep their DEC-004 model and evidence gates.
