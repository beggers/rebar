#!/usr/bin/env python3
"""Freeze a first-party Rust scoped-Unicode start-set soundness correction.

Source verification authenticates plaintext ledgers, public receipts, and Rust
sources only.  It never opens a raw observation, archive, native binary, final
holdout, or private build root.  Root-only materialization is separately gated
on the committed and pushed three-owner freeze.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("scoped-Unicode source verification must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_scoped_unicode_startset_v1.py"
PROTOCOL = "oracle/phase2/RUST-SCOPED-UNICODE-STARTSET-V1.md"
CONTRACT = "oracle/phase2/rust-scoped-unicode-startset-v1.json"
PARENT = "candidates/rust/variants"
DIRECTORY = "scoped_unicode_startset_v1"
TARGET = PARENT + "/" + DIRECTORY + "/lib.rs"
SCHEMA = "rebar-owned-rust-scoped-unicode-startset-v1-source-freeze"
DEVICE = 2064
PARENT_INODE = 524946
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_DEPTH = 72
NOT_MEASURED = "NOT MEASURED"

A = 256
I = 2
L = 4
U = 32
BYTE = 1 << 31
PUBLISHED_SEED = 5928217332825411634
MATRIX_SHA256 = "0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d"

CANONICAL_SHA256 = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
CANONICAL_BYTES = 177967
CORRECTED_SHA256 = "e5971616329a1622a7514954ec26871ff8465db87ad1a956cea104ee8a8478ac"
CORRECTED_BYTES = 178037
ANCHOR_SHA256 = "5fa8c47c88c1f5d830a59735946378910374afab6f1558d281f0254207ad5e84"
ANCHOR_CORRECTED_SHA256 = "b5172d0506b67f484254f4488b8023591c353cb40140e652b4f993875d3ea1ab"
ANCHOR_CORRECTED_BYTES = 189439
COMBINED_SHA256 = "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
COMBINED_CORRECTED_SHA256 = "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38"
COMBINED_CORRECTED_BYTES = 189493
COMBINED_SEARCH_SHA256 = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"

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

# role, repository-relative plaintext owner, SHA-256, bytes, inode.
# Raw benchmark observations, native objects, compressed archives, final cases,
# and private roots are intentionally absent from the complete allowlist.
OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_p0_ledger", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("actual_v25_original_failure",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-"
     "rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json",
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("public_matrix_source", "tools/rust_public_practice_benchmark_v2.py",
     "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6", 112729, 429259),
    ("public_matrix_protocol", "oracle/phase3/RUST-PUBLIC-PRACTICE-BENCHMARK-V2.md",
     "4040c458119a6d347c1eb876e1120a4400f76b8f16611d21de15371b50508586", 8982, 525935),
    ("public_matrix_contract", "oracle/phase3/rust-public-practice-benchmark-v2.json",
     "7c4120c549a006cc162abb545032e1808637cf3c088f4a21023d5c99fb351e4a", 10117, 525936),
    ("native_public_gate_source", "tools/run_owned_rust_native_architecture_public_gate_v2.py",
     "96f7770f9b5eec4a093435f94e1a6158b78bcdbba045cb76386018a298103a1d", 89208, 430802),
    ("native_public_gate_protocol", "oracle/phase2/RUST-NATIVE-ARCHITECTURE-PUBLIC-GATE-V2.md",
     "dfc84515df187cc0c7318eb9d36d33ad8472a6df02864c7297ada546a60446a8", 5053, 525228),
    ("native_public_gate_contract", "oracle/phase2/rust-native-architecture-public-gate-v2.json",
     "aca87ed3450127bc7afc3829bea37ac4087b41a2e2be84d39f80244d3748ef17", 19717, 525234),
    ("v26_build_publication",
     "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-"
     "mandatory-anchor-root-provenance-publication-receipt.json",
     "8a0e9d70dab2a3e1f3738d6e0e1a4716b78e0a1b329ce3b16010bd94b6598cd6", 5075, 524963),
    ("v26_root_provenance",
     "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-"
     "mandatory-anchor-root-provenance-root-provenance-receipt.json",
     "aaed35f9fe86090d75ce2162bae7902910461a7b4e731c22eba275406f328ba1", 76442, 524964),
    ("v27_build_publication",
     "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-"
     "compiler-fast-v1-root-provenance-publication-receipt.json",
     "7fcbe3e07885f2a488ed1b3c79bc02888ad22dd2b21179081b3cecfc7b464c99", 6444, 524869),
    ("v27_root_provenance",
     "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-"
     "compiler-fast-v1-root-provenance-root-provenance-receipt.json",
     "c6958056757ab6145d613490db1a21165714dcb89c61e6d3bdf52500fad221b0", 64122, 524870),
    ("v26_public_result",
     "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-anchor-"
     "public-run-001-publication-receipt.json",
     "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80", 40906, 525333),
    ("v27_public_result",
     "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-compiler-"
     "public-run-001-publication-receipt.json",
     "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449", 68330, 525426),
    ("combined_transformer_source",
     "tools/apply_owned_rust_combined_search_compiler_fastpath_v2.py",
     "f8f2f7cf4e9339cf592048fd75cafe9a9d22d79c77137d1f8ab6d3b7493d976b", 89742, 430531),
    ("combined_transformer_protocol",
     "oracle/phase2/RUST-COMBINED-SEARCH-COMPILER-FASTPATH-V2.md",
     "b612af3b53bb21b6f13b69db4c4197590a71af045fab14de250dad301a1794a1", 5577, 524866),
    ("combined_transformer_contract",
     "oracle/phase2/rust-combined-search-compiler-fastpath-v2.json",
     "68f097d8433596fb45a9a9ca940eff68dcb8fe9f0d667a8c0ce9c5eb403196a6", 13914, 524939),
    ("combined_materialization",
     "oracle/phase2/evidence/rust-combined-search-compiler-fastpath-v2-application.json",
     "1bce63305e04e4056ce3c660760a0bb8a3670a76aa528b9309232d0918c5061e", 2201, 525099),
    ("cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("canonical_engine", "candidates/rust/src/lib.rs",
     CANONICAL_SHA256, CANONICAL_BYTES, 428096),
    ("mandatory_anchor_engine", "candidates/rust/variants/mandatory_anchor_search_v1/lib.rs",
     ANCHOR_SHA256, 189369, 526181),
    ("combined_engine", "candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs",
     COMBINED_SHA256, 189423, 525097),
    ("combined_search", "candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs",
     COMBINED_SEARCH_SHA256, 24305, 525098),
)


class FreezeError(Exception):
    """The physical wall, authenticated evidence, or one-site proof failed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash complete immutable bytes")
    return hashlib.sha256(value).hexdigest()


def exact_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1, "require one complete SHA-256: " + label)
    assert isinstance(value, str)
    return value


def exact_commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1, "require one complete pushed commit: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "subprocess", "socket", "threading", "multiprocessing",
                 "random", "json", "candidates", "rebar", "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject imported matcher, candidate, native loader, process, or generator")


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive frozen JSON nesting")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        substitutions = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                         "\n": "\\n", "\r": "\\r", "\t": "\\t"}
        require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value),
                "reject a frozen JSON surrogate")
        return '"' + "".join(substitutions.get(char, "\\u" + format(ord(char), "04x")
                                                if ord(char) < 32 else char)
                               for char in value) + '"'
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject nontext frozen JSON keys")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported frozen JSON value")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class StrictJSON:
    """Decode bounded public JSON without importing Python's regex-backed decoder."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require complete bounded immutable JSON bytes")
        self.text = raw.decode("utf-8", "strict")
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\n\r":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "require a JSON string")
        self.index += 1
        items: list[str] = []
        escapes = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                   "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            value = self.text[self.index]
            self.index += 1
            if value == '"':
                return "".join(items)
            if value != "\\":
                require(ord(value) >= 32 and not 0xD800 <= ord(value) <= 0xDFFF,
                        "reject an invalid JSON string character")
                items.append(value)
                continue
            require(self.index < len(self.text), "reject an incomplete JSON escape")
            value = self.text[self.index]
            self.index += 1
            if value != "u":
                require(value in escapes, "reject an unknown JSON escape")
                items.append(escapes[value])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(char in "0123456789abcdefABCDEF"
                                             for char in digits),
                    "reject an incomplete JSON Unicode escape")
            self.index += 4
            number = int(digits, 16)
            if 0xD800 <= number <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject an unpaired high surrogate")
                lower = self.text[self.index + 2:self.index + 6]
                require(len(lower) == 4 and all(char in "0123456789abcdefABCDEF"
                                                for char in lower),
                        "reject a malformed low surrogate")
                low = int(lower, 16)
                require(0xDC00 <= low <= 0xDFFF, "reject an unpaired high surrogate")
                self.index += 6
                number = 0x10000 + ((number - 0xD800) << 10) + low - 0xDC00
            else:
                require(not 0xDC00 <= number <= 0xDFFF, "reject an unpaired low surrogate")
            items.append(chr(number))
        raise FreezeError("reject an unterminated JSON string")

    def number(self) -> int | float:
        first = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject an incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or self.text[self.index] not in "0123456789",
                    "reject a leading-zero JSON number")
        else:
            require(self.text[self.index] in "123456789", "reject a malformed JSON number")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        fractional = False
        if self.text[self.index:self.index + 1] == ".":
            fractional = True
            self.index += 1
            require(self.index < len(self.text) and self.text[self.index] in "0123456789",
                    "reject a malformed JSON fraction")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        if self.text[self.index:self.index + 1] in ("e", "E"):
            fractional = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            require(self.index < len(self.text) and self.text[self.index] in "0123456789",
                    "reject a malformed JSON exponent")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        literal = self.text[first:self.index]
        if not fractional:
            return int(literal)
        result = float(literal)
        require(result == result and result not in (float("inf"), float("-inf")),
                "reject a nonfinite JSON number")
        return result

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject excessive public evidence nesting")
        self.whitespace()
        require(self.index < len(self.text), "reject incomplete JSON evidence")
        current = self.text[self.index]
        if current == '"':
            return self.string()
        if current == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "reject duplicate JSON object keys")
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "reject a malformed JSON object")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                require(separator in (",", "}"), "reject a malformed JSON object separator")
                self.index += 1
                if separator == "}":
                    return result
        if current == "[":
            self.index += 1
            result: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result
            while True:
                result.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                require(separator in (",", "]"), "reject a malformed JSON array separator")
                self.index += 1
                if separator == "]":
                    return result
        if current == "-" or current in "0123456789":
            return self.number()
        for spelling, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(spelling, self.index):
                self.index += len(spelling)
                return value
        raise FreezeError("reject malformed or nonfinite public JSON evidence")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing JSON evidence")
        return result


def json_object(raw: bytes, label: str) -> dict[str, object]:
    result = StrictJSON(raw).decode()
    require(type(result) is dict, "require a complete JSON object: " + label)
    assert isinstance(result, dict)
    return result


class SourceWall:
    """Deny-default owner descriptors; optionally publish one exclusive child file."""

    def __init__(self, apply: bool) -> None:
        self.apply = apply
        self.allowed = frozenset(
            (ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT)
            + tuple(ROOT + "/" + row[1] for row in OWNERS)
        )
        self.parent_path = ROOT + "/" + PARENT
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
        raise FreezeError("scoped-Unicode source wall rejected " + category)

    def approved_owner(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/") and path == os.path.normpath(path)
                and not any(piece in (".", "..") for piece in path.split("/"))
                and not path.endswith((".so", ".gz", ".raw.json", ".jsonl")))

    def temporary(self, flags: object) -> bool:
        flag = getattr(os, "O_TMPFILE", 0)
        return type(flags) is int and flag != 0 and flags & flag == flag

    def directory_flags(self, flags: object) -> bool:
        required = os.O_DIRECTORY | os.O_NOFOLLOW
        destructive = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_TRUNC | os.O_APPEND
        return (type(flags) is int and flags & required == required
                and not flags & destructive and not self.temporary(flags))

    def output_flags(self, flags: object) -> bool:
        required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        forbidden = os.O_RDWR | os.O_TRUNC | os.O_APPEND | os.O_DIRECTORY
        return (type(flags) is int and flags & required == required
                and not flags & forbidden and not self.temporary(flags))

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            owner = (self.approved_owner(path) and type(flags) is int
                     and flags & os.O_NOFOLLOW
                     and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                                      | os.O_TRUNC | os.O_APPEND | os.O_DIRECTORY)
                     and not self.temporary(flags))
            parent = (self.apply and self.stage == "ready" and path == self.parent_path
                      and self.directory_flags(flags))
            child = (self.apply and self.stage == "created" and path == DIRECTORY
                     and self.directory_flags(flags))
            output = (self.apply and self.stage == "child" and path == "lib.rs"
                      and self.output_flags(flags) and not self.output_opened)
            if not any((owner, parent, child, output)):
                self.deny("unowned-source-native-raw-archive-final-or-write-open")
        elif event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            directory = arguments[2] if len(arguments) > 2 else None
            if not (self.apply and self.stage == "parent" and path == DIRECTORY
                    and mode == 0o700 and directory == self.parent_fd):
                self.deny("unapproved-directory-mutation")
        elif (event in ("import", "compile", "exec", "marshal.loads", "code.__new__",
                        "sys.addaudithook", "os.system", "os.fork", "os.posix_spawn",
                        "os.posix_spawnp", "os.rename", "os.replace", "os.remove",
                        "os.unlink", "os.rmdir", "os.chmod", "os.chown", "os.link",
                        "os.symlink", "os.truncate", "os.putenv", "os.unsetenv",
                        "os.urandom", "os.getrandom")
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
        require(not self.installed, "install one irreversible scoped-Unicode wall")
        native_open = os.open
        native_read = os.read
        native_write = os.write
        native_fstat = os.fstat
        native_close = os.close
        native_fsync = os.fsync
        native_mkdir = os.mkdir

        def guarded_open(path: object, flags: object, mode: int = 0o777,
                         *, dir_fd: object = None) -> int:
            require(type(flags) is int and type(mode) is int,
                    "reject malformed source-only descriptor flags")
            owner = (dir_fd is None and self.approved_owner(path)
                     and flags & os.O_NOFOLLOW
                     and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                                      | os.O_TRUNC | os.O_APPEND | os.O_DIRECTORY)
                     and not self.temporary(flags))
            parent = (self.apply and self.stage == "ready" and path == self.parent_path
                      and dir_fd is None and self.directory_flags(flags))
            child = (self.apply and self.stage == "created" and path == DIRECTORY
                     and dir_fd == self.parent_fd and self.directory_flags(flags))
            output = (self.apply and self.stage == "child" and path == "lib.rs"
                      and dir_fd == self.child_fd and self.output_flags(flags)
                      and mode == 0o600 and not self.output_opened)
            if not any((owner, parent, child, output)):
                self.deny("foreign-owner-directory-or-output-descriptor")
            descriptor = native_open(path, flags, mode, dir_fd=dir_fd)
            require(type(descriptor) is int and descriptor >= 0
                    and descriptor not in self.owner_fds
                    and descriptor not in (self.parent_fd, self.child_fd, self.output_fd),
                    "reject an invalid, inherited, or reused source descriptor")
            if owner:
                self.owner_fds.add(descriptor)
            elif parent:
                self.parent_fd = descriptor
                self.stage = "parent"
            elif child:
                self.child_fd = descriptor
                self.stage = "child"
            else:
                self.output_fd = descriptor
                self.output_opened = True
            return descriptor

        def guarded_read(descriptor: object, count: object) -> bytes:
            if (type(descriptor) is not int or descriptor not in self.owner_fds
                    or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES):
                self.deny("foreign-or-unbounded-source-descriptor-read")
            return native_read(descriptor, count)

        def guarded_write(descriptor: object, value: object) -> int:
            if (not self.apply or descriptor != self.output_fd
                    or type(value) not in (bytes, memoryview)):
                self.deny("unapproved-source-or-inherited-descriptor-write")
            block = bytes(value)
            if not block or block != self.expected[self.written:self.written + len(block)]:
                self.deny("unapproved-or-out-of-order-corrected-source-bytes")
            written = native_write(descriptor, value)
            require(type(written) is int and 0 < written <= len(block),
                    "reject incomplete exclusive corrected-source writes")
            self.written += written
            return written

        def guarded_fstat(descriptor: object) -> os.stat_result:
            if (type(descriptor) is not int or descriptor not in self.owner_fds
                    and descriptor not in (self.parent_fd, self.child_fd, self.output_fd)):
                self.deny("foreign-descriptor-metadata")
            return native_fstat(descriptor)

        def guarded_close(descriptor: object) -> None:
            if type(descriptor) is not int:
                self.deny("foreign-descriptor-close")
            if descriptor in self.owner_fds:
                self.owner_fds.remove(descriptor)
            elif descriptor == self.output_fd:
                require(self.output_synced and self.written == len(self.expected),
                        "never close unsynchronized or incomplete corrected source")
                self.output_fd = None
            elif descriptor == self.child_fd:
                require(self.child_synced and self.output_fd is None,
                        "synchronize the corrected child before closing it")
                self.child_fd = None
            elif descriptor == self.parent_fd:
                require(self.parent_synced and self.child_fd is None,
                        "synchronize the parent after the completed child")
                self.parent_fd = None
            else:
                self.deny("foreign-descriptor-close")
            native_close(descriptor)

        def guarded_fsync(descriptor: object) -> None:
            if not self.apply or type(descriptor) is not int:
                self.deny("foreign-source-or-inherited-descriptor-fsync")
            if descriptor == self.output_fd:
                require(self.written == len(self.expected) and not self.output_synced,
                        "synchronize the exact complete corrected source once")
                native_fsync(descriptor)
                self.output_synced = True
            elif descriptor == self.child_fd:
                require(self.output_synced and self.output_fd is None and not self.child_synced,
                        "synchronize the corrected child only after its complete source")
                native_fsync(descriptor)
                self.child_synced = True
            elif descriptor == self.parent_fd:
                require(self.child_synced and self.child_fd is None and not self.parent_synced,
                        "synchronize the parent only after its complete private child")
                native_fsync(descriptor)
                self.parent_synced = True
            else:
                self.deny("foreign-source-or-inherited-descriptor-fsync")

        def guarded_mkdir(path: object, mode: int = 0o777,
                          *, dir_fd: object = None) -> None:
            if (not self.apply or self.stage != "parent" or path != DIRECTORY
                    or mode != 0o700 or dir_fd != self.parent_fd):
                self.deny("unapproved-private-variant-directory")
            native_mkdir(path, mode, dir_fd=dir_fd)
            self.stage = "created"

        authorization = self.apply

        def immutable_audit(event: str, arguments: tuple[object, ...]) -> None:
            if self.apply is not authorization:
                self.deny("forged-root-materialization-authority")
            self.audit(event, arguments)

        sys.addaudithook(immutable_audit)
        native_module = sys.modules.get("posix")
        require(native_module is not None, "authenticate the existing native OS module")
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                setattr(module, "open_code", self.forbidden("direct-open-code"))
        os.open = guarded_open
        os.read = guarded_read
        os.write = guarded_write
        os.fstat = guarded_fstat
        os.close = guarded_close
        os.fsync = guarded_fsync
        os.mkdir = guarded_mkdir
        native_module.open = guarded_open
        native_module.read = guarded_read
        native_module.write = guarded_write
        native_module.fstat = guarded_fstat
        native_module.close = guarded_close
        native_module.fsync = guarded_fsync
        native_module.mkdir = guarded_mkdir
        for name in ("fdopen", "dup", "dup2", "stat", "lstat", "readlink", "listdir",
                     "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
                     "posix_spawnp", "system", "makedirs", "remove", "unlink", "rename",
                     "replace", "rmdir", "chmod", "chown", "urandom", "getrandom",
                     "pread", "pwrite", "preadv", "pwritev", "readv", "writev",
                     "sendfile", "copy_file_range", "splice", "truncate", "ftruncate",
                     "utime", "link", "symlink", "fchmod", "fchown", "mknod", "mkfifo",
                     "execv", "execve", "execvp", "execvpe", "execl", "execle",
                     "execlp", "execlpe", "spawnl", "spawnle", "spawnlp", "spawnlpe",
                     "spawnv", "spawnve", "spawnvp", "spawnvpe", "kill", "killpg",
                     "chdir", "fchdir", "setuid", "setgid", "setreuid", "setregid"):
            if hasattr(os, name):
                reject = self.forbidden("direct-os-" + name)
                setattr(os, name, reject)
                if hasattr(native_module, name):
                    setattr(native_module, name, reject)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                     "thread_time_ns", "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall, row: tuple[object, ...]) -> bytes:
    role, relative, expected, size, inode = row
    require(type(role) is str and type(relative) is str
            and type(size) is int and 0 < size <= MAX_OWNER_BYTES
            and type(inode) is int and inode > 0,
            "reject an incomplete authenticated source owner")
    exact_sha(expected, relative)
    path = ROOT + "/" + relative
    require(wall.installed and wall.approved_owner(path),
            "install the deny-default source wall before all owner reads")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == size and before.st_nlink == 1
                and before.st_uid == os.geteuid(),
                "reject exchanged complete frozen owner: " + role)
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            part = os.read(descriptor, min(65536, remaining))
            require(type(part) is bytes and bool(part), "reject a truncated owner: " + role)
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "reject extra authenticated owner bytes")
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject a concurrently changed authenticated source owner: " + role)
        result = b"".join(chunks)
        require(digest(result) == expected, "reject changed frozen owner bytes: " + role)
        return result
    finally:
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, relative: str, expected: str) -> tuple[object, ...]:
    require(relative in (SOURCE, PROTOCOL, CONTRACT), "reject an unrelated live freeze owner")
    exact_sha(expected, relative)
    path = ROOT + "/" + relative
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_dev == DEVICE and identity.st_nlink == 1
                and identity.st_uid == os.geteuid()
                and 0 < identity.st_size <= MAX_OWNER_BYTES,
                "reject an exchanged or incomplete live source-freeze owner: " + role)
    finally:
        os.close(descriptor)
    return role, relative, expected, identity.st_size, identity.st_ino


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    role, path, sha256, size, inode = row
    return {"role": role, "path": path, "sha256": sha256, "bytes": size,
            "device": DEVICE, "inode": inode, "mode": "0600", "nlink": 1}


def validate_original(ledger: dict[str, object], failure: dict[str, object]) -> dict[str, object]:
    require(ledger.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and ledger.get("status") == "PASS"
            and ledger.get("original_case_execution_denominator") == 31237
            and ledger.get("original_suite_count") == 13
            and ledger.get("original_named_private_waiver_count") == 13,
            "preserve the exact complete original 31,237-case P0 ledger")
    oracle = ledger.get("original_oracle")
    phase = ledger.get("phase_gate")
    require(type(oracle) is dict and type(phase) is dict
            and oracle.get("case_execution_denominator") == 31237
            and oracle.get("suite_count") == 13
            and phase.get("status") == "PASS"
            and phase.get("final_holdout_authorized") is False
            and phase.get("performance_oracle_authorized") is False,
            "never merge supplemental cases or authorize a final holdout")
    suites = oracle.get("suites")
    require(type(suites) is list and len(suites) == 13
            and sum(row.get("case_execution_count", -1) for row in suites
                    if type(row) is dict) == 31237,
            "preserve every distinct original suite and its case denominator")
    require(failure.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt"
            and failure.get("status") == "PASS"
            and failure.get("publication_status") == "PASS"
            and failure.get("candidate_status") == "FAIL"
            and failure.get("case_execution_denominator") == 31237
            and failure.get("suite_count") == 13
            and failure.get("semantic_mismatch_count") == 1352
            and failure.get("verified_passing_case_count") == 15877
            and failure.get("holdout") == "NOT OPENED",
            "durable publication must never be mistaken for candidate correctness")
    rows = failure.get("suite_integrity")
    require(type(rows) is list and len(rows) == 13,
            "preserve all thirteen actual original-suite outcomes")
    mismatches = {row.get("suite"): row.get("mismatch_count")
                  for row in rows if type(row) is dict and row.get("mismatch_count")}
    require(mismatches == {"substitution_v2": 240, "shape_v2": 1112},
            "preserve the actual 240 substitution plus 1,112 shape mismatches")
    return {"original_case_execution_denominator": 31237, "original_suite_count": 13,
            "original_named_private_waiver_count": 13,
            "actual_v25_candidate_status": "FAIL",
            "actual_v25_semantic_mismatch_count": 1352,
            "actual_v25_substitution_mismatch_count": 240,
            "actual_v25_shape_mismatch_count": 1112,
            "actual_v25_verified_passing_case_count": 15877}


class PublicSeed:
    """Exact CPython integer-seeded MT19937, implemented without importing random."""

    def __init__(self, seed: int):
        require(type(seed) is int and seed >= 0, "require the exact public integer seed")
        words: list[int] = []
        while seed:
            words.append(seed & 0xFFFFFFFF)
            seed >>= 32
        if not words:
            words.append(0)
        self.state = [19650218]
        for index in range(1, 624):
            prior = self.state[index - 1]
            self.state.append((1812433253 * (prior ^ (prior >> 30)) + index) & 0xFFFFFFFF)
        first = 1
        second = 0
        for _ in range(max(624, len(words))):
            prior = self.state[first - 1]
            self.state[first] = ((self.state[first]
                                  ^ ((prior ^ (prior >> 30)) * 1664525))
                                 + words[second] + second) & 0xFFFFFFFF
            first += 1
            second += 1
            if first >= 624:
                self.state[0] = self.state[623]
                first = 1
            if second >= len(words):
                second = 0
        for _ in range(623):
            prior = self.state[first - 1]
            self.state[first] = ((self.state[first]
                                  ^ ((prior ^ (prior >> 30)) * 1566083941))
                                 - first) & 0xFFFFFFFF
            first += 1
            if first >= 624:
                self.state[0] = self.state[623]
                first = 1
        self.state[0] = 0x80000000
        self.index = 624

    def word(self) -> int:
        if self.index >= 624:
            for index in range(624):
                value = ((self.state[index] & 0x80000000)
                         | (self.state[(index + 1) % 624] & 0x7FFFFFFF))
                self.state[index] = (self.state[(index + 397) % 624]
                                     ^ (value >> 1)
                                     ^ (0x9908B0DF if value & 1 else 0)) & 0xFFFFFFFF
            self.index = 0
        value = self.state[self.index]
        self.index += 1
        value ^= value >> 11
        value ^= (value << 7) & 0x9D2C5680
        value ^= (value << 15) & 0xEFC60000
        value ^= value >> 18
        return value & 0xFFFFFFFF

    def below(self, width: int) -> int:
        require(type(width) is int and width > 0, "require a bounded public random range")
        bits = width.bit_length()
        while True:
            value = self.word() >> (32 - bits)
            if value < width:
                return value


def public_case_metadata(source: bytes, manifest: dict[str, object]) -> list[dict[str, object]]:
    require(manifest.get("schema")
            == "rebar-rust-independent-public-practice-v2-public-protocol-commitment"
            and manifest.get("published_seed") == PUBLISHED_SEED
            and manifest.get("canonical_matrix_sha256") == MATRIX_SHA256
            and manifest.get("case_count") == 10434
            and manifest.get("dataset_count") == 94
            and manifest.get("text_dataset_count") == 47
            and manifest.get("operation_count") == 111
            and manifest.get("source_only_candidate_imports") == 0
            and manifest.get("source_only_benchmark_files_read") == 0,
            "preserve the exact public development matrix without opening raw observations")
    datasets = manifest.get("public_text_datasets")
    operations = manifest.get("public_operations")
    require(type(datasets) is list and len(datasets) == 47
            and datasets.index("text.scanner.scoped_u_override") == 39
            and type(operations) is list and len(operations) == 111
            and operations[33] == "pattern.search.pos_endpos"
            and operations[42] == "pattern.finditer.pos_endpos",
            "derive both public case IDs from the authenticated matrix ordering")
    witness = (
        b'("text.scanner.scoped_u_override", r"(?P<word>(?u:\\w+))(?P<number>\\d*)",\n'
        + '         "café42", ASCII, "scanner-scoped-unicode-override"),'.encode("utf-8")
    )
    require(source.count(witness) == 1 and b"ASCII = 256" in source
            and b'"pattern.search.pos_endpos",' in source
            and b'"pattern.finditer.pos_endpos",' in source
            and b'start = min(seeded.randrange(0, 4), subject_length)' in source
            and b'end = max(start, subject_length - seeded.randrange(0, 3))' in source
            and b'"rust-public-practice.v2." + format(len(cases), "05d")' in source,
            "authenticate the exact witness pattern, subject, flags, seed, and case generator")
    random = PublicSeed(PUBLISHED_SEED)
    wanted = {39 * 111 + 33: "pattern.search.pos_endpos",
              39 * 111 + 42: "pattern.finditer.pos_endpos"}
    found: list[dict[str, object]] = []
    for number in range(max(wanted) + 1):
        first = random.below(4)
        back = random.below(3)
        limit = random.below(4) + 1
        repetitions = random.below(3) + 2
        if number in wanted:
            position = min(first, 6)
            end = max(position, 6 - back)
            require(position == 3 and end == 6,
                    "rederive both witness bounds from the exact CPython public seed")
            found.append({"case": "rust-public-practice.v2." + format(number, "05d"),
                          "dataset": "text.scanner.scoped_u_override",
                          "operation": wanted[number], "domain": "text",
                          "pattern": r"(?P<word>(?u:\w+))(?P<number>\d*)",
                          "subject": "café42", "flags": A, "pos": position,
                          "endpos": end, "subject_length": 6,
                          "limit": limit, "repetitions": repetitions,
                          "expected_match": "é42", "expected_span": [3, 6],
                          "previous_match": "42", "previous_span": [4, 6]})
    require([case["case"] for case in found]
            == ["rust-public-practice.v2.04362", "rust-public-practice.v2.04371"],
            "preserve the two exact independently derived public witness IDs")
    return found


def validate_architectures(evidence: dict[str, bytes]) -> dict[str, object]:
    gate = json_object(evidence["native_public_gate_contract"], "native public gate")
    require(gate.get("schema") == "rebar-owned-rust-native-architecture-public-gate-v2-source-freeze"
            and gate.get("source_sha256") == OWNERS[6][2]
            and gate.get("protocol_sha256") == OWNERS[7][2]
            and gate.get("controller_final_holdout_content_open_count") == 0,
            "authenticate the complete immutable first-party public-architecture gate")
    context = gate.get("public_context")
    matrix = gate.get("public_correctness")
    architectures = gate.get("architectures")
    require(type(context) is dict and context.get("original_case_denominator") == 31237
            and context.get("original_mismatch_count") == 1352
            and context.get("public_correctness_case_count") == 10434
            and context.get("public_profile_case_count") == 416
            and type(matrix) is dict and matrix.get("case_count") == 10434
            and matrix.get("matrix_sha256") == MATRIX_SHA256
            and matrix.get("published_seed") == PUBLISHED_SEED
            and type(architectures) is dict and set(architectures) == {"v26", "v27"},
            "preserve the original denominator and the two exact public architectures")
    records: list[dict[str, object]] = []
    for name, build_role, root_role, public_role, expected_engine in (
        ("v26", "v26_build_publication", "v26_root_provenance", "v26_public_result",
         "fde7b6a6193cd3877753e0f119d29727014b836b2aa2e4c07bdcec0c9f29c102"),
        ("v27", "v27_build_publication", "v27_root_provenance", "v27_public_result",
         "04492763937d0631f162514098ce5d3148e71de21fe7b4cd3f5f876b634f5876"),
    ):
        architecture = architectures.get(name)
        build = json_object(evidence[build_role], name + " first-party native build receipt")
        root = json_object(evidence[root_role], name + " first-party root receipt")
        public = json_object(evidence[public_role], name + " public result receipt")
        require(type(architecture) is dict
                and architecture.get("engine_sha256") == expected_engine
                and architecture.get("publication_sha256") == digest(evidence[build_role])
                and architecture.get("root_receipt_sha256") == digest(evidence[root_role])
                and build.get("status") == "PASS" and build.get("build_status") == "PASS"
                and build.get("family") == "rust" and build.get("actual_compiler_process_count") == 28
                and build.get("candidate_matching") == "NOT RUN"
                and build.get("candidate_qualified") is False
                and root.get("status") == "PASS"
                and root.get("contract_sha256") == architecture.get("contract_sha256")
                and root.get("source_sha256") == architecture.get("source_sha256")
                and root.get("protocol_sha256") == architecture.get("protocol_sha256"),
                "preserve independent exact first-party build provenance: " + name)
        root_directory = root.get("root")
        require(type(root_directory) is dict and root_directory.get("phase_count") == 2
                and root_directory.get("directory_scanned") is False,
                "authenticate private-root metadata without opening a private root: " + name)
        require(public.get("schema")
                == "rebar-owned-rust-native-architecture-public-gate-v2-durable-publication-receipt"
                and public.get("status") == "PASS"
                and public.get("architecture") == name
                and public.get("contract_sha256") == OWNERS[8][2]
                and public.get("protocol_sha256") == OWNERS[7][2]
                and public.get("source_sha256") == OWNERS[6][2]
                and public.get("engine_sha256") == expected_engine
                and public.get("public_10434_case_count") == 10434
                and public.get("public_10434_mismatch_count") == 1145
                and public.get("public_10434_correctness_status") == "FAIL"
                and public.get("candidate_qualified") is False
                and public.get("hidden_cases_read") == 0
                and public.get("hidden_case_files_generated") == 0,
                "never report the published 1,145 public mismatches as candidate correctness")
        rows = public.get("artifacts")
        require(type(rows) is list and len(rows) >= 3 and type(rows[2]) is dict
                and rows[2].get("sha256")
                    == "7fc4c743e35bbe4f57ed0e3a872b9a9646b2603feedb9ae2c24421afed5430aa"
                and type(rows[2].get("path")) is str
                and rows[2]["path"].endswith("public-10434-correctness.raw.json"),
                "authenticate public raw-ledger metadata without opening its bytes")
        records.append({"architecture": name, "engine_sha256": expected_engine,
                        "build_publication_sha256": digest(evidence[build_role]),
                        "root_provenance_sha256": digest(evidence[root_role]),
                        "public_result_sha256": digest(evidence[public_role]),
                        "public_case_count": 10434,
                        "public_mismatch_count": 1145,
                        "public_correctness_status": "FAIL",
                        "published_raw_ledger_sha256_metadata_only": rows[2]["sha256"],
                        "raw_ledger_bytes_opened": 0,
                        "actual_build_compiler_process_count_historical": 28})
    return {"historical_architectures": records,
            "historical_distinct_engine_count": len({item["engine_sha256"] for item in records}),
            "historical_public_mismatch_count_each": 1145,
            "historical_raw_public_ledger_sha256":
                "7fc4c743e35bbe4f57ed0e3a872b9a9646b2603feedb9ae2c24421afed5430aa",
            "historical_raw_public_ledger_content_open_count": 0}


def derive_sources(evidence: dict[str, bytes]) -> tuple[bytes, dict[str, object]]:
    canonical_engine = evidence["canonical_engine"]
    anchor = evidence["mandatory_anchor_engine"]
    combined = evidence["combined_engine"]
    require(canonical_engine.count(OLD_GUARD) == 1 and anchor.count(OLD_GUARD) == 1
            and combined.count(OLD_GUARD) == 1 and NEW_GUARD not in canonical_engine
            and NEW_GUARD not in anchor and NEW_GUARD not in combined,
            "locate exactly one unchanged unsafe start-set guard in all three lineages")
    required = (
        b"fn has_scoped_category_prefix(node: &Expr, global_flags: u32) -> bool {",
        b"Expr::Cat(_, flags) | Expr::Class(_, _, flags) => {",
        b"(*flags ^ global_flags) & (A | L | BYTE) != 0",
        b"let prefix_flags = (*flags & !(A | L | BYTE)) | (global_flags & (A | L | BYTE));",
        b"let start_set = starts.as_ref().map(search::StartSet::new);",
    )
    require(all(marker in canonical_engine and marker in anchor and marker in combined
                for marker in required),
            "prove lexical category/class flags already exist and the stale start set consumes them")
    corrected = canonical_engine.replace(OLD_GUARD, NEW_GUARD, 1)
    corrected_anchor = anchor.replace(OLD_GUARD, NEW_GUARD, 1)
    corrected_combined = combined.replace(OLD_GUARD, NEW_GUARD, 1)
    require(digest(corrected) == CORRECTED_SHA256 and len(corrected) == CORRECTED_BYTES
            and digest(corrected_anchor) == ANCHOR_CORRECTED_SHA256
            and len(corrected_anchor) == ANCHOR_CORRECTED_BYTES
            and digest(corrected_combined) == COMBINED_CORRECTED_SHA256
            and len(corrected_combined) == COMBINED_CORRECTED_BYTES,
            "independently predict one canonical correction and its two exact compositions")
    require(corrected.replace(NEW_GUARD, OLD_GUARD, 1) == canonical_engine
            and corrected_anchor.replace(NEW_GUARD, OLD_GUARD, 1) == anchor
            and corrected_combined.replace(NEW_GUARD, OLD_GUARD, 1) == combined,
            "prove each one-site source correction is exactly reversible")
    for original, transformed in ((canonical_engine, corrected), (anchor, corrected_anchor),
                                  (combined, corrected_combined)):
        prefix, suffix = original.split(OLD_GUARD)
        require(transformed == prefix + NEW_GUARD + suffix,
                "preserve every parser, scanner, VM, allocator, and anchor byte")
        forbidden = (b"extern crate regex", b"use regex::Regex", b"pcre2", b"oniguruma",
                     b"std::process::Command", b"dlopen(", b"PyImport_ImportModule")
        require(not any(value in NEW_GUARD for value in forbidden),
                "reject delegation, external regex dependencies, or candidate process execution")
    manifest = evidence["cargo_manifest"]
    lock = evidence["cargo_lock"]
    require(manifest.count(b"[package]") == 1 and b"[dependencies]" not in manifest
            and b"regex" not in manifest.lower() and lock.count(b"[[package]]") == 1,
            "preserve one first-party Cargo package and zero external regex packages")
    combined_contract = json_object(evidence["combined_transformer_contract"],
                                    "combined first-party frozen source")
    application = json_object(evidence["combined_materialization"],
                              "combined first-party materialization")
    require(combined_contract.get("schema")
            == "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
            and combined_contract.get("version") == 2
            and combined_contract.get("source", {}).get("sha256") == OWNERS[15][2]
            and combined_contract.get("protocol", {}).get("sha256") == OWNERS[16][2]
            and combined_contract.get("derived", {}).get("engine", {}).get("sha256")
                == COMBINED_SHA256
            and combined_contract.get("derived", {}).get("search", {}).get("sha256")
                == COMBINED_SEARCH_SHA256
            and application.get("status") == "APPLIED"
            and application.get("source_sha256") == OWNERS[15][2]
            and application.get("protocol_sha256") == OWNERS[16][2]
            and application.get("contract_sha256") == OWNERS[17][2]
            and application.get("created", {}).get("engine", {}).get("sha256")
                == COMBINED_SHA256
            and application.get("created", {}).get("search", {}).get("sha256")
                == COMBINED_SEARCH_SHA256,
            "authenticate the exact already materialized first-party combined lineage")
    anchor_marker = b"fn mandatory_anchor_search(root: &Expr) -> Option<search::AnchorPlan> {"
    require(anchor_marker in anchor and anchor_marker in combined
            and anchor.count(anchor_marker) == corrected_anchor.count(anchor_marker) == 1
            and combined.count(anchor_marker) == corrected_combined.count(anchor_marker) == 1
            and evidence["combined_search"] == evidence["combined_search"],
            "preserve the independent mandatory-anchor fast path and unchanged search source")
    return corrected, {
        "source_replacement_count": 1,
        "source_delta_bytes": len(NEW_GUARD) - len(OLD_GUARD),
        "replacement_exactly_reversible": True,
        "canonical_parent": {"path": OWNERS[21][1], "sha256": CANONICAL_SHA256,
                             "bytes": CANONICAL_BYTES},
        "standalone_corrected": {"path": TARGET, "sha256": CORRECTED_SHA256,
                                 "bytes": CORRECTED_BYTES,
                                 "materialization_status": "NOT MATERIALIZED"},
        "mandatory_anchor_parent": {"path": OWNERS[22][1], "sha256": ANCHOR_SHA256,
                                    "bytes": 189369},
        "mandatory_anchor_corrected_composition": {
            "sha256": ANCHOR_CORRECTED_SHA256, "bytes": ANCHOR_CORRECTED_BYTES,
            "materialization_status": "NOT MATERIALIZED"},
        "combined_parent": {"path": OWNERS[23][1], "sha256": COMBINED_SHA256,
                            "bytes": 189423},
        "combined_corrected_composition": {
            "sha256": COMBINED_CORRECTED_SHA256, "bytes": COMBINED_CORRECTED_BYTES,
            "materialization_status": "NOT MATERIALIZED"},
        "combined_search_preserved": {"path": OWNERS[24][1],
                                     "sha256": COMBINED_SEARCH_SHA256, "bytes": 24305},
        "mandatory_anchor_accelerator_preserved": True,
        "compiler_allocation_fastpath_preserved_when_composed": True,
        "external_rust_dependency_count": 0,
        "candidate_or_external_matcher_import_count": 0,
    }


def locale_flags(flags: int) -> bool:
    return flags & (L | BYTE) == L | BYTE


def nullable(node: tuple) -> bool:
    tag = node[0]
    if tag in ("anchor", "empty"):
        return True
    if tag in ("group", "atomic"):
        return nullable(node[1])
    if tag == "repeat":
        return node[2] == 0 or nullable(node[1])
    if tag == "seq":
        return all(nullable(child) for child in node[1])
    if tag == "alt":
        return any(nullable(child) for child in node[1])
    if tag == "cond":
        return nullable(node[1]) or nullable(node[2])
    return False


def scoped_prefix(node: tuple, global_flags: int) -> bool:
    tag = node[0]
    if tag in ("cat", "class"):
        return (node[-1] ^ global_flags) & (A | L | BYTE) != 0
    if tag in ("group", "atomic", "repeat"):
        return scoped_prefix(node[1], global_flags)
    if tag == "seq":
        for child in node[1]:
            if scoped_prefix(child, global_flags):
                return True
            if not nullable(child):
                break
        return False
    if tag == "alt":
        return any(scoped_prefix(child, global_flags) for child in node[1])
    if tag == "cond":
        return scoped_prefix(node[1], global_flags) or scoped_prefix(node[2], global_flags)
    return False


def locale_sensitive(node: tuple) -> bool:
    tag = node[0]
    if tag in ("cat", "class", "lit", "dot", "anchor"):
        return locale_flags(node[-1])
    if tag in ("group", "atomic", "repeat"):
        return locale_sensitive(node[1])
    if tag in ("seq", "alt"):
        return any(locale_sensitive(child) for child in node[1])
    if tag == "cond":
        return locale_sensitive(node[1]) or locale_sensitive(node[2])
    return False


def category(code: str, value: int, flags: int) -> bool:
    character = chr(value)
    ascii_only = bool(flags & (A | L | BYTE))
    if code.lower() == "w":
        matched = (value < 128 and (character.isalnum() or character == "_")) if ascii_only \
            else character.isalnum() or character == "_"
    elif code.lower() == "d":
        matched = (48 <= value <= 57) if ascii_only else character.isdecimal()
    elif code.lower() == "s":
        matched = (character in " \t\n\r\v\f") if ascii_only else character.isspace()
    else:
        raise FreezeError("reject an unknown synthetic first-party category")
    return not matched if code.isupper() else matched


def literal_matches(expected: int, value: int, flags: int) -> bool:
    if expected == value:
        return True
    if not flags & I:
        return False
    if flags & (A | L | BYTE):
        return expected < 128 and value < 128 and chr(expected).lower() == chr(value).lower()
    return chr(expected).lower() == chr(value).lower()


def class_matches(members: tuple, negative: bool, value: int, flags: int) -> bool:
    matched = False
    for member in members:
        if member[0] == "cat":
            matched |= category(member[1], value, flags)
        elif member[0] == "lit":
            matched |= literal_matches(member[1], value, flags)
        elif member[0] == "range":
            matched |= member[1] <= value <= member[2]
        else:
            raise FreezeError("reject an unknown synthetic first-party class member")
    return not matched if negative else matched


def add_starts(node: tuple, starts: set[int], global_flags: int) -> tuple[bool, bool]:
    tag = node[0]
    if tag == "cat":
        code, flags = node[1], node[2]
        flags = (flags & ~(A | L | BYTE)) | (global_flags & (A | L | BYTE))
        starts.update(value for value in range(256) if category(code, value, flags))
        return False, True
    if tag == "class":
        members, negative, flags = node[1], node[2], node[3]
        if ((flags ^ global_flags) & (A | L | BYTE)
                and flags & I and any(item[0] == "lit" for item in members)):
            return False, False
        flags = (flags & ~(A | L | BYTE)) | (global_flags & (A | L | BYTE))
        starts.update(value for value in range(256)
                      if class_matches(members, negative, value, flags))
        return False, True
    if tag == "lit":
        expected, flags = node[1], node[2]
        starts.update(value for value in range(256) if literal_matches(expected, value, flags))
        return False, True
    if tag == "dot":
        starts.update(range(256))
        return False, True
    if tag in ("anchor", "empty"):
        return True, True
    if tag in ("group", "atomic"):
        return add_starts(node[1], starts, global_flags)
    if tag == "repeat":
        empty, known = add_starts(node[1], starts, global_flags)
        return node[2] == 0 or empty, known
    if tag == "seq":
        for child in node[1]:
            empty, known = add_starts(child, starts, global_flags)
            if not known:
                return False, False
            if not empty:
                return False, True
        return True, True
    if tag == "alt":
        if any(scoped_prefix(child, global_flags) for child in node[1]):
            return False, False
        empty = False
        for child in node[1]:
            child_empty, known = add_starts(child, starts, global_flags)
            if not known:
                return False, False
            empty |= child_empty
        return empty, True
    if tag == "cond":
        yes_empty, yes_known = add_starts(node[1], starts, global_flags)
        no_empty, no_known = add_starts(node[2], starts, global_flags)
        return yes_empty or no_empty, yes_known and no_known
    raise FreezeError("reject an unknown synthetic first-party expression")


def start_table(node: tuple, global_flags: int, corrected: bool) -> set[int] | None:
    if locale_flags(global_flags) or locale_sensitive(node):
        return None
    if corrected and scoped_prefix(node, global_flags):
        return None
    starts: set[int] = set()
    empty, known = add_starts(node, starts, global_flags)
    return starts if known and not empty else None


def leading_atom(node: tuple) -> tuple | None:
    tag = node[0]
    if tag in ("group", "atomic", "repeat"):
        return leading_atom(node[1])
    if tag == "seq":
        for child in node[1]:
            result = leading_atom(child)
            if result is not None:
                return result
            if not nullable(child):
                return None
        return None
    return node if tag in ("cat", "class", "lit", "dot") else None


def prefilter_allows(node: tuple, global_flags: int, value: int,
                     starts: set[int] | None) -> bool:
    if starts is None:
        return True
    if value < 256:
        return value in starts
    first = leading_atom(node)
    if first is None:
        return True
    if first[0] == "cat":
        flags = (first[2] & ~(A | L | BYTE)) | (global_flags & (A | L | BYTE))
        return category(first[1], value, flags)
    if first[0] == "class":
        flags = (first[3] & ~(A | L | BYTE)) | (global_flags & (A | L | BYTE))
        return class_matches(first[1], first[2], value, flags)
    if first[0] == "lit":
        return literal_matches(first[1], value, first[2])
    return True


def matches(node: tuple, subject: tuple[int, ...], position: int, end: int,
            depth: int = 0) -> list[int]:
    require(depth <= 32, "reject unbounded synthetic expression recursion")
    tag = node[0]
    if tag in ("anchor", "empty"):
        return [position]
    if tag == "cat":
        return [position + 1] if position < end and category(node[1], subject[position], node[2]) else []
    if tag == "class":
        return [position + 1] if (position < end
                                  and class_matches(node[1], node[2], subject[position], node[3])) else []
    if tag == "lit":
        return [position + 1] if (position < end
                                  and literal_matches(node[1], subject[position], node[2])) else []
    if tag == "dot":
        return [position + 1] if position < end else []
    if tag in ("group", "atomic"):
        return matches(node[1], subject, position, end, depth + 1)
    if tag == "seq":
        positions = [position]
        for child in node[1]:
            positions = [finish for start in positions
                         for finish in matches(child, subject, start, end, depth + 1)]
            if not positions:
                break
        return positions
    if tag == "alt":
        return [finish for child in node[1]
                for finish in matches(child, subject, position, end, depth + 1)]
    if tag == "cond":
        return (matches(node[1], subject, position, end, depth + 1)
                + matches(node[2], subject, position, end, depth + 1))
    if tag == "repeat":
        child, minimum, maximum = node[1], node[2], node[3]
        limit = min(maximum, end - position + 1)
        buckets: list[list[int]] = [[position]]
        for _ in range(limit):
            following = [finish for start in buckets[-1]
                         for finish in matches(child, subject, start, end, depth + 1)
                         if finish != start]
            if not following:
                break
            buckets.append(following)
        return [finish for count in range(len(buckets) - 1, minimum - 1, -1)
                for finish in buckets[count]]
    raise FreezeError("reject an unknown synthetic first-party match expression")


def search(node: tuple, global_flags: int, subject: tuple[int, ...], first: int,
           last: int, policy: str) -> tuple[int, int] | None:
    table = None if policy == "oracle" else start_table(node, global_flags, policy == "corrected")
    for position in range(first, last + 1):
        if position < last and not prefilter_allows(node, global_flags, subject[position], table):
            continue
        ends = matches(node, subject, position, last)
        if ends:
            return position, ends[0]
    return None


def synthetic_semantics() -> dict[str, object]:
    scoped_word = ("cat", "w", U)
    scoped_digit = ("cat", "d", U)
    scoped_space = ("cat", "s", U)
    scoped_class = ("class", (("cat", "w"),), False, U)
    scoped_negative_class = ("class", (("cat", "W"),), True, U)
    ascii_word = ("cat", "w", A)
    plain_word = ("cat", "w", 0)
    plain_digit = ("cat", "d", 0)
    literal_a = ("lit", ord("a"), 0)
    literal_z = ("lit", ord("z"), 0)
    witness = ("seq", (("group", ("repeat", scoped_word, 1, 8)),
                        ("group", ("repeat", ("cat", "d", A), 0, 8))))
    patterns: list[tuple[str, tuple, int]] = [
        ("text-global-ascii-scoped-unicode-category", scoped_word, A),
        ("text-global-ascii-scoped-unicode-digit", scoped_digit, A),
        ("text-global-ascii-scoped-unicode-space", scoped_space, A),
        ("text-global-ascii-scoped-unicode-group-repeat", witness, A),
        ("text-global-ascii-scoped-unicode-atomic", ("atomic", scoped_word), A),
        ("text-global-ascii-scoped-unicode-class", scoped_class, A),
        ("text-global-ascii-scoped-unicode-negative-class", scoped_negative_class, A),
        ("text-global-ascii-scoped-unicode-nullable-prefix",
         ("seq", (("repeat", literal_a, 0, 2), ("group", scoped_word))), A),
        ("text-global-ascii-scoped-unicode-anchor-prefix",
         ("seq", (("anchor", A), ("group", scoped_word))), A),
        ("text-global-ascii-scoped-unicode-condition",
         ("cond", scoped_word, scoped_class), A),
        ("text-global-ascii-scoped-unicode-alt-preexisting-bailout",
         ("alt", (scoped_word, literal_z)), A),
        ("text-global-ascii-scoped-unicode-nullable-root",
         ("repeat", scoped_word, 0, 3), A),
        ("text-global-unicode-scoped-ascii-category", ascii_word, 0),
        ("text-global-unicode-scoped-ascii-class",
         ("class", (("cat", "w"),), False, A), 0),
        ("text-global-unicode-scoped-ascii-group-repeat",
         ("group", ("repeat", ascii_word, 1, 4)), 0),
        ("text-global-unicode-unchanged-word", plain_word, 0),
        ("text-global-unicode-unchanged-digit", plain_digit, 0),
        ("text-global-ascii-unchanged-word", ascii_word, A),
        ("text-global-ascii-unchanged-class",
         ("class", (("cat", "w"),), False, A), A),
        ("text-unrelated-literal", literal_a, A),
        ("text-unrelated-literal-scoped-after-required-prefix",
         ("seq", (literal_a, scoped_word)), A),
        ("text-unrelated-ordered-alternatives",
         ("alt", (literal_a, literal_z)), 0),
        ("text-unrelated-ignorecase", ("lit", ord("K"), I), I),
        ("bytes-ordinary-category", ("cat", "w", BYTE), BYTE),
        ("bytes-scoped-ascii-category", ("cat", "w", BYTE | A), BYTE),
        ("bytes-scoped-ascii-class",
         ("class", (("cat", "w"),), False, BYTE | A), BYTE),
        ("bytes-global-locale-guard", ("cat", "w", BYTE | L), BYTE | L),
        ("bytes-nested-locale-guard",
         ("seq", (("lit", ord("a"), BYTE), ("cat", "w", BYTE | L))), BYTE),
        ("text-nested-scoped-class-repeat",
         ("group", ("atomic", ("repeat", scoped_class, 1, 4))), A),
        ("text-mixed-scoped-digit-suffix",
         ("seq", (("group", scoped_word), ("cat", "d", A))), A),
        ("text-scoped-category-with-fixed-mandatory-anchor",
         ("seq", (scoped_word, literal_a, literal_z)), A),
    ]
    fixed_subjects = [(), tuple(map(ord, "café42")), tuple(map(ord, "é42")),
                      tuple(map(ord, "aé2")), tuple(map(ord, "__42")),
                      tuple(map(ord, " Ω9")), (0x1F600, ord("a"), ord("2")),
                      (0x0662, ord("a"), ord("9")),
                      (0x2003, ord("a"), ord("2")),
                      (0x0301, ord("e"), ord("2")),
                      (0, 255, 128, ord("a")), tuple(map(ord, "aaaaaz")),
                      tuple(map(ord, "ZaZ")), tuple(map(ord, "💡é_2"))]
    alphabet = (ord("a"), ord("Z"), ord("2"), ord("_"), ord("é"), 0x03A9,
                0x0662, 0x2003, 0x1F600, ord("-"))
    generated: list[tuple[int, ...]] = []
    state = 0x52454241525F5531
    for index in range(88):
        length = index % 6 + 1
        values: list[int] = []
        for _ in range(length):
            state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            values.append(alphabet[(state >> 33) % len(alphabet)])
        generated.append(tuple(values))
    subjects = fixed_subjects + generated
    checks = 0
    repaired = 0
    unchanged = 0
    scoped_checks = 0
    byte_checks = 0
    locale_checks = 0
    class_checks = 0
    astral_checks = 0
    optimizer_preserved = 0
    scoped_optimizer_disabled = 0
    for family, node, global_flags in patterns:
        scoped = scoped_prefix(node, global_flags)
        old_table = start_table(node, global_flags, False)
        new_table = start_table(node, global_flags, True)
        if scoped:
            require(new_table is None,
                    "disable only the unsafe leading scoped-category/class accelerator")
            scoped_optimizer_disabled += 1
        else:
            require(new_table == old_table,
                    "preserve every unrelated first-byte accelerator exactly")
            if new_table is not None:
                optimizer_preserved += 1
        if locale_flags(global_flags) or locale_sensitive(node):
            require(old_table is None and new_table is None,
                    "preserve the existing bytes/locale safety bailout")
        for values in subjects:
            for first in range(len(values) + 1):
                for last in range(first, len(values) + 1):
                    expected = search(node, global_flags, values, first, last, "oracle")
                    previous = search(node, global_flags, values, first, last, "legacy")
                    corrected = search(node, global_flags, values, first, last, "corrected")
                    require(corrected == expected,
                            "corrected first-party scoped prefix changed VM semantics: " + family)
                    if previous != expected:
                        require(scoped,
                                "an unrelated existing start-set accelerator changed semantics")
                        repaired += 1
                    else:
                        unchanged += 1
                    checks += 1
                    scoped_checks += int(scoped)
                    byte_checks += int(bool(global_flags & BYTE))
                    locale_checks += int(locale_flags(global_flags) or locale_sensitive(node))
                    class_checks += int("class" in family)
                    astral_checks += int(any(value > 0xFFFF for value in values))
    witness_subject = tuple(map(ord, "café42"))
    require(search(witness, A, witness_subject, 3, 6, "oracle") == (3, 6)
            and search(witness, A, witness_subject, 3, 6, "legacy") == (4, 6)
            and search(witness, A, witness_subject, 3, 6, "corrected") == (3, 6)
            and start_table(witness, A, False) is not None
            and start_table(witness, A, True) is None,
            "reproduce and correct the exact public café42 scoped-Unicode witness")
    safe_prefix = ("seq", (("lit", ord("a"), 0), scoped_word))
    require(not scoped_prefix(safe_prefix, A)
            and start_table(safe_prefix, A, True) == start_table(safe_prefix, A, False),
            "retain the unrelated mandatory literal first-byte accelerator")
    require(repaired > 0 and unchanged > 0 and scoped_checks > 0 and byte_checks > 0
            and locale_checks > 0 and class_checks > 0 and astral_checks > 0
            and optimizer_preserved > 0 and scoped_optimizer_disabled > 0,
            "require exhaustive bounded category, class, flags, bytes, and Unicode coverage")
    return {"pattern_family_count": len(patterns), "subject_family_count": len(subjects),
            "bounded_differential_case_count": checks,
            "previously_unsound_cases_repaired": repaired,
            "previously_correct_cases_preserved": unchanged,
            "scoped_category_or_class_case_count": scoped_checks,
            "bytes_case_count": byte_checks,
            "locale_bailout_case_count": locale_checks,
            "class_prefix_case_count": class_checks,
            "multibyte_or_astral_case_count": astral_checks,
            "unchanged_first_byte_optimizer_pattern_count": optimizer_preserved,
            "unsafe_scoped_optimizer_pattern_count_disabled": scoped_optimizer_disabled,
            "exact_public_witness_expected_span": [3, 6],
            "exact_public_witness_previous_span": [4, 6],
            "exact_public_witness_corrected_span": [3, 6],
            "exact_public_witness_start_table_disabled": True,
            "independent_mandatory_anchor_search_preserved": True,
            "candidate_executed": False, "external_matcher_imported": False}


def make_contract(source_row: tuple[object, ...], protocol_row: tuple[object, ...],
                  original: dict[str, object], architecture: dict[str, object],
                  cases: list[dict[str, object]], transformation: dict[str, object],
                  synthetic: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA, "version": 1, "family": "rust", "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; SCOPED-UNICODE VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
        "source": owner_document(source_row), "protocol": owner_document(protocol_row),
        "authenticated_previous_owner_count": len(OWNERS),
        "authenticated_previous_owners": [owner_document(row) for row in OWNERS],
        "authenticated_original_ledger": original,
        "authenticated_public_architecture_history": architecture,
        "public_matrix": {"case_count": 10434, "dataset_count": 94,
                          "operation_count": 111, "seed": PUBLISHED_SEED,
                          "matrix_sha256": MATRIX_SHA256,
                          "raw_public_observation_content_open_count": 0},
        "targeted_residual_public_mismatches": {"case_count": 2,
                                                "cases": cases,
                                                "source_case_derivation_only": True,
                                                "raw_case_bytes_opened": 0},
        "root_cause": {
            "component": "FIRST-PARTY RUST START-SET / WIDE PREFIX ACCELERATOR",
            "global_flags": A, "scoped_lexical_flags": U,
            "incorrect_prefix_flag_expression":
                "(*flags & !(A | L | BYTE)) | (global_flags & (A | L | BYTE))",
            "existing_scoped_prefix_detector": "has_scoped_category_prefix",
            "old_guard": OLD_GUARD.decode("utf-8"),
            "corrected_guard": NEW_GUARD.decode("utf-8"),
            "vm_lexical_category_and_class_flags_preserved": True,
            "stale_first_byte_and_wide_prefix_filters_disabled_together": True,
            "existing_locale_byte_guard_preserved": True,
            "independent_mandatory_anchor_accelerator_preserved": True,
        },
        "first_party_source_correction": transformation,
        "synthetic_differential_semantics": synthetic,
        "physical_source_wall": {
            "policy": "CONTINUOUS DENY DEFAULT; PINNED OWNER DESCRIPTORS",
            "installed_before_owner_reads": True,
            "candidate_imports_permitted": 0,
            "candidate_processes_permitted": 0,
            "native_binary_or_library_opens_permitted": 0,
            "raw_benchmark_file_opens_permitted": 0,
            "archive_opens_permitted": 0,
            "private_root_opens_permitted": 0,
            "final_case_or_holdout_opens_permitted": 0,
            "final_holdout_metadata_probes_permitted": 0,
            "clock_or_timer_samples_permitted": 0,
            "source_mode_filesystem_writes_permitted": 0,
            "dynamic_code_compilation_permitted": 0,
            "underlying_posix_aliases_guarded": True,
            "root_output_parent_inode": PARENT_INODE,
            "root_output_directory_mode": "0700",
            "root_output_file_mode": "0600",
            "root_output_file_policy": "O_CREAT|O_EXCL|O_NOFOLLOW",
            "full_linux_o_tmpfile_composite_rejected": True,
            "ordinary_linux_o_directory_allowed_only_during_root_apply": True,
            "continuous_wall_remains_active_during_root_publication": True,
        },
        "source_only_effects": {
            "candidate_imports": 0, "candidate_workers_started": 0,
            "candidate_executions": 0, "compiler_processes_started": 0,
            "native_libraries_loaded": 0, "native_binary_files_opened": 0,
            "raw_benchmark_files_opened": 0, "archives_opened": 0,
            "private_roots_opened": 0, "final_holdout_files_opened": 0,
            "final_holdout_metadata_probes": 0, "hidden_cases_opened": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "workspace_mutations": 0, "candidate_correctness": NOT_MEASURED,
            "candidate_performance": NOT_MEASURED, "candidate_memory": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED, "qualified_candidate_count": 0,
            "winner_selected": False,
        },
        "original_case_execution_denominator": 31237,
        "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
        "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
        "candidate_qualified": False, "winner_selected": False,
        "holdout": "NOT OPENED",
    }


def validate_runtime() -> None:
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and sys.flags.no_site == 1,
            "use the exact pinned CPython 3.14.6 with -I -B -S")
    clean_imports()


def arguments(values: list[str]) -> tuple[str, dict[str, str], frozenset[str]]:
    require(bool(values), "select exactly one explicit source-freeze action")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject an unknown, combined, or missing source-freeze action")
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
                "reject unknown, duplicated, or missing immutable authority")
        pins[name] = (exact_sha(values[index + 1], name) if name.endswith("sha256")
                      else exact_commit(values[index + 1], name))
        index += 2
    if mode == "--render-contract":
        require(set(pins) == {"--source-sha256", "--protocol-sha256"} and not flags,
                "rendering requires only two independently pinned source owners")
    elif mode in ("--verify-source", "--self-test"):
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
                and not flags, "source-only gates require exactly three immutable owner pins")
    else:
        require(set(pins) == {"--source-sha256", "--protocol-sha256", "--contract-sha256",
                              "--frozen-commit", "--pushed-commit"}
                and flags == {"--root-authorized", "--frozen-committed-pushed"}
                and pins["--frozen-commit"] == pins["--pushed-commit"],
                "only root may apply an exactly committed and already pushed source freeze")
    return mode, pins, frozenset(flags)


def load_context(wall: SourceWall, mode: str, pins: dict[str, str]) -> dict[str, object]:
    source_row = live_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = live_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source_row)
    read_owner(wall, protocol_row)
    contract_row = None if mode == "--render-contract" else live_owner(
        wall, "contract", CONTRACT, pins["--contract-sha256"])
    evidence = {row[0]: read_owner(wall, row) for row in OWNERS}
    original = validate_original(json_object(evidence["original_p0_ledger"], "original P0"),
                                 json_object(evidence["actual_v25_original_failure"],
                                             "actual original V25 failure"))
    manifest = json_object(evidence["public_matrix_contract"], "public matrix contract")
    cases = public_case_metadata(evidence["public_matrix_source"], manifest)
    history = validate_architectures(evidence)
    corrected, transformation = derive_sources(evidence)
    synthetic = synthetic_semantics()
    contract = make_contract(source_row, protocol_row, original, history,
                             cases, transformation, synthetic)
    if contract_row is not None:
        complete = read_owner(wall, contract_row)
        require(complete == document(contract)
                and json_object(complete, "complete scoped-Unicode freeze") == contract,
                "reject omitted, changed, reordered, or incomplete source-freeze obligations")
    require(not wall.owner_fds and wall.parent_fd is None and wall.child_fd is None
            and wall.output_fd is None and not wall.output_opened,
            "close every owned descriptor without opening candidate, raw, archive, or final data")
    clean_imports()
    return {"contract": contract, "corrected": corrected, "synthetic": synthetic,
            "cases": cases, "history": history}


def expect_rejected(wall: SourceWall, name: str, callback) -> str:
    before = sum(wall.blocked.values())
    try:
        callback()
    except (FreezeError, OSError, TypeError, ValueError, UnicodeError, IndexError):
        require(sum(wall.blocked.values()) > before,
                "hostile physical control never reached the source-only wall: " + name)
        return name
    raise FreezeError("hostile source-only control escaped the physical wall: " + name)


def hostile_self_test(wall: SourceWall, state: dict[str, object]) -> dict[str, object]:
    own = ROOT + "/" + SOURCE
    native = sys.modules["posix"]

    def forged_authority() -> None:
        old = wall.apply
        wall.apply = not old
        try:
            sys.audit("os.exec", "/bin/true", (), None)
        finally:
            wall.apply = old

    attempts = [
        expect_rejected(wall, "builtins-open", lambda: builtins.open(own, "rb")),
        expect_rejected(wall, "io-open", lambda: io.open(own, "rb")),
        expect_rejected(wall, "_io-open", lambda: _io.open(own, "rb")),
        expect_rejected(wall, "owner-missing-nofollow", lambda: os.open(own, os.O_RDONLY)),
        expect_rejected(wall, "owner-write", lambda: os.open(own, os.O_WRONLY)),
        expect_rejected(wall, "unsafe-owner-alias",
                        lambda: os.open(ROOT + "/tools/../" + SOURCE,
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "raw-public-ledger",
                        lambda: os.open(ROOT + "/experiments/rust_native_architecture_public_v2/"
                                        "v26-anchor-public-run-001/public-10434-correctness.raw.json",
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "native-object",
                        lambda: os.open(ROOT + "/candidates/_rust_engine.so",
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "compressed-archive",
                        lambda: os.open(ROOT + "/oracle/phase2/evidence/private.json.gz",
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "final-holdout",
                        lambda: os.open(ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json",
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "final-holdout-metadata",
                        lambda: os.lstat(ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json")),
        expect_rejected(wall, "private-build-root",
                        lambda: os.open("/tmp/rebar-phase2-native-build-v9-rust-b3xca14k",
                                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "variants-parent-before-apply",
                        lambda: os.open(ROOT + "/" + PARENT,
                                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "linux-full-composite-tmpfile",
                        lambda: os.open(ROOT + "/" + PARENT,
                                        os.O_TMPFILE | os.O_RDWR | os.O_NOFOLLOW)),
        expect_rejected(wall, "target-before-apply",
                        lambda: os.open(ROOT + "/" + TARGET,
                                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        expect_rejected(wall, "inherited-read", lambda: os.read(0, 1)),
        expect_rejected(wall, "inherited-write", lambda: os.write(1, b"reject")),
        expect_rejected(wall, "inherited-fstat", lambda: os.fstat(0)),
        expect_rejected(wall, "inherited-fsync", lambda: os.fsync(1)),
        expect_rejected(wall, "inherited-close", lambda: os.close(0)),
        expect_rejected(wall, "native-posix-read", lambda: native.read(0, 1)),
        expect_rejected(wall, "native-posix-write", lambda: native.write(1, b"reject")),
        expect_rejected(wall, "native-posix-stat", lambda: native.fstat(0)),
        expect_rejected(wall, "candidate-process", lambda: os.system("true")),
        expect_rejected(wall, "dynamic-compile", lambda: compile(b"1", "foreign.py", "exec")),
        expect_rejected(wall, "dynamic-execution", lambda: exec("1")),
        expect_rejected(wall, "matcher-import", lambda: __import__("re")),
        expect_rejected(wall, "native-loader-import", lambda: __import__("ctypes")),
        expect_rejected(wall, "seconds-clock", lambda: time.time()),
        expect_rejected(wall, "nanosecond-clock", lambda: time.perf_counter_ns()),
        expect_rejected(wall, "forged-root-authority", forged_authority),
    ]
    for name in ("dup", "pread", "pwrite", "readv", "writev", "sendfile", "stat",
                 "listdir", "truncate", "execv", "spawnv", "kill", "chdir"):
        if hasattr(os, name):
            function = getattr(os, name)
            attempts.append(expect_rejected(wall, "descriptor-alias-" + name,
                                            lambda actual=function: actual()))
    malformed = (b'{"duplicate":1,"duplicate":2}', b'{"zero":01}',
                 b'{"nan":NaN}', b'{"fraction":1.}', b'{"trailing":1}{}',
                 b'{"surrogate":"\\ud800"}', b'{"escape":"\\q"}', b"[]")
    rejected = 0
    for value in malformed:
        try:
            json_object(value, "hostile public JSON")
        except (FreezeError, UnicodeError, ValueError, IndexError):
            rejected += 1
        else:
            raise FreezeError("hostile duplicate, nonfinite, or incomplete JSON escaped")
    require(len(attempts) >= 40 and rejected == len(malformed)
            and state["contract"]["source_only_effects"]["workspace_mutations"] == 0,
            "complete all physical, evidence, and filesystem isolation controls")
    clean_imports()
    return {"physical_hostile_control_count": len(attempts),
            "physical_hostile_controls": attempts,
            "malformed_public_json_control_count": rejected,
            "physically_blocked_categories": dict(wall.blocked),
            "underlying_posix_aliases_guarded": True,
            "raw_public_ledger_open_count": 0,
            "final_holdout_content_open_count": 0,
            "final_holdout_metadata_probe_count": 0,
            "candidate_process_count": 0,
            "clock_sample_count": 0,
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
            "require the complete pushed root freeze before the first source mutation")
    wall.expected = corrected
    wall.stage = "ready"
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open(ROOT + "/" + PARENT, directory_flags)
    parent_identity = os.fstat(parent)
    require(stat.S_ISDIR(parent_identity.st_mode)
            and stat.S_IMODE(parent_identity.st_mode) == 0o700
            and parent_identity.st_dev == DEVICE and parent_identity.st_ino == PARENT_INODE
            and parent_identity.st_uid == os.geteuid(),
            "authenticate the exact existing first-party Rust variants parent")
    os.mkdir(DIRECTORY, 0o700, dir_fd=parent)
    child = os.open(DIRECTORY, directory_flags, dir_fd=parent)
    child_identity = os.fstat(child)
    require(stat.S_ISDIR(child_identity.st_mode)
            and stat.S_IMODE(child_identity.st_mode) == 0o700
            and child_identity.st_dev == DEVICE and child_identity.st_uid == os.geteuid(),
            "authenticate exactly one new private corrected-source directory")
    output_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    output = os.open("lib.rs", output_flags, 0o600, dir_fd=child)
    initial = os.fstat(output)
    require(stat.S_ISREG(initial.st_mode) and stat.S_IMODE(initial.st_mode) == 0o600
            and initial.st_dev == DEVICE and initial.st_uid == os.geteuid()
            and initial.st_nlink == 1 and initial.st_size == 0,
            "require one fresh exclusive no-follow first-party Rust source")
    while wall.written < len(corrected):
        os.write(output, memoryview(corrected)[wall.written:])
    os.fsync(output)
    complete = os.fstat(output)
    require(complete.st_dev == initial.st_dev and complete.st_ino == initial.st_ino
            and complete.st_size == CORRECTED_BYTES and complete.st_nlink == 1
            and stat.S_IMODE(complete.st_mode) == 0o600,
            "reject an incomplete, replaced, linked, or permission-altered corrected source")
    os.close(output)
    os.fsync(child)
    os.close(child)
    os.fsync(parent)
    os.close(parent)
    require(wall.output_opened and wall.output_synced and wall.child_synced and wall.parent_synced
            and wall.output_fd is None and wall.child_fd is None and wall.parent_fd is None,
            "fully synchronize the one exclusive corrected source and both directories")
    return {"schema": SCHEMA + "-application", "status": "APPLIED", "mode": "apply",
            "source_sha256": pins["--source-sha256"],
            "protocol_sha256": pins["--protocol-sha256"],
            "contract_sha256": pins["--contract-sha256"],
            "frozen_pushed_commit": pins["--pushed-commit"],
            "created": {"directory": {"path": PARENT + "/" + DIRECTORY,
                                       "device": child_identity.st_dev,
                                       "inode": child_identity.st_ino,
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
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "raw_benchmark_files_opened": 0,
            "archives_opened": 0, "final_holdout_content_open_count": 0,
            "final_holdout_metadata_probe_count": 0, "clock_samples": 0,
            "original_case_execution_denominator": 31237,
            "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
            "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False}


def main() -> int:
    validate_runtime()
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
                  "historical_v25_semantic_mismatch_count": 1352,
                  "historical_v26_public_mismatch_count": 1145,
                  "historical_v27_public_mismatch_count": 1145,
                  "targeted_residual_public_mismatch_count": 2,
                  "targeted_public_case_ids": [case["case"] for case in state["cases"]],
                  "derived_canonical_engine_sha256": CORRECTED_SHA256,
                  "derived_canonical_engine_bytes": CORRECTED_BYTES,
                  "derived_anchor_composition_sha256": ANCHOR_CORRECTED_SHA256,
                  "derived_combined_composition_sha256": COMBINED_CORRECTED_SHA256,
                  "bounded_synthetic_case_count":
                      state["synthetic"]["bounded_differential_case_count"],
                  "previously_unsound_synthetic_cases_repaired":
                      state["synthetic"]["previously_unsound_cases_repaired"],
                  "mandatory_anchor_accelerator_preserved": True,
                  "source_mutations": 0, "candidate_imports": 0,
                  "candidate_processes_started": 0, "native_libraries_loaded": 0,
                  "raw_benchmark_files_opened": 0, "archives_opened": 0,
                  "private_roots_opened": 0, "final_holdout_content_open_count": 0,
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
        sys.stderr.write("scoped-Unicode first-party source freeze rejected: " + str(error) + "\n")
        raise SystemExit(2)
