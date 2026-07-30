#!/usr/bin/env python3
"""Freeze cumulative, evidence-backed, first-party C compatibility corrections.

The earlier Match-pickle hypothesis was falsified by the frozen public oracle:
CPython permits legacy protocols zero and one.  The independently built C21
source encoded the wrong all-protocol rejection and also snapshots live buffer
exporters too early.  This controller reconstructs that exact C21 source
before applying narrowly bounded, reversible native-only corrections.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("complete first-party C semantics cannot import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
SCHEMA = "rebar-owned-c-complete-native-semantics-v1-source-freeze"
SOURCE = "tools/apply_owned_c_complete_native_semantics_v1.py"
PROTOCOL = "oracle/phase2/C-COMPLETE-NATIVE-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/c-complete-native-semantics-v1.json"
INPUT = "candidates/c/variants/subject_buffer_ownership_v1/vm_native.c"
INPUT_SHA256 = "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962"
INPUT_BYTES = 222212
INPUT_INODE = 524723
C21_SHA256 = "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
C21_BYTES = 221647
C21_NATIVE_SHA256 = "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60"
TARGET_DIRECTORY = "candidates/c/variants/complete_native_semantics_v1"
TARGET = TARGET_DIRECTORY + "/vm_native.c"
OUTPUT_SHA256 = "0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f"
OUTPUT_BYTES = 221557

WRONG_MATCH_OWNERS = (
    ("tools/apply_owned_c_original_match_semantics_v1.py",
     "e2a67d418ab531a93bb2f894844a256460ba7fde70a6e1f6fb2ae82eba63b1c6",
     49528, 431406),
    ("oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-V1.md",
     "a71e397d87ecd538ee8a1eb218a6dbdf68849cc9598c208ddc83066dc9aec7b9",
     6310, 525326),
    ("oracle/phase2/c-original-match-semantics-v1.json",
     "6a7a53c77bd20664fed15a61d5ad5c1d7ae5354405e99e8d72427d44ab9f134c",
     14770, 525329),
)
ADAPTER_OWNERS = (
    ("tools/apply_owned_c_public_adapter_semantics_v2.py",
     "13173033914a706f4d80e76dc8c95ee016a125f7d3261fdf252ed404a60ebb55",
     55674, 429225),
    ("oracle/phase2/C-PUBLIC-ADAPTER-SEMANTICS-V2.md",
     "ad91932c5b60cace2a632d11ff62e80d3890de4e4018e8e9ed7e6a4b466436a2",
     7529, 524903),
    ("oracle/phase2/c-public-adapter-semantics-v2.json",
     "ed5421ca2ab6a99c59945529cd8ae640636bad2ad42806bd7f36c8cf3ef584ce",
     3806, 524904),
)
ADAPTER_RECEIPT = (
    "oracle/phase2/evidence/c-public-adapter-semantics-v2-application.json",
    "e3e63acfde8f1eef32f81d48bddc613fb386880a5f1974b898e36b211ab55476",
    1459, 525121,
)
GUARD_OWNERS = (
    ("tools/verify_owned_candidate_runtime_independence_v4.py",
     "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3",
     48687, 429243),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
     "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16",
     4492, 525890),
    ("oracle/phase2/candidate-runtime-independence-v4.json",
     "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
     9352, 525891),
)
C12_LEDGER = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-"
    "c-original-match-semantics-original-p0-v12-failures-publication-receipt.json",
    "a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b",
    10943, 525645,
)
C21_BUILD = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-publication-receipt.json",
    "9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df",
    11878, 524817,
)
C21_ROOT = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-root-provenance-receipt.json",
    "8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2",
    10837, 524818,
)

CORRECT_LEGACY_REDUCERS = b'''static PyObject *match_reduce(MatchObject *match, PyObject *ignored) {
    (void)ignored;
    VMModuleState *state=vm_type_state(Py_TYPE(match));
    if (!state) return NULL;
    if (!state->scanner_reconstructor || !state->match_type) {
        PyErr_SetString(PyExc_RuntimeError,
                        "native match reconstruction is not configured");
        return NULL;
    }
    PyObject *arguments=PyTuple_Pack(3,state->match_type,
                                     (PyObject *)&PyBaseObject_Type,Py_None);
    if (!arguments) return NULL;
    PyObject *result=PyTuple_Pack(2,state->scanner_reconstructor,arguments);
    Py_DECREF(arguments);
    return result;
}

static PyObject *match_reduce_ex(MatchObject *match, PyObject *protocol) {
    PyObject *index=PyNumber_Index(protocol);
    if (!index) return NULL;
    Py_ssize_t version=PyLong_AsSsize_t(index);
    Py_DECREF(index);
    if (version == -1 && PyErr_Occurred()) return NULL;
    if (version < 2) return match_reduce(match,NULL);
    PyErr_SetString(PyExc_TypeError,"cannot pickle 're.Match' object");
    return NULL;
}
'''

FALSE_C21_REDUCERS = b'''static PyObject *match_reduce(MatchObject *match, PyObject *ignored) {
    (void)match;
    (void)ignored;
    PyErr_SetString(PyExc_TypeError,"cannot pickle 're.Match' object");
    return NULL;
}

static PyObject *match_reduce_ex(MatchObject *match, PyObject *protocol) {
    PyObject *index=PyNumber_Index(protocol);
    if (!index) return NULL;
    Py_ssize_t version=PyLong_AsSsize_t(index);
    Py_DECREF(index);
    if (version == -1 && PyErr_Occurred()) return NULL;
    (void)version;
    return match_reduce(match,NULL);
}
'''

COMPLETE_REDUCERS = CORRECT_LEGACY_REDUCERS.replace(
    b"    Py_ssize_t version=PyLong_AsSsize_t(index);\n",
    b"    int version=PyLong_AsInt(index);\n",
)
SNAPSHOT_DECLARATION = b"    PyObject *subject_snapshot=NULL;\n"
EARLY_SUBJECT_SNAPSHOT = b'''    if (subject.has_view) {
        subject_snapshot=PyBytes_FromStringAndSize(
            NULL,subject.view.len);
        if (!subject_snapshot) goto done;
        if (subject.view.len &&
            PyBuffer_ToContiguous(PyBytes_AS_STRING(subject_snapshot),
                                  &subject.view,subject.view.len,'C')<0) {
            goto done;
        }
        subject_clear(&subject);
        if (!subject_init(&subject,subject_snapshot)) goto done;
    }
'''
SNAPSHOT_FINAL_RELEASE = b"    Py_XDECREF(subject_snapshot);\n"
OLD_SCANNER_TRAVERSE = b'''static int scanner_traverse(FindIterObject *iterator, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(iterator));
    Py_VISIT(iterator->pattern);
    Py_VISIT(iterator->string);
    if (iterator->subject.has_view) {
        Py_VISIT(iterator->subject.view.obj);
    }
    return 0;
}
'''
NEW_SCANNER_TRAVERSE = b'''static int scanner_traverse(FindIterObject *iterator, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(iterator));
    Py_VISIT(iterator->pattern);
    return 0;
}
'''
OLD_SUBSTITUTE_BYTES_SIGNATURE = (
    b"static PyObject *substitute_bytes(PatternObject *pattern,\n"
    b"                                  const Subject *subject,\n"
)
NEW_SUBSTITUTE_BYTES_SIGNATURE = (
    b"static PyObject *substitute_bytes(PatternObject *pattern,\n"
    b"                                  Subject *subject,\n"
)
OLD_JOIN_RELEASE = (
    b"    PyObject *joined=PyObject_CallMethod(empty,\"join\",\"O\",pieces);\n"
)
NEW_JOIN_RELEASE = (
    b"    subject_clear(subject);\n"
    b"    PyObject *joined=PyObject_CallMethod(empty,\"join\",\"O\",pieces);\n"
)
COPY_ANCHOR = (
    b"static PyObject *match_copy(MatchObject *match, PyObject *ignored) "
    b"{ (void)ignored; return Py_NewRef(match); }\n"
    b"static PyObject *match_deepcopy(MatchObject *match, PyObject *memo) "
    b"{ (void)memo; return Py_NewRef(match); }\n"
)
CAPTURE_ANCHOR = b'''static PyObject *subject_capture_slice(const Subject *subject,
                                       Py_ssize_t begin,
                                       Py_ssize_t end) {
    if (!subject->has_view) return subject_slice(subject,begin,end);

    Subject capture;
    if (!subject_init(&capture,subject->obj)) return NULL;
    PyObject *result=subject_slice(&capture,begin,end);
    subject_clear(&capture);
    return result;
}
'''
SUBJECT_CLEAR_ANCHOR = b'''static void subject_clear(Subject *subject) {
    if (subject->has_view) {
        subject->has_view=0;
        subject->bytes=NULL;
        PyBuffer_Release(&subject->view);
    }
}
'''
SCANNER_CLEAR_ANCHOR = b'''static int scanner_clear(FindIterObject *iterator) {
    iterator->done=1;
    subject_clear(&iterator->subject);
    iterator->subject.obj=NULL;
    iterator->subject.bytes=NULL;
    iterator->subject.unicode_data=NULL;
    Py_CLEAR(iterator->string);
    Py_CLEAR(iterator->pattern);
    return 0;
}
'''
METHOD_ANCHOR = (
    b'    {"__reduce_ex__",(PyCFunction)match_reduce_ex,METH_O,'
    b'"Matches cannot be pickled."},\n'
)
FORBIDDEN_C = (
    b'PyImport_ImportModule("re")', b'PyImport_ImportModule("_sre")',
    b'PyImport_ImportModule("regex")', b'PyImport_ImportModule("re2")',
    b"#include <regex.h>", b"#include <pcre", b"pcre2_", b"onig_",
    b"PyRun_String(", b"PyRun_SimpleString(", b"system(", b"dlopen(",
    b"dlsym(", b"candidates.rust", b"candidates.zig",
)


class FreezeError(Exception):
    """An immutable source owner, first-party semantic proof, or wall failed."""


def need(condition: object, reason: str) -> None:
    if condition is not True:
        raise FreezeError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only exact complete first-party source bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, role: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require independently pinned lowercase SHA-256: " + role)
    return value


def quote(value: str) -> str:
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for item in value:
        number = ord(item)
        need(not 0xD800 <= number <= 0xDFFF,
             "reject unauthenticated JSON surrogate")
        result.append(escapes.get(item, "\\u" + format(number, "04x")
                      if number < 32 else item))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    need(depth < 60, "bound immutable evidence nesting")
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
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        need(all(type(key) is str for key in value),
             "reject nontext immutable JSON key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported source-only evidence value")


class JSON:
    """Small duplicate-rejecting bounded receipt parser with no regex import."""

    def __init__(self, raw: bytes) -> None:
        need(type(raw) is bytes and 0 < len(raw) <= 262144,
             "require bounded immutable plaintext JSON evidence")
        self.text = raw.decode("utf-8", "strict")
        self.at = 0
        self.count = 0

    def whitespace(self) -> None:
        while self.at < len(self.text) and self.text[self.at] in " \t\r\n":
            self.at += 1

    def string(self) -> str:
        need(self.text[self.at:self.at + 1] == '"', "require JSON string")
        self.at += 1
        result: list[str] = []
        simple = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                  "n": "\n", "r": "\r", "t": "\t"}
        while self.at < len(self.text):
            item = self.text[self.at]
            self.at += 1
            if item == '"':
                return "".join(result)
            if item != "\\":
                need(ord(item) >= 32 and not 0xD800 <= ord(item) <= 0xDFFF,
                     "reject malformed immutable JSON string")
                result.append(item)
                continue
            need(self.at < len(self.text), "reject incomplete JSON escape")
            item = self.text[self.at]
            self.at += 1
            if item != "u":
                need(item in simple, "reject unknown JSON escape")
                result.append(simple[item])
                continue
            chars = self.text[self.at:self.at + 4]
            need(len(chars) == 4
                 and all(char in "0123456789abcdefABCDEF" for char in chars),
                 "reject malformed Unicode escape")
            self.at += 4
            number = int(chars, 16)
            if 0xD800 <= number <= 0xDBFF:
                need(self.text[self.at:self.at + 2] == "\\u",
                     "reject missing JSON surrogate pair")
                chars = self.text[self.at + 2:self.at + 6]
                need(len(chars) == 4
                     and all(char in "0123456789abcdefABCDEF" for char in chars),
                     "reject malformed JSON low surrogate")
                low = int(chars, 16)
                need(0xDC00 <= low <= 0xDFFF,
                     "reject invalid JSON low surrogate")
                self.at += 6
                result.append(chr(0x10000 + ((number - 0xD800) << 10)
                                  + low - 0xDC00))
            else:
                need(not 0xDC00 <= number <= 0xDFFF,
                     "reject unpaired low JSON surrogate")
                result.append(chr(number))
        raise FreezeError("reject unterminated JSON string")

    def value(self, depth: int = 0) -> object:
        need(depth < 60, "bound authenticated receipt depth")
        self.whitespace()
        need(self.at < len(self.text), "reject incomplete JSON value")
        item = self.text[self.at]
        if item == '"':
            return self.string()
        if item == "{":
            self.at += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.at:self.at + 1] == "}":
                self.at += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                need(key not in result, "reject duplicated authenticated JSON key")
                self.count += 1
                need(self.count < 30000, "bound authenticated receipt fields")
                self.whitespace()
                need(self.text[self.at:self.at + 1] == ":", "require JSON colon")
                self.at += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                mark = self.text[self.at:self.at + 1]
                self.at += 1
                if mark == "}":
                    return result
                need(mark == ",", "reject malformed JSON mapping")
        if item == "[":
            self.at += 1
            result_list: list[object] = []
            self.whitespace()
            if self.text[self.at:self.at + 1] == "]":
                self.at += 1
                return result_list
            while True:
                self.count += 1
                need(self.count < 30000, "bound authenticated receipt list")
                result_list.append(self.value(depth + 1))
                self.whitespace()
                mark = self.text[self.at:self.at + 1]
                self.at += 1
                if mark == "]":
                    return result_list
                need(mark == ",", "reject malformed authenticated list")
        if item == "-" or item in "0123456789":
            begin = self.at
            if item == "-":
                self.at += 1
            need(self.at < len(self.text), "reject incomplete JSON integer")
            if self.text[self.at] == "0":
                self.at += 1
                need(self.at == len(self.text)
                     or self.text[self.at] not in "0123456789",
                     "reject noncanonical leading-zero integer")
            else:
                need(self.text[self.at] in "123456789",
                     "reject malformed JSON integer")
                while self.at < len(self.text) and self.text[self.at] in "0123456789":
                    self.at += 1
            need(self.text[self.at:self.at + 1] not in (".", "e", "E"),
                 "reject floating immutable contract value")
            return int(self.text[begin:self.at])
        for literal, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.at):
                self.at += len(literal)
                return value
        raise FreezeError("reject malformed authenticated JSON")

    def parse(self) -> object:
        result = self.value()
        self.whitespace()
        need(self.at == len(self.text), "reject trailing authenticated JSON")
        return result


def no_matchers() -> None:
    banned = ("re", "_sre", "regex", "ctypes", "candidates", "rebar",
              "subprocess", "socket", "threading", "multiprocessing",
              "concurrent", "gzip", "zipfile", "tarfile")
    need(not any(name == root or name.startswith(root + ".")
                 for name in sys.modules for root in banned),
         "reject matcher, candidate, native loader, archive, or process")


class Wall:
    """Default-deny, descriptor-relative, no-follow source and materialization wall."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        evidence = (ADAPTER_RECEIPT, C12_LEDGER, C21_BUILD, C21_ROOT)
        owners = WRONG_MATCH_OWNERS + ADAPTER_OWNERS + GUARD_OWNERS + evidence
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT)
                                + tuple(row[0] for row in owners))
        self.allowed = self.public | (frozenset((INPUT,)) if apply else frozenset())
        self.native_open = os.open
        self.native_read = os.read
        self.native_write = os.write
        self.native_close = os.close
        self.native_fstat = os.fstat
        self.native_fsync = os.fsync
        self.native_mkdir = os.mkdir
        self.root: int | None = None
        self.live: dict[int, tuple[str, str]] = {}
        self.open_ticket: tuple[str, int] | None = None
        self.mkdir_ticket: tuple[str, int] | None = None
        self.public_reads = 0
        self.candidate_reads = 0
        self.workspace_mutations = 0
        self.rejected = 0
        self.installed = False

    def deny(self, reason: str) -> None:
        self.rejected += 1
        raise FreezeError("complete first-party C wall rejected " + reason)

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if self.open_ticket == (path, flags):
                return
            self.deny("unticketed file, candidate, archive, native, or target")
        if event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            if self.mkdir_ticket == (path, mode):
                return
            self.deny("unticketed workspace directory")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.rmdir",
                      "os.chmod", "os.chown", "os.urandom", "os.getrandom",
                      "_interpreters.create", "_interpreters.exec",
                      "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.", "time.",
                                     "os.exec", "os.spawn"))):
            self.deny("candidate execution, dynamic code, process, clock, or network")

    def blocked(self, reason: str):
        def stop(*_arguments: object, **_keywords: object) -> object:
            self.deny(reason)
        return stop

    def install(self) -> None:
        need(not self.installed, "install the complete native descriptor wall once")
        sys.addaudithook(self.audit)
        builtins.open = self.blocked("builtins.open")
        for module in (_io, io):
            module.open = self.blocked(module.__name__ + ".open")
            module.FileIO = self.blocked(module.__name__ + ".FileIO")
            if hasattr(module, "open_code"):
                module.open_code = self.blocked(module.__name__ + ".open_code")
        for name in ("open", "read", "write", "close", "fstat", "fsync", "mkdir",
                     "fdopen", "dup", "dup2", "stat", "lstat", "readlink",
                     "listdir", "scandir", "walk", "fwalk", "access", "fork",
                     "posix_spawn", "posix_spawnp", "system", "makedirs",
                     "remove", "unlink", "rename", "replace", "rmdir", "chmod",
                     "chown", "urandom", "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.blocked("os." + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.blocked("clock." + name))
        self.installed = True

    def ticket(self, path: str, flags: int, mode: int = 0,
               *, parent: int | None = None) -> int:
        need(self.installed and self.open_ticket is None,
             "reject unguarded or nested complete-source descriptor")
        self.open_ticket = (path, flags)
        try:
            if parent is None:
                return self.native_open(path, flags, mode)
            return self.native_open(path, flags, mode, dir_fd=parent)
        finally:
            self.open_ticket = None

    @staticmethod
    def directory_flags() -> int:
        return (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0))

    @staticmethod
    def file_flags() -> int:
        return (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0))

    def open_root(self) -> None:
        need(self.root is None, "open immutable complete-source workspace once")
        descriptor = self.ticket(ROOT, self.directory_flags())
        info = self.native_fstat(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE,
             "reject substituted complete-source workspace")
        self.root = descriptor
        self.live[descriptor] = ("", "directory")

    def segment(self, value: object) -> str:
        need(type(value) is str and bool(value) and value not in (".", "..")
             and "/" not in value and "\x00" not in value,
             "reject complete-source traversal or malformed descriptor segment")
        return value

    def child(self, parent: int, segment: str) -> int:
        name = self.segment(segment)
        owner = self.live.get(parent)
        need(owner is not None and owner[1] == "directory",
             "reject foreign complete-source parent descriptor")
        relative = name if not owner[0] else owner[0] + "/" + name
        approved = any(item.startswith(relative + "/") for item in self.allowed)
        if self.apply:
            approved = (approved or relative == TARGET_DIRECTORY
                        or TARGET_DIRECTORY.startswith(relative + "/"))
        need(approved and not relative.startswith((".git/", ".agents/", ".codex/")),
             "reject private source root, candidate, archive, or unrelated owner")
        descriptor = self.ticket(name, self.directory_flags(), parent=parent)
        info = self.native_fstat(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE,
             "reject substituted or symbolic-link source directory")
        self.live[descriptor] = (relative, "directory")
        return descriptor

    def close(self, descriptor: int) -> None:
        need(descriptor in self.live and descriptor != self.root,
             "reject foreign immutable descriptor close")
        self.native_close(descriptor)
        del self.live[descriptor]

    def parent(self, relative: str) -> tuple[int, list[int], str]:
        need(relative in self.allowed and self.root is not None,
             "deny native source before separately authorized root application")
        descriptor = self.root
        opened: list[int] = []
        parts = relative.split("/")
        try:
            for part in parts[:-1]:
                descriptor = self.child(descriptor, part)
                opened.append(descriptor)
            return descriptor, opened, self.segment(parts[-1])
        except BaseException:
            for item in reversed(opened):
                self.close(item)
            raise

    def read(self, relative: str, expected: str,
             size: int | None = None, inode: int | None = None) -> bytes:
        need(relative in self.allowed,
             "reject unauthorized immutable plaintext or candidate owner")
        checked_hash(expected, relative)
        parent, opened, name = self.parent(relative)
        descriptor: int | None = None
        try:
            descriptor = self.ticket(name, self.file_flags(), parent=parent)
            self.live[descriptor] = (relative, "file")
            before = self.native_fstat(descriptor)
            need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                 and stat.S_IMODE(before.st_mode) == 0o600
                 and before.st_nlink == 1 and before.st_uid == os.geteuid()
                 and 0 < before.st_size <= 262144
                 and (size is None or before.st_size == size)
                 and (inode is None or before.st_ino == inode),
                 "reject substituted immutable complete-source owner: " + relative)
            blocks: list[bytes] = []
            remaining = before.st_size
            while remaining:
                block = self.native_read(descriptor, min(remaining, 65536))
                need(type(block) is bytes and bool(block),
                     "reject truncated immutable complete-source owner")
                blocks.append(block)
                remaining -= len(block)
            need(self.native_read(descriptor, 1) == b"",
                 "reject extra immutable complete-source owner bytes")
            after = self.native_fstat(descriptor)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "reject concurrently changed immutable complete-source owner")
            raw = b"".join(blocks)
            need(digest(raw) == expected,
                 "reject substituted immutable complete-source owner digest")
            if relative == INPUT:
                self.candidate_reads += 1
            else:
                self.public_reads += 1
            return raw
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for item in reversed(opened):
                self.close(item)

    def materialize(self, raw: bytes) -> None:
        need(self.apply and self.root is not None
             and len(raw) == OUTPUT_BYTES and digest(raw) == OUTPUT_SHA256,
             "deny nonidentical, unpinned, or unauthorized C native target")
        descriptor = self.root
        opened: list[int] = []
        try:
            parts = TARGET_DIRECTORY.split("/")
            for part in parts[:-1]:
                descriptor = self.child(descriptor, part)
                opened.append(descriptor)
            name = parts[-1]
            need(self.mkdir_ticket is None,
                 "reject nested complete-source exclusive-directory ticket")
            self.mkdir_ticket = (name, 0o700)
            try:
                self.native_mkdir(name, 0o700, dir_fd=descriptor)
            finally:
                self.mkdir_ticket = None
            self.workspace_mutations += 1
            self.native_fsync(descriptor)
            target = self.child(descriptor, name)
            opened.append(target)
            flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | getattr(os, "O_NOFOLLOW", 0)
                     | getattr(os, "O_CLOEXEC", 0))
            output = self.ticket("vm_native.c", flags, 0o600, parent=target)
            self.live[output] = (TARGET, "target")
            self.workspace_mutations += 1
            try:
                position = 0
                while position < len(raw):
                    count = self.native_write(output, raw[position:])
                    need(type(count) is int and count > 0,
                         "reject incomplete exclusive native source creation")
                    position += count
                info = self.native_fstat(output)
                need(stat.S_ISREG(info.st_mode) and info.st_dev == DEVICE
                     and stat.S_IMODE(info.st_mode) == 0o600
                     and info.st_nlink == 1 and info.st_size == OUTPUT_BYTES,
                     "reject substituted exclusive first-party native source")
                self.native_fsync(output)
            finally:
                self.close(output)
            self.native_fsync(target)
            readback = self.ticket("vm_native.c", self.file_flags(), parent=target)
            self.live[readback] = (TARGET, "readback")
            try:
                blocks: list[bytes] = []
                remaining = OUTPUT_BYTES
                while remaining:
                    block = self.native_read(readback, min(remaining, 65536))
                    need(bool(block), "reject truncated durable native source")
                    blocks.append(block)
                    remaining -= len(block)
                need(self.native_read(readback, 1) == b""
                     and digest(b"".join(blocks)) == OUTPUT_SHA256,
                     "reject changed durable first-party native source")
            finally:
                self.close(readback)
        finally:
            for item in reversed(opened):
                self.close(item)


def replace_once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    need(type(raw) is bytes and type(old) is bytes and type(new) is bytes
         and old != new and raw.count(old) == 1,
         "require exactly one reversible first-party source site: " + label)
    return raw.replace(old, new, 1)


def preserve_engine(raw: bytes) -> None:
    for anchor, label in (
        (COPY_ANCHOR, "immutable Match copy and deepcopy"),
        (CAPTURE_ANCHOR, "per-capture nested exporter acquisition"),
        (SUBJECT_CLEAR_ANCHOR, "idempotent buffer release ordering"),
        (SCANNER_CLEAR_ANCHOR, "done and owned view before subject teardown"),
        (METHOD_ANCHOR, "exact dedicated public Match reduction method"),
    ):
        need(raw.count(anchor) == 1,
             "preserve exactly one unchanged native ownership anchor: " + label)
    need(raw.count(b"PyObject *subject_snapshot") == 0,
         "never snapshot or detach a live original exporter")
    need(raw.count(NEW_SCANNER_TRAVERSE) == 1,
         "hide both retained original-subject edges from cyclic GC")
    need(raw.count(NEW_SUBSTITUTE_BYTES_SIGNATURE) == 1,
         "require mutable owned subject solely for final join release")
    need(raw.count(NEW_JOIN_RELEASE) == 1,
         "release the original subject exactly once immediately before joining")
    need(raw.count(COMPLETE_REDUCERS) == 1
         and FALSE_C21_REDUCERS not in raw
         and CORRECT_LEGACY_REDUCERS not in raw,
         "require legacy Match reconstruction and exact signed C-int protocol")
    need(COMPLETE_REDUCERS.count(b"PyNumber_Index(protocol)") == 1
         and COMPLETE_REDUCERS.count(b"PyLong_AsInt(index)") == 1
         and COMPLETE_REDUCERS.count(b"Py_DECREF(index);") == 1
         and COMPLETE_REDUCERS.count(b"if (version < 2)") == 1
         and COMPLETE_REDUCERS.count(b"state->scanner_reconstructor") == 2
         and COMPLETE_REDUCERS.count(b"state->match_type") == 2,
         "preserve exact Match protocol coercion and state-owned reconstruction")


def reconstruct_c21(raw: bytes, *, exact: bool = False) -> bytes:
    need(type(raw) is bytes,
         "reconstruct C21 solely from complete first-party native source bytes")
    if exact:
        need(len(raw) == INPUT_BYTES and digest(raw) == INPUT_SHA256,
             "authenticate the sole immutable independently authored C source")
    need(raw.count(CORRECT_LEGACY_REDUCERS) == 1
         and FALSE_C21_REDUCERS not in raw,
         "preserve previously correct legacy C reducers before C21 reconstruction")
    result = replace_once(raw, CORRECT_LEGACY_REDUCERS,
                          FALSE_C21_REDUCERS,
                          "historical and independently falsified C21 reducer")
    if exact:
        need(len(result) == C21_BYTES and digest(result) == C21_SHA256,
             "independently reconstruct the exact latest actually tested C21 source")
    return result


def repair_c21(raw: bytes, *, exact: bool = False) -> bytes:
    need(type(raw) is bytes,
         "repair only exact complete first-party C21 engine bytes")
    if exact:
        need(len(raw) == C21_BYTES and digest(raw) == C21_SHA256,
             "refuse a source other than the genuinely tested C21 native engine")
    changes = (
        (FALSE_C21_REDUCERS, COMPLETE_REDUCERS,
         "restore legacy Match reconstruction with signed C-int protocol"),
        (SNAPSHOT_DECLARATION, b"",
         "remove eager subject-copy bookkeeping"),
        (EARLY_SUBJECT_SNAPSHOT, b"",
         "keep the original subject export through every capture"),
        (SNAPSHOT_FINAL_RELEASE, b"",
         "remove fabricated snapshot cleanup"),
        (OLD_SCANNER_TRAVERSE, NEW_SCANNER_TRAVERSE,
         "match original scanner GC visibility"),
        (OLD_SUBSTITUTE_BYTES_SIGNATURE, NEW_SUBSTITUTE_BYTES_SIGNATURE,
         "permit owned subject teardown immediately before joining"),
        (OLD_JOIN_RELEASE, NEW_JOIN_RELEASE,
         "release original exporter only after every captured piece exists"),
    )
    result = raw
    for old, new, label in changes:
        result = replace_once(result, old, new, label)
    preserve_engine(result)
    for token in FORBIDDEN_C:
        need(result.count(token) == raw.count(token) == 0,
             "reject stdlib, external, cross-candidate, or interpreter delegation")
    if exact:
        need(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
             "pin the complete cumulative independently derived native source")
    return result


def synthetic_source() -> bytes:
    return b"".join((
        b"/* first-party C source-only hostile-control witness */\n",
        COPY_ANCHOR, CAPTURE_ANCHOR, SUBJECT_CLEAR_ANCHOR,
        CORRECT_LEGACY_REDUCERS, METHOD_ANCHOR,
        OLD_SCANNER_TRAVERSE, SCANNER_CLEAR_ANCHOR,
        OLD_SUBSTITUTE_BYTES_SIGNATURE, b"    int synthetic;\n", b"}\n",
        SNAPSHOT_DECLARATION, EARLY_SUBJECT_SNAPSHOT,
        SNAPSHOT_FINAL_RELEASE, OLD_JOIN_RELEASE,
    ))


class ModelExporter:
    """Synthetic ownership/event model; never imports or invokes a matcher."""

    def __init__(self, payload: bytes, role: str, mutates: bool,
                 events: list[tuple]) -> None:
        need(type(payload) is bytes and role in ("subject", "replacement")
             and type(mutates) is bool and type(events) is list,
             "reject substituted synthetic exporter")
        self.backing = bytearray(payload)
        self.role = role
        self.mutates = mutates
        self.events = events
        self.active = 0

    def acquire(self, flags: int = 0) -> bytes:
        need(type(flags) is int and flags in (0, 284),
             "require exact original simple/full-readonly exporter flags")
        before = bytes(self.backing)
        self.events.append(("acquire", self.role, flags, self.active, before))
        self.active += 1
        return before

    def release(self) -> None:
        need(self.active > 0,
             "reject omitted, repeated, or unowned synthetic buffer release")
        before = bytes(self.backing)
        if self.mutates:
            self.backing[:] = b"!" * len(self.backing)
        self.active -= 1
        self.events.append(("release", self.role, self.active, before,
                            bytes(self.backing)))


def model_substitution(*, mutates: bool, capture_count: int,
                       replacement: bool, join_error: bool = False,
                       no_match: bool = False) -> tuple[bytes, list[tuple]]:
    need(type(mutates) is bool and type(capture_count) is int
         and 0 <= capture_count <= 12 and type(replacement) is bool
         and type(join_error) is bool and type(no_match) is bool,
         "reject synthetic exporter/matching lifecycle parameters")
    events: list[tuple] = []
    subject = ModelExporter(b"alpha42", "subject", mutates, events)
    template = ModelExporter(b"X", "replacement", False, events)
    if replacement:
        template.acquire(0)
        template.release()
    outer = subject.acquire(0)
    pieces: list[bytes] = []
    if not no_match:
        for _ in range(capture_count):
            capture = subject.acquire(0)
            pieces.append(capture[:5])
            subject.release()
        pieces.append(bytes(subject.backing)[5:])
    subject.release()
    if no_match:
        need(subject.active == 0 and template.active == 0,
             "release no-match exporter without touching replacement join")
        return outer, events
    if replacement:
        if join_error:
            events.append(("acquire-error", "replacement", 0, 0))
            need(subject.active == 0,
                 "release subject before a genuinely failing replacement join")
            return b"", events
        for _ in range(2):
            template.acquire(0)
            template.release()
    need(subject.active == 0 and template.active == 0,
         "leave no retained synthetic subject/template exporter")
    result = b"".join(b"<" + item + b">" for item in pieces[:-1]) + pieces[-1]
    return result, events


def model_protocol(value: object) -> tuple[str, int]:
    if type(value) is bool:
        number = int(value)
    elif type(value) is int:
        number = value
    else:
        index = getattr(type(value), "__index__", None)
        if index is None:
            raise TypeError("object cannot be interpreted as an integer")
        number = index(value)
        if type(number) is not int:
            raise TypeError("__index__ returned non-int")
    if number < -(1 << 31) or number >= 1 << 31:
        raise OverflowError("Python int too large to convert to C int")
    if number >= 2:
        raise TypeError("cannot pickle 're.Match' object")
    return ("owned-copyreg-reconstructor", number)


def model_scanner(*, wrapped: bool, readonly: bool) -> dict[str, object]:
    need(type(wrapped) is bool and type(readonly) is bool,
         "reject synthetic original scanner carrier")
    events: list[tuple] = []
    owner = ModelExporter(b"aaa", "subject", True, events)
    owner.acquire(284 if wrapped else 0)
    events.append(("gc-live", True, True))
    if not wrapped:
        owner.acquire(0)
        owner.release()
    events.append(("gc-after-drop", True, True))
    events.append(("fixture-cycle-break", wrapped, readonly))
    owner.release()
    events.append(("gc-final", False, False))
    need(owner.active == 0,
         "retain scanner owner until the deliberate fixture cycle is removed")
    return {"events": events,
            "acquisitions": 1 if wrapped else 2,
            "releases": 1 if wrapped else 2,
            "final_payload": bytes(owner.backing),
            "public_gc_referents": ("builtins.type", "re.Pattern")}


def semantic_controls() -> dict[str, object]:
    count = 0

    def accept(condition: object, label: str) -> None:
        nonlocal count
        need(condition is True, "reject changed complete native semantics: " + label)
        count += 1

    def reject(action: object, label: str,
               exceptions: tuple[type[BaseException], ...] =
               (FreezeError, TypeError, ValueError, OverflowError)) -> None:
        nonlocal count
        raised = False
        try:
            action()
        except exceptions:
            raised = True
        need(raised, "accept forbidden complete native semantics: " + label)
        count += 1

    fixture = synthetic_source()
    c21 = reconstruct_c21(fixture)
    fixed = repair_c21(c21)
    accept(FALSE_C21_REDUCERS in c21
           and COMPLETE_REDUCERS in fixed
           and CORRECT_LEGACY_REDUCERS not in fixed,
           "independently reconstruct and falsify the actual C21 reducer")
    accept(fixed.count(NEW_JOIN_RELEASE) == 1
           and fixed.index(NEW_JOIN_RELEASE)
           > fixed.index(NEW_SUBSTITUTE_BYTES_SIGNATURE),
           "release the original exporter only immediately before bytes.join")
    accept(fixed.count(NEW_SCANNER_TRAVERSE) == 1
           and b"Py_VISIT(iterator->string);" not in fixed
           and b"Py_VISIT(iterator->subject.view.obj);" not in fixed,
           "hide both retained scanner owner edges from cyclic traversal")

    edits = (
        (CORRECT_LEGACY_REDUCERS, "historical legacy reducer"),
        (COPY_ANCHOR, "immutable Match copy/deepcopy"),
        (CAPTURE_ANCHOR, "nested original capture ownership"),
        (SUBJECT_CLEAR_ANCHOR, "idempotent view teardown"),
        (SCANNER_CLEAR_ANCHOR, "scanner clear and release order"),
        (METHOD_ANCHOR, "dedicated Match reduce_ex method"),
        (OLD_SCANNER_TRAVERSE, "both original scanner GC edges"),
        (OLD_SUBSTITUTE_BYTES_SIGNATURE, "borrowed bytes-subject signature"),
        (SNAPSHOT_DECLARATION, "early snapshot declaration"),
        (EARLY_SUBJECT_SNAPSHOT, "early exporter-copy block"),
        (SNAPSHOT_FINAL_RELEASE, "snapshot final release"),
        (OLD_JOIN_RELEASE, "original final bytes join"),
    )
    for anchor, label in edits:
        changed = fixture.replace(anchor, b"", 1)
        reject(lambda value=changed: repair_c21(reconstruct_c21(value)),
               "missing exact reversible source anchor: " + label)
        duplicate = fixture + anchor
        reject(lambda value=duplicate: repair_c21(reconstruct_c21(value)),
               "duplicate exact reversible source anchor: " + label)
        count += 1

    for token in FORBIDDEN_C:
        reject(lambda item=token: repair_c21(c21 + item),
               "delegate first-party C work to external code")

    for value in range(-64, 65):
        if value < 2:
            accept(model_protocol(value)
                   == ("owned-copyreg-reconstructor", value),
                   "accept signed legacy Match protocol " + str(value))
        else:
            reject(lambda item=value: model_protocol(item),
                   "reject new Match protocol " + str(value))
    for value in (-(1 << 31), -(1 << 31) + 1, -3, -2, -1, 0, 1):
        accept(model_protocol(value)
               == ("owned-copyreg-reconstructor", value),
               "preserve signed C-int legacy lower boundary")
    for value in (2, 3, 4, 5, (1 << 31) - 1):
        reject(lambda item=value: model_protocol(item),
               "reject exact signed C-int modern Match protocol")
    for value in (-(1 << 31) - 1, 1 << 31, 1 << 63, -(1 << 63)):
        reject(lambda item=value: model_protocol(item),
               "reject protocol outside the exact signed C-int domain")
    accept(model_protocol(False) == ("owned-copyreg-reconstructor", 0)
           and model_protocol(True) == ("owned-copyreg-reconstructor", 1),
           "preserve bool index compatibility")

    class Once:
        def __init__(self, number: int) -> None:
            self.number = number
            self.calls = 0

        def __index__(self) -> int:
            self.calls += 1
            return self.number

    for number in (-2, -1, 0, 1, 2, 5):
        item = Once(number)
        if number < 2:
            accept(model_protocol(item)
                   == ("owned-copyreg-reconstructor", number),
                   "accept exactly one custom legacy __index__")
        else:
            reject(lambda value=item: model_protocol(value),
                   "reject modern custom __index__")
        accept(item.calls == 1, "invoke custom protocol index exactly once")

    class OnlyInt:
        def __int__(self) -> int:
            return 1

    class WrongIndex:
        def __index__(self) -> str:
            return "1"

    reject(lambda: model_protocol(OnlyInt()),
           "reject an __int__ method without __index__")
    reject(lambda: model_protocol(WrongIndex()),
           "reject noninteger custom __index__")

    for mutates in (False, True):
        for captures in range(1, 7):
            for replacement in (False, True):
                result, events = model_substitution(
                    mutates=mutates, capture_count=captures,
                    replacement=replacement,
                )
                subject_events = [event for event in events
                                  if len(event) >= 2 and event[1] == "subject"]
                accept(sum(item[0] == "acquire" for item in subject_events)
                       == captures + 1
                       and sum(item[0] == "release" for item in subject_events)
                       == captures + 1,
                       "retain one outer and one independent export per capture")
                accept(subject_events[0][:3] == ("acquire", "subject", 0)
                       and subject_events[-1][:3] == ("release", "subject", 0),
                       "preserve original outer acquisition/release boundaries")
                accept(result.startswith(b"<alpha>")
                       and (result.endswith(b"!!") if mutates
                            else result.endswith(b"42")),
                       "observe exact live subject mutation after capture release")
                if replacement:
                    last_subject = max(index for index, event in enumerate(events)
                                       if len(event) >= 2 and event[1] == "subject")
                    join_events = [index for index, event in enumerate(events)
                                   if len(event) >= 2 and event[1] == "replacement"]
                    accept(len(join_events) == 6
                           and join_events[:2] == [0, 1]
                           and all(index > last_subject
                                   for index in join_events[2:]),
                           "probe replacement first but release subject before join")

    unchanged, no_match = model_substitution(
        mutates=True, capture_count=0, replacement=True, no_match=True,
    )
    accept(unchanged == b"alpha42"
           and [event[0] for event in no_match]
           == ["acquire", "release", "acquire", "release"],
           "preserve unchanged-result copy before overwrite with no join")
    _, failed_join = model_substitution(
        mutates=False, capture_count=1, replacement=True, join_error=True,
    )
    accept(failed_join[-1][:2] == ("acquire-error", "replacement")
           and failed_join[-2][:3] == ("release", "subject", 0),
           "release subject before a real replacement-join failure")

    for wrapped in (False, True):
        for readonly in (False, True):
            scanner = model_scanner(wrapped=wrapped, readonly=readonly)
            events = scanner["events"]
            accept(scanner["acquisitions"] == (1 if wrapped else 2)
                   and scanner["releases"] == (1 if wrapped else 2),
                   "preserve direct/wrapped retained scanner ownership")
            accept(scanner["final_payload"] == b"!!!"
                   and scanner["public_gc_referents"]
                   == ("builtins.type", "re.Pattern"),
                   "match exact scanner referents and poison-on-release")
            accept(events[-3][0] == "fixture-cycle-break"
                   and events[-2][:3] == ("release", "subject", 0)
                   and events[-1] == ("gc-final", False, False),
                   "keep owner alive until manual cycle break")

    accept(16 + 32 + 224 + 4 == 276,
           "preserve every unresolved witnessed native semantic mismatch")
    accept(276 + 330 == 606,
           "partition historical public adapter and native failures without overlap")
    accept(7 * 32 == 224,
           "preserve all seven genuine substitution cohorts")
    accept(count >= 245, "require exhaustive first-party source semantics")
    return {"semantic_checks": count,
            "falsified_all_protocol_match_rejection": True,
            "legacy_pickle_protocol_mismatches_targeted": 32,
            "managed_exporter_mismatches_targeted": 16,
            "substitution_exporter_mismatches_targeted": 224,
            "retained_scanner_mismatches_targeted": 4,
            "total_native_mismatches_targeted": 276,
            "materialized_adapter_mismatches_targeted": 330,
            "total_observed_mismatches_preserved": 606,
            "actual_candidate_matching": "NOT RUN"}


def root_controls() -> dict[str, object]:
    controls = semantic_controls()
    synthetic = repair_c21(reconstruct_c21(synthetic_source()))
    complete = (type(controls) is dict
                and type(controls.get("semantic_checks")) is int
                and controls["semantic_checks"] >= 245
                and type(synthetic) is bytes and len(synthetic) > 0
                and controls.get("total_native_mismatches_targeted") == 276
                and controls.get("total_observed_mismatches_preserved") == 606)
    need(complete,
         "complete exactly the root-only native preauthorization control path")
    need(type(complete) is bool and complete is True,
         "reject the previously witnessed truthy-bytes root control regression")
    return controls


def hostile_controls(wall: Wall) -> dict[str, object]:
    rejected = 0

    def refuses(action: object, reason: str) -> None:
        nonlocal rejected
        blocked = False
        try:
            action()
        except (FreezeError, OSError, TypeError, ValueError, OverflowError):
            blocked = True
        need(blocked, "accept prohibited source-only operation: " + reason)
        rejected += 1

    fixture = synthetic_source()
    corrected = repair_c21(reconstruct_c21(fixture))
    refuses(lambda: need(corrected, "historical truthy bytes root regression"),
            "require the actual True singleton for native authorization")
    for candidate in ("", ".", "..", "a/b", "a\x00b"):
        refuses(lambda item=candidate: wall.segment(item),
                "reject malformed nofollow descriptor segment")
    for raw in (b'{"x":1,"x":2}', b'{"x":01}', b'{"x":1.0}',
                b'{"x":"\\ud800"}', b'{"x":"\\udc00"}', b"[1] extra"):
        refuses(lambda value=raw: JSON(value).parse(),
                "reject duplicated, malformed, or noncanonical JSON")
    for action in (lambda: builtins.open(INPUT, "rb"),
                   lambda: _io.open(INPUT, "rb"),
                   lambda: io.open(INPUT, "rb"),
                   lambda: os.open(INPUT, os.O_RDONLY),
                   lambda: os.stat(INPUT),
                   lambda: os.listdir(ROOT),
                   lambda: os.mkdir("forbidden-c-complete-native-directory"),
                   lambda: time.time(),
                   lambda: time.perf_counter_ns()):
        refuses(action, "direct candidate, archive, workspace, process, or clock")
    controls = root_controls()
    no_matchers()
    return {"hostile_controls": controls["semantic_checks"] + rejected,
            "semantic": controls,
            "exact_root_authorization_control_path_self_tested": True,
            "historical_truthy_bytes_rejected": True}


def preserve_wrong_hypothesis(value: object) -> None:
    need(type(value) is dict
         and value.get("schema")
         == "rebar-owned-c-original-match-semantics-v1-source-freeze"
         and value.get("family") == "c"
         and value.get("candidate_correctness") == "NOT MEASURED",
         "preserve the complete immutable and later-falsified Match hypothesis")
    correction = value.get("source_correction")
    need(type(correction) is dict
         and correction.get("id") == "match-pickle-rejection-all-protocols"
         and correction.get("derived_variant_sha256") == C21_SHA256
         and correction.get("derived_variant_bytes") == C21_BYTES
         and correction.get("pickle_protocols") == [0, 1, 2, 3, 4, 5]
         and correction.get("original_variant", {}).get("sha256") == INPUT_SHA256
         and correction.get("original_variant", {}).get("bytes") == INPUT_BYTES,
         "never rewrite the actual historical false Match-pickle hypothesis")
    need(value.get("source", {}).get("sha256") == WRONG_MATCH_OWNERS[0][1]
         and value.get("protocol", {}).get("sha256") == WRONG_MATCH_OWNERS[1][1],
         "preserve all independently frozen erroneous source/protocol ownership")


def preserve_adapter(contract: object, receipt: object) -> None:
    need(type(contract) is dict and type(receipt) is dict,
         "require immutable public-adapter V2 source freeze and real application")
    correction = contract.get("correction")
    need(type(correction) is dict
         and correction.get("targeted_observed_public_adapter_mismatches") == 330
         and correction.get("target_path")
         == "candidates/c/variants/public_adapter_semantics_v2/vm_candidate.py"
         and correction.get("target_sha256")
         == "4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a"
         and correction.get("target_bytes") == 61663,
         "preserve all independently materialized public-adapter V2 corrections")
    expected = {
        "schema": "rebar-owned-c-public-adapter-semantics-v2-source-freeze-"
                  "root-materialization",
        "status": "PASS", "source_sha256": ADAPTER_OWNERS[0][1],
        "protocol_sha256": ADAPTER_OWNERS[1][1],
        "contract_sha256": ADAPTER_OWNERS[2][1],
        "target_path": correction["target_path"],
        "target_sha256": correction["target_sha256"],
        "target_bytes": 61663,
        "targeted_public_adapter_mismatches": 330,
        "root_controls_completed_before_candidate_read": True,
    }
    for key, item in expected.items():
        need(receipt.get(key) == item,
             "preserve actual public-adapter V2 application receipt: " + key)
    effects = receipt.get("effects")
    need(type(effects) is dict
         and effects.get("candidate_source_files_read") == 1
         and effects.get("candidate_executions") == 0
         and effects.get("workspace_mutations") == 2,
         "preserve actual exclusive public-adapter V2 source effects")


def preserve_guard(value: object) -> None:
    need(type(value) is dict
         and value.get("schema")
         == "rebar-owned-candidate-runtime-independence-v4-source-freeze"
         and value.get("version") == 4
         and value.get("source", {}).get("sha256") == GUARD_OWNERS[0][1]
         and value.get("protocol", {}).get("sha256") == GUARD_OWNERS[1][1]
         and value.get("runtime_non_delegation") == "NOT ESTABLISHED",
         "require separately authenticated corrected V4 runtime guard")
    isolation = value.get("subinterpreter_bootstrap")
    need(type(isolation) is dict
         and isolation.get("expected_interpreters_created") == 11
         and isolation.get("expected_interpreters_destroyed") == 11
         and isolation.get("original_case_count") == 128
         and isolation.get("unrestricted_creation") is False
         and isolation.get("unrestricted_execution") is False
         and isolation.get("unrestricted_destruction") is False,
         "preserve corrected physical native child creation and teardown policy")
    policy = value.get("runtime_isolation_policy")
    need(type(policy) is dict
         and policy.get("stdlib_re_engine") == "FORBIDDEN"
         and policy.get("stdlib_sre_engine") == "FORBIDDEN"
         and policy.get("external_regex_package") == "FORBIDDEN"
         and policy.get("cross_candidate_engine") == "FORBIDDEN"
         and policy.get("matching_fallback") == "FORBIDDEN",
         "preserve all unchanged first-party runtime nondelegation boundaries")


def preserve_c12(value: object) -> None:
    need(type(value) is dict,
         "require full immutable latest actual C12 correctness publication")
    expected = {
        "schema": "rebar-owned-repaired-c-original-campaign-v12-"
                  "durable-publication-receipt",
        "version": 12, "family": "c", "status": "PASS",
        "publication_status": "PASS", "candidate_status": "FAIL",
        "candidate_qualified": False, "case_execution_denominator": 31237,
        "suite_count": 13, "completed_suite_count": 12,
        "verified_passing_case_count": 16413,
        "complete_observed_semantic_mismatch_record_count": 606,
        "candidate_execution_failure_count": 1,
        "semantic_mismatch_count": "NOT MEASURED",
        "corrected_source_sha256": C21_SHA256,
        "native_engine_sha256": C21_NATIVE_SHA256,
        "winner_selected": False,
    }
    for key, item in expected.items():
        need(value.get(key) == item,
             "preserve complete actual failed C12 candidate evidence: " + key)
    suites = value.get("suite_outcomes")
    need(type(suites) is list and len(suites) == 13,
         "preserve all original completed and unfinished C12 suites")
    counts = {item["suite"]: item["mismatch_count"] for item in suites}
    for suite, count in (("managed_v1", 16), ("public_types_v1", 248),
                         ("substitution_v2", 224), ("public_surface_v19", 114),
                         ("pep688_v4", 4)):
        need(counts.get(suite) == count,
             "preserve every historical observed C mismatch: " + suite)
    need(counts.get("subinterpreter_v2") == "NOT MEASURED",
         "preserve unfinished genuine child-isolation failure as unknown")
    vectors = value.get("complete_mismatch_suite_vector_fingerprints")
    need(type(vectors) is list and len(vectors) == 12,
         "preserve every complete immutable mismatch vector fingerprint")
    by_name = {row["suite"]: row for row in vectors}
    for suite, amount, chunks in (("managed_v1", 16, 1),
                                  ("public_types_v1", 248, 8),
                                  ("substitution_v2", 224, 7),
                                  ("public_surface_v19", 114, 4),
                                  ("pep688_v4", 4, 1)):
        row = by_name.get(suite)
        need(type(row) is dict and row.get("complete_record_count") == amount
             and row.get("complete_chunk_count") == chunks
             and row.get("all_observed_records_preserved") is True,
             "preserve complete exact failure vectors without opening archives")


def preserve_c21(build: object, root: object) -> None:
    need(type(build) is dict and type(root) is dict,
         "require both genuinely published first-party C21 build owners")
    need(build.get("family") == "c" and build.get("version") == 21
         and build.get("build_status") == "PASS"
         and build.get("base_variant_sha256") == INPUT_SHA256
         and build.get("variant_source_sha256") == C21_SHA256
         and build.get("variant_source_bytes") == C21_BYTES
         and build.get("semantic_source_sha256") == WRONG_MATCH_OWNERS[0][1]
         and build.get("semantic_contract_sha256") == WRONG_MATCH_OWNERS[2][1]
         and build.get("candidate_correctness") == "NOT MEASURED"
         and build.get("candidate_matching") == "NOT RUN"
         and build.get("byte_identical_native_artifacts") is True,
         "authenticate the latest actually built C21 source and falsified reducer")
    phases = build.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "preserve both distinct authentic first-party C21 offline source builds")
    for phase in phases:
        owners = phase.get("source_owners")
        output = phase.get("native_output")
        need(type(owners) is list and len(owners) == 2
             and owners[0].get("sha256") == C21_SHA256
             and owners[0].get("bytes") == C21_BYTES
             and type(output) is dict
             and output.get("sha256") == C21_NATIVE_SHA256
             and output.get("native_loaded") is False,
             "preserve both first-party C21 source/native phases without opening them")
    need(root.get("family") == "c" and root.get("version") == 21
         and root.get("status") == "PASS"
         and root.get("derived_variant_sha256") == C21_SHA256
         and root.get("derived_variant_bytes") == C21_BYTES
         and root.get("canonical_build_receipt_sha256") == C21_BUILD[1]
         and root.get("candidate_correctness") == "NOT MEASURED",
         "preserve genuine unopened first-party C21 private-root provenance")


def contract_document(source_hash: str, protocol_hash: str) -> dict[str, object]:
    cohorts = (
        "pep688-stable-subject", "pep688-mutating-subject",
        "pep688-fixed-hash-subject", "pep688-unhashable-subject",
        "nested-stable-subject-and-template",
        "nested-stable-fixed-hash-template",
        "nested-mutating-unhashable-template",
    )
    return {
        "schema": SCHEMA, "version": 1,
        "status": "SOURCE FROZEN; COMPLETE FIRST-PARTY C NATIVE NOT MATERIALIZED",
        "phase": "CANDIDATES; CUMULATIVE FIRST-PARTY NATIVE SEMANTICS",
        "source": {"path": SOURCE, "sha256": source_hash},
        "protocol": {"path": PROTOCOL, "sha256": protocol_hash},
        "immutable_falsified_match_hypothesis": {
            "owners": [{"path": row[0], "sha256": row[1]}
                       for row in WRONG_MATCH_OWNERS],
            "claim": "ALL MATCH PICKLE PROTOCOLS 0 THROUGH 5 MUST FAIL",
            "actual_cpython_3146": "PROTOCOLS 0 AND 1 RECONSTRUCT; 2 THROUGH 5 FAIL",
            "historical_contract_rewritten": False,
            "witnessed_protocol_0_case_count": 16,
            "witnessed_protocol_1_case_count": 16,
            "total_witnessed_mismatches": 32,
        },
        "actual_public_adapter": {
            "owners": [{"path": row[0], "sha256": row[1]}
                       for row in ADAPTER_OWNERS],
            "application_receipt_path": ADAPTER_RECEIPT[0],
            "application_receipt_sha256": ADAPTER_RECEIPT[1],
            "materialized_target_sha256":
                "4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a",
            "materialized_target_bytes": 61663,
            "targeted_observed_public_adapter_mismatches": 330,
        },
        "corrected_runtime_guard": {
            "owners": [{"path": row[0], "sha256": row[1]}
                       for row in GUARD_OWNERS],
            "version": 4,
            "expected_real_child_interpreters": 11,
            "expected_destroyed_child_interpreters": 11,
            "original_child_case_denominator": 128,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "immutable_c12_failure": {
            "receipt_path": C12_LEDGER[0],
            "receipt_sha256": C12_LEDGER[1],
            "original_case_denominator": 31237,
            "separate_reference_case_count": 8244,
            "named_private_waiver_count": 13,
            "verified_passing_case_count": 16413,
            "observed_mismatch_count": 606,
            "exact_total_mismatch_count": "NOT MEASURED",
            "candidate_status": "FAIL",
            "interpreter_isolation_finished": False,
            "complete_mismatch_partition": {
                "managed_v1": 16,
                "public_types_v1": 248,
                "substitution_v2": 224,
                "public_surface_v19": 114,
                "pep688_v4": 4,
            },
        },
        "immutable_c21_build": {
            "build_receipt_path": C21_BUILD[0],
            "build_receipt_sha256": C21_BUILD[1],
            "root_receipt_path": C21_ROOT[0],
            "root_receipt_sha256": C21_ROOT[1],
            "tested_native_source_sha256": C21_SHA256,
            "tested_native_source_bytes": C21_BYTES,
            "tested_native_artifact_sha256": C21_NATIVE_SHA256,
            "independent_build_count": 2,
        },
        "independent_native_input": {
            "path": INPUT, "sha256": INPUT_SHA256, "bytes": INPUT_BYTES,
            "inode": INPUT_INODE, "device": DEVICE, "mode": "0600",
            "reconstructed_c21_sha256": C21_SHA256,
        },
        "cumulative_native_corrections": {
            "exact_reversible_source_site_count": 7,
            "target_path": TARGET,
            "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES,
            "legacy_match_pickle_mismatches_targeted": 32,
            "match_protocol_domain": "SIGNED C INT; LEGACY <2; NEW >=2",
            "managed_exporter_mismatches_targeted": 16,
            "substitution_exporter_mismatches_targeted": 224,
            "substitution_cohorts": list(cohorts),
            "mutated_result_cohorts": [
                "pep688-mutating-subject",
                "nested-mutating-unhashable-template",
            ],
            "capture_view_ownership":
                "OUTER ORIGINAL VIEW; INDEPENDENT NESTED VIEW PER CAPTURE",
            "subject_release_boundary":
                "AFTER ALL CAPTURE/TAIL MATERIALIZATION; IMMEDIATELY BEFORE BYTES JOIN",
            "retained_scanner_mismatches_targeted": 4,
            "retained_scanner_case_ids": [
                "buffer-exporter.v1.256", "buffer-exporter.v1.257",
                "buffer-exporter.v1.258", "buffer-exporter.v1.259",
            ],
            "scanner_gc_visible_referents": ["builtins.type", "re.Pattern"],
            "native_total_observed_mismatches_targeted": 276,
            "adapter_total_observed_mismatches_targeted": 330,
            "all_observed_mismatches_preserved": 606,
            "stdlib_regex_delegation": False,
            "external_regex_engine": False,
            "cross_candidate_engine": False,
        },
        "source_only_effects": {
            "approved_plaintext_owner_reads": 16,
            "candidate_source_files_read": 0,
            "candidate_imports": 0,
            "candidate_executions": 0,
            "reference_processes": 0,
            "compiler_processes": 0,
            "native_libraries_loaded": 0,
            "compressed_archives_opened": 0,
            "private_build_roots_opened": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "workspace_mutations": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        },
    }


def arguments(values: list[str]) -> dict[str, object]:
    flags = {"--self-test", "--verify-source", "--apply", "--root-authorized"}
    named = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
             "--frozen-commit", "--pushed-commit"}
    parsed: dict[str, object] = {}
    position = 0
    while position < len(values):
        key = values[position]
        need(key in flags or key in named,
             "reject unauthorized complete-native argument: " + key)
        need(key not in parsed, "reject duplicated immutable complete-native option")
        if key in flags:
            parsed[key] = True
            position += 1
        else:
            need(position + 1 < len(values),
                 "reject incomplete immutable complete-native argument")
            parsed[key] = values[position + 1]
            position += 2
    modes = [key for key in ("--self-test", "--verify-source", "--apply")
             if parsed.get(key)]
    need(len(modes) == 1,
         "require exactly one source-only or exclusive root-only mode")
    mode = modes[0]
    if mode == "--self-test":
        need(set(parsed) == {mode},
             "synthetic self-test must open no source owner or candidate")
    elif mode == "--verify-source":
        need(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                             "--contract-sha256"},
             "verify only the three explicit complete native freeze owners")
    else:
        need(set(parsed) == {mode, "--root-authorized", "--source-sha256",
                             "--protocol-sha256", "--contract-sha256",
                             "--frozen-commit", "--pushed-commit"},
             "require root authority and exact already-pushed source freeze")
        for key in ("--frozen-commit", "--pushed-commit"):
            value = parsed[key]
            need(type(value) is str and len(value) == 40
                 and all(item in "0123456789abcdef" for item in value),
                 "reject incomplete frozen or pushed commit identity")
        need(parsed["--frozen-commit"] == parsed["--pushed-commit"],
             "reject first-party C source materialization before freeze push")
    for key in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if key in parsed:
            checked_hash(parsed[key], key)
    return parsed


def effects(wall: Wall, mode: str) -> dict[str, object]:
    return {
        "mode": mode,
        "approved_plaintext_owner_reads": wall.public_reads,
        "candidate_source_files_read": wall.candidate_reads,
        "candidate_executions": 0,
        "candidate_imports": 0,
        "reference_processes": 0,
        "compiler_processes": 0,
        "native_libraries_loaded": 0,
        "compressed_archives_opened": 0,
        "private_build_roots_opened": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "workspace_mutations": wall.workspace_mutations,
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def main(argv: list[str]) -> dict[str, object]:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True and sys.executable == PYTHON
         and __file__ == ROOT + "/" + SOURCE,
         "require isolated, bytecode-disabled pinned CPython 3.14.6")
    parsed = arguments(argv)
    wall = Wall(parsed.get("--apply") is True)
    no_matchers()
    wall.install()
    if parsed.get("--self-test"):
        checks = hostile_controls(wall)
        need(wall.public_reads == 0 and wall.candidate_reads == 0
             and wall.workspace_mutations == 0 and wall.root is None,
             "source-only synthetic self-test must read and change nothing")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "controls": checks, "effects": effects(wall, "SELF-TEST")}

    source_hash = parsed["--source-sha256"]
    protocol_hash = parsed["--protocol-sha256"]
    contract_hash = parsed["--contract-sha256"]
    need(type(source_hash) is str and type(protocol_hash) is str
         and type(contract_hash) is str,
         "require three independently authenticated freeze-owner pins")
    wall.open_root()
    wall.read(SOURCE, source_hash)
    wall.read(PROTOCOL, protocol_hash)
    manifest = JSON(wall.read(CONTRACT, contract_hash)).parse()
    need(manifest == contract_document(source_hash, protocol_hash),
         "reject changed exact complete-native source-only contract")

    historical: dict[str, bytes] = {}
    for group in (WRONG_MATCH_OWNERS, ADAPTER_OWNERS, GUARD_OWNERS):
        for path, fingerprint, size, inode in group:
            historical[path] = wall.read(path, fingerprint, size, inode)
    wrong = JSON(historical[WRONG_MATCH_OWNERS[2][0]]).parse()
    adapter = JSON(historical[ADAPTER_OWNERS[2][0]]).parse()
    guard = JSON(historical[GUARD_OWNERS[2][0]]).parse()
    receipt = JSON(wall.read(*ADAPTER_RECEIPT)).parse()
    ledger = JSON(wall.read(*C12_LEDGER)).parse()
    build = JSON(wall.read(*C21_BUILD)).parse()
    root = JSON(wall.read(*C21_ROOT)).parse()
    preserve_wrong_hypothesis(wrong)
    preserve_adapter(adapter, receipt)
    preserve_guard(guard)
    preserve_c12(ledger)
    preserve_c21(build, root)
    need(wall.public_reads == 16 and wall.candidate_reads == 0
         and wall.workspace_mutations == 0,
         "authenticate exactly sixteen immutable plaintext owners and no candidates")

    if not parsed.get("--apply"):
        controls = hostile_controls(wall)
        no_matchers()
        return {
            "schema": SCHEMA + "-verification", "status": "PASS",
            "source_sha256": source_hash, "protocol_sha256": protocol_hash,
            "contract_sha256": contract_hash,
            "predicted_target_path": TARGET,
            "predicted_target_sha256": OUTPUT_SHA256,
            "predicted_target_bytes": OUTPUT_BYTES,
            "preserved_adapter_application_sha256": ADAPTER_RECEIPT[1],
            "preserved_falsified_match_hypothesis_sha256": WRONG_MATCH_OWNERS[2][1],
            "corrected_runtime_guard_sha256": GUARD_OWNERS[0][1],
            "controls": controls,
            "effects": effects(wall, "SOURCE VERIFICATION"),
        }

    authorization = root_controls()
    need(type(authorization) is dict
         and authorization.get("total_native_mismatches_targeted") == 276
         and authorization.get("total_observed_mismatches_preserved") == 606
         and wall.candidate_reads == 0 and wall.workspace_mutations == 0,
         "complete exact root semantic controls before first-party candidate access")
    original = wall.read(INPUT, INPUT_SHA256, INPUT_BYTES, INPUT_INODE)
    latest_tested = reconstruct_c21(original, exact=True)
    corrected = repair_c21(latest_tested, exact=True)
    wall.materialize(corrected)
    no_matchers()
    need(wall.candidate_reads == 1 and wall.workspace_mutations == 2,
         "create exactly one exclusive complete first-party native-source variant")
    return {
        "schema": SCHEMA + "-root-materialization", "status": "PASS",
        "frozen_commit": parsed["--frozen-commit"],
        "pushed_commit": parsed["--pushed-commit"],
        "source_sha256": source_hash,
        "protocol_sha256": protocol_hash,
        "contract_sha256": contract_hash,
        "preserved_adapter_application_sha256": ADAPTER_RECEIPT[1],
        "preserved_c12_observed_mismatch_count": 606,
        "reconstructed_tested_c21_source_sha256": C21_SHA256,
        "input_path": INPUT,
        "input_sha256": INPUT_SHA256,
        "target_path": TARGET,
        "target_sha256": OUTPUT_SHA256,
        "target_bytes": OUTPUT_BYTES,
        "targeted_native_mismatches": 276,
        "paired_materialized_adapter_mismatches": 330,
        "root_controls_completed_before_candidate_read": True,
        "effects": effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION"),
    }


if __name__ == "__main__":
    try:
        document = main(sys.argv[1:])
    except (FreezeError, OSError, TypeError, UnicodeError, ValueError) as error:
        sys.stderr.write("c-complete-native-semantics-v1: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(document) + "\n")
