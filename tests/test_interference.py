"""B-05 numerical verification of coherent vector superposition; no physical verdict."""

import copy
import json
import math
import resource
import sys
import time
import tracemalloc
from dataclasses import replace
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from interference_reference import reference
from plane_wave_reference import pairs_as_complex, sin_cos
from test_plane_wave import flatten, metrics

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields import (
    FieldSamples,
    PlaneWave,
    evaluate_counterpropagating_pair,
    evaluate_plane_wave,
    evaluate_plane_wave_pair,
    mean_intensity_w_m2,
)

FIXTURE = Path(__file__).parent / "fixtures/fields/B05-interference.json"
DATA = json.loads(FIXTURE.read_text())
CASES = DATA["cases"]
TOLERANCE = 2048 * sys.float_info.epsilon


def evaluate(case):
    return evaluate_plane_wave_pair(
        PlaneWave(**case["first"]),
        PlaneWave(**case["second"]),
        case["coordinates_m"],
        box_min_m=case["box_min_m"],
        box_max_m=case["box_max_m"],
        workspace_bytes=case["workspace_bytes"],
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_independent_field_and_integrated_flux(case, record_property):
    field = evaluate(case)
    observed = metrics(field, reference(case))
    record_property("case_id", case["id"])
    record_property("normalized_tolerance", TOLERANCE)
    record_property("field_error_metrics", json.dumps(observed, sort_keys=True))
    assert DATA["normalized_tolerance"] == TOLERANCE
    assert all(item["max"] <= TOLERANCE for item in observed.values()), observed
    assert FieldSamples.from_artifacts(field.to_artifacts()) == field


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_decimal_precision_stability(case):
    first, second = reference(case, 60), reference(case, 80)
    with localcontext() as context:
        context.prec = 90
        for name in ("pressure", "velocity", "pressure_gradient", "intensity"):
            for a, b in zip(flatten(first[name]), flatten(second[name]), strict=True):
                assert abs(a - b) / second["scales"][name] < Decimal("1e-45")


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_backend_at_actual_arguments(case, monkeypatch, record_property):
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


def test_literal_b05_table_checks_oracle_and_production():
    field = evaluate(CASES[0])
    oracle = reference(CASES[0])
    k, a, z = 2 * math.pi / 0.0015, 2, 1_500_000
    tables = {
        "pressure": [2, 0, 1 + 1j, 2j],
        "velocity": [(1, 1, 0), (1, -1, 0), (1j, 1, 0), (1j, 1j, 0)],
        "pressure_gradient": [(1j, 1j, 0), (1j, -1j, 0), (-1, 1j, 0), (-1, -1, 0)],
        "intensity": [(2, 2, 0), (0, 0, 0), (1, 1, 0), (2, 2, 0)],
    }
    actual = {
        "pressure": field.pressure_pa,
        "velocity": field.velocity_m_s,
        "pressure_gradient": field.pressure_gradient_pa_m,
        "intensity": mean_intensity_w_m2(field),
    }
    scales = {
        "pressure": a,
        "velocity": a / z,
        "pressure_gradient": k * a,
        "intensity": a * a / (2 * z),
    }
    for name, expected in tables.items():
        if name == "intensity":
            independent = [float(x) for x in flatten(oracle[name])]
        else:
            rows = oracle[name] if name == "pressure" else [x for row in oracle[name] for x in row]
            independent = pairs_as_complex(rows)
        for values in (flatten(actual[name]), independent):
            for got, want in zip(values, flatten(expected), strict=True):
                assert abs(got / scales[name] - want) <= TOLERANCE
    node = FieldSamples.from_artifacts(field.to_artifacts())
    assert abs(node.pressure_pa[1]) / 4 <= TOLERANCE
    assert abs(node.velocity_m_s[1][0]) > 1e-6
    assert node.velocity_m_s[1][1].real < -1e-6
    assert abs(node.pressure_gradient_pa_m[1][0]) > 8000


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_order_invariance_and_euler(case):
    field = evaluate(case)
    assert field == evaluate({**case, "first": case["second"], "second": case["first"]})
    scale = float(reference(case)["scales"]["pressure_gradient"])
    for vs, gs in zip(field.velocity_m_s, field.pressure_gradient_pa_m, strict=True):
        for v, g in zip(vs, gs, strict=True):
            assert abs(g - 1j * 2 * math.pi * 1e6 * 1000 * v) / scale <= TOLERANCE


def test_frozen_rotation_translation_and_common_phase():
    base = evaluate(CASES[0])
    rotated = evaluate(CASES[1])
    assert rotated.pressure_pa == base.pressure_pa
    for name in ("velocity_m_s", "pressure_gradient_pa_m"):
        assert getattr(rotated, name) == tuple(row[1:] + row[:1] for row in getattr(base, name))
    assert mean_intensity_w_m2(rotated) == tuple(
        row[1:] + row[:1] for row in mean_intensity_w_m2(base)
    )
    assert all(
        v["max"] <= TOLERANCE for v in metrics(evaluate(CASES[3]), reference(CASES[0])).values()
    )
    phase = evaluate(CASES[2])
    for name, scale in (
        ("pressure_pa", 4),
        ("velocity_m_s", 4 / 1.5e6),
        ("pressure_gradient_pa_m", 4 * 2 * math.pi / 0.0015),
    ):
        assert all(
            abs(a - 1j * b) / scale <= TOLERANCE
            for a, b in zip(
                flatten(getattr(phase, name)), flatten(getattr(base, name)), strict=True
            )
        )
    assert all(
        abs(a - b) / (16 / (2 * 1.5e6)) <= TOLERANCE
        for a, b in zip(
            flatten(mean_intensity_w_m2(phase)), flatten(mean_intensity_w_m2(base)), strict=True
        )
    )


def test_distinct_reference_reparameterization_and_neighboring_nodes():
    case = copy.deepcopy(CASES[0])
    case["first"].update(reference_m=[0.000375, 0, 0], phase_rad=math.pi / 2)
    case["second"].update(reference_m=[0, -0.0001875, 0], phase_rad=-math.pi / 4)
    assert all(v["max"] <= TOLERANCE for v in metrics(evaluate(case), reference(CASES[0])).values())
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [
        [0, math.nextafter(0.00075, direction), 0] for direction in (-math.inf, math.inf)
    ]
    field = evaluate(case)
    assert all(v["max"] <= TOLERANCE for v in metrics(field, reference(case)).values())
    assert all(abs(row[0]) > 1e-6 and abs(row[1]) > 1e-6 for row in field.velocity_m_s)


def test_parallel_opposite_single_and_zero_limits():
    case = copy.deepcopy(CASES[0])
    first = PlaneWave(**case["first"])
    options = {k: case[k] for k in ("box_min_m", "box_max_m", "workspace_bytes")}
    case["second"]["direction"] = [1, 0, 0]
    assert evaluate(case) == evaluate_plane_wave(
        replace(first, peak_pressure_pa=4), case["coordinates_m"], **options
    )
    case["second"]["direction"] = [-1, 0, 0]
    assert evaluate(case) == evaluate_counterpropagating_pair(
        first, PlaneWave(**case["second"]), case["coordinates_m"], **options
    )
    with pytest.raises(InvalidInputError, match="FIELD_DIRECTION"):
        evaluate_counterpropagating_pair(
            first, PlaneWave(**CASES[0]["second"]), case["coordinates_m"], **options
        )
    assert evaluate(CASES[7]) == evaluate_plane_wave(first, case["coordinates_m"], **options)
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


@pytest.mark.parametrize(
    "corruption", ["average_pressure", "scalar_speeds", "drop_node_vectors", "rotate_only_samples"]
)
def test_known_wrong_fields_are_detected(corruption):
    field = evaluate(CASES[0])
    if corruption == "average_pressure":
        field = replace(field, pressure_pa=[p / 2 for p in field.pressure_pa])
    elif corruption == "scalar_speeds":
        field = replace(field, velocity_m_s=[(4 / 1.5e6, 0, 0)] * 4)
    elif corruption == "drop_node_vectors":
        vs, gs = list(field.velocity_m_s), list(field.pressure_gradient_pa_m)
        vs[1] = gs[1] = (0, 0, 0)
        field = replace(field, velocity_m_s=vs, pressure_gradient_pa_m=gs)
    else:
        case = copy.deepcopy(CASES[0])
        case["coordinates_m"] = CASES[1]["coordinates_m"]
        field = evaluate(case)
    assert any(v["max"] > TOLERANCE for v in metrics(field, reference(CASES[0])).values())


def test_individual_flux_sum_misses_coherent_cross_term():
    field = evaluate(CASES[0])
    actual = mean_intensity_w_m2(field)
    independent_single_flux = 2**2 / (2 * 1_500_000)
    assert actual[0][0] == 2 * independent_single_flux
    assert actual[0][1] == 2 * independent_single_flux
    assert abs(actual[1][0]) / (16 / (2 * 1.5e6)) <= TOLERANCE
    assert abs(actual[0][0] - independent_single_flux) / (16 / (2 * 1.5e6)) > TOLERANCE


@pytest.mark.parametrize(
    "source,key,bad",
    [
        ("second", "density_kg_m3", 999),
        ("second", "sound_speed_m_s", 1499),
        ("second", "frequency_hz", 999999),
        ("second", "direction", [0, 2, 0]),
        ("second", "direction", [0, 0, 0]),
        ("second", "dynamic_viscosity_pa_s", 0.001),
        ("first", "amplitude_attenuation_per_m", 0.1),
        ("second", "phase_rad", 5 * math.pi),
        ("first", "phase_rad", 5 * math.pi),
        ("second", "reference_m", [0, 1e10, 0]),
        ("second", "peak_pressure_pa", float("nan")),
    ],
)
def test_source_preflight_precedes_either_evaluation(source, key, bad, monkeypatch):
    import aura.fields.analytic as implementation

    case = copy.deepcopy(CASES[6])
    case[source][key] = bad

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid source reached field evaluation")

    monkeypatch.setattr(implementation, "_evaluate_prepared", forbidden)
    with pytest.raises(InvalidInputError):
        evaluate(case)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("coordinates_m", []),
        ("coordinates_m", [[0, 0, 0]] * 257),
        ("coordinates_m", [[0, 0.002, 0]]),
        ("coordinates_m", [[True, 0, 0]]),
        ("coordinates_m", [[0, float("inf"), 0]]),
        ("coordinates_m", None),
        ("box_min_m", [0.0015] * 3),
        ("box_max_m", [0, 0]),
        ("workspace_bytes", 4096 * 4 + 8191),
        ("workspace_bytes", True),
        ("workspace_bytes", 1e7),
    ],
)
def test_geometry_and_budget_preflight(key, bad, monkeypatch):
    import aura.fields.analytic as implementation

    case = copy.deepcopy(CASES[0])
    case[key] = bad

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid geometry reached field evaluation")

    monkeypatch.setattr(implementation, "_evaluate_prepared", forbidden)
    with pytest.raises(InvalidInputError):
        evaluate(case)


def test_invalid_specs_and_unrepresentable_sum():
    first, second = PlaneWave(**CASES[0]["first"]), PlaneWave(**CASES[0]["second"])
    options = {k: CASES[0][k] for k in ("box_min_m", "box_max_m", "workspace_bytes")}
    for waves in ((None, second), (first, {}), (first, [second])):
        with pytest.raises(InvalidInputError, match="FIELD_SPEC"):
            evaluate_plane_wave_pair(*waves, [[0, 0, 0]], **options)
    huge = copy.deepcopy(CASES[0])
    huge["coordinates_m"] = [[0, 0, 0]]
    for wave in (huge["first"], huge["second"]):
        wave.update(peak_pressure_pa=1e308, frequency_hz=1)
    with pytest.raises(NumericalDomainError, match="NUMERIC_RANGE"):
        evaluate(huge)


def test_maximum_resource_measurement(record_property):
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[0, 0.00075, 0]] * 256
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
    assert peak <= 4096 * 256 + 8192
    assert len(encoded) <= 32768 + 1024 * 256
    assert field.coordinates_m == ((0, 0.00075, 0),) * 256
