#!/usr/bin/env python3
"""Freeze one owned Zig scanner-capture source change without running Zig."""

from __future__ import annotations

import argparse
import builtins
import hashlib
import importlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SCHEMA = "rebar-phase2-owned-zig-scanner-capture-source-repair-v1"
SOURCE_PATH = "tools/apply_owned_zig_scanner_capture_source_repair_v1.py"
PROTOCOL_PATH = "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md"
CONTRACT_PATH = "oracle/phase2/zig-scanner-capture-source-repair-v1.json"
MAX_OWNER_BYTES = 64 * 1024 * 1024
COMPILER_PARENT = "zig-x86_64-linux-0.16.0"
COMPILER_SHA256 = "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
COMPILER_BYTES = 172641672
PRIVATE_ROOT_PREFIX = "rebar-phase2-zig-scanner-capture-source-build-v1-"
ORIGINAL_PATH = "candidates/zig/py_bridge.c"
ORIGINAL_SHA256 = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
ORIGINAL_BYTES = 173026
ENGINE_PATH = "candidates/zig/mini_regex.zig"
ENGINE_SHA256 = "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
ENGINE_BYTES = 186915
ADAPTER_PATH = "candidates/zig_candidate.py"
ADAPTER_SHA256 = "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862"
ADAPTER_BYTES = 68422
DERIVED_SHA256 = "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
DERIVED_BYTES = 173082
SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)
SUPPORT = {
    "GOAL.md": "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    "oracle/phase1/p0-completeness-v1.json": "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    "oracle/phase1/P0-COMPLETENESS-V1.md": "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
    "tools/verify_p0_completeness_v1.py": "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
    "docs/evidence/candidate-current-overview-v19.inputs.json": "8f1eb51ff477f0b59934ee503d9bf795f472fd6674180e2af244c7ad4504560c",
    "docs/evidence/candidate-current-overview-v19.json": "504de87d091c555eb53d664fbfaaa70660ff4dd2f9abc22803246f8a5e18287f",
    "docs/evidence/candidate-current-overview-v20.inputs.json": "bf09019d4a8df9ab5519a0b6bbbe9c4aaa8574dbcc4a9eafc1b424ba1961f021",
    "docs/evidence/candidate-current-overview-v20.json": "89e89c27a9295bc5c2f0ddb1141bb9969b1fda32a82c546e4afd55bc9c758544",
    "docs/evidence/candidate-current-overview-v21.inputs.json": "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
    "docs/evidence/candidate-current-overview-v21.json": "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
    "docs/evidence/candidate-current-overview-v21.svg": "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
    "tools/render_candidate_current_overview_v21.py": "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
    "tools/run_owned_six_family_original_p0_producer_v3.py": "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md": "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
    "oracle/phase2/six-family-p0-producer-v3.json": "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
    "toolchains/zig-0.16.0.lock.json": "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
    "experiments/rust_public_practice_v1/zig-scanner-verbose-comments-v1-phase2-v6-verbose-publication-receipt.json": "3e8d850af3ad191c24b92182ed4e694c44c23716b37c607a31c50c45659428d9",
    "experiments/rust_public_practice_v1/zig-managed-buffer-lifetime-v1-phase2-v6-managed-publication-receipt.json": "d28c95236df9b19e5ab27a1174d5b8616cf2ba22394314ee2dcb78c13034d516",
    "experiments/rust_public_practice_v1/zig-public-type-identity-serialization-v1-phase2-v6-types-publication-receipt.json": "82f96615d0894b99ed1316df6fde2c713e3d7d4b19f18cf71a7e97e82a2352df",
    "experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v2-phase2-v6-substitution-publication-receipt.json": "9b4c4daaf775bb585a3dcfbe693b91c14d49eb09aafd79360fb41ed5cd083791",
    "experiments/rust_public_practice_v1/zig-shape-changing-buffer-semantics-v2-phase2-v6-shape-publication-receipt.json": "e020e83774064cb9c9c9f9a70229ad3bcd04b0e417942317be4fbdb33f365ba9",
}
FUNCTION_ANCHOR = b"static int zig_scanner_project_match("
NEXT_FUNCTION_ANCHOR = b"static ZigMatch *zig_iterator_record("
LOCAL_PROJECTION = b"""    for (size_t logical = 1; logical <= iterator->groups; logical++) {
        if (logical > iterator->native_groups - outer) break;
        size_t actual = outer + logical;
        if (actual >= next_outer) break;
        if (begins[actual] < 0) continue;
        if (ends[actual] < begins[actual]) {
            PyErr_SetString(PyExc_RuntimeError,
                            "invalid owned Zig scanner local capture");
            return 0;
        }
        match->spans[logical] = begins[actual];
        match->spans[exposed_stride + logical] = ends[actual];
    }
"""
OLD_BLOCK = b"""    size_t branch_group = active + 1;
    match->spans[branch_group] = begins[0];
    match->spans[exposed_stride + branch_group] = ends[0];
    match->lastindex = (Py_ssize_t)branch_group;
"""
NEW_BLOCK = b"""    size_t branch_group = active + 1;
    if (match->spans[branch_group] < 0) {
        match->spans[branch_group] = begins[0];
        match->spans[exposed_stride + branch_group] = ends[0];
    }
    match->lastindex = (Py_ssize_t)branch_group;
"""
OLD_BLOCK_SHA256 = "42009e889c83ee06194f14223b629bb221326ce7a3ebf3efe09f5d1a76344978"
NEW_BLOCK_SHA256 = "7a7fa3a9a16d9dae07e74845984bbd36d17309c1f06ddb091d6d3986b4e27177"


class GateError(Exception):
    """The exact frozen Zig scanner-source obligation failed."""


def require(condition: object, reason: str) -> None:
    if condition is not True:
        raise GateError(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError,
            RecursionError) as error:
        raise GateError("require one finite canonical Zig source document") from error


def valid_digest(value: object, label: str) -> str:
    require(isinstance(value, str) and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            f"invalid {label} SHA-256")
    return value


def relative_parts(value: object) -> tuple[str, ...]:
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "invalid canonical relative Zig owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value,
            "reject a noncanonical or absolute source owner")
    require(0 < len(parsed.parts) <= 12
            and all(part not in ("", ".", "..") for part in parsed.parts),
            "reject an escaping source-owner component")
    return parsed.parts


def checked_read(relative: str, expected: str,
                 expected_bytes: int | None = None) -> bytes:
    parts = relative_parts(relative)
    valid_digest(expected, relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and 0 <= before.st_size <= MAX_OWNER_BYTES,
                    "reject a nonregular or oversized Zig context owner")
            if expected_bytes is not None:
                require(before.st_size == expected_bytes,
                        "authenticated owner size changed")
            chunks: list[bytes] = []
            total = 0
            while True:
                part = os.read(descriptor, min(1024 * 1024,
                                               MAX_OWNER_BYTES + 1 - total))
                if not part:
                    break
                total += len(part)
                require(total <= MAX_OWNER_BYTES, "owner exceeded its hard byte bound")
                chunks.append(part)
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns),
                    "owner changed during a same-inode source read")
            result = b"".join(chunks)
            require(len(result) == before.st_size
                    and sha256(result) == expected,
                    f"authenticated owner digest changed: {relative}")
            return result
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def strict_json(data: bytes, label: str) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        value: dict[str, object] = {}
        for key, item in pairs:
            require(key not in value, f"duplicate JSON key in {label}")
            value[key] = item
        return value

    try:
        value = json.loads(
            data.decode("utf-8", "strict"), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GateError(f"nonfinite JSON value in {label}")),
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise GateError(f"invalid authenticated JSON: {label}") from error
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def repaired_source(source: bytes, original_digest: str,
                    original_bytes: int, *, frozen: bool = True) -> bytes:
    require(isinstance(source, bytes) and len(source) == original_bytes
            and sha256(source) == original_digest,
            "the original Zig scanner bridge is not the pinned source")
    require(sha256(OLD_BLOCK) == OLD_BLOCK_SHA256 and len(OLD_BLOCK) == 190
            and sha256(NEW_BLOCK) == NEW_BLOCK_SHA256
            and len(NEW_BLOCK) == 246,
            "the exact unique Zig scanner source blocks changed")
    require(source.count(FUNCTION_ANCHOR) == 1
            and source.count(NEXT_FUNCTION_ANCHOR) == 1,
            "the Zig scanner function must have one unambiguous boundary")
    require(source.count(OLD_BLOCK) == 1 and source.count(NEW_BLOCK) == 0,
            "require exactly one original and no pre-applied scanner block")
    start = source.index(FUNCTION_ANCHOR)
    finish = source.index(NEXT_FUNCTION_ANCHOR, start + len(FUNCTION_ANCHOR))
    offset = source.index(OLD_BLOCK)
    require(start < offset < finish,
            "the owned scanner repair escaped its one projection function")
    function = source[start:finish]
    require(function.count(LOCAL_PROJECTION) == 1
            and function.index(LOCAL_PROJECTION) < function.index(OLD_BLOCK),
            "preserve every original local-capture range and error check")
    require(function.count(b"match->lastindex = (Py_ssize_t)branch_group;") == 1,
            "preserve the unique original scanner branch lastindex")
    derived = source[:offset] + NEW_BLOCK + source[offset + len(OLD_BLOCK):]
    require(derived[:offset] == source[:offset]
            and derived[offset + len(NEW_BLOCK):]
            == source[offset + len(OLD_BLOCK):],
            "reject every change outside the sole anchored scanner block")
    require(derived.count(OLD_BLOCK) == 0 and derived.count(NEW_BLOCK) == 1,
            "require exactly one privately derived scanner source block")
    repaired_finish = derived.index(NEXT_FUNCTION_ANCHOR, start)
    fixed = derived[start:repaired_finish]
    require(fixed.count(LOCAL_PROJECTION) == 1
            and fixed.index(LOCAL_PROJECTION) < fixed.index(NEW_BLOCK),
            "do not discard an already projected local capture")
    require(fixed.count(b"if (match->spans[branch_group] < 0)") == 1
            and fixed.count(b"match->lastindex = (Py_ssize_t)branch_group;") == 1
            and fixed.index(b"if (match->spans[branch_group] < 0)")
            < fixed.index(b"match->lastindex = (Py_ssize_t)branch_group;"),
            "only an unset branch slot may receive the whole-match fallback")
    for marker in (
        b"PyObject_GetBuffer(", b"PyBuffer_Release(", b"PyBUF_SIMPLE",
        b"PyCallable_Check(", b"zig_prepare_expand_template(",
        b"zig_match_expand(", b"zig_live_exporter_subn(",
        b"bridge_generic_subn(", b"PyImport_ImportModule",
        b"import re", b"from re ", b"import _sre",
        b"dlopen(", b"pcre", b"oniguruma", b"hyperscan",
        b"candidates.rust", b"candidates.vm_candidate",
        b"candidates.cpp", b"candidates.go", b"candidates.fortran",
    ):
        require(source.count(marker) == derived.count(marker),
                "reject changed buffers, other semantics, or regex delegation")
    if frozen:
        require(original_digest == ORIGINAL_SHA256
                and original_bytes == ORIGINAL_BYTES
                and sha256(derived) == DERIVED_SHA256
                and len(derived) == DERIVED_BYTES,
                "the derived scanner is not the independently frozen owner")
    return derived


class SourceOnlyBoundary:
    """Prevent real filesystem, process, import, network, and clock effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def forbidden(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GateError(f"source-only Zig boundary: {name}")

        self.saved.append((owner, name, original))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, names in (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "remove", "unlink", "replace", "rename",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "mkdir", "unlink", "rename", "replace",
                    "stat", "lstat", "resolve")),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (threading.Thread, ("start",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (importlib, ("import_module",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "thread_time", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object,
                 _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def private_parts(value: object) -> tuple[str, ...]:
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "invalid private Zig scanner snapshot")
    parsed = PurePosixPath(value)
    require(parsed.is_absolute() and str(parsed) == value,
            "require an exact absolute private scanner snapshot")
    parts = parsed.parts
    require(len(parts) == 5 and parts[1] == "tmp"
            and parts[2].startswith(PRIVATE_ROOT_PREFIX)
            and len(parts[2]) > len(PRIVATE_ROOT_PREFIX)
            and all(item.isascii() and (item.isalnum() or item in "-_")
                    for item in parts[2])
            and parts[3] in ("reference-a", "reference-b")
            and parts[4] == "source",
            "reject a repository, unsafe, cross-family, or reused phase root")
    return parts


def sample_source() -> bytes:
    return (
        b"/* wholly synthetic owned Zig scanner */\n"
        + FUNCTION_ANCHOR + b"void) {\n"
        + LOCAL_PROJECTION + OLD_BLOCK + b"    return 1;\n}\n"
        + NEXT_FUNCTION_ANCHOR + b"void) { return NULL; }\n"
    )


def self_test() -> dict:
    accepted = 0
    rejected = 0
    sample = sample_source()
    sample_hash = sha256(sample)
    with SourceOnlyBoundary() as boundary:
        derived = repaired_source(sample, sample_hash, len(sample), frozen=False)
        controls = (
            (derived.count(NEW_BLOCK) == 1, "one derived scanner block"),
            (derived.count(OLD_BLOCK) == 0, "remove exactly the old block"),
            (sha256(OLD_BLOCK) == OLD_BLOCK_SHA256, "original exact block digest"),
            (sha256(NEW_BLOCK) == NEW_BLOCK_SHA256, "derived exact block digest"),
            (len(OLD_BLOCK) == 190, "original exact block size"),
            (len(NEW_BLOCK) == 246, "derived exact block size"),
            (derived.count(LOCAL_PROJECTION) == 1, "preserve capture range checks"),
            (derived.index(LOCAL_PROJECTION) < derived.index(NEW_BLOCK),
             "capture projection precedes the conditional fallback"),
            (derived.count(b"if (match->spans[branch_group] < 0)") == 1,
             "populate only an unset branch slot"),
            (derived.count(b"match->lastindex = (Py_ssize_t)branch_group;") == 1,
             "preserve scanner branch selection"),
            (derived.index(b"if (match->spans[branch_group] < 0)")
             < derived.index(b"match->lastindex = (Py_ssize_t)branch_group;"),
             "preserve original branch lastindex order"),
            (derived[:derived.index(NEW_BLOCK)]
             == sample[:sample.index(OLD_BLOCK)], "preserve every prefix byte"),
            (derived[derived.index(NEW_BLOCK) + len(NEW_BLOCK):]
             == sample[sample.index(OLD_BLOCK) + len(OLD_BLOCK):],
             "preserve every suffix byte"),
            (derived.count(FUNCTION_ANCHOR) == 1,
             "preserve unique scanner projection ownership"),
            (derived.count(NEXT_FUNCTION_ANCHOR) == 1,
             "preserve the following original match function"),
            (private_parts("/tmp/" + PRIVATE_ROOT_PREFIX
                           + "synthetic/reference-a/source")[3] == "reference-a",
             "recognize only the first owned private phase"),
            (private_parts("/tmp/" + PRIVATE_ROOT_PREFIX
                           + "synthetic/reference-b/source")[3] == "reference-b",
             "recognize only the second owned private phase"),
        )
        for valid, label in controls:
            require(valid, f"synthetic Zig source control failed: {label}")
            accepted += 1

        def reject(operation: object, label: str) -> None:
            nonlocal rejected
            try:
                operation()  # type: ignore[operator]
            except (GateError, OSError, ValueError, TypeError,
                    OverflowError, UnicodeError):
                rejected += 1
            else:
                raise GateError(f"accepted hostile Zig source control: {label}")

        changed = {
            "wrong original digest": (sample, "0" * 64, len(sample)),
            "wrong original byte count": (sample, sample_hash, len(sample) + 1),
            "missing original projection":
                (sample.replace(OLD_BLOCK, b"/* missing */\n"), None, None),
            "duplicate original projection":
                (sample.replace(OLD_BLOCK, OLD_BLOCK + OLD_BLOCK), None, None),
            "already repaired projection":
                (sample.replace(OLD_BLOCK, NEW_BLOCK), None, None),
            "missing scanner function":
                (sample.replace(FUNCTION_ANCHOR, b"unowned_projection("), None, None),
            "duplicate scanner function": (FUNCTION_ANCHOR + sample, None, None),
            "missing following function":
                (sample.replace(NEXT_FUNCTION_ANCHOR, b"unowned_match("), None, None),
            "duplicate following function":
                (sample + NEXT_FUNCTION_ANCHOR, None, None),
            "removed capture range checks":
                (sample.replace(LOCAL_PROJECTION, b"/* no checks */\n"), None, None),
            "duplicate capture range checks":
                (sample.replace(LOCAL_PROJECTION,
                                LOCAL_PROJECTION + LOCAL_PROJECTION), None, None),
            "projection outside the scanner":
                (OLD_BLOCK + sample.replace(OLD_BLOCK, b"/* moved */\n"),
                 None, None),
            "falsely frozen synthetic owner": (sample, sample_hash, len(sample)),
        }
        for label, (source, digest, size) in changed.items():
            digest = sha256(source) if digest is None else digest
            size = len(source) if size is None else size
            reject(lambda raw=source, pin=digest, count=size,
                   exact=label == "falsely frozen synthetic owner":
                   repaired_source(raw, pin, count, frozen=exact), label)
        for value in ("", "/", "/tmp", "/home/dev-user/src/rebar",
                      "/tmp/rebar-phase2-zig-scanner-capture-source-build-v1-",
                      "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-c/source",
                      "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-a/native",
                      "/tmp/" + PRIVATE_ROOT_PREFIX + "x/../source",
                      "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-a/source/",
                      "/tmp/rebar-phase2-rust-source-build-v1-x/reference-a/source",
                      "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-a/source/extra"):
            reject(lambda item=value: private_parts(item),
                   "unsafe or cross-family private snapshot")
        for value in ("", "/", "../owner", "a/../owner", "a/./owner",
                      "a//owner", "./owner", "a/", "x" * 513,
                      "/home/dev-user/src/rebar/candidates/zig/py_bridge.c"):
            reject(lambda item=value: relative_parts(item),
                   "noncanonical source-owner path")
        for value in ("", "0" * 63, "0" * 65, "F" * 64, "g" * 64):
            reject(lambda item=value: valid_digest(item, "synthetic"),
                   "hostile source-owner digest")
        reject(lambda: strict_json(b'{"x":1,"x":2}', "synthetic"),
               "duplicate source-contract JSON key")
        reject(lambda: strict_json(b'{"x":NaN}', "synthetic"),
               "nonfinite source-contract JSON")
        reject(lambda: strict_json(b"[]", "synthetic"),
               "nonobject source-contract JSON")
        conflicting: dict[str, str] = {}
        discover_evidence(
            {"path": "oracle/phase2/evidence/synthetic.json",
             "sha256": "0" * 64}, conflicting,
        )
        reject(lambda: discover_evidence(
            {"path": "oracle/phase2/evidence/synthetic.json",
             "sha256": "1" * 64}, conflicting),
            "conflicting authenticated historical evidence")
        probes = (
            (lambda: builtins.open("/tmp/forbidden"), "built-in filesystem"),
            (lambda: io.open("/tmp/forbidden"), "I/O filesystem"),
            (lambda: os.open("/tmp/forbidden", os.O_RDONLY), "file descriptor"),
            (lambda: os.read(0, 1), "real source read"),
            (lambda: os.write(1, b"x"), "source write"),
            (lambda: os.stat("/tmp"), "filesystem stat"),
            (lambda: os.lstat("/tmp"), "symlink traversal"),
            (lambda: os.mkdir("/tmp/forbidden"), "directory creation"),
            (lambda: os.unlink("/tmp/forbidden"), "source deletion"),
            (lambda: os.replace("/tmp/a", "/tmp/b"), "source replacement"),
            (lambda: Path("/tmp/forbidden").read_bytes(), "path read"),
            (lambda: Path("/tmp/forbidden").write_bytes(b"x"), "path write"),
            (lambda: Path("/tmp").resolve(), "path resolution"),
            (lambda: subprocess.run(("true",)), "subprocess"),
            (lambda: subprocess.Popen(("true",)), "native compiler"),
            (lambda: socket.socket(), "network"),
            (lambda: tempfile.mkdtemp(), "private directory"),
            (lambda: tempfile.mkstemp(), "temporary source"),
            (lambda: importlib.import_module("candidates.zig_candidate"),
             "Zig candidate import"),
            (lambda: importlib.import_module("candidates.rust_candidate"),
             "cross-family candidate import"),
            (lambda: importlib.import_module("re"), "stdlib regex import"),
            (lambda: threading.Thread().start(), "worker thread"),
            (lambda: time.perf_counter(), "performance clock"),
            (lambda: time.perf_counter_ns(), "performance nanoclock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.sleep(0), "waiting"),
        )
        for operation, label in probes:
            reject(operation, label)
        blocked = boundary.blocked
    require(blocked == len(probes),
            "every synthetic filesystem, process, import, and clock is blocked")
    return {
        "accepted_source_controls": accepted,
        "blocked_effect_controls": blocked,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "clock_samples": 0,
        "compiler_processes_started": 0,
        "holdout_opened": False,
        "mode": "SOURCE-ONLY SELF-TEST",
        "network_requests": 0,
        "rejected_hostile_controls": rejected,
        "schema": SCHEMA,
        "status": "PASS",
        "workspace_mutations": 0,
    }


def discover_evidence(value: object, output: dict[str, str]) -> None:
    if isinstance(value, dict):
        path = value.get("path")
        digest = value.get("sha256")
        if (isinstance(path, str) and isinstance(digest, str)
                and path.startswith(("oracle/phase2/evidence/",
                                     "experiments/rust_public_practice_v1/"))):
            relative_parts(path)
            valid_digest(digest, "historical evidence")
            require(path not in output or output[path] == digest,
                    "reject a conflicting digest-addressed historical owner")
            output[path] = digest
        for item in value.values():
            discover_evidence(item, output)
    elif isinstance(value, list):
        for item in value:
            discover_evidence(item, output)


def authenticate_compiler() -> dict:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    tmp = os.open("/tmp", flags | os.O_DIRECTORY)
    parent = descriptor = None
    try:
        parent = os.open(COMPILER_PARENT, flags | os.O_DIRECTORY, dir_fd=tmp)
        descriptor = os.open("zig", flags, dir_fd=parent)
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and before.st_size == COMPILER_BYTES
                and before.st_mode & stat.S_IXUSR != 0,
                "the pinned Zig compiler is not the original stable owner")
        hasher = hashlib.sha256()
        read_count = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            read_count += len(chunk)
            require(read_count <= COMPILER_BYTES,
                    "the pinned compiler exceeded its exact frozen size")
            hasher.update(chunk)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns),
                "the pinned compiler changed during authenticated read")
        require(read_count == COMPILER_BYTES
                and hasher.hexdigest() == COMPILER_SHA256,
                "the official stable Zig 0.16.0 compiler digest changed")
        return {
            "bytes": COMPILER_BYTES,
            "path": "/tmp/" + COMPILER_PARENT + "/zig",
            "sha256": COMPILER_SHA256,
            "version": "0.16.0",
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if parent is not None:
            os.close(parent)
        os.close(tmp)


def verify_receipts(protected: dict[str, bytes]) -> None:
    base = "experiments/rust_public_practice_v1/"
    verbose = strict_json(
        protected[base + "zig-scanner-verbose-comments-v1-phase2-v6-verbose-publication-receipt.json"],
        "original Zig verbose scanner failure",
    )
    require(verbose.get("schema")
            == "rebar-independent-scanner-verbose-comments-recorder-v1-durable-candidate-publication-receipt"
            and verbose.get("status") == "PASS"
            and verbose.get("candidate_result_status") == "FAIL"
            and verbose.get("candidate_family") == "zig"
            and verbose.get("case_count") == 2854
            and verbose.get("mismatch_count") == 620
            and verbose.get("mismatches_by_cohort")
            == {"semantic": 620, "tokenizer": 0}
            and verbose.get("mismatches_by_expected_kind") == {
                "continued-comment-empty": 0,
                "continued-comment-unterminated": 0,
                "full-match": 620,
                "prefix-then-fallback": 0,
            }
            and verbose.get("all_mismatches_preserved") is True
            and verbose.get("hidden_cases_read") == 0
            and verbose.get("clock_samples") == 0
            and verbose.get("performance") == "NOT MEASURED",
            "preserve every one of the 620 actual failed scanner witnesses")
    expected = (
        ("zig-managed-buffer-lifetime-v1-phase2-v6-managed-publication-receipt.json",
         "PASS", 1024, 0),
        ("zig-public-type-identity-serialization-v1-phase2-v6-types-publication-receipt.json",
         "FAIL", 6912, 248),
        ("zig-substitution-buffer-semantics-v2-phase2-v6-substitution-publication-receipt.json",
         "FAIL", 5120, 64),
        ("zig-shape-changing-buffer-semantics-v2-phase2-v6-shape-publication-receipt.json",
         "FAIL", 10240, 672),
    )
    for filename, result, cases, mismatches in expected:
        receipt = strict_json(protected[base + filename], filename)
        require(receipt.get("status") == "PASS"
                and receipt.get("candidate_result_status") == result
                and receipt.get("candidate_family") == "zig"
                and receipt.get("case_count") == cases
                and receipt.get("mismatch_count") == mismatches
                and receipt.get("all_mismatches_preserved") is True
                and receipt.get("hidden_cases_read") == 0
                and receipt.get("clock_samples") == 0
                and receipt.get("performance") == "NOT MEASURED",
                "preserve every original Zig passing and failing cohort")
    shape = strict_json(
        protected[base + "zig-shape-changing-buffer-semantics-v2-phase2-v6-shape-publication-receipt.json"],
        "original Zig changing-buffer failure",
    )
    require(shape.get("mismatches_by_api") == {
        "match.expand": 176,
        "module.sub": 112,
        "module.subn": 128,
        "pattern.sub": 128,
        "pattern.subn": 128,
    }, "the scanner-only source change may not erase Match.expand failures")
    substitution = strict_json(
        protected[base + "zig-substitution-buffer-semantics-v2-phase2-v6-substitution-publication-receipt.json"],
        "original Zig substitution failure",
    )
    require(substitution.get("mismatches_by_api") == {
        "match.expand": 0,
        "module.sub": 16,
        "module.subn": 16,
        "pattern.sub": 16,
        "pattern.subn": 16,
    }, "the scanner-only source change may not erase substitution failures")


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None) -> tuple[dict, bytes]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "run the freeze only under isolated stable CPython 3.14.6")
    checked_read(SOURCE_PATH, valid_digest(source_pin, "Zig source tool"))
    checked_read(PROTOCOL_PATH, valid_digest(protocol_pin, "Zig source protocol"))
    protected = {path: checked_read(path, digest)
                 for path, digest in SUPPORT.items()}
    original = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    checked_read(ENGINE_PATH, ENGINE_SHA256, ENGINE_BYTES)
    checked_read(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    derived = repaired_source(original, ORIGINAL_SHA256, ORIGINAL_BYTES)
    compiler = authenticate_compiler()

    p0 = strict_json(protected["oracle/phase1/p0-completeness-v1.json"],
                     "frozen original CPython correctness oracle")
    require(p0.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and p0.get("version") == 1,
            "the original stable CPython compatibility oracle changed")
    denominator = p0.get("denominator")
    require(isinstance(denominator, dict)
            and tuple(denominator.get("counted_suite_ids", ())) == SUITE_IDS
            and denominator.get("final_required_case_execution_denominator") == 31237
            and denominator.get("private_upstream_methods_outside_public_denominator") == 13,
            "preserve all 13 suites, 31,237 cases, and 13 private waivers")
    runtime = p0.get("runtime")
    require(isinstance(runtime, dict)
            and runtime.get("python_implementation") == "CPython"
            and runtime.get("python_version") == "3.14.6"
            and isinstance(runtime.get("executable"), dict)
            and runtime["executable"].get("path") == PYTHON
            and runtime["executable"].get("sha256") == PYTHON_SHA256,
            "preserve the independently pinned stable Python oracle")
    phase_gate = p0.get("phase_gate")
    require(isinstance(phase_gate, dict)
            and phase_gate.get("status") == "PASS"
            and phase_gate.get("all_obligations_mapped") is True
            and phase_gate.get("final_holdout_authorized") is False,
            "the complete original oracle must remain frozen and unopened")

    lock = strict_json(protected["toolchains/zig-0.16.0.lock.json"],
                       "official stable Zig toolchain lock")
    require(lock.get("schema") == "rebar-official-language-toolchain-v1"
            and lock.get("language") == "Zig"
            and lock.get("version") == "0.16.0"
            and lock.get("release_channel") == "stable"
            and lock.get("compiler_sha256") == compiler["sha256"]
            and lock.get("compiler_relative_path")
            == COMPILER_PARENT + "/zig",
            "retain only the genuine pinned stable Zig compiler")

    corrected = strict_json(
        protected["oracle/phase2/six-family-p0-producer-v3.json"],
        "current corrected independent V3 producer freeze",
    )
    require(corrected.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and corrected.get("version") == 3
            and corrected.get("status") == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
            and corrected.get("family_count") == 6
            and corrected.get("source_owner_count") == 25
            and corrected.get("pairwise_shared_semantic_source_count") == 0
            and corrected.get("suite_count") == 13
            and corrected.get("case_execution_denominator") == 31237
            and corrected.get("goal_sha256") == SUPPORT["GOAL.md"],
            "retain the exact corrected, genuinely independent V3 owner closure")
    families = corrected.get("families")
    require(isinstance(families, list) and len(families) == 6,
            "preserve all six distinct first-party source families")
    family_ids: set[str] = set()
    all_sources: set[str] = set()
    zig: dict | None = None
    for family in families:
        require(isinstance(family, dict), "reject a forged native source family")
        identifier = family.get("family")
        require(isinstance(identifier, str) and identifier not in family_ids,
                "reject a repeated independent source family")
        family_ids.add(identifier)
        sources = family.get("sources")
        require(isinstance(sources, list)
                and len(sources) == family.get("owned_source_count")
                and len(sources) > 0,
                "reject an incomplete first-party matching engine")
        for owner in sources:
            require(isinstance(owner, dict), "reject a forged semantic source owner")
            path = owner.get("relative")
            expected = owner.get("sha256")
            size = owner.get("size_bytes")
            require(isinstance(path, str) and path not in all_sources
                    and isinstance(expected, str)
                    and isinstance(size, int) and size >= 0,
                    "reject repeated, cross-family, or missing semantic ownership")
            checked_read(path, expected, size)
            all_sources.add(path)
        if identifier == "zig":
            zig = family
    require(family_ids == {"c", "rust", "zig", "cpp", "go", "fortran"}
            and len(all_sources) == 25
            and isinstance(zig, dict)
            and zig.get("owned_source_count") == 3
            and zig.get("bridge_module") == "candidates._zig_bridge"
            and zig.get("adapter_relative") == ADAPTER_PATH
            and {ORIGINAL_PATH, ENGINE_PATH, ADAPTER_PATH}.issubset(all_sources),
            "the scanner correction must remain one independent Zig family")
    effects = corrected.get("verification_effects")
    require(isinstance(effects, dict)
            and effects.get("actual_candidate_imports") == 0
            and effects.get("actual_candidate_workers") == 0
            and effects.get("actual_source_builds") == 0
            and effects.get("actual_native_activations") == 0
            and effects.get("actual_network_requests") == 0
            and effects.get("actual_subprocesses_started") == 0
            and effects.get("clock_samples") == 0
            and effects.get("hidden_cases_read") == 0
            and effects.get("candidate_qualified_count") == 0
            and effects.get("holdout") == "NOT OPENED"
            and effects.get("performance") == "NOT MEASURED",
            "the corrected V3 producer cannot authorize a candidate or holdout")

    v19_inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v19.inputs.json"],
        "preserved V19 evidence graph",
    )
    v19_summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v19.json"],
        "preserved V19 evidence summary",
    )
    history: dict[str, str] = {}
    discover_evidence(v19_inputs, history)
    discover_evidence(v19_summary, history)
    require(len(history) == 76
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 46
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "preserve exactly 76 genuine V19 history owners, never all JSON links")
    v20_inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v20.inputs.json"],
        "preserved V20 evidence graph",
    )
    v20_summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v20.json"],
        "preserved V20 evidence summary",
    )
    require(v20_inputs.get("all_digest_addressed_history_path_count") == 78
            and v20_inputs.get("repository_evidence_owner_count") == 73
            and v20_summary.get("authenticated_digest_addressed_history_paths") == 78
            and v20_summary.get("repository_evidence_owner_count") == 73,
            "retain the exact original 78-reference V20 history")
    v20_snapshot = v20_summary.get("snapshot")
    require(isinstance(v20_snapshot, dict), "missing original V20 native evidence")
    original_build = v20_snapshot.get("c_v8_repaired_build")
    require(isinstance(original_build, dict)
            and original_build.get("status") == "PASS",
            "preserve the genuine already published native build")
    for role in ("archive", "receipt"):
        owner = original_build.get(role)
        require(isinstance(owner, dict), "missing original additional V20 owner")
        path, digest = owner.get("path"), owner.get("sha256")
        require(isinstance(path, str) and isinstance(digest, str)
                and path.startswith("oracle/phase2/evidence/")
                and path not in history,
                "the two actual V20 owners must be distinct historical evidence")
        valid_digest(digest, "V20 native evidence")
        history[path] = digest
    require(len(history) == 78, "preserve exactly the genuine V20 history")

    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v21.inputs.json"],
        "current V21 evidence graph",
    )
    summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v21.json"],
        "current V21 evidence summary",
    )
    require(inputs.get("schema") == "rebar-candidate-current-overview-v21-inputs"
            and inputs.get("version") == 21
            and inputs.get("repository_evidence_owner_count") == 103
            and inputs.get("all_digest_addressed_history_path_count") == 108
            and inputs.get("preserved_v20_repository_evidence_owner_count") == 73
            and inputs.get("preserved_v20_digest_addressed_history_path_count") == 78
            and inputs.get("new_repaired_c_campaign_repository_evidence_owner_count") == 30
            and inputs.get("current_source_owner_count") == 25
            and inputs.get("current_tested_candidate_family_count") == 5
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("verified_activation_v4_current_active_target_count") == 0
            and inputs.get("suite_count") == 13
            and inputs.get("full_case_denominator") == 31237
            and inputs.get("private_waiver_count") == 13,
            "preserve 103 real owners, 108 history references, and zero qualification")
    campaign = inputs.get("repaired_c_original_campaign")
    require(isinstance(campaign, dict)
            and campaign.get("new_repository_evidence_owner_count") == 30,
            "preserve all thirty additional actual published campaign owners")
    fresh: dict[str, str] = {}
    discover_evidence(campaign, fresh)
    require(len(fresh) == 30 and not (set(fresh) & set(history)),
            "reject invented, duplicated, or omitted V21 history evidence")
    history.update(fresh)
    require(len(history) == 108
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 78
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "authenticate exactly 108 genuine evidence references")
    for path, digest in sorted(history.items()):
        checked_read(path, digest)
    require(summary.get("schema") == "rebar-candidate-current-overview-v21-summary"
            and summary.get("status") == "PASS"
            and summary.get("repository_evidence_owner_count") == 103
            and summary.get("authenticated_digest_addressed_history_paths") == 108
            and summary.get("qualified_candidate_count") == 0
            and summary.get("suite_count") == 13
            and summary.get("full_case_denominator") == 31237,
            "preserve the committed V21 truthful source-and-history summary")
    snapshot = summary.get("snapshot")
    require(isinstance(snapshot, dict)
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 103
            and snapshot.get("all_digest_addressed_history_path_count") == 108
            and snapshot.get("current_source_owner_count") == 25
            and snapshot.get("frozen_independent_engine_family_count") == 6
            and snapshot.get("current_tested_candidate_family_count") == 5
            and snapshot.get("qualified_candidate_count") == 0
            and snapshot.get("verified_activation_v4_current_active_target_count") == 0
            and snapshot.get("zig_actual_semantic_mismatch_count") == 1764
            and snapshot.get("zig_verified_passing_case_executions") == 3583
            and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS,
            "never erase 1,764 original Zig failures or count partial passes")
    zig_gate = snapshot.get("zig_full_gate")
    require(isinstance(zig_gate, dict)
            and zig_gate.get("gate_status") == "FAIL"
            and zig_gate.get("actual_semantic_mismatch_count") == 1764
            and zig_gate.get("qualified_candidate_case_executions") == 0
            and tuple(zig_gate.get("failed_suite_ids", ())) == (
                "scanner_v3", "scanner_verbose_v1", "public_types_v1",
                "substitution_v2", "shape_v2", "public_surface_v19",
                "subinterpreter_v2",
            ),
            "the source-only correction cannot qualify or silently repair Zig")
    for document in (inputs, summary, snapshot):
        require(document.get("final_holdout_opened") is False
                and document.get("final_comparison_cases_generated") is False
                and document.get("final_comparison_planned_case_count") == 4194304
                and document.get("performance") == "NOT MEASURED"
                and document.get("memory") == "NOT MEASURED",
                "never read, generate, or infer the holdout or performance")
    require(summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False,
            "the Zig scanner source freeze cannot start an experiment")
    v3_history = corrected.get("frozen_v21_history")
    require(isinstance(v3_history, dict)
            and v3_history.get("actual_evidence_owner_count") == 103
            and v3_history.get("authenticated_reference_path_count") == 108
            and v3_history.get("new_actual_campaign_owner_count") == 30,
            "retain the independently corrected V3 proof of V21 history")
    v3_owners = v3_history.get("owners")
    require(isinstance(v3_owners, dict), "missing independent V21 owner proof")
    for role, relative in (
        ("source", "tools/render_candidate_current_overview_v21.py"),
        ("inputs", "docs/evidence/candidate-current-overview-v21.inputs.json"),
        ("summary", "docs/evidence/candidate-current-overview-v21.json"),
        ("svg", "docs/evidence/candidate-current-overview-v21.svg"),
    ):
        owner = v3_owners.get(role)
        require(isinstance(owner, dict)
                and owner.get("relative") == relative
                and owner.get("sha256") == SUPPORT[relative],
                "the corrected V3 freeze and V21 overview must agree")
    verify_receipts(protected)
    contract = contract_document(source_pin, protocol_pin)
    if contract_pin is not None:
        actual = checked_read(CONTRACT_PATH,
                              valid_digest(contract_pin, "Zig source contract"))
        require(actual == canonical(contract),
                "reject substituted or noncanonical frozen scanner contract")
    return contract, derived


def contract_document(source_pin: str, protocol_pin: str) -> dict:
    base = "experiments/rust_public_practice_v1/"
    return {
        "schema": SCHEMA,
        "version": 1,
        "phase": "ZIG SCANNER SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "tool": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "oracle": {
            "implementation": "CPython",
            "version": "3.14.6",
            "manifest_path": "oracle/phase1/p0-completeness-v1.json",
            "manifest_sha256": SUPPORT["oracle/phase1/p0-completeness-v1.json"],
            "suite_count": 13,
            "suite_ids": list(SUITE_IDS),
            "case_execution_count": 31237,
            "private_waiver_count": 13,
        },
        "zig_ownership": {
            "independent_family_count": 6,
            "first_party_source_owner_count": 25,
            "zig_source_owner_count": 3,
            "cross_family_semantic_source_count": 0,
            "engine": {
                "path": ENGINE_PATH, "sha256": ENGINE_SHA256,
                "bytes": ENGINE_BYTES, "modified": False,
            },
            "adapter": {
                "path": ADAPTER_PATH, "sha256": ADAPTER_SHA256,
                "bytes": ADAPTER_BYTES, "modified": False,
            },
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_delegation": "FORBIDDEN",
            "candidate_family": "zig",
            "candidate_family_added": False,
        },
        "official_compiler": {
            "version": "0.16.0",
            "path": "/tmp/" + COMPILER_PARENT + "/zig",
            "sha256": COMPILER_SHA256,
            "bytes": COMPILER_BYTES,
            "executed": False,
            "lock_path": "toolchains/zig-0.16.0.lock.json",
            "lock_sha256": SUPPORT["toolchains/zig-0.16.0.lock.json"],
        },
        "repair": {
            "function": "zig_scanner_project_match",
            "original_source": {
                "path": ORIGINAL_PATH, "sha256": ORIGINAL_SHA256,
                "bytes": ORIGINAL_BYTES, "modified": False,
            },
            "old_block": {
                "sha256": OLD_BLOCK_SHA256, "bytes": len(OLD_BLOCK),
                "occurrence_count_before": 1,
                "occurrence_count_after": 0,
            },
            "new_block": {
                "sha256": NEW_BLOCK_SHA256, "bytes": len(NEW_BLOCK),
                "occurrence_count_before": 0,
                "occurrence_count_after": 1,
            },
            "derived_source": {
                "sha256": DERIVED_SHA256,
                "bytes": DERIVED_BYTES,
                "materialized": False,
            },
            "local_capture_overwrite": "PREVENTED BY UNSET-SLOT GUARD ONLY",
            "fallback_without_local_capture": "PRESERVED",
            "branch_lastindex": "UNCHANGED",
            "range_checks": "UNCHANGED",
            "branch_identification": "UNCHANGED",
            "native_last_handling": "UNCHANGED",
            "match_expand": "UNCHANGED",
            "substitution": "UNCHANGED",
            "buffer_acquisition": "UNCHANGED",
            "source_bytes_outside_exact_block": "UNCHANGED",
            "proposed_repair_tested": False,
        },
        "published_history": {
            "overview_version": 21,
            "overview_inputs_path":
                "docs/evidence/candidate-current-overview-v21.inputs.json",
            "overview_inputs_sha256":
                SUPPORT["docs/evidence/candidate-current-overview-v21.inputs.json"],
            "overview_path": "docs/evidence/candidate-current-overview-v21.json",
            "overview_sha256":
                SUPPORT["docs/evidence/candidate-current-overview-v21.json"],
            "authoritative_counted_evidence_owner_count": 103,
            "authenticated_digest_addressed_history_paths": 108,
            "preserved_v19_history_paths": 76,
            "preserved_v20_history_paths": 78,
            "new_v21_evidence_owner_count": 30,
            "oracle_evidence_path_count": 78,
            "experiment_evidence_path_count": 30,
            "current_active_target_count": 0,
            "qualified_candidate_count": 0,
        },
        "preserved_zig_results": {
            "actual_total_semantic_mismatch_count": 1764,
            "candidate_status": "FAILED; NOT QUALIFIED",
            "verified_passing_case_executions": 3583,
            "qualified_case_executions": 0,
            "scanner_verbose_case_count": 2854,
            "scanner_verbose_mismatch_count": 620,
            "scanner_verbose_mismatches_are_still_preserved": True,
            "scanner_verbose_full_match_mismatch_count": 620,
            "scanner_verbose_tokenizer_mismatch_count": 0,
            "scanner_verbose_receipt_path":
                base + "zig-scanner-verbose-comments-v1-phase2-v6-verbose-publication-receipt.json",
            "scanner_verbose_receipt_sha256":
                SUPPORT[base + "zig-scanner-verbose-comments-v1-phase2-v6-verbose-publication-receipt.json"],
            "other_original_suite_mismatch_counts": {
                "scanner_v3": 64,
                "public_types_v1": 248,
                "substitution_v2": 64,
                "shape_v2": 672,
                "public_surface_v19": 96,
                "subinterpreter_v2_semantic": 0,
            },
            "shape_match_expand_mismatch_count": 176,
            "managed_buffer_case_count": 1024,
            "managed_buffer_mismatch_count": 0,
            "proposed_repair_tested": False,
        },
        "retained_corrected_v3": {
            "source_path": "tools/run_owned_six_family_original_p0_producer_v3.py",
            "source_sha256":
                SUPPORT["tools/run_owned_six_family_original_p0_producer_v3.py"],
            "protocol_path": "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
            "protocol_sha256":
                SUPPORT["oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md"],
            "contract_path": "oracle/phase2/six-family-p0-producer-v3.json",
            "contract_sha256":
                SUPPORT["oracle/phase2/six-family-p0-producer-v3.json"],
            "modified": False,
        },
        "apply_policy": {
            "explicit_apply_required": True,
            "workspace_destination": "FORBIDDEN",
            "candidate_source_mutation": "FORBIDDEN",
            "existing_destination": "FORBIDDEN",
            "external_owner": "FORBIDDEN",
            "private_root_parent": "/tmp",
            "private_root_prefix": PRIVATE_ROOT_PREFIX,
            "phase_names": ["reference-a", "reference-b"],
            "relative_destination": "candidates/zig/py_bridge.c",
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "holdout": "NOT OPENED",
        },
        "phase_boundary": {
            "source_apply_count": 0,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "network_requests": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "qualified_candidate_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "holdout": "NOT OPENED",
            "holdout_opened": False,
            "winner_selected": False,
        },
        "pinned_support": [
            {"path": path, "sha256": digest}
            for path, digest in sorted(SUPPORT.items())
        ],
    }


def checked_private_directory(parent: int, component: str) -> int:
    require(isinstance(parent, int) and parent >= 0
            and isinstance(component, str)
            and component not in ("", ".", "..")
            and "/" not in component and "\\" not in component,
            "reject an invalid Zig private owner component")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(component, flags, dir_fd=parent)
    try:
        owner = os.fstat(descriptor)
        require(stat.S_ISDIR(owner.st_mode)
                and stat.S_IMODE(owner.st_mode) == 0o700
                and owner.st_uid == os.geteuid(),
                "private Zig build directories must be nonlinked and mode 0700")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def apply_private(snapshot_root: str, derived: bytes) -> dict:
    parts = private_parts(snapshot_root)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    tmp = os.open("/tmp", flags)
    root = phase = sibling = source = candidates = zig = destination = None
    try:
        root = checked_private_directory(tmp, parts[2])
        phase = checked_private_directory(root, parts[3])
        sibling_name = "reference-b" if parts[3] == "reference-a" else "reference-a"
        sibling = checked_private_directory(root, sibling_name)
        left, right = os.fstat(phase), os.fstat(sibling)
        require((left.st_dev, left.st_ino) != (right.st_dev, right.st_ino),
                "private Zig reference phases cannot share a directory")
        source = checked_private_directory(phase, "source")
        candidates = checked_private_directory(source, "candidates")
        zig = checked_private_directory(candidates, "zig")
        original = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        require(repaired_source(original, ORIGINAL_SHA256, ORIGINAL_BYTES) == derived,
                "private application must derive from the immutable original")
        destination = os.open(
            "py_bridge.c",
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600, dir_fd=zig,
        )
        before = os.fstat(destination)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "private scanner source must be a fresh owner-only inode")
        offset = 0
        while offset < len(derived):
            count = os.write(destination, derived[offset:])
            require(isinstance(count, int) and count > 0,
                    "private Zig scanner source write was incomplete")
            offset += count
        os.fsync(destination)
        after = os.fstat(destination)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == DERIVED_BYTES,
                "reject replacement of the fresh private scanner inode")
        os.close(destination)
        destination = None
        verify = os.open("py_bridge.c",
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                         dir_fd=zig)
        try:
            visible = os.fstat(verify)
            require((visible.st_dev, visible.st_ino, visible.st_size)
                    == (after.st_dev, after.st_ino, after.st_size),
                    "reject a replaced private scanner source")
            hasher = hashlib.sha256()
            total = 0
            while True:
                piece = os.read(verify, 1024 * 1024)
                if not piece:
                    break
                total += len(piece)
                hasher.update(piece)
            require(total == DERIVED_BYTES
                    and hasher.hexdigest() == DERIVED_SHA256,
                    "the private scanner bytes are not the frozen derived source")
        finally:
            os.close(verify)
        os.fsync(zig)
        checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        checked_read(ENGINE_PATH, ENGINE_SHA256, ENGINE_BYTES)
        checked_read(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
        return {
            "candidate_original_modified": False,
            "derived_bytes": DERIVED_BYTES,
            "derived_sha256": DERIVED_SHA256,
            "mode": "EXCLUSIVE PRIVATE ZIG SCANNER SNAPSHOT APPLY",
            "phase": parts[3],
            "schema": SCHEMA,
            "snapshot_root": snapshot_root,
            "source_apply_count": 1,
            "status": "PASS",
        }
    finally:
        if destination is not None:
            os.close(destination)
        for descriptor in (zig, candidates, source, sibling, phase, root, tmp):
            if descriptor is not None:
                os.close(descriptor)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    options = parser.parse_args()
    try:
        valid_digest(options.source_sha256, "Zig scanner source")
        valid_digest(options.protocol_sha256, "Zig scanner protocol")
        if options.contract_sha256 is not None:
            valid_digest(options.contract_sha256, "Zig scanner contract")
        if options.self_test:
            require(options.snapshot_root is None,
                    "synthetic self-test cannot access a private build root")
            result = self_test()
        elif options.render_contract:
            require(options.snapshot_root is None
                    and options.contract_sha256 is None,
                    "read-only contract rendering cannot apply a source repair")
            result, _derived = verify_context(
                options.source_sha256, options.protocol_sha256,
            )
        else:
            require(options.contract_sha256 is not None,
                    "pin the independent exact Zig scanner source contract")
            contract, derived = verify_context(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256,
            )
            if options.verify_frozen_context:
                require(options.snapshot_root is None,
                        "context verification cannot apply a scanner repair")
                result = {
                    "authenticated_digest_addressed_history_paths": 108,
                    "authoritative_counted_evidence_owner_count": 103,
                    "candidate_imports": 0,
                    "candidate_processes_started": 0,
                    "clock_samples": 0,
                    "compiler_processes_started": 0,
                    "corrected_v3_producer_retained": True,
                    "derived_source_bytes": DERIVED_BYTES,
                    "derived_source_materialized": False,
                    "derived_source_sha256": DERIVED_SHA256,
                    "final_comparison_planned_case_count": 4194304,
                    "frozen_case_execution_count": 31237,
                    "frozen_independent_family_count": 6,
                    "frozen_private_waiver_count": 13,
                    "frozen_source_owner_count": 25,
                    "frozen_suite_count": 13,
                    "frozen_zig_source_owner_count": 3,
                    "historical_zig_semantic_mismatch_count": 1764,
                    "holdout_opened": False,
                    "mode": "READ-ONLY FROZEN CONTEXT",
                    "network_requests": 0,
                    "preserved_scanner_verbose_mismatch_count": 620,
                    "qualified_candidate_count": 0,
                    "schema": contract["schema"],
                    "source_apply_count": 0,
                    "status": "PASS",
                    "workspace_mutations": 0,
                }
            else:
                require(options.snapshot_root is not None,
                        "source application requires an explicit private phase")
                result = apply_private(options.snapshot_root, derived)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GateError, OSError, TypeError, ValueError,
            OverflowError, UnicodeError) as error:
        sys.stderr.write(f"OWNED ZIG SCANNER SOURCE FREEZE V1: FAIL: {error}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
