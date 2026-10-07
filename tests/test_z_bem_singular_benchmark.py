import importlib.util
import math
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools/research/benchmark_bem_singular_panel_primitives.py"
SPEC = importlib.util.spec_from_file_location("bem_singular_primitive_benchmark", TOOL)
BENCHMARK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BENCHMARK)


def test_singular_primitive_benchmark_repeats_checksums_without_matrix_allocation():
    result = BENCHMARK.run_level(panels=1, order=4, wall_time_cap_seconds=120.0)

    assert result["node_count"] == 4
    assert result["singular_correction_cases"] == 8
    assert result["singular_primitive_families"] == [
        "cauchy_principal_value_panel",
        "logarithmic_panel",
    ]
    assert result["density_modes"] == [0, 1]
    assert result["matrix_allocated"] is False
    assert len(result["correction_output_sha256"]) == 64
    assert len(result["repeat_records"]) == 3
    assert all(math.isfinite(record["wall_time_s"]) for record in result["repeat_records"])


@pytest.mark.parametrize("panels", [0, -1])
def test_singular_primitive_benchmark_rejects_nonpositive_panel_count(panels):
    with pytest.raises((ArithmeticError, ValueError, ZeroDivisionError)):
        BENCHMARK.run_level(panels=panels, order=4, wall_time_cap_seconds=120.0)
