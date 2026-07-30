#!/usr/bin/env python3
"""Freeze the first-party Rust template-probe and expand-validation correction.

Self-test and source verification never open candidate source, a native object,
an archive, a holdout, or a clock.  Exactly one frozen original V25 plaintext
publication receipt is authenticated.  Only independently authorized root
materialization may read the pinned no-introspection bridge once and create its
exclusive immutable successor after the same frozen commit has been pushed.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("source-only expand-probe freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
DEVICE = 2064
SCHEMA = "rebar-owned-rust-expand-probe-semantics-v1-source-freeze"
SOURCE = "tools/apply_owned_rust_expand_probe_semantics_v1.py"
PROTOCOL = "oracle/phase2/RUST-EXPAND-PROBE-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/rust-expand-probe-semantics-v1.json"
INPUT = "candidates/rust/variants/no_external_introspection_v1/py_bridge.c"
TARGET_DIRECTORY = "candidates/rust/variants/expand_probe_semantics_v1"
TARGET = TARGET_DIRECTORY + "/py_bridge.c"
INPUT_SHA256 = "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7"
INPUT_BYTES = 177146
INPUT_INODE = 524811
OUTPUT_SHA256 = "d0f0422a08592390619138d072cb831d6d446f38e2b67750798a221e7693d822"
OUTPUT_BYTES = 178081
LEDGER = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-"
    "failures-publication-receipt.json"
)
LEDGER_SHA256 = "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59"
LEDGER_BYTES = 11832
LEDGER_INODE = 524846
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 200_000
MAX_JSON_DEPTH = 80
TRAILING_ESCAPE = "bad escape (end of pattern)"
MALFORMED_NAMED_TEMPLATES = (
    "<\\g<word>:\\g<",
    "<\\g<word>:\\g<number",
)


ORIGINAL_RESTORE = b"""static int rust_restore_original_template_error(PyObject *replacement) {
    PyObject *raised = PyErr_GetRaisedException();
    if (raised == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Rust template lost its original exception");
        return -1;
    }

    PyObject *message = PyObject_GetAttrString(raised, "msg");
    if (message == NULL) {
        PyErr_Clear();
        PyErr_SetRaisedException(raised);
        return -1;
    }

    PyObject *position = PyObject_GetAttrString(raised, "pos");
    if (position == NULL) {
        PyErr_Clear();
        Py_DECREF(message);
        PyErr_SetRaisedException(raised);
        return -1;
    }

    if (position == Py_None || !PyUnicode_Check(message)) {
        Py_DECREF(position);
        Py_DECREF(message);
        PyErr_SetRaisedException(raised);
        return -1;
    }

    PyObject *restored = PyObject_CallFunctionObjArgs(
        (PyObject *)Py_TYPE(raised), message, replacement, position, NULL
    );
    Py_DECREF(position);
    Py_DECREF(message);
    Py_DECREF(raised);
    if (restored != NULL) {
        PyErr_SetRaisedException(restored);
    }
    return -1;
}
"""

RESTORE_INSERTION = b"""    int trailing_escape = PyUnicode_CompareWithASCIIString(
        message, "bad escape (end of pattern)"
    );
    if (trailing_escape < 0 && PyErr_Occurred()) {
        Py_DECREF(position);
        Py_DECREF(message);
        Py_DECREF(raised);
        return -1;
    }
    if (trailing_escape == 0 && PyObject_Length(replacement) < 0) {
        Py_DECREF(position);
        Py_DECREF(message);
        Py_DECREF(raised);
        return -1;
    }

"""

RESTORE_CALL = b"    PyObject *restored = PyObject_CallFunctionObjArgs(\n"
CORRECTED_RESTORE = ORIGINAL_RESTORE.replace(
    RESTORE_CALL, RESTORE_INSERTION + RESTORE_CALL, 1
)

ORIGINAL_EXPORTER = b"""            PyObject *normalized = rust_normalize_expand_buffer(template);
            if (normalized == NULL) return NULL;
            PyObject *result = rust_match_expand_fallback(match, normalized);
            Py_DECREF(normalized);
            if (result == NULL) {
                (void)rust_restore_original_template_error(template);
            }
            return result;
"""

EXPORTER_INSERTION = b"""            PyObject *validation_arguments[3] = {
                normalized, (PyObject *)match, Py_True
            };
            PyObject *validated = PyObject_Vectorcall(
                state->template_helper, validation_arguments, 3, NULL
            );
            if (validated == NULL) {
                Py_DECREF(normalized);
                (void)rust_restore_original_template_error(template);
                return NULL;
            }
            Py_DECREF(validated);
"""

EXPORTER_FALLBACK = (
    b"            PyObject *result = "
    b"rust_match_expand_fallback(match, normalized);\n"
)
CORRECTED_EXPORTER = ORIGINAL_EXPORTER.replace(
    EXPORTER_FALLBACK, EXPORTER_INSERTION + EXPORTER_FALLBACK, 1
)

PRESERVED_COUNTS = (
    (b"static int rust_restore_original_template_error(", 1),
    (b"static PyObject *rust_match_expand(RustMatch *match, PyObject *template)", 2),
    (b"static PyObject *rust_normalize_expand_buffer(PyObject *template)", 1),
    (b"PyObject_GetBuffer(template, &view, PyBUF_SIMPLE)", 1),
    (b"rust_normalize_expand_buffer(template)", 1),
    (b"rust_match_expand_fallback(match, normalized)", 1),
    (b"static int rust_output_capture(", 1),
    (b"size_t first = begin > capture.length ? capture.length : begin;", 1),
    (b"size_t finish = end > capture.length ? capture.length : end;", 1),
    (b"PyDescr_NewMethod(", 1),
)


class FreezeError(Exception):
    """Reject drift, unsafe effects, unauthorized evidence, or non-exact output."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete genuine bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require complete lowercase SHA-256: " + name)
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
    require(depth <= MAX_JSON_DEPTH, "reject excessive evidence depth")
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
    raise FreezeError("reject unsupported or nonfinite JSON evidence")


class StrictJSON:
    """Bounded, duplicate-rejecting JSON parser with no json/re import."""

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
            require(self.text[self.index] in "123456789", "reject invalid integer")
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
        value = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing evidence bytes")
        return value


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "rebar", "subprocess", "socket",
                 "threading", "multiprocessing", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matcher, candidate, native loader, worker, or network import")


class SourceWall:
    """Deny-default descriptor-relative physical ownership and root-only writer."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT, LEDGER))
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
        raise FreezeError("source-only physical wall rejected " + reason)

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            flags = args[2] if len(args) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed-candidate-native-archive-holdout-or-write-open")
        if event == "os.mkdir":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
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
        result = self.native_fstat(descriptor)
        require(stat.S_ISDIR(result.st_mode) and result.st_dev == DEVICE,
                "reject substituted immutable workspace root")
        self.root = descriptor
        self.live[descriptor] = ("", "directory")

    def child_directory(self, parent: int, component: str) -> int:
        component = self.checked_component(component)
        info = self.live.get(parent)
        require(info is not None and info[1] == "directory",
                "reject foreign parent directory descriptor")
        relative = component if not info[0] else info[0] + "/" + component
        allow = (any(path.startswith(relative + "/") for path in self.allowed)
                 or self.apply and (relative == TARGET_DIRECTORY
                                    or TARGET_DIRECTORY.startswith(relative + "/")))
        require(allow and not relative.startswith((".git/", ".agents/", ".codex/")),
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
                "reject unowned candidate, final, archive, native, or holdout path")
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
                    "reject concurrently mutated immutable frozen owner: " + relative)
            raw = b"".join(chunks)
            require(digest(raw) == checked_sha(expected_sha256, relative),
                    "reject substituted complete frozen owner digest: " + relative)
            if relative == INPUT:
                require(self.apply and self.source_reads == 0,
                        "candidate source may be read once only during root apply")
                self.source_reads += 1
            else:
                self.public_reads += 1
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
        require(self.apply and self.source_reads == 1 and not self.output_opened,
                "authorize exactly one new root-only corrected C bridge")
        require(type(raw) is bytes and len(raw) == OUTPUT_BYTES
                and digest(raw) == OUTPUT_SHA256,
                "reject non-frozen corrected bridge before workspace mutation")
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
                        "reject durable corrected bridge readback digest")
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


def transform(source: bytes, exact: bool = False) -> bytes:
    require(type(source) is bytes, "derive correction only from complete C bytes")
    require(ORIGINAL_RESTORE.count(RESTORE_CALL) == 1
            and ORIGINAL_EXPORTER.count(EXPORTER_FALLBACK) == 1,
            "require exact unambiguous correction insertion anchors")
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA256,
                "reject unauthenticated complete no-introspection bridge")
    require(source.count(ORIGINAL_RESTORE) == 1
            and source.count(ORIGINAL_EXPORTER) == 1,
            "require exactly one complete exception-restorer and exporter branch")
    require(source.index(ORIGINAL_RESTORE) < source.index(ORIGINAL_EXPORTER),
            "reject reordered exception-restorer and exporter branch")
    require(source.count(b"rust_bound_get_signature") == 0
            and source.count(b'PyImport_ImportModule("inspect")') == 0,
            "preserve the predecessor's no-external-introspection correction")
    for anchor, count in PRESERVED_COUNTS:
        require(source.count(anchor) == count,
                "reject missing, duplicated, or drifted preserved C anchor")
    result = source.replace(ORIGINAL_RESTORE, CORRECTED_RESTORE, 1)
    result = result.replace(ORIGINAL_EXPORTER, CORRECTED_EXPORTER, 1)
    require(result.count(CORRECTED_RESTORE) == 1
            and result.count(CORRECTED_EXPORTER) == 1,
            "require exactly two complete byte-anchored owned corrections")
    require(result.replace(CORRECTED_EXPORTER, ORIGINAL_EXPORTER, 1)
            .replace(CORRECTED_RESTORE, ORIGINAL_RESTORE, 1) == source,
            "require byte-exact reversible correction at exactly the two owned sites")
    require(len(result) == len(source) + len(RESTORE_INSERTION)
            + len(EXPORTER_INSERTION), "reject bytes changed outside the two sites")
    require(result.count(b"PyObject_Length(replacement)")
            == source.count(b"PyObject_Length(replacement)") + 1,
            "require exactly one message-gated replacement length probe")
    require(result.count(b'"bad escape (end of pattern)"')
            == source.count(b'"bad escape (end of pattern)"') + 1,
            "require exact trailing-escape message identity")
    require(result.count(b"state->template_helper, validation_arguments, 3, NULL") == 1,
            "require validate-only exporter helper vectorcall and exact arity")
    require(result.count(b"PyObject_GetBuffer(") == source.count(b"PyObject_GetBuffer(")
            and result.count(b"PyBuffer_Release(") == source.count(b"PyBuffer_Release(")
            and result.count(b"PyBUF_SIMPLE") == source.count(b"PyBUF_SIMPLE")
            and result.count(b"rust_subject_open(") == source.count(b"rust_subject_open(")
            and result.count(b"PyImport_ImportModule(")
            == source.count(b"PyImport_ImportModule("),
            "preserve exporter flags, acquisition lifetimes, imports, and subject sites")
    for anchor, count in PRESERVED_COUNTS:
        require(result.count(anchor) == count,
                "preserve native descriptors, capture clamping, and no-introspection")
    if exact:
        require(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
                "reject drift in exact predicted immutable corrected bridge")
    return result


def synthetic_source() -> bytes:
    return b"".join((
        b"static PyObject *rust_match_expand(RustMatch *match, PyObject *template);\n",
        b"static int rust_output_capture(\n",
        b"size_t first = begin > capture.length ? capture.length : begin;\n",
        b"size_t finish = end > capture.length ? capture.length : end;\n",
        b"PyDescr_NewMethod(pattern, NULL);\n",
        ORIGINAL_RESTORE,
        b"static PyObject *rust_normalize_expand_buffer(PyObject *template) {\n",
        b"PyObject_GetBuffer(template, &view, PyBUF_SIMPLE);\n",
        b"PyBuffer_Release(&view);\n}\n",
        b"static PyObject *rust_match_expand(RustMatch *match, PyObject *template) {\n",
        b"rust_subject_open(&subject, NULL, match->string, 0);\n",
        ORIGINAL_EXPORTER,
        b"}\n",
    ))


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
    require(type(error) is WitnessPatternError,
            "restore model must preserve an owned PatternError")
    if error.msg == TRAILING_ESCAPE:
        len(template)
    raise WitnessPatternError(error.msg, template, error.pos)


def validate_model(template: WitnessTemplate, events: list[str]) -> object:
    events.append("template-helper:validate-only")
    if template.text == MALFORMED_NAMED_TEMPLATES[0]:
        raise WitnessPatternError("missing group name", template, 10)
    if template.text == MALFORMED_NAMED_TEMPLATES[1]:
        raise WitnessPatternError("missing >, unterminated name", template, 10)
    if template.text.endswith("\\"):
        raise WitnessPatternError(TRAILING_ESCAPE, template, len(template.text) - 1)
    return True


def expand_model(template: WitnessTemplate, events: list[str]) -> str:
    events.append("buffer-acquire:template:outer:PyBUF_SIMPLE")
    normalized = template.text
    events.append("buffer-release:template:outer")
    try:
        validate_model(template, events)
    except WitnessPatternError as error:
        restore_model(error, template)
    events.append("template-helper:expand")
    if "\\g<word>" in normalized:
        events.append("match.group:word")
        events.append("buffer-acquire:subject:outer")
        events.append("buffer-release:subject:outer")
    return normalized


def substitution_model(template: WitnessTemplate, position: int,
                       events: list[str]) -> None:
    events.append("template-helper:parse")
    restore_model(WitnessPatternError(TRAILING_ESCAPE, template, position), template)


def targeted_records() -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    overlap: list[dict] = []

    def trailing(operation: str, shape: str, mutation: str,
                 index: int, collection: list[dict]) -> None:
        events: list[str] = []
        template = WitnessTemplate("outer\\", events, mutation)
        try:
            if operation == "expand":
                expand_model(template, events)
            else:
                substitution_model(template, 5, events)
        except WitnessPatternError as error:
            require(error.msg == TRAILING_ESCAPE and error.pattern is template
                    and error.pos == 5,
                    "preserve original nested error message, object, and position")
        else:
            raise FreezeError("missing synthetic trailing-escape PatternError")
        require(events.count("length-probe:template:outer") == 1,
                "require exactly one trailing-escape replacement length probe")
        require(not any(item.startswith("match.group:")
                        or item.startswith("buffer-acquire:subject:")
                        for item in events),
                "reject capture lookup or subject reacquisition before malformed error")
        collection.append({"case": index, "operation": operation, "shape": shape,
                           "mutation": mutation, "message": error_message(events),
                           "position": 5, "events": events})

    for operation in ("module.sub", "module.subn", "pattern.sub", "pattern.subn"):
        for index in range(8):
            trailing(operation, "template-only-direct", "stable", index, records)

    for shape, mutation in (("template-only-direct", "stable"),
                            ("both-direct", "stable"),
                            ("template-only-direct", "mutate")):
        for index in range(8):
            trailing("expand", shape, mutation, index, records)

    for text in MALFORMED_NAMED_TEMPLATES:
        require(len(text) in (13, 19), "require exact nested visible malformed lengths")
        for mutation in ("stable", "mutate"):
            for index in range(8):
                events: list[str] = []
                template = WitnessTemplate(text, events, mutation, fail_length=True)
                try:
                    expand_model(template, events)
                except WitnessPatternError as error:
                    require(error.pattern is template and error.pos == 10
                            and error.msg != TRAILING_ESCAPE,
                            "preserve malformed named-template original nested position")
                    message = error.msg
                else:
                    raise FreezeError("missing malformed named-template PatternError")
                require(events == ["buffer-acquire:template:outer:PyBUF_SIMPLE",
                                   "buffer-release:template:outer",
                                   "template-helper:validate-only"],
                        "malformed named template must perform zero probes and captures")
                records.append({"case": index, "operation": "expand",
                                "shape": "malformed-named-template",
                                "mutation": mutation, "visible_length": len(text),
                                "message": message, "position": 10,
                                "events": events})

    for operation in ("module.sub", "module.subn", "pattern.sub", "pattern.subn"):
        for index in range(8):
            trailing(operation, "both-direct", "stable", index, overlap)

    require(len(records) == 88 and len(overlap) == 32,
            "require disjoint B56+C32 denominator and separate explicit A32 overlap")
    require(sum(item["operation"] != "expand" for item in records) == 32
            and sum(item["operation"] == "expand"
                    and item["shape"] != "malformed-named-template"
                    for item in records) == 24
            and sum(item["shape"] == "malformed-named-template"
                    for item in records) == 32,
            "require exact 32 substitution + 24 expansion + 32 malformed partition")
    return records, overlap


def error_message(events: list[str]) -> str:
    require("length-probe:template:outer" in events,
            "require actual modeled outer length side effect")
    return TRAILING_ESCAPE


def synthetic_tests(wall: SourceWall) -> dict:
    source = synthetic_source()
    output = transform(source)
    require(len(output) - len(source) == len(RESTORE_INSERTION)
            + len(EXPORTER_INSERTION), "require exact synthetic two-site C delta")
    records, overlap = targeted_records()
    rejected = 0

    def reject(call, reason: str) -> None:
        nonlocal rejected
        try:
            call()
        except (FreezeError, OSError, TypeError, ValueError, WitnessProbeFailure):
            rejected += 1
            return
        raise FreezeError("hostile source-only control unexpectedly passed: " + reason)

    reject(lambda: transform(source.replace(ORIGINAL_RESTORE, b"", 1)),
           "missing complete owned error restorer")
    reject(lambda: transform(source.replace(ORIGINAL_RESTORE,
                                            ORIGINAL_RESTORE * 2, 1)),
           "duplicated complete owned error restorer")
    reject(lambda: transform(source.replace(ORIGINAL_EXPORTER, b"", 1)),
           "missing complete owned exporter fallback")
    reject(lambda: transform(source.replace(ORIGINAL_EXPORTER,
                                            ORIGINAL_EXPORTER * 2, 1)),
           "duplicated complete owned exporter fallback")
    reject(lambda: transform(source.replace(RESTORE_CALL,
                                            b"    PyObject *restored = NULL;\n", 1)),
           "substituted error reconstruction")
    reject(lambda: transform(source.replace(EXPORTER_FALLBACK,
                                            b"            return NULL;\n", 1)),
           "substituted owned exporter helper")
    for anchor, _count in PRESERVED_COUNTS:
        reject(lambda item=anchor: transform(source.replace(item, b"", 1)),
               "missing preserved native, exporter, or capture-clamp surface")
    for index in range(0, len(ORIGINAL_RESTORE), 41):
        altered = (ORIGINAL_RESTORE[:index]
                   + bytes((ORIGINAL_RESTORE[index] ^ 1,))
                   + ORIGINAL_RESTORE[index + 1:])
        reject(lambda value=altered: transform(source.replace(ORIGINAL_RESTORE,
                                                             value, 1)),
               "mutated complete owned error-restorer bytes")
    for index in range(0, len(ORIGINAL_EXPORTER), 29):
        altered = (ORIGINAL_EXPORTER[:index]
                   + bytes((ORIGINAL_EXPORTER[index] ^ 1,))
                   + ORIGINAL_EXPORTER[index + 1:])
        reject(lambda value=altered: transform(source.replace(ORIGINAL_EXPORTER,
                                                             value, 1)),
               "mutated complete owned exporter-branch bytes")
    for payload in (b'{"x":1,"x":2}', b"NaN", b"1.2", b"01",
                    b'{"x":"\\ud800"}', b'{"x":1} trailing'):
        reject(lambda value=payload: StrictJSON(value).decode(), "unsafe evidence JSON")

    for message in ("missing group name", "missing >, unterminated name",
                    "bad character in group name", "unknown group name"):
        events: list[str] = []
        template = WitnessTemplate("<\\g<name", events, "mutate", fail_length=True)
        try:
            restore_model(WitnessPatternError(message, template, 29), template)
        except WitnessPatternError as error:
            require(error.msg == message and error.pattern is template
                    and error.pos == 29 and not events,
                    "only the exact trailing-escape message may probe replacement")
        else:
            raise FreezeError("missing synthetic non-trailing PatternError")

    for operation in ("module.sub", "pattern.subn", "expand"):
        events = []
        template = WitnessTemplate("outer\\", events, "stable", fail_length=True)
        if operation == "expand":
            reject(lambda value=template, trace=events: expand_model(value, trace),
                   "expand replacement length failure must supersede PatternError")
        else:
            reject(lambda value=template, trace=events:
                   substitution_model(value, 97, trace),
                   "substitution replacement length failure must supersede PatternError")
        require(events.count("length-probe:template:outer") == 1,
                "require exactly one visible failed length probe")

    valid_events: list[str] = []
    valid = WitnessTemplate("<\\g<word>>", valid_events)
    require(expand_model(valid, valid_events) == "<\\g<word>>"
            and valid_events == ["buffer-acquire:template:outer:PyBUF_SIMPLE",
                                 "buffer-release:template:outer",
                                 "template-helper:validate-only",
                                 "template-helper:expand", "match.group:word",
                                 "buffer-acquire:subject:outer",
                                 "buffer-release:subject:outer"],
            "preserve successful exporter normalization, capture, and buffer ownership")

    reject(lambda: wall.parent(INPUT), "candidate source before root-only apply")
    reject(lambda: wall.parent("oracle/phase3/expanded-sealed-holdout-v2.json"),
           "invalidated final holdout proposal")
    reject(lambda: wall.parent(LEDGER[:-5] + ".json.gz"), "compressed failure archive")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved primitive unticketed candidate source")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level candidate read")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "direct candidate source read")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "workspace directory mutation")
    reject(lambda: time.time(), "timing sample")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native library")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None), "compiler")
    reject(lambda: sys.audit("socket.connect", None, None), "network")
    require(rejected >= 65 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "require exhaustive zero-candidate-read zero-write hostile controls")
    no_matching_imports()
    return {
        "synthetic_source_bytes": len(source),
        "synthetic_output_bytes": len(output),
        "exact_added_bytes": len(RESTORE_INSERTION) + len(EXPORTER_INSERTION),
        "targeted_record_count": len(records),
        "targeted_records_sha256": digest(canonical(records).encode("utf-8")),
        "disjoint_probe_missing_records": 56,
        "substitution_template_only_stable_records": 32,
        "match_expand_trailing_escape_records": 24,
        "malformed_named_template_records": 32,
        "malformed_visible_lengths": [13, 19],
        "separate_substitution_ordering_overlap_records": len(overlap),
        "separate_substitution_ordering_overlap_records_sha256":
            digest(canonical(overlap).encode("utf-8")),
        "overlap_included_in_targeted_record_count": False,
        "hostile_controls_rejected": rejected,
        "length_failure_supersedes_saved_pattern_error": True,
        "nested_pattern_error_position_preserved": True,
        "malformed_named_template_length_probe_count": 0,
        "malformed_named_template_capture_lookup_count": 0,
        "malformed_named_template_subject_reacquisition_count": 0,
        "candidate_source_reads": 0,
        "native_libraries_loaded": 0,
        "clock_samples": 0,
        "workspace_mutations": 0,
        "final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
        "runtime_non_delegation": "NOT ESTABLISHED",
    }


def value(document: object, name: str, expected: object) -> None:
    require(type(document) is dict and document.get(name) == expected,
            "reject incomplete or substituted authenticated evidence: " + name)


def authenticate_ledger(raw: bytes) -> dict:
    ledger = StrictJSON(raw).decode()
    value(ledger, "schema", "rebar-owned-repaired-rust-original-campaign-v25-"
                            "durable-publication-receipt")
    value(ledger, "status", "PASS")
    value(ledger, "publication_status", "PASS")
    value(ledger, "publication_pass_means", "DURABLE PUBLICATION ONLY")
    value(ledger, "candidate_status", "FAIL")
    value(ledger, "candidate_qualified", False)
    value(ledger, "suite_count", 13)
    value(ledger, "attempted_suite_count", 13)
    value(ledger, "completed_suite_count", 13)
    value(ledger, "case_execution_denominator", 31237)
    value(ledger, "semantic_mismatch_count", 1352)
    value(ledger, "verified_passing_case_count", 15877)
    value(ledger, "named_private_waiver_count", 13)
    value(ledger, "holdout", "NOT OPENED")
    value(ledger, "hidden_cases_read", 0)
    value(ledger, "clock_samples", 0)
    value(ledger, "actual_v25_build_archive_read_count", 0)
    value(ledger, "actual_v25_build_archive_gzip_inflation_count", 0)
    value(ledger, "winner_selected", False)
    suites = ledger["suite_integrity"]
    require(type(suites) is list and len(suites) == 13,
            "require all thirteen immutable original V25 suite ledger rows")
    indexed: dict[str, dict] = {}
    for suite in suites:
        require(type(suite) is dict and type(suite.get("suite")) is str,
                "reject malformed authenticated original V25 suite row")
        name = suite["suite"]
        require(name not in indexed, "reject duplicate original V25 suite row")
        indexed[name] = suite
        value(suite, "fully_observed", True)
        value(suite, "actual_worker_started", True)
    substitution = indexed["substitution_v2"]
    shape = indexed["shape_v2"]
    value(substitution, "case_execution_denominator", 5120)
    value(substitution, "mismatch_count", 240)
    value(substitution, "verified_passing_case_count", 0)
    value(substitution, "failure_class", "SEMANTIC MISMATCH")
    value(shape, "case_execution_denominator", 10240)
    value(shape, "mismatch_count", 1112)
    value(shape, "verified_passing_case_count", 0)
    value(shape, "failure_class", "SEMANTIC MISMATCH")
    require(sum(suite["case_execution_denominator"] for suite in suites) == 31237
            and sum(suite["mismatch_count"] for suite in suites) == 1352
            and sum(suite["verified_passing_case_count"] for suite in suites) == 15877,
            "preserve full authentic denominators, failures, and verified passes")
    return {"receipt_path": LEDGER, "receipt_sha256": LEDGER_SHA256,
            "publication_status": "PASS", "candidate_status": "FAIL",
            "suite_count": 13, "case_execution_denominator": 31237,
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "substitution_v2_mismatch_count": 240,
            "shape_v2_mismatch_count": 1112,
            "named_private_waiver_count": 13,
            "holdout": "NOT OPENED"}


def validate_contract(document: object, source_sha: str, protocol_sha: str) -> None:
    require(type(document) is dict, "require complete frozen correction contract")
    value(document, "schema", SCHEMA)
    value(document, "version", 1)
    value(document, "family", "rust")
    value(document, "phase", "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS")
    value(document, "status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; "
                              "NOT BUILT; NOT RUN")
    value(document, "source", {"path": SOURCE, "sha256": source_sha})
    value(document, "protocol", {"path": PROTOCOL, "sha256": protocol_sha})
    correction = document["exact_expand_probe_correction"]
    for key, expected in (
            ("input_path", INPUT), ("input_sha256", INPUT_SHA256),
            ("input_bytes", INPUT_BYTES), ("input_device", DEVICE),
            ("input_inode", INPUT_INODE), ("input_mode", "0600"),
            ("target_path", TARGET), ("target_sha256", OUTPUT_SHA256),
            ("target_bytes", OUTPUT_BYTES),
            ("source_delta_bytes", len(RESTORE_INSERTION) + len(EXPORTER_INSERTION)),
            ("replacement_site_count", 2),
            ("length_probe_error_message", TRAILING_ESCAPE),
            ("length_probe_message_equality_required", True),
            ("other_pattern_errors_probe_length", False),
            ("original_nested_error_position_preserved", True),
            ("length_probe_failure_supersedes_pattern_error", True),
            ("exporter_validation_scope", "MATCH_EXPAND_NON_BYTES_BUFFER_EXPORTER"),
            ("exporter_validation_helper_arity", 3),
            ("exporter_validation_flag", True),
            ("malformed_named_template_length_probe_count", 0),
            ("malformed_named_template_capture_lookup_count", 0),
            ("malformed_named_template_subject_reacquisition_count", 0),
            ("exporter_buffer_flags_preserved", "PyBUF_SIMPLE"),
            ("exporter_lifetimes_preserved", True),
            ("capture_clamp_correction_retained", True),
            ("no_external_introspection_correction_retained", True),
            ("stdlib_matching_delegation_added", False),
            ("external_regex_dependency_added", False),
            ("runtime_non_delegation", "NOT ESTABLISHED"),
            ("candidate_built", False), ("candidate_imported", False),
            ("candidate_matching", "NOT RUN"), ("candidate_qualified", False)):
        value(correction, key, expected)
    targeted = document["exact_targeted_original_shape_partition"]
    for key, expected in (
            ("targeted_record_count", 88),
            ("disjoint_missing_trailing_escape_probe_records", 56),
            ("substitution_template_only_direct_stable_records", 32),
            ("match_expand_trailing_escape_records", 24),
            ("match_expand_template_only_stable_records", 8),
            ("match_expand_both_direct_stable_records", 8),
            ("match_expand_template_only_mutate_records", 8),
            ("malformed_named_template_records", 32),
            ("malformed_visible_lengths", [13, 19]),
            ("malformed_stable_records", 16),
            ("malformed_mutate_records", 16),
            ("separate_substitution_ordering_overlap_records", 32),
            ("overlap_included_in_targeted_record_count", False),
            ("separate_substitution_ordering_owned_by_another_correction", True)):
        value(targeted, key, expected)
    ledger = document["immutable_original_v25_ledger"]
    for key, expected in (("receipt_path", LEDGER), ("receipt_sha256", LEDGER_SHA256),
                          ("receipt_bytes", LEDGER_BYTES),
                          ("receipt_device", DEVICE), ("receipt_inode", LEDGER_INODE),
                          ("publication_status", "PASS"),
                          ("candidate_status", "FAIL"), ("suite_count", 13),
                          ("case_execution_denominator", 31237),
                          ("semantic_mismatch_count", 1352),
                          ("verified_passing_case_count", 15877),
                          ("substitution_v2_mismatch_count", 240),
                          ("shape_v2_mismatch_count", 1112),
                          ("named_private_waiver_count", 13)):
        value(ledger, key, expected)
    wall = document["physical_source_wall"]
    for key, expected in (("installed_before_owner_reads", True),
                          ("descriptor_relative_o_nofollow", True),
                          ("authenticated_public_evidence_receipt_count", 1),
                          ("source_mode_candidate_source_reads", 0),
                          ("self_test_candidate_source_reads", 0),
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
                          ("final_holdout_open_allowed", False),
                          ("clock_access_allowed", False)):
        value(wall, key, expected)
    effects = document["source_only_effects"]
    for key in ("candidate_source_files_read", "candidate_executions",
                "candidate_imports", "candidate_workers_started",
                "compiler_processes_started", "native_binary_files_opened",
                "native_libraries_loaded", "compressed_archives_opened",
                "compressed_archives_inflated", "holdout_cases_opened",
                "holdout_cases_generated", "clock_samples", "network_requests",
                "workspace_mutations"):
        value(effects, key, 0)
    value(effects, "runtime_non_delegation", "NOT ESTABLISHED")
    value(effects, "candidate_correctness", "NOT MEASURED")
    value(effects, "candidate_matching", "NOT RUN")
    value(effects, "final_holdout", "INVALIDATED; REKEYED SUCCESSOR REQUIRED")
    value(effects, "performance", "NOT MEASURED")
    value(effects, "winner_selected", False)


def parse_arguments(arguments: list[str]) -> dict:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require explicit immutable command arguments")
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
            "require exactly one self-test, frozen-source verification, or root apply")
    mode = modes[0]
    if mode == "--self-test":
        require(set(parsed) == {mode}, "self-test takes no owner or root arguments")
    elif mode == "--verify-source":
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256"},
                "source verification requires exactly the frozen owner SHA-256 triple")
    else:
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256", "--root-authorized",
                                "--frozen-commit", "--pushed-commit"},
                "root-only apply requires frozen owners and identical pushed commit")
        for label in ("--frozen-commit", "--pushed-commit"):
            commit = parsed[label]
            require(type(commit) is str and len(commit) == 40
                    and all(char in "0123456789abcdef" for char in commit),
                    "require complete lowercase frozen commit: " + label)
        require(parsed["--frozen-commit"] == parsed["--pushed-commit"],
                "refuse root materialization until the frozen commit has been pushed")
    for label in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if label in parsed:
            checked_sha(parsed[label], label)
    return parsed


def zero_effects(wall: SourceWall, mode: str) -> dict:
    return {"mode": mode, "approved_public_owner_reads": wall.public_reads,
            "candidate_source_files_read": wall.source_reads,
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_workers_started": 0, "compiler_processes_started": 0,
            "native_binary_files_opened": 0, "native_libraries_loaded": 0,
            "compressed_archives_opened": 0, "compressed_archives_inflated": 0,
            "holdout_cases_opened": 0, "holdout_cases_generated": 0,
            "clock_samples": 0, "network_requests": 0,
            "workspace_mutations": wall.workspace_mutations,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_correctness": "NOT MEASURED",
            "candidate_matching": "NOT RUN", "candidate_qualified": False,
            "final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "performance": "NOT MEASURED", "winner_selected": False}


def main(arguments: list[str]) -> dict:
    options = parse_arguments(arguments)
    apply = options.get("--apply") is True
    wall = SourceWall(apply)
    no_matching_imports()
    wall.install()
    if options.get("--self-test") is True:
        tests = synthetic_tests(wall)
        require(wall.public_reads == 0 and wall.source_reads == 0
                and wall.workspace_mutations == 0 and wall.root is None,
                "self-test must read no owners or candidates and mutate nothing")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "synthetic_controls": tests, "effects": zero_effects(wall, "SELF-TEST")}

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
    original_ledger = authenticate_ledger(
        wall.read(LEDGER, LEDGER_BYTES, LEDGER_INODE, LEDGER_SHA256)
    )
    require(wall.public_reads == 4 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "authenticate only three frozen owners and one original plaintext ledger")
    if not apply:
        tests = synthetic_tests(wall)
        no_matching_imports()
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; SOURCE FROZEN; NO CANDIDATE SOURCE READ",
                "source_sha256": source_sha, "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "authenticated_original_ledger": original_ledger,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "synthetic_controls": tests,
                "effects": zero_effects(wall, "SOURCE FREEZE")}

    require(transform(synthetic_source()) and wall.source_reads == 0,
            "require complete synthetic correction before root-only source access")
    original = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA256)
    corrected = transform(original, exact=True)
    wall.materialize(corrected)
    no_matching_imports()
    require(wall.source_reads == 1 and wall.workspace_mutations == 2,
            "materialize exactly one exclusive directory and one corrected C file")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; EXACT EXPAND PROBE CORRECTION; NOT BUILT; NOT RUN",
            "frozen_commit": options["--frozen-commit"],
            "pushed_commit": options["--pushed-commit"],
            "source_sha256": source_sha, "protocol_sha256": protocol_sha,
            "contract_sha256": contract_sha, "input_path": INPUT,
            "input_sha256": INPUT_SHA256, "input_bytes": INPUT_BYTES,
            "target_path": TARGET, "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES,
            "exact_added_bytes": len(RESTORE_INSERTION) + len(EXPORTER_INSERTION),
            "targeted_record_count": 88,
            "separate_substitution_ordering_overlap_records": 32,
            "effects": zero_effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError) as error:
        sys.stderr.write("rust-expand-probe-semantics-v1: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
