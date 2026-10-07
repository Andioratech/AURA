import importlib.util
import math
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools/research/benchmark_bem_direct_sphere_maue_diagonal.py"
SPEC = importlib.util.spec_from_file_location("bem_direct_sphere_diagonal_benchmark", TOOL)
BENCHMARK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BENCHMARK)


def test_direct_sphere_maue_self_panel_benchmark_checksums_without_matrix():
    result = BENCHMARK.run_level(
        panels=1,
        meridian_order=4,
        azimuth_samples=16,
        wall_time_cap_seconds=120.0,
    )

    assert result["node_count"] == 4
    assert result["self_panel_action_count_per_repeat"] == 8
    assert result["density_modes"] == [0, 1]
    assert result["matrix_allocated"] is False
    assert len(result["self_panel_output_sha256"]) == 64
    assert len(result["repeat_records"]) == 3
    assert all(math.isfinite(item["wall_time_s"]) for item in result["repeat_records"])


@pytest.mark.parametrize("panels", [0, -1])
def test_direct_sphere_maue_self_panel_benchmark_rejects_invalid_panel_count(panels):
    with pytest.raises(ValueError, match="panels"):
        BENCHMARK.run_level(
            panels=panels,
            meridian_order=4,
            azimuth_samples=16,
            wall_time_cap_seconds=120.0,
        )
