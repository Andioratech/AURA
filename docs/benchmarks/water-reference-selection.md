# Water Reference Selection and Benchmark Design

**Prepared:** 2026-10-03 · **Work item:** LIT-02 · **Decision status:** exploratory reference selected; formal measurement benchmark INDETERMINATE

This record compares primary measurements for the small-particle-in-water campaign. It does not establish physical validation, choose hardware, infer unavailable data, or freeze a model tolerance. The preferred exploratory reference is SRC-W03 (Barnkob et al., 2012); access to its reported raw velocity fields is the remaining evidence gate. Muller et al. (2013) is retained as a three-dimensional alternative and discrepancy check.

## Search and source trace

The two-cycle search cap in the execution protocol was used. Search terms and date: 2026-10-03.

| Cycle | Search terms | Result |
|---|---|---|
| 1 | `site:aps.org Barnkob Augustsson Laurell Bruus 2012 056307 microparticle image velocimetry supplementary data`; `Barnkob 2012 Acoustic radiation streaming induced microparticle velocities supplementary data raw measurements uncertainty`; `Muller 2013 Ultrasound-induced acoustophoretic motion of microparticles in three dimensions supplementary data velocity field uncertainty`; `site:arxiv.org acoustophoretic microparticle velocity measured water acoustic radiation streaming Barnkob data` | Identified the 2012 micro-PIV source and the 2013 3D APTV alternative. |
| 2 | `"Acoustic radiation- and streaming-induced microparticle velocities" "Supplemental Material"`; `"Ultrasound-induced acoustophoretic motion of microparticles in three dimensions" "Supplemental Material"`; `"056307" "Raw data" Barnkob micro-PIV 2012`; `"023006" "data availability" Muller acoustophoretic` | APS lists the 2012 supplement as subscription-required. The 2013 author manuscript exposes figures, bin means and SEM, but no raw measurement arrays were found in the reviewed public material. |

Primary records:

| ID | Citation and access record | Relevant locator |
|---|---|---|
| SRC-W03 | R. Barnkob, P. Augustsson, T. Laurell, H. Bruus, “Acoustic radiation- and streaming-induced microparticle velocities determined by micro-PIV in an ultrasound symmetry plane,” *Physical Review E* 86, 056307 (2012), DOI [10.1103/PhysRevE.86.056307](https://doi.org/10.1103/PhysRevE.86.056307). [Author manuscript](https://arxiv.org/html/1208.6534); [APS record](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.86.056307). | Sections III–IV; Eqs. (1)–(22); Tables I–V; Figs. 1, 6–8. The text says the supplement contains the 22 measured velocity fields, Coulter-counter particle-size data and acquisition details. APS marks the supplement subscription-required. |
| ALT-W01 | K. Muller et al., “Ultrasound-induced acoustophoretic motion of microparticles in three dimensions,” *Physical Review E* 88, 023006 (2013), DOI [10.1103/PhysRevE.88.023006](https://doi.org/10.1103/PhysRevE.88.023006). [Author manuscript](https://arxiv.org/html/1303.0201); [APS record](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.88.023006). | Experimental setup and calibration; Figs. 5–8; 0.5 µm and 5.33 µm particle cases, 3D bins, SEM maps and calibration discussion. |

No new physical constants were taken from secondary summaries. Source access and the absence of downloadable raw arrays describe this search, not a claim that data do not exist elsewhere.

## Post-LIT-02 access follow-up

A later continuation checked the exact APS supplemental-material route after LIT-02 had completed its two-cycle literature search. The primary article explicitly identifies the supplement as containing all 22 measured velocity fields, the Coulter-counter data and the logged acquisition table. APS labels the supplement **Subscription Required** on its [official article page](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.86.056307). The direct [APS supplement route](https://journals.aps.org/pre/supplemental/10.1103/PhysRevE.86.056307) returned HTTP 401 in the unauthenticated retrieval used for this follow-up. No file was downloaded or inspected. Owner/institutional access has not been tested. Thus the data are known to exist in an official supplement, but their bytes, fields, metadata and checksums remain unavailable to this checkout. This finding does not change the formal benchmark status or the earlier LIT-02 search record.

The follow-up also searched university repository records for the DOI and the phrase “all measured acoustophoretic velocity fields.” It found the publication record and a DTU-hosted thesis that cites the APS supplement, but no public copy of the raw field files. This was a targeted access check rather than a new exhaustive literature search; it does not prove that no other copy exists.

## Candidate comparison

| Criterion | SRC-W03 — Barnkob et al. (2012) | ALT-W01 — Muller et al. (2013) |
|---|---|---|
| Observable | 2D micro-PIV particle-velocity vector fields in the ultrasound symmetry plane; particle motion combines streaming advection and radiation-force response. It is not a direct force measurement. | 3D acoustophoretic particle velocities from APTV; binned means and SEM are reported. It is not a direct force measurement. |
| Material / fluid | Polystyrene spheres suspended in pure Milli-Q water in series MQ1; particle diameters 0.6, 1.0, 1.9, 2.6, 5.1 and 10.2 µm are listed. Water temperature 25 °C. | Polystyrene spheres of 0.537 µm and 5.33 µm in water; temperature controlled at 25 °C. |
| Geometry / drive | Silicon-glass rectangular channel, length 35 mm, width 377 µm, height 157 µm; transverse standing half-wave resonance, 1.940 MHz. The measured symmetry-plane field of view is 892 × 446 µm. MQ1 is one of 22 field datasets across the article’s series. | Same family of 35 mm × 377 µm × 157 µm channel and 1.940 MHz transverse resonance; three-dimensional spatial sampling. More complex observable and reconstruction. |
| Calibration / fitting | Measured velocities are normalized to 1 V using a voltage-squared law. Table IV(a) fits all points and reports MQ1 `E_ac = 31.807 ± 0.569 J/m³`, `s = 0.247 ± 0.071`; Table IV(b) uses the 0.6 and 10 µm endpoint method and reports `32.436 ± 1.282 J/m³`, `s = 0.182 ± 0.008`. These are distinct fitting procedures, not interchangeable measurements. | The 5.33 µm case calibrates acoustic energy using only five near-centerline trajectories: `20.6 ± 0.7 J/m³`. Voltage scaling then gives `65 ± 2 J/m³` for 0.537 µm particles. This makes the small-particle calibration dependent on the separate large-particle trajectory fit. |
| Uncertainty / data | Article describes measured particle-size distributions, velocity fields and acquisition data in the supplement; the reported normalized-velocity standard deviation is smaller than plotting symbols, while particle-size spread is shown separately. Raw fields and full acquisition metadata are currently inaccessible to this checkout. Table V ratios have no reported uncertainty interval. | Maps include bin counts and SEM; typically 20–70 measurements per bin, with average absolute error about 1 µm/s and average relative error about 4%. Authors report measured velocity about 20% above the prediction on average and outside the combined stated 1σ uncertainty. Preserve this discrepancy. Raw arrays were not found in accessible reviewed material. |
| Model coupling / scope | Explicitly couples radiation and streaming contributions and includes wall-drag and thermoviscous corrections. Useful to study the measured particle response across size; not an isolated radiation-force benchmark. | Couples radiation and streaming with wall and thermoviscous effects. Useful for 3D distribution and calibration sensitivity; greater geometry/reconstruction complexity. |
| Reproduction burden | Low-to-moderate if the supplement is obtained; high uncertainty if reconstructed from figures only. | Moderate-to-high; 3D binning and cross-size calibration must be reproduced, and current public data are figure/map level. |

The article-reported material values relevant to the MQ1 case include polystyrene density 1050 kg/m³, sound speed 2350 m/s (source notes this value at 20 °C), and calculated compressibility 249 TPa⁻¹; water density 997 kg/m³, sound speed 1497 m/s, and viscosity 0.890 mPa·s at 25 °C. These are source-reported inputs, not independently measured values for a new AURA setup. Their temperature and derivation qualifications must travel with any future use. The article reports the field view, interrogation grid and depth-of-correlation limits; the latter vary from 14 to 94 µm with particle size, so the nominal symmetry-plane interpretation also has a finite optical sampling depth.

## Decision and limits

**Exploratory reference:** retain SRC-W03, specifically the 25 °C pure-water MQ1, 1.940 MHz transverse half-wave series. It has the most informative size-resolved, spatially resolved water-particle measurements among the reviewed candidates and the source describes a complete set of 22 discrete fields. Use the measured velocity field as the observable; do not relabel it as force. Use the article’s fitted energy-density and streaming values only as separately identified, calibration-dependent reported quantities.

**Formal selection:** DEFER / INDETERMINATE. The raw MQ1 field, pointwise uncertainty/correlation, and complete acquisition values are in subscription-gated supplemental material not available here. Figure digitization would add a separate extraction uncertainty and cannot replace the missing measurement uncertainty. Neither a formal acceptance tolerance nor an experimental-validation decision rule is justified yet. Do not fit and test on the same velocity points: a future protocol must reserve data or compare a preregistered model against measurements not used for calibration.

ALT-W01 remains a cross-check if a three-dimensional map is needed. It does not remove the data-access problem and its approximately 20% model-data discrepancy must remain visible; it is not a tolerance or an unexplained correction factor. Both sources come from a closely related microchannel research program, so agreement between them would not by itself be independent confirmation.

This decision retains the approved small-particle-in-water starting campaign and does not alter the broader staged objective in DEC-004. No owner scope choice is needed. Before formal benchmark acceptance, obtain authorized access to SRC-W03’s supplement (or another primary dataset with traceable raw measurements), capture the exact data/version, and define the measurement uncertainty and holdout/calibration split. No purchase, author contact or hardware selection is implied.

## Matching table and future benchmark protocol

| Field | Frozen exploratory match | Missing before formal measurement acceptance |
|---|---|---|
| Reference | SRC-W03, MQ1, 25 °C, pure Milli-Q water, 1.940 MHz, transverse half-wave (`λ/2 = 377 µm` per source setup) | Exact source supplement version and original digital values/checksum. |
| Particle | Polystyrene sphere; six nominal/listed diameters 0.6, 1.0, 1.9, 2.6, 5.1, 10.2 µm | Per-batch size distributions, raw Coulter counts, shape/surface characterization and covariance. |
| Channel / observation | 35 mm × 377 µm × 157 µm channel; symmetry plane; 892 × 446 µm field of view; reported 79 × 39 interrogation grid for MQ series | Exact MQ1 image/acquisition parameters, coordinate registration and covariance/correlation of spatial bins. |
| Drive / calibration | Source’s actual drive normalized to 1 V under stated voltage-squared scaling; acoustic-energy fits retained as separate Table IV methods | Original per-run drive values, measured field calibration traceability and uncertainty; avoid using test points for calibration. |
| Primary comparison quantity | Particle velocity vector field by size and spatial position; preserve streaming plus radiation response | Raw values, pointwise and systematic uncertainty, replicate hierarchy, digitization procedure if unavoidable. |
| Acceptance | None frozen | Domain-specific uncertainty model, independent/holdout comparison set and tolerance derived before evaluation. |

If the supplement becomes available, first verify source identity and checksums; transcribe units, coordinates and run metadata; independently inspect a sample against the publication; preserve raw data unchanged; then define calibration and holdout partitions. If only published plots remain available, retain a separately named figure-digitized exploratory dataset with two independent digitizations and sensitivity, and leave formal validation INDETERMINATE. Do not manufacture uncertainty or silently repair discrepant points.

## Separate synthetic verification case

`SYN-WATER-01` is a manufactured known-answer **data-path** fixture, not an experiment, water case, physical model, or run. It checks future parsing, coordinate ordering, vector-component handling and exact values only. Its arbitrary test units and values are intentionally not physical:

| Point | `y` (synthetic m) | `u_x` (synthetic m/s) | `u_y` (synthetic m/s) |
|---|---:|---:|---:|
| 1 | −0.5 | 0 | −1 |
| 2 | 0 | 0 | 0 |
| 3 | +0.5 | 0 | +1 |

Manufacturing rule: `w_SYN = 2 m`, `U_SYN = 1 m/s`, `u_x = 0`, and `u_y = U_SYN sin(2π y / w_SYN)` at the three listed points. Expected values are exact by construction. A later implementation may use this only to test data ingestion and vector metrics; passing it cannot verify acoustic fields, particle forces, fluid dynamics or any water measurement. Keep the `SYN-` identity separate from `SRC-` evidence, experimental identifiers, RUN-IDs and scientific results. No executable run was made for this documentary task.

## Bibliographic sources

1. Barnkob et al. (2012), DOI 10.1103/PhysRevE.86.056307; arXiv:1208.6534v1, manuscript dated 2012-08-31. Primary source and locators above.
2. Muller et al. (2013), DOI 10.1103/PhysRevE.88.023006; arXiv:1303.0201. Primary source and locators above.
