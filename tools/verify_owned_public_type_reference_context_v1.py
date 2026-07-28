#!/usr/bin/env python3
"""Freeze and reproduce Python's public regex tests in one honest context."""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import importlib.machinery
import io
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, NamedTuple, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase1-owned-public-type-reference-context-v1"
VERSION = 1
SOURCE = "tools/verify_owned_public_type_reference_context_v1.py"
PROTOCOL = "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md"
CONTRACT = "oracle/phase1/p0-public-type-reference-context-v1.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
ORACLE_MODULE = "tools.independent_public_type_identity_serialization_v1"
PUBLIC_MATRIX_SHA256 = "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
PUBLIC_CASE_COUNT = 6_912
ORIGINAL_CASE_COUNT = 31_237
ORIGINAL_SUITE_COUNT = 13
PRIVATE_WAIVER_COUNT = 13
PUBLISHED_SEED = 6_077_977_430_793_212_465
COHORT = "cache-pattern-type-separation"
COHORT_CASE_COUNT = 96
CASE_IDS_SHA256 = "a27fa99515fa1deef0253d49c5663a18821a07646cd8fadc5ebb5330d8cec35e"
CASE_IDS_CANONICAL_SHA256 = "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
COHORT_MATRIX_SHA256 = "09b5d7cb665af227b8d6c733c795d68f9a1e22c62956b9d64105a9234af6abca"
OLD_COHORT_RECORDS_SHA256 = "df849727d5aa74cbec19950c2d56764bd592404b76c49abe87418bccd3a5013a"
NAMED_COHORT_RECORDS_SHA256 = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
FIRST_CASE = "cache-pattern-type-separation/000"
LAST_CASE = "cache-pattern-type-separation/095"
FIRST_OLD_RECORD_SHA256 = "33d63c67211bba811706bef2457230573cd13b498642c5ba0fa27b2e5091688c"
FIRST_NAMED_RECORD_SHA256 = "7d8752048b7a3520b2657a21c3fe03722a507e0914d777404f16ffeec60d2292"
FIRST_RUST_MISMATCH_SHA256 = "3ec02cbb18243fd1f7a170146c22c82c00560a8b46447b9f87f2b1fb2e5130bd"
FIRST_C_MISMATCH_SHA256 = "63e4cd7d491fac94c70df35f5c83ba96f5fdc0aceb3d5d212b92e90d59575b34"
EVIDENCE_DIRECTORY = "oracle/phase1/evidence"
MAX_OWNER_BYTES = 40 * 1024 * 1024
MAX_WORKER_BYTES = 32 * 1024 * 1024
MAX_WORKER_STDERR_BYTES = 2 * 1024 * 1024
MAX_REPORT_BYTES = 96 * 1024 * 1024
MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 600
ROLES = ("reference-a", "reference-b")
DENIED_CANDIDATE_PREFIXES = (
    "candidates", "regex", "re2", "google_re2", "rure", "pcre2",
)


class ContextError(Exception):
    """An original source, record, boundary, or actual worker was invalid."""


class ForbiddenEffect(ContextError):
    """A source-only control attempted an actual outside effect."""


class ReferenceWorkerFailure(ContextError):
    """Preserve the real attempted process before rejecting its observation."""

    def __init__(self, message: str, evidence: dict[str, Any]) -> None:
        super().__init__(message)
        self.evidence = evidence


class Owner(NamedTuple):
    path: str
    sha256: str
    size: int


OWNERS: dict[str, Owner] = {
    "goal": Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
    "original_manifest": Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632),
    "original_protocol": Owner("oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392),
    "public_oracle": Owner("tools/independent_public_type_identity_serialization_v1.py", "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20", 150015),
    "candidate_gate": Owner("tools/run_frozen_p0_candidate_v1.py", "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8", 104772),
    "original_producer": Owner("tools/run_owned_six_family_original_p0_producer_v3.py", "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555),
    "original_public_recorder": Owner("tools/record_independent_public_type_identity_serialization_v1.py", "ee3e6fc00991758fee93b710a63dad9094f881f1ea57777cae2415397f752eae", 220890),
    "actual_context_falsification": Owner("oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json", "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670", 3892),
    "old_public_archive": Owner("experiments/rust_public_practice_v1/public-type-identity-serialization-v1-shared-suite-v1.json.gz", "8956c0b26e074d1537a47047062fb51e11d3f0196dc97ce4a6e24d2ae45128e2", 2926031),
    "old_public_receipt": Owner("experiments/rust_public_practice_v1/public-type-identity-serialization-v1-shared-suite-v1-publication-receipt.json", "6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd", 7596),
    "rust_matching_archive": Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures.json.gz", "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f", 3663299),
    "rust_matching_receipt": Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json", "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3", 4674),
    "c_matching_archive": Owner("oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures.json.gz", "8515dfecc873eaea60d0f945e1081ff59a65bda39802e65605198617462a1c9d", 5767499),
    "c_matching_receipt": Owner("oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json", "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9", 3482),
    "zig_matching_archive": Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures.json.gz", "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b", 3722337),
    "zig_matching_receipt": Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures-publication-receipt.json", "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96", 4111),
    "rust_v13_build_archive": Owner("oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0.json.gz", "c201c014f55a51454baab77d2148dc39d6024bae3273242d6eb1f1b43f419f6a", 108985),
    "rust_v13_build_receipt": Owner("oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0-publication-receipt.json", "4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805", 2437),
    "signature_archive": Owner("oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6.json.gz", "7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c", 8538),
    "signature_receipt": Owner("oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json", "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334", 3533),
    "python": Owner(PYTHON, PYTHON_SHA256, 32387816),
    "stdlib_re": Owner("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py", "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35", 17876),
    "stdlib_compiler": Owner("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/_compiler.py", "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91", 26855),
    "stdlib_parser": Owner("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/_parser.py", "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4", 40353),
    "stdlib_constants": Owner("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/_constants.py", "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b", 6036),
}


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ContextError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, ensure_ascii=True, allow_nan=False,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise ContextError("a reference document is not canonical JSON") from error


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash only complete, exact bytes")
    return hashlib.sha256(value).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and len(set(value)) > 1
        and all(character in "0123456789abcdef" for character in value),
        "an independently pinned SHA-256 is mandatory: " + label,
    )
    return value


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "duplicate JSON keys conceal a changed reference")
        result[key] = value
    return result


def decode_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_REPORT_BYTES,
            "bound the complete JSON owner: " + label)
    try:
        document = json.loads(
            raw, object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                ContextError("nonfinite JSON is forbidden: " + label)
            ),
        )
    except (ValueError, TypeError, UnicodeError) as error:
        raise ContextError("invalid complete JSON owner: " + label) from error
    require(type(document) is dict, "require a complete JSON object: " + label)
    return document


def verify_runtime() -> None:
    require(sys.version_info[:3] == (3, 14, 6),
            "only pinned CPython 3.14.6 is an admissible reference")
    require(os.path.abspath(sys.executable) == PYTHON,
            "use the independently pinned CPython executable")
    require(sys.flags.isolated == 1 and sys.dont_write_bytecode,
            "invoke pinned Python with -I -B")


def case_ids() -> list[str]:
    return [COHORT + "/" + f"{index:03d}"
            for index in range(COHORT_CASE_COUNT)]


def owner_document(item: Owner) -> dict[str, Any]:
    return {"path": item.path, "sha256": item.sha256, "bytes": item.size}


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "prospective reference-context source")
    checked_digest(protocol_pin, "prospective reference-context protocol")
    ids = case_ids()
    require(digest(canonical(ids)) == CASE_IDS_CANONICAL_SHA256,
            "never change an original public-case identifier")
    compact_ids = json.dumps(ids, sort_keys=True, ensure_ascii=True,
                             separators=(",", ":")).encode("ascii")
    require(digest(compact_ids) == CASE_IDS_SHA256,
            "retain the independently witnessed compact case vector")
    return {
        "schema": SCHEMA + "-frozen-contract",
        "version": VERSION,
        "phase": "CORRECTNESS ORACLE",
        "status": "SOURCE FROZEN; CORRECTED TWO-REFERENCE BASELINE NOT RUN",
        "source": {"path": SOURCE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL, "sha256": protocol_pin},
        "python": {"version": "3.14.6", **owner_document(OWNERS["python"])},
        "goal": owner_document(OWNERS["goal"]),
        "original_p0": {
            "case_execution_denominator": ORIGINAL_CASE_COUNT,
            "suite_count": ORIGINAL_SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "denominator_changed": False,
            "cases_removed": 0,
            "new_private_waivers": 0,
            "manifest": owner_document(OWNERS["original_manifest"]),
            "protocol": owner_document(OWNERS["original_protocol"]),
        },
        "original_public_suite": {
            "suite": "public_types_v1",
            "case_count": PUBLIC_CASE_COUNT,
            "matrix_sha256": PUBLIC_MATRIX_SHA256,
            "published_seed_decimal": str(PUBLISHED_SEED),
            "oracle": owner_document(OWNERS["public_oracle"]),
            "candidate_gate": owner_document(OWNERS["candidate_gate"]),
            "six_family_producer": owner_document(OWNERS["original_producer"]),
            "historical_recorder": owner_document(OWNERS["original_public_recorder"]),
            "historical_baseline": {
                "status": "FALSIFIED FOR CANDIDATE-FACING EXECUTION CONTEXT",
                "original_public_reference_status": "PASS IN SCRIPT CONTEXT",
                "full_vector_sha256": "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
                "actual_reference_process_ids": [82, 83],
                "archive": owner_document(OWNERS["old_public_archive"]),
                "receipt": owner_document(OWNERS["old_public_receipt"]),
                "archive_inflated_by_source_verification": False,
            },
        },
        "independently_reproduced_self_oracle_failure": {
            "status": "FAIL",
            "actual_falsification_evidence": owner_document(OWNERS["actual_context_falsification"]),
            "actual_isolated_stdlib_diagnostic_pid": 80,
            "cohort": COHORT,
            "case_count": COHORT_CASE_COUNT,
            "case_ids": ids,
            "case_ids_compact_sha256": CASE_IDS_SHA256,
            "case_ids_oracle_canonical_sha256": CASE_IDS_CANONICAL_SHA256,
            "original_cohort_matrix_sha256": COHORT_MATRIX_SHA256,
            "text_subclass_case_count": 48,
            "bytes_subclass_case_count": 48,
            "only_false_difference_path": "outcome.value.items[2].module",
            "script_context_fixture_module": "__main__",
            "candidate_facing_fixture_module": ORACLE_MODULE,
            "script_context_reference_subset_sha256": OLD_COHORT_RECORDS_SHA256,
            "candidate_context_stdlib_subset_sha256": NAMED_COHORT_RECORDS_SHA256,
            "historical_rust_subset_sha256": NAMED_COHORT_RECORDS_SHA256,
            "all_96_named_context_stdlib_records_equal_historical_rust": True,
            "first_case": FIRST_CASE,
            "last_case": LAST_CASE,
            "first_script_context_reference_record_sha256": FIRST_OLD_RECORD_SHA256,
            "first_named_context_stdlib_record_sha256": FIRST_NAMED_RECORD_SHA256,
            "first_rust_mismatch_sha256": FIRST_RUST_MISMATCH_SHA256,
            "canonical_hash_includes_one_trailing_newline": True,
            "historical_rust_matching_archive": owner_document(OWNERS["rust_matching_archive"]),
            "historical_rust_matching_receipt": owner_document(OWNERS["rust_matching_receipt"]),
            "historical_matching_archives_inflated_by_source_verification": 0,
            "candidate_imports_in_actual_stdlib_diagnostic": 0,
            "candidate_workers_in_actual_stdlib_diagnostic": 0,
            "additional_reference_workers_in_actual_stdlib_diagnostic": 0,
        },
        "preserved_real_candidate_differences": {
            "artifact_correction_is_not_a_candidate_waiver": True,
            "c": {
                "status": "FAIL",
                "semantic_mismatch_count": 1230,
                "verified_passing_case_count": 7325,
                "cache_case_count": 96,
                "first_case": FIRST_CASE,
                "first_mismatch_sha256": FIRST_C_MISMATCH_SHA256,
                "real_difference_path": "outcome.value.items[1].value",
                "expected_subclass_equality": True,
                "actual_subclass_equality": False,
                "fixture_module_difference_is_also_present": True,
                "matching_archive": owner_document(OWNERS["c_matching_archive"]),
                "matching_receipt": owner_document(OWNERS["c_matching_receipt"]),
            },
            "zig": {
                "status": "FAIL",
                "semantic_mismatch_count": 1764,
                "verified_passing_case_count": 3711,
                "cache_cohort_observations": "NOT ESTABLISHED",
                "matching_archive": owner_document(OWNERS["zig_matching_archive"]),
                "matching_receipt": owner_document(OWNERS["zig_matching_receipt"]),
            },
            "historical_rust": {
                "status": "FAIL",
                "semantic_mismatch_count": 1036,
                "verified_passing_case_count": 8965,
                "full_matching_denominator": ORIGINAL_CASE_COUNT,
            },
            "corrected_rust_v13": {
                "build_status": "PASS",
                "actual_compiler_process_count": 28,
                "matching_status": "NOT RUN",
                "build_archive": owner_document(OWNERS["rust_v13_build_archive"]),
                "build_receipt": owner_document(OWNERS["rust_v13_build_receipt"]),
            },
        },
        "prospective_correction": {
            "status": "NOT RUN",
            "method": "import the exact original public evaluator by its canonical named module in both independent CPython reference workers",
            "worker_roles": list(ROLES),
            "required_actual_distinct_reference_process_count": 2,
            "cases_per_reference_worker": PUBLIC_CASE_COUNT,
            "reference_records_must_agree": True,
            "preserve_full_original_matrix": True,
            "preserve_published_seed": True,
            "preserve_all_96_original_case_ids": True,
            "preserve_text_and_bytes_subclasses": True,
            "discard_record_fields": False,
            "normalize_away_real_subclass_equality": False,
            "evaluate_any_candidate": False,
            "load_any_candidate": False,
            "external_regex_package_allowed": False,
            "existing_reference_archives_inflated": False,
            "future_evidence_directory": EVIDENCE_DIRECTORY,
            "exclusive_publication": "O_CREAT|O_EXCL|O_NOFOLLOW; mode 0600; file and directory fsync",
            "recovery_root_parent": "/tmp",
            "recovery_root_prefix": "rebar-phase1-public-type-reference-context-v1-",
            "recovery_root_mode": "0700",
            "recovery_journal_mode": "0600",
            "recovery_snapshots": "exclusive append-only complete fsynced snapshots before each attempt, after each start, after each complete stream, before publication, and after each publication",
            "attempted_started_completed_and_validated_counts_are_distinct": True,
            "capture_failed_worker_pid_before_validation": True,
            "preserve_complete_bounded_worker_stdout_and_stderr": True,
            "preserve_timeout_and_process_spawn_failure": True,
            "preserve_archive_without_receipt_after_publication_failure": True,
            "maximum_worker_stdout_bytes": MAX_WORKER_BYTES,
            "maximum_worker_stderr_bytes": MAX_WORKER_STDERR_BYTES,
            "maximum_report_bytes": MAX_REPORT_BYTES,
            "maximum_archive_bytes": MAX_ARCHIVE_BYTES,
            "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        },
        "preserved_separate_signature_reference": {
            "status": "PASS",
            "additional_cases": 50,
            "included_in_original_denominator": False,
            "candidate_status": "NOT RUN",
            "archive": owner_document(OWNERS["signature_archive"]),
            "receipt": owner_document(OWNERS["signature_receipt"]),
        },
        "source_only_boundaries": {
            "corrected_reference_workers_started": 0,
            "candidate_processes_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "network_requests": 0,
            "threads_started": 0,
            "archive_decompressions": 0,
            "evidence_files_created": 0,
            "clock_samples": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "holdout": "NOT OPENED",
            "holdout_planned_case_count": 4194304,
            "holdout_frozen": False,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {name: 0 for name in (
            "filesystem", "write", "process", "import", "network",
            "thread", "clock", "native", "lock", "signal", "decompression",
        )}

    def deny(self, owner: Any, name: str, kind: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise ForbiddenEffect("physically blocked source-only " + kind + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyWall:
        actions: list[tuple[Any, tuple[str, ...], str]] = [
            (builtins, ("open",), "filesystem"),
            (builtins, ("__import__",), "import"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir", "listdir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "resolve", "iterdir"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename", "replace", "fsync", "symlink", "link"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename", "replace", "touch"), "write"),
            (tempfile, ("mkdtemp", "mkstemp", "TemporaryFile", "NamedTemporaryFile"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output", "_fork_exec"), "process"),
            (os, ("fork", "system", "posix_spawn", "posix_spawnp",
                  "execv", "execve", "execl", "execle", "execlp", "execlpe",
                  "execvp", "execvpe", "spawnv", "spawnve", "spawnvp",
                  "spawnvpe"), "process"),
            (importlib, ("import_module",), "import"),
            (importlib.machinery.SourceFileLoader,
             ("create_module", "exec_module", "load_module"), "import"),
            (importlib.machinery.SourcelessFileLoader,
             ("create_module", "exec_module", "load_module"), "import"),
            (importlib.machinery.ExtensionFileLoader,
             ("create_module", "exec_module", "load_module"), "native"),
            (importlib.machinery.BuiltinImporter,
             ("create_module", "exec_module", "load_module"), "native"),
            (importlib.machinery.FrozenImporter,
             ("create_module", "exec_module", "load_module"), "import"),
            (socket, ("socket", "create_connection", "getaddrinfo"), "network"),
            (threading, ("_start_joinable_thread", "_start_new_thread"), "thread"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "process_time", "thread_time"), "clock"),
            (ctypes, ("CDLL", "PyDLL", "_dlopen"), "native"),
            (fcntl, ("flock", "lockf"), "lock"),
            (signal, ("signal", "pthread_sigmask", "raise_signal"), "signal"),
            (gzip, ("decompress", "open", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        ]
        native_actions = (
            ("_io", ("open",), "filesystem"),
            ("posix", ("open", "read", "stat", "lstat", "scandir", "listdir"), "filesystem"),
            ("posix", ("write", "mkdir", "unlink", "remove", "rename",
                       "replace", "fsync", "symlink", "link"), "write"),
            ("posix", ("fork", "posix_spawn", "posix_spawnp", "execv",
                       "execve", "spawnv", "spawnve"), "process"),
            ("_posixsubprocess", ("fork_exec",), "process"),
            ("_ctypes", ("dlopen",), "native"),
            ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin",
                      "exec_builtin", "init_frozen"), "native"),
            ("_socket", ("socket", "getaddrinfo"), "network"),
            ("_thread", ("start_new_thread", "start_joinable_thread"), "thread"),
        )
        for module_name, names, kind in native_actions:
            native_module = sys.modules.get(module_name)
            if native_module is not None:
                actions.append((native_module, names, kind))
        for owner, names, kind in actions:
            for name in names:
                self.deny(owner, name, kind)
        return self

    def __exit__(self, *_details: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def synthetic_plan() -> dict[str, Any]:
    rows = []
    for index, identity in enumerate(case_ids()):
        kind = "TextSubclass" if index % 2 == 0 else "BytesSubclass"
        rows.append({
            "case": identity,
            "class_name": kind,
            "script_module": "__main__",
            "reference_a_module": ORACLE_MODULE,
            "reference_b_module": ORACLE_MODULE,
            "historical_rust_module": ORACLE_MODULE,
            "only_difference_path": "outcome.value.items[2].module",
            "real_subclass_equality": True,
        })
    return {
        "roles": [{"role": role, "pid": 41000 + index}
                  for index, role in enumerate(ROLES)],
        "cases": rows,
        "matrix_sha256": PUBLIC_MATRIX_SHA256,
        "cohort_matrix_sha256": COHORT_MATRIX_SHA256,
        "seed": PUBLISHED_SEED,
        "original_denominator": ORIGINAL_CASE_COUNT,
        "suite_count": ORIGINAL_SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "candidate_import_count": 0,
        "holdout_opened": False,
        "c_real_equality": {"expected": True, "actual": False},
        "zig_cache_observation": "NOT ESTABLISHED",
    }


def validate_synthetic_plan(plan: Any) -> dict[str, Any]:
    require(type(plan) is dict, "require the complete self-oracle plan")
    require(plan.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and plan.get("cohort_matrix_sha256") == COHORT_MATRIX_SHA256
            and plan.get("seed") == PUBLISHED_SEED
            and plan.get("original_denominator") == ORIGINAL_CASE_COUNT
            and plan.get("suite_count") == ORIGINAL_SUITE_COUNT
            and plan.get("private_waiver_count") == PRIVATE_WAIVER_COUNT,
            "never change a frozen original case, seed, suite, or denominator")
    require(plan.get("candidate_import_count") == 0
            and plan.get("holdout_opened") is False,
            "a phase-one reference cannot load a candidate or open the holdout")
    require(plan.get("zig_cache_observation") == "NOT ESTABLISHED",
            "never invent an unobserved Zig cache-cohort record")
    equality = plan.get("c_real_equality")
    require(type(equality) is dict and equality.get("expected") is True
            and equality.get("actual") is False,
            "never normalize away an independently observed genuine C mismatch")
    roles = plan.get("roles")
    require(type(roles) is list and len(roles) == 2,
            "require exactly two actual prospective reference roles")
    pids: set[int] = set()
    for index, role in enumerate(roles):
        require(type(role) is dict and role.get("role") == ROLES[index]
                and type(role.get("pid")) is int and role["pid"] > 0
                and role["pid"] not in pids,
                "reject a substituted, reordered, or duplicated reference worker")
        pids.add(role["pid"])
    rows = plan.get("cases")
    require(type(rows) is list and len(rows) == COHORT_CASE_COUNT,
            "preserve all 96 independently witnessed original cases")
    names = {"TextSubclass": 0, "BytesSubclass": 0}
    for index, row in enumerate(rows):
        require(type(row) is dict and row.get("case") == case_ids()[index],
                "reject an omitted, reordered, relabeled, or duplicated cache case")
        expected = "TextSubclass" if index % 2 == 0 else "BytesSubclass"
        require(row.get("class_name") == expected,
                "preserve the real text/bytes subclass fixture")
        names[expected] += 1
        require(row.get("script_module") == "__main__"
                and row.get("reference_a_module") == ORACLE_MODULE
                and row.get("reference_b_module") == ORACLE_MODULE
                and row.get("historical_rust_module") == ORACLE_MODULE
                and row.get("only_difference_path")
                == "outcome.value.items[2].module"
                and row.get("real_subclass_equality") is True,
                "correct only the independently proven fixture-module artifact")
    require(names == {"TextSubclass": 48, "BytesSubclass": 48},
            "require 48 genuine text and 48 genuine bytes subclasses")
    return {"reference_roles": 2, "distinct_reference_pids": len(pids),
            "case_count": len(rows), "subclass_counts": names,
            "real_c_equality_mismatch_preserved": True}


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    expected = contract_document(source_pin, protocol_pin)
    require(digest(canonical(expected)) == checked_digest(contract_pin, "reference-context contract"),
            "reject a substituted exact canonical phase-one contract")
    rejected: list[str] = []
    accepted: list[str] = []
    plan = synthetic_plan()

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except ContextError:
            rejected.append(name)
            return
        raise ContextError("accepted hostile source-only control: " + name)

    with SourceOnlyWall() as wall:
        proof = validate_synthetic_plan(plan)
        accepted.append("two-independent-named-context-references")
        accepted.append("all-original-96-text-and-bytes-cache-cases")
        accepted.append("genuine-c-subclass-equality-difference-preserved")
        faults = exercise_controller_faults(source_pin, protocol_pin,
                                            contract_pin)
        require(faults["simulated_fault_count"] == 6
                and all(value is True for key, value in faults.items()
                        if key != "simulated_fault_count"),
                "exercise real injected process and durable-publication failures")
        accepted.append("injected-popen-spawn-and-real-second-worker-faults")
        accepted.append("injected-real-timeout-and-complete-stream-retention")
        accepted.append("injected-archive-and-receipt-publication-faults")

        def mutated(name: str, edit: Any) -> None:
            def exercise() -> None:
                changed = copy.deepcopy(plan)
                edit(changed)
                validate_synthetic_plan(changed)
            reject(name, exercise)

        for key, bad in (
            ("matrix_sha256", "0" * 64),
            ("cohort_matrix_sha256", "0" * 64),
            ("seed", PUBLISHED_SEED + 1),
            ("original_denominator", ORIGINAL_CASE_COUNT - 1),
            ("suite_count", ORIGINAL_SUITE_COUNT - 1),
            ("private_waiver_count", PRIVATE_WAIVER_COUNT + 1),
            ("candidate_import_count", 1),
            ("holdout_opened", True),
            ("zig_cache_observation", "PASS"),
        ):
            mutated("reject-" + key,
                    lambda changed, field=key, value=bad:
                    changed.__setitem__(field, value))
        for index in range(COHORT_CASE_COUNT):
            mutated("reject-renamed-original-case-" + str(index),
                    lambda changed, number=index:
                    changed["cases"][number].__setitem__("case", "substituted/000"))
            mutated("reject-script-context-reference-" + str(index),
                    lambda changed, number=index:
                    changed["cases"][number].__setitem__("reference_a_module", "__main__"))
        for index in range(2):
            mutated("reject-role-order-" + str(index),
                    lambda changed, number=index:
                    changed["roles"][number].__setitem__("role", "borrowed"))
            mutated("reject-worker-pid-" + str(index),
                    lambda changed, number=index:
                    changed["roles"][number].__setitem__("pid", 0))
        mutated("reject-shared-worker-pid",
                lambda changed: changed["roles"][1].__setitem__(
                    "pid", changed["roles"][0]["pid"]))
        mutated("reject-waived-real-c-equality",
                lambda changed: changed["c_real_equality"].__setitem__("actual", True))
        probes: list[tuple[str, Any]] = [
            ("filesystem", lambda: os.stat(str(ROOT))),
            ("write", lambda: os.mkdir("forbidden-reference-context")),
            ("process", lambda: subprocess.run(["false"])),
            ("process", lambda: os.execv("/forbidden-source-only-process", [])),
            ("process", lambda: os.execve("/forbidden-source-only-process", [], {})),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("import", lambda: builtins.__import__("candidates.rust_candidate")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("native", lambda: ctypes.CDLL("forbidden-reference-context.so")),
            ("native", lambda: ctypes._dlopen("forbidden-reference-context.so")),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden")),
        ]
        direct_probes = (
            ("_io", "open", "filesystem", ("forbidden-source-only",)),
            ("posix", "open", "filesystem", ("forbidden-source-only", 0)),
            ("posix", "execv", "process", ("/forbidden-source-only", [])),
            ("_posixsubprocess", "fork_exec", "process", ()),
            ("_ctypes", "dlopen", "native", ("forbidden-source-only.so",)),
            ("_imp", "create_dynamic", "native", (None,)),
            ("_imp", "exec_dynamic", "native", (None,)),
            ("_imp", "create_builtin", "native", (None,)),
            ("_imp", "exec_builtin", "native", (None,)),
            ("_socket", "socket", "network", ()),
            ("_thread", "start_new_thread", "thread", (lambda: None, ())),
            ("_thread", "start_joinable_thread", "thread", (lambda: None,)),
        )
        for module_name, attribute, kind, arguments in direct_probes:
            native_module = sys.modules.get(module_name)
            if native_module is not None and hasattr(native_module, attribute):
                probes.append((kind, lambda owner=native_module,
                               name=attribute, args=arguments:
                               getattr(owner, name)(*args)))
        for attribute in (
            "execv", "execve", "execl", "execle", "execlp", "execlpe",
            "execvp", "execvpe", "spawnv", "spawnve", "spawnvp",
            "spawnvpe", "posix_spawn", "posix_spawnp", "fork",
        ):
            if hasattr(os, attribute):
                probes.append(("process", lambda name=attribute:
                               getattr(os, name)()))
        if hasattr(subprocess, "_fork_exec"):
            probes.append(("process", lambda: subprocess._fork_exec()))
        probes.extend((
            ("native", lambda:
             importlib.machinery.ExtensionFileLoader.create_module(None, None)),
            ("native", lambda:
             importlib.machinery.ExtensionFileLoader.exec_module(None, None)),
            ("import", lambda:
             importlib.machinery.SourceFileLoader.create_module(None, None)),
            ("import", lambda:
             importlib.machinery.SourceFileLoader.exec_module(None, None)),
        ))
        if hasattr(threading, "_start_joinable_thread"):
            probes.append(("thread", lambda:
                           threading._start_joinable_thread(lambda: None)))
        for kind, action in probes:
            previous = wall.blocked[kind]
            reject("physically-block-" + kind, action)
            require(wall.blocked[kind] == previous + 1,
                    "prove every actual forbidden effect was blocked: " + kind)
        require(len(rejected) >= 200 and all(wall.blocked.values()),
                "exercise every case, both workers, and every effect boundary")
        blocked = dict(wall.blocked)
    return {
        "schema": SCHEMA + "-source-only-self-test", "version": VERSION,
        "status": "PASS", "source_sha256": source_pin,
        "protocol_sha256": protocol_pin, "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "blocked_effects_by_kind": blocked,
        "synthetic_proof": proof,
        "simulated_controller_faults": faults,
        "original_self_oracle_status": "FALSIFIED FOR CANDIDATE CONTEXT",
        "corrected_reference_status": "NOT RUN",
        "candidate_matching": "NOT RUN", "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def read_owner(item: Owner) -> tuple[bytes, dict[str, Any]]:
    checked_digest(item.sha256, item.path)
    require(type(item.size) is int and 0 < item.size <= MAX_OWNER_BYTES,
            "bound every complete source or compressed evidence owner")
    path = Path(item.path) if os.path.isabs(item.path) else ROOT / item.path
    flags = os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(str(path), flags)
    except OSError as error:
        raise ContextError("cannot open exact no-follow owner: " + item.path) from error
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and info.st_size == item.size
                and info.st_nlink == 1,
                "reject a nonregular, aliased, or resized owner: " + item.path)
        chunks: list[bytes] = []
        total = 0
        while total <= item.size:
            chunk = os.read(descriptor, min(256 * 1024, item.size + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        content = b"".join(chunks)
        require(len(content) == item.size and digest(content) == item.sha256,
                "reject substituted complete owner bytes: " + item.path)
        again = os.fstat(descriptor)
        require((again.st_dev, again.st_ino, again.st_size, again.st_nlink)
                == (info.st_dev, info.st_ino, info.st_size, info.st_nlink),
                "reject a replaced owner descriptor: " + item.path)
        return content, {
            "path": item.path, "sha256": item.sha256, "bytes": item.size,
            "device": info.st_dev, "inode": info.st_ino,
            "mode": stat.S_IMODE(info.st_mode), "nlink": info.st_nlink,
        }
    finally:
        os.close(descriptor)


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    source_pin = checked_digest(source_pin, "reference-context source")
    protocol_pin = checked_digest(protocol_pin, "reference-context protocol")
    contract_pin = checked_digest(contract_pin, "reference-context contract")
    exact = contract_document(source_pin, protocol_pin)
    require(digest(canonical(exact)) == contract_pin,
            "reject a replaced canonical machine contract")
    documents: dict[str, dict[str, Any]] = {}
    retained: dict[str, dict[str, Any]] = {}
    for name, item in OWNERS.items():
        content, identity = read_owner(item)
        documents[name] = identity
        if name in {"original_manifest", "actual_context_falsification",
                    "old_public_receipt",
                    "rust_matching_receipt", "c_matching_receipt",
                    "zig_matching_receipt", "rust_v13_build_receipt",
                    "signature_receipt"}:
            retained[name] = decode_document(content, item.path)
    for name, path, pin in (
        ("source", SOURCE, source_pin),
        ("protocol", PROTOCOL, protocol_pin),
        ("contract", CONTRACT, contract_pin),
    ):
        real_path = ROOT / path
        try:
            count = os.stat(real_path, follow_symlinks=False).st_size
        except OSError as error:
            raise ContextError("cannot identify frozen owner: " + path) from error
        content, identity = read_owner(Owner(path, pin, count))
        documents[name] = identity
        if name == "contract":
            require(content == canonical(exact),
                    "the prospective canonical contract is not exact bytes")
    manifest = retained["original_manifest"]
    denominator = manifest.get("denominator")
    require(type(denominator) is dict
            and denominator.get("final_required_case_execution_denominator")
            == ORIGINAL_CASE_COUNT
            and type(manifest.get("suites")) is list
            and len(manifest["suites"]) == ORIGINAL_SUITE_COUNT,
            "preserve the exact frozen original 31,237-case ledger")
    public = [row for row in manifest["suites"]
              if row.get("id") == "public_types_v1"]
    require(len(public) == 1
            and public[0].get("case_execution_count") == PUBLIC_CASE_COUNT,
            "preserve the complete unchanged 6,912-case original public suite")
    falsification = retained["actual_context_falsification"]
    actual_replay = falsification.get("actual_replay")
    original_oracle = falsification.get("original_oracle")
    affected = falsification.get("falsifying_cases")
    immutable = falsification.get("immutable_sources")
    interpretation = falsification.get("interpretation")
    require(falsification.get("schema")
            == "rebar-public-type-candidate-context-falsification-v1"
            and falsification.get("status") == "FALSIFIED"
            and falsification.get("candidate_facing_self_oracle_status") == "FAIL"
            and type(actual_replay) is dict
            and actual_replay.get("python_version") == "3.14.6"
            and actual_replay.get("python_sha256") == PYTHON_SHA256
            and actual_replay.get("isolated_python_process_id") == 80
            and actual_replay.get("candidate_import_count") == 0
            and actual_replay.get("candidate_workers_started") == 0
            and actual_replay.get("reference_subprocesses_started") == 0
            and actual_replay.get("matching_archives_opened") == 0
            and actual_replay.get("holdout_opened") is False,
            "authenticate the actual real isolated standard-only falsification")
    require(type(original_oracle) is dict
            and original_oracle.get("case_execution_denominator") == ORIGINAL_CASE_COUNT
            and original_oracle.get("suite_count") == ORIGINAL_SUITE_COUNT
            and original_oracle.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and original_oracle.get("affected_suite") == "public_types_v1"
            and original_oracle.get("affected_suite_case_count") == PUBLIC_CASE_COUNT
            and original_oracle.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and original_oracle.get("published_seed_decimal") == str(PUBLISHED_SEED)
            and original_oracle.get("original_cases_removed") == 0
            and original_oracle.get("additional_private_waivers") == 0
            and original_oracle.get("case_denominator_changed") is False,
            "bind the real self-oracle failure to every original frozen obligation")
    require(type(affected) is dict
            and affected.get("cohort") == COHORT
            and affected.get("case_count") == COHORT_CASE_COUNT
            and affected.get("text_subclass_case_count") == 48
            and affected.get("bytes_subclass_case_count") == 48
            and affected.get("first_case") == FIRST_CASE
            and affected.get("last_case") == LAST_CASE
            and affected.get("case_ids_sha256") == CASE_IDS_CANONICAL_SHA256
            and affected.get("exact_case_matrix_sha256") == COHORT_MATRIX_SHA256
            and affected.get("published_script_context_records_sha256")
            == OLD_COHORT_RECORDS_SHA256
            and affected.get("actual_named_context_stdlib_records_sha256")
            == NAMED_COHORT_RECORDS_SHA256
            and affected.get("first_script_context_record_sha256")
            == FIRST_OLD_RECORD_SHA256
            and affected.get("first_named_context_stdlib_record_sha256")
            == FIRST_NAMED_RECORD_SHA256
            and affected.get("sole_normalized_difference_path")
            == "outcome.value.items[2].module"
            and affected.get("published_script_context_module") == "__main__"
            and affected.get("actual_candidate_facing_module") == ORACLE_MODULE,
            "authenticate all actual 96 false mismatches; never guess the replay")
    require(type(immutable) is dict
            and type(immutable.get("candidate_suite_gate")) is dict
            and immutable["candidate_suite_gate"].get("sha256")
            == OWNERS["candidate_gate"].sha256
            and type(immutable.get("public_type_observer")) is dict
            and immutable["public_type_observer"].get("sha256")
            == OWNERS["public_oracle"].sha256
            and type(immutable.get("candidate_case_producer")) is dict
            and immutable["candidate_case_producer"].get("sha256")
            == OWNERS["original_producer"].sha256
            and type(immutable.get("original_public_reference_archive")) is dict
            and immutable["original_public_reference_archive"].get("sha256")
            == OWNERS["old_public_archive"].sha256
            and immutable["original_public_reference_archive"].get("opened_by_replay") is False
            and type(immutable.get("original_public_reference_receipt")) is dict
            and immutable["original_public_reference_receipt"].get("sha256")
            == OWNERS["old_public_receipt"].sha256,
            "authenticate every source and unopened reference in the actual witness")
    require(type(interpretation) is dict
            and interpretation.get("candidate_facing_python_against_python_agrees") is False
            and interpretation.get("historical_rust_records_recomputed_or_deleted") is False
            and interpretation.get("c_pattern_equality_failure_waived") is False
            and interpretation.get("zig_pattern_equality_failure_waived") is False
            and interpretation.get("all_candidate_matching_blocked") is True
            and interpretation.get("same_context_reference_correction_status") == "NOT RUN"
            and interpretation.get("separate_50_case_reference_status") == "PASS"
            and interpretation.get("separate_50_case_candidate_status") == "NOT RUN"
            and interpretation.get("final_holdout_opened") is False,
            "retain the actual fail-closed phase-one evidence interpretation")
    old = retained["old_public_receipt"]
    require(old.get("status") == "PASS"
            and old.get("baseline_result_status") == "PASS"
            and old.get("case_count") == PUBLIC_CASE_COUNT
            and old.get("actual_reference_workers") == 2
            and old.get("baseline_reference_pids") == [82, 83]
            and old.get("baseline_records_sha256")
            == "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
            and old.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and old.get("oracle_source_sha256") == OWNERS["public_oracle"].sha256
            and old.get("published_seed_decimal") == str(PUBLISHED_SEED)
            and old.get("report_sha256") == OWNERS["old_public_archive"].sha256
            and old.get("report_bytes") == OWNERS["old_public_archive"].size,
            "authenticate the original script-context two-reference baseline")
    expected_results = (
        ("rust_matching_receipt", "rust_matching_archive", 1036, 8965),
        ("c_matching_receipt", "c_matching_archive", 1230, 7325),
        ("zig_matching_receipt", "zig_matching_archive", 1764, 3711),
    )
    for receipt_name, archive_name, mismatches, passes in expected_results:
        receipt = retained[receipt_name]
        archive = receipt.get("archive")
        require(receipt.get("status") == "PASS"
                and receipt.get("candidate_status") == "FAIL"
                and receipt.get("case_execution_denominator") == ORIGINAL_CASE_COUNT
                and receipt.get("suite_count") == ORIGINAL_SUITE_COUNT
                and receipt.get("completed_suite_count") == ORIGINAL_SUITE_COUNT
                and receipt.get("actual_candidate_workers") == ORIGINAL_SUITE_COUNT
                and receipt.get("semantic_mismatch_count") == mismatches
                and receipt.get("verified_passing_case_count") == passes
                and receipt.get("infrastructure_failure_count") == 0
                and type(archive) is dict
                and archive.get("sha256") == OWNERS[archive_name].sha256
                and archive.get("size_bytes") == OWNERS[archive_name].size,
                "preserve actual failed, independently owned history: " + receipt_name)
    build = retained["rust_v13_build_receipt"]
    require(build.get("status") == "PASS"
            and build.get("build_status") == "PASS"
            and build.get("actual_compiler_process_count") == 28
            and build.get("candidate_correctness") == "NOT MEASURED"
            and build.get("candidate_processes_started") == 0
            and build.get("archive_sha256") == OWNERS["rust_v13_build_archive"].sha256,
            "a new Rust source build is not a correctness result")
    signature = retained["signature_receipt"]
    require(signature.get("status") == "PASS"
            and signature.get("reference_status") == "PASS"
            and signature.get("actual_distinct_process_ids") == [81, 82]
            and signature.get("actual_reference_processes_started") == 2
            and signature.get("additional_case_count") == 50
            and signature.get("additional_cases_included_in_original_denominator") is False,
            "preserve the separately counted genuine 50-case reference")
    return {
        "schema": SCHEMA + "-verified-frozen-context",
        "version": VERSION, "status": "PASS", "source_sha256": source_pin,
        "protocol_sha256": protocol_pin, "contract_sha256": contract_pin,
        "authenticated_owner_count": len(documents),
        "authenticated_owners": documents,
        "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
        "original_suite_count": ORIGINAL_SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "public_suite_case_count": PUBLIC_CASE_COUNT,
        "actual_previous_script_context_reference_workers": 2,
        "previous_candidate_context_self_oracle": "FALSIFIED",
        "false_fixture_module_case_count": COHORT_CASE_COUNT,
        "text_subclass_case_count": 48,
        "bytes_subclass_case_count": 48,
        "genuine_c_subclass_equality_status": "FAIL; NOT WAIVED",
        "zig_cache_cohort_observation": "NOT ESTABLISHED",
        "corrected_two_reference_baseline": "NOT RUN",
        "corrected_reference_workers_started": 0,
        "candidate_workers_started": 0,
        "matching_archives_decompressed": 0,
        "reference_archives_decompressed": 0,
        "signature_reference_status": "PASS",
        "separate_signature_cases": 50,
        "signature_cases_included_in_original_denominator": False,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "qualified_candidate_count": 0, "winner_selected": False,
    }


def forbidden_candidate_modules() -> list[str]:
    return sorted(name for name in sys.modules
                  if any(name == prefix or name.startswith(prefix + ".")
                         for prefix in DENIED_CANDIDATE_PREFIXES))


def run_reference_worker(options: argparse.Namespace) -> dict[str, Any]:
    require(options.role in ROLES, "choose one genuine isolated reference role")
    context = verify_context(options.source_sha256,
                             options.protocol_sha256,
                             options.contract_sha256)
    require(context["status"] == "PASS", "authenticate the full worker context")
    require(not forbidden_candidate_modules(),
            "a candidate or external matcher entered a reference worker")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    gate = importlib.import_module("tools.run_frozen_p0_candidate_v1")
    require(os.path.abspath(str(gate.__file__))
            == str(ROOT / OWNERS["candidate_gate"].path),
            "use the exact candidate-facing frozen P0 gate")
    source = gate.import_suite_source(gate.suite_spec("public_types_v1"))
    require(source.__name__ == ORACLE_MODULE
            and os.path.abspath(str(source.__file__))
            == str(ROOT / OWNERS["public_oracle"].path)
            and source.TextSubclass.__module__ == ORACLE_MODULE
            and source.BytesSubclass.__module__ == ORACLE_MODULE,
            "run the candidate-facing named original fixture in each reference")
    matrix = source.build_matrix()
    require(source.validate_matrix(matrix) == PUBLIC_MATRIX_SHA256
            and len(matrix) == PUBLIC_CASE_COUNT,
            "never alter or reconstruct the complete original public matrix")
    selected = [case for case in matrix if case["cohort"] == COHORT]
    require(len(selected) == COHORT_CASE_COUNT
            and [case["case"] for case in selected] == case_ids()
            and source.digest(selected) == COHORT_MATRIX_SHA256,
            "preserve every actual frozen cache-cohort case and source matrix")
    support = source.preload_support_modules()
    source.verify_support_modules(support)
    reference = importlib.import_module("re")
    require(reference.__name__ == "re"
            and os.path.abspath(str(reference.__file__))
            == OWNERS["stdlib_re"].path,
            "load only the pinned standard reference inside its isolated worker")
    records: list[dict[str, Any]] = []
    for case in matrix:
        records.append(source.observe_case(case, reference, support))
    source.verify_support_modules(support)
    require(len(records) == PUBLIC_CASE_COUNT,
            "execute all 6,912 original public reference cases")
    cache_records = [record for record in records
                     if record.get("cohort") == COHORT]
    require(len(cache_records) == COHORT_CASE_COUNT
            and [record["case"] for record in cache_records] == case_ids()
            and source.digest(cache_records) == NAMED_COHORT_RECORDS_SHA256,
            "reproduce every independently witnessed named-context reference case")
    require(not forbidden_candidate_modules(),
            "never import a native candidate or foreign matcher")
    return {
        "schema": SCHEMA + "-actual-named-context-reference-worker",
        "status": "PASS", "version": VERSION, "role": options.role,
        "pid": os.getpid(), "python": "3.14.6",
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "contract_sha256": options.contract_sha256,
        "oracle_source_sha256": OWNERS["public_oracle"].sha256,
        "candidate_facing_gate_sha256": OWNERS["candidate_gate"].sha256,
        "oracle_module": source.__name__,
        "matrix_sha256": PUBLIC_MATRIX_SHA256,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": len(records),
        "records_sha256": source.digest(records),
        "records": records,
        "cache_case_count": len(cache_records),
        "cache_records_sha256": source.digest(cache_records),
        "candidate_import_count": 0, "candidate_workers_started": 0,
        "external_regex_packages_used": 0, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 72
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-_" for ch in value),
            "a short, independently pinned lowercase evidence label is required")
    return value


def reference_arguments(options: argparse.Namespace, role: str) -> list[str]:
    return [PYTHON, "-I", "-B", str(ROOT / SOURCE),
            "--internal-reference-worker", "--role", role,
            "--source-sha256", options.source_sha256,
            "--protocol-sha256", options.protocol_sha256,
            "--contract-sha256", options.contract_sha256]


def validate_actual_worker(value: Any, role: str, process: subprocess.Popen[bytes],
                           stdout: bytes, stderr: bytes,
                           options: argparse.Namespace) -> dict[str, Any]:
    require(type(value) is dict and value.get("schema")
            == SCHEMA + "-actual-named-context-reference-worker"
            and value.get("status") == "PASS"
            and value.get("role") == role
            and value.get("pid") == process.pid
            and type(process.pid) is int and process.pid > 0
            and process.returncode == 0 and stderr == b""
            and value.get("source_sha256") == options.source_sha256
            and value.get("protocol_sha256") == options.protocol_sha256
            and value.get("contract_sha256") == options.contract_sha256
            and value.get("oracle_source_sha256") == OWNERS["public_oracle"].sha256
            and value.get("candidate_facing_gate_sha256") == OWNERS["candidate_gate"].sha256
            and value.get("oracle_module") == ORACLE_MODULE
            and value.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and value.get("published_seed_decimal") == str(PUBLISHED_SEED)
            and value.get("case_count") == PUBLIC_CASE_COUNT
            and value.get("cache_case_count") == COHORT_CASE_COUNT
            and value.get("cache_records_sha256") == NAMED_COHORT_RECORDS_SHA256
            and value.get("candidate_import_count") == 0
            and value.get("candidate_workers_started") == 0
            and value.get("external_regex_packages_used") == 0
            and value.get("holdout") == "NOT OPENED"
            and stdout == canonical(value),
            "reject an invented, substituted, partial, or candidate-tainted worker")
    records = value.get("records")
    require(type(records) is list and len(records) == PUBLIC_CASE_COUNT
            and digest(canonical(records)) == value.get("records_sha256"),
            "preserve every full original reference record")
    selected = [record for record in records
                if record.get("cohort") == COHORT]
    require(len(selected) == COHORT_CASE_COUNT
            and [record.get("case") for record in selected] == case_ids()
            and digest(canonical(selected)) == NAMED_COHORT_RECORDS_SHA256,
            "never suppress one of the 96 actual candidate-context cases")
    return value


def encode_process_stream(value: Any, maximum: int) -> dict[str, Any]:
    require(type(value) is bytes,
            "retain a genuine process byte stream even on failure")
    complete = len(value) <= maximum
    retained = value if complete else value[:maximum]
    return {
        "sha256": digest(value),
        "bytes": len(value),
        "retained_bytes": len(retained),
        "complete": complete,
        "base64": base64.b64encode(retained).decode("ascii"),
    }


def process_envelope(role: str, process: Any, stdout: bytes,
                     stderr: bytes, timed_out: bool) -> dict[str, Any]:
    require(role in ROLES and type(getattr(process, "pid", None)) is int
            and process.pid > 0,
            "preserve the actual genuine reference process identity")
    return {
        "role": role,
        "pid": process.pid,
        "returncode": process.returncode,
        "timed_out": timed_out,
        "stdout": encode_process_stream(stdout, MAX_WORKER_BYTES),
        "stderr": encode_process_stream(stderr, MAX_WORKER_STDERR_BYTES),
    }


def start_reference(options: argparse.Namespace, role: str,
                    journal: Any, *, launcher: Any = None,
                    validator: Any = None
                    ) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in ROLES, "refuse an unowned reference process role")
    arguments = reference_arguments(options, role)
    journal.note_attempt(role, arguments)
    spawn = subprocess.Popen if launcher is None else launcher
    try:
        process = spawn(
            arguments, cwd=str(ROOT), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
    except Exception as error:
        evidence = {
            "stage": "spawn", "role": role, "pid": None,
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:8192],
        }
        journal.note_failure(evidence)
        raise ReferenceWorkerFailure(
            "preserve an independently witnessed reference spawn failure: "
            + role, evidence,
        ) from error

    started = {
        "role": role,
        "pid": getattr(process, "pid", None),
        "arguments": arguments,
    }
    require(type(started["pid"]) is int and started["pid"] > 0,
            "never invent or omit a genuine spawned reference PID")
    try:
        journal.note_started(started)
    except Exception as error:
        try:
            process.kill()
            stdout, stderr = process.communicate()
        except Exception:
            stdout, stderr = b"", b""
        evidence = {
            "stage": "started-journal", "role": role,
            "pid": process.pid,
            "process": process_envelope(role, process, stdout, stderr, False),
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:8192],
        }
        raise ReferenceWorkerFailure(
            "a real started reference cannot proceed without its durable PID",
            evidence,
        ) from error

    timed_out = False
    communicate_error: Exception | None = None
    try:
        stdout, stderr = process.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        timed_out = True
        communicate_error = error
        process.kill()
        stdout, stderr = process.communicate()
    except Exception as error:
        communicate_error = error
        try:
            if process.poll() is None:
                process.kill()
            stdout, stderr = process.communicate()
        except Exception:
            stdout, stderr = b"", b""
    envelope = process_envelope(role, process, stdout, stderr, timed_out)
    journal.note_completed(envelope)
    if communicate_error is not None:
        evidence = {
            "stage": "timeout" if timed_out else "communicate",
            "role": role, "pid": process.pid, "process": envelope,
            "error_type": type(communicate_error).__qualname__,
            "error_message": str(communicate_error)[:8192],
        }
        journal.note_failure(evidence)
        raise ReferenceWorkerFailure(
            "preserve the complete failed or timed-out real reference process",
            evidence,
        ) from communicate_error
    try:
        require(envelope["stdout"]["complete"]
                and envelope["stderr"]["complete"],
                "reject an oversized reference stream without concealing its PID or full hash")
        value = decode_document(stdout, role + " full process stdout")
        validate = validate_actual_worker if validator is None else validator
        worker = validate(value, role, process, stdout, stderr, options)
    except Exception as error:
        evidence = {
            "stage": "worker-validation", "role": role,
            "pid": process.pid, "process": envelope,
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:8192],
        }
        journal.note_failure(evidence)
        raise ReferenceWorkerFailure(
            "preserve the complete real reference before rejecting its output",
            evidence,
        ) from error
    journal.note_validated(role, process.pid, worker["records_sha256"])
    return worker, envelope


def publication_names(label: str, failed: bool = False) -> tuple[str, str]:
    stem = "public-type-reference-context-v1-" + validate_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def publish_bytes(directory_fd: int, name: str,
                  content: bytes, *, base_path: str = EVIDENCE_DIRECTORY
                  ) -> dict[str, Any]:
    require(type(content) is bytes and content,
            "publish only a complete exact evidence owner")
    require(type(name) is str and name not in {"", ".", ".."}
            and "/" not in name and "\\" not in name,
            "publish only one literal descriptor-bound evidence name")
    flags = os.O_WRONLY | os.O_CLOEXEC | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, 0o600, dir_fd=directory_fd)
    try:
        total = 0
        while total < len(content):
            written = os.write(descriptor, content[total:])
            require(written > 0, "preserve every evidence byte")
            total += written
        os.fsync(descriptor)
        created = os.fstat(descriptor)
        require(stat.S_ISREG(created.st_mode)
                and stat.S_IMODE(created.st_mode) == 0o600
                and created.st_nlink == 1 and created.st_size == len(content),
                "create one genuine exclusive owner-only evidence file")
    finally:
        os.close(descriptor)
    verify_flags = os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0)
    reopened = os.open(name, verify_flags, dir_fd=directory_fd)
    try:
        observed = os.fstat(reopened)
        require((observed.st_dev, observed.st_ino, observed.st_size)
                == (created.st_dev, created.st_ino, created.st_size),
                "reauthenticate the same newly published evidence inode")
        pieces: list[bytes] = []
        used = 0
        while used <= len(content):
            block = os.read(reopened, min(256 * 1024, len(content) + 1 - used))
            if not block:
                break
            pieces.append(block)
            used += len(block)
        require(b"".join(pieces) == content,
                "read back every exact newly published evidence byte")
    finally:
        os.close(reopened)
    os.fsync(directory_fd)
    return {"path": base_path + "/" + name,
            "sha256": digest(content), "bytes": len(content),
            "device": created.st_dev, "inode": created.st_ino,
            "mode": stat.S_IMODE(created.st_mode), "nlink": created.st_nlink,
            "exclusive_creation": True, "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "same_inode_readback_verified": True}


def publish_with_recovery(directory_fd: int, name: str, content: bytes,
                          journal: Any, stage: str, *, publisher: Any = None,
                          previous: dict[str, Any] | None = None
                          ) -> dict[str, Any]:
    require(stage in {"archive", "receipt"},
            "preserve the exact independently recoverable publication stage")
    operation = publish_bytes if publisher is None else publisher
    try:
        owner = operation(directory_fd, name, content)
        require(type(owner) is dict and type(owner.get("sha256")) is str,
                "a durable publication must yield its complete owner")
    except Exception as error:
        details: dict[str, Any] = {
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:8192],
            "target_name": name,
        }
        if previous is not None:
            details["archive"] = previous
        journal.snapshot(stage + "-publication-failed", details)
        raise
    details = {stage: owner}
    if previous is not None:
        details["archive"] = previous
    journal.snapshot(stage + "-published", details)
    return owner


class RecoveryJournal:
    """Retain every real reference attempt before advancing to its next stage."""

    def __init__(self, label: str, options: argparse.Namespace) -> None:
        checked = validate_label(label)
        self.path = (
            "/tmp/rebar-phase1-public-type-reference-context-v1-" + checked
        )
        self.options = options
        self.attempted: list[dict[str, Any]] = []
        self.started: list[dict[str, Any]] = []
        self.completed: list[dict[str, Any]] = []
        self.validated: list[dict[str, Any]] = []
        self.failures: list[dict[str, Any]] = []
        self.snapshots: list[dict[str, Any]] = []
        try:
            os.mkdir(self.path, 0o700)
        except OSError as error:
            raise ContextError(
                "refuse a missing, reused, or nonexclusive recovery directory: "
                + self.path
            ) from error
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY
        flags |= getattr(os, "O_NOFOLLOW", 0)
        self.descriptor = os.open(self.path, flags)
        identity = os.fstat(self.descriptor)
        require(stat.S_ISDIR(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o700
                and identity.st_uid == os.getuid(),
                "require one real independently owned mode-0700 recovery directory")
        self.identity = {
            "path": self.path, "device": identity.st_dev,
            "inode": identity.st_ino,
            "mode": stat.S_IMODE(identity.st_mode),
        }
        self.snapshot("preflight", {"status": "READY"})

    def snapshot(self, stage: str, details: dict[str, Any]) -> dict[str, Any]:
        require(type(stage) is str and stage
                and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-"
                        for ch in stage),
                "freeze every append-only journal stage")
        require(type(details) is dict,
                "retain complete structured recovery details")
        index = len(self.snapshots)
        document = {
            "schema": SCHEMA + "-actual-private-recovery-journal",
            "version": VERSION,
            "step": index,
            "stage": stage,
            "root": self.identity,
            "source_sha256": self.options.source_sha256,
            "protocol_sha256": self.options.protocol_sha256,
            "contract_sha256": self.options.contract_sha256,
            "attempted_reference_worker_count": len(self.attempted),
            "actual_started_reference_worker_count": len(self.started),
            "completed_reference_worker_count": len(self.completed),
            "validated_reference_worker_count": len(self.validated),
            "attempted_reference_roles": self.attempted,
            "actual_started_reference_processes": self.started,
            "complete_reference_processes": self.completed,
            "validated_reference_processes": self.validated,
            "complete_failure_evidence": self.failures,
            "previous_snapshot":
            self.snapshots[-1] if self.snapshots else None,
            "details": details,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "holdout": "NOT OPENED",
        }
        plain = canonical(document)
        require(len(plain) <= MAX_REPORT_BYTES,
                "bound every complete durable append-only recovery snapshot")
        name = f"journal-{index:04d}-{stage}.json"
        owner = publish_bytes(self.descriptor, name, plain,
                              base_path=self.path)
        self.snapshots.append(owner)
        return owner

    def note_attempt(self, role: str, arguments: list[str]) -> None:
        require(role in ROLES and len(self.attempted) < len(ROLES)
                and role == ROLES[len(self.attempted)]
                and arguments[:3] == [PYTHON, "-I", "-B"],
                "never invent, reorder, or duplicate an attempted reference")
        self.attempted.append({"role": role, "arguments": arguments})
        self.snapshot("preattempt-" + role, {"role": role})

    def note_started(self, evidence: dict[str, Any]) -> None:
        require(type(evidence) is dict and len(self.started) < len(self.attempted)
                and evidence.get("role") == self.attempted[-1]["role"]
                and type(evidence.get("pid")) is int and evidence["pid"] > 0
                and evidence["pid"] not in {item["pid"] for item in self.started},
                "journal the real unique spawned PID before communication")
        self.started.append(copy.deepcopy(evidence))
        self.snapshot("started-" + evidence["role"], evidence)

    def note_completed(self, evidence: dict[str, Any]) -> None:
        require(type(evidence) is dict
                and len(self.completed) < len(self.started)
                and evidence.get("role") == self.started[-1]["role"]
                and evidence.get("pid") == self.started[-1]["pid"],
                "journal both real process streams before decoding a worker")
        self.completed.append(copy.deepcopy(evidence))
        self.snapshot("completed-" + evidence["role"], evidence)

    def note_validated(self, role: str, pid: int,
                       records_sha256: str) -> None:
        checked_digest(records_sha256, "complete validated reference records")
        require(len(self.validated) < len(self.completed)
                and role == self.completed[-1]["role"]
                and pid == self.completed[-1]["pid"],
                "validate only an already journaled real complete reference")
        evidence = {"role": role, "pid": pid,
                    "records_sha256": records_sha256}
        self.validated.append(evidence)
        self.snapshot("validated-" + role, evidence)

    def note_failure(self, evidence: dict[str, Any]) -> None:
        require(type(evidence) is dict and evidence.get("role") in ROLES
                and type(evidence.get("stage")) is str,
                "preserve a complete actual structured reference failure")
        self.failures.append(copy.deepcopy(evidence))
        stage = evidence["stage"].replace("_", "-")
        self.snapshot("failed-" + stage, evidence)

    def describe(self) -> dict[str, Any]:
        return {
            "root": self.identity,
            "snapshot_count": len(self.snapshots),
            "latest_snapshot": self.snapshots[-1],
            "attempted_reference_worker_count": len(self.attempted),
            "actual_started_reference_worker_count": len(self.started),
            "completed_reference_worker_count": len(self.completed),
            "validated_reference_worker_count": len(self.validated),
        }

    def close(self) -> None:
        if self.descriptor is not None:
            os.close(self.descriptor)
            self.descriptor = None


class SyntheticRecoveryJournal:
    """Exercise real controller branches without a file or a subprocess."""

    def __init__(self) -> None:
        self.attempted: list[dict[str, Any]] = []
        self.started: list[dict[str, Any]] = []
        self.completed: list[dict[str, Any]] = []
        self.validated: list[dict[str, Any]] = []
        self.failures: list[dict[str, Any]] = []
        self.snapshots: list[dict[str, Any]] = []
        self.snapshot("preflight", {"status": "READY"})

    def snapshot(self, stage: str, details: dict[str, Any]) -> dict[str, Any]:
        require(type(stage) is str and stage and type(details) is dict,
                "retain an actual simulated publication or process stage")
        item = {"step": len(self.snapshots), "stage": stage,
                "details": copy.deepcopy(details),
                "attempted": len(self.attempted),
                "started": len(self.started),
                "completed": len(self.completed),
                "validated": len(self.validated)}
        self.snapshots.append(item)
        return item

    def note_attempt(self, role: str, arguments: list[str]) -> None:
        require(role in ROLES and len(self.attempted) < 2
                and role == ROLES[len(self.attempted)],
                "retain exact synthetic attempted role order")
        self.attempted.append({"role": role,
                               "arguments": copy.deepcopy(arguments)})
        self.snapshot("preattempt-" + role, {"role": role})

    def note_started(self, evidence: dict[str, Any]) -> None:
        require(self.attempted and evidence.get("role")
                == self.attempted[-1]["role"]
                and type(evidence.get("pid")) is int
                and evidence["pid"] > 0
                and evidence["pid"] not in {item["pid"]
                                             for item in self.started},
                "retain the exact synthetic started process PID")
        self.started.append(copy.deepcopy(evidence))
        self.snapshot("started-" + evidence["role"], evidence)

    def note_completed(self, evidence: dict[str, Any]) -> None:
        require(self.started and evidence.get("role")
                == self.started[-1]["role"]
                and evidence.get("pid") == self.started[-1]["pid"],
                "retain complete fake process output before validation")
        self.completed.append(copy.deepcopy(evidence))
        self.snapshot("completed-" + evidence["role"], evidence)

    def note_validated(self, role: str, pid: int,
                       records_sha256: str) -> None:
        require(self.completed and self.completed[-1]["role"] == role
                and self.completed[-1]["pid"] == pid,
                "never validate a process without its full prior stream")
        item = {"role": role, "pid": pid,
                "records_sha256": checked_digest(records_sha256,
                                                   "simulated complete vector")}
        self.validated.append(item)
        self.snapshot("validated-" + role, item)

    def note_failure(self, evidence: dict[str, Any]) -> None:
        require(type(evidence) is dict and evidence.get("role") in ROLES,
                "retain every actual simulated failure envelope")
        self.failures.append(copy.deepcopy(evidence))
        self.snapshot("failed-" + evidence["stage"].replace("_", "-"),
                      evidence)


class SyntheticReferenceProcess:
    """A no-effect substitute for exactly one genuinely observed Popen."""

    def __init__(self, pid: int, mode: str) -> None:
        self.pid = pid
        self.mode = mode
        self.returncode = 0
        self.killed = False

    def communicate(self, timeout: int | None = None) -> tuple[bytes, bytes]:
        if self.mode == "timeout" and timeout is not None:
            raise subprocess.TimeoutExpired("synthetic-reference", timeout)
        if self.mode == "timeout":
            return b"synthetic timed-out reference stdout\n", b"synthetic timeout\n"
        if self.mode == "first":
            return canonical({
                "schema": SCHEMA + "-synthetic-complete-reference-worker",
                "role": ROLES[0], "pid": self.pid,
                "records_sha256": NAMED_COHORT_RECORDS_SHA256,
            }), b""
        return b'{"not_a_complete_reference":true}\n', b""

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9

    def poll(self) -> int | None:
        return self.returncode


def verify_retained_process(envelope: dict[str, Any], role: str,
                            pid: int) -> None:
    require(envelope.get("role") == role and envelope.get("pid") == pid,
            "a real failed process PID or role was discarded")
    for name, maximum in (("stdout", MAX_WORKER_BYTES),
                          ("stderr", MAX_WORKER_STDERR_BYTES)):
        stream = envelope.get(name)
        require(type(stream) is dict and stream.get("complete") is True
                and type(stream.get("base64")) is str,
                "retain complete bounded " + name + " before validation")
        try:
            raw = base64.b64decode(stream["base64"], validate=True)
        except (ValueError, TypeError) as error:
            raise ContextError("a retained process stream was corrupted") from error
        require(len(raw) <= maximum and len(raw) == stream.get("bytes")
                and len(raw) == stream.get("retained_bytes")
                and digest(raw) == stream.get("sha256"),
                "authenticate every actual retained failed-process byte")


def exercise_controller_faults(source_pin: str, protocol_pin: str,
                               contract_pin: str) -> dict[str, Any]:
    options = argparse.Namespace(source_sha256=source_pin,
                                 protocol_sha256=protocol_pin,
                                 contract_sha256=contract_pin)

    def prime_first(journal: SyntheticRecoveryJournal) -> None:
        fake = SyntheticReferenceProcess(58001, "first")

        def fake_launcher(*_args: Any, **_kwargs: Any) -> SyntheticReferenceProcess:
            return fake

        def fake_validator(value: Any, role: str, process: Any,
                           stdout: bytes, stderr: bytes,
                           _options: argparse.Namespace) -> dict[str, Any]:
            require(value.get("schema")
                    == SCHEMA + "-synthetic-complete-reference-worker"
                    and value.get("role") == ROLES[0]
                    and value.get("pid") == 58001
                    and value.get("records_sha256") == NAMED_COHORT_RECORDS_SHA256
                    and role == ROLES[0] and process.pid == 58001
                    and stdout == canonical(value) and stderr == b"",
                    "validate the complete injected first worker honestly")
            return value

        worker, envelope = start_reference(
            options, ROLES[0], journal,
            launcher=fake_launcher, validator=fake_validator,
        )
        require(worker["records_sha256"] == NAMED_COHORT_RECORDS_SHA256
                and envelope["pid"] == 58001
                and len(journal.attempted) == 1
                and len(journal.started) == 1
                and len(journal.completed) == 1
                and len(journal.validated) == 1,
                "run a successful fake first process through production logic")

    class PreattemptFailureJournal(SyntheticRecoveryJournal):
        def note_attempt(self, role: str, arguments: list[str]) -> None:
            super().note_attempt(role, arguments)
            raise OSError("independently injected preattempt journal fault")

    preattempt = PreattemptFailureJournal()
    unexpected_launches: list[str] = []

    def forbidden_fake_launch(*_args: Any, **_kwargs: Any) -> Any:
        unexpected_launches.append("launched")
        return SyntheticReferenceProcess(58999, "invalid")

    try:
        start_reference(options, ROLES[0], preattempt,
                        launcher=forbidden_fake_launch)
    except OSError:
        require(len(preattempt.attempted) == 1
                and not preattempt.started and not preattempt.completed
                and not preattempt.validated and not unexpected_launches,
                "never start a process when its preattempt journal cannot commit")
    else:
        raise ContextError("accepted an injected preattempt recovery-journal fault")

    spawn_journal = SyntheticRecoveryJournal()

    def fail_to_spawn(*_args: Any, **_kwargs: Any) -> Any:
        raise OSError("independently injected Popen spawn fault")

    try:
        start_reference(options, ROLES[0], spawn_journal,
                        launcher=fail_to_spawn)
    except ReferenceWorkerFailure as error:
        require(error.evidence.get("stage") == "spawn"
                and error.evidence.get("pid") is None
                and len(spawn_journal.attempted) == 1
                and not spawn_journal.started
                and not spawn_journal.completed
                and not spawn_journal.validated
                and len(spawn_journal.failures) == 1,
                "preserve an actually simulated failed Popen attempt")
    else:
        raise ContextError("accepted an injected real controller spawn failure")

    second_journal = SyntheticRecoveryJournal()
    prime_first(second_journal)

    def invalid_second(*_args: Any, **_kwargs: Any) -> SyntheticReferenceProcess:
        return SyntheticReferenceProcess(58002, "invalid")

    try:
        start_reference(options, ROLES[1], second_journal,
                        launcher=invalid_second)
    except ReferenceWorkerFailure as error:
        require(error.evidence.get("stage") == "worker-validation"
                and error.evidence.get("pid") == 58002
                and len(second_journal.attempted) == 2
                and len(second_journal.started) == 2
                and len(second_journal.completed) == 2
                and len(second_journal.validated) == 1
                and len(second_journal.failures) == 1,
                "never conceal the actual failed second worker or first success")
        verify_retained_process(error.evidence["process"], ROLES[1], 58002)
        verify_retained_process(second_journal.completed[0], ROLES[0], 58001)
    else:
        raise ContextError("accepted an invalid complete second worker")

    timeout_journal = SyntheticRecoveryJournal()
    prime_first(timeout_journal)
    timed_process = SyntheticReferenceProcess(58003, "timeout")

    def timeout_second(*_args: Any, **_kwargs: Any) -> SyntheticReferenceProcess:
        return timed_process

    try:
        start_reference(options, ROLES[1], timeout_journal,
                        launcher=timeout_second)
    except ReferenceWorkerFailure as error:
        require(error.evidence.get("stage") == "timeout"
                and error.evidence.get("pid") == 58003
                and timed_process.killed
                and len(timeout_journal.attempted) == 2
                and len(timeout_journal.started) == 2
                and len(timeout_journal.completed) == 2
                and len(timeout_journal.validated) == 1,
                "preserve and reap an actually simulated timed-out worker")
        verify_retained_process(error.evidence["process"], ROLES[1], 58003)
    else:
        raise ContextError("accepted an actual simulated reference timeout")

    publication_journal = SyntheticRecoveryJournal()

    def published_archive(_fd: int, name: str,
                          value: bytes) -> dict[str, Any]:
        return {"path": "synthetic/" + name,
                "sha256": digest(value), "bytes": len(value)}

    archive = publish_with_recovery(
        -1, "synthetic.json.gz", b"synthetic-complete-archive",
        publication_journal, "archive", publisher=published_archive,
    )

    def failed_publication(*_args: Any, **_kwargs: Any) -> Any:
        raise OSError("independently injected exclusive publication fault")

    try:
        publish_with_recovery(
            -1, "synthetic-publication-receipt.json",
            b"synthetic-complete-receipt", publication_journal,
            "receipt", publisher=failed_publication, previous=archive,
        )
    except OSError:
        last = publication_journal.snapshots[-1]
        require(last["stage"] == "receipt-publication-failed"
                and last["details"].get("archive") == archive
                and publication_journal.snapshots[-2]["stage"]
                == "archive-published",
                "never conceal a real archive when receipt publication fails")
    else:
        raise ContextError("accepted an injected receipt publication failure")

    archive_failure_journal = SyntheticRecoveryJournal()
    try:
        publish_with_recovery(
            -1, "synthetic-failure.json.gz", b"synthetic-failure",
            archive_failure_journal, "archive",
            publisher=failed_publication,
        )
    except OSError:
        require(archive_failure_journal.snapshots[-1]["stage"]
                == "archive-publication-failed",
                "preserve the exact independently injected archive failure")
    else:
        raise ContextError("accepted an injected archive publication failure")
    return {
        "simulated_fault_count": 6,
        "preattempt_journal_fault_prevents_process_launch": True,
        "actual_popen_spawn_fault_preserved": True,
        "failed_second_worker_pid_and_streams_preserved": True,
        "actual_timeout_pid_and_streams_preserved": True,
        "receipt_fault_retains_published_archive": True,
        "archive_fault_retains_private_journal": True,
    }


def run_reference(options: argparse.Namespace) -> dict[str, Any]:
    validate_label(options.label)
    context = verify_context(options.source_sha256,
                             options.protocol_sha256,
                             options.contract_sha256)
    directory = ROOT / EVIDENCE_DIRECTORY
    directory_fd = os.open(
        str(directory), os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY
        | getattr(os, "O_NOFOLLOW", 0),
    )
    journal: RecoveryJournal | None = None
    try:
        all_names = (*publication_names(options.label, False),
                     *publication_names(options.label, True))
        for name in all_names:
            try:
                os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise ContextError("refuse to overwrite existing reference evidence: " + name)
        journal = RecoveryJournal(options.label, options)
        workers: list[dict[str, Any]] = []
        processes: list[dict[str, Any]] = []
        failed: dict[str, Any] | None = None
        try:
            for role in ROLES:
                worker, process = start_reference(options, role, journal)
                workers.append(worker)
                processes.append(process)
            require(len(workers) == 2 and len(processes) == 2
                    and processes[0]["pid"] != processes[1]["pid"]
                    and workers[0]["records_sha256"]
                    == workers[1]["records_sha256"]
                    and workers[0]["records"] == workers[1]["records"],
                    "require two real distinct complete agreeing CPython references")
        except Exception as error:
            failed = {"type": type(error).__qualname__,
                      "message": str(error)[:8192]}
            if isinstance(error, ReferenceWorkerFailure):
                failed["process_evidence"] = error.evidence
            else:
                detail = {
                    "stage": "reference-agreement",
                    "role": journal.attempted[-1]["role"]
                    if journal.attempted else ROLES[0],
                    "pid": journal.started[-1]["pid"]
                    if journal.started else None,
                    "error_type": type(error).__qualname__,
                    "error_message": str(error)[:8192],
                }
                journal.note_failure(detail)
                failed["process_evidence"] = detail
        status = "PASS" if failed is None else "FAIL"
        if status == "PASS":
            require(len(journal.attempted) == 2
                    and len(journal.started) == 2
                    and len(journal.completed) == 2
                    and len(journal.validated) == 2,
                    "never equate attempted, started, completed, and validated workers")
        journal.snapshot("prepublication-" + status.lower(), {
            "reference_status": status,
            "attempted_reference_worker_count": len(journal.attempted),
            "actual_started_reference_worker_count": len(journal.started),
            "completed_reference_worker_count": len(journal.completed),
            "validated_reference_worker_count": len(journal.validated),
        })
        report = {
            "schema": SCHEMA + "-actual-two-reference-report",
            "version": VERSION, "status": status,
            "label": options.label, "python": "3.14.6",
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "contract_sha256": options.contract_sha256,
            "candidate_facing_oracle_module": ORACLE_MODULE,
            "public_case_count_per_reference": PUBLIC_CASE_COUNT,
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "original_suite_count": ORIGINAL_SUITE_COUNT,
            "private_waiver_count": PRIVATE_WAIVER_COUNT,
            "matrix_sha256": PUBLIC_MATRIX_SHA256,
            "published_seed_decimal": str(PUBLISHED_SEED),
            "cache_case_count": COHORT_CASE_COUNT,
            "cache_case_ids_canonical_sha256": CASE_IDS_CANONICAL_SHA256,
            "cache_records_sha256": NAMED_COHORT_RECORDS_SHA256,
            "attempted_reference_worker_count": len(journal.attempted),
            "actual_reference_worker_count": len(journal.started),
            "actual_started_reference_worker_count": len(journal.started),
            "completed_reference_worker_count": len(journal.completed),
            "validated_reference_worker_count": len(journal.validated),
            "actual_distinct_reference_process_ids":
            [process["pid"] for process in journal.started],
            "full_reference_records_sha256":
            workers[0]["records_sha256"] if len(workers) == 2 and failed is None else "NOT ESTABLISHED",
            "complete_reference_workers": workers,
            "attempted_reference_roles": journal.attempted,
            "actual_started_reference_processes": journal.started,
            "complete_reference_processes": journal.completed,
            "validated_reference_processes": journal.validated,
            "private_recovery_journal": journal.describe(),
            "source_context_owner_count": context["authenticated_owner_count"],
            "self_oracle_failure_repaired": failed is None,
            "failure": failed,
            "candidate_imports": 0, "candidate_workers_started": 0,
            "external_regex_packages_used": 0,
            "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            "qualified_candidate_count": 0, "winner_selected": False,
        }
        plain = canonical(report)
        require(len(plain) <= MAX_REPORT_BYTES,
                "bound the two complete source-owned reference observations")
        archive_bytes = gzip.compress(plain, compresslevel=9, mtime=0)
        require(len(archive_bytes) <= MAX_ARCHIVE_BYTES,
                "bound the deterministic complete two-reference archive")
        archive_name, receipt_name = publication_names(options.label,
                                                       failed is not None)
        archive = publish_with_recovery(directory_fd, archive_name,
                                        archive_bytes, journal, "archive")
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "version": VERSION, "status": "PASS",
            "publication_status": "PASS", "reference_status": status,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "label": options.label, "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "contract_sha256": options.contract_sha256,
            "matrix_sha256": PUBLIC_MATRIX_SHA256,
            "public_case_count_per_reference": PUBLIC_CASE_COUNT,
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "attempted_reference_worker_count": len(journal.attempted),
            "actual_reference_worker_count": len(journal.started),
            "actual_started_reference_worker_count": len(journal.started),
            "completed_reference_worker_count": len(journal.completed),
            "validated_reference_worker_count": len(journal.validated),
            "actual_distinct_reference_process_ids":
            [process["pid"] for process in journal.started],
            "full_reference_records_sha256": report["full_reference_records_sha256"],
            "cache_records_sha256": NAMED_COHORT_RECORDS_SHA256,
            "candidate_imports": 0, "candidate_workers_started": 0,
            "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            "archive": archive, "uncompressed_bytes": len(plain),
            "uncompressed_sha256": digest(plain),
            "gzip_mtime": 0,
            "private_recovery_journal": journal.describe(),
        }
        receipt_owner = publish_with_recovery(
            directory_fd, receipt_name, canonical(receipt),
            journal, "receipt", previous=archive,
        )
        return {"schema": SCHEMA + "-actual-publication",
                "status": status, "publication_status": "PASS",
                "reference_status": status, "label": options.label,
                "attempted_reference_worker_count": len(journal.attempted),
                "actual_reference_worker_count": len(journal.started),
                "actual_started_reference_worker_count": len(journal.started),
                "completed_reference_worker_count": len(journal.completed),
                "validated_reference_worker_count": len(journal.validated),
                "actual_distinct_reference_process_ids":
                [process["pid"] for process in journal.started],
                "archive": archive, "receipt": receipt_owner,
                "private_recovery_journal": journal.describe(),
                "candidate_workers_started": 0,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED"}
    finally:
        if journal is not None:
            journal.close()
        os.close(directory_fd)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    flags = [value for value in values if value.startswith("--")]
    require(len(flags) == len(set(flags)),
            "reject repeated or ambiguous source-freeze authorizations")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--record-reference", action="store_true")
    modes.add_argument("--internal-reference-worker", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    parser.add_argument("--role", choices=ROLES)
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "reference-context source")
    checked_digest(options.protocol_sha256, "reference-context protocol")
    if options.emit_contract:
        require(options.contract_sha256 is None and options.label is None
                and options.role is None,
                "emitting a source contract cannot run a worker or publish")
    else:
        checked_digest(options.contract_sha256, "reference-context contract")
        if options.record_reference:
            validate_label(options.label)
            require(options.role is None,
                    "only a future controller can start two workers")
        elif options.internal_reference_worker:
            require(options.label is None and options.role in ROLES,
                    "an internal reference must have one exact role")
        else:
            require(options.label is None and options.role is None,
                    "a source-only gate can never start or label a worker")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    verify_runtime()
    options = parse_arguments(arguments)
    if options.emit_contract:
        with SourceOnlyWall() as wall:
            result = contract_document(options.source_sha256,
                                       options.protocol_sha256)
            require(not any(wall.blocked.values()),
                    "contract emission attempted a real source-only effect")
    elif options.self_test:
        result = self_test(options.source_sha256, options.protocol_sha256,
                           options.contract_sha256)
    elif options.verify_frozen_context:
        result = verify_context(options.source_sha256, options.protocol_sha256,
                                options.contract_sha256)
    elif options.internal_reference_worker:
        result = run_reference_worker(options)
    else:
        result = run_reference(options)
    output = canonical(result)
    require(len(output) <= (MAX_WORKER_BYTES if options.internal_reference_worker
                            else MAX_REPORT_BYTES),
            "bound every complete externally visible reference result")
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else (
        0 if options.emit_contract else 1
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContextError, OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        try:
            sys.stderr.write(type(error).__qualname__ + ": " + str(error) + "\n")
        except OSError:
            pass
        raise SystemExit(1)
