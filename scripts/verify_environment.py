"""Verify the reviewed development profile without resolving or downloading packages."""

import hashlib
import importlib.metadata
import json
import platform
import re
import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
PIN = re.compile(r"([a-z0-9-]+)==([^\s]+) --hash=sha256:([a-f0-9]{64})")


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def read_pins(text, *, development=False):
    pins = {}
    includes = 0
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if development and line == "-r core-linux-py312.lock":
            includes += 1
            continue
        match = PIN.fullmatch(line)
        if not match:
            raise ValueError(f"Unsupported lock line: {line}")
        name, version, digest = match.groups()
        if name in pins:
            raise ValueError(f"Duplicate lock package: {name}")
        pins[name] = (version, digest)
    if includes != int(development):
        raise ValueError("Development lock must include the core lock exactly once")
    return pins


def verify_inventory(manifest, core, development):
    expected = {"core": {}, "development": {}}
    names = set()
    for item in manifest["artifacts"]:
        name, scope = item["name"], item["scope"]
        if name in names or normalize(name) != name or scope not in expected:
            raise ValueError(f"Invalid or duplicate inventory package: {name}")
        names.add(name)
        expected[scope][name] = (item["version"], item["sha256"])
    if expected != {"core": core, "development": development}:
        raise ValueError("Lock versions/hashes/scopes differ from the inventory")
    return {item["name"]: item["version"] for item in manifest["artifacts"]}


def installed_versions(records):
    installed = {}
    for name, version in records:
        name = normalize(name)
        if name in installed and installed[name] != version:
            raise ValueError(f"Conflicting installed versions: {name}")
        installed[name] = version
    return installed


def runtime_snapshot():
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "system": platform.system(),
        "machine": platform.machine(),
        "libc": list(platform.libc_ver()),
        "platform": platform.platform(),
        "python_build": list(platform.python_build()),
        "python_compiler": platform.python_compiler(),
    }


def profile_errors(manifest, expected, installed, runtime):
    errors = []
    for key in ("python", "implementation", "system", "machine"):
        if runtime[key] != manifest[key]:
            errors.append(f"{key}: expected {manifest[key]}, found {runtime[key]}")
    libc, version = runtime["libc"]
    minimum = tuple(map(int, manifest["minimum_glibc"].split(".")))
    if libc != "glibc" or not re.fullmatch(r"\d+(?:\.\d+)+", version):
        errors.append("A recognized glibc version is required")
    elif tuple(map(int, version.split("."))) < minimum:
        errors.append("glibc is older than the profile minimum")
    for name in sorted(expected.keys() | installed.keys()):
        if expected.get(name) != installed.get(name):
            errors.append(f"{name}: expected {expected.get(name)}, found {installed.get(name)}")
    return errors


def main():
    try:
        folder = ROOT / "requirements"
        paths = [folder / name for name in (
            "environment-linux-py312.json", "core-linux-py312.lock", "dev-linux-py312.lock"
        )]
        manifest = json.loads(paths[0].read_text())
        expected = verify_inventory(
            manifest, read_pins(paths[1].read_text()),
            read_pins(paths[2].read_text(), development=True),
        )
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        expected[normalize(project["name"])] = project["version"]
        installed = installed_versions(
            (dist.metadata["Name"], dist.version)
            for dist in importlib.metadata.distributions()
        )
        runtime = runtime_snapshot()
        errors = profile_errors(manifest, expected, installed, runtime)
        print(json.dumps({
            "profile": manifest["profile"], "runtime": runtime,
            "installed": dict(sorted(installed.items())),
            "input_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in paths},
            "errors": errors,
        }, indent=2))
        return int(bool(errors))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Environment verification failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
