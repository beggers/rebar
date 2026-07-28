#!/usr/bin/env python3
"""Freeze three owned Rust public-contract changes for private snapshots only."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import contextlib
import copy
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Iterator, Mapping, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/apply_owned_rust_public_contract_source_repair_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V1.md"
CONTRACT_RELATIVE = "oracle/phase2/rust-public-contract-source-repair-v1.json"
SCHEMA = "rebar-phase2-owned-rust-public-contract-source-repair-v1"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_COMPRESSED_BYTES = 128 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 128 * 1024 * 1024
MAX_REPORT_BYTES = 2 * 1024 * 1024
SUITE_COUNT = 13
CASE_DENOMINATOR = 31237
PRIVATE_WAIVER_COUNT = 13
V22_EVIDENCE_OWNER_COUNT = 105
V22_AUTHENTICATED_REFERENCE_COUNT = 110
V21_EVIDENCE_OWNER_COUNT = 103
V21_AUTHENTICATED_REFERENCE_COUNT = 108
RUST_HISTORICAL_MISMATCH_COUNT = 2042
RUST_HISTORICAL_PASSING_CASE_COUNT = 7461
RUST_HISTORICAL_FAILED_SUITE_COUNT = 5
RUST_HISTORICAL_SURFACE_MISMATCH_COUNT = 66
RUST_HISTORICAL_PUBLIC_TYPE_MISMATCH_COUNT = 248
RUST_HISTORICAL_SUBSTITUTION_MISMATCH_COUNT = 336
RUST_HISTORICAL_SHAPE_MISMATCH_COUNT = 1392
ORIGINAL_RELATIVE = "candidates/rust_candidate.py"
ORIGINAL_SHA256 = "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"
ORIGINAL_BYTES = 31151
DERIVED_SHA256 = "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
DERIVED_BYTES = 31464
PRIVATE_ROOT_PREFIX = "rebar-phase2-native-build-"
PRIVATE_ROOT_FAMILY = "-rust-"
PHASE_NAMES = ("reference-a", "reference-b")

GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
)
PHASE_ONE = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
)
PHASE_ONE_PROTOCOL = (
    "oracle/phase1/P0-COMPLETENESS-V1.md",
    "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
)
PUBLIC_SURFACE_BASELINE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v19-self-oracle.json",
    "a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8",
)
SUITES: tuple[tuple[str, int], ...] = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
RUST_OWNERS: tuple[tuple[str, str, int], ...] = (
    (
        "candidates/rust/Cargo.lock",
        "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
        167,
    ),
    (
        "candidates/rust/Cargo.toml",
        "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
        225,
    ),
    (
        "candidates/rust/py_bridge.c",
        "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        175676,
    ),
    (
        "candidates/rust/src/lib.rs",
        "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d",
        177967,
    ),
    (
        "candidates/rust/src/newline.rs",
        "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
        14416,
    ),
    (
        "candidates/rust/src/search.rs",
        "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
        14773,
    ),
    (
        "candidates/rust/src/stack.rs",
        "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
        7269,
    ),
    (
        "candidates/rust/src/unicode_tables.rs",
        "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
        471989,
    ),
    (ORIGINAL_RELATIVE, ORIGINAL_SHA256, ORIGINAL_BYTES),
)
V21 = {
    "source": (
        "tools/render_candidate_current_overview_v21.py",
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v21.inputs.json",
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v21.json",
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v21.svg",
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
    ),
}
V22 = {
    "source": (
        "tools/render_candidate_current_overview_v22.py",
        "a07bf3d6e6d8dc28c206218f14e2ed6f6089e31c66dbab2961979409b30fc955",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v22.inputs.json",
        "6843292a1f1d62d4635be4737a1565554cee8ec9f359506bc95a94cb80af7b58",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v22.json",
        "5dc6229696e5aba546c38e3d1d1bd4ce422a892a57ec562ccea8cb75cbbfb21f",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v22.svg",
        "7314d28286b90ee8161c02fee175904ba2ddd2c67dd78163f93b04fef2d0a26c",
    ),
}
RUST_HISTORY: tuple[tuple[str, str, int], ...] = (
    (
        "oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-failures.json.gz",
        "bf0915a4dab62ebaea67b92258eafbc01f52b436b70f81bf7e0ca42211f95bff",
        9623,
    ),
    (
        "oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-failures-publication-receipt.json",
        "72070ab4f68200c305d317a59c7ff6405888d23fadaaf04835aba68d33a6c6ec",
        1186,
    ),
    (
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures.json.gz",
        "a2106050b59130a9eb7f083d13c2e42e22dcf9a33f5a7b35b634ff9dd9b2f9ae",
        716812,
    ),
    (
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures-publication-receipt.json",
        "f6fe003c100a93e06239a072380c4f3839dc9863391b939ebfc6d667b174f0d9",
        1161,
    ),
    (
        "experiments/rust_public_practice_v1/rust-managed-buffer-lifetime-v1-phase2-v5-managed.json.gz",
        "74a5ede2b9c75b9ad9a1d7ecc2802786793197c8a1f399046d5d6d1997b781ca",
        723027,
    ),
    (
        "experiments/rust_public_practice_v1/rust-managed-buffer-lifetime-v1-phase2-v5-managed-publication-receipt.json",
        "f63816d95048ed26bf1572d87676d91364761369fdfb5c49f65d1bcf3ef3ccf7",
        8383,
    ),
    (
        "experiments/rust_public_practice_v1/rust-scanner-verbose-comments-v1-phase2-v5-verbose.json.gz",
        "8f1b6df4044970fed48eecdf2b6bcd9434dcee1956abf8a3308fec80fad6d44a",
        405435,
    ),
    (
        "experiments/rust_public_practice_v1/rust-scanner-verbose-comments-v1-phase2-v5-verbose-publication-receipt.json",
        "929f4899b211d795c8a5e570148ca19c984d2dbeb78fda18ba89701ddee1e241",
        13206,
    ),
    (
        "experiments/rust_public_practice_v1/rust-public-type-identity-serialization-v1-phase2-v5-types.json.gz",
        "f5819a54871a88edf3c6e1b302d67809e5c74cc1912e9bba91a57b6f2e237772",
        501671,
    ),
    (
        "experiments/rust_public_practice_v1/rust-public-type-identity-serialization-v1-phase2-v5-types-publication-receipt.json",
        "ab6b37f02ef81945bef6a3f38dcaa9a7c4594a0cd6d851ecf9df89aa2507646a",
        17649,
    ),
    (
        "experiments/rust_public_practice_v1/rust-shape-changing-buffer-semantics-v2-phase2-v5-shape.json.gz",
        "ee69217102b87f5c5a288c2fa58b44a1e881f46191f21520e6510313cf346b00",
        1598600,
    ),
    (
        "experiments/rust_public_practice_v1/rust-shape-changing-buffer-semantics-v2-phase2-v5-shape-publication-receipt.json",
        "339a1744bffc467495daa4992622d3cfca0219bc4e7433cb21910b46c04b467c",
        16119,
    ),
    (
        "experiments/rust_public_practice_v1/rust-substitution-buffer-semantics-v2-phase2-v5-substitution.json.gz",
        "49c9bf367ddef35d1970b07c483d4468da9e09348522a26780bf0495391673fa",
        833208,
    ),
    (
        "experiments/rust_public_practice_v1/rust-substitution-buffer-semantics-v2-phase2-v5-substitution-publication-receipt.json",
        "4905f6cd20f44453b16f0598e5e77ffa99340107a229987c1728b9635a9e7e60",
        18338,
    ),
    (
        "oracle/phase2/evidence/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures.json.gz",
        "b73ea6fd2f944a46bbc89a593df251a054f62bed288b60765eb3c9dc3a9619cd",
        1061,
    ),
    (
        "oracle/phase2/evidence/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures-publication-receipt.json",
        "99b32d784182800b92b3fcb555add6c8d27d599a91dc5255b46ca597667c6049",
        1522,
    ),
)
ACTUAL_C_FAILURE: tuple[tuple[str, str, int], ...] = (
    (
        "oracle/phase2/evidence/repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures.json.gz",
        "a37a70f7ab9e4dcc72b176ca51fb1bfe8514d906431e8f02f269871a8b946810",
        2496,
    ),
    (
        "oracle/phase2/evidence/repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures-publication-receipt.json",
        "8a16520de9ac80aac1a6ea6d9a6cec3778379d35a611a52a2bca692685645c81",
        934,
    ),
)
OLD_FLAG_BLOCK = b"""        ordered = ((self.ASCII, "ASCII"), (self.IGNORECASE, "IGNORECASE"), (self.LOCALE, "LOCALE"), (self.UNICODE, "UNICODE"), (self.MULTILINE, "MULTILINE"), (self.DOTALL, "DOTALL"), (self.VERBOSE, "VERBOSE"), (self.DEBUG, "DEBUG"))
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
        if unknown:
            parts.append(hex(unknown))
        return "|".join(parts)
"""
NEW_FLAG_BLOCK = b"""        ordered = (
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
REPAIR_BLOCKS: tuple[tuple[str, bytes, bytes], ...] = (
    ("regex-flag-order-and-pure-unknown", OLD_FLAG_BLOCK, NEW_FLAG_BLOCK),
    ("owned-public-pattern-error-module", OLD_ERROR_BLOCK, NEW_ERROR_BLOCK),
    ("owned-pattern-repr-value-equality-and-hash",
     OLD_EQUALITY_BLOCK, NEW_EQUALITY_BLOCK),
)
SURFACE_MISMATCH_COHORTS = {
    "regexflag-intflag-and-noflag": 2,
    "unknown-flags-actually-compiled": 32,
    "mixed-inverted-and-indexed-flags": 32,
}
PUBLIC_TYPE_MISMATCH_COHORTS = {
    "module-public-error-alias": 96,
    "flags-unknown-bit-retention": 12,
    "pattern-and-match-representation": 12,
    "pickle-match-rejection": 32,
    "cache-pattern-type-separation": 96,
}
SUBSTITUTION_MISMATCH_COHORTS = {
    "nested-failing-template-after-subject": 48,
    "nested-mutating-subject-and-template": 48,
    "nested-mutating-unhashable-template": 48,
    "nested-stable-fixed-hash-template": 48,
    "nested-stable-subject-and-template": 48,
    "pep688-failing-hash-template": 32,
    "pep688-fixed-hash-template": 32,
    "pep688-unhashable-template": 32,
}


class RustPublicRepairError(Exception):
    """Reject substituted history, unsafe snapshots, or unproven source edits."""


class SourceOnlyEffect(RustPublicRepairError):
    """A synthetic source-only gate attempted a forbidden side effect."""


def require(condition: Any, reason: str) -> None:
    if condition is not True:
        raise RustPublicRepairError(reason)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete exact owner bytes")
    return hashlib.sha256(raw).hexdigest()


def valid_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "require an exact independently frozen SHA-256: " + label,
    )
    return value


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii")
            + b"\n"
        )
    except (
        TypeError,
        ValueError,
        UnicodeError,
        OverflowError,
        RecursionError,
    ) as error:
        raise RustPublicRepairError(
            "reject noncanonical Rust public source evidence"
        ) from error


def checked_relative(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require a bounded repository-relative source owner")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute()
        and str(parsed) == value
        and 0 < len(parsed.parts) <= 12
        and all(part not in ("", ".", "..") for part in parsed.parts),
        "reject an absolute, escaped, ambiguous, or substituted owner",
    )
    return parsed.parts


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "run only frozen isolated, bytecode-free CPython 3.14.6",
    )


def read_owner(
    relative: str,
    expected: str,
    expected_bytes: int | None = None,
    *,
    maximum: int = MAX_SOURCE_BYTES,
    private: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    parts = checked_relative(relative)
    valid_digest(expected, relative)
    require(type(maximum) is int and maximum > 0,
            "require an exact bounded owner maximum")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directories: list[int] = []
    descriptor: int | None = None
    try:
        parent = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
        directories.append(parent)
        for component in parts[:-1]:
            parent = os.open(
                component,
                flags | getattr(os, "O_DIRECTORY", 0),
                dir_fd=parent,
            )
            directories.append(parent)
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        before = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_nlink == 1
            and 0 < before.st_size <= maximum
            and (before.st_dev, before.st_ino, before.st_size)
            == (visible.st_dev, visible.st_ino, visible.st_size),
            "reject a linked, replaced, empty, or oversized owner: " + relative,
        )
        if expected_bytes is not None:
            require(
                before.st_size == expected_bytes,
                "reject changed source-owner byte count: " + relative,
            )
        if private:
            require(
                stat.S_IMODE(before.st_mode) == 0o600,
                "require an exact privately owned evidence owner: " + relative,
            )
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk),
                    "reject incomplete source-owner bytes: " + relative)
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject extra source-owner bytes: " + relative)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require(
            (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
            )
            and digest(raw) == expected,
            "reject concurrently changed or incorrectly pinned owner: " + relative,
        )
        return raw, {
            "path": relative,
            "sha256": expected,
            "bytes": after.st_size,
            "device": after.st_dev,
            "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for directory in reversed(directories):
            os.close(directory)


def strict_json(
    raw: bytes,
    label: str,
    *,
    canonical_required: bool = True,
) -> dict[str, Any]:
    def unique(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            require(type(key) is str and key not in result,
                    "reject duplicated historical JSON key: " + label)
            result[key] = value
        return result

    def invalid(_value: str) -> Any:
        raise RustPublicRepairError(
            "reject nonfinite historical Rust evidence: " + label
        )

    try:
        document = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=unique,
            parse_constant=invalid,
        )
    except (
        TypeError,
        UnicodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise RustPublicRepairError(
            "reject invalid complete historical Rust evidence: " + label
        ) from error
    require(type(document) is dict,
            "require one complete evidence object: " + label)
    if canonical_required:
        require(canonical(document) == raw,
                "reject noncanonical frozen evidence bytes: " + label)
    return document


def decompress_document(
    raw: bytes,
    label: str,
    *,
    expected_uncompressed_sha256: str | None = None,
    expected_uncompressed_bytes: int | None = None,
) -> dict[str, Any]:
    pieces: list[bytes] = []
    total = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as archive:
            while True:
                chunk = archive.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                require(
                    total <= MAX_UNCOMPRESSED_BYTES,
                    "reject oversized complete historical archive: " + label,
                )
                pieces.append(chunk)
    except (OSError, EOFError, ValueError) as error:
        raise RustPublicRepairError(
            "reject truncated historical Rust archive: " + label
        ) from error
    expanded = b"".join(pieces)
    if expected_uncompressed_sha256 is not None:
        require(
            digest(expanded)
            == valid_digest(expected_uncompressed_sha256, label),
            "reject changed complete historical archive contents: " + label,
        )
    if expected_uncompressed_bytes is not None:
        require(
            len(expanded) == expected_uncompressed_bytes,
            "reject changed complete historical archive size: " + label,
        )
    return strict_json(expanded, label)


def repair_block_document() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "original_sha256": digest(original),
            "original_bytes": len(original),
            "derived_sha256": digest(repaired),
            "derived_bytes": len(repaired),
            "original_occurrence_count": 1,
            "derived_occurrence_count": 1,
        }
        for name, original, repaired in REPAIR_BLOCKS
    ]


def repaired_source(
    source: bytes,
    source_sha256: str,
    source_bytes: int,
    *,
    frozen: bool = True,
) -> bytes:
    require(type(source) is bytes and len(source) == source_bytes,
            "reject changed original Rust Python source length")
    require(digest(source) == source_sha256,
            "reject changed original Rust Python source bytes")
    require(
        source.count(b"class RegexFlag(enum.IntFlag):") == 1
        and source.count(b"class PatternError(Exception):") == 1
        and source.count(b"class Pattern(metaclass=_PatternType):") == 1,
        "require the three original, independently owned Rust public classes",
    )
    derived = source
    for name, original, repaired in REPAIR_BLOCKS:
        require(
            derived.count(original) == 1
            and derived.count(repaired) == 0,
            "require exactly one unrepaired owned public block: " + name,
        )
        offset = derived.index(original)
        prefix = derived[:offset]
        suffix = derived[offset + len(original):]
        derived = prefix + repaired + suffix
        require(
            derived.startswith(prefix)
            and derived.endswith(suffix)
            and derived.count(repaired) == 1
            and derived.count(original) == 0,
            "reject extra changes outside the named owned block: " + name,
        )
    cache_anchors = (
        b"return _cache2[type(pattern), pattern, flags]",
        b"key = (type(pattern), pattern, flags)",
    )
    for marker in cache_anchors:
        require(
            source.count(marker) == 1 and derived.count(marker) == 1,
            "preserve the exact original type-sensitive compile-cache key",
        )
    for marker in (
        b"def _template(",
        b"def _cached_template(",
        b"def _restore_owned_generic_alias(",
        b"def __reduce__(self):",
        b"class Scanner:",
        b"_rust_bridge.set_template(_template)",
        b"__all__ = ",
    ):
        expected_count = (
            2
            if source_sha256 == ORIGINAL_SHA256
            and marker == b"def __reduce__(self):"
            else 1
        )
        require(
            source.count(marker) == expected_count
            and derived.count(marker) == expected_count,
            "never alter Rust buffer, scanner, pickle, or public export policy",
        )
    for forbidden in (
        b"import re\n",
        b"from re import",
        b"import _sre",
        b"from _sre",
        b"ctypes",
        b"subprocess",
        b"candidates.vm_candidate",
        b"candidates.zig_candidate",
        b"candidates.cpp_candidate",
        b"candidates.go_candidate",
        b"candidates.fortran_candidate",
        b"regex.compile",
        b"pcre",
        b"oniguruma",
    ):
        require(
            derived.count(forbidden) == source.count(forbidden),
            "reject introduced stdlib, external, or cross-family matching",
        )
    try:
        original_tree = ast.parse(
            source.decode("utf-8", "strict"),
            filename=ORIGINAL_RELATIVE,
        )
        derived_tree = ast.parse(
            derived.decode("utf-8", "strict"),
            filename="private-snapshot/" + ORIGINAL_RELATIVE,
        )
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise RustPublicRepairError(
            "reject an invalid independently owned Python public adapter"
        ) from error
    require(
        isinstance(original_tree, ast.Module)
        and isinstance(derived_tree, ast.Module),
        "require two complete statically parsed Python source modules",
    )
    classes = {
        item.name: item
        for item in derived_tree.body
        if isinstance(item, ast.ClassDef)
    }
    error_class = classes.get("PatternError")
    flag_class = classes.get("RegexFlag")
    pattern_class = classes.get("Pattern")
    require(
        isinstance(error_class, ast.ClassDef)
        and isinstance(flag_class, ast.ClassDef)
        and isinstance(pattern_class, ast.ClassDef),
        "preserve the actual three independently owned Rust public classes",
    )
    module_assignment = [
        item
        for item in error_class.body
        if isinstance(item, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__module__"
            for target in item.targets
        )
    ]
    require(
        len(module_assignment) == 1
        and isinstance(module_assignment[0].value, ast.Constant)
        and module_assignment[0].value.value == "re",
        "freeze only the original owned PatternError public module identity",
    )
    flag_repr = [
        item
        for item in flag_class.body
        if isinstance(item, ast.FunctionDef) and item.name == "__repr__"
    ]
    pattern_methods = {
        item.name: item
        for item in pattern_class.body
        if isinstance(item, ast.FunctionDef)
    }
    require(
        len(flag_repr) == 1
        and "__repr__" in pattern_methods
        and "__eq__" in pattern_methods
        and "__hash__" in pattern_methods,
        "preserve exactly one original flag repr and owned pattern value methods",
    )
    require(
        derived.count(b'return f"re.RegexFlag({value})"') == 1
        and derived.count(b'if rendered.startswith("re.RegexFlag(")') == 1
        and derived.count(b"rendered = hex(flags)") == 1
        and derived.count(b"return (self.pattern, self.flags) == "
                          b"(other.pattern, other.flags)") == 1
        and derived.count(b"return hash((self.pattern, self.flags))") == 1,
        "freeze exact unknown flags and value-compatible owned patterns",
    )
    if frozen:
        require(
            source_sha256 == ORIGINAL_SHA256
            and source_bytes == ORIGINAL_BYTES
            and len(derived) == DERIVED_BYTES
            and digest(derived) == DERIVED_SHA256,
            "require the exact immutable original and derived Rust adapter",
        )
    return derived


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    counts = {
        "blocked_reads": 0,
        "blocked_writes": 0,
        "blocked_processes": 0,
        "blocked_imports": 0,
        "blocked_network": 0,
        "blocked_threads": 0,
        "blocked_clocks": 0,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "reference_processes_started": 0,
        "compiler_processes_started": 0,
        "source_builds_started": 0,
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "workspace_mutations": 0,
        "source_apply_count": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
    }
    originals: list[tuple[Any, str, Any]] = []

    def prohibit(owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            counts[category] += 1
            raise SourceOnlyEffect(
                "synthetic-only Rust public repair forbids " + name
            )

        originals.append((owner, name, previous))
        setattr(owner, name, blocked)

    try:
        for owner, name in (
            (builtins, "open"),
            (io, "open"),
            (os, "open"),
            (os, "read"),
            (os, "stat"),
            (os, "lstat"),
            (os, "scandir"),
            (Path, "open"),
            (Path, "read_bytes"),
            (Path, "read_text"),
            (Path, "stat"),
            (Path, "resolve"),
        ):
            prohibit(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"),
            (os, "mkdir"),
            (os, "makedirs"),
            (os, "unlink"),
            (os, "remove"),
            (os, "rename"),
            (os, "replace"),
            (os, "fsync"),
            (Path, "write_bytes"),
            (Path, "write_text"),
            (Path, "mkdir"),
            (Path, "unlink"),
            (Path, "rename"),
            (Path, "replace"),
            (tempfile, "mkdtemp"),
            (tempfile, "mkstemp"),
        ):
            prohibit(owner, name, "blocked_writes")
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            prohibit(subprocess, name, "blocked_processes")
        prohibit(importlib, "import_module", "blocked_imports")
        prohibit(socket, "socket", "blocked_network")
        prohibit(socket, "create_connection", "blocked_network")
        prohibit(threading.Thread, "start", "blocked_threads")
        for name in (
            "time",
            "time_ns",
            "monotonic",
            "monotonic_ns",
            "perf_counter",
            "perf_counter_ns",
            "process_time",
            "process_time_ns",
            "thread_time",
            "thread_time_ns",
            "sleep",
        ):
            prohibit(time, name, "blocked_clocks")
        yield counts
    finally:
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)


def sample_source() -> bytes:
    return (
        b"import enum\n\n"
        b"class RegexFlag(enum.IntFlag):\n"
        b"    IGNORECASE = 2\n"
        b"    LOCALE = 4\n"
        b"    MULTILINE = 8\n"
        b"    DOTALL = 16\n"
        b"    UNICODE = 32\n"
        b"    VERBOSE = 64\n"
        b"    DEBUG = 128\n"
        b"    ASCII = 256\n"
        b"    def __repr__(self):\n"
        b"        value = int(self)\n"
        b"        if not value:\n"
        b"            return \"re.NOFLAG\"\n"
        + OLD_FLAG_BLOCK
        + b"\n"
        + OLD_ERROR_BLOCK
        + b"        super().__init__(msg)\n\n"
        b"class _PatternType(type):\n"
        b"    pass\n\n"
        b"class Pattern(metaclass=_PatternType):\n"
        + OLD_EQUALITY_BLOCK
        + b"\n"
        b"    def __reduce__(self):\n"
        b"        return None\n"
        b"    def _cached_template(self):\n"
        b"        return None\n\n"
        b"def _template():\n"
        b"    return None\n\n"
        b"def _restore_owned_generic_alias():\n"
        b"    return None\n\n"
        b"class Scanner:\n"
        b"    pass\n\n"
        b"def example(pattern, flags):\n"
        b"    key = (type(pattern), pattern, flags)\n"
        b"    return _cache2[type(pattern), pattern, flags]\n\n"
        b"def registration():\n"
        b"    _rust_bridge.set_template(_template)\n\n"
        b"__all__ = []\n"
    )


def self_test() -> dict[str, Any]:
    accepted = 0
    rejected = 0
    sample = sample_source()
    sample_sha256 = digest(sample)
    with source_only_boundary() as effects:
        derived = repaired_source(
            sample,
            sample_sha256,
            len(sample),
            frozen=False,
        )
        require(
            len(REPAIR_BLOCKS) == 3
            and sum(value for value in SURFACE_MISMATCH_COHORTS.values())
            == RUST_HISTORICAL_SURFACE_MISMATCH_COUNT
            and sum(value for value in PUBLIC_TYPE_MISMATCH_COHORTS.values())
            == RUST_HISTORICAL_PUBLIC_TYPE_MISMATCH_COUNT
            and sum(value for value in SUBSTITUTION_MISMATCH_COHORTS.values())
            == RUST_HISTORICAL_SUBSTITUTION_MISMATCH_COUNT
            and (
                RUST_HISTORICAL_SURFACE_MISMATCH_COUNT
                + RUST_HISTORICAL_PUBLIC_TYPE_MISMATCH_COUNT
                + RUST_HISTORICAL_SUBSTITUTION_MISMATCH_COUNT
                + RUST_HISTORICAL_SHAPE_MISMATCH_COUNT
            )
            == RUST_HISTORICAL_MISMATCH_COUNT,
            "preserve the exact signed historical mismatch decomposition",
        )
        accepted += 1
        for _, original, repaired in REPAIR_BLOCKS:
            require(
                derived.count(original) == 0
                and derived.count(repaired) == 1,
                "authenticate exactly one source-only synthetic public repair",
            )
            accepted += 1
        for marker in (
            b"return _cache2[type(pattern), pattern, flags]",
            b"key = (type(pattern), pattern, flags)",
            b"def __reduce__(self):",
            b"def _cached_template(",
            b"class Scanner:",
            b"_rust_bridge.set_template(_template)",
        ):
            require(
                sample.count(marker) == derived.count(marker) == 1,
                "preserve source-only original cache, pickle, and buffer ownership",
            )
            accepted += 1

        def reject(action: Any, name: str) -> None:
            nonlocal rejected
            try:
                action()
            except (
                RustPublicRepairError,
                TypeError,
                ValueError,
                OSError,
                SyntaxError,
            ):
                rejected += 1
            else:
                raise RustPublicRepairError(
                    "accepted a hostile Rust public source control: " + name
                )

        reject(
            lambda: repaired_source(
                sample,
                "0" * 64,
                len(sample),
                frozen=False,
            ),
            "substituted original digest",
        )
        reject(
            lambda: repaired_source(
                sample,
                sample_sha256,
                len(sample) + 1,
                frozen=False,
            ),
            "substituted original byte count",
        )
        reject(
            lambda: repaired_source(
                sample,
                sample_sha256,
                len(sample),
                frozen=True,
            ),
            "synthetic source disguised as genuine Rust",
        )
        for name, old, new in REPAIR_BLOCKS:
            variants = (
                ("missing original block", sample.replace(old, b"# removed\n")),
                ("duplicate original block", sample.replace(old, old + old)),
                ("already repaired block", sample.replace(old, new)),
            )
            for kind, hostile in variants:
                reject(
                    lambda data=hostile: repaired_source(
                        data,
                        digest(data),
                        len(data),
                        frozen=False,
                    ),
                    name + ": " + kind,
                )
        for marker in (
            b"return _cache2[type(pattern), pattern, flags]",
            b"key = (type(pattern), pattern, flags)",
            b"def __reduce__(self):",
            b"def _cached_template(",
            b"class Scanner:",
            b"_rust_bridge.set_template(_template)",
        ):
            hostile = sample.replace(marker, b"forbidden_public_replacement")
            reject(
                lambda data=hostile: repaired_source(
                    data,
                    digest(data),
                    len(data),
                    frozen=False,
                ),
                "changed owned public contract marker",
            )
        for path in (
            "",
            "/tmp/escaped",
            "../escaped",
            "a/../escaped",
            "a/./escaped",
            "a//escaped",
            "./escaped",
            "a/",
            "x" * 513,
        ):
            reject(
                lambda value=path: checked_relative(value),
                "unsafe repository owner path",
            )
        for fingerprint in (
            "",
            "0" * 63,
            "0" * 65,
            "A" * 64,
            "z" * 64,
        ):
            reject(
                lambda value=fingerprint: valid_digest(value, "hostile"),
                "unsafe owner fingerprint",
            )
        for hostile in (
            b'{"x":1,"x":2}\n',
            b'{"x":NaN}\n',
            b"[]\n",
            b'{"x":1}',
        ):
            reject(
                lambda raw=hostile: strict_json(raw, "hostile source document"),
                "altered canonical history",
            )
        probes = (
            ("blocked_reads", lambda: builtins.open("/tmp/rust-forbidden", "rb")),
            ("blocked_reads", lambda: io.open("/tmp/rust-forbidden", "rb")),
            ("blocked_reads", lambda: os.open("/tmp/rust-forbidden", os.O_RDONLY)),
            ("blocked_reads", lambda: os.read(-1, 1)),
            ("blocked_reads", lambda: os.stat("/tmp")),
            ("blocked_reads", lambda: Path("/tmp/rust-forbidden").read_bytes()),
            ("blocked_writes", lambda: os.write(-1, b"forbidden")),
            ("blocked_writes", lambda: os.mkdir("/tmp/rust-forbidden")),
            ("blocked_writes", lambda: os.unlink("/tmp/rust-forbidden")),
            ("blocked_writes", lambda: Path("/tmp/rust-forbidden").write_bytes(b"x")),
            ("blocked_writes", lambda: tempfile.mkdtemp()),
            ("blocked_processes", lambda: subprocess.run(("rust-forbidden",))),
            ("blocked_processes", lambda: subprocess.Popen(("rust-forbidden",))),
            (
                "blocked_imports",
                lambda: importlib.import_module("candidates.rust_candidate"),
            ),
            ("blocked_imports", lambda: importlib.import_module("re")),
            ("blocked_network", lambda: socket.socket()),
            (
                "blocked_network",
                lambda: socket.create_connection(("127.0.0.1", 1)),
            ),
            ("blocked_threads", lambda: threading.Thread().start()),
            ("blocked_clocks", lambda: time.perf_counter_ns()),
            ("blocked_clocks", lambda: time.monotonic()),
            ("blocked_clocks", lambda: time.time()),
            ("blocked_clocks", lambda: time.sleep(0)),
        )
        for name, action in probes:
            prior = effects[name]
            reject(action, "forbidden source-only effect")
            require(
                effects[name] == prior + 1,
                "authenticate each blocked synthetic source-only operation",
            )
        counts = dict(effects)
    require(
        rejected >= 50,
        "require substantial hostile source-only Rust public controls",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_source_controls": accepted,
        "rejected_hostile_controls": rejected,
        "source_only_effects": counts,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "historical_evidence_owner_count": V22_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            V22_AUTHENTICATED_REFERENCE_COUNT,
        "original_candidate_modified": False,
        "derived_source_materialized": False,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_compiler_processes": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "source_apply_count": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "candidate_correctness": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def mapping_document(
    mapping: Mapping[str, tuple[str, str]],
) -> dict[str, dict[str, str]]:
    return {
        key: {"path": path, "sha256": fingerprint}
        for key, (path, fingerprint) in sorted(mapping.items())
    }


def owner_document(
    values: Sequence[tuple[str, str, int]],
) -> list[dict[str, Any]]:
    return [
        {"path": path, "sha256": fingerprint, "bytes": count}
        for path, fingerprint, count in values
    ]


def contract_document(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    valid_digest(source_sha256, "public repair source")
    valid_digest(protocol_sha256, "public repair protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "phase": "SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "source": {
            "path": SOURCE_RELATIVE,
            "sha256": source_sha256,
        },
        "protocol": {
            "path": PROTOCOL_RELATIVE,
            "sha256": protocol_sha256,
        },
        "goal": {"path": GOAL[0], "sha256": GOAL[1]},
        "pinned_runtime": {
            "path": PYTHON,
            "sha256": PYTHON_SHA256,
            "version": "3.14.6",
            "isolated": True,
            "bytecode_writes": False,
        },
        "phase_one": {
            "protocol": {
                "path": PHASE_ONE_PROTOCOL[0],
                "sha256": PHASE_ONE_PROTOCOL[1],
            },
            "document": {
                "path": PHASE_ONE[0],
                "sha256": PHASE_ONE[1],
            },
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
        },
        "rust_source": {
            "family": "rust",
            "owner_count": len(RUST_OWNERS),
            "owners": owner_document(RUST_OWNERS),
            "external_regex_dependency_count": 0,
            "cargo_lock_package_count": 1,
            "stdlib_regex_delegation_allowed": False,
            "cross_family_semantic_source_allowed": False,
        },
        "published_v21": mapping_document(V21),
        "published_v22": mapping_document(V22),
        "published_history": {
            "v21_evidence_owner_count": V21_EVIDENCE_OWNER_COUNT,
            "v21_authenticated_reference_count":
                V21_AUTHENTICATED_REFERENCE_COUNT,
            "v22_evidence_owner_count": V22_EVIDENCE_OWNER_COUNT,
            "v22_authenticated_reference_count":
                V22_AUTHENTICATED_REFERENCE_COUNT,
            "rust_historical_status": "FAILED; NOT QUALIFIED",
            "rust_historical_case_execution_denominator": CASE_DENOMINATOR,
            "rust_historical_semantic_mismatch_count":
                RUST_HISTORICAL_MISMATCH_COUNT,
            "rust_historical_verified_passing_case_count":
                RUST_HISTORICAL_PASSING_CASE_COUNT,
            "rust_historical_failed_suite_count":
                RUST_HISTORICAL_FAILED_SUITE_COUNT,
            "rust_historical_evidence": owner_document(RUST_HISTORY),
            "preserved_actual_corrected_c_failure":
                owner_document(ACTUAL_C_FAILURE),
            "preserved_actual_corrected_c_status": "FAIL",
            "preserved_actual_corrected_c_matching": "NOT MEASURED",
        },
        "historical_original_mismatch_vectors": {
            "public_surface": {
                "case_execution_count": 1376,
                "semantic_mismatch_count":
                    RUST_HISTORICAL_SURFACE_MISMATCH_COUNT,
                "mismatches_by_cohort": dict(SURFACE_MISMATCH_COHORTS),
                "candidate_archive": {
                    "path": RUST_HISTORY[2][0],
                    "sha256": RUST_HISTORY[2][1],
                },
                "two_reference_baseline": {
                    "path": PUBLIC_SURFACE_BASELINE[0],
                    "sha256": PUBLIC_SURFACE_BASELINE[1],
                },
            },
            "public_types": {
                "case_execution_count": 6912,
                "semantic_mismatch_count":
                    RUST_HISTORICAL_PUBLIC_TYPE_MISMATCH_COUNT,
                "mismatches_by_cohort": dict(PUBLIC_TYPE_MISMATCH_COHORTS),
                "candidate_archive": {
                    "path": RUST_HISTORY[8][0],
                    "sha256": RUST_HISTORY[8][1],
                },
            },
            "substitution": {
                "case_execution_count": 5120,
                "semantic_mismatch_count":
                    RUST_HISTORICAL_SUBSTITUTION_MISMATCH_COUNT,
                "mismatches_by_cohort": dict(SUBSTITUTION_MISMATCH_COHORTS),
                "candidate_archive": {
                    "path": RUST_HISTORY[12][0],
                    "sha256": RUST_HISTORY[12][1],
                },
            },
            "shape_changing_buffers": {
                "case_execution_count": 10240,
                "semantic_mismatch_count":
                    RUST_HISTORICAL_SHAPE_MISMATCH_COUNT,
                "candidate_archive": {
                    "path": RUST_HISTORY[10][0],
                    "sha256": RUST_HISTORY[10][1],
                },
            },
            "pickle_semantics": "UNCHANGED; NOT RETESTED",
            "buffer_lifetimes": "UNCHANGED; NOT RETESTED",
            "correctness_after_source_repair": "NOT MEASURED",
        },
        "repair": {
            "original": {
                "path": ORIGINAL_RELATIVE,
                "sha256": ORIGINAL_SHA256,
                "bytes": ORIGINAL_BYTES,
                "modified": False,
            },
            "derived": {
                "path": ORIGINAL_RELATIVE,
                "sha256": DERIVED_SHA256,
                "bytes": DERIVED_BYTES,
                "materialized": False,
            },
            "anchored_block_count": len(REPAIR_BLOCKS),
            "blocks": repair_block_document(),
            "preserve_original_type_based_cache_key": True,
            "preserve_existing_pickle_policy": True,
            "preserve_existing_buffer_and_template_policy": True,
            "external_regex_package_added": False,
            "stdlib_regex_engine_added": False,
            "candidate_matching_proven": False,
        },
        "apply_policy": {
            "explicit_apply_required": True,
            "candidate_source_mutation": "FORBIDDEN",
            "workspace_destination": "FORBIDDEN",
            "existing_destination": "FORBIDDEN",
            "external_owner": "FORBIDDEN",
            "private_root_parent": "/tmp",
            "private_root_prefix": PRIVATE_ROOT_PREFIX,
            "private_root_required_family_component": PRIVATE_ROOT_FAMILY,
            "phase_names": list(PHASE_NAMES),
            "phase_and_source_directory_mode": "0700",
            "private_file_mode": "0600",
            "destination": ORIGINAL_RELATIVE,
            "mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
        },
        "phase_boundary": {
            "candidate_correctness": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "reference_processes_started": 0,
            "compiler_processes_started": 0,
            "source_builds_started": 0,
            "native_activations": 0,
            "native_libraries_loaded": 0,
            "workspace_mutations": 0,
            "source_apply_count": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        },
    }


def require_exact_receipt(
    document: Mapping[str, Any],
    archive: tuple[str, str, int],
    *,
    family: str = "rust",
    candidate_status: str | None = None,
    mismatch_count: int | None = None,
) -> None:
    require(
        document.get("status") == "PASS"
        and (
            document.get("candidate_family") == family
            or document.get("family") == family
        )
        and document.get("performance") == "NOT MEASURED",
        "reject a failed, substituted, or measured historical durable receipt",
    )
    link = document.get("archive")
    if isinstance(link, dict):
        require(
            (link.get("relative") or link.get("path")) == archive[0]
            and link.get("sha256") == archive[1]
            and (link.get("bytes") or link.get("size_bytes")) == archive[2],
            "reject a substituted historical archive owner link",
        )
    elif document.get("report_relative") is not None:
        require(
            document.get("report_relative") == archive[0]
            and document.get("report_sha256") == archive[1]
            and document.get("report_bytes") == archive[2],
            "reject an independently owned specialist report receipt",
        )
    elif document.get("archive_relative") is not None:
        require(
            document.get("archive_relative") == archive[0]
            and document.get("archive_sha256") == archive[1]
            and document.get("archive_bytes") == archive[2],
            "reject a substituted frozen interpreter archive",
        )
    else:
        raise RustPublicRepairError(
            "historical receipt does not authenticate its report owner"
        )
    if candidate_status is not None:
        observed = (
            document.get("candidate_status")
            or document.get("candidate_result_status")
            or document.get("result_status")
        )
        require(observed == candidate_status,
                "never confuse durable publication with candidate correctness")
    if mismatch_count is not None:
        require(
            document.get("mismatch_count") == mismatch_count,
            "never omit a genuine signed specialist mismatch",
        )


def decode_process(
    envelope: Any,
    label: str,
) -> dict[str, Any]:
    require(type(envelope) is dict,
            "require a complete actual historical process stream: " + label)
    require(envelope.get("complete") is True,
            "reject an incomplete actual historical process stream: " + label)
    encoded = envelope.get("data")
    if encoded is None:
        encoded = envelope.get("base64")
    require(type(encoded) is str,
            "require exact base64 historical process bytes: " + label)
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, UnicodeError, base64.binascii.Error) as error:
        raise RustPublicRepairError(
            "reject substituted actual historical process bytes: " + label
        ) from error
    if envelope.get("bytes") is not None:
        require(
            len(raw) == envelope["bytes"],
            "reject incomplete historical process byte count: " + label,
        )
    if envelope.get("sha256") is not None:
        require(
            digest(raw) == envelope["sha256"],
            "reject altered historical process stream: " + label,
        )
    return strict_json(raw, label)


def verify_public_surface(
    worker: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> dict[str, int]:
    rows = worker.get("all_suites")
    require(
        type(rows) is list
        and len(rows) == SUITE_COUNT
        and [
            (row.get("suite"), row.get("case_execution_denominator"))
            for row in rows
        ] == list(SUITES),
        "never omit or change an original frozen Rust P0 suite",
    )
    suites = {row["suite"]: row for row in rows}
    historical_failures = {
        "public_types_v1",
        "substitution_v2",
        "shape_v2",
        "public_surface_v19",
        "subinterpreter_v2",
    }
    require(
        {
            name
            for name, row in suites.items()
            if row.get("status") == "FAIL"
        } == historical_failures,
        "preserve all five genuine failed Rust suite routes",
    )
    public = suites["public_surface_v19"]
    process = public.get("actual_process")
    require(
        type(process) is dict
        and process.get("returncode") == 0
        and process.get("timed_out") is False,
        "require the genuine complete historical public-surface process",
    )
    candidate = decode_process(
        process.get("stdout"),
        "complete historical Rust public-surface candidate stdout",
    )
    require(
        candidate.get("status") == "OBSERVED"
        and candidate.get("candidate_family") == "rust"
        and candidate.get("suite") == "public_surface_v19"
        and candidate.get("case_denominator") == 1376
        and candidate.get("matrix_sha256")
        == "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa"
        and candidate.get("reference_records_sha256")
        == "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
        "reject a substituted public-surface process or frozen matrix",
    )
    require(
        reference.get("status") == "PASS"
        and reference.get("actual_independent_reference_count") == 2
        and reference.get("record_sha256")
        == "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
        "require both genuine candidate-free frozen public references",
    )
    reports = reference.get("reference_worker_reports")
    require(type(reports) is dict,
            "require both retained independent frozen public references")
    first = reports.get("reference_a")
    second = reports.get("reference_b")
    require(type(first) is dict and type(second) is dict,
            "reject a missing separately saved public reference")
    reference_a = first.get("records")
    reference_b = second.get("records")
    actual = candidate.get("candidate_records")
    require(
        type(reference_a) is list
        and type(reference_b) is list
        and type(actual) is list
        and len(reference_a) == len(reference_b) == len(actual) == 1376,
        "preserve every real historical public-surface case",
    )
    counts: dict[str, int] = {}
    for left, right, observed in zip(
        reference_a,
        reference_b,
        actual,
        strict=True,
    ):
        require(
            type(left) is dict
            and type(right) is dict
            and type(observed) is dict
            and canonical(left) == canonical(right),
            "never silently waive an original public self-oracle failure",
        )
        require(
            left.get("id") == observed.get("id")
            and left.get("cohort") == observed.get("cohort")
            and left.get("stimulus_sha256")
            == observed.get("stimulus_sha256"),
            "reject a substituted or reordered actual public case",
        )
        if canonical(left.get("outcome")) != canonical(
            observed.get("outcome")
        ):
            cohort = left["cohort"]
            counts[cohort] = counts.get(cohort, 0) + 1
    require(
        counts == SURFACE_MISMATCH_COHORTS
        and sum(counts.values())
        == RUST_HISTORICAL_SURFACE_MISMATCH_COUNT,
        "preserve all 66 signed historical Rust public-surface mismatches",
    )
    return counts


def positive_counts(value: Any) -> dict[str, int]:
    require(type(value) is dict,
            "require every original specialist mismatch cohort")
    output: dict[str, int] = {}
    for key, count in value.items():
        require(
            type(key) is str
            and type(count) is int
            and count >= 0,
            "reject a forged specialist cohort or mismatch count",
        )
        if count:
            output[key] = count
    return output


def verify_context(
    source_sha256: str,
    protocol_sha256: str,
    contract_sha256: str | None = None,
) -> tuple[dict[str, Any], bytes]:
    verify_runtime()
    owners: dict[str, dict[str, Any]] = {}
    for path, fingerprint in (
        (SOURCE_RELATIVE, source_sha256),
        (PROTOCOL_RELATIVE, protocol_sha256),
        GOAL,
        PHASE_ONE,
        PHASE_ONE_PROTOCOL,
        PUBLIC_SURFACE_BASELINE,
    ):
        raw, owners[path] = read_owner(path, fingerprint)
        if path == PHASE_ONE[0]:
            phase = strict_json(raw, "unchanged original phase-one P0 matrix")
        elif path == PUBLIC_SURFACE_BASELINE[0]:
            surface_reference = strict_json(
                raw,
                "unchanged independent public-surface self-oracle",
            )
    for version in (V21, V22):
        for path, fingerprint in version.values():
            _, owners[path] = read_owner(path, fingerprint)
    original_raw: bytes | None = None
    manifest_raw: bytes | None = None
    lock_raw: bytes | None = None
    for path, fingerprint, size in RUST_OWNERS:
        raw, owners[path] = read_owner(path, fingerprint, size)
        if path == ORIGINAL_RELATIVE:
            original_raw = raw
        elif path.endswith("/Cargo.toml"):
            manifest_raw = raw
        elif path.endswith("/Cargo.lock"):
            lock_raw = raw
    require(
        type(original_raw) is bytes
        and type(manifest_raw) is bytes
        and type(lock_raw) is bytes,
        "authenticate all nine unchanged independent Rust source owners",
    )
    require(
        b"[dependencies]" not in manifest_raw
        and b"regex" not in manifest_raw.lower()
        and lock_raw.count(b"[[package]]") == 1
        and b'name = "rebar-rust-continuation"' in lock_raw
        and b"dependencies =" not in lock_raw
        and b"source =" not in lock_raw
        and b"regex" not in lock_raw.lower(),
        "require the exact single-crate zero-external-dependency Cargo lock",
    )
    require(
        phase.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and phase.get("version") == 1
        and type(phase.get("suites")) is list
        and [
            (suite.get("id"), suite.get("case_execution_count"))
            for suite in phase["suites"]
        ] == list(SUITES)
        and sum(
            suite["case_execution_count"] for suite in phase["suites"]
        ) == CASE_DENOMINATOR,
        "preserve every unchanged original CPython P0 case and suite",
    )
    denominator = phase.get("denominator")
    require(
        type(denominator) is dict
        and denominator.get("final_required_case_execution_denominator")
        == CASE_DENOMINATOR
        and denominator.get("frozen_planned_case_execution_denominator")
        == CASE_DENOMINATOR
        and denominator.get(
            "private_upstream_methods_outside_public_denominator"
        ) == PRIVATE_WAIVER_COUNT
        and denominator.get("counted_suite_ids")
        == [name for name, _ in SUITES],
        "preserve 31,237 original cases and all 13 named private waivers",
    )
    v21_raw, _ = read_owner(V21["summary"][0], V21["summary"][1])
    prior = strict_json(v21_raw, "independently published V21 overview")
    require(
        prior.get("status") == "PASS"
        and prior.get("repository_evidence_owner_count")
        == V21_EVIDENCE_OWNER_COUNT
        and prior.get("authenticated_digest_addressed_history_paths")
        == V21_AUTHENTICATED_REFERENCE_COUNT
        and prior.get("suite_count") == SUITE_COUNT
        and prior.get("full_case_denominator") == CASE_DENOMINATOR,
        "preserve all genuine pre-existing V21 103/108 source history",
    )
    overview_raw, _ = read_owner(V22["summary"][0], V22["summary"][1])
    overview = strict_json(overview_raw, "independently published V22 overview")
    require(
        overview.get("schema")
        == "rebar-candidate-current-overview-v22-summary"
        and overview.get("status") == "PASS"
        and overview.get("suite_count") == SUITE_COUNT
        and overview.get("full_case_denominator") == CASE_DENOMINATOR
        and overview.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and overview.get("repository_evidence_owner_count")
        == V22_EVIDENCE_OWNER_COUNT
        and overview.get("authenticated_digest_addressed_history_paths")
        == V22_AUTHENTICATED_REFERENCE_COUNT
        and overview.get("qualified_candidate_count") == 0
        and overview.get("clock_samples") == 0
        and overview.get("hidden_cases_read") == 0
        and overview.get("timing_trials_run") == 0
        and overview.get("performance") == "NOT MEASURED"
        and overview.get("memory") == "NOT MEASURED"
        and overview.get("final_holdout_opened") is False
        and overview.get("winner_selected") is False,
        "bind the exact 105-owner, 110-path V22 published evidence history",
    )
    inputs_raw, _ = read_owner(V22["inputs"][0], V22["inputs"][1])
    inputs = strict_json(inputs_raw, "independently published V22 graph inputs")
    require(
        inputs.get("schema") == "rebar-candidate-current-overview-v22-inputs"
        and inputs.get("version") == 22
        and inputs.get("repository_evidence_owner_count")
        == V22_EVIDENCE_OWNER_COUNT
        and inputs.get("all_digest_addressed_history_path_count")
        == V22_AUTHENTICATED_REFERENCE_COUNT
        and inputs.get("preserved_v21_repository_evidence_owner_count")
        == V21_EVIDENCE_OWNER_COUNT
        and inputs.get("preserved_v21_digest_addressed_history_path_count")
        == V21_AUTHENTICATED_REFERENCE_COUNT
        and inputs.get("current_source_owner_count") == 25
        and inputs.get("suite_count") == SUITE_COUNT
        and inputs.get("full_case_denominator") == CASE_DENOMINATOR
        and inputs.get("candidate_qualified_count") == 0
        and inputs.get("performance") == "NOT MEASURED"
        and inputs.get("memory") == "NOT MEASURED"
        and inputs.get("final_holdout_opened") is False
        and inputs.get("winner_selected") is False,
        "reject changed independently published V22 graph inputs",
    )
    families = overview.get("families")
    require(type(families) is list, "require all actual V22 candidate families")
    rust_families = [
        family for family in families
        if type(family) is dict and family.get("family") == "rust"
    ]
    require(
        len(rust_families) == 1
        and rust_families[0].get("correctness") == "FAILED; NOT QUALIFIED"
        and rust_families[0].get("performance") == "NOT MEASURED"
        and rust_families[0].get("owned_sources")
        == [
            {"path": path, "sha256": fingerprint}
            for path, fingerprint, _ in RUST_OWNERS
        ],
        "preserve all nine actually owned, unqualified Rust source paths",
    )
    rust_graph = rust_families[0]
    frozen_correctness = rust_graph.get("correctness_evidence")
    require(
        type(frozen_correctness) is dict
        and frozen_correctness.get("actual_semantic_mismatch_count")
        == RUST_HISTORICAL_MISMATCH_COUNT
        and frozen_correctness.get("verified_passing_case_executions")
        == RUST_HISTORICAL_PASSING_CASE_COUNT
        and frozen_correctness.get("qualified_case_executions") == 0
        and frozen_correctness.get("passed_suite_count") == 8
        and frozen_correctness.get("failed_suite_ids")
        == [
            "public_types_v1",
            "substitution_v2",
            "shape_v2",
            "public_surface_v19",
            "subinterpreter_v2",
        ],
        "never upgrade a failed historical Rust campaign to a qualification",
    )
    expected_graph_history = [
        {"path": path, "sha256": fingerprint}
        for path, fingerprint, _ in RUST_HISTORY[4:]
    ]
    require(
        rust_graph.get("subordinate_evidence") == expected_graph_history,
        "preserve all 12 actual specialist failure and receipt owners",
    )
    for key, index in (
        ("archive", 0),
        ("receipt", 1),
        ("worker_archive", 2),
        ("worker_receipt", 3),
    ):
        observed = frozen_correctness.get(key)
        require(
            type(observed) is dict
            and observed.get("path") == RUST_HISTORY[index][0]
            and observed.get("sha256") == RUST_HISTORY[index][1],
            "reject a substituted frozen Rust aggregate or worker owner",
        )
    history: dict[str, bytes] = {}
    for relative, fingerprint, size in RUST_HISTORY:
        raw, owners[relative] = read_owner(
            relative,
            fingerprint,
            size,
            maximum=MAX_COMPRESSED_BYTES,
            private=True,
        )
        history[relative] = raw
    for offset, candidate_status, mismatches in (
        (0, "FAIL", None),
        (2, "FAIL", None),
        (4, "PASS", 0),
        (6, "PASS", 0),
        (8, "FAIL", RUST_HISTORICAL_PUBLIC_TYPE_MISMATCH_COUNT),
        (10, "FAIL", RUST_HISTORICAL_SHAPE_MISMATCH_COUNT),
        (12, "FAIL", RUST_HISTORICAL_SUBSTITUTION_MISMATCH_COUNT),
        (14, "FAIL", None),
    ):
        archive = RUST_HISTORY[offset]
        receipt = RUST_HISTORY[offset + 1]
        document = strict_json(history[receipt[0]], receipt[0])
        require_exact_receipt(
            document,
            archive,
            candidate_status=candidate_status,
            mismatch_count=mismatches,
        )
    aggregate_receipt = strict_json(
        history[RUST_HISTORY[1][0]],
        RUST_HISTORY[1][0],
    )
    aggregate = decompress_document(
        history[RUST_HISTORY[0][0]],
        RUST_HISTORY[0][0],
        expected_uncompressed_sha256=aggregate_receipt.get(
            "uncompressed_sha256"
        ),
        expected_uncompressed_bytes=aggregate_receipt.get(
            "uncompressed_bytes"
        ),
    )
    require(
        aggregate.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v5-actual-complete-candidate"
        and aggregate.get("status") == "FAIL"
        and aggregate.get("candidate_family") == "rust"
        and aggregate.get("suite_count") == SUITE_COUNT
        and aggregate.get("case_execution_denominator") == CASE_DENOMINATOR
        and aggregate.get("candidate_qualified") is False
        and aggregate.get("clock_samples") == 0
        and aggregate.get("hidden_cases_read") == 0
        and aggregate.get("performance") == "NOT MEASURED",
        "preserve the entire original failed V5 Rust matching gate",
    )
    worker_receipt = strict_json(
        history[RUST_HISTORY[3][0]],
        RUST_HISTORY[3][0],
    )
    worker = decompress_document(
        history[RUST_HISTORY[2][0]],
        RUST_HISTORY[2][0],
        expected_uncompressed_sha256=worker_receipt.get(
            "uncompressed_sha256"
        ),
        expected_uncompressed_bytes=worker_receipt.get(
            "uncompressed_bytes"
        ),
    )
    require(
        worker.get("schema")
        == "rebar-frozen-python-re-p0-candidate-worker-v3-complete-candidate-evaluation"
        and worker.get("status") == "FAIL"
        and worker.get("candidate_family") == "rust"
        and worker.get("case_execution_denominator") == CASE_DENOMINATOR
        and worker.get("suite_count") == SUITE_COUNT
        and worker.get("candidate_qualified") is False,
        "never replace the actual failed complete Rust suite worker",
    )
    surfaces = verify_public_surface(worker, surface_reference)
    for index, suite, case_count, mismatch_count in (
        (8, "public_types_v1", 6912,
         RUST_HISTORICAL_PUBLIC_TYPE_MISMATCH_COUNT),
        (10, "shape_v2", 10240,
         RUST_HISTORICAL_SHAPE_MISMATCH_COUNT),
        (12, "substitution_v2", 5120,
         RUST_HISTORICAL_SUBSTITUTION_MISMATCH_COUNT),
    ):
        report = decompress_document(
            history[RUST_HISTORY[index][0]],
            RUST_HISTORY[index][0],
        )
        require(
            report.get("status") == "FAIL"
            and report.get("candidate_family") == "rust"
            and report.get("case_count") == case_count
            and report.get("mismatch_count") == mismatch_count
            and type(report.get("all_mismatches")) is list
            and len(report["all_mismatches"]) == mismatch_count,
            "never omit a genuine complete original Rust specialist failure: "
            + suite,
        )
        if suite == "public_types_v1":
            require(
                positive_counts(report.get("mismatches_by_cohort"))
                == PUBLIC_TYPE_MISMATCH_COHORTS,
                "preserve all 248 exact Rust public type mismatch records",
            )
        if suite == "substitution_v2":
            require(
                positive_counts(report.get("mismatches_by_cohort"))
                == SUBSTITUTION_MISMATCH_COHORTS
                and report.get("mismatches_by_api")
                == {
                    "match.expand": 0,
                    "module.sub": 84,
                    "module.subn": 84,
                    "pattern.sub": 84,
                    "pattern.subn": 84,
                },
                "preserve all 336 exact nested-buffer and hash failures",
            )
        if suite == "shape_v2":
            require(
                report.get("all_mismatches_preserved") is True
                and report.get("mismatches_by_target")
                == {
                    "both-direct": 1104,
                    "both-wrapped": 0,
                    "callback-error": 0,
                    "callback-return": 0,
                    "subject-direct": 0,
                    "subject-wrapped": 0,
                    "template-direct": 288,
                    "template-wrapped": 0,
                },
                "preserve all 1,392 original shape-changing buffer failures",
            )
    managed = decompress_document(
        history[RUST_HISTORY[4][0]],
        RUST_HISTORY[4][0],
    )
    scanner = decompress_document(
        history[RUST_HISTORY[6][0]],
        RUST_HISTORY[6][0],
    )
    require(
        managed.get("status") == "PASS"
        and managed.get("candidate_family") == "rust"
        and managed.get("case_count") == 1024
        and managed.get("mismatch_count") == 0
        and scanner.get("status") == "PASS"
        and scanner.get("candidate_family") == "rust"
        and scanner.get("case_count") == 2854
        and scanner.get("mismatch_count") == 0,
        "never regress or erase historical managed-buffer and scanner passes",
    )
    interpreter = decompress_document(
        history[RUST_HISTORY[14][0]],
        RUST_HISTORY[14][0],
    )
    require(
        interpreter.get("status") == "FAIL"
        and interpreter.get("candidate_family") == "rust",
        "never upgrade unmeasured original Rust interpreter execution",
    )
    c_raw: bytes | None = None
    c_receipt_raw: bytes | None = None
    for position, (relative, fingerprint, size) in enumerate(ACTUAL_C_FAILURE):
        raw, owners[relative] = read_owner(
            relative,
            fingerprint,
            size,
            maximum=MAX_COMPRESSED_BYTES,
            private=True,
        )
        if position == 0:
            c_raw = raw
        else:
            c_receipt_raw = raw
    require(type(c_raw) is bytes and type(c_receipt_raw) is bytes,
            "preserve both actual corrected-C failure evidence owners")
    c_receipt = strict_json(c_receipt_raw, ACTUAL_C_FAILURE[1][0])
    require_exact_receipt(
        c_receipt,
        ACTUAL_C_FAILURE[0],
        family="c",
        candidate_status="FAIL",
    )
    c_report = decompress_document(
        c_raw,
        ACTUAL_C_FAILURE[0][0],
        expected_uncompressed_sha256=c_receipt.get("uncompressed_sha256"),
        expected_uncompressed_bytes=c_receipt.get("uncompressed_bytes"),
    )
    require(
        c_report.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v2-actual-recovered-campaign"
        and c_report.get("status") == "FAIL"
        and c_report.get("family") == "c"
        and c_report.get("label") == "phase2-v9-original-p0"
        and c_report.get("suite_count") == SUITE_COUNT
        and c_report.get("case_execution_denominator") == CASE_DENOMINATOR
        and c_report.get("completed_suite_count") == "NOT MEASURED"
        and c_report.get("verified_passing_case_count") == "NOT MEASURED"
        and c_report.get("semantic_mismatch_count") == "NOT MEASURED"
        and c_report.get("infrastructure_failure_count") == 1
        and c_report.get("candidate_qualified") is False
        and c_report.get("original_native_restored") is True
        and c_report.get("historical_evidence_owner_count")
        == V21_EVIDENCE_OWNER_COUNT
        and c_report.get("historical_authenticated_reference_count")
        == V21_AUTHENTICATED_REFERENCE_COUNT
        and c_report.get("clock_samples") == 0
        and c_report.get("hidden_cases_read") == 0
        and c_report.get("performance") == "NOT MEASURED"
        and c_report.get("holdout") == "NOT OPENED",
        "preserve the actual recovered-C runner failure without fabrication",
    )
    frozen_c = inputs.get("corrected_c_original_campaign")
    require(
        type(frozen_c) is dict
        and frozen_c.get("status") == "FAIL"
        and frozen_c.get("family") == "c"
        and frozen_c.get("label") == "phase2-v9-original-p0"
        and frozen_c.get("semantic_mismatch_count") == "NOT MEASURED"
        and frozen_c.get("infrastructure_failure_count") == 1
        and frozen_c.get("original_canonical_native_restored") is True
        and type(frozen_c.get("archive")) is dict
        and frozen_c["archive"].get("path") == ACTUAL_C_FAILURE[0][0]
        and frozen_c["archive"].get("sha256") == ACTUAL_C_FAILURE[0][1]
        and type(frozen_c.get("receipt")) is dict
        and frozen_c["receipt"].get("path") == ACTUAL_C_FAILURE[1][0]
        and frozen_c["receipt"].get("sha256") == ACTUAL_C_FAILURE[1][1],
        "bind V22 to both genuine unqualified corrected-C report owners",
    )
    derived = repaired_source(
        original_raw,
        ORIGINAL_SHA256,
        ORIGINAL_BYTES,
    )
    expected = contract_document(source_sha256, protocol_sha256)
    if contract_sha256 is not None:
        raw, owners[CONTRACT_RELATIVE] = read_owner(
            CONTRACT_RELATIVE,
            contract_sha256,
        )
        require(
            canonical(strict_json(raw, "frozen Rust public source contract"))
            == canonical(expected),
            "reject an altered private-only Rust public repair contract",
        )
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "read_only": True,
        "authenticated_owner_count": len(owners),
        "frozen_owners": owners,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "rust_owned_source_count": len(RUST_OWNERS),
        "rust_external_regex_dependency_count": 0,
        "rust_historical_semantic_mismatch_count":
            RUST_HISTORICAL_MISMATCH_COUNT,
        "rust_historical_public_surface_mismatches": surfaces,
        "rust_historical_public_type_mismatches":
            dict(PUBLIC_TYPE_MISMATCH_COHORTS),
        "rust_historical_substitution_mismatches":
            dict(SUBSTITUTION_MISMATCH_COHORTS),
        "rust_historical_shape_mismatch_count":
            RUST_HISTORICAL_SHAPE_MISMATCH_COUNT,
        "rust_historical_matching_status": "FAILED; NOT QUALIFIED",
        "historical_evidence_owner_count": V22_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            V22_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_actual_c_failure_owner_count":
            len(ACTUAL_C_FAILURE),
        "preserved_actual_c_matching_status": "NOT MEASURED",
        "original_source_sha256": ORIGINAL_SHA256,
        "original_source_bytes": ORIGINAL_BYTES,
        "original_candidate_modified": False,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        "derived_source_materialized": False,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_compiler_processes": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "source_apply_count": 0,
        "workspace_mutations": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "candidate_correctness": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return result, derived


def private_directory(parent: int, component: str) -> int:
    require(
        type(component) is str
        and bool(component)
        and component not in (".", "..")
        and "/" not in component
        and "\\" not in component,
        "reject an escaped or ambiguous private directory component",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    descriptor = os.open(component, flags, dir_fd=parent)
    try:
        owner = os.fstat(descriptor)
        require(
            stat.S_ISDIR(owner.st_mode)
            and stat.S_IMODE(owner.st_mode) == 0o700
            and owner.st_uid == os.geteuid(),
            "require an exact user-owned, no-follow, private 0700 source directory",
        )
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def apply_private(
    snapshot_root: str,
    derived: bytes,
) -> dict[str, Any]:
    require(
        type(snapshot_root) is str and 0 < len(snapshot_root) <= 512,
        "require one explicit bounded private Rust snapshot",
    )
    parsed = PurePosixPath(snapshot_root)
    pieces = parsed.parts
    require(
        parsed.is_absolute()
        and str(parsed) == snapshot_root
        and len(pieces) == 5
        and pieces[0] == "/"
        and pieces[1] == "tmp"
        and pieces[2].startswith(PRIVATE_ROOT_PREFIX)
        and PRIVATE_ROOT_FAMILY in pieces[2]
        and all(
            character.isascii()
            and (character.isalnum() or character in "-_")
            for character in pieces[2]
        )
        and pieces[3] in PHASE_NAMES
        and pieces[4] == "source",
        "apply only to a fresh independently owned /tmp Rust phase snapshot",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    temp = os.open("/tmp", flags)
    root = phase = sibling = source = candidates = destination = None
    try:
        root = private_directory(temp, pieces[2])
        phase = private_directory(root, pieces[3])
        other = (
            "reference-b"
            if pieces[3] == "reference-a"
            else "reference-a"
        )
        sibling = private_directory(root, other)
        actual_phase = os.fstat(phase)
        actual_sibling = os.fstat(sibling)
        require(
            (actual_phase.st_dev, actual_phase.st_ino)
            != (actual_sibling.st_dev, actual_sibling.st_ino),
            "never alias the two independently built Rust reference phases",
        )
        source = private_directory(phase, "source")
        candidates = private_directory(source, "candidates")
        original_before, original_owner = read_owner(
            ORIGINAL_RELATIVE,
            ORIGINAL_SHA256,
            ORIGINAL_BYTES,
        )
        require(
            repaired_source(
                original_before,
                ORIGINAL_SHA256,
                ORIGINAL_BYTES,
            ) == derived,
            "refuse private application after original source substitution",
        )
        destination = os.open(
            "rust_candidate.py",
            (
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            ),
            0o600,
            dir_fd=candidates,
        )
        before = os.fstat(destination)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "create only one fresh, private, unlinked Rust snapshot owner",
        )
        offset = 0
        while offset < len(derived):
            written = os.write(destination, derived[offset:])
            require(
                type(written) is int and written > 0,
                "never publish incomplete private Rust snapshot bytes",
            )
            offset += written
        os.fsync(destination)
        after = os.fstat(destination)
        require(
            (
                before.st_dev,
                before.st_ino,
                before.st_uid,
                before.st_nlink,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_uid,
                after.st_nlink,
            )
            and after.st_size == DERIVED_BYTES,
            "reject replacement of the private Rust snapshot during creation",
        )
        os.close(destination)
        destination = None
        verifier = os.open(
            "rust_candidate.py",
            (
                os.O_RDONLY
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            ),
            dir_fd=candidates,
        )
        try:
            information = os.fstat(verifier)
            require(
                (
                    information.st_dev,
                    information.st_ino,
                    information.st_uid,
                    information.st_nlink,
                    information.st_size,
                )
                == (
                    after.st_dev,
                    after.st_ino,
                    after.st_uid,
                    after.st_nlink,
                    after.st_size,
                ),
                "reject substituted private Rust public source identity",
            )
            blocks: list[bytes] = []
            remaining = information.st_size
            while remaining:
                part = os.read(verifier, min(remaining, 1024 * 1024))
                require(bool(part),
                        "reject truncated private Rust public source bytes")
                blocks.append(part)
                remaining -= len(part)
            require(
                os.read(verifier, 1) == b""
                and b"".join(blocks) == derived
                and digest(b"".join(blocks)) == DERIVED_SHA256,
                "reject changed independently owned private Rust derived bytes",
            )
        finally:
            os.close(verifier)
        os.fsync(candidates)
        unchanged_raw, unchanged_owner = read_owner(
            ORIGINAL_RELATIVE,
            ORIGINAL_SHA256,
            ORIGINAL_BYTES,
        )
        require(
            unchanged_raw == original_before
            and unchanged_owner == original_owner,
            "never mutate or substitute the real working-tree Rust candidate",
        )
        return {
            "schema": SCHEMA + "-private-snapshot-application",
            "status": "PASS",
            "phase": pieces[3],
            "snapshot_root": snapshot_root,
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_bytes": DERIVED_BYTES,
            "source_apply_count": 1,
            "original_candidate_modified": False,
            "candidate_correctness": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "actual_candidate_imports": 0,
            "actual_candidate_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
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
        for descriptor in (candidates, source, sibling, phase, root, temp):
            if descriptor is not None:
                os.close(descriptor)


def parse_arguments(
    arguments: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(
            all(
                getattr(options, name) is None
                for name in (
                    "source_sha256",
                    "protocol_sha256",
                    "contract_sha256",
                    "snapshot_root",
                )
            ),
            "a synthetic self-test cannot authorize a source or snapshot",
        )
        return options
    for name in ("source_sha256", "protocol_sha256"):
        valid_digest(getattr(options, name), name)
    if options.emit_contract:
        require(
            options.contract_sha256 is None
            and options.snapshot_root is None,
            "source-only contract emission cannot apply or assume a snapshot",
        )
        return options
    valid_digest(options.contract_sha256, "contract_sha256")
    if options.verify_frozen_context:
        require(
            options.snapshot_root is None,
            "read-only verification cannot select or mutate a snapshot",
        )
        return options
    require(
        type(options.snapshot_root) is str,
        "actual source application requires one explicit private snapshot",
    )
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            document = self_test()
        elif options.emit_contract:
            with source_only_boundary() as effects:
                document = contract_document(
                    options.source_sha256,
                    options.protocol_sha256,
                )
                require(
                    all(
                        value == 0
                        for name, value in effects.items()
                        if not name.startswith("blocked_")
                    ),
                    "pure contract emission attempted a real side effect",
                )
        else:
            context, derived = verify_context(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
            if options.verify_frozen_context:
                document = context
            else:
                document = apply_private(options.snapshot_root, derived)
        raw = canonical(document)
        require(
            len(raw) <= MAX_REPORT_BYTES,
            "never emit an unbounded Rust public source-freeze report",
        )
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if document.get("status", "PASS") == "PASS" else 1
    except BaseException as error:
        document = {
            "schema": SCHEMA + "-gate-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:8192],
            "candidate_correctness": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "actual_candidate_imports": 0,
            "actual_candidate_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "actual_native_libraries_loaded": 0,
            "source_apply_count": 0,
            "workspace_mutations": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(document))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
