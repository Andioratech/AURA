import math

import pytest

from aura.errors import InvalidInputError, NumericalDomainError
from aura.fields._bem_mesh import estimate_bem_dense_workspace, sphere_meridian_quadrature


def test_sphere_meridian_rule_reproduces_surface_moments_and_reflection_symmetry():
    radius = 0.025
    rows = sphere_meridian_quadrature(radius, panels=7, order_per_panel=16)

    area_without_azimuth = math.fsum(weight for _, weight in rows)
    first_axial_moment = math.fsum(weight * math.cos(theta) for theta, weight in rows)
    second_axial_moment = math.fsum(
        weight * math.cos(theta) ** 2 for theta, weight in rows
    )
    assert area_without_azimuth == pytest.approx(2.0 * radius**2, rel=2e-14, abs=1e-18)
    assert first_axial_moment == pytest.approx(0.0, abs=1e-18)
    assert second_axial_moment == pytest.approx(2.0 * radius**2 / 3.0, rel=2e-13, abs=1e-18)

    for (theta, weight), (reflected_theta, reflected_weight) in zip(
        rows, reversed(rows), strict=True
    ):
        assert theta + reflected_theta == pytest.approx(math.pi, abs=8 * math.ulp(math.pi))
        assert weight == pytest.approx(reflected_weight, rel=2e-13, abs=1e-18)


@pytest.mark.parametrize(
    ("radius", "panels", "order"),
    [
        (0.0, 1, 8),
        (math.nan, 1, 8),
        (True, 1, 8),
        (0.025, True, 8),
        (0.025, 1, 0),
        (0.025, 257, 256),
    ],
)
def test_sphere_meridian_rule_rejects_invalid_or_unbounded_inputs(radius, panels, order):
    with pytest.raises(InvalidInputError):
        sphere_meridian_quadrature(radius, panels=panels, order_per_panel=order)


@pytest.mark.parametrize("radius", [1e-200, 1e308])
def test_sphere_meridian_rule_rejects_nonrepresentable_surface_weights(radius):
    with pytest.raises(NumericalDomainError):
        sphere_meridian_quadrature(radius, panels=1, order_per_panel=2)


@pytest.mark.parametrize(
    ("panels", "nodes", "pairs", "operator_entries", "estimated_bytes"),
    [
        (4, 16, 256, 1024, 305_152),
        (8, 32, 1024, 4096, 741_376),
        (16, 64, 4096, 16384, 2_400_256),
    ],
)
def test_bem_workspace_estimate_is_exact_and_never_authorizes_execution(
    panels, nodes, pairs, operator_entries, estimated_bytes, monkeypatch
):
    import aura.fields._bem_mesh as mesh

    def forbidden(*args, **kwargs):
        raise AssertionError("Resource estimation must not create quadrature or solver arrays.")

    monkeypatch.setattr(mesh, "sphere_meridian_quadrature", forbidden)
    report = estimate_bem_dense_workspace(
        panels=panels,
        order_per_panel=4,
        ram_cap_bytes=16 * 1024**2,
        available_ram_bytes=32 * 1024**2,
    )

    assert report["contract"] == "BEM-DENSE-WORKSPACE-1.0"
    assert report["status"] == "INDETERMINATE"
    assert report["reason"] == "BEM_RUNTIME_UNCALIBRATED"
    assert report["node_count"] == nodes
    assert report["meridian_pair_count"] == pairs
    assert report["operator_entry_count"] == operator_entries
    assert report["estimated_ram_bytes"] == estimated_bytes
    assert report["runtime_estimate_seconds"] is None
    assert report["execution_authorized"] is False


@pytest.mark.parametrize(
    ("ram_cap", "available_ram"),
    [(100_000, 32 * 1024**2), (16 * 1024**2, 100_000)],
)
def test_bem_workspace_estimate_rejects_before_any_allocation(ram_cap, available_ram):
    report = estimate_bem_dense_workspace(
        panels=16,
        order_per_panel=4,
        ram_cap_bytes=ram_cap,
        available_ram_bytes=available_ram,
    )

    assert report["status"] == "REJECTED"
    assert report["reason"] == "RESOURCE_BUDGET_EXCEEDED"
    assert report["estimated_ram_bytes"] > min(ram_cap, available_ram)
    assert report["execution_authorized"] is False


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"panels": True}, "BEM_MERIDIAN_PANELS"),
        ({"order_per_panel": 513}, "BEM_MERIDIAN_ORDER"),
        ({"panels": 20_000, "order_per_panel": 4}, "BEM_MERIDIAN_WORK"),
        ({"ram_cap_bytes": -1}, "BEM_RESOURCE_CAP"),
        ({"available_ram_bytes": 1.0}, "BEM_RESOURCE_AVAILABLE"),
    ],
)
def test_bem_workspace_estimate_rejects_invalid_dimensions_and_caps(changes, code):
    inputs = {
        "panels": 4,
        "order_per_panel": 4,
        "ram_cap_bytes": 16 * 1024**2,
        "available_ram_bytes": 32 * 1024**2,
    }
    inputs.update(changes)
    with pytest.raises(InvalidInputError) as error:
        estimate_bem_dense_workspace(**inputs)
    assert error.value.code == code
