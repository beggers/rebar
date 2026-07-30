#!/usr/bin/env python3
"""Freeze the one-site first-party Rust changing-capture clamp correction.

Only the immutable V24 C source is read.  No candidate is imported or executed,
no native object or archive is opened, and the V2 holdout proposal is inspected
by pinned metadata only.  Materialization is a separate explicitly attested,
exclusive operation reserved for the root coordinator after the freeze push.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("source-only capture-clamp freeze must not import a matcher")

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
SCHEMA = "rebar-owned-rust-capture-clamp-semantics-v1-source-freeze"
SOURCE = "tools/apply_owned_rust_capture_clamp_semantics_v1.py"
PROTOCOL = "oracle/phase2/RUST-CAPTURE-CLAMP-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/rust-capture-clamp-semantics-v1.json"
VARIANT = "candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c"
PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
V24_BRIDGE_SHA256 = "1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0"
V24_BRIDGE_BYTES = 178860
DERIVED_BRIDGE_SHA256 = "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54"
DERIVED_BRIDGE_BYTES = 178805
ACTUAL_V24_SHA256 = "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09"
PROPOSAL_SHA256 = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
PROPOSAL_BYTES = 15561
PROPOSAL_INODE = 525920
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_ITEMS = 200_000
MAX_JSON_DEPTH = 80
SIZE_T_MAX = (1 << 64) - 1
NOT_MEASURED = "NOT MEASURED"

# Public plaintext plus exactly one independently authenticated V24 C source.
# role, relative path, complete SHA-256, bytes, device-2064 inode.
OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA256, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 524713),
    ("supplemental_oracle", "oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
     5288, 525082),
    ("campaign_v24_source", "tools/run_owned_repaired_rust_original_campaign_v24.py",
     "f855f73e320f4ec33063dac1f22c11b1977ba04a02e1f97dfddca1d0670f705d",
     83262, 429270),
    ("campaign_v24_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V24.md",
     "d482cf8d06f9f328c08fda43a63db79db408e2421bad24e6e047ad507ef70431",
     6617, 525887),
    ("campaign_v24_contract", "oracle/phase2/repaired-rust-original-campaign-v24.json",
     "605737aa5060b78eb3802c8b3e58954a680bdf08b6f62a402de453552a0cd8f4",
     14607, 525907),
    ("build_v24_source",
     "tools/reproduce_owned_rust_capture_shape_semantics_v2_source_build_v24.py",
     "5bf779c3f9df24814565c2342dd2972254c2703d6f08d771c4096b5152683ac2",
     136322, 431516),
    ("build_v24_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2-SOURCE-BUILD-V24.md",
     "273ba50f4629961ed61e666593d9af49f9b49fbc73c83564d2453c3bf017b101",
     7361, 525609),
    ("build_v24_contract", "oracle/phase2/rust-capture-shape-semantics-v2-source-build-v24.json",
     "cd1a77792bbb9822bfe3e05f0005bb0629c05ecd16daa68a3e11337130a54876",
     578498, 525612),
    ("build_v24_receipt",
     "oracle/phase2/evidence/native-source-build-v24-rust-"
     "phase2-v24-rust-capture-shape-v2-root-provenance-publication-receipt.json",
     "da4edc2ff3352aab2a7b0c992286534b38dce422fd258f1fe1531464a277d6e4",
     4229, 525876),
    ("actual_v24_failure",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v24-rust-capture-shape-v2-root-provenance-"
     "original-p0-v24-failures-publication-receipt.json",
     ACTUAL_V24_SHA256, 11832, 525952),
    ("v24_corrected_first_party_bridge",
     "candidates/rust/variants/buffer_shape_pickle_findall_captures_semantics_v2/py_bridge.c",
     V24_BRIDGE_SHA256, V24_BRIDGE_BYTES, 525539),
)

SUITES = (
    ("original_bounded_v5", 151, 0, 151, "PASS", 81, 0,
     "176922acbce939c2875bffa7ea889c769bfee94467d1a4740260cc3862bc31e9"),
    ("public_v3", 864, 0, 864, "PASS", 83, 0,
     "97feb141e59589eae0dab58d06bb5a92c5d6a8e2ee14e874e2044f27548aa955"),
    ("scanner_v3", 1024, 0, 1024, "PASS", 84, 0,
     "a227261b738ae5faf93c48cd0dce21a66ecbf1fe55cbab668dc4bbacfc626a64"),
    ("buffer_v3", 768, 0, 768, "PASS", 85, 0,
     "98288e40950a2ca1c7cad937b6f50795143decc6b3f4d95942c44e366a9e6edd"),
    ("managed_v1", 1024, 0, 1024, "PASS", 86, 0,
     "bde1fe4f5ae5b1fd98d0a9a1415881935fd0eaa22f02fe60a86a963d72251c48"),
    ("scanner_verbose_v1", 2854, 0, 2854, "PASS", 87, 0,
     "a50902b4a878bc5844a2f025ce2a59469afad2dc71dc1de173a3c42375c7914a"),
    ("public_types_v1", 6912, 0, 6912, "PASS", 88, 0,
     "813db78cfc6ad10454186d03c9d866efe7540232140450913493c5c4dce1adbd"),
    ("substitution_v2", 5120, 240, 0, "SEMANTIC MISMATCH", 89, 1,
     "ee6e4d7fe0077f1c4298c5991fc1f556a961eb4b46ca5906b6b3573c5d266cdf"),
    ("shape_v2", 10240, 1112, 0, "SEMANTIC MISMATCH", 90, 1,
     "254582f93e213c9539ea406d12efd2057143d230a1395e85d1b04ee40021228a"),
    ("public_surface_v19", 1376, 0, 1376, "PASS", 91, 0,
     "4408b0f5c724fb259f4bbdfd362f751b9f9703116790ddf5abbef059901c9aa6"),
    ("subinterpreter_v2", 128, 0, 128, "PASS", 188, 0,
     "a09f5b7851006f3d3aec30c2f6bee49770e32a9c1b99cd6e439c2f8bc1408c9f"),
    ("pep688_v4", 264, 0, 264, "PASS", 189, 0,
     "3562b902c21997604282dd77f45cec2b907d7b091d8df371d7550bf7fc39d9e6"),
    ("threaded_pattern_v1", 512, 0, 512, "PASS", 190, 0,
     "593bc9a362592b5616d95d87763b6b47d11522c9a6f53090a747e33b2ff1fa4c"),
)

ORIGINAL_CAPTURE_FUNCTION = b"""static int rust_output_capture(
    RustOutputWriter *writer,
    const RustSubject *subject,
    size_t begin,
    size_t end
) {
    if (writer->text || PyBytes_CheckExact(subject->object)) {
        return rust_output_subject(writer, subject, begin, end);
    }

    RustSubject capture;
    if (!rust_subject_open(&capture, NULL, subject->object, 0)) {
        return -1;
    }
    if (end > capture.length) {
        rust_subject_release(&capture);
        PyErr_SetString(
            PyExc_BufferError,
            "Rust captured buffer changed size during replacement"
        );
        return -1;
    }
    int result = rust_output_subject(writer, &capture, begin, end);
    rust_subject_release(&capture);
    return result;
}
"""

CORRECTED_CAPTURE_FUNCTION = b"""static int rust_output_capture(
    RustOutputWriter *writer,
    const RustSubject *subject,
    size_t begin,
    size_t end
) {
    if (writer->text || PyBytes_CheckExact(subject->object)) {
        return rust_output_subject(writer, subject, begin, end);
    }

    RustSubject capture;
    if (!rust_subject_open(&capture, NULL, subject->object, 0)) {
        return -1;
    }
    size_t first = begin > capture.length ? capture.length : begin;
    size_t finish = end > capture.length ? capture.length : end;
    if (finish < first) finish = first;
    int result = rust_output_subject(writer, &capture, first, finish);
    rust_subject_release(&capture);
    return result;
}
"""


class FreezeError(Exception):
    """Frozen evidence, exact source anchors, or isolation changed."""


def require(value: object, label: str) -> None:
    if value is not True:
        raise FreezeError(label)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete genuine bytes only")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require a complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "JSON string must be genuine text")
    replacements = {"\"": "\\\"", "\\": "\\\\", "\b": "\\b",
                    "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for char in value:
        point = ord(char)
        require(not 0xD800 <= point <= 0xDFFF, "reject unpaired JSON surrogate")
        result.append(replacements.get(char, "\\u" + format(point, "04x")
                      if point < 32 else char))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive JSON depth")
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
        require(all(type(item) is str for item in value), "reject nontext JSON key")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject nonfinite or unsupported evidence JSON")


class StrictJSON:
    """Bounded duplicate-rejecting JSON without importing json or regex."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require bounded complete strict JSON bytes")
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
                    "reject invalid JSON Unicode escape")
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

    def number(self) -> int:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject incomplete JSON integer")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject leading-zero JSON integer")
        else:
            require(self.text[self.index] in "123456789", "reject invalid integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        require(self.index - start <= 128, "reject oversized evidence integer")
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                "reject floating or nonfinite evidence")
        return int(self.text[start:self.index])

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject deep evidence JSON")
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
                        "reject missing JSON object colon")
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
            values: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return values
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON array")
                values.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return values
                require(separator == ",", "reject malformed JSON array")
        if char == "-" or char in "0123456789":
            return self.number()
        for literal, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return value
        raise FreezeError("reject malformed or nonfinite JSON value")

    def decode(self) -> object:
        value = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing evidence bytes")
        return value


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "rebar", "subprocess", "socket",
                 "threading", "multiprocessing", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject candidate, regular-expression engine, native loader, or worker")


class SourceWall:
    """Deny-default descriptors, one metadata-only proposal, optional one write."""

    def __init__(self, apply: bool = False) -> None:
        self.allowed = frozenset(
            (ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT)
            + tuple(ROOT + "/" + row[1] for row in OWNERS)
        )
        self.apply = apply
        self.target = ROOT + "/" + VARIANT
        self.target_parent = self.target.rsplit("/", 1)[0]
        self.proposal = ROOT + "/" + PROPOSAL
        self.live: set[int] = set()
        self.output: int | None = None
        self.output_opened = False
        self.directory_created = False
        self.proposal_stat_count = 0
        self.proposal_open_count = 0
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.native_open = os.open
        self.native_read = os.read
        self.native_write = os.write
        self.native_fstat = os.fstat
        self.native_close = os.close
        self.native_fsync = os.fsync
        self.native_lstat = os.lstat
        self.native_mkdir = os.mkdir

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise FreezeError("source-only physical isolation rejected " + category)

    def approved_read(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/") and path == os.path.normpath(path)
                and not any(item in (".", "..") for item in path.split("/"))
                and not path.endswith((".so", ".gz")))

    def approved_write(self, path: object, flags: object) -> bool:
        required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        forbidden = os.O_RDWR | os.O_TRUNC | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
        return (self.apply and path == self.target and type(flags) is int
                and flags & required == required and not flags & forbidden
                and not self.output_opened and self.directory_created)

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                           | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (self.approved_read(path) and type(flags) is int
                    and not flags & destructive
                    and flags & getattr(os, "O_NOFOLLOW", 0)
                    and not type(mode) is str and False):
                return
            if (self.approved_read(path) and type(flags) is int
                    and not flags & destructive
                    and flags & getattr(os, "O_NOFOLLOW", 0)
                    and not (type(mode) is str and any(item in mode for item in "wax+"))):
                return
            if self.approved_write(path, flags):
                return
            if path == self.proposal:
                self.proposal_open_count += 1
            self.deny("unowned-source-native-archive-holdout-or-write-open")
        if event == "os.mkdir":
            path = args[0] if args else None
            if self.apply and path == self.target_parent and not self.directory_created:
                return
            self.deny("unauthorized-directory-mutation")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.rmdir",
                      "os.chmod", "os.chown", "os.urandom", "os.getrandom",
                      "_interpreters.create", "_interpreters.exec",
                      "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.",
                                     "tempfile.", "time.", "os.exec", "os.spawn"))):
            self.deny("candidate-process-network-native-clock-or-dynamic-code")

    def forbidden(self, category: str):
        def reject(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return reject

    def guarded_open(self, path: object, flags: object,
                     mode: int = 0o777, *, dir_fd: object = None) -> int:
        if dir_fd is not None:
            self.deny("foreign-directory-descriptor")
        write = self.approved_write(path, flags)
        read = (self.approved_read(path) and type(flags) is int
                and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                 | os.O_TRUNC | os.O_APPEND
                                 | getattr(os, "O_TMPFILE", 0)
                                 | getattr(os, "O_DIRECTORY", 0))
                and bool(flags & getattr(os, "O_NOFOLLOW", 0)))
        if not write and not read:
            self.deny("unowned-direct-os-open")
        assert isinstance(path, str) and isinstance(flags, int)
        descriptor = self.native_open(path, flags, mode)
        require(type(descriptor) is int and descriptor >= 0
                and descriptor not in self.live and descriptor != self.output,
                "reject invalid or reused source-wall descriptor")
        if write:
            self.output_opened = True
            self.output = descriptor
        else:
            self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor not in self.live
                or type(count) is not int or count < 0 or count > MAX_OWNER_BYTES):
            self.deny("foreign-or-unbounded-descriptor-read")
        assert isinstance(descriptor, int) and isinstance(count, int)
        return self.native_read(descriptor, count)

    def guarded_write(self, descriptor: object, value: object) -> int:
        if (not self.apply or descriptor != self.output
                or type(value) not in (bytes, memoryview)):
            self.deny("unowned-source-archive-or-stdout-write")
        assert isinstance(descriptor, int)
        return self.native_write(descriptor, value)

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if (type(descriptor) is not int
                or descriptor not in self.live and descriptor != self.output):
            self.deny("foreign-descriptor-metadata")
        assert isinstance(descriptor, int)
        return self.native_fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int:
            self.deny("foreign-descriptor-close")
        if descriptor == self.output:
            self.native_close(descriptor)
            self.output = None
            return
        if descriptor not in self.live:
            self.deny("foreign-descriptor-close")
        self.live.remove(descriptor)
        self.native_close(descriptor)

    def guarded_fsync(self, descriptor: object) -> None:
        if not self.apply or descriptor != self.output:
            self.deny("foreign-descriptor-sync")
        assert isinstance(descriptor, int)
        self.native_fsync(descriptor)

    def guarded_lstat(self, path: object, *, dir_fd: object = None) -> os.stat_result:
        if path != self.proposal or dir_fd is not None:
            self.deny("unowned-source-private-native-or-holdout-metadata")
        require(self.proposal_stat_count == 0, "inspect the unopened V2 proposal only once")
        assert isinstance(path, str)
        result = self.native_lstat(path)
        self.proposal_stat_count += 1
        return result

    def guarded_mkdir(self, path: object, mode: int = 0o777,
                      *, dir_fd: object = None) -> None:
        if (not self.apply or path != self.target_parent or dir_fd is not None
                or self.directory_created or mode != 0o700):
            self.deny("unauthorized-source-directory-mutation")
        assert isinstance(path, str)
        self.native_mkdir(path, mode)
        self.directory_created = True

    def install(self) -> None:
        require(not self.installed, "install each source-only wall exactly once")
        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        if hasattr(_io, "open_code"):
            _io.open_code = self.forbidden("direct-_io-open-code")
        if hasattr(io, "open_code"):
            io.open_code = self.forbidden("direct-io-open-code")
        os.open = self.guarded_open
        os.read = self.guarded_read
        os.write = self.guarded_write
        os.fstat = self.guarded_fstat
        os.close = self.guarded_close
        os.fsync = self.guarded_fsync
        os.lstat = self.guarded_lstat
        os.mkdir = self.guarded_mkdir
        for name in ("fdopen", "dup", "dup2", "stat", "readlink", "listdir",
                     "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
                     "posix_spawnp", "system", "makedirs", "remove", "unlink",
                     "rename", "replace", "rmdir", "chmod", "chown", "urandom",
                     "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("direct-os-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall, row: tuple) -> bytes:
    role, relative, expected, count, inode = row
    checked_sha(expected, relative)
    require(type(role) is str and type(relative) is str
            and type(count) is int and 0 < count <= MAX_OWNER_BYTES
            and type(inode) is int and inode > 0,
            "reject incomplete pinned plaintext owner")
    path = ROOT + "/" + relative
    require(wall.installed and wall.approved_read(path),
            "install physical wall before reading frozen owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_nlink == 1
                and before.st_uid == os.geteuid(),
                "reject substituted complete frozen owner: " + role)
        left = count
        blocks: list[bytes] = []
        while left:
            block = os.read(descriptor, min(left, 65536))
            require(type(block) is bytes and bool(block),
                    "reject truncated frozen owner: " + role)
            blocks.append(block)
            left -= len(block)
        require(os.read(descriptor, 1) == b"", "reject grown frozen owner: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, field) == getattr(after, field)
                    for field in ("st_dev", "st_ino", "st_size", "st_nlink",
                                  "st_mtime_ns", "st_ctime_ns")),
                "reject concurrently replaced frozen owner: " + role)
        result = b"".join(blocks)
        require(digest(result) == expected, "reject changed frozen owner: " + role)
        return result
    finally:
        os.close(descriptor)


def dynamic_owner(wall: SourceWall, role: str, relative: str, expected: str) -> tuple:
    require(relative in (SOURCE, PROTOCOL, CONTRACT), "reject unrelated live freeze owner")
    checked_sha(expected, relative)
    path = ROOT + "/" + relative
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        found = os.fstat(descriptor)
        require(stat.S_ISREG(found.st_mode) and stat.S_IMODE(found.st_mode) == 0o600
                and found.st_dev == DEVICE and found.st_uid == os.geteuid()
                and found.st_nlink == 1 and 0 < found.st_size <= MAX_OWNER_BYTES,
                "reject exchanged live frozen owner: " + role)
        return role, relative, expected, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


def proposal_metadata(wall: SourceWall) -> dict:
    found = os.lstat(ROOT + "/" + PROPOSAL)
    require(stat.S_ISREG(found.st_mode) and stat.S_IMODE(found.st_mode) == 0o600
            and found.st_dev == DEVICE and found.st_ino == PROPOSAL_INODE
            and found.st_size == PROPOSAL_BYTES and found.st_nlink == 1
            and found.st_uid == os.geteuid(),
            "reject substituted metadata-only unopened V2 holdout proposal")
    require(wall.proposal_open_count == 0 and wall.proposal_stat_count == 1,
            "never open the independently pinned V2 proposal")
    return {
        "path": PROPOSAL, "sha256_independently_pinned_not_read": PROPOSAL_SHA256,
        "bytes_metadata_only": PROPOSAL_BYTES, "device": DEVICE,
        "inode_metadata_only": PROPOSAL_INODE, "mode": "0600",
        "proposal_status": "PRE-PHASE-3 PROPOSAL",
        "case_count": 141557760, "original_case_count": 31237,
        "final_protocol_status": "NOT FROZEN",
        "case_status": "NOT GENERATED; NOT OPENED",
        "proposal_content_read": False, "proposal_file_open_count": 0,
        "metadata_probe_count": 1, "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
    }


def json_object(raw: bytes, label: str) -> dict:
    value = StrictJSON(raw).decode()
    require(type(value) is dict, "require one complete strict JSON object: " + label)
    assert isinstance(value, dict)
    return value


def validate_original_oracle(value: dict) -> None:
    expected = {
        "schema": "rebar-cpython-re-p0-completeness-v4", "status": "PASS",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13, "original_named_private_waiver_count": 13,
        "original_crosswalk_count": 34, "original_obligation_count": 73,
        "qualified_candidate_count": 0, "holdout": "NOT OPENED",
        "performance": NOT_MEASURED,
    }
    require(all(value.get(key) == item for key, item in expected.items()),
            "reject changed complete original 31,237-case correctness boundary")
    phase = value.get("phase_gate")
    original = value.get("original_oracle")
    separate = value.get("actual_supplemental_two_reference")
    require(type(phase) is dict and phase.get("status") == "PASS"
            and phase.get("final_holdout_authorized") is False
            and phase.get("performance_oracle_authorized") is False,
            "never authorize held-out cases or timing in phase two")
    require(type(original) is dict and original.get("case_execution_denominator") == 31237
            and original.get("suite_count") == 13
            and original.get("named_private_waiver_count") == 13
            and original.get("crosswalk_count") == 34
            and original.get("total_named_obligation_count") == 73,
            "preserve every original suite, crosswalk, and named waiver")
    suites = original.get("suites")
    require(type(suites) is list and len(suites) == len(SUITES)
            and [(row.get("id"), row.get("case_execution_count")) for row in suites]
            == [(row[0], row[1]) for row in SUITES],
            "preserve the ordered complete 13-suite original denominator")
    require(type(separate) is dict and separate.get("actual_reference_worker_count") == 2
            and separate.get("case_count_per_worker") == [8244, 8244]
            and separate.get("failed_per_worker") == [0, 0]
            and separate.get("case_denominator_included_in_original_31237") is False,
            "never merge the two 8,244-case reference vectors into original P0")


def validate_supplemental(value: dict) -> None:
    require(value.get("schema") == "rebar-owned-differential-fuzz-reference-v3"
            and value.get("original_case_execution_denominator") == 31237
            and value.get("original_suite_count") == 13
            and value.get("case_denominator_included_in_original_31237") is False
            and type(value.get("supplemental_corpus")) is dict
            and value["supplemental_corpus"].get("case_count") == 8244
            and value["supplemental_corpus"].get("unique_record_case_count") == 8244
            and type(value.get("seeds")) is dict and len(value["seeds"]) == 7,
            "preserve the distinct original supplemental reference history")


def validate_v24_campaign(value: dict) -> None:
    require(value.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v24-recoverable-source-freeze"
            and value.get("version") == 24 and value.get("family") == "rust"
            and value.get("goal_sha256") == GOAL_SHA256
            and value.get("source", {}).get("sha256") == OWNERS[3][2]
            and value.get("protocol", {}).get("sha256") == OWNERS[4][2],
            "preserve the full immutable original V24 campaign source contract")
    build = value.get("actual_v24_native_build")
    boundary = value.get("original_correctness_boundary")
    effects = value.get("source_only_effects")
    require(type(build) is dict and build.get("build_status") == "PASS"
            and build.get("actual_compiler_process_count") == 28
            and build.get("corrected_bridge_source_sha256") == V24_BRIDGE_SHA256
            and build.get("corrected_bridge_source_bytes") == V24_BRIDGE_BYTES
            and build.get("complete_contract_sha256") == OWNERS[8][2]
            and build.get("publication_receipt", {}).get("sha256") == OWNERS[9][2]
            and build.get("archive_opened") is False,
            "preserve actual authenticated first-party V24 native provenance")
    require(type(boundary) is dict and boundary.get("case_execution_denominator") == 31237
            and boundary.get("suite_count") == 13
            and boundary.get("named_private_waiver_count") == 13
            and boundary.get("supplemental_reference_case_count") == 8244
            and boundary.get("supplemental_counted_in_original_denominator") is False
            and boundary.get("corrected_reference_case_count") == 6912
            and boundary.get("corrected_reference_counted_in_original_denominator") is False,
            "preserve the exact original, supplemental, and corrected references")
    require(type(effects) is dict and effects.get("candidate_workers_started") == 0
            and effects.get("clock_samples") == 0
            and effects.get("holdout_cases_opened") == 0
            and effects.get("holdout") == "NOT OPENED"
            and effects.get("performance") == NOT_MEASURED,
            "preserve the immutable campaign freeze without reopening workers")


def validate_v24_build(contract: dict, receipt: dict) -> None:
    require(contract.get("schema")
            == "rebar-phase2-owned-rust-capture-shape-semantics-v2-source-build-v24-source-freeze"
            and contract.get("version") == 24 and contract.get("family") == "rust"
            and contract.get("source", {}).get("sha256") == OWNERS[6][2]
            and contract.get("protocol", {}).get("sha256") == OWNERS[7][2]
            and contract.get("goal_sha256") == GOAL_SHA256,
            "preserve the independently authenticated full V24 build source freeze")
    require(receipt.get("schema")
            == "rebar-phase2-owned-rust-capture-shape-semantics-v2-source-build-v24-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == "rust"
            and receipt.get("source_sha256") == OWNERS[6][2]
            and receipt.get("protocol_sha256") == OWNERS[7][2]
            and receipt.get("contract_sha256") == OWNERS[8][2]
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("candidate_matching") == "NOT RUN"
            and receipt.get("candidate_qualified") is False
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("performance") == NOT_MEASURED,
            "preserve the genuine first-party V24 native-build publication receipt")


def validate_actual_v24(value: dict) -> None:
    expected = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v24-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "family": "rust",
        "label": "phase2-v24-rust-capture-shape-v2-root-provenance-original-p0-v24",
        "campaign_source_sha256": OWNERS[3][2],
        "campaign_protocol_sha256": OWNERS[4][2],
        "campaign_contract_sha256": OWNERS[5][2],
        "case_execution_denominator": 31237, "suite_count": 13,
        "named_private_waiver_count": 13, "attempted_suite_count": 13,
        "started_suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "verified_passing_case_count": 15877,
        "semantic_mismatch_count": 1352, "infrastructure_failure_count": 0,
        "all_original_observation_vectors_complete": True,
        "all_original_suite_rows_validated_before_publication": True,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "combined_bridge_source_sha256": V24_BRIDGE_SHA256,
        "combined_bridge_source_bytes": V24_BRIDGE_BYTES,
        "actual_v24_build_source_sha256": OWNERS[6][2],
        "actual_v24_build_protocol_sha256": OWNERS[7][2],
        "actual_v24_build_contract_sha256": OWNERS[8][2],
        "actual_v24_build_receipt_sha256": OWNERS[9][2],
        "actual_v24_build_archive_read_count": 0,
        "actual_v24_build_archive_gzip_inflation_count": 0,
        "actual_v24_compiler_process_count": 28,
        "corrected_reference_case_count": 6912,
        "candidate_run_uses_both_complete_reference_vectors": True,
        "worker_failure_capture_count": 0,
        "all_worker_failure_capture_count": 0,
        "worker_failure_capture_complete": True,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "holdout": "NOT OPENED", "performance": NOT_MEASURED,
        "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
        "winner_selected": False,
    }
    require(all(value.get(key) == item for key, item in expected.items()),
            "never report V24 durable publication as candidate correctness")
    rows = value.get("suite_integrity")
    require(type(rows) is list and len(rows) == len(SUITES),
            "preserve all 13 fully observed independent V24 suites")
    pids: set[int] = set()
    expected_fields = {"actual_worker_started", "case_execution_denominator",
                       "complete_original_row_sha256", "failure_class",
                       "fully_observed", "mismatch_count", "pid", "returncode",
                       "suite", "verified_passing_case_count", "worker_attempted"}
    for row, frozen in zip(rows, SUITES, strict=True):
        require(type(row) is dict and set(row) == expected_fields,
                "reject omitted or invented V24 suite fields: " + frozen[0])
        actual = (row.get("suite"), row.get("case_execution_denominator"),
                  row.get("mismatch_count"), row.get("verified_passing_case_count"),
                  row.get("failure_class"), row.get("pid"), row.get("returncode"),
                  row.get("complete_original_row_sha256"))
        require(actual == frozen and row.get("fully_observed") is True
                and row.get("actual_worker_started") is True
                and row.get("worker_attempted") is True and frozen[5] not in pids,
                "reject changed complete actual V24 suite: " + frozen[0])
        pids.add(frozen[5])
    require(sum(row[1] for row in SUITES) == 31237
            and sum(row[2] for row in SUITES) == 1352
            and sum(row[3] for row in SUITES) == 15877
            and SUITES[7][2] == 240 and SUITES[8][2] == 1112
            and value.get("actual_worker_process_ids") == [row[5] for row in SUITES],
            "preserve the actual 240 substitution plus exactly 1,112 shape failures")


def derive_bridge(source: bytes) -> bytes:
    require(type(source) is bytes and len(source) == V24_BRIDGE_BYTES
            and digest(source) == V24_BRIDGE_SHA256,
            "start from the entire independently frozen V24 first-party bridge")
    require(source.count(ORIGINAL_CAPTURE_FUNCTION) == 1
            and source.count(CORRECTED_CAPTURE_FUNCTION) == 0
            and source.count(b"static int rust_output_capture(\n") == 1,
            "require exactly one complete unique capture-output function anchor")
    original = ORIGINAL_CAPTURE_FUNCTION
    corrected = CORRECTED_CAPTURE_FUNCTION
    prefix = b"    if (writer->text || PyBytes_CheckExact(subject->object)) {\n"
    acquisition = b"    if (!rust_subject_open(&capture, NULL, subject->object, 0)) {\n"
    release = b"    rust_subject_release(&capture);\n    return result;\n"
    require(original.count(prefix) == corrected.count(prefix) == 1
            and original.count(acquisition) == corrected.count(acquisition) == 1
            and original.endswith(release + b"}\n")
            and corrected.endswith(release + b"}\n")
            and original.count(b"rust_subject_open(") == 1
            and corrected.count(b"rust_subject_open(") == 1
            and original.count(b"rust_output_subject(") == 2
            and corrected.count(b"rust_output_subject(") == 2
            and b"PyExc_BufferError" in original
            and b"PyExc_BufferError" not in corrected
            and b"size_t first = begin > capture.length ? capture.length : begin;\n"
            in corrected
            and b"size_t finish = end > capture.length ? capture.length : end;\n"
            in corrected
            and b"if (finish < first) finish = first;\n" in corrected,
            "preserve fast paths, acquisition, release, and exact CPython clamping")
    forbidden = (b'PyImport_ImportModule("re")', b'PyImport_ImportModule("_sre")',
                 b'PyImport_ImportModule("regex")', b"#include <regex.h>",
                 b"#include <pcre", b"dlopen(", b"PyRun_", b"system(",
                 b"subprocess", b"fallback")
    require(not any(marker in corrected for marker in forbidden),
            "never add external regex, stdlib delegation, native loader, or fallback")
    updated = source.replace(original, corrected, 1)
    require(updated.count(corrected) == 1 and updated.count(original) == 0
            and len(updated) == DERIVED_BRIDGE_BYTES
            and digest(updated) == DERIVED_BRIDGE_SHA256
            and updated.replace(corrected, original, 1) == source,
            "prove exact reversible one-function V24-to-clamp byte transformation")
    return updated


def clamp_bounds(begin: int, end: int, length: int) -> tuple[int, int]:
    require(all(type(item) is int and 0 <= item <= SIZE_T_MAX
                for item in (begin, end, length)),
            "reject non-size_t synthetic capture bounds")
    first = length if begin > length else begin
    finish = length if end > length else end
    if finish < first:
        finish = first
    require(0 <= first <= finish <= length,
            "reject any synthetic out-of-bounds capture access")
    return first, finish


def semantic_model() -> dict:
    sizes = tuple(range(10)) + (16, 31)
    indices = tuple(range(12)) + (16, 31, 63, 255, 65535,
                                  (1 << 31) - 1, (1 << 63) - 1, SIZE_T_MAX)
    exhaustive = 0
    for length in sizes:
        payload = bytes((index * 29 + 7) % 256 for index in range(length))
        for begin in indices:
            for end in indices:
                first, finish = clamp_bounds(begin, end, length)
                require(payload[first:finish] == payload[begin:end],
                        "synthetic fresh-export capture differs from CPython slicing")
                exhaustive += 1

    # Public CPython witness encoded as explicit spans, without running re.
    original_subject = b"az12 bz34"
    fresh_export = b"X"
    captures = ((0, 2), (5, 7))
    first_a, finish_a = clamp_bounds(*captures[0], len(fresh_export))
    first_b, finish_b = clamp_bounds(*captures[1], len(fresh_export))
    witness = (fresh_export[first_a:finish_a]
               + original_subject[4:5] + fresh_export[first_b:finish_b])
    require(witness == b"X " and (first_a, finish_a) == (0, 1)
            and (first_b, finish_b) == (1, 1),
            "preserve the public changing-exporter CPython witness b'X '")

    alias_cases = 0
    backing = bytearray(b"alias-public-capture")
    outer = memoryview(backing)
    nested = memoryview(outer)[2:9]
    try:
        for view in (outer, nested):
            for begin in (0, 1, len(view), len(view) + 1, SIZE_T_MAX):
                for end in (0, 1, len(view), len(view) + 1, SIZE_T_MAX):
                    first, finish = clamp_bounds(begin, end, len(view))
                    require(view[first:finish].tobytes()
                            == view[begin:end].tobytes(),
                            "preserve all aliased and nested synthetic byte views")
                    alias_cases += 1
    finally:
        nested.release()
        outer.release()
    require(exhaustive == len(sizes) * len(indices) * len(indices)
            and alias_cases == 50,
            "require the complete exhaustive synthetic hostile bounds and aliases")
    return {
        "synthetic_exhaustive_length_count": len(sizes),
        "synthetic_exhaustive_index_count": len(indices),
        "synthetic_exhaustive_bounds_case_count": exhaustive,
        "synthetic_alias_case_count": alias_cases,
        "max_size_t_tested": SIZE_T_MAX,
        "public_cpython_pattern": "rb'([a-z]+)\\d+'",
        "public_cpython_replacement": "br'\\1'",
        "public_exporter_first_bytes": "az12 bz34",
        "public_exporter_second_bytes": "X",
        "public_cpython_expected_bytes": "X ",
        "public_witness_capture_spans": [[0, 2], [5, 7]],
        "public_witness_clamped_spans": [[0, 1], [1, 1]],
        "public_witness_executed_candidate": False,
        "synthetic_model_is_actual_candidate_matching": False,
        "fresh_export_acquired_before_clamp": True,
        "begin_and_end_both_clamped": True,
        "reversed_interval_normalized_to_empty": True,
        "capture_release_on_success": True,
        "bytes_and_text_fast_paths_preserved": True,
        "buffer_error_for_changed_capture_removed": True,
        "possible_out_of_bounds_capture_read": False,
        "new_buffer_acquisitions": 0,
        "new_buffer_releases": 0,
        "new_external_regular_expression_dependencies": 0,
        "stdlib_matching_delegation": False,
        "other_candidate_delegation": False,
        "fallback_added": False,
    }


def owner_document(row: tuple) -> dict:
    role, path, fingerprint, count, inode = row
    return {"role": role, "path": path, "sha256": fingerprint,
            "bytes": count, "device": DEVICE, "inode": inode,
            "mode": "0600", "uid": os.geteuid(), "nlink": 1}


def build_contract(source: tuple, protocol: tuple, proposal: dict,
                   semantics: dict) -> dict:
    return {
        "schema": SCHEMA, "version": 1,
        "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
        "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS", "family": "rust",
        "source": owner_document(source), "protocol": owner_document(protocol),
        "authenticated_frozen_owners": [owner_document(row) for row in OWNERS],
        "immutable_goal_sha256": GOAL_SHA256,
        "original_correctness_history": {
            "case_execution_denominator": 31237, "suite_count": 13,
            "named_private_waiver_count": 13, "crosswalk_count": 34,
            "obligation_count": 73, "supplemental_reference_case_count": 8244,
            "supplemental_reference_counted_in_original_denominator": False,
            "corrected_reference_case_count": 6912,
            "corrected_reference_counted_in_original_denominator": False,
        },
        "actual_complete_v24_candidate_failure": {
            "publication_receipt_sha256": ACTUAL_V24_SHA256,
            "publication_receipt_bytes": 11832,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL", "candidate_qualified": False,
            "case_execution_denominator": 31237, "suite_count": 13,
            "actual_candidate_worker_count": 13,
            "distinct_candidate_worker_count": 13,
            "completed_suite_count": 13,
            "all_original_observation_vectors_complete": True,
            "semantic_mismatch_count": 1352,
            "fully_observed_suite_mismatch_counts": {
                "substitution_v2": 240, "shape_v2": 1112,
            },
            "verified_passing_case_count": 15877,
            "failing_suite_passes_claimed": False,
            "infrastructure_failure_count": 0,
            "actual_worker_process_ids": [row[5] for row in SUITES],
            "complete_original_suite_row_sha256": [row[7] for row in SUITES],
        },
        "immutable_actual_v24_first_party_native_build": {
            "source_sha256": OWNERS[6][2], "protocol_sha256": OWNERS[7][2],
            "contract_sha256": OWNERS[8][2], "receipt_sha256": OWNERS[9][2],
            "actual_compiler_process_count": 28,
            "corrected_bridge_source_sha256": V24_BRIDGE_SHA256,
            "corrected_bridge_source_bytes": V24_BRIDGE_BYTES,
            "native_build_controller_executed": False,
            "native_binary_opened": False, "private_root_opened": False,
        },
        "derived_first_party_capture_clamp": {
            "source_base_path": OWNERS[11][1],
            "source_base_sha256": V24_BRIDGE_SHA256,
            "source_base_bytes": V24_BRIDGE_BYTES,
            "target_path": VARIANT, "sha256": DERIVED_BRIDGE_SHA256,
            "bytes": DERIVED_BRIDGE_BYTES, "materialized": False,
            "changed_function_count": 1,
            "changed_functions": ["rust_output_capture"],
            "replacement_site_count": 1,
            "original_capture_function_bytes": len(ORIGINAL_CAPTURE_FUNCTION),
            "corrected_capture_function_bytes": len(CORRECTED_CAPTURE_FUNCTION),
            "source_delta_bytes": DERIVED_BRIDGE_BYTES - V24_BRIDGE_BYTES,
            "complete_source_derivation": "EXACT ONE ANCHORED REVERSIBLE REPLACEMENT",
            "acquisition_and_release_preserved": True,
            "fresh_export_begin_clamped": True,
            "fresh_export_end_clamped": True,
            "reversed_clamped_interval_normalized": True,
            "changed_size_buffer_error_removed": True,
            "out_of_bounds_capture_precluded": True,
            "bytes_or_text_fast_path_preserved": True,
            "matcher_engine_changed": False,
            "external_regex_dependency_added": False,
            "stdlib_matching_delegation_added": False,
            "cross_candidate_engine_added": False,
            "candidate_built": False, "candidate_imported": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
        },
        "public_explicit_synthetic_semantics": semantics,
        "expanded_sealed_holdout_v2_proposal_metadata_only": proposal,
        "physical_source_wall": {
            "policy": "DENY DEFAULT; EXACT PINNED PLAINTEXT AND ONE V24 C FILE",
            "installed_before_owner_reads": True,
            "allowed_candidate_source_owner_count": 1,
            "allowed_native_binary_count": 0,
            "allowed_archive_count": 0,
            "allowed_holdout_content_count": 0,
            "allowed_unopened_phase3_proposal_metadata_count": 1,
            "foreign_descriptor_reads_allowed": False,
            "clock_access_allowed": False, "entropy_access_allowed": False,
            "compiler_or_worker_launch_allowed": False,
            "source_mode_filesystem_writes_allowed": False,
            "apply_mode_target_write_policy": "ROOT EXPLICIT; O_NOFOLLOW|O_CREAT|O_EXCL; ONCE",
            "apply_requires_frozen_commit_equals_pushed_commit": True,
        },
        "source_only_effects": {
            "candidate_source_files_read": 1,
            "candidate_imports": 0, "candidate_workers_started": 0,
            "reference_workers_started": 0,
            "compiler_processes_started": 0, "native_libraries_loaded": 0,
            "native_binary_files_opened": 0, "private_roots_opened": 0,
            "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0,
            "holdout_proposal_files_opened": 0,
            "holdout_proposal_metadata_probes": 1,
            "holdout_cases_generated": 0, "holdout_cases_opened": 0,
            "expanded_holdout_proposal_case_count": 141557760,
            "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "clock_samples": 0, "timing_trials_run": 0,
            "benchmark_files_opened": 0, "network_requests": 0,
            "candidate_correctness": NOT_MEASURED,
            "candidate_semantic_mismatch_count": NOT_MEASURED,
            "qualified_candidate_count": 0, "holdout": "NOT OPENED",
            "performance": NOT_MEASURED, "memory": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "winner_selected": False,
        },
    }


def canonical_document(value: dict) -> bytes:
    return (canonical(value) + "\n").encode("ascii")


def clone(value: dict) -> dict:
    result = StrictJSON(canonical_document(value)).decode()
    require(type(result) is dict, "require exact strict hostile evidence clone")
    assert isinstance(result, dict)
    return result


def rejected(action: object, label: str) -> str:
    require(callable(action), "require one executable source-only hostile control")
    try:
        action()
    except (FreezeError, OSError, ValueError, TypeError, IndexError,
            KeyError, OverflowError, UnicodeError):
        return label
    raise FreezeError("accepted hostile source-only control: " + label)


def self_test(wall: SourceWall, actual: dict, bridge: bytes,
              semantics: dict) -> list[str]:
    controls: list[str] = []
    for key, forged in (("candidate_status", "PASS"),
                        ("candidate_qualified", True),
                        ("publication_pass_means", "CANDIDATE PASSED"),
                        ("case_execution_denominator", 31236),
                        ("suite_count", 12),
                        ("completed_suite_count", 12),
                        ("actual_candidate_workers", 12),
                        ("semantic_mismatch_count", 1112),
                        ("verified_passing_case_count", 29885),
                        ("infrastructure_failure_count", 1),
                        ("combined_bridge_source_sha256", DERIVED_BRIDGE_SHA256),
                        ("holdout", "OPENED"),
                        ("clock_samples", 1),
                        ("winner_selected", True)):
        altered = clone(actual)
        altered[key] = forged
        controls.append(rejected(lambda item=altered: validate_actual_v24(item),
                                 "reject-forged-actual-v24-" + key))
    for index, row in enumerate(SUITES):
        for key, forged in (("mismatch_count", row[2] + 1),
                            ("pid", 0),
                            ("complete_original_row_sha256", "0" * 64),
                            ("fully_observed", False)):
            altered = clone(actual)
            altered["suite_integrity"][index][key] = forged
            controls.append(rejected(lambda item=altered: validate_actual_v24(item),
                                     "reject-forged-v24-suite-" + row[0] + "-" + key))

    for bad in ((-1, 0, 0), (0, -1, 0), (0, 0, -1),
                (SIZE_T_MAX + 1, 0, 0), (0, SIZE_T_MAX + 1, 0),
                (0, 0, SIZE_T_MAX + 1), (True, 0, 0), (0, False, 0),
                (0, 0, True), ("0", 0, 0), (0, 1.0, 0)):
        controls.append(rejected(lambda item=bad: clamp_bounds(*item),
                                 "reject-invalid-synthetic-size-t-" + str(len(controls))))

    for old in (bridge + b"\n", bridge.replace(ORIGINAL_CAPTURE_FUNCTION,
                CORRECTED_CAPTURE_FUNCTION, 1),
                bridge.replace(b"if (end > capture.length)",
                               b"if (begin > capture.length)", 1)):
        controls.append(rejected(lambda item=old: derive_bridge(item),
                                 "reject-forged-unique-v24-source-" + str(len(controls))))

    forbidden = (
        (ROOT + "/candidates/rust/py_bridge.c", "canonical-unsafe-bridge"),
        (ROOT + "/candidates/rust_candidate.py", "candidate-adapter"),
        (ROOT + "/candidates/_rust_engine.so", "native-engine"),
        (ROOT + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "native-bridge"),
        (ROOT + "/" + PROPOSAL, "unopened-v2-holdout-proposal"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json", "old-holdout-proposal"),
        (ROOT + "/oracle/phase2/evidence/forbidden.json.gz", "compressed-archive"),
        (ROOT + "/tools/../candidates/rust_candidate.py", "candidate-traversal"),
        ("/tmp/rebar-phase2-private-root", "private-root"),
        ("/etc/hosts", "unowned-host-file"),
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    for path, label in forbidden:
        controls.append(rejected(lambda item=path: os.open(item, flags),
                                 "source-wall-rejects-open-" + label))
        controls.append(rejected(lambda item=path: wall.native_open(item, flags),
                                 "source-wall-rejects-native-bypass-" + label))
    actions = (
        ("builtins-open", lambda: builtins.open(ROOT + "/" + OWNERS[11][1], "rb")),
        ("direct-_io-open", lambda: _io.open(ROOT + "/" + OWNERS[11][1], "rb")),
        ("direct-io-open", lambda: io.open(ROOT + "/" + OWNERS[11][1], "rb")),
        ("foreign-descriptor-read", lambda: os.read(0, 1)),
        ("foreign-descriptor-write", lambda: os.write(1, b"x")),
        ("foreign-descriptor-stat", lambda: os.fstat(0)),
        ("foreign-descriptor-close", lambda: os.close(0)),
        ("foreign-stat", lambda: os.stat(ROOT + "/" + OWNERS[11][1])),
        ("second-holdout-proposal-stat", lambda: os.lstat(ROOT + "/" + PROPOSAL)),
        ("clock-time", lambda: time.time()),
        ("clock-monotonic", lambda: time.monotonic()),
        ("clock-perf-counter", lambda: time.perf_counter()),
        ("entropy", lambda: os.urandom(1)),
        ("matching-import", lambda: sys.audit("import", "re", None)),
        ("external-regex-import", lambda: sys.audit("import", "regex", None)),
        ("native-dynamic-loader", lambda: sys.audit("ctypes.dlopen", "x")),
        ("candidate-worker", lambda: sys.audit("subprocess.Popen", "worker")),
        ("candidate-interpreter", lambda: sys.audit("cpython.PyInterpreterState_New")),
        ("network", lambda: sys.audit("socket.connect", "x")),
        ("untrusted-code", lambda: sys.audit("exec", "x")),
        ("source-write", lambda: os.open(ROOT + "/" + SOURCE,
                                         os.O_WRONLY | os.O_TRUNC)),
        ("variant-write-in-source-mode", lambda: os.open(ROOT + "/" + VARIANT,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0))),
        ("variant-directory-in-source-mode", lambda: os.mkdir(wall.target_parent, 0o700)),
    )
    for label, action in actions:
        controls.append(rejected(action, "source-wall-physically-rejects-" + label))
    controls.append(rejected(lambda: StrictJSON(b'{"x":1,"x":2}').decode(),
                             "reject-duplicate-json-keys"))
    controls.append(rejected(lambda: StrictJSON(b'{"x":1.0}').decode(),
                             "reject-floating-point-evidence"))
    require(semantics["synthetic_exhaustive_bounds_case_count"] >= 4000
            and semantics["synthetic_alias_case_count"] == 50
            and len(controls) >= 100 and not wall.live and wall.output is None,
            "require exhaustive real isolation controls without candidate execution")
    no_matching_imports()
    return controls


def parse_arguments(arguments: list[str]) -> dict:
    require(bool(arguments), "select one explicit source-only or root-apply mode")
    mode = arguments[0]
    require(mode in ("--render-contract", "--self-test", "--verify-frozen-context", "--apply"),
            "reject candidate execution, native build, worker, benchmark, and holdout modes")
    names = ["--source-sha256", "--protocol-sha256"]
    if mode != "--render-contract":
        names.append("--contract-sha256")
    if mode == "--apply":
        names.extend(("--frozen-commit", "--pushed-commit"))
    require(len(arguments) == 1 + 2 * len(names),
            "require exact complete freeze pins and explicit apply push attestation")
    pins: dict[str, str] = {}
    for index in range(1, len(arguments), 2):
        key, value = arguments[index], arguments[index + 1]
        require(key in names and key not in pins,
                "reject repeated or invented capture-clamp authority")
        if key.endswith("sha256"):
            pins[key] = checked_sha(value, key)
        else:
            require(type(value) is str and len(value) == 40
                    and all(char in "0123456789abcdef" for char in value),
                    "require one complete pushed Git commit identity")
            pins[key] = value
    require(set(pins) == set(names), "reject omitted frozen-context authority")
    if mode == "--apply":
        require(pins["--frozen-commit"] == pins["--pushed-commit"],
                "root may materialize only after the complete frozen source commit was pushed")
    return {"mode": mode, "pins": pins}


def load_context(wall: SourceWall, pins: dict, render: bool) -> dict:
    source_row = dynamic_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = dynamic_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source_row)
    read_owner(wall, protocol_row)
    if not render:
        contract_row = dynamic_owner(wall, "contract", CONTRACT, pins["--contract-sha256"])

    owners: dict[str, bytes] = {}
    for row in OWNERS:
        owners[row[0]] = read_owner(wall, row)
    validate_original_oracle(json_object(owners["original_oracle"], "original oracle"))
    validate_supplemental(json_object(owners["supplemental_oracle"], "separate 8,244 reference"))
    validate_v24_campaign(json_object(owners["campaign_v24_contract"], "V24 campaign contract"))
    validate_v24_build(json_object(owners["build_v24_contract"], "V24 full build contract"),
                       json_object(owners["build_v24_receipt"], "V24 native build receipt"))
    actual = json_object(owners["actual_v24_failure"], "actual complete V24 failure receipt")
    validate_actual_v24(actual)
    proposal = proposal_metadata(wall)
    corrected = derive_bridge(owners["v24_corrected_first_party_bridge"])
    semantics = semantic_model()
    frozen = build_contract(source_row, protocol_row, proposal, semantics)
    if not render:
        complete = read_owner(wall, contract_row)
        require(complete == canonical_document(frozen)
                and json_object(complete, "capture-clamp complete frozen contract") == frozen,
                "reject omitted, changed, or invented capture-clamp freeze obligations")
    require(not wall.live and wall.output is None,
            "close every frozen owner before source verification or root apply")
    no_matching_imports()
    return {"contract": frozen, "actual": actual,
            "bridge": owners["v24_corrected_first_party_bridge"],
            "corrected": corrected, "semantics": semantics}


def apply_exact_once(wall: SourceWall, corrected: bytes) -> dict:
    require(wall.apply and not wall.directory_created and not wall.output_opened
            and digest(corrected) == DERIVED_BRIDGE_SHA256
            and len(corrected) == DERIVED_BRIDGE_BYTES,
            "root apply requires the exact complete authenticated one-site source")
    os.mkdir(wall.target_parent, 0o700)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(wall.target, flags, 0o600)
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and stat.S_IMODE(initial.st_mode) == 0o600
                and initial.st_dev == DEVICE and initial.st_nlink == 1
                and initial.st_uid == os.geteuid() and initial.st_size == 0,
                "require a fresh exclusive no-follow private regular target")
        offset = 0
        while offset < len(corrected):
            count = os.write(descriptor, memoryview(corrected)[offset:])
            require(type(count) is int and count > 0,
                    "reject truncated exclusive first-party bridge publication")
            offset += count
        os.fsync(descriptor)
        found = os.fstat(descriptor)
        require(found.st_size == DERIVED_BRIDGE_BYTES
                and found.st_dev == initial.st_dev and found.st_ino == initial.st_ino
                and stat.S_IMODE(found.st_mode) == 0o600 and found.st_nlink == 1,
                "reject exchanged or truncated exclusive corrected bridge")
        result = {"path": VARIANT, "sha256": DERIVED_BRIDGE_SHA256,
                  "bytes": DERIVED_BRIDGE_BYTES, "device": found.st_dev,
                  "inode": found.st_ino, "mode": "0600", "nlink": 1,
                  "exclusive_no_follow": True, "materialized_once": True}
    finally:
        os.close(descriptor)
    return result


def main() -> int:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON and sys.flags.isolated == 1
            and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
            "require exact independently pinned CPython 3.14.6 with -I -B -S")
    no_matching_imports()
    choice = parse_arguments(list(sys.argv[1:]))
    wall = SourceWall(choice["mode"] == "--apply")
    wall.install()
    state = load_context(wall, choice["pins"], choice["mode"] == "--render-contract")
    if choice["mode"] == "--render-contract":
        sys.stdout.buffer.write(canonical_document(state["contract"]))
        sys.stdout.buffer.flush()
        return 0
    controls = (self_test(wall, state["actual"], state["bridge"], state["semantics"])
                if choice["mode"] == "--self-test" else [])
    materialized = (apply_exact_once(wall, state["corrected"])
                    if choice["mode"] == "--apply" else None)
    require(not wall.live and wall.output is None, "release all isolated descriptors")
    no_matching_imports()
    result = {
        "schema": SCHEMA + "-source-only-gate", "status": "PASS", "version": 1,
        "mode": choice["mode"][2:],
        "source_sha256": choice["pins"]["--source-sha256"],
        "protocol_sha256": choice["pins"]["--protocol-sha256"],
        "contract_sha256": choice["pins"]["--contract-sha256"],
        "authenticated_frozen_owner_count": len(OWNERS) + 3,
        "actual_v24_failure_receipt_sha256": ACTUAL_V24_SHA256,
        "actual_v24_candidate_status": "FAIL",
        "actual_v24_publication_status": "PASS",
        "actual_v24_publication_pass_means": "DURABLE PUBLICATION ONLY",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13, "named_private_waiver_count": 13,
        "actual_v24_complete_semantic_mismatch_count": 1352,
        "actual_v24_fully_observed_suite_mismatch_counts": {
            "substitution_v2": 240, "shape_v2": 1112,
        },
        "actual_v24_verified_passing_case_count": 15877,
        "actual_v24_candidate_worker_count": 13,
        "actual_v24_completed_suite_count": 13,
        "frozen_v24_bridge_sha256": V24_BRIDGE_SHA256,
        "frozen_v24_bridge_bytes": V24_BRIDGE_BYTES,
        "derived_bridge_sha256": DERIVED_BRIDGE_SHA256,
        "derived_bridge_bytes": DERIVED_BRIDGE_BYTES,
        "changed_function_count": 1, "changed_functions": ["rust_output_capture"],
        "public_witness_expected_bytes": "X ",
        "synthetic_exhaustive_bounds_case_count":
            state["semantics"]["synthetic_exhaustive_bounds_case_count"],
        "synthetic_alias_case_count": state["semantics"]["synthetic_alias_case_count"],
        "hostile_control_count": len(controls), "hostile_controls": controls,
        "physically_blocked_effects": dict(wall.blocked),
        "unopened_holdout_proposal_v2_case_count": 141557760,
        "holdout_proposal_content_open_count": 0,
        "holdout_proposal_metadata_probe_count": 1,
        "candidate_imports": 0, "candidate_workers_started": 0,
        "compiler_processes_started": 0, "native_libraries_loaded": 0,
        "archive_opens": 0, "private_root_opens": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "holdout": "NOT OPENED", "performance": NOT_MEASURED,
        "memory": NOT_MEASURED, "candidate_correctness": NOT_MEASURED,
        "candidate_qualified": False, "winner_selected": False,
        "variant_materialized": materialized is not None,
        "materialized_variant": materialized,
    }
    if materialized is not None:
        result["frozen_pushed_commit"] = choice["pins"]["--pushed-commit"]
    sys.stdout.buffer.write(canonical_document(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        raise SystemExit(2)
