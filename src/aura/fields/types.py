"""FIELD-1.0 immutable samples and FIELD-ARRAY-1.0 component records.

These checks validate representation, not equations, provenance or model coverage.
"""

from __future__ import annotations

from dataclasses import dataclass

from aura.errors import InvalidInputError
from aura.units import _finite_scalar

MAX_SAMPLES = 256
ARRAY_CONTRACT = "FIELD-ARRAY-1.0"
_SPECS = {
    "coordinates": ("coordinates_m", "m", "float64", True),
    "pressure": ("pressure_pa", "Pa", "complex128", False),
    "velocity": ("velocity_m_s", "m/s", "complex128", True),
    "pressure_gradient": ("pressure_gradient_pa_m", "Pa/m", "complex128", True),
}
_KEYS = {
    "contract", "quantity", "frame", "frequency_hz", "unit", "shape", "dtype",
    "phasor_convention", "amplitude_convention", "values",
}


def _require(condition: bool, path: str, message: str) -> None:
    if not condition:
        raise InvalidInputError("FIELD_REPRESENTATION", path, message)


def _real(value: object, path: str) -> float:
    return _finite_scalar(path.removeprefix("/"), value)


def _complex(value: object, path: str) -> complex:
    if type(value) is complex:
        return complex(_real(value.real, path + "/real"), _real(value.imag, path + "/imag"))
    return complex(_real(value, path), 0.0)


def _sequence(value: object, size: int, path: str) -> list | tuple:
    _require(type(value) in (list, tuple), path, "Expected a list or tuple.")
    _require(len(value) == size, path, "Wrong number of components or samples.")
    return value


def _values(value: object, count: int, vector: bool, convert, path: str) -> tuple:
    rows = _sequence(value, count, path)
    if not vector:
        return tuple(convert(item, f"{path}/{i}") for i, item in enumerate(rows))
    return tuple(
        tuple(convert(item, f"{path}/{i}/{j}") for j, item in enumerate(
            _sequence(row, 3, f"{path}/{i}")
        ))
        for i, row in enumerate(rows)
    )


def _pair(value: object, path: str) -> complex:
    _require(type(value) is list, path, "Complex storage requires [real, imaginary].")
    pair = _sequence(value, 2, path)
    return complex(_real(pair[0], path + "/0"), _real(pair[1], path + "/1"))


@dataclass(frozen=True)
class FieldSamples:
    """Peak harmonic incident-field samples in the chamber frame and canonical SI.

    Frequency and all four arrays are required. Lists are copied into tuples;
    duplicate sample positions are retained. No model is executed by this type.
    """

    frequency_hz: float
    coordinates_m: tuple[tuple[float, float, float], ...]
    pressure_pa: tuple[complex, ...]
    velocity_m_s: tuple[tuple[complex, complex, complex], ...]
    pressure_gradient_pa_m: tuple[tuple[complex, complex, complex], ...]

    def __post_init__(self) -> None:
        frequency = _real(self.frequency_hz, "/frequency_hz")
        _require(frequency > 0, "/frequency_hz", "Frequency must be positive.")
        coordinates = self.coordinates_m
        _require(type(coordinates) in (list, tuple), "/coordinates_m", "Expected sample rows.")
        count = len(coordinates)
        _require(1 <= count <= MAX_SAMPLES, "/coordinates_m", "Expected 1 to 256 samples.")
        object.__setattr__(self, "frequency_hz", frequency)
        for attr, _, dtype, vector in _SPECS.values():
            snapshot = _values(
                getattr(self, attr), count, vector,
                _real if dtype == "float64" else _complex, "/" + attr,
            )
            object.__setattr__(self, attr, snapshot)

    def to_artifacts(self) -> dict[str, dict]:
        """Return independent JSON-compatible records; no files or hashes are created."""
        records = {}
        count = len(self.coordinates_m)
        for quantity, (attr, unit, dtype, vector) in _SPECS.items():
            def encode(value, dtype=dtype):
                return value if dtype == "float64" else [value.real, value.imag]

            data = getattr(self, attr)
            values = (
                [[encode(item) for item in row] for row in data]
                if vector else [encode(item) for item in data]
            )
            records[quantity] = {
                "contract": ARRAY_CONTRACT,
                "quantity": quantity,
                "frame": "chamber",
                "frequency_hz": self.frequency_hz,
                "unit": unit,
                "shape": [count, 3] if vector else [count],
                "dtype": dtype,
                "phasor_convention": "exp(-iwt)",
                "amplitude_convention": "peak",
                "values": values,
            }
        return records

    @classmethod
    def from_artifacts(cls, records: dict[str, dict]) -> FieldSamples:
        """Read the four parsed records after the caller's file/hash/parser checks."""
        _require(type(records) is dict, "", "Expected a component-record mapping.")
        _require(set(records) == set(_SPECS), "", "Require exactly four field components.")
        arguments = {}
        count = None
        frequency = None
        for quantity, (attr, unit, dtype, vector) in _SPECS.items():
            path = "/" + quantity
            record = records[quantity]
            _require(type(record) is dict, path, "Expected a component record.")
            _require(set(record) == _KEYS, path, "Missing or unknown component fields.")
            fixed = {
                "contract": ARRAY_CONTRACT, "quantity": quantity, "frame": "chamber",
                "unit": unit, "dtype": dtype, "phasor_convention": "exp(-iwt)",
                "amplitude_convention": "peak",
            }
            for key, expected in fixed.items():
                _require(record[key] == expected, path + "/" + key, "Unsupported metadata.")
            actual_frequency = _real(record["frequency_hz"], path + "/frequency_hz")
            _require(actual_frequency > 0, path + "/frequency_hz", "Frequency must be positive.")
            if frequency is None:
                frequency = actual_frequency
            _require(actual_frequency == frequency, path + "/frequency_hz", "Frequency mismatch.")
            shape = record["shape"]
            _require(
                type(shape) is list and len(shape) == (2 if vector else 1)
                and all(type(item) is int for item in shape),
                path + "/shape", "Expected integer logical dimensions.",
            )
            if count is None:
                count = shape[0]
            _require(1 <= count <= MAX_SAMPLES, path + "/shape", "Expected 1 to 256 samples.")
            _require(shape == ([count, 3] if vector else [count]), path + "/shape", "Shape mismatch.")
            arguments[attr] = _values(
                record["values"], count, vector,
                _real if dtype == "float64" else _pair, path + "/values",
            )
        return cls(frequency_hz=frequency, **arguments)
