#!/usr/bin/env python3
"""Freeze an owned one-function Rust scanner pickle-protocol correction.

Verification reads only its three frozen owners, four committed plaintext
receipts, and the public dataset producer. Candidate source, raw comparison
artifacts, archives, native objects, holdouts, clocks, and subprocesses are
physically rejected. Only separately authorized root materialization may read
the clean, capture-clamped, no-introspection predecessor once and exclusively
create the one immutable successor.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("source-only scanner pickle freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
DEVICE = 2064
SCHEMA = "rebar-owned-rust-scanner-pickle-semantics-v1-source-freeze"
SOURCE = "tools/apply_owned_rust_scanner_pickle_semantics_v1.py"
PROTOCOL = "oracle/phase2/RUST-SCANNER-PICKLE-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/rust-scanner-pickle-semantics-v1.json"
INPUT = "candidates/rust/variants/no_external_introspection_v1/py_bridge.c"
TARGET_DIRECTORY = "candidates/rust/variants/scanner_pickle_semantics_v1"
TARGET = TARGET_DIRECTORY + "/py_bridge.c"
INPUT_SHA256 = "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7"
INPUT_BYTES = 177146
INPUT_INODE = 524811
OUTPUT_SHA256 = "e074be7b4a6882f2ac004f027f941240a373c85eb9267c59da4d5d354b8f4bfc"
OUTPUT_BYTES = 177348
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 300_000
MAX_JSON_DEPTH = 80
FINAL_HOLDOUT = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
RAW_COMPARISON_SHA256 = (
    "7fc4c743e35bbe4f57ed0e3a872b9a9646b2603feedb9ae2c24421afed5430aa"
)
RAW_COMPARISON_BYTES = 1428906
ORIGINAL_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-"
    "failures-publication-receipt.json"
)
NO_INTROSPECTION_RECEIPT = (
    "oracle/phase2/evidence/rust-no-external-introspection-v1-application.json"
)
PUBLIC_V26_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-"
    "anchor-public-run-001-publication-receipt.json"
)
PUBLIC_V27_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-"
    "compiler-public-run-001-publication-receipt.json"
)
PUBLIC_DATASET_SOURCE = "tools/rust_public_practice_benchmark_v2.py"

# Public plaintext only: four committed evidence receipts and the producer
# defining all 94 public datasets. Raw comparison artifacts and archives are
# intentionally absent from this descriptor-relative allowlist.
# role, relative path, full SHA-256, byte count, device-2064 inode.
OWNERS = (
    ("original_v25_receipt", ORIGINAL_RECEIPT,
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59",
     11832, 524846),
    ("no_introspection_receipt", NO_INTROSPECTION_RECEIPT,
     "57e28ad65b538db5189f264904d303f37f13506022eae07b12185a52f2624a43",
     1774, 524813),
    ("public_v26_receipt", PUBLIC_V26_RECEIPT,
     "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80",
     40906, 525333),
    ("public_v27_receipt", PUBLIC_V27_RECEIPT,
     "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449",
     68330, 525426),
    ("public_dataset_source", PUBLIC_DATASET_SOURCE,
     "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6",
     112729, 429259),
)

DATASETS = (
    "text.literal.short",
    "text.ascii.ignorecase",
    "text.unicode.words",
    "text.unicode.ascii_boundary",
    "text.unicode.combining",
    "text.unicode.astral",
    "text.unicode.kelvin",
    "text.unicode.long_s",
    "text.unicode.turkish",
    "text.unicode.greek",
    "text.unicode.digits",
    "text.unicode.spaces",
    "text.multiline.anchors",
    "text.dotall.lazy",
    "text.verbose.groups",
    "text.lookbehind.fixed",
    "text.lookahead.negative",
    "text.alternation.prefix",
    "text.backreference",
    "text.conditional.group",
    "text.atomic.group",
    "text.possessive.repeat",
    "text.flags.scoped",
    "text.absolute.anchors",
    "text.boundary.repeated",
    "text.nested.repeats",
    "text.email.like",
    "text.path.like",
    "text.json.like",
    "text.scanner.remainder",
    "text.no.match",
    "text.long.repeated",
    "text.scanner.scoped_i_enable",
    "text.scanner.scoped_i_disable",
    "text.scanner.scoped_s_enable",
    "text.scanner.scoped_s_disable",
    "text.scanner.scoped_m_enable",
    "text.scanner.scoped_m_disable",
    "text.scanner.scoped_a_enable",
    "text.scanner.scoped_u_override",
    "text.comment.inline_unknown_named_unicode",
    "text.comment.global_verbose_unknown_named_unicode",
    "text.comment.scoped_verbose_unknown_named_unicode",
    "text.named_unicode.valid",
    "text.prefilter.dense_first_sparse_last",
    "text.prefilter.sparse_first_dense_last",
    "text.buffer.changing_exporter",
    "bytes.literal.short",
    "bytes.ascii.ignorecase",
    "bytes.high.bit.words",
    "bytes.null.embedded",
    "bytes.hex.escapes",
    "bytes.octal.escapes",
    "bytes.multiline.anchors",
    "bytes.dotall.lazy",
    "bytes.verbose.groups",
    "bytes.lookbehind.fixed",
    "bytes.lookahead.negative",
    "bytes.alternation.prefix",
    "bytes.backreference",
    "bytes.conditional.group",
    "bytes.atomic.group",
    "bytes.possessive.repeat",
    "bytes.flags.scoped",
    "bytes.absolute.anchors",
    "bytes.boundary.repeated",
    "bytes.nested.repeats",
    "bytes.email.like",
    "bytes.path.like",
    "bytes.json.like",
    "bytes.no.match",
    "bytes.long.repeated",
    "bytes.bytearray.scanner_remainder",
    "bytes.bytearray.high_bit",
    "bytes.memoryview.mutable.scanner_remainder",
    "bytes.memoryview.readonly.scanner_remainder",
    "bytes.memoryview.mutable.nul",
    "bytes.memoryview.readonly.high_bit",
    "bytes.whitespace.binary",
    "bytes.scanner.scoped_i_enable",
    "bytes.scanner.scoped_i_disable",
    "bytes.scanner.scoped_s_enable",
    "bytes.scanner.scoped_s_disable",
    "bytes.scanner.scoped_m_enable",
    "bytes.scanner.scoped_m_disable",
    "bytes.scanner.scoped_a_enable",
    "bytes.scanner.scoped_a_highbit",
    "bytes.comment.inline_unknown_named_unicode",
    "bytes.comment.global_verbose_unknown_named_unicode",
    "bytes.comment.scoped_verbose_unknown_named_unicode",
    "bytes.comment.inline_known_named_unicode",
    "bytes.prefilter.dense_first_sparse_last",
    "bytes.prefilter.sparse_first_dense_last",
    "bytes.buffer.changing_exporter",
)
OVERLAP_DATASETS = (
    "text.comment.inline_unknown_named_unicode",
    "text.comment.global_verbose_unknown_named_unicode",
    "text.comment.scoped_verbose_unknown_named_unicode",
)
TARGETED_OPERATIONS = (
    ("pattern.scanner.reduce_ex.negative", -1, "RECONSTRUCTION"),
    ("pattern.scanner.reduce_ex.zero", 0, "RECONSTRUCTION"),
    ("pattern.scanner.reduce_ex.one", 1, "RECONSTRUCTION"),
    ("pattern.scanner.reduce_ex.string", "0", "TYPE_ERROR"),
    ("pattern.scanner.reduce_ex.overflow", 1 << 40, "OVERFLOW_ERROR"),
)
PRESERVED_OPERATIONS = (
    ("pattern.scanner.reduce_ex.two", 2),
    ("pattern.scanner.reduce_ex.five", 5),
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
PRESERVED_MARKERS = (
    (b"static PyObject *rust_owned_pickle_reconstruction(PyObject *value) {", 1),
    (b"static PyObject *rust_scanner_reduce(RustIterator *iterator, PyObject *ignored) {", 1),
    (b"return rust_owned_pickle_reconstruction((PyObject *)iterator);", 1),
    (b"static PyMethodDef rust_iterator_scanner_search_method = {", 1),
    (b"static PyObject *rust_match_reduce_ex(RustMatch *match, PyObject *protocol) {", 1),
    (b"size_t first = begin > capture.length ? capture.length : begin;", 1),
    (b"size_t finish = end > capture.length ? capture.length : end;", 1),
    (b"if (finish < first) finish = first;", 1),
    (b"PyDescr_NewMethod(", 1),
    (b'    .name = "_sre.SRE_Scanner",', 1),
    (b'{"__reduce_ex__", (PyCFunction)rust_scanner_reduce_ex, METH_O,', 1),
)


class FreezeError(Exception):
    """Reject evidence drift, unsafe access, or a non-exact owned correction."""


def require(value: object, label: str) -> None:
    if value is not True:
        raise FreezeError(label)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete genuine bytes only")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require a complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "JSON string must be genuine text")
    replacements = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                    "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for char in value:
        point = ord(char)
        require(not 0xD800 <= point <= 0xDFFF, "reject unpaired JSON surrogate")
        result.append(replacements.get(char, "\\u" + format(point, "04x")
                      if point < 32 else char))
    result.append('"')
    return "".join(result)


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
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject nontext JSON key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject nonfinite or unsupported evidence JSON")


class StrictJSON:
    """Bounded duplicate-rejecting JSON parser without importing json or re."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require complete bounded strict evidence bytes")
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
        require(self.index < len(self.text), "reject incomplete JSON integer")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject leading-zero JSON integer")
        else:
            require(self.text[self.index] in "123456789", "reject invalid JSON integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        fraction = False
        if self.text[self.index:self.index + 1] == ".":
            fraction = True
            self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "reject missing JSON fractional digits")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            fraction = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "reject missing JSON exponent digits")
        require(self.index - start <= 128, "reject oversized evidence number")
        token = self.text[start:self.index]
        if not fraction:
            return int(token)
        result = float(token)
        require(result == result and result not in (float("inf"), float("-inf")),
                "reject nonfinite public receipt timing evidence")
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
                 "ctypes", "candidates", "rebar", "inspect", "functools",
                 "pickle", "copyreg", "subprocess", "socket", "threading",
                 "multiprocessing", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matcher, introspection, candidate, native loader, or worker")


class SourceWall:
    """Deny-default descriptor-relative plaintext ownership and root-only writer."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT)
                                + tuple(row[1] for row in OWNERS))
        self.allowed = self.public | (frozenset((INPUT,)) if apply else frozenset())
        self.live: dict[int, tuple[str, str]] = {}
        self.root: int | None = None
        self.open_ticket: tuple[str, int] | None = None
        self.mkdir_ticket: tuple[str, int] | None = None
        self.output_opened = False
        self.directory_created = False
        self.source_reads = 0
        self.public_reads = 0
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
        raise FreezeError("scanner-pickle source-only physical wall rejected " + reason)

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed-candidate-native-proposal-final-archive-or-open")
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
            self.deny("candidate-import-process-native-network-clock-or-code")

    def forbidden(self, reason: str):
        def reject(*_arguments: object, **_keywords: object) -> object:
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
        information = self.live.get(parent)
        require(information is not None and information[1] == "directory",
                "reject foreign parent directory descriptor")
        relative = (component if not information[0]
                    else information[0] + "/" + component)
        allowed = (any(path.startswith(relative + "/") for path in self.allowed)
                   or self.apply and (relative == TARGET_DIRECTORY
                                      or TARGET_DIRECTORY.startswith(relative + "/")))
        require(allowed and not relative.startswith((".git/", ".agents/", ".codex/")),
                "reject candidate, native, raw, archive, final, or private directory")
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
                "reject unowned candidate, native, comparison, archive, or holdout")
        require(self.root is not None, "open isolated workspace root first")
        components = relative.split("/")
        require(all(self.checked_component(item) for item in components),
                "reject malformed frozen owner path")
        descriptor = self.root
        stack: list[int] = []
        try:
            for component in components[:-1]:
                descriptor = self.child_directory(descriptor, component)
                stack.append(descriptor)
            return descriptor, stack, components[-1]
        except BaseException:
            for descriptor in reversed(stack):
                self.close(descriptor)
            raise

    def read(self, relative: str, count: int | None, inode: int | None,
             expected_sha256: str) -> bytes:
        require(self.installed and relative in self.allowed,
                "reject candidate source outside separately authorized root apply")
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
                    and before.st_dev == DEVICE
                    and 0 < before.st_size <= MAX_OWNER_BYTES
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
                    "reject concurrently changed immutable frozen owner: " + relative)
            raw = b"".join(chunks)
            require(digest(raw) == checked_sha(expected_sha256, relative),
                    "reject substituted complete immutable owner digest: " + relative)
            if relative == INPUT:
                require(self.apply and self.source_reads == 0,
                        "candidate source may be read once during root apply only")
                self.source_reads += 1
            else:
                self.public_reads += 1
            return raw
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for descriptor in reversed(stack):
                self.close(descriptor)

    def make_target_directory(self) -> int:
        require(self.apply and not self.directory_created and self.root is not None,
                "require exactly one explicitly authorized root-only directory")
        descriptor = self.root
        stack: list[int] = []
        components = TARGET_DIRECTORY.split("/")
        try:
            for component in components[:-1]:
                descriptor = self.child_directory(descriptor, component)
                stack.append(descriptor)
            name = self.checked_component(components[-1])
            require(self.mkdir_ticket is None, "reject nested directory authorization")
            self.mkdir_ticket = (name, 0o700)
            try:
                self.native_mkdir(name, 0o700, dir_fd=descriptor)
            finally:
                self.mkdir_ticket = None
            self.directory_created = True
            self.workspace_mutations += 1
            return self.child_directory(descriptor, name)
        finally:
            for descriptor in reversed(stack):
                self.close(descriptor)

    def materialize(self, raw: bytes) -> None:
        require(self.apply and self.source_reads == 1 and not self.output_opened,
                "authorize exactly one exclusive root-only scanner bridge")
        require(type(raw) is bytes and len(raw) == OUTPUT_BYTES
                and digest(raw) == OUTPUT_SHA256,
                "reject nonfrozen corrected source before workspace mutation")
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
                        "reject incomplete exclusive corrected bridge write")
                written += count
            metadata = self.native_fstat(descriptor)
            require(stat.S_ISREG(metadata.st_mode)
                    and stat.S_IMODE(metadata.st_mode) == 0o600
                    and metadata.st_dev == DEVICE and metadata.st_size == OUTPUT_BYTES
                    and metadata.st_nlink == 1 and metadata.st_uid == os.geteuid(),
                    "reject substituted exclusive corrected scanner bridge")
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
                    block = self.native_read(readback, min(remaining, 65536))
                    require(bool(block), "reject incomplete durable bridge readback")
                    chunks.append(block)
                    remaining -= len(block)
                require(self.native_read(readback, 1) == b""
                        and digest(b"".join(chunks)) == OUTPUT_SHA256,
                        "reject durable corrected scanner bridge readback digest")
            finally:
                self.close(readback)
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            self.close(parent)

    def install(self) -> None:
        require(not self.installed, "install immutable scanner source wall once")
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


def transform(source: bytes, exact: bool = False) -> bytes:
    require(type(source) is bytes, "derive correction from complete genuine C bytes")
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA256,
                "reject unauthenticated clean no-introspection scanner predecessor")
    require(source.count(ORIGINAL_SCANNER) == 1
            and source.count(CORRECTED_SCANNER) == 0
            and source.count(MATCH_FUNCTION) == 1,
            "require one complete scanner body and its unchanged match exemplar")
    for marker, expected in PRESERVED_MARKERS:
        require(source.count(marker) == expected,
                "reject missing or duplicated clean preserved first-party surface")
    for forbidden in (b'PyImport_ImportModule("inspect")',
                      b'PyImport_ImportModule("functools")',
                      b'PyImport_ImportModule("re")',
                      b'PyImport_ImportModule("regex")',
                      b"rust_iterator_signature", b"__text_signature__"):
        require(forbidden not in source,
                "reject external matcher, private introspection, or signature getter")
    corrected = source.replace(ORIGINAL_SCANNER, CORRECTED_SCANNER, 1)
    require(corrected.count(ORIGINAL_SCANNER) == 0
            and corrected.count(CORRECTED_SCANNER) == 1
            and corrected.count(MATCH_FUNCTION) == 1,
            "require one exact first-party scanner-only protocol correction")
    require(corrected.replace(CORRECTED_SCANNER, ORIGINAL_SCANNER, 1) == source,
            "reject unrelated bridge changes or nonreversible scanner replacement")
    for marker, expected in PRESERVED_MARKERS:
        expected_after = (expected + 1 if marker ==
                          b"return rust_owned_pickle_reconstruction((PyObject *)iterator);"
                          else expected)
        require(corrected.count(marker) == expected_after,
                "preserve matching, scanner API, descriptors, and safe capture clamp")
    require(len(corrected) - len(source)
            == len(CORRECTED_SCANNER) - len(ORIGINAL_SCANNER) == 202,
            "require exactly one reversible 202-byte scanner correction")
    if exact:
        require(len(corrected) == OUTPUT_BYTES and digest(corrected) == OUTPUT_SHA256,
                "reject nonfrozen complete immutable corrected bridge")
    return corrected


def synthetic_source() -> bytes:
    return b"\n".join((
        b"static PyObject *rust_owned_pickle_reconstruction(PyObject *value) {",
        b"    return value;\n}",
        MATCH_FUNCTION,
        b"static PyObject *rust_scanner_reduce(RustIterator *iterator, PyObject *ignored) {",
        b"    return rust_owned_pickle_reconstruction((PyObject *)iterator);\n}",
        ORIGINAL_SCANNER,
        b"static PyMethodDef rust_iterator_scanner_search_method = {\n};",
        b"size_t first = begin > capture.length ? capture.length : begin;",
        b"size_t finish = end > capture.length ? capture.length : end;",
        b"if (finish < first) finish = first;",
        b"PyDescr_NewMethod(",
        b'    .name = "_sre.SRE_Scanner",',
        b'{"__reduce_ex__", (PyCFunction)rust_scanner_reduce_ex, METH_O,',
    ))


class WitnessInt(int):
    """An int subclass accepted by the existing PyLong_AsInt convention."""


class WitnessIndex:
    def __init__(self, number: object) -> None:
        self.number = number

    def __index__(self) -> object:
        return self.number


class WitnessIndexFailure:
    def __init__(self, exception: Exception) -> None:
        self.exception = exception

    def __index__(self) -> int:
        raise self.exception


def owned_reconstruction() -> tuple:
    return ("copyreg._reconstructor", ("_sre.SRE_Scanner", "object", None))


def protocol_as_c_int(protocol: object) -> int:
    if isinstance(protocol, int):
        value = int.__index__(protocol)
    else:
        index = getattr(type(protocol), "__index__", None)
        if index is None:
            raise TypeError("'" + type(protocol).__name__
                            + "' object cannot be interpreted as an integer")
        value = index(protocol)
        if not isinstance(value, int):
            raise TypeError("__index__ returned non-int (type "
                            + type(value).__name__ + ")")
        value = int.__index__(value)
    if value < -(1 << 31) or value >= 1 << 31:
        raise OverflowError("Python int too large to convert to C int")
    return value


def corrected_reduce_model(protocol: object) -> tuple:
    number = protocol_as_c_int(protocol)
    if number < 2:
        return owned_reconstruction()
    raise TypeError("cannot pickle '_sre.SRE_Scanner' object")


def original_reduce_model(_protocol: object) -> tuple:
    raise TypeError("cannot pickle '_sre.SRE_Scanner' object")


def observe(call, protocol: object) -> tuple:
    try:
        value = call(protocol)
    except (TypeError, OverflowError, RuntimeError, ValueError) as error:
        return ("ERROR", type(error).__name__, str(error))
    require(value == owned_reconstruction(),
            "preserve existing copyreg reconstruction without adding delegation")
    return ("VALUE", value)


def public_rows() -> tuple[list[dict], list[dict]]:
    require(len(DATASETS) == 94 and len(set(DATASETS)) == 94,
            "require all distinct 94 authenticated public text and binary datasets")
    require(len(OVERLAP_DATASETS) == 3 and set(OVERLAP_DATASETS) <= set(DATASETS),
            "require exactly three known text named-Unicode-comment lexer overlaps")
    rows: list[dict] = []
    preserved: list[dict] = []
    for dataset in DATASETS:
        for operation, protocol, expected_class in TARGETED_OPERATIONS:
            before = observe(original_reduce_model, protocol)
            after = observe(corrected_reduce_model, protocol)
            require(before != after,
                    "require each of the five scanner public operations to change")
            if expected_class == "RECONSTRUCTION":
                require(after == ("VALUE", owned_reconstruction()),
                        "negative, zero, and one must reuse owned reconstruction")
            elif expected_class == "TYPE_ERROR":
                require(after[0:2] == ("ERROR", "TypeError")
                        and after[2] != before[2],
                        "string protocol must propagate PyLong_AsInt TypeError")
            else:
                require(after[0:2] == ("ERROR", "OverflowError"),
                        "oversized protocol must propagate PyLong_AsInt OverflowError")
            overlap = dataset in OVERLAP_DATASETS
            rows.append({"dataset": dataset, "operation": operation,
                         "expected_class": expected_class,
                         "named_unicode_comment_overlap": overlap,
                         "scanner_only_independent_improvement": not overlap})
        for operation, protocol in PRESERVED_OPERATIONS:
            before = observe(original_reduce_model, protocol)
            after = observe(corrected_reduce_model, protocol)
            require(before == after == ("ERROR", "TypeError",
                                        "cannot pickle '_sre.SRE_Scanner' object"),
                    "protocols two and five must preserve exact cannot-pickle errors")
            preserved.append({"dataset": dataset, "operation": operation,
                              "preexisting_comment_compile_failure":
                              dataset in OVERLAP_DATASETS,
                              "scanner_behavior_changed": False})
    require(len(rows) == 470 and len(preserved) == 188,
            "require complete five-by-94 target and two-by-94 preserved matrix")
    require(sum(row["named_unicode_comment_overlap"] for row in rows) == 15
            and sum(row["scanner_only_independent_improvement"]
                    for row in rows) == 455
            and sum(row["preexisting_comment_compile_failure"]
                    for row in preserved) == 6,
            "account for 470 gross, 15 lexer overlaps, and 455 independent rows")
    return rows, preserved


def protocol_variations() -> list[dict]:
    cases = (
        ("negative-one-sentinel-without-error", -1, "VALUE"),
        ("negative-two", -2, "VALUE"),
        ("minimum-c-int", -(1 << 31), "VALUE"),
        ("zero", 0, "VALUE"),
        ("one", 1, "VALUE"),
        ("bool-false", False, "VALUE"),
        ("bool-true", True, "VALUE"),
        ("int-subclass-negative-one", WitnessInt(-1), "VALUE"),
        ("int-subclass-one", WitnessInt(1), "VALUE"),
        ("index-negative-one", WitnessIndex(-1), "VALUE"),
        ("index-one", WitnessIndex(1), "VALUE"),
        ("two", 2, "TypeError"),
        ("five", 5, "TypeError"),
        ("maximum-c-int", (1 << 31) - 1, "TypeError"),
        ("bool-compatible-int-subclass-two", WitnessInt(2), "TypeError"),
        ("index-two", WitnessIndex(2), "TypeError"),
        ("string", "0", "TypeError"),
        ("bytes", b"0", "TypeError"),
        ("none", None, "TypeError"),
        ("float", 1.0, "TypeError"),
        ("bad-index-result", WitnessIndex("1"), "TypeError"),
        ("positive-c-int-overflow", 1 << 31, "OverflowError"),
        ("negative-c-int-overflow", -(1 << 31) - 1, "OverflowError"),
        ("public-overflow", 1 << 40, "OverflowError"),
        ("negative-large-overflow", -(1 << 40), "OverflowError"),
        ("index-overflow", WitnessIndex(1 << 40), "OverflowError"),
        ("index-type-error", WitnessIndexFailure(TypeError("index refused")),
         "TypeError"),
        ("index-overflow-error", WitnessIndexFailure(OverflowError("index huge")),
         "OverflowError"),
        ("index-runtime-error", WitnessIndexFailure(RuntimeError("index exploded")),
         "RuntimeError"),
    )
    rows: list[dict] = []
    for name, protocol, expected in cases:
        observed = observe(corrected_reduce_model, protocol)
        if expected == "VALUE":
            require(observed == ("VALUE", owned_reconstruction()),
                    "negative and low protocols must use owned reconstruction")
        else:
            require(observed[0:2] == ("ERROR", expected),
                    "PyLong_AsInt must propagate the exact protocol exception class")
        rows.append({"case": name, "expected_class": expected,
                     "observed_class": observed[0] if expected == "VALUE"
                     else observed[1]})
    require(len(rows) == 29, "require all boundary, bool, subclass, and failure controls")
    return rows


def synthetic_tests(wall: SourceWall) -> dict:
    source = synthetic_source()
    corrected = transform(source)
    records, preserved = public_rows()
    variations = protocol_variations()
    rejected = 0

    def reject(call, reason: str) -> None:
        nonlocal rejected
        try:
            call()
        except (FreezeError, OSError, TypeError, ValueError, OverflowError):
            rejected += 1
            return
        raise FreezeError("hostile scanner source-only control unexpectedly passed: "
                          + reason)

    reject(lambda: transform(source.replace(ORIGINAL_SCANNER, b"", 1)),
           "missing complete scanner reduce_ex definition")
    reject(lambda: transform(source.replace(ORIGINAL_SCANNER,
                                            ORIGINAL_SCANNER * 2, 1)),
           "duplicate scanner reduce_ex definition")
    reject(lambda: transform(source.replace(MATCH_FUNCTION, b"", 1)),
           "missing complete existing match reduce_ex exemplar")
    reject(lambda: transform(source.replace(MATCH_FUNCTION, MATCH_FUNCTION * 2, 1)),
           "duplicated match reduce_ex exemplar")
    reject(lambda: transform(source.replace(b"    (void)protocol;\n",
                                            b"    (void)iterator;\n", 1)),
           "substituted original scanner protocol function")
    for marker, _count in PRESERVED_MARKERS:
        reject(lambda item=marker: transform(source.replace(item, b"", 1)),
               "missing unchanged capture clamp, helper, descriptor, or scanner API")
    for index in range(0, len(ORIGINAL_SCANNER), 17):
        altered = (ORIGINAL_SCANNER[:index]
                   + bytes((ORIGINAL_SCANNER[index] ^ 1,))
                   + ORIGINAL_SCANNER[index + 1:])
        reject(lambda replacement=altered:
               transform(source.replace(ORIGINAL_SCANNER, replacement, 1)),
               "mutated complete original scanner reduce_ex bytes")
    for forbidden in (b'PyImport_ImportModule("inspect")',
                      b'PyImport_ImportModule("functools")',
                      b'PyImport_ImportModule("re")',
                      b'PyImport_ImportModule("regex")',
                      b"rust_iterator_signature", b"__text_signature__"):
        reject(lambda item=forbidden: transform(source + b"\n" + item),
               "private introspection or external matcher")
    for payload in (b'{"x":1,"x":2}', b"NaN", b"Infinity", b"1.",
                    b"1e+", b"1e999999", b"01", b'{"x":"\\ud800"}',
                    b'{"x":1} trailing'):
        reject(lambda raw=payload: StrictJSON(raw).decode(), "unsafe evidence JSON")

    reject(lambda: wall.parent(INPUT), "candidate bridge source")
    reject(lambda: wall.parent(TARGET), "candidate variant target")
    reject(lambda: wall.parent("candidates/rust/target/release/candidate.so"),
           "native candidate artifact")
    reject(lambda: wall.parent("oracle/phase3/expanded-sealed-holdout-v2.json"),
           "invalidated proposal")
    reject(lambda: wall.parent("oracle/phase3/final-sealed-holdout-v3.json"),
           "final holdout artifact")
    reject(lambda: wall.parent(ORIGINAL_RECEIPT[:-5] + ".json.gz"),
           "compressed original failure archive")
    reject(lambda: wall.parent(
        "experiments/rust_native_architecture_public_v2/v26-anchor-public-run-001/"
        "public-10434-correctness.raw.json"), "raw public comparison artifact")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved primitive unticketed candidate source")
    reject(lambda: wall.native_open(ROOT + "/candidate.so", wall.file_flags()),
           "saved primitive native candidate")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level candidate source")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "direct candidate source open")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "candidate variant creation")
    reject(lambda: time.time(), "wall-clock sample")
    reject(lambda: time.perf_counter(), "performance clock")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native library load")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None),
           "compiler or worker subprocess")
    reject(lambda: sys.audit("socket.connect", None, None), "network connection")
    require(rejected >= 50 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "require exhaustive hostile controls with zero candidate reads and writes")
    no_matching_imports()
    return {
        "synthetic_source_bytes": len(source),
        "synthetic_output_bytes": len(corrected),
        "source_delta_bytes": 202,
        "dataset_count": 94,
        "targeted_operation_count": 5,
        "gross_targeted_public_mismatch_count": len(records),
        "targeted_public_rows_sha256": digest(canonical(records).encode("utf-8")),
        "named_unicode_comment_overlap_dataset_count": 3,
        "named_unicode_comment_overlap_row_count": 15,
        "scanner_only_independent_public_improvement_count": 455,
        "preserved_high_protocol_row_count": len(preserved),
        "preserved_high_protocol_comment_compile_failure_count": 6,
        "preserved_high_protocol_rows_sha256":
            digest(canonical(preserved).encode("utf-8")),
        "protocol_variation_count": len(variations),
        "protocol_variations_sha256": digest(canonical(variations).encode("utf-8")),
        "negative_one_without_error_is_valid": True,
        "bool_and_int_subclasses_supported": True,
        "protocol_type_and_overflow_errors_propagated": True,
        "protocol_two_and_five_unchanged": True,
        "capture_clamp_preserved": True,
        "no_external_introspection_preserved": True,
        "hostile_controls_rejected": rejected,
        "candidate_source_reads": 0,
        "raw_public_comparison_artifacts_opened": 0,
        "compressed_archives_opened": 0,
        "native_libraries_loaded": 0,
        "clock_samples": 0,
        "workspace_mutations": 0,
        "candidate_correctness": "NOT MEASURED",
        "final_holdout": FINAL_HOLDOUT,
    }


def value(document: object, key: str, expected: object) -> None:
    require(type(document) is dict and document.get(key) == expected,
            "reject incomplete or substituted authenticated evidence: " + key)


def authenticate_original(raw: bytes) -> dict:
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
            ("infrastructure_failure_count", 0),
            ("named_private_waiver_count", 13), ("holdout", "NOT OPENED"),
            ("hidden_cases_read", 0), ("clock_samples", 0),
            ("actual_v25_build_archive_read_count", 0),
            ("actual_v25_build_archive_gzip_inflation_count", 0),
            ("winner_selected", False)):
        value(document, key, expected)
    suites = document.get("suite_integrity")
    require(type(suites) is list and len(suites) == 13,
            "require complete thirteen-suite original failure ledger")
    indexed: dict[str, dict] = {}
    for suite in suites:
        require(type(suite) is dict and type(suite.get("suite")) is str,
                "reject malformed original suite ledger row")
        name = suite["suite"]
        require(name not in indexed, "reject duplicate original suite ledger row")
        indexed[name] = suite
        value(suite, "fully_observed", True)
        value(suite, "actual_worker_started", True)
    for name, denominator, mismatches in (
            ("substitution_v2", 5120, 240), ("shape_v2", 10240, 1112)):
        suite = indexed[name]
        value(suite, "case_execution_denominator", denominator)
        value(suite, "mismatch_count", mismatches)
        value(suite, "verified_passing_case_count", 0)
        value(suite, "failure_class", "SEMANTIC MISMATCH")
    require(sum(item["case_execution_denominator"] for item in suites) == 31237
            and sum(item["mismatch_count"] for item in suites) == 1352
            and sum(item["verified_passing_case_count"] for item in suites) == 15877,
            "preserve complete authentic original denominator and failure profile")
    archive = document.get("archive")
    require(type(archive) is dict,
            "authenticate archive identity from receipt without opening archive")
    value(archive, "sha256",
          "dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7")
    value(archive, "size_bytes", 3771743)
    value(archive, "inode", 524845)
    return {"receipt_path": ORIGINAL_RECEIPT,
            "receipt_sha256": OWNERS[0][2],
            "publication_status": "PASS", "candidate_status": "FAIL",
            "suite_count": 13, "case_execution_denominator": 31237,
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "substitution_v2_mismatch_count": 240,
            "shape_v2_mismatch_count": 1112,
            "compressed_archive_open_count": 0}


def authenticate_predecessor(raw: bytes) -> dict:
    document = StrictJSON(raw).decode()
    for key, expected in (
            ("schema", SCHEMA.replace("scanner-pickle-semantics",
                                     "no-external-introspection")
                       + "-root-materialization"),
            ("status", "PASS; EXACT PRIVATE INTROSPECTION REMOVED; "
                       "NOT BUILT; NOT RUN"),
            ("target_path", INPUT), ("target_sha256", INPUT_SHA256),
            ("target_bytes", INPUT_BYTES), ("capture_clamp_preserved", True),
            ("public_native_descriptors_preserved", True)):
        value(document, key, expected)
    effects = document.get("effects")
    require(type(effects) is dict, "require complete no-introspection source receipt")
    for key, expected in (("candidate_source_files_read", 1),
                          ("candidate_executions", 0), ("candidate_imports", 0),
                          ("native_binary_files_opened", 0),
                          ("compressed_archives_opened", 0),
                          ("holdout_cases_opened", 0), ("clock_samples", 0),
                          ("workspace_mutations", 2)):
        value(effects, key, expected)
    return {"receipt_path": NO_INTROSPECTION_RECEIPT,
            "receipt_sha256": OWNERS[1][2], "input_path": INPUT,
            "input_sha256": INPUT_SHA256, "input_bytes": INPUT_BYTES,
            "capture_clamp_preserved": True,
            "private_external_introspection_removed": True,
            "candidate_source_opened_for_this_source_freeze": False}


def authenticate_public(raw: bytes, architecture: str) -> dict:
    document = StrictJSON(raw).decode()
    for key, expected in (
            ("schema", "rebar-owned-rust-native-architecture-public-gate-v2-"
                       "durable-publication-receipt"),
            ("status", "PASS"), ("architecture", architecture),
            ("public_10434_case_count", 10434),
            ("public_10434_mismatch_count", 1145),
            ("public_10434_correctness_status", "FAIL"),
            ("hidden_cases_read", 0),
            ("controller_final_holdout_content_open_count", 0),
            ("candidate_qualified", False), ("winner_selected", False),
            ("bridge_sha256",
             "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4"),
            ("retired_v2_proposal_status",
             "COMPROMISED; RETIRED; NOT ACCESSED BY THIS CONTROLLER"),
            ("final_holdout_case_status",
             "NOT GENERATED; REKEYED SUCCESSOR REQUIRED")):
        value(document, key, expected)
    artifacts = document.get("artifacts")
    require(type(artifacts) is list and len(artifacts) == 18,
            "require complete immutable public comparison artifact receipt inventory")
    suffix = "/public-10434-correctness.raw.json"
    comparisons = [item for item in artifacts
                   if type(item) is dict and type(item.get("path")) is str
                   and item["path"].endswith(suffix)]
    require(len(comparisons) == 1,
            "require exactly one raw comparison identified by plaintext receipt only")
    comparison = comparisons[0]
    for key, expected in (("sha256", RAW_COMPARISON_SHA256),
                          ("bytes", RAW_COMPARISON_BYTES), ("device", DEVICE),
                          ("mode", "0600")):
        value(comparison, key, expected)
    expected_inode = 525295 if architecture == "v26" else 525408
    value(comparison, "inode", expected_inode)
    require("/" + architecture + "-" in comparison["path"],
            "reject substituted architecture-specific raw comparison receipt row")
    return {"architecture": architecture,
            "receipt_path": PUBLIC_V26_RECEIPT if architecture == "v26"
            else PUBLIC_V27_RECEIPT,
            "receipt_sha256": OWNERS[2][2] if architecture == "v26"
            else OWNERS[3][2],
            "public_case_count": 10434, "public_mismatch_count": 1145,
            "raw_comparison_sha256_receipt_only": RAW_COMPARISON_SHA256,
            "raw_comparison_bytes_receipt_only": RAW_COMPARISON_BYTES,
            "raw_comparison_open_count": 0,
            "gross_scanner_pickle_mismatch_count": 470,
            "named_unicode_comment_overlap_count": 15,
            "scanner_only_independent_improvement_count": 455}


def authenticate_dataset_source(raw: bytes) -> dict:
    marker = b"def public_datasets() -> tuple["
    require(raw.count(marker) == 1,
            "require exactly one immutable public dataset producer function")
    start = raw.index(marker)
    end = raw.index(b"\ndef ", start + len(marker))
    fragment = raw[start:end]
    discovered: list[str] = []
    for line in fragment.splitlines():
        if line.startswith((b'        ("text.', b'        ("bytes.')):
            beginning = line.index(b'"') + 1
            ending = line.index(b'"', beginning)
            discovered.append(line[beginning:ending].decode("ascii"))
    require(tuple(discovered) == DATASETS,
            "require all 94 frozen public dataset identifiers in producer order")
    operation_start = raw.index(b"OPERATIONS = (\n")
    operation_end = raw.index(b"\n)\n", operation_start)
    operations = raw[operation_start:operation_end]
    for operation, _protocol, _expected in TARGETED_OPERATIONS:
        require(operations.count(('    "' + operation + '",').encode("ascii")) == 1,
                "require each targeted operation in the frozen public matrix")
    for operation, _protocol in PRESERVED_OPERATIONS:
        require(operations.count(('    "' + operation + '",').encode("ascii")) == 1,
                "require unchanged protocol-two and protocol-five public operations")
    return {"path": PUBLIC_DATASET_SOURCE, "sha256": OWNERS[4][2],
            "dataset_count": len(discovered),
            "dataset_identifiers_sha256":
                digest(canonical(discovered).encode("utf-8")),
            "targeted_operation_count": len(TARGETED_OPERATIONS),
            "preserved_high_protocol_operation_count": len(PRESERVED_OPERATIONS),
            "producer_imported_or_executed": False}


def validate_contract(document: object, source_sha: str, protocol_sha: str) -> None:
    require(type(document) is dict, "require complete immutable scanner contract")
    for key, expected in (("schema", SCHEMA), ("version", 1), ("family", "rust"),
                          ("phase", "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS"),
                          ("status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; "
                                     "NOT BUILT; NOT RUN"),
                          ("source", {"path": SOURCE, "sha256": source_sha}),
                          ("protocol", {"path": PROTOCOL, "sha256": protocol_sha})):
        value(document, key, expected)
    correction = document.get("exact_scanner_pickle_correction")
    for key, expected in (
            ("input_path", INPUT), ("input_sha256", INPUT_SHA256),
            ("input_bytes", INPUT_BYTES), ("input_device", DEVICE),
            ("input_inode", INPUT_INODE), ("input_mode", "0600"),
            ("target_path", TARGET), ("target_sha256", OUTPUT_SHA256),
            ("target_bytes", OUTPUT_BYTES), ("source_delta_bytes", 202),
            ("changed_function", "rust_scanner_reduce_ex"),
            ("replacement_site_count", 1),
            ("protocol_parser", "PyLong_AsInt"),
            ("negative_one_without_error_is_valid", True),
            ("type_error_propagated", True), ("overflow_error_propagated", True),
            ("low_protocol_threshold", 2),
            ("existing_reconstructor", "rust_owned_pickle_reconstruction"),
            ("protocol_two_and_five_unchanged", True),
            ("match_reduce_ex_byte_identical", True),
            ("capture_clamp_correction_retained", True),
            ("no_external_introspection_correction_retained", True),
            ("stdlib_matching_delegation_added", False),
            ("external_regex_dependency_added", False),
            ("candidate_built", False), ("candidate_imported", False),
            ("candidate_matching", "NOT RUN"), ("candidate_qualified", False)):
        value(correction, key, expected)
    target = document.get("exact_targeted_public_partition")
    for key, expected in (
            ("dataset_count", 94), ("targeted_operation_count", 5),
            ("gross_targeted_public_mismatch_count", 470),
            ("targeted_operations", [row[0] for row in TARGETED_OPERATIONS]),
            ("named_unicode_comment_overlap_dataset_count", 3),
            ("named_unicode_comment_overlap_datasets", list(OVERLAP_DATASETS)),
            ("named_unicode_comment_overlap_row_count", 15),
            ("scanner_only_independent_public_improvement_count", 455),
            ("preserved_high_protocol_operations",
             [row[0] for row in PRESERVED_OPERATIONS]),
            ("preserved_high_protocol_row_count", 188),
            ("preserved_high_protocol_comment_compile_failure_count", 6),
            ("independent_effect_measured", False),
            ("candidate_correctness", "NOT MEASURED")):
        value(target, key, expected)
    original = document.get("immutable_original_v25_ledger")
    for key, expected in (("receipt_path", ORIGINAL_RECEIPT),
                          ("receipt_sha256", OWNERS[0][2]),
                          ("receipt_bytes", 11832), ("receipt_device", DEVICE),
                          ("receipt_inode", 524846),
                          ("publication_status", "PASS"),
                          ("candidate_status", "FAIL"), ("suite_count", 13),
                          ("case_execution_denominator", 31237),
                          ("semantic_mismatch_count", 1352),
                          ("verified_passing_case_count", 15877),
                          ("substitution_v2_mismatch_count", 240),
                          ("shape_v2_mismatch_count", 1112)):
        value(original, key, expected)
    predecessor = document.get("immutable_no_introspection_predecessor")
    for key, expected in (("receipt_path", NO_INTROSPECTION_RECEIPT),
                          ("receipt_sha256", OWNERS[1][2]),
                          ("receipt_bytes", 1774), ("receipt_device", DEVICE),
                          ("receipt_inode", 524813), ("target_path", INPUT),
                          ("target_sha256", INPUT_SHA256),
                          ("target_bytes", INPUT_BYTES),
                          ("capture_clamp_preserved", True),
                          ("private_external_introspection_removed", True)):
        value(predecessor, key, expected)
    public = document.get("immutable_public_v26_v27_comparison_receipts")
    for key, expected in (
            ("v26_receipt_path", PUBLIC_V26_RECEIPT),
            ("v26_receipt_sha256", OWNERS[2][2]), ("v26_receipt_bytes", 40906),
            ("v26_receipt_inode", 525333),
            ("v27_receipt_path", PUBLIC_V27_RECEIPT),
            ("v27_receipt_sha256", OWNERS[3][2]), ("v27_receipt_bytes", 68330),
            ("v27_receipt_inode", 525426),
            ("comparison_sha256_receipt_only", RAW_COMPARISON_SHA256),
            ("comparison_bytes_receipt_only", RAW_COMPARISON_BYTES),
            ("public_case_count", 10434), ("public_mismatch_count", 1145),
            ("identical_public_comparison_digest", True),
            ("raw_comparison_artifacts_opened", 0),
            ("public_dataset_source_path", PUBLIC_DATASET_SOURCE),
            ("public_dataset_source_sha256", OWNERS[4][2]),
            ("public_dataset_source_bytes", 112729),
            ("public_dataset_source_inode", 429259)):
        value(public, key, expected)
    wall = document.get("physical_source_wall")
    for key, expected in (("installed_before_owner_reads", True),
                          ("descriptor_relative_o_nofollow", True),
                          ("authenticated_public_evidence_receipt_count", 4),
                          ("authenticated_public_dataset_source_count", 1),
                          ("source_mode_candidate_source_reads", 0),
                          ("self_test_candidate_source_reads", 0),
                          ("raw_public_comparison_artifacts_opened", 0),
                          ("source_mode_filesystem_writes", 0),
                          ("self_test_filesystem_writes", 0),
                          ("apply_requires_explicit_root_authorization", True),
                          ("apply_requires_frozen_commit_equals_pushed_commit", True),
                          ("apply_candidate_source_read_count", 1),
                          ("apply_exclusive_new_target_only", True),
                          ("candidate_execution_allowed", False),
                          ("compiler_launch_allowed", False),
                          ("native_binary_open_allowed", False),
                          ("compressed_archive_open_allowed", False),
                          ("proposal_open_allowed", False),
                          ("final_holdout_open_allowed", False),
                          ("clock_access_allowed", False)):
        value(wall, key, expected)
    effects = document.get("source_only_effects")
    for key in ("candidate_source_files_read", "candidate_executions",
                "candidate_imports", "candidate_workers_started",
                "compiler_processes_started", "native_binary_files_opened",
                "native_libraries_loaded", "raw_public_comparison_artifacts_opened",
                "compressed_archives_opened", "compressed_archives_inflated",
                "proposal_files_opened", "holdout_cases_opened",
                "holdout_cases_generated", "clock_samples", "network_requests",
                "workspace_mutations"):
        value(effects, key, 0)
    for key, expected in (("runtime_non_delegation", "NOT ESTABLISHED"),
                          ("candidate_correctness", "NOT MEASURED"),
                          ("candidate_matching", "NOT RUN"),
                          ("final_holdout", FINAL_HOLDOUT),
                          ("performance", "NOT MEASURED"),
                          ("winner_selected", False)):
        value(effects, key, expected)


def parse_arguments(arguments: list[str]) -> dict:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require explicit immutable scanner command arguments")
    flags = {"--self-test", "--verify-source", "--apply", "--root-authorized"}
    options = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
               "--frozen-commit", "--pushed-commit"}
    parsed: dict[str, object] = {}
    index = 0
    while index < len(arguments):
        item = arguments[index]
        require(item in flags or item in options, "reject unknown option: " + item)
        require(item not in parsed, "reject duplicate option: " + item)
        if item in flags:
            parsed[item] = True
            index += 1
        else:
            require(index + 1 < len(arguments), "require complete option: " + item)
            parsed[item] = arguments[index + 1]
            index += 2
    modes = tuple(item for item in ("--self-test", "--verify-source", "--apply")
                  if parsed.get(item) is True)
    require(len(modes) == 1,
            "require exactly one self-test, source verification, or root-only apply")
    mode = modes[0]
    if mode == "--self-test":
        require(set(parsed) == {mode}, "self-test accepts no owner or root arguments")
    elif mode == "--verify-source":
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256"},
                "source verification requires exactly the frozen owner digest triple")
    else:
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256", "--root-authorized",
                                "--frozen-commit", "--pushed-commit"},
                "root-only apply requires explicit authorization and pushed commit")
        for option in ("--frozen-commit", "--pushed-commit"):
            commit = parsed[option]
            require(type(commit) is str and len(commit) == 40
                    and all(char in "0123456789abcdef" for char in commit),
                    "require complete lowercase frozen commit: " + option)
        require(parsed["--frozen-commit"] == parsed["--pushed-commit"],
                "refuse root materialization before frozen commit has been pushed")
    for option in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if option in parsed:
            checked_sha(parsed[option], option)
    return parsed


def zero_effects(wall: SourceWall, mode: str) -> dict:
    return {"mode": mode, "approved_public_owner_reads": wall.public_reads,
            "candidate_source_files_read": wall.source_reads,
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_workers_started": 0, "compiler_processes_started": 0,
            "native_binary_files_opened": 0, "native_libraries_loaded": 0,
            "raw_public_comparison_artifacts_opened": 0,
            "compressed_archives_opened": 0, "compressed_archives_inflated": 0,
            "proposal_files_opened": 0, "holdout_cases_opened": 0,
            "holdout_cases_generated": 0, "clock_samples": 0,
            "network_requests": 0, "workspace_mutations": wall.workspace_mutations,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_correctness": "NOT MEASURED",
            "candidate_matching": "NOT RUN", "candidate_qualified": False,
            "final_holdout": FINAL_HOLDOUT, "performance": "NOT MEASURED",
            "winner_selected": False}


def main(arguments: list[str]) -> dict:
    options = parse_arguments(arguments)
    apply = options.get("--apply") is True
    wall = SourceWall(apply)
    no_matching_imports()
    wall.install()
    if options.get("--self-test") is True:
        controls = synthetic_tests(wall)
        require(wall.public_reads == 0 and wall.source_reads == 0
                and wall.workspace_mutations == 0 and wall.root is None,
                "self-test must read no owners, candidates, raw cases, or archives")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "synthetic_controls": controls,
                "effects": zero_effects(wall, "SELF-TEST")}

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
    for role, path, owner_sha, count, inode in OWNERS:
        require(not path.startswith(("candidates/", "experiments/"))
                and not path.endswith((".gz", ".so")),
                "public frozen owners must exclude candidates, raw files, and archives")
        frozen[role] = wall.read(path, count, inode, owner_sha)
    original = authenticate_original(frozen["original_v25_receipt"])
    predecessor = authenticate_predecessor(frozen["no_introspection_receipt"])
    public_v26 = authenticate_public(frozen["public_v26_receipt"], "v26")
    public_v27 = authenticate_public(frozen["public_v27_receipt"], "v27")
    producer = authenticate_dataset_source(frozen["public_dataset_source"])
    require(public_v26["raw_comparison_sha256_receipt_only"]
            == public_v27["raw_comparison_sha256_receipt_only"]
            == RAW_COMPARISON_SHA256,
            "require identical immutable V26/V27 public comparison receipt digests")
    require(wall.public_reads == len(OWNERS) + 3 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "authenticate only frozen source owners and public plaintext evidence")
    if not apply:
        controls = synthetic_tests(wall)
        no_matching_imports()
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; SOURCE FROZEN; NO CANDIDATE SOURCE READ",
                "source_sha256": source_sha, "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "authenticated_original_ledger": original,
                "authenticated_no_introspection_predecessor": predecessor,
                "authenticated_public_v26": public_v26,
                "authenticated_public_v27": public_v27,
                "authenticated_public_dataset_producer": producer,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "synthetic_controls": controls,
                "effects": zero_effects(wall, "SOURCE FREEZE")}

    require(transform(synthetic_source()) and wall.source_reads == 0,
            "require complete source-only scanner proof before root-only bridge access")
    predecessor_source = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA256)
    corrected = transform(predecessor_source, exact=True)
    wall.materialize(corrected)
    no_matching_imports()
    require(wall.source_reads == 1 and wall.workspace_mutations == 2,
            "create only one exclusive variant directory and one immutable C bridge")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; EXACT SCANNER PICKLE CORRECTION; NOT BUILT; NOT RUN",
            "frozen_commit": options["--frozen-commit"],
            "pushed_commit": options["--pushed-commit"],
            "source_sha256": source_sha, "protocol_sha256": protocol_sha,
            "contract_sha256": contract_sha, "input_path": INPUT,
            "input_sha256": INPUT_SHA256, "input_bytes": INPUT_BYTES,
            "target_path": TARGET, "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES, "source_delta_bytes": 202,
            "gross_targeted_public_mismatch_count": 470,
            "named_unicode_comment_overlap_row_count": 15,
            "scanner_only_independent_public_improvement_count": 455,
            "candidate_correctness": "NOT MEASURED",
            "effects": zero_effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError) as error:
        sys.stderr.write("rust-scanner-pickle-semantics-v1: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
