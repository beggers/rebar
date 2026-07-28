#!/usr/bin/env python3
"""Freeze the corrected genuine, intent-authenticated subinterpreter gate.

The published version-one original observer is reused without changing its
source, original matcher guards, case semantics, or 31,237-case denominator.
An actual worker is forbidden until the separately published activator has
authenticated every durable canonical native promotion intention.
"""

from __future__ import annotations

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


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_candidate_subinterpreters_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/candidate-subinterpreters-v2.json"
EXPLANATION_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V2.md"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-owned-candidate-subinterpreters-v2"
PROTOCOL_SCHEMA = "rebar-owned-candidate-subinterpreters-protocol-v2"
RECEIPT_SCHEMA = SCHEMA + "-publication-receipt"
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
BUILD_SOURCE_RELATIVE = "tools/reproduce_phase2_native_builds_v2.py"
BUILD_SOURCE_SHA256 = "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796"
BUILD_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md"
BUILD_PROTOCOL_SHA256 = "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603"
BUILD_SCHEMA = "rebar-phase2-independent-native-source-build-v2"
ACTIVATION_SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v1.py"
ACTIVATION_SOURCE_SHA256 = "ebc2427f6981e12c136b7f9371e5c72bccd89e1362930ad63245751d76fef164"
ACTIVATION_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V1.md"
ACTIVATION_PROTOCOL_SHA256 = "8f69bc751ac07e6d0a55fe9563c0038838976873991e45c5a0967f0d21a989d2"
ACTIVATION_SCHEMA = "rebar-phase2-verified-native-candidate-activation-v1"
ACTIVATION_RECEIPT_SCHEMA = ACTIVATION_SCHEMA + "-durable-publication-receipt"
ACTIVATION_JOURNAL_SCHEMA = ACTIVATION_SCHEMA + "-recovery-journal"
ACTIVATION_INTENT_SCHEMA = ACTIVATION_SCHEMA + "-durable-promotion-intent"
ACTIVATION_PREFIX = "/tmp/rebar-phase2-verified-native-activation-v1-"
REFERENCE_SOURCE_SHA256 = "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8"
ORIGINAL_PROGRAM_SHA256 = "9d136a708a438c1f8060c047d89d415c4854ffaeeee9af2fb2d8619f2f0ed07d"
ADAPTED_PROGRAM_SHA256 = "147b09bcda37678b9ac4f2f050a22eb5435c7703cbce33247e9287e62e514f71"
MATRIX_SHA256 = "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3"
REFERENCE_SHA256 = "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8"
PROJECTED_SHA256 = "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"
C_BUILD_ARCHIVE_SHA256 = "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878"
C_BUILD_RECEIPT_SHA256 = "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24"
C_NATIVE_SHA256 = "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48
CASE_COUNT = 128
CASE_EXECUTIONS = 394
INTERPRETER_COUNT = 11
PROCESS_TIMEOUT_SECONDS = 180
PROCESS_CLEANUP_SECONDS = 15
RENAMES = {
    "actual_stdlib_reimport": "actual_engine_reimport",
    "match_is_stdlib_match": "match_is_engine_match",
    "module_identity": "engine_sysmodules_identity_verified",
    "pattern_is_stdlib_pattern": "pattern_is_engine_pattern",
    "reimported_origin_verified": "engine_reimported_origin_verified",
    "stdlib_owner": "engine_sysmodules_owner_verified",
    "stdlib_re_module": "engine_module_name_verified",
}


class SubinterpreterGateError(Exception):
    """A corrected complete real-interpreter prerequisite is not genuine."""


class SourceOnlyViolation(SubinterpreterGateError):
    """A synthetic test attempted a genuine external effect."""


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    audit_name: str
    module: str
    source_relative: str
    engine_relative: str
    bridge_relative: str
    owners: tuple[str, ...]


FAMILIES: dict[str, FamilySpec] = {
    "rust": FamilySpec(
        "rust", "rust", "candidates.rust_candidate",
        "candidates/rust_candidate.py", "candidates/_rust_engine.so",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        ("candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
         "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
         "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
         "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
         "candidates/rust/src/unicode_tables.rs"),
    ),
    "c": FamilySpec(
        "c", "c_vm", "candidates.vm_candidate", "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    ),
    "zig": FamilySpec(
        "zig", "zig", "candidates.zig_candidate", "candidates/zig_candidate.py",
        "candidates/_zig_probe.so", "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        ("candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
         "candidates/zig/py_bridge.c"),
    ),
}


def require(value: Any, message: str) -> None:
    if value is not True:
        raise SubinterpreterGateError(message)


def sha256(raw: Any) -> str:
    require(type(raw) is bytes, "hash only complete genuine bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(ch in "0123456789abcdef" for ch in value),
            "require the exact lowercase SHA-256 for " + label)
    return value


def checked_family(name: Any) -> FamilySpec:
    require(type(name) is str and name in FAMILIES,
            "choose one genuine independently owned Rust, C or Zig engine")
    spec = FAMILIES[name]
    require(spec.name == name and spec.source_relative in spec.owners
            and len(spec.owners) == {"rust": 9, "c": 2, "zig": 3}[name]
            and (spec.engine_relative == spec.bridge_relative) is (name == "c"),
            "the selected frozen native owner family was substituted")
    return spec


def checked_label(value: Any) -> str:
    require(type(value) is str and value.isascii()
            and 0 < len(value) <= MAX_LABEL_BYTES
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for ch in value)
            and not value.startswith("-") and not value.endswith("-")
            and "--" not in value,
            "require an exact, bounded, nontraversing publication label")
    return value


def _walk_json(value: Any, depth: int = 0,
               count: list[int] | None = None) -> None:
    require(depth <= 48, "a frozen JSON document exceeds its nesting bound")
    if count is None:
        count = [0]
    count[0] += 1
    require(count[0] <= 1_000_000,
            "a frozen JSON document exceeds its element bound")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        require(abs(value) <= 1 << 256, "reject an unbounded JSON integer")
        return
    if type(value) is str:
        require(not any(0xD800 <= ord(ch) <= 0xDFFF for ch in value),
                "reject an unpaired or encoded surrogate")
        return
    if type(value) is float:
        require(value == value and abs(value) != float("inf"),
                "reject an infinite or nonfinite JSON number")
        return
    if type(value) is list:
        for item in value:
            _walk_json(item, depth + 1, count)
        return
    if type(value) is dict:
        for key, item in value.items():
            require(type(key) is str, "JSON object keys must be exact strings")
            _walk_json(key, depth + 1, count)
            _walk_json(item, depth + 1, count)
        return
    raise SubinterpreterGateError("reject an unsupported canonical JSON value")


def canonical(value: Any) -> bytes:
    _walk_json(value)
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise SubinterpreterGateError("reject a noncanonical JSON value") from error


def canonical_line(value: Any) -> bytes:
    return canonical(value) + b"\n"


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in pairs:
        require(type(key) is str and key not in result,
                "reject duplicated or non-string JSON object keys")
        result[key] = item
    return result


def reject_constant(value: str) -> Any:
    raise SubinterpreterGateError("reject nonfinite JSON: " + value)


def decode_document(raw: Any, label: str, *, canonical_required: bool,
                    newline: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "require the full bounded " + label)
    try:
        result = json.loads(raw.decode("utf-8", "strict"),
                            object_pairs_hook=unique_pairs,
                            parse_constant=reject_constant)
    except (ValueError, UnicodeError, RecursionError, OverflowError) as error:
        raise SubinterpreterGateError("reject malformed " + label) from error
    require(type(result) is dict, "require one genuine JSON object: " + label)
    _walk_json(result)
    if canonical_required:
        require(raw == (canonical_line(result) if newline else canonical(result)),
                "reject changed bytes, suffix or newline for " + label)
    return result


def synthetic_protocol() -> dict[str, Any]:
    return {
        "schema": PROTOCOL_SCHEMA, "version": 2, "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; CANDIDATES NOT RUN",
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
        "previous_original_recorder": {
            "source_path": V1_SOURCE_RELATIVE, "source_sha256": V1_SOURCE_SHA256,
            "protocol_path": V1_PROTOCOL_RELATIVE,
            "protocol_sha256": V1_PROTOCOL_SHA256,
            "explanation_path": V1_EXPLANATION_RELATIVE,
            "explanation_sha256": V1_EXPLANATION_SHA256,
            "source_mutated": False, "semantic_program_mutated": False,
            "actual_worker_delegates_to_unchanged_original_recorder": True,
        },
        "phase1": {
            "inventory_path": "oracle/phase1/p0-completeness-v1.json",
            "inventory_sha256": PHASE1_SHA256,
            "suite_count": 13, "case_execution_denominator": 31237,
            "supplemental_subinterpreter_case_count": 128,
            "supplemental_cases_added_to_phase1_denominator": False,
        },
        "source_build_v2": {
            "source_path": BUILD_SOURCE_RELATIVE,
            "source_sha256": BUILD_SOURCE_SHA256,
            "protocol_path": BUILD_PROTOCOL_RELATIVE,
            "protocol_sha256": BUILD_PROTOCOL_SHA256,
            "completed_family_count": 1,
            "c": {
                "status": "PASS", "label": "phase2-v2",
                "archive_path": EVIDENCE_RELATIVE
                + "/native-source-build-v2-c-phase2-v2.json.gz",
                "archive_sha256": C_BUILD_ARCHIVE_SHA256,
                "receipt_path": EVIDENCE_RELATIVE
                + "/native-source-build-v2-c-phase2-v2-publication-receipt.json",
                "receipt_sha256": C_BUILD_RECEIPT_SHA256,
                "fresh_extension_sha256": C_NATIVE_SHA256,
                "fresh_extension_bytes": 163136,
                "independent_fresh_phase_count": 2,
                "candidate_imports": 0, "candidate_processes_started": 0,
                "native_libraries_loaded": 0,
            },
            "rust": "NOT RUN", "zig": "NOT RUN",
        },
        "corrected_canonical_activation": {
            "status": "SOURCE PUBLISHED; ACTUAL ACTIVATIONS NOT RUN",
            "source_path": ACTIVATION_SOURCE_RELATIVE,
            "source_sha256": ACTIVATION_SOURCE_SHA256,
            "protocol_path": ACTIVATION_PROTOCOL_RELATIVE,
            "protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
            "report_schema": ACTIVATION_SCHEMA,
            "receipt_schema": ACTIVATION_RECEIPT_SCHEMA,
            "journal_schema": ACTIVATION_JOURNAL_SCHEMA,
            "promotion_intent_schema": ACTIVATION_INTENT_SCHEMA,
            "authentic_source_validator_required": True,
            "authentic_intent_validator_required": True,
            "per_role_intent_actual_bytes_required": True,
            "private_journal_root_mode": "0700",
            "actual_report_receipt_journal_intent_backup_mode": "0600",
            "same_content_different_inode_accepted": False,
            "intent_bound_to_prepared_journal": True,
            "intent_bound_to_actual_canonical_native_inode": True,
            "verified_transactionally_activated_repo_binary_required": True,
            "frozen_guard_root_mutation_allowed": False,
            "actual_activations_completed": 0,
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
        "lossless_observation_field_renames": dict(RENAMES),
        "lifecycle": {
            "actual_case_execution_count": CASE_COUNT,
            "actual_a_observations": CASE_COUNT,
            "actual_b_observations": CASE_COUNT,
            "actual_repeated_a_observations": CASE_COUNT,
            "actual_fresh_interpreter_case_observations": 8,
            "actual_a_after_b_close_observations": 1,
            "actual_fresh_c_observations": 1,
            "actual_case_interpreter_exec_calls": CASE_EXECUTIONS,
            "actual_initialization_interpreter_exec_calls": INTERPRETER_COUNT,
            "actual_guard_cleanup_interpreter_exec_calls": INTERPRETER_COUNT,
            "actual_interpreters_created": INTERPRETER_COUNT,
            "actual_interpreters_destroyed": INTERPRETER_COUNT,
            "correctness_worker_timeout_seconds": PROCESS_TIMEOUT_SECONDS,
            "correctness_worker_cleanup_timeout_seconds": PROCESS_CLEANUP_SECONDS,
            "all_real_pipes_read_to_eof": True,
            "all_real_pipe_descriptors_closed": True,
            "interpreter_live_set_restored": True, "locale_restored": True,
        },
        "candidate_families": ["rust", "c", "zig"],
        "candidate_family_audit_names": {
            "rust": "rust", "c": "c_vm", "zig": "zig",
        },
        "evidence": {
            "directory": EVIDENCE_RELATIVE,
            "archive_template":
            "owned-candidate-subinterpreters-v2-FAMILY-LABEL.json.gz",
            "receipt_template":
            "owned-candidate-subinterpreters-v2-FAMILY-LABEL-publication-receipt.json",
            "failure_archive_template":
            "owned-candidate-subinterpreters-v2-FAMILY-LABEL-failures.json.gz",
            "failure_receipt_template":
            "owned-candidate-subinterpreters-v2-FAMILY-LABEL-failures-publication-receipt.json",
            "deterministic_gzip_mtime": 0, "exclusive_creation": True,
            "same_inode_readback_verified": True, "file_fsync_required": True,
            "directory_fsync_required": True,
            "complete_failures_preserved": True,
        },
        "boundaries": {
            "actual_candidate_workers_before_publication": 0,
            "actual_candidate_imports_before_publication": 0,
            "actual_activations_before_publication": 0,
            "actual_reference_workers_before_publication": 0,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
        },
    }


def validate_protocol(document: Any) -> dict[str, Any]:
    require(type(document) is dict
            and canonical(document) == canonical(synthetic_protocol()),
            "the complete corrected frozen V2 subinterpreter protocol changed")
    return document


def checked_relative(value: Any) -> str:
    require(type(value) is str and value.isascii() and bool(value)
            and not value.startswith("/") and "\\" not in value
            and "\x00" not in value
            and all(part not in {"", ".", ".."}
                    for part in value.split("/")),
            "reject a broad, traversing, or symlinkable owner path")
    return value


def checked_activation_root(value: Any, spec: FamilySpec) -> str:
    require(type(value) is str and value.isascii()
            and value.startswith(ACTIVATION_PREFIX + spec.name + "-")
            and value.count("/") == 2
            and value == os.path.normpath(value)
            and "\\" not in value and "\x00" not in value,
            "require the exact fresh selected private rollback root")
    return value


def read_owned(
    base: Path, relative: str, expected: str, *, maximum: int,
    exact_size: int | None = None, private: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    require(isinstance(base, Path) and base.is_absolute(),
            "require one exact absolute canonical or private owner root")
    safe = checked_relative(relative)
    checked_digest(expected, safe)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "require a bounded exact source, native artifact or recovery proof")
    directory_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_NOFOLLOW", 0))
    file_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                  | getattr(os, "O_NOFOLLOW", 0))
    descriptors: list[int] = []
    try:
        current = os.open(str(base), directory_flags)
        descriptors.append(current)
        initial = os.fstat(current)
        visible = os.lstat(str(base))
        require(stat.S_ISDIR(initial.st_mode)
                and (initial.st_dev, initial.st_ino)
                == (visible.st_dev, visible.st_ino)
                and (not private or (
                    initial.st_uid == os.geteuid()
                    and stat.S_IMODE(initial.st_mode) == 0o700
                )), "reject an unsafe, redirected or nonprivate owner root")
        pieces = safe.split("/")
        for part in pieces[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            descriptors.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a frozen owner parent was replaced by a symlink")
        descriptor = os.open(pieces[-1], file_flags, dir_fd=current)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(pieces[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size)
                and (not private or stat.S_IMODE(before.st_mode) == 0o600),
                "reject missing, redirected or non-0600 durable proof bytes")
        remaining = before.st_size
        parts: list[bytes] = []
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "an actual frozen artifact or intent was truncated")
            parts.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "an actual durable artifact contains concealed trailing bytes")
        after = os.fstat(descriptor)
        visible = os.stat(pieces[-1], dir_fd=current, follow_symlinks=False)
        require(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns)
            and (visible.st_dev, visible.st_ino, visible.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "an exact durable promotion intent changed during authentication",
        )
        raw = b"".join(parts)
        require(len(raw) == after.st_size and sha256(raw) == expected,
                "the exact pinned source, intent or native bytes differ")
        return raw, {
            "relative": safe, "path": str(base / safe),
            "sha256": expected, "size_bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def source_pins(spec: FamilySpec, values: Any) -> dict[str, str]:
    require(type(values) is list and len(values) == len(spec.owners),
            "pin every exact independently owned semantic source")
    result: dict[str, str] = {}
    for item in values:
        require(type(item) is str and item.count("=") == 1,
                "require one source-relative=sha256 owner")
        relative, pin = item.split("=", 1)
        require(relative in spec.owners and relative not in result,
                "reject omitted, duplicated or cross-family source ownership")
        result[relative] = checked_digest(pin, relative)
    require(set(result) == set(spec.owners),
            "the complete independent semantic owner closure was forged")
    return dict(sorted(result.items()))


def parse_arguments(arguments: Any) -> dict[str, Any]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require exact nonabbreviated subinterpreter V2 options")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(arguments and arguments[0] in
            {"--record-candidate", "--internal-worker"},
            "select source-only tests or an explicitly authorized genuine worker")
    result: dict[str, Any] = {
        "mode": arguments[0][2:], "owned_source_sha256": [],
    }
    mapping = {
        "--family": "family", "--label": "label",
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--explanation-sha256": "explanation_sha256",
        "--v1-source-sha256": "v1_source_sha256",
        "--v1-protocol-sha256": "v1_protocol_sha256",
        "--v1-explanation-sha256": "v1_explanation_sha256",
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
        "--candidate-source-sha256": "candidate_source_sha256",
        "--native-engine-sha256": "native_engine_sha256",
        "--native-bridge-sha256": "native_bridge_sha256",
    }
    position = 1
    while position < len(arguments):
        require(position + 1 < len(arguments),
                "a genuine candidate authorization is missing its exact value")
        key, value = arguments[position], arguments[position + 1]
        if key == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
        else:
            require(key in mapping and mapping[key] not in result,
                    "reject unknown, duplicate, benchmark or holdout options")
            result[mapping[key]] = value
        position += 2
    require(set(result) == {"mode", "owned_source_sha256", *mapping.values()},
            "pin every V2, unchanged V1, source-build and activation owner")
    spec = checked_family(result["family"])
    checked_label(result["label"])
    checked_label(result["build_label"])
    checked_activation_root(result["activation_root"], spec)
    for key in set(mapping.values()) - {"family", "label", "build_label",
                                       "activation_root"}:
        checked_digest(result[key], key)
    for key, expected in (
        ("v1_source_sha256", V1_SOURCE_SHA256),
        ("v1_protocol_sha256", V1_PROTOCOL_SHA256),
        ("v1_explanation_sha256", V1_EXPLANATION_SHA256),
        ("build_source_sha256", BUILD_SOURCE_SHA256),
        ("build_protocol_sha256", BUILD_PROTOCOL_SHA256),
        ("activation_source_sha256", ACTIVATION_SOURCE_SHA256),
        ("activation_protocol_sha256", ACTIVATION_PROTOCOL_SHA256),
    ):
        require(result[key] == expected,
                "a published immutable source or guard prerequisite changed: " + key)
    owners = source_pins(spec, result["owned_source_sha256"])
    require(owners[spec.source_relative] == result["candidate_source_sha256"],
            "the exact candidate source escaped its genuine semantic closure")
    require((result["native_engine_sha256"]
             == result["native_bridge_sha256"]) is (spec.name == "c"),
            "only C uses an identical actual engine and Python bridge")
    return result


def legacy_arguments(arguments: Mapping[str, Any]) -> dict[str, Any]:
    previous = dict(arguments)
    for key in ("v1_source_sha256", "v1_protocol_sha256",
                "v1_explanation_sha256"):
        previous.pop(key)
    previous["source_sha256"] = V1_SOURCE_SHA256
    previous["protocol_sha256"] = V1_PROTOCOL_SHA256
    previous["explanation_sha256"] = V1_EXPLANATION_SHA256
    return previous


def strict_same_owner(actual: Any, expected: Any, label: str) -> None:
    require(type(actual) is dict and type(expected) is dict,
            "require two exact real artifact owners: " + label)
    for field in ("relative", "path", "sha256", "size_bytes", "device",
                  "inode", "mode"):
        left, right = actual.get(field), expected.get(field)
        require(type(left) is type(right) and left == right,
                "reject substituted content, permission, inode or device: " + label)
    require(type(actual.get("mode")) is int,
            "retain actual operating-system permissions: " + label)


def authenticate_sources(arguments: Mapping[str, Any]) -> dict[str, Any]:
    require(sys.executable == PINNED_PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "require genuine isolated CPython 3.14.6 with no bytecode writes")
    source_records: dict[str, dict[str, Any]] = {}
    frozen = (
        ("GOAL.md", GOAL_SHA256),
        ("oracle/phase1/p0-completeness-v1.json", PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["protocol_sha256"]),
        (EXPLANATION_RELATIVE, arguments["explanation_sha256"]),
        (V1_SOURCE_RELATIVE, V1_SOURCE_SHA256),
        (V1_PROTOCOL_RELATIVE, V1_PROTOCOL_SHA256),
        (V1_EXPLANATION_RELATIVE, V1_EXPLANATION_SHA256),
        (BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256),
        (BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256),
        (ACTIVATION_SOURCE_RELATIVE, ACTIVATION_SOURCE_SHA256),
        (ACTIVATION_PROTOCOL_RELATIVE, ACTIVATION_PROTOCOL_SHA256),
    )
    for relative, pin in frozen:
        raw, evidence = read_owned(ROOT, relative, pin, maximum=MAX_SOURCE_BYTES)
        source_records[relative] = evidence
        if relative == PROTOCOL_RELATIVE:
            validate_protocol(decode_document(
                raw, "pretty version-two frozen protocol",
                canonical_required=False,
            ))
    spec = checked_family(arguments["family"])
    for relative, pin in source_pins(spec, arguments["owned_source_sha256"]).items():
        _, evidence = read_owned(ROOT, relative, pin, maximum=MAX_SOURCE_BYTES)
        source_records[relative] = evidence
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate entered before genuine durable promotion verification")
    return source_records


def authenticate_corrected_activation(
    arguments: Mapping[str, Any], spec: FamilySpec,
) -> dict[str, Any]:
    root_string = checked_activation_root(arguments["activation_root"], spec)
    private_root = Path(root_string)
    report_raw, report_owner = read_owned(
        private_root, "activation-report.json",
        arguments["activation_report_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    receipt_raw, receipt_owner = read_owned(
        private_root, "activation-receipt.json",
        arguments["activation_receipt_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    report = decode_document(report_raw, "corrected actual activation report",
                             canonical_required=True)
    receipt = decode_document(receipt_raw, "corrected actual activation receipt",
                              canonical_required=True)
    recorded_journal = report.get("recovery_journal")
    require(type(recorded_journal) is dict
            and recorded_journal.get("relative") == "recovery-journal.json"
            and recorded_journal.get("mode") == 0o600,
            "a genuine 0600 durable prepared recovery journal is mandatory")
    journal_raw, journal_owner = read_owned(
        private_root, "recovery-journal.json",
        checked_digest(recorded_journal.get("sha256"), "recovery journal"),
        maximum=MAX_SOURCE_BYTES,
        exact_size=recorded_journal.get("size_bytes"), private=True,
    )
    strict_same_owner(journal_owner, recorded_journal,
                      "actual prepared native recovery journal")
    journal = decode_document(journal_raw, "actual prepared recovery journal",
                              canonical_required=True)
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    activator = importlib.import_module("tools.activate_verified_native_candidate_v1")
    require(type(activator) is types.ModuleType
            and activator.__name__ == "tools.activate_verified_native_candidate_v1"
            and os.path.abspath(activator.__file__)
            == str(ROOT / ACTIVATION_SOURCE_RELATIVE)
            and getattr(activator, "SCHEMA", None) == ACTIVATION_SCHEMA
            and getattr(activator, "RECEIPT_SCHEMA", None)
            == ACTIVATION_RECEIPT_SCHEMA
            and getattr(activator, "JOURNAL_SCHEMA", None)
            == ACTIVATION_JOURNAL_SCHEMA
            and getattr(activator, "INTENT_SCHEMA", None)
            == ACTIVATION_INTENT_SCHEMA
            and callable(getattr(activator, "validate_activation_documents", None))
            and callable(getattr(activator, "validate_promotion_intent", None))
            and callable(getattr(activator, "same_owner", None)),
            "load only the exact published corrected durable activation validator")
    validation_args = {
        "family": spec.name,
        "activation_root": root_string,
        "activation_source_sha256": ACTIVATION_SOURCE_SHA256,
        "activation_protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
        "activation_report_sha256": arguments["activation_report_sha256"],
        "activation_receipt_sha256": arguments["activation_receipt_sha256"],
    }
    try:
        promotion = activator.validate_activation_documents(
            report, receipt, journal, arguments=validation_args,
        )
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the authentic frozen activator rejected the complete promotion proofs"
        ) from error
    require(type(promotion) is dict and promotion.get("status") == "PASS"
            and promotion.get("schema") == ACTIVATION_SCHEMA
            + "-authenticated-promotion"
            and promotion.get("candidate_import_root") == str(ROOT)
            and promotion.get("family") == spec.name,
            "the true original source-owned activation validator was substituted")
    provenance = report.get("source_build_v2")
    require(type(provenance) is dict
            and provenance.get("schema") == BUILD_SCHEMA
            and provenance.get("family") == spec.name
            and provenance.get("source_sha256") == BUILD_SOURCE_SHA256
            and provenance.get("protocol_sha256") == BUILD_PROTOCOL_SHA256
            and provenance.get("archive_sha256")
            == arguments["build_archive_sha256"]
            and provenance.get("receipt_sha256")
            == arguments["build_receipt_sha256"],
            "the actual corrected promotion is not tied to its frozen V2 build")
    targets = report.get("canonical_targets")
    roles = {"extension"} if spec.name == "c" else {"engine", "bridge"}
    require(type(targets) is dict and set(targets) == roles
            and canonical(targets) == canonical(receipt.get("canonical_targets")),
            "require every actual version-two canonical native engine and bridge")
    verified_intents: dict[str, dict[str, Any]] = {}
    current_native: dict[str, dict[str, Any]] = {}
    for role in sorted(roles):
        target = targets[role]
        require(type(target) is dict and target.get("role") == role,
                "a source-built canonical native role was substituted")
        expected_relative = (spec.engine_relative
                             if role in {"extension", "engine"}
                             else spec.bridge_relative)
        expected_pin = (arguments["native_engine_sha256"]
                        if role in {"extension", "engine"}
                        else arguments["native_bridge_sha256"])
        require(target.get("relative") == expected_relative
                and target.get("sha256") == expected_pin,
                "a canonical artifact does not match its frozen family and V2 pin")
        _, current = read_owned(
            ROOT, expected_relative, expected_pin, maximum=MAX_BINARY_BYTES,
            exact_size=target.get("size_bytes"),
        )
        strict_same_owner(current, target,
                          "actually installed canonical native artifact")
        require(activator.same_owner(current, target) is True,
                "the frozen activator rejected the actual canonical native inode")
        intention = target.get("promotion_intent")
        expected_name = "promotion-intent-" + role + ".json"
        require(type(intention) is dict
                and intention.get("relative") == expected_name
                and intention.get("mode") == 0o600,
                "each genuine promoted native role needs its own 0600 intention")
        intent_bytes, intent_owner = read_owned(
            private_root, expected_name,
            checked_digest(intention.get("sha256"), "durable intent " + role),
            maximum=MAX_SOURCE_BYTES,
            exact_size=intention.get("size_bytes"), private=True,
        )
        strict_same_owner(intent_owner, intention,
                          "genuine actual 0600 durable promotion intention")
        intent = decode_document(intent_bytes,
                                 "actual independently durable promotion intention",
                                 canonical_required=True)
        validate_intent_shape(
            intent, intent_owner, intention, target, current,
            spec=spec, role=role, root=root_string,
            journal_sha256=recorded_journal["sha256"],
        )
        try:
            approved = activator.validate_promotion_intent(
                intent, family=spec.name, root=root_string, role=role,
                journal_sha256=recorded_journal["sha256"], current=current,
            )
        except (Exception, RecursionError) as error:
            raise SubinterpreterGateError(
                "the genuine frozen per-role promotion-intent validator rejected "
                + role
            ) from error
        strict_same_owner(approved, current,
                          "promotion intention bound to actual native file")
        current_native[role] = current
        verified_intents[role] = {
            "document_owner": intent_owner,
            "journal_sha256": journal_owner["sha256"],
            "target_owner": current,
            "validated_by_source_pinned_activator": True,
        }
    backups = report.get("backup_entries")
    require(type(backups) is dict and set(backups) == roles
            and canonical(backups) == canonical(journal.get("backup_entries"))
            and canonical(backups) == canonical(receipt.get("backup_entries")),
            "retain all recoverable original native backup journal records")
    actual_backups: dict[str, dict[str, Any] | None] = {}
    for role, entry in backups.items():
        require(type(entry) is dict and type(entry.get("originally_present")) is bool,
                "reject an invented original native-file backup state")
        if entry["originally_present"]:
            backup = entry.get("backup")
            require(type(backup) is dict and backup.get("mode") == 0o600
                    and backup.get("exclusive_creation") is True
                    and backup.get("same_inode_readback_verified") is True
                    and backup.get("file_fsync_completed") is True,
                    "require a recoverable durable 0600 original native backup")
            _, saved = read_owned(
                private_root, backup.get("relative"),
                checked_digest(backup.get("sha256"), "original native backup"),
                maximum=MAX_BINARY_BYTES,
                exact_size=backup.get("size_bytes"), private=True,
            )
            strict_same_owner(saved, backup,
                              "actually recoverable unchanged native backup")
            actual_backups[role] = saved
        else:
            require(entry.get("backup") is None
                    and entry.get("original_owner") is None,
                    "an absent native file cannot claim a fabricated backup")
            actual_backups[role] = None
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a native candidate escaped genuine pre-execution promotion validation")
    return {
        "schema": ACTIVATION_SCHEMA + "-actual-intent-validated-promotion",
        "status": "PASS", "family": spec.name,
        "candidate_import_root": str(ROOT),
        "backup_root": root_string,
        "report": report_owner, "receipt": receipt_owner,
        "recovery_journal": journal_owner,
        "native_owners": current_native,
        "promotion_intents": verified_intents,
        "backup_owners": actual_backups,
        "original_guard_root_rebound": False,
        "source_build_archive_sha256": arguments["build_archive_sha256"],
        "source_build_receipt_sha256": arguments["build_receipt_sha256"],
        "candidate_imports": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "performance": "NOT MEASURED",
    }


def authenticate_prerequisites(arguments: Mapping[str, Any]) -> dict[str, Any]:
    support = authenticate_sources(arguments)
    spec = checked_family(arguments["family"])
    corrected_activation = authenticate_corrected_activation(arguments, spec)
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    original = importlib.import_module("tools.run_owned_candidate_subinterpreters_v1")
    require(type(original) is types.ModuleType
            and original.__name__ == "tools.run_owned_candidate_subinterpreters_v1"
            and os.path.abspath(original.__file__) == str(ROOT / V1_SOURCE_RELATIVE)
            and getattr(original, "SOURCE_RELATIVE", None) == V1_SOURCE_RELATIVE
            and getattr(original, "REFERENCE_PROGRAM_SHA256", None)
            == ORIGINAL_PROGRAM_SHA256
            and getattr(original, "ADAPTED_PROGRAM_SHA256", None)
            == ADAPTED_PROGRAM_SHA256
            and getattr(original, "CASE_EXEC_COUNT", None) == CASE_EXECUTIONS
            and getattr(original, "INTERPRETER_COUNT", None) == INTERPRETER_COUNT,
            "load only the exact unchanged genuine frozen original interpreter route")
    previous_args = legacy_arguments(arguments)
    try:
        verified_previous = original.authenticate_prerequisites(previous_args)
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the untouched original genuine-interpreter prerequisites did not pass"
        ) from error
    require(type(verified_previous) is dict
            and verified_previous.get("spec") is not None
            and getattr(verified_previous["spec"], "name", None) == spec.name,
            "the authenticated original V1 recorder changed candidate families")
    return {
        "support": support, "spec": spec, "previous": original,
        "previous_arguments": previous_args,
        "previous_context": verified_previous,
        "corrected_activation": corrected_activation,
    }


def worker_arguments(arguments: Mapping[str, Any]) -> list[str]:
    mapping = (
        ("--family", "family"), ("--label", "label"),
        ("--source-sha256", "source_sha256"),
        ("--protocol-sha256", "protocol_sha256"),
        ("--explanation-sha256", "explanation_sha256"),
        ("--v1-source-sha256", "v1_source_sha256"),
        ("--v1-protocol-sha256", "v1_protocol_sha256"),
        ("--v1-explanation-sha256", "v1_explanation_sha256"),
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
        ("--candidate-source-sha256", "candidate_source_sha256"),
        ("--native-engine-sha256", "native_engine_sha256"),
        ("--native-bridge-sha256", "native_bridge_sha256"),
    )
    result = [PINNED_PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE),
              "--internal-worker"]
    for option, key in mapping:
        result.extend((option, arguments[key]))
    for owner in arguments["owned_source_sha256"]:
        result.extend(("--owned-source-sha256", owner))
    return result


def validate_worker(
    report: Any, *, context: Mapping[str, Any], expected_pid: int,
) -> dict[str, Any]:
    require(type(report) is dict
            and report.get("schema") == SCHEMA + "-actual-worker"
            and report.get("status") == "PASS"
            and report.get("pid") == expected_pid,
            "a complete real corrected-version-two interpreter worker is required")
    activation = report.get("corrected_promotion")
    require(type(activation) is dict
            and canonical(activation) == canonical(context["corrected_activation"]),
            "the actual worker changed verified durable native promotion proof")
    previous = context["previous"]
    original_document = copy.deepcopy(report)
    original_document["schema"] = previous.SCHEMA + "-actual-worker"
    original_document.pop("corrected_promotion")
    original_document.pop("previous_original_source_sha256")
    original_document.pop("previous_original_protocol_sha256")
    baseline = previous.load_original_baseline()
    try:
        previous.validate_worker_document(
            original_document,
            spec=context["previous_context"]["spec"],
            pins=context["previous_context"]["pins"],
            original=baseline, expected_pid=expected_pid,
        )
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the immutable genuine original observer rejected the corrected worker"
        ) from error
    for name, expected in (
        ("case_count", CASE_COUNT),
        ("actual_case_interpreter_exec_calls", CASE_EXECUTIONS),
        ("actual_initialization_interpreter_exec_calls", INTERPRETER_COUNT),
        ("actual_guard_cleanup_interpreter_exec_calls", INTERPRETER_COUNT),
        ("actual_interpreters_created", INTERPRETER_COUNT),
        ("actual_interpreters_destroyed", INTERPRETER_COUNT),
    ):
        require(type(report.get(name)) is int and report[name] == expected,
                "the genuine actual original interpreter lifecycle changed: " + name)
    require(report.get("previous_original_source_sha256") == V1_SOURCE_SHA256
            and report.get("previous_original_protocol_sha256") == V1_PROTOCOL_SHA256,
            "the genuine previous original recorder source was substituted")
    return report


def internal_worker(arguments: Mapping[str, Any]) -> dict[str, Any]:
    context = authenticate_prerequisites(arguments)
    previous = context["previous"]
    try:
        actual = previous.internal_worker(context["previous_arguments"])
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the original frozen 394-execution subinterpreter worker failed"
        ) from error
    require(type(actual) is dict and actual.get("status") == "PASS"
            and actual.get("schema") == previous.SCHEMA + "-actual-worker",
            "the authentic unchanged original interpreter did not complete")
    result = dict(actual)
    result["schema"] = SCHEMA + "-actual-worker"
    result["corrected_promotion"] = context["corrected_activation"]
    result["previous_original_source_sha256"] = V1_SOURCE_SHA256
    result["previous_original_protocol_sha256"] = V1_PROTOCOL_SHA256
    return validate_worker(result, context=context, expected_pid=os.getpid())


def evidence_names(spec: FamilySpec, label: str,
                   *, failure: bool) -> tuple[str, str]:
    stem = "owned-candidate-subinterpreters-v2-" + spec.name + "-" + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_evidence_fresh(spec: FamilySpec, label: str) -> None:
    parent = ROOT / EVIDENCE_RELATIVE
    actual = os.lstat(str(parent))
    require(stat.S_ISDIR(actual.st_mode) and not stat.S_ISLNK(actual.st_mode),
            "require the genuine version-two durable evidence directory")
    for failed in (False, True):
        for name in evidence_names(spec, label, failure=failed):
            try:
                os.lstat(str(parent / name))
            except FileNotFoundError:
                continue
            raise SubinterpreterGateError(
                "refusing to overwrite preserved version-two results: " + name
            )


def publish_report(
    report: dict[str, Any], spec: FamilySpec, label: str,
    original: types.ModuleType,
) -> dict[str, Any]:
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(spec, label, failure=failed)
    plain = canonical_line(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "preserve a complete bounded genuine version-two report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(len(compressed) <= MAX_ARCHIVE_BYTES,
            "a genuine complete report exceeds its deterministic archive bound")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(str(ROOT / EVIDENCE_RELATIVE), flags)
    try:
        archive = original.write_fresh_evidence(directory, archive_name, compressed)
        os.fsync(directory)
        receipt = {
            "schema": RECEIPT_SCHEMA, "status": "PASS",
            "result_status": report["status"],
            "candidate_family": spec.name, "label": label,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "explanation_sha256": report["explanation_sha256"],
            "v1_source_sha256": V1_SOURCE_SHA256,
            "v1_protocol_sha256": V1_PROTOCOL_SHA256,
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
            "archive_directory_fsync": True,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "receipt_self_publication": "NOT CLAIMED",
        }
        receipt_bytes = canonical_line(receipt)
        evidence = original.write_fresh_evidence(directory, receipt_name,
                                                receipt_bytes)
        os.fsync(directory)
    finally:
        os.close(directory)
    return {
        "schema": SCHEMA + "-published-candidate-result",
        "status": report["status"], "candidate_family": spec.name,
        "label": label, "archive": archive, "receipt": evidence,
        "failure_preserved": failed, "directory_fsync": True,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def run_candidate(arguments: Mapping[str, Any]) -> dict[str, Any]:
    context = authenticate_prerequisites(arguments)
    spec: FamilySpec = context["spec"]
    previous = context["previous"]
    label = checked_label(arguments["label"])
    ensure_evidence_fresh(spec, label)
    baseline = previous.load_original_baseline()
    report: dict[str, Any] = {
        "schema": SCHEMA + "-candidate-evaluation", "status": "FAIL",
        "candidate_family": spec.name, "label": label,
        "source_sha256": arguments["source_sha256"],
        "protocol_sha256": arguments["protocol_sha256"],
        "explanation_sha256": arguments["explanation_sha256"],
        "v1_source_sha256": V1_SOURCE_SHA256,
        "v1_protocol_sha256": V1_PROTOCOL_SHA256,
        "activation_report_sha256": arguments["activation_report_sha256"],
        "activation_receipt_sha256": arguments["activation_receipt_sha256"],
        "corrected_activation": context["corrected_activation"],
        "static_independence_audit": None,
        "worker": None, "worker_process": None, "failure": None,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }
    process: Any = None
    try:
        report["static_independence_audit"] = previous.invoke_static_independence_audit(
            context["previous_context"]["spec"],
            context["previous_context"]["source_owners"],
        )
        process = subprocess.Popen(
            worker_arguments(arguments), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(ROOT), shell=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
        captured = previous.capture_process(
            process, "intent-authenticated genuine 394-case native subinterpreter",
        )
        report["worker_process"] = {
            key: value for key, value in captured.items()
            if key not in {"stdout_bytes", "stderr_bytes"}
        }
        require(captured.get("timed_out") is False
                and process.returncode == 0
                and captured.get("stderr_bytes") == b"",
                "a genuine corrected interpreter worker failed, crashed or timed out")
        worker = decode_document(
            captured.get("stdout_bytes"), "genuine corrected isolated worker",
            canonical_required=True,
        )
        report["worker"] = validate_worker(worker, context=context,
                                           expected_pid=process.pid)
        require(canonical(worker.get("records"))
                == canonical(worker.get("peer_records"))
                and canonical(worker.get("records"))
                == canonical(worker.get("repeated_a_records")),
                "the complete unchanged 128-case A/B/A observations disagree")
        report["projected_reference_records_sha256"] = PROJECTED_SHA256
        report["supplemental_case_count"] = CASE_COUNT
        report["phase1_case_execution_denominator"] = 31237
        report["supplemental_cases_added_to_phase1_denominator"] = False
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
    return publish_report(report, spec, label, previous)


def project_reference(record: Any) -> dict[str, Any]:
    fields = {
        "case_id", "cohort", "ordinal", "seed", "variant", "status",
        "actual_exec", "candidate_imports", "locale_unchanged",
        "stdlib_origin_verified", "pinned_executable_verified", "observation",
    }
    require(type(record) is dict and set(record) == fields
            and type(record.get("candidate_imports")) is int
            and record["candidate_imports"] == 0
            and record.get("stdlib_origin_verified") is True
            and record.get("actual_exec") is True
            and record.get("locale_unchanged") is True
            and record.get("pinned_executable_verified") is True
            and record.get("status") == "PASS"
            and type(record.get("observation")) is dict,
            "retain the complete unchanged original subinterpreter observation")
    result = {key: value for key, value in record.items()
              if key not in {"candidate_imports", "stdlib_origin_verified"}}
    observation = dict(record["observation"])
    for original, replacement in RENAMES.items():
        if original in observation:
            require(replacement not in observation,
                    "reject a collided original matching-owner observation")
            observation[replacement] = observation.pop(original)
    result["observation"] = observation
    return result


def validate_candidate_observation(
    row: Any, baseline: Any, spec: FamilySpec,
    pins: Mapping[str, str],
) -> dict[str, Any]:
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
    require(type(row) is dict and set(row) == fields,
            "retain every genuine candidate matching and engine provenance field")
    require(row.get("candidate_family") == spec.name
            and row.get("candidate_module") == spec.module
            and row.get("candidate_origin_verified") is True
            and type(row.get("candidate_import_count")) is int
            and row["candidate_import_count"] >= 1,
            "the actual independently owned candidate was substituted")
    for field, key in (
        ("candidate_source_sha256", "source"),
        ("candidate_engine_sha256", "engine"),
        ("candidate_bridge_sha256", "bridge"),
    ):
        require(row.get(field) == checked_digest(pins.get(key), field),
                "an original candidate native owner changed")
    require((row["candidate_engine_sha256"]
             == row["candidate_bridge_sha256"]) is (spec.name == "c"),
            "only the actual C combined engine and bridge may share bytes")
    for field in ("original_matcher_calls", "external_engine_imports",
                  "cross_candidate_imports", "foreign_native_loads"):
        require(type(row.get(field)) is int and row[field] == 0,
                "an original matcher, sibling or external native engine escaped")
    actual = {key: row[key] for key in project_reference(baseline)}
    require(canonical(actual) == canonical(project_reference(baseline)),
            "an exact genuine original case or observation type differs")
    return actual


def validate_intent_shape(
    intention: Any, owner: Any, recorded_owner: Any,
    target: Any, current: Any,
    *, spec: FamilySpec, role: str, root: str,
    journal_sha256: str,
) -> None:
    require(role in ({"extension"} if spec.name == "c"
                     else {"engine", "bridge"}),
            "reject a missing, sibling or fabricated durable native role")
    expected_relative = (spec.engine_relative
                         if role in {"extension", "engine"}
                         else spec.bridge_relative)
    require(type(intention) is dict
            and intention.get("schema") == ACTIVATION_INTENT_SCHEMA
            and intention.get("status") == "PREPARED"
            and intention.get("promotion_mode")
            == "recoverable-canonical-promotion"
            and intention.get("family") == spec.name
            and intention.get("activation_root") == root
            and intention.get("candidate_import_root") == str(ROOT)
            and intention.get("recovery_journal_sha256") == journal_sha256
            and intention.get("role") == role,
            "an actual immutable original-source promotion intention changed")
    expected_name = "promotion-intent-" + role + ".json"
    strict_same_owner(owner, recorded_owner,
                      "recorded and actual 0600 promotion-intent inode")
    require(type(owner) is dict and owner.get("relative") == expected_name
            and owner.get("path") == root + "/" + expected_name
            and owner.get("mode") == 0o600
            and owner.get("sha256") == sha256(canonical_line(intention))
            and owner.get("size_bytes") == len(canonical_line(intention))
            and type(owner.get("device")) is int
            and type(owner.get("inode")) is int,
            "the actual durable 0600 promotion intent bytes or inode differ")
    require(type(target) is dict and type(current) is dict
            and target.get("relative") == expected_relative
            and target.get("path") == str(ROOT / expected_relative),
            "the promotion intent references a different canonical native target")
    strict_same_owner(target, current,
                      "durable intention and exact promoted canonical inode")
    intended = intention.get("target")
    strict_same_owner(intended, current,
                      "actual durable staged native target")


class SourceOnlyBoundary:
    """Block every actual effect during deterministic synthetic controls."""

    def __init__(self) -> None:
        self.attempts: dict[str, int] = {
            "file_reads": 0, "file_writes": 0, "descriptor_reads": 0,
            "descriptor_writes": 0, "pipes": 0, "processes": 0,
            "threads": 0, "candidate_imports": 0,
            "interpreter_imports": 0, "activation_imports": 0,
            "legacy_recorder_imports": 0, "dynamic_imports": 0,
            "native_library_loads": 0, "audit_hooks": 0,
            "locale_changes": 0, "clock_samples": 0,
            "garbage_collections": 0, "network_requests": 0,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
        }
        self._stack = contextlib.ExitStack()
        self._before: frozenset[str] = frozenset()

    def blocked(self, category: str) -> Callable[..., Any]:
        require(category in self.attempts,
                "require a real named source-only safety boundary")

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
        original_import = builtins.__import__

        def guarded_import(name: Any, globals: Any = None, locals: Any = None,
                           fromlist: Any = (), level: int = 0) -> Any:
            if type(name) is str and (
                name == "candidates" or name.startswith("candidates.")
            ):
                return self.blocked("candidate_imports")()
            if type(name) is str and (
                name == "concurrent.interpreters"
                or name.startswith("concurrent.interpreters.")
                or name in {"_interpreters", "_interpqueues", "_interpchannels"}
                or (name == "concurrent" and fromlist is not None
                    and any(value == "interpreters" for value in fromlist))
            ):
                return self.blocked("interpreter_imports")()
            if type(name) is str and (
                name in {"ctypes", "_ctypes", "cffi", "_cffi_backend"}
                or name.startswith(("ctypes.", "cffi."))
            ):
                return self.blocked("native_library_loads")()
            if name == "socket" or (type(name) is str
                                     and name.startswith("socket.")):
                return self.blocked("network_requests")()
            if type(name) is str and (name == "multiprocessing"
                                      or name.startswith("multiprocessing.")):
                return self.blocked("processes")()
            if name == "tools.activate_verified_native_candidate_v1":
                return self.blocked("activation_imports")()
            if name == "tools.run_owned_candidate_subinterpreters_v1":
                return self.blocked("legacy_recorder_imports")()
            return original_import(name, globals, locals, fromlist, level)

        self._stack.callback(setattr, builtins, "__import__", original_import)
        builtins.__import__ = guarded_import
        for target, name in ((builtins, "open"), (io, "open"), (io, "open_code")):
            self.patch(target, name, "file_reads")
        for name in ("open", "stat", "lstat", "scandir", "listdir", "access"):
            self.patch(os, name, "file_reads")
        self.patch(os, "read", "descriptor_reads")
        self.patch(os, "pipe", "pipes")
        for name in ("write", "unlink", "remove", "rename", "replace",
                     "mkdir", "rmdir", "fsync", "fdatasync", "chmod"):
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
        existing = sys.modules.get("ctypes")
        if existing is not None:
            self.patch(existing, "CDLL", "native_library_loads")
            self.patch(existing, "PyDLL", "native_library_loads")
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> None:
        self._stack.close()
        added = set(sys.modules) - self._before
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in added),
                "the synthetic controls imported a real native candidate")
        require(not any(name == "concurrent.interpreters"
                        or name.startswith("concurrent.interpreters.")
                        or name in {"_interpreters", "_interpqueues",
                                    "_interpchannels"}
                        for name in added),
                "the synthetic controls imported a real subinterpreter")
        require("tools.activate_verified_native_candidate_v1" not in added
                and "tools.run_owned_candidate_subinterpreters_v1" not in added,
                "the synthetic controls loaded an actual controller")


def synthetic_pins(spec: FamilySpec) -> dict[str, str]:
    source = sha256((spec.name + ":source").encode("ascii"))
    engine = sha256((spec.name + ":engine").encode("ascii"))
    bridge = (engine if spec.name == "c"
              else sha256((spec.name + ":bridge").encode("ascii")))
    return {"source": source, "engine": engine, "bridge": bridge}


def synthetic_case(index: int) -> dict[str, Any]:
    require(type(index) is int and 0 <= index < CASE_COUNT,
            "require one exact synthetic source-only observation")
    return {
        "case_id": "synthetic-v2-" + str(index).zfill(3),
        "cohort": ("repeated-interpreter-creation-and-destruction"
                   if index < 8 else "source-only-cohort-" + str(index // 8)),
        "ordinal": index, "seed": 1_000_000 + index,
        "variant": index % 8, "status": "PASS", "actual_exec": True,
        "candidate_imports": 0, "locale_unchanged": True,
        "stdlib_origin_verified": True, "pinned_executable_verified": True,
        "observation": {
            "owner_state_intact": True,
            **{field: True for field in RENAMES},
            "captured_index": index,
        },
    }


def synthetic_candidate(index: int, spec: FamilySpec) -> dict[str, Any]:
    pins = synthetic_pins(spec)
    return {
        **project_reference(synthetic_case(index)),
        "candidate_family": spec.name, "candidate_module": spec.module,
        "candidate_source_sha256": pins["source"],
        "candidate_engine_sha256": pins["engine"],
        "candidate_bridge_sha256": pins["bridge"],
        "candidate_origin_verified": True, "candidate_import_count": 1,
        "original_matcher_calls": 0, "external_engine_imports": 0,
        "cross_candidate_imports": 0, "foreign_native_loads": 0,
    }


def synthetic_arguments(spec: FamilySpec) -> list[str]:
    pins = synthetic_pins(spec)
    arguments = [
        "--record-candidate", "--family", spec.name,
        "--label", "synthetic-v2", "--source-sha256", "a" * 64,
        "--protocol-sha256", "b" * 64,
        "--explanation-sha256", "c" * 64,
        "--v1-source-sha256", V1_SOURCE_SHA256,
        "--v1-protocol-sha256", V1_PROTOCOL_SHA256,
        "--v1-explanation-sha256", V1_EXPLANATION_SHA256,
        "--build-label", "phase2-v2",
        "--build-source-sha256", BUILD_SOURCE_SHA256,
        "--build-protocol-sha256", BUILD_PROTOCOL_SHA256,
        "--build-archive-sha256", "d" * 64,
        "--build-receipt-sha256", "e" * 64,
        "--activation-root", ACTIVATION_PREFIX + spec.name + "-synthetic",
        "--activation-source-sha256", ACTIVATION_SOURCE_SHA256,
        "--activation-protocol-sha256", ACTIVATION_PROTOCOL_SHA256,
        "--activation-report-sha256", "f" * 64,
        "--activation-receipt-sha256", "1" * 64,
        "--candidate-source-sha256", pins["source"],
        "--native-engine-sha256", pins["engine"],
        "--native-bridge-sha256", pins["bridge"],
    ]
    for relative in spec.owners:
        expected = (pins["source"] if relative == spec.source_relative
                    else sha256(relative.encode("ascii")))
        arguments.extend(("--owned-source-sha256", relative + "=" + expected))
    return arguments


def synthetic_intention(spec: FamilySpec, role: str) -> dict[str, Any]:
    pins = synthetic_pins(spec)
    root = ACTIVATION_PREFIX + spec.name + "-synthetic"
    journal = sha256((spec.name + ":journal").encode("ascii"))
    relative = (spec.engine_relative if role in {"extension", "engine"}
                else spec.bridge_relative)
    target = {
        "relative": relative, "path": str(ROOT / relative),
        "sha256": pins["engine"] if role in {"extension", "engine"}
        else pins["bridge"],
        "size_bytes": 1024, "device": 2064,
        "inode": 40_000 + (0 if role in {"extension", "engine"} else 1),
        "mode": 0o600,
    }
    intention = {
        "schema": ACTIVATION_INTENT_SCHEMA, "status": "PREPARED",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": spec.name, "activation_root": root,
        "candidate_import_root": str(ROOT),
        "recovery_journal_sha256": journal,
        "role": role, "target": dict(target),
    }
    raw = canonical_line(intention)
    owner = {
        "relative": "promotion-intent-" + role + ".json",
        "path": root + "/promotion-intent-" + role + ".json",
        "sha256": sha256(raw), "size_bytes": len(raw),
        "device": 2064, "inode": 80_000 + (0 if role in {"extension", "engine"}
                                               else 1),
        "mode": 0o600,
    }
    return {"document": intention, "owner": owner,
            "recorded_owner": dict(owner),
            "target": target, "current": dict(target),
            "root": root, "journal_sha256": journal}


def self_test() -> dict[str, Any]:
    positive: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: Any) -> None:
        require(type(name) is str and name not in positive and name not in rejected,
                "require separately named synthetic positive controls")
        require(value is True, "a genuine synthetic control failed: " + name)
        positive.append(name)

    def refuse(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in positive and name not in rejected,
                "require separately named synthetic hostile controls")
        try:
            action()
        except (SubinterpreterGateError, OSError, ValueError, TypeError,
                KeyError, AttributeError, UnicodeError, RecursionError,
                OverflowError, binascii.Error):
            rejected.append(name)
            return
        raise SubinterpreterGateError(
            "a hostile synthetic durable-interpreter control escaped: " + name
        )

    with SourceOnlyBoundary() as boundary:
        protocol = synthetic_protocol()
        accept("exact-strict-frozen-v2-protocol",
               validate_protocol(protocol) is protocol)
        accept("version-one-original-recorder-immutable",
               protocol["previous_original_recorder"]["source_sha256"]
               == V1_SOURCE_SHA256
               and protocol["previous_original_recorder"]["source_mutated"] is False)
        accept("published-corrected-activator-source",
               protocol["corrected_canonical_activation"]["source_sha256"]
               == ACTIVATION_SOURCE_SHA256)
        accept("exact-one-real-c-version-two-source-build",
               protocol["source_build_v2"]["completed_family_count"] == 1
               and protocol["source_build_v2"]["c"]["archive_sha256"]
               == C_BUILD_ARCHIVE_SHA256)
        accept("rust-and-zig-not-source-built",
               protocol["source_build_v2"]["rust"] == "NOT RUN"
               and protocol["source_build_v2"]["zig"] == "NOT RUN")
        accept("source-published-no-activation-run",
               protocol["corrected_canonical_activation"]
               ["actual_activations_completed"] == 0)
        accept("immutable-original-canonical-guard",
               protocol["corrected_canonical_activation"]
               ["frozen_guard_root_mutation_allowed"] is False)
        accept("separately-required-real-0600-native-intention",
               protocol["corrected_canonical_activation"]
               ["per_role_intent_actual_bytes_required"] is True)
        accept("no-semantics-added-to-phase-one-denominator",
               protocol["phase1"]["case_execution_denominator"] == 31237
               and protocol["phase1"]
               ["supplemental_cases_added_to_phase1_denominator"] is False)
        accept("genuine-original-observer-program-pins",
               protocol["reference"]["producer_program_sha256"]
               == ORIGINAL_PROGRAM_SHA256
               and protocol["reference"]["adapted_program_sha256"]
               == ADAPTED_PROGRAM_SHA256)
        accept("compact-canonical-original-no-newline",
               not canonical(protocol).endswith(b"\n")
               and canonical_line(protocol).endswith(b"\n"))
        accept("pretty-frozen-protocol-without-fabricated-bytes",
               validate_protocol(decode_document(
                   json.dumps(protocol, indent=2).encode("utf-8"),
                   "synthetic pretty protocol", canonical_required=False,
               )) == protocol)
        accept("bounded-correctness-worker-timeouts",
               PROCESS_TIMEOUT_SECONDS == 180 and PROCESS_CLEANUP_SECONDS == 15)
        for name, raw, strict, newline in (
            ("duplicate-json-keys", b'{"x":1,"x":2}', False, False),
            ("nonfinite-json", b'{"x":NaN}', False, False),
            ("positive-infinite-json", b'{"x":Infinity}', False, False),
            ("negative-infinite-json", b'{"x":-Infinity}', False, False),
            ("unexpected-json-whitespace", b'{ "x": 1 }', True, False),
            ("unexpected-json-newline", b'{"x":1}\n', True, False),
            ("missing-json-newline", b'{"x":1}', True, True),
            ("json-hidden-suffix", b'{"x":1}\nhidden', True, True),
            ("invalid-json-utf8", b'\xff', False, False),
            ("invalid-json-surrogate", b'{"x":"\\ud800"}', False, False),
        ):
            refuse(name, lambda raw=raw, strict=strict, newline=newline:
                   decode_document(raw, "synthetic poisoned JSON",
                                   canonical_required=strict, newline=newline))

        def mutate_protocol(section: str, key: str, value: Any) -> None:
            changed = copy.deepcopy(protocol)
            changed[section][key] = value
            validate_protocol(changed)

        attacks = (
            ("python", "isolated", 1),
            ("python", "bytecode_writes", 0),
            ("controller", "source_path", V1_SOURCE_RELATIVE),
            ("controller", "source_sha256_mode", "optional"),
            ("previous_original_recorder", "source_sha256", "0" * 64),
            ("previous_original_recorder", "protocol_sha256", "0" * 64),
            ("previous_original_recorder", "source_mutated", 0),
            ("previous_original_recorder", "semantic_program_mutated", 0),
            ("phase1", "suite_count", 13.0),
            ("phase1", "case_execution_denominator", 31237.0),
            ("phase1", "case_execution_denominator", 31365),
            ("phase1", "supplemental_cases_added_to_phase1_denominator", 0),
            ("source_build_v2", "completed_family_count", 0),
            ("source_build_v2", "completed_family_count", True),
            ("source_build_v2", "rust", "PASS"),
            ("source_build_v2", "zig", "PASS"),
            ("corrected_canonical_activation", "source_sha256", "0" * 64),
            ("corrected_canonical_activation", "protocol_sha256", "0" * 64),
            ("corrected_canonical_activation", "actual_activations_completed", 1),
            ("corrected_canonical_activation", "actual_activations_completed", False),
            ("corrected_canonical_activation", "frozen_guard_root_mutation_allowed", True),
            ("corrected_canonical_activation", "per_role_intent_actual_bytes_required", False),
            ("corrected_canonical_activation", "actual_report_receipt_journal_intent_backup_mode", "0644"),
            ("corrected_canonical_activation", "private_journal_root_mode", "0755"),
            ("reference", "case_count", 127),
            ("reference", "case_count", 128.0),
            ("reference", "adapted_program_sha256", "0" * 64),
            ("lifecycle", "actual_case_interpreter_exec_calls", 393),
            ("lifecycle", "actual_initialization_interpreter_exec_calls", 10),
            ("lifecycle", "actual_guard_cleanup_interpreter_exec_calls", 10),
            ("lifecycle", "all_real_pipes_read_to_eof", 1),
            ("boundaries", "hidden_cases_read", 1),
            ("boundaries", "hidden_cases_read", False),
            ("boundaries", "benchmark_files_read", 1),
            ("boundaries", "winner_selected", 0),
        )
        for index, (section, key, value) in enumerate(attacks):
            refuse("protocol-" + section + "-" + key + "-" + str(index),
                   lambda section=section, key=key, value=value:
                   mutate_protocol(section, key, value))

        for original in RENAMES:
            def missing_rename(original: str = original) -> None:
                changed = copy.deepcopy(protocol)
                del changed["lossless_observation_field_renames"][original]
                validate_protocol(changed)

            refuse("omitted-lossless-identity-" + original, missing_rename)

        for spec in FAMILIES.values():
            pins = synthetic_pins(spec)
            chosen = parse_arguments(synthetic_arguments(spec))
            accept("exact-pinned-original-and-activation-cli-" + spec.name,
                   chosen["v1_source_sha256"] == V1_SOURCE_SHA256
                   and chosen["activation_source_sha256"]
                   == ACTIVATION_SOURCE_SHA256)
            accept("exact-own-independent-source-closure-" + spec.name,
                   len(source_pins(spec, chosen["owned_source_sha256"]))
                   == len(spec.owners))

            def poison_cli(option: str, replacement: str | None,
                           *, repeated: bool = False,
                           selected: FamilySpec = spec) -> None:
                values = synthetic_arguments(selected)
                position = values.index(option)
                if replacement is None:
                    del values[position:position + 2]
                elif repeated:
                    values.extend((option, replacement))
                else:
                    values[position + 1] = replacement
                parse_arguments(values)

            for option in (
                "--v1-source-sha256", "--v1-protocol-sha256",
                "--v1-explanation-sha256", "--build-source-sha256",
                "--build-protocol-sha256", "--build-archive-sha256",
                "--build-receipt-sha256", "--activation-root",
                "--activation-source-sha256", "--activation-protocol-sha256",
                "--activation-report-sha256", "--activation-receipt-sha256",
            ):
                refuse("missing-v2-proof-" + spec.name + "-" + option[2:],
                       lambda option=option, spec=spec:
                       poison_cli(option, None, selected=spec))
            for option, changed in (
                ("--v1-source-sha256", "0" * 64),
                ("--v1-protocol-sha256", "0" * 64),
                ("--v1-explanation-sha256", "0" * 64),
                ("--build-source-sha256", V1_SOURCE_SHA256),
                ("--build-protocol-sha256", V1_PROTOCOL_SHA256),
                ("--activation-source-sha256", V1_SOURCE_SHA256),
                ("--activation-protocol-sha256", V1_PROTOCOL_SHA256),
            ):
                refuse("changed-published-source-" + spec.name + "-" + option[2:],
                       lambda option=option, changed=changed, spec=spec:
                       poison_cli(option, changed, selected=spec))
            other = "zig" if spec.name != "zig" else "c"
            refuse("cross-family-private-journal-" + spec.name,
                   lambda spec=spec, other=other:
                   poison_cli("--activation-root",
                              ACTIVATION_PREFIX + other + "-synthetic",
                              selected=spec))
            refuse("escaping-private-journal-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--activation-root",
                              ACTIVATION_PREFIX + spec.name + "-x/../escape",
                              selected=spec))
            refuse("duplicate-activation-report-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--activation-report-sha256", "f" * 64,
                              repeated=True, selected=spec))
            refuse("omitted-semantic-owner-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--owned-source-sha256", None, selected=spec))
            if spec.name == "c":
                refuse("forged-distinct-combined-c-engine",
                       lambda spec=spec:
                       poison_cli("--native-bridge-sha256", "4" * 64,
                                  selected=spec))
            else:
                refuse("forged-combined-independent-engine-" + spec.name,
                       lambda spec=spec:
                       poison_cli("--native-bridge-sha256",
                                  synthetic_pins(spec)["engine"],
                                  selected=spec))

            for index in range(CASE_COUNT):
                baseline = synthetic_case(index)
                observed = synthetic_candidate(index, spec)
                accept("complete-source-observation-" + spec.name + "-" + str(index),
                       canonical(validate_candidate_observation(
                           observed, baseline, spec, pins,
                       )) == canonical(project_reference(baseline)))
                if spec.name == "c":
                    def missing_case(index: int = index) -> None:
                        altered = synthetic_candidate(index, spec)
                        del altered["observation"]
                        validate_candidate_observation(altered,
                                                       synthetic_case(index),
                                                       spec, pins)

                    def forged_case(index: int = index) -> None:
                        altered = synthetic_candidate(index, spec)
                        altered["observation"]["captured_index"] += 1
                        validate_candidate_observation(altered,
                                                       synthetic_case(index),
                                                       spec, pins)

                    refuse("omitted-original-case-observation-" + str(index),
                           missing_case)
                    refuse("changed-original-case-observation-" + str(index),
                           forged_case)

            roles = ("extension",) if spec.name == "c" else ("engine", "bridge")
            for role in roles:
                bundle = synthetic_intention(spec, role)
                validate_intent_shape(
                    bundle["document"], bundle["owner"],
                    bundle["recorded_owner"], bundle["target"],
                    bundle["current"], spec=spec, role=role,
                    root=bundle["root"], journal_sha256=bundle["journal_sha256"],
                )
                accept("complete-real-role-intent-shape-" + spec.name + "-" + role,
                       True)

                def poison_intent(part: str, field: str, value: Any,
                                  *, spec: FamilySpec = spec,
                                  role: str = role) -> None:
                    changed = copy.deepcopy(synthetic_intention(spec, role))
                    changed[part][field] = value
                    validate_intent_shape(
                        changed["document"], changed["owner"],
                        changed["recorded_owner"], changed["target"],
                        changed["current"], spec=spec, role=role,
                        root=changed["root"],
                        journal_sha256=changed["journal_sha256"],
                    )

                attacks = (
                    ("document", "schema", ACTIVATION_JOURNAL_SCHEMA),
                    ("document", "status", "PASS"),
                    ("document", "family", "foreign"),
                    ("document", "role", "foreign"),
                    ("document", "candidate_import_root", "/tmp/foreign"),
                    ("document", "recovery_journal_sha256", "0" * 64),
                    ("owner", "mode", 0o644),
                    ("owner", "mode", False),
                    ("owner", "sha256", "0" * 64),
                    ("owner", "size_bytes", False),
                    ("owner", "inode", 999999),
                    ("owner", "device", 999999),
                    ("target", "inode", 999999),
                    ("target", "mode", 0o644),
                    ("target", "relative", "candidates/foreign.so"),
                    ("current", "inode", 999999),
                    ("current", "mode", 0o644),
                    ("current", "sha256", "0" * 64),
                )
                for attack_index, (part, field, value) in enumerate(attacks):
                    refuse("intent-" + spec.name + "-" + role + "-"
                           + part + "-" + field + "-" + str(attack_index),
                           lambda part=part, field=field, value=value,
                           spec=spec, role=role:
                           poison_intent(part, field, value,
                                         spec=spec, role=role))

        spec = FAMILIES["c"]
        candidate = synthetic_candidate(0, spec)
        baseline = synthetic_case(0)
        pins = synthetic_pins(spec)
        for field, value in (
            ("candidate_origin_verified", 1),
            ("candidate_import_count", True),
            ("original_matcher_calls", False),
            ("external_engine_imports", False),
            ("cross_candidate_imports", False),
            ("foreign_native_loads", False),
            ("candidate_source_sha256", "0" * 64),
            ("candidate_engine_sha256", "0" * 64),
            ("candidate_bridge_sha256", "0" * 64),
            ("candidate_family", "rust"),
            ("candidate_module", "candidates.rust_candidate"),
        ):
            def poison_observation(field: str = field,
                                   value: Any = value) -> None:
                changed = copy.deepcopy(candidate)
                changed[field] = value
                validate_candidate_observation(changed, baseline, spec, pins)

            refuse("actual-candidate-provenance-" + field,
                   poison_observation)
        refuse("reference-bool-is-not-zero-candidate-imports",
               lambda: project_reference({**baseline, "candidate_imports": False}))

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
            ("real-process-system", lambda: os.system("blocked")),
            ("real-process-popen", lambda: os.popen("blocked")),
            ("real-thread", lambda: threading.Thread(target=lambda: None).start()),
            ("real-dynamic-import",
             lambda: importlib.import_module("candidates.vm_candidate")),
            ("real-candidate-import",
             lambda: builtins.__import__("candidates.vm_candidate")),
            ("real-interpreter-import",
             lambda: builtins.__import__("concurrent.interpreters")),
            ("real-parent-interpreter-fromlist",
             lambda: builtins.__import__("concurrent",
                                         fromlist=("interpreters",))),
            ("real-low-level-interpreter",
             lambda: builtins.__import__("_interpreters")),
            ("real-ctypes-import", lambda: builtins.__import__("ctypes")),
            ("real-native-ffi-import", lambda: builtins.__import__("_ctypes")),
            ("real-cffi-import", lambda: builtins.__import__("cffi")),
            ("real-network", lambda: builtins.__import__("socket")),
            ("real-multiprocessing",
             lambda: builtins.__import__("multiprocessing")),
            ("real-activation-import",
             lambda: builtins.__import__(
                 "tools.activate_verified_native_candidate_v1"
             )),
            ("real-legacy-recorder-import",
             lambda: builtins.__import__(
                 "tools.run_owned_candidate_subinterpreters_v1"
             )),
            ("real-audit-hook",
             lambda: sys.addaudithook(lambda event, arguments: None)),
            ("real-locale-change",
             lambda: locale.setlocale(locale.LC_CTYPE, "C")),
            ("real-garbage-collection", lambda: gc.collect()),
            ("real-wall-clock", lambda: time.time()),
            ("real-monotonic-clock", lambda: time.monotonic()),
            ("real-performance-clock", lambda: time.perf_counter()),
        ):
            refuse("source-boundary-" + name, operation)

        for category in ("file_reads", "pipes", "processes", "threads",
                         "candidate_imports", "interpreter_imports",
                         "activation_imports", "legacy_recorder_imports",
                         "native_library_loads", "clock_samples",
                         "network_requests", "locale_changes", "audit_hooks"):
            accept("genuine-source-boundary-covered-" + category,
                   boundary.attempts[category] > 0)

    require(len(positive) >= 400 and len(rejected) >= 450,
            "run all complete genuine source-only and durable-intent controls")
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "source_only": True,
        "accepted_controls": len(positive),
        "rejected_hostile_controls": len(rejected),
        "accepted": positive, "rejected": rejected,
        "historical_v1_recorder_source_sha256": V1_SOURCE_SHA256,
        "corrected_activation_source_sha256": ACTIVATION_SOURCE_SHA256,
        "published_version_two_source_build_family_count": 1,
        "published_version_two_source_build_families": ["c"],
        "actual_activations_completed": 0,
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
        "actual_files_read": 0, "actual_files_written": 0,
        "actual_pipes_opened": 0, "actual_threads_started": 0,
        "actual_audit_hooks_installed": 0, "actual_locale_changes": 0,
        "actual_garbage_collections": 0,
        "network_requests": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "source_only_blocked_attempts": dict(boundary.attempts),
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        selected = parse_arguments(
            list(sys.argv[1:] if arguments is None else arguments)
        )
        if selected["mode"] == "self-test":
            report = self_test()
        elif selected["mode"] == "record-candidate":
            report = run_candidate(selected)
        else:
            report = internal_worker(selected)
        sys.stdout.buffer.write(canonical_line(report))
        sys.stdout.buffer.flush()
        return 0 if report.get("status") == "PASS" else 1
    except (SubinterpreterGateError, OSError, ValueError, TypeError,
            UnicodeError, RecursionError, OverflowError) as error:
        failure = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "actual_candidate_imports": 0,
            "actual_interpreters_created": 0,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        }
        sys.stdout.buffer.write(canonical_line(failure))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
