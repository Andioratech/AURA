from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "tools/research/benchmark_bem_exact_sphere_cbie_partition_sensitivity.py"
)


def _load_harness():
    spec = importlib.util.spec_from_file_location("cbie_partition_sensitivity", SCRIPT)
    assert spec is not None and spec.loader is not None
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    return harness


def test_partition_sensitivity_grid_fixes_meridian_and_azimuth_counts():
    harness = _load_harness()
    grid = harness.case_grid()

    assert len(grid) == 12
    assert len(set(grid)) == 12
    assert {case[0] for case in grid} == {120.0, 135.0, 175.0, 179.0}
    assert {case[1] for case in grid} == {6.0, 8.0, 10.0}
    assert harness.MERIDIAN_ORDER == 256
    assert harness.DIRECT_AZIMUTH_SAMPLES == 4_096
    assert harness.IMAGE_AZIMUTH_SAMPLES == 2_048


def test_partition_sensitivity_case_repeats_and_reconstructs_residual():
    harness = _load_harness()
    case = harness.measure_case(175.0, 8.0)

    assert case["repeat_checksum_sha256"]
    assert case["collocation_theta_degrees"] == 175.0
    assert case["meridian_split_factor"] == 8.0
    assert case["active_meridian_subintervals"] >= 1
    assert case["meridian_order_per_active_subinterval"] == 256
    assert case["direct_azimuth_samples"] == 4_096
    assert case["image_azimuth_samples"] == 2_048
    assert len(case["repeat_wall_times_s"]) == 2
