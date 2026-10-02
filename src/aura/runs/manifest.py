"""Bounded bundle IO and exclusive publication for local lifecycle records."""

import hashlib
import json
import os
import re
import stat
import uuid
from pathlib import Path

from aura.errors import IntegrityError
from aura.schema.quantities import check_json_tree

FILE_LIMIT = 1024 * 1024


def fail(code, message):
    raise IntegrityError(code, "", message)


def read_bytes(path, limit=FILE_LIMIT):
    """Read a stable regular file without waiting for FIFO writers; reject symlinks."""
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            fail("RUN_FILE_LIMIT", "Expected a regular file within the byte limit.")
        chunks, size = [], 0
        while chunk := os.read(fd, min(65536, limit - size + 1)):
            size += len(chunk)
            if size > limit:
                fail("RUN_FILE_LIMIT", "File exceeds the byte limit.")
            chunks.append(chunk)
        after = os.fstat(fd)
        current = os.stat(path, follow_symlinks=False)
        signature = lambda info: (info.st_dev, info.st_ino, info.st_size,
                                  info.st_mtime_ns, info.st_ctime_ns)
        if size != before.st_size or signature(before) != signature(after) or (
            signature(after) != signature(current)
        ):
            fail("RUN_FILE_CHANGED", "File changed while being read.")
        return b"".join(chunks)
    finally:
        os.close(fd)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(data):
    check_json_tree(data)
    payload = (json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()
    if len(payload) > FILE_LIMIT:
        fail("RUN_FILE_LIMIT", "Encoded record exceeds the byte limit.")
    return payload


def decode(payload):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                fail("DUPLICATE_KEY", "Duplicate bundle JSON key.")
            value[key] = item
        return value
    value = json.loads(payload, object_pairs_hook=pairs)
    check_json_tree(value)
    return value


def safe_file(folder, name):
    if type(name) is not str or re.fullmatch(r"[a-z][a-z0-9_.-]*", name) is None:
        fail("RUN_PATH", "Bundle references must be simple local filenames.")
    path = Path(folder) / name
    if path.is_symlink():
        fail("RUN_PATH", "Bundle symlinks are not supported.")
    return path


def publish(folder, name, data):
    """Atomically expose a complete file without replacing an existing name."""
    target = safe_file(folder, name)
    pending = Path(folder) / (".pending-" + uuid.uuid4().hex)
    try:
        with pending.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(pending, target)  # Atomic and fails if target already exists.
        directory = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        pending.unlink(missing_ok=True)
    return {"uri": name, "sha256": digest(data)}


def verified_bytes(folder, ref):
    if type(ref) is not dict or set(ref) != {"uri", "sha256"}:
        fail("RUN_REFERENCE", "Malformed artifact reference.")
    data = read_bytes(safe_file(folder, ref["uri"]))
    if digest(data) != ref["sha256"]:
        fail("HASH_MISMATCH", "Stored artifact differs from its recorded digest.")
    return data
