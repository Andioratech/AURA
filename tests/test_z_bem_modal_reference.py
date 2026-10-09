from __future__ import annotations

import cmath
import math
import subprocess
import sys
from pathlib import Path

import pytest

from tools.research.benchmark_bem_exact_sphere_modal_reference import (
    ANGLES_DEGREES,
    CUTOFFS,
    IMAGE_CENTER_DISTANCE_M,
    SPHERE_RADIUS_M,
    WAVE_NUMBER_RAD_M,
    evaluate_modal,
)


def _decode(value: dict[str, str]) -> complex:
    return complex(float.fromhex(value["real_hex"]), float.fromhex(value["imag_hex"]))


def test_modal_reference_import_keeps_field_backend_lazy():
    result = subprocess.run(
        (
            sys.executable,
            "-c",
            (
                "import sys; import tools.research.benchmark_bem_exact_sphere_modal_reference; "
                "assert 'aura.fields.numerical' not in sys.modules"
            ),
        ),
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("angle", ANGLES_DEGREES)
def test_image_layer_combination_matches_exact_reflected_monopole(angle):
    result = evaluate_modal(angle, 80)
    theta = math.radians(angle)
    image_distance = math.hypot(
        SPHERE_RADIUS_M * math.sin(theta),
        IMAGE_CENTER_DISTANCE_M + SPHERE_RADIUS_M * math.cos(theta),
    )
    exact_image = cmath.exp(1j * WAVE_NUMBER_RAD_M * image_distance) / (
        4.0 * math.pi * image_distance
    )
    image_layers = result["layers"]
    observed = _decode(image_layers["image_double_layer"]) - _decode(
        image_layers["image_single_layer"]
    )
    tail = float(result["layer_tail_upper_bounds_pa"]["image_double_layer_upper_pa"])
    assert abs(observed + exact_image) <= 2.0 * tail + 2e-12


def test_evaluator_records_each_layer_term_and_nested_candidate_tail_bounds():
    coarse, medium, fine = (evaluate_modal(179.0, cutoff) for cutoff in CUTOFFS)
    assert [case["cutoff_inclusive"] for case in (coarse, medium, fine)] == [48, 64, 80]
    assert all(len(case["modal_rows"]) == case["cutoff_inclusive"] + 1 for case in (coarse, medium, fine))
    assert all(case["tail_bound_status"] == "PRELIMINARY_OUTWARD_ROUNDED_CANDIDATE"
               for case in (coarse, medium, fine))
    layer_names = (
        "direct_double_layer_upper_pa",
        "direct_single_layer_upper_pa",
        "image_double_layer_upper_pa",
        "image_single_layer_upper_pa",
    )
    for layer in layer_names:
        assert float(fine["layer_tail_upper_bounds_pa"][layer]) < float(
            medium["layer_tail_upper_bounds_pa"][layer]
        ) < float(coarse["layer_tail_upper_bounds_pa"][layer])
    assert float(fine["layer_tail_upper_bounds_pa"]["direct_double_layer_upper_pa"]) == pytest.approx(
        2.560823123768433e-10, rel=2e-15
    )
    assert float(fine["layer_tail_upper_bounds_pa"]["direct_single_layer_upper_pa"]) == pytest.approx(
        1.282524282772518e-10, rel=2e-15
    )


def test_modal_trace_coefficients_reconstruct_closed_form_at_high_cutoff():
    result = evaluate_modal(179.0, 80)
    assert result["pressure_trace_absolute_difference_pa"] < 1e-12
    assert result["normal_derivative_trace_absolute_difference_pa_m"] < 1e-9


def test_same_modal_evaluation_repeats_bitwise():
    assert evaluate_modal(135.0, 64) == evaluate_modal(135.0, 64)


@pytest.mark.parametrize(
    ("angle", "cutoff"),
    [(True, 48), (90.0, 48), (179.0, True), (179.0, 32), (179.0, 96)],
)
def test_unsupported_modal_domain_is_rejected(angle, cutoff):
    with pytest.raises(ValueError):
        evaluate_modal(angle, cutoff)
