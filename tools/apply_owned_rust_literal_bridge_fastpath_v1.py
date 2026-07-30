#!/usr/bin/env python3
"""Freeze one independently implemented, bounded Rust-family C bridge shortcut."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("literal bridge source freeze cannot load matching engines")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_literal_bridge_fastpath_v1.py"
PROTOCOL = "oracle/phase2/RUST-LITERAL-BRIDGE-FASTPATH-V1.md"
CONTRACT = "oracle/phase2/rust-literal-bridge-fastpath-v1.json"
PARENT = "candidates/rust/variants"
DIRECTORY = "literal_bridge_fastpath_v1"
TARGET = PARENT + "/" + DIRECTORY + "/py_bridge.c"
SCHEMA = "rebar-owned-rust-literal-bridge-fastpath-v1-source-freeze"
DEVICE = 2064
PARENT_INODE = 524946
MAX_OWNER_BYTES = 1_048_576
NOT_MEASURED = "NOT MEASURED"
BASE_SHA256 = "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e"
BASE_BYTES = 178472
ENGINE_SHA256 = "7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136"
PERFORMANCE_RECEIPT_SHA256 = "db9288ea7c0a00e0c702acb7520e74482f8fb3c90cccee8f6e247f592811f2b3"
PERFORMANCE_SUMMARY_SHA256 = "7366a81a3fa1352cb6e8a165d5c45871f0081bda7e5c392e07d7bbf3f3a4cfef"

TARGETED_CASES = (
    "rust-public-profile.v1.0001", "rust-public-profile.v1.0010",
    "rust-public-profile.v1.0023", "rust-public-profile.v1.0024",
    "rust-public-profile.v1.0209", "rust-public-profile.v1.0212",
    "rust-public-profile.v1.0218", "rust-public-profile.v1.0221",
    "rust-public-profile.v1.0231", "rust-public-profile.v1.0232",
)
PRESERVED_OTHER_CASES = (
    "rust-public-profile.v1.0110", "rust-public-profile.v1.0119",
    "rust-public-profile.v1.0156", "rust-public-profile.v1.0342",
)

OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_ledger", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("complete_bridge", "candidates/rust/variants/complete_scanner_bridge_v1/py_bridge.c",
     BASE_SHA256, BASE_BYTES, 525163),
    ("exact_literal_engine", "candidates/rust/variants/exact_literal_fastpath_v1/lib.rs",
     ENGINE_SHA256, 194276, 525959),
    ("exact_literal_source", "tools/apply_owned_rust_exact_literal_fastpath_v1.py",
     "11f448875e70f5413731061b8b439c5caae9b5e212378febabbeb71fc7ea59e9", 59925, 430542),
    ("exact_literal_protocol", "oracle/phase2/RUST-EXACT-LITERAL-FASTPATH-V1.md",
     "14b30b449c47c6b5935da16cf5723f2e6a505be294e4497d2c24bf10edc4ce57", 5289, 525191),
    ("exact_literal_contract", "oracle/phase2/rust-exact-literal-fastpath-v1.json",
     "c0a76fb83774bd875759d24a31d255693c01ac12922029aefa8258ab8da86ac8", 7239, 525276),
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
    ("actual_static_non_delegation",
     "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json",
     "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203", 16427, 525089),
)

HELPER_ANCHOR = b"static PyObject *rust_pattern_direct(PyObject *pattern, void *handle,"
HELPER_SOURCE = b"""/* First-party bounded literal search: an exact necessary byte, never regex. */
static Py_ssize_t rust_literal_next_contiguous(
    const uint8_t *haystack,
    size_t length,
    const uint8_t *needle,
    size_t width,
    size_t from,
    size_t end
) {
    if (end > length) end = length;
    if (width == 0 || from > end || width > end - from) return -1;

    size_t offset = width - 1;
    if (width > 1 && end - from >= 128) {
        size_t sample = end - from < 64 ? end - from : 64;
        size_t first = 0;
        size_t last = 0;
        for (size_t index = 0; index < sample; index++) {
            uint8_t value = haystack[from + index];
            first += value == needle[0];
            last += value == needle[width - 1];
        }
        if (first < last) offset = 0;
    }

    size_t cursor = from + offset;
    size_t stop = end - width + offset + 1;
    while (cursor < stop) {
        const uint8_t *hit = memchr(
            haystack + cursor, needle[offset], stop - cursor
        );
        if (hit == NULL) return -1;
        size_t position = (size_t)(hit - haystack);
        size_t begin = position - offset;
        if (memcmp(haystack + begin, needle, width) == 0) {
            return (Py_ssize_t)begin;
        }
        cursor = position + 1;
    }
    return -1;
}

"""

SEARCH_OLD = b"""                if (subject.text) {
                    at = PyUnicode_Find(value, literal, (Py_ssize_t)start, (Py_ssize_t)end, 1);
                    if (at == -2) found = -1;
                } else {
                    const uint8_t *needle = (const uint8_t *)PyBytes_AS_STRING(literal);
                    const uint8_t *hit = memmem(subject.data + start, end - start, needle, (size_t)width);
                    if (hit != NULL) at = (Py_ssize_t)(hit - subject.data);
                }
"""

SEARCH_NEW = b"""                if (
                    width >= 2
                    && (!subject.text || (
                        subject.kind == PyUnicode_1BYTE_KIND
                        && PyUnicode_KIND(literal) == PyUnicode_1BYTE_KIND
                    ))
                ) {
                    const uint8_t *needle = subject.text
                        ? (const uint8_t *)PyUnicode_1BYTE_DATA(literal)
                        : (const uint8_t *)PyBytes_AS_STRING(literal);
                    at = rust_literal_next_contiguous(
                        subject.data, subject.length, needle,
                        (size_t)width, start, end
                    );
                } else if (subject.text) {
                    at = PyUnicode_Find(value, literal, (Py_ssize_t)start, (Py_ssize_t)end, 1);
                    if (at == -2) found = -1;
                } else {
                    const uint8_t *needle = (const uint8_t *)PyBytes_AS_STRING(literal);
                    const uint8_t *hit = memmem(subject.data + start, end - start, needle, (size_t)width);
                    if (hit != NULL) at = (Py_ssize_t)(hit - subject.data);
                }
"""

FINDALL_NEEDLE_OLD = b"""    const uint8_t *needle = subject.text
        ? NULL
        : (const uint8_t *)PyBytes_AS_STRING(literal);
"""

FINDALL_NEEDLE_NEW = b"""    const uint8_t *needle = subject.text
        ? (
            width >= 2
            && subject.kind == PyUnicode_1BYTE_KIND
            && PyUnicode_KIND(literal) == PyUnicode_1BYTE_KIND
                ? (const uint8_t *)PyUnicode_1BYTE_DATA(literal)
                : NULL
        )
        : (const uint8_t *)PyBytes_AS_STRING(literal);
"""

FINDALL_SEARCH_OLD = b"""        if (subject.text) {
            Py_ssize_t hit = width == 1
                ? PyUnicode_FindChar(value, character, (Py_ssize_t)cursor, (Py_ssize_t)end, 1)
                : PyUnicode_Find(value, literal, (Py_ssize_t)cursor, (Py_ssize_t)end, 1);
            if (hit < 0) {
                if (PyErr_Occurred()) {
                    Py_DECREF(result);
                    rust_subject_release(&subject);
                    return NULL;
                }
                break;
            }
            begin = (size_t)hit;
        } else {
            const uint8_t *hit = memmem(
                subject.data + cursor, end - cursor, needle, width
            );
            if (hit == NULL) break;
            begin = (size_t)(hit - subject.data);
        }
"""

FINDALL_SEARCH_NEW = b"""        if (width >= 2 && needle != NULL) {
            Py_ssize_t hit = rust_literal_next_contiguous(
                subject.data, subject.length, needle, width, cursor, end
            );
            if (hit < 0) break;
            begin = (size_t)hit;
        } else if (subject.text) {
            Py_ssize_t hit = width == 1
                ? PyUnicode_FindChar(value, character, (Py_ssize_t)cursor, (Py_ssize_t)end, 1)
                : PyUnicode_Find(value, literal, (Py_ssize_t)cursor, (Py_ssize_t)end, 1);
            if (hit < 0) {
                if (PyErr_Occurred()) {
                    Py_DECREF(result);
                    rust_subject_release(&subject);
                    return NULL;
                }
                break;
            }
            begin = (size_t)hit;
        } else {
            const uint8_t *hit = memmem(
                subject.data + cursor, end - cursor, needle, width
            );
            if (hit == NULL) break;
            begin = (size_t)(hit - subject.data);
        }
"""


class FreezeError(Exception):
    """Reject unsafe effects, incomplete evidence, or changed semantics."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash genuine complete immutable source")
    return hashlib.sha256(value).hexdigest()


def sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require one complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def pushed(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(char in "0123456789abcdef" for char in value),
            "require one complete pushed commit: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "subprocess", "socket", "threading", "multiprocessing",
                 "random", "json", "candidates", "rebar", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject regex engines, packages, candidates, processes, and dynamic loaders")


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
        require(all(type(key) is str for key in value), "require immutable text keys")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject noncanonical floating or unknown evidence")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class SourceWall:
    """Permanently permit only authenticated owners and one root-only output."""

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
        raise FreezeError("literal bridge source wall rejected " + category)

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
                self.deny("unowned-raw-native-private-proposal-hidden-or-write-open")
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
            self.deny("candidate-native-process-clock-final-or-dynamic-code")

    def forbidden(self, category: str):
        def reject(*_args: object, **_keywords: object) -> object:
            self.deny(category)
        return reject

    def install(self) -> None:
        require(not self.installed, "install one permanent deny-default source wall")
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
                require(self.written == len(self.expected), "sync complete source bytes only")
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
                "reject replaced, linked, modified, or nonprivate owner: " + role)
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
                "reject concurrent immutable owner mutation: " + role)
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
            "require one reversible unmodified source site: " + label)
    result = source.replace(before, after, 1)
    require(result.count(after) == 1 and result.replace(after, before, 1) == source,
            "reject nonexclusive source replacement: " + label)
    return result


def derive_bridge(base: bytes) -> bytes:
    require(len(base) == BASE_BYTES and digest(base) == BASE_SHA256,
            "authenticate the exact fully corrected first-party C bridge")
    require(base.count(HELPER_ANCHOR) == 1 and base.count(SEARCH_OLD) == 1
            and base.count(FINDALL_NEEDLE_OLD) == 1 and base.count(FINDALL_SEARCH_OLD) == 1,
            "locate exactly four unchanged first-party bridge sites")
    result = replace_once(base, HELPER_ANCHOR, HELPER_SOURCE + HELPER_ANCHOR,
                          "independent bounded literal byte finder")
    result = replace_once(result, SEARCH_OLD, SEARCH_NEW,
                          "bounded plain literal search dispatch")
    result = replace_once(result, FINDALL_NEEDLE_OLD, FINDALL_NEEDLE_NEW,
                          "compact Unicode literal byte access")
    result = replace_once(result, FINDALL_SEARCH_OLD, FINDALL_SEARCH_NEW,
                          "nonoverlapping literal collection dispatch")
    require(result.count(b"static Py_ssize_t rust_literal_next_contiguous(") == 1
            and result.count(b"rust_literal_next_contiguous(") == 3
            and result.count(b"subject.kind == PyUnicode_1BYTE_KIND") >= 2
            and result.count(b"width >= 2") >= 3
            and result.count(b"first < last") == 1,
            "preserve one exact adaptive finder and both bounded public entry points")
    additions = HELPER_SOURCE + SEARCH_NEW + FINDALL_NEEDLE_NEW + FINDALL_SEARCH_NEW
    forbidden = (b"PyImport_ImportModule", b"_sre", b"pcre", b"oniguruma",
                 b"regex::", b"dlopen(", b"PyObject_Call", b"system(", b"fork(")
    require(not any(marker in additions for marker in forbidden),
            "reject external matching, Python matching, callbacks, or process delegation")
    require(result.count(b"rebar_match_wide(") == base.count(b"rebar_match_wide(")
            and result.count(b"rebar_collect_wide(") == base.count(b"rebar_collect_wide("),
            "reject additional cross-boundary matching or collection calls")
    return result


def words(alphabet: tuple[int, ...], maximum: int):
    current = [()]
    yield ()
    for _length in range(maximum):
        current = [prefix + (value,) for prefix in current for value in alphabet]
        yield from current


def reference_next(needle: tuple[int, ...], subject: tuple[int, ...],
                   start: int, end: int) -> int | None:
    end = min(end, len(subject))
    if not needle or start > end or len(needle) > end - start:
        return None
    for cursor in range(start, end - len(needle) + 1):
        if subject[cursor:cursor + len(needle)] == needle:
            return cursor
    return None


def adaptive_next(needle: tuple[int, ...], subject: tuple[int, ...],
                  start: int, end: int) -> tuple[int | None, int]:
    end = min(end, len(subject))
    if not needle or start > end or len(needle) > end - start:
        return None, -1
    offset = len(needle) - 1
    if len(needle) > 1 and end - start >= 128:
        sample = min(end - start, 64)
        first = sum(value == needle[0] for value in subject[start:start + sample])
        last = sum(value == needle[-1] for value in subject[start:start + sample])
        if first < last:
            offset = 0
    cursor = start + offset
    stop = end - len(needle) + offset + 1
    while cursor < stop:
        while cursor < stop and subject[cursor] != needle[offset]:
            cursor += 1
        if cursor == stop:
            return None, offset
        begin = cursor - offset
        if subject[begin:begin + len(needle)] == needle:
            return begin, offset
        cursor += 1
    return None, offset


def model_match(needle: tuple[int, ...], subject: tuple[int, ...],
                start: int, end: int, mode: int, optimized: bool):
    end = min(end, len(subject))
    if not needle or start > end or len(needle) > end - start:
        return None
    if mode == 0:
        found = adaptive_next(needle, subject, start, end)[0] if optimized \
            else reference_next(needle, subject, start, end)
        return None if found is None else (found, found + len(needle))
    if mode == 2 and end - start != len(needle):
        return None
    return (start, start + len(needle)) \
        if subject[start:start + len(needle)] == needle else None


def model_collect(needle: tuple[int, ...], subject: tuple[int, ...],
                  start: int, end: int, capacity: int, optimized: bool):
    answer = []
    cursor = start
    while len(answer) < capacity:
        found = adaptive_next(needle, subject, cursor, end)[0] if optimized \
            else reference_next(needle, subject, cursor, end)
        if found is None:
            break
        finish = found + len(needle)
        answer.append((found, finish))
        cursor = finish
    return tuple(answer)


def eligible(width: int, subject_kind: int, pattern_kind: int,
             flags: int, groups: int, text: bool) -> bool:
    return (width >= 2 and groups == 0 and flags & (2 | 64) == 0
            and (not text or subject_kind == 1 and pattern_kind == 1))


def semantic_model() -> dict[str, object]:
    alphabet = (0, 65, 255)
    subjects = tuple(words(alphabet, 4))
    needles = tuple(word for word in words(alphabet, 4) if len(word) >= 2)
    matching = collection = high = windows = successes = 0
    projection = hashlib.sha256()
    for subject in subjects:
        bounds = sorted({0, 1, max(len(subject) - 1, 0), len(subject), len(subject) + 1})
        for needle in needles:
            for start in bounds:
                for end in bounds:
                    windows += 1
                    for mode in (0, 1, 2):
                        expected = model_match(needle, subject, start, end, mode, False)
                        actual = model_match(needle, subject, start, end, mode, True)
                        require(actual == expected,
                                "adaptive literal search changed bounded leftmost matching")
                        matching += 1
                        successes += int(actual is not None)
                        high += int(255 in needle or 255 in subject)
                        projection.update((str(subject) + str(needle) + str(start)
                                           + str(end) + str(mode) + str(actual)).encode())
                    for capacity in (0, 1, 2, 5):
                        expected = model_collect(needle, subject, start, end, capacity, False)
                        actual = model_collect(needle, subject, start, end, capacity, True)
                        require(actual == expected,
                                "adaptive literal collection changed nonoverlapping order")
                        collection += 1

    adaptive_first = adaptive_last = 0
    long_subjects = (
        (65,) * 130,
        (65,) * 129 + (66,),
        (66,) * 129 + (65,),
        (255, 0) * 68,
        (0, 255) * 67,
        (65,) * 64 + (66,) + (65,) * 69,
    )
    long_needles = ((65, 66), (66, 65), (65, 65, 66),
                    (66, 65, 65), (255, 0), (0, 255))
    long_cases = 0
    for subject in long_subjects:
        for needle in long_needles:
            for start, end in ((0, len(subject)), (1, len(subject)),
                               (2, len(subject) - 1), (64, len(subject))):
                actual, offset = adaptive_next(needle, subject, start, end)
                require(actual == reference_next(needle, subject, start, end),
                        "adaptive first/last anchor changed a long bounded result")
                adaptive_first += int(offset == 0)
                adaptive_last += int(offset == len(needle) - 1)
                long_cases += 1

    rejection = 0
    for width in (0, 1, 2, 3):
        for subject_kind in (1, 2, 4):
            for pattern_kind in (1, 2, 4):
                for flags in (0, 2, 4, 32, 64, 256):
                    for groups in (0, 1, 40):
                        for text in (False, True):
                            actual = eligible(width, subject_kind, pattern_kind,
                                              flags, groups, text)
                            expected = (width >= 2 and groups == 0
                                        and flags & (2 | 64) == 0
                                        and (not text or subject_kind == pattern_kind == 1))
                            require(actual == expected,
                                    "reject captures, case flags, width, or wide Unicode")
                            rejection += 1

    require(matching > 900000 and collection > 1200000
            and high > 800000 and successes > 0
            and adaptive_first > 0 and adaptive_last > 0 and rejection > 1000,
            "complete exhaustive high-byte, windows, modes, collection, and anchor proofs")
    return {"bounded_matching_case_count": matching,
            "bounded_collection_case_count": collection,
            "bounded_window_count": windows,
            "successful_matching_case_count": successes,
            "high_byte_matching_case_count": high,
            "long_adaptive_anchor_case_count": long_cases,
            "adaptive_first_anchor_case_count": adaptive_first,
            "adaptive_last_anchor_case_count": adaptive_last,
            "selection_rejection_case_count": rejection,
            "subject_family_count": len(subjects),
            "literal_family_count": len(needles),
            "projection_sha256": projection.hexdigest(),
            "candidate_executed": False,
            "stdlib_or_external_matching_imported": False}


def authenticate_evidence(evidence: dict[str, bytes]) -> None:
    summary = evidence["actual_corrected_public_summary"]
    markers = (
        b'"status":"PASS"', b'"case_count":416',
        b'"geomean_speedup_vs_stdlib":1.2424347186648022',
        b'"faster_case_count":252', b'"slower_case_count":164',
        b'"regression_over_20_percent_count":14',
        b'"lower":1.189358106927207', b'"upper":1.301024782265517',
    )
    require(all(marker in summary for marker in markers),
            "preserve every actual corrected 416-case speed and confidence result")
    opener = b'"all_regressions_over_20_percent":['
    closer = b'],"bottom_20_slower_cases":'
    require(summary.count(opener) == 1, "preserve one complete regression list")
    section = summary.split(opener, 1)[1].split(closer, 1)[0]
    require(section.count(b'"case":"') == 14,
            "preserve all 14 substantial public regressions")
    for case in TARGETED_CASES + PRESERVED_OTHER_CASES:
        require(section.count(('"case":"' + case + '"').encode()) == 1,
                "preserve the exact substantial regression: " + case)
    require(section.count(b'"cohort":"mandatory_literal_dense_same_first_byte"') == 10,
            "preserve the exact ten literal bridge regressions")

    original = evidence["actual_original_suite_pass"]
    public = evidence["actual_wider_public_pass"]
    receipt = evidence["actual_corrected_performance_receipt"]
    audit = evidence["actual_static_non_delegation"]
    require(b'"verified_passing_case_count":31237' in original
            and b'"semantic_mismatch_count":0' in original
            and b'"actual_candidate_workers":13' in original
            and b'"public_10434_case_count":10434' in public
            and b'"public_10434_mismatch_count":0' in public
            and b'"public_10434_case_count":10434' in receipt
            and b'"exact_v33_original_31237_case_count":31237' in receipt
            and b'"paired_row_count":1664' in receipt
            and b'"external_regex_packages":0' in audit
            and b'"external_regex_libraries":0' in audit,
            "authenticate the identical complete original, wider, static, and public records")
    engine = evidence["exact_literal_engine"]
    require(engine.count(b"struct ExactLiteralPlan") == 1
            and engine.count(b"search::next_singleton(values, needle[final_offset]") == 1
            and engine.count(b"fn exact_literal_collect(") == 1,
            "preserve the independently written exact literal Rust engine")
    exact_contract = evidence["exact_literal_contract"]
    require(ENGINE_SHA256.encode() in exact_contract
            and b'"external_regex_dependency_count":0' in exact_contract,
            "preserve previously frozen independently implemented Rust source")


def make_contract(source: tuple[object, ...], protocol: tuple[object, ...],
                  corrected: bytes, semantics: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA, "version": 1, "family": "rust", "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
        "source": owner_document(source), "protocol": owner_document(protocol),
        "authenticated_previous_owner_count": len(OWNERS),
        "authenticated_previous_owners": [owner_document(row) for row in OWNERS],
        "first_party_source_composition": {
            "base_bridge_path": OWNERS[2][1], "base_bridge_sha256": BASE_SHA256,
            "base_bridge_bytes": BASE_BYTES,
            "independent_exact_literal_engine_sha256": ENGINE_SHA256,
            "target_path": TARGET, "target_sha256": digest(corrected),
            "target_bytes": len(corrected), "source_delta_bytes": len(corrected) - BASE_BYTES,
            "exact_plain_literal_only": True, "minimum_literal_bytes": 2,
            "compact_one_byte_unicode_only": True,
            "two_and_four_byte_unicode_preserved": True,
            "adaptive_first_or_last_anchor": True,
            "adaptive_sampling_minimum_window_bytes": 128,
            "adaptive_sample_maximum_bytes": 64,
            "matching_mode_count": 3,
            "nonoverlapping_collection_preserved": True,
            "buffer_acquisition_release_preserved": True,
            "additional_python_rust_boundary_crossing_count": 0,
            "external_regex_dependency_count": 0,
            "stdlib_matching_delegation_count": 0,
            "canonical_source_mutations": 0,
            "candidate_built": False, "candidate_matching": "NOT RUN"},
        "actual_previous_correctness": {
            "original_case_count": 31237, "original_mismatch_count": 0,
            "wider_public_case_count": 10434, "wider_public_mismatch_count": 0,
            "static_external_regex_dependency_count": 0,
            "live_runtime_non_delegation": "NOT ESTABLISHED"},
        "historical_public_evidence": {
            "receipt_sha256": PERFORMANCE_RECEIPT_SHA256,
            "summary_sha256": PERFORMANCE_SUMMARY_SHA256,
            "case_count": 416, "paired_trial_count": 1664,
            "faster_case_count": 252, "slower_case_count": 164,
            "geomean_speedup_vs_stdlib_decimal": "1.2424347186648022",
            "confidence_95_lower_decimal": "1.189358106927207",
            "confidence_95_upper_decimal": "1.301024782265517",
            "regression_over_20_percent_count": 14,
            "targeted_literal_regression_case_count": len(TARGETED_CASES),
            "targeted_literal_regression_cases": list(TARGETED_CASES),
            "preserved_other_regression_case_count": len(PRESERVED_OTHER_CASES),
            "preserved_other_regression_cases": list(PRESERVED_OTHER_CASES),
            "new_architecture_performance": NOT_MEASURED},
        "independent_synthetic_semantics": semantics,
        "physical_source_wall": {
            "policy": "CONTINUOUS DENY DEFAULT; PINNED OWNER DESCRIPTORS",
            "installed_before_owner_reads": True,
            "root_output_parent_inode": PARENT_INODE,
            "root_output_directory_mode": "0700", "root_output_file_mode": "0600",
            "root_output_file_policy": "O_CREAT|O_EXCL|O_NOFOLLOW",
            "linux_o_tmpfile_composite_rejected": True,
            "source_mode_filesystem_writes_permitted": 0,
            "proposal_or_holdout_metadata_probes_permitted": 0,
            "raw_paired_timing_observation_opens_permitted": 0,
            "public_summary_owner_only_permitted": True,
            "archive_opens_permitted": 0, "native_binary_opens_permitted": 0,
            "candidate_or_compiler_processes_permitted": 0,
            "clock_or_timer_samples_permitted": 0},
        "source_only_effects": {
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_processes_started": 0, "compiler_processes_started": 0,
            "native_binary_files_opened": 0, "native_libraries_loaded": 0,
            "raw_paired_observations_opened": 0, "archives_opened": 0,
            "private_roots_opened": 0, "proposal_files_opened": 0,
            "proposal_metadata_probes": 0, "final_holdout_files_opened": 0,
            "final_holdout_metadata_probes": 0, "clock_samples": 0,
            "timing_trials_run": 0, "workspace_mutations": 0,
            "candidate_correctness": NOT_MEASURED,
            "candidate_performance": NOT_MEASURED,
            "candidate_memory": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False},
        "original_case_execution_denominator": 31237,
        "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
        "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
        "candidate_qualified": False, "winner_selected": False,
        "holdout": "NOT OPENED"}


def arguments(values: list[str]) -> tuple[str, dict[str, str], frozenset[str]]:
    require(bool(values), "select exactly one bridge freeze action")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject unauthorized bridge freeze action")
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
                "reject missing, repeated, or foreign bridge freeze pins")
        pins[key] = sha(values[index + 1], key) if key.endswith("sha256") \
            else pushed(values[index + 1], key)
        index += 2
    if mode == "--render-contract":
        require(set(pins) == {"--source-sha256", "--protocol-sha256"} and not flags,
                "render the canonical freeze using exactly two owners")
    elif mode in ("--verify-source", "--self-test"):
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
                and not flags, "source gates require exactly three freeze owners")
    else:
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256",
                              "--frozen-commit", "--pushed-commit"}
                and flags == {"--root-authorized", "--frozen-committed-pushed"}
                and pins["--frozen-commit"] == pins["--pushed-commit"],
                "root application requires an identical committed and pushed full freeze")
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
    corrected = derive_bridge(evidence["complete_bridge"])
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
    raise FreezeError("hostile bridge source control escaped: " + name)


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
            "clock_sample_count": 0, "wall_remains_installed": wall.installed}


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
            "authenticate the pushed root-only complete C bridge source freeze")
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
            "create exactly one root-owned private bridge source directory")
    output = os.open("py_bridge.c", os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=child)
    initial = os.fstat(output)
    require(stat.S_ISREG(initial.st_mode) and stat.S_IMODE(initial.st_mode) == 0o600
            and initial.st_dev == DEVICE and initial.st_uid == os.geteuid()
            and initial.st_nlink == 1 and initial.st_size == 0,
            "create one exclusive no-follow private bridge source file")
    while wall.written < len(corrected):
        os.write(output, memoryview(corrected)[wall.written:])
    os.fsync(output)
    complete = os.fstat(output)
    require(complete.st_dev == initial.st_dev and complete.st_ino == initial.st_ino
            and complete.st_size == target_bytes and complete.st_nlink == 1
            and stat.S_IMODE(complete.st_mode) == 0o600,
            "reject incomplete, swapped, linked, or public bridge source")
    os.close(output)
    os.fsync(child)
    os.close(child)
    os.fsync(parent)
    os.close(parent)
    require(wall.output_opened and wall.output_synced and wall.child_synced
            and wall.parent_synced and wall.output_fd is None
            and wall.child_fd is None and wall.parent_fd is None,
            "synchronize exactly one bridge source and both private directories")
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
            "workspace_mutation_count": 2, "continuous_source_wall_active": True,
            "bounded_matching_case_count":
                state["semantics"]["bounded_matching_case_count"],
            "bounded_collection_case_count":
                state["semantics"]["bounded_collection_case_count"],
            "targeted_previous_regression_count": len(TARGETED_CASES),
            "all_previous_regression_count": len(TARGETED_CASES) + len(PRESERVED_OTHER_CASES),
            "external_regex_dependency_count": 0,
            "stdlib_matching_delegation_count": 0,
            "additional_python_rust_boundary_crossing_count": 0,
            "canonical_source_mutations": 0, "candidate_executions": 0,
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "raw_paired_observations_opened": 0,
            "archives_opened": 0, "proposal_files_opened": 0,
            "proposal_metadata_probes": 0, "final_holdout_files_opened": 0,
            "final_holdout_metadata_probes": 0, "clock_samples": 0,
            "original_case_execution_denominator": 31237,
            "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
            "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False}


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
                  "derived_target_sha256": digest(state["corrected"]),
                  "derived_target_bytes": len(state["corrected"]),
                  "bounded_matching_case_count":
                      state["semantics"]["bounded_matching_case_count"],
                  "bounded_collection_case_count":
                      state["semantics"]["bounded_collection_case_count"],
                  "all_previous_regression_count": 14,
                  "targeted_previous_regression_count": 10,
                  "preserved_other_regression_count": 4,
                  "external_regex_dependency_count": 0,
                  "stdlib_matching_delegation_count": 0,
                  "additional_python_rust_boundary_crossing_count": 0,
                  "canonical_source_mutations": 0,
                  "candidate_executions": 0, "candidate_imports": 0,
                  "candidate_processes_started": 0,
                  "native_libraries_loaded": 0,
                  "raw_paired_observations_opened": 0,
                  "archives_opened": 0, "private_roots_opened": 0,
                  "proposal_files_opened": 0, "proposal_metadata_probes": 0,
                  "final_holdout_files_opened": 0,
                  "final_holdout_metadata_probes": 0,
                  "clock_samples": 0, "workspace_mutations": 0,
                  "candidate_correctness": NOT_MEASURED,
                  "performance": NOT_MEASURED, "memory": NOT_MEASURED,
                  "undefined_behavior": NOT_MEASURED,
                  "candidate_qualified": False, "winner_selected": False}
        if mode == "--self-test":
            result["self_test"] = self_test(wall, state)
    clean_imports()
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FreezeError as failure:
        sys.stderr.write("literal bridge freeze rejected: " + str(failure) + "\n")
        raise SystemExit(2) from failure
