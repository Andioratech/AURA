# ANA-01 — Equation Source Review

**Date:** 2026-10-02 · **Reviewer role:** implementation/source self-review · **Status:** bounded equation review, not independent physical validation

Question: which primary linear-fluid relations support pressure, fluid velocity, pressure gradients and mean flux for the four selected analytical references? Search scope: author-hosted Settnes/Bruus text and MIT's original acoustics lecture PDFs; queries included `linear acoustic plane wave spherical wave pressure velocity phasor` and the source titles. Stop when the actual equations, conventions and source-normalization assumptions can be reconciled. No force-model selection or experimental-water literature gate is closed by this review.

## Sources inspected

| ID | Verified record and direct text | Inspected locators / use |
|---|---|---|
| SRC-E01 | Mikkel Settnes and Henrik Bruus, *Forces acting on a small particle in an acoustical field in a viscous fluid*, Physical Review E 85, 016327 (30 January 2012), [publisher](https://doi.org/10.1103/PhysRevE.85.016327), [author PDF](https://bruus-lab.dk/TMF/publications/Bruus/Bruus_101.pdf) | Printed page 016327-2, Eqs. (6), (8), (9)/(11); bulk inviscid restriction discussed in Sec. III. Linear-fluid starting point and negative harmonic time sign only; no particle-force coefficient admitted. |
| SRC-E02 | MIT OpenCourseWare, 6.551J/HST.714J, Lecture 2, *One-Dimensional Traveling Waves*, dated 14 September 2004 in the PDF; [course record](https://ocw.mit.edu/courses/6-551j-acoustics-of-speech-and-hearing-fall-2004/pages/lecture-notes/), [original PDF](https://ocw.mit.edu/courses/6-551j-acoustics-of-speech-and-hearing-fall-2004/1149b68a00a45f7c67d4a5c24ed08b51_lec_2_2004.pdf) | pp. 1–2 assumptions/linear equations; p. 5 Eqs. (2.8)–(2.12); p. 7 Eqs. (2.15)–(2.18); p. 12 Eqs. (2.24)–(2.25). Opposite propagation and standing pair. |
| SRC-E03 | Same MIT course, Lecture 3, *Spherical Waves: Near & Far Field, Radiation Impedance, and Simple Sources*, dated 16 September 2004; [original PDF](https://ocw.mit.edu/courses/6-551j-acoustics-of-speech-and-hearing-fall-2004/7056ab51d5cb75810bf976ee38ac8f30_lec_3_2004.pdf) | p. 1 Eqs. (3.3)–(3.5), averaging; pp. 2–3 Eqs. (3.8)–(3.15), exact outgoing spherical solution and velocity. B-06 uses these, not the later approximate physical-source-strength formulas. |

The course lists Christopher Shera, John Rosowski, Kenneth Stevens and Louis Braida as instructors. The inspected PDFs do not establish individual authorship; no single author is invented. These are primary teaching derivations, not experimental reports. Their air examples do not supply water material data: AURA uses separately labeled manufactured rho/c and the stated ideal-fluid equations.

## Reconciliation and independent project derivations

MIT uses `Re(P exp(+i omega t))`; AURA uses `Re(p_hat exp(-i omega t))`. Conjugate the entire complex representation, including source phases, when translating. Thus an outgoing plane wave uses `exp(+ikx)` and the spherical velocity multiplier is `1+i/(kr)`. Pressure-amplitude reference points are specified in FIELD-1.0; no physical volume-velocity source calibration is inferred.

For each selected field, the project derives the pressure gradient by differentiating its spatial expression and then uses `grad(p)=i omega rho v`. This checks the velocity sign by a route separate from copying a phasor formula. The componentwise time integral of two real harmonic signals supplies mean flux. Source addition and B-03…B-05 tables follow elementary sine/cosine identities; B-06 distance ratios follow differentiation of its explicitly normalized radial ansatz. See [the contract](analytical-field-contract.md) and [frozen protocol](../benchmarks/B03-B06-analytical-protocols.md).

The selected spherical solution keeps the reactive velocity term at every admitted radius. Its exact real radial flux follows by direct multiplication, even though the lecture's subsequent far-field discussion also uses approximations. The project does not adopt that discussion as a general claim about radiator near fields. Point-source exclusions, finite hardware applicability, absorption and body scattering are separate unresolved questions.

## Limitations and evidence retained

The web PDF renderer timed out on the Lecture 2 screenshot attempt; the complete original PDF text was available, including the selected equations and dated page footers. No experimental figure or digitized measurement was used. Equation-source review establishes the stated ideal references only. Material uncertainty, actual source calibration, boundaries, acoustic forces, microgravity and larger-body applicability remain in their owning tasks. Independent numerical oracles and actual solver comparisons are still required after ANA-01.
