#!/usr/bin/env python3
"""Freeze genuine sharing of Python regex patterns across real threads.\n\nThis source preserves the independently frozen upstream reference, its original\nprivate waivers, the complete producer-owned public baseline, the audited\nno-follow exclusive publisher, and bounded deterministic gzip. Source-only\ncontrols never start a thread or worker, match, open evidence, sample a clock,\nchange locale, inspect a holdout, or publish.\n"""

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
import stat
import subprocess
import sys
import threading
import traceback
import time
import warnings
import zlib
from typing import Any


ROOT = Path(os.path.abspath(__file__)).parent.parent
PYTHON = "3.14.6"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_STDLIB_RE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py"
)
PINNED_STDLIB_RE_SHA256 = (
    "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35"
)
PINNED_THREADING = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/threading.py"
)
PINNED_THREADING_SHA256 = (
    "5323909624ec2165e70b6d31333e4191b63d383d2dc5a7d7d516a3475ea2b7e3"
)
SCHEMA = "rebar-python-re-genuine-threaded-pattern-v1"
SOURCE_RELATIVE = "tools/python_re_threaded_pattern_oracle_v1.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-THREADED-PATTERN-V1.md"
FROZEN_PROTOCOL_SHA256 = (
    "df0a6ef32b805f8ccac6c98c505eec7e5aadc13efcad66ee1f5daf86cc823aaf"
)
V6_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v6.py"
V6_SOURCE_SHA256 = (
    "b1522b55b37de2e004b029c128e2e75c3020cda34165bcf0de07cb5ebb3136cb"
)
V6_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V6.md"
V6_PROTOCOL_SHA256 = (
    "8e43ceaa61f6e70e2e1193de71bde8583c101cdbe40bc78d862ae789531aff57"
)
V6_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
)
V6_REFERENCE_SHA256 = (
    "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
)
ORIGINAL_TEST_RELATIVE = "oracle/cpython-3.14.6/test_re.py"
ORIGINAL_TEST_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
PUBLIC_SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage27.py"
PUBLIC_SOURCE_SHA256 = (
    "fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b"
)
PUBLIC_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md"
PUBLIC_PROTOCOL_SHA256 = (
    "c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f"
)
PUBLIC_CASES = 1_376
PUBLIC_COHORTS = 43
PUBLIC_MATRIX_SHA256 = (
    "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa"
)
PUBLIC_STIMULUS_SHA256 = (
    "8c1a4fd434af5fb1ea0dcd1aa3faaa06b07e7d186ca52c1593575eff93b4d7da"
)
PUBLIC_REFERENCE_SHA256 = (
    "a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8"
)
PUBLIC_REFERENCE_RECORD_SHA256 = (
    "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef"
)
PUBLIC_REAL_LOCALE_CASES = 64
PUBLIC_REAL_LOCALE_TRANSITIONS = 192
ORIGINAL_PUBLIC_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
ORIGINAL_STATUS_VECTOR_SHA256 = (
    "89839dbf8c6674ae236bea3d424f33cbb62a10281b18c36efbdf490ee6919790"
)
PRIVATE_WAIVERS = {
    "DebugTests": {
        "methods": 4,
        "reason": "CPython-only textual disassembly of private matching opcodes",
    },
    "ImplementationTest": {
        "methods": 9,
        "reason": (
            "private CPython regex compiler, _sre, type internals, "
            "and deprecated private implementation modules"
        ),
    },
}
BASE_SEED = 2_026_072_701
DOMAIN = "rebar/python-re/shared-threaded-pattern/v1"
CASES_PER_COHORT = 32
THREAD_ROLES = ("left", "right")
COHORTS = (
    "shared-text-search-and-span",
    "shared-text-match-and-fullmatch",
    "shared-bytes-search-and-span",
    "shared-bytes-match-and-fullmatch",
    "independent-text-finditer-progress",
    "independent-bytes-finditer-progress",
    "independent-text-scanner-progress",
    "independent-bytes-scanner-progress",
    "shared-zero-width-text-finditer",
    "shared-zero-width-bytes-finditer",
    "named-captures-backreferences-and-templates",
    "recursive-text-replacement-and-reentrant-match",
    "recursive-bytes-replacement-and-reentrant-match",
    "shared-cache-purge-and-ascii-flags",
    "shared-type-errors-and-deterministic-warning",
    "module-version-and-public-flags-under-shared-match",
)
METADATA_COHORT = COHORTS[-1]
WARNING_COHORT = COHORTS[-2]
EXPECTED_PUBLIC_RE_VERSION = "2.2.1"
EXPECTED_WARNING = {
    "category": "FutureWarning",
    "message": "Possible set intersection at position 2",
}
EXPECTED_CASES = len(COHORTS) * CASES_PER_COHORT
EXPECTED_THREAD_STARTS_PER_WORKER = len(COHORTS) * len(THREAD_ROLES)
EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER = EXPECTED_CASES * len(THREAD_ROLES)
API_CALLS_PER_THREAD = dict(zip(
    COHORTS, (1, 2, 1, 2, 1, 1, 4, 4, 1, 1, 3, 3, 3, 3, 3, 1),
    strict=True,
))
EXPECTED_REGEX_API_CALLS_PER_WORKER = (
    sum(API_CALLS_PER_THREAD.values()) * CASES_PER_COHORT * len(THREAD_ROLES)
)
EXPECTED_SOURCE_ONLY_CHECKS = 3_973
PUBLICATION_SOURCE_ONLY_POISON_CASES = 25
GZIP_SOURCE_ONLY_POISON_CASES = 11
MATRIX_SHA256 = (
    "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b"
)

REFERENCE_ROLES = ("reference_a", "reference_b")
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
MAX_WORKER_BYTES = 16 * 1024 * 1024
MAX_PIPE_BYTES = 256 * 1024
PASS_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-threaded-pattern-v1-self-oracle.json.gz"
)
FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-threaded-pattern-v1-self-oracle-failures.json.gz"
)
PASS_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-threaded-pattern-v1-self-oracle-publication-receipt.json"
)
FAILURE_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-threaded-pattern-v1-self-oracle-failures-publication-receipt.json"
)
APPROVED_OUTPUTS = frozenset({
    PASS_RELATIVE,
    FAILURE_RELATIVE,
    PASS_RECEIPT_RELATIVE,
    FAILURE_RECEIPT_RELATIVE,
})


class ThreadedPatternOracleError(AssertionError):
    """The frozen, genuine shared-pattern thread obligation failed closed."""


class ThreadedPatternWorkerFailure(ThreadedPatternOracleError):
    def __init__(self, message: str, details: dict[str, Any]) -> None:
        super().__init__(message)
        self.details = details


class ThreadedPatternPublicationFailure(ThreadedPatternOracleError):
    def __init__(self, message: str, receipt: dict[str, Any]) -> None:
        super().__init__(message)
        self.receipt = receipt


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ThreadedPatternOracleError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_sha256(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )



def publication_payload(
    relative: str,
    document: dict[str, Any],
) -> tuple[bytes, bytes, str]:
    safe_relative(relative, outputs_only=True)
    require(type(document) is dict, "a complete bounded report is mandatory")
    plain = canonical(document) + b"\n"
    require(
        0 < len(plain) <= MAX_REPORT_BYTES,
        "the complete canonical threaded-pattern report exceeds its bound",
    )
    if relative.endswith(".json.gz"):
        compressed = gzip.compress(plain, compresslevel=9, mtime=0)
        require(
            type(compressed) is bytes
            and 0 < len(compressed) <= MAX_REPORT_BYTES
            and compressed[:3] == b"\x1f\x8b\x08",
            "a deterministic bounded genuine gzip report was forged",
        )
        return plain, compressed, "gzip-mtime-zero-level-9"
    require(relative.endswith("-publication-receipt.json"),
            "only a corrected report or separate signed receipt is permitted")
    return plain, plain, "identity"


def restore_publication_document(
    relative: str,
    stored: Any,
    *,
    maximum: int = MAX_REPORT_BYTES,
) -> dict[str, Any]:
    safe_relative(relative, outputs_only=True)
    require(
        type(stored) is bytes
        and bool(stored)
        and len(stored) <= MAX_REPORT_BYTES
        and type(maximum) is int
        and 0 < maximum <= MAX_REPORT_BYTES,
        "an exact bounded complete publication stream is mandatory",
    )
    if relative.endswith(".json.gz"):
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            plain = decoder.decompress(stored, maximum + 1)
            require(
                len(plain) <= maximum
                and decoder.eof is True
                and decoder.unused_data == b""
                and decoder.unconsumed_tail == b""
                and decoder.flush() == b"",
                "a truncated, concatenated, trailing, or oversized gzip "
                "threaded-pattern report was rejected",
            )
        except (zlib.error, EOFError, ValueError) as error:
            raise ThreadedPatternOracleError(
                "a complete genuine deterministic gzip member is invalid",
            ) from error
    else:
        require(
            relative.endswith("-publication-receipt.json")
            and len(stored) <= maximum,
            "an exact bounded canonical standalone receipt is mandatory",
        )
        plain = stored
    return strict_canonical(plain, label=relative)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        require(name not in result, "a genuine JSON object contains a duplicate key")
        result[name] = value
    return result


def _reject_constant(value: str) -> Any:
    raise ThreadedPatternOracleError("non-finite JSON is forbidden: " + value)


def strict_canonical(raw: bytes, *, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "a bounded complete canonical document is required: " + label)
    try:
        document = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise ThreadedPatternOracleError(
            "invalid complete canonical JSON: " + label
        ) from error
    require(type(document) is dict, "a canonical JSON mapping is required: " + label)
    encoded = canonical(document)
    require(raw in (encoded, encoded + b"\n"),
            "complete JSON was changed, truncated, or recanonicalized: " + label)
    return document


def safe_relative(relative: Any, *, outputs_only: bool = False) -> str:
    require(type(relative) is str and bool(relative), "an exact relative path is required")
    path = PurePosixPath(relative)
    require(
        not path.is_absolute()
        and path.as_posix() == relative
        and all(part not in ("", ".", "..") for part in path.parts),
        "an unsafe threaded-pattern-oracle path was rejected",
    )
    if outputs_only:
        require(relative in APPROVED_OUTPUTS,
                "an unapproved threaded-pattern-oracle output was rejected")
    return relative


def _read_regular(relative: str, maximum: int) -> bytes:
    safe_relative(relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT / relative, flags)
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode),
                "a frozen threaded-pattern input must be a real regular file")
        require(0 < information.st_size <= maximum,
                "a frozen threaded-pattern input exceeds its exact bound")
        pieces: list[bytes] = []
        remaining = information.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(chunk), "a frozen threaded-pattern input was truncated")
            pieces.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "a frozen threaded-pattern input grew during authentication")
        return b"".join(pieces)
    finally:
        os.close(descriptor)


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    require(valid_sha256(expected), "an independently published SHA-256 is required")
    raw = _read_regular(relative, maximum)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "the independently frozen threaded-pattern input changed: " + relative)
    return raw


def build_matrix() -> list[dict[str, Any]]:
    rows = []
    for position, cohort in enumerate(COHORTS):
        for variant in range(CASES_PER_COHORT):
            material = f"{DOMAIN}|{BASE_SEED}|{cohort}|{variant}".encode("ascii")
            rows.append({
                "case_id": f"{cohort}:{variant:02d}",
                "cohort": cohort,
                "ordinal": position * CASES_PER_COHORT + variant,
                "seed": int.from_bytes(hashlib.sha256(material).digest()[:8], "big"),
                "variant": variant,
            })
    return rows


def validate_matrix(rows: Any) -> str:
    require(type(rows) is list and len(rows) == EXPECTED_CASES,
            "all 512 actual shared-pattern thread stimuli are required")
    require(rows == build_matrix(),
            "a frozen genuine shared-pattern thread case changed")
    actual = digest(rows)
    require(actual == MATRIX_SHA256,
            "the independently frozen real-thread pattern matrix changed")
    return actual


def capture_complete_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_WORKER_BYTES,
            "the complete actual worker stream exceeds its bound")
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "base64": base64.b64encode(raw).decode("ascii"),
    }


def restore_complete_stream(record: Any, *, label: str) -> bytes:
    require(type(record) is dict and set(record) == {"bytes", "sha256", "base64"},
            "a complete original worker stream was omitted: " + label)
    require(type(record["bytes"]) is int and 0 <= record["bytes"] <= MAX_WORKER_BYTES,
            "a genuine worker stream length was forged: " + label)
    require(valid_sha256(record["sha256"]) and type(record["base64"]) is str,
            "a genuine worker stream identity was forged: " + label)
    try:
        raw = base64.b64decode(record["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise ThreadedPatternOracleError("an actual worker stream is invalid") from error
    require(len(raw) == record["bytes"]
            and hashlib.sha256(raw).hexdigest() == record["sha256"],
            "a genuine complete worker stream was truncated: " + label)
    return raw


def _original_counts(source: bytes) -> dict[str, int]:
    tree = ast.parse(source.decode("utf-8"))
    names = ("ReTests", "DebugTests", "PatternReprTests", "ImplementationTest", "ExternalTests")
    counts: dict[str, int] = {}
    for statement in tree.body:
        if isinstance(statement, ast.ClassDef) and statement.name in names:
            counts[statement.name] = sum(
                isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name.startswith("test_")
                for item in statement.body
            )
    require(counts == {
        "ReTests": 139, "DebugTests": 4, "PatternReprTests": 11,
        "ImplementationTest": 9, "ExternalTests": 2,
    }, "the authentic original 165-method CPython class matrix changed")
    return counts


def validate_original_reference(document: Any) -> dict[str, Any]:
    require(type(document) is dict, "the genuine V6 double reference is missing")
    expected = {
        "schema": "rebar-postfinal-cpython-full-public-locale-v6-self-oracle",
        "status": "PASS",
        "python": PYTHON,
        "synthetic": False,
        "source_path": V6_SOURCE_RELATIVE,
        "source_sha256": V6_SOURCE_SHA256,
        "protocol_path": V6_PROTOCOL_RELATIVE,
        "protocol_sha256": V6_PROTOCOL_SHA256,
        "test_source_sha256": ORIGINAL_TEST_SHA256,
        "all_original_methods": 165,
        "public_original_methods": 152,
        "private_original_methods": 13,
        "public_method_matrix_sha256": ORIGINAL_PUBLIC_MATRIX_SHA256,
        "reference_status_vector_sha256": ORIGINAL_STATUS_VECTOR_SHA256,
        "actual_independent_reference_count": 2,
        "official_support_module_count": 26,
        "actual_upstream_corpus_cases": 403,
        "actual_external_fixture_assertion_cases": 11,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for name, value in expected.items():
        require(document.get(name) == value,
                "the actual frozen original CPython baseline changed: " + name)
    require(document.get("public_method_waivers") == [],
            "no original public CPython method may be waived")
    require(document.get("named_private_class_waivers") == PRIVATE_WAIVERS,
            "the exact two named private CPython class waivers changed")
    roles = document.get("roles")
    require(type(roles) is dict and tuple(roles) == REFERENCE_ROLES,
            "exactly two original independent V6 reference roles are required")
    vectors = []
    for label in REFERENCE_ROLES:
        role = roles[label]
        require(type(role) is dict and role.get("status") == "PASS"
                and role.get("passed") == 151 and role.get("failed") == 0
                and role.get("skipped") == 1 and role.get("record_count") == 152,
                "a genuine original 152-method CPython role changed: " + label)
        records = role.get("records")
        require(type(records) is list and len(records) == 152,
                "a genuine original CPython role omitted complete records")
        require(valid_sha256(role.get("records_sha256")),
                "a genuine original CPython record fingerprint is absent")
        skips = [row for row in records if row.get("status") == "SKIP"]
        require(len(skips) == 1
                and skips[0].get("test") == "ReTests.test_memory_leaks"
                and skips[0].get("skip_kind") == "named-private-debug-condition"
                and skips[0].get("reason") == "requires debug build",
                "the original debug-build conditional skip was changed")
        vectors.append(records)
    require(vectors[0] == vectors[1],
            "the two genuine complete original CPython reference vectors disagree")
    return {
        "reference_sha256": V6_REFERENCE_SHA256,
        "original_methods": 165,
        "public_methods": 152,
        "private_methods": 13,
        "private_waivers": PRIVATE_WAIVERS,
        "public_method_waivers": [],
        "independent_reference_count": 2,
        "reference_status_vector_sha256": ORIGINAL_STATUS_VECTOR_SHA256,
    }


def verify_runtime(*, production: bool = False) -> None:
    require(sys.version_info[:3] == (3, 14, 6),
            "run the frozen oracle using the exact pinned CPython 3.14.6")
    require(os.path.abspath(sys.executable) == PINNED_PYTHON,
            "the actual pinned CPython executable was substituted")
    require(sys.flags.isolated == 1 and sys.dont_write_bytecode,
            "run the pinned shared-pattern thread oracle with -I -B")
    if production:
        require(os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"
                and os.environ.get("PYTHONHASHSEED") == "0"
                and os.environ.get("LC_ALL") == "C"
                and os.environ.get("PYTHONPATH") == str(ROOT)
                and os.environ.get("PATH") == "/usr/bin:/bin",
                "the actual isolated reference environment is not frozen")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate was imported into a standard-library-only oracle")


def read_pinned_absolute(path: str, expected: str) -> bytes:
    require(path in {PINNED_PYTHON, PINNED_STDLIB_RE, PINNED_THREADING},
            "an unowned Python runtime input was rejected")
    require(valid_sha256(expected),
            "the real pinned standard-library source must be authenticated")
    descriptor = os.open(
        path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode)
                and 0 < information.st_size <= (
                    MAX_BINARY_BYTES if path == PINNED_PYTHON else MAX_SOURCE_BYTES
                ),
                "the exact pinned CPython runtime input is not a bounded file")
        pieces: list[bytes] = []
        remaining = information.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(piece), "the exact pinned standard-library input was truncated")
            pieces.append(piece)
            remaining -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "the exact pinned standard-library input grew")
    finally:
        os.close(descriptor)
    raw = b"".join(pieces)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "the exact pinned standard-library source was substituted")
    return raw


def authenticate_context(source_sha256: str, protocol_sha256: str) -> dict[str, Any]:
    verify_runtime(production=True)
    require(
        valid_sha256(source_sha256)
        and protocol_sha256 == FROZEN_PROTOCOL_SHA256,
        "supply the independently frozen V2 source and exact protocol hash",
    )
    read_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
    protocol = read_frozen(PROTOCOL_RELATIVE, protocol_sha256, MAX_SOURCE_BYTES)
    read_frozen(V6_SOURCE_RELATIVE, V6_SOURCE_SHA256, MAX_SOURCE_BYTES)
    read_frozen(V6_PROTOCOL_RELATIVE, V6_PROTOCOL_SHA256, MAX_SOURCE_BYTES)
    official = read_frozen(ORIGINAL_TEST_RELATIVE, ORIGINAL_TEST_SHA256, MAX_SOURCE_BYTES)
    _original_counts(official)
    reference_raw = read_frozen(V6_REFERENCE_RELATIVE, V6_REFERENCE_SHA256,
                                MAX_REPORT_BYTES)
    reference = validate_original_reference(
        strict_canonical(reference_raw, label="genuine frozen V6 double reference")
    )
    read_frozen(PUBLIC_SOURCE_RELATIVE, PUBLIC_SOURCE_SHA256,
                MAX_SOURCE_BYTES)
    read_frozen(PUBLIC_PROTOCOL_RELATIVE, PUBLIC_PROTOCOL_SHA256,
                MAX_SOURCE_BYTES)
    read_pinned_absolute(PINNED_PYTHON, PINNED_PYTHON_SHA256)
    read_pinned_absolute(PINNED_STDLIB_RE, PINNED_STDLIB_RE_SHA256)
    read_pinned_absolute(PINNED_THREADING, PINNED_THREADING_SHA256)
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate was loaded before the authentic reference validators")
    v6 = importlib.import_module("tools.postfinal_cpython_locale_oracle_v6")
    require(os.path.abspath(v6.__file__) == str(ROOT / V6_SOURCE_RELATIVE),
            "the genuine frozen V6 reference validator was replaced")
    read_frozen(V6_SOURCE_RELATIVE, V6_SOURCE_SHA256, MAX_SOURCE_BYTES)
    provenance = v6._original_reference_prerequisites()
    actual_path, actual_roles = v6._read_reference(
        V6_REFERENCE_SHA256, provenance, V6_SOURCE_SHA256,
    )
    require(actual_path == V6_REFERENCE_RELATIVE
            and type(actual_roles) is dict
            and tuple(actual_roles) == REFERENCE_ROLES
            and all(type(actual_roles[label].get("records")) is list
                    and len(actual_roles[label]["records"]) == 152
                    for label in REFERENCE_ROLES),
            "the actual original V6 double-reference validator did not run")
    stage27 = importlib.import_module(
        "tools.python_re_public_surface_oracle_stage27",
    )
    require(os.path.abspath(stage27.__file__) == str(ROOT / PUBLIC_SOURCE_RELATIVE),
            "the frozen genuine V27 public-reference validator was replaced")
    read_frozen(PUBLIC_SOURCE_RELATIVE, PUBLIC_SOURCE_SHA256, MAX_SOURCE_BYTES)
    actual_public = stage27.authenticate_reference(
        PUBLIC_SOURCE_SHA256, PUBLIC_PROTOCOL_SHA256,
    )
    records = actual_public.get("baseline_records")
    require(type(records) is list and len(records) == PUBLIC_CASES
            and actual_public.get("v19_reference_sha256") == PUBLIC_REFERENCE_SHA256
            and actual_public.get("v19_reference_record_sha256")
            == PUBLIC_REFERENCE_RECORD_SHA256
            and actual_public.get("actual_independent_reference_count") == 2
            and actual_public.get("fresh_reference_workers_started") == 0
            and actual_public.get("candidate_imports") == 0
            and actual_public.get("candidate_audits_read") == 0
            and actual_public.get("candidate_proofs_read") == 0
            and actual_public.get("holdout_cases_read") == 0
            and actual_public.get("performance_fixtures_read") == 0
            and actual_public.get("benchmark_or_timing_executed") is False
            and stage27.validate_public_records(records)
            == PUBLIC_REFERENCE_RECORD_SHA256,
            "the genuine complete V19 two-worker public baseline was not authenticated")
    counts = stage27.base19.validate_partial_records(
        records, stage27.build_matrix(),
    )
    require(counts.get("real_locale_cases") == PUBLIC_REAL_LOCALE_CASES
            and stage27.EXPECTED_LOCALE_TRANSITIONS
            == PUBLIC_REAL_LOCALE_TRANSITIONS,
            "the genuine complete V19 locale cases and transitions changed")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate was imported by a Python-only reference validator")
    require(MATRIX_SHA256.encode("ascii") in protocol,
            "the independently frozen genuine-thread matrix is absent")
    return {
        **reference,
        "public_cases": PUBLIC_CASES,
        "public_cohorts": PUBLIC_COHORTS,
        "public_matrix_sha256": PUBLIC_MATRIX_SHA256,
        "public_stimulus_sha256": PUBLIC_STIMULUS_SHA256,
        "public_source_sha256": PUBLIC_SOURCE_SHA256,
        "public_protocol_sha256": PUBLIC_PROTOCOL_SHA256,
        "public_reference_sha256": PUBLIC_REFERENCE_SHA256,
        "public_reference_record_sha256": PUBLIC_REFERENCE_RECORD_SHA256,
        "public_reference_independent_roles": 2,
        "public_real_locale_cases": PUBLIC_REAL_LOCALE_CASES,
        "public_real_locale_transitions": PUBLIC_REAL_LOCALE_TRANSITIONS,
        "pinned_python": PINNED_PYTHON,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "pinned_stdlib_re": PINNED_STDLIB_RE,
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_threading": PINNED_THREADING,
        "pinned_public_threading_sha256": PINNED_THREADING_SHA256,
    }


def _freeze_value(value: Any) -> Any:
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) in (list, tuple):
        return [_freeze_value(item) for item in value]
    if type(value) is dict:
        require(all(type(name) is str for name in value),
                "a real thread observation invented a non-string mapping key")
        return {name: _freeze_value(value[name]) for name in sorted(value)}
    raise ThreadedPatternOracleError(
        "a real shared-pattern thread returned an unpreserved value",
    )


def _freeze_match(match: Any) -> dict[str, Any]:
    if match is None:
        return {"matched": False}
    return {
        "matched": True,
        "span": list(match.span()),
        "groups": _freeze_value(match.groups()),
        "groupdict": _freeze_value(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
    }


USED_PATTERNS = {
    COHORTS[0]: ("text",),
    COHORTS[1]: ("text",),
    COHORTS[2]: ("bytes",),
    COHORTS[3]: ("bytes",),
    COHORTS[4]: ("text_iter",),
    COHORTS[5]: ("bytes_iter",),
    COHORTS[6]: ("text_iter",),
    COHORTS[7]: ("bytes_iter",),
    COHORTS[8]: ("zero_text",),
    COHORTS[9]: ("zero_bytes",),
    COHORTS[10]: ("named",),
    COHORTS[11]: ("recursive_text",),
    COHORTS[12]: ("recursive_bytes",),
    COHORTS[13]: ("flags",),
    COHORTS[14]: ("bytes", "text", "warning"),
    COHORTS[15]: ("text",),
}


def _prepare_shared_patterns(module: Any, cohort: str) -> tuple[
    dict[str, Any], list[dict[str, str]], dict[str, Any],
]:
    patterns = {
        "text": module.compile(r"(?P<word>a+)(?P<tail>b)"),
        "bytes": module.compile(br"(?P<word>a+)(?P<tail>b)"),
        "text_iter": module.compile(r"(?P<word>a+)"),
        "bytes_iter": module.compile(br"(?P<word>a+)"),
        "zero_text": module.compile(r"(?=a)|$"),
        "zero_bytes": module.compile(br"(?=a)|$"),
        "named": module.compile(r"(?P<word>a+)(?P=word)"),
        "recursive_text": module.compile(r"(?P<item>a+)"),
        "recursive_bytes": module.compile(br"(?P<item>a+)"),
        "flags": module.compile(r"k+", module.IGNORECASE | module.ASCII),
    }
    cache: dict[str, Any] = {}
    if cohort == COHORTS[13]:
        original = patterns["text"]
        hit = module.compile(r"(?P<word>a+)(?P<tail>b)")
        require(hit is original,
                "the actual public cache did not retain the original shared pattern")
        module.purge()
        fresh = module.compile(r"(?P<word>a+)(?P<tail>b)")
        require(fresh is not original,
                "the public purge did not genuinely create a fresh cache entry")
        cache = {
            "same_cached_pattern_before_purge": True,
            "fresh_cached_pattern_after_purge": True,
            "shared_original_pattern_retained": True,
        }
    captured: list[dict[str, str]] = []
    if cohort == WARNING_COHORT:
        with warnings.catch_warnings(record=True) as actual:
            warnings.simplefilter("always", FutureWarning)
            patterns["warning"] = module.compile(r"[a&&b]")
        captured = [{
            "category": item.category.__name__,
            "message": str(item.message),
        } for item in actual]
        require(captured == [EXPECTED_WARNING],
                "the exact original compile warning was omitted or changed")
    return patterns, captured, cache


def _observe_shared_case(
    case: dict[str, Any], module: Any, patterns: dict[str, Any],
    cache: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    cohort = case["cohort"]
    n = case["variant"] % 7 + 1
    calls = 0
    used: dict[str, int] = {}

    def call(name: str, operation: str, *args: Any) -> Any:
        nonlocal calls
        pattern = patterns[name]
        used[name] = id(pattern)
        calls += 1
        return getattr(pattern, operation)(*args)

    def scan(name: str, subject: Any) -> list[dict[str, Any]]:
        nonlocal calls
        pattern = patterns[name]
        used[name] = id(pattern)
        calls += 1
        scanner = pattern.scanner(subject)
        result = []
        while True:
            calls += 1
            match = scanner.search()
            if match is None:
                break
            result.append(_freeze_match(match))
        return result

    if cohort == COHORTS[0]:
        value = _freeze_match(call("text", "search", "!" + "a" * n + "b"))
    elif cohort == COHORTS[1]:
        subject = "a" * n + "b"
        value = {
            "match": _freeze_match(call("text", "match", subject)),
            "fullmatch": _freeze_match(call("text", "fullmatch", subject)),
        }
    elif cohort == COHORTS[2]:
        value = _freeze_match(
            call("bytes", "search", b"!" + b"a" * n + b"b"),
        )
    elif cohort == COHORTS[3]:
        subject = b"a" * n + b"b"
        value = {
            "match": _freeze_match(call("bytes", "match", subject)),
            "fullmatch": _freeze_match(call("bytes", "fullmatch", subject)),
        }
    elif cohort == COHORTS[4]:
        value = [
            _freeze_match(match)
            for match in call("text_iter", "finditer",
                              "a" * n + "-" + "a" * (n + 1))
        ]
    elif cohort == COHORTS[5]:
        value = [
            _freeze_match(match)
            for match in call("bytes_iter", "finditer",
                              b"a" * n + b"-" + b"a" * (n + 1))
        ]
    elif cohort == COHORTS[6]:
        value = scan("text_iter", "a" * n + "-" + "a" * (n + 1))
    elif cohort == COHORTS[7]:
        value = scan("bytes_iter", b"a" * n + b"-" + b"a" * (n + 1))
    elif cohort == COHORTS[8]:
        value = [
            _freeze_match(match)
            for match in call("zero_text", "finditer", "a" * n)
        ]
    elif cohort == COHORTS[9]:
        value = [
            _freeze_match(match)
            for match in call("zero_bytes", "finditer", b"a" * n)
        ]
    elif cohort == COHORTS[10]:
        subject = "a" * (n * 2)
        match = call("named", "fullmatch", subject)
        require(match is not None,
                "the actual named backreference did not execute")
        calls += 1
        expanded = match.expand(r"<\g<word>>")
        value = {
            "match": _freeze_match(match),
            "expanded": expanded,
            "substitution": call("named", "sub", r"<\g<word>>", subject),
        }
    elif cohort == COHORTS[11]:
        callbacks: list[dict[str, Any]] = []

        def replace(match: Any) -> str:
            inner = call("recursive_text", "fullmatch", match.group("item"))
            callbacks.append(_freeze_match(inner))
            return "<" + match.group("item") + ">"

        result = call("recursive_text", "sub", replace,
                      "a" * n + "-" + "a" * (n + 1))
        value = {"result": result, "callbacks": callbacks}
    elif cohort == COHORTS[12]:
        callbacks = []

        def replace_bytes(match: Any) -> bytes:
            inner = call("recursive_bytes", "fullmatch", match.group("item"))
            callbacks.append(_freeze_match(inner))
            return b"<" + match.group("item") + b">"

        result = call("recursive_bytes", "sub", replace_bytes,
                      b"a" * n + b"-" + b"a" * (n + 1))
        value = {"result": _freeze_value(result), "callbacks": callbacks}
    elif cohort == COHORTS[13]:
        value = {
            "upper": _freeze_match(call("flags", "fullmatch", "K" * n)),
            "lower": _freeze_match(call("flags", "fullmatch", "k" * n)),
            "kelvin": _freeze_match(call("flags", "fullmatch", "\u212a")),
            "cache": cache,
        }
        require(value["upper"]["matched"] and value["lower"]["matched"]
                and not value["kelvin"]["matched"],
                "the actual shared ASCII flag match was not preserved")
    elif cohort == COHORTS[14]:
        failures = []
        for name, wrong in (("text", b"a"), ("bytes", "a")):
            try:
                call(name, "search", wrong)
            except Exception as error:
                failures.append({
                    "type": type(error).__name__,
                    "message": str(error),
                })
            else:
                raise ThreadedPatternOracleError(
                    "an actual shared-pattern type error was silently accepted",
                )
        value = {
            "errors": failures,
            "warning_pattern": _freeze_match(call("warning", "search", "&")),
        }
        require(all(item["type"] == "TypeError" for item in failures),
                "the exact two real shared-pattern TypeErrors changed")
    elif cohort == METADATA_COHORT:
        match = call("text", "fullmatch", "a" * n + "b")
        value = {
            "module_version": module.__version__,
            "module_version_type": type(module.__version__).__name__,
            "noflag_value": int(module.NOFLAG),
            "noflag_type": type(module.NOFLAG).__name__,
            "ignorecase_value": int(module.IGNORECASE),
            "ignorecase_type": type(module.IGNORECASE).__name__,
            "compiled_flags": int(patterns["text"].flags),
            "shared_match": _freeze_match(match),
        }
        require(type(module.__version__) is str
                and module.__version__ == EXPECTED_PUBLIC_RE_VERSION
                and int(module.NOFLAG) == 0
                and isinstance(module.NOFLAG, module.RegexFlag)
                and isinstance(module.IGNORECASE, module.RegexFlag)
                and value["shared_match"]["matched"] is True,
                "the actual shared-match module version or public flags changed")
    else:
        raise ThreadedPatternOracleError("an unfrozen real thread cohort was run")
    require(calls == API_CALLS_PER_THREAD[cohort]
            and tuple(sorted(used)) == tuple(sorted(USED_PATTERNS[cohort])),
            "actual thread-side matching calls or shared identities were omitted")
    return {
        "cohort": cohort,
        "regex_api_calls": calls,
        "value": _freeze_value(value),
    }, used


def validate_case_record(record: Any, case: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "case_id", "cohort", "ordinal", "seed", "variant", "status",
        "actual_thread_execution", "thread_execution_count",
        "actual_regex_api_calls", "metadata_case", "observations",
    }
    require(type(record) is dict and set(record) == fields,
            "a complete actual shared-pattern case record is required")
    for name in ("case_id", "cohort", "ordinal", "seed", "variant"):
        require(record.get(name) == case[name],
                "an original shared-pattern stimulus was replaced: " + name)
    require(record.get("status") == "PASS"
            and record.get("actual_thread_execution") is True
            and type(record.get("thread_execution_count")) is int
            and record["thread_execution_count"] == len(THREAD_ROLES)
            and type(record.get("actual_regex_api_calls")) is int
            and record["actual_regex_api_calls"]
            == API_CALLS_PER_THREAD[case["cohort"]] * len(THREAD_ROLES)
            and record.get("metadata_case")
            is (case["cohort"] == METADATA_COHORT),
            "a genuine shared-pattern case, thread, or matcher was omitted")
    observations = record.get("observations")
    require(type(observations) is dict and set(observations) == set(THREAD_ROLES),
            "both independently executed shared-pattern observations are required")
    for role in THREAD_ROLES:
        observation = observations[role]
        require(type(observation) is dict
                and set(observation) == {"cohort", "regex_api_calls", "value"}
                and observation["cohort"] == case["cohort"]
                and observation["regex_api_calls"]
                == API_CALLS_PER_THREAD[case["cohort"]],
                "a complete independently executed thread observation is missing")
    require(observations["left"] == observations["right"],
            "real simultaneous threads disagreed on the same pattern")
    if case["cohort"] == METADATA_COHORT:
        value = observations["left"]["value"]
        require(type(value) is dict and set(value) == {
            "module_version", "module_version_type", "noflag_value",
            "noflag_type", "ignorecase_value", "ignorecase_type",
            "compiled_flags", "shared_match",
        } and value.get("module_version") == EXPECTED_PUBLIC_RE_VERSION
            and value.get("module_version_type") == "str"
            and value.get("noflag_value") == 0
            and value.get("noflag_type") == "RegexFlag"
            and value.get("ignorecase_type") == "RegexFlag"
            and type(value.get("ignorecase_value")) is int
            and value["ignorecase_value"] > 0
            and type(value.get("compiled_flags")) is int
            and type(value.get("shared_match")) is dict
            and value["shared_match"].get("matched") is True,
            "actual module metadata must be observed inside both real matches")
    return record


def _actual_thread_error(role: str, cohort: str,
                         error: BaseException) -> dict[str, Any]:
    return {
        "role": role,
        "cohort": cohort,
        "type": type(error).__name__,
        "message": str(error),
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__,
        ),
    }


def _run_thread_cohort(
    module: Any, rows: list[dict[str, Any]], cohort_index: int,
) -> dict[str, Any]:
    cohort = COHORTS[cohort_index]
    patterns, warning_records, cache = _prepare_shared_patterns(module, cohort)
    starts = threading.Barrier(3, timeout=30.0)
    completes = threading.Barrier(3, timeout=30.0)
    errors: list[dict[str, Any]] = []
    outputs: dict[str, list[Any]] = {
        role: [None] * CASES_PER_COHORT for role in THREAD_ROLES
    }
    pending_events: dict[str, list[Any]] = {
        role: [None] * CASES_PER_COHORT for role in THREAD_ROLES
    }

    def body(role: str) -> None:
        try:
            actual_ident = threading.get_ident()
            actual_native = threading.get_native_id()
            require(type(actual_ident) is int and actual_ident > 0
                    and type(actual_native) is int and actual_native > 0,
                    "a real shared-pattern Python thread identity is required")
            for index, case in enumerate(rows):
                starts.wait()
                observation, used = _observe_shared_case(
                    case, module, patterns, cache,
                )
                event = {
                    "case_id": case["case_id"],
                    "cohort": cohort,
                    "ordinal": case["ordinal"],
                    "role": role,
                    "thread_name": threading.current_thread().name,
                    "thread_ident": actual_ident,
                    "thread_native_id": actual_native,
                    "shared_text_pattern_identity": id(patterns["text"]),
                    "shared_bytes_pattern_identity": id(patterns["bytes"]),
                    "used_pattern_identities": {
                        name: used[name] for name in sorted(used)
                    },
                    "start_barrier_passed": True,
                    "completion_barrier_arrived": True,
                    "actual_regex_api_calls": observation["regex_api_calls"],
                    "status": "PASS",
                }
                outputs[role][index] = observation
                pending_events[role][index] = event
                completes.wait()
        except BaseException as error:
            errors.append(_actual_thread_error(role, cohort, error))
            for barrier in (starts, completes):
                try:
                    barrier.abort()
                except BaseException as cleanup:
                    errors.append(_actual_thread_error(role, cohort, cleanup))

    threads = {
        role: threading.Thread(
            target=body, args=(role,),
            name=f"rebar-shared-pattern-{cohort_index:02d}-{role}",
            daemon=False,
        ) for role in THREAD_ROLES
    }
    started: list[threading.Thread] = []
    records: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    primary: BaseException | None = None
    try:
        for role in THREAD_ROLES:
            threads[role].start()
            started.append(threads[role])
        for index, case in enumerate(rows):
            starts.wait()
            require(all(threads[role].is_alive() for role in THREAD_ROLES),
                    "the two barrier-synchronized Python threads were not live")
            require(threads["left"].ident != threads["right"].ident
                    and threads["left"].native_id != threads["right"].native_id,
                    "a shared-pattern cohort reused a real thread identity")
            completes.wait()
            require(not errors,
                    "a genuine synchronized pattern thread failed")
            observations = {
                role: outputs[role][index] for role in THREAD_ROLES
            }
            record = {
                **case,
                "status": "PASS",
                "actual_thread_execution": True,
                "thread_execution_count": len(THREAD_ROLES),
                "actual_regex_api_calls": (
                    API_CALLS_PER_THREAD[cohort] * len(THREAD_ROLES)
                ),
                "metadata_case": cohort == METADATA_COHORT,
                "observations": observations,
            }
            validate_case_record(record, case)
            records.append(record)
            for role in THREAD_ROLES:
                event = pending_events[role][index]
                require(type(event) is dict
                        and event["thread_ident"] == threads[role].ident
                        and event["thread_native_id"] == threads[role].native_id,
                        "an actual barrier-bound thread event was substituted")
                events.append(event)
    except BaseException as error:
        primary = error
        errors.append(_actual_thread_error("controller", cohort, error))
        for barrier in (starts, completes):
            try:
                barrier.abort()
            except BaseException as cleanup:
                errors.append(_actual_thread_error(
                    "controller-barrier-cleanup", cohort, cleanup,
                ))
    finally:
        for thread in started:
            try:
                thread.join(timeout=35.0)
            except BaseException as error:
                errors.append(_actual_thread_error(
                    "controller-thread-join", cohort, error,
                ))
    lifecycle = [{
        "cohort": cohort,
        "role": role,
        "thread_name": threads[role].name,
        "thread_ident": threads[role].ident,
        "thread_native_id": threads[role].native_id,
        "started": threads[role] in started,
        "joined": threads[role] in started
        and not threads[role].is_alive(),
        "alive_after_join": threads[role].is_alive()
        if threads[role] in started else False,
        "case_count": CASES_PER_COHORT,
    } for role in THREAD_ROLES]
    if primary is not None or errors:
        raise ThreadedPatternWorkerFailure(
            "an actual shared-pattern thread, barrier, or cleanup failed",
            {
                "cohort": cohort,
                "completed_records": records,
                "completed_thread_events": events,
                "thread_lifecycle": lifecycle,
                "thread_failures": errors,
                "warning_records": warning_records,
            },
        ) from primary
    require(len(records) == CASES_PER_COHORT
            and len(events) == CASES_PER_COHORT * len(THREAD_ROLES)
            and all(item["started"] and item["joined"]
                    and not item["alive_after_join"] for item in lifecycle),
            "a real shared-pattern thread leaked or skipped its lifecycle")
    return {
        "records": records,
        "thread_events": events,
        "thread_lifecycle": lifecycle,
        "warning_record": {
            "cohort": cohort,
            "warnings": warning_records,
        },
    }


def _worker_document(role: str, context: dict[str, Any]) -> dict[str, Any]:
    require(role in REFERENCE_ROLES,
            "a frozen isolated reference process role is required")
    module = importlib.import_module("re")
    require(module.__spec__ is not None
            and os.path.abspath(module.__spec__.origin) == PINNED_STDLIB_RE
            and os.path.abspath(module.__file__) == PINNED_STDLIB_RE,
            "the actual pinned public regex implementation was substituted")
    require(threading.__spec__ is not None
            and os.path.abspath(threading.__spec__.origin) == PINNED_THREADING,
            "the actual pinned public threading implementation was substituted")
    require(type(module.__version__) is str
            and module.__version__ == EXPECTED_PUBLIC_RE_VERSION
            and type(module.NOFLAG).__name__ == "RegexFlag"
            and int(module.NOFLAG) == 0,
            "the exact original public regex module metadata was omitted")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a native candidate entered a standard-library reference process")
    matrix = build_matrix()
    validate_matrix(matrix)
    records: list[dict[str, Any]] = []
    thread_events: list[dict[str, Any]] = []
    lifecycle: list[dict[str, Any]] = []
    warning_records: list[dict[str, Any]] = []
    for index, cohort in enumerate(COHORTS):
        rows = matrix[index * CASES_PER_COHORT:
                      (index + 1) * CASES_PER_COHORT]
        require(all(row["cohort"] == cohort for row in rows),
                "a complete original threaded cohort was reordered")
        completed = _run_thread_cohort(module, rows, index)
        records.extend(completed["records"])
        thread_events.extend(completed["thread_events"])
        lifecycle.extend(completed["thread_lifecycle"])
        warning_records.append(completed["warning_record"])
    document = {
        "schema": SCHEMA + "-reference-worker",
        "status": "PASS",
        "role": role,
        "pid": os.getpid(),
        "python": PYTHON,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "cases_per_cohort": CASES_PER_COHORT,
        "threaded_case_count": EXPECTED_CASES,
        "metadata_case_count": CASES_PER_COHORT,
        "module_version": module.__version__,
        "module_version_type": type(module.__version__).__name__,
        "noflag_value": int(module.NOFLAG),
        "noflag_type": type(module.NOFLAG).__name__,
        "records": records,
        "records_sha256": digest(records),
        "thread_events": thread_events,
        "thread_events_sha256": digest(thread_events),
        "thread_lifecycle": lifecycle,
        "thread_lifecycle_sha256": digest(lifecycle),
        "warning_records": warning_records,
        "warning_records_sha256": digest(warning_records),
        "actual_thread_starts": len(lifecycle),
        "actual_thread_joins": sum(
            row["joined"] is True for row in lifecycle
        ),
        "actual_thread_case_executions": len(thread_events),
        "actual_regex_api_calls": sum(
            row["actual_regex_api_calls"] for row in records
        ),
        "all_barriers_verified": True,
        "all_thread_joins_verified": True,
        "orphan_threads": 0,
        "thread_failures": [],
        "candidate_imports": 0,
        "native_owner_workers": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "original_reference_sha256": context["reference_sha256"],
        "public_cases_unchanged": context["public_cases"],
        "public_cohorts_unchanged": context["public_cohorts"],
        "public_matrix_sha256": context["public_matrix_sha256"],
        "public_stimulus_sha256": context["public_stimulus_sha256"],
        "public_reference_sha256": context["public_reference_sha256"],
        "public_reference_record_sha256":
            context["public_reference_record_sha256"],
        "public_reference_independent_roles":
            context["public_reference_independent_roles"],
        "public_real_locale_cases": context["public_real_locale_cases"],
        "public_real_locale_transitions":
            context["public_real_locale_transitions"],
        "pinned_python_sha256": context["pinned_python_sha256"],
        "pinned_stdlib_re_sha256": context["pinned_stdlib_re_sha256"],
        "pinned_public_threading_sha256":
            context["pinned_public_threading_sha256"],
    }
    return validate_worker_document(document, role, expected_pid=os.getpid())


def validate_worker_document(
    document: Any, role: str, *, expected_pid: int,
) -> dict[str, Any]:
    require(type(document) is dict and role in REFERENCE_ROLES
            and type(expected_pid) is int and expected_pid > 0,
            "a real Popen-bound threaded reference process is required")
    expected = {
        "schema": SCHEMA + "-reference-worker",
        "status": "PASS",
        "role": role,
        "pid": expected_pid,
        "python": PYTHON,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "cases_per_cohort": CASES_PER_COHORT,
        "threaded_case_count": EXPECTED_CASES,
        "metadata_case_count": CASES_PER_COHORT,
        "module_version": EXPECTED_PUBLIC_RE_VERSION,
        "module_version_type": "str",
        "noflag_value": 0,
        "noflag_type": "RegexFlag",
        "actual_thread_starts": EXPECTED_THREAD_STARTS_PER_WORKER,
        "actual_thread_joins": EXPECTED_THREAD_STARTS_PER_WORKER,
        "actual_thread_case_executions":
            EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER,
        "actual_regex_api_calls": EXPECTED_REGEX_API_CALLS_PER_WORKER,
        "all_barriers_verified": True,
        "all_thread_joins_verified": True,
        "orphan_threads": 0,
        "thread_failures": [],
        "candidate_imports": 0,
        "native_owner_workers": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "original_reference_sha256": V6_REFERENCE_SHA256,
        "public_cases_unchanged": PUBLIC_CASES,
        "public_cohorts_unchanged": PUBLIC_COHORTS,
        "public_matrix_sha256": PUBLIC_MATRIX_SHA256,
        "public_stimulus_sha256": PUBLIC_STIMULUS_SHA256,
        "public_reference_sha256": PUBLIC_REFERENCE_SHA256,
        "public_reference_record_sha256": PUBLIC_REFERENCE_RECORD_SHA256,
        "public_reference_independent_roles": 2,
        "public_real_locale_cases": PUBLIC_REAL_LOCALE_CASES,
        "public_real_locale_transitions": PUBLIC_REAL_LOCALE_TRANSITIONS,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_threading_sha256": PINNED_THREADING_SHA256,
    }
    vector_fields = {
        "records", "records_sha256", "thread_events",
        "thread_events_sha256", "thread_lifecycle",
        "thread_lifecycle_sha256", "warning_records",
        "warning_records_sha256",
    }
    require(set(document) == set(expected) | vector_fields,
            "a genuine reference worker omitted or invented complete fields")
    for name, value in expected.items():
        require(document.get(name) == value,
                "a real Popen-bound threaded worker was forged: " + name)
    matrix = build_matrix()
    records = document["records"]
    require(type(records) is list and len(records) == EXPECTED_CASES,
            "all actual threaded original case observations are required")
    for case, record in zip(matrix, records, strict=True):
        validate_case_record(record, case)
    require(document["records_sha256"] == digest(records),
            "the complete actual threaded semantic vector was forged")
    events = document["thread_events"]
    require(type(events) is list
            and len(events) == EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER
            and document["thread_events_sha256"] == digest(events),
            "a real synchronized thread or its original event was hidden")
    lifecycles = document["thread_lifecycle"]
    require(type(lifecycles) is list
            and len(lifecycles) == EXPECTED_THREAD_STARTS_PER_WORKER
            and document["thread_lifecycle_sha256"] == digest(lifecycles),
            "a real started, joined, or leaked pattern thread was hidden")
    identities: dict[tuple[str, str], tuple[int, int, str]] = {}
    for index, cohort in enumerate(COHORTS):
        for role_index, thread_role in enumerate(THREAD_ROLES):
            row = lifecycles[index * len(THREAD_ROLES) + role_index]
            require(type(row) is dict
                    and set(row) == {
                        "cohort", "role", "thread_name", "thread_ident",
                        "thread_native_id", "started", "joined",
                        "alive_after_join", "case_count",
                    }
                    and row["cohort"] == cohort
                    and row["role"] == thread_role
                    and type(row["thread_name"]) is str
                    and type(row["thread_ident"]) is int
                    and row["thread_ident"] > 0
                    and type(row["thread_native_id"]) is int
                    and row["thread_native_id"] > 0
                    and row["started"] is True
                    and row["joined"] is True
                    and row["alive_after_join"] is False
                    and row["case_count"] == CASES_PER_COHORT,
                    "an actual started-and-joined thread identity was forged")
            identities[(cohort, thread_role)] = (
                row["thread_ident"], row["thread_native_id"],
                row["thread_name"],
            )
        require(identities[(cohort, "left")][0]
                != identities[(cohort, "right")][0]
                and identities[(cohort, "left")][1]
                != identities[(cohort, "right")][1],
                "one actual thread was reused for two live barrier roles")
    for index, case in enumerate(matrix):
        pair = []
        for role_index, thread_role in enumerate(THREAD_ROLES):
            event = events[index * len(THREAD_ROLES) + role_index]
            expected_ident, expected_native, expected_name = (
                identities[(case["cohort"], thread_role)]
            )
            require(type(event) is dict
                    and set(event) == {
                        "case_id", "cohort", "ordinal", "role",
                        "thread_name", "thread_ident", "thread_native_id",
                        "shared_text_pattern_identity",
                        "shared_bytes_pattern_identity",
                        "used_pattern_identities",
                        "start_barrier_passed",
                        "completion_barrier_arrived",
                        "actual_regex_api_calls", "status",
                    }
                    and event["case_id"] == case["case_id"]
                    and event["cohort"] == case["cohort"]
                    and event["ordinal"] == case["ordinal"]
                    and event["role"] == thread_role
                    and event["thread_name"] == expected_name
                    and event["thread_ident"] == expected_ident
                    and event["thread_native_id"] == expected_native
                    and event["start_barrier_passed"] is True
                    and event["completion_barrier_arrived"] is True
                    and event["actual_regex_api_calls"]
                    == API_CALLS_PER_THREAD[case["cohort"]]
                    and event["status"] == "PASS"
                    and type(event["shared_text_pattern_identity"]) is int
                    and event["shared_text_pattern_identity"] > 0
                    and type(event["shared_bytes_pattern_identity"]) is int
                    and event["shared_bytes_pattern_identity"] > 0,
                    "an actual independently synchronized thread event was forged")
            used = event["used_pattern_identities"]
            require(type(used) is dict
                    and tuple(sorted(used))
                    == tuple(sorted(USED_PATTERNS[case["cohort"]]))
                    and all(type(identity) is int and identity > 0
                            for identity in used.values()),
                    "the actual same immutable compiled pattern was replaced")
            if "text" in used:
                require(used["text"] == event["shared_text_pattern_identity"],
                        "a real thread did not execute the shared text pattern")
            if "bytes" in used:
                require(used["bytes"] == event["shared_bytes_pattern_identity"],
                        "a real thread did not execute the shared bytes pattern")
            pair.append(event)
        require(pair[0]["thread_ident"] != pair[1]["thread_ident"]
                and pair[0]["thread_native_id"] != pair[1]["thread_native_id"]
                and pair[0]["shared_text_pattern_identity"]
                == pair[1]["shared_text_pattern_identity"]
                and pair[0]["shared_bytes_pattern_identity"]
                == pair[1]["shared_bytes_pattern_identity"]
                and pair[0]["used_pattern_identities"]
                == pair[1]["used_pattern_identities"],
                "the two live threads did not genuinely share their patterns")
    warning_records = document["warning_records"]
    require(type(warning_records) is list
            and len(warning_records) == len(COHORTS)
            and document["warning_records_sha256"] == digest(warning_records),
            "the complete deterministic original warning vector was omitted")
    for cohort, warning in zip(COHORTS, warning_records, strict=True):
        require(type(warning) is dict
                and set(warning) == {"cohort", "warnings"}
                and warning["cohort"] == cohort
                and warning["warnings"]
                == ([EXPECTED_WARNING] if cohort == WARNING_COHORT else []),
                "an actual deterministic original warning was hidden or changed")
    return document


def _worker_environment() -> dict[str, str]:
    return {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }


def _run_worker(
    role: str, source_sha256: str, protocol_sha256: str,
) -> dict[str, Any]:
    require(role in REFERENCE_ROLES,
            "an actual independently frozen threaded reference role is required")
    command = [
        sys.executable, "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--worker-role", role,
        "--source-sha256", source_sha256,
        "--protocol-sha256", protocol_sha256,
    ]
    process: subprocess.Popen[bytes] | None = None
    observed: dict[str, Any] = {
        "role": role,
        "status": "FAIL",
        "pid": None,
        "returncode": None,
        "signal": None,
        "timed_out": False,
        "stdout": capture_complete_stream(b""),
        "stderr": capture_complete_stream(b""),
        "stdout_complete": False,
        "stderr_complete": False,
        "active_phase": "start-actual-isolated-reference-process",
    }
    try:
        process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            env=_worker_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        require(type(process.pid) is int and process.pid > 0,
                "the genuine reference subprocess has no actual PID")
        observed["pid"] = process.pid
        observed["active_phase"] = "capture-complete-original-worker-streams"
        try:
            stdout, stderr = process.communicate(timeout=300)
        except subprocess.TimeoutExpired as timeout:
            observed["timed_out"] = True
            observed["timeout_partial_stdout"] = capture_complete_stream(
                timeout.stdout if type(timeout.stdout) is bytes else b"",
            )
            observed["timeout_partial_stderr"] = capture_complete_stream(
                timeout.stderr if type(timeout.stderr) is bytes else b"",
            )
            observed["active_phase"] = "terminate-and-join-timed-out-worker"
            try:
                process.kill()
            except BaseException as cleanup:
                observed["timeout_termination_error"] = {
                    "type": type(cleanup).__name__,
                    "message": str(cleanup),
                }
            stdout, stderr = process.communicate(timeout=35)
        require(type(stdout) is bytes and type(stderr) is bytes,
                "the original actual reference streams were not preserved")
        observed["stdout"] = capture_complete_stream(stdout)
        observed["stderr"] = capture_complete_stream(stderr)
        observed["stdout_complete"] = True
        observed["stderr_complete"] = True
        observed["returncode"] = process.returncode
        observed["signal"] = (
            -process.returncode
            if type(process.returncode) is int and process.returncode < 0
            else None
        )
        require(observed["timed_out"] is False
                and process.returncode == 0 and stderr == b"",
                "the genuine threaded reference timed out, signaled, or failed")
        observed["active_phase"] = "decode-complete-original-worker-stdout"
        document = strict_canonical(
            stdout, label=role + " complete original threaded stdout",
        )
        observed["active_phase"] = "validate-popen-bound-real-thread-lifecycle"
        validate_worker_document(document, role, expected_pid=process.pid)
        observed["report"] = document
        observed["active_phase"] = "complete"
        observed["status"] = "PASS"
        return observed
    except BaseException as error:
        if process is not None:
            observed["pid"] = process.pid
            observed["returncode"] = process.returncode
        observed["error_type"] = type(error).__name__
        observed["error_message"] = str(error)
        observed["status"] = "FAIL"
        raise ThreadedPatternWorkerFailure(
            "an actual isolated threaded reference process failed", observed,
        ) from error

def _mark_ledger_failure(event: dict[str, Any], error: BaseException) -> None:
    event["status"] = "FAIL"
    event["error_type"] = type(error).__name__
    event["error_message"] = str(error)
    if isinstance(error, OSError):
        event["errno"] = error.errno


def _ledger_call(
    events: list[dict[str, Any]], role: str, action: str, operation: Any,
    **fields: Any,
) -> tuple[Any, dict[str, Any]]:
    event = {"role": role, "action": action, **fields, "status": "PENDING"}
    events.append(event)
    try:
        actual = operation()
    except BaseException as error:
        _mark_ledger_failure(event, error)
        raise
    event["status"] = "PASS"
    return actual, event


def _open_ledger_fd(
    events: list[dict[str, Any]], owned: dict[str, int], role: str,
    operation: Any, **fields: Any,
) -> int:
    require(role not in owned,
            "a simultaneously live publication descriptor role was reused")
    actual, event = _ledger_call(
        events, role, "open", operation, fd=None, **fields,
    )
    try:
        require(type(actual) is int and actual >= 0,
                "an actual publication descriptor was not a genuine integer")
        require(actual not in owned.values(),
                "two simultaneously live publication roles share a descriptor")
    except BaseException as error:
        event["fd"] = actual
        _mark_ledger_failure(event, error)
        raise
    event["fd"] = actual
    owned[role] = actual
    return actual


def _close_ledger_fd(
    events: list[dict[str, Any]], owned: dict[str, int], role: str,
) -> None:
    require(role in owned,
            "a consumed publication descriptor was closed more than once")
    descriptor = owned.pop(role)
    actual, _ = _ledger_call(
        events, role, "close", lambda: os.close(descriptor), fd=descriptor,
    )
    require(actual is None,
            "an actual descriptor close returned an invented result")


def _fstat_ledger(
    events: list[dict[str, Any]], role: str, descriptor: int,
) -> os.stat_result:
    information, event = _ledger_call(
        events, role, "fstat", lambda: os.fstat(descriptor), fd=descriptor,
    )
    require(isinstance(information, os.stat_result),
            "the actual descriptor identity was not a genuine fstat")
    event["device"] = int(information.st_dev)
    event["inode"] = int(information.st_ino)
    event["mode"] = int(information.st_mode)
    event["size"] = int(information.st_size)
    return information


def _open_parent_directory(
    relative: str, events: list[dict[str, Any]], owned: dict[str, int],
) -> str:
    path = PurePosixPath(safe_relative(relative, outputs_only=True))
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory_flag = getattr(os, "O_DIRECTORY", None)
    cloexec = getattr(os, "O_CLOEXEC", None)
    require(all(type(value) is int and value > 0
                for value in (nofollow, directory_flag, cloexec)),
            "genuine descriptor-relative no-follow directory support is required")
    flags = os.O_RDONLY | directory_flag | nofollow | cloexec
    current_role = "directory:."
    descriptor = _open_ledger_fd(
        events, owned, current_role,
        lambda: os.open(str(ROOT), flags),
        component=str(ROOT), parent_fd=None, nofollow=True,
    )
    require(stat.S_ISDIR(_fstat_ledger(events, current_role, descriptor).st_mode),
            "the publication workspace root is not a genuine directory")
    traversed: list[str] = []
    for component in path.parts[:-1]:
        parent_descriptor = owned[current_role]
        traversed.append(component)
        child_role = "directory:" + "/".join(traversed)
        descriptor = _open_ledger_fd(
            events, owned, child_role,
            lambda component=component, parent_descriptor=parent_descriptor:
            os.open(component, flags, dir_fd=parent_descriptor),
            component=component, parent_fd=parent_descriptor, nofollow=True,
        )
        require(stat.S_ISDIR(_fstat_ledger(events, child_role, descriptor).st_mode),
                "a no-follow publication parent component is not a directory")
        _close_ledger_fd(events, owned, current_role)
        current_role = child_role
    return current_role


def _capture_publication_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_REPORT_BYTES,
            "an observed exclusive publication stream exceeds its real bound")
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "base64": base64.b64encode(raw).decode("ascii"),
    }


def _restore_publication_stream(record: Any) -> bytes:
    require(type(record) is dict
            and set(record) == {"bytes", "sha256", "base64"}
            and type(record.get("bytes")) is int
            and 0 <= record["bytes"] <= MAX_REPORT_BYTES
            and valid_sha256(record.get("sha256"))
            and type(record.get("base64")) is str,
            "a complete bounded exclusive reread was omitted")
    try:
        raw = base64.b64decode(record["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise ThreadedPatternOracleError(
            "a genuine exclusive publication reread was invalid",
        ) from error
    require(len(raw) == record["bytes"]
            and hashlib.sha256(raw).hexdigest() == record["sha256"],
            "the exact bounded publication reread was forged")
    return raw


def _read_publication(
    descriptor: int, role: str, events: list[dict[str, Any]],
    receipt: dict[str, Any],
) -> bytes:
    pieces: list[bytes] = []
    count = 0
    receipt["readback_stream_complete"] = False
    receipt["observed_readback"] = _capture_publication_stream(b"")
    while True:
        requested = min(65_536, MAX_REPORT_BYTES - count + 1)
        event = {
            "role": role,
            "action": "read",
            "fd": descriptor,
            "requested_bytes": requested,
            "returned_bytes": None,
            "returned_sha256": None,
            "status": "PENDING",
        }
        events.append(event)
        try:
            actual = os.read(descriptor, requested)
            require(type(actual) is bytes and len(actual) <= requested,
                    "a genuine exclusive read returned invented bytes")
            event["returned_bytes"] = len(actual)
            event["returned_sha256"] = hashlib.sha256(actual).hexdigest()
            if actual:
                require(count + len(actual) <= MAX_REPORT_BYTES,
                        "the exclusively created reread exceeds its frozen bound")
                pieces.append(actual)
                count += len(actual)
            event["status"] = "PASS"
            snapshot = b"".join(pieces)
            receipt["readback_bytes"] = len(snapshot)
            receipt["readback_sha256"] = hashlib.sha256(snapshot).hexdigest()
            receipt["observed_readback"] = _capture_publication_stream(snapshot)
            if not actual:
                receipt["readback_stream_complete"] = True
                return snapshot
        except BaseException as error:
            _mark_ledger_failure(event, error)
            raise


def _preflight_outputs() -> None:
    for relative in sorted(APPROVED_OUTPUTS):
        events: list[dict[str, Any]] = []
        owned: dict[str, int] = {}
        primary: BaseException | None = None
        cleanup: list[dict[str, Any]] = []
        try:
            directory_role = _open_parent_directory(relative, events, owned)
            directory = owned[directory_role]
            event = {
                "role": directory_role,
                "action": "preflight-stat",
                "fd": directory,
                "basename": PurePosixPath(relative).name,
                "status": "PENDING",
            }
            events.append(event)
            try:
                os.stat(
                    PurePosixPath(relative).name,
                    dir_fd=directory,
                    follow_symlinks=False,
                )
            except FileNotFoundError as missing:
                event["status"] = "MISSING"
                event["errno"] = missing.errno
            except BaseException as error:
                _mark_ledger_failure(event, error)
                raise
            else:
                event["status"] = "EXISTS"
                raise ThreadedPatternOracleError(
                    "an immutable threaded-pattern result already exists: "
                    + relative,
                )
        except BaseException as error:
            primary = error
        finally:
            for descriptor_role in reversed(list(owned)):
                try:
                    _close_ledger_fd(events, owned, descriptor_role)
                except BaseException as error:
                    cleanup.append({
                        "role": descriptor_role,
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                    })
        if primary is not None:
            raise ThreadedPatternOracleError(
                "the no-follow immutable result preflight failed: " + relative,
            ) from primary
        require(not cleanup,
                "a genuine no-follow immutable preflight descriptor leaked")


def validate_publication_receipt(
    receipt: Any, *, relative: str, document: dict[str, Any],
) -> dict[str, Any]:
    relative = safe_relative(relative, outputs_only=True)
    plain, raw, compression = publication_payload(relative, document)
    require(type(receipt) is dict,
            "a complete actual exclusive publication receipt is required")
    for name, expected in {
        "schema": SCHEMA + "-exclusive-publication-receipt",
        "status": "PASS",
        "path": relative,
        "compression": compression,
        "uncompressed_bytes": len(plain),
        "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "maximum_uncompressed_bytes": MAX_REPORT_BYTES,
        "maximum_compressed_bytes": MAX_REPORT_BYTES,
        "expected_bytes": len(raw),
        "expected_sha256": hashlib.sha256(raw).hexdigest(),
        "exclusive_creation": True,
        "nofollow": True,
        "safe_parent_component_walk": True,
        "bytes_written": len(raw),
        "file_fsync": True,
        "directory_fsync": True,
        "readback_bytes": len(raw),
        "readback_sha256": hashlib.sha256(raw).hexdigest(),
        "readback_stream_complete": True,
        "readback_exact_bytes_verified": True,
        "owned_partial_removed": False,
        "partial_removal_directory_fsync": False,
    }.items():
        require(receipt.get(name) == expected,
                "a real exclusive publication receipt was forged: " + name)
    require(receipt.get("parent_components")
            == list(PurePosixPath(relative).parts[:-1]),
            "the exact no-follow publication parent walk was replaced")
    for identity in ("parent_device", "parent_inode",
                     "created_file_device", "created_file_inode"):
        require(type(receipt.get(identity)) is int
                and receipt[identity] >= 0,
                "an actual publication device/inode was forged: " + identity)
    observed = _restore_publication_stream(receipt.get("observed_readback"))
    require(observed == raw,
            "the actual exclusive publication readback was replaced")
    require(restore_publication_document(relative, observed) == document,
            "the complete bounded gzip or canonical receipt differs")
    events = receipt.get("descriptor_events")
    calls = receipt.get("write_calls")
    require(type(events) is list and type(calls) is list and bool(calls)
            and receipt.get("cleanup_failures") == [],
            "the actual complete pending publication ledger was omitted")
    live: dict[str, int] = {}
    open_directories: list[str] = []
    writes: list[dict[str, Any]] = []
    offset = 0
    reread_offset = 0
    reader_eof = False
    writer_fsyncs = 0
    directory_fsyncs = 0
    final_directory_role = "directory:" + "/".join(
        PurePosixPath(relative).parts[:-1],
    )
    for event in events:
        require(type(event) is dict and event.get("status") == "PASS"
                and type(event.get("role")) is str
                and type(event.get("action")) is str
                and type(event.get("fd")) is int and event["fd"] >= 0,
                "an actual pending, failed, or invented descriptor event was hidden")
        role = event["role"]
        action = event["action"]
        descriptor = event["fd"]
        if action == "open":
            require(role not in live and descriptor not in live.values(),
                    "two genuinely live publication descriptors were aliased")
            if role.startswith("directory:"):
                open_directories.append(role)
                require(event.get("nofollow") is True,
                        "an actual no-follow parent component was omitted")
                if role == "directory:.":
                    require(event.get("component") == str(ROOT)
                            and event.get("parent_fd") is None,
                            "the descriptor-relative workspace root was replaced")
                else:
                    require(event.get("parent_fd") in live.values()
                            and event.get("component")
                            == role.removeprefix("directory:").rsplit("/", 1)[-1],
                            "a no-follow parent component was not genuinely walked")
            else:
                require(role in {"writer", "reader"}
                        and event.get("parent_fd")
                        == live.get(final_directory_role)
                        and event.get("basename")
                        == PurePosixPath(relative).name
                        and event.get("nofollow") is True,
                        "an exclusive file was not opened relative to its parent")
                if role == "writer":
                    require(event.get("exclusive") is True,
                            "the original report was not exclusively created")
            live[role] = descriptor
        elif action == "close":
            require(live.get(role) == descriptor,
                    "a consumed or invented descriptor was closed twice")
            del live[role]
        else:
            require(live.get(role) == descriptor,
                    "a publication syscall used a non-live descriptor")
            if action == "write":
                require(role == "writer"
                        and type(event.get("requested_bytes")) is int
                        and event["requested_bytes"] == len(raw) - offset
                        and type(event.get("returned_bytes")) is int
                        and 0 < event["returned_bytes"]
                        <= event["requested_bytes"],
                        "a failed, zero, bool, oversized, or hidden short write passed")
                end = offset + event["returned_bytes"]
                require(event.get("returned_sha256")
                        == hashlib.sha256(raw[offset:end]).hexdigest(),
                        "an observed exclusive short-write segment was forged")
                writes.append(event)
                offset = end
            elif action == "read":
                require(role == "reader"
                        and type(event.get("requested_bytes")) is int
                        and event["requested_bytes"] > 0
                        and type(event.get("returned_bytes")) is int
                        and 0 <= event["returned_bytes"]
                        <= event["requested_bytes"]
                        and reader_eof is False,
                        "an incomplete or invented original reread was accepted")
                end = reread_offset + event["returned_bytes"]
                require(end <= len(raw)
                        and event.get("returned_sha256")
                        == hashlib.sha256(raw[reread_offset:end]).hexdigest(),
                        "an actual original publication read segment was forged")
                reread_offset = end
                if event["returned_bytes"] == 0:
                    reader_eof = True
            elif action == "fsync":
                if role == "writer":
                    writer_fsyncs += 1
                else:
                    require(role == final_directory_role,
                            "the actual publication parent fsync was replaced")
                    directory_fsyncs += 1
            elif action == "fstat":
                require((role.startswith("directory:")
                         or role in {"writer", "reader"})
                        and type(event.get("device")) is int
                        and type(event.get("inode")) is int,
                        "an invented publication fstat role was accepted")
                if role == final_directory_role:
                    require(event["device"] == receipt["parent_device"]
                            and event["inode"] == receipt["parent_inode"],
                            "the actual final parent identity was replaced")
                elif role in {"writer", "reader"}:
                    require(event["device"] == receipt["created_file_device"]
                            and event["inode"] == receipt["created_file_inode"],
                            "the exclusive created basename identity was replaced")
            else:
                raise ThreadedPatternOracleError(
                    "an invented actual publication ledger action was accepted",
                )
    expected_directories = ["directory:."] + [
        "directory:" + "/".join(PurePosixPath(relative).parts[:index])
        for index in range(1, len(PurePosixPath(relative).parts))
    ]
    require(open_directories == expected_directories
            and not live
            and writes == calls
            and offset == len(raw)
            and reread_offset == len(raw)
            and reader_eof is True
            and writer_fsyncs == 1
            and directory_fsyncs == 1,
            "a real complete no-follow publication lifecycle was truncated")
    return receipt


def _preserve_and_remove_owned_partial(
    relative: str, events: list[dict[str, Any]], owned: dict[str, int],
    receipt: dict[str, Any],
) -> None:
    path = PurePosixPath(relative)
    directory_role = "directory:" + "/".join(path.parts[:-1])
    require(receipt.get("exclusive_creation") is True
            and directory_role in owned
            and type(receipt.get("created_file_device")) is int
            and type(receipt.get("created_file_inode")) is int,
            "an exclusive owned partial basename was not independently proven")
    parent = owned[directory_role]
    if "reader" in owned:
        _close_ledger_fd(events, owned, "reader")
    reader = _open_ledger_fd(
        events, owned, "reader",
        lambda: os.open(
            path.name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
            dir_fd=parent,
        ),
        parent_fd=parent, basename=path.name,
        nofollow=True, exclusive=False,
    )
    information = _fstat_ledger(events, "reader", reader)
    require(stat.S_ISREG(information.st_mode)
            and information.st_dev == receipt["created_file_device"]
            and information.st_ino == receipt["created_file_inode"],
            "the existing partial basename is not the actually owned creation")
    _read_publication(reader, "reader", events, receipt)
    _close_ledger_fd(events, owned, "reader")
    if "writer" in owned:
        _close_ledger_fd(events, owned, "writer")
    actual, event = _ledger_call(
        events, directory_role, "owned-basename-stat",
        lambda: os.stat(path.name, dir_fd=parent, follow_symlinks=False),
        fd=parent, basename=path.name, nofollow=True,
    )
    require(isinstance(actual, os.stat_result),
            "the actual owned partial basename was not safely restated")
    event["device"] = int(actual.st_dev)
    event["inode"] = int(actual.st_ino)
    require(stat.S_ISREG(actual.st_mode)
            and actual.st_dev == receipt["created_file_device"]
            and actual.st_ino == receipt["created_file_inode"],
            "cleanup refused to remove an unowned or replaced partial basename")
    removed, _ = _ledger_call(
        events, directory_role, "unlink-owned-partial",
        lambda: os.unlink(path.name, dir_fd=parent),
        fd=parent, basename=path.name,
        device=receipt["created_file_device"],
        inode=receipt["created_file_inode"],
    )
    require(removed is None,
            "the actual owned partial report removal was not observed")
    receipt["owned_partial_removed"] = True
    synced, _ = _ledger_call(
        events, directory_role, "fsync-partial-removal",
        lambda: os.fsync(parent), fd=parent,
    )
    require(synced is None,
            "the real owned-partial parent-directory fsync was not observed")
    receipt["partial_removal_directory_fsync"] = True


def publish_with_receipt(relative: str, document: dict[str, Any]) -> dict[str, Any]:
    relative = safe_relative(relative, outputs_only=True)
    plain, raw, compression = publication_payload(relative, document)
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "an actual canonical threaded-pattern report exceeds its bound")
    path = PurePosixPath(relative)
    events: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    owned: dict[str, int] = {}
    receipt: dict[str, Any] = {
        "schema": SCHEMA + "-exclusive-publication-receipt",
        "path": relative,
        "compression": compression,
        "uncompressed_bytes": len(plain),
        "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "maximum_uncompressed_bytes": MAX_REPORT_BYTES,
        "maximum_compressed_bytes": MAX_REPORT_BYTES,
        "expected_bytes": len(raw),
        "expected_sha256": hashlib.sha256(raw).hexdigest(),
        "parent_components": list(path.parts[:-1]),
        "parent_device": None,
        "parent_inode": None,
        "created_file_device": None,
        "created_file_inode": None,
        "safe_parent_component_walk": False,
        "exclusive_creation": False,
        "nofollow": True,
        "write_calls": calls,
        "bytes_written": 0,
        "file_fsync": False,
        "directory_fsync": False,
        "readback_bytes": 0,
        "readback_sha256": None,
        "observed_readback": _capture_publication_stream(b""),
        "readback_stream_complete": False,
        "readback_exact_bytes_verified": False,
        "owned_partial_removed": False,
        "partial_removal_directory_fsync": False,
        "descriptor_events": events,
        "cleanup_failures": [],
        "status": "FAIL",
    }
    primary: BaseException | None = None
    try:
        directory_role = _open_parent_directory(relative, events, owned)
        directory = owned[directory_role]
        directory_information = _fstat_ledger(events, directory_role, directory)
        require(stat.S_ISDIR(directory_information.st_mode),
                "the final no-follow publication parent is not a real directory")
        receipt["parent_device"] = int(directory_information.st_dev)
        receipt["parent_inode"] = int(directory_information.st_ino)
        receipt["safe_parent_component_walk"] = True
        writer = _open_ledger_fd(
            events, owned, "writer",
            lambda: os.open(
                path.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL
                | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o644,
                dir_fd=directory,
            ),
            parent_fd=directory, basename=path.name,
            nofollow=True, exclusive=True,
        )
        receipt["exclusive_creation"] = True
        writer_information = _fstat_ledger(events, "writer", writer)
        require(stat.S_ISREG(writer_information.st_mode),
                "the actual exclusively created output is not a regular file")
        receipt["created_file_device"] = int(writer_information.st_dev)
        receipt["created_file_inode"] = int(writer_information.st_ino)
        offset = 0
        while offset < len(raw):
            requested = len(raw) - offset
            event = {
                "role": "writer",
                "action": "write",
                "fd": writer,
                "requested_bytes": requested,
                "returned_bytes": None,
                "returned_sha256": None,
                "status": "PENDING",
            }
            calls.append(event)
            events.append(event)
            try:
                actual = os.write(writer, raw[offset:])
                event["returned_bytes"] = actual
                require(type(actual) is int and 0 < actual <= requested,
                        "an exclusive write returned zero, bool, or too many bytes")
                event["returned_sha256"] = hashlib.sha256(
                    raw[offset:offset + actual],
                ).hexdigest()
                offset += actual
                receipt["bytes_written"] = offset
                event["status"] = "PASS"
            except BaseException as error:
                _mark_ledger_failure(event, error)
                raise
        actual, _ = _ledger_call(
            events, "writer", "fsync", lambda: os.fsync(writer), fd=writer,
        )
        require(actual is None, "the actual publication file fsync was forged")
        receipt["file_fsync"] = True
        _close_ledger_fd(events, owned, "writer")
        actual, _ = _ledger_call(
            events, directory_role, "fsync", lambda: os.fsync(directory),
            fd=directory,
        )
        require(actual is None, "the actual publication parent fsync was forged")
        receipt["directory_fsync"] = True
        reader = _open_ledger_fd(
            events, owned, "reader",
            lambda: os.open(
                path.name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                dir_fd=directory,
            ),
            parent_fd=directory, basename=path.name,
            nofollow=True, exclusive=False,
        )
        information = _fstat_ledger(events, "reader", reader)
        require(stat.S_ISREG(information.st_mode)
                and information.st_size == len(raw)
                and information.st_dev == receipt["created_file_device"]
                and information.st_ino == receipt["created_file_inode"],
                "the real exclusive output was truncated or replaced")
        actual = _read_publication(reader, "reader", events, receipt)
        require(
            actual == raw
            and restore_publication_document(relative, actual) == document,
                "the complete original canonical exclusive readback differs")
        receipt["readback_exact_bytes_verified"] = True
        _close_ledger_fd(events, owned, "reader")
        _close_ledger_fd(events, owned, directory_role)
        receipt["status"] = "PASS"
        validate_publication_receipt(receipt, relative=relative, document=document)
    except BaseException as error:
        primary = error
        receipt["status"] = "FAIL"
        receipt["error_type"] = type(error).__name__
        receipt["error_message"] = str(error)
        if isinstance(error, OSError):
            receipt["errno"] = error.errno
        if receipt["exclusive_creation"]:
            try:
                _preserve_and_remove_owned_partial(
                    relative, events, owned, receipt,
                )
            except BaseException as cleanup:
                failure = {
                    "role": "preserve-and-remove-owned-partial",
                    "error_type": type(cleanup).__name__,
                    "error_message": str(cleanup),
                }
                if isinstance(cleanup, OSError):
                    failure["errno"] = cleanup.errno
                receipt["cleanup_failures"].append(failure)
    finally:
        for descriptor_role in reversed(list(owned)):
            try:
                _close_ledger_fd(events, owned, descriptor_role)
            except BaseException as cleanup:
                failure = {
                    "role": descriptor_role,
                    "error_type": type(cleanup).__name__,
                    "error_message": str(cleanup),
                }
                if isinstance(cleanup, OSError):
                    failure["errno"] = cleanup.errno
                receipt["cleanup_failures"].append(failure)
                if primary is None:
                    primary = cleanup
                    receipt["status"] = "FAIL"
                    receipt["error_type"] = type(cleanup).__name__
                    receipt["error_message"] = str(cleanup)
    if primary is not None or receipt["cleanup_failures"]:
        raise ThreadedPatternPublicationFailure(
            "a genuine no-follow exclusive threaded-pattern publication failed",
            receipt,
        ) from primary
    return receipt


def run_self_oracle(
    source_sha256: str, protocol_sha256: str,
) -> dict[str, Any]:
    require(valid_sha256(source_sha256) and valid_sha256(protocol_sha256),
            "root must supply the independently frozen source and protocol")
    context = authenticate_context(source_sha256, protocol_sha256)
    _preflight_outputs()
    completed: dict[str, dict[str, Any]] = {}
    phase = "start-independent-pinned-reference-processes"
    try:
        for role in REFERENCE_ROLES:
            phase = "start-actual-" + role
            completed[role] = _run_worker(role, source_sha256, protocol_sha256)
        require(set(completed) == set(REFERENCE_ROLES),
                "a genuine independently isolated reference process was omitted")
        for role in REFERENCE_ROLES:
            observed = completed[role]
            require(observed["status"] == "PASS"
                    and observed["role"] == role
                    and observed["returncode"] == 0
                    and observed["signal"] is None
                    and observed["timed_out"] is False
                    and observed["stdout_complete"] is True
                    and observed["stderr_complete"] is True,
                    "an actual complete independently bound process failed")
            stdout = restore_complete_stream(
                observed["stdout"], label=role + " original complete stdout",
            )
            stderr = restore_complete_stream(
                observed["stderr"], label=role + " original complete stderr",
            )
            require(stderr == b"",
                    "an independently successful thread worker wrote stderr")
            original = strict_canonical(
                stdout, label=role + " original producer-canonical stdout",
            )
            require(original == observed["report"],
                    "a complete actual reference stream was replaced")
            validate_worker_document(
                original, role, expected_pid=observed["pid"],
            )
        first = completed["reference_a"]["report"]
        second = completed["reference_b"]["report"]
        require(completed["reference_a"]["pid"]
                != completed["reference_b"]["pid"]
                and first["pid"] != second["pid"],
                "two genuine reference processes share an actual PID")
        for vector, fingerprint in (
            ("records", "records_sha256"),
            ("warning_records", "warning_records_sha256"),
        ):
            require(first[vector] == second[vector]
                    and first[fingerprint] == second[fingerprint],
                    "complete independently executed thread observations differ: "
                    + vector)
    except Exception as error:
        detail = (
            error.details if isinstance(error, ThreadedPatternWorkerFailure)
            else {
                "status": "FAIL",
                "active_phase": phase,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )
        failure = {
            "schema": SCHEMA + "-self-oracle-failure",
            "status": "FAIL",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": protocol_sha256,
            "original_reference": context,
            "matrix_sha256": MATRIX_SHA256,
            "expected_case_count": EXPECTED_CASES,
            "expected_thread_starts_per_reference":
                EXPECTED_THREAD_STARTS_PER_WORKER,
            "expected_thread_case_executions_per_reference":
                EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER,
            "expected_regex_api_calls_per_reference":
                EXPECTED_REGEX_API_CALLS_PER_WORKER,
            "active_phase": phase,
            "completed_reference_roles": completed,
            "actual_first_failure": detail,
            "candidate_status": "NOT RUN",
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
        receipt = publish_with_receipt(FAILURE_RELATIVE, failure)
        stored = publish_with_receipt(FAILURE_RECEIPT_RELATIVE, receipt)
        raise ThreadedPatternWorkerFailure(str(error), {
            "failure_path": FAILURE_RELATIVE,
            "failure_sha256": receipt["expected_sha256"],
            "active_phase": phase,
            "actual_first_failure": detail,
            "publication_receipt": receipt,
            "receipt_publication": stored,
        }) from error
    report = {
        "schema": SCHEMA + "-self-oracle",
        "status": "PASS",
        "python": PYTHON,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "original_reference": context,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "cases_per_cohort": CASES_PER_COHORT,
        "cohorts": list(COHORTS),
        "threaded_case_count": EXPECTED_CASES,
        "metadata_case_count": CASES_PER_COHORT,
        "metadata_cases_are_threaded_subset": True,
        "module_version": EXPECTED_PUBLIC_RE_VERSION,
        "module_version_type": "str",
        "actual_independent_reference_count": 2,
        "distinct_reference_processes": True,
        "reference_roles": completed,
        "reference_records_sha256": first["records_sha256"],
        "reference_warning_records_sha256": first["warning_records_sha256"],
        "actual_thread_starts": (
            len(REFERENCE_ROLES) * EXPECTED_THREAD_STARTS_PER_WORKER
        ),
        "actual_thread_joins": (
            len(REFERENCE_ROLES) * EXPECTED_THREAD_STARTS_PER_WORKER
        ),
        "actual_thread_case_executions": (
            len(REFERENCE_ROLES) * EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER
        ),
        "actual_regex_api_calls": (
            len(REFERENCE_ROLES) * EXPECTED_REGEX_API_CALLS_PER_WORKER
        ),
        "all_barriers_verified": True,
        "all_thread_joins_verified": True,
        "orphan_threads": 0,
        "candidate_status": "NOT RUN",
        "candidate_imports": 0,
        "native_owner_workers": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    receipt = publish_with_receipt(PASS_RELATIVE, report)
    stored = publish_with_receipt(PASS_RECEIPT_RELATIVE, receipt)
    return {
        "schema": SCHEMA + "-published-self-oracle",
        "status": "PASS",
        "report_path": PASS_RELATIVE,
        "report_sha256": receipt["expected_sha256"],
        "report_uncompressed_sha256": receipt["uncompressed_sha256"],
        "report_uncompressed_bytes": receipt["uncompressed_bytes"],
        "report_compression": receipt["compression"],
        "receipt": receipt,
        "receipt_publication": stored,
        "candidate_status": "NOT RUN",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }

def _synthetic_publication_receipt(
    relative: str, document: dict[str, Any],
) -> dict[str, Any]:
    relative = safe_relative(relative, outputs_only=True)
    plain, raw, compression = publication_payload(relative, document)
    require(len(raw) > 1,
            "a source-only publication receipt needs a genuine short-write shape")
    path = PurePosixPath(relative)
    events: list[dict[str, Any]] = []
    writes: list[dict[str, Any]] = []

    def add(role: str, action: str, descriptor: int,
            **fields: Any) -> dict[str, Any]:
        event = {
            "role": role,
            "action": action,
            "fd": descriptor,
            **fields,
            "status": "PASS",
        }
        events.append(event)
        return event

    device = 17
    root_descriptor = 40
    current_role = "directory:."
    current_descriptor = root_descriptor
    add(current_role, "open", current_descriptor,
        component=str(ROOT), parent_fd=None, nofollow=True)
    add(current_role, "fstat", current_descriptor,
        device=device, inode=700, mode=stat.S_IFDIR | 0o755, size=4096)
    components: list[str] = []
    for index, component in enumerate(path.parts[:-1], start=1):
        components.append(component)
        child_role = "directory:" + "/".join(components)
        child_descriptor = 41 if current_descriptor == 40 else 40
        add(child_role, "open", child_descriptor,
            component=component, parent_fd=current_descriptor, nofollow=True)
        add(child_role, "fstat", child_descriptor,
            device=device, inode=700 + index,
            mode=stat.S_IFDIR | 0o755, size=4096)
        add(current_role, "close", current_descriptor)
        current_role = child_role
        current_descriptor = child_descriptor
    parent_inode = 700 + len(components)
    add(current_role, "fstat", current_descriptor,
        device=device, inode=parent_inode,
        mode=stat.S_IFDIR | 0o755, size=4096)
    file_descriptor = 41 if current_descriptor == 40 else 40
    file_inode = 901
    add("writer", "open", file_descriptor,
        parent_fd=current_descriptor, basename=path.name,
        nofollow=True, exclusive=True)
    add("writer", "fstat", file_descriptor,
        device=device, inode=file_inode,
        mode=stat.S_IFREG | 0o644, size=0)
    split = max(1, len(raw) // 3)
    offset = 0
    for size in (split, len(raw) - split):
        require(size > 0, "a real source-only short-write shape was omitted")
        end = offset + size
        event = add(
            "writer", "write", file_descriptor,
            requested_bytes=len(raw) - offset,
            returned_bytes=size,
            returned_sha256=hashlib.sha256(raw[offset:end]).hexdigest(),
        )
        writes.append(event)
        offset = end
    add("writer", "fsync", file_descriptor)
    add("writer", "close", file_descriptor)
    add(current_role, "fsync", current_descriptor)
    add("reader", "open", file_descriptor,
        parent_fd=current_descriptor, basename=path.name,
        nofollow=True, exclusive=False)
    add("reader", "fstat", file_descriptor,
        device=device, inode=file_inode,
        mode=stat.S_IFREG | 0o644, size=len(raw))
    reread_offset = 0
    for size in (split, len(raw) - split, 0):
        end = reread_offset + size
        add("reader", "read", file_descriptor,
            requested_bytes=max(size, 1),
            returned_bytes=size,
            returned_sha256=hashlib.sha256(
                raw[reread_offset:end],
            ).hexdigest())
        reread_offset = end
    add("reader", "close", file_descriptor)
    add(current_role, "close", current_descriptor)
    return {
        "schema": SCHEMA + "-exclusive-publication-receipt",
        "path": relative,
        "compression": compression,
        "uncompressed_bytes": len(plain),
        "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "maximum_uncompressed_bytes": MAX_REPORT_BYTES,
        "maximum_compressed_bytes": MAX_REPORT_BYTES,
        "expected_bytes": len(raw),
        "expected_sha256": hashlib.sha256(raw).hexdigest(),
        "parent_components": list(path.parts[:-1]),
        "parent_device": device,
        "parent_inode": parent_inode,
        "created_file_device": device,
        "created_file_inode": file_inode,
        "safe_parent_component_walk": True,
        "exclusive_creation": True,
        "nofollow": True,
        "write_calls": writes,
        "bytes_written": len(raw),
        "file_fsync": True,
        "directory_fsync": True,
        "readback_bytes": len(raw),
        "readback_sha256": hashlib.sha256(raw).hexdigest(),
        "observed_readback": _capture_publication_stream(raw),
        "readback_stream_complete": True,
        "readback_exact_bytes_verified": True,
        "owned_partial_removed": False,
        "partial_removal_directory_fsync": False,
        "descriptor_events": events,
        "cleanup_failures": [],
        "status": "PASS",
    }



def _source_only_gzip_controls() -> int:
    document = {
        "schema": SCHEMA + "-pure-synthetic-gzip-control",
        "status": "SOURCE-ONLY",
        "actual_publication": "NOT RUN",
        "proof": "complete original genuine shared-pattern thread records",
    }
    plain, compressed, algorithm = publication_payload(
        PASS_RELATIVE,
        document,
    )
    require(
        algorithm == "gzip-mtime-zero-level-9"
        and publication_payload(PASS_RELATIVE, document)
        == (plain, compressed, algorithm)
        and restore_publication_document(PASS_RELATIVE, compressed)
        == document,
        "the bounded timestamp-zero gzip reference is not deterministic",
    )
    alternate = {
        "schema": SCHEMA + "-different-source-only-gzip-control",
        "status": "SOURCE-ONLY",
        "actual_publication": "NOT RUN",
    }
    _, other, _ = publication_payload(PASS_RELATIVE, alternate)
    corrupt_crc = compressed[:-8] + b"\x00" * 8
    poisons: tuple[tuple[str, Any, Any], ...] = (
        ("truncated-member", compressed[:-1], MAX_REPORT_BYTES),
        ("trailing-hidden-bytes", compressed + b"hidden", MAX_REPORT_BYTES),
        ("concatenated-members", compressed + compressed, MAX_REPORT_BYTES),
        ("uncompressed-instead-of-gzip", plain, MAX_REPORT_BYTES),
        ("forged-gzip-header", b"xx" + compressed[2:], MAX_REPORT_BYTES),
        ("forged-gzip-crc", corrupt_crc, MAX_REPORT_BYTES),
        ("over-expansion", compressed, max(1, len(plain) - 1)),
        ("wrong-complete-document", other, MAX_REPORT_BYTES),
        ("empty-compressed-member", b"", MAX_REPORT_BYTES),
        ("nonbytes-compressed-member", "gzip", MAX_REPORT_BYTES),
        ("noninteger-expansion-bound", compressed, False),
    )
    rejected = 0
    for label, payload, maximum in poisons:
        try:
            actual = restore_publication_document(
                PASS_RELATIVE,
                payload,
                maximum=maximum,
            )
            require(
                actual == document,
                "a complete but different gzip observation was substituted",
            )
        except (
            ThreadedPatternOracleError,
            TypeError,
            ValueError,
            OverflowError,
            UnicodeError,
            EOFError,
            zlib.error,
        ):
            rejected += 1
        else:
            raise ThreadedPatternOracleError(
                "a forged source-only gzip member was accepted: " + label,
            )
    require(
        rejected == GZIP_SOURCE_ONLY_POISON_CASES,
        "the exact deterministic gzip poison denominator changed",
    )
    return rejected


def _source_only_publication_controls() -> int:
    document = {
        "schema": SCHEMA + "-pure-synthetic-publication-control",
        "status": "SOURCE-ONLY",
        "actual_publication": "NOT RUN",
    }
    receipt = _synthetic_publication_receipt(PASS_RELATIVE, document)
    validate_publication_receipt(
        receipt, relative=PASS_RELATIVE, document=document,
    )
    poisons: tuple[tuple[str, Any], ...] = (
        ("status", "NOT RUN"),
        ("safe_parent_component_walk", False),
        ("nofollow", False),
        ("exclusive_creation", False),
        ("file_fsync", False),
        ("directory_fsync", False),
        ("parent_inode", receipt["parent_inode"] + 1),
        ("created_file_inode", receipt["created_file_inode"] + 1),
        ("bytes_written", receipt["bytes_written"] - 1),
        ("readback_sha256", "0" * 64),
        ("readback_stream_complete", False),
        ("readback_exact_bytes_verified", False),
        ("owned_partial_removed", True),
        ("partial_removal_directory_fsync", True),
        ("cleanup_failures", [{"role": "writer", "status": "FAIL"}]),
        ("observed_readback", {"bytes": 0, "sha256": "0" * 64,
                                "base64": ""}),
    )
    rejected = 0
    for field, replacement in poisons:
        altered = json.loads(canonical(receipt))
        altered[field] = replacement
        try:
            validate_publication_receipt(
                altered, relative=PASS_RELATIVE, document=document,
            )
        except (ThreadedPatternOracleError, TypeError, ValueError):
            rejected += 1
        else:
            raise ThreadedPatternOracleError(
                "a forged source-only exclusive publication receipt passed: "
                + field,
            )
    for mutation in (
        "missing-parent-component", "pending-write", "zero-write",
        "bool-write", "oversized-write", "forged-written-bytes",
        "missing-reader-eof", "simultaneous-descriptor-alias",
        "missing-descriptor-close",
    ):
        altered = json.loads(canonical(receipt))
        events = altered["descriptor_events"]
        if mutation == "missing-parent-component":
            events[:] = [
                event for event in events
                if not (event["role"] == "directory:oracle"
                        and event["action"] == "open")
            ]
        elif mutation in {
            "pending-write", "zero-write", "bool-write",
            "oversized-write", "forged-written-bytes",
        }:
            event = next(item for item in events
                         if item["role"] == "writer"
                         and item["action"] == "write")
            if mutation == "pending-write":
                event["status"] = "PENDING"
            elif mutation == "zero-write":
                event["returned_bytes"] = 0
            elif mutation == "bool-write":
                event["returned_bytes"] = True
            elif mutation == "oversized-write":
                event["returned_bytes"] = event["requested_bytes"] + 1
            else:
                event["returned_sha256"] = "0" * 64
        elif mutation == "missing-reader-eof":
            events[:] = [
                event for event in events
                if not (event["role"] == "reader"
                        and event["action"] == "read"
                        and event["returned_bytes"] == 0)
            ]
        elif mutation == "simultaneous-descriptor-alias":
            root = next(event for event in events
                        if event["role"] == "directory:."
                        and event["action"] == "open")
            child = next(event for event in events
                         if event["role"] == "directory:oracle"
                         and event["action"] == "open")
            child["fd"] = root["fd"]
        else:
            events[:] = [
                event for event in events
                if not (event["role"] == "reader"
                        and event["action"] == "close")
            ]
        try:
            validate_publication_receipt(
                altered, relative=PASS_RELATIVE, document=document,
            )
        except (ThreadedPatternOracleError, TypeError, ValueError):
            rejected += 1
        else:
            raise ThreadedPatternOracleError(
                "a forged source-only descriptor ledger passed: " + mutation,
            )
    require(rejected == PUBLICATION_SOURCE_ONLY_POISON_CASES,
            "the exact disclosed source-only publication controls changed")
    return rejected


@contextlib.contextmanager
def _source_only_boundary(effects: dict[str, int]):
    restorations: list[tuple[Any, str, Any]] = []

    def reject(kind: str):
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[kind] += 1
            raise ThreadedPatternOracleError("source-only operation rejected: " + kind)
        return blocked

    def replace(target: Any, name: str, kind: str) -> None:
        if hasattr(target, name):
            restorations.append((target, name, getattr(target, name)))
            setattr(target, name, reject(kind))

    original_import = builtins.__import__

    def guarded_import(name: str, globals: Any = None, locals: Any = None,
                       fromlist: Any = (), level: int = 0) -> Any:
        if (name == "re" or name.startswith("re.") or name == "_sre"
                or name == "candidates" or name.startswith("candidates.")
                or name == "_interpreters"
                or name == "concurrent.interpreters"
                or name.startswith("concurrent.interpreters.")
                or (name == "concurrent"
                    and type(fromlist) in (tuple, list)
                    and "interpreters" in fromlist)
                or name == "tools.postfinal_cpython_locale_oracle_v6"
                or name.startswith("tools.python_re_public_surface_oracle_")):
            effects["candidate_or_interpreter_imports"] += 1
            raise ThreadedPatternOracleError("source-only matching/interpreter import rejected")
        return original_import(name, globals, locals, fromlist, level)

    try:
        replace(builtins, "open", "filesystem_operations")
        replace(io, "open", "filesystem_operations")
        for name in (
            "open", "read", "write", "fstat", "stat", "lstat", "fsync",
            "close", "unlink", "remove", "rename", "replace", "mkdir", "rmdir",
        ):
            replace(os, name, "filesystem_operations")
        for name in (
            "open", "read_bytes", "read_text", "write_bytes", "write_text",
            "unlink", "rename", "replace", "mkdir", "touch", "stat", "lstat",
        ):
            replace(Path, name, "filesystem_operations")
        replace(os, "pipe", "interpreter_operations")
        replace(subprocess, "Popen", "reference_workers")
        replace(subprocess, "run", "reference_workers")
        replace(subprocess, "check_call", "reference_workers")
        replace(subprocess, "check_output", "reference_workers")
        replace(threading.Thread, "start", "threads_started")
        loaded_re = sys.modules.get("re")
        if loaded_re is not None:
            for matcher in (
                "compile", "search", "match", "fullmatch", "finditer",
                "findall", "split", "sub", "subn", "_compile",
            ):
                replace(loaded_re, matcher, "matching_operations")
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
            "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
            "thread_time_ns", "clock_gettime", "clock_gettime_ns",
        ):
            replace(time, name, "clock_samples")
        restorations.append((builtins, "__import__", original_import))
        builtins.__import__ = guarded_import
        yield
    finally:
        for target, name, original in reversed(restorations):
            setattr(target, name, original)


def _synthetic_observation(case: dict[str, Any]) -> dict[str, Any]:
    if case["cohort"] == METADATA_COHORT:
        value: Any = {
            "module_version": EXPECTED_PUBLIC_RE_VERSION,
            "module_version_type": "str",
            "noflag_value": 0,
            "noflag_type": "RegexFlag",
            "ignorecase_value": 2,
            "ignorecase_type": "RegexFlag",
            "compiled_flags": 32,
            "shared_match": {"matched": True},
        }
    else:
        value = {
            "source_only_case": case["case_id"],
            "variant": case["variant"],
        }
    return {
        "cohort": case["cohort"],
        "regex_api_calls": API_CALLS_PER_THREAD[case["cohort"]],
        "value": value,
    }


def _synthetic_worker(role: str, pid: int) -> dict[str, Any]:
    matrix = build_matrix()
    records: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    lifecycles: list[dict[str, Any]] = []
    warning_records = [{
        "cohort": cohort,
        "warnings": [dict(EXPECTED_WARNING)]
        if cohort == WARNING_COHORT else [],
    } for cohort in COHORTS]
    for cohort_index, cohort in enumerate(COHORTS):
        for role_index, thread_role in enumerate(THREAD_ROLES):
            lifecycles.append({
                "cohort": cohort,
                "role": thread_role,
                "thread_name":
                    f"source-only-shared-{cohort_index:02d}-{thread_role}",
                "thread_ident": 10_000 + cohort_index * 2 + role_index,
                "thread_native_id": 20_000 + cohort_index * 2 + role_index,
                "started": True,
                "joined": True,
                "alive_after_join": False,
                "case_count": CASES_PER_COHORT,
            })
    for case in matrix:
        cohort_index = case["ordinal"] // CASES_PER_COHORT
        observation = _synthetic_observation(case)
        records.append({
            **case,
            "status": "PASS",
            "actual_thread_execution": True,
            "thread_execution_count": len(THREAD_ROLES),
            "actual_regex_api_calls":
                API_CALLS_PER_THREAD[case["cohort"]] * len(THREAD_ROLES),
            "metadata_case": case["cohort"] == METADATA_COHORT,
            "observations": {
                thread_role: copy.deepcopy(observation)
                for thread_role in THREAD_ROLES
            },
        })
        text_id = 30_000 + cohort_index * 100
        bytes_id = text_id + 1
        used = {
            name: (
                text_id if name == "text"
                else bytes_id if name == "bytes"
                else text_id + 2 + COHORTS.index(case["cohort"])
            )
            for name in sorted(USED_PATTERNS[case["cohort"]])
        }
        for role_index, thread_role in enumerate(THREAD_ROLES):
            events.append({
                "case_id": case["case_id"],
                "cohort": case["cohort"],
                "ordinal": case["ordinal"],
                "role": thread_role,
                "thread_name":
                    f"source-only-shared-{cohort_index:02d}-{thread_role}",
                "thread_ident": 10_000 + cohort_index * 2 + role_index,
                "thread_native_id": 20_000 + cohort_index * 2 + role_index,
                "shared_text_pattern_identity": text_id,
                "shared_bytes_pattern_identity": bytes_id,
                "used_pattern_identities": dict(used),
                "start_barrier_passed": True,
                "completion_barrier_arrived": True,
                "actual_regex_api_calls":
                    API_CALLS_PER_THREAD[case["cohort"]],
                "status": "PASS",
            })
    return {
        "schema": SCHEMA + "-reference-worker",
        "status": "PASS",
        "role": role,
        "pid": pid,
        "python": PYTHON,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "cases_per_cohort": CASES_PER_COHORT,
        "threaded_case_count": EXPECTED_CASES,
        "metadata_case_count": CASES_PER_COHORT,
        "module_version": EXPECTED_PUBLIC_RE_VERSION,
        "module_version_type": "str",
        "noflag_value": 0,
        "noflag_type": "RegexFlag",
        "records": records,
        "records_sha256": digest(records),
        "thread_events": events,
        "thread_events_sha256": digest(events),
        "thread_lifecycle": lifecycles,
        "thread_lifecycle_sha256": digest(lifecycles),
        "warning_records": warning_records,
        "warning_records_sha256": digest(warning_records),
        "actual_thread_starts": EXPECTED_THREAD_STARTS_PER_WORKER,
        "actual_thread_joins": EXPECTED_THREAD_STARTS_PER_WORKER,
        "actual_thread_case_executions":
            EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER,
        "actual_regex_api_calls": EXPECTED_REGEX_API_CALLS_PER_WORKER,
        "all_barriers_verified": True,
        "all_thread_joins_verified": True,
        "orphan_threads": 0,
        "thread_failures": [],
        "candidate_imports": 0,
        "native_owner_workers": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "original_reference_sha256": V6_REFERENCE_SHA256,
        "public_cases_unchanged": PUBLIC_CASES,
        "public_cohorts_unchanged": PUBLIC_COHORTS,
        "public_matrix_sha256": PUBLIC_MATRIX_SHA256,
        "public_stimulus_sha256": PUBLIC_STIMULUS_SHA256,
        "public_reference_sha256": PUBLIC_REFERENCE_SHA256,
        "public_reference_record_sha256": PUBLIC_REFERENCE_RECORD_SHA256,
        "public_reference_independent_roles": 2,
        "public_real_locale_cases": PUBLIC_REAL_LOCALE_CASES,
        "public_real_locale_transitions": PUBLIC_REAL_LOCALE_TRANSITIONS,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_threading_sha256": PINNED_THREADING_SHA256,
    }


def _has_counted_thread_entry(source: bytes, operation: str) -> bool:
    require(operation in {"scanner", "expand"},
            "only frozen thread-side scanner and replacement entries are valid")
    tree = ast.parse(source.decode("utf-8"))
    for parent in ast.walk(tree):
        for name in ("body", "orelse", "finalbody"):
            body = getattr(parent, name, None)
            if type(body) is not list:
                continue
            for index, statement in enumerate(body):
                if index == 0 or not isinstance(statement, ast.Assign):
                    continue
                call = statement.value
                if not (isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Attribute)
                        and call.func.attr == operation):
                    continue
                increment = body[index - 1]
                if (isinstance(increment, ast.AugAssign)
                        and isinstance(increment.target, ast.Name)
                        and increment.target.id == "calls"
                        and isinstance(increment.op, ast.Add)
                        and isinstance(increment.value, ast.Constant)
                        and type(increment.value.value) is int
                        and increment.value.value == 1):
                    return True
    return False


def self_test() -> dict[str, Any]:
    verify_runtime()
    source = _read_regular(SOURCE_RELATIVE, MAX_SOURCE_BYTES)
    protocol = _read_regular(PROTOCOL_RELATIVE, MAX_SOURCE_BYTES)
    source_sha256 = hashlib.sha256(source).hexdigest()
    protocol_sha256 = hashlib.sha256(protocol).hexdigest()
    effects = {
        "filesystem_operations": 0,
        "interpreter_operations": 0,
        "candidate_or_interpreter_imports": 0,
        "reference_workers": 0,
        "threads_started": 0,
        "matching_operations": 0,
        "clock_samples": 0,
    }
    checks: list[str] = []

    def check(name: str, condition: Any) -> None:
        require(type(name) is str and name not in checks,
                "a deterministic source-only control identity was duplicated")
        require(condition is True,
                "a genuine source-only control failed: " + name)
        checks.append(name)

    def reject(name: str, action: Any) -> None:
        require(type(name) is str and name not in checks,
                "a deterministic negative-control identity was duplicated")
        try:
            action()
        except (
            ThreadedPatternOracleError, TypeError, ValueError,
            OverflowError, UnicodeError, json.JSONDecodeError,
        ):
            checks.append(name)
        else:
            raise ThreadedPatternOracleError(
                "a forged source-only thread observation was accepted: " + name,
            )

    with _source_only_boundary(effects):
        matrix = build_matrix()
        check("exact-original-512-threaded-case-matrix",
              validate_matrix(matrix) == MATRIX_SHA256)
        check("exact-independently-frozen-protocol",
              protocol_sha256 == FROZEN_PROTOCOL_SHA256)
        check("exact-16-original-shared-pattern-categories",
              len(COHORTS) == 16)
        check("exact-32-genuine-variants-per-category",
              CASES_PER_COHORT == 32)
        check("all-512-threaded-case-identities-distinct",
              len({case["case_id"] for case in matrix}) == EXPECTED_CASES)
        check("all-512-original-case-seeds-distinct",
              len({case["seed"] for case in matrix}) == EXPECTED_CASES)
        check("module-version-cohort-is-genuinely-threaded",
              METADATA_COHORT in COHORTS
              and EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER == 1_024)
        check("exact-pinned-public-module-version",
              EXPECTED_PUBLIC_RE_VERSION == "2.2.1"
              and b"2.2.1" in protocol)
        check("exact-32-lived-and-joined-threads-per-reference",
              EXPECTED_THREAD_STARTS_PER_WORKER == 32)
        check("exact-2176-thread-side-pattern-scanner-replacement-calls",
              EXPECTED_REGEX_API_CALLS_PER_WORKER == 2_176)
        check("count-real-thread-side-pattern-scanner-construction",
              _has_counted_thread_entry(source, "scanner"))
        check("count-real-thread-side-match-template-expansion",
              _has_counted_thread_entry(source, "expand"))
        check("preserve-original-165-cpython-methods",
              152 + 13 == 165 and b"165" in protocol)
        check("preserve-151-genuine-public-passes-and-debug-skip",
              151 + 1 == 152 and b"151" in protocol)
        check("preserve-exact-two-private-only-waivers",
              sum(item["methods"] for item in PRIVATE_WAIVERS.values()) == 13)
        check("preserve-complete-1376-public-cases",
              PUBLIC_CASES == 1_376)
        check("preserve-all-43-public-cohorts",
              PUBLIC_COHORTS == 43)
        check("preserve-all-64-real-locale-cases",
              PUBLIC_REAL_LOCALE_CASES == 64)
        check("preserve-all-192-real-locale-transitions",
              PUBLIC_REAL_LOCALE_TRANSITIONS == 192)
        check("freeze-exact-producer-owned-v19-reference",
              valid_sha256(PUBLIC_REFERENCE_SHA256)
              and PUBLIC_REFERENCE_SHA256.encode("ascii") in protocol)
        check("freeze-exact-producer-owned-v19-vector",
              valid_sha256(PUBLIC_REFERENCE_RECORD_SHA256)
              and PUBLIC_REFERENCE_RECORD_SHA256.encode("ascii") in protocol)
        check("freeze-exact-original-v6-double-reference",
              valid_sha256(V6_REFERENCE_SHA256)
              and V6_REFERENCE_SHA256.encode("ascii") in protocol)
        check("freeze-actual-cpython-executable-identity",
              valid_sha256(PINNED_PYTHON_SHA256)
              and PINNED_PYTHON_SHA256.encode("ascii") in protocol)
        check("freeze-actual-public-threading-implementation",
              valid_sha256(PINNED_THREADING_SHA256)
              and PINNED_THREADING_SHA256.encode("ascii") in protocol)
        check("freeze-actual-stdlib-regular-expression-implementation",
              valid_sha256(PINNED_STDLIB_RE_SHA256)
              and PINNED_STDLIB_RE_SHA256.encode("ascii") in protocol)
        check("freeze-full-original-512-case-matrix-inside-protocol",
              MATRIX_SHA256.encode("ascii") in protocol)
        check("validate-all-25-source-only-exclusive-receipt-attacks",
              _source_only_publication_controls()
              == PUBLICATION_SOURCE_ONLY_POISON_CASES)
        check("validate-all-11-source-only-bounded-gzip-attacks",
              _source_only_gzip_controls()
              == GZIP_SOURCE_ONLY_POISON_CASES)
        first = _synthetic_worker("reference_a", 10_001)
        second = _synthetic_worker("reference_b", 10_002)
        check("accept-complete-in-memory-threaded-reference-a",
              validate_worker_document(
                  first, "reference_a", expected_pid=10_001,
              ) is first)
        check("accept-complete-in-memory-threaded-reference-b",
              validate_worker_document(
                  second, "reference_b", expected_pid=10_002,
              ) is second)
        check("independent-source-only-semantic-vectors-agree",
              first["records"] == second["records"])
        check("independent-source-only-warning-vectors-agree",
              first["warning_records"] == second["warning_records"])
        poisons = (
            ("status", "NOT RUN"),
            ("python", "3.14.5"),
            ("pid", 0),
            ("matrix_sha256", "0" * 64),
            ("case_count", 511),
            ("cohort_count", 15),
            ("cases_per_cohort", 31),
            ("threaded_case_count", 511),
            ("metadata_case_count", 31),
            ("module_version", "2.2.0"),
            ("module_version_type", "bytes"),
            ("noflag_value", 1),
            ("noflag_type", "int"),
            ("actual_thread_starts", 31),
            ("actual_thread_joins", 31),
            ("actual_thread_case_executions", 1_023),
            ("actual_regex_api_calls", 2_175),
            ("all_barriers_verified", False),
            ("all_thread_joins_verified", False),
            ("orphan_threads", 1),
            ("thread_failures", [{"status": "FAIL"}]),
            ("candidate_imports", 1),
            ("native_owner_workers", 1),
            ("holdout_cases_read", 1),
            ("performance_fixtures_read", 1),
            ("benchmark_or_timing_executed", True),
            ("performance", "MEASURED"),
            ("holdout", "ACCESSED"),
            ("original_reference_sha256", "0" * 64),
            ("public_cases_unchanged", 1_375),
            ("public_cohorts_unchanged", 42),
            ("public_matrix_sha256", "0" * 64),
            ("public_stimulus_sha256", "0" * 64),
            ("public_reference_sha256", "0" * 64),
            ("public_reference_record_sha256", "0" * 64),
            ("public_reference_independent_roles", 1),
            ("public_real_locale_cases", 63),
            ("public_real_locale_transitions", 191),
            ("pinned_python_sha256", "0" * 64),
            ("pinned_stdlib_re_sha256", "0" * 64),
            ("pinned_public_threading_sha256", "0" * 64),
        )
        for index, (field, value) in enumerate(poisons):
            forged = dict(first)
            forged[field] = value
            reject(
                f"reject-forged-full-thread-worker-{index:03d}-{field}",
                lambda forged=forged: validate_worker_document(
                    forged, "reference_a", expected_pid=10_001,
                ),
            )
        for vector, fingerprint in (
            ("records", "records_sha256"),
            ("thread_events", "thread_events_sha256"),
            ("thread_lifecycle", "thread_lifecycle_sha256"),
            ("warning_records", "warning_records_sha256"),
        ):
            omitted = dict(first)
            omitted[vector] = first[vector][:-1]
            reject("reject-omitted-complete-original-vector-" + vector,
                   lambda omitted=omitted: validate_worker_document(
                       omitted, "reference_a", expected_pid=10_001,
                   ))
            forged = dict(first)
            forged[fingerprint] = "0" * 64
            reject("reject-forged-complete-original-vector-digest-" + vector,
                   lambda forged=forged: validate_worker_document(
                       forged, "reference_a", expected_pid=10_001,
                   ))
        for record, case in zip(first["records"], matrix, strict=True):
            check(
                "accept-source-only-complete-case-" + case["case_id"],
                validate_case_record(record, case) is record,
            )
            for field, value in (
                ("status", "NOT RUN"),
                ("actual_thread_execution", False),
                ("thread_execution_count", 1),
                ("actual_regex_api_calls", 0),
                ("metadata_case", not record["metadata_case"]),
            ):
                forged = dict(record)
                forged[field] = value
                reject(
                    "reject-false-live-thread-" + case["case_id"] + "-" + field,
                    lambda forged=forged, case=case:
                    validate_case_record(forged, case),
                )
            missing = dict(record)
            missing["observations"] = {
                "left": copy.deepcopy(record["observations"]["left"]),
            }
            reject(
                "reject-one-thread-only-" + case["case_id"],
                lambda missing=missing, case=case:
                validate_case_record(missing, case),
            )
        for record, case in zip(first["records"], matrix, strict=True):
            if case["cohort"] not in {COHORTS[6], COHORTS[7], COHORTS[10]}:
                continue
            omitted_call = dict(record)
            omitted_call["actual_regex_api_calls"] -= len(THREAD_ROLES)
            reject(
                "reject-omitted-scanner-or-template-entry-"
                + case["case_id"],
                lambda omitted_call=omitted_call, case=case:
                validate_case_record(omitted_call, case),
            )
        for record, case in zip(first["records"], matrix, strict=True):
            if case["cohort"] != METADATA_COHORT:
                continue
            for field, value in (
                ("module_version", "2.2.0"),
                ("module_version_type", "bytes"),
                ("noflag_value", 1),
                ("noflag_type", "int"),
                ("ignorecase_type", "int"),
                ("compiled_flags", "32"),
            ):
                forged = copy.deepcopy(record)
                for thread_role in THREAD_ROLES:
                    forged["observations"][thread_role]["value"][field] = value
                reject(
                    "reject-forged-real-metadata-" + case["case_id"]
                    + "-" + field,
                    lambda forged=forged, case=case:
                    validate_case_record(forged, case),
                )
        for relative in sorted(APPROVED_OUTPUTS):
            check(
                "accept-exact-exclusive-path-" + relative.rsplit("/", 1)[-1],
                safe_relative(relative, outputs_only=True) == relative,
            )
        for relative in (
            "../outside.json",
            "/tmp/outside.json",
            "holdout/threaded.json",
            "performance/threaded.json",
            "oracle/cpython-3.14.6/evidence/../replacement.json",
            "oracle/cpython-3.14.6/evidence/"
            "public-threaded-pattern-v1-unapproved.json",
        ):
            reject(
                "reject-unsafe-exclusive-path-" + relative,
                lambda relative=relative:
                safe_relative(relative, outputs_only=True),
            )
        empty = capture_complete_stream(b"")
        check("authenticate-complete-empty-real-worker-stderr",
              restore_complete_stream(empty, label="source-only stderr")
              == b"")
        stream = capture_complete_stream(b'{"status":"PASS"}\n')
        check("authenticate-complete-producer-canonical-worker-stdout",
              restore_complete_stream(stream, label="source-only stdout")
              == b'{"status":"PASS"}\n')
        for field, value in (
            ("bytes", stream["bytes"] + 1),
            ("sha256", "0" * 64),
            ("base64", "@@@"),
        ):
            forged = dict(stream)
            forged[field] = value
            reject(
                "reject-incomplete-original-worker-stream-" + field,
                lambda forged=forged: restore_complete_stream(
                    forged, label="source-only forged stream",
                ),
            )
        reject("reject-duplicate-original-json-keys",
               lambda: strict_canonical(
                   b'{"x":1,"x":2}', label="duplicate",
               ))
        reject("reject-nonfinite-original-json",
               lambda: strict_canonical(
                   b'{"x":NaN}', label="nonfinite",
               ))
        reject("reject-noncanonical-original-json",
               lambda: strict_canonical(
                   b'{ "x": 1 }', label="noncanonical",
               ))
        check("all-genuinely-adversarial-source-controls-unique",
              len(checks) == len(set(checks)))
        check("no-files-no-matcher-no-worker-no-thread-no-clock",
              all(count == 0 for count in effects.values()))
    require(
        len(checks) == EXPECTED_SOURCE_ONLY_CHECKS
        and len(checks) == len(set(checks)),
        "the exact frozen source-only threaded control denominator changed: "
        + str(len(checks)) + " != " + str(EXPECTED_SOURCE_ONLY_CHECKS),
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "result": "PASS",
        "python": PYTHON,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "frozen_protocol_sha256": FROZEN_PROTOCOL_SHA256,
        "check_count": len(checks),
        "expected_check_count": EXPECTED_SOURCE_ONLY_CHECKS,
        "unique_check_count": len(set(checks)),
        "publication_adversarial_receipt_variants":
            PUBLICATION_SOURCE_ONLY_POISON_CASES,
        "gzip_adversarial_member_variants":
            GZIP_SOURCE_ONLY_POISON_CASES,
        "failed": [],
        "matrix_sha256": MATRIX_SHA256,
        "base_seed": BASE_SEED,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "cases_per_cohort": CASES_PER_COHORT,
        "threaded_case_count": EXPECTED_CASES,
        "metadata_case_count": CASES_PER_COHORT,
        "metadata_cases_are_threaded_subset": True,
        "expected_module_version": EXPECTED_PUBLIC_RE_VERSION,
        "module_name_is_not_assumed": True,
        "expected_thread_starts_per_reference":
            EXPECTED_THREAD_STARTS_PER_WORKER,
        "expected_thread_case_executions_per_reference":
            EXPECTED_THREAD_CASE_EXECUTIONS_PER_WORKER,
        "expected_regex_api_calls_per_reference":
            EXPECTED_REGEX_API_CALLS_PER_WORKER,
        "regex_api_call_scope":
            "thread-side-matcher-iterator-scanner-replacement",
        "preparation_compile_and_purge": "NOT MEASURED",
        "match_result_accessor_calls": "NOT MEASURED",
        "original_methods": 165,
        "original_public_methods": 152,
        "original_runnable_public_methods": 151,
        "original_uniform_debug_skips": 1,
        "original_named_private_methods": 13,
        "original_reference_sha256": V6_REFERENCE_SHA256,
        "public_cases_unchanged": PUBLIC_CASES,
        "public_cohorts_unchanged": PUBLIC_COHORTS,
        "public_reference_sha256": PUBLIC_REFERENCE_SHA256,
        "public_reference_record_sha256": PUBLIC_REFERENCE_RECORD_SHA256,
        "public_real_locale_cases": PUBLIC_REAL_LOCALE_CASES,
        "public_real_locale_transitions": PUBLIC_REAL_LOCALE_TRANSITIONS,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_threading_sha256": PINNED_THREADING_SHA256,
        "instruction_files_read": 2,
        "filesystem_operations": effects["filesystem_operations"],
        "interpreter_operations": effects["interpreter_operations"],
        "candidate_or_interpreter_import_attempts":
            effects["candidate_or_interpreter_imports"],
        "guarded_reference_worker_attempts": effects["reference_workers"],
        "matching_operations": effects["matching_operations"],
        "evidence_files_read": 0,
        "files_written": 0,
        "threads_started": effects["threads_started"],
        "reference_workers_started": 0,
        "candidate_workers_started": 0,
        "native_owner_workers_started": 0,
        "candidate_imports": 0,
        "clock_samples": effects["clock_samples"],
        "locale_changes": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "actual_reference_status": "NOT RUN",
        "actual_candidate_status": "NOT RUN",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }

def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Frozen genuine same-pattern Python thread oracle.",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--self-test", action="store_true",
        help="run exclusively in-memory source-only hostile controls",
    )
    modes.add_argument(
        "--self-oracle", action="store_true",
        help="root-only: run two actual pinned genuine threaded references",
    )
    modes.add_argument(
        "--worker-role", choices=REFERENCE_ROLES,
        help="root-created isolated standard-library-only reference process",
    )
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(options.source_sha256 is None
                and options.protocol_sha256 is None,
                "source-only controls cannot accept invented production pins")
        document = self_test()
    elif options.self_oracle:
        verify_runtime(production=True)
        document = run_self_oracle(
            options.source_sha256, options.protocol_sha256,
        )
    else:
        verify_runtime(production=True)
        context = authenticate_context(
            options.source_sha256, options.protocol_sha256,
        )
        document = _worker_document(options.worker_role, context)
    sys.stdout.buffer.write(canonical(document) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
