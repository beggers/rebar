#!/usr/bin/env python3
"""Verify the owned one-pass Rust literal-findall source without executing it."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules:
    raise SystemExit("source-only Rust verification must not import a regex engine")

import builtins
import hashlib
import os
import stat

ROOT = "/home/dev-user/src/rebar"
PINNED_CPYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SOURCE_PATH = "tools/verify_owned_rust_literal_findall_source_v1.py"
PROTOCOL_PATH = "oracle/phase2/RUST-LITERAL-FINDALL-ONE-PASS-V1.md"
CONTRACT_PATH = "oracle/phase2/rust-literal-findall-one-pass-v1.json"
PREDECESSOR_PATH = "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c"
VARIANT_PATH = "candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c"
PREDECESSOR_SHA256 = "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
VARIANT_SHA256 = "b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112"
PROTOCOL_SHA256 = "842d51127db54a26d0dd9f874f38834f122f7888ea71c6f3fe77b8911bbd65d6"
BUILD_RECEIPT_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance"
    "-publication-receipt.json"
)
BUILD_RECEIPT_SHA256 = (
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc"
)
ROOT_RECEIPT_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance"
    "-root-provenance-receipt.json"
)
ROOT_RECEIPT_SHA256 = (
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99"
)
V19_SOURCE_PATH = "tools/reproduce_owned_rust_buffer_shape_source_build_v19.py"
V19_SOURCE_SHA256 = "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c"
V19_PROTOCOL_PATH = "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V19.md"
V19_PROTOCOL_SHA256 = "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5"
V19_CONTRACT_PATH = "oracle/phase2/rust-buffer-shape-source-build-v19.json"
V19_CONTRACT_SHA256 = "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46"
SCHEMA = "rebar-phase2-owned-rust-literal-findall-one-pass-v1-source-freeze"
MAX_OWNER_BYTES = 4 * 1024 * 1024
FUNCTION_START = b"static PyObject *rust_pattern_literal_findall_direct(\n"
FUNCTION_FOLLOW = b"\nstatic PyObject *bridge_bound_literal_findall("
ORIGINAL_FUNCTION = (
    b"static PyObject *rust_pattern_literal_findall_direct(\n"
    b"    PyObject *literal,\n"
    b"    PyObject *value,\n"
    b"    PyObject *pos,\n"
    b"    PyObject *endpos\n"
    b") {\n"
    b"    Py_ssize_t requested_pos;\n"
    b"    Py_ssize_t requested_end;\n"
    b"    if (!rust_window_indices(pos, endpos, &requested_pos, &requested_end)) return NULL;\n"
    b"    RustSubject subject;\n"
    b"    if (!rust_subject_open(&subject, literal, value, 0)) return NULL;\n"
    b"    size_t start;\n"
    b"    size_t end;\n"
    b"    rust_subject_clamp_window(&subject, requested_pos, requested_end, &start, &end);\n"
    b"    if (start > end) {\n"
    b"        rust_subject_release(&subject);\n"
    b"        return PyList_New(0);\n"
    b"    }\n"
    b"    size_t width = subject.text ? (size_t)PyUnicode_GET_LENGTH(literal) : (size_t)PyBytes_GET_SIZE(literal);\n"
    b"    if (width == 0) {\n"
    b"        rust_subject_release(&subject);\n"
    b"        return PyList_New(0);\n"
    b"    }\n"
    b"    Py_ssize_t count = 0;\n"
    b"    if (subject.text) {\n"
    b"        count = PyUnicode_Count(value, literal, (Py_ssize_t)start, (Py_ssize_t)end);\n"
    b"        if (count < 0) {\n"
    b"            rust_subject_release(&subject);\n"
    b"            return NULL;\n"
    b"        }\n"
    b"    } else {\n"
    b"        const void *needle = PyBytes_AS_STRING(literal);\n"
    b"        size_t cursor = start;\n"
    b"        while (cursor <= end && width <= end - cursor) {\n"
    b"            const uint8_t *hit = memmem(subject.data + cursor, end - cursor, needle, width);\n"
    b"            if (hit == NULL) break;\n"
    b"            count++;\n"
    b"            cursor = (size_t)(hit - subject.data) + width;\n"
    b"        }\n"
    b"    }\n"
    b"    PyObject *result = PyList_New(count);\n"
    b"    if (result == NULL || count == 0) {\n"
    b"        rust_subject_release(&subject);\n"
    b"        return result;\n"
    b"    }\n"
    b"    size_t cursor = start;\n"
    b"    for (Py_ssize_t index = 0; index < count; index++) {\n"
    b"        size_t begin;\n"
    b"        if (subject.text) {\n"
    b"            Py_ssize_t hit = width == 1\n"
    b"                ? PyUnicode_FindChar(value, PyUnicode_READ_CHAR(literal, 0), (Py_ssize_t)cursor, (Py_ssize_t)end, 1)\n"
    b"                : PyUnicode_Find(value, literal, (Py_ssize_t)cursor, (Py_ssize_t)end, 1);\n"
    b"            if (hit < 0) {\n"
    b"                if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, \"Rust literal search returned fewer matches than its count\");\n"
    b"                Py_DECREF(result);\n"
    b"                rust_subject_release(&subject);\n"
    b"                return NULL;\n"
    b"            }\n"
    b"            begin = (size_t)hit;\n"
    b"        } else {\n"
    b"            const uint8_t *hit = memmem(subject.data + cursor, end - cursor, PyBytes_AS_STRING(literal), width);\n"
    b"            if (hit == NULL) {\n"
    b"                PyErr_SetString(PyExc_RuntimeError, \"Rust literal search returned fewer matches than its count\");\n"
    b"                Py_DECREF(result);\n"
    b"                rust_subject_release(&subject);\n"
    b"                return NULL;\n"
    b"            }\n"
    b"            begin = (size_t)(hit - subject.data);\n"
    b"        }\n"
    b"\n"
    b"        size_t finish = begin + width;\n"
    b"        PyObject *piece;\n"
    b"        if (subject.text) {\n"
    b"            piece = PyUnicode_Substring(value, (Py_ssize_t)begin, (Py_ssize_t)finish);\n"
    b"        } else if (begin == 0 && finish == subject.length && PyBytes_CheckExact(value)) {\n"
    b"            piece = Py_NewRef(value);\n"
    b"        } else {\n"
    b"            piece = PyBytes_FromStringAndSize((const char *)subject.data + begin, (Py_ssize_t)width);\n"
    b"        }\n"
    b"        if (piece == NULL) {\n"
    b"            Py_DECREF(result);\n"
    b"            rust_subject_release(&subject);\n"
    b"            return NULL;\n"
    b"        }\n"
    b"        PyList_SET_ITEM(result, index, piece);\n"
    b"        cursor = finish;\n"
    b"    }\n"
    b"    rust_subject_release(&subject);\n"
    b"    return result;\n"
    b"}\n"
)
ONE_PASS_FUNCTION = (
    b"static PyObject *rust_pattern_literal_findall_direct(\n"
    b"    PyObject *literal,\n"
    b"    PyObject *value,\n"
    b"    PyObject *pos,\n"
    b"    PyObject *endpos\n"
    b") {\n"
    b"    Py_ssize_t requested_pos;\n"
    b"    Py_ssize_t requested_end;\n"
    b"    if (!rust_window_indices(pos, endpos, &requested_pos, &requested_end)) return NULL;\n"
    b"    RustSubject subject;\n"
    b"    if (!rust_subject_open(&subject, literal, value, 0)) return NULL;\n"
    b"    size_t start;\n"
    b"    size_t end;\n"
    b"    rust_subject_clamp_window(&subject, requested_pos, requested_end, &start, &end);\n"
    b"    if (start > end) {\n"
    b"        rust_subject_release(&subject);\n"
    b"        return PyList_New(0);\n"
    b"    }\n"
    b"    size_t width = subject.text ? (size_t)PyUnicode_GET_LENGTH(literal) : (size_t)PyBytes_GET_SIZE(literal);\n"
    b"    if (width == 0) {\n"
    b"        rust_subject_release(&subject);\n"
    b"        return PyList_New(0);\n"
    b"    }\n"
    b"    PyObject *result = PyList_New(0);\n"
    b"    if (result == NULL) {\n"
    b"        rust_subject_release(&subject);\n"
    b"        return NULL;\n"
    b"    }\n"
    b"    const uint8_t *needle = subject.text\n"
    b"        ? NULL\n"
    b"        : (const uint8_t *)PyBytes_AS_STRING(literal);\n"
    b"    Py_UCS4 character = subject.text && width == 1\n"
    b"        ? PyUnicode_READ_CHAR(literal, 0)\n"
    b"        : 0;\n"
    b"    size_t cursor = start;\n"
    b"    while (cursor <= end && width <= end - cursor) {\n"
    b"        size_t begin;\n"
    b"        if (subject.text) {\n"
    b"            Py_ssize_t hit = width == 1\n"
    b"                ? PyUnicode_FindChar(value, character, (Py_ssize_t)cursor, (Py_ssize_t)end, 1)\n"
    b"                : PyUnicode_Find(value, literal, (Py_ssize_t)cursor, (Py_ssize_t)end, 1);\n"
    b"            if (hit < 0) {\n"
    b"                if (PyErr_Occurred()) {\n"
    b"                    Py_DECREF(result);\n"
    b"                    rust_subject_release(&subject);\n"
    b"                    return NULL;\n"
    b"                }\n"
    b"                break;\n"
    b"            }\n"
    b"            begin = (size_t)hit;\n"
    b"        } else {\n"
    b"            const uint8_t *hit = memmem(\n"
    b"                subject.data + cursor, end - cursor, needle, width\n"
    b"            );\n"
    b"            if (hit == NULL) break;\n"
    b"            begin = (size_t)(hit - subject.data);\n"
    b"        }\n"
    b"        size_t finish = begin + width;\n"
    b"        if (\n"
    b"            rust_list_append_owned(\n"
    b"                result,\n"
    b"                rust_findall_item(&subject, (intptr_t)begin, (intptr_t)finish)\n"
    b"            ) != 0\n"
    b"        ) {\n"
    b"            Py_DECREF(result);\n"
    b"            rust_subject_release(&subject);\n"
    b"            return NULL;\n"
    b"        }\n"
    b"        cursor = finish;\n"
    b"    }\n"
    b"    rust_subject_release(&subject);\n"
    b"    return result;\n"
    b"}\n"
)

FIXED_OWNERS = (
    (
        "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3756,
    ),
    (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261,
    ),
    (
        "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875,
    ),
    (
        "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
        "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
        3929,
    ),
    (
        "oracle/phase1/p0-differential-fuzz-reference-v3.json",
        "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
        5288,
    ),
    (V19_SOURCE_PATH, V19_SOURCE_SHA256, 88532),
    (V19_PROTOCOL_PATH, V19_PROTOCOL_SHA256, 5808),
    (V19_CONTRACT_PATH, V19_CONTRACT_SHA256, 14975),
    (BUILD_RECEIPT_PATH, BUILD_RECEIPT_SHA256, 3486),
    (ROOT_RECEIPT_PATH, ROOT_RECEIPT_SHA256, 4367),
    (PREDECESSOR_PATH, PREDECESSOR_SHA256, 179961),
    (VARIANT_PATH, VARIANT_SHA256, 178950),
)

ALLOWED_OWNER_PATHS = frozenset(
    os.path.join(ROOT, path)
    for path in (
        SOURCE_PATH,
        PROTOCOL_PATH,
        CONTRACT_PATH,
        *(entry[0] for entry in FIXED_OWNERS),
    )
)

FORBIDDEN_IMPORTS = frozenset(
    (
        "re",
        "_sre",
        "regex",
        "ctypes",
        "subprocess",
        "multiprocessing",
        "socket",
        "time",
        "gzip",
        "bz2",
        "lzma",
        "tarfile",
        "zipfile",
    )
)

FORBIDDEN_AUDIT_EVENTS = frozenset(
    (
        "subprocess.Popen",
        "os.system",
        "os.posix_spawn",
        "os.posix_spawnp",
        "os.spawn",
        "os.fork",
        "os.forkpty",
        "ctypes.dlopen",
        "ctypes.dlsym",
        "socket.__new__",
        "socket.connect",
        "socket.bind",
        "socket.sendto",
        "time.sleep",
    )
)


class FreezeError(Exception):
    """An exact, source-only first-party Rust claim could not be proved."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "owner hashing requires exact bytes")
    return hashlib.sha256(raw).hexdigest()


def quote(value: str) -> str:
    require(type(value) is str, "JSON strings must have exact string type")
    escaped = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\f": "\\f",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
    }
    pieces = ['"']
    for character in value:
        point = ord(character)
        require(
            not 0xD800 <= point <= 0xDFFF,
            "canonical JSON cannot contain an unpaired surrogate",
        )
        if character in escaped:
            pieces.append(escaped[character])
        elif point < 32:
            pieces.append("\\u" + format(point, "04x"))
        else:
            pieces.append(character)
    pieces.append('"')
    return "".join(pieces)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= 32, "canonical JSON nesting is too deep")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return quote(value)
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(
            all(type(key) is str for key in value),
            "canonical JSON object keys must be strings",
        )
        return "{" + ",".join(
            quote(key) + ":" + canonical(value[key], depth + 1)
            for key in sorted(value)
        ) + "}"
    raise FreezeError("unsupported canonical JSON value")


def valid_sha256(value: str, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        label + " must be exactly 64 lowercase hexadecimal characters",
    )
    return value


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_AUDIT_EVENTS:
        raise FreezeError("source-only verification denied " + event)
    if event == "import":
        module = arguments[0] if arguments else None
        if (
            type(module) is str
            and module.partition(".")[0] in FORBIDDEN_IMPORTS
        ):
            raise FreezeError("source-only verification denied import " + module)
    if event != "open":
        return
    require(len(arguments) >= 3, "unverifiable open audit event")
    path, mode, flags = arguments[:3]
    require(type(path) is str, "source-only verification denied descriptor access")
    require(
        path in ALLOWED_OWNER_PATHS,
        "source-only verification denied unlisted file access",
    )
    require(
        mode in ("r", "rb"),
        "source-only verification denied writable file mode",
    )
    require(
        type(flags) is int
        and (flags & os.O_ACCMODE) == os.O_RDONLY
        and not (flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND)),
        "source-only verification denied writable file flags",
    )


def read_owner(path: str, expected_hash: str, expected_size: int | None) -> bytes:
    valid_sha256(expected_hash, path + " SHA-256")
    absolute = os.path.join(ROOT, path)
    require(absolute in ALLOWED_OWNER_PATHS, "owner is outside the read wall")
    before = os.stat(absolute, follow_symlinks=False)
    require(stat.S_ISREG(before.st_mode), "owner must be a real regular file")
    require(
        0 < before.st_size <= MAX_OWNER_BYTES,
        "owner exceeds the exact source-only size bound",
    )
    if expected_size is not None:
        require(before.st_size == expected_size, path + " has the wrong size")
    with builtins.open(absolute, "rb") as handle:
        opened = os.fstat(handle.fileno())
        require(
            (opened.st_dev, opened.st_ino, opened.st_size)
            == (before.st_dev, before.st_ino, before.st_size),
            path + " changed between stat and open",
        )
        raw = handle.read(before.st_size + 1)
        require(
            len(raw) == before.st_size,
            path + " changed or exceeded its bounded read",
        )
        after = os.fstat(handle.fileno())
        require(
            (after.st_dev, after.st_ino, after.st_size)
            == (opened.st_dev, opened.st_ino, opened.st_size),
            path + " changed during its bounded read",
        )
    require(sha256(raw) == expected_hash, path + " SHA-256 mismatch")
    return raw


def verify_one_function(predecessor: bytes, variant: bytes) -> None:
    require(type(predecessor) is bytes, "predecessor must be exact bytes")
    require(type(variant) is bytes, "variant must be exact bytes")
    require(
        predecessor.count(FUNCTION_START) == 1,
        "predecessor must contain exactly one literal-findall function",
    )
    require(
        variant.count(FUNCTION_START) == 1,
        "variant must contain exactly one literal-findall function",
    )
    old_start = predecessor.index(FUNCTION_START)
    old_end = predecessor.find(FUNCTION_FOLLOW, old_start)
    new_start = variant.index(FUNCTION_START)
    new_end = variant.find(FUNCTION_FOLLOW, new_start)
    require(old_end >= 0 and new_end >= 0, "function boundary is missing")
    require(
        predecessor[old_start:old_end] == ORIGINAL_FUNCTION,
        "the historical two-scan function is not exactly authenticated",
    )
    require(
        variant[new_start:new_end] == ONE_PASS_FUNCTION,
        "the owned single-scan function is not exactly authenticated",
    )
    require(
        predecessor[:old_start] == variant[:new_start],
        "bytes before literal-findall were modified",
    )
    require(
        predecessor[old_end:] == variant[new_end:],
        "bytes after literal-findall were modified",
    )
    require(
        ONE_PASS_FUNCTION.count(b"memmem(") == 1,
        "the bytes literal must have exactly one forward search",
    )
    require(
        ONE_PASS_FUNCTION.count(b"PyUnicode_Find(") == 1
        and ONE_PASS_FUNCTION.count(b"PyUnicode_FindChar(") == 1,
        "both native Unicode searches must be preserved exactly once",
    )
    require(
        b"PyUnicode_Count(" not in ONE_PASS_FUNCTION
        and b"PyList_New(count)" not in ONE_PASS_FUNCTION,
        "a pre-count or second full scan is forbidden",
    )
    require(
        ONE_PASS_FUNCTION.count(b"rust_subject_open(") == 1
        and ONE_PASS_FUNCTION.count(b"rust_subject_release(") == 6,
        "the original buffer acquisition and all six cleanup exits are required",
    )
    require(
        ONE_PASS_FUNCTION.count(b"rust_findall_item(") == 1
        and ONE_PASS_FUNCTION.count(b"rust_list_append_owned(") == 1,
        "owned value and amortized Python-list helpers must remain intact",
    )
    require(
        b"cursor <= end && width <= end - cursor" in ONE_PASS_FUNCTION,
        "the checked non-overlapping scan bound must be intact",
    )
    require(
        b"if (PyErr_Occurred())" in ONE_PASS_FUNCTION,
        "native Unicode search failures must not become successful misses",
    )


def contract_model(
    source_hash: str,
    source_bytes: int,
    protocol_hash: str,
    protocol_bytes: int,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "status": "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED",
        "family": "rust",
        "source": {
            "path": SOURCE_PATH,
            "sha256": source_hash,
            "bytes": source_bytes,
        },
        "protocol": {
            "path": PROTOCOL_PATH,
            "sha256": protocol_hash,
            "bytes": protocol_bytes,
        },
        "predecessor": {
            "path": PREDECESSOR_PATH,
            "sha256": PREDECESSOR_SHA256,
            "bytes": 179961,
            "lines": 4774,
            "native_build": {
                "label": "phase2-v19-rust-buffer-shape-root-provenance",
                "compiler_process_count": 28,
                "source_phase_count": 2,
                "publication_receipt": {
                    "path": BUILD_RECEIPT_PATH,
                    "sha256": BUILD_RECEIPT_SHA256,
                    "bytes": 3486,
                    "status": "PASS",
                },
                "root_provenance_receipt": {
                    "path": ROOT_RECEIPT_PATH,
                    "sha256": ROOT_RECEIPT_SHA256,
                    "bytes": 4367,
                    "status": "PASS",
                },
            },
        },
        "candidate_variant": {
            "path": VARIANT_PATH,
            "sha256": VARIANT_SHA256,
            "bytes": 178950,
            "lines": 4757,
            "changed_function": "rust_pattern_literal_findall_direct",
            "changed_function_count": 1,
            "all_other_predecessor_bytes_unchanged": True,
            "complete_independently_owned_source": True,
            "native_build": "NOT RUN",
            "matching": "NOT RUN",
            "qualified": False,
        },
        "frozen_python_reference": {
            "cpython": "3.14.6",
            "original_cases": 31237,
            "original_groups": 13,
            "named_private_waivers": 13,
            "additional_differential_property_cases": 8244,
            "reference_status": "PASS",
            "candidate_status": "NOT RUN",
        },
        "historical_practice_pilot": {
            "case_count": 864,
            "literal_findall_case_count": 0,
            "one_pass_variant_exercised": False,
            "one_pass_variant_timed": False,
            "effect_on_historical_pilot": "NOT MEASURED",
            "future_literal_practice_cases": "NOT FROZEN",
        },
        "required_future_gates": {
            "fresh_native_build_and_provenance": "NOT RUN",
            "complete_original_correctness": "NOT RUN",
            "complete_additional_correctness": "NOT RUN",
            "public_api_and_buffer_correctness": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "separately_frozen_literal_practice_cases": "NOT FROZEN",
        },
        "phase_boundary": {
            "archive_opens": 0,
            "candidate_processes_started": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "matching_operations": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "holdout_case_count": 4194304,
            "holdout": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "winner_selected": False,
            "external_regex_dependencies": 0,
            "stdlib_regex_delegation": False,
        },
    }


def expect_failure(callback: object, label: str) -> None:
    require(callable(callback), label + " is not callable")
    try:
        callback()
    except FreezeError:
        return
    raise FreezeError("hostile control was accepted: " + label)


def self_test() -> tuple[int, int]:
    positives = 0
    hostile = 0

    for index in range(192):
        prefix = ("/* synthetic prefix " + str(index) + " */\n").encode("ascii")
        suffix = FUNCTION_FOLLOW + (
            "PyObject *module) { /* synthetic suffix "
            + str(index)
            + " */ }\n"
        ).encode("ascii")
        old = prefix + ORIGINAL_FUNCTION + suffix
        new = prefix + ONE_PASS_FUNCTION + suffix
        verify_one_function(old, new)
        positives += 1

    for index in range(32):
        prefix = ("/* positive " + str(index) + " */\n").encode("ascii")
        suffix = FUNCTION_FOLLOW + (
            "PyObject *module) { /* bounded suffix "
            + str(index)
            + " */ }\n"
        ).encode("ascii")
        old = prefix + ORIGINAL_FUNCTION + suffix
        new = prefix + ONE_PASS_FUNCTION + suffix
        cases = (
            (old, b"X" + new, "modified prefix"),
            (old, new + b"X", "modified suffix"),
            (
                old.replace(FUNCTION_START, b"static PyObject *other(\n", 1),
                new,
                "missing original function",
            ),
            (
                old,
                new.replace(FUNCTION_START, b"static PyObject *other(\n", 1),
                "missing owned function",
            ),
            (
                old,
                new.replace(b"PyUnicode_FindChar(", b"PyUnicode_Count(", 1),
                "wrong Unicode single-character search",
            ),
            (
                old,
                new.replace(b"PyUnicode_Find(", b"PyUnicode_Count(", 1),
                "wrong Unicode multi-character search",
            ),
            (
                old,
                new.replace(b"memmem(", b"external_regex(", 1),
                "external bytes engine",
            ),
            (
                old,
                new.replace(b"rust_subject_release(&subject);", b"/* leak */", 1),
                "unbalanced subject lifetime",
            ),
            (
                old,
                new.replace(b"rust_list_append_owned(", b"PyList_SET_ITEM(", 1),
                "unsafe ownership",
            ),
            (
                old,
                new.replace(
                    b"width <= end - cursor",
                    b"width < end - cursor",
                    1,
                ),
                "wrong exact-width boundary",
            ),
            (
                old,
                new.replace(b"if (PyErr_Occurred())", b"if (0)", 1),
                "suppressed Unicode error",
            ),
            (
                old,
                new.replace(
                    b"rust_findall_item(&subject, (intptr_t)begin, (intptr_t)finish)",
                    b"Py_NewRef(value)",
                    1,
                ),
                "incorrect full-subject identity",
            ),
        )
        for bad_old, bad_new, label in cases:
            expect_failure(
                lambda a=bad_old, b=bad_new: verify_one_function(a, b),
                label,
            )
            hostile += 1

    allowed = os.path.join(ROOT, PREDECESSOR_PATH)
    for index in range(48):
        audit_wall("open", (allowed, "rb", os.O_RDONLY))
        positives += 1
        forbidden = (
            ("open", ("/tmp/holdout-" + str(index), "rb", os.O_RDONLY)),
            ("open", (allowed, "wb", os.O_WRONLY | os.O_CREAT)),
            ("open", (allowed, "r+", os.O_RDWR)),
            ("open", (index, "rb", os.O_RDONLY)),
            ("subprocess.Popen", ("candidate",)),
            ("ctypes.dlopen", ("engine.so",)),
            ("socket.connect", ("example.invalid",)),
            ("import", ("re", None, None, None, None)),
            ("import", ("_sre", None, None, None, None)),
            ("import", ("regex.fast", None, None, None, None)),
            ("import", ("time", None, None, None, None)),
            ("os.system", ("benchmark",)),
        )
        for event, arguments in forbidden:
            expect_failure(
                lambda e=event, a=arguments: audit_wall(e, a),
                "denied " + event,
            )
            hostile += 1

    for bad in ("", "a", "A" * 64, "g" * 64, "0" * 63, "0" * 65):
        expect_failure(
            lambda value=bad: valid_sha256(value, "synthetic pin"),
            "invalid SHA-256 pin",
        )
        hostile += 1

    expected = canonical({"z": [True, False, None, 2], "a": "line\n"})
    require(
        expected == '{"a":"line\\n","z":[true,false,null,2]}',
        "canonical JSON serialization changed",
    )
    positives += 1

    require(positives >= 200, "insufficient positive controls")
    require(hostile >= 900, "insufficient hostile controls")
    return positives, hostile


def parse_arguments(arguments: list[str]) -> tuple[str, str, str, str]:
    require(len(arguments) == 7, "one mode and exactly three SHA-256 pins are required")
    mode = arguments[0]
    require(
        mode in ("--self-test", "--verify-frozen-context"),
        "only the two frozen source-only modes are allowed",
    )
    pins: dict[str, str] = {}
    for index in range(1, len(arguments), 2):
        name = arguments[index]
        require(
            name in (
                "--source-sha256",
                "--protocol-sha256",
                "--contract-sha256",
            ),
            "unknown or unsafe source-only option",
        )
        require(name not in pins, "duplicate caller-controlled SHA-256 pin")
        pins[name] = valid_sha256(arguments[index + 1], name)
    require(len(pins) == 3, "all three caller-controlled SHA-256 pins are required")
    return (
        mode,
        pins["--source-sha256"],
        pins["--protocol-sha256"],
        pins["--contract-sha256"],
    )


def verify_pinned_interpreter() -> None:
    require(
        os.path.realpath(sys.executable) == PINNED_CPYTHON,
        "source verification requires the exact pinned CPython executable",
    )
    require(
        tuple(sys.version_info[:3]) == (3, 14, 6),
        "source verification requires exactly CPython 3.14.6",
    )
    require(
        sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314",
        "source verification requires the exact CPython 3.14 implementation",
    )
    require(
        sys.flags.isolated == 1,
        "source verification requires Python isolated mode (-I)",
    )
    require(
        sys.dont_write_bytecode is True,
        "source verification requires bytecode writes disabled (-B)",
    )


def verify_frozen_context(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> dict[str, object]:
    require(
        protocol_pin == PROTOCOL_SHA256,
        "caller did not pin the exact owned one-pass protocol",
    )
    source_raw = read_owner(SOURCE_PATH, source_pin, None)
    protocol_raw = read_owner(PROTOCOL_PATH, protocol_pin, 4515)
    contract_raw = read_owner(CONTRACT_PATH, contract_pin, None)
    authenticated: dict[str, bytes] = {}
    for path, expected_hash, expected_size in FIXED_OWNERS:
        authenticated[path] = read_owner(path, expected_hash, expected_size)
    verify_one_function(
        authenticated[PREDECESSOR_PATH],
        authenticated[VARIANT_PATH],
    )
    build = authenticated[BUILD_RECEIPT_PATH]
    provenance = authenticated[ROOT_RECEIPT_PATH]
    require(
        b'"build_status":"PASS"' in build
        and b'"actual_compiler_process_count":28' in build
        and PREDECESSOR_SHA256.encode("ascii") in build,
        "historical V19 native build does not attest the exact predecessor",
    )
    require(
        b'"status":"PASS"' in provenance
        and b'"actual_source_phase_count":2' in provenance
        and BUILD_RECEIPT_SHA256.encode("ascii") in provenance,
        "historical V19 root receipt does not attest the exact build receipt",
    )
    expected = (
        canonical(
            contract_model(
                source_pin,
                len(source_raw),
                protocol_pin,
                len(protocol_raw),
            )
        ).encode("utf-8")
        + b"\n"
    )
    require(
        contract_raw == expected,
        "contract is not exact canonical source-freeze evidence",
    )
    return {
        "status": "PASS",
        "schema": SCHEMA,
        "source_only": True,
        "authenticated_plaintext_owners": len(FIXED_OWNERS) + 3,
        "predecessor_sha256": PREDECESSOR_SHA256,
        "candidate_variant_sha256": VARIANT_SHA256,
        "changed_function_count": 1,
        "original_reference_cases": 31237,
        "additional_reference_cases": 8244,
        "existing_pilot_cases": 864,
        "existing_pilot_literal_findall_cases": 0,
        "native_build": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "native_libraries_loaded": 0,
        "candidate_processes_started": 0,
        "compiler_processes_started": 0,
        "archive_opens": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def main() -> int:
    mode, source_pin, protocol_pin, contract_pin = parse_arguments(sys.argv[1:])
    verify_pinned_interpreter()
    require(
        "re" not in sys.modules and "_sre" not in sys.modules,
        "source-only verification imported a forbidden matching engine",
    )
    sys.addaudithook(audit_wall)
    result = verify_frozen_context(source_pin, protocol_pin, contract_pin)
    result["mode"] = mode[2:]
    if mode == "--self-test":
        positive, hostile = self_test()
        result["positive_controls"] = positive
        result["hostile_controls"] = hostile
    require(
        "re" not in sys.modules and "_sre" not in sys.modules,
        "a forbidden matching engine was loaded during source verification",
    )
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FreezeError as error:
        sys.stderr.write("source-only Rust literal-findall verification failed: ")
        sys.stderr.write(str(error))
        sys.stderr.write("\n")
        raise SystemExit(1) from error
