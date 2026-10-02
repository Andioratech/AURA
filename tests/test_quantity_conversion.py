"""Explicit conversion fixtures, separate from schema definitions and conversion tables."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from aura.errors import InvalidInputError, NumericalDomainError
from aura.schema import canonical_quantity, validate_document


@pytest.mark.parametrize(
    "value,unit,canonical,expected",
    [
        (1, "um", "m", 0.000001),
        (1, "mm", "m", 0.001),
        (1, "cm", "m", 0.01),
        (1, "mg", "kg", 0.000001),
        (1, "g", "kg", 0.001),
        (1, "us", "s", 0.000001),
        (1, "ms", "s", 0.001),
        (1, "kHz", "Hz", 1000),
        (1, "MHz", "Hz", 1000000),
        (1, "kPa", "Pa", 1000),
        (1, "MPa", "Pa", 1000000),
        (180, "deg", "rad", 3.141592653589793),
    ],
)
def test_independently_specified_unit_factors(value, unit, canonical, expected):
    result = canonical_quantity({"value": value, "unit": unit}, expected_unit=canonical)
    assert result["unit"] == canonical
    assert result["value"] == pytest.approx(expected, rel=1e-12, abs=1e-15)


@pytest.mark.parametrize(
    "unit",
    [
        "1",
        "m",
        "kg",
        "s",
        "Hz",
        "rad",
        "Pa",
        "m/s",
        "m/s^2",
        "rad/s",
        "kg/m^3",
        "Pa*s",
        "1/Pa",
        "K",
        "N",
        "N*m",
        "W",
        "W/m^2",
        "kg*m^2",
        "1/m",
    ],
)
def test_canonical_identity(unit):
    assert canonical_quantity({"value": 0.125, "unit": unit}, expected_unit=unit) == {
        "value": 0.125,
        "unit": unit,
    }


def test_vector_signs_zero_and_input_immutability():
    data = {"value": [-1, 0, 1], "unit": "mm"}
    before = deepcopy(data)
    result = canonical_quantity(data, expected_unit="m", size=3, path="/position")
    assert result == {"value": [-0.001, 0.0, 0.001], "unit": "m"}
    assert data == before
    result["value"][0] = 9
    assert data == before


@pytest.mark.parametrize(
    "value,unit,target,code",
    [
        (1, "unknown", "m", "UNIT_UNSUPPORTED"),
        (1, "µm", "m", "UNIT_UNSUPPORTED"),
        (1, "degC", "K", "UNIT_UNSUPPORTED"),
        (1, "dB", "Pa", "UNIT_UNSUPPORTED"),
        (1, "mm", "s", "UNIT_MISMATCH"),
        (1, "1", "rad", "UNIT_MISMATCH"),
        (1, "rad/s", "Hz", "UNIT_MISMATCH"),
        (1, "g", "m/s^2", "UNIT_MISMATCH"),
        (1, "m", "mm", "UNIT_UNSUPPORTED"),
        (1, None, "m", "UNIT_UNSUPPORTED"),
    ],
)
def test_unsupported_or_wrong_units(value, unit, target, code):
    with pytest.raises(InvalidInputError) as caught:
        canonical_quantity(
            {"value": value, "unit": unit}, expected_unit=target, path="/body/radius"
        )
    assert caught.value.code == code
    assert caught.value.path == "/body/radius/unit"


@pytest.mark.parametrize(
    "value,code",
    [
        (True, "NUMBER_TYPE"),
        ("1", "NUMBER_TYPE"),
        (None, "NUMBER_TYPE"),
        (float("inf"), "NONFINITE"),
        (float("nan"), "NONFINITE"),
    ],
)
def test_invalid_vector_component_identifies_its_position(value, code):
    with pytest.raises(InvalidInputError) as caught:
        canonical_quantity(
            {"value": [0, value, 0], "unit": "mm"}, expected_unit="m", size=3, path="/position"
        )
    assert caught.value.code == code
    assert caught.value.path == "/position/value/1"


@pytest.mark.parametrize(
    "data,size",
    [
        ({"value": [1, 2], "unit": "mm"}, 3),
        ({"value": 1, "unit": "mm"}, 3),
        ({"value": [1], "unit": "mm"}, True),
        ({"value": [], "unit": "mm"}, 0),
        ({"value": 1}, None),
        ({"value": 1, "unit": "mm", "extra": 0}, None),
        (None, None),
    ],
)
def test_wrong_shapes_and_incomplete_quantities(data, size):
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        canonical_quantity(data, expected_unit="m", size=size)


@pytest.mark.parametrize(
    "value,unit,target",
    [(5e-324, "mm", "m"), (1e308, "MHz", "Hz"), (-1e308, "MPa", "Pa"), (5e-324, "deg", "rad")],
)
def test_conversion_result_out_of_numeric_range(value, unit, target):
    with pytest.raises(NumericalDomainError) as caught:
        canonical_quantity({"value": value, "unit": unit}, expected_unit=target, path="/quantity")
    assert caught.value.code == "NUMERIC_RANGE"
    assert caught.value.path == "/quantity/value"


def test_large_degree_conversion_avoids_intermediate_overflow():
    result = canonical_quantity({"value": 1e308, "unit": "deg"}, expected_unit="rad")
    assert result["value"] == pytest.approx(1.7453292519943295e306, rel=1e-12, abs=0)


def test_explicit_adapter_then_strict_scenario_validation():
    path = Path(__file__).resolve().parents[1] / "examples/schema/manufactured-scenario.json"
    canonical = json.loads(path.read_text())
    alternate = deepcopy(canonical)
    alternate["bodies"][0]["geometry"]["radius"] = {"value": 0.01, "unit": "mm"}
    with pytest.raises(InvalidInputError, match="UNIT_MISMATCH"):
        validate_document(alternate)
    raw = deepcopy(alternate["bodies"][0]["geometry"]["radius"])
    alternate["bodies"][0]["geometry"]["radius"] = canonical_quantity(raw, expected_unit="m")
    validated = validate_document(alternate).to_dict()
    assert validated == canonical
    assert raw == {"value": 0.01, "unit": "mm"}
    assert validated["gravity"] == {"value": [0, 0, 0], "unit": "m/s^2"}


def test_conversion_alone_does_not_claim_physical_range_validity():
    converted = canonical_quantity({"value": -1, "unit": "mm"}, expected_unit="m")
    assert converted["value"] == -0.001
    path = Path(__file__).resolve().parents[1] / "examples/schema/manufactured-scenario.json"
    scenario = json.loads(path.read_text())
    scenario["bodies"][0]["geometry"]["radius"] = converted
    with pytest.raises(InvalidInputError, match="SCHEMA_INVALID"):
        validate_document(scenario)


def test_b01_11_missing_temperature_is_not_inferred():
    path = Path(__file__).resolve().parents[1] / "examples/schema/manufactured-scenario.json"
    scenario = json.loads(path.read_text())
    del scenario["medium"]["temperature"]
    with pytest.raises(InvalidInputError) as caught:
        validate_document(scenario)
    assert caught.value.code == "SCHEMA_INVALID"
    assert caught.value.path == "/medium/temperature"
