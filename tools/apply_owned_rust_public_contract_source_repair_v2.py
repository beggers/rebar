#!/usr/bin/env python3
"""Freeze the observed, first-party Rust flag-order correction; never run it."""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
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
from typing import Any, Iterator, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-rust-public-contract-source-repair-v2"
SOURCE_RELATIVE = "tools/apply_owned_rust_public_contract_source_repair_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V2.md"
CONTRACT_RELATIVE = "oracle/phase2/rust-public-contract-source-repair-v2.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
LIMIT = 8 * 1024 * 1024
SUITE_COUNT = 13
CASE_DENOMINATOR = 31237
PRIVATE_WAIVER_COUNT = 13
CURRENT_EVIDENCE_OWNERS = 149
CURRENT_HISTORY_REFERENCES = 154
ORIGINAL_SHA256 = "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"
ORIGINAL_BYTES = 31151
V1_DERIVED_SHA256 = "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
DERIVED_SHA256 = "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
DERIVED_BYTES = 31464
PRIVATE_ROOT_PREFIX = "rebar-phase2-native-build-"
PRIVATE_ROOT_FAMILY = "-rust-"
PHASE_NAMES = ("reference-a", "reference-b")
UPSTREAM_LIBRARY = "/tmp/rebar-cpython/cpython-3.14.6-upstream-source/Python-3.14.6/Lib"
INSTALLED_LIBRARY = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14"
UPSTREAM_METHOD_SHA256 = "704b97cac458d08cce2fb03ed6e95ff3cf0c898bb09a97c39de0e113d3b5adbc"
UPSTREAM_METHOD_AST_SHA256 = "011c01bf4cb6f56f4f8317e5e1f1bf0d416e8ac43ac60cfffdc2e3ad113b9ff8"
RUST_JOURNAL = "b28862fc1433af8c2897299cf6d64fb672f452f011c68fe887714dc09b60ea65"
C_JOURNAL = "5844213bb1a986766ac5036e3de3e1795295540709710bc87c6383f08cdb23bd"


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int


GOAL = Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
COMMITTED_UPSTREAM_TEST = Owner("oracle/cpython-3.14.6/test_re.py", "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2", 150895)
V1 = (
    Owner("tools/apply_owned_rust_public_contract_source_repair_v1.py", "ac98ad24c6a4962fb38535cbaa470ae5cd4983643e7e8962e9fc9a1b6a0e12a0", 91232),
    Owner("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V1.md", "a297cbccfe4d4a2a321e7f8fe518662f451fd84f90e17bf86c62cf579875955f", 4027),
    Owner("oracle/phase2/rust-public-contract-source-repair-v1.json", "a3b4670c3e321cefd6a1ec65ba80b9aa1a06534a73e30ba56654cc75f6f11431", 13450),
)
V30 = (
    Owner("tools/render_candidate_current_overview_v30.py", "a8c2bb2e0ccfab0b76b5387437fe48279e01ca1034739a67967f543f1930c507", 60771),
    Owner("docs/evidence/candidate-current-overview-v30.inputs.json", "ea2ea381a22a9a23344ff40505d975aba8d25704d2ad90e03b58018fda44ca0f", 65902),
    Owner("docs/evidence/candidate-current-overview-v30.json", "b04db4e93dc74bb9200c13133c0a33bd33961b5f35e5810e74de65b29fcab534", 293980),
    Owner("docs/evidence/candidate-current-overview-v30.svg", "a3dbbb69c5140d15588463e0e3579d5bea5d95587f1abf444b6679cd3361d4c6", 12987),
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
RUST_ARCHIVE = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures.json.gz", "3ac7736c127d13d3fad579c4ab9974c6a83612b4253f7921ed3e44269f3a82ad", 5710284)
RUST_RECEIPT = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures-publication-receipt.json", "97f0b8c47823b20cd04740e3fe2883189cc648d49769015800c0998e6698c281", 4447)
C_RECEIPT = Owner("oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json", "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9", 3482)
ZIG_RECEIPT = Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba", 4534)
ZIG_PREFLIGHT_RECEIPT = Owner("oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23", 1992)
INSTALLED_RE = Owner(INSTALLED_LIBRARY + "/re/__init__.py", "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35", 17876)
INSTALLED_COMPILER = Owner(INSTALLED_LIBRARY + "/re/_compiler.py", "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91", 26855)
INSTALLED_CONSTANTS = Owner(INSTALLED_LIBRARY + "/re/_constants.py", "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b", 6036)
UPSTREAM_TEST = Owner(UPSTREAM_LIBRARY + "/test/test_re.py", "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2", 150895)

SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
OBSERVED_ACTUAL = "re.LOCALE|re.MULTILINE|re.DOTALL|re.UNICODE|re.VERBOSE|re.DEBUG|re.ASCII|0x1"
OBSERVED_EXPECTED = "re.ASCII|re.LOCALE|re.UNICODE|re.MULTILINE|re.DOTALL|re.VERBOSE|re.DEBUG|0x1"
OFFICIAL_EXPECTATIONS = (
    "re.IGNORECASE",
    "re.IGNORECASE|re.DOTALL|re.VERBOSE",
    "re.IGNORECASE|re.DOTALL|re.VERBOSE|0x100000",
    OBSERVED_EXPECTED,
    "re.ASCII|re.LOCALE|re.UNICODE|re.MULTILINE|re.DEBUG|0x1",
    "re.ASCII|re.LOCALE|re.UNICODE|re.MULTILINE|re.DEBUG|0xffe01",
)
CANONICAL_FLAG_ORDER = ("ASCII", "IGNORECASE", "LOCALE", "UNICODE", "MULTILINE", "DOTALL", "VERBOSE", "DEBUG")

OLD_FLAG_BLOCK = b"""        ordered = ((self.ASCII, "ASCII"), (self.IGNORECASE, "IGNORECASE"), (self.LOCALE, "LOCALE"), (self.UNICODE, "UNICODE"), (self.MULTILINE, "MULTILINE"), (self.DOTALL, "DOTALL"), (self.VERBOSE, "VERBOSE"), (self.DEBUG, "DEBUG"))
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
        if unknown:
            parts.append(hex(unknown))
        return "|".join(parts)
"""
V1_BAD_FLAG_BLOCK = b"""        ordered = (
            (self.IGNORECASE, "IGNORECASE"),
            (self.LOCALE, "LOCALE"),
            (self.MULTILINE, "MULTILINE"),
            (self.DOTALL, "DOTALL"),
            (self.UNICODE, "UNICODE"),
            (self.VERBOSE, "VERBOSE"),
            (self.DEBUG, "DEBUG"),
            (self.ASCII, "ASCII"),
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
CORRECTED_FLAG_BLOCK = b"""        ordered = (
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
NEW_ERROR_BLOCK = b"""class PatternError(Exception):
    __module__ = "re"

    def __init__(self, msg, pattern=None, pos=None):
"""
OLD_EQUALITY_BLOCK = b"""    def __repr__(self):
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
NEW_EQUALITY_BLOCK = b"""    def __repr__(self):
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
REPAIR_BLOCKS = (
    ("observed-cpython-flag-order-and-pure-unknown", OLD_FLAG_BLOCK, CORRECTED_FLAG_BLOCK),
    ("owned-public-pattern-error-module", OLD_ERROR_BLOCK, NEW_ERROR_BLOCK),
    ("owned-pattern-repr-value-equality-and-hash", OLD_EQUALITY_BLOCK, NEW_EQUALITY_BLOCK),
)


class RepairError(Exception):
    """An owner, actual witness, source-only boundary, or private path failed."""


class ForbiddenEffect(RepairError):
    """An actual side effect was physically blocked during synthetic tests."""


def need(value: object, message: str) -> None:
    if value is not True:
        raise RepairError(message)


def sha256(value: bytes) -> str:
    need(type(value) is bytes, "hash only exact immutable bytes")
    return hashlib.sha256(value).hexdigest()


def checked_sha256(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value), "reject an unpinned, noncanonical, or substituted SHA-256: " + label)
    return value


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject an ambiguous source-freeze machine document") from exc


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    need(type(raw) is bytes and 0 < len(raw) <= LIMIT, "reject oversized, empty, or non-byte evidence: " + label)

    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            need(type(key) is str and key not in result, "reject duplicate evidence fields: " + label)
            result[key] = value
        return result

    def nonfinite(value: str) -> Any:
        raise RepairError("reject nonfinite source-freeze evidence: " + value)

    try:
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=pairs, parse_constant=nonfinite)
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject malformed source-freeze evidence: " + label) from exc
    need(type(value) is dict and canonical(value) == raw, "reject a noncanonical machine evidence owner: " + label)
    return value


def checked_relative(path: object) -> tuple[str, ...]:
    need(type(path) is str and 0 < len(path) <= 512 and "\\" not in path and "\x00" not in path, "reject an escaped relative owner")
    parsed = PurePosixPath(path)
    need(not parsed.is_absolute() and str(parsed) == path and 0 < len(parsed.parts) <= 12 and all(part not in ("", ".", "..") for part in parsed.parts), "reject an absolute, ambiguous, or broadened source owner")
    return parsed.parts


def runtime() -> None:
    need(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6) and sys.flags.isolated == 1 and sys.dont_write_bytecode is True and os.path.abspath(sys.executable) == PYTHON and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE), "require the exact isolated, bytecode-free, stable CPython 3.14.6 source-freeze process")
    need(os.path.abspath(oracle_re.__file__) == INSTALLED_RE.path and os.path.abspath(oracle_re._compiler.__file__) == INSTALLED_COMPILER.path and os.path.abspath(oracle_re._constants.__file__) == INSTALLED_CONSTANTS.path, "authenticate installed CPython re before considering the separate upstream test source")
    need(not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "never import a candidate into a source-freeze or stdlib-only oracle process")


def owner_document(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size}


def read_owner(owner: Owner, *, external: bool = False) -> tuple[bytes, dict[str, Any]]:
    checked_sha256(owner.sha256, owner.path)
    need(type(owner.size) is int and 0 < owner.size <= LIMIT, "reject an oversized or unbounded authenticated owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    folders: list[int] = []
    handle: int | None = None
    try:
        if external:
            allowed = {UPSTREAM_TEST.path, INSTALLED_RE.path, INSTALLED_COMPILER.path, INSTALLED_CONSTANTS.path}
            need(owner.path in allowed, "never inspect a substituted upstream or host stdlib path")
            handle = os.open(owner.path, flags)
            visible = os.stat(owner.path, follow_symlinks=False)
        else:
            parts = checked_relative(owner.path)
            if parts[0] == "candidates":
                need(owner.path in {item.path for item in RUST_OWNERS}, "never read a Rust native target or another candidate family")
            if owner.path.endswith(".gz"):
                need(owner == RUST_ARCHIVE, "never open another compressed candidate or performance archive")
            folder = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
            folders.append(folder)
            for name in parts[:-1]:
                folder = os.open(name, flags | getattr(os, "O_DIRECTORY", 0), dir_fd=folder)
                folders.append(folder)
            handle = os.open(parts[-1], flags, dir_fd=folder)
            visible = os.stat(parts[-1], dir_fd=folder, follow_symlinks=False)
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid() and before.st_nlink == 1 and before.st_size == owner.size and (before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink) == (visible.st_dev, visible.st_ino, visible.st_size, visible.st_uid, visible.st_nlink), "reject a linked, foreign, truncated, symlinked, or exchanged immutable owner: " + owner.path)
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(handle, min(remaining, 1024 * 1024))
            need(type(chunk) is bytes and bool(chunk), "reject truncated authenticated source evidence")
            chunks.append(chunk)
            remaining -= len(chunk)
        need(os.read(handle, 1) == b"", "reject appended authenticated source evidence")
        raw = b"".join(chunks)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_uid, after.st_nlink, after.st_mtime_ns, after.st_ctime_ns) and sha256(raw) == owner.sha256, "reject an owner altered during descriptor-bound authentication: " + owner.path)
        return raw, {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size, "device": after.st_dev, "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode), "uid": after.st_uid, "nlink": after.st_nlink}
    finally:
        if handle is not None:
            os.close(handle)
        for folder in reversed(folders):
            os.close(folder)


def repair_block_documents() -> list[dict[str, Any]]:
    return [{"name": name, "original_sha256": sha256(before), "original_bytes": len(before), "derived_sha256": sha256(after), "derived_bytes": len(after), "original_occurrence_count": 1, "derived_occurrence_count": 1} for name, before, after in REPAIR_BLOCKS]


def repaired_source(raw: bytes, *, frozen: bool, flag_block: bytes = CORRECTED_FLAG_BLOCK) -> bytes:
    need(type(raw) is bytes and 0 < len(raw) <= LIMIT, "require one complete original first-party Rust Python adapter")
    if frozen:
        need(len(raw) == ORIGINAL_BYTES and sha256(raw) == ORIGINAL_SHA256, "reject a substituted original Rust public source")
    blocks = ((REPAIR_BLOCKS[0][0], OLD_FLAG_BLOCK, flag_block), REPAIR_BLOCKS[1], REPAIR_BLOCKS[2])
    derived = raw
    for name, before, after in blocks:
        need(derived.count(before) == 1 and derived.count(after) == 0, "require one uniquely anchored unmodified Rust public block: " + name)
        offset = derived.index(before)
        prefix, suffix = derived[:offset], derived[offset + len(before):]
        derived = prefix + after + suffix
        need(derived.startswith(prefix) and derived.endswith(suffix) and derived.count(before) == 0 and derived.count(after) == 1, "never alter bytes outside the exact anchored Rust public block: " + name)
    for marker in (b"return _cache2[type(pattern), pattern, flags]", b"key = (type(pattern), pattern, flags)", b"def _template(", b"def _cached_template(", b"def _restore_owned_generic_alias(", b"class Scanner:", b"_rust_bridge.set_template(_template)", b"__all__ = "):
        need(raw.count(marker) == 1 and derived.count(marker) == 1, "preserve the owned Rust cache, templates, scanner, and exports")
    reduce_count = 2 if frozen else 1
    need(raw.count(b"def __reduce__(self):") == reduce_count and derived.count(b"def __reduce__(self):") == reduce_count, "preserve every original Rust pickle policy")
    for forbidden in (b"import re\n", b"from re import", b"import _sre", b"from _sre", b"regex.compile", b"pcre", b"oniguruma", b"candidates.vm_candidate", b"candidates.zig_candidate", b"candidates.cpp_candidate", b"candidates.go_candidate", b"candidates.fortran_candidate", b"subprocess", b"ctypes"):
        need(derived.count(forbidden) == raw.count(forbidden), "never introduce stdlib re, an external regex engine, fallback, or another family")
    try:
        tree = ast.parse(derived.decode("utf-8", "strict"), filename="private-snapshot/candidates/rust_candidate.py")
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise RepairError("reject an invalid corrected first-party Rust public source") from exc
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    need(set(("RegexFlag", "PatternError", "Pattern")) <= set(classes), "preserve all three first-party Rust public classes")
    need(derived.count(b'return f"re.RegexFlag({value})"') == 1 and derived.count(b'if rendered.startswith("re.RegexFlag(")') == 1 and derived.count(b"rendered = hex(flags)") == 1 and derived.count(b"return (self.pattern, self.flags) == (other.pattern, other.flags)") == 1 and derived.count(b"return hash((self.pattern, self.flags))") == 1, "retain every frozen V1 pure-unknown, value-equality, and owned-pattern repair")
    error = classes["PatternError"]
    module = [item for item in error.body if isinstance(item, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__module__" for target in item.targets)]
    need(len(module) == 1 and isinstance(module[0].value, ast.Constant) and module[0].value.value == "re", "preserve the V1-owned public PatternError module")
    if frozen and flag_block == CORRECTED_FLAG_BLOCK:
        need(len(derived) == DERIVED_BYTES and sha256(derived) == DERIVED_SHA256, "freeze only the independently reproduced exact corrected Rust public source")
    if frozen and flag_block == V1_BAD_FLAG_BLOCK:
        need(len(derived) == DERIVED_BYTES and sha256(derived) == V1_DERIVED_SHA256, "authenticate the actual historical failing V1 Rust public source")
    return derived


def baseline() -> dict[str, Any]:
    return {"full_case_denominator": CASE_DENOMINATOR, "suite_count": SUITE_COUNT, "private_waiver_count": PRIVATE_WAIVER_COUNT, "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS, "authenticated_reference_count": CURRENT_HISTORY_REFERENCES, "qualified_candidate_count": 0, "rust_status": "FAIL", "rust_workers": 13, "rust_mismatches": 1087, "rust_passing_cases": 7438, "rust_infrastructure_failures": 0, "c_status": "FAIL", "c_mismatches": 1230, "c_passing_cases": 7325, "historical_c_mismatches": 1262, "historical_c_passing_cases": 7325, "zig_status": "FAIL", "zig_mismatches": 2172, "zig_passing_cases": 2847, "zig_preflight_workers": 0, "rust_source_owner_count": 9, "cargo_package_count": 1, "external_regex_dependency_count": 0, "cross_family_dependency_count": 0, "candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "final_holdout_opened": False, "final_comparison_cases_generated": False, "final_comparison_planned_case_count": 4194304, "source_apply_count": 0, "candidate_workers_started": 0, "native_activations": 0, "workspace_mutations": 0, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_c_archive_bytes_read": 0, "uncompressed_zig_archive_bytes_read": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "winner_selected": False}


def validate_baseline(value: object) -> None:
    need(type(value) is dict and value == baseline(), "reject altered current V30 history, any candidate qualification, stale denominators, weakened no-delegation policy, premature timing, archive inflation, or an opened final holdout")


def observed_failure() -> dict[str, Any]:
    return {"archive": owner_document(RUST_ARCHIVE), "actual_archive_compressed_bytes": RUST_ARCHIVE.size, "previous_bounded_compressed_bytes_read": 57344, "previous_bounded_compressed_bytes_consumed": 55267, "previous_bounded_uncompressed_bytes_read": 1048576, "previous_bounded_uncompressed_limit": 1048576, "previous_bounded_uncompressed_prefix_sha256": "5cdf8809d277b4efbe908b67be9b11aa318eb7ed982318859a321411ae3f1bc7", "full_archive_decompressed": False, "full_archive_json_parsed": False, "suite_results_uncompressed_offset": 6273, "first_actual_mismatch_uncompressed_offset": 7270, "first_actual_mismatch_entry_end_offset": 8352, "suite": "original_bounded_v5", "suite_case_execution_denominator": 151, "suite_actual_mismatch_count": 1, "failure_class": "SEMANTIC MISMATCH", "test": "PatternReprTests.test_flags_repr", "original_test_line": 2887, "upstream_method_start_line": 2881, "upstream_method_end_line": 2893, "upstream_method_source_sha256": UPSTREAM_METHOD_SHA256, "upstream_method_ast_sha256": UPSTREAM_METHOD_AST_SHA256, "actual": OBSERVED_ACTUAL, "expected": OBSERVED_EXPECTED, "other_rust_failure_root_causes": "NOT MEASURED", "corrected_candidate_matching": "NOT MEASURED", "source_only_gates_reopen_compressed_archive_for_decompression": False}


def boundary() -> dict[str, Any]:
    return {"candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "qualified_candidate_count": 0, "candidate_imports": 0, "candidate_workers_started": 0, "reference_processes_started": 0, "upstream_test_processes_started": 0, "upstream_unittest_methods_executed": 0, "source_builds_started": 0, "compiler_processes_started": 0, "native_activations": 0, "native_libraries_loaded": 0, "recovery_locks_acquired": 0, "recovery_journals_created": 0, "signal_handlers_installed": 0, "signal_masks_installed": 0, "network_requests": 0, "threads_started": 0, "source_apply_count": 0, "workspace_mutations": 0, "canonical_native_target_reads": 0, "canonical_native_target_stats": 0, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_c_archive_bytes_read": 0, "uncompressed_zig_archive_bytes_read": 0, "benchmark_files_read": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "final_holdout_opened": False, "final_comparison_cases_generated": False, "winner_selected": False}


def contract_document(source: str, protocol: str) -> dict[str, Any]:
    checked_sha256(source, "version 2 source")
    checked_sha256(protocol, "version 2 protocol")
    return {"schema": SCHEMA + "-source-freeze", "version": 2, "phase": "SOURCE FREEZE; NO APPLICATION, BUILD, OR CANDIDATE RUN", "source": {"path": SOURCE_RELATIVE, "sha256": source}, "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol}, "goal": owner_document(GOAL), "phase_one": owner_document(PHASE_ONE), "runtime": {"implementation": "cpython", "version": "3.14.6", "python": PYTHON, "python_sha256": PYTHON_SHA256, "isolated": True, "bytecode_writes": False}, "upstream_oracle": {"committed_test": owner_document(COMMITTED_UPSTREAM_TEST), "separately_located_upstream_test": owner_document(UPSTREAM_TEST), "separately_installed_re": [owner_document(INSTALLED_RE), owner_document(INSTALLED_COMPILER), owner_document(INSTALLED_CONSTANTS)], "upstream_test_module_in_installed_stdlib": False, "upstream_re_assumed": False, "test_name": "PatternReprTests.test_flags_repr", "official_assertion_count": 6, "official_expected_representations": list(OFFICIAL_EXPECTATIONS), "method_source_sha256": UPSTREAM_METHOD_SHA256, "method_ast_sha256": UPSTREAM_METHOD_AST_SHA256, "canonical_known_flag_order": list(CANONICAL_FLAG_ORDER), "source_only_upstream_unit_execution": "NOT RUN", "pure_unknown_1024": "re.RegexFlag(1024)", "mixed_unknown_1280": "re.ASCII|0x400", "zero": "re.NOFLAG"}, "observed_actual_rust_failure": observed_failure(), "preserved_v1": {"owners": [owner_document(item) for item in V1], "actual_incorrect_derived_source_sha256": V1_DERIVED_SHA256, "actual_incorrect_flag_block_sha256": "de034e8441955e2f77a90c2c0261b4d537329cdcec43d1be8c6d486d3630ec0f", "historical_tool_modified": False, "historical_protocol_modified": False, "historical_contract_modified": False, "historical_matching_failure_hidden": False, "v1_verify_context_called": False}, "rust_source": {"family": "rust", "owner_count": len(RUST_OWNERS), "owners": [owner_document(item) for item in RUST_OWNERS], "cargo_lock_package_count": 1, "external_regex_dependency_count": 0, "cross_family_dependency_count": 0, "stdlib_re_delegation_allowed": False, "native_parser_compiler_executor_modified": False, "native_bridge_modified": False}, "repair": {"original": {"path": "candidates/rust_candidate.py", "sha256": ORIGINAL_SHA256, "bytes": ORIGINAL_BYTES, "modified": False}, "derived": {"path": "candidates/rust_candidate.py", "sha256": DERIVED_SHA256, "bytes": DERIVED_BYTES, "materialized": False}, "anchored_block_count": 3, "blocks": repair_block_documents(), "known_flag_order": list(CANONICAL_FLAG_ORDER), "only_v1_change": "CORRECT EIGHT KNOWN FLAG ORDER ENTRIES", "preserve_pure_unknown": True, "preserve_mixed_unknown": True, "preserve_noflag": True, "preserve_v1_public_error": True, "preserve_v1_pattern_equality": True, "preserve_v1_pattern_hash": True, "preserve_v1_pattern_repr": True, "preserve_type_sensitive_cache": True, "preserve_all_native_rust_source": True, "external_regex_package_added": False, "stdlib_regex_engine_added": False, "cross_family_source_added": False, "candidate_matching_proven": False}, "published_history": {"v30": [owner_document(item) for item in V30], "rust_actual_failure_receipt": owner_document(RUST_RECEIPT), "rust_actual_failure_raw_archive": owner_document(RUST_ARCHIVE), "c_actual_failure_receipt": owner_document(C_RECEIPT), "zig_actual_failure_receipt": owner_document(ZIG_RECEIPT), "zig_preflight_failure_receipt": owner_document(ZIG_PREFLIGHT_RECEIPT), "current": baseline()}, "apply_policy": {"explicit_apply_required": True, "independent_derived_sha256_required": True, "independent_derived_bytes_required": True, "snapshot_root_required": True, "private_parent": "/tmp", "private_root_prefix": PRIVATE_ROOT_PREFIX, "private_root_required_family_component": PRIVATE_ROOT_FAMILY, "phase_names": list(PHASE_NAMES), "private_directory_mode": "0700", "private_file_mode": "0600", "destination_relative": "source/candidates/rust_candidate.py", "creation_mode": "O_CREAT | O_EXCL | O_NOFOLLOW", "two_distinct_phase_directories_required": True, "existing_destination": "FORBIDDEN", "canonical_worktree_destination": "FORBIDDEN", "other_family_destination": "FORBIDDEN", "candidate_activation": "FORBIDDEN", "source_build": "FORBIDDEN"}, "phase_boundary": boundary()}


class SourceWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {name: 0 for name in ("filesystem", "write", "process", "import", "network", "thread", "clock", "native", "lock", "signal", "decompression")}

    def deny(self, owner: Any, name: str, category: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise ForbiddenEffect("physically blocked source-only " + category + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceWall:
        for owner, names, category in (
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
            (gzip, ("open", "decompress"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        ):
            for name in names:
                self.deny(owner, name, category)
        return self

    def __exit__(self, *_args: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def sample_source() -> bytes:
    return (
        b"import enum\n\nclass RegexFlag(enum.IntFlag):\n"
        b"    NOFLAG = 0\n    ASCII = A = 256\n    IGNORECASE = I = 2\n"
        b"    LOCALE = L = 4\n    UNICODE = U = 32\n    MULTILINE = M = 8\n"
        b"    DOTALL = S = 16\n    VERBOSE = X = 64\n    DEBUG = 128\n"
        b"    _numeric_repr_ = hex\n    def __repr__(self):\n"
        b"        value = int(self)\n        if not value:\n            return \"re.NOFLAG\"\n"
        + OLD_FLAG_BLOCK
        + b"\n" + OLD_ERROR_BLOCK
        + b"        super().__init__(msg)\n\nclass _PatternType(type):\n    pass\n\nclass Pattern(metaclass=_PatternType):\n"
        + OLD_EQUALITY_BLOCK
        + b"\n    def __reduce__(self):\n        return None\n    def _cached_template(self):\n        return None\n\ndef _template():\n    return None\n\ndef _restore_owned_generic_alias():\n    return None\n\nclass Scanner:\n    pass\n\ndef example(pattern, flags):\n    key = (type(pattern), pattern, flags)\n    return _cache2[type(pattern), pattern, flags]\n\ndef registration():\n    _rust_bridge.set_template(_template)\n\n__all__ = []\n"
    )


def synthetic_flag_class(source: bytes) -> type[enum.IntFlag]:
    tree = ast.parse(source.decode("utf-8", "strict"), filename="in-memory-owned-rust-flag-witness")
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RegexFlag"]
    need(len(classes) == 1, "require exactly one synthetic first-party Rust flag class")
    module = ast.Module(body=[classes[0]], type_ignores=[])
    namespace: dict[str, Any] = {"enum": enum, "__name__": SCHEMA + "_synthetic"}
    exec(compile(ast.fix_missing_locations(module), "<synthetic-owned-rust-flag-v2>", "exec", dont_inherit=True), namespace)
    result = namespace["RegexFlag"]
    need(isinstance(result, enum.EnumType) and issubclass(result, enum.IntFlag), "require one actual synthetic-owned IntFlag")
    return result


def verify_flag_vectors(corrected: type[enum.IntFlag]) -> dict[str, Any]:
    values = (
        corrected.I,
        corrected.I | corrected.S | corrected.X,
        corrected.I | corrected.S | corrected.X | (1 << 20),
        ~corrected.I,
        ~(corrected.I | corrected.S | corrected.X),
        ~(corrected.I | corrected.S | corrected.X | (1 << 20)),
    )
    results = tuple(repr(value) for value in values)
    need(results == OFFICIAL_EXPECTATIONS, "reject any changed genuine CPython six-vector flag witness")
    need(repr(corrected(0)) == "re.NOFLAG" and repr(corrected(1024)) == "re.RegexFlag(1024)" and repr(corrected(1280)) == "re.ASCII|0x400", "never regress zero, pure-unknown, or mixed-unknown V1 compatibility")
    sparse = (-((1 << 30) + 1), -(1 << 20), 1 << 20, (1 << 20) | 44, (1 << 30), (1 << 30) | 256, (1 << 30) | 2 | 64)
    count = 0
    for value in (*range(-1024, 4097), *sparse):
        need(repr(corrected(value)) == repr(oracle_re.RegexFlag(value)), "reject a real isolated-stdlib RegexFlag representation mismatch: " + str(value))
        count += 1
    need(count == 5128, "never silently change the exhaustive isolated-reference denominator")
    return {"official_source_vector_count": len(results), "actual_isolated_stdlib_vector_count": count, "pure_unknown_1024": repr(corrected(1024)), "mixed_unknown_1280": repr(corrected(1280)), "noflag": repr(corrected(0)), "inverted_ignorecase": results[3], "known_order": list(CANONICAL_FLAG_ORDER)}


def validate_upstream_test(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8", "strict")
        tree = ast.parse(text, filename=UPSTREAM_TEST.path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise RepairError("reject the actual frozen upstream CPython test source") from exc
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "PatternReprTests"]
    need(len(classes) == 1, "authenticate the one genuine upstream PatternReprTests class")
    methods = [node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == "test_flags_repr"]
    need(len(methods) == 1, "authenticate the one genuine upstream six-assertion flag test")
    method = methods[0]
    segment = ast.get_source_segment(text, method)
    need(type(segment) is str and method.lineno == 2881 and method.end_lineno == 2893 and sha256(segment.encode("utf-8")) == UPSTREAM_METHOD_SHA256 and sha256(ast.dump(method, include_attributes=False).encode("utf-8")) == UPSTREAM_METHOD_AST_SHA256, "reject a substituted or reconstructed upstream flag-test method")
    expected: list[str] = []
    for item in method.body:
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
            call = item.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "assertEqual" and len(call.args) >= 2 and isinstance(call.args[1], ast.Constant) and isinstance(call.args[1].value, str):
                expected.append(call.args[1].value)
    need(tuple(expected) == OFFICIAL_EXPECTATIONS, "derive the exact six expectations from genuine upstream test AST")
    return {"test": "PatternReprTests.test_flags_repr", "source_path": UPSTREAM_TEST.path, "source_sha256": UPSTREAM_TEST.sha256, "start_line": method.lineno, "end_line": method.end_lineno, "method_source_sha256": UPSTREAM_METHOD_SHA256, "method_ast_sha256": UPSTREAM_METHOD_AST_SHA256, "official_assertion_count": len(expected), "official_expected_representations": expected, "unit_test_executed": False}


def self_test(source_pin: str, protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    expected_contract = contract_document(source_pin, protocol_pin)
    need(sha256(canonical(expected_contract)) == checked_sha256(contract_pin, "V2 canonical contract"), "reject a source-only substituted canonical V2 contract")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: bool) -> None:
        need(condition, "rejected required source-only positive control: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (RepairError, OSError, ValueError, TypeError, SyntaxError, UnicodeError, RecursionError, OverflowError):
            rejected.append(name)
            return
        raise RepairError("accepted hostile source-only evidence: " + name)

    with SourceWall() as wall:
        original = sample_source()
        fixed = repaired_source(original, frozen=False)
        wrong = repaired_source(original, frozen=False, flag_block=V1_BAD_FLAG_BLOCK)
        candidate = synthetic_flag_class(fixed)
        historical = synthetic_flag_class(wrong)
        vectors = verify_flag_vectors(candidate)
        accept("reproduce all six genuine upstream AST witness vectors", vectors["official_source_vector_count"] == 6)
        accept("compare all 5,128 real pinned-stdlib vectors", vectors["actual_isolated_stdlib_vector_count"] == 5128)
        accept("reproduce the actual first archived V1 failure", repr(~historical.I) == OBSERVED_ACTUAL)
        accept("correct the exact actual first archived V1 failure", repr(~candidate.I) == OBSERVED_EXPECTED)
        accept("preserve zero NOFLAG representation", vectors["noflag"] == "re.NOFLAG")
        accept("preserve a purely unknown decimal flag", vectors["pure_unknown_1024"] == "re.RegexFlag(1024)")
        accept("preserve a mixed known and unknown hexadecimal flag", vectors["mixed_unknown_1280"] == "re.ASCII|0x400")
        accept("freeze all eight actual CPython flag names", vectors["known_order"] == list(CANONICAL_FLAG_ORDER))
        accept("retain all three independent V1 source repairs", len(REPAIR_BLOCKS) == 3)
        accept("preserve the true current 149 owners and 154 references", baseline()["repository_evidence_owner_count"] == 149 and baseline()["authenticated_reference_count"] == 154)
        accept("preserve the current actual Rust C and Zig failures", baseline()["rust_mismatches"] == 1087 and baseline()["c_mismatches"] == 1230 and baseline()["zig_mismatches"] == 2172)
        accept("preserve previous C separately", baseline()["historical_c_mismatches"] == 1262)
        accept("preserve original full obligations", len(SUITES) == SUITE_COUNT and sum(total for _, total in SUITES) == CASE_DENOMINATOR)
        accept("never claim candidate matching or speed", baseline()["candidate_correctness"] == "NOT MEASURED" and baseline()["performance"] == "NOT MEASURED")
        accept("leave the actual holdout unopened", baseline()["holdout"] == "NOT OPENED" and baseline()["final_holdout_opened"] is False)
        validate_baseline(baseline())
        for name, before, after in REPAIR_BLOCKS:
            accept("preserve unique anchored block: " + name, fixed.count(before) == 0 and fixed.count(after) == 1)
            for label, hostile in (("missing", original.replace(before, b"# removed\n")), ("duplicate", original.replace(before, before + before)), ("already changed", original.replace(before, after))):
                reject("reject " + label + " anchored " + name, lambda data=hostile: repaired_source(data, frozen=False))
        reject("reject actual V1 incorrect known-bit order", lambda: need(repr(~historical.I) == OBSERVED_EXPECTED, "actual V1 order differs"))
        reject("reject wrong 5,128-vector oracle", lambda: verify_flag_vectors(historical))
        reject("reject synthetic source as canonical candidate", lambda: repaired_source(original, frozen=True))
        for marker in (b"return _cache2[type(pattern), pattern, flags]", b"key = (type(pattern), pattern, flags)", b"def _template(", b"def _cached_template(", b"def _restore_owned_generic_alias(", b"class Scanner:", b"_rust_bridge.set_template(_template)", b"__all__ = "):
            hostile = original.replace(marker, b"forbidden_unowned_policy")
            reject("reject changed native cache, scanner, template, or export anchor", lambda data=hostile: repaired_source(data, frozen=False))
        for fingerprint in ("", "0" * 63, "0" * 65, "A" * 64, "z" * 64, None, 0, True):
            reject("reject hostile independent digest", lambda value=fingerprint: checked_sha256(value, "hostile"))
        for path in ("", "/tmp/escaped", "../escaped", "a/../b", "a//b", "a/./b", "./a", "a/", "a\\b", "x" * 513):
            reject("reject hostile source-owner path", lambda value=path: checked_relative(value))
        for raw in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n', b"[]\n", b'{"x":1}', b"", b"null\n"):
            reject("reject noncanonical hostile history", lambda data=raw: strict_json(data, "hostile"))
        for key, bad in (("full_case_denominator", 31236), ("suite_count", 12), ("private_waiver_count", 12), ("repository_evidence_owner_count", 105), ("authenticated_reference_count", 110), ("qualified_candidate_count", 1), ("rust_status", "PASS"), ("rust_mismatches", 0), ("rust_passing_cases", 7461), ("c_mismatches", 1262), ("c_passing_cases", 7357), ("historical_c_mismatches", 1230), ("zig_mismatches", 0), ("zig_preflight_workers", 1), ("rust_source_owner_count", 8), ("cargo_package_count", 2), ("external_regex_dependency_count", 1), ("cross_family_dependency_count", 1), ("candidate_correctness", "PASS"), ("candidate_qualified", True), ("performance", "FASTER"), ("memory", "ZERO"), ("undefined_behavior", "PASS"), ("holdout", "OPENED"), ("final_holdout_opened", True), ("final_comparison_cases_generated", True), ("source_apply_count", 1), ("candidate_workers_started", 1), ("native_activations", 1), ("workspace_mutations", 1), ("uncompressed_rust_archive_bytes_read", 1), ("hidden_cases_read", 1), ("clock_samples", 1), ("timing_trials_run", 1), ("winner_selected", True)):
            changed = baseline()
            changed[key] = bad
            reject("reject altered actual baseline: " + key, lambda value=changed: validate_baseline(value))
        probes = (
            ("filesystem", lambda: builtins.open("/tmp/rebar-v2-forbidden", "rb")),
            ("filesystem", lambda: io.open("/tmp/rebar-v2-forbidden", "rb")),
            ("filesystem", lambda: os.open("/tmp/rebar-v2-forbidden", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("/tmp/rebar-v2-forbidden")),
            ("filesystem", lambda: Path("/tmp/rebar-v2-forbidden").read_bytes()),
            ("write", lambda: os.write(-1, b"forbidden")),
            ("write", lambda: tempfile.mkdtemp()),
            ("process", lambda: subprocess.run(("rebar-v2-forbidden",))),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("import", lambda: importlib.import_module("re")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("native", lambda: ctypes.CDLL("rebar-v2-forbidden")),
            ("lock", lambda: fcntl.flock(-1, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden")),
            ("decompression", lambda: zlib.decompress(b"forbidden")),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            reject("physically block " + kind, action)
            need(wall.blocked[kind] == before + 1, "prove that a real source-only effect was blocked")
        blocked = dict(wall.blocked)
    need(len(rejected) >= 75 and all(amount > 0 for amount in blocked.values()), "require exhaustive hostile history and every physically blocked source effect")
    return {"schema": SCHEMA + "-source-only-self-test", "status": "PASS", "version": 2, "mode": "SYNTHETIC SOURCE ONLY", "source_sha256": source_pin, "protocol_sha256": protocol_pin, "contract_sha256": contract_pin, "accepted_control_count": len(accepted), "rejected_hostile_control_count": len(rejected), "blocked_effects_by_kind": blocked, "official_flag_vector_count": vectors["official_source_vector_count"], "actual_isolated_stdlib_flag_vector_count": vectors["actual_isolated_stdlib_vector_count"], "actual_observed_failure_reproduced": True, "actual_observed_failure_corrected_in_synthetic_source": True, "pure_unknown_preserved": True, "mixed_unknown_preserved": True, "noflag_preserved": True, "derived_source_sha256": DERIVED_SHA256, "derived_source_bytes": DERIVED_BYTES, "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_DENOMINATOR, "named_private_waiver_count": PRIVATE_WAIVER_COUNT, "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS, "authenticated_digest_addressed_history_paths": CURRENT_HISTORY_REFERENCES, "actual_rust_semantic_mismatch_count": 1087, "actual_rust_verified_passing_case_count": 7438, "actual_c_semantic_mismatch_count": 1230, "actual_c_verified_passing_case_count": 7325, "historical_c_semantic_mismatch_count": 1262, "actual_zig_semantic_mismatch_count": 2172, "historical_zig_preflight_candidate_workers": 0, **boundary()}


def read_contract_owners(source_pin: str, protocol_pin: str, contract_pin: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source_owner = Owner(SOURCE_RELATIVE, checked_sha256(source_pin, "source"), os.stat(str(ROOT / SOURCE_RELATIVE), follow_symlinks=False).st_size)
    protocol_owner = Owner(PROTOCOL_RELATIVE, checked_sha256(protocol_pin, "protocol"), os.stat(str(ROOT / PROTOCOL_RELATIVE), follow_symlinks=False).st_size)
    contract_owner = Owner(CONTRACT_RELATIVE, checked_sha256(contract_pin, "contract"), os.stat(str(ROOT / CONTRACT_RELATIVE), follow_symlinks=False).st_size)
    source_raw, source_actual = read_owner(source_owner)
    protocol_raw, protocol_actual = read_owner(protocol_owner)
    contract_raw, contract_actual = read_owner(contract_owner)
    need(len(source_raw) == source_owner.size and len(protocol_raw) == protocol_owner.size, "authenticate complete frozen V2 source and protocol")
    expected = contract_document(source_pin, protocol_pin)
    need(strict_json(contract_raw, "V2 canonical source contract") == expected and sha256(canonical(expected)) == contract_pin, "authenticate the exact caller-pinned canonical V2 contract")
    return expected, [source_actual, protocol_actual, contract_actual]


def validate_v1(v1_raw: bytes, contract_raw: bytes) -> None:
    frozen = strict_json(contract_raw, "immutable historical V1 source freeze")
    need(frozen.get("schema") == "rebar-phase2-owned-rust-public-contract-source-repair-v1-source-freeze" and frozen.get("phase") == "SOURCE FREEZE; NO BUILD OR CANDIDATE RUN", "preserve the immutable historical Rust V1 source freeze")
    repair = frozen.get("repair")
    need(isinstance(repair, dict) and repair.get("derived", {}).get("sha256") == V1_DERIVED_SHA256 and repair.get("derived", {}).get("bytes") == DERIVED_BYTES and repair.get("derived", {}).get("materialized") is False and repair.get("original", {}).get("sha256") == ORIGINAL_SHA256 and repair.get("anchored_block_count") == 3, "preserve all exact previous derived V1 owner claims")
    blocks = repair.get("blocks")
    need(isinstance(blocks, list) and len(blocks) == 3 and blocks[0].get("derived_sha256") == sha256(V1_BAD_FLAG_BLOCK) and blocks[1].get("derived_sha256") == sha256(NEW_ERROR_BLOCK) and blocks[2].get("derived_sha256") == sha256(NEW_EQUALITY_BLOCK), "preserve the real incorrect V1 flag order and the two unchanged V1 repair blocks")
    try:
        tree = ast.parse(v1_raw.decode("utf-8", "strict"), filename=V1[0].path)
        values: dict[str, bytes] = {}
        names = {"OLD_FLAG_BLOCK", "NEW_FLAG_BLOCK", "OLD_ERROR_BLOCK", "NEW_ERROR_BLOCK", "OLD_EQUALITY_BLOCK", "NEW_EQUALITY_BLOCK"}
        for item in tree.body:
            if isinstance(item, ast.Assign) and len(item.targets) == 1 and isinstance(item.targets[0], ast.Name) and item.targets[0].id in names:
                need(item.targets[0].id not in values, "reject a duplicated V1 anchored source block")
                values[item.targets[0].id] = ast.literal_eval(item.value)
    except (SyntaxError, TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject an altered immutable V1 source repair") from exc
    expected = {"OLD_FLAG_BLOCK": OLD_FLAG_BLOCK, "NEW_FLAG_BLOCK": V1_BAD_FLAG_BLOCK, "OLD_ERROR_BLOCK": OLD_ERROR_BLOCK, "NEW_ERROR_BLOCK": NEW_ERROR_BLOCK, "OLD_EQUALITY_BLOCK": OLD_EQUALITY_BLOCK, "NEW_EQUALITY_BLOCK": NEW_EQUALITY_BLOCK}
    need(values == expected, "derive V2 from genuine exact V1 block bytes without invoking V1 verification")


def validate_history(summary: dict[str, Any], inputs: dict[str, Any], rust: dict[str, Any], c: dict[str, Any], zig: dict[str, Any], preflight: dict[str, Any], raw_archive: dict[str, Any]) -> None:
    need(summary.get("schema") == "rebar-candidate-current-overview-v30-summary" and summary.get("status") == "PASS" and summary.get("full_case_denominator") == CASE_DENOMINATOR and summary.get("suite_count") == SUITE_COUNT and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT and summary.get("repository_evidence_owner_count") == CURRENT_EVIDENCE_OWNERS and summary.get("authenticated_digest_addressed_history_paths") == CURRENT_HISTORY_REFERENCES and summary.get("qualified_candidate_count") == 0 and summary.get("c_original_campaign_status") == "FAIL" and summary.get("c_original_campaign_semantic_mismatch_count") == 1230 and summary.get("c_original_campaign_verified_passing_case_count") == 7325 and summary.get("historical_c_semantic_mismatch_count") == 1262 and summary.get("historical_c_verified_passing_case_count") == 7325 and summary.get("rust_original_campaign_status") == "FAIL" and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087 and summary.get("rust_original_campaign_verified_passing_case_count") == 7438 and summary.get("zig_original_campaign_status") == "FAIL" and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172 and summary.get("zig_original_campaign_verified_passing_case_count") == 2847 and summary.get("historical_zig_preflight_failure", {}).get("actual_candidate_workers") == 0 and summary.get("final_comparison_planned_case_count") == 4194304 and summary.get("final_comparison_cases_generated") is False and summary.get("final_holdout_opened") is False and summary.get("performance") == "NOT MEASURED" and summary.get("memory") == "NOT MEASURED" and summary.get("confidence_intervals") == "NOT MEASURED" and summary.get("undefined_behavior") == "NOT MEASURED" and summary.get("hidden_cases_read") == 0 and summary.get("clock_samples") == 0 and summary.get("timing_trials_run") == 0 and summary.get("winner_selected") is False, "preserve the exact current 149/154 V30 truth and all genuine Rust, C, and Zig losses")
    need(inputs.get("schema") == "rebar-candidate-current-overview-v30-inputs" and inputs.get("version") == 30 and inputs.get("full_case_denominator") == CASE_DENOMINATOR and inputs.get("suite_count") == SUITE_COUNT and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT and inputs.get("repository_evidence_owner_count") == CURRENT_EVIDENCE_OWNERS and inputs.get("all_digest_addressed_history_path_count") == CURRENT_HISTORY_REFERENCES and inputs.get("candidate_qualified_count") == 0 and inputs.get("c_original_campaign_status") == "FAIL" and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230 and inputs.get("c_original_campaign_verified_passing_case_count") == 7325 and inputs.get("historical_c_semantic_mismatch_count") == 1262 and inputs.get("actual_rust_semantic_mismatch_count") == 1087 and inputs.get("actual_rust_verified_passing_case_count") == 7438 and inputs.get("actual_zig_semantic_mismatch_count") == 2172 and inputs.get("final_holdout_opened") is False, "preserve separately authenticated exact V30 graph inputs")
    archive = rust.get("archive")
    need(rust.get("schema") == "rebar-owned-repaired-rust-original-campaign-v3-durable-publication-receipt" and rust.get("status") == "PASS" and rust.get("candidate_status") == "FAIL" and rust.get("family") == "rust" and rust.get("suite_count") == SUITE_COUNT and rust.get("completed_suite_count") == SUITE_COUNT and rust.get("case_execution_denominator") == CASE_DENOMINATOR and rust.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT and rust.get("actual_candidate_workers") == 13 and rust.get("semantic_mismatch_count") == 1087 and rust.get("verified_passing_case_count") == 7438 and rust.get("infrastructure_failure_count") == 0 and rust.get("candidate_qualified") is False and rust.get("recovery_journal_sha256") == RUST_JOURNAL and rust.get("all_four_original_targets_restored") is True and rust.get("restoration_verified_before_publication") is True and isinstance(archive, dict) and archive.get("sha256") == raw_archive["sha256"] and archive.get("size_bytes") == raw_archive["bytes"] and archive.get("device") == raw_archive["device"] and archive.get("inode") == raw_archive["inode"] and archive.get("mode") == 0o600 and archive.get("exclusive_creation") is True and archive.get("streaming_readback_verified") is True and archive.get("file_fsync_completed") is True and archive.get("directory_fsync_completed") is True and rust.get("holdout") == "NOT OPENED" and rust.get("performance") == "NOT MEASURED", "authenticate the real complete 1,087-mismatch Rust failure through raw compressed owner and small receipt only")
    need(c.get("schema") == "rebar-owned-repaired-c-original-campaign-v4-durable-publication-receipt" and c.get("status") == "PASS" and c.get("publication_status") == "PASS" and c.get("publication_pass_means") == "DURABLE PUBLICATION ONLY" and c.get("candidate_status") == "FAIL" and c.get("actual_candidate_workers") == 13 and c.get("completed_suite_count") == SUITE_COUNT and c.get("case_execution_denominator") == CASE_DENOMINATOR and c.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT and c.get("semantic_mismatch_count") == 1230 and c.get("verified_passing_case_count") == 7325 and c.get("infrastructure_failure_count") == 0 and c.get("candidate_execution_failure_count") == 0 and c.get("candidate_qualified") is False and c.get("recovery_journal_sha256") == C_JOURNAL and c.get("exact_original_native_restored") is True and c.get("restoration_verified_before_publication") is True and c.get("holdout") == "NOT OPENED", "preserve the latest first-party C actual failure and recovered original")
    need(zig.get("schema") == "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt" and zig.get("status") == "PASS" and zig.get("candidate_status") == "FAIL" and zig.get("actual_candidate_workers") == 13 and zig.get("completed_suite_count") == SUITE_COUNT and zig.get("case_execution_denominator") == CASE_DENOMINATOR and zig.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT and zig.get("semantic_mismatch_count") == 2172 and zig.get("verified_passing_case_count") == 2847 and zig.get("infrastructure_failure_count") == 0 and zig.get("candidate_qualified") is False and zig.get("holdout") == "NOT OPENED", "preserve the completed genuine 2,172-mismatch Zig failure")
    need(preflight.get("schema") == "rebar-owned-zig-campaign-preflight-failure-v1-durable-publication-receipt" and preflight.get("status") == "PASS" and preflight.get("preserved_failure_status") == "FAIL" and preflight.get("actual_candidate_workers") == 0 and preflight.get("actual_matching_case_execution_count") == 0 and preflight.get("semantic_mismatch_count") == "NOT MEASURED" and preflight.get("holdout") == "NOT OPENED", "preserve the distinct zero-worker Zig preflight without calling it matching")


def verify_context(source_pin: str, protocol_pin: str, contract_pin: str) -> tuple[dict[str, Any], bytes]:
    expected, frozen = read_contract_owners(source_pin, protocol_pin, contract_pin)
    support: list[dict[str, Any]] = []
    raw: dict[str, bytes] = {}
    for owner in (GOAL, PHASE_ONE, COMMITTED_UPSTREAM_TEST, *V1, *V30, *RUST_OWNERS, RUST_ARCHIVE, RUST_RECEIPT, C_RECEIPT, ZIG_RECEIPT, ZIG_PREFLIGHT_RECEIPT):
        payload, actual = read_owner(owner)
        raw[owner.path] = payload
        support.append(actual)
    external: list[dict[str, Any]] = []
    external_raw: dict[str, bytes] = {}
    for owner in (UPSTREAM_TEST, INSTALLED_RE, INSTALLED_COMPILER, INSTALLED_CONSTANTS):
        payload, actual = read_owner(owner, external=True)
        external_raw[owner.path] = payload
        external.append(actual)
    need(raw[COMMITTED_UPSTREAM_TEST.path] == external_raw[UPSTREAM_TEST.path], "bind the upstream source checkout to the byte-identical committed genuine CPython test")
    witness = validate_upstream_test(external_raw[UPSTREAM_TEST.path])
    phase = strict_json(raw[PHASE_ONE.path], "unchanged original P0 matrix")
    denominator = phase.get("denominator")
    need(phase.get("schema") == "rebar-cpython-re-p0-completeness-v1" and isinstance(denominator, dict) and denominator.get("final_required_case_execution_denominator") == CASE_DENOMINATOR and denominator.get("frozen_planned_case_execution_denominator") == CASE_DENOMINATOR and denominator.get("private_upstream_methods_outside_public_denominator") == PRIVATE_WAIVER_COUNT and denominator.get("counted_suite_ids") == [name for name, _ in SUITES], "preserve all thirteen unchanged original P0 suites and named private waivers")
    validate_v1(raw[V1[0].path], raw[V1[2].path])
    original = raw[RUST_OWNERS[-1].path]
    derived = repaired_source(original, frozen=True)
    historical = repaired_source(original, frozen=True, flag_block=V1_BAD_FLAG_BLOCK)
    need(sha256(historical) == V1_DERIVED_SHA256 and sha256(derived) == DERIVED_SHA256 and derived != historical, "derive the actual corrected adapter without modifying the actual failing historical adapter")
    cargo = raw[RUST_OWNERS[1].path].decode("utf-8", "strict")
    lock = raw[RUST_OWNERS[0].path].decode("utf-8", "strict")
    need("[dependencies" not in cargo and "[dev-dependencies" not in cargo and "[build-dependencies" not in cargo and lock.count("[[package]]") == 1 and 'name = "rebar-rust-continuation"' in lock, "reject an external package, delegated engine, or expanded Rust lock")
    baseline_summary = strict_json(raw[V30[2].path], "current V30 summary")
    baseline_inputs = strict_json(raw[V30[1].path], "current V30 inputs")
    rust = strict_json(raw[RUST_RECEIPT.path], "actual Rust durable failure receipt")
    c = strict_json(raw[C_RECEIPT.path], "actual C durable failure receipt")
    zig = strict_json(raw[ZIG_RECEIPT.path], "actual Zig durable failure receipt")
    preflight = strict_json(raw[ZIG_PREFLIGHT_RECEIPT.path], "zero-worker Zig receipt")
    rust_raw = next(item for item in support if item["path"] == RUST_ARCHIVE.path)
    validate_history(baseline_summary, baseline_inputs, rust, c, zig, preflight, rust_raw)
    corrected = synthetic_flag_class(derived)
    wrong = synthetic_flag_class(historical)
    vectors = verify_flag_vectors(corrected)
    need(repr(~wrong.I) == OBSERVED_ACTUAL and repr(~corrected.I) == OBSERVED_EXPECTED, "prove the archived real failure and corrected derived representation without importing the candidate")
    need(not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "never import a candidate during source-only verification")
    outcome = {"schema": SCHEMA + "-read-only-frozen-context", "status": "PASS", "version": 2, "mode": "READ-ONLY EVIDENCE-FIRST SOURCE FREEZE", "source_sha256": source_pin, "protocol_sha256": protocol_pin, "contract_sha256": contract_pin, "frozen_owner_count": len(frozen), "authenticated_support_owner_count": len(support), "authenticated_external_oracle_owner_count": len(external), "original_adapter_sha256": ORIGINAL_SHA256, "original_adapter_bytes": ORIGINAL_BYTES, "historical_v1_derived_sha256": V1_DERIVED_SHA256, "corrected_derived_sha256": DERIVED_SHA256, "corrected_derived_bytes": DERIVED_BYTES, "anchored_repair_block_count": len(REPAIR_BLOCKS), "observed_actual_failure": {"test": witness["test"], "line": 2887, "actual": OBSERVED_ACTUAL, "expected": OBSERVED_EXPECTED, "archive_sha256": RUST_ARCHIVE.sha256, "first_mismatch_uncompressed_offset": 7270, "archive_decompressed_again": False}, "official_upstream_method_sha256": UPSTREAM_METHOD_SHA256, "official_upstream_method_ast_sha256": UPSTREAM_METHOD_AST_SHA256, "official_flag_vector_count": vectors["official_source_vector_count"], "actual_isolated_stdlib_flag_vector_count": vectors["actual_isolated_stdlib_vector_count"], "actual_observed_failure_corrected_in_synthetic_source": True, "pure_unknown_preserved": True, "mixed_unknown_preserved": True, "noflag_preserved": True, "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS, "authenticated_digest_addressed_history_paths": CURRENT_HISTORY_REFERENCES, "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_DENOMINATOR, "named_private_waiver_count": PRIVATE_WAIVER_COUNT, "actual_rust_semantic_mismatch_count": 1087, "actual_rust_verified_passing_case_count": 7438, "actual_c_semantic_mismatch_count": 1230, "actual_c_verified_passing_case_count": 7325, "historical_c_semantic_mismatch_count": 1262, "actual_zig_semantic_mismatch_count": 2172, "actual_zig_verified_passing_case_count": 2847, "historical_zig_preflight_candidate_workers": 0, "raw_rust_archive_bytes_read": RUST_ARCHIVE.size, "v1_verify_context_invoked": False, "upstream_test_imported_or_executed": False, "installed_stdlib_path_substituted": False, "rust_external_regex_dependency_count": 0, "cross_family_dependency_count": 0, **boundary()}
    need(expected == contract_document(source_pin, protocol_pin), "retain the caller-pinned exact versioned source contract")
    return outcome, derived


def open_private_directory(parent: int, name: str) -> int:
    need(type(name) is str and bool(name) and name not in (".", "..") and "/" not in name and "\\" not in name, "reject an escaped private snapshot directory")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    handle = os.open(name, flags, dir_fd=parent)
    try:
        current = os.fstat(handle)
        visible = os.stat(name, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISDIR(current.st_mode) and current.st_uid == os.geteuid() and stat.S_IMODE(current.st_mode) == 0o700 and (current.st_dev, current.st_ino) == (visible.st_dev, visible.st_ino), "require one unchanged owner-only no-follow Rust private phase")
        return handle
    except BaseException:
        os.close(handle)
        raise


def apply_private(root: str, derived: bytes, source_pin: str, protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    need(type(root) is str and 0 < len(root) <= 512, "require an exact explicitly caller-pinned private source root")
    parsed = PurePosixPath(root)
    pieces = parsed.parts
    need(parsed.is_absolute() and str(parsed) == root and len(pieces) == 5 and pieces[0] == "/" and pieces[1] == "tmp" and pieces[2].startswith(PRIVATE_ROOT_PREFIX) and PRIVATE_ROOT_FAMILY in pieces[2] and all(char.isascii() and (char.isalnum() or char in "-_") for char in pieces[2]) and pieces[3] in PHASE_NAMES and pieces[4] == "source", "never write outside an exact independently owned first-party Rust /tmp reference phase")
    need(type(derived) is bytes and len(derived) == DERIVED_BYTES and sha256(derived) == DERIVED_SHA256, "reject unpinned private source bytes")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    temp = os.open("/tmp", flags)
    top: int | None = None
    phase: int | None = None
    sibling: int | None = None
    source: int | None = None
    destination_dir: int | None = None
    destination: int | None = None
    try:
        top = open_private_directory(temp, pieces[2])
        phase = open_private_directory(top, pieces[3])
        sibling = open_private_directory(top, "reference-b" if pieces[3] == "reference-a" else "reference-a")
        a, b = os.fstat(phase), os.fstat(sibling)
        need((a.st_dev, a.st_ino) != (b.st_dev, b.st_ino), "never alias the two independent private Rust build phases")
        source = open_private_directory(phase, "source")
        destination_dir = open_private_directory(source, "candidates")
        before_original, before_owner = read_owner(RUST_OWNERS[-1])
        need(repaired_source(before_original, frozen=True) == derived, "refuse to apply after canonical source substitution")
        destination = os.open("rust_candidate.py", os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=destination_dir)
        before = os.fstat(destination)
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid() and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600, "create only a fresh privately owned exact Rust public snapshot")
        cursor = 0
        while cursor < len(derived):
            count = os.write(destination, derived[cursor:])
            need(type(count) is int and count > 0, "never create a partial private source snapshot")
            cursor += count
        os.fsync(destination)
        after = os.fstat(destination)
        need((before.st_dev, before.st_ino, before.st_uid, before.st_nlink) == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink) and after.st_size == DERIVED_BYTES, "reject a swapped or incomplete private source inode")
        os.close(destination)
        destination = None
        verifier = os.open("rust_candidate.py", os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=destination_dir)
        try:
            info = os.fstat(verifier)
            need((info.st_dev, info.st_ino, info.st_uid, info.st_nlink, info.st_size) == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink, after.st_size), "reject a substituted private derived source owner")
            pieces_read: list[bytes] = []
            remaining = info.st_size
            while remaining:
                chunk = os.read(verifier, min(remaining, 1024 * 1024))
                need(type(chunk) is bytes and bool(chunk), "reject truncated private source readback")
                pieces_read.append(chunk)
                remaining -= len(chunk)
            actual = b"".join(pieces_read)
            need(os.read(verifier, 1) == b"" and actual == derived and sha256(actual) == DERIVED_SHA256, "reauthenticate the complete exact independently pinned private source")
        finally:
            os.close(verifier)
        os.fsync(destination_dir)
        after_original, after_owner = read_owner(RUST_OWNERS[-1])
        need(after_original == before_original and after_owner == before_owner, "never modify the actual canonical Rust candidate")
        return {"schema": SCHEMA + "-private-snapshot-application", "status": "PASS", "version": 2, "source_sha256": source_pin, "protocol_sha256": protocol_pin, "contract_sha256": contract_pin, "snapshot_root": root, "phase": pieces[3], "derived_source_sha256": DERIVED_SHA256, "derived_source_bytes": DERIVED_BYTES, "source_apply_count": 1, "canonical_candidate_modified": False, "candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "candidate_imports": 0, "candidate_workers_started": 0, "source_builds_started": 0, "native_activations": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}
    finally:
        if destination is not None:
            os.close(destination)
        for item in (destination_dir, source, sibling, phase, top, temp):
            if item is not None:
                os.close(item)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    flags = [value for value in values if value.startswith("--")]
    need(len(flags) == len(set(flags)), "reject repeated or ambiguous V2 caller authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", "--render-contract", dest="emit_contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    parser.add_argument("--derived-source-sha256")
    parser.add_argument("--derived-source-bytes", type=int)
    options = parser.parse_args(values)
    checked_sha256(options.source_sha256, "V2 source")
    checked_sha256(options.protocol_sha256, "V2 protocol")
    if options.emit_contract:
        need(options.contract_sha256 is None and options.snapshot_root is None and options.derived_source_sha256 is None and options.derived_source_bytes is None, "contract emission never authorizes an application or candidate")
    else:
        checked_sha256(options.contract_sha256, "V2 canonical contract")
        if options.apply:
            need(options.snapshot_root is not None and checked_sha256(options.derived_source_sha256, "independently pinned private derived source") == DERIVED_SHA256 and options.derived_source_bytes == DERIVED_BYTES, "require explicit independent root, exact derived digest, and exact derived bytes before private application")
        else:
            need(options.snapshot_root is None and options.derived_source_sha256 is None and options.derived_source_bytes is None, "source-only gates may never authorize a snapshot application")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        runtime()
        options = parse_arguments(arguments)
        if options.emit_contract:
            output = contract_document(options.source_sha256, options.protocol_sha256)
        elif options.self_test:
            output = self_test(options.source_sha256, options.protocol_sha256, options.contract_sha256)
        elif options.verify_frozen_context:
            output, _ = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256)
        else:
            _, derived = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256)
            output = apply_private(options.snapshot_root, derived, options.source_sha256, options.protocol_sha256, options.contract_sha256)
        sys.stdout.buffer.write(canonical(output))
        return 0
    except (RepairError, OSError, ValueError, TypeError, UnicodeError, RecursionError, SyntaxError, OverflowError, KeyError, AttributeError) as exc:
        sys.stderr.write("owned Rust public source repair v2 rejected: " + str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
