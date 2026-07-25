#!/usr/bin/env python3
"""Durably preserve one complete, frozen Rust public-practice comparison.

Only explicit ``--record`` starts the candidate. It invokes the independently
frozen correctness checker exactly once, preserves every genuine mismatch, and
publishes both the full canonical report and a separately durable receipt.
Import and ``--self-test`` never run a candidate, clock, benchmark, or record.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib
from importlib.machinery import EXTENSION_SUFFIXES
import os
from pathlib import Path
import stat
import sys
from typing import Any, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/record_rust_public_correctness_v1.py"
CHECKER_RELATIVE = "tools/rust_public_practice_benchmark_v1.py"
CHECKER_MODULE = "tools.rust_public_practice_benchmark_v1"
CHECKER_SHA256 = (
    "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37"
)
PUBLIC_MATRIX_SHA256 = (
    "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e"
)
EXPECTED_BASELINE_RECORDS_SHA256 = (
    "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c"
)
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
CANDIDATE_RELATIVE = "candidates/rust_candidate.py"
BRIDGE_MODULE = "candidates._rust_bridge"
NATIVE_ENGINE_RELATIVE = "candidates/_rust_engine.so"
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
SCHEMA = "rebar-frozen-rust-public-correctness-recorder-v1"
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
PUBLIC_CASE_COUNT = 864

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


class RecorderError(Exception):
    """Preserve a genuine first provenance, preflight, or publication failure."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


def verify_runtime() -> None:
    expected_root = str(ROOT)
    expected_source = str(ROOT / SOURCE_RELATIVE)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == expected_root
            and os.path.realpath(expected_root) == expected_root
            and os.path.abspath(__file__) == expected_source
            and os.path.realpath(__file__) == expected_source
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
            "use only the literal no-symlink root, source, and pinned CPython")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a Rust candidate escaped into the source-only recorder process")


def validate_digest(value: Any, *, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(letter in "0123456789abcdef" for letter in value)
            and len(set(value)) > 1,
            "an exact independently pinned lowercase SHA-256 is required: "
            + label)
    return value


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64,
            "a bounded lowercase public-record slug is required")
    require(value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for letter in value)
            and "--" not in value,
            "the public-record slug contains an escaping or ambiguous component")
    return value


def approved_relative_paths(label: Any) -> tuple[str, str]:
    slug = validate_label(label)
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def directory_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    )


def regular_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _safe_relative_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\x00" not in relative and "\\" not in relative,
            "an exact bounded owned relative path is required")
    components = tuple(relative.split("/"))
    require(all(component not in ("", ".", "..") for component in components)
            and "/".join(components) == relative,
            "an escaping, empty, or substituted relative component is forbidden")
    return components


def read_owned_regular(
    relative: str, *, maximum: int,
    expected_sha256: str | None = None,
) -> tuple[bytes, dict[str, Any]]:
    components = _safe_relative_parts(relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "an exact bounded frozen source or owned bridge read is mandatory")
    if expected_sha256 is not None:
        validate_digest(expected_sha256, label=relative)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        root_info = os.fstat(current)
        require(stat.S_ISDIR(root_info.st_mode),
                "the literal frozen repository root is not an actual directory")
        for name in components[:-1]:
            following = os.open(name, directory_flags(), dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "an owned source component is not a no-follow directory")
            current = following
        descriptor = os.open(components[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode)
                and 0 < info.st_size <= maximum,
                "the frozen owned source or bridge is not a bounded regular file")
        remaining = info.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the authentic owned source or Rust bridge was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "an owned source or bridge changed while being authenticated")
        final_info = os.fstat(descriptor)
        require(final_info.st_dev == info.st_dev
                and final_info.st_ino == info.st_ino
                and final_info.st_size == info.st_size,
                "the actual authenticated source or bridge inode changed")
        actual = b"".join(chunks)
        fingerprint = hashlib.sha256(actual).hexdigest()
        require(expected_sha256 is None or fingerprint == expected_sha256,
                "the exact frozen source bytes changed: " + relative)
        return actual, {
            "relative": relative,
            "sha256": fingerprint,
            "bytes": len(actual),
            "device": info.st_dev,
            "inode": info.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def authenticate_frozen_checker() -> Any:
    verify_runtime()
    read_owned_regular(
        CHECKER_RELATIVE, maximum=MAX_SOURCE_BYTES,
        expected_sha256=CHECKER_SHA256,
    )
    checker = importlib.import_module(CHECKER_MODULE)
    expected_file = str(ROOT / CHECKER_RELATIVE)
    require(checker.__name__ == CHECKER_MODULE
            and type(checker.__file__) is str
            and os.path.abspath(checker.__file__) == expected_file
            and os.path.realpath(checker.__file__) == expected_file
            and checker.ROOT == ROOT
            and checker.PINNED_PYTHON == PINNED_PYTHON
            and checker.MATRIX_SHA256 == PUBLIC_MATRIX_SHA256
            and checker.DEFAULT_PAIRED_TRIALS == 12,
            "the frozen public checker, root, pinned runtime, or matrix changed")
    checker.verify_pinned_runtime()
    matrix = checker.build_public_matrix()
    require(checker.validate_public_matrix(matrix) == PUBLIC_MATRIX_SHA256
            and len(matrix) == PUBLIC_CASE_COUNT
            and checker.digest(matrix) == PUBLIC_MATRIX_SHA256,
            "the original frozen complete public-practice cases were substituted")
    return checker


def authenticate_candidate_files(
    source_sha256: str, native_engine_sha256: str, native_bridge_sha256: str,
) -> dict[str, Any]:
    pinned_source = validate_digest(source_sha256, label="Rust candidate source")
    pinned_engine = validate_digest(
        native_engine_sha256, label="actual semantic native Rust engine",
    )
    pinned_bridge = validate_digest(
        native_bridge_sha256, label="actual native CPython Rust bridge",
    )
    _, source = read_owned_regular(
        CANDIDATE_RELATIVE, maximum=MAX_SOURCE_BYTES,
        expected_sha256=pinned_source,
    )
    _, native_engine = read_owned_regular(
        NATIVE_ENGINE_RELATIVE, maximum=MAX_BINARY_BYTES,
        expected_sha256=pinned_engine,
    )
    actual_bridges: list[dict[str, Any]] = []
    for suffix in dict.fromkeys(EXTENSION_SUFFIXES):
        relative = "candidates/_rust_bridge" + suffix
        try:
            _, provenance = read_owned_regular(
                relative, maximum=MAX_BINARY_BYTES,
            )
        except FileNotFoundError:
            continue
        actual_bridges.append(provenance)
    require(len(actual_bridges) == 1,
            "exactly one owned no-symlink candidates._rust_bridge is required")
    bridge = actual_bridges[0]
    require(bridge["relative"].startswith("candidates/_rust_bridge.")
            and any(bridge["relative"].endswith(suffix)
                    for suffix in EXTENSION_SUFFIXES)
            and bridge["sha256"] == pinned_bridge
            and valid_candidate_provenance(
                source, native_engine, bridge,
                pinned_source, pinned_engine, pinned_bridge,
            ),
            "the exact owned Rust adapter, semantic engine, or bridge changed")
    return {
        "source": source,
        "native_engine": native_engine,
        "native_bridge": bridge,
    }


def valid_candidate_provenance(
    source: Any, native_engine: Any, bridge: Any,
    expected_source: str, expected_engine: str, expected_bridge: str,
) -> bool:
    return (
        type(source) is dict and type(native_engine) is dict
        and type(bridge) is dict
        and source.get("relative") == CANDIDATE_RELATIVE
        and source.get("sha256") == expected_source
        and type(source.get("bytes")) is int and source["bytes"] > 0
        and native_engine.get("relative") == NATIVE_ENGINE_RELATIVE
        and native_engine.get("sha256") == expected_engine
        and type(native_engine.get("bytes")) is int
        and native_engine["bytes"] > 0
        and type(bridge.get("relative")) is str
        and bridge["relative"].startswith("candidates/_rust_bridge.")
        and any(bridge["relative"].endswith(suffix)
                for suffix in EXTENSION_SUFFIXES)
        and bridge.get("sha256") == expected_bridge
        and type(bridge.get("bytes")) is int and bridge["bytes"] > 0
        and type(source.get("device")) is int
        and type(source.get("inode")) is int
        and type(native_engine.get("device")) is int
        and type(native_engine.get("inode")) is int
        and type(bridge.get("device")) is int
        and type(bridge.get("inode")) is int
    )


@contextlib.contextmanager
def preflight_fresh_outputs(
    checker: Any, label: str,
) -> Iterator[dict[str, Any]]:
    report_relative, receipt_relative = approved_relative_paths(label)
    report_parts = checker.approved_output_parts(report_relative)
    receipt_parts = checker.approved_output_parts(receipt_relative)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "only the exact two distinct public-practice report paths are allowed")
    opened: list[int] = []
    created: list[tuple[int, str]] = []
    preflight_completed = False
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        root_info = os.fstat(current)
        require(stat.S_ISDIR(root_info.st_mode),
                "the literal approved root is not a no-follow directory")
        for component in report_parts[:-1]:
            try:
                following = os.open(component, directory_flags(), dir_fd=current)
            except FileNotFoundError:
                os.mkdir(component, mode=0o755, dir_fd=current)
                created.append((current, component))
                following = os.open(component, directory_flags(), dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "an approved evidence component is not a no-follow directory")
            current = following
        parent_info = os.fstat(current)
        for name in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(name, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError(
                "refusing to replace an existing real or symlinked report: "
                + name,
            )
        preflight_completed = True
        yield {
            "report_relative": report_relative,
            "receipt_relative": receipt_relative,
            "report_basename": report_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": parent_info.st_dev,
            "directory_inode": parent_info.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
        }
    finally:
        active_error = sys.exc_info()[1]
        cleanup_errors: list[Exception] = []
        if not preflight_completed:
            for descriptor, component in reversed(created):
                try:
                    os.rmdir(component, dir_fd=descriptor)
                    os.fsync(descriptor)
                except Exception as error:
                    cleanup_errors.append(error)
        for descriptor in reversed(opened):
            try:
                os.close(descriptor)
            except Exception as error:
                cleanup_errors.append(error)
        if cleanup_errors and active_error is None:
            raise RecorderError(
                "an owned preflight cleanup failed: " + str(cleanup_errors[0]),
            ) from cleanup_errors[0]


def verify_retained_directory(preflight: Mapping[str, Any]) -> None:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "the actual approved public-report directory was not retained")
    info = os.fstat(descriptor)
    require(stat.S_ISDIR(info.st_mode)
            and info.st_dev == preflight.get("directory_device")
            and info.st_ino == preflight.get("directory_inode"),
            "the actual preflight-approved output directory was substituted")


def validate_complete_report(
    checker: Any, report: Any,
) -> dict[str, Any]:
    require(type(report) is dict,
            "the complete actual frozen correctness document is mandatory")
    expected = {
        "schema": checker.SCHEMA + "-actual-untimed-correctness",
        "label": checker.PRACTICE_LABEL,
        "python": "3.14.6",
        "published_seed": checker.PUBLISHED_SEED,
        "matrix_sha256": PUBLIC_MATRIX_SHA256,
        "case_denominator": PUBLIC_CASE_COUNT,
        "actual_baseline_cases": PUBLIC_CASE_COUNT,
        "actual_rust_cases": PUBLIC_CASE_COUNT,
        "baseline_records_sha256": EXPECTED_BASELINE_RECORDS_SHA256,
        "actual_candidate_workers": 1,
        "timing_trials_run": 0, "clock_samples": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "files_written": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for name, value in expected.items():
        require(report.get(name) == value,
                "an actual complete frozen correctness field changed: " + name)
    require(report.get("status") in ("PASS", "FAIL")
            and type(report.get("baseline_pid")) is int
            and report["baseline_pid"] > 0
            and type(report.get("rust_pid")) is int
            and report["rust_pid"] > 0
            and report["baseline_pid"] != report["rust_pid"]
            and validate_digest(
                report.get("rust_records_sha256"), label="actual Rust case vector",
            ), "a genuine actual worker or complete case-vector hash was forged")
    mismatches = report.get("all_mismatches")
    require(type(mismatches) is list
            and type(report.get("mismatch_count")) is int
            and report["mismatch_count"] == len(mismatches)
            and 0 <= len(mismatches) <= PUBLIC_CASE_COUNT
            and report.get("first_mismatch") == (
                mismatches[0] if mismatches else None
            )
            and report["status"] == ("FAIL" if mismatches else "PASS"),
            "an actual failed mismatch, first failure, or exit status was hidden")
    matrix = checker.build_public_matrix()
    positions = {case["case"]: index for index, case in enumerate(matrix)}
    previous = -1
    required_keys = {
        "case", "dataset", "domain", "operation", "lifecycle", "flags",
        "pattern", "subject", "replacement", "limit",
        "baseline_outcome", "rust_outcome",
    }
    for mismatch in mismatches:
        require(type(mismatch) is dict and set(mismatch) == required_keys
                and mismatch.get("case") in positions,
                "a complete original public mismatch was omitted or substituted")
        position = positions[mismatch["case"]]
        require(position > previous,
                "the authentic full mismatch order was repeated or reordered")
        original = matrix[position]
        require(all(mismatch.get(key) == original[key] for key in (
            "case", "dataset", "domain", "operation", "lifecycle", "flags",
            "pattern", "subject", "replacement", "limit",
        )), "an exact original mismatch input or case identity was substituted")
        original_outcome = mismatch["baseline_outcome"]
        rust_outcome = mismatch["rust_outcome"]
        require(type(original_outcome) is dict and type(rust_outcome) is dict
                and original_outcome != rust_outcome
                and original_outcome.get("status") in ("return", "raise")
                and rust_outcome.get("status") in ("return", "raise")
                and type(original_outcome.get("callbacks")) is list
                and type(rust_outcome.get("callbacks")) is list
                and type(original_outcome.get("warnings")) is list
                and type(rust_outcome.get("warnings")) is list,
                "an actual complete original outcome or warning was hidden")
        previous = position
    return dict(report)


def read_published_document(
    checker: Any, preflight: Mapping[str, Any], document: Mapping[str, Any],
    publication: Mapping[str, Any], *, kind: str,
) -> bytes:
    verify_retained_directory(preflight)
    require(kind in ("report", "receipt"),
            "only an exact preflighted report or receipt can be verified")
    relative = preflight[kind + "_relative"]
    basename = preflight[kind + "_basename"]
    expected = checker.canonical(dict(document))
    require(0 < len(expected) <= MAX_REPORT_BYTES
            and type(publication) is dict
            and publication.get("path") == relative
            and publication.get("bytes") == len(expected)
            and publication.get("sha256")
            == hashlib.sha256(expected).hexdigest()
            and publication.get("actual_write_calls") == 1
            and publication.get("file_fsync_completed") is True
            and publication.get("directory_fsync_completed") is True,
            "the genuine full exclusive " + kind + " publication was substituted")
    directory = preflight["directory_descriptor"]
    descriptor = os.open(
        basename, regular_flags(), dir_fd=directory,
    )
    try:
        info = os.fstat(descriptor)
        named_info = os.stat(
            basename, dir_fd=directory, follow_symlinks=False,
        )
        require(stat.S_ISREG(info.st_mode)
                and stat.S_ISREG(named_info.st_mode)
                and info.st_dev == named_info.st_dev
                and info.st_ino == named_info.st_ino
                and info.st_size == len(expected),
                "the exclusively published actual " + kind
                + " changed its exact inode or length")
        remaining = len(expected)
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the genuinely durable complete " + kind
                    + " readback was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "the actual published full " + kind
                + " has a concealed byte suffix")
    finally:
        os.close(descriptor)
    actual = b"".join(chunks)
    require(actual == expected
            and hashlib.sha256(actual).hexdigest() == publication["sha256"],
            "the durable full " + kind
            + " omitted or replaced its exact genuine canonical bytes")
    return actual


def read_published_report(
    checker: Any, preflight: Mapping[str, Any], report: Mapping[str, Any],
    publication: Mapping[str, Any],
) -> bytes:
    return read_published_document(
        checker, preflight, report, publication, kind="report",
    )


def read_published_receipt(
    checker: Any, preflight: Mapping[str, Any], receipt: Mapping[str, Any],
    publication: Mapping[str, Any],
) -> bytes:
    return read_published_document(
        checker, preflight, receipt, publication, kind="receipt",
    )


def require_unchanged_candidate(
    expected: Mapping[str, Any], source_sha256: str,
    native_engine_sha256: str, native_bridge_sha256: str,
) -> None:
    current = authenticate_candidate_files(
        source_sha256, native_engine_sha256, native_bridge_sha256,
    )
    require(current == dict(expected),
            "the exact Rust adapter, semantic engine, or bridge changed in flight")


def record_correctness(
    label: str, candidate_source_sha256: str,
    native_engine_sha256: str, native_bridge_sha256: str,
) -> dict[str, Any]:
    slug = validate_label(label)
    candidate_pin = validate_digest(
        candidate_source_sha256, label="actual owned Rust candidate source",
    )
    engine_pin = validate_digest(
        native_engine_sha256, label="actual frozen semantic Rust engine",
    )
    bridge_pin = validate_digest(
        native_bridge_sha256, label="actual frozen native CPython bridge",
    )
    checker = authenticate_frozen_checker()
    candidate = authenticate_candidate_files(
        candidate_pin, engine_pin, bridge_pin,
    )
    with preflight_fresh_outputs(checker, slug) as preflight:
        verify_retained_directory(preflight)

        # Exactly one genuine untimed candidate comparison. A FAIL is data, not
        # an exception or a reason to discard its complete mismatch vector.
        complete = validate_complete_report(
            checker, checker.run_correctness_only(),
        )
        verify_runtime()
        verify_retained_directory(preflight)
        require_unchanged_candidate(
            candidate, candidate_pin, engine_pin, bridge_pin,
        )

        report_publication = checker.write_approved_output(
            preflight["report_relative"], complete,
        )
        actual_report = read_published_report(
            checker, preflight, complete, report_publication,
        )

        receipt_document = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS",
            "label": slug,
            "practice_label": checker.PRACTICE_LABEL,
            "python": "3.14.6",
            "checker_source_relative": CHECKER_RELATIVE,
            "checker_source_sha256": CHECKER_SHA256,
            "candidate_source_relative": CANDIDATE_RELATIVE,
            "candidate_source_sha256": candidate["source"]["sha256"],
            "candidate_source_bytes": candidate["source"]["bytes"],
            "candidate_source_device": candidate["source"]["device"],
            "candidate_source_inode": candidate["source"]["inode"],
            "native_engine_relative": candidate["native_engine"]["relative"],
            "native_engine_sha256": candidate["native_engine"]["sha256"],
            "native_engine_bytes": candidate["native_engine"]["bytes"],
            "native_engine_device": candidate["native_engine"]["device"],
            "native_engine_inode": candidate["native_engine"]["inode"],
            "native_bridge_module": BRIDGE_MODULE,
            "native_bridge_relative": candidate["native_bridge"]["relative"],
            "native_bridge_sha256": candidate["native_bridge"]["sha256"],
            "native_bridge_bytes": candidate["native_bridge"]["bytes"],
            "native_bridge_device": candidate["native_bridge"]["device"],
            "native_bridge_inode": candidate["native_bridge"]["inode"],
            "public_matrix_sha256": PUBLIC_MATRIX_SHA256,
            "case_denominator": PUBLIC_CASE_COUNT,
            "baseline_records_sha256": complete["baseline_records_sha256"],
            "rust_records_sha256": complete["rust_records_sha256"],
            "baseline_pid": complete["baseline_pid"],
            "rust_pid": complete["rust_pid"],
            "correctness_status": complete["status"],
            "mismatch_count": complete["mismatch_count"],
            "all_mismatches_preserved": True,
            "report_relative": preflight["report_relative"],
            "report_sha256": hashlib.sha256(actual_report).hexdigest(),
            "report_bytes": len(actual_report),
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
        verify_retained_directory(preflight)
        receipt_publication = checker.write_approved_output(
            preflight["receipt_relative"], receipt_document,
        )
        actual_receipt = read_published_receipt(
            checker, preflight, receipt_document, receipt_publication,
        )
        return {
            "schema": SCHEMA + "-compact-result",
            "status": complete["status"],
            "label": slug,
            "practice_label": checker.PRACTICE_LABEL,
            "checker_source_sha256": CHECKER_SHA256,
            "candidate_source_sha256": candidate_pin,
            "candidate_source_bytes": candidate["source"]["bytes"],
            "candidate_source_device": candidate["source"]["device"],
            "candidate_source_inode": candidate["source"]["inode"],
            "native_engine_sha256": candidate["native_engine"]["sha256"],
            "native_engine_bytes": candidate["native_engine"]["bytes"],
            "native_engine_device": candidate["native_engine"]["device"],
            "native_engine_inode": candidate["native_engine"]["inode"],
            "native_bridge_sha256": candidate["native_bridge"]["sha256"],
            "native_bridge_bytes": candidate["native_bridge"]["bytes"],
            "native_bridge_device": candidate["native_bridge"]["device"],
            "native_bridge_inode": candidate["native_bridge"]["inode"],
            "public_matrix_sha256": PUBLIC_MATRIX_SHA256,
            "case_denominator": PUBLIC_CASE_COUNT,
            "mismatch_count": complete["mismatch_count"],
            "baseline_records_sha256": complete["baseline_records_sha256"],
            "rust_records_sha256": complete["rust_records_sha256"],
            "baseline_pid": complete["baseline_pid"],
            "rust_pid": complete["rust_pid"],
            "report_publication": report_publication,
            "receipt_publication": receipt_publication,
            "receipt_complete_readback_verified": True,
            "receipt_verified_bytes": len(actual_receipt),
            "actual_candidate_comparison_count": 1,
            "actual_clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }


def source_self_test() -> dict[str, Any]:
    checker = authenticate_frozen_checker()
    original = checker.source_self_test()
    require(type(original) is dict
            and original.get("status") == "PASS"
            and original.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and original.get("case_count") == PUBLIC_CASE_COUNT
            and original.get("baseline_records_sha256")
            == EXPECTED_BASELINE_RECORDS_SHA256
            and original.get("baseline_vs_baseline_reference_count") == 2
            and original.get("actual_candidate_workers") == 0
            and original.get("candidate_import_count") == 0
            and original.get("timing_trials_run") == 0
            and original.get("benchmark_files_read") == 0
            and original.get("hidden_cases_read") == 0
            and original.get("files_written") == 0,
            "the genuine frozen baseline-only source controls no longer pass")

    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and bool(condition) and name not in accepted,
                "a recorder source-only positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        require(type(name) is str and name not in rejected and callable(operation),
                "an actual recorder source poison was duplicated")
        try:
            operation()
        except (RecorderError, checker.PracticeBenchmarkError,
                ValueError, TypeError):
            rejected.append(name)
            return
        raise RecorderError("a recorder poison control was accepted: " + name)

    accept("authenticate-literal-pinned-checker-without-candidate",
           checker.MATRIX_SHA256 == PUBLIC_MATRIX_SHA256
           and checker.ROOT == ROOT)
    accept("preserve-all-frozen-original-public-case-identities",
           checker.validate_public_matrix(checker.build_public_matrix())
           == PUBLIC_MATRIX_SHA256)
    accept("preserve-two-actual-candidate-free-original-baselines",
           original["baseline_vs_baseline_reference_count"] == 2)
    accept("preserve-exact-frozen-864-case-baseline-vector",
           original["baseline_records_sha256"]
           == EXPECTED_BASELINE_RECORDS_SHA256)
    accept("accept-one-strict-original-public-slug",
           validate_label("rust-original-public-v1")
           == "rust-original-public-v1")
    expected_paths = (
        APPROVED_DIRECTORY + "/rust-original-public-v1.json",
        APPROVED_DIRECTORY
        + "/rust-original-public-v1-publication-receipt.json",
    )
    accept("derive-exactly-two-distinct-approved-public-paths",
           approved_relative_paths("rust-original-public-v1") == expected_paths
           and checker.approved_output_parts(expected_paths[0])[:-1]
           == checker.approved_output_parts(expected_paths[1])[:-1]
           == ("experiments", "rust_public_practice_v1"))
    accept("accept-real-independent-frozen-checker-digest",
           validate_digest(CHECKER_SHA256, label="synthetic checker control")
           == CHECKER_SHA256)

    synthetic_source_pin = "12" * 32
    synthetic_engine_pin = "34" * 32
    synthetic_bridge_pin = "56" * 32
    synthetic_source = {
        "relative": CANDIDATE_RELATIVE, "sha256": synthetic_source_pin,
        "bytes": 11, "device": 17, "inode": 101,
    }
    synthetic_engine = {
        "relative": NATIVE_ENGINE_RELATIVE, "sha256": synthetic_engine_pin,
        "bytes": 23, "device": 17, "inode": 102,
    }
    synthetic_bridge = {
        "relative": "candidates/_rust_bridge" + EXTENSION_SUFFIXES[0],
        "sha256": synthetic_bridge_pin,
        "bytes": 31, "device": 17, "inode": 103,
    }
    accept("authenticate-synthetic-exact-three-owned-rust-components",
           valid_candidate_provenance(
               synthetic_source, synthetic_engine, synthetic_bridge,
               synthetic_source_pin, synthetic_engine_pin, synthetic_bridge_pin,
           ))
    for name, kind, key, value in (
        ("shadow-adapter", "source", "relative",
         "candidates/rust_candidate/__init__.py"),
        ("changed-adapter-digest", "source", "sha256", "78" * 32),
        ("substituted-semantic-engine", "engine", "relative",
         "candidates/foreign-rust-engine.so"),
        ("changed-semantic-engine-digest", "engine", "sha256", "9a" * 32),
        ("substituted-native-bridge", "bridge", "relative",
         "candidates/foreign-bridge.so"),
        ("changed-native-bridge-digest", "bridge", "sha256", "bc" * 32),
        ("missing-semantic-engine-inode", "engine", "inode", None),
        ("missing-native-bridge-device", "bridge", "device", None),
    ):
        forged_source = dict(synthetic_source)
        forged_engine = dict(synthetic_engine)
        forged_bridge = dict(synthetic_bridge)
        target = {
            "source": forged_source,
            "engine": forged_engine,
            "bridge": forged_bridge,
        }[kind]
        target[key] = value
        reject("reject-synthetic-" + name,
               lambda forged_source=forged_source,
               forged_engine=forged_engine, forged_bridge=forged_bridge: require(
                   valid_candidate_provenance(
                       forged_source, forged_engine, forged_bridge,
                       synthetic_source_pin, synthetic_engine_pin,
                       synthetic_bridge_pin,
                   ), "a forged three-component Rust provenance was rejected",
               ))

    for index, slug in enumerate((
        "", ".", "..", "../escape", "/tmp/escape", "UPPER",
        "has space", "has_underscore", "two--hyphens", "-leading",
        "trailing-", "line\nbreak", "slash/component",
        "back\\slash", "\x00", "a" * 65,
    )):
        reject("reject-escaping-or-ambiguous-slug-" + format(index, "02d"),
               lambda slug=slug: validate_label(slug))
    for index, invalid in enumerate((
        None, 0, True, "", "0" * 64, "A" * 64,
        "g" * 64, "ab" * 31, "ab" * 33,
        CHECKER_SHA256.upper(), CHECKER_SHA256 + "0",
    )):
        reject("reject-nonactual-frozen-digest-" + format(index, "02d"),
               lambda invalid=invalid: validate_digest(
                   invalid, label="synthetic digest poison",
               ))
    for index, invalid in enumerate((
        "", "/tmp/foreign.json", "../foreign.json", "a/../foreign.json",
        "experiments//foreign.json", "experiments/./foreign.json",
        "experiments\\foreign.json", "nul\x00foreign.json",
    )):
        reject("reject-escaping-owned-source-components-"
               + format(index, "02d"),
               lambda invalid=invalid: _safe_relative_parts(invalid))
    for index, invalid in enumerate((
        "/tmp/foreign.json", "../foreign.json",
        "experiments/foreign.json",
        "experiments/rust_public_practice_v1/../foreign.json",
        "experiments/rust_public_practice_v1/foreign.txt",
    )):
        reject("reject-unapproved-frozen-checker-output-"
               + format(index, "02d"),
               lambda invalid=invalid: checker.approved_output_parts(invalid))
    verify_runtime()
    accept("load-no-candidate-no-clock-no-evidence",
           not any(name == "candidates" or name.startswith("candidates.")
                   for name in sys.modules)
           and original["actual_candidate_workers"] == 0
           and original["timing_trials_run"] == 0
           and original["files_written"] == 0)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "practice_label": checker.PRACTICE_LABEL,
        "python": "3.14.6",
        "checker_source_sha256": CHECKER_SHA256,
        "public_matrix_sha256": PUBLIC_MATRIX_SHA256,
        "case_denominator": PUBLIC_CASE_COUNT,
        "baseline_records_sha256": EXPECTED_BASELINE_RECORDS_SHA256,
        "actual_independent_baseline_workers": 2,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Preserve one entire frozen public Rust correctness comparison; "
            "never a hidden, timed, or final result"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record", action="store_true")
    parser.add_argument("--label")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(options.label is None and options.candidate_source_sha256 is None
                and options.native_engine_sha256 is None
                and options.native_bridge_sha256 is None,
                "a recorder source test cannot name, pin, or import a candidate")
        document = source_self_test()
    else:
        require(options.label is not None
                and options.candidate_source_sha256 is not None
                and options.native_engine_sha256 is not None
                and options.native_bridge_sha256 is not None,
                "actual recording requires a strict slug and all three frozen "
                "Rust adapter, semantic-engine, and native-bridge digests")
        document = record_correctness(
            options.label, options.candidate_source_sha256,
            options.native_engine_sha256, options.native_bridge_sha256,
        )
    checker = sys.modules.get(CHECKER_MODULE)
    require(checker is not None,
            "the exact frozen checker must supply complete canonical output")
    sys.stdout.buffer.write(checker.canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecorderError as error:
        print("frozen public correctness recording failed closed: " + str(error),
              file=sys.stderr)
        raise SystemExit(1) from error
