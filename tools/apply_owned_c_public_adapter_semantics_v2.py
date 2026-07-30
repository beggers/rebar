#!/usr/bin/env python3
"""Correct the authenticated first-party C adapter materialization controller.

The previous V1 controller rejected its own completed root-only controls because
it gave a bytes object to a guard that requires the singleton True.  This V2
freeze preserves the real failure, the complete V1 freeze, and all actual C
evidence without opening any candidate in source-only modes.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("first-party C adapter V2 cannot import a regular-expression engine")

import _io
import builtins
import enum
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
SCHEMA = "rebar-owned-c-public-adapter-semantics-v2-source-freeze"
SOURCE = "tools/apply_owned_c_public_adapter_semantics_v2.py"
PROTOCOL = "oracle/phase2/C-PUBLIC-ADAPTER-SEMANTICS-V2.md"
CONTRACT = "oracle/phase2/c-public-adapter-semantics-v2.json"
INPUT = "candidates/vm_candidate.py"
INPUT_SHA256 = "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
INPUT_BYTES = 60707
INPUT_INODE = 428074
TARGET_DIRECTORY = "candidates/c/variants/public_adapter_semantics_v2"
TARGET = TARGET_DIRECTORY + "/vm_candidate.py"
OUTPUT_SHA256 = "4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a"
OUTPUT_BYTES = 61663

V1_OWNERS = (
    ("tools/apply_owned_c_public_adapter_semantics_v1.py",
     "4604e145a6c5d135f690cb8ab2f869be33456e20f9ad27acc193f93fb1beaddb"),
    ("oracle/phase2/C-PUBLIC-ADAPTER-SEMANTICS-V1.md",
     "fe36c0ebba88d61375146bf22eb339456b86bf07f01ed8e0d64abe2c2562696a"),
    ("oracle/phase2/c-public-adapter-semantics-v1.json",
     "e0a794cf149b03880355e4660a669ebee4bca86efd937f09c3acfc79992afa6a"),
)
V1_FAILURE = (
    "oracle/phase2/evidence/c-public-adapter-semantics-v1-preapplication-failure.json",
    "d82ed4077f0b16310c7650bbe6c6f7c47f301d2d3a8f1f720c0958effc3788fa",
    845, 525054,
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
C21_ENGINE_SHA256 = "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
C21_NATIVE_SHA256 = "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60"

OLD_FLAG = b'''class RegexFlag(enum.IntFlag):
    ASCII = 256
    IGNORECASE = 2
    LOCALE = 4
    UNICODE = 32
    MULTILINE = 8
    DOTALL = 16
    VERBOSE = 64
    DEBUG = 128

    def __repr__(self):
        value = int(self)
        if not value:
            return "re.NOFLAG"
        ordered = ((self.ASCII, "ASCII"), (self.IGNORECASE, "IGNORECASE"), (self.LOCALE, "LOCALE"), (self.UNICODE, "UNICODE"), (self.MULTILINE, "MULTILINE"), (self.DOTALL, "DOTALL"), (self.VERBOSE, "VERBOSE"), (self.DEBUG, "DEBUG"))
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
        if unknown:
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = __repr__
'''

NEW_FLAG = b'''class RegexFlag(enum.IntFlag):
    NOFLAG = 0
    ASCII = A = 256
    IGNORECASE = I = 2
    LOCALE = L = 4
    UNICODE = U = 32
    MULTILINE = M = 8
    DOTALL = S = 16
    VERBOSE = X = 64
    DEBUG = 128
    _numeric_repr_ = hex

    def __repr__(self):
        value = int(self)
        if not value:
            return "re.NOFLAG"
        ordered = (
            (2, "IGNORECASE"),
            (4, "LOCALE"),
            (8, "MULTILINE"),
            (16, "DOTALL"),
            (32, "UNICODE"),
            (64, "VERBOSE"),
            (128, "DEBUG"),
            (256, "ASCII"),
        )
        parts = [f"re.{name}" for bit, name in ordered if value & bit]
        unknown = value & ~sum(bit for bit, _ in ordered)
        if unknown:
            if not parts:
                return f"re.RegexFlag({value!r})"
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = object.__str__
'''

OLD_ERROR = b"class PatternError(Exception):\n    def __init__(self, msg, pattern=None, pos=None):\n"
NEW_ERROR = b"class PatternError(Exception):\n    __module__ = \"re\"\n\n    def __init__(self, msg, pattern=None, pos=None):\n"
OLD_CONFIGURE = b"_vm_native.configure(_template, _template_parts)\n"
NEW_CONFIGURE = OLD_CONFIGURE + b"RegexFlag.__module__ = \"re\"\n"
OLD_CACHES = b"_CACHE = {}\n\n\ndef compile(pattern, flags=0):\n"
NEW_CACHES = (b"_CACHE = {}\n_CACHE2 = {}\n_MAXCACHE = 512\n_MAXCACHE2 = 256\n\n\n"
              b"def compile(pattern, flags=0):\n")
OLD_LOOKUP = b'''    key = (type(pattern), pattern, flags)
    try:
        return _CACHE[key]
    except KeyError:
        cached = _CACHE.get((type(pattern), pattern, flags))
        if cached is not None:
            return cached
    flags = int(flags)
'''
NEW_LOOKUP = b'''    key = (type(pattern), pattern, flags)
    try:
        return _CACHE2[key]
    except KeyError:
        pass
    cached = _CACHE.pop(key, None)
    if cached is not None:
        if len(_CACHE) >= _MAXCACHE:
            try:
                del _CACHE[next(iter(_CACHE))]
            except (StopIteration, RuntimeError, KeyError):
                pass
        _CACHE[key] = cached
        if len(_CACHE2) >= _MAXCACHE2:
            try:
                del _CACHE2[next(iter(_CACHE2))]
            except (StopIteration, RuntimeError, KeyError):
                pass
        _CACHE2[key] = cached
        return cached
    flags = int(flags)
'''
OLD_STORE = b'''    canonical_pattern = str.__str__(pattern) if isinstance(pattern, str) else bytes(pattern)
    _CACHE[(type(pattern), canonical_pattern, flags)] = result
    if flags & int(DEBUG):
        print(f"AST {node!r}")
    return result
'''
NEW_STORE = b'''    if flags & int(DEBUG):
        print(f"AST {node!r}")
        return result
    key = (type(pattern), pattern, flags)
    if len(_CACHE) >= _MAXCACHE:
        try:
            del _CACHE[next(iter(_CACHE))]
        except (StopIteration, RuntimeError, KeyError):
            pass
    _CACHE[key] = result
    if len(_CACHE2) >= _MAXCACHE2:
        try:
            del _CACHE2[next(iter(_CACHE2))]
        except (StopIteration, RuntimeError, KeyError):
            pass
    _CACHE2[key] = result
    return result
'''
OLD_PURGE = b"def purge():\n    _CACHE.clear()\n"
NEW_PURGE = b"def purge():\n    _CACHE.clear()\n    _CACHE2.clear()\n"
EDITS = (("public flag aliases and representation", OLD_FLAG, NEW_FLAG),
         ("PatternError public module", OLD_ERROR, NEW_ERROR),
         ("flag module after native ownership attestation", OLD_CONFIGURE, NEW_CONFIGURE),
         ("bounded two-cache declaration", OLD_CACHES, NEW_CACHES),
         ("type-preserving FIFO and LRU lookup", OLD_LOOKUP, NEW_LOOKUP),
         ("DEBUG bypass and bounded insertion", OLD_STORE, NEW_STORE),
         ("two-cache public purge", OLD_PURGE, NEW_PURGE))
PRESERVED = ((b"import enum\n", 1),
             (b"from candidates import _vm_native\n", 1),
             (b"class _BytecodeParser:\n", 1),
             (b"class _BytecodeCompiler:\n", 1),
             (b"class Pattern(_vm_native.Pattern, metaclass=_PatternType):\n", 1),
             (b"Match = _vm_native.Match\n", 1),
             (OLD_CONFIGURE, 1),
             (b"def compile(pattern, flags=0):\n", 1),
             (b"def purge():\n", 1))


class FreezeError(Exception):
    """Reject substituted frozen owners or unauthorized source effects."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only complete owned source bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(char in "0123456789abcdef" for char in value),
         "require complete lowercase SHA-256 for " + label)
    return value


def quote(value: str) -> str:
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for item in value:
        number = ord(item)
        need(not 0xD800 <= number <= 0xDFFF, "reject invalid JSON surrogate")
        result.append(escapes.get(item, "\\u" + format(number, "04x")
                      if number < 32 else item))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    need(depth < 60, "bound immutable JSON evidence nesting")
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
        need(all(type(key) is str for key in value), "reject nontext JSON key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported source-only evidence")


class JSON:
    """Bounded duplicate-rejecting receipt parser with no matcher imports."""

    def __init__(self, raw: bytes) -> None:
        need(type(raw) is bytes and 0 < len(raw) <= 131072,
             "require a bounded immutable plaintext owner")
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
                need(0xDC00 <= low <= 0xDFFF, "reject invalid JSON low surrogate")
                self.at += 6
                result.append(chr(0x10000 + ((number - 0xD800) << 10)
                                  + low - 0xDC00))
            else:
                need(not 0xDC00 <= number <= 0xDFFF,
                     "reject unpaired low JSON surrogate")
                result.append(chr(number))
        raise FreezeError("reject unterminated JSON string")

    def value(self, depth: int = 0) -> object:
        need(depth < 60, "bound source-only JSON parser depth")
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
                need(key not in result, "reject duplicate authenticated JSON key")
                self.count += 1
                need(self.count < 20000, "bound authenticated receipt fields")
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
                need(self.count < 20000, "bound immutable receipt list")
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
                     "reject noncanonical leading-zero number")
            else:
                need(self.text[self.at] in "123456789", "reject malformed integer")
                while self.at < len(self.text) and self.text[self.at] in "0123456789":
                    self.at += 1
            need(self.text[self.at:self.at + 1] not in (".", "e", "E"),
                 "reject floating source-only contract values")
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
    roots = ("re", "_sre", "regex", "ctypes", "candidates", "rebar",
             "subprocess", "socket", "threading", "multiprocessing",
             "concurrent", "gzip", "zipfile", "tarfile")
    need(not any(name == root or name.startswith(root + ".")
                 for name in sys.modules for root in roots),
         "reject matcher, candidate, native loader, archive, or process")


class Wall:
    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT, V1_FAILURE[0],
                                 C12_LEDGER[0], C21_BUILD[0], C21_ROOT[0])
                                + tuple(row[0] for row in V1_OWNERS))
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
        raise FreezeError("first-party C adapter V2 wall rejected " + reason)

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
        need(not self.installed, "install the descriptor wall once")
        sys.addaudithook(self.audit)
        builtins.open = self.blocked("builtins.open")
        for module in (_io, io):
            module.open = self.blocked(module.__name__ + ".open")
            module.FileIO = self.blocked(module.__name__ + ".FileIO")
            if hasattr(module, "open_code"):
                module.open_code = self.blocked(module.__name__ + ".open_code")
        for name in ("open", "read", "write", "close", "fstat", "fsync",
                     "mkdir", "fdopen", "dup", "dup2", "stat", "lstat",
                     "readlink", "listdir", "scandir", "walk", "fwalk", "access",
                     "fork", "posix_spawn", "posix_spawnp", "system", "makedirs",
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
             "reject unguarded or nested descriptor authorization")
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
        return os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)

    def open_root(self) -> None:
        need(self.root is None, "open immutable workspace once")
        value = self.ticket(ROOT, self.directory_flags())
        info = self.native_fstat(value)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE,
             "reject substituted immutable workspace root")
        self.root = value
        self.live[value] = ("", "directory")

    def segment(self, value: object) -> str:
        need(type(value) is str and bool(value) and value not in (".", "..")
             and "/" not in value and "\x00" not in value,
             "reject unauthenticated or traversal descriptor segment")
        return value

    def child(self, parent: int, segment: str) -> int:
        name = self.segment(segment)
        owner = self.live.get(parent)
        need(owner is not None and owner[1] == "directory",
             "reject foreign parent directory descriptor")
        relative = name if not owner[0] else owner[0] + "/" + name
        allowed = any(item.startswith(relative + "/") for item in self.allowed)
        if self.apply:
            allowed = allowed or relative == TARGET_DIRECTORY or TARGET_DIRECTORY.startswith(relative + "/")
        need(allowed and not relative.startswith((".git/", ".agents/", ".codex/")),
             "reject private root, candidate, archive, or foreign owner")
        descriptor = self.ticket(name, self.directory_flags(), parent=parent)
        info = self.native_fstat(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE,
             "reject substituted or symlink source directory")
        self.live[descriptor] = (relative, "directory")
        return descriptor

    def close(self, descriptor: int) -> None:
        need(descriptor in self.live and descriptor != self.root,
             "reject foreign immutable descriptor close")
        self.native_close(descriptor)
        del self.live[descriptor]

    def parent(self, relative: str) -> tuple[int, list[int], str]:
        need(relative in self.allowed and self.root is not None,
             "deny candidate source before root-only authorization")
        pieces = relative.split("/")
        descriptor = self.root
        opened: list[int] = []
        try:
            for piece in pieces[:-1]:
                descriptor = self.child(descriptor, piece)
                opened.append(descriptor)
            return descriptor, opened, self.segment(pieces[-1])
        except BaseException:
            for item in reversed(opened):
                self.close(item)
            raise

    def read(self, relative: str, expected: str,
             size: int | None = None, inode: int | None = None) -> bytes:
        need(relative in self.allowed, "reject unauthorized immutable owner")
        checked_hash(expected, relative)
        parent, opened, name = self.parent(relative)
        descriptor: int | None = None
        try:
            descriptor = self.ticket(name, self.file_flags(), parent=parent)
            self.live[descriptor] = (relative, "file")
            before = self.native_fstat(descriptor)
            need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                 and stat.S_IMODE(before.st_mode) == 0o600 and before.st_nlink == 1
                 and before.st_uid == os.geteuid() and 0 < before.st_size < 262144
                 and (size is None or before.st_size == size)
                 and (inode is None or before.st_ino == inode),
                 "reject substituted complete immutable owner: " + relative)
            blocks: list[bytes] = []
            left = before.st_size
            while left:
                block = self.native_read(descriptor, min(left, 65536))
                need(type(block) is bytes and bool(block),
                     "reject truncated immutable evidence owner")
                blocks.append(block)
                left -= len(block)
            need(self.native_read(descriptor, 1) == b"",
                 "reject extra immutable evidence owner bytes")
            after = self.native_fstat(descriptor)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "reject owner concurrently modified while reading")
            payload = b"".join(blocks)
            need(digest(payload) == expected,
                 "reject substituted complete immutable owner digest")
            if relative == INPUT:
                self.candidate_reads += 1
            else:
                self.public_reads += 1
            return payload
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for item in reversed(opened):
                self.close(item)

    def materialize(self, data: bytes) -> None:
        need(self.apply and self.root is not None
             and len(data) == OUTPUT_BYTES and digest(data) == OUTPUT_SHA256,
             "deny unauthorized nonidentical adapter materialization")
        descriptor = self.root
        opened: list[int] = []
        try:
            pieces = TARGET_DIRECTORY.split("/")
            for part in pieces[:-1]:
                descriptor = self.child(descriptor, part)
                opened.append(descriptor)
            name = pieces[-1]
            need(self.mkdir_ticket is None, "reject nested directory ticket")
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
                     | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
            output = self.ticket("vm_candidate.py", flags, 0o600, parent=target)
            self.live[output] = (TARGET, "target")
            self.workspace_mutations += 1
            try:
                cursor = 0
                while cursor < len(data):
                    count = self.native_write(output, data[cursor:])
                    need(type(count) is int and count > 0,
                         "reject incomplete exclusive C adapter creation")
                    cursor += count
                info = self.native_fstat(output)
                need(stat.S_ISREG(info.st_mode) and info.st_dev == DEVICE
                     and stat.S_IMODE(info.st_mode) == 0o600
                     and info.st_nlink == 1 and info.st_size == OUTPUT_BYTES,
                     "reject substituted exclusive immutable C adapter")
                self.native_fsync(output)
            finally:
                self.close(output)
            self.native_fsync(target)
            readback = self.ticket("vm_candidate.py", self.file_flags(),
                                   parent=target)
            self.live[readback] = (TARGET, "readback")
            try:
                blocks: list[bytes] = []
                remaining = OUTPUT_BYTES
                while remaining:
                    block = self.native_read(readback, min(remaining, 65536))
                    need(bool(block), "reject incomplete durable C adapter readback")
                    blocks.append(block)
                    remaining -= len(block)
                need(self.native_read(readback, 1) == b""
                     and digest(b"".join(blocks)) == OUTPUT_SHA256,
                     "reject nonidentical durable C adapter materialization")
            finally:
                self.close(readback)
        finally:
            for item in reversed(opened):
                self.close(item)


def transform(raw: bytes, exact: bool = False) -> bytes:
    need(type(raw) is bytes, "transform only complete first-party adapter bytes")
    if exact:
        need(len(raw) == INPUT_BYTES and digest(raw) == INPUT_SHA256,
             "reject substituted canonical C Python adapter")
    previous = -1
    for description, original, _replacement in EDITS:
        need(raw.count(original) == 1,
             "require one exact reversible first-party site: " + description)
        location = raw.index(original)
        need(location > previous, "reject reordered owned adapter sites")
        previous = location
    for anchor, amount in PRESERVED:
        need(raw.count(anchor) == amount,
             "preserve first-party Python compiler and native matcher owner")
    result = raw
    for description, original, replacement in EDITS:
        result = result.replace(original, replacement, 1)
        need(result.count(replacement) == 1,
             "reject duplicate first-party correction: " + description)
    restored = result
    for _description, original, replacement in reversed(EDITS):
        restored = restored.replace(replacement, original, 1)
    need(restored == raw,
         "reject changes outside exactly seven reversible first-party sites")
    need(len(result) == len(raw)
         + sum(len(after) - len(before) for _name, before, after in EDITS),
         "reject extra first-party candidate source bytes")
    for anchor, amount in PRESERVED:
        need(result.count(anchor) == amount,
             "preserve the genuine independent C engine interface")
    for item in (b"import re\n", b"from re import ", b"import regex\n",
                 b"from regex import ", b"import ctypes\n", b"_sre."):
        need(raw.count(item) == result.count(item) == 0,
             "reject delegated CPython, external package, or foreign engine")
    if exact:
        need(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA256,
             "reject predicted immutable first-party adapter output drift")
    return result


def synthetic_source() -> bytes:
    return b"".join((b"import enum\n", b"from candidates import _vm_native\n",
                     OLD_FLAG, OLD_ERROR, b"        return None\n",
                     b"class _BytecodeParser:\n    pass\n",
                     b"class _BytecodeCompiler:\n    pass\n",
                     b"class Pattern(_vm_native.Pattern, metaclass=_PatternType):\n    pass\n",
                     b"Match = _vm_native.Match\n", OLD_CONFIGURE,
                     OLD_CACHES, OLD_LOOKUP, OLD_STORE, OLD_PURGE))


class ModelFlag(enum.IntFlag):
    NOFLAG = 0
    ASCII = A = 256
    IGNORECASE = I = 2
    LOCALE = L = 4
    UNICODE = U = 32
    MULTILINE = M = 8
    DOTALL = S = 16
    VERBOSE = X = 64
    DEBUG = 128
    _numeric_repr_ = hex

    def __repr__(self) -> str:
        value = int(self)
        if not value:
            return "re.NOFLAG"
        ordered = ((2, "IGNORECASE"), (4, "LOCALE"), (8, "MULTILINE"),
                   (16, "DOTALL"), (32, "UNICODE"), (64, "VERBOSE"),
                   (128, "DEBUG"), (256, "ASCII"))
        parts = ["re." + name for bit, name in ordered if value & bit]
        unknown = value & ~sum(bit for bit, _name in ordered)
        if unknown:
            if not parts:
                return "re.RegexFlag(" + repr(value) + ")"
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = object.__str__


ModelFlag.__module__ = "re"


class ModelCache:
    def __init__(self) -> None:
        self.lru: dict[tuple, object] = {}
        self.fifo: dict[tuple, object] = {}
        self.emissions = 0

    def compile(self, pattern: object, flags: int = 0) -> object:
        key = (type(pattern), pattern, flags)
        try:
            return self.fifo[key]
        except KeyError:
            pass
        result = self.lru.pop(key, None)
        if result is None:
            result = object()
            if flags & 128:
                self.emissions += 1
                return result
        if len(self.lru) >= 512:
            del self.lru[next(iter(self.lru))]
        self.lru[key] = result
        if len(self.fifo) >= 256:
            del self.fifo[next(iter(self.fifo))]
        self.fifo[key] = result
        return result

    def purge(self) -> None:
        self.lru.clear()
        self.fifo.clear()


def semantic_controls() -> dict[str, object]:
    count = 0
    need(ModelFlag.__module__ == "re", "preserve public RegexFlag module")
    count += 1
    aliases = (("ASCII", "A", 256), ("IGNORECASE", "I", 2),
               ("LOCALE", "L", 4), ("UNICODE", "U", 32),
               ("MULTILINE", "M", 8), ("DOTALL", "S", 16),
               ("VERBOSE", "X", 64))
    for name, alias, number in aliases:
        member = getattr(ModelFlag, name)
        need(member is getattr(ModelFlag, alias) and int(member) == number
             and member.name == name,
             "preserve genuine CPython public RegexFlag alias: " + alias)
        count += 1
    need(tuple(ModelFlag.__members__) == (
        "NOFLAG", "ASCII", "A", "IGNORECASE", "I", "LOCALE", "L",
        "UNICODE", "U", "MULTILINE", "M", "DOTALL", "S", "VERBOSE",
        "X", "DEBUG",
    ), "preserve exact first-party public flag alias ordering")
    count += 1
    examples = ((0, "re.NOFLAG"), (2, "re.IGNORECASE"), (4, "re.LOCALE"),
                (8, "re.MULTILINE"), (16, "re.DOTALL"), (32, "re.UNICODE"),
                (64, "re.VERBOSE"), (128, "re.DEBUG"), (256, "re.ASCII"),
                (258, "re.IGNORECASE|re.ASCII"),
                (1048576, "re.RegexFlag(1048576)"),
                (1048578, "re.IGNORECASE|0x100000"),
                (244215808, "re.RegexFlag(244215808)"),
                (1630208, "re.RegexFlag(1630208)"),
                (1847296, "re.RegexFlag(1847296)"))
    for value, expected in examples:
        member = ModelFlag(value)
        need(repr(member) == expected and str(member) == expected,
             "preserve exact known, mixed, unknown, and inverted public flags")
        count += 2

    class Text(str):
        pass

    class Bytes(bytes):
        pass

    cache = ModelCache()
    for index in range(96):
        text = "word-" + str(index)
        value = Text(text) if index % 2 == 0 else Bytes(text.encode("ascii"))
        original = cache.compile(value, index % 4)
        need(cache.compile(value, index % 4) is original,
             "retain exact same subclass cache identity")
        plain = str(value) if isinstance(value, Text) else bytes(value)
        need(cache.compile(plain, index % 4) is not original,
             "distinguish builtins and user pattern subclasses")
        count += 2
    debug = ModelCache()
    for ordinal in range(8):
        first = debug.compile("debug-" + str(ordinal), 128)
        second = debug.compile("debug-" + str(ordinal), 128)
        need(first is not second and not debug.lru and not debug.fifo,
             "never cache or suppress DEBUG compilations")
        count += 1
    need(debug.emissions == 16, "emit both actual public DEBUG observations")
    count += 1
    eviction = ModelCache()
    first = eviction.compile("oldest")
    for ordinal in range(512):
        eviction.compile("later-" + str(ordinal))
    need(len(eviction.lru) == 512 and len(eviction.fifo) == 256
         and eviction.compile("oldest") is not first,
         "preserve first-party 512 LRU and 256 FIFO eviction")
    count += 1
    old = eviction.compile("purge")
    eviction.purge()
    need(not eviction.lru and not eviction.fifo
         and eviction.compile("purge") is not old,
         "public purge clears both genuine first-party compile caches")
    count += 1
    modeled = {"pattern_error_module": 96, "subclass_cache_identity": 96,
               "public_types_unknown_flag_repr": 12,
               "pattern_flag_repr_order": 12,
               "surface_unknown_flag_repr": 96,
               "debug_cache_bypass": 8, "bounded_cache_eviction": 10}
    need(sum(modeled.values()) == 330,
         "preserve every one of 330 observed adapter-specific differences")
    return {"semantic_checks": count, "targeted_public_adapter_mismatches": 330,
            "modeled_partition": modeled, "additional_public_class_aliases": 7,
            "additional_public_flag_module_identity": 1,
            "unresolved_native_match_pickle_mismatches": 32}


def root_controls() -> dict[str, object]:
    """Exactly the same preauthorization path runs in self-test and root apply."""
    controls = semantic_controls()
    synthetic = transform(synthetic_source())
    ready = (type(controls) is dict
             and type(controls.get("semantic_checks")) is int
             and controls["semantic_checks"] >= 200
             and type(synthetic) is bytes and len(synthetic) > 0)
    need(ready, "require complete independent controls before root-only candidate access")
    need(type(ready) is bool and ready is True,
         "reject the historical truthy-bytes V1 preapplication regression")
    return controls


def hostile_controls(wall: Wall) -> dict[str, object]:
    rejected = 0

    def refuses(action: object, reason: str) -> None:
        nonlocal rejected
        failed = False
        try:
            action()
        except (FreezeError, OSError, ValueError, TypeError):
            failed = True
        need(failed, "accept forbidden source-only operation: " + reason)
        rejected += 1

    source = synthetic_source()
    corrected = transform(source)
    need(type(corrected) is bytes and bool(corrected),
         "require genuine byte-valued synthetic correction")
    refuses(lambda: need(corrected, "historical V1 truthy bytes"),
            "historical V1 truthy bytes passed as singleton True")
    for description, original, replacement in EDITS:
        refuses(lambda item=original: transform(source.replace(item, b"", 1)),
                "missing reversible site " + description)
        refuses(lambda item=original: transform(source + item),
                "duplicated reversible site " + description)
        need(corrected.count(replacement) == 1,
             "preserve exactly one first-party correction site")
        rejected += 1
    for action in (lambda: builtins.open(INPUT, "rb"),
                   lambda: _io.open(INPUT, "rb"),
                   lambda: io.open(INPUT, "rb"),
                   lambda: os.open(INPUT, os.O_RDONLY),
                   lambda: os.stat(INPUT), lambda: os.listdir(ROOT),
                   lambda: os.mkdir("forbidden-c-v2-directory"),
                   lambda: time.time(), lambda: time.perf_counter_ns()):
        refuses(action, "direct filesystem, candidate, archive, or clock")
    controls = root_controls()
    no_matchers()
    return {"hostile_controls": rejected + controls["semantic_checks"],
            "semantic": controls,
            "root_authorization_control_path_self_tested": True,
            "historical_v1_truthy_bytes_rejected": True}


def preserve_v1_failure(document: object) -> None:
    need(type(document) is dict, "require preserved actual root preapplication failure")
    expected = {
        "schema": "rebar-owned-c-public-adapter-semantics-v1-root-preapplication-failure",
        "status": "FAIL", "failure_phase": "PREAPPLICATION_SOURCE_CONTROL",
        "error": "require complete independent controls before root-only candidate access",
        "frozen_commit": "ccf7f71aba1df44b203a0b4d40b339feb7be8292",
        "pushed_commit": "ccf7f71aba1df44b203a0b4d40b339feb7be8292",
        "controller_source_sha256": V1_OWNERS[0][1],
        "protocol_sha256": V1_OWNERS[1][1],
        "contract_sha256": V1_OWNERS[2][1],
        "candidate_target_created": False,
        "candidate_executions": 0,
        "preserved_recorded_adapter_mismatches": 330,
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "final_cases_generated": 0,
        "winner_selected": False,
    }
    need(document == expected,
         "never replace, reinterpret, suppress, or weaken the real V1 failure")


def preserve_c12(document: object) -> None:
    need(type(document) is dict, "require authentic C12 failure publication")
    values = {"schema": "rebar-owned-repaired-c-original-campaign-v12-durable-publication-receipt",
              "version": 12, "family": "c", "status": "PASS",
              "publication_status": "PASS", "candidate_status": "FAIL",
              "candidate_qualified": False, "case_execution_denominator": 31237,
              "suite_count": 13, "completed_suite_count": 12,
              "verified_passing_case_count": 16413,
              "complete_observed_semantic_mismatch_record_count": 606,
              "candidate_execution_failure_count": 1,
              "semantic_mismatch_count": "NOT MEASURED",
              "unchanged_adapter_sha256": INPUT_SHA256,
              "corrected_source_sha256": C21_ENGINE_SHA256,
              "native_engine_sha256": C21_NATIVE_SHA256,
              "winner_selected": False}
    for name, value in values.items():
        need(document.get(name) == value,
             "preserve the actual failed C12 candidate result: " + name)
    suites = document.get("suite_outcomes")
    need(type(suites) is list and len(suites) == 13,
         "preserve all completed and unfinished original C groups")
    counts = {item["suite"]: item["mismatch_count"] for item in suites}
    for suite, count in (("managed_v1", 16), ("public_types_v1", 248),
                         ("substitution_v2", 224), ("public_surface_v19", 114),
                         ("pep688_v4", 4)):
        need(counts.get(suite) == count,
             "preserve every genuine observed C mismatch: " + suite)
    need(counts.get("subinterpreter_v2") == "NOT MEASURED",
         "preserve unfinished child-interpreter failure and unknown denominator")


def preserve_c21(build: object, root: object) -> None:
    need(type(build) is dict and type(root) is dict,
         "preserve both actual first-party C21 published provenance owners")
    need(build.get("family") == "c" and build.get("version") == 21
         and build.get("build_status") == "PASS"
         and build.get("adapter_source_sha256") == INPUT_SHA256
         and build.get("variant_source_sha256") == C21_ENGINE_SHA256
         and build.get("candidate_correctness") == "NOT MEASURED"
         and build.get("candidate_matching") == "NOT RUN"
         and build.get("byte_identical_native_artifacts") is True,
         "reject substituted first-party C21 build publication")
    phases = build.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "preserve both distinct first-party C21 offline source builds")
    for phase in phases:
        owners = phase.get("source_owners")
        need(type(owners) is list and len(owners) == 2
             and owners[0].get("sha256") == C21_ENGINE_SHA256
             and owners[0].get("bytes") == 221647
             and owners[1].get("sha256") == INPUT_SHA256
             and owners[1].get("bytes") == INPUT_BYTES
             and phase.get("native_output", {}).get("sha256") == C21_NATIVE_SHA256,
             "reject substituted first-party engine, adapter, or native artifact")
    need(root.get("family") == "c" and root.get("status") == "PASS"
         and root.get("derived_variant_sha256") == C21_ENGINE_SHA256
         and root.get("canonical_build_receipt_sha256") == C21_BUILD[1]
         and root.get("candidate_correctness") == "NOT MEASURED",
         "reject substituted actual C21 private-root publication")


def contract_document(source_hash: str, protocol_hash: str) -> dict[str, object]:
    return {
        "schema": SCHEMA, "version": 2,
        "status": "SOURCE FROZEN; V1 FAILURE PRESERVED; V2 VARIANT NOT MATERIALIZED",
        "phase": "CANDIDATES; ROOT-ONLY PREAPPLICATION CONTROL CORRECTION",
        "source": {"path": SOURCE, "sha256": source_hash},
        "protocol": {"path": PROTOCOL, "sha256": protocol_hash},
        "preserved_v1_source_freeze": [
            {"path": path, "sha256": value} for path, value in V1_OWNERS
        ],
        "preserved_v1_actual_failure": {
            "path": V1_FAILURE[0], "sha256": V1_FAILURE[1],
            "bytes": V1_FAILURE[2], "inode": V1_FAILURE[3],
            "failure_phase": "PREAPPLICATION_SOURCE_CONTROL",
            "target_created": False, "candidate_execution_count": 0,
            "exact_root_cause": "truthy bytes is not the singleton True",
            "corrected_path_tested_in_self_test": True,
        },
        "canonical_input": {"path": INPUT, "sha256": INPUT_SHA256,
                            "bytes": INPUT_BYTES, "inode": INPUT_INODE,
                            "device": DEVICE, "mode": "0600"},
        "correction": {
            "target_path": TARGET, "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES, "exact_reversible_site_count": 7,
            "same_output_as_preserved_v1": True,
            "targeted_observed_public_adapter_mismatches": 330,
            "additional_public_class_alias_obligations": 7,
            "additional_public_regex_flag_module_obligations": 1,
            "lru_capacity": 512, "fifo_capacity": 256,
            "root_controls_boolean_type_required": True,
            "root_controls_completed_before_canonical_read": True,
            "stdlib_regex_delegation": False,
            "external_regex_engine": False,
            "cross_candidate_engine": False,
        },
        "immutable_c12_failure": {
            "receipt_path": C12_LEDGER[0], "receipt_sha256": C12_LEDGER[1],
            "original_case_denominator": 31237,
            "verified_passing_case_count": 16413,
            "observed_mismatch_count": 606,
            "exact_total_mismatch_count": "NOT MEASURED",
            "candidate_status": "FAIL", "interpreter_isolation_finished": False,
        },
        "immutable_c21_build": {
            "build_receipt_path": C21_BUILD[0],
            "build_receipt_sha256": C21_BUILD[1],
            "root_receipt_path": C21_ROOT[0],
            "root_receipt_sha256": C21_ROOT[1],
            "native_source_sha256": C21_ENGINE_SHA256,
            "native_artifact_sha256": C21_NATIVE_SHA256,
            "independent_build_count": 2,
            "candidate_correctness": "NOT MEASURED",
        },
        "source_only_effects": {
            "candidate_source_files_read": 0,
            "candidate_imports": 0,
            "candidate_executions": 0,
            "compiler_processes": 0,
            "native_libraries_loaded": 0,
            "compressed_archives_opened": 0,
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
    index = 0
    while index < len(values):
        key = values[index]
        need(key in flags or key in named, "reject unauthorized argument: " + key)
        need(key not in parsed, "reject duplicated immutable option: " + key)
        if key in flags:
            parsed[key] = True
            index += 1
        else:
            need(index + 1 < len(values), "reject incomplete immutable argument")
            parsed[key] = values[index + 1]
            index += 2
    modes = [key for key in ("--self-test", "--verify-source", "--apply")
             if parsed.get(key)]
    need(len(modes) == 1, "require exactly one source-only or root-only mode")
    mode = modes[0]
    if mode == "--self-test":
        need(set(parsed) == {mode}, "self-test cannot open frozen owners")
    elif mode == "--verify-source":
        need(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                             "--contract-sha256"},
             "verify only the three exact frozen V2 owners")
    else:
        need(set(parsed) == {mode, "--root-authorized", "--source-sha256",
                             "--protocol-sha256", "--contract-sha256",
                             "--frozen-commit", "--pushed-commit"},
             "require explicit root authority and pushed frozen commitment")
        for key in ("--frozen-commit", "--pushed-commit"):
            commit = parsed[key]
            need(type(commit) is str and len(commit) == 40
                 and all(char in "0123456789abcdef" for char in commit),
                 "reject incomplete frozen or pushed commitment")
        need(parsed["--frozen-commit"] == parsed["--pushed-commit"],
             "reject root materialization before pushing the V2 freeze")
    for key in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if key in parsed:
            checked_hash(parsed[key], key)
    return parsed


def effects(wall: Wall, mode: str) -> dict[str, object]:
    return {"mode": mode, "approved_plaintext_owner_reads": wall.public_reads,
            "candidate_source_files_read": wall.candidate_reads,
            "candidate_executions": 0, "candidate_imports": 0,
            "compiler_processes": 0, "native_libraries_loaded": 0,
            "compressed_archives_opened": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "workspace_mutations": wall.workspace_mutations,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "candidate_qualified": False,
            "winner_selected": False}


def main(argv: list[str]) -> dict[str, object]:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode and sys.executable == PYTHON
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
             "self-test opens no owners or candidates and changes nothing")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "controls": checks, "effects": effects(wall, "SELF-TEST")}

    source_hash = parsed["--source-sha256"]
    protocol_hash = parsed["--protocol-sha256"]
    contract_hash = parsed["--contract-sha256"]
    assert isinstance(source_hash, str) and isinstance(protocol_hash, str)
    assert isinstance(contract_hash, str)
    wall.open_root()
    wall.read(SOURCE, source_hash)
    wall.read(PROTOCOL, protocol_hash)
    manifest = JSON(wall.read(CONTRACT, contract_hash)).parse()
    need(manifest == contract_document(source_hash, protocol_hash),
         "reject weakened or substituted complete V2 source-only contract")
    for path, value in V1_OWNERS:
        wall.read(path, value)
    failure = JSON(wall.read(V1_FAILURE[0], V1_FAILURE[1],
                             V1_FAILURE[2], V1_FAILURE[3])).parse()
    preserve_v1_failure(failure)
    old = JSON(wall.read(C12_LEDGER[0], C12_LEDGER[1],
                         C12_LEDGER[2], C12_LEDGER[3])).parse()
    build = JSON(wall.read(C21_BUILD[0], C21_BUILD[1],
                           C21_BUILD[2], C21_BUILD[3])).parse()
    root = JSON(wall.read(C21_ROOT[0], C21_ROOT[1],
                          C21_ROOT[2], C21_ROOT[3])).parse()
    preserve_c12(old)
    preserve_c21(build, root)
    need(wall.public_reads == 10 and wall.candidate_reads == 0
         and wall.workspace_mutations == 0,
         "authenticate exactly V2, V1, real failure, and historical plaintext owners")
    if not parsed.get("--apply"):
        controls = hostile_controls(wall)
        no_matchers()
        return {"schema": SCHEMA + "-verification", "status": "PASS",
                "source_sha256": source_hash, "protocol_sha256": protocol_hash,
                "contract_sha256": contract_hash,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "preserved_v1_failure_sha256": V1_FAILURE[1],
                "controls": controls,
                "effects": effects(wall, "SOURCE VERIFICATION")}

    preauthorization = root_controls()
    need(type(preauthorization) is dict
         and preauthorization.get("targeted_public_adapter_mismatches") == 330
         and wall.candidate_reads == 0 and wall.workspace_mutations == 0,
         "complete boolean-authenticated root controls before candidate access")
    original = wall.read(INPUT, INPUT_SHA256, INPUT_BYTES, INPUT_INODE)
    result = transform(original, exact=True)
    wall.materialize(result)
    no_matchers()
    need(wall.candidate_reads == 1 and wall.workspace_mutations == 2,
         "materialize exactly one exclusive immutable V2 candidate variant")
    return {"schema": SCHEMA + "-root-materialization", "status": "PASS",
            "frozen_commit": parsed["--frozen-commit"],
            "pushed_commit": parsed["--pushed-commit"],
            "source_sha256": source_hash, "protocol_sha256": protocol_hash,
            "contract_sha256": contract_hash,
            "preserved_v1_failure_sha256": V1_FAILURE[1],
            "input_path": INPUT, "input_sha256": INPUT_SHA256,
            "target_path": TARGET, "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES,
            "targeted_public_adapter_mismatches": 330,
            "root_controls_completed_before_candidate_read": True,
            "effects": effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        answer = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError) as error:
        sys.stderr.write("c-public-adapter-semantics-v2: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(answer) + "\n")
