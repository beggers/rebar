#!/usr/bin/env python3
"""Durably preserve exactly one unchanged original CPython Rust-suite run.

Only explicit ``--record`` launches the frozen original suite.  Both complete
process streams, all authentic 152 baseline and candidate method records, every
failure traceback, and every mismatch are preserved before a failing result is
returned.  ``--self-test`` is synthetic, entirely in memory, and blocks actual
files, candidates, clocks, workers, and publications.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass, replace
import gc
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/record_rust_original_cpython_v2.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SCHEMA = "rebar-frozen-rust-original-cpython-recorder-v2"
ORIGINAL_RELATIVE = "tools/rust_original_cpython_suite_v2.py"
ORIGINAL_MODULE = "tools.rust_original_cpython_suite_v2"
ORIGINAL_SHA256 = (
    "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267"
)
TEST_HARNESS_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
TEST_HARNESS_SHA256 = (
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
)
ORIGINAL_SCHEMA = "rebar-original-cpython-re-full-methods-v2"
PUBLIC_RECORDER_RELATIVE = "tools/record_rust_public_correctness_v1.py"
PUBLIC_RECORDER_MODULE = "tools.record_rust_public_correctness_v1"
PUBLIC_RECORDER_SHA256 = (
    "41b749696cc498be4e2b5d63866fb103d29d54e1277dae6a5659fd63302daa49"
)
MATRIX_SHA256 = (
    "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
)
BASELINE_SHA256 = (
    "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
)
ORIGINAL_TEST_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
CANDIDATE_RELATIVE = "candidates/rust_candidate.py"
NATIVE_ENGINE_RELATIVE = "candidates/_rust_engine.so"
NATIVE_BRIDGE_RELATIVE = (
    "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
)
TOTAL_METHODS = 165
PUBLIC_METHODS = 152
PRIVATE_WAIVERS = 13
GUARD_CHECKS = 2 * PUBLIC_METHODS
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 128 * 1024 * 1024
PRIVATE_METHODS = (
    "DebugTests.test_debug_flag",
    "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one",
    "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable",
    "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
RESULT_FIELDS = {
    "schema", "status", "python", "controller_source_sha256",
    "matrix_sha256", "original_source_sha256",
    "test_harness_relative", "test_harness_sha256",
    "all_original_method_count",
    "actual_public_method_count", "private_waiver_count", "private_waivers",
    "public_waivers", "all_original_methods_executed",
    "all_original_methods_qualified", "baseline_records_sha256",
    "candidate_records_sha256", "baseline_records", "candidate_records",
    "mismatch_count", "all_mismatches", "baseline_pid", "candidate_pid",
    "native_provenance", "matcher_guard", "actual_candidate_workers",
    "actual_localedef_workers", "actual_private_temporary_directories_created",
    "actual_private_locale_outputs_created",
    "all_private_temporary_directories_removed", "clock_samples",
    "timing_trials_run", "workspace_files_written", "benchmark_files_read",
    "hidden_cases_read", "performance", "final_winner_selected",
}
RECORD_FIELDS = {
    "test", "source_ast_sha256", "status", "tests_run", "failure_count",
    "error_count", "skip_count", "failure_tracebacks", "error_tracebacks",
    "skip_reasons",
}


class RecorderError(Exception):
    """Reject an altered source, hidden method, or unsafe publication."""


class SourceOnlyError(RecorderError):
    """A synthetic-only operation attempted an actual external effect."""


@dataclass(frozen=True)
class OwnerPins:
    original: str
    public_recorder: str
    matrix: str
    baseline: str
    candidate: str
    native_engine: str
    native_bridge: str


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and len(set(value)) > 1
            and all(letter in "0123456789abcdef" for letter in value),
            "an independently pinned lowercase SHA-256 is required: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON),
            "use only isolated no-bytecode frozen CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "an original recorder must never import a Rust candidate")


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for letter in value)
            and "--" not in value,
            "a bounded, lowercase, nonescaping original-run label is required")
    return value


def approved_paths(label: Any) -> tuple[str, str]:
    slug = validate_label(label)
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def _relative_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "an exact owned no-follow relative path is mandatory")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative,
            "an escaping or noncanonical original-recorder path was rejected")
    return parts


def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0))


def read_owned_regular(
    relative: str, expected: str, *, maximum: int,
) -> tuple[bytes, dict[str, Any]]:
    parts = _relative_parts(relative)
    validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "an exact bounded, owned original artifact is required")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the literal original-recorder root is not a real directory")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an original source parent is not an owned directory")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino)
                == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum,
                "an original source was replaced, linked, or unbounded")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "a complete frozen original source was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "a frozen original source gained a concealed suffix")
        after = os.fstat(descriptor)
        require((after.st_dev, after.st_ino, after.st_size)
                == (before.st_dev, before.st_ino, before.st_size),
                "an original source inode changed during authentication")
        raw = b"".join(chunks)
        require(hashlib.sha256(raw).hexdigest() == expected,
                "an independently frozen original source changed: " + relative)
        return raw, {
            "relative": relative, "sha256": expected, "bytes": len(raw),
            "device": before.st_dev, "inode": before.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "duplicate original result keys cannot conceal a failure")
        result[key] = value
    return result


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "the complete bounded original process output is mandatory: " + label)
    try:
        actual = json.loads(
            raw, object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                RecorderError("nonfinite original-suite evidence is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise RecorderError("invalid full original process JSON: " + label) from error
    require(type(actual) is dict and canonical(actual) == raw,
            "the complete canonical original process bytes changed: " + label)
    return actual


def positive_int(value: Any, label: str) -> int:
    require(type(value) is int and value > 0,
            "a genuine positive original observation is required: " + label)
    return value


def valid_provenance(value: Any, pins: OwnerPins) -> bool:
    if type(value) is not dict or set(value) != {
        "source", "native_engine", "native_bridge",
    }:
        return False
    expectations = (
        ("source", CANDIDATE_RELATIVE, pins.candidate),
        ("native_engine", NATIVE_ENGINE_RELATIVE, pins.native_engine),
        ("native_bridge", NATIVE_BRIDGE_RELATIVE, pins.native_bridge),
    )
    for name, relative, expected in expectations:
        item = value.get(name)
        if not (type(item) is dict
                and set(item) == {"relative", "sha256", "bytes", "device", "inode"}
                and item.get("relative") == relative
                and item.get("sha256") == expected
                and type(item.get("bytes")) is int and item["bytes"] > 0
                and type(item.get("device")) is int and item["device"] >= 0
                and type(item.get("inode")) is int and item["inode"] > 0):
            return False
    return True


def authenticate_sources(pins: OwnerPins) -> tuple[Any, Any, list[dict[str, Any]]]:
    verify_runtime()
    require(pins.original == ORIGINAL_SHA256
            and pins.public_recorder == PUBLIC_RECORDER_SHA256
            and pins.matrix == MATRIX_SHA256
            and pins.baseline == BASELINE_SHA256,
            "the frozen V2 controller, immutable V1 harness, or baseline changed")
    read_owned_regular(ORIGINAL_RELATIVE, pins.original,
                       maximum=MAX_SOURCE_BYTES)
    read_owned_regular(TEST_HARNESS_RELATIVE, TEST_HARNESS_SHA256,
                       maximum=MAX_SOURCE_BYTES)
    read_owned_regular(PUBLIC_RECORDER_RELATIVE, pins.public_recorder,
                       maximum=MAX_SOURCE_BYTES)
    suite = importlib.import_module(ORIGINAL_MODULE)
    recorder = importlib.import_module(PUBLIC_RECORDER_MODULE)
    require(suite.__name__ == ORIGINAL_MODULE
            and os.path.abspath(suite.__file__) == str(ROOT / ORIGINAL_RELATIVE)
            and suite.SCHEMA == ORIGINAL_SCHEMA
            and suite.MATRIX_SHA256 == pins.matrix
            and suite.BASELINE_SHA256 == pins.baseline
            and suite.HARNESS_RELATIVE == TEST_HARNESS_RELATIVE
            and suite.HARNESS_SHA256 == TEST_HARNESS_SHA256
            and suite.ORIGINAL_METHOD_COUNT == TOTAL_METHODS
            and suite.PUBLIC_METHOD_COUNT == PUBLIC_METHODS
            and suite.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVERS
            and recorder.__name__ == PUBLIC_RECORDER_MODULE
            and os.path.abspath(recorder.__file__)
            == str(ROOT / PUBLIC_RECORDER_RELATIVE)
            and recorder.ROOT == ROOT
            and recorder.PINNED_PYTHON == PINNED_PYTHON
            and recorder.CANDIDATE_RELATIVE == CANDIDATE_RELATIVE
            and recorder.NATIVE_ENGINE_RELATIVE == NATIVE_ENGINE_RELATIVE,
            "the exact frozen V2 controller or three-owner authenticator changed")
    harness = suite.load_original_test_harness()
    require(harness.__name__ == "tools.rust_original_cpython_suite_v1"
            and os.path.abspath(harness.__file__)
            == str(ROOT / TEST_HARNESS_RELATIVE)
            and harness.METHOD_MATRIX_SHA256 == pins.matrix
            and harness.BASELINE_RECORDS_SHA256 == pins.baseline
            and harness.TEST_SOURCE_SHA256 == ORIGINAL_TEST_SHA256
            and tuple(harness.PRIVATE_METHODS) == PRIVATE_METHODS,
            "the real immutable V1 original test harness was substituted")
    matrix = harness.build_matrix()
    require(harness.validate_matrix(matrix) == pins.matrix
            and digest(matrix) == pins.matrix
            and len(matrix) == TOTAL_METHODS,
            "all 165 actual V1 source-ordered methods are mandatory for V2")
    verify_runtime()
    return suite, recorder, matrix

def _validate_method(
    requirement: Mapping[str, Any], observed: Any,
) -> dict[str, Any]:
    require(type(observed) is dict and set(observed) == RECORD_FIELDS
            and observed.get("test") == requirement["test"]
            and observed.get("source_ast_sha256")
            == requirement["source_ast_sha256"]
            and observed.get("status") in ("PASS", "FAIL", "SKIP")
            and observed.get("tests_run") == 1,
            "an original method identity or complete result was hidden")
    for count, vector in (
        ("failure_count", "failure_tracebacks"),
        ("error_count", "error_tracebacks"),
        ("skip_count", "skip_reasons"),
    ):
        values = observed.get(vector)
        require(type(values) is list
                and all(type(value) is str for value in values)
                and type(observed.get(count)) is int
                and observed[count] == len(values),
                "a complete original failure, traceback, or skip was concealed")
    expected = (
        "FAIL" if observed["failure_count"] or observed["error_count"]
        else "SKIP" if observed["skip_count"] else "PASS"
    )
    require(observed["status"] == expected
            and not (observed["skip_count"]
                     and (observed["failure_count"] or observed["error_count"])),
            "an actual original test outcome was reclassified")
    return observed


def _validate_guard(guard: Any) -> None:
    require(type(guard) is dict
            and set(guard) == {
                "cached_original_matcher_descendant_count",
                "cached_original_holder_count", "original_matchers_blocked",
                "adapter_import_quarantined", "native_sre_blocked",
                "builtins_import_guarded", "importlib_import_guarded",
                "actual_object_identity_guarded",
                "public_type_names_used_for_ownership",
                "actual_method_guard_checks",
            }
            and type(guard.get("cached_original_matcher_descendant_count")) is int
            and guard["cached_original_matcher_descendant_count"] >= 0
            and type(guard.get("cached_original_holder_count")) is int
            and guard["cached_original_holder_count"] >= 0
            and guard.get("actual_method_guard_checks") == GUARD_CHECKS
            and all(guard.get(key) is True for key in (
                "original_matchers_blocked", "adapter_import_quarantined",
                "native_sre_blocked", "builtins_import_guarded",
                "importlib_import_guarded", "actual_object_identity_guarded",
            ))
            and guard.get("public_type_names_used_for_ownership") is False,
            "all 304 genuine object-identity-quarantined V2 guards are mandatory")

def _validate_native(native: Any, owners: Mapping[str, Any], pins: OwnerPins) -> None:
    require(type(native) is dict
            and set(native) == {"source", "native_engine", "native_bridge"}
            and valid_provenance(owners, pins),
            "all three real original-suite native owners are mandatory")
    source = native.get("source")
    require(type(source) is dict and set(source) == {
        "relative", "sha256", "bytes",
    } and all(source.get(key) == owners["source"][key]
             for key in ("relative", "sha256", "bytes")),
            "the exact original Rust source owner was substituted")
    for key in ("native_engine", "native_bridge"):
        require(native.get(key) == owners[key],
                "the exact loaded original native owner changed: " + key)


def validate_suite_result(
    result: Any, matrix: list[dict[str, Any]],
    pins: OwnerPins, owners: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(result) is dict and set(result) == RESULT_FIELDS,
            "the complete original candidate process document is mandatory")
    require(type(matrix) is list and len(matrix) == TOTAL_METHODS
            and digest(matrix) == pins.matrix,
            "the complete 165-method frozen original matrix was changed")
    expected = {
        "schema": ORIGINAL_SCHEMA + "-actual-original-candidate-result",
        "python": "3.14.6", "controller_source_sha256": pins.original,
        "matrix_sha256": pins.matrix,
        "original_source_sha256": ORIGINAL_TEST_SHA256,
        "test_harness_relative": TEST_HARNESS_RELATIVE,
        "test_harness_sha256": TEST_HARNESS_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVERS,
        "private_waivers": list(PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "baseline_records_sha256": pins.baseline,
        "actual_candidate_workers": 1,
        "actual_localedef_workers": 4,
        "actual_private_temporary_directories_created": 2,
        "actual_private_locale_outputs_created": 4,
        "all_private_temporary_directories_removed": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED", "final_winner_selected": False,
    }
    for name, value in expected.items():
        require(result.get(name) == value,
                "a complete frozen original observation changed: " + name)
    public = [row for row in matrix if row.get("classification") == "public"]
    private = [row for row in matrix
               if row.get("classification") == "named-private-waiver"]
    require(len(public) == PUBLIC_METHODS and len(private) == PRIVATE_WAIVERS
            and tuple(row["test"] for row in private) == PRIVATE_METHODS,
            "an original public method or named private waiver was replaced")
    original = result.get("baseline_records")
    candidate = result.get("candidate_records")
    require(type(original) is list and type(candidate) is list
            and len(original) == len(candidate) == PUBLIC_METHODS
            and digest(original) == pins.baseline
            and result.get("candidate_records_sha256") == digest(candidate),
            "both complete genuine 152-method vectors must be preserved")
    mismatch: list[dict[str, Any]] = []
    for requirement, baseline_row, candidate_row in zip(
        public, original, candidate, strict=True,
    ):
        baseline_row = _validate_method(requirement, baseline_row)
        candidate_row = _validate_method(requirement, candidate_row)
        if baseline_row != candidate_row:
            mismatch.append({
                "test": requirement["test"],
                "baseline": baseline_row, "candidate": candidate_row,
            })
    require(sum(row["status"] == "PASS" for row in original) == 151
            and sum(row["status"] == "SKIP" for row in original) == 1
            and sum(row["status"] == "FAIL" for row in original) == 0,
            "the authentic original baseline must have 151 passes and one skip")
    skips = [row for row in original if row["status"] == "SKIP"]
    require(skips[0]["test"] == "ReTests.test_memory_leaks"
            and skips[0]["skip_reasons"] == ["requires debug build"],
            "the sole genuine CPython debug-build waiver was substituted")
    require(type(result.get("all_mismatches")) is list
            and result["all_mismatches"] == mismatch
            and type(result.get("mismatch_count")) is int
            and result["mismatch_count"] == len(mismatch)
            and result.get("status") == ("FAIL" if mismatch else "PASS"),
            "an original mismatch, complete traceback, or FAIL was hidden")
    baseline_pid = positive_int(result.get("baseline_pid"), "baseline PID")
    candidate_pid = positive_int(result.get("candidate_pid"), "candidate PID")
    require(baseline_pid != candidate_pid,
            "the original baseline and candidate were not isolated")
    _validate_native(result.get("native_provenance"), owners, pins)
    _validate_guard(result.get("matcher_guard"))
    return result


def capture_stream(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "the complete bounded original process stream is mandatory: " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def build_complete_report(
    *, label: str, stdout: bytes, stderr: bytes, returncode: int,
    process_pid: int, matrix: list[dict[str, Any]], pins: OwnerPins,
    owners_before: Mapping[str, Any], owners_after: Mapping[str, Any] | None,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    slug = validate_label(label)
    positive_int(process_pid, "full original controller PID")
    require(type(returncode) is int and valid_provenance(owners_before, pins),
            "the genuine original process and pre-run owners are required")
    captured_stdout = capture_stream(stdout, "original process stdout")
    captured_stderr = capture_stream(stderr, "original process stderr")
    result: dict[str, Any] | None = None
    failure: str | None = post_run_error
    if owners_after is None or not valid_provenance(owners_after, pins) \
            or dict(owners_after) != dict(owners_before):
        failure = (failure or "the exact original source or native owner changed")
    try:
        parsed = decode_canonical(stdout, "full original candidate process")
        result = validate_suite_result(parsed, matrix, pins, owners_before)
        expected_exit = 0 if result["status"] == "PASS" else 1
        require(returncode == expected_exit,
                "the actual full original candidate exit was misclassified")
    except (RecorderError, ValueError, TypeError, KeyError) as error:
        failure = (failure + "; " if failure else "") + str(error)
    status = "PASS" if result is not None \
        and result["status"] == "PASS" and failure is None else "FAIL"
    baseline_records = result["baseline_records"] if result is not None else []
    candidate_records = result["candidate_records"] if result is not None else []
    mismatches = result["all_mismatches"] if result is not None else []
    return {
        "schema": SCHEMA + "-complete-first-run-report",
        "status": status, "label": slug, "python": "3.14.6",
        "original_suite_relative": ORIGINAL_RELATIVE,
        "original_suite_sha256": pins.original,
        "public_recorder_relative": PUBLIC_RECORDER_RELATIVE,
        "public_recorder_sha256": pins.public_recorder,
        "original_test_source_sha256": ORIGINAL_TEST_SHA256,
        "test_harness_relative": TEST_HARNESS_RELATIVE,
        "test_harness_sha256": TEST_HARNESS_SHA256,
        "matrix_sha256": pins.matrix,
        "baseline_records_sha256": (
            result["baseline_records_sha256"] if result is not None else None
        ),
        "candidate_records_sha256": (
            result["candidate_records_sha256"] if result is not None else None
        ),
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVERS,
        "private_waivers": list(PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "validated_baseline_record_count": len(baseline_records),
        "validated_candidate_record_count": len(candidate_records),
        "baseline_records": baseline_records,
        "candidate_records": candidate_records,
        "mismatch_count": len(mismatches),
        "all_mismatches": mismatches,
        "all_mismatches_preserved": result is not None,
        "complete_original_suite_result": result,
        "complete_original_process_stdout": captured_stdout,
        "complete_original_process_stderr": captured_stderr,
        "original_process_pid": process_pid,
        "original_process_returncode": returncode,
        "actual_original_suite_invocations": 1,
        "candidate_provenance_before": dict(owners_before),
        "candidate_provenance_after": (
            dict(owners_after) if owners_after is not None else None
        ),
        "candidate_provenance_unchanged": (
            owners_after is not None
            and valid_provenance(owners_after, pins)
            and dict(owners_after) == dict(owners_before)
        ),
        "validation_error": failure,
        "baseline_pid": result["baseline_pid"] if result is not None else None,
        "candidate_pid": result["candidate_pid"] if result is not None else None,
        "matcher_guard": result["matcher_guard"] if result is not None else None,
        "actual_method_guard_checks": (
            result["matcher_guard"]["actual_method_guard_checks"]
            if result is not None else 0
        ),
        "actual_object_identity_guarded": (
            result["matcher_guard"]["actual_object_identity_guarded"]
            if result is not None else False
        ),
        "public_type_names_used_for_ownership": (
            result["matcher_guard"]["public_type_names_used_for_ownership"]
            if result is not None else None
        ),
        "multiprocessing_start_method": "fork" if result is not None else None,
        "actual_localedef_workers": (
            result["actual_localedef_workers"] if result is not None else 0
        ),
        "actual_private_temporary_directories_created": (
            result["actual_private_temporary_directories_created"]
            if result is not None else 0
        ),
        "all_private_temporary_directories_removed": (
            result["all_private_temporary_directories_removed"]
            if result is not None else False
        ),
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


@contextlib.contextmanager
def preflight_fresh_outputs(label: str) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(label)
    report_parts = _relative_parts(report)
    receipt_parts = _relative_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "preflight exactly two distinct approved original-run outputs")
    opened: list[int] = []
    created: list[tuple[int, str]] = []
    successful = False
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact original-output root is not an owned directory")
        for component in report_parts[:-1]:
            try:
                following = os.open(component, directory_flags(), dir_fd=current)
            except FileNotFoundError:
                os.mkdir(component, mode=0o755, dir_fd=current)
                created.append((current, component))
                os.fsync(current)
                following = os.open(component, directory_flags(), dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "the original output parent followed a symlink")
            current = following
        info = os.fstat(current)
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError(
                "refusing to overwrite an existing original-run report: "
                + basename,
            )
        successful = True
        yield {
            "report_relative": report, "receipt_relative": receipt,
            "report_basename": report_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": info.st_dev,
            "directory_inode": info.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
        }
    finally:
        active = sys.exc_info()[1]
        errors: list[Exception] = []
        if not successful:
            for descriptor, component in reversed(created):
                try:
                    os.rmdir(component, dir_fd=descriptor)
                    os.fsync(descriptor)
                except Exception as error:
                    errors.append(error)
        for descriptor in reversed(opened):
            try:
                os.close(descriptor)
            except Exception as error:
                errors.append(error)
        if errors and active is None:
            raise RecorderError("owned original preflight cleanup failed") \
                from errors[0]


def verify_retained_directory(preflight: Mapping[str, Any]) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain the actual preflighted original evidence directory")
    info = os.fstat(descriptor)
    require(stat.S_ISDIR(info.st_mode)
            and info.st_dev == preflight.get("directory_device")
            and info.st_ino == preflight.get("directory_inode"),
            "the preflight-approved original evidence directory changed")
    return descriptor


def publish_fresh(
    preflight: Mapping[str, Any], document: Mapping[str, Any], *, kind: str,
) -> tuple[dict[str, Any], bytes]:
    require(kind in ("report", "receipt"),
            "publish only the exact preflighted original report or receipt")
    directory = verify_retained_directory(preflight)
    raw = canonical(dict(document))
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "the complete original-run publication exceeds its exact bound")
    basename = preflight[kind + "_basename"]
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(basename, flags, 0o644, dir_fd=directory)
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode),
                "the exclusive original publication is not an owned file")
        actual_write_calls = 0
        position = 0
        while position < len(raw):
            written = os.write(descriptor, raw[position:])
            actual_write_calls += 1
            require(type(written) is int and written > 0,
                    "the complete original-result exclusive write was truncated")
            position += written
        os.fsync(descriptor)
        require(os.fstat(descriptor).st_size == len(raw),
                "the actual original publication lost complete canonical bytes")
    finally:
        os.close(descriptor)
    os.fsync(directory)
    publication = {
        "path": preflight[kind + "_relative"],
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "actual_write_calls": actual_write_calls,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
    }
    actual = read_published(preflight, document, publication, kind=kind)
    return publication, actual


def read_published(
    preflight: Mapping[str, Any], document: Mapping[str, Any],
    publication: Mapping[str, Any], *, kind: str,
) -> bytes:
    require(kind in ("report", "receipt"),
            "read back only an actually published original report or receipt")
    directory = verify_retained_directory(preflight)
    expected = canonical(dict(document))
    require(type(publication) is dict
            and publication.get("path") == preflight[kind + "_relative"]
            and publication.get("bytes") == len(expected)
            and publication.get("sha256") == hashlib.sha256(expected).hexdigest()
            and type(publication.get("actual_write_calls")) is int
            and publication["actual_write_calls"] >= 1
            and publication.get("file_fsync_completed") is True
            and publication.get("directory_fsync_completed") is True,
            "the durable full original publication receipt was substituted")
    basename = preflight[kind + "_basename"]
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        info = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(info.st_mode) and stat.S_ISREG(named.st_mode)
                and (info.st_dev, info.st_ino) == (named.st_dev, named.st_ino)
                and info.st_size == len(expected),
                "the authentic durable original result changed inode or size")
        remaining = len(expected)
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the genuine complete original publication readback failed")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "the complete original publication has a concealed suffix")
    finally:
        os.close(descriptor)
    actual = b"".join(chunks)
    require(actual == expected
            and hashlib.sha256(actual).hexdigest() == publication["sha256"],
            "the full original vectors, tracebacks, or streams were lost")
    return actual


def candidate_owners(recorder: Any, pins: OwnerPins) -> dict[str, Any]:
    actual = recorder.authenticate_candidate_files(
        pins.candidate, pins.native_engine, pins.native_bridge,
    )
    require(valid_provenance(actual, pins),
            "the exact actual original adapter, engine, or bridge changed")
    return actual


def run_exactly_one_original(pins: OwnerPins) -> tuple[bytes, bytes, int, int]:
    verify_runtime()
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / ORIGINAL_RELATIVE),
        "--candidate", "--oracle-source-sha256", pins.original,
        "--matrix-sha256", pins.matrix,
        "--candidate-source-sha256", pins.candidate,
        "--native-engine-sha256", pins.native_engine,
        "--native-bridge-sha256", pins.native_bridge,
    ]
    process = subprocess.Popen(
        arguments, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(ROOT), shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "LC_ALL": "C", "PATH": "/usr/bin:/bin",
        },
    )
    # No timeout, monotonic clock, retry, or second original candidate run.
    stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and type(process.returncode) is int,
            "the one complete original-process pipe was not collected")
    return stdout, stderr, process.returncode, positive_int(
        process.pid, "actual single original-process PID",
    )


def record_original(label: str, pins: OwnerPins) -> dict[str, Any]:
    slug = validate_label(label)
    for name in ("original", "public_recorder", "matrix", "baseline",
                 "candidate", "native_engine", "native_bridge"):
        validate_digest(getattr(pins, name), name)
    _, recorder, matrix = authenticate_sources(pins)
    owners_before = candidate_owners(recorder, pins)
    with preflight_fresh_outputs(slug) as preflight:
        verify_retained_directory(preflight)
        before_launch = candidate_owners(recorder, pins)
        require(before_launch == owners_before,
                "a frozen original owner changed before its single process")
        stdout, stderr, returncode, process_pid = run_exactly_one_original(pins)
        owners_after: dict[str, Any] | None = None
        post_run_error: str | None = None
        try:
            owners_after = candidate_owners(recorder, pins)
        except (RecorderError, OSError, ValueError, TypeError,
                recorder.RecorderError) as error:
            post_run_error = "post-run actual owner verification failed: " + str(error)
        report = build_complete_report(
            label=slug, stdout=stdout, stderr=stderr,
            returncode=returncode, process_pid=process_pid,
            matrix=matrix, pins=pins,
            owners_before=owners_before, owners_after=owners_after,
            post_run_error=post_run_error,
        )
        verify_runtime()
        verify_retained_directory(preflight)
        report_publication, actual_report = publish_fresh(
            preflight, report, kind="report",
        )
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS", "correctness_status": report["status"],
            "label": slug, "python": "3.14.6",
            "original_suite_relative": ORIGINAL_RELATIVE,
            "original_suite_sha256": pins.original,
            "test_harness_relative": TEST_HARNESS_RELATIVE,
            "test_harness_sha256": TEST_HARNESS_SHA256,
            "public_recorder_relative": PUBLIC_RECORDER_RELATIVE,
            "public_recorder_sha256": pins.public_recorder,
            "matrix_sha256": pins.matrix,
            "baseline_records_sha256": report["baseline_records_sha256"],
            "candidate_records_sha256": report["candidate_records_sha256"],
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVERS,
            "private_waivers": list(PRIVATE_METHODS),
            "public_waivers": [],
            "validated_baseline_record_count": report[
                "validated_baseline_record_count"
            ],
            "validated_candidate_record_count": report[
                "validated_candidate_record_count"
            ],
            "mismatch_count": report["mismatch_count"],
            "all_mismatches_preserved": report["all_mismatches_preserved"],
            "actual_method_guard_checks": report["actual_method_guard_checks"],
            "candidate_source_relative": CANDIDATE_RELATIVE,
            "candidate_source_sha256": pins.candidate,
            "native_engine_relative": NATIVE_ENGINE_RELATIVE,
            "native_engine_sha256": pins.native_engine,
            "native_bridge_relative": NATIVE_BRIDGE_RELATIVE,
            "native_bridge_sha256": pins.native_bridge,
            "candidate_provenance_before": dict(owners_before),
            "candidate_provenance_after": (
                dict(owners_after) if owners_after is not None else None
            ),
            "candidate_provenance_unchanged": report[
                "candidate_provenance_unchanged"
            ],
            "original_process_pid": process_pid,
            "original_process_returncode": returncode,
            "original_process_stdout_sha256": report[
                "complete_original_process_stdout"
            ]["sha256"],
            "original_process_stdout_bytes": report[
                "complete_original_process_stdout"
            ]["bytes"],
            "original_process_stderr_sha256": report[
                "complete_original_process_stderr"
            ]["sha256"],
            "original_process_stderr_bytes": report[
                "complete_original_process_stderr"
            ]["bytes"],
            "actual_original_suite_invocations": 1,
            "report_relative": preflight["report_relative"],
            "report_sha256": hashlib.sha256(actual_report).hexdigest(),
            "report_bytes": len(actual_report),
            "report_actual_write_calls": report_publication[
                "actual_write_calls"
            ],
            "report_file_fsync_completed": True,
            "report_directory_fsync_completed": True,
            "report_complete_readback_verified": True,
            "receipt_complete_readback_required": True,
            "receipt_complete_readback_verified": True,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
            "clock_samples": 0, "timing_trials_run": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        receipt_publication, actual_receipt = publish_fresh(
            preflight, receipt, kind="receipt",
        )
        verify_runtime()
        return {
            "schema": SCHEMA + "-compact-result",
            "status": report["status"], "label": slug, "python": "3.14.6",
            "original_suite_sha256": pins.original,
            "test_harness_relative": TEST_HARNESS_RELATIVE,
            "test_harness_sha256": TEST_HARNESS_SHA256,
            "public_recorder_sha256": pins.public_recorder,
            "matrix_sha256": pins.matrix,
            "baseline_records_sha256": report["baseline_records_sha256"],
            "candidate_records_sha256": report["candidate_records_sha256"],
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVERS,
            "public_waivers": [],
            "validated_baseline_record_count": report[
                "validated_baseline_record_count"
            ],
            "validated_candidate_record_count": report[
                "validated_candidate_record_count"
            ],
            "mismatch_count": report["mismatch_count"],
            "actual_method_guard_checks": report["actual_method_guard_checks"],
            "candidate_source_sha256": pins.candidate,
            "native_engine_sha256": pins.native_engine,
            "native_bridge_sha256": pins.native_bridge,
            "original_process_returncode": returncode,
            "actual_original_suite_invocations": 1,
            "report_publication": report_publication,
            "receipt_publication": receipt_publication,
            "receipt_complete_readback_verified": True,
            "receipt_verified_bytes": len(actual_receipt),
            "clock_samples": 0, "timing_trials_run": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0, "file_writes": 0,
        "candidate_imports": 0, "reference_imports": 0,
        "workers_started": 0, "threads_started": 0,
        "clock_samples": 0, "gc_collections": 0,
        "hidden_cases_read": 0, "performance_files_read": 0,
        "blocked_reads": 0, "blocked_writes": 0,
        "blocked_imports": 0, "blocked_workers": 0,
        "blocked_threads": 0, "blocked_clocks": 0,
        "blocked_gc_collections": 0,
    }
    installed: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def deny(counter: str, message: str) -> Callable[..., Any]:
        def blocked(*args: Any, **keywords: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyError(message)
        return blocked

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, deny(
                "blocked_reads", "a synthetic original control cannot read files",
            ))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, deny(
                "blocked_writes", "a synthetic original control cannot write files",
            ))
        install(importlib, "import_module", deny(
            "blocked_imports", "a synthetic control cannot import a candidate",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "a synthetic original control cannot import",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny(
                "blocked_workers", "a synthetic control cannot start a worker",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "a synthetic control cannot start a thread",
        ))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns"):
            install(time, name, deny(
                "blocked_clocks", "a synthetic control cannot read a clock",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections", "a synthetic control cannot collect garbage",
        ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_documents() -> tuple[
    list[dict[str, Any]], OwnerPins, dict[str, Any],
    dict[str, Any], dict[str, Any],
]:
    matrix: list[dict[str, Any]] = []
    baseline: list[dict[str, Any]] = []
    for index in range(PUBLIC_METHODS):
        name = ("ReTests.test_memory_leaks" if index == PUBLIC_METHODS - 1
                else "ReTests.test_synthetic_" + format(index, "03d"))
        ast_sha = hashlib.sha256(name.encode("ascii")).hexdigest()
        matrix.append({
            "index": index, "test": name, "class": "ReTests",
            "method": name.split(".", 1)[1],
            "source_ast_sha256": ast_sha,
            "classification": "public", "waiver_reason": None,
        })
        skipped = index == PUBLIC_METHODS - 1
        baseline.append({
            "test": name, "source_ast_sha256": ast_sha,
            "status": "SKIP" if skipped else "PASS", "tests_run": 1,
            "failure_count": 0, "error_count": 0,
            "skip_count": 1 if skipped else 0,
            "failure_tracebacks": [], "error_tracebacks": [],
            "skip_reasons": ["requires debug build"] if skipped else [],
        })
    for identity in PRIVATE_METHODS:
        cls, method = identity.split(".", 1)
        matrix.append({
            "index": len(matrix), "test": identity, "class": cls,
            "method": method,
            "source_ast_sha256": hashlib.sha256(
                identity.encode("ascii"),
            ).hexdigest(),
            "classification": "named-private-waiver",
            "waiver_reason": "synthetic named private-only control",
        })
    pins = OwnerPins(
        original=ORIGINAL_SHA256,
        public_recorder=PUBLIC_RECORDER_SHA256,
        matrix=digest(matrix), baseline=digest(baseline),
        candidate="12" * 32, native_engine="34" * 32,
        native_bridge="56" * 32,
    )
    owners = {
        "source": {
            "relative": CANDIDATE_RELATIVE, "sha256": pins.candidate,
            "bytes": 11, "device": 17, "inode": 101,
        },
        "native_engine": {
            "relative": NATIVE_ENGINE_RELATIVE,
            "sha256": pins.native_engine,
            "bytes": 23, "device": 17, "inode": 102,
        },
        "native_bridge": {
            "relative": NATIVE_BRIDGE_RELATIVE,
            "sha256": pins.native_bridge,
            "bytes": 31, "device": 17, "inode": 103,
        },
    }
    guard = {
        "cached_original_matcher_descendant_count": 5,
        "cached_original_holder_count": 7,
        "original_matchers_blocked": True,
        "adapter_import_quarantined": True,
        "native_sre_blocked": True,
        "builtins_import_guarded": True,
        "importlib_import_guarded": True,
        "actual_object_identity_guarded": True,
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": GUARD_CHECKS,
    }
    native = {
        "source": {
            key: owners["source"][key]
            for key in ("relative", "sha256", "bytes")
        },
        "native_engine": dict(owners["native_engine"]),
        "native_bridge": dict(owners["native_bridge"]),
    }

    def make(candidate: list[dict[str, Any]]) -> dict[str, Any]:
        mismatches = [
            {"test": original["test"], "baseline": original,
             "candidate": observed}
            for original, observed in zip(baseline, candidate, strict=True)
            if original != observed
        ]
        return {
            "schema": ORIGINAL_SCHEMA + "-actual-original-candidate-result",
            "status": "FAIL" if mismatches else "PASS",
            "python": "3.14.6",
            "controller_source_sha256": pins.original,
            "matrix_sha256": pins.matrix,
            "original_source_sha256": ORIGINAL_TEST_SHA256,
            "test_harness_relative": TEST_HARNESS_RELATIVE,
            "test_harness_sha256": TEST_HARNESS_SHA256,
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVERS,
            "private_waivers": list(PRIVATE_METHODS),
            "public_waivers": [],
            "all_original_methods_executed": False,
            "all_original_methods_qualified": False,
            "baseline_records_sha256": pins.baseline,
            "candidate_records_sha256": digest(candidate),
            "baseline_records": baseline,
            "candidate_records": candidate,
            "mismatch_count": len(mismatches),
            "all_mismatches": mismatches,
            "baseline_pid": 1011, "candidate_pid": 1012,
            "native_provenance": native, "matcher_guard": guard,
            "actual_candidate_workers": 1,
            "actual_localedef_workers": 4,
            "actual_private_temporary_directories_created": 2,
            "actual_private_locale_outputs_created": 4,
            "all_private_temporary_directories_removed": True,
            "clock_samples": 0, "timing_trials_run": 0,
            "workspace_files_written": 0, "benchmark_files_read": 0,
            "hidden_cases_read": 0, "performance": "NOT MEASURED",
            "final_winner_selected": False,
        }

    passed = make(copy.deepcopy(baseline))
    failing_candidate = copy.deepcopy(baseline)
    failing_candidate[3]["status"] = "FAIL"
    failing_candidate[3]["failure_count"] = 1
    failing_candidate[3]["failure_tracebacks"] = [
        "Traceback (most recent call last):\n"
        "  File synthetic, line 3\nAssertionError: genuine synthetic failure\n",
    ]
    failed = make(failing_candidate)
    return matrix, pins, owners, passed, failed


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a genuine original-recorder positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "an original source-only forgery control was duplicated")
        try:
            action()
        except (RecorderError, ValueError, TypeError, KeyError, OSError):
            rejected.append(name)
            return
        raise RecorderError("a forged original result was accepted: " + name)

    with source_only_boundary() as effects:
        matrix, pins, owners, passed, failed = synthetic_documents()
        require(validate_suite_result(passed, matrix, pins, owners) is passed
                and validate_suite_result(failed, matrix, pins, owners) is failed,
                "synthetic complete original PASS and FAIL controls were lost")
        passing_report = build_complete_report(
            label="synthetic-original-pass-v2", stdout=canonical(passed),
            stderr=b"", returncode=0, process_pid=501,
            matrix=matrix, pins=pins, owners_before=owners,
            owners_after=copy.deepcopy(owners),
        )
        failing_report = build_complete_report(
            label="synthetic-original-fail-v2", stdout=canonical(failed),
            stderr=b"synthetic diagnostic\n", returncode=1,
            process_pid=502, matrix=matrix, pins=pins,
            owners_before=owners, owners_after=copy.deepcopy(owners),
        )
        broken_report = build_complete_report(
            label="synthetic-original-process-fail-v2",
            stdout=b"synthetic full non-JSON original failure\n",
            stderr=b"synthetic complete original traceback\n",
            returncode=2, process_pid=503,
            matrix=matrix, pins=pins, owners_before=owners,
            owners_after=copy.deepcopy(owners),
        )
        accept("preserve-all-165-literal-source-ordered-methods",
               len(matrix) == TOTAL_METHODS)
        accept("preserve-all-152-public-methods-and-13-named-private-waivers",
               sum(row["classification"] == "public" for row in matrix)
               == PUBLIC_METHODS
               and sum(row["classification"] == "named-private-waiver"
                       for row in matrix) == PRIVATE_WAIVERS)
        accept("preserve-exact-151-original-passes-and-one-debug-only-skip",
               sum(row["status"] == "PASS"
                   for row in passed["baseline_records"]) == 151
               and sum(row["status"] == "SKIP"
                       for row in passed["baseline_records"]) == 1)
        accept("preserve-both-complete-independent-152-method-vectors",
               passing_report["validated_baseline_record_count"]
               == passing_report["validated_candidate_record_count"]
               == PUBLIC_METHODS)
        accept("preserve-every-genuine-failure-traceback-and-mismatch",
               failing_report["status"] == "FAIL"
               and failing_report["mismatch_count"] == 1
               and failing_report["all_mismatches"][0]["candidate"]
               ["failure_tracebacks"] == failed["candidate_records"][3]
               ["failure_tracebacks"])
        accept("preserve-complete-original-stdout-stderr-and-failing-exit",
               failing_report["original_process_returncode"] == 1
               and failing_report["complete_original_process_stdout"]
               ["complete"] is True
               and failing_report["complete_original_process_stderr"]
               ["complete"] is True)
        accept("preserve-full-unparseable-process-failure-without-fake-records",
               broken_report["status"] == "FAIL"
               and broken_report["complete_original_suite_result"] is None
               and broken_report["validated_baseline_record_count"] == 0
               and broken_report["validated_candidate_record_count"] == 0
               and broken_report["complete_original_process_stdout"]
               ["complete"] is True)
        accept("require-all-304-actual-native-owner-guard-checks",
               passing_report["actual_method_guard_checks"] == GUARD_CHECKS)
        accept("require-genuine-object-identity-without-public-name-guessing",
               passing_report["actual_object_identity_guarded"] is True
               and passing_report["public_type_names_used_for_ownership"]
               is False)
        accept("preserve-genuine-fork-and-private-temporary-cleanup",
               passing_report["multiprocessing_start_method"] == "fork"
               and passing_report["actual_private_temporary_directories_created"]
               == 2
               and passing_report["all_private_temporary_directories_removed"]
               is True)
        accept("pin-three-synthetic-native-owners-before-and-after",
               valid_provenance(owners, pins)
               and passing_report["candidate_provenance_unchanged"] is True)
        accept("predeclare-exactly-two-distinct-safe-original-output-paths",
               approved_paths("synthetic-original-pass-v2") == (
                   APPROVED_DIRECTORY + "/synthetic-original-pass-v2.json",
                   APPROVED_DIRECTORY
                   + "/synthetic-original-pass-v2-publication-receipt.json",
               ))
        accept("never-claim-hidden-qualification-timing-memory-or-winner",
               passing_report["clock_samples"] == 0
               and passing_report["timing_trials_run"] == 0
               and passing_report["hidden_cases_read"] == 0
               and passing_report["performance"] == "NOT MEASURED"
               and passing_report["candidate_qualified_for_hidden_benchmark"]
               is False and passing_report["final_winner_selected"] is False)

        for index, key in enumerate(sorted(RESULT_FIELDS)):
            poisoned = dict(passed)
            poisoned.pop(key)
            reject("reject-omitted-complete-original-field-"
                   + format(index, "02d"),
                   lambda poisoned=poisoned: validate_suite_result(
                       poisoned, matrix, pins, owners,
                   ))
        for index, key, value in (
            (0, "all_original_method_count", 164),
            (1, "actual_public_method_count", 151),
            (2, "private_waiver_count", 12),
            (3, "public_waivers", ["ReTests.test_synthetic_001"]),
            (4, "all_original_methods_executed", True),
            (5, "all_original_methods_qualified", True),
            (6, "matrix_sha256", "ab" * 32),
            (7, "controller_source_sha256", "cd" * 32),
            (8, "baseline_records_sha256", "ef" * 32),
            (9, "actual_candidate_workers", 0),
            (10, "actual_localedef_workers", 3),
            (11, "actual_private_temporary_directories_created", 1),
            (12, "actual_private_locale_outputs_created", 3),
            (13, "all_private_temporary_directories_removed", False),
            (14, "clock_samples", 1),
            (15, "timing_trials_run", 1),
            (16, "benchmark_files_read", 1),
            (17, "hidden_cases_read", 1),
            (18, "final_winner_selected", True),
            (19, "performance", "FASTER"),
            (20, "status", "FAIL"),
            (21, "baseline_pid", passed["candidate_pid"]),
        ):
            poisoned = dict(passed)
            poisoned[key] = value
            reject("reject-false-original-count-waiver-source-or-effect-"
                   + format(index, "02d"),
                   lambda poisoned=poisoned: validate_suite_result(
                       poisoned, matrix, pins, owners,
                   ))
        for index, poison in enumerate((
            ("baseline_records", lambda rows: rows[:-1]),
            ("candidate_records", lambda rows: rows[:-1]),
            ("baseline_records", lambda rows: list(reversed(rows))),
            ("candidate_records", lambda rows: list(reversed(rows))),
            ("all_mismatches", lambda _: []),
            ("mismatch_count", lambda _: 0),
            ("candidate_records_sha256", lambda _: "ab" * 32),
            ("private_waivers", lambda rows: rows[:-1]),
        )):
            key, transform = poison
            template = failed if key in ("all_mismatches", "mismatch_count") \
                else passed
            poisoned = dict(template)
            poisoned[key] = transform(template[key])
            reject("reject-clipped-reordered-or-concealed-original-vector-"
                   + format(index, "02d"),
                   lambda poisoned=poisoned: validate_suite_result(
                       poisoned, matrix, pins, owners,
                   ))
        for index, key, value in (
            (0, "actual_method_guard_checks", GUARD_CHECKS - 1),
            (1, "original_matchers_blocked", False),
            (2, "adapter_import_quarantined", False),
            (3, "native_sre_blocked", False),
            (4, "builtins_import_guarded", False),
            (5, "importlib_import_guarded", False),
            (6, "cached_original_holder_count", -1),
            (7, "actual_object_identity_guarded", False),
            (8, "public_type_names_used_for_ownership", True),
        ):
            poisoned = dict(passed)
            guard = dict(passed["matcher_guard"])
            guard[key] = value
            poisoned["matcher_guard"] = guard
            reject("reject-unguarded-original-native-matcher-"
                   + format(index, "02d"),
                   lambda poisoned=poisoned: validate_suite_result(
                       poisoned, matrix, pins, owners,
                   ))
        for index, slug in enumerate((
            "", ".", "..", "../escape", "/tmp/escape", "UPPER",
            "a space", "has_underscore", "two--hyphens", "-leading",
            "trailing-", "line\nbreak", "slash/component",
            "back\\slash", "\x00", "a" * 65,
        )):
            reject("reject-escaping-original-publication-label-"
                   + format(index, "02d"),
                   lambda slug=slug: validate_label(slug))
        for index, invalid in enumerate((
            None, 0, True, "", "0" * 64, "A" * 64,
            "g" * 64, "ab" * 31, "ab" * 33,
            ORIGINAL_SHA256.upper(), ORIGINAL_SHA256 + "0",
        )):
            reject("reject-unpinned-original-source-or-native-digest-"
                   + format(index, "02d"),
                   lambda invalid=invalid: validate_digest(
                       invalid, "synthetic original poison",
                   ))
        for index, kind, key, value in (
            (0, "source", "relative", "candidates/foreign.py"),
            (1, "source", "sha256", "78" * 32),
            (2, "native_engine", "relative", "candidates/foreign.so"),
            (3, "native_engine", "sha256", "9a" * 32),
            (4, "native_bridge", "relative", "candidates/foreign-bridge.so"),
            (5, "native_bridge", "sha256", "bc" * 32),
            (6, "source", "inode", 0),
            (7, "native_engine", "device", -1),
            (8, "native_bridge", "bytes", 0),
        ):
            forged = copy.deepcopy(owners)
            forged[kind][key] = value
            reject("reject-substituted-original-three-component-native-owner-"
                   + format(index, "02d"),
                   lambda forged=forged: require(
                       valid_provenance(forged, pins),
                       "the forged original native owner was rejected",
                   ))
        for name, action in (
            ("block-real-original-source-file-read",
             lambda: builtins.open(ORIGINAL_RELATIVE, "rb")),
            ("block-real-public-recorder-source-read",
             lambda: io.open(PUBLIC_RECORDER_RELATIVE, "rb")),
            ("block-real-owned-original-output-open",
             lambda: os.open(approved_paths("synthetic-original-pass-v2")[0],
                             os.O_RDONLY)),
            ("block-real-original-evidence-write",
             lambda: os.write(1, b"forbidden")),
            ("block-real-original-evidence-publication",
             lambda: os.replace("synthetic-report", "synthetic-receipt")),
            ("block-real-rust-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("block-real-original-suite-import",
             lambda: importlib.import_module(ORIGINAL_MODULE)),
            ("block-real-original-candidate-worker",
             lambda: subprocess.Popen([str(PINNED_PYTHON)])),
            ("block-real-background-original-worker",
             lambda: threading.Thread(target=lambda: None).start()),
            ("block-real-original-timing-clock",
             lambda: time.perf_counter()),
            ("block-real-original-wall-clock", lambda: time.time()),
            ("block-real-original-garbage-collection", lambda: gc.collect()),
        ):
            reject(name, action)
        accept("reject-at-least-40-genuinely-distinct-original-forgeries",
               len(rejected) >= 40 and len(rejected) == len(set(rejected)))
        accept("prove-ten-real-original-recorder-side-effects-remain-zero",
               all(effects[key] == 0 for key in (
                   "file_reads", "file_writes", "candidate_imports",
                   "reference_imports", "workers_started", "threads_started",
                   "clock_samples", "gc_collections", "hidden_cases_read",
                   "performance_files_read",
               )))
        accept("prove-seven-independent-side-effect-categories-are-blocked",
               all(effects[key] > 0 for key in (
                   "blocked_reads", "blocked_writes", "blocked_imports",
                   "blocked_workers", "blocked_threads", "blocked_clocks",
                   "blocked_gc_collections",
               )))
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "original_suite_relative": ORIGINAL_RELATIVE,
        "original_suite_sha256": ORIGINAL_SHA256,
        "test_harness_relative": TEST_HARNESS_RELATIVE,
        "test_harness_sha256": TEST_HARNESS_SHA256,
        "public_recorder_relative": PUBLIC_RECORDER_RELATIVE,
        "public_recorder_sha256": PUBLIC_RECORDER_SHA256,
        "frozen_actual_matrix_sha256": MATRIX_SHA256,
        "frozen_actual_baseline_records_sha256": BASELINE_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVERS,
        "synthetic_baseline_pass_count": 151,
        "synthetic_baseline_skip_count": 1,
        "complete_synthetic_baseline_record_count": PUBLIC_METHODS,
        "complete_synthetic_candidate_record_count": PUBLIC_METHODS,
        "synthetic_original_method_guard_checks": GUARD_CHECKS,
        "synthetic_actual_object_identity_guarded": True,
        "synthetic_public_type_names_used_for_ownership": False,
        "synthetic_failures_preserved": 1,
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "effects": effects,
        "actual_original_suite_invocations": 0,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "actual_clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "files_written": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "synthetic": True,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Durably preserve one complete frozen original CPython run",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record", action="store_true")
    parser.add_argument("--label")
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "label", "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "a synthetic original control must not pin or execute a candidate")
        document = source_self_test()
    else:
        require(type(options.label) is str,
                "explicit original recording requires an actual fresh label")
        source = validate_digest(
            options.oracle_source_sha256, "frozen original-suite controller",
        )
        matrix = validate_digest(options.matrix_sha256,
                                 "frozen 165-method original matrix")
        require(source == ORIGINAL_SHA256 and matrix == MATRIX_SHA256,
                "pin the exact unchanged original-suite source and method matrix")
        pins = OwnerPins(
            original=source, public_recorder=PUBLIC_RECORDER_SHA256,
            matrix=matrix, baseline=BASELINE_SHA256,
            candidate=validate_digest(
                options.candidate_source_sha256, "original Rust adapter",
            ),
            native_engine=validate_digest(
                options.native_engine_sha256, "original native Rust engine",
            ),
            native_bridge=validate_digest(
                options.native_bridge_sha256, "original native Python bridge",
            ),
        )
        document = record_original(options.label, pins)
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecorderError as error:
        print("frozen original CPython recording failed closed: " + str(error),
              file=sys.stderr)
        raise SystemExit(1) from error
