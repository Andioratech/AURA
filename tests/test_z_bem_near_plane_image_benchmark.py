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
