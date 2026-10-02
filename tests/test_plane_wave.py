"""B-03 numerical verification and rejection; no physical run admission."""

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
from plane_wave_reference import pairs_as_complex, pi, reference, sin_cos

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields import FieldSamples, PlaneWave, evaluate_plane_wave, mean_intensity_w_m2
from aura.units import plane_progressive_wave_intensity_w_m2, sinusoid_peak_to_rms

FIXTURE = Path(__file__).parent / "fixtures" / "fields" / "B03-plane-wave.json"
DATA = json.loads(FIXTURE.read_text())
CASES = DATA["cases"]
TOLERANCE = 2048 * sys.float_info.epsilon


def evaluate(case):
    return evaluate_plane_wave(
        PlaneWave(**case["wave"]),
        case["coordinates_m"],
        box_min_m=case["box_min_m"],
        box_max_m=case["box_max_m"],
        workspace_bytes=case["workspace_bytes"],
    )


def metrics(field, expected):
    actual = {
        "pressure": field.pressure_pa,
        "velocity": field.velocity_m_s,
        "pressure_gradient": field.pressure_gradient_pa_m,
        "intensity": mean_intensity_w_m2(field),
    }
    result = {}
    for name, values in actual.items():
        scale = float(expected["scales"][name])
        if name == "intensity":
            got = [x for row in values for x in row]
            want = [float(x) for row in expected[name] for x in row]
        elif name == "pressure":
            got = values
            want = pairs_as_complex(expected[name])
        else:
            got = [x for row in values for x in row]
            want = pairs_as_complex([x for row in expected[name] for x in row])
        errors = [abs(a - b) / scale for a, b in zip(got, want, strict=True)]
        result[name] = {
            "scale_si": scale,
            "errors": errors,
            "max": max(errors),
            "rms": math.sqrt(sum(e * e for e in errors) / len(errors)),
        }
    return result


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_independent_decimal_field_comparison(case, record_property):
    field = evaluate(case)
    observed = metrics(field, reference(case, 60))
    record_property("case_id", case["id"])
    record_property("normalized_tolerance", TOLERANCE)
    record_property("field_error_metrics", json.dumps(observed, sort_keys=True))
    assert DATA["normalized_tolerance"] == TOLERANCE
    assert all(values["max"] <= TOLERANCE for values in observed.values()), observed
    assert FieldSamples.from_artifacts(field.to_artifacts()) == field


def flatten(value):
    if isinstance(value, dict):
        return [item for child in value.values() for item in flatten(child)]
    if isinstance(value, (list, tuple)):
        return [item for child in value for item in flatten(child)]
    return [value]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_reference_precision_stability(case):
    first, second = reference(case, 60), reference(case, 80)
    with localcontext() as context:
        context.prec = 90
        for name in ("pressure", "velocity", "pressure_gradient", "intensity"):
            scale = second["scales"][name]
            for a, b in zip(flatten(first[name]), flatten(second[name]), strict=True):
                assert abs(a - b) / scale < Decimal("1e-45")


def test_oracle_exact_known_values_and_bounded_pi():
    with localcontext() as context:
        context.prec = 90
        value = pi(80)
        assert Decimal("3.14159265358979323846264338327950288419716939937510") < value
        assert value < Decimal("3.14159265358979323846264338327950288419716939937511")
        for angle, s, c in ((Decimal(0), 0, 1), (value / 2, 1, 0), (value, 0, -1)):
            sine, cosine = sin_cos(angle, 80)
            assert abs(sine - s) < Decimal("1e-75")
            assert abs(cosine - c) < Decimal("1e-75")


@pytest.mark.parametrize("case_id", list(DATA["hand_normalized"]))
def test_literal_quarter_turn_answers(case_id):
    case = next(case for case in CASES if case["id"] == case_id)
    field = evaluate(case)
    expected = DATA["hand_normalized"][case_id]
    scales = reference(case)["scales"]
    arrays = {
        "pressure": field.pressure_pa,
        "velocity": field.velocity_m_s,
        "pressure_gradient": field.pressure_gradient_pa_m,
    }
    for name, values in arrays.items():
        got = list(values) if name == "pressure" else [x for row in values for x in row]
        want = expected[name] if name == "pressure" else [x for row in expected[name] for x in row]
        assert (
            max(
                abs(a / float(scales[name]) - b)
                for a, b in zip(got, pairs_as_complex(want), strict=True)
            )
            <= TOLERANCE
        )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_actual_backend_arguments_against_decimal(case, monkeypatch, record_property):
    observed = []
    original_sin, original_cos = math.sin, math.cos

    def checked(name, function):
        def call(angle):
            result = function(angle)
            sine, cosine = sin_cos(Decimal.from_float(angle), 80)
            expected = sine if name == "sin" else cosine
            error = abs(Decimal.from_float(result) - expected)
            observed.append(float(error))
            return result

        return call

    monkeypatch.setattr(math, "sin", checked("sin", original_sin))
    monkeypatch.setattr(math, "cos", checked("cos", original_cos))
    evaluate(case)
    assert len(observed) == 2 * len(case["coordinates_m"])
    record_property("backend_absolute_error_max", max(observed))
    assert max(observed) <= 4 * sys.float_info.epsilon


def test_rotation_translation_and_time_sign():
    outputs = {case["id"]: evaluate(case) for case in CASES}
    axial, rotated = outputs["B03-AXIAL"], outputs["B03-ROTATED"]
    assert axial.pressure_pa == rotated.pressure_pa
    assert rotated.velocity_m_s == tuple((v[1], v[2], v[0]) for v in axial.velocity_m_s)
    assert rotated.pressure_gradient_pa_m == tuple(
        (g[1], g[2], g[0]) for g in axial.pressure_gradient_pa_m
    )
    translated = outputs["B03-TRANSLATED"]
    for a, b in zip(translated.pressure_pa, axial.pressure_pa[:4], strict=True):
        assert abs(a - b) / 2 <= TOLERANCE
    oblique, oblique_rotated = outputs["B03-OBLIQUE"], outputs["B03-OBLIQUE-ROTATED"]
    assert oblique.pressure_pa == oblique_rotated.pressure_pa
    assert oblique_rotated.velocity_m_s == tuple((v[1], v[2], v[0]) for v in oblique.velocity_m_s)
    pressure = outputs["B03-PHASE"].pressure_pa[0]
    # Re(p exp(-i omega t)) = Re(p) cos(omega t) + Im(p) sin(omega t).
    for turn, expected in zip((0, 0.25, 0.5, 0.75), (0, 1, 0, -1), strict=True):
        value = pressure.real * math.cos(2 * math.pi * turn) + pressure.imag * math.sin(
            2 * math.pi * turn
        )
        assert abs(value / 2 - expected) <= TOLERANCE


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_euler_impedance_and_independent_intensity_helper(case):
    field = evaluate(case)
    rho, speed = 1000, 1500
    omega = 2 * math.pi * 1_000_000
    direction = case["wave"]["direction"]
    scale = reference(case)["scales"]
    flux = plane_progressive_wave_intensity_w_m2(
        sinusoid_peak_to_rms(case["wave"]["peak_pressure_pa"]), rho, speed
    )
    for pressure, velocity, gradient, intensity in zip(
        field.pressure_pa,
        field.velocity_m_s,
        field.pressure_gradient_pa_m,
        mean_intensity_w_m2(field),
        strict=True,
    ):
        for n, v, g, intensity_component in zip(
            direction, velocity, gradient, intensity, strict=True
        ):
            assert abs(g - 1j * omega * rho * v) / float(scale["pressure_gradient"]) <= TOLERANCE
            assert abs(rho * speed * v - n * pressure) / float(scale["pressure"]) <= TOLERANCE
            assert abs(intensity_component - n * flux) / float(scale["intensity"]) <= TOLERANCE


@pytest.mark.parametrize("corruption", ["spatial_sign", "rms", "velocity_sign", "missing_gradient"])
def test_known_wrong_results_fail_frozen_budget(corruption):
    field = evaluate(CASES[0])
    if corruption == "spatial_sign":
        field = replace(field, pressure_pa=[p.conjugate() for p in field.pressure_pa])
    elif corruption == "rms":
        field = replace(field, pressure_pa=[p / math.sqrt(2) for p in field.pressure_pa])
    elif corruption == "velocity_sign":
        field = replace(field, velocity_m_s=[[-v for v in row] for row in field.velocity_m_s])
    else:
        field = replace(field, pressure_gradient_pa_m=[[0, 0, 0]] * len(field.pressure_pa))
    observed = metrics(field, reference(CASES[0]))
    assert any(item["max"] > TOLERANCE for item in observed.values())


def test_specification_and_output_do_not_alias_caller_inputs():
    case = copy.deepcopy(CASES[0])
    spec = PlaneWave(**case["wave"])
    case["wave"]["direction"][0] = -1
    case["wave"]["reference_m"][0] = 99
    assert spec.direction == (1, 0, 0) and spec.reference_m == (0, 0, 0)
    with pytest.raises(FrozenInstanceError):
        spec.phase_rad = 1
    field = evaluate(CASES[0])
    assert field.coordinates_m == tuple(tuple(row) for row in CASES[0]["coordinates_m"])
    assert field.frequency_hz == 1_000_000


@pytest.mark.parametrize(
    "key",
    [
        "density_kg_m3",
        "sound_speed_m_s",
        "frequency_hz",
        "peak_pressure_pa",
        "phase_rad",
        "dynamic_viscosity_pa_s",
        "amplitude_attenuation_per_m",
    ],
)
@pytest.mark.parametrize("bad", [True, "1", None, float("nan"), float("inf"), 10**400])
def test_invalid_specification_scalars(key, bad):
    data = copy.deepcopy(CASES[0]["wave"])
    data[key] = bad
    with pytest.raises(InvalidInputError):
        PlaneWave(**data)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("density_kg_m3", 0),
        ("sound_speed_m_s", -1),
        ("frequency_hz", 0),
        ("peak_pressure_pa", -1),
        ("dynamic_viscosity_pa_s", 0.001),
        ("amplitude_attenuation_per_m", 0.1),
        ("direction", [0, 0, 0]),
        ("direction", [2, 0, 0]),
        ("direction", [1 + 1e-12, 0, 0]),
        ("direction", [True, 0, 0]),
        ("direction", [1, 0]),
        ("reference_m", None),
        ("reference_m", [0, 1j, 0]),
        ("reference_m", [0, float("inf"), 0]),
    ],
)
def test_model_range_and_direction_rejections(key, bad):
    with pytest.raises(InvalidInputError):
        PlaneWave(**{**CASES[0]["wave"], key: bad})


@pytest.mark.parametrize(
    "key,bad",
    [
        ("coordinates_m", []),
        ("coordinates_m", [[0, 0, 0]] * 257),
        ("coordinates_m", [[0, 0, 0], [0.002, 0, 0]]),
        ("coordinates_m", [[0, 0, 0], [float("nan"), 0, 0]]),
        ("coordinates_m", [[0, 0, 0], [True, 0, 0]]),
        ("coordinates_m", [[0, 0]]),
        ("coordinates_m", None),
        ("box_min_m", [0.0015, 0, 0]),
        ("box_max_m", [-0.0015, 0, 0]),
        ("box_min_m", [0, 0]),
        ("box_max_m", [float("inf"), 1, 1]),
        ("workspace_bytes", 0),
        ("workspace_bytes", True),
        ("workspace_bytes", 2.0),
    ],
)
def test_reject_before_trig_or_field_allocation(key, bad, monkeypatch):
    import aura.fields.analytic as implementation

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid input reached trig or field allocation")

    case = copy.deepcopy(CASES[0])
    case[key] = bad
    monkeypatch.setattr(math, "sin", forbidden)
    monkeypatch.setattr(math, "cos", forbidden)
    monkeypatch.setattr(implementation, "FieldSamples", forbidden)
    with pytest.raises(InvalidInputError):
        evaluate(case)


def test_phase_conditioning_and_unsupported_specification():
    case = copy.deepcopy(CASES[0])
    case["wave"]["phase_rad"] = 5 * math.pi
    with pytest.raises(NumericalDomainError, match="FIELD_PHASE_RANGE"):
        evaluate(case)
    case["wave"]["phase_rad"] = 0
    case["wave"]["reference_m"] = [1e10, 0, 0]
    case["coordinates_m"] = [[1e10, 0, 0]]
    case["box_min_m"], case["box_max_m"] = [1e10 - 1, -1, -1], [1e10 + 1, 1, 1]
    with pytest.raises(NumericalDomainError, match="FIELD_PHASE_RANGE"):
        evaluate(case)
    with pytest.raises(InvalidInputError, match="FIELD_SPEC"):
        evaluate_plane_wave(
            None, [[0, 0, 0]], box_min_m=[-1] * 3, box_max_m=[1] * 3, workspace_bytes=8192
        )
    with pytest.raises(InvalidInputError, match="FIELD_SPEC"):
        mean_intensity_w_m2(None)


def test_zero_drive_duplicates_and_maximum_workload():
    field = evaluate(next(case for case in CASES if case["id"] == "B03-ZERO"))
    assert all(
        value == 0
        for value in flatten(
            [
                field.pressure_pa,
                field.velocity_m_s,
                field.pressure_gradient_pa_m,
                mean_intensity_w_m2(field),
            ]
        )
    )
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[0, 0, 0]] * 256
    field = evaluate(case)
    assert field.pressure_pa == (2 + 0j,) * 256
    assert len(json.dumps(field.to_artifacts()).encode()) < 32768 + 1024 * 256


def test_arithmetic_range_errors_are_not_plausible_field_results():
    case = copy.deepcopy(CASES[0])
    case["wave"]["frequency_hz"] = sys.float_info.max
    case["wave"]["sound_speed_m_s"] = sys.float_info.min
    with pytest.raises(NumericalDomainError):
        evaluate(case)
    case = copy.deepcopy(CASES[0])
    case["wave"]["peak_pressure_pa"] = 5e-324
    case["coordinates_m"] = [[0, 0, 0]]
    with pytest.raises(NumericalDomainError):
        evaluate(case)
    field = FieldSamples(
        frequency_hz=1,
        coordinates_m=[[0, 0, 0]],
        pressure_pa=[sys.float_info.max],
        velocity_m_s=[[sys.float_info.max, 0, 0]],
        pressure_gradient_pa_m=[[0, 0, 0]],
    )
    with pytest.raises(NumericalDomainError):
        mean_intensity_w_m2(field)


def test_incremental_workspace_and_serialization_measurement(record_property):
    case = copy.deepcopy(CASES[0])
    case["coordinates_m"] = [[0.000375, 0, 0]] * 256
    started = time.perf_counter()
    tracemalloc.start()
    try:
        field = evaluate(case)
        encoded = json.dumps(field.to_artifacts(), allow_nan=False).encode()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    elapsed = time.perf_counter() - started
    record_property("maximum_samples", 256)
    record_property("peak_traced_python_bytes", peak)
    record_property("encoded_component_bytes", len(encoded))
    record_property("evaluation_and_encoding_elapsed_s", elapsed)
    record_property(
        "whole_test_process_peak_rss_bytes",
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    )
    assert peak <= 4096 * 256 + 4096
    assert len(encoded) <= 32768 + 1024 * 256


def test_flux_uses_both_real_and_imaginary_vector_components():
    field = FieldSamples(
        frequency_hz=1,
        coordinates_m=[[0, 0, 0]],
        pressure_pa=[2 + 3j],
        velocity_m_s=[[5 + 7j, -11 + 13j, 17 - 19j]],
        pressure_gradient_pa_m=[[0, 0, 0]],
    )
    # Synthetic arithmetic reference, not an Euler-consistent physical field.
    assert mean_intensity_w_m2(field) == ((15.5, 8.5, -11.5),)
