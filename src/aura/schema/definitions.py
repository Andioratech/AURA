"""Local Draft 2020-12 schemas for the initial canonical SI contract."""

from __future__ import annotations

from copy import deepcopy

from .quantities import SI_UNITS, quantity

VERSION = "1.0"
SCENARIO_VERSION = "1.1"
TEXT = {"type": "string", "minLength": 1}
IDENTIFIER = {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9_.-]*$(?!\n)"}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$", "minLength": 64, "maxLength": 64}
POSITIVE_INT = {"type": "integer", "minimum": 1}
VERDICTS = ["ACCEPTED", "ALERT", "INVALIDATED", "INDETERMINATE"]


def obj(properties: dict, optional: tuple[str, ...] = ()) -> dict:
    return {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "required": [name for name in properties if name not in optional],
    }


def array(items: dict, minimum: int = 0) -> dict:
    return {"type": "array", "items": items, "minItems": minimum}


def ref(name: str) -> dict:
    return {"$ref": f"#/$defs/{name}"}


PROVENANCE = obj(
    {
        "basis": {"enum": ["measured", "assumed", "manufactured"]},
        "reference": TEXT,
        "uncertainty_status": {"enum": ["reported", "unknown", "not_applicable"]},
        "uncertainty_reference": {"type": ["string", "null"], "minLength": 1},
    }
)
ARTIFACT = obj({"uri": TEXT, "sha256": HASH})
RESOURCES = obj(
    {
        "ram_bytes": POSITIVE_INT,
        "disk_bytes": POSITIVE_INT,
        "wall_time": quantity("s", positive=True),
    }
)
WINDOW = obj({"start": quantity("s", nonnegative=True), "end": quantity("s", positive=True)})
GEOMETRY = obj(
    {
        "kind": {"enum": ["sphere", "box"]},
        "radius": quantity("m", positive=True),
        "dimensions": quantity("m", size=3, positive=True),
    },
    optional=("radius", "dimensions"),
)
GEOMETRY["allOf"] = [
    {
        "if": {"properties": {"kind": {"const": "sphere"}}},
        "then": {"required": ["radius"], "not": {"required": ["dimensions"]}},
        "else": {"required": ["dimensions"], "not": {"required": ["radius"]}},
    }
]
INITIAL_STATE = obj(
    {
        "position": quantity("m", size=3),
        "velocity": quantity("m/s", size=3),
        "orientation": quantity("1", size=4),
        "angular_velocity": quantity("rad/s", size=3),
    }
)
SOURCE = obj(
    {
        "id": IDENTIFIER,
        "position": quantity("m", size=3),
        "normal": quantity("1", size=3),
        "phase": quantity("rad"),
        "pressure_amplitude": quantity("Pa", nonnegative=True),
        "pressure_limit": quantity("Pa", positive=True),
        "model": {"enum": ["ideal_plane_wave", "circular_piston", "ideal_spherical_wave"]},
        "model_contract": {"const": "SPHERICAL-WAVE-1.0"},
        "center": quantity("m", size=3),
        "reference_radius": quantity("m", positive=True),
        "minimum_radius": quantity("m", positive=True),
        "aperture_radius": quantity("m", positive=True),
    },
    optional=(
        "position", "normal", "model_contract", "center", "reference_radius",
        "minimum_radius", "aperture_radius",
    ),
)
SOURCE["allOf"] = [
    {
        "if": {"properties": {"model": {"const": "ideal_plane_wave"}}, "required": ["model"]},
        "then": {
            "required": ["position", "normal"],
            "not": {"anyOf": [{"required": [name]} for name in (
                "model_contract", "center", "reference_radius", "minimum_radius", "aperture_radius"
            )]},
        },
    },
    {
        "if": {"properties": {"model": {"const": "circular_piston"}}, "required": ["model"]},
        "then": {
            "required": ["position", "normal", "aperture_radius"],
            "not": {"anyOf": [{"required": [name]} for name in (
                "model_contract", "center", "reference_radius", "minimum_radius"
            )]},
        },
    },
    {
        "if": {"properties": {"model": {"const": "ideal_spherical_wave"}}, "required": ["model"]},
        "then": {
            "required": ["model_contract", "center", "reference_radius", "minimum_radius"],
            "not": {"anyOf": [{"required": [name]} for name in (
                "position", "normal", "aperture_radius"
            )]},
        },
    },
]

# Scenario 1.1 gives a uniformly displaced baffled piston its own SI amplitude
# contract. Scenario 1.0 remains frozen for existing records.
SOURCE_V11 = deepcopy(SOURCE)
SOURCE_V11["properties"].update({
    "displacement_amplitude": quantity("m", nonnegative=True),
    "displacement_limit": quantity("m", positive=True),
})
SOURCE_V11["properties"]["pressure_amplitude"] = quantity("Pa", nonnegative=True)
SOURCE_V11["properties"]["pressure_limit"] = quantity("Pa", positive=True)
SOURCE_V11["required"] = [
    name for name in SOURCE_V11["required"] if name not in ("pressure_amplitude", "pressure_limit")
]
SOURCE_V11["allOf"] = [
    {
        "if": {"properties": {"model": {"const": model}}, "required": ["model"]},
        "then": {
            "required": required,
            "not": {"anyOf": [{"required": [name]} for name in forbidden]},
        },
    }
    for model, required, forbidden in (
        (
            "ideal_plane_wave",
            ["position", "normal", "pressure_amplitude", "pressure_limit"],
            ["model_contract", "center", "reference_radius", "minimum_radius",
             "aperture_radius", "displacement_amplitude", "displacement_limit"],
        ),
        (
            "circular_piston",
            ["position", "normal", "aperture_radius", "displacement_amplitude", "displacement_limit"],
            ["model_contract", "center", "reference_radius", "minimum_radius",
             "pressure_amplitude", "pressure_limit"],
        ),
        (
            "ideal_spherical_wave",
            ["model_contract", "center", "reference_radius", "minimum_radius",
             "pressure_amplitude", "pressure_limit"],
            ["position", "normal", "aperture_radius", "displacement_amplitude", "displacement_limit"],
        ),
    )
]
CHECK_STATE = {
    "oneOf": [
        obj({"status": {"const": "not_run"}}),
        obj({"status": {"const": "completed"}, "verdict": {"enum": VERDICTS}, "report": ARTIFACT}),
    ]
}
SAMPLE_ARTIFACT = obj(
    {
        "artifact": ARTIFACT,
        "unit": {"enum": list(SI_UNITS)},
        "shape": array(POSITIVE_INT, 1),
        "dtype": {"enum": ["float64", "complex128"]},
    }
)
DEFINITIONS = {
    "medium": obj(
        {
            "id": IDENTIFIER,
            "name": TEXT,
            "temperature": quantity("K", positive=True),
            "density": quantity("kg/m^3", positive=True),
            "sound_speed": quantity("m/s", positive=True),
            "dynamic_viscosity": quantity("Pa*s", nonnegative=True),
            "compressibility": quantity("1/Pa", positive=True),
            "amplitude_attenuation": quantity("1/m", nonnegative=True),
            "provenance": PROVENANCE,
        }
    ),
    "body": obj(
        {
            "id": IDENTIFIER,
            "material": TEXT,
            "geometry": GEOMETRY,
            "mass": quantity("kg", positive=True),
            "density": quantity("kg/m^3", positive=True),
            "compressibility": quantity("1/Pa", positive=True),
            "initial_state": INITIAL_STATE,
            "provenance": PROVENANCE,
            "inertia": obj(
                {
                    "frame": {"const": "body"},
                    "unit": {"const": "kg*m^2"},
                    "value": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 3,
                        "items": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {"type": "number"},
                        },
                    },
                }
            ),
        },
        optional=("inertia",),
    ),
    "transducer_array": obj(
        {
            "id": IDENTIFIER,
            "frequency": quantity("Hz", positive=True),
            "amplitude_convention": {"const": "peak"},
            "phasor_convention": {"const": "exp(-iwt)"},
            "elements": array(SOURCE, 1),
            "provenance": PROVENANCE,
        }
    ),
    "solver_spec": obj(
        {
            "id": IDENTIFIER,
            "model_id": IDENTIFIER,
            "model_version": TEXT,
            "equation_ids": array(IDENTIFIER, 1),
            "regime": array(TEXT, 1),
            "precision": {"enum": ["float64", "complex128"]},
            "parameters": obj(
                {
                    "max_iterations": POSITIVE_INT,
                    "tolerance": {"type": "number", "exclusiveMinimum": 0},
                    "mesh_spacing": quantity("m", positive=True),
                    "time_step": quantity("s", positive=True),
                },
                optional=("max_iterations", "tolerance", "mesh_spacing", "time_step"),
            ),
        }
    ),
    "scenario": obj(
        {
            "id": IDENTIFIER,
            "conventions": {"const": "CONV-1.0"},
            "frame": {"const": "chamber"},
            "medium": ref("medium"),
            "bodies": array(ref("body"), 1),
            "sources": ref("transducer_array"),
            "solver": ref("solver_spec"),
            "domain": obj(
                {
                    "origin": quantity("m", size=3),
                    "size": quantity("m", size=3, positive=True),
                    "boundary_model": IDENTIFIER,
                    "boundary_reference": TEXT,
                }
            ),
            "gravity": quantity("m/s^2", size=3),
            "target": obj({"acceleration": quantity("m/s^2", size=3), "window": WINDOW}),
            "resources": RESOURCES,
            "provenance": PROVENANCE,
        }
    ),
    "experiment": obj(
        {
            "id": IDENTIFIER,
            "scenario_id": IDENTIFIER,
            "scenario_sha256": HASH,
            "hypothesis": TEXT,
            "claim_id": IDENTIFIER,
            "primary_observable": obj(
                {
                    "name": IDENTIFIER,
                    "unit": {"enum": list(SI_UNITS)},
                    "definition": TEXT,
                    "window": WINDOW,
                }
            ),
            "acceptance_rule": TEXT,
            "uncertainty_plan": TEXT,
            "protocol": ARTIFACT,
            "provenance": PROVENANCE,
        }
    ),
    "run_manifest": obj(
        {
            "id": IDENTIFIER,
            "experiment_id": IDENTIFIER,
            "scenario_id": IDENTIFIER,
            "claim_id": IDENTIFIER,
            "hypothesis": TEXT,
            "observables": array(TEXT, 1),
            "timestamp_utc": {
                "type": "string",
                "format": "date-time",
                "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z$",
            },
            "execution_status": {"enum": ["planned", "running", "completed", "failed", "aborted"]},
            "source": obj(
                {
                    "revision": {
                        "type": "string",
                        "pattern": r"^[0-9a-f]{40}([0-9a-f]{24})?$(?!\n)",
                    },
                    "dirty": {"type": "boolean"},
                    "patch_sha256": {"anyOf": [HASH, {"type": "null"}]},
                }
            ),
            "configuration_sha256": HASH,
            "environment": obj({"lock": ARTIFACT, "platform": TEXT}),
            "solver": ref("solver_spec"),
            "seed": {"type": ["integer", "null"], "minimum": 0},
            "resources": RESOURCES,
            "inputs": array(ARTIFACT),
            "outputs": array(ARTIFACT),
            "metrics": array(
                obj(
                    {
                        "name": IDENTIFIER,
                        "value": {"type": "number"},
                        "unit": {"enum": list(SI_UNITS)},
                        "definition": TEXT,
                    }
                )
            ),
            "convergence": array(ARTIFACT),
            "mclf_pre": CHECK_STATE,
            "mclf_post": CHECK_STATE,
            "failure_code": {"type": ["string", "null"], "minLength": 1},
            "operator_notes": {"type": "string"},
        }
    ),
    "field_result": obj(
        {
            "id": IDENTIFIER,
            "run_id": IDENTIFIER,
            "frame": {"const": "chamber"},
            "model_id": IDENTIFIER,
            "model_version": TEXT,
            "regime": array(TEXT, 1),
            "coordinates": SAMPLE_ARTIFACT,
            "pressure": SAMPLE_ARTIFACT,
            "velocity": {"anyOf": [SAMPLE_ARTIFACT, {"type": "null"}]},
            "phasor_convention": {"const": "exp(-iwt)"},
            "amplitude_convention": {"const": "peak"},
            "diagnostics": array(TEXT),
            "provenance": PROVENANCE,
        }
    ),
    "force_result": obj(
        {
            "id": IDENTIFIER,
            "run_id": IDENTIFIER,
            "body_id": IDENTIFIER,
            "frame": {"const": "chamber"},
            "model_id": IDENTIFIER,
            "model_version": TEXT,
            "precision": {"const": "float64"},
            "regime": array(TEXT, 1),
            "force": quantity("N", size=3),
            "torque": {"anyOf": [quantity("N*m", size=3), {"type": "null"}]},
            "torque_status": {"enum": ["available", "unsupported"]},
            "validity": {"enum": VERDICTS},
            "provenance": PROVENANCE,
        }
    ),
    "mclf_report": obj(
        {
            "id": IDENTIFIER,
            "run_id": IDENTIFIER,
            "level": {"enum": ["L0", "L1", "L2", "L3", "L4", "L5"]},
            "verdict": {"enum": VERDICTS},
            "checks": array(
                obj(
                    {
                        "rule_id": {"type": "string", "pattern": "^R-[0-9]{3}$", "maxLength": 5},
                        "verdict": {"enum": VERDICTS},
                        "message": TEXT,
                        "assumptions": array(TEXT),
                    }
                ),
                1,
            ),
            "limitations": array(TEXT),
        }
    ),
}

DEFINITIONS_V11 = deepcopy(DEFINITIONS)
DEFINITIONS_V11["transducer_array"]["properties"]["elements"]["items"] = SOURCE_V11


def document_schema(document_type: str, version: str = VERSION) -> dict:
    """Return an isolated schema; every reference is local to this document."""
    definitions = DEFINITIONS_V11 if document_type == "scenario" and version == SCENARIO_VERSION else DEFINITIONS
    if document_type not in definitions or version not in (VERSION, SCENARIO_VERSION):
        raise KeyError((document_type, version))
    if document_type != "scenario" and version != VERSION:
        raise KeyError((document_type, version))
    domain = deepcopy(definitions[document_type])
    domain["properties"] = {
        "document_type": {"const": document_type},
        "schema_version": {"const": version},
        **domain["properties"],
    }
    domain["required"] += ["document_type", "schema_version"]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": deepcopy(definitions),
        **domain,
    }
