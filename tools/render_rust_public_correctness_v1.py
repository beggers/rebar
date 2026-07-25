#!/usr/bin/env python3
"""Render one authenticated, untimed, public-only Rust correctness experiment.

The renderer never starts or imports a matching candidate.  Only ``--write``
may replace its two exact, repository-owned chart destinations.  ``--check``
only authenticates and compares existing files; ``--self-test`` uses synthetic
in-memory cases and explicitly blocks filesystem, process, timer, and garbage
collection effects.
"""

from __future__ import annotations

import argparse
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
SOURCE_RELATIVE = "tools/render_rust_public_correctness_v1.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SCHEMA = "rebar-rust-public-correctness-render-v1"
CHART_LABEL = "PUBLIC DEVELOPMENT CHECK · NOT FINAL BENCHMARK"
PRACTICE_LABEL = "PUBLIC PRACTICE ONLY; NOT A HIDDEN OR FINAL BENCHMARK"
PUBLIC_CASE_COUNT = 864
PUBLISHED_SEED = 0x5245_4241_525F_5031
CHECKER_RELATIVE = "tools/rust_public_practice_benchmark_v1.py"
CHECKER_MODULE = "tools.rust_public_practice_benchmark_v1"
CHECKER_SHA256 = (
    "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37"
)
RECORDER_RELATIVE = "tools/record_rust_public_correctness_v1.py"
RECORDER_MODULE = "tools.record_rust_public_correctness_v1"
RECORDER_SHA256 = (
    "41b749696cc498be4e2b5d63866fb103d29d54e1277dae6a5659fd63302daa49"
)
MATRIX_SHA256 = (
    "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e"
)
BASELINE_RECORDS_SHA256 = (
    "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c"
)
CANDIDATE_SOURCE_RELATIVE = "candidates/rust_candidate.py"
CANDIDATE_SOURCE_SHA256 = (
    "6341a4e2e456f0f0e28f1f51329630ef1a0c8c9f4f62b8d46b240a1b95a2a169"
)
NATIVE_ENGINE_RELATIVE = "candidates/_rust_engine.so"
NATIVE_ENGINE_SHA256 = (
    "d590300720215718782227dd8da1192047b4781bdb41ed94446cac06ba880e84"
)
NATIVE_BRIDGE_MODULE = "candidates._rust_bridge"
NATIVE_BRIDGE_RELATIVE = (
    "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
)
NATIVE_BRIDGE_SHA256 = (
    "382483ce462aaf31fa067b86db606bc5d2d912796026366a6baf4bed11fb8a77"
)
APPROVED_EVIDENCE_DIRECTORY = "experiments/rust_public_practice_v1"
SVG_RELATIVE = "docs/evidence/rust-public-correctness-v1.svg"
JSON_RELATIVE = "docs/evidence/rust-public-correctness-v1.json"
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_EVIDENCE_BYTES = 32 * 1024 * 1024

OPERATIONS = (
    "module.compile", "module.search", "module.match", "module.fullmatch",
    "module.findall", "module.finditer", "module.split",
    "module.split.positional", "module.sub.literal", "module.sub.positional",
    "module.sub.positional_callback_error", "module.subn.literal",
    "module.subn.positional", "module.subn.positional_callback_error",
    "module.sub.callback", "module.subn.callback", "module.sub.callback_error",
    "pattern.search", "pattern.match", "pattern.fullmatch", "pattern.findall",
    "pattern.finditer", "pattern.split", "pattern.sub.literal",
    "pattern.subn.literal", "pattern.sub.callback", "pattern.subn.callback",
    "pattern.sub.callback_error", "pattern.scanner.search",
    "pattern.scanner.match", "pattern.scanner.loop", "scanner.scan",
    "scanner.scan.callback_error", "match.group", "match.expand",
    "compile.fresh.search",
)
SCANNER_OPERATIONS = tuple(
    operation for operation in OPERATIONS
    if operation.startswith("pattern.scanner.")
    or operation.startswith("scanner.scan")
)
AUTHORIZED_STATIC_READS = frozenset({
    CHECKER_RELATIVE, RECORDER_RELATIVE, SVG_RELATIVE, JSON_RELATIVE,
})
AUTHORIZED_OUTPUTS = frozenset({SVG_RELATIVE, JSON_RELATIVE})


class RenderError(Exception):
    """A frozen public case, real receipt, or chart was changed or omitted."""


class SourceOnlyError(RenderError):
    """A synthetic-only control correctly prevented a real-world effect."""


@dataclass(frozen=True)
class EvidencePins:
    checker: str
    recorder: str
    matrix: str
    baseline: str
    rust: str
    candidate: str
    native_engine: str
    native_bridge: str
    report: str
    receipt: str
    label: str
    report_relative: str
    receipt_relative: str


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RenderError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64 and len(set(value)) > 1
        and all(character in "0123456789abcdef" for character in value),
        "an actual frozen lowercase SHA-256 is required: " + label,
    )
    return value


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == str(ROOT)
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "use exactly isolated, pinned, no-bytecode CPython 3.14.6",
    )
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "a chart renderer must never import or run a matching candidate",
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in document,
                "duplicate evidence keys cannot conceal a failed public case")
        document[key] = value
    return document


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_EVIDENCE_BYTES,
            "a complete bounded canonical document is required: " + label)
    try:
        document = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                RenderError("nonfinite JSON is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise RenderError("invalid complete public evidence: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "a full canonical public document was truncated or altered: " + label)
    return document


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64,
            "an exact bounded lowercase public-record slug is required")
    require(value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for letter in value)
            and "--" not in value,
            "a public-record slug is escaping, ambiguous, or noncanonical")
    return value


def approved_relative_paths(label: Any) -> tuple[str, str]:
    slug = validate_label(label)
    return (
        APPROVED_EVIDENCE_DIRECTORY + "/" + slug + ".json",
        APPROVED_EVIDENCE_DIRECTORY + "/" + slug
        + "-publication-receipt.json",
    )


def _relative_parts(relative: Any, *, output: bool = False) -> tuple[str, ...]:
    require(type(relative) is str,
            "an exact no-symlink repository-owned relative path is mandatory")
    if output:
        require(relative in AUTHORIZED_OUTPUTS,
                "only the two approved deterministic chart outputs are allowed")
    elif relative not in AUTHORIZED_STATIC_READS:
        prefix = APPROVED_EVIDENCE_DIRECTORY + "/"
        require(relative.startswith(prefix) and relative.endswith(".json"),
                "only an explicitly selected frozen public report may be read")
        basename = relative[len(prefix):]
        suffix = "-publication-receipt.json"
        if basename.endswith(suffix):
            label = basename[:-len(suffix)]
            require(relative == approved_relative_paths(label)[1],
                    "a selected receipt has an unapproved public path")
        else:
            require(relative == approved_relative_paths(basename[:-5])[0],
                    "a selected report has an unapproved public path")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "\\" not in relative and "\x00" not in relative,
            "a chart path escaped the repository-owned no-follow directory")
    return parts


def _directory_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )


@contextlib.contextmanager
def owned_parent(relative: str, *, output: bool = False) -> Iterator[tuple[int, str]]:
    parts = _relative_parts(relative, output=output)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), _directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact repository root is not a genuine directory")
        for part in parts[:-1]:
            following = os.open(part, _directory_flags(), dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "a public evidence parent followed a non-directory")
            current = following
        yield current, parts[-1]
    finally:
        errors: list[Exception] = []
        for descriptor in reversed(opened):
            try:
                os.close(descriptor)
            except Exception as error:
                errors.append(error)
        if errors and sys.exc_info()[1] is None:
            raise RenderError("an owned chart descriptor did not close") from errors[0]


def read_owned_regular(relative: str, expected: str, maximum: int) -> bytes:
    validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_EVIDENCE_BYTES,
            "an exact bounded no-follow source or evidence read is required")
    with owned_parent(relative) as (parent, basename):
        flags = (
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        descriptor = os.open(basename, flags, dir_fd=parent)
        try:
            info = os.fstat(descriptor)
            named = os.stat(basename, dir_fd=parent, follow_symlinks=False)
            require(
                stat.S_ISREG(info.st_mode) and stat.S_ISREG(named.st_mode)
                and (info.st_dev, info.st_ino) == (named.st_dev, named.st_ino)
                and 0 < info.st_size <= maximum,
                "a frozen public artifact was replaced, linked, or oversized",
            )
            remaining = info.st_size
            chunks: list[bytes] = []
            while remaining:
                chunk = os.read(descriptor, min(remaining, 1_048_576))
                require(type(chunk) is bytes and bool(chunk),
                        "the complete frozen public artifact was truncated")
                chunks.append(chunk)
                remaining -= len(chunk)
            require(os.read(descriptor, 1) == b"",
                    "a frozen public artifact contains a hidden suffix")
            final = os.fstat(descriptor)
            require(
                (final.st_dev, final.st_ino, final.st_size)
                == (info.st_dev, info.st_ino, info.st_size),
                "the exact authenticated public artifact changed during reading",
            )
        finally:
            os.close(descriptor)
    raw = b"".join(chunks)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "the exact independently frozen public artifact hash changed: " + relative)
    return raw


def authenticate_frozen_modules(pins: EvidencePins) -> tuple[Any, Any, list[dict[str, Any]]]:
    verify_runtime()
    read_owned_regular(CHECKER_RELATIVE, pins.checker, MAX_SOURCE_BYTES)
    read_owned_regular(RECORDER_RELATIVE, pins.recorder, MAX_SOURCE_BYTES)
    checker = importlib.import_module(CHECKER_MODULE)
    recorder = importlib.import_module(RECORDER_MODULE)
    require(
        checker.__name__ == CHECKER_MODULE
        and os.path.abspath(checker.__file__) == str(ROOT / CHECKER_RELATIVE)
        and recorder.__name__ == RECORDER_MODULE
        and os.path.abspath(recorder.__file__) == str(ROOT / RECORDER_RELATIVE)
        and checker.MATRIX_SHA256 == pins.matrix
        and recorder.CHECKER_SHA256 == pins.checker
        and recorder.PUBLIC_MATRIX_SHA256 == pins.matrix
        and recorder.EXPECTED_BASELINE_RECORDS_SHA256 == pins.baseline
        and tuple(checker.OPERATIONS) == OPERATIONS
        and checker.PRACTICE_LABEL == PRACTICE_LABEL
        and checker.PUBLISHED_SEED == PUBLISHED_SEED,
        "the exact frozen recorder, checker, seed, or public API was substituted",
    )
    matrix = checker.build_public_matrix()
    require(
        checker.validate_public_matrix(matrix) == pins.matrix
        and checker.digest(matrix) == pins.matrix
        and digest(matrix) == pins.matrix
        and type(matrix) is list and len(matrix) == PUBLIC_CASE_COUNT,
        "all original 864 public cases and their exact order are mandatory",
    )
    verify_runtime()
    return checker, recorder, matrix


REPORT_FIELDS = {
    "schema", "status", "label", "python", "published_seed", "matrix_sha256",
    "case_denominator", "actual_baseline_cases", "actual_rust_cases",
    "baseline_records_sha256", "rust_records_sha256", "baseline_pid", "rust_pid",
    "mismatch_count", "first_mismatch", "all_mismatches",
    "actual_candidate_workers", "timing_trials_run", "clock_samples",
    "benchmark_files_read", "hidden_cases_read", "files_written", "performance",
    "candidate_qualified_for_hidden_benchmark", "final_winner_selected",
}
MISMATCH_FIELDS = {
    "case", "dataset", "domain", "operation", "lifecycle", "flags", "pattern",
    "subject", "replacement", "limit", "baseline_outcome", "rust_outcome",
}
RECEIPT_FIELDS = {
    "schema", "status", "label", "practice_label", "python",
    "checker_source_relative", "checker_source_sha256",
    "candidate_source_relative", "candidate_source_sha256",
    "candidate_source_bytes", "candidate_source_device", "candidate_source_inode",
    "native_engine_relative", "native_engine_sha256", "native_engine_bytes",
    "native_engine_device", "native_engine_inode", "native_bridge_module",
    "native_bridge_relative", "native_bridge_sha256", "native_bridge_bytes",
    "native_bridge_device", "native_bridge_inode", "public_matrix_sha256",
    "case_denominator", "baseline_records_sha256", "rust_records_sha256",
    "baseline_pid", "rust_pid", "correctness_status", "mismatch_count",
    "all_mismatches_preserved", "report_relative", "report_sha256", "report_bytes",
    "report_actual_write_calls", "report_file_fsync_completed",
    "report_directory_fsync_completed", "report_complete_readback_verified",
    "receipt_complete_readback_required", "receipt_complete_readback_verified",
    "approved_fresh_path_count", "fresh_paths_checked_before_candidate",
    "actual_candidate_comparison_count", "actual_clock_samples",
    "timing_trials_run", "benchmark_files_read", "hidden_cases_read",
    "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
}


def _positive_integer(value: Any, label: str) -> int:
    require(type(value) is int and value > 0,
            "an actual positive public provenance value is required: " + label)
    return value


def validate_bundle(
    report: Mapping[str, Any],
    receipt: Mapping[str, Any],
    report_raw: bytes,
    receipt_raw: bytes,
    matrix: list[dict[str, Any]],
    pins: EvidencePins,
) -> dict[str, Any]:
    require(type(report) is dict and set(report) == REPORT_FIELDS,
            "a complete untimed 864-case public report was altered")
    require(type(receipt) is dict and set(receipt) == RECEIPT_FIELDS,
            "a complete separately durable public receipt was altered")
    require(type(matrix) is list and len(matrix) == PUBLIC_CASE_COUNT
            and digest(matrix) == pins.matrix,
            "all frozen, source-ordered public practice cases are mandatory")
    require(type(report_raw) is bytes and canonical(report) == report_raw
            and hashlib.sha256(report_raw).hexdigest() == pins.report,
            "the complete actual public report bytes or fingerprint changed")
    require(type(receipt_raw) is bytes and canonical(receipt) == receipt_raw
            and hashlib.sha256(receipt_raw).hexdigest() == pins.receipt,
            "the complete actual durable receipt bytes or fingerprint changed")

    expected_report = {
        "schema": "rebar-rust-fresh-public-practice-v1-actual-untimed-correctness",
        "label": PRACTICE_LABEL, "python": "3.14.6",
        "published_seed": PUBLISHED_SEED, "matrix_sha256": pins.matrix,
        "case_denominator": PUBLIC_CASE_COUNT,
        "actual_baseline_cases": PUBLIC_CASE_COUNT,
        "actual_rust_cases": PUBLIC_CASE_COUNT,
        "baseline_records_sha256": pins.baseline,
        "rust_records_sha256": pins.rust,
        "actual_candidate_workers": 1,
        "timing_trials_run": 0, "clock_samples": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "files_written": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for key, expected in expected_report.items():
        require(report.get(key) == expected,
                "a genuine untimed public report field changed: " + key)
    baseline_pid = _positive_integer(report.get("baseline_pid"), "baseline PID")
    rust_pid = _positive_integer(report.get("rust_pid"), "Rust PID")
    require(baseline_pid != rust_pid,
            "the original and Rust observations are not independent processes")

    case_positions: dict[str, int] = {}
    for index, case in enumerate(matrix):
        require(type(case) is dict and type(case.get("case")) is str
                and case["case"] not in case_positions
                and case.get("operation") in OPERATIONS,
                "a frozen original public case was duplicated or replaced")
        case_positions[case["case"]] = index
    require(len(case_positions) == PUBLIC_CASE_COUNT,
            "one or more original public cases were omitted")

    mismatches = report.get("all_mismatches")
    require(type(mismatches) is list
            and type(report.get("mismatch_count")) is int
            and 0 <= report["mismatch_count"] <= PUBLIC_CASE_COUNT
            and report["mismatch_count"] == len(mismatches)
            and report.get("first_mismatch") == (mismatches[0] if mismatches else None)
            and report.get("status") == ("FAIL" if mismatches else "PASS"),
            "a real public mismatch, original denominator, or failure was hidden")
    previous = -1
    failures_by_operation = {operation: 0 for operation in OPERATIONS}
    failures_by_domain: dict[str, int] = {"text": 0, "bytes": 0}
    for mismatch in mismatches:
        require(type(mismatch) is dict and set(mismatch) == MISMATCH_FIELDS,
                "a complete genuine public mismatch field was hidden")
        case_id = mismatch.get("case")
        require(type(case_id) is str and case_id in case_positions,
                "an unmatched public case identity was invented")
        position = case_positions[case_id]
        require(position > previous,
                "real public mismatches must preserve strict original case order")
        original = matrix[position]
        for key in (
            "case", "dataset", "domain", "operation", "lifecycle", "flags",
            "pattern", "subject", "replacement", "limit",
        ):
            require(mismatch.get(key) == original.get(key),
                    "a genuine original mismatch input changed: " + key)
        baseline = mismatch.get("baseline_outcome")
        rust = mismatch.get("rust_outcome")
        require(type(baseline) is dict and type(rust) is dict and baseline != rust
                and baseline.get("status") in ("return", "raise")
                and rust.get("status") in ("return", "raise")
                and type(baseline.get("callbacks")) is list
                and type(rust.get("callbacks")) is list
                and type(baseline.get("warnings")) is list
                and type(rust.get("warnings")) is list,
                "an actual result, callback, warning, or mismatch was concealed")
        require(mismatch["domain"] in failures_by_domain,
                "an unfrozen public mismatch domain was introduced")
        failures_by_operation[mismatch["operation"]] += 1
        failures_by_domain[mismatch["domain"]] += 1
        previous = position

    expected_receipt = {
        "schema": (
            "rebar-frozen-rust-public-correctness-recorder-v1"
            "-durable-publication-receipt"
        ),
        "status": "PASS", "label": pins.label,
        "practice_label": PRACTICE_LABEL, "python": "3.14.6",
        "checker_source_relative": CHECKER_RELATIVE,
        "checker_source_sha256": pins.checker,
        "candidate_source_relative": CANDIDATE_SOURCE_RELATIVE,
        "candidate_source_sha256": pins.candidate,
        "native_engine_relative": NATIVE_ENGINE_RELATIVE,
        "native_engine_sha256": pins.native_engine,
        "native_bridge_module": NATIVE_BRIDGE_MODULE,
        "native_bridge_relative": NATIVE_BRIDGE_RELATIVE,
        "native_bridge_sha256": pins.native_bridge,
        "public_matrix_sha256": pins.matrix,
        "case_denominator": PUBLIC_CASE_COUNT,
        "baseline_records_sha256": pins.baseline,
        "rust_records_sha256": pins.rust,
        "baseline_pid": baseline_pid, "rust_pid": rust_pid,
        "correctness_status": report["status"],
        "mismatch_count": len(mismatches),
        "all_mismatches_preserved": True,
        "report_relative": pins.report_relative,
        "report_sha256": pins.report,
        "report_bytes": len(report_raw),
        "report_actual_write_calls": 1,
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_complete_readback_verified": True,
        "receipt_complete_readback_required": True,
        "receipt_complete_readback_verified": True,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
        "actual_candidate_comparison_count": 1,
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for key, expected in expected_receipt.items():
        require(receipt.get(key) == expected,
                "a genuine full-readback public receipt field changed: " + key)
    for prefix in ("candidate_source", "native_engine", "native_bridge"):
        for suffix in ("bytes", "device", "inode"):
            _positive_integer(receipt.get(prefix + "_" + suffix),
                              prefix + " " + suffix)

    totals = {operation: 0 for operation in OPERATIONS}
    domains = {"text": 0, "bytes": 0}
    for case in matrix:
        totals[case["operation"]] += 1
        require(case.get("domain") in domains,
                "a public case domain was removed or invented")
        domains[case["domain"]] += 1
    require(all(count == 24 for count in totals.values())
            and domains == {"text": PUBLIC_CASE_COUNT // 2,
                            "bytes": PUBLIC_CASE_COUNT // 2},
            "the 36 equally weighted original public APIs or domains changed")
    breakdown = [
        {
            "operation": operation,
            "total": totals[operation],
            "passed": totals[operation] - failures_by_operation[operation],
            "failed": failures_by_operation[operation],
        }
        for operation in OPERATIONS
    ]
    require(sum(row["total"] for row in breakdown) == PUBLIC_CASE_COUNT
            and sum(row["failed"] for row in breakdown) == len(mismatches),
            "a chart operation or failed-case denominator was changed")
    scanner = [row for row in breakdown if row["operation"] in SCANNER_OPERATIONS]
    return {
        "case_denominator": PUBLIC_CASE_COUNT,
        "baseline_passed": PUBLIC_CASE_COUNT,
        "rust_passed": PUBLIC_CASE_COUNT - len(mismatches),
        "rust_failed": len(mismatches),
        "status": report["status"],
        "operation_breakdown": breakdown,
        "scanner_breakdown": scanner,
        "domain_breakdown": [
            {
                "domain": domain, "total": domains[domain],
                "passed": domains[domain] - failures_by_domain[domain],
                "failed": failures_by_domain[domain],
            }
            for domain in ("text", "bytes")
        ],
        "all_case_ids": [case["case"] for case in matrix],
        "all_mismatches": copy.deepcopy(mismatches),
    }


def _xml(value: Any) -> str:
    return (
        str(value).replace("&", "&amp;")
        .replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;").replace("'", "&apos;")
    )


def _percent(part: int, total: int) -> str:
    require(type(part) is int and type(total) is int and 0 <= part <= total
            and total > 0, "a chart percentage has an invalid honest denominator")
    hundredths = (part * 10_000 + total // 2) // total
    return str(hundredths // 100) + "." + format(hundredths % 100, "02d") + "%"


def _bar(
    *, x: int, y: int, width: int, height: int,
    passed: int, total: int,
) -> list[str]:
    require(0 <= passed <= total and total > 0,
            "a chart cannot hide or fabricate passed and failed cases")
    green = width * passed // total
    red = width - green
    fragments = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        'rx="8" fill="#e2e8f0"/>',
    ]
    if green:
        fragments.append(
            f'<rect x="{x}" y="{y}" width="{green}" height="{height}" '
            'rx="8" fill="#047857"/>',
        )
    if red:
        fragments.append(
            f'<rect x="{x + green}" y="{y}" width="{red}" height="{height}" '
            'fill="#be123c"/>',
        )
    return fragments


def render_svg(summary: Mapping[str, Any]) -> bytes:
    total = summary["case_denominator"]
    passed = summary["rust_passed"]
    failed = summary["rust_failed"]
    scanner = summary["scanner_breakdown"]
    operations = summary["operation_breakdown"]
    require(total == PUBLIC_CASE_COUNT and passed + failed == total
            and len(scanner) == len(SCANNER_OPERATIONS)
            and len(operations) == len(OPERATIONS),
            "every public case and API must appear in the honest chart")
    width = 1_040
    operation_top = 558
    operation_rows = (len(operations) + 1) // 2
    height = operation_top + operation_rows * 45 + 94
    title = "Python and Rust: complete public regular-expression correctness"
    description = (
        f"Python passes {total} of {total} independently checked public cases. "
        f"Rust passes {passed} of {total}; {failed} cases fail and are shown in red. "
        "Every frozen API and scanner failure is included. "
        "This is an untimed public development check, not a final benchmark."
    )
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="rust-public-title rust-public-description">',
        f'<title id="rust-public-title">{_xml(title)}</title>',
        f'<desc id="rust-public-description">{_xml(description)}</desc>',
        '<rect width="100%" height="100%" rx="18" fill="#f8fafc"/>',
        '<g font-family="system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">',
        '<text x="42" y="52" fill="#0f172a" font-size="26" '
        'font-weight="760">Python and Rust: public correctness</text>',
        f'<text x="42" y="80" fill="#475569" font-size="14">'
        f'{_xml(CHART_LABEL)}</text>',
        '<rect x="34" y="103" width="972" height="174" rx="14" fill="#ffffff"/>',
        '<text x="54" y="137" fill="#0f172a" font-size="15" '
        'font-weight="700">Pinned Python baseline</text>',
        f'<text x="984" y="137" text-anchor="end" fill="#065f46" '
        f'font-size="15" font-weight="760">{total} / {total} passed</text>',
    ]
    lines.extend(_bar(x=54, y=151, width=930, height=25,
                      passed=total, total=total))
    lines.extend([
        '<text x="54" y="210" fill="#0f172a" font-size="15" '
        'font-weight="700">From-scratch Rust</text>',
        f'<text x="984" y="210" text-anchor="end" fill="#0f172a" '
        f'font-size="15" font-weight="760">{passed} / {total} passed · '
        f'<tspan fill="#be123c">{failed} failed</tspan></text>',
    ])
    lines.extend(_bar(x=54, y=224, width=930, height=25,
                      passed=passed, total=total))
    lines.extend([
        '<circle cx="54" cy="298" r="6" fill="#047857"/>',
        '<text x="67" y="303" fill="#334155" font-size="13">'
        'Matches Python</text>',
        '<circle cx="204" cy="298" r="6" fill="#be123c"/>',
        '<text x="217" y="303" fill="#334155" font-size="13">'
        'Genuine mismatch; included in the total</text>',
        f'<text x="984" y="303" text-anchor="end" fill="#475569" '
        f'font-size="13">Rust: {_percent(passed, total)} correct</text>',
        '<rect x="34" y="322" width="972" height="190" rx="14" fill="#ffffff"/>',
        '<text x="54" y="354" fill="#0f172a" font-size="17" '
        'font-weight="740">Scanner and scanner-callback details</text>',
    ])
    for index, row in enumerate(scanner):
        y = 374 + index * 24
        lines.append(
            f'<text x="54" y="{y + 12}" fill="#334155" font-size="12">'
            f'{_xml(row["operation"])}</text>',
        )
        lines.extend(_bar(x=300, y=y, width=520, height=13,
                          passed=row["passed"], total=row["total"]))
        failed_color = "#be123c" if row["failed"] else "#065f46"
        lines.append(
            f'<text x="984" y="{y + 12}" text-anchor="end" '
            f'fill="{failed_color}" font-size="12" font-weight="660">'
            f'{row["passed"]}/{row["total"]} · '
            f'{row["failed"]} failed</text>',
        )
    lines.append(
        '<text x="42" y="544" fill="#0f172a" font-size="17" '
        'font-weight="740">All 36 frozen public operations · '
        '24 original cases each</text>',
    )
    for index, row in enumerate(operations):
        column = index // operation_rows
        position = index % operation_rows
        x = 42 + column * 510
        y = operation_top + position * 45
        lines.append(
            f'<text x="{x}" y="{y + 13}" fill="#334155" font-size="11">'
            f'{_xml(row["operation"])}</text>',
        )
        lines.extend(_bar(x=x, y=y + 19, width=348, height=12,
                          passed=row["passed"], total=row["total"]))
        color = "#be123c" if row["failed"] else "#065f46"
        lines.append(
            f'<text x="{x + 467}" y="{y + 30}" text-anchor="end" '
            f'fill="{color}" font-size="11" font-weight="650">'
            f'{row["passed"]}/{row["total"]} · {row["failed"]} fail</text>',
        )
    footer_y = operation_top + operation_rows * 45 + 28
    lines.extend([
        f'<line x1="42" x2="998" y1="{footer_y - 15}" '
        f'y2="{footer_y - 15}" stroke="#cbd5e1"/>',
        f'<text x="42" y="{footer_y + 7}" fill="#475569" font-size="12">'
        'Pinned CPython 3.14.6 · every case counted · performance and memory '
        'NOT MEASURED · no hidden or final benchmark</text>',
        '</g>',
        '</svg>',
    ])
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_manifest(
    summary: Mapping[str, Any], report: Mapping[str, Any],
    receipt: Mapping[str, Any], svg: bytes, pins: EvidencePins,
) -> dict[str, Any]:
    require(type(svg) is bytes and svg.startswith(b"<svg "),
            "a complete deterministic accessible SVG is mandatory")
    return {
        "schema": SCHEMA + "-manifest",
        "status": "PASS",
        "chart_label": CHART_LABEL,
        "practice_label": PRACTICE_LABEL,
        "python": "3.14.6",
        "checker_source_relative": CHECKER_RELATIVE,
        "checker_source_sha256": pins.checker,
        "recorder_source_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": pins.recorder,
        "source_report_relative": pins.report_relative,
        "source_report_sha256": pins.report,
        "source_report_bytes": len(canonical(report)),
        "source_receipt_relative": pins.receipt_relative,
        "source_receipt_sha256": pins.receipt,
        "source_receipt_bytes": len(canonical(receipt)),
        "public_matrix_sha256": pins.matrix,
        "baseline_records_sha256": pins.baseline,
        "rust_records_sha256": pins.rust,
        "candidate_source_relative": CANDIDATE_SOURCE_RELATIVE,
        "candidate_source_sha256": pins.candidate,
        "native_engine_relative": NATIVE_ENGINE_RELATIVE,
        "native_engine_sha256": pins.native_engine,
        "native_bridge_relative": NATIVE_BRIDGE_RELATIVE,
        "native_bridge_sha256": pins.native_bridge,
        "case_denominator": summary["case_denominator"],
        "baseline_passed": summary["baseline_passed"],
        "rust_passed": summary["rust_passed"],
        "rust_failed": summary["rust_failed"],
        "rust_correctness_status": summary["status"],
        "domain_breakdown": summary["domain_breakdown"],
        "scanner_breakdown": summary["scanner_breakdown"],
        "operation_breakdown": summary["operation_breakdown"],
        "all_case_ids": summary["all_case_ids"],
        "all_mismatches": summary["all_mismatches"],
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "svg_bytes": len(svg),
        "timing_trials_run": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def render_actual(pins: EvidencePins) -> tuple[bytes, bytes, dict[str, Any]]:
    checker, recorder, matrix = authenticate_frozen_modules(pins)
    report_raw = read_owned_regular(pins.report_relative, pins.report,
                                    MAX_EVIDENCE_BYTES)
    receipt_raw = read_owned_regular(pins.receipt_relative, pins.receipt,
                                     MAX_EVIDENCE_BYTES)
    report = decode_canonical(report_raw, "genuine full public Rust report")
    receipt = decode_canonical(receipt_raw, "genuine separate durable receipt")
    actual_rust = validate_digest(
        report.get("rust_records_sha256"), "actual complete Rust case vector",
    )
    require(receipt.get("rust_records_sha256") == actual_rust,
            "the genuine full Rust vector is unbound from its durable receipt")
    require(not pins.rust or pins.rust == actual_rust,
            "an externally pinned Rust public case vector was substituted")
    pins = replace(pins, rust=actual_rust)
    require(recorder.validate_complete_report(checker, report) == report,
            "the original recorder rejects the complete actual case vector")
    summary = validate_bundle(report, receipt, report_raw, receipt_raw,
                              matrix, pins)
    svg = render_svg(summary)
    manifest = build_manifest(summary, report, receipt, svg, pins)
    verify_runtime()
    return svg, canonical(manifest), manifest


def write_atomic(relative: str, payload: bytes) -> dict[str, Any]:
    require(relative in AUTHORIZED_OUTPUTS and type(payload) is bytes
            and 0 < len(payload) <= MAX_EVIDENCE_BYTES,
            "only one exact bounded public chart or manifest can be written")
    with owned_parent(relative, output=True) as (directory, basename):
        try:
            previous = os.stat(basename, dir_fd=directory,
                               follow_symlinks=False)
        except FileNotFoundError:
            previous = None
        if previous is not None:
            require(stat.S_ISREG(previous.st_mode),
                    "refusing to follow or replace a symlinked chart destination")
        temporary = "." + basename + ".rust-public-v1-" + str(os.getpid())
        flags = (
            os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        descriptor: int | None = None
        original_info: os.stat_result | None = None
        published = False
        try:
            descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
            original_info = os.fstat(descriptor)
            require(stat.S_ISREG(original_info.st_mode),
                    "the exclusively created chart temporary is not regular")
            actual = os.write(descriptor, payload)
            require(type(actual) is int and actual == len(payload),
                    "the single deterministic chart write was incomplete")
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = None
            os.replace(temporary, basename,
                       src_dir_fd=directory, dst_dir_fd=directory)
            published = True
            os.fsync(directory)
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if not published and original_info is not None:
                try:
                    current = os.stat(temporary, dir_fd=directory,
                                      follow_symlinks=False)
                except FileNotFoundError:
                    current = None
                if current is not None:
                    require(
                        stat.S_ISREG(current.st_mode)
                        and (current.st_dev, current.st_ino)
                        == (original_info.st_dev, original_info.st_ino),
                        "refusing to delete a foreign chart temporary inode",
                    )
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
    return {
        "path": relative,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "actual_write_calls": 1,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
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

    def deny(counter: str, reason: str) -> Callable[..., Any]:
        def blocked(*args: Any, **keywords: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyError(reason)
        return blocked

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"), (Path, "read_bytes"),
            (Path, "read_text"),
        ):
            install(owner, name, deny("blocked_reads",
                                      "synthetic chart controls cannot read a file"))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "rename"), (os, "replace"), (os, "mkdir"),
            (os, "rmdir"), (os, "fsync"), (Path, "write_bytes"),
            (Path, "write_text"), (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, deny("blocked_writes",
                                      "synthetic chart controls cannot alter a file"))
        install(importlib, "import_module", deny(
            "blocked_imports", "synthetic chart controls cannot import an engine",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "synthetic chart controls cannot import a module",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny(
                "blocked_workers", "synthetic chart controls cannot start a process",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "synthetic chart controls cannot start a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "process_time_ns",
        ):
            install(time, name, deny(
                "blocked_clocks", "synthetic chart controls cannot measure time",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections", "synthetic chart controls cannot collect garbage",
        ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def _synthetic_bundle() -> tuple[
    dict[str, Any], dict[str, Any], bytes, bytes,
    list[dict[str, Any]], EvidencePins,
]:
    synthetic_label = "synthetic-public-render-controls-v1"
    synthetic_report_relative, synthetic_receipt_relative = approved_relative_paths(
        synthetic_label,
    )
    matrix: list[dict[str, Any]] = []
    for dataset in range(24):
        domain = "text" if dataset < 12 else "bytes"
        pattern = (
            {"type": "str", "value": "synthetic"}
            if domain == "text" else {"type": "bytes", "hex": "73796e"}
        )
        for operation in OPERATIONS:
            matrix.append({
                "case": "rust-public-practice.v1." + format(len(matrix), "04d"),
                "dataset": "synthetic." + domain + "." + format(dataset, "02d"),
                "domain": domain,
                "operation": operation,
                "lifecycle": "synthetic-only",
                "flags": 0,
                "pattern": pattern,
                "subject": pattern,
                "replacement": pattern,
                "limit": 1,
                "weight_numerator": 1,
            })
    mismatches: list[dict[str, Any]] = []
    for index, case in enumerate(matrix):
        if case["operation"].startswith("scanner.scan") and index % 5 == 1:
            baseline = {
                "status": "return", "value": {"type": "synthetic-baseline"},
                "callbacks": [], "warnings": [],
            }
            rust = {
                "status": "return", "value": {"type": "synthetic-rust"},
                "callbacks": [], "warnings": [],
            }
            mismatches.append({
                key: copy.deepcopy(case[key])
                for key in (
                    "case", "dataset", "domain", "operation", "lifecycle",
                    "flags", "pattern", "subject", "replacement", "limit",
                )
            } | {"baseline_outcome": baseline, "rust_outcome": rust})
    require(bool(mismatches), "real synthetic mismatch poison controls are required")
    matrix_hash = digest(matrix)
    report = {
        "schema": "rebar-rust-fresh-public-practice-v1-actual-untimed-correctness",
        "status": "FAIL",
        "label": PRACTICE_LABEL,
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": matrix_hash,
        "case_denominator": PUBLIC_CASE_COUNT,
        "actual_baseline_cases": PUBLIC_CASE_COUNT,
        "actual_rust_cases": PUBLIC_CASE_COUNT,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "rust_records_sha256": "78" * 32,
        "baseline_pid": 101,
        "rust_pid": 102,
        "mismatch_count": len(mismatches),
        "first_mismatch": copy.deepcopy(mismatches[0]),
        "all_mismatches": mismatches,
        "actual_candidate_workers": 1,
        "timing_trials_run": 0,
        "clock_samples": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    report_raw = canonical(report)
    receipt = {
        "schema": (
            "rebar-frozen-rust-public-correctness-recorder-v1"
            "-durable-publication-receipt"
        ),
        "status": "PASS", "label": synthetic_label,
        "practice_label": PRACTICE_LABEL, "python": "3.14.6",
        "checker_source_relative": CHECKER_RELATIVE,
        "checker_source_sha256": CHECKER_SHA256,
        "candidate_source_relative": CANDIDATE_SOURCE_RELATIVE,
        "candidate_source_sha256": CANDIDATE_SOURCE_SHA256,
        "candidate_source_bytes": 1,
        "candidate_source_device": 2,
        "candidate_source_inode": 3,
        "native_engine_relative": NATIVE_ENGINE_RELATIVE,
        "native_engine_sha256": NATIVE_ENGINE_SHA256,
        "native_engine_bytes": 4,
        "native_engine_device": 5,
        "native_engine_inode": 6,
        "native_bridge_module": NATIVE_BRIDGE_MODULE,
        "native_bridge_relative": NATIVE_BRIDGE_RELATIVE,
        "native_bridge_sha256": NATIVE_BRIDGE_SHA256,
        "native_bridge_bytes": 7,
        "native_bridge_device": 8,
        "native_bridge_inode": 9,
        "public_matrix_sha256": matrix_hash,
        "case_denominator": PUBLIC_CASE_COUNT,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "rust_records_sha256": report["rust_records_sha256"],
        "baseline_pid": report["baseline_pid"],
        "rust_pid": report["rust_pid"],
        "correctness_status": report["status"],
        "mismatch_count": len(mismatches),
        "all_mismatches_preserved": True,
        "report_relative": synthetic_report_relative,
        "report_sha256": hashlib.sha256(report_raw).hexdigest(),
        "report_bytes": len(report_raw),
        "report_actual_write_calls": 1,
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_complete_readback_verified": True,
        "receipt_complete_readback_required": True,
        "receipt_complete_readback_verified": True,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
        "actual_candidate_comparison_count": 1,
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    receipt_raw = canonical(receipt)
    pins = EvidencePins(
        checker=CHECKER_SHA256,
        recorder=RECORDER_SHA256,
        matrix=matrix_hash,
        baseline=BASELINE_RECORDS_SHA256,
        rust=report["rust_records_sha256"],
        candidate=CANDIDATE_SOURCE_SHA256,
        native_engine=NATIVE_ENGINE_SHA256,
        native_bridge=NATIVE_BRIDGE_SHA256,
        report=hashlib.sha256(report_raw).hexdigest(),
        receipt=hashlib.sha256(receipt_raw).hexdigest(),
        label=synthetic_label,
        report_relative=synthetic_report_relative,
        receipt_relative=synthetic_receipt_relative,
    )
    return report, receipt, report_raw, receipt_raw, matrix, pins


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a genuine synthetic chart control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "an in-memory chart poison was duplicated")
        try:
            action()
        except (RenderError, ValueError, TypeError, KeyError, OSError):
            rejected.append(name)
            return
        raise RenderError("a forged chart or source effect was accepted: " + name)

    with source_only_boundary() as effects:
        report, receipt, raw, receipt_raw, matrix, pins = _synthetic_bundle()
        result = validate_bundle(report, receipt, raw, receipt_raw, matrix, pins)
        svg = render_svg(result)
        manifest = build_manifest(result, report, receipt, svg, pins)
        accept("accept-only-864-complete-synthetic-public-cases",
               result["case_denominator"] == PUBLIC_CASE_COUNT
               and len(result["all_case_ids"]) == PUBLIC_CASE_COUNT)
        accept("derive-rust-failures-only-from-complete-synthetic-vector",
               result["rust_failed"] == len(report["all_mismatches"])
               and result["rust_passed"] + result["rust_failed"]
               == PUBLIC_CASE_COUNT)
        accept("show-every-one-of-36-original-public-operations",
               len(result["operation_breakdown"]) == len(OPERATIONS)
               and all(row["total"] == 24
                       for row in result["operation_breakdown"]))
        accept("show-every-frozen-scanner-operation-and-failure",
               len(result["scanner_breakdown"]) == len(SCANNER_OPERATIONS)
               and sum(row["failed"] for row in result["scanner_breakdown"])
               == result["rust_failed"])
        accept("create-deterministic-accessible-in-memory-svg",
               svg == render_svg(result)
               and b'role="img"' in svg
               and b'aria-labelledby="rust-public-title rust-public-description"'
               in svg and b"#047857" in svg and b"#be123c" in svg)
        accept("label-public-development-and-no-final-benchmark",
               CHART_LABEL.encode("utf-8") in svg
               and b"NOT MEASURED" in svg
               and manifest["chart_label"] == CHART_LABEL)
        accept("preserve-every-real-mismatch-in-canonical-manifest",
               manifest["all_mismatches"] == report["all_mismatches"]
               and manifest["rust_failed"] == len(report["all_mismatches"])
               and manifest["svg_sha256"] == hashlib.sha256(svg).hexdigest()
               and decode_canonical(canonical(manifest), "synthetic manifest")
               == manifest)
        accept("preserve-all-three-independent-rust-component-pins",
               manifest["candidate_source_sha256"] == CANDIDATE_SOURCE_SHA256
               and manifest["native_engine_sha256"] == NATIVE_ENGINE_SHA256
               and manifest["native_bridge_sha256"] == NATIVE_BRIDGE_SHA256)

        for index, key in enumerate(sorted(REPORT_FIELDS)):
            poisoned = copy.deepcopy(report)
            poisoned.pop(key)
            reject(
                "reject-missing-complete-public-report-field-" + format(index, "02d"),
                lambda poisoned=poisoned: validate_bundle(
                    poisoned, receipt, canonical(poisoned), receipt_raw,
                    matrix, replace(pins, report=digest(poisoned)),
                ),
            )
        for index, key in enumerate(sorted(RECEIPT_FIELDS)):
            poisoned = copy.deepcopy(receipt)
            poisoned.pop(key)
            reject(
                "reject-missing-durable-receipt-field-" + format(index, "02d"),
                lambda poisoned=poisoned: validate_bundle(
                    report, poisoned, raw, canonical(poisoned), matrix,
                    replace(pins, receipt=digest(poisoned)),
                ),
            )
        for index in range(min(48, len(matrix))):
            omitted = list(matrix)
            omitted.pop(index)
            reject(
                "reject-omitted-original-public-case-" + format(index, "03d"),
                lambda omitted=omitted: validate_bundle(
                    report, receipt, raw, receipt_raw, omitted, pins,
                ),
            )
        reordered = copy.deepcopy(matrix)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        reject("reject-reordered-frozen-original-case-vector",
               lambda: validate_bundle(report, receipt, raw, receipt_raw,
                                       reordered, pins))
        duplicated = copy.deepcopy(matrix)
        duplicated[-1] = copy.deepcopy(duplicated[0])
        reject("reject-duplicated-frozen-original-case-identity",
               lambda: validate_bundle(report, receipt, raw, receipt_raw,
                                       duplicated, pins))

        for index, key in enumerate(sorted(MISMATCH_FIELDS)):
            poisoned = copy.deepcopy(report)
            poisoned["all_mismatches"][0].pop(key)
            poisoned["first_mismatch"] = copy.deepcopy(
                poisoned["all_mismatches"][0],
            )
            mutated_raw = canonical(poisoned)
            mutated_receipt = copy.deepcopy(receipt)
            mutated_receipt["report_sha256"] = hashlib.sha256(mutated_raw).hexdigest()
            mutated_receipt["report_bytes"] = len(mutated_raw)
            mutated_receipt_raw = canonical(mutated_receipt)
            mutated_pins = replace(
                pins, report=hashlib.sha256(mutated_raw).hexdigest(),
                receipt=hashlib.sha256(mutated_receipt_raw).hexdigest(),
            )
            reject(
                "reject-concealed-genuine-mismatch-field-" + format(index, "02d"),
                lambda poisoned=poisoned, mutated_receipt=mutated_receipt,
                mutated_raw=mutated_raw, mutated_receipt_raw=mutated_receipt_raw,
                mutated_pins=mutated_pins: validate_bundle(
                    poisoned, mutated_receipt, mutated_raw, mutated_receipt_raw,
                    matrix, mutated_pins,
                ),
            )
        for name, action in (
            ("block-source-only-report-open",
             lambda: builtins.open(pins.report_relative, "rb")),
            ("block-source-only-receipt-open",
             lambda: io.open(pins.receipt_relative, "rb")),
            ("block-source-only-chart-path-read",
             lambda: (ROOT / SVG_RELATIVE).read_bytes()),
            ("block-source-only-raw-report-open",
             lambda: os.open(pins.report_relative, os.O_RDONLY)),
            ("block-source-only-raw-chart-write",
             lambda: os.write(1, b"forbidden")),
            ("block-source-only-chart-replace",
             lambda: os.replace(SVG_RELATIVE, JSON_RELATIVE)),
            ("block-source-only-chart-delete",
             lambda: os.unlink(SVG_RELATIVE)),
            ("block-source-only-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("block-source-only-frozen-checker-import",
             lambda: importlib.import_module(CHECKER_MODULE)),
            ("block-source-only-reference-worker",
             lambda: subprocess.Popen([str(PINNED_PYTHON)])),
            ("block-source-only-thread",
             lambda: threading.Thread(target=lambda: None).start()),
            ("block-source-only-performance-clock",
             lambda: time.perf_counter()),
            ("block-source-only-wall-clock", lambda: time.time()),
            ("block-source-only-garbage-collection", lambda: gc.collect()),
        ):
            reject(name, action)

        actual_zero_keys = (
            "file_reads", "file_writes", "candidate_imports",
            "reference_imports", "workers_started", "threads_started",
            "clock_samples", "gc_collections", "hidden_cases_read",
            "performance_files_read",
        )
        accept("prove-ten-actual-external-effect-counters-remain-zero",
               all(effects[key] == 0 for key in actual_zero_keys))
        accept("prove-all-seven-real-attack-categories-intercepted",
               all(effects[key] > 0 for key in (
                   "blocked_reads", "blocked_writes", "blocked_imports",
                   "blocked_workers", "blocked_threads", "blocked_clocks",
                   "blocked_gc_collections",
               )))
        accept("retain-at-least-125-distinct-genuine-rejection-controls",
               len(rejected) >= 125 and len(set(rejected)) == len(rejected))

    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "chart_label": CHART_LABEL,
        "checker_source_sha256": CHECKER_SHA256,
        "recorder_source_sha256": RECORDER_SHA256,
        "public_matrix_sha256": MATRIX_SHA256,
        "case_denominator": PUBLIC_CASE_COUNT,
        "operation_count": len(OPERATIONS),
        "scanner_operation_count": len(SCANNER_OPERATIONS),
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "effects": effects,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "performance_files_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "synthetic": True,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one complete, untimed, authenticated public Rust check",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    parser.add_argument("--report")
    parser.add_argument("--receipt")
    parser.add_argument("--report-sha256")
    parser.add_argument("--receipt-sha256")
    parser.add_argument("--checker-source-sha256")
    parser.add_argument("--recorder-source-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--rust-records-sha256")
    return parser.parse_args(arguments)


def command_pins(options: argparse.Namespace) -> EvidencePins:
    require(type(options.report) is str and type(options.receipt) is str,
            "explicit full report and separate durable receipt paths are required")
    prefix = APPROVED_EVIDENCE_DIRECTORY + "/"
    require(options.report.startswith(prefix) and options.report.endswith(".json"),
            "the selected actual report must remain in its frozen public directory")
    label = validate_label(options.report[len(prefix):-5])
    report_relative, receipt_relative = approved_relative_paths(label)
    require(options.report == report_relative
            and options.receipt == receipt_relative,
            "the selected actual report and durable receipt do not share one slug")
    supplied = {
        "report": options.report_sha256,
        "receipt": options.receipt_sha256,
        "checker": options.checker_source_sha256,
        "recorder": options.recorder_source_sha256,
        "candidate": options.candidate_source_sha256,
        "native_engine": options.native_engine_sha256,
        "native_bridge": options.native_bridge_sha256,
    }
    for key, value in supplied.items():
        validate_digest(value, key)
    require(supplied["checker"] == CHECKER_SHA256,
            "the immutable frozen public checker was substituted")
    require(supplied["recorder"] == RECORDER_SHA256,
            "the immutable frozen durable public recorder was substituted")
    rust = ""
    if options.rust_records_sha256 is not None:
        rust = validate_digest(options.rust_records_sha256,
                               "externally pinned actual Rust vector")
    return EvidencePins(
        checker=supplied["checker"], recorder=supplied["recorder"],
        matrix=MATRIX_SHA256, baseline=BASELINE_RECORDS_SHA256,
        rust=rust, candidate=supplied["candidate"],
        native_engine=supplied["native_engine"],
        native_bridge=supplied["native_bridge"],
        report=supplied["report"], receipt=supplied["receipt"],
        label=label, report_relative=report_relative,
        receipt_relative=receipt_relative,
    )


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, key) is None for key in (
            "report", "receipt", "report_sha256", "receipt_sha256",
            "checker_source_sha256", "recorder_source_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256", "rust_records_sha256",
        )), "synthetic controls may not consume actual public evidence")
        result = source_self_test()
    else:
        pins = command_pins(options)
        svg, manifest_raw, manifest = render_actual(pins)
        if options.check:
            actual_svg = read_owned_regular(
                SVG_RELATIVE, hashlib.sha256(svg).hexdigest(), MAX_EVIDENCE_BYTES,
            )
            actual_json = read_owned_regular(
                JSON_RELATIVE, hashlib.sha256(manifest_raw).hexdigest(),
                MAX_EVIDENCE_BYTES,
            )
            require(actual_svg == svg and actual_json == manifest_raw,
                    "the complete deterministic public chart or manifest changed")
            publications: list[dict[str, Any]] = []
        else:
            publications = [
                write_atomic(SVG_RELATIVE, svg),
                write_atomic(JSON_RELATIVE, manifest_raw),
            ]
        result = {
            "schema": SCHEMA + ("-checked" if options.check else "-published"),
            "status": "PASS",
            "chart_label": CHART_LABEL,
            "public_matrix_sha256": pins.matrix,
            "case_denominator": PUBLIC_CASE_COUNT,
            "baseline_passed": manifest["baseline_passed"],
            "rust_passed": manifest["rust_passed"],
            "rust_failed": manifest["rust_failed"],
            "report_sha256": pins.report,
            "receipt_sha256": pins.receipt,
            "svg_sha256": hashlib.sha256(svg).hexdigest(),
            "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "publications": publications,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
