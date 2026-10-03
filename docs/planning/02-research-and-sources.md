# 02 — Research Program and Primary Source Register

## Research products

Research must produce a usable equation record, property table, benchmark specification, model-selection decision or limit argument. A bibliography alone does not close a task. Store new research notes in `docs/research/`, benchmark definitions in `docs/benchmarks/`, and source/equation/claim records under `docs/registers/` when those tasks execute.

## Questions and work products

| Question | Required investigation | Deliverable | Used by |
|---|---|---|---|
| Which water experiment can be reproduced? | Geometry, particle/material, fluid state, drive calibration, measured observable, uncertainty, access/license | Candidate comparison and selected water dossier | LIT-02, FOR-05 |
| Which particle-force approximation applies? | Wavelength, particle and boundary-layer scales; material contrast; wall/source distance; field amplitude | Regime map and equation records | LIT-03, FOR-01 |
| How much motion comes from the water? | Streaming, bulk flow and wall-drag corrections; separate calibration inputs | Force inventory and fluid model decision | LIT-04, FOR-06, MOT-01 |
| What limits acceleration? | Force reachability, drag demand over time, workspace, response bandwidth, pressure and power constraints | Necessary-condition analysis and adversarial cases | LIT-05, CTL-01, ADV-01 |
| What changes in microgravity? | Residual acceleration spectrum, frame definition, buoyancy/flow changes, measurement assumptions | Earth/ideal/residual-gravity comparison contract | MOT-06, ADV-04 |
| Could thermal, stochastic or collective effects reverse the answer? | Temperature dependence, Brownian scales, interactions and heating under proposed operation | Omitted-effects budget and branch triggers | FOR-06, MOT-01, ADV-02 |
| What has already been done? | Acoustic manipulation, controlled particle motion and acceleration under comparable assumptions | Dated closest-prior-work and novelty comparison | IND-04, EXP-01 |

## Verified starting sources, checked 2026-10-02

These are starting points, not an exhaustive or newest-literature review. Publication years below come from article metadata, not search-engine crawl dates. Full equation transcription and scenario matching remain task deliverables.

### SRC-W01 — Viscous particle force

M. Settnes and H. Bruus, “Forces acting on a small particle in an acoustical field in a viscous fluid,” *Physical Review E* 85, 016327 (2012). [DOI](https://doi.org/10.1103/PhysRevE.85.016327); [author-hosted full text](https://bruus-lab.dk/TMF/publications/Bruus/Bruus_101.pdf).

Metadata and relevant full-text sections were inspected. Useful locators are Eq. (1), viscous penetration depth; Eqs. (8)–(11), harmonic/averaging convention; Eq. (14), force from a surrounding momentum-flux surface. The paper's small-particle and small-boundary-layer assumptions relative to wavelength must accompany any implementation. LIT-03 must record the exact selected force coefficients and their assumptions before coding. Reading this source does not approve a universal radius cutoff.

### SRC-W02 — Thermoviscous refinement

J. T. Karlsen and H. Bruus, “Forces acting on a small particle in an acoustical field in a thermoviscous fluid,” *Physical Review E* 92, 043010 (2015). [DOI](https://doi.org/10.1103/PhysRevE.92.043010); [author-hosted full text](https://bruus-lab.dk/TMF/publications/pub2015/Karlsen_thermoviscous_radiation_force_PRE_92_043010_2015.pdf); [author manuscript record](https://arxiv.org/abs/1507.01043).

Metadata and the opening scope were checked. The analysis includes viscous and thermal effects for a small spherical particle, with different solid/droplet models. The model cannot be selected from radius alone. Detailed coefficient/equation review is still OPEN in LIT-03; do not describe the whole paper as already audited.

### SRC-W03 — Measured radiation/streaming motion candidate

R. Barnkob, P. Augustsson, T. Laurell and H. Bruus, “Acoustic radiation- and streaming-induced microparticle velocities determined by microparticle image velocimetry in an ultrasound symmetry plane,” *Physical Review E* 86, 056307 (2012). [DOI](https://doi.org/10.1103/PhysRevE.86.056307); [author manuscript](https://arxiv.org/abs/1208.6534); [full text](https://arxiv.org/pdf/1208.6534).

Metadata and Sec. II were inspected. Eqs. (1)–(4) connect the specified transverse field, radiation force and terminal motion; Sec. II.B treats boundary-driven streaming. This is a candidate for distinguishing fluid transport from radiation-driven particle response. It is not an acceleration or microgravity validation. LIT-02 compared its dataset availability, calibration dependence, uncertainty and matching against ALT-W01; see the [selection record](../benchmarks/water-reference-selection.md). Formal measurement acceptance remains INDETERMINATE.

### SRC-A02 — Acoustic force and levitation precedents

The bounded LIT-05 comparison is in the [prior-work register](../registers/prior-work.md). It covers NASA's measured one-axis forces across several body shapes (Oran et al., 1979), microgravity sample positioning (Trinh, 1989), opposed-array 3D EPS manipulation (Ochiai et al., 2014), reduced-gravity droplet transport/coalescence (Hasegawa et al., 2019), and microgravity trapping of filamentous cyanobacteria (Dupont et al., 2026). These records rule out broad novelty claims about acoustic levitation, phased-array 3D manipulation or acoustic trapping in reduced gravity. They do not settle whether a later, explicitly bounded acceleration-tracking question is novel. The search was not exhaustive.

### SRC-A01 — Existing air reference

Use the source/provenance already recorded in [P1.3](../benchmarks/P1.3-andrade-force-curve-specification.md). Preserve its missing-uncertainty limitation and figure-reading metadata. Do not transplant its material model or uncertainty into water cases.

## Search procedure for LIT tasks

1. Write one question and search terms, including medium, particle/material, geometry and desired observable.
2. Search original papers, publisher records, author repositories and archived supplements. Record unsuccessful searches as well as matches.
3. Inspect title/authors/year/DOI, full text, relevant equation/figure/table, assumptions and correction/erratum history.
4. Follow citations backward for the equation and forward for corrections or a more appropriate regime. Record the access date and exact version.
5. Extract each numeric property with units, temperature, material/composition and uncertainty. Never merge incompatible temperatures or different material grades without an explicit approximation study.
6. Distinguish independently measured inputs from fitted/calibrated values. A benchmark using the same observation for amplitude calibration and evaluation needs separate held-out data or an explicit conditional interpretation.
7. Score candidates against completeness, relevant regime, independent observables, uncertainty, reproducibility, numerical cost and access rights. Missing uncertainty is a visible weakness, not an arbitrary score that can be averaged away.
8. Close with SELECT, REJECT or DEFER and a reason. Apply the two-cycle research rule in [00](00-execution-protocol.md).

No emails, author outreach, paid acquisition or publication occurs automatically. Prepare an exact request if those become necessary; continue independent tasks while access is unresolved.

## Equation record fields

Assign EQ identifiers on registration. Store full source locator, equation in the project's notation, symbols and SI units, amplitude/phasor conventions, assumptions, asymptotic conditions, retained/omitted terms, implementation path, independently derived check, tolerance rationale, test IDs and review status. Never mark `verified` solely because a DOI resolves.

## Property and assumption record fields

For each value: property ID, SI value/range, uncertainty type, source locator, material and temperature, interpolation method, measured/fitted/assumed status, affected equations, sensitivity experiment and expiration/review condition. If an assumption materially changes the conclusion, branch to a new experiment and report both outcomes.

## Closing the research track

The initial research gate can close with a clearly bounded incomplete comparison under DEC-003. Formal validation remains unavailable where required measurement or model evidence is missing. Reopen literature review at every changed material, scale, boundary configuration or control capability; do not carry a previous validation across an unmatched domain.
