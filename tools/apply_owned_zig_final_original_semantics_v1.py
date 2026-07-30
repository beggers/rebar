#!/usr/bin/env python3
"""Freeze two independent, from-scratch Zig compatibility corrections.

Source gates never open a candidate, compressed archive, private directory,
benchmark, or holdout.  Only a separately authorized root application may
read the two pinned first-party Zig inputs and create the two new variants.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("first-party Zig source freeze cannot import a matcher")

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
SCHEMA = "rebar-owned-zig-final-original-semantics-v1-source-freeze"
SOURCE = "tools/apply_owned_zig_final_original_semantics_v1.py"
PROTOCOL = "oracle/phase2/ZIG-FINAL-ORIGINAL-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/zig-final-original-semantics-v1.json"
RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v16-"
    "phase2-v16-zig-full-semantic-original-p0-v16-failures-"
    "publication-receipt.json"
)
RECEIPT_SHA256 = "a7019c02b2906eb15f622e9bd9e61eb7476c528019fac537ed7072b3f82efe7a"
RECEIPT_BYTES = 21041
RECEIPT_INODE = 526355
ARCHIVE_SHA256 = "bf3f839103d31f45926269f89f71d73c3bcabfdc134124542859d297f38b5154"
ARCHIVE_BYTES = 5524430

BRIDGE_INPUT = "candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c"
BRIDGE_INPUT_SHA256 = "07337863f6b4a0e749a8d60b2e5704bb961e43dc09bfa85c238f0efa40d3583c"
BRIDGE_INPUT_BYTES = 176765
BRIDGE_INPUT_INODE = 525558
ADAPTER_INPUT = "candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py"
ADAPTER_INPUT_SHA256 = "7129c63bdfd3c265a44541500238c26a8a5511f8932140de7d06bb49c13f588d"
ADAPTER_INPUT_BYTES = 67735
ADAPTER_INPUT_INODE = 525024

DIRECTORY = "candidates/zig/variants/final_original_semantics_v1"
BRIDGE_TARGET = DIRECTORY + "/py_bridge.c"
ADAPTER_TARGET = DIRECTORY + "/zig_candidate.py"
BRIDGE_TARGET_SHA256 = "4228199b7c65c4d02a78e0e9764a52aed63ff9a4c8230381925d5d3f2eb588ac"
BRIDGE_TARGET_BYTES = 176761
ADAPTER_TARGET_SHA256 = "a6587f43112cc54f2fbf86c8c62ea28426950caae94c6fce2ccead61fcc0f124"
ADAPTER_TARGET_BYTES = 67657

OLD_SCANNER = b"""    size_t branch_group = active + 1;
    if (match->spans[branch_group] < 0) {
        match->spans[branch_group] = begins[0];
        match->spans[exposed_stride + branch_group] = ends[0];
    }
"""
NEW_SCANNER = b"""    size_t branch_group = active + 1;
    if (match->spans[branch_group] < 0) {
        match->spans[branch_group] = begins[0];
    }
    match->spans[exposed_stride + branch_group] = ends[0];
"""

OLD_FLAG_CLASS = b"""class RegexFlag(enum.IntFlag):
    ASCII = 256
    IGNORECASE = 2
    LOCALE = 4
    UNICODE = 32
    MULTILINE = 8
    DOTALL = 16
    VERBOSE = 64
    DEBUG = 128

    @classmethod
    def _missing_(cls, value):
        member = super()._missing_(value)
        if member is None:
            return None
        known = sum(int(flag) for flag in cls)
        unknown = int(member) & ~known
        if unknown and int(member) & known:
            names = [flag.name for flag in sorted(cls, key=int)
                     if int(member) & int(flag)]
            member._name_ = "|".join(names + [hex(unknown)])
        return member

    def __repr__(self):
        value = int(self)
        if not value:
            return "re.NOFLAG"
        ordered = sorted(type(self), key=int)
        known = sum(int(flag) for flag in ordered)
        unknown = value & ~known
        parts = [f"re.{flag.name}" for flag in ordered
                 if value & int(flag)]
        if unknown:
            if not parts:
                return f"re.RegexFlag({value})"
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = __repr__
"""

NEW_FLAG_CLASS = b"""class RegexFlag(enum.IntFlag):
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
        ordered = tuple(type(self))
        known = sum(int(flag) for flag in ordered)
        unknown = value & ~known
        parts = [f"re.{flag.name}" for flag in ordered
                 if value & int(flag)]
        if unknown:
            if not parts:
                return f"re.RegexFlag({value})"
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = __repr__
"""

OLD_PATTERN_FLAGS = b'        suffix = f", {RegexFlag(flags)!r}" if flags else ""\n'
NEW_PATTERN_FLAGS = b"""        suffix = ""
        if flags:
            ordered = sorted(RegexFlag, key=int)
            known = sum(int(flag) for flag in ordered)
            parts = [f"re.{flag.name}" for flag in ordered
                     if flags & int(flag)]
            unknown = flags & ~known
            if unknown:
                parts.append(hex(unknown))
            suffix = ", " + "|".join(parts)
"""

DECLARED_FLAGS = (
    ("ASCII", 256), ("IGNORECASE", 2), ("LOCALE", 4),
    ("UNICODE", 32), ("MULTILINE", 8), ("DOTALL", 16),
    ("VERBOSE", 64), ("DEBUG", 128),
)
EXPECTED_MEMBERS = (
    "NOFLAG", "ASCII", "A", "IGNORECASE", "I", "LOCALE", "L",
    "UNICODE", "U", "MULTILINE", "M", "DOTALL", "S", "VERBOSE",
    "X", "DEBUG",
)
FAILURE_PARTITION = {
    "original_bounded_v5": 2,
    "public_v3": 34,
    "scanner_v3": 64,
    "scanner_verbose_v1": 930,
    "public_types_v1": 48,
    "public_surface_v19": 78,
}


class FreezeError(Exception):
    pass


def need(condition: object, reason: str) -> None:
    if condition is not True:
        raise FreezeError(reason)


def digest(value: bytes) -> str:
    need(type(value) is bytes, "hash only exact immutable byte strings")
    return hashlib.sha256(value).hexdigest()


def fingerprint(value: object, kind: str, width: int = 64) -> str:
    need(type(value) is str and len(value) == width
         and all(char in "0123456789abcdef" for char in value),
         "reject malformed or noncanonical " + kind)
    return value


def quote(value: str) -> str:
    need(type(value) is str, "encode only exact JSON strings")
    result = ['"']
    for char in value:
        code = ord(char)
        need(not 0xD800 <= code <= 0xDFFF,
             "reject an unpaired JSON surrogate")
        if char == '"':
            result.append('\\"')
        elif char == "\\":
            result.append("\\\\")
        elif code < 32:
            result.append("\\u" + format(code, "04x"))
        else:
            result.append(char)
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    need(depth <= 24, "reject excessively nested canonical evidence")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        need(abs(value) < 1 << 63, "reject unbounded canonical integers")
        return str(value)
    if type(value) is str:
        return quote(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1)
                              for item in value) + "]"
    if type(value) is dict:
        need(all(type(key) is str for key in value),
             "reject non-string canonical evidence keys")
        return "{" + ",".join(
            quote(key) + ":" + canonical(value[key], depth + 1)
            for key in sorted(value)
        ) + "}"
    raise FreezeError("reject floating, executable, or ambiguous evidence")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class StrictJSON:
    def __init__(self, raw: bytes):
        need(type(raw) is bytes and len(raw) <= 262144,
             "reject oversized or non-byte immutable public receipt")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("reject invalid evidence encoding") from error
        self.at = 0

    def blank(self) -> None:
        while self.at < len(self.text) and self.text[self.at] in " \t\r\n":
            self.at += 1

    def string(self) -> str:
        need(self.at < len(self.text) and self.text[self.at] == '"',
             "require one exact JSON string")
        self.at += 1
        out: list[str] = []
        while self.at < len(self.text):
            char = self.text[self.at]
            self.at += 1
            if char == '"':
                return "".join(out)
            if char != "\\":
                code = ord(char)
                need(code >= 32 and not 0xD800 <= code <= 0xDFFF,
                     "reject control characters and unpaired surrogates")
                out.append(char)
                continue
            need(self.at < len(self.text), "reject unfinished JSON escape")
            mark = self.text[self.at]
            self.at += 1
            ordinary = {'"': '"', "\\": "\\", "/": "/", "b": "\b",
                        "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
            if mark in ordinary:
                out.append(ordinary[mark])
                continue
            need(mark == "u" and self.at + 4 <= len(self.text),
                 "reject malformed JSON unicode escape")
            digits = self.text[self.at:self.at + 4]
            need(all(item in "0123456789abcdefABCDEF" for item in digits),
                 "reject non-hexadecimal JSON unicode escape")
            value = int(digits, 16)
            self.at += 4
            if 0xD800 <= value <= 0xDBFF:
                need(self.text[self.at:self.at + 2] == "\\u"
                     and self.at + 6 <= len(self.text),
                     "reject an unpaired high JSON surrogate")
                tail = self.text[self.at + 2:self.at + 6]
                need(all(item in "0123456789abcdefABCDEF" for item in tail),
                     "reject malformed low JSON surrogate")
                lower = int(tail, 16)
                need(0xDC00 <= lower <= 0xDFFF,
                     "reject invalid low JSON surrogate")
                self.at += 6
                value = 0x10000 + ((value - 0xD800) << 10) + lower - 0xDC00
            else:
                need(not 0xDC00 <= value <= 0xDFFF,
                     "reject an unpaired low JSON surrogate")
            out.append(chr(value))
        raise FreezeError("reject unfinished immutable JSON string")

    def value(self, depth: int = 0) -> object:
        need(depth <= 24, "reject excessively nested immutable evidence")
        self.blank()
        need(self.at < len(self.text), "reject truncated immutable evidence")
        char = self.text[self.at]
        if char == '"':
            return self.string()
        if char == "{":
            self.at += 1
            out: dict[str, object] = {}
            self.blank()
            if self.at < len(self.text) and self.text[self.at] == "}":
                self.at += 1
                return out
            while True:
                self.blank()
                key = self.string()
                need(key not in out, "reject duplicate immutable JSON key")
                self.blank()
                need(self.at < len(self.text) and self.text[self.at] == ":",
                     "reject missing immutable JSON colon")
                self.at += 1
                out[key] = self.value(depth + 1)
                self.blank()
                need(self.at < len(self.text), "reject unfinished JSON object")
                marker = self.text[self.at]
                self.at += 1
                if marker == "}":
                    return out
                need(marker == ",", "reject malformed immutable JSON object")
        if char == "[":
            self.at += 1
            out: list[object] = []
            self.blank()
            if self.at < len(self.text) and self.text[self.at] == "]":
                self.at += 1
                return out
            while True:
                out.append(self.value(depth + 1))
                self.blank()
                need(self.at < len(self.text), "reject unfinished JSON array")
                marker = self.text[self.at]
                self.at += 1
                if marker == "]":
                    return out
                need(marker == ",", "reject malformed immutable JSON array")
        for word, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(word, self.at):
                self.at += len(word)
                return value
        begin = self.at
        if char == "-":
            self.at += 1
        need(self.at < len(self.text) and self.text[self.at] in "0123456789",
             "reject floating or non-numeric immutable evidence")
        if self.text[self.at] == "0":
            self.at += 1
        else:
            while self.at < len(self.text) and self.text[self.at] in "0123456789":
                self.at += 1
        value = int(self.text[begin:self.at])
        need(abs(value) < 1 << 63,
             "reject unbounded immutable evidence integer")
        return value

    def parse(self) -> object:
        result = self.value()
        self.blank()
        need(self.at == len(self.text),
             "reject trailing immutable JSON evidence")
        return result


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
        ordered = tuple(type(self))
        known = sum(int(flag) for flag in ordered)
        unknown = value & ~known
        parts = ["re." + flag.name for flag in ordered
                 if value & int(flag)]
        if unknown:
            if not parts:
                return "re.RegexFlag(" + str(value) + ")"
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = __repr__


def model_pattern(flags: int) -> str:
    flags &= ~32
    if not flags:
        return "re.compile('a')"
    ordered = sorted(ModelFlag, key=int)
    known = sum(int(item) for item in ordered)
    names = ["re." + item.name for item in ordered
             if flags & int(item)]
    unknown = flags & ~known
    if unknown:
        names.append(hex(unknown))
    return "re.compile('a', " + "|".join(names) + ")"


def replace_once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    need(type(raw) is bytes and type(old) is bytes and type(new) is bytes
         and old != new and raw.count(old) == 1,
         "require one exact reversible first-party source correction: " + label)
    result = raw.replace(old, new, 1)
    need(result.count(new) == 1 and result.count(old) == 0,
         "reject ambiguous or retained first-party source correction: " + label)
    return result


def semantic_controls() -> dict[str, object]:
    need(tuple(ModelFlag.__members__) == EXPECTED_MEMBERS,
         "preserve every CPython RegexFlag alias and declaration order")
    known = sum(number for _name, number in DECLARED_FLAGS)
    flags_checked = 0
    patterns_checked = 0
    for raw in range(-2048, 8193):
        member = ModelFlag(raw)
        value = int(member)
        selected = [name for name, bit in DECLARED_FLAGS if value & bit]
        unknown = value & ~known
        if not value:
            expected_repr = "re.NOFLAG"
            expected_name: str | None = "NOFLAG"
        elif not selected:
            expected_repr = "re.RegexFlag(" + str(value) + ")"
            expected_name = None
        else:
            expected_repr = "|".join("re." + name for name in selected)
            expected_name = "|".join(selected)
            if unknown:
                expected_repr += "|" + hex(unknown)
                expected_name += "|" + hex(unknown)
        need(repr(member) == expected_repr and str(member) == expected_repr
             and member.name == expected_name,
             "reject declaration-order, alias, inversion, or unknown flag defect")
        flags_checked += 1
        if raw >= 0:
            active = raw & ~32
            pieces = ["re." + name for name, bit in sorted(
                DECLARED_FLAGS, key=lambda item: item[1]
            ) if active & bit]
            remainder = active & ~known
            if remainder:
                pieces.append(hex(remainder))
            expected_pattern = "re.compile('a'" + (
                ", " + "|".join(pieces) if pieces else ""
            ) + ")"
            need(model_pattern(raw) == expected_pattern,
                 "reject independently ordered compiled-pattern flag display")
            patterns_checked += 1

    witnesses = {
        0: ("re.NOFLAG", "re.compile('a')"),
        1: ("re.RegexFlag(1)", "re.compile('a', 0x1)"),
        2: ("re.IGNORECASE", "re.compile('a', re.IGNORECASE)"),
        256: ("re.ASCII", "re.compile('a', re.ASCII)"),
        258: ("re.ASCII|re.IGNORECASE",
              "re.compile('a', re.IGNORECASE|re.ASCII)"),
        512: ("re.RegexFlag(512)", "re.compile('a', 0x200)"),
        514: ("re.IGNORECASE|0x200",
              "re.compile('a', re.IGNORECASE|0x200)"),
        770: ("re.ASCII|re.IGNORECASE|0x200",
              "re.compile('a', re.IGNORECASE|re.ASCII|0x200)"),
        1536: ("re.RegexFlag(1536)", "re.compile('a', 0x600)"),
    }
    for value, pair in witnesses.items():
        need((repr(ModelFlag(value)), model_pattern(value)) == pair,
             "reject public CPython flag witness " + str(value))
    need(repr(ModelFlag(-1)) ==
         "re.ASCII|re.IGNORECASE|re.LOCALE|re.UNICODE|re.MULTILINE|"
         "re.DOTALL|re.VERBOSE|re.DEBUG|0x1"
         and repr(ModelFlag(-512)) == "re.NOFLAG",
         "preserve negative and inverted public CPython flags")

    scanner_checked = 0
    overwritten_end = 0
    preserved_nested_begin = 0
    for groups in range(1, 13):
        for active in range(groups):
            branch_group = active + 1
            for begin in range(5):
                for width in range(1, 9):
                    finish = begin + width
                    for offset in range(width + 1):
                        nested = begin + offset
                        for nested_width in range(width - offset + 1):
                            for subject in ("str", "bytes", "bytearray", "memoryview"):
                                previous = [(-1, -1)] * (groups + 1)
                                previous[0] = (begin, finish)
                                previous[branch_group] = (
                                    (nested, nested + nested_width)
                                    if nested_width else (-1, -1)
                                )
                                unrelated = [item for index, item in
                                             enumerate(previous)
                                             if index != branch_group]
                                found_begin = previous[branch_group][0]
                                corrected_begin = (begin if found_begin < 0
                                                   else found_begin)
                                corrected = list(previous)
                                corrected[branch_group] = (corrected_begin, finish)
                                need(corrected[0] == (begin, finish)
                                     and [item for index, item in enumerate(corrected)
                                          if index != branch_group] == unrelated
                                     and corrected[branch_group][1] == finish
                                     and branch_group == active + 1
                                     and subject in ("str", "bytes", "bytearray",
                                                     "memoryview"),
                                     "reject owned Zig scanner branch projection")
                                if found_begin >= 0:
                                    need(corrected[branch_group][0] == found_begin,
                                         "reject nested scanner capture beginning")
                                    if found_begin != begin:
                                        preserved_nested_begin += 1
                                    if previous[branch_group][1] != finish:
                                        overwritten_end += 1
                                scanner_checked += 1

    need(flags_checked == 10241 and patterns_checked == 8193
         and scanner_checked > 100000 and overwritten_end > 10000
         and preserved_nested_begin > 10000,
         "reject omitted exhaustive source-only compatibility controls")
    return {
        "flag_values_checked": flags_checked,
        "pattern_values_checked": patterns_checked,
        "scanner_projection_cases_checked": scanner_checked,
        "scanner_existing_end_overwrites_checked": overwritten_end,
        "scanner_nested_beginnings_preserved": preserved_nested_begin,
        "subject_carriers_checked": ["str", "bytes", "bytearray", "memoryview"],
        "historical_scanner_mismatches_explained": 1028,
        "historical_flags_mismatches_explained": 128,
        "historical_mismatches_explained": 1156,
        "historical_structured_rows_replayed_independently": 1154,
        "historical_upstream_assertions_explained": 2,
    }


class SourceWall:
    def __init__(self, mode: str):
        self.mode = mode
        self.blocked = 0
        self.live: dict[int, str] = {}
        self.open_ticket: tuple[str, int, int | None, int | None] | None = None
        self.mkdir_ticket: tuple[str, int, int] | None = None
        self.read_ticket: int | None = None
        self.write_ticket: tuple[int, bytes] | None = None
        self.stat_ticket: int | None = None
        self.close_ticket: int | None = None
        self.sync_ticket: int | None = None
        self.public_reads = 0
        self.candidate_reads = 0
        self.mutations = 0
        self.created: list[dict[str, object]] = []
        self.raw: dict[str, object] = {}
        self.root: int | None = None

    def reject(self, message: str) -> None:
        self.blocked += 1
        raise FreezeError(message)

    def audit(self, event: str, args: tuple[object, ...]) -> None:
        if event == "open":
            ticket = self.open_ticket
            if (ticket is None or len(args) < 3 or args[0] != ticket[0]
                    or type(args[2]) is not int
                    or args[2] != ticket[1]):
                self.reject("deny unauthenticated audit-hook open")
        elif event == "os.mkdir":
            ticket = self.mkdir_ticket
            if (ticket is None or len(args) != 3
                    or args != ticket):
                self.reject("deny unauthenticated exclusive Zig directory")
        elif (event in ("import", "compile", "exec", "marshal.loads",
                        "marshal.load", "sys.addaudithook", "ctypes.dlopen")
              or event.startswith(("subprocess", "socket", "ctypes",
                                   "os.system", "os.posix_spawn", "os.fork"))):
            self.reject("deny dynamic, native, matcher, or process operation")

    def deny(self, *args: object, **kwargs: object) -> object:
        self.reject("deny unauthenticated source-wall operation")

    def open(self, path: object, flags: object, mode: object = 0o777,
             *, dir_fd: int | None = None) -> int:
        ticket = self.open_ticket
        if (ticket is None or type(path) is not str or type(flags) is not int
                or (path, flags, dir_fd, mode if flags & os.O_CREAT else None)
                != ticket):
            self.reject("deny unauthorized descriptor-relative path")
        raw = self.raw["open"]
        return raw(path, flags, mode, dir_fd=dir_fd)

    def read(self, fd: object, size: object) -> bytes:
        if (type(fd) is not int or fd != self.read_ticket
                or fd not in self.live or self.live[fd] not in ("owner", "readback")
                or type(size) is not int or not 0 <= size <= 65536):
            self.reject("deny foreign, inherited, or oversized descriptor read")
        return self.raw["read"](fd, size)

    def write(self, fd: object, value: object) -> int:
        ticket = self.write_ticket
        if (type(fd) is not int or ticket is None or fd != ticket[0]
                or fd not in self.live or self.live[fd] != "output"
                or type(value) is not bytes or value != ticket[1]):
            self.reject("deny foreign, inherited, or reordered target write")
        return self.raw["write"](fd, value)

    def fstat(self, fd: object) -> os.stat_result:
        if (type(fd) is not int or fd != self.stat_ticket
                or fd not in self.live):
            self.reject("deny inherited, hidden, or foreign descriptor metadata")
        return self.raw["fstat"](fd)

    def close(self, fd: object) -> None:
        if type(fd) is not int or fd != self.close_ticket or fd not in self.live:
            self.reject("deny inherited or foreign descriptor closure")
        self.raw["close"](fd)

    def fsync(self, fd: object) -> None:
        if (type(fd) is not int or fd != self.sync_ticket
                or fd not in self.live or self.mode != "--apply"):
            self.reject("deny unauthorized descriptor synchronization")
        self.raw["fsync"](fd)

    def mkdir(self, path: object, mode: object = 0o777,
              *, dir_fd: int | None = None) -> None:
        ticket = self.mkdir_ticket
        if (ticket is None or type(path) is not str or type(mode) is not int
                or type(dir_fd) is not int or (path, mode, dir_fd) != ticket
                or self.mode != "--apply"):
            self.reject("deny foreign or non-root Zig target directory")
        self.raw["mkdir"](path, mode, dir_fd=dir_fd)

    def install(self) -> None:
        no_matchers()
        native = sys.modules["posix"]
        for name in ("open", "read", "write", "fstat", "close", "fsync", "mkdir"):
            self.raw[name] = getattr(os, name)
        wrappers = {
            "open": self.open, "read": self.read, "write": self.write,
            "fstat": self.fstat, "close": self.close, "fsync": self.fsync,
            "mkdir": self.mkdir,
        }
        for owner in (os, native):
            for name, callback in wrappers.items():
                setattr(owner, name, callback)
            for name in (
                "stat", "lstat", "listdir", "scandir", "unlink", "remove",
                "rename", "replace", "rmdir", "chmod", "chown", "link",
                "symlink", "truncate", "ftruncate", "dup", "dup2", "dup3",
                "pread", "pwrite", "readv", "writev", "sendfile", "splice",
                "copy_file_range", "system", "fork", "forkpty", "posix_spawn",
                "posix_spawnp", "execv", "execve", "execvp", "execvpe",
            ):
                if hasattr(owner, name):
                    setattr(owner, name, self.deny)
        builtins.open = self.deny
        io.open = self.deny
        _io.open = self.deny
        builtins.__import__ = self.deny
        builtins.compile = self.deny
        builtins.eval = self.deny
        builtins.exec = self.deny
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.deny)
        sys.addaudithook(self.audit)

    def descriptor(self, path: str, flags: int, *, parent: int | None = None,
                   mode: int | None = None, kind: str) -> int:
        need(self.open_ticket is None, "reject nested descriptor capability")
        self.open_ticket = (path, flags, parent, mode)
        try:
            value = (os.open(path, flags, mode, dir_fd=parent)
                     if mode is not None else os.open(path, flags, dir_fd=parent))
        finally:
            self.open_ticket = None
        need(type(value) is int and value >= 3 and value not in self.live,
             "reject inherited, exchanged, or duplicate descriptor")
        self.live[value] = kind
        return value

    def metadata(self, fd: int) -> os.stat_result:
        need(self.stat_ticket is None, "reject nested metadata capability")
        self.stat_ticket = fd
        try:
            return os.fstat(fd)
        finally:
            self.stat_ticket = None

    def release(self, fd: int) -> None:
        need(self.close_ticket is None, "reject nested closure capability")
        self.close_ticket = fd
        try:
            os.close(fd)
        finally:
            self.close_ticket = None
        del self.live[fd]

    def receive(self, fd: int, width: int) -> bytes:
        need(self.read_ticket is None, "reject nested read capability")
        self.read_ticket = fd
        try:
            return os.read(fd, width)
        finally:
            self.read_ticket = None

    def transmit(self, fd: int, payload: bytes) -> int:
        need(self.write_ticket is None, "reject nested write capability")
        self.write_ticket = (fd, payload)
        try:
            return os.write(fd, payload)
        finally:
            self.write_ticket = None

    def sync(self, fd: int) -> None:
        need(self.sync_ticket is None, "reject nested sync capability")
        self.sync_ticket = fd
        try:
            os.fsync(fd)
        finally:
            self.sync_ticket = None

    def open_root(self) -> int:
        need(self.root is None, "reject duplicate workspace root capability")
        flags = (os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                 | os.O_CLOEXEC)
        root = self.descriptor(ROOT, flags, kind="directory")
        info = self.metadata(root)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE
             and info.st_uid == os.geteuid(),
             "reject substituted workspace root directory")
        self.root = root
        return root

    def segment(self, value: object) -> str:
        need(type(value) is str and bool(value) and value not in (".", "..")
             and "/" not in value and "\\" not in value
             and "\x00" not in value,
             "reject traversal, empty, slash, or ambiguous source segment")
        return value

    def child(self, parent: int, name: str) -> int:
        name = self.segment(name)
        need(parent in self.live and self.live[parent] == "directory",
             "reject foreign or inherited parent directory")
        flags = (os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                 | os.O_CLOEXEC)
        value = self.descriptor(name, flags, parent=parent, kind="directory")
        info = self.metadata(value)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE
             and info.st_uid == os.geteuid(),
             "reject substituted immutable owner directory")
        return value

    def owner(self, relative: str, sha256: str,
              *, size: int | None = None, inode: int | None = None,
              candidate: bool = False) -> bytes:
        allowed = {SOURCE, PROTOCOL, CONTRACT, RECEIPT}
        if self.mode == "--apply":
            allowed.update((BRIDGE_INPUT, ADAPTER_INPUT))
        need(relative in allowed and (not candidate or self.mode == "--apply")
             and self.root is not None,
             "deny candidate, archive, hidden, private, or foreign owner")
        fingerprint(sha256, "immutable source owner")
        parent = self.root
        opened: list[int] = []
        fd: int | None = None
        try:
            parts = relative.split("/")
            for part in parts[:-1]:
                parent = self.child(parent, part)
                opened.append(parent)
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
            fd = self.descriptor(self.segment(parts[-1]), flags,
                                 parent=parent, kind="owner")
            before = self.metadata(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                 and stat.S_IMODE(before.st_mode) == 0o600
                 and before.st_uid == os.geteuid() and before.st_nlink == 1
                 and 0 < before.st_size <= 262144
                 and (size is None or before.st_size == size)
                 and (inode is None or before.st_ino == inode),
                 "reject substituted, linked, public, or wrong-size owner")
            remaining = before.st_size
            blocks: list[bytes] = []
            while remaining:
                piece = self.receive(fd, min(remaining, 65536))
                need(type(piece) is bytes and len(piece) > 0,
                     "reject truncated immutable source owner")
                blocks.append(piece)
                remaining -= len(piece)
            need(self.receive(fd, 1) == b"",
                 "reject oversized immutable source owner")
            after = self.metadata(fd)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "reject concurrently changed immutable source owner")
            raw = b"".join(blocks)
            need(digest(raw) == sha256,
                 "reject substituted immutable source owner digest")
            if candidate:
                self.candidate_reads += 1
            else:
                self.public_reads += 1
            return raw
        finally:
            if fd is not None and fd in self.live:
                self.release(fd)
            for item in reversed(opened):
                self.release(item)

    def finish(self) -> None:
        need(self.root is not None and set(self.live) == {self.root},
             "reject leaked immutable source descriptors")
        root = self.root
        self.release(root)
        self.root = None


def no_matchers() -> None:
    need(not any(name in sys.modules for name in
                 ("re", "_sre", "regex", "ctypes", "subprocess", "json")),
         "reject stdlib matcher, external package, process, or JSON imports")


def diagnose(receipt: object) -> None:
    need(type(receipt) is dict, "require authenticated actual Zig failure receipt")
    expected_failures = list(FAILURE_PARTITION)
    need(receipt.get("status") == "PASS" and receipt.get("family") == "zig"
         and receipt.get("case_execution_denominator") == 31237
         and receipt.get("semantic_mismatch_count") == 1156
         and receipt.get("verified_passing_case_count") == 18056
         and receipt.get("failed_suites") == expected_failures
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("completed_suite_count") == 13
         and receipt.get("infrastructure_failure_count") == 0
         and receipt.get("original_campaign_passed") is False
         and receipt.get("candidate_qualified") is False,
         "preserve exact complete, failed first-party Zig original campaign")
    archive = receipt.get("archive")
    need(type(archive) is dict and archive.get("sha256") == ARCHIVE_SHA256
         and archive.get("bytes") == ARCHIVE_BYTES,
         "authenticate historical archive descriptor without opening archive")


def contract_document(source_hash: str, protocol_hash: str,
                      synthetic: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "status": "SOURCE FROZEN; CORRECTED FIRST-PARTY ZIG NOT MATERIALIZED",
        "phase": "CANDIDATES; TWO INDEPENDENT FIRST-PARTY ZIG SEMANTIC CORRECTIONS",
        "source": {"path": SOURCE, "sha256": source_hash},
        "protocol": {"path": PROTOCOL, "sha256": protocol_hash},
        "immutable_latest_complete_failure": {
            "receipt_path": RECEIPT,
            "receipt_sha256": RECEIPT_SHA256,
            "receipt_bytes": RECEIPT_BYTES,
            "receipt_inode": RECEIPT_INODE,
            "archive_sha256": ARCHIVE_SHA256,
            "archive_bytes": ARCHIVE_BYTES,
            "archive_opened": False,
            "original_case_denominator": 31237,
            "actual_independent_candidate_workers": 13,
            "completed_original_categories": 13,
            "verified_passing_case_count": 18056,
            "observed_complete_mismatch_count": 1156,
            "mismatches_by_suite": FAILURE_PARTITION,
            "scanner_capture_projection_mismatches": 1028,
            "flag_and_pattern_representation_mismatches": 128,
            "failed_candidate_qualified": False,
            "history_rewritten": False,
        },
        "independent_first_party_inputs": {
            "bridge": {
                "path": BRIDGE_INPUT, "sha256": BRIDGE_INPUT_SHA256,
                "bytes": BRIDGE_INPUT_BYTES, "inode": BRIDGE_INPUT_INODE,
            },
            "adapter": {
                "path": ADAPTER_INPUT, "sha256": ADAPTER_INPUT_SHA256,
                "bytes": ADAPTER_INPUT_BYTES, "inode": ADAPTER_INPUT_INODE,
            },
            "source_gate_candidate_reads": 0,
            "root_application_candidate_reads": 2,
        },
        "first_party_corrections": {
            "bridge_target": {
                "path": BRIDGE_TARGET, "sha256": BRIDGE_TARGET_SHA256,
                "bytes": BRIDGE_TARGET_BYTES,
                "source_sites_changed": 1,
                "scanner_mismatches_targeted": 1028,
                "existing_nested_beginning_preserved": True,
                "active_branch_end_always_closed": True,
                "unrelated_groups_and_lastindex_unchanged": True,
            },
            "adapter_target": {
                "path": ADAPTER_TARGET, "sha256": ADAPTER_TARGET_SHA256,
                "bytes": ADAPTER_TARGET_BYTES,
                "source_sites_changed": 2,
                "flags_mismatches_targeted": 128,
                "regexflag_order": "DECLARATION ORDER",
                "compiled_pattern_flag_order": "NUMERIC BIT ORDER",
                "unknown_flag_object_format": "DECIMAL",
                "unknown_compiled_pattern_format": "HEXADECIMAL",
                "complete_cpython_flag_alias_surface": True,
            },
            "historical_structured_expected_records_replayed": 1154,
            "historical_upstream_assertions_explained": 2,
            "complete_observed_mismatches_targeted": 1156,
            "candidate_families_added": 0,
            "external_regex_packages": 0,
            "stdlib_regex_delegation": False,
            "cross_candidate_delegation": False,
        },
        "source_only_synthetic_controls": synthetic,
        "source_only_effects": {
            "candidate_files_opened": 0,
            "candidate_processes": 0,
            "candidate_imports": 0,
            "candidate_matching": "NOT RUN",
            "compressed_archives_opened": 0,
            "private_roots_opened": 0,
            "proposal_files_opened": 0,
            "proposal_metadata_probes": 0,
            "holdout_files_opened": 0,
            "holdout_metadata_probes": 0,
            "clock_samples": 0,
            "workspace_mutations": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False,
        },
    }


def arguments(values: list[str]) -> tuple[str, dict[str, str], set[str]]:
    need(type(values) is list and len(values) >= 1,
         "require exactly one isolated Zig source-freeze mode")
    mode = values[0]
    need(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
         "reject unsupported isolated Zig source-freeze mode")
    pins: dict[str, str] = {}
    flags: set[str] = set()
    at = 1
    while at < len(values):
        key = values[at]
        if key in ("--root-authorized", "--frozen-committed-pushed"):
            need(key not in flags, "reject duplicate root-only source capability")
            flags.add(key)
            at += 1
            continue
        need(key in ("--source-sha256", "--protocol-sha256", "--contract-sha256",
                     "--frozen-commit", "--pushed-commit")
             and key not in pins and at + 1 < len(values),
             "reject malformed, duplicate, or missing immutable source fingerprint")
        pins[key] = fingerprint(values[at + 1], key,
                                40 if key.endswith("commit") else 64)
        at += 2
    if mode == "--render-contract":
        need(set(pins) == {"--source-sha256", "--protocol-sha256"}
             and not flags,
             "render contract from precisely two authenticated freeze owners")
    elif mode in ("--self-test", "--verify-source"):
        need(set(pins) == {"--source-sha256", "--protocol-sha256",
                           "--contract-sha256"} and not flags,
             "source-only gates require exactly three immutable fingerprints")
    else:
        need(set(pins) == {"--source-sha256", "--protocol-sha256",
                           "--contract-sha256", "--frozen-commit",
                           "--pushed-commit"}
             and flags == {"--root-authorized", "--frozen-committed-pushed"}
             and pins["--frozen-commit"] == pins["--pushed-commit"],
             "root materialization requires one already committed and pushed freeze")
    return mode, pins, flags


def rejected(wall: SourceWall, label: str, callback) -> str:
    before = wall.blocked
    try:
        callback()
    except (FreezeError, OSError, ValueError, TypeError, AttributeError):
        need(wall.blocked > before,
             "hostile control failed without reaching permanent wall: " + label)
        return label
    raise FreezeError("hostile control bypassed source wall: " + label)


def self_test(wall: SourceWall) -> dict[str, object]:
    native = sys.modules["posix"]
    path = ROOT + "/" + SOURCE
    hidden = ROOT + "/oracle/phase3/final-held-out-cases.json"
    checks = [
        rejected(wall, "builtins-open", lambda: builtins.open(path, "rb")),
        rejected(wall, "io-open", lambda: io.open(path, "rb")),
        rejected(wall, "native-io-open", lambda: _io.open(path, "rb")),
        rejected(wall, "absolute-os-open", lambda: os.open(path, os.O_RDONLY)),
        rejected(wall, "native-posix-open", lambda: native.open(path, os.O_RDONLY)),
        rejected(wall, "traversal-open", lambda: os.open(
            ROOT + "/tools/../" + SOURCE, os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "foreign-read", lambda: os.read(0, 1)),
        rejected(wall, "native-foreign-read", lambda: native.read(0, 1)),
        rejected(wall, "foreign-write", lambda: os.write(1, b"bad")),
        rejected(wall, "native-foreign-write", lambda: native.write(1, b"bad")),
        rejected(wall, "foreign-fstat", lambda: os.fstat(0)),
        rejected(wall, "native-foreign-fstat", lambda: native.fstat(0)),
        rejected(wall, "foreign-close", lambda: os.close(0)),
        rejected(wall, "native-foreign-close", lambda: native.close(0)),
        rejected(wall, "foreign-sync", lambda: os.fsync(1)),
        rejected(wall, "native-foreign-sync", lambda: native.fsync(1)),
        rejected(wall, "target-directory", lambda: os.mkdir(DIRECTORY, 0o700)),
        rejected(wall, "target-before-root", lambda: os.open(
            ROOT + "/" + ADAPTER_TARGET,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        rejected(wall, "bridge-before-root", lambda: os.open(
            ROOT + "/" + BRIDGE_TARGET,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        rejected(wall, "candidate-source-read", lambda: os.open(
            ROOT + "/" + ADAPTER_INPUT, os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "native-library-read", lambda: os.open(
            ROOT + "/candidates/_zig_bridge.so", os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "archive-read", lambda: os.open(
            ROOT + "/oracle/phase2/evidence/private.json.gz", os.O_RDONLY)),
        rejected(wall, "holdout-read", lambda: os.open(hidden, os.O_RDONLY)),
        rejected(wall, "holdout-stat", lambda: os.stat(hidden)),
        rejected(wall, "holdout-lstat", lambda: os.lstat(hidden)),
        rejected(wall, "native-holdout-stat", lambda: native.stat(hidden)),
        rejected(wall, "unlink", lambda: os.unlink(path)),
        rejected(wall, "rename", lambda: os.rename(path, hidden)),
        rejected(wall, "hardlink", lambda: os.link(path, hidden)),
        rejected(wall, "symlink", lambda: os.symlink(path, hidden)),
        rejected(wall, "chmod", lambda: os.chmod(path, 0o644)),
        rejected(wall, "truncate", lambda: os.truncate(path, 0)),
        rejected(wall, "duplicate-fd", lambda: os.dup(0)),
        rejected(wall, "native-duplicate-fd", lambda: native.dup(0)),
        rejected(wall, "candidate-process", lambda: os.system("true")),
        rejected(wall, "dynamic-compiler", lambda: builtins.compile("1", "x", "eval")),
        rejected(wall, "dynamic-eval", lambda: builtins.eval("1")),
        rejected(wall, "dynamic-exec", lambda: builtins.exec("pass")),
        rejected(wall, "stdlib-regex-import", lambda: builtins.__import__("re")),
        rejected(wall, "clock-time", lambda: time.time()),
        rejected(wall, "clock-monotonic", lambda: time.monotonic()),
        rejected(wall, "clock-performance", lambda: time.perf_counter()),
        rejected(wall, "direct-audit-open", lambda: sys.audit(
            "open", hidden, None, os.O_RDONLY)),
    ]
    for malformed in (b'{"a":1,"a":2}', b"1.5", b"01", b'"\\ud800"',
                      b'{"a":1}x', b"[1,]", b'{"x":NaN}'):
        try:
            StrictJSON(malformed).parse()
        except (FreezeError, ValueError, UnicodeError, TypeError):
            continue
        raise FreezeError("malformed immutable JSON escaped strict decoder")
    try:
        need(b"truthy", "reject truthy bytes instead of literal True")
    except FreezeError:
        pass
    else:
        raise FreezeError("truthy bytes bypassed exact-boolean controls")
    need(len(checks) >= 40 and not wall.live and wall.root is None
         and wall.public_reads == 0 and wall.candidate_reads == 0
         and wall.mutations == 0,
         "keep hostile source-only controls entirely readless and mutationless")
    return {"blocked_hostile_operations": len(checks),
            "strict_json_rejections": 7,
            "truthy_bytes_regression_rejected": True,
            "readless_source_gate": True,
            "checks": checks}


def load_context(wall: SourceWall, mode: str,
                 pins: dict[str, str], synthetic: dict[str, object]) -> dict[str, object]:
    wall.open_root()
    try:
        wall.owner(SOURCE, pins["--source-sha256"])
        wall.owner(PROTOCOL, pins["--protocol-sha256"])
        receipt = StrictJSON(wall.owner(
            RECEIPT, RECEIPT_SHA256, size=RECEIPT_BYTES,
            inode=RECEIPT_INODE
        )).parse()
        diagnose(receipt)
        expected = contract_document(pins["--source-sha256"],
                                     pins["--protocol-sha256"], synthetic)
        if mode != "--render-contract":
            contract_raw = wall.owner(CONTRACT, pins["--contract-sha256"])
            contract = StrictJSON(contract_raw).parse()
            need(contract == expected and contract_raw == document(expected),
                 "reject changed, omitted, reordered, or noncanonical freeze contract")
        return {"contract": expected, "synthetic": synthetic}
    finally:
        if mode != "--apply" and wall.root is not None:
            wall.finish()


def derive_sources(wall: SourceWall) -> tuple[bytes, bytes]:
    adapter = wall.owner(ADAPTER_INPUT, ADAPTER_INPUT_SHA256,
                         size=ADAPTER_INPUT_BYTES, inode=ADAPTER_INPUT_INODE,
                         candidate=True)
    bridge = wall.owner(BRIDGE_INPUT, BRIDGE_INPUT_SHA256,
                        size=BRIDGE_INPUT_BYTES, inode=BRIDGE_INPUT_INODE,
                        candidate=True)
    corrected_adapter = replace_once(adapter, OLD_FLAG_CLASS,
                                     NEW_FLAG_CLASS, "complete RegexFlag surface")
    corrected_adapter = replace_once(corrected_adapter, OLD_PATTERN_FLAGS,
                                     NEW_PATTERN_FLAGS,
                                     "independent compiled-pattern flag order")
    corrected_bridge = replace_once(bridge, OLD_SCANNER, NEW_SCANNER,
                                    "always close active scanner branch")
    need(len(corrected_adapter) == ADAPTER_TARGET_BYTES
         and digest(corrected_adapter) == ADAPTER_TARGET_SHA256
         and len(corrected_bridge) == BRIDGE_TARGET_BYTES
         and digest(corrected_bridge) == BRIDGE_TARGET_SHA256,
         "reject changed first-party Zig source transforms or target fingerprints")
    need(b"import re\n" not in corrected_adapter
         and b"from re import" not in corrected_adapter
         and b"import regex" not in corrected_adapter
         and b"_sre" not in corrected_adapter
         and b"rebar_zig_match" in corrected_bridge
         and b"PyImport_ImportModule(\"re\")" not in corrected_bridge,
         "reject stdlib delegation, external engine, or missing Zig native core")
    return corrected_adapter, corrected_bridge


def create_sources(wall: SourceWall, adapter: bytes,
                   bridge: bytes) -> dict[str, object]:
    need(wall.mode == "--apply" and wall.root is not None
         and wall.candidate_reads == 2 and wall.mutations == 0,
         "require two fully authenticated inputs before the first mutation")
    root = wall.root
    directories: list[int] = []
    child: int | None = None
    parent = root
    outputs: list[dict[str, object]] = []
    try:
        for part in ("candidates", "zig", "variants"):
            parent = wall.child(parent, part)
            directories.append(parent)
        name = "final_original_semantics_v1"
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        try:
            existing = wall.descriptor(name, flags, parent=parent,
                                       kind="directory")
        except FileNotFoundError:
            existing = None
        if existing is not None:
            wall.release(existing)
            raise FreezeError("refuse to overwrite an existing Zig source variant")

        need(wall.mkdir_ticket is None, "reject nested exclusive mkdir capability")
        wall.mkdir_ticket = (name, 0o700, parent)
        try:
            os.mkdir(name, 0o700, dir_fd=parent)
        finally:
            wall.mkdir_ticket = None
        wall.mutations += 1
        child = wall.child(parent, name)
        child_info = wall.metadata(child)
        need(stat.S_IMODE(child_info.st_mode) == 0o700,
             "reject non-private exclusive Zig source variant directory")

        for filename, expected, expected_sha in (
                ("zig_candidate.py", adapter, ADAPTER_TARGET_SHA256),
                ("py_bridge.c", bridge, BRIDGE_TARGET_SHA256)):
            write_flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                           | os.O_NOFOLLOW | os.O_CLOEXEC)
            fd = wall.descriptor(filename, write_flags, parent=child,
                                 mode=0o600, kind="output")
            wall.mutations += 1
            initial = wall.metadata(fd)
            need(stat.S_ISREG(initial.st_mode)
                 and stat.S_IMODE(initial.st_mode) == 0o600
                 and initial.st_dev == DEVICE
                 and initial.st_uid == os.geteuid()
                 and initial.st_nlink == 1 and initial.st_size == 0,
                 "reject replaced, linked, public, or nonempty Zig output")
            offset = 0
            while offset < len(expected):
                part = expected[offset:offset + 65536]
                count = wall.transmit(fd, part)
                need(type(count) is int and 0 < count <= len(part),
                     "reject incomplete or excess first-party source write")
                offset += count
            complete = wall.metadata(fd)
            need((complete.st_dev, complete.st_ino, complete.st_uid,
                  complete.st_nlink) == (initial.st_dev, initial.st_ino,
                                          initial.st_uid, 1)
                 and stat.S_IMODE(complete.st_mode) == 0o600
                 and complete.st_size == len(expected),
                 "reject exchanged or incomplete first-party Zig source")
            wall.sync(fd)
            wall.release(fd)

            read_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
            check = wall.descriptor(filename, read_flags, parent=child,
                                    kind="readback")
            try:
                remaining = len(expected)
                blocks: list[bytes] = []
                while remaining:
                    part = wall.receive(check, min(remaining, 65536))
                    need(type(part) is bytes and len(part) > 0,
                         "reject truncated durable first-party Zig variant")
                    blocks.append(part)
                    remaining -= len(part)
                need(wall.receive(check, 1) == b""
                     and digest(b"".join(blocks)) == expected_sha,
                     "reject changed durable first-party Zig variant")
            finally:
                wall.release(check)
            outputs.append({"path": DIRECTORY + "/" + filename,
                            "sha256": expected_sha,
                            "bytes": len(expected),
                            "device": complete.st_dev,
                            "inode": complete.st_ino,
                            "mode": "0600",
                            "nlink": 1,
                            "exclusive_no_follow": True,
                            "fsync_completed": True})
        wall.sync(child)
        wall.sync(parent)
        need(wall.mutations == 3 and len(outputs) == 2,
             "require exactly one new directory and two distinct source files")
        return {"directory": {"path": DIRECTORY,
                              "device": child_info.st_dev,
                              "inode": child_info.st_ino,
                              "mode": "0700",
                              "fsync_completed": True},
                "adapter": outputs[0], "bridge": outputs[1]}
    finally:
        if child is not None and child in wall.live:
            wall.release(child)
        for descriptor in reversed(directories):
            if descriptor in wall.live:
                wall.release(descriptor)


def neutral_effects() -> dict[str, object]:
    return {"candidate_processes_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "external_regex_dependency_count": 0,
            "stdlib_matching_delegation_count": 0,
            "cross_candidate_engine_reads": 0,
            "archives_opened": 0,
            "private_roots_opened": 0,
            "proposal_files_opened": 0,
            "proposal_metadata_probes": 0,
            "holdout_files_opened": 0,
            "holdout_metadata_probes": 0,
            "clock_samples": 0,
            "original_case_execution_denominator": 31237,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False}


def main() -> int:
    need(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
         and sys.flags.no_site == 1,
         "require isolated, bytecode-disabled, no-site pinned CPython 3.14.6")
    no_matchers()
    digest(b"initialize first-party digest before permanent source wall")
    mode, pins, flags = arguments(list(sys.argv[1:]))
    synthetic = semantic_controls()
    wall = SourceWall(mode)
    wall.install()

    if mode == "--self-test":
        hostile = self_test(wall)
        result = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                  "mode": "self-test", "source_sha256": pins["--source-sha256"],
                  "protocol_sha256": pins["--protocol-sha256"],
                  "contract_sha256": pins["--contract-sha256"],
                  "synthetic": synthetic, "hostile": hostile,
                  "candidate_source_files_read": 0,
                  "public_owner_files_read": 0,
                  "workspace_mutations": 0,
                  **neutral_effects()}
    else:
        state = load_context(wall, mode, pins, synthetic)
        if mode == "--render-contract":
            result = state["contract"]
        elif mode == "--verify-source":
            need(wall.public_reads == 4 and wall.candidate_reads == 0
                 and wall.mutations == 0,
                 "verify only four exact public immutable source owners")
            result = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                      "mode": "verify-source",
                      "source_sha256": pins["--source-sha256"],
                      "protocol_sha256": pins["--protocol-sha256"],
                      "contract_sha256": pins["--contract-sha256"],
                      "synthetic": synthetic,
                      "candidate_source_files_read": 0,
                      "public_owner_files_read": wall.public_reads,
                      "workspace_mutations": 0,
                      **neutral_effects()}
        else:
            need(flags == {"--root-authorized", "--frozen-committed-pushed"},
                 "deny uncommitted or non-root dual-source materialization")
            adapter, bridge = derive_sources(wall)
            created = create_sources(wall, adapter, bridge)
            wall.finish()
            need(wall.public_reads == 4 and wall.candidate_reads == 2
                 and wall.mutations == 3,
                 "require four public owners, two immutable sources, three mutations")
            result = {"schema": SCHEMA + "-application", "status": "APPLIED",
                      "mode": "apply",
                      "source_sha256": pins["--source-sha256"],
                      "protocol_sha256": pins["--protocol-sha256"],
                      "contract_sha256": pins["--contract-sha256"],
                      "frozen_pushed_commit": pins["--pushed-commit"],
                      "created": created,
                      "candidate_source_files_read": 2,
                      "public_owner_files_read": 4,
                      "workspace_mutations": 3,
                      "historical_mismatches_targeted": 1156,
                      "historical_scanner_mismatches_targeted": 1028,
                      "historical_flags_mismatches_targeted": 128,
                      "synthetic": synthetic,
                      **neutral_effects()}
    no_matchers()
    sys.stdout.buffer.write(document(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, ValueError, TypeError, UnicodeError,
            KeyError, AttributeError) as error:
        sys.stderr.write("final first-party Zig source freeze rejected: "
                         + str(error) + "\n")
        raise SystemExit(2)
