#!/usr/bin/env python3
"""Render only a complete, authenticated, public Rust practice comparison.

No candidate, matching engine, timer, benchmark, hidden case, or subprocess is
started here.  A speed result is accepted only from an explicitly pinned,
correctness-gated report containing every one of the 864 frozen public cases
and all 12 independently paired observations.  Only ``--write`` can publish the
four exact SVG charts and their canonical JSON manifest.
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
import math
import os
from pathlib import Path
import random
import stat
import statistics
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SOURCE_RELATIVE = "tools/render_rust_public_speed_v1.py"
SCHEMA = "rebar-rust-public-practice-speed-render-v1"
PRACTICE_LABEL = "PUBLIC PRACTICE ONLY; NOT A HIDDEN OR FINAL BENCHMARK"
CHART_LABEL = "PUBLIC DEVELOPMENT · NOT FINAL · NATIVE MEMORY NOT MEASURED"
CHECKER_RELATIVE = "tools/rust_public_practice_benchmark_v1.py"
CHECKER_MODULE = "tools.rust_public_practice_benchmark_v1"
CHECKER_SHA256 = (
    "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37"
)
CORRECTNESS_RENDERER_RELATIVE = "tools/render_rust_public_correctness_v1.py"
CORRECTNESS_RENDERER_MODULE = "tools.render_rust_public_correctness_v1"
CORRECTNESS_RENDERER_SHA256 = (
    "6f7c36c29c66c6792d578eba6907bc2ebcf869888693129382adf839af1dee4e"
)
CORRECTNESS_RECORDER_SHA256 = (
    "41b749696cc498be4e2b5d63866fb103d29d54e1277dae6a5659fd63302daa49"
)
MATRIX_SHA256 = (
    "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e"
)
BASELINE_RECORDS_SHA256 = (
    "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c"
)
PUBLISHED_SEED = 0x5245_4241_525F_5031
PUBLIC_CASE_COUNT = 864
PAIRED_TRIALS = 12
BATCH_ITERATIONS = 12
WARMUP_ITERATIONS = 2
BOOTSTRAP_RESAMPLES = 1_000
APPROVED_PUBLIC_DIRECTORY = "experiments/rust_public_practice_v1"
CANDIDATE_SOURCE_RELATIVE = "candidates/rust_candidate.py"
NATIVE_ENGINE_RELATIVE = "candidates/_rust_engine.so"
NATIVE_BRIDGE_MODULE = "candidates._rust_bridge"
NATIVE_BRIDGE_RELATIVE = "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_EVIDENCE_BYTES = 32 * 1024 * 1024
OVERALL_RELATIVE = "docs/evidence/rust-public-speed-v1-overall.svg"
OUTCOMES_RELATIVE = "docs/evidence/rust-public-speed-v1-outcomes.svg"
OPERATIONS_RELATIVE = "docs/evidence/rust-public-speed-v1-operations.svg"
REGRESSIONS_RELATIVE = "docs/evidence/rust-public-speed-v1-regressions.svg"
MANIFEST_RELATIVE = "docs/evidence/rust-public-speed-v1.json"
APPROVED_OUTPUTS = (
    OVERALL_RELATIVE, OUTCOMES_RELATIVE, OPERATIONS_RELATIVE,
    REGRESSIONS_RELATIVE, MANIFEST_RELATIVE,
)
AUTHORIZED_STATIC_READS = frozenset({
    CHECKER_RELATIVE, CORRECTNESS_RENDERER_RELATIVE, *APPROVED_OUTPUTS,
})
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


class RenderError(Exception):
    """Reject an omitted observation, false speed, hidden data, or fake win."""


class SourceOnlyError(RenderError):
    """An actual external effect was intercepted in a synthetic self-test."""


@dataclass(frozen=True)
class EvidencePins:
    checker: str
    correctness_renderer: str
    correctness_recorder: str
    matrix: str
    baseline: str
    report: str
    correctness_receipt: str
    candidate: str
    native_engine: str
    native_bridge: str
    report_relative: str
    correctness_receipt_relative: str


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
    require(type(value) is str and len(value) == 64 and len(set(value)) > 1
            and all(letter in "0123456789abcdef" for letter in value),
            "an independently supplied lowercase SHA-256 is required: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "use only isolated pinned no-bytecode CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a speed renderer must never import or start a Rust candidate")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "duplicate evidence keys cannot conceal a raw observation")
        result[key] = value
    return result


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_EVIDENCE_BYTES,
            "complete bounded canonical evidence is required: " + label)
    try:
        document = json.loads(
            raw, object_pairs_hook=_unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                RenderError("nonfinite public evidence is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise RenderError("invalid complete public evidence: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "the complete canonical public evidence changed: " + label)
    return document


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for letter in value)
            and "--" not in value,
            "an exact lowercase, nonescaping public evidence slug is required")
    return value


def _relative_parts(relative: Any, *, output: bool = False) -> tuple[str, ...]:
    require(type(relative) is str, "an exact bounded relative path is required")
    if output:
        require(relative in APPROVED_OUTPUTS,
                "publish only the four speed charts and one manifest")
    elif relative not in AUTHORIZED_STATIC_READS:
        prefix = APPROVED_PUBLIC_DIRECTORY + "/"
        require(relative.startswith(prefix) and relative.endswith(".json"),
                "read only an explicitly selected public development report")
        basename = relative[len(prefix):]
        suffix = "-publication-receipt.json"
        label = basename[:-len(suffix)] if basename.endswith(suffix) else basename[:-5]
        validate_label(label)
        require(relative == prefix + label + (
            suffix if basename.endswith(suffix) else ".json"
        ), "a public development report or receipt escaped its frozen directory")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "\\" not in relative and "\x00" not in relative,
            "an approved speed-chart component is noncanonical")
    return parts


def _directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


@contextlib.contextmanager
def owned_parent(relative: str, *, output: bool = False) -> Iterator[tuple[int, str]]:
    parts = _relative_parts(relative, output=output)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), _directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the literal public repository root is not a directory")
        for component in parts[:-1]:
            following = os.open(component, _directory_flags(), dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "a public evidence component followed a symlink")
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
            raise RenderError("an owned speed-chart descriptor did not close") from errors[0]


def read_owned_regular(relative: str, expected: str, maximum: int) -> bytes:
    validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_EVIDENCE_BYTES,
            "a complete bounded no-follow public artifact is required")
    with owned_parent(relative) as (directory, basename):
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(basename, flags, dir_fd=directory)
        try:
            info = os.fstat(descriptor)
            named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
            require(stat.S_ISREG(info.st_mode) and stat.S_ISREG(named.st_mode)
                    and (info.st_dev, info.st_ino) == (named.st_dev, named.st_ino)
                    and 0 < info.st_size <= maximum,
                    "a public source, report, or chart changed its owned inode")
            remaining = info.st_size
            chunks: list[bytes] = []
            while remaining:
                part = os.read(descriptor, min(remaining, 1_048_576))
                require(type(part) is bytes and bool(part),
                        "a complete public speed artifact was truncated")
                chunks.append(part)
                remaining -= len(part)
            require(os.read(descriptor, 1) == b"",
                    "a public speed artifact contains an unreported suffix")
            final = os.fstat(descriptor)
            require((final.st_dev, final.st_ino, final.st_size)
                    == (info.st_dev, info.st_ino, info.st_size),
                    "a public artifact changed while being authenticated")
        finally:
            os.close(descriptor)
    raw = b"".join(chunks)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "an externally pinned public artifact changed: " + relative)
    return raw


REPORT_FIELDS = {
    "schema", "status", "label", "python", "published_seed", "matrix_sha256",
    "case_count", "matrix", "correctness_reference_records_sha256",
    "correctness_reference_records", "baseline_correctness_pid",
    "rust_correctness_pid", "paired_trials", "batch_iterations",
    "warmup_iterations", "trial_process_provenance", "raw_paired_rows_sha256",
    "raw_paired_rows", "results", "benchmark_files_read", "hidden_cases_read",
    "candidate_production_reference_delegation", "final_winner_selected",
}
ROW_FIELDS = {
    "case", "trial", "case_order_position", "pair_order", "baseline_pid",
    "rust_pid", "batch_iterations", "correctness_checks_per_engine",
    "expected_outcome_sha256", "baseline_elapsed_ns", "rust_elapsed_ns",
}
PROVENANCE_FIELDS = {
    "trial", "engine", "pair_execution_position", "pid", "rows_sha256",
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


def geometric_mean(values: list[float]) -> float:
    require(type(values) is list and bool(values)
            and all(type(value) in (int, float)
                    and math.isfinite(value) and value > 0 for value in values),
            "a geometric mean requires all finite positive paired observations")
    return math.exp(math.fsum(math.log(value) for value in values) / len(values))


def bootstrap_case_interval(pairs: list[tuple[int, int]], seed: int) -> dict[str, Any]:
    require(type(pairs) is list and bool(pairs)
            and all(type(pair) is tuple and len(pair) == 2
                    and all(type(value) is int and value > 0 for value in pair)
                    for pair in pairs),
            "all true original paired trials are mandatory for a case interval")
    generator = random.Random(seed)
    estimates: list[float] = []
    count = len(pairs)
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [pairs[generator.randrange(count)] for _ in range(count)]
        estimates.append(geometric_mean([
            baseline / candidate for baseline, candidate in sample
        ]))
    estimates.sort()
    return {
        "method": "published-seed paired percentile bootstrap",
        "confidence_level": 0.95,
        "resamples": BOOTSTRAP_RESAMPLES,
        "lower": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.025)],
        "upper": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.975)],
    }


def bootstrap_overall_interval(
    cases: list[list[tuple[int, int]]], seed: int,
) -> dict[str, Any]:
    require(type(cases) is list and bool(cases)
            and all(type(pairs) is list and bool(pairs) for pairs in cases),
            "every equally weighted case is required for a 95% interval")
    generator = random.Random(seed)
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        case_estimates: list[float] = []
        for _ in range(len(cases)):
            pairs = cases[generator.randrange(len(cases))]
            ratios: list[float] = []
            for _ in range(len(pairs)):
                baseline, candidate = pairs[generator.randrange(len(pairs))]
                require(type(baseline) is int and baseline > 0
                        and type(candidate) is int and candidate > 0,
                        "an actual bootstrap paired observation was forged")
                ratios.append(baseline / candidate)
            case_estimates.append(geometric_mean(ratios))
        estimates.append(geometric_mean(case_estimates))
    estimates.sort()
    return {
        "method": (
            "published-seed equally weighted case-and-paired-trial "
            "geometric-mean bootstrap"
        ),
        "confidence_level": 0.95,
        "resamples": BOOTSTRAP_RESAMPLES,
        "lower": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.025)],
        "upper": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.975)],
    }


def _positive_int(value: Any, label: str) -> int:
    require(type(value) is int and value > 0,
            "an exact positive actual public observation is required: " + label)
    return value


def authenticate_frozen_sources(pins: EvidencePins) -> tuple[Any, Any, list[dict[str, Any]]]:
    verify_runtime()
    read_owned_regular(CHECKER_RELATIVE, pins.checker, MAX_SOURCE_BYTES)
    read_owned_regular(CORRECTNESS_RENDERER_RELATIVE,
                       pins.correctness_renderer, MAX_SOURCE_BYTES)
    checker = importlib.import_module(CHECKER_MODULE)
    correctness = importlib.import_module(CORRECTNESS_RENDERER_MODULE)
    require(checker.__name__ == CHECKER_MODULE
            and os.path.abspath(checker.__file__) == str(ROOT / CHECKER_RELATIVE)
            and correctness.__name__ == CORRECTNESS_RENDERER_MODULE
            and os.path.abspath(correctness.__file__)
            == str(ROOT / CORRECTNESS_RENDERER_RELATIVE)
            and checker.MATRIX_SHA256 == pins.matrix
            and checker.PUBLISHED_SEED == PUBLISHED_SEED
            and checker.DEFAULT_PAIRED_TRIALS == PAIRED_TRIALS
            and checker.DEFAULT_BATCH_ITERATIONS == BATCH_ITERATIONS
            and checker.DEFAULT_WARMUP_ITERATIONS == WARMUP_ITERATIONS
            and checker.BOOTSTRAP_RESAMPLES == BOOTSTRAP_RESAMPLES
            and checker.PRACTICE_LABEL == PRACTICE_LABEL
            and tuple(checker.OPERATIONS) == OPERATIONS
            and correctness.CHECKER_SHA256 == pins.checker
            and correctness.RECORDER_SHA256 == pins.correctness_recorder
            and correctness.MATRIX_SHA256 == pins.matrix
            and correctness.BASELINE_RECORDS_SHA256 == pins.baseline
            and correctness.PRACTICE_LABEL == PRACTICE_LABEL,
            "a frozen public checker, genuine correctness gate, or statistic changed")
    matrix = checker.build_public_matrix()
    require(checker.validate_public_matrix(matrix) == pins.matrix
            and checker.digest(matrix) == pins.matrix
            and digest(matrix) == pins.matrix
            and len(matrix) == PUBLIC_CASE_COUNT,
            "every exact original public case and seed is mandatory")
    verify_runtime()
    return checker, correctness, matrix


def validate_correctness_receipt(
    receipt: Mapping[str, Any], raw: bytes, pins: EvidencePins,
) -> None:
    require(type(receipt) is dict and set(receipt) == RECEIPT_FIELDS,
            "a complete separately durable current correctness receipt is mandatory")
    require(canonical(receipt) == raw
            and hashlib.sha256(raw).hexdigest() == pins.correctness_receipt,
            "the complete authentic current correctness receipt bytes changed")
    prefix = APPROVED_PUBLIC_DIRECTORY + "/"
    require(pins.correctness_receipt_relative.startswith(prefix)
            and pins.correctness_receipt_relative.endswith(
                "-publication-receipt.json",
            ), "only a frozen, separately durable public receipt is approved")
    label = validate_label(
        pins.correctness_receipt_relative[len(prefix):-len(
            "-publication-receipt.json",
        )],
    )
    expected = {
        "schema": (
            "rebar-frozen-rust-public-correctness-recorder-v1"
            "-durable-publication-receipt"
        ),
        "status": "PASS", "label": label,
        "practice_label": PRACTICE_LABEL,
        "python": "3.14.6",
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
        "rust_records_sha256": pins.baseline,
        "correctness_status": "PASS",
        "mismatch_count": 0,
        "all_mismatches_preserved": True,
        "report_relative": prefix + label + ".json",
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
    for key, expected_value in expected.items():
        require(receipt.get(key) == expected_value,
                "a genuine current correctness receipt field changed: " + key)
    for prefix_key in ("candidate_source", "native_engine", "native_bridge"):
        for suffix in ("bytes", "device", "inode"):
            _positive_int(receipt.get(prefix_key + "_" + suffix),
                          prefix_key + " " + suffix)
    _positive_int(receipt.get("report_bytes"), "durable correctness report size")
    validate_digest(receipt.get("report_sha256"),
                    "actual current full correctness report")
    baseline_pid = _positive_int(receipt.get("baseline_pid"),
                                 "current baseline correctness PID")
    rust_pid = _positive_int(receipt.get("rust_pid"),
                             "current Rust correctness PID")
    require(baseline_pid != rust_pid,
            "the full original and current Rust correctness workers were reused")


def _validate_original_reference(
    records: Any, matrix: list[dict[str, Any]], expected_hash: str,
) -> dict[str, dict[str, Any]]:
    require(type(records) is list and len(records) == PUBLIC_CASE_COUNT
            and digest(records) == expected_hash,
            "the complete original 864-case correctness vector was changed")
    result: dict[str, dict[str, Any]] = {}
    for case, record in zip(matrix, records, strict=True):
        require(type(record) is dict and set(record) == {"case", "outcome"}
                and record.get("case") == case["case"]
                and type(record.get("outcome")) is dict
                and record["outcome"].get("status") in ("return", "raise")
                and type(record["outcome"].get("callbacks")) is list
                and type(record["outcome"].get("warnings")) is list,
                "a frozen original baseline case or normalized outcome was omitted")
        result[case["case"]] = record["outcome"]
    return result


def validate_raw_observations(
    report: Mapping[str, Any], matrix: list[dict[str, Any]], pins: EvidencePins,
) -> tuple[list[dict[str, Any]], list[list[tuple[int, int]]]]:
    require(type(report) is dict and set(report) == REPORT_FIELDS,
            "the complete original public timing report was altered")
    require(type(matrix) is list and len(matrix) == PUBLIC_CASE_COUNT
            and digest(matrix) == pins.matrix,
            "all 864 unchanged public timing cases are required")
    expected = {
        "schema": "rebar-rust-fresh-public-practice-v1-actual-public-practice-report",
        "status": "PASS", "label": PRACTICE_LABEL, "python": "3.14.6",
        "published_seed": PUBLISHED_SEED, "matrix_sha256": pins.matrix,
        "case_count": PUBLIC_CASE_COUNT,
        "correctness_reference_records_sha256": pins.baseline,
        "paired_trials": PAIRED_TRIALS,
        "batch_iterations": BATCH_ITERATIONS,
        "warmup_iterations": WARMUP_ITERATIONS,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "candidate_production_reference_delegation": (
            "NOT AUDITED BY PUBLIC PRACTICE"
        ),
        "final_winner_selected": False,
    }
    for key, expected_value in expected.items():
        require(report.get(key) == expected_value,
                "a frozen complete public timing field changed: " + key)
    require(report.get("matrix") == matrix,
            "the complete frozen, source-ordered timing matrix changed")
    baseline_pid = _positive_int(report.get("baseline_correctness_pid"),
                                 "timing baseline correctness PID")
    rust_pid = _positive_int(report.get("rust_correctness_pid"),
                             "timing Rust correctness PID")
    require(baseline_pid != rust_pid,
            "the correctness-gated original and Rust workers were reused")
    reference = _validate_original_reference(
        report.get("correctness_reference_records"), matrix, pins.baseline,
    )
    raw_rows = report.get("raw_paired_rows")
    require(type(raw_rows) is list
            and len(raw_rows) == PUBLIC_CASE_COUNT * PAIRED_TRIALS
            and report.get("raw_paired_rows_sha256") == digest(raw_rows),
            "all 10,368 original paired observations are mandatory")
    provenance = report.get("trial_process_provenance")
    require(type(provenance) is list and len(provenance) == 2 * PAIRED_TRIALS,
            "every one of 24 actual isolated timing workers is required")
    by_trial: dict[tuple[int, str], dict[str, Any]] = {}
    pids: set[int] = set()
    for item in provenance:
        require(type(item) is dict and set(item) == PROVENANCE_FIELDS,
                "an actual complete public timing worker was concealed")
        trial = item.get("trial")
        engine = item.get("engine")
        require(type(trial) is int and 0 <= trial < PAIRED_TRIALS
                and engine in ("stdlib", "rust")
                and (trial, engine) not in by_trial,
                "an actual paired public worker was skipped or duplicated")
        order = ("stdlib", "rust") if trial % 2 == 0 else ("rust", "stdlib")
        require(item.get("pair_execution_position") == order.index(engine),
                "the original alternating pair order was forged")
        pid = _positive_int(item.get("pid"), "actual paired timing PID")
        require(pid not in pids,
                "an independent timed public worker process was reused")
        pids.add(pid)
        validate_digest(item.get("rows_sha256"), "actual complete worker vector")
        by_trial[(trial, engine)] = item

    by_case: dict[str, list[tuple[int, int] | None]] = {
        case["case"]: [None] * PAIRED_TRIALS for case in matrix
    }
    case_ids = [case["case"] for case in matrix]
    cursor = 0
    for trial in range(PAIRED_TRIALS):
        case_order = list(case_ids)
        random.Random(PUBLISHED_SEED ^ (trial + 1)).shuffle(case_order)
        pair_order = ["stdlib", "rust"] if trial % 2 == 0 else ["rust", "stdlib"]
        reconstructed: dict[str, list[dict[str, Any]]] = {
            "stdlib": [], "rust": [],
        }
        for position, case_id in enumerate(case_order):
            row = raw_rows[cursor]
            cursor += 1
            require(type(row) is dict and set(row) == ROW_FIELDS,
                    "a complete paired public timing observation was concealed")
            require(row.get("case") == case_id
                    and row.get("trial") == trial
                    and row.get("case_order_position") == position
                    and row.get("pair_order") == pair_order
                    and row.get("baseline_pid")
                    == by_trial[(trial, "stdlib")]["pid"]
                    and row.get("rust_pid") == by_trial[(trial, "rust")]["pid"]
                    and row.get("batch_iterations") == BATCH_ITERATIONS
                    and row.get("correctness_checks_per_engine")
                    == WARMUP_ITERATIONS + BATCH_ITERATIONS + 1
                    and row.get("expected_outcome_sha256")
                    == digest(reference[case_id]),
                    "an authentic paired case, order, process, or correctness gate changed")
            baseline = _positive_int(row.get("baseline_elapsed_ns"),
                                     "real original elapsed nanoseconds")
            candidate = _positive_int(row.get("rust_elapsed_ns"),
                                      "real Rust elapsed nanoseconds")
            require(by_case[case_id][trial] is None,
                    "a frozen case's original trial was repeated")
            by_case[case_id][trial] = (baseline, candidate)
            for engine, elapsed in (("stdlib", baseline), ("rust", candidate)):
                reconstructed[engine].append({
                    "case": case_id, "trial": trial, "position": position,
                    "elapsed_ns": elapsed,
                    "batch_iterations": BATCH_ITERATIONS,
                    "correctness_checks": WARMUP_ITERATIONS + BATCH_ITERATIONS + 1,
                    "expected_outcome_sha256": digest(reference[case_id]),
                })
        for engine in ("stdlib", "rust"):
            require(digest(reconstructed[engine])
                    == by_trial[(trial, engine)]["rows_sha256"],
                    "the actual isolated worker's full raw vector was substituted")
    require(cursor == len(raw_rows),
            "an extra or omitted original public paired row was concealed")
    pairs: list[list[tuple[int, int]]] = []
    for case in matrix:
        observed = by_case[case["case"]]
        require(all(item is not None for item in observed),
                "a genuine original case is missing a paired trial")
        pairs.append([item for item in observed if item is not None])
    return raw_rows, pairs


def derive_statistics(
    matrix: list[dict[str, Any]], pairs: list[list[tuple[int, int]]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(len(matrix) == len(pairs) == PUBLIC_CASE_COUNT,
            "derive speed from all 864 original equally weighted cases")
    summaries: list[dict[str, Any]] = []
    for index, (case, observed) in enumerate(zip(matrix, pairs, strict=True)):
        require(len(observed) == PAIRED_TRIALS,
                "all 12 original paired rounds are mandatory")
        ratio = geometric_mean([baseline / rust for baseline, rust in observed])
        interval = bootstrap_case_interval(
            observed, PUBLISHED_SEED ^ ((index + 1) * 0x9E37_79B9),
        )
        baseline_median = statistics.median([pair[0] for pair in observed])
        rust_median = statistics.median([pair[1] for pair in observed])
        summaries.append({
            "case": case["case"], "dataset": case["dataset"],
            "domain": case["domain"], "operation": case["operation"],
            "lifecycle": case["lifecycle"], "flags": case["flags"],
            "weight_numerator": 1,
            "weight_denominator": PUBLIC_CASE_COUNT,
            "paired_trial_count": PAIRED_TRIALS,
            "baseline_median_batch_ns_descriptive": baseline_median,
            "rust_median_batch_ns_descriptive": rust_median,
            "median_batch_ratio_descriptive": baseline_median / rust_median,
            "point_estimator": "geometric mean of all paired trial ratios",
            "speedup_vs_baseline": ratio,
            "rust_change_percent": (1.0 / ratio - 1.0) * 100.0,
            "speedup_confidence_interval": interval,
            "statistically_faster": interval["lower"] > 1.0,
            "statistically_slower": interval["upper"] < 1.0,
            "regression_exceeds_20_percent": (1.0 / ratio) > 1.2,
        })
    speed = geometric_mean([row["speedup_vs_baseline"] for row in summaries])
    interval = bootstrap_overall_interval(pairs, PUBLISHED_SEED ^ 0xA110_CAFE)
    faster = sum(row["statistically_faster"] for row in summaries)
    slower = sum(row["statistically_slower"] for row in summaries)
    regressions = [row for row in summaries if row["regression_exceeds_20_percent"]]
    result = {
        "label": PRACTICE_LABEL,
        "weight_policy": "each of the frozen public cases has identical weight",
        "point_estimator": (
            "equally weighted geometric mean of each case's "
            "geometric mean of all original paired trial ratios"
        ),
        "timed_interval": (
            "full public regex operation, result materialization, exact "
            "observable and warning normalization, and per-call "
            "baseline-outcome correctness comparison; not native-only timing"
        ),
        "case_denominator": PUBLIC_CASE_COUNT,
        "paired_trials_per_case": PAIRED_TRIALS,
        "baseline_first_paired_rounds": (PAIRED_TRIALS + 1) // 2,
        "rust_first_paired_rounds": PAIRED_TRIALS // 2,
        "pair_order_is_exactly_balanced": True,
        "total_complete_paired_rows": PUBLIC_CASE_COUNT * PAIRED_TRIALS,
        "text_case_count": sum(case["domain"] == "text" for case in matrix),
        "bytes_case_count": sum(case["domain"] == "bytes" for case in matrix),
        "operation_count": len(OPERATIONS),
        "weighted_geomean_speedup_vs_baseline": speed,
        "overall_speedup_confidence_interval": interval,
        "statistically_faster_case_count": faster,
        "statistically_faster_fraction": faster / PUBLIC_CASE_COUNT,
        "statistically_slower_case_count": slower,
        "regression_over_20_percent_count": len(regressions),
        "all_regressions_over_20_percent": regressions,
        "all_case_results": summaries,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    operation_results: list[dict[str, Any]] = []
    for index, operation in enumerate(OPERATIONS):
        rows = [row for row in summaries if row["operation"] == operation]
        require(len(rows) == 24,
                "an entire original public operation disappeared: " + operation)
        operation_results.append({
            "operation": operation,
            "case_denominator": len(rows),
            "speedup_vs_baseline": geometric_mean([
                row["speedup_vs_baseline"] for row in rows
            ]),
            "statistically_faster_case_count": sum(
                row["statistically_faster"] for row in rows
            ),
            "statistically_slower_case_count": sum(
                row["statistically_slower"] for row in rows
            ),
            "uncertain_case_count": sum(
                not row["statistically_faster"]
                and not row["statistically_slower"] for row in rows
            ),
            "regression_over_20_percent_count": sum(
                row["regression_exceeds_20_percent"] for row in rows
            ),
            "operation_order": index,
        })
    return result, operation_results


def validate_public_report(
    report: Mapping[str, Any], report_raw: bytes,
    receipt: Mapping[str, Any], receipt_raw: bytes,
    matrix: list[dict[str, Any]], pins: EvidencePins,
    *, expected_results: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(type(report_raw) is bytes and canonical(report) == report_raw
            and hashlib.sha256(report_raw).hexdigest() == pins.report,
            "the complete genuine public paired report fingerprint changed")
    require(type(receipt_raw) is bytes and canonical(receipt) == receipt_raw
            and hashlib.sha256(receipt_raw).hexdigest() == pins.correctness_receipt,
            "the complete genuine current correctness receipt fingerprint changed")
    validate_correctness_receipt(receipt, receipt_raw, pins)
    _, pairs = validate_raw_observations(report, matrix, pins)
    if expected_results is None:
        derived, operations = derive_statistics(matrix, pairs)
    else:
        require(type(expected_results) is dict,
                "a synthetic independent summary must be a complete mapping")
        derived = dict(expected_results)
        operations = []
    require(type(report.get("results")) is dict
            and report["results"] == derived,
            "reported confidence intervals or overall speed disagree with raw data")
    if expected_results is not None:
        summaries = derived.get("all_case_results")
        require(type(summaries) is list and len(summaries) == PUBLIC_CASE_COUNT,
                "a synthetic complete per-case result was omitted")
        for index, operation in enumerate(OPERATIONS):
            rows = [row for row in summaries if row["operation"] == operation]
            require(len(rows) == 24,
                    "a synthetic frozen operation was hidden")
            operations.append({
                "operation": operation, "case_denominator": 24,
                "speedup_vs_baseline": geometric_mean([
                    row["speedup_vs_baseline"] for row in rows
                ]),
                "statistically_faster_case_count": sum(
                    row["statistically_faster"] for row in rows
                ),
                "statistically_slower_case_count": sum(
                    row["statistically_slower"] for row in rows
                ),
                "uncertain_case_count": sum(
                    not row["statistically_faster"]
                    and not row["statistically_slower"] for row in rows
                ),
                "regression_over_20_percent_count": sum(
                    row["regression_exceeds_20_percent"] for row in rows
                ),
                "operation_order": index,
            })
    return derived, operations


def _xml(value: Any) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def _number(value: float, places: int = 3) -> str:
    require(type(value) in (int, float) and math.isfinite(value),
            "a displayed public speed must be a real finite measurement")
    return format(value, "." + str(places) + "f")


def _svg_frame(title: str, description: str, height: int) -> list[str]:
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="1040" height="{height}" viewBox="0 0 1040 {height}" '
        'role="img" aria-labelledby="public-speed-title public-speed-description">',
        f'<title id="public-speed-title">{_xml(title)}</title>',
        f'<desc id="public-speed-description">{_xml(description)}</desc>',
        '<rect width="100%" height="100%" rx="18" fill="#f8fafc"/>',
        '<g font-family="system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">',
        f'<text x="42" y="49" fill="#0f172a" font-size="24" '
        f'font-weight="750">{_xml(title)}</text>',
        f'<text x="42" y="76" fill="#475569" font-size="13">'
        f'{_xml(CHART_LABEL)}</text>',
    ]


def _finish(lines: list[str], height: int) -> bytes:
    lines.extend([
        f'<line x1="42" x2="998" y1="{height - 49}" '
        f'y2="{height - 49}" stroke="#cbd5e1"/>',
        f'<text x="42" y="{height - 25}" fill="#475569" font-size="12">'
        'Pinned CPython 3.14.6 · all 864 public cases · 12 paired rounds · '
        'native memory not measured · no hidden benchmark or winner</text>',
        '</g>', '</svg>',
    ])
    return ("\n".join(lines) + "\n").encode("utf-8")


def render_overall(results: Mapping[str, Any]) -> bytes:
    speed = results["weighted_geomean_speedup_vs_baseline"]
    interval = results["overall_speedup_confidence_interval"]
    scale = max(1.0, speed, interval["upper"])
    require(math.isfinite(scale) and scale > 0,
            "the honest public speed and uncertainty must be finite")
    width = 738
    lines = _svg_frame(
        "Current Rust compared with Python",
        "An equally weighted geometric speed comparison over every public "
        "case, including a seeded 95 percent paired confidence interval; "
        "not a final benchmark.",
        334,
    )
    lines.extend([
        '<rect x="34" y="99" width="972" height="168" rx="14" fill="#ffffff"/>',
        '<text x="54" y="132" fill="#0f172a" font-size="15" '
        'font-weight="700">Python baseline</text>',
        '<text x="984" y="132" text-anchor="end" fill="#334155" '
        'font-size="15" font-weight="700">1.000×</text>',
        f'<rect x="54" y="144" width="{int(width / scale)}" height="24" '
        'rx="7" fill="#475569"/>',
        '<text x="54" y="203" fill="#0f172a" font-size="15" '
        'font-weight="700">From-scratch current Rust</text>',
        f'<text x="984" y="203" text-anchor="end" fill="#0f172a" '
        f'font-size="15" font-weight="750">{_number(speed)}× · 95% '
        f'[{_number(interval["lower"])}, {_number(interval["upper"])}]</text>',
        f'<rect x="54" y="215" width="{int(width * speed / scale)}" '
        'height="24" rx="7" fill="#047857"/>',
    ])
    return _finish(lines, 334)


def render_outcomes(results: Mapping[str, Any]) -> bytes:
    total = results["case_denominator"]
    faster = results["statistically_faster_case_count"]
    slower = results["statistically_slower_case_count"]
    uncertain = total - faster - slower
    require(total == PUBLIC_CASE_COUNT and min(faster, slower, uncertain) >= 0,
            "all 864 faster, uncertain, and slower cases remain mandatory")
    width = 930
    green = width * faster // total
    amber = width * uncertain // total
    red = width - green - amber
    lines = _svg_frame(
        "Which public examples are faster?",
        "Every original case is classified using its independently "
        "recomputed 95 percent paired confidence interval.",
        291,
    )
    lines.extend([
        '<rect x="34" y="101" width="972" height="122" rx="14" fill="#ffffff"/>',
        f'<rect x="54" y="126" width="{green}" height="31" '
        'fill="#047857"/>',
        f'<rect x="{54 + green}" y="126" width="{amber}" height="31" '
        'fill="#d97706"/>',
        f'<rect x="{54 + green + amber}" y="126" width="{red}" height="31" '
        'fill="#be123c"/>',
        f'<circle cx="59" cy="190" r="6" fill="#047857"/>'
        f'<text x="73" y="194" fill="#14532d" font-size="13">'
        f'Faster: {faster} / {total}</text>',
        f'<circle cx="334" cy="190" r="6" fill="#d97706"/>'
        f'<text x="348" y="194" fill="#78350f" font-size="13">'
        f'Uncertain: {uncertain} / {total}</text>',
        f'<circle cx="665" cy="190" r="6" fill="#be123c"/>'
        f'<text x="679" y="194" fill="#881337" font-size="13">'
        f'Slower: {slower} / {total}</text>',
    ])
    return _finish(lines, 291)


def render_operations(operations: list[dict[str, Any]]) -> bytes:
    require(type(operations) is list and len(operations) == len(OPERATIONS)
            and [row.get("operation") for row in operations] == list(OPERATIONS)
            and all(row.get("case_denominator") == 24 for row in operations),
            "the chart must preserve all 36 original 24-case public operations")
    per_column = (len(operations) + 1) // 2
    height = 136 + per_column * 44 + 59
    scale = max(1.0, *(row["speedup_vs_baseline"] for row in operations))
    lines = _svg_frame(
        "Every public regular-expression operation",
        "All 36 equally weighted public API groups are shown; each contains "
        "all 24 original cases and includes any slower cases.",
        height,
    )
    for index, row in enumerate(operations):
        column = index // per_column
        position = index % per_column
        x = 42 + column * 510
        y = 104 + position * 44
        ratio = row["speedup_vs_baseline"]
        color = "#047857" if ratio >= 1.0 else "#be123c"
        lines.extend([
            f'<text x="{x}" y="{y + 11}" fill="#334155" font-size="11">'
            f'{_xml(row["operation"])}</text>',
            f'<rect x="{x}" y="{y + 17}" width="360" height="12" '
            'rx="5" fill="#e2e8f0"/>',
            f'<rect x="{x}" y="{y + 17}" '
            f'width="{int(360 * ratio / scale)}" height="12" '
            f'rx="5" fill="{color}"/>',
            f'<text x="{x + 462}" y="{y + 28}" text-anchor="end" '
            f'fill="{color}" font-size="11" font-weight="650">'
            f'{_number(ratio)}× · {row["case_denominator"]} cases</text>',
        ])
    return _finish(lines, height)


def render_regressions(results: Mapping[str, Any]) -> bytes:
    losses = results["all_regressions_over_20_percent"]
    require(type(losses) is list
            and len(losses) == results["regression_over_20_percent_count"]
            and all(type(row) is dict
                    and row.get("regression_exceeds_20_percent") is True
                    for row in losses),
            "every genuine public slowdown above 20 percent must remain visible")
    ordered = sorted(
        losses, key=lambda row: (-row["rust_change_percent"], row["case"]),
    )
    visible = max(1, len(ordered))
    height = 150 + visible * 34 + 56
    maximum = max([20.0] + [row["rust_change_percent"] for row in ordered])
    lines = _svg_frame(
        "Every public case more than 20% slower",
        "No public regression is omitted. Values show the complete paired "
        "geometric slowdown relative to Python.",
        height,
    )
    if not ordered:
        lines.append(
            '<text x="48" y="132" fill="#065f46" font-size="15" '
            'font-weight="650">No measured public case is more than '
            '20% slower.</text>',
        )
    for index, row in enumerate(ordered):
        y = 103 + index * 34
        percent = row["rust_change_percent"]
        require(math.isfinite(percent) and percent > 20.0,
                "an invented or under-threshold regression was displayed")
        lines.extend([
            f'<text x="45" y="{y + 12}" fill="#334155" font-size="10">'
            f'{_xml(row["case"])} · {_xml(row["operation"])}</text>',
            f'<rect x="477" y="{y + 1}" '
            f'width="{int(410 * percent / maximum)}" height="14" '
            'rx="5" fill="#be123c"/>',
            f'<text x="983" y="{y + 13}" text-anchor="end" '
            f'fill="#881337" font-size="11" font-weight="650">'
            f'+{_number(percent, 1)}%</text>',
        ])
    return _finish(lines, height)


def build_manifest(
    pins: EvidencePins, report: Mapping[str, Any],
    results: Mapping[str, Any], operations: list[dict[str, Any]],
    charts: Mapping[str, bytes],
) -> dict[str, Any]:
    require(set(charts) == {
        OVERALL_RELATIVE, OUTCOMES_RELATIVE, OPERATIONS_RELATIVE,
        REGRESSIONS_RELATIVE,
    }, "exactly four deterministic public speed charts are mandatory")
    return {
        "schema": SCHEMA + "-manifest",
        "status": "PASS",
        "chart_label": CHART_LABEL,
        "practice_label": PRACTICE_LABEL,
        "python": "3.14.6",
        "checker_source_relative": CHECKER_RELATIVE,
        "checker_source_sha256": pins.checker,
        "correctness_renderer_relative": CORRECTNESS_RENDERER_RELATIVE,
        "correctness_renderer_sha256": pins.correctness_renderer,
        "correctness_recorder_sha256": pins.correctness_recorder,
        "public_matrix_sha256": pins.matrix,
        "baseline_records_sha256": pins.baseline,
        "public_report_relative": pins.report_relative,
        "public_report_sha256": pins.report,
        "public_report_bytes": len(canonical(report)),
        "correctness_receipt_relative": pins.correctness_receipt_relative,
        "correctness_receipt_sha256": pins.correctness_receipt,
        "candidate_source_relative": CANDIDATE_SOURCE_RELATIVE,
        "candidate_source_sha256": pins.candidate,
        "native_engine_relative": NATIVE_ENGINE_RELATIVE,
        "native_engine_sha256": pins.native_engine,
        "native_bridge_relative": NATIVE_BRIDGE_RELATIVE,
        "native_bridge_sha256": pins.native_bridge,
        "case_denominator": PUBLIC_CASE_COUNT,
        "paired_trials_per_case": PAIRED_TRIALS,
        "total_complete_paired_rows": PUBLIC_CASE_COUNT * PAIRED_TRIALS,
        "raw_paired_rows_sha256": report["raw_paired_rows_sha256"],
        "weight_policy": results["weight_policy"],
        "point_estimator": results["point_estimator"],
        "overall_speedup_vs_python": results[
            "weighted_geomean_speedup_vs_baseline"
        ],
        "overall_95_percent_confidence_interval": results[
            "overall_speedup_confidence_interval"
        ],
        "statistically_faster_case_count": results[
            "statistically_faster_case_count"
        ],
        "uncertain_case_count": (
            PUBLIC_CASE_COUNT
            - results["statistically_faster_case_count"]
            - results["statistically_slower_case_count"]
        ),
        "statistically_slower_case_count": results[
            "statistically_slower_case_count"
        ],
        "regression_over_20_percent_count": results[
            "regression_over_20_percent_count"
        ],
        "all_regressions_over_20_percent": results[
            "all_regressions_over_20_percent"
        ],
        "all_case_results": results["all_case_results"],
        "all_operation_results": operations,
        "charts": [
            {
                "path": relative,
                "sha256": hashlib.sha256(charts[relative]).hexdigest(),
                "bytes": len(charts[relative]),
            }
            for relative in (
                OVERALL_RELATIVE, OUTCOMES_RELATIVE,
                OPERATIONS_RELATIVE, REGRESSIONS_RELATIVE,
            )
        ],
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "native_memory": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def render_actual(pins: EvidencePins) -> tuple[dict[str, bytes], bytes, dict[str, Any]]:
    _, _, matrix = authenticate_frozen_sources(pins)
    report_raw = read_owned_regular(pins.report_relative, pins.report,
                                    MAX_EVIDENCE_BYTES)
    receipt_raw = read_owned_regular(
        pins.correctness_receipt_relative, pins.correctness_receipt,
        MAX_EVIDENCE_BYTES,
    )
    report = decode_canonical(report_raw, "complete frozen public speed report")
    receipt = decode_canonical(receipt_raw,
                               "complete current durable public correctness receipt")
    results, operations = validate_public_report(
        report, report_raw, receipt, receipt_raw, matrix, pins,
    )
    charts = {
        OVERALL_RELATIVE: render_overall(results),
        OUTCOMES_RELATIVE: render_outcomes(results),
        OPERATIONS_RELATIVE: render_operations(operations),
        REGRESSIONS_RELATIVE: render_regressions(results),
    }
    manifest = build_manifest(pins, report, results, operations, charts)
    verify_runtime()
    return charts, canonical(manifest), manifest


def write_atomic(relative: str, payload: bytes) -> dict[str, Any]:
    require(relative in APPROVED_OUTPUTS and type(payload) is bytes
            and 0 < len(payload) <= MAX_EVIDENCE_BYTES,
            "write only an exact bounded public speed chart or manifest")
    with owned_parent(relative, output=True) as (directory, basename):
        try:
            previous = os.stat(basename, dir_fd=directory,
                               follow_symlinks=False)
        except FileNotFoundError:
            previous = None
        if previous is not None:
            require(stat.S_ISREG(previous.st_mode),
                    "refusing to overwrite a symlinked speed-chart destination")
        temporary = "." + basename + ".rust-public-speed-v1-" + str(os.getpid())
        flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                 | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
        descriptor: int | None = None
        original_info: os.stat_result | None = None
        published = False
        try:
            descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
            original_info = os.fstat(descriptor)
            require(stat.S_ISREG(original_info.st_mode),
                    "the exclusive chart temporary is not an owned regular file")
            written = os.write(descriptor, payload)
            require(type(written) is int and written == len(payload),
                    "the single atomic speed-chart write was incomplete")
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
                    actual = os.stat(temporary, dir_fd=directory,
                                     follow_symlinks=False)
                except FileNotFoundError:
                    actual = None
                if actual is not None:
                    require(stat.S_ISREG(actual.st_mode)
                            and (actual.st_dev, actual.st_ino)
                            == (original_info.st_dev, original_info.st_ino),
                            "refusing to remove a foreign speed-chart inode")
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


def _synthetic_documents() -> tuple[
    dict[str, Any], dict[str, Any], bytes, bytes,
    list[dict[str, Any]], EvidencePins, dict[str, Any],
]:
    matrix: list[dict[str, Any]] = []
    baseline_records: list[dict[str, Any]] = []
    for dataset in range(24):
        domain = "text" if dataset < 12 else "bytes"
        for operation in OPERATIONS:
            case_id = "rust-public-practice.v1." + format(len(matrix), "04d")
            case = {
                "case": case_id,
                "dataset": "synthetic." + domain + "." + format(dataset, "02d"),
                "domain": domain, "operation": operation,
                "lifecycle": "synthetic-only", "flags": 0,
                "pattern": {"type": domain, "value": "synthetic"},
                "subject": {"type": domain, "value": "synthetic"},
                "replacement": {"type": domain, "value": "synthetic"},
                "limit": 1, "weight_numerator": 1,
            }
            matrix.append(case)
            baseline_records.append({
                "case": case_id,
                "outcome": {
                    "status": "return", "value": "synthetic-only",
                    "callbacks": [], "warnings": [],
                },
            })
    matrix_hash = digest(matrix)
    baseline_hash = digest(baseline_records)
    label = "synthetic-public-speed-controls-v1"
    report_relative = APPROVED_PUBLIC_DIRECTORY + "/" + label + ".json"
    receipt_relative = (
        APPROVED_PUBLIC_DIRECTORY + "/synthetic-public-correctness-v1"
        "-publication-receipt.json"
    )
    candidate_hash = "12" * 32
    engine_hash = "34" * 32
    bridge_hash = "56" * 32
    rows: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    reference = {row["case"]: row["outcome"] for row in baseline_records}
    for trial in range(PAIRED_TRIALS):
        order = ["stdlib", "rust"] if trial % 2 == 0 else ["rust", "stdlib"]
        case_order = [case["case"] for case in matrix]
        random.Random(PUBLISHED_SEED ^ (trial + 1)).shuffle(case_order)
        worker_rows: dict[str, list[dict[str, Any]]] = {
            "stdlib": [], "rust": [],
        }
        pids = {"stdlib": 10_001 + trial * 2,
                "rust": 10_002 + trial * 2}
        for position, case_id in enumerate(case_order):
            case_index = int(case_id.rsplit(".", 1)[1])
            baseline_ns = 12_000 + case_index % 127 + trial
            if case_index % 17 == 0:
                rust_ns = baseline_ns * 2
            elif case_index % 13 == 0:
                rust_ns = baseline_ns
            else:
                rust_ns = max(1, baseline_ns * 3 // 4)
            expected = digest(reference[case_id])
            rows.append({
                "case": case_id, "trial": trial,
                "case_order_position": position, "pair_order": list(order),
                "baseline_pid": pids["stdlib"],
                "rust_pid": pids["rust"],
                "batch_iterations": BATCH_ITERATIONS,
                "correctness_checks_per_engine": (
                    WARMUP_ITERATIONS + BATCH_ITERATIONS + 1
                ),
                "expected_outcome_sha256": expected,
                "baseline_elapsed_ns": baseline_ns,
                "rust_elapsed_ns": rust_ns,
            })
            for engine, elapsed in (
                ("stdlib", baseline_ns), ("rust", rust_ns),
            ):
                worker_rows[engine].append({
                    "case": case_id, "trial": trial, "position": position,
                    "elapsed_ns": elapsed,
                    "batch_iterations": BATCH_ITERATIONS,
                    "correctness_checks": WARMUP_ITERATIONS + BATCH_ITERATIONS + 1,
                    "expected_outcome_sha256": expected,
                })
        for pair_position, engine in enumerate(order):
            provenance.append({
                "trial": trial, "engine": engine,
                "pair_execution_position": pair_position,
                "pid": pids[engine],
                "rows_sha256": digest(worker_rows[engine]),
            })
    provisional_pins = EvidencePins(
        checker=CHECKER_SHA256,
        correctness_renderer=CORRECTNESS_RENDERER_SHA256,
        correctness_recorder=CORRECTNESS_RECORDER_SHA256,
        matrix=matrix_hash,
        baseline=baseline_hash,
        report="ab" * 32,
        correctness_receipt="cd" * 32,
        candidate=candidate_hash,
        native_engine=engine_hash,
        native_bridge=bridge_hash,
        report_relative=report_relative,
        correctness_receipt_relative=receipt_relative,
    )
    report = {
        "schema": "rebar-rust-fresh-public-practice-v1-actual-public-practice-report",
        "status": "PASS", "label": PRACTICE_LABEL,
        "python": "3.14.6", "published_seed": PUBLISHED_SEED,
        "matrix_sha256": matrix_hash,
        "case_count": PUBLIC_CASE_COUNT, "matrix": matrix,
        "correctness_reference_records_sha256": baseline_hash,
        "correctness_reference_records": baseline_records,
        "baseline_correctness_pid": 41,
        "rust_correctness_pid": 42,
        "paired_trials": PAIRED_TRIALS,
        "batch_iterations": BATCH_ITERATIONS,
        "warmup_iterations": WARMUP_ITERATIONS,
        "trial_process_provenance": provenance,
        "raw_paired_rows_sha256": digest(rows),
        "raw_paired_rows": rows,
        "results": {},
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "candidate_production_reference_delegation": (
            "NOT AUDITED BY PUBLIC PRACTICE"
        ),
        "final_winner_selected": False,
    }
    _, observed_pairs = validate_raw_observations(report, matrix, provisional_pins)
    derived, _ = derive_statistics(matrix, observed_pairs)
    report["results"] = derived
    report_raw = canonical(report)
    receipt = {
        "schema": (
            "rebar-frozen-rust-public-correctness-recorder-v1"
            "-durable-publication-receipt"
        ),
        "status": "PASS", "label": "synthetic-public-correctness-v1",
        "practice_label": PRACTICE_LABEL, "python": "3.14.6",
        "checker_source_relative": CHECKER_RELATIVE,
        "checker_source_sha256": CHECKER_SHA256,
        "candidate_source_relative": CANDIDATE_SOURCE_RELATIVE,
        "candidate_source_sha256": candidate_hash,
        "candidate_source_bytes": 1,
        "candidate_source_device": 2,
        "candidate_source_inode": 3,
        "native_engine_relative": NATIVE_ENGINE_RELATIVE,
        "native_engine_sha256": engine_hash,
        "native_engine_bytes": 4,
        "native_engine_device": 5,
        "native_engine_inode": 6,
        "native_bridge_module": NATIVE_BRIDGE_MODULE,
        "native_bridge_relative": NATIVE_BRIDGE_RELATIVE,
        "native_bridge_sha256": bridge_hash,
        "native_bridge_bytes": 7,
        "native_bridge_device": 8,
        "native_bridge_inode": 9,
        "public_matrix_sha256": matrix_hash,
        "case_denominator": PUBLIC_CASE_COUNT,
        "baseline_records_sha256": baseline_hash,
        "rust_records_sha256": baseline_hash,
        "baseline_pid": 41, "rust_pid": 42,
        "correctness_status": "PASS", "mismatch_count": 0,
        "all_mismatches_preserved": True,
        "report_relative": (
            APPROVED_PUBLIC_DIRECTORY + "/synthetic-public-correctness-v1.json"
        ),
        "report_sha256": "ef" * 32,
        "report_bytes": 1,
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
    pins = replace(
        provisional_pins,
        report=hashlib.sha256(report_raw).hexdigest(),
        correctness_receipt=hashlib.sha256(receipt_raw).hexdigest(),
    )
    return report, receipt, report_raw, receipt_raw, matrix, pins, derived


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
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, deny(
                "blocked_reads", "synthetic speed controls cannot read a file",
            ))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"), (Path, "unlink"),
            (Path, "mkdir"),
        ):
            install(owner, name, deny(
                "blocked_writes", "synthetic speed controls cannot write a file",
            ))
        install(importlib, "import_module", deny(
            "blocked_imports", "synthetic speed controls cannot import an engine",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "synthetic speed controls cannot import a module",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny(
                "blocked_workers", "synthetic speed controls cannot start a worker",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "synthetic speed controls cannot start a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "process_time_ns",
        ):
            install(time, name, deny(
                "blocked_clocks", "synthetic speed controls cannot sample a clock",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections", "synthetic speed controls cannot collect garbage",
        ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a genuine synthetic speed control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a source-only speed poison was duplicated")
        try:
            action()
        except (RenderError, ValueError, TypeError, KeyError, OSError):
            rejected.append(name)
            return
        raise RenderError("a forged public observation was accepted: " + name)

    with source_only_boundary() as effects:
        report, receipt, raw, receipt_raw, matrix, pins, expected = (
            _synthetic_documents()
        )
        derived, operations = validate_public_report(
            report, raw, receipt, receipt_raw, matrix, pins,
            expected_results=expected,
        )
        charts = {
            OVERALL_RELATIVE: render_overall(derived),
            OUTCOMES_RELATIVE: render_outcomes(derived),
            OPERATIONS_RELATIVE: render_operations(operations),
            REGRESSIONS_RELATIVE: render_regressions(derived),
        }
        manifest = build_manifest(pins, report, derived, operations, charts)
        accept("synthesize-all-864-original-public-cases-in-memory",
               len(matrix) == PUBLIC_CASE_COUNT and derived["case_denominator"]
               == PUBLIC_CASE_COUNT)
        accept("preserve-all-10368-paired-12-round-observations",
               len(report["raw_paired_rows"])
               == PUBLIC_CASE_COUNT * PAIRED_TRIALS
               and derived["total_complete_paired_rows"]
               == PUBLIC_CASE_COUNT * PAIRED_TRIALS)
        accept("preserve-all-36-equally-weighted-public-api-groups",
               len(operations) == len(OPERATIONS)
               and all(row["case_denominator"] == 24 for row in operations))
        accept("independently-recompute-real-95-percent-case-intervals",
               all(row["speedup_confidence_interval"]["confidence_level"] == 0.95
                   and row["speedup_confidence_interval"]["resamples"]
                   == BOOTSTRAP_RESAMPLES
                   for row in derived["all_case_results"]))
        accept("derive-faster-uncertain-slower-with-unchanged-denominator",
               manifest["statistically_faster_case_count"]
               + manifest["uncertain_case_count"]
               + manifest["statistically_slower_case_count"]
               == PUBLIC_CASE_COUNT)
        accept("preserve-every-real-synthetic-regression-over-20-percent",
               bool(derived["all_regressions_over_20_percent"])
               and len(derived["all_regressions_over_20_percent"])
               == derived["regression_over_20_percent_count"])
        accept("render-only-four-complete-accessible-public-svg-charts",
               len(charts) == 4
               and all(payload.startswith(b"<svg ")
                       and b'role="img"' in payload
                       and CHART_LABEL.encode("utf-8") in payload
                       for payload in charts.values()))
        accept("never-claim-measured-native-memory-or-a-winner",
               manifest["native_memory"] == "NOT MEASURED"
               and manifest["candidate_qualified_for_hidden_benchmark"] is False
               and manifest["final_winner_selected"] is False)
        accept("bind-full-public-report-current-receipt-and-three-rust-components",
               manifest["public_report_sha256"] == pins.report
               and manifest["correctness_receipt_sha256"]
               == pins.correctness_receipt
               and manifest["candidate_source_sha256"] == pins.candidate
               and manifest["native_engine_sha256"] == pins.native_engine
               and manifest["native_bridge_sha256"] == pins.native_bridge)
        accept("canonical-manifest-keeps-all-cases-and-all-public-regressions",
               len(manifest["all_case_results"]) == PUBLIC_CASE_COUNT
               and manifest["all_regressions_over_20_percent"]
               == derived["all_regressions_over_20_percent"]
               and decode_canonical(canonical(manifest), "synthetic manifest")
               == manifest)

        for index, key in enumerate(sorted(REPORT_FIELDS)):
            altered = dict(report)
            altered.pop(key)
            altered_raw = canonical(altered)
            altered_pins = replace(pins, report=hashlib.sha256(altered_raw).hexdigest())
            reject(
                "reject-missing-complete-public-speed-report-field-"
                + format(index, "02d"),
                lambda altered=altered, altered_raw=altered_raw,
                altered_pins=altered_pins: validate_public_report(
                    altered, altered_raw, receipt, receipt_raw,
                    matrix, altered_pins, expected_results=expected,
                ),
            )
        for index, key in enumerate(sorted(RECEIPT_FIELDS)):
            altered = dict(receipt)
            altered.pop(key)
            altered_raw = canonical(altered)
            altered_pins = replace(
                pins, correctness_receipt=hashlib.sha256(altered_raw).hexdigest(),
            )
            reject(
                "reject-missing-current-durable-correctness-field-"
                + format(index, "02d"),
                lambda altered=altered, altered_raw=altered_raw,
                altered_pins=altered_pins: validate_public_report(
                    report, raw, altered, altered_raw,
                    matrix, altered_pins, expected_results=expected,
                ),
            )
        for index, key, value in (
            (0, "case_count", PUBLIC_CASE_COUNT - 1),
            (1, "paired_trials", PAIRED_TRIALS - 1),
            (2, "batch_iterations", BATCH_ITERATIONS + 1),
            (3, "warmup_iterations", WARMUP_ITERATIONS + 1),
            (4, "hidden_cases_read", 1),
            (5, "benchmark_files_read", 1),
            (6, "final_winner_selected", True),
            (7, "candidate_production_reference_delegation", "PASS"),
            (8, "published_seed", PUBLISHED_SEED + 1),
            (9, "matrix_sha256", "ab" * 32),
        ):
            altered = dict(report)
            altered[key] = value
            altered_raw = canonical(altered)
            altered_pins = replace(pins, report=hashlib.sha256(altered_raw).hexdigest())
            reject(
                "reject-false-speed-denominator-hidden-data-or-win-"
                + format(index, "02d"),
                lambda altered=altered, altered_raw=altered_raw,
                altered_pins=altered_pins: validate_public_report(
                    altered, altered_raw, receipt, receipt_raw,
                    matrix, altered_pins, expected_results=expected,
                ),
            )
        for index in range(18):
            altered = dict(report)
            altered_rows = list(report["raw_paired_rows"])
            poisoned_row = dict(altered_rows[index])
            key, value = (
                ("baseline_elapsed_ns", 0) if index % 6 == 0
                else ("rust_elapsed_ns", 0) if index % 6 == 1
                else ("trial", PAIRED_TRIALS) if index % 6 == 2
                else ("case_order_position", -1) if index % 6 == 3
                else ("expected_outcome_sha256", "ab" * 32)
                if index % 6 == 4 else ("pair_order", ["rust", "stdlib"])
            )
            poisoned_row[key] = value
            altered_rows[index] = poisoned_row
            altered["raw_paired_rows"] = altered_rows
            altered["raw_paired_rows_sha256"] = digest(altered_rows)
            altered_raw = canonical(altered)
            altered_pins = replace(pins, report=hashlib.sha256(altered_raw).hexdigest())
            reject(
                "reject-forged-actual-public-paired-observation-"
                + format(index, "02d"),
                lambda altered=altered, altered_raw=altered_raw,
                altered_pins=altered_pins: validate_public_report(
                    altered, altered_raw, receipt, receipt_raw,
                    matrix, altered_pins, expected_results=expected,
                ),
            )

        for name, action in (
            ("reject-hidden-and-performance-root-path",
             lambda: _relative_parts("performance/hidden.json")),
            ("reject-parent-escaping-public-report",
             lambda: _relative_parts("experiments/rust_public_practice_v1/../x.json")),
            ("reject-foreign-publication-destination",
             lambda: _relative_parts("docs/evidence/unapproved.svg", output=True)),
            ("block-source-only-actual-report-read",
             lambda: builtins.open(pins.report_relative, "rb")),
            ("block-source-only-actual-receipt-read",
             lambda: io.open(pins.correctness_receipt_relative, "rb")),
            ("block-source-only-owned-raw-report-open",
             lambda: os.open(pins.report_relative, os.O_RDONLY)),
            ("block-source-only-actual-speed-chart-write",
             lambda: os.write(1, b"forbidden")),
            ("block-source-only-speed-chart-replacement",
             lambda: os.replace(OVERALL_RELATIVE, OUTCOMES_RELATIVE)),
            ("block-source-only-hidden-benchmark-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("block-source-only-frozen-checker-import",
             lambda: importlib.import_module(CHECKER_MODULE)),
            ("block-source-only-actual-reference-worker",
             lambda: subprocess.Popen([str(PINNED_PYTHON)])),
            ("block-source-only-background-thread",
             lambda: threading.Thread(target=lambda: None).start()),
            ("block-source-only-performance-clock",
             lambda: time.perf_counter()),
            ("block-source-only-wall-clock", lambda: time.time()),
            ("block-source-only-real-garbage-collection", lambda: gc.collect()),
        ):
            reject(name, action)

        accept("prove-ten-source-only-real-effect-counters-are-zero",
               all(effects[key] == 0 for key in (
                   "file_reads", "file_writes", "candidate_imports",
                   "reference_imports", "workers_started", "threads_started",
                   "clock_samples", "gc_collections", "hidden_cases_read",
                   "performance_files_read",
               )))
        accept("prove-seven-independent-actual-effects-are-intercepted",
               all(effects[key] > 0 for key in (
                   "blocked_reads", "blocked_writes", "blocked_imports",
                   "blocked_workers", "blocked_threads", "blocked_clocks",
                   "blocked_gc_collections",
               )))
        accept("reject-at-least-80-distinct-real-public-speed-forgeries",
               len(rejected) >= 80 and len(rejected) == len(set(rejected)))

    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "chart_label": CHART_LABEL,
        "python": "3.14.6",
        "checker_source_sha256": CHECKER_SHA256,
        "correctness_renderer_source_sha256": CORRECTNESS_RENDERER_SHA256,
        "correctness_recorder_source_sha256": CORRECTNESS_RECORDER_SHA256,
        "public_matrix_sha256": MATRIX_SHA256,
        "case_denominator": PUBLIC_CASE_COUNT,
        "operation_count": len(OPERATIONS),
        "paired_trials_per_case": PAIRED_TRIALS,
        "total_complete_paired_rows": PUBLIC_CASE_COUNT * PAIRED_TRIALS,
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
        "native_memory": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "synthetic": True,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render only a complete, independently verified public practice",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--check", action="store_true")
    parser.add_argument("--report")
    parser.add_argument("--report-sha256")
    parser.add_argument("--correctness-receipt")
    parser.add_argument("--correctness-receipt-sha256")
    parser.add_argument("--practice-source-sha256")
    parser.add_argument("--correctness-renderer-source-sha256")
    parser.add_argument("--correctness-recorder-source-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def command_pins(options: argparse.Namespace) -> EvidencePins:
    require(type(options.report) is str and type(options.correctness_receipt) is str,
            "supply the exact frozen public timing report and current receipt")
    _relative_parts(options.report)
    _relative_parts(options.correctness_receipt)
    require(options.correctness_receipt.endswith("-publication-receipt.json"),
            "the current correctness gate requires its independently durable receipt")
    values = {
        "checker": options.practice_source_sha256,
        "correctness_renderer": options.correctness_renderer_source_sha256,
        "correctness_recorder": options.correctness_recorder_source_sha256,
        "report": options.report_sha256,
        "correctness_receipt": options.correctness_receipt_sha256,
        "candidate": options.candidate_source_sha256,
        "native_engine": options.native_engine_sha256,
        "native_bridge": options.native_bridge_sha256,
    }
    for name, value in values.items():
        validate_digest(value, name)
    require(values["checker"] == CHECKER_SHA256
            and values["correctness_renderer"] == CORRECTNESS_RENDERER_SHA256
            and values["correctness_recorder"] == CORRECTNESS_RECORDER_SHA256,
            "the independently frozen practice and correctness controllers changed")
    return EvidencePins(
        checker=values["checker"],
        correctness_renderer=values["correctness_renderer"],
        correctness_recorder=values["correctness_recorder"],
        matrix=MATRIX_SHA256, baseline=BASELINE_RECORDS_SHA256,
        report=values["report"],
        correctness_receipt=values["correctness_receipt"],
        candidate=values["candidate"],
        native_engine=values["native_engine"],
        native_bridge=values["native_bridge"],
        report_relative=options.report,
        correctness_receipt_relative=options.correctness_receipt,
    )


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "report", "report_sha256", "correctness_receipt",
            "correctness_receipt_sha256", "practice_source_sha256",
            "correctness_renderer_source_sha256",
            "correctness_recorder_source_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "synthetic speed controls cannot read actual reports or artifacts")
        document = source_self_test()
    else:
        pins = command_pins(options)
        charts, manifest_raw, manifest = render_actual(pins)
        all_payloads = dict(charts)
        all_payloads[MANIFEST_RELATIVE] = manifest_raw
        publications: list[dict[str, Any]] = []
        for relative in APPROVED_OUTPUTS:
            payload = all_payloads[relative]
            if options.write:
                publications.append(write_atomic(relative, payload))
            else:
                actual = read_owned_regular(
                    relative, hashlib.sha256(payload).hexdigest(),
                    MAX_EVIDENCE_BYTES,
                )
                require(actual == payload,
                        "a complete deterministic public speed chart was altered")
        document = {
            "schema": SCHEMA + ("-published" if options.write else "-checked"),
            "status": "PASS",
            "chart_label": CHART_LABEL,
            "public_matrix_sha256": MATRIX_SHA256,
            "case_denominator": PUBLIC_CASE_COUNT,
            "paired_trials_per_case": PAIRED_TRIALS,
            "total_complete_paired_rows": PUBLIC_CASE_COUNT * PAIRED_TRIALS,
            "report_sha256": pins.report,
            "correctness_receipt_sha256": pins.correctness_receipt,
            "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "charts": manifest["charts"],
            "publications": publications,
            "hidden_cases_read": 0,
            "native_memory": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
