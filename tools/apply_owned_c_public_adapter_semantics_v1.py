#!/usr/bin/env python3
"""Freeze one independently written correction to the first-party C adapter.

Source verification never reads a candidate, loads native code, opens compressed
evidence, creates a process, observes a clock, or changes the workspace.  Only
the separately authorized coordinator may materialize the predicted adapter
after the three exact frozen owners were committed and pushed.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("first-party C adapter source freeze must not load a matcher")

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
SOURCE = "tools/apply_owned_c_public_adapter_semantics_v1.py"
PROTOCOL = "oracle/phase2/C-PUBLIC-ADAPTER-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/c-public-adapter-semantics-v1.json"
SCHEMA = "rebar-owned-c-public-adapter-semantics-v1-source-freeze"
INPUT = "candidates/vm_candidate.py"
INPUT_SHA256 = "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
INPUT_BYTES = 60707
INPUT_INODE = 428074
TARGET_DIRECTORY = "candidates/c/variants/public_adapter_semantics_v1"
TARGET = TARGET_DIRECTORY + "/vm_candidate.py"
OUTPUT_SHA256 = "4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a"
OUTPUT_BYTES = 61663

C12_LEDGER = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-"
    "c-original-match-semantics-original-p0-v12-failures-publication-receipt.json",
    "a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b",
    10943,
    525645,
)
C21_BUILD = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-publication-receipt.json",
    "9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df",
    11878,
    524817,
)
C21_ROOT = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-root-provenance-receipt.json",
    "8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2",
    10837,
    524818,
)
C21_ENGINE_SHA256 = (
    "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
)
C21_NATIVE_SHA256 = (
    "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60"
)

ORIGINAL_FLAG_CLASS = b'''class RegexFlag(enum.IntFlag):
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

CORRECTED_FLAG_CLASS = b'''class RegexFlag(enum.IntFlag):
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

ORIGINAL_ERROR_CLASS = b"class PatternError(Exception):\n    def __init__(self, msg, pattern=None, pos=None):\n"
CORRECTED_ERROR_CLASS = b"class PatternError(Exception):\n    __module__ = \"re\"\n\n    def __init__(self, msg, pattern=None, pos=None):\n"

ORIGINAL_NATIVE_CONFIGURATION = b"_vm_native.configure(_template, _template_parts)\n"
CORRECTED_NATIVE_CONFIGURATION = (
    b"_vm_native.configure(_template, _template_parts)\n"
    b"RegexFlag.__module__ = \"re\"\n"
)

ORIGINAL_CACHE_DECLARATION = b"_CACHE = {}\n\n\ndef compile(pattern, flags=0):\n"
CORRECTED_CACHE_DECLARATION = (
    b"_CACHE = {}\n_CACHE2 = {}\n_MAXCACHE = 512\n_MAXCACHE2 = 256\n\n\n"
    b"def compile(pattern, flags=0):\n"
)

ORIGINAL_CACHE_LOOKUP = b'''    key = (type(pattern), pattern, flags)
    try:
        return _CACHE[key]
    except KeyError:
        cached = _CACHE.get((type(pattern), pattern, flags))
        if cached is not None:
            return cached
    flags = int(flags)
'''

CORRECTED_CACHE_LOOKUP = b'''    key = (type(pattern), pattern, flags)
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

ORIGINAL_CACHE_STORE = b'''    canonical_pattern = str.__str__(pattern) if isinstance(pattern, str) else bytes(pattern)
    _CACHE[(type(pattern), canonical_pattern, flags)] = result
    if flags & int(DEBUG):
        print(f"AST {node!r}")
    return result
'''

CORRECTED_CACHE_STORE = b'''    if flags & int(DEBUG):
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

ORIGINAL_PURGE = b"def purge():\n    _CACHE.clear()\n"
CORRECTED_PURGE = b"def purge():\n    _CACHE.clear()\n    _CACHE2.clear()\n"

EDITS = (
    ("public RegexFlag representation", ORIGINAL_FLAG_CLASS, CORRECTED_FLAG_CLASS),
    ("public PatternError module", ORIGINAL_ERROR_CLASS, CORRECTED_ERROR_CLASS),
    ("public RegexFlag module after first-party native ownership attestation",
     ORIGINAL_NATIVE_CONFIGURATION, CORRECTED_NATIVE_CONFIGURATION),
    ("bounded first-party cache declarations", ORIGINAL_CACHE_DECLARATION,
     CORRECTED_CACHE_DECLARATION),
    ("FIFO and LRU source-type cache lookup", ORIGINAL_CACHE_LOOKUP,
     CORRECTED_CACHE_LOOKUP),
    ("DEBUG bypass and bounded exact-type cache storage", ORIGINAL_CACHE_STORE,
     CORRECTED_CACHE_STORE),
    ("complete public purge", ORIGINAL_PURGE, CORRECTED_PURGE),
)

PRESERVED = (
    (b"from candidates import _vm_native\n", 1),
    (b"import enum\n", 1),
    (b"from copyreg import _reconstructor as _copy_reconstructor\n", 1),
    (b"class _BytecodeParser:\n", 1),
    (b"class _BytecodeCompiler:\n", 1),
    (b"class Pattern(_vm_native.Pattern, metaclass=_PatternType):\n", 1),
    (b"Match = _vm_native.Match\n", 1),
    (b"_vm_native.configure(_template, _template_parts)\n", 1),
    (b"def compile(pattern, flags=0):\n", 1),
    (b"def purge():\n", 1),
)


class FreezeError(Exception):
    """Reject unsafe effects, drift, invented evidence, or non-owned edits."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def sha256(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only complete first-party owner bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require a complete lowercase SHA-256 for " + label)
    return value


def quoted(value: str) -> str:
    need(type(value) is str, "encode only real text keys")
    replacements = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                    "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for item in value:
        code = ord(item)
        need(not 0xD800 <= code <= 0xDFFF, "reject unpaired JSON surrogate")
        result.append(replacements.get(item, "\\u" + format(code, "04x")
                      if code < 32 else item))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    need(depth < 64, "bound authenticated source-only evidence depth")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return quoted(value)
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1)
                              for item in value) + "]"
    if type(value) is dict:
        need(all(type(key) is str for key in value), "reject nontext JSON keys")
        return "{" + ",".join(quoted(key) + ":" + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported authenticated JSON value")


class StrictJSON:
    """Small duplicate-rejecting JSON reader without importing Python's matcher."""

    def __init__(self, raw: bytes) -> None:
        need(type(raw) is bytes and 0 < len(raw) <= 131072,
             "require bounded immutable plaintext evidence")
        self.text = raw.decode("utf-8", "strict")
        self.index = 0
        self.items = 0

    def space(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        need(self.text[self.index:self.index + 1] == '"', "require JSON text")
        self.index += 1
        value: list[str] = []
        simple = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                  "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(value)
            if char != "\\":
                need(ord(char) >= 32 and not 0xD800 <= ord(char) <= 0xDFFF,
                     "reject malformed authenticated JSON text")
                value.append(char)
                continue
            need(self.index < len(self.text), "reject incomplete JSON escape")
            char = self.text[self.index]
            self.index += 1
            if char != "u":
                need(char in simple, "reject unknown JSON text escape")
                value.append(simple[char])
                continue
            digits = self.text[self.index:self.index + 4]
            need(len(digits) == 4
                 and all(item in "0123456789abcdefABCDEF" for item in digits),
                 "reject malformed Unicode JSON escape")
            self.index += 4
            code = int(digits, 16)
            if 0xD800 <= code <= 0xDBFF:
                need(self.text[self.index:self.index + 2] == "\\u",
                     "reject missing surrogate pair")
                low_digits = self.text[self.index + 2:self.index + 6]
                need(len(low_digits) == 4
                     and all(item in "0123456789abcdefABCDEF"
                             for item in low_digits), "reject malformed low surrogate")
                low = int(low_digits, 16)
                need(0xDC00 <= low <= 0xDFFF, "reject nonpaired low surrogate")
                self.index += 6
                value.append(chr(0x10000 + ((code - 0xD800) << 10)
                                 + low - 0xDC00))
            else:
                need(not 0xDC00 <= code <= 0xDFFF, "reject lone low surrogate")
                value.append(chr(code))
        raise FreezeError("reject unterminated JSON text")

    def value(self, depth: int = 0) -> object:
        need(depth < 64, "bound immutable evidence nesting")
        self.space()
        need(self.index < len(self.text), "reject incomplete JSON document")
        char = self.text[self.index]
        if char == '"':
            return self.string()
        if char == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.space()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.space()
                key = self.string()
                need(key not in result, "reject duplicate immutable JSON key")
                self.items += 1
                need(self.items <= 20000, "reject oversized authenticated evidence")
                self.space()
                need(self.text[self.index:self.index + 1] == ":",
                     "reject missing JSON object colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.space()
                item = self.text[self.index:self.index + 1]
                self.index += 1
                if item == "}":
                    return result
                need(item == ",", "reject malformed immutable JSON object")
        if char == "[":
            self.index += 1
            result_list: list[object] = []
            self.space()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result_list
            while True:
                self.items += 1
                need(self.items <= 20000, "bound immutable evidence array")
                result_list.append(self.value(depth + 1))
                self.space()
                item = self.text[self.index:self.index + 1]
                self.index += 1
                if item == "]":
                    return result_list
                need(item == ",", "reject malformed immutable JSON array")
        if char == "-" or char in "0123456789":
            start = self.index
            if char == "-":
                self.index += 1
            need(self.index < len(self.text), "reject incomplete JSON integer")
            if self.text[self.index] == "0":
                self.index += 1
                need(self.index == len(self.text)
                     or self.text[self.index] not in "0123456789",
                     "reject noncanonical leading-zero integer")
            else:
                need(self.text[self.index] in "123456789",
                     "reject malformed authenticated JSON integer")
                while self.index < len(self.text) and self.text[self.index] in "0123456789":
                    self.index += 1
            need(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                 "reject floating source-only contract numbers")
            literal = self.text[start:self.index]
            need(len(literal) <= 40, "reject oversized immutable JSON integer")
            return int(literal)
        for literal, result in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return result
        raise FreezeError("reject malformed immutable JSON value")

    def decode(self) -> object:
        result = self.value()
        self.space()
        need(self.index == len(self.text), "reject extra immutable JSON bytes")
        return result


def no_matchers() -> None:
    forbidden = (
        "re", "_sre", "regex", "_regex", "pcre", "re2", "rure", "ctypes",
        "candidates", "rebar", "subprocess", "socket", "threading",
        "multiprocessing", "concurrent", "gzip", "zipfile", "tarfile",
    )
    need(not any(name == item or name.startswith(item + ".")
                 for name in sys.modules for item in forbidden),
         "reject candidate, external matcher, native loader, archive, or worker")


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode and sys.executable == PYTHON
         and __file__ == ROOT + "/" + SOURCE,
         "require isolated, bytecode-disabled, pinned CPython 3.14.6")


class Wall:
    """Deny every descriptor and effect except specifically ticketed owners."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.owners = frozenset((SOURCE, PROTOCOL, CONTRACT, C12_LEDGER[0],
                                 C21_BUILD[0], C21_ROOT[0]))
        self.allowed = self.owners | (frozenset((INPUT,)) if apply else frozenset())
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
        self.read_count = 0
        self.candidate_reads = 0
        self.workspace_mutations = 0
        self.rejected = 0
        self.installed = False

    def reject(self, reason: str) -> None:
        self.rejected += 1
        raise FreezeError("first-party C adapter wall rejected " + reason)

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if self.open_ticket == (path, flags):
                return
            self.reject("unticketed descriptor, candidate, archive, or write")
        if event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            if self.mkdir_ticket == (path, mode):
                return
            self.reject("unticketed directory creation")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.rmdir",
                      "os.chmod", "os.chown", "os.urandom", "os.getrandom",
                      "_interpreters.create", "_interpreters.exec",
                      "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.", "time.",
                                     "os.exec", "os.spawn"))):
            self.reject("candidate execution, process, code, network, or clock")

    def denied(self, reason: str):
        def stop(*_values: object, **_keywords: object) -> object:
            self.reject(reason)
        return stop

    def install(self) -> None:
        need(not self.installed, "install first-party descriptor wall exactly once")
        sys.addaudithook(self.audit)
        builtins.open = self.denied("builtins.open")
        _io.open = self.denied("_io.open")
        _io.FileIO = self.denied("_io.FileIO")
        io.open = self.denied("io.open")
        io.FileIO = self.denied("io.FileIO")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                module.open_code = self.denied("open_code")
        for name in ("open", "read", "write", "close", "fstat", "fsync",
                     "mkdir", "fdopen", "dup", "dup2", "stat", "lstat",
                     "readlink", "listdir", "scandir", "walk", "fwalk",
                     "access", "fork", "posix_spawn", "posix_spawnp", "system",
                     "makedirs", "remove", "unlink", "rename", "replace",
                     "rmdir", "chmod", "chown", "urandom", "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.denied("os." + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.denied("clock." + name))
        self.installed = True

    def ticketed(self, path: str, flags: int, mode: int = 0,
                 *, parent: int | None = None) -> int:
        need(self.installed and self.open_ticket is None,
             "reject nested unauthenticated descriptor ticket")
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
        need(self.root is None, "open immutable workspace descriptor once")
        descriptor = self.ticketed(ROOT, self.directory_flags())
        info = self.native_fstat(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE,
             "reject substituted source workspace")
        self.root = descriptor
        self.live[descriptor] = ("", "directory")

    def component(self, value: object) -> str:
        need(type(value) is str and bool(value) and value not in (".", "..")
             and "/" not in value and "\x00" not in value,
             "reject traversal or substituted descriptor component")
        return value

    def child(self, parent: int, value: str) -> int:
        name = self.component(value)
        state = self.live.get(parent)
        need(state is not None and state[1] == "directory",
             "reject non-owned directory descriptor")
        relative = name if not state[0] else state[0] + "/" + name
        permitted = any(owner.startswith(relative + "/") for owner in self.allowed)
        if self.apply:
            permitted = permitted or relative == TARGET_DIRECTORY or TARGET_DIRECTORY.startswith(relative + "/")
        need(permitted and not relative.startswith((".git/", ".agents/", ".codex/")),
             "reject private root, native owner, archive, or unauthorized target")
        descriptor = self.ticketed(name, self.directory_flags(), parent=parent)
        info = self.native_fstat(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE,
             "reject symlink or substituted owner directory")
        self.live[descriptor] = (relative, "directory")
        return descriptor

    def close(self, descriptor: int) -> None:
        need(descriptor in self.live and descriptor != self.root,
             "reject foreign or root descriptor close")
        self.native_close(descriptor)
        del self.live[descriptor]

    def parent(self, relative: str) -> tuple[int, list[int], str]:
        need(relative in self.allowed and self.root is not None,
             "reject candidate source in source verification")
        parts = relative.split("/")
        descriptor = self.root
        opened: list[int] = []
        try:
            for part in parts[:-1]:
                descriptor = self.child(descriptor, part)
                opened.append(descriptor)
            return descriptor, opened, self.component(parts[-1])
        except BaseException:
            for item in reversed(opened):
                self.close(item)
            raise

    def read(self, relative: str, expected_hash: str,
             size: int | None = None, inode: int | None = None) -> bytes:
        need(relative in self.allowed, "deny non-owned immutable source read")
        checked_hash(expected_hash, relative)
        parent, opened, name = self.parent(relative)
        descriptor: int | None = None
        try:
            descriptor = self.ticketed(name, self.file_flags(), parent=parent)
            self.live[descriptor] = (relative, "file")
            before = self.native_fstat(descriptor)
            need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                 and stat.S_IMODE(before.st_mode) == 0o600
                 and before.st_nlink == 1 and before.st_uid == os.geteuid()
                 and 0 < before.st_size <= 262144
                 and (size is None or before.st_size == size)
                 and (inode is None or before.st_ino == inode),
                 "reject substituted immutable owner identity: " + relative)
            pieces: list[bytes] = []
            remaining = before.st_size
            while remaining:
                piece = self.native_read(descriptor, min(remaining, 65536))
                need(type(piece) is bytes and bool(piece), "reject truncated owner")
                pieces.append(piece)
                remaining -= len(piece)
            need(self.native_read(descriptor, 1) == b"", "reject excess owner bytes")
            after = self.native_fstat(descriptor)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "reject owner changed while source freeze was reading")
            data = b"".join(pieces)
            need(sha256(data) == expected_hash, "reject immutable owner digest drift")
            if relative == INPUT:
                self.candidate_reads += 1
            else:
                self.read_count += 1
            return data
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for item in reversed(opened):
                self.close(item)

    def materialize(self, corrected: bytes) -> None:
        need(self.apply and self.root is not None
             and len(corrected) == OUTPUT_BYTES and sha256(corrected) == OUTPUT_SHA256,
             "deny unapproved or substituted first-party adapter materialization")
        parent = self.root
        opened: list[int] = []
        try:
            for part in TARGET_DIRECTORY.split("/")[:-1]:
                parent = self.child(parent, part)
                opened.append(parent)
            name = TARGET_DIRECTORY.rsplit("/", 1)[-1]
            need(self.mkdir_ticket is None, "reject nested directory authorization")
            self.mkdir_ticket = (name, 0o700)
            try:
                self.native_mkdir(name, 0o700, dir_fd=parent)
            finally:
                self.mkdir_ticket = None
            self.workspace_mutations += 1
            self.native_fsync(parent)
            target_parent = self.child(parent, name)
            opened.append(target_parent)
            flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
            descriptor = self.ticketed("vm_candidate.py", flags, 0o600,
                                       parent=target_parent)
            self.live[descriptor] = (TARGET, "target")
            self.workspace_mutations += 1
            try:
                offset = 0
                while offset < len(corrected):
                    written = self.native_write(descriptor, corrected[offset:])
                    need(type(written) is int and written > 0,
                         "reject incomplete immutable adapter write")
                    offset += written
                info = self.native_fstat(descriptor)
                need(stat.S_ISREG(info.st_mode) and info.st_dev == DEVICE
                     and stat.S_IMODE(info.st_mode) == 0o600
                     and info.st_nlink == 1 and info.st_size == OUTPUT_BYTES,
                     "reject substituted exclusive first-party adapter target")
                self.native_fsync(descriptor)
            finally:
                self.close(descriptor)
            self.native_fsync(target_parent)
            readback = self.ticketed("vm_candidate.py", self.file_flags(),
                                     parent=target_parent)
            self.live[readback] = (TARGET, "readback")
            try:
                pieces: list[bytes] = []
                remaining = OUTPUT_BYTES
                while remaining:
                    piece = self.native_read(readback, min(remaining, 65536))
                    need(bool(piece), "reject incomplete durable adapter readback")
                    pieces.append(piece)
                    remaining -= len(piece)
                need(self.native_read(readback, 1) == b""
                     and sha256(b"".join(pieces)) == OUTPUT_SHA256,
                     "reject nonidentical durable adapter materialization")
            finally:
                self.close(readback)
        finally:
            for item in reversed(opened):
                self.close(item)


def transform(raw: bytes, exact: bool = False) -> bytes:
    need(type(raw) is bytes, "transform only complete first-party Python bytes")
    if exact:
        need(len(raw) == INPUT_BYTES and sha256(raw) == INPUT_SHA256,
             "reject substituted canonical first-party C Python adapter")
    previous = -1
    for description, original, _corrected in EDITS:
        need(raw.count(original) == 1, "require one exact owned site: " + description)
        location = raw.index(original)
        need(location > previous, "reject reordered first-party adapter edits")
        previous = location
    for anchor, count in PRESERVED:
        need(raw.count(anchor) == count, "reject missing owned adapter anchor")
    corrected = raw
    for description, original, replacement in EDITS:
        corrected = corrected.replace(original, replacement, 1)
        need(corrected.count(replacement) == 1,
             "reject duplicated corrected first-party adapter site: " + description)
    restored = corrected
    for _description, original, replacement in reversed(EDITS):
        restored = restored.replace(replacement, original, 1)
    need(restored == raw, "reject edits beyond the seven reversible adapter sites")
    delta = sum(len(replacement) - len(original)
                for _description, original, replacement in EDITS)
    need(len(corrected) == len(raw) + delta,
         "reject unowned first-party adapter byte insertion")
    for anchor, count in PRESERVED:
        need(corrected.count(anchor) == count,
             "preserve owned parser, native VM, public types, and replacement compiler")
    for token in (b"import re\n", b"from re import ", b"import regex\n",
                  b"from regex import ", b"import ctypes\n",
                  b"import subprocess\n", b"_sre."):
        need(corrected.count(token) == raw.count(token) == 0,
             "reject borrowed Python matching, external regex, or other engine")
    if exact:
        need(len(corrected) == OUTPUT_BYTES and sha256(corrected) == OUTPUT_SHA256,
             "reject drift in exact frozen first-party adapter successor")
    return corrected


def synthetic_source() -> bytes:
    return b"".join((
        b"import enum\n",
        b"from copyreg import _reconstructor as _copy_reconstructor\n",
        b"from candidates import _vm_native\n",
        ORIGINAL_FLAG_CLASS,
        ORIGINAL_ERROR_CLASS,
        b"        return None\n",
        b"class _BytecodeParser:\n    pass\n",
        b"class _BytecodeCompiler:\n    pass\n",
        b"class Pattern(_vm_native.Pattern, metaclass=_PatternType):\n    pass\n",
        b"Match = _vm_native.Match\n",
        b"_vm_native.configure(_template, _template_parts)\n",
        ORIGINAL_CACHE_DECLARATION,
        ORIGINAL_CACHE_LOOKUP,
        ORIGINAL_CACHE_STORE,
        ORIGINAL_PURGE,
    ))


class WitnessFlag(enum.IntFlag):
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
        pieces = ["re." + name for bit, name in ordered if value & bit]
        unknown = value & ~sum(bit for bit, _name in ordered)
        if unknown:
            if not pieces:
                return "re.RegexFlag(" + repr(value) + ")"
            pieces.append(hex(unknown))
        return "|".join(pieces)

    __str__ = object.__str__


WitnessFlag.__module__ = "re"


class WitnessCache:
    """Independent bounded LRU/FIFO witness; never imports an adapter."""

    def __init__(self, lru_limit: int = 512, fifo_limit: int = 256) -> None:
        self.lru: dict[tuple, object] = {}
        self.fifo: dict[tuple, object] = {}
        self.lru_limit = lru_limit
        self.fifo_limit = fifo_limit
        self.compiles = 0
        self.debug_emissions = 0

    def compile(self, pattern: object, flags: int = 0) -> object:
        key = (type(pattern), pattern, flags)
        try:
            return self.fifo[key]
        except KeyError:
            pass
        cached = self.lru.pop(key, None)
        if cached is None:
            self.compiles += 1
            cached = object()
            if flags & 128:
                self.debug_emissions += 1
                return cached
        if len(self.lru) >= self.lru_limit:
            del self.lru[next(iter(self.lru))]
        self.lru[key] = cached
        if len(self.fifo) >= self.fifo_limit:
            del self.fifo[next(iter(self.fifo))]
        self.fifo[key] = cached
        return cached

    def purge(self) -> None:
        self.lru.clear()
        self.fifo.clear()


def semantic_controls() -> dict[str, object]:
    checks = 0
    need(WitnessFlag.__module__ == "re",
         "publish the owned public RegexFlag type in Python's re module")
    checks += 1
    aliases = (("ASCII", "A", 256), ("IGNORECASE", "I", 2),
               ("LOCALE", "L", 4), ("UNICODE", "U", 32),
               ("MULTILINE", "M", 8), ("DOTALL", "S", 16),
               ("VERBOSE", "X", 64))
    for canonical_name, alias, value in aliases:
        member = getattr(WitnessFlag, canonical_name)
        need(member is getattr(WitnessFlag, alias)
             and int(member) == value
             and member.name == canonical_name,
             "preserve every standard public RegexFlag class alias")
        checks += 1
    need(tuple(WitnessFlag.__members__) == (
        "NOFLAG", "ASCII", "A", "IGNORECASE", "I", "LOCALE", "L",
        "UNICODE", "U", "MULTILINE", "M", "DOTALL", "S", "VERBOSE",
        "X", "DEBUG",
    ), "preserve all CPython public flag aliases and exact member order")
    checks += 1
    flag_expectations = {
        0: "re.NOFLAG",
        2: "re.IGNORECASE",
        4: "re.LOCALE",
        8: "re.MULTILINE",
        16: "re.DOTALL",
        32: "re.UNICODE",
        64: "re.VERBOSE",
        128: "re.DEBUG",
        256: "re.ASCII",
        258: "re.IGNORECASE|re.ASCII",
        10: "re.IGNORECASE|re.MULTILINE",
        1048576: "re.RegexFlag(1048576)",
        1048578: "re.IGNORECASE|0x100000",
        244215808: "re.RegexFlag(244215808)",
        1630208: "re.RegexFlag(1630208)",
        1847296: "re.RegexFlag(1847296)",
    }
    for value, expected in flag_expectations.items():
        member = WitnessFlag(value)
        need(repr(member) == expected and str(member) == expected,
             "preserve exact public IntFlag name, numeric unknown, and bit order")
        checks += 2

    class TextSubclass(str):
        pass

    class BytesSubclass(bytes):
        pass

    witness = WitnessCache()
    for index in range(96):
        kind = TextSubclass if index % 2 == 0 else BytesSubclass
        text = "token-" + str(index)
        value = kind(text if kind is TextSubclass else text.encode("ascii"))
        first = witness.compile(value, index % 4)
        need(witness.compile(value, index % 4) is first,
             "retain exact subclass type and object in first-party cache key")
        plain = str(value) if kind is TextSubclass else bytes(value)
        need(witness.compile(plain, index % 4) is not first,
             "never conflate builtins with their public pattern subclasses")
        checks += 2

    debug = WitnessCache()
    for index in range(8):
        first = debug.compile("debug-" + str(index), 128)
        second = debug.compile("debug-" + str(index), 128)
        need(first is not second and not debug.lru and not debug.fifo,
             "compile DEBUG independently without caching or suppressing output")
        checks += 1
    need(debug.debug_emissions == 16,
         "emit both genuine public DEBUG compilations for every witness")
    checks += 1

    evictions = WitnessCache()
    retained = evictions.compile("first")
    for ordinal in range(512):
        evictions.compile("later-" + str(ordinal))
    need(len(evictions.lru) == 512 and len(evictions.fifo) == 256
         and evictions.compile("first") is not retained,
         "preserve CPython 512-entry LRU and 256-entry FIFO eviction")
    checks += 1
    identity = evictions.compile("purge-me")
    evictions.purge()
    need(not evictions.lru and not evictions.fifo
         and evictions.compile("purge-me") is not identity,
         "public purge clears both independently owned compile caches")
    checks += 1

    modeled = {
        "pattern_error_module": 96,
        "subclass_cache_identity": 96,
        "public_types_unknown_flag_repr": 12,
        "pattern_flag_repr_order": 12,
        "surface_unknown_flag_repr": 96,
        "debug_cache_bypass": 8,
        "bounded_cache_eviction": 10,
    }
    need(sum(modeled.values()) == 330,
         "retain all 330 witnessed disjoint public adapter mismatches")
    return {"semantic_checks": checks,
            "exact_modeled_public_adapter_mismatches": 330,
            "modeled_failure_partition": modeled,
            "additional_public_class_alias_obligations": len(aliases),
            "additional_public_flag_module_obligations": 1,
            "remaining_match_pickle_mismatches": 32,
            "original_denominator": 31237}


def hostile_controls(wall: Wall) -> dict[str, object]:
    controls = 0

    def refuses(action: object, label: str) -> None:
        nonlocal controls
        denied = False
        try:
            action()
        except (FreezeError, OSError, ValueError, TypeError):
            denied = True
        need(denied, "accept forbidden first-party source effect: " + label)
        controls += 1

    source = synthetic_source()
    corrected = transform(source)
    need(corrected and corrected != source,
         "require synthetic owned adapter correction without execution")
    controls += 1
    for description, original, replacement in EDITS:
        refuses(lambda raw=original: transform(source.replace(raw, b"", 1)),
                "missing " + description)
        refuses(lambda raw=original: transform(source + raw),
                "duplicated " + description)
        need(corrected.count(replacement) == 1,
             "retain exactly one reversible corrected adapter owner")
        controls += 1
    for forbidden in (
        lambda: builtins.open(INPUT, "rb"),
        lambda: _io.open(INPUT, "rb"),
        lambda: io.open(INPUT, "rb"),
        lambda: os.open(INPUT, os.O_RDONLY),
        lambda: os.stat(INPUT),
        lambda: os.listdir(ROOT),
        lambda: os.mkdir("unauthorized-owned-adapter"),
        lambda: time.time(),
        lambda: time.perf_counter_ns(),
    ):
        refuses(forbidden, "physical side effect")
    checks = semantic_controls()
    controls += checks["semantic_checks"]
    no_matchers()
    return {"hostile_controls": controls, "semantic": checks}


def authenticate_c12(document: object) -> None:
    need(type(document) is dict, "require complete immutable C12 publication")
    expected = {
        "schema": "rebar-owned-repaired-c-original-campaign-v12-durable-publication-receipt",
        "version": 12,
        "family": "c",
        "status": "PASS",
        "publication_status": "PASS",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "completed_suite_count": 12,
        "verified_passing_case_count": 16413,
        "complete_observed_semantic_mismatch_record_count": 606,
        "all_observed_semantic_mismatch_records_preserved": True,
        "candidate_execution_failure_count": 1,
        "semantic_mismatch_count": "NOT MEASURED",
        "unchanged_adapter_sha256": INPUT_SHA256,
        "corrected_source_sha256": C21_ENGINE_SHA256,
        "native_engine_sha256": C21_NATIVE_SHA256,
        "winner_selected": False,
    }
    for key, value in expected.items():
        need(document.get(key) == value,
             "preserve authentic failed C12 evidence: " + key)
    outcomes = document.get("suite_outcomes")
    need(type(outcomes) is list and len(outcomes) == 13,
         "retain every frozen C original-suite outcome")
    counts = {item["suite"]: item["mismatch_count"] for item in outcomes}
    for suite, expected_count in (("managed_v1", 16), ("public_types_v1", 248),
                                  ("substitution_v2", 224),
                                  ("public_surface_v19", 114), ("pep688_v4", 4)):
        need(counts.get(suite) == expected_count,
             "preserve complete C12 failure partition: " + suite)
    need(counts.get("subinterpreter_v2") == "NOT MEASURED",
         "never claim unfinished interpreter isolation was repaired")


def authenticate_c21(build: object, root: object) -> None:
    need(type(build) is dict and type(root) is dict,
         "require both authentic published first-party C21 owners")
    need(build.get("family") == "c" and build.get("version") == 21
         and build.get("build_status") == "PASS"
         and build.get("adapter_source_sha256") == INPUT_SHA256
         and build.get("variant_source_sha256") == C21_ENGINE_SHA256
         and build.get("candidate_correctness") == "NOT MEASURED"
         and build.get("candidate_matching") == "NOT RUN"
         and build.get("byte_identical_native_artifacts") is True,
         "reject substituted, delegated, or falsely qualified C21 build")
    phases = build.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "preserve both independent first-party C21 source builds")
    for phase in phases:
        sources = phase.get("source_owners")
        need(type(sources) is list and len(sources) == 2
             and sources[0].get("sha256") == C21_ENGINE_SHA256
             and sources[0].get("bytes") == 221647
             and sources[1].get("sha256") == INPUT_SHA256
             and sources[1].get("bytes") == INPUT_BYTES
             and phase.get("native_output", {}).get("sha256") == C21_NATIVE_SHA256,
             "reject unauthenticated C21 engine, adapter, or native owner")
    need(root.get("family") == "c" and root.get("status") == "PASS"
         and root.get("derived_variant_sha256") == C21_ENGINE_SHA256
         and root.get("canonical_build_receipt_sha256") == C21_BUILD[1]
         and root.get("candidate_correctness") == "NOT MEASURED",
         "reject substituted published C21 private-root provenance")


def document(source_hash: str, protocol_hash: str) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "phase": "CANDIDATES; SOURCE-ONLY FIRST-PARTY C ADAPTER CORRECTION",
        "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
        "source": {"path": SOURCE, "sha256": source_hash},
        "protocol": {"path": PROTOCOL, "sha256": protocol_hash},
        "canonical_input": {"path": INPUT, "sha256": INPUT_SHA256,
                            "bytes": INPUT_BYTES, "device": DEVICE,
                            "inode": INPUT_INODE, "mode": "0600"},
        "immutable_c12_failure_ledger": {"path": C12_LEDGER[0],
                                         "sha256": C12_LEDGER[1],
                                         "bytes": C12_LEDGER[2],
                                         "inode": C12_LEDGER[3],
                                         "case_execution_denominator": 31237,
                                         "completed_suite_count": 12,
                                         "verified_passing_case_count": 16413,
                                         "observed_mismatch_count": 606,
                                         "candidate_status": "FAIL",
                                         "exact_total_mismatch_count": "NOT MEASURED",
                                         "unfinished_interpreter_isolation": True},
        "immutable_first_party_c21": {"build_receipt_path": C21_BUILD[0],
                                      "build_receipt_sha256": C21_BUILD[1],
                                      "root_receipt_path": C21_ROOT[0],
                                      "root_receipt_sha256": C21_ROOT[1],
                                      "native_source_sha256": C21_ENGINE_SHA256,
                                      "native_artifact_sha256": C21_NATIVE_SHA256,
                                      "independent_build_count": 2,
                                      "candidate_correctness": "NOT MEASURED"},
        "correction": {
            "family": "c",
            "site_count": len(EDITS),
            "sites": [item[0] for item in EDITS],
            "output_path": TARGET,
            "output_sha256": OUTPUT_SHA256,
            "output_bytes": OUTPUT_BYTES,
            "exact_targeted_public_adapter_mismatch_count": 330,
            "public_types_adapter_mismatch_count": 216,
            "public_surface_adapter_mismatch_count": 114,
            "pattern_error_module_count": 96,
            "subclass_cache_identity_count": 96,
            "unknown_flag_representation_count": 108,
            "pattern_flag_order_representation_count": 12,
            "debug_cache_bypass_count": 8,
            "bounded_cache_eviction_count": 10,
            "additional_public_class_alias_count": 7,
            "additional_public_regex_flag_module_count": 1,
            "preserved_native_match_pickle_mismatch_count": 32,
            "lru_capacity": 512,
            "fifo_capacity": 256,
            "production_stdlib_matching_delegation": False,
            "external_regular_expression_engine": False,
            "cross_candidate_engine": False,
        },
        "physical_source_wall": {
            "installed_before_owner_reads": True,
            "source_mode_candidate_reads": 0,
            "source_mode_workspace_mutations": 0,
            "source_mode_native_opens": 0,
            "source_mode_archive_opens": 0,
            "source_mode_processes": 0,
            "source_mode_clock_samples": 0,
            "authorized_plaintext_evidence_receipt_count": 3,
            "apply_requires_root_authorization": True,
            "apply_requires_identical_frozen_pushed_commit": True,
            "apply_exclusive_target_only": True,
        },
        "source_only_effects": {
            "candidate_source_files_read": 0,
            "candidate_imports": 0,
            "candidate_executions": 0,
            "compiler_processes_started": 0,
            "native_binary_files_opened": 0,
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


def options(values: list[str]) -> dict[str, object]:
    flags = {"--self-test", "--verify-source", "--apply", "--root-authorized"}
    arguments = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
                 "--frozen-commit", "--pushed-commit"}
    result: dict[str, object] = {}
    at = 0
    while at < len(values):
        name = values[at]
        need(name in flags or name in arguments and name not in result,
             "reject missing, repeated, or unauthorized option: " + name)
        if name in flags:
            need(name not in result, "reject duplicated source mode")
            result[name] = True
            at += 1
        else:
            need(at + 1 < len(values), "reject incomplete source owner digest")
            result[name] = values[at + 1]
            at += 2
    modes = [name for name in ("--self-test", "--verify-source", "--apply")
             if result.get(name)]
    need(len(modes) == 1, "require one self-test, verification, or root materialization")
    mode = modes[0]
    if mode == "--self-test":
        need(set(result) == {mode}, "self-test may not access owner paths")
    elif mode == "--verify-source":
        need(set(result) == {mode, "--source-sha256", "--protocol-sha256",
                             "--contract-sha256"},
             "source verification requires exactly the frozen owner triple")
    else:
        need(set(result) == {mode, "--root-authorized", "--source-sha256",
                             "--protocol-sha256", "--contract-sha256",
                             "--frozen-commit", "--pushed-commit"},
             "exclusive materialization requires explicit pushed root authorization")
        for key in ("--frozen-commit", "--pushed-commit"):
            commit = result[key]
            need(type(commit) is str and len(commit) == 40
                 and all(char in "0123456789abcdef" for char in commit),
                 "require complete lowercase pushed freeze commitment")
        need(result["--frozen-commit"] == result["--pushed-commit"],
             "reject materialization before the exact source freeze was pushed")
    for key in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if key in result:
            checked_hash(result[key], key)
    return result


def effects(wall: Wall, mode: str) -> dict[str, object]:
    return {"mode": mode,
            "approved_plaintext_owner_reads": wall.read_count,
            "candidate_source_files_read": wall.candidate_reads,
            "candidate_executions": 0,
            "candidate_imports": 0,
            "native_binary_files_opened": 0,
            "compressed_archives_opened": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "workspace_mutations": wall.workspace_mutations,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False}


def main(arguments: list[str]) -> dict[str, object]:
    runtime()
    parsed = options(arguments)
    apply = parsed.get("--apply") is True
    wall = Wall(apply)
    no_matchers()
    wall.install()

    if parsed.get("--self-test"):
        controls = hostile_controls(wall)
        need(wall.read_count == 0 and wall.candidate_reads == 0
             and wall.workspace_mutations == 0 and wall.root is None,
             "self-test never reads owners, candidates, or private roots")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "controls": controls, "effects": effects(wall, "SELF-TEST")}

    source_hash = parsed["--source-sha256"]
    protocol_hash = parsed["--protocol-sha256"]
    contract_hash = parsed["--contract-sha256"]
    assert isinstance(source_hash, str) and isinstance(protocol_hash, str)
    assert isinstance(contract_hash, str)
    wall.open_root()
    wall.read(SOURCE, source_hash)
    wall.read(PROTOCOL, protocol_hash)
    actual_contract = StrictJSON(wall.read(CONTRACT, contract_hash)).decode()
    expected_contract = document(source_hash, protocol_hash)
    need(actual_contract == expected_contract,
         "reject noncanonical, substituted, or weakened first-party source contract")
    ledger = StrictJSON(wall.read(C12_LEDGER[0], C12_LEDGER[1],
                                 C12_LEDGER[2], C12_LEDGER[3])).decode()
    build = StrictJSON(wall.read(C21_BUILD[0], C21_BUILD[1],
                                C21_BUILD[2], C21_BUILD[3])).decode()
    root = StrictJSON(wall.read(C21_ROOT[0], C21_ROOT[1],
                               C21_ROOT[2], C21_ROOT[3])).decode()
    authenticate_c12(ledger)
    authenticate_c21(build, root)
    need(wall.read_count == 6 and wall.candidate_reads == 0
         and wall.workspace_mutations == 0,
         "verify only frozen owners and three historical plaintext receipts")

    if not apply:
        controls = hostile_controls(wall)
        no_matchers()
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; SOURCE FROZEN; CANDIDATE NOT READ OR RUN",
                "source_sha256": source_hash,
                "protocol_sha256": protocol_hash,
                "contract_sha256": contract_hash,
                "predicted_target_path": TARGET,
                "predicted_target_sha256": OUTPUT_SHA256,
                "predicted_target_bytes": OUTPUT_BYTES,
                "controls": controls,
                "effects": effects(wall, "SOURCE VERIFICATION")}

    need(semantic_controls() and transform(synthetic_source()),
         "require complete independent controls before root-only candidate access")
    original = wall.read(INPUT, INPUT_SHA256, INPUT_BYTES, INPUT_INODE)
    corrected = transform(original, exact=True)
    wall.materialize(corrected)
    no_matchers()
    need(wall.candidate_reads == 1 and wall.workspace_mutations == 2,
         "create exactly one exclusive directory and immutable adapter file")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; FIRST-PARTY ADAPTER VARIANT; NOT BUILT; NOT RUN",
            "frozen_commit": parsed["--frozen-commit"],
            "pushed_commit": parsed["--pushed-commit"],
            "source_sha256": source_hash,
            "protocol_sha256": protocol_hash,
            "contract_sha256": contract_hash,
            "input_path": INPUT,
            "input_sha256": INPUT_SHA256,
            "target_path": TARGET,
            "target_sha256": OUTPUT_SHA256,
            "target_bytes": OUTPUT_BYTES,
            "exact_modeled_public_adapter_mismatch_count": 330,
            "effects": effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        result = main(sys.argv[1:])
    except (FreezeError, OSError, ValueError, UnicodeError) as error:
        sys.stderr.write("c-public-adapter-semantics-v1: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(result) + "\n")
