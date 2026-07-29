#!/usr/bin/env python3
"""Freeze a separate, first-party Zig controller for the original Python ``re`` tests.

No candidate can run until a separately frozen, independently verified live Zig
activation exists. Source-only gates authenticate current V45 history, final
Rust V7, genuine historical Rust V6 failure effects, the original V4 producer,
the failing expanded public-entrypoint oracle, and the dedicated Zig worker.
They never open archives or the holdout, execute a compiler, or load native code.
"""

from __future__ import annotations

import _ctypes
import _imp
import _io
import _posixsubprocess
import _socket
import _thread
import argparse
import ast
import base64
import builtins
import contextlib
import copy
import ctypes
import gzip
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
import types
import zlib
from typing import Any, Iterator, NamedTuple, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_zig_original_p0_candidate_v1.py"
WORKER_RELATIVE = "tools/run_frozen_zig_original_p0_candidate_worker_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/ZIG-ORIGINAL-P0-CANDIDATE-PROTOCOL-V1.md"
DOCUMENT_RELATIVE = "oracle/phase2/zig-original-p0-candidate-protocol-v1.json"
SCHEMA = "rebar-frozen-zig-original-p0-candidate-v1"
WORKER_SCHEMA = "rebar-frozen-zig-original-p0-candidate-worker-v1"
CONTRACT_SCHEMA = "rebar-frozen-zig-original-p0-candidate-protocol-v1"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
FAMILY = "zig"
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1_024),
    ("buffer_v3", 768),
    ("managed_v1", 1_024),
    ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912),
    ("substitution_v2", 5_120),
    ("shape_v2", 10_240),
    ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
PRIVATE_WAIVER_COUNT = 13
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PUBLIC_REPORT_BYTES = 32 * 1024 * 1024
MAX_CHILD_STDOUT_BYTES = 1024 * 1024
MAX_CHILD_STDERR_BYTES = 2 * 1024 * 1024
MAX_ERROR_BYTES = 64 * 1024
WORKER_TIMEOUT_SECONDS = 3_600
V4_SOURCE_SHA256 = (
    "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8"
)
V4_PROTOCOL_SHA256 = (
    "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5"
)
V4_DOCUMENT_SHA256 = (
    "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5"
)
CORRECTED_PUBLIC_RECORDS_SHA256 = (
    "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
)
CORRECTED_PUBLIC_COHORT_RECORDS_SHA256 = (
    "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
)
CORRECTED_PUBLIC_REFERENCE_PIDS = (81, 82)
CURRENT_V45_SUMMARY_SHA256 = (
    "1086a7bd72116b590d00f5216835534ec745265a0f249d3cd5eb05a3701ff840"
)
CURRENT_V45_SUMMARY_BYTES = 1_013_003
CURRENT_RUST_V7_SOURCE_SHA256 = (
    "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104"
)
CURRENT_PUBLIC_MATRIX_SHA256 = (
    "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
)
CURRENT_EVIDENCE_OWNER_LOWER_BOUND = 166
CURRENT_AUTHENTICATED_REFERENCE_LOWER_BOUND = 171


class Owner(NamedTuple):
    path: str
    sha256: str
    size_bytes: int


class AggregateGateError(Exception):
    """Reject partial evidence, invented workers, or premature Zig matching."""


class SourceOnlyEffect(AggregateGateError):
    """A source-only gate attempted a physically prohibited effect."""


class WorkerProcessFailure(AggregateGateError):
    """Keep the actual started child and complete streams after failure."""

    def __init__(self, message: str, process: dict[str, Any]) -> None:
        super().__init__(message)
        self.process = copy.deepcopy(process)


def require(value: Any, message: str) -> None:
    if value is not True:
        raise AggregateGateError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash only exact complete byte streams")
    return hashlib.sha256(value).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require an exact independent SHA-256 for " + label,
    )
    return value


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise AggregateGateError("reject invalid or noncanonical controller evidence") from error


def bounded_error(error: BaseException) -> str:
    raw = str(error).encode("utf-8", "backslashreplace")
    if len(raw) > MAX_ERROR_BYTES:
        raw = raw[:MAX_ERROR_BYTES] + b" [error summary truncated]"
    return raw.decode("utf-8", "replace")


def bounded_public_report(value: Any, maximum: int = MAX_PUBLIC_REPORT_BYTES) -> bytes:
    require(type(maximum) is int and maximum > 0, "require a positive public-report bound")
    raw = canonical(value)
    require(len(raw) <= maximum, "never truncate an oversized candidate report")
    return raw


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and "\\" not in value and "\x00" not in value,
            "require a safe relative frozen source owner")
    parts = value.split("/")
    require(all(part not in ("", ".", "..") for part in parts),
            "reject absolute, traversing, or ambiguous source-owner paths")
    lowered = value.casefold()
    require(
        not lowered.endswith((".gz", ".xz", ".bz2", ".zip", ".tar", ".so"))
        and "holdout" not in lowered
        and not lowered.startswith(("performance/", "benchmarks/", "benchmark/")),
        "never authenticate archives, native libraries, holdouts, or benchmarks as source files",
    )
    return value


def read_owner(owner: Owner) -> tuple[bytes, dict[str, Any]]:
    require(type(owner) is Owner, "require a genuine controller source-owner tuple")
    relative = checked_relative(owner.path)
    checked_digest(owner.sha256, relative)
    require(type(owner.size_bytes) is int and 0 < owner.size_bytes <= MAX_SOURCE_BYTES,
            "require an exact bounded frozen controller owner size")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    descriptors: list[int] = []
    try:
        directory = os.open(str(ROOT), directory_flags)
        descriptors.append(directory)
        pieces = relative.split("/")
        for piece in pieces[:-1]:
            directory = os.open(piece, directory_flags, dir_fd=directory)
            descriptors.append(directory)
        descriptor = os.open(pieces[-1], flags, dir_fd=directory)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(pieces[-1], dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and (before.st_dev, before.st_ino, before.st_size)
            == (visible.st_dev, visible.st_ino, visible.st_size)
            and before.st_size == owner.size_bytes,
            "reject a missing, linked, resized, or substituted source owner: " + relative,
        )
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk), "reject truncated source: " + relative)
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "reject hidden source bytes: " + relative)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and digest(raw) == owner.sha256,
            "reject an owner changed during complete controller verification: " + relative,
        )
        return raw, {
            "path": owner.path,
            "sha256": owner.sha256,
            "bytes": owner.size_bytes,
        }
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "run only the exact dedicated Zig controller in isolated pinned CPython 3.14.6",
    )


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = dict.fromkeys((
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "source_builds", "native_activations",
        "native_libraries_loaded", "threads_started", "network_requests",
        "clock_samples", "hidden_cases_read", "benchmark_files_read",
        "blocked_reads", "blocked_writes", "blocked_processes",
        "blocked_imports", "blocked_low_level_imports", "blocked_native_loads",
        "blocked_decompression", "blocked_threads", "blocked_network",
        "blocked_clocks",
    ), 0)
    originals: list[tuple[Any, str, Any]] = []

    def block(owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def forbidden(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyEffect("the source-only Zig V1 controller forbids " + name)

        originals.append((owner, name, previous))
        setattr(owner, name, forbidden)

    try:
        for owner, name in (
            (builtins, "open"), (_io, "open"), (io, "open"),
            (os, "open"), (os, "read"), (os, "stat"), (os, "lstat"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
        ):
            block(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "mkdir"), (os, "makedirs"), (os, "replace"),
            (os, "rename"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "touch"), (Path, "unlink"), (Path, "mkdir"),
            (tempfile, "mkstemp"), (tempfile, "mkdtemp"),
        ):
            block(owner, name, "blocked_writes")
        block(importlib, "import_module", "blocked_imports")
        for name in ("create_dynamic", "exec_dynamic", "create_builtin"):
            block(_imp, name, "blocked_low_level_imports")
        for owner, name in (
            (_ctypes, "dlopen"), (ctypes, "CDLL"), (ctypes, "PyDLL"),
        ):
            block(owner, name, "blocked_native_loads")
        for owner, name in (
            (gzip, "GzipFile"), (gzip, "decompress"),
            (zlib, "decompress"), (zlib, "decompressobj"),
        ):
            block(owner, name, "blocked_decompression")
        for owner, name in (
            (subprocess, "Popen"), (subprocess, "run"),
            (_posixsubprocess, "fork_exec"), (os, "fork"), (os, "system"),
            (os, "execv"), (os, "execve"), (os, "posix_spawn"),
        ):
            block(owner, name, "blocked_processes")
        block(_thread, "start_new_thread", "blocked_threads")
        block(threading.Thread, "start", "blocked_threads")
        for owner, name in (
            (socket, "create_connection"), (socket.socket, "connect"),
            (_socket, "socket"),
        ):
            block(owner, name, "blocked_network")
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns", "thread_time", "thread_time_ns", "sleep",
        ):
            block(time, name, "blocked_clocks")
        yield effects
    finally:
        for owner, name, previous in reversed(originals):
            setattr(owner, name, previous)


def synthetic_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-synthetic-source-control",
        "family": FAMILY,
        "worker_schema": WORKER_SCHEMA,
        "contract_schema": CONTRACT_SCHEMA + "-source-freeze",
        "suite_count": SUITE_COUNT,
        "suites": [{"id": name, "case_execution_count": count} for name, count in SUITES],
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "current_overview_version": 45,
        "current_overview_summary_sha256": CURRENT_V45_SUMMARY_SHA256,
        "current_overview_summary_bytes": CURRENT_V45_SUMMARY_BYTES,
        "current_evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "current_authenticated_reference_lower_bound":
            CURRENT_AUTHENTICATED_REFERENCE_LOWER_BOUND,
        "publication_safe_rust_v7_source_sha256": CURRENT_RUST_V7_SOURCE_SHA256,
        "publication_safe_rust_v7_matching": "NOT RUN",
        "actual_rust_v6_preflight": "FAIL",
        "actual_rust_v6_historical_build_archive_read_count": 1,
        "actual_rust_v6_historical_build_archive_inflation_count": 1,
        "actual_rust_v6_candidate_workers": 0,
        "public_entrypoint_matrix_case_count": 32,
        "public_entrypoint_matrix_sha256": CURRENT_PUBLIC_MATRIX_SHA256,
        "public_entrypoint_status": "FAIL",
        "public_entrypoint_case_status_counts": {
            "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
            "NOT ESTABLISHED": 1, "NOT OPENED": 1,
        },
        "original_producer_source_sha256": V4_SOURCE_SHA256,
        "original_producer_protocol_sha256": V4_PROTOCOL_SHA256,
        "original_producer_contract_sha256": V4_DOCUMENT_SHA256,
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "corrected_public_cache_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "corrected_public_reference_process_ids":
            list(CORRECTED_PUBLIC_REFERENCE_PIDS),
        "reference_case_count_per_worker": 6_912,
        "total_reference_case_observation_count": 13_824,
        "cache_case_count_per_reference": 96,
        "expected_actual_worker_count_only_after_complete_success": SUITE_COUNT,
        "actual_candidate_workers": 0,
        "candidate_matching": "NOT RUN",
        "live_zig_activation": "NOT FROZEN; FAIL CLOSED",
        "historical_build_activates_native": False,
        "scanner_correction_applied": False,
        "scanner_verbose_620_repaired": False,
        "preserved_historical_zig_semantic_mismatch_count": 1_764,
        "source_family_inventory_is_candidate_execution": False,
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_synthetic(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(synthetic_contract()),
            "reject changed Zig controller owners, reference, cases, history, or activation")
    require(len(value["suites"]) == SUITE_COUNT
            and sum(row["case_execution_count"] for row in value["suites"])
            == CASE_DENOMINATOR,
            "preserve all 13 original suites and exactly 31,237 cases")
    return value


def expect_rejection(function: Any, *arguments: Any) -> None:
    try:
        function(*arguments)
    except (
        AggregateGateError, SourceOnlyEffect, WorkerProcessFailure,
        ValueError, TypeError, KeyError, OSError,
    ):
        return
    raise AggregateGateError("accepted an adversarial synthetic Zig controller case")


def _retain_complete_stream(raw: Any, limit: int, name: str) -> dict[str, Any]:
    require(type(raw) is bytes and type(limit) is int and limit > 0,
            "retain a complete real worker stream using an exact positive bound")
    retained = raw[:limit]
    tail = raw[-limit:]
    return {
        name + "_bytes": len(raw),
        name + "_sha256": digest(raw),
        name + "_retained_base64": base64.b64encode(retained).decode("ascii"),
        name + "_retained_bytes": len(retained),
        name + "_retained_sha256": digest(retained),
        name + "_tail_base64": base64.b64encode(tail).decode("ascii"),
        name + "_tail_bytes": len(tail),
        name + "_tail_sha256": digest(tail),
        name + "_overflow": len(raw) > limit,
        name + "_complete": len(raw) <= limit,
        name + "_full_stream_hash_recorded": True,
    }


def worker_process(
    arguments: list[str],
    *,
    launcher: Any | None = None,
    on_started: Any | None = None,
) -> dict[str, Any]:
    require(type(arguments) is list and bool(arguments)
            and all(type(item) is str for item in arguments),
            "launch only an exact complete pinned Zig worker argument vector")
    process: dict[str, Any] = {
        "attempted": True,
        "started": False,
        "pid": None,
        "returncode": None,
        "timed_out": False,
        "failure_phase": "spawn",
        "stdout_capture_completed": False,
        "stderr_capture_completed": False,
        "cleanup_kill_attempted": False,
        "cleanup_reap_attempted": False,
        "cleanup_reap_completed": False,
    }
    child: Any = None
    try:
        launch = subprocess.Popen if launcher is None else launcher
        child = launch(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        actual_pid = getattr(child, "pid", None)
        process.update({
            "started": True,
            "pid": actual_pid if type(actual_pid) is int and actual_pid > 0 else None,
            "failure_phase": "started",
        })
        if on_started is not None:
            on_started(copy.deepcopy(process))
        require(type(actual_pid) is int and actual_pid > 0,
                "record and reject a genuinely launched child without a valid PID")
        try:
            stdout, stderr = child.communicate(timeout=WORKER_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process["timed_out"] = True
            process["failure_phase"] = "timeout"
            process["cleanup_kill_attempted"] = True
            child.kill()
            process["cleanup_reap_attempted"] = True
            stdout, stderr = child.communicate()
            process["cleanup_reap_completed"] = True
        process["returncode"] = child.returncode
        process.update(_retain_complete_stream(stdout, MAX_CHILD_STDOUT_BYTES, "stdout"))
        process["stdout_capture_completed"] = True
        process.update(_retain_complete_stream(stderr, MAX_CHILD_STDERR_BYTES, "stderr"))
        process["stderr_capture_completed"] = True
        if process["stdout_overflow"] or process["stderr_overflow"]:
            process["failure_phase"] = "stream-overflow"
            raise WorkerProcessFailure(
                "preserve oversized complete stream, retained head, and tail hashes",
                process,
            )
        if process["timed_out"]:
            raise WorkerProcessFailure(
                "preserve PID, timeout, killed child, and both complete stream hashes",
                process,
            )
        process["failure_phase"] = None
        return process
    except WorkerProcessFailure:
        raise
    except BaseException as error:
        process["error_type"] = type(error).__qualname__
        process["error_message"] = bounded_error(error)
        if process["started"] and child is not None:
            if getattr(child, "returncode", None) is None:
                process["cleanup_kill_attempted"] = True
                try:
                    child.kill()
                except BaseException as cleanup_error:
                    process["cleanup_kill_error_type"] = type(cleanup_error).__qualname__
                    process["cleanup_kill_error_message"] = bounded_error(cleanup_error)
                process["cleanup_reap_attempted"] = True
                try:
                    stdout, stderr = child.communicate()
                    process.update(_retain_complete_stream(
                        stdout, MAX_CHILD_STDOUT_BYTES, "stdout"
                    ))
                    process["stdout_capture_completed"] = True
                    process.update(_retain_complete_stream(
                        stderr, MAX_CHILD_STDERR_BYTES, "stderr"
                    ))
                    process["stderr_capture_completed"] = True
                    process["cleanup_reap_completed"] = True
                except BaseException as cleanup_error:
                    process["cleanup_reap_error_type"] = type(cleanup_error).__qualname__
                    process["cleanup_reap_error_message"] = bounded_error(cleanup_error)
            process["returncode"] = getattr(child, "returncode", None)
        raise WorkerProcessFailure("retain the actual worker launch or capture failure", process) from error


def campaign_accounting(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    require(type(rows) is list and len(rows) == SUITE_COUNT,
            "require one and only one explicit record for every original Zig suite")
    known_names = set()
    pids: list[int] = []
    launches = 0
    observed_cases = 0
    infrastructure: list[str] = []
    semantic: list[str] = []
    mismatch_sum = 0
    for index, ((expected_name, expected_count), row) in enumerate(zip(SUITES, rows), start=1):
        require(type(row) is dict and row.get("suite") == expected_name
                and expected_name not in known_names
                and row.get("case_execution_denominator") == expected_count
                and row.get("attempt_index") == index,
                "reject reordered, duplicated, missing, or incorrectly counted Zig suite records")
        known_names.add(expected_name)
        attempted = row.get("actual_worker_attempted")
        started = row.get("actual_worker_started")
        require(type(attempted) is bool and type(started) is bool,
                "account for whether each genuine suite worker was actually attempted and started")
        if attempted:
            launches += 1
        if started:
            pid = row.get("actual_worker_pid")
            process = row.get("process")
            require(attempted and type(pid) is int and pid > 0
                    and type(process) is dict and process.get("started") is True
                    and process.get("pid") == pid,
                    "preserve each actually started worker and its genuine process identifier")
            pids.append(pid)
        else:
            require(row.get("actual_worker_pid") is None,
                    "never invent a process identifier for an unstarted suite")
        status = row.get("status")
        require(status in ("PASS", "FAIL"), "require an explicit PASS or FAIL for every suite")
        if not started or row.get("genuine_original_suite") is not True:
            require(status == "FAIL" and row.get("mismatch_count") is None,
                    "never hide an infrastructure failure behind zero semantic mismatches")
            infrastructure.append(expected_name)
            continue
        observed_cases += expected_count
        require(row.get("all_original_records_and_mismatches_preserved") is True,
                "retain all original records and complete mismatch evidence")
        mismatch_count = row.get("mismatch_count")
        require(type(mismatch_count) is int and mismatch_count >= 0,
                "require a nonnegative complete suite mismatch count")
        require((status == "PASS") is (mismatch_count == 0),
                "never relabel a semantic mismatch or false PASS")
        mismatch_sum += mismatch_count
        if mismatch_count:
            semantic.append(expected_name)
    distinct = len(set(pids)) == len(pids)
    require(distinct, "never count the same actual PID as multiple independent suite workers")
    complete = not infrastructure and len(pids) == SUITE_COUNT
    return {
        "suite_count": SUITE_COUNT,
        "completed_suite_count": len(rows) - len(infrastructure),
        "case_execution_denominator": CASE_DENOMINATOR,
        "observed_case_count": observed_cases,
        "actual_worker_launch_attempt_count": launches,
        "actual_candidate_workers": len(pids),
        "actual_worker_process_ids": pids,
        "actual_worker_pids_are_distinct": distinct,
        "infrastructure_failure_suites": infrastructure,
        "infrastructure_failure_count": len(infrastructure),
        "semantic_failure_suites": semantic,
        "observed_partial_semantic_mismatch_count": mismatch_sum,
        "semantic_mismatch_count": mismatch_sum if complete else "NOT MEASURED",
        "semantic_mismatch_count_complete": complete,
        "candidate_status": "PASS" if complete and mismatch_sum == 0 else "FAIL",
    }


def synthetic_worker_fault_controls() -> dict[str, int]:
    class FakeChild:
        def __init__(self, mode: str, pid: Any) -> None:
            self.mode = mode
            self.pid = pid
            self.returncode: int | None = None
            self.calls = 0
            self.killed = False

        def communicate(self, timeout: Any = None) -> tuple[bytes, bytes]:
            self.calls += 1
            if self.killed:
                return (b"{}\n", b"")
            if self.mode == "timeout" and self.calls == 1:
                raise subprocess.TimeoutExpired(("synthetic-zig-worker",), 1)
            if self.mode == "post-spawn":
                raise OSError("synthetic post-spawn stream capture failure")
            if self.mode == "stdout-overflow":
                self.returncode = 0
                return (b"x" * (MAX_CHILD_STDOUT_BYTES + 1), b"")
            if self.mode == "stderr-overflow":
                self.returncode = 0
                return (b"{}\n", b"y" * (MAX_CHILD_STDERR_BYTES + 1))
            self.returncode = 0
            return (b"{}\n", b"")

        def kill(self) -> None:
            self.killed = True
            self.returncode = -9

    def launcher(mode: str, pid: Any = 8_701) -> Any:
        def launch(*arguments: Any, **keywords: Any) -> FakeChild:
            if mode == "failed-spawn":
                raise OSError("synthetic worker spawn failure")
            return FakeChild(mode, pid)
        return launch

    accepted = 0
    rejected = 0
    starts: list[dict[str, Any]] = []
    success = worker_process(
        ["synthetic-zig-worker"], launcher=launcher("success"),
        on_started=starts.append,
    )
    require(
        success.get("started") is True
        and success.get("pid") == 8_701
        and success.get("returncode") == 0
        and success.get("timed_out") is False
        and success.get("stdout_bytes") == 3
        and success.get("stdout_sha256") == digest(b"{}\n")
        and success.get("stdout_retained_sha256") == digest(b"{}\n")
        and success.get("stdout_tail_sha256") == digest(b"{}\n")
        and success.get("stdout_full_stream_hash_recorded") is True
        and success.get("stderr_bytes") == 0
        and success.get("stderr_sha256") == digest(b"")
        and len(starts) == 1 and starts[0].get("pid") == 8_701,
        "prove early synthetic PID evidence and complete full/head/tail stream hashes",
    )
    accepted += 1
    for mode in (
        "failed-spawn", "post-spawn", "timeout", "stdout-overflow",
        "stderr-overflow", "missing-pid",
    ):
        pid: Any = None if mode == "missing-pid" else 8_800 + rejected
        try:
            worker_process(["synthetic-zig-worker"], launcher=launcher(mode, pid))
        except WorkerProcessFailure as error:
            record = error.process
            require(record.get("attempted") is True,
                    "preserve every attempted synthetic process launch")
            if mode == "failed-spawn":
                require(record.get("started") is False and record.get("pid") is None,
                        "never invent a child PID after a failed launch")
            elif mode == "missing-pid":
                require(record.get("started") is True and record.get("pid") is None
                        and record.get("cleanup_kill_attempted") is True
                        and record.get("cleanup_reap_completed") is True,
                        "retain and reap a genuinely launched child with no provable PID")
            else:
                require(record.get("started") is True and record.get("pid") == pid,
                        "retain the actual started child after downstream worker failure")
            if mode == "timeout":
                require(record.get("timed_out") is True
                        and record.get("returncode") == -9
                        and record.get("cleanup_kill_attempted") is True
                        and record.get("cleanup_reap_completed") is True,
                        "retain timeout, kill, reap, PID, and complete streams")
            if mode == "post-spawn":
                require(record.get("cleanup_kill_attempted") is True
                        and record.get("cleanup_reap_completed") is True,
                        "kill and reap every child after capture failure")
            if mode in ("stdout-overflow", "stderr-overflow"):
                name = "stdout" if mode == "stdout-overflow" else "stderr"
                limit = MAX_CHILD_STDOUT_BYTES if name == "stdout" else MAX_CHILD_STDERR_BYTES
                fill = b"x" if name == "stdout" else b"y"
                expected = fill * (limit + 1)
                require(record.get(name + "_overflow") is True
                        and record.get(name + "_bytes") == limit + 1
                        and record.get(name + "_sha256") == digest(expected)
                        and record.get(name + "_retained_sha256")
                        == digest(expected[:limit])
                        and record.get(name + "_tail_sha256")
                        == digest(expected[-limit:]),
                        "retain full, head, and tail hashes for oversized worker streams")
            rejected += 1
        else:
            raise AggregateGateError("accepted a synthetic Zig worker fault: " + mode)

    rows: list[dict[str, Any]] = []
    for index, (name, count) in enumerate(SUITES, start=1):
        pid = 9_000 + index
        rows.append({
            "suite": name,
            "case_execution_denominator": count,
            "attempt_index": index,
            "actual_worker_attempted": True,
            "actual_worker_started": True,
            "actual_worker_pid": pid,
            "status": "PASS",
            "genuine_original_suite": True,
            "mismatch_count": 0,
            "all_original_records_and_mismatches_preserved": True,
            "process": {"attempted": True, "started": True, "pid": pid},
        })
    account = campaign_accounting(rows)
    require(account.get("actual_candidate_workers") == SUITE_COUNT
            and account.get("observed_case_count") == CASE_DENOMINATOR
            and account.get("actual_worker_pids_are_distinct") is True
            and account.get("semantic_mismatch_count") == 0
            and account.get("candidate_status") == "PASS",
            "prove exactly 13 distinct synthetic workers and all 31,237 original cases")
    accepted += 1
    for mode in (
        "missing-suite", "extra-suite", "reordered-suite", "wrong-case-count",
        "duplicate-pid", "false-pass", "missing-records", "wrong-attempt-index",
    ):
        altered = copy.deepcopy(rows)
        if mode == "missing-suite":
            altered.pop()
        elif mode == "extra-suite":
            altered.append(copy.deepcopy(altered[-1]))
        elif mode == "reordered-suite":
            altered[0], altered[1] = altered[1], altered[0]
        elif mode == "wrong-case-count":
            altered[2]["case_execution_denominator"] -= 1
        elif mode == "duplicate-pid":
            pid = altered[0]["actual_worker_pid"]
            altered[1]["actual_worker_pid"] = pid
            altered[1]["process"]["pid"] = pid
        elif mode == "false-pass":
            altered[3]["mismatch_count"] = 1
        elif mode == "missing-records":
            altered[4]["all_original_records_and_mismatches_preserved"] = False
        else:
            altered[5]["attempt_index"] = 1
        expect_rejection(campaign_accounting, altered)
        rejected += 1
    partial = copy.deepcopy(rows)
    partial[6].update({
        "actual_worker_attempted": False,
        "actual_worker_started": False,
        "actual_worker_pid": None,
        "status": "FAIL",
        "genuine_original_suite": False,
        "mismatch_count": None,
        "process": {"attempted": False, "started": False, "pid": None},
    })
    incomplete = campaign_accounting(partial)
    require(incomplete.get("candidate_status") == "FAIL"
            and incomplete.get("actual_candidate_workers") == 12
            and incomplete.get("infrastructure_failure_count") == 1
            and incomplete.get("semantic_mismatch_count") == "NOT MEASURED"
            and incomplete.get("semantic_mismatch_count_complete") is False,
            "never claim complete semantic results when one genuine worker did not run")
    accepted += 1
    return {"accepted": accepted, "rejected": rejected}


def synthetic_boundary_controls(effects: dict[str, int]) -> dict[str, int]:
    probes: tuple[tuple[str, Any, tuple[Any, ...]], ...] = (
        ("blocked_reads", builtins.open, ("never-read-zig-controller",)),
        ("blocked_reads", _io.open, ("never-read-zig-controller",)),
        ("blocked_reads", os.open, ("never-read-zig-controller", os.O_RDONLY)),
        ("blocked_writes", os.write, (-1, b"x")),
        ("blocked_writes", os.unlink, ("never-unlink-zig-controller",)),
        ("blocked_processes", subprocess.Popen, (["never-launch-zig"],)),
        ("blocked_processes", subprocess.run, (["never-launch-zig"],)),
        ("blocked_native_loads", ctypes.CDLL, ("never-load-native-zig",)),
        ("blocked_native_loads", _ctypes.dlopen, ("never-load-native-zig",)),
        ("blocked_decompression", gzip.decompress, (b"never-open-evidence",)),
        ("blocked_decompression", zlib.decompress, (b"never-open-evidence",)),
        ("blocked_imports", importlib.import_module, ("candidates.zig_candidate",)),
        ("blocked_low_level_imports", _imp.create_dynamic, (None,)),
        ("blocked_threads", _thread.start_new_thread, (lambda: None, ())),
        ("blocked_network", socket.create_connection, (("127.0.0.1", 1),)),
        ("blocked_clocks", time.perf_counter, ()),
        ("blocked_clocks", time.sleep, (0,)),
    )
    rejected = 0
    for counter, function, arguments in probes:
        previous = effects[counter]
        expect_rejection(function, *arguments)
        require(effects[counter] == previous + 1,
                "physically block and account for each prohibited source-only controller effect")
        rejected += 1
    return {"accepted": 0, "rejected": rejected}


def source_self_test() -> dict[str, Any]:
    with source_only_boundary() as effects:
        original = validate_synthetic(synthetic_contract())
        accepted = 1
        rejected = 0
        for key, changed in (
            ("schema", WORKER_SCHEMA),
            ("family", "c"),
            ("worker_schema", "rebar-frozen-python-re-p0-candidate-worker-v8"),
            ("suite_count", 12),
            ("case_execution_denominator", 31_236),
            ("named_private_waiver_count", 12),
            ("current_overview_version", 44),
            ("current_overview_summary_sha256", "0" * 64),
            ("current_overview_summary_bytes", CURRENT_V45_SUMMARY_BYTES - 1),
            ("current_evidence_owner_lower_bound", 164),
            ("current_authenticated_reference_lower_bound", 169),
            ("publication_safe_rust_v7_source_sha256", "0" * 64),
            ("publication_safe_rust_v7_matching", "PASS"),
            ("actual_rust_v6_preflight", "PASS"),
            ("actual_rust_v6_historical_build_archive_read_count", 0),
            ("actual_rust_v6_historical_build_archive_inflation_count", 0),
            ("actual_rust_v6_candidate_workers", 1),
            ("public_entrypoint_matrix_case_count", 31),
            ("public_entrypoint_matrix_sha256", "0" * 64),
            ("public_entrypoint_status", "PASS"),
            ("original_producer_source_sha256", "0" * 64),
            ("original_producer_protocol_sha256", "0" * 64),
            ("original_producer_contract_sha256", "0" * 64),
            ("corrected_public_records_sha256", "0" * 64),
            ("corrected_public_cache_records_sha256", "0" * 64),
            ("corrected_public_reference_process_ids", [82, 83]),
            ("corrected_public_reference_process_ids", [81, 81]),
            ("reference_case_count_per_worker", 6_911),
            ("total_reference_case_observation_count", 6_912),
            ("cache_case_count_per_reference", 95),
            ("expected_actual_worker_count_only_after_complete_success", 12),
            ("actual_candidate_workers", 13),
            ("candidate_matching", "PASS"),
            ("live_zig_activation", "PASS"),
            ("historical_build_activates_native", True),
            ("scanner_correction_applied", True),
            ("scanner_verbose_620_repaired", True),
            ("preserved_historical_zig_semantic_mismatch_count", 0),
            ("source_family_inventory_is_candidate_execution", True),
            ("qualified_candidate_count", 1),
            ("performance", "FASTER"),
            ("memory", 0),
            ("undefined_behavior", "PASS"),
            ("runtime_non_delegation", "PASS"),
            ("holdout", "OPENED"),
            ("winner_selected", True),
        ):
            altered = copy.deepcopy(original)
            altered[key] = changed
            expect_rejection(validate_synthetic, altered)
            rejected += 1
        for changed in (
            "oracle/phase1/evidence/reference.json.gz",
            "candidates/_zig_probe.so",
            "performance/final-holdout.json",
            "oracle/phase3/holdout.json",
            "../GOAL.md",
            "/tmp/owner.json",
        ):
            expect_rejection(checked_relative, changed)
            rejected += 1
        process = synthetic_worker_fault_controls()
        boundary = synthetic_boundary_controls(effects)
        accepted += process["accepted"] + boundary["accepted"]
        rejected += process["rejected"] + boundary["rejected"]
        require(all(effects[key] == 0 for key in (
            "file_reads", "file_writes", "candidate_imports", "candidate_workers",
            "reference_workers", "source_builds", "native_activations",
            "native_libraries_loaded", "threads_started", "network_requests",
            "clock_samples", "hidden_cases_read", "benchmark_files_read",
        )), "never claim that rejected synthetic probes performed real external effects")
        observed_effects = copy.deepcopy(effects)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "family": FAMILY,
        "synthetic_controls_accepted": accepted,
        "synthetic_controls_rejected": rejected,
        "process_fault_controls_are_synthetic": True,
        "source_only_effects": observed_effects,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "archives_opened": 0,
        "archives_inflated": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_matching": "NOT RUN",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def load_worker(options: argparse.Namespace) -> tuple[types.ModuleType, dict[str, Any]]:
    owner = Owner(WORKER_RELATIVE, options.worker_source_sha256, options.worker_source_size_bytes)
    raw, record = read_owner(owner)
    try:
        tree = ast.parse(raw.decode("utf-8", "strict"), filename=WORKER_RELATIVE)
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise AggregateGateError("reject malformed dedicated first-party Zig worker source") from error
    require(
        any(isinstance(item, ast.FunctionDef) and item.name == "verify_frozen_context"
            for item in tree.body)
        and any(isinstance(item, ast.FunctionDef) and item.name == "source_self_test"
                for item in tree.body),
        "require the real source-authenticated independent Zig worker and its source-only context gate",
    )
    module_name = "_rebar_frozen_zig_original_p0_candidate_worker_v1_source_only"
    require(module_name not in sys.modules, "reject an already-loaded or substituted worker module")
    module = types.ModuleType(module_name)
    module.__file__ = str(ROOT / WORKER_RELATIVE)
    sys.modules[module_name] = module
    try:
        exec(compile(tree, module.__file__, "exec"), module.__dict__)
        require(module.SCHEMA == WORKER_SCHEMA and module.RUNNER_SCHEMA == SCHEMA
                and module.FAMILY == FAMILY
                and tuple(module.SUITES) == SUITES
                and module.CASE_DENOMINATOR == CASE_DENOMINATOR,
                "never substitute the C-only worker, another candidate family, or a reduced oracle")
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module, record


def worker_context_arguments(options: argparse.Namespace) -> list[str]:
    return [
        "--verify-frozen-context",
        "--source-sha256", options.worker_source_sha256,
        "--source-size-bytes", str(options.worker_source_size_bytes),
        "--runner-source-sha256", options.source_sha256,
        "--runner-source-size-bytes", str(options.source_size_bytes),
        "--protocol-sha256", options.protocol_sha256,
        "--protocol-size-bytes", str(options.protocol_size_bytes),
        "--document-sha256", options.document_sha256,
        "--document-size-bytes", str(options.document_size_bytes),
        "--producer-source-sha256", options.producer_source_sha256,
        "--producer-protocol-sha256", options.producer_protocol_sha256,
        "--producer-document-sha256", options.producer_document_sha256,
    ]


def actual_worker_arguments(options: argparse.Namespace, suite: str) -> list[str]:
    require(suite in {name for name, _ in SUITES}, "require one genuine original suite")
    return [
        PINNED_PYTHON, "-I", "-B", str(ROOT / WORKER_RELATIVE),
        "--run", "--candidate", FAMILY, "--suite", suite,
        "--label", options.label,
        "--source-sha256", options.worker_source_sha256,
        "--source-size-bytes", str(options.worker_source_size_bytes),
        "--runner-source-sha256", options.source_sha256,
        "--runner-source-size-bytes", str(options.source_size_bytes),
        "--protocol-sha256", options.protocol_sha256,
        "--protocol-size-bytes", str(options.protocol_size_bytes),
        "--document-sha256", options.document_sha256,
        "--document-size-bytes", str(options.document_size_bytes),
        "--producer-source-sha256", options.producer_source_sha256,
        "--producer-protocol-sha256", options.producer_protocol_sha256,
        "--producer-document-sha256", options.producer_document_sha256,
    ]


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    source_owner = Owner(SOURCE_RELATIVE, options.source_sha256, options.source_size_bytes)
    protocol_owner = Owner(PROTOCOL_RELATIVE, options.protocol_sha256, options.protocol_size_bytes)
    contract_owner = Owner(DOCUMENT_RELATIVE, options.document_sha256, options.document_size_bytes)
    source_raw, source = read_owner(source_owner)
    protocol_raw, protocol = read_owner(protocol_owner)
    document_raw, contract = read_owner(contract_owner)
    try:
        ast.parse(source_raw.decode("utf-8", "strict"), filename=SOURCE_RELATIVE)
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise AggregateGateError("reject an invalid source-authenticated dedicated Zig controller") from error
    require(bool(protocol_raw), "require the independently frozen complete Zig source-only protocol")
    worker, worker_owner = load_worker(options)
    selected = worker.parse_arguments(worker_context_arguments(options))
    worker_context = worker.verify_frozen_context(selected)
    history = worker_context.get("v45_history")
    rust_v7 = worker_context.get("rust_v7_history")
    failure = worker_context.get("actual_rust_v6_failure")
    public = worker_context.get("public_entrypoint")
    compiler = worker_context.get("official_zig_compiler")
    require(worker_context.get("status") == "PASS"
            and worker_context.get("family") == FAMILY
            and worker_context.get("suite_count") == SUITE_COUNT
            and worker_context.get("case_execution_denominator") == CASE_DENOMINATOR
            and worker_context.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and worker_context.get("candidate_matching_status") == "NOT RUN"
            and worker_context.get("live_activation_status") == "NOT FROZEN; FAIL CLOSED"
            and type(history) is dict
            and history.get("overview") == "V45"
            and history.get("authenticated_evidence_owner_lower_bound")
            == CURRENT_EVIDENCE_OWNER_LOWER_BOUND
            and history.get("authenticated_history_reference_lower_bound")
            == CURRENT_AUTHENTICATED_REFERENCE_LOWER_BOUND
            and history.get("actually_runnable_candidate_family_count") == 0
            and type(rust_v7) is dict
            and rust_v7.get("rust_candidate_matching") == "NOT RUN"
            and type(rust_v7.get("owners")) is dict
            and rust_v7["owners"].get("source", {}).get("sha256")
            == CURRENT_RUST_V7_SOURCE_SHA256
            and type(failure) is dict
            and failure.get("actual_preflight_status") == "FAIL"
            and failure.get("historical_source_build_archive_read_count") == 1
            and failure.get("historical_source_build_archive_gzip_inflation_count") == 1
            and failure.get("historical_candidate_workers") == 0
            and type(public) is dict
            and public.get("public_entrypoint_status") == "FAIL"
            and public.get("matrix_case_count") == 32
            and public.get("matrix_sha256") == CURRENT_PUBLIC_MATRIX_SHA256
            and public.get("case_status_counts") == {
                "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
                "NOT ESTABLISHED": 1, "NOT OPENED": 1,
            }
            and public.get("candidate_qualified") is False
            and type(compiler) is dict
            and compiler.get("path") == "/tmp/zig-x86_64-linux-0.16.0/zig"
            and compiler.get("sha256")
            == "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
            and compiler.get("bytes") == 172_641_672
            and compiler.get("compiler_executed") is False,
            "reauthenticate actual V45, real public failures, publication-safe Rust V7, "
            "preserved V6 effects, pinned Zig compiler and fail-closed matching")
    parsed = worker.exact_json(document_raw, "dedicated first-party Zig V1 canonical contract")
    expected = worker_context.get("expected_protocol_document")
    require(type(expected) is dict and worker.canonical(parsed) == worker.canonical(expected),
            "reject a changed Zig worker contract, corrected references, history, or original cases")
    return {
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS",
        "family": FAMILY,
        "source": source,
        "worker": worker_owner,
        "protocol": protocol,
        "contract": contract,
        "worker_context": worker_context,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "current_overview_version": 45,
        "current_overview_summary_sha256": CURRENT_V45_SUMMARY_SHA256,
        "authenticated_evidence_owner_lower_bound":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "authenticated_history_reference_lower_bound":
            CURRENT_AUTHENTICATED_REFERENCE_LOWER_BOUND,
        "publication_safe_rust_v7": rust_v7,
        "actual_rust_v6_failure": failure,
        "expanded_public_entrypoint": public,
        "official_zig_compiler": compiler,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "archives_opened": 0,
        "archives_inflated": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_matching_status": "NOT RUN",
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    if arguments is None:
        arguments = sys.argv[1:]
    require(isinstance(arguments, (list, tuple)) and all(type(item) is str for item in arguments),
            "require one unambiguous first-party Zig controller command")
    flags = [item for item in arguments if item.startswith("--")]
    require(len(flags) == len(set(flags)), "reject repeated or ambiguous controller authorization flags")
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=(FAMILY,))
    parser.add_argument("--label")
    for name in ("source", "worker-source", "protocol", "document"):
        parser.add_argument("--" + name + "-sha256")
        parser.add_argument("--" + name + "-size-bytes", type=int)
    for name in ("producer-source", "producer-protocol", "producer-document"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(list(arguments))
    digest_names = (
        "source_sha256", "worker_source_sha256", "protocol_sha256",
        "document_sha256", "producer_source_sha256", "producer_protocol_sha256",
        "producer_document_sha256",
    )
    size_names = (
        "source_size_bytes", "worker_source_size_bytes",
        "protocol_size_bytes", "document_size_bytes",
    )
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            *digest_names, *size_names, "candidate", "label",
        )), "source-only synthetic checks never authorize an owner, candidate, worker, or run")
        return options
    for name in digest_names:
        checked_digest(getattr(options, name), name)
    for name in size_names:
        value = getattr(options, name)
        require(type(value) is int and 0 < value <= MAX_SOURCE_BYTES,
                "independently pin complete dedicated Zig owner bytes for " + name)
    require(options.producer_source_sha256 == V4_SOURCE_SHA256
            and options.producer_protocol_sha256 == V4_PROTOCOL_SHA256
            and options.producer_document_sha256 == V4_DOCUMENT_SHA256,
            "reject stale V3, missing pins, shared engines, and the C-only runner")
    if options.verify_frozen_context:
        require(options.candidate is None and options.label is None,
                "read-only source context cannot select or execute a candidate")
        return options
    require(options.candidate == FAMILY
            and type(options.label) is str and 0 < len(options.label) <= 48
            and all(character.isascii()
                    and (character.isalnum() or character in "-_")
                    for character in options.label),
            "require an exact safe Zig-only campaign label")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = source_self_test()
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            context = verify_frozen_context(options)
            require(context.get("status") == "PASS",
                    "authenticate the complete Zig V1 frozen source before any actual action")
            worker, _ = load_worker(options)
            worker.require_verified_zig_activation()
            raise AggregateGateError(
                "ACTUAL FIRST-PARTY ZIG MATCHING IS NOT AUTHORIZED; "
                "NO LIVE VERIFIED ZIG ACTIVATION OR FROZEN SUITE PUBLICATION EXISTS"
            )
        sys.stdout.buffer.write(bounded_public_report(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        result = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "family": FAMILY,
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "actual_native_libraries_loaded": 0,
            "archives_opened": 0,
            "archives_inflated": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_matching_status": "NOT RUN",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        try:
            sys.stdout.buffer.write(bounded_public_report(result))
            sys.stdout.buffer.flush()
        except BaseException:
            return 1
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
