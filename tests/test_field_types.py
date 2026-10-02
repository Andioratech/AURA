"""FIELD-1.0 representation checks; no acoustic solver is exercised here."""

import copy
import json
import sys
from dataclasses import FrozenInstanceError

import pytest

from aura.errors import InvalidInputError
from aura.fields import FieldSamples
from aura.fields.types import MAX_SAMPLES
from aura.schema import validate_document


def inputs():
    # Deliberately arbitrary component values: representation is not a physics audit.
    return {
        "frequency_hz": 1_000_000,
        "coordinates_m": [[0, 0, 0], [0.000375, 0, 0]],
        "pressure_pa": [2, 0],
        "velocity_m_s": [[0, 0, 0], [2j, 0, 0]],
        "pressure_gradient_pa_m": [[0, 0, 0], [-2, 0, 0]],
    }


def test_explicit_json_round_trip_preserves_zero_pressure_nonzero_velocity():
    field = FieldSamples(**inputs())
    records = field.to_artifacts()
    assert records["pressure"]["values"] == [[2.0, 0.0], [0.0, 0.0]]
    assert records["velocity"]["values"][1] == [[0.0, 2.0], [0.0, 0.0], [0.0, 0.0]]
    assert records["pressure_gradient"]["unit"] == "Pa/m"
    assert records["velocity"]["shape"] == [2, 3]
    assert records["coordinates"]["values"][1] == [0.000375, 0, 0]
    assert FieldSamples.from_artifacts(json.loads(json.dumps(records, allow_nan=False))) == field


def test_no_aliasing_in_constructor_or_export():
    data = inputs()
    field = FieldSamples(**data)
    data["coordinates_m"][0][0] = 99
    data["velocity_m_s"][1][0] = 99
    exported = field.to_artifacts()
    exported["pressure"]["values"][0][0] = 99
    exported["coordinates"]["shape"][0] = 99
    assert field.coordinates_m[0][0] == 0
    assert field.velocity_m_s[1][0] == 2j
    assert field.pressure_pa[0] == 2
    with pytest.raises(FrozenInstanceError):
        field.frequency_hz = 1


def test_duplicate_points_order_and_complex_components_are_retained():
    data = inputs()
    data["coordinates_m"] = [[1, 2, 3], [1, 2, 3]]
    data["pressure_pa"] = [-2 + 3j, -4 - 5j]
    data["velocity_m_s"] = [[1j, -2j, 3j], [-4j, 5j, -6j]]
    field = FieldSamples(**data)
    assert field.coordinates_m == ((1, 2, 3), (1, 2, 3))
    assert field.pressure_pa == (-2 + 3j, -4 - 5j)
    assert FieldSamples.from_artifacts(field.to_artifacts()) == field


@pytest.mark.parametrize("value", [True, "1", None, 0, -1, float("inf"), float("nan"), 1j])
def test_invalid_frequency(value):
    data = inputs()
    data["frequency_hz"] = value
    with pytest.raises(InvalidInputError) as caught:
        FieldSamples(**data)
    assert caught.value.path == "/frequency_hz"


@pytest.mark.parametrize("key", list(inputs())[1:])
@pytest.mark.parametrize("value", [None, [], [0], "data", {"x": 1}])
def test_missing_or_ragged_arrays(key, value):
    data = inputs()
    data[key] = value
    with pytest.raises(InvalidInputError):
        FieldSamples(**data)


@pytest.mark.parametrize("key", list(inputs())[1:])
@pytest.mark.parametrize("bad", [True, "1", float("nan"), float("inf"), 10**400])
def test_invalid_scalar_components(key, bad):
    data = inputs()
    if key == "pressure_pa":
        data[key][0] = bad
    else:
        data[key][0][0] = bad
    with pytest.raises(InvalidInputError):
        FieldSamples(**data)


@pytest.mark.parametrize("bad", [complex(float("nan"), 0), complex(0, float("inf"))])
def test_nonfinite_complex_components(bad):
    data = inputs()
    data["pressure_pa"][0] = bad
    with pytest.raises(InvalidInputError):
        FieldSamples(**data)


def test_coordinates_cannot_be_complex_and_vectors_need_three_components():
    data = inputs()
    data["coordinates_m"][0][0] = 1 + 0j
    with pytest.raises(InvalidInputError):
        FieldSamples(**data)
    for key in ("coordinates_m", "velocity_m_s", "pressure_gradient_pa_m"):
        data = inputs()
        data[key][0] = [0, 0]
        with pytest.raises(InvalidInputError):
            FieldSamples(**data)


def test_sample_limit_and_serialization_budget():
    for count in (1, MAX_SAMPLES, MAX_SAMPLES + 1):
        data = inputs()
        for key in list(data)[1:]:
            data[key] = [copy.deepcopy(data[key][0]) for _ in range(count)]
        if count > MAX_SAMPLES:
            with pytest.raises(InvalidInputError):
                FieldSamples(**data)
        else:
            field = FieldSamples(**data)
            assert FieldSamples.from_artifacts(field.to_artifacts()) == field
            assert len(json.dumps(field.to_artifacts()).encode()) < 32768 + 1024 * count


@pytest.mark.parametrize("quantity", ["coordinates", "pressure", "velocity", "pressure_gradient"])
@pytest.mark.parametrize("key,bad", [
    ("contract", "FIELD-ARRAY-2.0"), ("quantity", "unknown"), ("frame", "body"),
    ("frequency_hz", 2), ("unit", "mm"), ("dtype", "float32"),
    ("phasor_convention", "exp(+iwt)"), ("amplitude_convention", "rms"),
    ("shape", [2.0, 3]), ("shape", [True, 3]), ("shape", [2, 3, 2]),
    ("values", None), ("values", []),
])
def test_wrong_artifact_metadata_or_shape(quantity, key, bad):
    records = FieldSamples(**inputs()).to_artifacts()
    records[quantity][key] = bad
    with pytest.raises(InvalidInputError):
        FieldSamples.from_artifacts(records)


@pytest.mark.parametrize("bad", [1, "1+2j", [1], [1, 2, 3], [True, 0], [0, float("nan")]])
def test_complex_artifact_storage_requires_finite_numeric_pair(bad):
    records = FieldSamples(**inputs()).to_artifacts()
    records["pressure"]["values"][0] = bad
    with pytest.raises(InvalidInputError):
        FieldSamples.from_artifacts(records)


def test_artifact_missing_unknown_fields_and_components():
    original = FieldSamples(**inputs()).to_artifacts()
    for quantity in original:
        records = copy.deepcopy(original)
        del records[quantity]
        with pytest.raises(InvalidInputError):
            FieldSamples.from_artifacts(records)
    for key in original["pressure"]:
        records = copy.deepcopy(original)
        del records["pressure"][key]
        with pytest.raises(InvalidInputError):
            FieldSamples.from_artifacts(records)
    for records in (None, [], {**original, "force": {}},
                    {**original, "pressure": {**original["pressure"], "extra": 1}}):
        with pytest.raises(InvalidInputError):
            FieldSamples.from_artifacts(records)


@pytest.mark.parametrize("shape", [[0, 3], [-1, 3], [257, 3], [2, 2], [], None])
def test_invalid_coordinate_artifact_shape(shape):
    records = FieldSamples(**inputs()).to_artifacts()
    records["coordinates"]["shape"] = shape
    with pytest.raises(InvalidInputError):
        FieldSamples.from_artifacts(records)


def test_import_snapshots_artifact_data_and_is_not_schema_one_field_result():
    records = FieldSamples(**inputs()).to_artifacts()
    field = FieldSamples.from_artifacts(records)
    records["pressure"]["values"][0][0] = 99
    assert field.pressure_pa[0] == 2
    with pytest.raises(InvalidInputError):
        validate_document(records["pressure"])


def test_worst_length_finite_components_fit_initial_encoding_budget():
    data = inputs()
    large = -sys.float_info.max
    data["coordinates_m"] = [[large, large, large] for _ in range(MAX_SAMPLES)]
    data["pressure_pa"] = [complex(large, large)] * MAX_SAMPLES
    for key in ("velocity_m_s", "pressure_gradient_pa_m"):
        data[key] = [[complex(large, large)] * 3 for _ in range(MAX_SAMPLES)]
    field = FieldSamples(**data)
    encoded = json.dumps(field.to_artifacts(), allow_nan=False).encode()
    assert len(encoded) < 32768 + 1024 * MAX_SAMPLES
    assert FieldSamples.from_artifacts(json.loads(encoded)) == field
