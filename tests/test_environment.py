"""Known profile mutations must fail without changing the actual environment."""

import copy
import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ROOT / "scripts/verify_environment.py"))
MANIFEST = json.loads((ROOT / "requirements/environment-linux-py312.json").read_text())
EXPECTED = {item["name"]: item["version"] for item in MANIFEST["artifacts"]}
RUNTIME = {key: MANIFEST[key] for key in ("python", "implementation", "system", "machine")}
RUNTIME["libc"] = ["glibc", "2.28"]


def test_repository_locks_match_inventory():
    core = MODULE["read_pins"]((ROOT / "requirements/core-linux-py312.lock").read_text())
    dev = MODULE["read_pins"](
        (ROOT / "requirements/dev-linux-py312.lock").read_text(), development=True,
    )
    assert MODULE["verify_inventory"](MANIFEST, core, dev) == EXPECTED
    assert not MODULE["profile_errors"](MANIFEST, EXPECTED, EXPECTED, RUNTIME)


@pytest.mark.parametrize("mutation", ["missing", "wrong", "extra"])
def test_package_changes_fail(mutation):
    installed = dict(EXPECTED)
    if mutation == "missing":
        del installed["attrs"]
    elif mutation == "wrong":
        installed["attrs"] = "0.0.0"
    else:
        installed["unreviewed"] = "1.0"
    assert MODULE["profile_errors"](MANIFEST, EXPECTED, installed, RUNTIME)


@pytest.mark.parametrize("key,value", [
    ("python", "3.12.13"), ("implementation", "PyPy"), ("system", "Darwin"),
    ("machine", "aarch64"), ("libc", ["glibc", "2.27"]),
    ("libc", ["musl", "1.2"]), ("libc", ["glibc", "unknown"]),
])
def test_runtime_changes_fail(key, value):
    runtime = {**RUNTIME, key: value}
    assert MODULE["profile_errors"](MANIFEST, EXPECTED, EXPECTED, runtime)


@pytest.mark.parametrize("text,development", [
    ("attrs>=26", False), ("-r arbitrary.lock", False), ("", True),
    ("-r core-linux-py312.lock\n-r core-linux-py312.lock", True),
    (("attrs==26.1.0 --hash=sha256:" + "a" * 64 + "\n") * 2, False),
])
def test_malformed_locks_fail(text, development):
    with pytest.raises(ValueError):
        MODULE["read_pins"](text, development=development)


@pytest.mark.parametrize("field,value", [
    ("version", "0.0"), ("sha256", "0" * 64), ("scope", "unreviewed"),
    ("name", "Invalid_Name"),
])
def test_inventory_changes_fail(field, value):
    altered = copy.deepcopy(MANIFEST)
    altered["artifacts"][0][field] = value
    core = MODULE["read_pins"]((ROOT / "requirements/core-linux-py312.lock").read_text())
    dev = MODULE["read_pins"](
        (ROOT / "requirements/dev-linux-py312.lock").read_text(), development=True,
    )
    with pytest.raises(ValueError):
        MODULE["verify_inventory"](altered, core, dev)


def test_duplicate_inventory_fails():
    altered = copy.deepcopy(MANIFEST)
    altered["artifacts"].append(altered["artifacts"][0])
    with pytest.raises(ValueError, match="duplicate"):
        MODULE["verify_inventory"](altered, {}, {})


def test_duplicate_editable_metadata_with_same_version_is_collapsed():
    assert MODULE["installed_versions"]([
        ("AURA_science", "0.1.0"), ("aura-science", "0.1.0"),
    ]) == {"aura-science": "0.1.0"}


def test_conflicting_installed_metadata_fails():
    with pytest.raises(ValueError, match="Conflicting"):
        MODULE["installed_versions"]([("attrs", "26.1.0"), ("attrs", "0.0")])
