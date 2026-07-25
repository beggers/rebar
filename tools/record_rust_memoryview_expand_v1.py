#!/usr/bin/env python3
"""Preserve one complete, unchanged memoryview Match.expand differential run.

Only explicit --record starts the frozen memoryview oracle. Its candidate CLI
does not publish full baseline or candidate vectors; this recorder never
invents them. It preserves all 768 case obligations, every actual complete
mismatch, the complete canonical result and both original process streams.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass
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
SOURCE_RELATIVE = "tools/record_rust_memoryview_expand_v1.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SCHEMA = "rebar-frozen-rust-memoryview-expand-recorder-v1"
ORIGINAL_RELATIVE = "tools/rust_memoryview_expand_differential_v1.py"
ORIGINAL_MODULE = "tools.rust_memoryview_expand_differential_v1"
ORIGINAL_SHA256 = (
    "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6"
)
ORIGINAL_SCHEMA = "rebar-independent-rust-memoryview-expand-differential-v1"
PUBLIC_RECORDER_RELATIVE = "tools/record_rust_public_correctness_v1.py"
PUBLIC_RECORDER_MODULE = "tools.record_rust_public_correctness_v1"
PUBLIC_RECORDER_SHA256 = (
    "41b749696cc498be4e2b5d63866fb103d29d54e1277dae6a5659fd63302daa49"
)
MATRIX_SHA256 = (
    "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60"
)
BASELINE_SHA256 = (
    "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75"
)
PUBLISHED_SEED = 0x4D45_5850_414E_4431
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
CANDIDATE_RELATIVE = "candidates/rust_candidate.py"
NATIVE_ENGINE_RELATIVE = "candidates/_rust_engine.so"
NATIVE_BRIDGE_RELATIVE = (
    "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
)
FAMILIES = (
    "measured-mutable-memoryview", "measured-readonly-memoryview",
    "sliced-mutable-memoryview", "sliced-readonly-memoryview",
    "strided-mutable-memoryview", "strided-readonly-memoryview",
    "released-before-search", "released-after-match",
    "bytearray-control", "bytes-control",
    "empty-mutable-memoryview", "empty-readonly-memoryview",
    "named-capture-template", "numbered-capture-template",
    "octal-escape-template", "escaped-backslash-template",
    "unmatched-optional-capture", "missing-numbered-capture",
    "missing-named-capture", "malformed-escape-template",
    "wrong-template-type", "unicode-text-separation",
    "mutable-source-after-match", "buffer-exporter-error",
)
VARIANTS_PER_FAMILY = 32
CASE_COUNT = 768
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 128 * 1024 * 1024
RESULT_FIELDS = {
    "schema", "status", "python", "published_seed", "matrix_sha256",
    "baseline_records_sha256", "candidate_records_sha256",
    "case_denominator", "actual_baseline_cases", "actual_candidate_cases",
    "mismatch_count", "mismatches_by_family", "all_mismatches",
    "first_mismatch", "baseline_pid", "candidate_pid", "native_engine",
    "actual_candidate_workers", "clock_samples", "timing_trials_run",
    "benchmark_files_read", "hidden_cases_read", "files_written",
    "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
}
MISMATCH_FIELDS = {
    "case", "family", "input", "baseline_outcome", "rust_outcome",
}

class RecorderError(Exception):
    """Reject a substituted memoryview result or unsafe publication."""

class SourceOnlyError(RecorderError):
    """A synthetic control attempted an actual external effect."""

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

def authenticate_sources(
    pins: OwnerPins,
) -> tuple[Any, Any, list[dict[str, Any]]]:
    verify_runtime()
    require(
        pins.original == ORIGINAL_SHA256
        and pins.public_recorder == PUBLIC_RECORDER_SHA256
        and pins.matrix == MATRIX_SHA256
        and pins.baseline == BASELINE_SHA256,
        "the independently frozen memoryview oracle or baseline changed",
    )
    read_owned_regular(
        ORIGINAL_RELATIVE, pins.original, maximum=MAX_SOURCE_BYTES,
    )
    read_owned_regular(
        PUBLIC_RECORDER_RELATIVE, pins.public_recorder,
        maximum=MAX_SOURCE_BYTES,
    )
    oracle = importlib.import_module(ORIGINAL_MODULE)
    recorder = importlib.import_module(PUBLIC_RECORDER_MODULE)
    require(
        oracle.__name__ == ORIGINAL_MODULE
        and os.path.abspath(oracle.__file__) == str(ROOT / ORIGINAL_RELATIVE)
        and oracle.ROOT == ROOT
        and oracle.PINNED_PYTHON == PINNED_PYTHON
        and oracle.SCHEMA == ORIGINAL_SCHEMA
        and oracle.MATRIX_SHA256 == pins.matrix
        and oracle.BASELINE_SHA256 == pins.baseline
        and oracle.PUBLISHED_SEED == PUBLISHED_SEED
        and tuple(oracle.FAMILIES) == FAMILIES
        and oracle.VARIANTS_PER_FAMILY == VARIANTS_PER_FAMILY
        and oracle.CASE_COUNT == CASE_COUNT
        and recorder.__name__ == PUBLIC_RECORDER_MODULE
        and os.path.abspath(recorder.__file__)
        == str(ROOT / PUBLIC_RECORDER_RELATIVE)
        and recorder.ROOT == ROOT
        and recorder.PINNED_PYTHON == PINNED_PYTHON
        and recorder.CANDIDATE_RELATIVE == CANDIDATE_RELATIVE
        and recorder.NATIVE_ENGINE_RELATIVE == NATIVE_ENGINE_RELATIVE,
        "the frozen memoryview source, seed, families, or authenticator changed",
    )
    oracle.verify_runtime()
    matrix = oracle.build_matrix()
    require(
        oracle.validate_matrix(matrix) == pins.matrix
        and digest(matrix) == pins.matrix
        and len(matrix) == CASE_COUNT,
        "all 768 original 24-family memoryview cases are mandatory",
    )
    verify_runtime()
    return oracle, recorder, matrix


def validate_expand_result(
    result: Any,
    matrix: list[dict[str, Any]],
    pins: OwnerPins,
    actual_owners: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        type(result) is dict and set(result) == RESULT_FIELDS,
        "the complete unchanged memoryview candidate document is mandatory",
    )
    require(
        type(matrix) is list and len(matrix) == CASE_COUNT
        and digest(matrix) == pins.matrix
        and valid_provenance(actual_owners, pins),
        "the complete frozen memoryview matrix and three native owners changed",
    )
    for family in FAMILIES:
        require(
            sum(row.get("family") == family for row in matrix)
            == VARIANTS_PER_FAMILY,
            "an entire 32-case memoryview family disappeared: " + family,
        )
    expected = {
        "schema": ORIGINAL_SCHEMA + "-candidate-result",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": pins.matrix,
        "baseline_records_sha256": pins.baseline,
        "case_denominator": CASE_COUNT,
        "actual_baseline_cases": CASE_COUNT,
        "actual_candidate_cases": CASE_COUNT,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for name, value in expected.items():
        require(
            result.get(name) == value,
            "an original memoryview observation changed: " + name,
        )
    validate_digest(
        result.get("candidate_records_sha256"),
        "original complete internal candidate-vector fingerprint",
    )
    baseline_pid = positive_int(result.get("baseline_pid"), "baseline PID")
    candidate_pid = positive_int(result.get("candidate_pid"), "candidate PID")
    require(
        baseline_pid != candidate_pid,
        "the actual memoryview candidate and reference were not isolated",
    )
    require(
        result.get("native_engine") == actual_owners["native_engine"],
        "the genuine memoryview worker used a substituted native engine",
    )
    family_counts = result.get("mismatches_by_family")
    require(
        type(family_counts) is dict
        and set(family_counts) == set(FAMILIES)
        and all(
            type(family_counts[family]) is int
            and 0 <= family_counts[family] <= VARIANTS_PER_FAMILY
            for family in FAMILIES
        ),
        "the complete 24-family memoryview mismatch denominator changed",
    )
    mismatches = result.get("all_mismatches")
    require(
        type(mismatches) is list
        and 0 <= len(mismatches) <= CASE_COUNT
        and type(result.get("mismatch_count")) is int
        and result["mismatch_count"] == len(mismatches)
        and result.get("first_mismatch")
        == (mismatches[0] if mismatches else None)
        and result.get("status") == ("FAIL" if mismatches else "PASS"),
        "a genuine first memoryview failure or complete mismatch was hidden",
    )
    positions = {case["case"]: index for index, case in enumerate(matrix)}
    previous = -1
    derived_counts = {family: 0 for family in FAMILIES}
    for mismatch in mismatches:
        require(
            type(mismatch) is dict and set(mismatch) == MISMATCH_FIELDS
            and mismatch.get("case") in positions,
            "a complete original memoryview mismatch was omitted",
        )
        position = positions[mismatch["case"]]
        require(
            position > previous,
            "a memoryview mismatch was reordered, repeated, or omitted",
        )
        original_case = matrix[position]
        require(
            mismatch["family"] == original_case["family"]
            and mismatch["input"] == original_case,
            "an exact original memoryview input or family was substituted",
        )
        baseline = mismatch.get("baseline_outcome")
        rust = mismatch.get("rust_outcome")
        require(
            type(baseline) is dict and type(rust) is dict
            and baseline != rust
            and baseline.get("status") in ("return", "raise")
            and rust.get("status") in ("return", "raise")
            and type(baseline.get("warnings")) is list
            and type(rust.get("warnings")) is list,
            "a complete real memoryview warning or exception was hidden",
        )
        derived_counts[mismatch["family"]] += 1
        previous = position
    require(
        derived_counts == family_counts
        and sum(family_counts.values()) == len(mismatches),
        "an actual memoryview mismatch family was hidden or fabricated",
    )
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
    *,
    label: str,
    stdout: bytes,
    stderr: bytes,
    returncode: int,
    process_pid: int,
    matrix: list[dict[str, Any]],
    pins: OwnerPins,
    owners_before: Mapping[str, Any],
    owners_after: Mapping[str, Any] | None,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    slug = validate_label(label)
    positive_int(process_pid, "single memoryview process PID")
    require(
        type(returncode) is int and valid_provenance(owners_before, pins),
        "the genuine memoryview process and pre-run owners are mandatory",
    )
    captured_stdout = capture_stream(stdout, "full memoryview stdout")
    captured_stderr = capture_stream(stderr, "full memoryview stderr")
    result: dict[str, Any] | None = None
    failure: str | None = post_run_error
    if (
        owners_after is None
        or not valid_provenance(owners_after, pins)
        or dict(owners_after) != dict(owners_before)
    ):
        failure = failure or "a memoryview owner changed during the real run"
    try:
        parsed = decode_canonical(stdout, "complete memoryview process output")
        result = validate_expand_result(parsed, matrix, pins, owners_before)
        require(
            returncode == (0 if result["status"] == "PASS" else 1),
            "the actual memoryview failure exit was misclassified",
        )
    except (RecorderError, ValueError, TypeError, KeyError) as error:
        failure = (failure + "; " if failure else "") + str(error)
    status = (
        "PASS"
        if result is not None and result["status"] == "PASS" and failure is None
        else "FAIL"
    )
    return {
        "schema": SCHEMA + "-complete-first-run-report",
        "status": status,
        "label": slug,
        "python": "3.14.6",
        "oracle_source_relative": ORIGINAL_RELATIVE,
        "oracle_source_sha256": pins.original,
        "public_recorder_relative": PUBLIC_RECORDER_RELATIVE,
        "public_recorder_sha256": pins.public_recorder,
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": pins.matrix,
        "case_denominator": CASE_COUNT,
        "family_count": len(FAMILIES),
        "variants_per_family": VARIANTS_PER_FAMILY,
        "families": list(FAMILIES),
        "baseline_records_sha256": (
            result["baseline_records_sha256"] if result is not None else None
        ),
        "candidate_records_sha256": (
            result["candidate_records_sha256"] if result is not None else None
        ),
        "actual_baseline_cases": (
            result["actual_baseline_cases"] if result is not None else 0
        ),
        "actual_candidate_cases": (
            result["actual_candidate_cases"] if result is not None else 0
        ),
        "baseline_records_available_from_frozen_candidate_cli": False,
        "candidate_records_available_from_frozen_candidate_cli": False,
        "full_vectors": "NOT AVAILABLE FROM IMMUTABLE CANDIDATE CLI",
        "mismatch_count": result["mismatch_count"] if result is not None else 0,
        "mismatches_by_family": (
            result["mismatches_by_family"] if result is not None else None
        ),
        "all_mismatches": result["all_mismatches"] if result is not None else [],
        "first_mismatch": result["first_mismatch"] if result is not None else None,
        "all_emitted_mismatches_preserved": result is not None,
        "complete_original_candidate_result": result,
        "complete_original_process_stdout": captured_stdout,
        "complete_original_process_stderr": captured_stderr,
        "original_process_pid": process_pid,
        "original_process_returncode": returncode,
        "actual_original_oracle_invocations": 1,
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
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def run_exactly_one_expand(
    pins: OwnerPins,
) -> tuple[bytes, bytes, int, int]:
    verify_runtime()
    arguments = [
        str(PINNED_PYTHON),
        "-I",
        "-B",
        str(ROOT / ORIGINAL_RELATIVE),
        "--candidate",
    ]
    process = subprocess.Popen(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(ROOT),
        shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "LC_ALL": "C",
            "PATH": "/usr/bin:/bin",
        },
    )
    # The immutable CLI accepts no owner flags, timeout, clock, or retry.
    stdout, stderr = process.communicate()
    require(
        type(stdout) is bytes and type(stderr) is bytes
        and type(process.returncode) is int,
        "the one complete memoryview process pipe was not collected",
    )
    return (
        stdout,
        stderr,
        process.returncode,
        positive_int(process.pid, "actual memoryview controller PID"),
    )


def record_expand(label: str, pins: OwnerPins) -> dict[str, Any]:
    slug = validate_label(label)
    for key in (
        "original",
        "public_recorder",
        "matrix",
        "baseline",
        "candidate",
        "native_engine",
        "native_bridge",
    ):
        validate_digest(getattr(pins, key), key)
    _, recorder, matrix = authenticate_sources(pins)
    owners_before = candidate_owners(recorder, pins)
    with preflight_fresh_outputs(slug) as preflight:
        verify_retained_directory(preflight)
        require(
            candidate_owners(recorder, pins) == owners_before,
            "a real memoryview native owner changed before its one process",
        )
        stdout, stderr, returncode, process_pid = run_exactly_one_expand(pins)
        owners_after: dict[str, Any] | None = None
        post_run_error: str | None = None
        try:
            owners_after = candidate_owners(recorder, pins)
        except (
            RecorderError,
            OSError,
            ValueError,
            TypeError,
            recorder.RecorderError,
        ) as error:
            post_run_error = (
                "post-run exact memoryview owner verification failed: "
                + str(error)
            )
        complete = build_complete_report(
            label=slug,
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
            process_pid=process_pid,
            matrix=matrix,
            pins=pins,
            owners_before=owners_before,
            owners_after=owners_after,
            post_run_error=post_run_error,
        )
        verify_runtime()
        report_publication, actual_report = publish_fresh(
            preflight, complete, kind="report",
        )
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS",
            "correctness_status": complete["status"],
            "label": slug,
            "python": "3.14.6",
            "oracle_source_relative": ORIGINAL_RELATIVE,
            "oracle_source_sha256": pins.original,
            "public_recorder_relative": PUBLIC_RECORDER_RELATIVE,
            "public_recorder_sha256": pins.public_recorder,
            "published_seed": PUBLISHED_SEED,
            "matrix_sha256": pins.matrix,
            "case_denominator": CASE_COUNT,
            "family_count": len(FAMILIES),
            "variants_per_family": VARIANTS_PER_FAMILY,
            "families": list(FAMILIES),
            "baseline_records_sha256": complete["baseline_records_sha256"],
            "candidate_records_sha256": complete["candidate_records_sha256"],
            "actual_baseline_cases": complete["actual_baseline_cases"],
            "actual_candidate_cases": complete["actual_candidate_cases"],
            "baseline_records_available_from_frozen_candidate_cli": False,
            "candidate_records_available_from_frozen_candidate_cli": False,
            "full_vectors": "NOT AVAILABLE FROM IMMUTABLE CANDIDATE CLI",
            "mismatch_count": complete["mismatch_count"],
            "mismatches_by_family": complete["mismatches_by_family"],
            "all_emitted_mismatches_preserved": (
                complete["all_emitted_mismatches_preserved"]
            ),
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
            "candidate_provenance_unchanged": (
                complete["candidate_provenance_unchanged"]
            ),
            "original_process_pid": process_pid,
            "original_process_returncode": returncode,
            "original_process_stdout_sha256": (
                complete["complete_original_process_stdout"]["sha256"]
            ),
            "original_process_stdout_bytes": (
                complete["complete_original_process_stdout"]["bytes"]
            ),
            "original_process_stderr_sha256": (
                complete["complete_original_process_stderr"]["sha256"]
            ),
            "original_process_stderr_bytes": (
                complete["complete_original_process_stderr"]["bytes"]
            ),
            "actual_original_oracle_invocations": 1,
            "report_relative": preflight["report_relative"],
            "report_sha256": hashlib.sha256(actual_report).hexdigest(),
            "report_bytes": len(actual_report),
            "report_actual_write_calls": (
                report_publication["actual_write_calls"]
            ),
            "report_file_fsync_completed": True,
            "report_directory_fsync_completed": True,
            "report_complete_readback_verified": True,
            "receipt_complete_readback_required": True,
            "receipt_complete_readback_verified": True,
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
        receipt_publication, actual_receipt = publish_fresh(
            preflight, receipt, kind="receipt",
        )
        verify_runtime()
        return {
            "schema": SCHEMA + "-compact-result",
            "status": complete["status"],
            "label": slug,
            "python": "3.14.6",
            "oracle_source_sha256": pins.original,
            "public_recorder_sha256": pins.public_recorder,
            "matrix_sha256": pins.matrix,
            "baseline_records_sha256": complete["baseline_records_sha256"],
            "candidate_records_sha256": complete["candidate_records_sha256"],
            "case_denominator": CASE_COUNT,
            "family_count": len(FAMILIES),
            "variants_per_family": VARIANTS_PER_FAMILY,
            "actual_baseline_cases": complete["actual_baseline_cases"],
            "actual_candidate_cases": complete["actual_candidate_cases"],
            "mismatch_count": complete["mismatch_count"],
            "mismatches_by_family": complete["mismatches_by_family"],
            "all_emitted_mismatches_preserved": (
                complete["all_emitted_mismatches_preserved"]
            ),
            "baseline_records_available_from_frozen_candidate_cli": False,
            "candidate_records_available_from_frozen_candidate_cli": False,
            "candidate_source_sha256": pins.candidate,
            "native_engine_sha256": pins.native_engine,
            "native_bridge_sha256": pins.native_bridge,
            "original_process_returncode": returncode,
            "actual_original_oracle_invocations": 1,
            "report_publication": report_publication,
            "receipt_publication": receipt_publication,
            "receipt_complete_readback_verified": True,
            "receipt_verified_bytes": len(actual_receipt),
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
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
    list[dict[str, Any]],
    OwnerPins,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    matrix: list[dict[str, Any]] = []
    for family in FAMILIES:
        for variant in range(VARIANTS_PER_FAMILY):
            index = len(matrix)
            matrix.append({
                "case": "memoryview-expand.v1." + format(index, "04d"),
                "family": family,
                "variant": variant,
                "flags": 0,
                "pattern": {"kind": "bytes", "hex": "61"},
                "subject": {
                    "kind": "readonly-memoryview",
                    "hex": "61",
                    "start": 0,
                    "stop": 1,
                    "step": 1,
                },
                "template": {"kind": "bytes", "hex": "61"},
                "mutation": "none",
            })
    baseline_records = [
        {
            "case": case["case"],
            "family": case["family"],
            "outcome": {
                "status": "return",
                "stage": "expand",
                "value": {"kind": "bytes", "hex": "61"},
                "match_before": None,
                "source_after": None,
                "mutation": None,
                "warnings": [],
            },
        }
        for case in matrix
    ]
    pins = OwnerPins(
        original=ORIGINAL_SHA256,
        public_recorder=PUBLIC_RECORDER_SHA256,
        matrix=digest(matrix),
        baseline=digest(baseline_records),
        candidate="12" * 32,
        native_engine="34" * 32,
        native_bridge="56" * 32,
    )
    actual_owners = {
        "source": {
            "relative": CANDIDATE_RELATIVE,
            "sha256": pins.candidate,
            "bytes": 11,
            "device": 17,
            "inode": 101,
        },
        "native_engine": {
            "relative": NATIVE_ENGINE_RELATIVE,
            "sha256": pins.native_engine,
            "bytes": 23,
            "device": 17,
            "inode": 102,
        },
        "native_bridge": {
            "relative": NATIVE_BRIDGE_RELATIVE,
            "sha256": pins.native_bridge,
            "bytes": 31,
            "device": 17,
            "inode": 103,
        },
    }

    def make(failures: bool) -> dict[str, Any]:
        counts = {family: 0 for family in FAMILIES}
        mismatches: list[dict[str, Any]] = []
        candidate_records = copy.deepcopy(baseline_records)
        limits = {
            "released-after-match": 32,
            "buffer-exporter-error": 16,
            "wrong-template-type": 5,
        }
        if failures:
            for index, case in enumerate(matrix):
                if case["variant"] >= limits.get(case["family"], 0):
                    continue
                observed = {
                    "status": "raise",
                    "stage": "expand",
                    "exception": {
                        "kind": "ordinary-python-error",
                        "module": "builtins",
                        "type": "ValueError",
                        "args": {
                            "kind": "tuple",
                            "items": ["synthetic real memoryview mismatch"],
                        },
                    },
                    "match_before": None,
                    "source_after": None,
                    "mutation": None,
                    "warnings": [],
                }
                candidate_records[index]["outcome"] = observed
                counts[case["family"]] += 1
                mismatches.append({
                    "case": case["case"],
                    "family": case["family"],
                    "input": case,
                    "baseline_outcome": baseline_records[index]["outcome"],
                    "rust_outcome": observed,
                })
        return {
            "schema": ORIGINAL_SCHEMA + "-candidate-result",
            "status": "FAIL" if mismatches else "PASS",
            "python": "3.14.6",
            "published_seed": PUBLISHED_SEED,
            "matrix_sha256": pins.matrix,
            "baseline_records_sha256": pins.baseline,
            "candidate_records_sha256": digest(candidate_records),
            "case_denominator": CASE_COUNT,
            "actual_baseline_cases": CASE_COUNT,
            "actual_candidate_cases": CASE_COUNT,
            "mismatch_count": len(mismatches),
            "mismatches_by_family": counts,
            "all_mismatches": mismatches,
            "first_mismatch": mismatches[0] if mismatches else None,
            "baseline_pid": 2001,
            "candidate_pid": 2002,
            "native_engine": dict(actual_owners["native_engine"]),
            "actual_candidate_workers": 1,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "files_written": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }

    return matrix, pins, actual_owners, make(False), make(True)

def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(
            type(name) is str and name not in accepted and bool(condition),
            "a real memoryview recorder positive control failed: " + name,
        )
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(
            type(name) is str and name not in rejected and callable(action),
            "a genuine memoryview poison control was duplicated",
        )
        try:
            action()
        except (RecorderError, ValueError, TypeError, KeyError, OSError):
            rejected.append(name)
            return
        raise RecorderError("a forged memoryview result was accepted: " + name)

    with source_only_boundary() as effects:
        matrix, pins, actual_owners, passed, failed = synthetic_documents()
        require(
            validate_expand_result(passed, matrix, pins, actual_owners)
            is passed
            and validate_expand_result(failed, matrix, pins, actual_owners)
            is failed,
            "complete synthetic memoryview PASS and FAIL were not preserved",
        )
        passing = build_complete_report(
            label="synthetic-memoryview-expand-pass-v1",
            stdout=canonical(passed),
            stderr=b"",
            returncode=0,
            process_pid=501,
            matrix=matrix,
            pins=pins,
            owners_before=actual_owners,
            owners_after=copy.deepcopy(actual_owners),
        )
        failing = build_complete_report(
            label="synthetic-memoryview-expand-fail-v1",
            stdout=canonical(failed),
            stderr=b"complete synthetic memoryview diagnostic\n",
            returncode=1,
            process_pid=502,
            matrix=matrix,
            pins=pins,
            owners_before=actual_owners,
            owners_after=copy.deepcopy(actual_owners),
        )
        malformed = build_complete_report(
            label="synthetic-memoryview-expand-malformed-v1",
            stdout=b"complete synthetic malformed memoryview process\n",
            stderr=b"complete synthetic memoryview traceback\n",
            returncode=2,
            process_pid=503,
            matrix=matrix,
            pins=pins,
            owners_before=actual_owners,
            owners_after=copy.deepcopy(actual_owners),
        )
        accept(
            "preserve-every-one-of-768-original-memoryview-cases",
            len(matrix) == CASE_COUNT and passing["case_denominator"] == 768,
        )
        accept(
            "preserve-all-24-families-and-all-32-variants",
            len(FAMILIES) == 24 and VARIANTS_PER_FAMILY == 32
            and all(
                sum(row["family"] == family for row in matrix) == 32
                for family in FAMILIES
            ),
        )
        accept(
            "preserve-all-53-source-ordered-three-family-memoryview-failures",
            failing["status"] == "FAIL"
            and failing["mismatch_count"] == 53
            and len(failing["all_mismatches"]) == 53
            and failing["mismatches_by_family"]["released-after-match"] == 32
            and failing["mismatches_by_family"]["buffer-exporter-error"] == 16
            and failing["mismatches_by_family"]["wrong-template-type"] == 5,
        )
        accept(
            "preserve-complete-canonical-oracle-result-and-both-streams",
            failing["complete_original_candidate_result"] == failed
            and failing["complete_original_process_stdout"]["complete"] is True
            and failing["complete_original_process_stderr"]["complete"] is True,
        )
        accept(
            "preserve-real-failure-and-exit-without-dropping-mismatches",
            failing["original_process_returncode"] == 1
            and failing["all_emitted_mismatches_preserved"] is True,
        )
        accept(
            "preserve-malformed-full-stdout-and-stderr-without-fake-results",
            malformed["status"] == "FAIL"
            and malformed["complete_original_candidate_result"] is None
            and malformed["complete_original_process_stdout"]["complete"] is True
            and malformed["complete_original_process_stderr"]["complete"] is True
            and malformed["actual_baseline_cases"] == 0
            and malformed["actual_candidate_cases"] == 0,
        )
        accept(
            "honestly-mark-unpublished-768-outcome-vectors-not-available",
            passing["baseline_records_available_from_frozen_candidate_cli"]
            is False
            and passing["candidate_records_available_from_frozen_candidate_cli"]
            is False
            and passing["full_vectors"]
            == "NOT AVAILABLE FROM IMMUTABLE CANDIDATE CLI",
        )
        accept(
            "authenticate-three-exact-native-owners-before-and-after",
            valid_provenance(actual_owners, pins)
            and passing["candidate_provenance_unchanged"] is True,
        )
        accept(
            "predeclare-exactly-two-distinct-exclusive-public-report-paths",
            approved_paths("synthetic-memoryview-expand-pass-v1")
            == (
                APPROVED_DIRECTORY
                + "/synthetic-memoryview-expand-pass-v1.json",
                APPROVED_DIRECTORY
                + "/synthetic-memoryview-expand-pass-v1-publication-receipt.json",
            ),
        )
        accept(
            "record-no-hidden-timings-performance-or-winner",
            passing["hidden_cases_read"] == 0
            and passing["clock_samples"] == 0
            and passing["timing_trials_run"] == 0
            and passing["performance"] == "NOT MEASURED"
            and passing["candidate_qualified_for_hidden_benchmark"] is False
            and passing["final_winner_selected"] is False,
        )

        for index, key in enumerate(sorted(RESULT_FIELDS)):
            forged = dict(passed)
            forged.pop(key)
            reject(
                "reject-omitted-complete-memoryview-result-field-"
                + format(index, "02d"),
                lambda forged=forged: validate_expand_result(
                    forged, matrix, pins, actual_owners,
                ),
            )
        for index, key, value in (
            (0, "case_denominator", 767),
            (1, "actual_baseline_cases", 767),
            (2, "actual_candidate_cases", 767),
            (3, "matrix_sha256", "ab" * 32),
            (4, "baseline_records_sha256", "cd" * 32),
            (5, "published_seed", PUBLISHED_SEED + 1),
            (6, "actual_candidate_workers", 0),
            (7, "clock_samples", 1),
            (8, "timing_trials_run", 1),
            (9, "benchmark_files_read", 1),
            (10, "hidden_cases_read", 1),
            (11, "files_written", 1),
            (12, "performance", "FASTER"),
            (13, "candidate_qualified_for_hidden_benchmark", True),
            (14, "final_winner_selected", True),
            (15, "status", "FAIL"),
            (16, "baseline_pid", passed["candidate_pid"]),
            (17, "candidate_records_sha256", "0" * 64),
        ):
            forged = dict(passed)
            forged[key] = value
            reject(
                "reject-false-memoryview-count-owner-or-effect-"
                + format(index, "02d"),
                lambda forged=forged: validate_expand_result(
                    forged, matrix, pins, actual_owners,
                ),
            )
        for index, key, transform in (
            (0, "all_mismatches", lambda rows: rows[:-1]),
            (1, "all_mismatches", lambda rows: list(reversed(rows))),
            (2, "all_mismatches", lambda rows: rows[1:]),
            (3, "mismatch_count", lambda count: count - 1),
            (4, "first_mismatch", lambda _: None),
            (5, "mismatches_by_family", lambda rows: {
                family: (
                    count + 1 if family == "released-after-match" else count
                )
                for family, count in rows.items()
            }),
            (6, "mismatches_by_family", lambda rows: {
                family: count
                for family, count in rows.items()
                if family != "buffer-exporter-error"
            }),
        ):
            forged = dict(failed)
            forged[key] = transform(failed[key])
            reject(
                "reject-clipped-reordered-or-concealed-memoryview-mismatch-"
                + format(index, "02d"),
                lambda forged=forged: validate_expand_result(
                    forged, matrix, pins, actual_owners,
                ),
            )
        for index, family in enumerate(FAMILIES):
            forged = dict(failed)
            counts = dict(failed["mismatches_by_family"])
            counts[family] = VARIANTS_PER_FAMILY + 1
            forged["mismatches_by_family"] = counts
            reject(
                "reject-overflowed-original-memoryview-family-"
                + format(index, "02d"),
                lambda forged=forged: validate_expand_result(
                    forged, matrix, pins, actual_owners,
                ),
            )
        for index, slug in enumerate((
            "", ".", "..", "../escape", "/tmp/escape", "UPPER",
            "a space", "has_underscore", "two--hyphens", "-leading",
            "trailing-", "line\nbreak", "slash/component",
            "back\\slash", "\x00", "a" * 65,
        )):
            reject(
                "reject-escaping-memoryview-report-label-"
                + format(index, "02d"),
                lambda slug=slug: validate_label(slug),
            )
        for index, invalid in enumerate((
            None,
            0,
            True,
            "",
            "0" * 64,
            "A" * 64,
            "g" * 64,
            "ab" * 31,
            "ab" * 33,
            ORIGINAL_SHA256.upper(),
            ORIGINAL_SHA256 + "0",
        )):
            reject(
                "reject-unpinned-memoryview-source-or-native-owner-"
                + format(index, "02d"),
                lambda invalid=invalid: validate_digest(
                    invalid, "synthetic memoryview owner poison",
                ),
            )
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
            forged = copy.deepcopy(actual_owners)
            forged[kind][key] = value
            reject(
                "reject-substituted-memoryview-three-native-owners-"
                + format(index, "02d"),
                lambda forged=forged: require(
                    valid_provenance(forged, pins),
                    "a forged memoryview native owner was rejected",
                ),
            )
        for name, action in (
            (
                "block-real-memoryview-oracle-source-read",
                lambda: builtins.open(ORIGINAL_RELATIVE, "rb"),
            ),
            (
                "block-real-public-recorder-source-read",
                lambda: io.open(PUBLIC_RECORDER_RELATIVE, "rb"),
            ),
            (
                "block-real-memoryview-evidence-open",
                lambda: os.open(
                    approved_paths("synthetic-memoryview-expand-pass-v1")[0],
                    os.O_RDONLY,
                ),
            ),
            (
                "block-real-memoryview-evidence-write",
                lambda: os.write(1, b"forbidden"),
            ),
            (
                "block-real-memoryview-evidence-replacement",
                lambda: os.replace("synthetic-report", "synthetic-receipt"),
            ),
            (
                "block-real-memoryview-rust-candidate-import",
                lambda: importlib.import_module("candidates.rust_candidate"),
            ),
            (
                "block-real-memoryview-oracle-module-import",
                lambda: importlib.import_module(ORIGINAL_MODULE),
            ),
            (
                "block-real-memoryview-candidate-worker",
                lambda: subprocess.Popen([str(PINNED_PYTHON)]),
            ),
            (
                "block-real-memoryview-background-worker",
                lambda: threading.Thread(target=lambda: None).start(),
            ),
            (
                "block-real-memoryview-performance-clock",
                lambda: time.perf_counter(),
            ),
            (
                "block-real-memoryview-wall-clock",
                lambda: time.time(),
            ),
            (
                "block-real-memoryview-garbage-collection",
                lambda: gc.collect(),
            ),
        ):
            reject(name, action)
        accept(
            "reject-at-least-40-distinct-real-memoryview-tamper-controls",
            len(rejected) >= 40 and len(rejected) == len(set(rejected)),
        )
        accept(
            "prove-ten-real-memoryview-recorder-effects-are-zero",
            all(effects[key] == 0 for key in (
                "file_reads",
                "file_writes",
                "candidate_imports",
                "reference_imports",
                "workers_started",
                "threads_started",
                "clock_samples",
                "gc_collections",
                "hidden_cases_read",
                "performance_files_read",
            )),
        )
        accept(
            "prove-seven-independent-real-side-effects-are-blocked",
            all(effects[key] > 0 for key in (
                "blocked_reads",
                "blocked_writes",
                "blocked_imports",
                "blocked_workers",
                "blocked_threads",
                "blocked_clocks",
                "blocked_gc_collections",
            )),
        )
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_relative": ORIGINAL_RELATIVE,
        "oracle_source_sha256": ORIGINAL_SHA256,
        "public_recorder_relative": PUBLIC_RECORDER_RELATIVE,
        "public_recorder_sha256": PUBLIC_RECORDER_SHA256,
        "frozen_matrix_sha256": MATRIX_SHA256,
        "frozen_baseline_records_sha256": BASELINE_SHA256,
        "case_denominator": CASE_COUNT,
        "family_count": len(FAMILIES),
        "variants_per_family": VARIANTS_PER_FAMILY,
        "synthetic_failure_count": 53,
        "synthetic_released_after_match_failures": 32,
        "synthetic_buffer_exporter_failures": 16,
        "synthetic_wrong_template_failures": 5,
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "effects": effects,
        "actual_original_oracle_invocations": 0,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "synthetic": True,
    }

def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Durably preserve one complete frozen memoryview Match.expand run"
        ),
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
        require(
            all(getattr(options, name) is None for name in (
                "label",
                "oracle_source_sha256",
                "matrix_sha256",
                "candidate_source_sha256",
                "native_engine_sha256",
                "native_bridge_sha256",
            )),
            "a synthetic memoryview control cannot pin or run a candidate",
        )
        document = source_self_test()
    else:
        require(
            type(options.label) is str,
            "actual memoryview recording requires an exact fresh label",
        )
        source = validate_digest(
            options.oracle_source_sha256,
            "independently frozen memoryview oracle",
        )
        matrix = validate_digest(
            options.matrix_sha256,
            "independently frozen memoryview case matrix",
        )
        require(
            source == ORIGINAL_SHA256 and matrix == MATRIX_SHA256,
            "pin the exact unchanged memoryview oracle and all 768 cases",
        )
        pins = OwnerPins(
            original=source,
            public_recorder=PUBLIC_RECORDER_SHA256,
            matrix=matrix,
            baseline=BASELINE_SHA256,
            candidate=validate_digest(
                options.candidate_source_sha256,
                "actual owned memoryview Rust adapter",
            ),
            native_engine=validate_digest(
                options.native_engine_sha256,
                "actual owned memoryview Rust engine",
            ),
            native_bridge=validate_digest(
                options.native_bridge_sha256,
                "actual owned memoryview Python extension",
            ),
        )
        document = record_expand(options.label, pins)
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecorderError as error:
        print(
            "frozen memoryview differential recording failed closed: "
            + str(error),
            file=sys.stderr,
        )
        raise SystemExit(1) from error
