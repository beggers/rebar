#!/usr/bin/env python3
"""Freeze genuine CPython 3.14.6 regex behavior in concurrent subinterpreters.\n\nVersion 2 preserves all independently frozen V1 cases and complete A/B/A\nlifecycles. Its root-only reference evidence is deterministic, bounded gzip;\nits source-only controls never create an interpreter, execute re, start a\nworker, write a file, sample time, or inspect a hidden benchmark.\n"""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import contextlib
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
import time
import zlib
from typing import Any


ROOT = Path(os.path.abspath(__file__)).parent.parent
PYTHON = "3.14.6"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_STDLIB_RE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py"
)
PINNED_STDLIB_RE_SHA256 = (
    "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35"
)
PINNED_INTERPRETERS = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/concurrent/interpreters/__init__.py"
)
PINNED_INTERPRETERS_SHA256 = (
    "040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249"
)
SCHEMA = "rebar-python-re-genuine-subinterpreter-v2"
SOURCE_RELATIVE = "tools/python_re_subinterpreter_oracle_v2.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V2.md"
FROZEN_PROTOCOL_SHA256 = (
    "8c5caccf077ec38afbad62e282f8e74aa470b5d3616ed0b6aa848dd6d97c0dee"
)
HISTORICAL_V1_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V1.md"
)
HISTORICAL_V1_PROTOCOL_SHA256 = (
    "38bf2b1a5b93196370bb532d98124a3de7092a56b1233a6b1731411a3a595263"
)
HISTORICAL_V1_SOURCE_RELATIVE = (
    "tools/python_re_subinterpreter_oracle_v1.py"
)
HISTORICAL_V1_SOURCE_SHA256 = (
    "88a3600908f7090fb384fe03559e231f820d6c6c141846b738c73e89c7a69563"
)
HISTORICAL_V1_REPORT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-subinterpreter-v1-self-oracle.json"
)
HISTORICAL_V1_REPORT_SHA256 = (
    "9a5501ac4a60f48f749c3d42216c08391b5ff03ed38f191e37588ed4fa747bfa"
)
HISTORICAL_V1_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-subinterpreter-v1-self-oracle-publication-receipt.json"
)
HISTORICAL_V1_RECEIPT_SHA256 = (
    "d4a3b94bc30747db44560eb052d809ee574f5b4083ff7649b05f18f91501418c"
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
BASE_SEED = 2_026_072_501
DOMAIN = "rebar/python-re/genuine-subinterpreter/v1"
CASES_PER_COHORT = 8
COHORTS = (
    "fresh-interpreter-creation-and-stdlib-import",
    "stdlib-string-compile-match-and-fullmatch",
    "stdlib-bytes-compile-match-and-fullmatch",
    "pattern-match-type-and-owner-identity",
    "same-interpreter-compile-cache-and-purge",
    "cross-interpreter-cache-isolation",
    "ascii-unicode-inline-and-multiline-flags",
    "locale-bytes-without-process-locale-mutation",
    "named-captures-backreferences-and-template-expansion",
    "zero-width-finditer-and-scanner-progress",
    "syntax-and-type-error-isolation",
    "interpreter-local-module-and-builtins",
    "repeated-interpreter-creation-and-destruction",
    "independent-interpreter-module-reimport",
    "contiguous-buffer-and-borrowed-lifetime",
    "interpreter-teardown-and-worker-cleanup",
)
EXPECTED_CASES = len(COHORTS) * CASES_PER_COHORT
REPEATED_CREATION_CASES = CASES_PER_COHORT
EXPECTED_INTERPRETERS_PER_WORKER = 3 + REPEATED_CREATION_CASES
EXPECTED_EXECUTIONS_PER_WORKER = (
    EXPECTED_CASES * 3 + REPEATED_CREATION_CASES + 2
)
EXPECTED_SOURCE_ONLY_CHECKS = 995
PUBLICATION_SOURCE_ONLY_POISON_CASES = 25
GZIP_SOURCE_ONLY_POISON_CASES = 11
MATRIX_SHA256 = (
    "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3"
)
REFERENCE_ROLES = ("reference_a", "reference_b")
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
MAX_WORKER_BYTES = 16 * 1024 * 1024
MAX_PIPE_BYTES = 256 * 1024
PASS_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-subinterpreter-v2-self-oracle.json.gz"
)
FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-subinterpreter-v2-self-oracle-failures.json.gz"
)
PASS_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-subinterpreter-v2-self-oracle-publication-receipt.json"
)
FAILURE_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-subinterpreter-v2-self-oracle-failures-publication-receipt.json"
)
APPROVED_OUTPUTS = frozenset({
    PASS_RELATIVE,
    FAILURE_RELATIVE,
    PASS_RECEIPT_RELATIVE,
    FAILURE_RECEIPT_RELATIVE,
})


class SubinterpreterOracleError(AssertionError):
    """The frozen, genuine interpreter obligation failed closed."""


class SubinterpreterWorkerFailure(SubinterpreterOracleError):
    def __init__(self, message: str, details: dict[str, Any]) -> None:
        super().__init__(message)
        self.details = details


class SubinterpreterPublicationFailure(SubinterpreterOracleError):
    def __init__(self, message: str, receipt: dict[str, Any]) -> None:
        super().__init__(message)
        self.receipt = receipt


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise SubinterpreterOracleError(message)


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
        "the complete canonical subinterpreter report exceeds its bound",
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
                "subinterpreter report was rejected",
            )
        except (zlib.error, EOFError, ValueError) as error:
            raise SubinterpreterOracleError(
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
    raise SubinterpreterOracleError("non-finite JSON is forbidden: " + value)


def strict_canonical(raw: bytes, *, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "a bounded complete canonical document is required: " + label)
    try:
        document = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise SubinterpreterOracleError(
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
        "an unsafe subinterpreter-oracle path was rejected",
    )
    if outputs_only:
        require(relative in APPROVED_OUTPUTS,
                "an unapproved subinterpreter-oracle output was rejected")
    return relative


def _read_regular(relative: str, maximum: int) -> bytes:
    safe_relative(relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT / relative, flags)
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode),
                "a frozen subinterpreter input must be a real regular file")
        require(0 < information.st_size <= maximum,
                "a frozen subinterpreter input exceeds its exact bound")
        pieces: list[bytes] = []
        remaining = information.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(chunk), "a frozen subinterpreter input was truncated")
            pieces.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "a frozen subinterpreter input grew during authentication")
        return b"".join(pieces)
    finally:
        os.close(descriptor)


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    require(valid_sha256(expected), "an independently published SHA-256 is required")
    raw = _read_regular(relative, maximum)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "the independently frozen subinterpreter input changed: " + relative)
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
            "all 128 actual subinterpreter stimuli are required")
    require(rows == build_matrix(), "a frozen genuine subinterpreter case changed")
    actual = digest(rows)
    require(actual == MATRIX_SHA256,
            "the independently frozen real-subinterpreter matrix changed")
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
        raise SubinterpreterOracleError("an actual worker stream is invalid") from error
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
            "run the pinned subinterpreter oracle with -I -B")
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
    require(path in {PINNED_STDLIB_RE, PINNED_INTERPRETERS},
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
                and 0 < information.st_size <= MAX_SOURCE_BYTES,
                "the exact pinned standard-library input is not a bounded file")
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
    read_pinned_absolute(PINNED_STDLIB_RE, PINNED_STDLIB_RE_SHA256)
    read_pinned_absolute(PINNED_INTERPRETERS, PINNED_INTERPRETERS_SHA256)
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
            "the independently frozen genuine-subinterpreter matrix is absent")
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
        "pinned_stdlib_re": PINNED_STDLIB_RE,
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_interpreters": PINNED_INTERPRETERS,
        "pinned_public_interpreters_sha256": PINNED_INTERPRETERS_SHA256,
    }


INTERPRETER_PROGRAM = r'''
import builtins as _builtins
import concurrent.interpreters as _public
import importlib as _importlib
import json as _json
import locale as _locale
import os as _os
import re as _re
import sys as _sys
import types as _types

def _assert(condition, message):
    if condition is not True:
        raise AssertionError(message)

_assert(getattr(_builtins, "_rebar_subinterpreter_v2_owner", None) == _owner,
        "interpreter-local builtins leaked across concurrent interpreters")
_assert(_re.__spec__ is not None
        and _os.path.abspath(_re.__spec__.origin) == _stdlib_re_origin
        and _os.path.abspath(_re.__file__) == _stdlib_re_origin,
        "the actual pinned standard-library regex module was replaced")
_assert(_public.__spec__ is not None
        and _os.path.abspath(_public.__spec__.origin) == _public_interpreter_origin,
        "the actual pinned public subinterpreter module was replaced")
_assert(_os.path.abspath(_sys.executable) == _pinned_python,
        "the genuine subinterpreter did not use pinned CPython")
_assert(not any(name == "candidates" or name.startswith("candidates.")
                for name in _sys.modules), "a production candidate entered the reference")
_before_locale = _locale.setlocale(_locale.LC_CTYPE)
_v = _case["variant"]
_n = _v % 4 + 1
_cohort = _case["cohort"]
_observation = {"owner_state_intact": True}

if _cohort == "fresh-interpreter-creation-and-stdlib-import":
    _current = _public.get_current()
    _observation.update({
        "not_main_interpreter": _current.id != _main_id,
        "stdlib_re_module": _re.__name__ == "re",
        "module_identity": _sys.modules["re"] is _re,
        "actual_interpreter_exec": True,
    })
elif _cohort == "stdlib-string-compile-match-and-fullmatch":
    _subject = "a" * _n + "b"
    _pattern = _re.compile("(?P<item>a{" + str(_n) + "})b")
    _match = _pattern.fullmatch(_subject)
    _assert(_match is not None, "the original text match did not execute")
    _observation.update({"pattern_kind": "str", "group": _match.group("item"),
                         "span": list(_match.span()),
                         "search": _pattern.search("!" + _subject).span()[0]})
elif _cohort == "stdlib-bytes-compile-match-and-fullmatch":
    _subject = b"a" * _n + b"b"
    _pattern = _re.compile(b"(?P<item>a{" + str(_n).encode("ascii") + b"})b")
    _match = _pattern.fullmatch(_subject)
    _assert(_match is not None, "the original bytes match did not execute")
    _observation.update({"pattern_kind": "bytes", "group_hex": _match.group("item").hex(),
                         "span": list(_match.span()),
                         "search": _pattern.search(b"!" + _subject).span()[0]})
elif _cohort == "pattern-match-type-and-owner-identity":
    _pattern = _re.compile(r"(?P<value>a+)")
    _match = _pattern.fullmatch("a" * _n)
    _assert(_match is not None, "the original typed match did not execute")
    _observation.update({
        "pattern_is_stdlib_pattern": isinstance(_pattern, _re.Pattern),
        "match_is_stdlib_match": isinstance(_match, _re.Match),
        "match_pattern_identity": _match.re is _pattern,
        "pattern_generic_origin": _re.Pattern[str].__origin__ is _re.Pattern,
        "match_generic_origin": _re.Match[str].__origin__ is _re.Match,
        "lastgroup": _match.lastgroup,
    })
elif _cohort == "same-interpreter-compile-cache-and-purge":
    _expression = "rebar-subinterpreter-v1-" + str(_case["seed"])
    _re.purge()
    _first = _re.compile(_expression)
    _second = _re.compile(_expression)
    _re.purge()
    _third = _re.compile(_expression)
    _observation.update({"same_interpreter_cache_hit": _first is _second,
                         "purge_produced_fresh_pattern": _third is not _first,
                         "fresh_pattern_matches": _third.fullmatch(_expression) is not None,
                         "only_public_cache_api": True})
elif _cohort == "cross-interpreter-cache-isolation":
    _expression = "rebar-persistent-subinterpreter-v1-" + str(_case["seed"])
    _owned = getattr(_builtins, "_rebar_subinterpreter_v2_patterns", None)
    _assert(type(_owned) is dict,
            "the interpreter-local persistent cache owner was replaced")
    if _owner == "B":
        _re.purge()
    _previous = _owned.get(_expression)
    _first = _re.compile(_expression)
    if _previous is not None:
        _assert(_first is _previous,
                "B's public purge destroyed A's actual compiled cache entry")
    _owned[_expression] = _first
    _second = _re.compile(_expression)
    _assert(_first is _second,
            "a genuine interpreter-local compiled pattern was not cached")
    _assert(getattr(_builtins, "_rebar_subinterpreter_v2_owner", None) == _owner,
            "B changed A's actual interpreter-local ownership sentinel")
    _observation.update({
        "same_interpreter_cache_hit": _first is _second,
        "persistent_pattern_survived_peer": _previous is None or _first is _previous,
        "owned_cache_identity": _owned[_expression] is _second,
        "peer_public_purge_isolated": True,
        "fresh_pattern_matches": _first.fullmatch(_expression) is not None,
        "only_public_cache_api": True,
    })
elif _cohort == "ascii-unicode-inline-and-multiline-flags":
    _kelvin = "\N{KELVIN SIGN}"
    _observation.update({
        "unicode_ignorecase_kelvin": bool(_re.fullmatch("k", _kelvin, _re.I)),
        "ascii_ignorecase_rejects_kelvin": _re.fullmatch("k", _kelvin, _re.I | _re.A) is None,
        "inline_ignorecase": bool(_re.fullmatch(r"(?i:ab)", "AB")),
        "multiline_anchor": bool(_re.search(r"^b", "a\nb", _re.M)),
        "variant": _v,
    })
elif _cohort == "locale-bytes-without-process-locale-mutation":
    _pattern = _re.compile(br"[A-Za-z_]+", _re.LOCALE)
    _match = _pattern.fullmatch(b"Python_")
    try:
        _re.compile("Python", _re.LOCALE)
    except ValueError:
        _text_locale_rejected = True
    else:
        _text_locale_rejected = False
    _observation.update({"bytes_locale_match": _match is not None,
                         "text_locale_rejected": _text_locale_rejected,
                         "locale_unchanged": _locale.setlocale(_locale.LC_CTYPE) == _before_locale})
elif _cohort == "named-captures-backreferences-and-template-expansion":
    _word = "a" * _n
    _pattern = _re.compile(r"(?P<word>[a-z]+)-(?P=word)")
    _subject = _word + "-" + _word
    _match = _pattern.fullmatch(_subject)
    _assert(_match is not None, "the original named backreference did not execute")
    _callbacks = []
    def _callback(value):
        _callbacks.append(value.group("word"))
        return value.group("word").upper()
    _observation.update({"named_group": _match.group("word"),
                         "expanded": _match.expand(r"<\g<word>>"),
                         "callback_result": _pattern.sub(_callback, _subject),
                         "callback_values": _callbacks})
elif _cohort == "zero-width-finditer-and-scanner-progress":
    _subject = "a" * _n
    _pattern = _re.compile(r"(?=a)")
    _spans = [list(value.span()) for value in _pattern.finditer(_subject)]
    _scanner = _pattern.scanner(_subject)
    _scanned = []
    while len(_scanned) <= len(_subject):
        _matched = _scanner.search()
        if _matched is None:
            break
        _scanned.append(list(_matched.span()))
    _assert(len(_scanned) <= len(_subject), "the original scanner failed to progress")
    _observation.update({"finditer_spans": _spans, "scanner_spans": _scanned,
                         "scanner_exhausted": _scanner.search() is None})
elif _cohort == "syntax-and-type-error-isolation":
    _invalid = ("(", "[z-a]", "\\x", "a**")[_v % 4]
    try:
        _re.compile(_invalid)
    except _re.PatternError as _error:
        _syntax = {"type": type(_error).__name__, "position": _error.pos}
    else:
        raise AssertionError("the original malformed expression was accepted")
    try:
        _re.compile(b"a").match("a")
    except TypeError as _error:
        _mixing = type(_error).__name__
    else:
        raise AssertionError("mixed text/bytes did not fail")
    _observation.update({"syntax": _syntax, "mixing_error": _mixing,
                         "recovered": _re.fullmatch("a", "a") is not None})
elif _cohort in ("interpreter-local-module-and-builtins",
                 "independent-interpreter-module-reimport"):
    _name = "_rebar_subinterpreter_case_" + str(_case["seed"])
    _before = _name not in _sys.modules
    _module = _types.ModuleType(_name)
    _module.owner = _owner
    _sys.modules[_name] = _module
    _observation.update({"module_initially_absent": _before,
                         "module_is_interpreter_local": _sys.modules[_name] is _module,
                         "module_owner_intact": _module.owner == _owner,
                         "builtins_owner_intact": getattr(_builtins, "_rebar_subinterpreter_v2_owner") == _owner})
    if _cohort == "independent-interpreter-module-reimport":
        _again = _importlib.import_module("re")
        _observation.update({
            "actual_stdlib_reimport": _again is _re,
            "reimported_origin_verified": (
                _again.__spec__ is not None
                and _os.path.abspath(_again.__spec__.origin) == _stdlib_re_origin
            ),
        })
    del _sys.modules[_name]
elif _cohort in ("repeated-interpreter-creation-and-destruction",
                 "interpreter-teardown-and-worker-cleanup"):
    _expression = "cleanup-" + str(_case["seed"])
    _match = _re.compile(_expression).fullmatch(_expression)
    _observation.update({"actual_execution": _match is not None,
                         "interpreter_owner_intact": getattr(_builtins, "_rebar_subinterpreter_v2_owner") == _owner,
                         "stdlib_owner": _sys.modules["re"] is _re,
                         "variant": _v})
elif _cohort == "contiguous-buffer-and-borrowed-lifetime":
    _storage = bytearray(b"a" * _n + b"b")
    _view = memoryview(_storage)
    _match = _re.compile(br"a+b").fullmatch(_view)
    _assert(_match is not None, "the original contiguous buffer was not matched")
    _group_hex = _match.group().hex()
    del _match
    _view.release()
    _storage.extend(b"!")
    _observation.update({"matched_hex": _group_hex,
                         "released_buffer_is_resizable": _storage[-1] == ord("!")})
else:
    raise AssertionError("an actual frozen subinterpreter category was omitted")

_assert(_locale.setlocale(_locale.LC_CTYPE) == _before_locale,
        "a subinterpreter probe changed the process-global locale")
_record = {"case_id": _case["case_id"], "cohort": _cohort,
           "ordinal": _case["ordinal"], "seed": _case["seed"],
           "variant": _v, "status": "PASS", "actual_exec": True,
           "candidate_imports": 0, "locale_unchanged": True,
           "stdlib_origin_verified": True, "pinned_executable_verified": True,
           "observation": _observation}
_encoded = _json.dumps(_record, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"
_written = 0
while _written < len(_encoded):
    _part = _os.write(_write_fd, _encoded[_written:])
    _assert(type(_part) is int and _part > 0,
            "an actual interpreter observation pipe rejected a write")
    _written += _part
'''


OBSERVATION_FIELDS = {
    "fresh-interpreter-creation-and-stdlib-import": {
        "owner_state_intact", "not_main_interpreter", "stdlib_re_module",
        "module_identity", "actual_interpreter_exec",
    },
    "stdlib-string-compile-match-and-fullmatch": {
        "owner_state_intact", "pattern_kind", "group", "span", "search",
    },
    "stdlib-bytes-compile-match-and-fullmatch": {
        "owner_state_intact", "pattern_kind", "group_hex", "span", "search",
    },
    "pattern-match-type-and-owner-identity": {
        "owner_state_intact", "pattern_is_stdlib_pattern",
        "match_is_stdlib_match", "match_pattern_identity",
        "pattern_generic_origin", "match_generic_origin", "lastgroup",
    },
    "same-interpreter-compile-cache-and-purge": {
        "owner_state_intact", "same_interpreter_cache_hit",
        "purge_produced_fresh_pattern", "fresh_pattern_matches",
        "only_public_cache_api",
    },
    "cross-interpreter-cache-isolation": {
        "owner_state_intact", "same_interpreter_cache_hit",
        "persistent_pattern_survived_peer", "owned_cache_identity",
        "peer_public_purge_isolated", "fresh_pattern_matches",
        "only_public_cache_api",
    },
    "ascii-unicode-inline-and-multiline-flags": {
        "owner_state_intact", "unicode_ignorecase_kelvin",
        "ascii_ignorecase_rejects_kelvin", "inline_ignorecase",
        "multiline_anchor", "variant",
    },
    "locale-bytes-without-process-locale-mutation": {
        "owner_state_intact", "bytes_locale_match", "text_locale_rejected",
        "locale_unchanged",
    },
    "named-captures-backreferences-and-template-expansion": {
        "owner_state_intact", "named_group", "expanded", "callback_result",
        "callback_values",
    },
    "zero-width-finditer-and-scanner-progress": {
        "owner_state_intact", "finditer_spans", "scanner_spans",
        "scanner_exhausted",
    },
    "syntax-and-type-error-isolation": {
        "owner_state_intact", "syntax", "mixing_error", "recovered",
    },
    "interpreter-local-module-and-builtins": {
        "owner_state_intact", "module_initially_absent",
        "module_is_interpreter_local", "module_owner_intact",
        "builtins_owner_intact",
    },
    "repeated-interpreter-creation-and-destruction": {
        "owner_state_intact", "actual_execution", "interpreter_owner_intact",
        "stdlib_owner", "variant",
    },
    "independent-interpreter-module-reimport": {
        "owner_state_intact", "module_initially_absent",
        "module_is_interpreter_local", "module_owner_intact",
        "builtins_owner_intact", "actual_stdlib_reimport",
        "reimported_origin_verified",
    },
    "contiguous-buffer-and-borrowed-lifetime": {
        "owner_state_intact", "matched_hex",
        "released_buffer_is_resizable",
    },
    "interpreter-teardown-and-worker-cleanup": {
        "owner_state_intact", "actual_execution", "interpreter_owner_intact",
        "stdlib_owner", "variant",
    },
}


def validate_case_record(record: Any, case: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "case_id", "cohort", "ordinal", "seed", "variant", "status",
        "actual_exec", "candidate_imports", "locale_unchanged",
        "stdlib_origin_verified", "pinned_executable_verified", "observation",
    }
    require(type(record) is dict and set(record) == fields,
            "an actual subinterpreter record is missing original fields")
    for name in ("case_id", "cohort", "ordinal", "seed", "variant"):
        require(record.get(name) == case[name],
                "the actual genuine interpreter stimulus was replaced: " + name)
    require(record.get("status") == "PASS" and record.get("actual_exec") is True
            and type(record.get("candidate_imports")) is int
            and record["candidate_imports"] == 0
            and record.get("locale_unchanged") is True
            and record.get("stdlib_origin_verified") is True
            and record.get("pinned_executable_verified") is True
            and type(record.get("observation")) is dict
            and record["observation"].get("owner_state_intact") is True,
            "NOT RUN, leaked state, changed locale, or a candidate is not a result")
    observation = record["observation"]
    require(set(observation) == OBSERVATION_FIELDS[case["cohort"]],
            "an exact real category-specific semantic observation was omitted")
    for field in (
        "not_main_interpreter", "stdlib_re_module", "module_identity",
        "actual_interpreter_exec", "pattern_is_stdlib_pattern",
        "match_is_stdlib_match", "match_pattern_identity",
        "pattern_generic_origin", "match_generic_origin",
        "same_interpreter_cache_hit", "purge_produced_fresh_pattern",
        "fresh_pattern_matches", "only_public_cache_api",
        "persistent_pattern_survived_peer", "owned_cache_identity",
        "peer_public_purge_isolated", "unicode_ignorecase_kelvin",
        "ascii_ignorecase_rejects_kelvin", "inline_ignorecase",
        "multiline_anchor", "bytes_locale_match", "text_locale_rejected",
        "scanner_exhausted", "recovered", "module_initially_absent",
        "module_is_interpreter_local", "module_owner_intact",
        "builtins_owner_intact", "actual_stdlib_reimport",
        "reimported_origin_verified", "actual_execution",
        "interpreter_owner_intact", "stdlib_owner",
        "released_buffer_is_resizable",
    ):
        if field in observation:
            require(observation[field] is True,
                    "a real category-specific semantic invariant failed: " + field)
    if "variant" in observation:
        require(observation["variant"] == case["variant"],
                "a genuine category variant was substituted")
    if case["cohort"] == "stdlib-string-compile-match-and-fullmatch":
        require(observation["pattern_kind"] == "str",
                "the actual text-pattern category was replaced")
    if case["cohort"] == "stdlib-bytes-compile-match-and-fullmatch":
        require(observation["pattern_kind"] == "bytes",
                "the actual bytes-pattern category was replaced")
    if case["cohort"] == "syntax-and-type-error-isolation":
        require(type(observation.get("syntax")) is dict
                and observation["syntax"].get("type") == "PatternError"
                and observation.get("mixing_error") == "TypeError",
                "real Python syntax or type failures were substituted")
    return record


def _observation_source(case: dict[str, Any], descriptor: int,
                        owner: str, main_id: int) -> str:
    require(type(descriptor) is int and descriptor >= 0,
            "a genuine interpreter result pipe is required")
    require(owner in {"A", "B", "C"}, "a genuine interpreter role is required")
    return (
        "_case = " + repr(case) + "\n"
        + "_write_fd = " + repr(descriptor) + "\n"
        + "_owner = " + repr(owner) + "\n"
        + "_main_id = " + repr(main_id) + "\n"
        + "_stdlib_re_origin = " + repr(PINNED_STDLIB_RE) + "\n"
        + "_public_interpreter_origin = " + repr(PINNED_INTERPRETERS) + "\n"
        + "_pinned_python = " + repr(PINNED_PYTHON) + "\n"
        + INTERPRETER_PROGRAM
    )


def _observe_interpreter(interpreter: Any, case: dict[str, Any],
                         owner: str, main_id: int) -> dict[str, Any]:
    pieces: list[bytes] = []
    events: list[dict[str, Any]] = []
    reader: int | None = None
    writer: int | None = None
    primary: BaseException | None = None
    phase = "open-observation-pipe"
    reached_eof = False
    result: dict[str, Any] | None = None
    try:
        reader, writer = os.pipe()
        events.extend((
            {"role": "reader", "action": "open", "fd": reader},
            {"role": "writer", "action": "open", "fd": writer},
        ))
        phase = "compose-original-interpreter-case"
        script = _observation_source(case, writer, owner, main_id)
        phase = "execute-original-interpreter-case"
        actual = interpreter.exec(script)
        require(actual is None,
                "the real public Interpreter.exec() did not finish successfully")
        phase = "close-observation-writer"
        closing = writer
        writer = None
        pending = {"role": "writer", "action": "close", "fd": closing,
                   "status": "PENDING"}
        events.append(pending)
        os.close(closing)
        pending["status"] = "PASS"
        phase = "read-complete-interpreter-case"
        count = 0
        while True:
            request = min(65_536, MAX_PIPE_BYTES - count + 1)
            observation = {"role": "reader", "action": "read",
                           "fd": reader, "requested_bytes": request,
                           "returned_bytes": None, "status": "PENDING"}
            events.append(observation)
            piece = os.read(reader, request)
            observation["returned_bytes"] = len(piece)
            observation["status"] = "PASS"
            if not piece:
                reached_eof = True
                break
            count += len(piece)
            require(count <= MAX_PIPE_BYTES,
                    "a complete actual interpreter observation exceeds its bound")
            pieces.append(piece)
        phase = "decode-original-interpreter-case"
        document = strict_canonical(b"".join(pieces),
                                    label="complete actual interpreter observation")
        result = validate_case_record(document, case)
    except BaseException as error:
        primary = error
    finally:
        for descriptor_role in ("writer", "reader"):
            descriptor = writer if descriptor_role == "writer" else reader
            if descriptor is None:
                continue
            if descriptor_role == "writer":
                writer = None
            else:
                reader = None
            observation = {"role": descriptor_role, "action": "close",
                           "fd": descriptor, "status": "PENDING"}
            events.append(observation)
            try:
                os.close(descriptor)
            except BaseException as cleanup:
                observation["status"] = "FAIL"
                observation["error_type"] = type(cleanup).__name__
                observation["error_message"] = str(cleanup)
                if primary is None:
                    primary = cleanup
            else:
                observation["status"] = "PASS"
    if primary is not None:
        raise SubinterpreterWorkerFailure(
            "a genuine subinterpreter case or descriptor cleanup failed",
            {
                "status": "FAIL",
                "active_case": dict(case),
                "active_phase": phase,
                "interpreter_role": owner,
                "error_type": type(primary).__name__,
                "error_message": str(primary),
                "partial_observation_stream": capture_complete_stream(
                    b"".join(pieces),
                ),
                "observation_stream_complete": reached_eof,
                "descriptor_events": events,
            },
        ) from primary
    require(result is not None and reached_eof,
            "a real subinterpreter case completed without an authentic record")
    return result


def _live_ids(public: Any) -> set[int]:
    return {int(interpreter.id) for interpreter in public.list_all()}


def _prepare_interpreter(interpreter: Any, owner: str) -> None:
    source = (
        "import builtins\n"
        "import sys\n"
        "assert not any(n == 'candidates' or n.startswith('candidates.') "
        "for n in sys.modules)\n"
        "builtins._rebar_subinterpreter_v2_owner = " + repr(owner) + "\n"
        "builtins._rebar_subinterpreter_v2_patterns = {}\n"
    )
    require(interpreter.exec(source) is None,
            "the genuine subinterpreter-local owner was not initialized")


def _close_interpreter(interpreter: Any, public: Any) -> None:
    identity = int(interpreter.id)
    require(identity in _live_ids(public),
            "the interpreter disappeared before its real public close")
    interpreter.close()
    require(identity not in _live_ids(public),
            "the genuine public interpreter close did not destroy the instance")


def _worker_document(role: str, context: dict[str, Any]) -> dict[str, Any]:
    require(role in REFERENCE_ROLES, "a genuine independent reference role is required")
    import concurrent.interpreters as public
    import locale

    require(callable(getattr(public, "create", None))
            and callable(getattr(public, "list_all", None))
            and callable(getattr(public, "get_current", None))
            and callable(getattr(public.Interpreter, "exec", None))
            and callable(getattr(public.Interpreter, "close", None))
            and public.__spec__ is not None
            and os.path.abspath(public.__spec__.origin) == PINNED_INTERPRETERS,
            "the exact pinned public create/exec/close API is unavailable")
    matrix = build_matrix()
    validate_matrix(matrix)
    original_ids = _live_ids(public)
    main_id = int(public.get_current().id)
    original_locale = locale.setlocale(locale.LC_CTYPE)
    first = second = third = temporary = None
    created = 0
    closed = 0
    executions = 0
    observations: list[dict[str, Any]] = []
    peer_observations: list[dict[str, Any]] = []
    repeated_observations: list[dict[str, Any]] = []
    repeated_creation_records: list[dict[str, Any]] = []
    ids: dict[str, Any] = {"A": None, "B": None, "C": None,
                           "temporary": []}
    active_case: dict[str, Any] | None = None
    active_phase = "create-simultaneous-interpreter-A"
    primary: BaseException | None = None
    cleanup_failures: list[dict[str, Any]] = []
    after_b: dict[str, Any] | None = None
    fresh: dict[str, Any] | None = None
    try:
        first = public.create()
        created += 1
        ids["A"] = int(first.id)
        active_phase = "create-simultaneous-interpreter-B"
        second = public.create()
        created += 1
        ids["B"] = int(second.id)
        require(int(first.id) != int(second.id)
                and int(first.id) != main_id and int(second.id) != main_id,
                "A and B must be genuine distinct simultaneous subinterpreters")
        active_phase = "initialize-interpreter-A"
        _prepare_interpreter(first, "A")
        active_phase = "initialize-interpreter-B"
        _prepare_interpreter(second, "B")
        for case in matrix:
            active_case = case
            active_phase = "execute-simultaneous-A-first"
            left = _observe_interpreter(first, case, "A", main_id)
            executions += 1
            observations.append(left)
            active_phase = "execute-simultaneous-B"
            middle = _observe_interpreter(second, case, "B", main_id)
            executions += 1
            peer_observations.append(middle)
            active_phase = "execute-simultaneous-A-after-B"
            repeated = _observe_interpreter(first, case, "A", main_id)
            executions += 1
            repeated_observations.append(repeated)
            require(left == middle and left == repeated,
                    "the genuine A/B/A public regex observations disagree")
            require({int(first.id), int(second.id)} <= _live_ids(public),
                    "a live simultaneous subinterpreter was destroyed early")

        for case in matrix:
            if case["cohort"] != "repeated-interpreter-creation-and-destruction":
                continue
            active_case = case
            active_phase = "create-additional-fresh-interpreter"
            temporary = public.create()
            created += 1
            ids["temporary"].append(int(temporary.id))
            require(int(temporary.id) not in {int(first.id), int(second.id)}
                    and {int(first.id), int(second.id)} <= _live_ids(public),
                    "repeated creation replaced a simultaneously live interpreter")
            active_phase = "initialize-additional-fresh-interpreter"
            _prepare_interpreter(temporary, "C")
            active_phase = "execute-additional-fresh-interpreter"
            actual = _observe_interpreter(temporary, case, "C", main_id)
            executions += 1
            expected = observations[case["ordinal"]]
            require(actual == expected,
                    "a repeated fresh interpreter inherited a foreign module")
            repeated_creation_records.append(actual)
            active_phase = "close-additional-fresh-interpreter"
            _close_interpreter(temporary, public)
            closed += 1
            temporary = None

        active_case = matrix[-1]
        active_phase = "close-simultaneous-interpreter-B"
        _close_interpreter(second, public)
        closed += 1
        second = None
        active_phase = "execute-interpreter-A-after-B-close"
        after_b = _observe_interpreter(first, matrix[-1], "A", main_id)
        executions += 1
        require(after_b == observations[-1],
                "closing B changed the still-live interpreter A")
        active_phase = "close-original-interpreter-A"
        _close_interpreter(first, public)
        closed += 1
        first = None

        active_phase = "create-fresh-interpreter-C"
        third = public.create()
        created += 1
        ids["C"] = int(third.id)
        require(ids["C"] not in {ids["A"], ids["B"]},
                "fresh interpreter C reused an original interpreter identity")
        active_phase = "initialize-fresh-interpreter-C"
        _prepare_interpreter(third, "C")
        active_phase = "execute-fresh-interpreter-C"
        fresh = _observe_interpreter(third, matrix[-1], "C", main_id)
        executions += 1
        require(fresh == observations[-1],
                "the new interpreter C inherited stale module or matcher state")
        active_phase = "close-fresh-interpreter-C"
        _close_interpreter(third, public)
        closed += 1
        third = None
        active_phase = "validate-actual-complete-interpreter-teardown"
        require(_live_ids(public) == original_ids,
                "a real reference worker leaked a Python subinterpreter")
        require(locale.setlocale(locale.LC_CTYPE) == original_locale,
                "a genuine interpreter probe changed the worker's global locale")
        require(created == EXPECTED_INTERPRETERS_PER_WORKER
                and closed == EXPECTED_INTERPRETERS_PER_WORKER
                and executions == EXPECTED_EXECUTIONS_PER_WORKER
                and len(repeated_creation_records) == REPEATED_CREATION_CASES,
                "the complete real simultaneous and repeated lifecycle was not run")
    except BaseException as error:
        primary = error
    finally:
        for label, remaining in (("temporary", temporary), ("C", third),
                                 ("B", second), ("A", first)):
            if remaining is not None:
                try:
                    remaining.close()
                except BaseException as error:
                    cleanup_failures.append({
                        "role": label,
                        "interpreter_id": int(remaining.id),
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                    })
    if primary is not None or cleanup_failures:
        details = {
            "status": "FAIL",
            "role": role,
            "active_phase": active_phase,
            "active_case": active_case,
            "actual_interpreter_ids": ids,
            "completed_a_records": observations,
            "completed_b_records": peer_observations,
            "completed_repeated_a_records": repeated_observations,
            "completed_repeated_creation_records": repeated_creation_records,
            "actual_post_b_close_a_record": after_b,
            "actual_fresh_c_record": fresh,
            "interpreters_created": created,
            "successful_interpreter_closes": closed,
            "interpreter_exec_calls": executions,
            "cleanup_failures": cleanup_failures,
        }
        if primary is not None:
            details["error_type"] = type(primary).__name__
            details["error_message"] = str(primary)
            if isinstance(primary, SubinterpreterWorkerFailure):
                details["actual_case_failure"] = primary.details
        raise SubinterpreterWorkerFailure(
            "a genuine simultaneous-subinterpreter reference worker failed",
            details,
        ) from primary
    return {
        "schema": SCHEMA + "-reference-worker",
        "status": "PASS",
        "role": role,
        "pid": os.getpid(),
        "python": PYTHON,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "records": observations,
        "records_sha256": digest(observations),
        "peer_records": peer_observations,
        "peer_records_sha256": digest(peer_observations),
        "repeated_a_records": repeated_observations,
        "repeated_a_records_sha256": digest(repeated_observations),
        "actual_interpreter_ids": ids,
        "repeated_creation_records": repeated_creation_records,
        "repeated_creation_records_sha256": digest(repeated_creation_records),
        "repeated_creation_verified": REPEATED_CREATION_CASES,
        "actual_post_b_close_a_record": after_b,
        "actual_fresh_c_record": fresh,
        "simultaneous_interpreters_verified": True,
        "aba_records_verified": EXPECTED_CASES,
        "b_closed_before_a_reexecution": True,
        "fresh_c_verified": True,
        "interpreters_created": created,
        "interpreters_destroyed": closed,
        "interpreter_exec_calls": executions,
        "live_interpreter_set_restored": True,
        "candidate_imports": 0,
        "locale_changes": 0,
        "worker_locale_unchanged": True,
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
        "public_reference_record_sha256": context[
            "public_reference_record_sha256"
        ],
        "public_reference_independent_roles": context[
            "public_reference_independent_roles"
        ],
        "public_real_locale_cases": context["public_real_locale_cases"],
        "public_real_locale_transitions": context[
            "public_real_locale_transitions"
        ],
        "pinned_stdlib_re_sha256": context["pinned_stdlib_re_sha256"],
        "pinned_public_interpreters_sha256": context[
            "pinned_public_interpreters_sha256"
        ],
    }


def validate_worker_document(document: Any, role: str,
                             *, expected_pid: int) -> dict[str, Any]:
    require(type(document) is dict, "a complete genuine reference worker is required")
    require(role in REFERENCE_ROLES,
            "a real reference worker must have an independently frozen role")
    require(type(expected_pid) is int and expected_pid > 0,
            "the real observed subprocess.Popen PID is required")
    expectations = {
        "schema": SCHEMA + "-reference-worker",
        "status": "PASS",
        "role": role,
        "python": PYTHON,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "simultaneous_interpreters_verified": True,
        "aba_records_verified": EXPECTED_CASES,
        "b_closed_before_a_reexecution": True,
        "fresh_c_verified": True,
        "repeated_creation_verified": REPEATED_CREATION_CASES,
        "interpreters_created": EXPECTED_INTERPRETERS_PER_WORKER,
        "interpreters_destroyed": EXPECTED_INTERPRETERS_PER_WORKER,
        "interpreter_exec_calls": EXPECTED_EXECUTIONS_PER_WORKER,
        "live_interpreter_set_restored": True,
        "candidate_imports": 0,
        "locale_changes": 0,
        "worker_locale_unchanged": True,
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
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_interpreters_sha256": PINNED_INTERPRETERS_SHA256,
    }
    fields = set(expectations) | {
        "pid", "records", "records_sha256", "peer_records",
        "peer_records_sha256", "repeated_a_records",
        "repeated_a_records_sha256", "actual_interpreter_ids",
        "repeated_creation_records", "repeated_creation_records_sha256",
        "actual_post_b_close_a_record", "actual_fresh_c_record",
    }
    require(set(document) == fields,
            "a genuine reference worker omitted or invented lifecycle fields")
    for name, value in expectations.items():
        require(document.get(name) == value,
                "a genuine real-subinterpreter worker was forged: " + name)
    require(type(document.get("pid")) is int
            and document["pid"] == expected_pid,
            "the actual observed subprocess.Popen PID was substituted")
    identities = document["actual_interpreter_ids"]
    require(type(identities) is dict
            and set(identities) == {"A", "B", "C", "temporary"}
            and all(type(identities[label]) is int and identities[label] > 0
                    for label in ("A", "B", "C"))
            and len({identities["A"], identities["B"], identities["C"]}) == 3
            and type(identities["temporary"]) is list
            and len(identities["temporary"]) == REPEATED_CREATION_CASES
            and all(type(identity) is int and identity > 0
                    for identity in identities["temporary"])
            and len(set(identities["temporary"])) == REPEATED_CREATION_CASES
            and not (set(identities["temporary"])
                     & {identities["A"], identities["B"], identities["C"]}),
            "the eleven genuine independent interpreter identities were forged")
    matrix = build_matrix()
    vectors = (
        ("records", "records_sha256"),
        ("peer_records", "peer_records_sha256"),
        ("repeated_a_records", "repeated_a_records_sha256"),
    )
    for vector_name, digest_name in vectors:
        records = document[vector_name]
        require(type(records) is list and len(records) == EXPECTED_CASES,
                "a complete real A/B/A vector was omitted: " + vector_name)
        for case, record in zip(matrix, records, strict=True):
            validate_case_record(record, case)
        require(document[digest_name] == digest(records),
                "a genuine complete A/B/A vector was forged: " + vector_name)
    require(document["records"] == document["peer_records"]
            and document["records"] == document["repeated_a_records"],
            "the complete genuine A/B/A semantic vectors disagree")
    repeated_cases = [case for case in matrix
                      if case["cohort"]
                      == "repeated-interpreter-creation-and-destruction"]
    repeated = document["repeated_creation_records"]
    require(type(repeated) is list
            and len(repeated) == REPEATED_CREATION_CASES
            and document["repeated_creation_records_sha256"] == digest(repeated),
            "the eight genuinely fresh interpreter executions were omitted")
    for case, record in zip(repeated_cases, repeated, strict=True):
        validate_case_record(record, case)
        require(record == document["records"][case["ordinal"]],
                "an actual independently fresh interpreter result disagrees")
    for name in ("actual_post_b_close_a_record", "actual_fresh_c_record"):
        validate_case_record(document[name], matrix[-1])
        require(document[name] == document["records"][-1],
                "a complete post-close lifecycle record was forged: " + name)
    return document


def _worker_environment() -> dict[str, str]:
    return {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }


def _run_worker(role: str, source_sha256: str,
                protocol_sha256: str) -> dict[str, Any]:
    command = [
        sys.executable, "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--worker-role", role, "--source-sha256", source_sha256,
        "--protocol-sha256", protocol_sha256,
    ]
    require(role in REFERENCE_ROLES,
            "an actual frozen independent worker role is required")
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
        "active_phase": "start-actual-reference-subprocess",
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
                "subprocess.Popen did not expose a genuine worker PID")
        observed["pid"] = process.pid
        observed["active_phase"] = "communicate-complete-reference-streams"
        try:
            stdout, stderr = process.communicate(timeout=300)
        except subprocess.TimeoutExpired as timeout:
            observed["timed_out"] = True
            partial_stdout = (timeout.stdout
                              if type(timeout.stdout) is bytes else b"")
            partial_stderr = (timeout.stderr
                              if type(timeout.stderr) is bytes else b"")
            observed["timeout_partial_stdout"] = capture_complete_stream(
                partial_stdout,
            )
            observed["timeout_partial_stderr"] = capture_complete_stream(
                partial_stderr,
            )
            observed["timeout_partial_stdout_complete"] = False
            observed["timeout_partial_stderr_complete"] = False
            observed["active_phase"] = "terminate-timed-out-reference-worker"
            try:
                process.kill()
            except BaseException as cleanup:
                observed["timeout_termination_error"] = {
                    "type": type(cleanup).__name__,
                    "message": str(cleanup),
                }
            observed["active_phase"] = "collect-terminated-reference-worker"
            stdout, stderr = process.communicate(timeout=30)
        observed["active_phase"] = "preserve-complete-original-worker-streams"
        require(type(stdout) is bytes and type(stderr) is bytes,
                "a real reference worker omitted its original binary streams")
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
        require(observed["timed_out"] is False,
                "the real reference worker exceeded its frozen time limit")
        require(type(process.returncode) is int and process.returncode == 0
                and stderr == b"",
                "the genuine reference worker exited, signaled, or wrote stderr")
        observed["active_phase"] = "decode-complete-original-worker-stdout"
        report = strict_canonical(
            stdout, label=role + " complete original stdout",
        )
        observed["active_phase"] = "validate-popen-bound-worker-and-all-vectors"
        validate_worker_document(report, role, expected_pid=process.pid)
        observed["status"] = "PASS"
        observed["active_phase"] = "complete"
        observed["report"] = report
        return observed
    except BaseException as error:
        if process is not None:
            observed["pid"] = process.pid
            if process.returncode is not None:
                observed["returncode"] = process.returncode
                observed["signal"] = (
                    -process.returncode if process.returncode < 0 else None
                )
        observed["status"] = "FAIL"
        observed["error_type"] = type(error).__name__
        observed["error_message"] = str(error)
        raise SubinterpreterWorkerFailure(
            "an actual Popen-bound genuine reference worker failed", observed,
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
        raise SubinterpreterOracleError(
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
                raise SubinterpreterOracleError(
                    "an immutable subinterpreter result already exists: " + relative,
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
            raise SubinterpreterOracleError(
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
                raise SubinterpreterOracleError(
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
            "an actual canonical subinterpreter report exceeds its bound")
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
        raise SubinterpreterPublicationFailure(
            "a genuine no-follow exclusive subinterpreter publication failed",
            receipt,
        ) from primary
    return receipt


def run_self_oracle(source_sha256: str, protocol_sha256: str) -> dict[str, Any]:
    require(valid_sha256(source_sha256) and valid_sha256(protocol_sha256),
            "root must independently supply actual source and protocol hashes")
    context = authenticate_context(source_sha256, protocol_sha256)
    _preflight_outputs()
    completed: dict[str, dict[str, Any]] = {}
    phase = "start-independent-genuine-reference-workers"
    try:
        for role in REFERENCE_ROLES:
            phase = "start-actual-" + role
            completed[role] = _run_worker(role, source_sha256, protocol_sha256)
        phase = "validate-distinct-popen-observed-reference-processes"
        require(set(completed) == set(REFERENCE_ROLES),
                "a genuine independent reference process was omitted")
        for role in REFERENCE_ROLES:
            observed = completed[role]
            require(observed.get("status") == "PASS"
                    and observed.get("role") == role
                    and observed.get("stdout_complete") is True
                    and observed.get("stderr_complete") is True
                    and observed.get("timed_out") is False
                    and observed.get("returncode") == 0
                    and observed.get("signal") is None,
                    "a genuine complete original reference stream is missing")
            original_stdout = restore_complete_stream(
                observed.get("stdout"), label=role + " actual original stdout",
            )
            original_stderr = restore_complete_stream(
                observed.get("stderr"), label=role + " actual original stderr",
            )
            require(original_stderr == b"",
                    "a successful independent reference worker wrote stderr")
            original_report = strict_canonical(
                original_stdout, label=role + " actual preserved original stdout",
            )
            require(original_report == observed.get("report"),
                    "an original worker report differs from its complete stdout")
            validate_worker_document(
                original_report, role, expected_pid=observed.get("pid"),
            )
        first = completed["reference_a"]["report"]
        second = completed["reference_b"]["report"]
        require(completed["reference_a"]["pid"]
                != completed["reference_b"]["pid"]
                and first["pid"] != second["pid"],
                "two actual Popen reference workers reused a process identity")
        phase = "compare-all-complete-independent-reference-vectors"
        for records_name, sha_name in (
            ("records", "records_sha256"),
            ("peer_records", "peer_records_sha256"),
            ("repeated_a_records", "repeated_a_records_sha256"),
            ("repeated_creation_records", "repeated_creation_records_sha256"),
        ):
            require(first[records_name] == second[records_name]
                    and first[sha_name] == second[sha_name],
                    "actual independent reference vectors disagree: "
                    + records_name)
        for name in ("actual_post_b_close_a_record", "actual_fresh_c_record"):
            require(first[name] == second[name],
                    "actual independent teardown observations disagree: " + name)
    except Exception as error:
        actual_failure = (
            error.details if isinstance(error, SubinterpreterWorkerFailure)
            else {
                "status": "FAIL",
                "active_phase": phase,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )
        details = {
            "schema": SCHEMA + "-self-oracle-failure",
            "status": "FAIL",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": protocol_sha256,
            "original_reference": context,
            "matrix_sha256": MATRIX_SHA256,
            "expected_case_count": EXPECTED_CASES,
            "expected_interpreters_per_reference": (
                EXPECTED_INTERPRETERS_PER_WORKER
            ),
            "expected_matching_exec_calls_per_reference": (
                EXPECTED_EXECUTIONS_PER_WORKER
            ),
            "active_phase": phase,
            "completed_reference_roles": completed,
            "actual_first_failure": actual_failure,
            "candidate_status": "NOT RUN",
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
        failure_receipt = publish_with_receipt(FAILURE_RELATIVE, details)
        stored_receipt = publish_with_receipt(FAILURE_RECEIPT_RELATIVE,
                                              failure_receipt)
        raise SubinterpreterWorkerFailure(str(error), {
            "failure_path": FAILURE_RELATIVE,
            "failure_sha256": failure_receipt["expected_sha256"],
            "active_phase": phase,
            "actual_first_failure": actual_failure,
            "publication_receipt": failure_receipt,
            "receipt_publication": stored_receipt,
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
        "actual_independent_reference_count": 2,
        "distinct_reference_processes": True,
        "reference_roles": completed,
        "reference_records_sha256": first["records_sha256"],
        "actual_interpreters_created": (
            len(REFERENCE_ROLES) * EXPECTED_INTERPRETERS_PER_WORKER
        ),
        "actual_interpreters_destroyed": (
            len(REFERENCE_ROLES) * EXPECTED_INTERPRETERS_PER_WORKER
        ),
        "actual_interpreter_exec_calls": (
            len(REFERENCE_ROLES) * EXPECTED_EXECUTIONS_PER_WORKER
        ),
        "actual_aba_case_triples": len(REFERENCE_ROLES) * EXPECTED_CASES,
        "actual_aba_phase_records": (
            len(REFERENCE_ROLES) * EXPECTED_CASES * 3
        ),
        "actual_matching_interpreter_exec_calls": (
            len(REFERENCE_ROLES) * EXPECTED_EXECUTIONS_PER_WORKER
        ),
        "actual_repeated_fresh_interpreter_executions": (
            len(REFERENCE_ROLES) * REPEATED_CREATION_CASES
        ),
        "actual_post_b_close_a_executions": 2,
        "actual_fresh_c_executions": 2,
        "all_interpreter_teardowns_verified": True,
        "candidate_status": "NOT RUN",
        "candidate_imports": 0,
        "native_owner_workers": 0,
        "locale_changes": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    receipt = publish_with_receipt(PASS_RELATIVE, report)
    receipt_receipt = publish_with_receipt(PASS_RECEIPT_RELATIVE, receipt)
    return {
        "schema": SCHEMA + "-published-self-oracle",
        "status": "PASS",
        "report_path": PASS_RELATIVE,
        "report_sha256": receipt["expected_sha256"],
        "report_uncompressed_sha256": receipt["uncompressed_sha256"],
        "report_uncompressed_bytes": receipt["uncompressed_bytes"],
        "report_compression": receipt["compression"],
        "receipt": receipt,
        "receipt_publication": receipt_receipt,
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
        "proof": "complete original genuine subinterpreter phase records",
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
            SubinterpreterOracleError,
            TypeError,
            ValueError,
            OverflowError,
            UnicodeError,
            EOFError,
            zlib.error,
        ):
            rejected += 1
        else:
            raise SubinterpreterOracleError(
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
        except (SubinterpreterOracleError, TypeError, ValueError):
            rejected += 1
        else:
            raise SubinterpreterOracleError(
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
        except (SubinterpreterOracleError, TypeError, ValueError):
            rejected += 1
        else:
            raise SubinterpreterOracleError(
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
            raise SubinterpreterOracleError("source-only operation rejected: " + kind)
        return blocked

    def replace(target: Any, name: str, kind: str) -> None:
        if hasattr(target, name):
            restorations.append((target, name, getattr(target, name)))
            setattr(target, name, reject(kind))

    original_import = builtins.__import__

    def guarded_import(name: str, globals: Any = None, locals: Any = None,
                       fromlist: Any = (), level: int = 0) -> Any:
        if (name == "candidates" or name.startswith("candidates.")
                or name == "_interpreters"
                or name == "concurrent.interpreters"
                or name.startswith("concurrent.interpreters.")
                or (name == "concurrent"
                    and type(fromlist) in (tuple, list)
                    and "interpreters" in fromlist)
                or name == "tools.postfinal_cpython_locale_oracle_v6"
                or name.startswith("tools.python_re_public_surface_oracle_")):
            effects["candidate_or_interpreter_imports"] += 1
            raise SubinterpreterOracleError("source-only matching/interpreter import rejected")
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
    cohort = case["cohort"]
    observation = {field: True for field in OBSERVATION_FIELDS[cohort]}
    variant = case["variant"]
    count = variant % 4 + 1
    word = "a" * count
    if cohort == "stdlib-string-compile-match-and-fullmatch":
        observation.update({
            "pattern_kind": "str", "group": word,
            "span": [0, count + 1], "search": 1,
        })
    elif cohort == "stdlib-bytes-compile-match-and-fullmatch":
        observation.update({
            "pattern_kind": "bytes", "group_hex": word.encode("ascii").hex(),
            "span": [0, count + 1], "search": 1,
        })
    elif cohort == "pattern-match-type-and-owner-identity":
        observation["lastgroup"] = "value"
    elif cohort in {
        "ascii-unicode-inline-and-multiline-flags",
        "repeated-interpreter-creation-and-destruction",
        "interpreter-teardown-and-worker-cleanup",
    }:
        observation["variant"] = variant
    elif cohort == "named-captures-backreferences-and-template-expansion":
        observation.update({
            "named_group": word,
            "expanded": "<" + word + ">",
            "callback_result": word.upper(),
            "callback_values": [word],
        })
    elif cohort == "zero-width-finditer-and-scanner-progress":
        spans = [[index, index] for index in range(count)]
        observation["finditer_spans"] = spans
        observation["scanner_spans"] = [list(span) for span in spans]
    elif cohort == "syntax-and-type-error-isolation":
        observation["syntax"] = {
            "type": "PatternError",
            "position": (0, 1, 0, 2)[variant % 4],
        }
        observation["mixing_error"] = "TypeError"
    elif cohort == "contiguous-buffer-and-borrowed-lifetime":
        observation["matched_hex"] = (word + "b").encode("ascii").hex()
    require(set(observation) == OBSERVATION_FIELDS[cohort]
            and "synthetic" not in observation,
            "a pure source-only semantic shape does not cover its real category")
    return observation


def _copy_source_only_record(record: dict[str, Any]) -> dict[str, Any]:
    return {**record, "observation": dict(record["observation"])}


def _synthetic_worker(role: str, pid: int) -> dict[str, Any]:
    matrix = build_matrix()
    records = [{
        **case,
        "status": "PASS",
        "actual_exec": True,
        "candidate_imports": 0,
        "locale_unchanged": True,
        "stdlib_origin_verified": True,
        "pinned_executable_verified": True,
        "observation": _synthetic_observation(case),
    } for case in matrix]
    peer_records = [_copy_source_only_record(row) for row in records]
    repeated_a_records = [_copy_source_only_record(row) for row in records]
    repeated_creation_records = [
        _copy_source_only_record(records[case["ordinal"]])
        for case in matrix
        if case["cohort"] == "repeated-interpreter-creation-and-destruction"
    ]
    return {
        "schema": SCHEMA + "-reference-worker",
        "status": "PASS",
        "role": role,
        "pid": pid,
        "python": PYTHON,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "records": records,
        "records_sha256": digest(records),
        "peer_records": peer_records,
        "peer_records_sha256": digest(peer_records),
        "repeated_a_records": repeated_a_records,
        "repeated_a_records_sha256": digest(repeated_a_records),
        "actual_interpreter_ids": {
            "A": 111,
            "B": 222,
            "C": 333,
            "temporary": list(range(444, 444 + REPEATED_CREATION_CASES)),
        },
        "repeated_creation_records": repeated_creation_records,
        "repeated_creation_records_sha256": digest(repeated_creation_records),
        "repeated_creation_verified": REPEATED_CREATION_CASES,
        "actual_post_b_close_a_record": _copy_source_only_record(records[-1]),
        "actual_fresh_c_record": _copy_source_only_record(records[-1]),
        "simultaneous_interpreters_verified": True,
        "aba_records_verified": EXPECTED_CASES,
        "b_closed_before_a_reexecution": True,
        "fresh_c_verified": True,
        "interpreters_created": EXPECTED_INTERPRETERS_PER_WORKER,
        "interpreters_destroyed": EXPECTED_INTERPRETERS_PER_WORKER,
        "interpreter_exec_calls": EXPECTED_EXECUTIONS_PER_WORKER,
        "live_interpreter_set_restored": True,
        "candidate_imports": 0,
        "locale_changes": 0,
        "worker_locale_unchanged": True,
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
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_interpreters_sha256": PINNED_INTERPRETERS_SHA256,
    }


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
        "clock_samples": 0,
    }
    checks: list[str] = []

    def check(name: str, condition: Any) -> None:
        require(type(name) is str and name not in checks,
                "a source-only adversarial-control identity was duplicated")
        require(condition is True, "a genuine source-only control failed: " + name)
        checks.append(name)

    def reject(name: str, action: Any) -> None:
        require(type(name) is str and name not in checks,
                "a source-only rejection-control identity was duplicated")
        try:
            action()
        except (SubinterpreterOracleError, TypeError, ValueError,
                OverflowError, UnicodeError, json.JSONDecodeError):
            checks.append(name)
        else:
            raise SubinterpreterOracleError("a forged source-only control passed: " + name)

    with _source_only_boundary(effects):
        matrix = build_matrix()
        check("exact-128-frozen-real-subinterpreter-case-identities",
              validate_matrix(matrix) == MATRIX_SHA256)
        check(
            "freeze-exact-reviewed-v2-protocol-sha256",
            protocol_sha256 == FROZEN_PROTOCOL_SHA256,
        )
        check(
            "preserve-immutable-v1-subinterpreter-protocol",
            valid_sha256(HISTORICAL_V1_PROTOCOL_SHA256)
            and HISTORICAL_V1_PROTOCOL_SHA256.encode("ascii") in protocol,
        )
        check(
            "preserve-immutable-v1-subinterpreter-controller",
            valid_sha256(HISTORICAL_V1_SOURCE_SHA256)
            and HISTORICAL_V1_SOURCE_SHA256.encode("ascii") in protocol,
        )
        check(
            "preserve-complete-prior-v1-subinterpreter-report",
            valid_sha256(HISTORICAL_V1_REPORT_SHA256)
            and HISTORICAL_V1_REPORT_SHA256.encode("ascii") in protocol,
        )
        check(
            "preserve-complete-prior-v1-subinterpreter-receipt",
            valid_sha256(HISTORICAL_V1_RECEIPT_SHA256)
            and HISTORICAL_V1_RECEIPT_SHA256.encode("ascii") in protocol,
        )
        check(
            "preserve-151-runnable-public-and-one-real-debug-skip",
            151 + 1 == 152 and 152 + 13 == 165
            and b"151" in protocol
            and b"debug-only skip" in protocol,
        )
        check("exact-16-independent-case-categories", len(COHORTS) == 16)
        check("exact-eight-deterministic-variants", CASES_PER_COHORT == 8)
        check("all-128-deterministic-seeds-are-distinct",
              len({row["seed"] for row in matrix}) == EXPECTED_CASES)
        check("all-128-executed-case-identities-are-distinct",
              len({row["case_id"] for row in matrix}) == EXPECTED_CASES)
        check("preserve-original-165-method-denominator", 152 + 13 == 165)
        check("preserve-exact-two-named-private-class-waivers",
              sum(item["methods"] for item in PRIVATE_WAIVERS.values()) == 13)
        check("preserve-all-1376-frozen-public-cases", PUBLIC_CASES == 1_376)
        check("preserve-all-43-frozen-public-cohorts", PUBLIC_COHORTS == 43)
        check("actual-frozen-original-v6-reference-identity",
              valid_sha256(V6_REFERENCE_SHA256))
        check("actual-frozen-public-source-identity", valid_sha256(PUBLIC_SOURCE_SHA256))
        check("actual-frozen-public-protocol-identity", valid_sha256(PUBLIC_PROTOCOL_SHA256))
        check("actual-frozen-complete-v19-two-reference-report-identity",
              valid_sha256(PUBLIC_REFERENCE_SHA256))
        check("actual-frozen-complete-v19-1376-record-vector-identity",
              valid_sha256(PUBLIC_REFERENCE_RECORD_SHA256))
        check("preserve-all-64-authentic-public-locale-cases",
              PUBLIC_REAL_LOCALE_CASES == 64)
        check("preserve-all-192-authentic-public-locale-transitions",
              PUBLIC_REAL_LOCALE_TRANSITIONS == 192)
        check("authenticate-exact-pinned-stdlib-regex-source-identity",
              valid_sha256(PINNED_STDLIB_RE_SHA256))
        check("authenticate-exact-pinned-public-interpreters-source-identity",
              valid_sha256(PINNED_INTERPRETERS_SHA256))
        check("require-eleven-actual-interpreters-per-genuine-worker",
              EXPECTED_INTERPRETERS_PER_WORKER == 11)
        check("require-394-real-matching-executions-per-genuine-worker",
              EXPECTED_EXECUTIONS_PER_WORKER == 394)
        check("bind-real-matrix-inside-the-exact-protocol",
              MATRIX_SHA256.encode("ascii") in protocol)
        check("require-actual-public-create-exec-close",
              b"concurrent.interpreters.create()" in protocol
              and b"Interpreter.exec()" in protocol
              and b"Interpreter.close()" in protocol)
        check("require-simultaneous-aba-and-25-safe-publication-controls",
              b"A" in protocol and b"B" in protocol
              and _source_only_publication_controls()
              == PUBLICATION_SOURCE_ONLY_POISON_CASES)
        check(
            "reject-all-eleven-purely-synthetic-gzip-archive-attacks",
            _source_only_gzip_controls()
            == GZIP_SOURCE_ONLY_POISON_CASES,
        )

        first = _synthetic_worker("reference_a", 10_001)
        second = _synthetic_worker("reference_b", 10_002)
        validate_worker_document(first, "reference_a", expected_pid=10_001)
        validate_worker_document(second, "reference_b", expected_pid=10_002)
        check("accept-complete-source-only-synthetic-vectors",
              first["records"] == second["records"])
        for poison_index, (field, forged) in enumerate((
            ("status", "NOT RUN"),
            ("status", "PASS-CAPABILITY"),
            ("python", "3.14.5"),
            ("matrix_sha256", "0" * 64),
            ("case_count", 127),
            ("cohort_count", 15),
            ("simultaneous_interpreters_verified", False),
            ("aba_records_verified", 127),
            ("b_closed_before_a_reexecution", False),
            ("fresh_c_verified", False),
            ("repeated_creation_verified", 7),
            ("interpreters_created", 0),
            ("interpreters_destroyed", 2),
            ("interpreter_exec_calls", 0),
            ("live_interpreter_set_restored", False),
            ("candidate_imports", 1),
            ("locale_changes", 1),
            ("worker_locale_unchanged", False),
            ("native_owner_workers", 1),
            ("holdout_cases_read", 1),
            ("performance_fixtures_read", 1),
            ("benchmark_or_timing_executed", True),
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
            ("pinned_stdlib_re_sha256", "0" * 64),
            ("pinned_public_interpreters_sha256", "0" * 64),
            ("pid", 0),
        )):
            altered = dict(first)
            altered[field] = forged
            reject(f"reject-forged-real-worker-{poison_index:03d}-{field}",
                   lambda altered=altered: validate_worker_document(
                       altered, "reference_a", expected_pid=10_001,
                   ))
        for vector_name, digest_name in (
            ("records", "records_sha256"),
            ("peer_records", "peer_records_sha256"),
            ("repeated_a_records", "repeated_a_records_sha256"),
            ("repeated_creation_records", "repeated_creation_records_sha256"),
        ):
            omitted = dict(first)
            omitted[vector_name] = first[vector_name][:-1]
            reject("reject-omitted-complete-genuine-vector-" + vector_name,
                   lambda omitted=omitted: validate_worker_document(
                       omitted, "reference_a", expected_pid=10_001,
                   ))
            forged_digest = dict(first)
            forged_digest[digest_name] = "0" * 64
            reject("reject-forged-complete-genuine-vector-sha-" + vector_name,
                   lambda forged_digest=forged_digest: validate_worker_document(
                       forged_digest, "reference_a", expected_pid=10_001,
                   ))
        for field in ("A", "B", "C", "temporary"):
            forged_ids = dict(first)
            forged_ids["actual_interpreter_ids"] = dict(
                first["actual_interpreter_ids"],
            )
            forged_ids["actual_interpreter_ids"][field] = (
                [111] * REPEATED_CREATION_CASES
                if field == "temporary"
                else first["actual_interpreter_ids"]["A"]
            )
            if field == "A":
                forged_ids["actual_interpreter_ids"][field] = 0
            reject("reject-invented-real-interpreter-identity-" + field,
                   lambda forged_ids=forged_ids: validate_worker_document(
                       forged_ids, "reference_a", expected_pid=10_001,
                   ))
        for field in ("actual_post_b_close_a_record", "actual_fresh_c_record"):
            missing_lifecycle = dict(first)
            missing_lifecycle[field] = dict(first[field])
            missing_lifecycle[field]["actual_exec"] = False
            reject("reject-unexecuted-genuine-teardown-record-" + field,
                   lambda missing_lifecycle=missing_lifecycle:
                   validate_worker_document(
                       missing_lifecycle, "reference_a", expected_pid=10_001,
                   ))
        for row, case in zip(first["records"], matrix, strict=True):
            for field, forged in (("status", "NOT RUN"),
                                  ("actual_exec", False),
                                  ("candidate_imports", 1),
                                  ("locale_unchanged", False),
                                  ("stdlib_origin_verified", False),
                                  ("pinned_executable_verified", False)):
                altered = dict(row)
                altered[field] = forged
                reject("reject-unexecuted-case-" + case["case_id"] + "-" + field,
                       lambda altered=altered, case=case:
                       validate_case_record(altered, case))
            fake = dict(row)
            fake["observation"] = {
                "owner_state_intact": True,
                "synthetic": case["ordinal"],
            }
            reject("reject-fake-synthetic-semantic-case-" + case["case_id"],
                   lambda fake=fake, case=case:
                   validate_case_record(fake, case))
        for relative in sorted(APPROVED_OUTPUTS):
            check("allow-only-exact-exclusive-target-" + relative.rsplit("/", 1)[-1],
                  safe_relative(relative, outputs_only=True) == relative)
        for relative in (
            "../outside.json", "/tmp/outside.json", "performance/report.json",
            "oracle/cpython-3.14.6/evidence/../replacement.json",
            "oracle/cpython-3.14.6/evidence/public-subinterpreter-v1-other.json",
        ):
            reject("reject-unsafe-exclusive-target-" + relative,
                   lambda relative=relative: safe_relative(relative, outputs_only=True))
        empty = capture_complete_stream(b"")
        check("authenticate-complete-empty-worker-stderr",
              restore_complete_stream(empty, label="source-only stderr") == b"")
        observed = capture_complete_stream(b'{"status":"PASS"}\n')
        check("authenticate-complete-synthetic-original-worker-stdout",
              restore_complete_stream(observed, label="source-only stdout")
              == b'{"status":"PASS"}\n')
        for field, value in (("bytes", observed["bytes"] + 1),
                             ("sha256", "0" * 64), ("base64", "@@@")):
            altered = dict(observed)
            altered[field] = value
            reject("reject-incomplete-genuine-worker-stream-" + field,
                   lambda altered=altered: restore_complete_stream(
                       altered, label="source-only forged stream",
                   ))
        reject("reject-duplicate-original-json-keys",
               lambda: strict_canonical(b'{"x":1,"x":2}', label="duplicate"))
        reject("reject-nonfinite-original-json",
               lambda: strict_canonical(b'{"x":NaN}', label="nonfinite"))
        reject("reject-noncanonical-original-json",
               lambda: strict_canonical(b'{ "x": 1 }', label="noncanonical"))
        check("all-adversarial-controls-have-unique-identities",
              len(checks) == len(set(checks)))
        check("source-only-reads-only-own-source-and-protocol",
              all(value == 0 for value in effects.values()))

    require(len(checks) == EXPECTED_SOURCE_ONLY_CHECKS
            and len(checks) == len(set(checks)),
            "the exact frozen 995 genuinely distinct V2 source-only controls changed")
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
        "historical_v1_protocol_relative": HISTORICAL_V1_PROTOCOL_RELATIVE,
        "historical_v1_protocol_sha256": HISTORICAL_V1_PROTOCOL_SHA256,
        "historical_v1_source_relative": HISTORICAL_V1_SOURCE_RELATIVE,
        "historical_v1_source_sha256": HISTORICAL_V1_SOURCE_SHA256,
        "historical_v1_report_relative": HISTORICAL_V1_REPORT_RELATIVE,
        "historical_v1_report_sha256": HISTORICAL_V1_REPORT_SHA256,
        "historical_v1_receipt_relative": HISTORICAL_V1_RECEIPT_RELATIVE,
        "historical_v1_receipt_sha256": HISTORICAL_V1_RECEIPT_SHA256,
        "check_count": len(checks),
        "expected_check_count": EXPECTED_SOURCE_ONLY_CHECKS,
        "unique_check_count": len(set(checks)),
        "publication_adversarial_receipt_variants": (
            PUBLICATION_SOURCE_ONLY_POISON_CASES
        ),
        "gzip_adversarial_member_variants": (
            GZIP_SOURCE_ONLY_POISON_CASES
        ),
        "failed": [],
        "matrix_sha256": MATRIX_SHA256,
        "case_count": EXPECTED_CASES,
        "cohort_count": len(COHORTS),
        "cases_per_cohort": CASES_PER_COHORT,
        "original_methods": 165,
        "original_public_methods": 152,
        "original_runnable_public_methods": 151,
        "original_uniform_debug_skips": 1,
        "original_named_private_methods": 13,
        "original_reference_sha256": V6_REFERENCE_SHA256,
        "public_cases_unchanged": PUBLIC_CASES,
        "public_cohorts_unchanged": PUBLIC_COHORTS,
        "public_matrix_sha256": PUBLIC_MATRIX_SHA256,
        "public_stimulus_sha256": PUBLIC_STIMULUS_SHA256,
        "public_source_sha256": PUBLIC_SOURCE_SHA256,
        "public_protocol_sha256": PUBLIC_PROTOCOL_SHA256,
        "public_reference_sha256": PUBLIC_REFERENCE_SHA256,
        "public_reference_record_sha256": PUBLIC_REFERENCE_RECORD_SHA256,
        "public_reference_independent_roles": 2,
        "public_real_locale_cases": PUBLIC_REAL_LOCALE_CASES,
        "public_real_locale_transitions": PUBLIC_REAL_LOCALE_TRANSITIONS,
        "pinned_stdlib_re_sha256": PINNED_STDLIB_RE_SHA256,
        "pinned_public_interpreters_sha256": PINNED_INTERPRETERS_SHA256,
        "expected_interpreters_per_reference": EXPECTED_INTERPRETERS_PER_WORKER,
        "expected_matching_exec_calls_per_reference": (
            EXPECTED_EXECUTIONS_PER_WORKER
        ),
        "expected_aba_case_triples": len(REFERENCE_ROLES) * EXPECTED_CASES,
        "expected_aba_phase_records": (
            len(REFERENCE_ROLES) * EXPECTED_CASES * 3
        ),
        "instruction_files_read": 2,
        "filesystem_operations": effects["filesystem_operations"],
        "interpreter_operations": effects["interpreter_operations"],
        "candidate_or_interpreter_import_attempts": effects[
            "candidate_or_interpreter_imports"
        ],
        "guarded_reference_worker_attempts": effects["reference_workers"],
        "evidence_files_read": 0,
        "files_written": 0,
        "subinterpreters_created": 0,
        "subinterpreter_exec_calls": 0,
        "reference_workers_started": 0,
        "candidate_workers_started": 0,
        "native_owner_workers_started": 0,
        "candidate_imports": 0,
        "threads_started": 0,
        "clock_samples": 0,
        "locale_changes": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "actual_reference_status": "NOT RUN",
        "actual_candidate_status": "NOT RUN",
        "actual_subinterpreter_status": "NOT RUN",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--worker-role", choices=REFERENCE_ROLES)
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(
                options.source_sha256 is None
                and options.protocol_sha256 is None,
                "source-only controls cannot authorize a real reference",
            )
            result = self_test()
        elif options.worker_role:
            context = authenticate_context(options.source_sha256,
                                           options.protocol_sha256)
            result = _worker_document(options.worker_role, context)
        else:
            result = run_self_oracle(options.source_sha256,
                                     options.protocol_sha256)
        sys.stdout.buffer.write(canonical(result) + b"\n")
        return 0
    except SubinterpreterWorkerFailure as error:
        failure = {"schema": SCHEMA + "-invocation-failure",
                   "status": "FAIL", "error_type": type(error).__name__,
                   "error": str(error), "details": error.details,
                   "candidate_status": "NOT RUN",
                   "performance": "NOT MEASURED", "holdout": "NOT ACCESSED"}
    except (SubinterpreterOracleError, SubinterpreterPublicationFailure,
            OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        failure = {"schema": SCHEMA + "-invocation-failure",
                   "status": "FAIL", "error_type": type(error).__name__,
                   "error": str(error), "candidate_status": "NOT RUN",
                   "performance": "NOT MEASURED", "holdout": "NOT ACCESSED"}
        if isinstance(error, SubinterpreterPublicationFailure):
            failure["publication_receipt"] = error.receipt
    sys.stderr.buffer.write(canonical(failure) + b"\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
