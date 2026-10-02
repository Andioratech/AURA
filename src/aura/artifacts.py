"""Bounded read-only SHA-256 checks of explicitly supplied local regular files."""

import hashlib
import os
import re
import stat
from pathlib import Path

from aura.errors import IntegrityError, InvalidInputError

CHUNK_BYTES = 64 * 1024


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def file_sha256(path: str | Path, *, max_bytes: int) -> str:
    """Hash observed bytes; detect ordinary changes, not adversarial filesystem races.

    Symlinks to regular files are allowed. No URI resolution or file writes occur.
    The explicit cap bounds bytes read; it is not a wall-time or storage-speed cap.
    """
    if type(max_bytes) is not int or max_bytes < 0:
        raise InvalidInputError("BYTE_LIMIT", "/max_bytes", "Expected a nonnegative integer cap.")
    # Nonblocking open avoids hanging on a FIFO before its type can be checked.
    if not hasattr(os, "O_NONBLOCK"):
        raise InvalidInputError("PLATFORM_UNSUPPORTED", "", "Nonblocking file open is required.")
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise IntegrityError("ARTIFACT_TYPE", "", "Expected a regular file.")
        if before.st_size > max_bytes:
            raise IntegrityError("ARTIFACT_LIMIT", "", "File exceeds the supplied byte cap.")
        digest, count = hashlib.sha256(), 0
        while True:
            chunk = os.read(descriptor, min(CHUNK_BYTES, max_bytes - count + 1))
            if not chunk:
                break
            count += len(chunk)
            if count > max_bytes:
                raise IntegrityError("ARTIFACT_LIMIT", "", "File exceeds the supplied byte cap.")
            digest.update(chunk)
        after = os.fstat(descriptor)
        current = os.stat(path)
        if count != before.st_size or _signature(before) != _signature(after) or (
            _signature(after) != _signature(current)
        ):
            raise IntegrityError("ARTIFACT_CHANGED", "", "File changed while being hashed.")
        return digest.hexdigest()
    finally:
        os.close(descriptor)


def verify_file(path: str | Path, expected_sha256: str, *, max_bytes: int) -> str:
    """Compare actual bytes against a separately retained lowercase SHA-256 digest."""
    if type(expected_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise InvalidInputError("DIGEST_FORMAT", "/sha256", "Expected 64 lowercase hex digits.")
    actual = file_sha256(path, max_bytes=max_bytes)
    if actual != expected_sha256:
        raise IntegrityError("HASH_MISMATCH", "/sha256", "File content differs from expected digest.")
    return actual
