import importlib.util
from pathlib import Path

import pytest

TOOL = (
    Path(__file__).resolve().parents[1]
    / "tools/research/benchmark_bem_exact_sphere_image_action.py"
)
SPEC = importlib.util.spec_from_file_location("bem_exact_sphere_image_action", TOOL)
BENCHMARK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BENCHMARK)


def test_ring_routes_and_meridian_refinement_are_reported_against_exact_image():
    coarse = BENCHMARK.image_action(
        120.0, 16, azimuth_samples=128, route="static_subtracted_ring"
    )
    medium = BENCHMARK.image_action(
        120.0, 32, azimuth_samples=128, route="static_subtracted_ring"
    )
    fine = BENCHMARK.image_action(
        120.0, 64, azimuth_samples=128, route="static_subtracted_ring"
    )
    independent_ring = BENCHMARK.image_action(
        120.0, 16, azimuth_samples=2048, route="pointwise_midpoint"
    )

    assert coarse["relative_complex_difference"] > medium["relative_complex_difference"]
    assert medium["relative_complex_difference"] > fine["relative_complex_difference"]
    def decode(encoded):
        real, imaginary = encoded.split(":")
        return complex(float.fromhex(real), float.fromhex(imaginary))

    assert decode(coarse["image_action"]) == pytest.approx(
        decode(independent_ring["image_action"]), rel=2e-12
    )
    assert all(item["double_layer"] and item["single_layer"] for item in (coarse, medium, fine))


def test_near_plane_case_records_finite_unresolved_meridian_sensitivity():
    result = BENCHMARK.image_action(
        179.0, 64, azimuth_samples=128, route="static_subtracted_ring"
    )

    assert result["relative_complex_difference"] > 0.0
    assert result["absolute_complex_difference"] > 0.0
    assert result["image_action"] != result["analytic_reflected_monopole"]
