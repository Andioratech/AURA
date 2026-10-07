from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "tools/research/benchmark_bem_exact_sphere_cbie_azimuth_sensitivity.py"
)


def _load_harness():
    spec = importlib.util.spec_from_file_location("cbie_azimuth_sensitivity", SCRIPT)
    assert spec is not None and spec.loader is not None
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    return harness


def test_azimuth_sensitivity_grid_is_factorial_and_fixed_meridian():
    harness = _load_harness()
    grid = harness.case_grid()

    assert len(grid) == 36
    assert len(set(grid)) == 36
    assert {case[0] for case in grid} == {120.0, 135.0, 175.0, 179.0}
    assert {case[1] for case in grid} == {256, 512, 1_024}
    assert {case[2] for case in grid} == {512, 1_024, 2_048}
    assert harness.MERIDIAN_ORDER == 256


def test_azimuth_sensitivity_case_repeats_and_reconstructs_residual():
    harness = _load_harness()
    case = harness.measure_case(175.0, 256, 512, meridian_order=256)

    assert case["repeat_checksum_sha256"]
    assert case["collocation_theta_degrees"] == 175.0
    assert case["direct_azimuth_samples"] == 256
    assert case["image_azimuth_samples"] == 512
    assert len(case["repeat_wall_times_s"]) == 2
