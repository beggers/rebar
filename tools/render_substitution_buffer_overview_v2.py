#!/usr/bin/env python3
"""Safely show all 5,120 corrected Python replacement-and-buffer checks.

The original V1 callback reports are preserved, signed, and FALSIFIED.
Only the corrected V2 Python baseline and fully verified V3 candidate
reports can contribute to the visible comparison.

The immutable input manifest is independently authored. Two signed CPython
reference streams define the baseline. Every selected native result is rebuilt
from its complete signed worker stream and every source-ordered mismatch.
A receipt records publication, not compatibility. Rust, C, and Zig remain
separate, fully owned families; no candidate, Python matcher, worker, clock,
benchmark, or holdout is executed by this chart.

Only the exact SVG-and-summary pair can be published. Existing files are never
overwritten without both explicitly pinned prior hashes; failed paired updates
restore the exact original pair. All self-tests operate solely in memory.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import builtins
import codecs
import contextlib
import copy
import gc
import hashlib
import importlib
import io
import json
import os
import random
import stat
import subprocess
import sys
import threading
import time
import zlib
from collections.abc import Callable, Iterator, Mapping
from typing import Any

ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/render_substitution_buffer_overview_v2.py"
SCHEMA = "rebar-substitution-buffer-overview-v2"
MANIFEST_RELATIVE = "docs/evidence/substitution-buffer-overview-v2.inputs.json"
SVG_RELATIVE = "docs/evidence/substitution-buffer-overview-v2.svg"
SUMMARY_RELATIVE = "docs/evidence/substitution-buffer-overview-v2.json"
EVIDENCE_DIRECTORY = "experiments/rust_public_practice_v1"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
ORACLE_RELATIVE = "tools/independent_substitution_buffer_semantics_v2.py"
ORACLE_SHA256 = (
    "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573"
)
RECORDER_RELATIVE = (
    "tools/record_independent_substitution_buffer_semantics_v3.py"
)
RECORDER_SHA256 = (
    "1e6bd77cea22c511ca3ee0ccdd4c02b12b4aa22c4fb79cb0df74d2894280807c"
)
PREVIOUS_RECORDER_RELATIVE = (
    "tools/record_independent_substitution_buffer_semantics_v1.py"
)
PREVIOUS_RECORDER_SHA256 = (
    "1dbb45e8950a0eceb966a56adcbe2f9d1da35ec04883458a780b6f08f5a4735d"
)
PRESERVED_PREVIOUS_FAILURE_RELATIVE = (
    "experiments/rust_public_practice_v1/"
    "substitution-buffer-semantics-v1-shared-suite-v1-"
    "controller-failure-v1.json"
)
PRESERVED_PREVIOUS_FAILURE_SHA256 = (
    "a80316f3d1fe87808c8f16cb651393d275132d408633303da16a5142f55ba807"
)
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
POLICY_V2_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
POLICY_V2_SHA256 = (
    "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
)
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
MATRIX_SHA256 = (
    "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54"
)
PUBLISHED_SEED = 6_004_778_603_531_028_017
VARIANTS_PER_COHORT = 80
COHORTS = (
    "text-literal",
    "text-escaped",
    "text-callback",
    "text-callback-error",
    "text-named-captures",
    "text-numeric-captures",
    "text-missing-capture",
    "text-invalid-escape",
    "text-zero-width-lookahead",
    "text-zero-width-empty",
    "text-count-limit",
    "text-window-pos-endpos",
    "text-lone-surrogate",
    "text-combining-mark",
    "text-precomposed-unicode",
    "text-cross-domain-bytes-template",
    "bytes-literal",
    "bytes-escaped",
    "bytes-callback",
    "bytes-callback-error",
    "bytes-named-captures",
    "bytes-numeric-captures",
    "bytes-missing-capture",
    "bytes-invalid-escape",
    "bytes-zero-width-lookahead",
    "bytes-zero-width-empty",
    "bytes-count-limit",
    "bytes-window-pos-endpos",
    "bytearray-subject-literal",
    "bytearray-subject-escaped",
    "bytearray-replacement-literal",
    "bytearray-replacement-escaped",
    "readonly-subject-memoryview",
    "writable-subject-memoryview",
    "readonly-strided-subject-memoryview",
    "writable-strided-subject-memoryview",
    "released-readonly-subject-memoryview",
    "released-writable-subject-memoryview",
    "readonly-template-memoryview",
    "writable-template-memoryview",
    "readonly-strided-template-memoryview",
    "writable-strided-template-memoryview",
    "released-readonly-template-memoryview",
    "released-writable-template-memoryview",
    "pep688-stable-subject",
    "pep688-mutating-subject",
    "pep688-failing-subject",
    "pep688-fixed-hash-subject",
    "pep688-unhashable-subject",
    "pep688-stable-template",
    "pep688-mutating-template",
    "pep688-failing-template",
    "pep688-fixed-hash-template",
    "pep688-unhashable-template",
    "pep688-failing-hash-template",
    "pep688-wrapped-readonly-subject",
    "pep688-wrapped-writable-subject",
    "nested-stable-subject-and-template",
    "nested-mutating-subject-and-template",
    "nested-stable-fixed-hash-template",
    "nested-mutating-unhashable-template",
    "nested-failing-template-after-subject",
    "match-expand-buffer-retention",
    "callback-capture-and-buffer-order",
)

CASE_COUNT = 5_120
APIS = (
    "module.sub",
    "module.subn",
    "pattern.sub",
    "pattern.subn",
    "match.expand",
)
SIMPLE_BUFFER_FLAG = 0
FULL_READONLY_BUFFER_FLAG = 284
BASELINE_LABEL = "shared-suite-v2"
BASELINE_ARCHIVE_RELATIVE = (
    EVIDENCE_DIRECTORY
    + "/substitution-buffer-semantics-v2-shared-suite-v2.json.gz"
)
BASELINE_ARCHIVE_SHA256 = (
    "2037e28bd452e00950819451786bc4212c6c685061f4122d27f5baa6b82dd12e"
)
BASELINE_ARCHIVE_BYTES = 6_362_950
BASELINE_RECEIPT_RELATIVE = (
    EVIDENCE_DIRECTORY
    + "/substitution-buffer-semantics-v2-shared-suite-v2-"
    "publication-receipt.json"
)
BASELINE_RECEIPT_SHA256 = (
    "be2e495d1f983c7f59073490df90935562b94a241855cea0dbc870800ba73171"
)
BASELINE_REPORT_SHA256 = (
    "1c7bde361897c44e39c44503e4fe39de48a6a6d2b7f2d6fe1fa1f615fb403561"
)
BASELINE_REPORT_BYTES = 87_138_140
BASELINE_RECORDS_SHA256 = (
    "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b"
)
C_LABEL = "native-lifetime-repair-v1"
C_ARCHIVE_RELATIVE = (
    EVIDENCE_DIRECTORY
    + "/c-substitution-buffer-semantics-v1-native-lifetime-repair-v1.json.gz"
)
C_ARCHIVE_SHA256 = (
    "b1545e5850caaf59fd9640358527dfaf160f90b3f48fc9f80accd5a49a305111"
)
C_ARCHIVE_BYTES = 839_723
C_RECEIPT_RELATIVE = (
    EVIDENCE_DIRECTORY
    + "/c-substitution-buffer-semantics-v1-native-lifetime-repair-v1-"
    "publication-receipt.json"
)
C_RECEIPT_SHA256 = (
    "933852815241f3b2c82f6e5a07a5624422c323c7d4f86cebeb3f6f700cefa5b2"
)
C_REPORT_SHA256 = (
    "cd6ed6aa853f51989e473b0cfe3a5d8b4cd8c8576d758919954e27cd4de4ed7c"
)
C_REPORT_BYTES = 18_841_043
C_RECORDS_SHA256 = (
    "39e318519c1b463c853103b14c099df56b974c595a6a5301bad91e386fabbf04"
)
C_MISMATCH_EVIDENCE_SHA256 = (
    "dd3662164eddb3ac983f9618f0b53a2c52fbbe31f8cc456731109ef89cad9f13"
)
ZIG_LABEL = "owned-safe-buffer-repair-v1"
ZIG_ARCHIVE_RELATIVE = (
    EVIDENCE_DIRECTORY
    + "/zig-substitution-buffer-semantics-v1-"
    "owned-safe-buffer-repair-v1.json.gz"
)
ZIG_ARCHIVE_SHA256 = (
    "8adefae4fb5248d3a95cefc852bfafa9dfca39d0d868a0b424df6394eef9a402"
)
ZIG_ARCHIVE_BYTES = 815_309
ZIG_RECEIPT_RELATIVE = (
    EVIDENCE_DIRECTORY
    + "/zig-substitution-buffer-semantics-v1-"
    "owned-safe-buffer-repair-v1-publication-receipt.json"
)
ZIG_RECEIPT_SHA256 = (
    "89d5f12fb076b4152cf14a12d6fd22f18a0ba99c07a82a2a8efdb4d1ff12a03e"
)
ZIG_REPORT_SHA256 = (
    "0d6b6a5878e408125e09177f36003004da161c2104af297d41ac2331ed0a8c93"
)
ZIG_REPORT_BYTES = 18_750_611
ZIG_RECORDS_SHA256 = (
    "027bb34006927e9f86134b7c6f29ebf81b331b077b1133f4d12af6267cfb4a1b"
)
ZIG_MISMATCH_EVIDENCE_SHA256 = (
    "a01c0e3a9bbe11be08502e2469f9052f31748520fc5cd513ea20795719d4a48a"
)


HISTORICAL_V1_STATUS = "FALSIFIED"
HISTORICAL_V1_BASELINE_LABEL = "shared-suite-v1"
HISTORICAL_V1_ORACLE_RELATIVE = "tools/independent_substitution_buffer_semantics_v1.py"
HISTORICAL_V1_ORACLE_SHA256 = (
    "a325528aa62f107969b9dfdf5dea2ae8f9426607887a317fe20fcf9a1b7fd445"
)
HISTORICAL_V1_RENDERER_RELATIVE = (
    "tools/render_substitution_buffer_overview_v1.py"
)
HISTORICAL_V1_RENDERER_SHA256 = (
    "13183b23a77e7e4757d160d83363dd5a5be08ee287c4e2eceef8ab0c4afaa6f2"
)
HARDENED_PREDECESSOR_RELATIVE = (
    "tools/record_independent_substitution_buffer_semantics_v2.py"
)
HARDENED_PREDECESSOR_SHA256 = (
    "a7cf45ce72a178fead7eb0d0789fd1f0f37ed63789fe086070eefa613e959a33"
)
HISTORICAL_V1_BASELINE_ARCHIVE_RELATIVE = (
    EVIDENCE_DIRECTORY
    + "/substitution-buffer-semantics-v1-shared-suite-v1.json.gz"
)
HISTORICAL_V1_BASELINE_ARCHIVE_SHA256 = (
    "2e24e17862e75f4f2f778d15d67416f6e643eff01c0d110e750cea99b2550fab"
)
HISTORICAL_V1_REPORTED_FAILURE_COUNTS = {"c": 464, "zig": 192}
HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS = {"c": 128, "zig": 128}
HISTORICAL_V1_REAL_FAILURE_COUNTS = {"c": 336, "zig": 64}

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_RECEIPT_BYTES = MAX_SOURCE_BYTES
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_ENCODED_PROCESS_STREAM_BYTES = 128 * 1024 * 1024
MAX_COMPACT_REPORT_METADATA_BYTES = 32 * 1024 * 1024
MAX_COMPACT_REPORT_BYTES = 288 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 320 * 1024 * 1024
MAX_ARCHIVE_BYTES = 384 * 1024 * 1024
MAX_SELECTED_VALUE_BYTES = MAX_COMPACT_REPORT_BYTES
CHUNK_BYTES = 131_072
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
FAMILY_ORDER = ("rust", "c", "zig")
FAMILY_LABELS = {
    "python": "Python baseline",
    "rust": "Rust",
    "c": "C",
    "zig": "Zig",
}
FAMILY_SPECS: dict[str, tuple[str, str, str, tuple[str, ...]]] = {
    "rust": (
        "candidates/rust_candidate.py",
        "candidates/_rust_engine.so",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/rust_candidate.py",
            "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml",
            "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs",
            "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs",
            "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
    ),
    "c": (
        "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    ),
    "zig": (
        "candidates/zig_candidate.py",
        "candidates/_zig_probe.so",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
    ),
}
FORBIDDEN_ROOTS = frozenset({
    "candidates", "_regex", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "rebar", "regex",
    "rust_regex", "sre_compile", "sre_constants", "sre_parse",
    "vectorscan",
})


class OverviewError(Exception):
    """A frozen complete replacement-and-buffer observation was changed."""


class SourceOnlyError(OverviewError):
    """A solely in-memory control attempted an external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OverviewError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (
        TypeError,
        ValueError,
        UnicodeError,
        OverflowError,
        RecursionError,
    ) as error:
        raise OverviewError("exact canonical evidence is mandatory") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_hash(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def fixed_fields(
    value: Mapping[str, Any],
    expected: Mapping[str, Any],
    label: str,
) -> None:
    require(isinstance(value, Mapping), label + " is not a complete object")
    for field, original in expected.items():
        require(
            field in value
            and type(value[field]) is type(original)
            and value[field] == original,
            label + " changed: " + field,
        )


def safe_parts(value: Any) -> tuple[str, ...]:
    require(
        type(value) is str
        and bool(value)
        and "\\" not in value
        and "\x00" not in value,
        "an exact safe relative path is mandatory",
    )
    parts = tuple(value.split("/"))
    require(
        all(part not in {"", ".", ".."} for part in parts)
        and "/".join(parts) == value,
        "a frozen input or graph output escaped the project root",
    )
    return parts


def validate_label(value: Any) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    require(
        type(value) is str
        and 1 <= len(value) <= 64
        and value[0] in alphabet
        and value[-1] in alphabet
        and all(character in alphabet + "-" for character in value)
        and "--" not in value,
        "an exact bounded lowercase evidence label is mandatory",
    )
    return value


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(
            type(key) is str and key not in result,
            "a duplicate evidence field can hide a real failure",
        )
        result[key] = value
    return result


def decode_document(
    raw: Any,
    label: str,
    maximum: int = MAX_RECEIPT_BYTES,
) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= maximum,
        "complete bounded canonical evidence is mandatory: " + label,
    )

    def reject_constant(_: str) -> None:
        raise OverviewError("nonfinite evidence is forbidden")

    try:
        document = json.loads(
            raw,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (
        OverviewError,
        TypeError,
        ValueError,
        UnicodeError,
        RecursionError,
    ) as error:
        raise OverviewError("invalid complete evidence: " + label) from error
    require(
        type(document) is dict and canonical(document) == raw,
        "evidence was truncated, reordered, duplicated, or gained a suffix",
    )
    return document

BASELINE_RECEIPT_FIELDS = frozenset({
    "actual_baseline_controller_invocations",
    "actual_candidate_imports",
    "actual_candidate_workers",
    "actual_reference_workers",
    "apis",
    "approved_fresh_path_count",
    "baseline_records_sha256",
    "baseline_reference_pids",
    "baseline_result_status",
    "benchmark_files_read",
    "candidate_qualified_for_hidden_benchmark",
    "case_count",
    "clock_samples",
    "cohort_count",
    "cohorts",
    "final_winner_selected",
    "fresh_paths_checked_before_baseline",
    "full_readonly_buffer_flag",
    "hardened_predecessor_relative",
    "hardened_predecessor_sha256",
    "historical_v1_oracle_artifact_counts",
    "historical_v1_oracle_relative",
    "historical_v1_oracle_sha256",
    "historical_v1_real_failure_counts",
    "historical_v1_reported_failure_counts",
    "historical_v1_status",
    "hidden_cases_read",
    "label",
    "matrix_sha256",
    "maximum_archive_bytes",
    "maximum_compact_report_bytes",
    "maximum_compact_report_metadata_bytes",
    "maximum_encoded_process_stream_bytes",
    "maximum_process_stream_count",
    "maximum_raw_process_stream_bytes",
    "maximum_uncompressed_bytes",
    "oracle_relative",
    "oracle_source_sha256",
    "original_v5_relative",
    "original_v5_sha256",
    "ownership_audit_relative",
    "ownership_audit_sha256",
    "performance",
    "preserved_previous_failure_relative",
    "preserved_previous_failure_sha256",
    "previous_recorder_relative",
    "previous_recorder_sha256",
    "published_seed",
    "published_seed_decimal",
    "python",
    "receipt_relative",
    "recorder_relative",
    "recorder_source_sha256",
    "report_atomic_no_overwrite_link",
    "report_bytes",
    "report_complete_readback_verified",
    "report_compression",
    "report_directory_fsync_completed",
    "report_file_fsync_completed",
    "report_relative",
    "report_sha256",
    "report_uncompressed_bytes",
    "report_uncompressed_sha256",
    "schema",
    "simple_buffer_flag",
    "source_closure_after",
    "source_closure_before",
    "source_closure_unchanged",
    "status",
    "timing_trials_run",
    "validated_reference_a_case_count",
    "validated_reference_b_case_count",
    "variants_per_cohort",
})

CANDIDATE_RECEIPT_FIELDS = frozenset({
    "actual_candidate_imports",
    "actual_candidate_process_invocations",
    "actual_candidate_workers",
    "actual_method_guard_checks",
    "actual_reference_workers",
    "actual_warning_registry_guard_checks",
    "all_mismatches_preserved",
    "apis",
    "approved_fresh_path_count",
    "baseline_archive_relative",
    "baseline_archive_sha256",
    "baseline_label",
    "baseline_receipt_relative",
    "baseline_receipt_sha256",
    "baseline_records_sha256",
    "baseline_reference_pids",
    "benchmark_files_read",
    "candidate_family",
    "candidate_owner_after",
    "candidate_owner_before",
    "candidate_owner_unchanged",
    "candidate_qualified_for_hidden_benchmark",
    "candidate_records_sha256",
    "candidate_result_status",
    "candidate_source_sha256",
    "case_count",
    "clock_samples",
    "cohort_count",
    "cohorts",
    "final_winner_selected",
    "fresh_paths_checked_before_candidate",
    "full_readonly_buffer_flag",
    "hardened_predecessor_relative",
    "hardened_predecessor_sha256",
    "historical_v1_oracle_artifact_counts",
    "historical_v1_oracle_relative",
    "historical_v1_oracle_sha256",
    "historical_v1_real_failure_counts",
    "historical_v1_reported_failure_counts",
    "historical_v1_status",
    "hidden_cases_read",
    "label",
    "matrix_sha256",
    "maximum_archive_bytes",
    "maximum_compact_report_bytes",
    "maximum_compact_report_metadata_bytes",
    "maximum_encoded_process_stream_bytes",
    "maximum_process_stream_count",
    "maximum_raw_process_stream_bytes",
    "maximum_uncompressed_bytes",
    "mismatch_count",
    "mismatch_evidence_sha256",
    "mismatches_by_api",
    "mismatches_by_cohort",
    "native_bridge_sha256",
    "native_engine_sha256",
    "oracle_source_sha256",
    "original_v5_sha256",
    "ownership_audit_sha256",
    "performance",
    "preserved_previous_failure_relative",
    "preserved_previous_failure_sha256",
    "previous_recorder_relative",
    "previous_recorder_sha256",
    "published_seed",
    "published_seed_decimal",
    "python",
    "receipt_relative",
    "recorder_source_sha256",
    "report_atomic_no_overwrite_link",
    "report_bytes",
    "report_complete_readback_verified",
    "report_compression",
    "report_directory_fsync_completed",
    "report_file_fsync_completed",
    "report_relative",
    "report_sha256",
    "report_uncompressed_bytes",
    "report_uncompressed_sha256",
    "schema",
    "simple_buffer_flag",
    "status",
    "timing_trials_run",
    "validated_baseline_record_count",
    "validated_candidate_record_count",
    "validated_prior_reference_workers",
    "variants_per_cohort",
})

BASELINE_FIELDS = frozenset({
    "actual_baseline_controller_invocations",
    "actual_baseline_controller_pid",
    "actual_baseline_process_returncode",
    "actual_baseline_process_signal",
    "actual_baseline_process_spawn_error",
    "actual_baseline_process_timed_out",
    "actual_candidate_imports",
    "actual_candidate_workers",
    "actual_reference_workers",
    "all_failure_reasons",
    "apis",
    "baseline_failure_schema",
    "baseline_records_sha256",
    "baseline_reference_pids",
    "baseline_result_reconstruction",
    "baseline_result_sha256",
    "benchmark_files_read",
    "candidate_qualified_for_hidden_benchmark",
    "case_count",
    "clock_samples",
    "cohort_count",
    "cohorts",
    "complete_baseline_process_stderr",
    "complete_baseline_process_stdout",
    "complete_process_representation",
    "failure_count",
    "final_winner_selected",
    "full_readonly_buffer_flag",
    "hardened_predecessor_relative",
    "hardened_predecessor_sha256",
    "historical_v1_oracle_artifact_counts",
    "historical_v1_oracle_relative",
    "historical_v1_oracle_sha256",
    "historical_v1_real_failure_counts",
    "historical_v1_reported_failure_counts",
    "historical_v1_status",
    "hidden_cases_read",
    "label",
    "matrix_sha256",
    "maximum_archive_bytes",
    "maximum_compact_report_bytes",
    "maximum_compact_report_metadata_bytes",
    "maximum_encoded_process_stream_bytes",
    "maximum_process_stream_count",
    "maximum_raw_process_stream_bytes",
    "maximum_uncompressed_bytes",
    "oracle_relative",
    "oracle_source_sha256",
    "original_v5_relative",
    "original_v5_sha256",
    "ownership_audit_relative",
    "ownership_audit_sha256",
    "performance",
    "preserved_previous_failure_relative",
    "preserved_previous_failure_sha256",
    "previous_recorder_relative",
    "previous_recorder_sha256",
    "published_seed",
    "published_seed_decimal",
    "python",
    "recorder_relative",
    "recorder_source_sha256",
    "schema",
    "simple_buffer_flag",
    "source_closure_after",
    "source_closure_before",
    "source_closure_unchanged",
    "status",
    "timing_trials_run",
    "validated_reference_a_case_count",
    "validated_reference_b_case_count",
    "variants_per_cohort",
})

CANDIDATE_FIELDS = frozenset({
    "actual_candidate_imports",
    "actual_candidate_pid",
    "actual_candidate_process_invocations",
    "actual_candidate_process_returncode",
    "actual_candidate_process_signal",
    "actual_candidate_process_spawn_error",
    "actual_candidate_process_timed_out",
    "actual_candidate_workers",
    "actual_method_guard_checks",
    "actual_reference_workers",
    "actual_warning_registry_guard_checks",
    "all_failure_reasons",
    "all_mismatches",
    "all_mismatches_preserved",
    "apis",
    "baseline_archive_relative",
    "baseline_archive_sha256",
    "baseline_label",
    "baseline_receipt_relative",
    "baseline_receipt_sha256",
    "baseline_records_reconstruction",
    "baseline_records_sha256",
    "baseline_reference_pids",
    "benchmark_files_read",
    "candidate_family",
    "candidate_owner_after",
    "candidate_owner_before",
    "candidate_owner_unchanged",
    "candidate_qualified_for_hidden_benchmark",
    "candidate_records_reconstruction",
    "candidate_records_sha256",
    "candidate_source_sha256",
    "case_count",
    "clock_samples",
    "cohort_count",
    "cohorts",
    "complete_candidate_process_stderr",
    "complete_candidate_process_stdout",
    "complete_process_representation",
    "failure_count",
    "final_winner_selected",
    "full_readonly_buffer_flag",
    "hardened_predecessor_relative",
    "hardened_predecessor_sha256",
    "historical_v1_oracle_artifact_counts",
    "historical_v1_oracle_relative",
    "historical_v1_oracle_sha256",
    "historical_v1_real_failure_counts",
    "historical_v1_reported_failure_counts",
    "historical_v1_status",
    "hidden_cases_read",
    "label",
    "matrix_sha256",
    "maximum_archive_bytes",
    "maximum_compact_report_bytes",
    "maximum_compact_report_metadata_bytes",
    "maximum_encoded_process_stream_bytes",
    "maximum_process_stream_count",
    "maximum_raw_process_stream_bytes",
    "maximum_uncompressed_bytes",
    "mismatch_count",
    "mismatch_evidence_sha256",
    "mismatch_outcome_reconstruction",
    "mismatches_by_api",
    "mismatches_by_cohort",
    "native_bridge_sha256",
    "native_engine_sha256",
    "oracle_relative",
    "oracle_source_sha256",
    "original_v5_relative",
    "original_v5_sha256",
    "ownership_audit_relative",
    "ownership_audit_sha256",
    "performance",
    "preserved_previous_failure_relative",
    "preserved_previous_failure_sha256",
    "previous_recorder_relative",
    "previous_recorder_sha256",
    "published_seed",
    "published_seed_decimal",
    "python",
    "recorder_relative",
    "recorder_source_sha256",
    "schema",
    "simple_buffer_flag",
    "status",
    "timing_trials_run",
    "validated_baseline_record_count",
    "validated_candidate_record_count",
    "validated_prior_reference_workers",
    "variants_per_cohort",
})

def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == ROOT + "/" + SOURCE_RELATIVE
        and os.path.realpath(__file__) == ROOT + "/" + SOURCE_RELATIVE,
        "use only this exact source and isolated pinned Python 3.14.6",
    )
    for name in tuple(sys.modules):
        require(
            type(name) is str
            and name.partition(".")[0] not in FORBIDDEN_ROOTS,
            "the substitution-buffer chart imported an implementation or engine",
        )

def validate_owned_limit(value: Any) -> int:
    require(
        type(value) is int
        and 0 < value <= MAX_ARCHIVE_BYTES,
        "an exact bounded project-owned graph input is mandatory",
    )
    return value

@contextlib.contextmanager
def open_owned(
    relative: str,
    maximum: int,
) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_parts(relative)
    maximum = validate_owned_limit(maximum)
    regular = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directory_flags = regular | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        require(
            stat.S_ISDIR(os.fstat(current).st_mode),
            "the exact graph workspace was substituted",
        )
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "a frozen substitution-buffer parent became a symlink",
            )
        descriptor = os.open(parts[-1], regular, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(
            parts[-1],
            dir_fd=current,
            follow_symlinks=False,
        )
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (
                before.st_dev, before.st_ino, before.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            )
            and 0 < before.st_size <= maximum,
            "an owned no-follow graph input was substituted or oversized",
        )
        yield descriptor, before
        final = os.fstat(descriptor)
        named = os.stat(
            parts[-1],
            dir_fd=current,
            follow_symlinks=False,
        )
        require(
            (
                before.st_dev, before.st_ino, before.st_size,
            ) == (
                final.st_dev, final.st_ino, final.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            ),
            "a source-pinned correctness input changed while being read",
        )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)

def read_frozen(
    relative: str,
    source: str,
    maximum: int,
) -> bytes:
    expected = valid_hash(source, relative)
    with open_owned(relative, maximum) as (descriptor, info):
        remaining = info.st_size
        observed = hashlib.sha256()
        chunks: list[bytes] = []
        while remaining:
            block = os.read(
                descriptor,
                min(CHUNK_BYTES, remaining),
            )
            require(
                type(block) is bytes and bool(block),
                "a frozen substitution-buffer input was truncated",
            )
            observed.update(block)
            remaining -= len(block)
            chunks.append(block)
        require(
            os.read(descriptor, 1) == b""
            and observed.hexdigest() == expected,
            "a frozen substitution-buffer source failed its exact SHA-256",
        )
        return b"".join(chunks)

class VerifiedGzipReader:
    """Authenticate exactly one complete, bounded frozen gzip member."""

    def __init__(
        self,
        descriptor: int,
        archive_bytes: int,
        archive_sha256: str,
        original_bytes: int,
        original_sha256: str,
    ) -> None:
        require(
            type(descriptor) is int
            and type(archive_bytes) is int
            and 0 < archive_bytes <= MAX_ARCHIVE_BYTES
            and type(original_bytes) is int
            and 0 < original_bytes <= MAX_UNCOMPRESSED_BYTES,
            "exact bounded compressed and original evidence is mandatory",
        )
        self.descriptor = descriptor
        self.archive_bytes = archive_bytes
        self.archive_sha256 = valid_hash(
            archive_sha256,
            "complete substitution-buffer gzip",
        )
        self.original_bytes = original_bytes
        self.original_sha256 = valid_hash(
            original_sha256,
            "complete restored substitution-buffer report",
        )
        self.inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self.compressed_hash = hashlib.sha256()
        self.original_hash = hashlib.sha256()
        self.compressed_count = 0
        self.original_count = 0
        self.pending = b""
        self.finished = False

    def read(self, requested: int) -> bytes:
        require(
            type(requested) is int and 0 < requested <= CHUNK_BYTES,
            "stream only bounded complete frozen evidence blocks",
        )
        result = bytearray()
        while len(result) < requested and not self.finished:
            if (
                not self.pending
                and self.compressed_count < self.archive_bytes
            ):
                block = os.read(
                    self.descriptor,
                    min(
                        CHUNK_BYTES,
                        self.archive_bytes - self.compressed_count,
                    ),
                )
                require(
                    type(block) is bytes and bool(block),
                    "a genuinely authenticated gzip was truncated",
                )
                self.compressed_count += len(block)
                self.compressed_hash.update(block)
                self.pending = block
            if self.pending:
                limit = min(
                    requested - len(result),
                    self.original_bytes - self.original_count + 1,
                )
                try:
                    plain = self.inflater.decompress(
                        self.pending,
                        limit,
                    )
                except (
                    zlib.error, ValueError, OverflowError,
                ) as error:
                    raise OverviewError(
                        "the substitution-buffer gzip archive is invalid",
                    ) from error
                require(
                    not self.inflater.unused_data,
                    "extra gzip members and trailing bytes are forbidden",
                )
                self.pending = self.inflater.unconsumed_tail
                if plain:
                    self.original_count += len(plain)
                    require(
                        self.original_count <= self.original_bytes,
                        "gzip expansion exceeded its frozen safe bound",
                    )
                    self.original_hash.update(plain)
                    result.extend(plain)
                continue
            require(
                self.compressed_count == self.archive_bytes
                and self.inflater.eof
                and not self.inflater.unused_data
                and os.read(self.descriptor, 1) == b"",
                "a complete single-member gzip footer is mandatory",
            )
            try:
                tail = self.inflater.flush(CHUNK_BYTES)
            except (zlib.error, ValueError) as error:
                raise OverviewError(
                    "the lossless substitution-buffer gzip footer is invalid",
                ) from error
            require(
                not tail
                and self.compressed_hash.hexdigest()
                == self.archive_sha256
                and self.original_count == self.original_bytes
                and self.original_hash.hexdigest()
                == self.original_sha256,
                "a complete lossless report failed its exact size or SHA-256",
            )
            self.finished = True
        return bytes(result)

def reject_nonfinite_stream_value(_: str) -> None:
    raise OverviewError("nonfinite complete streamed evidence is forbidden")


class StreamingObject:
    """Validate every report field while streaming its authenticated gzip."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.utf8 = codecs.getincrementaldecoder("utf-8")("strict")
        self.decoder = json.JSONDecoder(
            object_pairs_hook=unique_object,
            parse_constant=reject_nonfinite_stream_value,
        )
        self.buffer = ""
        self.position = 0
        self.ended = False

    def fill(self) -> bool:
        if self.ended:
            return False
        block = self.stream.read(CHUNK_BYTES)
        require(
            type(block) is bytes,
            "a streamed complete report emitted non-byte evidence",
        )
        if not block:
            self.buffer += self.utf8.decode(b"", final=True)
            self.ended = True
            return False
        self.buffer += self.utf8.decode(block, final=False)
        return True

    def compact(self) -> None:
        if self.position >= 2 * CHUNK_BYTES:
            self.buffer = self.buffer[self.position:]
            self.position = 0

    def peek(self) -> str | None:
        while self.position == len(self.buffer) and self.fill():
            pass
        if self.position < len(self.buffer):
            return self.buffer[self.position]
        return None

    def take(self) -> str:
        value = self.peek()
        require(
            value is not None,
            "the complete substitution-buffer report was truncated",
        )
        self.position += 1
        return value

    def whitespace(self) -> None:
        while self.peek() in (" ", "\t", "\r", "\n"):
            self.position += 1
            self.compact()

    def literal(self, expected: str) -> None:
        self.whitespace()
        require(
            self.take() == expected,
            "an authenticated report delimiter was substituted",
        )

    def value(self) -> Any:
        self.whitespace()
        self.compact()
        while True:
            try:
                result, ending = self.decoder.raw_decode(
                    self.buffer,
                    self.position,
                )
            except json.JSONDecodeError as error:
                require(
                    not self.ended,
                    "a complete streamed JSON value was clipped",
                )
                require(
                    len(self.buffer) - self.position
                    <= MAX_SELECTED_VALUE_BYTES,
                    "a complete streamed worker exceeds its safe bound",
                )
                if not self.fill():
                    raise OverviewError(
                        "a complete streamed JSON value is missing",
                    ) from error
                continue
            self.position = ending
            return result

    def skip(self) -> None:
        self.whitespace()
        first = self.peek()
        require(
            first is not None,
            "a complete report value was truncated",
        )
        if first == '"':
            self.take()
            escaped = False
            while True:
                item = self.take()
                if escaped:
                    escaped = False
                elif item == "\\":
                    escaped = True
                elif item == '"':
                    return
                self.compact()
        elif first in ("{", "["):
            stack: list[str] = []
            quoted = False
            escaped = False
            while True:
                item = self.take()
                if quoted:
                    if escaped:
                        escaped = False
                    elif item == "\\":
                        escaped = True
                    elif item == '"':
                        quoted = False
                elif item == '"':
                    quoted = True
                elif item in ("{", "["):
                    stack.append("}" if item == "{" else "]")
                elif item in ("}", "]"):
                    require(
                        bool(stack) and stack[-1] == item,
                        "an unselected complete JSON container is invalid",
                    )
                    stack.pop()
                    if not stack:
                        return
                self.compact()
        else:
            beginning = self.position
            while True:
                item = self.peek()
                if item is None or item in (
                    ",", "}", "]", " ", "\t", "\r", "\n",
                ):
                    break
                self.position += 1
            raw = self.buffer[beginning:self.position]
            try:
                _, ending = self.decoder.raw_decode(raw)
            except json.JSONDecodeError as error:
                raise OverviewError(
                    "an unselected complete JSON scalar was forged",
                ) from error
            require(
                ending == len(raw),
                "an unselected complete JSON scalar was corrupted",
            )

    def select(self, fields: frozenset[str]) -> dict[str, Any]:
        require(
            type(fields) is frozenset and bool(fields),
            "an exact complete streamed evidence schema is mandatory",
        )
        self.literal("{")
        found: set[str] = set()
        result: dict[str, Any] = {}
        self.whitespace()
        if self.peek() == "}":
            self.take()
        else:
            while True:
                key = self.value()
                require(
                    type(key) is str and key not in found,
                    "a complete report field was duplicated",
                )
                found.add(key)
                self.literal(":")
                if key in fields:
                    result[key] = self.value()
                else:
                    self.skip()
                self.whitespace()
                ending = self.take()
                if ending == "}":
                    break
                require(
                    ending == ",",
                    "a complete report separator was substituted",
                )
        self.whitespace()
        require(
            self.peek() is None
            and found == fields
            and set(result) == fields,
            "a complete report field was omitted, injected, or concealed",
        )
        return result

def frozen_bounds() -> dict[str, int]:
    require(
        len(COHORTS) == 64
        and len(set(COHORTS)) == 64
        and len(APIS) == 5
        and len(set(APIS)) == 5
        and CASE_COUNT == 5_120
        and VARIANTS_PER_COHORT == 80
        and len(COHORTS) * VARIANTS_PER_COHORT == CASE_COUNT
        and PUBLISHED_SEED == 6_004_778_603_531_028_017
        and MAX_PROCESS_BYTES == 96 * 1024 * 1024
        and MAX_ENCODED_PROCESS_STREAM_BYTES == 128 * 1024 * 1024
        and MAX_COMPACT_REPORT_METADATA_BYTES == 32 * 1024 * 1024
        and MAX_COMPACT_REPORT_BYTES == 288 * 1024 * 1024
        and MAX_UNCOMPRESSED_BYTES == 320 * 1024 * 1024
        and MAX_ARCHIVE_BYTES == 384 * 1024 * 1024
        and MAX_COMPACT_REPORT_BYTES < MAX_UNCOMPRESSED_BYTES
        and MAX_UNCOMPRESSED_BYTES < MAX_ARCHIVE_BYTES,
        "the complete 5,120-case matrix or proven V2 byte ceilings changed",
    )
    return {
        "maximum_raw_process_stream_bytes": MAX_PROCESS_BYTES,
        "maximum_encoded_process_stream_bytes": (
            MAX_ENCODED_PROCESS_STREAM_BYTES
        ),
        "maximum_process_stream_count": 2,
        "maximum_compact_report_metadata_bytes": (
            MAX_COMPACT_REPORT_METADATA_BYTES
        ),
        "maximum_compact_report_bytes": MAX_COMPACT_REPORT_BYTES,
        "maximum_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "maximum_archive_bytes": MAX_ARCHIVE_BYTES,
    }


def evidence_pin(
    value: Any,
    seen: set[str],
    *,
    reuse: bool = False,
) -> tuple[str, str]:
    require(
        type(value) is dict and set(value) == {"relative", "sha256"},
        "every complete signed evidence path and SHA-256 is mandatory",
    )
    relative = value["relative"]
    require(
        safe_parts(relative)[:2]
        == safe_parts(EVIDENCE_DIRECTORY),
        "a signed report escaped its exact evidence directory",
    )
    source = valid_hash(value["sha256"], relative)
    if not reuse:
        require(
            relative not in seen,
            "a report, receipt, or historical loss was counted twice",
        )
        seen.add(relative)
    return relative, source


def report_pin(relative: str, source: str) -> dict[str, str]:
    safe_parts(relative)
    return {
        "relative": relative,
        "sha256": valid_hash(source, relative),
    }



def historical_lineage_fields() -> dict[str, Any]:
    return {
        "historical_v1_status": HISTORICAL_V1_STATUS,
        "historical_v1_oracle_relative": HISTORICAL_V1_ORACLE_RELATIVE,
        "historical_v1_oracle_sha256": HISTORICAL_V1_ORACLE_SHA256,
        "hardened_predecessor_relative": HARDENED_PREDECESSOR_RELATIVE,
        "hardened_predecessor_sha256": HARDENED_PREDECESSOR_SHA256,
        "historical_v1_reported_failure_counts": dict(
            HISTORICAL_V1_REPORTED_FAILURE_COUNTS,
        ),
        "historical_v1_oracle_artifact_counts": dict(
            HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS,
        ),
        "historical_v1_real_failure_counts": dict(
            HISTORICAL_V1_REAL_FAILURE_COUNTS,
        ),
    }


def historical_v1_manifest() -> dict[str, Any]:
    return {
        "status": HISTORICAL_V1_STATUS,
        "oracle": report_pin(
            HISTORICAL_V1_ORACLE_RELATIVE, HISTORICAL_V1_ORACLE_SHA256,
        ),
        "previous_renderer": report_pin(
            HISTORICAL_V1_RENDERER_RELATIVE, HISTORICAL_V1_RENDERER_SHA256,
        ),
        "baseline_archive": report_pin(
            HISTORICAL_V1_BASELINE_ARCHIVE_RELATIVE,
            HISTORICAL_V1_BASELINE_ARCHIVE_SHA256,
        ),
        "c_archive": report_pin(C_ARCHIVE_RELATIVE, C_ARCHIVE_SHA256),
        "c_receipt": report_pin(C_RECEIPT_RELATIVE, C_RECEIPT_SHA256),
        "zig_archive": report_pin(ZIG_ARCHIVE_RELATIVE, ZIG_ARCHIVE_SHA256),
        "zig_receipt": report_pin(ZIG_RECEIPT_RELATIVE, ZIG_RECEIPT_SHA256),
        "reported_failure_counts": dict(HISTORICAL_V1_REPORTED_FAILURE_COUNTS),
        "oracle_artifact_counts": dict(HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS),
        "genuine_remaining_difference_counts": dict(
            HISTORICAL_V1_REAL_FAILURE_COUNTS,
        ),
    }


def read_archive(
    relative: str,
    archive_hash: str,
    fields: frozenset[str],
    original_hash: str,
    original_bytes: int,
    archive_bytes: int,
) -> dict[str, Any]:
    with open_owned(relative, MAX_ARCHIVE_BYTES) as (
        descriptor,
        info,
    ):
        require(
            info.st_size == archive_bytes,
            "the complete lossless gzip changed its exact signed size",
        )
        stream = VerifiedGzipReader(
            descriptor,
            archive_bytes,
            archive_hash,
            original_bytes,
            original_hash,
        )
        value = StreamingObject(stream).select(fields)
        require(
            stream.finished,
            "a full signed candidate or baseline archive was not restored",
        )
        return value


Loader = Callable[
    [str, str, str, str | None, int | None, int | None],
    dict[str, Any],
]


def actual_loader(
    relative: str,
    expected: str,
    kind: str,
    original_hash: str | None,
    original_bytes: int | None,
    archive_bytes: int | None,
) -> dict[str, Any]:
    safe_parts(relative)
    valid_hash(expected, relative)
    require(
        kind in {"receipt", "baseline", "candidate"},
        "select only a signed receipt, baseline, or candidate report",
    )
    if kind == "receipt":
        require(
            original_hash is None
            and original_bytes is None
            and archive_bytes is None,
            "a signed canonical receipt cannot hide a gzip report",
        )
        return decode_document(
            read_frozen(relative, expected, MAX_RECEIPT_BYTES),
            relative,
        )
    require(
        type(original_hash) is str
        and type(original_bytes) is int
        and type(archive_bytes) is int,
        "every compressed and original byte count must be signed",
    )
    return read_archive(
        relative,
        expected,
        BASELINE_FIELDS if kind == "baseline" else CANDIDATE_FIELDS,
        original_hash,
        original_bytes,
        archive_bytes,
    )


def frozen_baseline_fields(label: str) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "label": validate_label(label),
        **historical_lineage_fields(),
        "recorder_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": RECORDER_SHA256,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "cohorts": list(COHORTS),
        "apis": list(APIS),
        "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
        "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
        **frozen_bounds(),
    }


def validate_preserved_failure(value: Any) -> dict[str, Any]:
    expected = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-v1-"
            "controller-failure-preserved-v1"
        ),
        "status": "FAIL",
        "python": "3.14.6",
        "label": HISTORICAL_V1_BASELINE_LABEL,
        "recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "recorder_source_sha256": PREVIOUS_RECORDER_SHA256,
        "oracle_relative": HISTORICAL_V1_ORACLE_RELATIVE,
        "oracle_source_sha256": HISTORICAL_V1_ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "actual_reference_worker_count": "UNKNOWN",
        "reported_reference_worker_count_is_reliable": False,
        "baseline_result_status": "NOT MEASURED",
        "reference_outcomes_status": "NOT MEASURED",
        "report_publication_status": "NOT PUBLISHED",
        "receipt_publication_status": "NOT PUBLISHED",
        "actual_baseline_controller_invocations": 1,
        "actual_candidate_workers": 0,
        "controller_exit_code": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }
    require(
        type(value) is dict
        and set(value) == set(expected)
        | {"failure_explanation", "complete_controller_failure_stdout"},
        "the exact original unreliable V1 failure must remain complete",
    )
    fixed_fields(value, expected, "the preserved original V1 failure")
    explanation = value["failure_explanation"]
    require(
        type(explanation) is str
        and "268435456" in explanation
        and "not reliable" in explanation,
        "the unreliable earlier reference counter was misrepresented",
    )
    envelope = value["complete_controller_failure_stdout"]
    fixed_fields(
        envelope,
        {
            "schema": (
                "rebar-independent-substitution-buffer-semantics-"
                "recorder-v1-failure"
            ),
            "status": "FAIL",
            "actual_reference_workers": 0,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
        },
        "the preserved unreliable V1 outer failure envelope",
    )
    require(
        envelope.get("error_type") == "RecorderError"
        and envelope.get("error")
        == "a complete substitution report exceeds its bound",
        "the exact original 256 MiB failure was rewritten",
    )
    return {
        "relative": PRESERVED_PREVIOUS_FAILURE_RELATIVE,
        "sha256": PRESERVED_PREVIOUS_FAILURE_SHA256,
        "status": "FAIL",
        "reference_worker_count": "UNKNOWN",
        "reported_reference_worker_count_is_reliable": False,
        "baseline_result_status": "NOT MEASURED",
        "reference_outcomes_status": "NOT MEASURED",
        "report_publication_status": "NOT PUBLISHED",
        "receipt_publication_status": "NOT PUBLISHED",
        "failure_explanation": explanation,
    }


class ActualValidators:
    """Use authenticated, pure V2 validators without starting any worker."""

    def __init__(self) -> None:
        for relative, source in (
            (ORACLE_RELATIVE, ORACLE_SHA256),
            (RECORDER_RELATIVE, RECORDER_SHA256),
            (PREVIOUS_RECORDER_RELATIVE, PREVIOUS_RECORDER_SHA256),
            (AUDIT_RELATIVE, AUDIT_SHA256),
            (POLICY_V2_RELATIVE, POLICY_V2_SHA256),
            (V5_RELATIVE, V5_SHA256),
        ):
            read_frozen(relative, source, MAX_SOURCE_BYTES)
        self.preserved = validate_preserved_failure(
            decode_document(
                read_frozen(
                    PRESERVED_PREVIOUS_FAILURE_RELATIVE,
                    PRESERVED_PREVIOUS_FAILURE_SHA256,
                    MAX_SOURCE_BYTES,
                ),
                "the original preserved V1 controller failure",
            ),
        )
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        try:
            self.oracle = importlib.import_module(
                "tools.independent_substitution_buffer_semantics_v2",
            )
            self.recorder = importlib.import_module(
                "tools.record_independent_substitution_buffer_semantics_v3",
            )
            self.audit = importlib.import_module(
                "tools.independent_from_scratch_audit_v3",
            )
            self.v5 = importlib.import_module(
                "tools.independent_original_cpython_suite_v5",
            )
        except Exception as error:
            raise OverviewError(
                "an exact frozen pure substitution validator could not load",
            ) from error
        for module, relative, source in (
            (self.oracle, ORACLE_RELATIVE, ORACLE_SHA256),
            (self.recorder, RECORDER_RELATIVE, RECORDER_SHA256),
            (self.audit, AUDIT_RELATIVE, AUDIT_SHA256),
            (self.v5, V5_RELATIVE, V5_SHA256),
        ):
            require(
                os.path.abspath(getattr(module, "__file__", ""))
                == ROOT + "/" + relative
                and os.path.realpath(getattr(module, "__file__", ""))
                == ROOT + "/" + relative,
                "an authenticated frozen pure validator was substituted",
            )
            read_frozen(relative, source, MAX_SOURCE_BYTES)
        verify_runtime()
        self.baseline_pins = self.recorder.make_baseline_pins(
            BASELINE_LABEL,
            BASELINE_RECEIPT_SHA256,
            BASELINE_ARCHIVE_SHA256,
            BASELINE_RECORDS_SHA256,
        )
        self.matrix = self.oracle.build_matrix(PUBLISHED_SEED)
        self.oracle.validate_matrix(self.matrix)
        self.recorder.validate_matrix(self.matrix, MATRIX_SHA256)
        require(
            self.recorder.baseline_source_fields(
                RECORDER_SHA256,
                BASELINE_LABEL,
            )
            == frozen_baseline_fields(BASELINE_LABEL)
            and self.recorder.validate_compact_bounds()
            == frozen_bounds(),
            "the authenticated V2 matrix, seed, or exact bounds changed",
        )

    def owner_pins(
        self,
        family: str,
        adapter: str,
        engine: str,
        bridge: str,
        sources: Mapping[str, str],
    ) -> Any:
        require(type(sources) is dict, "pin every actual native source")
        try:
            pins = self.recorder.make_owner_pins(
                family,
                RECORDER_SHA256,
                adapter,
                engine,
                bridge,
                [
                    relative + "=" + source
                    for relative, source in sorted(sources.items())
                ],
                self.baseline_pins,
            )
            manifest = self.recorder.make_audit_manifest(
                pins,
                self.audit,
            )
            self.audit.validate_manifest(manifest, family)
            spec = self.v5.family_spec(family)
            require(
                self.v5.validate_pins(
                    {
                        "source": adapter,
                        "native_engine": engine,
                        "native_bridge": bridge,
                    },
                    spec,
                )
                == {
                    "source": adapter,
                    "native_engine": engine,
                    "native_bridge": bridge,
                },
                "the independently frozen V5 family policy changed",
            )
        except OverviewError:
            raise
        except Exception as error:
            raise OverviewError(
                "the frozen V2, V3, or V5 owner policy rejected " + family,
            ) from error
        return pins

    def authenticate_family(
        self,
        family: str,
        selected: Mapping[str, Any],
    ) -> Any:
        adapter_path, engine_path, bridge_path, expected_paths = (
            FAMILY_SPECS[family]
        )
        sources = selected["owned_source_sha256"]
        require(
            type(sources) is dict
            and set(sources) == set(expected_paths),
            "pin every from-scratch " + family + " source and lockfile",
        )
        for relative in expected_paths:
            source = valid_hash(sources[relative], relative)
            read_frozen(relative, source, MAX_SOURCE_BYTES)
        adapter = valid_hash(
            selected["candidate_source_sha256"],
            family + " owned adapter",
        )
        engine = valid_hash(
            selected["native_engine_sha256"],
            family + " owned matching engine",
        )
        bridge = valid_hash(
            selected["native_bridge_sha256"],
            family + " owned Python bridge",
        )
        require(
            sources.get(adapter_path) == adapter
            and (engine == bridge) is (family == "c"),
            "only the owned combined C engine and bridge may alias",
        )
        read_frozen(engine_path, engine, MAX_BINARY_BYTES)
        if bridge_path != engine_path:
            read_frozen(bridge_path, bridge, MAX_BINARY_BYTES)
        return self.owner_pins(family, adapter, engine, bridge, sources)

    def validate_baseline(
        self,
        receipt: Any,
        report: Any,
        pins: Any,
    ) -> dict[str, Any]:
        require(
            type(receipt) is dict
            and set(receipt) == BASELINE_RECEIPT_FIELDS
            and type(report) is dict
            and set(report) == BASELINE_FIELDS,
            "retain every genuine reference receipt and complete report field",
        )
        try:
            validated_receipt = self.recorder.validate_baseline_receipt(
                receipt,
                pins,
            )
            baseline = self.recorder.validate_archived_baseline(
                report,
                pins,
                self.oracle,
                self.matrix,
                validated_receipt,
            )
        except Exception as error:
            raise OverviewError(
                "the complete signed two-reference baseline was invalid",
            ) from error
        require(
            receipt["baseline_reference_pids"] == [82, 83]
            and receipt["report_bytes"] == BASELINE_ARCHIVE_BYTES
            and receipt["report_uncompressed_bytes"]
            == BASELINE_REPORT_BYTES
            and receipt["report_uncompressed_sha256"]
            == BASELINE_REPORT_SHA256
            and baseline["reference_a_records"]
            == baseline["reference_b_records"],
            "both actually observed Python workers must agree on all 5,120",
        )
        return baseline

    def validate_candidate(
        self,
        family: str,
        selected: Mapping[str, Any],
        receipt: Any,
        report: Any,
        baseline: Mapping[str, Any],
        *,
        historical: bool = False,
    ) -> dict[str, Any]:
        require(
            type(receipt) is dict
            and set(receipt) == CANDIDATE_RECEIPT_FIELDS
            and type(report) is dict
            and set(report) == CANDIDATE_FIELDS,
            "retain the full candidate receipt, worker, and 5,120 outcomes",
        )
        owner = receipt.get("candidate_owner_before")
        require(
            type(owner) is dict
            and owner == receipt.get("candidate_owner_after")
            and receipt.get("candidate_owner_unchanged") is True
            and type(owner.get("manifest")) is dict,
            "a complete frozen native source or owner was changed",
        )
        ownership = owner["manifest"]
        adapter = valid_hash(
            receipt.get("candidate_source_sha256"),
            family + " complete adapter",
        )
        engine = valid_hash(
            receipt.get("native_engine_sha256"),
            family + " complete engine",
        )
        bridge = valid_hash(
            receipt.get("native_bridge_sha256"),
            family + " complete bridge",
        )
        require(
            ownership.get("family") == family
            and ownership.get("candidate_source_sha256") == adapter
            and ownership.get("native_engine_sha256") == engine
            and ownership.get("native_bridge_sha256") == bridge
            and receipt.get("candidate_family") == family,
            "a receipt was taken from another native engine family",
        )
        if not historical:
            fixed_fields(
                selected,
                {
                    "family": family,
                    "candidate_source_sha256": adapter,
                    "native_engine_sha256": engine,
                    "native_bridge_sha256": bridge,
                    "owned_source_sha256": ownership["source_sha256"],
                },
                "the complete current " + family + " native ownership",
            )
        pins = self.owner_pins(
            family,
            adapter,
            engine,
            bridge,
            ownership["source_sha256"],
        )
        expected_receipt = {
            "schema": (
                "rebar-independent-substitution-buffer-semantics-"
                "recorder-v3-durable-candidate-publication-receipt"
            ),
            "status": "PASS",
            "python": "3.14.6",
            **historical_lineage_fields(),
            "candidate_family": family,
            "candidate_source_sha256": adapter,
            "native_engine_sha256": engine,
            "native_bridge_sha256": bridge,
            "baseline_label": BASELINE_LABEL,
            "recorder_source_sha256": RECORDER_SHA256,
            "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
            "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
            "preserved_previous_failure_relative": (
                PRESERVED_PREVIOUS_FAILURE_RELATIVE
            ),
            "preserved_previous_failure_sha256": (
                PRESERVED_PREVIOUS_FAILURE_SHA256
            ),
            "oracle_source_sha256": ORACLE_SHA256,
            "original_v5_sha256": V5_SHA256,
            "ownership_audit_sha256": AUDIT_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
            "published_seed_decimal": str(PUBLISHED_SEED),
            "case_count": CASE_COUNT,
            "cohort_count": len(COHORTS),
            "variants_per_cohort": VARIANTS_PER_COHORT,
            "cohorts": list(COHORTS),
            "apis": list(APIS),
            "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
            "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
            **frozen_bounds(),
            "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
            "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
            "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
            "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
            "baseline_records_sha256": BASELINE_RECORDS_SHA256,
            "baseline_reference_pids": [82, 83],
            "validated_baseline_record_count": CASE_COUNT,
            "validated_candidate_record_count": CASE_COUNT,
            "all_mismatches_preserved": True,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
            "validated_prior_reference_workers": 2,
            "actual_reference_workers": 0,
            "actual_candidate_workers": 1,
            "actual_candidate_process_invocations": 1,
            "candidate_owner_before": owner,
            "candidate_owner_after": owner,
            "candidate_owner_unchanged": True,
            "report_compression": "gzip-mtime-zero-level-9",
            "report_file_fsync_completed": True,
            "report_directory_fsync_completed": True,
            "report_atomic_no_overwrite_link": True,
            "report_complete_readback_verified": True,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        fixed_fields(
            receipt,
            expected_receipt,
            "the fully signed " + family + " candidate receipt",
        )
        require(
            type(receipt["actual_candidate_imports"]) is int
            and receipt["actual_candidate_imports"] >= 2
            and type(receipt["label"]) is str
            and validate_label(receipt["label"]) == receipt["label"]
            and receipt["report_relative"]
            == selected["_report_relative"]
            and receipt["report_sha256"] == selected["_report_sha256"]
            and receipt["receipt_relative"]
            == selected["_receipt_relative"],
            "the complete candidate report, worker, or receipt was swapped",
        )
        fixed_fields(
            report,
            {
                "schema": (
                    "rebar-independent-substitution-buffer-semantics-"
                    "recorder-v3-complete-candidate-report"
                ),
                "python": "3.14.6",
                **historical_lineage_fields(),
                "label": receipt["label"],
                "candidate_family": family,
                "candidate_source_sha256": adapter,
                "native_engine_sha256": engine,
                "native_bridge_sha256": bridge,
                "baseline_label": BASELINE_LABEL,
                "recorder_relative": RECORDER_RELATIVE,
                "recorder_source_sha256": RECORDER_SHA256,
                "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
                "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
                "preserved_previous_failure_relative": (
                    PRESERVED_PREVIOUS_FAILURE_RELATIVE
                ),
                "preserved_previous_failure_sha256": (
                    PRESERVED_PREVIOUS_FAILURE_SHA256
                ),
                "oracle_relative": ORACLE_RELATIVE,
                "oracle_source_sha256": ORACLE_SHA256,
                "original_v5_relative": V5_RELATIVE,
                "original_v5_sha256": V5_SHA256,
                "ownership_audit_relative": AUDIT_RELATIVE,
                "ownership_audit_sha256": AUDIT_SHA256,
                "matrix_sha256": MATRIX_SHA256,
                "published_seed": PUBLISHED_SEED,
                "published_seed_decimal": str(PUBLISHED_SEED),
                "case_count": CASE_COUNT,
                "cohort_count": len(COHORTS),
                "variants_per_cohort": VARIANTS_PER_COHORT,
                "cohorts": list(COHORTS),
                "apis": list(APIS),
                "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
                "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
                **frozen_bounds(),
                "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
                "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
                "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
                "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
                "baseline_records_sha256": BASELINE_RECORDS_SHA256,
                "baseline_reference_pids": [82, 83],
                "candidate_owner_before": owner,
                "candidate_owner_after": owner,
                "candidate_owner_unchanged": True,
                "complete_process_representation": (
                    "single-canonical-candidate-stream"
                ),
                "candidate_records_reconstruction": (
                    "decode-and-validate-complete-candidate-process-stdout"
                ),
                "baseline_records_reconstruction": (
                    "decode-and-validate-pinned-complete-baseline-archive"
                ),
                "mismatch_outcome_reconstruction": (
                    "frozen-matrix-plus-pinned-baseline-plus-candidate-stdout"
                ),
                "validated_baseline_record_count": CASE_COUNT,
                "validated_candidate_record_count": CASE_COUNT,
                "all_mismatches_preserved": True,
                "actual_method_guard_checks": 2 * CASE_COUNT,
                "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
                "validated_prior_reference_workers": 2,
                "actual_reference_workers": 0,
                "actual_candidate_workers": 1,
                "actual_candidate_imports": (
                    receipt["actual_candidate_imports"]
                ),
                "actual_candidate_process_invocations": 1,
                "actual_candidate_process_returncode": 0,
                "actual_candidate_process_signal": None,
                "actual_candidate_process_timed_out": False,
                "actual_candidate_process_spawn_error": None,
                "clock_samples": 0,
                "timing_trials_run": 0,
                "benchmark_files_read": 0,
                "hidden_cases_read": 0,
                "performance": "NOT MEASURED",
                "candidate_qualified_for_hidden_benchmark": False,
                "final_winner_selected": False,
            },
            "the complete signed " + family + " candidate report",
        )
        try:
            self.recorder.validate_compact_report_document(report)
            stdout = self.recorder.decode_stream(
                report["complete_candidate_process_stdout"],
                family + " complete signed isolated worker stdout",
            )
            require(
                self.recorder.decode_stream(
                    report["complete_candidate_process_stderr"],
                    family + " complete signed isolated worker stderr",
                )
                == b"",
                "the signed native candidate concealed complete stderr",
            )
            worker = self.recorder.decode_document(
                stdout,
                family + " complete signed isolated worker",
            )
            validated = self.recorder.validate_candidate_worker(
                worker,
                pins,
                self.matrix,
                expected_pid=report["actual_candidate_pid"],
                oracle=self.oracle,
                audit=self.audit,
            )
            mismatches, by_cohort, by_api = (
                self.recorder.validate_mismatch_evidence(
                    report["all_mismatches"],
                    self.matrix,
                    baseline["reference_a_records"],
                    validated["records"],
                    report["mismatch_evidence_sha256"],
                )
            )
        except OverviewError:
            raise
        except Exception as error:
            raise OverviewError(
                "a complete " + family + " worker or mismatch was forged",
            ) from error
        count = len(mismatches)
        expected_status = "FAIL" if count else "PASS"
        fixed_fields(
            receipt,
            {
                "candidate_result_status": expected_status,
                "candidate_records_sha256": (
                    validated["records_sha256"]
                ),
                "mismatch_count": count,
                "mismatch_evidence_sha256": (
                    report["mismatch_evidence_sha256"]
                ),
                "mismatches_by_cohort": by_cohort,
                "mismatches_by_api": by_api,
            },
            "the signed complete " + family + " mismatch ledger",
        )
        fixed_fields(
            report,
            {
                "status": expected_status,
                "candidate_records_sha256": (
                    validated["records_sha256"]
                ),
                "mismatch_count": count,
                "mismatches_by_cohort": by_cohort,
                "mismatches_by_api": by_api,
                "failure_count": 1 if count else 0,
                "all_failure_reasons": (
                    [
                        "the independent candidate differs on "
                        + str(count)
                        + " frozen substitution and buffer cases"
                    ]
                    if count
                    else []
                ),
            },
            "the reconstructed complete " + family + " outcomes",
        )
        require(
            sum(by_cohort.values()) == sum(by_api.values()) == count
            and len(report["all_mismatches"]) == count
            and receipt["status"] == "PASS"
            and receipt["candidate_result_status"] == expected_status,
            "publication success was confused with actual compatibility",
        )
        return {
            "state": "RUN",
            "candidate_result_status": expected_status,
            "publication_status": "PASS",
            "candidate_records_sha256": validated["records_sha256"],
            "mismatch_evidence_sha256": (
                report["mismatch_evidence_sha256"]
            ),
            "passed": CASE_COUNT - count,
            "failed": count,
            "not_measured": 0,
            "mismatches_by_cohort": by_cohort,
            "mismatches_by_api": by_api,
            "all_mismatches_preserved": True,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
            "actual_candidate_workers": 1,
            "actual_reference_workers": 0,
            "validated_prior_reference_workers": 2,
        }


MANIFEST_FIELDS = frozenset({
    "schema",
    "python",
    "case_denominator",
    "cohort_count",
    "variants_per_cohort",
    "oracle_source_sha256",
    "recorder_source_sha256",
    "previous_recorder_source_sha256",
    "preserved_previous_failure",
    "historical_v1",
    "ownership_audit_sha256",
    "original_v5_sha256",
    "pinned_python_sha256",
    "matrix_sha256",
    "published_seed",
    "baseline",
    "families",
})
FAMILY_MANIFEST_FIELDS = frozenset({
    "family",
    "candidate_source_sha256",
    "native_engine_sha256",
    "native_bridge_sha256",
    "owned_source_sha256",
    "state",
    "report",
    "receipt",
    "superseded",
})


def manifest_rows(
    manifest: Any,
    loader: Loader,
    validators: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(
        type(manifest) is dict and set(manifest) == MANIFEST_FIELDS,
        "the exact independently frozen 5,120-case inputs are mandatory",
    )
    fixed_fields(
        manifest,
        {
            "schema": SCHEMA + "-inputs",
            "python": "3.14.6",
            "case_denominator": CASE_COUNT,
            "cohort_count": len(COHORTS),
            "variants_per_cohort": VARIANTS_PER_COHORT,
            "oracle_source_sha256": ORACLE_SHA256,
            "recorder_source_sha256": RECORDER_SHA256,
            "previous_recorder_source_sha256": PREVIOUS_RECORDER_SHA256,
            "ownership_audit_sha256": AUDIT_SHA256,
            "original_v5_sha256": V5_SHA256,
            "pinned_python_sha256": PINNED_PYTHON_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
        },
        "the actual frozen replacement-and-buffer matrix",
    )
    require(
        type(manifest.get("historical_v1")) is dict
        and manifest["historical_v1"] == historical_v1_manifest(),
        "falsified V1 evidence was omitted or counted as a corrected result",
    )
    preserved = manifest["preserved_previous_failure"]
    require(
        type(preserved) is dict
        and preserved
        == report_pin(
            PRESERVED_PREVIOUS_FAILURE_RELATIVE,
            PRESERVED_PREVIOUS_FAILURE_SHA256,
        ),
        "preserve the exact original V1 failure and unreliable worker count",
    )
    require(
        type(validators.preserved) is dict
        and validators.preserved["relative"]
        == PRESERVED_PREVIOUS_FAILURE_RELATIVE
        and validators.preserved["sha256"]
        == PRESERVED_PREVIOUS_FAILURE_SHA256
        and validators.preserved["reference_worker_count"] == "UNKNOWN"
        and validators.preserved["reported_reference_worker_count_is_reliable"]
        is False,
        "the original failed experiment was concealed or rewritten",
    )
    seen: set[str] = {PRESERVED_PREVIOUS_FAILURE_RELATIVE}
    declared_baseline = manifest["baseline"]
    require(
        type(declared_baseline) is dict
        and set(declared_baseline)
        == {"label", "archive", "receipt", "records_sha256"}
        and declared_baseline["label"] == BASELINE_LABEL
        and declared_baseline["records_sha256"] == BASELINE_RECORDS_SHA256,
        "the complete previously signed two-reference baseline is mandatory",
    )
    baseline_archive_path, baseline_archive_hash = evidence_pin(
        declared_baseline["archive"],
        seen,
    )
    baseline_receipt_path, baseline_receipt_hash = evidence_pin(
        declared_baseline["receipt"],
        seen,
    )
    require(
        (
            baseline_archive_path,
            baseline_archive_hash,
            baseline_receipt_path,
            baseline_receipt_hash,
        )
        == (
            BASELINE_ARCHIVE_RELATIVE,
            BASELINE_ARCHIVE_SHA256,
            BASELINE_RECEIPT_RELATIVE,
            BASELINE_RECEIPT_SHA256,
        ),
        "the actual signed reference archive or receipt was replaced",
    )
    baseline_receipt = loader(
        baseline_receipt_path,
        baseline_receipt_hash,
        "receipt",
        None,
        None,
        None,
    )
    require(
        type(baseline_receipt) is dict
        and type(baseline_receipt.get("report_uncompressed_sha256")) is str
        and type(baseline_receipt.get("report_uncompressed_bytes")) is int
        and type(baseline_receipt.get("report_bytes")) is int,
        "a complete signed reference gzip and original bounds are mandatory",
    )
    families = manifest["families"]
    require(
        type(families) is list
        and len(families) == len(FAMILY_ORDER)
        and [
            selected.get("family")
            if type(selected) is dict
            else None
            for selected in families
        ]
        == list(FAMILY_ORDER),
        "show Rust, C, and Zig once, in exactly that independent order",
    )
    baseline_pins: Any = None
    family_pins: dict[str, Any] = {}
    for family, selected in zip(FAMILY_ORDER, families, strict=True):
        require(
            type(selected) is dict
            and set(selected) == FAMILY_MANIFEST_FIELDS
            and selected["family"] == family
            and selected["state"] in {"RUN", "NOT MEASURED"}
            and type(selected["superseded"]) is list,
            "a native family, complete source, result, or history was hidden",
        )
        family_pins[family] = validators.authenticate_family(
            family,
            selected,
        )
        if baseline_pins is None:
            baseline_pins = family_pins[family]
    require(baseline_pins is not None, "a pinned native family is mandatory")
    baseline_report = loader(
        baseline_archive_path,
        baseline_archive_hash,
        "baseline",
        baseline_receipt["report_uncompressed_sha256"],
        baseline_receipt["report_uncompressed_bytes"],
        baseline_receipt["report_bytes"],
    )
    original = validators.validate_baseline(
        baseline_receipt,
        baseline_report,
        baseline_pins,
    )
    baseline = {
        "label": BASELINE_LABEL,
        "archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "archive_sha256": BASELINE_ARCHIVE_SHA256,
        "archive_bytes": BASELINE_ARCHIVE_BYTES,
        "receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "receipt_sha256": BASELINE_RECEIPT_SHA256,
        "report_uncompressed_sha256": BASELINE_REPORT_SHA256,
        "report_uncompressed_bytes": BASELINE_REPORT_BYTES,
        "records_sha256": BASELINE_RECORDS_SHA256,
        "reference_pids": [82, 83],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
    }
    zero_cohorts = {cohort: 0 for cohort in COHORTS}
    zero_apis = {api: 0 for api in APIS}
    rows: list[dict[str, Any]] = [{
        "family": "python",
        "label": FAMILY_LABELS["python"],
        "state": "RUN",
        "candidate_result_status": "PASS",
        "publication_status": "PASS",
        "case_denominator": CASE_COUNT,
        "passed": CASE_COUNT,
        "failed": 0,
        "not_measured": 0,
        "mismatches_by_cohort": zero_cohorts,
        "mismatches_by_api": zero_apis,
        "all_mismatches_preserved": True,
        "superseded": [],
    }]
    for family, selected in zip(FAMILY_ORDER, families, strict=True):
        adapter = valid_hash(
            selected["candidate_source_sha256"],
            family + " complete owned adapter",
        )
        history: list[dict[str, Any]] = []
        for previous in selected["superseded"]:
            require(
                type(previous) is dict
                and set(previous) == {"report", "receipt"},
                "a complete superseded candidate result was hidden",
            )
            report_path, report_hash = evidence_pin(
                previous["report"],
                seen,
            )
            receipt_path, receipt_hash = evidence_pin(
                previous["receipt"],
                seen,
            )
            prior_receipt = loader(
                receipt_path,
                receipt_hash,
                "receipt",
                None,
                None,
                None,
            )
            require(
                type(prior_receipt) is dict
                and prior_receipt.get("candidate_family") == family
                and type(prior_receipt.get("report_uncompressed_sha256"))
                is str
                and type(prior_receipt.get("report_uncompressed_bytes"))
                is int
                and type(prior_receipt.get("report_bytes")) is int,
                "a complete historical result was replaced or concealed",
            )
            prior_report = loader(
                report_path,
                report_hash,
                "candidate",
                prior_receipt["report_uncompressed_sha256"],
                prior_receipt["report_uncompressed_bytes"],
                prior_receipt["report_bytes"],
            )
            historical_selection = {
                "_report_relative": report_path,
                "_report_sha256": report_hash,
                "_receipt_relative": receipt_path,
            }
            historical = validators.validate_candidate(
                family,
                historical_selection,
                prior_receipt,
                prior_report,
                original,
                historical=True,
            )
            history.append({
                "report": report_pin(report_path, report_hash),
                "receipt": report_pin(receipt_path, receipt_hash),
                "candidate_source_sha256": (
                    prior_receipt["candidate_source_sha256"]
                ),
                **historical,
            })
        row: dict[str, Any] = {
            "family": family,
            "label": FAMILY_LABELS[family],
            "candidate_source_sha256": adapter,
            "native_engine_sha256": selected["native_engine_sha256"],
            "native_bridge_sha256": selected["native_bridge_sha256"],
            "owned_source_sha256": dict(
                selected["owned_source_sha256"],
            ),
            "state": selected["state"],
            "case_denominator": CASE_COUNT,
            "superseded": history,
        }
        if selected["state"] == "NOT MEASURED":
            require(
                selected["report"] is None
                and selected["receipt"] is None,
                "an unmeasured family cannot claim a current signed run",
            )
            row.update({
                "candidate_result_status": "NOT MEASURED",
                "publication_status": "NOT MEASURED",
                "candidate_records_sha256": None,
                "mismatch_evidence_sha256": None,
                "passed": 0,
                "failed": 0,
                "not_measured": CASE_COUNT,
                "mismatches_by_cohort": None,
                "mismatches_by_api": None,
                "all_mismatches_preserved": None,
                "actual_method_guard_checks": 0,
                "actual_warning_registry_guard_checks": 0,
                "actual_candidate_workers": 0,
                "actual_reference_workers": 0,
                "validated_prior_reference_workers": 0,
                "report": None,
                "receipt": None,
            })
        else:
            report_path, report_hash = evidence_pin(
                selected["report"],
                seen,
            )
            receipt_path, receipt_hash = evidence_pin(
                selected["receipt"],
                seen,
            )
            receipt = loader(
                receipt_path,
                receipt_hash,
                "receipt",
                None,
                None,
                None,
            )
            require(
                type(receipt) is dict
                and type(receipt.get("report_uncompressed_sha256")) is str
                and type(receipt.get("report_uncompressed_bytes")) is int
                and type(receipt.get("report_bytes")) is int,
                "every recorded family requires its full signed gzip bounds",
            )
            report = loader(
                report_path,
                report_hash,
                "candidate",
                receipt["report_uncompressed_sha256"],
                receipt["report_uncompressed_bytes"],
                receipt["report_bytes"],
            )
            actual_selection = {
                **selected,
                "_report_relative": report_path,
                "_report_sha256": report_hash,
                "_receipt_relative": receipt_path,
            }
            row.update(
                validators.validate_candidate(
                    family,
                    actual_selection,
                    receipt,
                    report,
                    original,
                ),
            )
            row["report"] = report_pin(report_path, report_hash)
            row["receipt"] = report_pin(receipt_path, receipt_hash)
        require(
            all(
                type(row[field]) is int and row[field] >= 0
                for field in ("passed", "failed", "not_measured")
            )
            and row["passed"] + row["failed"] + row["not_measured"]
            == CASE_COUNT
            and (
                row["candidate_result_status"]
                == (
                    "NOT MEASURED"
                    if row["not_measured"]
                    else "FAIL" if row["failed"] else "PASS"
                )
            ),
            "an independent family silently changed its real denominator",
        )
        rows.append(row)
    return baseline, rows

def escape_xml(value: str) -> str:
    require(type(value) is str, "all chart labels must be safe text")
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def make_svg(
    rows: list[dict[str, Any]],
    source: str,
    manifest: str,
) -> bytes:
    require(
        type(rows) is list
        and len(rows) == 4
        and [row.get("family") for row in rows]
        == ["python", *FAMILY_ORDER],
        "show Python, Rust, C, and Zig exactly once",
    )
    source = valid_hash(source, "the complete frozen chart renderer")
    manifest = valid_hash(manifest, "the complete frozen input manifest")
    colors = (
        ("passed", "#15803d", "Matches Python"),
        ("failed", "#dc2626", "Does not match Python"),
        ("not_measured", "#94a3b8", "Not yet measured"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" '
        'height="594" viewBox="0 0 1120 594" role="img" '
        'aria-labelledby="substitution-buffer-title '
        'substitution-buffer-description">',
        '<title id="substitution-buffer-title">'
        'Does each replacement work exactly like Python?</title>',
        '<desc id="substitution-buffer-description">'
        'Python, Rust, C, and Zig are compared against the same 5,120 '
        'independently frozen Python replacement-and-buffer tests. '
        'Green means the result matches Python, red means it does not, '
        'and gray means the implementation has not yet been tested. '
        'This is a correctness comparison, not a speed measurement.</desc>',
        '<rect width="1120" height="594" rx="18" fill="#f8fafc"/>',
        '<text x="43" y="53" fill="#0f172a" '
        'font-family="system-ui,sans-serif" font-size="26" '
        'font-weight="700">Does each replacement work exactly '
        'like Python?</text>',
        '<text x="43" y="82" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="15">'
        'The same 5,120 Python tests for every implementation '
        '&#183; speed not yet measured</text>',
    ]
    for index, (_, color, label) in enumerate(colors):
        x = 43 + index * 266
        parts.append(
            f'<rect x="{x}" y="105" width="14" height="14" rx="3" '
            f'fill="{color}"/><text x="{x + 22}" y="117" '
            'fill="#334155" font-family="system-ui,sans-serif" '
            f'font-size="13">{escape_xml(label)}</text>',
        )
    for index, row in enumerate(rows):
        require(
            all(
                type(row.get(field)) is int and row[field] >= 0
                for field in ("passed", "failed", "not_measured")
            )
            and row.get("case_denominator") == CASE_COUNT
            and row["passed"] + row["failed"] + row["not_measured"]
            == CASE_COUNT,
            "a visible chart row changed its 5,120-test denominator",
        )
        top = 151 + index * 82
        label = escape_xml(row["label"])
        if row["not_measured"]:
            caption = "NOT MEASURED"
            caption_color = "#64748b"
        elif row["failed"]:
            caption = (
                f'{row["passed"]:,} match'
                f' \u00b7 {row["failed"]:,} fail'
            )
            caption_color = "#dc2626"
        else:
            caption = f'{row["passed"]:,} / {CASE_COUNT:,} match Python'
            caption_color = "#15803d"
        parts.extend((
            f'<text x="43" y="{top + 18}" fill="#0f172a" '
            'font-family="system-ui,sans-serif" font-size="17" '
            f'font-weight="700">{label}</text>',
            f'<text x="1040" y="{top + 18}" '
            f'fill="{caption_color}" text-anchor="end" '
            'font-family="system-ui,sans-serif" font-size="14" '
            f'font-weight="600">{escape_xml(caption)}</text>',
            f'<rect x="43" y="{top + 30}" width="997" height="26" '
            'rx="6" fill="#e2e8f0"/>',
        ))
        cumulative = 0
        for field, color, meaning in colors:
            beginning = 43 + cumulative * 997 // CASE_COUNT
            cumulative += row[field]
            ending = 43 + cumulative * 997 // CASE_COUNT
            if ending > beginning:
                parts.append(
                    f'<rect x="{beginning}" y="{top + 30}" '
                    f'width="{ending - beginning}" height="26" '
                    f'fill="{color}"><title>{label}: '
                    f'{row[field]:,} {escape_xml(meaning.lower())} '
                    f'out of {CASE_COUNT:,}</title></rect>',
                )
    parts.extend((
        '<text x="43" y="502" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="13">'
        'Includes text, bytes, callbacks, capture groups, invalid inputs, '
        'and nested Python buffer behavior.</text>',
        '<text x="43" y="523" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="13">'
        'Every failure and earlier result is preserved. '
        'Speed and the final holdout have not been measured.</text>',
        f'<text x="43" y="562" fill="#64748b" '
        'font-family="system-ui,sans-serif" font-size="10">'
        f'Manifest SHA-256: {manifest} '
        f'&#183; renderer SHA-256: {source}</text>',
        "</svg>\n",
    ))
    return "\n".join(parts).encode("utf-8")


SUMMARY_FIELDS = frozenset({
    "schema",
    "python",
    "source_relative",
    "source_sha256",
    "manifest_relative",
    "manifest_sha256",
    "svg_relative",
    "svg_sha256",
    "oracle_relative",
    "oracle_source_sha256",
    "recorder_relative",
    "recorder_source_sha256",
    "previous_recorder_relative",
    "previous_recorder_source_sha256",
    "preserved_previous_failure",
    "historical_v1",
    "ownership_audit_relative",
    "ownership_audit_sha256",
    "original_v5_relative",
    "original_v5_sha256",
    "pinned_python_sha256",
    "matrix_sha256",
    "published_seed",
    "published_seed_decimal",
    "case_denominator",
    "cohort_count",
    "variants_per_cohort",
    "baseline",
    "families",
    "overall",
    "actual_candidate_workers",
    "actual_candidate_imports",
    "hidden_cases_read",
    "benchmark_files_read",
    "clock_samples",
    "timing_trials_run",
    "performance",
    "final_holdout_opened",
    "winner_selected",
})


def validate_visible_rows(
    rows: Any,
) -> dict[str, int]:
    require(
        type(rows) is list
        and len(rows) == 4
        and [
            row.get("family") if type(row) is dict else None
            for row in rows
        ]
        == ["python", *FAMILY_ORDER],
        "the chart must show Python, Rust, C, and Zig exactly once",
    )
    passed = 0
    failed = 0
    observed = 0
    for index, row in enumerate(rows):
        require(
            type(row) is dict
            and row.get("case_denominator") == CASE_COUNT
            and all(
                type(row.get(field)) is int
                and row[field] >= 0
                for field in ("passed", "failed", "not_measured")
            )
            and row["passed"] + row["failed"] + row["not_measured"]
            == CASE_COUNT
            and row.get("state") in {"RUN", "NOT MEASURED"},
            "a summary row hid a real result or changed its denominator",
        )
        if index == 0:
            require(
                row["family"] == "python"
                and row["state"] == "RUN"
                and row["passed"] == CASE_COUNT
                and row["failed"] == 0
                and row["not_measured"] == 0,
                "the complete two-worker Python baseline was concealed",
            )
            continue
        if row["state"] == "NOT MEASURED":
            require(
                row["passed"] == row["failed"] == 0
                and row["not_measured"] == CASE_COUNT
                and row.get("candidate_result_status") == "NOT MEASURED"
                and row.get("publication_status") == "NOT MEASURED"
                and row.get("report") is None
                and row.get("receipt") is None
                and row.get("mismatches_by_api") is None
                and row.get("mismatches_by_cohort") is None,
                "an unmeasured native family was shown as tested",
            )
            continue
        observed += 1
        passed += row["passed"]
        failed += row["failed"]
        by_cohort = row.get("mismatches_by_cohort")
        by_api = row.get("mismatches_by_api")
        require(
            row["not_measured"] == 0
            and row.get("candidate_result_status")
            == ("FAIL" if row["failed"] else "PASS")
            and row.get("publication_status") == "PASS"
            and row.get("all_mismatches_preserved") is True
            and type(by_cohort) is dict
            and set(by_cohort) == set(COHORTS)
            and all(type(number) is int and number >= 0
                    for number in by_cohort.values())
            and sum(by_cohort.values()) == row["failed"]
            and type(by_api) is dict
            and set(by_api) == set(APIS)
            and all(type(number) is int and number >= 0
                    for number in by_api.values())
            and sum(by_api.values()) == row["failed"]
            and type(row.get("report")) is dict
            and type(row.get("receipt")) is dict,
            "a recorded result lost a failure, cohort, API, or signed proof",
        )
    return {
        "observed_candidate_families": observed,
        "candidate_case_denominator": observed * CASE_COUNT,
        "candidate_checks_matching_python": passed,
        "candidate_checks_failing_python": failed,
        "unmeasured_candidate_families": len(FAMILY_ORDER) - observed,
    }


def build_documents(
    manifest: Mapping[str, Any],
    source: str,
    manifest_hash: str,
    loader: Loader,
    validators: Any,
) -> tuple[bytes, bytes]:
    source = valid_hash(source, "the complete chart renderer")
    manifest_hash = valid_hash(manifest_hash, "the exact chart manifest")
    baseline, rows = manifest_rows(manifest, loader, validators)
    overall = validate_visible_rows(rows)
    svg = make_svg(rows, source, manifest_hash)
    summary = {
        "schema": SCHEMA + "-summary",
        "python": "3.14.6",
        "source_relative": SOURCE_RELATIVE,
        "source_sha256": source,
        "manifest_relative": MANIFEST_RELATIVE,
        "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": RECORDER_SHA256,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_source_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure": dict(validators.preserved),
        "historical_v1": historical_v1_manifest(),
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "baseline": baseline,
        "families": rows,
        "overall": overall,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    require(
        set(summary) == SUMMARY_FIELDS,
        "a complete chart summary field was omitted or injected",
    )
    return svg, canonical(summary)


def validate_previous_outputs(
    old_svg: Any,
    old_summary: Any,
    previous_svg: Any,
    previous_summary: Any,
    source: str,
) -> dict[str, Any]:
    require(
        type(old_svg) is bytes
        and 0 < len(old_svg) <= MAX_SOURCE_BYTES
        and type(old_summary) is bytes
        and 0 < len(old_summary) <= MAX_SOURCE_BYTES,
        "authenticate both complete previous graph files before replacing",
    )
    svg_hash = valid_hash(previous_svg, "the exact previous SVG")
    summary_hash = valid_hash(
        previous_summary,
        "the exact previous summary",
    )
    source = valid_hash(source, "the exact current chart source")
    require(
        hashlib.sha256(old_svg).hexdigest() == svg_hash
        and hashlib.sha256(old_summary).hexdigest() == summary_hash,
        "an explicitly pinned previous chart file was substituted",
    )
    document = decode_document(
        old_summary,
        "the complete previous substitution-buffer summary",
        MAX_SOURCE_BYTES,
    )
    require(
        set(document) == SUMMARY_FIELDS,
        "a previous summary hid a family, source, or historical loss",
    )
    fixed_fields(
        document,
        {
            "schema": SCHEMA + "-summary",
            "python": "3.14.6",
            "source_relative": SOURCE_RELATIVE,
            "source_sha256": source,
            "manifest_relative": MANIFEST_RELATIVE,
            "svg_relative": SVG_RELATIVE,
            "svg_sha256": svg_hash,
            "oracle_relative": ORACLE_RELATIVE,
            "oracle_source_sha256": ORACLE_SHA256,
            "recorder_relative": RECORDER_RELATIVE,
            "recorder_source_sha256": RECORDER_SHA256,
            "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
            "previous_recorder_source_sha256": PREVIOUS_RECORDER_SHA256,
            "ownership_audit_relative": AUDIT_RELATIVE,
            "ownership_audit_sha256": AUDIT_SHA256,
            "original_v5_relative": V5_RELATIVE,
            "original_v5_sha256": V5_SHA256,
            "pinned_python_sha256": PINNED_PYTHON_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
            "published_seed_decimal": str(PUBLISHED_SEED),
            "case_denominator": CASE_COUNT,
            "cohort_count": len(COHORTS),
            "variants_per_cohort": VARIANTS_PER_COHORT,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_opened": False,
            "winner_selected": False,
        },
        "the exact previously generated chart",
    )
    previous_history = document["preserved_previous_failure"]
    require(
        type(previous_history) is dict
        and previous_history.get("relative")
        == PRESERVED_PREVIOUS_FAILURE_RELATIVE
        and previous_history.get("sha256")
        == PRESERVED_PREVIOUS_FAILURE_SHA256
        and previous_history.get("reference_worker_count") == "UNKNOWN"
        and previous_history.get(
            "reported_reference_worker_count_is_reliable",
        )
        is False,
        "a replacement discarded the original unreliable V1 failure",
    )
    require(
        validate_visible_rows(document["families"]) == document["overall"]
        and make_svg(
            document["families"],
            source,
            valid_hash(
                document["manifest_sha256"],
                "the exact previous graph manifest",
            ),
        )
        == old_svg,
        "a prior summary, genuine failure, or SVG no longer agrees",
    )
    baseline = document["baseline"]
    fixed_fields(
        baseline,
        {
            "label": BASELINE_LABEL,
            "archive_relative": BASELINE_ARCHIVE_RELATIVE,
            "archive_sha256": BASELINE_ARCHIVE_SHA256,
            "archive_bytes": BASELINE_ARCHIVE_BYTES,
            "receipt_relative": BASELINE_RECEIPT_RELATIVE,
            "receipt_sha256": BASELINE_RECEIPT_SHA256,
            "report_uncompressed_sha256": BASELINE_REPORT_SHA256,
            "report_uncompressed_bytes": BASELINE_REPORT_BYTES,
            "records_sha256": BASELINE_RECORDS_SHA256,
            "reference_pids": [82, 83],
            "actual_reference_workers": 2,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
        },
        "the previous actual complete Python reference pair",
    )
    return document

def read_existing_output(
    directory: int,
    basename: str,
    operations: Any = os,
) -> tuple[bytes, os.stat_result] | None:
    require(
        basename in {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        },
        "only the two independently approved graph outputs may be read",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = operations.open(
            basename,
            flags,
            dir_fd=directory,
        )
    except FileNotFoundError:
        return None
    try:
        first = operations.fstat(descriptor)
        named = operations.stat(
            basename,
            dir_fd=directory,
            follow_symlinks=False,
        )
        require(
            stat.S_ISREG(first.st_mode)
            and (
                first.st_dev, first.st_ino, first.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            )
            and 0 < first.st_size <= MAX_SOURCE_BYTES,
            "an existing output is a symlink, nonregular, or oversized",
        )
        remaining = first.st_size
        blocks: list[bytes] = []
        while remaining:
            block = operations.read(
                descriptor,
                min(CHUNK_BYTES, remaining),
            )
            require(
                type(block) is bytes and bool(block),
                "a genuine previous chart output was truncated",
            )
            remaining -= len(block)
            blocks.append(block)
        require(
            operations.read(descriptor, 1) == b"",
            "a previous chart output gained hidden trailing bytes",
        )
        final = operations.fstat(descriptor)
        named = operations.stat(
            basename,
            dir_fd=directory,
            follow_symlinks=False,
        )
        require(
            (
                first.st_dev, first.st_ino, first.st_size,
            ) == (
                final.st_dev, final.st_ino, final.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            ),
            "a previous chart output changed while authenticated",
        )
        return b"".join(blocks), first
    finally:
        operations.close(descriptor)

def approve_publication(
    old_svg: bytes | None,
    old_summary: bytes | None,
    new_svg: bytes,
    new_summary: bytes,
    replace: bool,
    previous_svg: str | None,
    previous_summary: str | None,
    source: str,
) -> bool:
    require(
        type(new_svg) is bytes
        and 0 < len(new_svg) <= MAX_SOURCE_BYTES
        and type(new_summary) is bytes
        and 0 < len(new_summary) <= MAX_SOURCE_BYTES
        and type(replace) is bool,
        "bounded complete chart bytes and an explicit replacement "
        "choice are mandatory",
    )
    if not replace:
        require(
            previous_svg is None and previous_summary is None,
            "previous pins cannot silently authorize graph replacement",
        )
        require(
            (old_svg is None and old_summary is None)
            or (old_svg == new_svg and old_summary == new_summary),
            "refusing a partial pair or an unapproved chart overwrite",
        )
        return False
    validate_previous_outputs(
        old_svg,
        old_summary,
        previous_svg,
        previous_summary,
        source,
    )
    return old_svg != new_svg or old_summary != new_summary

def retained_directory(
    directory: int,
    identity: tuple[int, int],
    operations: Any,
) -> None:
    require(
        type(directory) is int
        and directory >= 0
        and type(identity) is tuple
        and len(identity) == 2
        and all(type(number) is int and number >= 0 for number in identity),
        "retain exactly one independently approved no-follow directory",
    )
    observed = operations.fstat(directory)
    require(
        stat.S_ISDIR(observed.st_mode)
        and (observed.st_dev, observed.st_ino) == identity,
        "the retained generated-chart directory was substituted",
    )

def owned_stage(
    directory: int,
    basename: str,
    raw: bytes,
    operations: Any,
) -> tuple[str, tuple[int, int, int]]:
    require(
        basename in {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        }
        and type(raw) is bytes
        and 0 < len(raw) <= MAX_SOURCE_BYTES,
        "stage only the two exact derived substitution-buffer outputs",
    )
    temporary = (
        ".rebar-substitution-buffer-overview-v2-stage-"
        + basename
        + "-"
        + str(os.getpid())
        + "-"
        + hashlib.sha256(raw).hexdigest()[:20]
    )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = operations.open(
        temporary,
        flags,
        0o644,
        dir_fd=directory,
    )
    first = operations.fstat(descriptor)
    try:
        require(
            stat.S_ISREG(first.st_mode),
            "the exact staged chart must be a private regular file",
        )
        offset = 0
        while offset < len(raw):
            written = operations.write(
                descriptor,
                raw[offset:],
            )
            require(
                type(written) is int and written > 0,
                "the complete staged chart was not fully written",
            )
            offset += written
        operations.fsync(descriptor)
        current = operations.fstat(descriptor)
        named = operations.stat(
            temporary,
            dir_fd=directory,
            follow_symlinks=False,
        )
        identity = (
            first.st_dev,
            first.st_ino,
            len(raw),
        )
        require(
            (
                current.st_dev,
                current.st_ino,
                current.st_size,
            ) == (
                named.st_dev,
                named.st_ino,
                named.st_size,
            ) == identity,
            "a fully flushed private graph stage was substituted",
        )
        return temporary, identity
    except BaseException:
        try:
            named = operations.stat(
                temporary,
                dir_fd=directory,
                follow_symlinks=False,
            )
            if (named.st_dev, named.st_ino) == (
                first.st_dev,
                first.st_ino,
            ):
                operations.unlink(
                    temporary,
                    dir_fd=directory,
                )
                operations.fsync(directory)
        except (OSError, OverviewError):
            pass
        raise
    finally:
        operations.close(descriptor)

def remove_owned_name(
    directory: int,
    basename: str,
    identity: tuple[int, int, int],
    operations: Any,
) -> None:
    try:
        named = operations.stat(
            basename,
            dir_fd=directory,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return
    require(
        stat.S_ISREG(named.st_mode)
        and (
            named.st_dev,
            named.st_ino,
            named.st_size,
        ) == identity,
        "refusing to remove an unowned graph transaction file",
    )
    operations.unlink(basename, dir_fd=directory)

def atomic_publish_pair(
    directory: int,
    identity: tuple[int, int],
    old_svg: bytes | None,
    old_summary: bytes | None,
    new_svg: bytes,
    new_summary: bytes,
    operations: Any = os,
) -> None:
    """Publish both fresh files or safely replace and restore both together."""
    retained_directory(directory, identity, operations)
    require(
        (old_svg is None) is (old_summary is None),
        "a partial generated chart pair cannot be published",
    )
    fresh = old_svg is None
    pairs = (
        (
            safe_parts(SVG_RELATIVE)[-1],
            old_svg,
            new_svg,
        ),
        (
            safe_parts(SUMMARY_RELATIVE)[-1],
            old_summary,
            new_summary,
        ),
    )
    stages: dict[str, tuple[str, tuple[int, int, int]]] = {}
    backups: dict[str, tuple[str, tuple[int, int, int]]] = {}
    committed: list[str] = []
    originals = {
        name: previous
        for name, previous, _ in pairs
    }
    updates = {
        name: updated
        for name, _, updated in pairs
    }
    try:
        for name, previous, updated in pairs:
            current = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                (
                    fresh and current is None
                )
                or (
                    not fresh
                    and current is not None
                    and current[0] == previous
                ),
                "the complete graph pair changed before staging",
            )
            stages[name] = owned_stage(
                directory,
                name,
                updated,
                operations,
            )
            retained_directory(directory, identity, operations)
        if not fresh:
            for name, previous, _ in pairs:
                current = read_existing_output(
                    directory,
                    name,
                    operations,
                )
                require(
                    current is not None and current[0] == previous,
                    "the authenticated chart changed before backup",
                )
                backup = (
                    ".rebar-substitution-buffer-overview-v2-backup-"
                    + name
                    + "-"
                    + str(os.getpid())
                    + "-"
                    + hashlib.sha256(previous).hexdigest()[:20]
                )
                operations.link(
                    name,
                    backup,
                    src_dir_fd=directory,
                    dst_dir_fd=directory,
                    follow_symlinks=False,
                )
                named = operations.stat(
                    backup,
                    dir_fd=directory,
                    follow_symlinks=False,
                )
                original = current[1]
                require(
                    stat.S_ISREG(named.st_mode)
                    and (
                        named.st_dev,
                        named.st_ino,
                        named.st_size,
                    ) == (
                        original.st_dev,
                        original.st_ino,
                        original.st_size,
                    ),
                    "a rollback backup escaped its exact previous graph",
                )
                backups[name] = (
                    backup,
                    (
                        named.st_dev,
                        named.st_ino,
                        named.st_size,
                    ),
                )
                retained_directory(directory, identity, operations)
        operations.fsync(directory)
        for name, previous, updated in pairs:
            current = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                (
                    fresh and current is None
                )
                or (
                    not fresh
                    and current is not None
                    and current[0] == previous
                ),
                "a graph output changed immediately before commit",
            )
            temporary, staged_identity = stages[name]
            named = operations.stat(
                temporary,
                dir_fd=directory,
                follow_symlinks=False,
            )
            require(
                (
                    named.st_dev,
                    named.st_ino,
                    named.st_size,
                ) == staged_identity,
                "the fully staged substitution-buffer output was replaced",
            )
            if fresh:
                operations.link(
                    temporary,
                    name,
                    src_dir_fd=directory,
                    dst_dir_fd=directory,
                    follow_symlinks=False,
                )
            else:
                operations.replace(
                    temporary,
                    name,
                    src_dir_fd=directory,
                    dst_dir_fd=directory,
                )
            committed.append(name)
            observed = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                observed is not None and observed[0] == updated,
                "a committed substitution-buffer graph failed exact readback",
            )
            retained_directory(directory, identity, operations)
        operations.fsync(directory)
        for name, _, updated in pairs:
            observed = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                observed is not None and observed[0] == updated,
                "the complete committed graph pair failed verification",
            )
        retained_directory(directory, identity, operations)
    except BaseException as original_error:
        rollback_error: BaseException | None = None
        try:
            for name in reversed(committed):
                observed = read_existing_output(
                    directory,
                    name,
                    operations,
                )
                require(
                    observed is not None
                    and observed[0] == updates[name],
                    "refusing to roll back an externally altered graph",
                )
                if fresh:
                    temporary, stage_identity = stages[name]
                    del temporary
                    remove_owned_name(
                        directory,
                        name,
                        stage_identity,
                        operations,
                    )
                else:
                    backup, backup_identity = backups[name]
                    named = operations.stat(
                        backup,
                        dir_fd=directory,
                        follow_symlinks=False,
                    )
                    require(
                        (
                            named.st_dev,
                            named.st_ino,
                            named.st_size,
                        ) == backup_identity,
                        "a rollback backup was substituted",
                    )
                    operations.replace(
                        backup,
                        name,
                        src_dir_fd=directory,
                        dst_dir_fd=directory,
                    )
                    restored = read_existing_output(
                        directory,
                        name,
                        operations,
                    )
                    require(
                        restored is not None
                        and restored[0] == originals[name],
                        "an exact previous graph could not be restored",
                    )
                    del backups[name]
            for name, (
                backup,
                backup_identity,
            ) in list(backups.items()):
                remove_owned_name(
                    directory,
                    backup,
                    backup_identity,
                    operations,
                )
                del backups[name]
            for name, (
                temporary,
                stage_identity,
            ) in list(stages.items()):
                if fresh or name not in committed:
                    remove_owned_name(
                        directory,
                        temporary,
                        stage_identity,
                        operations,
                    )
            operations.fsync(directory)
            for name, previous, _ in pairs:
                observed = read_existing_output(
                    directory,
                    name,
                    operations,
                )
                require(
                    (
                        fresh and observed is None
                    )
                    or (
                        not fresh
                        and observed is not None
                        and observed[0] == previous
                    ),
                    "the failed transaction did not restore the full pair",
                )
        except BaseException as error:
            rollback_error = error
        if rollback_error is not None:
            raise OverviewError(
                "substitution-buffer graph publication failed; preserve "
                "owned rollback files because full recovery is unverified",
            ) from rollback_error
        raise original_error
    for name, (
        backup,
        backup_identity,
    ) in list(backups.items()):
        remove_owned_name(
            directory,
            backup,
            backup_identity,
            operations,
        )
        del backups[name]
    if fresh:
        for _, (
            temporary,
            stage_identity,
        ) in list(stages.items()):
            remove_owned_name(
                directory,
                temporary,
                stage_identity,
                operations,
            )
    operations.fsync(directory)
    for name, _, updated in pairs:
        observed = read_existing_output(
            directory,
            name,
            operations,
        )
        require(
            observed is not None and observed[0] == updated,
            "the final safe graph pair changed after publication",
        )

def authenticate_pinned_python() -> None:
    expected = valid_hash(
        PINNED_PYTHON_SHA256,
        "the exact stable CPython 3.14.6 executable",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(PINNED_PYTHON, flags)
    try:
        before = os.fstat(descriptor)
        named = os.stat(PINNED_PYTHON, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and (before.st_dev, before.st_ino, before.st_size)
            == (named.st_dev, named.st_ino, named.st_size)
            and 0 < before.st_size <= MAX_BINARY_BYTES,
            "the exact isolated stable Python executable was replaced",
        )
        observed = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(CHUNK_BYTES, remaining))
            require(
                type(block) is bytes and bool(block),
                "the exact stable Python executable was truncated",
            )
            observed.update(block)
            remaining -= len(block)
        after = os.fstat(descriptor)
        final = os.stat(PINNED_PYTHON, follow_symlinks=False)
        require(
            os.read(descriptor, 1) == b""
            and observed.hexdigest() == expected
            and (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            == (final.st_dev, final.st_ino, final.st_size),
            "the complete pinned stable CPython executable changed",
        )
    finally:
        os.close(descriptor)


def render(
    source: str,
    manifest_relative: str,
    manifest_hash: str,
    *,
    replace: bool = False,
    previous_svg: str | None = None,
    previous_summary: str | None = None,
) -> dict[str, Any]:
    verify_runtime()
    source = valid_hash(source, "the explicitly frozen chart renderer")
    manifest_hash = valid_hash(
        manifest_hash,
        "the externally frozen immutable chart inputs",
    )
    require(
        manifest_relative == MANIFEST_RELATIVE,
        "render only the independently authored 5,120-case input manifest",
    )
    read_frozen(SOURCE_RELATIVE, source, MAX_SOURCE_BYTES)
    authenticate_pinned_python()
    manifest = decode_document(
        read_frozen(MANIFEST_RELATIVE, manifest_hash, MAX_SOURCE_BYTES),
        "the independent immutable replacement-and-buffer input manifest",
        MAX_SOURCE_BYTES,
    )
    validators = ActualValidators()
    svg, summary = build_documents(
        manifest,
        source,
        manifest_hash,
        actual_loader,
        validators,
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    opened: list[int] = []
    replaced = False
    try:
        current = os.open(ROOT, flags)
        opened.append(current)
        for part in ("docs", "evidence"):
            current = os.open(part, flags, dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "the independently approved chart parent was replaced",
            )
        info = os.fstat(current)
        identity = (info.st_dev, info.st_ino)
        old_svg_result = read_existing_output(
            current,
            safe_parts(SVG_RELATIVE)[-1],
        )
        old_summary_result = read_existing_output(
            current,
            safe_parts(SUMMARY_RELATIVE)[-1],
        )
        old_svg = (
            None if old_svg_result is None else old_svg_result[0]
        )
        old_summary = (
            None if old_summary_result is None else old_summary_result[0]
        )
        replaced = approve_publication(
            old_svg,
            old_summary,
            svg,
            summary,
            replace,
            previous_svg,
            previous_summary,
            source,
        )
        if old_svg is None or replaced:
            atomic_publish_pair(
                current,
                identity,
                old_svg,
                old_summary,
                svg,
                summary,
            )
        else:
            require(
                old_svg == svg and old_summary == summary,
                "an unchanged no-overwrite chart pair was substituted",
            )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)
    verify_runtime()
    document = decode_document(
        summary,
        "the complete generated substitution-buffer summary",
        MAX_SOURCE_BYTES,
    )
    return {
        "schema": SCHEMA + "-rendered",
        "status": "PASS",
        "source_sha256": source,
        "manifest_relative": MANIFEST_RELATIVE,
        "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "summary_relative": SUMMARY_RELATIVE,
        "summary_sha256": hashlib.sha256(summary).hexdigest(),
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "published_seed": PUBLISHED_SEED,
        "replaced_generated_pair": replaced,
        "rows": [
            {
                "family": row["family"],
                "passed": row["passed"],
                "failed": row["failed"],
                "not_measured": row["not_measured"],
            }
            for row in document["families"]
        ],
        "overall": document["overall"],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }

class SourceOnlyBoundary:
    """Prevent every actual external effect during synthetic chart tests."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "reads": 0,
            "writes": 0,
            "workers": 0,
            "imports": 0,
            "threads": 0,
            "clocks": 0,
            "garbage_collections": 0,
            "randomness": 0,
            "matchers": 0,
        }

    def install(
        self,
        owner: Any,
        name: str,
        category: str,
    ) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)
        self.originals.append((owner, name, original))

        def denied(*args: Any, **kwargs: Any) -> Any:
            actual = category
            if category == "reads":
                mode = (
                    args[1]
                    if len(args) > 1
                    else kwargs.get("mode", "r")
                )
                if type(mode) is str and any(
                    item in mode for item in "wax+"
                ):
                    actual = "writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY
                    | os.O_RDWR
                    | os.O_CREAT
                    | os.O_TRUNC
                    | os.O_APPEND
                ):
                    actual = "writes"
            self.blocked[actual] += 1
            raise SourceOnlyError(
                "source-only substitution-buffer controls forbid " + actual,
            )

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, name, category in (
            (builtins, "open", "reads"),
            (io, "open", "reads"),
            (os, "open", "reads"),
            (os, "stat", "reads"),
            (os, "lstat", "reads"),
            (os, "scandir", "reads"),
            (os, "listdir", "reads"),
            (os, "readlink", "reads"),
            (os, "write", "writes"),
            (os, "replace", "writes"),
            (os, "rename", "writes"),
            (os, "link", "writes"),
            (os, "unlink", "writes"),
            (os, "remove", "writes"),
            (os, "mkdir", "writes"),
            (os, "makedirs", "writes"),
            (os, "fsync", "writes"),
            (subprocess, "run", "workers"),
            (subprocess, "Popen", "workers"),
            (os, "system", "workers"),
            (os, "fork", "workers"),
            (os, "posix_spawn", "workers"),
            (importlib, "import_module", "imports"),
            (builtins, "__import__", "imports"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clocks"),
            (time, "time_ns", "clocks"),
            (time, "monotonic", "clocks"),
            (time, "monotonic_ns", "clocks"),
            (time, "perf_counter", "clocks"),
            (time, "perf_counter_ns", "clocks"),
            (gc, "collect", "garbage_collections"),
            (os, "urandom", "randomness"),
        ):
            self.install(owner, name, category)
        return self

    def __exit__(
        self,
        error_type: Any,
        error: Any,
        trace: Any,
    ) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False

def synthetic_stream(
    raw: bytes,
    *,
    archive: bytes | None = None,
    archive_hash: str | None = None,
    original_hash: str | None = None,
    original_bytes: int | None = None,
    fields: frozenset[str] = frozenset({"proof", "value"}),
) -> dict[str, Any]:
    require(
        type(raw) is bytes and bool(raw),
        "an exclusively in-memory complete gzip control is mandatory",
    )
    if archive is None:
        compressor = zlib.compressobj(
            level=9,
            wbits=16 + zlib.MAX_WBITS,
        )
        archive = compressor.compress(raw) + compressor.flush()
    require(
        type(archive) is bytes and bool(archive),
        "an exclusively in-memory gzip member is mandatory",
    )
    selected_archive = (
        hashlib.sha256(archive).hexdigest()
        if archive_hash is None
        else archive_hash
    )
    selected_original = (
        hashlib.sha256(raw).hexdigest()
        if original_hash is None
        else original_hash
    )
    selected_bytes = (
        len(raw) if original_bytes is None else original_bytes
    )
    descriptor = -5_120_071
    position = 0
    previous = os.read

    def read_memory(
        selected: int,
        requested: int,
    ) -> bytes:
        nonlocal position
        require(
            selected == descriptor
            and type(requested) is int
            and requested > 0,
            "a synthetic gzip attempted to read a genuine descriptor",
        )
        block = archive[position:position + requested]
        position += len(block)
        return block

    os.read = read_memory
    try:
        stream = VerifiedGzipReader(
            descriptor,
            len(archive),
            selected_archive,
            selected_bytes,
            selected_original,
        )
        value = StreamingObject(stream).select(fields)
        require(
            stream.finished and position == len(archive),
            "the complete in-memory gzip was not authenticated",
        )
        return value
    finally:
        os.read = previous

class SyntheticPublication:
    """Exercise full fresh and replacement transactions with fake files."""

    def __init__(
        self,
        svg: bytes | None,
        summary: bytes | None,
        *,
        fail_replace: int | None = None,
        fail_link: int | None = None,
        fail_stage_write: bool = False,
    ) -> None:
        self.directory = 71
        self.next_descriptor = 80
        self.next_inode = 100_000
        self.files: dict[str, dict[str, Any]] = {}
        self.descriptors: dict[int, dict[str, Any]] = {}
        self.replace_count = 0
        self.publish_link_count = 0
        self.fail_replace = fail_replace
        self.fail_link = fail_link
        self.fail_stage_write = fail_stage_write
        self.failed_once = False
        self.sync_count = 0
        if svg is not None:
            self.install(safe_parts(SVG_RELATIVE)[-1], svg)
        if summary is not None:
            self.install(safe_parts(SUMMARY_RELATIVE)[-1], summary)

    def install(self, name: str, raw: bytes) -> None:
        self.next_inode += 1
        self.files[name] = {
            "raw": bytearray(raw),
            "device": 7,
            "inode": self.next_inode,
        }

    def info(self, value: Mapping[str, Any]) -> os.stat_result:
        return os.stat_result((
            stat.S_IFREG | 0o644,
            value["inode"],
            value["device"],
            1,
            0,
            0,
            len(value["raw"]),
            0,
            0,
            0,
        ))

    def open(
        self,
        name: str,
        flags: int,
        mode: int = 0o644,
        *,
        dir_fd: int | None = None,
    ) -> int:
        del mode
        require(
            dir_fd == self.directory and type(name) is str,
            "the fake chart transaction escaped its fake directory",
        )
        if flags & os.O_CREAT:
            require(
                flags & os.O_EXCL and name not in self.files,
                "a fake graph staging file was not exclusive",
            )
            self.install(name, b"")
        elif name not in self.files:
            raise FileNotFoundError(name)
        self.next_descriptor += 1
        descriptor = self.next_descriptor
        self.descriptors[descriptor] = {
            "entry": self.files[name],
            "offset": 0,
            "writable": bool(
                flags & (os.O_WRONLY | os.O_RDWR),
            ),
        }
        return descriptor

    def fstat(self, descriptor: int) -> os.stat_result:
        if descriptor == self.directory:
            return os.stat_result((
                stat.S_IFDIR | 0o755,
                7_001,
                7,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
            ))
        require(
            descriptor in self.descriptors,
            "a fake chart transaction used a real descriptor",
        )
        return self.info(
            self.descriptors[descriptor]["entry"],
        )

    def stat(
        self,
        name: str,
        *,
        dir_fd: int | None = None,
        follow_symlinks: bool = False,
    ) -> os.stat_result:
        require(
            dir_fd == self.directory
            and follow_symlinks is False,
            "a fake chart transaction accessed a real path",
        )
        if name not in self.files:
            raise FileNotFoundError(name)
        return self.info(self.files[name])

    def read(self, descriptor: int, count: int) -> bytes:
        require(
            descriptor in self.descriptors
            and type(count) is int
            and count > 0,
            "a fake chart transaction attempted a genuine read",
        )
        selected = self.descriptors[descriptor]
        start = selected["offset"]
        result = bytes(
            selected["entry"]["raw"][start:start + count],
        )
        selected["offset"] = start + len(result)
        return result

    def write(self, descriptor: int, value: bytes) -> int:
        require(
            descriptor in self.descriptors
            and self.descriptors[descriptor]["writable"]
            and type(value) is bytes,
            "a fake chart transaction attempted a genuine write",
        )
        if self.fail_stage_write and not self.failed_once:
            self.failed_once = True
            raise OSError("synthetic staged chart write failure")
        selected = self.descriptors[descriptor]
        selected["entry"]["raw"].extend(value)
        selected["offset"] += len(value)
        return len(value)

    def fsync(self, descriptor: int) -> None:
        require(
            descriptor == self.directory
            or descriptor in self.descriptors,
            "a fake chart transaction synchronized a real descriptor",
        )
        self.sync_count += 1

    def close(self, descriptor: int) -> None:
        require(
            descriptor in self.descriptors,
            "a fake chart transaction closed a real descriptor",
        )
        del self.descriptors[descriptor]

    def link(
        self,
        source: str,
        destination: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = False,
    ) -> None:
        require(
            src_dir_fd == dst_dir_fd == self.directory
            and follow_symlinks is False
            and source in self.files
            and destination not in self.files,
            "a fake chart link escaped the in-memory transaction",
        )
        if destination in {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        }:
            self.publish_link_count += 1
            if (
                self.fail_link == self.publish_link_count
                and not self.failed_once
            ):
                self.failed_once = True
                raise OSError(
                    "synthetic atomic no-overwrite graph link failure",
                )
        self.files[destination] = self.files[source]

    def replace(
        self,
        source: str,
        destination: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        require(
            src_dir_fd == dst_dir_fd == self.directory
            and source in self.files
            and destination in self.files,
            "a fake graph replacement escaped its chart pair",
        )
        if source.startswith(
            ".rebar-substitution-buffer-overview-v2-stage-",
        ):
            self.replace_count += 1
            if (
                self.fail_replace == self.replace_count
                and not self.failed_once
            ):
                self.failed_once = True
                raise OSError(
                    "synthetic atomic paired graph replacement failure",
                )
        self.files[destination] = self.files.pop(source)

    def unlink(
        self,
        name: str,
        *,
        dir_fd: int | None = None,
    ) -> None:
        require(
            dir_fd == self.directory
            and name in self.files
            and (
                name.startswith(
                    ".rebar-substitution-buffer-overview-v2-",
                )
                or name in {
                    safe_parts(SVG_RELATIVE)[-1],
                    safe_parts(SUMMARY_RELATIVE)[-1],
                }
            ),
            "a fake transaction attempted to delete a real file",
        )
        del self.files[name]

    def pair(self) -> tuple[bytes | None, bytes | None]:
        result: list[bytes | None] = []
        for name in (
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        ):
            entry = self.files.get(name)
            result.append(
                None if entry is None else bytes(entry["raw"]),
            )
        return result[0], result[1]

    def only_outputs_remain(self) -> bool:
        output_names = {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        }
        return (
            not (set(self.files) - output_names)
            and not self.descriptors
        )

def synthetic_hash(label: str) -> str:
    require(type(label) is str and bool(label), "name each synthetic control")
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def synthetic_capture(value: Mapping[str, Any]) -> dict[str, Any]:
    raw = canonical(dict(value))
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def restore_synthetic_capture(value: Any, label: str) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"base64", "bytes", "sha256", "complete"}
        and type(value.get("base64")) is str
        and type(value.get("bytes")) is int
        and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
        and value.get("complete") is True,
        "restore the complete solely in-memory worker: " + label,
    )
    try:
        raw = base64.b64decode(
            value["base64"].encode("ascii"),
            validate=True,
        )
    except (ValueError, UnicodeError, binascii.Error) as error:
        raise OverviewError(
            "a synthetic complete worker stream is not reversible",
        ) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"],
        "a complete synthetic candidate or baseline stream changed",
    )
    return decode_document(raw, label, MAX_SOURCE_BYTES)


def synthetic_preserved_failure() -> dict[str, Any]:
    envelope = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v1-failure"
        ),
        "status": "FAIL",
        "error": "a complete substitution report exceeds its bound",
        "error_type": "RecorderError",
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-v1-"
            "controller-failure-preserved-v1"
        ),
        "status": "FAIL",
        "python": "3.14.6",
        "label": HISTORICAL_V1_BASELINE_LABEL,
        "recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "recorder_source_sha256": PREVIOUS_RECORDER_SHA256,
        "oracle_relative": HISTORICAL_V1_ORACLE_RELATIVE,
        "oracle_source_sha256": HISTORICAL_V1_ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "actual_reference_worker_count": "UNKNOWN",
        "reported_reference_worker_count_is_reliable": False,
        "baseline_result_status": "NOT MEASURED",
        "reference_outcomes_status": "NOT MEASURED",
        "report_publication_status": "NOT PUBLISHED",
        "receipt_publication_status": "NOT PUBLISHED",
        "actual_baseline_controller_invocations": 1,
        "actual_candidate_workers": 0,
        "controller_exit_code": 1,
        "failure_explanation": (
            "The complete original controller exceeded its "
            "268435456-byte bound; its outer reference count is not "
            "reliable and remains UNKNOWN."
        ),
        "complete_controller_failure_stdout": envelope,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def synthetic_owner(
    relative: str,
    source: str,
    index: int,
    *,
    external: bool = False,
) -> dict[str, Any]:
    return {
        "path" if external else "relative": relative,
        "sha256": valid_hash(source, relative),
        "bytes": 4_096 + index,
        "device": 7,
        "inode": 100_000 + index,
    }


def synthetic_family_selection(
    family: str,
    state: str,
) -> dict[str, Any]:
    require(
        family in FAMILY_ORDER and state in {"RUN", "NOT MEASURED"},
        "select exactly one synthetic independently owned native family",
    )
    adapter_path, engine_path, bridge_path, owned_paths = (
        FAMILY_SPECS[family]
    )
    sources = {
        relative: synthetic_hash("synthetic-source:" + relative)
        for relative in owned_paths
    }
    engine = synthetic_hash("synthetic-native:" + engine_path)
    bridge = (
        engine
        if bridge_path == engine_path
        else synthetic_hash("synthetic-native:" + bridge_path)
    )
    return {
        "family": family,
        "candidate_source_sha256": sources[adapter_path],
        "native_engine_sha256": engine,
        "native_bridge_sha256": bridge,
        "owned_source_sha256": sources,
        "state": state,
        "report": None,
        "receipt": None,
        "superseded": [],
    }


def synthetic_family_owner(
    selected: Mapping[str, Any],
) -> dict[str, Any]:
    family = selected["family"]
    _, engine_path, bridge_path, _ = FAMILY_SPECS[family]
    native = {engine_path: selected["native_engine_sha256"]}
    if bridge_path != engine_path:
        native[bridge_path] = selected["native_bridge_sha256"]
    policies = {
        POLICY_V2_RELATIVE: POLICY_V2_SHA256,
        V5_RELATIVE: V5_SHA256,
    }
    manifest = {
        "family": family,
        "candidate_source_sha256": selected[
            "candidate_source_sha256"
        ],
        "native_engine_sha256": selected["native_engine_sha256"],
        "native_bridge_sha256": selected["native_bridge_sha256"],
        "source_sha256": dict(
            sorted(selected["owned_source_sha256"].items()),
        ),
        "native_sha256": dict(sorted(native.items())),
        "immutable_policy_sha256": dict(sorted(policies.items())),
    }
    index = 1
    source_owners: dict[str, dict[str, Any]] = {}
    for relative, source in manifest["source_sha256"].items():
        source_owners[relative] = synthetic_owner(
            relative,
            source,
            index,
        )
        index += 1
    native_owners: dict[str, dict[str, Any]] = {}
    for relative, source in manifest["native_sha256"].items():
        native_owners[relative] = synthetic_owner(
            relative,
            source,
            index,
        )
        index += 1
    policy_owners: dict[str, dict[str, Any]] = {}
    for relative, source in policies.items():
        policy_owners[relative] = synthetic_owner(
            relative,
            source,
            index,
        )
        index += 1
    return {
        "family": family,
        "manifest": manifest,
        "source_owners": source_owners,
        "native_owners": native_owners,
        "policy_owners": policy_owners,
        "oracle_owner": synthetic_owner(
            AUDIT_RELATIVE,
            AUDIT_SHA256,
            index,
        ),
        "python_owner": synthetic_owner(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            index + 1,
            external=True,
        ),
    }


def synthetic_records() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    matrix: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for index in range(CASE_COUNT):
        cohort = COHORTS[index // VARIANTS_PER_COHORT]
        api = APIS[index % len(APIS)]
        case = (
            "substitution-buffer-semantics.v1."
            + format(index, "05d")
        )
        matrix.append({
            "case": case,
            "cohort": cohort,
            "api": api,
            "seed": PUBLISHED_SEED,
            "variant": index % VARIANTS_PER_COHORT,
        })
        records.append({
            "case": case,
            "cohort": cohort,
            "api": api,
            "outcome": {
                "kind": "synthetic-match",
                "index": index,
            },
        })
    require(
        len(matrix) == len(records) == CASE_COUNT,
        "construct every solely in-memory 5,120-case control",
    )
    return matrix, records


def synthetic_compare(
    matrix: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    candidate: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    dict[str, int],
    dict[str, int],
]:
    require(
        type(matrix) is list
        and type(baseline) is list
        and type(candidate) is list
        and len(matrix) == len(baseline) == len(candidate) == CASE_COUNT,
        "compare every source-ordered solely in-memory case",
    )
    mismatches: list[dict[str, Any]] = []
    by_cohort = {cohort: 0 for cohort in COHORTS}
    by_api = {api: 0 for api in APIS}
    for index, (case, original, actual) in enumerate(
        zip(matrix, baseline, candidate, strict=True),
    ):
        require(
            case["case"] == original.get("case") == actual.get("case")
            and case["cohort"]
            == original.get("cohort") == actual.get("cohort")
            and case["api"] == original.get("api") == actual.get("api")
            and case["cohort"] in by_cohort
            and case["api"] in by_api,
            "a complete synthetic case or outcome was reordered",
        )
        if original["outcome"] != actual["outcome"]:
            by_cohort[case["cohort"]] += 1
            by_api[case["api"]] += 1
            mismatches.append({
                "index": index,
                "case": case["case"],
                "cohort": case["cohort"],
                "api": case["api"],
                "baseline_outcome_sha256": digest(
                    original["outcome"],
                ),
                "candidate_outcome_sha256": digest(
                    actual["outcome"],
                ),
            })
    require(
        len(mismatches)
        == sum(by_cohort.values())
        == sum(by_api.values()),
        "a real-shaped synthetic mismatch was hidden",
    )
    return mismatches, by_cohort, by_api


class SyntheticValidators:
    """Validate complete real-shaped fixtures without files or workers."""

    def __init__(
        self,
        matrix: list[dict[str, Any]],
        records: list[dict[str, Any]],
    ) -> None:
        self.matrix = matrix
        self.records = records
        self.preserved = validate_preserved_failure(
            synthetic_preserved_failure(),
        )

    def authenticate_family(
        self,
        family: str,
        selected: Mapping[str, Any],
    ) -> dict[str, Any]:
        adapter_path, engine_path, bridge_path, owned_paths = (
            FAMILY_SPECS[family]
        )
        sources = selected["owned_source_sha256"]
        require(
            type(sources) is dict
            and set(sources) == set(owned_paths)
            and all(
                valid_hash(sources[relative], relative)
                == synthetic_hash("synthetic-source:" + relative)
                for relative in owned_paths
            )
            and selected["candidate_source_sha256"]
            == sources[adapter_path]
            and selected["native_engine_sha256"]
            == synthetic_hash("synthetic-native:" + engine_path)
            and selected["native_bridge_sha256"]
            == (
                selected["native_engine_sha256"]
                if engine_path == bridge_path
                else synthetic_hash("synthetic-native:" + bridge_path)
            )
            and (
                selected["native_engine_sha256"]
                == selected["native_bridge_sha256"]
            )
            is (family == "c"),
            "a synthetic complete native family or C-only alias was forged",
        )
        return {
            "family": family,
            "baseline": BASELINE_RECORDS_SHA256,
        }

    def validate_baseline(
        self,
        receipt: Any,
        report: Any,
        pins: Any,
    ) -> dict[str, Any]:
        require(
            type(receipt) is dict
            and set(receipt) == BASELINE_RECEIPT_FIELDS
            and type(report) is dict
            and set(report) == BASELINE_FIELDS
            and type(pins) is dict
            and pins.get("baseline") == BASELINE_RECORDS_SHA256,
            "a complete real-shaped synthetic baseline field was omitted",
        )
        fixed_fields(
            receipt,
            {
                "schema": (
                    "rebar-independent-substitution-buffer-semantics-"
                    "recorder-v3-durable-baseline-publication-receipt"
                ),
                "status": "PASS",
                "baseline_result_status": "PASS",
                "report_sha256": BASELINE_ARCHIVE_SHA256,
                "report_relative": BASELINE_ARCHIVE_RELATIVE,
                "receipt_relative": BASELINE_RECEIPT_RELATIVE,
                "baseline_reference_pids": [82, 83],
                "actual_reference_workers": 2,
                "actual_candidate_workers": 0,
                "actual_candidate_imports": 0,
                "baseline_records_sha256": BASELINE_RECORDS_SHA256,
                "validated_reference_a_case_count": CASE_COUNT,
                "validated_reference_b_case_count": CASE_COUNT,
                **frozen_baseline_fields(BASELINE_LABEL),
            },
            "the complete solely in-memory baseline receipt",
        )
        fixed_fields(
            report,
            {
                "schema": (
                    "rebar-independent-substitution-buffer-semantics-"
                    "recorder-v3-complete-baseline-report"
                ),
                "status": "PASS",
                "baseline_reference_pids": [82, 83],
                "actual_reference_workers": 2,
                "actual_candidate_workers": 0,
                "actual_candidate_imports": 0,
                "baseline_records_sha256": BASELINE_RECORDS_SHA256,
                "validated_reference_a_case_count": CASE_COUNT,
                "validated_reference_b_case_count": CASE_COUNT,
                **frozen_baseline_fields(BASELINE_LABEL),
            },
            "the complete solely in-memory baseline report",
        )
        controller = restore_synthetic_capture(
            report["complete_baseline_process_stdout"],
            "the solely in-memory two-reference controller",
        )
        require(
            controller.get("reference_pids") == [82, 83]
            and controller.get("reference_a_records") == self.records
            and controller.get("reference_b_records") == self.records
            and report["complete_baseline_process_stderr"]
            == synthetic_capture({})
            and receipt["report_uncompressed_sha256"]
            == digest(report)
            and receipt["report_uncompressed_bytes"]
            == len(canonical(report)),
            "both full solely in-memory reference streams must agree",
        )
        return {
            **report,
            "reference_a_records": self.records,
            "reference_b_records": self.records,
        }

    def validate_candidate(
        self,
        family: str,
        selected: Mapping[str, Any],
        receipt: Any,
        report: Any,
        baseline: Mapping[str, Any],
        *,
        historical: bool = False,
    ) -> dict[str, Any]:
        require(
            type(receipt) is dict
            and set(receipt) == CANDIDATE_RECEIPT_FIELDS
            and type(report) is dict
            and set(report) == CANDIDATE_FIELDS
            and baseline.get("reference_a_records") == self.records
            and receipt.get("candidate_family") == family
            and report.get("candidate_family") == family
            and receipt.get("status") == "PASS"
            and receipt.get("report_relative")
            == selected.get("_report_relative")
            and receipt.get("report_sha256")
            == selected.get("_report_sha256")
            and receipt.get("receipt_relative")
            == selected.get("_receipt_relative")
            and receipt.get("baseline_reference_pids") == [82, 83]
            and report.get("baseline_reference_pids") == [82, 83]
            and receipt.get("validated_prior_reference_workers") == 2
            and report.get("validated_prior_reference_workers") == 2
            and receipt.get("actual_reference_workers") == 0
            and report.get("actual_reference_workers") == 0
            and receipt.get("actual_candidate_workers") == 1
            and report.get("actual_candidate_workers") == 1
            and receipt.get("actual_method_guard_checks")
            == 2 * CASE_COUNT
            and report.get("actual_method_guard_checks")
            == 2 * CASE_COUNT
            and receipt.get("actual_warning_registry_guard_checks")
            == 2 * CASE_COUNT
            and report.get("actual_warning_registry_guard_checks")
            == 2 * CASE_COUNT,
            "a full real-shaped isolated synthetic observation was hidden",
        )
        if not historical:
            fixed_fields(
                selected,
                {
                    "family": family,
                    "candidate_source_sha256": receipt[
                        "candidate_source_sha256"
                    ],
                    "native_engine_sha256": receipt[
                        "native_engine_sha256"
                    ],
                    "native_bridge_sha256": receipt[
                        "native_bridge_sha256"
                    ],
                    "owned_source_sha256": (
                        receipt["candidate_owner_before"]["manifest"][
                            "source_sha256"
                        ]
                    ),
                },
                "the real-shaped synthetic complete native source owner",
            )
        worker = restore_synthetic_capture(
            report["complete_candidate_process_stdout"],
            "the complete solely in-memory candidate worker",
        )
        records = worker.get("records")
        require(
            type(records) is list
            and len(records) == CASE_COUNT
            and worker.get("status") == "OBSERVED"
            and worker.get("role") == "candidate-" + family
            and worker.get("pid") == report["actual_candidate_pid"]
            and worker["pid"] not in [82, 83]
            and worker.get("actual_reference_workers") == 0
            and worker.get("validated_prior_reference_workers") == 2
            and worker.get("actual_candidate_workers") == 1,
            "the full synthetic worker was not separate from both references",
        )
        mismatches, by_cohort, by_api = synthetic_compare(
            self.matrix,
            self.records,
            records,
        )
        ledger = digest(mismatches)
        record_hash = digest(records)
        count = len(mismatches)
        expected_status = "FAIL" if count else "PASS"
        expected = {
            "candidate_records_sha256": record_hash,
            "mismatch_count": count,
            "mismatch_evidence_sha256": ledger,
            "mismatches_by_cohort": by_cohort,
            "mismatches_by_api": by_api,
            "all_mismatches_preserved": True,
        }
        fixed_fields(
            receipt,
            {
                **expected,
                "candidate_result_status": expected_status,
                "report_uncompressed_sha256": digest(report),
                "report_uncompressed_bytes": len(canonical(report)),
            },
            "the complete solely in-memory signed candidate receipt",
        )
        fixed_fields(
            report,
            {
                **expected,
                "status": expected_status,
                "all_mismatches": mismatches,
                "failure_count": 1 if count else 0,
                "actual_candidate_process_returncode": 0,
            },
            "the complete solely in-memory signed candidate report",
        )
        return {
            "state": "RUN",
            "candidate_result_status": expected_status,
            "publication_status": "PASS",
            "candidate_records_sha256": record_hash,
            "mismatch_evidence_sha256": ledger,
            "passed": CASE_COUNT - count,
            "failed": count,
            "not_measured": 0,
            "mismatches_by_cohort": by_cohort,
            "mismatches_by_api": by_api,
            "all_mismatches_preserved": True,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
            "actual_candidate_workers": 1,
            "actual_reference_workers": 0,
            "validated_prior_reference_workers": 2,
        }


def synthetic_candidate_documents(
    selected: Mapping[str, Any],
    matrix: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    failures: int,
    report_path: str,
    report_hash: str,
    receipt_path: str,
    *,
    label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        type(failures) is int and 0 <= failures <= CASE_COUNT,
        "bound every complete synthetic failure denominator",
    )
    family = selected["family"]
    owner = synthetic_family_owner(selected)
    records = [
        {
            **record,
            "outcome": (
                {
                    "kind": "synthetic-mismatch",
                    "family": family,
                    "index": index,
                }
                if index < failures
                else record["outcome"]
            ),
        }
        for index, record in enumerate(baseline)
    ]
    mismatches, by_cohort, by_api = synthetic_compare(
        matrix,
        baseline,
        records,
    )
    worker = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v3-isolated-candidate-worker"
        ),
        "status": "OBSERVED",
        "role": "candidate-" + family,
        "pid": 181 + FAMILY_ORDER.index(family),
        "candidate_family": family,
        "records": records,
        "records_sha256": digest(records),
        "baseline_reference_pids": [82, 83],
        "actual_reference_workers": 0,
        "validated_prior_reference_workers": 2,
        "actual_candidate_workers": 1,
    }
    report = {field: None for field in CANDIDATE_FIELDS}
    common = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v3-complete-candidate-report"
        ),
        "status": "FAIL" if failures else "PASS",
        **frozen_baseline_fields(BASELINE_LABEL),
        "label": label,
        "candidate_family": family,
        "candidate_source_sha256": selected[
            "candidate_source_sha256"
        ],
        "native_engine_sha256": selected["native_engine_sha256"],
        "native_bridge_sha256": selected["native_bridge_sha256"],
        "baseline_label": BASELINE_LABEL,
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": [82, 83],
        "candidate_owner_before": owner,
        "candidate_owner_after": owner,
        "candidate_owner_unchanged": True,
        "complete_candidate_process_stdout": synthetic_capture(worker),
        "complete_candidate_process_stderr": synthetic_capture({}),
        "complete_process_representation": (
            "single-canonical-candidate-stream"
        ),
        "candidate_records_reconstruction": (
            "decode-and-validate-complete-candidate-process-stdout"
        ),
        "baseline_records_reconstruction": (
            "decode-and-validate-pinned-complete-baseline-archive"
        ),
        "mismatch_outcome_reconstruction": (
            "frozen-matrix-plus-pinned-baseline-plus-candidate-stdout"
        ),
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "candidate_records_sha256": digest(records),
        "mismatch_count": failures,
        "all_mismatches": mismatches,
        "mismatch_evidence_sha256": digest(mismatches),
        "mismatches_by_cohort": by_cohort,
        "mismatches_by_api": by_api,
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": 3,
        "actual_candidate_process_invocations": 1,
        "actual_candidate_pid": worker["pid"],
        "actual_candidate_process_returncode": 0,
        "actual_candidate_process_signal": None,
        "actual_candidate_process_timed_out": False,
        "actual_candidate_process_spawn_error": None,
        "all_failure_reasons": (
            [
                "the independent candidate differs on "
                + str(failures)
                + " frozen substitution and buffer cases"
            ]
            if failures
            else []
        ),
        "failure_count": 1 if failures else 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        set(common) == CANDIDATE_FIELDS,
        "construct every real V2 complete candidate field",
    )
    report.update(common)
    receipt = {field: None for field in CANDIDATE_RECEIPT_FIELDS}
    expected_receipt = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v3-durable-candidate-publication-receipt"
        ),
        "status": "PASS",
        "candidate_result_status": report["status"],
        "python": "3.14.6",
        **historical_lineage_fields(),
        "label": label,
        "candidate_family": family,
        "candidate_source_sha256": selected[
            "candidate_source_sha256"
        ],
        "native_engine_sha256": selected["native_engine_sha256"],
        "native_bridge_sha256": selected["native_bridge_sha256"],
        "baseline_label": BASELINE_LABEL,
        "recorder_source_sha256": RECORDER_SHA256,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "cohorts": list(COHORTS),
        "apis": list(APIS),
        "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
        "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
        **frozen_bounds(),
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": [82, 83],
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "candidate_records_sha256": digest(records),
        "mismatch_count": failures,
        "mismatch_evidence_sha256": digest(mismatches),
        "mismatches_by_cohort": by_cohort,
        "mismatches_by_api": by_api,
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": 3,
        "actual_candidate_process_invocations": 1,
        "candidate_owner_before": owner,
        "candidate_owner_after": owner,
        "candidate_owner_unchanged": True,
        "report_relative": report_path,
        "report_sha256": report_hash,
        "report_bytes": 100_000 + len(mismatches),
        "report_uncompressed_sha256": digest(report),
        "report_uncompressed_bytes": len(canonical(report)),
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_path,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        set(expected_receipt) == CANDIDATE_RECEIPT_FIELDS,
        "construct every real V2 durable candidate receipt field",
    )
    receipt.update(expected_receipt)
    return receipt, report


def synthetic_fixture(
    *,
    c_failures: int = 7,
    zig_failures: int = 5,
    rust_state: str = "NOT MEASURED",
    c_state: str = "RUN",
    zig_state: str = "RUN",
    rust_failures: int = 0,
    history: bool = True,
) -> tuple[
    dict[str, Any],
    Loader,
    SyntheticValidators,
    dict[str, Any],
]:
    matrix, reference = synthetic_records()
    validators = SyntheticValidators(matrix, reference)
    selections = [
        synthetic_family_selection("rust", rust_state),
        synthetic_family_selection("c", c_state),
        synthetic_family_selection("zig", zig_state),
    ]
    baseline_report = {field: None for field in BASELINE_FIELDS}
    controller = {
        "schema": "synthetic-complete-two-reference-controller",
        "reference_pids": [82, 83],
        "reference_a_records": reference,
        "reference_b_records": reference,
    }
    baseline_report.update({
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v3-complete-baseline-report"
        ),
        "status": "PASS",
        **frozen_baseline_fields(BASELINE_LABEL),
        "source_closure_before": {},
        "source_closure_after": {},
        "source_closure_unchanged": True,
        "complete_baseline_process_stdout": synthetic_capture(
            controller,
        ),
        "complete_baseline_process_stderr": synthetic_capture({}),
        "complete_process_representation": (
            "single-canonical-controller-stream"
        ),
        "baseline_result_reconstruction": (
            "decode-and-validate-complete-baseline-process-stdout"
        ),
        "baseline_result_sha256": digest(controller),
        "baseline_failure_schema": None,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": [82, 83],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "actual_baseline_controller_pid": 180,
        "actual_baseline_process_returncode": 0,
        "actual_baseline_process_signal": None,
        "actual_baseline_process_timed_out": False,
        "actual_baseline_process_spawn_error": None,
        "all_failure_reasons": [],
        "failure_count": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    })
    require(
        set(baseline_report) == BASELINE_FIELDS,
        "build all 64 complete baseline report fields",
    )
    baseline_receipt = {
        field: None
        for field in BASELINE_RECEIPT_FIELDS
    }
    baseline_receipt.update({
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v3-durable-baseline-publication-receipt"
        ),
        "status": "PASS",
        "baseline_result_status": "PASS",
        **frozen_baseline_fields(BASELINE_LABEL),
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_reference_pids": [82, 83],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "source_closure_before": {},
        "source_closure_after": {},
        "source_closure_unchanged": True,
        "report_relative": BASELINE_ARCHIVE_RELATIVE,
        "report_sha256": BASELINE_ARCHIVE_SHA256,
        "report_bytes": BASELINE_ARCHIVE_BYTES,
        "report_uncompressed_sha256": digest(baseline_report),
        "report_uncompressed_bytes": len(
            canonical(baseline_report),
        ),
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_baseline": True,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    })
    require(
        set(baseline_receipt) == BASELINE_RECEIPT_FIELDS,
        "build all 65 complete signed baseline receipt fields",
    )
    documents: dict[
        tuple[str, str, str],
        dict[str, Any],
    ] = {
        (
            BASELINE_RECEIPT_RELATIVE,
            BASELINE_RECEIPT_SHA256,
            "receipt",
        ): baseline_receipt,
        (
            BASELINE_ARCHIVE_RELATIVE,
            BASELINE_ARCHIVE_SHA256,
            "baseline",
        ): baseline_report,
    }
    observations: dict[str, Any] = {
        "matrix": matrix,
        "reference": reference,
        "baseline_receipt": baseline_receipt,
        "baseline_report": baseline_report,
        "candidate_receipts": {},
        "candidate_reports": {},
    }
    for selected in selections:
        family = selected["family"]
        if selected["state"] == "NOT MEASURED":
            continue
        failures = {
            "rust": rust_failures,
            "c": c_failures,
            "zig": zig_failures,
        }[family]
        label = "synthetic-complete-" + family + "-v2"
        report_path = (
            EVIDENCE_DIRECTORY + "/" + family
            + "-substitution-buffer-semantics-v2-"
            + label + ".json.gz"
        )
        receipt_path = (
            EVIDENCE_DIRECTORY + "/" + family
            + "-substitution-buffer-semantics-v2-"
            + label + "-publication-receipt.json"
        )
        report_hash = synthetic_hash("synthetic-report:" + report_path)
        receipt_hash = synthetic_hash("synthetic-receipt:" + receipt_path)
        selected["report"] = report_pin(report_path, report_hash)
        selected["receipt"] = report_pin(receipt_path, receipt_hash)
        receipt, report = synthetic_candidate_documents(
            selected,
            matrix,
            reference,
            failures,
            report_path,
            report_hash,
            receipt_path,
            label=label,
        )
        documents[(receipt_path, receipt_hash, "receipt")] = receipt
        documents[(report_path, report_hash, "candidate")] = report
        observations["candidate_receipts"][family] = receipt
        observations["candidate_reports"][family] = report
    if history:
        require(
            selections[1]["state"] == "RUN",
            "synthetic history requires a measured corrected C family",
        )
        selected = selections[1]
        previous_label = "synthetic-preserved-c-failure-v0"
        previous_report = (
            EVIDENCE_DIRECTORY
            + "/c-substitution-buffer-semantics-v2-"
            + previous_label
            + ".json.gz"
        )
        previous_receipt = (
            EVIDENCE_DIRECTORY
            + "/c-substitution-buffer-semantics-v2-"
            + previous_label
            + "-publication-receipt.json"
        )
        previous_report_hash = synthetic_hash(
            "synthetic-report:" + previous_report,
        )
        previous_receipt_hash = synthetic_hash(
            "synthetic-receipt:" + previous_receipt,
        )
        prior_receipt, prior_report = synthetic_candidate_documents(
            selected,
            matrix,
            reference,
            17,
            previous_report,
            previous_report_hash,
            previous_receipt,
            label=previous_label,
        )
        documents[(
            previous_receipt,
            previous_receipt_hash,
            "receipt",
        )] = prior_receipt
        documents[(
            previous_report,
            previous_report_hash,
            "candidate",
        )] = prior_report
        selected["superseded"].append({
            "report": report_pin(
                previous_report,
                previous_report_hash,
            ),
            "receipt": report_pin(
                previous_receipt,
                previous_receipt_hash,
            ),
        })
        observations["historical_c_receipt"] = prior_receipt
        observations["historical_c_report"] = prior_report

    def loader(
        relative: str,
        expected: str,
        kind: str,
        original_hash: str | None,
        original_bytes: int | None,
        archive_bytes: int | None,
    ) -> dict[str, Any]:
        key = (relative, expected, kind)
        require(
            key in documents,
            "a fixture attempted a genuine file or concealed signed evidence",
        )
        document = documents[key]
        if kind == "receipt":
            require(
                original_hash is original_bytes is archive_bytes is None,
                "a solely in-memory receipt concealed an archive",
            )
        else:
            counterpart = next(
                (
                    receipt
                    for (path, _, selected_kind), receipt
                    in documents.items()
                    if selected_kind == "receipt"
                    and receipt.get("report_relative") == relative
                    and receipt.get("report_sha256") == expected
                ),
                None,
            )
            require(
                type(counterpart) is dict
                and original_hash
                == counterpart["report_uncompressed_sha256"]
                and original_bytes
                == counterpart["report_uncompressed_bytes"]
                and archive_bytes == counterpart["report_bytes"],
                "a full solely in-memory archive lost a signed bound",
            )
        return document

    manifest = {
        "schema": SCHEMA + "-inputs",
        "python": "3.14.6",
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_source_sha256": RECORDER_SHA256,
        "previous_recorder_source_sha256": (
            PREVIOUS_RECORDER_SHA256
        ),
        "historical_v1": historical_v1_manifest(),
        "preserved_previous_failure": report_pin(
            PRESERVED_PREVIOUS_FAILURE_RELATIVE,
            PRESERVED_PREVIOUS_FAILURE_SHA256,
        ),
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_sha256": V5_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "baseline": {
            "label": BASELINE_LABEL,
            "archive": report_pin(
                BASELINE_ARCHIVE_RELATIVE,
                BASELINE_ARCHIVE_SHA256,
            ),
            "receipt": report_pin(
                BASELINE_RECEIPT_RELATIVE,
                BASELINE_RECEIPT_SHA256,
            ),
            "records_sha256": BASELINE_RECORDS_SHA256,
        },
        "families": selections,
    }
    return manifest, loader, validators, observations

def self_test() -> dict[str, Any]:
    """Run complete 5,120-case controls without real files or processes."""
    verify_runtime()
    counters = {
        "positive_controls": 0,
        "negative_controls": 0,
        "full_vector_cases_checked": 0,
        "paired_publication_controls": 0,
        "compressed_stream_controls": 0,
    }

    def positive(condition: Any, message: str) -> None:
        require(condition, message)
        counters["positive_controls"] += 1

    def rejected(
        action: Callable[[], Any],
        message: str,
    ) -> None:
        try:
            action()
        except (
            OverviewError,
            SourceOnlyError,
            OSError,
            TypeError,
            ValueError,
            KeyError,
            IndexError,
            OverflowError,
            UnicodeError,
            RecursionError,
            binascii.Error,
            zlib.error,
        ):
            counters["negative_controls"] += 1
            return
        raise OverviewError(message)

    with SourceOnlyBoundary() as boundary:
        frozen_bounds()

        def deny_synthetic_matcher(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            boundary.blocked["matchers"] += 1
            raise SourceOnlyError("source-only graphs cannot call a matcher")

        baseline_manifest, baseline_loader, baseline_validators, (
            baseline_proof
        ) = synthetic_fixture(
            rust_state="NOT MEASURED",
            c_state="NOT MEASURED",
            zig_state="NOT MEASURED",
            history=False,
        )
        baseline_source = synthetic_hash("source-only-baseline-chart-v2")
        baseline_svg, baseline_summary = build_documents(
            baseline_manifest,
            baseline_source,
            digest(baseline_manifest),
            baseline_loader,
            baseline_validators,
        )
        baseline_document = decode_document(
            baseline_summary,
            "the complete corrected baseline-only synthetic chart",
            MAX_SOURCE_BYTES,
        )
        positive(
            [
                (
                    row["family"], row["passed"], row["failed"],
                    row["not_measured"],
                )
                for row in baseline_document["families"]
            ] == [
                ("python", CASE_COUNT, 0, 0),
                ("rust", 0, 0, CASE_COUNT),
                ("c", 0, 0, CASE_COUNT),
                ("zig", 0, 0, CASE_COUNT),
            ],
            "show corrected Python green and every native engine gray",
        )
        positive(
            baseline_document["overall"] == {
                "observed_candidate_families": 0,
                "candidate_case_denominator": 0,
                "candidate_checks_matching_python": 0,
                "candidate_checks_failing_python": 0,
                "unmeasured_candidate_families": 3,
            },
            "do not invent any corrected candidate or performance result",
        )
        positive(
            baseline_document["historical_v1"]
            == historical_v1_manifest()
            and baseline_document["historical_v1"]["status"]
            == "FALSIFIED"
            and baseline_document["historical_v1"][
                "reported_failure_counts"
            ] == {"c": 464, "zig": 192}
            and baseline_document["historical_v1"][
                "oracle_artifact_counts"
            ] == {"c": 128, "zig": 128}
            and baseline_document["historical_v1"][
                "genuine_remaining_difference_counts"
            ] == {"c": 336, "zig": 64},
            "retain all falsified V1 evidence outside corrected results",
        )
        positive(
            baseline_svg.count(b"NOT MEASURED") >= 3
            and b"5,120 / 5,120 match Python" in baseline_svg
            and b"7 fail" not in baseline_svg
            and b"5 fail" not in baseline_svg
            and b"#15803d" in baseline_svg
            and b"#94a3b8" in baseline_svg,
            "draw one real green reference and three truthful gray rows",
        )
        positive(
            baseline_proof["baseline_receipt"][
                "oracle_source_sha256"
            ] == ORACLE_SHA256
            and baseline_proof["baseline_receipt"][
                "recorder_source_sha256"
            ] == RECORDER_SHA256
            and baseline_proof["baseline_receipt"][
                "baseline_records_sha256"
            ] == BASELINE_RECORDS_SHA256,
            "validate only the corrected complete two-reference vector",
        )
        counters["full_vector_cases_checked"] += 2 * CASE_COUNT
        manifest, loader, validators, proof = synthetic_fixture()
        source = synthetic_hash("source-only-substitution-chart-v2")
        manifest_hash = digest(manifest)
        svg, summary = build_documents(
            manifest,
            source,
            manifest_hash,
            loader,
            validators,
        )
        document = decode_document(
            summary,
            "the complete solely in-memory chart",
            MAX_SOURCE_BYTES,
        )
        positive(
            [row["family"] for row in document["families"]]
            == ["python", "rust", "c", "zig"],
            "show all four independent implementations",
        )
        positive(
            [
                (row["passed"], row["failed"], row["not_measured"])
                for row in document["families"]
            ]
            == [
                (5_120, 0, 0),
                (0, 0, 5_120),
                (5_113, 7, 0),
                (5_115, 5, 0),
            ],
            "retain future independently observed corrected failures",
        )
        positive(
            document["overall"]
            == {
                "observed_candidate_families": 2,
                "candidate_case_denominator": 10_240,
                "candidate_checks_matching_python": 10_228,
                "candidate_checks_failing_python": 12,
                "unmeasured_candidate_families": 1,
            },
            "report the complete honest candidate-versus-Python overview",
        )
        positive(
            document["published_seed"]
            == 6_004_778_603_531_028_017
            and document["published_seed_decimal"]
            == "6004778603531028017",
            "the full 64-bit original matrix seed must never be rounded",
        )
        positive(
            document["preserved_previous_failure"][
                "reference_worker_count"
            ]
            == "UNKNOWN"
            and document["preserved_previous_failure"][
                "reported_reference_worker_count_is_reliable"
            ]
            is False,
            "the original V1 reference count remains honestly unknown",
        )
        positive(
            len(document["families"][2]["superseded"]) == 1
            and document["families"][2]["superseded"][0][
                "failed"
            ]
            == 17
            and document["families"][2]["superseded"][0][
                "candidate_result_status"
            ]
            == "FAIL",
            "preserve a genuine real-shaped earlier candidate failure",
        )
        positive(
            document["families"][2]["publication_status"] == "PASS"
            and document["families"][2]["candidate_result_status"]
            == "FAIL"
            and document["families"][3]["publication_status"] == "PASS"
            and document["families"][3]["candidate_result_status"]
            == "FAIL",
            "a published candidate report must not be called a passing engine",
        )
        positive(
            b"5,113 match" in svg
            and b"7 fail" in svg
            and b"5,115 match" in svg
            and b"5 fail" in svg
            and b"NOT MEASURED" in svg
            and b"speed not yet measured" in svg
            and b"#dc2626" in svg
            and b"#94a3b8" in svg,
            "make the actual outcomes understandable in the generated SVG",
        )
        positive(
            set(document) == SUMMARY_FIELDS
            and document["performance"] == "NOT MEASURED"
            and document["final_holdout_opened"] is False
            and document["winner_selected"] is False,
            "never infer speed, inspect the holdout, or choose a winner",
        )
        counters["full_vector_cases_checked"] += (
            4 * CASE_COUNT
        )

        for field in sorted(MANIFEST_FIELDS):
            broken = dict(manifest)
            broken.pop(field)
            rejected(
                lambda broken=broken: manifest_rows(
                    broken,
                    loader,
                    validators,
                ),
                "reject every missing immutable manifest field",
            )
        for field, incorrect in (
            ("schema", SCHEMA + "-fake"),
            ("python", "3.13.0"),
            ("case_denominator", CASE_COUNT - 1),
            ("cohort_count", 63),
            ("variants_per_cohort", 79),
            ("oracle_source_sha256", synthetic_hash("wrong-oracle")),
            ("recorder_source_sha256", synthetic_hash("wrong-recorder")),
            (
                "previous_recorder_source_sha256",
                synthetic_hash("wrong-previous-recorder"),
            ),
            ("ownership_audit_sha256", synthetic_hash("wrong-audit")),
            ("original_v5_sha256", synthetic_hash("wrong-v5")),
            (
                "pinned_python_sha256",
                synthetic_hash("wrong-original-python"),
            ),
            ("matrix_sha256", synthetic_hash("wrong-matrix")),
            ("published_seed", PUBLISHED_SEED - 1),
        ):
            broken = {**manifest, field: incorrect}
            rejected(
                lambda broken=broken: manifest_rows(
                    broken,
                    loader,
                    validators,
                ),
                "reject a forged frozen matrix, full seed, or source",
            )
        for field in sorted(BASELINE_RECEIPT_FIELDS):
            broken = dict(proof["baseline_receipt"])
            broken.pop(field)
            rejected(
                lambda broken=broken: validators.validate_baseline(
                    broken,
                    proof["baseline_report"],
                    {"family": "c", "baseline": BASELINE_RECORDS_SHA256},
                ),
                "reject every missing actual baseline receipt field",
            )
        for field in sorted(BASELINE_FIELDS):
            broken = dict(proof["baseline_report"])
            broken.pop(field)
            rejected(
                lambda broken=broken: validators.validate_baseline(
                    proof["baseline_receipt"],
                    broken,
                    {"family": "c", "baseline": BASELINE_RECORDS_SHA256},
                ),
                "reject every missing complete baseline report field",
            )
        for family in ("c", "zig"):
            index = 1 if family == "c" else 2
            entry = manifest["families"][index]
            receipt = proof["candidate_receipts"][family]
            report = proof["candidate_reports"][family]
            actual_entry = {
                **entry,
                "_report_relative": entry["report"]["relative"],
                "_report_sha256": entry["report"]["sha256"],
                "_receipt_relative": entry["receipt"]["relative"],
            }
            baseline = {
                **proof["baseline_report"],
                "reference_a_records": proof["reference"],
                "reference_b_records": proof["reference"],
            }
            for field in sorted(CANDIDATE_RECEIPT_FIELDS):
                broken = dict(receipt)
                broken.pop(field)
                rejected(
                    lambda broken=broken: (
                        validators.validate_candidate(
                            family,
                            actual_entry,
                            broken,
                            report,
                            baseline,
                        )
                    ),
                    "reject every missing complete " + family + " receipt",
                )
            for field in sorted(CANDIDATE_FIELDS):
                broken = dict(report)
                broken.pop(field)
                rejected(
                    lambda broken=broken: (
                        validators.validate_candidate(
                            family,
                            actual_entry,
                            receipt,
                            broken,
                            baseline,
                        )
                    ),
                    "reject every missing complete " + family + " report",
                )
            for field, incorrect in (
                ("candidate_result_status", "PASS"),
                ("status", "FAIL"),
                ("mismatch_count", 0),
                ("validated_prior_reference_workers", 0),
                ("actual_reference_workers", 2),
                ("actual_candidate_workers", 0),
                ("actual_method_guard_checks", 0),
                ("actual_warning_registry_guard_checks", 0),
                ("all_mismatches_preserved", False),
                (
                    "mismatch_evidence_sha256",
                    synthetic_hash("hidden-" + family + "-mismatches"),
                ),
            ):
                broken_receipt = {**receipt, field: incorrect}
                rejected(
                    lambda broken_receipt=broken_receipt: (
                        validators.validate_candidate(
                            family,
                            actual_entry,
                            broken_receipt,
                            report,
                            baseline,
                        )
                    ),
                    "reject publication-as-pass and hidden " + family + " losses",
                )
            for field, incorrect in (
                ("status", "PASS"),
                ("mismatch_count", 0),
                ("validated_prior_reference_workers", 0),
                ("actual_reference_workers", 2),
                ("actual_candidate_workers", 0),
                ("actual_method_guard_checks", 0),
                ("actual_warning_registry_guard_checks", 0),
                ("all_mismatches_preserved", False),
                (
                    "mismatch_evidence_sha256",
                    synthetic_hash("swapped-" + family + "-ledger"),
                ),
                ("all_mismatches", []),
                ("actual_candidate_process_returncode", 1),
            ):
                broken_report = {**report, field: incorrect}
                rejected(
                    lambda broken_report=broken_report: (
                        validators.validate_candidate(
                            family,
                            actual_entry,
                            receipt,
                            broken_report,
                            baseline,
                        )
                    ),
                    "reject a concealed " + family + " failure or worker",
                )
        for family in FAMILY_ORDER:
            index = FAMILY_ORDER.index(family)
            selected = manifest["families"][index]
            _, _, _, owned = FAMILY_SPECS[family]
            for relative in owned:
                broken_sources = dict(selected["owned_source_sha256"])
                broken_sources.pop(relative)
                broken_selected = {
                    **selected,
                    "owned_source_sha256": broken_sources,
                }
                rejected(
                    lambda broken_selected=broken_selected: (
                        validators.authenticate_family(
                            family,
                            broken_selected,
                        )
                    ),
                    "reject an omitted owned " + family + " source",
                )
            if family != "c":
                broken_selected = {
                    **selected,
                    "native_bridge_sha256": selected[
                        "native_engine_sha256"
                    ],
                }
                rejected(
                    lambda broken_selected=broken_selected: (
                        validators.authenticate_family(
                            family,
                            broken_selected,
                        )
                    ),
                    "reject cross-family engine and bridge aliasing",
                )
        for bad in (
            {},
            {
                "relative": "../hidden.json",
                "sha256": synthetic_hash("escape"),
            },
            {
                "relative": EVIDENCE_DIRECTORY + "/forged.json",
                "sha256": "0" * 64,
            },
            {
                "relative": EVIDENCE_DIRECTORY + "/forged.json",
                "sha256": synthetic_hash("pin"),
                "hidden": True,
            },
        ):
            rejected(
                lambda bad=bad: evidence_pin(bad, set()),
                "reject hidden, invented, or escaping evidence",
            )
        repeated: set[str] = set()
        evidence_pin(manifest["baseline"]["archive"], repeated)
        rejected(
            lambda: evidence_pin(
                manifest["baseline"]["archive"],
                repeated,
            ),
            "reject a duplicate report or denominator",
        )

        raw = canonical({
            "proof": "complete replacement-and-buffer member",
            "value": [
                {
                    "family": "c",
                    "denominator": CASE_COUNT,
                    "failed": 7,
                },
                {
                    "family": "zig",
                    "denominator": CASE_COUNT,
                    "failed": 5,
                },
            ],
        })
        restored = synthetic_stream(raw)
        positive(
            restored
            == decode_document(raw, "the solely in-memory gzip control"),
            "restore one complete bounded canonical V2 gzip member",
        )
        counters["compressed_stream_controls"] += 1
        compressor = zlib.compressobj(
            level=9,
            wbits=16 + zlib.MAX_WBITS,
        )
        archive = compressor.compress(raw) + compressor.flush()
        for kwargs in (
            {"archive": archive[:-1]},
            {"archive": archive + b"hidden"},
            {"archive": archive + archive},
            {"archive_hash": synthetic_hash("wrong-archive")},
            {"original_hash": synthetic_hash("wrong-original")},
            {"original_bytes": len(raw) - 1},
            {"original_bytes": len(raw) + 1},
        ):
            rejected(
                lambda kwargs=kwargs: synthetic_stream(
                    raw,
                    **kwargs,
                ),
                "reject truncated, concatenated, forged, or overexpanded gzip",
            )
            counters["compressed_stream_controls"] += 1
        for archive_size, original_size in (
            (MAX_ARCHIVE_BYTES + 1, 1),
            (1, MAX_UNCOMPRESSED_BYTES + 1),
            (0, 1),
            (1, 0),
        ):
            rejected(
                lambda archive_size=archive_size,
                original_size=original_size: VerifiedGzipReader(
                    -1,
                    archive_size,
                    synthetic_hash("bounded-gzip"),
                    original_size,
                    synthetic_hash("bounded-original"),
                ),
                "reject compression beyond the exact 384/320 MiB bounds",
            )
            counters["compressed_stream_controls"] += 1
        valid_edge = VerifiedGzipReader(
            -1,
            MAX_ARCHIVE_BYTES,
            synthetic_hash("exact-archive-limit"),
            MAX_UNCOMPRESSED_BYTES,
            synthetic_hash("exact-uncompressed-limit"),
        )
        positive(
            valid_edge.archive_bytes == 384 * 1024 * 1024
            and valid_edge.original_bytes == 320 * 1024 * 1024,
            "accept both exact prospective V2 compression ceilings",
        )
        counters["compressed_stream_controls"] += 1
        for corrupt in (
            b'{"proof":"x","proof":"hidden","value":[]}\n',
            b'{"proof":"x","value":[],"hidden":true}\n',
            b'{"proof":"x"}\n',
            b'{"proof":"x","value":[]} trailing\n',
            b'{"proof":"x","value":[NaN]}\n',
        ):
            rejected(
                lambda corrupt=corrupt: synthetic_stream(corrupt),
                "reject concealed duplicate, injected, or nonfinite JSON",
            )
            counters["compressed_stream_controls"] += 1

        fresh = SyntheticPublication(None, None)
        atomic_publish_pair(
            fresh.directory,
            (7, 7_001),
            None,
            None,
            svg,
            summary,
            fresh,
        )
        positive(
            fresh.pair() == (svg, summary)
            and fresh.only_outputs_remain(),
            "publish both fresh outputs atomically in memory",
        )
        counters["paired_publication_controls"] += 1
        previous_svg, previous_summary = svg, summary
        replacement_source = source
        replacement_hash = synthetic_hash(
            "second-frozen-synthetic-manifest",
        )
        updated_svg, updated_summary = build_documents(
            manifest,
            replacement_source,
            replacement_hash,
            loader,
            validators,
        )
        positive(
            validate_previous_outputs(
                previous_svg,
                previous_summary,
                hashlib.sha256(previous_svg).hexdigest(),
                hashlib.sha256(previous_summary).hexdigest(),
                replacement_source,
            )["source_sha256"] == replacement_source,
            "authenticate both complete prior chart hashes and history",
        )
        replacement = SyntheticPublication(
            previous_svg,
            previous_summary,
        )
        atomic_publish_pair(
            replacement.directory,
            (7, 7_001),
            previous_svg,
            previous_summary,
            updated_svg,
            updated_summary,
            replacement,
        )
        positive(
            replacement.pair() == (updated_svg, updated_summary)
            and replacement.only_outputs_remain(),
            "replace both exactly authenticated outputs together",
        )
        counters["paired_publication_controls"] += 1
        for failed_link in (1, 2):
            attempted = SyntheticPublication(
                None,
                None,
                fail_link=failed_link,
            )
            rejected(
                lambda attempted=attempted: atomic_publish_pair(
                    attempted.directory,
                    (7, 7_001),
                    None,
                    None,
                    svg,
                    summary,
                    attempted,
                ),
                "roll back every failed fresh two-file commit",
            )
            positive(
                attempted.pair() == (None, None)
                and attempted.only_outputs_remain(),
                "a failed fresh pair must leave no output or stage",
            )
            counters["paired_publication_controls"] += 1
        for failed_replace in (1, 2):
            attempted = SyntheticPublication(
                previous_svg,
                previous_summary,
                fail_replace=failed_replace,
            )
            rejected(
                lambda attempted=attempted: atomic_publish_pair(
                    attempted.directory,
                    (7, 7_001),
                    previous_svg,
                    previous_summary,
                    updated_svg,
                    updated_summary,
                    attempted,
                ),
                "restore both exact prior files after failed replacement",
            )
            positive(
                attempted.pair() == (previous_svg, previous_summary)
                and attempted.only_outputs_remain(),
                "a failed replacement must restore the complete old pair",
            )
            counters["paired_publication_controls"] += 1
        staged = SyntheticPublication(
            previous_svg,
            previous_summary,
            fail_stage_write=True,
        )
        rejected(
            lambda: atomic_publish_pair(
                staged.directory,
                (7, 7_001),
                previous_svg,
                previous_summary,
                updated_svg,
                updated_summary,
                staged,
            ),
            "restore the exact pair after an interrupted stage write",
        )
        positive(
            staged.pair() == (previous_svg, previous_summary)
            and staged.only_outputs_remain(),
            "a staged write failure must preserve both previous outputs",
        )
        counters["paired_publication_controls"] += 1
        for bad_svg, bad_summary, pin_svg, pin_summary in (
            (
                previous_svg,
                None,
                hashlib.sha256(previous_svg).hexdigest(),
                hashlib.sha256(previous_summary).hexdigest(),
            ),
            (
                None,
                previous_summary,
                hashlib.sha256(previous_svg).hexdigest(),
                hashlib.sha256(previous_summary).hexdigest(),
            ),
            (
                previous_svg,
                previous_summary,
                synthetic_hash("wrong-prior-svg"),
                hashlib.sha256(previous_summary).hexdigest(),
            ),
            (
                previous_svg,
                previous_summary,
                hashlib.sha256(previous_svg).hexdigest(),
                synthetic_hash("wrong-prior-summary"),
            ),
        ):
            rejected(
                lambda bad_svg=bad_svg,
                bad_summary=bad_summary,
                pin_svg=pin_svg,
                pin_summary=pin_summary: validate_previous_outputs(
                    bad_svg,
                    bad_summary,
                    pin_svg,
                    pin_summary,
                    source,
                ),
                "reject a partial, substituted, or incorrectly pinned pair",
            )
            counters["paired_publication_controls"] += 1
        rejected(
            lambda: approve_publication(
                previous_svg,
                previous_summary,
                updated_svg,
                updated_summary,
                False,
                None,
                None,
                source,
            ),
            "never overwrite a graph without explicit complete prior pins",
        )
        counters["paired_publication_controls"] += 1
        for identity in ((7, 7_002), (8, 7_001)):
            rejected(
                lambda identity=identity: atomic_publish_pair(
                    fresh.directory,
                    identity,
                    svg,
                    summary,
                    updated_svg,
                    updated_summary,
                    fresh,
                ),
                "reject a substituted graph directory identity",
            )
            counters["paired_publication_controls"] += 1

        full_manifest, full_loader, full_validators, _ = (
            synthetic_fixture(
                c_failures=0,
                zig_failures=0,
                rust_state="RUN",
                rust_failures=0,
                history=False,
            )
        )
        _, passing_summary = build_documents(
            full_manifest,
            source,
            digest(full_manifest),
            full_loader,
            full_validators,
        )
        passing = decode_document(
            passing_summary,
            "the complete all-family synthetic pass controls",
            MAX_SOURCE_BYTES,
        )
        positive(
            all(
                row["passed"] == CASE_COUNT
                and row["failed"] == 0
                and row["not_measured"] == 0
                and row["candidate_result_status"] == "PASS"
                for row in passing["families"]
            )
            and passing["overall"]
            == {
                "observed_candidate_families": 3,
                "candidate_case_denominator": 3 * CASE_COUNT,
                "candidate_checks_matching_python": 3 * CASE_COUNT,
                "candidate_checks_failing_python": 0,
                "unmeasured_candidate_families": 0,
            },
            "accept three independently owned complete passing families",
        )
        counters["full_vector_cases_checked"] += 4 * CASE_COUNT
        for omitted in range(CASE_COUNT):
            if omitted in (0, 1, 6, 7, 79, 80, 5_118, 5_119):
                altered = proof["reference"][:omitted] + (
                    proof["reference"][omitted + 1:]
                )
                rejected(
                    lambda altered=altered: synthetic_compare(
                        proof["matrix"],
                        proof["reference"],
                        altered,
                    ),
                    "reject a missing original, boundary, or final outcome",
                )
        swapped = list(proof["reference"])
        swapped[0], swapped[1] = swapped[1], swapped[0]
        rejected(
            lambda: synthetic_compare(
                proof["matrix"],
                proof["reference"],
                swapped,
            ),
            "reject reordered source or candidate outcomes",
        )

        boundary_checks: tuple[
            tuple[str, Callable[[], Any]],
            ...,
        ] = (
            (
                "reads",
                lambda: builtins.open(
                    "/unreachable-source-only-substitution",
                    "rb",
                ),
            ),
            (
                "writes",
                lambda: builtins.open(
                    "/unreachable-source-only-substitution",
                    "wb",
                ),
            ),
            (
                "workers",
                lambda: subprocess.run(
                    ["source-only-worker-must-never-start"],
                    check=False,
                ),
            ),
            (
                "imports",
                lambda: importlib.import_module(
                    "source_only_import_must_never_run",
                ),
            ),
            (
                "imports",
                lambda: builtins.__import__(
                    "source_only_import_must_never_run",
                ),
            ),
            (
                "matchers",
                lambda: deny_synthetic_matcher("synthetic"),
            ),
            (
                "threads",
                lambda: threading.Thread(target=lambda: None).start(),
            ),
            ("clocks", lambda: time.perf_counter_ns()),
            ("clocks", lambda: time.time_ns()),
            ("garbage_collections", lambda: gc.collect()),
            ("randomness", lambda: os.urandom(1)),
        )
        for category, action in boundary_checks:
            previous = boundary.blocked[category]
            rejected(
                action,
                "deny every genuine external source-only effect",
            )
            positive(
                boundary.blocked[category] == previous + 1,
                "count each genuinely denied source-only boundary",
            )
        positive(
            all(
                boundary.blocked[category] > 0
                for category in (
                    "reads",
                    "writes",
                    "workers",
                    "imports",
                    "matchers",
                    "threads",
                    "clocks",
                    "garbage_collections",
                    "randomness",
                )
            ),
            "actively prove every file, worker, clock, and import is denied",
        )
        blocked = dict(boundary.blocked)

    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "matrix_sha256": MATRIX_SHA256,
        "baseline_reference_pids": [82, 83],
        "expected_rows": [
            {
                "family": "python",
                "passed": CASE_COUNT,
                "failed": 0,
                "not_measured": 0,
            },
            {
                "family": "rust",
                "passed": 0,
                "failed": 0,
                "not_measured": CASE_COUNT,
            },
            {
                "family": "c",
                "passed": 0,
                "failed": 0,
                "not_measured": CASE_COUNT,
            },
            {
                "family": "zig",
                "passed": 0,
                "failed": 0,
                "not_measured": CASE_COUNT,
            },
        ],
        "expected_observed_candidate_checks": 0,
        "expected_observed_candidate_matches": 0,
        "expected_observed_candidate_failures": 0,
        "historical_v1": historical_v1_manifest(),
        "actual_matcher_invocations": 0,
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "preserved_previous_reference_worker_count": "UNKNOWN",
        "positive_controls": counters["positive_controls"],
        "negative_controls": counters["negative_controls"],
        "full_vector_cases_checked": (
            counters["full_vector_cases_checked"]
        ),
        "paired_publication_controls": (
            counters["paired_publication_controls"]
        ),
        "compressed_stream_controls": (
            counters["compressed_stream_controls"]
        ),
        "source_only_boundary": blocked,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render only the independently frozen 5,120-case Python "
            "replacement-and-buffer correctness comparison"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--self-test",
        action="store_true",
        help="run solely in-memory complete hostile source controls",
    )
    modes.add_argument(
        "--render",
        action="store_true",
        help="render only the exact externally frozen inputs manifest",
    )
    parser.add_argument("--source-sha256")
    parser.add_argument("--manifest")
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--replace-generated", action="store_true")
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--previous-summary-sha256")
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            require(
                all(
                    getattr(options, field) is None
                    for field in (
                        "source_sha256",
                        "manifest",
                        "manifest_sha256",
                        "previous_svg_sha256",
                        "previous_summary_sha256",
                    )
                )
                and options.replace_generated is False,
                "source-only tests cannot authorize reads or publication",
            )
            result = self_test()
        else:
            require(
                options.render is True,
                "explicitly select the frozen 5,120-case comparison",
            )
            result = render(
                options.source_sha256,
                options.manifest,
                options.manifest_sha256,
                replace=options.replace_generated,
                previous_svg=options.previous_svg_sha256,
                previous_summary=options.previous_summary_sha256,
            )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (
        OverviewError,
        OSError,
        TypeError,
        ValueError,
        KeyError,
        IndexError,
        OverflowError,
        UnicodeError,
        RecursionError,
        binascii.Error,
        zlib.error,
    ) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "actual_reference_workers": 0,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_opened": False,
            "winner_selected": False,
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
