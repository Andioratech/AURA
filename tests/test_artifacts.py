"""Raw file known answers, bounded reads and tamper/change detection."""

import hashlib
import os
from pathlib import Path

import pytest

import aura.artifacts as artifact_module
from aura.artifacts import CHUNK_BYTES, file_sha256, verify_file
from aura.errors import IntegrityError, InvalidInputError

ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


@pytest.mark.parametrize("data,expected", [(b"", EMPTY), (b"abc", ABC)])
def test_standard_sha256_known_answers(tmp_path, data, expected):
    path = tmp_path / "input.bin"
    path.write_bytes(data)
    original = path.stat()
    assert file_sha256(path, max_bytes=len(data)) == expected
    assert verify_file(path, expected, max_bytes=len(data)) == expected
    assert path.read_bytes() == data
    assert path.stat().st_mtime_ns == original.st_mtime_ns
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("data", [b"abd", b"ab", b"abc\n", b""])
def test_changed_or_truncated_file_fails(tmp_path, data):
    path = tmp_path / "input.bin"
    path.write_bytes(data)
    with pytest.raises(IntegrityError) as caught:
        verify_file(path, ABC, max_bytes=10)
    assert (caught.value.code, caught.value.path) == ("HASH_MISMATCH", "/sha256")
    assert path.read_bytes() == data


def test_environment_lock_digest_ignores_location_not_bytes(tmp_path):
    a, b = tmp_path / "environment.lock", tmp_path / "moved.lock"
    a.write_bytes(b"abc")
    b.write_bytes(b"abc")
    assert file_sha256(a, max_bytes=3) == file_sha256(b, max_bytes=3) == ABC
    b.write_bytes(b"abd")
    with pytest.raises(IntegrityError, match="HASH_MISMATCH"):
        verify_file(b, ABC, max_bytes=3)


@pytest.mark.parametrize("cap", [-1, True, 1.5, None, "3"])
def test_invalid_caps_rejected_before_open(tmp_path, cap):
    with pytest.raises(InvalidInputError) as caught:
        file_sha256(tmp_path / "absent", max_bytes=cap)
    assert (caught.value.code, caught.value.path) == ("BYTE_LIMIT", "/max_bytes")


@pytest.mark.parametrize("digest", ["a" * 63, "A" * 64, "g" * 64, "a" * 64 + "\n", None, True])
def test_invalid_expected_digest_rejected_before_open(tmp_path, digest):
    with pytest.raises(InvalidInputError) as caught:
        verify_file(tmp_path / "absent", digest, max_bytes=10)
    assert (caught.value.code, caught.value.path) == ("DIGEST_FORMAT", "/sha256")


def test_missing_file_retains_io_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        verify_file(tmp_path / "absent", ABC, max_bytes=10)


def test_limit_rejects_before_content_read(tmp_path, monkeypatch):
    path = tmp_path / "large"
    path.write_bytes(b"abcd")
    monkeypatch.setattr(os, "read", lambda *args: pytest.fail("Oversized file was read"))
    with pytest.raises(IntegrityError, match="ARTIFACT_LIMIT"):
        file_sha256(path, max_bytes=3)


def test_streaming_uses_bounded_chunks(tmp_path, monkeypatch):
    data = b"abc" * CHUNK_BYTES
    path = tmp_path / "large"
    path.write_bytes(data)
    original = os.read
    sizes = []

    def read(fd, count):
        sizes.append(count)
        return original(fd, count)

    monkeypatch.setattr(os, "read", read)
    assert file_sha256(path, max_bytes=len(data)) == hashlib.sha256(data).hexdigest()
    assert len(sizes) >= 4 and max(sizes) <= CHUNK_BYTES


@pytest.mark.parametrize("kind", ["directory", "fifo"])
def test_special_file_rejection_without_blocking(tmp_path, kind):
    path = tmp_path / "special"
    if kind == "directory":
        path.mkdir()
    else:
        os.mkfifo(path)
    with pytest.raises(IntegrityError, match="ARTIFACT_TYPE"):
        file_sha256(path, max_bytes=10)


def test_symlink_to_regular_file_uses_content(tmp_path):
    source, link = tmp_path / "source", tmp_path / "link"
    source.write_bytes(b"abc")
    link.symlink_to(source)
    assert file_sha256(link, max_bytes=3) == ABC


@pytest.mark.parametrize("mode", ["rewrite", "replace", "grow", "remove"])
def test_changes_during_read_are_not_accepted(tmp_path, monkeypatch, mode):
    path = tmp_path / "input"
    path.write_bytes(b"abc")
    original = os.read
    touched = False

    def read(fd, count):
        nonlocal touched
        chunk = original(fd, count)
        if not touched:
            touched = True
            if mode == "rewrite":
                path.write_bytes(b"abd")
            elif mode == "replace":
                other = tmp_path / "replacement"
                other.write_bytes(b"abc")
                other.replace(path)
            elif mode == "grow":
                with path.open("ab") as stream:
                    stream.write(b"d")
            else:
                path.unlink()
        return chunk

    monkeypatch.setattr(os, "read", read)
    if mode == "remove":
        with pytest.raises(FileNotFoundError):
            file_sha256(path, max_bytes=3)
    else:
        with pytest.raises(IntegrityError) as caught:
            file_sha256(path, max_bytes=3)
        assert caught.value.code == ("ARTIFACT_LIMIT" if mode == "grow" else "ARTIFACT_CHANGED")


def test_same_size_rewrite_is_detected_when_stat_signature_is_coarse(tmp_path, monkeypatch):
    path = tmp_path / "input"
    path.write_bytes(b"abc")
    original = os.read
    touched = False

    def read(fd, count):
        nonlocal touched
        chunk = original(fd, count)
        if not touched:
            touched = True
            path.write_bytes(b"abd")
        return chunk

    monkeypatch.setattr(artifact_module, "_signature", lambda _info: (1, 2, 3, 4, 5))
    monkeypatch.setattr(os, "read", read)
    with pytest.raises(IntegrityError, match="ARTIFACT_CHANGED"):
        file_sha256(path, max_bytes=3)


def test_descriptors_closed_after_rejection(tmp_path, monkeypatch):
    path = tmp_path / "input"
    path.write_bytes(b"abc")
    original = os.close
    closed = []

    def close(fd):
        closed.append(fd)
        original(fd)

    monkeypatch.setattr(os, "close", close)
    with pytest.raises(IntegrityError, match="ARTIFACT_LIMIT"):
        file_sha256(path, max_bytes=2)
    assert len(closed) == 1
    with pytest.raises(OSError):
        os.fstat(closed[0])


def test_no_nonblocking_support_is_explicit(tmp_path, monkeypatch):
    monkeypatch.delattr(os, "O_NONBLOCK")
    with pytest.raises(InvalidInputError, match="PLATFORM_UNSUPPORTED"):
        file_sha256(Path(tmp_path) / "missing", max_bytes=1)
