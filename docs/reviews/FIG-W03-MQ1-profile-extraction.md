# FIG-W03-MQ1 — Review of Figure-Derived Velocity Profiles

**Status:** EXPLORATORY DIGITIZATION CHECKED · **Formal measurement benchmark:** INDETERMINATE · **Date:** 2026-10-03

## Question and scope

Can the author-thesis copy of the SRC-W03 supplemental material yield reproducible plotted MQ1 profile values even though it contains no original numerical micro-PIV arrays?

The bounded extraction digitizes only the six one-dimensional plots of the axial average of transverse particle velocity, `⟨u_y⟩_x`, on the right of Supplemental Material Figure 3. It does not digitize the two-dimensional color maps, reconstruct the original micro-PIV arrays, fit a physical model, or assess an AURA prediction. The source article identifies the red points as measurements away from side walls used for its sinusoidal fit; its plotted error bars are standard deviations of the axial average, not measurement uncertainty ([author manuscript, Fig. 7 discussion](https://arxiv.org/html/1208.6534#S4.SS1)).

## Source and derived artifact

The input is THS-W03, Rune Barnkob’s 2012 DTU thesis, which embeds the SRC-W03 supplement. The exact 17,033,914-byte PDF has SHA-256 `8adfc59f1a64b5ea2748b81ecf3171e04488a92520f9a10485d4d99ecfc52a3e`; its extracted PDF page 204 is printed page 4 of the supplement. The source and all local outputs are retained under the ignored path `results/research/SRC-W03-MQ1-FIG3-EXTRACTION-20261003/`.

The immutable derived identifier is `FIG-W03-MQ1-20261003-01`. Its CSV contains 234 plotted mean-marker centers: 39 spatial positions for each figure diameter label (0.59, 0.99, 1.93, 2.55, 4.94 and 10.6 µm). A flag identifies the 25 red-highlighted profile positions in each panel; these red markers overlie positions in the 39-point profile and are not a second dataset. The extracted ordinate is the plotted velocity normalized to `U_pp = 1 V`. The source’s MQ1 acquisition log and particle-size values are matched to the figure panels in the JSON report.

| Artifact | SHA-256 |
|---|---|
| Source thesis PDF | `8adfc59f1a64b5ea2748b81ecf3171e04488a92520f9a10485d4d99ecfc52a3e` |
| `mq1-mean-velocity-profile.csv` | `37d7c05e26a1cab40e52cf1bdcd9fd8d3502b54205ab52c15216d99ef6ea91da` |
| `extraction-report.json` | `3d6677cdee46284f9f0cc882715194582508f72f96dd6db0e0b7a8614ada0d82` |
| `extract.py` | `b194707f866f7f3460fce49897a7b607e51a5887bd02740736de94c09341123d` |
| Retained failed affine-transform CSV | `eb2db004d60d66068ec6f2e9f297821a9d44d221d2ff3a9de164fac6383e90db` |

The complete per-file digest list, source provenance, package versions, calibrated axes, acquisition rows and validation results are in the local `sha256sums.json` and `extraction-report.json`. Python 3.13.5 was used with PyMuPDF 1.26.7, pdfplumber 0.11.10, pdfminer.six 20260107, pypdfium2 5.13.0 and Pillow 12.3.0. These temporary extraction tools were installed outside AURA’s project environment and are not solver dependencies.

## Extraction and checks

The primary extraction locates the filled point-marker paths on PDF page 204 with PyMuPDF, takes each path’s bounding-box center, and calibrates the plot axes from the vector tick locations. Tick-label values were read from the displayed figure. A second vector parser, pdfplumber/pdfminer.six, found the same 64 plotted marker objects in each panel (39 profile markers plus 25 red overplots); corresponding centers differed by at most `0.000130` PDF point across 384 parser comparisons.

As an independent raster check, PDFium rendered the page at 432 dpi. Color-thresholded connected components recovered the 150 red-circle centers, 25 per panel. Their centroid differences from the vector centers were RMS `0.0594` PDF point and maximum `0.1025` PDF point. An axis-calibration sensitivity check compared linear fits to all labelled ticks with endpoint-only fits: the maximum spatial-coordinate change was `0.095 µm`; the largest velocity-coordinate change was `0.429 µm/s` (10.6 µm panel). This is extraction sensitivity only, not measurement uncertainty. The displayed marker half-widths are separately reported in the CSV as a visualization-resolution indicator, not as uncertainty intervals.

The extraction asserts the source checksum and 214-page count, checks marker counts and panel assignments, requires all 234 accepted coordinates to lie within the displayed 0–446 µm spatial axis, verifies the exact 25-point red subset per panel, matches both vector parsers within the declared bound, and cross-checks the raster red markers one-to-one. The retained development log records the initial marker-count, parser-tolerance and inverted-coordinate failures; the failed CSV remains separate from accepted data.

## Limits and interpretation

This result provides plotted one-dimensional particle-velocity means for the six MQ1 size cases. It is a figure-derived exploratory artifact, not an experimental raw-data release or a measured force/acceleration dataset. No AURA model was tested. The original 79 × 39 vector arrays, pointwise measurement uncertainty/covariance and calibration uncertainty budget remain unavailable. The error bars were not transcribed and cannot be reinterpreted as uncertainty of the measured means. The two-dimensional color maps have no machine-readable values or numerical color scale in this facsimile and were not reconstructed.

The two vector parsers and raster check are independent extraction implementations, not independent human/scientific reviewers. They verify recovery of plotted marker locations; they do not validate the source experiment or physical model. Formal water benchmark status therefore remains **INDETERMINATE**, and no acceptance tolerance or validation claim follows from this digitization.
