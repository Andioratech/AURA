# B-01 — Independent Foundation Reference Values

**Protocol:** B01-v1.0 · **Frozen:** 2026-10-02 · **Owner task:** FND-01, execution in FND-03/FND-05

All values below are manufactured arithmetic checks, not measured water properties or selected operating points. Expected numbers are calculated independently of the implementation. Scalar float comparisons use relative tolerance 1e-12 and absolute tolerance 1e-15 for these order-one/millimeter values: these allow rounding from decimal fixtures and a few binary64 operations while remaining far below any physical measurement tolerance. This is not a universal simulation acceptance rule. Unit/name/shape rejection and diagnostic identifiers are exact checks.

| ID | Inputs | Expected value / outcome | Independent derivation |
|---|---|---|---|
| B01-01 | c = 343 m/s, f = 70 Hz | wavelength 4.9 m | 70 * 4.9 = 343 |
| B01-02 | c = 1500 m/s, f = 1000000 Hz | wavelength 0.0015 m | Decimal division by 10^6 |
| B01-03 | c = 2 m/s, f = 1 Hz | k = 3.141592653589793 rad/m | A two-meter wavelength spans one full turn |
| B01-04 | a = 0.5 m, wavelength = 2 m | ka = 1.5707963267948966 | Quarter of a full phase turn |
| B01-05 | p_rms = 2 Pa, rho = 2 kg/m³, c = 4 m/s | intensity = 0.5 W/m² | 4 / 8 |
| B01-06 | harmonic peak = 2 Pa | RMS = 1.4142135623730951 Pa | Integral of 4*cos² over a full period equals 2 |
| B01-07 | radius = 0.001 m vs equivalent supported input 1 mm | Same canonical length after FND-03 conversion | 1000 mm per m |
| B01-08 | diameter 0.002 m | radius 0.001 m only via an explicit diameter adapter | Divide diameter by 2; never reinterpret a radius field |
| B01-09 | gravity = [0, 0, 0] m/s² | Remains explicit zero gravity | No terrestrial default |
| B01-10 | boolean or numeric-string physical value | Reject with field path | Types are not explicit physical numbers |
| B01-11 | missing required temperature, invalid unit or two-element vector | Reject with field path | Contract check before solver allocation |
| B01-12 | finite operands whose result cannot be represented | Controlled numerical-domain error in FND-03 | No accepted infinity/NaN/zero from unsupported arithmetic underflow |

The existing loose approximate ka check for the air sphere is a domain illustration, not a model validation benchmark. It does not replace the independent manufactured checks here. No experiment/run identity is assigned to these unit-check fixtures; scientific solver runs do not yet exist.
