#!/usr/bin/env python3
"""Freeze two first-party Rust buffer-error corrections without execution."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("a source-only Rust freeze must not import a regex engine")

import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_capture_shape_semantics_v1.py"
PROTOCOL = "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/rust-capture-shape-semantics-v1.json"
SCHEMA = "rebar-owned-rust-capture-shape-semantics-v1-source-freeze"
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_DEPTH = 48
MAX_JSON_ITEMS = 65_536
NOT_MEASURED = "NOT MEASURED"
DERIVED_BRIDGE_SHA256 = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
DERIVED_BRIDGE_BYTES = 179147
OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875),
    ("supplemental_oracle", "oracle/phase1/p0-differential-fuzz-reference-v3.json", "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff", 5288),
    ("substitution_oracle_source", "tools/independent_substitution_buffer_semantics_v2.py", "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573", 317541),
    ("shape_oracle_source", "tools/independent_shape_changing_buffer_semantics_v2.py", "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c", 137527),
    ("literal_bridge", "candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c", "b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112", 178950),
    ("selected_bridge", "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c", "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a", 179520),
    ("rust_engine_source", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    ("restored_public_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
    ("capture_feature_source", "tools/verify_owned_rust_captured_findall_source_v1.py", "61c4d4beda9baf82150a8ae5e47f78eb1363595a583f0317626e93beb5373832", 59368),
    ("capture_feature_protocol", "oracle/phase2/RUST-CAPTURED-FINDALL-ONE-PASS-V1.md", "ffcaeec11704a81a2fd5ca25d7fc746c8a66fab033bb1f108f0e6c19445079fe", 5953),
    ("capture_feature_contract", "oracle/phase2/rust-captured-findall-one-pass-v1.json", "ec396c100f606923f08d1969f283a9bb2bcf35dbf9edf9e9c5d2360057f9079b", 5320),
    ("actual_v21_native_build_receipt", "oracle/phase2/evidence/native-source-build-v21-rust-phase2-v21-rust-captured-findall-root-provenance-publication-receipt.json", "bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102", 3502),
    ("actual_v19_failure_receipt", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v21-rust-captured-findall-root-provenance-original-p0-v19-failures-publication-receipt.json", "e48a4115a85d827cbf16a32b6b44390d2bf4b092e1823989c9bcafe874fa04fe", 29374),
)

SUITES = (
    ("original_bounded_v5", 151, False, NOT_MEASURED, 0, "INFRASTRUCTURE FAILURE", 81, 2),
    ("public_v3", 864, False, NOT_MEASURED, 0, "INFRASTRUCTURE FAILURE", 82, 2),
    ("scanner_v3", 1024, False, NOT_MEASURED, 0, "INFRASTRUCTURE FAILURE", 83, 2),
    ("buffer_v3", 768, False, NOT_MEASURED, 0, "INFRASTRUCTURE FAILURE", 84, 2),
    ("managed_v1", 1024, True, 0, 1024, "PASS", 85, 0),
    ("scanner_verbose_v1", 2854, True, 0, 2854, "PASS", 86, 0),
    ("public_types_v1", 6912, True, 0, 6912, "PASS", 87, 0),
    ("substitution_v2", 5120, True, 240, 0, "SEMANTIC MISMATCH", 88, 1),
    ("shape_v2", 10240, True, 1056, 0, "SEMANTIC MISMATCH", 89, 1),
    ("public_surface_v19", 1376, True, 0, 1376, "PASS", 90, 0),
    ("subinterpreter_v2", 128, False, NOT_MEASURED, 0, "INFRASTRUCTURE FAILURE", 187, 2),
    ("pep688_v4", 264, True, 0, 264, "PASS", 188, 0),
    ("threaded_pattern_v1", 512, True, 0, 512, "PASS", 189, 0),
)

OUTER_LENGTH_REWRITE = b"""    if (
        PyUnicode_CompareWithASCIIString(
            message, "bad escape (end of pattern)"
        ) == 0
    ) {
        Py_ssize_t original_length = PyObject_Length(replacement);
        if (original_length < 0) {
            Py_DECREF(position);
            Py_DECREF(message);
            Py_DECREF(raised);
            return -1;
        }
        PyObject *original_position = PyLong_FromSsize_t(original_length - 1);
        if (original_position == NULL) {
            Py_DECREF(position);
            Py_DECREF(message);
            Py_DECREF(raised);
            return -1;
        }
        Py_SETREF(position, original_position);
    }

"""

FAILED_REPLACEMENT_ORIGINAL = b"""        } else {
            PyErr_Clear();
            if (PyObject_CheckBuffer(replacement)) {
"""

FAILED_REPLACEMENT_CORRECTED = b"""        } else {
            if (
                PyErr_ExceptionMatches(PyExc_BufferError)
                || (
                    PyMemoryView_Check(replacement)
                    && PyErr_ExceptionMatches(PyExc_ValueError)
                )
            ) {
                return -1;
            }
            PyErr_Clear();
            if (PyObject_CheckBuffer(replacement)) {
"""

CAPTURE_INSERTION = b"""    if (groups == 2) {
        PyObject *row = PyTuple_New(2);
        if (row == NULL) return -1;
        PyObject *first = rust_findall_item(subject, begins[1], ends[1]);
        if (first == NULL) {
            Py_DECREF(row);
            return -1;
        }
        PyTuple_SET_ITEM(row, 0, first);
        PyObject *second = rust_findall_item(subject, begins[2], ends[2]);
        if (second == NULL) {
            Py_DECREF(row);
            return -1;
        }
        PyTuple_SET_ITEM(row, 1, second);
        return rust_list_append_owned(result, row);
    }
"""

EXPECTED_LEDGER = (
    ("acquire", "subject", 0, 0, 1),
    ("acquire", "subject", 0, 1, 2),
    ("acquire", "replacement", 284, 0, 1),
    ("release", "replacement", None, 1, 0),
    ("release", "subject", None, 2, 1),
    ("release", "subject", None, 1, 0),
)
EXPECTED_ERRORS = (
    ("released-subject", "TypeError", "expected string or bytes-like object, got 'memoryview'"),
    ("released-replacement", "ValueError", "operation forbidden on released memoryview object"),
    ("writable-replacement-hash", "ValueError", "cannot hash writable memoryview object"),
    ("failing-replacement-exporter", "BufferError", "frozen substitution replacement exporter failure"),
    ("failing-replacement-hash", "TypeError", "frozen substitution replacement exporter hash failure"),
)


class FreezeError(Exception):
    """A first-party source-freeze obligation failed."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def valid_digest(value: object, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def quote(value: str) -> str:
    require(type(value) is str, "JSON keys and strings must be genuine text")
    escaped = {"\"": "\\\"", "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for char in value:
        point = ord(char)
        require(not 0xD800 <= point <= 0xDFFF, "unpaired JSON surrogate")
        result.append(escaped.get(char, "\\u" + format(point, "04x") if point < 32 else char))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "JSON exceeds its frozen depth")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quote(value)
    if type(value) is int:
        return str(value)
    if type(value) in (tuple, list):
        require(len(value) <= MAX_JSON_ITEMS, "JSON array exceeds its frozen bound")
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(len(value) <= MAX_JSON_ITEMS, "JSON object exceeds its frozen bound")
        require(all(type(item) is str for item in value), "JSON object has a nontext key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1) for key in sorted(value)) + "}"
    raise FreezeError("unsupported or nonfinite source-freeze JSON")


class StrictJSON:
    """Decode bounded evidence without importing json or a regex engine."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES, "JSON owner is unbounded")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("JSON owner is not strict UTF-8") from error
        self.index = 0
        self.items = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "JSON string required")
        self.index += 1
        output: list[str] = []
        escaped = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(output)
            if char != "\\":
                require(ord(char) >= 32 and not 0xD800 <= ord(char) <= 0xDFFF, "invalid JSON text")
                output.append(char)
                continue
            require(self.index < len(self.text), "incomplete JSON escape")
            char = self.text[self.index]
            self.index += 1
            if char != "u":
                require(char in escaped, "invalid short JSON escape")
                output.append(escaped[char])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(item in "0123456789abcdefABCDEF" for item in digits), "invalid JSON Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u", "unpaired high JSON surrogate")
                low_text = self.text[self.index + 2:self.index + 6]
                require(len(low_text) == 4 and all(item in "0123456789abcdefABCDEF" for item in low_text), "invalid low JSON surrogate")
                low = int(low_text, 16)
                require(0xDC00 <= low <= 0xDFFF, "unpaired high JSON surrogate")
                self.index += 6
                output.append(chr(0x10000 + ((point - 0xD800) << 10) + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF, "unpaired low JSON surrogate")
                output.append(chr(point))
        raise FreezeError("unterminated JSON string")

    def number(self) -> int:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "incomplete JSON integer")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or self.text[self.index] not in "0123456789", "leading JSON integer zero")
        else:
            require(self.text[self.index] in "123456789", "invalid JSON integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        require(self.index - start <= 128, "unbounded JSON integer")
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"), "noninteger or nonfinite evidence")
        return int(self.text[start:self.index])

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "JSON exceeds its frozen depth")
        self.whitespace()
        require(self.index < len(self.text), "missing JSON value")
        char = self.text[self.index]
        if char == '"':
            return self.string()
        if char == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "duplicate evidence key: " + key)
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "unbounded JSON evidence")
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":", "missing JSON colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "invalid JSON object separator")
        if char == "[":
            self.index += 1
            result_list: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result_list
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "unbounded JSON evidence")
                result_list.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result_list
                require(separator == ",", "invalid JSON array separator")
        if char == "-" or char in "0123456789":
            return self.number()
        for literal, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return value
        raise FreezeError("invalid or nonfinite JSON evidence")

    def decode(self) -> object:
        value = self.value()
        self.whitespace()
        require(self.index == len(self.text), "trailing or concatenated JSON evidence")
        return value


ALLOWED_PATHS = frozenset(
    (ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT)
    + tuple(ROOT + "/" + owner[1] for owner in OWNERS)
)
BLOCKED_EVENTS: dict[str, int] = {}


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        name = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        destructive = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
        if type(name) is str and name in ALLOWED_PATHS and not name.endswith(".gz") and type(flags) is int and not flags & destructive:
            return
    elif event in {"import", "exec", "compile", "os.system", "os.rename", "os.remove", "os.mkdir", "os.rmdir", "os.chmod", "os.chown", "os.fork", "os.posix_spawn", "marshal.loads", "code.__new__", "function.__new__"} or event.startswith(("ctypes.", "subprocess.", "socket.", "multiprocessing.", "threading.", "tempfile.", "time.", "os.exec")):
        pass
    else:
        return
    BLOCKED_EVENTS[event] = BLOCKED_EVENTS.get(event, 0) + 1
    raise FreezeError("source-only audit wall rejected " + event)


def no_matcher_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma", "candidates", "rebar")
    require(
        not any(name == root or name.startswith(root + ".") for name in sys.modules for root in forbidden),
        "a Python matcher, external regex engine, or candidate was imported",
    )


def read_owner(path: str, expected_hash: str, expected_size: int | None = None) -> bytes:
    valid_digest(expected_hash, path)
    absolute = ROOT + "/" + path
    require(absolute in ALLOWED_PATHS and not absolute.endswith(".gz"), "unlisted, hidden, or compressed owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot open pinned plaintext owner: " + path) from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "owner is not one private regular file: " + path)
        require(0 < before.st_size <= MAX_OWNER_BYTES, "owner is outside its frozen size bound: " + path)
        require(expected_size is None or before.st_size == expected_size, "pinned owner size changed: " + path)
        pieces: list[bytes] = []
        count = 0
        while count < before.st_size:
            block = os.read(descriptor, min(65_536, before.st_size - count))
            require(bool(block), "pinned owner was truncated during its single read: " + path)
            pieces.append(block)
            count += len(block)
        require(os.read(descriptor, 1) == b"", "pinned owner grew during its single read: " + path)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns", "st_nlink")
    require(all(getattr(before, item) == getattr(after, item) for item in identity), "owner identity changed during its single read: " + path)
    raw = b"".join(pieces)
    require(count == before.st_size and digest(raw) == expected_hash, "pinned owner SHA-256 changed: " + path)
    return raw


def split_function(raw: bytes, start: bytes, follow: bytes, label: str) -> tuple[bytes, bytes, bytes]:
    require(type(raw) is bytes and raw.count(start) == 1, "missing or duplicated C function: " + label)
    first = raw.index(start)
    require(raw.count(follow, first + len(start)) == 1, "missing or duplicated C function boundary: " + label)
    last = raw.index(follow, first + len(start))
    return raw[:first], raw[first:last], raw[last:]


def assert_preserved_function(original: bytes, changed: bytes, start: bytes, follow: bytes, label: str) -> None:
    _, old, _ = split_function(original, start, follow, label)
    _, new, _ = split_function(changed, start, follow, label)
    require(old == new, "an untargeted first-party function changed: " + label)


def derive_bridge(original: bytes, predecessor: bytes) -> bytes:
    require(digest(original) == OWNERS[6][2] and len(original) == OWNERS[6][3], "the actually tested a0b9 Rust bridge changed")
    require(digest(predecessor) == OWNERS[5][2] and len(predecessor) == OWNERS[5][3], "the immediate first-party literal predecessor changed")
    capture_start = b"static int rust_append_batched_findall("
    capture_follow = b"\nstatic PyObject *rust_batched_findall("
    left, old_capture, right = split_function(original, capture_start, capture_follow, "captured findall")
    previous_left, previous_capture, previous_right = split_function(predecessor, capture_start, capture_follow, "literal findall")
    require(left == previous_left and right == previous_right, "the historical 17-line capture change is not the only predecessor difference")
    require(old_capture.count(CAPTURE_INSERTION) == 1 and old_capture.replace(CAPTURE_INSERTION, b"", 1) == previous_capture, "the complete two-capture fast path changed")

    helper_start = b"static int rust_restore_original_template_error("
    helper_follow = b"\nstatic int rust_replacement_cache("
    before, helper, after = split_function(original, helper_start, helper_follow, "template-error restoration")
    require(helper.count(OUTER_LENGTH_REWRITE) == 1, "the exact outer-length rewrite is missing or duplicated")
    fixed_helper = helper.replace(OUTER_LENGTH_REWRITE, b"", 1)
    require(b"PyObject_Length(replacement)" not in fixed_helper, "a shape-changing exporter still receives an outer-length probe")
    require(fixed_helper.count(b"PyObject_GetAttrString(raised, \"pos\")") == 1, "the parser's authentic visible-buffer error position was not preserved")
    require(fixed_helper.count(b"(PyObject *)Py_TYPE(raised), message, replacement, position, NULL") == 1, "the original exception type, message, exporter, or visible position changed")
    partially_corrected = before + fixed_helper + after

    cache_start = b"static int rust_replacement_cache("
    cache_follow = b"\nstatic PyObject *rust_normalize_expand_buffer("
    before, cache, after = split_function(partially_corrected, cache_start, cache_follow, "replacement exporter failure")
    require(cache.count(FAILED_REPLACEMENT_ORIGINAL) == 1, "the first failed replacement-buffer branch is missing or duplicated")
    fixed_cache = cache.replace(FAILED_REPLACEMENT_ORIGINAL, FAILED_REPLACEMENT_CORRECTED, 1)
    require(fixed_cache.count(FAILED_REPLACEMENT_CORRECTED) == 1, "the role-specific replacement error correction is missing")
    require(fixed_cache.count(b"PyObject_GetBuffer(") == cache.count(b"PyObject_GetBuffer("), "the correction added or omitted a buffer acquisition")
    require(fixed_cache.count(b"PyBuffer_Release(") == cache.count(b"PyBuffer_Release("), "the correction added or omitted a buffer release")
    require(fixed_cache.count(b"PyObject_Hash(") == cache.count(b"PyObject_Hash("), "the correction changed custom hash execution")
    changed = before + fixed_cache + after

    preserved = (
        (b"static int rust_subject_open(", b"\nstatic int rust_subject_match(", "released-subject error and visible subject acquisition"),
        (b"static int rust_append_batched_findall(", b"\nstatic PyObject *rust_batched_findall(", "complete two-capture fast path"),
        (b"static int rust_output_capture(", b"\nstatic int rust_output_template(", "reentrant nested capture and subject lifetime"),
        (b"static PyObject *rust_normalize_expand_buffer(", b"\nstatic PyObject *rust_match_expand(", "released and writable expansion buffers"),
        (b"static PyObject *rust_substitute_core(", b"\nstatic PyObject *rust_bound_substitute(", "callbacks, zero-width progression, and replacement lifetime"),
    )
    for start, follow, label in preserved:
        assert_preserved_function(original, changed, start, follow, label)
    require(changed != original, "the proposed engine correction is not materially different source")
    require(
        len(changed) == DERIVED_BRIDGE_BYTES
        and digest(changed) == DERIVED_BRIDGE_SHA256,
        "the complete two-function first-party bridge is not the frozen exact derivation",
    )
    added = FAILED_REPLACEMENT_CORRECTED
    forbidden = (b'PyImport_ImportModule("re")', b'PyImport_ImportModule("_sre")', b'PyImport_ImportModule("regex")', b"#include <regex.h>", b"#include <pcre", b"dlopen(", b"system(", b"PyRun_", b"subprocess", b"fallback")
    require(not any(marker in added for marker in forbidden), "the correction introduced a delegated matching engine or fallback")
    return changed


def validate_oracle_sources(substitution: bytes, shape: bytes) -> None:
    required_substitution = (
        b'SIMPLE_BUFFER_FLAG = 0',
        b'FULL_READONLY_BUFFER_FLAG = 284',
        b'synthetic_event("acquire", "subject", flags=0, before=0, after=1',
        b'synthetic_event("acquire", "subject", flags=0, before=1, after=2',
        b'synthetic_event("acquire", "replacement", flags=284, before=0, after=1',
        b'synthetic_event("release", "replacement", flags=None, before=1, after=0',
        b'synthetic_event("release", "subject", flags=None, before=2, after=1',
        b'synthetic_event("release", "subject", flags=None, before=1, after=0',
        b'expected string or bytes-like object, got \'memoryview\'',
        b'operation forbidden on released memoryview object',
        b'cannot hash writable memoryview object',
        b'frozen substitution replacement exporter failure',
        b'frozen substitution replacement exporter hash failure',
    )
    for marker in required_substitution:
        require(marker in substitution, "the frozen role-specific substitution oracle changed: " + marker.decode("ascii", "replace"))
    required_shape = (
        b'WITNESSED_REGRESSION_OUTER_SIZE = 13',
        b'WITNESSED_REGRESSION_NESTED_SIZES = (0, 1, 2, 5, 8)',
        b'self.append_event("length-probe", "outer", None, self.active, self.active)',
        b'return len(self.backing)',
        b'return len(subject.nested.backing)',
        b'"module.sub", "module.subn", "pattern.sub", "pattern.subn", "match.expand"',
        b'"captures", "zero-lookahead", "empty", "optional-captures"',
        b'"literal", "named", "numeric", "invalid", "missing"',
    )
    for marker in required_shape:
        require(marker in shape, "the frozen visible-buffer shape oracle changed: " + marker.decode("ascii", "replace"))


def validate_original_oracle(value: object) -> dict[str, object]:
    require(type(value) is dict, "the frozen original Python oracle must be an object")
    checks = (
        ("schema", "rebar-cpython-re-p0-completeness-v4"),
        ("status", "PASS"),
        ("original_case_execution_denominator", 31237),
        ("original_suite_count", 13),
        ("original_named_private_waiver_count", 13),
        ("first_party_candidate_family_count", 6),
        ("qualified_candidate_count", 0),
        ("holdout", "NOT OPENED"),
        ("performance", NOT_MEASURED),
    )
    for key, expected in checks:
        require(value.get(key) == expected, "the frozen original correctness oracle changed: " + key)
    phase = value.get("phase_gate")
    candidate = value.get("candidate_qualification_gate")
    supplement = value.get("actual_supplemental_two_reference")
    require(type(phase) is dict and phase.get("status") == "PASS" and phase.get("final_holdout_authorized") is False, "the phase-one reference or holdout boundary changed")
    require(type(candidate) is dict and candidate.get("status") == "BLOCKED" and candidate.get("runtime_no_delegation") == "NOT ESTABLISHED", "unqualified candidate status was concealed")
    require(type(supplement) is dict and supplement.get("status") == "PASS" and supplement.get("actual_reference_worker_count") == 2 and supplement.get("case_count_per_worker") == [8244, 8244] and supplement.get("failed_per_worker") == [0, 0] and supplement.get("case_denominator_included_in_original_31237") is False, "the two independent 8,244-case references were combined or falsified")
    return value


def validate_supplemental_oracle(value: object) -> dict[str, object]:
    require(type(value) is dict and value.get("schema") == "rebar-owned-differential-fuzz-reference-v3", "the historical supplemental source contract changed")
    require(value.get("original_case_execution_denominator") == 31237 and value.get("original_suite_count") == 13 and value.get("case_denominator_included_in_original_31237") is False, "the historical supplemental denominator changed")
    corpus = value.get("supplemental_corpus")
    require(type(corpus) is dict and corpus.get("case_count") == 8244 and corpus.get("unique_record_case_count") == 8244, "the separate historical property and fuzz case count changed")
    seeds = value.get("seeds")
    require(type(seeds) is dict and len(seeds) == 7, "the seven unchanged differential seeds were dropped")
    return value


def validate_build_receipt(value: object) -> dict[str, object]:
    require(type(value) is dict, "the V21 public first-party native-build receipt changed")
    expected = (
        ("schema", "rebar-phase2-owned-rust-captured-findall-source-build-v21-durable-publication-receipt"),
        ("status", "PASS"),
        ("build_status", "PASS"),
        ("actual_compiler_process_count", 28),
        ("corrected_public_adapter_sha256", "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"),
        ("candidate_matching", "NOT RUN"),
        ("candidate_qualified", False),
        ("holdout", "NOT OPENED"),
        ("performance", NOT_MEASURED),
    )
    for key, expected_value in expected:
        require(value.get(key) == expected_value, "the actual first-party V21 build evidence changed: " + key)
    return value


def validate_capture_contract(value: object) -> dict[str, object]:
    require(type(value) is dict and value.get("schema") == "rebar-phase2-owned-rust-captured-findall-one-pass-v1-source-freeze", "the preserved captured-findall source freeze changed")
    bridge = value.get("candidate_variant")
    require(type(bridge) is dict and bridge.get("path") == OWNERS[6][1] and bridge.get("sha256") == OWNERS[6][2] and bridge.get("bytes") == OWNERS[6][3] and bridge.get("specialized_capture_count") == 2, "the exact existing two-capture specialization was lost")
    previous = value.get("immediate_literal_predecessor")
    require(type(previous) is dict and previous.get("path") == OWNERS[5][1] and previous.get("sha256") == OWNERS[5][2] and previous.get("bytes") == OWNERS[5][3], "the independently written literal predecessor changed")
    return value


def validate_v19_receipt(value: object) -> dict[str, object]:
    require(type(value) is dict, "the actual Rust V19 campaign receipt must be an object")
    expected = (
        ("schema", "rebar-owned-repaired-rust-original-campaign-v19-durable-publication-receipt"),
        ("publication_status", "PASS"),
        ("candidate_status", "FAIL"),
        ("candidate_qualified", False),
        ("case_execution_denominator", 31237),
        ("suite_count", 13),
        ("attempted_suite_count", 13),
        ("completed_suite_count", 8),
        ("actual_candidate_workers", 13),
        ("distinct_worker_process_id_count", 13),
        ("infrastructure_failure_count", 5),
        ("verified_passing_case_count", 12942),
        ("semantic_mismatch_count", NOT_MEASURED),
        ("named_private_waiver_count", 13),
        ("combined_bridge_source_sha256", OWNERS[6][2]),
        ("corrected_public_adapter_sha256", "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"),
        ("all_original_observation_vectors_complete", False),
        ("holdout", "NOT OPENED"),
        ("hidden_cases_read", 0),
        ("benchmark_files_read", 0),
        ("clock_samples", 0),
        ("performance", NOT_MEASURED),
        ("memory", NOT_MEASURED),
        ("winner_selected", False),
    )
    for key, expected_value in expected:
        require(value.get(key) == expected_value, "a genuine Rust V19 campaign outcome changed: " + key)
    rows = value.get("suite_integrity")
    require(type(rows) is list and len(rows) == len(SUITES), "a real Rust V19 worker was dropped, duplicated, or reordered")
    for actual, expected_row in zip(rows, SUITES, strict=True):
        require(type(actual) is dict, "a genuine Rust V19 suite row was forged")
        observed = (actual.get("suite"), actual.get("case_execution_denominator"), actual.get("fully_observed"), actual.get("mismatch_count"), actual.get("verified_passing_case_count"), actual.get("failure_class"), actual.get("pid"), actual.get("returncode"))
        require(observed == expected_row and actual.get("actual_worker_started") is True and actual.get("worker_attempted") is True, "a genuine original V19 suite outcome changed: " + expected_row[0])
        valid_digest(actual.get("complete_original_row_sha256"), "complete original suite row " + expected_row[0])
    require(sum(row[1] for row in SUITES) == 31237 and sum(row[4] for row in SUITES) == 12942, "case or proven-pass accounting changed")
    require(len({row[6] for row in SUITES}) == 13, "the 13 independent actual Rust worker identities changed")
    return value


def validate_ledger(events: object) -> tuple[tuple[object, ...], ...]:
    require(type(events) in (tuple, list) and len(events) == 6, "the complete six-event buffer lifetime is required")
    active = {"subject": 0, "replacement": 0}
    stack: list[str] = []
    normalized: list[tuple[object, ...]] = []
    for event in events:
        require(type(event) in (tuple, list) and len(event) == 5, "a complete role-specific buffer event is required")
        kind, role, flags, before, after = event
        require(role in active and type(before) is int and type(after) is int and before == active[role], "a nested exporter owner or active count was forged")
        if kind == "acquire":
            require(type(flags) is int and flags in (0, 284) and after == before + 1, "a SIMPLE or FULL_READONLY buffer flag was changed")
            stack.append(role)
            active[role] = after
        else:
            require(kind == "release" and flags is None and after == before - 1 and bool(stack) and stack[-1] == role, "a nested buffer release was leaked or reordered")
            stack.pop()
            active[role] = after
        normalized.append((kind, role, flags, before, after))
    result = tuple(normalized)
    require(not stack and active == {"subject": 0, "replacement": 0}, "a first-party exporter was not released")
    require(result == EXPECTED_LEDGER, "the exact subject-0, subject-0, replacement-284 role or LIFO order changed")
    return result


def validate_visible_position(outer: object, nested: object, position: object) -> int:
    require(type(outer) is int and type(nested) is int and type(position) is int, "visible exporter sizes must be genuine integers")
    require(outer == 13 and nested in (0, 1, 2, 5, 8) and position == nested - 1, "a template position was derived from outer storage rather than visible nested bytes")
    return position


def validate_error(case: object) -> tuple[str, str, str]:
    require(type(case) in (tuple, list) and len(case) == 3, "a role-specific original exception is required")
    result = tuple(case)
    require(result in EXPECTED_ERRORS, "a released subject, replacement, hash, or exporter error was substituted")
    return result


def load_context() -> tuple[dict[str, bytes], bytes, dict[str, object]]:
    observed: dict[str, bytes] = {}
    for name, path, expected_hash, size in OWNERS:
        observed[name] = read_owner(path, expected_hash, size)
    validate_original_oracle(StrictJSON(observed["original_oracle"]).decode())
    validate_supplemental_oracle(StrictJSON(observed["supplemental_oracle"]).decode())
    validate_oracle_sources(observed["substitution_oracle_source"], observed["shape_oracle_source"])
    validate_capture_contract(StrictJSON(observed["capture_feature_contract"]).decode())
    validate_build_receipt(StrictJSON(observed["actual_v21_native_build_receipt"]).decode())
    receipt = validate_v19_receipt(StrictJSON(observed["actual_v19_failure_receipt"]).decode())
    derived = derive_bridge(observed["selected_bridge"], observed["literal_bridge"])
    validate_ledger(EXPECTED_LEDGER)
    for nested in (0, 1, 2, 5, 8):
        validate_visible_position(13, nested, nested - 1)
    for error in EXPECTED_ERRORS:
        validate_error(error)
    return observed, derived, receipt


def build_contract(source_hash: str, source: bytes, protocol_hash: str, protocol: bytes, derived: bytes) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "status": "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED",
        "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS",
        "family": "rust",
        "source": {"path": SOURCE, "sha256": source_hash, "bytes": len(source)},
        "protocol": {"path": PROTOCOL, "sha256": protocol_hash, "bytes": len(protocol)},
        "authenticated_plaintext_owners": [
            {"name": name, "path": path, "sha256": owner_hash, "bytes": size}
            for name, path, owner_hash, size in OWNERS
        ],
        "observed_previous_candidate": {
            "receipt_sha256": OWNERS[13][2],
            "publication_status": "PASS",
            "candidate_status": "FAIL",
            "candidate_qualified": False,
            "original_case_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "attempted_worker_count": 13,
            "completed_suite_count": 8,
            "infrastructure_failure_count": 5,
            "verified_passing_case_count": 12942,
            "global_semantic_mismatch_count": NOT_MEASURED,
            "fully_observed_mismatch_lower_bound": 1296,
            "fully_observed_suite_mismatch_counts": {"shape_v2": 1056, "substitution_v2": 240},
            "passed_case_count_in_failing_suites": "NOT CLAIMED",
            "corrected_adapter_sha256": "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e",
        },
        "derived_first_party_bridge": {
            "derivation": "IN MEMORY ONLY; COMPLETE C SOURCE NOT WRITTEN",
            "source_base_path": OWNERS[6][1],
            "source_base_sha256": OWNERS[6][2],
            "source_base_bytes": OWNERS[6][3],
            "sha256": digest(derived),
            "bytes": len(derived),
            "changed_function_count": 2,
            "changed_functions": ["rust_restore_original_template_error", "rust_replacement_cache"],
            "outer_length_probe_removed": True,
            "original_visible_pattern_position_preserved": True,
            "released_subject_error_path_changed": False,
            "released_replacement_error_preserved": "ValueError",
            "failing_replacement_export_error_preserved": "BufferError",
            "new_buffer_acquisitions": 0,
            "new_buffer_releases": 0,
            "new_hash_probes": 0,
            "reentrant_subject_capture_unchanged": True,
            "subject_subject_replacement_flags": [0, 0, 284],
            "complete_lifo_event_order": [list(item) for item in EXPECTED_LEDGER],
            "preserved_two_capture_insert_lines": 17,
            "preserved_matcher_engine_source_sha256": OWNERS[7][2],
            "new_external_regex_dependencies": 0,
            "new_stdlib_matching_delegation": False,
            "new_other_candidate_delegation": False,
            "match_outcome": NOT_MEASURED,
            "build": "NOT RUN",
            "qualification": "NOT ESTABLISHED",
        },
        "frozen_correctness_boundaries": {
            "cpython": "3.14.6",
            "original_case_count": 31237,
            "original_suite_count": 13,
            "named_private_waivers": 13,
            "supplemental_differential_case_count": 8244,
            "supplemental_counted_in_original_denominator": False,
            "qualified_independent_candidate_count": 0,
        },
        "phase_boundary": {
            "candidate_variant_build": "NOT RUN",
            "candidate_variant_matching": "NOT RUN",
            "candidate_variant_correctness": NOT_MEASURED,
            "candidate_variant_qualified": False,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "archive_opens": 0,
            "archive_inflations": 0,
            "private_root_opens": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "holdout": "NOT OPENED",
            "expanded_holdout_proposal_case_count": 14155776,
            "expanded_holdout_cases": "NOT GENERATED; NOT OPENED",
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def clone(value: object) -> object:
    return StrictJSON((canonical(value) + "\n").encode("utf-8")).decode()


def expect_rejection(label: str, action: object) -> None:
    try:
        action()
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError, OverflowError):
        return
    raise FreezeError("a hostile source-only control was accepted: " + label)


def self_test(observed: dict[str, bytes], derived: bytes, receipt: dict[str, object], expected: dict[str, object]) -> tuple[int, int]:
    rejected = 0

    def reject(label: str, action: object) -> None:
        nonlocal rejected
        expect_rejection(label, action)
        rejected += 1

    original = observed["selected_bridge"]
    predecessor = observed["literal_bridge"]
    reject("changed actual a0b9 bridge", lambda: derive_bridge(original + b"\n", predecessor))
    reject("changed literal predecessor", lambda: derive_bridge(original, predecessor + b"\n"))
    reject("removed captured findall fast path", lambda: derive_bridge(original.replace(CAPTURE_INSERTION, b"", 1), predecessor))
    reject("duplicated captured findall fast path", lambda: derive_bridge(original.replace(CAPTURE_INSERTION, CAPTURE_INSERTION * 2, 1), predecessor))
    reject("missing original outer-length bug", lambda: derive_bridge(original.replace(OUTER_LENGTH_REWRITE, b"", 1), predecessor))
    reject("duplicated original outer-length bug", lambda: derive_bridge(original.replace(OUTER_LENGTH_REWRITE, OUTER_LENGTH_REWRITE * 2, 1), predecessor))
    reject("missing failed replacement anchor", lambda: derive_bridge(original.replace(FAILED_REPLACEMENT_ORIGINAL, b"        } else {\n            return -1;\n", 1), predecessor))
    reject("reintroduced outer length probe", lambda: require(derived.replace(b"PyObject_GetAttrString(raised, \"pos\")", b"PyObject_Length(replacement)", 1) == derive_bridge(original, predecessor), "outer length probe was restored"))
    for start, follow, label in (
        (b"static int rust_subject_open(", b"\nstatic int rust_subject_match(", "released-subject error"),
        (b"static int rust_append_batched_findall(", b"\nstatic PyObject *rust_batched_findall(", "two-capture optimization"),
        (b"static int rust_output_capture(", b"\nstatic int rust_output_template(", "reentrant nested capture"),
        (b"static PyObject *rust_normalize_expand_buffer(", b"\nstatic PyObject *rust_match_expand(", "expand buffer and writable hash"),
        (b"static PyObject *rust_substitute_core(", b"\nstatic PyObject *rust_bound_substitute(", "callback and zero-width progression"),
    ):
        _, function, _ = split_function(derived, start, follow, label)
        reject("mutated preserved " + label, lambda key=start, end=follow, title=label, bad=function: assert_preserved_function(original, derived.replace(bad, bad + b"\n", 1), key, end, title))

    for index, forged in (
        (0, ("acquire", "replacement", 0, 0, 1)),
        (1, ("acquire", "subject", 0, 0, 1)),
        (2, ("acquire", "replacement", 0, 0, 1)),
        (3, ("release", "subject", None, 2, 1)),
        (4, ("release", "replacement", None, 1, 0)),
        (5, ("release", "subject", None, 2, 1)),
    ):
        changed = list(EXPECTED_LEDGER)
        changed[index] = forged
        reject("forged role, 284 flag, active count, or LIFO event " + str(index), lambda value=changed: validate_ledger(value))
    reject("missing exporter release", lambda: validate_ledger(EXPECTED_LEDGER[:-1]))
    swapped = list(EXPECTED_LEDGER)
    swapped[3], swapped[4] = swapped[4], swapped[3]
    reject("reordered cross-role LIFO releases", lambda: validate_ledger(swapped))
    for nested in (0, 1, 2, 5, 8):
        reject("outer-length-derived position for nested " + str(nested), lambda size=nested: validate_visible_position(13, size, 12))
        reject("out-of-bounds nested position " + str(nested), lambda size=nested: validate_visible_position(13, size, size))
    for role, exception, message in EXPECTED_ERRORS:
        reject("wrong exception type for " + role, lambda label=role, text=message: validate_error((label, "RuntimeError", text)))
        reject("wrong exception message for " + role, lambda label=role, kind=exception: validate_error((label, kind, "fabricated error")))
    reject("subject and replacement released errors conflated", lambda: validate_error(("released-subject", "ValueError", "operation forbidden on released memoryview object")))
    reject("replacement and subject released errors conflated", lambda: validate_error(("released-replacement", "TypeError", "expected string or bytes-like object, got 'memoryview'")))

    def forged_receipt(label: str, key: str, value: object) -> None:
        wrong = clone(receipt)
        require(type(wrong) is dict, "the V19 hostile receipt clone failed")
        wrong[key] = value
        reject(label, lambda item=wrong: validate_v19_receipt(item))

    for key, value in (
        ("publication_status", "FAIL"), ("candidate_status", "PASS"),
        ("candidate_qualified", True), ("case_execution_denominator", 31236),
        ("suite_count", 12), ("attempted_suite_count", 12),
        ("completed_suite_count", 13), ("actual_candidate_workers", 12),
        ("distinct_worker_process_id_count", 12), ("infrastructure_failure_count", 0),
        ("verified_passing_case_count", 29941), ("semantic_mismatch_count", 1296),
        ("named_private_waiver_count", 12), ("all_original_observation_vectors_complete", True),
        ("hidden_cases_read", 1), ("benchmark_files_read", 1),
        ("clock_samples", 1), ("holdout", "OPENED"),
        ("performance", "1.5x"), ("winner_selected", True),
    ):
        forged_receipt("falsified actual V19 " + key, key, value)
    for index, field, value in (
        (7, "mismatch_count", 0), (8, "mismatch_count", 0),
        (7, "verified_passing_case_count", 4880),
        (8, "verified_passing_case_count", 9184),
        (0, "fully_observed", True), (0, "failure_class", "PASS"),
        (4, "pid", 81), (11, "returncode", 1),
    ):
        wrong = clone(receipt)
        require(type(wrong) is dict and type(wrong.get("suite_integrity")) is list, "the hostile suite clone failed")
        wrong["suite_integrity"][index][field] = value
        reject("forged genuine V19 suite " + str(index) + ":" + field, lambda item=wrong: validate_v19_receipt(item))

    for malformed in (
        b'{"a":1,"a":2}', b'{"a":01}', b'{"a":NaN}',
        b'{"a":Infinity}', b'{"a":"\\uD800"}', b'{"a":"\\uDC00"}',
        b'{"a":1}{"a":2}', b'{"a":1,}', b'[1,]', b'{"a":1.5}',
    ):
        reject("duplicate, malformed, nonfinite, or noncanonical JSON", lambda raw=malformed: StrictJSON(raw).decode())
    for key, value in (
        ("candidate_variant_build", "PASS"), ("candidate_variant_matching", "PASS"),
        ("candidate_variant_correctness", "PASS"), ("candidate_variant_qualified", True),
        ("candidate_imports", 1), ("candidate_workers_started", 1),
        ("compiler_processes_started", 1), ("native_libraries_loaded", 1),
        ("archive_opens", 1), ("private_root_opens", 1),
        ("hidden_cases_read", 1), ("benchmark_files_read", 1),
        ("holdout", "OPENED"), ("clock_samples", 1),
        ("performance", "1.5x"), ("qualified_candidate_count", 1),
        ("winner_selected", True),
    ):
        wrong = clone(expected)
        require(type(wrong) is dict and type(wrong.get("phase_boundary")) is dict, "the hostile contract clone failed")
        wrong["phase_boundary"][key] = value
        reject("fabricated phase-boundary " + key, lambda item=wrong: require(item == expected, "source-only effects were fabricated"))

    physical = (
        ("unlisted plaintext", lambda: builtins.open("/etc/hosts", "rb")),
        ("compressed candidate failures", lambda: builtins.open(ROOT + "/oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v21-rust-captured-findall-root-provenance-original-p0-v19-failures.json.gz", "rb")),
        ("hidden holdout", lambda: builtins.open(ROOT + "/benchmarks/holdout.json", "rb")),
        ("source mutation", lambda: builtins.open(ROOT + "/" + SOURCE, "w")),
        ("stdlib regular expression", lambda: sys.audit("import", "re", None, None, None, None)),
        ("CPython matching engine", lambda: sys.audit("import", "_sre", None, None, None, None)),
        ("external regular-expression package", lambda: sys.audit("import", "regex", None, None, None, None)),
        ("candidate activation", lambda: sys.audit("import", "candidates.rust_candidate", None, None, None, None)),
        ("native dynamic loader", lambda: sys.audit("ctypes.dlopen", "forbidden.so")),
        ("compiler or worker", lambda: sys.audit("subprocess.Popen", "rustc", (), None, None)),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("clock sample", lambda: sys.audit("time.monotonic")),
        ("dynamic code", lambda: sys.audit("exec", "forbidden")),
        ("temporary private root", lambda: sys.audit("tempfile.mkdtemp", "/tmp/forbidden")),
        ("destructive rename", lambda: sys.audit("os.rename", "old", "new", -1, -1)),
    )
    for label, action in physical:
        reject("source-only audit wall: " + label, action)
    require(sum(BLOCKED_EVENTS.values()) >= len(physical), "physical source-only audit controls were not rejected")
    no_matcher_imports()
    return rejected, len(physical)


def parse_arguments() -> tuple[str, dict[str, str]]:
    arguments = sys.argv[1:]
    require(bool(arguments), "exactly one source-only verification mode is mandatory")
    mode = arguments[0]
    require(mode in ("--render-contract", "--self-test", "--verify-frozen-context"), "unknown or repeated source-only mode")
    required = ("--source-sha256", "--protocol-sha256")
    if mode != "--render-contract":
        required += ("--contract-sha256",)
    require(len(arguments) == 1 + len(required) * 2, "exactly the independent source, protocol, and contract pins are mandatory")
    pins: dict[str, str] = {}
    for offset in range(1, len(arguments), 2):
        key, value = arguments[offset], arguments[offset + 1]
        require(key in required and key not in pins, "unknown or repeated frozen owner pin")
        pins[key] = valid_digest(value, key)
    require(set(pins) == set(required), "a required frozen owner pin is missing")
    return mode, pins


def main() -> int:
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6) and sys.executable == PYTHON, "the exact stable CPython 3.14.6 oracle is mandatory")
    require(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, "run source-only checks with exact -I -B -S")
    no_matcher_imports()
    digest(b"source-only first-party Rust capture-shape semantic freeze")
    mode, pins = parse_arguments()
    sys.addaudithook(audit_wall)
    source = read_owner(SOURCE, pins["--source-sha256"])
    protocol = read_owner(PROTOCOL, pins["--protocol-sha256"])
    observed, derived, receipt = load_context()
    expected = build_contract(pins["--source-sha256"], source, pins["--protocol-sha256"], protocol, derived)
    encoded = (canonical(expected) + "\n").encode("utf-8")
    if mode == "--render-contract":
        no_matcher_imports()
        sys.stdout.write(encoded.decode("utf-8"))
        return 0
    actual = read_owner(CONTRACT, pins["--contract-sha256"])
    require(actual == encoded and StrictJSON(actual).decode() == expected, "the independently pinned canonical source contract changed")
    controls = 0
    physical = 0
    if mode == "--self-test":
        controls, physical = self_test(observed, derived, receipt, expected)
    result = {
        "schema": SCHEMA + "-source-only-gate",
        "status": "PASS",
        "mode": mode.removeprefix("--"),
        "authenticated_plaintext_owner_count": len(OWNERS) + 3,
        "source_only_hostile_controls": controls,
        "physical_audit_wall_controls": physical,
        "actual_v19_candidate_status": "FAIL",
        "actual_v19_publication_status": "PASS",
        "actual_v19_completed_suite_count": 8,
        "actual_v19_infrastructure_failure_count": 5,
        "actual_v19_verified_passing_case_count": 12942,
        "actual_v19_global_mismatch_count": NOT_MEASURED,
        "actual_v19_observed_suite_mismatch_counts": {"shape_v2": 1056, "substitution_v2": 240},
        "original_case_denominator": 31237,
        "separate_differential_case_count": 8244,
        "derived_bridge_sha256": digest(derived),
        "derived_bridge_bytes": len(derived),
        "derived_bridge_build": "NOT RUN",
        "derived_bridge_correctness": NOT_MEASURED,
        "qualified_candidate_count": 0,
        "performance": NOT_MEASURED,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    no_matcher_imports()
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
        sys.stderr.write("Rust capture-shape source freeze failed: " + str(error) + "\n")
        raise SystemExit(1)
