#!/usr/bin/env python3
"""Freeze the observed Rust compiled-pattern representation repair."""

from __future__ import annotations

import argparse
import ast
import builtins
import ctypes
import enum
import fcntl
import gzip
import hashlib
import importlib
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re as oracle_re
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-rust-public-contract-source-repair-v3"
SOURCE_RELATIVE = "tools/apply_owned_rust_public_contract_source_repair_v3.py"
PROTOCOL_RELATIVE = "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md"
CONTRACT_RELATIVE = "oracle/phase2/rust-public-contract-source-repair-v3.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
LIMIT = 8 * 1024 * 1024
SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
PRIVATE_WAIVER_COUNT = 13
V32_HISTORY_OWNERS = 153
V32_HISTORY_REFERENCES = 158
APPENDED_ZIG_OWNERS = 2
CURRENT_EVIDENCE_LOWER_BOUND = 155
CURRENT_REFERENCE_LOWER_BOUND = 160
ORIGINAL_SHA256 = "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"
ORIGINAL_BYTES = 31_151
V2_DERIVED_SHA256 = "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
V2_DERIVED_BYTES = 31_464
DERIVED_SHA256 = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
DERIVED_BYTES = 31_934
PRIVATE_ROOT_PREFIX = "rebar-phase2-native-build-"
PRIVATE_ROOT_FAMILY = "-rust-"
PHASE_NAMES = ("reference-a", "reference-b")


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int


GOAL = Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
SUPPLEMENT = Owner("oracle/phase1/p0-callable-introspection-v1.json", "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749)
UPSTREAM_TEST = Owner("oracle/cpython-3.14.6/test_re.py", "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2", 150895)
TYPE_EVALUATOR = Owner("tools/independent_public_type_identity_serialization_v1.py", "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20", 150015)
ORIGINAL_PRODUCER = Owner("tools/run_owned_six_family_original_p0_producer_v3.py", "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555)
V2 = (
    Owner("tools/apply_owned_rust_public_contract_source_repair_v2.py", "d0f90145195e9978482a7797956ef916adb1d0612118c2fc6343c4f38b823fa8", 74140),
    Owner("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V2.md", "3f469ca7298b08cc1d50d18aff5029ae17a3f4f318c4fc7a2d8f8f45cc16e239", 5505),
    Owner("oracle/phase2/rust-public-contract-source-repair-v2.json", "b87c876e16041b0e08619aec0a86a069598b54478a1fa55cc9baa220c2c1f53b", 13826),
)
V32 = (
    Owner("tools/render_candidate_current_overview_v32.py", "998c8589cd1fb5a2d309603991e4b377c75cfb3dc85057ea597c6b08e9045df7", 75889),
    Owner("docs/evidence/candidate-current-overview-v32.inputs.json", "1739b0c1b785b93f9f47522a22bc844e9ce5c898bd6580ec01157ce7bdd9a82d", 100773),
    Owner("docs/evidence/candidate-current-overview-v32.json", "394ba794ce6bcad9d04da271d45f4465adcada8c4e00e3a75138ae9c257c71d2", 362246),
    Owner("docs/evidence/candidate-current-overview-v32.svg", "6366260bf300fab10893d9be20f1b5a2e181acb64db9776ee9e0fce3fcb699aa", 13753),
)
RUST_OWNERS = (
    Owner("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    Owner("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    Owner("candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
    Owner("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    Owner("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    Owner("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    Owner("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    Owner("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    Owner("candidates/rust_candidate.py", ORIGINAL_SHA256, ORIGINAL_BYTES),
)
RUST_ARCHIVE = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures.json.gz", "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f", 3663299)
RUST_RECEIPT = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json", "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3", 4674)
C_RECEIPT = Owner("oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json", "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9", 3482)
ZIG_RECEIPT = Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba", 4534)
ZIG_V12_ARCHIVE = Owner("oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2.json.gz", "3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d", 48371)
ZIG_V12_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2-publication-receipt.json", "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b", 2029)
INSTALLED = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14"
INSTALLED_RE = Owner(INSTALLED + "/re/__init__.py", "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35", 17876)
INSTALLED_COMPILER = Owner(INSTALLED + "/re/_compiler.py", "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91", 26855)
INSTALLED_CONSTANTS = Owner(INSTALLED + "/re/_constants.py", "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b", 6036)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
ENUM_FLAG_ORDER = ("ASCII", "IGNORECASE", "LOCALE", "UNICODE", "MULTILINE", "DOTALL", "VERBOSE", "DEBUG")
PATTERN_FLAG_ORDER = ("IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "UNICODE", "VERBOSE", "DEBUG", "ASCII")
ACTUAL_CASE = "pattern-and-match-representation/058"
CASE_PATTERN = "(?P<word>[A-Za-z]+)(?P<number>[0-9]+)"
CASE_MATCH = "<re.Match object; span=(0, 7), match='Alpha42'>"
ACTUAL_PATTERN_REPR = "re.compile('(?P<word>[A-Za-z]+)(?P<number>[0-9]+)', re.ASCII|re.IGNORECASE)"
EXPECTED_PATTERN_REPR = "re.compile('(?P<word>[A-Za-z]+)(?P<number>[0-9]+)', re.IGNORECASE|re.ASCII)"
CASE_RECORD_SHA256 = "1130da7818fe8b27a0d74f607bd4531c43f5f12ec9d6674419aa448786884d75"
CASE_RECORD_BYTES = 901
NESTED_ARCHIVE_SHA256 = "1c2c54598d2642c9f3ed764e7cebf3498273defbf1242594bc9e394e8a90b8a0"
OUTER_PREFIX_SHA256 = "9d90192b27a21c183b5208e87e4a86cf396a98306873aa7b570c1162d0a03c6d"
NESTED_PREFIX_SHA256 = "d865de60cfb433dc63b2cc2175f8f8e4ddf70465ba7ec9e8c20414a8a90622f3"

OLD_FLAG_BLOCK = b"""        ordered = ((self.ASCII, "ASCII"), (self.IGNORECASE, "IGNORECASE"), (self.LOCALE, "LOCALE"), (self.UNICODE, "UNICODE"), (self.MULTILINE, "MULTILINE"), (self.DOTALL, "DOTALL"), (self.VERBOSE, "VERBOSE"), (self.DEBUG, "DEBUG"))
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
        if unknown:
            parts.append(hex(unknown))
        return "|".join(parts)
"""
V2_FLAG_BLOCK = b"""        ordered = (
            (self.ASCII, "ASCII"),
            (self.IGNORECASE, "IGNORECASE"),
            (self.LOCALE, "LOCALE"),
            (self.UNICODE, "UNICODE"),
            (self.MULTILINE, "MULTILINE"),
            (self.DOTALL, "DOTALL"),
            (self.VERBOSE, "VERBOSE"),
            (self.DEBUG, "DEBUG"),
        )
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
        if unknown:
            if not parts:
                return f"re.RegexFlag({value})"
            parts.append(hex(unknown))
        return "|".join(parts)
"""
OLD_ERROR_BLOCK = b"""class PatternError(Exception):
    def __init__(self, msg, pattern=None, pos=None):
"""
V2_ERROR_BLOCK = b"""class PatternError(Exception):
    __module__ = "re"

    def __init__(self, msg, pattern=None, pos=None):
"""
OLD_PATTERN_BLOCK = b"""    def __repr__(self):
        flags = self.flags & ~int(UNICODE)
        shown = repr(self.pattern)
        if len(shown) > 200:
            shown = shown[:200]
        suffix = f", {RegexFlag(flags)!r}" if flags else ""
        return f"re.compile({shown}{suffix})"

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (type(self.pattern), self.pattern, self.flags) == (type(other.pattern), other.pattern, other.flags)

    def __hash__(self):
        return hash((type(self.pattern), self.pattern, self.flags))
"""
V2_PATTERN_BLOCK = b"""    def __repr__(self):
        flags = self.flags & ~int(UNICODE)
        shown = repr(self.pattern)
        if len(shown) > 200:
            shown = shown[:200]
        if flags:
            rendered = repr(RegexFlag(flags))
            if rendered.startswith("re.RegexFlag("):
                rendered = hex(flags)
            suffix = f", {rendered}"
        else:
            suffix = ""
        return f"re.compile({shown}{suffix})"

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (self.pattern, self.flags) == (other.pattern, other.flags)

    def __hash__(self):
        return hash((self.pattern, self.flags))
"""
V3_PATTERN_BLOCK = b"""    def __repr__(self):
        flags = self.flags & ~int(UNICODE)
        shown = repr(self.pattern)
        if len(shown) > 200:
            shown = shown[:200]
        if flags:
            ordered = (
                (int(IGNORECASE), "re.IGNORECASE"),
                (int(LOCALE), "re.LOCALE"),
                (int(MULTILINE), "re.MULTILINE"),
                (int(DOTALL), "re.DOTALL"),
                (int(UNICODE), "re.UNICODE"),
                (int(VERBOSE), "re.VERBOSE"),
                (int(DEBUG), "re.DEBUG"),
                (int(ASCII), "re.ASCII"),
            )
            parts = [name for bit, name in ordered if flags & bit]
            unknown = flags & ~sum(bit for bit, _ in ordered)
            if unknown:
                parts.append(hex(unknown))
            suffix = ", " + "|".join(parts)
        else:
            suffix = ""
        return f"re.compile({shown}{suffix})"

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (self.pattern, self.flags) == (other.pattern, other.flags)

    def __hash__(self):
        return hash((self.pattern, self.flags))
"""
UPSTREAM_METHODS = {
    "test_without_flags": (2823, 2825, "37293c5eaca711e98a3f1ded6eefe090f7a03206806de64a7e075f7c2b12f448"),
    "test_single_flag": (2827, 2829, "6174462e038a7052ca3be79afe3d8b99c63e9b28693924a8bd09876ab6a57126"),
    "test_multiple_flags": (2831, 2834, "32942cc3eb5cfe57916f4058c86612b365633387397fd874c45b92aa8a600bc8"),
    "test_unicode_flag": (2836, 2841, "f89370b933636bb8fbf8dd7b59ab6b50f0c229aeca8c5450880fda3f5d32988f"),
    "test_unknown_flags": (2847, 2851, "fc77ec59ea16c5b7885d2f168ee7525126f30dee97cee932d9c597ae9d986604"),
    "test_bytes": (2853, 2857, "57e43e4ed97797cf465e2200c63588d9b5d979f32724d14609f9642341b1c00f"),
    "test_locale": (2859, 2861, "351e235e6d1a244aab62378856426e9e1054f2c35ba545c6caee5266a993a142"),
    "test_flags_repr": (2881, 2893, "704b97cac458d08cce2fb03ed6e95ff3cf0c898bb09a97c39de0e113d3b5adbc"),
}


class RepairError(Exception):
    """An authenticated source, witness, private path, or phase was rejected."""


class ForbiddenEffect(RepairError):
    """An actual forbidden effect was physically blocked."""


def need(value: object, message: str) -> None:
    if value is not True:
        raise RepairError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only immutable bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(char in "0123456789abcdef" for char in value),
         "reject an unpinned or noncanonical SHA-256: " + label)
    return value


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                           allow_nan=False, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject an ambiguous canonical evidence document") from exc


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    need(type(raw) is bytes and 0 < len(raw) <= LIMIT,
         "reject unbounded or empty JSON: " + label)

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            need(type(key) is str and key not in result,
                 "reject duplicate JSON evidence: " + label)
            result[key] = value
        return result

    def nonfinite(value: str) -> Any:
        raise RepairError("reject nonfinite JSON: " + value)

    try:
        value = json.loads(raw.decode("utf-8", "strict"),
                           object_pairs_hook=unique, parse_constant=nonfinite)
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject malformed evidence: " + label) from exc
    need(type(value) is dict and canonical(value) == raw,
         "reject noncanonical evidence: " + label)
    return value


def owner_document(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size}


def checked_relative(path: object) -> tuple[str, ...]:
    need(type(path) is str and 0 < len(path) <= 512
         and "\\" not in path and "\x00" not in path,
         "reject an escaped or non-string relative path")
    value = PurePosixPath(path)
    need(not value.is_absolute() and str(value) == path
         and 0 < len(value.parts) <= 12
         and all(part not in ("", ".", "..") for part in value.parts),
         "reject an escaped, ambiguous, or broadened owner path")
    return value.parts


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.abspath(sys.executable) == PYTHON
         and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
         "require pinned isolated and bytecode-free CPython 3.14.6")
    need(os.path.abspath(oracle_re.__file__) == INSTALLED_RE.path
         and os.path.abspath(oracle_re._compiler.__file__) == INSTALLED_COMPILER.path
         and os.path.abspath(oracle_re._constants.__file__) == INSTALLED_CONSTANTS.path,
         "authenticate the actually installed isolated standard-library oracle")
    need(not any(name == "candidates" or name.startswith("candidates.")
                 for name in sys.modules),
         "never import a production candidate into the source-only oracle")


def read_owner(owner: Owner, *, external: bool = False) -> tuple[bytes, dict[str, Any]]:
    checked_digest(owner.sha256, owner.path)
    need(type(owner.size) is int and 0 < owner.size <= LIMIT,
         "reject an oversized or unbounded evidence owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories: list[int] = []
    handle: int | None = None
    try:
        if external:
            need(owner in (INSTALLED_RE, INSTALLED_COMPILER, INSTALLED_CONSTANTS),
                 "reject an unpinned external oracle path")
            handle = os.open(owner.path, flags)
            visible = os.stat(owner.path, follow_symlinks=False)
        else:
            parts = checked_relative(owner.path)
            if parts[0] == "candidates":
                need(owner in RUST_OWNERS,
                     "never read a native target or another candidate family")
            if owner.path.endswith(".gz"):
                need(owner in (RUST_ARCHIVE, ZIG_V12_ARCHIVE),
                     "never inspect another matching, build, or holdout archive")
            folder = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
            directories.append(folder)
            for part in parts[:-1]:
                folder = os.open(part, flags | getattr(os, "O_DIRECTORY", 0),
                                 dir_fd=folder)
                directories.append(folder)
            handle = os.open(parts[-1], flags, dir_fd=folder)
            visible = os.stat(parts[-1], dir_fd=folder, follow_symlinks=False)
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
             and before.st_nlink == 1 and before.st_size == owner.size
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_uid, before.st_nlink)
             == (visible.st_dev, visible.st_ino, visible.st_size,
                 visible.st_uid, visible.st_nlink),
             "reject linked, changed, foreign, or truncated owner: " + owner.path)
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(handle, min(remaining, 65536))
            need(type(chunk) is bytes and bool(chunk),
                 "reject truncated descriptor-bound evidence: " + owner.path)
            pieces.append(chunk)
            remaining -= len(chunk)
        need(os.read(handle, 1) == b"", "reject appended owner: " + owner.path)
        raw = b"".join(pieces)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size, before.st_uid,
              before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                 after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
             and digest(raw) == owner.sha256,
             "reject changed or substituted immutable owner: " + owner.path)
        return raw, {"path": owner.path, "sha256": owner.sha256,
                     "bytes": owner.size, "device": after.st_dev,
                     "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
                     "uid": after.st_uid, "nlink": after.st_nlink}
    finally:
        if handle is not None:
            os.close(handle)
        for directory in reversed(directories):
            os.close(directory)


def observed_case() -> dict[str, Any]:
    def row(rendered: str) -> dict[str, Any]:
        return {
            "case": ACTUAL_CASE,
            "cohort": "pattern-and-match-representation",
            "domain": "str",
            "flags": 258,
            "outcome": {
                "status": "return",
                "value": {
                    "items": [{"kind": "str", "value": rendered},
                              {"kind": "str", "value": CASE_MATCH}],
                    "kind": "tuple",
                },
                "warnings": [],
            },
            "pattern_index": 0,
            "pickle_protocol": 0,
        }

    return {"actual_record": row(ACTUAL_PATTERN_REPR),
            "case": ACTUAL_CASE,
            "expected_record": row(EXPECTED_PATTERN_REPR)}


def verify_case(value: object) -> None:
    need(type(value) is dict and value == observed_case(),
         "reject a reconstructed or substituted actual archived mismatch")
    raw = canonical(value)[:-1]
    need(len(raw) == CASE_RECORD_BYTES and digest(raw) == CASE_RECORD_SHA256,
         "bind the complete exact 901-byte first actual V4 mismatch")


def replace_once(source: bytes, old: bytes, new: bytes, label: str) -> bytes:
    need(type(source) is bytes and type(old) is bytes and type(new) is bytes
         and bool(old) and bool(new) and old != new,
         "reject invalid anchored bytes: " + label)
    need(source.count(old) == 1 and source.count(new) == 0,
         "require one unchanged first-party source anchor: " + label)
    offset = source.index(old)
    prefix, suffix = source[:offset], source[offset + len(old):]
    result = prefix + new + suffix
    need(result.startswith(prefix) and result.endswith(suffix)
         and result.count(old) == 0 and result.count(new) == 1,
         "reject an out-of-anchor Rust source edit: " + label)
    return result


def derive_sources(source: bytes, *, frozen: bool) -> tuple[bytes, bytes]:
    need(type(source) is bytes and 0 < len(source) <= LIMIT,
         "require one complete original first-party Rust adapter")
    if frozen:
        need(len(source) == ORIGINAL_BYTES and digest(source) == ORIGINAL_SHA256,
             "reject a substituted original Rust public adapter")
    v2 = source
    for label, before, after in (
        ("preserved-v2-standalone-regexflag", OLD_FLAG_BLOCK, V2_FLAG_BLOCK),
        ("preserved-v2-public-pattern-error", OLD_ERROR_BLOCK, V2_ERROR_BLOCK),
        ("preserved-v2-pattern-value-equality-and-hash", OLD_PATTERN_BLOCK, V2_PATTERN_BLOCK),
    ):
        v2 = replace_once(v2, before, after, label)
    if frozen:
        need(len(v2) == V2_DERIVED_BYTES and digest(v2) == V2_DERIVED_SHA256,
             "reproduce the actual independently tested V2 adapter in memory")
    fixed = replace_once(v2, V2_PATTERN_BLOCK, V3_PATTERN_BLOCK,
                         "actual-public-types-pattern-058-compiled-flag-order")
    need(fixed.count(V2_FLAG_BLOCK) == 1 and v2.count(V2_FLAG_BLOCK) == 1
         and fixed.count(V2_ERROR_BLOCK) == 1 and v2.count(V2_ERROR_BLOCK) == 1,
         "never change V2 standalone flags or public errors")
    for marker in (b"return _cache2[type(pattern), pattern, flags]",
                   b"key = (type(pattern), pattern, flags)",
                   b"def _template(", b"def _cached_template(",
                   b"def _restore_owned_generic_alias(", b"class Scanner:",
                   b"_rust_bridge.set_template(_template)", b"__all__ = "):
        need(source.count(marker) == 1 and v2.count(marker) == 1
             and fixed.count(marker) == 1,
             "preserve exact cache, template, scanner, and export owner: " + marker.decode())
    for marker in (b"return (self.pattern, self.flags) == (other.pattern, other.flags)",
                   b"return hash((self.pattern, self.flags))"):
        need(v2.count(marker) == 1 and fixed.count(marker) == 1,
             "preserve exact V2 pattern equality and hashing")
    for forbidden in (b"import re\n", b"from re import", b"import _sre",
                      b"from _sre", b"regex.compile", b"pcre", b"oniguruma",
                      b"candidates.vm_candidate", b"candidates.zig_candidate",
                      b"candidates.cpp_candidate", b"candidates.go_candidate",
                      b"candidates.fortran_candidate", b"subprocess", b"ctypes"):
        need(fixed.count(forbidden) == source.count(forbidden),
             "never introduce a delegated matcher or another candidate")
    try:
        tree = ast.parse(fixed.decode("utf-8", "strict"),
                         filename="private-snapshot/candidates/rust_candidate.py")
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise RepairError("reject syntactically invalid owned Rust adapter") from exc
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    need({"RegexFlag", "PatternError", "Pattern"} <= set(classes),
         "preserve the actual owned Rust public classes")
    error_modules = [node for node in classes["PatternError"].body
                     if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name)
                             and target.id == "__module__"
                             for target in node.targets)]
    need(len(error_modules) == 1
         and isinstance(error_modules[0].value, ast.Constant)
         and error_modules[0].value.value == "re",
         "preserve the owned V2 PatternError public module")
    if frozen:
        need(len(fixed) == DERIVED_BYTES and digest(fixed) == DERIVED_SHA256,
             "freeze only the exact independently derived V3 source")
    return v2, fixed


def sample_source() -> bytes:
    return (
        b"import enum\n\nclass RegexFlag(enum.IntFlag):\n"
        b"    NOFLAG = 0\n    ASCII = A = 256\n    IGNORECASE = I = 2\n"
        b"    LOCALE = L = 4\n    UNICODE = U = 32\n    MULTILINE = M = 8\n"
        b"    DOTALL = S = 16\n    VERBOSE = X = 64\n    DEBUG = 128\n"
        b"    _numeric_repr_ = hex\n    def __repr__(self):\n"
        b"        value = int(self)\n        if not value:\n            return \"re.NOFLAG\"\n"
        + OLD_FLAG_BLOCK + b"\n" + OLD_ERROR_BLOCK
        + b"        super().__init__(msg)\n\nclass Pattern:\n"
        + OLD_PATTERN_BLOCK
        + b"\n    def __reduce__(self):\n        return None\n"
        b"    def _cached_template(self):\n        return None\n"
        b"\ndef _template():\n    return None\n"
        b"\ndef _restore_owned_generic_alias():\n    return None\n"
        b"\nclass Scanner:\n    pass\n"
        b"\ndef example(pattern, flags):\n"
        b"    key = (type(pattern), pattern, flags)\n"
        b"    return _cache2[type(pattern), pattern, flags]\n"
        b"\ndef registration():\n    _rust_bridge.set_template(_template)\n"
        b"\n__all__ = []\n"
    )


def synthetic_types(source: bytes) -> tuple[type[enum.IntFlag], type[Any]]:
    try:
        tree = ast.parse(source.decode("utf-8", "strict"),
                         filename="in-memory-first-party-rust-v3")
        flags = [node for node in tree.body
                 if isinstance(node, ast.ClassDef) and node.name == "RegexFlag"]
        patterns = [node for node in tree.body
                    if isinstance(node, ast.ClassDef) and node.name == "Pattern"]
        need(len(flags) == 1 and len(patterns) == 1,
             "require exactly one synthetic owned flag and pattern type")
        methods = [node for node in patterns[0].body
                   if isinstance(node, ast.FunctionDef) and node.name == "__repr__"]
        need(len(methods) == 1, "require one owned compiled-pattern repr")
        namespace: dict[str, Any] = {"enum": enum, "__name__": SCHEMA + "_synthetic"}
        module = ast.Module(body=[flags[0]], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module),
                     "<synthetic-owned-rust-v3-flags>", "exec", dont_inherit=True), namespace)
        flag_type = namespace["RegexFlag"]
        need(isinstance(flag_type, enum.EnumType)
             and issubclass(flag_type, enum.IntFlag),
             "require a genuine synthetic owned IntFlag")
        for name in ENUM_FLAG_ORDER:
            namespace[name] = getattr(flag_type, name)
        pattern_class = ast.ClassDef(name="Pattern", bases=[], keywords=[],
                                     body=[methods[0]], decorator_list=[])
        pattern_module = ast.Module(body=[pattern_class], type_ignores=[])
        exec(compile(ast.fix_missing_locations(pattern_module),
                     "<synthetic-owned-rust-v3-pattern>", "exec", dont_inherit=True), namespace)
        return flag_type, namespace["Pattern"]
    except (SyntaxError, UnicodeError, TypeError, ValueError, RecursionError) as exc:
        raise RepairError("reject invalid synthetic owned representation") from exc


def pattern_repr(pattern_type: type[Any], pattern: str | bytes,
                 flags: int) -> str:
    value = pattern_type.__new__(pattern_type)
    value.pattern = pattern
    value.flags = flags
    return repr(value)


def verify_flag_vectors(flag_type: type[enum.IntFlag]) -> dict[str, Any]:
    sparse = (-(1 << 30) - 1, -(1 << 20), 1 << 20,
              (1 << 20) | 44, 1 << 30, (1 << 30) | 256,
              (1 << 30) | 2 | 64)
    count = 0
    for value in (*range(-1024, 4097), *sparse):
        need(repr(flag_type(value)) == repr(oracle_re.RegexFlag(value)),
             "reject an actual pinned standalone RegexFlag mismatch: " + str(value))
        count += 1
    need(count == 5128, "preserve all 5,128 genuine standalone flag vectors")
    need(repr(flag_type(0)) == "re.NOFLAG"
         and repr(flag_type(1024)) == "re.RegexFlag(1024)"
         and repr(flag_type(1280)) == "re.ASCII|0x400",
         "preserve V2 zero, pure unknown, and mixed unknown flags")
    return {"actual_isolated_stdlib_flag_vector_count": count,
            "known_order": list(ENUM_FLAG_ORDER),
            "zero": repr(flag_type(0)),
            "pure_unknown": repr(flag_type(1024)),
            "mixed_unknown": repr(flag_type(1280))}


def expression_value(node: ast.AST, values: dict[str, int]) -> int:
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id == "re" and node.attr in values):
        return values[node.attr]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return expression_value(node.left, values) | expression_value(node.right, values)
    raise RepairError("reject an unverified upstream pattern-flag expression")


def official_pattern_vectors(upstream: bytes) -> list[tuple[str | bytes, int, str]]:
    try:
        text = upstream.decode("utf-8", "strict")
        tree = ast.parse(text, filename=UPSTREAM_TEST.path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise RepairError("reject the genuine pinned upstream representation tests") from exc
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == "PatternReprTests"]
    need(len(classes) == 1, "require the genuine PatternReprTests class")
    methods = {node.name: node for node in classes[0].body
               if isinstance(node, ast.FunctionDef)}
    for name, (start, end, expected_hash) in UPSTREAM_METHODS.items():
        node = methods.get(name)
        need(node is not None and node.lineno == start and node.end_lineno == end,
             "reject a substituted genuine upstream method: " + name)
        source = ast.get_source_segment(text, node)
        need(type(source) is str and digest(source.encode("utf-8")) == expected_hash,
             "reject an altered upstream representation method: " + name)
    values = {name: int(getattr(oracle_re, name)) for name in ENUM_FLAG_ORDER}
    values.update({"A": values["ASCII"], "I": values["IGNORECASE"],
                   "L": values["LOCALE"], "M": values["MULTILINE"],
                   "S": values["DOTALL"], "U": values["UNICODE"],
                   "X": values["VERBOSE"]})
    result: list[tuple[str | bytes, int, str]] = []
    for name in ("test_without_flags", "test_single_flag", "test_multiple_flags",
                 "test_unicode_flag", "test_unknown_flags", "test_bytes",
                 "test_locale"):
        for item in methods[name].body:
            if not (isinstance(item, ast.Expr)
                    and isinstance(item.value, ast.Call)
                    and isinstance(item.value.func, ast.Attribute)
                    and isinstance(item.value.func.value, ast.Name)
                    and item.value.func.value.id == "self"
                    and item.value.func.attr in ("check", "check_flags")):
                continue
            call = item.value
            args = call.args
            if call.func.attr == "check":
                need(len(args) == 2, "reject ambiguous official pattern check")
                pattern_node, expected_node = args
                flags = 0
            else:
                need(len(args) == 3, "reject ambiguous official pattern flag check")
                pattern_node, flag_node, expected_node = args
                flags = expression_value(flag_node, values)
            need(isinstance(pattern_node, ast.Constant)
                 and isinstance(pattern_node.value, (str, bytes))
                 and isinstance(expected_node, ast.Constant)
                 and isinstance(expected_node.value, str),
                 "derive pattern repr witnesses only from actual upstream AST")
            result.append((pattern_node.value, flags, expected_node.value))
    need(len(result) == 10,
         "never change the ten source-derived official pattern witnesses")
    return result


def verify_pattern_vectors(pattern_type: type[Any],
                           vectors: list[tuple[str | bytes, int, str]]) -> int:
    for pattern, flags, expected in vectors:
        need(pattern_repr(pattern_type, pattern, flags) == expected,
             "reject actual upstream compiled-pattern repr witness")
    need(pattern_repr(pattern_type, CASE_PATTERN, 258) == EXPECTED_PATTERN_REPR,
         "correct the actual archived public-types 058 mismatch")
    return len(vectors) + 1


def accounting() -> dict[str, Any]:
    return {
        "historical_v32_evidence_owner_count": V32_HISTORY_OWNERS,
        "historical_v32_authenticated_reference_count": V32_HISTORY_REFERENCES,
        "appended_authenticated_zig_v12_evidence_owner_count": APPENDED_ZIG_OWNERS,
        "authenticated_repository_evidence_owner_lower_bound": CURRENT_EVIDENCE_LOWER_BOUND,
        "authenticated_reference_lower_bound": CURRENT_REFERENCE_LOWER_BOUND,
        "historical_v32_is_not_asserted_to_be_current": True,
        "later_append_only_evidence_allowed": True,
        "rust_candidate_status": "FAIL",
        "rust_semantic_mismatch_count": 1036,
        "rust_verified_passing_case_count": 8965,
        "rust_candidate_worker_count": 13,
        "rust_infrastructure_failure_count": 0,
        "c_candidate_status": "FAIL",
        "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "last_tested_zig_candidate_status": "FAIL",
        "last_tested_zig_semantic_mismatch_count": 2172,
        "last_tested_zig_verified_passing_case_count": 2847,
        "zig_v12_source_build_status": "PASS",
        "zig_v12_actual_compiler_process_count": 26,
        "zig_v12_actual_source_apply_count": 2,
        "zig_v12_candidate_matching": "NOT MEASURED",
        "supplementary_signature_case_count": 50,
        "supplementary_signature_reference_status": "NOT RUN",
        "supplementary_signature_reference_cases_executed": 0,
        "full_case_denominator": CASE_DENOMINATOR,
        "suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "qualified_candidate_count": 0,
    }


def validate_accounting(value: object) -> None:
    need(type(value) is dict and value == accounting(),
         "reject false current ownership, hidden failures, an opened supplement, or a weakened oracle")


def boundary() -> dict[str, Any]:
    return {
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_processes_started": 0,
        "upstream_unittest_methods_executed": 0,
        "supplementary_reference_cases_executed": 0,
        "source_builds_started": 0,
        "compiler_processes_started": 0,
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "canonical_native_target_reads": 0,
        "canonical_native_target_stats": 0,
        "source_apply_count": 0,
        "workspace_mutations": 0,
        "recovery_locks_acquired": 0,
        "recovery_journals_created": 0,
        "network_requests": 0,
        "threads_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "rust_matching_archive_uncompressed_bytes_read": 0,
        "nested_matching_archive_uncompressed_bytes_read": 0,
        "c_matching_archive_uncompressed_bytes_read": 0,
        "zig_matching_archive_uncompressed_bytes_read": 0,
        "zig_v12_build_archive_uncompressed_bytes_read": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "final_holdout_opened": False,
        "final_comparison_cases_generated": False,
        "winner_selected": False,
    }


def forensic_document() -> dict[str, Any]:
    verify_case(observed_case())
    return {
        "archive": owner_document(RUST_ARCHIVE),
        "publication_receipt": owner_document(RUST_RECEIPT),
        "lifetime_outer_prefix_inspection_count": 4,
        "outer_prefix_uncompressed_bytes": 1_638_400,
        "outer_prefix_uncompressed_limit": 1_638_400,
        "outer_prefix_sha256": OUTER_PREFIX_SHA256,
        "outer_prefix_compressed_bytes_consumed": 1_179_658,
        "outer_archive_fully_decompressed": False,
        "nested_public_types_gzip_sha256": NESTED_ARCHIVE_SHA256,
        "nested_public_types_gzip_compressed_bytes": 203_558,
        "nested_public_types_complete_uncompressed_bytes": 15_869_754,
        "nested_prefix_uncompressed_bytes": 4096,
        "nested_prefix_uncompressed_limit": 65_536,
        "nested_prefix_compressed_bytes_consumed": 131_082,
        "nested_prefix_sha256": NESTED_PREFIX_SHA256,
        "nested_archive_fully_decompressed": False,
        "failing_suite": "public_types_v1",
        "failing_suite_case_execution_denominator": 6912,
        "failing_suite_actual_mismatch_count": 140,
        "preceding_complete_passing_suite_count": 6,
        "failure_class": "SEMANTIC MISMATCH",
        "first_actual_case": ACTUAL_CASE,
        "first_actual_case_record_sha256": CASE_RECORD_SHA256,
        "first_actual_case_record_bytes": CASE_RECORD_BYTES,
        "first_actual_case_record": observed_case(),
        "actual_corrected_v2_pattern_repr": ACTUAL_PATTERN_REPR,
        "actual_frozen_cpython_pattern_repr": EXPECTED_PATTERN_REPR,
        "actual_match_repr_unchanged": CASE_MATCH,
        "candidate_matching_after_v3": "NOT MEASURED",
        "source_gates_reopen_matching_archive_for_decompression": False,
    }


def block_document() -> dict[str, Any]:
    return {
        "name": "actual-public-types-pattern-058-compiled-flag-order",
        "original_sha256": digest(V2_PATTERN_BLOCK),
        "original_bytes": len(V2_PATTERN_BLOCK),
        "original_occurrence_count": 1,
        "derived_sha256": digest(V3_PATTERN_BLOCK),
        "derived_bytes": len(V3_PATTERN_BLOCK),
        "derived_occurrence_count": 1,
    }


def contract_document(source: str, protocol: str) -> dict[str, Any]:
    checked_digest(source, "V3 source")
    checked_digest(protocol, "V3 explanation")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 3,
        "phase": "SOURCE FREEZE; NO APPLICATION, BUILD, CANDIDATE, OR PERFORMANCE RUN",
        "source": {"path": SOURCE_RELATIVE, "sha256": source},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol},
        "goal": owner_document(GOAL),
        "original_p0": owner_document(PHASE_ONE),
        "supplementary_signature_source_freeze": owner_document(SUPPLEMENT),
        "runtime": {"implementation": "cpython", "version": "3.14.6",
                    "python": PYTHON, "python_sha256": PYTHON_SHA256,
                    "isolated": True, "bytecode_writes": False},
        "upstream": {"test": owner_document(UPSTREAM_TEST),
                     "pattern_methods": {
                         key: {"start_line": value[0], "end_line": value[1],
                               "source_sha256": value[2]}
                         for key, value in UPSTREAM_METHODS.items()},
                     "public_type_evaluator": owner_document(TYPE_EVALUATOR),
                     "original_producer": owner_document(ORIGINAL_PRODUCER),
                     "official_source_derived_pattern_vector_count": 10,
                     "actual_stdlib_regexflag_vector_count": 5128,
                     "upstream_unittest_methods_executed": 0},
        "preserved_v2": {"owners": [owner_document(item) for item in V2],
                         "derived_sha256": V2_DERIVED_SHA256,
                         "derived_bytes": V2_DERIVED_BYTES,
                         "standalone_flag_block_sha256": digest(V2_FLAG_BLOCK),
                         "standalone_flag_order": list(ENUM_FLAG_ORDER),
                         "error_block_sha256": digest(V2_ERROR_BLOCK),
                         "pattern_equality_preserved": True,
                         "pattern_hash_preserved": True,
                         "pure_unknown_preserved": True,
                         "mixed_unknown_preserved": True,
                         "noflag_preserved": True,
                         "v2_verifier_invoked": False},
        "actual_failure": forensic_document(),
        "repair": {
            "original": {"path": "candidates/rust_candidate.py",
                         "sha256": ORIGINAL_SHA256, "bytes": ORIGINAL_BYTES,
                         "modified": False},
            "derived": {"path": "candidates/rust_candidate.py",
                        "sha256": DERIVED_SHA256, "bytes": DERIVED_BYTES,
                        "materialized": False},
            "anchored_v3_block_count": 1,
            "anchored_v2_block_count": 3,
            "block": block_document(),
            "standalone_regexflag_order": list(ENUM_FLAG_ORDER),
            "compiled_pattern_flag_order": list(PATTERN_FLAG_ORDER),
            "standalone_flags_modified": False,
            "native_parser_compiler_executor_modified": False,
            "native_bridge_modified": False,
            "external_regex_engine_added": False,
            "stdlib_regex_delegation_added": False,
            "cross_family_delegation_added": False,
            "all_other_v2_source_bytes_preserved": True,
            "candidate_matching_proven": False,
        },
        "rust_source": {"family": "rust",
                        "owners": [owner_document(item) for item in RUST_OWNERS],
                        "cargo_lock_package_count": 1,
                        "external_regex_dependency_count": 0,
                        "cross_family_dependency_count": 0},
        "published_history": {
            "immutable_v32_snapshot": {
                "owners": [owner_document(item) for item in V32],
                "historical_repository_evidence_owner_count": V32_HISTORY_OWNERS,
                "historical_authenticated_reference_count": V32_HISTORY_REFERENCES,
                "asserted_to_be_current": False,
            },
            "authenticated_append_only_zig_v12_source_build": {
                "archive": owner_document(ZIG_V12_ARCHIVE),
                "receipt": owner_document(ZIG_V12_RECEIPT),
                "new_evidence_owner_count": APPENDED_ZIG_OWNERS,
                "compiler_process_count": 26,
                "source_apply_count": 2,
                "candidate_matching": "NOT MEASURED",
            },
            "rust_v4_failure_receipt": owner_document(RUST_RECEIPT),
            "c_v4_failure_receipt": owner_document(C_RECEIPT),
            "last_tested_zig_failure_receipt": owner_document(ZIG_RECEIPT),
            "authenticated_accounting": accounting(),
        },
        "apply_policy": {
            "explicit_apply_required": True,
            "independent_source_digest_required": True,
            "independent_source_length_required": True,
            "snapshot_root_required": True,
            "private_parent": "/tmp",
            "private_root_prefix": PRIVATE_ROOT_PREFIX,
            "private_root_required_family_component": PRIVATE_ROOT_FAMILY,
            "phase_names": list(PHASE_NAMES),
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "destination_relative": "source/candidates/rust_candidate.py",
            "creation_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "distinct_reference_phase_inodes_required": True,
            "canonical_candidate_destination": "FORBIDDEN",
            "other_candidate_destination": "FORBIDDEN",
            "candidate_activation": "FORBIDDEN",
            "candidate_build": "FORBIDDEN",
        },
        "phase_boundary": boundary(),
    }


class SourceWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {name: 0 for name in (
            "filesystem", "write", "process", "import", "network", "thread",
            "clock", "native", "lock", "signal", "decompression")}

    def deny(self, owner: Any, name: str, category: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise ForbiddenEffect("physically blocked " + category + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceWall:
        rules = (
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "resolve"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename", "replace", "fsync"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename", "replace"), "write"),
            (tempfile, ("mkdtemp", "mkstemp"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output"), "process"),
            (importlib, ("import_module",), "import"),
            (socket, ("socket", "create_connection"), "network"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "process_time", "process_time_ns", "sleep"), "clock"),
            (ctypes, ("CDLL", "PyDLL"), "native"),
            (fcntl, ("flock",), "lock"),
            (signal, ("signal", "pthread_sigmask"), "signal"),
            (gzip, ("open", "decompress", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        )
        for owner, names, category in rules:
            for name in names:
                self.deny(owner, name, category)
        return self

    def __exit__(self, *_args: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def validate_v2(source: bytes, contract: dict[str, Any]) -> None:
    need(contract.get("schema")
         == "rebar-phase2-owned-rust-public-contract-source-repair-v2-source-freeze"
         and contract.get("version") == 2,
         "authenticate the actual immutable V2 source freeze")
    repair = contract.get("repair")
    need(type(repair) is dict
         and repair.get("original", {}).get("sha256") == ORIGINAL_SHA256
         and repair.get("derived", {}).get("sha256") == V2_DERIVED_SHA256
         and repair.get("derived", {}).get("bytes") == V2_DERIVED_BYTES
         and repair.get("derived", {}).get("materialized") is False
         and repair.get("anchored_block_count") == 3
         and repair.get("known_flag_order") == list(ENUM_FLAG_ORDER),
         "preserve all actual V2 source repairs without invoking V2")
    try:
        tree = ast.parse(source.decode("utf-8", "strict"), filename=V2[0].path)
        actual: dict[str, bytes] = {}
        names = {"OLD_FLAG_BLOCK", "CORRECTED_FLAG_BLOCK", "OLD_ERROR_BLOCK",
                 "NEW_ERROR_BLOCK", "OLD_EQUALITY_BLOCK", "NEW_EQUALITY_BLOCK"}
        for item in tree.body:
            if isinstance(item, ast.Assign) and len(item.targets) == 1:
                target = item.targets[0]
                if isinstance(target, ast.Name) and target.id in names:
                    need(target.id not in actual,
                         "reject duplicated immutable V2 source blocks")
                    actual[target.id] = ast.literal_eval(item.value)
    except (SyntaxError, TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject changed immutable V2 source blocks") from exc
    expected = {"OLD_FLAG_BLOCK": OLD_FLAG_BLOCK,
                "CORRECTED_FLAG_BLOCK": V2_FLAG_BLOCK,
                "OLD_ERROR_BLOCK": OLD_ERROR_BLOCK,
                "NEW_ERROR_BLOCK": V2_ERROR_BLOCK,
                "OLD_EQUALITY_BLOCK": OLD_PATTERN_BLOCK,
                "NEW_EQUALITY_BLOCK": V2_PATTERN_BLOCK}
    need(actual == expected,
         "derive V3 solely from the actual pinned V2 blocks")


def validate_history(summary: dict[str, Any], inputs: dict[str, Any],
                     rust: dict[str, Any], c: dict[str, Any], zig: dict[str, Any],
                     zig_build: dict[str, Any], supplement: dict[str, Any],
                     rust_archive_owner: dict[str, Any],
                     zig_archive_owner: dict[str, Any]) -> None:
    need(summary.get("schema") == "rebar-candidate-current-overview-v32-summary"
         and summary.get("status") == "PASS"
         and summary.get("full_case_denominator") == CASE_DENOMINATOR
         and summary.get("suite_count") == SUITE_COUNT
         and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
         and summary.get("repository_evidence_owner_count") == V32_HISTORY_OWNERS
         and summary.get("authenticated_digest_addressed_history_paths") == V32_HISTORY_REFERENCES
         and summary.get("qualified_candidate_count") == 0
         and summary.get("rust_original_campaign_status") == "FAIL"
         and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
         and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
         and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
         and summary.get("c_original_campaign_verified_passing_case_count") == 7325
         and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
         and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
         and summary.get("additional_signature_frozen_case_count") == 50
         and summary.get("additional_signature_reference_cases_executed") == 0
         and summary.get("additional_signature_reference_status") == "NOT RUN"
         and summary.get("final_comparison_planned_case_count") == 4_194_304
         and summary.get("final_holdout_opened") is False
         and summary.get("final_comparison_cases_generated") is False
         and summary.get("performance") == "NOT MEASURED"
         and summary.get("memory") == "NOT MEASURED"
         and summary.get("undefined_behavior") == "NOT MEASURED"
         and summary.get("clock_samples") == 0
         and summary.get("winner_selected") is False,
         "authenticate V32 strictly as historical 153/158 evidence")
    need(inputs.get("schema") == "rebar-candidate-current-overview-v32-inputs"
         and inputs.get("version") == 32
         and inputs.get("repository_evidence_owner_count") == V32_HISTORY_OWNERS
         and inputs.get("all_digest_addressed_history_path_count") == V32_HISTORY_REFERENCES
         and inputs.get("full_case_denominator") == CASE_DENOMINATOR
         and inputs.get("suite_count") == SUITE_COUNT
         and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
         and inputs.get("candidate_qualified_count") == 0
         and inputs.get("actual_rust_candidate_workers") == 13
         and inputs.get("actual_rust_infrastructure_failure_count") == 0
         and inputs.get("actual_rust_semantic_mismatch_count") == 1036
         and inputs.get("actual_rust_verified_passing_case_count") == 8965
         and inputs.get("all_four_original_rust_targets_restored") is True
         and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
         and inputs.get("actual_zig_semantic_mismatch_count") == 2172
         and inputs.get("additional_signature_frozen_case_count") == 50
         and inputs.get("additional_signature_reference_cases_executed") == 0
         and inputs.get("additional_signature_reference_status") == "NOT RUN"
         and inputs.get("final_holdout_opened") is False,
         "preserve the immutable V32 graph inputs as history, not current")
    archive = rust.get("archive")
    need(rust.get("schema") == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
         and rust.get("status") == "PASS"
         and rust.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
         and rust.get("candidate_status") == "FAIL"
         and rust.get("family") == "rust"
         and rust.get("actual_candidate_workers") == 13
         and rust.get("completed_suite_count") == SUITE_COUNT
         and rust.get("case_execution_denominator") == CASE_DENOMINATOR
         and rust.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
         and rust.get("semantic_mismatch_count") == 1036
         and rust.get("verified_passing_case_count") == 8965
         and rust.get("infrastructure_failure_count") == 0
         and rust.get("candidate_qualified") is False
         and rust.get("corrected_public_adapter_sha256") == V2_DERIVED_SHA256
         and rust.get("corrected_bridge_source_sha256")
         == "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
         and rust.get("all_four_original_targets_restored") is True
         and rust.get("restoration_verified_before_publication") is True
         and type(archive) is dict
         and archive.get("sha256") == rust_archive_owner["sha256"]
         and archive.get("size_bytes") == rust_archive_owner["bytes"]
         and archive.get("device") == rust_archive_owner["device"]
         and archive.get("inode") == rust_archive_owner["inode"]
         and rust.get("holdout") == "NOT OPENED"
         and rust.get("performance") == "NOT MEASURED",
         "bind the genuine complete 1,036-mismatch V4 Rust failure")
    need(c.get("schema") == "rebar-owned-repaired-c-original-campaign-v4-durable-publication-receipt"
         and c.get("candidate_status") == "FAIL"
         and c.get("actual_candidate_workers") == 13
         and c.get("completed_suite_count") == SUITE_COUNT
         and c.get("case_execution_denominator") == CASE_DENOMINATOR
         and c.get("semantic_mismatch_count") == 1230
         and c.get("verified_passing_case_count") == 7325
         and c.get("candidate_qualified") is False
         and c.get("holdout") == "NOT OPENED",
         "preserve the real failed C candidate")
    need(zig.get("schema") == "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt"
         and zig.get("candidate_status") == "FAIL"
         and zig.get("actual_candidate_workers") == 13
         and zig.get("completed_suite_count") == SUITE_COUNT
         and zig.get("case_execution_denominator") == CASE_DENOMINATOR
         and zig.get("semantic_mismatch_count") == 2172
         and zig.get("verified_passing_case_count") == 2847
         and zig.get("candidate_qualified") is False
         and zig.get("holdout") == "NOT OPENED",
         "preserve the last genuinely tested failed Zig candidate")
    appended = zig_build.get("archive")
    need(zig_build.get("schema")
         == "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt"
         and zig_build.get("status") == "PASS"
         and zig_build.get("build_status") == "PASS"
         and zig_build.get("family") == "zig"
         and zig_build.get("actual_evidence_owner_count_before_publication")
         == V32_HISTORY_OWNERS
         and zig_build.get("actual_authenticated_reference_count_before_publication")
         == V32_HISTORY_REFERENCES
         and zig_build.get("new_actual_evidence_owner_count") == APPENDED_ZIG_OWNERS
         and zig_build.get("repository_evidence_owner_count_after_publication")
         == CURRENT_EVIDENCE_LOWER_BOUND
         and zig_build.get("authenticated_history_reference_count_after_publication")
         == CURRENT_REFERENCE_LOWER_BOUND
         and zig_build.get("actual_compiler_process_count") == 26
         and zig_build.get("actual_source_apply_count") == 2
         and zig_build.get("candidate_correctness") == "NOT MEASURED"
         and zig_build.get("candidate_imports") == 0
         and zig_build.get("candidate_processes_started") == 0
         and zig_build.get("holdout") == "NOT OPENED"
         and zig_build.get("clock_samples") == 0
         and zig_build.get("timing_trials_run") == 0
         and zig_build.get("winner_selected") is False
         and type(appended) is dict
         and appended.get("sha256") == zig_archive_owner["sha256"]
         and appended.get("bytes") == zig_archive_owner["bytes"]
         and appended.get("inode") == zig_archive_owner["inode"],
         "prove append-only genuine 155/160 Zig-build evidence without claiming matching")
    extra = supplement.get("additional_obligation")
    wall = supplement.get("phase_boundary")
    need(supplement.get("schema")
         == "rebar-python-re-callable-introspection-v1-source-freeze"
         and supplement.get("status")
         == "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN"
         and type(extra) is dict and extra.get("case_count") == 50
         and type(extra.get("case_matrix")) is list
         and len(extra["case_matrix"]) == 50
         and type(wall) is dict
         and wall.get("introspection_reference") == "NOT RUN"
         and wall.get("candidate_introspection") == "NOT MEASURED"
         and wall.get("actual_reference_roles_started") == 0
         and wall.get("actual_candidate_imports") == 0
         and wall.get("holdout") == "NOT OPENED",
         "preserve all 50 separate signature cases without running their reference")


def read_contract_owners(source_pin: str, protocol_pin: str,
                         contract_pin: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frozen: list[dict[str, Any]] = []
    for path, pin in ((SOURCE_RELATIVE, source_pin),
                      (PROTOCOL_RELATIVE, protocol_pin),
                      (CONTRACT_RELATIVE, contract_pin)):
        checked_digest(pin, path)
        size = os.stat(str(ROOT / path), follow_symlinks=False).st_size
        _, actual = read_owner(Owner(path, pin, size))
        frozen.append(actual)
    contract_raw, _ = read_owner(Owner(CONTRACT_RELATIVE, contract_pin,
                                        frozen[2]["bytes"]))
    expected = contract_document(source_pin, protocol_pin)
    need(strict_json(contract_raw, "exact V3 caller-pinned source contract") == expected
         and digest(canonical(expected)) == contract_pin,
         "reject a changed or substituted V3 canonical contract")
    return expected, frozen


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str) -> tuple[dict[str, Any], bytes]:
    expected, frozen = read_contract_owners(source_pin, protocol_pin, contract_pin)
    owners = (GOAL, PHASE_ONE, SUPPLEMENT, UPSTREAM_TEST, TYPE_EVALUATOR,
              ORIGINAL_PRODUCER, *V2, *V32, *RUST_OWNERS, RUST_ARCHIVE,
              RUST_RECEIPT, C_RECEIPT, ZIG_RECEIPT,
              ZIG_V12_ARCHIVE, ZIG_V12_RECEIPT)
    raw: dict[str, bytes] = {}
    actual: list[dict[str, Any]] = []
    for owner in owners:
        payload, identity = read_owner(owner)
        raw[owner.path] = payload
        actual.append(identity)
    external: list[dict[str, Any]] = []
    for owner in (INSTALLED_RE, INSTALLED_COMPILER, INSTALLED_CONSTANTS):
        _, identity = read_owner(owner, external=True)
        external.append(identity)
    phase = strict_json(raw[PHASE_ONE.path], "unchanged complete P0 matrix")
    denominator = phase.get("denominator")
    need(phase.get("schema") == "rebar-cpython-re-p0-completeness-v1"
         and type(denominator) is dict
         and denominator.get("final_required_case_execution_denominator") == CASE_DENOMINATOR
         and denominator.get("frozen_planned_case_execution_denominator") == CASE_DENOMINATOR
         and denominator.get("private_upstream_methods_outside_public_denominator")
         == PRIVATE_WAIVER_COUNT
         and denominator.get("counted_suite_ids") == [name for name, _ in SUITES],
         "preserve exactly all 31,237 original cases and 13 named exclusions")
    v2_contract = strict_json(raw[V2[2].path], "immutable V2 source contract")
    validate_v2(raw[V2[0].path], v2_contract)
    v2, fixed = derive_sources(raw[RUST_OWNERS[-1].path], frozen=True)
    source = raw[ORIGINAL_PRODUCER.path]
    need(source.count(b'SuiteSpec("public_types_v1", 6912,') == 1
         and source.count(b'"tools/independent_public_type_identity_serialization_v1.py"') >= 1,
         "authenticate the frozen source of the actually failing original suite")
    need(raw[TYPE_EVALUATOR.path].count(
        b'if cohort == "pattern-and-match-representation":') == 1,
        "authenticate the actual first failing pattern-representation cohort")
    cargo = raw[RUST_OWNERS[1].path].decode("utf-8", "strict")
    lock = raw[RUST_OWNERS[0].path].decode("utf-8", "strict")
    need("[dependencies" not in cargo and "[dev-dependencies" not in cargo
         and "[build-dependencies" not in cargo
         and lock.count("[[package]]") == 1
         and 'name = "rebar-rust-continuation"' in lock,
         "reject an external package or borrowed Rust regex engine")
    summary = strict_json(raw[V32[2].path], "immutable V32 historical summary")
    inputs = strict_json(raw[V32[1].path], "immutable V32 historical inputs")
    rust = strict_json(raw[RUST_RECEIPT.path], "actual V4 Rust failure receipt")
    c = strict_json(raw[C_RECEIPT.path], "actual C failure receipt")
    zig = strict_json(raw[ZIG_RECEIPT.path], "last completed Zig failure receipt")
    zig_build = strict_json(raw[ZIG_V12_RECEIPT.path], "actual appended Zig V12 build receipt")
    supplement = strict_json(raw[SUPPLEMENT.path], "unrun 50-case signature supplement")
    rust_identity = next(item for item in actual if item["path"] == RUST_ARCHIVE.path)
    zig_identity = next(item for item in actual if item["path"] == ZIG_V12_ARCHIVE.path)
    validate_history(summary, inputs, rust, c, zig, zig_build, supplement,
                     rust_identity, zig_identity)
    old_flags, old_pattern = synthetic_types(v2)
    flags, pattern = synthetic_types(fixed)
    old_vectors = verify_flag_vectors(old_flags)
    vectors = verify_flag_vectors(flags)
    official = official_pattern_vectors(raw[UPSTREAM_TEST.path])
    pattern_count = verify_pattern_vectors(pattern, official)
    need(pattern_repr(old_pattern, CASE_PATTERN, 258) == ACTUAL_PATTERN_REPR
         and pattern_repr(pattern, CASE_PATTERN, 258) == EXPECTED_PATTERN_REPR,
         "reproduce and fix the actual archived first Rust failure in memory")
    need(old_vectors == vectors and vectors["known_order"] == list(ENUM_FLAG_ORDER),
         "never regress V2 standalone flags to compiled-pattern ordering")
    verify_case(observed_case())
    validate_accounting(accounting())
    need(not any(name == "candidates" or name.startswith("candidates.")
                 for name in sys.modules), "never import a candidate")
    need(expected == contract_document(source_pin, protocol_pin),
         "preserve the exact independent V3 source freeze")
    output = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": 3,
        "mode": "READ-ONLY EVIDENCE-FIRST SOURCE FREEZE",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "frozen_owner_count": len(frozen),
        "authenticated_support_owner_count": len(actual),
        "authenticated_external_oracle_owner_count": len(external),
        "original_adapter_sha256": ORIGINAL_SHA256,
        "actual_previously_tested_v2_adapter_sha256": V2_DERIVED_SHA256,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        "actual_first_failure_case": ACTUAL_CASE,
        "actual_first_failure_record_sha256": CASE_RECORD_SHA256,
        "actual_first_failure_record_bytes": CASE_RECORD_BYTES,
        "actual_first_failure_suite": "public_types_v1",
        "actual_first_failure_suite_mismatches": 140,
        "actual_first_failure_actual": ACTUAL_PATTERN_REPR,
        "actual_first_failure_expected": EXPECTED_PATTERN_REPR,
        "actual_failure_corrected_in_synthetic_source": True,
        "actual_stdlib_standalone_flag_vector_count": vectors["actual_isolated_stdlib_flag_vector_count"],
        "actual_upstream_pattern_source_vector_count": len(official),
        "total_in_memory_pattern_vector_count": pattern_count,
        "v2_standalone_flag_bytes_preserved": True,
        "v2_error_equality_and_hash_preserved": True,
        "source_matching_archive_compressed_bytes_authenticated": RUST_ARCHIVE.size,
        "source_zig_build_archive_compressed_bytes_authenticated": ZIG_V12_ARCHIVE.size,
        "historical_v32_evidence_owner_count": V32_HISTORY_OWNERS,
        "historical_v32_authenticated_reference_count": V32_HISTORY_REFERENCES,
        "authenticated_repository_evidence_owner_lower_bound": CURRENT_EVIDENCE_LOWER_BOUND,
        "authenticated_reference_lower_bound": CURRENT_REFERENCE_LOWER_BOUND,
        "authenticated_append_only_zig_v12_build_process_count": 26,
        "authenticated_append_only_zig_v12_source_apply_count": 2,
        "latest_built_zig_matching": "NOT MEASURED",
        "last_tested_zig_mismatches": 2172,
        "actual_rust_semantic_mismatch_count": 1036,
        "actual_rust_verified_passing_case_count": 8965,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_zig_semantic_mismatch_count": 2172,
        "supplementary_signature_case_count": 50,
        "supplementary_signature_reference_status": "NOT RUN",
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        **boundary(),
    }
    return output, fixed


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    expected = contract_document(source_pin, protocol_pin)
    need(digest(canonical(expected)) == checked_digest(contract_pin, "V3 contract"),
         "reject a caller-substituted source-only V3 contract")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(label: str, condition: bool) -> None:
        need(condition, "rejected positive control: " + label)
        accepted.append(label)

    def reject(label: str, action: Any) -> None:
        try:
            action()
        except (RepairError, OSError, ValueError, TypeError, UnicodeError,
                SyntaxError, RecursionError, OverflowError):
            rejected.append(label)
            return
        raise RepairError("accepted hostile source-only control: " + label)

    with SourceWall() as wall:
        sample = sample_source()
        previous, fixed = derive_sources(sample, frozen=False)
        previous_flags, previous_pattern = synthetic_types(previous)
        flags, pattern = synthetic_types(fixed)
        old_vectors = verify_flag_vectors(previous_flags)
        vectors = verify_flag_vectors(flags)
        accept("preserve all 5,128 actual standalone CPython flag vectors",
               vectors["actual_isolated_stdlib_flag_vector_count"] == 5128)
        accept("preserve all V2 standalone flag vectors byte-for-byte",
               old_vectors == vectors)
        accept("reproduce the actual V4 pattern case",
               pattern_repr(previous_pattern, CASE_PATTERN, 258) == ACTUAL_PATTERN_REPR)
        accept("fix the actual V4 pattern case only in synthetic owned source",
               pattern_repr(pattern, CASE_PATTERN, 258) == EXPECTED_PATTERN_REPR)
        accept("preserve actual archived match representation",
               observed_case()["actual_record"]["outcome"]["value"]["items"][1]["value"] == CASE_MATCH)
        verify_case(observed_case())
        accept("authenticate the exact 901-byte real mismatch",
               len(canonical(observed_case())[:-1]) == CASE_RECORD_BYTES)
        accept("preserve V2 zero flag", vectors["zero"] == "re.NOFLAG")
        accept("preserve V2 pure unknown", vectors["pure_unknown"] == "re.RegexFlag(1024)")
        accept("preserve V2 mixed unknown", vectors["mixed_unknown"] == "re.ASCII|0x400")
        accept("separate compiled and standalone flag ordering",
               ENUM_FLAG_ORDER != PATTERN_FLAG_ORDER)
        accept("preserve exact actual 155/160 appended-evidence lower bound",
               accounting()["authenticated_repository_evidence_owner_lower_bound"] == 155
               and accounting()["authenticated_reference_lower_bound"] == 160)
        accept("label 153/158 V32 strictly as history",
               accounting()["historical_v32_is_not_asserted_to_be_current"] is True)
        accept("preserve actual Zig source build without claiming matching",
               accounting()["zig_v12_actual_compiler_process_count"] == 26
               and accounting()["zig_v12_actual_source_apply_count"] == 2
               and accounting()["zig_v12_candidate_matching"] == "NOT MEASURED")
        accept("preserve current actual Rust failure",
               accounting()["rust_semantic_mismatch_count"] == 1036
               and accounting()["rust_verified_passing_case_count"] == 8965)
        accept("preserve current actual C and last-tested Zig failures",
               accounting()["c_semantic_mismatch_count"] == 1230
               and accounting()["last_tested_zig_semantic_mismatch_count"] == 2172)
        accept("never execute the 50-case extra signature reference",
               accounting()["supplementary_signature_case_count"] == 50
               and accounting()["supplementary_signature_reference_status"] == "NOT RUN")
        accept("preserve all original P0 cases",
               len(SUITES) == SUITE_COUNT
               and sum(amount for _, amount in SUITES) == CASE_DENOMINATOR)
        accept("never claim candidate correctness or speed",
               boundary()["candidate_correctness"] == "NOT MEASURED"
               and boundary()["performance"] == "NOT MEASURED")
        accept("preserve an unopened holdout",
               boundary()["holdout"] == "NOT OPENED"
               and boundary()["final_holdout_opened"] is False)
        validate_accounting(accounting())
        for label, before in (
            ("standalone RegexFlag", OLD_FLAG_BLOCK),
            ("owned PatternError", OLD_ERROR_BLOCK),
            ("owned Pattern repr/equality/hash", OLD_PATTERN_BLOCK),
        ):
            for kind, hostile in (
                ("missing", sample.replace(before, b"# missing\n")),
                ("duplicate", sample.replace(before, before + before)),
            ):
                reject("reject " + kind + " anchored " + label,
                       lambda value=hostile: derive_sources(value, frozen=False))
        reject("reject an already applied standalone flag block",
               lambda: derive_sources(sample.replace(OLD_FLAG_BLOCK, V2_FLAG_BLOCK), frozen=False))
        reject("reject an already applied pattern block",
               lambda: derive_sources(sample.replace(OLD_PATTERN_BLOCK, V2_PATTERN_BLOCK), frozen=False))
        reject("reject synthetic sample as canonical candidate",
               lambda: derive_sources(sample, frozen=True))
        reject("reject the old actual failing Pattern representation",
               lambda: need(pattern_repr(previous_pattern, CASE_PATTERN, 258)
                            == EXPECTED_PATTERN_REPR, "actual V2 failure preserved"))
        reject("reject swapping true archived expected and actual",
               lambda: verify_case({**observed_case(),
                                    "actual_record": observed_case()["expected_record"]}))
        reject("reject changing first genuine frozen mismatch ID",
               lambda: verify_case({**observed_case(), "case": ACTUAL_CASE + "x"}))
        for bad in ("", "0" * 63, "0" * 65, "A" * 64,
                    "z" * 64, None, 0, True):
            reject("reject hostile independent digest",
                   lambda value=bad: checked_digest(value, "hostile"))
        for bad in ("", "/tmp/escaped", "../escaped", "a/../b", "a//b",
                    "a/./b", "./a", "a/", "a\\b", "x" * 513):
            reject("reject hostile evidence path",
                   lambda value=bad: checked_relative(value))
        for bad in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n', b"[]\n",
                    b'{"x":1}', b"", b"null\n"):
            reject("reject noncanonical hostile evidence",
                   lambda value=bad: strict_json(value, "hostile"))
        attacks = {
            "historical_v32_evidence_owner_count": 155,
            "historical_v32_authenticated_reference_count": 160,
            "appended_authenticated_zig_v12_evidence_owner_count": 0,
            "authenticated_repository_evidence_owner_lower_bound": 153,
            "authenticated_reference_lower_bound": 158,
            "historical_v32_is_not_asserted_to_be_current": False,
            "later_append_only_evidence_allowed": False,
            "rust_candidate_status": "PASS",
            "rust_semantic_mismatch_count": 0,
            "rust_verified_passing_case_count": 31237,
            "rust_candidate_worker_count": 12,
            "rust_infrastructure_failure_count": 1,
            "c_candidate_status": "PASS",
            "c_semantic_mismatch_count": 0,
            "c_verified_passing_case_count": 31237,
            "last_tested_zig_candidate_status": "PASS",
            "last_tested_zig_semantic_mismatch_count": 0,
            "last_tested_zig_verified_passing_case_count": 31237,
            "zig_v12_source_build_status": "FAIL",
            "zig_v12_actual_compiler_process_count": 0,
            "zig_v12_actual_source_apply_count": 0,
            "zig_v12_candidate_matching": "PASS",
            "supplementary_signature_case_count": 0,
            "supplementary_signature_reference_status": "PASS",
            "supplementary_signature_reference_cases_executed": 50,
            "full_case_denominator": 31236,
            "suite_count": 12,
            "private_waiver_count": 12,
            "qualified_candidate_count": 1,
        }
        for key, replacement in attacks.items():
            changed = accounting()
            changed[key] = replacement
            reject("reject forged actual baseline: " + key,
                   lambda value=changed: validate_accounting(value))
        for key, replacement in (
            ("candidate_correctness", "PASS"),
            ("candidate_qualified", True),
            ("candidate_imports", 1),
            ("candidate_workers_started", 1),
            ("reference_processes_started", 1),
            ("upstream_unittest_methods_executed", 1),
            ("supplementary_reference_cases_executed", 1),
            ("source_builds_started", 1),
            ("compiler_processes_started", 1),
            ("native_activations", 1),
            ("native_libraries_loaded", 1),
            ("canonical_native_target_reads", 1),
            ("canonical_native_target_stats", 1),
            ("source_apply_count", 1),
            ("workspace_mutations", 1),
            ("recovery_locks_acquired", 1),
            ("network_requests", 1),
            ("threads_started", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("rust_matching_archive_uncompressed_bytes_read", 1),
            ("nested_matching_archive_uncompressed_bytes_read", 1),
            ("c_matching_archive_uncompressed_bytes_read", 1),
            ("zig_matching_archive_uncompressed_bytes_read", 1),
            ("zig_v12_build_archive_uncompressed_bytes_read", 1),
            ("performance", "FASTER"),
            ("memory", "ZERO"),
            ("undefined_behavior", "PASS"),
            ("holdout", "OPENED"),
            ("final_holdout_opened", True),
            ("final_comparison_cases_generated", True),
            ("winner_selected", True),
        ):
            hostile = boundary()
            hostile[key] = replacement
            reject("reject forbidden phase-boundary effect: " + key,
                   lambda value=hostile: need(value == boundary(),
                                             "changed source-only boundary"))
        probes = (
            ("filesystem", lambda: builtins.open("/tmp/rebar-v3-forbidden", "rb")),
            ("filesystem", lambda: io.open("/tmp/rebar-v3-forbidden", "rb")),
            ("filesystem", lambda: os.open("/tmp/rebar-v3-forbidden", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("/tmp/rebar-v3-forbidden")),
            ("filesystem", lambda: Path("/tmp/rebar-v3-forbidden").read_bytes()),
            ("write", lambda: os.write(-1, b"forbidden")),
            ("write", lambda: tempfile.mkdtemp()),
            ("process", lambda: subprocess.run(("rebar-v3-forbidden",))),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("import", lambda: importlib.import_module("re")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("native", lambda: ctypes.CDLL("rebar-v3-forbidden")),
            ("lock", lambda: fcntl.flock(-1, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden")),
            ("decompression", lambda: zlib.decompress(b"forbidden")),
            ("decompression", lambda: gzip.GzipFile(fileobj=io.BytesIO())),
        )
        for category, action in probes:
            before = wall.blocked[category]
            reject("physically block " + category, action)
            need(wall.blocked[category] == before + 1,
                 "prove a genuine hostile effect was blocked: " + category)
        blocked = dict(wall.blocked)
    need(len(accepted) >= 18 and len(rejected) >= 100
         and all(value > 0 for value in blocked.values()),
         "require all positive controls, hostile controls, and blocked effects")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "version": 3,
        "mode": "PHYSICALLY WALLED SYNTHETIC SOURCE ONLY",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "blocked_effects_by_kind": blocked,
        "actual_first_failure_case": ACTUAL_CASE,
        "actual_first_failure_record_sha256": CASE_RECORD_SHA256,
        "actual_first_failure_corrected_in_synthetic_source": True,
        "actual_stdlib_standalone_flag_vector_count": 5128,
        "v2_standalone_flag_bytes_preserved": True,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        "historical_v32_evidence_owner_count": V32_HISTORY_OWNERS,
        "historical_v32_authenticated_reference_count": V32_HISTORY_REFERENCES,
        "authenticated_repository_evidence_owner_lower_bound": CURRENT_EVIDENCE_LOWER_BOUND,
        "authenticated_reference_lower_bound": CURRENT_REFERENCE_LOWER_BOUND,
        "supplementary_signature_case_count": 50,
        "supplementary_signature_reference_status": "NOT RUN",
        "actual_rust_semantic_mismatch_count": 1036,
        "actual_rust_verified_passing_case_count": 8965,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_zig_semantic_mismatch_count": 2172,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        **boundary(),
    }


def open_private_directory(parent: int, name: str) -> int:
    need(type(name) is str and bool(name) and name not in (".", "..")
         and "/" not in name and "\\" not in name,
         "reject an escaped private source directory")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    handle = os.open(name, flags, dir_fd=parent)
    try:
        current = os.fstat(handle)
        visible = os.stat(name, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISDIR(current.st_mode) and current.st_uid == os.geteuid()
             and stat.S_IMODE(current.st_mode) == 0o700
             and (current.st_dev, current.st_ino)
             == (visible.st_dev, visible.st_ino),
             "require a no-follow, unchanged, owner-only private phase")
        return handle
    except BaseException:
        os.close(handle)
        raise


def apply_private(root: str, derived: bytes, source_pin: str,
                  protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    need(type(root) is str and 0 < len(root) <= 512,
         "require one independently caller-pinned private root")
    parsed = PurePosixPath(root)
    parts = parsed.parts
    need(parsed.is_absolute() and str(parsed) == root and len(parts) == 5
         and parts[0] == "/" and parts[1] == "tmp"
         and parts[2].startswith(PRIVATE_ROOT_PREFIX)
         and PRIVATE_ROOT_FAMILY in parts[2]
         and all(char.isascii() and (char.isalnum() or char in "-_")
                 for char in parts[2])
         and parts[3] in PHASE_NAMES and parts[4] == "source",
         "never write outside the exact first-party Rust /tmp private phase")
    need(type(derived) is bytes and len(derived) == DERIVED_BYTES
         and digest(derived) == DERIVED_SHA256,
         "reject changed private derived source bytes")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    tmp = os.open("/tmp", flags)
    top = phase = sibling = source = destination_dir = destination = None
    try:
        top = open_private_directory(tmp, parts[2])
        phase = open_private_directory(top, parts[3])
        other = "reference-b" if parts[3] == "reference-a" else "reference-a"
        sibling = open_private_directory(top, other)
        a, b = os.fstat(phase), os.fstat(sibling)
        need((a.st_dev, a.st_ino) != (b.st_dev, b.st_ino),
             "require two genuinely distinct Rust reference phases")
        source = open_private_directory(phase, "source")
        destination_dir = open_private_directory(source, "candidates")
        before, before_owner = read_owner(RUST_OWNERS[-1])
        _, expected = derive_sources(before, frozen=True)
        need(expected == derived,
             "refuse to apply after canonical candidate substitution")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        destination = os.open("rust_candidate.py", create, 0o600,
                              dir_fd=destination_dir)
        initial = os.fstat(destination)
        need(stat.S_ISREG(initial.st_mode)
             and initial.st_uid == os.geteuid() and initial.st_nlink == 1
             and stat.S_IMODE(initial.st_mode) == 0o600,
             "create only a fresh exclusively owned private Rust snapshot")
        cursor = 0
        while cursor < len(derived):
            count = os.write(destination, derived[cursor:])
            need(type(count) is int and count > 0,
                 "reject incomplete private source creation")
            cursor += count
        os.fsync(destination)
        complete = os.fstat(destination)
        need((initial.st_dev, initial.st_ino, initial.st_uid, initial.st_nlink)
             == (complete.st_dev, complete.st_ino, complete.st_uid,
                 complete.st_nlink) and complete.st_size == DERIVED_BYTES,
             "reject a swapped private source inode")
        os.close(destination)
        destination = None
        verify_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        verify_flags |= getattr(os, "O_NOFOLLOW", 0)
        verifier = os.open("rust_candidate.py", verify_flags,
                           dir_fd=destination_dir)
        try:
            info = os.fstat(verifier)
            need((info.st_dev, info.st_ino, info.st_uid, info.st_nlink,
                  info.st_size)
                 == (complete.st_dev, complete.st_ino, complete.st_uid,
                     complete.st_nlink, complete.st_size),
                 "reject changed private Rust source on readback")
            blocks: list[bytes] = []
            remaining = info.st_size
            while remaining:
                block = os.read(verifier, min(remaining, 65536))
                need(type(block) is bytes and bool(block),
                     "reject truncated private V3 readback")
                blocks.append(block)
                remaining -= len(block)
            actual = b"".join(blocks)
            need(os.read(verifier, 1) == b"" and actual == derived
                 and digest(actual) == DERIVED_SHA256,
                 "verify all bytes of the independent V3 private source")
        finally:
            os.close(verifier)
        os.fsync(destination_dir)
        after, after_owner = read_owner(RUST_OWNERS[-1])
        need(after == before and after_owner == before_owner,
             "never modify the actual canonical Rust adapter")
        return {
            "schema": SCHEMA + "-private-source-application",
            "status": "PASS", "version": 3,
            "source_sha256": source_pin,
            "protocol_sha256": protocol_pin,
            "contract_sha256": contract_pin,
            "snapshot_root": root,
            "phase": parts[3],
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_bytes": DERIVED_BYTES,
            "source_apply_count": 1,
            "canonical_candidate_modified": False,
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "source_builds_started": 0,
            "native_activations": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
    finally:
        if destination is not None:
            os.close(destination)
        for descriptor in (destination_dir, source, sibling, phase, top, tmp):
            if descriptor is not None:
                os.close(descriptor)


def parse_arguments(values: Sequence[str] | None = None) -> argparse.Namespace:
    arguments = list(sys.argv[1:] if values is None else values)
    flags = [value for value in arguments if value.startswith("--")]
    need(len(flags) == len(set(flags)), "reject repeated V3 authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", "--render-contract",
                       dest="emit_contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    parser.add_argument("--derived-source-sha256")
    parser.add_argument("--derived-source-bytes", type=int)
    options = parser.parse_args(arguments)
    checked_digest(options.source_sha256, "V3 source")
    checked_digest(options.protocol_sha256, "V3 protocol")
    if options.emit_contract:
        need(options.contract_sha256 is None
             and options.snapshot_root is None
             and options.derived_source_sha256 is None
             and options.derived_source_bytes is None,
             "contract emission never authorizes a source application")
    else:
        checked_digest(options.contract_sha256, "V3 contract")
        if options.apply:
            need(options.snapshot_root is not None
                 and checked_digest(options.derived_source_sha256,
                                    "independent derived source") == DERIVED_SHA256
                 and options.derived_source_bytes == DERIVED_BYTES,
                 "require exact independent private root, digest, and bytes")
        else:
            need(options.snapshot_root is None
                 and options.derived_source_sha256 is None
                 and options.derived_source_bytes is None,
                 "source-only gates cannot authorize a private write")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        runtime()
        options = parse_arguments(arguments)
        if options.emit_contract:
            output = contract_document(options.source_sha256,
                                       options.protocol_sha256)
        elif options.self_test:
            output = self_test(options.source_sha256,
                               options.protocol_sha256,
                               options.contract_sha256)
        elif options.verify_frozen_context:
            output, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256,
                                       options.contract_sha256)
        else:
            _, derived = verify_context(options.source_sha256,
                                        options.protocol_sha256,
                                        options.contract_sha256)
            output = apply_private(options.snapshot_root, derived,
                                   options.source_sha256,
                                   options.protocol_sha256,
                                   options.contract_sha256)
        sys.stdout.buffer.write(canonical(output))
        return 0
    except (RepairError, OSError, ValueError, TypeError, UnicodeError,
            RecursionError, SyntaxError, OverflowError, KeyError,
            AttributeError) as exc:
        sys.stderr.write("owned Rust public source repair v3 rejected: "
                         + str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
