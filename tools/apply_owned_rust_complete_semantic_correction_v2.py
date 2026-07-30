#!/usr/bin/env python3
"""Freeze the composed first-party Rust correction for all known V25 failures.

Source modes authenticate immutable public plaintext owners only and never open
a candidate, native object, archive, final holdout, Git state, clock, or timer.
Separately authorized root application reads the already materialized expansion
successor exactly once and exclusively creates one complete corrected bridge.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("complete semantic freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
DEVICE = 2064
SCHEMA = "rebar-owned-rust-complete-semantic-correction-v2-source-freeze"
SOURCE = "tools/apply_owned_rust_complete_semantic_correction_v2.py"
PROTOCOL = "oracle/phase2/RUST-COMPLETE-SEMANTIC-CORRECTION-V2.md"
CONTRACT = "oracle/phase2/rust-complete-semantic-correction-v2.json"
INPUT = "candidates/rust/variants/expand_probe_semantics_v1/py_bridge.c"
INPUT_SHA256 = "d0f0422a08592390619138d072cb831d6d446f38e2b67750798a221e7693d822"
INPUT_BYTES = 178081
INPUT_INODE = 525501
TARGET_DIRECTORY = "candidates/rust/variants/complete_semantic_correction_v2"
TARGET = TARGET_DIRECTORY + "/py_bridge.c"
OUTPUT_SHA256 = "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55"
OUTPUT_BYTES = 178270
FINAL_HOLDOUT = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 250_000
MAX_JSON_DEPTH = 80
TRAILING_ESCAPE = "bad escape (end of pattern)"
MALFORMED_NAMED_TEMPLATES = ("<\\g<word>:\\g<", "<\\g<word>:\\g<number")
SIMPLE = 0
FULL_READONLY = 284

# role, exact public plaintext pathname, SHA-256, bytes, device-2064 inode.
# The candidate INPUT and all archives/native/final/Git paths are absent.
OWNERS = (
    ("expand_source", "tools/apply_owned_rust_expand_probe_semantics_v1.py",
     "849a38fed6508b4e69ca049e46e932be65a98cbc49c0c3096e5edaf55ae75957",
     65552, 430793),
    ("expand_protocol", "oracle/phase2/RUST-EXPAND-PROBE-SEMANTICS-V1.md",
     "e9eecf30afff954bfa1ceee79bef551f0cd31215de24e0d55a9f704adde559bf",
     6545, 525224),
    ("expand_contract", "oracle/phase2/rust-expand-probe-semantics-v1.json",
     "e739146385553032f6f5705b4b43f230f4fe72070a0d4f636b86bbb66e4c1e14",
     5270, 525225),
    ("expand_application",
     "oracle/phase2/evidence/rust-expand-probe-semantics-v1-application.json",
     "9eaff0631cb6aed1e8231d8dc9e1a346d2efb1cab88cb5b5cd686689f5a092b1",
     1720, 525502),
    ("order_source", "tools/apply_owned_rust_substitution_event_order_v2.py",
     "50489f3ce64e254364ab416c132045c1bdcafed8bf5393efc6afb4727323658e",
     88530, 430898),
    ("order_protocol", "oracle/phase2/RUST-SUBSTITUTION-EVENT-ORDER-V2.md",
     "d1c30f4bf11682a09ed7a67d368585daf51168079cdbb22816f19889bd8d8cae",
     11616, 525503),
    ("order_contract", "oracle/phase2/rust-substitution-event-order-v2.json",
     "de964c871ce364dce87e88fb97e151d0e8307199a50e24b35a8cbb4830fd7d00",
     9407, 525522),
    ("order_application",
     "oracle/phase2/evidence/rust-substitution-event-order-v2-application.json",
     "51d783da90847820cff44fe0cdaf329200e35948798c34aa2fe9d371c7ca2fac",
     2199, 525554),
    ("v25_complete_failure_receipt",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v25-rust-capture-clamp-v1-root-provenance-"
     "original-p0-v25-failures-publication-receipt.json",
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59",
     11832, 524846),
    ("v1_source", "tools/apply_owned_rust_complete_semantic_correction_v1.py",
     "15dc2a9836a0e75323935508efdf8d8af7414ea1e074e26a94bf7bb688f25627",
     85883, 431405),
    ("v1_protocol", "oracle/phase2/RUST-COMPLETE-SEMANTIC-CORRECTION-V1.md",
     "0e13cd5553dbae90abcfd732cda1e97e3ad2f4c2efa7e5e192304470053fe99b",
     9023, 525840),
    ("v1_contract", "oracle/phase2/rust-complete-semantic-correction-v1.json",
     "09e5847ff7139f8f6cbfef3abbc769b01f899cdc3b5259ef64c67fd74ebd6f25",
     6634, 525841),
    ("v1_preapplication_failure",
     "oracle/phase2/evidence/rust-complete-semantic-correction-v1-"
     "preapplication-failure.json",
     "150e269c74f2f60b6fd188e5794d13a014b8e059cce91fa01ad59b2829b3f1c1",
     883, 525938),
)

CORE_START = (
    b"static PyObject *rust_substitute_core(PyObject *pattern, void *handle, "
    b"PyObject *groupindex, PyObject *pattern_value, PyObject *templates, "
    b"size_t groups, PyObject *replacement, PyObject *value, "
    b"Py_ssize_t limit, int want_count) {\n"
)
CORE_END = b"\nstatic PyObject *rust_bound_substitute("
CACHE_START = b"static int rust_replacement_cache("
EXPAND_FORWARD = b"static PyObject *rust_match_expand(RustMatch *match, PyObject *template);"
EXPAND_START = b"static PyObject *rust_match_expand(RustMatch *match, PyObject *template) {"
CAPTURE_START = b"static int rust_output_capture(\n"
CLAMP_FIRST = b"size_t first = begin > capture.length ? capture.length : begin;"
CLAMP_FINISH = b"size_t finish = end > capture.length ? capture.length : end;"
FULL_FLAG = b"materialization_flags = PyBUF_FULL_RO;"
CACHED_TEMPLATE = b'PyObject_CallMethod(pattern, "_cached_template", "OOn", normalized, subject, length)'
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
    """Reject incorrect lineage, effects, events, source bytes, or authorization."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete genuine bytes only")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require complete lowercase SHA-256: " + name)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "require genuine JSON text")
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
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject nontext JSON key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported or nonfinite JSON value")


class StrictJSON:
    """Bounded, duplicate-rejecting JSON parser that never imports json/re."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require bounded complete strict JSON bytes")
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

    def number(self) -> int:
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
        require(self.index - start <= 128, "reject oversized evidence integer")
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                "reject floating or nonfinite evidence")
        return int(self.text[start:self.index])

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
                require(self.items <= MAX_JSON_ITEMS, "reject oversized evidence")
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
            values: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return values
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON array")
                values.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return values
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
        require(self.index == len(self.text), "reject trailing JSON evidence bytes")
        return result


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "rebar", "subprocess", "socket",
                 "threading", "multiprocessing", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matcher, candidate, native loader, worker, or network import")


class SourceWall:
    """Deny-default descriptor-relative owners and one root-only exclusive writer."""

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
        raise FreezeError("complete semantic source wall rejected " + reason)

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            flags = args[2] if len(args) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed-candidate-native-archive-holdout-git-or-write-open")
        if event == "os.mkdir":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
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
        def reject(*_args: object, **_kwargs: object) -> object:
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
                "authorize sole candidate input only after complete source-only controls")
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
                        "candidate source may be read once only during root apply")
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
                "authorize exactly one root-only complete corrected C bridge")
        require(type(raw) is bytes and len(raw) == OUTPUT_BYTES
                and digest(raw) == OUTPUT_SHA256,
                "reject non-frozen complete corrected bridge before workspace mutation")
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
                    "reject substituted exclusive corrected bridge")
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
                        "reject durable complete corrected bridge digest")
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
            "require exactly one owned substitution core and following boundary")
    start = source.index(CORE_START)
    finish = source.index(CORE_END, start + len(CORE_START))
    return source[:start], source[start:finish], source[finish:]


def preserved_source(source: bytes) -> None:
    anchors = (
        (CACHE_START, 1), (EXPAND_FORWARD, 1), (EXPAND_START, 1),
        (CAPTURE_START, 1), (CLAMP_FIRST, 1), (CLAMP_FINISH, 1),
        (FULL_FLAG, 1), (CACHED_TEMPLATE, 1), (TRAILING_GATE, 1),
        (TRAILING_PROBE, 1), (VALIDATION_CALL, 1), (VALIDATION_FLAG, 1),
        (b"static PyObject *rust_normalize_expand_buffer(", 1),
        (b"PyObject_GetBuffer(template, &view, PyBUF_SIMPLE)", 1),
        (b"rust_match_expand_fallback(match, normalized)", 1),
        (b"PyDescr_NewMethod(", 1), (b"static PyObject *bridge_bind(", 1),
        (b"Py_CLEAR(method->signature);", 2),
        (b"Py_VISIT(method->signature);", 1),
    )
    for anchor, count in anchors:
        require(source.count(anchor) == count,
                "preserve capture clamp, native descriptors, expansion, and ordering")
    for forbidden in (b"rust_bound_get_signature", b'PyImport_ImportModule("inspect")',
                      b'PyImport_ImportModule("functools")',
                      b'PyImport_ImportModule("re")',
                      b'PyImport_ImportModule("regex")'):
        require(source.count(forbidden) == 0,
                "reject external introspection, matcher delegation, or regex dependency")


def transform(source: bytes, exact: bool = False) -> bytes:
    require(type(source) is bytes, "derive correction from complete genuine C bytes")
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA256,
                "reject unauthenticated complete expansion-corrected bridge")
    preserved_source(source)
    before, core, after = extract_core(source)
    require(before.count(EXPAND_FORWARD) == 1 and before.count(CACHE_START) == 1
            and before.count(EXPAND_START) == 1
            and before.index(EXPAND_FORWARD) < before.index(CACHE_START)
            < before.index(EXPAND_START),
            "distinguish the match.expand forward declaration from its full definition")
    require(before.count(TRAILING_GATE) == 1 and before.count(TRAILING_PROBE) == 1
            and before.count(VALIDATION_CALL) == 1 and before.count(VALIDATION_FLAG) == 1,
            "retain both complete materialized expansion/probe correction sites")
    sites = ((ORIGINAL_INITIAL, CORRECTED_INITIAL),
             (ORIGINAL_JOIN, CORRECTED_JOIN),
             (ORIGINAL_SUCCESS, CORRECTED_SUCCESS),
             (ORIGINAL_FAILURE, CORRECTED_FAILURE))
    corrected = core
    for original, replacement in sites:
        require(corrected.count(original) == 1 and corrected.count(replacement) == 0,
                "require each unique unapplied substitution-order correction site")
        corrected = corrected.replace(original, replacement, 1)
    validation = corrected.index(b"rust_replacement_cache(\n")
    subject_open = corrected.index(b"rust_subject_open(&subject, pattern_value, value, 1)")
    require(validation < subject_open and corrected.count(b"                0, &raw, &tokens\n") == 1,
            "validate all noncallable replacements before acquiring their subjects")
    require(corrected.count(b"int subject_acquired = 0;") == 1
            and corrected.count(b"subject_acquired = 1;") == 1
            and corrected.count(b"subject_acquired = 0;") == 2,
            "track exactly one subject acquisition and one early release")
    deferred = corrected.index(CORRECTED_JOIN)
    release = corrected.index(b"rust_subject_release(&subject);", deferred)
    separator = corrected.index(b"PyObject *separator = Py_GetConstant(", deferred)
    join = corrected.index(b"PyBytes_Join(separator, pieces)", separator)
    require(deferred < release < separator < join,
            "copy tail, release noncallback subject, and only then join replacements")
    require(corrected.count(b"if (subject_acquired) rust_subject_release(&subject);") == 2
            and corrected.count(b"if (!callback) {\n            rust_subject_release") == 1,
            "preserve callbacks and prevent every duplicate subject release")
    reversed_core = corrected
    for original, replacement in reversed(sites):
        require(reversed_core.count(replacement) == 1,
                "reject nonunique reversible composed correction")
        reversed_core = reversed_core.replace(replacement, original, 1)
    require(reversed_core == core, "require four reversible edits in one C function")
    result = before + corrected + after
    preserved_source(result)
    result_before, _result_core, result_after = extract_core(result)
    require(result_before == before and result_after == after,
            "never mutate existing expansion, cache, clamp, descriptors, or engine")
    require(len(result) == len(source) + 189,
            "reject bytes outside the exact four-site event-order correction")
    if exact:
        require(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
                "reject drift in complete predicted composed corrected bridge")
    return result


def synthetic_source() -> bytes:
    return b"".join((
        EXPAND_FORWARD, b"\n", CACHE_START, b"void) {\n    ", FULL_FLAG,
        b"\n    ", CACHED_TEMPLATE, b";\n}\n",
        TRAILING_GATE, TRAILING_PROBE, b"    return -1;\n}\n",
        CAPTURE_START, b") {\n    ", CLAMP_FIRST, b"\n    ", CLAMP_FINISH,
        b"\n}\nPyDescr_NewMethod(pattern, NULL);\n",
        b"static PyObject *rust_normalize_expand_buffer(\n",
        b"PyObject_GetBuffer(template, &view, PyBUF_SIMPLE);\n}\n",
        EXPAND_START, b"\n", VALIDATION_FLAG, VALIDATION_CALL,
        b";\nrust_match_expand_fallback(match, normalized);\n}\n",
        b"static PyObject *bridge_bind(\nPy_CLEAR(method->signature);\n",
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
    require(kind in ("acquire", "release", "acquire-error", "hash")
            and role in ("subject", "replacement")
            and owner in ("outer", "nested", "join")
            and (flags is None or flags in (SIMPLE, FULL_READONLY)),
            "require exact synthetic PEP-688 ownership event")
    return kind, role, flags, owner


def validate_events(events: list[tuple[str, str, int | None, str]],
                    *, forbid_subject: bool = False) -> None:
    require(type(events) is list, "require complete ordered exporter events")
    active = {"subject": 0, "replacement": 0}
    stack: list[str] = []
    for item in events:
        require(type(item) is tuple and len(item) == 4,
                "reject incomplete synthetic exporter event")
        kind, role, flags, _owner = item
        require(role in active and kind in ("acquire", "release", "acquire-error", "hash"),
                "reject forged exporter operation or role")
        if forbid_subject:
            require(role != "subject", "failing replacement illegally touches subject")
        if kind == "acquire":
            require(flags in (SIMPLE, FULL_READONLY), "preserve exact buffer flags")
            active[role] += 1
            stack.append(role)
        elif kind == "release":
            require(flags is None and active[role] > 0 and bool(stack)
                    and stack[-1] == role,
                    "reject unmatched, reordered, or duplicate exporter release")
            active[role] -= 1
            stack.pop()
        elif kind == "acquire-error":
            require(flags in (SIMPLE, FULL_READONLY), "preserve failing exporter flags")
        else:
            require(role == "replacement" and flags is None,
                    "preserve owned replacement hash ordering")
    require(not stack and all(count == 0 for count in active.values()),
            "require each acquired subject and replacement export to release once")


def substitution_records() -> list[dict]:
    cohorts = ((57, "stable"), (58, "mutate"), (59, "fixed-hash"),
               (60, "unhashable"), (61, "fail"))
    apis = ("module.sub", "module.subn", "pattern.sub", "pattern.subn", "match.expand")
    cases: list[dict] = []
    cohort_counts = {behavior: 0 for _index, behavior in cohorts}
    api_counts = {api: 0 for api in apis[:-1]}
    failing = full_readonly = fixed_hash = 0
    for cohort_index, behavior in cohorts:
        for variant in range(80):
            api = apis[variant % 5]
            style = ("literal", "escaped-named", "escaped-numeric", "callback")[variant % 4]
            if api == "match.expand" or style == "callback":
                continue
            if behavior == "fail":
                events = [event("acquire-error", "replacement", SIMPLE),
                          event("acquire-error", "replacement", SIMPLE),
                          event("acquire-error", "replacement", FULL_READONLY)]
                validate_events(events, forbid_subject=True)
                failing += 1
            else:
                events = [event("acquire", "replacement", SIMPLE),
                          event("release", "replacement")]
                if style != "literal":
                    if behavior == "fixed-hash":
                        events.append(event("hash", "replacement"))
                        fixed_hash += 1
                    flags = FULL_READONLY if behavior == "unhashable" else SIMPLE
                    events.extend((event("acquire", "replacement", flags),
                                   event("release", "replacement")))
                    full_readonly += int(flags == FULL_READONLY)
                events.extend((event("acquire", "subject", SIMPLE),
                               event("release", "subject")))
                if style == "literal":
                    events.extend((event("acquire", "replacement", SIMPLE, "join"),
                                   event("release", "replacement", owner="join")))
                validate_events(events)
                first_subject = next(index for index, item in enumerate(events)
                                     if item[1] == "subject")
                require(all(item[1] == "replacement" for item in events[:first_subject]),
                        "require complete replacement validation before subject export")
                if style == "literal":
                    require(next(index for index, item in enumerate(events)
                                 if item[:2] == ("release", "subject"))
                            < next(index for index, item in enumerate(events)
                                   if item[3] == "join"),
                            "release literal subjects before replacement join exports")
            cohort_counts[behavior] += 1
            api_counts[api] += 1
            cases.append({"id": "substitution-v2:" + str(cohort_index * 80 + variant),
                          "api": api, "behavior": behavior, "style": style,
                          "events": events})
    require(len(cases) == 240 and all(value == 48 for value in cohort_counts.values())
            and all(value == 60 for value in api_counts.values())
            and failing == 48 and full_readonly == 32 and fixed_hash == 32,
            "model all 240 substitution failures, fixed hashes, FULL_RO and failures")
    return cases


def ordering_shape_records() -> list[dict]:
    names = ("zero", "one", "two", "short", "five", "equal", "thirteen", "long")
    apis = ("module.sub", "module.subn", "pattern.sub", "pattern.subn")
    behaviors = ("stable", "mutate", "fail-outer", "fail-nested")
    cases: list[dict] = []
    failures = 0
    for outer in names:
        for nested in names:
            for api in apis:
                for behavior in behaviors:
                    if behavior == "fail-outer":
                        events = [event("acquire-error", "replacement", SIMPLE)]
                    elif behavior == "fail-nested":
                        events = [event("acquire", "replacement", SIMPLE),
                                  event("acquire-error", "replacement", SIMPLE, "nested"),
                                  event("release", "replacement")]
                    else:
                        events = [event("acquire", "replacement", SIMPLE),
                                  event("release", "replacement"),
                                  event("acquire", "subject", SIMPLE),
                                  event("release", "subject")]
                    failed = behavior.startswith("fail-")
                    validate_events(events, forbid_subject=failed)
                    failures += int(failed)
                    cases.append({"id": "shape-order:" + outer + ":" + nested
                                  + ":" + api + ":" + behavior,
                                  "api": api, "behavior": behavior, "events": events})
    require(len(cases) == 1024 and failures == 512,
            "model all 1,024 shape ordering inversions and 512 untouched-subject failures")
    for api in apis:
        require(sum(case["api"] == api for case in cases) == 256,
                "model exactly 256 ordering cases per substitution API")
    for behavior in behaviors:
        require(sum(case["behavior"] == behavior for case in cases) == 256,
                "model exactly 256 ordering cases per exporter behavior")
    return cases


class WitnessPatternError(Exception):
    def __init__(self, message: str, replacement: object, position: int) -> None:
        super().__init__(message)
        self.msg = message
        self.pattern = replacement
        self.pos = position


class WitnessProbeFailure(Exception):
    pass


class WitnessTemplate:
    def __init__(self, text: str, events: list[str], mutation: str = "stable",
                 fail_length: bool = False) -> None:
        self.text = text
        self.events = events
        self.mutation = mutation
        self.fail_length = fail_length

    def __len__(self) -> int:
        self.events.append("length-probe:template:outer")
        if self.fail_length:
            raise WitnessProbeFailure("template outer length rejected")
        if self.mutation == "mutate":
            self.events.append("mutation:template:outer")
        return len(self.text)


def restore_model(error: WitnessPatternError, template: WitnessTemplate) -> None:
    require(type(error) is WitnessPatternError, "preserve owned PatternError identity")
    if error.msg == TRAILING_ESCAPE:
        len(template)
    raise WitnessPatternError(error.msg, template, error.pos)


def expand_model(template: WitnessTemplate, events: list[str]) -> None:
    events.append("buffer-acquire:template:outer:PyBUF_SIMPLE")
    events.append("buffer-release:template:outer")
    events.append("template-helper:validate-only")
    if template.text in MALFORMED_NAMED_TEMPLATES:
        message = ("missing group name" if template.text == MALFORMED_NAMED_TEMPLATES[0]
                   else "missing >, unterminated name")
        restore_model(WitnessPatternError(message, template, 10), template)
    if template.text.endswith("\\"):
        restore_model(WitnessPatternError(TRAILING_ESCAPE, template, 5), template)
    events.append("template-helper:expand")


def probe_and_expansion_records() -> tuple[list[dict], list[dict], list[dict]]:
    probes: list[dict] = []
    malformed: list[dict] = []
    overlap: list[dict] = []
    apis = ("module.sub", "module.subn", "pattern.sub", "pattern.subn")

    def trailing(operation: str, shape: str, mutation: str, index: int,
                 destination: list[dict]) -> None:
        events: list[str] = []
        template = WitnessTemplate("outer\\", events, mutation)
        try:
            if operation == "expand":
                expand_model(template, events)
            else:
                events.append("template-helper:parse")
                restore_model(WitnessPatternError(TRAILING_ESCAPE, template, 5), template)
        except WitnessPatternError as error:
            require(error.msg == TRAILING_ESCAPE and error.pattern is template
                    and error.pos == 5, "preserve original nested trailing error")
        else:
            raise FreezeError("missing trailing-escape PatternError")
        require(events.count("length-probe:template:outer") == 1
                and not any(item.startswith("match.group:")
                            or item.startswith("buffer-acquire:subject:")
                            for item in events),
                "probe exactly once before captures or subject reacquisition")
        prefix = "shape-overlap:" if destination is overlap else "shape-probe:"
        destination.append({"id": prefix + operation + ":" + shape + ":"
                            + mutation + ":" + str(index), "api": operation,
                            "shape": shape, "mutation": mutation, "events": events})

    for api in apis:
        for index in range(8):
            trailing(api, "template-only-direct", "stable", index, probes)
    for shape, mutation in (("template-only-direct", "stable"),
                            ("both-direct", "stable"),
                            ("template-only-direct", "mutate")):
        for index in range(8):
            trailing("expand", shape, mutation, index, probes)
    for text in MALFORMED_NAMED_TEMPLATES:
        require(len(text) in (13, 19), "preserve exact malformed visible lengths")
        for mutation in ("stable", "mutate"):
            for index in range(8):
                events: list[str] = []
                template = WitnessTemplate(text, events, mutation, fail_length=True)
                try:
                    expand_model(template, events)
                except WitnessPatternError as error:
                    require(error.msg != TRAILING_ESCAPE and error.pattern is template
                            and error.pos == 10, "preserve malformed nested error")
                    message = error.msg
                else:
                    raise FreezeError("missing malformed named-template PatternError")
                require(events == ["buffer-acquire:template:outer:PyBUF_SIMPLE",
                                   "buffer-release:template:outer",
                                   "template-helper:validate-only"],
                        "malformed named templates must avoid probes and reacquisition")
                malformed.append({"id": "shape-expand:" + str(len(text)) + ":"
                                  + mutation + ":" + str(index), "api": "expand",
                                  "visible_length": len(text), "mutation": mutation,
                                  "message": message, "events": events})
    for api in apis:
        for index in range(8):
            trailing(api, "both-direct", "stable", index, overlap)
    require(len(probes) == 56 and len(malformed) == 32 and len(overlap) == 32,
            "require disjoint B56+C32 records and separate A32 ordering overlap")
    require(sum(case["api"] != "expand" for case in probes) == 32
            and sum(case["api"] == "expand" for case in probes) == 24,
            "require exact 32 substitution and 24 expansion trailing probes")
    return probes, malformed, overlap


def modeled_partition() -> dict:
    substitution = substitution_records()
    ordering = ordering_shape_records()
    probes, malformed, overlap = probe_and_expansion_records()
    disjoint = substitution + ordering + probes + malformed
    labels = [case["id"] for case in disjoint]
    require(len(disjoint) == 1352 and len(set(labels)) == 1352,
            "partition every authentic original mismatch exactly once")
    require(240 + 1024 + 56 + 32 == 1352,
            "retain exact 240 substitution + 1,024 ordering + 56 probe + 32 expansion")
    require(not any(case["id"] in set(labels) for case in overlap),
            "report the 32 ordering/probe overlaps separately without double counting")
    return {"total_disjoint_original_failure_count": 1352,
            "substitution_v2_failure_count": len(substitution),
            "shape_v2_ordering_failure_count": len(ordering),
            "shape_v2_trailing_probe_failure_count": len(probes),
            "shape_v2_malformed_expansion_failure_count": len(malformed),
            "shape_v2_failure_count": len(ordering) + len(probes) + len(malformed),
            "separate_ordering_probe_overlap_count": len(overlap),
            "overlap_included_in_total": False,
            "disjoint_failure_projection_sha256": digest(
                canonical(disjoint).encode("utf-8")),
            "separate_overlap_projection_sha256": digest(
                canonical(overlap).encode("utf-8")),
            "subject_acquired_for_failing_replacement_count": 0,
            "failing_replacement_buffer_error_count": 512,
            "fixed_hash_escaped_case_count": 32,
            "full_readonly_escaped_case_count": 32,
            "malformed_visible_lengths": [13, 19],
            "malformed_named_template_length_probe_count": 0,
            "malformed_named_template_subject_reacquisition_count": 0}


def synthetic_tests(wall: SourceWall) -> dict:
    require(not wall.input_authorized and INPUT not in wall.allowed,
            "all hostile source-only controls must run before candidate authorization")
    source = synthetic_source()
    corrected = transform(source)
    require(len(corrected) - len(source) == 189,
            "retain exact four-site +189-byte correction on expansion successor")
    require(source.count(b"static PyObject *rust_match_expand(") == 2
            and source.count(EXPAND_FORWARD) == 1
            and source.count(EXPAND_START) == 1,
            "distinguish actual declaration from full match.expand definition")
    partition = modeled_partition()
    rejected = 0

    def reject(operation, reason: str) -> None:
        nonlocal rejected
        try:
            operation()
        except (FreezeError, OSError, TypeError, ValueError,
                IndexError, WitnessProbeFailure):
            rejected += 1
            return
        raise FreezeError("hostile source-only control unexpectedly passed: " + reason)

    anchors = (ORIGINAL_INITIAL, ORIGINAL_JOIN, ORIGINAL_SUCCESS, ORIGINAL_FAILURE,
               CORE_START, CORE_END, CACHE_START, EXPAND_FORWARD, EXPAND_START,
               CAPTURE_START, CLAMP_FIRST, CLAMP_FINISH, FULL_FLAG, CACHED_TEMPLATE,
               TRAILING_GATE, TRAILING_PROBE, VALIDATION_CALL, VALIDATION_FLAG)
    for anchor in anchors:
        reject(lambda item=anchor: transform(source.replace(item, b"", 1)),
               "missing exact correction or preserved expansion/clamp anchor")
        reject(lambda item=anchor: transform(source.replace(item, item + item, 1)),
               "duplicated exact correction or preserved expansion/clamp anchor")
    for site in (ORIGINAL_INITIAL, ORIGINAL_JOIN, ORIGINAL_SUCCESS, ORIGINAL_FAILURE):
        for offset in range(0, len(site), 29):
            altered = site[:offset] + bytes((site[offset] ^ 1,)) + site[offset + 1:]
            reject(lambda original=site, damage=altered: transform(
                source.replace(original, damage, 1)), "single-byte owned C source drift")
    for payload in (b'{"x":1,"x":2}', b"NaN", b"1.2", b"01",
                    b'{"x":"\\ud800"}', b'{"x":true} trailing'):
        reject(lambda raw=payload: StrictJSON(raw).decode(), "unsafe public evidence JSON")
    reject(lambda: validate_events([event("release", "subject")]),
           "release without subject ownership")
    reject(lambda: validate_events([event("acquire", "subject", SIMPLE),
                                    event("release", "subject"),
                                    event("release", "subject")]),
           "duplicate subject release")
    reject(lambda: validate_events([event("acquire", "subject", SIMPLE),
                                    event("release", "subject")], forbid_subject=True),
           "failing replacement touches its subject")
    for message in ("missing group name", "missing >, unterminated name",
                    "unknown group name", "bad character in group name"):
        events: list[str] = []
        template = WitnessTemplate("<\\g<word", events, fail_length=True)
        try:
            restore_model(WitnessPatternError(message, template, 10), template)
        except WitnessPatternError as error:
            require(error.msg == message and error.pattern is template
                    and error.pos == 10 and not events,
                    "non-trailing PatternErrors must never probe replacement length")
        else:
            raise FreezeError("missing preserved non-trailing PatternError")
    for operation in ("sub", "expand"):
        events = []
        template = WitnessTemplate("outer\\", events, fail_length=True)
        reject(lambda item=template: restore_model(
            WitnessPatternError(TRAILING_ESCAPE, item, 5), item),
            operation + " failed length supersedes saved PatternError")
        require(events == ["length-probe:template:outer"],
                "failed trailing replacement length must be probed exactly once")
    reject(lambda: wall.parent(INPUT), "candidate source in a source-only mode")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved primitive unticketed candidate source read")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level candidate source read")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "direct candidate source read")
    reject(lambda: builtins.open(ROOT + "/.git/config"), "Git metadata access")
    reject(lambda: builtins.open(ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json"),
           "invalidated final holdout proposal access")
    reject(lambda: builtins.open(ROOT + "/oracle/phase2/evidence/"
                                "repaired-rust-original-campaign-v16-rust-phase2-v25-"
                                "rust-capture-clamp-v1-root-provenance-original-p0-v25-"
                                "failures.json.gz"), "compressed failure archive read")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "workspace directory mutation")
    reject(lambda: time.time(), "clock sample")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native library load")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None),
           "compiler or candidate worker launch")
    reject(lambda: sys.audit("socket.connect", None, None), "network request")
    require(rejected >= 80 and wall.candidate_source_reads == 0
            and wall.workspace_mutations == 0 and not wall.input_authorized
            and INPUT not in wall.allowed,
            "require exhaustive combined hostile controls without source reads/writes")
    no_matching_imports()
    return {"synthetic_input_bytes": len(source),
            "synthetic_output_bytes": len(corrected),
            "synthetic_source_delta_bytes": 189,
            "existing_expansion_correction_sites_preserved": 2,
            "new_substitution_order_correction_sites": 4,
            "match_expand_forward_declaration_distinguished": True,
            "hostile_controls_rejected": rejected,
            "modeled_original_failure_partition": partition,
            "candidate_source_files_read": 0,
            "workspace_mutations": 0,
            "candidate_executions": 0,
            "final_holdout": FINAL_HOLDOUT}


def value(document: object, name: str, expected: object) -> None:
    require(type(document) is dict and document.get(name) == expected,
            "reject incomplete or substituted immutable evidence: " + name)


def authenticated_evidence(owners: dict[str, bytes]) -> dict:
    expand_contract = StrictJSON(owners["expand_contract"]).decode()
    value(expand_contract, "schema", "rebar-owned-rust-expand-probe-semantics-v1-source-freeze")
    value(expand_contract["source"], "path", OWNERS[0][1])
    value(expand_contract["source"], "sha256", OWNERS[0][2])
    value(expand_contract["protocol"], "path", OWNERS[1][1])
    value(expand_contract["protocol"], "sha256", OWNERS[1][2])
    expand_correction = expand_contract["exact_expand_probe_correction"]
    for key, expected in (("target_path", INPUT), ("target_sha256", INPUT_SHA256),
                          ("target_bytes", INPUT_BYTES),
                          ("capture_clamp_correction_retained", True),
                          ("no_external_introspection_correction_retained", True),
                          ("stdlib_matching_delegation_added", False),
                          ("external_regex_dependency_added", False)):
        value(expand_correction, key, expected)
    expand_partition = expand_contract["exact_targeted_original_shape_partition"]
    for key, expected in (("targeted_record_count", 88),
                          ("disjoint_missing_trailing_escape_probe_records", 56),
                          ("malformed_named_template_records", 32),
                          ("separate_substitution_ordering_overlap_records", 32),
                          ("overlap_included_in_targeted_record_count", False)):
        value(expand_partition, key, expected)
    expansion = StrictJSON(owners["expand_application"]).decode()
    for key, expected in (("schema", "rebar-owned-rust-expand-probe-semantics-v1-"
                           "source-freeze-root-materialization"),
                          ("source_sha256", OWNERS[0][2]),
                          ("protocol_sha256", OWNERS[1][2]),
                          ("contract_sha256", OWNERS[2][2]),
                          ("target_path", INPUT), ("target_sha256", INPUT_SHA256),
                          ("target_bytes", INPUT_BYTES),
                          ("targeted_record_count", 88),
                          ("separate_substitution_ordering_overlap_records", 32)):
        value(expansion, key, expected)
    require(type(expansion["frozen_commit"]) is str
            and len(expansion["frozen_commit"]) == 40
            and expansion["frozen_commit"] == expansion["pushed_commit"],
            "authenticate pushed expansion application commit")
    for key, expected in (("candidate_source_files_read", 1),
                          ("candidate_executions", 0), ("workspace_mutations", 2),
                          ("final_holdout", FINAL_HOLDOUT)):
        value(expansion["effects"], key, expected)

    order_contract = StrictJSON(owners["order_contract"]).decode()
    value(order_contract, "schema", "rebar-owned-rust-substitution-event-order-v2-source-freeze")
    value(order_contract["source"], "path", OWNERS[4][1])
    value(order_contract["source"], "sha256", OWNERS[4][2])
    value(order_contract["protocol"], "path", OWNERS[5][1])
    value(order_contract["protocol"], "sha256", OWNERS[5][2])
    ordering = order_contract["exact_first_party_event_order_correction"]
    for key, expected in (("target_sha256", "c69e24a87c251a332b79c4f4b5ed1a9f"
                           "232847e446518930473a2ec871f020ab"),
                          ("target_bytes", 177335), ("source_delta_bytes", 189),
                          ("exact_replacement_site_count", 4),
                          ("noncallback_replacement_validated_before_subject", True),
                          ("match_expand_forward_declaration_preserved", True),
                          ("match_expand_complete_definition_preserved", True),
                          ("capture_clamp_correction_retained", True),
                          ("no_external_introspection_correction_retained", True)):
        value(ordering, key, expected)
    value(order_contract["modeled_original_substitution_v2_failures"],
          "historical_failure_count", 240)
    value(order_contract["modeled_original_shape_v2_failures"],
          "targeted_evaluation_order_case_count", 1024)
    value(order_contract, "combined_targeted_historical_mismatch_count", 1264)
    order_application = StrictJSON(owners["order_application"]).decode()
    for key, expected in (("schema", "rebar-owned-rust-substitution-event-order-v2-"
                           "source-freeze-root-materialization"),
                          ("source_sha256", OWNERS[4][2]),
                          ("protocol_sha256", OWNERS[5][2]),
                          ("contract_sha256", OWNERS[6][2]),
                          ("target_sha256", "c69e24a87c251a332b79c4f4b5ed1a9f"
                           "232847e446518930473a2ec871f020ab"),
                          ("target_bytes", 177335),
                          ("capture_clamp_preserved", True),
                          ("no_external_introspection_preserved", True),
                          ("replacement_validated_before_subject", True),
                          ("duplicate_subject_release_precluded", True),
                          ("combined_targeted_historical_mismatch_count", 1264),
                          ("final_holdout", FINAL_HOLDOUT)):
        value(order_application, key, expected)
    require(type(order_application["frozen_commit"]) is str
            and len(order_application["frozen_commit"]) == 40
            and order_application["frozen_commit"] == order_application["pushed_commit"],
            "authenticate pushed ordering V2 application commit")
    for key, expected in (("candidate_source_files_read", 1),
                          ("candidate_executions", 0), ("workspace_mutations", 2)):
        value(order_application["effects"], key, expected)

    ledger = StrictJSON(owners["v25_complete_failure_receipt"]).decode()
    for key, expected in (("publication_status", "PASS"),
                          ("publication_pass_means", "DURABLE PUBLICATION ONLY"),
                          ("candidate_status", "FAIL"),
                          ("semantic_mismatch_count", 1352),
                          ("verified_passing_case_count", 15877),
                          ("case_execution_denominator", 31237),
                          ("suite_count", 13),
                          ("actual_candidate_workers", 13),
                          ("named_private_waiver_count", 13),
                          ("candidate_qualified", False),
                          ("hidden_cases_read", 0),
                          ("benchmark_files_read", 0),
                          ("clock_samples", 0)):
        value(ledger, key, expected)
    suites = ledger["suite_integrity"]
    require(type(suites) is list and len(suites) == 13,
            "authenticate all thirteen original complete suite records")
    failures = {row["suite"]: row["mismatch_count"] for row in suites
                if row.get("mismatch_count", 0)}
    require(failures == {"substitution_v2": 240, "shape_v2": 1112}
            and sum(row["case_execution_denominator"] for row in suites) == 31237
            and sum(row["verified_passing_case_count"] for row in suites) == 15877,
            "preserve the complete 240+1112 authentic historical failure partition")
    archive = ledger["archive"]
    value(archive, "sha256", "dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7")
    value(archive, "size_bytes", 3771743)
    previous_contract = StrictJSON(owners["v1_contract"]).decode()
    value(previous_contract, "schema",
          "rebar-owned-rust-complete-semantic-correction-v1-source-freeze")
    value(previous_contract, "version", 1)
    value(previous_contract["source"], "path", OWNERS[9][1])
    value(previous_contract["source"], "sha256", OWNERS[9][2])
    value(previous_contract["protocol"], "path", OWNERS[10][1])
    value(previous_contract["protocol"], "sha256", OWNERS[10][2])
    value(previous_contract["exact_complete_semantic_correction"],
          "target_sha256", OUTPUT_SHA256)
    failure = StrictJSON(owners["v1_preapplication_failure"]).decode()
    for key, expected in (("schema", "rebar-rust-complete-semantic-"
                           "correction-v1-preapplication-failure"),
                          ("source_sha256", OWNERS[9][2]),
                          ("protocol_sha256", OWNERS[10][2]),
                          ("contract_sha256", OWNERS[11][2]),
                          ("status", "FAIL"),
                          ("error", "hostile source-only control unexpectedly passed: "
                           "candidate source in a source-only mode"),
                          ("candidate_source_variant_created", False),
                          ("candidate_workers_started", 0),
                          ("hidden_cases_read", 0),
                          ("historical_target_case_count", 1352),
                          ("candidate_qualified", False),
                          ("winner_selected", False)):
        value(failure, key, expected)
    require(type(failure["frozen_commit"]) is str
            and len(failure["frozen_commit"]) == 40,
            "authenticate actual immutable V1 preapplication failure")
    return {"expand_source_sha256": OWNERS[0][2],
            "expand_protocol_sha256": OWNERS[1][2],
            "expand_contract_sha256": OWNERS[2][2],
            "expand_application_sha256": OWNERS[3][2],
            "expand_materialized_source_sha256": INPUT_SHA256,
            "expand_materialized_source_bytes": INPUT_BYTES,
            "ordering_source_sha256": OWNERS[4][2],
            "ordering_protocol_sha256": OWNERS[5][2],
            "ordering_contract_sha256": OWNERS[6][2],
            "ordering_application_sha256": OWNERS[7][2],
            "original_v25_failure_receipt_sha256": OWNERS[8][2],
            "v1_source_sha256": OWNERS[9][2],
            "v1_protocol_sha256": OWNERS[10][2],
            "v1_contract_sha256": OWNERS[11][2],
            "v1_preapplication_failure_sha256": OWNERS[12][2],
            "v1_preapplication_failure_status": "FAIL",
            "candidate_input_authorized_after_all_controls": True,
            "original_candidate_status": "FAIL",
            "original_semantic_mismatch_count": 1352,
            "original_verified_passing_case_count": 15877,
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "original_failing_suite_counts": failures,
            "archive_opened": False, "archive_inflated": False,
            "candidate_correctness": "NOT MEASURED"}


def validate_contract(document: object, source_sha: str, protocol_sha: str) -> None:
    require(type(document) is dict, "require complete frozen correction contract")
    value(document, "schema", SCHEMA)
    value(document, "version", 2)
    value(document, "family", "rust")
    value(document, "phase", "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS")
    value(document, "status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN")
    value(document, "final_holdout", FINAL_HOLDOUT)
    value(document, "source", {"path": SOURCE, "sha256": source_sha})
    value(document, "protocol", {"path": PROTOCOL, "sha256": protocol_sha})
    correction = document["exact_complete_semantic_correction"]
    for key, expected in (("input_path", INPUT), ("input_sha256", INPUT_SHA256),
                          ("input_bytes", INPUT_BYTES), ("input_device", DEVICE),
                          ("input_inode", INPUT_INODE), ("input_mode", "0600"),
                          ("target_path", TARGET), ("target_sha256", OUTPUT_SHA256),
                          ("target_bytes", OUTPUT_BYTES), ("source_delta_bytes", 189),
                          ("existing_expansion_correction_sites_preserved", 2),
                          ("new_substitution_order_correction_sites", 4),
                          ("changed_function", "rust_substitute_core"),
                          ("changed_function_count", 1),
                          ("noncallback_replacement_validated_before_subject", True),
                          ("adapter_validation_length", 0),
                          ("deferred_noncallback_subject_released_before_bytes_join", True),
                          ("callback_subject_ownership_unchanged", True),
                          ("duplicate_subject_release_precluded", True),
                          ("match_expand_forward_declaration_preserved", True),
                          ("match_expand_complete_definition_preserved", True),
                          ("trailing_escape_probe_message_exact", TRAILING_ESCAPE),
                          ("other_pattern_errors_probe_length", False),
                          ("match_expand_exporter_validation_helper_arity", 3),
                          ("malformed_named_template_subject_reacquisition_count", 0),
                          ("capture_clamp_correction_retained", True),
                          ("no_external_introspection_correction_retained", True),
                          ("stdlib_matching_delegation_added", False),
                          ("external_regex_dependency_added", False),
                          ("candidate_built", False), ("candidate_imported", False),
                          ("candidate_matching", "NOT RUN"),
                          ("candidate_qualified", False),
                          ("runtime_non_delegation", "NOT ESTABLISHED")):
        value(correction, key, expected)
    partition = document["exact_disjoint_original_failure_partition"]
    for key, expected in (("total_disjoint_original_failure_count", 1352),
                          ("substitution_v2_failure_count", 240),
                          ("shape_v2_ordering_failure_count", 1024),
                          ("shape_v2_trailing_probe_failure_count", 56),
                          ("shape_v2_malformed_expansion_failure_count", 32),
                          ("shape_v2_failure_count", 1112),
                          ("separate_ordering_probe_overlap_count", 32),
                          ("overlap_included_in_total", False),
                          ("subject_acquired_for_failing_replacement_count", 0),
                          ("failing_replacement_buffer_error_count", 512),
                          ("fixed_hash_escaped_case_count", 32),
                          ("full_readonly_escaped_case_count", 32),
                          ("malformed_visible_lengths", [13, 19]),
                          ("malformed_named_template_length_probe_count", 0),
                          ("malformed_named_template_subject_reacquisition_count", 0)):
        value(partition, key, expected)
    checked_sha(partition["disjoint_failure_projection_sha256"],
                "disjoint_failure_projection_sha256")
    checked_sha(partition["separate_overlap_projection_sha256"],
                "separate_overlap_projection_sha256")
    lineage = document["authenticated_public_predecessors"]
    for key, expected in (("expand_source_sha256", OWNERS[0][2]),
                          ("expand_protocol_sha256", OWNERS[1][2]),
                          ("expand_contract_sha256", OWNERS[2][2]),
                          ("expand_application_sha256", OWNERS[3][2]),
                          ("ordering_source_sha256", OWNERS[4][2]),
                          ("ordering_protocol_sha256", OWNERS[5][2]),
                          ("ordering_contract_sha256", OWNERS[6][2]),
                          ("ordering_application_sha256", OWNERS[7][2]),
                          ("original_v25_failure_receipt_sha256", OWNERS[8][2]),
                          ("v1_source_sha256", OWNERS[9][2]),
                          ("v1_protocol_sha256", OWNERS[10][2]),
                          ("v1_contract_sha256", OWNERS[11][2]),
                          ("v1_preapplication_failure_sha256", OWNERS[12][2]),
                          ("v1_preapplication_failure_status", "FAIL"),
                          ("original_semantic_mismatch_count", 1352),
                          ("original_case_execution_denominator", 31237),
                          ("original_suite_count", 13),
                          ("original_failing_suite_counts",
                           {"substitution_v2": 240, "shape_v2": 1112}),
                          ("archive_opened", False), ("archive_inflated", False)):
        value(lineage, key, expected)
    wall = document["physical_source_wall"]
    for key, expected in (("installed_before_owner_reads", True),
                          ("descriptor_relative_o_nofollow", True),
                          ("authenticated_public_predecessor_owner_count", len(OWNERS)),
                          ("authenticated_public_owner_count_including_current", len(OWNERS) + 3),
                          ("source_mode_candidate_source_reads", 0),
                          ("self_test_candidate_source_reads", 0),
                          ("source_mode_filesystem_writes", 0),
                          ("self_test_filesystem_writes", 0),
                          ("archive_content_reads", 0), ("archive_inflations", 0),
                          ("native_binary_reads", 0), ("timer_reads", 0),
                          ("git_metadata_reads", 0), ("final_holdout_content_reads", 0),
                          ("proposal_content_reads", 0),
                          ("apply_requires_explicit_root_authorization", True),
                          ("apply_requires_frozen_commit_equals_pushed_commit", True),
                          ("apply_candidate_source_read_count", 1),
                          ("candidate_input_denied_until_all_source_controls_pass", True),
                          ("actual_apply_runs_all_hostile_controls_before_input_authorization", True),
                          ("candidate_input_authorized_once_after_complete_owner_verification", True),
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


def parse_arguments(arguments: list[str]) -> dict:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require explicit complete immutable arguments")
    flags = {"--self-test", "--verify-source", "--verify-frozen-context",
             "--apply", "--root-authorized"}
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
    modes = tuple(item for item in ("--self-test", "--verify-source",
                                    "--verify-frozen-context", "--apply")
                  if parsed.get(item) is True)
    require(len(modes) == 1, "require exactly one source-only gate or root-only apply")
    mode = modes[0]
    if mode == "--self-test":
        require(set(parsed) == {mode}, "source-only self-test accepts no owner pins")
    elif mode in ("--verify-source", "--verify-frozen-context"):
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256"},
                "source verification requires exactly the frozen owner SHA-256 triple")
    else:
        require(set(parsed) == {mode, "--root-authorized", "--source-sha256",
                                "--protocol-sha256", "--contract-sha256",
                                "--frozen-commit", "--pushed-commit"},
                "root-only apply requires all owner pins and identical pushed commit")
        for label in ("--frozen-commit", "--pushed-commit"):
            commit = parsed[label]
            require(type(commit) is str and len(commit) == 40
                    and all(char in "0123456789abcdef" for char in commit),
                    "require complete lowercase frozen commit: " + label)
        require(parsed["--frozen-commit"] == parsed["--pushed-commit"],
                "refuse complete correction until its frozen commit has been pushed")
    for label in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if label in parsed:
            checked_sha(parsed[label], label)
    return parsed


def effects(wall: SourceWall, mode: str) -> dict:
    return {"mode": mode, "approved_public_owner_reads": wall.public_owner_reads,
            "candidate_source_files_read": wall.candidate_source_reads,
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_workers_started": 0, "reference_workers_started": 0,
            "compiler_processes_started": 0, "native_binary_files_opened": 0,
            "native_libraries_loaded": 0, "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0, "final_holdout_cases_opened": 0,
            "final_holdout_cases_generated": 0,
            "final_holdout_proposal_files_opened": 0, "git_metadata_reads": 0,
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
                "self-test must read no owner/candidate and mutate no workspace")
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
    contract = StrictJSON(wall.read(CONTRACT, None, None, contract_sha)).decode()
    validate_contract(contract, source_sha, protocol_sha)
    owners: dict[str, bytes] = {}
    for role, relative, expected, count, inode in OWNERS:
        require(not relative.startswith("candidates/")
                and not relative.endswith((".gz", ".so"))
                and "holdout" not in relative and "phase3/" not in relative
                and ".git/" not in relative,
                "never admit candidate, archive, native, Git, timer, or final owner")
        owners[role] = wall.read(relative, count, inode, expected)
    evidence = authenticated_evidence(owners)
    require(wall.public_owner_reads == len(OWNERS) + 3
            and wall.candidate_source_reads == 0 and wall.workspace_mutations == 0,
            "authenticate complete predecessors using public plaintext owners only")
    tests = synthetic_tests(wall)
    partition = tests["modeled_original_failure_partition"]
    for key in ("disjoint_failure_projection_sha256", "separate_overlap_projection_sha256"):
        value(contract["exact_disjoint_original_failure_partition"], key, partition[key])
    if not apply:
        no_matching_imports()
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; ALL 1352 ORIGINAL FAILURES MODELED; SOURCE FROZEN",
                "source_sha256": source_sha, "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "authenticated_public_owner_count": len(OWNERS),
                "authenticated_complete_predecessors": evidence,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "synthetic_controls": tests,
                "effects": effects(wall, "SOURCE FREEZE")}

    wall.authorize_input()
    original = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA256)
    corrected = transform(original, exact=True)
    wall.materialize(corrected)
    no_matching_imports()
    require(wall.candidate_source_reads == 1 and wall.workspace_mutations == 2,
            "create exactly one exclusive directory and one complete corrected source")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; ALL ORIGINAL FAILURES MODELED; NOT BUILT; NOT RUN",
            "frozen_commit": options["--frozen-commit"],
            "pushed_commit": options["--pushed-commit"],
            "source_sha256": source_sha, "protocol_sha256": protocol_sha,
            "contract_sha256": contract_sha,
            "input_path": INPUT, "input_sha256": INPUT_SHA256,
            "input_bytes": INPUT_BYTES,
            "target_path": TARGET, "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES,
            "complete_disjoint_original_failure_count": 1352,
            "substitution_v2_failure_count": 240,
            "shape_v2_failure_count": 1112,
            "separate_ordering_probe_overlap_count": 32,
            "capture_clamp_preserved": True,
            "no_external_introspection_preserved": True,
            "existing_expansion_correction_preserved": True,
            "candidate_input_authorized_after_all_source_controls": True,
            "actual_root_hostile_controls_rejected": tests["hostile_controls_rejected"],
            "replacement_validated_before_subject": True,
            "duplicate_subject_release_precluded": True,
            "post_correction_actual_mismatch_count": "NOT MEASURED",
            "final_holdout": FINAL_HOLDOUT,
            "effects": effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError, KeyError,
            IndexError, TypeError) as error:
        sys.stderr.write("rust-complete-semantic-correction-v2: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
