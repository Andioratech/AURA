"""Reproduce the exploratory digitization of SRC-W03/MQ1 Figure 3.

Run from the repository root after placing the checksum-identified source PDF
in the ignored `-02` evidence directory and installing the pinned, external
research-tool versions documented in the artifact review. The script records
its clean Git revision and refuses to replace any differing artifact.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import fitz
import pdfplumber
import pypdfium2 as pdfium

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = "SRC-W03-MQ1-FIG3-EXTRACTION-20261003-02"
ROOT = REPOSITORY_ROOT / "results" / "research" / DATASET_DIRECTORY
SOURCE = ROOT / "source-thesis.pdf"
TOOL = Path(__file__).resolve()
TOOL_COPY = ROOT / "extract.py"
TOOL_REPOSITORY_PATH = TOOL.relative_to(REPOSITORY_ROOT).as_posix()
EXPECTED_SOURCE_SHA256 = "8adfc59f1a64b5ea2748b81ecf3171e04488a92520f9a10485d4d99ecfc52a3e"
EXPECTED_ENVIRONMENT = {
    "python": "3.13.5",
    "PyMuPDF": "1.26.7",
    "pdfplumber": "0.11.10",
    "pdfminer.six": "20260107",
    "pypdfium2": "5.13.0",
    "Pillow": "12.3.0",
}
PAGE_INDEX = 203  # PDF page 204, thesis supplemental-material Figure 3 (MQ1)
SCALE = 6.0  # PDFium pixels per PDF point; 432 dpi
CROP_PT = (395.0, 53.0, 560.0, 455.0)  # left, top, right, bottom
FRAMES = (
    (57.575, 118.742),
    (123.270, 184.440),
    (188.970, 250.130),
    (254.660, 315.830),
    (320.360, 381.520),
    (390.160, 451.320),
)
DIAMETER_LABELS_UM = (0.59, 0.99, 1.93, 2.55, 4.94, 10.6)
MQ1_ACQUISITION = (
    {"figure_label_um": 0.59, "logged_diameter_um": 0.6, "logged_timestamp": "2012-02-25 15:49:37", "camera_fps": 404, "repeats": 150, "U_pp_V": 7.940, "size_source": "manufacturer; 0.591 +/- 0.030 um"},
    {"figure_label_um": 0.99, "logged_diameter_um": 1.0, "logged_timestamp": "2012-02-24 18:15:02", "camera_fps": 404, "repeats": 100, "U_pp_V": 7.940, "size_source": "manufacturer; 0.992 +/- 0.050 um"},
    {"figure_label_um": 1.93, "logged_diameter_um": 2.0, "logged_timestamp": "2012-02-25 11:10:08", "camera_fps": 404, "repeats": 100, "U_pp_V": 6.334, "size_source": "Coulter counter; 1.91 +/- 0.07 um"},
    {"figure_label_um": 2.55, "logged_diameter_um": 3.0, "logged_timestamp": "2012-02-25 12:22:39", "camera_fps": 404, "repeats": 100, "U_pp_V": 4.767, "size_source": "Coulter counter; 2.57 +/- 0.07 um"},
    {"figure_label_um": 4.94, "logged_diameter_um": 5.0, "logged_timestamp": "2012-02-24 16:08:43", "camera_fps": 808, "repeats": 101, "U_pp_V": 3.936, "size_source": "Coulter counter; 5.11 +/- 0.16 um"},
    {"figure_label_um": 10.6, "logged_diameter_um": 10.0, "logged_timestamp": "2012-02-25 13:39:10", "camera_fps": 404, "repeats": 100, "U_pp_V": 1.951, "size_source": "Coulter counter; 10.16 +/- 0.20 um"},
)
Y_TICK_VALUES = (
    (10.0, 0.0, -10.0),
    (20.0, 0.0, -20.0),
    (40.0, 20.0, 0.0, -20.0, -40.0),
    (50.0, 0.0, -50.0),
    (200.0, 0.0, -200.0),
    (500.0, 0.0, -500.0),
)
DARK = (0.13669, 0.12195, 0.12529)
RED = (0.904, 0.181, 0.178)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def immutable_write(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise SystemExit(
                f"refusing to replace differing immutable artifact: {path}; "
                "use a new dataset ID/output directory"
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def repository_revision() -> str:
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--", TOOL_REPOSITORY_PATH],
        cwd=REPOSITORY_ROOT,
        text=True,
    )
    if dirty:
        raise SystemExit("extractor must be committed and clean before reproduction")
    return revision


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom
    intercept = ybar - slope * xbar
    residual = max(abs(y - (intercept + slope * x)) for x, y in zip(xs, ys))
    return intercept, slope, residual


def same_color(value, expected: tuple[float, float, float]) -> bool:
    return (
        isinstance(value, (tuple, list))
        and len(value) == 3
        and max(abs(a - b) for a, b in zip(value, expected)) < 0.003
    )


def panel_for(y: float) -> int | None:
    for index, (top, bottom) in enumerate(FRAMES):
        if top < y < bottom:
            return index
    return None


def validate_and_extract() -> None:
    actual_environment = {
        "python": sys.version.split()[0],
        "PyMuPDF": version("PyMuPDF"),
        "pdfplumber": version("pdfplumber"),
        "pdfminer.six": version("pdfminer.six"),
        "pypdfium2": version("pypdfium2"),
        "Pillow": version("Pillow"),
    }
    if actual_environment != EXPECTED_ENVIRONMENT:
        raise SystemExit(
            f"unsupported extraction environment: {actual_environment}; "
            f"expected {EXPECTED_ENVIRONMENT}"
        )
    revision = repository_revision()
    tool_bytes = TOOL.read_bytes()
    immutable_write(TOOL_COPY, tool_bytes)
    if not SOURCE.is_file():
        raise SystemExit(
            f"place the source thesis PDF at {SOURCE}; see the source URL in the artifact review"
        )
    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"unexpected source digest: {source_hash}")

    document = fitz.open(SOURCE)
    if len(document) != 214:
        raise SystemExit(f"unexpected PDF page count: {len(document)}")
    page = document[PAGE_INDEX]
    drawings = page.get_drawings()

    # Calibrate the shared x-axis from the five vector tick marks, whose printed
    # labels are 0, 100, 200, 300 and 400 micrometres.
    x_tick_positions = sorted(
        d["rect"].x0
        for d in drawings
        if d["color"]
        and same_color(d["color"], DARK)
        and abs(d["rect"].x1 - d["rect"].x0) < 0.01
        and 1.5 < d["rect"].height < 1.8
        and abs(d["rect"].y0 - 449.697) < 0.02
    )
    if len(x_tick_positions) != 5:
        raise SystemExit(f"unexpected x-axis ticks: {x_tick_positions}")
    x_axis_intercept, x_axis_slope, x_tick_residual = linear_fit(
        x_tick_positions, [0.0, 100.0, 200.0, 300.0, 400.0]
    )
    x_endpoint_intercept, x_endpoint_slope, _ = linear_fit(
        [x_tick_positions[0], x_tick_positions[-1]], [0.0, 400.0]
    )

    y_axis_fits = []
    for panel_index, ((top, bottom), tick_values) in enumerate(
        zip(FRAMES, Y_TICK_VALUES), start=1
    ):
        y_tick_positions = sorted(
            d["rect"].y0
            for d in drawings
            if d["color"]
            and same_color(d["color"], DARK)
            and abs(d["rect"].height) < 0.01
            and 1.5 < d["rect"].width < 1.8
            and 398.4 < d["rect"].x0 < 398.8
            and top < d["rect"].y0 < bottom
        )
        if len(y_tick_positions) != len(tick_values):
            raise SystemExit(
                f"panel {panel_index}: unexpected y ticks {y_tick_positions}"
            )
        intercept, slope, residual = linear_fit(y_tick_positions, list(tick_values))
        endpoint_intercept, endpoint_slope, _ = linear_fit(
            [y_tick_positions[0], y_tick_positions[-1]],
            [tick_values[0], tick_values[-1]],
        )
        y_axis_fits.append(
            {
                "intercept_um_s": intercept,
                "slope_um_s_per_pt": slope,
                "tick_residual_um_s": residual,
                "endpoint_intercept_um_s": endpoint_intercept,
                "endpoint_slope_um_s_per_pt": endpoint_slope,
                "endpoint_calibration_max_difference_um_s": None,
            }
        )

    vector_markers: dict[int, dict[str, list[tuple[float, float, float, float]]]] = {
        i: {"all": [], "fit_subset": []} for i in range(6)
    }
    for drawing in drawings:
        rect = drawing["rect"]
        center_x = (rect.x0 + rect.x1) / 2
        center_y = (rect.y0 + rect.y1) / 2
        panel_index = panel_for(center_y)
        if panel_index is None or not (402.0 < center_x < 549.0):
            continue
        if not (2.0 < rect.width < 2.2 and 2.0 < rect.height < 2.2):
            continue
        if drawing["type"] != "f":
            continue
        if same_color(drawing["fill"], DARK):
            vector_markers[panel_index]["all"].append(
                (center_x, center_y, rect.width, rect.height)
            )
        elif same_color(drawing["fill"], RED):
            vector_markers[panel_index]["fit_subset"].append(
                (center_x, center_y, rect.width, rect.height)
            )

    # Independently parse the same PDF vectors through pdfplumber/pdfminer.six.
    pdfminer_markers: dict[int, list[tuple[float, float]]] = {i: [] for i in range(6)}
    with pdfplumber.open(SOURCE) as pdf:
        if len(pdf.pages) != 214:
            raise SystemExit("pdfplumber page-count disagreement")
        for curve in pdf.pages[PAGE_INDEX].curves:
            cx = (curve["x0"] + curve["x1"]) / 2
            cy = (curve["top"] + curve["bottom"]) / 2
            panel_index = panel_for(cy)
            if panel_index is None or not (402.0 < cx < 549.0):
                continue
            if not (
                2.0 < curve["x1"] - curve["x0"] < 2.2
                and 2.0 < curve["bottom"] - curve["top"] < 2.2
            ):
                continue
            pdfminer_markers[panel_index].append((cx, cy))

    panel_results = []
    csv_rows = []
    raster_expected = []
    for panel_index, ((top, bottom), diameter) in enumerate(
        zip(FRAMES, DIAMETER_LABELS_UM)
    ):
        all_markers = sorted(vector_markers[panel_index]["all"])
        fit_markers = sorted(vector_markers[panel_index]["fit_subset"])
        second_parse = pdfminer_markers[panel_index]
        if len(all_markers) != 39 or len(fit_markers) != 25:
            raise SystemExit(
                f"panel {panel_index+1}: marker counts {len(all_markers)}/{len(fit_markers)}"
            )
        if len(second_parse) != 64:
            raise SystemExit(f"panel {panel_index+1}: pdfminer count {len(second_parse)}")

        combined = [(x, y) for x, y, _, _ in all_markers + fit_markers]
        y_axis_fits[panel_index]["endpoint_calibration_max_difference_um_s"] = max(
            abs(
                (y_axis_fits[panel_index]["intercept_um_s"] + y_axis_fits[panel_index]["slope_um_s_per_pt"] * y)
                - (
                    y_axis_fits[panel_index]["endpoint_intercept_um_s"]
                    + y_axis_fits[panel_index]["endpoint_slope_um_s_per_pt"] * y
                )
            )
            for _, y in combined
        )
        parser_distances = [
            math.hypot(left[0] - right[0], left[1] - right[1])
            for left, right in zip(sorted(combined), sorted(second_parse))
        ]
        if max(parser_distances) > 1e-3:
            raise SystemExit(
                f"panel {panel_index+1}: independent vector parsers differ by "
                f"{max(parser_distances)} PDF points"
            )

        fit_centers = [(x, y) for x, y, _, _ in fit_markers]
        fit_center_set = {(x, y) for x, y in fit_centers}
        fit_membership = []
        for point_index, (x, y, width, height) in enumerate(all_markers, start=1):
            highlighted = (x, y) in fit_center_set
            fit_membership.append(highlighted)
            uy = y_axis_fits[panel_index]["intercept_um_s"] + y_axis_fits[panel_index]["slope_um_s_per_pt"] * y
            y_um = x_axis_intercept + x_axis_slope * x
            csv_rows.append(
                {
                    "figure_id": "FIG-W03-MQ1-20261003-01",
                    "series": "MQ1",
                    "pdf_page": 204,
                    "figure_panel": panel_index + 1,
                    "particle_diameter_figure_label_um": diameter,
                    "point_index_in_increasing_y": point_index,
                    "spatial_y_um": y_um,
                    "mean_particle_velocity_y_at_1V_um_s": uy,
                    "red_fit_subset_marker": str(highlighted).lower(),
                    "vector_marker_width_pt": width,
                    "vector_marker_height_pt": height,
                    "pdf_marker_center_x_pt": x,
                    "pdf_marker_center_y_from_top_pt": y,
                    "display_half_marker_y_um_s": height / 2 * abs(y_axis_fits[panel_index]["slope_um_s_per_pt"]),
                    "display_half_marker_y_um": width / 2 * abs(x_axis_slope),
                }
            )
            if highlighted:
                raster_expected.append((panel_index, x, y))

        panel_results.append(
            {
                "panel": panel_index + 1,
                "diameter_figure_label_um": diameter,
                "vector_all_mean_markers": len(all_markers),
                "red_fit_subset_markers": len(fit_markers),
                "red_markers_are_exact_subset_of_all_centers": sum(fit_membership) == 25,
                "pdfminer_curve_markers": len(second_parse),
                "max_vector_parser_coordinate_difference_pt": max(parser_distances),
            }
        )

    if len(csv_rows) != 234:
        raise SystemExit(f"unexpected accepted profile row count: {len(csv_rows)}")
    outside_axis = [
        row["spatial_y_um"]
        for row in csv_rows
        if not math.isfinite(row["spatial_y_um"])
        or not 0.0 <= row["spatial_y_um"] <= 446.0
    ]
    if outside_axis:
        raise SystemExit(f"profile coordinate outside plotted 0-446 um axis: {outside_axis}")

    # Independent raster re-reading of all red fit-subset point centers using PDFium.
    bitmap = pdfium.PdfDocument(SOURCE)[PAGE_INDEX].render(scale=SCALE, rotation=0)
    image = bitmap.to_pil().convert("RGB")
    left, top, right, bottom = CROP_PT
    crop_box = (int(left * SCALE), int(top * SCALE), int(right * SCALE), int(bottom * SCALE))
    crop = image.crop(crop_box)
    width, height = crop.size
    raw = crop.tobytes()
    red_pixels = set()
    for offset in range(0, len(raw), 3):
        red, green, blue = raw[offset : offset + 3]
        if red > 150 and green < 120 and blue < 120 and red > green * 1.8 and red > blue * 1.8:
            pixel_index = offset // 3
            red_pixels.add((pixel_index % width, pixel_index // width))

    components = []
    unseen = set(red_pixels)
    while unseen:
        start = unseen.pop()
        stack = [start]
        component = [start]
        while stack:
            px, py = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    neighbor = (px + dx, py + dy)
                    if (dx or dy) and neighbor in unseen:
                        unseen.remove(neighbor)
                        stack.append(neighbor)
                        component.append(neighbor)
        if len(component) > 10:
            components.append(component)

    raster_centers = []
    for component in components:
        xs = [point[0] for point in component]
        ys = [point[1] for point in component]
        raster_centers.append(
            (
                left + (sum(xs) / len(xs) + 0.5) / SCALE,
                top + (sum(ys) / len(ys) + 0.5) / SCALE,
                len(component),
            )
        )
    if len(raster_centers) != 150 or len(raster_expected) != 150:
        raise SystemExit(
            f"raster/vector subset count disagreement: {len(raster_centers)}/{len(raster_expected)}"
        )

    # Panel-wise one-to-one nearest matches; no expected center is reused.
    raster_differences = []
    for panel_index in range(6):
        expected = [(x, y) for i, x, y in raster_expected if i == panel_index]
        observed = [
            (x, y)
            for x, y, _ in raster_centers
            if FRAMES[panel_index][0] < y < FRAMES[panel_index][1]
        ]
        if len(observed) != 25 or len(expected) != 25:
            raise SystemExit(f"panel {panel_index+1}: raster count mismatch")
        remaining = list(observed)
        for point in expected:
            distance, nearest = min(
                (math.hypot(point[0] - q[0], point[1] - q[1]), q) for q in remaining
            )
            raster_differences.append(distance)
            remaining.remove(nearest)
    if max(raster_differences) > 0.20:
        raise SystemExit(f"raster cross-check exceeds 0.20 pt: {max(raster_differences)}")

    csv_path = ROOT / "mq1-mean-velocity-profile.csv"
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=list(csv_rows[0]))
    writer.writeheader()
    writer.writerows(csv_rows)
    immutable_write(csv_path, csv_buffer.getvalue().encode("utf-8"))

    report = {
        "dataset_id": "FIG-W03-MQ1-20261003-02",
        "source": {
            "url": "https://www.fysik.dtu.dk/english/-/media/institutter/fysik/research/ph-d/ph-d-projekter/pdf-theses/2012/barnkop-rune-2012.pdf",
            "file": "source-thesis.pdf",
            "sha256": source_hash,
            "bytes": SOURCE.stat().st_size,
            "pdf_pages": 214,
            "extracted_pdf_page": 204,
            "printed_supplement_page": 4,
            "figure": "Supplemental Material Figure 3, MQ1; right-hand panels (b)",
        },
        "scientific_quantity": "plotted axial average of transverse particle velocity, <u_y>_x, normalized to Upp = 1 V",
        "matched_MQ1_acquisition_table": MQ1_ACQUISITION,
        "software": {
            **actual_environment,
            "raster_scale_px_per_pdf_pt": SCALE,
        },
        "execution_provenance": {
            "repository_revision": revision,
            "extractor_path": TOOL_REPOSITORY_PATH,
            "extractor_sha256": sha256(TOOL),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "axis_calibration": {
            "tick_label_method": "Values transcribed from the visible plot labels; tick positions extracted from vector paths.",
            "x_axis": {
                "quantity": "spatial y [um]",
                "intercept_um": x_axis_intercept,
                "slope_um_per_pdf_pt": x_axis_slope,
                "tick_values_um": [0, 100, 200, 300, 400],
                "max_tick_fit_residual_um": x_tick_residual,
                "endpoint_calibration_max_difference_um": max(
                    abs(
                        (x_axis_intercept + x_axis_slope * x)
                        - (x_endpoint_intercept + x_endpoint_slope * x)
                    )
                    for panel in vector_markers.values()
                    for x, y, _, _ in panel["all"] + panel["fit_subset"]
                ),
            },
            "y_axes_by_panel": y_axis_fits,
        },
        "validation": {
            "vector_parser_a": "PyMuPDF path bounding boxes, marker centers at bounding-box centers",
            "vector_parser_b": "pdfplumber/pdfminer.six curve bounding boxes, marker centers at bounding-box centers",
            "vector_parser_a_vs_b_centers_within_1e-3_pt": sum(p["vector_all_mean_markers"] + p["red_fit_subset_markers"] for p in panel_results),
            "max_vector_coordinate_difference_pt": max(p["max_vector_parser_coordinate_difference_pt"] for p in panel_results),
            "independent_raster_check": "PDFium 432-dpi render, color-thresholded connected-component centroids for red fit-subset circles",
            "raster_fit_subset_points": len(raster_centers),
            "raster_centroid_max_error_pt": max(raster_differences),
            "raster_centroid_rms_error_pt": math.sqrt(sum(d*d for d in raster_differences) / len(raster_differences)),
            "points_per_panel": panel_results,
        },
        "limitations": [
            "This is figure-derived exploratory data, not the original micro-PIV grid or raw measurement arrays.",
            "The two vector paths reproduce PDF plotting geometry; the raster re-read independently checks only the 25 red-highlighted fit-subset markers per panel.",
            "The 39 centers per panel are the plotted profile means; plotted error bars are identified by the article as standard deviations, not measurement uncertainty, and are not transcribed here.",
            "The 2D color maps on the same plate have no machine-readable arrays or numerical color scale in this facsimile and are not reconstructed.",
            "Marker half-width values in the CSV describe display-symbol size only; they are not experimental uncertainty intervals.",
            "No model was fitted and no validation verdict or acceptance tolerance was calculated.",
        ],
    }
    report_path = ROOT / "extraction-report.json"
    immutable_write(
        report_path,
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    retained_failures = ROOT / "failed-attempts" / "attempt-03-inverted-x-calibration.csv"
    files = [SOURCE, csv_path, report_path, TOOL_COPY, ROOT / "development-attempts.md"]
    if retained_failures.exists():
        files.append(retained_failures)
    files.extend(sorted((ROOT / "failed-attempts").glob("attempt-04-dark-raster-localization.*")))
    files.extend(sorted((ROOT / "failed-attempts").glob("attempt-05-opened-raster-component-centroids.*")))
    file_manifest = {"files": {str(path.relative_to(ROOT)): sha256(path) for path in files}}
    immutable_write(
        ROOT / "sha256sums.json",
        (json.dumps(file_manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    print(json.dumps(report["validation"], indent=2))
    print("CSV SHA-256", sha256(csv_path))
    print("REPORT SHA-256", sha256(report_path))
    print("SCRIPT SHA-256", sha256(TOOL))


if __name__ == "__main__":
    validate_and_extract()
