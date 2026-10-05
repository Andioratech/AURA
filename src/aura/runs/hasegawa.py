"""RUN-1.1 adapter for the bounded stationary piston/sphere field diagnostic."""

from __future__ import annotations

import math

from aura.errors import IncompleteEvidenceError, InvalidInputError
from aura.preflight import estimate_air_series, require_ready
from aura.schema import FieldResult, Scenario

from .manifest import digest, encode, fail

DRIVER = "hasegawa-piston-sphere-field"
VERSION = "1.0"
RUN_POLICY = "HASEGAWA-FIELD-RUN-1.0"
REQUEST_CONTRACT = "HASEGAWA-FIELD-REQUEST-1.0"
INDEX_CONTRACT = "FIELD-INDEX-1.0"
OUTPUT_NAMES = {
    "field-coordinates.json", "field-pressure.json", "field-velocity.json",
    "field-pressure-gradient.json", "field-result.json", "field-index.json",
}
SCOPE = (
    "Numerical field software diagnostic for the declared homogeneous-air, coaxial, "
    "uniformly displaced baffled-piston and stationary sound-hard sphere model only; "
    "no measured-field, force, motion, or gravity-equivalence validation."
)


def is_driver(driver_id: str) -> bool:
    return driver_id == DRIVER


def _invalid(code: str, path: str, message: str) -> None:
    raise InvalidInputError(code, path, message)


def parse_request(raw: bytes) -> dict:
    from .manifest import decode

    request = decode(raw)
    expected = {
        "contract", "case_id", "gap_m", "coordinates_m", "max_order",
        "quadrature_order", "point_chunk_size",
    }
    if type(request) is not dict or set(request) != expected or request.get("contract") != REQUEST_CONTRACT:
        _invalid("HASEGAWA_REQUEST", "", "Expected the exact HASEGAWA-FIELD-REQUEST-1.0 fields.")
    if type(request["case_id"]) is not str or not request["case_id"]:
        _invalid("HASEGAWA_REQUEST", "/case_id", "A frozen case ID is required.")
    gap = request["gap_m"]
    if type(gap) not in (int, float) or type(gap) is bool or not math.isfinite(gap) or gap <= 0:
        _invalid("HASEGAWA_REQUEST", "/gap_m", "Gap must be a finite positive SI distance.")
    points = request["coordinates_m"]
    if type(points) is not list or not 1 <= len(points) <= 256:
        _invalid("HASEGAWA_REQUEST", "/coordinates_m", "Expected 1 to 256 ordered samples.")
    for index, row in enumerate(points):
        if type(row) is not list or len(row) != 3 or any(
            type(value) not in (int, float) or type(value) is bool or not math.isfinite(value)
            for value in row
        ):
            _invalid("HASEGAWA_REQUEST", f"/coordinates_m/{index}", "Expected a finite SI coordinate triple.")
    order = request["max_order"]
    if type(order) is not int or not 0 <= order <= 512:
        _invalid("HASEGAWA_REQUEST", "/max_order", "Harmonic order must be explicit and in [0, 512].")
    quadrature = request["quadrature_order"]
    if type(quadrature) is not int or not 1 <= quadrature <= 512:
        _invalid("HASEGAWA_REQUEST", "/quadrature_order", "Preflight quadrature dimension must be in [1, 512].")
    chunk = request["point_chunk_size"]
    if type(chunk) is not int or chunk != len(points):
        _invalid("HASEGAWA_REQUEST", "/point_chunk_size", "This request is one complete bounded field chunk.")
    return request


def admit(scenario: Scenario, request: dict) -> dict:
    config = scenario.to_dict()
    if config["schema_version"] != "1.1":
        _invalid("RUN_SCENARIO_VERSION", "/schema_version", "The Hasegawa driver requires Scenario 1.1.")
    solver = config["solver"]
    if (solver["model_id"], solver["model_version"], solver["equation_ids"], solver["precision"]) != (
        DRIVER, VERSION, ["EQ-HASEGAWA-1985"], "complex128"
    ) or solver["parameters"]:
        _invalid("RUN_MODEL", "/solver", "Hasegawa driver identity, equation, precision, or parameters differ.")
    medium = config["medium"]
    if medium["dynamic_viscosity"]["value"] != 0 or medium["amplitude_attenuation"]["value"] != 0:
        _invalid("FIELD_MODEL", "/medium", "Only the frozen homogeneous, lossless linear-air case is admitted.")
    sources = config["sources"]
    if sources["frequency"]["value"] != 25_230 or len(sources["elements"]) != 1:
        _invalid("FIELD_SOURCE", "/sources", "Expected the single 25,230 Hz frozen piston source.")
    if (medium["temperature"]["value"], medium["density"]["value"], medium["sound_speed"]["value"]) != (
        298.15, 1.18, 346
    ):
        _invalid("FIELD_MEDIUM", "/medium", "Medium differs from the frozen 25 °C homogeneous-air case.")
    source = sources["elements"][0]
    if source["model"] != "circular_piston" or source["position"]["value"] != [0, 0, 0] or (
        source["normal"]["value"] != [0, 0, 1]
    ) or source["aperture_radius"]["value"] != 0.01:
        _invalid("FIELD_SOURCE", "/sources/elements/0", "Source differs from the centered 10 mm baffled piston contract.")
    if source["displacement_amplitude"]["value"] != 15e-6 or source["phase"]["value"] != 0:
        _invalid("FIELD_SOURCE", "/sources/elements/0/displacement_amplitude", "Source amplitude/phase differs from the frozen DEC-002 case.")
    if len(config["bodies"]) != 1:
        _invalid("FIELD_BODY", "/bodies", "Expected one stationary spherical reference body.")
    body = config["bodies"][0]
    radius = body["geometry"].get("radius", {}).get("value")
    distance = radius + request["gap_m"]
    if body["geometry"]["kind"] != "sphere" or radius != 0.025 or (
        body["initial_state"]["position"]["value"] != [0, 0, distance]
    ) or body["initial_state"]["velocity"]["value"] != [0, 0, 0]:
        _invalid("FIELD_BODY", "/bodies/0", "Body must be the stationary 25 mm sphere at the requested axial gap.")
    if body["material"] != "rigid-sound-hard-reference":
        _invalid("FIELD_BODY", "/bodies/0/material", "This field branch admits only the declared rigid sound-hard reference.")
    if sources["phasor_convention"] != "exp(-iwt)" or sources["amplitude_convention"] != "peak":
        _invalid("FIELD_CONVENTION", "/sources", "Expected peak amplitudes with exp(-iwt) phasors.")
    k = 2 * math.pi * sources["frequency"]["value"] / medium["sound_speed"]["value"]
    velocity = -1j * 2 * math.pi * sources["frequency"]["value"] * source[
        "displacement_amplitude"
    ]["value"] * complex(math.cos(source["phase"]["value"]), math.sin(source["phase"]["value"]))
    field_argument_max = max(
        k * math.hypot(row[0], row[1], row[2] - distance) for row in request["coordinates_m"]
    )
    if field_argument_max > 40:
        _invalid("FIELD_ARGUMENT_RANGE", "/coordinates_m", "Field samples exceed the evaluator's kr <= 40 domain.")
    maximum_argument = max(
        field_argument_max, k * radius,
        k * math.hypot(distance, source["aperture_radius"]["value"]),
    )
    if maximum_argument > 8192:
        _invalid("FIELD_ARGUMENT_RANGE", "/coordinates_m", "Preflight Bessel argument exceeds the supported recurrence domain.")
    for index, row in enumerate(request["coordinates_m"]):
        origin = config["domain"]["origin"]["value"]
        upper = [float(a) + float(b) for a, b in zip(origin, config["domain"]["size"]["value"])]
        if any(not low <= coordinate <= high for coordinate, low, high in zip(row, origin, upper)):
            _invalid("FIELD_DOMAIN", f"/coordinates_m/{index}", "Sample lies outside the declared Scenario domain.")
        r = math.hypot(row[0], row[1], row[2] - distance)
        surface_roundoff = 8 * math.ulp(float(radius))
        if not math.isfinite(r) or r < radius - surface_roundoff:
            _invalid("FIELD_DOMAIN", f"/coordinates_m/{index}", "Sample must lie on or outside the sphere.")
        if abs(r - radius) <= surface_roundoff:
            r = float(radius)
        if row[2] <= 0 or r >= distance:
            _invalid("FIELD_DOMAIN", f"/coordinates_m/{index}", "Sample is outside the piston/sphere expansion shell.")
    return {
        "config": config, "source": source, "body": body, "distance_m": distance,
        "radius_m": radius, "velocity_m_s": velocity, "maximum_argument": maximum_argument,
    }


def preflight(scenario: Scenario, request: dict, calibration: dict, calibration_sha256: str,
              source_snapshot: dict, environment: dict, output_dir) -> dict:
    bound = admit(scenario, request)
    if source_snapshot["dirty"] or source_snapshot["revision"] is None:
        raise IncompleteEvidenceError(
            "PREFLIGHT_SOURCE_DIRTY", "/source",
            "Runtime calibration requires the exact clean source revision.",
        )
    if environment["profile"] != "ENV-1.0":
        raise IncompleteEvidenceError("PREFLIGHT_ENVIRONMENT", "/environment", "Runtime calibration requires ENV-1.0.")
    workload = {
        "contract": "AIR-SERIES-WORKLOAD-1.1", "solver_model_id": DRIVER,
        "solver_model_version": VERSION, "gap_count": 1,
        "points_per_gap": len(request["coordinates_m"]), "harmonic_order": request["max_order"],
        "quadrature_order": request["quadrature_order"],
        "bessel_argument_max": bound["maximum_argument"],
        "point_chunk_size": request["point_chunk_size"],
    }
    from .manifest import digest as payload_digest

    report = estimate_air_series(
        bound["config"], workload, calibration, calibration_sha256=calibration_sha256,
        output_dir=output_dir, current_source_revision=source_snapshot["revision"],
        current_environment_sha256=payload_digest(encode(environment)),
    )
    require_ready(report)
    return report


def execute_field(scenario: Scenario, request: dict, run_id: str, estimate: dict, emit) -> None:
    bound = admit(scenario, request)
    from aura.fields.hasegawa import evaluate_hasegawa_piston_sphere_field

    config = bound["config"]
    samples = evaluate_hasegawa_piston_sphere_field(
        request["coordinates_m"], density_kg_m3=config["medium"]["density"]["value"],
        sound_speed_m_s=config["medium"]["sound_speed"]["value"],
        frequency_hz=config["sources"]["frequency"]["value"],
        piston_velocity_peak_m_s=bound["velocity_m_s"],
        piston_radius_m=bound["source"]["aperture_radius"]["value"],
        sphere_radius_m=bound["radius_m"], sphere_center_distance_m=bound["distance_m"],
        max_order=request["max_order"], workspace_bytes=estimate["estimates"]["ram_bytes"],
    )
    artifacts = samples.to_artifacts()
    names = {
        "coordinates": "field-coordinates.json", "pressure": "field-pressure.json",
        "velocity": "field-velocity.json", "pressure_gradient": "field-pressure-gradient.json",
    }
    refs = {key: emit(name, artifacts[key]) for key, name in names.items()}
    field_result = FieldResult({
        "document_type": "field_result", "schema_version": "1.0", "id": run_id + "-FIELD",
        "run_id": run_id, "frame": "chamber", "model_id": DRIVER, "model_version": VERSION,
        "regime": ["Hasegawa-1985", "homogeneous-air", "lossless", "linear", "stationary-rigid-sphere"],
        "coordinates": {"artifact": {"uri": refs["coordinates"]["uri"], "sha256": refs["coordinates"]["sha256"]},
                        "unit": "m", "shape": [len(samples.coordinates_m), 3], "dtype": "float64"},
        "pressure": {"artifact": {"uri": refs["pressure"]["uri"], "sha256": refs["pressure"]["sha256"]},
                     "unit": "Pa", "shape": [len(samples.coordinates_m)], "dtype": "complex128"},
        "velocity": {"artifact": {"uri": refs["velocity"]["uri"], "sha256": refs["velocity"]["sha256"]},
                     "unit": "m/s", "shape": [len(samples.coordinates_m), 3], "dtype": "complex128"},
        "phasor_convention": "exp(-iwt)", "amplitude_convention": "peak",
        "diagnostics": [
            f"Diagnostic finite sum through max_order={request['max_order']}; no convergence or field-accuracy tolerance is asserted.",
            "Ideal source displacement was converted to face velocity using v_n=-i*omega*xi under exp(-iwt).",
            "Numerical software verification only; this result is not model validation or an experimental observation.",
        ], "provenance": config["provenance"],
    }).to_dict()
    result_ref = emit("field-result.json", field_result)
    emit("field-index.json", {
        "contract": INDEX_CONTRACT, "run_policy": RUN_POLICY, "run_id": run_id,
        "field_result_id": field_result["id"], "field_result_sha256": result_ref["sha256"],
        "case_id": request["case_id"], "frequency_hz": samples.frequency_hz,
        "pressure_gradient": {
            "artifact": {"uri": refs["pressure_gradient"]["uri"], "sha256": refs["pressure_gradient"]["sha256"]},
            "unit": "Pa/m", "shape": [len(samples.coordinates_m), 3], "dtype": "complex128",
        },
        "scope": SCOPE,
    })


def check_preflight(report: dict, scenario: Scenario, request: dict, calibration_sha256: str) -> None:
    if type(report) is not dict or report.get("contract") != "AIR-SERIES-PREFLIGHT-1.1" or (
        report.get("status") != "BUDGETS_WITHIN_CAPS" or report.get("execution_authorized") is not False
    ):
        fail("RUN_PREFLIGHT", "Stored Hasegawa NUM-02 preflight is not a budget-fit report.")
    if report.get("solver_model_id") != DRIVER or report.get("solver_model_version") != VERSION or (
        report.get("calibration", {}).get("calibration_sha256") != calibration_sha256
    ):
        fail("RUN_PREFLIGHT", "Stored Hasegawa preflight identity/calibration differs.")
    bound = admit(scenario, request)
    dimensions = report.get("dimensions", {})
    if dimensions.get("gap_count") != 1 or dimensions.get("points_per_gap") != len(request["coordinates_m"]) or (
        dimensions.get("harmonic_order") != request["max_order"]
    ) or dimensions.get("point_chunk_size") != len(request["coordinates_m"]) or (
        dimensions.get("bessel_argument_max") != bound["maximum_argument"]
    ):
        fail("RUN_PREFLIGHT", "Preflight workload differs from the immutable Hasegawa request.")


def check_field_outputs(run_id: str, config: dict, request: dict, refs: list[dict], content: dict) -> None:
    from aura.fields import FieldSamples


    if {ref["uri"] for ref in refs} != OUTPUT_NAMES:
        fail("FIELD_OUTPUTS", "Hasegawa run has a missing or unexpected output artifact.")
    samples = FieldSamples.from_artifacts({
        key: content[name] for key, name in {
            "coordinates": "field-coordinates.json", "pressure": "field-pressure.json",
            "velocity": "field-velocity.json", "pressure_gradient": "field-pressure-gradient.json",
        }.items()
    })
    if samples.coordinates_m != tuple(tuple(row) for row in request["coordinates_m"]):
        fail("FIELD_SAMPLES", "Hasegawa output coordinates differ from the ordered request.")
    by_name = {ref["uri"]: ref for ref in refs}
    result = FieldResult(content["field-result.json"]).to_dict()
    driver_id = config["solver"]["model_id"]
    if (result["run_id"], result["id"], result["model_id"], result["model_version"]) != (
        run_id, run_id + "-FIELD", driver_id, VERSION
    ):
        fail("FIELD_RESULT", "Hasegawa FieldResult identity differs.")
    if result["frame"] != "chamber" or result["regime"] != [
        "Hasegawa-1985", "homogeneous-air", "lossless", "linear", "stationary-rigid-sphere"
    ] or result["phasor_convention"] != "exp(-iwt)" or result["amplitude_convention"] != "peak":
        fail("FIELD_RESULT", "Hasegawa field model or phasor metadata differs.")
    if samples.frequency_hz != config["sources"]["frequency"]["value"]:
        fail("FIELD_FREQUENCY", "Hasegawa field frequency differs from the Scenario.")
    index = content["field-index.json"]
    if set(index) != {
        "contract", "run_policy", "run_id", "field_result_id", "field_result_sha256",
        "case_id", "frequency_hz", "pressure_gradient", "scope",
    }:
        fail("FIELD_INDEX", "Hasegawa FIELD-INDEX has missing or unexpected fields.")
    if index.get("contract") != INDEX_CONTRACT or index.get("run_policy") != RUN_POLICY or (
        index.get("run_id") != run_id or index.get("field_result_id") != result["id"]
    ) or index.get("field_result_sha256") != by_name["field-result.json"]["sha256"] or (
        index.get("field_result_sha256") != digest(encode(result))
    ) or index.get("case_id") != request["case_id"] or index.get("frequency_hz") != samples.frequency_hz or (
        index.get("scope") != SCOPE
    ):
        fail("FIELD_INDEX", "Hasegawa FIELD-INDEX identity differs.")
    gradient = index.get("pressure_gradient", {})
    if gradient != {
        "artifact": {"uri": by_name["field-pressure-gradient.json"]["uri"],
                     "sha256": by_name["field-pressure-gradient.json"]["sha256"]},
        "unit": "Pa/m", "shape": [len(samples.coordinates_m), 3], "dtype": "complex128",
    }:
        fail("FIELD_INDEX", "Hasegawa pressure-gradient reference differs.")
    for key, unit, shape, dtype, filename in (
        ("coordinates", "m", [len(samples.coordinates_m), 3], "float64", "field-coordinates.json"),
        ("pressure", "Pa", [len(samples.coordinates_m)], "complex128", "field-pressure.json"),
        ("velocity", "m/s", [len(samples.coordinates_m), 3], "complex128", "field-velocity.json"),
    ):
        reference = by_name[filename]
        descriptor = result[key]
        expected = {
            "artifact": {"uri": reference["uri"], "sha256": reference["sha256"]},
            "unit": unit, "shape": shape, "dtype": dtype,
        }
        if descriptor != expected:
            fail("FIELD_RESULT", f"Hasegawa FieldResult {key} reference differs from its artifact.")
