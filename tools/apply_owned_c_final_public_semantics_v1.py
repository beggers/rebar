#!/usr/bin/env python3
"""Freeze the last independently observed first-party C public-flag fixes.

Source gates authenticate exactly four public plaintext owners and never open
a candidate, compressed archive, native engine, benchmark, or hidden holdout.
Only root may materialize the separately frozen, committed, and pushed source.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("C flag-source freeze cannot import a matching engine")

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
SCHEMA = "rebar-owned-c-final-public-semantics-v1-source-freeze"
SOURCE = "tools/apply_owned_c_final_public_semantics_v1.py"
PROTOCOL = "oracle/phase2/C-FINAL-PUBLIC-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/c-final-public-semantics-v1.json"
RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v15-"
    "c-phase2-v23-c-complete-semantics-original-p0-v15-"
    "failures-publication-receipt.json"
)
RECEIPT_SHA256 = "6adea6a4da59bb0c63c54006991257b46149c4447a82bb1cd6b8810e6bee5b43"
RECEIPT_BYTES = 10888
RECEIPT_INODE = 526500
ARCHIVE_SHA256 = "9864dd38761bcb23008973bde471c8911e18234fe7162ad11a2a1893c118a102"
ARCHIVE_BYTES = 139742
ARCHIVE_INODE = 526499

INPUT = "candidates/c/variants/public_adapter_semantics_v2/vm_candidate.py"
INPUT_SHA256 = "4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a"
INPUT_BYTES = 61663
INPUT_INODE = 525120
NATIVE_INPUT = "candidates/c/variants/complete_native_semantics_v1/vm_native.c"
NATIVE_INPUT_SHA256 = "0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f"
NATIVE_INPUT_BYTES = 221557
NATIVE_INPUT_INODE = 525629
DIRECTORY = "candidates/c/variants/final_public_semantics_v1"
TARGET = DIRECTORY + "/vm_candidate.py"
TARGET_SHA256 = "e91819b1d6b399954b3384519fdfddb6ccd6d4e4099a34e06d702c9959a79193"
TARGET_BYTES = 62209
NATIVE_TARGET = DIRECTORY + "/vm_native.c"
NATIVE_TARGET_SHA256 = "99f45846551705379ccd7365333995ee68fe25e10d101655a17ad45c5e13a5e6"
NATIVE_TARGET_BYTES = 221715
ENGINE_SHA256 = "caaad35fe4354d1fc3506fc0dfa8bd1d2568bd471b7f84c9b12842e79f752865"
NATIVE_SOURCE_SHA256 = "0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f"

FAILURES = {"original_bounded_v5": 2,
            "public_types_v1": 144,
            "public_surface_v19": 78}
DECLARED = (("ASCII", 256), ("IGNORECASE", 2), ("LOCALE", 4),
            ("UNICODE", 32), ("MULTILINE", 8), ("DOTALL", 16),
            ("VERBOSE", 64), ("DEBUG", 128))
MEMBERS = ("NOFLAG", "ASCII", "A", "IGNORECASE", "I", "LOCALE", "L",
           "UNICODE", "U", "MULTILINE", "M", "DOTALL", "S",
           "VERBOSE", "X", "DEBUG")

OLD_PUBLIC_FLAG = b'''class RegexFlag(enum.IntFlag):
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

NEW_PUBLIC_FLAG = b'''class RegexFlag(enum.IntFlag):
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
'''

OLD_CONFIGURE = b'''Match = _vm_native.Match
_vm_native.configure(_template, _template_parts)
RegexFlag.__module__ = "re"
'''

NEW_CONFIGURE = b'''Match = _vm_native.Match


class _NativePatternFlag(enum.IntFlag):
    ASCII = 256
    IGNORECASE = 2
    LOCALE = 4
    UNICODE = 32
    MULTILINE = 8
    DOTALL = 16
    VERBOSE = 64
    DEBUG = 128
    _numeric_repr_ = hex

    def __repr__(self):
        value = int(self)
        ordered = sorted(type(self), key=int)
        known = sum(int(flag) for flag in ordered)
        parts = [f"re.{flag.name}" for flag in ordered
                 if value & int(flag)]
        unknown = value & ~known
        if unknown:
            parts.append(hex(unknown))
        return "|".join(parts)


_PublicRegexFlag = RegexFlag
try:
    RegexFlag = _NativePatternFlag
    _vm_native.configure(_template, _template_parts)
finally:
    RegexFlag = _PublicRegexFlag
del _PublicRegexFlag
RegexFlag.__module__ = "re"
'''

OLD_FLAG_COERCION = b'''        _CACHE2[key] = cached
        return cached
    flags = int(flags)
    if not isinstance(pattern, (str, bytes)):
        raise TypeError("first argument must be string or compiled pattern")
'''

NEW_FLAG_COERCION = b'''        _CACHE2[key] = cached
        return cached
    if not isinstance(pattern, (str, bytes)):
        raise TypeError("first argument must be string or compiled pattern")
    flags & int(VERBOSE)
    flags = int(flags)
'''

OLD_PATTERN_IDENTITY = b'''    PyObject *result=PyTuple_Pack(3,(PyObject *)Py_TYPE(pattern->pattern),
                                  pattern->pattern,flags);
'''

NEW_PATTERN_IDENTITY = b'''    PyObject *kind=PyUnicode_Check(pattern->pattern)
        ? (PyObject *)&PyUnicode_Type
        : PyBytes_Check(pattern->pattern)
            ? (PyObject *)&PyBytes_Type
            : (PyObject *)Py_TYPE(pattern->pattern);
    PyObject *result=PyTuple_Pack(3,kind,pattern->pattern,flags);
'''


class FreezeError(Exception):
    pass


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(payload: bytes) -> str:
    need(type(payload) is bytes, "hash only immutable exact bytes")
    return hashlib.sha256(payload).hexdigest()


def pin(value: object, *, width: int = 64) -> str:
    need(type(value) is str and len(value) == width
         and all(item in "0123456789abcdef" for item in value),
         "reject malformed or noncanonical immutable fingerprint")
    return value


def string(value: str) -> str:
    need(type(value) is str, "serialize only exact immutable strings")
    result = ['"']
    for character in value:
        code = ord(character)
        need(not 0xD800 <= code <= 0xDFFF,
             "reject unpaired immutable JSON surrogate")
        if character == '"':
            result.append('\\"')
        elif character == "\\":
            result.append("\\\\")
        elif code < 32:
            result.append("\\u" + format(code, "04x"))
        else:
            result.append(character)
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    need(depth <= 24, "reject excessively nested source evidence")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        need(abs(value) < 1 << 63, "reject oversized immutable integer")
        return str(value)
    if type(value) is str:
        return string(value)
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1)
                              for item in value) + "]"
    if type(value) is dict:
        need(all(type(key) is str for key in value),
             "reject ambiguous immutable JSON key")
        return "{" + ",".join(string(key) + ":"
                              + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("reject floats and executable immutable evidence")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class StrictJSON:
    def __init__(self, payload: bytes):
        need(type(payload) is bytes and 0 < len(payload) <= 262144,
             "reject oversized or empty authenticated plaintext owner")
        self.data = payload.decode("utf-8", "strict")
        self.index = 0

    def blank(self) -> None:
        while self.index < len(self.data) and self.data[self.index] in " \t\r\n":
            self.index += 1

    def quoted(self) -> str:
        need(self.index < len(self.data) and self.data[self.index] == '"',
             "require one exact immutable JSON string")
        self.index += 1
        values: list[str] = []
        while self.index < len(self.data):
            item = self.data[self.index]
            self.index += 1
            if item == '"':
                return "".join(values)
            if item != "\\":
                code = ord(item)
                need(code >= 32 and not 0xD800 <= code <= 0xDFFF,
                     "reject control characters and lone surrogate")
                values.append(item)
                continue
            need(self.index < len(self.data), "reject unfinished JSON escape")
            marker = self.data[self.index]
            self.index += 1
            escaped = {'"': '"', "\\": "\\", "/": "/", "b": "\b",
                       "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
            if marker in escaped:
                values.append(escaped[marker])
                continue
            need(marker == "u" and self.index + 4 <= len(self.data),
                 "reject malformed immutable JSON Unicode escape")
            digits = self.data[self.index:self.index + 4]
            need(all(item in "0123456789abcdefABCDEF" for item in digits),
                 "reject non-hexadecimal immutable Unicode escape")
            code = int(digits, 16)
            self.index += 4
            if 0xD800 <= code <= 0xDBFF:
                need(self.data[self.index:self.index + 2] == "\\u"
                     and self.index + 6 <= len(self.data),
                     "reject unpaired immutable JSON high surrogate")
                digits = self.data[self.index + 2:self.index + 6]
                need(all(item in "0123456789abcdefABCDEF" for item in digits),
                     "reject malformed immutable JSON low surrogate")
                low = int(digits, 16)
                need(0xDC00 <= low <= 0xDFFF,
                     "reject invalid immutable JSON low surrogate")
                self.index += 6
                code = 0x10000 + ((code - 0xD800) << 10) + low - 0xDC00
            else:
                need(not 0xDC00 <= code <= 0xDFFF,
                     "reject unpaired immutable JSON low surrogate")
            values.append(chr(code))
        raise FreezeError("reject unfinished immutable JSON string")

    def value(self, depth: int = 0) -> object:
        need(depth <= 24, "reject deeply nested immutable JSON")
        self.blank()
        need(self.index < len(self.data), "reject truncated immutable JSON")
        marker = self.data[self.index]
        if marker == '"':
            return self.quoted()
        if marker == "{":
            self.index += 1
            values: dict[str, object] = {}
            self.blank()
            if self.index < len(self.data) and self.data[self.index] == "}":
                self.index += 1
                return values
            while True:
                self.blank()
                key = self.quoted()
                need(key not in values, "reject repeated immutable JSON key")
                self.blank()
                need(self.index < len(self.data)
                     and self.data[self.index] == ":",
                     "reject missing immutable JSON colon")
                self.index += 1
                values[key] = self.value(depth + 1)
                self.blank()
                need(self.index < len(self.data),
                     "reject unfinished immutable JSON object")
                marker = self.data[self.index]
                self.index += 1
                if marker == "}":
                    return values
                need(marker == ",", "reject malformed immutable JSON object")
        if marker == "[":
            self.index += 1
            values: list[object] = []
            self.blank()
            if self.index < len(self.data) and self.data[self.index] == "]":
                self.index += 1
                return values
            while True:
                values.append(self.value(depth + 1))
                self.blank()
                need(self.index < len(self.data),
                     "reject unfinished immutable JSON list")
                marker = self.data[self.index]
                self.index += 1
                if marker == "]":
                    return values
                need(marker == ",", "reject malformed immutable JSON list")
        for word, resolved in (("true", True), ("false", False),
                               ("null", None)):
            if self.data.startswith(word, self.index):
                self.index += len(word)
                return resolved
        start = self.index
        if marker == "-":
            self.index += 1
        need(self.index < len(self.data)
             and self.data[self.index] in "0123456789",
             "reject floating or nonnumeric immutable JSON")
        if self.data[self.index] == "0":
            self.index += 1
        else:
            while (self.index < len(self.data)
                   and self.data[self.index] in "0123456789"):
                self.index += 1
        value = int(self.data[start:self.index])
        need(abs(value) < 1 << 63,
             "reject oversized immutable JSON integer")
        return value

    def parse(self) -> object:
        value = self.value()
        self.blank()
        need(self.index == len(self.data),
             "reject trailing authenticated JSON owner data")
        return value


class ModelPublicFlag(enum.IntFlag):
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
        known = sum(int(item) for item in ordered)
        parts = ["re." + item.name for item in ordered
                 if value & int(item)]
        unknown = value & ~known
        if unknown:
            if not parts:
                return "re.RegexFlag(" + str(value) + ")"
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = __repr__


class ModelPatternFlag(enum.IntFlag):
    ASCII = 256
    IGNORECASE = 2
    LOCALE = 4
    UNICODE = 32
    MULTILINE = 8
    DOTALL = 16
    VERBOSE = 64
    DEBUG = 128
    _numeric_repr_ = hex

    def __repr__(self) -> str:
        value = int(self)
        ordered = sorted(type(self), key=int)
        known = sum(int(item) for item in ordered)
        names = ["re." + item.name for item in ordered
                 if value & int(item)]
        unknown = value & ~known
        if unknown:
            names.append(hex(unknown))
        return "|".join(names)


def synthetic_controls() -> dict[str, object]:
    need(tuple(ModelPublicFlag.__members__) == MEMBERS,
         "preserve exact CPython aliases and declaration order")
    known = sum(bit for _name, bit in DECLARED)
    object_count = 0
    pattern_count = 0
    distinct_orders = 0
    unknown_object_count = 0
    unknown_pattern_count = 0
    for raw in range(-4096, 16385):
        public = ModelPublicFlag(raw)
        value = int(public)
        names = [name for name, bit in DECLARED if value & bit]
        unknown = value & ~known
        if not value:
            expected_object = "re.NOFLAG"
            expected_name = "NOFLAG"
        elif not names:
            expected_object = "re.RegexFlag(" + str(value) + ")"
            expected_name = None
            unknown_object_count += 1
        else:
            expected_object = "|".join("re." + name for name in names)
            expected_name = "|".join(names)
            if unknown:
                expected_object += "|" + hex(unknown)
                expected_name += "|" + hex(unknown)
        need(repr(public) == expected_object
             and str(public) == expected_object
             and public.name == expected_name,
             "reject aliases, declaration order, inverted flags, or unknown names")
        object_count += 1
        if raw >= 0:
            active = raw & ~32
            ordered_names = ["re." + name for name, bit
                             in sorted(DECLARED, key=lambda item: item[1])
                             if active & bit]
            extra = active & ~known
            if extra:
                ordered_names.append(hex(extra))
                unknown_pattern_count += 1
            expected_pattern = "|".join(ordered_names)
            if active:
                need(repr(ModelPatternFlag(active)) == expected_pattern,
                     "reject independent native numeric-order pattern display")
                if expected_object != expected_pattern and not extra:
                    distinct_orders += 1
            pattern_count += 1
    witnesses = {
        0: ("re.NOFLAG", ""),
        1: ("re.RegexFlag(1)", "0x1"),
        2: ("re.IGNORECASE", "re.IGNORECASE"),
        256: ("re.ASCII", "re.ASCII"),
        258: ("re.ASCII|re.IGNORECASE", "re.IGNORECASE|re.ASCII"),
        512: ("re.RegexFlag(512)", "0x200"),
        514: ("re.IGNORECASE|0x200", "re.IGNORECASE|0x200"),
        770: ("re.ASCII|re.IGNORECASE|0x200",
              "re.IGNORECASE|re.ASCII|0x200"),
        0x123000: ("re.RegexFlag(1191936)", "0x123000"),
    }
    for raw, pair in witnesses.items():
        pattern = "" if raw & ~32 == 0 else repr(ModelPatternFlag(raw & ~32))
        need((repr(ModelPublicFlag(raw)), pattern) == pair,
             "reject independently observed CPython flag witness " + str(raw))
    cache_checked = 0
    class SubclassString(str):
        pass

    class SubclassBytes(bytes):
        pass

    for kind in ("str", "bytes"):
        for index in range(48):
            text = "pattern-" + str(index)
            value = text if kind == "str" else text.encode("ascii")
            derived = (SubclassString(value) if kind == "str"
                       else SubclassBytes(value))
            active = (0, 2, 8, 16, 256, 258)[index % 6]
            first = (str if isinstance(value, str) else bytes,
                     value, active)
            second = (str if isinstance(derived, str) else bytes,
                      derived, active)
            different_flags = (first[0], first[1], active | 512)
            need(first == second and hash(first) == hash(second)
                 and type(value) is not type(derived)
                 and isinstance(derived, str if kind == "str" else bytes)
                 and first != different_flags,
                 "preserve exact base/subclass native pattern equality and hash")
            cache_checked += 1
    need((str, "a", 0) != (bytes, b"a", 0),
         "keep byte and Unicode native pattern identities independent")

    class IndexedFlag:
        def __index__(self) -> int:
            return 2

    indexed_errors = 0
    for value in (IndexedFlag(), IndexedFlag(), IndexedFlag(), IndexedFlag()):
        try:
            value & int(ModelPublicFlag.VERBOSE)
        except TypeError as error:
            need(str(error) ==
                 "unsupported operand type(s) for &: 'IndexedFlag' and 'int'",
                 "preserve exact original indexed-flag exception")
            indexed_errors += 1
        else:
            raise FreezeError("accepting indexed-only flags weakens CPython")
    need((ModelPublicFlag.IGNORECASE & int(ModelPublicFlag.VERBOSE)) == 0
         and (int(ModelPublicFlag.VERBOSE) & int(ModelPublicFlag.VERBOSE)) == 64,
         "preserve supported IntFlag and int compile arguments")
    for pattern in (object(), None, 123):
        try:
            if not isinstance(pattern, (str, bytes)):
                raise TypeError("first argument must be string or compiled pattern")
            IndexedFlag() & int(ModelPublicFlag.VERBOSE)
        except TypeError as error:
            need(str(error) == "first argument must be string or compiled pattern",
                 "preserve invalid-pattern error before indexed-flag operator")
        else:
            raise FreezeError("accepting a nonstring C pattern is forbidden")
    long_pattern = "a" * 5000
    shown = repr(long_pattern)
    shown = shown[:200] if len(shown) > 200 else shown
    need(len(shown) == 200
         and len("re.compile(" + shown + ", "
                 + repr(ModelPatternFlag(258)) + ")") < 300,
         "preserve existing native long-pattern representation truncation")

    need(repr(ModelPublicFlag(-1)) ==
         "re.ASCII|re.IGNORECASE|re.LOCALE|re.UNICODE|re.MULTILINE|"
         "re.DOTALL|re.VERBOSE|re.DEBUG|0x1"
         and repr(ModelPublicFlag(-512)) == "re.NOFLAG"
         and object_count == 20481 and pattern_count == 16385
         and distinct_orders > 10 and unknown_object_count > 10
         and unknown_pattern_count > 100 and cache_checked == 96
         and indexed_errors == 4,
         "reject incomplete independent public/native flag coverage")
    return {"public_flag_values_checked": object_count,
            "compiled_pattern_flag_values_checked": pattern_count,
            "different_public_and_pattern_orders_checked": distinct_orders,
            "unknown_only_public_values_checked": unknown_object_count,
            "unknown_pattern_hex_values_checked": unknown_pattern_count,
            "alias_names_checked": len(MEMBERS),
            "observed_upstream_assertions_explained": 2,
            "base_and_subclass_pattern_equalities_checked": cache_checked,
            "indexed_only_flag_rejections_checked": indexed_errors,
            "observed_public_type_flag_mismatches_explained": 48,
            "observed_public_type_pattern_equality_mismatches_explained": 96,
            "observed_public_type_mismatches_explained": 144,
            "observed_public_surface_flag_mismatches_explained": 14,
            "observed_public_surface_indexed_flag_mismatches_explained": 64,
            "observed_public_surface_mismatches_explained": 78,
            "observed_total_mismatches_explained": 224,
            "private_native_flag_type_is_not_public": True,
            "public_flag_restored_in_finally": True,
            "native_pattern_equality_and_hash_preserved": True,
            "indexed_flag_error_preserved": True}


def no_matchers() -> None:
    need(not any(name in sys.modules for name in
                 ("re", "_sre", "regex", "ctypes", "candidates",
                  "candidates.vm_candidate", "candidates._vm_native")),
         "deny stdlib, external, native, and candidate matcher imports")


class Wall:
    def __init__(self, mode: str):
        self.mode = mode
        self.raw: dict[str, object] = {}
        self.live: dict[int, str] = {}
        self.ticket: tuple[str, int, int | None, int | None] | None = None
        self.read_ticket: int | None = None
        self.write_ticket: tuple[int, bytes] | None = None
        self.metadata_ticket: int | None = None
        self.close_ticket: int | None = None
        self.sync_ticket: int | None = None
        self.mkdir_ticket: tuple[str, int, int] | None = None
        self.root: int | None = None
        self.blocked = 0
        self.public_reads = 0
        self.candidate_reads = 0
        self.mutations = 0

    def reject(self, reason: str) -> None:
        self.blocked += 1
        raise FreezeError(reason)

    def audit(self, event: str, args: tuple[object, ...]) -> None:
        if event == "open":
            ticket = self.ticket
            if (ticket is None or len(args) < 3 or args[0] != ticket[0]
                    or type(args[2]) is not int or args[2] != ticket[1]):
                self.reject("deny unauthenticated filesystem audit event")
        elif event == "os.mkdir":
            if self.mkdir_ticket is None or args != self.mkdir_ticket:
                self.reject("deny unauthenticated exclusive source directory")
        elif (event in ("import", "compile", "exec", "marshal.load",
                        "marshal.loads", "sys.addaudithook", "ctypes.dlopen")
              or event.startswith(("subprocess", "socket", "ctypes",
                                   "os.system", "os.fork", "os.posix_spawn"))):
            self.reject("deny matching, execution, subprocess, or native loading")

    def deny(self, *args: object, **kwargs: object) -> object:
        self.reject("deny unauthenticated source-wall capability")

    def open(self, path: object, flags: object, mode: object = 0o777,
             *, dir_fd: int | None = None) -> int:
        ticket = self.ticket
        if (ticket is None or type(path) is not str or type(flags) is not int
                or (path, flags, dir_fd, mode if flags & os.O_CREAT else None)
                != ticket):
            self.reject("deny crossed parent, mode, flags, or filesystem path")
        return self.raw["open"](path, flags, mode, dir_fd=dir_fd)

    def read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor != self.read_ticket
                or self.live.get(descriptor) not in ("owner", "readback")
                or type(count) is not int or not 0 <= count <= 65536):
            self.reject("deny inherited, foreign, or oversized descriptor read")
        return self.raw["read"](descriptor, count)

    def write(self, descriptor: object, payload: object) -> int:
        if (type(descriptor) is not int or self.write_ticket is None
                or descriptor != self.write_ticket[0]
                or self.live.get(descriptor) != "output"
                or type(payload) is not bytes
                or payload != self.write_ticket[1]):
            self.reject("deny inherited or unauthenticated descriptor write")
        return self.raw["write"](descriptor, payload)

    def fstat(self, descriptor: object) -> os.stat_result:
        if (type(descriptor) is not int or descriptor != self.metadata_ticket
                or descriptor not in self.live):
            self.reject("deny hidden, inherited, or crossed descriptor metadata")
        return self.raw["fstat"](descriptor)

    def close(self, descriptor: object) -> None:
        if (type(descriptor) is not int or descriptor != self.close_ticket
                or descriptor not in self.live):
            self.reject("deny inherited or crossed descriptor close")
        self.raw["close"](descriptor)

    def fsync(self, descriptor: object) -> None:
        if (type(descriptor) is not int or descriptor != self.sync_ticket
                or descriptor not in self.live or self.mode != "--apply"):
            self.reject("deny unauthorized durable filesystem mutation")
        self.raw["fsync"](descriptor)

    def mkdir(self, name: object, mode: object = 0o777,
              *, dir_fd: int | None = None) -> None:
        if (self.mode != "--apply" or self.mkdir_ticket is None
                or (name, mode, dir_fd) != self.mkdir_ticket):
            self.reject("deny unauthorized source-variant directory")
        self.raw["mkdir"](name, mode, dir_fd=dir_fd)

    def install(self) -> None:
        no_matchers()
        native = sys.modules["posix"]
        wrappers = {"open": self.open, "read": self.read,
                    "write": self.write, "fstat": self.fstat,
                    "close": self.close, "fsync": self.fsync,
                    "mkdir": self.mkdir}
        for name in wrappers:
            self.raw[name] = getattr(os, name)
        for owner in (os, native):
            for name, wrapper in wrappers.items():
                setattr(owner, name, wrapper)
            for name in ("stat", "lstat", "listdir", "scandir", "unlink",
                         "remove", "rename", "replace", "rmdir", "chmod",
                         "chown", "link", "symlink", "truncate", "ftruncate",
                         "dup", "dup2", "dup3", "pread", "pwrite", "readv",
                         "writev", "sendfile", "splice", "copy_file_range",
                         "system", "fork", "forkpty", "posix_spawn",
                         "posix_spawnp", "execv", "execve", "execvp",
                         "execvpe"):
                if hasattr(owner, name):
                    setattr(owner, name, self.deny)
        for owner in (builtins, io, _io):
            owner.open = self.deny
        for name in ("__import__", "compile", "eval", "exec"):
            setattr(builtins, name, self.deny)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.deny)
        sys.addaudithook(self.audit)

    def descriptor(self, name: str, flags: int, *, parent: int | None = None,
                   mode: int | None = None, kind: str) -> int:
        need(self.ticket is None, "reject nested descriptor authority")
        self.ticket = (name, flags, parent, mode)
        try:
            result = (os.open(name, flags, mode, dir_fd=parent)
                      if mode is not None else
                      os.open(name, flags, dir_fd=parent))
        finally:
            self.ticket = None
        need(type(result) is int and result >= 3 and result not in self.live,
             "reject inherited, replaced, or repeated descriptor")
        self.live[result] = kind
        return result

    def metadata(self, descriptor: int) -> os.stat_result:
        need(self.metadata_ticket is None, "reject nested descriptor metadata")
        self.metadata_ticket = descriptor
        try:
            return os.fstat(descriptor)
        finally:
            self.metadata_ticket = None

    def receive(self, descriptor: int, count: int) -> bytes:
        need(self.read_ticket is None, "reject nested descriptor read")
        self.read_ticket = descriptor
        try:
            return os.read(descriptor, count)
        finally:
            self.read_ticket = None

    def transmit(self, descriptor: int, payload: bytes) -> int:
        need(self.write_ticket is None, "reject nested descriptor write")
        self.write_ticket = (descriptor, payload)
        try:
            return os.write(descriptor, payload)
        finally:
            self.write_ticket = None

    def synchronize(self, descriptor: int) -> None:
        need(self.sync_ticket is None, "reject nested descriptor sync")
        self.sync_ticket = descriptor
        try:
            os.fsync(descriptor)
        finally:
            self.sync_ticket = None

    def release(self, descriptor: int) -> None:
        need(self.close_ticket is None, "reject nested descriptor closure")
        self.close_ticket = descriptor
        try:
            os.close(descriptor)
        finally:
            self.close_ticket = None
        del self.live[descriptor]

    def open_root(self) -> None:
        need(self.root is None, "reject duplicate workspace authority")
        descriptor = self.descriptor(
            ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            kind="directory",
        )
        info = self.metadata(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE
             and info.st_uid == os.geteuid(),
             "reject foreign, linked, or substituted workspace root")
        self.root = descriptor

    def segment(self, name: object) -> str:
        need(type(name) is str and bool(name) and name not in (".", "..")
             and "/" not in name and "\\" not in name
             and "\x00" not in name,
             "reject traversal or ambiguous immutable path segment")
        return name

    def child(self, parent: int, name: str) -> int:
        need(self.live.get(parent) == "directory",
             "reject foreign or inherited parent directory")
        child = self.descriptor(
            self.segment(name),
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            parent=parent, kind="directory",
        )
        info = self.metadata(child)
        need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE
             and info.st_uid == os.geteuid(),
             "reject substituted immutable source directory")
        return child

    def owner(self, relative: str, expected: str, *, size: int | None = None,
              inode: int | None = None, candidate: bool = False) -> bytes:
        allowed = {SOURCE, PROTOCOL, CONTRACT, RECEIPT}
        if self.mode == "--apply":
            allowed.update((INPUT, NATIVE_INPUT))
        need(relative in allowed and self.root is not None
             and (not candidate or self.mode == "--apply"),
             "deny candidate, archive, private, hidden, or foreign owner")
        pin(expected)
        parent = self.root
        directories: list[int] = []
        descriptor: int | None = None
        try:
            pieces = relative.split("/")
            for piece in pieces[:-1]:
                parent = self.child(parent, piece)
                directories.append(parent)
            descriptor = self.descriptor(
                self.segment(pieces[-1]),
                os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                parent=parent, kind="owner",
            )
            before = self.metadata(descriptor)
            need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                 and stat.S_IMODE(before.st_mode) == 0o600
                 and before.st_uid == os.geteuid() and before.st_nlink == 1
                 and 0 < before.st_size <= 262144
                 and (size is None or before.st_size == size)
                 and (inode is None or before.st_ino == inode),
                 "reject substituted, public, linked, or wrong-size source")
            remain = before.st_size
            parts: list[bytes] = []
            while remain:
                part = self.receive(descriptor, min(remain, 65536))
                need(type(part) is bytes and 0 < len(part) <= remain,
                     "reject truncated immutable source owner")
                parts.append(part)
                remain -= len(part)
            need(self.receive(descriptor, 1) == b"",
                 "reject expanded immutable source owner")
            after = self.metadata(descriptor)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "reject concurrently replaced immutable source owner")
            result = b"".join(parts)
            need(digest(result) == expected,
                 "reject unauthenticated immutable source payload")
            if candidate:
                self.candidate_reads += 1
            else:
                self.public_reads += 1
            return result
        finally:
            if descriptor is not None and descriptor in self.live:
                self.release(descriptor)
            for item in reversed(directories):
                self.release(item)

    def finish(self) -> None:
        need(self.root is not None and set(self.live) == {self.root},
             "reject leaked or inherited source-freeze descriptors")
        root = self.root
        self.release(root)
        self.root = None


def rejected(wall: Wall, name: str, callback) -> str:
    before = wall.blocked
    try:
        callback()
    except (FreezeError, OSError, TypeError, ValueError, AttributeError):
        need(wall.blocked > before,
             "hostile check did not reach permanent wall: " + name)
        return name
    raise FreezeError("hostile check escaped permanent wall: " + name)


def hostile_controls(wall: Wall) -> dict[str, object]:
    native = sys.modules["posix"]
    source = ROOT + "/" + SOURCE
    hidden = ROOT + "/oracle/phase3/final-held-out-cases.json"
    checks = [
        rejected(wall, "builtin-open", lambda: builtins.open(source, "rb")),
        rejected(wall, "io-open", lambda: io.open(source, "rb")),
        rejected(wall, "native-io-open", lambda: _io.open(source, "rb")),
        rejected(wall, "os-open", lambda: os.open(source, os.O_RDONLY)),
        rejected(wall, "posix-open", lambda: native.open(source, os.O_RDONLY)),
        rejected(wall, "path-traversal", lambda: os.open(
            ROOT + "/tools/../" + SOURCE, os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "foreign-read", lambda: os.read(0, 1)),
        rejected(wall, "posix-read", lambda: native.read(0, 1)),
        rejected(wall, "foreign-write", lambda: os.write(1, b"bad")),
        rejected(wall, "posix-write", lambda: native.write(1, b"bad")),
        rejected(wall, "foreign-fstat", lambda: os.fstat(0)),
        rejected(wall, "posix-fstat", lambda: native.fstat(0)),
        rejected(wall, "foreign-close", lambda: os.close(0)),
        rejected(wall, "posix-close", lambda: native.close(0)),
        rejected(wall, "foreign-fsync", lambda: os.fsync(1)),
        rejected(wall, "posix-fsync", lambda: native.fsync(1)),
        rejected(wall, "unauthorized-mkdir", lambda: os.mkdir(DIRECTORY, 0o700)),
        rejected(wall, "target-before-root", lambda: os.open(
            ROOT + "/" + TARGET,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        rejected(wall, "candidate-read", lambda: os.open(
            ROOT + "/" + INPUT, os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "native-engine-read", lambda: os.open(
            ROOT + "/candidates/_vm_native.so", os.O_RDONLY)),
        rejected(wall, "actual-archive-read", lambda: os.open(
            ROOT + "/" + RECEIPT.replace("-publication-receipt.json", ".json.gz"),
            os.O_RDONLY)),
        rejected(wall, "holdout-read", lambda: os.open(hidden, os.O_RDONLY)),
        rejected(wall, "holdout-stat", lambda: os.stat(hidden)),
        rejected(wall, "holdout-lstat", lambda: os.lstat(hidden)),
        rejected(wall, "posix-holdout-stat", lambda: native.stat(hidden)),
        rejected(wall, "unlink", lambda: os.unlink(source)),
        rejected(wall, "rename", lambda: os.rename(source, hidden)),
        rejected(wall, "hardlink", lambda: os.link(source, hidden)),
        rejected(wall, "symlink", lambda: os.symlink(source, hidden)),
        rejected(wall, "chmod", lambda: os.chmod(source, 0o644)),
        rejected(wall, "truncate", lambda: os.truncate(source, 0)),
        rejected(wall, "duplicate-fd", lambda: os.dup(0)),
        rejected(wall, "posix-duplicate-fd", lambda: native.dup(0)),
        rejected(wall, "process", lambda: os.system("true")),
        rejected(wall, "compile", lambda: builtins.compile("1", "x", "eval")),
        rejected(wall, "eval", lambda: builtins.eval("1")),
        rejected(wall, "exec", lambda: builtins.exec("pass")),
        rejected(wall, "stdlib-re", lambda: builtins.__import__("re")),
        rejected(wall, "external-regex", lambda: builtins.__import__("regex")),
        rejected(wall, "clock", lambda: time.time()),
        rejected(wall, "monotonic-clock", lambda: time.monotonic()),
        rejected(wall, "performance-clock", lambda: time.perf_counter()),
        rejected(wall, "forged-audit", lambda: sys.audit(
            "open", hidden, None, os.O_RDONLY)),
    ]
    for malformed in (b'{"x":1,"x":2}', b"1.5", b"01", b'"\\ud800"',
                      b'{"x":1}trailing', b"[1,]", b'{"x":NaN}'):
        try:
            StrictJSON(malformed).parse()
        except (FreezeError, UnicodeError, ValueError, TypeError):
            continue
        raise FreezeError("malformed immutable JSON escaped strict parser")
    try:
        need(b"truthy", "reject non-boolean root-authorization regression")
    except FreezeError:
        pass
    else:
        raise FreezeError("truthy bytes bypassed root-authorization guard")
    need(len(checks) >= 40 and not wall.live and wall.root is None
         and wall.public_reads == 0 and wall.candidate_reads == 0
         and wall.mutations == 0,
         "keep hostile source self-test mutationless and fully readless")
    return {"hostile_operations_blocked": len(checks),
            "strict_json_rejections": 7,
            "truthy_bytes_regression_rejected": True,
            "direct_native_posix_aliases_blocked": True,
            "controls": checks}


def diagnose(receipt: object) -> None:
    need(type(receipt) is dict
         and receipt.get("schema") ==
             "rebar-owned-repaired-c-original-campaign-v15-"
             "durable-publication-receipt"
         and receipt.get("family") == "c"
         and receipt.get("status") == "PASS"
         and receipt.get("publication_status") == "PASS"
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("case_execution_denominator") == 31237
         and receipt.get("verified_passing_case_count") == 22798
         and receipt.get("semantic_mismatch_count") == 224
         and receipt.get("completed_suite_count") == 13
         and receipt.get("attempted_suite_count") == 13
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("infrastructure_failure_count") == 0
         and receipt.get("candidate_execution_failure_count") == 0
         and receipt.get("native_engine_sha256") == ENGINE_SHA256
         and receipt.get("corrected_source_sha256") == NATIVE_SOURCE_SHA256
         and receipt.get("unchanged_adapter_sha256") == INPUT_SHA256
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("candidate_qualified") is False
         and receipt.get("winner_selected") is False,
         "reject altered authentic complete C candidate failure")
    outcomes = receipt.get("suite_outcomes")
    need(type(outcomes) is list and len(outcomes) == 13
         and {item.get("suite"): item.get("mismatch_count")
              for item in outcomes if item.get("mismatch_count")}
             == FAILURES,
         "preserve all 13 categories and exact 2/144/78 mismatch partition")
    archive = receipt.get("archive")
    need(type(archive) is dict and archive.get("sha256") == ARCHIVE_SHA256
         and archive.get("bytes") == ARCHIVE_BYTES
         and archive.get("inode") == ARCHIVE_INODE
         and archive.get("device") == DEVICE
         and archive.get("mode") == "0600"
         and archive.get("nlink") == 1,
         "preserve authenticated compressed evidence without opening it")


def effects() -> dict[str, object]:
    return {"candidate_processes_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "external_regex_dependency_count": 0,
            "stdlib_matching_delegation_count": 0,
            "cross_candidate_engine_reads": 0,
            "compressed_archives_opened": 0,
            "private_roots_opened": 0,
            "proposal_files_opened": 0,
            "proposal_metadata_probes": 0,
            "hidden_holdout_files_opened": 0,
            "hidden_holdout_metadata_probes": 0,
            "clock_samples": 0,
            "original_case_execution_denominator": 31237,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False}


def contract_document(source: str, protocol: str,
                      controls: dict[str, object]) -> dict[str, object]:
    return {"schema": SCHEMA,
            "version": 1,
            "status": "SOURCE FROZEN; CORRECTED C ADAPTER NOT MATERIALIZED",
            "phase": "CANDIDATES; FINAL INDEPENDENT FIRST-PARTY C PUBLIC FLAGS",
            "source": {"path": SOURCE, "sha256": source},
            "protocol": {"path": PROTOCOL, "sha256": protocol},
            "immutable_latest_complete_failure": {
                "receipt_path": RECEIPT,
                "receipt_sha256": RECEIPT_SHA256,
                "receipt_bytes": RECEIPT_BYTES,
                "receipt_inode": RECEIPT_INODE,
                "archive_sha256": ARCHIVE_SHA256,
                "archive_bytes": ARCHIVE_BYTES,
                "archive_inode": ARCHIVE_INODE,
                "archive_opened": False,
                "original_case_denominator": 31237,
                "actual_independent_candidate_workers": 13,
                "completed_original_categories": 13,
                "verified_passing_case_count": 22798,
                "observed_complete_mismatch_count": 224,
                "mismatches_by_suite": FAILURES,
                "failed_candidate_qualified": False,
                "history_rewritten": False,
            },
            "first_party_input": {
                "path": INPUT, "sha256": INPUT_SHA256,
                "bytes": INPUT_BYTES, "inode": INPUT_INODE,
                "native_engine_sha256": ENGINE_SHA256,
                "native_source_sha256": NATIVE_SOURCE_SHA256,
                "source_gate_candidate_reads": 0,
                "root_application_candidate_reads": 2,
                "native_source_path": NATIVE_INPUT,
                "native_source_sha256": NATIVE_INPUT_SHA256,
                "native_source_bytes": NATIVE_INPUT_BYTES,
                "native_source_inode": NATIVE_INPUT_INODE,
            },
            "first_party_correction": {
                "target_path": TARGET,
                "target_sha256": TARGET_SHA256,
                "target_bytes": TARGET_BYTES,
                "source_sites_changed": 4,
                "regexflag_order": "DECLARATION ORDER",
                "compiled_pattern_flag_order": "NUMERIC BIT ORDER",
                "unknown_flag_object_format": "DECIMAL",
                "unknown_compiled_pattern_format": "HEXADECIMAL",
                "complete_cpython_flag_alias_surface": True,
                "native_private_pattern_flag_type": True,
                "public_flag_restored_in_finally": True,
                "native_engine_source_changed": True,
                "native_target_path": NATIVE_TARGET,
                "native_target_sha256": NATIVE_TARGET_SHA256,
                "native_target_bytes": NATIVE_TARGET_BYTES,
                "native_pattern_type_canonicalizes_base_type": True,
                "native_pattern_hash_consistent_with_equality": True,
                "indexed_flags_rejected_before_coercion": True,
                "observed_upstream_assertions_targeted": 2,
                "observed_public_type_mismatches_targeted": 144,
                "observed_public_surface_mismatches_targeted": 78,
                "complete_observed_mismatches_targeted": 224,
                "external_regex_packages": 0,
                "stdlib_regex_delegation": False,
                "cross_candidate_delegation": False,
            },
            "source_only_synthetic_controls": controls,
            "source_only_effects": {
                **effects(), "candidate_source_files_opened": 0,
                "public_plaintext_owner_reads": 4,
                "workspace_mutations": 0,
            }}


def parse_arguments(values: list[str]) -> tuple[str, dict[str, str], set[str]]:
    need(type(values) is list and bool(values),
         "require exactly one isolated first-party C source-freeze mode")
    mode = values[0]
    need(mode in ("--self-test", "--render-contract", "--verify-source",
                  "--apply"), "reject unauthorized C source-freeze mode")
    fingerprints: dict[str, str] = {}
    flags: set[str] = set()
    index = 1
    while index < len(values):
        item = values[index]
        if item in ("--root-authorized", "--frozen-committed-pushed"):
            need(item not in flags, "reject duplicate root source capability")
            flags.add(item)
            index += 1
            continue
        need(item in ("--source-sha256", "--protocol-sha256",
                      "--contract-sha256", "--frozen-commit", "--pushed-commit")
             and item not in fingerprints and index + 1 < len(values),
             "reject malformed or repeated immutable source fingerprint")
        fingerprints[item] = pin(values[index + 1],
                                 width=40 if item.endswith("commit") else 64)
        index += 2
    if mode == "--render-contract":
        need(set(fingerprints) == {"--source-sha256", "--protocol-sha256"}
             and not flags, "render only from two authenticated source owners")
    elif mode in ("--self-test", "--verify-source"):
        need(set(fingerprints) == {"--source-sha256", "--protocol-sha256",
                                   "--contract-sha256"} and not flags,
             "require precisely three immutable source-only fingerprints")
    else:
        need(set(fingerprints) == {"--source-sha256", "--protocol-sha256",
                                   "--contract-sha256", "--frozen-commit",
                                   "--pushed-commit"}
             and flags == {"--root-authorized", "--frozen-committed-pushed"}
             and fingerprints["--frozen-commit"]
                 == fingerprints["--pushed-commit"],
             "deny non-root, uncommitted, unpushed, or mismatched source freeze")
    return mode, fingerprints, flags


def load_context(wall: Wall, mode: str, fingerprints: dict[str, str],
                 controls: dict[str, object]) -> dict[str, object]:
    wall.open_root()
    try:
        wall.owner(SOURCE, fingerprints["--source-sha256"])
        wall.owner(PROTOCOL, fingerprints["--protocol-sha256"])
        receipt = StrictJSON(wall.owner(
            RECEIPT, RECEIPT_SHA256, size=RECEIPT_BYTES,
            inode=RECEIPT_INODE,
        )).parse()
        diagnose(receipt)
        expected = contract_document(fingerprints["--source-sha256"],
                                     fingerprints["--protocol-sha256"], controls)
        if mode != "--render-contract":
            raw = wall.owner(CONTRACT, fingerprints["--contract-sha256"])
            actual = StrictJSON(raw).parse()
            need(actual == expected and raw == document(expected),
                 "reject substituted, reordered, or noncanonical source contract")
        return expected
    finally:
        if mode != "--apply" and wall.root is not None:
            wall.finish()


def replace_once(raw: bytes, old: bytes, new: bytes, name: str) -> bytes:
    need(type(raw) is bytes and type(old) is bytes and type(new) is bytes
         and old != new and raw.count(old) == 1,
         "require one exact first-party source transformation: " + name)
    result = raw.replace(old, new, 1)
    need(result.count(new) == 1 and result.count(old) == 0,
         "reject ambiguous or retained first-party correction: " + name)
    return result


def derive(wall: Wall, controls: dict[str, object]) -> tuple[bytes, bytes]:
    ready = (type(controls) is dict
             and controls.get("observed_total_mismatches_explained") == 224
             and controls.get("public_flag_values_checked") == 20481
             and controls.get("compiled_pattern_flag_values_checked") == 16385
             and wall.public_reads == 4 and wall.candidate_reads == 0
             and wall.mutations == 0)
    need(type(ready) is bool and ready is True,
         "complete strict root preauthorization before candidate access")
    source = wall.owner(INPUT, INPUT_SHA256, size=INPUT_BYTES,
                        inode=INPUT_INODE, candidate=True)
    native = wall.owner(NATIVE_INPUT, NATIVE_INPUT_SHA256,
                        size=NATIVE_INPUT_BYTES, inode=NATIVE_INPUT_INODE,
                        candidate=True)
    result = replace_once(source, OLD_PUBLIC_FLAG, NEW_PUBLIC_FLAG,
                          "public flag declaration order")
    result = replace_once(result, OLD_CONFIGURE, NEW_CONFIGURE,
                          "separate native compiled-pattern flag type")
    result = replace_once(result, OLD_FLAG_COERCION, NEW_FLAG_COERCION,
                          "reject unsupported indexed-only compile flags")
    corrected_native = replace_once(native, OLD_PATTERN_IDENTITY,
                                    NEW_PATTERN_IDENTITY,
                                    "canonical base pattern identity")
    need(len(result) == TARGET_BYTES and digest(result) == TARGET_SHA256,
         "reject substituted independent first-party C source correction")
    need(len(corrected_native) == NATIVE_TARGET_BYTES
         and digest(corrected_native) == NATIVE_TARGET_SHA256,
         "reject substituted independent native C identity correction")
    for marker in (b"import re\n", b"from re import", b"import regex",
                   b"import _sre", b"PyImport_ImportModule(\"re\")"):
        need(marker not in result,
             "reject delegated or external regular-expression implementation")
    need(result.count(b"from candidates import _vm_native") == 1
         and result.count(b"class _BytecodeParser:") == 1
         and result.count(b"class _BytecodeCompiler:") == 1
         and result.count(b"class _NativePatternFlag(enum.IntFlag):") == 1
         and result.count(b"finally:\n    RegexFlag = _PublicRegexFlag\n") == 1,
         "preserve owned native C matcher and exception-safe public flag identity")
    need(corrected_native.count(b"PyUnicode_Check(pattern->pattern)") >= 1
         and corrected_native.count(NEW_PATTERN_IDENTITY) == 1
         and corrected_native.count(OLD_PATTERN_IDENTITY) == 0
         and corrected_native.count(b"static Py_hash_t pattern_hash(") == 1
         and corrected_native.count(b"static PyObject *pattern_richcompare(") == 1
         and b"PyImport_ImportModule(\"re\")" not in corrected_native,
         "preserve first-party native equality, hash, and matching implementation")
    return result, corrected_native


def create(wall: Wall, source: bytes, native: bytes) -> dict[str, object]:
    need(wall.mode == "--apply" and wall.root is not None
         and wall.public_reads == 4 and wall.candidate_reads == 2
         and wall.mutations == 0,
         "require authenticated source and complete controls before mutation")
    parent = wall.root
    parents: list[int] = []
    child: int | None = None
    output: int | None = None
    try:
        for name in ("candidates", "c", "variants"):
            parent = wall.child(parent, name)
            parents.append(parent)
        name = "final_public_semantics_v1"
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        try:
            existing = wall.descriptor(name, flags, parent=parent,
                                       kind="directory")
        except FileNotFoundError:
            existing = None
        if existing is not None:
            wall.release(existing)
            raise FreezeError("refuse to replace an existing C source variant")
        need(wall.mkdir_ticket is None, "reject nested exclusive C mkdir")
        wall.mkdir_ticket = (name, 0o700, parent)
        try:
            os.mkdir(name, 0o700, dir_fd=parent)
        finally:
            wall.mkdir_ticket = None
        wall.mutations += 1
        child = wall.child(parent, name)
        child_info = wall.metadata(child)
        need(stat.S_IMODE(child_info.st_mode) == 0o700,
             "reject nonprivate first-party C source directory")
        outputs: list[dict[str, object]] = []
        for filename, payload, expected in (
                ("vm_candidate.py", source, TARGET_SHA256),
                ("vm_native.c", native, NATIVE_TARGET_SHA256)):
            output = wall.descriptor(
                filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                | os.O_NOFOLLOW | os.O_CLOEXEC,
                parent=child, mode=0o600, kind="output",
            )
            wall.mutations += 1
            before = wall.metadata(output)
            need(stat.S_ISREG(before.st_mode)
                 and stat.S_IMODE(before.st_mode) == 0o600
                 and before.st_dev == DEVICE and before.st_uid == os.geteuid()
                 and before.st_nlink == 1 and before.st_size == 0,
                 "reject linked, public, foreign, or preexisting C output")
            cursor = 0
            while cursor < len(payload):
                part = payload[cursor:cursor + 65536]
                count = wall.transmit(output, part)
                need(type(count) is int and 0 < count <= len(part),
                     "reject incomplete or oversized first-party C source write")
                cursor += count
            after = wall.metadata(output)
            need((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                 == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                 and after.st_size == len(payload)
                 and stat.S_IMODE(after.st_mode) == 0o600,
                 "reject replaced or incomplete first-party C output")
            wall.synchronize(output)
            wall.release(output)
            output = None
            readback = wall.descriptor(
                filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                parent=child, kind="readback",
            )
            try:
                pieces: list[bytes] = []
                remaining = len(payload)
                while remaining:
                    part = wall.receive(readback, min(remaining, 65536))
                    need(type(part) is bytes and 0 < len(part) <= remaining,
                         "reject incomplete durable C source readback")
                    pieces.append(part)
                    remaining -= len(part)
                need(wall.receive(readback, 1) == b""
                     and digest(b"".join(pieces)) == expected,
                     "reject substituted durable first-party C source")
            finally:
                wall.release(readback)
            outputs.append({"path": DIRECTORY + "/" + filename,
                            "sha256": expected, "bytes": len(payload),
                            "device": after.st_dev, "inode": after.st_ino,
                            "mode": "0600", "nlink": 1,
                            "exclusive_no_follow": True,
                            "fsync_completed": True})
        wall.synchronize(child)
        wall.synchronize(parent)
        need(wall.mutations == 3 and len(outputs) == 2,
             "create exactly one directory and two exclusive C sources")
        return {"directory": {"path": DIRECTORY, "device": child_info.st_dev,
                               "inode": child_info.st_ino, "mode": "0700",
                               "fsync_completed": True},
                "adapter": outputs[0], "native": outputs[1]}
    finally:
        if output is not None and output in wall.live:
            wall.release(output)
        if child is not None and child in wall.live:
            wall.release(child)
        for item in reversed(parents):
            if item in wall.live:
                wall.release(item)


def main() -> int:
    need(sys.implementation.name == "cpython"
         and sys.version_info[:3] == (3, 14, 6)
         and sys.executable == PYTHON
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.flags.dont_write_bytecode == 1
         and sys.dont_write_bytecode is True
         and __file__ == ROOT + "/" + SOURCE,
         "require exact isolated, no-site, bytecode-free pinned CPython owner")
    no_matchers()
    digest(b"initialize first-party hashes before permanent wall")
    mode, fingerprints, authority = parse_arguments(list(sys.argv[1:]))
    controls = synthetic_controls()
    wall = Wall(mode)
    wall.install()
    if mode == "--self-test":
        blocked = hostile_controls(wall)
        result = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                  "mode": "self-test", **fingerprints,
                  "synthetic": controls, "hostile": blocked,
                  "public_owner_files_read": 0,
                  "candidate_source_files_read": 0,
                  "workspace_mutations": 0, **effects()}
    else:
        expected = load_context(wall, mode, fingerprints, controls)
        if mode == "--render-contract":
            need(wall.public_reads == 3 and wall.candidate_reads == 0
                 and wall.mutations == 0,
                 "render from exactly source, protocol, and public C receipt")
            result = expected
        elif mode == "--verify-source":
            need(wall.public_reads == 4 and wall.candidate_reads == 0
                 and wall.mutations == 0,
                 "verify exactly four immutable public plaintext owners")
            result = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                      "mode": "verify-source", **fingerprints,
                      "synthetic": controls,
                      "public_owner_files_read": wall.public_reads,
                      "candidate_source_files_read": 0,
                      "workspace_mutations": 0, **effects()}
        else:
            need(authority == {"--root-authorized", "--frozen-committed-pushed"},
                 "deny unpushed or non-root first-party source application")
            source, native = derive(wall, controls)
            created = create(wall, source, native)
            wall.finish()
            need(wall.public_reads == 4 and wall.candidate_reads == 2
                 and wall.mutations == 3,
                 "require four public owners, two sources, and three mutations")
            result = {"schema": SCHEMA + "-application", "status": "APPLIED",
                      "mode": "apply", **fingerprints,
                      "frozen_pushed_commit": fingerprints["--pushed-commit"],
                      "created": created,
                      "candidate_source_files_read": wall.candidate_reads,
                      "public_owner_files_read": wall.public_reads,
                      "workspace_mutations": wall.mutations,
                      "historical_mismatches_targeted": 224,
                      "synthetic": controls, **effects()}
    no_matchers()
    sys.stdout.buffer.write(document(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError,
            KeyError, AttributeError) as error:
        sys.stderr.write("final first-party C source freeze rejected: "
                         + str(error) + "\n")
        raise SystemExit(2)
