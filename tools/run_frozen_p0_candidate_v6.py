#!/usr/bin/env python3
"""Publish the complete, failure-aware frozen Python-regex candidate result."""

from __future__ import annotations

import argparse
import builtins
import contextlib
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from typing import Any, Callable, Iterator, Mapping, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_v6.py"
WORKER_RELATIVE = "tools/run_frozen_p0_candidate_worker_v4.py"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v6.json"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V6.md"
SCHEMA = "rebar-frozen-python-re-p0-candidate-v6"
WORKER_SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v4"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
NESTED_V3_SHA256 = "21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4"
NESTED_V3_DOCUMENT_SHA256 = "17dac72e6a0ae75bf1f013656b9779a1e948e71439cf336499c1e680beb19284"
NESTED_V3_PROTOCOL_SHA256 = "97354130b4d1ab97ee2c684b43b72e29a0a68439c2a1ead5a4f45edc20e6c9b4"
SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
FAMILIES = ("rust", "c", "zig")
BUILD_VERSIONS = {"rust": "2", "c": "2", "zig": "3"}


class AggregateGateError(Exception):
    """The original complete independently observed candidate did not qualify."""


class SourceOnlyEffect(AggregateGateError):
    """A purely synthetic aggregate control attempted a real external effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise AggregateGateError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")).encode("ascii")
                + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise AggregateGateError("require exact finite canonical evidence") from error


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require an exact lowercase independently pinned SHA-256: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only the exact isolated pinned Python and genuine V6 source")


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    counters = {field: 0 for field in (
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "source_builds", "native_promotions",
        "native_libraries_loaded", "interpreter_creations", "thread_starts",
        "network_requests", "clock_samples", "hidden_cases_read",
        "benchmark_files_read", "blocked_reads", "blocked_writes",
        "blocked_processes", "blocked_imports", "blocked_threads",
        "blocked_clocks", "blocked_promotions", "blocked_network",
    )}
    previous: list[tuple[Any, str, Any]] = []

    def reject(field: str, name: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            counters[field] += 1
            raise SourceOnlyEffect("the synthetic aggregate forbids " + name)
        return blocked

    def install(owner: Any, name: str, field: str) -> None:
        if hasattr(owner, name):
            previous.append((owner, name, getattr(owner, name)))
            setattr(owner, name, reject(field, name))

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "mkdir"),
            (os, "makedirs"), (os, "rename"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"), (Path, "touch"),
            (Path, "mkdir"), (Path, "unlink"),
            (tempfile, "mkstemp"), (tempfile, "mkdtemp"),
        ):
            install(owner, name, "blocked_writes")
        install(os, "replace", "blocked_promotions")
        install(importlib, "import_module", "blocked_imports")
        install(subprocess, "Popen", "blocked_processes")
        install(subprocess, "run", "blocked_processes")
        install(threading.Thread, "start", "blocked_threads")
        install(socket, "create_connection", "blocked_network")
        install(socket.socket, "connect", "blocked_network")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns"):
            install(time, name, "blocked_clocks")
        yield counters
    finally:
        for owner, name, original in reversed(previous):
            setattr(owner, name, original)


def synthetic_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-synthetic-frozen-contract",
        "phase": "CANDIDATES",
        "goal_sha256": GOAL_SHA256,
        "phase1_sha256": PHASE1_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "candidate_families": list(FAMILIES),
        "build_versions": dict(BUILD_VERSIONS),
        "nested_v3_source_sha256": NESTED_V3_SHA256,
        "nested_v3_protocol_sha256": NESTED_V3_DOCUMENT_SHA256,
        "nested_v3_explanation_sha256": NESTED_V3_PROTOCOL_SHA256,
        "historical_actual_qualified_cases": {"c": 7197, "rust": 7461},
        "historical_actual_mismatches": {"c": 2094, "rust": 2042},
        "historical_original_interpreter_calls":
        {"c": 0, "rust": "NOT ESTABLISHED"},
        "historical_report_count": 32,
        "historical_restoration_receipt_count": 2,
        "source_specific_record_digests_required": True,
        "failed_publication_is_success": False,
        "fresh_reference_workers_allowed": False,
        "candidate_external_engine_allowed": False,
        "candidate_cross_family_engine_allowed": False,
        "fallback_allowed": False,
        "supplemental_cases_added_to_denominator": False,
        "maximum_aggregate_report_bytes": MAX_REPORT_BYTES,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "holdout_opened": False,
        "winner_selected": False,
    }


def validate_synthetic_contract(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(synthetic_contract()),
            "reject any changed complete source-only aggregate invariant")
    return value


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, operation: Callable[[], Any]) -> Any:
        try:
            result = operation()
        except Exception as error:
            raise AggregateGateError("a genuine positive control failed: " + name) from error
        accepted.append(name)
        return result

    def reject(name: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (AggregateGateError, SourceOnlyEffect, TypeError, ValueError,
                KeyError, UnicodeError, RecursionError, OverflowError):
            rejected.append(name)
            return
        raise AggregateGateError("a hostile source-only control escaped: " + name)

    with source_only_boundary() as effects:
        contract = accept("retain-complete-source-frozen-version-six-contract",
                          lambda: validate_synthetic_contract(synthetic_contract()))
        accept("retain-thirteen-original-source-owned-suites",
               lambda: require(contract["suite_count"] == 13,
                               "all thirteen original suites are mandatory"))
        accept("retain-31237-runnable-original-cases",
               lambda: require(contract["case_execution_denominator"] == 31237,
                               "never change the original runnable denominator"))
        accept("retain-c-rust-and-zig-independent-families",
               lambda: require(set(contract["candidate_families"])
                               == {"c", "rust", "zig"},
                               "require all actual independent native families"))
        for field in contract:
            def mutate(field: str = field) -> Any:
                forged = synthetic_contract()
                original = forged[field]
                if type(original) is bool:
                    forged[field] = not original
                elif type(original) is int:
                    forged[field] = original + 1
                elif type(original) is dict:
                    forged[field] = {**original, "forged": True}
                elif type(original) is list:
                    forged[field] = original[:-1]
                else:
                    forged[field] = str(original) + "-forged"
                return validate_synthetic_contract(forged)
            reject("reject-changed-source-only-" + field, mutate)
        for family in FAMILIES:
            accept("retain-exact-source-build-version-" + family,
                   lambda family=family: require(
                       BUILD_VERSIONS[family]
                       == ("3" if family == "zig" else "2"),
                       "reject a cross-version source-built native family"))
        for name, operation in (
            ("file-read", lambda: builtins.open("GOAL.md", "rb")),
            ("descriptor-read", lambda: os.open("GOAL.md", os.O_RDONLY)),
            ("actual-candidate-process", lambda: subprocess.Popen([PINNED_PYTHON])),
            ("candidate-import", lambda: importlib.import_module("candidates")),
            ("actual-clock", lambda: time.perf_counter()),
            ("native-promotion", lambda: os.replace("synthetic-a", "synthetic-b")),
            ("network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("temporary-file", lambda: tempfile.mkstemp()),
        ):
            reject("reject-real-source-only-" + name, operation)
        reject("reject-integer-for-strict-frozen-true",
               lambda: require(1, "never confuse an integer with literal true"))
    for field in (
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "source_builds", "native_promotions",
        "native_libraries_loaded", "interpreter_creations", "thread_starts",
        "network_requests", "clock_samples", "hidden_cases_read",
        "benchmark_files_read",
    ):
        require(effects[field] == 0,
                "a synthetic V6 check produced a genuine effect: " + field)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "synthetic": True,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted": accepted,
        "rejected": rejected,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "preserved_historical_artifact_count": 32,
        "preserved_historical_restoration_receipt_count": 2,
        "source_only_effects": effects,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_promotions": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def read_exact_owned(relative: str, expected: str,
                     *, maximum: int = MAX_SOURCE_BYTES) -> dict[str, Any]:
    checked_digest(expected, relative)
    permitted = {SOURCE_RELATIVE, WORKER_RELATIVE,
                 DOCUMENT_RELATIVE, PROTOCOL_RELATIVE}
    require(type(relative) is str and relative in permitted
            and type(maximum) is int and 0 < maximum <= MAX_SOURCE_BYTES,
            "read only independently predetermined exact V6 frozen source owners")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    handles: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags)
        handles.append(current)
        parts = relative.split("/")
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            handles.append(current)
        descriptor = os.open(parts[-1], flags, dir_fd=current)
        handles.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum,
                "reject a replaced, copied, oversized, or symlinked V6 owner")
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "reject a truncated complete V6 owner")
            remaining -= len(block)
            hasher.update(block)
        require(os.read(descriptor, 1) == b"",
                "reject an extra frozen V6 owner suffix")
        after = os.fstat(descriptor)
        final = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                and hasher.hexdigest() == expected,
                "bind each exact V6 source to its unchanged authentic inode")
        return {"relative": relative, "path": str(ROOT / relative),
                "sha256": expected, "size_bytes": after.st_size,
                "device": after.st_dev, "inode": after.st_ino}
    finally:
        for descriptor in reversed(handles):
            os.close(descriptor)


def load_frozen_worker(options: argparse.Namespace) -> Any:
    verify_runtime()
    pins = (
        (SOURCE_RELATIVE, options.source_sha256),
        (WORKER_RELATIVE, options.worker_source_sha256),
        (DOCUMENT_RELATIVE, options.document_sha256),
        (PROTOCOL_RELATIVE, options.protocol_sha256),
    )
    owners = {relative: read_exact_owned(relative, fingerprint)
              for relative, fingerprint in pins}
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    worker = importlib.import_module("tools.run_frozen_p0_candidate_worker_v4")
    require(getattr(worker, "SCHEMA", None) == WORKER_SCHEMA
            and os.path.abspath(str(worker.__file__)) == str(ROOT / WORKER_RELATIVE)
            and getattr(worker, "CASE_DENOMINATOR", None) == CASE_DENOMINATOR
            and getattr(worker, "SUITE_COUNT", None) == SUITE_COUNT,
            "load only the genuine separately authenticated complete V4 case worker")
    for relative, fingerprint in pins:
        read_exact_owned(relative, fingerprint)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "loading a frozen correctness validator cannot import a candidate")
    return worker, owners


def context_worker_options(options: argparse.Namespace,
                           worker: Any) -> argparse.Namespace:
    return worker.parse_arguments([
        "--verify-frozen-context",
        "--source-sha256", options.worker_source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--document-sha256", options.document_sha256,
    ])


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    require(options.candidate is None and options.label is None
            and options.build_version is None and options.build_label is None
            and options.activation_root is None
            and not options.owned_source_sha256,
            "a read-only V6 context cannot authorize any native candidate")
    worker, owners = load_frozen_worker(options)
    observed = worker.verify_frozen_context(
        context_worker_options(options, worker),
    )
    require(type(observed) is dict and observed.get("status") == "PASS"
            and observed.get("actual_candidate_workers") == 0
            and observed.get("actual_reference_workers") == 0
            and observed.get("actual_candidate_imports") == 0
            and observed.get("case_execution_denominator") == CASE_DENOMINATOR
            and observed.get("suite_count") == SUITE_COUNT
            and observed.get("preserved_historical_artifact_count") == 32
            and observed.get("preserved_historical_restoration_receipt_count") == 2
            and observed.get("clock_samples") == 0
            and observed.get("benchmark_files_read") == 0
            and observed.get("hidden_cases_read") == 0
            and observed.get("performance") == "NOT MEASURED",
            "independently verify the entire read-only source-owned P0 context")
    histories = observed["preserved_actual_campaigns"]
    require(histories["c"]["qualified_case_count"] == 7197
            and histories["c"]["actual_semantic_mismatch_count"] == 2094
            and histories["c"]["actual_case_interpreter_exec_calls"] == 0
            and histories["rust"]["qualified_case_count"] == 7461
            and histories["rust"]["actual_semantic_mismatch_count"] == 2042
            and histories["rust"]["actual_case_interpreter_exec_calls"]
            == "NOT ESTABLISHED",
            "preserve actual historical candidate failures without upgrading them")
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "read_only": True,
        "frozen_v6_source_owners": owners,
        "full_case_worker_verification": observed,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "preserved_historical_artifact_count": 32,
        "preserved_historical_restoration_receipt_count": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_promotions": 0,
        "actual_interpreters_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def actual_worker_arguments(options: argparse.Namespace) -> list[str]:
    names: tuple[tuple[str, Any], ...] = (
        ("--candidate", options.candidate),
        ("--label", options.label),
        ("--build-version", options.build_version),
        ("--build-label", options.build_label),
        ("--source-sha256", options.worker_source_sha256),
        ("--protocol-sha256", options.protocol_sha256),
        ("--document-sha256", options.document_sha256),
        ("--subinterpreter-source-sha256", NESTED_V3_SHA256),
        ("--subinterpreter-protocol-sha256", NESTED_V3_DOCUMENT_SHA256),
        ("--subinterpreter-explanation-sha256", NESTED_V3_PROTOCOL_SHA256),
        ("--build-source-sha256", options.build_source_sha256),
        ("--build-protocol-sha256", options.build_protocol_sha256),
        ("--build-archive-sha256", options.build_archive_sha256),
        ("--build-receipt-sha256", options.build_receipt_sha256),
        ("--activation-root", options.activation_root),
        ("--activation-source-sha256", options.activation_source_sha256),
        ("--activation-protocol-sha256", options.activation_protocol_sha256),
        ("--activation-report-sha256", options.activation_report_sha256),
        ("--activation-receipt-sha256", options.activation_receipt_sha256),
        ("--candidate-source-sha256", options.candidate_source_sha256),
        ("--native-engine-sha256", options.native_engine_sha256),
        ("--native-bridge-sha256", options.native_bridge_sha256),
    )
    result = ["--run"]
    for flag, value in names:
        require(type(value) is str and bool(value),
                "pin every actual candidate, corrected native build, and worker owner")
        result.extend((flag, value))
    if options.recovery_journal_sha256 is not None:
        result.extend(("--recovery-journal-sha256", options.recovery_journal_sha256))
    for entry in options.owned_source_sha256:
        result.extend(("--owned-source-sha256", entry))
    return result


def ensure_fresh_aggregate(worker: Any, family: str, label: str) -> None:
    for failed in (False, True):
        stem = ("oracle/phase2/evidence/frozen-p0-candidate-v6-"
                + family + "-" + label + ("-failures" if failed else ""))
        for relative in (stem + ".json.gz", stem + "-publication-receipt.json"):
            try:
                os.lstat(str(ROOT / relative))
            except FileNotFoundError:
                continue
            raise AggregateGateError(
                "refuse to overwrite complete existing V6 candidate evidence: "
                + relative
            )
    worker.ensure_fresh_run_evidence(family, label)


def authenticate_actual_worker_result(
    value: Any, process: Mapping[str, Any], options: argparse.Namespace,
    worker: Any, context: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(type(value) is dict
            and value.get("schema")
            == WORKER_SCHEMA + "-published-complete-candidate"
            and value.get("status") in {"PASS", "FAIL"}
            and value.get("candidate_family") == options.candidate
            and value.get("label") == options.label
            and value.get("suite_count") == SUITE_COUNT
            and value.get("case_execution_denominator") == CASE_DENOMINATOR
            and process.get("returncode")
            == (0 if value["status"] == "PASS" else 1),
            "authenticate genuine complete worker output before applying its status")
    archive_path, receipt_path = worker.planned_worker_paths(
        options.candidate, options.label,
        failure=value["status"] == "FAIL",
    )
    allowed = frozenset({*context["allowed_paths"], archive_path, receipt_path})
    compressed, archive_owner = worker.source_owned_publication(
        value.get("complete_archive"), archive_path,
        compressed=True, allowed=allowed,
    )
    receipt_raw, receipt_owner = worker.source_owned_publication(
        value.get("complete_publication_receipt"), receipt_path,
        compressed=False, allowed=allowed,
    )
    plain = worker.bounded_gzip(compressed, "full original V4 worker report",
                                maximum=MAX_REPORT_BYTES)
    report = worker.decode_document(plain, "complete actual original V4 worker",
                                    maximum=MAX_REPORT_BYTES)
    receipt = worker.decode_document(receipt_raw, "actual full V4 worker receipt",
                                     canonical_required=True)
    suites = report.get("all_suites")
    require(report.get("schema") == WORKER_SCHEMA + "-complete-candidate-evaluation"
            and report.get("status") == value["status"]
            and report.get("candidate_family") == options.candidate
            and report.get("label") == options.label
            and report.get("source_sha256") == options.worker_source_sha256
            and report.get("protocol_sha256") == options.protocol_sha256
            and report.get("document_sha256") == options.document_sha256
            and report.get("build_version") == options.build_version
            and report.get("suite_count") == SUITE_COUNT
            and report.get("case_execution_denominator") == CASE_DENOMINATOR
            and type(suites) is list and len(suites) == SUITE_COUNT
            and [item.get("suite") for item in suites]
            == [suite.name for suite in worker.FROZEN_SUITES]
            and receipt.get("schema") == WORKER_SCHEMA + "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == report["status"]
            and receipt.get("candidate_family") == options.candidate
            and receipt.get("label") == options.label
            and receipt.get("uncompressed_bytes") == len(plain)
            and receipt.get("uncompressed_sha256")
            == hashlib.sha256(plain).hexdigest()
            and receipt.get("archive") == value["complete_archive"],
            "authenticate every complete source-owned worker suite and receipt")
    passed = [row for row in suites if row.get("status") == "PASS"]
    qualified = sum(row["actual_candidate_case_count"] for row in passed)
    mismatches = sum(row.get("mismatch_count", 0) for row in suites)
    require(report.get("completed_candidate_suite_count") == len(passed)
            and report.get("qualified_candidate_case_executions") == qualified
            and report.get("actual_semantic_mismatch_count") == mismatches
            and value.get("completed_candidate_suite_count") == len(passed)
            and value.get("qualified_candidate_case_executions") == qualified
            and report.get("candidate_qualified")
            is (len(passed) == SUITE_COUNT and qualified == CASE_DENOMINATOR)
            and value.get("candidate_qualified") == report["candidate_qualified"]
            and (report["status"] == "PASS") is report["candidate_qualified"],
            "never change passing case denominators or promote a partial candidate")
    history = report.get("preserved_actual_v5_campaigns")
    require(type(history) is dict and set(history) == {"c", "rust"}
            and history["c"]["qualified_case_count"] == 7197
            and history["c"]["actual_semantic_mismatch_count"] == 2094
            and history["rust"]["qualified_case_count"] == 7461
            and history["rust"]["actual_semantic_mismatch_count"] == 2042,
            "retain both independently reconstructed genuine historical campaigns")
    return report, archive_owner, receipt_owner


def run_actual_candidate(options: argparse.Namespace) -> dict[str, Any]:
    worker, owners = load_frozen_worker(options)
    worker_args = worker.parse_arguments(actual_worker_arguments(options))
    context = worker.authenticate_frozen_context(worker_args)
    approval = worker.authenticate_canonical_activation(worker_args, context)
    require(approval.get("family") == options.candidate
            and approval.get("build_version") == options.build_version,
            "use only the independently proved genuine native candidate")
    ensure_fresh_aggregate(worker, options.candidate, options.label)
    report: dict[str, Any] = {
        "schema": SCHEMA + "-actual-complete-candidate",
        "status": "FAIL",
        "candidate_family": options.candidate,
        "label": options.label,
        "source_sha256": options.source_sha256,
        "worker_source_sha256": options.worker_source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "document_sha256": options.document_sha256,
        "build_version": options.build_version,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "attempted_candidate_suite_count": 0,
        "completed_candidate_suite_count": 0,
        "qualified_candidate_case_executions": 0,
        "actual_semantic_mismatch_count": 0,
        "candidate_qualified": False,
        "all_suites": [],
        "worker_process": None,
        "worker_complete_archive": None,
        "worker_complete_publication_receipt": None,
        "failure": None,
        "frozen_v6_source_owners": owners,
        "corrected_canonical_activation": approval["canonical_activation"],
        "corrected_source_build": approval["source_build"],
        "preserved_actual_v5_campaigns": context["preserved_v5_campaigns"],
        "preserved_historical_artifact_count": 32,
        "preserved_historical_restoration_receipt_count": 2,
        "supplemental_cases_added_to_phase1_denominator": False,
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    try:
        command = [PINNED_PYTHON, "-I", "-B", str(ROOT / WORKER_RELATIVE),
                   *actual_worker_arguments(options)]
        process = worker.encoded_process(command)
        report["worker_process"] = process
        require(process.get("timed_out") is False
                and process.get("returncode") in {0, 1},
                "preserve an actual failed, timed-out, or signalled whole worker")
        stderr = worker.restore_stream(process.get("stderr"),
                                       "complete whole-case-worker stderr")
        require(stderr == b"", "never conceal a complete correctness-worker error")
        actual = worker.decode_document(
            worker.restore_stream(process.get("stdout"),
                                  "complete whole-case-worker stdout"),
            "actual published V4 whole-candidate result",
        )
        proved, archive, receipt = authenticate_actual_worker_result(
            actual, process, options, worker, context,
        )
        report.update({
            "status": proved["status"],
            "attempted_candidate_suite_count":
            proved["attempted_candidate_suite_count"],
            "completed_candidate_suite_count":
            proved["completed_candidate_suite_count"],
            "qualified_candidate_case_executions":
            proved["qualified_candidate_case_executions"],
            "actual_semantic_mismatch_count":
            proved["actual_semantic_mismatch_count"],
            "candidate_qualified": proved["candidate_qualified"],
            "all_suites": proved["all_suites"],
            "worker_complete_archive": archive,
            "worker_complete_publication_receipt": receipt,
            "failure": None if proved["status"] == "PASS" else {
                "type": "ActualCandidateMismatch",
                "message": "one or more original Python regex cases actually failed",
                "failed_suite_count":
                SUITE_COUNT - proved["completed_candidate_suite_count"],
                "actual_semantic_mismatch_count":
                proved["actual_semantic_mismatch_count"],
                "all_failure_reasons": proved["all_failure_reasons"],
            },
        })
    except Exception as error:
        report["failure"] = {
            "type": type(error).__qualname__,
            "message": str(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__,
            ),
        }
    return worker.publish_actual_report(
        report, options,
        prefix="frozen-p0-candidate-v6-", schema=SCHEMA,
    )


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record all complete frozen Python regex candidate results.",
        allow_abbrev=False,
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=FAMILIES)
    parser.add_argument("--label")
    parser.add_argument("--build-version", choices=("2", "3"))
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    for name in (
        "source", "worker-source", "protocol", "document", "build-source",
        "build-protocol", "build-archive", "build-receipt", "activation-source",
        "activation-protocol", "activation-report", "activation-receipt",
        "recovery-journal", "candidate-source", "native-engine", "native-bridge",
    ):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(not any(getattr(options, name) is not None for name in (
            "candidate", "label", "build_version", "build_label",
            "activation_root", "source_sha256", "worker_source_sha256",
            "protocol_sha256", "document_sha256",
        )) and not options.owned_source_sha256,
                "a synthetic source test cannot authorize real candidates")
        return options
    frozen = ("source_sha256", "worker_source_sha256", "protocol_sha256",
              "document_sha256")
    require(all(getattr(options, name) is not None for name in frozen),
            "independently pin all four separately committed V6 source owners")
    for name in (
        *frozen, "build_source_sha256", "build_protocol_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "activation_source_sha256", "activation_protocol_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256", "candidate_source_sha256",
        "native_engine_sha256", "native_bridge_sha256",
    ):
        if getattr(options, name) is not None:
            checked_digest(getattr(options, name), name)
    if options.verify_frozen_context:
        return options
    required = (
        "candidate", "label", "build_version", "build_label", "activation_root",
        "build_source_sha256", "build_protocol_sha256", "build_archive_sha256",
        "build_receipt_sha256", "activation_source_sha256",
        "activation_protocol_sha256", "activation_report_sha256",
        "activation_receipt_sha256", "candidate_source_sha256",
        "native_engine_sha256", "native_bridge_sha256",
    )
    require(all(getattr(options, name) is not None for name in required)
            and bool(options.owned_source_sha256),
            "explicitly authorize all genuine native-build and owner proofs")
    require(BUILD_VERSIONS[options.candidate] == options.build_version,
            "use genuine Zig source-build V3 or C/Rust source-build V2")
    for entry in options.owned_source_sha256:
        require(type(entry) is str and entry.count("=") == 1,
                "authenticate every independent candidate source owner")
        relative, fingerprint = entry.split("=", 1)
        require(bool(relative), "preserve each real source-owned family path")
        checked_digest(fingerprint, relative)
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
        if options.self_test:
            result = source_self_test()
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            result = run_actual_candidate(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except Exception as error:
        result = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__qualname__, "error_message": str(error),
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
