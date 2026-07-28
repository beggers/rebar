#!/usr/bin/env python3
"""Frozen, genuine, independently owned CPython 3.14 subinterpreter gate.

``--self-test`` is synthetic: it reads no project files, starts no workers,
creates no interpreters, loads no candidates, and never accesses a benchmark.
An actual candidate can run only with separately pinned frozen source, a
published two-phase owned-source build proof, and explicit authorization.
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
SCHEMA = "rebar-owned-candidate-subinterpreters-v1"
PROTOCOL_SCHEMA = "rebar-owned-candidate-subinterpreters-protocol-v1"
RECEIPT_SCHEMA = SCHEMA + "-publication-receipt"
SOURCE_RELATIVE = "tools/run_owned_candidate_subinterpreters_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/candidate-subinterpreters-v1.json"
EXPLANATION_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V1.md"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_INVENTORY_SHA256 = (
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
)
PHASE1_VERIFIER_SHA256 = (
    "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c"
)
CANDIDATE_GATE_SHA256 = (
    "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8"
)
CANDIDATE_PROTOCOL_SHA256 = (
    "7ca70c9d4ae7491ae2b9b9a660c8c72efcee629708103ac7654f31353fa7cd0c"
)
BUILD_SOURCE_SHA256 = (
    "e4cee196fcd6ff0908f46c26ef66363aa059e3003f2e89b302df10f35f9a3afd"
)
BUILD_PROTOCOL_SHA256 = (
    "33c495f6852155130c92af73422b7a6c6aae26b1c7012e65e2ddddab028064a2"
)
BUILD_V2_SOURCE_RELATIVE = "tools/reproduce_phase2_native_builds_v2.py"
BUILD_V2_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md"
BUILD_V2_SOURCE_SHA256 = (
    "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796"
)
BUILD_V2_PROTOCOL_SHA256 = (
    "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603"
)
BUILD_V2_SCHEMA = "rebar-phase2-independent-native-source-build-v2"
BUILD_V2_RECEIPT_SCHEMA = BUILD_V2_SCHEMA + "-durable-publication-receipt"
ACTIVATION_SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v1.py"
ACTIVATION_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V1.md"
ACTIVATION_SCHEMA = "rebar-phase2-verified-native-candidate-activation-v1"
ACTIVATION_RECEIPT_SCHEMA = ACTIVATION_SCHEMA + "-durable-publication-receipt"
ACTIVATION_PREFIX = "/tmp/rebar-phase2-verified-native-activation-v1-"
PINNED_INTERPRETERS = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/concurrent/interpreters/__init__.py"
)
PINNED_INTERPRETERS_SHA256 = (
    "040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249"
)
PUBLISHED_C_BUILD_LABEL = "phase2-v1"
PUBLISHED_C_BUILD_ARCHIVE_SHA256 = (
    "b7844048cde986cae25ec4dafadfbb6dc560f4ea86108b908fe074176423f2e2"
)
PUBLISHED_C_BUILD_RECEIPT_SHA256 = (
    "7736349d1e8dce83e47fdf741a4e34fb313d4d370a11a2d5563dba4468e55002"
)
PUBLISHED_C_BUILD_EXTENSION_SHA256 = (
    "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697"
)
PUBLISHED_C_BUILD_EXTENSION_BYTES = 163136
AUDIT_SOURCE_SHA256 = (
    "f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5"
)
AUDIT_PROTOCOL_SHA256 = (
    "a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292"
)
V5_SOURCE_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
IDENTITY_GUARD_SHA256 = (
    "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267"
)
WARNING_GUARD_SHA256 = (
    "55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2"
)
PRIVATE_GUARD_SOURCES: dict[str, str] = {
    "tools/independent_original_cpython_suite_v5.py": V5_SOURCE_SHA256,
    "tools/independent_original_cpython_suite_v4.py": (
        "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3"
    ),
    "tools/rust_original_cpython_suite_v1.py": (
        "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
    ),
    "tools/rust_original_cpython_suite_v2.py": IDENTITY_GUARD_SHA256,
    "tools/rust_original_cpython_suite_v3.py": WARNING_GUARD_SHA256,
}
REFERENCE_SOURCE_SHA256 = (
    "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8"
)
REFERENCE_PROTOCOL_SHA256 = (
    "8c5caccf077ec38afbad62e282f8e74aa470b5d3616ed0b6aa848dd6d97c0dee"
)
REFERENCE_PROGRAM_SHA256 = (
    "9d136a708a438c1f8060c047d89d415c4854ffaeeee9af2fb2d8619f2f0ed07d"
)
ADAPTED_PROGRAM_SHA256 = (
    "147b09bcda37678b9ac4f2f050a22eb5435c7703cbce33247e9287e62e514f71"
)
ADAPTED_PROGRAM_BYTES = 12759
MATRIX_SHA256 = "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3"
REFERENCE_RECORDS_SHA256 = (
    "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8"
)
PROJECTED_REFERENCE_SHA256 = (
    "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"
)
REFERENCE_ARCHIVE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-subinterpreter-v2-self-oracle.json.gz"
)
REFERENCE_ARCHIVE_SHA256 = (
    "62a32bb04b69d517f2838dad9687014cce93c3734e2f45c6865e68f47101459b"
)
REFERENCE_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-subinterpreter-v2-self-oracle-publication-receipt.json"
)
REFERENCE_RECEIPT_SHA256 = (
    "4bd5768de68aeadfa6a1c4936bc9a6464c4245a573f5abc88029f9893389a24c"
)
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
CASE_COUNT = 128
FRESH_CASE_COUNT = 8
CASE_EXEC_COUNT = 394
INTERPRETER_COUNT = 11
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_PIPE_BYTES = 256 * 1024
MAX_LABEL_BYTES = 48
PROCESS_TIMEOUT_SECONDS = 180
PROCESS_CLEANUP_SECONDS = 15
RENAME_FIELDS: dict[str, str] = {
    "actual_stdlib_reimport": "actual_engine_reimport",
    "match_is_stdlib_match": "match_is_engine_match",
    "module_identity": "engine_sysmodules_identity_verified",
    "pattern_is_stdlib_pattern": "pattern_is_engine_pattern",
    "reimported_origin_verified": "engine_reimported_origin_verified",
    "stdlib_owner": "engine_sysmodules_owner_verified",
    "stdlib_re_module": "engine_module_name_verified",
}
REFERENCE_ONLY_FIELDS = frozenset({
    "candidate_imports", "stdlib_origin_verified",
})
REQUIRED_CASE_FIELDS = frozenset({
    "actual_exec", "case_id", "cohort", "locale_unchanged", "observation",
    "ordinal", "pinned_executable_verified", "seed", "status", "variant",
})
REQUIRED_CANDIDATE_FIELDS = frozenset({
    "candidate_family", "candidate_module", "candidate_source_sha256",
    "candidate_engine_sha256", "candidate_bridge_sha256",
    "candidate_origin_verified", "candidate_import_count",
    "original_matcher_calls", "external_engine_imports",
    "cross_candidate_imports", "foreign_native_loads",
})


class SubinterpreterGateError(Exception):
    """The actual independently owned interpreter gate cannot be proven."""


class SourceOnlyViolation(SubinterpreterGateError):
    """A synthetic control tried to perform a real-world action."""


class ActualCaseFailure(SubinterpreterGateError):
    """Retain the full actual pipe, descriptor, and interpreter failure."""

    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    audit_name: str
    adapter_module: str
    adapter_relative: str
    bridge_module: str
    engine_relative: str
    bridge_relative: str
    source_owners: tuple[str, ...]


FAMILIES: dict[str, FamilySpec] = {
    "rust": FamilySpec(
        "rust", "rust", "candidates.rust_candidate",
        "candidates/rust_candidate.py", "candidates._rust_bridge",
        "candidates/_rust_engine.so",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
    ),
    "c": FamilySpec(
        "c", "c_vm", "candidates.vm_candidate",
        "candidates/vm_candidate.py", "candidates._vm_native",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    ),
    "zig": FamilySpec(
        "zig", "zig", "candidates.zig_candidate",
        "candidates/zig_candidate.py", "candidates._zig_bridge",
        "candidates/_zig_probe.so",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
    ),
}


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise SubinterpreterGateError(message)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact in-memory bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require an exact lowercase SHA-256 for " + label,
    )
    return value


def checked_family(name: Any) -> FamilySpec:
    require(type(name) is str and name in FAMILIES,
            "select exactly one independently implemented Rust, C, or Zig engine")
    result = FAMILIES[name]
    require(result.name == name and result.audit_name in {"rust", "c_vm", "zig"}
            and (result.engine_relative == result.bridge_relative) is (name == "c")
            and len(result.source_owners) == {"rust": 9, "c": 2, "zig": 3}[name]
            and result.adapter_relative in result.source_owners,
            "the independently owned frozen engine family was substituted")
    return result


def checked_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= MAX_LABEL_BYTES
            and value.isascii()
            and all(character in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for character in value)
            and not value.startswith("-") and not value.endswith("-")
            and "--" not in value,
            "use a bounded, exact, non-traversing lowercase evidence label")
    return value


def _walk_json(value: Any, *, depth: int = 0,
               state: list[int] | None = None) -> None:
    require(depth <= 48, "a canonical document exceeded its nesting bound")
    if state is None:
        state = [0]
    state[0] += 1
    require(state[0] <= 1_000_000, "a canonical document exceeded its item bound")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        require(abs(value) <= (1 << 256), "a canonical integer exceeded its bound")
        return
    if type(value) is str:
        require(not any(0xD800 <= ord(item) <= 0xDFFF for item in value),
                "a canonical JSON string contained a surrogate")
        return
    if type(value) is float:
        require(value == value and abs(value) != float("inf"),
                "a canonical JSON number was nonfinite")
        return
    if type(value) is list:
        for item in value:
            _walk_json(item, depth=depth + 1, state=state)
        return
    if type(value) is dict:
        for key, item in value.items():
            require(type(key) is str, "canonical JSON object keys must be strings")
            _walk_json(key, depth=depth + 1, state=state)
            _walk_json(item, depth=depth + 1, state=state)
        return
    raise SubinterpreterGateError("reject an unsupported canonical JSON value")


def canonical(value: Any) -> bytes:
    """The frozen subinterpreter producer digest has NO trailing newline."""
    _walk_json(value)
    try:
        return json.dumps(
            value, ensure_ascii=True, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise SubinterpreterGateError("reject noncanonical JSON") from error


def canonical_line(value: Any) -> bytes:
    return canonical(value) + b"\n"


def digest(value: Any) -> str:
    return sha256(canonical(value))


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicate or forged canonical JSON object keys")
        result[key] = value
    return result


def _nonfinite(value: str) -> Any:
    raise SubinterpreterGateError("reject the nonfinite JSON number " + value)


def decode_document(raw: Any, label: str, *, newline: bool) -> Any:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "require complete bounded bytes for " + label)
    try:
        decoded = raw.decode("utf-8", "strict")
        value = json.loads(decoded, object_pairs_hook=_unique_pairs,
                           parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError,
            OverflowError) as error:
        raise SubinterpreterGateError("reject an invalid complete " + label) from error
    expected = canonical_line(value) if newline else canonical(value)
    require(raw == expected,
            "reject changed whitespace, suffixes, or incomplete " + label)
    return value


def synthetic_protocol() -> dict[str, Any]:
    """Build the complete public protocol without reading a project file."""
    return {
        "schema": PROTOCOL_SCHEMA, "version": 1, "phase": "CANDIDATES",
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
        "phase1": {
            "inventory_path": "oracle/phase1/p0-completeness-v1.json",
            "inventory_sha256": PHASE1_INVENTORY_SHA256,
            "verifier_path": "tools/verify_p0_completeness_v1.py",
            "verifier_sha256": PHASE1_VERIFIER_SHA256,
            "full_suite_count": 13, "full_case_execution_denominator": 31237,
        },
        "candidate_gate": {
            "source_path": "tools/run_frozen_p0_candidate_v1.py",
            "source_sha256": CANDIDATE_GATE_SHA256,
            "inventory_path": "oracle/phase2/p0-candidate-protocol-v1.json",
            "inventory_sha256": CANDIDATE_PROTOCOL_SHA256,
        },
        "source_build": {
            "source_path": "tools/reproduce_phase2_native_builds_v1.py",
            "source_sha256": BUILD_SOURCE_SHA256,
            "protocol_path": "oracle/phase2/NATIVE-SOURCE-BUILDS-V1.md",
            "protocol_sha256": BUILD_PROTOCOL_SHA256,
            "actual_published_selected_family_build_required": True,
            "preexisting_native_binary_is_source_build_proof": False,
            "candidate_authorization": {
                "required_protocol_version": 2,
                "status": "V2_PUBLISHED_NO_FAMILY_BUILDS",
                "source_path": BUILD_V2_SOURCE_RELATIVE,
                "source_sha256": BUILD_V2_SOURCE_SHA256,
                "protocol_path": BUILD_V2_PROTOCOL_RELATIVE,
                "protocol_sha256": BUILD_V2_PROTOCOL_SHA256,
                "report_schema": BUILD_V2_SCHEMA,
                "receipt_schema": BUILD_V2_RECEIPT_SCHEMA,
                "future_digest_policy": (
                    "mandatory-exact-caller-pinned-published-source-"
                    "protocol-archive-and-receipt"
                ),
                "version_1_can_authorize_candidate": False,
                "actual_native_must_match_both_fresh_v2_outputs": True,
                "versioned_undefined_regex_symbol_audit_required": True,
            },
            "published_before_controller_freeze": {
                "completed_family_count": 1,
                "c": {
                    "status": "PASS", "family": "c",
                    "label": PUBLISHED_C_BUILD_LABEL,
                    "archive_path": EVIDENCE_RELATIVE + (
                        "/native-source-build-v1-c-phase2-v1.json.gz"
                    ),
                    "archive_sha256": PUBLISHED_C_BUILD_ARCHIVE_SHA256,
                    "receipt_path": EVIDENCE_RELATIVE + (
                        "/native-source-build-v1-c-phase2-v1-"
                        "publication-receipt.json"
                    ),
                    "receipt_sha256": PUBLISHED_C_BUILD_RECEIPT_SHA256,
                    "fresh_extension_sha256": PUBLISHED_C_BUILD_EXTENSION_SHA256,
                    "fresh_extension_bytes": PUBLISHED_C_BUILD_EXTENSION_BYTES,
                    "independent_fresh_phase_count": 2,
                    "byte_identical": True,
                    "candidate_processes_started": 0,
                    "candidate_imports": 0,
                    "native_libraries_loaded": 0,
                },
                "rust": "NOT RUN", "zig": "NOT RUN",
            },
        },
        "canonical_activation": {
            "status": "REQUIRED_NOT_PUBLISHED",
            "source_path": ACTIVATION_SOURCE_RELATIVE,
            "protocol_path": ACTIVATION_PROTOCOL_RELATIVE,
            "report_schema": ACTIVATION_SCHEMA,
            "receipt_schema": ACTIVATION_RECEIPT_SCHEMA,
            "backup_root_prefix": ACTIVATION_PREFIX,
            "backup_root_mode": "0700",
            "source_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "protocol_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "report_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "receipt_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "exact_v2_source_build_required": True,
            "preexisting_repo_native_binary_authorizes_candidate": False,
            "verified_transactionally_activated_repo_binary_required": True,
            "frozen_guard_root_mutation_allowed": False,
            "complete_reversible_native_backup_required": True,
            "transactional_rollback_required": True,
            "canonical_frozen_guard_source_sha256": dict(PRIVATE_GUARD_SOURCES),
        },
        "independence_audit": {
            "source_path": "tools/audit_candidate_independence_v1.py",
            "source_sha256": AUDIT_SOURCE_SHA256,
            "protocol_path": "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md",
            "protocol_sha256": AUDIT_PROTOCOL_SHA256,
            "runtime_no_delegation_proved_by_static_audit": False,
            "persistent_per_interpreter_v5_guard_required": True,
        },
        "original_guard": {
            "source_path": "tools/independent_original_cpython_suite_v5.py",
            "source_sha256": V5_SOURCE_SHA256,
            "identity_guard_path": "tools/rust_original_cpython_suite_v2.py",
            "identity_guard_sha256": IDENTITY_GUARD_SHA256,
            "warning_guard_path": "tools/rust_original_cpython_suite_v3.py",
            "warning_guard_sha256": WARNING_GUARD_SHA256,
            "persistent_guard_per_interpreter": True,
            "public_re_alias_is_authenticated_own_candidate_only": True,
            "public_re_alias_is_original_stdlib": False,
        },
        "reference": {
            "source_path": "tools/python_re_subinterpreter_oracle_v2.py",
            "source_sha256": REFERENCE_SOURCE_SHA256,
            "protocol_path": "oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V2.md",
            "protocol_sha256": REFERENCE_PROTOCOL_SHA256,
            "producer_program_bytes": 11378,
            "producer_program_sha256": REFERENCE_PROGRAM_SHA256,
            "adapted_program_bytes": ADAPTED_PROGRAM_BYTES,
            "adapted_program_sha256": ADAPTED_PROGRAM_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "reference_records_sha256": REFERENCE_RECORDS_SHA256,
            "projected_reference_records_sha256": PROJECTED_REFERENCE_SHA256,
            "case_count": CASE_COUNT, "cohort_count": 16,
            "cases_per_cohort": 8, "independent_reference_roles": 2,
            "reference_process_ids": (
                "actual independently validated archive values; not hardcoded"
            ),
        },
        "identity_projection": {
            "name": "explicit-lossless-reference-only-owner-identity-v1",
            "projected_reference_only_top_level_fields": [
                "candidate_imports", "stdlib_origin_verified",
            ],
            "lossless_observation_field_renames": dict(RENAME_FIELDS),
            "semantic_fields_dropped": 0,
            "canonical_json_has_trailing_newline": False,
        },
        "lifecycle": {
            "actual_case_execution_count": CASE_COUNT,
            "actual_a_observations": CASE_COUNT,
            "actual_b_observations": CASE_COUNT,
            "actual_repeated_a_observations": CASE_COUNT,
            "actual_fresh_interpreter_case_observations": FRESH_CASE_COUNT,
            "actual_a_after_b_close_observations": 1,
            "actual_fresh_c_observations": 1,
            "actual_case_interpreter_exec_calls": CASE_EXEC_COUNT,
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
        "family_audit_names": {"rust": "rust", "c": "c_vm", "zig": "zig"},
        "evidence": {
            "directory": EVIDENCE_RELATIVE,
            "pass_archive_template": (
                "owned-candidate-subinterpreters-v1-FAMILY-LABEL.json.gz"
            ),
            "pass_receipt_template": (
                "owned-candidate-subinterpreters-v1-FAMILY-LABEL-"
                "publication-receipt.json"
            ),
            "failure_archive_template": (
                "owned-candidate-subinterpreters-v1-FAMILY-LABEL-failures.json.gz"
            ),
            "failure_receipt_template": (
                "owned-candidate-subinterpreters-v1-FAMILY-LABEL-failures-"
                "publication-receipt.json"
            ),
            "deterministic_gzip_mtime": 0, "exclusive_no_overwrite": True,
            "no_follow": True, "same_inode_readback_verified": True,
            "file_fsync_required": True, "directory_fsync_required": True,
            "complete_failures_preserved": True,
        },
        "boundaries": {
            "actual_candidate_workers_before_publication": 0,
            "actual_completed_source_builds_before_publication": 1,
            "actual_source_builds_started_by_self_test": 0,
            "candidate_results": "NOT MEASURED", "hidden_cases_read": 0,
            "benchmark_files_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "performance": "NOT MEASURED",
            "final_holdout_authorized": False, "final_holdout_opened": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        },
    }


def validate_protocol_document(document: Any) -> dict[str, Any]:
    require(type(document) is dict
            and canonical(document) == canonical(synthetic_protocol()),
            "the complete frozen owned-subinterpreter protocol was substituted")
    return document


def project_reference_record(record: Any) -> dict[str, Any]:
    require(type(record) is dict
            and set(record) == REQUIRED_CASE_FIELDS | REFERENCE_ONLY_FIELDS
            and type(record.get("candidate_imports")) is int
            and record.get("candidate_imports") == 0
            and record.get("stdlib_origin_verified") is True
            and record.get("actual_exec") is True
            and record.get("locale_unchanged") is True
            and record.get("pinned_executable_verified") is True
            and record.get("status") == "PASS"
            and type(record.get("observation")) is dict,
            "retain every original frozen genuine subinterpreter observation")
    result = {
        key: value for key, value in record.items()
        if key not in REFERENCE_ONLY_FIELDS
    }
    observation = dict(record["observation"])
    for original, replacement in RENAME_FIELDS.items():
        if original in observation:
            require(replacement not in observation,
                    "reject collided candidate observation owner identity")
            observation[replacement] = observation.pop(original)
    require(set(RENAME_FIELDS.values()).isdisjoint(set(RENAME_FIELDS)),
            "the exact seven-field identity projection must be injective")
    result["observation"] = observation
    require(set(result) == REQUIRED_CASE_FIELDS,
            "a genuine semantic case field was dropped")
    return result


def validate_case_record(record: Any, baseline: Any, spec: FamilySpec,
                         pins: Mapping[str, str]) -> dict[str, Any]:
    require(type(record) is dict
            and set(record) == REQUIRED_CASE_FIELDS | REQUIRED_CANDIDATE_FIELDS,
            "retain the exact complete in-interpreter candidate observation")
    require(record.get("candidate_family") == spec.name
            and record.get("candidate_module") == spec.adapter_module
            and record.get("candidate_origin_verified") is True
            and type(record.get("candidate_import_count")) is int
            and record["candidate_import_count"] >= 1,
            "the genuinely imported selected native candidate was substituted")
    for field, pin in (
        ("candidate_source_sha256", "source"),
        ("candidate_engine_sha256", "native_engine"),
        ("candidate_bridge_sha256", "native_bridge"),
    ):
        require(record.get(field) == checked_digest(pins.get(pin), pin),
                "the selected candidate's authenticated native owner changed")
    require((record["candidate_engine_sha256"]
             == record["candidate_bridge_sha256"]) is (spec.name == "c"),
            "only the actual C engine and Python bridge may be the same binary")
    require(all(type(record.get(name)) is int and record.get(name) == 0 for name in (
        "original_matcher_calls", "external_engine_imports",
        "cross_candidate_imports", "foreign_native_loads",
    )), "the original Python matcher or a foreign regex engine escaped")
    actual = {name: record[name] for name in REQUIRED_CASE_FIELDS}
    require(canonical(actual) == canonical(project_reference_record(baseline)),
            "an actual owned-engine case differs from the full frozen Python case")
    return actual


def parse_arguments(arguments: list[str]) -> dict[str, Any]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require exact explicit frozen-owned-subinterpreter arguments")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(arguments and arguments[0] in {
        "--record-candidate", "--internal-worker",
    }, "choose the source-only test or explicitly pin one actual candidate")
    result: dict[str, Any] = {
        "mode": arguments[0][2:], "owned_source_sha256": [],
    }
    options = {
        "--family": "family", "--label": "label",
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--explanation-sha256": "explanation_sha256",
        "--build-label": "build_label",
        "--build-archive-sha256": "build_archive_sha256",
        "--build-receipt-sha256": "build_receipt_sha256",
        "--build-source-sha256": "build_source_sha256",
        "--build-protocol-sha256": "build_protocol_sha256",
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
                "a frozen candidate authorization is missing its exact value")
        option, value = arguments[position], arguments[position + 1]
        if option == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
        else:
            require(option in options,
                    "reject hidden, abbreviated, benchmark, or holdout options")
            key = options[option]
            require(key not in result,
                    "reject a repeated actual-candidate authorization")
            result[key] = value
        position += 2
    expected = {"mode", "family", "label", "source_sha256",
                "protocol_sha256", "explanation_sha256", "build_label",
                "build_archive_sha256", "build_receipt_sha256",
                "build_source_sha256", "build_protocol_sha256",
                "candidate_source_sha256", "native_engine_sha256",
                "native_bridge_sha256", "activation_root",
                "activation_source_sha256", "activation_protocol_sha256",
                "activation_report_sha256", "activation_receipt_sha256",
                "owned_source_sha256"}
    require(set(result) == expected,
            "pin all three frozen sources and actual build, audit, and owner proofs")
    spec = checked_family(result["family"])
    checked_label(result["label"])
    checked_label(result["build_label"])
    for name in expected - {"mode", "family", "label", "build_label",
                            "activation_root", "owned_source_sha256"}:
        checked_digest(result[name], name)
    require(result["build_source_sha256"] == BUILD_V2_SOURCE_SHA256
            and result["build_protocol_sha256"] == BUILD_V2_PROTOCOL_SHA256,
            "only the published, exact version-2 native source builder is valid")
    validate_activation_root_string(result["activation_root"], spec)
    parse_owned_source_pins(spec, result["owned_source_sha256"])
    pins = candidate_pins(result)
    require((pins["native_engine"] == pins["native_bridge"])
            is (spec.name == "c"),
            "only the selected C family has a combined engine and bridge")
    return result


def parse_owned_source_pins(spec: FamilySpec, values: Any) -> dict[str, str]:
    require(type(values) is list and len(values) == len(spec.source_owners),
            "pin the exact complete independently owned selected source closure")
    result: dict[str, str] = {}
    for value in values:
        require(type(value) is str and value.count("=") == 1,
                "require one relative-owner=sha256 pin per source")
        relative, supplied = value.split("=", 1)
        require(relative in spec.source_owners and relative not in result,
                "reject duplicate, sibling, foreign, or omitted source owners")
        result[relative] = checked_digest(supplied, relative)
    require(set(result) == set(spec.source_owners),
            "authenticate every selected family's actual source owner")
    return result


def candidate_pins(arguments: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source": checked_digest(
            arguments.get("candidate_source_sha256"), "candidate source",
        ),
        "native_engine": checked_digest(
            arguments.get("native_engine_sha256"), "native engine",
        ),
        "native_bridge": checked_digest(
            arguments.get("native_bridge_sha256"), "native bridge",
        ),
    }


def checked_relative(value: Any) -> str:
    require(type(value) is str and value.isascii() and value
            and "\\" not in value and "\x00" not in value
            and not value.startswith("/")
            and all(part not in {"", ".", ".."}
                    for part in value.split("/")),
            "require an exact safe project-owned relative path")
    return value


def authenticate_path(path: Path, expected: str, *, maximum: int,
                      exact_size: int | None = None) -> tuple[bytes, dict[str, Any]]:
    require(isinstance(path, Path) and path.is_absolute(),
            "authenticate one exact absolute regular file")
    checked_digest(expected, str(path))
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "require a genuine bounded authenticated file")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "reject a symlink, stale binary, or incorrect owner size")
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1_048_576))
            require(type(piece) is bytes and bool(piece),
                    "an authenticated source or native artifact was truncated")
            pieces.append(piece)
            remaining -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "an authenticated artifact contained a hidden suffix")
        after = os.fstat(descriptor)
        visible = os.lstat(str(path))
        require(
            stat.S_ISREG(visible.st_mode)
            and (before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns)
            and (visible.st_dev, visible.st_ino, visible.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "an authenticated artifact was redirected or changed during its read",
        )
        raw = b"".join(pieces)
        require(len(raw) == before.st_size and sha256(raw) == expected,
                "the exact caller-pinned source, proof, or native bytes differ")
        return raw, {
            "path": str(path), "sha256": expected, "size_bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
        }
    finally:
        os.close(descriptor)


def read_owned(relative: str, expected: str, *, maximum: int,
               exact_size: int | None = None) -> tuple[bytes, dict[str, Any]]:
    safe = checked_relative(relative)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    )
    regular_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    checked_digest(expected, safe)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "require a bounded exact owned source or evidence")
    opened: list[int] = []
    try:
        parent = os.open(str(ROOT), directory_flags)
        opened.append(parent)
        require(stat.S_ISDIR(os.fstat(parent).st_mode),
                "the project-owned root was replaced")
        parts = safe.split("/")
        for part in parts[:-1]:
            parent = os.open(part, directory_flags, dir_fd=parent)
            opened.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "a project-owned parent was replaced by a symlink")
        descriptor = os.open(parts[-1], regular_flags, dir_fd=parent)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "reject an unsafe, stale, redirected, or oversized owned artifact")
        remaining = before.st_size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(descriptor, min(remaining, 1_048_576))
            require(type(piece) is bytes and bool(piece),
                    "an exact owned artifact was truncated")
            pieces.append(piece)
            remaining -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "an exact owned artifact contained hidden trailing bytes")
        after = os.fstat(descriptor)
        current = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns)
            and (current.st_dev, current.st_ino, current.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "a frozen owned artifact changed during no-follow authentication",
        )
        raw = b"".join(pieces)
        require(len(raw) == before.st_size and sha256(raw) == expected,
                "the exact published owned-source or artifact hash changed")
        return raw, {
            "relative": safe, "path": str(ROOT / safe),
            "sha256": expected, "size_bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def decode_source_json(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "require the complete exact hash-pinned " + label)
    try:
        actual = json.loads(raw.decode("utf-8", "strict"),
                            object_pairs_hook=_unique_pairs,
                            parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError, ValueError,
            RecursionError, OverflowError) as error:
        raise SubinterpreterGateError("reject invalid frozen " + label) from error
    require(type(actual) is dict,
            "a complete frozen protocol must be a JSON object")
    _walk_json(actual)
    return actual


def bounded_gzip(raw: Any, *, label: str) -> bytes:
    require(type(raw) is bytes and 10 <= len(raw) <= MAX_ARCHIVE_BYTES
            and raw[:3] == b"\x1f\x8b\x08"
            and raw[4:8] == b"\x00\x00\x00\x00",
            "require one bounded deterministic zero-time gzip for " + label)
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = decompressor.decompress(raw, MAX_REPORT_BYTES + 1)
        require(len(plain) <= MAX_REPORT_BYTES
                and not decompressor.unconsumed_tail,
                "a frozen report exceeded its uncompressed bound")
        plain += decompressor.flush(MAX_REPORT_BYTES - len(plain) + 1)
    except (zlib.error, ValueError, OverflowError) as error:
        raise SubinterpreterGateError("reject invalid " + label) from error
    require(0 < len(plain) <= MAX_REPORT_BYTES
            and decompressor.eof and not decompressor.unused_data,
            "reject truncated, concatenated, or oversized proof archives")
    require(gzip.compress(plain, compresslevel=9, mtime=0) == raw,
            "reject noncanonical deterministic source-build proof bytes")
    return plain


def validate_clean_elf(value: Any, *, family: str, kind: str) -> dict[str, Any]:
    require(type(value) is dict,
            "require the actual version-aware native ELF symbol audit")
    records = value.get("symbol_records")
    require(type(value.get("symbol_count")) is int
            and type(value.get("versioned_symbol_count")) is int
            and type(records) is list and len(records) == value["symbol_count"]
            and value["symbol_count"] > 0,
            "retain every correctly positioned GNU dynamic-symbol-table record")
    derived_undefined: list[str] = []
    versioned = 0
    for index, row in enumerate(records):
        require(type(row) is dict and type(row.get("index")) is int
                and row["index"] == index
                and type(row.get("section")) is str,
                "reject missing, shifted, duplicate, or reordered ELF symbol rows")
        name = row.get("name")
        raw_name = row.get("raw_name")
        if name is None:
            require(raw_name is None and index == 0,
                    "only the genuine null ELF symbol may omit its name")
            continue
        require(type(name) is str and name.isascii() and name
                and type(raw_name) is str and raw_name.isascii()
                and raw_name.split("@", 1)[0] == name
                and not (name.startswith("(") and name.endswith(")")),
                "a genuine eighth-column versioned ELF name was replaced")
        version = row.get("version")
        if version is not None:
            require(type(version) is str and bool(version) and "@" in raw_name,
                    "a genuine versioned ELF matcher suffix was hidden")
            versioned += 1
        if row["section"] == "UND":
            derived_undefined.append(name)
    require(versioned == value["versioned_symbol_count"],
            "a genuine versioned native symbol was omitted")
    symbols = value.get("undefined")
    require(type(symbols) is list
            and all(type(item) is str and item.isascii() and item
                    for item in symbols)
            and len(symbols) == len(set(symbols))
            and sorted(set(derived_undefined)) == symbols,
            "require complete uniquely identified actual undefined ELF symbols")
    for item in symbols:
        require(not (item.startswith("(") and item.endswith(")")),
                "reject a V1 readelf version-index pseudo-symbol")
        normalized = item.split("@", 1)[0].casefold()
        require(
            normalized not in {
                "regcomp", "regexec", "regerror", "regfree",
                "_sre", "sre_compile", "sre_parse", "sre_constants",
            }
            and not normalized.startswith((
                "pcre", "pcre2", "onig", "hyperscan", "vectorscan",
                "re2_", "google_re2", "rust_regex", "fancy_regex",
            )),
            "reject a genuine versioned original or foreign regex matcher",
        )
    require(type(value.get("external_regex_dependency_count")) is int
            and value.get("external_regex_dependency_count") == 0
            and type(value.get("cross_family_dependency_count")) is int
            and value.get("cross_family_dependency_count") == 0
            and value.get("role") == kind,
            "reject a sibling or external dynamic regex engine")
    return value


def validate_build_v2_document(
    report: Any, receipt: Any, *, archive: bytes,
    archive_evidence: Mapping[str, Any], spec: FamilySpec,
    source_owners: Mapping[str, str], arguments: Mapping[str, Any],
    verifier: types.ModuleType,
) -> dict[str, Any]:
    label = checked_label(arguments.get("build_label"))
    require(type(report) is dict and type(receipt) is dict,
            "require the actual published version-2 report and durable receipt")
    require(report.get("schema") == BUILD_V2_SCHEMA
            and receipt.get("schema") == BUILD_V2_RECEIPT_SCHEMA
            and report.get("status") == "PASS"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and report.get("family") == receipt.get("family") == spec.name
            and report.get("label") == receipt.get("label") == label,
            "a historical V1, failed, sibling, or forged V2 proof is not authority")
    for key, argument in (
        ("source_sha256", "build_source_sha256"),
        ("protocol_sha256", "build_protocol_sha256"),
    ):
        require(report.get(key) == receipt.get(key) == arguments.get(argument),
                "the caller-pinned frozen V2 producer or protocol changed")
    archive_name = "native-source-build-v2-" + spec.name + "-" + label + ".json.gz"
    archive_relative = EVIDENCE_RELATIVE + "/" + archive_name
    plain = canonical_line(report)
    require(receipt.get("archive_relative") == archive_relative
            and receipt.get("archive_sha256") == sha256(archive)
            and receipt.get("archive_bytes") == len(archive)
            and receipt.get("uncompressed_sha256") == sha256(plain)
            and receipt.get("uncompressed_bytes") == len(plain),
            "the independently published V2 archive and full receipt disagree")
    archive_publication = receipt.get("archive_publication")
    require(type(archive_publication) is dict
            and archive_publication.get("sha256") == sha256(archive)
            and archive_publication.get("bytes") == len(archive)
            and archive_publication.get("exclusive_creation") is True
            and archive_publication.get("same_inode_readback_verified") is True
            and archive_publication.get("file_fsync_completed") is True,
            "require genuine exclusive, synchronized V2 archive publication")
    directory_sync = receipt.get("archive_directory_fsync")
    require(type(directory_sync) is dict
            and directory_sync.get("completed") is True
            and type(directory_sync.get("device")) is int
            and type(directory_sync.get("inode")) is int,
            "a V2 publication's genuine directory sync was omitted")
    require(archive_evidence.get("relative") == archive_relative,
            "the V2 archive was redirected")
    require(report.get("owned_source_sha256") == dict(sorted(source_owners.items()))
            and receipt.get("owned_source_sha256")
            == dict(sorted(source_owners.items())),
            "the V2 build did not use the complete actual family source closure")
    for key in ("owned_source_before", "owned_source_after"):
        snapshot = report.get(key)
        require(type(snapshot) is dict and set(snapshot) == set(spec.source_owners),
                "a complete genuinely read V2 source snapshot was omitted")
        for relative in spec.source_owners:
            owner = snapshot[relative]
            require(type(owner) is dict
                    and owner.get("sha256") == source_owners[relative]
                    and owner.get("path") == str(ROOT / relative)
                    and type(owner.get("size_bytes")) is int
                    and owner["size_bytes"] > 0
                    and type(owner.get("device")) is int
                    and type(owner.get("inode")) is int,
                    "a fresh V2 source owner was replaced")
    for owner in (report, receipt):
        for field in ("candidate_processes_started", "candidate_imports",
                      "native_libraries_loaded", "hidden_cases_read",
                      "benchmark_files_read", "clock_samples", "timing_trials_run"):
            require(type(owner.get(field)) is int and owner.get(field) == 0,
                    "a V2 build ran a candidate, read holdout, or measured timing")
        require(owner.get("performance") == "NOT MEASURED",
                "a V2 correctness source build measured performance")
    for field in ("reference_processes_started", "network_requests"):
        require(type(report.get(field)) is int and report.get(field) == 0,
                "a native V2 source build ran a reference or accessed the network")
    audit = report.get("source_independence_audit")
    require(type(audit) is dict
            and type(audit.get("source_owner_count")) is int
            and audit.get("source_owner_count") == len(spec.source_owners)
            and type(audit.get("cross_family_dependency_count")) is int
            and audit.get("cross_family_dependency_count") == 0
            and type(audit.get("external_regex_package_count")) is int
            and audit.get("external_regex_package_count") == 0,
            "the genuine V2 source-closure independence audit is missing")
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and all(type(row) is dict for row in phases)
            and [row.get("name") for row in phases]
            == ["reference-a", "reference-b"],
            "require two actual distinct version-2 source-build phases")
    try:
        verified = verifier.verify_reproducible_phases(spec.name, phases)
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the frozen V2 producer rejected the two actual native phases"
        ) from error
    require(type(verified) is dict
            and canonical(verified) == canonical(report.get("reproducibility"))
            and verified.get("independent_fresh_phase_count") == 2
            and verified.get("byte_identical") is True
            and verified.get("prebuilt_binary_count") == 0
            and verified.get("native_libraries_loaded") == 0,
            "two independently fresh identical V2 native builds are mandatory")
    kinds = {"extension"} if spec.name == "c" else {"engine", "bridge"}
    outputs = verified.get("native_outputs")
    require(type(outputs) is dict and set(outputs) == kinds,
            "a version-2 native engine or Python bridge was omitted")
    for phase in phases:
        require(type(phase) is dict
                and all(type(phase.get(key)) is int and phase.get(key) == 0
                        for key in ("candidate_processes_started",
                                    "candidate_imports", "native_libraries_loaded",
                                    "timing_trials_run", "hidden_cases_read"))
                and type(phase.get("copied_source_owners")) is dict
                and set(phase["copied_source_owners"])
                == set(spec.source_owners)
                and type(phase.get("native_outputs")) is dict
                and set(phase["native_outputs"]) == kinds,
                "a complete genuine V2 phase or its owned source copy is missing")
        for kind in kinds:
            phase_output = phase["native_outputs"][kind]
            shared = outputs[kind]
            require(type(phase_output) is dict and type(shared) is dict
                    and type(phase_output.get("size_bytes")) is int
                    and type(shared.get("size_bytes")) is int
                    and phase_output.get("sha256") == shared.get("sha256")
                    and phase_output.get("size_bytes") == shared.get("size_bytes")
                    and phase_output.get("file_name") == shared.get("file_name")
                    and phase_output.get("elf") == shared.get("elf")
                    and phase_output.get("candidate_imported") is False
                    and phase_output.get("prebuilt_binary_read") is False
                    and shared.get("reproduced_in_two_fresh_directories") is True,
                    "the two complete V2 phase-native owners disagree")
            validate_clean_elf(shared["elf"], family=spec.name, kind=kind)
    pins = candidate_pins(arguments)
    names = {"extension": spec.bridge_relative.rsplit("/", 1)[-1]}
    if spec.name != "c":
        names = {
            "engine": spec.engine_relative.rsplit("/", 1)[-1],
            "bridge": spec.bridge_relative.rsplit("/", 1)[-1],
        }
    native: dict[str, dict[str, Any]] = {}
    for kind in kinds:
        output = outputs[kind]
        require(output.get("file_name") == names[kind],
                "the V2 source build produced a different native family")
        relative = spec.engine_relative if kind in {"engine", "extension"} else spec.bridge_relative
        expected = pins["native_engine"] if kind in {"engine", "extension"} else pins["native_bridge"]
        require(output.get("sha256") == expected,
                "the actual candidate pin is not the genuine fresh V2 output")
        require(type(output.get("size_bytes")) is int
                and 0 < output["size_bytes"] <= MAX_BINARY_BYTES,
                "the exact V2 native output size was omitted")
        native[kind] = {
            "relative": relative, "sha256": expected,
            "size_bytes": output["size_bytes"],
            "file_name": names[kind], "elf": output["elf"],
            "activation": "VERIFIED REVERSIBLE CANONICAL ACTIVATION REQUIRED",
        }
    return {
        "schema": BUILD_V2_SCHEMA, "status": "PASS", "family": spec.name,
        "label": label, "archive_sha256": sha256(archive),
        "receipt_sha256": arguments["build_receipt_sha256"],
        "source_sha256": arguments["build_source_sha256"],
        "protocol_sha256": arguments["build_protocol_sha256"],
        "actual_native_owners": native,
        "independent_fresh_phase_count": 2,
        "versioned_undefined_regex_symbols_verified": True,
    }


def authenticate_prerequisites(arguments: Mapping[str, Any]) -> dict[str, Any]:
    """Fail closed on V2/source/native proof before any interpreter import."""
    spec = checked_family(arguments.get("family"))
    owners = parse_owned_source_pins(spec, arguments.get("owned_source_sha256"))
    pins = candidate_pins(arguments)
    require(owners.get(spec.adapter_relative) == pins["source"],
            "the adapter pin differs from the complete genuine source closure")
    frozen: dict[str, dict[str, Any]] = {}
    for relative, expected in (
        ("GOAL.md", GOAL_SHA256),
        (SOURCE_RELATIVE, arguments["source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["protocol_sha256"]),
        (EXPLANATION_RELATIVE, arguments["explanation_sha256"]),
        ("oracle/phase1/p0-completeness-v1.json", PHASE1_INVENTORY_SHA256),
        ("tools/verify_p0_completeness_v1.py", PHASE1_VERIFIER_SHA256),
        ("tools/run_frozen_p0_candidate_v1.py", CANDIDATE_GATE_SHA256),
        ("oracle/phase2/p0-candidate-protocol-v1.json", CANDIDATE_PROTOCOL_SHA256),
        ("tools/audit_candidate_independence_v1.py", AUDIT_SOURCE_SHA256),
        ("oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md", AUDIT_PROTOCOL_SHA256),
        ("tools/independent_original_cpython_suite_v5.py", V5_SOURCE_SHA256),
        ("tools/rust_original_cpython_suite_v2.py", IDENTITY_GUARD_SHA256),
        ("tools/rust_original_cpython_suite_v3.py", WARNING_GUARD_SHA256),
        ("tools/python_re_subinterpreter_oracle_v2.py", REFERENCE_SOURCE_SHA256),
        ("oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V2.md",
         REFERENCE_PROTOCOL_SHA256),
        (BUILD_V2_SOURCE_RELATIVE, arguments["build_source_sha256"]),
        (BUILD_V2_PROTOCOL_RELATIVE, arguments["build_protocol_sha256"]),
        (ACTIVATION_SOURCE_RELATIVE, arguments["activation_source_sha256"]),
        (ACTIVATION_PROTOCOL_RELATIVE, arguments["activation_protocol_sha256"]),
    ):
        raw, evidence = read_owned(relative, expected, maximum=MAX_SOURCE_BYTES)
        frozen[relative] = evidence
        if relative == PROTOCOL_RELATIVE:
            validate_protocol_document(decode_source_json(raw, "pretty frozen protocol"))
    for relative, expected in sorted(owners.items()):
        _, evidence = read_owned(relative, expected, maximum=MAX_SOURCE_BYTES)
        frozen[relative] = evidence
    require(sys.executable == PINNED_PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "run only isolated pinned stable CPython 3.14.6 without bytecode")
    _, python_owner = authenticate_path(
        Path(PINNED_PYTHON), PINNED_PYTHON_SHA256,
        maximum=MAX_BINARY_BYTES,
    )
    label = checked_label(arguments["build_label"])
    base = EVIDENCE_RELATIVE + "/native-source-build-v2-" + spec.name + "-" + label
    archive_raw, archive_owner = read_owned(
        base + ".json.gz", arguments["build_archive_sha256"],
        maximum=MAX_ARCHIVE_BYTES,
    )
    receipt_raw, receipt_owner = read_owned(
        base + "-publication-receipt.json", arguments["build_receipt_sha256"],
        maximum=MAX_SOURCE_BYTES,
    )
    report = decode_document(
        bounded_gzip(archive_raw, label="genuine version-2 source-build proof"),
        "canonical version-2 source-build report", newline=True,
    )
    receipt = decode_document(
        receipt_raw, "canonical version-2 durable publication receipt", newline=True,
    )
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    verifier = importlib.import_module("tools.reproduce_phase2_native_builds_v2")
    require(type(verifier) is types.ModuleType
            and verifier.__name__ == "tools.reproduce_phase2_native_builds_v2"
            and os.path.abspath(verifier.__file__) == str(ROOT / BUILD_V2_SOURCE_RELATIVE)
            and getattr(verifier, "SCHEMA", None) == BUILD_V2_SCHEMA
            and getattr(verifier, "RECEIPT_SCHEMA", None) == BUILD_V2_RECEIPT_SCHEMA,
            "load only the exact source-authenticated frozen V2 producer")
    build = validate_build_v2_document(
        report, receipt, archive=archive_raw, archive_evidence=archive_owner,
        spec=spec, source_owners=owners, arguments=arguments, verifier=verifier,
    )
    require(receipt_owner["sha256"] == arguments["build_receipt_sha256"],
            "the exact V2 receipt bytes changed during authentication")
    activation = authenticate_canonical_activation(arguments, spec, owners, build)
    return {
        "spec": spec, "pins": pins, "source_owners": owners,
        "frozen_sources": frozen, "pinned_python": python_owner,
        "source_build_v2": build, "canonical_activation": activation,
    }


def validate_activation_root_string(value: Any, spec: FamilySpec) -> str:
    require(type(value) is str and value.isascii()
            and value.startswith(ACTIVATION_PREFIX + spec.name + "-")
            and value.count("/") == 2
            and "\\" not in value and "\x00" not in value
            and value == os.path.normpath(value)
            and 1 <= len(value) <= 240,
            "require the exact selected private, direct /tmp activation root")
    return value


def read_private_owned(
    root: str, relative: str, expected: str, *, maximum: int,
    exact_size: int | None = None,
) -> tuple[bytes, dict[str, Any]]:
    safe = checked_relative(relative)
    checked_digest(expected, safe)
    directory_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_NOFOLLOW", 0)
                       | getattr(os, "O_DIRECTORY", 0))
    regular_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                     | getattr(os, "O_NOFOLLOW", 0))
    opened: list[int] = []
    try:
        current = os.open(root, directory_flags)
        opened.append(current)
        root_stat = os.fstat(current)
        visible_root = os.lstat(root)
        require(stat.S_ISDIR(root_stat.st_mode)
                and (root_stat.st_mode & 0o777) == 0o700
                and root_stat.st_uid == os.geteuid()
                and (visible_root.st_dev, visible_root.st_ino)
                == (root_stat.st_dev, root_stat.st_ino),
                "reject a nonprivate, replaced, or symlinked activation root")
        parts = safe.split("/")
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a private activation parent is not a real owned directory")
        descriptor = os.open(parts[-1], regular_flags, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "a private activation source or native binary was substituted")
        remaining = before.st_size
        parts_read: list[bytes] = []
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "a private activation artifact was truncated")
            parts_read.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "a private activation artifact contains concealed bytes")
        after = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns)
            and (visible.st_dev, visible.st_ino, visible.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "a private verified artifact changed during authentication",
        )
        raw = b"".join(parts_read)
        require(len(raw) == after.st_size and sha256(raw) == expected,
                "the actual private activation bytes differ from their proof")
        return raw, {
            "relative": safe, "path": root + "/" + safe,
            "sha256": expected, "size_bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def authenticate_canonical_activation(
    arguments: Mapping[str, Any], spec: FamilySpec,
    owners: Mapping[str, str], build: Mapping[str, Any],
) -> dict[str, Any]:
    root = validate_activation_root_string(arguments.get("activation_root"), spec)
    report_raw, report_identity = read_private_owned(
        root, "activation-report.json", arguments["activation_report_sha256"],
        maximum=MAX_SOURCE_BYTES,
    )
    receipt_raw, receipt_identity = read_private_owned(
        root, "activation-receipt.json", arguments["activation_receipt_sha256"],
        maximum=MAX_SOURCE_BYTES,
    )
    report = decode_document(report_raw, "actual canonical activation report",
                             newline=True)
    receipt = decode_document(receipt_raw, "actual canonical activation receipt",
                              newline=True)
    require(type(report) is dict and type(receipt) is dict
            and report.get("schema") == ACTIVATION_SCHEMA
            and receipt.get("schema") == ACTIVATION_RECEIPT_SCHEMA
            and report.get("status") == "PASS"
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and report.get("promotion_mode") == "recoverable-canonical-promotion"
            and receipt.get("promotion_mode") == "recoverable-canonical-promotion"
            and report.get("family") == receipt.get("family") == spec.name
            and report.get("activation_root") == root
            and receipt.get("activation_root") == root
            and report.get("candidate_import_root") == str(ROOT)
            and receipt.get("candidate_import_root") == str(ROOT),
            "reject noncanonical, unverified, sibling, V1, or irreversible activation")
    for key, option in (
        ("activation_source_sha256", "activation_source_sha256"),
        ("activation_protocol_sha256", "activation_protocol_sha256"),
    ):
        require(report.get(key) == receipt.get(key) == arguments[option],
                "the exact isolated activation source or protocol differs")
    provenance = report.get("source_build_v2")
    require(type(provenance) is dict and provenance.get("schema") == BUILD_V2_SCHEMA
            and provenance.get("family") == spec.name
            and provenance.get("source_sha256") == arguments["build_source_sha256"]
            and provenance.get("protocol_sha256") == arguments["build_protocol_sha256"]
            and provenance.get("archive_sha256") == arguments["build_archive_sha256"]
            and provenance.get("receipt_sha256") == arguments["build_receipt_sha256"]
            and provenance.get("independent_fresh_phase_count") == 2,
            "canonical native promotion is not from the exact proved V2 build")
    require(canonical(report.get("owned_source_sha256"))
            == canonical(dict(sorted(owners.items()))),
            "canonical activation substituted the selected complete source closure")
    canonical_sources: dict[str, dict[str, Any]] = {}
    reported_sources = report.get("source_owners")
    require(type(reported_sources) is dict
            and set(reported_sources) == set(owners),
            "retain every actual canonical candidate source owner")
    for relative, expected in sorted(owners.items()):
        _, actual = read_owned(relative, expected, maximum=MAX_SOURCE_BYTES)
        announced = reported_sources[relative]
        require(type(announced) is dict
                and all(announced.get(key) == actual.get(key)
                        for key in ("relative", "path", "sha256", "size_bytes",
                                    "device", "inode")),
                "a canonical source owner changed after reversible activation")
        canonical_sources[relative] = actual
    reported_guards = report.get("original_guard_sources")
    require(type(reported_guards) is dict
            and set(reported_guards) == set(PRIVATE_GUARD_SOURCES),
            "authenticate every unchanged original canonical matcher guard")
    canonical_guards: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(PRIVATE_GUARD_SOURCES.items()):
        _, actual = read_owned(relative, expected, maximum=MAX_SOURCE_BYTES)
        announced = reported_guards[relative]
        require(type(announced) is dict and announced.get("sha256") == expected
                and announced.get("path") == str(ROOT / relative)
                and announced.get("size_bytes") == actual["size_bytes"]
                and announced.get("device") == actual["device"]
                and announced.get("inode") == actual["inode"],
                "an unchanged canonical original V5/warning guard was replaced")
        canonical_guards[relative] = actual
    adapter = report.get("adapter")
    actual_adapter = canonical_sources[spec.adapter_relative]
    require(type(adapter) is dict and adapter.get("module") == spec.adapter_module
            and adapter.get("relative") == spec.adapter_relative
            and all(adapter.get(name) == actual_adapter.get(name)
                    for name in ("path", "sha256", "size_bytes", "device", "inode")),
            "the actual canonical candidate adapter is not the V2-owned source")
    reported_native = report.get("canonical_targets")
    announced_native = build.get("actual_native_owners")
    require(type(reported_native) is dict and type(announced_native) is dict
            and set(reported_native) == set(announced_native),
            "a canonically promoted V2 native engine or bridge was omitted")
    canonical_native: dict[str, dict[str, Any]] = {}
    for kind, proof in announced_native.items():
        claimed = reported_native[kind]
        require(type(claimed) is dict,
                "an actual canonical native provenance was replaced")
        _, actual = read_owned(
            proof["relative"], proof["sha256"],
            maximum=MAX_BINARY_BYTES, exact_size=proof["size_bytes"],
        )
        require(claimed.get("relative") == proof["relative"]
                and claimed.get("role") == kind
                and claimed.get("elf") == proof["elf"]
                and claimed.get("atomic_replace_completed") is True
                and claimed.get("adjacent_exclusive_stage_verified") is True
                and claimed.get("candidate_directory_fsync_completed") is True
                and all(claimed.get(name) == actual.get(name)
                        for name in ("path", "sha256", "size_bytes",
                                     "device", "inode")),
                "the canonical native bytes do not equal both actual V2 builds")
        validate_clean_elf(claimed["elf"], family=spec.name, kind=kind)
        source_phases = claimed.get("source_build_phases")
        require(type(source_phases) is list and len(source_phases) == 2,
                "retain both independently fresh canonical source-build phases")
        canonical_native[kind] = actual
    entries = report.get("backup_entries")
    require(type(entries) is dict and set(entries) == set(announced_native)
            and canonical(entries) == canonical(receipt.get("backup_entries")),
            "retain every exact reversible canonical native backup entry")
    for kind, entry in entries.items():
        proof = announced_native[kind]
        require(type(entry) is dict and entry.get("role") == kind
                and entry.get("target_relative") == proof["relative"]
                and entry.get("target_path") == str(ROOT / proof["relative"])
                and entry.get("promoted_sha256") == proof["sha256"]
                and entry.get("promoted_size_bytes") == proof["size_bytes"]
                and type(entry.get("originally_present")) is bool,
                "a recoverable canonical activation target was substituted")
        if entry["originally_present"]:
            previous = entry.get("original_owner")
            backup = entry.get("backup")
            require(type(previous) is dict and type(backup) is dict
                    and backup.get("exclusive_creation") is True
                    and backup.get("same_inode_readback_verified") is True
                    and backup.get("file_fsync_completed") is True
                    and previous.get("sha256") == backup.get("sha256")
                    and previous.get("size_bytes") == backup.get("size_bytes"),
                    "a preexisting binary has no exact recoverable private backup")
            _, actual_backup = read_private_owned(
                root, backup.get("relative"), backup.get("sha256"),
                maximum=MAX_BINARY_BYTES,
                exact_size=backup.get("size_bytes"),
            )
            require(all(backup.get(key) == actual_backup.get(key)
                        for key in ("relative", "path", "sha256", "size_bytes",
                                    "device", "inode")),
                    "a preserved original canonical binary backup changed")
        else:
            require(entry.get("original_owner") is None
                    and entry.get("backup") is None,
                    "an absent original canonical binary backup was forged")
    recovery = report.get("recovery_journal")
    require(type(recovery) is dict
            and canonical(recovery) == canonical(receipt.get("recovery_journal"))
            and recovery.get("relative") == "recovery-journal.json"
            and recovery.get("exclusive_creation") is True
            and recovery.get("same_inode_readback_verified") is True
            and recovery.get("file_fsync_completed") is True
            and recovery.get("directory_fsync_completed") is True,
            "the durable recoverable canonical promotion journal is missing")
    journal_raw, actual_journal = read_private_owned(
        root, recovery["relative"], recovery.get("sha256"),
        maximum=MAX_SOURCE_BYTES, exact_size=recovery.get("size_bytes"),
    )
    require(all(recovery.get(key) == actual_journal.get(key)
                for key in ("relative", "path", "sha256", "size_bytes",
                            "device", "inode")),
            "the durable canonical recovery journal inode was replaced")
    journal = decode_document(journal_raw, "canonical recovery journal",
                              newline=True)
    require(type(journal) is dict
            and journal.get("schema") == ACTIVATION_SCHEMA + "-recovery-journal"
            and journal.get("status") == "PREPARED"
            and journal.get("promotion_mode") == "recoverable-canonical-promotion"
            and journal.get("family") == spec.name
            and journal.get("activation_root") == root
            and journal.get("candidate_import_root") == str(ROOT)
            and canonical(journal.get("backup_entries")) == canonical(entries),
            "the separately durable original-binary recovery state was forged")
    require(receipt.get("report_relative") == "activation-report.json"
            and receipt.get("report_sha256") == sha256(report_raw)
            and receipt.get("report_bytes") == len(report_raw),
            "the canonical activation receipt does not bind its exact report")
    publication = receipt.get("report_publication")
    require(type(publication) is dict
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True
            and all(publication.get(key) == report_identity.get(key)
                    for key in ("path", "sha256", "size_bytes", "device", "inode")),
            "require the complete exclusive, durable canonical activation report")
    report_sync = receipt.get("report_directory_fsync")
    require(type(report_sync) is dict and report_sync.get("completed") is True,
            "the canonical activation report directory was not synchronized")
    require(report.get("performance") == "NOT MEASURED"
            and report.get("candidate_correctness") == "NOT MEASURED"
            and report.get("winner_selected") is False,
            "activation must never run a candidate, benchmark, or choose a winner")
    for key in ("candidate_imports", "candidate_processes_started",
                "native_libraries_loaded", "hidden_cases_read",
                "benchmark_files_read", "clock_samples", "timing_trials_run",
                "reference_processes_started", "network_requests"):
        require(type(report.get(key)) is int and report.get(key) == 0
                and type(receipt.get(key)) is int and receipt.get(key) == 0,
                "canonical activation ran an engine, benchmark, reference, or network")
    return {
        "schema": ACTIVATION_SCHEMA, "status": "PASS", "family": spec.name,
        "backup_root": root, "candidate_import_root": str(ROOT),
        "promotion_mode": "recoverable-canonical-promotion",
        "report": report_identity, "receipt": receipt_identity,
        "recovery_journal": actual_journal, "backup_entries": entries,
        "source_owners": canonical_sources, "guard_owners": canonical_guards,
        "native_owners": canonical_native,
        "candidate_adapter": actual_adapter,
    }


def replace_unique(program: str, original: str, replacement: str,
                   *, count: int = 1) -> str:
    require(type(program) is str and type(original) is str
            and type(replacement) is str and type(count) is int and count > 0
            and original and program.count(original) == count,
            "reject missing, duplicate, or noncontextual original producer edits")
    result = program.replace(original, replacement)
    require(result.count(original) == count * replacement.count(original),
            "an authentic original producer marker escaped transformation")
    return result


def compose_owned_program(
    program: Any, spec: FamilySpec, pins: Mapping[str, str], *,
    expected_source_sha256: str = REFERENCE_PROGRAM_SHA256,
    expected_source_bytes: int = 11378,
) -> dict[str, Any]:
    require(type(program) is str and type(expected_source_bytes) is int,
            "require the exact complete original interpreter program")
    raw = program.encode("utf-8", "strict")
    require(len(raw) == expected_source_bytes
            and sha256(raw) == checked_digest(expected_source_sha256,
                                               "original interpreter program"),
            "never adapt an approximate or altered original Python producer")
    checked_family(spec.name)
    for key in ("source", "native_engine", "native_bridge"):
        checked_digest(pins.get(key), key)
    require((pins["native_engine"] == pins["native_bridge"])
            is (spec.name == "c"),
            "reject substituted or crossed native candidate families")
    result = replace_unique(
        program, "import re as _re\n",
        '_phase2_state = getattr(_builtins, '
        '"_rebar_owned_candidate_subinterpreter_v1", None)\n'
        'if type(_phase2_state) is not dict:\n'
        '    raise AssertionError("missing persistent owned original V5 guard")\n'
        '_phase2_state["verify"]()\n'
        '_re = _phase2_state["candidate"]\n',
    )
    result = replace_unique(
        result,
        '_assert(_re.__spec__ is not None\n'
        '        and _os.path.abspath(_re.__spec__.origin) == _stdlib_re_origin\n'
        '        and _os.path.abspath(_re.__file__) == _stdlib_re_origin,\n'
        '        "the actual pinned standard-library regex module was replaced")',
        '_assert(_re.__spec__ is not None\n'
        '        and _re.__name__ == _candidate_module_name\n'
        '        and _os.path.abspath(_re.__spec__.origin) == _candidate_adapter_origin\n'
        '        and _os.path.abspath(_re.__file__) == _candidate_adapter_origin\n'
        '        and _sys.modules.get(_candidate_module_name) is _re,\n'
        '        "the exact authenticated owned candidate adapter was replaced")',
    )
    result = replace_unique(
        result,
        '_assert(not any(name == "candidates" or name.startswith("candidates.")\n'
        '                for name in _sys.modules), "a production candidate entered the reference")',
        '_assert(all(name in _allowed_candidate_modules\n'
        '            for name in _sys.modules\n'
        '            if name == "candidates" or name.startswith("candidates.")),\n'
        '        "a sibling or external candidate entered the guarded interpreter")',
    )
    replacements = (
        ('"stdlib_re_module": _re.__name__ == "re",',
         '"engine_module_name_verified": '
         '_re.__name__ == _candidate_module_name,'),
        ('"module_identity": _sys.modules["re"] is _re,',
         '"engine_sysmodules_identity_verified": '
         '_sys.modules["re"] is _re\n'
         '        and _sys.modules.get(_candidate_module_name) is _re,'),
        ('"pattern_is_stdlib_pattern":', '"pattern_is_engine_pattern":'),
        ('"match_is_stdlib_match":', '"match_is_engine_match":'),
        ('"actual_stdlib_reimport":', '"actual_engine_reimport":'),
        ('"reimported_origin_verified":',
         '"engine_reimported_origin_verified":'),
        ('_os.path.abspath(_again.__spec__.origin) == _stdlib_re_origin',
         '_os.path.abspath(_again.__spec__.origin) == _candidate_adapter_origin'),
        ('"stdlib_owner": _sys.modules["re"] is _re,',
         '"engine_sysmodules_owner_verified": '
         '_sys.modules["re"] is _re\n'
         '                         and _sys.modules.get(_candidate_module_name) '
         'is _re,'),
    )
    for original, replacement in replacements:
        result = replace_unique(result, original, replacement)
    result = replace_unique(
        result,
        '           "candidate_imports": 0, "locale_unchanged": True,\n'
        '           "stdlib_origin_verified": True, '
        '"pinned_executable_verified": True,\n',
        '           "locale_unchanged": True, '
        '"pinned_executable_verified": True,\n'
        '           "candidate_family": _candidate_family,\n'
        '           "candidate_module": _candidate_module_name,\n'
        '           "candidate_source_sha256": _candidate_source_sha256,\n'
        '           "candidate_engine_sha256": _candidate_engine_sha256,\n'
        '           "candidate_bridge_sha256": _candidate_bridge_sha256,\n'
        '           "candidate_origin_verified": '
        '_phase2_state["candidate_origin_verified"],\n'
        '           "candidate_import_count": '
        '_phase2_state["candidate_import_count"],\n'
        '           "original_matcher_calls": '
        '_phase2_state["original_matcher_calls"],\n'
        '           "external_engine_imports": '
        '_phase2_state["external_engine_imports"],\n'
        '           "cross_candidate_imports": '
        '_phase2_state["cross_candidate_imports"],\n'
        '           "foreign_native_loads": '
        '_phase2_state["foreign_native_loads"],\n',
    )
    result = replace_unique(
        result,
        '_record = {"case_id": _case["case_id"], "cohort": _cohort,\n',
        '_phase2_state["verify"]()\n'
        '_record = {"case_id": _case["case_id"], "cohort": _cohort,\n',
    )
    try:
        ast.parse(result, filename="<actual-frozen-owned-subinterpreter-v1>",
                  mode="exec")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise SubinterpreterGateError(
            "the losslessly adapted real original interpreter program is invalid"
        ) from error
    for original in RENAME_FIELDS:
        require(('"' + original + '":') not in result,
                "an unmapped original-owner identity escaped the candidate program")
    require(result.count('_phase2_state["verify"]()') == 2
            and '"candidate_imports": 0' not in result
            and '"stdlib_origin_verified": True' not in result,
            "continuous original V5 verification or actual candidate proof was lost")
    encoded = result.encode("utf-8", "strict")
    if expected_source_sha256 == REFERENCE_PROGRAM_SHA256:
        require(len(encoded) == ADAPTED_PROGRAM_BYTES
                and sha256(encoded) == ADAPTED_PROGRAM_SHA256,
                "the exact independently frozen adapted interpreter program changed")
    return {
        "source": result, "sha256": sha256(encoded), "bytes": len(encoded),
        "original_sha256": expected_source_sha256,
        "original_bytes": expected_source_bytes,
        "lossless_observation_field_renames": dict(RENAME_FIELDS),
    }


def load_original_baseline() -> dict[str, Any]:
    """Read the existing original evidence; never rerun a reference worker."""
    archive, _ = read_owned(
        REFERENCE_ARCHIVE_RELATIVE, REFERENCE_ARCHIVE_SHA256,
        maximum=MAX_ARCHIVE_BYTES,
    )
    receipt_bytes, _ = read_owned(
        REFERENCE_RECEIPT_RELATIVE, REFERENCE_RECEIPT_SHA256,
        maximum=MAX_SOURCE_BYTES,
    )
    report = decode_document(
        bounded_gzip(archive, label="complete original subinterpreter evidence"),
        "original reference archive", newline=True,
    )
    receipt = decode_document(
        receipt_bytes, "original reference publication receipt", newline=True,
    )
    source = importlib.import_module("tools.python_re_subinterpreter_oracle_v2")
    gate = importlib.import_module("tools.run_frozen_p0_candidate_v1")
    require(type(source) is types.ModuleType and type(gate) is types.ModuleType
            and os.path.abspath(source.__file__)
            == str(ROOT / "tools/python_re_subinterpreter_oracle_v2.py")
            and os.path.abspath(gate.__file__)
            == str(ROOT / "tools/run_frozen_p0_candidate_v1.py"),
            "load only the exact already authenticated frozen source producers")
    try:
        source.validate_publication_receipt(
            receipt, relative=REFERENCE_ARCHIVE_RELATIVE, document=report,
        )
    except (Exception, RecursionError) as error:
        raise SubinterpreterGateError(
            "the genuine original reference archive or durable receipt differs"
        ) from error
    require(report.get("schema")
            == "rebar-python-re-genuine-subinterpreter-v2-self-oracle"
            and report.get("status") == "PASS"
            and report.get("matrix_sha256") == MATRIX_SHA256
            and report.get("reference_records_sha256") == REFERENCE_RECORDS_SHA256
            and report.get("candidate_imports") == 0
            and report.get("performance") == "NOT MEASURED",
            "the complete published original subinterpreter self-oracle changed")
    roles = report.get("reference_roles")
    require(type(roles) is dict and set(roles) == {"reference_a", "reference_b"},
            "retain both genuine independently preserved reference processes")
    validated: list[dict[str, Any]] = []
    for role in ("reference_a", "reference_b"):
        observed = roles[role]
        require(type(observed) is dict and observed.get("role") == role
                and observed.get("status") == "PASS"
                and observed.get("returncode") == 0
                and observed.get("signal") is None
                and observed.get("stdout_complete") is True
                and observed.get("stderr_complete") is True
                and observed.get("timed_out") is False
                and type(observed.get("pid")) is int
                and observed["pid"] > 0,
                "retain the actual independent reference PID and complete streams")
        original = observed.get("report")
        try:
            source.validate_worker_document(original, role,
                                            expected_pid=observed["pid"])
        except (Exception, RecursionError) as error:
            raise SubinterpreterGateError(
                "an unchanged original role or 394-case real lifecycle was forged"
            ) from error
        validated.append(original)
    require(roles["reference_a"]["pid"] != roles["reference_b"]["pid"]
            and canonical(validated[0]["records"])
            == canonical(validated[1]["records"])
            and digest(validated[0]["records"]) == REFERENCE_RECORDS_SHA256,
            "the independent original reference records or processes disagree")
    matrix = source.build_matrix()
    require(source.validate_matrix(matrix) == MATRIX_SHA256
            and type(matrix) is list and len(matrix) == CASE_COUNT,
            "retain all 128 authentic, source-ordered interpreter cases")
    originals = validated[0]["records"]
    for case, record in zip(matrix, originals, strict=True):
        try:
            source.validate_case_record(record, case)
        except (Exception, RecursionError) as error:
            raise SubinterpreterGateError(
                "an authentic original case or observation was omitted"
            ) from error
    projected = [gate.project_subinterpreter_reference(row) for row in originals]
    require(all(canonical(row) == canonical(project_reference_record(original))
                for row, original in zip(projected, originals, strict=True))
            and digest(projected) == PROJECTED_REFERENCE_SHA256,
            "retain the exact lossless no-newline 128-case reference projection")
    program = compose_owned_program(
        source.INTERPRETER_PROGRAM, FAMILIES["c"],
        {"source": "1" * 64, "native_engine": "2" * 64,
         "native_bridge": "2" * 64},
    )
    return {
        "source": source, "gate": gate, "matrix": matrix,
        "records": originals, "projected_records": projected,
        "original_program": source.INTERPRETER_PROGRAM,
        "adapted_program_sha256": program["sha256"],
        "reference_archive_sha256": REFERENCE_ARCHIVE_SHA256,
        "reference_receipt_sha256": REFERENCE_RECEIPT_SHA256,
        "reference_process_ids": [roles[role]["pid"]
                                  for role in ("reference_a", "reference_b")],
    }


def encoded_stream(value: Any) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_REPORT_BYTES,
            "retain one complete bounded real isolated process stream")
    return {
        "encoding": "base64", "bytes": len(value), "sha256": sha256(value),
        "data": base64.b64encode(value).decode("ascii"),
        "complete": True,
    }


def restore_encoded_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"encoding", "bytes", "sha256", "data", "complete"}
            and value.get("encoding") == "base64"
            and value.get("complete") is True
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_REPORT_BYTES
            and type(value.get("data")) is str,
            "retain the complete genuine " + label)
    try:
        raw = base64.b64decode(value["data"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError, binascii.Error) as error:
        raise SubinterpreterGateError("reject a forged " + label) from error
    require(len(raw) == value["bytes"] and sha256(raw) == value.get("sha256")
            and base64.b64encode(raw).decode("ascii") == value["data"],
            "a genuine bounded process or interpreter stream differs")
    return raw


def validate_pipe_schedule(
    matrix: list[dict[str, Any]], identities: Mapping[str, Any],
    pipes: Any, records: list[dict[str, Any]], peers: list[dict[str, Any]],
    repeats: list[dict[str, Any]], fresh: list[dict[str, Any]],
    post_b: dict[str, Any], final_c: dict[str, Any],
) -> None:
    require(type(pipes) is list and len(pipes) == CASE_EXEC_COUNT,
            "retain all 394 actual source-ordered operating-system pipe ledgers")
    expected: list[tuple[str, str, int, dict[str, Any]]] = []
    require(len(matrix) == len(records) == len(peers) == len(repeats) == CASE_COUNT,
            "derive a pipe schedule only from all genuine A/B/A observations")
    for index, case in enumerate(matrix):
        expected.extend((
            (case["case_id"], "A", identities["A"], records[index]),
            (case["case_id"], "B", identities["B"], peers[index]),
            (case["case_id"], "A", identities["A"], repeats[index]),
        ))
    cohort = [case for case in matrix
              if case["cohort"]
              == "repeated-interpreter-creation-and-destruction"]
    require(len(cohort) == len(fresh) == len(identities["temporary"])
            == FRESH_CASE_COUNT,
            "retain all actual temporary-interpreter pipe identities")
    for index, case in enumerate(cohort):
        expected.append((case["case_id"], "C", identities["temporary"][index],
                         fresh[index]))
    expected.extend((
        (matrix[-1]["case_id"], "A", identities["A"], post_b),
        (matrix[-1]["case_id"], "C", identities["C"], final_c),
    ))
    require(len(expected) == CASE_EXEC_COUNT,
            "the original actual A/B/A/fresh/post-close pipe schedule changed")
    for ledger, (case_id, owner, interpreter_id, record) in zip(
        pipes, expected, strict=True,
    ):
        require(type(ledger) is dict and ledger.get("case_id") == case_id
                and ledger.get("owner") == owner
                and type(ledger.get("interpreter_id")) is int
                and ledger["interpreter_id"] == interpreter_id
                and ledger.get("reached_eof") is True
                and ledger.get("all_descriptors_closed") is True,
                "an actual matching case, phase, or interpreter identity was replaced")
        events = ledger.get("descriptor_events")
        require(type(events) is list and len(events) >= 5
                and all(type(event) is dict and event.get("status") == "PASS"
                        and type(event.get("fd")) is int
                        and event["fd"] >= 0 for event in events),
                "a genuine pipe event failed or omitted its real descriptor")
        openings = [row for row in events if row.get("action") == "open"]
        closures = [row for row in events if row.get("action") == "close"]
        reads = [row for row in events if row.get("action") == "read"]
        require(len(openings) == len(closures) == 2
                and len(events) == 4 + len(reads)
                and events[0].get("action") == "open"
                and events[0].get("role") == "reader"
                and events[1].get("action") == "open"
                and events[1].get("role") == "writer"
                and events[2].get("action") == "close"
                and events[2].get("role") == "writer"
                and events[2].get("fd") == events[1].get("fd")
                and events[-1].get("action") == "close"
                and events[-1].get("role") == "reader"
                and events[-1].get("fd") == events[0].get("fd")
                and all(row.get("action") == "read"
                        and row.get("role") == "reader"
                        and row.get("fd") == events[0].get("fd")
                        for row in events[3:-1])
                and {row.get("role") for row in openings} == {"reader", "writer"}
                and {row.get("role") for row in closures} == {"reader", "writer"}
                and all(any(closing.get("role") == opened["role"]
                            and closing.get("fd") == opened["fd"]
                            for closing in closures) for opened in openings)
                and bool(reads)
                and all(type(row.get("requested_bytes")) is int
                        and 0 < row["requested_bytes"] <= MAX_PIPE_BYTES
                        and type(row.get("returned_bytes")) is int
                        and 0 <= row["returned_bytes"] <= row["requested_bytes"]
                        for row in reads)
                and reads[-1]["returned_bytes"] == 0
                and all(row["returned_bytes"] > 0 for row in reads[:-1]),
                "an actual observation pipe was not fully read and closed")
        stream = restore_encoded_stream(ledger.get("observation_stream"),
                                        "actual frozen case pipe stream")
        require(0 < len(stream) <= MAX_PIPE_BYTES
                and sum(row["returned_bytes"] for row in reads) == len(stream)
                and canonical(decode_document(
                    stream, "complete actual case pipe stream", newline=True,
                )) == canonical(record),
                "a real case pipe does not contain its exact matching observation")


def interpreter_bootstrap_source(
    spec: FamilySpec, pins: Mapping[str, str], activation: Mapping[str, Any],
    source_owners: Mapping[str, str], *, owner: str,
) -> str:
    require(owner in {"A", "B", "C"},
            "assign one genuine isolated interpreter owner")
    require(type(activation) is dict
            and activation.get("candidate_import_root") == str(ROOT),
            "require genuine recoverable canonical V2 native activation")
    root = str(ROOT)
    prefix = (
        "import builtins as _phase2_builtins\n"
        "import contextlib as _phase2_contextlib\n"
        "import importlib as _phase2_importlib\n"
        "import os as _phase2_os\n"
        "from pathlib import Path as _phase2_Path\n"
        "import sys as _phase2_sys\n"
        "import types as _phase2_types\n"
        "_phase2_root = _phase2_Path(" + repr(root) + ")\n"
        "_phase2_family = " + repr(spec.name) + "\n"
        "_phase2_adapter = " + repr(spec.adapter_module) + "\n"
        "_phase2_bridge = " + repr(spec.bridge_module) + "\n"
        "_phase2_pins = " + repr(dict(pins)) + "\n"
        "_phase2_source_owners = " + repr(dict(sorted(source_owners.items()))) + "\n"
        "_phase2_support = " + repr(dict(sorted(PRIVATE_GUARD_SOURCES.items()))) + "\n"
        "_phase2_owner = " + repr(owner) + "\n"
        "assert not any(n == 'candidates' or n.startswith('candidates.') "
        "for n in _phase2_sys.modules), 'candidate already loaded in real interpreter'\n"
        "_phase2_previous_original = _phase2_importlib.import_module('re')\n"
        "if not _phase2_sys.path or _phase2_sys.path[0] != str(_phase2_root):\n"
        "    _phase2_sys.path.insert(0, str(_phase2_root))\n"
        "_phase2_names = ("
        "'tools.independent_original_cpython_suite_v5',"
        "'tools.independent_original_cpython_suite_v4',"
        "'tools.rust_original_cpython_suite_v1',"
        "'tools.rust_original_cpython_suite_v2',"
        "'tools.rust_original_cpython_suite_v3')\n"
        "_phase2_loaded = {}\n"
        "for _phase2_name in _phase2_names:\n"
        "    _phase2_module = _phase2_importlib.import_module(_phase2_name)\n"
        "    _phase2_relative = _phase2_name.replace('.', '/') + '.py'\n"
        "    assert isinstance(_phase2_module, _phase2_types.ModuleType)\n"
        "    assert _phase2_module.__name__ == _phase2_name\n"
        "    assert _phase2_module.__spec__ is not None\n"
        "    assert _phase2_os.path.abspath(_phase2_module.__file__) == "
        "str(_phase2_root / _phase2_relative)\n"
        "    assert _phase2_os.path.abspath(_phase2_module.__spec__.origin) == "
        "str(_phase2_root / _phase2_relative)\n"
        "    assert _phase2_module.ROOT == _phase2_root, "
        "'the immutable canonical original matcher guard was relocated'\n"
        "    _phase2_loaded[_phase2_name] = _phase2_module\n"
        "    assert _phase2_sys.path[0] == str(_phase2_root), "
        "'the canonical original guard path changed'\n"
        "_phase2_v5 = _phase2_loaded['tools.independent_original_cpython_suite_v5']\n"
        "for _phase2_relative, _phase2_digest in _phase2_support.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=" + repr(MAX_SOURCE_BYTES) + ")\n"
        "for _phase2_relative, _phase2_digest in _phase2_source_owners.items():\n"
        "    _phase2_v5.read_owned(_phase2_relative, _phase2_digest, "
        "maximum=" + repr(MAX_SOURCE_BYTES) + ")\n"
        "_phase2_spec = _phase2_v5.family_spec(_phase2_family)\n"
        "assert _phase2_spec.adapter_module == _phase2_adapter\n"
        "assert _phase2_spec.bridge_module == _phase2_bridge\n"
        "_phase2_v5.read_owned(_phase2_spec.engine_relative, "
        "_phase2_pins['native_engine'], maximum=" + repr(MAX_BINARY_BYTES) + ")\n"
        "_phase2_v5.read_owned(_phase2_spec.bridge_relative, "
        "_phase2_pins['native_bridge'], maximum=" + repr(MAX_BINARY_BYTES) + ")\n"
        "_phase2_warning, _phase2_identity, _phase2_harness, "
        "_phase2_matrix = _phase2_v5.load_frozen_oracles()\n"
        "_phase2_stack = _phase2_contextlib.ExitStack()\n"
        "try:\n"
        "    _phase2_stack.enter_context("
        "_phase2_warning.installed_warning_safe_guard(_phase2_identity))\n"
        "    _phase2_active = _phase2_stack.enter_context("
        "_phase2_v5.chosen_original_guard(_phase2_previous_original, "
        "_phase2_pins, _phase2_spec, _phase2_identity, _phase2_warning))\n"
        "    _phase2_active['verify']()\n"
        "    _phase2_candidate = _phase2_active['candidate']\n"
        "    assert _phase2_candidate.__name__ == _phase2_adapter\n"
        "    assert _phase2_candidate.__spec__ is not None\n"
        "    assert _phase2_os.path.abspath(_phase2_candidate.__file__) == "
        "str(_phase2_root / _phase2_spec.adapter_relative)\n"
        "    assert _phase2_os.path.abspath(_phase2_candidate.__spec__.origin) == "
        "str(_phase2_root / _phase2_spec.adapter_relative)\n"
        "    assert _phase2_sys.modules.get(_phase2_adapter) "
        "is _phase2_candidate\n"
        "    assert _phase2_sys.modules.get('re') is _phase2_candidate\n"
        "    _phase2_bridge_object = _phase2_sys.modules.get(_phase2_bridge)\n"
        "    assert isinstance(_phase2_bridge_object, _phase2_types.ModuleType)\n"
        "    assert _phase2_os.path.abspath(_phase2_bridge_object.__file__) == "
        "str(_phase2_root / _phase2_spec.bridge_relative)\n"
        "    assert isinstance(_phase2_candidate.Pattern, type)\n"
        "    assert _phase2_candidate.Match is _phase2_bridge_object.Match\n"
        "    assert _phase2_v5.validate_owners("
        "_phase2_active['native_provenance'], _phase2_spec, _phase2_pins)\n"
        "    _phase2_blocker = _phase2_sys.meta_path[0]\n"
        "    assert isinstance(_phase2_blocker, _phase2_v5.FamilyImportBlocker)\n"
        "    _phase2_evidence = _phase2_blocker.evidence\n"
        "    _phase2_cross = "
        "_phase2_evidence['rejected_cross_family_or_external_imports']\n"
        "    _phase2_foreign = "
        "_phase2_evidence['rejected_foreign_dynamic_loads']\n"
        "    assert type(_phase2_cross) is int and _phase2_cross == 0\n"
        "    assert type(_phase2_foreign) is int and _phase2_foreign == 0\n"
        "    _phase2_origin_verified = ("
        "_phase2_candidate.__name__ == _phase2_adapter and "
        "_phase2_os.path.abspath(_phase2_candidate.__file__) == "
        "str(_phase2_root / _phase2_spec.adapter_relative) and "
        "_phase2_sys.modules.get(_phase2_adapter) is _phase2_candidate)\n"
        "    _phase2_import_count = sum("
        "1 for n in _phase2_sys.modules if n == _phase2_adapter)\n"
        "    _phase2_original_calls = int(not "
        "_phase2_active['original_matchers_blocked'])\n"
        "    assert _phase2_origin_verified is True\n"
        "    assert type(_phase2_import_count) is int "
        "and _phase2_import_count == 1\n"
        "    assert _phase2_original_calls == 0\n"
        "    _phase2_builtins._rebar_owned_candidate_subinterpreter_v1 = {\n"
        "        'candidate': _phase2_candidate,\n"
        "        'adapter_module': _phase2_adapter,\n"
        "        'bridge_module': _phase2_bridge,\n"
        "        'bridge': _phase2_bridge_object,\n"
        "        'verify': _phase2_active['verify'],\n"
        "        'stack': _phase2_stack,\n"
        "        'original': _phase2_previous_original,\n"
        "        'candidate_origin_verified': _phase2_origin_verified,\n"
        "        'candidate_import_count': _phase2_import_count,\n"
        "        'original_matcher_calls': _phase2_original_calls,\n"
        "        'external_engine_imports': _phase2_cross,\n"
        "        'cross_candidate_imports': _phase2_cross,\n"
        "        'foreign_native_loads': _phase2_foreign,\n"
        "    }\n"
        "    _phase2_builtins._rebar_subinterpreter_v2_owner = _phase2_owner\n"
        "    _phase2_builtins._rebar_subinterpreter_v2_patterns = {}\n"
        "except BaseException:\n"
        "    _phase2_stack.close()\n"
        "    raise\n"
    )
    try:
        ast.parse(prefix, filename="<canonical-original-v5-interpreter-bootstrap>")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise SubinterpreterGateError(
            "the actual unchanged canonical original-guard bootstrap is invalid"
        ) from error
    return prefix


def interpreter_cleanup_source() -> str:
    source = (
        "import builtins as _phase2_builtins\n"
        "import sys as _phase2_sys\n"
        "_phase2_state = getattr(_phase2_builtins, "
        "'_rebar_owned_candidate_subinterpreter_v1', None)\n"
        "assert type(_phase2_state) is dict, "
        "'the actual persistent matcher guard disappeared'\n"
        "_phase2_original = _phase2_state['original']\n"
        "_phase2_candidate = _phase2_state['candidate']\n"
        "_phase2_adapter = _phase2_state['adapter_module']\n"
        "_phase2_bridge = _phase2_state['bridge_module']\n"
        "assert _phase2_sys.modules.get(_phase2_adapter) is _phase2_candidate\n"
        "assert _phase2_sys.modules.get(_phase2_bridge) "
        "is _phase2_state['bridge']\n"
        "_phase2_state['verify']()\n"
        "try:\n"
        "    _phase2_state['stack'].close()\n"
        "finally:\n"
        "    for _phase2_name in ("
        "'_rebar_owned_candidate_subinterpreter_v1',"
        "'_rebar_subinterpreter_v2_owner',"
        "'_rebar_subinterpreter_v2_patterns'):\n"
        "        if hasattr(_phase2_builtins, _phase2_name):\n"
        "            delattr(_phase2_builtins, _phase2_name)\n"
        "assert _phase2_sys.modules.get('re') is _phase2_original, "
        "'the authentic original matcher was not restored'\n"
        "for _phase2_name in (_phase2_adapter, _phase2_bridge):\n"
        "    if _phase2_name.startswith('candidates.'):\n"
        "        _phase2_sys.modules.pop(_phase2_name, None)\n"
        "_phase2_sys.modules.pop('candidates', None)\n"
        "assert not any(n == 'candidates' or n.startswith('candidates.') "
        "for n in _phase2_sys.modules), "
        "'a private candidate escaped real interpreter cleanup'\n"
    )
    ast.parse(source, filename="<persistent-original-v5-cleanup>")
    return source


def observation_source(
    case: Mapping[str, Any], descriptor: int, owner: str,
    main_id: int, source: types.ModuleType, program: Mapping[str, Any],
    spec: FamilySpec, pins: Mapping[str, str], private_root: str,
) -> str:
    require(type(case) is dict and type(descriptor) is int and descriptor >= 0
            and owner in {"A", "B", "C"}
            and type(main_id) is int and main_id >= 0,
            "compose only an authenticated actual case and operating-system pipe")
    require(program.get("sha256") == ADAPTED_PROGRAM_SHA256
            and program.get("bytes") == ADAPTED_PROGRAM_BYTES
            and sha256(program["source"].encode("utf-8"))
            == ADAPTED_PROGRAM_SHA256,
            "the genuine exactly frozen observation program changed")
    return (
        "_case = " + repr(dict(case)) + "\n"
        + "_write_fd = " + repr(descriptor) + "\n"
        + "_owner = " + repr(owner) + "\n"
        + "_main_id = " + repr(main_id) + "\n"
        + "_stdlib_re_origin = " + repr(source.PINNED_STDLIB_RE) + "\n"
        + "_public_interpreter_origin = " + repr(PINNED_INTERPRETERS) + "\n"
        + "_pinned_python = " + repr(PINNED_PYTHON) + "\n"
        + "_candidate_family = " + repr(spec.name) + "\n"
        + "_candidate_module_name = " + repr(spec.adapter_module) + "\n"
        + "_candidate_adapter_origin = "
        + repr(private_root + "/" + spec.adapter_relative) + "\n"
        + "_candidate_source_sha256 = " + repr(pins["source"]) + "\n"
        + "_candidate_engine_sha256 = " + repr(pins["native_engine"]) + "\n"
        + "_candidate_bridge_sha256 = " + repr(pins["native_bridge"]) + "\n"
        + "_allowed_candidate_modules = "
        + repr(frozenset({"candidates", spec.adapter_module, spec.bridge_module}))
        + "\n" + program["source"]
    )


def observe_interpreter(
    interpreter: Any, *, case: dict[str, Any], baseline: dict[str, Any],
    owner: str, main_id: int, source: types.ModuleType,
    gate: types.ModuleType, program: Mapping[str, Any], spec: FamilySpec,
    pins: Mapping[str, str], private_root: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    pieces: list[bytes] = []
    reader: int | None = None
    writer: int | None = None
    primary: BaseException | None = None
    phase = "open-genuine-observation-pipe"
    eof = False
    result: dict[str, Any] | None = None
    try:
        reader, writer = os.pipe()
        events.extend(({"role": "reader", "action": "open", "fd": reader,
                        "status": "PASS"},
                       {"role": "writer", "action": "open", "fd": writer,
                        "status": "PASS"}))
        phase = "compose-authentic-original-private-case"
        script = observation_source(
            case, writer, owner, main_id, source, program, spec, pins, private_root,
        )
        phase = "execute-real-public-interpreter-case"
        require(interpreter.exec(script) is None,
                "the actual private candidate interpreter case did not complete")
        phase = "close-real-observation-writer"
        pending = {"role": "writer", "action": "close", "fd": writer,
                   "status": "PENDING"}
        events.append(pending)
        closing = writer
        writer = None
        os.close(closing)
        pending["status"] = "PASS"
        phase = "read-real-observation-to-eof"
        total = 0
        while True:
            request = min(65_536, MAX_PIPE_BYTES - total + 1)
            event: dict[str, Any] = {
                "role": "reader", "action": "read", "fd": reader,
                "requested_bytes": request, "returned_bytes": None,
                "status": "PENDING",
            }
            events.append(event)
            piece = os.read(reader, request)
            event["returned_bytes"] = len(piece)
            event["status"] = "PASS"
            if not piece:
                eof = True
                break
            total += len(piece)
            require(total <= MAX_PIPE_BYTES,
                    "the genuine original producer's 256-KiB pipe bound was exceeded")
            pieces.append(piece)
        phase = "decode-complete-original-candidate-record"
        parsed = decode_document(
            b"".join(pieces), "actual genuine candidate interpreter observation",
            newline=True,
        )
        validate_case_record(parsed, baseline, spec, pins)
        try:
            gate.validate_subinterpreter_candidate_record(parsed, baseline)
        except (Exception, RecursionError) as error:
            raise SubinterpreterGateError(
                "the original frozen P0 candidate gate rejected the actual case"
            ) from error
        result = parsed
    except BaseException as error:
        primary = error
    finally:
        for role in ("writer", "reader"):
            descriptor = writer if role == "writer" else reader
            if descriptor is None:
                continue
            if role == "writer":
                writer = None
            else:
                reader = None
            event = {"role": role, "action": "close", "fd": descriptor,
                     "status": "PENDING"}
            events.append(event)
            try:
                os.close(descriptor)
            except BaseException as cleanup:
                event["status"] = "FAIL"
                event["error_type"] = type(cleanup).__name__
                event["error_message"] = str(cleanup)
                if primary is None:
                    primary = cleanup
            else:
                event["status"] = "PASS"
    if primary is not None:
        raise ActualCaseFailure(
            "a real interpreter observation or operating-system pipe failed",
            {
                "status": "FAIL", "active_case": dict(case),
                "active_phase": phase, "interpreter_role": owner,
                "error_type": type(primary).__name__,
                "error_message": str(primary),
                "partial_observation_stream": encoded_stream(b"".join(pieces)),
                "observation_stream_complete": eof,
                "descriptor_events": events,
            },
        ) from primary
    require(type(result) is dict and eof,
            "a genuine real interpreter case did not yield a full observation")
    require(all(event.get("status") == "PASS" for event in events)
            and sum(event.get("action") == "open" for event in events) == 2
            and sum(event.get("action") == "close" for event in events) == 2,
            "a genuine observation pipe descriptor leaked")
    return result, {
        "case_id": case["case_id"], "owner": owner,
        "interpreter_id": int(interpreter.id),
        "reached_eof": eof, "all_descriptors_closed": True,
        "descriptor_events": events,
        "observation_stream": encoded_stream(b"".join(pieces)),
    }


def validate_worker_document(
    value: Any, *, spec: FamilySpec, pins: Mapping[str, str],
    original: Mapping[str, Any], expected_pid: int | None,
) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("schema") == SCHEMA + "-actual-worker"
            and value.get("status") == "PASS"
            and value.get("candidate_family") == spec.name
            and value.get("candidate_module") == spec.adapter_module,
            "a genuine complete isolated private candidate worker is required")
    if expected_pid is not None:
        require(type(expected_pid) is int and expected_pid > 0
                and value.get("pid") == expected_pid,
                "the complete real worker was not bound to its Popen PID")
    counts = {
        "case_count": CASE_COUNT,
        "actual_case_interpreter_exec_calls": CASE_EXEC_COUNT,
        "actual_initialization_interpreter_exec_calls": INTERPRETER_COUNT,
        "actual_guard_cleanup_interpreter_exec_calls": INTERPRETER_COUNT,
        "actual_interpreters_created": INTERPRETER_COUNT,
        "actual_interpreters_destroyed": INTERPRETER_COUNT,
        "fresh_interpreter_case_count": FRESH_CASE_COUNT,
        "original_matcher_calls": 0,
        "external_engine_imports": 0,
        "cross_candidate_imports": 0,
        "foreign_native_loads": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
    }
    for name, expected in counts.items():
        require(type(value.get(name)) is int and value[name] == expected,
                "a genuine matching, initialization, cleanup, or boundary count changed: "
                + name)
    for name in ("all_real_pipes_read_to_eof", "all_real_pipe_descriptors_closed",
                 "interpreter_live_set_restored", "locale_restored",
                 "simultaneous_interpreters_verified", "b_closed_before_a_reexecution",
                 "fresh_c_verified", "persistent_original_v5_per_interpreter"):
        require(value.get(name) is True,
                "a complete real interpreter lifecycle proof is missing: " + name)
    require(value.get("performance") == "NOT MEASURED"
            and value.get("holdout") == "NOT OPENED"
            and value.get("adapted_program_sha256") == ADAPTED_PROGRAM_SHA256
            and value.get("adapted_program_bytes") == ADAPTED_PROGRAM_BYTES
            and value.get("reference_records_sha256") == REFERENCE_RECORDS_SHA256
            and value.get("projected_reference_records_sha256")
            == PROJECTED_REFERENCE_SHA256,
            "the genuine full original producer, holdout boundary, or adapter changed")
    matrix = original["matrix"]
    reference = original["records"]
    for vector_name in ("records", "peer_records", "repeated_a_records"):
        rows = value.get(vector_name)
        require(type(rows) is list and len(rows) == CASE_COUNT,
                "retain every real original case in " + vector_name)
        for row, baseline, case in zip(rows, reference, matrix, strict=True):
            require(row.get("case_id") == case["case_id"],
                    "an original source-ordered case was omitted or rearranged")
            validate_case_record(row, baseline, spec, pins)
        projected = [{key: row[key] for key in REQUIRED_CASE_FIELDS}
                     for row in rows]
        require(digest(projected) == PROJECTED_REFERENCE_SHA256,
                "an actual complete A/B/A vector differs from frozen Python")
    require(canonical(value["records"]) == canonical(value["peer_records"])
            and canonical(value["records"])
            == canonical(value["repeated_a_records"]),
            "actual A, B, and repeated A interpreter records disagree")
    identities = value.get("actual_interpreter_ids")
    require(type(identities) is dict
            and set(identities) == {"A", "B", "C", "temporary"}
            and all(type(identities.get(name)) is int
                    and identities[name] >= 0 for name in ("A", "B", "C"))
            and len({identities["A"], identities["B"], identities["C"]}) == 3
            and type(identities.get("temporary")) is list
            and len(identities["temporary"]) == FRESH_CASE_COUNT
            and all(type(identifier) is int and identifier >= 0
                    for identifier in identities["temporary"])
            and len(set(identities["temporary"])) == FRESH_CASE_COUNT
            and set(identities["temporary"]).isdisjoint(
                {identities["A"], identities["B"], identities["C"]},
            ), "require eleven distinct genuine public-interpreter identities")
    fresh_cases = [case for case in matrix
                   if case["cohort"]
                   == "repeated-interpreter-creation-and-destruction"]
    fresh = value.get("repeated_creation_records")
    require(type(fresh) is list and len(fresh) == FRESH_CASE_COUNT
            and len(fresh_cases) == FRESH_CASE_COUNT,
            "retain all eight genuinely created independent interpreter cases")
    for case, row in zip(fresh_cases, fresh, strict=True):
        validate_case_record(row, reference[case["ordinal"]], spec, pins)
        require(canonical(row) == canonical(value["records"][case["ordinal"]]),
                "an actual fresh interpreter disagrees with the original case")
    for name in ("actual_post_b_close_a_record", "actual_fresh_c_record"):
        row = value.get(name)
        validate_case_record(row, reference[-1], spec, pins)
        require(canonical(row) == canonical(value["records"][-1]),
                "the actual A-after-B or independently created C result differs")
    validate_pipe_schedule(
        matrix, identities, value.get("pipe_ledgers"),
        value["records"], value["peer_records"], value["repeated_a_records"],
        fresh, value["actual_post_b_close_a_record"],
        value["actual_fresh_c_record"],
    )
    return value


def internal_worker(arguments: Mapping[str, Any]) -> dict[str, Any]:
    context = authenticate_prerequisites(arguments)
    spec: FamilySpec = context["spec"]
    pins: dict[str, str] = context["pins"]
    activation = context["canonical_activation"]
    source_owners = context["source_owners"]
    original = load_original_baseline()
    _, _ = authenticate_path(
        Path(PINNED_INTERPRETERS), PINNED_INTERPRETERS_SHA256,
        maximum=MAX_SOURCE_BYTES,
    )
    public = importlib.import_module("concurrent.interpreters")
    require(type(public) is types.ModuleType and public.__spec__ is not None
            and os.path.abspath(public.__spec__.origin) == PINNED_INTERPRETERS
            and callable(getattr(public, "create", None))
            and callable(getattr(public, "list_all", None))
            and callable(getattr(public, "get_current", None))
            and callable(getattr(public.Interpreter, "exec", None))
            and callable(getattr(public.Interpreter, "close", None)),
            "load the exact pinned genuine public Python subinterpreter provider")
    program = compose_owned_program(original["original_program"], spec, pins)
    original_live = {int(item.id) for item in public.list_all()}
    main_id = int(public.get_current().id)
    original_locale = locale.setlocale(locale.LC_CTYPE)
    first = second = third = temporary = None
    created = destroyed = case_calls = init_calls = cleanup_calls = 0
    ids: dict[str, Any] = {"A": None, "B": None, "C": None, "temporary": []}
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

    def prepare(interpreter: Any, owner: str) -> None:
        nonlocal init_calls
        init_calls += 1
        require(interpreter.exec(interpreter_bootstrap_source(
            spec, pins, activation, source_owners, owner=owner,
        )) is None, "the actual persistent private original V5 guard did not install")

    def close(interpreter: Any, owner: str) -> None:
        nonlocal cleanup_calls, destroyed
        identity = int(interpreter.id)
        require(identity in {int(item.id) for item in public.list_all()},
                "an authentic interpreter disappeared before guard cleanup")
        cleanup_calls += 1
        require(interpreter.exec(interpreter_cleanup_source()) is None,
                "the actual persistent original matcher guard failed to restore")
        interpreter.close()
        destroyed += 1
        require(identity not in {int(item.id) for item in public.list_all()},
                "a genuine public interpreter remained alive after close")

    def execute(interpreter: Any, case: dict[str, Any], owner: str,
                baseline: dict[str, Any]) -> dict[str, Any]:
        nonlocal case_calls
        case_calls += 1
        row, ledger = observe_interpreter(
            interpreter, case=case, baseline=baseline, owner=owner,
            main_id=main_id, source=original["source"], gate=original["gate"],
            program=program, spec=spec, pins=pins,
            private_root=activation["candidate_import_root"],
        )
        pipes.append(ledger)
        return row

    try:
        first = public.create()
        created += 1
        ids["A"] = int(first.id)
        phase = "create-real-simultaneous-private-interpreter-B"
        second = public.create()
        created += 1
        ids["B"] = int(second.id)
        require(len({main_id, ids["A"], ids["B"]}) == 3,
                "A and B are not genuine distinct simultaneously live interpreters")
        phase = "install-real-persistent-original-V5-in-A"
        prepare(first, "A")
        phase = "install-real-persistent-original-V5-in-B"
        prepare(second, "B")
        for case, baseline in zip(original["matrix"], original["records"],
                                  strict=True):
            active_case = case
            phase = "execute-actual-simultaneous-A"
            left = execute(first, case, "A", baseline)
            records.append(left)
            phase = "execute-actual-simultaneous-B"
            middle = execute(second, case, "B", baseline)
            peers.append(middle)
            phase = "execute-actual-repeated-A-after-B"
            right = execute(first, case, "A", baseline)
            repeats.append(right)
            require(canonical(left) == canonical(middle)
                    and canonical(left) == canonical(right),
                    "genuine simultaneous A/B/A candidate interpreters disagree")
        repeated_cases = [case for case in original["matrix"]
                          if case["cohort"]
                          == "repeated-interpreter-creation-and-destruction"]
        require(len(repeated_cases) == FRESH_CASE_COUNT,
                "an authentic fresh-interpreter matrix cohort was changed")
        for case in repeated_cases:
            active_case = case
            phase = "create-real-independent-fresh-interpreter"
            temporary = public.create()
            created += 1
            ids["temporary"].append(int(temporary.id))
            phase = "install-persistent-original-V5-in-fresh-interpreter"
            prepare(temporary, "C")
            phase = "execute-real-independent-fresh-interpreter"
            actual = execute(temporary, case, "C",
                             original["records"][case["ordinal"]])
            fresh.append(actual)
            phase = "cleanup-real-independent-fresh-interpreter"
            close(temporary, "temporary")
            temporary = None
        phase = "restore-real-original-V5-and-close-B"
        close(second, "B")
        second = None
        phase = "execute-real-A-after-actual-B-close"
        active_case = original["matrix"][-1]
        post_b = execute(first, active_case, "A", original["records"][-1])
        phase = "restore-real-original-V5-and-close-A"
        close(first, "A")
        first = None
        phase = "create-genuine-independent-final-interpreter-C"
        third = public.create()
        created += 1
        ids["C"] = int(third.id)
        phase = "install-persistent-original-V5-in-final-C"
        prepare(third, "C")
        phase = "execute-genuine-independent-final-C"
        final_c = execute(third, active_case, "C", original["records"][-1])
        phase = "restore-real-original-V5-and-close-C"
        close(third, "C")
        third = None
        require(created == destroyed == init_calls == cleanup_calls
                == INTERPRETER_COUNT and case_calls == CASE_EXEC_COUNT,
                "the complete genuine 394 + 11 + 11 interpreter lifecycle differs")
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
            "active_phase": phase, "active_case": active_case,
            "actual_interpreter_ids": ids,
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
            "pipe_ledgers": pipes, "cleanup_failures": cleanup_failures,
        }
        if primary is not None:
            details.update({"error_type": type(primary).__name__,
                            "error_message": str(primary)})
            if isinstance(primary, ActualCaseFailure):
                details["actual_case_failure"] = primary.details
        raise ActualCaseFailure(
            "the genuinely executed, isolated native interpreter lifecycle failed",
            details,
        ) from primary
    restored_ids = {int(item.id) for item in public.list_all()}
    restored_locale = locale.setlocale(locale.LC_CTYPE)
    require(restored_ids == original_live and restored_locale == original_locale,
            "the actual interpreter set or process-global locale was not restored")
    report: dict[str, Any] = {
        "schema": SCHEMA + "-actual-worker", "status": "PASS",
        "pid": os.getpid(), "python": "3.14.6",
        "candidate_family": spec.name, "candidate_module": spec.adapter_module,
        "matrix_sha256": MATRIX_SHA256, "case_count": CASE_COUNT,
        "reference_records_sha256": REFERENCE_RECORDS_SHA256,
        "projected_reference_records_sha256": PROJECTED_REFERENCE_SHA256,
        "adapted_program_sha256": ADAPTED_PROGRAM_SHA256,
        "adapted_program_bytes": ADAPTED_PROGRAM_BYTES,
        "records": records, "peer_records": peers, "repeated_a_records": repeats,
        "repeated_creation_records": fresh,
        "actual_post_b_close_a_record": post_b,
        "actual_fresh_c_record": final_c,
        "actual_interpreter_ids": ids,
        "actual_case_interpreter_exec_calls": case_calls,
        "actual_initialization_interpreter_exec_calls": init_calls,
        "actual_guard_cleanup_interpreter_exec_calls": cleanup_calls,
        "actual_interpreters_created": created,
        "actual_interpreters_destroyed": destroyed,
        "fresh_interpreter_case_count": len(fresh),
        "simultaneous_interpreters_verified": True,
        "b_closed_before_a_reexecution": True, "fresh_c_verified": True,
        "persistent_original_v5_per_interpreter": True,
        "all_real_pipes_read_to_eof": all(row["reached_eof"] for row in pipes),
        "all_real_pipe_descriptors_closed": all(
            row["all_descriptors_closed"] for row in pipes
        ),
        "pipe_ledgers": pipes, "interpreter_live_set_restored": True,
        "locale_restored": True,
        "original_matcher_calls": sum(row["original_matcher_calls"]
                                      for row in records + peers + repeats + fresh
                                      + [post_b, final_c]),
        "external_engine_imports": sum(row["external_engine_imports"]
                                      for row in records + peers + repeats + fresh
                                      + [post_b, final_c]),
        "cross_candidate_imports": sum(row["cross_candidate_imports"]
                                      for row in records + peers + repeats + fresh
                                      + [post_b, final_c]),
        "foreign_native_loads": sum(row["foreign_native_loads"]
                                   for row in records + peers + repeats + fresh
                                   + [post_b, final_c]),
        "source_build_v2": context["source_build_v2"],
        "canonical_activation": context["canonical_activation"],
        "reference_process_ids": original["reference_process_ids"],
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }
    return validate_worker_document(
        report, spec=spec, pins=pins, original=original,
        expected_pid=os.getpid(),
    )


def invoke_static_independence_audit(
    spec: FamilySpec, source_owners: Mapping[str, str],
) -> dict[str, Any]:
    arguments = [
        PINNED_PYTHON, "-I", "-B",
        str(ROOT / "tools/audit_candidate_independence_v1.py"),
        "--verify", "--family", spec.audit_name,
        "--source-sha256", AUDIT_SOURCE_SHA256,
        "--protocol-sha256", AUDIT_PROTOCOL_SHA256,
    ]
    for relative, expected in sorted(source_owners.items()):
        arguments.extend(["--expect-owner-sha256", relative + "=" + expected])
    process = subprocess.Popen(
        arguments, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(ROOT), shell=False,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
             "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
    )
    evidence = capture_process(process, "frozen static independence audit")
    stdout, stderr = evidence["stdout_bytes"], evidence["stderr_bytes"]
    require(type(stdout) is bytes and type(stderr) is bytes
            and len(stdout) <= MAX_REPORT_BYTES
            and len(stderr) <= MAX_REPORT_BYTES,
            "retain the complete bounded static-audit process streams")
    if evidence["timed_out"] or process.returncode != 0 or stderr != b"":
        raise ActualCaseFailure(
            "the frozen isolated static independence audit did not pass",
            {key: value for key, value in evidence.items()
             if key not in {"stdout_bytes", "stderr_bytes"}},
        )
    result = decode_document(stdout, "frozen isolated static independence audit",
                             newline=True)
    require(type(result) is dict
            and result.get("schema")
            == "rebar-phase2-candidate-independence-static-audit-v1"
            and result.get("status") == "PASS"
            and result.get("static_independence") == "PASS"
            and result.get("family_count") == 1
            and type(result.get("families")) is list
            and len(result["families"]) == 1
            and result["families"][0].get("name") == spec.audit_name
            and result["families"][0].get("static_independence") == "PASS"
            and result.get("candidate_code_executed") is False
            and result.get("native_libraries_loaded") is False,
            "the selected candidate's frozen full static source audit differs")
    for name in ("candidate_workers_started", "reference_workers_started",
                 "clock_samples", "hidden_cases_read", "performance_files_read"):
        require(type(result.get(name)) is int and result[name] == 0,
                "the static audit ran a candidate, a reference, or a benchmark")
    return {
        "report": result, "pid": process.pid, "returncode": process.returncode,
        "stdout": encoded_stream(stdout), "stderr": encoded_stream(stderr),
    }


def capture_process(process: Any, role: str) -> dict[str, Any]:
    require(type(role) is str and role
            and isinstance(process, subprocess.Popen),
            "capture only the exact genuinely spawned isolated process")
    timed_out = False
    partial_stdout = b""
    partial_stderr = b""
    try:
        try:
            stdout, stderr = process.communicate(timeout=PROCESS_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as error:
            timed_out = True
            partial_stdout = error.output if type(error.output) is bytes else b""
            partial_stderr = error.stderr if type(error.stderr) is bytes else b""
            process.kill()
            stdout, stderr = process.communicate(timeout=PROCESS_CLEANUP_SECONDS)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=PROCESS_CLEANUP_SECONDS)
    require(type(stdout) is bytes and type(stderr) is bytes
            and len(stdout) <= MAX_REPORT_BYTES
            and len(stderr) <= MAX_REPORT_BYTES,
            "preserve only bounded complete actual subprocess output")
    require(type(process.pid) is int and process.pid > 0
            and type(process.returncode) is int,
            "reap the actual isolated process and retain its real exit code")
    return {
        "role": role, "pid": process.pid, "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "timed_out": timed_out,
        "timeout_seconds": PROCESS_TIMEOUT_SECONDS,
        "partial_timeout_stdout": encoded_stream(partial_stdout),
        "partial_timeout_stderr": encoded_stream(partial_stderr),
        "stdout": encoded_stream(stdout), "stderr": encoded_stream(stderr),
        "stdout_bytes": stdout, "stderr_bytes": stderr,
        "process_reaped": True,
    }


def process_arguments(arguments: Mapping[str, Any]) -> list[str]:
    mapping = (
        ("--family", "family"), ("--label", "label"),
        ("--source-sha256", "source_sha256"),
        ("--protocol-sha256", "protocol_sha256"),
        ("--explanation-sha256", "explanation_sha256"),
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
        result.extend([option, arguments[key]])
    for owner in arguments["owned_source_sha256"]:
        result.extend(["--owned-source-sha256", owner])
    return result


def evidence_names(spec: FamilySpec, label: str,
                   *, failure: bool) -> tuple[str, str]:
    base = "owned-candidate-subinterpreters-v1-" + spec.name + "-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def ensure_evidence_fresh(spec: FamilySpec, label: str) -> None:
    parent = ROOT / EVIDENCE_RELATIVE
    observed = os.lstat(str(parent))
    require(stat.S_ISDIR(observed.st_mode) and not stat.S_ISLNK(observed.st_mode),
            "the frozen evidence directory is not a genuine owned directory")
    for failed in (False, True):
        for name in evidence_names(spec, label, failure=failed):
            try:
                os.lstat(str(parent / name))
            except FileNotFoundError:
                continue
            raise SubinterpreterGateError(
                "refusing to overwrite any preserved interpreter evidence: " + name
            )


def write_fresh_evidence(directory: int, name: str, content: bytes) -> dict[str, Any]:
    require(type(name) is str and "/" not in name and name
            and type(content) is bytes and 0 < len(content) <= MAX_ARCHIVE_BYTES,
            "publish only one exact bounded frozen result")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(name, flags, 0o600, dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode),
                "exclusive evidence did not create a real owned regular file")
        position = 0
        while position < len(content):
            written = os.write(descriptor, content[position:])
            require(type(written) is int and written > 0,
                    "the complete durable evidence write failed")
            position += written
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
                and after.st_size == len(content),
                "an exclusively written result inode changed")
    finally:
        os.close(descriptor)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    reader = os.open(name, flags, dir_fd=directory)
    try:
        identity = os.fstat(reader)
        require((identity.st_dev, identity.st_ino) == (after.st_dev, after.st_ino)
                and identity.st_size == len(content),
                "the durable evidence readback changed its actual inode")
        parts: list[bytes] = []
        remaining = identity.st_size
        while remaining:
            piece = os.read(reader, min(remaining, 1_048_576))
            require(type(piece) is bytes and bool(piece),
                    "a durable evidence readback was truncated")
            parts.append(piece)
            remaining -= len(piece)
        require(os.read(reader, 1) == b""
                and b"".join(parts) == content,
                "the exact durable evidence readback differs")
    finally:
        os.close(reader)
    return {
        "relative": EVIDENCE_RELATIVE + "/" + name,
        "sha256": sha256(content), "bytes": len(content),
        "device": after.st_dev, "inode": after.st_ino,
        "exclusive_creation": True, "nofollow": True,
        "file_fsync": True, "same_inode_readback_verified": True,
    }


def publish_report(report: dict[str, Any], spec: FamilySpec,
                   label: str) -> dict[str, Any]:
    failure = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(spec, label, failure=failure)
    plain = canonical_line(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "a complete real interpreter report exceeded its frozen bound")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(len(archive) <= MAX_ARCHIVE_BYTES,
            "a complete compressed interpreter report exceeded its frozen bound")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(str(ROOT / EVIDENCE_RELATIVE), flags)
    try:
        archive_record = write_fresh_evidence(directory, archive_name, archive)
        os.fsync(directory)
        receipt = {
            "schema": RECEIPT_SCHEMA, "status": "PASS",
            "result_status": report["status"], "family": spec.name,
            "label": label, "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "explanation_sha256": report["explanation_sha256"],
            "archive_relative": archive_record["relative"],
            "archive_sha256": archive_record["sha256"],
            "archive_bytes": archive_record["bytes"],
            "uncompressed_sha256": sha256(plain),
            "uncompressed_bytes": len(plain),
            "archive_publication": archive_record,
            "archive_directory_fsync": True,
            "source_build_v2_sha256": report.get("source_build_v2_archive_sha256"),
            "activation_report_sha256": report.get("activation_report_sha256"),
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "receipt_self_publication": "NOT CLAIMED",
        }
        receipt_bytes = canonical_line(receipt)
        receipt_record = write_fresh_evidence(directory, receipt_name, receipt_bytes)
        os.fsync(directory)
    finally:
        os.close(directory)
    return {
        "schema": SCHEMA + "-published-candidate-result",
        "status": report["status"], "candidate_family": spec.name,
        "label": label, "archive": archive_record, "receipt": receipt_record,
        "failure_preserved": failure, "directory_fsync": True,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def run_candidate(arguments: Mapping[str, Any]) -> dict[str, Any]:
    context = authenticate_prerequisites(arguments)
    spec: FamilySpec = context["spec"]
    label = checked_label(arguments["label"])
    ensure_evidence_fresh(spec, label)
    original = load_original_baseline()
    report: dict[str, Any] = {
        "schema": SCHEMA + "-candidate-evaluation", "status": "FAIL",
        "candidate_family": spec.name, "label": label,
        "source_sha256": arguments["source_sha256"],
        "protocol_sha256": arguments["protocol_sha256"],
        "explanation_sha256": arguments["explanation_sha256"],
        "source_build_v2_archive_sha256": arguments["build_archive_sha256"],
        "activation_report_sha256": arguments["activation_report_sha256"],
        "static_independence_audit": None, "worker": None,
        "worker_process": None, "failure": None,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }
    process: Any = None
    try:
        report["static_independence_audit"] = invoke_static_independence_audit(
            spec, context["source_owners"],
        )
        process = subprocess.Popen(
            process_arguments(arguments), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(ROOT), shell=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
        process_evidence = capture_process(
            process, "genuine isolated candidate subinterpreter worker",
        )
        stdout = process_evidence["stdout_bytes"]
        stderr = process_evidence["stderr_bytes"]
        require(type(stdout) is bytes and type(stderr) is bytes
                and len(stdout) <= MAX_REPORT_BYTES
                and len(stderr) <= MAX_REPORT_BYTES,
                "preserve complete genuine candidate process output")
        report["worker_process"] = {
            key: value for key, value in process_evidence.items()
            if key not in {"stdout_bytes", "stderr_bytes"}
        }
        require(process_evidence["timed_out"] is False,
                "the actual isolated candidate exceeded its correctness timeout")
        require(process.returncode in (0, 1),
                "the complete candidate process crashed or was signal-terminated")
        require(stderr == b"", "the real isolated candidate produced stderr")
        worker = decode_document(stdout, "actual isolated candidate worker",
                                 newline=True)
        if process.returncode != 0:
            raise ActualCaseFailure("the genuine candidate interpreter worker failed",
                                   worker)
        report["worker"] = validate_worker_document(
            worker, spec=spec, pins=context["pins"], original=original,
            expected_pid=process.pid,
        )
        report["status"] = "PASS"
    except BaseException as error:
        details: dict[str, Any] = {
            "error_type": type(error).__name__, "error_message": str(error),
        }
        if isinstance(error, ActualCaseFailure):
            details["actual_failure"] = error.details
        if process is not None:
            details["pid"] = process.pid
            details["returncode"] = process.returncode
        report["failure"] = details
    return publish_report(report, spec, label)


class SourceOnlyBoundary:
    """Reject real I/O, workers, interpreters, timings, and candidate imports."""

    def __init__(self) -> None:
        self.attempts: dict[str, int] = {
            "file_reads": 0, "file_writes": 0, "descriptor_reads": 0,
            "descriptor_writes": 0, "pipes": 0, "processes": 0,
            "threads": 0, "dynamic_imports": 0,
            "candidate_imports": 0, "interpreter_imports": 0,
            "interpreters_created": 0, "interpreter_exec_calls": 0,
            "native_library_loads": 0, "audit_hooks": 0,
            "locale_changes": 0, "clock_samples": 0,
            "garbage_collections": 0, "hidden_cases_read": 0,
            "benchmark_files_read": 0, "network_requests": 0,
        }
        self._stack = contextlib.ExitStack()
        self._before_modules: frozenset[str] = frozenset()

    def blocked(self, category: str) -> Callable[..., Any]:
        require(category in self.attempts,
                "reject an invented source-only boundary category")

        def reject(*args: Any, **kwargs: Any) -> Any:
            self.attempts[category] += 1
            raise SourceOnlyViolation(
                "synthetic source control blocked real " + category
            )

        return reject

    def patch(self, target: Any, name: str, category: str) -> None:
        if not hasattr(target, name):
            return
        original = getattr(target, name)
        self._stack.callback(setattr, target, name, original)
        setattr(target, name, self.blocked(category))

    def __enter__(self) -> SourceOnlyBoundary:
        self._before_modules = frozenset(sys.modules)
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
                or (name == "concurrent"
                    and fromlist is not None
                    and any(item == "interpreters" for item in fromlist))
                or name == "_interpreters" or name == "_interpchannels"
                or name == "_interpqueues"
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
            return original_import(name, globals, locals, fromlist, level)

        self._stack.callback(setattr, builtins, "__import__", original_import)
        builtins.__import__ = guarded_import
        self.patch(builtins, "open", "file_reads")
        self.patch(io, "open", "file_reads")
        self.patch(io, "open_code", "file_reads")
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
        for name in ("write_bytes", "write_text", "mkdir", "unlink",
                     "rename", "replace", "touch", "chmod"):
            self.patch(Path, name, "file_writes")
        self.patch(importlib, "import_module", "dynamic_imports")
        self.patch(subprocess, "Popen", "processes")
        self.patch(subprocess, "run", "processes")
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
        loaded = sys.modules.get("concurrent.interpreters")
        if loaded is not None:
            self.patch(loaded, "create", "interpreters_created")
            interpreter_type = getattr(loaded, "Interpreter", None)
            if interpreter_type is not None:
                for operation, category in (("exec", "interpreter_exec_calls"),
                                            ("close", "interpreters_created")):
                    try:
                        self.patch(interpreter_type, operation, category)
                    except (TypeError, AttributeError):
                        pass
        ffi = sys.modules.get("ctypes")
        if ffi is not None:
            self.patch(ffi, "CDLL", "native_library_loads")
            self.patch(ffi, "PyDLL", "native_library_loads")
        return self

    def __exit__(self, error_type: Any, error: Any, traceback: Any) -> None:
        self._stack.close()
        added = set(sys.modules) - self._before_modules
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in added),
                "a synthetic source test imported a real native candidate")
        require(not any(name == "concurrent.interpreters"
                        or name.startswith("concurrent.interpreters.")
                        or name in {"_interpreters", "_interpchannels",
                                    "_interpqueues"}
                        for name in added),
                "a synthetic source test imported a real interpreter provider")


SYNTHETIC_PRODUCER_PROGRAM = r'''
import builtins as _builtins
import concurrent.interpreters as _public
import importlib as _importlib
import json as _json
import locale as _locale
import os as _os
import re as _re
import sys as _sys

def _assert(condition, message):
    if condition is not True:
        raise AssertionError(message)

_assert(_re.__spec__ is not None
        and _os.path.abspath(_re.__spec__.origin) == _stdlib_re_origin
        and _os.path.abspath(_re.__file__) == _stdlib_re_origin,
        "the actual pinned standard-library regex module was replaced")
_assert(not any(name == "candidates" or name.startswith("candidates.")
                for name in _sys.modules), "a production candidate entered the reference")
_observation = {
        "stdlib_re_module": _re.__name__ == "re",
        "module_identity": _sys.modules["re"] is _re,
        "pattern_is_stdlib_pattern": True,
        "match_is_stdlib_match": True,
}
_again = _importlib.import_module("re")
_observation.update({
            "actual_stdlib_reimport": _again is _re,
            "reimported_origin_verified": (
                _again.__spec__ is not None
                and _os.path.abspath(_again.__spec__.origin) == _stdlib_re_origin
            ),
})
_observation.update({"actual_execution": True,
                         "stdlib_owner": _sys.modules["re"] is _re,
                         "variant": 0})
_cohort = "synthetic"
_v = 0
_record = {"case_id": _case["case_id"], "cohort": _cohort,
           "ordinal": _case["ordinal"], "seed": _case["seed"],
           "variant": _v, "status": "PASS", "actual_exec": True,
           "candidate_imports": 0, "locale_unchanged": True,
           "stdlib_origin_verified": True, "pinned_executable_verified": True,
           "observation": _observation}
'''


def synthetic_case(index: int) -> dict[str, Any]:
    require(type(index) is int and 0 <= index < CASE_COUNT,
            "require a source-only original synthetic case")
    cohort = ("repeated-interpreter-creation-and-destruction"
              if index < FRESH_CASE_COUNT
              else "source-only-cohort-" + str(index // 8))
    return {
        "case_id": "synthetic-case-" + str(index).zfill(3),
        "cohort": cohort, "ordinal": index,
        "seed": 900_000 + index, "variant": index % 8,
    }


def synthetic_reference(index: int) -> dict[str, Any]:
    case = synthetic_case(index)
    return {
        **case, "status": "PASS", "actual_exec": True,
        "candidate_imports": 0, "locale_unchanged": True,
        "stdlib_origin_verified": True, "pinned_executable_verified": True,
        "observation": {
            "owner_state_intact": True,
            **{name: True for name in RENAME_FIELDS},
            "capture": index, "variant": case["variant"],
        },
    }


def synthetic_pins(spec: FamilySpec) -> dict[str, str]:
    source = sha256((spec.name + ":source").encode("ascii"))
    engine = sha256((spec.name + ":engine").encode("ascii"))
    bridge = (engine if spec.name == "c"
              else sha256((spec.name + ":bridge").encode("ascii")))
    return {"source": source, "native_engine": engine,
            "native_bridge": bridge}


def synthetic_candidate(index: int, spec: FamilySpec) -> dict[str, Any]:
    original = synthetic_reference(index)
    pins = synthetic_pins(spec)
    return {
        **project_reference_record(original),
        "candidate_family": spec.name, "candidate_module": spec.adapter_module,
        "candidate_source_sha256": pins["source"],
        "candidate_engine_sha256": pins["native_engine"],
        "candidate_bridge_sha256": pins["native_bridge"],
        "candidate_origin_verified": True, "candidate_import_count": 1,
        "original_matcher_calls": 0, "external_engine_imports": 0,
        "cross_candidate_imports": 0, "foreign_native_loads": 0,
    }


def synthetic_ledger(
    case: Mapping[str, Any], row: dict[str, Any], owner: str,
    interpreter_id: int,
) -> dict[str, Any]:
    payload = canonical_line(row)
    reader, writer = 42, 43
    return {
        "case_id": case["case_id"], "owner": owner,
        "interpreter_id": interpreter_id,
        "reached_eof": True, "all_descriptors_closed": True,
        "descriptor_events": [
            {"role": "reader", "action": "open", "fd": reader,
             "status": "PASS"},
            {"role": "writer", "action": "open", "fd": writer,
             "status": "PASS"},
            {"role": "writer", "action": "close", "fd": writer,
             "status": "PASS"},
            {"role": "reader", "action": "read", "fd": reader,
             "requested_bytes": MAX_PIPE_BYTES,
             "returned_bytes": len(payload), "status": "PASS"},
            {"role": "reader", "action": "read", "fd": reader,
             "requested_bytes": MAX_PIPE_BYTES,
             "returned_bytes": 0, "status": "PASS"},
            {"role": "reader", "action": "close", "fd": reader,
             "status": "PASS"},
        ],
        "observation_stream": encoded_stream(payload),
    }


def synthetic_arguments(spec: FamilySpec) -> list[str]:
    pins = synthetic_pins(spec)
    owners = []
    for relative in spec.source_owners:
        expected = (pins["source"] if relative == spec.adapter_relative
                    else sha256(relative.encode("ascii")))
        owners.extend(["--owned-source-sha256", relative + "=" + expected])
    fixed = [
        "--record-candidate", "--family", spec.name,
        "--label", "source-only-control",
        "--source-sha256", "a" * 64,
        "--protocol-sha256", "b" * 64,
        "--explanation-sha256", "c" * 64,
        "--build-label", "source-only-build",
        "--build-source-sha256", BUILD_V2_SOURCE_SHA256,
        "--build-protocol-sha256", BUILD_V2_PROTOCOL_SHA256,
        "--build-archive-sha256", "d" * 64,
        "--build-receipt-sha256", "e" * 64,
        "--activation-root", ACTIVATION_PREFIX + spec.name + "-synthetic",
        "--activation-source-sha256", "f" * 64,
        "--activation-protocol-sha256", "1" * 64,
        "--activation-report-sha256", "2" * 64,
        "--activation-receipt-sha256", "3" * 64,
        "--candidate-source-sha256", pins["source"],
        "--native-engine-sha256", pins["native_engine"],
        "--native-bridge-sha256", pins["native_bridge"],
    ]
    return fixed + owners


def synthetic_elf() -> dict[str, Any]:
    records = [
        {"index": 0, "section": "UND", "name": None, "raw_name": None,
         "version": None},
        {"index": 1, "section": "1", "name": "PyInit__vm_native",
         "raw_name": "PyInit__vm_native", "version": None},
        {"index": 2, "section": "UND", "name": "malloc",
         "raw_name": "malloc@GLIBC_2.2.5", "version": "GLIBC_2.2.5"},
    ]
    return {
        "role": "extension", "undefined": ["malloc"],
        "exports": ["PyInit__vm_native"],
        "symbol_count": 3, "versioned_symbol_count": 1,
        "symbol_records": records,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
    }


def self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "require individually named synthetic positive controls")
        require(condition is True,
                "a genuine synthetic positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Callable[[], Any]) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "require individually named synthetic hostile controls")
        try:
            operation()
        except (SubinterpreterGateError, OSError, ValueError, TypeError,
                KeyError, AttributeError, UnicodeError, RecursionError,
                OverflowError, SyntaxError, binascii.Error):
            rejected.append(name)
            return
        raise SubinterpreterGateError(
            "an unsafe synthetic interpreter control was accepted: " + name
        )

    with SourceOnlyBoundary() as boundary:
        protocol = synthetic_protocol()
        accept("complete-strict-versioned-protocol",
               validate_protocol_document(protocol) is protocol)
        accept("isolated-stable-python-source-pin",
               protocol["python"]["sha256"] == PINNED_PYTHON_SHA256)
        accept("published-strict-v2-source-build-freeze",
               protocol["source_build"]["candidate_authorization"]["status"]
               == "V2_PUBLISHED_NO_FAMILY_BUILDS")
        accept("historical-only-nonqualifying-v1-build",
               protocol["source_build"]["published_before_controller_freeze"]
               ["completed_family_count"] == 1
               and protocol["source_build"]["candidate_authorization"]
               ["version_1_can_authorize_candidate"] is False)
        accept("immutable-canonical-guard-required",
               protocol["canonical_activation"]
               ["frozen_guard_root_mutation_allowed"] is False)
        accept("canonical-recovery-and-backup-required",
               protocol["canonical_activation"]
               ["transactional_rollback_required"] is True
               and protocol["canonical_activation"]
               ["complete_reversible_native_backup_required"] is True)
        accept("all-five-canonical-original-guards-pinned",
               len(protocol["canonical_activation"]
                   ["canonical_frozen_guard_source_sha256"]) == 5)
        accept("exact-no-newline-reference-digests-differ",
               PROJECTED_REFERENCE_SHA256 != REFERENCE_RECORDS_SHA256
               and not canonical(protocol).endswith(b"\n"))
        accept("exact-frozen-derived-program-pin",
               protocol["reference"]["adapted_program_sha256"]
               == ADAPTED_PROGRAM_SHA256
               and protocol["reference"]["adapted_program_bytes"]
               == ADAPTED_PROGRAM_BYTES)
        accept("genuine-256-kib-original-pipe-limit",
               MAX_PIPE_BYTES == 256 * 1024)
        accept("bounded-correctness-subprocess-timeouts",
               PROCESS_TIMEOUT_SECONDS == 180 and PROCESS_CLEANUP_SECONDS == 15)
        accept("source-only-canonical-json-round-trip",
               decode_document(canonical_line(protocol),
                               "synthetic protocol", newline=True) == protocol)
        accept("source-only-pretty-protocol-round-trip",
               validate_protocol_document(decode_source_json(
                   json.dumps(protocol, indent=2).encode("utf-8"),
                   "synthetic pretty frozen protocol",
               )) == protocol)
        for name, raw, newline in (
            ("duplicate-json-keys", b'{"a":1,"a":2}', False),
            ("nonfinite-json-number", b'{"a":NaN}', False),
            ("positive-infinite-json", b'{"a":Infinity}', False),
            ("negative-infinite-json", b'{"a":-Infinity}', False),
            ("uncanonical-json-whitespace", b'{ "a": 1 }', False),
            ("json-unexpected-trailing-newline", b'{"a":1}\n', False),
            ("json-missing-required-newline", b'{"a":1}', True),
            ("json-hidden-suffix", b'{"a":1}\nhidden', True),
            ("json-invalid-utf8", b'\xff', False),
            ("json-surrogate", b'{"a":"\\ud800"}', False),
        ):
            reject(name, lambda raw=raw, newline=newline:
                   decode_document(raw, "synthetic hostile document",
                                   newline=newline))
        reject("pretty-source-duplicate-keys",
               lambda: decode_source_json(b'{"a":1,"a":2}', "synthetic"))

        def mutate_protocol(section: str, key: str, value: Any) -> None:
            changed = copy.deepcopy(protocol)
            changed[section][key] = value
            validate_protocol_document(changed)

        attacks = (
            ("python", "isolated", 1),
            ("python", "bytecode_writes", 0),
            ("phase1", "full_suite_count", 13.0),
            ("phase1", "full_case_execution_denominator", 31237.0),
            ("controller", "source_path", "tools/substitute.py"),
            ("controller", "source_sha256_mode", "guessed"),
            ("controller", "protocol_sha256_mode", "optional"),
            ("controller", "explanation_sha256_mode", "optional"),
            ("reference", "case_count", 127),
            ("reference", "case_count", 128.0),
            ("reference", "adapted_program_bytes", ADAPTED_PROGRAM_BYTES + 1),
            ("reference", "adapted_program_sha256", "0" * 64),
            ("reference", "projected_reference_records_sha256", "0" * 64),
            ("source_build", "actual_published_selected_family_build_required", 1),
            ("independence_audit", "persistent_per_interpreter_v5_guard_required", 1),
            ("original_guard", "persistent_guard_per_interpreter", 1),
            ("original_guard", "public_re_alias_is_original_stdlib", 0),
            ("lifecycle", "actual_case_interpreter_exec_calls", 393),
            ("lifecycle", "actual_initialization_interpreter_exec_calls", 10),
            ("lifecycle", "actual_guard_cleanup_interpreter_exec_calls", 10),
            ("lifecycle", "actual_interpreters_created", 10),
            ("lifecycle", "actual_interpreters_destroyed", 10),
            ("lifecycle", "all_real_pipes_read_to_eof", 1),
            ("canonical_activation", "frozen_guard_root_mutation_allowed", True),
            ("canonical_activation", "transactional_rollback_required", False),
            ("canonical_activation", "complete_reversible_native_backup_required", False),
            ("canonical_activation", "verified_transactionally_activated_repo_binary_required", False),
            ("boundaries", "hidden_cases_read", False),
            ("boundaries", "benchmark_files_read", 1),
            ("boundaries", "final_holdout_opened", 0),
            ("boundaries", "final_winner_selected", 0),
        )
        for attack_index, (section, key, value) in enumerate(attacks):
            reject("protocol-" + section + "-" + key
                   + "-" + str(attack_index),
                   lambda section=section, key=key, value=value:
                   mutate_protocol(section, key, value))
        for original, replacement in RENAME_FIELDS.items():
            def missing(original: str = original) -> None:
                changed = copy.deepcopy(protocol)
                del changed["identity_projection"][
                    "lossless_observation_field_renames"
                ][original]
                validate_protocol_document(changed)

            def collided(original: str = original) -> None:
                changed = copy.deepcopy(protocol)
                changed["identity_projection"]
                ["lossless_observation_field_renames"][original] = (
                    "engine_module_name_verified"
                )
                validate_protocol_document(changed)

            reject("omitted-identity-" + original, missing)
            if original != "stdlib_re_module":
                reject("collided-identity-" + original, collided)

        fixture_raw = SYNTHETIC_PRODUCER_PROGRAM.encode("utf-8")
        fixture_digest = sha256(fixture_raw)
        for spec in FAMILIES.values():
            pins = synthetic_pins(spec)
            derived = compose_owned_program(
                SYNTHETIC_PRODUCER_PROGRAM, spec, pins,
                expected_source_sha256=fixture_digest,
                expected_source_bytes=len(fixture_raw),
            )
            accept("actual-contextual-producer-transform-" + spec.name,
                   derived["original_sha256"] == fixture_digest
                   and derived["source"].count('_phase2_state["verify"]()') == 2
                   and all(('"' + key + '":') not in derived["source"]
                           for key in RENAME_FIELDS))
            chosen = parse_arguments(synthetic_arguments(spec))
            accept("exact-explicit-canonical-activation-cli-" + spec.name,
                   chosen["family"] == spec.name
                   and chosen["build_source_sha256"] == BUILD_V2_SOURCE_SHA256
                   and chosen["build_protocol_sha256"] == BUILD_V2_PROTOCOL_SHA256)
            accept("exact-independent-family-source-closure-" + spec.name,
                   len(parse_owned_source_pins(spec, chosen["owned_source_sha256"]))
                   == len(spec.source_owners))

            def poison_cli(option: str, replacement: str | None,
                           *, repeat: bool = False,
                           selected: FamilySpec = spec) -> None:
                altered = synthetic_arguments(selected)
                index = altered.index(option)
                if replacement is None:
                    del altered[index:index + 2]
                elif repeat:
                    altered.extend([option, replacement])
                else:
                    altered[index + 1] = replacement
                parse_arguments(altered)

            reject("reject-historical-v1-build-source-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--build-source-sha256", BUILD_SOURCE_SHA256,
                              selected=spec))
            reject("reject-historical-v1-build-protocol-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--build-protocol-sha256", BUILD_PROTOCOL_SHA256,
                              selected=spec))
            for option in ("--build-source-sha256", "--build-protocol-sha256",
                           "--build-archive-sha256", "--build-receipt-sha256",
                           "--activation-root", "--activation-source-sha256",
                           "--activation-protocol-sha256",
                           "--activation-report-sha256",
                           "--activation-receipt-sha256"):
                reject("missing-proof-" + spec.name + "-" + option[2:],
                       lambda option=option, spec=spec:
                       poison_cli(option, None, selected=spec))
            reject("repeated-activation-proof-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--activation-report-sha256", "2" * 64,
                              repeat=True, selected=spec))
            reject("traversing-activation-root-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--activation-root",
                              ACTIVATION_PREFIX + spec.name + "-x/../escape",
                              selected=spec))
            other = "zig" if spec.name != "zig" else "c"
            reject("cross-family-activation-root-" + spec.name,
                   lambda spec=spec, other=other:
                   poison_cli("--activation-root",
                              ACTIVATION_PREFIX + other + "-synthetic",
                              selected=spec))
            reject("missing-owned-source-" + spec.name,
                   lambda spec=spec:
                   poison_cli("--owned-source-sha256", None, selected=spec))
            if spec.name == "c":
                reject("crossed-combined-c-native-owners",
                       lambda spec=spec:
                       poison_cli("--native-bridge-sha256", "4" * 64,
                                  selected=spec))
            else:
                reject("forged-combined-native-owners-" + spec.name,
                       lambda spec=spec:
                       poison_cli("--native-bridge-sha256",
                                  synthetic_pins(spec)["native_engine"],
                                  selected=spec))
            for index in range(CASE_COUNT):
                reference = synthetic_reference(index)
                row = synthetic_candidate(index, spec)
                accept("source-case-" + spec.name + "-" + str(index),
                       canonical(validate_case_record(row, reference, spec, pins))
                       == canonical(project_reference_record(reference)))
                if spec.name == "c":
                    def missing_case(index: int = index) -> None:
                        changed = synthetic_candidate(index, spec)
                        del changed["observation"]
                        validate_case_record(changed, synthetic_reference(index),
                                             spec, pins)

                    def changed_case(index: int = index) -> None:
                        changed = synthetic_candidate(index, spec)
                        changed["observation"]["capture"] += 1
                        validate_case_record(changed, synthetic_reference(index),
                                             spec, pins)

                    reject("omitted-real-observation-" + str(index), missing_case)
                    reject("changed-real-observation-" + str(index), changed_case)

        spec = FAMILIES["c"]
        pins = synthetic_pins(spec)
        baseline = synthetic_reference(0)
        candidate = synthetic_candidate(0, spec)
        for key, poisoned in (
            ("candidate_origin_verified", 1),
            ("candidate_import_count", True),
            ("original_matcher_calls", False),
            ("external_engine_imports", False),
            ("cross_candidate_imports", False),
            ("foreign_native_loads", False),
            ("candidate_family", "rust"),
            ("candidate_module", "candidates.rust_candidate"),
            ("candidate_source_sha256", "0" * 64),
            ("candidate_engine_sha256", "0" * 64),
            ("candidate_bridge_sha256", "0" * 64),
        ):
            def poisoned_candidate(key: str = key, value: Any = poisoned) -> None:
                changed = copy.deepcopy(candidate)
                changed[key] = value
                validate_case_record(changed, baseline, spec, pins)

            reject("candidate-provenance-" + key, poisoned_candidate)
        for field in ("actual_exec", "locale_unchanged",
                      "pinned_executable_verified"):
            def wrong_boolean(field: str = field) -> None:
                changed = copy.deepcopy(candidate)
                changed[field] = 1
                validate_case_record(changed, baseline, spec, pins)

            reject("candidate-boolean-type-" + field, wrong_boolean)
        reject("reference-bool-candidate-counter",
               lambda: project_reference_record(
                   {**baseline, "candidate_imports": False}
               ))

        matrix = [synthetic_case(index) for index in range(CASE_COUNT)]
        records = [synthetic_candidate(index, spec) for index in range(CASE_COUNT)]
        peers = copy.deepcopy(records)
        repeats = copy.deepcopy(records)
        temporary = list(range(200, 200 + FRESH_CASE_COUNT))
        ids = {"A": 101, "B": 102, "C": 103, "temporary": temporary}
        fresh = [copy.deepcopy(records[index])
                 for index in range(FRESH_CASE_COUNT)]
        post = copy.deepcopy(records[-1])
        last = copy.deepcopy(records[-1])
        ledgers: list[dict[str, Any]] = []
        for index, case in enumerate(matrix):
            ledgers.extend((
                synthetic_ledger(case, records[index], "A", ids["A"]),
                synthetic_ledger(case, peers[index], "B", ids["B"]),
                synthetic_ledger(case, repeats[index], "A", ids["A"]),
            ))
        for index in range(FRESH_CASE_COUNT):
            ledgers.append(synthetic_ledger(
                matrix[index], fresh[index], "C", temporary[index],
            ))
        ledgers.extend((
            synthetic_ledger(matrix[-1], post, "A", ids["A"]),
            synthetic_ledger(matrix[-1], last, "C", ids["C"]),
        ))
        validate_pipe_schedule(matrix, ids, ledgers, records, peers, repeats,
                               fresh, post, last)
        accept("complete-genuine-394-source-ordered-pipe-fixture", True)

        def poisoned_pipe(position: int, kind: str) -> None:
            changed = copy.deepcopy(ledgers)
            actual = changed[position]
            if kind == "case":
                actual["case_id"] = "forged-case"
            elif kind == "owner":
                actual["owner"] = "B" if actual["owner"] != "B" else "A"
            elif kind == "interpreter":
                actual["interpreter_id"] = 999_999
            elif kind == "eof":
                actual["descriptor_events"][-2]["returned_bytes"] = 1
            elif kind == "stream":
                actual["observation_stream"] = encoded_stream(b"{}\n")
            elif kind == "open-order":
                events = actual["descriptor_events"]
                events[0], events[1] = events[1], events[0]
            elif kind == "read-fd":
                actual["descriptor_events"][3]["fd"] = 999
            elif kind == "read-role":
                actual["descriptor_events"][3]["role"] = "writer"
            elif kind == "byte-count":
                actual["descriptor_events"][3]["returned_bytes"] += 1
            elif kind == "missing":
                changed.pop(position)
            elif kind == "duplicated":
                changed[position] = copy.deepcopy(
                    changed[(position + 1) % len(changed)]
                )
            elif kind == "close-order":
                events = actual["descriptor_events"]
                events[2], events[-1] = events[-1], events[2]
            else:
                raise SubinterpreterGateError("unknown synthetic ledger attack")
            validate_pipe_schedule(matrix, ids, changed, records, peers,
                                   repeats, fresh, post, last)

        for kind in ("case", "owner", "interpreter", "eof", "stream",
                     "open-order", "read-fd", "read-role", "byte-count",
                     "missing", "duplicated", "close-order"):
            for position, phase in ((0, "first-a"), (1, "first-b"),
                                    (2, "repeated-a"), (384, "fresh"),
                                    (392, "post-b"), (393, "fresh-c")):
                reject("pipe-" + kind + "-" + phase,
                       lambda position=position, kind=kind:
                       poisoned_pipe(position, kind))

        elf = synthetic_elf()
        accept("complete-versioned-eighth-column-elf",
               validate_clean_elf(elf, family="c", kind="extension") is elf)
        for field in ("external_regex_dependency_count",
                      "cross_family_dependency_count"):
            def poisoned_elf_counter(field: str = field) -> None:
                changed = copy.deepcopy(elf)
                changed[field] = False
                validate_clean_elf(changed, family="c", kind="extension")

            reject("forged-bool-elf-counter-" + field,
                   poisoned_elf_counter)
        for name in ("regexec", "regcomp", "regerror", "regfree",
                     "pcre2_match", "onig_search", "hyperscan_open",
                     "re2_compile", "rust_regex_compile", "_sre"):
            def hidden_symbol(name: str = name) -> None:
                forged = copy.deepcopy(elf)
                forged["symbol_records"][2]["name"] = name
                forged["symbol_records"][2]["raw_name"] = name + "@GLIBC_2.2.5"
                forged["undefined"] = [name]
                validate_clean_elf(forged, family="c", kind="extension")

            reject("versioned-forbidden-symbol-" + name, hidden_symbol)
        for name, change in (
            ("v1-version-index-pseudo-symbol", "(2)"),
            ("omitted-real-symbol-record", None),
        ):
            def forged_elf(change: Any = change) -> None:
                forged = copy.deepcopy(elf)
                if change is None:
                    forged["symbol_records"].pop()
                else:
                    forged["symbol_records"][2]["name"] = change
                    forged["symbol_records"][2]["raw_name"] = change
                    forged["undefined"] = [change]
                validate_clean_elf(forged, family="c", kind="extension")

            reject(name, forged_elf)

        for name, action in (
            ("real-builtin-open", lambda: builtins.open("/tmp/blocked", "rb")),
            ("real-io-open", lambda: io.open("/tmp/blocked", "rb")),
            ("real-open-code", lambda: io.open_code("/tmp/blocked")),
            ("real-os-open", lambda: os.open("/tmp/blocked", os.O_RDONLY)),
            ("real-os-read", lambda: os.read(0, 1)),
            ("real-os-write", lambda: os.write(1, b"blocked")),
            ("real-os-stat", lambda: os.stat("/tmp/blocked")),
            ("real-os-lstat", lambda: os.lstat("/tmp/blocked")),
            ("real-os-pipe", lambda: os.pipe()),
            ("real-path-read", lambda: Path("/tmp/blocked").read_bytes()),
            ("real-path-write", lambda: Path("/tmp/blocked").write_bytes(b"x")),
            ("real-path-resolve", lambda: Path("/tmp/blocked").resolve()),
            ("real-path-exists", lambda: Path("/tmp/blocked").exists()),
            ("real-file-unlink", lambda: os.unlink("/tmp/blocked")),
            ("real-file-rename", lambda: os.rename("/tmp/a", "/tmp/b")),
            ("real-file-replace", lambda: os.replace("/tmp/a", "/tmp/b")),
            ("real-directory-create", lambda: os.mkdir("/tmp/blocked")),
            ("real-directory-remove", lambda: os.rmdir("/tmp/blocked")),
            ("real-file-fsync", lambda: os.fsync(0)),
            ("real-isolated-process", lambda: subprocess.Popen(["blocked"])),
            ("real-process-run", lambda: subprocess.run(["blocked"])),
            ("real-process-system", lambda: os.system("blocked")),
            ("real-process-popen", lambda: os.popen("blocked")),
            ("real-process-fork", lambda: os.fork()),
            ("real-thread-start", lambda: threading.Thread(target=lambda: None).start()),
            ("real-dynamic-candidate-import",
             lambda: importlib.import_module("candidates.vm_candidate")),
            ("real-builtin-candidate-import",
             lambda: builtins.__import__("candidates.vm_candidate")),
            ("real-interpreter-provider-import",
             lambda: builtins.__import__("concurrent.interpreters")),
            ("real-native-interpreter-import",
             lambda: builtins.__import__("_interpreters")),
            ("real-parent-fromlist-interpreter-import",
             lambda: builtins.__import__("concurrent", fromlist=("interpreters",))),
            ("real-ctypes-import", lambda: builtins.__import__("ctypes")),
            ("real-native-ctypes-import", lambda: builtins.__import__("_ctypes")),
            ("real-external-cffi-import", lambda: builtins.__import__("cffi")),
            ("real-multiprocessing-import",
             lambda: builtins.__import__("multiprocessing")),
            ("real-network-import", lambda: builtins.__import__("socket")),
            ("real-irrevocable-audit-hook",
             lambda: sys.addaudithook(lambda event, arguments: None)),
            ("real-process-locale-change",
             lambda: locale.setlocale(locale.LC_CTYPE, "C")),
            ("real-garbage-collection", lambda: gc.collect()),
            ("real-wall-clock", lambda: time.time()),
            ("real-monotonic-clock", lambda: time.monotonic()),
            ("real-performance-clock", lambda: time.perf_counter()),
            ("real-process-clock", lambda: time.process_time()),
        ):
            reject("source-boundary-" + name, action)

        accept("strictly-synthetic-file-boundary-covered",
               boundary.attempts["file_reads"] > 0)
        accept("strictly-synthetic-pipe-boundary-covered",
               boundary.attempts["pipes"] > 0)
        accept("strictly-synthetic-candidate-boundary-covered",
               boundary.attempts["candidate_imports"] > 0)
        accept("strictly-synthetic-interpreter-boundary-covered",
               boundary.attempts["interpreter_imports"] > 0)
        accept("strictly-synthetic-worker-boundary-covered",
               boundary.attempts["processes"] > 0)
        accept("strictly-synthetic-native-library-boundary-covered",
               boundary.attempts["native_library_loads"] > 0)
        accept("strictly-synthetic-network-boundary-covered",
               boundary.attempts["network_requests"] > 0)
        accept("strictly-synthetic-clock-boundary-covered",
               boundary.attempts["clock_samples"] > 0)
        accept("strictly-synthetic-warning-and-locale-boundary-covered",
               boundary.attempts["locale_changes"] > 0)
        accept("strictly-synthetic-audit-hook-boundary-covered",
               boundary.attempts["audit_hooks"] > 0)

    require(len(accepted) >= 400 and len(rejected) >= 350,
            "run all complete original synthetic positive and hostile controls")
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "source_only": True,
        "accepted_controls": len(accepted),
        "rejected_hostile_controls": len(rejected),
        "accepted": accepted, "rejected": rejected,
        "protocol_schema": PROTOCOL_SCHEMA,
        "matrix_case_count": CASE_COUNT,
        "expected_case_interpreter_exec_calls": CASE_EXEC_COUNT,
        "expected_initialization_interpreter_exec_calls": INTERPRETER_COUNT,
        "expected_guard_cleanup_interpreter_exec_calls": INTERPRETER_COUNT,
        "actual_case_interpreter_exec_calls": 0,
        "actual_initialization_interpreter_exec_calls": 0,
        "actual_guard_cleanup_interpreter_exec_calls": 0,
        "actual_interpreters_created": 0,
        "actual_interpreters_destroyed": 0,
        "actual_interpreter_exec_calls": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_libraries_loaded": 0,
        "actual_source_builds_started": 0,
        "actual_canonical_activations_started": 0,
        "actual_files_read": 0, "actual_files_written": 0,
        "actual_pipes_opened": 0, "actual_threads_started": 0,
        "actual_audit_hooks_installed": 0,
        "actual_locale_changes": 0,
        "actual_garbage_collections": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "network_requests": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "source_only_blocked_attempts": dict(boundary.attempts),
        "published_source_build_v2_status": "V2_PUBLISHED_NO_FAMILY_BUILDS",
        "published_source_build_v2_family_count": 0,
        "historical_v1_completed_family_count": 1,
        "canonical_activation_status": "REQUIRED_NOT_PUBLISHED",
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        selected = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if selected["mode"] == "self-test":
            result = self_test()
        elif selected["mode"] == "record-candidate":
            result = run_candidate(selected)
        else:
            result = internal_worker(selected)
        sys.stdout.buffer.write(canonical_line(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except (SubinterpreterGateError, OSError, ValueError, TypeError,
            UnicodeError, RecursionError, OverflowError) as error:
        result: dict[str, Any] = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__name__, "error_message": str(error),
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        }
        if isinstance(error, ActualCaseFailure):
            result["actual_failure"] = error.details
        sys.stdout.buffer.write(canonical_line(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
