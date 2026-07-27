#!/usr/bin/env python3
"""Render only the separately frozen 2,854-case Python Scanner comparison.

The graph is made entirely from source-pinned, lossless correctness reports.
Its source-only self-test is synthetic: it cannot read or write a file, import
an implementation, start a worker, inspect a benchmark, or sample a clock.
An actual graph requires an explicitly pinned manifest. Existing graph bytes
can change only with an explicit, authenticated two-file refresh.
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
SOURCE_RELATIVE = "tools/render_scanner_verbose_overview_v1.py"
SCHEMA = "rebar-scanner-verbose-overview-v1"
MANIFEST_RELATIVE = "docs/evidence/scanner-verbose-overview-v1.inputs.json"
SVG_RELATIVE = "docs/evidence/scanner-verbose-overview-v1.svg"
SUMMARY_RELATIVE = "docs/evidence/scanner-verbose-overview-v1.json"
EVIDENCE_DIRECTORY = "experiments/rust_public_practice_v1"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
ORACLE_RELATIVE = "tools/independent_scanner_verbose_comments_v1.py"
ORACLE_SHA256 = (
    "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d"
)
ORACLE_SCHEMA = "rebar-independent-scanner-verbose-comments-v1"
RECORDER_RELATIVE = "tools/record_independent_scanner_verbose_comments_v1.py"
RECORDER_SHA256 = (
    "d75934bef992e01ad5c1131a8abef997d3b540f8b150518822ad7e55c39c9191"
)
RECORDER_SCHEMA = "rebar-independent-scanner-verbose-comments-recorder-v1"
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
V2_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
V2_SHA256 = (
    "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
)
MATRIX_SHA256 = (
    "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b"
)
PUBLISHED_SEED = 0x5343_4E56_4552_5631
CASE_COUNT = 2_854
SEMANTIC_CASE_COUNT = 2_560
TOKENIZER_CASE_COUNT = 294
VERBOSE = 64
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 96 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_SELECTED_VALUE_BYTES = 96 * 1024 * 1024
CHUNK_BYTES = 131_072
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
FAMILY_ORDER = ("rust", "c", "zig")
FAMILY_LABELS = {"rust": "Rust", "c": "C", "zig": "Zig"}
FAMILY_SPECS: dict[str, tuple[str, str, str, tuple[str, ...], bool]] = {
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
        False,
    ),
    "c": (
        "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
        False,
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
        True,
    ),
}
EXPECTED_COUNTS = {
    "full-match": 2_612,
    "continued-comment-empty": 32,
    "prefix-then-fallback": 108,
    "continued-comment-unterminated": 102,
}
EXPECTED_NEGATIVE_COUNTS = {"semantic": 48, "tokenizer": 54}
COMMENT_PAYLOADS = (
    "(((", "(?P<phantom>q)", "\\8", "(?(99)a|b)", "(?P=missing)",
    "(?x:", "(?-x:", "[unclosed(", ") ((( ???", "\\",
    "# another comment", "(?<=(", "(?<!(", "(?>(",
    "(?P<_phantom>(", "(?#not-really",
)
SEMANTIC_TAILS = (
    ("literal", "a", "a"),
    ("plain_capture", "(a)", "a"),
    ("named_capture", "(?P<real>a)", "a"),
    ("conditional_yes", "(a)?(?(1)b|c)", "ab"),
    ("conditional_no", "(a)?(?(1)b|c)", "c"),
    ("numeric_backreference", "(a)\\1", "aa"),
    ("named_backreference", "(?P<real>a)(?P=real)", "aa"),
    ("inner_verbose_scope", "(?x:a b)", "ab"),
)
SEMANTIC_ENDINGS = (("lf", "\n"), ("crlf", "\r\n"))
SEMANTIC_CONTEXTS = (
    "root_verbose", "global_verbose", "scoped_verbose",
    "nested_enable", "nested_disable",
)
TOKENIZER_ENDINGS = (
    ("none", ""), ("lf", "\n"), ("cr", "\r"), ("crlf", "\r\n"),
    ("lfcr", "\n\r"), ("double_lf", "\n\n"), ("latin1_nel", "\x85"),
)
TOKENIZER_CONTEXTS = ("root", "global", "scoped")
TRUSTED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
GUARD_TRUE = (
    "original_matchers_blocked",
    "adapter_import_quarantined",
    "native_sre_blocked",
    "builtins_import_guarded",
    "importlib_import_guarded",
    "actual_object_identity_guarded",
    "warning_registry_introspection_safe",
    "warning_registry_exactly_absent",
    "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
GUARD_COUNTERS = (
    "cached_original_matcher_descendant_count",
    "cached_original_holder_count",
    "owned_ctypes_load_count",
    "owned_ctypes_symbol_count",
)
PINNED_STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
PINNED_STDLIB_SOURCES = {
    "re": (
        "__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    ),
    "re._compiler": (
        "_compiler.py",
        "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91",
    ),
    "re._parser": (
        "_parser.py",
        "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4",
    ),
    "re._constants": (
        "_constants.py",
        "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b",
    ),
}
FORBIDDEN_ROOTS = frozenset({
    "candidates", "_regex", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})
COMMON_SOURCE_FIELDS = frozenset({
    "python", "label", "recorder_relative", "recorder_source_sha256",
    "oracle_relative", "oracle_source_sha256", "original_v5_relative",
    "original_v5_sha256", "ownership_audit_relative",
    "ownership_audit_sha256", "matrix_sha256", "published_seed",
    "case_count", "semantic_case_count", "tokenizer_case_count",
    "expected_kind_counts", "expected_pattern_error_counts",
})
BASELINE_FIELDS = COMMON_SOURCE_FIELDS | frozenset({
    "schema", "status", "source_closure_before", "source_closure_after",
    "source_closure_unchanged", "complete_baseline_process_stdout",
    "complete_baseline_process_stderr", "complete_decoded_baseline_process",
    "complete_baseline_result", "complete_structured_baseline_failure",
    "complete_reference_worker_failure", "validated_reference_a_case_count",
    "validated_reference_b_case_count", "baseline_records_sha256",
    "baseline_reference_pids", "reference_a_records", "reference_b_records",
    "reference_a_process", "reference_b_process", "actual_reference_workers",
    "actual_candidate_workers", "actual_candidate_imports",
    "actual_baseline_controller_invocations", "actual_baseline_controller_pid",
    "actual_baseline_process_returncode", "actual_baseline_process_signal",
    "actual_baseline_process_timed_out", "actual_baseline_process_spawn_error",
    "all_failure_reasons", "failure_count", "clock_samples",
    "timing_trials_run", "benchmark_files_read", "hidden_cases_read",
    "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})
BASELINE_RECEIPT_FIELDS = COMMON_SOURCE_FIELDS | frozenset({
    "schema", "status", "baseline_result_status", "baseline_records_sha256",
    "validated_reference_a_case_count", "validated_reference_b_case_count",
    "baseline_reference_pids", "actual_reference_workers",
    "actual_candidate_workers", "actual_candidate_imports",
    "actual_baseline_controller_invocations", "source_closure_before",
    "source_closure_after", "source_closure_unchanged", "report_relative",
    "report_sha256", "report_bytes", "report_uncompressed_sha256",
    "report_uncompressed_bytes", "report_compression",
    "report_file_fsync_completed", "report_directory_fsync_completed",
    "report_atomic_no_overwrite_link", "report_complete_readback_verified",
    "receipt_relative", "approved_fresh_path_count",
    "fresh_paths_checked_before_baseline", "clock_samples",
    "timing_trials_run", "benchmark_files_read", "hidden_cases_read",
    "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})
CANDIDATE_FIELDS = frozenset({
    "schema", "status", "python", "label", "candidate_family",
    "candidate_source_sha256", "native_engine_sha256", "native_bridge_sha256",
    "baseline_label", "recorder_relative", "recorder_source_sha256",
    "oracle_relative", "oracle_source_sha256", "original_v5_relative",
    "original_v5_sha256", "ownership_audit_relative",
    "ownership_audit_sha256", "matrix_sha256", "published_seed",
    "case_count", "semantic_case_count", "tokenizer_case_count",
    "expected_kind_counts", "expected_pattern_error_counts",
    "baseline_receipt_relative", "baseline_receipt_sha256",
    "baseline_archive_relative", "baseline_archive_sha256",
    "baseline_records_sha256", "baseline_reference_pids",
    "candidate_owner_before", "candidate_owner_after",
    "candidate_owner_unchanged", "complete_candidate_process_stdout",
    "complete_candidate_process_stderr", "complete_decoded_candidate_process",
    "complete_candidate_result", "validated_baseline_record_count",
    "validated_candidate_record_count", "candidate_records_sha256",
    "baseline_records", "candidate_records", "mismatch_count",
    "all_mismatches", "mismatches_by_expected_kind", "mismatches_by_cohort",
    "all_mismatches_preserved", "matcher_guard",
    "actual_method_guard_checks", "actual_warning_registry_guard_checks",
    "validated_prior_reference_workers", "actual_reference_workers",
    "actual_candidate_workers", "actual_candidate_imports",
    "actual_candidate_process_invocations", "actual_candidate_pid",
    "actual_candidate_process_returncode", "actual_candidate_process_signal",
    "actual_candidate_process_timed_out", "actual_candidate_process_spawn_error",
    "all_failure_reasons", "failure_count", "clock_samples",
    "timing_trials_run", "benchmark_files_read", "hidden_cases_read",
    "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})
CANDIDATE_RECEIPT_FIELDS = frozenset({
    "schema", "status", "candidate_result_status", "python", "label",
    "candidate_family", "candidate_source_sha256", "native_engine_sha256",
    "native_bridge_sha256", "baseline_label", "recorder_source_sha256",
    "oracle_source_sha256", "original_v5_sha256", "ownership_audit_sha256",
    "matrix_sha256", "published_seed", "case_count", "semantic_case_count",
    "tokenizer_case_count", "expected_kind_counts",
    "expected_pattern_error_counts", "baseline_receipt_relative",
    "baseline_receipt_sha256", "baseline_archive_relative",
    "baseline_archive_sha256", "baseline_records_sha256",
    "baseline_reference_pids", "validated_baseline_record_count",
    "validated_candidate_record_count", "candidate_records_sha256",
    "mismatch_count", "mismatches_by_expected_kind", "mismatches_by_cohort",
    "all_mismatches_preserved", "actual_method_guard_checks",
    "actual_warning_registry_guard_checks", "validated_prior_reference_workers",
    "actual_reference_workers", "actual_candidate_workers",
    "actual_candidate_imports", "actual_candidate_process_invocations",
    "candidate_owner_before", "candidate_owner_after",
    "candidate_owner_unchanged", "report_relative", "report_sha256",
    "report_bytes", "report_uncompressed_sha256", "report_uncompressed_bytes",
    "report_compression", "report_file_fsync_completed",
    "report_directory_fsync_completed", "report_atomic_no_overwrite_link",
    "report_complete_readback_verified", "receipt_relative",
    "approved_fresh_path_count", "fresh_paths_checked_before_candidate",
    "clock_samples", "timing_trials_run", "benchmark_files_read",
    "hidden_cases_read", "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})


class OverviewError(Exception):
    """The separately frozen Scanner graph evidence is incomplete or forged."""


class SourceOnlyError(OverviewError):
    """A synthetic-only graph check attempted an actual external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OverviewError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise OverviewError("complete canonical Scanner evidence is mandatory") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_hash(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def safe_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\\" not in value and "\x00" not in value,
            "an exact safe relative graph path is mandatory")
    parts = tuple(value.split("/"))
    require(all(part not in {"", ".", ".."} for part in parts)
            and "/".join(parts) == value,
            "the Scanner graph path escapes the approved project root")
    return parts


def validate_label(value: Any) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    require(type(value) is str and 1 <= len(value) <= 64
            and value[0] in alphabet and value[-1] in alphabet
            and all(item in alphabet + "-" for item in value)
            and "--" not in value,
            "an exact bounded scanner evidence label is mandatory")
    return value


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "a complete Scanner evidence field was duplicated")
        result[key] = value
    return result


def decode_document(
    raw: Any, label: str, maximum: int = MAX_RECEIPT_BYTES,
) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= maximum,
            "complete bounded canonical evidence is mandatory: " + label)

    def reject_constant(_: str) -> None:
        raise OverviewError("nonfinite Scanner graph evidence is forbidden")

    try:
        value = json.loads(
            raw, object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (OverviewError, TypeError, ValueError, UnicodeError) as error:
        raise OverviewError("invalid complete Scanner graph evidence: " + label) from error
    require(type(value) is dict and canonical(value) == raw,
            "Scanner evidence was truncated, noncanonical, or gained a suffix")
    return value


def fixed_fields(
    actual: Mapping[str, Any], expected: Mapping[str, Any], label: str,
) -> None:
    for name, original in expected.items():
        value = actual.get(name)
        require(type(value) is type(original) and value == original,
                label + " changed: " + name)


def encode_subject(value: str | bytes) -> dict[str, str]:
    if type(value) is str:
        return {"kind": "str", "value": value}
    require(type(value) is bytes, "an exact str or bytes Scanner carrier is required")
    return {"kind": "bytes", "hex": value.hex()}


def decode_subject(value: Any, domain: str) -> str | bytes:
    require(type(value) is dict and domain in {"str", "bytes"},
            "an exact frozen Scanner carrier is mandatory")
    if domain == "str":
        require(set(value) == {"kind", "value"}
                and value.get("kind") == "str"
                and type(value.get("value")) is str,
                "an exact Unicode Scanner carrier was substituted")
        return value["value"]
    require(set(value) == {"kind", "hex"}
            and value.get("kind") == "bytes"
            and type(value.get("hex")) is str,
            "an exact bytes Scanner carrier was substituted")
    try:
        raw = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise OverviewError("a frozen Scanner carrier is not canonical hex") from error
    require(raw.hex() == value["hex"], "a Scanner carrier is not lowercase hex")
    return raw


def semantic_contexts(
    payload: str, ending: str, tail: str, subject: str,
) -> tuple[tuple[str, str, int, str], ...]:
    return (
        ("root_verbose", "# " + payload + ending + tail, VERBOSE, subject),
        ("global_verbose", "(?x)# " + payload + ending + tail, 0, subject),
        ("scoped_verbose", "(?x:# " + payload + ending + tail + ")", 0, subject),
        (
            "nested_enable",
            "(?-x:\\#(?x:# " + payload + ending + tail + "))",
            VERBOSE,
            "#" + subject,
        ),
        (
            "nested_disable",
            "(?x:# " + payload + ending + "(?-x:\\#)(?x:" + tail + "))",
            0,
            "#" + subject,
        ),
    )


def append_case(
    rows: list[dict[str, Any]], *, domain: str, cohort: str,
    context: str, phrase: str, flags: int, subject: str,
    ending: str, tail: str | None, payload_index: int | None,
    slash_count: int | None, expected: str,
) -> None:
    require(domain in {"str", "bytes"} and expected in EXPECTED_COUNTS,
            "an unfrozen Scanner graph property was injected")
    native_phrase: str | bytes = phrase
    native_subject: str | bytes = subject
    if domain == "bytes":
        native_phrase = phrase.encode("latin1")
        native_subject = subject.encode("latin1")
    parts = [cohort, domain, context, ending]
    if payload_index is not None:
        parts.extend((str(payload_index), str(tail)))
    if slash_count is not None:
        parts.append(str(slash_count))
    rows.append({
        "case": "/".join(parts),
        "cohort": cohort,
        "context": context,
        "domain": domain,
        "flags": flags,
        "phrase": encode_subject(native_phrase),
        "subject": encode_subject(native_subject),
        "line_ending": ending,
        "tail": tail,
        "payload_index": payload_index,
        "slash_count": slash_count,
        "expected_kind": expected,
        "seed": PUBLISHED_SEED,
    })


def frozen_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for domain in ("str", "bytes"):
        for payload_index, payload in enumerate(COMMENT_PAYLOADS):
            for ending_name, ending in SEMANTIC_ENDINGS:
                for tail_name, tail, subject in SEMANTIC_TAILS:
                    for context, phrase, flags, actual in semantic_contexts(
                        payload, ending, tail, subject,
                    ):
                        slash_count = len(payload) - len(payload.rstrip("\\"))
                        continued = ending_name == "lf" and slash_count % 2 == 1
                        expected = (
                            "continued-comment-empty"
                            if continued and context in {
                                "root_verbose", "global_verbose",
                            }
                            else "continued-comment-unterminated"
                            if continued else "full-match"
                        )
                        append_case(
                            rows, domain=domain, cohort="semantic",
                            context=context, phrase=phrase, flags=flags,
                            subject=actual, ending=ending_name, tail=tail_name,
                            payload_index=payload_index, slash_count=None,
                            expected=expected,
                        )
        for slash_count in range(7):
            for ending_name, ending in TOKENIZER_ENDINGS:
                body = "a # " + "\\" * slash_count + ending + "b"
                terminated = (
                    ending_name in {"crlf", "double_lf"}
                    or ending_name in {"lf", "lfcr"} and slash_count % 2 == 0
                )
                for context in TOKENIZER_CONTEXTS:
                    phrase = (
                        body if context == "root"
                        else "(?x)" + body if context == "global"
                        else "(?x:" + body + ")"
                    )
                    expected = (
                        "full-match" if terminated
                        else "continued-comment-unterminated"
                        if context == "scoped" else "prefix-then-fallback"
                    )
                    append_case(
                        rows, domain=domain, cohort="tokenizer",
                        context=context, phrase=phrase,
                        flags=VERBOSE if context == "root" else 0,
                        subject="ab", ending=ending_name, tail=None,
                        payload_index=None, slash_count=slash_count,
                        expected=expected,
                    )
    require(len(rows) == CASE_COUNT, "a frozen Scanner graph case was omitted")
    random.Random(PUBLISHED_SEED).shuffle(rows)
    return validate_matrix(rows)


def validate_matrix(rows: Any) -> list[dict[str, Any]]:
    require(type(rows) is list and len(rows) == CASE_COUNT,
            "all 2,854 frozen Scanner cases must remain visible")
    fields = {
        "case", "cohort", "context", "domain", "flags", "phrase", "subject",
        "line_ending", "tail", "payload_index", "slash_count",
        "expected_kind", "seed",
    }
    seen: set[str] = set()
    kinds = {name: 0 for name in EXPECTED_COUNTS}
    cohorts = {"semantic": 0, "tokenizer": 0}
    errors = {"semantic": 0, "tokenizer": 0}
    for row in rows:
        require(type(row) is dict and set(row) == fields,
                "a frozen Scanner graph matrix field was changed")
        case = row.get("case")
        cohort = row.get("cohort")
        domain = row.get("domain")
        kind = row.get("expected_kind")
        require(type(case) is str and case not in seen
                and cohort in cohorts and domain in {"str", "bytes"}
                and kind in kinds and type(row.get("flags")) is int
                and row["flags"] in {0, VERBOSE}
                and type(row.get("seed")) is int
                and row["seed"] == PUBLISHED_SEED,
                "a Scanner case, source order, flag, or 64-bit seed changed")
        seen.add(case)
        decode_subject(row.get("phrase"), domain)
        decode_subject(row.get("subject"), domain)
        cohorts[cohort] += 1
        kinds[kind] += 1
        if kind == "continued-comment-unterminated":
            errors[cohort] += 1
        if cohort == "semantic":
            require(row.get("context") in SEMANTIC_CONTEXTS
                    and row.get("line_ending") in {"lf", "crlf"}
                    and row.get("tail") in {item[0] for item in SEMANTIC_TAILS}
                    and type(row.get("payload_index")) is int
                    and 0 <= row["payload_index"] < len(COMMENT_PAYLOADS)
                    and row.get("slash_count") is None,
                    "a frozen Scanner scope, capture, or comment was hidden")
        else:
            require(row.get("context") in TOKENIZER_CONTEXTS
                    and row.get("line_ending")
                    in {item[0] for item in TOKENIZER_ENDINGS}
                    and row.get("tail") is None
                    and row.get("payload_index") is None
                    and type(row.get("slash_count")) is int
                    and 0 <= row["slash_count"] <= 6,
                    "a frozen Scanner escaped newline was hidden")
    require(cohorts == {
        "semantic": SEMANTIC_CASE_COUNT,
        "tokenizer": TOKENIZER_CASE_COUNT,
    } and kinds == EXPECTED_COUNTS and errors == EXPECTED_NEGATIVE_COUNTS
            and digest(rows) == MATRIX_SHA256,
            "the independently frozen Scanner matrix or denominator changed")
    return rows


def validate_normalized(value: Any) -> None:
    require(type(value) is dict and type(value.get("kind")) is str,
            "a complete typed Scanner observation is mandatory")
    kind = value["kind"]
    if kind == "none":
        require(set(value) == {"kind"}, "a genuine None was forged")
    elif kind in {"bool", "int", "str"}:
        native = {"bool": bool, "int": int, "str": str}[kind]
        require(set(value) == {"kind", "value"}
                and type(value.get("value")) is native,
                "a typed Scanner scalar was forged")
    elif kind in {"bytes", "bytearray"}:
        require(set(value) == {"kind", "hex"}
                and type(value.get("hex")) is str,
                "a complete Scanner binary result was omitted")
        try:
            raw = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise OverviewError("a Scanner binary value is not canonical hex") from error
        require(raw.hex() == value["hex"],
                "a Scanner binary value is not lowercase hex")
    elif kind == "memoryview":
        require(set(value) == {
            "kind", "readonly", "format", "itemsize", "ndim", "shape",
            "strides", "contiguous", "hex",
        } and type(value.get("readonly")) is bool
                and type(value.get("format")) is str
                and type(value.get("itemsize")) is int
                and value["itemsize"] > 0
                and type(value.get("ndim")) is int and value["ndim"] >= 0
                and type(value.get("contiguous")) is bool
                and type(value.get("hex")) is str,
                "a complete observed Scanner buffer layout was concealed")
        try:
            raw = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise OverviewError("a Scanner buffer is not canonical hex") from error
        require(raw.hex() == value["hex"],
                "a Scanner buffer value is not canonical lowercase hex")
        for name in ("shape", "strides"):
            actual = value[name]
            require(actual is None or type(actual) is list
                    and len(actual) == value["ndim"]
                    and all(type(item) is int for item in actual),
                    "an observed Scanner buffer layout was omitted")
    elif kind in {"tuple", "list"}:
        require(set(value) == {"kind", "items"}
                and type(value.get("items")) is list,
                "a complete ordered Scanner result was omitted")
        for item in value["items"]:
            validate_normalized(item)
    elif kind == "mapping":
        require(set(value) == {"kind", "items"}
                and type(value.get("items")) is list,
                "a complete observed Scanner mapping was omitted")
        previous: bytes | None = None
        for pair in value["items"]:
            require(type(pair) is list and len(pair) == 2,
                    "an observed Scanner mapping entry was omitted")
            validate_normalized(pair[0])
            validate_normalized(pair[1])
            actual = canonical(pair[0])
            require(previous is None or previous < actual,
                    "Scanner mapping entries were reordered or duplicated")
            previous = actual
    else:
        raise OverviewError("an approximate Scanner carrier was injected")


def validate_pattern(value: Any) -> None:
    require(type(value) is dict and set(value) == {
        "kind", "pattern", "flags", "groups", "groupindex",
    } and value.get("kind") == "compiled-pattern"
            and type(value.get("flags")) is int
            and type(value.get("groups")) is int and value["groups"] >= 0,
            "a complete combined Scanner pattern was concealed")
    validate_normalized(value["pattern"])
    validate_normalized(value["groupindex"])


def validate_match(value: Any) -> None:
    require(type(value) is dict and set(value) == {
        "kind", "pattern", "string", "group", "groups", "spans",
        "groupdict", "lastindex", "lastgroup", "pos", "endpos",
    } and value.get("kind") == "match",
            "a complete genuine Scanner callback match was concealed")
    validate_pattern(value["pattern"])
    count = value["pattern"]["groups"]
    require(type(value.get("groups")) is list and len(value["groups"]) == count
            and type(value.get("spans")) is list
            and len(value["spans"]) == count + 1
            and type(value.get("pos")) is int
            and type(value.get("endpos")) is int
            and (value.get("lastindex") is None
                 or type(value["lastindex"]) is int)
            and (value.get("lastgroup") is None
                 or type(value["lastgroup"]) is str),
            "a Scanner capture, position, or complete match span was omitted")
    for name in ("string", "group", "groupdict"):
        validate_normalized(value[name])
    for item in value["groups"]:
        validate_normalized(item)
    for span in value["spans"]:
        require(type(span) is list and len(span) == 2
                and all(type(item) is int for item in span),
                "a complete Scanner callback capture span was omitted")


def validate_error(value: Any) -> None:
    require(type(value) is dict and type(value.get("kind")) is str,
            "a complete original Python Scanner exception is mandatory")
    if value["kind"] == "public-regex-error":
        require(set(value) == {
            "kind", "type", "args", "message", "pattern", "position",
            "line", "column",
        } and type(value.get("type")) is str
                and (value.get("message") is None
                     or type(value["message"]) is str),
                "a genuine Scanner PatternError was approximated")
        validate_normalized(value["args"])
        validate_normalized(value["pattern"])
        for name in ("position", "line", "column"):
            require(value[name] is None or type(value[name]) is int,
                    "an original Scanner PatternError position was hidden")
    else:
        require(value["kind"] == "ordinary-python-error"
                and set(value) == {"kind", "module", "type", "args"}
                and type(value.get("module")) is str
                and type(value.get("type")) is str,
                "a genuine Scanner Python exception was approximated")
        validate_normalized(value["args"])


def validate_outcome(value: Any, *, candidate: bool = False) -> None:
    require(type(value) is dict and type(value.get("status")) is str,
            "a complete actual Scanner case outcome is mandatory")
    if value["status"] == "contract-violation":
        require(candidate and set(value) == {
            "status", "violation", "callbacks", "warnings", "combined_pattern",
        } and type(value.get("violation")) is dict
                and set(value["violation"]) == {"type", "message"}
                and all(type(value["violation"].get(name)) is str
                        for name in ("type", "message"))
                and type(value.get("callbacks")) is list
                and type(value.get("warnings")) is list,
                "a genuine Scanner compatibility violation was concealed")
        if value["combined_pattern"] is not None:
            validate_pattern(value["combined_pattern"])
        for callback in value["callbacks"]:
            require(type(callback) is dict,
                    "a partial Scanner failure callback was concealed")
        return
    require(value["status"] in {"return", "raise"},
            "an unknown or approximated Scanner result was injected")
    wanted = {"status", "callbacks", "warnings", "combined_pattern"}
    wanted.add("value" if value["status"] == "return" else "exception")
    require(set(value) == wanted
            and type(value.get("callbacks")) is list
            and len(value["callbacks"]) <= 2
            and type(value.get("warnings")) is list,
            "a Scanner return, callback, warning, or exception was omitted")
    if value["combined_pattern"] is not None:
        validate_pattern(value["combined_pattern"])
    for event in value["callbacks"]:
        require(type(event) is dict and set(event) == {
            "branch", "token", "match", "combined_pattern",
            "match_uses_combined_pattern",
        } and type(event.get("branch")) is int and event["branch"] in {0, 1}
                and type(event.get("match_uses_combined_pattern")) is bool,
                "a complete observed Scanner callback was omitted")
        validate_normalized(event["token"])
        validate_match(event["match"])
        validate_pattern(event["combined_pattern"])
    for warning in value["warnings"]:
        require(type(warning) is dict and set(warning) == {
            "category_module", "category", "message",
        } and all(type(warning[name]) is str for name in warning),
                "a complete original Scanner warning was hidden")
    if value["status"] == "return":
        validate_normalized(value["value"])
    else:
        validate_error(value["exception"])


def normalized_subject(value: str | bytes) -> dict[str, Any]:
    return encode_subject(value)


def verify_expected_outcome(case: Mapping[str, Any], outcome: Mapping[str, Any]) -> None:
    expected = case["expected_kind"]
    callbacks = outcome["callbacks"]
    if expected == "continued-comment-unterminated":
        require(outcome["status"] == "raise"
                and outcome["exception"]["kind"] == "public-regex-error"
                and outcome["exception"]["type"] in {"PatternError", "error"}
                and callbacks == [] and outcome["combined_pattern"] is None,
                "a genuine Scanner PatternError was hidden")
        return
    require(outcome["status"] == "return"
            and outcome["combined_pattern"] is not None,
            "a valid standard-Python Scanner observation unexpectedly raised")
    returned = outcome["value"]
    require(returned["kind"] == "tuple" and len(returned["items"]) == 2
            and returned["items"][0]["kind"] == "list",
            "the original Scanner tokens and remainder were approximated")
    tokens = returned["items"][0]["items"]
    remainder = returned["items"][1]
    subject = decode_subject(case["subject"], case["domain"])
    empty = normalized_subject(subject[:0])
    if expected == "continued-comment-empty":
        require(tokens == [] and callbacks == []
                and remainder == normalized_subject(subject),
                "a zero-width original Scanner stop was hidden")
    elif expected == "full-match":
        require(len(tokens) == len(callbacks) == 1
                and callbacks[0]["branch"] == 0
                and callbacks[0]["token"] == normalized_subject(subject)
                and callbacks[0]["match_uses_combined_pattern"] is True
                and remainder == empty,
                "an actual original Scanner match or callback changed")
    else:
        require(expected == "prefix-then-fallback"
                and len(tokens) == len(callbacks) == 2
                and [item["branch"] for item in callbacks] == [0, 1]
                and callbacks[0]["token"] == normalized_subject(subject[:1])
                and callbacks[1]["token"] == normalized_subject(subject[1:])
                and all(item["match_uses_combined_pattern"] is True
                        for item in callbacks)
                and remainder == empty,
                "an actual original Scanner fallback callback was hidden")


def validate_records(
    matrix: list[dict[str, Any]], records: Any, records_sha256: Any,
    *, candidate: bool = False,
) -> list[dict[str, Any]]:
    expected = valid_hash(records_sha256, "all source-ordered Scanner results")
    require(type(records) is list and len(records) == CASE_COUNT,
            "every one of the 2,854 Scanner case outcomes is mandatory")
    for case, record in zip(matrix, records, strict=True):
        require(type(record) is dict and set(record) == {
            "case", "cohort", "expected_kind", "outcome",
        } and record.get("case") == case["case"]
                and record.get("cohort") == case["cohort"]
                and record.get("expected_kind") == case["expected_kind"],
                "an actual Scanner result was omitted, relabeled, or reordered")
        validate_outcome(record["outcome"], candidate=candidate)
        if not candidate:
            verify_expected_outcome(case, record["outcome"])
    require(digest(records) == expected,
            "the complete source-ordered Scanner outcome vector was changed")
    return records


def validate_owner(
    value: Any, relative: str, expected: str | None = None,
    *, external: bool = False,
) -> dict[str, Any]:
    key = "path" if external else "relative"
    require(type(value) is dict
            and set(value) == {key, "sha256", "bytes", "device", "inode"}
            and value.get(key) == relative
            and type(value.get("bytes")) is int and value["bytes"] > 0
            and type(value.get("device")) is int and value["device"] >= 0
            and type(value.get("inode")) is int and value["inode"] > 0,
            "a complete authenticated Scanner owner was omitted: " + relative)
    actual = valid_hash(value.get("sha256"), relative)
    require(expected is None or actual == expected,
            "a frozen Scanner source or native owner was substituted")
    return value


def validate_tool_closure(value: Any) -> dict[str, Any]:
    expected = {
        "recorder": (RECORDER_RELATIVE, RECORDER_SHA256),
        "scanner_oracle": (ORACLE_RELATIVE, ORACLE_SHA256),
        "original_v5": (V5_RELATIVE, V5_SHA256),
        "from_scratch_audit_v3": (AUDIT_RELATIVE, AUDIT_SHA256),
    }
    require(type(value) is dict and set(value) == set(expected),
            "the complete Scanner oracle and ownership-policy closure was omitted")
    for name, (relative, source) in expected.items():
        validate_owner(value[name], relative, source)
    return value


def validate_standard_owners(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and set(value) == {"oracle", "python", *PINNED_STDLIB_SOURCES},
            "the complete genuine CPython Scanner source closure was omitted")
    validate_owner(value["oracle"], ROOT + "/" + ORACLE_RELATIVE,
                   ORACLE_SHA256, external=True)
    validate_owner(value["python"], PINNED_PYTHON,
                   PINNED_PYTHON_SHA256, external=True)
    for name, (filename, source) in PINNED_STDLIB_SOURCES.items():
        validate_owner(value[name], PINNED_STDLIB_DIRECTORY + filename,
                       source, external=True)
    return value


def validate_audit_manifest(
    value: Any, family: str, adapter: str, engine: str, bridge: str,
) -> dict[str, Any]:
    adapter_path, engine_path, bridge_path, sources, _ = FAMILY_SPECS[family]
    require(type(value) is dict and set(value) == {
        "family", "candidate_source_sha256", "native_engine_sha256",
        "native_bridge_sha256", "source_sha256", "native_sha256",
        "immutable_policy_sha256",
    } and value.get("family") == family
            and value.get("candidate_source_sha256") == adapter
            and value.get("native_engine_sha256") == engine
            and value.get("native_bridge_sha256") == bridge,
            "a complete independently owned Scanner engine manifest was forged")
    owned = value.get("source_sha256")
    native = value.get("native_sha256")
    require(type(owned) is dict and set(owned) == set(sources)
            and type(native) is dict
            and set(native) == {engine_path, bridge_path}
            and owned.get(adapter_path) == adapter
            and native.get(engine_path) == engine
            and native.get(bridge_path) == bridge,
            "a family-owned engine, native bridge, or source was omitted")
    for relative, source in (*owned.items(), *native.items()):
        safe_parts(relative)
        valid_hash(source, relative)
    require(len(set(owned.values())) == len(owned)
            and len(set(native.values())) == len(native)
            and (engine == bridge) is (family == "c"),
            "an independent parser, compiler, or native bridge was aliased")
    require(value.get("immutable_policy_sha256") == {
        V2_RELATIVE: V2_SHA256,
        V5_RELATIVE: V5_SHA256,
    }, "the immutable no-delegation ownership policies were changed")
    return value


def validate_candidate_closure(
    value: Any, family: str, adapter: str, engine: str, bridge: str,
) -> dict[str, Any]:
    require(type(value) is dict and set(value) == {
        "family", "manifest", "source_owners", "native_owners",
        "policy_owners", "oracle_owner", "python_owner",
    } and value.get("family") == family,
            "a complete independently owned Scanner family closure is mandatory")
    manifest = validate_audit_manifest(
        value["manifest"], family, adapter, engine, bridge,
    )
    sources = value["source_owners"]
    native = value["native_owners"]
    policies = value["policy_owners"]
    require(type(sources) is dict and set(sources) == set(manifest["source_sha256"])
            and type(native) is dict and set(native) == set(manifest["native_sha256"])
            and type(policies) is dict and set(policies) == {V2_RELATIVE, V5_RELATIVE},
            "a complete source, binary, or frozen policy owner was concealed")
    for path, source in manifest["source_sha256"].items():
        validate_owner(sources[path], path, source)
    for path, source in manifest["native_sha256"].items():
        validate_owner(native[path], path, source)
    validate_owner(policies[V2_RELATIVE], V2_RELATIVE, V2_SHA256)
    validate_owner(policies[V5_RELATIVE], V5_RELATIVE, V5_SHA256)
    validate_owner(value["oracle_owner"], AUDIT_RELATIVE, AUDIT_SHA256)
    validate_owner(value["python_owner"], PINNED_PYTHON,
                   PINNED_PYTHON_SHA256, external=True)
    return value


def validate_guard(value: Any, family: str) -> dict[str, Any]:
    require(type(value) is dict, "continuous Scanner no-delegation guards are mandatory")
    for name in GUARD_TRUE:
        require(value.get(name) is True,
                "an independently owned Scanner guard was disabled: " + name)
    require(value.get("public_type_names_used_for_ownership") is False,
            "a genuine family-owned Scanner type was misidentified")
    for name in ("actual_method_guard_checks", "actual_warning_registry_guard_checks"):
        require(type(value.get(name)) is int and value[name] == 2 * CASE_COUNT,
                "all 5,708 before-and-after Scanner guards are mandatory")
    ffi = FAMILY_SPECS[family][4]
    require(value.get("owned_native_ffi_allowed") is ffi,
            "the independently owned Zig native-loader policy changed")
    for name in (
        "trusted_stdlib_ctypes_preloaded",
        "trusted_stdlib_ctypes_builtin_verified",
        "trusted_stdlib_ctypes_pythonapi_initialized",
    ):
        require(value.get(name) is ffi,
                "the independently owned native binding guard changed")
    require(value.get("trusted_stdlib_ctypes_source_sha256")
            == (TRUSTED_CTYPES_SHA256 if ffi else None),
            "the frozen trusted native binding source was substituted")
    for name in GUARD_COUNTERS:
        require(type(value.get(name)) is int and value[name] >= 0,
                "a genuine continuous native guard counter was concealed")
    if ffi:
        require(value["owned_ctypes_load_count"] > 0
                and value["owned_ctypes_symbol_count"] > 0,
                "the independently owned Zig native engine never loaded")
    else:
        require(value["owned_ctypes_load_count"] == 0
                and value["owned_ctypes_symbol_count"] == 0,
                "a candidate delegated to an unowned native engine")
    return value


def capture_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "a complete bounded genuine process stream is mandatory")
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"base64", "bytes", "sha256", "complete"}
            and type(value.get("base64")) is str
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and value.get("complete") is True,
            "a complete source-authenticated process stream was omitted: " + label)
    expected = valid_hash(value.get("sha256"), label)
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError, binascii.Error) as error:
        raise OverviewError("a complete Scanner process stream was forged") from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == expected
            and base64.b64encode(raw).decode("ascii") == value["base64"],
            "a source-authenticated Scanner process stream was truncated")
    return raw


def validate_reference_guard(value: Any) -> None:
    require(value == {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "required_method_guard_checks": 2 * CASE_COUNT,
        "future_candidate_guard_relative": V5_RELATIVE,
        "future_candidate_guard_sha256": V5_SHA256,
        "future_ownership_audit_relative": AUDIT_RELATIVE,
        "future_ownership_audit_sha256": AUDIT_SHA256,
        "future_candidate_guard_installed": False,
    }, "a complete standard-Python reference guard was disabled")


def validate_reference_worker(
    value: Any, role: str, matrix: list[dict[str, Any]],
    records_hash: str,
) -> dict[str, Any]:
    expected = {
        "schema": ORACLE_SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": EXPECTED_COUNTS,
        "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
        "records_sha256": records_hash,
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(type(value) is dict and set(value) == set(expected) | {
        "pid", "records", "source_owners", "reference_guard",
    }, "a complete independent standard reference worker was concealed")
    fixed_fields(value, expected, "the independent standard Python worker")
    require(type(value.get("pid")) is int and value["pid"] > 0,
            "a genuine independent standard reference PID is mandatory")
    validate_standard_owners(value["source_owners"])
    validate_reference_guard(value["reference_guard"])
    validate_records(matrix, value["records"], records_hash)
    return value


def validate_reference_process(value: Any, worker: Mapping[str, Any], role: str) -> None:
    require(type(value) is dict and set(value) == {
        "role", "pid", "returncode", "stdout", "stderr",
    } and value.get("role") == role
            and value.get("pid") == worker["pid"]
            and type(value.get("returncode")) is int
            and value["returncode"] == 0,
            "a genuine isolated standard Scanner worker process was substituted")
    require(decode_stream(value["stdout"], role + " stdout")
            == canonical(dict(worker))
            and decode_stream(value["stderr"], role + " stderr") == b"",
            "the complete standard reference worker streams were replaced")


def source_fields(label: str) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "label": validate_label(label),
        "recorder_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": RECORDER_SHA256,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": EXPECTED_COUNTS,
        "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
    }


def evidence_pin(value: Any, seen: set[str]) -> tuple[str, str]:
    require(type(value) is dict and set(value) == {"relative", "sha256"},
            "an exact source-pinned Scanner report or receipt is mandatory")
    relative = value.get("relative")
    parts = safe_parts(relative)
    require(len(parts) == 3
            and parts[:2] == ("experiments", "rust_public_practice_v1")
            and relative not in seen,
            "Scanner evidence was reused or escaped the approved directory")
    seen.add(relative)
    return relative, valid_hash(value.get("sha256"), relative)


def approved_paths(
    label: str, family: str | None = None,
) -> tuple[str, str]:
    label = validate_label(label)
    if family is None:
        stem = "scanner-verbose-comments-v1-" + label
    else:
        require(family in FAMILY_ORDER,
                "select only an independently written Scanner family")
        stem = family + "-scanner-verbose-comments-v1-" + label
    return (
        EVIDENCE_DIRECTORY + "/" + stem + ".json.gz",
        EVIDENCE_DIRECTORY + "/" + stem + "-publication-receipt.json",
    )


def validate_baseline_receipt(
    value: Any, label: str, archive_path: str, archive_hash: str,
    receipt_path: str,
) -> dict[str, Any]:
    expected = {
        "schema": RECORDER_SCHEMA + "-durable-baseline-publication-receipt",
        "status": "PASS",
        "baseline_result_status": "PASS",
        **source_fields(label),
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "source_closure_unchanged": True,
        "report_relative": archive_path,
        "report_sha256": archive_hash,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_path,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_baseline": True,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(type(value) is dict and set(value) == BASELINE_RECEIPT_FIELDS,
            "a complete two-reference Scanner baseline receipt is mandatory")
    fixed_fields(value, expected, "the passing standard-Python Scanner receipt")
    valid_hash(value.get("baseline_records_sha256"), "complete baseline records")
    valid_hash(value.get("report_uncompressed_sha256"), "complete baseline report")
    require(type(value.get("report_bytes")) is int
            and 0 < value["report_bytes"] <= MAX_ARCHIVE_BYTES
            and type(value.get("report_uncompressed_bytes")) is int
            and 0 < value["report_uncompressed_bytes"] <= MAX_UNCOMPRESSED_BYTES,
            "the complete single-member baseline archive bounds were hidden")
    pids = value.get("baseline_reference_pids")
    require(type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1],
            "two genuinely independent standard-Python workers are mandatory")
    before = validate_tool_closure(value.get("source_closure_before"))
    after = validate_tool_closure(value.get("source_closure_after"))
    require(before == after,
            "a frozen Scanner oracle or ownership policy changed")
    return value


def validate_baseline_result(
    value: Any, matrix: list[dict[str, Any]], receipt: Mapping[str, Any],
) -> dict[str, Any]:
    records_hash = receipt["baseline_records_sha256"]
    expected = {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": EXPECTED_COUNTS,
        "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
        "baseline_records_sha256": records_hash,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(type(value) is dict and set(value) == set(expected) | {
        "source_owners", "reference_a", "reference_b",
        "reference_a_process", "reference_b_process",
    }, "a complete independently observed two-worker baseline was concealed")
    fixed_fields(value, expected, "the genuine two-reference Scanner baseline")
    shared = validate_standard_owners(value["source_owners"])
    first = validate_reference_worker(value["reference_a"], "reference_a", matrix,
                                      records_hash)
    second = validate_reference_worker(value["reference_b"], "reference_b", matrix,
                                       records_hash)
    validate_reference_process(value["reference_a_process"], first, "reference_a")
    validate_reference_process(value["reference_b_process"], second, "reference_b")
    require(first["pid"] != second["pid"]
            and [first["pid"], second["pid"]] == receipt["baseline_reference_pids"]
            and first["source_owners"] == second["source_owners"] == shared
            and first["records"] == second["records"],
            "two independently observed standard-Python Scanner workers disagree")
    return value


def validate_baseline(
    value: Any, matrix: list[dict[str, Any]], receipt: Mapping[str, Any],
) -> list[dict[str, Any]]:
    expected = {
        "schema": RECORDER_SCHEMA + "-complete-baseline-report",
        "status": "PASS",
        **source_fields(receipt["label"]),
        "source_closure_unchanged": True,
        "complete_structured_baseline_failure": None,
        "complete_reference_worker_failure": None,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_records_sha256": receipt["baseline_records_sha256"],
        "baseline_reference_pids": receipt["baseline_reference_pids"],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
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
    }
    require(type(value) is dict and set(value) == BASELINE_FIELDS,
            "the complete archived Scanner baseline report is mandatory")
    fixed_fields(value, expected, "the lossless passing Scanner baseline")
    before = validate_tool_closure(value["source_closure_before"])
    after = validate_tool_closure(value["source_closure_after"])
    require(before == after == receipt["source_closure_before"],
            "the frozen Scanner baseline source closure was changed")
    controller_pid = value.get("actual_baseline_controller_pid")
    require(type(controller_pid) is int and controller_pid > 0
            and controller_pid not in receipt["baseline_reference_pids"],
            "the standard-Python controller was aliased to a reference worker")
    result = validate_baseline_result(value["complete_baseline_result"], matrix, receipt)
    require(value["complete_decoded_baseline_process"] == result
            and decode_stream(value["complete_baseline_process_stdout"],
                              "baseline controller stdout") == canonical(result)
            and decode_stream(value["complete_baseline_process_stderr"],
                              "baseline controller stderr") == b""
            and value["reference_a_records"] == result["reference_a"]["records"]
            and value["reference_b_records"] == result["reference_b"]["records"]
            and value["reference_a_process"] == result["reference_a_process"]
            and value["reference_b_process"] == result["reference_b_process"],
            "a complete standard-Python controller stream or result was omitted")
    return result["reference_a"]["records"]


def validate_candidate_receipt(
    value: Any, family: str, source_hash: str,
    baseline: Mapping[str, Any], report_path: str, report_hash: str,
    receipt_path: str,
) -> dict[str, Any]:
    require(type(value) is dict and set(value) == CANDIDATE_RECEIPT_FIELDS,
            "a complete owned Scanner candidate publication receipt is mandatory")
    label = validate_label(value.get("label"))
    require((report_path, receipt_path) == approved_paths(label, family),
            "a candidate report or receipt escaped its exact owned label")
    engine = valid_hash(value.get("native_engine_sha256"), "owned Scanner engine")
    bridge = valid_hash(value.get("native_bridge_sha256"), "owned Scanner bridge")
    expected = {
        "schema": RECORDER_SCHEMA + "-durable-candidate-publication-receipt",
        "status": "PASS",
        "python": "3.14.6",
        "label": label,
        "candidate_family": family,
        "candidate_source_sha256": source_hash,
        "native_engine_sha256": engine,
        "native_bridge_sha256": bridge,
        "baseline_label": baseline["label"],
        "recorder_source_sha256": RECORDER_SHA256,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": EXPECTED_COUNTS,
        "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
        "baseline_receipt_relative": baseline["receipt_relative"],
        "baseline_receipt_sha256": baseline["receipt_sha256"],
        "baseline_archive_relative": baseline["archive_relative"],
        "baseline_archive_sha256": baseline["archive_sha256"],
        "baseline_records_sha256": baseline["records_sha256"],
        "baseline_reference_pids": baseline["reference_pids"],
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_process_invocations": 1,
        "candidate_owner_unchanged": True,
        "report_relative": report_path,
        "report_sha256": report_hash,
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
    fixed_fields(value, expected, "the durable owned Scanner candidate receipt")
    actual_status = value.get("candidate_result_status")
    mismatches = value.get("mismatch_count")
    require(actual_status in {"PASS", "FAIL"}
            and type(mismatches) is int and 0 <= mismatches <= CASE_COUNT
            and (actual_status == "PASS") is (mismatches == 0),
            "candidate correctness was confused with successful publication")
    valid_hash(value.get("candidate_records_sha256"), "complete candidate records")
    valid_hash(value.get("report_uncompressed_sha256"), "complete candidate report")
    require(type(value.get("report_bytes")) is int
            and 0 < value["report_bytes"] <= MAX_ARCHIVE_BYTES
            and type(value.get("report_uncompressed_bytes")) is int
            and 0 < value["report_uncompressed_bytes"] <= MAX_UNCOMPRESSED_BYTES,
            "a lossless candidate report size was omitted")
    require(type(value.get("actual_candidate_imports")) is int
            and value["actual_candidate_imports"] >= 2,
            "an independently owned Scanner and native bridge were never imported")
    before = validate_candidate_closure(
        value.get("candidate_owner_before"), family, source_hash, engine, bridge,
    )
    after = validate_candidate_closure(
        value.get("candidate_owner_after"), family, source_hash, engine, bridge,
    )
    require(before == after, "an independently owned Scanner source changed")
    validate_mismatch_counts(value, mismatches)
    return value


def validate_mismatch_counts(value: Mapping[str, Any], mismatch_count: int) -> None:
    kinds = value.get("mismatches_by_expected_kind")
    cohorts = value.get("mismatches_by_cohort")
    require(type(kinds) is dict and set(kinds) == set(EXPECTED_COUNTS)
            and all(type(kinds[name]) is int
                    and 0 <= kinds[name] <= EXPECTED_COUNTS[name]
                    for name in EXPECTED_COUNTS)
            and sum(kinds.values()) == mismatch_count,
            "an original Scanner result class or failure was hidden")
    require(type(cohorts) is dict and set(cohorts) == {"semantic", "tokenizer"}
            and all(type(count) is int and count >= 0 for count in cohorts.values())
            and cohorts["semantic"] <= SEMANTIC_CASE_COUNT
            and cohorts["tokenizer"] <= TOKENIZER_CASE_COUNT
            and sum(cohorts.values()) == mismatch_count,
            "a complete Scanner scope or escaped-newline failure was hidden")


def validate_native_provenance(
    value: Any, family: str, source: str, engine: str, bridge: str,
) -> None:
    adapter_path, engine_path, bridge_path, _, _ = FAMILY_SPECS[family]
    require(type(value) is dict and set(value) == {
        "source", "native_engine", "native_bridge",
    }, "complete owned Scanner-native provenance is mandatory")
    validate_owner(value["source"], adapter_path, source)
    validate_owner(value["native_engine"], engine_path, engine)
    validate_owner(value["native_bridge"], bridge_path, bridge)
    require((value["native_engine"] == value["native_bridge"])
            is (family == "c"),
            "a genuine owned Scanner bridge was incorrectly aliased")


def validate_candidate_worker(
    value: Any, receipt: Mapping[str, Any], baseline: Mapping[str, Any],
    matrix: list[dict[str, Any]], closure: Mapping[str, Any],
) -> dict[str, Any]:
    family = receipt["candidate_family"]
    expected = {
        "schema": RECORDER_SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + family,
        "candidate_family": family,
        **source_fields(baseline["label"]),
        "baseline_receipt_relative": baseline["receipt_relative"],
        "baseline_receipt_sha256": baseline["receipt_sha256"],
        "baseline_archive_relative": baseline["archive_relative"],
        "baseline_archive_sha256": baseline["archive_sha256"],
        "baseline_records_sha256": baseline["records_sha256"],
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    extras = {
        "pid", "baseline_reference_pids", "baseline_receipt_owner",
        "baseline_archive_owner", "source_provenance", "audit_manifest",
        "owned_source_closure", "native_provenance", "matcher_guard",
        "records_sha256", "records", "actual_candidate_imports",
    }
    require(type(value) is dict and set(value) == set(expected) | extras,
            "a complete isolated owned Scanner worker was concealed")
    fixed_fields(value, expected, "the isolated family-owned Scanner worker")
    pid = value.get("pid")
    require(type(pid) is int and pid > 0
            and pid not in baseline["reference_pids"],
            "an owned Scanner worker was aliased to a standard reference")
    require(value.get("baseline_reference_pids") == baseline["reference_pids"]
            and value.get("actual_candidate_imports")
            == receipt["actual_candidate_imports"]
            and value.get("records_sha256") == receipt["candidate_records_sha256"],
            "a genuine candidate process or outcome vector was substituted")
    validate_owner(value.get("baseline_receipt_owner"),
                   baseline["receipt_relative"], baseline["receipt_sha256"])
    validate_owner(value.get("baseline_archive_owner"),
                   baseline["archive_relative"], baseline["archive_sha256"])
    validate_tool_closure(value.get("source_provenance"))
    manifest = validate_audit_manifest(
        value.get("audit_manifest"), family,
        receipt["candidate_source_sha256"], receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    owned = validate_candidate_closure(
        value.get("owned_source_closure"), family,
        receipt["candidate_source_sha256"], receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    require(owned == closure and owned["manifest"] == manifest,
            "the actual Scanner worker escaped its pinned family ownership")
    validate_native_provenance(
        value.get("native_provenance"), family,
        receipt["candidate_source_sha256"], receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    validate_guard(value.get("matcher_guard"), family)
    validate_records(matrix, value["records"], receipt["candidate_records_sha256"],
                     candidate=True)
    return value


def validate_candidate(
    value: Any, receipt: Mapping[str, Any], baseline: Mapping[str, Any],
    matrix: list[dict[str, Any]], original: list[dict[str, Any]],
) -> dict[str, Any]:
    expected = {
        "schema": RECORDER_SCHEMA + "-complete-candidate-report",
        "status": receipt["candidate_result_status"],
        "python": "3.14.6",
        "label": receipt["label"],
        "candidate_family": receipt["candidate_family"],
        "candidate_source_sha256": receipt["candidate_source_sha256"],
        "native_engine_sha256": receipt["native_engine_sha256"],
        "native_bridge_sha256": receipt["native_bridge_sha256"],
        "baseline_label": baseline["label"],
        "recorder_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": RECORDER_SHA256,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": EXPECTED_COUNTS,
        "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
        "baseline_receipt_relative": baseline["receipt_relative"],
        "baseline_receipt_sha256": baseline["receipt_sha256"],
        "baseline_archive_relative": baseline["archive_relative"],
        "baseline_archive_sha256": baseline["archive_sha256"],
        "baseline_records_sha256": baseline["records_sha256"],
        "baseline_reference_pids": baseline["reference_pids"],
        "candidate_owner_unchanged": True,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "candidate_records_sha256": receipt["candidate_records_sha256"],
        "mismatch_count": receipt["mismatch_count"],
        "mismatches_by_expected_kind": receipt["mismatches_by_expected_kind"],
        "mismatches_by_cohort": receipt["mismatches_by_cohort"],
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": receipt["actual_candidate_imports"],
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
    }
    require(type(value) is dict and set(value) == CANDIDATE_FIELDS,
            "the complete frozen 2,854-case candidate report is mandatory")
    fixed_fields(value, expected, "the complete family-owned Scanner report")
    family = receipt["candidate_family"]
    closure = validate_candidate_closure(
        value["candidate_owner_before"], family,
        receipt["candidate_source_sha256"], receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    final = validate_candidate_closure(
        value["candidate_owner_after"], family,
        receipt["candidate_source_sha256"], receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    require(closure == final == receipt["candidate_owner_before"]
            == receipt["candidate_owner_after"],
            "the complete Scanner family source ownership changed")
    candidate = validate_candidate_worker(
        value["complete_candidate_result"], receipt, baseline, matrix, closure,
    )
    require(value["complete_decoded_candidate_process"] == candidate
            and value["candidate_records"] == candidate["records"]
            and decode_stream(value["complete_candidate_process_stdout"],
                              "candidate worker stdout") == canonical(candidate)
            and decode_stream(value["complete_candidate_process_stderr"],
                              "candidate worker stderr") == b""
            and value.get("actual_candidate_pid") == candidate["pid"]
            and value.get("matcher_guard") == candidate["matcher_guard"],
            "a complete actual Scanner worker stream or guard was omitted")
    require(value.get("baseline_records") == original,
            "the candidate was compared with a different Python baseline")
    mismatches: list[dict[str, Any]] = []
    kinds = {kind: 0 for kind in EXPECTED_COUNTS}
    cohorts = {"semantic": 0, "tokenizer": 0}
    for case, standard, observed in zip(
        matrix, original, candidate["records"], strict=True,
    ):
        require(case["case"] == standard["case"] == observed["case"]
                and case["cohort"] == standard["cohort"] == observed["cohort"]
                and case["expected_kind"] == standard["expected_kind"]
                == observed["expected_kind"],
                "an actual source-ordered Scanner case was hidden")
        if standard["outcome"] != observed["outcome"]:
            kinds[case["expected_kind"]] += 1
            cohorts[case["cohort"]] += 1
            mismatches.append({
                "case": case["case"],
                "cohort": case["cohort"],
                "expected_kind": case["expected_kind"],
                "input": case,
                "baseline_outcome": standard["outcome"],
                "candidate_outcome": observed["outcome"],
            })
    require(value.get("all_mismatches") == mismatches
            and value["mismatch_count"] == len(mismatches)
            and value["mismatches_by_expected_kind"] == kinds
            and value["mismatches_by_cohort"] == cohorts,
            "a real Scanner compatibility failure was hidden or approximated")
    reasons = value.get("all_failure_reasons")
    require(type(reasons) is list and all(type(reason) is str for reason in reasons)
            and type(value.get("failure_count")) is int
            and value["failure_count"] == len(reasons)
            and (len(reasons) == 0) is (len(mismatches) == 0)
            and (value["status"] == "PASS") is (len(mismatches) == 0),
            "a genuine Scanner worker failure or compatibility loss was concealed")
    return {
        "passed": CASE_COUNT - len(mismatches),
        "failed": len(mismatches),
        "not_measured": 0,
        "mismatches_by_expected_kind": kinds,
        "mismatches_by_cohort": cohorts,
    }


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE_RELATIVE
            and os.path.realpath(__file__) == ROOT + "/" + SOURCE_RELATIVE,
            "use only exact isolated pinned Python 3.14.6 and this graph source")
    for name in sys.modules:
        require(type(name) is str and name.partition(".")[0] not in FORBIDDEN_ROOTS,
                "the graph cannot import a candidate or external regex engine")


@contextlib.contextmanager
def open_owned(relative: str, maximum: int) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_parts(relative)
    require(type(maximum) is int and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
            "an exact bounded owned correctness input is mandatory")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact graph workspace root was substituted")
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a frozen graph parent was replaced by a symlink")
        descriptor = os.open(parts[-1], flags, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= maximum,
                "an exact no-follow Scanner graph input was substituted")
        yield descriptor, before
        final = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                == (named.st_dev, named.st_ino, named.st_size),
                "a frozen Scanner report changed while it was being read")
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    expected = valid_hash(expected, relative)
    with open_owned(relative, maximum) as (descriptor, before):
        remaining = before.st_size
        hasher = hashlib.sha256()
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(CHUNK_BYTES, remaining))
            require(type(block) is bytes and bool(block),
                    "a frozen Scanner evidence input was truncated")
            remaining -= len(block)
            hasher.update(block)
            blocks.append(block)
        require(os.read(descriptor, 1) == b""
                and hasher.hexdigest() == expected,
                "a frozen Scanner evidence input failed its SHA-256")
        return b"".join(blocks)


class VerifiedGzipReader:
    """Authenticate and stream exactly one bounded, lossless gzip member."""

    def __init__(
        self, descriptor: int, archive_bytes: int, archive_sha256: str,
        original_bytes: int, original_sha256: str,
    ) -> None:
        require(type(descriptor) is int
                and type(archive_bytes) is int
                and 0 < archive_bytes <= MAX_ARCHIVE_BYTES
                and type(original_bytes) is int
                and 0 < original_bytes <= MAX_UNCOMPRESSED_BYTES,
                "exact bounded original and compressed evidence is mandatory")
        self.descriptor = descriptor
        self.archive_bytes = archive_bytes
        self.archive_sha256 = valid_hash(archive_sha256, "Scanner gzip archive")
        self.original_bytes = original_bytes
        self.original_sha256 = valid_hash(original_sha256, "Scanner original report")
        self.inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self.compressed_hash = hashlib.sha256()
        self.original_hash = hashlib.sha256()
        self.compressed_count = 0
        self.original_count = 0
        self.pending = b""
        self.finished = False

    def read(self, requested: int) -> bytes:
        require(type(requested) is int and 0 < requested <= CHUNK_BYTES,
                "stream only bounded complete Scanner evidence blocks")
        result = bytearray()
        while len(result) < requested and not self.finished:
            if not self.pending and self.compressed_count < self.archive_bytes:
                block = os.read(
                    self.descriptor,
                    min(CHUNK_BYTES, self.archive_bytes - self.compressed_count),
                )
                require(type(block) is bytes and bool(block),
                        "an authenticated Scanner gzip archive was truncated")
                self.compressed_count += len(block)
                self.compressed_hash.update(block)
                self.pending = block
            if self.pending:
                limit = min(requested - len(result),
                            self.original_bytes - self.original_count + 1)
                try:
                    plain = self.inflater.decompress(self.pending, limit)
                except (zlib.error, ValueError, OverflowError) as error:
                    raise OverviewError("the Scanner gzip archive is invalid") from error
                require(not self.inflater.unused_data,
                        "Scanner gzip trailing bytes or extra members are forbidden")
                self.pending = self.inflater.unconsumed_tail
                if plain:
                    self.original_count += len(plain)
                    require(self.original_count <= self.original_bytes,
                            "Scanner gzip expansion exceeded its exact safe bound")
                    self.original_hash.update(plain)
                    result.extend(plain)
                continue
            require(self.compressed_count == self.archive_bytes,
                    "the exact authenticated Scanner gzip bytes are incomplete")
            require(self.inflater.eof and not self.inflater.unused_data,
                    "a complete single-member Scanner gzip footer is mandatory")
            require(os.read(self.descriptor, 1) == b"",
                    "the Scanner gzip archive gained an unauthenticated suffix")
            try:
                tail = self.inflater.flush(CHUNK_BYTES)
            except (zlib.error, ValueError) as error:
                raise OverviewError("the Scanner gzip footer could not finish") from error
            require(not tail, "the Scanner gzip retained unverified original bytes")
            require(self.compressed_hash.hexdigest() == self.archive_sha256,
                    "the complete Scanner gzip failed its frozen SHA-256")
            require(self.original_count == self.original_bytes
                    and self.original_hash.hexdigest() == self.original_sha256,
                    "the restored Scanner report failed its exact bytes or SHA-256")
            self.finished = True
        return bytes(result)


class StreamingObject:
    """Read all frozen top-level report fields without loading gzip bytes."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.utf8 = codecs.getincrementaldecoder("utf-8")("strict")
        self.decoder = json.JSONDecoder(object_pairs_hook=unique_object)
        self.buffer = ""
        self.position = 0
        self.ended = False

    def fill(self) -> bool:
        if self.ended:
            return False
        block = self.stream.read(CHUNK_BYTES)
        require(type(block) is bytes,
                "a streamed Scanner report emitted non-byte observations")
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
        return self.buffer[self.position] if self.position < len(self.buffer) else None

    def take(self) -> str:
        value = self.peek()
        require(value is not None, "the complete Scanner JSON report was truncated")
        self.position += 1
        return value

    def whitespace(self) -> None:
        while self.peek() in (" ", "\t", "\r", "\n"):
            self.position += 1
            self.compact()

    def literal(self, expected: str) -> None:
        self.whitespace()
        require(self.take() == expected,
                "a streamed Scanner JSON delimiter was substituted")

    def value(self) -> Any:
        self.whitespace()
        self.compact()
        while True:
            try:
                result, ending = self.decoder.raw_decode(self.buffer, self.position)
            except json.JSONDecodeError as error:
                require(not self.ended,
                        "a complete selected Scanner JSON value was clipped")
                require(len(self.buffer) - self.position <= MAX_SELECTED_VALUE_BYTES,
                        "a complete selected Scanner outcome exceeds its safe bound")
                if not self.fill():
                    raise OverviewError("a complete Scanner JSON value is missing") from error
                continue
            self.position = ending
            return result

    def skip(self) -> None:
        self.whitespace()
        first = self.peek()
        require(first is not None, "an unselected Scanner JSON value was truncated")
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
                    require(bool(stack) and stack[-1] == item,
                            "an unselected Scanner JSON container was corrupted")
                    stack.pop()
                    if not stack:
                        return
                self.compact()
        else:
            start = self.position
            while True:
                item = self.peek()
                if item is None or item in (",", "}", "]", " ", "\t", "\r", "\n"):
                    break
                self.position += 1
            raw = self.buffer[start:self.position]
            try:
                _, ending = self.decoder.raw_decode(raw)
            except json.JSONDecodeError as error:
                raise OverviewError("an unselected Scanner JSON scalar is invalid") from error
            require(ending == len(raw),
                    "an unselected Scanner JSON scalar was corrupted")

    def select(self, fields: frozenset[str]) -> dict[str, Any]:
        require(type(fields) is frozenset and bool(fields),
                "an exact complete Scanner evidence schema is mandatory")
        self.literal("{")
        found: set[str] = set()
        selected: dict[str, Any] = {}
        self.whitespace()
        if self.peek() == "}":
            self.take()
        else:
            while True:
                key = self.value()
                require(type(key) is str and key not in found,
                        "a full Scanner report field was duplicated")
                found.add(key)
                self.literal(":")
                if key in fields:
                    selected[key] = self.value()
                else:
                    self.skip()
                self.whitespace()
                ending = self.take()
                if ending == "}":
                    break
                require(ending == ",",
                        "a complete Scanner JSON separator was substituted")
        self.whitespace()
        require(self.peek() is None,
                "a complete Scanner report gained a hidden JSON suffix")
        require(found == fields and set(selected) == fields,
                "a complete Scanner report field was hidden or injected")
        return selected


def read_archive(
    relative: str, archive_hash: str, fields: frozenset[str],
    report_hash: str, report_bytes: int,
) -> dict[str, Any]:
    with open_owned(relative, MAX_ARCHIVE_BYTES) as (descriptor, info):
        stream = VerifiedGzipReader(
            descriptor, info.st_size, archive_hash, report_bytes, report_hash,
        )
        result = StreamingObject(stream).select(fields)
        require(stream.finished,
                "the complete Scanner report was not fully authenticated")
        return result


Loader = Callable[[str, str, str, str | None, int | None], dict[str, Any]]


def actual_loader(
    relative: str, expected: str, kind: str,
    original_hash: str | None, original_bytes: int | None,
) -> dict[str, Any]:
    parts = safe_parts(relative)
    require(len(parts) == 3
            and parts[:2] == ("experiments", "rust_public_practice_v1"),
            "the Scanner chart can access only exact correctness evidence")
    if kind == "receipt":
        require(relative.endswith("-publication-receipt.json")
                and original_hash is None and original_bytes is None,
                "only an exact source-pinned durable receipt may be read")
        return decode_document(
            read_frozen(relative, expected, MAX_RECEIPT_BYTES), relative,
        )
    require(kind in {"baseline", "candidate"}
            and relative.endswith(".json.gz")
            and type(original_hash) is str and type(original_bytes) is int,
            "only an exactly pinned, lossless Scanner gzip may be read")
    return read_archive(
        relative, expected,
        BASELINE_FIELDS if kind == "baseline" else CANDIDATE_FIELDS,
        original_hash, original_bytes,
    )


def manifest_rows(
    manifest: Any, loader: Loader,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(type(manifest) is dict and set(manifest) == {
        "schema", "python", "case_denominator", "oracle_source_sha256",
        "recorder_source_sha256", "ownership_audit_sha256",
        "original_v5_sha256", "matrix_sha256", "published_seed",
        "baseline", "families",
    }, "the exact separately frozen 2,854-case Scanner graph manifest is mandatory")
    fixed_fields(manifest, {
        "schema": SCHEMA + "-inputs",
        "python": "3.14.6",
        "case_denominator": CASE_COUNT,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_source_sha256": RECORDER_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
    }, "the separately frozen Scanner graph and its exact 64-bit seed")
    matrix = frozen_matrix()
    seen: set[str] = set()
    base = manifest.get("baseline")
    require(type(base) is dict and set(base) == {"label", "archive", "receipt"},
            "the pinned independently observed Scanner baseline is mandatory")
    label = validate_label(base.get("label"))
    receipt_path, receipt_hash = evidence_pin(base["receipt"], seen)
    archive_path, archive_hash = evidence_pin(base["archive"], seen)
    require((archive_path, receipt_path) == approved_paths(label),
            "the passing Scanner baseline was silently substituted")
    receipt = validate_baseline_receipt(
        loader(receipt_path, receipt_hash, "receipt", None, None),
        label, archive_path, archive_hash, receipt_path,
    )
    original = validate_baseline(
        loader(
            archive_path, archive_hash, "baseline",
            receipt["report_uncompressed_sha256"],
            receipt["report_uncompressed_bytes"],
        ),
        matrix, receipt,
    )
    baseline = {
        "label": label,
        "archive_relative": archive_path,
        "archive_sha256": archive_hash,
        "receipt_relative": receipt_path,
        "receipt_sha256": receipt_hash,
        "records_sha256": receipt["baseline_records_sha256"],
        "reference_pids": receipt["baseline_reference_pids"],
    }
    zero_kinds = {name: 0 for name in EXPECTED_COUNTS}
    zero_cohorts = {"semantic": 0, "tokenizer": 0}
    rows: list[dict[str, Any]] = [{
        "family": "python",
        "label": "Python baseline",
        "state": "RUN",
        "case_denominator": CASE_COUNT,
        "passed": CASE_COUNT,
        "failed": 0,
        "not_measured": 0,
        "mismatches_by_expected_kind": zero_kinds,
        "mismatches_by_cohort": zero_cohorts,
    }]
    families = manifest.get("families")
    require(type(families) is list and len(families) == len(FAMILY_ORDER),
            "all three independently written Scanner engines are mandatory")
    for family, item in zip(FAMILY_ORDER, families, strict=True):
        require(type(item) is dict and set(item) == {
            "family", "candidate_source_sha256", "state",
            "report", "receipt", "superseded",
        } and item.get("family") == family,
                "an independently written Scanner engine was hidden or reordered")
        source = valid_hash(item.get("candidate_source_sha256"), family)
        state = item.get("state")
        require(state in {"RUN", "NOT MEASURED"}
                and type(item.get("superseded")) is list,
                "an unmeasured or historical Scanner run was misclassified")
        historical: list[dict[str, Any]] = []
        for older in item["superseded"]:
            require(type(older) is dict and set(older) == {"report", "receipt"},
                    "a complete historical Scanner report pair was hidden")
            old_receipt_path, old_receipt_hash = evidence_pin(older["receipt"], seen)
            old_report_path, old_report_hash = evidence_pin(older["report"], seen)
            old = loader(old_receipt_path, old_receipt_hash, "receipt", None, None)
            require(type(old) is dict and old.get("candidate_family") == family,
                    "a historical Scanner result was taken from another engine")
            old_source = valid_hash(old.get("candidate_source_sha256"),
                                    "historical Scanner adapter")
            valid_old = validate_candidate_receipt(
                old, family, old_source, baseline,
                old_report_path, old_report_hash, old_receipt_path,
            )
            old_report = loader(
                old_report_path, old_report_hash, "candidate",
                valid_old["report_uncompressed_sha256"],
                valid_old["report_uncompressed_bytes"],
            )
            result = validate_candidate(old_report, valid_old, baseline, matrix, original)
            historical.append({
                "report": {"relative": old_report_path, "sha256": old_report_hash},
                "receipt": {"relative": old_receipt_path,
                            "sha256": old_receipt_hash},
                "candidate_source_sha256": old_source,
                "passed": result["passed"],
                "failed": result["failed"],
                "mismatches_by_expected_kind": result["mismatches_by_expected_kind"],
                "mismatches_by_cohort": result["mismatches_by_cohort"],
            })
        row: dict[str, Any] = {
            "family": family,
            "label": FAMILY_LABELS[family],
            "candidate_source_sha256": source,
            "state": state,
            "case_denominator": CASE_COUNT,
            "superseded": historical,
        }
        if state == "NOT MEASURED":
            require(item["report"] is None and item["receipt"] is None,
                    "an unmeasured Scanner engine cannot claim a current result")
            row.update({
                "passed": 0,
                "failed": 0,
                "not_measured": CASE_COUNT,
                "report": None,
                "receipt": None,
                "mismatches_by_expected_kind": None,
                "mismatches_by_cohort": None,
            })
        else:
            report_path, report_hash = evidence_pin(item["report"], seen)
            actual_receipt_path, actual_receipt_hash = evidence_pin(
                item["receipt"], seen,
            )
            candidate_receipt = validate_candidate_receipt(
                loader(actual_receipt_path, actual_receipt_hash,
                       "receipt", None, None),
                family, source, baseline, report_path, report_hash,
                actual_receipt_path,
            )
            report = loader(
                report_path, report_hash, "candidate",
                candidate_receipt["report_uncompressed_sha256"],
                candidate_receipt["report_uncompressed_bytes"],
            )
            row.update(validate_candidate(report, candidate_receipt,
                                          baseline, matrix, original))
            row["report"] = {"relative": report_path, "sha256": report_hash}
            row["receipt"] = {
                "relative": actual_receipt_path,
                "sha256": actual_receipt_hash,
            }
        require(all(type(row[name]) is int and row[name] >= 0
                    for name in ("passed", "failed", "not_measured"))
                and row["passed"] + row["failed"] + row["not_measured"]
                == CASE_COUNT,
                "a Scanner engine silently changed its 2,854-case denominator")
        rows.append(row)
    return baseline, rows


def escape_xml(value: str) -> str:
    require(type(value) is str, "all Scanner graph text must be safely escaped")
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def make_svg(rows: list[dict[str, Any]], source: str, manifest: str) -> bytes:
    require(type(rows) is list and len(rows) == 4,
            "show Python and all three independently written Scanner engines")
    colors = (
        ("passed", "#15803d", "Matches Python"),
        ("failed", "#dc2626", "Does not match Python"),
        ("not_measured", "#94a3b8", "Not yet measured"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="550" '
        'viewBox="0 0 1120 550" role="img" aria-labelledby="scanner-title scanner-desc">',
        '<title id="scanner-title">Extra Python Scanner compatibility checks</title>',
        '<desc id="scanner-desc">Python, Rust, C, and Zig are compared with '
        'the same separately frozen 2,854 original Python Scanner checks. '
        'Green matches Python; red does not; gray has not yet been measured. '
        'This graph contains no speed result or hidden benchmark.</desc>',
        '<rect width="1120" height="550" rx="18" fill="#f8fafc"/>',
        '<text x="42" y="53" fill="#0f172a" '
        'font-family="system-ui,sans-serif" font-size="26" font-weight="700">'
        'Extra Python Scanner compatibility</text>',
        '<text x="42" y="82" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="15">'
        'The same 2,854 extra Python checks for every engine '
        '&#183; speed not measured</text>',
    ]
    for index, (_, color, label) in enumerate(colors):
        x = 43 + index * 247
        parts.append(
            f'<rect x="{x}" y="104" width="14" height="14" rx="3" '
            f'fill="{color}"/><text x="{x + 22}" y="116" fill="#334155" '
            'font-family="system-ui,sans-serif" font-size="13">'
            f'{escape_xml(label)}</text>'
        )
    for index, row in enumerate(rows):
        top = 151 + index * 78
        label = escape_xml(row["label"])
        if row["not_measured"]:
            caption = "NOT MEASURED"
            caption_color = "#64748b"
        else:
            caption = f'{row["passed"]:,} / {CASE_COUNT:,} match Python'
            caption_color = "#dc2626" if row["failed"] else "#15803d"
        parts.append(
            f'<text x="43" y="{top + 17}" fill="#0f172a" '
            'font-family="system-ui,sans-serif" font-size="17" '
            f'font-weight="700">{label}</text>'
        )
        parts.append(
            f'<text x="1038" y="{top + 17}" fill="{caption_color}" '
            'text-anchor="end" font-family="system-ui,sans-serif" '
            f'font-size="14" font-weight="600">{escape_xml(caption)}</text>'
        )
        parts.append(
            f'<rect x="43" y="{top + 27}" width="996" height="24" '
            'rx="6" fill="#e2e8f0"/>'
        )
        cumulative = 0
        for field, color, meaning in colors:
            start = 43 + cumulative * 996 // CASE_COUNT
            cumulative += row[field]
            end = 43 + cumulative * 996 // CASE_COUNT
            if end > start:
                parts.append(
                    f'<rect x="{start}" y="{top + 27}" width="{end-start}" '
                    f'height="24" fill="{color}"><title>{label}: '
                    f'{row[field]:,} {escape_xml(meaning.lower())} out of '
                    f'{CASE_COUNT:,}</title></rect>'
                )
    parts.extend((
        '<text x="43" y="474" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="12">'
        'These are 2,854 separately frozen Scanner checks. They do not change '
        'the original 2,807 checks or the 1,024 memory-safety checks.</text>',
        '<text x="43" y="494" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="12">'
        'All failures and older results remain in the complete evidence. '
        'Final speed and the expanded holdout remain not measured.</text>',
        f'<text x="43" y="524" fill="#64748b" '
        f'font-family="system-ui,sans-serif" font-size="10">'
        f'Manifest SHA-256: {manifest} '
        f'&#183; renderer SHA-256: {source}</text>',
        "</svg>\n",
    ))
    return "\n".join(parts).encode("utf-8")


def build_documents(
    manifest: Mapping[str, Any], source: str, manifest_hash: str, loader: Loader,
) -> tuple[bytes, bytes]:
    source = valid_hash(source, "frozen Scanner graph renderer")
    manifest_hash = valid_hash(manifest_hash, "frozen Scanner graph manifest")
    baseline, rows = manifest_rows(manifest, loader)
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
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_denominator": CASE_COUNT,
        "semantic_case_denominator": SEMANTIC_CASE_COUNT,
        "tokenizer_case_denominator": TOKENIZER_CASE_COUNT,
        "independent_of_original_2807_case_denominator": True,
        "independent_of_memory_1024_case_denominator": True,
        "baseline": baseline,
        "families": rows,
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
    return svg, canonical(summary)


def existing_output(directory: int, basename: str) -> tuple[bytes, os.stat_result] | None:
    require(basename in {
        safe_parts(SVG_RELATIVE)[-1], safe_parts(SUMMARY_RELATIVE)[-1],
    }, "only the exact Scanner graph and summary can be inspected")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = os.open(basename, flags, dir_fd=directory)
    except FileNotFoundError:
        return None
    try:
        info = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(info.st_mode)
                and (info.st_dev, info.st_ino, info.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < info.st_size <= MAX_SOURCE_BYTES,
                "the existing exact Scanner graph was replaced or oversized")
        left = info.st_size
        blocks: list[bytes] = []
        while left:
            block = os.read(descriptor, min(left, CHUNK_BYTES))
            require(type(block) is bytes and bool(block),
                    "the existing exact Scanner graph was truncated")
            left -= len(block)
            blocks.append(block)
        require(os.read(descriptor, 1) == b"",
                "the existing exact Scanner graph gained a hidden suffix")
        final = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((info.st_dev, info.st_ino, info.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                == (named.st_dev, named.st_ino, named.st_size),
                "the existing Scanner graph changed while being authenticated")
        return b"".join(blocks), info
    finally:
        os.close(descriptor)


def validate_refresh(
    existing_svg: bytes | None, existing_summary: bytes | None,
    svg: bytes, summary: bytes, replace: bool,
    previous_svg: str | None, previous_summary: str | None,
) -> bool:
    require(type(svg) is bytes and type(summary) is bytes
            and 0 < len(svg) <= MAX_SOURCE_BYTES
            and 0 < len(summary) <= MAX_SOURCE_BYTES,
            "exact bounded Scanner graph and summary bytes are mandatory")
    if not replace:
        require(previous_svg is None and previous_summary is None,
                "refresh pins require an explicit graph replacement")
        require(existing_svg is None or existing_svg == svg,
                "refusing to overwrite different existing Scanner graph bytes")
        require(existing_summary is None or existing_summary == summary,
                "refusing to overwrite a different existing Scanner summary")
        return False
    require(type(replace) is bool and replace is True,
            "graph replacement must be expressly authorized")
    expected_svg = valid_hash(previous_svg, "previous exact Scanner graph")
    expected_summary = valid_hash(previous_summary, "previous exact Scanner summary")
    require(type(existing_svg) is bytes and type(existing_summary) is bytes,
            "authenticate both complete old graph files before replacing either")
    require(hashlib.sha256(existing_svg).hexdigest() == expected_svg
            and hashlib.sha256(existing_summary).hexdigest() == expected_summary,
            "the explicitly pinned previous Scanner graph pair was substituted")
    return existing_svg != svg or existing_summary != summary


def atomic_output(
    directory: int, basename: str, value: bytes,
    previous_info: os.stat_result | None, *, replace: bool,
) -> None:
    require(basename in {
        safe_parts(SVG_RELATIVE)[-1], safe_parts(SUMMARY_RELATIVE)[-1],
    } and type(value) is bytes and 0 < len(value) <= MAX_SOURCE_BYTES,
            "only the exact Scanner graph and summary may be published")
    previous = existing_output(directory, basename)
    if previous is not None and previous[0] == value:
        return
    if previous is not None:
        require(replace and previous_info is not None
                and (previous[1].st_dev, previous[1].st_ino, previous[1].st_size)
                == (previous_info.st_dev, previous_info.st_ino,
                    previous_info.st_size),
                "refusing to overwrite an unauthenticated existing Scanner graph")
    else:
        require(previous_info is None,
                "the authenticated old Scanner graph disappeared")
    temporary = (
        ".rebar-scanner-verbose-overview-v1-" + basename + "-"
        + str(os.getpid()) + "-" + hashlib.sha256(value).hexdigest()[:16]
    )
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    published = False
    original = os.fstat(descriptor)
    try:
        require(stat.S_ISREG(original.st_mode),
                "the Scanner graph temporary must be an exact regular file")
        offset = 0
        while offset < len(value):
            written = os.write(descriptor, value[offset:])
            require(type(written) is int and written > 0,
                    "the complete Scanner graph was not fully written")
            offset += written
        os.fsync(descriptor)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino, named.st_size)
                == (original.st_dev, original.st_ino, len(value)),
                "the independently generated Scanner graph was substituted")
        if previous is None:
            os.link(temporary, basename, src_dir_fd=directory,
                    dst_dir_fd=directory, follow_symlinks=False)
            published = True
            os.fsync(directory)
            destination = os.stat(basename, dir_fd=directory, follow_symlinks=False)
            require((destination.st_dev, destination.st_ino, destination.st_size)
                    == (original.st_dev, original.st_ino, len(value)),
                    "the no-clobber Scanner graph publication was substituted")
            os.unlink(temporary, dir_fd=directory)
        else:
            current = os.stat(basename, dir_fd=directory, follow_symlinks=False)
            require((current.st_dev, current.st_ino, current.st_size)
                    == (previous_info.st_dev, previous_info.st_ino,
                        previous_info.st_size),
                    "the authenticated Scanner graph changed before replacement")
            os.replace(temporary, basename,
                       src_dir_fd=directory, dst_dir_fd=directory)
            published = True
            destination = os.stat(basename, dir_fd=directory, follow_symlinks=False)
            require((destination.st_dev, destination.st_ino, destination.st_size)
                    == (original.st_dev, original.st_ino, len(value)),
                    "the explicitly replaced Scanner graph was substituted")
        os.fsync(directory)
    except BaseException:
        if not published:
            try:
                named = os.stat(temporary, dir_fd=directory,
                                follow_symlinks=False)
                if (named.st_dev, named.st_ino) == (original.st_dev, original.st_ino):
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, OverviewError):
                pass
        raise
    finally:
        os.close(descriptor)


def render(
    source: str, manifest_relative: str, manifest_hash: str,
    *, replace: bool = False, previous_svg: str | None = None,
    previous_summary: str | None = None,
) -> dict[str, Any]:
    verify_runtime()
    source = valid_hash(source, "explicitly frozen Scanner graph source")
    manifest_hash = valid_hash(manifest_hash, "explicitly frozen Scanner graph manifest")
    require(manifest_relative == MANIFEST_RELATIVE,
            "only the exact separate Scanner graph manifest may be rendered")
    for relative, pinned in (
        (SOURCE_RELATIVE, source),
        (ORACLE_RELATIVE, ORACLE_SHA256),
        (RECORDER_RELATIVE, RECORDER_SHA256),
        (AUDIT_RELATIVE, AUDIT_SHA256),
        (V5_RELATIVE, V5_SHA256),
        (V2_RELATIVE, V2_SHA256),
    ):
        read_frozen(relative, pinned, MAX_SOURCE_BYTES)
    manifest = decode_document(
        read_frozen(MANIFEST_RELATIVE, manifest_hash, MAX_SOURCE_BYTES),
        "the independently frozen Scanner graph manifest", MAX_SOURCE_BYTES,
    )
    svg, summary = build_documents(manifest, source, manifest_hash, actual_loader)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    )
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        for part in ("docs", "evidence"):
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the exact Scanner chart parent became a symlink")
        svg_name = safe_parts(SVG_RELATIVE)[-1]
        summary_name = safe_parts(SUMMARY_RELATIVE)[-1]
        old_svg = existing_output(current, svg_name)
        old_summary = existing_output(current, summary_name)
        changed = validate_refresh(
            old_svg[0] if old_svg is not None else None,
            old_summary[0] if old_summary is not None else None,
            svg, summary, replace, previous_svg, previous_summary,
        )
        atomic_output(current, svg_name, svg,
                      old_svg[1] if old_svg is not None else None,
                      replace=replace)
        atomic_output(current, summary_name, summary,
                      old_summary[1] if old_summary is not None else None,
                      replace=replace)
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)
    verify_runtime()
    result = decode_document(summary, "the complete generated Scanner summary",
                             MAX_SOURCE_BYTES)
    return {
        "schema": SCHEMA + "-rendered",
        "status": "PASS",
        "source_sha256": source,
        "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "summary_relative": SUMMARY_RELATIVE,
        "summary_sha256": hashlib.sha256(summary).hexdigest(),
        "case_denominator": CASE_COUNT,
        "published_seed": PUBLISHED_SEED,
        "replaced_generated_pair": changed,
        "rows": [{
            "family": row["family"],
            "passed": row["passed"],
            "failed": row["failed"],
            "not_measured": row["not_measured"],
        } for row in result["families"]],
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
    """Block genuine files, processes, engines, timing, and graph publication."""

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
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)
        self.originals.append((owner, name, original))

        def denied(*args: Any, **kwargs: Any) -> Any:
            actual = category
            if category == "reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(char in mode for char in "wax+"):
                    actual = "writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT
                    | os.O_TRUNC | os.O_APPEND
                ):
                    actual = "writes"
            self.blocked[actual] += 1
            raise SourceOnlyError(
                "source-only Scanner graph controls forbid " + actual
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

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_stream(
    raw: bytes, *, archive: bytes | None = None,
    archive_sha256: str | None = None, original_sha256: str | None = None,
    original_bytes: int | None = None,
    fields: frozenset[str] = frozenset({"proof", "value"}),
) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw),
            "complete exclusively in-memory Scanner gzip controls are mandatory")
    if archive is None:
        compressor = zlib.compressobj(level=9, wbits=16 + zlib.MAX_WBITS)
        archive = compressor.compress(raw) + compressor.flush()
    require(type(archive) is bytes and bool(archive),
            "an exclusively in-memory Scanner gzip member is mandatory")
    compressed_hash = (hashlib.sha256(archive).hexdigest()
                       if archive_sha256 is None else archive_sha256)
    plain_hash = (hashlib.sha256(raw).hexdigest()
                  if original_sha256 is None else original_sha256)
    plain_count = len(raw) if original_bytes is None else original_bytes
    descriptor = -2_854_031
    position = 0
    previous = os.read

    def read_memory(selected: int, requested: int) -> bytes:
        nonlocal position
        require(selected == descriptor and type(requested) is int and requested > 0,
                "a synthetic Scanner stream attempted an actual descriptor")
        block = archive[position:position + requested]
        position += len(block)
        return block

    os.read = read_memory
    try:
        stream = VerifiedGzipReader(
            descriptor, len(archive), compressed_hash, plain_count, plain_hash,
        )
        value = StreamingObject(stream).select(fields)
        require(stream.finished and position == len(archive),
                "the in-memory Scanner gzip was not completely authenticated")
        return value
    finally:
        os.read = previous


def synthetic_owner(relative: str, source: str, number: int,
                    *, external: bool = False) -> dict[str, Any]:
    return {
        "path" if external else "relative": relative,
        "sha256": source,
        "bytes": 4_096 + number,
        "device": 7,
        "inode": 80_000 + number,
    }


def synthetic_tool_closure() -> dict[str, Any]:
    return {
        "recorder": synthetic_owner(RECORDER_RELATIVE, RECORDER_SHA256, 1),
        "scanner_oracle": synthetic_owner(ORACLE_RELATIVE, ORACLE_SHA256, 2),
        "original_v5": synthetic_owner(V5_RELATIVE, V5_SHA256, 3),
        "from_scratch_audit_v3": synthetic_owner(AUDIT_RELATIVE, AUDIT_SHA256, 4),
    }


def synthetic_standard_owners() -> dict[str, Any]:
    result = {
        "oracle": synthetic_owner(ROOT + "/" + ORACLE_RELATIVE,
                                  ORACLE_SHA256, 10, external=True),
        "python": synthetic_owner(PINNED_PYTHON, PINNED_PYTHON_SHA256,
                                  11, external=True),
    }
    for number, (name, (filename, source)) in enumerate(
        PINNED_STDLIB_SOURCES.items(), start=12,
    ):
        result[name] = synthetic_owner(
            PINNED_STDLIB_DIRECTORY + filename, source, number, external=True,
        )
    return result


def synthetic_normalized(value: str | bytes) -> dict[str, Any]:
    return encode_subject(value)


def synthetic_pattern(domain: str) -> dict[str, Any]:
    pattern: str | bytes = "synthetic combined pattern"
    if domain == "bytes":
        pattern = pattern.encode("ascii")
    return {
        "kind": "compiled-pattern",
        "pattern": synthetic_normalized(pattern),
        "flags": 0,
        "groups": 0,
        "groupindex": {"kind": "mapping", "items": []},
    }


def synthetic_callback(
    subject: str | bytes, token: str | bytes, pattern: Mapping[str, Any],
    branch: int, start: int,
) -> dict[str, Any]:
    match = {
        "kind": "match",
        "pattern": dict(pattern),
        "string": synthetic_normalized(subject),
        "group": synthetic_normalized(token),
        "groups": [],
        "spans": [[start, start + len(token)]],
        "groupdict": {"kind": "mapping", "items": []},
        "lastindex": None,
        "lastgroup": None,
        "pos": 0,
        "endpos": len(subject),
    }
    return {
        "branch": branch,
        "token": synthetic_normalized(token),
        "match": match,
        "combined_pattern": dict(pattern),
        "match_uses_combined_pattern": True,
    }


def synthetic_outcome(case: Mapping[str, Any]) -> dict[str, Any]:
    subject = decode_subject(case["subject"], case["domain"])
    expected = case["expected_kind"]
    if expected == "continued-comment-unterminated":
        return {
            "status": "raise",
            "exception": {
                "kind": "public-regex-error",
                "type": "PatternError",
                "args": {"kind": "tuple", "items": [
                    {"kind": "str", "value": "synthetic unterminated comment"},
                ]},
                "message": "synthetic unterminated comment",
                "pattern": synthetic_normalized(subject[:0]),
                "position": 0,
                "line": 1,
                "column": 1,
            },
            "callbacks": [],
            "warnings": [],
            "combined_pattern": None,
        }
    pattern = synthetic_pattern(case["domain"])
    if expected == "continued-comment-empty":
        callbacks: list[dict[str, Any]] = []
        tokens: list[dict[str, Any]] = []
        remainder = synthetic_normalized(subject)
    elif expected == "full-match":
        callbacks = [synthetic_callback(subject, subject, pattern, 0, 0)]
        tokens = [synthetic_normalized(subject)]
        remainder = synthetic_normalized(subject[:0])
    else:
        callbacks = [
            synthetic_callback(subject, subject[:1], pattern, 0, 0),
            synthetic_callback(subject, subject[1:], pattern, 1, 1),
        ]
        tokens = [synthetic_normalized(subject[:1]),
                  synthetic_normalized(subject[1:])]
        remainder = synthetic_normalized(subject[:0])
    return {
        "status": "return",
        "value": {"kind": "tuple", "items": [
            {"kind": "list", "items": tokens}, remainder,
        ]},
        "callbacks": callbacks,
        "warnings": [],
        "combined_pattern": pattern,
    }


def synthetic_guard(family: str) -> dict[str, Any]:
    ffi = FAMILY_SPECS[family][4]
    value = {name: True for name in GUARD_TRUE}
    value.update({
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "owned_native_ffi_allowed": ffi,
        "trusted_stdlib_ctypes_preloaded": ffi,
        "trusted_stdlib_ctypes_builtin_verified": ffi,
        "trusted_stdlib_ctypes_pythonapi_initialized": ffi,
        "trusted_stdlib_ctypes_source_sha256":
            TRUSTED_CTYPES_SHA256 if ffi else None,
        "cached_original_matcher_descendant_count": 0,
        "cached_original_holder_count": 0,
        "owned_ctypes_load_count": 1 if ffi else 0,
        "owned_ctypes_symbol_count": 2 if ffi else 0,
    })
    return value


def synthetic_family_closure(
    family: str, adapter: str, engine: str, bridge: str,
) -> dict[str, Any]:
    adapter_path, engine_path, bridge_path, source_paths, _ = FAMILY_SPECS[family]
    source_map = {
        path: adapter if path == adapter_path
        else hashlib.sha256((family + ":" + path).encode("ascii")).hexdigest()
        for path in source_paths
    }
    native_map = {engine_path: engine}
    if bridge_path != engine_path:
        native_map[bridge_path] = bridge
    manifest = {
        "family": family,
        "candidate_source_sha256": adapter,
        "native_engine_sha256": engine,
        "native_bridge_sha256": bridge,
        "source_sha256": dict(sorted(source_map.items())),
        "native_sha256": dict(sorted(native_map.items())),
        "immutable_policy_sha256": {
            V2_RELATIVE: V2_SHA256,
            V5_RELATIVE: V5_SHA256,
        },
    }
    source_owners = {
        path: synthetic_owner(path, source, 100 + number)
        for number, (path, source) in enumerate(manifest["source_sha256"].items())
    }
    native_owners = {
        path: synthetic_owner(path, source, 200 + number)
        for number, (path, source) in enumerate(manifest["native_sha256"].items())
    }
    return {
        "family": family,
        "manifest": manifest,
        "source_owners": source_owners,
        "native_owners": native_owners,
        "policy_owners": {
            V2_RELATIVE: synthetic_owner(V2_RELATIVE, V2_SHA256, 301),
            V5_RELATIVE: synthetic_owner(V5_RELATIVE, V5_SHA256, 302),
        },
        "oracle_owner": synthetic_owner(AUDIT_RELATIVE, AUDIT_SHA256, 303),
        "python_owner": synthetic_owner(
            PINNED_PYTHON, PINNED_PYTHON_SHA256, 304, external=True,
        ),
    }


def synthetic_reference(
    role: str, pid: int, records: list[dict[str, Any]], records_hash: str,
    owners: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": ORACLE_SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": pid,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": EXPECTED_COUNTS,
        "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
        "records_sha256": records_hash,
        "records": records,
        "source_owners": dict(owners),
        "reference_guard": {
            "candidate_import_count": 0,
            "external_regex_import_count": 0,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "required_method_guard_checks": 2 * CASE_COUNT,
            "future_candidate_guard_relative": V5_RELATIVE,
            "future_candidate_guard_sha256": V5_SHA256,
            "future_ownership_audit_relative": AUDIT_RELATIVE,
            "future_ownership_audit_sha256": AUDIT_SHA256,
            "future_candidate_guard_installed": False,
        },
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def synthetic_process(worker: Mapping[str, Any], role: str) -> dict[str, Any]:
    return {
        "role": role,
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": capture_stream(canonical(dict(worker))),
        "stderr": capture_stream(b""),
    }


def synthetic_fixtures() -> tuple[
    dict[str, Any], dict[tuple[str, str], dict[str, Any]],
]:
    matrix = frozen_matrix()
    records = [{
        "case": row["case"],
        "cohort": row["cohort"],
        "expected_kind": row["expected_kind"],
        "outcome": synthetic_outcome(row),
    } for row in matrix]
    records_hash = digest(records)
    label = "synthetic-v1"
    archive_path, receipt_path = approved_paths(label)
    archive_hash = "12" * 32
    receipt_hash = "34" * 32
    tool_owners = synthetic_tool_closure()
    standard_owners = synthetic_standard_owners()
    first = synthetic_reference("reference_a", 82, records, records_hash,
                                standard_owners)
    second = synthetic_reference("reference_b", 83, records, records_hash,
                                 standard_owners)
    first_process = synthetic_process(first, "reference_a")
    second_process = synthetic_process(second, "reference_b")
    result = {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": EXPECTED_COUNTS,
        "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
        "baseline_records_sha256": records_hash,
        "source_owners": standard_owners,
        "reference_a": first,
        "reference_b": second,
        "reference_a_process": first_process,
        "reference_b_process": second_process,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    report = {
        "schema": RECORDER_SCHEMA + "-complete-baseline-report",
        "status": "PASS",
        **source_fields(label),
        "source_closure_before": tool_owners,
        "source_closure_after": tool_owners,
        "source_closure_unchanged": True,
        "complete_baseline_process_stdout": capture_stream(canonical(result)),
        "complete_baseline_process_stderr": capture_stream(b""),
        "complete_decoded_baseline_process": result,
        "complete_baseline_result": result,
        "complete_structured_baseline_failure": None,
        "complete_reference_worker_failure": None,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_records_sha256": records_hash,
        "baseline_reference_pids": [82, 83],
        "reference_a_records": records,
        "reference_b_records": records,
        "reference_a_process": first_process,
        "reference_b_process": second_process,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "actual_baseline_controller_pid": 81,
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
    }
    plain = canonical(report)
    base_receipt = {
        "schema": RECORDER_SCHEMA + "-durable-baseline-publication-receipt",
        "status": "PASS",
        "baseline_result_status": "PASS",
        **source_fields(label),
        "baseline_records_sha256": records_hash,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_reference_pids": [82, 83],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "source_closure_before": tool_owners,
        "source_closure_after": tool_owners,
        "source_closure_unchanged": True,
        "report_relative": archive_path,
        "report_sha256": archive_hash,
        "report_bytes": 4_096,
        "report_uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "report_uncompressed_bytes": len(plain),
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_path,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_baseline": True,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    evidence: dict[tuple[str, str], dict[str, Any]] = {
        (archive_path, archive_hash): report,
        (receipt_path, receipt_hash): base_receipt,
    }
    baseline = {
        "label": label,
        "archive_relative": archive_path,
        "archive_sha256": archive_hash,
        "receipt_relative": receipt_path,
        "receipt_sha256": receipt_hash,
        "records_sha256": records_hash,
        "reference_pids": [82, 83],
    }

    def add_candidate(
        family: str, run_label: str, source: str, failure_count: int,
        archive_digest: str, receipt_digest: str,
    ) -> tuple[dict[str, str], dict[str, str]]:
        engine = hashlib.sha256((family + ":engine:" + run_label).encode()).hexdigest()
        bridge = (engine if family == "c" else
                  hashlib.sha256((family + ":bridge:" + run_label).encode()).hexdigest())
        closure = synthetic_family_closure(family, source, engine, bridge)
        changed: list[dict[str, Any]] = []
        mismatches: list[dict[str, Any]] = []
        kinds = {name: 0 for name in EXPECTED_COUNTS}
        cohorts = {"semantic": 0, "tokenizer": 0}
        for index, (case, standard) in enumerate(zip(matrix, records, strict=True)):
            observed = dict(standard)
            if index < failure_count:
                actual = copy.deepcopy(standard["outcome"])
                if actual["status"] == "raise":
                    actual["exception"]["message"] = "synthetic incompatible error"
                else:
                    actual["combined_pattern"]["flags"] = 128
                observed["outcome"] = actual
                kinds[case["expected_kind"]] += 1
                cohorts[case["cohort"]] += 1
                mismatches.append({
                    "case": case["case"],
                    "cohort": case["cohort"],
                    "expected_kind": case["expected_kind"],
                    "input": case,
                    "baseline_outcome": standard["outcome"],
                    "candidate_outcome": actual,
                })
            changed.append(observed)
        actual_hash = digest(changed)
        guard = synthetic_guard(family)
        report_path, receipt_path = approved_paths(run_label, family)
        adapter_path, engine_path, bridge_path, _, _ = FAMILY_SPECS[family]
        worker = {
            "schema": RECORDER_SCHEMA + "-isolated-candidate-worker",
            "status": "OBSERVED",
            "python": "3.14.6",
            "role": "candidate-" + family,
            "pid": {"rust": 101, "c": 102, "zig": 103}[family],
            "candidate_family": family,
            **source_fields(label),
            "baseline_receipt_relative": baseline["receipt_relative"],
            "baseline_receipt_sha256": baseline["receipt_sha256"],
            "baseline_archive_relative": baseline["archive_relative"],
            "baseline_archive_sha256": baseline["archive_sha256"],
            "baseline_records_sha256": baseline["records_sha256"],
            "baseline_reference_pids": baseline["reference_pids"],
            "baseline_receipt_owner": synthetic_owner(
                baseline["receipt_relative"], baseline["receipt_sha256"], 401,
            ),
            "baseline_archive_owner": synthetic_owner(
                baseline["archive_relative"], baseline["archive_sha256"], 402,
            ),
            "source_provenance": synthetic_tool_closure(),
            "audit_manifest": closure["manifest"],
            "owned_source_closure": closure,
            "native_provenance": {
                "source": closure["source_owners"][adapter_path],
                "native_engine": closure["native_owners"][engine_path],
                "native_bridge": closure["native_owners"][bridge_path],
            },
            "matcher_guard": guard,
            "records_sha256": actual_hash,
            "records": changed,
            "validated_prior_reference_workers": 2,
            "actual_reference_workers": 0,
            "actual_candidate_workers": 1,
            "actual_candidate_imports": 3,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        reasons = ([] if not failure_count else [
            "the owned candidate differs on " + str(failure_count)
            + " frozen Scanner cases",
        ])
        report_document = {
            "schema": RECORDER_SCHEMA + "-complete-candidate-report",
            "status": "FAIL" if failure_count else "PASS",
            "python": "3.14.6",
            "label": run_label,
            "candidate_family": family,
            "candidate_source_sha256": source,
            "native_engine_sha256": engine,
            "native_bridge_sha256": bridge,
            "baseline_label": label,
            "recorder_relative": RECORDER_RELATIVE,
            "recorder_source_sha256": RECORDER_SHA256,
            "oracle_relative": ORACLE_RELATIVE,
            "oracle_source_sha256": ORACLE_SHA256,
            "original_v5_relative": V5_RELATIVE,
            "original_v5_sha256": V5_SHA256,
            "ownership_audit_relative": AUDIT_RELATIVE,
            "ownership_audit_sha256": AUDIT_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
            "case_count": CASE_COUNT,
            "semantic_case_count": SEMANTIC_CASE_COUNT,
            "tokenizer_case_count": TOKENIZER_CASE_COUNT,
            "expected_kind_counts": EXPECTED_COUNTS,
            "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
            "baseline_receipt_relative": baseline["receipt_relative"],
            "baseline_receipt_sha256": baseline["receipt_sha256"],
            "baseline_archive_relative": baseline["archive_relative"],
            "baseline_archive_sha256": baseline["archive_sha256"],
            "baseline_records_sha256": baseline["records_sha256"],
            "baseline_reference_pids": baseline["reference_pids"],
            "candidate_owner_before": closure,
            "candidate_owner_after": closure,
            "candidate_owner_unchanged": True,
            "complete_candidate_process_stdout": capture_stream(canonical(worker)),
            "complete_candidate_process_stderr": capture_stream(b""),
            "complete_decoded_candidate_process": worker,
            "complete_candidate_result": worker,
            "validated_baseline_record_count": CASE_COUNT,
            "validated_candidate_record_count": CASE_COUNT,
            "candidate_records_sha256": actual_hash,
            "baseline_records": records,
            "candidate_records": changed,
            "mismatch_count": failure_count,
            "all_mismatches": mismatches,
            "mismatches_by_expected_kind": kinds,
            "mismatches_by_cohort": cohorts,
            "all_mismatches_preserved": True,
            "matcher_guard": guard,
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
            "all_failure_reasons": reasons,
            "failure_count": len(reasons),
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        plain_report = canonical(report_document)
        candidate_receipt = {
            "schema": RECORDER_SCHEMA + "-durable-candidate-publication-receipt",
            "status": "PASS",
            "candidate_result_status": report_document["status"],
            "python": "3.14.6",
            "label": run_label,
            "candidate_family": family,
            "candidate_source_sha256": source,
            "native_engine_sha256": engine,
            "native_bridge_sha256": bridge,
            "baseline_label": label,
            "recorder_source_sha256": RECORDER_SHA256,
            "oracle_source_sha256": ORACLE_SHA256,
            "original_v5_sha256": V5_SHA256,
            "ownership_audit_sha256": AUDIT_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
            "case_count": CASE_COUNT,
            "semantic_case_count": SEMANTIC_CASE_COUNT,
            "tokenizer_case_count": TOKENIZER_CASE_COUNT,
            "expected_kind_counts": EXPECTED_COUNTS,
            "expected_pattern_error_counts": EXPECTED_NEGATIVE_COUNTS,
            "baseline_receipt_relative": baseline["receipt_relative"],
            "baseline_receipt_sha256": baseline["receipt_sha256"],
            "baseline_archive_relative": baseline["archive_relative"],
            "baseline_archive_sha256": baseline["archive_sha256"],
            "baseline_records_sha256": baseline["records_sha256"],
            "baseline_reference_pids": baseline["reference_pids"],
            "validated_baseline_record_count": CASE_COUNT,
            "validated_candidate_record_count": CASE_COUNT,
            "candidate_records_sha256": actual_hash,
            "mismatch_count": failure_count,
            "mismatches_by_expected_kind": kinds,
            "mismatches_by_cohort": cohorts,
            "all_mismatches_preserved": True,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
            "validated_prior_reference_workers": 2,
            "actual_reference_workers": 0,
            "actual_candidate_workers": 1,
            "actual_candidate_imports": 3,
            "actual_candidate_process_invocations": 1,
            "candidate_owner_before": closure,
            "candidate_owner_after": closure,
            "candidate_owner_unchanged": True,
            "report_relative": report_path,
            "report_sha256": archive_digest,
            "report_bytes": 4_096,
            "report_uncompressed_sha256": hashlib.sha256(plain_report).hexdigest(),
            "report_uncompressed_bytes": len(plain_report),
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
        evidence[(report_path, archive_digest)] = report_document
        evidence[(receipt_path, receipt_digest)] = candidate_receipt
        return (
            {"relative": report_path, "sha256": archive_digest},
            {"relative": receipt_path, "sha256": receipt_digest},
        )

    rust_source = "56" * 32
    c_source = "78" * 32
    zig_source = "9a" * 32
    rust_report, rust_receipt = add_candidate(
        "rust", "synthetic-rust-v1", rust_source, 0, "ab" * 32, "bc" * 32,
    )
    c_report, c_receipt = add_candidate(
        "c", "synthetic-c-v1", c_source, 37, "cd" * 32, "de" * 32,
    )
    historical_report, historical_receipt = add_candidate(
        "c", "synthetic-c-history-v1", "ef" * 32, 53,
        "01" * 32, "23" * 32,
    )
    manifest = {
        "schema": SCHEMA + "-inputs",
        "python": "3.14.6",
        "case_denominator": CASE_COUNT,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_source_sha256": RECORDER_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "baseline": {
            "label": label,
            "archive": {"relative": archive_path, "sha256": archive_hash},
            "receipt": {"relative": receipt_path, "sha256": receipt_hash},
        },
        "families": [
            {
                "family": "rust",
                "candidate_source_sha256": rust_source,
                "state": "RUN",
                "report": rust_report,
                "receipt": rust_receipt,
                "superseded": [],
            },
            {
                "family": "c",
                "candidate_source_sha256": c_source,
                "state": "RUN",
                "report": c_report,
                "receipt": c_receipt,
                "superseded": [{
                    "report": historical_report,
                    "receipt": historical_receipt,
                }],
            },
            {
                "family": "zig",
                "candidate_source_sha256": zig_source,
                "state": "NOT MEASURED",
                "report": None,
                "receipt": None,
                "superseded": [],
            },
        ],
    }
    return manifest, evidence


def self_test() -> dict[str, Any]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "source-only Scanner graph checks require isolated stable Python 3.14.6")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a source-only Scanner graph positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a source-only Scanner graph rejection was duplicated")
        try:
            action()
        except (OverviewError, OSError, TypeError, ValueError, KeyError,
                IndexError, OverflowError, UnicodeError, binascii.Error, zlib.error):
            rejected.append(name)
            return
        raise OverviewError("forged Scanner graph evidence was accepted: " + name)

    with SourceOnlyBoundary() as boundary:
        document = {"proof": "memory only", "value": [1, 2, 3]}
        raw = canonical(document)
        compressor = zlib.compressobj(level=9, wbits=16 + zlib.MAX_WBITS)
        archive = compressor.compress(raw) + compressor.flush()
        accept("authenticate-a-real-single-member-gzip-without-reading-a-file",
               synthetic_stream(raw, archive=archive) == document)
        for name, kwargs in (
            ("reject-a-truncated-gzip-member", {"archive": archive[:-1]}),
            ("reject-hidden-gzip-trailing-bytes", {"archive": archive + b"hidden"}),
            ("reject-a-second-gzip-member", {"archive": archive + archive}),
            ("reject-a-corrupted-gzip-footer", {
                "archive": archive[:-1] + bytes((archive[-1] ^ 1,)),
            }),
            ("reject-a-substituted-compressed-digest", {
                "archive": archive, "archive_sha256": "0" * 64,
            }),
            ("reject-a-substituted-original-digest", {
                "archive": archive, "original_sha256": "0" * 64,
            }),
            ("reject-overexpanded-original-evidence", {
                "archive": archive, "original_bytes": len(raw) - 1,
            }),
            ("reject-truncated-original-evidence", {
                "archive": archive, "original_bytes": len(raw) + 1,
            }),
        ):
            reject(name, lambda kwargs=kwargs: synthetic_stream(raw, **kwargs))
        reject("reject-duplicate-streamed-json-fields",
               lambda: synthetic_stream(b'{"proof":1,"proof":2,"value":[]}\n'))
        reject("reject-an-omitted-streamed-json-field",
               lambda: synthetic_stream(b'{"proof":"missing"}\n'))
        reject("reject-an-extra-streamed-json-field",
               lambda: synthetic_stream(b'{"proof":1,"value":[],"hidden":2}\n'))

        matrix = frozen_matrix()
        accept("reproduce-the-prospectively-frozen-2854-case-matrix",
               len(matrix) == CASE_COUNT and digest(matrix) == MATRIX_SHA256)
        accept("preserve-the-exact-published-64-bit-seed",
               PUBLISHED_SEED == 5_999_725_261_024_810_545
               and all(row["seed"] == PUBLISHED_SEED for row in matrix))

        manifest, evidence = synthetic_fixtures()

        def loader(
            relative: str, expected: str, kind: str,
            original_sha256: str | None, original_bytes: int | None,
        ) -> dict[str, Any]:
            require(kind in {"receipt", "baseline", "candidate"},
                    "a synthetic Scanner evidence kind was forged")
            if kind == "receipt":
                require(original_sha256 is None and original_bytes is None,
                        "a synthetic receipt claimed a compressed body")
            else:
                require(type(original_sha256) is str and type(original_bytes) is int,
                        "a complete synthetic original report was not pinned")
            value = evidence.get((relative, expected))
            require(type(value) is dict,
                    "a synthetic Scanner evidence source pin was substituted")
            return value

        baseline, rows = manifest_rows(manifest, loader)
        accept("authenticate-two-independent-complete-python-reference-workers",
               baseline["reference_pids"] == [82, 83])
        accept("show-python-rust-c-and-zig-in-consistent-order",
               [row["family"] for row in rows] == ["python", "rust", "c", "zig"])
        accept("keep-all-original-2854-case-denominators-identical",
               all(row["case_denominator"] == CASE_COUNT for row in rows))
        accept("show-a-genuine-complete-candidate-pass-as-green",
               rows[1]["passed"] == CASE_COUNT and rows[1]["failed"] == 0)
        accept("never-treat-successful-publication-as-candidate-correctness",
               rows[2]["passed"] == CASE_COUNT - 37 and rows[2]["failed"] == 37)
        accept("preserve-an-entire-superseded-failing-source-version",
               len(rows[2]["superseded"]) == 1
               and rows[2]["superseded"][0]["failed"] == 53)
        accept("show-a-truly-unmeasured-engine-in-gray",
               rows[3]["passed"] == 0 and rows[3]["failed"] == 0
               and rows[3]["not_measured"] == CASE_COUNT)
        source_pin = "45" * 32
        manifest_pin = digest(manifest)
        svg, summary = build_documents(manifest, source_pin, manifest_pin, loader)
        decoded = decode_document(summary, "source-only synthetic Scanner summary",
                                  MAX_SOURCE_BYTES)
        accept("render-an-accessible-plain-language-scanner-comparison",
               b"<svg" in svg and b"Python Scanner compatibility" in svg
               and b"2,854 / 2,854 match Python" in svg
               and b"2,817 / 2,854 match Python" in svg
               and b"NOT MEASURED" in svg)
        accept("keep-the-original-2807-and-memory-1024-graphs-independent",
               decoded["independent_of_original_2807_case_denominator"] is True
               and decoded["independent_of_memory_1024_case_denominator"] is True)
        accept("retain-every-current-and-historical-failure-in-canonical-json",
               decoded["families"][2]["failed"] == 37
               and decoded["families"][2]["superseded"][0]["failed"] == 53
               and decoded["performance"] == "NOT MEASURED"
               and decoded["final_holdout_opened"] is False)
        accept("regenerate-byte-identical-scanner-chart-and-summary",
               (svg, summary) == build_documents(
                   manifest, source_pin, manifest_pin, loader,
               ))

        def changed_manifest(name: str, replacement: Any) -> None:
            forged = dict(manifest)
            forged[name] = replacement
            manifest_rows(forged, loader)

        for name, replacement in (
            ("schema", "foreign"),
            ("python", "3.14.5"),
            ("case_denominator", CASE_COUNT - 1),
            ("oracle_source_sha256", "0" * 64),
            ("recorder_source_sha256", "0" * 64),
            ("ownership_audit_sha256", "0" * 64),
            ("original_v5_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("published_seed", float(PUBLISHED_SEED)),
            ("published_seed", PUBLISHED_SEED - 1),
            ("families", manifest["families"][:-1]),
            ("families", list(reversed(manifest["families"]))),
        ):
            reject("reject-forged-scanner-manifest-" + name + "-" + str(len(rejected)),
                   lambda name=name, replacement=replacement:
                   changed_manifest(name, replacement))

        base_archive = manifest["baseline"]["archive"]
        base_receipt_pin = manifest["baseline"]["receipt"]
        base_receipt = evidence[(base_receipt_pin["relative"],
                                 base_receipt_pin["sha256"])]
        for name, replacement in (
            ("status", "FAIL"),
            ("baseline_result_status", "FAIL"),
            ("recorder_source_sha256", "0" * 64),
            ("oracle_source_sha256", "0" * 64),
            ("ownership_audit_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("published_seed", PUBLISHED_SEED - 1),
            ("case_count", CASE_COUNT - 1),
            ("validated_reference_a_case_count", CASE_COUNT - 1),
            ("validated_reference_b_case_count", CASE_COUNT - 1),
            ("actual_reference_workers", 1),
            ("actual_candidate_workers", 1),
            ("source_closure_unchanged", False),
            ("report_sha256", "0" * 64),
            ("report_compression", "none"),
            ("report_file_fsync_completed", False),
            ("report_directory_fsync_completed", False),
            ("report_atomic_no_overwrite_link", False),
            ("report_complete_readback_verified", False),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("performance", "fast"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            forged = dict(base_receipt)
            forged[name] = replacement
            reject("reject-forged-baseline-receipt-" + name,
                   lambda forged=forged: validate_baseline_receipt(
                       forged, manifest["baseline"]["label"],
                       base_archive["relative"], base_archive["sha256"],
                       base_receipt_pin["relative"],
                   ))

        c = manifest["families"][1]
        c_receipt = evidence[(c["receipt"]["relative"], c["receipt"]["sha256"])]
        c_report = evidence[(c["report"]["relative"], c["report"]["sha256"])]
        for name, replacement in (
            ("status", "FAIL"),
            ("candidate_result_status", "PASS"),
            ("candidate_family", "rust"),
            ("candidate_source_sha256", "0" * 64),
            ("native_engine_sha256", "0" * 64),
            ("native_bridge_sha256", "0" * 64),
            ("recorder_source_sha256", "0" * 64),
            ("oracle_source_sha256", "0" * 64),
            ("original_v5_sha256", "0" * 64),
            ("ownership_audit_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("published_seed", PUBLISHED_SEED - 1),
            ("case_count", CASE_COUNT - 1),
            ("baseline_archive_sha256", "0" * 64),
            ("baseline_receipt_sha256", "0" * 64),
            ("baseline_records_sha256", "0" * 64),
            ("validated_baseline_record_count", CASE_COUNT - 1),
            ("validated_candidate_record_count", CASE_COUNT - 1),
            ("mismatch_count", 36),
            ("all_mismatches_preserved", False),
            ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
            ("actual_warning_registry_guard_checks", 2 * CASE_COUNT - 1),
            ("actual_reference_workers", 1),
            ("actual_candidate_workers", 0),
            ("actual_candidate_imports", 0),
            ("candidate_owner_unchanged", False),
            ("report_sha256", "0" * 64),
            ("report_compression", "none"),
            ("report_file_fsync_completed", False),
            ("report_directory_fsync_completed", False),
            ("report_atomic_no_overwrite_link", False),
            ("report_complete_readback_verified", False),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("performance", "fast"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            forged = dict(c_receipt)
            forged[name] = replacement
            reject("reject-forged-candidate-receipt-" + name,
                   lambda forged=forged: validate_candidate_receipt(
                       forged, "c", c["candidate_source_sha256"], baseline,
                       c["report"]["relative"], c["report"]["sha256"],
                       c["receipt"]["relative"],
                   ))
        for name, replacement in (
            ("status", "PASS"),
            ("candidate_source_sha256", "0" * 64),
            ("case_count", CASE_COUNT - 1),
            ("validated_candidate_record_count", CASE_COUNT - 1),
            ("mismatch_count", 36),
            ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
            ("actual_warning_registry_guard_checks", 2 * CASE_COUNT - 1),
            ("actual_candidate_workers", 0),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("performance", "fast"),
            ("candidate_records", c_report["candidate_records"][:-1]),
            ("baseline_records", c_report["baseline_records"][:-1]),
            ("all_mismatches", c_report["all_mismatches"][:-1]),
        ):
            forged = dict(c_report)
            forged[name] = replacement
            reject("reject-forged-full-candidate-report-" + name,
                   lambda forged=forged: validate_candidate(
                       forged, c_receipt, baseline, matrix,
                       evidence[(base_archive["relative"],
                                 base_archive["sha256"])]["reference_a_records"],
                   ))

        for name, action in (
            ("reject-a-hidden-scanner-failure", lambda: validate_mismatch_counts(
                {"mismatches_by_expected_kind": {
                    **c_receipt["mismatches_by_expected_kind"],
                    "full-match": c_receipt["mismatches_by_expected_kind"]["full-match"] + 1,
                }, "mismatches_by_cohort": c_receipt["mismatches_by_cohort"]}, 37,
            )),
            ("reject-a-hidden-scanner-cohort-loss", lambda: validate_mismatch_counts(
                {"mismatches_by_expected_kind": c_receipt["mismatches_by_expected_kind"],
                 "mismatches_by_cohort": {"semantic": 36, "tokenizer": 0}}, 37,
            )),
            ("reject-duplicate-canonical-json-fields",
             lambda: decode_document(b'{"proof":1,"proof":2}\n', "synthetic")),
            ("reject-noncanonical-json-evidence",
             lambda: decode_document(b'{"proof": 1}\n', "synthetic")),
            ("reject-nonfinite-json-evidence",
             lambda: decode_document(b'{"proof":NaN}\n', "synthetic")),
            ("reject-a-truncated-process-stream", lambda: decode_stream({
                **capture_stream(b"synthetic"), "bytes": 8,
            }, "synthetic process")),
            ("reject-a-forged-process-digest", lambda: decode_stream({
                **capture_stream(b"synthetic"), "sha256": "0" * 64,
            }, "synthetic process")),
            ("reject-a-second-baseline-worker-sharing-its-pid", lambda:
             validate_baseline_receipt({
                 **base_receipt, "baseline_reference_pids": [82, 82],
             }, manifest["baseline"]["label"], base_archive["relative"],
                base_archive["sha256"], base_receipt_pin["relative"])),
        ):
            reject(name, action)
        for path in ("", "/tmp/escape", "../escape", "a/../b", "a//b", "a\\b"):
            reject("reject-unsafe-path-" + repr(path),
                   lambda path=path: safe_parts(path))

        old_svg = b"old scanner svg"
        old_summary = b"old scanner summary"
        old_svg_hash = hashlib.sha256(old_svg).hexdigest()
        old_summary_hash = hashlib.sha256(old_summary).hexdigest()
        accept("allow-exact-idempotent-no-clobber-graph-publication",
               validate_refresh(svg, summary, svg, summary,
                                False, None, None) is False)
        accept("allow-only-a-two-file-explicitly-source-pinned-refresh",
               validate_refresh(old_svg, old_summary, svg, summary, True,
                                old_svg_hash, old_summary_hash) is True)
        for name, args in (
            ("reject-silent-svg-replacement",
             (old_svg, summary, svg, summary, False, None, None)),
            ("reject-silent-summary-replacement",
             (svg, old_summary, svg, summary, False, None, None)),
            ("reject-refresh-without-the-old-svg",
             (None, old_summary, svg, summary, True,
              old_svg_hash, old_summary_hash)),
            ("reject-refresh-without-the-old-summary",
             (old_svg, None, svg, summary, True,
              old_svg_hash, old_summary_hash)),
            ("reject-refresh-with-a-forged-old-svg",
             (old_svg, old_summary, svg, summary, True,
              "0" * 64, old_summary_hash)),
            ("reject-refresh-with-a-forged-old-summary",
             (old_svg, old_summary, svg, summary, True,
              old_svg_hash, "0" * 64)),
            ("reject-refresh-pins-without-explicit-replacement",
             (svg, summary, svg, summary, False,
              hashlib.sha256(svg).hexdigest(), None)),
        ):
            reject(name, lambda args=args: validate_refresh(*args))

        for name, action in (
            ("block-all-correctness-evidence-reads",
             lambda: builtins.open("experiments/synthetic.json", "rb")),
            ("block-all-generated-graph-writes",
             lambda: builtins.open(SVG_RELATIVE, "wb")),
            ("block-no-follow-evidence-access",
             lambda: os.open("experiments/synthetic.json", os.O_RDONLY)),
            ("block-any-hidden-or-benchmark-directory-access",
             lambda: os.stat("performance")),
            ("block-any-owned-or-external-candidate-import",
             lambda: importlib.import_module("candidates.zig_candidate")),
            ("block-candidate-reference-and-audit-workers",
             lambda: subprocess.run([PINNED_PYTHON])),
            ("block-background-worker-threads",
             lambda: threading.Thread(target=lambda: None).start()),
            ("block-all-performance-timing",
             lambda: time.perf_counter()),
            ("block-silent-generated-graph-replacement",
             lambda: os.replace("synthetic-old", "synthetic-new")),
            ("block-no-clobber-generated-graph-links",
             lambda: os.link("synthetic-old", "synthetic-new")),
            ("block-generated-graph-directory-synchronization",
             lambda: os.fsync(-1)),
            ("block-garbage-collection-side-effects",
             lambda: gc.collect()),
            ("block-external-random-seed-generation",
             lambda: os.urandom(8)),
        ):
            reject(name, action)
        accept("exercise-every-source-only-external-effect-boundary",
               all(count > 0 for count in boundary.blocked.values()))

    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_source_sha256": RECORDER_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_denominator": CASE_COUNT,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "workspace_files_read": 0,
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
        description="Render only the independent 2,854-case Python Scanner comparison",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run exclusively in-memory, effect-blocked source controls")
    modes.add_argument("--render", action="store_true",
                       help="render only the explicitly frozen Scanner manifest")
    parser.add_argument("--source-sha256")
    parser.add_argument("--manifest")
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--replace-generated", action="store_true")
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--previous-summary-sha256")
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            require(all(getattr(options, name) is None for name in (
                "source_sha256", "manifest", "manifest_sha256",
                "previous_svg_sha256", "previous_summary_sha256",
            )) and options.replace_generated is False,
                    "source-only controls cannot authorize rendering or graph replacement")
            result = self_test()
        else:
            require(options.render is True,
                    "explicitly select the frozen Scanner correctness graph")
            result = render(
                options.source_sha256, options.manifest, options.manifest_sha256,
                replace=options.replace_generated,
                previous_svg=options.previous_svg_sha256,
                previous_summary=options.previous_summary_sha256,
            )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (OverviewError, OSError, TypeError, ValueError, KeyError, IndexError,
            OverflowError, UnicodeError, binascii.Error, zlib.error) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
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
