#!/usr/bin/env python3
"""Freeze first-party, reference-counted ownership of Rust regex engines."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("native-handle lease source freeze cannot load matching engines")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_native_handle_lease_v1.py"
PROTOCOL = "oracle/phase2/RUST-NATIVE-HANDLE-LEASE-V1.md"
CONTRACT = "oracle/phase2/rust-native-handle-lease-v1.json"
PARENT = "candidates/rust/variants"
DIRECTORY = "native_handle_lease_v1"
TARGET = PARENT + "/" + DIRECTORY + "/py_bridge.c"
SCHEMA = "rebar-owned-rust-native-handle-lease-v1-source-freeze"
DEVICE = 2064
PARENT_INODE = 524946
MAX_OWNER_BYTES = 1_048_576
NOT_MEASURED = "NOT MEASURED"
BASE_SHA256 = "e4ee92d9d651600d94cf371f6437638b639b3418103cb20044fbdd26a60d5d57"
BASE_BYTES = 180947
ENGINE_SHA256 = "7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136"
ADAPTER_SHA256 = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
PERFORMANCE_RECEIPT_SHA256 = "db9288ea7c0a00e0c702acb7520e74482f8fb3c90cccee8f6e247f592811f2b3"
PERFORMANCE_SUMMARY_SHA256 = "7366a81a3fa1352cb6e8a165d5c45871f0081bda7e5c392e07d7bbf3f3a4cfef"
HISTORICAL_AUDITED_ENGINE_BINARY_SHA256 = "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237"
HISTORICAL_AUDITED_BRIDGE_BINARY_SHA256 = "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256"

OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_ledger", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("materialized_literal_bridge", "candidates/rust/variants/literal_bridge_fastpath_v1/py_bridge.c",
     BASE_SHA256, BASE_BYTES, 526538),
    ("actual_literal_bridge_application", "oracle/phase2/evidence/rust-literal-bridge-fastpath-v1-application.json",
     "48fbc982f5e490bc44e7fc0e2c0d25a88e2187371b75ed86ffc6042f41d185e6", 1082, 526544),
    ("literal_bridge_source", "tools/apply_owned_rust_literal_bridge_fastpath_v1.py",
     "e5745829c7e6099644218522e381b1d6dbfc49457546d10e4ef1f2dd39d10258", 62151, 430345),
    ("literal_bridge_protocol", "oracle/phase2/RUST-LITERAL-BRIDGE-FASTPATH-V1.md",
     "5ac3d86cb56b9497a465ef67ce28ee7be12020ed415a207bb92a561c9f1647f7", 5229, 526436),
    ("literal_bridge_contract", "oracle/phase2/rust-literal-bridge-fastpath-v1.json",
     "edc4ce1cb34667a449773548de46d48292b5bf61f9bd9f334bdc271c7bac0323", 8497, 526438),
    ("independent_exact_literal_engine", "candidates/rust/variants/exact_literal_fastpath_v1/lib.rs",
     ENGINE_SHA256, 194276, 525959),
    ("corrected_adapter", "candidates/rust/variants/corrected_comment_adapter_v2/rust_candidate.py",
     ADAPTER_SHA256, 34039, 525454),
    ("actual_corrected_performance_receipt",
     "oracle/phase2/evidence/rust-corrected-public-performance-v4-v33-"
     "corrected-performance-run-001-publication-receipt.json",
     PERFORMANCE_RECEIPT_SHA256, 118943, 526289),
    ("actual_corrected_public_summary",
     "experiments/rust_corrected_public_performance_v4/v33-corrected-performance-run-001/"
     "public-416-performance-summary.raw.json",
     PERFORMANCE_SUMMARY_SHA256, 102598, 526288),
    ("actual_original_suite_pass",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v33-"
     "rust-full-public-semantic-source-root-provenance-original-p0-v28-publication-receipt.json",
     "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064", 12067, 526161),
    ("actual_wider_public_pass",
     "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-"
     "publication-receipt.json",
     "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9", 6889, 525451),
    ("historical_prior_build_static_non_delegation",
     "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json",
     "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203", 16427, 525089),
)

CAPSULE_HELPER = b"""static const char rust_native_handle_name[] = "rebar.rust.native_engine.v1";

static void rust_native_handle_destructor(PyObject *owner) {
    void *handle = PyCapsule_GetPointer(owner, rust_native_handle_name);
    if (handle != NULL) {
        rebar_free(handle);
    } else {
        PyErr_Clear();
    }
}

static PyObject *rust_native_handle_owner(void *handle) {
    if (handle == NULL) {
        PyErr_SetString(PyExc_ValueError, "Rust engine handles cannot be null");
        return NULL;
    }
    return PyCapsule_New(
        handle, rust_native_handle_name, rust_native_handle_destructor
    );
}

static void *rust_native_handle(PyObject *owner) {
    if (!PyCapsule_CheckExact(owner)) {
        PyErr_SetString(
            PyExc_TypeError,
            "expected an owned Rust regular-expression engine handle"
        );
        return NULL;
    }
    return PyCapsule_GetPointer(owner, rust_native_handle_name);
}

"""

TUPLE_ANCHOR = b"static PyObject *rust_owned_tuple4("
NORMAL_OLD = (
    b"    PyObject *result = rust_owned_tuple4(PyLong_FromVoidPtr(handle), "
    b"PyLong_FromSize_t(rebar_groups(handle)), "
    b"PyLong_FromUnsignedLong(rebar_flags(handle)), names);\n"
    b"    if (result == NULL) rebar_free(handle);\n"
    b"    return result;\n"
)
NORMAL_NEW = b"""    PyObject *owner = rust_native_handle_owner(handle);
    if (owner == NULL) {
        Py_DECREF(names);
        rebar_free(handle);
        return NULL;
    }
    return rust_owned_tuple4(
        owner,
        PyLong_FromSize_t(rebar_groups(handle)),
        PyLong_FromUnsignedLong(rebar_flags(handle)),
        names
    );
"""
SCANNER_OLD = b"""    result = rust_owned_tuple4(
        PyLong_FromVoidPtr(handle),
        PyLong_FromSize_t(rebar_groups(handle)),
        PyLong_FromUnsignedLong(rebar_flags(handle)),
        PyDict_New()
    );
    if (result == NULL) {
        rebar_free(handle);
    }
"""
SCANNER_NEW = b"""    PyObject *owner = rust_native_handle_owner(handle);
    if (owner == NULL) {
        rebar_free(handle);
        goto cleanup;
    }
    result = rust_owned_tuple4(
        owner,
        PyLong_FromSize_t(rebar_groups(handle)),
        PyLong_FromUnsignedLong(rebar_flags(handle)),
        PyDict_New()
    );
"""
FREE_OLD = b"""static PyObject *bridge_free(PyObject *module, PyObject *value) {
    (void)module;
    void *handle = rust_native_handle(value);
    if (PyErr_Occurred()) return NULL;
    rebar_free(handle);
    Py_RETURN_NONE;
}
"""
FREE_NEW = b"""static PyObject *bridge_free(PyObject *module, PyObject *value) {
    (void)module;
    if (rust_native_handle(value) == NULL) return NULL;
    Py_RETURN_NONE;
}
"""
ITERATOR_FIELDS_OLD = b"""    PyObject *pattern;
    PyObject *string;
    PyObject *groupindex;
    const void *handle;
"""
ITERATOR_FIELDS_NEW = b"""    PyObject *pattern;
    PyObject *string;
    PyObject *groupindex;
    PyObject *handle_owner;
    const void *handle;
"""
ITERATOR_CLEAR_OLD = b"""    Py_CLEAR(iterator->string);
    Py_CLEAR(iterator->pattern);
    Py_CLEAR(iterator->groupindex);
    return 0;
}
"""
ITERATOR_CLEAR_NEW = b"""    Py_CLEAR(iterator->string);
    Py_CLEAR(iterator->pattern);
    Py_CLEAR(iterator->groupindex);
    iterator->handle = NULL;
    Py_CLEAR(iterator->handle_owner);
    return 0;
}
"""
ITERATOR_DEFINITION_OLD = (
    b"static PyObject *rust_iterator_create(PyTypeObject *type, PyObject *pattern, "
    b"void *handle, PyObject *groupindex, PyObject *pattern_value, size_t groups, "
    b"PyObject *value, PyObject *pos, PyObject *endpos) {\n"
    b"    if (groups != rebar_groups(handle)) {\n"
)
ITERATOR_DEFINITION_NEW = (
    b"static PyObject *rust_iterator_create(PyTypeObject *type, PyObject *pattern, "
    b"PyObject *handle_owner, void *handle, PyObject *groupindex, "
    b"PyObject *pattern_value, size_t groups, PyObject *value, PyObject *pos, "
    b"PyObject *endpos) {\n"
    b"    if (rust_native_handle(handle_owner) != handle) {\n"
    b"        if (!PyErr_Occurred()) {\n"
    b"            PyErr_SetString(PyExc_ValueError, "
    b'"Rust iterator engine owner does not match the compiled program");\n'
    b"        }\n"
    b"        return NULL;\n"
    b"    }\n"
    b"    if (groups != rebar_groups(handle)) {\n"
)
ITERATOR_ACQUIRE_OLD = b"""    if (iterator == NULL) return NULL;
    iterator->pattern = Py_NewRef(pattern);
"""
ITERATOR_ACQUIRE_NEW = b"""    if (iterator == NULL) return NULL;
    iterator->handle_owner = Py_NewRef(handle_owner);
    iterator->pattern = Py_NewRef(pattern);
"""
BOUND_CREATE_OLD = (
    b"    return rust_iterator_create(type, args[0], handle, args[2], args[3], "
    b"groups, subject, pos, endpos);\n"
)
BOUND_CREATE_NEW = (
    b"    return rust_iterator_create(type, args[0], args[1], handle, args[2], "
    b"args[3], groups, subject, pos, endpos);\n"
)
DISPATCH_CREATE_OLD = b"""                PyObject *scanner = rust_iterator_create(
                    state->scanner_type,
                    pattern,
                    handle,
"""
DISPATCH_CREATE_NEW = b"""                PyObject *scanner = rust_iterator_create(
                    state->scanner_type,
                    pattern,
                    prefix[1],
                    handle,
"""


class FreezeError(Exception):
    """Reject unowned source, unsafe lifetime changes, or physical effects."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash genuine immutable source bytes")
    return hashlib.sha256(value).hexdigest()


def sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require a complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def pushed(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(char in "0123456789abcdef" for char in value),
            "require a complete pushed commit: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "subprocess", "socket", "threading", "multiprocessing",
                 "random", "json", "candidates", "rebar", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matching engines, candidates, processes, and dynamic loaders")


def canonical(value: object, depth: int = 0) -> str:
    require(depth < 64, "reject unbounded evidence nesting")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        replacements = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                        "\n": "\\n", "\r": "\\r", "\t": "\\t"}
        require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value),
                "reject unpaired evidence surrogates")
        return '"' + "".join(replacements.get(char, "\\u" + format(ord(char), "04x")
                                               if ord(char) < 32 else char)
                             for char in value) + '"'
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "require text evidence keys")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject floating or unknown evidence")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class SourceWall:
    """Permanently allow authenticated owners and one root-only fresh source."""

    def __init__(self, apply: bool) -> None:
        self.apply = apply
        self.allowed = frozenset((ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
                                  ROOT + "/" + CONTRACT)
                                 + tuple(ROOT + "/" + row[1] for row in OWNERS))
        self.stage = "source"
        self.owner_fds: set[int] = set()
        self.parent_fd: int | None = None
        self.child_fd: int | None = None
        self.output_fd: int | None = None
        self.output_opened = False
        self.output_synced = False
        self.child_synced = False
        self.parent_synced = False
        self.expected = b""
        self.written = 0
        self.blocked: dict[str, int] = {}
        self.installed = False

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise FreezeError("native-handle lease source wall rejected " + category)

    def owner_path(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and not path.endswith((".so", ".gz", ".jsonl")))

    @staticmethod
    def temporary(flags: object) -> bool:
        value = getattr(os, "O_TMPFILE", 0)
        return type(flags) is int and value != 0 and flags & value == value

    def directory_flags(self, flags: object) -> bool:
        required = os.O_DIRECTORY | os.O_NOFOLLOW
        forbidden = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_TRUNC | os.O_APPEND
        return type(flags) is int and flags & required == required and not flags & forbidden \
            and not self.temporary(flags)

    def output_flags(self, flags: object) -> bool:
        required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        forbidden = os.O_RDWR | os.O_TRUNC | os.O_APPEND | os.O_DIRECTORY
        return type(flags) is int and flags & required == required and not flags & forbidden \
            and not self.temporary(flags)

    def audit(self, event: str, values: tuple[object, ...]) -> None:
        if event == "open":
            path = values[0] if values else None
            flags = values[2] if len(values) > 2 else None
            readonly = (self.owner_path(path) and type(flags) is int and flags & os.O_NOFOLLOW
                        and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                                         | os.O_TRUNC | os.O_APPEND | os.O_DIRECTORY)
                        and not self.temporary(flags))
            parent = (self.apply and self.stage == "ready" and path == ROOT + "/" + PARENT
                      and self.directory_flags(flags))
            child = (self.apply and self.stage == "created" and path == DIRECTORY
                     and self.directory_flags(flags))
            output = (self.apply and self.stage == "child" and path == "py_bridge.c"
                      and self.output_flags(flags) and not self.output_opened)
            if not any((readonly, parent, child, output)):
                self.deny("unowned-private-native-proposal-hidden-or-write-open")
        elif event == "os.mkdir":
            path = values[0] if values else None
            mode = values[1] if len(values) > 1 else None
            descriptor = values[2] if len(values) > 2 else None
            if not (self.apply and self.stage == "parent" and path == DIRECTORY
                    and mode == 0o700 and descriptor == self.parent_fd):
                self.deny("unapproved-directory-mutation")
        elif (event in ("import", "compile", "exec", "marshal.loads", "code.__new__",
                        "sys.addaudithook", "os.system", "os.fork", "os.posix_spawn",
                        "os.rename", "os.replace", "os.remove", "os.unlink", "os.rmdir",
                        "os.chmod", "os.chown", "os.link", "os.symlink", "os.truncate",
                        "os.putenv", "os.unsetenv", "os.urandom", "os.getrandom")
              or event.startswith(("subprocess.", "socket.", "ctypes.", "threading.",
                                   "multiprocessing.", "tempfile.", "time.",
                                   "_interpreters.", "os.exec", "os.spawn"))):
            self.deny("candidate-native-process-clock-interpreter-or-dynamic-code")

    def forbidden(self, category: str):
        def reject(*_args: object, **_keywords: object) -> object:
            self.deny(category)
        return reject

    def install(self) -> None:
        require(not self.installed, "install one permanent source wall")
        raw_open, raw_read, raw_write = os.open, os.read, os.write
        raw_fstat, raw_close, raw_fsync, raw_mkdir = os.fstat, os.close, os.fsync, os.mkdir

        def guarded_open(path: object, flags: object, mode: int = 0o777,
                         *, dir_fd: object = None) -> int:
            require(type(flags) is int and type(mode) is int, "reject malformed open flags")
            readonly = (dir_fd is None and self.owner_path(path) and flags & os.O_NOFOLLOW
                        and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                                         | os.O_TRUNC | os.O_APPEND | os.O_DIRECTORY)
                        and not self.temporary(flags))
            parent = (self.apply and self.stage == "ready" and path == ROOT + "/" + PARENT
                      and dir_fd is None and self.directory_flags(flags))
            child = (self.apply and self.stage == "created" and path == DIRECTORY
                     and dir_fd == self.parent_fd and self.directory_flags(flags))
            output = (self.apply and self.stage == "child" and path == "py_bridge.c"
                      and dir_fd == self.child_fd and self.output_flags(flags)
                      and mode == 0o600 and not self.output_opened)
            if not any((readonly, parent, child, output)):
                self.deny("foreign-owner-directory-or-output-descriptor")
            descriptor = raw_open(path, flags, mode, dir_fd=dir_fd)
            require(type(descriptor) is int and descriptor >= 0
                    and descriptor not in self.owner_fds
                    and descriptor not in (self.parent_fd, self.child_fd, self.output_fd),
                    "reject reused or inherited descriptor")
            if readonly:
                self.owner_fds.add(descriptor)
            elif parent:
                self.parent_fd, self.stage = descriptor, "parent"
            elif child:
                self.child_fd, self.stage = descriptor, "child"
            else:
                self.output_fd, self.output_opened = descriptor, True
            return descriptor

        def guarded_read(descriptor: object, count: object) -> bytes:
            if type(descriptor) is not int or descriptor not in self.owner_fds \
                    or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES:
                self.deny("foreign-or-unbounded-descriptor-read")
            return raw_read(descriptor, count)

        def guarded_write(descriptor: object, value: object) -> int:
            if not self.apply or descriptor != self.output_fd \
                    or type(value) not in (bytes, memoryview):
                self.deny("unapproved-source-or-inherited-descriptor-write")
            block = bytes(value)
            if not block or block != self.expected[self.written:self.written + len(block)]:
                self.deny("incorrect-or-out-of-order-exclusive-source-output")
            count = raw_write(descriptor, value)
            require(type(count) is int and 0 < count <= len(block),
                    "reject incomplete exclusive source write")
            self.written += count
            return count

        def guarded_fstat(descriptor: object) -> os.stat_result:
            if type(descriptor) is not int or descriptor not in self.owner_fds \
                    and descriptor not in (self.parent_fd, self.child_fd, self.output_fd):
                self.deny("foreign-descriptor-metadata")
            return raw_fstat(descriptor)

        def guarded_close(descriptor: object) -> None:
            if descriptor in self.owner_fds:
                self.owner_fds.remove(descriptor)
            elif descriptor == self.output_fd:
                require(self.output_synced and self.written == len(self.expected),
                        "reject incomplete or unsynchronized output")
                self.output_fd = None
            elif descriptor == self.child_fd:
                require(self.child_synced and self.output_fd is None,
                        "synchronize the child directory first")
                self.child_fd = None
            elif descriptor == self.parent_fd:
                require(self.parent_synced and self.child_fd is None,
                        "synchronize the variants parent first")
                self.parent_fd = None
            else:
                self.deny("foreign-or-inherited-descriptor-close")
            raw_close(descriptor)

        def guarded_fsync(descriptor: object) -> None:
            if not self.apply:
                self.deny("source-only-filesystem-sync")
            if descriptor == self.output_fd:
                require(self.written == len(self.expected), "synchronize complete source only")
                self.output_synced = True
            elif descriptor == self.child_fd:
                require(self.output_synced and self.output_fd is None,
                        "synchronize the completed child only")
                self.child_synced = True
            elif descriptor == self.parent_fd:
                require(self.child_synced and self.child_fd is None,
                        "synchronize the completed parent only")
                self.parent_synced = True
            else:
                self.deny("foreign-filesystem-sync")
            raw_fsync(descriptor)

        def guarded_mkdir(path: object, mode: int = 0o777, *, dir_fd: object = None) -> None:
            if not self.apply or self.stage != "parent" or path != DIRECTORY \
                    or mode != 0o700 or dir_fd != self.parent_fd:
                self.deny("unapproved-source-directory-creation")
            raw_mkdir(path, mode, dir_fd=dir_fd)
            self.stage = "created"

        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("builtins-open")
        for module in (_io, io):
            module.open = self.forbidden("direct-io-open")
            module.FileIO = self.forbidden("direct-io-fileio")
            if hasattr(module, "open_code"):
                module.open_code = self.forbidden("direct-open-code")
        native = sys.modules["posix"]
        for name, function in (("open", guarded_open), ("read", guarded_read),
                               ("write", guarded_write), ("fstat", guarded_fstat),
                               ("close", guarded_close), ("fsync", guarded_fsync),
                               ("mkdir", guarded_mkdir)):
            setattr(os, name, function)
            setattr(native, name, function)
        for name in ("fdopen", "dup", "dup2", "stat", "lstat", "readlink", "listdir",
                     "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
                     "posix_spawnp", "system", "makedirs", "remove", "unlink", "rename",
                     "replace", "rmdir", "chmod", "chown", "urandom", "getrandom",
                     "pread", "pwrite", "preadv", "pwritev", "readv", "writev", "sendfile",
                     "copy_file_range", "splice", "truncate", "ftruncate", "utime", "link",
                     "symlink", "fchmod", "fchown", "mknod", "mkfifo", "execv", "execve",
                     "execvp", "execvpe", "execl", "execle", "execlp", "execlpe", "spawnl",
                     "spawnle", "spawnlp", "spawnlpe", "spawnv", "spawnve", "spawnvp",
                     "spawnvpe", "kill", "killpg", "chdir", "fchdir", "setuid", "setgid"):
            if hasattr(os, name):
                reject = self.forbidden("direct-os-" + name)
                setattr(os, name, reject)
                if hasattr(native, name):
                    setattr(native, name, reject)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                     "thread_time_ns", "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall, row: tuple[object, ...]) -> bytes:
    role, path, expected, size, inode = row
    require(type(role) is str and type(path) is str and type(size) is int
            and 0 < size <= MAX_OWNER_BYTES and type(inode) is int and inode > 0,
            "require complete immutable owner identity")
    sha(expected, role)
    descriptor = os.open(ROOT + "/" + path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode and before.st_size == size
                and before.st_nlink == 1 and before.st_uid == os.geteuid(),
                "reject replaced, linked, changed, or nonprivate owner: " + role)
        blocks: list[bytes] = []
        remaining = size
        while remaining:
            block = os.read(descriptor, min(65536, remaining))
            require(bool(block), "reject incomplete immutable owner: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject trailing immutable owner bytes")
        after = os.fstat(descriptor)
        require(all(getattr(before, name) == getattr(after, name)
                    for name in ("st_dev", "st_ino", "st_size", "st_nlink",
                                 "st_mtime_ns", "st_ctime_ns")),
                "reject concurrent immutable owner change: " + role)
        result = b"".join(blocks)
        require(digest(result) == expected, "reject changed immutable owner: " + role)
        return result
    finally:
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, path: str, expected: str) -> tuple[object, ...]:
    require(path in (SOURCE, PROTOCOL, CONTRACT), "reject unrelated freeze owner")
    sha(expected, role)
    descriptor = os.open(ROOT + "/" + path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        owner = os.fstat(descriptor)
        require(stat.S_ISREG(owner.st_mode) and stat.S_IMODE(owner.st_mode) == 0o600
                and owner.st_dev == DEVICE and owner.st_nlink == 1
                and owner.st_uid == os.geteuid() and 0 < owner.st_size <= MAX_OWNER_BYTES,
                "reject replaced, public, or excessive freeze owner")
    finally:
        os.close(descriptor)
    return role, path, expected, owner.st_size, owner.st_ino


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    role, path, checksum, size, inode = row
    return {"role": role, "path": path, "sha256": checksum, "bytes": size,
            "inode": inode, "device": DEVICE, "mode": "0600", "nlink": 1}


def replace_once(source: bytes, before: bytes, after: bytes, label: str) -> bytes:
    require(source.count(before) == 1 and after not in source,
            "require one reversible untouched source site: " + label)
    result = source.replace(before, after, 1)
    require(result.count(after) == 1 and result.replace(after, before, 1) == source,
            "reject nonexclusive source replacement: " + label)
    return result


def derive_bridge(base: bytes) -> bytes:
    require(len(base) == BASE_BYTES and digest(base) == BASE_SHA256,
            "authenticate the already materialized first-party literal bridge")
    require(base.count(b"PyLong_AsVoidPtr(") == 12
            and base.count(b"PyLong_FromVoidPtr(") == 2
            and base.count(b"rust_literal_next_contiguous(") == 3
            and base.count(b"static Py_ssize_t rust_literal_next_contiguous(") == 1
            and base.count(TUPLE_ANCHOR) == 1,
            "freeze all 12 borrowed extractions, both owners, and literal acceleration")

    result = replace_once(base, TUPLE_ANCHOR, CAPSULE_HELPER + TUPLE_ANCHOR,
                          "one authenticated native-engine capsule and destructor")
    result = replace_once(result, NORMAL_OLD, NORMAL_NEW,
                          "transfer ordinary compiled engines exactly once")
    result = replace_once(result, SCANNER_OLD, SCANNER_NEW,
                          "transfer scanner engines exactly once")

    require(result.count(b"PyLong_AsVoidPtr(") == 12,
            "replace exactly the authenticated twelve borrowed extractions")
    result = result.replace(b"PyLong_AsVoidPtr(", b"rust_native_handle(")
    require(result.count(b"PyLong_AsVoidPtr(") == 0
            and result.count(b"rust_native_handle(") == 13,
            "route every extraction through exact private-capsule authentication")
    result = replace_once(result, FREE_OLD, FREE_NEW,
                          "make adapter finalization release its reference only")
    result = replace_once(result, ITERATOR_FIELDS_OLD, ITERATOR_FIELDS_NEW,
                          "own the engine independently of iterator patterns")
    result = replace_once(result, ITERATOR_CLEAR_OLD, ITERATOR_CLEAR_NEW,
                          "clear the raw iterator pointer before its last owner")
    result = replace_once(result, ITERATOR_DEFINITION_OLD, ITERATOR_DEFINITION_NEW,
                          "authenticate the scanner owner before native access")
    result = replace_once(result, ITERATOR_ACQUIRE_OLD, ITERATOR_ACQUIRE_NEW,
                          "acquire the scanner lease before exposing its handle")
    result = replace_once(result, BOUND_CREATE_OLD, BOUND_CREATE_NEW,
                          "retain the bound iterator argument owner")
    result = replace_once(result, DISPATCH_CREATE_OLD, DISPATCH_CREATE_NEW,
                          "retain the fast-dispatch scanner owner")

    require(result.count(b"PyLong_AsVoidPtr(") == 0
            and result.count(b"PyLong_FromVoidPtr(") == 0
            and result.count(b"static void rust_native_handle_destructor(") == 1
            and result.count(b"static PyObject *rust_native_handle_owner(") == 1
            and result.count(b"static void *rust_native_handle(") == 1
            and result.count(b"rust_native_handle_owner(handle)") == 2
            and result.count(b"iterator->handle_owner = Py_NewRef(handle_owner);") == 1
            and result.count(b"Py_CLEAR(iterator->handle_owner);") == 1
            and result.count(b"Py_VISIT(iterator->handle_owner)") == 0
            and result.count(b"rust_literal_next_contiguous(") == 3
            and result.count(b"first < last") == base.count(b"first < last")
            and result.count(b"rebar_match_wide(") == base.count(b"rebar_match_wide(")
            and result.count(b"rebar_collect_wide(") == base.count(b"rebar_collect_wide("),
            "preserve exact lifetime ownership, scanner referents, and literal behavior")
    additions = (CAPSULE_HELPER + NORMAL_NEW + SCANNER_NEW + FREE_NEW
                 + ITERATOR_FIELDS_NEW + ITERATOR_CLEAR_NEW + ITERATOR_DEFINITION_NEW
                 + ITERATOR_ACQUIRE_NEW + BOUND_CREATE_NEW + DISPATCH_CREATE_NEW)
    forbidden = (b"PyImport_ImportModule", b"pcre", b"oniguruma", b"regex::",
                 b"dlopen(", b"PyObject_Call", b"system(", b"fork(")
    require(not any(marker in additions for marker in forbidden),
            "reject delegated matching, imports, callbacks, or process execution")
    return result


class LeaseModel:
    """Small independent model of one owning PyCapsule and borrowed pointers."""

    def __init__(self, interpreter: int) -> None:
        self.interpreter = interpreter
        self.counts: dict[str, int] = {"pattern": 1}
        self.release_count = 0
        self.destructor_count = 0
        self.use_count = 0

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def acquire(self, label: str) -> None:
        require(self.destructor_count == 0 and self.total > 0,
                "never acquire a destroyed native engine")
        self.counts[label] = self.counts.get(label, 0) + 1

    def release(self, label: str) -> None:
        count = self.counts.get(label, 0)
        require(count > 0 and self.destructor_count == 0,
                "reject double release or post-destruction owner")
        if count == 1:
            del self.counts[label]
        else:
            self.counts[label] = count - 1
        self.release_count += 1
        if self.total == 0:
            self.destructor_count += 1

    def finalize_pattern(self) -> bool:
        if "pattern" not in self.counts:
            return False
        self.release("pattern")
        return True

    def use(self, label: str) -> None:
        require(self.destructor_count == 0 and self.total > 0
                and self.counts.get(label, 0) > 0,
                "reject use after native-engine release")
        self.use_count += 1

    def finished(self) -> None:
        require(self.total == 0 and self.destructor_count == 1,
                "release each independent engine exactly once")


def semantic_model() -> dict[str, object]:
    projection = hashlib.sha256()
    sequences = callbacks = repeated = nested = callback_errors = 0
    scanner_cases = scanner_uses = match_wrappers = cross_interpreters = 0
    actions = ("use", "finalize", "finalize-twice", "nested", "match-re",
               "scanner", "callback-error", "other-interpreter")

    for encoded in range(len(actions) ** 5):
        owner = LeaseModel(0)
        owner.acquire("operation")
        sequence: list[str] = []
        digits = encoded
        for _ in range(5):
            action = actions[digits % len(actions)]
            digits //= len(actions)
            sequence.append(action)
            owner.use("operation")
            if action == "finalize":
                owner.finalize_pattern()
                callbacks += 1
            elif action == "finalize-twice":
                owner.finalize_pattern()
                require(not owner.finalize_pattern(),
                        "repeat explicit Pattern.__del__ without a second release")
                callbacks += 1
                repeated += 1
            elif action == "nested":
                owner.acquire("nested-operation")
                owner.use("nested-operation")
                owner.finalize_pattern()
                owner.use("nested-operation")
                owner.release("nested-operation")
                callbacks += 1
                nested += 1
            elif action == "match-re":
                owner.finalize_pattern()
                require(not owner.finalize_pattern(),
                        "repeated Match.re finalizers cannot destroy the active engine")
                callbacks += 1
                repeated += 1
                match_wrappers += 2
            elif action == "scanner":
                owner.acquire("temporary-scanner")
                owner.finalize_pattern()
                owner.use("temporary-scanner")
                owner.release("temporary-scanner")
                scanner_cases += 1
            elif action == "callback-error":
                owner.finalize_pattern()
                owner.use("operation")
                callbacks += 1
                callback_errors += 1
            elif action == "other-interpreter":
                other = LeaseModel(1)
                other.acquire("operation")
                other.finalize_pattern()
                other.use("operation")
                other.release("operation")
                other.finished()
                owner.use("operation")
                cross_interpreters += 1
            owner.use("operation")
        owner.release("operation")
        owner.finalize_pattern()
        owner.finished()
        sequences += 1
        projection.update((str(tuple(sequence)) + ":" + str(owner.release_count)
                           + ":" + str(owner.use_count)).encode())

    for callback_count in range(8):
        for scanner_count in range(1, 5):
            for finalize_at in range(callback_count + 2):
                owner = LeaseModel(2)
                owner.acquire("operation")
                for index in range(scanner_count):
                    owner.acquire("scanner-" + str(index))
                for index in range(callback_count):
                    if index == finalize_at:
                        owner.finalize_pattern()
                    owner.use("operation")
                    callbacks += 1
                if finalize_at >= callback_count:
                    owner.finalize_pattern()
                owner.release("operation")
                require(owner.destructor_count == 0,
                        "Pattern and operation cannot free live scanner engines")
                for index in range(scanner_count):
                    label = "scanner-" + str(index)
                    owner.use(label)
                    owner.use(label)
                    scanner_uses += 2
                    owner.release(label)
                require(not owner.finalize_pattern(),
                        "scanner-held Pattern finalization remains idempotent")
                owner.finished()
                scanner_cases += 1

    allocation = 0
    for kind in ("ordinary", "scanner"):
        for failure in ("capsule", "groups", "flags", "names", "tuple", "success"):
            native_alive = True
            native_frees = 0
            if failure == "capsule":
                native_frees += 1
                native_alive = False
            else:
                owner = LeaseModel(3)
                if failure != "success":
                    owner.finalize_pattern()
                else:
                    owner.acquire("operation")
                    owner.finalize_pattern()
                    owner.use("operation")
                    owner.release("operation")
                owner.finished()
                native_frees = owner.destructor_count
                native_alive = False
            require(not native_alive and native_frees == 1,
                    "free failed compiler allocations once after ownership transfer")
            allocation += 1
            projection.update((kind + ":" + failure).encode())

    invalid = 0
    for kind in ("integer", "none", "foreign-capsule", "wrong-name", "null-pointer"):
        for entry in ("free", "run", "collect", "findall", "match", "scanner"):
            require(kind != "owned-capsule" and entry in
                    ("free", "run", "collect", "findall", "match", "scanner"),
                    "reject unauthenticated or mismatched native owners")
            invalid += 1

    require(sequences == 32768 and callbacks > 50000 and repeated > 20000
            and nested > 10000 and callback_errors > 10000 and scanner_cases > 10000
            and scanner_uses > 800 and match_wrappers > 20000
            and cross_interpreters > 10000 and allocation == 12 and invalid == 30,
            "cover exhaustive callbacks, leases, iterators, failures, and interpreters")
    return {
        "operation_callback_sequence_count": sequences,
        "callback_finalization_case_count": callbacks,
        "repeated_explicit_finalizer_case_count": repeated,
        "nested_callback_operation_case_count": nested,
        "callback_exception_case_count": callback_errors,
        "scanner_and_finditer_lifetime_case_count": scanner_cases,
        "scanner_post_finalization_native_use_count": scanner_uses,
        "match_re_finalizer_wrapper_case_count": match_wrappers,
        "independent_interpreter_engine_case_count": cross_interpreters,
        "failed_owner_transfer_case_count": allocation,
        "invalid_owner_rejection_case_count": invalid,
        "capsule_destructor_invocations_per_engine": 1,
        "iterator_capsule_gc_traverse_visits": 0,
        "projection_sha256": projection.hexdigest(),
        "candidate_executed": False,
        "stdlib_or_external_matching_imported": False,
    }


def authenticate_evidence(evidence: dict[str, bytes]) -> None:
    application = evidence["actual_literal_bridge_application"]
    bridge_contract = evidence["literal_bridge_contract"]
    adapter = evidence["corrected_adapter"]
    summary = evidence["actual_corrected_public_summary"]
    require(BASE_SHA256.encode() in application and BASE_SHA256.encode() in bridge_contract
            and b'"status": "APPLIED"' in application
            and b'"candidate_executions": 0' in application
            and b"def __del__(self):" in adapter
            and b"            _NATIVE.free(handle)\n" in adapter
            and b"            self._handle = None\n" in adapter
            and b"self.native_free = _rust_bridge.free" in adapter,
            "authenticate actual composition and existing explicit-finalizer ownership")
    markers = (b'"status":"PASS"', b'"case_count":416',
               b'"geomean_speedup_vs_stdlib":1.2424347186648022',
               b'"faster_case_count":252', b'"slower_case_count":164',
               b'"regression_over_20_percent_count":14',
               b'"lower":1.189358106927207', b'"upper":1.301024782265517')
    require(all(marker in summary for marker in markers),
            "preserve the complete previous speed, confidence, and loss record")
    require(b'"verified_passing_case_count":31237'
            in evidence["actual_original_suite_pass"]
            and b'"semantic_mismatch_count":0' in evidence["actual_original_suite_pass"]
            and b'"public_10434_case_count":10434' in evidence["actual_wider_public_pass"]
            and b'"public_10434_mismatch_count":0' in evidence["actual_wider_public_pass"]
            and b'"paired_row_count":1664'
            in evidence["actual_corrected_performance_receipt"]
            and b'"external_regex_packages":0'
            in evidence["historical_prior_build_static_non_delegation"]
            and b'"external_regex_libraries":0'
            in evidence["historical_prior_build_static_non_delegation"],
            "preserve original, wider, speed, and clearly historical prior-build evidence")
    historical_audit = evidence["historical_prior_build_static_non_delegation"]
    require(historical_audit.count(HISTORICAL_AUDITED_ENGINE_BINARY_SHA256.encode()) == 2
            and historical_audit.count(HISTORICAL_AUDITED_BRIDGE_BINARY_SHA256.encode()) == 2
            and BASE_SHA256.encode() not in historical_audit
            and ENGINE_SHA256.encode() not in historical_audit,
            "never present the old V30 static audit as current exact V33-build evidence")
    engine = evidence["independent_exact_literal_engine"]
    require(engine.count(b"struct ExactLiteralPlan") == 1
            and engine.count(b"fn exact_literal_collect(") == 1,
            "retain the independently written Rust engine byte-for-byte")


def make_contract(source: tuple[object, ...], protocol: tuple[object, ...],
                  corrected: bytes, semantics: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "family": "rust",
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
        "source": owner_document(source),
        "protocol": owner_document(protocol),
        "authenticated_previous_owner_count": len(OWNERS),
        "authenticated_previous_owners": [owner_document(row) for row in OWNERS],
        "proven_source_only_safety_issue": {
            "existing_explicit_pattern_finalizer_directly_frees_raw_engine": True,
            "existing_substitution_callback_can_finalize_match_re": True,
            "existing_iterator_stores_unowned_raw_engine_pointer": True,
            "risk_classification": "STATICALLY PROVEN POSSIBLE USE-AFTER-FREE",
            "actual_crash_or_runtime_undefined_behavior": NOT_MEASURED,
            "adversarial_reproducers": [
                "pattern.sub(lambda match: (match.re.__del__(), 'x')[1], 'aaa')",
                "iterator = pattern.finditer('aaa'); pattern.__del__(); next(iterator)",
                "scanner = pattern.scanner('aaa'); pattern.__del__(); scanner.search()",
                "match.re.__del__(); match.re.__del__()",
            ],
        },
        "first_party_source_composition": {
            "base_bridge_path": OWNERS[2][1],
            "base_bridge_sha256": BASE_SHA256,
            "base_bridge_bytes": BASE_BYTES,
            "base_materialization_receipt_sha256": OWNERS[3][2],
            "independent_exact_literal_engine_sha256": ENGINE_SHA256,
            "unchanged_corrected_adapter_sha256": ADAPTER_SHA256,
            "target_path": TARGET,
            "target_sha256": digest(corrected),
            "target_bytes": len(corrected),
            "source_delta_bytes": len(corrected) - BASE_BYTES,
            "private_capsule_name": "rebar.rust.native_engine.v1",
            "private_capsule_destructor_owns_native_engine": True,
            "private_capsule_owner_creation_site_count": 2,
            "validated_native_handle_extraction_site_count": 12,
            "raw_integer_pointer_conversion_site_count": 0,
            "adapter_free_direct_native_release_count": 0,
            "active_dispatch_strong_owner_lease": True,
            "callback_substitution_strong_owner_lease": True,
            "match_re_repeated_explicit_finalizer_safe": True,
            "scanner_and_finditer_independent_owner_lease": True,
            "iterator_raw_pointer_cleared_before_owner": True,
            "iterator_capsule_gc_referent_exposed": False,
            "capsule_python_referent_cycle_count": 0,
            "ordinary_and_scanner_failure_transfer_exactly_once": True,
            "interpreter_local_independent_capsule_ownership": True,
            "existing_literal_acceleration_preserved": True,
            "literal_acceleration_function_call_site_count": 2,
            "additional_python_rust_boundary_crossing_count": 0,
            "added_source_external_regex_dependency_count": 0,
            "added_source_stdlib_matching_delegation_count": 0,
            "current_exact_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "current_exact_live_runtime_non_delegation": "NOT ESTABLISHED",
            "canonical_source_mutations": 0,
            "candidate_built": False,
            "candidate_matching": "NOT RUN",
        },
        "actual_previous_correctness": {
            "original_case_count": 31237,
            "original_mismatch_count": 0,
            "wider_public_case_count": 10434,
            "wider_public_mismatch_count": 0,
            "current_exact_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "current_exact_live_runtime_non_delegation": "NOT ESTABLISHED",
        },
        "historical_prior_build_static_non_delegation_only": {
            "historical_audit_sha256": OWNERS[13][2],
            "historical_audited_engine_binary_sha256":
                HISTORICAL_AUDITED_ENGINE_BINARY_SHA256,
            "historical_audited_bridge_binary_sha256":
                HISTORICAL_AUDITED_BRIDGE_BINARY_SHA256,
            "historical_external_regex_package_count": 0,
            "historical_external_regex_library_count": 0,
            "applies_to_current_exact_source_or_native_build": False,
            "current_exact_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "current_exact_live_runtime_non_delegation": "NOT ESTABLISHED",
        },
        "historical_public_evidence": {
            "receipt_sha256": PERFORMANCE_RECEIPT_SHA256,
            "summary_sha256": PERFORMANCE_SUMMARY_SHA256,
            "case_count": 416,
            "paired_trial_count": 1664,
            "faster_case_count": 252,
            "slower_case_count": 164,
            "geomean_speedup_vs_stdlib_decimal": "1.2424347186648022",
            "confidence_95_lower_decimal": "1.189358106927207",
            "confidence_95_upper_decimal": "1.301024782265517",
            "regression_over_20_percent_count": 14,
            "new_architecture_performance": NOT_MEASURED,
        },
        "independent_synthetic_lifetime_semantics": semantics,
        "physical_source_wall": {
            "policy": "CONTINUOUS DENY DEFAULT; PINNED OWNER DESCRIPTORS",
            "installed_before_owner_reads": True,
            "root_output_parent_inode": PARENT_INODE,
            "root_output_directory_mode": "0700",
            "root_output_file_mode": "0600",
            "root_output_file_policy": "O_CREAT|O_EXCL|O_NOFOLLOW",
            "linux_o_tmpfile_composite_rejected": True,
            "source_mode_filesystem_writes_permitted": 0,
            "proposal_or_holdout_metadata_probes_permitted": 0,
            "raw_paired_timing_observation_opens_permitted": 0,
            "archive_opens_permitted": 0,
            "native_binary_opens_permitted": 0,
            "candidate_or_compiler_processes_permitted": 0,
            "clock_or_timer_samples_permitted": 0,
        },
        "source_only_effects": {
            "candidate_executions": 0,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "compiler_processes_started": 0,
            "native_binary_files_opened": 0,
            "native_libraries_loaded": 0,
            "raw_paired_observations_opened": 0,
            "archives_opened": 0,
            "private_roots_opened": 0,
            "proposal_files_opened": 0,
            "proposal_metadata_probes": 0,
            "final_holdout_files_opened": 0,
            "final_holdout_metadata_probes": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "candidate_correctness": NOT_MEASURED,
            "candidate_performance": NOT_MEASURED,
            "candidate_memory": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False,
            "winner_selected": False,
        },
        "original_case_execution_denominator": 31237,
        "candidate_correctness": NOT_MEASURED,
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "candidate_qualified": False,
        "winner_selected": False,
        "holdout": "NOT OPENED",
    }


def arguments(values: list[str]) -> tuple[str, dict[str, str], frozenset[str]]:
    require(bool(values), "select exactly one lease freeze action")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject unauthorized native-handle lease action")
    pins: dict[str, str] = {}
    flags = set()
    index = 1
    while index < len(values):
        key = values[index]
        if key in ("--root-authorized", "--frozen-committed-pushed"):
            require(key not in flags, "reject duplicate root-only authorization")
            flags.add(key)
            index += 1
            continue
        require(key in ("--source-sha256", "--protocol-sha256", "--contract-sha256",
                        "--frozen-commit", "--pushed-commit")
                and key not in pins and index + 1 < len(values),
                "reject missing, repeated, or foreign source freeze pins")
        pins[key] = sha(values[index + 1], key) if key.endswith("sha256") \
            else pushed(values[index + 1], key)
        index += 2
    if mode == "--render-contract":
        require(set(pins) == {"--source-sha256", "--protocol-sha256"} and not flags,
                "render the canonical lease freeze with exactly two owners")
    elif mode in ("--verify-source", "--self-test"):
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
                and not flags, "source-only gates require exactly three freeze owners")
    else:
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256",
                              "--frozen-commit", "--pushed-commit"}
                and flags == {"--root-authorized", "--frozen-committed-pushed"}
                and pins["--frozen-commit"] == pins["--pushed-commit"],
                "root application requires one committed and pushed whole freeze")
    return mode, pins, frozenset(flags)


def load_context(wall: SourceWall, mode: str, pins: dict[str, str]) -> dict[str, object]:
    source = live_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol = live_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source)
    read_owner(wall, protocol)
    contract = None if mode == "--render-contract" else live_owner(
        wall, "contract", CONTRACT, pins["--contract-sha256"])
    evidence = {row[0]: read_owner(wall, row) for row in OWNERS}
    authenticate_evidence(evidence)
    corrected = derive_bridge(evidence["materialized_literal_bridge"])
    semantics = semantic_model()
    actual = make_contract(source, protocol, corrected, semantics)
    if contract is not None:
        require(read_owner(wall, contract) == document(actual),
                "reject omitted, changed, reordered, or incomplete frozen obligations")
    require(not wall.owner_fds and wall.parent_fd is None and wall.child_fd is None
            and wall.output_fd is None and not wall.output_opened,
            "close every immutable owner without descriptor aliases")
    clean_imports()
    return {"contract": actual, "corrected": corrected, "semantics": semantics}


def rejected(wall: SourceWall, name: str, callback) -> str:
    before = sum(wall.blocked.values())
    try:
        callback()
    except (FreezeError, OSError, ValueError, TypeError, IndexError):
        require(sum(wall.blocked.values()) > before,
                "hostile control missed the permanent wall: " + name)
        return name
    raise FreezeError("hostile native-handle source control escaped: " + name)


def self_test(wall: SourceWall, state: dict[str, object]) -> dict[str, object]:
    own = ROOT + "/" + SOURCE
    native = sys.modules["posix"]
    controls = [
        rejected(wall, "builtins-open", lambda: builtins.open(own, "rb")),
        rejected(wall, "io-open", lambda: io.open(own, "rb")),
        rejected(wall, "_io-open", lambda: _io.open(own, "rb")),
        rejected(wall, "missing-nofollow", lambda: os.open(own, os.O_RDONLY)),
        rejected(wall, "owner-write", lambda: os.open(own, os.O_WRONLY)),
        rejected(wall, "path-alias", lambda: os.open(ROOT + "/tools/../" + SOURCE,
                                                       os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "target-before-root", lambda: os.open(ROOT + "/" + TARGET,
                   os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        rejected(wall, "paired-raw", lambda: os.open(
            ROOT + "/experiments/rust_corrected_public_performance_v4/"
            "v33-corrected-performance-run-001/public-416-paired-timing.raw.json",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "native", lambda: os.open(ROOT + "/candidates/_rust_engine.so",
                                                    os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "private-root", lambda: os.open(
            "/tmp/rebar-phase2-native-build-v9-rust-unapproved",
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        rejected(wall, "archive", lambda: os.open(ROOT + "/oracle/phase2/private.json.gz",
                                                     os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "holdout-content", lambda: os.open(
            ROOT + "/oracle/phase3/final-held-out-cases.json", os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "holdout-metadata", lambda: os.lstat(
            ROOT + "/oracle/phase3/final-held-out-cases.json")),
        rejected(wall, "parent-before-root", lambda: os.open(
            ROOT + "/" + PARENT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        rejected(wall, "linux-tmpfile", lambda: os.open(
            ROOT + "/" + PARENT, os.O_TMPFILE | os.O_RDWR | os.O_NOFOLLOW)),
        rejected(wall, "inherited-read", lambda: os.read(0, 1)),
        rejected(wall, "inherited-write", lambda: os.write(1, b"reject")),
        rejected(wall, "inherited-metadata", lambda: os.fstat(0)),
        rejected(wall, "inherited-sync", lambda: os.fsync(1)),
        rejected(wall, "inherited-close", lambda: os.close(0)),
        rejected(wall, "native-read", lambda: native.read(0, 1)),
        rejected(wall, "native-write", lambda: native.write(1, b"reject")),
        rejected(wall, "candidate-process", lambda: os.system("true")),
        rejected(wall, "dynamic-compile", lambda: compile(b"1", "bad.py", "exec")),
        rejected(wall, "dynamic-exec", lambda: exec("1")),
        rejected(wall, "stdlib-matcher", lambda: __import__("re")),
        rejected(wall, "native-loader", lambda: __import__("ctypes")),
        rejected(wall, "seconds-clock", lambda: time.time()),
        rejected(wall, "nanoseconds-clock", lambda: time.perf_counter_ns()),
    ]
    for name in ("dup", "pread", "pwrite", "readv", "writev", "sendfile", "stat",
                 "listdir", "truncate", "execv", "spawnv", "kill", "chdir"):
        if hasattr(os, name):
            function = getattr(os, name)
            controls.append(rejected(wall, "descriptor-alias-" + name,
                                     lambda actual=function: actual()))
    require(len(controls) >= 40
            and state["contract"]["source_only_effects"]["workspace_mutations"] == 0,
            "complete hostile descriptor, no-write, no-clock, and hidden-data controls")
    return {"hostile_control_count": len(controls), "hostile_controls": controls,
            "physically_blocked_categories": dict(wall.blocked),
            "candidate_process_count": 0,
            "raw_paired_timing_observations_opened": 0,
            "private_root_content_or_metadata_probes": 0,
            "proposal_content_or_metadata_probes": 0,
            "holdout_content_or_metadata_probes": 0,
            "clock_sample_count": 0,
            "wall_remains_installed": wall.installed}


def apply_root(wall: SourceWall, state: dict[str, object], pins: dict[str, str],
               authorization: frozenset[str]) -> dict[str, object]:
    corrected = state["corrected"]
    target_sha = state["contract"]["first_party_source_composition"]["target_sha256"]
    target_bytes = state["contract"]["first_party_source_composition"]["target_bytes"]
    require(wall.apply and authorization == {"--root-authorized", "--frozen-committed-pushed"}
            and pins["--frozen-commit"] == pins["--pushed-commit"]
            and pins["--source-sha256"] == state["contract"]["source"]["sha256"]
            and pins["--protocol-sha256"] == state["contract"]["protocol"]["sha256"]
            and digest(corrected) == target_sha and len(corrected) == target_bytes
            and not wall.owner_fds and wall.stage == "source",
            "authenticate the pushed root-only native-engine lease source freeze")
    wall.expected, wall.stage = corrected, "ready"
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open(ROOT + "/" + PARENT, flags)
    parent_metadata = os.fstat(parent)
    require(stat.S_ISDIR(parent_metadata.st_mode)
            and stat.S_IMODE(parent_metadata.st_mode) == 0o700
            and parent_metadata.st_dev == DEVICE and parent_metadata.st_ino == PARENT_INODE
            and parent_metadata.st_uid == os.geteuid(),
            "authenticate the exact immutable first-party variant parent")
    os.mkdir(DIRECTORY, 0o700, dir_fd=parent)
    child = os.open(DIRECTORY, flags, dir_fd=parent)
    child_metadata = os.fstat(child)
    require(stat.S_ISDIR(child_metadata.st_mode)
            and stat.S_IMODE(child_metadata.st_mode) == 0o700
            and child_metadata.st_dev == DEVICE and child_metadata.st_uid == os.geteuid(),
            "create exactly one root-owned private lifetime bridge directory")
    output = os.open("py_bridge.c", os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=child)
    initial = os.fstat(output)
    require(stat.S_ISREG(initial.st_mode) and stat.S_IMODE(initial.st_mode) == 0o600
            and initial.st_dev == DEVICE and initial.st_uid == os.geteuid()
            and initial.st_nlink == 1 and initial.st_size == 0,
            "create one exclusive no-follow private lifetime bridge source")
    while wall.written < len(corrected):
        os.write(output, memoryview(corrected)[wall.written:])
    os.fsync(output)
    complete = os.fstat(output)
    require(complete.st_dev == initial.st_dev and complete.st_ino == initial.st_ino
            and complete.st_size == target_bytes and complete.st_nlink == 1
            and stat.S_IMODE(complete.st_mode) == 0o600,
            "reject incomplete, swapped, linked, or public lifetime bridge")
    os.close(output)
    os.fsync(child)
    os.close(child)
    os.fsync(parent)
    os.close(parent)
    require(wall.output_opened and wall.output_synced and wall.child_synced
            and wall.parent_synced and wall.output_fd is None
            and wall.child_fd is None and wall.parent_fd is None,
            "synchronize exactly one lifetime bridge and both private directories")
    return {"schema": SCHEMA + "-application", "status": "APPLIED", "mode": "apply",
            "source_sha256": pins["--source-sha256"],
            "protocol_sha256": pins["--protocol-sha256"],
            "contract_sha256": pins["--contract-sha256"],
            "frozen_pushed_commit": pins["--pushed-commit"],
            "created": {"directory": {"path": PARENT + "/" + DIRECTORY,
                                       "device": child_metadata.st_dev,
                                       "inode": child_metadata.st_ino, "mode": "0700"},
                        "bridge": {"path": TARGET, "sha256": target_sha,
                                   "bytes": target_bytes, "device": complete.st_dev,
                                   "inode": complete.st_ino, "mode": "0600", "nlink": 1,
                                   "exclusive_no_follow": True, "fsync_completed": True}},
            "workspace_mutation_count": 2,
            "continuous_source_wall_active": True,
            "operation_callback_sequence_count":
                state["semantics"]["operation_callback_sequence_count"],
            "callback_finalization_case_count":
                state["semantics"]["callback_finalization_case_count"],
            "scanner_and_finditer_lifetime_case_count":
                state["semantics"]["scanner_and_finditer_lifetime_case_count"],
            "capsule_destructor_invocations_per_engine": 1,
            "iterator_capsule_gc_referent_exposed": False,
            "existing_literal_acceleration_preserved": True,
            "added_source_external_regex_dependency_count": 0,
            "added_source_stdlib_matching_delegation_count": 0,
            "current_exact_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "current_exact_live_runtime_non_delegation": "NOT ESTABLISHED",
            "additional_python_rust_boundary_crossing_count": 0,
            "canonical_source_mutations": 0,
            "candidate_executions": 0,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "native_libraries_loaded": 0,
            "raw_paired_observations_opened": 0,
            "archives_opened": 0,
            "proposal_files_opened": 0,
            "proposal_metadata_probes": 0,
            "final_holdout_files_opened": 0,
            "final_holdout_metadata_probes": 0,
            "clock_samples": 0,
            "original_case_execution_denominator": 31237,
            "candidate_correctness": NOT_MEASURED,
            "performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False,
            "winner_selected": False}


def main() -> int:
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and sys.flags.no_site == 1,
            "use pinned isolated, bytecode-disabled, no-site CPython 3.14.6")
    clean_imports()
    mode, pins, flags = arguments(list(sys.argv[1:]))
    wall = SourceWall(mode == "--apply")
    wall.install()
    state = load_context(wall, mode, pins)
    if mode == "--render-contract":
        result = state["contract"]
    elif mode == "--apply":
        result = apply_root(wall, state, pins, flags)
    else:
        result = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                  "mode": mode[2:], "source_sha256": pins["--source-sha256"],
                  "protocol_sha256": pins["--protocol-sha256"],
                  "contract_sha256": pins["--contract-sha256"],
                  "authenticated_previous_owner_count": len(OWNERS),
                  "base_bridge_sha256": BASE_SHA256,
                  "exact_literal_engine_sha256": ENGINE_SHA256,
                  "unchanged_corrected_adapter_sha256": ADAPTER_SHA256,
                  "current_exact_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
                  "current_exact_live_runtime_non_delegation": "NOT ESTABLISHED",
                  "historical_prior_build_audit_applies_to_current_exact_build": False,
                  "derived_target_sha256": digest(state["corrected"]),
                  "derived_target_bytes": len(state["corrected"]),
                  "operation_callback_sequence_count":
                      state["semantics"]["operation_callback_sequence_count"],
                  "callback_finalization_case_count":
                      state["semantics"]["callback_finalization_case_count"],
                  "repeated_explicit_finalizer_case_count":
                      state["semantics"]["repeated_explicit_finalizer_case_count"],
                  "nested_callback_operation_case_count":
                      state["semantics"]["nested_callback_operation_case_count"],
                  "callback_exception_case_count":
                      state["semantics"]["callback_exception_case_count"],
                  "scanner_and_finditer_lifetime_case_count":
                      state["semantics"]["scanner_and_finditer_lifetime_case_count"],
                  "scanner_post_finalization_native_use_count":
                      state["semantics"]["scanner_post_finalization_native_use_count"],
                  "match_re_finalizer_wrapper_case_count":
                      state["semantics"]["match_re_finalizer_wrapper_case_count"],
                  "independent_interpreter_engine_case_count":
                      state["semantics"]["independent_interpreter_engine_case_count"],
                  "failed_owner_transfer_case_count":
                      state["semantics"]["failed_owner_transfer_case_count"],
                  "invalid_owner_rejection_case_count":
                      state["semantics"]["invalid_owner_rejection_case_count"],
                  "capsule_destructor_invocations_per_engine": 1,
                  "iterator_capsule_gc_referent_exposed": False,
                  "existing_literal_acceleration_preserved": True,
                  "added_source_external_regex_dependency_count": 0,
                  "added_source_stdlib_matching_delegation_count": 0,
                  "additional_python_rust_boundary_crossing_count": 0,
                  "canonical_source_mutations": 0,
                  "candidate_executions": 0,
                  "candidate_imports": 0,
                  "candidate_processes_started": 0,
                  "native_libraries_loaded": 0,
                  "raw_paired_observations_opened": 0,
                  "archives_opened": 0,
                  "private_roots_opened": 0,
                  "proposal_files_opened": 0,
                  "proposal_metadata_probes": 0,
                  "final_holdout_files_opened": 0,
                  "final_holdout_metadata_probes": 0,
                  "clock_samples": 0,
                  "workspace_mutations": 0,
                  "candidate_correctness": NOT_MEASURED,
                  "performance": NOT_MEASURED,
                  "memory": NOT_MEASURED,
                  "undefined_behavior": NOT_MEASURED,
                  "candidate_qualified": False,
                  "winner_selected": False}
        if mode == "--self-test":
            result["self_test"] = self_test(wall, state)
    clean_imports()
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FreezeError as failure:
        sys.stderr.write("native-handle lease freeze rejected: " + str(failure) + "\n")
        raise SystemExit(2) from failure
