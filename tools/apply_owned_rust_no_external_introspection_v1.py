#!/usr/bin/env python3
"""Freeze one first-party Rust private-introspection removal without running it.

Self-test and source verification never read a candidate source.  The existing
capture-clamp bridge can be read exactly once only in the separately authorized,
exclusive root materialization mode after an identical frozen/pushed commit.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("source-only introspection freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
DEVICE = 2064
SCHEMA = "rebar-owned-rust-no-external-introspection-v1-source-freeze"
SOURCE = "tools/apply_owned_rust_no_external_introspection_v1.py"
PROTOCOL = "oracle/phase2/RUST-NO-EXTERNAL-INTROSPECTION-V1.md"
CONTRACT = "oracle/phase2/rust-no-external-introspection-v1.json"
INPUT = "candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c"
TARGET_DIRECTORY = "candidates/rust/variants/no_external_introspection_v1"
TARGET = TARGET_DIRECTORY + "/py_bridge.c"
INPUT_SHA256 = "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54"
INPUT_BYTES = 178805
INPUT_INODE = 526064
OUTPUT_SHA256 = "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7"
OUTPUT_BYTES = 177146
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 200_000
MAX_JSON_DEPTH = 80
V4_RECEIPT_SHA256 = "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19"
V25_ROOT_SHA256 = "e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2"
V25_PUBLICATION_SHA256 = "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc"

# Only public tools, documentation, contracts, and published evidence.  Candidate
# source INPUT is intentionally absent and is authorized exclusively in --apply.
# role, relative path, SHA-256, bytes, inode (device 2064; mode 0600; nlink 1).
OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("v4_source", "tools/audit_candidate_runtime_non_delegation_v4.py",
     "597f2f1156d773a42e32103ef7370e8552a416756910c013cdcd0cfc34d39b02", 121807, 429582),
    ("v4_protocol", "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md",
     "6c3bd6b2ccabe3ab240771d743afce5b32f1de17a510bedd835e867c5cea7826", 5325, 526087),
    ("v4_contract", "oracle/phase2/runtime-non-delegation-v4.json",
     "edc3ac8866da7afb5934b56fbcbff38a908e5109f7975f998753b479aa7bc672", 7266, 526086),
    ("v4_actual_failure", "oracle/phase2/evidence/"
     "runtime-non-delegation-v4-actual-source-audit-failure.json",
     V4_RECEIPT_SHA256, 20985, 526140),
    ("v25_source", "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py",
     "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408", 186263, 429530),
    ("v25_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md",
     "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85", 7140, 525993),
    ("v25_contract", "oracle/phase2/rust-capture-clamp-source-build-v25.json",
     "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a", 229419, 526066),
    ("v25_publication", "oracle/phase2/evidence/native-source-build-v25-rust-"
     "phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json",
     V25_PUBLICATION_SHA256, 5231, 526084),
    ("v25_root", "oracle/phase2/evidence/native-source-build-v25-rust-"
     "phase2-v25-rust-capture-clamp-v1-root-provenance-root-provenance-receipt.json",
     V25_ROOT_SHA256, 61798, 526085),
    ("capture_clamp_source", "tools/apply_owned_rust_capture_clamp_semantics_v1.py",
     "ff4b45f370bb6df1a3693cb1046031df93f3dffb336f4cca695768a1adb34fb7", 71522, 429579),
    ("capture_clamp_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SEMANTICS-V1.md",
     "15bd3b25b3f86638ddcb45cbc11d962341a905903a4cd52a632f6c3f1a078ff9", 4645, 526033),
    ("capture_clamp_contract", "oracle/phase2/rust-capture-clamp-semantics-v1.json",
     "46344723f24c65c123c4550c9652b3547866a2ae1a8419444d3359eb048294c6", 11342, 526034),
)

FUNCTION = b"""static PyObject *rust_bound_get_signature(RustBoundMethod *method, void *closure) {
    (void)closure;
    if (method->signature != NULL) return Py_NewRef(method->signature);
    PyObject *functools = PyImport_ImportModule("functools");
    if (functools == NULL) return NULL;
    PyObject *partial_type = PyObject_GetAttrString(functools, "partial");
    Py_DECREF(functools);
    if (partial_type == NULL) return NULL;
    Py_ssize_t count = Py_SIZE(method);
    PyObject *arguments = PyTuple_New(count + 1);
    if (arguments == NULL) {
        Py_DECREF(partial_type);
        return NULL;
    }
    PyTuple_SET_ITEM(arguments, 0, Py_NewRef(method->function));
    for (Py_ssize_t index = 0; index < count; index++) PyTuple_SET_ITEM(arguments, index + 1, Py_NewRef(method->prefix[index]));
    PyObject *partial = PyObject_CallObject(partial_type, arguments);
    Py_DECREF(arguments);
    Py_DECREF(partial_type);
    if (partial == NULL) return NULL;
    PyObject *inspect = PyImport_ImportModule("inspect");
    if (inspect == NULL) {
        Py_DECREF(partial);
        return NULL;
    }
    PyObject *signature_function = PyObject_GetAttrString(inspect, "signature");
    Py_DECREF(inspect);
    if (signature_function == NULL) {
        Py_DECREF(partial);
        return NULL;
    }
    PyObject *signature = PyObject_CallOneArg(signature_function, partial);
    Py_DECREF(signature_function);
    Py_DECREF(partial);
    if (signature == NULL) return NULL;
    method->signature = signature;
    return Py_NewRef(signature);
}

"""
GETSET_ROW = (
    b'    {"__signature__", (getter)rust_bound_get_signature, NULL, '
    b'"The Python-compatible bound method signature.", NULL},\n'
)
REPR_ANCHOR = b"static PyObject *rust_bound_repr(RustBoundMethod *method) {\n"
GETSET_TERMINATOR = b"    {NULL, NULL, NULL, NULL, NULL},\n};\n\nstatic PyMemberDef rust_bound_members[]"
PATTERN_METHODS = b"static PyMethodDef rust_pattern_methods[] = {\n"
DESCRIPTORS = b"static PyObject *bridge_pattern_descriptors(\n"
NEXT_PUBLIC_DESCRIPTOR = b"static PyObject *bridge_pattern_type(\n"
CAPTURE_START = b"static int rust_output_capture(\n"
CLAMP_FIRST = b"size_t first = begin > capture.length ? capture.length : begin;"
CLAMP_FINISH = b"size_t finish = end > capture.length ? capture.length : end;"
PRESERVED_COUNTS = (
    (b"static PyObject *rust_bound_call(", 1),
    (b"static PyObject *rust_bound_get_self(", 1),
    (b"static PyObject *rust_bound_get_name(", 1),
    (b"static PyObject *rust_bound_get_qualname(", 1),
    (b"static PyObject *rust_bound_get_doc(", 1),
    (REPR_ANCHOR, 1),
    (b"static PyObject *bridge_bind(", 1),
    (PATTERN_METHODS, 1),
    (DESCRIPTORS, 1),
    (b"PyDescr_NewMethod(", 1),
    (b"Py_CLEAR(method->signature);", 2),
    (b"Py_VISIT(method->signature);", 1),
    (CAPTURE_START, 1),
    (CLAMP_FIRST, 1),
    (CLAMP_FINISH, 1),
)


class FreezeError(Exception):
    """Reject substituted evidence, non-exact source, or unauthorized effects."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash genuine complete bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require complete lowercase SHA-256: " + name)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "JSON string must be genuine text")
    replacements = {"\"": "\\\"", "\\": "\\\\", "\b": "\\b",
                    "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for char in value:
        point = ord(char)
        require(not 0xD800 <= point <= 0xDFFF, "reject unpaired JSON surrogate")
        result.append(replacements.get(char, "\\u" + format(point, "04x")
                      if point < 32 else char))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive JSON depth")
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
    raise FreezeError("reject nonfinite or unsupported evidence JSON")

class StrictJSON:
    """Bounded duplicate-rejecting JSON without importing json or regex."""

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
                    "reject invalid JSON Unicode escape")
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
        require(depth <= MAX_JSON_DEPTH, "reject deep evidence JSON")
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
            "reject matcher, candidate, worker, network, or native loader import")


class SourceWall:
    """Deny-default, ticketed O_NOFOLLOW descriptor-relative public ownership."""

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
        raise FreezeError("source-only physical wall rejected " + reason)

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            flags = args[2] if len(args) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed-source-native-private-or-write-open")
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
                "reject substituted frozen workspace root")
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
                "reject unowned, hidden, private, or candidate directory")
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
                and descriptor != self.root,
                "reject foreign or root descriptor closure")
        self.native_close(descriptor)
        del self.live[descriptor]

    def parent(self, relative: str) -> tuple[int, list[int], str]:
        require(type(relative) is str and relative in self.allowed,
                "reject unowned plaintext candidate, source, or holdout path")
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
                    "reject extra frozen owner bytes: " + relative)
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
                        "candidate source may be read once in root-only apply")
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
            output = self.child_directory(descriptor, name)
            return output
        finally:
            for item in reversed(stack):
                self.close(item)

    def materialize(self, raw: bytes) -> None:
        require(self.apply and self.source_reads == 1 and not self.output_opened,
                "authorize exactly one new root-only corrected bridge")
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
                left = OUTPUT_BYTES
                while left:
                    part = self.native_read(readback, min(left, 65536))
                    require(bool(part), "reject incomplete durable bridge readback")
                    chunks.append(part)
                    left -= len(part)
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
        require(not self.installed, "install immutable source wall exactly once")
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


def public_descriptor_slice(source: bytes) -> bytes:
    require(source.count(PATTERN_METHODS) == 1 and source.count(DESCRIPTORS) == 1
            and source.count(NEXT_PUBLIC_DESCRIPTOR) == 1,
            "require unique first-party public native descriptor surfaces")
    start = source.index(PATTERN_METHODS)
    middle = source.index(DESCRIPTORS)
    finish = source.index(NEXT_PUBLIC_DESCRIPTOR)
    require(start < middle < finish, "reject reordered public descriptor surfaces")
    return source[start:finish]


def transform(source: bytes, exact: bool = False) -> bytes:
    require(type(source) is bytes, "derive correction only from complete C bytes")
    require(len(FUNCTION) == 1541 and len(GETSET_ROW) == 118,
            "reject drift in exact frozen private-only deletion lengths")
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA256,
                "reject unauthenticated complete capture-clamp bridge")
    require(source.count(FUNCTION) == 1 and source.count(GETSET_ROW) == 1,
            "require exactly one exact private getter and one exact getset row")
    require(source.count(GETSET_TERMINATOR) == 1,
            "require exactly one native bound-method getset terminator")
    for anchor, count in PRESERVED_COUNTS:
        require(source.count(anchor) == count,
                "reject missing, duplicated, or modified preserved first-party surface")
    require(source.count(b'PyImport_ImportModule("inspect")') == 1
            and source.count(b'PyImport_ImportModule("functools")') == 1,
            "require the exact sole private inspect/functools import chain")
    public_before = public_descriptor_slice(source)
    function_at = source.index(FUNCTION)
    row_at = source.index(GETSET_ROW)
    require(function_at < row_at, "reject reordered private signature surfaces")
    result = source[:function_at] + source[function_at + len(FUNCTION):]
    require(result.count(GETSET_ROW) == 1,
            "reject non-unique private signature getset after getter deletion")
    result = result.replace(GETSET_ROW, b"", 1)
    require(result.count(b"rust_bound_get_signature") == 0
            and result.count(b'PyImport_ImportModule("inspect")') == 0
            and result.count(b'PyImport_ImportModule("functools")') == 0,
            "reject surviving private or external introspection escape hatch")
    require(public_descriptor_slice(result) == public_before,
            "preserve public method descriptors, docstrings, and native signatures")
    for anchor, count in PRESERVED_COUNTS:
        require(result.count(anchor) == count,
                "preserve existing matching, binding, capture-clamp, and GC ownership")
    reversed_row = result.replace(GETSET_TERMINATOR,
                                  GETSET_ROW + GETSET_TERMINATOR, 1)
    reversed_source = reversed_row.replace(REPR_ANCHOR, FUNCTION + REPR_ANCHOR, 1)
    require(reversed_source == source,
            "require byte-exact reversible removal at precisely the two owned sites")
    require(len(result) == len(source) - len(FUNCTION) - len(GETSET_ROW),
            "reject non-exact source delta outside the two frozen deletions")
    if exact:
        require(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
                "reject drift in exact predicted exclusive corrected bridge")
    return result


def synthetic_source() -> bytes:
    return b"".join((
        PATTERN_METHODS, b'    {"search", NULL, 0, "search($self, /, string)"},\n};\n',
        DESCRIPTORS, b"    PyDescr_NewMethod(pattern, NULL);\n}\n",
        NEXT_PUBLIC_DESCRIPTOR, b"    return NULL;\n}\n",
        b"static PyObject *rust_bound_call(\n",
        b"static PyObject *rust_bound_get_self(\n",
        b"static PyObject *rust_bound_get_name(\n",
        b"static PyObject *rust_bound_get_qualname(\n",
        b"static PyObject *rust_bound_get_doc(\n",
        b"Py_CLEAR(method->signature);\nPy_CLEAR(method->signature);\n",
        b"Py_VISIT(method->signature);\n",
        CAPTURE_START, CLAMP_FIRST, b"\n", CLAMP_FINISH, b"\n",
        FUNCTION, REPR_ANCHOR,
        b"static PyGetSetDef rust_bound_getsets[] = {\n", GETSET_ROW,
        GETSET_TERMINATOR, b"[] = {};\n",
        b"static PyObject *bridge_bind(\n",
    ))


def synthetic_tests(wall: SourceWall) -> dict:
    source = synthetic_source()
    output = transform(source)
    require(len(source) - len(output) == 1659,
            "require exact synthetic private-only source delta")
    rejected = 0

    def reject(call, reason: str) -> None:
        nonlocal rejected
        try:
            call()
        except (FreezeError, OSError, TypeError, ValueError):
            rejected += 1
            return
        raise FreezeError("hostile source-only control unexpectedly passed: " + reason)

    reject(lambda: transform(source.replace(FUNCTION, b"", 1)), "missing getter")
    reject(lambda: transform(source.replace(FUNCTION, FUNCTION + FUNCTION, 1)),
           "duplicate getter")
    reject(lambda: transform(source.replace(GETSET_ROW, b"", 1)), "missing getset")
    reject(lambda: transform(source.replace(GETSET_ROW, GETSET_ROW * 2, 1)),
           "duplicate getset")
    reject(lambda: transform(source.replace(FUNCTION, FUNCTION.replace(
        b'"inspect"', b'"inspect_alias"', 1), 1)), "aliased private import")
    reject(lambda: transform(source.replace(FUNCTION, FUNCTION.replace(
        b'"functools"', b'"functools_alias"', 1), 1)), "aliased partial import")
    reject(lambda: transform(source.replace(REPR_ANCHOR, b"", 1)), "missing repr")
    reject(lambda: transform(source.replace(GETSET_TERMINATOR, b"", 1)),
           "missing getset sentinel")
    for anchor, _count in PRESERVED_COUNTS:
        reject(lambda item=anchor: transform(source.replace(item, b"", 1)),
               "removed preserved owned surface")
    for index in range(0, len(FUNCTION), 37):
        altered = FUNCTION[:index] + bytes((FUNCTION[index] ^ 1,)) + FUNCTION[index + 1:]
        reject(lambda changed=altered: transform(source.replace(FUNCTION, changed, 1)),
               "mutated private getter body")
    for payload in (b'{"x":1,"x":2}', b"NaN", b"1.2", b"01",
                    b'{"x":"\\ud800"}', b'{"x":1} trailing'):
        reject(lambda value=payload: StrictJSON(value).decode(), "unsafe evidence JSON")
    reject(lambda: wall.parent(INPUT), "candidate source path before root-only apply")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved primitive unticketed candidate read")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level candidate read")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "direct os candidate read")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "workspace directory mutation")
    reject(lambda: time.time(), "timing sample")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native library load")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None), "compiler")
    reject(lambda: sys.audit("socket.connect", None, None), "network")
    require(rejected >= 75 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "require exhaustive zero-candidate-read zero-write hostile controls")
    no_matching_imports()
    return {
        "synthetic_source_bytes": len(source),
        "synthetic_output_bytes": len(output),
        "exact_deleted_bytes": 1659,
        "private_function_deleted_bytes": 1541,
        "private_getset_row_deleted_bytes": 118,
        "hostile_controls_rejected": rejected,
        "candidate_source_reads": 0,
        "candidate_executions": 0,
        "native_libraries_loaded": 0,
        "clock_samples": 0,
        "workspace_mutations": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
    }


def value(document: object, name: str, expected: object) -> None:
    require(type(document) is dict and document.get(name) == expected,
            "reject incomplete or substituted authenticated evidence: " + name)


def authenticated_evidence(owners: dict[str, bytes]) -> dict:
    v4_contract = StrictJSON(owners["v4_contract"]).decode()
    value(v4_contract, "schema", "rebar-phase2-first-party-runtime-non-delegation-v4")
    value(v4_contract, "version", 4)
    value(v4_contract, "family_count", 6)
    current = v4_contract["current_source_findings"]
    value(current, "rust_native_bind_adapter_calls", 0)
    value(current, "rust_public_matching_delegation", "NOT PROVEN")

    v4 = StrictJSON(owners["v4_actual_failure"]).decode()
    value(v4, "schema", "rebar-phase2-first-party-runtime-non-delegation-v4-root-static-audit")
    value(v4, "status", "FAIL")
    value(v4, "finding_count", 1)
    value(v4, "candidate_family_count", 6)
    value(v4, "candidate_qualified", False)
    value(v4, "holdout", "NOT OPENED")
    value(v4, "performance", "NOT MEASURED")
    value(v4, "winner_selected", False)
    finding = v4["findings"]
    require(type(finding) is list and len(finding) == 1,
            "require complete sole authentic V4 private introspection finding")
    finding = finding[0]
    value(finding, "code", "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE")
    value(finding, "family", "rust")
    value(finding, "path", "candidates/rust/py_bridge.c")
    value(finding, "line", 4403)
    value(finding, "severity", "FAIL")
    value(finding, "provenance", "CANDIDATE_OWNED")
    value(finding, "reachability",
          "PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN")
    value(finding, "import_chain",
          ["candidate native bridge", "inspect", "tokenize", "re", "re.compile"])
    reach = v4["rust_reachability"]
    value(reach, "public_pattern_methods_use_native_descriptors", True)
    value(reach, "adapter_native_bind_call_count", 0)
    value(reach, "public_matching_delegation_proven", False)
    value(reach, "bridge_has_legacy_signature_getter", True)
    zig = v4["first_party_zig_ffi_and_facade_provenance"]
    value(zig, "status", "PASS")
    value(zig, "ffi_used", True)
    value(zig, "external_regex_engine_count", 0)
    for key in ("candidate_executions", "candidate_imports", "candidate_workers",
                "compiler_processes", "native_library_loads", "clock_samples",
                "holdout_reads", "workspace_mutations"):
        value(v4["effects"], key, 0)
    predecessors = v4["immutable_predecessors"]
    value(predecessors["immutable_v2"], "v2_candidate_executions", 0)
    value(predecessors["immutable_v2"], "v2_runtime_non_delegation", "NOT ESTABLISHED")
    value(predecessors["immutable_v3"], "candidate_executions", 0)
    value(predecessors["immutable_v3"], "finding_count", 7)
    value(predecessors["immutable_v3"], "runtime_non_delegation", "NOT ESTABLISHED")

    clamp = StrictJSON(owners["capture_clamp_contract"]).decode()
    value(clamp, "schema", "rebar-owned-rust-capture-clamp-semantics-v1-source-freeze")
    derivative = clamp["derived_first_party_capture_clamp"]
    value(derivative, "sha256", INPUT_SHA256)
    value(derivative, "bytes", INPUT_BYTES)
    value(derivative, "target_path", INPUT)
    value(derivative, "matcher_engine_changed", False)
    value(derivative, "external_regex_dependency_added", False)
    value(derivative, "fresh_export_begin_clamped", True)
    value(derivative, "fresh_export_end_clamped", True)
    history = clamp["actual_complete_v24_candidate_failure"]
    value(history, "candidate_status", "FAIL")
    value(history, "semantic_mismatch_count", 1352)
    value(history, "verified_passing_case_count", 15877)
    value(history, "case_execution_denominator", 31237)
    value(history, "suite_count", 13)

    build = StrictJSON(owners["v25_contract"]).decode()
    value(build, "schema", "rebar-phase2-owned-rust-capture-clamp-source-build-v25-source-freeze")
    value(build, "version", 25)
    variant = build["materialized_first_party_variant"]
    value(variant, "complete_source_sha256", INPUT_SHA256)
    value(variant, "complete_source_bytes", INPUT_BYTES)
    input_owner = variant["owner"]
    for key, expected in (("path", INPUT), ("sha256", INPUT_SHA256),
                          ("bytes", INPUT_BYTES), ("device", DEVICE),
                          ("inode", INPUT_INODE), ("mode", "0600"), ("nlink", 1)):
        value(input_owner, key, expected)

    publication = StrictJSON(owners["v25_publication"]).decode()
    root = StrictJSON(owners["v25_root"]).decode()
    value(publication, "schema", "rebar-phase2-owned-rust-capture-clamp-source-build-v25-durable-publication-receipt")
    value(root, "schema", "rebar-phase2-owned-rust-capture-clamp-source-build-v25-durable-root-provenance-receipt")
    for receipt in (publication, root):
        for key, expected in (("status", "PASS"), ("family", "rust"),
                              ("actual_compiler_process_count", 28),
                              ("candidate_workers_started", 0),
                              ("native_libraries_loaded", 0),
                              ("clock_samples", 0),
                              ("runtime_non_delegation", "NOT ESTABLISHED"),
                              ("holdout", "NOT OPENED"),
                              ("performance", "NOT MEASURED"),
                              ("candidate_qualified", False),
                              ("winner_selected", False),
                              ("latest_v24_candidate_status", "FAIL"),
                              ("latest_v24_semantic_mismatch_count", 1352),
                              ("latest_v24_verified_passing_case_count", 15877),
                              ("source_sha256", OWNERS[6][2]),
                              ("protocol_sha256", OWNERS[7][2]),
                              ("contract_sha256", OWNERS[8][2]),
                              ("capture_clamp_source_sha256", OWNERS[11][2]),
                              ("capture_clamp_protocol_sha256", OWNERS[12][2]),
                              ("capture_clamp_contract_sha256", OWNERS[13][2])):
            value(receipt, key, expected)
    value(publication, "combined_bridge_sha256", INPUT_SHA256)
    value(publication, "combined_bridge_bytes", INPUT_BYTES)
    value(publication, "candidate_imports", 0)
    value(publication, "candidate_processes_started", 0)
    value(root, "actual_source_phase_count", 2)
    value(root, "expected_actual_compiler_process_count", 28)
    value(root, "materialized_complete_bridge_sha256", INPUT_SHA256)
    value(root, "materialized_complete_bridge_bytes", INPUT_BYTES)
    value(root, "original_suite_count", 13)
    value(root, "original_case_execution_denominator", 31237)
    value(root, "named_private_waiver_count", 13)
    value(root, "cross_phase_complete_bridge_elf_byte_identical", True)
    value(root, "cross_phase_complete_engine_elf_byte_identical", True)
    value(root, "canonical_sources_modified", False)
    value(root, "historical_archives_opened", 0)
    value(root, "hidden_cases_read", 0)
    outputs = root["actual_reproduced_native_outputs"]
    bridge, engine = outputs["bridge"], outputs["engine"]
    value(bridge, "sha256", "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4")
    value(engine, "sha256", "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f")
    for binary in (bridge, engine):
        value(binary["audit"], "external_regex_dependency_count", 0)
        value(binary["audit"], "cross_family_dependency_count", 0)
    value(bridge["audit"], "needed", ["_rust_engine.so", "libc.so.6"])
    value(bridge["audit"], "runpath", ["$ORIGIN"])
    return {
        "v4_finding": finding,
        "v4_reachability": reach,
        "actual_v4_receipt_sha256": V4_RECEIPT_SHA256,
        "v25_publication_sha256": V25_PUBLICATION_SHA256,
        "v25_root_sha256": V25_ROOT_SHA256,
        "actual_v25_compiler_process_count": 28,
        "prior_actual_candidate_status": "FAIL",
        "prior_actual_semantic_mismatch_count": 1352,
        "prior_verified_passing_case_count": 15877,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "first_party_zig_ffi_status": "PASS",
        "external_regex_dependency_count": 0,
    }


def validate_contract(document: object, source_sha: str, protocol_sha: str) -> None:
    require(type(document) is dict, "require complete frozen correction contract")
    value(document, "schema", SCHEMA)
    value(document, "version", 1)
    value(document, "family", "rust")
    value(document, "phase", "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS")
    value(document, "status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN")
    value(document, "source", {"path": SOURCE, "sha256": source_sha})
    value(document, "protocol", {"path": PROTOCOL, "sha256": protocol_sha})
    correction = document["exact_private_introspection_correction"]
    for key, expected in (
            ("input_path", INPUT), ("input_sha256", INPUT_SHA256),
            ("input_bytes", INPUT_BYTES), ("input_device", DEVICE),
            ("input_inode", INPUT_INODE), ("input_mode", "0600"),
            ("target_path", TARGET), ("target_sha256", OUTPUT_SHA256),
            ("target_bytes", OUTPUT_BYTES), ("source_delta_bytes", -1659),
            ("deleted_private_function", "rust_bound_get_signature"),
            ("deleted_private_function_bytes", 1541),
            ("deleted_private_getset", "__signature__"),
            ("deleted_private_getset_bytes", 118),
            ("replacement_site_count", 2),
            ("public_pattern_methods_use_native_descriptors", True),
            ("public_descriptor_bytes_unchanged", True),
            ("normal_inspect_signature_pattern_search_unchanged", True),
            ("native_bind_adapter_call_count", 0),
            ("signature_field_retained", True),
            ("signature_gc_clear_sites_retained", 2),
            ("signature_gc_visit_sites_retained", 1),
            ("capture_clamp_correction_retained", True),
            ("matching_engine_changed", False),
            ("stdlib_matching_delegation_added", False),
            ("external_regex_dependency_added", False),
            ("runtime_non_delegation", "NOT ESTABLISHED"),
            ("candidate_built", False), ("candidate_imported", False),
            ("candidate_matching", "NOT RUN"), ("candidate_qualified", False)):
        value(correction, key, expected)
    predecessor = document["immutable_actual_v4_static_failure"]
    for key, expected in (("receipt_sha256", V4_RECEIPT_SHA256),
                          ("status", "FAIL"), ("finding_count", 1),
                          ("finding_code", "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"),
                          ("finding_family", "rust"),
                          ("finding_path", "candidates/rust/py_bridge.c"),
                          ("finding_line", 4403),
                          ("public_matching_delegation_proven", False),
                          ("candidate_executions", 0),
                          ("first_party_zig_ffi_status", "PASS")):
        value(predecessor, key, expected)
    lineage = document["immutable_actual_v25_first_party_native_build"]
    for key, expected in (("publication_receipt_sha256", V25_PUBLICATION_SHA256),
                          ("root_receipt_sha256", V25_ROOT_SHA256),
                          ("actual_compiler_process_count", 28),
                          ("actual_source_phase_count", 2),
                          ("capture_clamp_bridge_sha256", INPUT_SHA256),
                          ("capture_clamp_bridge_bytes", INPUT_BYTES),
                          ("external_regex_dependency_count", 0),
                          ("prior_actual_candidate_status", "FAIL"),
                          ("prior_actual_semantic_mismatch_count", 1352),
                          ("prior_verified_passing_case_count", 15877),
                          ("original_suite_count", 13),
                          ("original_case_execution_denominator", 31237),
                          ("named_private_waiver_count", 13),
                          ("runtime_non_delegation", "NOT ESTABLISHED")):
        value(lineage, key, expected)
    wall = document["physical_source_wall"]
    for key, expected in (("installed_before_owner_reads", True),
                          ("descriptor_relative_o_nofollow", True),
                          ("source_mode_candidate_source_reads", 0),
                          ("self_test_candidate_source_reads", 0),
                          ("source_mode_filesystem_writes", 0),
                          ("self_test_filesystem_writes", 0),
                          ("allowed_public_frozen_owner_count", len(OWNERS)),
                          ("apply_requires_explicit_root_authorization", True),
                          ("apply_requires_frozen_commit_equals_pushed_commit", True),
                          ("apply_candidate_source_read_count", 1),
                          ("apply_exclusive_new_target_only", True),
                          ("candidate_execution_allowed", False),
                          ("compiler_launch_allowed", False),
                          ("native_binary_open_allowed", False),
                          ("holdout_open_allowed", False),
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
    value(effects, "holdout", "NOT OPENED")
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
    require(len(modes) == 1, "require exactly one self-test, source freeze, or root apply")
    mode = modes[0]
    if mode == "--self-test":
        require(set(parsed) == {mode}, "self-test takes no owner or root arguments")
    elif mode == "--verify-source":
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                              "--contract-sha256"},
                "source verification requires exactly the complete frozen owner triple")
    else:
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                              "--contract-sha256", "--root-authorized",
                              "--frozen-commit", "--pushed-commit"},
                "root-only apply requires frozen owner triple and identical pushed commit")
        for label in ("--frozen-commit", "--pushed-commit"):
            commit = parsed[label]
            require(type(commit) is str and len(commit) == 40
                    and all(char in "0123456789abcdef" for char in commit),
                    "require complete lowercase frozen commit: " + label)
        require(parsed["--frozen-commit"] == parsed["--pushed-commit"],
                "refuse materialization before the frozen correction commit is pushed")
    for label in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if label in parsed:
            checked_sha(parsed[label], label)
    return parsed


def zero_effects(wall: SourceWall, mode: str) -> dict:
    return {
        "mode": mode,
        "approved_public_owner_reads": wall.public_reads,
        "candidate_source_files_read": wall.source_reads,
        "candidate_executions": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "compiler_processes_started": 0,
        "native_binary_files_opened": 0,
        "native_libraries_loaded": 0,
        "compressed_archives_opened": 0,
        "compressed_archives_inflated": 0,
        "holdout_cases_opened": 0,
        "holdout_cases_generated": 0,
        "clock_samples": 0,
        "network_requests": 0,
        "workspace_mutations": wall.workspace_mutations,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }


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
                "self-test must not read owners, candidates, or mutate workspace")
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
    contract = StrictJSON(contract_raw).decode()
    validate_contract(contract, source_sha, protocol_sha)
    frozen: dict[str, bytes] = {}
    for role, path, owner_sha, count, inode in OWNERS:
        require(not path.startswith("candidates/"),
                "candidate source must not be admitted as a public frozen owner")
        frozen[role] = wall.read(path, count, inode, owner_sha)
    evidence = authenticated_evidence(frozen)
    require(wall.public_reads == len(OWNERS) + 3 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "frozen verification must authenticate only public plaintext owners")
    if not apply:
        tests = synthetic_tests(wall)
        no_matching_imports()
        return {
            "schema": SCHEMA + "-verification",
            "status": "PASS; SOURCE FROZEN; NO CANDIDATE SOURCE READ",
            "source_sha256": source_sha,
            "protocol_sha256": protocol_sha,
            "contract_sha256": contract_sha,
            "authenticated_public_owner_count": len(OWNERS),
            "immutable_actual_evidence": evidence,
            "predicted_target_path": TARGET,
            "predicted_target_sha256": OUTPUT_SHA256,
            "predicted_target_bytes": OUTPUT_BYTES,
            "synthetic_controls": tests,
            "effects": zero_effects(wall, "SOURCE FREEZE"),
        }

    require(transform(synthetic_source()) and wall.source_reads == 0,
            "require complete synthetic correction before root-only source access")
    original = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA256)
    corrected = transform(original, exact=True)
    wall.materialize(corrected)
    no_matching_imports()
    require(wall.source_reads == 1 and wall.workspace_mutations == 2,
            "materialize exactly one exclusive directory and one corrected C file")
    return {
        "schema": SCHEMA + "-root-materialization",
        "status": "PASS; EXACT PRIVATE INTROSPECTION REMOVED; NOT BUILT; NOT RUN",
        "frozen_commit": options["--frozen-commit"],
        "pushed_commit": options["--pushed-commit"],
        "source_sha256": source_sha,
        "protocol_sha256": protocol_sha,
        "contract_sha256": contract_sha,
        "input_path": INPUT,
        "input_sha256": INPUT_SHA256,
        "input_bytes": INPUT_BYTES,
        "target_path": TARGET,
        "target_sha256": OUTPUT_SHA256,
        "target_bytes": OUTPUT_BYTES,
        "deleted_private_function_bytes": len(FUNCTION),
        "deleted_private_getset_row_bytes": len(GETSET_ROW),
        "public_native_descriptors_preserved": True,
        "capture_clamp_preserved": True,
        "effects": zero_effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION"),
    }


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError) as error:
        sys.stderr.write("rust-no-external-introspection-v1: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
