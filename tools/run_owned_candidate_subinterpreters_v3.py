#!/usr/bin/env python3
"""Run the unchanged 128-case interpreter oracle with genuine native owners.

The version-one observer and its original Python reference remain immutable.
Version three fixes the actually recorded 256-MiB/128-MiB guard-limit failure
by giving the original guard the authenticated exact byte size of every source
and native file. It independently authenticates the published, crash-safe
version-two activator and explicitly selected version-two or version-three
native build before importing or starting any candidate.

``--self-test`` is entirely synthetic: it never reads a file, loads a native
library, imports a candidate, starts an interpreter, samples a clock, creates
evidence, or opens the final holdout.
"""

from __future__ import annotations

import ast
import base64
import binascii
import builtins
import contextlib
import copy
from dataclasses import dataclass
import gc
import gzip
import hashlib
import importlib
import io
import json
import locale
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import types
from typing import Any, Callable, Mapping
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_candidate_subinterpreters_v3.py"
PROTOCOL_RELATIVE = "oracle/phase2/candidate-subinterpreters-v3.json"
EXPLANATION_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V3.md"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-owned-candidate-subinterpreters-v3"
PROTOCOL_SCHEMA = "rebar-owned-candidate-subinterpreters-protocol-v3"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
V1_SOURCE_RELATIVE = "tools/run_owned_candidate_subinterpreters_v1.py"
V1_SOURCE_SHA256 = "45e9b47c7c635fc30ebdb2cb4830d2d1fe382a5a7e4b663fb1a8e0112779e1a7"
V1_PROTOCOL_RELATIVE = "oracle/phase2/candidate-subinterpreters-v1.json"
V1_PROTOCOL_SHA256 = "7d282b559952df68b95b5ebd55634b99d922ffc27b7a640778822ec3eed6ebe2"
V1_EXPLANATION_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V1.md"
V1_EXPLANATION_SHA256 = "1dee7ebb7a98ccfec65cdb58f95378836a6747c1c9532ca676599cce62367332"
V2_SOURCE_RELATIVE = "tools/run_owned_candidate_subinterpreters_v2.py"
V2_SOURCE_SHA256 = "7dd5b4a5cdfecbe6dd674632bb5cee456ee877291de88ffc76ba60472d81408a"
V2_PROTOCOL_RELATIVE = "oracle/phase2/candidate-subinterpreters-v2.json"
V2_PROTOCOL_SHA256 = "f740da205f8431898f0a1089df5419f01612c2384def78c7d9831748ecca1b24"
V2_EXPLANATION_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V2.md"
V2_EXPLANATION_SHA256 = "c7a501f4487dfbe547c2cf8f5844be5179da035e7ae5f5e89f803234f3bf32dc"
ACTIVATION_SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v2.py"
ACTIVATION_SOURCE_SHA256 = "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218"
ACTIVATION_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md"
ACTIVATION_PROTOCOL_SHA256 = "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529"
ACTIVATION_SCHEMA = "rebar-phase2-verified-native-candidate-activation-v2"
ACTIVATION_RECEIPT_SCHEMA = ACTIVATION_SCHEMA + "-durable-publication-receipt"
ACTIVATION_JOURNAL_SCHEMA = ACTIVATION_SCHEMA + "-recovery-journal"
ACTIVATION_INTENT_SCHEMA = ACTIVATION_SCHEMA + "-durable-promotion-intent"
ACTIVATION_PREFIX = "/tmp/rebar-phase2-verified-native-activation-v2-"
REFERENCE_SOURCE_SHA256 = "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8"
ORIGINAL_PROGRAM_SHA256 = "9d136a708a438c1f8060c047d89d415c4854ffaeeee9af2fb2d8619f2f0ed07d"
ADAPTED_PROGRAM_SHA256 = "147b09bcda37678b9ac4f2f050a22eb5435c7703cbce33247e9287e62e514f71"
MATRIX_SHA256 = "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3"
REFERENCE_SHA256 = "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8"
PROJECTED_SHA256 = "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
CASE_COUNT = 128
CASE_EXECUTIONS = 394
INTERPRETER_COUNT = 11
FRESH_INTERPRETER_CASE_COUNT = 8
PHASE1_CASE_COUNT = 31_237
ORIGINAL_GUARD_MAX_BINARY_BYTES = 128 * 1024 * 1024
LEGACY_INTERPRETER_MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48
PROCESS_TIMEOUT_SECONDS = 180
PROCESS_CLEANUP_SECONDS = 15
OWNER_FIELDS = (
    "relative", "path", "sha256", "size_bytes", "device", "inode", "mode",
)
DURABLE_FLAGS = (
    "exclusive_creation", "same_inode_readback_verified",
    "file_fsync_completed", "directory_fsync_completed",
)
PROMOTION_FLAGS = (
    "atomic_replace_completed", "adjacent_exclusive_stage_verified",
    "candidate_directory_fsync_completed",
)
RENAMES = {
    "actual_stdlib_reimport": "actual_engine_reimport",
    "match_is_stdlib_match": "match_is_engine_match",
    "module_identity": "engine_sysmodules_identity_verified",
    "pattern_is_stdlib_pattern": "pattern_is_engine_pattern",
    "reimported_origin_verified": "engine_reimported_origin_verified",
    "stdlib_owner": "engine_sysmodules_owner_verified",
    "stdlib_re_module": "engine_module_name_verified",
}
ORIGINAL_GUARD_SOURCES = {
    "tools/independent_original_cpython_suite_v5.py":
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
    "tools/independent_original_cpython_suite_v4.py":
        "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3",
    "tools/rust_original_cpython_suite_v1.py":
        "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95",
    "tools/rust_original_cpython_suite_v2.py":
        "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267",
    "tools/rust_original_cpython_suite_v3.py":
        "55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2",
}


class SubinterpreterGateError(Exception):
    """A genuine versioned real-interpreter proof was missing or changed."""


class SourceOnlyViolation(SubinterpreterGateError):
    """A synthetic control attempted an actual external effect."""


class ActualCaseFailure(SubinterpreterGateError):
    """Preserve the complete actual failed interpreter lifecycle."""

    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    audit_name: str
    module: str
    source_relative: str
    engine_relative: str
    bridge_relative: str
    owners: tuple[str, ...]
    build_version: str
    build_label: str
    build_source_sha256: str
    build_protocol_sha256: str
    build_archive_sha256: str
    build_receipt_sha256: str
    native_engine_sha256: str
    native_bridge_sha256: str
    native_engine_bytes: int
    native_bridge_bytes: int


FAMILIES: dict[str, FamilySpec] = {
    "c": FamilySpec(
        "c", "c_vm", "candidates.vm_candidate", "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
        "2", "phase2-v2",
        "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796",
        "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603",
        "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878",
        "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24",
        "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697",
        "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697",
        163_136, 163_136,
    ),
    "rust": FamilySpec(
        "rust", "rust", "candidates.rust_candidate", "candidates/rust_candidate.py",
        "candidates/_rust_engine.so",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        ("candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
         "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
         "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
         "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
         "candidates/rust/src/unicode_tables.rs"),
        "2", "phase2-v2",
        "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796",
        "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603",
        "69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d",
        "15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e",
        "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
        "9e13396f93872222f77577ac7658609f5e2d3e77c0655a27c83572f0a1a06b4c",
        658_344, 148_536,
    ),
    "zig": FamilySpec(
        "zig", "zig", "candidates.zig_candidate", "candidates/zig_candidate.py",
        "candidates/_zig_probe.so",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        ("candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
         "candidates/zig/py_bridge.c"),
        "3", "phase2-v3",
        "c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f",
        "273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3",
        "485fcf3434d2c46088f8e358ce43a34aee63e3f4aacb878e63109279afb2c46c",
        "050f0156647c90ed03ebffe7d530e0a9f56d605f3728df618c85dc2f8ae570e8",
        "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071",
        "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
        108_888, 133_656,
    ),
}

ADAPTER_SOURCE_SHA256 = {
    "c": "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    "rust": "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
    "zig": "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
}

HISTORICAL_EVIDENCE: dict[str, tuple[str, str, int]] = {
    "nested_failure_archive": (
        EVIDENCE_RELATIVE + "/owned-candidate-subinterpreters-v1-c-phase2-v5-subinterpreters-failures.json.gz",
        "e375edafd74a0b77e349178b59d2d38d2cf423272b9b91dfb4baad91ad94c0f6", 6276,
    ),
    "nested_failure_receipt": (
        EVIDENCE_RELATIVE + "/owned-candidate-subinterpreters-v1-c-phase2-v5-subinterpreters-failures-publication-receipt.json",
        "3e05efd1a83cd650ab3d91cebf0380df0f0cacd5758e6c92f91e08f8acd26a62", 1514,
    ),
    "full_worker_failure_archive": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-worker-v3-c-phase2-v5-failures.json.gz",
        "149bc01c571c15034896d26eb05708985a7a3a49e361e26199682860f8c83e13", 707346,
    ),
    "full_worker_failure_receipt": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-worker-v3-c-phase2-v5-failures-publication-receipt.json",
        "fc68840c6bbf0e9bc1510894b575d0111246401eba70e8706e2a33542365fc55", 1155,
    ),
    "full_v5_failure_archive": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v5-c-phase2-v5-failures.json.gz",
        "f8c4465be0d982445f79ec66744c710b20c64bd308eaff8a12ba571b5bb0ef91", 7304,
    ),
    "full_v5_failure_receipt": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v5-c-phase2-v5-failures-publication-receipt.json",
        "10b1bb903ae3e6cf6b0b732e0518bfadce8f17a0021c36ba86bef1e641da07a1", 1180,
    ),
    "original_c_restoration": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v5-c-phase2-v5-restoration-receipt.json",
        "2bc016478561ea93c4783773a89789af4534368b9388f2d81baf2aefcdeb9dde", 2152,
    ),
    "rust_nested_failure_archive": (
        EVIDENCE_RELATIVE + "/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures.json.gz",
        "b73ea6fd2f944a46bbc89a593df251a054f62bed288b60765eb3c9dc3a9619cd", 1061,
    ),
    "rust_nested_failure_receipt": (
        EVIDENCE_RELATIVE + "/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures-publication-receipt.json",
        "99b32d784182800b92b3fcb555add6c8d27d599a91dc5255b46ca597667c6049", 1522,
    ),
    "rust_full_worker_failure_archive": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures.json.gz",
        "a2106050b59130a9eb7f083d13c2e42e22dcf9a33f5a7b35b634ff9dd9b2f9ae", 716812,
    ),
    "rust_full_worker_failure_receipt": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures-publication-receipt.json",
        "f6fe003c100a93e06239a072380c4f3839dc9863391b939ebfc6d667b174f0d9", 1161,
    ),
    "rust_full_v5_failure_archive": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v5-rust-phase2-v5-failures.json.gz",
        "bf0915a4dab62ebaea67b92258eafbc01f52b436b70f81bf7e0ca42211f95bff", 9623,
    ),
    "rust_full_v5_failure_receipt": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v5-rust-phase2-v5-failures-publication-receipt.json",
        "72070ab4f68200c305d317a59c7ff6405888d23fadaaf04835aba68d33a6c6ec", 1186,
    ),
    "original_rust_restoration": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v5-rust-phase2-v5-restoration-receipt.json",
        "3cd828fbd507d048d0e80715efef754930e89f3c176717ba1dd8985784832889", 2572,
    ),
    "full_v3_failure_archive": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v3-c-phase2-v3-failures.json.gz",
        "3f7718b09080d0aa9612dabc7f97e8f41ea35958c8bbfeb7febbbf678d06028d", 1096,
    ),
    "full_v3_failure_receipt": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v3-c-phase2-v3-failures-publication-receipt.json",
        "02996c09c8662c75eadadeccef2ac77895d942a56e06aca323e880f951a330a1", 1179,
    ),
    "full_v4_failure_archive": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v4-c-phase2-v4-failures.json.gz",
        "08614ef777081edb2335bcdaed615104c1d8a957ce246261b05d275d8bc6f50c", 0,
    ),
    "full_v4_failure_receipt": (
        EVIDENCE_RELATIVE + "/frozen-p0-candidate-v4-c-phase2-v4-failures-publication-receipt.json",
        "4ba965cca31ae3644ba37b4d8bb52f093d27349dd2aa1b747b8d2918fd60e23b", 0,
    ),
}

HISTORICAL_C_SUITE_OUTCOMES: tuple[tuple[str, str, int], ...] = (
    ("original_bounded_v5", "PASS", 82),
    ("public_v3", "PASS", 88),
    ("scanner_v3", "PASS", 89),
    ("buffer_v3", "PASS", 90),
    ("managed_v1", "PASS", 91),
    ("scanner_verbose_v1", "PASS", 93),
    ("public_types_v1", "FAIL", 95),
    ("substitution_v2", "FAIL", 97),
    ("shape_v2", "FAIL", 99),
    ("public_surface_v19", "FAIL", 101),
    ("subinterpreter_v2", "FAIL", 202),
    ("pep688_v4", "FAIL", 205),
    ("threaded_pattern_v1", "PASS", 206),
)

HISTORICAL_RUST_SUITE_OUTCOMES: tuple[tuple[str, str, int], ...] = (
    ("original_bounded_v5", "PASS", 82),
    ("public_v3", "PASS", 88),
    ("scanner_v3", "PASS", 89),
    ("buffer_v3", "PASS", 90),
    ("managed_v1", "PASS", 91),
    ("scanner_verbose_v1", "PASS", 93),
    ("public_types_v1", "FAIL", 95),
    ("substitution_v2", "FAIL", 97),
    ("shape_v2", "FAIL", 99),
    ("public_surface_v19", "FAIL", 101),
    ("subinterpreter_v2", "FAIL", 202),
    ("pep688_v4", "PASS", 204),
    ("threaded_pattern_v1", "PASS", 205),
)


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise SubinterpreterGateError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require one exact lowercase SHA-256: " + label)
    return value


def sha256(raw: Any) -> str:
    require(type(raw) is bytes, "hash only actual complete source-owned bytes")
    return hashlib.sha256(raw).hexdigest()


def _walk_json(value: Any, depth: int = 0,
               count: list[int] | None = None) -> None:
    require(depth <= 48, "reject excessive canonical JSON nesting")
    if count is None:
        count = [0]
    count[0] += 1
    require(count[0] <= 2_000_000, "reject an excessive JSON element count")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        require(abs(value) <= 1 << 256, "reject an unbounded JSON integer")
        return
    if type(value) is str:
        require(not any(0xD800 <= ord(item) <= 0xDFFF for item in value),
                "reject unpaired JSON surrogate values")
        return
    if type(value) is float:
        require(value == value and abs(value) != float("inf"),
                "reject nonfinite JSON numbers")
        return
    if type(value) is list:
        for item in value:
            _walk_json(item, depth + 1, count)
        return
    if type(value) is dict:
        for key, item in value.items():
            require(type(key) is str, "require exact string JSON keys")
            _walk_json(key, depth + 1, count)
            _walk_json(item, depth + 1, count)
        return
    raise SubinterpreterGateError("reject an unsupported canonical JSON value")


def canonical(value: Any) -> bytes:
    _walk_json(value)
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError,
            RecursionError) as error:
        raise SubinterpreterGateError("reject noncanonical JSON") from error


def canonical_line(value: Any) -> bytes:
    return canonical(value) + b"\n"


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject repeated or non-string frozen JSON keys")
        result[key] = value
    return result


def reject_constant(value: str) -> Any:
    raise SubinterpreterGateError("reject nonfinite JSON: " + value)


def decode_document(raw: Any, label: str, *, canonical_required: bool,
                    newline: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "require complete bounded JSON: " + label)
    try:
        document = json.loads(raw.decode("utf-8", "strict"),
                              object_pairs_hook=unique_pairs,
                              parse_constant=reject_constant)
    except (ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise SubinterpreterGateError("reject malformed JSON: " + label) from error
    require(type(document) is dict, "require one exact JSON object: " + label)
    _walk_json(document)
    if canonical_required:
        expected = canonical_line(document) if newline else canonical(document)
        require(raw == expected, "reject altered complete JSON bytes: " + label)
    return document


def bounded_gzip(raw: Any, *, label: str) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "require a complete bounded historical archive: " + label)
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = decoder.decompress(raw, MAX_REPORT_BYTES + 1)
        require(len(plain) <= MAX_REPORT_BYTES,
                "reject an oversized decompressed report: " + label)
        plain += decoder.flush(MAX_REPORT_BYTES + 1 - len(plain))
    except (ValueError, zlib.error, OverflowError) as error:
        raise SubinterpreterGateError("reject invalid archived evidence: " + label) from error
    require(0 < len(plain) <= MAX_REPORT_BYTES and decoder.eof
            and not decoder.unused_data and not decoder.unconsumed_tail
            and gzip.compress(plain, compresslevel=9, mtime=0) == raw,
            "reject truncated, concatenated, hidden, or altered evidence: " + label)
    return plain


def checked_family(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILIES,
            "select one independently owned C, Rust, or Zig engine")
    spec = FAMILIES[value]
    require(spec.name == value and spec.source_relative in spec.owners
            and len(spec.owners) == {"c": 2, "rust": 9, "zig": 3}[value]
            and (spec.engine_relative == spec.bridge_relative) is (value == "c")
            and spec.build_version == {"c": "2", "rust": "2", "zig": "3"}[value],
            "reject a substituted owned-source or real versioned build family")
    return spec


def checked_build_version(value: Any) -> str:
    require(type(value) is str and value in {"2", "3"},
            "explicitly choose actual native build version 2 or 3")
    return value


def checked_positive_size(value: Any, label: str, *,
                          maximum: int = ORIGINAL_GUARD_MAX_BINARY_BYTES) -> int:
    require(type(maximum) is int and 0 < maximum <= ORIGINAL_GUARD_MAX_BINARY_BYTES,
            "require the unchanged original guard's real 128-MiB size cap")
    require(type(value) is int and 0 < value <= maximum,
            "require an exact typed positive original-guard owner size: " + label)
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and value.isascii()
            and 0 < len(value) <= MAX_LABEL_BYTES
            and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for item in value)
            and not value.startswith("-") and not value.endswith("-")
            and "--" not in value,
            "reject a missing, escaping, repeated, or noncanonical evidence label")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and value.isascii() and bool(value)
            and not value.startswith("/") and "\\" not in value
            and "\x00" not in value
            and all(item not in {"", ".", ".."} for item in value.split("/")),
            "reject an absolute, traversing, or disguised frozen owner")
    return value


def checked_activation_root(value: Any, spec: FamilySpec) -> str:
    require(type(value) is str and value.isascii()
            and value.startswith(ACTIVATION_PREFIX + spec.name + "-")
            and value.count("/") == 2 and value == os.path.normpath(value)
            and "\\" not in value and "\x00" not in value,
            "require the actual selected 0700 version-two activation root")
    suffix = value.rsplit("/", 1)[1].removeprefix(
        "rebar-phase2-verified-native-activation-v2-" + spec.name + "-"
    )
    require(bool(suffix) and all(item.isascii()
                                and (item.isalnum() or item in "-_")
                                for item in suffix),
            "reject an injected, absent, or cross-family recovery suffix")
    return value


def strict_same_owner(actual: Any, expected: Any, label: str) -> None:
    require(type(actual) is dict and type(expected) is dict,
            "require complete independent owner dictionaries: " + label)
    for field in OWNER_FIELDS:
        require(field in actual and field in expected
                and type(actual[field]) is type(expected[field])
                and actual[field] == expected[field],
                "reject changed typed owner field " + field + ": " + label)
    require(all(type(actual[field]) is int
                for field in ("size_bytes", "device", "inode", "mode"))
            and actual["size_bytes"] > 0 and actual["inode"] > 0,
            "reject missing, boolean, or nonpositive owner identity: " + label)


def validate_backup_owner(
    entry: Any, actual: Any, *, spec: FamilySpec, role: str,
    activation_root: str, target: Mapping[str, Any],
) -> dict[str, Any] | None:
    roles = {"extension"} if spec.name == "c" else {"engine", "bridge"}
    require(role in roles and type(entry) is dict
            and entry.get("role") == role
            and entry.get("target_relative") == target.get("relative")
            and entry.get("target_path") == target.get("path")
            and entry.get("promoted_sha256") == target.get("sha256")
            and entry.get("promoted_size_bytes") == target.get("size_bytes")
            and type(entry.get("originally_present")) is bool,
            "preserve complete genuine per-role recoverable native history")
    if entry["originally_present"] is False:
        require(entry.get("original_owner") is None
                and entry.get("backup") is None and actual is None,
                "an absent native artifact cannot invent original backup bytes")
        return None
    original = entry.get("original_owner")
    rich = entry.get("backup")
    require(type(original) is dict and type(rich) is dict and type(actual) is dict,
            "require actual separately read durable original native backup bytes")
    relative = "backups/" + target["relative"]
    require(rich.get("relative") == relative
            and rich.get("path") == activation_root + "/" + relative
            and all(rich.get(flag) is True for flag in DURABLE_FLAGS[:3])
            and type(rich.get("write_calls")) is int
            and rich["write_calls"] > 0
            and type(rich.get("mode")) is int
            and rich["mode"] == 0o600,
            "require original independently published 0600 backup durability")
    strict_same_owner(actual, rich,
                      "actual independently reread original native backup " + role)
    require(original.get("sha256") == actual["sha256"]
            and type(original.get("size_bytes")) is int
            and original["size_bytes"] == actual["size_bytes"]
            and type(original.get("mode")) is int
            and target.get("mode") == original["mode"],
            "retain exact source-era original native bytes and executable mode")
    checked_digest(actual.get("sha256"), "actual backup " + role)
    checked_positive_size(actual.get("size_bytes"), "actual backup " + role)
    return actual


def read_owned(base: Path, relative: str, expected: str, *, maximum: int,
               exact_size: int | None = None,
               private: bool = False) -> tuple[bytes, dict[str, Any]]:
    require(isinstance(base, Path) and base.is_absolute(),
            "require one exact absolute frozen project or private root")
    safe = checked_relative(relative)
    checked_digest(expected, safe)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "require one bounded frozen source, archive, or actual native owner")
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "require the complete exact positively typed source-owner size")
    directories = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                   | getattr(os, "O_DIRECTORY", 0)
                   | getattr(os, "O_NOFOLLOW", 0))
    regular = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
               | getattr(os, "O_NOFOLLOW", 0))
    opened: list[int] = []
    try:
        current = os.open(str(base), directories)
        opened.append(current)
        first = os.fstat(current)
        visible = os.lstat(str(base))
        require(stat.S_ISDIR(first.st_mode)
                and (first.st_dev, first.st_ino)
                == (visible.st_dev, visible.st_ino)
                and (not private or (
                    first.st_uid == os.geteuid()
                    and stat.S_IMODE(first.st_mode) == 0o700
                )), "reject a redirected, unowned, or non-0700 frozen root")
        pieces = safe.split("/")
        for item in pieces[:-1]:
            current = os.open(item, directories, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "reject a symlinked or substituted frozen owner directory")
        descriptor = os.open(pieces[-1], regular, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(pieces[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size)
                and (not private or stat.S_IMODE(before.st_mode) == 0o600),
                "reject a changed, incomplete, nonregular, or nonprivate owner")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "an exact source, recovery proof, or archive was truncated")
            remaining -= len(block)
            chunks.append(block)
        require(os.read(descriptor, 1) == b"",
                "an independently pinned frozen owner has concealed trailing bytes")
        after = os.fstat(descriptor)
        named = os.stat(pieces[-1], dir_fd=current, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (named.st_dev, named.st_ino, named.st_size),
                "the exact independently frozen owner changed while being read")
        raw = b"".join(chunks)
        require(len(raw) == after.st_size and sha256(raw) == expected,
                "an actual caller-pinned owner failed its complete source hash")
        return raw, {
            "relative": safe, "path": str(base / safe),
            "sha256": expected, "size_bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def expected_family_protocol(spec: FamilySpec) -> dict[str, Any]:
    return {
        "candidate_source_sha256": ADAPTER_SOURCE_SHA256[spec.name],
        "build_version": spec.build_version,
        "build_label": spec.build_label,
        "build_source_sha256": spec.build_source_sha256,
        "build_protocol_sha256": spec.build_protocol_sha256,
        "build_archive_sha256": spec.build_archive_sha256,
        "build_receipt_sha256": spec.build_receipt_sha256,
        "native_engine_sha256": spec.native_engine_sha256,
        "native_bridge_sha256": spec.native_bridge_sha256,
        "native_engine_bytes": spec.native_engine_bytes,
        "native_bridge_bytes": spec.native_bridge_bytes,
        "independent_source_owner_count": len(spec.owners),
    }


def synthetic_protocol() -> dict[str, Any]:
    return {
        "schema": PROTOCOL_SCHEMA,
        "version": 3,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; VERSION-THREE INTERPRETER CANDIDATES NOT RUN",
        "goal_sha256": GOAL_SHA256,
        "controller": {
            "source_path": SOURCE_RELATIVE,
            "source_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "explanation_path": EXPLANATION_RELATIVE,
            "explanation_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
        },
        "python": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PINNED_PYTHON, "sha256": PINNED_PYTHON_SHA256,
            "isolated": True, "bytecode_writes": False,
        },
        "phase1": {
            "inventory_path": "oracle/phase1/p0-completeness-v1.json",
            "inventory_sha256": PHASE1_SHA256,
            "suite_count": 13,
            "case_execution_denominator": PHASE1_CASE_COUNT,
            "supplemental_subinterpreter_case_count": CASE_COUNT,
            "supplemental_cases_added_to_phase1_denominator": False,
        },
        "preserved_original_recorders": {
            "v1": {
                "source_path": V1_SOURCE_RELATIVE,
                "source_sha256": V1_SOURCE_SHA256,
                "protocol_path": V1_PROTOCOL_RELATIVE,
                "protocol_sha256": V1_PROTOCOL_SHA256,
                "explanation_path": V1_EXPLANATION_RELATIVE,
                "explanation_sha256": V1_EXPLANATION_SHA256,
                "source_mutated": False,
            },
            "v2": {
                "source_path": V2_SOURCE_RELATIVE,
                "source_sha256": V2_SOURCE_SHA256,
                "protocol_path": V2_PROTOCOL_RELATIVE,
                "protocol_sha256": V2_PROTOCOL_SHA256,
                "explanation_path": V2_EXPLANATION_RELATIVE,
                "explanation_sha256": V2_EXPLANATION_SHA256,
                "source_mutated": False,
            },
        },
        "corrected_canonical_activation": {
            "source_path": ACTIVATION_SOURCE_RELATIVE,
            "source_sha256": ACTIVATION_SOURCE_SHA256,
            "protocol_path": ACTIVATION_PROTOCOL_RELATIVE,
            "protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
            "report_schema": ACTIVATION_SCHEMA,
            "receipt_schema": ACTIVATION_RECEIPT_SCHEMA,
            "journal_schema": ACTIVATION_JOURNAL_SCHEMA,
            "promotion_intent_schema": ACTIVATION_INTENT_SCHEMA,
            "explicit_native_build_version_required": True,
            "private_journal_root_mode": "0700",
            "actual_report_receipt_journal_intent_backup_mode": "0600",
            "typed_identity_fields": list(OWNER_FIELDS),
            "independently_authenticated_durability_flags": list(DURABLE_FLAGS),
            "positive_typed_publication_write_calls_required": True,
            "rich_durability_compared_as_bare_identity": False,
            "source_owned_activation_validators_required": True,
            "independently_reauthenticated_prior_build_process_count": 39,
            "actual_original_backup_bytes_required": True,
            "actual_original_backup_inode_required": True,
            "failed_build_publication_receipt_accepted": False,
            "preserved_original_matcher_guard_root": str(ROOT),
            "frozen_guard_root_mutation_allowed": False,
        },
        "candidate_families": {
            name: expected_family_protocol(spec)
            for name, spec in FAMILIES.items()
        },
        "reference": {
            "source_path": "tools/python_re_subinterpreter_oracle_v2.py",
            "source_sha256": REFERENCE_SOURCE_SHA256,
            "producer_program_bytes": 11378,
            "producer_program_sha256": ORIGINAL_PROGRAM_SHA256,
            "adapted_program_bytes": 12759,
            "adapted_program_sha256": ADAPTED_PROGRAM_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "reference_records_sha256": REFERENCE_SHA256,
            "projected_reference_records_sha256": PROJECTED_SHA256,
            "case_count": CASE_COUNT,
        },
        "original_guard_size_correction": {
            "preserved_original_guard_source":
                "tools/independent_original_cpython_suite_v5.py",
            "preserved_original_guard_sha256":
                ORIGINAL_GUARD_SOURCES[
                    "tools/independent_original_cpython_suite_v5.py"
                ],
            "original_guard_maximum_binary_bytes":
                ORIGINAL_GUARD_MAX_BINARY_BYTES,
            "rejected_legacy_interpreter_maximum_binary_bytes":
                LEGACY_INTERPRETER_MAX_BINARY_BYTES,
            "actual_positive_source_sizes_required": True,
            "actual_positive_native_sizes_required": True,
            "candidate_source_or_original_guard_mutated": False,
            "legacy_internal_worker_invoked": False,
        },
        "lossless_observation_field_renames": dict(RENAMES),
        "lifecycle": {
            "expected_case_execution_count": CASE_COUNT,
            "expected_a_observations": CASE_COUNT,
            "expected_b_observations": CASE_COUNT,
            "expected_repeated_a_observations": CASE_COUNT,
            "expected_fresh_interpreter_case_observations":
                FRESH_INTERPRETER_CASE_COUNT,
            "expected_a_after_b_close_observations": 1,
            "expected_fresh_c_observations": 1,
            "expected_case_interpreter_exec_calls": CASE_EXECUTIONS,
            "expected_initialization_interpreter_exec_calls": INTERPRETER_COUNT,
            "expected_guard_cleanup_interpreter_exec_calls": INTERPRETER_COUNT,
            "expected_interpreters_created": INTERPRETER_COUNT,
            "expected_interpreters_destroyed": INTERPRETER_COUNT,
            "correctness_worker_timeout_seconds": PROCESS_TIMEOUT_SECONDS,
            "correctness_worker_cleanup_timeout_seconds": PROCESS_CLEANUP_SECONDS,
            "all_real_pipes_read_to_eof_required": True,
            "all_real_pipe_descriptors_closed_required": True,
            "interpreter_live_set_restoration_required": True,
            "locale_restoration_required": True,
        },
        "preserved_c_v5_actual_failure": {
            "archive_path": HISTORICAL_EVIDENCE["nested_failure_archive"][0],
            "archive_sha256": HISTORICAL_EVIDENCE["nested_failure_archive"][1],
            "archive_bytes": HISTORICAL_EVIDENCE["nested_failure_archive"][2],
            "receipt_path": HISTORICAL_EVIDENCE["nested_failure_receipt"][0],
            "receipt_sha256": HISTORICAL_EVIDENCE["nested_failure_receipt"][1],
            "receipt_bytes": HISTORICAL_EVIDENCE["nested_failure_receipt"][2],
            "uncompressed_sha256":
                "24a0dbc4bb7e331f5bec729b58476d159e16c5bfcbab2ba651dcea33377a7b9c",
            "uncompressed_bytes": 14943,
            "result_status": "FAIL",
            "failure_publication_receipt_status": "PASS",
            "failed_phase": "install-real-persistent-original-V5-in-A",
            "actual_case_interpreter_exec_calls": 0,
            "actual_initialization_interpreter_exec_calls": 1,
            "actual_guard_cleanup_interpreter_exec_calls": 2,
            "actual_interpreters_created": 2,
            "actual_interpreters_destroyed": 2,
            "actual_failed_cleanup_count": 2,
            "failed_worker_pid": 204,
            "static_audit_pid": 203,
            "historical_suite_process_count": 13,
            "historical_total_distinct_child_process_count": 16,
            "historical_passed_suite_count": 7,
            "historical_failed_suite_count": 6,
            "historical_executed_passing_candidate_case_count": 7197,
            "failed_candidate_qualified": False,
            "all_complete_process_evidence_preserved": True,
            "original_c_restoration_receipt_sha256":
                HISTORICAL_EVIDENCE["original_c_restoration"][1],
        },
        "preserved_rust_v5_actual_failure": {
            "archive_path": HISTORICAL_EVIDENCE["rust_nested_failure_archive"][0],
            "archive_sha256": HISTORICAL_EVIDENCE["rust_nested_failure_archive"][1],
            "archive_bytes": HISTORICAL_EVIDENCE["rust_nested_failure_archive"][2],
            "receipt_path": HISTORICAL_EVIDENCE["rust_nested_failure_receipt"][0],
            "receipt_sha256": HISTORICAL_EVIDENCE["rust_nested_failure_receipt"][1],
            "receipt_bytes": HISTORICAL_EVIDENCE["rust_nested_failure_receipt"][2],
            "uncompressed_sha256":
                "db58671b49bbf31b705cd903bc7860c49ccb165ab93e9063bc0d585d17c2ad04",
            "uncompressed_bytes": 1981,
            "result_status": "FAIL",
            "failure_publication_receipt_status": "PASS",
            "failed_phase": "frozen static independence audit",
            "actual_nested_worker_started": False,
            "actual_case_interpreter_exec_calls": 0,
            "actual_interpreters_created": 0,
            "failed_static_audit_pid": 203,
            "historical_suite_process_count": 13,
            "historical_total_distinct_child_process_count": 15,
            "historical_passed_suite_count": 8,
            "historical_failed_suite_count": 5,
            "historical_executed_passing_candidate_case_count": 7461,
            "failed_candidate_qualified": False,
            "all_complete_process_evidence_preserved": True,
            "original_rust_restoration_receipt_sha256":
                HISTORICAL_EVIDENCE["original_rust_restoration"][1],
        },
        "evidence": {
            "directory": EVIDENCE_RELATIVE,
            "archive_template":
                "owned-candidate-subinterpreters-v3-FAMILY-LABEL.json.gz",
            "receipt_template":
                "owned-candidate-subinterpreters-v3-FAMILY-LABEL-publication-receipt.json",
            "failure_archive_template":
                "owned-candidate-subinterpreters-v3-FAMILY-LABEL-failures.json.gz",
            "failure_receipt_template":
                "owned-candidate-subinterpreters-v3-FAMILY-LABEL-failures-publication-receipt.json",
            "deterministic_gzip_mtime": 0,
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_required": True,
            "directory_fsync_required": True,
            "complete_failures_preserved": True,
        },
        "source_only_boundaries": {
            "actual_version_three_candidate_workers_started": 0,
            "actual_version_three_candidate_imports": 0,
            "actual_version_three_interpreters_created": 0,
            "actual_version_three_native_activations_started": 0,
            "actual_version_three_source_builds_started": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
            "historical_real_candidate_execution_falsely_denied": False,
        },
    }


def validate_protocol(document: Any) -> dict[str, Any]:
    require(type(document) is dict
            and canonical(document) == canonical(synthetic_protocol()),
            "reject a changed frozen nested V3 oracle, history, owner, or boundary")
    return document


def source_pins(spec: FamilySpec, values: Any) -> dict[str, str]:
    require(type(values) is list and len(values) == len(spec.owners),
            "pin every independent selected family owner exactly once")
    result: dict[str, str] = {}
    for value in values:
        require(type(value) is str and value.count("=") == 1,
                "require exactly RELATIVE/PATH=SHA256 for each owner")
        relative, digest = value.split("=", 1)
        checked_relative(relative)
        require(relative in spec.owners and relative not in result,
                "reject missing, cross-family, duplicate, or unrelated sources")
        result[relative] = checked_digest(digest, relative)
    require(set(result) == set(spec.owners),
            "authenticate the exact complete independent source graph")
    return dict(sorted(result.items()))


def _parse_decimal(value: Any, name: str) -> int:
    require(type(value) is str and value.isascii() and value.isdecimal()
            and value == str(int(value)),
            "require canonical exact decimal native bytes: " + name)
    return checked_positive_size(int(value), name)


def parse_arguments(arguments: Any) -> dict[str, Any]:
    require(type(arguments) is list
            and all(type(value) is str for value in arguments),
            "require one complete exact nested V3 command")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(bool(arguments)
            and arguments[0] in {
                "--record-candidate", "--internal-worker", "--verify-frozen-context",
            }, "explicitly select a source check or an authorized actual worker")
    mode = arguments[0][2:]
    if mode == "verify-frozen-context":
        mapping = {
            "--source-sha256": "source_sha256",
            "--protocol-sha256": "protocol_sha256",
            "--explanation-sha256": "explanation_sha256",
        }
        result: dict[str, Any] = {"mode": mode}
    else:
        mapping = {
            "--family": "family",
            "--build-version": "build_version",
            "--label": "label",
            "--candidate-source-sha256": "candidate_source_sha256",
            "--source-sha256": "source_sha256",
            "--protocol-sha256": "protocol_sha256",
            "--explanation-sha256": "explanation_sha256",
            "--v1-source-sha256": "v1_source_sha256",
            "--v1-protocol-sha256": "v1_protocol_sha256",
            "--v1-explanation-sha256": "v1_explanation_sha256",
            "--v2-source-sha256": "v2_source_sha256",
            "--v2-protocol-sha256": "v2_protocol_sha256",
            "--v2-explanation-sha256": "v2_explanation_sha256",
            "--build-label": "build_label",
            "--build-source-sha256": "build_source_sha256",
            "--build-protocol-sha256": "build_protocol_sha256",
            "--build-archive-sha256": "build_archive_sha256",
            "--build-receipt-sha256": "build_receipt_sha256",
            "--activation-root": "activation_root",
            "--activation-source-sha256": "activation_source_sha256",
            "--activation-protocol-sha256": "activation_protocol_sha256",
            "--activation-report-sha256": "activation_report_sha256",
            "--activation-receipt-sha256": "activation_receipt_sha256",
            "--native-engine-sha256": "native_engine_sha256",
            "--native-bridge-sha256": "native_bridge_sha256",
            "--native-engine-bytes": "native_engine_bytes",
            "--native-bridge-bytes": "native_bridge_bytes",
        }
        result = {"mode": mode, "owned_source_sha256": []}
    position = 1
    while position < len(arguments):
        require(position + 1 < len(arguments),
                "require an exact value for every frozen V3 authorization")
        option, value = arguments[position:position + 2]
        if option == "--owned-source-sha256" and mode != "verify-frozen-context":
            result["owned_source_sha256"].append(value)
        else:
            require(option in mapping and mapping[option] not in result,
                    "reject unknown, duplicated, abbreviated, or holdout options")
            key = mapping[option]
            result[key] = (_parse_decimal(value, key)
                           if key in {"native_engine_bytes", "native_bridge_bytes"}
                           else value)
        position += 2
    expected = {"mode", *mapping.values()}
    if mode != "verify-frozen-context":
        expected.add("owned_source_sha256")
    require(set(result) == expected,
            "pin every original, versioned activation, build, and native proof")
    for key, value in result.items():
        if key.endswith("_sha256") and key != "owned_source_sha256":
            checked_digest(value, key)
    if mode == "verify-frozen-context":
        return result
    spec = checked_family(result["family"])
    checked_label(result["label"])
    checked_label(result["build_label"])
    checked_activation_root(result["activation_root"], spec)
    checked_build_version(result["build_version"])
    required = {
        "candidate_source_sha256": ADAPTER_SOURCE_SHA256[spec.name],
        "v1_source_sha256": V1_SOURCE_SHA256,
        "v1_protocol_sha256": V1_PROTOCOL_SHA256,
        "v1_explanation_sha256": V1_EXPLANATION_SHA256,
        "v2_source_sha256": V2_SOURCE_SHA256,
        "v2_protocol_sha256": V2_PROTOCOL_SHA256,
        "v2_explanation_sha256": V2_EXPLANATION_SHA256,
        "activation_source_sha256": ACTIVATION_SOURCE_SHA256,
        "activation_protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
        "build_source_sha256": spec.build_source_sha256,
        "build_protocol_sha256": spec.build_protocol_sha256,
        "build_archive_sha256": spec.build_archive_sha256,
        "build_receipt_sha256": spec.build_receipt_sha256,
        "native_engine_sha256": spec.native_engine_sha256,
        "native_bridge_sha256": spec.native_bridge_sha256,
    }
    for key, expected_value in required.items():
        require(result[key] == expected_value,
                "reject stale, failed, cross-version, or altered proof: " + key)
    require(result["build_version"] == spec.build_version
            and result["build_label"] == spec.build_label
            and result["native_engine_bytes"] == spec.native_engine_bytes
            and result["native_bridge_bytes"] == spec.native_bridge_bytes,
            "require the actual published family, source build, and native sizes")
    owners = source_pins(spec, result["owned_source_sha256"])
    require(owners[spec.source_relative] == result["candidate_source_sha256"],
            "bind the genuine adapter to its complete source-owner closure")
    require((result["native_engine_sha256"]
             == result["native_bridge_sha256"]) is (spec.name == "c"),
            "only the actual combined C engine and bridge may share bytes")
    return result


def _fresh_module(relative: str, expected: str) -> types.ModuleType:
    read_owned(ROOT, relative, expected, maximum=MAX_SOURCE_BYTES)
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    name = relative.removesuffix(".py").replace("/", ".")
    module = importlib.import_module(name)
    require(type(module) is types.ModuleType and module.__name__ == name
            and os.path.abspath(module.__file__) == str(ROOT / relative),
            "load only the exact source-authenticated original oracle owner")
    read_owned(ROOT, relative, expected, maximum=MAX_SOURCE_BYTES)
    return module


def _verify_encoded_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict and value.get("encoding") == "base64"
            and value.get("complete") is True
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_REPORT_BYTES
            and type(value.get("data")) is str,
            "require a complete actual recorded process stream: " + label)
    try:
        raw = base64.b64decode(value["data"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError, binascii.Error) as error:
        raise SubinterpreterGateError("reject forged process stream: " + label) from error
    require(len(raw) == value["bytes"]
            and sha256(raw) == checked_digest(value.get("sha256"), label),
            "preserve the exact complete real process stream: " + label)
    return raw


def _history_record(name: str) -> tuple[bytes, dict[str, Any]]:
    relative, digest, size = HISTORICAL_EVIDENCE[name]
    return read_owned(ROOT, relative, digest, maximum=MAX_ARCHIVE_BYTES,
                      exact_size=size if size else None)


def _check_failure_receipt(receipt: dict[str, Any], archive: bytes,
                           archive_relative: str, plain: bytes,
                           *, result_key: str) -> None:
    require(receipt.get("status") == "PASS"
            and receipt.get(result_key) == "FAIL",
            "receipt PASS proves failure publication, never candidate success")
    publication = receipt.get("archive")
    if publication is None:
        publication = receipt.get("archive_publication")
    require(type(publication) is dict
            and publication.get("relative", archive_relative) == archive_relative
            and publication.get("sha256") == sha256(archive)
            and publication.get("bytes") == len(archive)
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and (publication.get("file_fsync_completed") is True
                 or publication.get("file_fsync") is True)
            and receipt.get("uncompressed_sha256") == sha256(plain)
            and receipt.get("uncompressed_bytes") == len(plain),
            "require exact exclusive historical failure bytes and durability")


def authenticate_preserved_failure() -> dict[str, Any]:
    nested_raw, nested_owner = _history_record("nested_failure_archive")
    nested_plain = bounded_gzip(nested_raw, label="actual C V5 nested failure")
    nested = decode_document(nested_plain, "actual C V5 nested failure",
                             canonical_required=True)
    receipt_raw, receipt_owner = _history_record("nested_failure_receipt")
    receipt = decode_document(receipt_raw, "actual nested C failure receipt",
                              canonical_required=True)
    _check_failure_receipt(receipt, nested_raw, nested_owner["relative"],
                           nested_plain, result_key="result_status")
    require(nested.get("schema")
            == "rebar-owned-candidate-subinterpreters-v1-candidate-evaluation"
            and nested.get("status") == "FAIL"
            and nested.get("candidate_family") == "c"
            and nested.get("label") == "phase2-v5-subinterpreters"
            and nested.get("worker") is None,
            "preserve the genuinely failed original C real-interpreter worker")
    failure = nested.get("failure")
    require(type(failure) is dict, "preserve the full original nested failure")
    middle = failure.get("actual_failure")
    require(type(middle) is dict and middle.get("status") == "FAIL",
            "preserve the actual original nested worker failure")
    detail = middle.get("actual_failure")
    require(type(detail) is dict
            and detail.get("active_phase")
            == "install-real-persistent-original-V5-in-A"
            and type(detail.get("actual_case_interpreter_exec_calls")) is int
            and detail["actual_case_interpreter_exec_calls"] == 0
            and type(detail.get("actual_initialization_interpreter_exec_calls")) is int
            and detail["actual_initialization_interpreter_exec_calls"] == 1
            and type(detail.get("actual_guard_cleanup_interpreter_exec_calls")) is int
            and detail["actual_guard_cleanup_interpreter_exec_calls"] == 2
            and detail.get("actual_interpreters_created") == 2
            and detail.get("actual_interpreters_destroyed") == 2
            and type(detail.get("cleanup_failures")) is list
            and len(detail["cleanup_failures"]) == 2
            and "an exact independently owned source or native size is mandatory"
            in str(detail.get("error_message", "")),
            "preserve the true 256-MiB guard failure and both real cleanup errors")
    nested_process = nested.get("worker_process")
    audit = nested.get("static_independence_audit")
    require(type(nested_process) is dict and nested_process.get("pid") == 204
            and nested_process.get("returncode") == 1
            and nested_process.get("timed_out") is False
            and nested_process.get("process_reaped") is True
            and type(audit) is dict and audit.get("pid") == 203
            and audit.get("returncode") == 0,
            "retain both authentic static-audit and failed child process IDs")
    stdout = _verify_encoded_stream(nested_process.get("stdout"),
                                    "failed original subinterpreter stdout")
    stderr = _verify_encoded_stream(nested_process.get("stderr"),
                                    "failed original subinterpreter stderr")
    require(stderr == b"" and stdout
            and decode_document(stdout, "failed actual nested worker output",
                                canonical_required=True).get("status") == "FAIL",
            "preserve complete actual failed nested-worker process streams")

    worker_raw, worker_owner = _history_record("full_worker_failure_archive")
    worker_plain = bounded_gzip(worker_raw, label="actual C V5 complete worker")
    worker = decode_document(worker_plain, "actual complete C V5 worker",
                             canonical_required=True)
    worker_receipt_raw, worker_receipt_owner = _history_record(
        "full_worker_failure_receipt"
    )
    worker_receipt = decode_document(worker_receipt_raw,
                                     "actual complete worker failure receipt",
                                     canonical_required=True)
    _check_failure_receipt(worker_receipt, worker_raw, worker_owner["relative"],
                           worker_plain, result_key="candidate_status")
    suites = worker.get("all_suites")
    require(worker.get("status") == "FAIL"
            and worker.get("candidate_family") == "c"
            and worker.get("case_execution_denominator") == PHASE1_CASE_COUNT
            and worker.get("suite_count") == 13
            and worker.get("completed_candidate_suite_count") == 7
            and worker.get("qualified_candidate_case_executions") == 7197
            and worker.get("all_required_suites_executed") is True
            and worker.get("all_required_suites_passed") is False
            and type(worker.get("all_failure_reasons")) is list
            and len(worker["all_failure_reasons"]) == 6
            and type(suites) is list and len(suites) == 13,
            "retain all 13 real historical C suites, six losses, and 7,197 cases")
    actual_pids: list[int] = []
    for suite, expected in zip(suites, HISTORICAL_C_SUITE_OUTCOMES, strict=True):
        name, status, pid = expected
        require(type(suite) is dict and suite.get("suite") == name
                and suite.get("status") == status,
                "preserve every genuine original C suite and its exact outcome")
        process = suite.get("actual_process")
        require(type(process) is dict and process.get("pid") == pid
                and type(process.get("returncode")) is int
                and process.get("timed_out") is False,
                "preserve every actual distinct recorded C suite process")
        for stream in ("stdout", "stderr"):
            _verify_encoded_stream(process.get(stream), name + " " + stream)
        actual_pids.append(pid)

    aggregate_raw, aggregate_owner = _history_record("full_v5_failure_archive")
    aggregate_plain = bounded_gzip(aggregate_raw, label="actual C V5 full failure")
    aggregate = decode_document(aggregate_plain, "actual C V5 full failure",
                                canonical_required=True)
    aggregate_receipt_raw, aggregate_receipt_owner = _history_record(
        "full_v5_failure_receipt"
    )
    aggregate_receipt = decode_document(
        aggregate_receipt_raw, "actual C V5 full failure receipt",
        canonical_required=True,
    )
    _check_failure_receipt(aggregate_receipt, aggregate_raw,
                           aggregate_owner["relative"], aggregate_plain,
                           result_key="candidate_status")
    outer = aggregate.get("failed_worker_process")
    require(aggregate.get("status") == "FAIL"
            and aggregate.get("candidate_family") == "c"
            and aggregate.get("case_execution_denominator") == PHASE1_CASE_COUNT
            and aggregate.get("suite_count") == 13
            and aggregate.get("candidate_qualified") is False
            and aggregate.get("supplemental_subinterpreter_case_count") == 0
            and aggregate.get("supplemental_cases_added_to_original_denominator")
            is False and type(outer) is dict and outer.get("pid") == 81
            and outer.get("returncode") == 1,
            "never infer a passing aggregate or 128 successful failed observations")
    restoration_raw, restoration_owner = _history_record("original_c_restoration")
    restoration = decode_document(restoration_raw, "actual original C restoration",
                                  canonical_required=True)
    target = restoration.get("restored_targets", {}).get("extension")
    require(restoration.get("status") == "PASS"
            and restoration.get("family") == "c"
            and type(target) is dict
            and target.get("sha256")
            == "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
            and target.get("size_bytes") == 149_976
            and target.get("restored_from_verified_backup") is True,
            "preserve genuine exact byte-for-byte original native restoration")
    all_pids = sorted([81, 203, 204, *actual_pids])
    require(len(all_pids) == 16 and len(set(all_pids)) == 16,
            "preserve all 16 distinct actual historical C child processes")
    return {
        "schema": SCHEMA + "-authenticated-historical-c-v5-failure",
        "status": "PASS",
        "historical_candidate_result": "FAIL",
        "failure_publication_status": "PASS",
        "historical_supplemental_case_executions": 0,
        "historical_actual_initialization_calls": 1,
        "historical_actual_cleanup_calls": 2,
        "historical_failed_cleanup_count": 2,
        "historical_passed_suite_count": 7,
        "historical_failed_suite_count": 6,
        "historical_executed_passing_candidate_cases": 7197,
        "historical_child_process_count": 16,
        "historical_child_process_ids": all_pids,
        "failed_nested_worker_pid": 204,
        "actual_failure_phase": "install-real-persistent-original-V5-in-A",
        "failure_archive": nested_owner,
        "failure_receipt": receipt_owner,
        "complete_worker_archive": worker_owner,
        "complete_worker_receipt": worker_receipt_owner,
        "aggregate_failure_archive": aggregate_owner,
        "aggregate_failure_receipt": aggregate_receipt_owner,
        "original_restoration_receipt": restoration_owner,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def authenticate_preserved_rust_failure() -> dict[str, Any]:
    raw, nested_owner = _history_record("rust_nested_failure_archive")
    plain = bounded_gzip(raw, label="actual Rust V5 nested static-audit failure")
    nested = decode_document(plain, "actual Rust nested failure",
                             canonical_required=True)
    receipt_raw, receipt_owner = _history_record("rust_nested_failure_receipt")
    receipt = decode_document(receipt_raw, "actual Rust nested failure receipt",
                              canonical_required=True)
    _check_failure_receipt(receipt, raw, nested_owner["relative"], plain,
                           result_key="result_status")
    require(nested.get("schema")
            == "rebar-owned-candidate-subinterpreters-v1-candidate-evaluation"
            and nested.get("status") == "FAIL"
            and nested.get("candidate_family") == "rust"
            and nested.get("label") == "phase2-v5-subinterpreters"
            and nested.get("worker") is None
            and nested.get("worker_process") is None
            and nested.get("static_independence_audit") is None,
            "never describe a failed Rust static audit as an executed interpreter")
    failure = nested.get("failure")
    require(type(failure) is dict
            and failure.get("error_type") == "ActualCaseFailure"
            and failure.get("error_message")
            == "the frozen isolated static independence audit did not pass",
            "preserve the exact genuine original Rust static-audit failure")
    audit = failure.get("actual_failure")
    require(type(audit) is dict and audit.get("pid") == 203
            and audit.get("returncode") == 1
            and audit.get("role") == "frozen static independence audit"
            and audit.get("timed_out") is False
            and audit.get("process_reaped") is True,
            "preserve the real independently failed Rust static-audit process")
    stdout = _verify_encoded_stream(audit.get("stdout"),
                                    "actual failed Rust static-audit stdout")
    stderr = _verify_encoded_stream(audit.get("stderr"),
                                    "actual failed Rust static-audit stderr")
    result = decode_document(stdout, "genuine failed Rust native-owner audit",
                             canonical_required=True)
    require(stderr == b"" and result.get("status") == "FAIL"
            and result.get("schema")
            == "rebar-phase2-candidate-independence-static-audit-v1"
            and "unexpected native library identity"
            in str(result.get("error", "")),
            "never misattribute the Rust native-identity failure to the C bootstrap")

    full_raw, worker_owner = _history_record("rust_full_worker_failure_archive")
    full_plain = bounded_gzip(full_raw, label="actual Rust complete V5 worker")
    worker = decode_document(full_plain, "actual Rust complete V5 worker",
                             canonical_required=True)
    full_receipt_raw, worker_receipt_owner = _history_record(
        "rust_full_worker_failure_receipt"
    )
    full_receipt = decode_document(full_receipt_raw,
                                   "actual Rust full worker failure receipt",
                                   canonical_required=True)
    _check_failure_receipt(full_receipt, full_raw, worker_owner["relative"],
                           full_plain, result_key="candidate_status")
    suites = worker.get("all_suites")
    require(worker.get("status") == "FAIL"
            and worker.get("candidate_family") == "rust"
            and worker.get("case_execution_denominator") == PHASE1_CASE_COUNT
            and worker.get("suite_count") == 13
            and worker.get("completed_candidate_suite_count") == 8
            and worker.get("qualified_candidate_case_executions") == 7461
            and worker.get("all_required_suites_executed") is True
            and worker.get("all_required_suites_passed") is False
            and type(worker.get("all_failure_reasons")) is list
            and len(worker["all_failure_reasons"]) == 5
            and type(suites) is list and len(suites) == 13,
            "preserve all real Rust outcomes, five failures, and 7,461 cases")
    pids: list[int] = []
    for row, expected in zip(suites, HISTORICAL_RUST_SUITE_OUTCOMES, strict=True):
        name, status, pid = expected
        require(type(row) is dict and row.get("suite") == name
                and row.get("status") == status,
                "preserve every actual original Rust suite outcome")
        process = row.get("actual_process")
        require(type(process) is dict and process.get("pid") == pid
                and type(process.get("returncode")) is int
                and process.get("timed_out") is False,
                "retain every real actual Rust suite child process")
        for stream in ("stdout", "stderr"):
            _verify_encoded_stream(process.get(stream),
                                   "Rust " + name + " " + stream)
        pids.append(pid)

    aggregate_raw, aggregate_owner = _history_record(
        "rust_full_v5_failure_archive"
    )
    aggregate_plain = bounded_gzip(aggregate_raw,
                                   label="actual complete Rust V5 failure")
    aggregate = decode_document(aggregate_plain, "actual Rust V5 full failure",
                                canonical_required=True)
    aggregate_receipt_raw, aggregate_receipt_owner = _history_record(
        "rust_full_v5_failure_receipt"
    )
    aggregate_receipt = decode_document(
        aggregate_receipt_raw, "actual Rust V5 full failure receipt",
        canonical_required=True,
    )
    _check_failure_receipt(aggregate_receipt, aggregate_raw,
                           aggregate_owner["relative"], aggregate_plain,
                           result_key="candidate_status")
    outer = aggregate.get("failed_worker_process")
    require(aggregate.get("status") == "FAIL"
            and aggregate.get("candidate_family") == "rust"
            and aggregate.get("case_execution_denominator") == PHASE1_CASE_COUNT
            and aggregate.get("suite_count") == 13
            and aggregate.get("candidate_qualified") is False
            and aggregate.get("supplemental_subinterpreter_case_count") == 0
            and aggregate.get("supplemental_cases_added_to_original_denominator")
            is False and type(outer) is dict and outer.get("pid") == 81
            and outer.get("returncode") == 1,
            "reject a fabricated passing Rust interpreter or qualification")
    restoration_raw, restoration_owner = _history_record(
        "original_rust_restoration"
    )
    restoration = decode_document(restoration_raw,
                                  "actual original Rust native restoration",
                                  canonical_required=True)
    targets = restoration.get("restored_targets")
    require(restoration.get("status") == "PASS"
            and restoration.get("family") == "rust"
            and type(targets) is dict
            and set(targets) == {"engine", "bridge"},
            "preserve both genuinely restored original Rust native roles")
    for role, digest, size in (
        ("engine",
         "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
         660_440),
        ("bridge",
         "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
         144_992),
    ):
        target = targets[role]
        require(type(target) is dict and target.get("sha256") == digest
                and target.get("size_bytes") == size
                and target.get("restored_from_verified_backup") is True,
                "preserve byte-exact actual original Rust " + role + " restoration")
    process_ids = sorted([81, 203, *pids])
    require(len(process_ids) == 15 and len(set(process_ids)) == 15,
            "preserve all distinct actual historical Rust child processes")
    return {
        "schema": SCHEMA + "-authenticated-historical-rust-v5-failure",
        "status": "PASS",
        "historical_candidate_result": "FAIL",
        "failure_publication_status": "PASS",
        "historical_supplemental_case_executions": 0,
        "historical_nested_interpreter_worker_started": False,
        "historical_passed_suite_count": 8,
        "historical_failed_suite_count": 5,
        "historical_executed_passing_candidate_cases": 7461,
        "historical_child_process_count": 15,
        "historical_child_process_ids": process_ids,
        "failed_static_audit_pid": 203,
        "actual_failure_phase": "frozen static independence audit",
        "failure_archive": nested_owner,
        "failure_receipt": receipt_owner,
        "complete_worker_archive": worker_owner,
        "complete_worker_receipt": worker_receipt_owner,
        "aggregate_failure_archive": aggregate_owner,
        "aggregate_failure_receipt": aggregate_receipt_owner,
        "original_restoration_receipt": restoration_owner,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def authenticate_support(arguments: Mapping[str, Any]) -> dict[str, Any]:
    require(sys.executable == PINNED_PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "require the exact isolated stable CPython 3.14.6 oracle")
    support: dict[str, dict[str, Any]] = {}
    required = (
        ("GOAL.md", GOAL_SHA256),
        ("oracle/phase1/p0-completeness-v1.json", PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["protocol_sha256"]),
        (EXPLANATION_RELATIVE, arguments["explanation_sha256"]),
        (V1_SOURCE_RELATIVE, V1_SOURCE_SHA256),
        (V1_PROTOCOL_RELATIVE, V1_PROTOCOL_SHA256),
        (V1_EXPLANATION_RELATIVE, V1_EXPLANATION_SHA256),
        (V2_SOURCE_RELATIVE, V2_SOURCE_SHA256),
        (V2_PROTOCOL_RELATIVE, V2_PROTOCOL_SHA256),
        (V2_EXPLANATION_RELATIVE, V2_EXPLANATION_SHA256),
        (ACTIVATION_SOURCE_RELATIVE, ACTIVATION_SOURCE_SHA256),
        (ACTIVATION_PROTOCOL_RELATIVE, ACTIVATION_PROTOCOL_SHA256),
        ("tools/python_re_subinterpreter_oracle_v2.py", REFERENCE_SOURCE_SHA256),
    )
    for relative, digest in required:
        raw, owner = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
        support[relative] = owner
        if relative == PROTOCOL_RELATIVE:
            validate_protocol(decode_document(raw, "published nested V3 protocol",
                                              canonical_required=False))
    guard_sizes: dict[str, int] = {}
    for relative, digest in sorted(ORIGINAL_GUARD_SOURCES.items()):
        _, owner = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
        support[relative] = owner
        guard_sizes[relative] = checked_positive_size(owner["size_bytes"], relative)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "reject any actual candidate before frozen support authentication")
    return {"support": support, "guard_sizes": guard_sizes}


def authenticate_activation(arguments: Mapping[str, Any],
                            preliminary: Mapping[str, Any]) -> dict[str, Any]:
    spec = checked_family(arguments["family"])
    owners = source_pins(spec, arguments["owned_source_sha256"])
    version = checked_build_version(arguments["build_version"])
    activator = _fresh_module(ACTIVATION_SOURCE_RELATIVE,
                              ACTIVATION_SOURCE_SHA256)
    require(getattr(activator, "SCHEMA", None) == ACTIVATION_SCHEMA
            and getattr(activator, "RECEIPT_SCHEMA", None)
            == ACTIVATION_RECEIPT_SCHEMA
            and getattr(activator, "JOURNAL_SCHEMA", None)
            == ACTIVATION_JOURNAL_SCHEMA
            and getattr(activator, "INTENT_SCHEMA", None)
            == ACTIVATION_INTENT_SCHEMA
            and tuple(getattr(activator, "OWNER_FIELDS", ())) == OWNER_FIELDS
            and tuple(getattr(activator, "DURABLE_FLAGS", ())) == DURABLE_FLAGS
            and callable(getattr(activator, "validate_activation_documents", None))
            and callable(getattr(activator, "validate_build_report", None))
            and callable(getattr(activator, "authenticate_promotion_intents", None))
            and callable(getattr(activator, "authenticate_preserved_v2_history", None))
            and callable(getattr(activator, "expected_history_summary", None))
            and callable(getattr(activator, "same_owner", None)),
            "load only the exact frozen dual-version crash-recovery validator")
    try:
        actual_native_history = activator.authenticate_preserved_v2_history()
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the frozen activator rejected an actual original native-build process"
        ) from error
    require(type(actual_native_history) is dict
            and actual_native_history == activator.expected_history_summary()
            and type(actual_native_history.get("records")) is list
            and len(actual_native_history["records"]) == 3
            and sum(
                record.get("genuine_process_count", -1)
                for record in actual_native_history["records"]
                if type(record) is dict
            ) == 39,
            "independently reauthenticate all 39 C, Rust, and failed Zig processes")
    root = activator.checked_private_root(
        arguments["activation_root"], spec.name, build=False,
    )
    raw_report, report_owner = activator.read_owned(
        root, "activation-report.json", arguments["activation_report_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    raw_receipt, receipt_owner = activator.read_owned(
        root, "activation-receipt.json", arguments["activation_receipt_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    report = activator.decode_document(raw_report, "exact real activation report")
    receipt = activator.decode_document(raw_receipt, "exact real activation receipt")
    require(report.get("preserved_version_two") == actual_native_history
            and receipt.get("preserved_version_two") == actual_native_history,
            "bind activation to the actual independently replayed native history")
    recorded_journal = report.get("recovery_journal")
    require(type(recorded_journal) is dict,
            "preserve the genuine pre-promotion owner-only recovery journal")
    raw_journal, journal_owner = activator.read_owned(
        root, "recovery-journal.json",
        checked_digest(recorded_journal.get("sha256"), "recovery journal"),
        maximum=MAX_REPORT_BYTES,
        exact_size=checked_positive_size(recorded_journal.get("size_bytes"),
                                         "recovery journal"),
        private=True,
    )
    strict_same_owner(journal_owner, recorded_journal,
                      "genuine private recovery-journal owner")
    journal = activator.decode_document(raw_journal,
                                        "actual pre-promotion recovery journal")
    activation_arguments = {
        "family": spec.name, "build_version": version,
        "activation_root": root,
        "activation_source_sha256": ACTIVATION_SOURCE_SHA256,
        "activation_protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
        "activation_report_sha256": arguments["activation_report_sha256"],
        "activation_receipt_sha256": arguments["activation_receipt_sha256"],
    }
    try:
        promotion = activator.validate_activation_documents(
            report, receipt, journal, arguments=activation_arguments,
        )
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the published versioned native activator rejected its full real proofs"
        ) from error
    require(type(promotion) is dict
            and promotion.get("schema") == ACTIVATION_SCHEMA + "-authenticated-promotion"
            and promotion.get("status") == "PASS"
            and promotion.get("family") == spec.name
            and promotion.get("build_version") == version
            and promotion.get("candidate_import_root") == str(ROOT),
            "reject substituted genuine source-owned dual-version promotion")
    provenance = promotion.get("source_build")
    require(type(provenance) is dict
            and provenance.get("build_version") == version
            and provenance.get("archive_sha256") == spec.build_archive_sha256
            and provenance.get("receipt_sha256") == spec.build_receipt_sha256
            and provenance.get("source_sha256") == spec.build_source_sha256
            and provenance.get("protocol_sha256") == spec.build_protocol_sha256
            and provenance.get("label") == spec.build_label
            and provenance.get("independent_fresh_phase_count") == 2
            and provenance.get("actual_versioned_symbol_streams_verified") is True
            and provenance.get("preserved_version_two_history_process_count") == 39,
            "reject missing, failed, relabeled, or cross-version native provenance")
    build_root = activator.checked_private_root(
        provenance.get("build_root"), spec.name,
        build=True, build_version=version,
    )
    archive, archive_owner = read_owned(
        ROOT, provenance["archive_relative"], spec.build_archive_sha256,
        maximum=MAX_ARCHIVE_BYTES,
    )
    build_receipt_raw, build_receipt_owner = read_owned(
        ROOT, provenance["receipt_relative"], spec.build_receipt_sha256,
        maximum=MAX_SOURCE_BYTES,
    )
    build_report = activator.decode_document(
        activator.bounded_gzip(archive), "genuine exact native source-build report"
    )
    build_receipt = activator.decode_document(
        build_receipt_raw, "genuine exact native source-build receipt"
    )
    build_arguments = {
        "family": spec.name, "build_version": version,
        "build_label": spec.build_label, "build_root": build_root,
        "build_source_sha256": spec.build_source_sha256,
        "build_protocol_sha256": spec.build_protocol_sha256,
        "build_report_sha256": spec.build_archive_sha256,
        "build_receipt_sha256": spec.build_receipt_sha256,
        "native_engine_sha256": spec.native_engine_sha256,
        "native_bridge_sha256": spec.native_bridge_sha256,
        "native_engine_bytes": spec.native_engine_bytes,
        "native_bridge_bytes": spec.native_bridge_bytes,
    }
    try:
        outputs = activator.validate_build_report(
            build_report, build_receipt, archive, build_arguments, owners,
        )
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "reject nonpassing receipt-only or mixed-version native source evidence"
        ) from error
    roles = {"extension"} if spec.name == "c" else {"engine", "bridge"}
    require(type(outputs) is dict and set(outputs) == roles,
            "authenticate every genuine source-built canonical native role")
    targets = promotion["canonical_targets"]
    try:
        intentions = activator.authenticate_promotion_intents(
            root, journal, journal_owner["sha256"],
            announced_targets=targets,
        )
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the genuine source-owned promotion-intent validator rejected a role"
        ) from error
    require(type(intentions) is dict and set(intentions) == roles,
            "require the full actual independently durable promotion-role closure")
    current_native: dict[str, dict[str, Any]] = {}
    phase_records: dict[str, list[dict[str, Any]]] = {}
    backup_owners: dict[str, dict[str, Any] | None] = {}
    backup_entries = promotion.get("backup_entries")
    require(type(backup_entries) is dict and set(backup_entries) == roles,
            "require all actual recoverable native role backup entries")
    for role in sorted(roles):
        target = targets[role]
        proof = intentions[role]
        output = outputs[role]
        require(type(target) is dict and type(proof) is dict
                and type(output) is dict
                and all(target.get(flag) is True for flag in PROMOTION_FLAGS)
                and target.get("sha256") == output.get("sha256")
                and target.get("size_bytes") == output.get("size_bytes"),
                "reject an unpromoted, altered, or non-source-built native role")
        checked_positive_size(target.get("size_bytes"), role + " native bytes")
        current = activator.current_canonical(target["relative"])
        require(type(current) is tuple and len(current) == 2,
                "require actual unchanged canonical source-built native bytes")
        strict_same_owner(current[1], target, "actual native owner " + role)
        require(activator.same_owner(current[1], target) is True,
                "the actual frozen activator rejected the canonical native inode")
        rich = target.get("promotion_intent")
        require(type(rich) is dict and type(proof.get("intent")) is dict,
                "retain original rich independently durable promotion evidence")
        strict_same_owner(proof["intent"], rich, "durable intention " + role)
        require(all(rich.get(flag) is True for flag in DURABLE_FLAGS)
                and type(rich.get("write_calls")) is int
                and rich["write_calls"] > 0
                and rich.get("mode") == 0o600,
                "authenticate actual rich intention flags and typed write counts")
        strict_same_owner(proof.get("target"), target,
                          "durable intention target " + role)
        phases = target.get("source_build_phases")
        require(type(phases) is list and len(phases) == 2,
                "require both actual distinct fresh source-build native phases")
        actual_phases: list[dict[str, Any]] = []
        for index, phase in enumerate(phases):
            require(type(phase) is dict,
                    "require a complete independently built native phase")
            expected_relative = ("reference-a", "reference-b")[index] \
                + "/native/" + output["file_name"]
            require(phase.get("relative") == expected_relative,
                    "never reuse, exchange, or relabel actual source-build phases")
            _, actual = activator.read_owned(
                build_root, expected_relative, output["sha256"],
                maximum=MAX_BINARY_BYTES,
                exact_size=checked_positive_size(output["size_bytes"],
                                                 role + " source-built bytes"),
                private=True,
            )
            strict_same_owner(actual, phase,
                              "actual independently built native phase " + role)
            actual_phases.append(actual)
        require((actual_phases[0]["device"], actual_phases[0]["inode"])
                != (actual_phases[1]["device"], actual_phases[1]["inode"]),
                "reject two phase records describing the same actual native inode")
        backup_entry = backup_entries[role]
        require(type(backup_entry) is dict
                and type(backup_entry.get("originally_present")) is bool,
                "preserve the true originally-present native target state")
        actual_backup = None
        if backup_entry["originally_present"]:
            rich_backup = backup_entry.get("backup")
            require(type(rich_backup) is dict,
                    "require the source-produced original native backup evidence")
            backup_relative = "backups/" + target["relative"]
            _, actual_backup = activator.read_owned(
                root, backup_relative,
                checked_digest(rich_backup.get("sha256"),
                               "original native backup " + role),
                maximum=MAX_BINARY_BYTES,
                exact_size=checked_positive_size(
                    rich_backup.get("size_bytes"),
                    "actual original native backup " + role,
                ),
                private=True,
            )
        backup_owners[role] = validate_backup_owner(
            backup_entry, actual_backup,
            spec=spec, role=role, activation_root=root, target=target,
        )
        current_native[role] = current[1]
        phase_records[role] = actual_phases
    records = report.get("source_owners")
    guards = report.get("original_guard_sources")
    require(type(records) is dict and set(records) == set(owners)
            and type(guards) is dict and set(guards) == set(ORIGINAL_GUARD_SOURCES),
            "require every actual candidate source and unchanged matcher guard")
    actual_source_owners: dict[str, dict[str, Any]] = {}
    source_sizes: dict[str, int] = {}
    for relative, digest in owners.items():
        _, observed = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
        strict_same_owner(observed, records[relative],
                          "actual source-build family owner " + relative)
        source_sizes[relative] = checked_positive_size(observed["size_bytes"],
                                                       relative)
        actual_source_owners[relative] = observed
    actual_guard_sizes: dict[str, int] = {}
    for relative, digest in sorted(ORIGINAL_GUARD_SOURCES.items()):
        _, observed = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
        strict_same_owner(observed, guards[relative],
                          "unchanged actual original matcher guard " + relative)
        actual_guard_sizes[relative] = checked_positive_size(
            observed["size_bytes"], relative,
        )
    require(actual_guard_sizes == preliminary["guard_sizes"],
            "an original matcher guard changed between exact source checks")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "reject an actual candidate imported before full crash-proof verification")
    return {
        "schema": SCHEMA + "-versioned-intent-authenticated-promotion",
        "status": "PASS", "family": spec.name, "build_version": version,
        "candidate_import_root": str(ROOT), "activation_root": root,
        "activation_report": report_owner,
        "activation_receipt": receipt_owner,
        "recovery_journal": journal_owner,
        "source_build": provenance,
        "independently_reauthenticated_version_two_history":
            actual_native_history,
        "source_build_archive": archive_owner,
        "source_build_receipt": build_receipt_owner,
        "source_owners": actual_source_owners,
        "source_sizes": source_sizes,
        "original_guard_owners": guards,
        "original_guard_sizes": actual_guard_sizes,
        "canonical_targets": targets,
        "current_native_owners": current_native,
        "native_phase_owners": phase_records,
        "promotion_intents": intentions,
        "backup_entries": backup_entries,
        "backup_owners": backup_owners,
        "original_matcher_guard_root_rebound": False,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
    }


def authenticate_prerequisites(arguments: Mapping[str, Any]) -> dict[str, Any]:
    preliminary = authenticate_support(arguments)
    historical = authenticate_preserved_failure()
    historical_rust = authenticate_preserved_rust_failure()
    spec = checked_family(arguments["family"])
    version = checked_build_version(arguments["build_version"])
    build_source = ("tools/reproduce_phase2_native_builds_v" + version + ".py")
    build_protocol = ("oracle/phase2/NATIVE-SOURCE-BUILDS-V"
                      + version + ".md")
    for relative, digest in (
        (build_source, spec.build_source_sha256),
        (build_protocol, spec.build_protocol_sha256),
    ):
        _, owner = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
        preliminary["support"][relative] = owner
    promotion = authenticate_activation(arguments, preliminary)
    original = _fresh_module(V1_SOURCE_RELATIVE, V1_SOURCE_SHA256)
    require(getattr(original, "SCHEMA", None)
            == "rebar-owned-candidate-subinterpreters-v1"
            and getattr(original, "REFERENCE_PROGRAM_SHA256", None)
            == ORIGINAL_PROGRAM_SHA256
            and getattr(original, "ADAPTED_PROGRAM_SHA256", None)
            == ADAPTED_PROGRAM_SHA256
            and getattr(original, "CASE_EXEC_COUNT", None) == CASE_EXECUTIONS
            and getattr(original, "INTERPRETER_COUNT", None) == INTERPRETER_COUNT
            and getattr(original, "PRIVATE_GUARD_SOURCES", None)
            == ORIGINAL_GUARD_SOURCES,
            "preserve the exact immutable original real-interpreter observer")
    previous_spec = original.FAMILIES.get(spec.name)
    require(previous_spec is not None and previous_spec.name == spec.name
            and previous_spec.adapter_module == spec.module
            and previous_spec.adapter_relative == spec.source_relative
            and previous_spec.engine_relative == spec.engine_relative
            and previous_spec.bridge_relative == spec.bridge_relative,
            "use only the exact genuine original independent candidate guard")
    return {
        "spec": spec, "previous_spec": previous_spec,
        "source_pins": source_pins(spec, arguments["owned_source_sha256"]),
        "support": preliminary["support"], "historical_failure": historical,
        "historical_rust_failure": historical_rust,
        "activation": promotion, "original": original,
        "pins": {
            "source": source_pins(spec, arguments["owned_source_sha256"])[
                spec.source_relative
            ],
            "native_engine": spec.native_engine_sha256,
            "native_bridge": spec.native_bridge_sha256,
        },
    }


def replace_unique(source: str, old: str, new: str, label: str) -> str:
    require(type(source) is str and type(old) is str and bool(old)
            and type(new) is str and source.count(old) == 1,
            "require one exact immutable original bootstrap marker: " + label)
    result = source.replace(old, new, 1)
    require(result.count(old) == new.count(old),
            "reject repeated or incomplete original bootstrap correction: " + label)
    return result


def repair_original_bootstrap(program: str, *,
                              original_support: Mapping[str, str],
                              support_sizes: Mapping[str, int],
                              source_owners: Mapping[str, str],
                              source_sizes: Mapping[str, int],
                              native_sizes: Mapping[str, int]) -> str:
    require(type(program) is str and program
            and type(original_support) is dict
            and original_support == ORIGINAL_GUARD_SOURCES
            and type(support_sizes) is dict
            and set(support_sizes) == set(original_support)
            and type(source_owners) is dict
            and type(source_sizes) is dict
            and set(source_sizes) == set(source_owners)
            and type(native_sizes) is dict
            and set(native_sizes) == {"engine", "bridge"},
            "require every original guard, family source, and native exact owner")
    for relative, size in (*support_sizes.items(), *source_sizes.items(),
                           *native_sizes.items()):
        checked_positive_size(size, relative)
    support_line = "_phase2_support = " + repr(
        dict(sorted(original_support.items()))
    ) + "\n"
    insertion = (support_line
                 + "_phase2_support_sizes = "
                 + repr(dict(sorted(support_sizes.items()))) + "\n"
                 + "_phase2_source_sizes = "
                 + repr(dict(sorted(source_sizes.items()))) + "\n"
                 + "_phase2_native_sizes = "
                 + repr(dict(sorted(native_sizes.items()))) + "\n")
    corrected = replace_unique(program, support_line, insertion,
                               "actual immutable original guard source sizes")
    source_maximum = str(MAX_SOURCE_BYTES)
    support_marker = (
        "for _phase2_relative, _phase2_digest in _phase2_support.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=" + source_maximum + ")\n"
    )
    corrected = replace_unique(
        corrected, support_marker,
        "for _phase2_relative, _phase2_digest in _phase2_support.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=_phase2_support_sizes[_phase2_relative])\n",
        "exact actual original guard-source sizes",
    )
    owner_marker = (
        "for _phase2_relative, _phase2_digest in "
        "_phase2_source_owners.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=" + source_maximum + ")\n"
    )
    corrected = replace_unique(
        corrected, owner_marker,
        "for _phase2_relative, _phase2_digest in "
        "_phase2_source_owners.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=_phase2_source_sizes[_phase2_relative])\n",
        "exact actual independently built native family source sizes",
    )
    for role in ("engine", "bridge"):
        original_limit = str(LEGACY_INTERPRETER_MAX_BINARY_BYTES)
        marker = ("_phase2_pins['native_" + role + "'], maximum="
                  + original_limit + ")")
        replacement = ("_phase2_pins['native_" + role
                       + "'], maximum=_phase2_native_sizes['" + role + "'])")
        corrected = replace_unique(
            corrected, marker, replacement,
            "exact actual " + role + " bytes within original 128-MiB guard cap",
        )
    require("maximum=" + str(LEGACY_INTERPRETER_MAX_BINARY_BYTES)
            not in corrected,
            "never pass the genuinely rejected 256-MiB cap into the original guard")
    try:
        ast.parse(corrected,
                  filename="<authentic-size-corrected-original-v5-bootstrap>")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise SubinterpreterGateError(
            "the exact original size-corrected genuine bootstrap is invalid"
        ) from error
    return corrected


def actual_bootstrap(context: Mapping[str, Any], *, owner: str) -> str:
    original = context["original"]
    spec = context["previous_spec"]
    promotion = context["activation"]
    original_source = original.interpreter_bootstrap_source(
        spec, context["pins"], promotion,
        context["source_pins"], owner=owner,
    )
    selected = checked_family(spec.name)
    engine_role = "extension" if selected.name == "c" else "engine"
    bridge_role = "extension" if selected.name == "c" else "bridge"
    return repair_original_bootstrap(
        original_source,
        original_support=dict(original.PRIVATE_GUARD_SOURCES),
        support_sizes=dict(promotion["original_guard_sizes"]),
        source_owners=dict(context["source_pins"]),
        source_sizes=dict(promotion["source_sizes"]),
        native_sizes={
            "engine": promotion["current_native_owners"][engine_role]["size_bytes"],
            "bridge": promotion["current_native_owners"][bridge_role]["size_bytes"],
        },
    )


def validate_actual_worker(value: Any, *, context: Mapping[str, Any],
                           baseline: Mapping[str, Any],
                           expected_pid: int) -> dict[str, Any]:
    require(type(value) is dict and value.get("schema") == SCHEMA + "-actual-worker"
            and value.get("status") == "PASS"
            and type(expected_pid) is int and expected_pid > 0
            and value.get("pid") == expected_pid,
            "require the genuine complete isolated nested V3 worker and actual PID")
    require(value.get("build_version") == context["spec"].build_version
            and value.get("historical_c_v5_failure")
            == context["historical_failure"]
            and value.get("historical_rust_v5_failure")
            == context["historical_rust_failure"]
            and value.get("versioned_canonical_activation")
            == context["activation"]
            and value.get("exact_owner_sizes_used") is True,
            "reject changed activation, actual native sizes, or concealed history")
    original = context["original"]
    projected = dict(value)
    projected["schema"] = original.SCHEMA + "-actual-worker"
    for field in ("build_version", "historical_c_v5_failure",
                  "historical_rust_v5_failure",
                  "versioned_canonical_activation", "exact_owner_sizes_used",
                  "preserved_v1_source_sha256", "preserved_v2_source_sha256"):
        projected.pop(field, None)
    try:
        original.validate_worker_document(
            projected, spec=context["previous_spec"], pins=context["pins"],
            original=baseline, expected_pid=expected_pid,
        )
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the immutable original 128-case and 394-call observer rejected V3"
        ) from error
    require(value.get("preserved_v1_source_sha256") == V1_SOURCE_SHA256
            and value.get("preserved_v2_source_sha256") == V2_SOURCE_SHA256
            and value.get("case_count") == CASE_COUNT
            and value.get("actual_case_interpreter_exec_calls") == CASE_EXECUTIONS
            and value.get("actual_initialization_interpreter_exec_calls")
            == INTERPRETER_COUNT
            and value.get("actual_guard_cleanup_interpreter_exec_calls")
            == INTERPRETER_COUNT,
            "preserve all actual original 128/394/11/11 interpreter observations")
    return value


def internal_worker(arguments: Mapping[str, Any]) -> dict[str, Any]:
    context = authenticate_prerequisites(arguments)
    original = context["original"]
    spec = context["previous_spec"]
    pins = context["pins"]
    activation = context["activation"]
    baseline = original.load_original_baseline()
    original.authenticate_path(
        Path(original.PINNED_INTERPRETERS), original.PINNED_INTERPRETERS_SHA256,
        maximum=MAX_SOURCE_BYTES,
    )
    public = importlib.import_module("concurrent.interpreters")
    require(type(public) is types.ModuleType and public.__spec__ is not None
            and os.path.abspath(public.__spec__.origin)
            == original.PINNED_INTERPRETERS
            and callable(getattr(public, "create", None))
            and callable(getattr(public, "list_all", None))
            and callable(getattr(public, "get_current", None))
            and callable(getattr(public.Interpreter, "exec", None))
            and callable(getattr(public.Interpreter, "close", None)),
            "load only the authentic frozen public CPython interpreter provider")
    program = original.compose_owned_program(baseline["original_program"],
                                             spec, pins)
    original_live = {int(item.id) for item in public.list_all()}
    main_id = int(public.get_current().id)
    original_locale = locale.setlocale(locale.LC_CTYPE)
    first = second = third = temporary = None
    created = destroyed = case_calls = init_calls = cleanup_calls = 0
    identities: dict[str, Any] = {
        "A": None, "B": None, "C": None, "temporary": [],
    }
    records: list[dict[str, Any]] = []
    peers: list[dict[str, Any]] = []
    repeats: list[dict[str, Any]] = []
    fresh: list[dict[str, Any]] = []
    pipes: list[dict[str, Any]] = []
    post_b: dict[str, Any] | None = None
    final_c: dict[str, Any] | None = None
    active_case: dict[str, Any] | None = None
    phase = "create-real-private-interpreter-A"
    primary: BaseException | None = None
    cleanup_failures: list[dict[str, Any]] = []
    prepared: set[int] = set()

    def prepare(interpreter: Any, owner: str) -> None:
        nonlocal init_calls
        init_calls += 1
        require(interpreter.exec(actual_bootstrap(context, owner=owner)) is None,
                "the exact-size genuine persistent original V5 guard failed")
        prepared.add(int(interpreter.id))

    def close(interpreter: Any, owner: str) -> None:
        nonlocal cleanup_calls, destroyed
        identity = int(interpreter.id)
        require(identity in {int(item.id) for item in public.list_all()},
                "a genuine interpreter disappeared before verified cleanup")
        if identity in prepared:
            cleanup_calls += 1
            require(interpreter.exec(original.interpreter_cleanup_source()) is None,
                    "the exact original persistent guard failed to restore")
            prepared.remove(identity)
        interpreter.close()
        destroyed += 1
        require(identity not in {int(item.id) for item in public.list_all()},
                "a real candidate subinterpreter remained alive after close")

    def execute(interpreter: Any, case: dict[str, Any], owner: str,
                expected: dict[str, Any]) -> dict[str, Any]:
        nonlocal case_calls
        case_calls += 1
        actual, ledger = original.observe_interpreter(
            interpreter, case=case, baseline=expected, owner=owner,
            main_id=main_id, source=baseline["source"],
            gate=baseline["gate"], program=program, spec=spec, pins=pins,
            private_root=activation["candidate_import_root"],
        )
        pipes.append(ledger)
        return actual

    try:
        first = public.create()
        created += 1
        identities["A"] = int(first.id)
        phase = "create-real-simultaneous-private-interpreter-B"
        second = public.create()
        created += 1
        identities["B"] = int(second.id)
        require(len({main_id, identities["A"], identities["B"]}) == 3,
                "require two distinct simultaneously live genuine interpreters")
        phase = "install-exact-size-real-persistent-original-V5-in-A"
        prepare(first, "A")
        phase = "install-exact-size-real-persistent-original-V5-in-B"
        prepare(second, "B")
        for case, expected in zip(baseline["matrix"], baseline["records"],
                                  strict=True):
            active_case = case
            phase = "execute-actual-simultaneous-A"
            left = execute(first, case, "A", expected)
            records.append(left)
            phase = "execute-actual-simultaneous-B"
            middle = execute(second, case, "B", expected)
            peers.append(middle)
            phase = "execute-actual-repeated-A-after-B"
            right = execute(first, case, "A", expected)
            repeats.append(right)
            require(canonical(left) == canonical(middle)
                    and canonical(left) == canonical(right),
                    "the genuine complete original A/B/A observations differ")
        repeated_cases = [
            case for case in baseline["matrix"]
            if case["cohort"] == "repeated-interpreter-creation-and-destruction"
        ]
        require(len(repeated_cases) == FRESH_INTERPRETER_CASE_COUNT,
                "preserve all eight actual fresh original interpreter cases")
        for case in repeated_cases:
            active_case = case
            phase = "create-real-independent-fresh-interpreter"
            temporary = public.create()
            created += 1
            identities["temporary"].append(int(temporary.id))
            phase = "install-exact-size-original-V5-in-fresh-interpreter"
            prepare(temporary, "C")
            phase = "execute-real-independent-fresh-interpreter"
            fresh.append(execute(
                temporary, case, "C", baseline["records"][case["ordinal"]],
            ))
            phase = "cleanup-real-independent-fresh-interpreter"
            close(temporary, "temporary")
            temporary = None
        phase = "restore-real-original-V5-and-close-B"
        close(second, "B")
        second = None
        phase = "execute-real-A-after-actual-B-close"
        active_case = baseline["matrix"][-1]
        post_b = execute(first, active_case, "A", baseline["records"][-1])
        phase = "restore-real-original-V5-and-close-A"
        close(first, "A")
        first = None
        phase = "create-genuine-independent-final-interpreter-C"
        third = public.create()
        created += 1
        identities["C"] = int(third.id)
        phase = "install-exact-size-original-V5-in-final-C"
        prepare(third, "C")
        phase = "execute-genuine-independent-final-C"
        final_c = execute(third, active_case, "C", baseline["records"][-1])
        phase = "restore-real-original-V5-and-close-C"
        close(third, "C")
        third = None
        require(created == destroyed == init_calls == cleanup_calls
                == INTERPRETER_COUNT and case_calls == CASE_EXECUTIONS
                and not prepared,
                "preserve the complete genuine 394/11/11 original lifecycle")
    except BaseException as error:
        primary = error
    finally:
        for owner, interpreter in (("temporary", temporary), ("C", third),
                                   ("B", second), ("A", first)):
            if interpreter is None:
                continue
            try:
                close(interpreter, owner)
            except BaseException as error:
                cleanup_failures.append({
                    "role": owner, "interpreter_id": int(interpreter.id),
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                })
                try:
                    interpreter.close()
                    destroyed += 1
                except BaseException as final_error:
                    cleanup_failures.append({
                        "role": owner, "interpreter_id": int(interpreter.id),
                        "error_type": type(final_error).__name__,
                        "error_message": str(final_error),
                    })
    if primary is not None or cleanup_failures:
        details: dict[str, Any] = {
            "status": "FAIL", "candidate_family": spec.name,
            "build_version": context["spec"].build_version,
            "active_phase": phase, "active_case": active_case,
            "actual_interpreter_ids": identities,
            "completed_a_records": records,
            "completed_b_records": peers,
            "completed_repeated_a_records": repeats,
            "completed_repeated_creation_records": fresh,
            "actual_post_b_close_a_record": post_b,
            "actual_fresh_c_record": final_c,
            "actual_case_interpreter_exec_calls": case_calls,
            "actual_initialization_interpreter_exec_calls": init_calls,
            "actual_guard_cleanup_interpreter_exec_calls": cleanup_calls,
            "actual_interpreters_created": created,
            "actual_interpreters_destroyed": destroyed,
            "actual_prepared_interpreter_ids": sorted(prepared),
            "pipe_ledgers": pipes, "cleanup_failures": cleanup_failures,
        }
        if primary is not None:
            details["error_type"] = type(primary).__name__
            details["error_message"] = str(primary)
            if hasattr(primary, "details") and type(primary.details) is dict:
                details["actual_case_failure"] = primary.details
        raise ActualCaseFailure(
            "the genuine exact-size isolated native interpreter lifecycle failed",
            details,
        ) from primary
    restored = {int(item.id) for item in public.list_all()}
    require(restored == original_live
            and locale.setlocale(locale.LC_CTYPE) == original_locale,
            "restore every real Python interpreter and the exact original locale")
    report: dict[str, Any] = {
        "schema": SCHEMA + "-actual-worker", "status": "PASS",
        "pid": os.getpid(), "python": "3.14.6",
        "candidate_family": spec.name,
        "candidate_module": spec.adapter_module,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "reference_records_sha256": REFERENCE_SHA256,
        "projected_reference_records_sha256": PROJECTED_SHA256,
        "adapted_program_sha256": ADAPTED_PROGRAM_SHA256,
        "adapted_program_bytes": 12759,
        "records": records, "peer_records": peers,
        "repeated_a_records": repeats,
        "repeated_creation_records": fresh,
        "actual_post_b_close_a_record": post_b,
        "actual_fresh_c_record": final_c,
        "actual_interpreter_ids": identities,
        "actual_case_interpreter_exec_calls": case_calls,
        "actual_initialization_interpreter_exec_calls": init_calls,
        "actual_guard_cleanup_interpreter_exec_calls": cleanup_calls,
        "actual_interpreters_created": created,
        "actual_interpreters_destroyed": destroyed,
        "fresh_interpreter_case_count": len(fresh),
        "simultaneous_interpreters_verified": True,
        "b_closed_before_a_reexecution": True,
        "fresh_c_verified": True,
        "persistent_original_v5_per_interpreter": True,
        "all_real_pipes_read_to_eof": all(
            ledger["reached_eof"] for ledger in pipes
        ),
        "all_real_pipe_descriptors_closed": all(
            ledger["all_descriptors_closed"] for ledger in pipes
        ),
        "pipe_ledgers": pipes,
        "interpreter_live_set_restored": True,
        "locale_restored": True,
        "original_matcher_calls": sum(
            row["original_matcher_calls"]
            for row in records + peers + repeats + fresh + [post_b, final_c]
        ),
        "external_engine_imports": sum(
            row["external_engine_imports"]
            for row in records + peers + repeats + fresh + [post_b, final_c]
        ),
        "cross_candidate_imports": sum(
            row["cross_candidate_imports"]
            for row in records + peers + repeats + fresh + [post_b, final_c]
        ),
        "foreign_native_loads": sum(
            row["foreign_native_loads"]
            for row in records + peers + repeats + fresh + [post_b, final_c]
        ),
        "source_build_v2": activation["source_build"],
        "canonical_activation": activation,
        "reference_process_ids": baseline["reference_process_ids"],
        "build_version": context["spec"].build_version,
        "versioned_canonical_activation": activation,
        "historical_c_v5_failure": context["historical_failure"],
        "historical_rust_v5_failure": context["historical_rust_failure"],
        "exact_owner_sizes_used": True,
        "preserved_v1_source_sha256": V1_SOURCE_SHA256,
        "preserved_v2_source_sha256": V2_SOURCE_SHA256,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }
    return validate_actual_worker(report, context=context,
                                  baseline=baseline, expected_pid=os.getpid())


def evidence_names(spec: FamilySpec, label: str,
                   *, failure: bool) -> tuple[str, str]:
    stem = "owned-candidate-subinterpreters-v3-" + spec.name + "-" \
        + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_evidence_fresh(spec: FamilySpec, label: str) -> None:
    root = ROOT / EVIDENCE_RELATIVE
    observed = os.lstat(str(root))
    require(stat.S_ISDIR(observed.st_mode) and not stat.S_ISLNK(observed.st_mode),
            "require the exact genuine non-symlinked phase-two evidence root")
    for failure in (False, True):
        for name in evidence_names(spec, label, failure=failure):
            try:
                os.lstat(str(root / name))
            except FileNotFoundError:
                continue
            raise SubinterpreterGateError(
                "refuse to replace immutable existing nested V3 evidence: " + name
            )


def worker_arguments(arguments: Mapping[str, Any]) -> list[str]:
    ordered = (
        ("--family", "family"),
        ("--build-version", "build_version"),
        ("--label", "label"),
        ("--candidate-source-sha256", "candidate_source_sha256"),
        ("--source-sha256", "source_sha256"),
        ("--protocol-sha256", "protocol_sha256"),
        ("--explanation-sha256", "explanation_sha256"),
        ("--v1-source-sha256", "v1_source_sha256"),
        ("--v1-protocol-sha256", "v1_protocol_sha256"),
        ("--v1-explanation-sha256", "v1_explanation_sha256"),
        ("--v2-source-sha256", "v2_source_sha256"),
        ("--v2-protocol-sha256", "v2_protocol_sha256"),
        ("--v2-explanation-sha256", "v2_explanation_sha256"),
        ("--build-label", "build_label"),
        ("--build-source-sha256", "build_source_sha256"),
        ("--build-protocol-sha256", "build_protocol_sha256"),
        ("--build-archive-sha256", "build_archive_sha256"),
        ("--build-receipt-sha256", "build_receipt_sha256"),
        ("--activation-root", "activation_root"),
        ("--activation-source-sha256", "activation_source_sha256"),
        ("--activation-protocol-sha256", "activation_protocol_sha256"),
        ("--activation-report-sha256", "activation_report_sha256"),
        ("--activation-receipt-sha256", "activation_receipt_sha256"),
        ("--native-engine-sha256", "native_engine_sha256"),
        ("--native-bridge-sha256", "native_bridge_sha256"),
        ("--native-engine-bytes", "native_engine_bytes"),
        ("--native-bridge-bytes", "native_bridge_bytes"),
    )
    result = [PINNED_PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE),
              "--internal-worker"]
    for option, key in ordered:
        result.extend((option, str(arguments[key])))
    for owner in arguments["owned_source_sha256"]:
        result.extend(("--owned-source-sha256", owner))
    return result


def publish_report(report: dict[str, Any], spec: FamilySpec, label: str,
                   original: types.ModuleType) -> dict[str, Any]:
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(spec, label, failure=failed)
    plain = canonical_line(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "preserve a complete bounded actual nested interpreter report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(len(compressed) <= MAX_ARCHIVE_BYTES,
            "preserve the complete deterministic actual interpreter archive")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(str(ROOT / EVIDENCE_RELATIVE), flags)
    try:
        archive = original.write_fresh_evidence(directory, archive_name,
                                               compressed)
        os.fsync(directory)
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "status": "PASS",
            "result_status": report["status"],
            "candidate_family": spec.name,
            "build_version": spec.build_version,
            "label": label,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "explanation_sha256": report["explanation_sha256"],
            "activation_source_sha256": ACTIVATION_SOURCE_SHA256,
            "activation_protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
            "activation_report_sha256": report["activation_report_sha256"],
            "activation_receipt_sha256": report["activation_receipt_sha256"],
            "archive_relative": archive["relative"],
            "archive_sha256": archive["sha256"],
            "archive_bytes": archive["bytes"],
            "uncompressed_sha256": sha256(plain),
            "uncompressed_bytes": len(plain),
            "archive_publication": archive,
            "archive_directory_fsync_completed": True,
            "supplemental_case_count": CASE_COUNT if not failed else
                report.get("actual_successful_supplemental_cases", 0),
            "phase1_case_execution_denominator": PHASE1_CASE_COUNT,
            "supplemental_cases_added_to_phase1_denominator": False,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "receipt_self_publication": "NOT CLAIMED",
        }
        evidence = original.write_fresh_evidence(
            directory, receipt_name, canonical_line(receipt),
        )
        os.fsync(directory)
    finally:
        os.close(directory)
    return {
        "schema": SCHEMA + "-published-candidate-result",
        "status": report["status"],
        "candidate_family": spec.name,
        "build_version": spec.build_version,
        "label": label,
        "archive": archive,
        "receipt": evidence,
        "failure_preserved": failed,
        "directory_fsync_completed": True,
        "supplemental_case_count": CASE_COUNT if not failed else
            report.get("actual_successful_supplemental_cases", 0),
        "phase1_case_execution_denominator": PHASE1_CASE_COUNT,
        "supplemental_cases_added_to_phase1_denominator": False,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def run_candidate(arguments: Mapping[str, Any]) -> dict[str, Any]:
    context = authenticate_prerequisites(arguments)
    spec = context["spec"]
    original = context["original"]
    label = checked_label(arguments["label"])
    ensure_evidence_fresh(spec, label)
    report: dict[str, Any] = {
        "schema": SCHEMA + "-candidate-evaluation", "status": "FAIL",
        "candidate_family": spec.name,
        "build_version": spec.build_version,
        "label": label,
        "source_sha256": arguments["source_sha256"],
        "protocol_sha256": arguments["protocol_sha256"],
        "explanation_sha256": arguments["explanation_sha256"],
        "activation_report_sha256": arguments["activation_report_sha256"],
        "activation_receipt_sha256": arguments["activation_receipt_sha256"],
        "corrected_activation": context["activation"],
        "preserved_historical_failure": context["historical_failure"],
        "preserved_historical_rust_failure": context["historical_rust_failure"],
        "static_independence_audit": None,
        "worker": None,
        "worker_process": None,
        "failure": None,
        "actual_successful_supplemental_cases": 0,
        "phase1_case_execution_denominator": PHASE1_CASE_COUNT,
        "supplemental_cases_added_to_phase1_denominator": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    process: subprocess.Popen[bytes] | None = None
    try:
        report["static_independence_audit"] = original.invoke_static_independence_audit(
            context["previous_spec"], context["source_pins"],
        )
        process = subprocess.Popen(
            worker_arguments(arguments), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(ROOT), shell=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
        captured = original.capture_process(
            process, "genuine exact-size versioned 394-call subinterpreter worker"
        )
        report["worker_process"] = {
            key: value for key, value in captured.items()
            if key not in {"stdout_bytes", "stderr_bytes"}
        }
        require(captured.get("timed_out") is False
                and process.returncode == 0
                and captured.get("stderr_bytes") == b"",
                "preserve an actual crashed, failed, or timed-out worker")
        worker = decode_document(captured.get("stdout_bytes"),
                                 "genuine nested V3 actual worker output",
                                 canonical_required=True)
        baseline = original.load_original_baseline()
        report["worker"] = validate_actual_worker(
            worker, context=context, baseline=baseline,
            expected_pid=process.pid,
        )
        report["actual_successful_supplemental_cases"] = CASE_COUNT
        report["status"] = "PASS"
    except BaseException as error:
        failure: dict[str, Any] = {
            "error_type": type(error).__name__, "error_message": str(error),
        }
        if hasattr(error, "details") and type(error.details) is dict:
            failure["actual_failure"] = error.details
        if process is not None:
            failure["pid"] = process.pid
            failure["returncode"] = process.returncode
        report["failure"] = failure
    return publish_report(report, spec, label, original)


def project_reference(record: Any) -> dict[str, Any]:
    required = {
        "case_id", "cohort", "ordinal", "seed", "variant", "status",
        "actual_exec", "candidate_imports", "locale_unchanged",
        "stdlib_origin_verified", "pinned_executable_verified", "observation",
    }
    require(type(record) is dict and set(record) == required
            and type(record.get("candidate_imports")) is int
            and record["candidate_imports"] == 0
            and record.get("stdlib_origin_verified") is True
            and record.get("actual_exec") is True
            and record.get("locale_unchanged") is True
            and record.get("pinned_executable_verified") is True
            and record.get("status") == "PASS"
            and type(record.get("observation")) is dict,
            "retain the exact complete immutable original interpreter reference")
    result = {
        key: value for key, value in record.items()
        if key not in {"candidate_imports", "stdlib_origin_verified"}
    }
    observed = dict(record["observation"])
    for old, replacement in RENAMES.items():
        if old in observed:
            require(replacement not in observed,
                    "reject an original matching-owner rename collision")
            observed[replacement] = observed.pop(old)
    result["observation"] = observed
    return result


def validate_candidate_observation(row: Any, baseline: Any,
                                   spec: FamilySpec,
                                   pins: Mapping[str, str]) -> dict[str, Any]:
    fields = {
        "case_id", "cohort", "ordinal", "seed", "variant", "status",
        "actual_exec", "locale_unchanged", "pinned_executable_verified",
        "observation", "candidate_family", "candidate_module",
        "candidate_source_sha256", "candidate_engine_sha256",
        "candidate_bridge_sha256", "candidate_origin_verified",
        "candidate_import_count", "original_matcher_calls",
        "external_engine_imports", "cross_candidate_imports",
        "foreign_native_loads",
    }
    require(type(row) is dict and set(row) == fields
            and row.get("candidate_family") == spec.name
            and row.get("candidate_module") == spec.module
            and row.get("candidate_origin_verified") is True
            and type(row.get("candidate_import_count")) is int
            and row["candidate_import_count"] >= 1,
            "preserve complete independent candidate and native provenance")
    for field, key in (
        ("candidate_source_sha256", "source"),
        ("candidate_engine_sha256", "engine"),
        ("candidate_bridge_sha256", "bridge"),
    ):
        require(row.get(field) == checked_digest(pins.get(key), field),
                "reject a changed genuine candidate owner: " + field)
    require((row["candidate_engine_sha256"]
             == row["candidate_bridge_sha256"]) is (spec.name == "c"),
            "only C may use one exact engine-and-bridge native owner")
    for field in ("original_matcher_calls", "external_engine_imports",
                  "cross_candidate_imports", "foreign_native_loads"):
        require(type(row.get(field)) is int and row[field] == 0,
                "reject stdlib, external engine, sibling, or FFI delegation")
    expected = project_reference(baseline)
    actual = {key: row[key] for key in expected}
    require(canonical(actual) == canonical(expected),
            "preserve every authentic ordered original interpreter observation")
    return actual


class SourceOnlyBoundary:
    """Actively prohibit every genuine effect during synthetic verification."""

    def __init__(self) -> None:
        self.attempts: dict[str, int] = {
            "file_reads": 0, "file_writes": 0,
            "descriptor_reads": 0, "descriptor_writes": 0,
            "pipes": 0, "processes": 0, "threads": 0,
            "candidate_imports": 0, "interpreter_imports": 0,
            "activation_imports": 0, "legacy_recorder_imports": 0,
            "dynamic_imports": 0, "native_library_loads": 0,
            "audit_hooks": 0, "locale_changes": 0,
            "clock_samples": 0, "garbage_collections": 0,
            "network_requests": 0, "hidden_cases_read": 0,
            "benchmark_files_read": 0,
        }
        self._stack = contextlib.ExitStack()
        self._before: frozenset[str] = frozenset()

    def blocked(self, category: str) -> Callable[..., Any]:
        require(category in self.attempts, "require a named synthetic boundary")

        def stop(*arguments: Any, **keywords: Any) -> Any:
            self.attempts[category] += 1
            raise SourceOnlyViolation("source-only blocked " + category)

        return stop

    def patch(self, target: Any, name: str, category: str) -> None:
        if not hasattr(target, name):
            return
        previous = getattr(target, name)
        self._stack.callback(setattr, target, name, previous)
        setattr(target, name, self.blocked(category))

    def __enter__(self) -> SourceOnlyBoundary:
        self._before = frozenset(sys.modules)
        previous_import = builtins.__import__

        def guarded_import(name: Any, globals: Any = None,
                           locals: Any = None, fromlist: Any = (),
                           level: int = 0) -> Any:
            if type(name) is str and (
                name == "candidates" or name.startswith("candidates.")
            ):
                return self.blocked("candidate_imports")()
            if type(name) is str and (
                name == "concurrent.interpreters"
                or name.startswith("concurrent.interpreters.")
                or name in {"_interpreters", "_interpqueues", "_interpchannels"}
                or (name == "concurrent" and fromlist is not None
                    and any(item == "interpreters" for item in fromlist))
            ):
                return self.blocked("interpreter_imports")()
            if type(name) is str and (
                name in {"ctypes", "_ctypes", "cffi", "_cffi_backend"}
                or name.startswith(("ctypes.", "cffi."))
            ):
                return self.blocked("native_library_loads")()
            if type(name) is str and (
                name == "socket" or name.startswith("socket.")
            ):
                return self.blocked("network_requests")()
            if type(name) is str and (
                name == "multiprocessing" or name.startswith("multiprocessing.")
            ):
                return self.blocked("processes")()
            if name == "tools.activate_verified_native_candidate_v2":
                return self.blocked("activation_imports")()
            if name in {
                "tools.run_owned_candidate_subinterpreters_v1",
                "tools.run_owned_candidate_subinterpreters_v2",
            }:
                return self.blocked("legacy_recorder_imports")()
            return previous_import(name, globals, locals, fromlist, level)

        self._stack.callback(setattr, builtins, "__import__", previous_import)
        builtins.__import__ = guarded_import
        for target, name in ((builtins, "open"), (io, "open"), (io, "open_code")):
            self.patch(target, name, "file_reads")
        for name in ("open", "stat", "lstat", "scandir", "listdir", "access"):
            self.patch(os, name, "file_reads")
        self.patch(os, "read", "descriptor_reads")
        self.patch(os, "pipe", "pipes")
        for name in ("write", "unlink", "remove", "rename", "replace", "mkdir",
                     "rmdir", "fsync", "fdatasync", "chmod"):
            self.patch(os, name, "descriptor_writes")
        for name in ("open", "read_bytes", "read_text", "exists", "stat",
                     "lstat", "resolve", "glob", "rglob", "iterdir"):
            self.patch(Path, name, "file_reads")
        for name in ("write_bytes", "write_text", "mkdir", "unlink", "rename",
                     "replace", "touch", "chmod"):
            self.patch(Path, name, "file_writes")
        self.patch(importlib, "import_module", "dynamic_imports")
        for name in ("Popen", "run"):
            self.patch(subprocess, name, "processes")
        for name in ("system", "popen", "fork", "forkpty", "posix_spawn",
                     "posix_spawnp", "spawnv", "spawnve", "spawnvp",
                     "spawnvpe", "execv", "execve", "execvp", "execvpe"):
            self.patch(os, name, "processes")
        self.patch(threading.Thread, "start", "threads")
        self.patch(sys, "addaudithook", "audit_hooks")
        self.patch(locale, "setlocale", "locale_changes")
        self.patch(gc, "collect", "garbage_collections")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            self.patch(time, name, "clock_samples")
        ctypes_module = sys.modules.get("ctypes")
        if ctypes_module is not None:
            self.patch(ctypes_module, "CDLL", "native_library_loads")
            self.patch(ctypes_module, "PyDLL", "native_library_loads")
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> None:
        self._stack.close()
        added = set(sys.modules) - self._before
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in added),
                "source-only controls imported an independently owned candidate")
        require(not any(name == "concurrent.interpreters"
                        or name.startswith("concurrent.interpreters.")
                        or name in {"_interpreters", "_interpqueues",
                                    "_interpchannels"} for name in added),
                "source-only controls created or imported a real interpreter")
        require("tools.activate_verified_native_candidate_v2" not in added
                and "tools.run_owned_candidate_subinterpreters_v1" not in added
                and "tools.run_owned_candidate_subinterpreters_v2" not in added,
                "source-only controls imported actual frozen build or guard owners")


def synthetic_case(index: int) -> dict[str, Any]:
    require(type(index) is int and 0 <= index < CASE_COUNT,
            "require one frozen ordered synthetic case")
    return {
        "case_id": "synthetic-v3-" + str(index).zfill(3),
        "cohort": ("repeated-interpreter-creation-and-destruction"
                   if index < FRESH_INTERPRETER_CASE_COUNT
                   else "synthetic-cohort-" + str(index // 8)),
        "ordinal": index,
        "seed": 2_000_000 + index,
        "variant": index % 8,
        "status": "PASS",
        "actual_exec": True,
        "candidate_imports": 0,
        "locale_unchanged": True,
        "stdlib_origin_verified": True,
        "pinned_executable_verified": True,
        "observation": {
            "owner_state_intact": True,
            **{name: True for name in RENAMES},
            "captured_index": index,
        },
    }


def synthetic_pins(spec: FamilySpec) -> dict[str, str]:
    source = sha256((spec.name + ":source").encode("ascii"))
    engine = sha256((spec.name + ":engine").encode("ascii"))
    bridge = (engine if spec.name == "c"
              else sha256((spec.name + ":bridge").encode("ascii")))
    return {"source": source, "engine": engine, "bridge": bridge}


def synthetic_candidate(index: int, spec: FamilySpec) -> dict[str, Any]:
    pins = synthetic_pins(spec)
    return {
        **project_reference(synthetic_case(index)),
        "candidate_family": spec.name,
        "candidate_module": spec.module,
        "candidate_source_sha256": pins["source"],
        "candidate_engine_sha256": pins["engine"],
        "candidate_bridge_sha256": pins["bridge"],
        "candidate_origin_verified": True,
        "candidate_import_count": 1,
        "original_matcher_calls": 0,
        "external_engine_imports": 0,
        "cross_candidate_imports": 0,
        "foreign_native_loads": 0,
    }


def synthetic_arguments(spec: FamilySpec) -> list[str]:
    result = [
        "--record-candidate",
        "--family", spec.name,
        "--build-version", spec.build_version,
        "--label", "synthetic-v3",
        "--candidate-source-sha256", ADAPTER_SOURCE_SHA256[spec.name],
        "--source-sha256", "a" * 64,
        "--protocol-sha256", "b" * 64,
        "--explanation-sha256", "c" * 64,
        "--v1-source-sha256", V1_SOURCE_SHA256,
        "--v1-protocol-sha256", V1_PROTOCOL_SHA256,
        "--v1-explanation-sha256", V1_EXPLANATION_SHA256,
        "--v2-source-sha256", V2_SOURCE_SHA256,
        "--v2-protocol-sha256", V2_PROTOCOL_SHA256,
        "--v2-explanation-sha256", V2_EXPLANATION_SHA256,
        "--build-label", spec.build_label,
        "--build-source-sha256", spec.build_source_sha256,
        "--build-protocol-sha256", spec.build_protocol_sha256,
        "--build-archive-sha256", spec.build_archive_sha256,
        "--build-receipt-sha256", spec.build_receipt_sha256,
        "--activation-root", ACTIVATION_PREFIX + spec.name + "-synthetic",
        "--activation-source-sha256", ACTIVATION_SOURCE_SHA256,
        "--activation-protocol-sha256", ACTIVATION_PROTOCOL_SHA256,
        "--activation-report-sha256", "d" * 64,
        "--activation-receipt-sha256", "e" * 64,
        "--native-engine-sha256", spec.native_engine_sha256,
        "--native-bridge-sha256", spec.native_bridge_sha256,
        "--native-engine-bytes", str(spec.native_engine_bytes),
        "--native-bridge-bytes", str(spec.native_bridge_bytes),
    ]
    for relative in spec.owners:
        digest = (ADAPTER_SOURCE_SHA256[spec.name]
                  if relative == spec.source_relative
                  else sha256(relative.encode("ascii")))
        result.extend(("--owned-source-sha256",
                       relative + "=" + digest))
    return result


def synthetic_owner(*, role: str, rich: bool) -> dict[str, Any]:
    owner = {
        "relative": "promotion-intent-" + role + ".json",
        "path": "/tmp/rebar-phase2-verified-native-activation-v2-c-synthetic/"
                + "promotion-intent-" + role + ".json",
        "sha256": sha256(("intention:" + role).encode("ascii")),
        "size_bytes": 871,
        "device": 2064,
        "inode": 4001,
        "mode": 0o600,
    }
    if rich:
        owner.update({name: True for name in DURABLE_FLAGS})
        owner["write_calls"] = 1
    return owner


def synthetic_backup_bundle(spec: FamilySpec,
                            role: str) -> dict[str, Any]:
    roles = {"extension"} if spec.name == "c" else {"engine", "bridge"}
    require(role in roles, "select one genuine synthetic native backup role")
    relative = (spec.engine_relative if role in {"extension", "engine"}
                else spec.bridge_relative)
    root = ACTIVATION_PREFIX + spec.name + "-synthetic"
    actual_digest = (spec.native_engine_sha256
                     if role in {"extension", "engine"}
                     else spec.native_bridge_sha256)
    actual_size = (spec.native_engine_bytes
                   if role in {"extension", "engine"}
                   else spec.native_bridge_bytes)
    target = {
        "relative": relative, "path": str(ROOT / relative),
        "sha256": actual_digest, "size_bytes": actual_size,
        "device": 2064, "inode": 30_001, "mode": 0o755,
    }
    original_digest = sha256((spec.name + ":original:" + role).encode("ascii"))
    original = {
        "relative": relative, "path": str(ROOT / relative),
        "sha256": original_digest, "size_bytes": 913,
        "device": 2064, "inode": 30_000, "mode": 0o755,
    }
    backup_relative = "backups/" + relative
    backup = {
        "relative": backup_relative, "path": root + "/" + backup_relative,
        "sha256": original_digest, "size_bytes": 913,
        "device": 2064, "inode": 80_001, "mode": 0o600,
        "exclusive_creation": True, "same_inode_readback_verified": True,
        "file_fsync_completed": True, "write_calls": 1,
    }
    observed = {key: backup[key] for key in OWNER_FIELDS}
    entry = {
        "role": role, "target_relative": relative,
        "target_path": str(ROOT / relative), "originally_present": True,
        "original_owner": original, "backup": backup,
        "promoted_sha256": actual_digest,
        "promoted_size_bytes": actual_size,
    }
    return {"entry": entry, "observed": observed, "target": target,
            "activation_root": root}


def synthetic_bootstrap(spec: FamilySpec) -> tuple[str, dict[str, int],
                                                       dict[str, int]]:
    support = dict(sorted(ORIGINAL_GUARD_SOURCES.items()))
    own = {relative: sha256(relative.encode("ascii"))
           for relative in spec.owners}
    program = (
        "_phase2_support = " + repr(support) + "\n"
        "for _phase2_relative, _phase2_digest in _phase2_support.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=" + str(MAX_SOURCE_BYTES) + ")\n"
        "for _phase2_relative, _phase2_digest in _phase2_source_owners.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=" + str(MAX_SOURCE_BYTES) + ")\n"
        "_phase2_v5.read_owned(_phase2_spec.engine_relative, "
        "_phase2_pins['native_engine'], maximum="
        + str(LEGACY_INTERPRETER_MAX_BINARY_BYTES) + ")\n"
        "_phase2_v5.read_owned(_phase2_spec.bridge_relative, "
        "_phase2_pins['native_bridge'], maximum="
        + str(LEGACY_INTERPRETER_MAX_BINARY_BYTES) + ")\n"
    )
    guard_sizes = {relative: 101 + index
                   for index, relative in enumerate(support)}
    source_sizes = {relative: 201 + index
                    for index, relative in enumerate(spec.owners)}
    repaired = repair_original_bootstrap(
        program,
        original_support=support,
        support_sizes=guard_sizes,
        source_owners=own,
        source_sizes=source_sizes,
        native_sizes={"engine": spec.native_engine_bytes,
                      "bridge": spec.native_bridge_bytes},
    )
    return repaired, guard_sizes, source_sizes


def self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "require one uniquely named synthetic positive control")
        require(condition is True, "a genuine source-only control failed: " + name)
        accepted.append(name)

    def refuse(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "require one uniquely named synthetic hostile control")
        try:
            action()
        except (SubinterpreterGateError, OSError, ValueError, TypeError,
                KeyError, AttributeError, UnicodeError, RecursionError,
                OverflowError, binascii.Error):
            rejected.append(name)
            return
        raise SubinterpreterGateError(
            "an actual hostile synthetic interpreter control escaped: " + name
        )

    with SourceOnlyBoundary() as boundary:
        document = synthetic_protocol()
        accept("strict-complete-original-frozen-protocol",
               validate_protocol(document) is document)
        accept("immutable-original-p0-case-denominator",
               document["phase1"]["case_execution_denominator"]
               == PHASE1_CASE_COUNT
               and document["phase1"]
               ["supplemental_cases_added_to_phase1_denominator"] is False)
        accept("preserve-all-three-genuine-source-built-native-families",
               set(document["candidate_families"]) == {"c", "rust", "zig"})
        accept("actual-version-two-c-and-rust-version-three-zig",
               document["candidate_families"]["c"]["build_version"] == "2"
               and document["candidate_families"]["rust"]["build_version"] == "2"
               and document["candidate_families"]["zig"]["build_version"] == "3")
        accept("genuine-pushed-dual-version-activation-source",
               document["corrected_canonical_activation"]["source_sha256"]
               == ACTIVATION_SOURCE_SHA256)
        accept("all-seven-typed-independent-owner-fields",
               tuple(document["corrected_canonical_activation"]
                     ["typed_identity_fields"]) == OWNER_FIELDS)
        accept("all-four-independently-durable-publication-flags",
               tuple(document["corrected_canonical_activation"]
                     ["independently_authenticated_durability_flags"])
               == DURABLE_FLAGS)
        accept("source-owned-revalidation-of-all-39-real-build-processes",
               document["corrected_canonical_activation"]
               ["independently_reauthenticated_prior_build_process_count"] == 39)
        accept("real-original-backup-bytes-and-inodes-are-required",
               document["corrected_canonical_activation"]
               ["actual_original_backup_bytes_required"] is True
               and document["corrected_canonical_activation"]
               ["actual_original_backup_inode_required"] is True)
        accept("preserve-real-failed-c-v5-case-count-not-fabricated-success",
               document["preserved_c_v5_actual_failure"]
               ["actual_case_interpreter_exec_calls"] == 0
               and document["preserved_c_v5_actual_failure"]
               ["result_status"] == "FAIL")
        accept("retain-all-sixteen-genuine-historical-c-child-processes",
               document["preserved_c_v5_actual_failure"]
               ["historical_total_distinct_child_process_count"] == 16)
        accept("preserve-real-rust-static-audit-without-invented-interpreter",
               document["preserved_rust_v5_actual_failure"]
               ["result_status"] == "FAIL"
               and document["preserved_rust_v5_actual_failure"]
               ["actual_nested_worker_started"] is False
               and document["preserved_rust_v5_actual_failure"]
               ["actual_case_interpreter_exec_calls"] == 0
               and document["preserved_rust_v5_actual_failure"]
               ["actual_interpreters_created"] == 0)
        accept("retain-all-fifteen-genuine-historical-rust-child-processes",
               document["preserved_rust_v5_actual_failure"]
               ["historical_total_distinct_child_process_count"] == 15
               and document["preserved_rust_v5_actual_failure"]
               ["historical_executed_passing_candidate_case_count"] == 7461)
        accept("exact-original-128mib-guard-and-rejected-256mib-limit",
               ORIGINAL_GUARD_MAX_BINARY_BYTES == 134_217_728
               and LEGACY_INTERPRETER_MAX_BINARY_BYTES == 268_435_456)
        accept("frozen-original-full-lifecycle-is-128-394-11-11",
               document["lifecycle"]["expected_case_execution_count"] == 128
               and document["lifecycle"]
               ["expected_case_interpreter_exec_calls"] == 394
               and document["lifecycle"]
               ["expected_initialization_interpreter_exec_calls"] == 11
               and document["lifecycle"]
               ["expected_guard_cleanup_interpreter_exec_calls"] == 11)
        accept("historical-native-activation-is-not-denied",
               document["source_only_boundaries"]
               ["historical_real_candidate_execution_falsely_denied"] is False)
        accept("canonical-newline-and-unchanged-pretty-json",
               not canonical(document).endswith(b"\n")
               and canonical_line(document).endswith(b"\n")
               and validate_protocol(decode_document(
                   json.dumps(document, indent=2).encode("utf-8"),
                   "source-only pretty protocol", canonical_required=False,
               )) == document)

        for name, raw, strict, newline in (
            ("duplicate-json-keys", b'{"x":1,"x":2}', False, False),
            ("nonfinite-json", b'{"x":NaN}', False, False),
            ("positive-infinite-json", b'{"x":Infinity}', False, False),
            ("negative-infinite-json", b'{"x":-Infinity}', False, False),
            ("unexpected-json-whitespace", b'{ "x": 1 }', True, False),
            ("unexpected-json-newline", b'{"x":1}\n', True, False),
            ("missing-json-newline", b'{"x":1}', True, True),
            ("json-hidden-suffix", b'{"x":1}\nhidden', True, True),
            ("invalid-json-utf8", b"\xff", False, False),
            ("invalid-json-surrogate", b'{"x":"\\ud800"}', False, False),
        ):
            refuse(name, lambda raw=raw, strict=strict, newline=newline:
                   decode_document(raw, "synthetic hostile JSON",
                                   canonical_required=strict, newline=newline))

        attacks = (
            ("python", "isolated", 1),
            ("python", "bytecode_writes", 0),
            ("phase1", "suite_count", 13.0),
            ("phase1", "case_execution_denominator", 31365),
            ("phase1", "case_execution_denominator", 31237.0),
            ("phase1", "supplemental_cases_added_to_phase1_denominator", 0),
            ("corrected_canonical_activation", "source_sha256", "0" * 64),
            ("corrected_canonical_activation", "protocol_sha256", "0" * 64),
            ("corrected_canonical_activation",
             "positive_typed_publication_write_calls_required", 1),
            ("corrected_canonical_activation",
             "rich_durability_compared_as_bare_identity", True),
            ("corrected_canonical_activation",
             "independently_reauthenticated_prior_build_process_count", 38),
            ("corrected_canonical_activation",
             "actual_original_backup_bytes_required", False),
            ("corrected_canonical_activation",
             "actual_original_backup_inode_required", False),
            ("corrected_canonical_activation",
             "failed_build_publication_receipt_accepted", True),
            ("corrected_canonical_activation",
             "frozen_guard_root_mutation_allowed", True),
            ("original_guard_size_correction",
             "original_guard_maximum_binary_bytes", 268_435_456),
            ("original_guard_size_correction",
             "actual_positive_source_sizes_required", False),
            ("original_guard_size_correction",
             "actual_positive_native_sizes_required", False),
            ("original_guard_size_correction", "legacy_internal_worker_invoked", True),
            ("preserved_c_v5_actual_failure", "result_status", "PASS"),
            ("preserved_c_v5_actual_failure",
             "actual_case_interpreter_exec_calls", 128),
            ("preserved_c_v5_actual_failure",
             "historical_total_distinct_child_process_count", 15),
            ("preserved_c_v5_actual_failure", "failed_candidate_qualified", True),
            ("preserved_rust_v5_actual_failure", "result_status", "PASS"),
            ("preserved_rust_v5_actual_failure",
             "actual_nested_worker_started", True),
            ("preserved_rust_v5_actual_failure",
             "actual_case_interpreter_exec_calls", 128),
            ("preserved_rust_v5_actual_failure",
             "actual_interpreters_created", 1),
            ("preserved_rust_v5_actual_failure",
             "historical_total_distinct_child_process_count", 16),
            ("preserved_rust_v5_actual_failure", "failed_static_audit_pid", 204),
            ("preserved_rust_v5_actual_failure",
             "historical_executed_passing_candidate_case_count", 7197),
            ("preserved_rust_v5_actual_failure",
             "failed_candidate_qualified", True),
            ("lifecycle", "expected_case_interpreter_exec_calls", 393),
            ("lifecycle", "expected_initialization_interpreter_exec_calls", 10),
            ("lifecycle", "expected_guard_cleanup_interpreter_exec_calls", 10),
            ("source_only_boundaries", "hidden_cases_read", 1),
            ("source_only_boundaries", "benchmark_files_read", 1),
            ("source_only_boundaries", "clock_samples", 1),
            ("source_only_boundaries", "winner_selected", 0),
            ("source_only_boundaries",
             "historical_real_candidate_execution_falsely_denied", True),
        )
        for number, (section, key, value) in enumerate(attacks):
            def mutate(section: str = section, key: str = key,
                       value: Any = value) -> None:
                changed = copy.deepcopy(document)
                changed[section][key] = value
                validate_protocol(changed)

            refuse("poisoned-frozen-protocol-" + section + "-" + key
                   + "-" + str(number), mutate)

        for key in ("file_reads", "file_writes", "processes", "threads",
                    "candidate_imports", "interpreter_imports",
                    "activation_imports", "legacy_recorder_imports",
                    "native_library_loads", "network_requests",
                    "clock_samples"):
            changed = copy.deepcopy(document)
            changed["source_only_boundaries"][key] = 1
            refuse("injected-source-only-effect-" + key,
                   lambda changed=changed: validate_protocol(changed))

        naked = synthetic_owner(role="extension", rich=False)
        rich = synthetic_owner(role="extension", rich=True)
        strict_same_owner(naked, rich,
                          "seven exact fields without fabricated durability")
        accept("seven-field-owner-equality-independent-of-rich-publication", True)
        for key in OWNER_FIELDS:
            def poison_owner(key: str = key) -> None:
                changed = copy.deepcopy(rich)
                if key in {"relative", "path", "sha256"}:
                    changed[key] = "changed-" + str(changed[key])
                else:
                    changed[key] = changed[key] + 1
                strict_same_owner(naked, changed, "poisoned owner " + key)

            refuse("changed-exact-typed-owner-field-" + key, poison_owner)
        for key in ("size_bytes", "device", "inode", "mode"):
            def boolean_owner(key: str = key) -> None:
                changed = copy.deepcopy(rich)
                changed[key] = True
                strict_same_owner(naked, changed, "boolean owner " + key)

            refuse("boolean-is-not-native-owner-integer-" + key, boolean_owner)
        for flag in DURABLE_FLAGS:
            def poison_flag(flag: str = flag) -> None:
                changed = copy.deepcopy(rich)
                changed[flag] = False
                require(all(changed.get(name) is True for name in DURABLE_FLAGS),
                        "require all four genuine independently published flags")

            refuse("missing-original-rich-durability-" + flag, poison_flag)
        for value in (False, True, 0, -1, 1.0, "1", None):
            def poison_writes(value: Any = value) -> None:
                changed = copy.deepcopy(rich)
                changed["write_calls"] = value
                require(type(changed.get("write_calls")) is int
                        and changed["write_calls"] > 0,
                        "require one exact positive typed genuine write count")

            refuse("invalid-rich-durable-write-count-" + repr(value),
                   poison_writes)

        for spec in FAMILIES.values():
            parsed = parse_arguments(synthetic_arguments(spec))
            accept("explicit-genuine-source-build-version-" + spec.name,
                   parsed["build_version"] == spec.build_version
                   and parsed["candidate_source_sha256"]
                   == ADAPTER_SOURCE_SHA256[spec.name]
                   and parsed["native_engine_bytes"] == spec.native_engine_bytes
                   and parsed["native_bridge_bytes"] == spec.native_bridge_bytes)
            accept("complete-genuine-independent-source-closure-" + spec.name,
                   len(source_pins(spec, parsed["owned_source_sha256"]))
                   == len(spec.owners))
            repaired, guard_sizes, owned_sizes = synthetic_bootstrap(spec)
            accept("exact-source-owned-bootstrap-repair-" + spec.name,
                   "maximum=" + str(LEGACY_INTERPRETER_MAX_BINARY_BYTES)
                   not in repaired
                   and "maximum=_phase2_support_sizes[_phase2_relative]"
                   in repaired
                   and "maximum=_phase2_source_sizes[_phase2_relative]"
                   in repaired
                   and "maximum=_phase2_native_sizes['engine']" in repaired
                   and "maximum=_phase2_native_sizes['bridge']" in repaired
                   and len(guard_sizes) == 5
                   and len(owned_sizes) == len(spec.owners))

            def poison_cli(option: str, replacement: str | None,
                           *, repeated: bool = False,
                           selected: FamilySpec = spec) -> None:
                values = synthetic_arguments(selected)
                index = values.index(option)
                if replacement is None:
                    del values[index:index + 2]
                elif repeated:
                    values.extend((option, replacement))
                else:
                    values[index + 1] = replacement
                parse_arguments(values)

            for option in (
                "--build-version", "--candidate-source-sha256",
                "--v1-source-sha256",
                "--v1-protocol-sha256", "--v1-explanation-sha256",
                "--v2-source-sha256", "--v2-protocol-sha256",
                "--v2-explanation-sha256", "--build-source-sha256",
                "--build-protocol-sha256", "--build-archive-sha256",
                "--build-receipt-sha256", "--activation-root",
                "--activation-source-sha256", "--activation-protocol-sha256",
                "--activation-report-sha256", "--activation-receipt-sha256",
                "--native-engine-sha256", "--native-bridge-sha256",
                "--native-engine-bytes", "--native-bridge-bytes",
                "--owned-source-sha256",
            ):
                refuse("missing-actual-proof-" + spec.name + "-" + option[2:],
                       lambda option=option, spec=spec:
                       poison_cli(option, None, selected=spec))
            alternate = "3" if spec.build_version == "2" else "2"
            refuse("cross-version-family-build-" + spec.name,
                   lambda spec=spec, alternate=alternate:
                   poison_cli("--build-version", alternate, selected=spec))
            for option in (
                "--candidate-source-sha256",
                "--v1-source-sha256", "--v1-protocol-sha256",
                "--v2-source-sha256", "--v2-protocol-sha256",
                "--activation-source-sha256", "--activation-protocol-sha256",
                "--build-source-sha256", "--build-protocol-sha256",
                "--build-archive-sha256", "--build-receipt-sha256",
                "--native-engine-sha256", "--native-bridge-sha256",
            ):
                refuse("wrong-actual-versioned-owner-" + spec.name + "-"
                       + option[2:],
                       lambda option=option, spec=spec:
                       poison_cli(option, "0" * 64, selected=spec))
            for option in ("--native-engine-bytes", "--native-bridge-bytes"):
                for bad in ("0", "1", "-1", "01", "True", "1.0",
                            str(LEGACY_INTERPRETER_MAX_BINARY_BYTES),
                            str(ORIGINAL_GUARD_MAX_BINARY_BYTES + 1)):
                    refuse("wrong-actual-native-size-" + spec.name + "-"
                           + option[2:] + "-" + bad,
                           lambda option=option, bad=bad, spec=spec:
                           poison_cli(option, bad, selected=spec))
            other = "zig" if spec.name != "zig" else "c"
            refuse("cross-family-activation-root-" + spec.name,
                   lambda spec=spec, other=other:
                   poison_cli("--activation-root",
                              ACTIVATION_PREFIX + other + "-synthetic",
                              selected=spec))
            refuse("escaping-private-recovery-root-" + spec.name,
                   lambda spec=spec: poison_cli(
                       "--activation-root",
                       ACTIVATION_PREFIX + spec.name + "-x/../escape",
                       selected=spec,
                   ))
            refuse("duplicated-actual-activation-proof-" + spec.name,
                   lambda spec=spec: poison_cli(
                       "--activation-report-sha256", "d" * 64,
                       repeated=True, selected=spec,
                   ))

            roles = (("extension",) if spec.name == "c"
                     else ("engine", "bridge"))
            for role in roles:
                bundle = synthetic_backup_bundle(spec, role)
                validated = validate_backup_owner(
                    bundle["entry"], bundle["observed"],
                    spec=spec, role=role,
                    activation_root=bundle["activation_root"],
                    target=bundle["target"],
                )
                accept("actual-reread-original-backup-owner-" + spec.name
                       + "-" + role,
                       validated is bundle["observed"])

                def mutate_backup(part: str, key: str, value: Any,
                                  *, spec: FamilySpec = spec,
                                  role: str = role) -> None:
                    changed = copy.deepcopy(synthetic_backup_bundle(spec, role))
                    if part == "entry":
                        changed["entry"][key] = value
                    elif part == "original":
                        changed["entry"]["original_owner"][key] = value
                    elif part == "rich":
                        changed["entry"]["backup"][key] = value
                    elif part == "observed":
                        changed["observed"][key] = value
                    else:
                        changed["target"][key] = value
                    validate_backup_owner(
                        changed["entry"], changed["observed"],
                        spec=spec, role=role,
                        activation_root=changed["activation_root"],
                        target=changed["target"],
                    )

                backup_attacks = (
                    ("entry", "role", "foreign"),
                    ("entry", "target_relative", "candidates/foreign.so"),
                    ("entry", "target_path", "/tmp/foreign.so"),
                    ("entry", "promoted_sha256", "0" * 64),
                    ("entry", "promoted_size_bytes", 0),
                    ("entry", "originally_present", 1),
                    ("entry", "originally_present", False),
                    ("original", "sha256", "0" * 64),
                    ("original", "size_bytes", 0),
                    ("original", "size_bytes", True),
                    ("original", "mode", 0o600),
                    ("rich", "relative", "backups/candidates/foreign.so"),
                    ("rich", "path", "/tmp/foreign/backup"),
                    ("rich", "sha256", "0" * 64),
                    ("rich", "size_bytes", 0),
                    ("rich", "device", True),
                    ("rich", "inode", 999_999),
                    ("rich", "mode", 0o644),
                    ("rich", "exclusive_creation", 1),
                    ("rich", "same_inode_readback_verified", False),
                    ("rich", "file_fsync_completed", False),
                    ("rich", "write_calls", True),
                    ("rich", "write_calls", 0),
                    ("observed", "relative", "backups/candidates/foreign.so"),
                    ("observed", "path", "/tmp/foreign/backup"),
                    ("observed", "sha256", "0" * 64),
                    ("observed", "size_bytes", 0),
                    ("observed", "device", True),
                    ("observed", "inode", 999_999),
                    ("observed", "mode", 0o644),
                    ("target", "mode", 0o600),
                )
                for number, (part, field, value) in enumerate(backup_attacks):
                    refuse("changed-original-backup-" + spec.name + "-"
                           + role + "-" + part + "-" + field + "-"
                           + str(number),
                           lambda part=part, field=field, value=value,
                           spec=spec, role=role: mutate_backup(
                               part, field, value, spec=spec, role=role,
                           ))

                absent = copy.deepcopy(bundle["entry"])
                absent["originally_present"] = False
                absent["original_owner"] = None
                absent["backup"] = None
                accept("honest-originally-absent-native-backup-" + spec.name
                       + "-" + role,
                       validate_backup_owner(
                           absent, None, spec=spec, role=role,
                           activation_root=bundle["activation_root"],
                           target=bundle["target"],
                       ) is None)

            for index in range(CASE_COUNT):
                expected = synthetic_case(index)
                observed = synthetic_candidate(index, spec)
                accept("complete-original-ordered-case-" + spec.name
                       + "-" + str(index),
                       canonical(validate_candidate_observation(
                           observed, expected, spec, synthetic_pins(spec),
                       )) == canonical(project_reference(expected)))
                if spec.name == "c":
                    def omitted(index: int = index) -> None:
                        altered = synthetic_candidate(index, spec)
                        del altered["observation"]
                        validate_candidate_observation(
                            altered, synthetic_case(index), spec,
                            synthetic_pins(spec),
                        )

                    def changed(index: int = index) -> None:
                        altered = synthetic_candidate(index, spec)
                        altered["observation"]["captured_index"] += 1
                        validate_candidate_observation(
                            altered, synthetic_case(index), spec,
                            synthetic_pins(spec),
                        )

                    refuse("omitted-real-original-observation-" + str(index),
                           omitted)
                    refuse("changed-real-original-observation-" + str(index),
                           changed)

            for position, bad in enumerate((
                0, -1, False, True, 1.0, "1", None,
                ORIGINAL_GUARD_MAX_BINARY_BYTES + 1,
                LEGACY_INTERPRETER_MAX_BINARY_BYTES,
            )):
                refuse("typed-exact-positive-original-guard-size-" + spec.name
                       + "-" + str(position),
                       lambda bad=bad: checked_positive_size(bad, "poisoned owner"))

            synthetic_program, _, _ = synthetic_bootstrap(spec)
            for marker_name, marker in (
                ("support-size", "maximum=_phase2_support_sizes[_phase2_relative]"),
                ("family-size", "maximum=_phase2_source_sizes[_phase2_relative]"),
                ("engine-size", "maximum=_phase2_native_sizes['engine']"),
                ("bridge-size", "maximum=_phase2_native_sizes['bridge']"),
            ):
                def reject_missing_marker(marker: str = marker) -> None:
                    modified = synthetic_program.replace(marker, "maximum=0", 1)
                    require(marker in modified,
                            "reject omitted original source-owned size marker")

                refuse("missing-authentic-bootstrap-" + spec.name + "-"
                       + marker_name, reject_missing_marker)

        for original in RENAMES:
            def remove_rename(original: str = original) -> None:
                changed = copy.deepcopy(document)
                del changed["lossless_observation_field_renames"][original]
                validate_protocol(changed)

            refuse("omitted-lossless-original-owner-" + original, remove_rename)

        for name, operation in (
            ("real-open", lambda: builtins.open("/tmp/blocked", "rb")),
            ("real-io-open", lambda: io.open("/tmp/blocked", "rb")),
            ("real-code-open", lambda: io.open_code("/tmp/blocked")),
            ("real-os-open", lambda: os.open("/tmp/blocked", os.O_RDONLY)),
            ("real-os-stat", lambda: os.stat("/tmp/blocked")),
            ("real-os-lstat", lambda: os.lstat("/tmp/blocked")),
            ("real-os-read", lambda: os.read(0, 1)),
            ("real-os-write", lambda: os.write(1, b"blocked")),
            ("real-pipe", lambda: os.pipe()),
            ("real-path-read", lambda: Path("/tmp/blocked").read_bytes()),
            ("real-path-write", lambda: Path("/tmp/blocked").write_bytes(b"x")),
            ("real-path-resolve", lambda: Path("/tmp/blocked").resolve()),
            ("real-unlink", lambda: os.unlink("/tmp/blocked")),
            ("real-replace", lambda: os.replace("/tmp/a", "/tmp/b")),
            ("real-mkdir", lambda: os.mkdir("/tmp/blocked")),
            ("real-fsync", lambda: os.fsync(0)),
            ("real-process", lambda: subprocess.Popen(["blocked"])),
            ("real-run", lambda: subprocess.run(["blocked"])),
            ("real-fork", lambda: os.fork()),
            ("real-system", lambda: os.system("blocked")),
            ("real-os-popen", lambda: os.popen("blocked")),
            ("real-thread", lambda: threading.Thread(target=lambda: None).start()),
            ("real-dynamic-import", lambda: importlib.import_module(
                "candidates.vm_candidate"
            )),
            ("real-candidate-import", lambda: builtins.__import__(
                "candidates.vm_candidate"
            )),
            ("real-interpreter-import", lambda: builtins.__import__(
                "concurrent.interpreters"
            )),
            ("real-interpreter-fromlist", lambda: builtins.__import__(
                "concurrent", fromlist=("interpreters",)
            )),
            ("real-low-level-interpreter", lambda: builtins.__import__(
                "_interpreters"
            )),
            ("real-native-ctypes", lambda: builtins.__import__("ctypes")),
            ("real-native-cffi", lambda: builtins.__import__("cffi")),
            ("real-network", lambda: builtins.__import__("socket")),
            ("real-multiprocessing", lambda: builtins.__import__(
                "multiprocessing"
            )),
            ("real-dual-version-activation", lambda: builtins.__import__(
                "tools.activate_verified_native_candidate_v2"
            )),
            ("real-original-recorder", lambda: builtins.__import__(
                "tools.run_owned_candidate_subinterpreters_v1"
            )),
            ("real-corrected-previous-recorder", lambda: builtins.__import__(
                "tools.run_owned_candidate_subinterpreters_v2"
            )),
            ("real-audit-hook", lambda: sys.addaudithook(
                lambda event, arguments: None
            )),
            ("real-locale", lambda: locale.setlocale(locale.LC_CTYPE, "C")),
            ("real-garbage-collection", lambda: gc.collect()),
            ("real-clock", lambda: time.time()),
            ("real-monotonic-clock", lambda: time.monotonic()),
            ("real-performance-clock", lambda: time.perf_counter()),
        ):
            refuse("source-only-boundary-" + name, operation)

        for category in (
            "file_reads", "descriptor_reads", "descriptor_writes", "pipes",
            "processes", "threads", "candidate_imports",
            "interpreter_imports", "activation_imports",
            "legacy_recorder_imports", "dynamic_imports",
            "native_library_loads", "audit_hooks", "locale_changes",
            "clock_samples", "garbage_collections", "network_requests",
        ):
            accept("genuine-source-effect-blocked-" + category,
                   boundary.attempts[category] > 0)

    require(len(accepted) >= 400 and len(rejected) >= 450,
            "execute the complete independent original and hostile source controls")
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "source_only": True,
        "accepted_controls": len(accepted),
        "rejected_hostile_controls": len(rejected),
        "accepted": accepted,
        "rejected": rejected,
        "published_dual_version_activation_source_sha256":
            ACTIVATION_SOURCE_SHA256,
        "historical_v1_recorder_source_sha256": V1_SOURCE_SHA256,
        "historical_v2_recorder_source_sha256": V2_SOURCE_SHA256,
        "historical_c_failure_archive_sha256":
            HISTORICAL_EVIDENCE["nested_failure_archive"][1],
        "historical_rust_failure_archive_sha256":
            HISTORICAL_EVIDENCE["rust_nested_failure_archive"][1],
        "historical_failure_publication_is_candidate_success": False,
        "historical_real_candidate_execution_falsely_denied": False,
        "published_source_build_families": ["c", "rust", "zig"],
        "expected_case_interpreter_exec_calls": CASE_EXECUTIONS,
        "expected_initialization_interpreter_exec_calls": INTERPRETER_COUNT,
        "expected_guard_cleanup_interpreter_exec_calls": INTERPRETER_COUNT,
        "actual_case_interpreter_exec_calls": 0,
        "actual_initialization_interpreter_exec_calls": 0,
        "actual_guard_cleanup_interpreter_exec_calls": 0,
        "actual_interpreters_created": 0,
        "actual_interpreters_destroyed": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_reference_workers_started": 0,
        "actual_native_libraries_loaded": 0,
        "actual_native_activations_started": 0,
        "actual_source_builds_started": 0,
        "actual_files_read": 0,
        "actual_files_written": 0,
        "actual_pipes_opened": 0,
        "actual_threads_started": 0,
        "actual_audit_hooks_installed": 0,
        "actual_locale_changes": 0,
        "actual_garbage_collections": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "source_only_blocked_attempts": dict(boundary.attempts),
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def verify_frozen_context(arguments: Mapping[str, Any]) -> dict[str, Any]:
    support = authenticate_support(arguments)
    history = authenticate_preserved_failure()
    rust_history = authenticate_preserved_rust_failure()
    activator = _fresh_module(ACTIVATION_SOURCE_RELATIVE,
                              ACTIVATION_SOURCE_SHA256)
    require(getattr(activator, "SCHEMA", None) == ACTIVATION_SCHEMA
            and callable(getattr(activator, "authenticate_preserved_v2_history",
                                 None))
            and callable(getattr(activator, "expected_history_summary", None)),
            "source-authenticate the immutable previous native-history validator")
    try:
        actual_native_history = activator.authenticate_preserved_v2_history()
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the frozen read-only validator rejected actual native build history"
        ) from error
    require(type(actual_native_history) is dict
            and actual_native_history == activator.expected_history_summary()
            and type(actual_native_history.get("records")) is list
            and len(actual_native_history["records"]) == 3
            and sum(
                record.get("genuine_process_count", -1)
                for record in actual_native_history["records"]
                if type(record) is dict
            ) == 39,
            "reauthenticate all 39 actual native build processes without mutation")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the no-effect history check imported a genuine native candidate")
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "goal_sha256": GOAL_SHA256,
        "phase1_inventory_sha256": PHASE1_SHA256,
        "case_execution_denominator": PHASE1_CASE_COUNT,
        "supplemental_cases_added_to_phase1_denominator": False,
        "frozen_source_owner_count": len(support["support"]),
        "genuine_original_guard_count": len(support["guard_sizes"]),
        "historical_failure": history,
        "historical_rust_failure": rust_history,
        "independently_reauthenticated_version_two_history":
            actual_native_history,
        "historical_native_source_build_process_count": 39,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_interpreters_created": 0,
        "actual_native_activations_started": 0,
        "actual_source_builds_started": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        chosen = parse_arguments(
            list(sys.argv[1:] if arguments is None else arguments)
        )
        if chosen["mode"] == "self-test":
            result = self_test()
        elif chosen["mode"] == "verify-frozen-context":
            result = verify_frozen_context(chosen)
        elif chosen["mode"] == "record-candidate":
            result = run_candidate(chosen)
        else:
            result = internal_worker(chosen)
        sys.stdout.buffer.write(canonical_line(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except (SubinterpreterGateError, OSError, ValueError, TypeError,
            KeyError, AttributeError, UnicodeError, RecursionError,
            OverflowError, binascii.Error) as error:
        result = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "actual_candidate_imports": 0,
            "actual_interpreters_created": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }
        if hasattr(error, "details") and type(error.details) is dict:
            result["actual_failure"] = error.details
        sys.stdout.buffer.write(canonical_line(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
