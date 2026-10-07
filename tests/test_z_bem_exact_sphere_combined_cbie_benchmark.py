from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "tools/research/benchmark_bem_exact_sphere_combined_cbie.py"
)


def _decode(value: str) -> complex:
    real, imaginary = value.split(":")
    return complex(float.fromhex(real), float.fromhex(imaginary))


def test_combined_cbie_action_repeats_and_reconstructs_recorded_residual():
    spec = importlib.util.spec_from_file_location("combined_cbie_benchmark", _SCRIPT)
    assert spec is not None and spec.loader is not None
    benchmark = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(benchmark)

    case = benchmark._measure(175.0, 64)
    expected = (
        _decode(case["jump_half_pressure"])
        + _decode(case["direct_double_layer"])
        + _decode(case["image_double_layer"])
        - _decode(case["direct_single_layer"])
        - _decode(case["image_single_layer"])
    )

    assert case["repeat_checksum_sha256"]
    assert _decode(case["cbie_residual"]) == expected
    assert case["normalized_residual_by_boundary_pressure"] >= 0.0
