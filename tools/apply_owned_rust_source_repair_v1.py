#!/usr/bin/env python3
"""Freeze one first-party Rust buffer-order repair without changing a candidate."""

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
SCHEMA = "rebar-phase2-owned-rust-source-repair-v1"
MAX_OWNER_BYTES = 64 * 1024 * 1024
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
    "tools/reproduce_owned_native_source_build_v7.py": "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
    "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md": "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
    "oracle/phase2/native-source-build-v7.json": "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
    "tools/render_candidate_current_overview_v19.py": "8144272f7c91e3821306a4d3963c8e201c68b275cecacf80d5000dd98c502494",
    "docs/evidence/candidate-current-overview-v19.inputs.json": "8f1eb51ff477f0b59934ee503d9bf795f472fd6674180e2af244c7ad4504560c",
    "docs/evidence/candidate-current-overview-v19.json": "504de87d091c555eb53d664fbfaaa70660ff4dd2f9abc22803246f8a5e18287f",
    "docs/evidence/candidate-current-overview-v19.svg": "7dea68622d7c360f9d2af83f97d76210889b2aeda6662e06178009a1127cf3d6",
    "tools/apply_owned_first_party_source_repair_v1.py": "c04bbc8e7bc45bdbe1fb9eb93942286f5b32b39aef554db15b8b1acd9cc8cd99",
    "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md": "1a2e83caaca5cb43fc82445c2a4fc3097bc3d51bdfc568783b8815797b8c63f5",
    "oracle/phase2/first-party-source-repair-v1.json": "8f1a5676bbef5f2ef560d03fef910bf4ed3a4df029ecc0c638e3fa971206dab5",
    "experiments/rust_public_practice_v1/rust-shape-changing-buffer-semantics-v2-phase2-v5-shape-publication-receipt.json": "339a1744bffc467495daa4992622d3cfca0219bc4e7433cb21910b46c04b467c",
    "experiments/rust_public_practice_v1/rust-substitution-buffer-semantics-v2-phase2-v5-substitution-publication-receipt.json": "4905f6cd20f44453b16f0598e5e77ffa99340107a229987c1728b9635a9e7e60",
}
ORIGINAL_PATH = "candidates/rust/py_bridge.c"
ORIGINAL_SHA256 = "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b"
ORIGINAL_BYTES = 175676
ADAPTER_PATH = "candidates/rust_candidate.py"
ADAPTER_SHA256 = "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"
ADAPTER_BYTES = 31151
DERIVED_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
DERIVED_BYTES = 176118
OLD_BLOCK = b"""    RustSubject subject;
    if (!rust_subject_open(&subject, pattern_value, value, 1)) return NULL;
    int callback = PyCallable_Check(replacement);
    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (!callback) {
        if (rust_replacement_cache(pattern, templates, replacement, value, (Py_ssize_t)subject.length, &raw, &tokens) < 0) {
            rust_subject_release(&subject);
            return NULL;
        }
    }
"""
NEW_BLOCK = b"""    RustSubject subject = {0};
    int callback = PyCallable_Check(replacement);
    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (!callback) {
        Py_ssize_t validation_length = 0;
        if (PyUnicode_Check(value)) {
            validation_length = PyUnicode_GET_LENGTH(value);
        } else if (PyBytes_Check(value)) {
            validation_length = PyBytes_GET_SIZE(value);
        } else if (PyByteArray_Check(value)) {
            validation_length = PyByteArray_GET_SIZE(value);
        }
        if (rust_replacement_cache(pattern, templates, replacement, value, validation_length, &raw, &tokens) < 0) {
            Py_XDECREF(raw);
            Py_XDECREF(tokens);
            return NULL;
        }
    }
    if (!rust_subject_open(&subject, pattern_value, value, 1)) {
        Py_XDECREF(raw);
        Py_XDECREF(tokens);
        return NULL;
    }
"""
FUNCTION_ANCHOR = b"static PyObject *rust_substitute_core("
NEXT_FUNCTION_ANCHOR = b"static PyObject *rust_bound_substitute("
GROUP_GUARD = (
    b"    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(pattern));\n"
    b"    if (state == NULL) return NULL;\n"
    b"    if (groups != rebar_groups(handle)) {\n"
    b"        PyErr_SetString(PyExc_ValueError, \"Rust regex group count does not match the compiled program\");\n"
    b"        return NULL;\n"
    b"    }\n"
)
SUCCESS_CLEANUP = (
    b"    if (begins != local_begins) PyMem_Free(begins);\n"
    b"    Py_XDECREF(pieces);\n"
    b"    Py_XDECREF(raw);\n"
    b"    Py_XDECREF(tokens);\n"
    b"    rust_subject_release(&subject);\n"
    b"    return rust_sub_result(joined, replaced, want_count);\n"
)
ERROR_CLEANUP = (
    b"substitute_error:\n"
    b"    rust_output_discard(&writer);\n"
    b"    if (begins != local_begins) PyMem_Free(begins);\n"
    b"    Py_XDECREF(pieces);\n"
    b"    Py_XDECREF(raw);\n"
    b"    Py_XDECREF(tokens);\n"
    b"    rust_subject_release(&subject);\n"
    b"    return NULL;\n"
)


class GateError(Exception):
    """A frozen first-party Rust source obligation failed."""


def require(condition: object, reason: str) -> None:
    if condition is not True:
        raise GateError(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    except (ValueError, TypeError, OverflowError, RecursionError,
            UnicodeError) as error:
        raise GateError("require one exact finite canonical source contract") from error


def valid_digest(value: object, name: str) -> str:
    require(isinstance(value, str) and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            f"invalid {name} SHA-256")
    return value


def relative_parts(value: object) -> tuple[str, ...]:
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "invalid owner path")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value,
            "owner must be a canonical relative path")
    require(0 < len(parsed.parts) <= 12
            and all(part not in ("", ".", "..") for part in parsed.parts),
            "invalid owner path component")
    return parsed.parts


def checked_read(relative: str, expected: str, expected_bytes: int | None = None,
                 *, base: str = str(ROOT)) -> bytes:
    parts = relative_parts(relative)
    valid_digest(expected, "owner")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(base, flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode), "owner is not a regular file")
            require(0 <= before.st_size <= MAX_OWNER_BYTES,
                    "owner exceeds strict authenticated read bound")
            if expected_bytes is not None:
                require(before.st_size == expected_bytes,
                        "owner byte count changed")
            chunks: list[bytes] = []
            count = 0
            while True:
                chunk = os.read(descriptor,
                                min(1024 * 1024, MAX_OWNER_BYTES + 1 - count))
                if not chunk:
                    break
                count += len(chunk)
                require(count <= MAX_OWNER_BYTES,
                        "owner exceeded the authenticated read bound")
                chunks.append(chunk)
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns),
                    "owner changed during authenticated read")
            data = b"".join(chunks)
            require(len(data) == before.st_size,
                    "owner was not read completely")
            require(sha256(data) == expected,
                    f"owner digest changed: {relative}")
            return data
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def strict_json(data: bytes, name: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        value: dict[str, object] = {}
        for key, item in items:
            require(key not in value, f"duplicate key in {name}")
            value[key] = item
        return value

    try:
        result = json.loads(data.decode("utf-8", "strict"),
                            object_pairs_hook=unique,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                GateError(f"non-finite value in {name}")))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise GateError(f"invalid JSON in {name}: {error}") from error
    require(isinstance(result, dict), f"{name} must be a JSON object")
    return result


def repaired_source(source: bytes, baseline_digest: str,
                    baseline_bytes: int, *, frozen: bool = True) -> bytes:
    require(isinstance(source, bytes) and len(source) == baseline_bytes,
            "original Rust source byte count changed")
    require(sha256(source) == baseline_digest,
            "original Rust source digest changed")
    require(source.count(FUNCTION_ANCHOR) == 1,
            "Rust replacement function is not uniquely owned")
    require(source.count(NEXT_FUNCTION_ANCHOR) == 1,
            "Rust replacement function end is not uniquely owned")
    require(source.count(OLD_BLOCK) == 1,
            "original Rust replacement block is not unique")
    require(source.count(NEW_BLOCK) == 0,
            "Rust source already contains the derived block")
    start = source.index(FUNCTION_ANCHOR)
    finish = source.index(NEXT_FUNCTION_ANCHOR, start + len(FUNCTION_ANCHOR))
    at = source.index(OLD_BLOCK)
    require(start < at < finish,
            "Rust replacement block escapes its own substitution function")
    function = source[start:finish]
    require(function.count(GROUP_GUARD) == 1,
            "Rust state and compiled group validation changed")
    require(function.index(GROUP_GUARD) < function.index(OLD_BLOCK),
            "Rust template validation moved ahead of state or group errors")
    require(function.count(SUCCESS_CLEANUP) == 1,
            "Rust successful buffer cleanup is not uniquely preserved")
    require(function.count(ERROR_CLEANUP) == 1,
            "Rust failure buffer cleanup is not uniquely preserved")
    derived = source[:at] + NEW_BLOCK + source[at + len(OLD_BLOCK):]
    require(derived[:at] == source[:at]
            and derived[at + len(NEW_BLOCK):]
            == source[at + len(OLD_BLOCK):],
            "Rust repair changed bytes outside its sole anchored source block")
    require(derived.count(OLD_BLOCK) == 0
            and derived.count(NEW_BLOCK) == 1,
            "Rust derived source must contain exactly one replacement block")
    require(derived.count(FUNCTION_ANCHOR) == 1
            and derived.count(NEXT_FUNCTION_ANCHOR) == 1,
            "Rust repair changed semantic function ownership")
    require(derived.count(b"PyBUF_SIMPLE") == source.count(b"PyBUF_SIMPLE"),
            "Rust repair changed authentic buffer request flags")
    require(derived.count(b"PyCallable_Check(")
            == source.count(b"PyCallable_Check("),
            "Rust repair changed callable replacement detection")
    for marker in (
        b"_subject_length(", b"PyObject_Length(", b"PyObject_Size(",
        b"PyObject_GetBuffer(", b"PyBuffer_Release(",
        b"import re", b"from re ", b"import _sre",
        b"PyImport_ImportModule", b"dlopen(", b"ctypes", b"subprocess",
        b"candidates.vm_candidate", b"candidates.zig", b"candidates.cpp",
        b"candidates.go", b"candidates.fortran",
    ):
        require(derived.count(marker) == source.count(marker),
                "Rust repair introduced subject acquisition or foreign delegation")
    fixed = derived[start:derived.index(NEXT_FUNCTION_ANCHOR, start)]
    require(fixed.count(GROUP_GUARD) == 1
            and fixed.index(GROUP_GUARD) < fixed.index(NEW_BLOCK),
            "Rust repair changed state/group exception precedence")
    require(fixed.count(SUCCESS_CLEANUP) == 1
            and fixed.count(ERROR_CLEANUP) == 1,
            "Rust repair changed its single successful or error buffer release")
    if frozen:
        require(baseline_digest == ORIGINAL_SHA256
                and baseline_bytes == ORIGINAL_BYTES,
                "Rust repair is not based on its frozen first-party source")
        require(sha256(derived) == DERIVED_SHA256
                and len(derived) == DERIVED_BYTES,
                "Rust derived source is not the exact frozen single-block repair")
        require(source.count(b"PyBUF_SIMPLE") == 10
                and source.count(b"PyCallable_Check(") == 2,
                "original Rust buffer or callback witnesses changed")
    return derived


class SourceOnlyBoundary:
    """Block every real source-only filesystem, candidate, or timing effect."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def forbidden(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GateError(f"source-only boundary: {name}")

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


def sample_source() -> bytes:
    return (
        b"/* strictly synthetic first-party Rust bridge */\n"
        + FUNCTION_ANCHOR
        + b"void *handle) {\n"
        + GROUP_GUARD
        + OLD_BLOCK
        + b"    if (PyBUF_SIMPLE) PyCallable_Check(replacement);\n"
        + SUCCESS_CLEANUP
        + ERROR_CLEANUP
        + b"}\n"
        + NEXT_FUNCTION_ANCHOR
        + b"void *handle) { return NULL; }\n"
    )


def self_test() -> dict:
    accepted = 0
    rejected = 0
    sample = sample_source()
    sample_digest = sha256(sample)
    with SourceOnlyBoundary() as boundary:
        result = repaired_source(sample, sample_digest, len(sample), frozen=False)
        require(result.count(NEW_BLOCK) == 1,
                "synthetic Rust source was not uniquely repaired")
        accepted += 1
        require(result.count(b"PyBUF_SIMPLE") == 1,
                "synthetic Rust buffer flags changed")
        accepted += 1
        require(result.count(b"PyCallable_Check(") == 2,
                "synthetic Rust callback classification changed")
        accepted += 1
        require(result.count(SUCCESS_CLEANUP) == 1,
                "synthetic Rust successful cleanup changed")
        accepted += 1
        require(result.count(ERROR_CLEANUP) == 1,
                "synthetic Rust error cleanup changed")
        accepted += 1
        require(NEW_BLOCK.index(b"rust_replacement_cache(")
                < NEW_BLOCK.index(b"rust_subject_open("),
                "Rust replacement must be prepared before subject acquisition")
        accepted += 1
        require(NEW_BLOCK.index(b"Py_ssize_t validation_length = 0;")
                < NEW_BLOCK.index(b"PyUnicode_Check(value)")
                < NEW_BLOCK.index(b"PyBytes_Check(value)")
                < NEW_BLOCK.index(b"PyByteArray_Check(value)")
                < NEW_BLOCK.index(b"rust_replacement_cache("),
                "opaque Rust subjects must use zero without invoking an exporter")
        accepted += 1
        require(b"_subject_length(" not in NEW_BLOCK
                and b"PyObject_Length(" not in NEW_BLOCK
                and b"PyObject_Size(" not in NEW_BLOCK
                and b"PyObject_GetBuffer(" not in NEW_BLOCK,
                "Rust template preparation must not inspect an arbitrary subject")
        accepted += 1
        template_failure = (
            b"        if (rust_replacement_cache(pattern, templates, replacement, value, validation_length, &raw, &tokens) < 0) {\n"
            b"            Py_XDECREF(raw);\n"
            b"            Py_XDECREF(tokens);\n"
            b"            return NULL;\n"
            b"        }\n"
        )
        require(NEW_BLOCK.count(template_failure) == 1
                and NEW_BLOCK.index(template_failure)
                < NEW_BLOCK.index(b"rust_subject_open("),
                "invalid Rust replacements must fail without subject acquisition")
        accepted += 1
        subject_failure = (
            b"    if (!rust_subject_open(&subject, pattern_value, value, 1)) {\n"
            b"        Py_XDECREF(raw);\n"
            b"        Py_XDECREF(tokens);\n"
            b"        return NULL;\n"
            b"    }\n"
        )
        require(NEW_BLOCK.count(subject_failure) == 1,
                "failed Rust subject must release template references exactly once")
        accepted += 1
        require(b"rust_subject_release(" not in subject_failure
                and b"rust_subject_release(" not in template_failure,
                "failed Rust preparation must not double-release a subject")
        accepted += 1
        require(NEW_BLOCK.count(b"if (!callback)") == 1
                and NEW_BLOCK.index(b"if (!callback)")
                < NEW_BLOCK.index(b"rust_subject_open("),
                "Rust callable replacements must retain subject-first behavior")
        accepted += 1
        require(result[:result.index(NEW_BLOCK)]
                == sample[:sample.index(OLD_BLOCK)],
                "Rust synthetic repair changed its untouched source prefix")
        accepted += 1
        require(result[result.index(NEW_BLOCK) + len(NEW_BLOCK):]
                == sample[sample.index(OLD_BLOCK) + len(OLD_BLOCK):],
                "Rust synthetic repair changed its untouched source suffix")
        accepted += 1
        require(sha256(OLD_BLOCK)
                == "164afc04529a2e1b3dbd112ed907bd89d6e7a870fd6fa6ccdfef7b36e72a08de",
                "exact original Rust source block changed")
        accepted += 1
        require(sha256(NEW_BLOCK)
                == "e73571d971682ff2167e2338b044eda2bc46566dcb6b90af78db85d592e01d0b",
                "exact derived Rust source block changed")
        accepted += 1

        def reject(call: object, label: str) -> None:
            nonlocal rejected
            try:
                call()  # type: ignore[operator]
            except (GateError, OSError, ValueError, TypeError,
                    OverflowError, UnicodeError):
                rejected += 1
            else:
                raise GateError(f"hostile Rust source control was accepted: {label}")

        mutations = {
            "wrong original digest": (sample, "0" * 64, len(sample)),
            "wrong original byte count": (sample, sample_digest, len(sample) + 1),
            "missing repair block":
                (sample.replace(OLD_BLOCK, b"/* absent */\n"), None, None),
            "duplicate repair block":
                (sample.replace(OLD_BLOCK, OLD_BLOCK + OLD_BLOCK), None, None),
            "already-repaired source":
                (sample.replace(OLD_BLOCK, NEW_BLOCK), None, None),
            "duplicate function":
                (FUNCTION_ANCHOR + b"foreign\n" + sample, None, None),
            "missing function":
                (sample.replace(FUNCTION_ANCHOR, b"not_the_owner("), None, None),
            "duplicate next function":
                (sample + NEXT_FUNCTION_ANCHOR, None, None),
            "missing next function":
                (sample.replace(NEXT_FUNCTION_ANCHOR, b"not_the_end("), None, None),
            "missing group guard":
                (sample.replace(GROUP_GUARD, b"/* guard removed */\n"), None, None),
            "duplicate group guard":
                (sample.replace(GROUP_GUARD, GROUP_GUARD + GROUP_GUARD), None, None),
            "missing successful cleanup":
                (sample.replace(SUCCESS_CLEANUP, b"return NULL;\n"), None, None),
            "duplicate successful cleanup":
                (sample.replace(SUCCESS_CLEANUP,
                                SUCCESS_CLEANUP + SUCCESS_CLEANUP), None, None),
            "missing error cleanup":
                (sample.replace(ERROR_CLEANUP, b"return NULL;\n"), None, None),
            "duplicate error cleanup":
                (sample.replace(ERROR_CLEANUP,
                                ERROR_CLEANUP + ERROR_CLEANUP), None, None),
            "block outside Rust function":
                (OLD_BLOCK + sample.replace(OLD_BLOCK, b"/* moved */\n"),
                 None, None),
            "frozen synthetic owner": (sample, sample_digest, len(sample)),
        }
        for name, (mutated, expected, size) in mutations.items():
            expected = sha256(mutated) if expected is None else expected
            size = len(mutated) if size is None else size
            reject(lambda data=mutated, digest=expected, count=size,
                   exact=(name == "frozen synthetic owner"):
                   repaired_source(data, digest, count, frozen=exact), name)

        for value in ("", "/tmp/escape", "../escape", "a/../escape",
                      "a/./escape", "a//escape", "./owner", "a/",
                      "a" * 513, "/home/dev-user/src/rebar/candidates/rust/py_bridge.c"):
            reject(lambda item=value: relative_parts(item),
                   f"hostile Rust source path {value!r}")
        for value in ("", "0" * 63, "0" * 65, "F" * 64,
                      "g" * 64, "../" + "0" * 61):
            reject(lambda item=value: valid_digest(item, "hostile"),
                   "hostile Rust source digest")
        reject(lambda: strict_json(b'{"a":1,"a":2}', "hostile"),
               "duplicate source-contract JSON key")
        reject(lambda: strict_json(b'{"a":NaN}', "hostile"),
               "nonfinite source-contract JSON")
        reject(lambda: strict_json(b"[]", "hostile"),
               "nonobject source-contract JSON")

        probes = (
            (lambda: builtins.open("/tmp/forbidden"), "builtins file read"),
            (lambda: io.open("/tmp/forbidden"), "io file read"),
            (lambda: os.open("/tmp/forbidden", os.O_RDONLY), "file descriptor"),
            (lambda: os.read(0, 1), "real source read"),
            (lambda: os.write(1, b"x"), "workspace write"),
            (lambda: os.stat("/tmp"), "path stat"),
            (lambda: os.lstat("/tmp"), "symlink stat"),
            (lambda: os.mkdir("/tmp/forbidden"), "root creation"),
            (lambda: os.unlink("/tmp/forbidden"), "owner deletion"),
            (lambda: os.replace("/tmp/a", "/tmp/b"), "owner replacement"),
            (lambda: Path("/tmp/forbidden").read_bytes(), "Path source read"),
            (lambda: Path("/tmp/forbidden").write_bytes(b"x"),
             "Path source write"),
            (lambda: Path("/tmp").resolve(), "path resolution"),
            (lambda: subprocess.run(("true",)), "subprocess"),
            (lambda: subprocess.Popen(("true",)), "compiler or candidate"),
            (lambda: socket.socket(), "network"),
            (lambda: tempfile.mkdtemp(), "private source root"),
            (lambda: tempfile.mkstemp(), "temporary source"),
            (lambda: importlib.import_module("candidates.rust_candidate"),
             "Rust candidate import"),
            (lambda: importlib.import_module("candidates.vm_candidate"),
             "foreign C candidate import"),
            (lambda: importlib.import_module("re"), "stdlib regex import"),
            (lambda: threading.Thread().start(), "thread"),
            (lambda: time.perf_counter(), "performance clock"),
            (lambda: time.perf_counter_ns(), "performance nanoclock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.sleep(0), "waiting"),
        )
        for probe, label in probes:
            reject(probe, label)
        blocked = boundary.blocked
    require(blocked == len(probes),
            "synthetic Rust source-effect accounting changed")
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
            valid_digest(digest, "historical evidence")
            relative_parts(path)
            require(path not in output or output[path] == digest,
                    "conflicting historical evidence owner")
            output[path] = digest
        for child in value.values():
            discover_evidence(child, output)
    elif isinstance(value, list):
        for child in value:
            discover_evidence(child, output)


def verify_rust_failure_receipts(shape: dict, substitution: dict) -> None:
    require(shape.get("schema")
            == "rebar-independent-shape-changing-buffer-semantics-recorder-v2-durable-candidate-publication-receipt"
            and shape.get("status") == "PASS"
            and shape.get("candidate_result_status") == "FAIL"
            and shape.get("candidate_family") == "rust"
            and shape.get("case_count") == 10240
            and shape.get("mismatch_count") == 1392
            and shape.get("all_mismatches_preserved") is True
            and shape.get("mismatches_by_api") == {
                "match.expand": 176,
                "module.sub": 304, "module.subn": 304,
                "pattern.sub": 304, "pattern.subn": 304,
            }
            and shape.get("hidden_cases_read") == 0
            and shape.get("clock_samples") == 0
            and shape.get("performance") == "NOT MEASURED",
            "never infer a Rust repair from a changed original shape witness")
    require(substitution.get("schema")
            == "rebar-independent-substitution-buffer-semantics-recorder-v3-durable-candidate-publication-receipt"
            and substitution.get("status") == "PASS"
            and substitution.get("candidate_result_status") == "FAIL"
            and substitution.get("candidate_family") == "rust"
            and substitution.get("case_count") == 5120
            and substitution.get("mismatch_count") == 336
            and substitution.get("all_mismatches_preserved") is True
            and substitution.get("mismatches_by_api") == {
                "match.expand": 0,
                "module.sub": 84, "module.subn": 84,
                "pattern.sub": 84, "pattern.subn": 84,
            }
            and substitution.get("full_readonly_buffer_flag") == 284
            and substitution.get("simple_buffer_flag") == 0
            and substitution.get("hidden_cases_read") == 0
            and substitution.get("clock_samples") == 0
            and substitution.get("performance") == "NOT MEASURED",
            "never infer a Rust repair from a changed substitution witness")


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None) -> tuple[dict, bytes]:
    require(sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.executable == PYTHON
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "require independently pinned isolated CPython 3.14.6")
    valid_digest(source_pin, "Rust repair tool")
    valid_digest(protocol_pin, "Rust repair protocol")
    checked_read("tools/apply_owned_rust_source_repair_v1.py", source_pin)
    checked_read("oracle/phase2/RUST-SOURCE-REPAIR-V1.md", protocol_pin)
    protected = {path: checked_read(path, digest)
                 for path, digest in SUPPORT.items()}
    original = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    checked_read(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    derived = repaired_source(original, ORIGINAL_SHA256, ORIGINAL_BYTES)

    p0 = strict_json(protected["oracle/phase1/p0-completeness-v1.json"], "P0")
    require(p0.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and p0.get("version") == 1,
            "original frozen Rust compatibility oracle changed")
    denominator = p0.get("denominator")
    require(isinstance(denominator, dict)
            and tuple(denominator.get("counted_suite_ids", ())) == SUITE_IDS
            and denominator.get("final_required_case_execution_denominator") == 31237
            and denominator.get("private_upstream_methods_outside_public_denominator") == 13,
            "original 13-suite, 31,237-case, 13-waiver Rust gate changed")
    gate = p0.get("phase_gate")
    require(isinstance(gate, dict)
            and gate.get("status") == "PASS"
            and gate.get("all_obligations_mapped") is True
            and gate.get("final_holdout_authorized") is False,
            "original reference compatibility oracle is not independently frozen")
    runtime = p0.get("runtime")
    require(isinstance(runtime, dict)
            and runtime.get("python_version") == "3.14.6"
            and runtime.get("python_implementation") == "CPython",
            "original CPython 3.14.6 correctness runtime changed")
    executable = runtime.get("executable")
    require(isinstance(executable, dict)
            and executable.get("path") == PYTHON
            and executable.get("sha256") == PYTHON_SHA256,
            "original CPython correctness executable pin changed")

    v7 = strict_json(protected["oracle/phase2/native-source-build-v7.json"], "V7")
    require(v7.get("schema")
            == "rebar-phase2-owned-native-source-build-v7-source-freeze"
            and v7.get("version") == 7
            and v7.get("family_count") == 6
            and v7.get("source_owner_count") == 25
            and v7.get("qualified_candidate_count") == 0,
            "frozen six-family, 25-source first-party baseline changed")
    families = v7.get("families")
    require(isinstance(families, list) and len(families) == 6,
            "first-party independent source-family count changed")
    ids: list[str] = []
    paths: set[str] = set()
    rust: dict | None = None
    for family in families:
        require(isinstance(family, dict), "invalid first-party family")
        identifier = family.get("id")
        require(isinstance(identifier, str) and identifier not in ids,
                "repeated first-party family")
        ids.append(identifier)
        if identifier == "rust":
            rust = family
        owners = family.get("owners")
        require(isinstance(owners, list) and bool(owners),
                "empty first-party semantic source family")
        for owner in owners:
            require(isinstance(owner, dict), "invalid first-party source owner")
            path, digest = owner.get("path"), owner.get("sha256")
            size = owner.get("bytes")
            require(isinstance(path, str) and path not in paths
                    and isinstance(digest, str)
                    and isinstance(size, int) and size >= 0,
                    "duplicate or changed first-party source owner")
            checked_read(path, digest, size)
            paths.add(path)
    require(tuple(ids) == ("c", "rust", "zig", "cpp", "go", "fortran")
            and len(paths) == 25
            and ORIGINAL_PATH in paths and ADAPTER_PATH in paths,
            "Rust repair changed the original independent source closure")
    require(isinstance(rust, dict) and rust.get("language") == "Rust"
            and isinstance(rust.get("owners"), list)
            and len(rust["owners"]) == 9
            and rust.get("adapter_import") == "_rust_bridge",
            "original Rust must retain all nine distinct first-party owners")
    policy = v7.get("build_policy")
    require(isinstance(policy, dict)
            and policy.get("rust_external_package_count") == 0
            and policy.get("cross_family_matching_dependencies") == 0
            and policy.get("external_regular_expression_packages") == 0
            and policy.get("stdlib_matching_delegation") == 0,
            "Rust repair may not introduce an external or borrowed regex engine")

    c_contract = strict_json(
        protected["oracle/phase2/first-party-source-repair-v1.json"],
        "unchanged independent C source-repair contract")
    require(c_contract.get("schema")
            == "rebar-phase2-owned-first-party-source-repair-v1"
            and c_contract.get("version") == 1,
            "the independently frozen C source repair changed")
    c_tool = c_contract.get("tool")
    c_protocol = c_contract.get("protocol")
    require(isinstance(c_tool, dict)
            and c_tool.get("path") == "tools/apply_owned_first_party_source_repair_v1.py"
            and c_tool.get("sha256")
            == SUPPORT["tools/apply_owned_first_party_source_repair_v1.py"]
            and isinstance(c_protocol, dict)
            and c_protocol.get("path")
            == "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md"
            and c_protocol.get("sha256")
            == SUPPORT["oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md"],
            "Rust overlay must retain the separate pinned C source repair")

    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v19.inputs.json"],
        "V19 inputs")
    summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v19.json"],
        "V19 summary")
    require(inputs.get("repository_evidence_owner_count") == 71
            and inputs.get("preserved_v18_repository_evidence_owner_count") == 69
            and inputs.get("new_go_result_repository_evidence_owner_count") == 2
            and inputs.get("full_case_denominator") == 31237
            and inputs.get("suite_count") == 13,
            "published 71-owner source baseline changed")
    require(summary.get("schema")
            == "rebar-candidate-current-overview-v19-summary"
            and summary.get("status") == "PASS"
            and summary.get("repository_evidence_owner_count") == 71
            and summary.get("full_case_denominator") == 31237
            and summary.get("suite_count") == 13,
            "frozen published V19 overview changed")
    snapshot = summary.get("snapshot")
    require(isinstance(snapshot, dict)
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 71
            and snapshot.get("current_source_owner_count") == 25
            and snapshot.get("frozen_independent_engine_family_count") == 6
            and snapshot.get("current_tested_candidate_family_count") == 5
            and snapshot.get("qualified_candidate_count") == 0
            and snapshot.get("verified_activation_v4_current_active_target_count") == 0
            and snapshot.get("rust_actual_semantic_mismatch_count") == 2042
            and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS,
            "Rust source freeze changed actual existing outcomes or activations")
    go = snapshot.get("go_v2_full_original_campaign")
    require(isinstance(go, dict) and go.get("status") == "FAIL"
            and go.get("completed_suite_count") == 13
            and go.get("semantic_mismatch_count") == 4518
            and go.get("infrastructure_failure_count") == 4
            and go.get("crash_count") == 0 and go.get("timeout_count") == 0
            and go.get("restoration_status") == "PASS",
            "Rust overlay changed genuine complete Go candidate results")
    for document in (inputs, summary, snapshot):
        require(document.get("final_holdout_opened") is False
                and document.get("final_comparison_cases_generated") is False
                and document.get("final_comparison_planned_case_count") == 4194304
                and document.get("performance") == "NOT MEASURED"
                and document.get("memory") == "NOT MEASURED"
                and document.get("confidence_intervals") == "NOT MEASURED",
                "Rust source freeze accessed or inferred holdout performance")
    require(snapshot.get("hidden_cases_read") == 0
            and snapshot.get("performance_files_read") == 0
            and snapshot.get("clock_samples") == 0
            and snapshot.get("timing_trials_run") == 0
            and snapshot.get("final_holdout_authorized") is False
            and snapshot.get("winner_selected") is False,
            "Rust source freeze crossed a performance or holdout boundary")

    shape = strict_json(
        protected[
            "experiments/rust_public_practice_v1/"
            "rust-shape-changing-buffer-semantics-v2-phase2-v5-shape-publication-receipt.json"
        ], "original Rust shape-changing failure receipt")
    substitution = strict_json(
        protected[
            "experiments/rust_public_practice_v1/"
            "rust-substitution-buffer-semantics-v2-phase2-v5-substitution-publication-receipt.json"
        ], "original Rust replacement failure receipt")
    verify_rust_failure_receipts(shape, substitution)

    history: dict[str, str] = {}
    discover_evidence(inputs, history)
    discover_evidence(summary, history)
    require(len(history) == 76,
            "complete independently digest-addressed V19 history changed")
    for path, digest in sorted(history.items()):
        checked_read(path, digest)
    require(sum(path.startswith("oracle/phase2/evidence/")
                for path in history) == 46
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "original 76-reference evidence categories changed")

    document = contract_document(source_pin, protocol_pin)
    if contract_pin is not None:
        valid_digest(contract_pin, "Rust repair contract")
        actual = checked_read("oracle/phase2/rust-source-repair-v1.json",
                              contract_pin)
        require(actual == canonical(document),
                "Rust source contract is not exact canonical frozen bytes")
    return document, derived


def contract_document(source_pin: str, protocol_pin: str) -> dict:
    return {
        "schema": SCHEMA,
        "version": 1,
        "phase": "RUST SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "tool": {
            "path": "tools/apply_owned_rust_source_repair_v1.py",
            "sha256": source_pin,
        },
        "protocol": {
            "path": "oracle/phase2/RUST-SOURCE-REPAIR-V1.md",
            "sha256": protocol_pin,
        },
        "oracle": {
            "case_execution_count": 31237,
            "implementation": "CPython",
            "manifest_path": "oracle/phase1/p0-completeness-v1.json",
            "manifest_sha256": SUPPORT["oracle/phase1/p0-completeness-v1.json"],
            "private_waiver_count": 13,
            "suite_count": 13,
            "suite_ids": list(SUITE_IDS),
            "version": "3.14.6",
        },
        "source_baseline": {
            "frozen_family_count": 6,
            "frozen_family_ids": ["c", "rust", "zig", "cpp", "go", "fortran"],
            "frozen_rust_owner_count": 9,
            "frozen_source_owner_count": 25,
            "manifest_path": "oracle/phase2/native-source-build-v7.json",
            "manifest_sha256": SUPPORT["oracle/phase2/native-source-build-v7.json"],
            "rust_external_package_count": 0,
            "shared_semantic_owner_count": 0,
        },
        "repair": {
            "adapter": {
                "bytes": ADAPTER_BYTES,
                "path": ADAPTER_PATH,
                "sha256": ADAPTER_SHA256,
            },
            "callable_detection_count_after": 2,
            "callable_detection_count_before": 2,
            "callable_order": "ORIGINAL SUBJECT-FIRST; UNCHANGED",
            "derived_source": {
                "bytes": DERIVED_BYTES,
                "materialized": False,
                "sha256": DERIVED_SHA256,
            },
            "function": "rust_substitute_core",
            "match_expand_modified": False,
            "new_block": {
                "bytes": len(NEW_BLOCK),
                "occurrence_count_after": 1,
                "occurrence_count_before": 0,
                "sha256": sha256(NEW_BLOCK),
            },
            "opaque_subject_validation_length": 0,
            "opaque_subject_buffer_acquired": False,
            "old_block": {
                "bytes": len(OLD_BLOCK),
                "occurrence_count_after": 0,
                "occurrence_count_before": 1,
                "sha256": sha256(OLD_BLOCK),
            },
            "original_source": {
                "bytes": ORIGINAL_BYTES,
                "modified": False,
                "path": ORIGINAL_PATH,
                "sha256": ORIGINAL_SHA256,
            },
            "pybuf_simple_occurrence_count_after": 10,
            "pybuf_simple_occurrence_count_before": 10,
            "replacement_cache_modified": False,
            "replacement_hash_modified": False,
            "safe_known_subject_length_accessors": [
                "PyUnicode_GET_LENGTH", "PyBytes_GET_SIZE",
                "PyByteArray_GET_SIZE",
            ],
            "successful_subject_cleanup":
            "EXISTING SINGLE SUCCESSFUL BUFFER RELEASE; UNCHANGED",
            "error_subject_cleanup":
            "EXISTING SINGLE ERROR-LABEL BUFFER RELEASE; UNCHANGED",
            "subject_failure_cleanup":
            "ONE RAW DECREF; ONE TOKEN DECREF; NO SUBJECT DOUBLE RELEASE",
            "template_failure_cleanup":
            "NO SUBJECT ACQUIRED; ONE RAW/TOKEN CLEANUP",
            "transformation": "EXACTLY ONE ANCHORED FIRST-PARTY RUST BRIDGE BLOCK",
        },
        "published_history": {
            "authenticated_digest_addressed_history_paths": 76,
            "authoritative_counted_evidence_owner_count": 71,
            "current_active_target_count": 0,
            "current_tested_candidate_family_count": 5,
            "experiment_history_path_count": 30,
            "go_full_campaign_infrastructure_failure_count": 4,
            "go_full_campaign_semantic_mismatch_count": 4518,
            "go_full_campaign_status": "FAIL",
            "go_full_campaign_suite_count": 13,
            "go_restoration_status": "PASS",
            "oracle_evidence_path_count": 46,
            "overview_inputs_path":
            "docs/evidence/candidate-current-overview-v19.inputs.json",
            "overview_inputs_sha256":
            SUPPORT["docs/evidence/candidate-current-overview-v19.inputs.json"],
            "overview_path": "docs/evidence/candidate-current-overview-v19.json",
            "overview_sha256":
            SUPPORT["docs/evidence/candidate-current-overview-v19.json"],
            "qualified_candidate_count": 0,
        },
        "retained_c_repair": {
            "source_path": "tools/apply_owned_first_party_source_repair_v1.py",
            "source_sha256":
            SUPPORT["tools/apply_owned_first_party_source_repair_v1.py"],
            "protocol_path": "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md",
            "protocol_sha256":
            SUPPORT["oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md"],
            "contract_path": "oracle/phase2/first-party-source-repair-v1.json",
            "contract_sha256":
            SUPPORT["oracle/phase2/first-party-source-repair-v1.json"],
            "modified": False,
        },
        "historical_rust_witness": {
            "shape_case_count": 10240,
            "shape_mismatch_count": 1392,
            "shape_match_expand_mismatch_count": 176,
            "shape_substitution_mismatch_count": 1216,
            "substitution_case_count": 5120,
            "substitution_mismatch_count": 336,
            "combined_hypothesized_affected_case_upper_bound": 1552,
            "proposed_repair_tested": False,
            "shape_receipt_path":
            "experiments/rust_public_practice_v1/"
            "rust-shape-changing-buffer-semantics-v2-phase2-v5-shape-publication-receipt.json",
            "shape_receipt_sha256": SUPPORT[
                "experiments/rust_public_practice_v1/"
                "rust-shape-changing-buffer-semantics-v2-phase2-v5-shape-publication-receipt.json"
            ],
            "substitution_receipt_path":
            "experiments/rust_public_practice_v1/"
            "rust-substitution-buffer-semantics-v2-phase2-v5-substitution-publication-receipt.json",
            "substitution_receipt_sha256": SUPPORT[
                "experiments/rust_public_practice_v1/"
                "rust-substitution-buffer-semantics-v2-phase2-v5-substitution-publication-receipt.json"
            ],
        },
        "apply_policy": {
            "candidate_source_mutation": "FORBIDDEN",
            "existing_destination": "FORBIDDEN",
            "explicit_apply_required": True,
            "external_owner": "FORBIDDEN",
            "holdout": "NOT OPENED",
            "mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "phase_names": ["reference-a", "reference-b"],
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "private_root_parent": "/tmp",
            "private_root_prefix": "rebar-phase2-native-build-v9-rust-",
            "relative_destination": "candidates/rust/py_bridge.c",
            "workspace_destination": "FORBIDDEN",
        },
        "phase_boundary": {
            "candidate_correctness": "NOT MEASURED",
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "clock_samples": 0,
            "compiler_processes_started": 0,
            "final_comparison_cases_generated": False,
            "final_comparison_planned_case_count": 4194304,
            "holdout": "NOT OPENED",
            "holdout_opened": False,
            "memory": "NOT MEASURED",
            "native_libraries_loaded": 0,
            "network_requests": 0,
            "performance": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "source_apply_count": 0,
            "timing_trials_run": 0,
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        },
        "pinned_support": [
            {"path": path, "sha256": digest}
            for path, digest in sorted(SUPPORT.items())
        ],
    }


def checked_private_directory(parent: int, component: str) -> int:
    require(isinstance(parent, int) and parent >= 0,
            "invalid Rust private parent descriptor")
    require(isinstance(component, str)
            and component not in ("", ".", "..")
            and "/" not in component and "\\" not in component,
            "invalid Rust private directory component")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(component, flags, dir_fd=parent)
    try:
        owner = os.fstat(descriptor)
        require(stat.S_ISDIR(owner.st_mode)
                and stat.S_IMODE(owner.st_mode) == 0o700
                and owner.st_uid == os.geteuid(),
                "Rust private phase directory is not owner-only")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def apply_private(snapshot_root: str, derived: bytes) -> dict:
    require(isinstance(snapshot_root, str) and len(snapshot_root) <= 512,
            "invalid private Rust snapshot root")
    parsed = PurePosixPath(snapshot_root)
    require(parsed.is_absolute() and str(parsed) == snapshot_root,
            "Rust snapshot root must be a canonical absolute path")
    parts = parsed.parts
    require(len(parts) == 5 and parts[1] == "tmp"
            and parts[2].startswith("rebar-phase2-native-build-v9-rust-")
            and len(parts[2]) > len("rebar-phase2-native-build-v9-rust-")
            and all(character.isascii()
                    and (character.isalnum() or character in "-_")
                    for character in parts[2])
            and parts[3] in ("reference-a", "reference-b")
            and parts[4] == "source",
            "Rust snapshot must be a fresh owner-only two-phase V9 root")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    tmpfd = os.open("/tmp", flags)
    rootfd = phasefd = sourcefd = candidatefd = rustfd = otherfd = None
    destination = None
    try:
        rootfd = checked_private_directory(tmpfd, parts[2])
        phasefd = checked_private_directory(rootfd, parts[3])
        other = "reference-b" if parts[3] == "reference-a" else "reference-a"
        otherfd = checked_private_directory(rootfd, other)
        require((os.fstat(phasefd).st_dev, os.fstat(phasefd).st_ino)
                != (os.fstat(otherfd).st_dev, os.fstat(otherfd).st_ino),
                "independent Rust source-build phases cannot alias")
        sourcefd = checked_private_directory(phasefd, "source")
        candidatefd = checked_private_directory(sourcefd, "candidates")
        rustfd = checked_private_directory(candidatefd, "rust")
        original_before = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256,
                                       ORIGINAL_BYTES)
        require(repaired_source(original_before, ORIGINAL_SHA256,
                                ORIGINAL_BYTES) == derived,
                "private Rust snapshot no longer matches the original source")
        file_flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                      | os.O_NOFOLLOW | os.O_CLOEXEC)
        destination = os.open("py_bridge.c", file_flags, 0o600,
                              dir_fd=rustfd)
        before = os.fstat(destination)
        require(stat.S_ISREG(before.st_mode)
                and before.st_nlink == 1
                and before.st_uid == os.geteuid()
                and stat.S_IMODE(before.st_mode) == 0o600,
                "private Rust source is not a unique owner-only inode")
        offset = 0
        while offset < len(derived):
            written = os.write(destination, derived[offset:])
            require(isinstance(written, int) and written > 0,
                    "private Rust source write was incomplete")
            offset += written
        os.fsync(destination)
        after = os.fstat(destination)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == DERIVED_BYTES,
                "private Rust source identity changed during exclusive write")
        os.close(destination)
        destination = None
        descriptor = os.open("py_bridge.c",
                             os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=rustfd)
        try:
            visible = os.fstat(descriptor)
            require((visible.st_dev, visible.st_ino, visible.st_uid,
                     visible.st_nlink, visible.st_size)
                    == (after.st_dev, after.st_ino, after.st_uid,
                        after.st_nlink, after.st_size),
                    "private Rust source owner was replaced")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            require(b"".join(chunks) == derived,
                    "private Rust source bytes do not match the frozen repair")
        finally:
            os.close(descriptor)
        os.fsync(rustfd)
        checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        checked_read(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
        return {
            "candidate_original_modified": False,
            "derived_bytes": DERIVED_BYTES,
            "derived_sha256": DERIVED_SHA256,
            "mode": "EXCLUSIVE PRIVATE RUST SNAPSHOT APPLY",
            "phase": parts[3],
            "schema": SCHEMA,
            "snapshot_root": snapshot_root,
            "source_apply_count": 1,
            "status": "PASS",
        }
    finally:
        if destination is not None:
            os.close(destination)
        for descriptor in (rustfd, candidatefd, sourcefd, otherfd,
                           phasefd, rootfd, tmpfd):
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
        valid_digest(options.source_sha256, "Rust repair source")
        valid_digest(options.protocol_sha256, "Rust repair protocol")
        if options.contract_sha256 is not None:
            valid_digest(options.contract_sha256, "Rust repair contract")
        if options.self_test:
            require(options.snapshot_root is None,
                    "source-only Rust self-test cannot apply a repair")
            result = self_test()
        elif options.render_contract:
            require(options.snapshot_root is None
                    and options.contract_sha256 is None,
                    "read-only contract rendering cannot apply Rust source")
            result, _derived = verify_context(options.source_sha256,
                                              options.protocol_sha256)
        else:
            require(options.contract_sha256 is not None,
                    "frozen Rust verification requires its exact contract pin")
            contract, derived = verify_context(options.source_sha256,
                                               options.protocol_sha256,
                                               options.contract_sha256)
            if options.verify_frozen_context:
                require(options.snapshot_root is None,
                        "read-only verification cannot apply Rust source")
                result = {
                    "authenticated_digest_addressed_history_paths": 76,
                    "authoritative_counted_evidence_owner_count": 71,
                    "candidate_imports": 0,
                    "candidate_processes_started": 0,
                    "clock_samples": 0,
                    "compiler_processes_started": 0,
                    "derived_source_bytes": DERIVED_BYTES,
                    "derived_source_materialized": False,
                    "derived_source_sha256": DERIVED_SHA256,
                    "final_comparison_planned_case_count": 4194304,
                    "frozen_case_execution_count": 31237,
                    "frozen_independent_family_count": 6,
                    "frozen_private_waiver_count": 13,
                    "frozen_rust_source_owner_count": 9,
                    "frozen_source_owner_count": 25,
                    "frozen_suite_count": 13,
                    "holdout_opened": False,
                    "mode": "READ-ONLY FROZEN CONTEXT",
                    "network_requests": 0,
                    "qualified_candidate_count": 0,
                    "retained_c_source_repair_unchanged": True,
                    "schema": contract["schema"],
                    "source_apply_count": 0,
                    "status": "PASS",
                    "workspace_mutations": 0,
                }
            else:
                require(options.snapshot_root is not None,
                        "Rust application requires one explicit private snapshot")
                result = apply_private(options.snapshot_root, derived)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GateError, OSError, ValueError, TypeError,
            UnicodeError, OverflowError) as error:
        sys.stderr.write(f"FIRST-PARTY RUST SOURCE REPAIR V1: FAIL: {error}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
