from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "tools/research/benchmark_bem_exact_sphere_cbie_meridian_refinement.py"
)


def _load_harness():
    spec = importlib.util.spec_from_file_location("cbie_meridian_refinement", SCRIPT)
    assert spec is not None and spec.loader is not None
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    return harness


def test_meridian_refinement_grid_freezes_azimuth_rules():
    harness = _load_harness()
    grid = harness.case_grid()

    assert len(grid) == 12
    assert len(set(grid)) == 12
    assert {case[0] for case in grid} == {120.0, 135.0, 175.0, 179.0}
    assert {case[1] for case in grid} == {256, 384, 512}
    assert {case[2] for case in grid} == {4_096}
    assert {case[3] for case in grid} == {2_048}


def test_meridian_refinement_case_repeats_and_reconstructs_residual():
    harness = _load_harness()
    case = harness.measure_case(175.0, 256, 4_096, 2_048)

    assert case["repeat_checksum_sha256"]
    assert case["collocation_theta_degrees"] == 175.0
    assert case["meridian_order_per_active_subinterval"] == 256
    assert case["direct_azimuth_samples"] == 4_096
    assert case["image_azimuth_samples"] == 2_048
    assert len(case["repeat_wall_times_s"]) == 2
