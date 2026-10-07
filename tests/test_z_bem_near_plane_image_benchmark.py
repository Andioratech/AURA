import importlib.util
import math
from pathlib import Path

TOOL = (
    Path(__file__).resolve().parents[1]
    / "tools/research/benchmark_bem_near_plane_image_ring.py"
)
SPEC = importlib.util.spec_from_file_location("bem_near_plane_image_benchmark", TOOL)
BENCHMARK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BENCHMARK)


def test_near_plane_image_benchmark_records_repeatable_refinements():
    case = BENCHMARK.geometry(175.0, 175.1)
    measured = BENCHMARK.measure_case(
        case,
        reference_counts=(64, 128),
        gauss_reference_cases=((4, 4), (8, 4)),
        candidate_counts=(8,),
        split_multiples=(2.0, 6.0),
        repeats=2,
    )

    assert measured["image_separation_m"] > 0.0
    assert [item["azimuth_samples"] for item in measured["reference_midpoint"]] == [64, 128]
    assert [item["panels"] for item in measured["reference_gauss_legendre"]] == [4, 8]
    assert math.isfinite(measured["midpoint_gauss_reference_relative_difference"])
    assert len(measured["candidate_results"]) == 3
    assert all(len(item["repeat_wall_times_s"]) == 2 for item in measured["candidate_results"])
    assert all(item["repeat_checksum"] for item in measured["candidate_results"])
    assert all(math.isfinite(item["absolute_difference_from_high_reference"])
               for item in measured["candidate_results"])
    assert all(math.isfinite(item["relative_difference_from_high_gauss_reference"])
               for item in measured["candidate_results"])
    assert measured["candidate_results"][0]["rule"] == "midpoint"
    assert measured["candidate_results"][1]["split_multiple"] == 2.0
    assert measured["candidate_results"][2]["split_multiple"] == 6.0


def test_gauss_legendre_rule_integrates_polynomial_moments():
    rule = BENCHMARK.gauss_legendre_rule(8)

    assert math.isclose(sum(weight for _, weight in rule), 2.0, rel_tol=0.0, abs_tol=2e-15)
    for degree in range(16):
        observed = math.fsum(weight * node**degree for node, weight in rule)
        expected = 0.0 if degree % 2 else 2.0 / (degree + 1)
        assert math.isclose(observed, expected, rel_tol=0.0, abs_tol=3e-15)
    assert BENCHMARK.gauss_legendre_rule(1) == ((0.0, 2.0),)


def test_candidate_mesh_pair_selection_is_deterministic_and_includes_diagonal():
    cases = BENCHMARK.candidate_mesh_pairs()

    assert len(cases) == 6
    assert [case["mesh_pair"]["node_count"] for case in cases] == [16, 16, 32, 32, 64, 64]
    for self_case, distinct_case in zip(cases[::2], cases[1::2], strict=True):
        self_pair = self_case["mesh_pair"]
        distinct_pair = distinct_case["mesh_pair"]
        assert self_pair["selection"] == "minimum_angular_scale_self_pair"
        assert self_pair["field_node_index"] == self_pair["source_node_index"]
        assert distinct_pair["selection"] == "minimum_angular_scale_distinct_pair"
        assert distinct_pair["field_node_index"] < distinct_pair["source_node_index"]
        assert self_pair["angular_scale_rad"] > 0.0
        assert distinct_pair["angular_scale_rad"] > 0.0


def test_candidate_mesh_diagonal_sweep_covers_every_gl4_node():
    cases = BENCHMARK.candidate_mesh_self_pairs()

    assert len(cases) == sum((16, 32, 64))
    for node_count in (16, 32, 64):
        mesh_cases = [
            case for case in cases if case["mesh_pair"]["node_count"] == node_count
        ]
        assert len(mesh_cases) == node_count
        assert [case["mesh_pair"]["field_node_index"] for case in mesh_cases] == list(
            range(node_count)
        )
        assert all(
            case["mesh_pair"]["selection"] == "diagonal_all_nodes"
            and case["mesh_pair"]["field_node_index"]
            == case["mesh_pair"]["source_node_index"]
            and case["field_theta_degrees"] == case["source_theta_degrees"]
            for case in mesh_cases
        )
        assert all(
            case["field_radius_m"]
            == BENCHMARK.SPHERE_RADIUS_M * math.sin(case["mesh_pair"]["field_theta_rad"])
            and case["source_height_m"]
            == BENCHMARK.PLANE_GAP_M
            + BENCHMARK.SPHERE_RADIUS_M
            * (1.0 + math.cos(case["mesh_pair"]["source_theta_rad"]))
            for case in mesh_cases
        )
