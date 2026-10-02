"""Actual clean-checkout and locked-environment observations; no supplied identities."""

import json
import subprocess
import sys
from pathlib import Path

from .manifest import digest, fail, read_bytes

SOURCE_ROOT = Path(__file__).resolve().parents[3]
LOCK_NAMES = ("core-linux-py312.lock", "dev-linux-py312.lock", "environment-linux-py312.json")


def git(*args):
    try:
        result = subprocess.run(
            ["git", "-C", str(SOURCE_ROOT), *args], capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        fail("RUN_SOURCE", "Git observation is unavailable or exceeded its time cap.")
    if result.returncode:
        fail("RUN_SOURCE", "Cannot inspect the executing package's Git checkout.")
    return result.stdout


def source_snapshot():
    root = git("rev-parse", "--show-toplevel").decode().strip()
    if Path(root).resolve() != SOURCE_ROOT:
        fail("RUN_SOURCE", "The executing package must belong to this checkout root.")
    revision = git("rev-parse", "HEAD").decode().strip()
    if git("status", "--porcelain", "--untracked-files=all"):
        fail("RUN_DIRTY_SOURCE", "Commit reviewed public changes before recording a run.")
    files = {}
    for path in sorted((SOURCE_ROOT / "src/aura").rglob("*.py")):
        files[str(path.relative_to(SOURCE_ROOT))] = digest(read_bytes(path))
    tracked = set(git("ls-files", "--", "src/aura").decode().splitlines())
    if not set(files).issubset(tracked):
        fail("RUN_SOURCE", "Executing package contains source absent from Git history.")
    if not files or len(files) > 256:
        fail("RUN_SOURCE", "Unexpected source inventory size.")
    # Recheck to reject ordinary edits during observation.
    if git("status", "--porcelain", "--untracked-files=all") or (
        git("rev-parse", "HEAD").decode().strip() != revision
    ):
        fail("RUN_SOURCE_CHANGED", "Source changed during observation.")
    return {"revision": revision, "dirty": False, "patch_sha256": None,
            "package_files_sha256": files}


def capture():
    source = source_snapshot()
    locks = {name: read_bytes(SOURCE_ROOT / "requirements" / name) for name in LOCK_NAMES}
    try:
        result = subprocess.run(
            [sys.executable, str(SOURCE_ROOT / "scripts/verify_environment.py")],
            capture_output=True, timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        fail("RUN_ENVIRONMENT", "Environment observation is unavailable or exceeded its time cap.")
    if result.returncode:
        fail("RUN_ENVIRONMENT", "The executing interpreter does not match ENV-1.0.")
    environment = json.loads(result.stdout)
    if environment["errors"] or environment["input_sha256"] != {
        name: digest(data) for name, data in locks.items()
    }:
        fail("RUN_ENVIRONMENT", "Environment or lock observations disagree.")
    if source_snapshot() != source:
        fail("RUN_SOURCE_CHANGED", "Source changed during environment observation.")
    return source, environment, locks
