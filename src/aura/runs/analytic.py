"""Versioned, bounded admission and serialization for analytic field runs."""

from __future__ import annotations

import resource

from aura.errors import InvalidInputError
from aura.fields import (
    FieldSamples,
    PlaneWave,
    evaluate_plane_wave,
    evaluate_plane_wave_pair,
)
from aura.schema import FieldResult, Scenario

from .manifest import decode, digest, encode, fail

DRIVER = "analytic-plane-field"
DRIVER_VERSION = "1.0"
RUN_POLICY = "ANALYTIC-RUN-1.0"
REQUEST_CONTRACT = "FIELD-REQUEST-1.0"
INDEX_CONTRACT = "FIELD-INDEX-1.0"
SCOPE = (
    "Analytical incident-field software verification only; no body coupling, force, "
    "motion, physical transducer, or experimental validation."
)
OUTPUT_NAMES = {
    "field-coordinates.json",
    "field-pressure.json",
    "field-velocity.json",
    "field-pressure-gradient.json",
    "field-result.json",
    "field-index.json",
}


def _invalid(code: str, path: str, message: str) -> None:
    raise InvalidInputError(code, path, message)


def parse_request(raw: bytes) -> dict:
    """Validate the closed request shape before any field-sized allocation."""
    request = decode(raw)
    expected = {"contract", "case_id", "box_min_m", "box_max_m", "coordinates_m"}
    if type(request) is not dict or set(request) != expected:
        _invalid("FIELD_REQUEST", "", "Expected exactly the FIELD-REQUEST-1.0 fields.")
    if request["contract"] != REQUEST_CONTRACT:
        _invalid("FIELD_REQUEST", "/contract", "Unsupported field request contract.")
    if type(request["case_id"]) is not str or not request["case_id"]:
        _invalid("FIELD_REQUEST", "/case_id", "Expected a nonempty frozen case ID.")
    for name in ("box_min_m", "box_max_m"):
        value = request[name]
        if type(value) is not list or len(value) != 3 or any(
            type(component) not in (int, float) for component in value
        ):
            _invalid("FIELD_REQUEST", "/" + name, "Expected three finite SI coordinates.")
    low, high = request["box_min_m"], request["box_max_m"]
    if any(not (lo < hi) for lo, hi in zip(low, high)):
        _invalid("FIELD_REQUEST", "/box_max_m", "Observation box must have positive extent.")
    points = request["coordinates_m"]
    if type(points) is not list or not 1 <= len(points) <= 256:
        _invalid("FIELD_REQUEST", "/coordinates_m", "Expected 1 to 256 ordered samples.")
    for index, point in enumerate(points):
        if type(point) is not list or len(point) != 3 or any(
            type(component) not in (int, float) for component in point
        ):
            _invalid("FIELD_REQUEST", f"/coordinates_m/{index}", "Expected a finite SI triple.")
        if any(not lo <= coordinate <= hi for coordinate, lo, hi in zip(point, low, high)):
            _invalid("FIELD_DOMAIN", f"/coordinates_m/{index}", "Sample lies outside the request box.")
    return request


def admit(scenario: Scenario, request: dict) -> tuple[list[PlaneWave], int]:
    """Bind a request to schema-1.0 plane-source inputs and check preconditions."""
    config = scenario.to_dict()
    medium = config["medium"]
    sources = config["sources"]
    solver = config["solver"]
    if solver["model_id"] != DRIVER or solver["model_version"] != DRIVER_VERSION:
        _invalid("RUN_MODEL", "/solver", "Analytical driver/version is not admitted.")
    count = len(sources["elements"])
    family = request["case_id"].split("-", 1)[0]
    expected_equations = {
        ("B03", 1): ["EQ-007"],
        ("B04", 2): ["EQ-008"],
        ("B05", 2): ["EQ-008"],
    }
    if solver["parameters"] or solver["precision"] != "complex128" or (
        expected_equations.get((family, count)) != solver["equation_ids"]
    ):
        _invalid("RUN_MODEL", "/solver", "Unsupported analytical solver parameters or precision.")
    if medium["dynamic_viscosity"]["value"] != 0 or medium["amplitude_attenuation"]["value"] != 0:
        _invalid("FIELD_MODEL", "/medium", "Only explicit zero-loss medium inputs are admitted.")
    if sources["amplitude_convention"] != "peak" or sources["phasor_convention"] != "exp(-iwt)":
        _invalid("FIELD_MODEL", "/sources", "Source conventions do not match FIELD-1.0.")
    frequency = sources["frequency"]["value"]
    origin = config["domain"]["origin"]["value"]
    size = config["domain"]["size"]["value"]
    expected_low, expected_high = request["box_min_m"], request["box_max_m"]
    if origin != expected_low or [a + b for a, b in zip(origin, size)] != expected_high:
        _invalid("FIELD_DOMAIN", "/domain", "Request box must equal the declared scenario box.")
    waves = []
    elements = sources["elements"]
    if not 1 <= len(elements) <= 2:
        _invalid("FIELD_MODEL", "/sources/elements", "Admit one or two ideal plane waves.")
    for index, element in enumerate(elements):
        path = f"/sources/elements/{index}"
        if element["model"] != "ideal_plane_wave":
            _invalid("FIELD_MODEL", path + "/model", "Only explicit ideal plane waves are admitted.")
        amplitude = element["pressure_amplitude"]["value"]
        if amplitude > element["pressure_limit"]["value"]:
            _invalid("FIELD_MODEL", path + "/pressure_amplitude", "Source exceeds its declared limit.")
        waves.append(PlaneWave(
            density_kg_m3=medium["density"]["value"],
            sound_speed_m_s=medium["sound_speed"]["value"],
            frequency_hz=frequency,
            peak_pressure_pa=amplitude,
            direction=tuple(element["normal"]["value"]),
            reference_m=tuple(element["position"]["value"]),
            phase_rad=element["phase"]["value"],
            dynamic_viscosity_pa_s=medium["dynamic_viscosity"]["value"],
            amplitude_attenuation_per_m=medium["amplitude_attenuation"]["value"],
        ))
    workspace = 4096 * len(request["coordinates_m"]) + 4096 * len(waves)
    resources = config["resources"]
    if resources["wall_time"]["value"] > 30 or resources["disk_bytes"] > 16 * 1024**2:
        _invalid("RUN_RESOURCE", "/resources", "Analytical run exceeds the frozen time or bundle cap.")
    if resources["ram_bytes"] < workspace:
        _invalid("RUN_RESOURCE", "/resources/ram_bytes", "RAM cap is below the preflight workspace.")
    return waves, workspace


def preflight(scenario: Scenario, request: dict) -> dict:
    waves, workspace = admit(scenario, request)
    count = len(request["coordinates_m"])
    # Include the already-imported recorder/runtime footprint with 2x headroom.
    baseline_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    ram_estimate = 2 * baseline_rss + workspace
    return {
        "ram_bytes": max(ram_estimate, 4096 * count + 4096 * len(waves)),
        "disk_bytes": 16 * 1024**2,
        "wall_time_s": 30.0,
        "cpu_workers": 1,
        "gpu": False,
        "field_samples": count,
        "source_count": len(waves),
        "workspace_bytes": workspace,
        "basis": "FIELD-1.0 bounded analytic point evaluation; conservative contract estimate, not a measured solver cost.",
    }


def check_preflight(record: dict, scenario: Scenario, request: dict) -> None:
    """Check the frozen workload estimate's policy fields, not host memory again."""
    waves, workspace = admit(scenario, request)
    expected = {
        "disk_bytes": 16 * 1024**2,
        "wall_time_s": 30.0,
        "cpu_workers": 1,
        "gpu": False,
        "field_samples": len(request["coordinates_m"]),
        "source_count": len(waves),
        "workspace_bytes": workspace,
        "basis": "FIELD-1.0 bounded analytic point evaluation; conservative contract estimate, not a measured solver cost.",
    }
    if type(record) is not dict or set(record) != set(expected) | {"ram_bytes"} or any(
        record.get(key) != value for key, value in expected.items()
    ):
        fail("RUN_PREFLIGHT", "Stored analytical preflight differs from the frozen workload policy.")
    config = scenario.to_dict()
    if type(record.get("ram_bytes")) is not int or record["ram_bytes"] < workspace or (
        record["ram_bytes"] > config["resources"]["ram_bytes"]
    ) or record["disk_bytes"] > config["resources"]["disk_bytes"] or (
        record["wall_time_s"] > config["resources"]["wall_time"]["value"]
    ):
        fail("RUN_PREFLIGHT", "Stored analytical estimate exceeds declared resource caps.")


def execute_field(scenario: Scenario, request: dict, run_id: str, emit) -> None:
    waves, workspace = admit(scenario, request)
    cfg = scenario.to_dict()
    kwargs = {
        "coordinates_m": request["coordinates_m"],
        "box_min_m": request["box_min_m"],
        "box_max_m": request["box_max_m"],
        "workspace_bytes": workspace,
    }
    samples = evaluate_plane_wave(waves[0], **kwargs) if len(waves) == 1 else evaluate_plane_wave_pair(
        waves[0], waves[1], **kwargs
    )
    artifacts = samples.to_artifacts()
    refs = {}
    filenames = {
        "coordinates": "field-coordinates.json",
        "pressure": "field-pressure.json",
        "velocity": "field-velocity.json",
        "pressure_gradient": "field-pressure-gradient.json",
    }
    for quantity, filename in filenames.items():
        refs[quantity] = emit(filename, artifacts[quantity])
    field_result = FieldResult({
        "document_type": "field_result",
        "schema_version": "1.0",
        "id": run_id + "-FIELD",
        "run_id": run_id,
        "frame": "chamber",
        "model_id": DRIVER,
        "model_version": DRIVER_VERSION,
        "regime": ["ideal-plane-wave", "homogeneous", "linear", "stationary", "lossless", "uncoupled"],
        "coordinates": {"artifact": {"uri": refs["coordinates"]["uri"], "sha256": refs["coordinates"]["sha256"]}, "unit": "m", "shape": [len(samples.coordinates_m), 3], "dtype": "float64"},
        "pressure": {"artifact": {"uri": refs["pressure"]["uri"], "sha256": refs["pressure"]["sha256"]}, "unit": "Pa", "shape": [len(samples.coordinates_m)], "dtype": "complex128"},
        "velocity": {"artifact": {"uri": refs["velocity"]["uri"], "sha256": refs["velocity"]["sha256"]}, "unit": "m/s", "shape": [len(samples.coordinates_m), 3], "dtype": "complex128"},
        "phasor_convention": "exp(-iwt)",
        "amplitude_convention": "peak",
        "diagnostics": ["Incident field only; Scenario bodies are recorded context and are not coupled."],
        "provenance": cfg["provenance"],
    })
    field_ref = emit("field-result.json", field_result.to_dict())
    index = {
        "contract": INDEX_CONTRACT,
        "run_policy": RUN_POLICY,
        "run_id": run_id,
        "field_result_id": field_result.to_dict()["id"],
        "field_result_sha256": field_ref["sha256"],
        "case_id": request["case_id"],
        "frequency_hz": samples.frequency_hz,
        "pressure_gradient": {
            "artifact": {"uri": refs["pressure_gradient"]["uri"], "sha256": refs["pressure_gradient"]["sha256"]},
            "unit": "Pa/m", "shape": [len(samples.coordinates_m), 3], "dtype": "complex128",
        },
        "scope": SCOPE,
    }
    emit("field-index.json", index)


def check_field_outputs(run_id: str, config: dict, request: dict, refs: list[dict], content: dict) -> None:
    """Cross-check field records and FIELD-INDEX without recalculating the model."""
    actual = {ref["uri"] for ref in refs}
    if actual != OUTPUT_NAMES:
        fail("FIELD_OUTPUTS", "Analytical run has a missing or unexpected output artifact.")
    records = {}
    for quantity, filename in {
        "coordinates": "field-coordinates.json",
        "pressure": "field-pressure.json",
        "velocity": "field-velocity.json",
        "pressure_gradient": "field-pressure-gradient.json",
    }.items():
        records[quantity] = content[filename]
    try:
        samples = FieldSamples.from_artifacts(records)
    except InvalidInputError as exc:
        fail("FIELD_ARTIFACT", f"Stored field component is structurally invalid: {exc.code}.")
    if samples.coordinates_m != tuple(tuple(row) for row in request["coordinates_m"]):
        fail("FIELD_SAMPLES", "Stored sample ordering or coordinates differ from the request.")
    expected_frequency = config["sources"]["frequency"]["value"]
    if samples.frequency_hz != expected_frequency:
        fail("FIELD_FREQUENCY", "Field frequency differs from the Scenario.")
    by_name = {ref["uri"]: ref for ref in refs}
    try:
        result = FieldResult(content["field-result.json"])
    except InvalidInputError as exc:
        fail("FIELD_RESULT", f"Stored FieldResult is structurally invalid: {exc.code}.")
    result_data = result.to_dict()
    if result_data["run_id"] != run_id or result_data["id"] != run_id + "-FIELD":
        fail("FIELD_RESULT_ID", "FieldResult does not identify this run.")
    if result_data["model_id"] != DRIVER or result_data["model_version"] != DRIVER_VERSION or (
        result_data["frame"] != "chamber"
        or result_data["phasor_convention"] != "exp(-iwt)"
        or result_data["amplitude_convention"] != "peak"
    ):
        fail("FIELD_RESULT", "FieldResult model or convention differs from the admitted driver.")
    admit(Scenario(config), request)
    index = content["field-index.json"]
    if type(index) is not dict or set(index) != {
        "contract", "run_policy", "run_id", "field_result_id", "field_result_sha256", "case_id",
        "frequency_hz", "pressure_gradient", "scope",
    }:
        fail("FIELD_INDEX", "FIELD-INDEX-1.0 has missing or unexpected fields.")
    field_result_ref = by_name["field-result.json"]
    if index["contract"] != INDEX_CONTRACT or index["run_policy"] != RUN_POLICY or (
        index["run_id"] != run_id
    ) or (
        index["field_result_id"] != result_data["id"]
    ) or index["field_result_sha256"] != field_result_ref["sha256"] or (
        index["field_result_sha256"] != digest(encode(result_data))
    ):
        fail("FIELD_INDEX", "FIELD-INDEX identity or FieldResult digest differs.")
    gradient = index["pressure_gradient"]
    gref = by_name.get("field-pressure-gradient.json")
    if gradient != {
        "artifact": {"uri": gref["uri"], "sha256": gref["sha256"]},
        "unit": "Pa/m", "shape": [len(samples.coordinates_m), 3], "dtype": "complex128",
    }:
        fail("FIELD_INDEX", "Gradient reference differs from stored component bytes.")
    if index["case_id"] != request["case_id"] or index["frequency_hz"] != expected_frequency or (
        index["scope"] != SCOPE
    ):
        fail("FIELD_INDEX", "FIELD-INDEX request identity or frequency differs.")
    for key, quantity, filename in (
        ("coordinates", "coordinates", "field-coordinates.json"),
        ("pressure", "pressure", "field-pressure.json"),
        ("velocity", "velocity", "field-velocity.json"),
    ):
        descriptor = result_data[key]
        reference = by_name.get(filename)
        expected = {
            "artifact": {"uri": reference["uri"], "sha256": reference["sha256"]},
            "unit": records[quantity]["unit"], "shape": records[quantity]["shape"],
            "dtype": records[quantity]["dtype"],
        }
        if descriptor != expected:
            fail("FIELD_RESULT", f"FieldResult {key} reference differs from component bytes.")
