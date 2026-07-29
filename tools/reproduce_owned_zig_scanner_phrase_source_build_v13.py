#!/usr/bin/env python3
"""Freeze, and only when expressly requested build, the first-party Zig fix."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import ctypes
import errno
import fcntl
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import signal
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-owned-zig-scanner-phrase-source-build-v13"
VERSION = 13
SOURCE_PATH = "tools/reproduce_owned_zig_scanner_phrase_source_build_v13.py"
PROTOCOL_PATH = "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-BUILD-V13.md"
CONTRACT_PATH = "oracle/phase2/zig-scanner-phrase-source-build-v13.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
GRAPH_VERSION = 84
EVIDENCE_LOWER_BOUND = 272
HISTORY_LOWER_BOUND = 277
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_TOOLCHAIN_BYTES = 256 * 1024 * 1024
MAX_NATIVE_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 16 * 1024 * 1024
MAX_RECEIPT_BYTES = 32 * 1024 * 1024
PRIVATE_ROOT_PREFIX = "rebar-phase2-zig-scanner-phrase-source-build-v13-"
PHASE_NAMES = ("reference-a", "reference-b")
ENGINE_NAME = "_zig_probe.so"
BRIDGE_NAME = "_zig_bridge.cpython-314-x86_64-linux-gnu.so"
CANONICAL_SOURCE_PREFIX = "/rebar-owned-zig-scanner-phrase-v13-source"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
PINNED_ZIG = "/tmp/zig-x86_64-linux-0.16.0/zig"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
MATRIX_SHA256 = "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c"
OVERFLOW_SHA256 = "e1b75493de4be5ea1583e30077737405112b22fdb072cd8b0e38e2770a2959e6"
RUST_V15_RECEIPT_PATH = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v15-rust-phase2-v19-"
    "rust-buffer-shape-root-provenance-original-p0-v15-"
    "failures-publication-receipt.json"
)

SUITE_CASES = (
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

OWNERS: dict[str, tuple[str, int]] = {
    "GOAL.md": (
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756,
    ),
    "oracle/phase1/p0-completeness-v1.json": (
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632,
    ),
    "oracle/phase1/p0-completeness-v4.json": (
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875,
    ),
    "oracle/phase2/six-family-p0-producer-v4.json": (
        "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867,
    ),
    (
        "oracle/phase1/evidence/"
        "differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/"
        "two-independent-reference-result.json"
    ): (
        "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096", 3658,
    ),
    RUST_V15_RECEIPT_PATH: (
        "5b1cfdc72f88c3a847f65f5a06da77cd27557ca2c2306320b6c8d44a91e28578", 18510,
    ),
    "tools/apply_owned_zig_scanner_phrase_source_repair_v4.py": (
        "31dafa08a8f394a8803fa352dd31c806fdac7aa6ee9160e67f2d5f60b2736a63", 65425,
    ),
    "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md": (
        "e17a46e13652e2950171d84096a0bf812020c88168589c17e50e1bab187339cf", 6919,
    ),
    "oracle/phase2/zig-scanner-phrase-source-repair-v4.json": (
        "5c8f9a220bf93fc56e9d8054002ea4358323c23a9a951d3ce28201b59947b19c", 11500,
    ),
    "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py": (
        "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b", 68530,
    ),
    "candidates/zig/mini_regex.zig": (
        "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915,
    ),
    "candidates/zig/py_bridge.c": (
        "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026,
    ),
    "candidates/zig_candidate.py": (
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422,
    ),
    "toolchains/zig-0.16.0.lock.json": (
        "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd", 628,
    ),
    "tools/render_candidate_current_overview_v84.py": (
        "00f9767cf82571ae10246f80a12d2c87a221f1a97f8d8c3baecce32e8eda3a8d", 72026,
    ),
    "docs/evidence/candidate-current-overview-v84.inputs.json": (
        "08a83e53458e457f9cc62ca876a25e9291c58f048a5f9bbe93a4784b82ff027a", 1320360,
    ),
    "docs/evidence/candidate-current-overview-v84.json": (
        "9f801745dbed779b2cd02aacd5fc6aaeecf016a8e33c37ae1eee043ffab18bca", 3798003,
    ),
    "docs/evidence/candidate-current-overview-v84.svg": (
        "8f140d26cfc0759abd5599c8604d143d1e9da660f91d3dc5a72da1749a175d03", 6100,
    ),
}

GRAPH_PATHS = (
    "tools/render_candidate_current_overview_v84.py",
    "docs/evidence/candidate-current-overview-v84.inputs.json",
    "docs/evidence/candidate-current-overview-v84.json",
    "docs/evidence/candidate-current-overview-v84.svg",
)

TOOLCHAINS: dict[str, tuple[str, str, int, bool]] = {
    "python": (
        PINNED_PYTHON,
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        32387816,
        True,
    ),
    "python_header": (
        PINNED_INCLUDE + "/Python.h",
        "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
        4399,
        False,
    ),
    "python_patchlevel": (
        PINNED_INCLUDE + "/patchlevel.h",
        "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
        1773,
        False,
    ),
    "gcc": (
        PINNED_GCC,
        "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        1023032,
        True,
    ),
    "readelf": (
        PINNED_READELF,
        "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        789280,
        True,
    ),
    "zig": (
        PINNED_ZIG,
        "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
        172641672,
        True,
    ),
}

PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version",
    "build_zig_engine", "build_zig_bridge",
    "engine_dynamic", "engine_symbols", "engine_sections", "engine_notes",
    "bridge_dynamic", "bridge_symbols", "bridge_sections", "bridge_notes",
)

REQUIRED_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
})
REQUIRED_BRIDGE_IMPORTS = frozenset({
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
})
ALLOWED_UNICODE_HELPERS = frozenset({
    "_PyUnicode_IsWhitespace", "_PyUnicode_IsDecimalDigit",
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDigit", "_PyUnicode_IsNumeric",
    "_PyUnicode_ToLowercase", "_PyUnicode_ToUppercase",
})
FORBIDDEN_PREFIXES = (
    "_sre", "sre_", "pcre", "onig", "re2_", "hs_", "hyperscan",
    "rebar_rust_", "rebar_c_", "rebar_vm_", "rebar_cpp_",
    "rebar_go_", "rebar_fortran_",
)
FORBIDDEN_SYMBOLS = frozenset({
    "regcomp", "regexec", "regerror", "regfree", "dlopen", "dlmopen",
    "dlsym", "system", "execve", "posix_spawn", "socket", "connect",
    "getaddrinfo", "PyImport_Import", "PyImport_ImportModule",
    "PyImport_ExecCodeModule",
})


class FreezeError(Exception):
    """The exact frozen source, native-build plan, or safety wall changed."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def checked_sha(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "require an exact independently caller-pinned SHA-256: " + label,
    )
    return value


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash only exact complete bytes")
    return hashlib.sha256(value).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError) as error:
        raise FreezeError("reject nonfinite or noncanonical build evidence") from error


def strict_json(
    raw: bytes, label: str, *, canonical_required: bool = True,
) -> dict[str, Any]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(type(key) is str and key not in result,
                    "reject a repeated " + label + " field")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique,
            parse_constant=lambda _item: (_ for _ in ()).throw(
                FreezeError("reject nonfinite " + label)
            ),
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise FreezeError("reject malformed " + label) from error
    require(type(value) is dict, "require a complete object for " + label)
    if canonical_required:
        require(canonical(value) == raw, "require complete canonical " + label)
    return value


def safe_relative(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and 0 < len(relative) <= 512,
            "require a bounded repository source path")
    parts = tuple(relative.split("/"))
    require(
        not relative.startswith("/")
        and all(part not in ("", ".", "..") for part in parts)
        and all("\\" not in part and "\x00" not in part for part in parts)
        and not relative.endswith((".gz", ".xz", ".zip", ".tar", ".so", ".pyc"))
        and all(part not in ("holdout", "performance", "benchmarks", ".git")
                for part in parts),
        "reject archives, native artifacts, holdout, benchmarks, or escaped owners",
    )
    return parts


def owner_metadata(path: str, info: os.stat_result, fingerprint: str) -> dict[str, Any]:
    return {
        "path": path,
        "sha256": fingerprint,
        "bytes": info.st_size,
        "device": info.st_dev,
        "inode": info.st_ino,
        "uid": info.st_uid,
        "mode": format(stat.S_IMODE(info.st_mode), "04o"),
        "nlink": info.st_nlink,
    }


def read_descriptor(
    descriptor: int,
    expected: str,
    expected_size: int,
    limit: int,
    label: str,
    *,
    retain: bool = True,
    executable: bool = False,
    private: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    checked_sha(expected, label)
    require(type(expected_size) is int and 0 < expected_size <= limit,
            "bound the complete owner: " + label)
    before = os.fstat(descriptor)
    require(
        stat.S_ISREG(before.st_mode)
        and before.st_size == expected_size
        and before.st_nlink == 1,
        "reject an aliased, nonregular, or incorrectly sized owner: " + label,
    )
    if executable:
        require(bool(before.st_mode & 0o111),
                "require the genuine pinned compiler executable: " + label)
    if private:
        require(
            before.st_uid == os.geteuid()
            and stat.S_IMODE(before.st_mode) == 0o600,
            "require a fresh private mode-0600 source owner: " + label,
        )
    hasher = hashlib.sha256()
    total = 0
    chunks: list[bytes] = []
    while True:
        remaining = min(1024 * 1024, limit + 1 - total)
        require(remaining > 0, "reject an oversized owner: " + label)
        part = os.read(descriptor, remaining)
        if not part:
            break
        total += len(part)
        require(total <= limit, "reject an oversized owner: " + label)
        hasher.update(part)
        if retain:
            chunks.append(part)
    after = os.fstat(descriptor)
    require(
        (
            before.st_dev, before.st_ino, before.st_size, before.st_uid,
            before.st_nlink, before.st_mtime_ns, before.st_ctime_ns,
        ) == (
            after.st_dev, after.st_ino, after.st_size, after.st_uid,
            after.st_nlink, after.st_mtime_ns, after.st_ctime_ns,
        )
        and total == expected_size
        and hasher.hexdigest() == expected,
        "reject a changed or incomplete independently authenticated owner: " + label,
    )
    raw = b"".join(chunks) if retain else None
    if retain:
        require(raw is not None and len(raw) == expected_size,
                "retain every authenticated source byte: " + label)
    return owner_metadata(label, after, expected), raw


def read_repository_owner(relative: str, fingerprint: str, size: int) -> tuple[
    dict[str, Any], bytes
]:
    parts = safe_relative(relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            owner, raw = read_descriptor(
                descriptor, fingerprint, size, MAX_SOURCE_BYTES, relative,
            )
        finally:
            os.close(descriptor)
        require(raw is not None, "retain the complete repository source owner")
        require(owner["uid"] == os.geteuid() and owner["mode"] == "0600",
                "require a real individually owned mode-0600 repository source")
        return owner, raw
    finally:
        os.close(directory)


def read_external_owner(
    name: str,
) -> dict[str, Any]:
    require(name in TOOLCHAINS, "authenticate only an explicitly frozen toolchain")
    path, fingerprint, size, executable = TOOLCHAINS[name]
    require(path.startswith("/") and "\x00" not in path and "\\" not in path,
            "reject an unpinned external compiler path")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        owner, raw = read_descriptor(
            descriptor, fingerprint, size, MAX_TOOLCHAIN_BYTES, path,
            retain=False, executable=executable,
        )
        require(raw is None, "do not retain or execute pinned compiler bytes")
        return {"id": name, "executable": executable, **owner}
    finally:
        os.close(descriptor)


def validate_phase_one(value: dict[str, Any]) -> None:
    denominator = value.get("denominator")
    suites = value.get("suites")
    require(
        value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and type(denominator) is dict
        and denominator.get("final_required_case_execution_denominator") == 31237
        and denominator.get("available_frozen_vector_case_executions") == 31237
        and denominator.get("private_upstream_methods_outside_public_denominator") == 13
        and type(suites) is list
        and tuple((item.get("id"), item.get("case_execution_count"))
                  for item in suites) == SUITE_CASES
        and sum(count for _, count in SUITE_CASES) == 31237
        and value.get("phase_gate", {}).get("status") == "PASS",
        "preserve the complete original 31,237-case, 13-suite CPython oracle",
    )


def validate_readiness(value: dict[str, Any]) -> None:
    phase = value.get("phase_gate")
    candidates = value.get("candidate_qualification_gate")
    supplement = value.get("actual_supplemental_two_reference")
    require(
        value.get("schema") == "rebar-cpython-re-p0-completeness-v4"
        and value.get("version") == 4
        and value.get("status") == "PASS"
        and value.get("original_case_execution_denominator") == 31237
        and value.get("original_suite_count") == 13
        and value.get("original_named_private_waiver_count") == 13
        and value.get("original_obligation_count") == 73
        and value.get("original_crosswalk_count") == 34
        and value.get("first_party_candidate_family_count") == 6
        and type(phase) is dict
        and phase.get("status") == "PASS"
        and phase.get("candidate_evaluation_authorized") is True
        and phase.get("final_holdout_authorized") is False
        and phase.get("performance_oracle_authorized") is False
        and type(candidates) is dict
        and candidates.get("status") == "BLOCKED"
        and candidates.get("qualified_candidate_count") == 0
        and candidates.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and type(supplement) is dict
        and supplement.get("actual_reference_worker_count") == 2
        and supplement.get("actual_reference_worker_process_ids") == [81, 82]
        and supplement.get("case_count_per_worker") == [8244, 8244]
        and supplement.get("failed_per_worker") == [0, 0]
        and supplement.get("case_denominator_included_in_original_31237") is False
        and value.get("qualified_candidate_count") == 0
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "preserve actual phase-one readiness without inventing candidate passes",
    )


def validate_supplement(value: dict[str, Any]) -> None:
    require(
        value.get("schema")
        == "rebar-owned-differential-fuzz-reference-v3-actual-reference"
        and value.get("status") == "PASS"
        and value.get("actual_reference_worker_count") == 2
        and value.get("actual_reference_worker_process_ids") == [81, 82]
        and value.get("actual_candidate_worker_count") == 0
        and value.get("candidate_status") == "NOT RUN"
        and value.get("candidate_qualified") is False
        and value.get("original_case_execution_denominator") == 31237
        and value.get("supplemental_case_count") == 8244
        and value.get("case_denominator_included_in_original_31237") is False
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("qualified_candidate_count") == 0,
        "retain all 8,244 separate actually referenced checks",
    )


def validate_lock(value: dict[str, Any]) -> None:
    require(
        value.get("schema") == "rebar-official-language-toolchain-v1"
        and value.get("language") == "Zig"
        and value.get("version") == "0.16.0"
        and value.get("release_channel") == "stable"
        and value.get("platform") == "x86_64-linux"
        and value.get("archive_root") == "zig-x86_64-linux-0.16.0"
        and value.get("compiler_relative_path") == "zig-x86_64-linux-0.16.0/zig"
        and value.get("compiler_sha256") == TOOLCHAINS["zig"][1]
        and value.get("archive_sha256")
        == "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00"
        and value.get("archive_bytes") == 55478392,
        "require the exact official offline Zig 0.16.0 toolchain lock",
    )


def validate_actual_rust_v15(value: dict[str, Any]) -> None:
    workers = value.get("actual_worker_process_ids")
    require(
        value.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v15-durable-publication-receipt"
        and value.get("status") == "PASS"
        and value.get("publication_status") == "PASS"
        and value.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and value.get("family") == "rust"
        and value.get("candidate_status") == "FAIL"
        and value.get("candidate_qualified") is False
        and value.get("actual_candidate_workers") == 13
        and type(workers) is list
        and len(workers) == 13
        and all(type(item) is int and item > 0 for item in workers)
        and len(set(workers)) == 13
        and value.get("distinct_worker_process_id_count") == 13
        and value.get("duplicate_worker_process_id_count") == 0
        and value.get("missing_worker_process_id_count") == 0
        and value.get("started_suite_count") == 13
        and value.get("attempted_suite_count") == 13
        and value.get("suite_count") == 13
        and value.get("completed_suite_count") == 8
        and value.get("case_execution_denominator") == 31237
        and value.get("named_private_waiver_count") == 13
        and value.get("semantic_mismatch_count") == "NOT MEASURED"
        and value.get("verified_passing_case_count") == 12942
        and value.get("infrastructure_failure_count") == 5
        and value.get("worker_failure_capture_count") == 5
        and value.get("worker_failure_capture_complete") is True
        and value.get("all_original_observation_vectors_complete") is False
        and value.get("preserved_previous_rust_semantic_mismatch_count") == 1440
        and value.get("preserved_previous_rust_verified_passing_case_count") == 14853
        and value.get("all_four_original_targets_restored") is True
        and value.get("restoration_verified_before_publication") is True
        and value.get("historical_evidence_owner_count_before_publication") == 270
        and value.get("historical_authenticated_reference_count_before_publication") == 275
        and value.get("new_repository_evidence_owner_count") == 2
        and value.get("resulting_repository_evidence_owner_count") == 272
        and value.get("resulting_authenticated_reference_count") == 277
        and value.get("actual_v19_compiler_process_count") == 28
        and value.get("actual_v19_build_archive_read_count") == 0
        and value.get("actual_v19_build_archive_gzip_inflation_count") == 0
        and value.get("benchmark_files_read") == 0
        and value.get("clock_samples") == 0
        and value.get("timing_trials_run") == 0
        and value.get("hidden_cases_read") == 0
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "preserve the genuine partial Rust V15 failure using its plaintext receipt only",
    )


def validate_feature(value: dict[str, Any]) -> None:
    feature = value.get("first_party_source_feature")
    matrix = feature.get("scanner_matrix") if type(feature) is dict else None
    history = value.get("previous_actual_zig_matching")
    oracle = value.get("original_oracle")
    require(
        value.get("schema") == "rebar-owned-zig-scanner-phrase-source-repair-v4"
        and value.get("version") == 4
        and value.get("status")
        == "SOURCE FROZEN; FIRST-PARTY ZIG VARIANT NOT BUILT OR TESTED"
        and type(oracle) is dict
        and oracle.get("original_case_execution_denominator") == 31237
        and oracle.get("suite_count") == 13
        and oracle.get("named_private_waiver_count") == 13
        and oracle.get("mapped_obligation_count") == 73
        and oracle.get("additional_independently_referenced_case_count") == 8244
        and oracle.get("additional_cases_included_in_original_denominator") is False
        and type(feature) is dict
        and feature.get("family") == "zig"
        and feature.get("semantic_owner_count") == 1
        and feature.get("new_independent_candidate_family_count") == 0
        and feature.get("variant_materialized") is True
        and feature.get("outside_feature_block_unchanged") is True
        and feature.get("capture_check_occurs_before_native_compile") is True
        and feature.get("corrected_candidate_build") == "NOT RUN"
        and feature.get("corrected_candidate_matching") == "NOT RUN"
        and feature.get("corrected_candidate_qualified") is False
        and feature.get("complete_materialized_variant", {}).get("sha256")
        == OWNERS["candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"][0]
        and feature.get("complete_materialized_variant", {}).get("bytes") == 68530
        and feature.get("independent_engine", {}).get("sha256")
        == OWNERS["candidates/zig/mini_regex.zig"][0]
        and feature.get("independent_cpython_bridge", {}).get("sha256")
        == OWNERS["candidates/zig/py_bridge.c"][0]
        and type(matrix) is dict
        and matrix.get("matrix_sha256") == MATRIX_SHA256
        and matrix.get("matrix_case_count") == 1024
        and matrix.get("overflow_case_count") == 64
        and matrix.get("overflow_case_ids_sha256") == OVERFLOW_SHA256
        and matrix.get("overflow_family_case_counts")
        == {"nested-captures": 32, "numbered-captures": 16, "named-captures": 16}
        and matrix.get("preserved_nonoverflow_case_count") == 960
        and type(history) is dict
        and history.get("status") == "FAIL"
        and history.get("semantic_mismatch_count") == 1764
        and history.get("verified_passing_case_count") == 3711
        and history.get("actual_candidate_worker_count") == 13
        and history.get("case_execution_denominator") == 31237
        and value.get("qualified_candidate_count") == 0
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "bind native building exclusively to the genuine complete V4 Zig phrase fix",
    )


def validate_variant(original: bytes, corrected: bytes) -> None:
    previous = (
        b"        if not branches:\n"
        b'            raise RuntimeError("invalid SRE code")\n'
        b"        group_count = len(branches)\n"
    )
    replacement = (
        b"        group_count = len(branches)\n"
        b"        if not group_count or any(\n"
        b"            local_groups > group_count\n"
        b"            for _body, local_groups in branches\n"
        b"        ):\n"
        b'            raise RuntimeError("invalid SRE code")\n'
    )
    require(
        original.count(previous) == 1
        and original.count(replacement) == 0
        and corrected.count(previous) == 0
        and corrected.count(replacement) == 1
        and original.replace(previous, replacement, 1) == corrected
        and corrected.replace(replacement, previous, 1) == original
        and b"from candidates import _zig_bridge\n" in corrected,
        "reject any changed first-party adapter byte outside the V4 scanner correction",
    )
    try:
        ast.parse(corrected, filename="candidates/zig_candidate.py", mode="exec")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise FreezeError("reject a syntactically invalid complete V4 Zig adapter") from error


def validate_graph(value: dict[str, Any], *, inputs: bool = False) -> None:
    phrase = value.get("zig_scanner_phrase_v4_source_freeze")
    owners = phrase.get("owners") if type(phrase) is dict else None
    rust_v15 = value.get("actual_rust_v15_original_campaign")
    rust_receipt = rust_v15.get("receipt_owner") if type(rust_v15) is dict else None
    require(
        value.get("version") == GRAPH_VERSION
        and value.get("authenticated_evidence_owner_lower_bound")
        == EVIDENCE_LOWER_BOUND
        and value.get("authenticated_history_reference_lower_bound")
        == HISTORY_LOWER_BOUND
        and value.get("phase1_v4_oracle_readiness_status") == "PASS"
        and value.get("phase1_v4_candidate_testing_authorized") is True
        and value.get("first_party_source_inventory_family_count") == 6
        and value.get("qualified_candidate_count") == 0
        and value.get("zig_original_campaign_status") == "FAIL"
        and value.get("zig_original_campaign_semantic_mismatch_count") == 1764
        and value.get("zig_original_campaign_verified_passing_case_count") == 3711
        and value.get("zig_original_campaign_candidate_worker_count") == 13
        and value.get("zig_v1_official_compiler_path") == PINNED_ZIG
        and value.get("zig_v1_official_compiler_version") == "0.16.0"
        and value.get("zig_v1_official_compiler_sha256") == TOOLCHAINS["zig"][1]
        and value.get("zig_v1_official_compiler_bytes") == TOOLCHAINS["zig"][2]
        and value.get("zig_v12_source_build_status") == "PASS"
        and value.get("zig_v12_source_build_process_count") == 26
        and value.get("zig_v12_source_build_external_regex_dependency_count") == 0
        and value.get("zig_v12_source_build_cross_family_engine_count") == 0
        and value.get("zig_scanner_phrase_v4_status")
        == "SOURCE FROZEN; FIRST-PARTY ZIG VARIANT NOT BUILT OR TESTED"
        and value.get("zig_scanner_phrase_v4_complete_original_scanner_case_count") == 1024
        and value.get("zig_scanner_phrase_v4_corrected_original_scanner_case_count") == 64
        and value.get("zig_scanner_phrase_v4_preserved_original_scanner_case_count") == 960
        and value.get("zig_scanner_phrase_v4_candidate_build") == "NOT RUN"
        and value.get("zig_scanner_phrase_v4_candidate_matching") == "NOT RUN"
        and value.get("zig_scanner_phrase_v4_candidate_workers_started") == 0
        and value.get("zig_scanner_phrase_v4_actual_compiler_process_count") == 0
        and value.get("zig_scanner_phrase_v4_candidate_qualified") is False
        and type(phrase) is dict
        and phrase.get("schema")
        == "rebar-candidate-current-overview-v73-first-party-zig-scanner-source-v4"
        and phrase.get("status")
        == "SOURCE FROZEN; FIRST-PARTY ZIG VARIANT NOT BUILT OR TESTED"
        and phrase.get("complete_original_scanner_case_count") == 1024
        and phrase.get("corrected_original_scanner_case_count") == 64
        and phrase.get("preserved_original_scanner_case_count") == 960
        and phrase.get("historical_actual_zig_matching_status") == "FAIL"
        and phrase.get("historical_actual_zig_semantic_mismatch_count") == 1764
        and phrase.get("historical_actual_zig_verified_passing_case_count") == 3711
        and phrase.get("independent_feature_source_owner_count") == 4
        and type(owners) is dict
        and owners.get("source", {}).get("sha256")
        == OWNERS["tools/apply_owned_zig_scanner_phrase_source_repair_v4.py"][0]
        and owners.get("protocol", {}).get("sha256")
        == OWNERS["oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md"][0]
        and owners.get("contract", {}).get("sha256")
        == OWNERS["oracle/phase2/zig-scanner-phrase-source-repair-v4.json"][0]
        and owners.get("variant", {}).get("sha256")
        == OWNERS["candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"][0]
        and value.get("rust_native_build_v19_status") == "PASS"
        and value.get("rust_native_build_v19_compiler_process_count") == 28
        and value.get("rust_v11_original_campaign_execution_status")
        == "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"
        and value.get("rust_original_campaign_status") == "FAIL"
        and value.get("rust_original_campaign_semantic_mismatch_count") == 1440
        and value.get("rust_original_campaign_verified_passing_case_count") == 14853
        and value.get("rust_v15_original_campaign_actual_worker_count") == 13
        and value.get("rust_v15_original_campaign_started_suite_count") == 13
        and value.get("rust_v15_original_campaign_attempted_suite_count") == 13
        and value.get("rust_v15_original_campaign_distinct_worker_count") == 13
        and value.get("rust_v15_original_campaign_candidate_matching") == "FAIL"
        and value.get("rust_v15_original_campaign_candidate_qualified") is False
        and value.get("rust_v15_original_campaign_completed_suite_count") == 8
        and value.get("rust_v15_original_campaign_infrastructure_failure_count") == 5
        and value.get("rust_v15_original_campaign_semantic_mismatch_count")
        == "NOT MEASURED"
        and value.get("rust_v15_original_campaign_verified_passing_case_count") == 12942
        and value.get("rust_v15_original_campaign_worker_failure_capture_attempts") == 5
        and value.get("rust_v15_original_campaign_worker_failure_capture_complete") is True
        and value.get("rust_v15_original_campaign_complete_observation_vectors") is False
        and value.get("rust_v15_original_campaign_all_original_targets_restored") is True
        and value.get("rust_v15_original_campaign_outcome_receipt_sha256")
        == OWNERS[RUST_V15_RECEIPT_PATH][0]
        and value.get("rust_v15_original_campaign_publication_status") == "PASS"
        and value.get("rust_v15_original_campaign_publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and value.get("rust_v15_original_campaign_outcome_archive_opened_by_graph")
        is False
        and value.get("rust_v15_original_campaign_outcome_archive_inflated_by_graph")
        is False
        and type(rust_v15) is dict
        and rust_v15.get("schema")
        == "rebar-candidate-current-overview-v84-actual-rust-original-campaign-v15-outcome"
        and rust_v15.get("version") == 15
        and rust_v15.get("candidate_status") == "FAIL"
        and rust_v15.get("candidate_whole_project_qualified") is False
        and rust_v15.get("actual_candidate_worker_count") == 13
        and rust_v15.get("started_suite_count") == 13
        and rust_v15.get("attempted_suite_count") == 13
        and rust_v15.get("completed_suite_count") == 8
        and rust_v15.get("verified_passing_case_count") == 12942
        and rust_v15.get("semantic_mismatch_count") == "NOT MEASURED"
        and rust_v15.get("infrastructure_failure_count") == 5
        and rust_v15.get("worker_failure_capture_count") == 5
        and rust_v15.get("worker_failure_capture_complete") is True
        and rust_v15.get("all_original_observation_vectors_complete") is False
        and rust_v15.get("archive_opened_by_graph") is False
        and rust_v15.get("archive_inflated_by_graph") is False
        and rust_v15.get("archive_digest_recomputed_by_graph") is False
        and rust_v15.get("all_four_original_targets_restored") is True
        and rust_v15.get("restoration_verified_before_publication") is True
        and rust_v15.get("publication_status") == "PASS"
        and rust_v15.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and type(rust_receipt) is dict
        and rust_receipt.get("path") == RUST_V15_RECEIPT_PATH
        and rust_receipt.get("sha256") == OWNERS[RUST_V15_RECEIPT_PATH][0]
        and rust_receipt.get("bytes") == OWNERS[RUST_V15_RECEIPT_PATH][1]
        and value.get("c_native_build_v16_status") == "PASS"
        and value.get("c_native_build_v16_compiler_process_count") == 14
        and value.get("c_original_campaign_status") == "FAIL"
        and value.get("c_original_campaign_semantic_mismatch_count") == 1230
        and value.get("c_original_campaign_verified_passing_case_count") == 7325
        and value.get("clean_original_producer_v5_status")
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and value.get("clean_original_producer_v5_family_count") == 6
        and value.get("clean_original_producer_v5_first_party_source_owner_count") == 25
        and value.get("clean_original_producer_v5_source_owner_count") == 3
        and value.get("clean_original_producer_v5_original_case_count") == 31237
        and value.get("clean_original_producer_v5_original_suite_count") == 13
        and value.get("clean_original_producer_v5_original_obligation_count") == 73
        and value.get("clean_original_producer_v5_named_private_waiver_count") == 13
        and value.get("clean_original_producer_v5_separate_supplemental_case_count") == 8244
        and value.get("clean_original_producer_v5_actual_candidate_workers") == 0
        and value.get("clean_original_producer_v5_candidate_matching") == "NOT RUN"
        and value.get("clean_original_producer_v5_candidate_qualified") is False
        and value.get("final_holdout_opened") is False
        and value.get("performance") == "NOT MEASURED"
        and value.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and value.get("winner_selected") is False,
        "require genuine pushed V84 and preserve every actual matching/build outcome",
    )
    if not inputs:
        require(
            value.get("zig_v12_source_build_phase_count") == 2
            and value.get("zig_v12_source_build_stdlib_regex_engine_count") == 0
            and value.get("lossless_family_evidence_pool_schema")
            == "rebar-candidate-current-overview-v83-lossless-complete-family-proof-pool-v1"
            and value.get("lossless_family_evidence_pool_entry_count") == 9
            and value.get("lossless_family_references_per_family") == 9
            and value.get("lossless_actual_outcome_evidence_pool_schema")
            == "rebar-candidate-current-overview-v84-lossless-complete-actual-outcome-pool-v1"
            and value.get("lossless_actual_outcome_evidence_pool_entry_count") == 1
            and value.get("lossless_actual_outcome_references_per_family") == 1
            and value.get("phase1_differential_fuzz_reference_v3_reference_case_count")
            == 8244
            and value.get("phase1_differential_fuzz_reference_v3_execution_status")
            == "PASS"
            and value.get("phase1_differential_fuzz_reference_v3_actual_worker_case_counts")
            == [8244, 8244]
            and value.get("phase1_differential_fuzz_reference_v3_actual_worker_failure_counts")
            == [0, 0]
            and value.get("zig_original_campaign_case_execution_denominator") == 31237
            and value.get("zig_original_campaign_completed_suite_count") == 13
            and value.get("zig_original_campaign_private_waiver_count") == 13,
            "retain exact actual Zig denominator, waivers, and reference results",
        )


def checked_root(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded exclusive private build root")
    parsed = PurePosixPath(value)
    require(parsed.is_absolute() and str(parsed) == value,
            "require a canonical absolute private root")
    parts = parsed.parts
    require(
        len(parts) == 3 and parts[1] == "tmp"
        and parts[2].startswith(PRIVATE_ROOT_PREFIX),
        "reject broad, cross-family, historical, or escaped build roots",
    )
    suffix = parts[2][len(PRIVATE_ROOT_PREFIX):]
    require(
        len(suffix) >= 8
        and all(char.isascii() and (char.isalnum() or char in "-_")
                for char in suffix),
        "require a fresh bounded owner-specific private root suffix",
    )
    return value


def checked_label(value: Any) -> str:
    require(
        type(value) is str
        and 1 <= len(value) <= 64
        and value[0].isascii() and value[0].islower()
        and all(char.isascii() and (char.islower() or char.isdigit() or char == "-")
                for char in value)
        and "--" not in value and not value.endswith("-")
        and value not in ("holdout", "performance", "benchmarks"),
        "require one exclusive lowercase, bounded, deterministic build label",
    )
    return value


def phase_paths(workdir: str, phase: str) -> dict[str, Path]:
    root = Path(checked_root(workdir))
    require(type(phase) is str and phase in PHASE_NAMES,
            "require exactly two independently owned phase names")
    base = root / phase
    source = base / "source"
    native = base / "native"
    return {
        "base": base,
        "source": source,
        "source_candidates": source / "candidates",
        "source_zig": source / "candidates" / "zig",
        "source_adapter": source / "candidates" / "zig_candidate.py",
        "source_engine": source / "candidates" / "zig" / "mini_regex.zig",
        "source_bridge": source / "candidates" / "zig" / "py_bridge.c",
        "native": native,
        "artifact_engine": native / ENGINE_NAME,
        "artifact_bridge": native / BRIDGE_NAME,
        "temporary": base / "temporary",
        "zig_local_cache": base / "zig-local-cache",
        "zig_global_cache": base / "zig-global-cache",
    }


def prefix_flags(workdir: str) -> list[str]:
    checked_root(workdir)
    return [
        "-ffile-prefix-map=" + str(phase_paths(workdir, phase)["source"])
        + "=" + CANONICAL_SOURCE_PREFIX
        for phase in PHASE_NAMES
    ]


def build_environment(workdir: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, phase)
    return {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
        "ZIG_LOCAL_CACHE_DIR": str(paths["zig_local_cache"]),
        "ZIG_GLOBAL_CACHE_DIR": str(paths["zig_global_cache"]),
    }


def planned_commands(workdir: str, phase: str) -> dict[str, list[str]]:
    paths = phase_paths(workdir, phase)
    commands: dict[str, list[str]] = {
        "readelf_version": [PINNED_READELF, "--version"],
        "gcc_version": [PINNED_GCC, "--version"],
        "zig_version": [PINNED_ZIG, "version"],
        "build_zig_engine": [
            PINNED_ZIG, "build-lib", str(paths["source_engine"]),
            "-dynamic", "-lc", "-O", "ReleaseFast", "-fstrip",
            "-fallow-shlib-undefined", "-fsoname=" + ENGINE_NAME,
            "--cache-dir", str(paths["zig_local_cache"]),
            "--global-cache-dir", str(paths["zig_global_cache"]),
            "-femit-bin=" + str(paths["artifact_engine"]),
        ],
        "build_zig_bridge": [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=sha1",
            *prefix_flags(workdir),
            "-I" + PINNED_INCLUDE,
            str(paths["source_bridge"]),
            "-L" + str(paths["native"]),
            "-l:" + ENGINE_NAME,
            "-Wl,-rpath,$ORIGIN",
            "-o", str(paths["artifact_bridge"]),
        ],
    }
    for role in ("engine", "bridge"):
        target = str(paths["artifact_" + role])
        commands[role + "_dynamic"] = [PINNED_READELF, "--dynamic", "--wide", target]
        commands[role + "_symbols"] = [PINNED_READELF, "--dyn-syms", "--wide", target]
        commands[role + "_sections"] = [PINNED_READELF, "--sections", "--wide", target]
        commands[role + "_notes"] = [PINNED_READELF, "--notes", "--wide", target]
    require(tuple(commands) == PROCESS_ROLES and len(commands) == 13,
            "require the exact thirteen direct first-party compiler/inspection roles")
    return commands


def checked_command(name: Any, argv: Any, workdir: str, phase: str) -> list[str]:
    expected = planned_commands(workdir, phase)
    require(
        type(name) is str and name in expected
        and type(argv) is list
        and all(type(item) is str and "\x00" not in item for item in argv)
        and argv == expected[name]
        and argv[0] in (PINNED_ZIG, PINNED_GCC, PINNED_READELF),
        "reject shell, substituted compiler, network, cross-phase, or external engine",
    )
    return list(argv)


def sanitized(value: Any, workdir: str) -> Any:
    root = checked_root(workdir)
    if type(value) is str:
        return value.replace(root, "<FRESH_PRIVATE_ROOT>")
    if type(value) is list:
        return [sanitized(item, root) for item in value]
    if type(value) is dict:
        return {key: sanitized(item, root) for key, item in value.items()}
    return value


def command_templates() -> list[dict[str, Any]]:
    root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic00000001"
    return [
        {
            "phase": phase,
            "working_directory": sanitized(str(phase_paths(root, phase)["base"]), root),
            "environment": sanitized(build_environment(root, phase), root),
            "processes": [
                {"role": role, "argv": sanitized(argv, root)}
                for role, argv in planned_commands(root, phase).items()
            ],
        }
        for phase in PHASE_NAMES
    ]


def source_boundaries() -> dict[str, Any]:
    return {
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "compiler_processes_started": 0,
        "compiler_binaries_executed": 0,
        "native_libraries_loaded": 0,
        "native_activations": 0,
        "private_roots_created": 0,
        "private_phase_directories_created": 0,
        "private_source_files_written": 0,
        "private_root_receipts_published": 0,
        "build_receipts_published": 0,
        "matching_archives_opened": 0,
        "matching_archives_inflated": 0,
        "reference_archives_opened": 0,
        "holdout_files_opened": 0,
        "benchmark_files_opened": 0,
        "network_requests": 0,
        "clock_samples": 0,
        "files_written": 0,
    }


def graph_options(options: argparse.Namespace) -> None:
    actual = (
        options.graph_source_sha256,
        options.graph_inputs_sha256,
        options.graph_summary_sha256,
        options.graph_svg_sha256,
    )
    require(
        tuple(checked_sha(value, "V84 graph owner") for value in actual)
        == tuple(OWNERS[path][0] for path in GRAPH_PATHS),
        "independently caller-pin all four genuinely committed V84 graph owners",
    )


def authenticate_context(options: argparse.Namespace) -> dict[str, Any]:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON,
        "require pinned, isolated, no-bytecode stable CPython 3.14.6",
    )
    graph_options(options)
    source_size = os.stat(ROOT / SOURCE_PATH, follow_symlinks=False).st_size
    source_owner, source = read_repository_owner(
        SOURCE_PATH, checked_sha(options.source_sha256, "V13 source"), source_size,
    )
    protocol_size = os.stat(ROOT / PROTOCOL_PATH, follow_symlinks=False).st_size
    protocol_owner, protocol = read_repository_owner(
        PROTOCOL_PATH, checked_sha(options.protocol_sha256, "V13 protocol"),
        protocol_size,
    )
    owners: dict[str, dict[str, Any]] = {}
    protected: dict[str, bytes] = {}
    for path, (fingerprint, size) in OWNERS.items():
        owners[path], protected[path] = read_repository_owner(path, fingerprint, size)
    validate_phase_one(strict_json(
        protected["oracle/phase1/p0-completeness-v1.json"], "original P0",
    ))
    readiness = strict_json(protected["oracle/phase1/p0-completeness-v4.json"],
                            "actual phase-one V4 readiness")
    validate_readiness(readiness)
    supplemental = next(
        path for path in OWNERS if path.endswith("two-independent-reference-result.json")
    )
    validate_supplement(strict_json(protected[supplemental], "supplemental reference"))
    rust_v15_receipt = strict_json(
        protected[RUST_V15_RECEIPT_PATH],
        "actual Rust V15 plaintext partial-failure receipt",
    )
    validate_actual_rust_v15(rust_v15_receipt)
    producer = strict_json(
        protected["oracle/phase2/six-family-p0-producer-v4.json"],
        "independent first-party six-family original producer",
    )
    require(
        producer.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
        and producer.get("version") == 4
        and producer.get("case_execution_denominator") == 31237
        and producer.get("suite_count") == 13
        and producer.get("status")
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        "preserve the actual independent original six-family producer",
    )
    feature = strict_json(
        protected["oracle/phase2/zig-scanner-phrase-source-repair-v4.json"],
        "independently published complete V4 Zig source correction",
    )
    validate_feature(feature)
    validate_variant(
        protected["candidates/zig_candidate.py"],
        protected["candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"],
    )
    lock = strict_json(
        protected["toolchains/zig-0.16.0.lock.json"],
        "official offline Zig lock",
        canonical_required=False,
    )
    validate_lock(lock)
    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v84.inputs.json"],
        "committed V84 graph inputs",
    )
    graph = strict_json(
        protected["docs/evidence/candidate-current-overview-v84.json"],
        "committed V84 graph summary",
    )
    validate_graph(inputs, inputs=True)
    validate_graph(graph)
    tools = {name: read_external_owner(name) for name in TOOLCHAINS}
    return {
        "source": source,
        "source_owner": source_owner,
        "protocol": protocol,
        "protocol_owner": protocol_owner,
        "owners": owners,
        "protected": protected,
        "readiness": readiness,
        "feature": feature,
        "graph": graph,
        "graph_inputs": inputs,
        "rust_v15_receipt": rust_v15_receipt,
        "toolchains": tools,
    }


def contract_document(context: dict[str, Any]) -> dict[str, Any]:
    graph = context["graph"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; CORRECTED ZIG BUILD NOT RUN",
        "phase": "PHASE 2 FIRST-PARTY ZIG V4 PHRASE NATIVE BUILD SOURCE FREEZE",
        "source": context["source_owner"],
        "protocol": context["protocol_owner"],
        "current_graph": {
            "version": GRAPH_VERSION,
            "owners": [context["owners"][path] for path in GRAPH_PATHS],
            "authenticated_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND,
            "authenticated_history_reference_lower_bound": HISTORY_LOWER_BOUND,
            "lower_bounds_are_complete_repository_census": False,
            "source_freeze_new_evidence_owner_count": 0,
            "prospective_independent_feature_source_owner_count": 3,
            "prospective_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND + 3,
            "prospective_history_reference_lower_bound": HISTORY_LOWER_BOUND + 3,
        },
        "original_oracle": {
            "python_implementation": "CPython",
            "python_version": "3.14.6",
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "original_named_private_waiver_count": 13,
            "mapped_original_obligation_count": 73,
            "original_crosswalk_count": 34,
            "supplemental_reference_case_count": 8244,
            "supplemental_reference_worker_count": 2,
            "supplemental_cases_added_to_original_denominator": False,
            "supplemental_candidate_status": "NOT RUN",
        },
        "first_party_phrase_repair": {
            "version": 4,
            "family": "zig",
            "source": context["owners"][
                "tools/apply_owned_zig_scanner_phrase_source_repair_v4.py"
            ],
            "protocol": context["owners"][
                "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md"
            ],
            "contract": context["owners"][
                "oracle/phase2/zig-scanner-phrase-source-repair-v4.json"
            ],
            "complete_corrected_adapter": context["owners"][
                "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"
            ],
            "unchanged_original_adapter": context["owners"][
                "candidates/zig_candidate.py"
            ],
            "first_party_zig_parser_compiler_executor": context["owners"][
                "candidates/zig/mini_regex.zig"
            ],
            "first_party_cpython_c_api_bridge": context["owners"][
                "candidates/zig/py_bridge.c"
            ],
            "complete_original_scanner_matrix_case_count": 1024,
            "scanner_matrix_sha256": MATRIX_SHA256,
            "corrected_source_witness_count": 64,
            "corrected_source_witness_ids_sha256": OVERFLOW_SHA256,
            "preserved_original_scanner_case_count": 960,
            "original_engine_modified": False,
            "original_bridge_modified": False,
            "original_adapter_modified": False,
            "additional_candidate_family_count": 0,
            "corrected_candidate_matching": "NOT RUN",
        },
        "offline_toolchain": {
            "lock": context["owners"]["toolchains/zig-0.16.0.lock.json"],
            "owners": [context["toolchains"][name] for name in TOOLCHAINS],
            "zig_version": "0.16.0",
            "zig_exact_executable": PINNED_ZIG,
            "compiler_binaries_executed": 0,
            "network_requests": 0,
        },
        "preserved_actual_history": {
            "zig_original_matching": {
                "status": graph["zig_original_campaign_status"],
                "semantic_mismatch_count": graph[
                    "zig_original_campaign_semantic_mismatch_count"
                ],
                "verified_passing_case_count": graph[
                    "zig_original_campaign_verified_passing_case_count"
                ],
                "candidate_worker_count": graph[
                    "zig_original_campaign_candidate_worker_count"
                ],
                "case_execution_denominator": graph[
                    "zig_original_campaign_case_execution_denominator"
                ],
            },
            "rust_v19_native_build": {
                "status": graph["rust_native_build_v19_status"],
                "compiler_process_count": graph[
                    "rust_native_build_v19_compiler_process_count"
                ],
            },
            "rust_v11_original_campaign": {
                "status": graph["rust_v11_original_campaign_execution_status"],
            },
            "rust_original_matching": {
                "status": graph["rust_original_campaign_status"],
                "semantic_mismatch_count": graph[
                    "rust_original_campaign_semantic_mismatch_count"
                ],
                "verified_passing_case_count": graph[
                    "rust_original_campaign_verified_passing_case_count"
                ],
            },
            "actual_rust_v15_original_matching": {
                "candidate_status": graph[
                    "rust_v15_original_campaign_candidate_matching"
                ],
                "candidate_qualified": graph[
                    "rust_v15_original_campaign_candidate_qualified"
                ],
                "actual_candidate_worker_count": graph[
                    "rust_v15_original_campaign_actual_worker_count"
                ],
                "started_suite_count": graph[
                    "rust_v15_original_campaign_started_suite_count"
                ],
                "attempted_suite_count": graph[
                    "rust_v15_original_campaign_attempted_suite_count"
                ],
                "completed_suite_count": graph[
                    "rust_v15_original_campaign_completed_suite_count"
                ],
                "semantic_mismatch_count": graph[
                    "rust_v15_original_campaign_semantic_mismatch_count"
                ],
                "verified_passing_case_count": graph[
                    "rust_v15_original_campaign_verified_passing_case_count"
                ],
                "infrastructure_failure_count": graph[
                    "rust_v15_original_campaign_infrastructure_failure_count"
                ],
                "worker_failure_capture_count": graph[
                    "rust_v15_original_campaign_worker_failure_capture_attempts"
                ],
                "worker_failure_capture_complete": graph[
                    "rust_v15_original_campaign_worker_failure_capture_complete"
                ],
                "all_original_observation_vectors_complete": graph[
                    "rust_v15_original_campaign_complete_observation_vectors"
                ],
                "all_original_targets_restored": graph[
                    "rust_v15_original_campaign_all_original_targets_restored"
                ],
                "publication_status": graph[
                    "rust_v15_original_campaign_publication_status"
                ],
                "publication_pass_means": graph[
                    "rust_v15_original_campaign_publication_pass_means"
                ],
                "plaintext_receipt": context["owners"][RUST_V15_RECEIPT_PATH],
                "matching_archive_opened": False,
                "matching_archive_inflated": False,
                "publication_is_candidate_correctness": False,
            },
            "c_native_build": {
                "status": graph["c_native_build_v16_status"],
                "compiler_process_count": graph[
                    "c_native_build_v16_compiler_process_count"
                ],
            },
            "c_original_matching": {
                "status": graph["c_original_campaign_status"],
                "semantic_mismatch_count": graph[
                    "c_original_campaign_semantic_mismatch_count"
                ],
                "verified_passing_case_count": graph[
                    "c_original_campaign_verified_passing_case_count"
                ],
            },
            "lossless_family_evidence_pool": {
                "schema": graph["lossless_family_evidence_pool_schema"],
                "entry_count": graph["lossless_family_evidence_pool_entry_count"],
                "references_per_family": graph[
                    "lossless_family_references_per_family"
                ],
            },
            "lossless_actual_outcome_evidence_pool": {
                "schema": graph["lossless_actual_outcome_evidence_pool_schema"],
                "entry_count": graph[
                    "lossless_actual_outcome_evidence_pool_entry_count"
                ],
                "references_per_family": graph[
                    "lossless_actual_outcome_references_per_family"
                ],
            },
            "complete_proof_references_across_six_families": (
                graph["first_party_source_inventory_family_count"]
                * (
                    graph["lossless_family_references_per_family"]
                    + graph["lossless_actual_outcome_references_per_family"]
                )
            ),
        },
        "future_native_build": {
            "authorization": "EXPLICIT --build --label AFTER COMMITTED SOURCE FREEZE",
            "status": "NOT RUN",
            "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
            "private_root_mode": "0700",
            "private_source_mode": "0600",
            "phase_names": list(PHASE_NAMES),
            "independent_phase_count": 2,
            "independent_source_owners_per_phase": 3,
            "native_roles_per_phase": ["engine", "bridge"],
            "process_roles_per_phase": list(PROCESS_ROLES),
            "expected_process_count_per_phase": 13,
            "expected_process_count_only_after_both_phases": 26,
            "actual_process_count": 0,
            "actual_source_snapshot_count": 0,
            "actual_private_root_receipt_count": 0,
            "actual_build_receipt_count": 0,
            "byte_identical_engine_and_bridge": "NOT MEASURED",
            "full_native_elf_audit": "NOT RUN",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "private_root_receipt_schema": SCHEMA + "-private-root-receipt",
            "build_receipt_schema": SCHEMA + "-plaintext-build-receipt",
            "private_root_receipt_template": (
                EVIDENCE_PATH + "/zig-scanner-phrase-source-build-v13-"
                "<FRESH_LABEL>-private-root-receipt.json"
            ),
            "build_receipt_template": (
                EVIDENCE_PATH + "/zig-scanner-phrase-source-build-v13-"
                "<FRESH_LABEL>-build-receipt.json"
            ),
            "receipts_are_exclusive_plaintext_json": True,
            "compressed_evidence_owner_count": 0,
            "failure_cleanup_restricts_exact_owned_private_root": True,
            "planned_commands": command_templates(),
        },
        "from_scratch_policy": {
            "stdlib_regex_engine": "FORBIDDEN",
            "stdlib_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "prebuilt_matching_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "network_fetch": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "source_only_effects": source_boundaries(),
        "frozen_source_owners": [context["owners"][path] for path in OWNERS],
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def checked_private_child(path: Any, workdir: str, phase: str) -> Path:
    root = Path(checked_root(workdir))
    require(
        isinstance(path, Path)
        and path.is_absolute()
        and path != root
        and phase in PHASE_NAMES
        and path.is_relative_to(root / phase)
        and all(part not in (".", "..") and "\\" not in part
                and "\x00" not in part for part in path.parts),
        "restrict all build writes to the exact independently owned phase",
    )
    return path


def directory_owner(descriptor: int, path: str) -> dict[str, Any]:
    info = os.fstat(descriptor)
    require(
        stat.S_ISDIR(info.st_mode)
        and info.st_uid == os.geteuid()
        and stat.S_IMODE(info.st_mode) == 0o700,
        "require an owned, non-symlinked mode-0700 private directory: " + path,
    )
    return {
        "path": path,
        "device": info.st_dev,
        "inode": info.st_ino,
        "uid": info.st_uid,
        "mode": "0700",
    }


def create_phase_directory(path: Path, workdir: str, phase: str) -> dict[str, Any]:
    checked = checked_private_child(path, workdir, phase)
    os.mkdir(str(checked), 0o700)
    descriptor = os.open(
        str(checked), os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW,
    )
    try:
        return directory_owner(descriptor, str(checked))
    finally:
        os.close(descriptor)


def open_private_directory(
    workdir: str, phase: str, components: tuple[str, ...],
) -> tuple[int, dict[str, Any]]:
    root = checked_root(workdir)
    require(
        phase in PHASE_NAMES and type(components) is tuple
        and all(type(part) is str and part not in ("", ".", "..")
                and "/" not in part and "\\" not in part and "\x00" not in part
                for part in components),
        "reject any escaped or substituted private phase component",
    )
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    root_descriptor = os.open(root, flags)
    current: int | None = root_descriptor
    try:
        directory_owner(current, root)
        for part in (phase, *components):
            following = os.open(part, flags, dir_fd=current)
            directory_owner(following, part)
            os.close(current)
            current = following
        require(current is not None, "require one authenticated private directory")
        label = str(Path(root) / phase / Path(*components))
        metadata = directory_owner(current, label)
        result = current
        current = None
        return result, metadata
    finally:
        if current is not None:
            os.close(current)


def prepare_phases(workdir: str) -> list[dict[str, Any]]:
    root = checked_root(workdir)
    phases: list[dict[str, Any]] = []
    for phase in PHASE_NAMES:
        paths = phase_paths(root, phase)
        directories: dict[str, dict[str, Any]] = {}
        for key in (
            "base", "source", "source_candidates", "source_zig",
            "native", "temporary", "zig_local_cache", "zig_global_cache",
        ):
            directories[key] = create_phase_directory(paths[key], root, phase)
        phases.append({"name": phase, "directories": directories})
    require(
        len({(item["directories"]["base"]["device"],
              item["directories"]["base"]["inode"]) for item in phases}) == 2,
        "require two actually distinct fresh first-party phase roots",
    )
    return phases


def write_private_source(
    workdir: str, phase: str, destination: str,
    raw: bytes, fingerprint: str,
) -> dict[str, Any]:
    relative = safe_relative(destination)
    require(
        destination in (
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
            "candidates/zig_candidate.py",
        )
        and type(raw) is bytes and digest(raw) == checked_sha(fingerprint, destination),
        "snapshot only complete genuine first-party Zig engine, bridge, or V4 adapter",
    )
    directory, _directory_owner = open_private_directory(
        workdir, phase, ("source", *relative[:-1]),
    )
    descriptor: int | None = None
    try:
        descriptor = os.open(
            relative[-1],
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "create one exclusively owned mode-0600 phase source",
        )
        offset = 0
        while offset < len(raw):
            written = os.write(descriptor, raw[offset:])
            require(type(written) is int and written > 0,
                    "persist every complete first-party phase-source byte")
            offset += written
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
            and after.st_size == len(raw),
            "reject a swapped or incomplete corrected phase source",
        )
        os.close(descriptor)
        descriptor = None
        verify = os.open(
            relative[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
            dir_fd=directory,
        )
        try:
            label = str(phase_paths(workdir, phase)["source"] / destination)
            owner, repeated = read_descriptor(
                verify, fingerprint, len(raw), MAX_SOURCE_BYTES, label,
                private=True,
            )
        finally:
            os.close(verify)
        require(repeated == raw and (owner["device"], owner["inode"])
                == (after.st_dev, after.st_ino),
                "verify complete corrected source through the same fresh inode")
        os.fsync(directory)
        return owner
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "bound the complete genuine compiler or ELF inspection output")
    return {
        "sha256": digest(raw),
        "bytes": len(raw),
        "base64": base64.b64encode(raw).decode("ascii"),
    }


def decode_stream(value: Any) -> bytes:
    require(type(value) is dict and type(value.get("base64")) is str,
            "require one complete canonical process stream")
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise FreezeError("reject malformed actual compiler output") from error
    require(
        len(raw) <= MAX_PROCESS_BYTES
        and value.get("bytes") == len(raw)
        and value.get("sha256") == digest(raw),
        "reject omitted or substituted compiler output bytes",
    )
    return raw


def run_process(
    name: str, workdir: str, phase: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    argv = checked_command(name, planned_commands(workdir, phase)[name], workdir, phase)
    cwd = str(phase_paths(workdir, phase)["base"])
    environment = build_environment(workdir, phase)
    process = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=environment,
        shell=False,
        close_fds=True,
    )
    stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes,
            "capture every actual process byte without shell delegation")
    record = {
        "phase": phase,
        "role": name,
        "argv": argv,
        "working_directory": cwd,
        "environment": environment,
        "pid": process.pid,
        "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    records.append(record)
    require(process.returncode == 0,
            "preserve the genuine failed compiler or inspection role: "
            + phase + "/" + name)
    if name == "zig_version":
        require(stdout == b"0.16.0\n", "reject a replaced stable Zig compiler")
    if name in ("gcc_version", "readelf_version") or name.endswith(
        ("_dynamic", "_symbols", "_sections")
    ):
        require(bool(stdout), "retain complete nonempty actual compiler/ELF output")
    return record


def validate_elf_header(raw: bytes, role: str) -> None:
    require(
        role in ("engine", "bridge")
        and type(raw) is bytes and 64 <= len(raw) <= MAX_NATIVE_BYTES
        and raw[:4] == b"\x7fELF"
        and raw[4] == 2 and raw[5] == 1 and raw[6] == 1,
        "require one complete genuine little-endian ELF64 first-party native artifact",
    )
    try:
        elf_type, machine, elf_version = struct.unpack_from("<HHI", raw, 16)
    except struct.error as error:
        raise FreezeError("reject an incomplete native ELF header") from error
    require(elf_type == 3 and machine == 62 and elf_version == 1,
            "require an actual x86-64 ET_DYN Zig engine or CPython bridge")


def capture_native(workdir: str, phase: str, role: str) -> tuple[
    dict[str, Any], bytes
]:
    require(role in ("engine", "bridge"), "capture only the two owned native roles")
    directory, _metadata = open_private_directory(workdir, phase, ("native",))
    filename = ENGINE_NAME if role == "engine" else BRIDGE_NAME
    descriptor = os.open(
        filename, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=directory,
    )
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and 64 <= before.st_size <= MAX_NATIVE_BYTES,
            "require a fresh exclusively owned complete native phase artifact",
        )
        chunks: list[bytes] = []
        total = 0
        while True:
            remaining = min(1024 * 1024, MAX_NATIVE_BYTES + 1 - total)
            require(remaining > 0, "reject oversized phase native artifact")
            chunk = os.read(descriptor, remaining)
            if not chunk:
                break
            total += len(chunk)
            require(total <= MAX_NATIVE_BYTES, "reject oversized phase native artifact")
            chunks.append(chunk)
        after = os.fstat(descriptor)
        require(
            (
                before.st_dev, before.st_ino, before.st_size, before.st_uid,
                before.st_nlink, before.st_mtime_ns, before.st_ctime_ns,
            ) == (
                after.st_dev, after.st_ino, after.st_size, after.st_uid,
                after.st_nlink, after.st_mtime_ns, after.st_ctime_ns,
            )
            and total == before.st_size,
            "reject a changed, incomplete, or substituted private ELF artifact",
        )
        raw = b"".join(chunks)
        validate_elf_header(raw, role)
        return owner_metadata(str(phase_paths(workdir, phase)["artifact_" + role]),
                              after, digest(raw)), raw
    finally:
        os.close(descriptor)
        os.close(directory)


def dynamic_fields(raw: bytes) -> dict[str, list[str]]:
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeError as error:
        raise FreezeError("reject malformed pinned readelf dynamic output") from error
    result: dict[str, list[str]] = {
        "needed": [], "soname": [], "runpath": [], "rpath": [],
    }
    tokens = {
        "(NEEDED)": "needed", "(SONAME)": "soname",
        "(RUNPATH)": "runpath", "(RPATH)": "rpath",
    }
    for line in text.splitlines():
        for token, key in tokens.items():
            if token not in line:
                continue
            begin = line.find("[")
            end = line.find("]", begin + 1)
            require(begin >= 0 and end > begin,
                    "reject malformed actual dynamic dependency")
            name = line[begin + 1:end]
            require(name and "\x00" not in name,
                    "reject an empty or malformed native dependency")
            result[key].append(name)
            break
    require(all(len(items) == len(set(items)) for items in result.values()),
            "reject repeated or redirected native dynamic dependencies")
    return result


def dynamic_symbols(raw: bytes) -> tuple[set[str], set[str]]:
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeError as error:
        raise FreezeError("reject malformed pinned readelf symbol output") from error
    defined: set[str] = set()
    undefined: set[str] = set()
    for line in text.splitlines():
        pieces = line.split()
        if len(pieces) < 8 or not pieces[0].endswith(":"):
            continue
        index = pieces[0][:-1]
        if not index.isascii() or not index.isdecimal():
            continue
        name = pieces[7].split("@", 1)[0]
        if not name:
            continue
        require(
            name not in FORBIDDEN_SYMBOLS
            and not any(name.lower().startswith(prefix)
                        for prefix in FORBIDDEN_PREFIXES),
            "reject stdlib matching, external regex, native loader, or another family: "
            + name,
        )
        (undefined if pieces[6] == "UND" else defined).add(name)
    require(bool(defined or undefined), "require a genuine nonempty ELF symbol table")
    require(not (defined & undefined), "reject ambiguous owned/imported native symbols")
    return defined, undefined


def audit_native(
    role: str,
    dynamic_output: bytes,
    symbol_output: bytes,
    sections_output: bytes,
) -> dict[str, Any]:
    require(role in ("engine", "bridge"), "audit only a first-party native role")
    require(bool(sections_output), "retain the complete real ELF section listing")
    fields = dynamic_fields(dynamic_output)
    defined, undefined = dynamic_symbols(symbol_output)
    require(not fields["rpath"], "forbid insecure legacy native library lookup")
    if role == "engine":
        require(
            fields["needed"] == ["libc.so.6"]
            and fields["soname"] == [ENGINE_NAME]
            and not fields["runpath"]
            and REQUIRED_ENGINE_EXPORTS.issubset(defined)
            and {item for item in undefined if item.startswith("_PyUnicode_")}
            == ALLOWED_UNICODE_HELPERS
            and not any(item.startswith("rebar_") for item in undefined),
            "bind the Zig parser/executor only to libc and original Unicode helpers",
        )
    else:
        require(
            fields["needed"] == [ENGINE_NAME, "libc.so.6"]
            and not fields["soname"]
            and fields["runpath"] == ["$ORIGIN"]
            and "PyInit__zig_bridge" in defined
            and REQUIRED_BRIDGE_IMPORTS.issubset(undefined)
            and {item for item in undefined if item.startswith("rebar_")}
            == REQUIRED_BRIDGE_IMPORTS,
            "link the real CPython C-API bridge only to its own adjacent Zig engine",
        )
    return {
        "role": role,
        "needed": fields["needed"],
        "soname": fields["soname"][0] if fields["soname"] else None,
        "runpath": fields["runpath"][0] if fields["runpath"] else None,
        "legacy_rpath_count": 0,
        "defined_dynamic_symbol_count": len(defined),
        "undefined_dynamic_symbol_count": len(undefined),
        "defined_first_party_symbols": sorted(
            item for item in defined if item.startswith("rebar_zig_")
        ),
        "imported_first_party_symbols": sorted(
            item for item in undefined if item.startswith("rebar_zig_")
        ),
        "allowed_unicode_helpers": sorted(
            item for item in undefined if item in ALLOWED_UNICODE_HELPERS
        ),
        "external_regex_dependency_count": 0,
        "stdlib_regex_engine_count": 0,
        "cross_family_engine_count": 0,
        "native_loader_dependency_count": 0,
    }


def validate_schedule(records: Any, workdir: str, *, complete: bool) -> None:
    require(type(records) is list, "require genuine ordered native process receipts")
    expected = [(phase, role) for phase in PHASE_NAMES for role in PROCESS_ROLES]
    require(len(records) <= len(expected), "reject excess or invented process roles")
    if complete:
        require(len(records) == 26, "claim 26 roles only after 26 actual processes")
    seen: set[int] = set()
    for offset, record in enumerate(records):
        phase, role = expected[offset]
        require(type(record) is dict, "reject a malformed real process record")
        require(record.get("phase") == phase and record.get("role") == role,
                "reject a reordered, duplicated, missing, or cross-phase process")
        checked_command(role, record.get("argv"), workdir, phase)
        require(
            record.get("working_directory") == str(phase_paths(workdir, phase)["base"])
            and record.get("environment") == build_environment(workdir, phase),
            "require the exact owner-only phase and sanitized process environment",
        )
        pid = record.get("pid")
        require(type(pid) is int and pid > 0 and pid not in seen,
                "require an independently observed unique child process identity")
        seen.add(pid)
        require(record.get("returncode") == 0 and record.get("signal") is None,
                "reject crashed, incomplete, or failed compiler inspection")
        decode_stream(record.get("stdout"))
        decode_stream(record.get("stderr"))


def evidence_names(label: str) -> tuple[str, str]:
    selected = checked_label(label)
    prefix = "zig-scanner-phrase-source-build-v13-" + selected
    return prefix + "-private-root-receipt.json", prefix + "-build-receipt.json"


def evidence_directory() -> int:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    current = os.open(str(ROOT), flags)
    try:
        for part in safe_relative(EVIDENCE_PATH):
            following = os.open(part, flags, dir_fd=current)
            info = os.fstat(following)
            require(
                stat.S_ISDIR(info.st_mode)
                and info.st_uid == os.geteuid()
                and stat.S_IMODE(info.st_mode) == 0o700,
                "require exclusively owned evidence publication directories",
            )
            os.close(current)
            current = following
        result = current
        current = -1
        return result
    finally:
        if current >= 0:
            os.close(current)


def require_fresh_evidence(label: str) -> None:
    directory = evidence_directory()
    try:
        for name in evidence_names(label):
            try:
                os.stat(name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise FreezeError("never reuse an existing plaintext Zig receipt: " + name)
    finally:
        os.close(directory)


def exclusive_plaintext(
    directory: int, filename: str, document: dict[str, Any],
) -> dict[str, Any]:
    require(
        type(filename) is str and filename.endswith(".json")
        and filename not in ("", ".", "..")
        and "/" not in filename and "\\" not in filename,
        "publish only one exclusive plaintext Zig evidence owner",
    )
    raw = canonical(document)
    require(0 < len(raw) <= MAX_RECEIPT_BYTES,
            "bound complete independently durable plaintext build evidence")
    descriptor: int | None = None
    try:
        descriptor = os.open(
            filename,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "require a fresh nonlinked owned plaintext receipt",
        )
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(type(count) is int and count > 0,
                    "durably publish every original plaintext evidence byte")
            offset += count
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
            and after.st_size == len(raw),
            "reject swapped or incomplete plaintext Zig build evidence",
        )
        os.close(descriptor)
        descriptor = None
        verify = os.open(
            filename, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=directory,
        )
        try:
            owner, repeated = read_descriptor(
                verify, digest(raw), len(raw), MAX_RECEIPT_BYTES,
                EVIDENCE_PATH + "/" + filename,
                private=True,
            )
        finally:
            os.close(verify)
        require(repeated == raw and (owner["device"], owner["inode"])
                == (after.st_dev, after.st_ino),
                "independently reread every durable receipt through its original inode")
        os.fsync(directory)
        return {**owner, "file_fsync": True, "directory_fsync": True}
    finally:
        if descriptor is not None:
            os.close(descriptor)


def cleanup_directory_contents(descriptor: int) -> None:
    for name in os.listdir(descriptor):
        require(
            type(name) is str and name not in ("", ".", "..")
            and "/" not in name and "\\" not in name and "\x00" not in name,
            "reject any escaped or untrusted cleanup target",
        )
        info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        require(info.st_uid == os.geteuid(),
                "clean only children owned by the actual exclusive build user")
        if stat.S_ISDIR(info.st_mode):
            child = os.open(
                name,
                os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptor,
            )
            try:
                current = os.fstat(child)
                require((current.st_dev, current.st_ino)
                        == (info.st_dev, info.st_ino),
                        "reject a replaced cleanup directory")
                cleanup_directory_contents(child)
            finally:
                os.close(child)
            os.rmdir(name, dir_fd=descriptor)
        else:
            require(stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode),
                    "reject special files in a failed private build root")
            os.unlink(name, dir_fd=descriptor)


def cleanup_private_root(workdir: str, expected: dict[str, Any]) -> dict[str, Any]:
    root = checked_root(workdir)
    descriptor = os.open(
        root, os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW,
    )
    try:
        actual = directory_owner(descriptor, root)
        require(
            (actual["device"], actual["inode"], actual["uid"])
            == (expected["device"], expected["inode"], expected["uid"]),
            "never clean a replaced, broad, cross-family, or reused private root",
        )
        cleanup_directory_contents(descriptor)
    finally:
        os.close(descriptor)
    os.rmdir(root)
    return {
        "status": "PASS",
        "restricted_exact_root": root,
        "expected_device": expected["device"],
        "expected_inode": expected["inode"],
        "root_removed": True,
        "broader_directory_removed": False,
    }


def root_receipt_document(
    context: dict[str, Any], options: argparse.Namespace,
    report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-private-root-receipt",
        "version": VERSION,
        "status": report["status"],
        "family": "zig",
        "label": checked_label(options.label),
        "source_sha256": checked_sha(options.source_sha256, "V13 source"),
        "protocol_sha256": checked_sha(options.protocol_sha256, "V13 protocol"),
        "contract_sha256": checked_sha(options.contract_sha256, "V13 contract"),
        "frozen_graph_version": GRAPH_VERSION,
        "frozen_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND,
        "frozen_history_reference_lower_bound": HISTORY_LOWER_BOUND,
        "private_root": report.get("private_root"),
        "private_root_retained": report["status"] == "PASS",
        "private_root_cleanup": report.get("failure_cleanup"),
        "phase_names": list(PHASE_NAMES),
        "phases": report.get("build_phases", []),
        "source_snapshots_per_completed_phase": 3,
        "actual_process_count": len(report["processes"]),
        "candidate_workers_started": 0,
        "native_activations": 0,
        "compressed_archives_created": 0,
        "candidate_correctness": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }


def publish_plaintext_pair(
    context: dict[str, Any], options: argparse.Namespace,
    report: dict[str, Any],
) -> dict[str, Any]:
    root_name, build_name = evidence_names(options.label)
    root_document = root_receipt_document(context, options, report)
    directory = evidence_directory()
    try:
        root_owner = exclusive_plaintext(directory, root_name, root_document)
        build_document = {
            "schema": SCHEMA + "-plaintext-build-receipt",
            "version": VERSION,
            "status": report["status"],
            "family": "zig",
            "label": checked_label(options.label),
            "source_sha256": checked_sha(options.source_sha256, "V13 source"),
            "protocol_sha256": checked_sha(options.protocol_sha256, "V13 protocol"),
            "contract_sha256": checked_sha(options.contract_sha256, "V13 contract"),
            "private_root_receipt": root_owner,
            "private_root_receipt_sha256": root_owner["sha256"],
            "frozen_graph_version": GRAPH_VERSION,
            "frozen_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND,
            "frozen_history_reference_lower_bound": HISTORY_LOWER_BOUND,
            "failure_preserved": report["status"] != "PASS",
            "complete_actual_build": report,
            "new_exclusive_plaintext_evidence_owner_count": 2,
            "compressed_evidence_owner_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }
        build_owner = exclusive_plaintext(directory, build_name, build_document)
    finally:
        os.close(directory)
    return {
        "schema": SCHEMA + "-actual-build-publication",
        "version": VERSION,
        "status": report["status"],
        "family": "zig",
        "label": checked_label(options.label),
        "private_root_receipt": root_owner,
        "build_receipt": build_owner,
        "actual_compiler_process_count": len(report["processes"]),
        "actual_phase_count": len(report.get("build_phases", [])),
        "native_reproducibility": report.get("reproducibility", "NOT MEASURED"),
        "new_exclusive_plaintext_evidence_owner_count": 2,
        "matching_status": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def run_build(options: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    selected = checked_label(options.label)
    context = authenticate_context(options)
    require_machine_contract(options, context)
    require_fresh_evidence(selected)
    report: dict[str, Any] = {
        "schema": SCHEMA + "-complete-actual-build",
        "version": VERSION,
        "status": "FAIL",
        "family": "zig",
        "label": selected,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "contract_sha256": options.contract_sha256,
        "frozen_graph_version": GRAPH_VERSION,
        "frozen_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND,
        "frozen_history_reference_lower_bound": HISTORY_LOWER_BOUND,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "original_named_private_waiver_count": 13,
        "supplemental_reference_case_count": 8244,
        "corrected_adapter_sha256": OWNERS[
            "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"
        ][0],
        "first_party_engine_source_sha256": OWNERS["candidates/zig/mini_regex.zig"][0],
        "first_party_bridge_source_sha256": OWNERS["candidates/zig/py_bridge.c"][0],
        "expected_process_count_only_after_success": 26,
        "actual_process_count": 0,
        "actual_source_snapshot_count": 0,
        "processes": [],
        "build_phases": [],
        "reproducibility": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "native_libraries_loaded": 0,
        "native_activations": 0,
        "external_regex_dependency_count": 0,
        "stdlib_regex_engine_count": 0,
        "cross_family_engine_count": 0,
        "network_requests": 0,
        "matching_archives_opened": 0,
        "holdout_files_opened": 0,
        "benchmark_files_opened": 0,
        "clock_samples": 0,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
        "owned_original_sources_before": {
            path: context["owners"][path]
            for path in (
                "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py",
                "candidates/zig/mini_regex.zig", "candidates/zig/py_bridge.c",
                "candidates/zig_candidate.py",
            )
        },
        "owned_original_sources_after": "NOT MEASURED",
        "failure_cleanup": "NOT NEEDED",
    }
    root: str | None = None
    root_owner: dict[str, Any] | None = None
    try:
        root = tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX, dir="/tmp")
        checked_root(root)
        descriptor = os.open(
            root, os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
        try:
            root_owner = directory_owner(descriptor, root)
        finally:
            os.close(descriptor)
        report["private_root"] = root_owner
        phases = prepare_phases(root)
        report["build_phases"] = phases
        sources = (
            (
                "candidates/zig/mini_regex.zig",
                "candidates/zig/mini_regex.zig",
            ),
            (
                "candidates/zig/py_bridge.c",
                "candidates/zig/py_bridge.c",
            ),
            (
                "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py",
                "candidates/zig_candidate.py",
            ),
        )
        for phase_document in phases:
            phase = phase_document["name"]
            phase_document["source_snapshots"] = {}
            for origin, destination in sources:
                owner = write_private_source(
                    root, phase, destination,
                    context["protected"][origin], OWNERS[origin][0],
                )
                phase_document["source_snapshots"][destination] = owner
                report["actual_source_snapshot_count"] += 1
        require(report["actual_source_snapshot_count"] == 6,
                "snapshot three complete independently owned sources per phase")
        for _, destination in sources:
            identities = [phase["source_snapshots"][destination] for phase in phases]
            require(
                len({(item["device"], item["inode"]) for item in identities}) == 2,
                "never share source snapshots between independent build phases",
            )
        actual_raw: dict[tuple[str, str], bytes] = {}
        for phase_document in phases:
            phase = phase_document["name"]
            outputs: dict[str, Any] = {}
            for role in PROCESS_ROLES:
                try:
                    record = run_process(role, root, phase, report["processes"])
                finally:
                    report["actual_process_count"] = len(report["processes"])
                if role == "build_zig_bridge":
                    for native_role in ("engine", "bridge"):
                        owner, raw = capture_native(root, phase, native_role)
                        outputs[native_role] = {"owner": owner}
                        actual_raw[(phase, native_role)] = raw
                    phase_document["native_outputs"] = outputs
                elif role.endswith(("_dynamic", "_symbols", "_sections", "_notes")):
                    native_role, _, inspection = role.partition("_")
                    require(native_role in outputs,
                            "inspect only an already compiled same-phase ELF owner")
                    outputs[native_role][inspection + "_output"] = record["stdout"]
            for native_role in ("engine", "bridge"):
                role_output = outputs[native_role]
                role_output["independence_audit"] = audit_native(
                    native_role,
                    decode_stream(role_output["dynamic_output"]),
                    decode_stream(role_output["symbols_output"]),
                    decode_stream(role_output["sections_output"]),
                )
                repeated_owner, repeated = capture_native(root, phase, native_role)
                original_owner = role_output["owner"]
                require(
                    repeated == actual_raw[(phase, native_role)]
                    and (repeated_owner["device"], repeated_owner["inode"],
                         repeated_owner["sha256"])
                    == (original_owner["device"], original_owner["inode"],
                        original_owner["sha256"]),
                    "retain the exact same owned ELF inode through every inspection",
                )
        validate_schedule(report["processes"], root, complete=True)
        comparisons: dict[str, Any] = {}
        for role in ("engine", "bridge"):
            first = phases[0]["native_outputs"][role]["owner"]
            second = phases[1]["native_outputs"][role]["owner"]
            require(
                (first["device"], first["inode"])
                != (second["device"], second["inode"]),
                "require two genuinely different actual native artifact owners",
            )
            identical = actual_raw[(PHASE_NAMES[0], role)] == actual_raw[
                (PHASE_NAMES[1], role)
            ]
            require(identical and first["sha256"] == second["sha256"]
                    and first["bytes"] == second["bytes"],
                    "preserve an actual two-phase deterministic native-build failure")
            comparisons[role] = {
                "sha256": first["sha256"],
                "bytes": first["bytes"],
                "distinct_phase_owner_count": 2,
                "byte_identical": True,
            }
        report["reproducibility"] = {
            "status": "PASS",
            "independent_phase_count": 2,
            "compiler_process_count": 26,
            "unique_compiler_process_count": len(
                {item["pid"] for item in report["processes"]}
            ),
            "source_snapshot_count": 6,
            "native_roles": comparisons,
            "all_native_artifacts_byte_identical": True,
        }
        renewed = authenticate_context(options)
        require_machine_contract(options, renewed)
        report["owned_original_sources_after"] = {
            path: renewed["owners"][path]
            for path in report["owned_original_sources_before"]
        }
        require(
            report["owned_original_sources_after"]
            == report["owned_original_sources_before"],
            "fail closed if any immutable original first-party source changed",
        )
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["actual_process_count"] = len(report["processes"])
        report["error"] = {"type": type(error).__name__, "message": str(error)}
        if root is not None and root_owner is not None:
            try:
                report["failure_cleanup"] = cleanup_private_root(root, root_owner)
            except Exception as cleanup_error:
                report["failure_cleanup"] = {
                    "status": "FAIL",
                    "restricted_exact_root": root,
                    "broader_directory_removed": False,
                    "error_type": type(cleanup_error).__name__,
                    "error_message": str(cleanup_error),
                    "recovery": "STOP; REQUIRE EXPLICIT INDEPENDENT ROOT RECOVERY",
                }
    publication = publish_plaintext_pair(context, options, report)
    return (0 if report["status"] == "PASS" else 1), publication


class SourceOnlyBoundary:
    """Physically forbid every real build, candidate, archive, and timing effect."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {
            kind: 0 for kind in (
                "filesystem", "write", "private_root", "process", "import",
                "native", "archive", "network", "thread", "clock", "lock", "signal",
            )
        }

    def reject(self, name: str, kind: str) -> Any:
        def denied(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise FreezeError("physically blocked source-only effect: " + name)
        return denied

    def install(self, owner: Any, name: str, kind: str) -> None:
        if not hasattr(owner, name):
            return
        key = (id(owner), name)
        if any((id(saved), previous) == key for saved, previous, _ in self.saved):
            return
        previous = getattr(owner, name)
        self.saved.append((owner, name, previous))
        setattr(owner, name, self.reject(name, kind))

    def __enter__(self) -> SourceOnlyBoundary:
        groups: tuple[tuple[Any, tuple[str, ...], str], ...] = (
            (builtins, ("open", "__import__"), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "listdir", "scandir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "iterdir"),
             "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename",
                  "replace", "fsync", "symlink", "link", "rmdir"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename",
                    "replace", "touch", "rmdir"), "write"),
            (tempfile, ("mkdtemp", "mkstemp", "TemporaryFile", "NamedTemporaryFile",
                        "TemporaryDirectory"), "private_root"),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output",
                          "_fork_exec"), "process"),
            (os, ("system", "popen", "fork", "posix_spawn", "execv", "execve"),
             "process"),
            (importlib, ("import_module",), "import"),
            (ctypes, ("CDLL", "PyDLL", "WinDLL", "OleDLL"), "native"),
            (gzip, ("open", "decompress"), "archive"),
            (zlib, ("decompress", "decompressobj"), "archive"),
            (socket, ("socket", "create_connection", "getaddrinfo"), "network"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                    "perf_counter_ns", "process_time", "process_time_ns",
                    "thread_time", "thread_time_ns", "sleep"), "clock"),
            (fcntl, ("flock", "lockf", "fcntl"), "lock"),
            (signal, ("signal", "pthread_kill", "raise_signal"), "signal"),
        )
        for owner, names, kind in groups:
            for name in names:
                self.install(owner, name, kind)
        for module_name, names, kind in (
            ("_ctypes", ("dlopen",), "native"),
            ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin",
                       "exec_builtin"), "native"),
            ("_socket", ("socket", "getaddrinfo"), "network"),
            ("_thread", ("start_new_thread", "start_joinable_thread"), "thread"),
        ):
            module = sys.modules.get(module_name)
            if module is not None:
                for name in names:
                    self.install(module, name, kind)
        return self

    def __exit__(self, *_error: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def syntax_nodes(node: ast.AST) -> Any:
    require(isinstance(node, ast.AST), "inspect only complete frozen Python syntax")
    pending = [node]
    while pending:
        current = pending.pop()
        yield current
        pending.extend(ast.iter_child_nodes(current))


def reject_hostile_controls(context: dict[str, Any]) -> int:
    count = 0

    def reject(action: Any, label: str) -> None:
        nonlocal count
        try:
            action()
        except (FreezeError, ValueError, TypeError, KeyError, IndexError,
                struct.error, UnicodeError):
            count += 1
            return
        raise FreezeError("a hostile build-freeze control unexpectedly passed: " + label)

    for value in (None, "", "0", "A" * 64, "x" * 64, "0" * 63, "0" * 65):
        reject(lambda item=value: checked_sha(item, "forged caller pin"), "caller pin")
    for value in (
        None, "", "X", "../zig", "/tmp", "a/b", "a--b", "a-", ".git",
        "holdout", "A", "a_b", "x" * 65,
    ):
        reject(lambda item=value: checked_label(item), "escaped/reused build label")
    for value in (
        None, "", "/", "/tmp", "/tmp/other", "/tmp/../tmp/other",
        "/tmp/" + PRIVATE_ROOT_PREFIX,
        "/tmp/" + PRIVATE_ROOT_PREFIX + "short",
        "/tmp/" + PRIVATE_ROOT_PREFIX + "bad.value",
        "/tmp/" + PRIVATE_ROOT_PREFIX + "bad/slash",
        "/tmp/rebar-phase2-zig-scanner-capture-source-build-v1-synthetic123",
    ):
        reject(lambda item=value: checked_root(item), "unsafe build root")
    for value in (
        "", "/tmp/secret", "../secret", "./secret", "a//b", "a/../b",
        "holdout/secret.json", "performance/secret.json", ".git/config",
        "oracle/phase2/evidence/secret.json.gz", "native/probe.so",
    ):
        reject(lambda item=value: safe_relative(item), "unsafe frozen source path")
    graph = context["graph"]
    for key, value in (
        ("version", 83),
        ("authenticated_evidence_owner_lower_bound", EVIDENCE_LOWER_BOUND - 1),
        ("authenticated_history_reference_lower_bound", HISTORY_LOWER_BOUND - 1),
        ("phase1_v4_oracle_readiness_status", "FAIL"),
        ("phase1_v4_candidate_testing_authorized", False),
        ("first_party_source_inventory_family_count", 5),
        ("qualified_candidate_count", 1),
        ("zig_original_campaign_status", "PASS"),
        ("zig_original_campaign_semantic_mismatch_count", 0),
        ("zig_original_campaign_verified_passing_case_count", 31237),
        ("zig_original_campaign_candidate_worker_count", 0),
        ("zig_v1_official_compiler_path", "/usr/bin/zig"),
        ("zig_v1_official_compiler_version", "0.15.0"),
        ("zig_v1_official_compiler_sha256", "0" * 64),
        ("zig_v1_official_compiler_bytes", 172641671),
        ("zig_v12_source_build_status", "FAIL"),
        ("zig_v12_source_build_phase_count", 1),
        ("zig_v12_source_build_process_count", 25),
        ("zig_v12_source_build_stdlib_regex_engine_count", 1),
        ("zig_v12_source_build_external_regex_dependency_count", 1),
        ("zig_v12_source_build_cross_family_engine_count", 1),
        ("zig_scanner_phrase_v4_complete_original_scanner_case_count", 1023),
        ("zig_scanner_phrase_v4_corrected_original_scanner_case_count", 63),
        ("zig_scanner_phrase_v4_preserved_original_scanner_case_count", 959),
        ("zig_scanner_phrase_v4_candidate_build", "PASS"),
        ("zig_scanner_phrase_v4_candidate_matching", "PASS"),
        ("zig_scanner_phrase_v4_candidate_workers_started", 1),
        ("zig_scanner_phrase_v4_actual_compiler_process_count", 1),
        ("zig_scanner_phrase_v4_candidate_qualified", True),
        ("rust_native_build_v19_status", "FAIL"),
        ("rust_native_build_v19_compiler_process_count", 27),
        ("rust_v11_original_campaign_execution_status", "PASS"),
        ("rust_original_campaign_status", "PASS"),
        ("rust_original_campaign_semantic_mismatch_count", 0),
        ("rust_original_campaign_verified_passing_case_count", 31237),
        ("rust_v15_original_campaign_actual_worker_count", 12),
        ("rust_v15_original_campaign_started_suite_count", 12),
        ("rust_v15_original_campaign_attempted_suite_count", 12),
        ("rust_v15_original_campaign_distinct_worker_count", 12),
        ("rust_v15_original_campaign_candidate_matching", "PASS"),
        ("rust_v15_original_campaign_candidate_qualified", True),
        ("rust_v15_original_campaign_completed_suite_count", 13),
        ("rust_v15_original_campaign_infrastructure_failure_count", 0),
        ("rust_v15_original_campaign_semantic_mismatch_count", 0),
        ("rust_v15_original_campaign_verified_passing_case_count", 31237),
        ("rust_v15_original_campaign_worker_failure_capture_attempts", 0),
        ("rust_v15_original_campaign_worker_failure_capture_complete", False),
        ("rust_v15_original_campaign_complete_observation_vectors", True),
        ("rust_v15_original_campaign_all_original_targets_restored", False),
        ("rust_v15_original_campaign_outcome_receipt_sha256", "0" * 64),
        ("rust_v15_original_campaign_publication_status", "FAIL"),
        ("rust_v15_original_campaign_publication_pass_means", "CANDIDATE PASS"),
        ("rust_v15_original_campaign_outcome_archive_opened_by_graph", True),
        ("rust_v15_original_campaign_outcome_archive_inflated_by_graph", True),
        ("c_native_build_v16_status", "FAIL"),
        ("c_native_build_v16_compiler_process_count", 13),
        ("c_original_campaign_status", "PASS"),
        ("c_original_campaign_semantic_mismatch_count", 0),
        ("c_original_campaign_verified_passing_case_count", 31237),
        ("final_holdout_opened", True),
        ("performance", "1.5x"),
        ("runtime_no_delegation", "ESTABLISHED"),
        ("winner_selected", True),
    ):
        reject(lambda name=key, forged=value: validate_graph(
            dict(graph, **{name: forged})
        ), "forged V84 graph field " + key)
    feature = context["feature"]
    for key, value in (
        ("version", 3),
        ("status", "PASS"),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "2x"),
        ("winner_selected", True),
    ):
        reject(lambda name=key, forged=value: validate_feature(
            dict(feature, **{name: forged})
        ), "forged V4 feature " + key)
    for key, value in (
        ("version", "0.15.0"),
        ("release_channel", "nightly"),
        ("compiler_sha256", "0" * 64),
        ("archive_sha256", "0" * 64),
        ("archive_bytes", 1),
    ):
        lock = strict_json(
            context["protected"]["toolchains/zig-0.16.0.lock.json"],
            "offline lock",
            canonical_required=False,
        )
        reject(lambda name=key, forged=value, owned=lock: validate_lock(
            dict(owned, **{name: forged})
        ), "forged pinned offline Zig lock " + key)
    root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic00000001"
    for phase in ("", "reference-c", "../reference-a", "/reference-a", None):
        reject(lambda item=phase: phase_paths(root, item), "forged phase name")
    for phase in PHASE_NAMES:
        commands = planned_commands(root, phase)
        for role in PROCESS_ROLES:
            forged = list(commands[role])
            forged[0] = "/bin/sh"
            reject(lambda name=role, value=forged, item=phase: checked_command(
                name, value, root, item,
            ), "substituted compiler/shell " + role)
        for role in PROCESS_ROLES:
            other = "reference-b" if phase == "reference-a" else "reference-a"
            if planned_commands(root, phase)[role] != planned_commands(root, other)[role]:
                reject(lambda name=role, item=phase, wrong=other: checked_command(
                    name, planned_commands(root, wrong)[name], root, item,
                ), "cross-phase compiler " + role)
    for role, raw in (
        ("engine", b""),
        ("engine", b"x" * 64),
        ("bridge", b"\x7fELF" + b"\x00" * 60),
    ):
        reject(lambda item=role, data=raw: validate_elf_header(data, item),
               "invented or malformed native ELF")
    for data in (
        {"bytes": 0, "sha256": "0" * 64, "base64": ""},
        {"bytes": 1, "sha256": "0" * 64, "base64": "eA=="},
        {"bytes": 1, "sha256": digest(b"x"), "base64": "!"},
    ):
        reject(lambda item=data: decode_stream(item), "invented process bytes")
    bad_dynamic = b"0x0000000000000001 (NEEDED) Shared library: missing\n"
    reject(lambda: dynamic_fields(bad_dynamic), "malformed delegated ELF dependency")
    delegated_symbols = (
        b"Symbol table '.dynsym' contains 2 entries:\n"
        b" 1: 0000000000000000 0 FUNC GLOBAL DEFAULT UND pcre2_match\n"
    )
    reject(lambda: dynamic_symbols(delegated_symbols), "external regex symbol")
    source_tree = ast.parse(context["source"], filename=SOURCE_PATH, mode="exec")
    functions = {
        item.name: item for item in source_tree.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    require(
        "run_build" in functions and "run_process" in functions
        and "publish_plaintext_pair" in functions
        and any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "mkdtemp"
            for node in syntax_nodes(functions["run_build"])
        )
        and any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "Popen"
            for node in syntax_nodes(functions["run_process"])
        )
        and any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "publish_plaintext_pair"
            for node in syntax_nodes(functions["run_build"])
        ),
        "prove the future native build has actual root, subprocess, and receipt dispatch",
    )
    return count


def source_only_result(
    context: dict[str, Any], *, hostile: bool,
) -> dict[str, Any]:
    existing = frozenset(
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
        or name in ("_sre", "regex")
    )
    rejected = 0
    with SourceOnlyBoundary() as boundary:
        templates = command_templates()
        require(len(templates) == 2 and all(len(item["processes"]) == 13
                                           for item in templates),
                "retain the complete two-phase 26-role direct source-build plan")
        if hostile:
            rejected = reject_hostile_controls(context)
            probes: tuple[tuple[str, Any, str], ...] = (
                ("filesystem", lambda: builtins.open("/tmp/forbidden", "rb"),
                 "repository or holdout open"),
                ("filesystem", lambda: io.open("/tmp/forbidden", "rb"),
                 "alternate filesystem open"),
                ("filesystem", lambda: os.open("/tmp", os.O_RDONLY),
                 "private root directory inspection"),
                ("write", lambda: os.mkdir("/tmp/forbidden"),
                 "private phase creation"),
                ("write", lambda: Path("/tmp/forbidden").write_bytes(b"x"),
                 "native or receipt publication"),
                ("private_root", lambda: tempfile.mkdtemp(
                    prefix=PRIVATE_ROOT_PREFIX, dir="/tmp",
                 ), "fresh private build root"),
                ("process", lambda: subprocess.Popen([PINNED_ZIG, "version"]),
                 "offline Zig compiler execution"),
                ("process", lambda: subprocess.run([PINNED_GCC, "--version"]),
                 "CPython C-bridge compiler execution"),
                ("import", lambda: importlib.import_module("candidates.zig_candidate"),
                 "candidate activation"),
                ("native", lambda: ctypes.CDLL(ENGINE_NAME),
                 "native engine loading"),
                ("archive", lambda: gzip.open("forbidden.json.gz"),
                 "matching archive access"),
                ("archive", lambda: zlib.decompress(b"x"),
                 "matching archive inflation"),
                ("network", lambda: socket.socket(), "network access"),
                ("thread", lambda: threading.Thread().start(), "thread start"),
                ("clock", lambda: time.perf_counter(), "benchmark clock"),
                ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX), "external file lock"),
                ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
                 "signal mutation"),
            )
            for kind, action, label in probes:
                before = boundary.blocked[kind]
                try:
                    action()
                except FreezeError:
                    require(boundary.blocked[kind] == before + 1,
                            "prove the source wall physically blocks " + label)
                else:
                    raise FreezeError("source-only wall allowed " + label)
            require(all(number > 0 for number in boundary.blocked.values()),
                    "exercise every source-only external-effect boundary")
        blocked = dict(boundary.blocked)
    require(
        frozenset(
            name for name in sys.modules
            if name == "candidates" or name.startswith("candidates.")
            or name in ("_sre", "regex")
        ) == existing,
        "source-only verification imported a candidate or matching implementation",
    )
    return {
        "schema": SCHEMA + "-source-only-result",
        "version": VERSION,
        "status": "PASS",
        "mode": "SELF-TEST" if hostile else "FROZEN CONTEXT",
        "current_graph_version": GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND,
        "authenticated_history_reference_lower_bound": HISTORY_LOWER_BOUND,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "original_named_private_waiver_count": 13,
        "mapped_original_obligation_count": 73,
        "supplemental_reference_case_count": 8244,
        "supplemental_cases_added_to_original_denominator": False,
        "first_party_candidate_family_count": 6,
        "first_party_zig_engine_source_sha256": OWNERS[
            "candidates/zig/mini_regex.zig"
        ][0],
        "first_party_cpython_bridge_source_sha256": OWNERS[
            "candidates/zig/py_bridge.c"
        ][0],
        "complete_corrected_adapter_sha256": OWNERS[
            "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"
        ][0],
        "complete_corrected_adapter_bytes": 68530,
        "complete_original_scanner_case_count": 1024,
        "corrected_original_scanner_source_witness_count": 64,
        "preserved_original_scanner_case_count": 960,
        "offline_zig_version": "0.16.0",
        "offline_zig_executable": PINNED_ZIG,
        "offline_zig_compiler_sha256": TOOLCHAINS["zig"][1],
        "pinned_toolchain_owner_count": len(TOOLCHAINS),
        "actual_historical_zig_matching": "FAIL",
        "actual_historical_zig_mismatch_count": 1764,
        "actual_historical_zig_verified_passing_case_count": 3711,
        "future_independent_build_phase_count": 2,
        "future_process_count_per_phase": 13,
        "future_total_compiler_process_count": 26,
        "future_source_snapshot_count_per_phase": 3,
        "future_private_root_receipt_count": 1,
        "future_plaintext_build_receipt_count": 1,
        "actual_build_status": "NOT RUN",
        "actual_native_reproducibility": "NOT MEASURED",
        "actual_matching_status": "NOT RUN",
        "actual_candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "hostile_controls_rejected": rejected,
        "external_effect_controls_blocked": sum(blocked.values()),
        "blocked_effects_by_kind": blocked,
        **source_boundaries(),
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def require_machine_contract(
    options: argparse.Namespace, context: dict[str, Any],
) -> dict[str, Any]:
    require(options.contract_sha256 is not None,
            "independently caller-pin the complete published V13 machine contract")
    size = os.stat(ROOT / CONTRACT_PATH, follow_symlinks=False).st_size
    owner, raw = read_repository_owner(
        CONTRACT_PATH, checked_sha(options.contract_sha256, "V13 contract"), size,
    )
    expected = contract_document(context)
    require(strict_json(raw, "V13 Zig scanner phrase native build contract") == expected,
            "bind the complete V13 build plan to every actual independently frozen owner")
    return owner


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FreezeError("reject unauthorized Zig V13 build action: " + message)


def parse_arguments() -> argparse.Namespace:
    values = sys.argv[1:]
    flags = [value for value in values if value.startswith("--")]
    require(len(flags) == len(set(flags)),
            "reject repeated build modes and duplicated independent caller pins")
    parser = SafeArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--graph-source-sha256", required=True)
    parser.add_argument("--graph-inputs-sha256", required=True)
    parser.add_argument("--graph-summary-sha256", required=True)
    parser.add_argument("--graph-svg-sha256", required=True)
    parser.add_argument("--label")
    options = parser.parse_args(values)
    checked_sha(options.source_sha256, "V13 source")
    checked_sha(options.protocol_sha256, "V13 protocol")
    if options.contract_sha256 is not None:
        checked_sha(options.contract_sha256, "V13 contract")
    if options.render_contract:
        require(options.contract_sha256 is None and options.label is None,
                "render one canonical contract without any build or publication")
    elif options.build:
        require(options.contract_sha256 is not None and options.label is not None,
                "require independent contract authorization and a fresh build label")
        checked_label(options.label)
    else:
        require(options.contract_sha256 is not None and options.label is None,
                "forbid build labels and require all source-only caller pins")
    return options


def main() -> int:
    try:
        options = parse_arguments()
        if options.build:
            code, result = run_build(options)
        else:
            context = authenticate_context(options)
            if options.render_contract:
                result = contract_document(context)
            else:
                require_machine_contract(options, context)
                result = source_only_result(context, hostile=options.self_test)
            code = 0
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return code
    except (
        FreezeError, OSError, ValueError, TypeError, KeyError, IndexError,
        UnicodeError, OverflowError, RecursionError, struct.error,
        subprocess.SubprocessError, json.JSONDecodeError,
    ) as error:
        sys.stderr.write("zig-scanner-phrase-source-build-v13: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
