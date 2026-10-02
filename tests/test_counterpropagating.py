"""B-04 field, cancellation, reference and admission checks; no physical validation."""

import copy
import json
import math
import resource
import subprocess
import sys
import time
import tracemalloc
from dataclasses import replace
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from counterpropagating_reference import reference
from plane_wave_reference import sin_cos
from test_plane_wave import flatten, metrics

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields import (
    FieldSamples,
    PlaneWave,
    evaluate_counterpropagating_pair,
    evaluate_plane_wave,
    mean_intensity_w_m2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "fields" / "B04-counterpropagating.json"
DATA = json.loads(FIXTURE.read_text())
CASES = DATA["cases"]
TOLERANCE = 2048 * sys.float_info.epsilon


def evaluate(case):
    return evaluate_counterpropagating_pair(
        PlaneWave(**case["forward"]),
        PlaneWave(**case["backward"]),
        case["coordinates_m"],
        box_min_m=case["box_min_m"],
        box_max_m=case["box_max_m"],
        workspace_bytes=case["workspace_bytes"],
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_independent_combined_identity(case, record_property):
    field = evaluate(case)
    observed = metrics(field, reference(case))
    record_property("case_id", case["id"])
    record_property("normalized_tolerance", TOLERANCE)
    record_property("field_error_metrics", json.dumps(observed, sort_keys=True))
    assert DATA["normalized_tolerance"] == TOLERANCE
    assert all(item["max"] <= TOLERANCE for item in observed.values()), observed
    assert FieldSamples.from_artifacts(field.to_artifacts()) == field


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_independent_precision_stability(case):
    first, second = reference(case, 60), reference(case, 80)
    with localcontext() as context:
        context.prec = 90
        for name in ("pressure", "velocity", "pressure_gradient", "intensity"):
            for a, b in zip(flatten(first[name]), flatten(second[name]), strict=True):
                assert abs(a - b) / second["scales"][name] < Decimal("1e-45")


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_actual_backend_arguments(case, monkeypatch, record_property):
    errors = []

    def checked(function, index):
        def call(angle):
            result = function(angle)
            expected = sin_cos(Decimal.from_float(angle), 80)[index]
            errors.append(float(abs(Decimal.from_float(result) - expected)))
            return result

        return call

    monkeypatch.setattr(math, "sin", checked(math.sin, 0))
    monkeypatch.setattr(math, "cos", checked(math.cos, 1))
    evaluate(case)
    record_property("backend_absolute_error_max", max(errors))
    assert len(errors) == 4 * len(case["coordinates_m"])
    assert max(errors) <= 4 * sys.float_info.epsilon


def test_literal_nodes_phases_and_signed_flux():
    a, z, k = 2, 1_500_000, 2 * math.pi / 0.0015
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = CASES[1]["coordinates_m"]
    # Independently frozen B-04 table: pressure, axial velocity, gradient, flux.
    tables = [
        (case, [(2, 0, 0, 0), (0, 2j, -2, 0), (-2, 0, 0, 0), (0, -2j, 2, 0)]),
        (CASES[1], [(1 + 1j, 1 - 1j, 1 + 1j, 0)]),
        (CASES[2], [(3, 1, 1j, 3)]),
        (CASES[3], [(3, -1, -1j, -3)]),
    ]
    for case, rows in tables:
        field, oracle = evaluate(case), reference(case)
        flux = mean_intensity_w_m2(field)
        for i, (p, v, g, intensity) in enumerate(rows):
            assert abs(field.pressure_pa[i] / a - p) <= TOLERANCE
            assert abs(field.velocity_m_s[i][0] * z / a - v) <= TOLERANCE
            assert abs(field.pressure_gradient_pa_m[i][0] / (k * a) - g) <= TOLERANCE
            assert abs(flux[i][0] / (a * a / (2 * z)) - intensity) <= TOLERANCE
            for name, target, scale in (
                ("pressure", p, a),
                ("velocity", v, a / z),
                ("pressure_gradient", g, k * a),
            ):
                pair = oracle[name][i] if name == "pressure" else oracle[name][i][0]
                assert abs(complex(*map(float, pair)) / scale - target) <= TOLERANCE
            assert (
                abs(float(oracle["intensity"][i][0]) / (a * a / (2 * z)) - intensity) <= TOLERANCE
            )
    restored = FieldSamples.from_artifacts(evaluate(tables[0][0]).to_artifacts())
    assert abs(restored.pressure_pa[1]) < 1e-12
    assert abs(restored.velocity_m_s[1][0]) > 2e-6


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_order_and_euler(case):
    field = evaluate(case)
    swapped = evaluate({**case, "forward": case["backward"], "backward": case["forward"]})
    assert field == swapped
    for velocity, gradient in zip(field.velocity_m_s, field.pressure_gradient_pa_m, strict=True):
        for v, g in zip(velocity, gradient, strict=True):
            assert (
                abs(g - 1j * 2 * math.pi * 1e6 * 1000 * v) / (6 * 2 * math.pi / 0.0015) <= TOLERANCE
            )


def test_translation_rotation_common_phase_and_single_source():
    case = copy.deepcopy(CASES[2])
    field = evaluate(case)
    for wave in (case["forward"], case["backward"]):
        wave["reference_m"] = [0.000375, 0, 0]
    case["coordinates_m"] = [[x + 0.000375, y, z] for x, y, z in case["coordinates_m"]]
    assert all(v["max"] <= TOLERANCE for v in metrics(evaluate(case), reference(CASES[2])).values())
    case = copy.deepcopy(CASES[5])
    oblique = evaluate(case)
    for wave in (case["forward"], case["backward"]):
        wave["direction"] = wave["direction"][1:] + wave["direction"][:1]
    case["coordinates_m"] = [point[1:] + point[:1] for point in case["coordinates_m"]]
    rotated = evaluate(case)
    assert rotated.pressure_pa == oblique.pressure_pa
    assert rotated.velocity_m_s == tuple(row[1:] + row[:1] for row in oblique.velocity_m_s)
    assert rotated.pressure_gradient_pa_m == tuple(
        row[1:] + row[:1] for row in oblique.pressure_gradient_pa_m
    )
    common = evaluate(CASES[4])
    equal = evaluate({**CASES[0], "coordinates_m": CASES[4]["coordinates_m"]})
    for name, scale in (
        ("pressure_pa", 4),
        ("velocity_m_s", 4 / 1.5e6),
        ("pressure_gradient_pa_m", 4 * 2 * math.pi / 0.0015),
    ):
        assert all(
            abs(a - 1j * b) / scale <= TOLERANCE
            for a, b in zip(
                flatten(getattr(common, name)), flatten(getattr(equal, name)), strict=True
            )
        )
    single = CASES[7]
    progressive = evaluate_plane_wave(
        PlaneWave(**single["forward"]),
        single["coordinates_m"],
        box_min_m=single["box_min_m"],
        box_max_m=single["box_max_m"],
        workspace_bytes=single["workspace_bytes"],
    )
    assert evaluate(single) == progressive
    assert field.pressure_pa[0] == 6
    zero = evaluate(CASES[6])
    assert all(
        x == 0
        for x in flatten(
            [
                zero.pressure_pa,
                zero.velocity_m_s,
                zero.pressure_gradient_pa_m,
                mean_intensity_w_m2(zero),
            ]
        )
    )


@pytest.mark.parametrize("corruption", ["velocity_sign", "averaging", "missing_gradient"])
def test_detect_known_wrong_fields(corruption):
    field = evaluate(CASES[0])
    if corruption == "velocity_sign":
        field = replace(field, velocity_m_s=[[-v for v in row] for row in field.velocity_m_s])
    elif corruption == "averaging":
        field = replace(field, pressure_pa=[p / 2 for p in field.pressure_pa])
    else:
        field = replace(field, pressure_gradient_pa_m=[[0, 0, 0]] * len(field.pressure_pa))
    assert any(v["max"] > TOLERANCE for v in metrics(field, reference(CASES[0])).values())


def test_pressure_only_flux_shortcut_is_detectably_wrong():
    field = evaluate(CASES[0])
    actual = mean_intensity_w_m2(field)[0][0]
    wrong = abs(field.pressure_pa[0]) ** 2 / (2 * 1_500_000)
    assert actual == 0 and wrong > 0
    assert abs(actual - wrong) / float(reference(CASES[0])["scales"]["intensity"]) > TOLERANCE


@pytest.mark.parametrize(
    "source,key,bad",
    [
        ("backward", "density_kg_m3", 999),
        ("backward", "sound_speed_m_s", 1499),
        ("backward", "frequency_hz", 999999),
        ("backward", "direction", [0, -1, 0]),
        ("backward", "direction", [-1, 1e-15, 0]),
        ("backward", "phase_rad", 5 * math.pi),
        ("forward", "phase_rad", 5 * math.pi),
        ("backward", "reference_m", [1e10, 0, 0]),
    ],
)
def test_bad_second_source_rejected_before_either_is_evaluated(source, key, bad, monkeypatch):
    import aura.fields.analytic as implementation

    case = copy.deepcopy(CASES[6])  # Zero drive must not bypass input checks.
    case[source][key] = bad

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid pair reached field evaluation")

    monkeypatch.setattr(implementation, "_evaluate_prepared", forbidden)
    with pytest.raises(InvalidInputError):
        evaluate(case)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("coordinates_m", []),
        ("coordinates_m", [[0, 0, 0]] * 257),
        ("coordinates_m", [[0, 0, 0], [0.002, 0, 0]]),
        ("coordinates_m", [[float("nan"), 0, 0]]),
        ("coordinates_m", [[True, 0, 0]]),
        ("coordinates_m", None),
        ("box_min_m", [0.0015, 0, 0]),
        ("box_max_m", [float("inf"), 1, 1]),
        ("workspace_bytes", 4096 * 129 + 8191),
        ("workspace_bytes", True),
        ("workspace_bytes", 2.0),
    ],
)
def test_bad_geometry_and_budget_fail_before_evaluation(key, bad, monkeypatch):
    import aura.fields.analytic as implementation

    case = copy.deepcopy(CASES[0])
    case[key] = bad

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid pair reached field evaluation")

    monkeypatch.setattr(implementation, "_evaluate_prepared", forbidden)
    with pytest.raises(InvalidInputError):
        evaluate(case)


def test_wrong_spec_and_combined_overflow():
    case = CASES[0]
    for first, second in (
        (None, PlaneWave(**case["backward"])),
        (PlaneWave(**case["forward"]), None),
    ):
        with pytest.raises(InvalidInputError, match="FIELD_SPEC"):
            evaluate_counterpropagating_pair(
                first,
                second,
                [[0, 0, 0]],
                box_min_m=[-1] * 3,
                box_max_m=[1] * 3,
                workspace_bytes=12288,
            )
    huge = copy.deepcopy(case)
    huge["coordinates_m"] = [[0, 0, 0]]
    for wave in (huge["forward"], huge["backward"]):
        wave.update(peak_pressure_pa=1e308, frequency_hz=1)
    with pytest.raises(NumericalDomainError, match="NUMERIC_RANGE"):
        evaluate(huge)


def test_maximum_workspace_encoding_and_duplicate_samples(record_property):
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[0.000375, 0, 0]] * 256
    case["workspace_bytes"] = 4096 * 256 + 8192
    start = time.perf_counter()
    tracemalloc.start()
    try:
        field = evaluate(case)
        encoded = json.dumps(field.to_artifacts(), allow_nan=False).encode()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    record_property("peak_traced_python_bytes", peak)
    record_property("encoded_component_bytes", len(encoded))
    record_property("evaluation_and_encoding_elapsed_s", time.perf_counter() - start)
    record_property(
        "whole_test_process_peak_rss_bytes",
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    )
    assert field.coordinates_m == ((0.000375, 0, 0),) * 256
    assert peak <= 4096 * 256 + 8192
    assert len(encoded) <= 32768 + 1024 * 256


def test_export_matches_frozen_fields_and_refuses_overwrite(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "plot-data.json"
    command = [sys.executable, str(root / "scripts/export_standing_wave.py"), str(output)]
    completed = subprocess.run(command, capture_output=True, timeout=10, check=False)
    assert completed.returncode == 0, completed.stderr
    content = output.read_bytes()
    exported = json.loads(content)
    assert exported["format"] == "B04-PLOT-1.0"
    assert len(exported["cases"]) == 8
    for case, stored in zip(CASES, exported["cases"], strict=True):
        field = evaluate(case)
        assert stored["id"] == case["id"]
        assert FieldSamples.from_artifacts(stored["field_artifacts"]) == field
        assert stored["pressure_magnitude_pa"] == [abs(p) for p in field.pressure_pa]
        assert stored["velocity_x_magnitude_m_s"] == [abs(v[0]) for v in field.velocity_m_s]
        assert stored["intensity_x_w_m2"] == [v[0] for v in mean_intensity_w_m2(field)]
    rejected = subprocess.run(command, capture_output=True, timeout=10, check=False)
    assert rejected.returncode != 0
    assert output.read_bytes() == content
