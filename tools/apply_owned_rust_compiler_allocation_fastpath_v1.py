#!/usr/bin/env python3
"""Freeze two exact, first-party Rust compiler allocation improvements.

Source-only modes read pinned public evidence and two first-party candidate
source owners behind a physical deny-default wall.  They never execute a
candidate, start a process, sample a clock, build native code, or inspect
holdout contents.  Only the separately attested root operation may create the
one exclusive derived Rust source variant.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("first-party compiler freeze must not import a matcher")

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
SOURCE = "tools/apply_owned_rust_compiler_allocation_fastpath_v1.py"
PROTOCOL = "oracle/phase2/RUST-COMPILER-ALLOCATION-FASTPATH-V1.md"
CONTRACT = "oracle/phase2/rust-compiler-allocation-fastpath-v1.json"
VARIANT = "candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs"
PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
SCHEMA = "rebar-owned-rust-compiler-allocation-fastpath-v1-source-freeze"
NOT_MEASURED = "NOT MEASURED"
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_DEPTH = 80
MAX_JSON_ITEMS = 200_000
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ORIGINAL_SHA256 = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
ORIGINAL_BYTES = 177_967
DERIVED_SHA256 = "64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6"
DERIVED_BYTES = 178_021
ACTUAL_V24_SHA256 = "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09"
PROFILE_MATRIX_SHA256 = "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
PROFILE_RECORDS_SHA256 = "41f83dc761a93ea8e3203f46cedbba1e10918cf053194c20b37b8c209e992242"
PROFILE_ROWS_SHA256 = "ce5ddb143be0d58588d2b18540c0db1b716eebb138cfe32a04690a0efe62c378"
PROPOSAL_SHA256 = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
PROPOSAL_BYTES = 15_561
PROPOSAL_INODE = 525920

# role, relative path, complete SHA-256, complete byte length, device-2064 inode
OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA256, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 524713),
    ("supplemental_oracle", "oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
     5288, 525082),
    ("actual_v24_failure",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v24-rust-capture-shape-v2-root-provenance-"
     "original-p0-v24-failures-publication-receipt.json",
     ACTUAL_V24_SHA256, 11832, 525952),
    ("first_party_cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
     225, 428094),
    ("first_party_cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
     167, 428098),
    ("first_party_rust_compiler", "candidates/rust/src/lib.rs",
     ORIGINAL_SHA256, ORIGINAL_BYTES, 428096),
    ("first_party_v24_bridge",
     "candidates/rust/variants/buffer_shape_pickle_findall_captures_semantics_v2/py_bridge.c",
     "1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0",
     178860, 525539),
    ("public_profile_source", "tools/rust_public_profile_v1.py",
     "ada1e9cfc8684ecb4fcf9294057347018b6058fc1619ae9de6a8b31097aa1562",
     79693, 429476),
    ("public_profile_protocol", "oracle/phase3/RUST-PUBLIC-PROFILE-V1.md",
     "6664f17ddd65c1953782f43b7fe1fa01427f1f510adfbad86fe8efdb135829ba",
     5281, 525927),
    ("public_profile_contract", "oracle/phase3/rust-public-profile-v1.json",
     "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5",
     1797, 525928),
    ("public_stdlib_correctness",
     "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json",
     "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381",
     445036, 526005),
    ("public_rust_correctness",
     "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json",
     "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0",
     445394, 526006),
    ("public_paired_timing",
     "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json",
     "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85",
     504907, 526015),
)

OLD_PARSER = b"struct Parser {\n    source: Vec<u32>,\n"
NEW_PARSER = b"struct Parser<'a> {\n    source: &'a [u32],\n"
OLD_IMPLEMENTATION = b"impl Parser {\n"
NEW_IMPLEMENTATION = b"impl Parser<'_> {\n"
OLD_ALT = b"""    fn alt(&mut self, flags: u32) -> PResult<Expr> {
        let mut branches = vec![self.seq(flags)?];
        while self.now() == Some('|') {
            self.global_allowed = false;
            self.at += 1;
            let branch_flags = if self.group_depth == 0 {
                self.flags
            } else {
                flags
            };
            branches.push(self.seq(branch_flags)?);
        }
        Ok(if branches.len() == 1 {
            branches.swap_remove(0)
        } else {
            Expr::Alt(branches)
        })
    }
"""
NEW_ALT = b"""    fn alt(&mut self, flags: u32) -> PResult<Expr> {
        let first = self.seq(flags)?;
        if self.now() != Some('|') {
            return Ok(first);
        }
        let mut branches = Vec::with_capacity(2);
        branches.push(first);
        while self.now() == Some('|') {
            self.global_allowed = false;
            self.at += 1;
            let branch_flags = if self.group_depth == 0 {
                self.flags
            } else {
                flags
            };
            branches.push(self.seq(branch_flags)?);
        }
        Ok(Expr::Alt(branches))
    }
"""
OLD_NORMAL_SOURCE = (
    b"    let source = unsafe { slice::from_raw_parts(pattern, length) }.to_vec();\n"
)
NEW_NORMAL_SOURCE = b"    let source = unsafe { slice::from_raw_parts(pattern, length) };\n"
OLD_SCANNER_SOURCE = (
    b"            source: unsafe { slice::from_raw_parts(phrase.source, phrase.length) }"
    b".to_vec(),\n"
)
NEW_SCANNER_SOURCE = (
    b"            source: unsafe { slice::from_raw_parts(phrase.source, phrase.length) },\n"
)
OLD_TEST_SOURCE = b"        let source = if byte_mode {\n"
NEW_TEST_SOURCE = b"        let source: Vec<u32> = if byte_mode {\n"
OLD_TEST_PARSER = (
    b"        let flags = lexical_flags | if byte_mode { BYTE } else { 0 };\n"
    b"        let mut parser = Parser {\n"
    b"            source,\n"
)
NEW_TEST_PARSER = (
    b"        let flags = lexical_flags | if byte_mode { BYTE } else { 0 };\n"
    b"        let mut parser = Parser {\n"
    b"            source: &source,\n"
)
REPLACEMENTS = (
    ("parser_borrowed_lifetime", OLD_PARSER, NEW_PARSER),
    ("parser_implementation_lifetime", OLD_IMPLEMENTATION, NEW_IMPLEMENTATION),
    ("lazy_alternation", OLD_ALT, NEW_ALT),
    ("normal_ffi_borrow", OLD_NORMAL_SOURCE, NEW_NORMAL_SOURCE),
    ("scanner_ffi_borrow", OLD_SCANNER_SOURCE, NEW_SCANNER_SOURCE),
    ("owned_test_source_type", OLD_TEST_SOURCE, NEW_TEST_SOURCE),
    ("owned_test_parser_borrow", OLD_TEST_PARSER, NEW_TEST_PARSER),
)


class FreezeError(Exception):
    """Reject altered sources, public evidence, or isolation boundaries."""


def require(value: object, message: str) -> None:
    if value is not True:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash complete genuine bytes only")
    return hashlib.sha256(value).hexdigest()


def check_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require exact lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quoted(value: str) -> str:
    require(type(value) is str, "require a JSON string")
    escaped = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    pieces = ['"']
    for item in value:
        point = ord(item)
        require(not 0xD800 <= point <= 0xDFFF, "reject unpaired JSON surrogate")
        pieces.append(escaped.get(item, "\\u" + format(point, "04x")
                                  if point < 32 else item))
    pieces.append('"')
    return "".join(pieces)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive JSON depth")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quoted(value)
    if type(value) is int:
        return str(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(item) is str for item in value), "reject nontext JSON key")
        return "{" + ",".join(quoted(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported or nonfinite JSON evidence")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class StrictJSON:
    """Small bounded, duplicate-rejecting parser without importing regex."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "reject unbounded JSON evidence")
        self.text = raw.decode("utf-8", "strict")
        self.index = 0
        self.items = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "require JSON string")
        self.index += 1
        pieces: list[str] = []
        escapes = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                   "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            item = self.text[self.index]
            self.index += 1
            if item == '"':
                return "".join(pieces)
            if item != "\\":
                require(ord(item) >= 32 and not 0xD800 <= ord(item) <= 0xDFFF,
                        "reject invalid raw JSON character")
                pieces.append(item)
                continue
            require(self.index < len(self.text), "reject truncated JSON escape")
            escape = self.text[self.index]
            self.index += 1
            if escape != "u":
                require(escape in escapes, "reject unknown JSON escape")
                pieces.append(escapes[escape])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4
                    and all(item in "0123456789abcdefABCDEF" for item in digits),
                    "reject malformed Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject unpaired high surrogate")
                low_digits = self.text[self.index + 2:self.index + 6]
                require(len(low_digits) == 4
                        and all(item in "0123456789abcdefABCDEF" for item in low_digits),
                        "reject malformed low surrogate")
                low = int(low_digits, 16)
                require(0xDC00 <= low <= 0xDFFF, "reject unpaired high surrogate")
                self.index += 6
                pieces.append(chr(0x10000 + ((point - 0xD800) << 10) + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF, "reject unpaired low surrogate")
                pieces.append(chr(point))
        raise FreezeError("reject unterminated JSON string")

    def number(self) -> int:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject leading-zero JSON integer")
        else:
            require(self.text[self.index] in "123456789", "reject invalid JSON integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        require(self.index - start <= 128, "reject oversized JSON integer")
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                "reject floating or nonfinite JSON evidence")
        return int(self.text[start:self.index])

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject deep JSON evidence")
        self.whitespace()
        require(self.index < len(self.text), "reject missing JSON value")
        item = self.text[self.index]
        if item == '"':
            return self.string()
        if item == "{":
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
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON object")
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
        if item == "[":
            self.index += 1
            result: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON array")
                result.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result
                require(separator == ",", "reject malformed JSON array")
        if item == "-" or item in "0123456789":
            return self.number()
        for literal, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return value
        raise FreezeError("reject malformed or nonfinite JSON value")

    def decode(self) -> object:
        value = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing JSON evidence")
        return value


def json_object(raw: bytes, name: str) -> dict:
    result = StrictJSON(raw).decode()
    require(type(result) is dict, "require complete JSON object: " + name)
    assert isinstance(result, dict)
    return result


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "rebar", "subprocess", "socket",
                 "threading", "multiprocessing", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matcher, candidate, native loader, worker, or subprocess")


class SourceWall:
    """Deny-default pinned descriptors, metadata-only holdout, one exclusive file."""

    def __init__(self, apply: bool = False) -> None:
        self.allowed = frozenset(
            (ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT)
            + tuple(ROOT + "/" + row[1] for row in OWNERS)
        )
        self.apply = apply
        self.target = ROOT + "/" + VARIANT
        self.parent = self.target.rsplit("/", 1)[0]
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
        raise FreezeError("compiler source wall rejected " + category)

    def approved_read(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/") and path == os.path.normpath(path)
                and not any(item in (".", "..") for item in path.split("/"))
                and not path.endswith((".so", ".gz", ".er")))

    def approved_write(self, path: object, flags: object) -> bool:
        required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        forbidden = os.O_RDWR | os.O_TRUNC | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
        return (self.apply and path == self.target and type(flags) is int
                and flags & required == required and not flags & forbidden
                and self.directory_created and not self.output_opened)

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
                    and not (type(mode) is str and any(item in mode for item in "wax+"))):
                return
            if self.approved_write(path, flags):
                return
            if path == self.proposal:
                self.deny("unopened-final-holdout-content-open")
            self.deny("unowned-source-candidate-native-holdout-or-write-open")
        if event == "os.mkdir":
            path = args[0] if args else None
            if self.apply and path == self.parent and not self.directory_created:
                return
            self.deny("unauthorized-directory-mutation")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.rmdir",
                      "os.chmod", "os.chown", "os.urandom", "os.getrandom",
                      "_interpreters.create", "_interpreters.exec",
                      "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.", "tempfile.",
                                     "time.", "os.exec", "os.spawn"))):
            self.deny("candidate-native-worker-network-clock-or-dynamic-code")

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
                "reject invalid or repeated compiler source descriptor")
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
            self.deny("unowned-source-or-output-write")
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
        require(self.proposal_stat_count == 0,
                "inspect unopened final proposal metadata exactly once")
        assert isinstance(path, str)
        result = self.native_lstat(path)
        self.proposal_stat_count += 1
        return result

    def guarded_mkdir(self, path: object, mode: int = 0o777,
                      *, dir_fd: object = None) -> None:
        if (not self.apply or path != self.parent or dir_fd is not None
                or self.directory_created or mode != 0o700):
            self.deny("unauthorized-compiler-variant-directory")
        assert isinstance(path, str)
        self.native_mkdir(path, mode)
        self.directory_created = True

    def install(self) -> None:
        require(not self.installed, "install compiler source wall exactly once")
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
    check_sha(expected, relative)
    require(type(role) is str and type(relative) is str
            and type(count) is int and 0 < count <= MAX_OWNER_BYTES
            and type(inode) is int and inode > 0,
            "reject incomplete pinned owner")
    path = ROOT + "/" + relative
    require(wall.installed and wall.approved_read(path),
            "install compiler source wall before reading owners")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_nlink == 1
                and before.st_uid == os.geteuid(),
                "reject substituted frozen owner: " + role)
        remaining = count
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            require(type(block) is bytes and bool(block),
                    "reject truncated frozen owner: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject grown frozen owner: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject concurrently replaced owner: " + role)
        value = b"".join(blocks)
        require(digest(value) == expected, "reject altered owner: " + role)
        return value
    finally:
        os.close(descriptor)


def dynamic_owner(wall: SourceWall, role: str, relative: str, expected: str) -> tuple:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject unrelated live compiler freeze owner")
    check_sha(expected, relative)
    path = ROOT + "/" + relative
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        result = os.fstat(descriptor)
        require(stat.S_ISREG(result.st_mode)
                and stat.S_IMODE(result.st_mode) == 0o600
                and result.st_dev == DEVICE and result.st_uid == os.geteuid()
                and result.st_nlink == 1 and 0 < result.st_size <= MAX_OWNER_BYTES,
                "reject substituted live compiler freeze owner: " + role)
        return role, relative, expected, result.st_size, result.st_ino
    finally:
        os.close(descriptor)


def owner_pin(row: tuple) -> dict:
    role, relative, sha256, size, inode = row
    return {"role": role, "path": relative, "sha256": sha256,
            "bytes": size, "device": DEVICE, "inode": inode,
            "mode": "0600", "nlink": 1}


def proposal_metadata(wall: SourceWall) -> dict:
    result = os.lstat(ROOT + "/" + PROPOSAL)
    require(stat.S_ISREG(result.st_mode)
            and stat.S_IMODE(result.st_mode) == 0o600
            and result.st_dev == DEVICE and result.st_ino == PROPOSAL_INODE
            and result.st_size == PROPOSAL_BYTES and result.st_nlink == 1
            and result.st_uid == os.geteuid()
            and wall.proposal_open_count == 0 and wall.proposal_stat_count == 1,
            "reject altered unopened final proposal metadata")
    return {"path": PROPOSAL, "sha256_independently_pinned_not_read": PROPOSAL_SHA256,
            "bytes_metadata_only": PROPOSAL_BYTES, "device": DEVICE,
            "inode_metadata_only": PROPOSAL_INODE, "case_count": 141557760,
            "original_case_count": 31237, "content_open_count": 0,
            "metadata_probe_count": 1, "final_protocol_status": "NOT FROZEN",
            "case_status": "NOT GENERATED; NOT OPENED",
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3}


def validate_oracles(original: dict, supplemental: dict, actual: dict) -> None:
    require(original.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and original.get("original_case_execution_denominator") == 31237
            and original.get("original_suite_count") == 13
            and original.get("status") == "PASS"
            and original.get("qualified_candidate_count") == 0,
            "preserve the exact frozen 31,237-case original denominator")
    require(supplemental.get("schema") == "rebar-owned-differential-fuzz-reference-v3"
            and supplemental.get("original_case_execution_denominator") == 31237
            and supplemental.get("original_suite_count") == 13
            and type(supplemental.get("supplemental_corpus")) is dict
            and supplemental["supplemental_corpus"].get("case_count") == 8244
            and supplemental.get("case_denominator_included_in_original_31237") is False,
            "never add 8,244 supplemental cases to the original denominator")
    rows = actual.get("suite_integrity")
    require(actual.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v24-durable-publication-receipt"
            and actual.get("status") == "PASS"
            and actual.get("publication_status") == "PASS"
            and actual.get("candidate_status") == "FAIL"
            and actual.get("case_execution_denominator") == 31237
            and actual.get("completed_suite_count") == 13
            and actual.get("actual_candidate_workers") == 13
            and actual.get("semantic_mismatch_count") == 1352
            and actual.get("verified_passing_case_count") == 15877
            and actual.get("candidate_qualified") is False
            and actual.get("holdout") == "NOT OPENED"
            and type(rows) is list and len(rows) == 13,
            "preserve the complete failed Rust V24 original campaign")
    failing = {item["suite"]: item["mismatch_count"]
               for item in rows if item["mismatch_count"]}
    require(failing == {"substitution_v2": 240, "shape_v2": 1112},
            "preserve all 1,352 original Rust mismatches")


def validate_first_party(cargo: bytes, lock: bytes, bridge: bytes) -> None:
    require(cargo.count(b"[package]") == 1
            and b'name = "rebar-rust-continuation"' in cargo
            and b'crate-type = ["cdylib"]' in cargo
            and b"[profile.release]" in cargo
            and b"lto = true" in cargo and b"codegen-units = 1" in cargo
            and b"[dependencies" not in cargo and b"[target." not in cargo,
            "require the existing independently authored zero-dependency Rust crate")
    require(lock.count(b"[[package]]") == 1
            and b'name = "rebar-rust-continuation"' in lock
            and b"dependencies =" not in lock and b"source =" not in lock,
            "reject external Cargo package, dependency, or registry")
    normal_call = (
        b"void *handle = rebar_compile(source, (size_t)length, (uint32_t)flags, "
        b"(uint8_t)byte_mode, positions, values, (size_t)count);\n"
        b"    PyMem_Free(owned_names);\n"
        b"    PyMem_Free(owned_pattern);"
    )
    scanner_call = (
        b"    handle = rebar_compile_scanner(\n"
        b"        phrases,\n"
        b"        count,\n"
        b"        (uint32_t)flags,\n"
        b"        &failed_index\n"
        b"    );"
    )
    require(bridge.count(normal_call) == 1 and bridge.count(scanner_call) == 1
            and bridge.count(b"phrases[index].source = owned_sources[index];") == 1
            and bridge.find(scanner_call) < bridge.rfind(b"PyMem_Free(owned_sources[index]);")
            and b"uint32_t local_pattern[RUST_LOCAL_PATTERN_WORDS];" in bridge
            and b"source = (const uint32_t *)PyUnicode_4BYTE_DATA(pattern);" in bridge,
            "prove both C-owned u32 source buffers outlive complete synchronous parsing")


def validate_public_profile(profile: dict, baseline: dict,
                            candidate: dict, paired: dict) -> dict:
    require(profile.get("schema") == "rebar-rust-fresh-public-profile-v1-source-freeze"
            and profile.get("case_count") == 416
            and profile.get("dataset_count") == 16
            and profile.get("operation_count") == 26
            and profile.get("matrix_sha256") == PROFILE_MATRIX_SHA256
            and profile.get("pinned_cpython") == "3.14.6"
            and profile.get("pinned_python") == PYTHON,
            "authenticate the independent public-only practice protocol")
    for engine, row in (("stdlib", baseline), ("rust", candidate)):
        require(row.get("schema")
                == "rebar-rust-fresh-public-profile-v1-isolated-observations"
                and row.get("status") == "PASS" and row.get("engine") == engine
                and row.get("case_count") == 416
                and row.get("matrix_sha256") == PROFILE_MATRIX_SHA256
                and row.get("records_sha256") == PROFILE_RECORDS_SHA256
                and type(row.get("records")) is list and len(row["records"]) == 416
                and row.get("fixture_files_read") == 0
                and row.get("holdout_files_read") == 0
                and row.get("archive_files_read") == 0,
                "authenticate the isolated complete public " + engine + " answers")
    require(baseline["records"] == candidate["records"]
            and type(baseline.get("pid")) is int
            and type(candidate.get("pid")) is int
            and baseline["pid"] != candidate["pid"],
            "require two distinct workers with every public answer identical")
    rows = paired.get("rows")
    require(paired.get("schema") == "rebar-rust-fresh-public-profile-v1-paired-timing-rows"
            and paired.get("matrix_sha256") == PROFILE_MATRIX_SHA256
            and paired.get("rows_sha256") == PROFILE_ROWS_SHA256
            and type(rows) is list and len(rows) == 1664,
            "preserve all 1,664 existing paired public-only observations")
    baseline_total = 0
    rust_total = 0
    wins = 0
    rounds = set()
    case_ids = set()
    dense_count = 0
    for row in rows:
        require(type(row) is dict
                and type(row.get("baseline_elapsed_ns")) is int
                and row["baseline_elapsed_ns"] > 0
                and type(row.get("rust_elapsed_ns")) is int
                and row["rust_elapsed_ns"] > 0
                and type(row.get("round")) is int and 0 <= row["round"] < 4
                and type(row.get("case")) is str
                and type(row.get("baseline_pid")) is int
                and type(row.get("rust_pid")) is int
                and row["baseline_pid"] != row["rust_pid"]
                and row.get("iterations") == 3,
                "reject incomplete or nonpaired public-only timing evidence")
        baseline_total += row["baseline_elapsed_ns"]
        rust_total += row["rust_elapsed_ns"]
        wins += int(row["rust_elapsed_ns"] < row["baseline_elapsed_ns"])
        rounds.add(row["round"])
        case_ids.add(row["case"])
        dense_count += int(row.get("cohort") == "mandatory_literal_dense_same_first_byte")
    require(rounds == {0, 1, 2, 3} and len(case_ids) == 416
            and dense_count == 416
            and baseline_total == 96434251 and rust_total == 161853767
            and wins == 723,
            "preserve every existing public-only win, loss, and dense-search case")
    return {"case_count": 416, "distinct_case_count": 416,
            "paired_rounds": 4, "paired_row_count": 1664,
            "baseline_total_ns": baseline_total, "rust_total_ns": rust_total,
            "rust_faster_paired_row_count": wins,
            "dense_first_byte_paired_row_count": dense_count,
            "records_sha256": PROFILE_RECORDS_SHA256,
            "rows_sha256": PROFILE_ROWS_SHA256,
            "matrix_sha256": PROFILE_MATRIX_SHA256,
            "final_holdout": False,
            "candidate_qualified": False,
            "optimized_variant_measured": False,
            "optimized_variant_speed": NOT_MEASURED}


def derive_source(source: bytes) -> bytes:
    require(type(source) is bytes and len(source) == ORIGINAL_BYTES
            and digest(source) == ORIGINAL_SHA256,
            "require exact complete immutable Rust compiler source")
    updated = source
    for label, previous, corrected in REPLACEMENTS:
        require(type(previous) is bytes and type(corrected) is bytes
                and previous != corrected and updated.count(previous) == 1
                and updated.count(corrected) == 0,
                "require exactly one unique source anchor: " + label)
        updated = updated.replace(previous, corrected, 1)
        require(updated.count(corrected) == 1 and updated.count(previous) == 0,
                "require exactly one reversible source replacement: " + label)
    reversed_source = updated
    for label, previous, corrected in reversed(REPLACEMENTS):
        require(reversed_source.count(corrected) == 1,
                "require one reversible transformed anchor: " + label)
        reversed_source = reversed_source.replace(corrected, previous, 1)
    require(reversed_source == source,
            "prove all seven source changes reverse exactly to the original")
    require(len(updated) == DERIVED_BYTES and digest(updated) == DERIVED_SHA256,
            "reject incomplete, invented, or unrelated compiler optimization")
    require(updated.count(b"struct Parser<'a> {") == 1
            and updated.count(b"source: &'a [u32],") == 1
            and updated.count(b"impl Parser<'_> {") == 1
            and updated.count(b"let mut parser = Parser {") == 3
            and updated.count(b".to_vec()") == source.count(b".to_vec()") - 2
            and updated.count(NEW_ALT) == 1,
            "preserve all three parser constructors and remove only two source clones")
    forbidden = (b"extern crate regex", b"regex::", b"pcre", b"oniguruma",
                 b"_sre", b"PyImport_ImportModule", b"dlopen(", b"fallback")
    for marker in forbidden:
        require(updated.count(marker) == source.count(marker),
                "never add external matching, delegation, fallback, or loader")
    return updated


class SyntheticError(Exception):
    def __init__(self, text: str, position: int) -> None:
        super().__init__(text)
        self.text = text
        self.position = position


class SyntheticSourceOwner:
    """A checked public model of one synchronous C-owned u32 source."""

    def __init__(self, values: tuple[int, ...]) -> None:
        self.values = values
        self.live = True
        self.active_borrows = 0

    def borrow(self):
        require(self.live, "reject a synthetic borrow after its owner was freed")
        self.active_borrows += 1
        return SyntheticSourceBorrow(self)

    def close(self) -> None:
        require(self.live, "reject a twice-freed synthetic source owner")
        require(self.active_borrows == 0,
                "reject source-owner release while synchronous parsing is active")
        self.live = False


class SyntheticSourceBorrow:
    """An explicitly invalidatable bounded view into one live source owner."""

    def __init__(self, owner: SyntheticSourceOwner) -> None:
        self.owner = owner
        self.active = True

    def read(self, index: int) -> int:
        require(self.active and self.owner.live,
                "reject access through a released or dangling synthetic source")
        require(type(index) is int and 0 <= index < len(self.owner.values),
                "reject an out-of-bounds synthetic borrowed source")
        return self.owner.values[index]

    def release(self) -> None:
        require(self.active and self.owner.active_borrows > 0,
                "reject twice-released synthetic source borrow")
        self.active = False
        self.owner.active_borrows -= 1


class SyntheticParser:
    """Independent bounded lexical model for old/new alternation equivalence."""

    def __init__(self, source: str, flags: int, scanner: bool, optimized: bool) -> None:
        self.source = source
        self.index = 0
        self.flags = flags
        self.depth = 0
        self.global_allowed = True
        self.scanner = scanner
        self.runtime_flags = flags
        self.optimized = optimized
        self.allocations = 0

    def leaf_flags(self, lexical: int) -> int:
        return self.runtime_flags if self.scanner else lexical

    def now(self) -> str | None:
        return self.source[self.index] if self.index < len(self.source) else None

    def skip(self, flags: int) -> None:
        if not flags & 2:
            return
        while self.index < len(self.source):
            value = self.source[self.index]
            if value in " \t\r\n":
                self.index += 1
            elif value == "#":
                self.index += 1
                while self.index < len(self.source) and self.source[self.index] != "\n":
                    self.index += 1
            else:
                return

    def group(self, flags: int) -> tuple:
        begin = self.index
        self.index += 1
        group_flags = flags
        if self.source.startswith("?:", self.index):
            self.index += 2
            kind = "plain"
        elif self.source.startswith("?i:", self.index):
            self.index += 3
            group_flags |= 1
            kind = "scoped-i"
        elif self.source.startswith("?-i:", self.index):
            self.index += 4
            group_flags &= ~1
            kind = "scoped-minus-i"
        elif self.source.startswith("?x:", self.index):
            self.index += 3
            group_flags |= 2
            kind = "scoped-x"
        elif self.source.startswith("?i)", self.index):
            if self.depth != 0 or not self.global_allowed:
                raise SyntheticError("global flags not at the start", begin)
            self.index += 3
            self.flags |= 1
            return ("global-i",)
        elif self.source.startswith("?#", self.index):
            self.index += 2
            while self.now() not in (None, ")"):
                if self.now() == "\\":
                    self.index += 1
                    if self.now() is None:
                        raise SyntheticError("bad escape", self.index - 1)
                self.index += 1
            if self.now() != ")":
                raise SyntheticError("unterminated comment", begin)
            self.index += 1
            return ("comment",)
        else:
            kind = "capture"
        self.depth += 1
        try:
            child = self.alt(group_flags)
            if self.now() != ")":
                raise SyntheticError("missing )", begin)
            self.index += 1
        finally:
            self.depth -= 1
        return ("group", kind, child)

    def seq(self, flags: int) -> tuple:
        result: list[tuple] = []
        while True:
            self.skip(flags)
            current = self.now()
            if current in (None, "|", ")"):
                return ("seq", tuple(result))
            if current == "\\":
                begin = self.index
                self.index += 1
                escaped = self.now()
                if escaped is None:
                    raise SyntheticError("bad escape", begin)
                self.index += 1
                result.append(("escaped", escaped, self.leaf_flags(flags)))
            elif current == "[":
                begin = self.index
                self.index += 1
                characters: list[str] = []
                while self.now() not in (None, "]"):
                    if self.now() == "\\":
                        self.index += 1
                        if self.now() is None:
                            raise SyntheticError("bad class escape", self.index - 1)
                    characters.append(self.now())
                    self.index += 1
                if self.now() != "]":
                    raise SyntheticError("unterminated class", begin)
                self.index += 1
                result.append(("class", tuple(characters), self.leaf_flags(flags)))
            elif current == "(":
                node = self.group(flags)
                if node[0] == "global-i":
                    flags = self.flags
                    continue
                if node[0] == "comment":
                    continue
                result.append(node)
            else:
                self.index += 1
                result.append(("literal", current, self.leaf_flags(flags)))
            self.global_allowed = False

    def alt(self, flags: int) -> tuple:
        first = self.seq(flags)
        if self.optimized and self.now() != "|":
            return first
        self.allocations += 1
        branches = [first]
        while self.now() == "|":
            self.global_allowed = False
            self.index += 1
            branch_flags = self.flags if self.depth == 0 else flags
            branches.append(self.seq(branch_flags))
        return first if len(branches) == 1 else ("alt", tuple(branches))

    def parse(self) -> tuple:
        result = self.alt(self.flags)
        self.skip(self.flags)
        if self.index != len(self.source):
            raise SyntheticError("unbalanced parenthesis", self.index)
        return result


def synthetic_outcome(value: str, flags: int, scanner: bool, optimized: bool) -> tuple:
    parser = SyntheticParser(value, flags, scanner, optimized)
    try:
        result = ("PASS", parser.parse(), parser.flags, parser.index)
    except SyntheticError as error:
        result = ("FAIL", error.text, error.position, parser.flags, parser.index)
    return result, parser.allocations


def synthetic_semantics() -> dict:
    corpus = (
        "", "a", "abc", "|", "a|", "|a", "||", "a|b", "a|b|c",
        "(a)", "((a))", "(?:a)", "(?:a|b)", "(?:|a|)", "(a|(?:b|c))",
        "(?i)a", "(?i)a|b", "(?i:a|B)", "(?-i:a|B)", "(?x:a | b)",
        "(?x:a # ignored | branch\n |b)", "a\\|b", "[|]", "[a|b]|c",
        "(?# ignored | pipe)a", "(?:a|)", "(?:|)", "(?:a|(?:|b))",
        "(", ")", "(?:a", "a)", "[", "[a", "\\", "(?#oops",
        "a(?i)b", "(?i:a(?i)b)", "a\\\\|b", "(?x:a\\|b # z\n| c)",
    )
    cases = 0
    no_alternation = 0
    actual_alternation = 0
    allocation_saved = 0
    error_cases = 0
    scanner_distinctions = 0
    for left in corpus:
        for suffix in ("", "|z", "(?:k|m)"):
            value = left + suffix
            for flags in (0, 1, 2, 3):
                for scanner in (False, True):
                    original, previous_allocations = synthetic_outcome(
                        value, flags, scanner, False,
                    )
                    improved, current_allocations = synthetic_outcome(
                        value, flags, scanner, True,
                    )
                    require(original == improved,
                            "synthetic alternation AST, flags, or diagnostic diverged")
                    require(0 <= current_allocations <= previous_allocations,
                            "lazy alternation introduced an eager allocation")
                    saved = previous_allocations - current_allocations
                    allocation_saved += saved
                    cases += 1
                    error_cases += int(original[0] == "FAIL")
                    if saved:
                        no_alternation += 1
                    if current_allocations:
                        actual_alternation += 1
                    if scanner:
                        nonscanner, _ = synthetic_outcome(value, flags, False, True)
                        scanner_distinctions += int(improved != nonscanner)
    # A synchronous borrow is legal only while its real owner remains live and
    # explicitly leased.  Exercise both use-after-free and early-owner-release.
    lifetime_controls = 0
    for kind in ("stack", "heap", "unicode-four-byte", "scanner-owned", "test-owned"):
        for copied in (False, True):
            for live_before, live_during, live_after in (
                (True, True, True), (True, True, False), (True, False, False),
                (False, False, False),
            ):
                owner = SyntheticSourceOwner((65, 124, 66, len(kind)))
                if not live_before:
                    owner.close()
                    try:
                        owner.borrow()
                    except FreezeError:
                        pass
                    else:
                        raise FreezeError("accepted a source borrowed after owner release")
                elif not live_during:
                    borrowed = owner.borrow()
                    try:
                        owner.close()
                    except FreezeError:
                        pass
                    else:
                        raise FreezeError("released a source during synchronous parsing")
                    owner.live = False
                    try:
                        borrowed.read(0)
                    except FreezeError:
                        pass
                    else:
                        raise FreezeError("accepted a dangling synthetic parser borrow")
                    owner.live = True
                    borrowed.release()
                    owner.close()
                else:
                    borrowed = owner.borrow()
                    observed = tuple(borrowed.read(index)
                                     for index in range(len(owner.values)))
                    if copied:
                        observed = tuple(list(observed))
                    require(observed == (65, 124, 66, len(kind)),
                            "borrowed and copied synchronous parsers disagree")
                    borrowed.release()
                    if not live_after:
                        owner.close()
                    require(owner.active_borrows == 0 and owner.live is live_after,
                            "retain no parser borrow after synchronous compilation")
                    try:
                        borrowed.read(0)
                    except FreezeError:
                        pass
                    else:
                        raise FreezeError("retained a released parser source view")
                lifetime_controls += 1
    require(cases >= 900 and no_alternation > 200 and actual_alternation > 200
            and allocation_saved > 300 and error_cases > 100
            and scanner_distinctions > 40 and lifetime_controls == 40,
            "require exhaustive alternate, empty, scoped, error, and lifetime models")
    return {"synthetic_case_count": cases,
            "synthetic_error_case_count": error_cases,
            "synthetic_no_alternation_improved_case_count": no_alternation,
            "synthetic_actual_alternation_case_count": actual_alternation,
            "synthetic_eager_allocations_eliminated": allocation_saved,
            "synthetic_distinct_scanner_runtime_flag_case_count": scanner_distinctions,
            "synthetic_source_lifetime_control_count": lifetime_controls,
            "old_and_new_ast_match": True,
            "old_and_new_error_position_match": True,
            "old_and_new_global_flags_match": True,
            "scoped_flags_preserved": True,
            "scanner_runtime_flags_preserved": True,
            "empty_leading_trailing_alternatives_preserved": True,
            "escaped_pipe_and_character_class_pipe_preserved": True,
            "verbose_and_parenthesized_comments_preserved": True,
            "dangling_source_borrow_rejected": True,
            "candidate_executed": False}


def owner_manifest(rows: tuple) -> list[dict]:
    return [owner_pin(row) for row in rows]


def build_contract(source_row: tuple, protocol_row: tuple,
                   proposal: dict, public: dict, semantics: dict) -> dict:
    return {
        "schema": SCHEMA,
        "version": 1,
        "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
        "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS",
        "family": "rust",
        "immutable_goal_sha256": GOAL_SHA256,
        "source": owner_pin(source_row),
        "protocol": owner_pin(protocol_row),
        "authenticated_frozen_owners": owner_manifest(OWNERS),
        "original_correctness_history": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_reference_case_count": 8244,
            "supplemental_reference_counted_in_original_denominator": False,
        },
        "actual_complete_v24_candidate_failure": {
            "receipt_sha256": ACTUAL_V24_SHA256,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "case_execution_denominator": 31237,
            "completed_suite_count": 13,
            "actual_candidate_worker_count": 13,
            "semantic_mismatch_count": 1352,
            "fully_observed_suite_mismatch_counts": {
                "substitution_v2": 240, "shape_v2": 1112,
            },
            "verified_passing_case_count": 15877,
            "candidate_qualified": False,
        },
        "first_party_crate": {
            "package_count": 1,
            "external_dependency_count": 0,
            "runtime_external_regex_engine": False,
            "stdlib_matching_delegation": False,
            "another_candidate_engine_delegation": False,
        },
        "derived_first_party_compiler_source": {
            "source_base_path": "candidates/rust/src/lib.rs",
            "source_base_sha256": ORIGINAL_SHA256,
            "source_base_bytes": ORIGINAL_BYTES,
            "target_path": VARIANT,
            "sha256": DERIVED_SHA256,
            "bytes": DERIVED_BYTES,
            "source_delta_bytes": DERIVED_BYTES - ORIGINAL_BYTES,
            "exact_reversible_replacement_count": len(REPLACEMENTS),
            "semantic_optimization_count": 2,
            "semantic_optimizations": [
                "borrow the C-owned u32 pattern only during synchronous parsing",
                "allocate alternation branches only after an actual unescaped pipe",
            ],
            "normal_pattern_u32_heap_clone_removed": True,
            "scanner_phrase_u32_heap_clone_removed": True,
            "alternation_free_parser_heap_allocation_removed": True,
            "ordinary_two_branch_initial_growth_removed": True,
            "rust_test_helper_retains_owned_source": True,
            "parser_constructor_count": 3,
            "parser_borrow_retained_by_engine": False,
            "capture_clamp_variant_changed": False,
            "bridge_source_changed": False,
            "public_python_api_changed": False,
            "original_p0_denominator_changed": False,
            "external_dependencies_added": 0,
            "materialized": False,
            "built": False,
            "executed": False,
            "candidate_correctness": NOT_MEASURED,
            "performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
        },
        "independent_existing_public_practice": public,
        "synthetic_differential_compiler_semantics": semantics,
        "expanded_final_holdout_metadata_only": proposal,
        "physical_source_wall": {
            "policy": "DENY DEFAULT; EXACT PUBLIC EVIDENCE AND TWO FIRST-PARTY SOURCES",
            "installed_before_owner_reads": True,
            "allowed_candidate_source_owner_count": 2,
            "allowed_native_binary_count": 0,
            "allowed_archive_count": 0,
            "allowed_holdout_content_count": 0,
            "allowed_unopened_holdout_metadata_count": 1,
            "source_modes_filesystem_writes_allowed": False,
            "candidate_or_compiler_process_allowed": False,
            "clock_access_allowed": False,
            "apply_requires_matching_frozen_and_pushed_commit": True,
            "apply_target_policy": "EXCLUSIVE O_NOFOLLOW|O_CREAT|O_EXCL EXACTLY ONCE",
        },
        "source_only_effects": {
            "candidate_source_files_read": 2,
            "public_existing_practice_evidence_files_read": 3,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "reference_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "native_binary_files_opened": 0,
            "compressed_archives_opened": 0,
            "private_roots_opened": 0,
            "network_requests": 0,
            "clock_samples": 0,
            "new_timing_trials_run": 0,
            "holdout_cases_generated": 0,
            "holdout_cases_opened": 0,
            "holdout_proposal_content_open_count": 0,
            "holdout_proposal_metadata_probe_count": 1,
            "holdout": "NOT OPENED",
            "final_holdout_proposal_case_count": 141557760,
            "candidate_correctness": NOT_MEASURED,
            "optimized_candidate_speed": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def rejected(action, label: str) -> str:
    try:
        action()
    except (FreezeError, OSError, TypeError, ValueError, UnicodeError):
        return label
    raise FreezeError("hostile compiler control was not rejected: " + label)


def self_test(wall: SourceWall, rust: bytes,
              semantics: dict, public: dict) -> list[str]:
    controls: list[str] = []
    for label, previous, corrected in REPLACEMENTS:
        for forged in (rust + b"\n", rust.replace(previous, b"", 1),
                       rust.replace(previous, previous + previous, 1),
                       rust.replace(previous, corrected, 1)):
            controls.append(rejected(lambda item=forged: derive_source(item),
                                     "reject-forged-source-" + label))
    for value in ("", "x", "0" * 63, "0" * 65, "F" * 64,
                  "0" * 63 + "z", None, 0, [], {}):
        controls.append(rejected(lambda item=value: check_sha(item, "hostile"),
                                 "reject-invalid-sha256"))
    forbidden = (
        (ROOT + "/candidates/rust_candidate.py", "candidate-adapter"),
        (ROOT + "/candidates/rust/py_bridge.c", "unowned-canonical-bridge"),
        (ROOT + "/candidates/rust/src/search.rs", "unowned-rust-search"),
        (ROOT + "/candidates/rust/src/stack.rs", "unowned-rust-stack"),
        (ROOT + "/candidates/_rust_engine.so", "native-engine"),
        (ROOT + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "native-bridge"),
        (ROOT + "/" + PROPOSAL, "unopened-final-holdout-proposal"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json", "older-holdout"),
        (ROOT + "/oracle/phase2/evidence/forbidden.json.gz", "compressed-archive"),
        (ROOT + "/experiments/rust_public_profile_v1/public-run-001/stdlib.er/heaptrace",
         "unapproved-profiler-native-archive"),
        (ROOT + "/tools/../candidates/rust_candidate.py", "path-traversal"),
        (ROOT + "/candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs",
         "premature-derived-candidate"),
        ("/tmp/rebar-phase2-native-build-v9-rust-3v12tbmr", "private-native-root"),
        ("/etc/hosts", "host-file"),
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    for path, label in forbidden:
        controls.append(rejected(lambda item=path: os.open(item, flags),
                                 "wall-rejects-open-" + label))
        controls.append(rejected(lambda item=path: wall.native_open(item, flags),
                                 "wall-rejects-native-open-" + label))
    actions = (
        ("builtins-open", lambda: builtins.open(ROOT + "/" + OWNERS[6][1], "rb")),
        ("_io-open", lambda: _io.open(ROOT + "/" + OWNERS[6][1], "rb")),
        ("io-open", lambda: io.open(ROOT + "/" + OWNERS[6][1], "rb")),
        ("foreign-read", lambda: os.read(0, 1)),
        ("foreign-write", lambda: os.write(1, b"x")),
        ("foreign-stat", lambda: os.fstat(0)),
        ("foreign-close", lambda: os.close(0)),
        ("ordinary-stat", lambda: os.stat(ROOT + "/" + OWNERS[6][1])),
        ("second-proposal-stat", lambda: os.lstat(ROOT + "/" + PROPOSAL)),
        ("clock-time", lambda: time.time()),
        ("clock-monotonic", lambda: time.monotonic()),
        ("clock-perf-counter", lambda: time.perf_counter()),
        ("entropy", lambda: os.urandom(1)),
        ("stdlib-matcher-import", lambda: sys.audit("import", "re", None)),
        ("external-matcher-import", lambda: sys.audit("import", "regex", None)),
        ("native-dynamic-loader", lambda: sys.audit("ctypes.dlopen", "foreign")),
        ("worker", lambda: sys.audit("subprocess.Popen", "worker")),
        ("interpreter", lambda: sys.audit("cpython.PyInterpreterState_New")),
        ("network", lambda: sys.audit("socket.connect", "foreign")),
        ("dynamic-code", lambda: sys.audit("exec", "foreign")),
        ("canonical-source-write", lambda: os.open(ROOT + "/" + OWNERS[6][1],
                                                     os.O_WRONLY | os.O_TRUNC)),
        ("source-freeze-write", lambda: os.open(ROOT + "/" + SOURCE,
                                                  os.O_WRONLY | os.O_TRUNC)),
        ("variant-write", lambda: os.open(ROOT + "/" + VARIANT,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0))),
        ("variant-directory", lambda: os.mkdir(wall.parent, 0o700)),
    )
    for label, action in actions:
        controls.append(rejected(action, "wall-rejects-" + label))
    for raw in (b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}',
                b'{"x":01}', b'{"x":"\\ud800"}', b'{"x":[1,]}',
                b'{"x":1} trailing', b'[{]'):
        controls.append(rejected(lambda item=raw: StrictJSON(item).decode(),
                                 "reject-hostile-json"))
    for value in (-1, 0, 31236, 31238, 1664, 416):
        controls.append(rejected(lambda item=value: require(item == 31237,
                                                             "P0 denominator changed"),
                                 "reject-changed-original-denominator"))
    for bogus in (0, 1, 415, 417, 31237, 141557760):
        controls.append(rejected(lambda item=bogus: require(item == public["case_count"],
                                                             "public denominator changed"),
                                 "reject-changed-public-denominator"))
    require(semantics["synthetic_case_count"] >= 900
            and semantics["synthetic_source_lifetime_control_count"] == 40
            and len(controls) >= 100 and not wall.live and wall.output is None
            and wall.proposal_open_count == 0,
            "require complete hostile physical and semantic compiler controls")
    no_matching_imports()
    return controls


def parse_arguments(values: list[str]) -> dict:
    require(bool(values), "select one explicit source-only or root-only mode")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject candidate, compiler, worker, benchmark, and holdout execution")
    names = ["--source-sha256", "--protocol-sha256"]
    if mode != "--render-contract":
        names.append("--contract-sha256")
    if mode == "--apply":
        names.extend(("--frozen-commit", "--pushed-commit"))
    require(len(values) == 1 + 2 * len(names),
            "require exact frozen source pins and explicit root push attestation")
    pins: dict[str, str] = {}
    for index in range(1, len(values), 2):
        name, value = values[index], values[index + 1]
        require(name in names and name not in pins,
                "reject repeated or invented compiler optimization authority")
        if name.endswith("sha256"):
            pins[name] = check_sha(value, name)
        else:
            require(type(value) is str and len(value) == 40
                    and all(item in "0123456789abcdef" for item in value),
                    "require complete lowercase pushed commit identity")
            pins[name] = value
    require(set(pins) == set(names), "reject missing source-freeze authority")
    if mode == "--apply":
        require(pins["--frozen-commit"] == pins["--pushed-commit"],
                "root may apply only after the complete freeze commit was pushed")
    return {"mode": mode, "pins": pins}


def load_context(wall: SourceWall, pins: dict, render: bool) -> dict:
    source_row = dynamic_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = dynamic_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source_row)
    read_owner(wall, protocol_row)
    contract_row = None
    if not render:
        contract_row = dynamic_owner(wall, "contract", CONTRACT, pins["--contract-sha256"])

    evidence = {row[0]: read_owner(wall, row) for row in OWNERS}
    original = json_object(evidence["original_oracle"], "frozen original P0")
    supplemental = json_object(evidence["supplemental_oracle"], "independent supplemental P0")
    actual = json_object(evidence["actual_v24_failure"], "complete V24 Rust failure")
    validate_oracles(original, supplemental, actual)
    validate_first_party(evidence["first_party_cargo_manifest"],
                         evidence["first_party_cargo_lock"],
                         evidence["first_party_v24_bridge"])
    profile = json_object(evidence["public_profile_contract"], "frozen public profile")
    baseline = json_object(evidence["public_stdlib_correctness"], "public stdlib correctness")
    candidate = json_object(evidence["public_rust_correctness"], "public Rust correctness")
    paired = json_object(evidence["public_paired_timing"], "complete paired public rows")
    public = validate_public_profile(profile, baseline, candidate, paired)
    proposal = proposal_metadata(wall)
    corrected = derive_source(evidence["first_party_rust_compiler"])
    semantics = synthetic_semantics()
    frozen = build_contract(source_row, protocol_row, proposal, public, semantics)
    if not render:
        assert contract_row is not None
        contract = read_owner(wall, contract_row)
        require(contract == document(frozen)
                and json_object(contract, "complete frozen compiler contract") == frozen,
                "reject incomplete or altered compiler optimization obligations")
    require(not wall.live and wall.output is None and wall.proposal_open_count == 0,
            "close every public descriptor without opening a candidate or holdout")
    no_matching_imports()
    return {"contract": frozen, "corrected": corrected,
            "rust": evidence["first_party_rust_compiler"],
            "semantics": semantics, "public": public}


def apply_exact_once(wall: SourceWall, corrected: bytes) -> dict:
    require(wall.apply and not wall.directory_created and not wall.output_opened
            and digest(corrected) == DERIVED_SHA256 and len(corrected) == DERIVED_BYTES,
            "root apply requires the exact authenticated derived Rust source")
    os.mkdir(wall.parent, 0o700)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(wall.target, flags, 0o600)
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and stat.S_IMODE(initial.st_mode) == 0o600
                and initial.st_dev == DEVICE and initial.st_nlink == 1
                and initial.st_uid == os.geteuid() and initial.st_size == 0,
                "require one exclusive empty private compiler variant")
        offset = 0
        while offset < len(corrected):
            written = os.write(descriptor, memoryview(corrected)[offset:])
            require(type(written) is int and written > 0,
                    "reject incomplete exclusive compiler variant")
            offset += written
        os.fsync(descriptor)
        complete = os.fstat(descriptor)
        require(complete.st_dev == initial.st_dev and complete.st_ino == initial.st_ino
                and complete.st_size == DERIVED_BYTES and complete.st_nlink == 1
                and stat.S_IMODE(complete.st_mode) == 0o600,
                "reject altered or exchanged compiler variant")
        return {"path": VARIANT, "sha256": DERIVED_SHA256,
                "bytes": DERIVED_BYTES, "device": complete.st_dev,
                "inode": complete.st_ino, "mode": "0600", "nlink": 1,
                "exclusive_no_follow": True, "materialized_once": True}
    finally:
        os.close(descriptor)


def main() -> int:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON and sys.flags.isolated == 1
            and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
            "require pinned CPython 3.14.6 under -I -B -S")
    no_matching_imports()
    selection = parse_arguments(list(sys.argv[1:]))
    wall = SourceWall(selection["mode"] == "--apply")
    wall.install()
    state = load_context(wall, selection["pins"],
                         selection["mode"] == "--render-contract")
    if selection["mode"] == "--render-contract":
        sys.stdout.buffer.write(document(state["contract"]))
        sys.stdout.buffer.flush()
        return 0
    controls = (self_test(wall, state["rust"], state["semantics"], state["public"])
                if selection["mode"] == "--self-test" else [])
    materialized = (apply_exact_once(wall, state["corrected"])
                    if selection["mode"] == "--apply" else None)
    require(not wall.live and wall.output is None,
            "release all isolated compiler source descriptors")
    no_matching_imports()
    result = {
        "schema": SCHEMA + "-source-only-gate",
        "status": "PASS",
        "version": 1,
        "mode": selection["mode"][2:],
        "source_sha256": selection["pins"]["--source-sha256"],
        "protocol_sha256": selection["pins"]["--protocol-sha256"],
        "contract_sha256": selection["pins"]["--contract-sha256"],
        "authenticated_frozen_owner_count": len(OWNERS) + 3,
        "original_case_execution_denominator": 31237,
        "actual_v24_candidate_status": "FAIL",
        "actual_v24_semantic_mismatch_count": 1352,
        "actual_v24_verified_passing_case_count": 15877,
        "canonical_rust_source_sha256": ORIGINAL_SHA256,
        "canonical_rust_source_bytes": ORIGINAL_BYTES,
        "derived_rust_source_sha256": DERIVED_SHA256,
        "derived_rust_source_bytes": DERIVED_BYTES,
        "exact_reversible_replacement_count": 7,
        "semantic_optimization_count": 2,
        "synthetic_differential_case_count": state["semantics"]["synthetic_case_count"],
        "synthetic_source_lifetime_control_count":
            state["semantics"]["synthetic_source_lifetime_control_count"],
        "preserved_public_practice_case_count": 416,
        "preserved_public_paired_row_count": 1664,
        "preserved_public_paired_raw_sha256": OWNERS[13][2],
        "hostile_control_count": len(controls),
        "hostile_controls": controls,
        "physically_blocked_effects": dict(wall.blocked),
        "unopened_final_holdout_proposal_case_count": 141557760,
        "holdout_content_open_count": 0,
        "holdout_metadata_probe_count": 1,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "native_binaries_opened": 0,
        "clock_samples": 0,
        "new_timing_trials_run": 0,
        "holdout": "NOT OPENED",
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "candidate_correctness": NOT_MEASURED,
        "candidate_qualified": False,
        "winner_selected": False,
        "variant_materialized": materialized is not None,
        "materialized_variant": materialized,
    }
    if materialized is not None:
        result["frozen_pushed_commit"] = selection["pins"]["--pushed-commit"]
    sys.stdout.buffer.write(document(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, TypeError, ValueError) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        raise SystemExit(2)
