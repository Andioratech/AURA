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
        candidate_counts=(8,),
        split_multiples=(2.0, 6.0),
        repeats=2,
    )

    assert measured["image_separation_m"] > 0.0
    assert [item["azimuth_samples"] for item in measured["reference_midpoint"]] == [64, 128]
    assert len(measured["candidate_results"]) == 3
    assert all(len(item["repeat_wall_times_s"]) == 2 for item in measured["candidate_results"])
    assert all(item["repeat_checksum"] for item in measured["candidate_results"])
    assert all(math.isfinite(item["absolute_difference_from_high_reference"])
               for item in measured["candidate_results"])
    assert measured["candidate_results"][0]["rule"] == "midpoint"
    assert measured["candidate_results"][1]["split_multiple"] == 2.0
    assert measured["candidate_results"][2]["split_multiple"] == 6.0


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
