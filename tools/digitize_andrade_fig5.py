#!/usr/bin/env python3
"""Extract the red experimental trace in Andrade et al. (2016), Fig. 5.

This creates figure-derived points, not the experiment's original raw data.
The scale calibration is tied to a page-9 render at 180 dpi and scales linearly
with the render DPI. See docs/benchmarks/P1.3-andrade-force-curve-specification.md.
"""

import argparse
import csv
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path, help="PNG render of PDF page 9")
    parser.add_argument("output", type=Path, help="CSV output path")
    parser.add_argument("--dpi", type=float, choices=(180.0, 360.0), required=True)
    parser.add_argument(
        "--method",
        choices=("window-median", "center-column"),
        default="window-median",
    )
    args = parser.parse_args()

    scale = args.dpi / 180.0
    x_left, x_right = 477.0 * scale, 1120.0 * scale
    y_top, y_bottom = 193.0 * scale, 749.0 * scale
    image = Image.open(args.image).convert("RGB")
    expected = (round(1530 * scale), round(1980 * scale))
    if image.size != expected:
        raise SystemExit(f"Unexpected image size {image.size}; expected {expected}")

    pixels = image.load()
    # Exclude the red legend at the top right; the plotted measurement stays
    # below 1.3 gf, while the legend is above 1.5 gf.
    y_min = round((749.0 - 1.35 * 556.0 / 1.8) * scale)
    window = max(1, round(1.0 * scale))
    rows = []
    for step in range(1, 301):
        gap_mm = step / 10.0
        x = x_left + (gap_mm / 30.0) * (x_right - x_left)
        center = round(x)
        ys = []
        half_width = window if args.method == "window-median" else 0
        for px in range(center - half_width, center + half_width + 1):
            if px < 0 or px >= image.width:
                continue
            for py in range(y_min, round(y_bottom)):
                red, green, blue = pixels[px, py]
                if red >= 150 and red >= 1.45 * green and red >= 1.25 * blue:
                    ys.append(py)
        if not ys:
            # At H=0.1 mm the red trace touches the dark y-axis. A wider
            # fallback catches the visible trace just inside the plot.
            fallback = max(3, round(3.0 * scale))
            for px in range(center - fallback, center + fallback + 1):
                if px < 0 or px >= image.width:
                    continue
                for py in range(y_min, round(y_bottom)):
                    red, green, blue = pixels[px, py]
                    if red >= 150 and red >= 1.45 * green and red >= 1.25 * blue:
                        ys.append(py)
        if not ys:
            rows.append((gap_mm, ""))
            continue
        y = sorted(ys)[len(ys) // 2]
        force_gf = (y_bottom - y) / (y_bottom - y_top) * 1.8
        rows.append((gap_mm, f"{force_gf:.5f}"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("gap_mm", "experimental_force_gf"))
        writer.writerows(rows)


if __name__ == "__main__":
    main()
