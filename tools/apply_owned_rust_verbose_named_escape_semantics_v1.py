#!/usr/bin/env python3
"""Freeze a flag-aware, first-party Rust adapter named-escape correction.

Self-test and source verification install a deny-default physical wall before
reading anything.  Verification authenticates only the three frozen owners, the
latest immutable V26/V27 public receipts, and the original immutable V25 ledger.
The canonical adapter is never opened except by separately authorized root-only
materialization after the identical frozen commit has been pushed.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("source-only named-escape freeze must not import a matcher")

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
SCHEMA = "rebar-owned-rust-verbose-named-escape-semantics-v1-source-freeze"
SOURCE = "tools/apply_owned_rust_verbose_named_escape_semantics_v1.py"
PROTOCOL = "oracle/phase2/RUST-VERBOSE-NAMED-ESCAPE-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/rust-verbose-named-escape-semantics-v1.json"
INPUT = "candidates/rust_candidate.py"
INPUT_SHA256 = "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"
INPUT_BYTES = 31151
INPUT_INODE = 428100
TARGET_DIRECTORY = "candidates/rust/variants/verbose_named_escape_semantics_v1"
TARGET = TARGET_DIRECTORY + "/rust_candidate.py"
OUTPUT_SHA256 = "c1d150d467d5732eab4cc589f7e18583e59892592fb48d7d6f37700c00dccda0"
OUTPUT_BYTES = 33256
VERBOSE = 64
PUBLIC_CASE_COUNT = 10434
PUBLIC_MISMATCH_COUNT = 1145
TARGETED_MISMATCH_COUNT = 324
COMMENT_ONLY_MISMATCH_COUNT = 297
SCANNER_OVERLAP_COUNT = 15
SUBSTITUTION_OVERLAP_COUNT = 12
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 200_000
MAX_JSON_DEPTH = 80
FROZEN_PUBLIC_COMMIT = "9095467be5523a71e51dee86fcc25df65a8eb3a2"

PUBLIC_RECEIPTS = (
    (
        "v26",
        "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-"
        "v26-anchor-public-run-001-publication-receipt.json",
        "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80",
        40906,
        525333,
        "v26-anchor-public-run-001",
    ),
    (
        "v27",
        "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-"
        "v27-compiler-public-run-001-publication-receipt.json",
        "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449",
        68330,
        525426,
        "v27-compiler-public-run-001",
    ),
)
LEDGER = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-"
    "failures-publication-receipt.json"
)
LEDGER_SHA256 = "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59"
LEDGER_BYTES = 11832
LEDGER_INODE = 524846

ORIGINAL_COMPILE = (
    b'        named = _named_escapes(pattern) if isinstance(pattern, str) '
    b'and "\\\\N" in pattern else ()\n'
)
CORRECTED_COMPILE = (
    b'        named = _named_escapes(pattern, flags) if isinstance(pattern, str) '
    b'and "\\\\N" in pattern else ()\n'
)
ORIGINAL_SCANNER_CALL = b"                _named_escapes(pattern)\n"
CORRECTED_SCANNER_CALL = b"                _named_escapes(pattern, flags)\n"

ORIGINAL_NAMED_SCANNER = b'''def _named_escapes(pattern):
    if isinstance(pattern, bytes):
        return []
    found = []
    index = 0
    while index < len(pattern):
        if pattern[index] != "\\\\":
            index += 1
            continue
        slash = index
        index += 1
        if pattern[index:index + 2] != "N{":
            index += bool(pattern[index:index + 1])
            continue
        close = pattern.find("}", index + 2)
        if close == index + 2 or (close < 0 and index + 2 == len(pattern)):
            raise PatternError("missing character name", pattern, slash + 3)
        if close < 0:
            raise PatternError("missing }, unterminated name", pattern, slash + 3)
        name = pattern[index + 2:close]
        try:
            value = unicodedata.lookup(name)
        except KeyError:
            raise PatternError(f"undefined character name {name!r}", pattern, slash) from None
        if len(value) != 1:
            raise PatternError(f"undefined character name {name!r}", pattern, slash)
        found.append((slash, ord(value)))
        index = close + 1
    return found
'''

CORRECTED_NAMED_SCANNER = b'''def _named_escapes(pattern, flags=0):
    if isinstance(pattern, bytes):
        return []
    found = []
    index = 0
    verbose = bool(flags & int(VERBOSE))
    scopes = []
    in_class = False
    class_start = -1
    while index < len(pattern):
        char = pattern[index]
        if char == "\\\\":
            slash = index
            index += 1
            if pattern[index:index + 2] != "N{":
                index += bool(pattern[index:index + 1])
                continue
            close = pattern.find("}", index + 2)
            if close == index + 2 or (close < 0 and index + 2 == len(pattern)):
                raise PatternError("missing character name", pattern, slash + 3)
            if close < 0:
                raise PatternError("missing }, unterminated name", pattern, slash + 3)
            name = pattern[index + 2:close]
            try:
                value = unicodedata.lookup(name)
            except KeyError:
                raise PatternError(f"undefined character name {name!r}", pattern, slash) from None
            if len(value) != 1:
                raise PatternError(f"undefined character name {name!r}", pattern, slash)
            found.append((slash, ord(value)))
            index = close + 1
            continue
        if in_class:
            if char == "]" and index > class_start:
                in_class = False
            index += 1
            continue
        if verbose and char == "#":
            newline = pattern.find("\\n", index + 1)
            if newline < 0:
                break
            index = newline + 1
            continue
        if char == "[":
            in_class = True
            class_start = index + 1
            if pattern[class_start:class_start + 1] == "^":
                class_start += 1
            index += 1
            continue
        if char == "(":
            if pattern[index:index + 3] == "(?#":
                close = pattern.find(")", index + 3)
                index = len(pattern) if close < 0 else close + 1
                continue
            if pattern[index:index + 2] == "(?":
                marker = index + 2
                while (marker < len(pattern)
                       and pattern[marker] in "aiLmsux-"):
                    marker += 1
                if (marker > index + 2
                        and pattern[marker:marker + 1] in (":", ")")):
                    enabled, _, disabled = pattern[index + 2:marker].partition("-")
                    scoped_verbose = verbose
                    if "x" in enabled:
                        scoped_verbose = True
                    if "x" in disabled:
                        scoped_verbose = False
                    if pattern[marker] == ")":
                        verbose = scoped_verbose
                        index = marker + 1
                        continue
                    scopes.append(verbose)
                    verbose = scoped_verbose
                    index = marker + 1
                    continue
            scopes.append(verbose)
            index += 1
            continue
        if char == ")" and scopes:
            verbose = scopes.pop()
        index += 1
    return found
'''

PRESERVED_ANCHORS = (
    (b"from candidates import _rust_bridge\n", 1),
    (b"import unicodedata\n", 1),
    (b"class RegexFlag(enum.IntFlag):\n", 1),
    (b"    VERBOSE = X = 64\n", 1),
    (b"class _Native:\n", 1),
    (b"    def compile(self, pattern, flags):\n", 1),
    (b"    def compile_scanner(self, patterns, flags):\n", 1),
    (b"compiled = self.native_compile(pattern, flags, positions, values)", 1),
    (b"compiled = _rust_bridge.compile_scanner(\n", 1),
    (b"def _warn_ambiguous(pattern):\n", 1),
    (b"def _compile(pattern, flags):\n", 1),
    (b"_cache_pattern(key, result)", 1),
)


class FreezeError(Exception):
    """Reject drift, unsafe effects, unauthorized evidence, or non-exact output."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete genuine bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "canonical JSON requires genuine text")
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
    raise FreezeError("reject unsupported canonical JSON value")


class StrictJSON:
    """Bounded duplicate-rejecting JSON reader, including finite receipt floats."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require complete bounded authenticated JSON bytes")
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
        floating = False
        if self.text[self.index:self.index + 1] == ".":
            floating = True
            self.index += 1
            first = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > first, "reject incomplete JSON fraction")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            floating = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            first = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > first, "reject incomplete JSON exponent")
        literal = self.text[start:self.index]
        require(len(literal) <= 128, "reject oversized authenticated JSON number")
        if not floating:
            return int(literal)
        number = float(literal)
        require(number == number and number not in (float("inf"), float("-inf")),
                "reject nonfinite authenticated JSON number")
        return number

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
                        "require authenticated JSON object colon")
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
            result_list: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result_list
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON array")
                result_list.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result_list
                require(separator == ",", "reject malformed JSON array")
        if char == "-" or char in "0123456789":
            return self.number()
        for literal, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return value
        raise FreezeError("reject malformed or nonfinite authenticated JSON")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing evidence bytes")
        return result


def no_matching_imports() -> None:
    forbidden = (
        "re", "_sre", "regex", "_regex", "re2", "google_re2", "rure", "pcre",
        "pcre2", "oniguruma", "hyperscan", "ctypes", "candidates", "rebar",
        "subprocess", "socket", "threading", "multiprocessing", "concurrent",
        "importlib", "zipfile", "gzip", "tarfile", "pathlib",
    )
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matcher, external package, candidate, archive, process, or loader")


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.dont_write_bytecode is True
            and sys.executable == PYTHON
            and __file__ == ROOT + "/" + SOURCE,
            "require the isolated -I -B -S pinned CPython 3.14.6 frozen source")


class SourceWall:
    """Deny-default descriptor wall with exactly one root-authorized output."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT, LEDGER)
                                + tuple(item[1] for item in PUBLIC_RECEIPTS))
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
        raise FreezeError("source-only named-escape wall rejected " + reason)

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed-candidate-native-archive-holdout-or-write-open")
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
        info = self.live.get(parent)
        require(info is not None and info[1] == "directory",
                "reject foreign parent directory descriptor")
        relative = component if not info[0] else info[0] + "/" + component
        permitted = (any(path.startswith(relative + "/") for path in self.allowed)
                     or self.apply and (relative == TARGET_DIRECTORY
                                        or TARGET_DIRECTORY.startswith(relative + "/")))
        require(permitted and not relative.startswith((".git/", ".agents/", ".codex/")),
                "reject unowned hidden, final, candidate, archive, or private root")
        descriptor = self.native_ticket_open(component, self.directory_flags(),
                                             dir_fd=parent)
        metadata = self.native_fstat(descriptor)
        require(stat.S_ISDIR(metadata.st_mode) and metadata.st_dev == DEVICE,
                "reject substituted or symlink owner directory: " + relative)
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
                "reject candidate, native, proposal, archive, final, or foreign owner")
        require(self.root is not None, "open isolated workspace root first")
        components = relative.split("/")
        require(all(self.checked_component(item) for item in components),
                "reject invalid owner path component")
        descriptor = self.root
        opened: list[int] = []
        try:
            for component in components[:-1]:
                descriptor = self.child_directory(descriptor, component)
                opened.append(descriptor)
            return descriptor, opened, components[-1]
        except BaseException:
            for item in reversed(opened):
                self.close(item)
            raise

    def read(self, relative: str, count: int | None, inode: int | None,
             expected_sha256: str) -> bytes:
        require(self.installed and relative in self.allowed,
                "candidate source is forbidden before root-only materialization")
        require(count is None or type(count) is int and 0 < count <= MAX_OWNER_BYTES,
                "reject oversized frozen owner")
        parent, opened, filename = self.parent(relative)
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
                    "reject substituted complete immutable owner: " + relative)
            chunks: list[bytes] = []
            remaining = before.st_size
            while remaining:
                chunk = self.native_read(descriptor, min(remaining, 65536))
                require(type(chunk) is bytes and bool(chunk),
                        "reject truncated immutable owner: " + relative)
                chunks.append(chunk)
                remaining -= len(chunk)
            require(self.native_read(descriptor, 1) == b"",
                    "reject extra immutable owner bytes: " + relative)
            after = self.native_fstat(descriptor)
            require((after.st_dev, after.st_ino, after.st_size, after.st_mode,
                     after.st_mtime_ns, after.st_ctime_ns)
                    == (before.st_dev, before.st_ino, before.st_size, before.st_mode,
                        before.st_mtime_ns, before.st_ctime_ns),
                    "reject concurrently mutated immutable owner: " + relative)
            result = b"".join(chunks)
            require(digest(result) == checked_sha(expected_sha256, relative),
                    "reject complete frozen owner digest: " + relative)
            if relative == INPUT:
                require(self.apply and self.source_reads == 0,
                        "read canonical adapter exactly once only in root apply")
                self.source_reads += 1
            else:
                self.public_reads += 1
            return result
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for item in reversed(opened):
                self.close(item)

    def make_target_directory(self) -> int:
        require(self.apply and not self.directory_created and self.root is not None,
                "require explicit one-time root-only variant directory creation")
        descriptor = self.root
        opened: list[int] = []
        components = TARGET_DIRECTORY.split("/")
        try:
            for component in components[:-1]:
                descriptor = self.child_directory(descriptor, component)
                opened.append(descriptor)
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
            for item in reversed(opened):
                self.close(item)

    def materialize(self, corrected: bytes) -> None:
        require(self.apply and self.source_reads == 1 and not self.output_opened,
                "authorize exactly one immutable corrected Python adapter")
        require(type(corrected) is bytes and len(corrected) == OUTPUT_BYTES
                and digest(corrected) == OUTPUT_SHA256,
                "reject non-frozen adapter before workspace mutation")
        parent = self.make_target_directory()
        descriptor: int | None = None
        try:
            flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
            descriptor = self.native_ticket_open("rust_candidate.py", flags, 0o600,
                                                 dir_fd=parent)
            self.live[descriptor] = (TARGET, "output")
            self.output_opened = True
            self.workspace_mutations += 1
            position = 0
            while position < len(corrected):
                written = self.native_write(descriptor, corrected[position:])
                require(type(written) is int and written > 0,
                        "reject incomplete exclusive adapter write")
                position += written
            metadata = self.native_fstat(descriptor)
            require(stat.S_ISREG(metadata.st_mode)
                    and stat.S_IMODE(metadata.st_mode) == 0o600
                    and metadata.st_dev == DEVICE and metadata.st_size == OUTPUT_BYTES
                    and metadata.st_nlink == 1 and metadata.st_uid == os.geteuid(),
                    "reject substituted immutable corrected adapter")
            self.native_fsync(descriptor)
            self.close(descriptor)
            descriptor = None
            self.native_fsync(parent)
            readback = self.native_ticket_open("rust_candidate.py", self.file_flags(),
                                              dir_fd=parent)
            try:
                self.live[readback] = (TARGET, "readback")
                chunks: list[bytes] = []
                remaining = OUTPUT_BYTES
                while remaining:
                    chunk = self.native_read(readback, min(remaining, 65536))
                    require(bool(chunk), "reject incomplete durable adapter readback")
                    chunks.append(chunk)
                    remaining -= len(chunk)
                require(self.native_read(readback, 1) == b""
                        and digest(b"".join(chunks)) == OUTPUT_SHA256,
                        "reject complete durable corrected adapter digest")
            finally:
                self.close(readback)
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            self.close(parent)

    def install(self) -> None:
        require(not self.installed, "install physical source wall exactly once")
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
    require(type(source) is bytes, "transform only complete owned adapter bytes")
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA256,
                "reject unauthenticated complete canonical Rust adapter")
    require(source.count(ORIGINAL_COMPILE) == 1
            and source.count(ORIGINAL_SCANNER_CALL) == 1
            and source.count(ORIGINAL_NAMED_SCANNER) == 1,
            "require exactly one compile call, scanner call, and lexical helper")
    first = source.index(ORIGINAL_COMPILE)
    second = source.index(ORIGINAL_SCANNER_CALL)
    third = source.index(ORIGINAL_NAMED_SCANNER)
    require(first < second < third,
            "reject reordered compile, scanner, or named-escape owned anchors")
    for anchor, count in PRESERVED_ANCHORS:
        require(source.count(anchor) == count,
                "reject missing or duplicated first-party adapter anchor")
    result = source.replace(ORIGINAL_COMPILE, CORRECTED_COMPILE, 1)
    result = result.replace(ORIGINAL_SCANNER_CALL, CORRECTED_SCANNER_CALL, 1)
    result = result.replace(ORIGINAL_NAMED_SCANNER, CORRECTED_NAMED_SCANNER, 1)
    require(result.count(CORRECTED_COMPILE) == 1
            and result.count(CORRECTED_SCANNER_CALL) == 1
            and result.count(CORRECTED_NAMED_SCANNER) == 1,
            "require exactly three reversible owned Python correction sites")
    restored = result.replace(CORRECTED_NAMED_SCANNER, ORIGINAL_NAMED_SCANNER, 1)
    restored = restored.replace(CORRECTED_SCANNER_CALL, ORIGINAL_SCANNER_CALL, 1)
    restored = restored.replace(CORRECTED_COMPILE, ORIGINAL_COMPILE, 1)
    require(restored == source,
            "require byte-exact reversible edits only at the three owned sites")
    delta = (len(CORRECTED_COMPILE) - len(ORIGINAL_COMPILE)
             + len(CORRECTED_SCANNER_CALL) - len(ORIGINAL_SCANNER_CALL)
             + len(CORRECTED_NAMED_SCANNER) - len(ORIGINAL_NAMED_SCANNER))
    require(len(result) == len(source) + delta,
            "reject additional bytes outside the frozen lexical correction")
    for anchor, count in PRESERVED_ANCHORS:
        require(result.count(anchor) == count,
                "preserve native bridge, public flags, warning, cache, and engine")
    require(result.count(b"unicodedata.lookup(name)")
            == source.count(b"unicodedata.lookup(name)") == 1,
            "preserve the original first-party Unicode lookup and error behavior")
    for forbidden in (b"import re\n", b"import regex\n", b"from re import ",
                      b"from regex import ", b"import subprocess\n",
                      b"import ctypes\n"):
        require(result.count(forbidden) == source.count(forbidden) == 0,
                "reject production stdlib matching, external engine, or native loader")
    if exact:
        require(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
                "reject drift in exact frozen immutable adapter successor")
    return result


def synthetic_source() -> bytes:
    return b"".join((
        b"from candidates import _rust_bridge\n",
        b"import unicodedata\n",
        b"class RegexFlag(enum.IntFlag):\n",
        b"    VERBOSE = X = 64\n",
        b"class _Native:\n",
        b"    def compile(self, pattern, flags):\n",
        ORIGINAL_COMPILE,
        b"        compiled = self.native_compile(pattern, flags, positions, values)\n",
        b"    def compile_scanner(self, patterns, flags):\n",
        ORIGINAL_SCANNER_CALL,
        b"        compiled = _rust_bridge.compile_scanner(\n",
        ORIGINAL_NAMED_SCANNER,
        b"def _warn_ambiguous(pattern):\n",
        b"def _compile(pattern, flags):\n",
        b"    return _cache_pattern(key, result)\n",
    ))


class WitnessPatternError(Exception):
    def __init__(self, message: str, pattern: str, position: int) -> None:
        super().__init__(message)
        self.msg = message
        self.pattern = pattern
        self.pos = position


KNOWN_NAMES = {
    "LATIN SMALL LETTER A": "a",
    "LATIN CAPITAL LETTER A": "A",
    "BLACK HEART SUIT": "♥",
    "MULTI CODEPOINT": "ab",
}


def witness_named_escapes(pattern: str | bytes, flags: int = 0,
                          lookups: list[str] | None = None) -> list[tuple[int, int]]:
    """Independent source-only lexical witness; never imports or calls a matcher."""
    if isinstance(pattern, bytes):
        return []
    found: list[tuple[int, int]] = []
    index = 0
    verbose = bool(flags & VERBOSE)
    scopes: list[bool] = []
    in_class = False
    class_start = -1
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            slash = index
            index += 1
            if pattern[index:index + 2] != "N{":
                index += bool(pattern[index:index + 1])
                continue
            close = pattern.find("}", index + 2)
            if close == index + 2 or (close < 0 and index + 2 == len(pattern)):
                raise WitnessPatternError("missing character name", pattern, slash + 3)
            if close < 0:
                raise WitnessPatternError("missing }, unterminated name", pattern,
                                          slash + 3)
            name = pattern[index + 2:close]
            if lookups is not None:
                lookups.append(name)
            value = KNOWN_NAMES.get(name)
            if value is None or len(value) != 1:
                raise WitnessPatternError(f"undefined character name {name!r}",
                                          pattern, slash)
            found.append((slash, ord(value)))
            index = close + 1
            continue
        if in_class:
            if char == "]" and index > class_start:
                in_class = False
            index += 1
            continue
        if verbose and char == "#":
            newline = pattern.find("\n", index + 1)
            if newline < 0:
                break
            index = newline + 1
            continue
        if char == "[":
            in_class = True
            class_start = index + 1
            if pattern[class_start:class_start + 1] == "^":
                class_start += 1
            index += 1
            continue
        if char == "(":
            if pattern[index:index + 3] == "(?#":
                close = pattern.find(")", index + 3)
                index = len(pattern) if close < 0 else close + 1
                continue
            if pattern[index:index + 2] == "(?":
                marker = index + 2
                while marker < len(pattern) and pattern[marker] in "aiLmsux-":
                    marker += 1
                if (marker > index + 2
                        and pattern[marker:marker + 1] in (":", ")")):
                    enabled, _, disabled = pattern[index + 2:marker].partition("-")
                    scoped_verbose = verbose
                    if "x" in enabled:
                        scoped_verbose = True
                    if "x" in disabled:
                        scoped_verbose = False
                    if pattern[marker] == ")":
                        verbose = scoped_verbose
                        index = marker + 1
                        continue
                    scopes.append(verbose)
                    verbose = scoped_verbose
                    index = marker + 1
                    continue
            scopes.append(verbose)
            index += 1
            continue
        if char == ")" and scopes:
            verbose = scopes.pop()
        index += 1
    return found


PUBLIC_COMMENT_DATASETS = (
    ("text.comment.inline_unknown_named_unicode",
     r"(?# \N{NO SUCH PUBLIC CHARACTER})(?P<word>a)(?P<number>\d*)", 0),
    ("text.comment.global_verbose_unknown_named_unicode",
     r"# \N{NO SUCH PUBLIC CHARACTER}" + "\n"
     + r"(?P<word>a)(?P<number>\d*)", VERBOSE),
    ("text.comment.scoped_verbose_unknown_named_unicode",
     r"(?x:# \N{NO SUCH PUBLIC CHARACTER}" + "\n"
     + r"(?P<word>a)(?P<number>\d*))", 0),
)


def targeted_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for dataset, pattern, flags in PUBLIC_COMMENT_DATASETS:
        for category, count in (("comment_only", 99),
                                ("scanner_overlap", 5),
                                ("substitution_overlap", 4)):
            for ordinal in range(count):
                lookups: list[str] = []
                require(witness_named_escapes(pattern, flags, lookups) == []
                        and lookups == [],
                        "ignore every unknown named escape inside its real comment")
                records.append({"dataset": dataset, "category": category,
                                "ordinal": ordinal, "flags": flags,
                                "ignored_lookup_count": 0})
    require(len(records) == TARGETED_MISMATCH_COUNT,
            "require exact 324-record frozen public correction denominator")
    require(sum(row["category"] == "comment_only" for row in records)
            == COMMENT_ONLY_MISMATCH_COUNT,
            "require exactly 297 disjoint comment-only public mismatches")
    require(sum(row["category"] == "scanner_overlap" for row in records)
            == SCANNER_OVERLAP_COUNT,
            "require exactly fifteen explicit scanner overlaps")
    require(sum(row["category"] == "substitution_overlap" for row in records)
            == SUBSTITUTION_OVERLAP_COUNT,
            "require exactly twelve explicit substitution overlaps")
    for dataset, _pattern, _flags in PUBLIC_COMMENT_DATASETS:
        require(sum(row["dataset"] == dataset for row in records) == 108,
                "retain exactly 108 modeled mismatches for each named-comment dataset")
    return records


def semantic_tests() -> dict[str, object]:
    cases = 0
    rejected = 0

    def accepted(pattern: str | bytes, flags: int,
                 expected: list[tuple[int, int]], expected_lookups: list[str]) -> None:
        nonlocal cases
        lookups: list[str] = []
        require(witness_named_escapes(pattern, flags, lookups) == expected
                and lookups == expected_lookups,
                "reject changed comment, class, scope, valid-name, or bytes semantics")
        cases += 1

    def rejected_error(pattern: str, flags: int, message: str, position: int) -> None:
        nonlocal cases, rejected
        try:
            witness_named_escapes(pattern, flags)
        except WitnessPatternError as error:
            require(error.msg == message and error.pattern is pattern
                    and error.pos == position,
                    "preserve exact active named-escape error, pattern, and offset")
            cases += 1
            rejected += 1
            return
        raise FreezeError("active malformed or unknown named escape unexpectedly passed")

    known = r"\N{LATIN SMALL LETTER A}"
    capital = r"\N{LATIN CAPITAL LETTER A}"
    unknown = r"\N{NO SUCH PUBLIC CHARACTER}"
    malformed = (unknown, r"\N{}", r"\N{", r"\N{UNTERMINATED")
    for payload in malformed:
        for ordinal in range(24):
            prefix = "a" * (ordinal % 5)
            suffix = "z" * (ordinal // 5)
            inline = prefix + "(?# " + payload + " " + suffix + ")" + known
            accepted(inline, ordinal % 2 * VERBOSE,
                     [(inline.index(known), ord("a"))], ["LATIN SMALL LETTER A"])
            global_comment = prefix + "# " + payload + " " + suffix + "\n" + known
            accepted(global_comment, VERBOSE,
                     [(global_comment.index(known), ord("a"))],
                     ["LATIN SMALL LETTER A"])
            scoped = prefix + "(?x:# " + payload + " " + suffix + "\n" + known + ")"
            accepted(scoped, ordinal % 2 * VERBOSE,
                     [(scoped.index(known), ord("a"))], ["LATIN SMALL LETTER A"])

    for ordinal in range(96):
        payload = malformed[ordinal % len(malformed)].encode("ascii")
        pattern = b"(?x:# " + payload + b"\n[a#])"
        accepted(pattern, VERBOSE if ordinal % 2 else 0, [], [])

    for outer in ("x", "-x", "imx-s", "im-x"):
        for inner in ("x", "-x", "ix-m", "i-x", "i", "s-m"):
            for initial in (0, VERBOSE):
                pattern = ("(?" + outer + ":(?" + inner + ":# " + unknown
                           + "\n" + known + ")" + capital + ")" + known)
                enabled, _, disabled = inner.partition("-")
                inner_verbose = ("x" in enabled
                                 or "x" not in disabled
                                 and ("x" in outer.partition("-")[0]
                                      or "x" not in outer.partition("-")[2]
                                      and bool(initial & VERBOSE)))
                if inner_verbose:
                    expected = [(pattern.index(known), ord("a")),
                                (pattern.index(capital), ord("A")),
                                (pattern.rindex(known), ord("a"))]
                    accepted(pattern, initial, expected,
                             ["LATIN SMALL LETTER A", "LATIN CAPITAL LETTER A",
                              "LATIN SMALL LETTER A"])
                else:
                    rejected_error(pattern, initial,
                                   "undefined character name 'NO SUCH PUBLIC CHARACTER'",
                                   pattern.index(unknown))

    for ordinal in range(40):
        pattern = "(?x)" + "a" * (ordinal % 4) + "# " + unknown + "\r\n" + known
        accepted(pattern, 0, [(pattern.index(known), ord("a"))],
                 ["LATIN SMALL LETTER A"])
        pattern = "(?i-x:" + r"\#" + known + ")"
        accepted(pattern, VERBOSE, [(pattern.index(known), ord("a"))],
                 ["LATIN SMALL LETTER A"])

    class_patterns = (
        "[#" + known + "]",
        "[^#" + known + "]",
        "[]#" + known + "]",
        "[^]#" + known + "]",
        "[" + r"\]" + "#" + known + "]",
        "(?x:[#" + known + "])" + capital,
    )
    for pattern in class_patterns:
        expected: list[tuple[int, int]] = [(pattern.index(known), ord("a"))]
        names = ["LATIN SMALL LETTER A"]
        if capital in pattern:
            expected.append((pattern.index(capital), ord("A")))
            names.append("LATIN CAPITAL LETTER A")
        for flags in (0, VERBOSE, VERBOSE | 2, VERBOSE | 256):
            accepted(pattern, flags, expected, names)

    escaped = (
        (r"\\N{NO SUCH PUBLIC CHARACTER}" + known, 0),
        (r"\#" + known, VERBOSE),
        (r"\(" + known + r"\)", VERBOSE),
        (r"\[" + known + r"\]", VERBOSE),
        (r"\ " + known, VERBOSE),
        ("\\" + "\n" + known, VERBOSE),
    )
    for pattern, flags in escaped:
        accepted(pattern, flags, [(pattern.index(known), ord("a"))],
                 ["LATIN SMALL LETTER A"])

    for flags in (0, 2, 32, 64, 66, 96, 256, 320, -1):
        for prefix in ("", "a", "(?:", "(?i:"):
            suffix = ")" if prefix.endswith(":") else ""
            pattern = prefix + known + suffix
            accepted(pattern, flags, [(pattern.index(known), ord("a"))],
                     ["LATIN SMALL LETTER A"])

    active_errors = (
        (r"\N{}", 0, "missing character name", 3),
        (r"\N{", 0, "missing character name", 3),
        (r"x\N{BROKEN", 0, "missing }, unterminated name", 4),
        (unknown, 0, "undefined character name 'NO SUCH PUBLIC CHARACTER'", 0),
        (r"\N{MULTI CODEPOINT}", 0,
         "undefined character name 'MULTI CODEPOINT'", 0),
        ("#" + unknown, 0,
         "undefined character name 'NO SUCH PUBLIC CHARACTER'", 1),
        (r"\#" + unknown, VERBOSE,
         "undefined character name 'NO SUCH PUBLIC CHARACTER'", 2),
        ("[#" + unknown + "]", VERBOSE,
         "undefined character name 'NO SUCH PUBLIC CHARACTER'", 2),
        ("(?-x:#" + unknown + ")", VERBOSE,
         "undefined character name 'NO SUCH PUBLIC CHARACTER'", 6),
    )
    for pattern, flags, message, position in active_errors:
        rejected_error(pattern, flags, message, position)

    no_newline = "# " + unknown
    accepted(no_newline, VERBOSE, [], [])
    accepted("(?# " + unknown, 0, [], [])
    accepted("(?x:# " + unknown, 0, [], [])

    records = targeted_records()
    cases += len(records)
    require(cases >= 800 and len(records) == 324 and rejected >= 15,
            "require exhaustive comment, scope, class, flags, bytes, and error tests")
    return {
        "semantic_case_count": cases,
        "active_error_case_count": rejected,
        "targeted_record_count": len(records),
        "targeted_records_sha256": digest(canonical(records).encode("utf-8")),
        "named_comment_dataset_count": len(PUBLIC_COMMENT_DATASETS),
        "mismatches_per_named_comment_dataset": 108,
        "disjoint_comment_only_record_count": COMMENT_ONLY_MISMATCH_COUNT,
        "scanner_overlap_record_count": SCANNER_OVERLAP_COUNT,
        "substitution_overlap_record_count": SUBSTITUTION_OVERLAP_COUNT,
        "comment_unknown_lookup_count": 0,
        "global_verbose_flag_forwarded": True,
        "scanner_verbose_flag_forwarded": True,
        "nested_scoped_enable_disable_preserved": True,
        "inline_comment_ignored": True,
        "verbose_line_comments_ignored": True,
        "character_class_named_escapes_preserved": True,
        "active_named_error_offsets_preserved": True,
        "bytes_patterns_unchanged": True,
    }


def synthetic_tests(wall: SourceWall) -> dict[str, object]:
    source = synthetic_source()
    corrected = transform(source)
    rejected = 0

    def reject(callback, reason: str) -> None:
        nonlocal rejected
        try:
            callback()
        except (FreezeError, OSError, TypeError, ValueError, WitnessPatternError):
            rejected += 1
            return
        raise FreezeError("hostile source-only control unexpectedly passed: " + reason)

    for original in (ORIGINAL_COMPILE, ORIGINAL_SCANNER_CALL, ORIGINAL_NAMED_SCANNER):
        reject(lambda item=original: transform(source.replace(item, b"", 1)),
               "removed exact frozen adapter correction site")
        reject(lambda item=original: transform(source.replace(item, item * 2, 1)),
               "duplicated exact frozen adapter correction site")
        for offset in range(0, len(original), max(1, len(original) // 11)):
            changed = original[:offset] + bytes((original[offset] ^ 1,)) \
                + original[offset + 1:]
            reject(lambda old=original, new=changed:
                   transform(source.replace(old, new, 1)),
                   "mutated complete exact frozen adapter correction site")
    for anchor, _count in PRESERVED_ANCHORS:
        reject(lambda item=anchor: transform(source.replace(item, b"", 1)),
               "removed immutable first-party bridge, warning, flags, or cache anchor")
    for payload in (b'{"x":1,"x":2}', b"NaN", b"Infinity", b"-Infinity",
                    b"1e999", b"1.", b"1e", b"01", b'{"x":"\\ud800"}',
                    b'{"x":1} trailing'):
        reject(lambda value=payload: StrictJSON(value).decode(),
               "malformed, duplicate, nonfinite, or trailing authenticated evidence")
    require(StrictJSON(b'{"x":1.25,"y":-2e-3}').decode()
            == {"x": 1.25, "y": -0.002},
            "authenticate complete public receipts containing ordinary finite floats")

    reject(lambda: wall.parent(INPUT), "canonical candidate source in source-only mode")
    reject(lambda: wall.parent("candidates/_rust_engine.so"), "native Rust matcher")
    reject(lambda: wall.parent("candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
           "native bridge")
    reject(lambda: wall.parent("oracle/phase3/expanded-sealed-holdout-v2.json"),
           "invalidated final holdout proposal")
    reject(lambda: wall.parent("oracle/phase3/expanded-sealed-holdout-v3.json"),
           "unpublished rekeyed holdout proposal")
    reject(lambda: wall.parent(LEDGER[:-5] + ".json.gz"), "compressed original archive")
    reject(lambda: wall.parent(".git/config"), "repository internals")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved unticketed canonical adapter read")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level canonical adapter")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "direct canonical adapter")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "workspace directory mutation")
    reject(lambda: time.time(), "wall-clock sample")
    reject(lambda: time.perf_counter(), "performance timing sample")
    reject(lambda: sys.audit("import", "re", None, None, None, None),
           "production stdlib regular-expression package")
    reject(lambda: sys.audit("import", "regex", None, None, None, None),
           "third-party regular-expression package")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native loader")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None), "compiler")
    reject(lambda: sys.audit("socket.connect", None, None), "network")

    semantics = semantic_tests()
    require(rejected >= 70 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "require exhaustive hostile controls with no candidate reads or writes")
    no_matching_imports()
    return {"synthetic_source_bytes": len(source),
            "synthetic_output_bytes": len(corrected),
            "exact_source_delta_bytes": len(corrected) - len(source),
            "replacement_site_count": 3,
            "hostile_controls_rejected": rejected,
            "candidate_source_files_read": 0,
            "native_libraries_loaded": 0,
            "archive_files_opened": 0,
            "proposal_files_opened": 0,
            "clock_samples": 0,
            "workspace_mutations": 0,
            "semantics": semantics}


def value(document: object, name: str, expected: object) -> None:
    require(type(document) is dict and document.get(name) == expected,
            "reject incomplete or substituted authenticated evidence: " + name)


def canonical_adapter_row(document: dict[str, object], field: str) -> None:
    rows = document.get(field)
    require(type(rows) is list, "require complete public canonical-candidate ledger")
    matches = [row for row in rows if type(row) is dict and row.get("path") == INPUT]
    require(len(matches) == 1, "require one exact immutable public canonical adapter")
    adapter = matches[0]
    assert isinstance(adapter, dict)
    for key, expected in (("role", "rust_adapter"), ("path", INPUT),
                          ("sha256", INPUT_SHA256), ("bytes", INPUT_BYTES),
                          ("device", DEVICE), ("inode", INPUT_INODE),
                          ("mode", "0600")):
        value(adapter, key, expected)


def authenticate_public_receipt(raw: bytes, record: tuple) -> dict[str, object]:
    architecture, relative, sha, count, inode, session = record
    document = StrictJSON(raw).decode()
    value(document, "schema", "rebar-owned-rust-native-architecture-public-gate-v2-"
                              "durable-publication-receipt")
    value(document, "status", "PASS")
    value(document, "root_authorization", "EXPLICIT")
    value(document, "architecture", architecture)
    value(document, "session", session)
    value(document, "frozen_commit", FROZEN_PUBLIC_COMMIT)
    value(document, "pushed_commit", FROZEN_PUBLIC_COMMIT)
    value(document, "canonical_candidate_modified", False)
    value(document, "public_10434_case_count", PUBLIC_CASE_COUNT)
    value(document, "public_10434_correctness_status", "FAIL")
    value(document, "public_10434_mismatch_count", PUBLIC_MISMATCH_COUNT)
    value(document, "public_416_timing_status", "PASS")
    value(document, "performance_evidence_scope",
          "EXPLORATORY CORRECTNESS-GATED PUBLIC 416 ONLY; PUBLIC 10434 FAILED")
    value(document, "qualified_independent_family_count", 0)
    value(document, "minimum_qualified_independent_family_count", 3)
    value(document, "candidate_qualified", False)
    value(document, "runtime_non_delegation", "NOT ESTABLISHED; V4 STRICT AUDIT FAIL 1")
    value(document, "retired_v2_proposal_status",
          "COMPROMISED; RETIRED; NOT ACCESSED BY THIS CONTROLLER")
    value(document, "holdout", "INVALIDATED; REKEYED SUCCESSOR REQUIRED")
    value(document, "hidden_cases_read", 0)
    value(document, "controller_final_holdout_content_open_count", 0)
    value(document, "winner_selected", False)
    gate = document["public_416_correctness_gate"]
    value(gate, "status", "PASS")
    value(gate, "case_count", 416)
    value(gate, "mismatch_count", 0)
    value(gate, "all_mismatches", [])
    assert isinstance(document, dict)
    canonical_adapter_row(document, "canonical_candidates_before")
    canonical_adapter_row(document, "canonical_candidates_after")
    return {
        "architecture": architecture,
        "receipt_path": relative,
        "receipt_sha256": sha,
        "receipt_bytes": count,
        "receipt_device": DEVICE,
        "receipt_inode": inode,
        "session": session,
        "publication_status": "PASS",
        "public_10434_case_count": PUBLIC_CASE_COUNT,
        "public_10434_correctness_status": "FAIL",
        "public_10434_mismatch_count": PUBLIC_MISMATCH_COUNT,
        "public_416_case_count": 416,
        "public_416_mismatch_count": 0,
        "canonical_adapter_sha256": INPUT_SHA256,
        "qualified_independent_family_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED; V4 STRICT AUDIT FAIL 1",
        "winner_selected": False,
    }


def authenticate_ledger(raw: bytes) -> dict[str, object]:
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
    assert isinstance(ledger, dict)
    suites = ledger["suite_integrity"]
    require(type(suites) is list and len(suites) == 13,
            "require all thirteen complete immutable V25 original suite rows")
    indexed: dict[str, dict[str, object]] = {}
    for suite in suites:
        require(type(suite) is dict and type(suite.get("suite")) is str,
                "reject malformed original V25 authenticated suite")
        name = suite["suite"]
        assert isinstance(name, str)
        require(name not in indexed, "reject duplicate original V25 suite")
        indexed[name] = suite
        value(suite, "fully_observed", True)
        value(suite, "actual_worker_started", True)
    substitution = indexed["substitution_v2"]
    shape = indexed["shape_v2"]
    for key, expected in (("case_execution_denominator", 5120),
                          ("mismatch_count", 240),
                          ("verified_passing_case_count", 0),
                          ("failure_class", "SEMANTIC MISMATCH")):
        value(substitution, key, expected)
    for key, expected in (("case_execution_denominator", 10240),
                          ("mismatch_count", 1112),
                          ("verified_passing_case_count", 0),
                          ("failure_class", "SEMANTIC MISMATCH")):
        value(shape, key, expected)
    require(sum(suite["case_execution_denominator"] for suite in suites) == 31237
            and sum(suite["mismatch_count"] for suite in suites) == 1352
            and sum(suite["verified_passing_case_count"] for suite in suites) == 15877,
            "preserve original complete denominators, failures, and verified passes")
    return {"receipt_path": LEDGER, "receipt_sha256": LEDGER_SHA256,
            "receipt_bytes": LEDGER_BYTES, "receipt_device": DEVICE,
            "receipt_inode": LEDGER_INODE, "publication_status": "PASS",
            "candidate_status": "FAIL", "suite_count": 13,
            "case_execution_denominator": 31237, "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "substitution_v2_mismatch_count": 240,
            "shape_v2_mismatch_count": 1112,
            "named_private_waiver_count": 13}


def validate_contract(document: object, source_sha: str, protocol_sha: str) -> None:
    require(type(document) is dict, "require complete frozen named-escape contract")
    value(document, "schema", SCHEMA)
    value(document, "version", 1)
    value(document, "family", "rust")
    value(document, "phase", "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS")
    value(document, "status", "SOURCE FROZEN; VARIANT NOT MATERIALIZED; "
                              "NOT BUILT; NOT RUN")
    value(document, "source", {"path": SOURCE, "sha256": source_sha})
    value(document, "protocol", {"path": PROTOCOL, "sha256": protocol_sha})
    correction = document["exact_verbose_named_escape_correction"]
    delta = (len(CORRECTED_COMPILE) - len(ORIGINAL_COMPILE)
             + len(CORRECTED_SCANNER_CALL) - len(ORIGINAL_SCANNER_CALL)
             + len(CORRECTED_NAMED_SCANNER) - len(ORIGINAL_NAMED_SCANNER))
    for key, expected in (
            ("input_path", INPUT), ("input_sha256", INPUT_SHA256),
            ("input_bytes", INPUT_BYTES), ("input_device", DEVICE),
            ("input_inode", INPUT_INODE), ("input_mode", "0600"),
            ("target_path", TARGET), ("target_sha256", OUTPUT_SHA256),
            ("target_bytes", OUTPUT_BYTES), ("source_delta_bytes", delta),
            ("replacement_site_count", 3),
            ("module_compile_effective_flags_forwarded", True),
            ("scanner_compile_effective_flags_forwarded", True),
            ("inline_comment_named_escapes_ignored", True),
            ("global_verbose_comment_named_escapes_ignored", True),
            ("scoped_verbose_comment_named_escapes_ignored", True),
            ("nested_inline_verbose_enable_disable_supported", True),
            ("escaped_character_boundaries_preserved", True),
            ("character_class_named_escapes_preserved", True),
            ("line_comment_terminator", "LF"),
            ("bytes_pattern_behavior_unchanged", True),
            ("active_named_escape_error_offsets_preserved", True),
            ("public_flags_warnings_cache_semantics_preserved", True),
            ("engine_from_scratch_preserved", True),
            ("stdlib_matching_delegation_added", False),
            ("external_regex_dependency_added", False),
            ("runtime_non_delegation", "NOT ESTABLISHED"),
            ("candidate_built", False), ("candidate_imported", False),
            ("candidate_matching", "NOT RUN"), ("candidate_qualified", False)):
        value(correction, key, expected)

    partition = document["exact_public_failure_partition"]
    for key, expected in (
            ("public_case_count", PUBLIC_CASE_COUNT),
            ("authenticated_public_mismatch_count", PUBLIC_MISMATCH_COUNT),
            ("targeted_record_count", TARGETED_MISMATCH_COUNT),
            ("disjoint_comment_only_record_count", COMMENT_ONLY_MISMATCH_COUNT),
            ("scanner_overlap_record_count", SCANNER_OVERLAP_COUNT),
            ("substitution_overlap_record_count", SUBSTITUTION_OVERLAP_COUNT),
            ("named_comment_dataset_count", 3),
            ("mismatches_per_named_comment_dataset", 108),
            ("predicted_remaining_public_mismatch_count", 821),
            ("predicted_remaining_public_mismatch_measured", False),
            ("other_public_patterns_preserved", True),
            ("candidate_correctness", "NOT MEASURED")):
        value(partition, key, expected)
    value(partition, "named_comment_datasets",
          [item[0] for item in PUBLIC_COMMENT_DATASETS])

    receipts = document["immutable_public_v26_v27_receipts"]
    require(type(receipts) is list and len(receipts) == len(PUBLIC_RECEIPTS),
            "require exactly the two immutable latest public V26/V27 receipts")
    for document_receipt, owner in zip(receipts, PUBLIC_RECEIPTS):
        architecture, path, sha, count, inode, session = owner
        for key, expected in (("architecture", architecture), ("receipt_path", path),
                              ("receipt_sha256", sha), ("receipt_bytes", count),
                              ("receipt_device", DEVICE), ("receipt_inode", inode),
                              ("session", session), ("publication_status", "PASS"),
                              ("public_10434_case_count", PUBLIC_CASE_COUNT),
                              ("public_10434_correctness_status", "FAIL"),
                              ("public_10434_mismatch_count", PUBLIC_MISMATCH_COUNT),
                              ("public_416_case_count", 416),
                              ("public_416_mismatch_count", 0),
                              ("canonical_adapter_sha256", INPUT_SHA256),
                              ("qualified_independent_family_count", 0),
                              ("runtime_non_delegation",
                               "NOT ESTABLISHED; V4 STRICT AUDIT FAIL 1"),
                              ("winner_selected", False)):
            value(document_receipt, key, expected)

    ledger = document["immutable_original_v25_ledger"]
    for key, expected in (("receipt_path", LEDGER), ("receipt_sha256", LEDGER_SHA256),
                          ("receipt_bytes", LEDGER_BYTES),
                          ("receipt_device", DEVICE), ("receipt_inode", LEDGER_INODE),
                          ("publication_status", "PASS"), ("candidate_status", "FAIL"),
                          ("suite_count", 13), ("case_execution_denominator", 31237),
                          ("semantic_mismatch_count", 1352),
                          ("verified_passing_case_count", 15877),
                          ("substitution_v2_mismatch_count", 240),
                          ("shape_v2_mismatch_count", 1112),
                          ("named_private_waiver_count", 13)):
        value(ledger, key, expected)

    wall = document["physical_source_wall"]
    for key, expected in (
            ("installed_before_owner_reads", True),
            ("descriptor_relative_o_nofollow", True),
            ("authenticated_public_evidence_receipt_count", 3),
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
            ("proposal_open_allowed", False),
            ("final_holdout_open_allowed", False),
            ("clock_access_allowed", False)):
        value(wall, key, expected)

    effects = document["source_only_effects"]
    for key in ("candidate_source_files_read", "candidate_executions",
                "candidate_imports", "candidate_workers_started",
                "compiler_processes_started", "native_binary_files_opened",
                "native_libraries_loaded", "compressed_archives_opened",
                "compressed_archives_inflated", "proposals_opened",
                "holdout_cases_opened", "holdout_cases_generated", "clock_samples",
                "network_requests", "workspace_mutations"):
        value(effects, key, 0)
    value(effects, "runtime_non_delegation", "NOT ESTABLISHED")
    value(effects, "candidate_correctness", "NOT MEASURED")
    value(effects, "candidate_matching", "NOT RUN")
    value(effects, "final_holdout", "INVALIDATED; REKEYED SUCCESSOR REQUIRED")
    value(effects, "performance", "NOT MEASURED")
    value(effects, "winner_selected", False)


def parse_arguments(arguments: list[str]) -> dict[str, object]:
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
        require(item not in parsed, "reject duplicated immutable option: " + item)
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
        require(set(parsed) == {mode}, "self-test takes no owner or root arguments")
    elif mode == "--verify-source":
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256"},
                "source verification requires exactly the frozen owner digest triple")
    else:
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256", "--root-authorized",
                                "--frozen-commit", "--pushed-commit"},
                "root-only apply requires exact frozen owners and pushed commitment")
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


def zero_effects(wall: SourceWall, mode: str) -> dict[str, object]:
    return {"mode": mode,
            "approved_public_owner_reads": wall.public_reads,
            "candidate_source_files_read": wall.source_reads,
            "candidate_executions": 0,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_binary_files_opened": 0,
            "native_libraries_loaded": 0,
            "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0,
            "proposals_opened": 0,
            "holdout_cases_opened": 0,
            "holdout_cases_generated": 0,
            "clock_samples": 0,
            "network_requests": 0,
            "workspace_mutations": wall.workspace_mutations,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_correctness": "NOT MEASURED",
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
            "final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "performance": "NOT MEASURED",
            "winner_selected": False}


def main(arguments: list[str]) -> dict[str, object]:
    verify_runtime()
    options = parse_arguments(arguments)
    apply = options.get("--apply") is True
    wall = SourceWall(apply)
    no_matching_imports()
    wall.install()
    if options.get("--self-test") is True:
        controls = synthetic_tests(wall)
        require(wall.public_reads == 0 and wall.source_reads == 0
                and wall.workspace_mutations == 0 and wall.root is None,
                "self-test reads no owners or candidates and mutates nothing")
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
    receipts: list[dict[str, object]] = []
    for receipt in PUBLIC_RECEIPTS:
        architecture, relative, sha, count, inode, _session = receipt
        assert isinstance(relative, str) and isinstance(sha, str)
        assert isinstance(count, int) and isinstance(inode, int)
        receipts.append(authenticate_public_receipt(
            wall.read(relative, count, inode, sha), receipt))
        require(receipts[-1]["architecture"] == architecture,
                "reject swapped immutable public V26/V27 publication receipts")
    ledger = authenticate_ledger(
        wall.read(LEDGER, LEDGER_BYTES, LEDGER_INODE, LEDGER_SHA256))
    require(wall.public_reads == 6 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "authenticate only three frozen owners and V26/V27/V25 receipts")

    if not apply:
        controls = synthetic_tests(wall)
        no_matching_imports()
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; SOURCE FROZEN; NO CANDIDATE SOURCE READ",
                "source_sha256": source_sha,
                "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "authenticated_public_receipts": receipts,
                "authenticated_original_ledger": ledger,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "synthetic_controls": controls,
                "effects": zero_effects(wall, "SOURCE FREEZE")}

    require(transform(synthetic_source()) and semantic_tests()
            and wall.source_reads == 0,
            "require exhaustive independent controls before root-only adapter access")
    original = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA256)
    corrected = transform(original, exact=True)
    wall.materialize(corrected)
    no_matching_imports()
    require(wall.source_reads == 1 and wall.workspace_mutations == 2,
            "materialize exactly one exclusive directory and corrected adapter file")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; EXACT NAMED-ESCAPE CORRECTION; NOT BUILT; NOT RUN",
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
            "targeted_public_mismatch_count": TARGETED_MISMATCH_COUNT,
            "disjoint_comment_only_mismatch_count": COMMENT_ONLY_MISMATCH_COUNT,
            "scanner_overlap_count": SCANNER_OVERLAP_COUNT,
            "substitution_overlap_count": SUBSTITUTION_OVERLAP_COUNT,
            "effects": zero_effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError) as error:
        sys.stderr.write("rust-verbose-named-escape-semantics-v1: "
                         + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
