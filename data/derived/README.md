# Derived Benchmark Data

## Andrade et al. (2016), Figure 5 experimental curve

The two CSV files are figure-derived readings of the red experimental trace in Figure 5. They are **not the original measurement records** and do not replace source uncertainty data.

| File | Source-figure render |
|---|---|
| `andrade2016-fig5-experimental-180dpi.csv` | Page 9 of the accepted manuscript, rendered at 180 dpi |
| `andrade2016-fig5-experimental-360dpi.csv` | Same page, rendered at 360 dpi |

Both files contain 300 force readings at gaps from 0.1 through 30.0 mm in 0.1 mm steps. Force remains in the figure's unit, gram-force (gf). Values are read from the red trace using the axis calibration and red-pixel rule in [`tools/digitize_andrade_fig5.py`](../../tools/digitize_andrade_fig5.py). The first major measured peak is about 1.19 gf near 7.1 mm in both extractions.

The 180 dpi and 360 dpi passes use the same extraction method and author. Their difference is a **render-resolution sensitivity check**, not two independent experimental measurements or an independent manual digitization. Across the 300 common points, the median absolute difference is 0.00324 gf and the maximum is 0.06960 gf near the steep first peak. This spread describes sensitivity to rendering and pixel selection only; it is not the experiment's measurement uncertainty and is not an acceptance tolerance.

### Provenance and reproduction

- Article: M. A. B. Andrade, A. L. Bernassau, and J. C. Adamowski, “Acoustic levitation of a large solid sphere,” *Applied Physics Letters* 109, 044101 (2016), [DOI 10.1063/1.4959862](https://doi.org/10.1063/1.4959862).
- Source manuscript: [Heriot-Watt University repository record](https://researchportal.hw.ac.uk/en/publications/acoustic-levitation-of-a-large-solid-sphere/); page 9, Figure 5.
- Downloaded PDF SHA-256: `306d320c485170da70da7470527ca86f8068c0d138e5f825a2d80c19e8cbc749`.
- 180 dpi page-image SHA-256: `552954467c516c1c6b62498fbde4126f4f1cdd2a0654abba5ec1f40645c2fc03`.
- 360 dpi page-image SHA-256: `22a5251a5916017a8a54ca29be8335714f91eba0c1555c1b98ae8df1a7f35819`.
- The manuscript PDF and rendered images are not copied into this repository. Re-download the institutional manuscript, confirm its checksum, and render PDF page 9 at 180 dpi and 360 dpi with Poppler `pdftoppm` before regenerating the CSV files. The extraction was run with Poppler 26.01.0 and Pillow 12.1.1.

Example workflow, after downloading the PDF to `source.pdf`:

```sh
pdftoppm -f 9 -l 9 -png -r 180 source.pdf page180
pdftoppm -f 9 -l 9 -png -r 360 source.pdf page360
python tools/digitize_andrade_fig5.py page180-09.png data/derived/andrade2016-fig5-experimental-180dpi.csv --dpi 180
python tools/digitize_andrade_fig5.py page360-09.png data/derived/andrade2016-fig5-experimental-360dpi.csv --dpi 360
```

The plotted curve has no uncertainty bars. The article attributes the difference between measured and simulated peak values partly to experimental uncertainty and modeling simplifications, but does not quantify the experimental uncertainty. Until an independent digitization and source measurement uncertainty are available, comparisons using these CSV files remain descriptive and formal validation is **INDETERMINATE**.
