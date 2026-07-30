#!/usr/bin/env python3
"""Freeze a conservative first-party exact-literal Rust execution shortcut."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("exact-literal source freeze must not load a matching engine")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_exact_literal_fastpath_v1.py"
PROTOCOL = "oracle/phase2/RUST-EXACT-LITERAL-FASTPATH-V1.md"
CONTRACT = "oracle/phase2/rust-exact-literal-fastpath-v1.json"
PARENT = "candidates/rust/variants"
DIRECTORY = "exact_literal_fastpath_v1"
TARGET = PARENT + "/" + DIRECTORY + "/lib.rs"
SCHEMA = "rebar-owned-rust-exact-literal-fastpath-v1-source-freeze"
DEVICE = 2064
PARENT_INODE = 524946
MAX_OWNER_BYTES = 1_048_576
NOT_MEASURED = "NOT MEASURED"
I = 2
L = 4
BYTE = 1 << 31
CAPACITY = 32

BASE_SHA256 = "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38"
BASE_BYTES = 189493
COMBINED_SHA256 = "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
CANONICAL_SHA256 = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
SCOPED_SHA256 = "e5971616329a1622a7514954ec26871ff8465db87ad1a956cea104ee8a8478ac"
SEARCH_SHA256 = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
TARGET_SHA256 = "7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136"
TARGET_BYTES = 194276

OLD_GUARD = (
    b"    if locale_byte_flags(global_flags) || contains_locale_sensitive_expression(root) {\n"
    b"        return None;\n"
    b"    }"
)
NEW_GUARD = (
    b"    if locale_byte_flags(global_flags)\n"
    b"        || contains_locale_sensitive_expression(root)\n"
    b"        || has_scoped_category_prefix(root, global_flags)\n"
    b"    {\n"
    b"        return None;\n"
    b"    }"
)

OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_ledger", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("scoped_combination_source", "tools/apply_owned_rust_combined_scoped_unicode_engine_v1.py",
     "819b2a2576825e7bb84738564e432162063240ed09b9d3b8031c3815d2d17d16", 74851, 430270),
    ("scoped_combination_protocol", "oracle/phase2/RUST-COMBINED-SCOPED-UNICODE-ENGINE-V1.md",
     "6eba43efaa7019826806055ef2af6d0fe8cf180884f53baac0457d911ec9c36b", 5807, 524902),
    ("scoped_combination_contract", "oracle/phase2/rust-combined-scoped-unicode-engine-v1.json",
     "d5eb343f1ab16ace5d3ae9038a934d7a2dc5a22282e1e81f607234478c01a570", 9863, 525036),
    ("canonical_engine", "candidates/rust/src/lib.rs",
     CANONICAL_SHA256, 177967, 428096),
    ("standalone_scoped_engine", "candidates/rust/variants/scoped_unicode_startset_v1/lib.rs",
     SCOPED_SHA256, 178037, 524924),
    ("combined_engine", "candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs",
     COMBINED_SHA256, 189423, 525097),
    ("combined_search", "candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs",
     SEARCH_SHA256, 24305, 525098),
    ("cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("historical_v28_public_receipt",
     "oracle/phase2/evidence/rust-native-architecture-public-gate-v3-"
     "v28-combined-public-run-001-publication-receipt.json",
     "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb", 40372, 525923),
)

PLAN_ANCHOR = b"\n\npub struct Engine {\n"
PLAN_SOURCE = b"""

/// A proven, capture-free, exact-case byte-valued literal expression.
#[derive(Clone, Copy)]
struct ExactLiteralPlan {
    bytes: [u8; 32],
    length: u8,
}

impl ExactLiteralPlan {
    #[inline]
    fn new(root: &Expr, groups: usize) -> Option<Self> {
        if groups != 0 {
            return None;
        }
        let Expr::Seq(values) = root else {
            return None;
        };
        if !(2..=32).contains(&values.len()) {
            return None;
        }
        let mut plan = Self { bytes: [0; 32], length: values.len() as u8 };
        for (index, expression) in values.iter().enumerate() {
            let Expr::Lit(value, flags) = expression else {
                return None;
            };
            if flags & (I | L) != 0 {
                return None;
            }
            plan.bytes[index] = u8::try_from(*value).ok()?;
        }
        Some(plan)
    }

    #[inline(always)]
    fn as_slice(&self) -> &[u8] {
        &self.bytes[..usize::from(self.length)]
    }
}
"""

RUN_MATCH_ANCHOR = b"\nfn run_match(\n    engine: &Engine,\n"
MATCH_HELPERS = b"""

/// Find the first full literal using the existing bounded native byte primitive.
#[inline]
fn exact_literal_next(
    plan: &ExactLiteralPlan,
    values: &[u8],
    from: usize,
    end: usize,
) -> Option<usize> {
    let stop = end.min(values.len());
    let needle = plan.as_slice();
    if from > stop || needle.len() > stop.saturating_sub(from) {
        return None;
    }
    let final_offset = needle.len() - 1;
    let mut cursor = from.checked_add(final_offset)?;
    while let Some(last) = search::next_singleton(values, needle[final_offset], cursor, stop) {
        let start = last - final_offset;
        if values.get(start..=last) == Some(needle) {
            return Some(start);
        }
        cursor = last.checked_add(1)?;
    }
    None
}

/// Preserve Python's exact bounded search, match, and fullmatch semantics.
#[inline]
fn exact_literal_match(
    plan: &ExactLiteralPlan,
    context: &Context<'_>,
    pos: usize,
    mode: u8,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) -> Option<i32> {
    let values = context.bytes.or_else(|| {
        context.wide.filter(|subject| subject.kind == 1).map(|subject| subject.data)
    })?;
    if mode > 2 {
        return None;
    }
    begins.fill(-1);
    ends.fill(-1);
    *last = -1;
    let end = context.end.min(values.len());
    let length = usize::from(plan.length);
    if pos > end || length > end.saturating_sub(pos) {
        return Some(0);
    }
    let start = match mode {
        0 => match exact_literal_next(plan, values, pos, end) {
            Some(found) => found,
            None => return Some(0),
        },
        1 | 2 => {
            if mode == 2 && end - pos != length {
                return Some(0);
            }
            let finish = pos + length;
            if values.get(pos..finish) != Some(plan.as_slice()) {
                return Some(0);
            }
            pos
        },
        _ => unreachable!("validated matching mode"),
    };
    begins[0] = start as isize;
    ends[0] = (start + length) as isize;
    Some(1)
}

/// Collect nonoverlapping, nonempty exact literals in one native traversal.
#[inline]
fn exact_literal_collect(
    plan: &ExactLiteralPlan,
    context: &Context<'_>,
    pos: usize,
    capacity: usize,
    starts: &mut [isize],
    finishes: &mut [isize],
    lasts: &mut [isize],
) -> Option<isize> {
    let values = context.bytes.or_else(|| {
        context.wide.filter(|subject| subject.kind == 1).map(|subject| subject.data)
    })?;
    let end = context.end.min(values.len());
    if pos > end || capacity == 0 {
        return Some(0);
    }
    let length = usize::from(plan.length);
    let mut cursor = pos;
    let mut count = 0;
    while count < capacity {
        let Some(begin) = exact_literal_next(plan, values, cursor, end) else {
            break;
        };
        let finish = begin + length;
        starts[count] = begin as isize;
        finishes[count] = finish as isize;
        lasts[count] = -1;
        count += 1;
        cursor = finish;
    }
    Some(count as isize)
}
"""

RUN_GUARD = (
    b"    if pos > context.end && mode != 1 {\n"
    b"        return 0;\n"
    b"    }\n\n"
    b"    let last_start ="
)
RUN_GUARD_REPLACEMENT = (
    b"    if pos > context.end && mode != 1 {\n"
    b"        return 0;\n"
    b"    }\n"
    b"    if let Some(plan) = engine.exact_literal.as_ref()\n"
    b"        && let Some(result) = exact_literal_match(\n"
    b"            plan, context, pos, mode, begins, ends, last\n"
    b"        )\n"
    b"    {\n"
    b"        return result;\n"
    b"    }\n\n"
    b"    let last_start ="
)
COLLECT_GUARD = (
    b") -> isize {\n"
    b"    if let Some(delimiter) = engine.even_suffix_delimiter\n"
)
COLLECT_GUARD_REPLACEMENT = (
    b") -> isize {\n"
    b"    if let Some(plan) = engine.exact_literal.as_ref()\n"
    b"        && let Some(result) = exact_literal_collect(\n"
    b"            plan, context, pos, capacity, starts, finishes, last_values\n"
    b"        )\n"
    b"    {\n"
    b"        return result;\n"
    b"    }\n"
    b"    if let Some(delimiter) = engine.even_suffix_delimiter\n"
)


class FreezeError(Exception):
    """Reject incorrect provenance, semantics, effects, or materialization."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash complete genuine immutable bytes")
    return hashlib.sha256(value).hexdigest()


def sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require a complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def commit(value: object, label: str) -> str:
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
            "reject matcher, candidate, package, subprocess, or native-loader imports")


def canonical(value: object, depth: int = 0) -> str:
    require(depth < 64, "reject excessive evidence nesting")
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
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "require text evidence keys")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject floating, nonfinite, or unsupported evidence")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class SourceWall:
    """Deny everything except exact immutable owners and one exclusive root output."""

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
        raise FreezeError("exact-literal source wall rejected " + category)

    def owner_path(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and not path.endswith((".so", ".gz", ".raw.json", ".jsonl")))

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
            output = (self.apply and self.stage == "child" and path == "lib.rs"
                      and self.output_flags(flags) and not self.output_opened)
            if not any((readonly, parent, child, output)):
                self.deny("unowned-source-native-raw-archive-proposal-final-or-write-open")
        elif event == "os.mkdir":
            path = values[0] if values else None
            mode = values[1] if len(values) > 1 else None
            parent = values[2] if len(values) > 2 else None
            if not (self.apply and self.stage == "parent" and path == DIRECTORY
                    and mode == 0o700 and parent == self.parent_fd):
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
        require(not self.installed, "install the permanent source wall exactly once")
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
            output = (self.apply and self.stage == "child" and path == "lib.rs"
                      and dir_fd == self.child_fd and self.output_flags(flags)
                      and mode == 0o600 and not self.output_opened)
            if not any((readonly, parent, child, output)):
                self.deny("foreign-owner-directory-or-output-descriptor")
            descriptor = raw_open(path, flags, mode, dir_fd=dir_fd)
            require(type(descriptor) is int and descriptor >= 0
                    and descriptor not in self.owner_fds
                    and descriptor not in (self.parent_fd, self.child_fd, self.output_fd),
                    "reject reused, inherited, or invalid descriptor")
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
                self.deny("incorrect-or-out-of-order-source-output")
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
            "reject incomplete immutable owner identity")
    sha(expected, role)
    descriptor = os.open(ROOT + "/" + path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode and before.st_size == size
                and before.st_nlink == 1 and before.st_uid == os.geteuid(),
                "reject replaced, linked, or nonprivate owner: " + role)
        blocks: list[bytes] = []
        remaining = size
        while remaining:
            block = os.read(descriptor, min(65536, remaining))
            require(bool(block), "reject incomplete immutable owner: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject trailing immutable owner bytes")
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject concurrently modified immutable owner: " + role)
        raw = b"".join(blocks)
        require(digest(raw) == expected, "reject changed immutable owner: " + role)
        return raw
    finally:
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, path: str, expected: str) -> tuple[object, ...]:
    require(path in (SOURCE, PROTOCOL, CONTRACT), "reject unrelated live freeze owner")
    sha(expected, role)
    descriptor = os.open(ROOT + "/" + path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        owner = os.fstat(descriptor)
        require(stat.S_ISREG(owner.st_mode) and stat.S_IMODE(owner.st_mode) == 0o600
                and owner.st_dev == DEVICE and owner.st_nlink == 1
                and owner.st_uid == os.geteuid() and 0 < owner.st_size <= MAX_OWNER_BYTES,
                "reject changed or nonprivate live freeze owner")
    finally:
        os.close(descriptor)
    return role, path, expected, owner.st_size, owner.st_ino


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    role, path, value, size, inode = row
    return {"role": role, "path": path, "sha256": value, "bytes": size,
            "inode": inode, "device": DEVICE, "mode": "0600", "nlink": 1}


def replace_once(source: bytes, before: bytes, after: bytes, label: str) -> bytes:
    require(source.count(before) == 1 and after not in source,
            "require a unique, unapplied first-party source site: " + label)
    result = source.replace(before, after, 1)
    require(result.count(after) == 1 and result.replace(after, before, 1) == source,
            "require an exact reversible first-party source edit: " + label)
    return result


def derive_base(evidence: dict[str, bytes]) -> bytes:
    canonical_engine = evidence["canonical_engine"]
    standalone = evidence["standalone_scoped_engine"]
    combined = evidence["combined_engine"]
    require(canonical_engine.count(OLD_GUARD) == combined.count(OLD_GUARD) == 1
            and standalone.count(NEW_GUARD) == 1
            and canonical_engine.replace(OLD_GUARD, NEW_GUARD, 1) == standalone,
            "reproduce the materialized standalone scoped-Unicode correction exactly")
    result = combined.replace(OLD_GUARD, NEW_GUARD, 1)
    require(len(result) == BASE_BYTES and digest(result) == BASE_SHA256
            and result.replace(NEW_GUARD, OLD_GUARD, 1) == combined,
            "reconstruct the exact optimized scoped-Unicode parent in memory")
    contract = evidence["scoped_combination_contract"]
    for marker in (BASE_SHA256.encode(), COMBINED_SHA256.encode(), SEARCH_SHA256.encode(),
                   b'"candidate_qualified":false', b'"performance":"NOT MEASURED"'):
        require(marker in contract, "authenticate complete first-party parent obligations")
    require(evidence["cargo_manifest"].count(b"[package]") == 1
            and b"[dependencies]" not in evidence["cargo_manifest"]
            and evidence["cargo_lock"].count(b"[[package]]") == 1,
            "preserve one first-party Rust package and zero external dependencies")
    receipt = evidence["historical_v28_public_receipt"]
    for marker in (b'"candidate_qualified":false', b'"public_10434_case_count":10434',
                   b'"public_10434_mismatch_count":1145', b'"case_count":416',
                   b'"faster_case_count":208',
                   b'"geomean_speedup_vs_stdlib":1.2298384265743338'):
        require(marker in receipt, "preserve the exact historical public-only evidence")
    return result


def derive_engine(base: bytes, frozen: bool = True) -> bytes:
    require(type(base) is bytes and len(base) == BASE_BYTES and digest(base) == BASE_SHA256,
            "require the complete predicted corrected first-party Rust parent")
    require(base.count(PLAN_ANCHOR) == 1 and base.count(RUN_MATCH_ANCHOR) == 1
            and base.count(RUN_GUARD) == 1 and base.count(COLLECT_GUARD) == 1,
            "locate unique engine, match, bounded-window, and collection sites")
    result = replace_once(base, PLAN_ANCHOR, PLAN_SOURCE + PLAN_ANCHOR, "literal plan")
    result = replace_once(result,
        b"    byte_mode: bool,\n    deterministic: bool,\n",
        b"    byte_mode: bool,\n    exact_literal: Option<ExactLiteralPlan>,\n"
        b"    deterministic: bool,\n", "engine plan field")
    result = replace_once(result,
        b"            let deterministic = deterministic_program(&program, parser.groups);\n",
        b"            let deterministic = deterministic_program(&program, parser.groups);\n"
        b"            let exact_literal = ExactLiteralPlan::new(&root, parser.groups);\n",
        "pattern-only plan recognition")
    result = replace_once(result,
        b"                byte_mode: byte_mode != 0,\n                deterministic,\n",
        b"                byte_mode: byte_mode != 0,\n                exact_literal,\n"
        b"                deterministic,\n", "pattern plan installation")
    result = replace_once(result,
        b"        byte_mode: false,\n        deterministic,\n",
        b"        byte_mode: false,\n        exact_literal: None,\n        deterministic,\n",
        "scanner plan exclusion")
    result = replace_once(result,
        b"            byte_mode: true,\n            deterministic: false,\n",
        b"            byte_mode: true,\n            exact_literal: None,\n"
        b"            deterministic: false,\n", "capture regression test initializer")
    result = replace_once(result,
        b"            byte_mode: true,\n            deterministic,\n",
        b"            byte_mode: true,\n            exact_literal: None,\n"
        b"            deterministic,\n", "locale regression test initializer")
    result = replace_once(result, RUN_MATCH_ANCHOR, MATCH_HELPERS + RUN_MATCH_ANCHOR,
                          "exact bounded literal helpers")
    result = replace_once(result, RUN_GUARD, RUN_GUARD_REPLACEMENT,
                          "conservative matching dispatch")
    result = replace_once(result, COLLECT_GUARD, COLLECT_GUARD_REPLACEMENT,
                          "conservative nonoverlapping collection dispatch")
    require(result.count(b"ExactLiteralPlan::new(&root, parser.groups)") == 1
            and result.count(b"search::next_singleton(values, needle[final_offset], cursor, stop)") == 1
            and result.count(b"exact_literal: None,") == 3
            and result.count(b"engine.exact_literal.as_ref()") == 2
            and result.count(NEW_GUARD) == 1 and OLD_GUARD not in result,
            "retain exact scoped Unicode, scanner exclusions, and first-party literal dispatch")
    forbidden = (b"extern crate regex", b"use regex::Regex", b"pcre2", b"oniguruma",
                 b"std::process::Command", b"dlopen(", b"PyImport_ImportModule")
    require(not any(marker in PLAN_SOURCE + MATCH_HELPERS
                    + RUN_GUARD_REPLACEMENT + COLLECT_GUARD_REPLACEMENT
                    for marker in forbidden), "reject matching delegation or external engines")
    if frozen:
        require(len(result) == TARGET_BYTES and digest(result) == TARGET_SHA256,
                "reject nonfrozen complete exact-literal engine bytes")
    return result


def words(alphabet: tuple[int, ...], maximum: int):
    current = [()]
    yield ()
    for _length in range(maximum):
        current = [prefix + (value,) for prefix in current for value in alphabet]
        yield from current


def recognize(expression: tuple, groups: int) -> tuple[int, ...] | None:
    if groups != 0 or not expression or expression[0] != "seq":
        return None
    values = expression[1]
    if not 2 <= len(values) <= CAPACITY:
        return None
    answer: list[int] = []
    for item in values:
        if len(item) != 3 or item[0] != "lit" or item[2] & (I | L) \
                or not 0 <= item[1] <= 255:
            return None
        answer.append(item[1])
    return tuple(answer)


def reference_next(needle: tuple[int, ...], subject: tuple[int, ...],
                   start: int, end: int) -> int | None:
    end = min(end, len(subject))
    if start > end or len(needle) > end - start:
        return None
    for index in range(start, end - len(needle) + 1):
        if subject[index:index + len(needle)] == needle:
            return index
    return None


def accelerated_next(needle: tuple[int, ...], subject: tuple[int, ...],
                     start: int, end: int) -> int | None:
    end = min(end, len(subject))
    if start > end or len(needle) > end - start:
        return None
    offset = len(needle) - 1
    cursor = start + offset
    while cursor < end:
        while cursor < end and subject[cursor] != needle[offset]:
            cursor += 1
        if cursor == end:
            return None
        first = cursor - offset
        if subject[first:cursor + 1] == needle:
            return first
        cursor += 1
    return None


def model_match(needle: tuple[int, ...], subject: tuple[int, ...],
                start: int, end: int, mode: int, optimized: bool) -> tuple[int, int] | None:
    end = min(end, len(subject))
    if start > end or len(needle) > end - start:
        return None
    if mode == 0:
        first = (accelerated_next if optimized else reference_next)(needle, subject, start, end)
        return None if first is None else (first, first + len(needle))
    if mode == 2 and end - start != len(needle):
        return None
    return (start, start + len(needle)) \
        if subject[start:start + len(needle)] == needle else None


def model_collect(needle: tuple[int, ...], subject: tuple[int, ...],
                  start: int, end: int, capacity: int,
                  optimized: bool) -> tuple[tuple[int, int], ...]:
    next_match = accelerated_next if optimized else reference_next
    cursor = start
    result: list[tuple[int, int]] = []
    while len(result) < capacity:
        first = next_match(needle, subject, cursor, end)
        if first is None:
            break
        finish = first + len(needle)
        result.append((first, finish))
        cursor = finish
    return tuple(result)


def semantic_model() -> dict[str, object]:
    alphabet = (0, 97, 255)
    subjects = tuple(words(alphabet, 4))
    needles = tuple(value for value in words(alphabet, 4) if len(value) >= 2)
    cases = matches = collections = bounded_windows = high_byte_cases = 0
    projection = hashlib.sha256()
    for subject in subjects:
        windows = sorted({0, 1, max(len(subject) - 1, 0), len(subject), len(subject) + 1})
        for needle in needles:
            shape = ("seq", tuple(("lit", value, BYTE) for value in needle))
            require(recognize(shape, 0) == needle, "reject a genuine exact-case literal")
            for start in windows:
                for end in windows:
                    bounded_windows += 1
                    for mode in (0, 1, 2):
                        expected = model_match(needle, subject, start, end, mode, False)
                        actual = model_match(needle, subject, start, end, mode, True)
                        require(actual == expected,
                                "literal search changed exact bounded leftmost matching")
                        matches += int(actual is not None)
                        high_byte_cases += int(255 in needle or 255 in subject)
                        cases += 1
                        projection.update((str(subject) + str(needle) + str(start)
                                           + str(end) + str(mode) + str(actual)).encode())
                    for capacity in (0, 1, 2, 5):
                        expected = model_collect(needle, subject, start, end, capacity, False)
                        actual = model_collect(needle, subject, start, end, capacity, True)
                        require(actual == expected,
                                "literal collection changed nonoverlapping leftmost order")
                        collections += 1
    rejected = (
        (("seq", ()), 0),
        (("seq", (("lit", 97, 0),)), 0),
        (("seq", (("lit", 97, I), ("lit", 98, 0))), 0),
        (("seq", (("lit", 97, L), ("lit", 98, 0))), 0),
        (("seq", (("lit", 97, 0), ("lit", 256, 0))), 0),
        (("seq", (("lit", 97, 0), ("lit", 0x1F600, 0))), 0),
        (("seq", (("lit", 97, 0), ("cat", "w", 0))), 0),
        (("seq", (("lit", 97, 0), ("lit", 98, 0))), 1),
        (("group", (("lit", 97, 0), ("lit", 98, 0))), 0),
        (("alt", (("lit", 97, 0), ("lit", 98, 0))), 0),
        (("seq", tuple(("lit", 97, 0) for _ in range(CAPACITY + 1))), 0),
    )
    for expression, groups in rejected:
        require(recognize(expression, groups) is None,
                "reject captures, empty, singleton, locale, folding, or nonliteral paths")
    require(recognize(("seq", (("lit", 97, BYTE), ("lit", 255, 32))), 0)
            == (97, 255), "retain exact byte and Unicode-safe literal flags")
    require(cases > 400000 and collections > 500000 and matches > 0,
            "require exhaustive independent bounded matching and collection models")
    return {"bounded_match_case_count": cases,
            "bounded_collection_case_count": collections,
            "bounded_window_count": bounded_windows,
            "successful_match_case_count": matches,
            "high_byte_case_count": high_byte_cases,
            "excluded_expression_family_count": len(rejected),
            "subject_family_count": len(subjects),
            "literal_family_count": len(needles),
            "projection_sha256": projection.hexdigest(),
            "candidate_executed": False, "external_matcher_imported": False}


def make_contract(source: tuple[object, ...], protocol: tuple[object, ...],
                  corrected: bytes, synthetic: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA, "version": 1, "family": "rust", "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
        "source": owner_document(source), "protocol": owner_document(protocol),
        "authenticated_previous_owner_count": len(OWNERS),
        "authenticated_previous_owners": [owner_document(row) for row in OWNERS],
        "first_party_source_composition": {
            "optimized_scoped_parent_path":
                "candidates/rust/variants/combined_scoped_unicode_engine_v1/lib.rs",
            "optimized_scoped_parent_sha256": BASE_SHA256,
            "optimized_scoped_parent_bytes": BASE_BYTES,
            "optimized_parent_materialized_source_required": False,
            "combined_engine_sha256": COMBINED_SHA256,
            "unchanged_search_source_sha256": SEARCH_SHA256,
            "target_path": TARGET, "target_sha256": digest(corrected),
            "target_bytes": len(corrected),
            "source_delta_bytes": len(corrected) - BASE_BYTES,
            "plan_maximum_bytes": CAPACITY, "plan_minimum_bytes": 2,
            "case_sensitive_only": True, "locale_sensitive_excluded": True,
            "capturing_patterns_excluded": True, "nonliteral_patterns_excluded": True,
            "empty_and_singleton_patterns_excluded": True,
            "unicode_two_and_four_byte_storage_excluded": True,
            "existing_first_party_bounded_memchr_reused": True,
            "matching_mode_count": 3, "nonoverlapping_collection_retained": True,
            "exact_scoped_unicode_correction_retained": True,
            "mandatory_anchor_search_retained": True,
            "compiler_allocation_fastpath_retained": True,
            "external_regex_dependency_count": 0,
            "stdlib_matching_delegation_count": 0,
            "canonical_source_mutations": 0,
            "candidate_built": False, "candidate_matching": "NOT RUN"},
        "historical_public_evidence": {
            "receipt_sha256": OWNERS[-1][2], "case_count": 416,
            "faster_case_count": 208,
            "geomean_speedup_vs_stdlib_decimal": "1.2298384265743338",
            "wider_public_case_count": 10434,
            "wider_public_mismatch_count": 1145,
            "candidate_qualified": False,
            "new_architecture_performance": NOT_MEASURED},
        "independent_synthetic_semantics": synthetic,
        "physical_source_wall": {
            "policy": "CONTINUOUS DENY DEFAULT; PINNED OWNER DESCRIPTORS",
            "installed_before_owner_reads": True,
            "root_output_parent_inode": PARENT_INODE,
            "root_output_directory_mode": "0700", "root_output_file_mode": "0600",
            "root_output_file_policy": "O_CREAT|O_EXCL|O_NOFOLLOW",
            "linux_o_tmpfile_composite_rejected": True,
            "source_mode_filesystem_writes_permitted": 0,
            "proposal_or_holdout_metadata_probes_permitted": 0,
            "raw_public_observation_opens_permitted": 0,
            "archive_opens_permitted": 0, "native_binary_opens_permitted": 0,
            "candidate_or_compiler_processes_permitted": 0,
            "clock_or_timer_samples_permitted": 0},
        "source_only_effects": {
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_processes_started": 0, "compiler_processes_started": 0,
            "native_binary_files_opened": 0, "native_libraries_loaded": 0,
            "raw_public_observations_opened": 0, "archives_opened": 0,
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
    require(bool(values), "select exactly one exact-literal freeze action")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject missing, combined, or unknown freeze action")
    pins: dict[str, str] = {}
    flags: set[str] = set()
    index = 1
    while index < len(values):
        key = values[index]
        if key in ("--root-authorized", "--frozen-committed-pushed"):
            require(key not in flags, "reject repeated root authorization")
            flags.add(key)
            index += 1
            continue
        require(key in ("--source-sha256", "--protocol-sha256", "--contract-sha256",
                        "--frozen-commit", "--pushed-commit")
                and key not in pins and index + 1 < len(values),
                "reject unknown, missing, or repeated owner authentication")
        pins[key] = sha(values[index + 1], key) if key.endswith("sha256") \
            else commit(values[index + 1], key)
        index += 2
    if mode == "--render-contract":
        require(set(pins) == {"--source-sha256", "--protocol-sha256"} and not flags,
                "render using exactly two authenticated freeze owners")
    elif mode in ("--verify-source", "--self-test"):
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
                and not flags, "source gates require exactly three owner fingerprints")
    else:
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256",
                              "--frozen-commit", "--pushed-commit"}
                and flags == {"--root-authorized", "--frozen-committed-pushed"}
                and pins["--frozen-commit"] == pins["--pushed-commit"],
                "root application requires a completely committed and pushed source freeze")
    return mode, pins, frozenset(flags)


def load_context(wall: SourceWall, mode: str, pins: dict[str, str]) -> dict[str, object]:
    source = live_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol = live_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source)
    read_owner(wall, protocol)
    contract_owner = None if mode == "--render-contract" else live_owner(
        wall, "contract", CONTRACT, pins["--contract-sha256"])
    evidence = {row[0]: read_owner(wall, row) for row in OWNERS}
    base = derive_base(evidence)
    corrected = derive_engine(base)
    synthetic = semantic_model()
    contract_value = make_contract(source, protocol, corrected, synthetic)
    if contract_owner is not None:
        require(read_owner(wall, contract_owner) == document(contract_value),
                "reject omitted, changed, reordered, or incomplete frozen obligations")
    require(not wall.owner_fds and wall.parent_fd is None and wall.child_fd is None
            and wall.output_fd is None and not wall.output_opened,
            "close every exact immutable owner without foreign access")
    clean_imports()
    return {"contract": contract_value, "corrected": corrected, "synthetic": synthetic}


def rejected(wall: SourceWall, name: str, callback) -> str:
    previous = sum(wall.blocked.values())
    try:
        callback()
    except (FreezeError, OSError, ValueError, TypeError, IndexError):
        require(sum(wall.blocked.values()) > previous,
                "hostile control failed before reaching the permanent wall: " + name)
        return name
    raise FreezeError("hostile source-wall control escaped: " + name)


def self_test(wall: SourceWall, state: dict[str, object]) -> dict[str, object]:
    own = ROOT + "/" + SOURCE
    native = sys.modules["posix"]
    controls = [
        rejected(wall, "builtins-open", lambda: builtins.open(own, "rb")),
        rejected(wall, "io-open", lambda: io.open(own, "rb")),
        rejected(wall, "_io-open", lambda: _io.open(own, "rb")),
        rejected(wall, "missing-nofollow", lambda: os.open(own, os.O_RDONLY)),
        rejected(wall, "owner-write", lambda: os.open(own, os.O_WRONLY)),
        rejected(wall, "alias", lambda: os.open(ROOT + "/tools/../" + SOURCE,
                                                  os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "target-before-root", lambda: os.open(ROOT + "/" + TARGET,
                          os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        rejected(wall, "raw-public", lambda: os.open(
            ROOT + "/experiments/rust_native_architecture_public_v3/"
            "v28-combined-public-run-001/public-416-paired-timing.raw.json",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "native", lambda: os.open(ROOT + "/candidates/_rust_engine.so",
                                                    os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "archive", lambda: os.open(ROOT + "/oracle/phase2/private.json.gz",
                                                     os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "holdout-open", lambda: os.open(
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
        rejected(wall, "native-alias-read", lambda: native.read(0, 1)),
        rejected(wall, "native-alias-write", lambda: native.write(1, b"reject")),
        rejected(wall, "candidate-process", lambda: os.system("true")),
        rejected(wall, "dynamic-compilation", lambda: compile(b"1", "hostile.py", "exec")),
        rejected(wall, "dynamic-execution", lambda: exec("1")),
        rejected(wall, "external-engine", lambda: __import__("re")),
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
            "complete hostile no-write, no-process, no-holdout physical controls")
    return {"hostile_control_count": len(controls), "hostile_controls": controls,
            "physically_blocked_categories": dict(wall.blocked),
            "candidate_process_count": 0, "proposal_content_open_count": 0,
            "proposal_metadata_probe_count": 0,
            "raw_public_observation_content_open_count": 0,
            "final_holdout_content_open_count": 0,
            "final_holdout_metadata_probe_count": 0,
            "clock_sample_count": 0, "wall_remains_installed": wall.installed}


def apply_root(wall: SourceWall, state: dict[str, object], pins: dict[str, str],
               authorization: frozenset[str]) -> dict[str, object]:
    corrected = state["corrected"]
    require(wall.apply and authorization == {"--root-authorized", "--frozen-committed-pushed"}
            and pins["--frozen-commit"] == pins["--pushed-commit"]
            and pins["--source-sha256"] == state["contract"]["source"]["sha256"]
            and pins["--protocol-sha256"] == state["contract"]["protocol"]["sha256"]
            and digest(corrected) == TARGET_SHA256 and len(corrected) == TARGET_BYTES
            and not wall.owner_fds and wall.stage == "source",
            "authenticate the committed and pushed root-only exact source experiment")
    wall.expected, wall.stage = corrected, "ready"
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open(ROOT + "/" + PARENT, flags)
    parent_metadata = os.fstat(parent)
    require(stat.S_ISDIR(parent_metadata.st_mode)
            and stat.S_IMODE(parent_metadata.st_mode) == 0o700
            and parent_metadata.st_dev == DEVICE and parent_metadata.st_ino == PARENT_INODE
            and parent_metadata.st_uid == os.geteuid(),
            "authenticate the exact existing first-party variants parent")
    os.mkdir(DIRECTORY, 0o700, dir_fd=parent)
    child = os.open(DIRECTORY, flags, dir_fd=parent)
    child_metadata = os.fstat(child)
    require(stat.S_ISDIR(child_metadata.st_mode)
            and stat.S_IMODE(child_metadata.st_mode) == 0o700
            and child_metadata.st_dev == DEVICE and child_metadata.st_uid == os.geteuid(),
            "authenticate one private, new exact-literal source directory")
    output = os.open("lib.rs", os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=child)
    initial = os.fstat(output)
    require(stat.S_ISREG(initial.st_mode) and stat.S_IMODE(initial.st_mode) == 0o600
            and initial.st_dev == DEVICE and initial.st_uid == os.geteuid()
            and initial.st_nlink == 1 and initial.st_size == 0,
            "create one exclusive, no-follow, private first-party source file")
    while wall.written < len(corrected):
        os.write(output, memoryview(corrected)[wall.written:])
    os.fsync(output)
    complete = os.fstat(output)
    require(complete.st_dev == initial.st_dev and complete.st_ino == initial.st_ino
            and complete.st_size == TARGET_BYTES and complete.st_nlink == 1
            and stat.S_IMODE(complete.st_mode) == 0o600,
            "reject incomplete, linked, exchanged, or public exact-literal source")
    os.close(output)
    os.fsync(child)
    os.close(child)
    os.fsync(parent)
    os.close(parent)
    require(wall.output_opened and wall.output_synced and wall.child_synced and wall.parent_synced
            and wall.output_fd is None and wall.child_fd is None and wall.parent_fd is None,
            "synchronize complete exact source and both private directories")
    return {"schema": SCHEMA + "-application", "status": "APPLIED", "mode": "apply",
            "source_sha256": pins["--source-sha256"],
            "protocol_sha256": pins["--protocol-sha256"],
            "contract_sha256": pins["--contract-sha256"],
            "frozen_pushed_commit": pins["--pushed-commit"],
            "created": {"directory": {"path": PARENT + "/" + DIRECTORY,
                                       "device": child_metadata.st_dev,
                                       "inode": child_metadata.st_ino, "mode": "0700"},
                        "engine": {"path": TARGET, "sha256": TARGET_SHA256,
                                   "bytes": TARGET_BYTES, "device": complete.st_dev,
                                   "inode": complete.st_ino, "mode": "0600", "nlink": 1,
                                   "exclusive_no_follow": True, "fsync_completed": True}},
            "workspace_mutation_count": 2, "continuous_source_wall_active": True,
            "bounded_match_case_count": state["synthetic"]["bounded_match_case_count"],
            "bounded_collection_case_count":
                state["synthetic"]["bounded_collection_case_count"],
            "external_regex_dependency_count": 0,
            "stdlib_matching_delegation_count": 0,
            "canonical_source_mutations": 0, "candidate_executions": 0,
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "raw_public_observations_opened": 0,
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
            "use pinned CPython 3.14.6 in isolated, bytecode-disabled, no-site mode")
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
                  "optimized_scoped_parent_sha256": BASE_SHA256,
                  "derived_target_sha256": digest(state["corrected"]),
                  "derived_target_bytes": len(state["corrected"]),
                  "bounded_match_case_count":
                      state["synthetic"]["bounded_match_case_count"],
                  "bounded_collection_case_count":
                      state["synthetic"]["bounded_collection_case_count"],
                  "external_regex_dependency_count": 0,
                  "stdlib_matching_delegation_count": 0,
                  "canonical_source_mutations": 0,
                  "candidate_executions": 0, "candidate_imports": 0,
                  "candidate_processes_started": 0, "native_libraries_loaded": 0,
                  "raw_public_observations_opened": 0, "archives_opened": 0,
                  "proposal_files_opened": 0, "proposal_metadata_probes": 0,
                  "final_holdout_files_opened": 0,
                  "final_holdout_metadata_probes": 0,
                  "clock_samples": 0, "workspace_mutations": 0,
                  "candidate_correctness": NOT_MEASURED,
                  "performance": NOT_MEASURED, "memory": NOT_MEASURED,
                  "undefined_behavior": NOT_MEASURED,
                  "candidate_qualified": False, "winner_selected": False}
        if mode == "--self-test":
            result["hostile"] = self_test(wall, state)
    sys.stdout.buffer.write(document(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError, IndexError,
            KeyError, AttributeError) as error:
        sys.stderr.write("exact-literal source freeze rejected: " + str(error) + "\n")
        raise SystemExit(2)
