"""Export the frozen B-04 field samples for a separate diagnostic renderer."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from aura.fields import PlaneWave, evaluate_counterpropagating_pair, mean_intensity_w_m2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new JSON path; existing files are refused")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests/fixtures/fields/B04-counterpropagating.json"
    content = fixture.read_bytes()
    cases = json.loads(content)["cases"]
    result = {
        "format": "B04-PLOT-1.0",
        "scope": "numerical software verification",
        "source_revision": subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip(),
        "source_dirty": bool(
            subprocess.check_output(
                ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]
            )
        ),
        "fixture_sha256": hashlib.sha256(content).hexdigest(),
        "cases": [],
    }
    for case in cases:
        field = evaluate_counterpropagating_pair(
            PlaneWave(**case["forward"]),
            PlaneWave(**case["backward"]),
            case["coordinates_m"],
            box_min_m=case["box_min_m"],
            box_max_m=case["box_max_m"],
            workspace_bytes=case["workspace_bytes"],
        )
        result["cases"].append(
            {
                "id": case["id"],
                "field_artifacts": field.to_artifacts(),
                "x_over_wavelength": [p[0] / 0.0015 for p in field.coordinates_m],
                "pressure_magnitude_pa": [abs(p) for p in field.pressure_pa],
                "velocity_x_magnitude_m_s": [abs(v[0]) for v in field.velocity_m_s],
                "intensity_x_w_m2": [v[0] for v in mean_intensity_w_m2(field)],
                "incorrect_pressure_only_flux_w_m2": [
                    abs(p) ** 2 / (2 * 1_500_000) for p in field.pressure_pa
                ],
            }
        )
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
