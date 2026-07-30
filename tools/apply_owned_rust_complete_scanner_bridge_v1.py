#!/usr/bin/env python3
"""Freeze the commuting complete-original and scanner-protocol Rust bridge.

Source-only gates authenticate public plaintext owners and receipts without
opening either committed candidate bridge, native objects, archives, final
material, Git state, clocks, or external matching engines.  Only separately
authorized root application, after the exact freeze has been committed and
pushed, may read the complete corrected bridge once and exclusively materialize
the one predicted complete-plus-scanner successor.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("complete scanner bridge freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
DEVICE = 2064
SCHEMA = "rebar-owned-rust-complete-scanner-bridge-v1-source-freeze"
SOURCE = "tools/apply_owned_rust_complete_scanner_bridge_v1.py"
PROTOCOL = "oracle/phase2/RUST-COMPLETE-SCANNER-BRIDGE-V1.md"
CONTRACT = "oracle/phase2/rust-complete-scanner-bridge-v1.json"
INPUT = "candidates/rust/variants/complete_semantic_correction_v2/py_bridge.c"
INPUT_SHA256 = "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55"
INPUT_BYTES = 178270
INPUT_INODE = 526052
SCANNER_VARIANT = "candidates/rust/variants/scanner_pickle_semantics_v2/py_bridge.c"
SCANNER_VARIANT_SHA256 = "e074be7b4a6882f2ac004f027f941240a373c85eb9267c59da4d5d354b8f4bfc"
SCANNER_VARIANT_BYTES = 177348
SCANNER_VARIANT_INODE = 526082
TARGET_DIRECTORY = "candidates/rust/variants/complete_scanner_bridge_v1"
TARGET = TARGET_DIRECTORY + "/py_bridge.c"
OUTPUT_SHA256 = "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e"
OUTPUT_BYTES = 178472
FINAL_HOLDOUT = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 300_000
MAX_JSON_DEPTH = 80
RAW_COMPARISON_SHA256 = "7fc4c743e35bbe4f57ed0e3a872b9a9646b2603feedb9ae2c24421afed5430aa"
RAW_COMPARISON_BYTES = 1428906

COMPLETE_SOURCE = "tools/apply_owned_rust_complete_semantic_correction_v2.py"
COMPLETE_PROTOCOL = "oracle/phase2/RUST-COMPLETE-SEMANTIC-CORRECTION-V2.md"
COMPLETE_CONTRACT = "oracle/phase2/rust-complete-semantic-correction-v2.json"
COMPLETE_APPLICATION = "oracle/phase2/evidence/rust-complete-semantic-correction-v2-application.json"
SCANNER_SOURCE = "tools/apply_owned_rust_scanner_pickle_semantics_v2.py"
SCANNER_PROTOCOL = "oracle/phase2/RUST-SCANNER-PICKLE-SEMANTICS-V2.md"
SCANNER_CONTRACT = "oracle/phase2/rust-scanner-pickle-semantics-v2.json"
SCANNER_APPLICATION = "oracle/phase2/evidence/rust-scanner-pickle-semantics-v2-application.json"
V25_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-"
    "failures-publication-receipt.json"
)
V26_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-"
    "anchor-public-run-001-publication-receipt.json"
)
V27_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-"
    "compiler-public-run-001-publication-receipt.json"
)
V28_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v3-v28-"
    "combined-public-run-001-publication-receipt.json"
)
PUBLIC_DATASET_SOURCE = "tools/rust_public_practice_benchmark_v2.py"

# role, exact public plaintext path, SHA-256, byte count, device-2064 inode.
# Neither committed C bridge nor any raw comparison/archive/native/final owner
# belongs to this descriptor-relative allowlist.
OWNERS = (
    ("complete_source", COMPLETE_SOURCE,
     "dd80de72a2104703d8c36269cbef56e67231add6f31a7a8c8f7bf05aa5f0e807", 90354, 431596),
    ("complete_protocol", COMPLETE_PROTOCOL,
     "aae4793c84f1f4d93806f2484047d3b1e2a7f544c25d02b08551f2d9f07f2936", 10629, 525979),
    ("complete_contract", COMPLETE_CONTRACT,
     "25ae3e1a35fae2ace9533b14fdaf771c0270b50b5b93b5b702d683906ca2dbe3", 8308, 525985),
    ("complete_application", COMPLETE_APPLICATION,
     "304396bb08709d63d0cb89e08d40e369a754f9e4352015955a33ab6fb99113cb", 2387, 526053),
    ("scanner_source", SCANNER_SOURCE,
     "0a61db87974b1801e0af598440af1b4d30e71cd9a8c63e1b250d5676f078d5b8", 85123, 431662),
    ("scanner_protocol", SCANNER_PROTOCOL,
     "a078bb4563cad5616ab668cdbde4ac735d42dcabc44501259ac8143667ece7f7", 11560, 526054),
    ("scanner_contract", SCANNER_CONTRACT,
     "14786ce9b80fb353af728019c8734c2a9b7022387257729ee0b520f4557a5422", 9158, 526060),
    ("scanner_application", SCANNER_APPLICATION,
     "c76760a4f738a7843cab4a5604c991776652b50307f671df9209b506178df99a", 2021, 526091),
    ("v25_complete_failure_receipt", V25_RECEIPT,
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("v26_public_receipt", V26_RECEIPT,
     "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80", 40906, 525333),
    ("v27_public_receipt", V27_RECEIPT,
     "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449", 68330, 525426),
    ("v28_public_receipt", V28_RECEIPT,
     "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb", 40372, 525923),
    ("public_dataset_source", PUBLIC_DATASET_SOURCE,
     "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6", 112729, 429259),
)

TARGETED_OPERATIONS = (
    "pattern.scanner.reduce_ex.negative",
    "pattern.scanner.reduce_ex.zero",
    "pattern.scanner.reduce_ex.one",
    "pattern.scanner.reduce_ex.string",
    "pattern.scanner.reduce_ex.overflow",
)
PRESERVED_OPERATIONS = (
    "pattern.scanner.reduce_ex.two",
    "pattern.scanner.reduce_ex.five",
)
OVERLAP_DATASETS = (
    "text.comment.inline_unknown_named_unicode",
    "text.comment.global_verbose_unknown_named_unicode",
    "text.comment.scoped_verbose_unknown_named_unicode",
)

ORIGINAL_SCANNER = b"""static PyObject *rust_scanner_reduce_ex(RustIterator *iterator, PyObject *protocol) {
    (void)protocol;
    return PyErr_Format(
        PyExc_TypeError,
        "cannot pickle '%.200s' object",
        Py_TYPE(iterator)->tp_name
    );
}
"""
CORRECTED_SCANNER = b"""static PyObject *rust_scanner_reduce_ex(RustIterator *iterator, PyObject *protocol) {
    int protocol_number = PyLong_AsInt(protocol);
    if (protocol_number == -1 && PyErr_Occurred()) return NULL;
    if (protocol_number < 2) {
        return rust_owned_pickle_reconstruction((PyObject *)iterator);
    }
    return PyErr_Format(
        PyExc_TypeError,
        "cannot pickle '%.200s' object",
        Py_TYPE(iterator)->tp_name
    );
}
"""
MATCH_FUNCTION = b"""static PyObject *rust_match_reduce_ex(RustMatch *match, PyObject *protocol) {
    int protocol_number = PyLong_AsInt(protocol);
    if (protocol_number == -1 && PyErr_Occurred()) return NULL;
    if (protocol_number < 2) {
        return rust_owned_pickle_reconstruction((PyObject *)match);
    }
    return PyErr_Format(
        PyExc_TypeError,
        "cannot pickle '%.200s' object",
        Py_TYPE(match)->tp_name
    );
}
"""
GENERIC_FINISH_CLAMP = b"if (finish < first) finish = first;"
CAPTURE_CLAMP_CONTEXT = (
    b"    size_t first = begin > capture.length ? capture.length : begin;\n"
    b"    size_t finish = end > capture.length ? capture.length : end;\n"
    b"    if (finish < first) finish = first;\n"
)
CORE_START = (
    b"static PyObject *rust_substitute_core(PyObject *pattern, void *handle, "
    b"PyObject *groupindex, PyObject *pattern_value, PyObject *templates, "
    b"size_t groups, PyObject *replacement, PyObject *value, "
    b"Py_ssize_t limit, int want_count) {\n"
)
CORE_END = b"\nstatic PyObject *rust_bound_substitute("
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
CORRECTED_SUCCESS = b"""    Py_XDECREF(tokens);
    if (subject_acquired) rust_subject_release(&subject);
    return rust_sub_result(joined, replaced, want_count);
"""
CORRECTED_FAILURE = b"""    Py_XDECREF(tokens);
    if (subject_acquired) rust_subject_release(&subject);
    return NULL;
}
"""
EXPAND_FORWARD = b"static PyObject *rust_match_expand(RustMatch *match, PyObject *template);"
EXPAND_START = b"static PyObject *rust_match_expand(RustMatch *match, PyObject *template) {"
CACHE_START = b"static int rust_replacement_cache("
TRAILING_GATE = (
    b"    int trailing_escape = PyUnicode_CompareWithASCIIString(\n"
    b'        message, "bad escape (end of pattern)"\n'
    b"    );\n"
)
TRAILING_PROBE = (
    b"    if (trailing_escape == 0 && PyObject_Length(replacement) < 0) {\n"
)
VALIDATION_CALL = b"state->template_helper, validation_arguments, 3, NULL"
VALIDATION_FLAG = b"                normalized, (PyObject *)match, Py_True\n"
FULL_FLAG = b"materialization_flags = PyBUF_FULL_RO;"


class FreezeError(Exception):
    """Reject substituted evidence, unsafe effects, or noncommuting C edits."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete genuine bytes only")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "require genuine JSON text")
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    output = ['"']
    for char in value:
        point = ord(char)
        require(not 0xD800 <= point <= 0xDFFF, "reject unpaired JSON surrogate")
        output.append(escapes.get(char, "\\u" + format(point, "04x")
                                  if point < 32 else char))
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
        require(all(type(key) is str for key in value), "reject nontext JSON key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported canonical JSON value")


class StrictJSON:
    """Bounded duplicate-rejecting JSON parser without importing json or re."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require complete bounded evidence bytes")
        self.text = raw.decode("utf-8", "strict")
        self.index = 0
        self.items = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "require JSON string")
        self.index += 1
        output: list[str] = []
        simple = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                  "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(output)
            if char != "\\":
                require(ord(char) >= 32 and not 0xD800 <= ord(char) <= 0xDFFF,
                        "reject invalid raw JSON character")
                output.append(char)
                continue
            require(self.index < len(self.text), "reject truncated JSON escape")
            char = self.text[self.index]
            self.index += 1
            if char != "u":
                require(char in simple, "reject unknown JSON escape")
                output.append(simple[char])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4
                    and all(item in "0123456789abcdefABCDEF" for item in digits),
                    "reject malformed JSON Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject unpaired high surrogate")
                low_digits = self.text[self.index + 2:self.index + 6]
                require(len(low_digits) == 4
                        and all(item in "0123456789abcdefABCDEF"
                                for item in low_digits), "reject malformed low surrogate")
                low = int(low_digits, 16)
                require(0xDC00 <= low <= 0xDFFF, "reject unpaired high surrogate")
                self.index += 6
                output.append(chr(0x10000 + ((point - 0xD800) << 10)
                                  + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF,
                        "reject unpaired low surrogate")
                output.append(chr(point))
        raise FreezeError("reject unterminated JSON string")

    def number(self) -> int | float:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject leading-zero JSON number")
        else:
            require(self.text[self.index] in "123456789", "reject invalid JSON number")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        fractional = False
        if self.text[self.index:self.index + 1] == ".":
            fractional = True
            self.index += 1
            first = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > first, "reject missing fractional digits")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            fractional = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            first = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > first, "reject missing exponent digits")
        require(self.index - start <= 128, "reject oversized evidence number")
        token = self.text[start:self.index]
        if not fractional:
            return int(token)
        result = float(token)
        require(result == result and result not in (float("inf"), float("-inf")),
                "reject nonfinite public timing evidence")
        return result

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject excessive evidence nesting")
        self.whitespace()
        require(self.index < len(self.text), "reject missing JSON value")
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
                require(key not in result, "reject duplicate JSON key: " + key)
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON object")
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "reject missing JSON object colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "reject malformed JSON object")
        if char == "[":
            self.index += 1
            result: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON array")
                result.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result
                require(separator == ",", "reject malformed JSON array")
        if char == "-" or char in "0123456789":
            return self.number()
        for literal, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return value
        raise FreezeError("reject malformed or nonfinite JSON value")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing evidence bytes")
        return result


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "rebar", "subprocess", "socket",
                 "threading", "multiprocessing", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matcher, candidate, native loader, worker, or network import")


class SourceWall:
    """Deny-default descriptor wall with one deferred root-only bridge reader."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT)
                                + tuple(owner[1] for owner in OWNERS))
        self.allowed = self.public
        self.input_authorized = False
        self.live: dict[int, tuple[str, str]] = {}
        self.root: int | None = None
        self.open_ticket: tuple[str, int] | None = None
        self.mkdir_ticket: tuple[str, int] | None = None
        self.output_opened = False
        self.directory_created = False
        self.candidate_source_reads = 0
        self.public_owner_reads = 0
        self.workspace_mutations = 0
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.native_open = os.open
        self.native_read = os.read
        self.native_write = os.write
        self.native_fstat = os.fstat
        self.native_close = os.close
        self.native_fsync = os.fsync
        self.native_mkdir = os.mkdir

    def deny(self, reason: str) -> None:
        self.blocked[reason] = self.blocked.get(reason, 0) + 1
        raise FreezeError("complete scanner source wall rejected " + reason)

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed-candidate-native-archive-holdout-git-or-write-open")
        if event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            if self.mkdir_ticket is not None and (path, mode) == self.mkdir_ticket:
                return
            self.deny("unticketed-workspace-directory-mutation")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.rmdir", "os.chmod",
                      "os.chown", "os.urandom", "os.getrandom", "_interpreters.create",
                      "_interpreters.exec", "cpython.PyInterpreterState_New",
                      "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.", "tempfile.",
                                     "time.", "os.exec", "os.spawn"))):
            self.deny("candidate-import-process-native-network-clock-or-code")

    def forbidden(self, reason: str):
        def reject(*_arguments: object, **_options: object) -> object:
            self.deny(reason)
        return reject

    def checked_component(self, value: object) -> str:
        if (type(value) is not str or not value or value in (".", "..")
                or "/" in value or "\x00" in value):
            self.deny("unowned-or-traversal-path-component")
        assert isinstance(value, str)
        return value

    def native_ticket_open(self, path: str, flags: int, mode: int = 0,
                           *, dir_fd: int | None = None) -> int:
        require(self.open_ticket is None, "reject nested descriptor authorization")
        self.open_ticket = (path, flags)
        try:
            if dir_fd is None:
                return self.native_open(path, flags, mode)
            return self.native_open(path, flags, mode, dir_fd=dir_fd)
        finally:
            self.open_ticket = None

    def directory_flags(self) -> int:
        return (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0))

    def file_flags(self) -> int:
        return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)

    def open_root(self) -> None:
        require(self.installed and self.root is None, "open exact root descriptor once")
        descriptor = self.native_ticket_open(ROOT, self.directory_flags())
        metadata = self.native_fstat(descriptor)
        require(stat.S_ISDIR(metadata.st_mode) and metadata.st_dev == DEVICE,
                "reject substituted immutable workspace root")
        self.root = descriptor
        self.live[descriptor] = ("", "directory")

    def child_directory(self, parent: int, component: str) -> int:
        component = self.checked_component(component)
        info = self.live.get(parent)
        require(info is not None and info[1] == "directory",
                "reject foreign parent directory descriptor")
        relative = component if not info[0] else info[0] + "/" + component
        authorized = (any(path.startswith(relative + "/") for path in self.allowed)
                      or self.apply and (relative == TARGET_DIRECTORY
                                         or TARGET_DIRECTORY.startswith(relative + "/")))
        require(authorized and not relative.startswith((".git/", ".agents/", ".codex/")),
                "reject unowned, hidden, final, private, or candidate directory")
        descriptor = self.native_ticket_open(component, self.directory_flags(),
                                             dir_fd=parent)
        metadata = self.native_fstat(descriptor)
        require(stat.S_ISDIR(metadata.st_mode) and metadata.st_dev == DEVICE,
                "reject substituted or symlink directory: " + relative)
        require(descriptor not in self.live, "reject descriptor alias")
        self.live[descriptor] = (relative, "directory")
        return descriptor

    def close(self, descriptor: int) -> None:
        require(type(descriptor) is int and descriptor in self.live
                and descriptor != self.root, "reject foreign or root descriptor")
        self.native_close(descriptor)
        del self.live[descriptor]

    def parent(self, relative: str) -> tuple[int, list[int], str]:
        require(type(relative) is str and relative in self.allowed,
                "reject unowned candidate, final, archive, native, Git, or holdout")
        require(self.root is not None, "open isolated workspace root first")
        components = relative.split("/")
        require(all(self.checked_component(item) for item in components),
                "reject invalid owner path component")
        descriptor = self.root
        stack: list[int] = []
        try:
            for item in components[:-1]:
                descriptor = self.child_directory(descriptor, item)
                stack.append(descriptor)
            return descriptor, stack, components[-1]
        except BaseException:
            for item in reversed(stack):
                self.close(item)
            raise

    def authorize_input(self) -> None:
        require(self.apply and self.installed and self.root is not None
                and not self.input_authorized and self.allowed == self.public
                and self.public_owner_reads == len(OWNERS) + 3
                and self.candidate_source_reads == 0
                and self.workspace_mutations == 0,
                "authorize the complete bridge only after all source controls pass")
        self.allowed = self.public | frozenset((INPUT,))
        self.input_authorized = True

    def read(self, relative: str, count: int | None, inode: int | None,
             expected_sha256: str) -> bytes:
        require(self.installed and relative in self.allowed,
                "candidate source access prohibited outside root-only apply")
        require(count is None or type(count) is int and 0 < count <= MAX_OWNER_BYTES,
                "reject oversized frozen owner")
        parent, stack, filename = self.parent(relative)
        descriptor: int | None = None
        try:
            descriptor = self.native_ticket_open(filename, self.file_flags(),
                                                 dir_fd=parent)
            self.live[descriptor] = (relative, "file")
            before = self.native_fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and stat.S_IMODE(before.st_mode) == 0o600
                    and before.st_dev == DEVICE and 0 < before.st_size <= MAX_OWNER_BYTES
                    and (count is None or before.st_size == count)
                    and before.st_nlink == 1 and before.st_uid == os.geteuid()
                    and (inode is None or before.st_ino == inode),
                    "reject substituted immutable frozen owner: " + relative)
            chunks: list[bytes] = []
            remaining = before.st_size
            while remaining:
                block = self.native_read(descriptor, min(remaining, 65536))
                require(type(block) is bytes and bool(block),
                        "reject truncated immutable frozen owner: " + relative)
                chunks.append(block)
                remaining -= len(block)
            require(self.native_read(descriptor, 1) == b"",
                    "reject additional immutable frozen owner bytes: " + relative)
            after = self.native_fstat(descriptor)
            require((after.st_dev, after.st_ino, after.st_size, after.st_mode,
                     after.st_mtime_ns, after.st_ctime_ns)
                    == (before.st_dev, before.st_ino, before.st_size, before.st_mode,
                        before.st_mtime_ns, before.st_ctime_ns),
                    "reject concurrently mutated immutable frozen owner: " + relative)
            raw = b"".join(chunks)
            require(digest(raw) == checked_sha(expected_sha256, relative),
                    "reject substituted complete frozen owner digest: " + relative)
            if relative == INPUT:
                require(self.apply and self.input_authorized
                        and self.candidate_source_reads == 0,
                        "complete candidate bridge may be read once during root apply")
                self.candidate_source_reads += 1
            else:
                self.public_owner_reads += 1
            return raw
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for item in reversed(stack):
                self.close(item)

    def make_target_directory(self) -> int:
        require(self.apply and not self.directory_created and self.root is not None,
                "require explicit one-time root-only directory creation")
        descriptor = self.root
        stack: list[int] = []
        components = TARGET_DIRECTORY.split("/")
        try:
            for component in components[:-1]:
                descriptor = self.child_directory(descriptor, component)
                stack.append(descriptor)
            name = self.checked_component(components[-1])
            require(self.mkdir_ticket is None, "reject nested directory ticket")
            self.mkdir_ticket = (name, 0o700)
            try:
                self.native_mkdir(name, 0o700, dir_fd=descriptor)
            finally:
                self.mkdir_ticket = None
            self.directory_created = True
            self.workspace_mutations += 1
            return self.child_directory(descriptor, name)
        finally:
            for item in reversed(stack):
                self.close(item)

    def materialize(self, raw: bytes) -> None:
        require(self.apply and self.candidate_source_reads == 1 and not self.output_opened,
                "authorize exactly one root-only composed Rust bridge")
        require(type(raw) is bytes and len(raw) == OUTPUT_BYTES
                and digest(raw) == OUTPUT_SHA256,
                "reject non-frozen composed bridge before workspace mutation")
        parent = self.make_target_directory()
        descriptor: int | None = None
        try:
            flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
            descriptor = self.native_ticket_open("py_bridge.c", flags, 0o600,
                                                 dir_fd=parent)
            self.output_opened = True
            self.workspace_mutations += 1
            self.live[descriptor] = (TARGET, "output")
            written = 0
            while written < len(raw):
                count = self.native_write(descriptor, raw[written:])
                require(type(count) is int and count > 0,
                        "reject incomplete exclusive composed bridge write")
                written += count
            metadata = self.native_fstat(descriptor)
            require(stat.S_ISREG(metadata.st_mode)
                    and stat.S_IMODE(metadata.st_mode) == 0o600
                    and metadata.st_dev == DEVICE and metadata.st_size == OUTPUT_BYTES
                    and metadata.st_nlink == 1 and metadata.st_uid == os.geteuid(),
                    "reject substituted exclusive composed bridge")
            self.native_fsync(descriptor)
            self.close(descriptor)
            descriptor = None
            self.native_fsync(parent)
            readback = self.native_ticket_open("py_bridge.c", self.file_flags(),
                                               dir_fd=parent)
            try:
                self.live[readback] = (TARGET, "readback")
                chunks: list[bytes] = []
                remaining = OUTPUT_BYTES
                while remaining:
                    part = self.native_read(readback, min(remaining, 65536))
                    require(bool(part), "reject incomplete durable bridge readback")
                    chunks.append(part)
                    remaining -= len(part)
                require(self.native_read(readback, 1) == b""
                        and digest(b"".join(chunks)) == OUTPUT_SHA256,
                        "reject durable complete scanner bridge digest")
            finally:
                self.close(readback)
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            self.close(parent)

    def install(self) -> None:
        require(not self.installed, "install immutable physical wall exactly once")
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
            "require one complete corrected substitution core and following boundary")
    first = source.index(CORE_START)
    last = source.index(CORE_END, first + len(CORE_START))
    return source[:first], source[first:last], source[last:]


def preserve_complete_source(source: bytes, scanner_corrected: bool) -> None:
    require(type(source) is bytes, "require complete genuine first-party bridge bytes")
    required = (
        (MATCH_FUNCTION, 1), (GENERIC_FINISH_CLAMP, 2), (CAPTURE_CLAMP_CONTEXT, 1),
        (CORE_START, 1), (CORE_END, 1), (CORRECTED_INITIAL, 1),
        (CORRECTED_JOIN, 1), (CORRECTED_SUCCESS, 1), (CORRECTED_FAILURE, 1),
        (CACHE_START, 1), (EXPAND_FORWARD, 1), (EXPAND_START, 1),
        (TRAILING_GATE, 1), (TRAILING_PROBE, 1), (VALIDATION_CALL, 1),
        (VALIDATION_FLAG, 1), (FULL_FLAG, 1),
        (b"static PyObject *rust_owned_pickle_reconstruction(PyObject *value) {", 1),
        (b"static PyObject *rust_scanner_reduce(RustIterator *iterator, PyObject *ignored) {", 1),
        (b"static PyMethodDef rust_iterator_scanner_search_method = {", 1),
        (b"PyDescr_NewMethod(", 1),
        (b'    .name = "_sre.SRE_Scanner",', 1),
        (b'{"__reduce_ex__", (PyCFunction)rust_scanner_reduce_ex, METH_O,', 1),
        (b"Py_CLEAR(method->signature);", 2),
        (b"Py_VISIT(method->signature);", 1),
        (b"PyObject_GetBuffer(template, &view, PyBUF_SIMPLE)", 1),
        (b"rust_match_expand_fallback(match, normalized)", 1),
    )
    for marker, expected in required:
        require(source.count(marker) == expected,
                "preserve scanner, safe clamp, complete replacement, and Match.expand")
    scanner_returns = b"return rust_owned_pickle_reconstruction((PyObject *)iterator);"
    require(source.count(scanner_returns) == (2 if scanner_corrected else 1),
            "preserve existing scanner reconstruction and its one corrected addition")
    expected_scanner = CORRECTED_SCANNER if scanner_corrected else ORIGINAL_SCANNER
    forbidden_scanner = ORIGINAL_SCANNER if scanner_corrected else CORRECTED_SCANNER
    require(source.count(expected_scanner) == 1 and source.count(forbidden_scanner) == 0,
            "require exactly one scanner function in its expected correction state")
    for forbidden in (b'PyImport_ImportModule("inspect")',
                      b'PyImport_ImportModule("functools")',
                      b'PyImport_ImportModule("re")',
                      b'PyImport_ImportModule("regex")',
                      b"rust_bound_get_signature", b"rust_iterator_signature",
                      b"__text_signature__"):
        require(forbidden not in source,
                "reject external matching, private introspection, or external regex")
    prefix, core, suffix = extract_core(source)
    require(prefix.count(expected_scanner) == 1 and core.count(expected_scanner) == 0
            and suffix.count(expected_scanner) == 0,
            "prove the scanner edit is disjoint from the complete substitution core")
    require(prefix.count(EXPAND_FORWARD) == 1 and prefix.count(EXPAND_START) == 1
            and prefix.index(EXPAND_FORWARD) < prefix.index(CACHE_START)
            < prefix.index(EXPAND_START),
            "preserve distinct Match.expand forward declaration and full definition")
    require(core.index(b"rust_replacement_cache(\n")
            < core.index(b"rust_subject_open(&subject, pattern_value, value, 1)"),
            "preserve replacement validation before subject acquisition")
    release = core.index(b"rust_subject_release(&subject);", core.index(CORRECTED_JOIN))
    separator = core.index(b"PyObject *separator = Py_GetConstant(", release)
    join = core.index(b"PyBytes_Join(separator, pieces)", separator)
    require(release < separator < join,
            "preserve noncallback release before replacement exporter reacquisition")
    require(core.count(b"if (subject_acquired) rust_subject_release(&subject);") == 2,
            "preserve both guarded cleanup sites without duplicate subject release")


def transform(source: bytes, exact: bool = False) -> bytes:
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA256,
                "reject unauthenticated complete original-correction bridge")
    preserve_complete_source(source, False)
    prefix, core, suffix = extract_core(source)
    corrected_prefix = prefix.replace(ORIGINAL_SCANNER, CORRECTED_SCANNER, 1)
    result = corrected_prefix + core + suffix
    preserve_complete_source(result, True)
    corrected_before, corrected_core, corrected_after = extract_core(result)
    require(corrected_core == core and corrected_after == suffix,
            "never edit substitution ordering, expansion, safe clamp, or native engine")
    require(corrected_before.replace(CORRECTED_SCANNER, ORIGINAL_SCANNER, 1) == prefix,
            "require one reversible scanner-only correction on the complete bridge")
    require(len(result) - len(source)
            == len(CORRECTED_SCANNER) - len(ORIGINAL_SCANNER) == 202,
            "require exactly one disjoint reversible 202-byte scanner edit")
    if exact:
        require(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
                "reject substituted deterministic complete scanner bridge")
    return result


def synthetic_source() -> bytes:
    return b"".join((
        b"static PyObject *rust_owned_pickle_reconstruction(PyObject *value) {\n}\n",
        MATCH_FUNCTION,
        b"static PyObject *rust_scanner_reduce(RustIterator *iterator, PyObject *ignored) {\n",
        b"    return rust_owned_pickle_reconstruction((PyObject *)iterator);\n}\n",
        ORIGINAL_SCANNER,
        b"static PyMethodDef rust_iterator_scanner_search_method = {\n};\n",
        b'{"__reduce_ex__", (PyCFunction)rust_scanner_reduce_ex, METH_O,\n',
        b'    .name = "_sre.SRE_Scanner",\n',
        b"    if (finish < first) finish = first;\n", CAPTURE_CLAMP_CONTEXT,
        b"PyDescr_NewMethod(pattern, NULL);\n",
        EXPAND_FORWARD, b"\n", CACHE_START, b"void) {\n    ", FULL_FLAG, b"\n}\n",
        TRAILING_GATE, TRAILING_PROBE, b"    return -1;\n}\n",
        b"PyObject_GetBuffer(template, &view, PyBUF_SIMPLE);\n",
        EXPAND_START, b"\n", VALIDATION_FLAG, VALIDATION_CALL,
        b";\nrust_match_expand_fallback(match, normalized);\n}\n",
        b"Py_CLEAR(method->signature);\nPy_CLEAR(method->signature);\n",
        b"Py_VISIT(method->signature);\n",
        CORE_START, CORRECTED_INITIAL,
        b"    if (deferred) {\n", CORRECTED_JOIN,
        b"        joined = PyBytes_Join(separator, pieces);\n    }\n",
        CORRECTED_SUCCESS, b"substitute_error:\n", CORRECTED_FAILURE,
        CORE_END, b"void) { return NULL; }\n",
    ))


class WitnessInt(int):
    pass


class WitnessIndex:
    def __init__(self, value: object) -> None:
        self.value = value

    def __index__(self) -> object:
        return self.value


class WitnessIndexFailure:
    def __index__(self) -> int:
        raise RuntimeError("original scanner __index__ failure")


def protocol_as_c_int(protocol: object) -> int:
    if isinstance(protocol, int):
        value = int(protocol)
    else:
        special = getattr(type(protocol), "__index__", None)
        if special is None:
            raise TypeError("scanner protocol must be an integer")
        value = special(protocol)
        if not isinstance(value, int):
            raise TypeError("__index__ returned non-integer")
        value = int(value)
    if not -(1 << 31) <= value < (1 << 31):
        raise OverflowError("scanner protocol does not fit C int")
    return value


def scanner_outcome(protocol: object) -> str:
    return "RECONSTRUCTION" if protocol_as_c_int(protocol) < 2 else "TYPE_ERROR"


def public_model(dataset_names: tuple[str, ...]) -> dict[str, object]:
    require(len(dataset_names) == 94 and len(set(dataset_names)) == 94,
            "require the exact 94 unique authenticated public datasets")
    require(all(item in dataset_names for item in OVERLAP_DATASETS),
            "preserve all three independently failing named-comment datasets")
    targeted = [(dataset, operation) for dataset in dataset_names
                for operation in TARGETED_OPERATIONS]
    overlap = [(dataset, operation) for dataset in OVERLAP_DATASETS
               for operation in TARGETED_OPERATIONS]
    preserved = [(dataset, operation) for dataset in dataset_names
                 for operation in PRESERVED_OPERATIONS]
    require(len(targeted) == 470 and len(overlap) == 15
            and len(targeted) - len(overlap) == 455 and len(preserved) == 188,
            "preserve exact 470 gross / 15 overlap / 455 independent scanner rows")
    return {"dataset_count": len(dataset_names), "targeted_operation_count": 5,
            "gross_targeted_public_mismatch_count": len(targeted),
            "named_unicode_comment_overlap_dataset_count": 3,
            "named_unicode_comment_overlap_datasets": list(OVERLAP_DATASETS),
            "named_unicode_comment_overlap_row_count": len(overlap),
            "scanner_only_independent_public_improvement_count": 455,
            "preserved_high_protocol_row_count": len(preserved),
            "preserved_high_protocol_comment_compile_failure_count": 6,
            "independent_effect_measured": False,
            "candidate_correctness": "NOT MEASURED"}


def synthetic_tests(wall: SourceWall) -> dict[str, object]:
    require(wall.installed and not wall.input_authorized and INPUT not in wall.allowed
            and SCANNER_VARIANT not in wall.allowed,
            "all hostile controls must precede authorization of either candidate")
    source = synthetic_source()
    corrected = transform(source)
    require(len(corrected) == len(source) + 202,
            "require exact reversible one-function synthetic scanner composition")
    rejected = 0

    def reject(operation, reason: str) -> None:
        nonlocal rejected
        try:
            operation()
        except (FreezeError, OSError, TypeError, ValueError, OverflowError, RuntimeError):
            rejected += 1
            return
        raise FreezeError("hostile source-only control unexpectedly passed: " + reason)

    anchors = (ORIGINAL_SCANNER, MATCH_FUNCTION, GENERIC_FINISH_CLAMP,
               CAPTURE_CLAMP_CONTEXT, CORE_START, CORE_END, CORRECTED_INITIAL,
               CORRECTED_JOIN, CORRECTED_SUCCESS, CORRECTED_FAILURE,
               CACHE_START, EXPAND_FORWARD, EXPAND_START, TRAILING_GATE,
               TRAILING_PROBE, VALIDATION_CALL, VALIDATION_FLAG, FULL_FLAG)
    for marker in anchors:
        reject(lambda item=marker: transform(source.replace(item, b"", 1)),
               "missing unique complete or scanner correction anchor")
        reject(lambda item=marker: transform(source.replace(item, item + item, 1)),
               "duplicated unique complete or scanner correction anchor")
    for index in range(0, len(ORIGINAL_SCANNER), 13):
        damaged = (ORIGINAL_SCANNER[:index]
                   + bytes((ORIGINAL_SCANNER[index] ^ 1,))
                   + ORIGINAL_SCANNER[index + 1:])
        reject(lambda value=damaged: transform(source.replace(ORIGINAL_SCANNER, value, 1)),
               "single-byte drift in the owned complete scanner function")
    for payload in (b'{"x":1,"x":2}', b"NaN", b"Infinity", b"1e309", b"01",
                    b'{"x":"\\ud800"}', b'{"x":true} trailing'):
        reject(lambda item=payload: StrictJSON(item).decode(),
               "unsafe, duplicate, nonfinite, malformed, or trailing JSON")
    controls = (
        (-1, "RECONSTRUCTION"), (-2, "RECONSTRUCTION"), (0, "RECONSTRUCTION"),
        (1, "RECONSTRUCTION"), (False, "RECONSTRUCTION"), (True, "RECONSTRUCTION"),
        (WitnessInt(-1), "RECONSTRUCTION"), (WitnessInt(1), "RECONSTRUCTION"),
        (WitnessIndex(-1), "RECONSTRUCTION"), (WitnessIndex(0), "RECONSTRUCTION"),
        (WitnessIndex(1), "RECONSTRUCTION"), (2, "TYPE_ERROR"), (5, "TYPE_ERROR"),
        ((1 << 31) - 1, "TYPE_ERROR"), (-(1 << 31), "RECONSTRUCTION"),
    )
    for protocol, expected in controls:
        require(scanner_outcome(protocol) == expected,
                "preserve exact scanner protocol threshold and existing reconstructor")
    for protocol in ("0", b"0", None, 0.5, 1 << 31, -(1 << 31) - 1,
                     1 << 40, -(1 << 40), WitnessIndex("0"),
                     WitnessIndex(1 << 40), WitnessIndexFailure()):
        reject(lambda value=protocol: scanner_outcome(value),
               "invalid, overflowing, or exceptional scanner protocol")
    reject(lambda: wall.parent(INPUT), "complete candidate bridge source read")
    reject(lambda: wall.parent(SCANNER_VARIANT), "standalone scanner candidate read")
    reject(lambda: wall.parent(TARGET), "composed candidate bridge target read")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved primitive unticketed complete bridge read")
    reject(lambda: wall.native_open(ROOT + "/" + SCANNER_VARIANT, wall.file_flags()),
           "saved primitive unticketed scanner bridge read")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level candidate read")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "direct candidate source read")
    reject(lambda: builtins.open(ROOT + "/.git/config"), "Git metadata read")
    reject(lambda: builtins.open(ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json"),
           "invalidated final holdout read")
    reject(lambda: builtins.open(ROOT + "/oracle/phase2/evidence/"
                                "repaired-rust-original-campaign-v16-rust-phase2-v25-"
                                "rust-capture-clamp-v1-root-provenance-original-p0-v25-"
                                "failures.json.gz"), "compressed original archive read")
    reject(lambda: builtins.open(ROOT + "/experiments/rust_native_architecture_public_v3/"
                                "v28-combined-public-run-001/"
                                "public-10434-correctness.raw.json"),
           "raw public comparison evidence read")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "workspace directory mutation")
    reject(lambda: time.time(), "clock or timing sample")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native library load")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None),
           "compiler process or candidate execution")
    reject(lambda: sys.audit("socket.connect", None, None), "network access")
    require(rejected >= 75 and wall.candidate_source_reads == 0
            and wall.workspace_mutations == 0 and not wall.input_authorized,
            "complete hostile controls without opening a bridge or mutating workspace")
    no_matching_imports()
    return {"synthetic_input_bytes": len(source),
            "synthetic_output_bytes": len(corrected), "source_delta_bytes": 202,
            "hostile_controls_rejected": rejected,
            "valid_scanner_protocol_controls": len(controls),
            "invalid_scanner_protocol_controls": 11,
            "complete_original_correction_preserved": True,
            "safe_capture_clamp_preserved": True,
            "candidate_source_files_read": 0, "workspace_mutations": 0,
            "candidate_executions": 0, "final_holdout": FINAL_HOLDOUT}


def value(document: object, key: str, expected: object) -> None:
    require(type(document) is dict and document.get(key) == expected,
            "reject incomplete or substituted authenticated evidence: " + key)


def authenticate_original(raw: bytes) -> dict[str, object]:
    document = StrictJSON(raw).decode()
    for key, expected in (
            ("schema", "rebar-owned-repaired-rust-original-campaign-v25-"
                       "durable-publication-receipt"),
            ("status", "PASS"), ("publication_status", "PASS"),
            ("publication_pass_means", "DURABLE PUBLICATION ONLY"),
            ("candidate_status", "FAIL"), ("candidate_qualified", False),
            ("suite_count", 13), ("attempted_suite_count", 13),
            ("started_suite_count", 13), ("completed_suite_count", 13),
            ("case_execution_denominator", 31237),
            ("semantic_mismatch_count", 1352),
            ("verified_passing_case_count", 15877),
            ("infrastructure_failure_count", 0), ("holdout", "NOT OPENED"),
            ("hidden_cases_read", 0), ("clock_samples", 0),
            ("actual_v25_build_archive_read_count", 0),
            ("actual_v25_build_archive_gzip_inflation_count", 0),
            ("winner_selected", False)):
        value(document, key, expected)
    suites = document.get("suite_integrity")
    require(type(suites) is list and len(suites) == 13,
            "require all thirteen immutable original failure suites")
    indexed: dict[str, dict] = {}
    for suite in suites:
        require(type(suite) is dict and type(suite.get("suite")) is str,
                "reject malformed original suite ledger")
        name = suite["suite"]
        require(name not in indexed, "reject duplicate original failure suite")
        indexed[name] = suite
        value(suite, "fully_observed", True)
        value(suite, "actual_worker_started", True)
    for name, denominator, mismatches in (("substitution_v2", 5120, 240),
                                          ("shape_v2", 10240, 1112)):
        suite = indexed[name]
        value(suite, "case_execution_denominator", denominator)
        value(suite, "mismatch_count", mismatches)
        value(suite, "verified_passing_case_count", 0)
        value(suite, "failure_class", "SEMANTIC MISMATCH")
    require(sum(suite["case_execution_denominator"] for suite in suites) == 31237
            and sum(suite["mismatch_count"] for suite in suites) == 1352
            and sum(suite["verified_passing_case_count"] for suite in suites) == 15877,
            "preserve complete authentic original denominator and mismatch partition")
    archive = document.get("archive")
    value(archive, "sha256",
          "dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7")
    value(archive, "size_bytes", 3771743)
    value(archive, "inode", 524845)
    return {"receipt_path": V25_RECEIPT, "receipt_sha256": OWNERS[8][2],
            "publication_status": "PASS", "candidate_status": "FAIL",
            "suite_count": 13, "case_execution_denominator": 31237,
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "substitution_v2_mismatch_count": 240,
            "shape_v2_mismatch_count": 1112, "compressed_archive_open_count": 0}


def authenticate_public(raw: bytes, architecture: str) -> dict[str, object]:
    document = StrictJSON(raw).decode()
    generation = "v3" if architecture == "v28" else "v2"
    for key, expected in (
            ("schema", "rebar-owned-rust-native-architecture-public-gate-"
                       + generation + "-durable-publication-receipt"),
            ("status", "PASS"), ("architecture", architecture),
            ("public_10434_case_count", 10434),
            ("public_10434_mismatch_count", 1145),
            ("public_10434_correctness_status", "FAIL"),
            ("hidden_cases_read", 0),
            ("controller_final_holdout_content_open_count", 0),
            ("candidate_qualified", False), ("winner_selected", False),
            ("retired_v2_proposal_status",
             "COMPROMISED; RETIRED; NOT ACCESSED BY THIS CONTROLLER"),
            ("current_final_holdout", FINAL_HOLDOUT),
            ("final_holdout_case_status",
             "NOT GENERATED; REKEYED SUCCESSOR REQUIRED")):
        value(document, key, expected)
    artifacts = document.get("artifacts")
    require(type(artifacts) is list and len(artifacts) == 18,
            "require complete immutable public receipt artifact inventory")
    matches = [artifact for artifact in artifacts
               if type(artifact) is dict and type(artifact.get("path")) is str
               and artifact["path"].endswith("/public-10434-correctness.raw.json")]
    require(len(matches) == 1,
            "identify one raw comparison only by its public plaintext receipt")
    comparison = matches[0]
    for key, expected in (("sha256", RAW_COMPARISON_SHA256),
                          ("bytes", RAW_COMPARISON_BYTES), ("device", DEVICE),
                          ("mode", "0600")):
        value(comparison, key, expected)
    inodes = {"v26": 525295, "v27": 525408, "v28": 525893}
    value(comparison, "inode", inodes[architecture])
    require("/" + architecture + "-" in comparison["path"],
            "reject substituted architecture-specific raw evidence identity")
    roles = {"v26": 9, "v27": 10, "v28": 11}
    return {"architecture": architecture, "receipt_path": OWNERS[roles[architecture]][1],
            "receipt_sha256": OWNERS[roles[architecture]][2],
            "public_case_count": 10434, "public_mismatch_count": 1145,
            "raw_comparison_sha256_receipt_only": RAW_COMPARISON_SHA256,
            "raw_comparison_bytes_receipt_only": RAW_COMPARISON_BYTES,
            "raw_comparison_open_count": 0}


def authenticate_dataset_source(raw: bytes) -> dict[str, object]:
    marker = b"def public_datasets() -> tuple["
    require(raw.count(marker) == 1,
            "require exactly one authenticated public dataset producer")
    first = raw.index(marker)
    last = raw.index(b"\ndef ", first + len(marker))
    names: list[str] = []
    for line in raw[first:last].splitlines():
        if line.startswith((b'        ("text.', b'        ("bytes.')):
            start = line.index(b'"') + 1
            finish = line.index(b'"', start)
            names.append(line[start:finish].decode("ascii"))
    first_operation = raw.index(b"OPERATIONS = (\n")
    last_operation = raw.index(b"\n)\n", first_operation)
    operations = raw[first_operation:last_operation]
    for operation in TARGETED_OPERATIONS + PRESERVED_OPERATIONS:
        require(operations.count(('    "' + operation + '",').encode("ascii")) == 1,
                "authenticate targeted and preserved public scanner operations")
    model = public_model(tuple(names))
    model["public_dataset_source_path"] = PUBLIC_DATASET_SOURCE
    model["public_dataset_source_sha256"] = OWNERS[12][2]
    model["dataset_identifiers_sha256"] = digest(canonical(names).encode("utf-8"))
    model["public_dataset_producer_imported_or_executed"] = False
    return model


def authenticate_predecessors(owners: dict[str, bytes]) -> dict[str, object]:
    complete = StrictJSON(owners["complete_contract"]).decode()
    scanner = StrictJSON(owners["scanner_contract"]).decode()
    for document, schema, source_path, source_sha, protocol_path, protocol_sha in (
            (complete, "rebar-owned-rust-complete-semantic-correction-v2-source-freeze",
             COMPLETE_SOURCE, OWNERS[0][2], COMPLETE_PROTOCOL, OWNERS[1][2]),
            (scanner, "rebar-owned-rust-scanner-pickle-semantics-v2-source-freeze",
             SCANNER_SOURCE, OWNERS[4][2], SCANNER_PROTOCOL, OWNERS[5][2])):
        for key, expected in (("schema", schema), ("version", 2), ("family", "rust"),
                              ("status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; "
                                         "NOT BUILT; NOT RUN"),
                              ("source", {"path": source_path, "sha256": source_sha}),
                              ("protocol", {"path": protocol_path,
                                             "sha256": protocol_sha})):
            value(document, key, expected)
    complete_correction = complete["exact_complete_semantic_correction"]
    for key, expected in (("target_path", INPUT), ("target_sha256", INPUT_SHA256),
                          ("target_bytes", INPUT_BYTES),
                          ("existing_expansion_correction_sites_preserved", 2),
                          ("new_substitution_order_correction_sites", 4),
                          ("changed_function", "rust_substitute_core"),
                          ("noncallback_replacement_validated_before_subject", True),
                          ("deferred_noncallback_subject_released_before_bytes_join", True),
                          ("duplicate_subject_release_precluded", True),
                          ("match_expand_forward_declaration_preserved", True),
                          ("match_expand_complete_definition_preserved", True),
                          ("capture_clamp_correction_retained", True),
                          ("no_external_introspection_correction_retained", True),
                          ("stdlib_matching_delegation_added", False),
                          ("external_regex_dependency_added", False)):
        value(complete_correction, key, expected)
    complete_partition = complete["exact_disjoint_original_failure_partition"]
    for key, expected in (("total_disjoint_original_failure_count", 1352),
                          ("substitution_v2_failure_count", 240),
                          ("shape_v2_ordering_failure_count", 1024),
                          ("shape_v2_trailing_probe_failure_count", 56),
                          ("shape_v2_malformed_expansion_failure_count", 32),
                          ("shape_v2_failure_count", 1112),
                          ("separate_ordering_probe_overlap_count", 32),
                          ("overlap_included_in_total", False),
                          ("disjoint_failure_projection_sha256",
                           "3f60354ffd19483b2419185637590f723b56ccb254fcf41405ddeb696d37db6d"),
                          ("separate_overlap_projection_sha256",
                           "50376b3356be2fc5c8151b78fd87e6011029f31c556dd577f9c103dfa2f63ae3")):
        value(complete_partition, key, expected)
    scanner_correction = scanner["exact_scanner_pickle_correction"]
    for key, expected in (("target_path", SCANNER_VARIANT),
                          ("target_sha256", SCANNER_VARIANT_SHA256),
                          ("target_bytes", SCANNER_VARIANT_BYTES),
                          ("source_delta_bytes", 202),
                          ("changed_function", "rust_scanner_reduce_ex"),
                          ("replacement_site_count", 1),
                          ("protocol_parser", "PyLong_AsInt"),
                          ("negative_one_without_error_is_valid", True),
                          ("low_protocol_threshold", 2),
                          ("existing_reconstructor", "rust_owned_pickle_reconstruction"),
                          ("protocol_two_and_five_unchanged", True),
                          ("match_reduce_ex_byte_identical", True),
                          ("capture_clamp_correction_retained", True),
                          ("generic_finish_clamp_occurrence_count", 2),
                          ("unique_capture_clamp_context_count", 1),
                          ("no_external_introspection_correction_retained", True),
                          ("stdlib_matching_delegation_added", False),
                          ("external_regex_dependency_added", False)):
        value(scanner_correction, key, expected)
    scanner_partition = scanner["exact_targeted_public_partition"]
    for key, expected in (("dataset_count", 94), ("targeted_operation_count", 5),
                          ("gross_targeted_public_mismatch_count", 470),
                          ("targeted_operations", list(TARGETED_OPERATIONS)),
                          ("named_unicode_comment_overlap_dataset_count", 3),
                          ("named_unicode_comment_overlap_datasets", list(OVERLAP_DATASETS)),
                          ("named_unicode_comment_overlap_row_count", 15),
                          ("scanner_only_independent_public_improvement_count", 455),
                          ("preserved_high_protocol_operations", list(PRESERVED_OPERATIONS)),
                          ("preserved_high_protocol_row_count", 188),
                          ("preserved_high_protocol_comment_compile_failure_count", 6),
                          ("independent_effect_measured", False),
                          ("candidate_correctness", "NOT MEASURED")):
        value(scanner_partition, key, expected)
    complete_application = StrictJSON(owners["complete_application"]).decode()
    scanner_application = StrictJSON(owners["scanner_application"]).decode()
    for document, schema, expected_source, expected_protocol, expected_contract, target, sha, count in (
            (complete_application,
             "rebar-owned-rust-complete-semantic-correction-v2-source-freeze-"
             "root-materialization", OWNERS[0][2], OWNERS[1][2], OWNERS[2][2],
             INPUT, INPUT_SHA256, INPUT_BYTES),
            (scanner_application,
             "rebar-owned-rust-scanner-pickle-semantics-v2-source-freeze-"
             "root-materialization", OWNERS[4][2], OWNERS[5][2], OWNERS[6][2],
             SCANNER_VARIANT, SCANNER_VARIANT_SHA256, SCANNER_VARIANT_BYTES)):
        for key, expected in (("schema", schema), ("source_sha256", expected_source),
                              ("protocol_sha256", expected_protocol),
                              ("contract_sha256", expected_contract),
                              ("target_path", target), ("target_sha256", sha),
                              ("target_bytes", count)):
            value(document, key, expected)
        effects = document.get("effects")
        for key, expected in (("candidate_source_files_read", 1),
                              ("candidate_executions", 0), ("candidate_imports", 0),
                              ("compiler_processes_started", 0),
                              ("native_binary_files_opened", 0),
                              ("compressed_archives_opened", 0),
                              ("clock_samples", 0), ("workspace_mutations", 2),
                              ("candidate_correctness", "NOT MEASURED"),
                              ("runtime_non_delegation", "NOT ESTABLISHED"),
                              ("final_holdout", FINAL_HOLDOUT)):
            value(effects, key, expected)
    for key, expected in (("status", "PASS; ALL ORIGINAL FAILURES MODELED; "
                                     "NOT BUILT; NOT RUN"),
                          ("complete_disjoint_original_failure_count", 1352),
                          ("substitution_v2_failure_count", 240),
                          ("shape_v2_failure_count", 1112),
                          ("separate_ordering_probe_overlap_count", 32),
                          ("capture_clamp_preserved", True),
                          ("no_external_introspection_preserved", True),
                          ("existing_expansion_correction_preserved", True),
                          ("candidate_input_authorized_after_all_source_controls", True),
                          ("replacement_validated_before_subject", True),
                          ("duplicate_subject_release_precluded", True),
                          ("post_correction_actual_mismatch_count", "NOT MEASURED")):
        value(complete_application, key, expected)
    for key, expected in (("status", "PASS; EXACT SCANNER PICKLE CORRECTION; "
                                     "NOT BUILT; NOT RUN"),
                          ("source_delta_bytes", 202),
                          ("gross_targeted_public_mismatch_count", 470),
                          ("named_unicode_comment_overlap_row_count", 15),
                          ("scanner_only_independent_public_improvement_count", 455),
                          ("candidate_correctness", "NOT MEASURED")):
        value(scanner_application, key, expected)
    require(owners["scanner_source"].count(ORIGINAL_SCANNER) == 1
            and owners["scanner_source"].count(CORRECTED_SCANNER) == 1,
            "authenticate exact original and corrected scanner bodies in frozen source")
    return {"complete_source_sha256": OWNERS[0][2],
            "complete_protocol_sha256": OWNERS[1][2],
            "complete_contract_sha256": OWNERS[2][2],
            "complete_application_sha256": OWNERS[3][2],
            "complete_bridge_sha256": INPUT_SHA256,
            "complete_bridge_bytes": INPUT_BYTES,
            "scanner_source_sha256": OWNERS[4][2],
            "scanner_protocol_sha256": OWNERS[5][2],
            "scanner_contract_sha256": OWNERS[6][2],
            "scanner_application_sha256": OWNERS[7][2],
            "scanner_bridge_sha256": SCANNER_VARIANT_SHA256,
            "scanner_bridge_bytes": SCANNER_VARIANT_BYTES,
            "complete_original_disjoint_modeled_count": 1352,
            "scanner_gross_modeled_count": 470,
            "scanner_overlap_modeled_count": 15,
            "scanner_independent_modeled_count": 455,
            "complete_bridge_opened_in_source_mode": False,
            "standalone_scanner_bridge_opened_in_any_mode": False}


def validate_contract(document: object, source_sha: str, protocol_sha: str) -> None:
    for key, expected in (("schema", SCHEMA), ("version", 1), ("family", "rust"),
                          ("phase", "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS"),
                          ("status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; "
                                     "NOT BUILT; NOT RUN"),
                          ("final_holdout", FINAL_HOLDOUT),
                          ("source", {"path": SOURCE, "sha256": source_sha}),
                          ("protocol", {"path": PROTOCOL, "sha256": protocol_sha})):
        value(document, key, expected)
    composition = document.get("exact_complete_scanner_bridge_composition")
    for key, expected in (
            ("complete_input_path", INPUT), ("complete_input_sha256", INPUT_SHA256),
            ("complete_input_bytes", INPUT_BYTES), ("complete_input_device", DEVICE),
            ("complete_input_inode", INPUT_INODE), ("complete_input_mode", "0600"),
            ("standalone_scanner_path", SCANNER_VARIANT),
            ("standalone_scanner_sha256", SCANNER_VARIANT_SHA256),
            ("standalone_scanner_bytes", SCANNER_VARIANT_BYTES),
            ("standalone_scanner_device", DEVICE),
            ("standalone_scanner_inode", SCANNER_VARIANT_INODE),
            ("target_path", TARGET), ("target_sha256", OUTPUT_SHA256),
            ("target_bytes", OUTPUT_BYTES), ("source_delta_bytes", 202),
            ("changed_function", "rust_scanner_reduce_ex"),
            ("replacement_site_count", 1),
            ("complete_substitution_core_byte_identical", True),
            ("complete_match_expand_byte_identical", True),
            ("safe_capture_clamp_retained", True),
            ("generic_finish_clamp_occurrence_count", 2),
            ("unique_capture_clamp_context_count", 1),
            ("no_external_introspection_retained", True),
            ("external_regex_dependency_added", False),
            ("stdlib_matching_delegation_added", False),
            ("scanner_protocol_parser", "PyLong_AsInt"),
            ("negative_one_without_error_is_valid", True),
            ("protocol_two_and_five_unchanged", True),
            ("candidate_built", False), ("candidate_imported", False),
            ("candidate_matching", "NOT RUN"), ("candidate_qualified", False),
            ("runtime_non_delegation", "NOT ESTABLISHED")):
        value(composition, key, expected)
    original = document.get("exact_disjoint_original_failure_partition")
    for key, expected in (("original_case_execution_denominator", 31237),
                          ("original_suite_count", 13),
                          ("total_disjoint_original_failure_count", 1352),
                          ("substitution_v2_failure_count", 240),
                          ("shape_v2_ordering_failure_count", 1024),
                          ("shape_v2_trailing_probe_failure_count", 56),
                          ("shape_v2_malformed_expansion_failure_count", 32),
                          ("shape_v2_failure_count", 1112),
                          ("separate_ordering_probe_overlap_count", 32),
                          ("separate_ordering_probe_overlap_included", False),
                          ("post_correction_actual_mismatch_count", "NOT MEASURED")):
        value(original, key, expected)
    scanner = document.get("exact_targeted_public_partition")
    for key, expected in (("dataset_count", 94), ("targeted_operation_count", 5),
                          ("targeted_operations", list(TARGETED_OPERATIONS)),
                          ("gross_targeted_public_mismatch_count", 470),
                          ("named_unicode_comment_overlap_dataset_count", 3),
                          ("named_unicode_comment_overlap_datasets", list(OVERLAP_DATASETS)),
                          ("named_unicode_comment_overlap_row_count", 15),
                          ("scanner_only_independent_public_improvement_count", 455),
                          ("preserved_high_protocol_operations", list(PRESERVED_OPERATIONS)),
                          ("preserved_high_protocol_row_count", 188),
                          ("preserved_high_protocol_comment_compile_failure_count", 6),
                          ("independent_effect_measured", False),
                          ("candidate_correctness", "NOT MEASURED")):
        value(scanner, key, expected)
    predecessors = document.get("authenticated_committed_predecessors")
    for key, expected in (("complete_source_sha256", OWNERS[0][2]),
                          ("complete_protocol_sha256", OWNERS[1][2]),
                          ("complete_contract_sha256", OWNERS[2][2]),
                          ("complete_application_sha256", OWNERS[3][2]),
                          ("scanner_source_sha256", OWNERS[4][2]),
                          ("scanner_protocol_sha256", OWNERS[5][2]),
                          ("scanner_contract_sha256", OWNERS[6][2]),
                          ("scanner_application_sha256", OWNERS[7][2]),
                          ("both_actual_materialization_receipts_authenticated", True),
                          ("both_candidate_bridges_opened_in_source_mode", False)):
        value(predecessors, key, expected)
    evidence = document.get("authenticated_public_v25_v26_v27_v28_receipts")
    for key, expected in (("v25_receipt_sha256", OWNERS[8][2]),
                          ("v26_receipt_sha256", OWNERS[9][2]),
                          ("v27_receipt_sha256", OWNERS[10][2]),
                          ("v28_receipt_sha256", OWNERS[11][2]),
                          ("public_dataset_source_sha256", OWNERS[12][2]),
                          ("public_case_count", 10434),
                          ("public_mismatch_count", 1145),
                          ("comparison_sha256_receipt_only", RAW_COMPARISON_SHA256),
                          ("comparison_bytes_receipt_only", RAW_COMPARISON_BYTES),
                          ("identical_v26_v27_v28_public_comparison_digest", True),
                          ("raw_public_comparison_artifacts_opened", 0)):
        value(evidence, key, expected)
    wall = document.get("physical_source_wall")
    for key, expected in (("installed_before_owner_reads", True),
                          ("descriptor_relative_o_nofollow", True),
                          ("authenticated_public_predecessor_owner_count", len(OWNERS)),
                          ("authenticated_public_owner_count_including_current", len(OWNERS) + 3),
                          ("source_mode_candidate_source_reads", 0),
                          ("self_test_candidate_source_reads", 0),
                          ("source_mode_filesystem_writes", 0),
                          ("self_test_filesystem_writes", 0),
                          ("archive_content_reads", 0),
                          ("raw_public_comparison_artifacts_opened", 0),
                          ("native_binary_reads", 0), ("timer_reads", 0),
                          ("git_metadata_reads", 0),
                          ("final_holdout_content_reads", 0),
                          ("apply_requires_explicit_root_authorization", True),
                          ("apply_requires_frozen_commit_equals_pushed_commit", True),
                          ("candidate_input_denied_until_all_source_controls_pass", True),
                          ("apply_candidate_source_read_count", 1),
                          ("standalone_scanner_candidate_source_reads", 0),
                          ("apply_exclusive_new_target_only", True),
                          ("candidate_execution_allowed", False),
                          ("compiler_launch_allowed", False),
                          ("network_access_allowed", False),
                          ("final_holdout", FINAL_HOLDOUT)):
        value(wall, key, expected)
    effects = document.get("source_only_effects")
    for key in ("candidate_source_files_read", "candidate_executions",
                "candidate_imports", "candidate_workers_started",
                "compiler_processes_started", "native_binary_files_opened",
                "native_libraries_loaded", "raw_public_comparison_artifacts_opened",
                "compressed_archives_opened", "compressed_archives_inflated",
                "final_holdout_cases_opened", "final_holdout_cases_generated",
                "final_holdout_proposal_files_opened", "git_metadata_reads",
                "clock_samples", "timing_trials_run", "network_requests",
                "workspace_mutations"):
        value(effects, key, 0)
    for key, expected in (("final_holdout", FINAL_HOLDOUT),
                          ("candidate_correctness", "NOT MEASURED"),
                          ("candidate_matching", "NOT RUN"),
                          ("candidate_semantic_mismatch_count", "NOT MEASURED"),
                          ("runtime_non_delegation", "NOT ESTABLISHED"),
                          ("performance", "NOT MEASURED"),
                          ("candidate_qualified", False), ("winner_selected", False)):
        value(effects, key, expected)


def parse_arguments(arguments: list[str]) -> dict[str, object]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require explicit complete scanner immutable arguments")
    flags = {"--self-test", "--verify-source", "--verify-frozen-context",
             "--apply", "--root-authorized"}
    options = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
               "--frozen-commit", "--pushed-commit"}
    parsed: dict[str, object] = {}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        require(argument in flags or argument in options,
                "reject unknown complete scanner option: " + argument)
        require(argument not in parsed, "reject duplicate option: " + argument)
        if argument in flags:
            parsed[argument] = True
            index += 1
        else:
            require(index + 1 < len(arguments), "require complete option: " + argument)
            parsed[argument] = arguments[index + 1]
            index += 2
    modes = tuple(mode for mode in ("--self-test", "--verify-source",
                                     "--verify-frozen-context", "--apply")
                  if parsed.get(mode) is True)
    require(len(modes) == 1, "require exactly one source-only gate or root-only apply")
    mode = modes[0]
    if mode == "--self-test":
        require(set(parsed) == {mode}, "source-only self-test accepts no owner pins")
    elif mode in ("--verify-source", "--verify-frozen-context"):
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256"},
                "source verification requires the exact frozen owner SHA-256 triple")
    else:
        require(set(parsed) == {mode, "--root-authorized", "--source-sha256",
                                "--protocol-sha256", "--contract-sha256",
                                "--frozen-commit", "--pushed-commit"},
                "root-only apply requires explicit authorization and pushed owner freeze")
        for label in ("--frozen-commit", "--pushed-commit"):
            commit = parsed[label]
            require(type(commit) is str and len(commit) == 40
                    and all(char in "0123456789abcdef" for char in commit),
                    "require complete lowercase frozen commit: " + label)
        require(parsed["--frozen-commit"] == parsed["--pushed-commit"],
                "refuse materialization until frozen commit has actually been pushed")
    for label in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if label in parsed:
            checked_sha(parsed[label], label)
    return parsed


def effects(wall: SourceWall, mode: str) -> dict[str, object]:
    return {"mode": mode, "approved_public_owner_reads": wall.public_owner_reads,
            "candidate_source_files_read": wall.candidate_source_reads,
            "standalone_scanner_candidate_source_reads": 0,
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_workers_started": 0, "compiler_processes_started": 0,
            "native_binary_files_opened": 0, "native_libraries_loaded": 0,
            "raw_public_comparison_artifacts_opened": 0,
            "compressed_archives_opened": 0, "compressed_archives_inflated": 0,
            "final_holdout_cases_opened": 0, "final_holdout_cases_generated": 0,
            "final_holdout_proposal_files_opened": 0, "git_metadata_reads": 0,
            "clock_samples": 0, "timing_trials_run": 0, "network_requests": 0,
            "workspace_mutations": wall.workspace_mutations,
            "final_holdout": FINAL_HOLDOUT,
            "candidate_correctness": "NOT MEASURED",
            "candidate_matching": "NOT RUN",
            "candidate_semantic_mismatch_count": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "candidate_qualified": False,
            "winner_selected": False}


def main(arguments: list[str]) -> dict[str, object]:
    options = parse_arguments(arguments)
    apply = options.get("--apply") is True
    wall = SourceWall(apply)
    no_matching_imports()
    wall.install()
    if options.get("--self-test") is True:
        controls = synthetic_tests(wall)
        require(wall.public_owner_reads == 0 and wall.candidate_source_reads == 0
                and wall.workspace_mutations == 0 and wall.root is None,
                "self-test must read no owner or candidate and mutate no workspace")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "synthetic_controls": controls, "effects": effects(wall, "SELF-TEST")}

    source_sha = options["--source-sha256"]
    protocol_sha = options["--protocol-sha256"]
    contract_sha = options["--contract-sha256"]
    assert isinstance(source_sha, str) and isinstance(protocol_sha, str)
    assert isinstance(contract_sha, str)
    wall.open_root()
    wall.read(SOURCE, None, None, source_sha)
    wall.read(PROTOCOL, None, None, protocol_sha)
    contract = StrictJSON(wall.read(CONTRACT, None, None, contract_sha)).decode()
    validate_contract(contract, source_sha, protocol_sha)
    owners: dict[str, bytes] = {}
    for role, relative, expected, count, inode in OWNERS:
        require(not relative.startswith(("candidates/", "experiments/"))
                and not relative.endswith((".gz", ".so"))
                and "holdout" not in relative and "phase3/" not in relative
                and ".git/" not in relative,
                "never authorize candidate, native, archive, final, Git, or raw owner")
        owners[role] = wall.read(relative, count, inode, expected)
    predecessors = authenticate_predecessors(owners)
    original = authenticate_original(owners["v25_complete_failure_receipt"])
    public_v26 = authenticate_public(owners["v26_public_receipt"], "v26")
    public_v27 = authenticate_public(owners["v27_public_receipt"], "v27")
    public_v28 = authenticate_public(owners["v28_public_receipt"], "v28")
    dataset = authenticate_dataset_source(owners["public_dataset_source"])
    require(public_v26["raw_comparison_sha256_receipt_only"]
            == public_v27["raw_comparison_sha256_receipt_only"]
            == public_v28["raw_comparison_sha256_receipt_only"]
            == RAW_COMPARISON_SHA256,
            "authenticate the same complete V26/V27/V28 public comparison receipt")
    require(wall.public_owner_reads == len(OWNERS) + 3
            and wall.candidate_source_reads == 0 and wall.workspace_mutations == 0,
            "authenticate both predecessor triples/apps and four plaintext receipts only")
    controls = synthetic_tests(wall)
    if not apply:
        no_matching_imports()
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; COMPLETE ORIGINAL AND SCANNER SOURCE FROZEN",
                "source_sha256": source_sha, "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "authenticated_public_owner_count": len(OWNERS),
                "authenticated_committed_predecessors": predecessors,
                "authenticated_original_v25": original,
                "authenticated_public_v26": public_v26,
                "authenticated_public_v27": public_v27,
                "authenticated_public_v28": public_v28,
                "modeled_public_scanner_partition": dataset,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "complete_original_modeled_correction_count": 1352,
                "scanner_gross_modeled_correction_count": 470,
                "scanner_overlap_modeled_count": 15,
                "scanner_independent_modeled_correction_count": 455,
                "synthetic_controls": controls,
                "effects": effects(wall, "SOURCE FREEZE")}

    wall.authorize_input()
    complete = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA256)
    composed = transform(complete, exact=True)
    wall.materialize(composed)
    no_matching_imports()
    require(wall.candidate_source_reads == 1 and wall.workspace_mutations == 2,
            "create exactly one exclusive directory and one composed source bridge")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; COMPLETE ORIGINAL AND SCANNER COMPOSED; "
                      "NOT BUILT; NOT RUN",
            "frozen_commit": options["--frozen-commit"],
            "pushed_commit": options["--pushed-commit"],
            "source_sha256": source_sha, "protocol_sha256": protocol_sha,
            "contract_sha256": contract_sha,
            "complete_input_path": INPUT, "complete_input_sha256": INPUT_SHA256,
            "complete_input_bytes": INPUT_BYTES,
            "standalone_scanner_sha256_receipt_only": SCANNER_VARIANT_SHA256,
            "standalone_scanner_bytes_receipt_only": SCANNER_VARIANT_BYTES,
            "target_path": TARGET, "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES, "source_delta_bytes": 202,
            "complete_original_disjoint_modeled_correction_count": 1352,
            "substitution_v2_failure_count": 240,
            "shape_v2_failure_count": 1112,
            "separate_ordering_probe_overlap_count": 32,
            "gross_targeted_public_mismatch_count": 470,
            "named_unicode_comment_overlap_row_count": 15,
            "scanner_only_independent_public_improvement_count": 455,
            "candidate_input_authorized_after_all_source_controls": True,
            "actual_root_hostile_controls_rejected": controls["hostile_controls_rejected"],
            "capture_clamp_preserved": True,
            "no_external_introspection_preserved": True,
            "existing_expansion_correction_preserved": True,
            "complete_substitution_core_byte_identical": True,
            "post_correction_actual_mismatch_count": "NOT MEASURED",
            "final_holdout": FINAL_HOLDOUT,
            "effects": effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError, KeyError,
            IndexError, TypeError, OverflowError) as error:
        sys.stderr.write("rust-complete-scanner-bridge-v1: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
