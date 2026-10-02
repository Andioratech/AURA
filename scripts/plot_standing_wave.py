"""Render exported B-04 samples with optional, separately installed Matplotlib."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, help="new PNG path; existing files are refused")
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    if data["format"] != "B04-PLOT-1.0":
        raise ValueError("Expected B04-PLOT-1.0")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cases = {case["id"]: case for case in data["cases"]}
    equal = cases["B04-EQUAL"]
    x = equal["x_over_wavelength"]
    fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    fig.subplots_adjust(top=0.88, bottom=0.20, hspace=0.36, left=0.12, right=0.96)
    fig.suptitle("B-04 | Two opposing acoustic waves", fontsize=18, x=0.12, ha="left", y=0.97)
    fig.text(
        0.12,
        0.925,
        "Numerical verification · ideal lossless fluid · 1 MHz · equal pair: 2 Pa per wave",
        fontsize=11,
    )
    axes[0].plot(x, equal["pressure_magnitude_pa"], color="#155e75", linewidth=2)
    axes[0].set(
        ylabel="Pressure magnitude (Pa)",
        title="Equal pair: pressure nodes at 1/4 and 3/4 wavelength",
    )
    axes[1].plot(
        x, [v * 1e6 for v in equal["velocity_x_magnitude_m_s"]], color="#6d28d9", linewidth=2
    )
    axes[1].set(
        ylabel="Fluid velocity magnitude (µm/s)",
        title="Equal pair: fluid velocity remains nonzero at pressure nodes",
    )
    for key, label, style, color in (
        ("B04-EQUAL", "Equal pair: zero net flux", "-", "#155e75"),
        ("B04-PHASE", "Shifted phase: zero net flux", ":", "#6d28d9"),
        ("B04-UNEQUAL", "4 Pa forward, 2 Pa backward", "--", "#15803d"),
        ("B04-REVERSED", "2 Pa forward, 4 Pa backward", "-.", "#b45309"),
    ):
        case = cases[key]
        axes[2].plot(
            case["x_over_wavelength"],
            [v * 1e6 for v in case["intensity_x_w_m2"]],
            style,
            color=color,
            label=label,
            linewidth=2,
        )
    axes[2].plot(
        x,
        [v * 1e6 for v in equal["incorrect_pressure_only_flux_w_m2"]],
        color="#dc2626",
        linestyle="--",
        label="Incorrect pressure-only shortcut (equal pair)",
    )
    axes[2].set(
        xlabel="Position x / wavelength",
        ylabel="Mean axial flux (µW/m²)",
        title="Use pressure AND velocity to calculate net energy transport",
    )
    axes[2].legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2)
    for axis in axes:
        axis.set_xlim(0, 1)
        axis.set_xticks([0, 0.25, 0.5, 0.75, 1])
        axis.grid(alpha=0.2)
        axis.spines[["top", "right"]].set_visible(False)
    fig.text(
        0.12,
        0.015,
        "Manufactured fields; no body force, tank response or experimental validation.\n"
        + "Source: "
        + data["source_revision"][:12]
        + " · fixture: "
        + data["fixture_sha256"][:12],
        fontsize=9,
    )
    with args.output.open("xb") as stream:
        fig.savefig(
            stream,
            format="png",
            dpi=130,
            metadata={"Software": "Matplotlib " + matplotlib.__version__},
        )
    plt.close(fig)


if __name__ == "__main__":
    main()
