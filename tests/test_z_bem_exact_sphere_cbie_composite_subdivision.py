from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / (
    "tools/research/benchmark_bem_exact_sphere_cbie_composite_subdivision.py"
)


def _load_harness():
    spec = importlib.util.spec_from_file_location("cbie_composite_subdivision", SCRIPT)
    assert spec is not None and spec.loader is not None
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    return harness


def test_composite_subdivision_grid_fixes_cutoff_order_and_azimuth_counts():
    harness = _load_harness()
    grid = harness.case_grid()

    assert grid == ((179.0, 10),)
    assert harness.MERIDIAN_SPLIT_FACTOR == 8.0
    assert harness.MERIDIAN_ORDER == 256
    assert harness.DIRECT_AZIMUTH_SAMPLES == 4_096
    assert harness.IMAGE_AZIMUTH_SAMPLES == 2_048


def test_composite_subdivision_case_repeats_and_reconstructs_residual():
    harness = _load_harness()
    case = harness.measure_case(179.0, 10)

    assert case["repeat_checksum_sha256"]
    assert case["collocation_theta_degrees"] == 179.0
    assert case["meridian_split_factor"] == 8.0
    assert case["meridian_subdivisions_per_active_interval"] == 10
    assert case["active_meridian_subintervals"] == 2
    assert case["evaluated_meridian_panels"] == 20
    assert case["meridian_order_per_active_subinterval"] == 256
    assert case["direct_azimuth_samples"] == 4_096
    assert case["image_azimuth_samples"] == 2_048
    assert len(case["repeat_wall_times_s"]) == 2


def test_action_rejects_nonpositive_or_noninteger_subdivision_count():
    harness = _load_harness()
    action = harness._base_module().evaluate_action

    for invalid in (0, -1, 1.5, True):
        try:
            action(175.0, 256, meridian_subdivisions=invalid)
        except ValueError as exc:
            assert "positive integer" in str(exc)
        else:
            raise AssertionError(f"Invalid subdivision count accepted: {invalid!r}")


def test_default_subdivision_matches_explicit_single_subdivision():
    action = _load_harness()._base_module().evaluate_action
    options = {"direct_azimuth_samples": 4, "image_azimuth_samples": 4}

    assert action(175.0, 64, **options) == action(
        175.0, 64, meridian_subdivisions=1, **options
    )
