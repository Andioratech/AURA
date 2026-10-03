# NUM-W01 — Reconcile the Existing Water Numerical Qualification

**Status:** DONE · **Date:** 2026-10-03 · **Decision:** Bounded software qualification PASS; physical water validation remains INDETERMINATE

## Question and scope

The task checked whether the owner's reported water-related numerical comparison is supported by immutable artifacts and whether it establishes enough software workflow capability to proceed to the air P4 field work. It did not attempt to validate water physics or measurements.

## Evidence and result

See the [NUM-W01 audit](../reviews/NUM-W01-water-numerical-qualification-audit.md). P3 ANA-07 supplies 32 analytical ideal-field cases and 264 independent reference samples. ANA-06 supplies four passing energy ledgers with explicitly ideal, lossless `rho=1000 kg/m³`, `c=1500 m/s`, `f=1 MHz` inputs. RUN-02 reproduces an admitted analytical field case exactly. These records support repeatable calculation/comparison in that manufactured water-like software scope.

They do not establish a water-specific numerical PDE/scattering solver or physical agreement with SRC-W03. The SRC-W03 figure extraction is repeatable, but original numerical measurements and a complete uncertainty budget remain unavailable. Formal measurement acceptance stays INDETERMINATE.

## Disposition

- **NUM-W01 task:** DONE.
- **Water-like ideal analytical workflow:** PASS within the bounded evidence above.
- **Water field-solver verification:** NOT ESTABLISHED; NUM-W02 not activated because this is outside the capability claim needed for the ordered route.
- **Water physical/measurement validation:** INDETERMINATE.
- **Next:** continue to air P4 NUM-01; preserve its distinct air references and acceptance criteria. Before solver-core implementation, explain the planned components, inputs, outputs, verification cases and limits in Spanish.

No code, dependency, benchmark tolerance, raw data or previous scientific result was changed. All source and measurement gaps remain visible.
