#!/usr/bin/env python3
"""Freeze the first-party Rust replacement-before-subject event-order repair.

Self-test and source verification authenticate public plaintext owners only.
They never open a candidate, native artifact, compressed archive, timer,
benchmark, final holdout, proposal, or private root.  Exactly one already
materialized, capture-clamped, no-external-introspection bridge may be opened
only by the separately pushed, explicitly root-authorized exclusive apply.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("source-only substitution freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
DEVICE = 2064
SCHEMA = "rebar-owned-rust-substitution-event-order-v1-source-freeze"
SOURCE = "tools/apply_owned_rust_substitution_event_order_v1.py"
PROTOCOL = "oracle/phase2/RUST-SUBSTITUTION-EVENT-ORDER-V1.md"
CONTRACT = "oracle/phase2/rust-substitution-event-order-v1.json"
INPUT = "candidates/rust/variants/no_external_introspection_v1/py_bridge.c"
TARGET_DIRECTORY = "candidates/rust/variants/substitution_event_order_v1"
TARGET = TARGET_DIRECTORY + "/py_bridge.c"
INPUT_SHA256 = "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7"
INPUT_BYTES = 177146
INPUT_INODE = 524811
OUTPUT_SHA256 = "c69e24a87c251a332b79c4f4b5ed1a9f232847e446518930473a2ec871f020ab"
OUTPUT_BYTES = 177335
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 250_000
MAX_JSON_DEPTH = 80
FINAL_HOLDOUT = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
SUBSTITUTION_MATRIX_SHA256 = (
    "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54"
)
SHAPE_MATRIX_SHA256 = (
    "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8"
)
BUILD_PUBLICATION_SHA256 = (
    "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc"
)
V25_FAILURE_RECEIPT_SHA256 = (
    "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59"
)
V25_FAILURE_ARCHIVE_SHA256 = (
    "dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7"
)
NO_INTROSPECTION_APPLICATION_SHA256 = (
    "57e28ad65b538db5189f264904d303f37f13506022eae07b12185a52f2624a43"
)

# Only immutable public plaintext tools, protocols, contracts, and receipts.
# Candidate INPUT and either compressed archive are deliberately absent.
# role, relative pathname, complete SHA-256, byte count, device-2064 inode.
OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
     3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 524713),
    ("substitution_oracle_source",
     "tools/independent_substitution_buffer_semantics_v2.py",
     "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
     317541, 432058),
    ("shape_oracle_source",
     "tools/independent_shape_changing_buffer_semantics_v2.py",
     "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
     137527, 432070),
    ("no_introspection_source",
     "tools/apply_owned_rust_no_external_introspection_v1.py",
     "68cafe6b6bdf336aff162f86c4c9ddc1aec7607e312c09b2a032e7462e466ec7",
     61181, 430722),
    ("no_introspection_protocol",
     "oracle/phase2/RUST-NO-EXTERNAL-INTROSPECTION-V1.md",
     "15f068ecd0c1970d8bec1f9cb011072c09cb5d064938c24abe1088e4565268c3",
     6240, 526268),
    ("no_introspection_contract",
     "oracle/phase2/rust-no-external-introspection-v1.json",
     "224e118a3878692552b31d588b38ea4953bee9c77c7853687b424360776b53d2",
     5305, 526270),
    ("no_introspection_application",
     "oracle/phase2/evidence/rust-no-external-introspection-v1-application.json",
     NO_INTROSPECTION_APPLICATION_SHA256, 1774, 524813),
    ("capture_clamp_source",
     "tools/apply_owned_rust_capture_clamp_semantics_v1.py",
     "ff4b45f370bb6df1a3693cb1046031df93f3dffb336f4cca695768a1adb34fb7",
     71522, 429579),
    ("capture_clamp_protocol",
     "oracle/phase2/RUST-CAPTURE-CLAMP-SEMANTICS-V1.md",
     "15bd3b25b3f86638ddcb45cbc11d962341a905903a4cd52a632f6c3f1a078ff9",
     4645, 526033),
    ("capture_clamp_contract",
     "oracle/phase2/rust-capture-clamp-semantics-v1.json",
     "46344723f24c65c123c4550c9652b3547866a2ae1a8419444d3359eb048294c6",
     11342, 526034),
    ("capture_clamp_application",
     "oracle/phase2/evidence/rust-capture-clamp-semantics-v1-application.json",
     "881c8b3583509f341f4851734a87f7e1e536c88ace7ae04473326b6a3a6d06df",
     2426, 526065),
    ("v25_build_source",
     "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py",
     "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408",
     186263, 429530),
    ("v25_build_protocol",
     "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md",
     "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85",
     7140, 525993),
    ("v25_build_contract",
     "oracle/phase2/rust-capture-clamp-source-build-v25.json",
     "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a",
     229419, 526066),
    ("v25_build_publication",
     "oracle/phase2/evidence/native-source-build-v25-rust-"
     "phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json",
     BUILD_PUBLICATION_SHA256, 5231, 526084),
    ("v25_campaign_source",
     "tools/run_owned_repaired_rust_original_campaign_v25.py",
     "09074713ee068a01dc91c07db68a7efcd4500f9b92990699f5e849fa77410edc",
     100824, 430716),
    ("v25_campaign_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V25.md",
     "9a2d0a3a71e998750cc6213a7ad4c42c6a8bf8a022347af55723d2407aa345e1",
     5638, 526197),
    ("v25_campaign_contract",
     "oracle/phase2/repaired-rust-original-campaign-v25.json",
     "230e4c98914b0ca2b1d4bc55eb9d7cf38474eed835626c2639916bd4ed581c1a",
     57478, 526253),
    ("v25_complete_failure_receipt",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v25-rust-capture-clamp-v1-root-provenance-"
     "original-p0-v25-failures-publication-receipt.json",
     V25_FAILURE_RECEIPT_SHA256, 11832, 524846),
)

COHORTS = (
    (57, "nested-stable-subject-and-template", "stable"),
    (58, "nested-mutating-subject-and-template", "mutate"),
    (59, "nested-stable-fixed-hash-template", "fixed-hash"),
    (60, "nested-mutating-unhashable-template", "unhashable"),
    (61, "nested-failing-template-after-subject", "fail"),
)
APIS = ("module.sub", "module.subn", "pattern.sub", "pattern.subn", "match.expand")
COUNTS = (0, 1, 2, 7)
SIMPLE = 0
FULL_READONLY = 284

CORE_START = (
    b"static PyObject *rust_substitute_core(PyObject *pattern, void *handle, "
    b"PyObject *groupindex, PyObject *pattern_value, PyObject *templates, "
    b"size_t groups, PyObject *replacement, PyObject *value, "
    b"Py_ssize_t limit, int want_count) {\n"
)
CORE_END = b"\nstatic PyObject *rust_bound_substitute("
CACHE_START = b"static int rust_replacement_cache("
EXPAND_START = b"static PyObject *rust_match_expand("
CAPTURE_START = b"static int rust_output_capture(\n"
CLAMP_FIRST = b"size_t first = begin > capture.length ? capture.length : begin;"
CLAMP_FINISH = b"size_t finish = end > capture.length ? capture.length : end;"
FULL_FLAG = b"materialization_flags = PyBUF_FULL_RO;"
CACHED_TEMPLATE = b'PyObject_CallMethod(pattern, "_cached_template", "OOn", normalized, subject, length)'

ORIGINAL_INITIAL = b"""    RustSubject subject = {0};
    int callback = PyCallable_Check(replacement);
    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (!rust_subject_open(&subject, pattern_value, value, 1)) {
        return NULL;
    }
    if (!callback) {
        if (subject.length > (size_t)PY_SSIZE_T_MAX) {
            rust_subject_release(&subject);
            return PyErr_NoMemory();
        }
        Py_ssize_t validation_length = (Py_ssize_t)subject.length;
        if (
            rust_replacement_cache(
                pattern, templates, replacement, value,
                validation_length, &raw, &tokens
            ) < 0
        ) {
            Py_XDECREF(raw);
            Py_XDECREF(tokens);
            rust_subject_release(&subject);
            return NULL;
        }
    }
"""

CORRECTED_INITIAL = b"""    RustSubject subject = {0};
    int callback = PyCallable_Check(replacement);
    int subject_acquired = 0;
    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (!callback) {
        if (
            rust_replacement_cache(
                pattern, templates, replacement, value,
                0, &raw, &tokens
            ) < 0
        ) {
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
    subject_acquired = 1;
    if (!callback && subject.length > (size_t)PY_SSIZE_T_MAX) {
        Py_XDECREF(raw);
        Py_XDECREF(tokens);
        rust_subject_release(&subject);
        return PyErr_NoMemory();
    }
"""

ORIGINAL_JOIN = b"""        if (previous < subject.length) {
            PyObject *tail = rust_findall_item(&subject, (intptr_t)previous, (intptr_t)subject.length);
            if (rust_list_append_owned(pieces, tail) != 0) goto substitute_error;
        }
        PyObject *separator = Py_GetConstant(subject.text ? Py_CONSTANT_EMPTY_STR : Py_CONSTANT_EMPTY_BYTES);
"""

CORRECTED_JOIN = b"""        if (previous < subject.length) {
            PyObject *tail = rust_findall_item(&subject, (intptr_t)previous, (intptr_t)subject.length);
            if (rust_list_append_owned(pieces, tail) != 0) goto substitute_error;
        }
        if (!callback) {
            rust_subject_release(&subject);
            subject_acquired = 0;
        }
        PyObject *separator = Py_GetConstant(subject.text ? Py_CONSTANT_EMPTY_STR : Py_CONSTANT_EMPTY_BYTES);
"""

ORIGINAL_SUCCESS = b"""    Py_XDECREF(tokens);
    rust_subject_release(&subject);
    return rust_sub_result(joined, replaced, want_count);
"""

CORRECTED_SUCCESS = b"""    Py_XDECREF(tokens);
    if (subject_acquired) rust_subject_release(&subject);
    return rust_sub_result(joined, replaced, want_count);
"""

ORIGINAL_FAILURE = b"""    Py_XDECREF(tokens);
    rust_subject_release(&subject);
    return NULL;
}
"""

CORRECTED_FAILURE = b"""    Py_XDECREF(tokens);
    if (subject_acquired) rust_subject_release(&subject);
    return NULL;
}
"""


class FreezeError(Exception):
    """Reject changed evidence, event ownership, or unauthorized side effects."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete genuine bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require a complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "JSON text must be a genuine string")
    replacements = {"\"": "\\\"", "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                    "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    output = ['"']
    for character in value:
        point = ord(character)
        require(not 0xD800 <= point <= 0xDFFF, "reject an unpaired JSON surrogate")
        output.append(replacements.get(character, "\\u" + format(point, "04x")
                      if point < 32 else character))
    output.append('"')
    return "".join(output)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive canonical JSON depth")
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
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject a nontext JSON key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported or nonfinite evidence JSON")


class StrictJSON:
    """Bounded, duplicate-rejecting JSON without importing json or a matcher."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require complete bounded public evidence bytes")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("reject invalid evidence UTF-8") from error
        self.index = 0
        self.items = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "require a JSON string")
        self.index += 1
        output: list[str] = []
        simple = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                  "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            character = self.text[self.index]
            self.index += 1
            if character == '"':
                return "".join(output)
            if character != "\\":
                require(ord(character) >= 32
                        and not 0xD800 <= ord(character) <= 0xDFFF,
                        "reject an invalid unescaped JSON character")
                output.append(character)
                continue
            require(self.index < len(self.text), "reject a truncated JSON escape")
            character = self.text[self.index]
            self.index += 1
            if character != "u":
                require(character in simple, "reject an unknown JSON escape")
                output.append(simple[character])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4
                    and all(item in "0123456789abcdefABCDEF" for item in digits),
                    "reject an invalid JSON Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject an unpaired high surrogate")
                low_digits = self.text[self.index + 2:self.index + 6]
                require(len(low_digits) == 4
                        and all(item in "0123456789abcdefABCDEF"
                                for item in low_digits), "reject a malformed low surrogate")
                low = int(low_digits, 16)
                require(0xDC00 <= low <= 0xDFFF, "reject an unpaired high surrogate")
                self.index += 6
                output.append(chr(0x10000 + ((point - 0xD800) << 10)
                                  + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF,
                        "reject an unpaired low surrogate")
                output.append(chr(point))
        raise FreezeError("reject an unterminated JSON string")

    def number(self) -> int:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject an incomplete JSON integer")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject a leading-zero JSON integer")
        else:
            require(self.text[self.index] in "123456789", "reject an invalid integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        require(self.index - start <= 128, "reject an oversized evidence integer")
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                "reject floating-point or nonfinite evidence")
        return int(self.text[start:self.index])

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject deeply nested public evidence")
        self.whitespace()
        require(self.index < len(self.text), "reject a missing JSON value")
        character = self.text[self.index]
        if character == '"':
            return self.string()
        if character == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "reject a duplicate JSON key: " + key)
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized public evidence")
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "reject a missing JSON object colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "reject a malformed JSON object")
        if character == "[":
            self.index += 1
            result: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized evidence array")
                result.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result
                require(separator == ",", "reject a malformed JSON array")
        if character == "-" or character in "0123456789":
            return self.number()
        for literal, result in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return result
        raise FreezeError("reject malformed, nonfinite, or substituted JSON")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing public evidence bytes")
        return result


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "rebar", "subprocess", "socket",
                 "threading", "multiprocessing", "gzip", "zipfile", "tarfile",
                 "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject a candidate, matcher, native loader, archive, or process import")


class SourceWall:
    """Deny-default, descriptor-relative, ticketed public owner isolation."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT)
                                + tuple(owner[1] for owner in OWNERS))
        self.allowed = self.public | (frozenset((INPUT,)) if apply else frozenset())
        self.live: dict[int, tuple[str, str]] = {}
        self.root: int | None = None
        self.open_ticket: tuple[str, int] | None = None
        self.mkdir_ticket: tuple[str, int] | None = None
        self.directory_created = False
        self.output_opened = False
        self.candidate_source_reads = 0
        self.public_owner_reads = 0
        self.workspace_mutations = 0
        self.denied: dict[str, int] = {}
        self.installed = False
        self.native_open = os.open
        self.native_read = os.read
        self.native_write = os.write
        self.native_fstat = os.fstat
        self.native_close = os.close
        self.native_fsync = os.fsync
        self.native_mkdir = os.mkdir

    def deny(self, reason: str) -> None:
        self.denied[reason] = self.denied.get(reason, 0) + 1
        raise FreezeError("source-only physical wall rejected " + reason)

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed-candidate-native-archive-holdout-or-write-open")
        if event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            if self.mkdir_ticket is not None and (path, mode) == self.mkdir_ticket:
                return
            self.deny("unticketed-workspace-directory-mutation")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.rmdir",
                      "os.chmod", "os.chown", "os.urandom", "os.getrandom",
                      "_interpreters.create", "_interpreters.exec",
                      "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.", "tempfile.",
                                     "time.", "os.exec", "os.spawn"))):
            self.deny("candidate-native-process-network-clock-or-code")

    def forbidden(self, reason: str):
        def reject(*_arguments: object, **_keywords: object) -> object:
            self.deny(reason)
        return reject

    def component(self, value: object) -> str:
        if (type(value) is not str or not value or value in (".", "..")
                or "/" in value or "\x00" in value):
            self.deny("unowned-or-traversal-path-component")
        assert isinstance(value, str)
        return value

    def ticket_open(self, path: str, flags: int, mode: int = 0,
                    *, directory: int | None = None) -> int:
        require(self.open_ticket is None, "reject nested native-open authorization")
        self.open_ticket = (path, flags)
        try:
            if directory is None:
                return self.native_open(path, flags, mode)
            return self.native_open(path, flags, mode, dir_fd=directory)
        finally:
            self.open_ticket = None

    def directory_flags(self) -> int:
        return (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0))

    def file_flags(self) -> int:
        return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)

    def open_root(self) -> None:
        require(self.installed and self.root is None,
                "open the exact isolated workspace root only once")
        descriptor = self.ticket_open(ROOT, self.directory_flags())
        owner = self.native_fstat(descriptor)
        require(stat.S_ISDIR(owner.st_mode) and owner.st_dev == DEVICE,
                "reject a substituted frozen workspace root")
        self.root = descriptor
        self.live[descriptor] = ("", "directory")

    def child(self, parent: int, component: str) -> int:
        component = self.component(component)
        current = self.live.get(parent)
        require(current is not None and current[1] == "directory",
                "reject a foreign parent directory descriptor")
        relative = component if not current[0] else current[0] + "/" + component
        allowed = (any(path.startswith(relative + "/") for path in self.allowed)
                   or self.apply and (relative == TARGET_DIRECTORY
                                      or TARGET_DIRECTORY.startswith(relative + "/")))
        require(allowed and not relative.startswith((".git/", ".agents/", ".codex/")),
                "reject an unowned, hidden, private, candidate, or holdout directory")
        descriptor = self.ticket_open(component, self.directory_flags(), directory=parent)
        owner = self.native_fstat(descriptor)
        require(stat.S_ISDIR(owner.st_mode) and owner.st_dev == DEVICE,
                "reject a substituted or symlink owner directory: " + relative)
        require(descriptor not in self.live, "reject a live descriptor alias")
        self.live[descriptor] = (relative, "directory")
        return descriptor

    def close(self, descriptor: int) -> None:
        require(type(descriptor) is int and descriptor in self.live
                and descriptor != self.root, "reject foreign or root descriptor closure")
        self.native_close(descriptor)
        del self.live[descriptor]

    def parent(self, relative: str) -> tuple[int, list[int], str]:
        require(type(relative) is str and relative in self.allowed,
                "reject an unowned source, candidate, archive, timer, or final holdout")
        require(self.root is not None, "open the isolated root descriptor first")
        components = relative.split("/")
        require(all(self.component(item) for item in components),
                "reject an invalid immutable owner path")
        descriptor = self.root
        stack: list[int] = []
        try:
            for item in components[:-1]:
                descriptor = self.child(descriptor, item)
                stack.append(descriptor)
            return descriptor, stack, components[-1]
        except BaseException:
            for item in reversed(stack):
                self.close(item)
            raise

    def read(self, relative: str, count: int | None, inode: int | None,
             expected: str) -> bytes:
        require(self.installed and relative in self.allowed,
                "candidate source is prohibited outside exclusive root-only apply")
        require(count is None or type(count) is int and 0 < count <= MAX_OWNER_BYTES,
                "reject an unbounded frozen plaintext owner")
        parent, stack, name = self.parent(relative)
        descriptor: int | None = None
        try:
            descriptor = self.ticket_open(name, self.file_flags(), directory=parent)
            self.live[descriptor] = (relative, "file")
            before = self.native_fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and stat.S_IMODE(before.st_mode) == 0o600
                    and before.st_dev == DEVICE
                    and 0 < before.st_size <= MAX_OWNER_BYTES
                    and (count is None or before.st_size == count)
                    and before.st_nlink == 1 and before.st_uid == os.geteuid()
                    and (inode is None or before.st_ino == inode),
                    "reject a substituted immutable owner: " + relative)
            chunks: list[bytes] = []
            remaining = before.st_size
            while remaining:
                chunk = self.native_read(descriptor, min(remaining, 65536))
                require(type(chunk) is bytes and bool(chunk),
                        "reject a truncated immutable owner: " + relative)
                chunks.append(chunk)
                remaining -= len(chunk)
            require(self.native_read(descriptor, 1) == b"",
                    "reject appended immutable owner bytes: " + relative)
            after = self.native_fstat(descriptor)
            require((after.st_dev, after.st_ino, after.st_size, after.st_mode,
                     after.st_mtime_ns, after.st_ctime_ns)
                    == (before.st_dev, before.st_ino, before.st_size, before.st_mode,
                        before.st_mtime_ns, before.st_ctime_ns),
                    "reject concurrently changed immutable owner: " + relative)
            raw = b"".join(chunks)
            require(digest(raw) == checked_sha(expected, relative),
                    "reject a changed complete immutable owner digest: " + relative)
            if relative == INPUT:
                require(self.apply and self.candidate_source_reads == 0,
                        "open the single pinned candidate source only in root apply")
                self.candidate_source_reads += 1
            else:
                self.public_owner_reads += 1
            return raw
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for item in reversed(stack):
                self.close(item)

    def create_target_directory(self) -> int:
        require(self.apply and not self.directory_created and self.root is not None,
                "authorize exactly one root-only new variant directory")
        descriptor = self.root
        stack: list[int] = []
        components = TARGET_DIRECTORY.split("/")
        try:
            for component in components[:-1]:
                descriptor = self.child(descriptor, component)
                stack.append(descriptor)
            name = self.component(components[-1])
            require(self.mkdir_ticket is None, "reject a nested directory ticket")
            self.mkdir_ticket = (name, 0o700)
            try:
                self.native_mkdir(name, 0o700, dir_fd=descriptor)
            finally:
                self.mkdir_ticket = None
            self.directory_created = True
            self.workspace_mutations += 1
            return self.child(descriptor, name)
        finally:
            for item in reversed(stack):
                self.close(item)

    def materialize(self, raw: bytes) -> None:
        require(self.apply and self.candidate_source_reads == 1
                and not self.output_opened,
                "authorize precisely one exclusive root-only corrected bridge")
        require(type(raw) is bytes and len(raw) == OUTPUT_BYTES
                and digest(raw) == OUTPUT_SHA256,
                "reject an unfrozen correction before any workspace mutation")
        directory = self.create_target_directory()
        descriptor: int | None = None
        try:
            flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
            descriptor = self.ticket_open("py_bridge.c", flags, 0o600,
                                          directory=directory)
            self.output_opened = True
            self.workspace_mutations += 1
            self.live[descriptor] = (TARGET, "output")
            written = 0
            while written < len(raw):
                amount = self.native_write(descriptor, raw[written:])
                require(type(amount) is int and amount > 0,
                        "reject a truncated exclusive corrected source write")
                written += amount
            owner = self.native_fstat(descriptor)
            require(stat.S_ISREG(owner.st_mode)
                    and stat.S_IMODE(owner.st_mode) == 0o600
                    and owner.st_dev == DEVICE and owner.st_size == OUTPUT_BYTES
                    and owner.st_nlink == 1 and owner.st_uid == os.geteuid(),
                    "reject substituted exclusive corrected source ownership")
            self.native_fsync(descriptor)
            self.close(descriptor)
            descriptor = None
            self.native_fsync(directory)
            readback = self.ticket_open("py_bridge.c", self.file_flags(),
                                        directory=directory)
            try:
                self.live[readback] = (TARGET, "readback")
                chunks: list[bytes] = []
                remaining = OUTPUT_BYTES
                while remaining:
                    chunk = self.native_read(readback, min(remaining, 65536))
                    require(bool(chunk), "reject incomplete durable source readback")
                    chunks.append(chunk)
                    remaining -= len(chunk)
                require(self.native_read(readback, 1) == b""
                        and digest(b"".join(chunks)) == OUTPUT_SHA256,
                        "reject the durable corrected-source readback digest")
            finally:
                self.close(readback)
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            self.close(directory)

    def install(self) -> None:
        require(not self.installed, "install the deny-default source wall exactly once")
        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                module.open_code = self.forbidden("direct-open-code")
        for name in ("open", "read", "write", "fstat", "close", "fsync", "mkdir",
                     "fdopen", "dup", "dup2", "stat", "lstat", "readlink", "listdir",
                     "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
                     "posix_spawnp", "system", "makedirs", "remove", "unlink",
                     "rename", "replace", "rmdir", "chmod", "chown", "urandom",
                     "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("direct-os-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns",
                     "thread_time", "thread_time_ns", "clock_gettime",
                     "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def extract_core(source: bytes) -> tuple[bytes, bytes, bytes]:
    require(source.count(CORE_START) == 1 and source.count(CORE_END) == 1,
            "require exactly one owned Rust substitution core and following boundary")
    start = source.index(CORE_START)
    finish = source.index(CORE_END, start + len(CORE_START))
    return source[:start], source[start:finish], source[finish:]


def preserved_source(source: bytes) -> None:
    anchors = (
        (CACHE_START, 1), (EXPAND_START, 1), (CAPTURE_START, 1),
        (CLAMP_FIRST, 1), (CLAMP_FINISH, 1), (FULL_FLAG, 1),
        (CACHED_TEMPLATE, 1), (b"static PyObject *bridge_bind(", 1),
        (b"Py_CLEAR(method->signature);", 2),
        (b"Py_VISIT(method->signature);", 1),
    )
    for anchor, count in anchors:
        require(source.count(anchor) == count,
                "preserve the clamped, no-introspection, first-party source surface")
    for forbidden in (b"rust_bound_get_signature", b'PyImport_ImportModule("inspect")',
                      b'PyImport_ImportModule("functools")',
                      b'PyImport_ImportModule("re")',
                      b'PyImport_ImportModule("regex")'):
        require(source.count(forbidden) == 0,
                "reject surviving external introspection or matcher delegation")


def transform(source: bytes, exact: bool = False) -> bytes:
    require(type(source) is bytes, "derive the repair from complete owned C bytes")
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA256,
                "reject an unauthenticated complete no-introspection bridge")
    preserved_source(source)
    before, core, after = extract_core(source)
    require(before.count(CACHE_START) == 1 and before.count(EXPAND_START) == 1
            and before.index(CACHE_START) < before.index(EXPAND_START),
            "require unchanged preceding replacement cache and match.expand")
    sites = ((ORIGINAL_INITIAL, CORRECTED_INITIAL),
             (ORIGINAL_JOIN, CORRECTED_JOIN),
             (ORIGINAL_SUCCESS, CORRECTED_SUCCESS),
             (ORIGINAL_FAILURE, CORRECTED_FAILURE))
    corrected = core
    for original, replacement in sites:
        require(corrected.count(original) == 1,
                "require each exact unique owned substitution-core correction site")
        require(corrected.count(replacement) == 0,
                "reject an already-applied or duplicated substitution correction")
        corrected = corrected.replace(original, replacement, 1)

    validation = corrected.index(b"rust_replacement_cache(\n")
    subject_open = corrected.index(b"rust_subject_open(&subject, pattern_value, value, 1)")
    require(validation < subject_open,
            "validate every noncallback replacement before acquiring the subject")
    require(corrected.count(b"                0, &raw, &tokens\n") == 1,
            "require exact safe zero-length adapter validation without subject export")
    require(corrected.count(b"int subject_acquired = 0;") == 1
            and corrected.count(b"subject_acquired = 1;") == 1
            and corrected.count(b"subject_acquired = 0;") == 2,
            "track exactly one subject acquisition and one deferred early release")
    deferred = corrected.index(CORRECTED_JOIN)
    early_release = corrected.index(b"rust_subject_release(&subject);", deferred)
    separator = corrected.index(b"PyObject *separator = Py_GetConstant(", deferred)
    join = corrected.index(b"PyBytes_Join(separator, pieces)", separator)
    require(deferred < early_release < separator < join,
            "release noncallback literal subject after tail copy and before bytes join")
    require(corrected.count(b"if (subject_acquired) rust_subject_release(&subject);")
            == 2, "guard the success and failure cleanup against duplicate release")
    require(corrected.count(b"if (!callback) {\n            rust_subject_release") == 1,
            "preserve callback ownership and condition early release on noncallbacks")

    reversed_core = corrected
    for original, replacement in reversed(sites):
        require(reversed_core.count(replacement) == 1,
                "reject a nonunique reversible substitution correction")
        reversed_core = reversed_core.replace(replacement, original, 1)
    require(reversed_core == core,
            "require byte-exact reversibility at only four sites in one C function")
    result = before + corrected + after
    preserved_source(result)
    result_before, _result_core, result_after = extract_core(result)
    require(result_before == before and result_after == after,
            "never change replacement cache, match.expand, engine, or other function")
    expected_delta = sum(len(replacement) - len(original)
                         for original, replacement in sites)
    require(len(result) == len(source) + expected_delta,
            "reject bytes outside the exact one-function event-order correction")
    if exact:
        require(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
                "reject drift in the complete predicted composed corrected bridge")
    return result


def synthetic_source() -> bytes:
    return b"".join((
        CACHE_START, b"void) {\n    ", FULL_FLAG, b"\n    ", CACHED_TEMPLATE,
        b";\n}\n", CAPTURE_START, b") {\n    ", CLAMP_FIRST, b"\n    ",
        CLAMP_FINISH, b"\n}\n", EXPAND_START, b"void) { return NULL; }\n",
        b"static PyObject *bridge_bind(\n", b"Py_CLEAR(method->signature);\n",
        b"Py_CLEAR(method->signature);\nPy_VISIT(method->signature);\n",
        CORE_START, ORIGINAL_INITIAL,
        b"    int deferred = callback || (tokens == Py_None);\n",
        b"    if (deferred) {\n", ORIGINAL_JOIN,
        b"        joined = PyBytes_Join(separator, pieces);\n    }\n",
        ORIGINAL_SUCCESS, b"substitute_error:\n", ORIGINAL_FAILURE,
        CORE_END, b"void) { return NULL; }\n",
    ))


def event(kind: str, role: str, flags: int | None = None,
          owner: str = "outer") -> tuple[str, str, int | None, str]:
    require(kind in ("acquire", "release", "acquire-error", "hash", "hash-error")
            and role in ("subject", "replacement")
            and owner in ("outer", "nested", "join")
            and (flags is None or flags in (SIMPLE, FULL_READONLY)),
            "require an exact synthetic PEP-688 ownership event")
    return kind, role, flags, owner


def validate_events(events: list[tuple[str, str, int | None, str]],
                    *, forbid_subject: bool = False) -> None:
    require(type(events) is list, "require a complete ordered synthetic event ledger")
    active = {"subject": 0, "replacement": 0}
    stack: list[str] = []
    for item in events:
        require(type(item) is tuple and len(item) == 4,
                "reject an incomplete synthetic exporter event")
        kind, role, flags, _owner = item
        require(kind in ("acquire", "release", "acquire-error", "hash", "hash-error")
                and role in active, "reject a forged exporter role or operation")
        if forbid_subject:
            require(role != "subject", "a failing replacement illegally touched its subject")
        if kind == "acquire":
            require(flags in (SIMPLE, FULL_READONLY), "preserve SIMPLE/FULL_RO flags")
            active[role] += 1
            stack.append(role)
        elif kind == "release":
            require(flags is None and active[role] > 0 and bool(stack)
                    and stack[-1] == role,
                    "reject an unmatched, reordered, or duplicate exporter release")
            active[role] -= 1
            stack.pop()
        elif kind == "acquire-error":
            require(flags in (SIMPLE, FULL_READONLY),
                    "preserve exact failing replacement acquisition flags")
        else:
            require(role == "replacement" and flags is None,
                    "preserve exact custom exporter hash ordering")
    require(not stack and all(value == 0 for value in active.values()),
            "require all subject and replacement exports to release exactly once")


def modeled_substitution_events(behavior: str, style: str,
                                variant: int) -> list[tuple[str, str, int | None, str]]:
    require(behavior in ("stable", "mutate", "fixed-hash", "unhashable", "fail")
            and style in ("literal", "escaped-named", "escaped-numeric"),
            "reject an unfrozen nested exporter cohort or replacement style")
    if behavior == "fail":
        result = [event("acquire-error", "replacement", SIMPLE),
                  event("acquire-error", "replacement", SIMPLE),
                  event("acquire-error", "replacement", FULL_READONLY)]
        validate_events(result, forbid_subject=True)
        return result

    result = [event("acquire", "replacement", SIMPLE),
              event("release", "replacement")]
    if style != "literal":
        if behavior == "fixed-hash":
            result.append(event("hash", "replacement"))
        flag = FULL_READONLY if behavior == "unhashable" else SIMPLE
        result.extend((event("acquire", "replacement", flag),
                       event("release", "replacement")))
    result.append(event("acquire", "subject", SIMPLE))
    result.append(event("release", "subject"))
    if style == "literal":
        count = COUNTS[(variant // len(APIS)) % len(COUNTS)]
        joins = min(count, 5) if count else 5
        result.extend(event("acquire", "replacement", SIMPLE, "join")
                      for _index in range(joins))
        result.extend(event("release", "replacement", owner="join")
                      for _index in range(joins))
    validate_events(result)
    return result


def synthetic_substitution_model() -> dict:
    by_cohort = {name: 0 for _index, name, _behavior in COHORTS}
    by_api = {name: 0 for name in APIS[:-1]}
    styles = {"literal": 0, "escaped-named": 0, "escaped-numeric": 0}
    failing = 0
    full_readonly = 0
    fixed_hash = 0
    cases: list[dict[str, object]] = []
    for cohort_index, cohort, behavior in COHORTS:
        for variant in range(80):
            api = APIS[variant % len(APIS)]
            style = ("literal", "escaped-named", "escaped-numeric", "callback")[variant % 4]
            if api == "match.expand" or style == "callback":
                continue
            assert style in ("literal", "escaped-named", "escaped-numeric")
            events = modeled_substitution_events(behavior, style, variant)
            if behavior == "fail":
                require(all(record[1] != "subject" for record in events),
                        "preserve BufferError without touching a failing template subject")
                failing += 1
            else:
                first_subject = next(index for index, record in enumerate(events)
                                     if record[1] == "subject")
                require(all(record[1] == "replacement"
                            for record in events[:first_subject]),
                        "validate exporter templates entirely before subject acquisition")
                if style == "literal":
                    subject_release = next(index for index, record in enumerate(events)
                                           if record[:2] == ("release", "subject"))
                    first_join = next(index for index, record in enumerate(events)
                                      if record[3] == "join")
                    require(subject_release < first_join,
                            "release literal subject before replacement joins reacquire")
                if behavior == "unhashable" and style != "literal":
                    require(any(record[2] == FULL_READONLY for record in events),
                            "preserve unhashable escaped replacement PyBUF_FULL_RO")
                    full_readonly += 1
                if behavior == "fixed-hash" and style != "literal":
                    require(sum(record[0] == "hash" for record in events) == 1,
                            "preserve exactly one fixed exporter hash")
                    fixed_hash += 1
            by_cohort[cohort] += 1
            by_api[api] += 1
            styles[style] += 1
            cases.append({"case": "substitution-buffer-semantics.v1."
                                   + format(cohort_index * 80 + variant, "05d"),
                          "cohort": cohort, "variant": variant, "api": api,
                          "style": style, "behavior": behavior,
                          "events": events,
                          "exception": "BufferError" if behavior == "fail" else None})
    require(len(cases) == 240 and all(count == 48 for count in by_cohort.values())
            and all(count == 60 for count in by_api.values())
            and styles == {"literal": 80, "escaped-named": 80,
                           "escaped-numeric": 80}
            and failing == 48 and full_readonly == 32 and fixed_hash == 32,
            "model all five authentic 48-case cohorts and all four 60-case APIs")
    require(sum(case["behavior"] != "fail" and case["style"] == "literal"
                for case in cases) == 64
            and sum(case["behavior"] != "fail"
                    and case["style"] != "literal" for case in cases) == 128,
            "preserve exactly 128 escaped, 64 literal, and 48 failing replacements")
    return {"case_count": len(cases), "case_projection_sha256": digest(
                canonical(cases).encode("utf-8")),
            "cohort_case_counts": by_cohort, "api_case_counts": by_api,
            "replacement_style_case_counts": styles,
            "successful_escaped_case_count": 128,
            "successful_literal_case_count": 64,
            "failing_replacement_case_count": failing,
            "full_readonly_escaped_case_count": full_readonly,
            "fixed_hash_escaped_case_count": fixed_hash,
            "failing_replacements_touch_subject": False,
            "callbacks_preserved_outside_model": True}


def synthetic_shape_model() -> dict:
    names = ("zero", "one", "two", "short", "five", "equal", "thirteen", "long")
    behaviors = ("stable", "mutate", "fail-outer", "fail-nested")
    by_api = {name: 0 for name in APIS[:-1]}
    by_behavior = {name: 0 for name in behaviors}
    failures = 0
    cases: list[tuple[str, str, str, str, tuple]] = []
    for outer in names:
        for nested in names:
            for api in APIS[:-1]:
                for behavior in behaviors:
                    if behavior == "fail-outer":
                        events = [event("acquire-error", "replacement", SIMPLE)]
                    elif behavior == "fail-nested":
                        events = [event("acquire", "replacement", SIMPLE),
                                  event("acquire-error", "replacement", SIMPLE,
                                        "nested"),
                                  event("release", "replacement")]
                    else:
                        events = [event("acquire", "replacement", SIMPLE),
                                  event("release", "replacement"),
                                  event("acquire", "subject", SIMPLE),
                                  event("release", "subject")]
                    is_failure = behavior.startswith("fail-")
                    validate_events(events, forbid_subject=is_failure)
                    by_api[api] += 1
                    by_behavior[behavior] += 1
                    failures += int(is_failure)
                    cases.append((outer, nested, api, behavior, tuple(events)))
    require(len(cases) == 1024 and failures == 512
            and all(count == 256 for count in by_api.values())
            and all(count == 256 for count in by_behavior.values()),
            "model all 1,024 shape-order inversions and all 512 BufferError cases")
    return {"case_count": len(cases), "case_projection_sha256": digest(
                canonical(cases).encode("utf-8")),
            "api_case_counts": by_api, "behavior_case_counts": by_behavior,
            "expected_buffer_error_count": failures,
            "expected_type_error_count": 0,
            "subject_acquired_for_failing_replacement_count": 0,
            "missing_outer_length_probe_substitution_case_count": 32,
            "missing_outer_length_probe_expand_case_count": 24,
            "redundant_match_expand_subject_reacquisition_case_count": 32,
            "shape_categories_can_overlap": True,
            "post_repair_measured_remaining_failure_count": "NOT MEASURED"}


def synthetic_tests(wall: SourceWall) -> dict:
    original = synthetic_source()
    corrected = transform(original)
    substitution = synthetic_substitution_model()
    shape = synthetic_shape_model()
    rejected = 0

    def reject(operation, label: str) -> None:
        nonlocal rejected
        try:
            operation()
        except (FreezeError, OSError, TypeError, ValueError, IndexError):
            rejected += 1
            return
        raise FreezeError("hostile source-only control unexpectedly passed: " + label)

    for anchor in (ORIGINAL_INITIAL, ORIGINAL_JOIN, ORIGINAL_SUCCESS,
                   ORIGINAL_FAILURE, CORE_START, CORE_END, CACHE_START,
                   EXPAND_START, CAPTURE_START, CLAMP_FIRST, CLAMP_FINISH,
                   FULL_FLAG, CACHED_TEMPLATE):
        reject(lambda value=anchor: transform(original.replace(value, b"", 1)),
               "missing exact first-party transformation or preservation anchor")
        reject(lambda value=anchor: transform(original.replace(value, value + value, 1)),
               "duplicated exact first-party transformation or preservation anchor")
    for site in (ORIGINAL_INITIAL, ORIGINAL_JOIN, ORIGINAL_SUCCESS, ORIGINAL_FAILURE):
        for offset in range(0, len(site), 31):
            changed = site[:offset] + bytes((site[offset] ^ 1,)) + site[offset + 1:]
            reject(lambda value=site, damage=changed: transform(
                original.replace(value, damage, 1)), "single-byte C source drift")
    for payload in (b'{"duplicate":1,"duplicate":2}', b"NaN", b"1.0", b"01",
                    b'{"surrogate":"\\ud800"}', b'{"safe":true} trailing'):
        reject(lambda raw=payload: StrictJSON(raw).decode(), "unsafe evidence JSON")
    reject(lambda: validate_events([event("release", "subject")]),
           "subject release without ownership")
    reject(lambda: validate_events([event("acquire", "subject", SIMPLE),
                                    event("release", "subject"),
                                    event("release", "subject")]),
           "duplicate subject release")
    reject(lambda: validate_events([event("acquire", "subject", SIMPLE),
                                    event("release", "subject")],
                                   forbid_subject=True),
           "failing replacement illegally acquires subject")
    reject(lambda: wall.parent(INPUT), "candidate source path in a source-only mode")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved primitive unticketed candidate source read")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level candidate source read")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "direct candidate source read")
    reject(lambda: builtins.open(ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json"),
           "invalidated final holdout proposal read")
    reject(lambda: builtins.open(
        ROOT + "/oracle/phase2/evidence/"
        "repaired-rust-original-campaign-v16-rust-phase2-v25-rust-"
        "capture-clamp-v1-root-provenance-original-p0-v25-failures.json.gz"),
        "original compressed failure archive read")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "workspace directory mutation")
    reject(lambda: time.time(), "clock sample")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native library load")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None),
           "compiler or candidate worker launch")
    reject(lambda: sys.audit("socket.connect", None, None), "network request")
    require(rejected >= 75 and wall.candidate_source_reads == 0
            and wall.workspace_mutations == 0,
            "require exhaustive hostile controls with no candidate reads or writes")
    no_matching_imports()
    return {"synthetic_original_source_bytes": len(original),
            "synthetic_corrected_source_bytes": len(corrected),
            "synthetic_source_delta_bytes": len(corrected) - len(original),
            "changed_function_count": 1, "exact_replacement_site_count": 4,
            "substitution_exporter_model": substitution,
            "shape_exporter_model": shape,
            "combined_targeted_historical_mismatch_count": 1264,
            "hostile_controls_rejected": rejected,
            "candidate_source_files_read": 0, "workspace_mutations": 0,
            "compressed_archives_opened": 0, "compressed_archives_inflated": 0,
            "clock_samples": 0, "candidate_executions": 0,
            "final_holdout": FINAL_HOLDOUT}


def value(document: object, name: str, expected: object) -> None:
    require(type(document) is dict and document.get(name) == expected,
            "reject incomplete or substituted immutable evidence: " + name)


def authenticated_evidence(owners: dict[str, bytes]) -> dict:
    phase1 = StrictJSON(owners["original_oracle"]).decode()
    value(phase1, "schema", "rebar-cpython-re-p0-completeness-v4")
    value(phase1, "version", 4)
    value(phase1, "original_case_execution_denominator", 31237)
    value(phase1, "original_suite_count", 13)
    original = phase1["original_oracle"]
    value(original, "case_execution_denominator", 31237)
    value(original, "suite_count", 13)
    suites = original["suites"]
    require(type(suites) is list and len(suites) == 13,
            "retain all thirteen immutable original correctness suites")
    selected = {row["id"]: row for row in suites
                if row.get("id") in ("substitution_v2", "shape_v2")}
    require(set(selected) == {"substitution_v2", "shape_v2"},
            "retain both complete independent original buffer-event suites")
    for suite, count, matrix, role in (
            ("substitution_v2", 5120, SUBSTITUTION_MATRIX_SHA256,
             "substitution_oracle_source"),
            ("shape_v2", 10240, SHAPE_MATRIX_SHA256, "shape_oracle_source")):
        row = selected[suite]
        value(row, "case_execution_count", count)
        value(row, "matrix_sha256", matrix)
        value(row["source"], "sha256", next(
            owner[2] for owner in OWNERS if owner[0] == role))
        value(row["source"], "path", next(
            owner[1] for owner in OWNERS if owner[0] == role))

    no_introspection = StrictJSON(owners["no_introspection_contract"]).decode()
    value(no_introspection, "schema",
          "rebar-owned-rust-no-external-introspection-v1-source-freeze")
    prior = no_introspection["exact_private_introspection_correction"]
    for key, expected in (("target_path", INPUT), ("target_sha256", INPUT_SHA256),
                          ("target_bytes", INPUT_BYTES),
                          ("capture_clamp_correction_retained", True),
                          ("matching_engine_changed", False),
                          ("external_regex_dependency_added", False),
                          ("stdlib_matching_delegation_added", False)):
        value(prior, key, expected)
    application = StrictJSON(owners["no_introspection_application"]).decode()
    for key, expected in (("schema", "rebar-owned-rust-no-external-introspection-"
                                      "v1-source-freeze-root-materialization"),
                          ("input_sha256", "a127ef85945a4dfa40a1b6c98f6c1a73"
                                            "ca7e1a487e190e8dde1d5aa2be47bb54"),
                          ("target_path", INPUT), ("target_sha256", INPUT_SHA256),
                          ("target_bytes", INPUT_BYTES),
                          ("capture_clamp_preserved", True),
                          ("public_native_descriptors_preserved", True),
                          ("source_sha256", OWNERS[4][2]),
                          ("protocol_sha256", OWNERS[5][2]),
                          ("contract_sha256", OWNERS[6][2])):
        value(application, key, expected)
    value(application["effects"], "candidate_executions", 0)
    value(application["effects"], "candidate_source_files_read", 1)

    clamp = StrictJSON(owners["capture_clamp_contract"]).decode()
    value(clamp, "schema", "rebar-owned-rust-capture-clamp-semantics-v1-source-freeze")
    capture = clamp["derived_first_party_capture_clamp"]
    value(capture, "fresh_export_begin_clamped", True)
    value(capture, "fresh_export_end_clamped", True)
    value(capture, "external_regex_dependency_added", False)
    clamp_application = StrictJSON(owners["capture_clamp_application"]).decode()
    value(clamp_application, "status", "PASS")
    value(clamp_application["materialized_variant"], "sha256",
          "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54")
    value(clamp_application["materialized_variant"], "bytes", 178805)

    build = StrictJSON(owners["v25_build_contract"]).decode()
    value(build, "schema",
          "rebar-phase2-owned-rust-capture-clamp-source-build-v25-source-freeze")
    value(build, "version", 25)
    build_variant = build["materialized_first_party_variant"]
    value(build_variant, "complete_source_sha256",
          "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54")
    value(build_variant, "complete_source_bytes", 178805)
    publication = StrictJSON(owners["v25_build_publication"]).decode()
    for key, expected in (("schema", "rebar-phase2-owned-rust-capture-clamp-"
                                      "source-build-v25-durable-publication-receipt"),
                          ("status", "PASS"), ("family", "rust"),
                          ("actual_compiler_process_count", 28),
                          ("candidate_workers_started", 0),
                          ("native_libraries_loaded", 0),
                          ("clock_samples", 0),
                          ("source_sha256", OWNERS[12][2]),
                          ("protocol_sha256", OWNERS[13][2]),
                          ("contract_sha256", OWNERS[14][2])):
        value(publication, key, expected)

    campaign = StrictJSON(owners["v25_campaign_contract"]).decode()
    value(campaign, "schema",
          "rebar-owned-repaired-rust-original-campaign-v25-recoverable-source-freeze")
    value(campaign, "version", 25)
    value(campaign, "family", "rust")
    value(campaign["original_correctness_boundary"], "case_execution_denominator", 31237)
    value(campaign["original_correctness_boundary"], "suite_count", 13)
    receipt = StrictJSON(owners["v25_complete_failure_receipt"]).decode()
    for key, expected in (("schema", "rebar-owned-repaired-rust-original-"
                                      "campaign-v25-durable-publication-receipt"),
                          ("status", "PASS"), ("publication_status", "PASS"),
                          ("publication_pass_means", "DURABLE PUBLICATION ONLY"),
                          ("family", "rust"), ("candidate_status", "FAIL"),
                          ("semantic_mismatch_count", 1352),
                          ("verified_passing_case_count", 15877),
                          ("case_execution_denominator", 31237),
                          ("suite_count", 13), ("completed_suite_count", 13),
                          ("actual_candidate_workers", 13),
                          ("distinct_worker_process_id_count", 13),
                          ("all_original_observation_vectors_complete", True),
                          ("actual_v25_build_archive_read_count", 0),
                          ("actual_v25_build_archive_gzip_inflation_count", 0),
                          ("actual_v25_build_receipt_sha256", BUILD_PUBLICATION_SHA256),
                          ("actual_v25_build_source_sha256", OWNERS[12][2]),
                          ("actual_v25_build_protocol_sha256", OWNERS[13][2]),
                          ("actual_v25_build_contract_sha256", OWNERS[14][2]),
                          ("campaign_source_sha256", OWNERS[16][2]),
                          ("campaign_protocol_sha256", OWNERS[17][2]),
                          ("campaign_contract_sha256", OWNERS[18][2]),
                          ("clock_samples", 0), ("timing_trials_run", 0),
                          ("winner_selected", False)):
        value(receipt, key, expected)
    archive = receipt["archive"]
    value(archive, "sha256", V25_FAILURE_ARCHIVE_SHA256)
    value(archive, "size_bytes", 3771743)
    value(archive, "inode", 524845)
    value(archive, "device", DEVICE)
    require(type(archive.get("relative")) is str
            and archive["relative"].endswith(".json.gz"),
            "authenticate the original failure archive by its published receipt only")
    integrity = receipt["suite_integrity"]
    require(type(integrity) is list and len(integrity) == 13
            and all(type(row) is dict and row.get("fully_observed") is True
                    for row in integrity),
            "preserve all thirteen fully observed original V25 suite outcomes")
    mismatches = {row["suite"]: row["mismatch_count"] for row in integrity
                  if row.get("mismatch_count", 0)}
    require(mismatches == {"substitution_v2": 240, "shape_v2": 1112}
            and sum(row.get("verified_passing_case_count", -1)
                    for row in integrity) == 15877,
            "retain the authentic 240 + 1112 original mismatch partition")
    return {"published_v25_complete_receipt_sha256": V25_FAILURE_RECEIPT_SHA256,
            "published_v25_build_receipt_sha256": BUILD_PUBLICATION_SHA256,
            "original_v25_failure_archive_sha256_receipt_only":
                V25_FAILURE_ARCHIVE_SHA256,
            "original_v25_failure_archive_bytes_receipt_only": 3771743,
            "original_v25_failure_archive_opened": False,
            "original_v25_failure_archive_inflated": False,
            "prior_candidate_status": "FAIL", "prior_semantic_mismatch_count": 1352,
            "prior_verified_passing_case_count": 15877,
            "prior_failing_suite_counts": mismatches,
            "historical_original_case_execution_denominator": 31237,
            "historical_original_suite_count": 13,
            "historical_original_actual_worker_count": 13,
            "capture_clamp_retained": True,
            "no_external_introspection_application_sha256":
                NO_INTROSPECTION_APPLICATION_SHA256,
            "no_external_introspection_retained": True,
            "candidate_input_source_opened": False,
            "final_holdout": FINAL_HOLDOUT}


def validate_contract(document: object, source_sha: str, protocol_sha: str) -> None:
    require(type(document) is dict, "require the complete event-order source contract")
    for key, expected in (("schema", SCHEMA), ("version", 1), ("family", "rust"),
                          ("phase", "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS"),
                          ("status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; "
                                     "NOT BUILT; NOT RUN"),
                          ("final_holdout", FINAL_HOLDOUT),
                          ("source", {"path": SOURCE, "sha256": source_sha}),
                          ("protocol", {"path": PROTOCOL, "sha256": protocol_sha})):
        value(document, key, expected)
    correction = document["exact_first_party_event_order_correction"]
    for key, expected in (("input_path", INPUT), ("input_sha256", INPUT_SHA256),
                          ("input_bytes", INPUT_BYTES), ("input_device", DEVICE),
                          ("input_inode", INPUT_INODE), ("input_mode", "0600"),
                          ("target_path", TARGET), ("target_sha256", OUTPUT_SHA256),
                          ("target_bytes", OUTPUT_BYTES),
                          ("source_delta_bytes", OUTPUT_BYTES - INPUT_BYTES),
                          ("changed_function_count", 1),
                          ("changed_function", "rust_substitute_core"),
                          ("exact_replacement_site_count", 4),
                          ("noncallback_replacement_validated_before_subject", True),
                          ("adapter_validation_length", 0),
                          ("failing_replacement_touches_subject", False),
                          ("escaped_replacement_hash_behavior_preserved", True),
                          ("unhashable_replacement_full_readonly_flags", FULL_READONLY),
                          ("deferred_noncallback_subject_released_after_tail_copy", True),
                          ("deferred_noncallback_subject_released_before_bytes_join", True),
                          ("callback_subject_ownership_unchanged", True),
                          ("duplicate_subject_release_precluded", True),
                          ("replacement_cache_function_unchanged", True),
                          ("match_expand_function_unchanged", True),
                          ("capture_clamp_correction_retained", True),
                          ("no_external_introspection_correction_retained", True),
                          ("matching_engine_changed", False),
                          ("stdlib_matching_delegation_added", False),
                          ("external_regex_dependency_added", False),
                          ("candidate_built", False), ("candidate_imported", False),
                          ("candidate_matching", "NOT RUN"),
                          ("candidate_qualified", False)):
        value(correction, key, expected)
    substitution = document["modeled_original_substitution_v2_failures"]
    for key, expected in (("original_suite_case_count", 5120),
                          ("historical_failure_count", 240),
                          ("nested_exporter_cohort_count", 5),
                          ("cases_per_nested_cohort", 48),
                          ("substitution_api_count", 4),
                          ("cases_per_substitution_api", 60),
                          ("successful_escaped_replacement_case_count", 128),
                          ("successful_literal_replacement_case_count", 64),
                          ("failing_replacement_case_count", 48),
                          ("failing_replacement_expected_exception", "BufferError"),
                          ("failing_replacement_subject_acquisition_count", 0),
                          ("matrix_sha256", SUBSTITUTION_MATRIX_SHA256),
                          ("candidate_semantics_after_correction", "NOT MEASURED")):
        value(substitution, key, expected)
    value(substitution, "cohort_case_counts", {
        name: 48 for _index, name, _behavior in COHORTS})
    shape = document["modeled_original_shape_v2_failures"]
    for key, expected in (("original_suite_case_count", 10240),
                          ("historical_failure_count", 1112),
                          ("targeted_evaluation_order_case_count", 1024),
                          ("targeted_api_count", 4),
                          ("targeted_cases_per_api", 256),
                          ("targeted_cases_per_behavior", 256),
                          ("expected_buffer_error_case_count", 512),
                          ("missing_outer_length_probe_substitution_case_count", 32),
                          ("missing_outer_length_probe_expand_case_count", 24),
                          ("redundant_match_expand_subject_reacquisition_case_count", 32),
                          ("untargeted_probe_or_expand_failure_count", 88),
                          ("historical_failure_categories_may_overlap", True),
                          ("post_correction_measured_remaining_failure_count",
                           "NOT MEASURED"),
                          ("matrix_sha256", SHAPE_MATRIX_SHA256)):
        value(shape, key, expected)
    value(document, "combined_targeted_historical_mismatch_count", 1264)
    lineage = document["immutable_published_v25_failure"]
    for key, expected in (("complete_publication_receipt_sha256",
                           V25_FAILURE_RECEIPT_SHA256),
                          ("build_publication_receipt_sha256",
                           BUILD_PUBLICATION_SHA256),
                          ("archive_sha256_receipt_only", V25_FAILURE_ARCHIVE_SHA256),
                          ("archive_bytes_receipt_only", 3771743),
                          ("archive_opened", False), ("archive_inflated", False),
                          ("candidate_status", "FAIL"),
                          ("semantic_mismatch_count", 1352),
                          ("verified_passing_case_count", 15877),
                          ("original_case_execution_denominator", 31237),
                          ("original_suite_count", 13),
                          ("actual_candidate_worker_count", 13),
                          ("failing_suite_counts", {"substitution_v2": 240,
                                                       "shape_v2": 1112})):
        value(lineage, key, expected)
    predecessor = document["immutable_no_external_introspection_predecessor"]
    for key, expected in (("application_receipt_sha256",
                           NO_INTROSPECTION_APPLICATION_SHA256),
                          ("application_target_path", INPUT),
                          ("application_target_sha256", INPUT_SHA256),
                          ("application_target_bytes", INPUT_BYTES),
                          ("capture_clamp_preserved", True),
                          ("no_external_introspection_preserved", True),
                          ("external_regex_dependency_added", False)):
        value(predecessor, key, expected)
    wall = document["physical_source_wall"]
    for key, expected in (("installed_before_owner_reads", True),
                          ("descriptor_relative_o_nofollow", True),
                          ("allowed_public_frozen_owner_count", len(OWNERS)),
                          ("source_mode_candidate_source_reads", 0),
                          ("self_test_candidate_source_reads", 0),
                          ("source_mode_filesystem_writes", 0),
                          ("self_test_filesystem_writes", 0),
                          ("archive_content_reads", 0),
                          ("archive_inflations", 0),
                          ("native_binary_reads", 0),
                          ("timer_reads", 0),
                          ("final_holdout_content_reads", 0),
                          ("proposal_content_reads", 0),
                          ("apply_requires_explicit_root_authorization", True),
                          ("apply_requires_frozen_commit_equals_pushed_commit", True),
                          ("apply_candidate_source_read_count", 1),
                          ("apply_exclusive_new_target_only", True),
                          ("candidate_execution_allowed", False),
                          ("compiler_launch_allowed", False),
                          ("network_access_allowed", False),
                          ("final_holdout", FINAL_HOLDOUT)):
        value(wall, key, expected)
    effects = document["source_only_effects"]
    for key in ("candidate_source_files_read", "candidate_executions",
                "candidate_imports", "candidate_workers_started",
                "reference_workers_started", "compiler_processes_started",
                "native_binary_files_opened", "native_libraries_loaded",
                "compressed_archives_opened", "compressed_archives_inflated",
                "final_holdout_cases_opened", "final_holdout_cases_generated",
                "final_holdout_proposal_files_opened", "clock_samples",
                "timing_trials_run", "network_requests", "workspace_mutations"):
        value(effects, key, 0)
    for key, expected in (("final_holdout", FINAL_HOLDOUT),
                          ("candidate_correctness", "NOT MEASURED"),
                          ("candidate_matching", "NOT RUN"),
                          ("candidate_semantic_mismatch_count", "NOT MEASURED"),
                          ("runtime_non_delegation", "NOT ESTABLISHED"),
                          ("performance", "NOT MEASURED"),
                          ("winner_selected", False)):
        value(effects, key, expected)


def parse_arguments(arguments: list[str]) -> dict:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require exact immutable command arguments")
    flags = {"--self-test", "--verify-source", "--verify-frozen-context",
             "--apply", "--root-authorized"}
    options = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
               "--frozen-commit", "--pushed-commit"}
    result: dict[str, object] = {}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        require(argument in flags or argument in options,
                "reject an unknown event-order freeze option: " + argument)
        require(argument not in result, "reject a duplicate option: " + argument)
        if argument in flags:
            result[argument] = True
            index += 1
        else:
            require(index + 1 < len(arguments),
                    "require a complete immutable option: " + argument)
            result[argument] = arguments[index + 1]
            index += 2
    modes = tuple(mode for mode in ("--self-test", "--verify-source",
                                    "--verify-frozen-context", "--apply")
                  if result.get(mode) is True)
    require(len(modes) == 1,
            "require exactly one self-test, source verification, or root apply")
    mode = modes[0]
    if mode == "--self-test":
        require(set(result) == {mode}, "source-only self-test accepts no owner pins")
    elif mode in ("--verify-source", "--verify-frozen-context"):
        require(set(result) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256"},
                "source verification requires exactly the complete frozen owner triple")
    else:
        require(set(result) == {mode, "--root-authorized", "--source-sha256",
                                "--protocol-sha256", "--contract-sha256",
                                "--frozen-commit", "--pushed-commit"},
                "exclusive root apply requires owner pins and the identical pushed commit")
        for label in ("--frozen-commit", "--pushed-commit"):
            commit = result[label]
            require(type(commit) is str and len(commit) == 40
                    and all(character in "0123456789abcdef" for character in commit),
                    "require a complete lowercase pushed commit: " + label)
        require(result["--frozen-commit"] == result["--pushed-commit"],
                "refuse source materialization before its exact freeze commit is pushed")
    for label in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if label in result:
            checked_sha(result[label], label)
    return result


def effects(wall: SourceWall, mode: str) -> dict:
    return {"mode": mode, "approved_public_owner_reads": wall.public_owner_reads,
            "candidate_source_files_read": wall.candidate_source_reads,
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_workers_started": 0, "reference_workers_started": 0,
            "compiler_processes_started": 0, "native_binary_files_opened": 0,
            "native_libraries_loaded": 0, "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0, "final_holdout_cases_opened": 0,
            "final_holdout_cases_generated": 0,
            "final_holdout_proposal_files_opened": 0,
            "clock_samples": 0, "timing_trials_run": 0, "network_requests": 0,
            "workspace_mutations": wall.workspace_mutations,
            "final_holdout": FINAL_HOLDOUT, "candidate_correctness": "NOT MEASURED",
            "candidate_matching": "NOT RUN",
            "candidate_semantic_mismatch_count": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "candidate_qualified": False,
            "winner_selected": False}


def main(arguments: list[str]) -> dict:
    options = parse_arguments(arguments)
    apply = options.get("--apply") is True
    wall = SourceWall(apply)
    no_matching_imports()
    wall.install()
    if options.get("--self-test") is True:
        tests = synthetic_tests(wall)
        require(wall.public_owner_reads == 0 and wall.candidate_source_reads == 0
                and wall.workspace_mutations == 0 and wall.root is None,
                "self-test must not read any owner or candidate or mutate the workspace")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "synthetic_controls": tests, "effects": effects(wall, "SELF-TEST")}

    source_sha = options["--source-sha256"]
    protocol_sha = options["--protocol-sha256"]
    contract_sha = options["--contract-sha256"]
    assert isinstance(source_sha, str) and isinstance(protocol_sha, str)
    assert isinstance(contract_sha, str)
    wall.open_root()
    wall.read(SOURCE, None, None, source_sha)
    wall.read(PROTOCOL, None, None, protocol_sha)
    contract_raw = wall.read(CONTRACT, None, None, contract_sha)
    validate_contract(StrictJSON(contract_raw).decode(), source_sha, protocol_sha)
    frozen: dict[str, bytes] = {}
    for role, relative, expected, count, inode in OWNERS:
        require(not relative.startswith("candidates/")
                and not relative.endswith((".gz", ".so"))
                and "holdout" not in relative and "phase3/" not in relative,
                "never admit candidate, native, archive, timer, or holdout as public owner")
        frozen[role] = wall.read(relative, count, inode, expected)
    evidence = authenticated_evidence(frozen)
    require(wall.public_owner_reads == len(OWNERS) + 3
            and wall.candidate_source_reads == 0 and wall.workspace_mutations == 0,
            "verify frozen context by public plaintext owners and receipts only")
    if not apply:
        tests = synthetic_tests(wall)
        no_matching_imports()
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; SOURCE FROZEN; NO CANDIDATE SOURCE READ",
                "source_sha256": source_sha, "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "authenticated_public_owner_count": len(OWNERS),
                "immutable_actual_evidence": evidence,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "synthetic_controls": tests,
                "effects": effects(wall, "SOURCE FREEZE")}

    require(bool(transform(synthetic_source())) and wall.candidate_source_reads == 0,
            "finish complete synthetic source correction before opening its sole input")
    original = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA256)
    corrected = transform(original, exact=True)
    wall.materialize(corrected)
    no_matching_imports()
    require(wall.candidate_source_reads == 1 and wall.workspace_mutations == 2,
            "create exactly one exclusive directory and one composed source variant")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; REPLACEMENT-FIRST EVENT ORDER; NOT BUILT; NOT RUN",
            "frozen_commit": options["--frozen-commit"],
            "pushed_commit": options["--pushed-commit"],
            "source_sha256": source_sha, "protocol_sha256": protocol_sha,
            "contract_sha256": contract_sha,
            "input_path": INPUT, "input_sha256": INPUT_SHA256,
            "input_bytes": INPUT_BYTES, "target_path": TARGET,
            "target_sha256": OUTPUT_SHA256, "target_bytes": OUTPUT_BYTES,
            "capture_clamp_preserved": True,
            "no_external_introspection_preserved": True,
            "replacement_validated_before_subject": True,
            "callback_subject_ownership_preserved": True,
            "deferred_literal_subject_released_before_join": True,
            "duplicate_subject_release_precluded": True,
            "combined_targeted_historical_mismatch_count": 1264,
            "post_correction_actual_mismatch_count": "NOT MEASURED",
            "final_holdout": FINAL_HOLDOUT,
            "effects": effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError, KeyError,
            IndexError, TypeError) as error:
        sys.stderr.write("rust-substitution-event-order-v1: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
