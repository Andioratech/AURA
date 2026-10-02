"""B-06 manufactured spherical-field verification; no physical-model acceptance."""

import copy
import json
import math
import resource
import sys
import time
import tracemalloc
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from plane_wave_reference import pairs_as_complex, sin_cos
from spherical_reference import reference
from test_plane_wave import flatten, metrics

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields import FieldSamples, SphericalWave, evaluate_spherical_wave, mean_intensity_w_m2

DATA = json.loads((Path(__file__).parent / "fixtures/fields/B06-spherical.json").read_text())
CASES = DATA["cases"]
TOLERANCE = 2048 * sys.float_info.epsilon


def evaluate(case):
    return evaluate_spherical_wave(
        SphericalWave(**case["wave"]),
        case["coordinates_m"],
        **{k: case[k] for k in ("box_min_m", "box_max_m", "workspace_bytes")},
    )


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_independent_field_and_flux(case, record_property):
    field = evaluate(case)
    observed = metrics(field, reference(case))
    record_property("case_id", case["id"])
    record_property("normalized_tolerance", TOLERANCE)
    record_property("field_error_metrics", json.dumps(observed, sort_keys=True))
    assert DATA["normalized_tolerance"] == TOLERANCE
    assert all(v["max"] <= TOLERANCE for v in observed.values()), observed
    assert FieldSamples.from_artifacts(field.to_artifacts()) == field


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_decimal_precision_stability(case):
    first, second = reference(case, 60), reference(case, 80)
    with localcontext() as context:
        context.prec = 90
        for name in ("pressure", "velocity", "pressure_gradient", "intensity"):
            for a, b in zip(flatten(first[name]), flatten(second[name]), strict=True):
                assert abs(a - b) / second["scales"][name] < Decimal("1e-45")


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_backend_at_actual_arguments(case, monkeypatch, record_property):
    trig_errors, norm_errors = [], []

    def checked(function, index):
        def call(angle):
            result = function(angle)
            expected = sin_cos(Decimal.from_float(angle), 80)[index]
            trig_errors.append(float(abs(Decimal.from_float(result) - expected)))
            return result

        return call

    original_hypot = math.hypot

    def checked_hypot(*args):
        result = original_hypot(*args)
        with localcontext() as context:
            context.prec = 90
            expected = sum(Decimal.from_float(x) ** 2 for x in args).sqrt()
            if expected:
                norm_errors.append(float(abs(Decimal.from_float(result) - expected) / expected))
        return result

    monkeypatch.setattr(math, "sin", checked(math.sin, 0))
    monkeypatch.setattr(math, "cos", checked(math.cos, 1))
    monkeypatch.setattr(math, "hypot", checked_hypot)
    evaluate(case)
    record_property("backend_absolute_error_max", max(trig_errors))
    record_property("hypot_relative_error_max", max(norm_errors))
    assert len(trig_errors) == 2 * len(case["coordinates_m"])
    assert max(trig_errors) <= 4 * sys.float_info.epsilon
    assert max(norm_errors) <= 2 * sys.float_info.epsilon


def test_literal_b06_table_checks_oracle_and_production():
    field, oracle = evaluate(CASES[0]), reference(CASES[0])
    k, a, z = 2 * math.pi / 0.0015, 2, 1_500_000
    tables = {
        "pressure": [1, 0.5j, -1 / 3],
        "velocity": [
            (1 + 2j / math.pi, 0, 0),
            (-1 / (2 * math.pi) + 0.5j, 0, 0),
            (-1 / 3 - 2j / (9 * math.pi), 0, 0),
        ],
        "pressure_gradient": [
            (-2 / math.pi + 1j, 0, 0),
            (-0.5 - 1j / (2 * math.pi), 0, 0),
            (2 / (9 * math.pi) - 1j / 3, 0, 0),
        ],
        "intensity": [(1, 0, 0), (0.25, 0, 0), (1 / 9, 0, 0)],
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


def test_distance_scaling_and_reference_normalization():
    field = evaluate(CASES[0])
    flux = mean_intensity_w_m2(field)
    assert field.pressure_pa[0] == 2
    for index, ratio in enumerate((1, 2, 3)):
        assert abs(abs(field.pressure_pa[index]) / 2 - 1 / ratio) <= TOLERANCE
        assert abs(flux[index][0] / flux[0][0] - 1 / ratio**2) <= TOLERANCE
        assert flux[index][1:] == (0, 0)
    assert field.velocity_m_s[0][0].imag > 0
    assert field.pressure_gradient_pa_m[0][0].real < 0


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_euler_relation(case):
    field = evaluate(case)
    scale = float(reference(case)["scales"]["pressure_gradient"])
    for vs, gs in zip(field.velocity_m_s, field.pressure_gradient_pa_m, strict=True):
        for v, g in zip(vs, gs, strict=True):
            assert abs(g - 1j * 2 * math.pi * 1e6 * 1000 * v) / scale <= TOLERANCE


def test_radial_directions_translation_and_phase():
    base, directions, phase, translated = [evaluate(case) for case in CASES[:4]]
    assert all(v["max"] <= TOLERANCE for v in metrics(translated, reference(CASES[0])).values())
    for name, scale in (
        ("pressure_pa", 2),
        ("velocity_m_s", 2 / 1.5e6),
        ("pressure_gradient_pa_m", 4 * math.pi / 0.0015),
    ):
        assert all(
            abs(a - 1j * b) / scale <= TOLERANCE
            for a, b in zip(
                flatten(getattr(phase, name)), flatten(getattr(base, name)), strict=True
            )
        )
    assert all(
        abs(a - b) / (4 / (2 * 1.5e6)) <= TOLERANCE
        for a, b in zip(
            flatten(mean_intensity_w_m2(phase)), flatten(mean_intensity_w_m2(base)), strict=True
        )
    )
    for row, n in enumerate(((-1, 0, 0), (0, 1, 0), (0, 0, -1), (0.6, 0.8, 0))):
        assert (
            abs(directions.pressure_pa[row] - base.pressure_pa[1 if row == 3 else 0]) / 2
            <= TOLERANCE
        )
        for name, scale in (
            ("velocity_m_s", 2 / 1.5e6),
            ("pressure_gradient_pa_m", 4 * math.pi / 0.0015),
        ):
            ref = getattr(base, name)[1 if row == 3 else 0][0]
            assert all(
                abs(got - ref * axis) / scale <= TOLERANCE
                for got, axis in zip(getattr(directions, name)[row], n, strict=True)
            )


def test_order_duplicates_zero_and_immutable_spec():
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [case["coordinates_m"][i] for i in (2, 0, 2, 1)]
    result, base = evaluate(case), evaluate(CASES[0])
    assert result.pressure_pa == tuple(base.pressure_pa[i] for i in (2, 0, 2, 1))
    assert result.coordinates_m[0] == result.coordinates_m[2]
    zero = evaluate(CASES[4])
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
    center = [0, 0, 0]
    wave = SphericalWave(**{**CASES[0]["wave"], "center_m": center})
    center[0] = 1
    assert wave.center_m == (0, 0, 0)
    with pytest.raises(FrozenInstanceError):
        wave.phase_rad = 1


@pytest.mark.parametrize("wrong", ["omit_reactive", "omit_spreading", "wrong_direction"])
def test_known_wrong_fields_are_detected(wrong):
    field = evaluate(CASES[0])
    if wrong == "omit_reactive":
        field = replace(field, velocity_m_s=[(p / 1.5e6, 0, 0) for p in field.pressure_pa])
    elif wrong == "omit_spreading":
        field = replace(field, pressure_pa=[p * (i + 1) for i, p in enumerate(field.pressure_pa)])
    else:
        field = replace(field, velocity_m_s=[tuple(-v for v in row) for row in field.velocity_m_s])
    assert any(v["max"] > TOLERANCE for v in metrics(field, reference(CASES[0])).values())


def test_inverse_distance_flux_is_detected():
    flux = mean_intensity_w_m2(evaluate(CASES[0]))
    for index, ratio in enumerate((2, 3), start=1):
        wrong = flux[0][0] / ratio
        assert abs(flux[index][0] - wrong) / (4 / (2 * 1.5e6)) > TOLERANCE


def test_exclusion_rounding_neighbors():
    radius = CASES[0]["wave"]["minimum_radius_m"]
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[math.nextafter(radius, -math.inf), 0, 0]]
    with pytest.raises(InvalidInputError, match="FIELD_EXCLUSION"):
        evaluate(case)
    case["coordinates_m"] = [[radius, 0, 0], [math.nextafter(radius, math.inf), 0, 0]]
    assert all(v["max"] <= TOLERANCE for v in metrics(evaluate(case), reference(case)).values())


@pytest.mark.parametrize(
    "key,bad",
    [
        ("density_kg_m3", 0),
        ("sound_speed_m_s", -1),
        ("frequency_hz", True),
        ("frequency_hz", float("inf")),
        ("peak_pressure_pa", -1),
        ("reference_radius_m", 0),
        ("reference_radius_m", 0.0001),
        ("minimum_radius_m", 0),
        ("minimum_radius_m", float("nan")),
        ("phase_rad", float("nan")),
        ("phase_rad", 5 * math.pi),
        ("center_m", [0, 0]),
        ("center_m", [True, 0, 0]),
        ("dynamic_viscosity_pa_s", 0.001),
        ("amplitude_attenuation_per_m", 0.1),
        ("peak_pressure_pa", "2"),
        ("density_kg_m3", 1e308),
    ],
)
def test_source_preflight(key, bad, monkeypatch):
    import aura.fields.analytic as implementation

    case = copy.deepcopy(CASES[4])
    case["wave"][key] = bad

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid source reached field evaluation")

    monkeypatch.setattr(implementation, "_evaluate_spherical_prepared", forbidden)
    with pytest.raises(InvalidInputError):
        evaluate(case)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("coordinates_m", []),
        ("coordinates_m", [[0.000375, 0, 0]] * 257),
        ("coordinates_m", [[0.000375, 0, 0], [0, 0, 0]]),
        ("coordinates_m", [[0.000374, 0, 0]]),
        ("coordinates_m", [[0.002, 0, 0]]),
        ("coordinates_m", [[True, 0, 0]]),
        ("coordinates_m", [[float("inf"), 0, 0]]),
        ("coordinates_m", None),
        ("box_min_m", [0.0015] * 3),
        ("box_max_m", [0, 0]),
        ("workspace_bytes", 4096 * 3 + 4095),
        ("workspace_bytes", True),
        ("workspace_bytes", 2e6),
    ],
)
def test_geometry_and_budget_preflight(key, bad, monkeypatch):
    import aura.fields.analytic as implementation

    case = copy.deepcopy(CASES[4])
    case[key] = bad

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid sample plan reached field evaluation")

    monkeypatch.setattr(implementation, "_evaluate_spherical_prepared", forbidden)
    with pytest.raises(InvalidInputError):
        evaluate(case)


def test_invalid_spec_conditioning_and_numeric_range():
    options = {k: CASES[0][k] for k in ("box_min_m", "box_max_m", "workspace_bytes")}
    for wave in (None, {}, CASES[0]["wave"]):
        with pytest.raises(InvalidInputError, match="FIELD_SPEC"):
            evaluate_spherical_wave(wave, CASES[0]["coordinates_m"], **options)
    case = copy.deepcopy(CASES[0])
    case["wave"].update(center_m=[1, 0, 0], frequency_hz=1)
    case.update(coordinates_m=[[1.00075, 0, 0]], box_min_m=[-2] * 3, box_max_m=[2] * 3)
    with pytest.raises(NumericalDomainError, match="FIELD_GEOMETRY_RANGE"):
        evaluate(case)
    case = copy.deepcopy(CASES[0])
    case["wave"]["frequency_hz"] = 1e7
    with pytest.raises(NumericalDomainError, match="FIELD_PHASE_RANGE"):
        evaluate(case)
    case = copy.deepcopy(CASES[0])
    case["wave"]["peak_pressure_pa"] = 1e308
    with pytest.raises(NumericalDomainError, match="NUMERIC_RANGE"):
        evaluate(case)
    case = copy.deepcopy(CASES[0])
    case["wave"]["peak_pressure_pa"] = 5e-324
    with pytest.raises(NumericalDomainError, match="NUMERIC_RANGE"):
        evaluate(case)


def test_maximum_resource_measurement(record_property):
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[0.00045, 0.0006, 0]] * 256
    case["workspace_bytes"] = 4096 * 256 + 4096
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
    assert peak <= 4096 * 256 + 4096
    assert len(encoded) <= 32768 + 1024 * 256
    assert field.coordinates_m == ((0.00045, 0.0006, 0),) * 256


def test_original_oblique_boundary_is_rejected_without_padding():
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[0.000225, 0.0003, 0]]
    assert math.hypot(0.000225, 0.0003, 0) < case["wave"]["minimum_radius_m"]
    with pytest.raises(InvalidInputError, match="FIELD_EXCLUSION"):
        evaluate(case)


def test_reference_sphere_reparameterization_and_box_faces():
    case = copy.deepcopy(CASES[0])
    case["wave"].update(reference_radius_m=0.00075, peak_pressure_pa=1, phase_rad=math.pi / 2)
    assert all(v["max"] <= TOLERANCE for v in metrics(evaluate(case), reference(CASES[0])).values())
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[0.0015, 0, 0], [-0.0015, 0, 0]]
    case["workspace_bytes"] = 4096 * 2 + 4096
    assert all(v["max"] <= TOLERANCE for v in metrics(evaluate(case), reference(case)).values())
