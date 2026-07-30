#!/usr/bin/env python3
"""Freeze one first-party composition; only root may materialize its source."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("source verification must not import a regular-expression engine")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_combined_scoped_unicode_engine_v1.py"
PROTOCOL = "oracle/phase2/RUST-COMBINED-SCOPED-UNICODE-ENGINE-V1.md"
CONTRACT = "oracle/phase2/rust-combined-scoped-unicode-engine-v1.json"
PARENT = "candidates/rust/variants"
DIRECTORY = "combined_scoped_unicode_engine_v1"
TARGET = PARENT + "/" + DIRECTORY + "/lib.rs"
SCHEMA = "rebar-owned-rust-combined-scoped-unicode-engine-v1-source-freeze"
DEVICE = 2064
PARENT_INODE = 524946
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_DEPTH = 72
NOT_MEASURED = "NOT MEASURED"
A = 256
U = 32
L = 4
BYTE = 1 << 31

CANONICAL_SHA256 = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
SCOPED_SHA256 = "e5971616329a1622a7514954ec26871ff8465db87ad1a956cea104ee8a8478ac"
ANCHOR_SHA256 = "5fa8c47c88c1f5d830a59735946378910374afab6f1558d281f0254207ad5e84"
COMBINED_SHA256 = "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
SEARCH_SHA256 = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
CORRECTED_SHA256 = "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38"
CORRECTED_BYTES = 189493

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

# role, exact repository-relative plaintext path, SHA-256, byte count, inode.
# No public observation, proposal, holdout, binary, private build root, or
# archive is present. The retired proposal's old contract is also excluded.
OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_p0_ledger", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("actual_original_failure",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-"
     "rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json",
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("standalone_source", "tools/apply_owned_rust_scoped_unicode_startset_v1.py",
     "441006145a2b5ebc4cb4fa2c9c1717741af189ad41694297d5586bee55ec9fe9", 98978, 431577),
    ("standalone_protocol", "oracle/phase2/RUST-SCOPED-UNICODE-STARTSET-V1.md",
     "1a993cbe4dcafb0e6a08f67a6600cf393be8e9d79e34ac55f6d9a2191c037afd", 6595, 525924),
    ("standalone_contract", "oracle/phase2/rust-scoped-unicode-startset-v1.json",
     "fecd091f5424e70eebad50268daba4e1dd2044c9e8e3d307a7fd658cba8991da", 15288, 525925),
    ("standalone_application", "oracle/phase2/evidence/rust-scoped-unicode-startset-v1-application.json",
     "9c6c402fbfa3c8ac96ccee7847dcb071dc6b279f711de7bf3c5cb75fb178ca09", 1512, 524933),
    ("combined_application",
     "oracle/phase2/evidence/rust-combined-search-compiler-fastpath-v2-application.json",
     "1bce63305e04e4056ce3c660760a0bb8a3670a76aa528b9309232d0918c5061e", 2201, 525099),
    ("cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("canonical_engine", "candidates/rust/src/lib.rs",
     CANONICAL_SHA256, 177967, 428096),
    ("standalone_corrected_engine", "candidates/rust/variants/scoped_unicode_startset_v1/lib.rs",
     SCOPED_SHA256, 178037, 524924),
    ("mandatory_anchor_engine", "candidates/rust/variants/mandatory_anchor_search_v1/lib.rs",
     ANCHOR_SHA256, 189369, 526181),
    ("combined_engine", "candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs",
     COMBINED_SHA256, 189423, 525097),
    ("combined_search", "candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs",
     SEARCH_SHA256, 24305, 525098),
)


class FreezeError(Exception):
    """Reject changed evidence, an unsafe source effect, or an incorrect composition."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash complete immutable source bytes")
    return hashlib.sha256(value).hexdigest()


def exact_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1, "require exact SHA-256: " + label)
    assert isinstance(value, str)
    return value


def exact_commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1, "require a complete pushed commit: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "subprocess", "socket", "threading", "multiprocessing",
                 "random", "json", "candidates", "rebar", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject candidate, external matcher, process, native loader, or case generator")


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive contract nesting")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                   "\n": "\\n", "\r": "\\r", "\t": "\\t"}
        require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value),
                "reject an unpaired contract surrogate")
        return '"' + "".join(escapes.get(char, "\\u" + format(ord(char), "04x")
                                          if ord(char) < 32 else char)
                             for char in value) + '"'
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "require text contract keys")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported contract value")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class StrictJSON:
    """Parse small frozen evidence without importing Python's regex-backed decoder."""

    def __init__(self, value: bytes) -> None:
        require(type(value) is bytes and 0 < len(value) <= MAX_OWNER_BYTES,
                "bound immutable JSON evidence")
        self.text = value.decode("utf-8", "strict")
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "require a JSON string")
        self.index += 1
        result: list[str] = []
        escapes = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                   "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(result)
            if char != "\\":
                require(ord(char) >= 32 and not 0xD800 <= ord(char) <= 0xDFFF,
                        "reject invalid JSON string content")
                result.append(char)
                continue
            require(self.index < len(self.text), "reject incomplete JSON escape")
            escape = self.text[self.index]
            self.index += 1
            if escape != "u":
                require(escape in escapes, "reject unknown JSON escape")
                result.append(escapes[escape])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(char in "0123456789abcdefABCDEF"
                                             for char in digits),
                    "reject incomplete Unicode escape")
            self.index += 4
            number = int(digits, 16)
            if 0xD800 <= number <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject unpaired high surrogate")
                lower = self.text[self.index + 2:self.index + 6]
                require(len(lower) == 4 and all(char in "0123456789abcdefABCDEF"
                                                for char in lower),
                        "reject malformed low surrogate")
                low = int(lower, 16)
                require(0xDC00 <= low <= 0xDFFF, "reject unpaired high surrogate")
                self.index += 6
                number = 0x10000 + ((number - 0xD800) << 10) + low - 0xDC00
            else:
                require(not 0xDC00 <= number <= 0xDFFF, "reject unpaired low surrogate")
            result.append(chr(number))
        raise FreezeError("reject unterminated JSON string")

    def number(self) -> int:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject an incomplete integer")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index >= len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject a leading-zero integer")
        else:
            require(self.text[self.index] in "123456789", "reject malformed integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                "reject fractional evidence and nonfinite numbers")
        return int(self.text[start:self.index])

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject deeply nested evidence")
        self.whitespace()
        require(self.index < len(self.text), "reject truncated JSON evidence")
        current = self.text[self.index]
        if current == '"':
            return self.string()
        if current == "{":
            self.index += 1
            answer: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return answer
            while True:
                self.whitespace()
                key = self.string()
                require(key not in answer, "reject duplicate JSON keys")
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "reject malformed JSON object")
                self.index += 1
                answer[key] = self.value(depth + 1)
                self.whitespace()
                delimiter = self.text[self.index:self.index + 1]
                require(delimiter in (",", "}"), "reject malformed object separator")
                self.index += 1
                if delimiter == "}":
                    return answer
        if current == "[":
            self.index += 1
            answer: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return answer
            while True:
                answer.append(self.value(depth + 1))
                self.whitespace()
                delimiter = self.text[self.index:self.index + 1]
                require(delimiter in (",", "]"), "reject malformed array separator")
                self.index += 1
                if delimiter == "]":
                    return answer
        if current == "-" or current in "0123456789":
            return self.number()
        for spelling, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(spelling, self.index):
                self.index += len(spelling)
                return value
        raise FreezeError("reject malformed, fractional, or nonfinite JSON")

    def decode(self) -> object:
        answer = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing JSON content")
        return answer


def json_object(value: bytes, label: str) -> dict[str, object]:
    answer = StrictJSON(value).decode()
    require(type(answer) is dict, "require complete JSON object: " + label)
    assert isinstance(answer, dict)
    return answer


class SourceWall:
    """Permanent deny-default source wall with one root-only exclusive output."""

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
        raise FreezeError("combined scoped-Unicode wall rejected " + category)

    def approved_owner(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and not path.endswith((".so", ".gz", ".raw.json", ".jsonl")))

    def temporary(self, flags: object) -> bool:
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
            owner = (self.approved_owner(path) and type(flags) is int and flags & os.O_NOFOLLOW
                     and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                                      | os.O_TRUNC | os.O_APPEND | os.O_DIRECTORY)
                     and not self.temporary(flags))
            parent = (self.apply and self.stage == "ready" and path == ROOT + "/" + PARENT
                      and self.directory_flags(flags))
            child = (self.apply and self.stage == "created" and path == DIRECTORY
                     and self.directory_flags(flags))
            output = (self.apply and self.stage == "child" and path == "lib.rs"
                      and self.output_flags(flags) and not self.output_opened)
            if not any((owner, parent, child, output)):
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
                                   "_interpreters.", "cpython.PyInterpreterState",
                                   "os.exec", "os.spawn"))):
            self.deny("candidate-native-process-clock-final-or-dynamic-code")

    def forbidden(self, category: str):
        def reject(*_args: object, **_keywords: object) -> object:
            self.deny(category)
        return reject

    def install(self) -> None:
        require(not self.installed, "install exactly one irreversible source wall")
        raw_open, raw_read, raw_write = os.open, os.read, os.write
        raw_fstat, raw_close, raw_fsync, raw_mkdir = os.fstat, os.close, os.fsync, os.mkdir

        def guarded_open(path: object, flags: object, mode: int = 0o777,
                         *, dir_fd: object = None) -> int:
            require(type(flags) is int and type(mode) is int, "reject malformed descriptor flags")
            owner = (dir_fd is None and self.approved_owner(path) and flags & os.O_NOFOLLOW
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
            if not any((owner, parent, child, output)):
                self.deny("foreign-owner-directory-or-output-descriptor")
            descriptor = raw_open(path, flags, mode, dir_fd=dir_fd)
            require(type(descriptor) is int and descriptor >= 0
                    and descriptor not in self.owner_fds
                    and descriptor not in (self.parent_fd, self.child_fd, self.output_fd),
                    "reject invalid, reused, or inherited source descriptor")
            if owner:
                self.owner_fds.add(descriptor)
            elif parent:
                self.parent_fd, self.stage = descriptor, "parent"
            elif child:
                self.child_fd, self.stage = descriptor, "child"
            else:
                self.output_fd, self.output_opened = descriptor, True
            return descriptor

        def guarded_read(descriptor: object, count: object) -> bytes:
            if (type(descriptor) is not int or descriptor not in self.owner_fds
                    or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES):
                self.deny("foreign-or-unbounded-source-descriptor-read")
            return raw_read(descriptor, count)

        def guarded_write(descriptor: object, value: object) -> int:
            if not self.apply or descriptor != self.output_fd \
                    or type(value) not in (bytes, memoryview):
                self.deny("unapproved-source-or-inherited-descriptor-write")
            block = bytes(value)
            if not block or block != self.expected[self.written:self.written + len(block)]:
                self.deny("incorrect-or-out-of-order-composed-engine-bytes")
            count = raw_write(descriptor, value)
            require(type(count) is int and 0 < count <= len(block),
                    "reject incomplete exclusive source writes")
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
                        "reject unsynchronized or incomplete composed source")
                self.output_fd = None
            elif descriptor == self.child_fd:
                require(self.child_synced and self.output_fd is None,
                        "synchronize completed child before closing")
                self.child_fd = None
            elif descriptor == self.parent_fd:
                require(self.parent_synced and self.child_fd is None,
                        "synchronize completed parent before closing")
                self.parent_fd = None
            else:
                self.deny("foreign-descriptor-close")
            raw_close(descriptor)

        def guarded_fsync(descriptor: object) -> None:
            if not self.apply or type(descriptor) is not int:
                self.deny("foreign-source-or-inherited-descriptor-fsync")
            if descriptor == self.output_fd:
                require(self.written == len(self.expected) and not self.output_synced,
                        "synchronize exact complete composed source once")
                raw_fsync(descriptor)
                self.output_synced = True
            elif descriptor == self.child_fd:
                require(self.output_synced and self.output_fd is None and not self.child_synced,
                        "synchronize child after complete exclusive source")
                raw_fsync(descriptor)
                self.child_synced = True
            elif descriptor == self.parent_fd:
                require(self.child_synced and self.child_fd is None and not self.parent_synced,
                        "synchronize parent after completed child")
                raw_fsync(descriptor)
                self.parent_synced = True
            else:
                self.deny("foreign-source-or-inherited-descriptor-fsync")

        def guarded_mkdir(path: object, mode: int = 0o777,
                          *, dir_fd: object = None) -> None:
            if not self.apply or self.stage != "parent" or path != DIRECTORY \
                    or mode != 0o700 or dir_fd != self.parent_fd:
                self.deny("unapproved-private-engine-directory")
            raw_mkdir(path, mode, dir_fd=dir_fd)
            self.stage = "created"

        authority = self.apply

        def immutable_audit(event: str, values: tuple[object, ...]) -> None:
            if self.apply is not authority:
                self.deny("forged-root-materialization-authority")
            self.audit(event, values)

        sys.addaudithook(immutable_audit)
        native = sys.modules.get("posix")
        require(native is not None, "authenticate the existing native operating-system module")
        builtins.open = self.forbidden("builtins-open")
        for module in (_io, io):
            module.open = self.forbidden("direct-io-open")
            module.FileIO = self.forbidden("direct-io-fileio")
            if hasattr(module, "open_code"):
                module.open_code = self.forbidden("direct-open-code")
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
            "reject incomplete frozen source owner")
    exact_sha(expected, path)
    absolute = ROOT + "/" + path
    require(wall.installed and wall.approved_owner(absolute),
            "install continuous wall before every exact plaintext owner read")
    descriptor = os.open(absolute, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == size and before.st_nlink == 1
                and before.st_uid == os.geteuid(), "reject exchanged owner: " + role)
        blocks: list[bytes] = []
        remaining = size
        while remaining:
            block = os.read(descriptor, min(65536, remaining))
            require(type(block) is bytes and bool(block), "reject incomplete owner: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject extra owner bytes: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject concurrently changed owner: " + role)
        result = b"".join(blocks)
        require(digest(result) == expected, "reject changed owner bytes: " + role)
        return result
    finally:
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, path: str, expected: str) -> tuple[object, ...]:
    require(path in (SOURCE, PROTOCOL, CONTRACT), "reject unrelated live owner")
    exact_sha(expected, path)
    descriptor = os.open(ROOT + "/" + path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_dev == DEVICE and identity.st_nlink == 1
                and identity.st_uid == os.geteuid() and 0 < identity.st_size <= MAX_OWNER_BYTES,
                "reject exchanged live freeze owner: " + role)
    finally:
        os.close(descriptor)
    return role, path, expected, identity.st_size, identity.st_ino


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    role, path, value, size, inode = row
    return {"role": role, "path": path, "sha256": value, "bytes": size,
            "device": DEVICE, "inode": inode, "mode": "0600", "nlink": 1}


def validate_original(evidence: dict[str, bytes]) -> dict[str, object]:
    ledger = json_object(evidence["original_p0_ledger"], "original P0 ledger")
    failure = json_object(evidence["actual_original_failure"], "actual original failure")
    require(ledger.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and ledger.get("status") == "PASS"
            and ledger.get("original_case_execution_denominator") == 31237
            and ledger.get("original_suite_count") == 13
            and ledger.get("original_named_private_waiver_count") == 13,
            "preserve the exact 31,237-case original correctness ledger")
    oracle = ledger.get("original_oracle")
    gate = ledger.get("phase_gate")
    require(type(oracle) is dict and type(gate) is dict
            and oracle.get("case_execution_denominator") == 31237
            and oracle.get("suite_count") == 13 and gate.get("status") == "PASS"
            and gate.get("final_holdout_authorized") is False
            and gate.get("performance_oracle_authorized") is False,
            "preserve the frozen original phase order without unlocking the final holdout")
    suites = oracle.get("suites")
    require(type(suites) is list and len(suites) == 13
            and sum(item.get("case_execution_count", -1) for item in suites
                    if type(item) is dict) == 31237,
            "retain every frozen original suite and its exact denominator")
    require(failure.get("status") == "PASS" and failure.get("publication_status") == "PASS"
            and failure.get("candidate_status") == "FAIL"
            and failure.get("case_execution_denominator") == 31237
            and failure.get("suite_count") == 13
            and failure.get("semantic_mismatch_count") == 1352
            and failure.get("verified_passing_case_count") == 15877
            and failure.get("holdout") == "NOT OPENED",
            "preserve actual original failure; durable publication is not qualification")
    rows = failure.get("suite_integrity")
    require(type(rows) is list and len(rows) == 13
            and {row.get("suite"): row.get("mismatch_count")
                 for row in rows if type(row) is dict and row.get("mismatch_count")}
            == {"substitution_v2": 240, "shape_v2": 1112},
            "preserve all thirteen suites and the exact 240 + 1,112 known failures")
    return {"original_case_execution_denominator": 31237, "original_suite_count": 13,
            "original_named_private_waiver_count": 13,
            "actual_candidate_status": "FAIL", "actual_semantic_mismatch_count": 1352,
            "actual_substitution_mismatch_count": 240,
            "actual_shape_mismatch_count": 1112,
            "actual_verified_passing_case_count": 15877}


def validate_lineages(evidence: dict[str, bytes]) -> dict[str, object]:
    scoped = json_object(evidence["standalone_contract"], "frozen scoped correction")
    scoped_applied = json_object(evidence["standalone_application"], "scoped application")
    combined_applied = json_object(evidence["combined_application"], "combined application")
    source = scoped.get("source")
    protocol = scoped.get("protocol")
    correction = scoped.get("first_party_source_correction")
    cases = scoped.get("targeted_residual_public_mismatches")
    synthetic = scoped.get("synthetic_differential_semantics")
    require(scoped.get("schema") == "rebar-owned-rust-scoped-unicode-startset-v1-source-freeze"
            and scoped.get("original_case_execution_denominator") == 31237
            and scoped.get("candidate_qualified") is False
            and scoped.get("candidate_correctness") == NOT_MEASURED
            and type(source) is dict and source.get("sha256") == OWNERS[3][2]
            and type(protocol) is dict and protocol.get("sha256") == OWNERS[4][2]
            and type(correction) is dict and type(cases) is dict and type(synthetic) is dict,
            "authenticate the complete previous standalone first-party source freeze")
    standalone = correction.get("standalone_corrected")
    predicted = correction.get("combined_corrected_composition")
    search = correction.get("combined_search_preserved")
    require(type(standalone) is dict and standalone.get("sha256") == SCOPED_SHA256
            and standalone.get("bytes") == 178037
            and type(predicted) is dict and predicted.get("sha256") == CORRECTED_SHA256
            and predicted.get("bytes") == CORRECTED_BYTES
            and type(search) is dict and search.get("sha256") == SEARCH_SHA256
            and correction.get("source_replacement_count") == 1
            and correction.get("mandatory_anchor_accelerator_preserved") is True
            and correction.get("compiler_allocation_fastpath_preserved_when_composed") is True,
            "authenticate the precommitted composed engine and unchanged optimized search")
    rows = cases.get("cases")
    require(cases.get("case_count") == 2 and cases.get("source_case_derivation_only") is True
            and cases.get("raw_case_bytes_opened") == 0
            and type(rows) is list and len(rows) == 2
            and [row.get("case") for row in rows if type(row) is dict]
            == ["rust-public-practice.v2.04362", "rust-public-practice.v2.04371"]
            and all(row.get("expected_span") == [3, 6]
                    and row.get("previous_span") == [4, 6]
                    and row.get("subject") == "café42" and row.get("flags") == A
                    and row.get("pos") == 3 and row.get("endpos") == 6 for row in rows)
            and synthetic.get("bounded_differential_case_count") == 42718
            and synthetic.get("previously_unsound_cases_repaired") == 2843
            and synthetic.get("candidate_executed") is False
            and synthetic.get("external_matcher_imported") is False,
            "preserve both exact public witnesses and the prior independent 42,718-case proof")
    require(scoped_applied.get("status") == "APPLIED"
            and scoped_applied.get("source_sha256") == OWNERS[3][2]
            and scoped_applied.get("protocol_sha256") == OWNERS[4][2]
            and scoped_applied.get("contract_sha256") == OWNERS[5][2]
            and scoped_applied.get("original_case_execution_denominator") == 31237
            and scoped_applied.get("candidate_qualified") is False
            and scoped_applied.get("candidate_correctness") == NOT_MEASURED,
            "authenticate the committed standalone root-only materialization")
    scoped_created = scoped_applied.get("created")
    require(type(scoped_created) is dict and type(scoped_created.get("engine")) is dict
            and scoped_created["engine"].get("sha256") == SCOPED_SHA256
            and scoped_created["engine"].get("inode") == OWNERS[11][4],
            "bind the authenticated standalone source to its actual exclusive inode")
    require(combined_applied.get("status") == "APPLIED"
            and combined_applied.get("original_case_execution_denominator") == 31237
            and combined_applied.get("candidate_qualified") is False
            and combined_applied.get("candidate_correctness") == NOT_MEASURED,
            "authenticate the already materialized optimized first-party combined lineage")
    combined_created = combined_applied.get("created")
    require(type(combined_created) is dict
            and type(combined_created.get("engine")) is dict
            and type(combined_created.get("search")) is dict
            and combined_created["engine"].get("sha256") == COMBINED_SHA256
            and combined_created["engine"].get("inode") == OWNERS[13][4]
            and combined_created["search"].get("sha256") == SEARCH_SHA256
            and combined_created["search"].get("inode") == OWNERS[14][4],
            "bind both optimized first-party sources to their actual exclusive inodes")
    return {"scoped_source_sha256": OWNERS[3][2],
            "scoped_protocol_sha256": OWNERS[4][2],
            "scoped_contract_sha256": OWNERS[5][2],
            "scoped_application_sha256": OWNERS[6][2],
            "combined_application_sha256": OWNERS[7][2],
            "prior_bounded_differential_case_count": 42718,
            "prior_repaired_synthetic_case_count": 2843,
            "public_case_count": 10434,
            "historical_public_mismatch_count": 1145,
            "targeted_residual_public_mismatch_count": 2,
            "targeted_public_case_ids": [row["case"] for row in rows],
            "public_observation_content_open_count": 0,
            "historical_candidate_qualified": False}


def derive_engine(evidence: dict[str, bytes]) -> tuple[bytes, dict[str, object]]:
    canonical_engine = evidence["canonical_engine"]
    standalone = evidence["standalone_corrected_engine"]
    anchor = evidence["mandatory_anchor_engine"]
    combined = evidence["combined_engine"]
    search = evidence["combined_search"]
    require(canonical_engine.count(OLD_GUARD) == 1 and OLD_GUARD not in standalone
            and standalone.count(NEW_GUARD) == 1
            and anchor.count(OLD_GUARD) == 1 and combined.count(OLD_GUARD) == 1
            and NEW_GUARD not in anchor and NEW_GUARD not in combined,
            "locate exactly one precommitted, uncorrected accelerator guard")
    standalone_derived = canonical_engine.replace(OLD_GUARD, NEW_GUARD, 1)
    require(standalone_derived == standalone and digest(standalone_derived) == SCOPED_SHA256
            and standalone_derived.replace(NEW_GUARD, OLD_GUARD, 1) == canonical_engine,
            "independently reproduce the existing standalone materialized correction")
    corrected = combined.replace(OLD_GUARD, NEW_GUARD, 1)
    require(digest(corrected) == CORRECTED_SHA256 and len(corrected) == CORRECTED_BYTES
            and corrected.replace(NEW_GUARD, OLD_GUARD, 1) == combined,
            "reproduce the previously committed optimized composition exactly and reversibly")
    before, after = combined.split(OLD_GUARD)
    require(corrected == before + NEW_GUARD + after
            and len(corrected) - len(combined) == len(NEW_GUARD) - len(OLD_GUARD) == 70,
            "preserve every parser, compiler, virtual-machine, and anchor-search byte")
    markers = (
        b"fn has_scoped_category_prefix(node: &Expr, global_flags: u32) -> bool {",
        b"(*flags ^ global_flags) & (A | L | BYTE) != 0",
        b"let prefix_flags = (*flags & !(A | L | BYTE)) | (global_flags & (A | L | BYTE));",
        b"let start_set = starts.as_ref().map(search::StartSet::new);",
        b"struct Compiler {",
    )
    require(all(marker in canonical_engine and marker in anchor and marker in combined
                and marker in corrected for marker in markers),
            "retain the first-party parser, compiler, VM, scoped detector, and anchor search")
    anchor_marker = b"fn mandatory_anchor_search(root: &Expr) -> Option<search::AnchorPlan> {"
    require(anchor.count(anchor_marker) == combined.count(anchor_marker)
            == corrected.count(anchor_marker) == 1
            and digest(search) == SEARCH_SHA256 and len(search) == 24305,
            "preserve the complete optimized anchor-search implementation unchanged")
    manifest = evidence["cargo_manifest"]
    lock = evidence["cargo_lock"]
    require(manifest.count(b"[package]") == 1 and b"[dependencies]" not in manifest
            and b"regex" not in manifest.lower() and lock.count(b"[[package]]") == 1,
            "preserve one first-party Rust package and zero external dependencies")
    forbidden = (b"extern crate regex", b"use regex::Regex", b"pcre2", b"oniguruma",
                 b"std::process::Command", b"dlopen(", b"PyImport_ImportModule")
    require(not any(marker in NEW_GUARD for marker in forbidden),
            "reject delegation, external regex engines, candidate imports, and processes")
    return corrected, {
        "source_replacement_count": 1,
        "source_delta_bytes": 70,
        "replacement_exactly_reversible": True,
        "standalone_correction_exactly_reproduced": True,
        "canonical_parent": {"path": OWNERS[10][1], "sha256": CANONICAL_SHA256,
                             "bytes": 177967},
        "standalone_corrected": {"path": OWNERS[11][1], "sha256": SCOPED_SHA256,
                                 "bytes": 178037},
        "combined_parent": {"path": OWNERS[13][1], "sha256": COMBINED_SHA256,
                            "bytes": 189423},
        "combined_corrected": {"path": TARGET, "sha256": CORRECTED_SHA256,
                               "bytes": CORRECTED_BYTES,
                               "materialization_status": "NOT MATERIALIZED"},
        "combined_search_preserved": {"path": OWNERS[14][1], "sha256": SEARCH_SHA256,
                                     "bytes": 24305},
        "mandatory_anchor_search_preserved": True,
        "compiler_allocation_fastpath_preserved": True,
        "parser_and_virtual_machine_preserved": True,
        "external_rust_dependency_count": 0,
        "external_matcher_import_count": 0,
    }


def nullable(node: tuple) -> bool:
    kind = node[0]
    if kind in ("cat", "class", "lit"):
        return False
    if kind == "anchor":
        return True
    if kind in ("group", "atomic"):
        return nullable(node[1])
    if kind == "seq":
        return all(nullable(item) for item in node[1])
    if kind == "alt":
        return any(nullable(item) for item in node[1])
    if kind == "repeat":
        return node[2] == 0 or nullable(node[1])
    if kind == "cond":
        return nullable(node[1]) or nullable(node[2])
    raise FreezeError("reject unsupported independent expression")


def scoped_prefix(node: tuple, flags: int) -> bool:
    kind = node[0]
    if kind in ("cat", "class"):
        return (node[2] ^ flags) & (A | L | BYTE) != 0
    if kind in ("group", "atomic", "repeat"):
        return scoped_prefix(node[1], flags)
    if kind == "seq":
        for value in node[1]:
            if scoped_prefix(value, flags):
                return True
            if not nullable(value):
                break
        return False
    if kind == "alt":
        return any(scoped_prefix(value, flags) for value in node[1])
    if kind == "cond":
        return scoped_prefix(node[1], flags) or scoped_prefix(node[2], flags)
    return False


def category(code: str, value: int, flags: int) -> bool:
    char = chr(value)
    ascii_only = bool(flags & (A | BYTE | L))
    if code == "w":
        return (value < 128 if ascii_only else True) and (char.isalnum() or value == 95)
    if code == "d":
        return (value < 128 if ascii_only else True) and char.isdecimal()
    if code == "s":
        return (value < 128 if ascii_only else True) and char.isspace()
    raise FreezeError("reject unsupported independent category")


def matches(node: tuple, values: tuple[int, ...], position: int, end: int) -> tuple[int, ...]:
    kind = node[0]
    if kind == "anchor":
        return (position,)
    if kind == "lit":
        return (position + 1,) if position < end and values[position] == node[1] else ()
    if kind == "cat":
        return (position + 1,) if position < end and category(node[1], values[position], node[2]) else ()
    if kind == "class":
        if position >= end:
            return ()
        result = category(node[1], values[position], node[2])
        return (position + 1,) if result != node[3] else ()
    if kind in ("group", "atomic"):
        return matches(node[1], values, position, end)
    if kind == "seq":
        states = (position,)
        for child in node[1]:
            states = tuple(next_position for current in states
                           for next_position in matches(child, values, current, end))
            if not states:
                break
        return states
    if kind == "alt":
        return tuple(next_position for child in node[1]
                     for next_position in matches(child, values, position, end))
    if kind == "cond":
        return matches(node[1], values, position, end) + matches(node[2], values, position, end)
    if kind == "repeat":
        child, least, most = node[1], node[2], node[3]
        frontier = (position,)
        layers: list[tuple[int, ...]] = [(position,)]
        for _ in range(most):
            frontier = tuple(after for current in frontier
                             for after in matches(child, values, current, end)
                             if after != current)
            if not frontier:
                break
            layers.append(frontier)
        return tuple(value for layer in reversed(layers[least:]) for value in layer)
    raise FreezeError("reject unsupported independent expression")


def first_atom(node: tuple) -> tuple | None:
    kind = node[0]
    if kind in ("cat", "class", "lit"):
        return node
    if kind in ("group", "atomic", "repeat"):
        return first_atom(node[1])
    if kind == "seq":
        for child in node[1]:
            atom = first_atom(child)
            if atom is not None:
                return atom
            if not nullable(child):
                return None
    return None


def search(node: tuple, flags: int, values: tuple[int, ...], first: int, end: int,
           mode: str) -> tuple[int, int] | None:
    leading = first_atom(node)
    unsafe = scoped_prefix(node, flags)
    for position in range(first, end + 1):
        if (mode == "legacy" or mode == "corrected" and not unsafe) \
                and leading is not None and position < end:
            if leading[0] == "cat":
                if not category(leading[1], values[position], flags):
                    continue
            elif leading[0] == "class":
                if category(leading[1], values[position], flags) == leading[3]:
                    continue
            elif leading[0] == "lit" and values[position] != leading[1]:
                continue
        endings = matches(node, values, position, end)
        if endings:
            return position, endings[0]
    return None


def synthetic_semantics() -> dict[str, object]:
    scoped_word = ("cat", "w", U)
    scoped_digit = ("cat", "d", U)
    scoped_space = ("cat", "s", U)
    scoped_class = ("class", "w", U, False)
    scoped_negative = ("class", "w", U, True)
    ascii_word = ("cat", "w", A)
    literal_a = ("lit", ord("a"))
    witness = ("seq", (("group", ("repeat", scoped_word, 1, 8)),
                        ("group", ("repeat", ("cat", "d", A), 0, 8))))
    patterns = (
        ("scoped-unicode-word", scoped_word, A),
        ("scoped-unicode-digit", scoped_digit, A),
        ("scoped-unicode-space", scoped_space, A),
        ("scoped-unicode-class", scoped_class, A),
        ("scoped-unicode-negative-class", scoped_negative, A),
        ("scoped-unicode-group-repeat", witness, A),
        ("scoped-unicode-atomic", ("atomic", scoped_word), A),
        ("scoped-unicode-anchor-prefix", ("seq", (("anchor",), scoped_word)), A),
        ("scoped-unicode-nullable-prefix", ("seq", (("repeat", literal_a, 0, 2), scoped_word)), A),
        ("scoped-unicode-condition", ("cond", scoped_word, scoped_class), A),
        ("scoped-unicode-alternative", ("alt", (scoped_word, literal_a)), A),
        ("global-unicode-scoped-ascii", ascii_word, 0),
        ("ordinary-unicode", ("cat", "w", 0), 0),
        ("ordinary-ascii", ascii_word, A),
        ("ordinary-byte", ("cat", "w", BYTE), BYTE),
        ("locale-byte", ("cat", "w", BYTE | L), BYTE | L),
        ("ordinary-required-anchor", ("seq", (literal_a, scoped_word)), A),
    )
    fixed = ((), tuple(map(ord, "café42")), tuple(map(ord, "é42")),
             tuple(map(ord, "aé2")), tuple(map(ord, "__42")),
             tuple(map(ord, " Ω9")), (0x1F600, ord("a"), ord("2")),
             (0x0662, ord("a"), ord("9")), (0x2003, ord("a"), ord("2")),
             (0, 255, 128, ord("a")), tuple(map(ord, "aaaaaz")),
             tuple(map(ord, "💡é_2")))
    alphabet = (ord("a"), ord("Z"), ord("2"), ord("_"), ord("é"), 0x03A9,
                0x0662, 0x2003, 0x1F600, ord("-"))
    generated: list[tuple[int, ...]] = []
    state = 0x52454241525F5532
    for index in range(64):
        values: list[int] = []
        for _ in range(index % 6 + 1):
            state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            values.append(alphabet[(state >> 33) % len(alphabet)])
        generated.append(tuple(values))
    subjects = fixed + tuple(generated)
    checks = repaired = unchanged = scoped_count = anchor_count = 0
    for family, node, flags in patterns:
        unsafe = scoped_prefix(node, flags)
        if not unsafe and first_atom(node) is not None:
            anchor_count += 1
        for values in subjects:
            for first in range(len(values) + 1):
                for end in range(first, len(values) + 1):
                    expected = search(node, flags, values, first, end, "oracle")
                    previous = search(node, flags, values, first, end, "legacy")
                    corrected = search(node, flags, values, first, end, "corrected")
                    require(corrected == expected,
                            "composed first-party accelerator changed matching: " + family)
                    if previous != expected:
                        require(unsafe, "unrelated first-party accelerator changed semantics")
                        repaired += 1
                    else:
                        unchanged += 1
                    checks += 1
                    scoped_count += int(unsafe)
    subject = tuple(map(ord, "café42"))
    require(search(witness, A, subject, 3, 6, "oracle") == (3, 6)
            and search(witness, A, subject, 3, 6, "legacy") == (4, 6)
            and search(witness, A, subject, 3, 6, "corrected") == (3, 6),
            "reproduce and correct both exact public scoped-Unicode failures")
    require(checks > 10000 and repaired > 0 and unchanged > 0
            and scoped_count > 0 and anchor_count > 0,
            "complete independent bounded cases while retaining unaffected accelerators")
    return {"pattern_family_count": len(patterns), "subject_family_count": len(subjects),
            "bounded_differential_case_count": checks,
            "previously_unsound_cases_repaired": repaired,
            "previously_correct_cases_preserved": unchanged,
            "scoped_prefix_case_count": scoped_count,
            "unaffected_accelerator_family_count": anchor_count,
            "exact_public_witness_expected_span": [3, 6],
            "exact_public_witness_previous_span": [4, 6],
            "exact_public_witness_corrected_span": [3, 6],
            "mandatory_anchor_accelerator_preserved": True,
            "compiler_allocation_fastpath_preserved": True,
            "candidate_executed": False, "external_matcher_imported": False}


def make_contract(source: tuple[object, ...], protocol: tuple[object, ...],
                  original: dict[str, object], lineages: dict[str, object],
                  transformation: dict[str, object], synthetic: dict[str, object]) -> dict[str, object]:
    return {"schema": SCHEMA, "version": 1, "family": "rust", "phase": "CANDIDATES",
            "status": "SOURCE FROZEN; COMPOSED VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
            "source": owner_document(source), "protocol": owner_document(protocol),
            "authenticated_previous_owner_count": len(OWNERS),
            "authenticated_previous_owners": [owner_document(row) for row in OWNERS],
            "authenticated_original_ledger": original,
            "authenticated_first_party_lineages": lineages,
            "first_party_source_composition": transformation,
            "independent_synthetic_differential_semantics": synthetic,
            "root_cause": {"component": "FIRST-PARTY RUST START-SET ACCELERATOR",
                           "global_flags": A, "scoped_lexical_flags": U,
                           "old_guard": OLD_GUARD.decode("utf-8"),
                           "corrected_guard": NEW_GUARD.decode("utf-8"),
                           "existing_scoped_prefix_detector": "has_scoped_category_prefix",
                           "mandatory_anchor_search_preserved": True,
                           "compiler_allocation_fastpath_preserved": True},
            "physical_source_wall": {
                "policy": "CONTINUOUS DENY DEFAULT; PINNED OWNER DESCRIPTORS",
                "installed_before_owner_reads": True,
                "candidate_imports_permitted": 0, "candidate_processes_permitted": 0,
                "native_binary_or_library_opens_permitted": 0,
                "raw_benchmark_file_opens_permitted": 0, "archive_opens_permitted": 0,
                "private_root_opens_permitted": 0, "proposal_opens_permitted": 0,
                "final_case_or_holdout_opens_permitted": 0,
                "proposal_or_holdout_metadata_probes_permitted": 0,
                "clock_or_timer_samples_permitted": 0,
                "source_mode_filesystem_writes_permitted": 0,
                "dynamic_code_compilation_permitted": 0,
                "underlying_posix_aliases_guarded": True,
                "root_output_parent_inode": PARENT_INODE,
                "root_output_directory_mode": "0700",
                "root_output_file_mode": "0600",
                "root_output_file_policy": "O_CREAT|O_EXCL|O_NOFOLLOW",
                "full_linux_o_tmpfile_composite_rejected": True,
                "continuous_wall_remains_active_during_root_publication": True},
            "source_only_effects": {
                "candidate_imports": 0, "candidate_executions": 0,
                "candidate_processes_started": 0, "compiler_processes_started": 0,
                "native_libraries_loaded": 0, "native_binary_files_opened": 0,
                "raw_benchmark_files_opened": 0, "archives_opened": 0,
                "private_roots_opened": 0, "proposal_files_opened": 0,
                "proposal_metadata_probes": 0, "final_holdout_files_opened": 0,
                "final_holdout_metadata_probes": 0, "hidden_cases_opened": 0,
                "clock_samples": 0, "timing_trials_run": 0, "workspace_mutations": 0,
                "candidate_correctness": NOT_MEASURED,
                "candidate_performance": NOT_MEASURED, "candidate_memory": NOT_MEASURED,
                "undefined_behavior": NOT_MEASURED, "qualified_candidate_count": 0,
                "winner_selected": False},
            "original_case_execution_denominator": 31237,
            "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
            "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False,
            "holdout": "NOT OPENED"}


def arguments(values: list[str]) -> tuple[str, dict[str, str], frozenset[str]]:
    require(bool(values), "select exactly one source-freeze action")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject unknown, combined, or missing source-freeze action")
    pins: dict[str, str] = {}
    flags: set[str] = set()
    index = 1
    while index < len(values):
        name = values[index]
        if name in ("--root-authorized", "--frozen-committed-pushed"):
            require(name not in flags, "reject repeated root authorization")
            flags.add(name)
            index += 1
            continue
        require(name in ("--source-sha256", "--protocol-sha256", "--contract-sha256",
                         "--frozen-commit", "--pushed-commit")
                and name not in pins and index + 1 < len(values),
                "reject unknown, duplicated, or missing owner pin")
        pins[name] = exact_sha(values[index + 1], name) if name.endswith("sha256") \
            else exact_commit(values[index + 1], name)
        index += 2
    if mode == "--render-contract":
        require(set(pins) == {"--source-sha256", "--protocol-sha256"} and not flags,
                "rendering requires exactly two independently pinned source owners")
    elif mode in ("--verify-source", "--self-test"):
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
                and not flags, "source gates require exactly three immutable owner pins")
    else:
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256",
                              "--frozen-commit", "--pushed-commit"}
                and flags == {"--root-authorized", "--frozen-committed-pushed"}
                and pins["--frozen-commit"] == pins["--pushed-commit"],
                "only root may apply the exact committed and already pushed freeze")
    return mode, pins, frozenset(flags)


def load_context(wall: SourceWall, mode: str, pins: dict[str, str]) -> dict[str, object]:
    source = live_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol = live_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source)
    read_owner(wall, protocol)
    contract = None if mode == "--render-contract" else live_owner(
        wall, "contract", CONTRACT, pins["--contract-sha256"])
    evidence = {row[0]: read_owner(wall, row) for row in OWNERS}
    original = validate_original(evidence)
    lineages = validate_lineages(evidence)
    corrected, transformation = derive_engine(evidence)
    synthetic = synthetic_semantics()
    expected = make_contract(source, protocol, original, lineages, transformation, synthetic)
    if contract is not None:
        complete = read_owner(wall, contract)
        require(complete == document(expected)
                and json_object(complete, "complete composition contract") == expected,
                "reject omitted, reordered, changed, or incomplete frozen obligations")
    require(not wall.owner_fds and wall.parent_fd is None and wall.child_fd is None
            and wall.output_fd is None and not wall.output_opened,
            "close all owned descriptors without opening a proposal, native object, or final case")
    clean_imports()
    return {"contract": expected, "corrected": corrected, "original": original,
            "lineages": lineages, "synthetic": synthetic}


def expect_rejected(wall: SourceWall, name: str, callback) -> str:
    before = sum(wall.blocked.values())
    try:
        callback()
    except (FreezeError, OSError, TypeError, ValueError, UnicodeError, IndexError):
        require(sum(wall.blocked.values()) > before,
                "hostile control did not reach the source wall: " + name)
        return name
    raise FreezeError("hostile source-only control escaped: " + name)


def hostile_self_test(wall: SourceWall, state: dict[str, object]) -> dict[str, object]:
    own = ROOT + "/" + SOURCE
    native = sys.modules["posix"]

    def forged_authority() -> None:
        previous = wall.apply
        wall.apply = not previous
        try:
            sys.audit("os.exec", "/bin/true", (), None)
        finally:
            wall.apply = previous

    controls = [
        expect_rejected(wall, "builtins-open", lambda: builtins.open(own, "rb")),
        expect_rejected(wall, "io-open", lambda: io.open(own, "rb")),
        expect_rejected(wall, "_io-open", lambda: _io.open(own, "rb")),
        expect_rejected(wall, "missing-nofollow", lambda: os.open(own, os.O_RDONLY)),
        expect_rejected(wall, "owner-write", lambda: os.open(own, os.O_WRONLY)),
        expect_rejected(wall, "owner-path-alias", lambda: os.open(
            ROOT + "/tools/../" + SOURCE, os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "external-package-owner", lambda: os.open(
            ROOT + "/candidates/rust/Cargo.lock.backup", os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "raw-public-observation", lambda: os.open(
            ROOT + "/experiments/rust_native_architecture_public_v2/"
            "v26-anchor-public-run-001/public-10434-correctness.raw.json",
            os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "native-binary", lambda: os.open(
            ROOT + "/candidates/_rust_engine.so", os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "compressed-archive", lambda: os.open(
            ROOT + "/oracle/phase2/evidence/private.json.gz", os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "final-cases", lambda: os.open(
            ROOT + "/oracle/phase3/final-held-out-cases.json", os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "proposal-or-holdout-metadata", lambda: os.lstat(
            ROOT + "/oracle/phase3/final-held-out-cases.json")),
        expect_rejected(wall, "private-build-root", lambda: os.open(
            "/tmp/rebar-private-build", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "variants-parent-before-apply", lambda: os.open(
            ROOT + "/" + PARENT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "linux-composite-tmpfile", lambda: os.open(
            ROOT + "/" + PARENT, os.O_TMPFILE | os.O_RDWR | os.O_NOFOLLOW)),
        expect_rejected(wall, "target-before-apply", lambda: os.open(
            ROOT + "/" + TARGET, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        expect_rejected(wall, "inherited-read", lambda: os.read(0, 1)),
        expect_rejected(wall, "inherited-write", lambda: os.write(1, b"reject")),
        expect_rejected(wall, "inherited-fstat", lambda: os.fstat(0)),
        expect_rejected(wall, "inherited-fsync", lambda: os.fsync(1)),
        expect_rejected(wall, "inherited-close", lambda: os.close(0)),
        expect_rejected(wall, "native-posix-read", lambda: native.read(0, 1)),
        expect_rejected(wall, "native-posix-write", lambda: native.write(1, b"reject")),
        expect_rejected(wall, "native-posix-metadata", lambda: native.fstat(0)),
        expect_rejected(wall, "candidate-process", lambda: os.system("true")),
        expect_rejected(wall, "dynamic-compilation", lambda: compile(b"1", "foreign.py", "exec")),
        expect_rejected(wall, "dynamic-execution", lambda: exec("1")),
        expect_rejected(wall, "external-matcher-import", lambda: __import__("re")),
        expect_rejected(wall, "native-loader-import", lambda: __import__("ctypes")),
        expect_rejected(wall, "seconds-clock", lambda: time.time()),
        expect_rejected(wall, "nanosecond-clock", lambda: time.perf_counter_ns()),
        expect_rejected(wall, "forged-root-authority", forged_authority),
    ]
    for name in ("dup", "pread", "pwrite", "readv", "writev", "sendfile", "stat",
                 "listdir", "truncate", "execv", "spawnv", "kill", "chdir"):
        if hasattr(os, name):
            function = getattr(os, name)
            controls.append(expect_rejected(wall, "descriptor-alias-" + name,
                                            lambda actual=function: actual()))
    invalid = (b'{"duplicate":1,"duplicate":2}', b'{"zero":01}', b'{"nan":NaN}',
               b'{"fraction":1.5}', b'{"infinite":1e999}', b'{"trailing":1}{}',
               b'{"surrogate":"\\ud800"}', b'{"escape":"\\q"}', b"[]")
    rejected = 0
    for value in invalid:
        try:
            json_object(value, "hostile JSON")
        except (FreezeError, UnicodeError, ValueError, IndexError):
            rejected += 1
        else:
            raise FreezeError("malformed or nonfinite JSON escaped")
    require(len(controls) >= 40 and rejected == len(invalid)
            and state["contract"]["source_only_effects"]["workspace_mutations"] == 0,
            "complete deny-default physical, evidence, and filesystem controls")
    clean_imports()
    return {"physical_hostile_control_count": len(controls),
            "physical_hostile_controls": controls,
            "malformed_evidence_control_count": rejected,
            "physically_blocked_categories": dict(wall.blocked),
            "underlying_posix_aliases_guarded": True,
            "proposal_content_open_count": 0, "proposal_metadata_probe_count": 0,
            "raw_public_observation_content_open_count": 0,
            "final_holdout_content_open_count": 0,
            "final_holdout_metadata_probe_count": 0,
            "candidate_process_count": 0, "clock_sample_count": 0,
            "wall_remains_installed": wall.installed}


def apply_root_only(wall: SourceWall, state: dict[str, object],
                    pins: dict[str, str], flags: frozenset[str]) -> dict[str, object]:
    corrected = state["corrected"]
    require(wall.apply and flags == {"--root-authorized", "--frozen-committed-pushed"}
            and pins["--frozen-commit"] == pins["--pushed-commit"]
            and pins["--source-sha256"] == state["contract"]["source"]["sha256"]
            and pins["--protocol-sha256"] == state["contract"]["protocol"]["sha256"]
            and digest(corrected) == CORRECTED_SHA256 and len(corrected) == CORRECTED_BYTES
            and not wall.owner_fds and wall.stage == "source",
            "require the complete committed and pushed root freeze before mutation")
    wall.expected, wall.stage = corrected, "ready"
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open(ROOT + "/" + PARENT, directory_flags)
    parent_identity = os.fstat(parent)
    require(stat.S_ISDIR(parent_identity.st_mode)
            and stat.S_IMODE(parent_identity.st_mode) == 0o700
            and parent_identity.st_dev == DEVICE and parent_identity.st_ino == PARENT_INODE
            and parent_identity.st_uid == os.geteuid(),
            "authenticate the exact existing first-party variants parent")
    os.mkdir(DIRECTORY, 0o700, dir_fd=parent)
    child = os.open(DIRECTORY, directory_flags, dir_fd=parent)
    child_identity = os.fstat(child)
    require(stat.S_ISDIR(child_identity.st_mode)
            and stat.S_IMODE(child_identity.st_mode) == 0o700
            and child_identity.st_dev == DEVICE and child_identity.st_uid == os.geteuid(),
            "authenticate exactly one new private combined-engine directory")
    flags_output = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    output = os.open("lib.rs", flags_output, 0o600, dir_fd=child)
    initial = os.fstat(output)
    require(stat.S_ISREG(initial.st_mode) and stat.S_IMODE(initial.st_mode) == 0o600
            and initial.st_dev == DEVICE and initial.st_uid == os.geteuid()
            and initial.st_nlink == 1 and initial.st_size == 0,
            "require a fresh exclusive no-follow first-party combined source")
    while wall.written < len(corrected):
        os.write(output, memoryview(corrected)[wall.written:])
    os.fsync(output)
    complete = os.fstat(output)
    require(complete.st_dev == initial.st_dev and complete.st_ino == initial.st_ino
            and complete.st_size == CORRECTED_BYTES and complete.st_nlink == 1
            and stat.S_IMODE(complete.st_mode) == 0o600,
            "reject incomplete, exchanged, linked, or permission-altered composed engine")
    os.close(output)
    os.fsync(child)
    os.close(child)
    os.fsync(parent)
    os.close(parent)
    require(wall.output_opened and wall.output_synced and wall.child_synced and wall.parent_synced
            and wall.output_fd is None and wall.child_fd is None and wall.parent_fd is None,
            "fully synchronize the exact exclusive source, its private child, and parent")
    return {"schema": SCHEMA + "-application", "status": "APPLIED", "mode": "apply",
            "source_sha256": pins["--source-sha256"],
            "protocol_sha256": pins["--protocol-sha256"],
            "contract_sha256": pins["--contract-sha256"],
            "frozen_pushed_commit": pins["--pushed-commit"],
            "created": {
                "directory": {"path": PARENT + "/" + DIRECTORY,
                              "device": child_identity.st_dev, "inode": child_identity.st_ino,
                              "mode": "0700", "fsync_completed": True},
                "engine": {"path": TARGET, "sha256": CORRECTED_SHA256,
                           "bytes": CORRECTED_BYTES, "device": complete.st_dev,
                           "inode": complete.st_ino, "mode": "0600", "nlink": 1,
                           "exclusive_no_follow": True, "fsync_completed": True}},
            "workspace_mutation_count": 2, "source_output_fsync_count": 1,
            "directory_fsync_count": 2, "continuous_source_wall_active": True,
            "targeted_public_mismatch_case_count": 2,
            "bounded_synthetic_case_count":
                state["synthetic"]["bounded_differential_case_count"],
            "mandatory_anchor_search_preserved": True,
            "compiler_allocation_fastpath_preserved": True,
            "external_rust_dependency_count": 0,
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "raw_benchmark_files_opened": 0,
            "archives_opened": 0, "proposal_content_open_count": 0,
            "proposal_metadata_probe_count": 0,
            "final_holdout_content_open_count": 0,
            "final_holdout_metadata_probe_count": 0, "clock_samples": 0,
            "original_case_execution_denominator": 31237,
            "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
            "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False}


def main() -> int:
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and sys.flags.no_site == 1,
            "use exact pinned CPython 3.14.6 with -I -B -S")
    clean_imports()
    mode, pins, flags = arguments(list(sys.argv[1:]))
    wall = SourceWall(mode == "--apply")
    wall.install()
    state = load_context(wall, mode, pins)
    if mode == "--render-contract":
        result = state["contract"]
    elif mode == "--apply":
        result = apply_root_only(wall, state, pins, flags)
    else:
        result = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                  "mode": mode[2:], "source_sha256": pins["--source-sha256"],
                  "protocol_sha256": pins["--protocol-sha256"],
                  "contract_sha256": pins["--contract-sha256"],
                  "authenticated_previous_owner_count": len(OWNERS),
                  "original_case_execution_denominator": 31237,
                  "historical_original_semantic_mismatch_count": 1352,
                  "historical_public_mismatch_count": 1145,
                  "targeted_residual_public_mismatch_count": 2,
                  "targeted_public_case_ids":
                      state["lineages"]["targeted_public_case_ids"],
                  "derived_combined_engine_sha256": CORRECTED_SHA256,
                  "derived_combined_engine_bytes": CORRECTED_BYTES,
                  "unchanged_combined_search_sha256": SEARCH_SHA256,
                  "bounded_synthetic_case_count":
                      state["synthetic"]["bounded_differential_case_count"],
                  "previously_unsound_synthetic_cases_repaired":
                      state["synthetic"]["previously_unsound_cases_repaired"],
                  "mandatory_anchor_search_preserved": True,
                  "compiler_allocation_fastpath_preserved": True,
                  "external_rust_dependency_count": 0,
                  "source_mutations": 0, "candidate_imports": 0,
                  "candidate_processes_started": 0, "native_libraries_loaded": 0,
                  "raw_benchmark_files_opened": 0, "archives_opened": 0,
                  "private_roots_opened": 0, "proposal_content_open_count": 0,
                  "proposal_metadata_probe_count": 0,
                  "final_holdout_content_open_count": 0,
                  "final_holdout_metadata_probe_count": 0, "clock_samples": 0,
                  "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
                  "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
                  "candidate_qualified": False, "winner_selected": False}
        if mode == "--self-test":
            result["hostile"] = hostile_self_test(wall, state)
    sys.stdout.buffer.write(document(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError, IndexError,
            KeyError, AttributeError) as error:
        sys.stderr.write("combined scoped-Unicode source freeze rejected: " + str(error) + "\n")
        raise SystemExit(2)
