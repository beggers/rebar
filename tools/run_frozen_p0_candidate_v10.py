#!/usr/bin/env python3
"""Record all 13 original correctness checks against the first-party C candidate.

Every process attempt is recorded before launch. Started process identifiers,
complete stream lengths and hashes, timeouts, crashes and publication failures
remain visible even when a worker cannot produce a valid report.
"""

from __future__ import annotations

import argparse
import _ctypes
import _imp
import _io
import _posixsubprocess
import _thread
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
import traceback
import types
import unicodedata
import zlib
from typing import Any, Iterator, Mapping, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_v10.py"
WORKER_RELATIVE = "tools/run_frozen_p0_candidate_worker_v8.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v10.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-v10"
WORKER_SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v8"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ORIGINAL_PRODUCER_SHA256 = "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8"
ORIGINAL_PRODUCER_PROTOCOL_SHA256 = "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5"
ORIGINAL_PRODUCER_DOCUMENT_SHA256 = "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5"
PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT = 30
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
ORIGINAL_C_SHA256 = "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
DERIVED_C_SHA256 = "8b35fba5b565ae18c5b9c180bec1dfbfb46b75bf3db7421626da4a73cdda2b94"
FAMILY = "c"
FAMILY_NAMES = ("rust", "c", "zig", "cpp", "go", "fortran")
CORRECTED_PUBLIC_RECORDS_SHA256 = "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
HISTORICAL_PUBLIC_RECORDS_SHA256 = "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
CORRECTED_PUBLIC_COHORT_RECORDS_SHA256 = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256 = "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
CORRECTED_PUBLIC_REFERENCE_PIDS = (81, 82)
CORRECTED_PUBLIC_COHORT_CASE_COUNT = 96
C15_NATIVE_SHA256 = "aed6e9c2fbe31ee3798c74bc6fe896494f1a3bfed41ff25dcfef6905e7b8e610"
V39_SUMMARY_SHA256 = "d25c486e36d82069c718f82a1f6281295d539606dcd72a0a6c2c295f5a4e4ca6"
V40_SUMMARY_SHA256 = "5e9f2216fc2a0ab4742d36a1aa49c422880a8ae17e3e1534da9b362ca0eeda92"
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
SUITE_COUNT = 13
CASE_DENOMINATOR = 31237
PRIVATE_WAIVER_COUNT = 13
HISTORICAL_EVIDENCE_OWNER_COUNT = 164
HISTORICAL_AUTHENTICATED_REFERENCE_COUNT = 169
SOURCE_FAMILY_COUNT = 6
SOURCE_OWNER_COUNT = 25
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PUBLIC_REPORT_BYTES = 32 * 1024 * 1024
MAX_CHILD_STDOUT_BYTES = 1024 * 1024
MAX_CHILD_STDERR_BYTES = 2 * 1024 * 1024
MAX_ERROR_BYTES = 64 * 1024
WORKER_TIMEOUT_SECONDS = 3600


class AggregateGateError(Exception):
    """Reject an incomplete original repaired-C correctness campaign."""


class SourceOnlyEffect(AggregateGateError):
    """A source-only check attempted an external operation."""


class WorkerProcessFailure(AggregateGateError):
    """Retain everything actually known when launching or observing fails."""

    def __init__(self, message: str, process: dict[str, Any]) -> None:
        super().__init__(message)
        self.process = copy.deepcopy(process)


def new_actual_effect_ledger(options: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-authorized-actual-effect-ledger",
        "mode": "AUTHORIZED ACTUAL CANDIDATE RUN",
        "candidate_family": options.candidate,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "label": options.label,
        "phase": "before-candidate-preflight",
        "planned_suite_count": SUITE_COUNT,
        "attempted_suite_count": 0,
        "started_suite_count": 0,
        "completed_suite_count": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_worker_pids": [],
        "worker_attempts": [],
        "durable_attempt_snapshots": [],
        "actual_native_activations": 0,
        "actual_native_promotions": 0,
        "actual_native_library_loads": "NOT MEASURED",
        "actual_source_builds": 0,
        "actual_reference_workers": 0,
        "archive_publication_attempted": False,
        "receipt_publication_attempted": False,
        "public_report_serialization_attempted": False,
        "public_report_write_attempted": False,
        "public_report_flush_attempted": False,
        "publication_status": "NOT ATTEMPTED",
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def actual_entry_failure_result(
    error: BaseException,
    ledger: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(ledger) is dict
            and ledger.get("schema")
            == SCHEMA + "-authorized-actual-effect-ledger"
            and ledger.get("mode") == "AUTHORIZED ACTUAL CANDIDATE RUN",
            "never turn a genuine actual run into a zero-effect source failure")
    retained = copy.deepcopy(dict(ledger))
    retained["effect_ledger_schema"] = retained.pop("schema")
    if (retained.get("archive_publication_attempted") is True
            or retained.get("receipt_publication_attempted") is True
            or retained.get("public_report_serialization_attempted") is True
            or retained.get("public_report_write_attempted") is True
            or retained.get("public_report_flush_attempted") is True):
        retained["publication_status"] = "FAIL"
    return {
        **retained,
        "schema": SCHEMA + "-entry-failure",
        "status": "FAIL",
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "semantic_mismatch_count": "NOT MEASURED",
        "all_original_suite_evidence_preserved": False,
        "source_only_zero_effects_claimed": False,
        "candidate_qualified": False,
        "error_type": type(error).__qualname__,
        "error_message": bounded_error(error),
        "winner_selected": False,
    }


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise AggregateGateError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete original bytes")
    return hashlib.sha256(raw).hexdigest()


def bounded_error(error: BaseException) -> str:
    raw = str(error).encode("utf-8", "backslashreplace")
    if len(raw) > MAX_ERROR_BYTES:
        raw = raw[:MAX_ERROR_BYTES] + b" [error summary truncated]"
    return raw.decode("utf-8", "replace")


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise AggregateGateError("reject noncanonical aggregate evidence") from error


def bounded_public_report(
    value: Any,
    maximum: int = MAX_PUBLIC_REPORT_BYTES,
) -> bytes:
    require(type(maximum) is int and maximum > 0,
            "require a positive complete outer report bound")
    raw = canonical(value)
    require(len(raw) <= maximum,
            "never truncate or publish an oversized complete campaign")
    return raw


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(part in "0123456789abcdef" for part in value),
            "require independently pinned aggregate owner: " + label)
    return value


def runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only isolated pinned CPython and the genuine V10 aggregate")


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {key: 0 for key in (
        "file_reads", "file_writes", "candidate_workers", "reference_workers",
        "source_builds", "native_activations", "candidate_imports",
        "interpreter_creations", "network_requests", "clock_samples",
        "hidden_cases_read", "benchmark_files_read", "blocked_reads",
        "blocked_writes", "blocked_processes", "blocked_imports",
        "blocked_threads", "blocked_network", "blocked_clocks",
        "blocked_native_loads", "blocked_decompression",
        "blocked_low_level_imports",
    )}
    originals: list[tuple[Any, str, Any]] = []

    def block(owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def reject(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyEffect("source-only V10 aggregate forbids " + name)

        originals.append((owner, name, previous))
        setattr(owner, name, reject)

    try:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (os, "read"), (os, "stat"),
                            (Path, "open"), (Path, "read_bytes")):
            block(owner, name, "blocked_reads")
        for owner, name in ((os, "write"), (os, "unlink"), (os, "replace"),
                            (os, "rename"), (os, "fsync"), (os, "mkdir"),
                            (Path, "write_bytes"), (Path, "write_text"),
                            (tempfile, "mkdtemp"), (tempfile, "mkstemp")):
            block(owner, name, "blocked_writes")
        block(importlib, "import_module", "blocked_imports")
        block(_imp, "create_dynamic", "blocked_low_level_imports")
        block(_imp, "exec_dynamic", "blocked_low_level_imports")
        block(_imp, "create_builtin", "blocked_low_level_imports")
        block(_io, "open", "blocked_reads")
        block(_posixsubprocess, "fork_exec", "blocked_processes")
        block(_thread, "start_new_thread", "blocked_threads")
        block(_ctypes, "dlopen", "blocked_native_loads")
        block(ctypes, "CDLL", "blocked_native_loads")
        block(ctypes, "PyDLL", "blocked_native_loads")
        block(gzip, "GzipFile", "blocked_decompression")
        block(gzip, "decompress", "blocked_decompression")
        block(zlib, "decompress", "blocked_decompression")
        block(zlib, "decompressobj", "blocked_decompression")
        block(subprocess, "Popen", "blocked_processes")
        block(subprocess, "run", "blocked_processes")
        block(threading.Thread, "start", "blocked_threads")
        block(socket, "create_connection", "blocked_network")
        block(socket.socket, "connect", "blocked_network")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            block(time, name, "blocked_clocks")
        yield effects
    finally:
        for owner, name, previous in reversed(originals):
            setattr(owner, name, previous)


def synthetic_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-synthetic-source-contract",
        "family": FAMILY,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "suite_ids": [name for name, _ in SUITES],
        "original_producer_sha256": ORIGINAL_PRODUCER_SHA256,
        "original_producer_protocol_sha256": ORIGINAL_PRODUCER_PROTOCOL_SHA256,
        "original_producer_document_sha256": ORIGINAL_PRODUCER_DOCUMENT_SHA256,
        "nested_producer_sha256": ORIGINAL_PRODUCER_SHA256,
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "historical_evidence_owner_count": HISTORICAL_EVIDENCE_OWNER_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "historical_authenticated_reference_count":
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "maximum_public_report_bytes": MAX_PUBLIC_REPORT_BYTES,
        "expected_v15_build_process_count": 14,
        "expected_actual_original_worker_count": 13,
        "family_names": list(FAMILY_NAMES),
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "historical_public_records_sha256": HISTORICAL_PUBLIC_RECORDS_SHA256,
        "corrected_public_cohort_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "corrected_public_cohort_case_ids_sha256":
            CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256,
        "corrected_public_cohort_case_count": CORRECTED_PUBLIC_COHORT_CASE_COUNT,
        "corrected_public_reference_pids": list(CORRECTED_PUBLIC_REFERENCE_PIDS),
        "c_pattern_equality_failure_waived": False,
        "current_overview_v40_sha256": V40_SUMMARY_SHA256,
        "preserved_overview_v39_sha256": V39_SUMMARY_SHA256,
        "current_c15_native_sha256": C15_NATIVE_SHA256,
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified_count": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_synthetic(value: Any) -> dict[str, Any]:
    expected = synthetic_contract()
    require(type(value) is dict and canonical(value) == canonical(expected),
            "reject changed original suite, derived source, activation, or history")
    require(len(SUITES) == SUITE_COUNT
            and len({name for name, _ in SUITES}) == SUITE_COUNT
            and sum(count for _, count in SUITES) == CASE_DENOMINATOR,
            "never omit or recount an unchanged original P0 suite")
    return value


def source_self_test() -> dict[str, Any]:
    accepted = 0
    rejected = 0
    with source_only_boundary() as effects:
        contract = validate_synthetic(synthetic_contract())
        accepted += 1
        changes = (
            ("schema", SCHEMA), ("family", "rust"),
            ("suite_count", 12), ("case_execution_denominator", 31236),
            ("named_private_waiver_count", 12),
            ("source_family_count", 5), ("source_owner_count", 24),
            ("runnable_candidate_family_count", 0),
            ("runnable_candidate_family_count", 6),
            ("runnable_candidate_families", ["rust"]),
            ("runnable_candidate_families", list(FAMILY_NAMES)),
            ("six_family_inventory_is_source_only", False),
            ("original_producer_sha256", "0" * 64),
            ("nested_producer_sha256", "0" * 64),
            ("original_c_source_sha256", DERIVED_C_SHA256),
            ("derived_c_source_sha256", ORIGINAL_C_SHA256),
            ("historical_evidence_owner_count", 76),
            ("historical_authenticated_reference_count", 71),
            ("maximum_public_report_bytes", MAX_PUBLIC_REPORT_BYTES + 1),
            ("expected_v15_build_process_count", 13),
            ("expected_actual_original_worker_count", 12),
            ("corrected_public_records_sha256", HISTORICAL_PUBLIC_RECORDS_SHA256),
            ("historical_public_records_sha256", CORRECTED_PUBLIC_RECORDS_SHA256),
            ("corrected_public_cohort_records_sha256", "0" * 64),
            ("corrected_public_cohort_case_ids_sha256", "0" * 64),
            ("corrected_public_cohort_case_count", 95),
            ("corrected_public_reference_pids", [81, 81]),
            ("c_pattern_equality_failure_waived", True),
            ("current_overview_v40_sha256", V39_SUMMARY_SHA256),
            ("preserved_overview_v39_sha256", V40_SUMMARY_SHA256),
            ("current_c15_native_sha256", "0" * 64),
            ("candidate_correctness", "PASS"),
            ("candidate_qualified_count", 1),
            ("hidden_cases_read", 1), ("clock_samples", 1),
            ("timing_trials_run", 1), ("performance", "PASS"),
            ("memory", "PASS"), ("holdout", "OPEN"),
            ("winner_selected", True),
        )
        for key, forged in changes:
            mutation = copy.deepcopy(contract)
            mutation[key] = forged
            try:
                validate_synthetic(mutation)
            except AggregateGateError:
                rejected += 1
            else:
                raise AggregateGateError("accepted forged contract: " + key)
        for index, (name, _) in enumerate(SUITES):
            mutation = copy.deepcopy(contract)
            mutation["suite_ids"][index] = name + "-forged"
            try:
                validate_synthetic(mutation)
            except AggregateGateError:
                rejected += 1
            else:
                raise AggregateGateError("accepted a changed original suite")
        for forged in (None, {}, [], True, 0, "forged"):
            try:
                validate_synthetic(forged)
            except (AggregateGateError, TypeError, AttributeError):
                rejected += 1
            else:
                raise AggregateGateError("accepted non-contract evidence")
        for bad in (None, "", "g" * 64, "a" * 63, "a" * 65, 1):
            try:
                checked_digest(bad, "synthetic owner")
            except AggregateGateError:
                rejected += 1
            else:
                raise AggregateGateError("accepted a forged digest")
        probes = (
            ("blocked_reads", lambda: builtins.open("/tmp/rebar-v10-forbidden", "rb")),
            ("blocked_reads", lambda: os.open("/tmp/rebar-v10-forbidden", os.O_RDONLY)),
            ("blocked_writes", lambda: os.write(-1, b"forbidden")),
            ("blocked_processes", lambda: subprocess.run(("forbidden-v10-worker",))),
            ("blocked_imports", lambda: importlib.import_module("candidates.vm_candidate")),
            ("blocked_threads", lambda: threading.Thread(target=lambda: None).start()),
            ("blocked_network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("blocked_clocks", lambda: time.perf_counter_ns()),
            ("blocked_reads", lambda: _io.open("/tmp/rebar-v10-forbidden", "rb")),
            ("blocked_processes", lambda: _posixsubprocess.fork_exec()),
            ("blocked_threads", lambda: _thread.start_new_thread(lambda: None, ())),
            ("blocked_native_loads", lambda: _ctypes.dlopen("forbidden-v10.so")),
            ("blocked_native_loads", lambda: ctypes.CDLL("forbidden-v10.so")),
            ("blocked_low_level_imports", lambda: _imp.create_dynamic(None)),
            ("blocked_decompression", lambda: zlib.decompress(b"forbidden")),
            ("blocked_decompression", lambda: gzip.decompress(b"forbidden")),
        )
        for counter, probe in probes:
            previous = effects[counter]
            try:
                probe()
            except SourceOnlyEffect:
                require(effects[counter] == previous + 1,
                        "authenticate the exact blocked V10 source-only effect")
                rejected += 1
            else:
                raise AggregateGateError("failed to block a source-only operation")
        fault_controls = synthetic_worker_fault_controls()
        accepted += fault_controls["accepted"]
        rejected += fault_controls["rejected"]
        require(rejected >= 75,
                "require substantial hostile complete-campaign controls")
        observed = dict(effects)
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "synthetic_only": True,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "synthetic_process_fault_controls": fault_controls,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "historical_evidence_owner_count": HISTORICAL_EVIDENCE_OWNER_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "historical_authenticated_reference_count":
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "source_only_effects": observed,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_activations": 0,
        "actual_source_builds": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified_count": 0,
        "winner_selected": False,
    }


def load_worker(
    options: argparse.Namespace,
) -> tuple[types.ModuleType, dict[str, Any]]:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(str(ROOT / WORKER_RELATIVE), flags)
    try:
        information = os.fstat(descriptor)
        require(
            stat.S_ISREG(information.st_mode)
            and 0 < information.st_size <= MAX_SOURCE_BYTES,
            "require the exact independently owned genuine V8 suite worker",
        )
        chunks: list[bytes] = []
        remaining = information.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(block), "reject a truncated V8 source worker")
            chunks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject concealed V8 source worker bytes")
        raw = b"".join(chunks)
        require(
            digest(raw) == options.worker_source_sha256,
            "reject an unpinned, changed, historical, or substituted worker",
        )
    finally:
        os.close(descriptor)
    module = types.ModuleType(
        "_rebar_frozen_p0_candidate_worker_v8_for_v10",
    )
    module.__file__ = str(ROOT / WORKER_RELATIVE)
    sys.modules[module.__name__] = module
    try:
        exec(compile(raw, module.__file__, "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(module.__name__, None)
        raise
    require(
        module.SCHEMA == WORKER_SCHEMA
        and module.RUNNER_SCHEMA == SCHEMA
        and module.SOURCE_RELATIVE == WORKER_RELATIVE
        and module.RUNNER_RELATIVE == SOURCE_RELATIVE
        and module.ORIGINAL_PRODUCER["source"][1]
        == ORIGINAL_PRODUCER_SHA256
        and module.ORIGINAL_PRODUCER["protocol"][1]
        == ORIGINAL_PRODUCER_PROTOCOL_SHA256
        and module.ORIGINAL_PRODUCER["document"][1]
        == ORIGINAL_PRODUCER_DOCUMENT_SHA256
        and tuple(module.SUITES) == SUITES
        and module.CASE_DENOMINATOR == CASE_DENOMINATOR
        and module.HISTORICAL_EVIDENCE_OWNER_COUNT
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and module.HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and module.PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and module.CORRECTED_PUBLIC_RECORDS_SHA256
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and module.HISTORICAL_PUBLIC_RECORDS_SHA256
        == HISTORICAL_PUBLIC_RECORDS_SHA256
        and module.CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and module.CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256
        == CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256
        and tuple(module.CORRECTED_PUBLIC_REFERENCE_PIDS)
        == CORRECTED_PUBLIC_REFERENCE_PIDS
        and module.CORRECTED_PUBLIC_COHORT_CASE_COUNT
        == CORRECTED_PUBLIC_COHORT_CASE_COUNT
        and module.V40_OWNERS["summary"][1] == V40_SUMMARY_SHA256
        and module.V39_OWNERS["summary"][1] == V39_SUMMARY_SHA256
        and module.C15_NATIVE_SHA256 == C15_NATIVE_SHA256
        and tuple(module.FAMILY_NAMES) == FAMILY_NAMES,
        "reject legacy worker, wrong V4 reference, V40, preserved V39, C15, or first-party family",
    )
    return module, {
        "relative": WORKER_RELATIVE,
        "sha256": options.worker_source_sha256,
        "size_bytes": information.st_size,
        "device": information.st_dev,
        "inode": information.st_ino,
    }


def worker_context_options(
    options: argparse.Namespace,
    worker: types.ModuleType,
) -> argparse.Namespace:
    return worker.parse_arguments([
        "--verify-frozen-context",
        "--source-sha256", options.worker_source_sha256,
        "--runner-source-sha256", options.source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--document-sha256", options.document_sha256,
        "--producer-source-sha256", options.producer_source_sha256,
        "--producer-protocol-sha256", options.producer_protocol_sha256,
        "--producer-document-sha256", options.producer_document_sha256,
    ])


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    runtime()
    worker, worker_owner = load_worker(options)
    for relative, expected in (
        (SOURCE_RELATIVE, options.source_sha256),
        (PROTOCOL_RELATIVE, options.protocol_sha256),
        (DOCUMENT_RELATIVE, options.document_sha256),
    ):
        worker.read_owner(relative, expected)
    context = worker.verify_frozen_context(
        worker_context_options(options, worker),
    )
    require(
        type(context) is dict
        and context.get("status") == "PASS"
        and context.get("read_only") is True
        and context.get("suite_count") == SUITE_COUNT
        and context.get("case_execution_denominator") == CASE_DENOMINATOR
        and context.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and context.get("runnable_candidate_family_count") == 1
        and context.get("runnable_candidate_families") == [FAMILY]
        and context.get("six_family_inventory_is_source_only") is True
        and context.get("historical_evidence_owner_count")
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and context.get("historical_authenticated_reference_count")
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and context.get("preserved_failed_campaign_evidence_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and context.get("original_producer_sha256")
        == options.producer_source_sha256
        and context.get("original_producer_protocol_sha256")
        == options.producer_protocol_sha256
        and context.get("original_producer_document_sha256")
        == options.producer_document_sha256
        and context.get("nested_producer_sha256")
        == options.producer_source_sha256
        and context.get("v4_frozen_context_verified_before_activation")
        is True
        and context.get("corrected_public_records_sha256")
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and context.get("historical_public_records_sha256")
        == HISTORICAL_PUBLIC_RECORDS_SHA256
        and context.get("corrected_public_cohort_records_sha256")
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and context.get("corrected_public_cohort_case_ids_sha256")
        == CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256
        and context.get("corrected_public_cohort_case_count")
        == CORRECTED_PUBLIC_COHORT_CASE_COUNT
        and context.get("corrected_public_reference_pids")
        == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and context.get("c_pattern_equality_failure_waived") is False
        and context.get("current_overview_v40_sha256")
        == V40_SUMMARY_SHA256
        and context.get("preserved_overview_v39_sha256")
        == V39_SUMMARY_SHA256
        and context.get("current_c15_native_sha256") == C15_NATIVE_SHA256
        and context.get("reference_archive_bytes_read") == 0
        and context.get("reference_archives_decompressed") == 0
        and context.get("build_archive_bytes_read") == 0
        and context.get("build_archives_decompressed") == 0
        and context.get("actual_candidate_workers") == 0
        and context.get("actual_native_activations") == 0
        and context.get("actual_source_builds") == 0
        and context.get("hidden_cases_read") == 0
        and context.get("clock_samples") == 0
        and context.get("performance") == "NOT MEASURED"
        and context.get("holdout") == "NOT OPENED",
        "reject candidate activation, V4/reference substitution, C15 loss, or V40/V39/P0 history loss",
    )
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "read_only": True,
        "worker_owner": worker_owner,
        "worker_frozen_context": context,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "historical_evidence_owner_count":
            HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "original_producer_sha256": options.producer_source_sha256,
        "original_producer_protocol_sha256":
            options.producer_protocol_sha256,
        "original_producer_document_sha256":
            options.producer_document_sha256,
        "nested_producer_sha256": options.producer_source_sha256,
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "historical_public_records_sha256": HISTORICAL_PUBLIC_RECORDS_SHA256,
        "corrected_public_cohort_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "corrected_public_cohort_case_ids_sha256":
            CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256,
        "corrected_public_cohort_case_count": CORRECTED_PUBLIC_COHORT_CASE_COUNT,
        "corrected_public_reference_pids": list(CORRECTED_PUBLIC_REFERENCE_PIDS),
        "c_pattern_equality_failure_waived": False,
        "current_overview_v40_sha256": V40_SUMMARY_SHA256,
        "preserved_overview_v39_sha256": V39_SUMMARY_SHA256,
        "current_c15_native_sha256": C15_NATIVE_SHA256,
        "reference_archive_bytes_read": 0,
        "reference_archives_decompressed": 0,
        "build_archive_bytes_read": 0,
        "build_archives_decompressed": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified_count": 0,
        "winner_selected": False,
    }

def actual_worker_arguments(
    options: argparse.Namespace,
    suite: str,
) -> list[str]:
    arguments = [
        PINNED_PYTHON,
        "-I",
        "-B",
        str(ROOT / WORKER_RELATIVE),
        "--run",
        "--candidate",
        FAMILY,
        "--suite",
        suite,
        "--label",
        options.label,
        "--build-label",
        options.build_label,
        "--source-sha256",
        options.worker_source_sha256,
        "--runner-source-sha256",
        options.source_sha256,
        "--protocol-sha256",
        options.protocol_sha256,
        "--document-sha256",
        options.document_sha256,
        "--producer-source-sha256",
        options.producer_source_sha256,
        "--producer-protocol-sha256",
        options.producer_protocol_sha256,
        "--producer-document-sha256",
        options.producer_document_sha256,
    ]
    for name in (
        "build-archive",
        "build-receipt",
        "native-engine",
        "native-bridge",
    ):
        value = getattr(options, name.replace("-", "_") + "_sha256")
        arguments.extend((
            "--" + name + "-sha256",
            checked_digest(value, name),
        ))
    return arguments

def _retain_complete_stream(raw: Any, limit: int, name: str) -> dict[str, Any]:
    require(type(raw) is bytes,
            "preserve the actual complete " + name + " process stream")
    retained = raw[:limit]
    return {
        name + "_base64": base64.b64encode(retained).decode("ascii"),
        name + "_bytes": len(raw),
        name + "_sha256": digest(raw),
        name + "_retained_bytes": len(retained),
        name + "_retained_sha256": digest(retained),
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
            "launch only the complete pinned argument vector")
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
        start = subprocess.Popen if launcher is None else launcher
        child = start(arguments, stdin=subprocess.DEVNULL,
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid = getattr(child, "pid", None)
        process.update({
            "started": True,
            "pid": pid if type(pid) is int and pid > 0 else None,
            "failure_phase": "started",
        })
        if on_started is not None:
            on_started(copy.deepcopy(process))
        require(type(pid) is int and pid > 0,
                "record and reject, without erasing, a started child with no valid PID")
        try:
            stdout, stderr = child.communicate(
                timeout=WORKER_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            process["timed_out"] = True
            process["failure_phase"] = "timeout"
            child.kill()
            stdout, stderr = child.communicate()
        process["returncode"] = child.returncode
        process.update(_retain_complete_stream(
            stdout, MAX_CHILD_STDOUT_BYTES, "stdout",
        ))
        process["stdout_capture_completed"] = True
        process.update(_retain_complete_stream(
            stderr, MAX_CHILD_STDERR_BYTES, "stderr",
        ))
        process["stderr_capture_completed"] = True
        if process["stdout_overflow"] or process["stderr_overflow"]:
            process["failure_phase"] = "stream-overflow"
            raise WorkerProcessFailure(
                "retain the full byte count and hash of an oversized worker stream",
                process,
            )
        if process["timed_out"]:
            raise WorkerProcessFailure(
                "retain the real PID and complete streams after a worker timeout",
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
                    process["cleanup_kill_error_type"] = (
                        type(cleanup_error).__qualname__
                    )
                    process["cleanup_kill_error_message"] = (
                        bounded_error(cleanup_error)
                    )
                process["cleanup_reap_attempted"] = True
                try:
                    stdout, stderr = child.communicate()
                    process.update(_retain_complete_stream(
                        stdout, MAX_CHILD_STDOUT_BYTES, "stdout",
                    ))
                    process["stdout_capture_completed"] = True
                    process.update(_retain_complete_stream(
                        stderr, MAX_CHILD_STDERR_BYTES, "stderr",
                    ))
                    process["stderr_capture_completed"] = True
                    process["cleanup_reap_completed"] = True
                except BaseException as cleanup_error:
                    process["cleanup_reap_error_type"] = (
                        type(cleanup_error).__qualname__
                    )
                    process["cleanup_reap_error_message"] = (
                        bounded_error(cleanup_error)
                    )
            process["returncode"] = getattr(child, "returncode", None)
        raise WorkerProcessFailure(
            "preserve the true worker launch or observation failure",
            process,
        ) from error


def campaign_accounting(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    require(
        type(rows) is list
        and len(rows) == SUITE_COUNT
        and [row.get("suite") for row in rows]
        == [name for name, _ in SUITES]
        and [row.get("case_execution_denominator") for row in rows]
        == [count for _, count in SUITES]
        and [row.get("attempt_index") for row in rows]
        == list(range(1, SUITE_COUNT + 1)),
        "retain exactly thirteen distinct original suite observations in frozen order",
    )
    attempted = sum(row.get("actual_worker_attempted") is True for row in rows)
    started = [row for row in rows if row.get("actual_worker_started") is True]
    pids = [row.get("actual_worker_pid") for row in started]
    pid_evidence_valid = (
        all(
            type(pid) is int and pid > 0
            and type(row.get("process")) is dict
            and row["process"].get("started") is True
            and row["process"].get("pid") == pid
            and row.get("actual_worker_attempted") is True
            for row, pid in zip(started, pids, strict=True)
        )
        and len(set(pids)) == len(pids)
        and all(
            row.get("actual_worker_started") is True
            or row.get("actual_worker_pid") is None
            for row in rows
        )
    )
    completed = sum(
        row.get("all_original_records_and_mismatches_preserved") is True
        and row.get("genuine_original_suite") is True
        and row.get("status") in ("PASS", "FAIL")
        and type(row.get("mismatch_count")) is int
        and row.get("actual_worker_started") is True
        for row in rows
    )
    known_mismatches = sum(
        row["mismatch_count"]
        for row in rows
        if row.get("genuine_original_suite") is True
        and type(row.get("mismatch_count")) is int
    )
    infrastructure = [
        row["suite"] for row in rows
        if row.get("failure_class") == "INFRASTRUCTURE FAILURE"
    ]
    full_mismatch_count = (
        known_mismatches
        if completed == SUITE_COUNT and not infrastructure and pid_evidence_valid
        else "NOT MEASURED"
    )
    return {
        "planned_suite_count": SUITE_COUNT,
        "recorded_suite_row_count": len(rows),
        "actual_worker_launch_attempt_count": attempted,
        "actual_candidate_workers": len(started),
        "actual_candidate_worker_pids": pids,
        "actual_worker_pids_are_distinct": pid_evidence_valid,
        "completed_suite_count": completed,
        "infrastructure_failure_suites": infrastructure,
        "infrastructure_failure_count": len(infrastructure),
        "observed_partial_semantic_mismatch_count": known_mismatches,
        "semantic_mismatch_count": full_mismatch_count,
        "semantic_mismatch_count_complete": full_mismatch_count != "NOT MEASURED",
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
                raise subprocess.TimeoutExpired(("synthetic-worker",), 1)
            if self.mode == "post-spawn":
                raise OSError("synthetic post-spawn stream failure")
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

    accepted = rejected = 0
    starts: list[dict[str, Any]] = []

    def launcher(mode: str, pid: Any = 8101) -> Any:
        def launch(*args: Any, **kwargs: Any) -> FakeChild:
            if mode == "failed-spawn":
                raise OSError("synthetic failed process launch")
            return FakeChild(mode, pid)
        return launch

    success = worker_process(
        ["synthetic-worker"], launcher=launcher("success"),
        on_started=starts.append,
    )
    require(
        success.get("attempted") is True
        and success.get("started") is True
        and success.get("pid") == 8101
        and success.get("returncode") == 0
        and success.get("timed_out") is False
        and success.get("stdout_bytes") == 3
        and success.get("stdout_sha256") == digest(b"{}\n")
        and success.get("stdout_complete") is True
        and success.get("stderr_bytes") == 0
        and len(starts) == 1 and starts[0].get("pid") == 8101,
        "prove exact synthetic started PID, early snapshot, and complete stream capture",
    )
    accepted += 1
    for mode in (
        "failed-spawn", "post-spawn", "timeout",
        "stdout-overflow", "stderr-overflow", "missing-pid",
    ):
        pid: Any = None if mode == "missing-pid" else 8200 + rejected
        try:
            worker_process(["synthetic-worker"], launcher=launcher(mode, pid))
        except WorkerProcessFailure as error:
            observed = error.process
            require(observed.get("attempted") is True,
                    "never erase a genuine synthetic launch attempt")
            if mode == "failed-spawn":
                require(observed.get("started") is False
                        and observed.get("pid") is None,
                        "never invent a process identifier for a failed launch")
            elif mode == "missing-pid":
                require(observed.get("started") is True
                        and observed.get("pid") is None
                        and observed.get("cleanup_kill_attempted") is True
                        and observed.get("cleanup_reap_completed") is True,
                        "retain and reap a genuinely launched worker with missing PID evidence")
            else:
                require(observed.get("started") is True
                        and observed.get("pid") == pid,
                        "preserve the real child identifier on every later failure")
            if mode == "timeout":
                require(observed.get("timed_out") is True
                        and observed.get("failure_phase") == "timeout"
                        and observed.get("returncode") == -9,
                        "retain timeout, forced termination, PID and both streams")
            if mode == "post-spawn":
                require(observed.get("cleanup_kill_attempted") is True
                        and observed.get("cleanup_reap_attempted") is True
                        and observed.get("cleanup_reap_completed") is True
                        and observed.get("returncode") == -9,
                        "always kill and reap a worker after post-launch capture failure")
            if mode == "stdout-overflow":
                raw = b"x" * (MAX_CHILD_STDOUT_BYTES + 1)
                require(observed.get("stdout_overflow") is True
                        and observed.get("stdout_bytes") == len(raw)
                        and observed.get("stdout_sha256") == digest(raw)
                        and observed.get("stdout_retained_bytes")
                        == MAX_CHILD_STDOUT_BYTES,
                        "retain the complete oversized stdout length and hash")
            if mode == "stderr-overflow":
                raw = b"y" * (MAX_CHILD_STDERR_BYTES + 1)
                require(observed.get("stderr_overflow") is True
                        and observed.get("stderr_bytes") == len(raw)
                        and observed.get("stderr_sha256") == digest(raw)
                        and observed.get("stderr_retained_bytes")
                        == MAX_CHILD_STDERR_BYTES,
                        "retain the complete oversized stderr length and hash")
            rejected += 1
        else:
            raise AggregateGateError("accepted synthetic worker fault: " + mode)

    valid_rows: list[dict[str, Any]] = []
    for index, (name, count) in enumerate(SUITES, start=1):
        pid = 8300 + index
        valid_rows.append({
            "suite": name,
            "case_execution_denominator": count,
            "attempt_index": index,
            "actual_worker_attempted": True,
            "actual_worker_started": True,
            "actual_worker_pid": pid,
            "status": "PASS",
            "genuine_original_suite": True,
            "mismatch_count": 0,
            "failure_class": "PASS",
            "process": {"attempted": True, "started": True, "pid": pid},
            "all_original_records_and_mismatches_preserved": True,
        })
    complete = campaign_accounting(valid_rows)
    require(complete.get("completed_suite_count") == SUITE_COUNT
            and complete.get("actual_worker_launch_attempt_count") == SUITE_COUNT
            and complete.get("actual_candidate_workers") == SUITE_COUNT
            and complete.get("actual_worker_pids_are_distinct") is True
            and complete.get("semantic_mismatch_count") == 0,
            "prove thirteen independently and completely observed fake workers")
    accepted += 1
    partial = copy.deepcopy(valid_rows)
    partial[5].update({
        "actual_worker_attempted": False,
        "actual_worker_started": False,
        "actual_worker_pid": None,
        "status": "FAIL",
        "genuine_original_suite": False,
        "mismatch_count": None,
        "failure_class": "INFRASTRUCTURE FAILURE",
        "process": None,
        "all_original_records_and_mismatches_preserved": False,
    })
    partial_metrics = campaign_accounting(partial)
    require(partial_metrics.get("planned_suite_count") == 13
            and partial_metrics.get("recorded_suite_row_count") == 13
            and partial_metrics.get("actual_worker_launch_attempt_count") == 12
            and partial_metrics.get("actual_candidate_workers") == 12
            and partial_metrics.get("completed_suite_count") == 12
            and partial_metrics.get("semantic_mismatch_count") == "NOT MEASURED"
            and partial_metrics.get("infrastructure_failure_count") == 1,
            "never count an unstarted suite or infer complete mismatch totals")
    accepted += 1
    duplicated = copy.deepcopy(valid_rows)
    duplicated[1]["actual_worker_pid"] = duplicated[0]["actual_worker_pid"]
    duplicated[1]["process"]["pid"] = duplicated[0]["actual_worker_pid"]
    collision = campaign_accounting(duplicated)
    require(collision.get("actual_worker_pids_are_distinct") is False
            and collision.get("semantic_mismatch_count") == "NOT MEASURED",
            "never accept a duplicate child PID or claim a full mismatch total")
    rejected += 1
    missing = copy.deepcopy(valid_rows)
    missing[3]["actual_worker_pid"] = None
    missing_metrics = campaign_accounting(missing)
    require(missing_metrics.get("actual_worker_pids_are_distinct") is False
            and missing_metrics.get("semantic_mismatch_count") == "NOT MEASURED",
            "never infer the identity of a started worker")
    rejected += 1
    for invalid in (valid_rows[:-1], valid_rows + [copy.deepcopy(valid_rows[0])]):
        try:
            campaign_accounting(invalid)
        except AggregateGateError:
            rejected += 1
        else:
            raise AggregateGateError("accepted an omitted or duplicated P0 suite")

    class FakePublicationWorker:
        EVIDENCE_RELATIVE = "oracle/phase2/evidence"

        def __init__(self, failed_stage: str | None = None) -> None:
            self.failed_stage = failed_stage
            self.snapshots: list[dict[str, Any]] = []

        @staticmethod
        def checked_label(value: Any, label: str = "label") -> str:
            require(type(value) is str and bool(value)
                    and value.replace("-", "").replace("_", "").isalnum(),
                    "reject an invalid fake durable journal label")
            return value

        @staticmethod
        def canonical(value: Any) -> bytes:
            return canonical(value)

        def create_private_owner(
            self, relative: str, raw: bytes,
        ) -> dict[str, Any]:
            if (self.failed_stage is not None
                    and relative.endswith("-" + self.failed_stage + ".json")):
                raise OSError("synthetic durable " + self.failed_stage + " failure")
            owner = {
                "relative": relative,
                "sha256": digest(raw),
                "size_bytes": len(raw),
                "synthetic_only": True,
            }
            self.snapshots.append(owner)
            return owner

        @staticmethod
        def exact_json(raw: bytes, label: str) -> dict[str, Any]:
            parsed = json.loads(raw.decode("ascii"))
            require(type(parsed) is dict,
                    "reject malformed synthetic publication " + label)
            return parsed

    options = argparse.Namespace(
        candidate=FAMILY,
        label="synthetic-fault",
        build_label="synthetic-c15",
        source_sha256="a" * 64,
        worker_source_sha256="b" * 64,
        protocol_sha256="c" * 64,
        document_sha256="d" * 64,
        producer_source_sha256=ORIGINAL_PRODUCER_SHA256,
        producer_protocol_sha256=ORIGINAL_PRODUCER_PROTOCOL_SHA256,
        producer_document_sha256=ORIGINAL_PRODUCER_DOCUMENT_SHA256,
        build_archive_sha256="e" * 64,
        build_receipt_sha256="f" * 64,
        native_engine_sha256=C15_NATIVE_SHA256,
        native_bridge_sha256=C15_NATIVE_SHA256,
    )
    for stage in (None, "pre-spawn", "started", "failed"):
        fake = FakePublicationWorker(stage)
        row = observe_worker(
            options, fake, SUITES[0], attempt_index=1,
            launcher=launcher("success", 8700 + rejected),
            include_traceback=False,
        )
        require(row.get("status") == "FAIL"
                and row.get("failure_class") == "INFRASTRUCTURE FAILURE",
                "never accept an invalid worker publication or journal")
        if stage == "pre-spawn":
            require(row.get("actual_worker_attempted") is False
                    and row.get("actual_worker_started") is False
                    and row.get("actual_worker_pid") is None,
                    "never launch when the durable pre-spawn snapshot fails")
        else:
            require(row.get("actual_worker_attempted") is True
                    and row.get("actual_worker_started") is True
                    and type(row.get("actual_worker_pid")) is int,
                    "preserve the true launched PID after publication or journal failure")
        if stage == "failed":
            require(any(type(item) is dict
                        and item.get("failure_phase")
                        == "failure-snapshot-publication"
                        for item in row.get("durable_attempt_snapshots", [])),
                    "retain a genuine failed durable recovery publication")
        rejected += 1
    for phase in (
        "canonical-serialization",
        "oversized-report",
        "archive-publication",
        "receipt-publication",
        "public-write",
        "public-flush",
    ):
        ledger = new_actual_effect_ledger(options)
        ledger.update({
            "phase": phase,
            "attempted_suite_count": 4,
            "started_suite_count": 3,
            "completed_suite_count": 2,
            "actual_candidate_workers": 3,
            "actual_candidate_worker_pids": [9201, 9202, 9203],
            "actual_native_activations": 1,
            "actual_native_promotions": 1,
            "actual_source_builds": 1,
            "actual_reference_workers": 2,
            "worker_attempts": [{"suite": SUITES[0][0], "pid": 9201}],
            "durable_attempt_snapshots": [
                {"relative": "synthetic-pre-spawn", "sha256": "a" * 64},
            ],
        })
        try:
            if phase == "canonical-serialization":
                ledger["public_report_serialization_attempted"] = True
                bounded_public_report({"not_serializable": object()}, 128)
            elif phase == "oversized-report":
                ledger["public_report_serialization_attempted"] = True
                bounded_public_report({"padding": "oversized"}, 8)
            else:
                flag = {
                    "archive-publication": "archive_publication_attempted",
                    "receipt-publication": "receipt_publication_attempted",
                    "public-write": "public_report_write_attempted",
                    "public-flush": "public_report_flush_attempted",
                }[phase]
                ledger[flag] = True
                raise OSError("synthetic first " + phase + " failure")
        except (AggregateGateError, OSError) as error:
            failure = actual_entry_failure_result(error, ledger)
            require(
                failure.get("status") == "FAIL"
                and failure.get("phase") == phase
                and failure.get("attempted_suite_count") == 4
                and failure.get("started_suite_count") == 3
                and failure.get("completed_suite_count") == 2
                and failure.get("actual_candidate_workers") == 3
                and failure.get("actual_candidate_worker_pids")
                == [9201, 9202, 9203]
                and failure.get("actual_native_activations") == 1
                and failure.get("actual_native_promotions") == 1
                and failure.get("actual_source_builds") == 1
                and failure.get("actual_reference_workers") == 2
                and len(failure.get("worker_attempts", [])) == 1
                and len(failure.get("durable_attempt_snapshots", [])) == 1
                and failure.get("publication_status") == "FAIL"
                and failure.get("semantic_mismatch_count") == "NOT MEASURED"
                and failure.get("source_only_zero_effects_claimed") is False,
                "never erase started workers, native effects or first failure after " + phase,
            )
            rejected += 1
        else:
            raise AggregateGateError("accepted a synthetic aggregate entry fault")
    return {"accepted": accepted, "rejected": rejected}


def verify_streamed_suite(worker: types.ModuleType,
                          publication: dict[str, Any],
                          suite: tuple[str, int], label: str) -> dict[str, Any]:
    name, count = suite
    require(publication.get("schema") == WORKER_SCHEMA + "-published-original-suite"
            and publication.get("candidate_family") == FAMILY
            and publication.get("suite") == name
            and publication.get("label") == label
            and publication.get("case_execution_denominator") == count
            and publication.get("original_producer_sha256")
            == ORIGINAL_PRODUCER_SHA256
            and publication.get("all_original_records_and_mismatches_preserved")
            is True
            and publication.get("performance") == "NOT MEASURED"
            and publication.get("holdout") == "NOT OPENED",
            "reject a substituted or incomplete original suite publication")
    archive = publication.get("archive")
    receipt_owner = publication.get("receipt")
    require(type(archive) is dict and type(receipt_owner) is dict,
            "require independent exact original suite owners")
    expected_archive, expected_receipt = worker.suite_evidence_names(name, label)
    compressed, actual_archive = worker.read_owner(
        expected_archive, archive.get("sha256"),
        maximum=worker.MAX_COMPRESSED_SUITE_BYTES,
        size=archive.get("size_bytes"), private=True)
    raw_receipt, actual_receipt = worker.read_owner(
        expected_receipt, receipt_owner.get("sha256"),
        maximum=MAX_SOURCE_BYTES,
        size=receipt_owner.get("size_bytes"), private=True)
    require((actual_archive["device"], actual_archive["inode"])
            != (actual_receipt["device"], actual_receipt["inode"]),
            "reject shared or substituted original suite owner identities")
    receipt = worker.exact_json(raw_receipt, "actual original suite receipt")
    require(receipt.get("schema")
            == WORKER_SCHEMA + "-durable-suite-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == publication.get("status")
            and receipt.get("candidate_family") == FAMILY
            and receipt.get("suite") == name
            and receipt.get("label") == label
            and receipt.get("case_execution_denominator") == count
            and receipt.get("phase_one_case_execution_denominator")
            == CASE_DENOMINATOR
            and receipt.get("original_producer_sha256")
            == ORIGINAL_PRODUCER_SHA256
            and receipt.get("original_c_source_sha256") == ORIGINAL_C_SHA256
            and receipt.get("derived_c_source_sha256") == DERIVED_C_SHA256
            and receipt.get("uncompressed_sha256")
            == publication.get("uncompressed_sha256")
            and receipt.get("uncompressed_bytes")
            == publication.get("uncompressed_bytes")
            and receipt.get("mismatch_count") == publication.get("mismatch_count")
            and receipt.get("all_original_records_and_mismatches_preserved")
            is True,
            "never treat publication success as candidate compatibility")
    full_hash = hashlib.sha256()
    full_size = 0
    with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as source:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            full_size += len(block)
            require(full_size <= worker.MAX_UNCOMPRESSED_SUITE_BYTES,
                    "reject an unbounded or truncated real suite report")
            full_hash.update(block)
    require(full_size == receipt["uncompressed_bytes"]
            and full_hash.hexdigest() == receipt["uncompressed_sha256"],
            "authenticate every byte of the complete streamed suite report")
    return {"archive": actual_archive, "receipt": actual_receipt,
            "receipt_document": receipt, "uncompressed_bytes": full_size,
            "uncompressed_sha256": full_hash.hexdigest()}


def publish_attempt_snapshot(
    worker: types.ModuleType,
    options: argparse.Namespace,
    suite: tuple[str, int],
    index: int,
    stage: str,
    process: dict[str, Any],
) -> dict[str, Any]:
    name, count = suite
    require(type(index) is int and 1 <= index <= SUITE_COUNT
            and stage in ("pre-spawn", "started", "completed", "failed"),
            "publish only a bounded immutable original worker-attempt stage")
    record = {
        "schema": SCHEMA + "-durable-worker-attempt-snapshot",
        "status": "PASS" if stage in ("pre-spawn", "started", "completed") else "FAIL",
        "candidate_family": options.candidate,
        "label": options.label,
        "suite": name,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "case_execution_denominator": count,
        "attempt_index": index,
        "stage": stage,
        "process": copy.deepcopy(process),
        "original_producer_sha256": ORIGINAL_PRODUCER_SHA256,
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }
    relative = (
        worker.EVIDENCE_RELATIVE + "/frozen-p0-candidate-v10-"
        + worker.checked_label(options.candidate, "candidate family")
        + "-" + worker.checked_label(options.label)
        + "-" + format(index, "02d") + "-" + name + "-" + stage + ".json"
    )
    return worker.create_private_owner(relative, worker.canonical(record))


def observe_worker(
    options: argparse.Namespace,
    worker: types.ModuleType,
    suite: tuple[str, int],
    *,
    attempt_index: int,
    launcher: Any | None = None,
    include_traceback: bool = True,
    effect_ledger: dict[str, Any] | None = None,
) -> dict[str, Any]:
    name, count = suite
    process: dict[str, Any] | None = None
    journal: list[dict[str, Any]] = []
    attempt_record: dict[str, Any] = {
        "suite": name,
        "case_execution_denominator": count,
        "attempt_index": attempt_index,
        "actual_worker_attempted": False,
        "actual_worker_started": False,
        "actual_worker_pid": None,
        "process": None,
        "durable_attempt_snapshots": journal,
        "first_failure": None,
        "fully_observed": False,
    }
    if effect_ledger is not None:
        effect_ledger["phase"] = "worker-pre-spawn"
        effect_ledger["worker_attempts"].append(attempt_record)
    try:
        before_start = {
            "attempted": False, "started": False, "pid": None,
            "failure_phase": "pre-spawn",
        }
        journal.append(publish_attempt_snapshot(
            worker, options, suite, attempt_index, "pre-spawn", before_start,
        ))
        if effect_ledger is not None:
            effect_ledger["durable_attempt_snapshots"].append(journal[-1])
            effect_ledger["attempted_suite_count"] += 1
            effect_ledger["phase"] = "worker-launch"
            attempt_record["actual_worker_attempted"] = True

        def retain_started(started: dict[str, Any]) -> None:
            nonlocal process
            process = copy.deepcopy(started)
            attempt_record["process"] = copy.deepcopy(started)
            attempt_record["actual_worker_started"] = True
            attempt_record["actual_worker_pid"] = started.get("pid")
            if effect_ledger is not None:
                effect_ledger["phase"] = "worker-started"
                effect_ledger["started_suite_count"] += 1
                effect_ledger["actual_candidate_workers"] += 1
                effect_ledger["actual_candidate_worker_pids"].append(
                    started.get("pid"),
                )
            journal.append(publish_attempt_snapshot(
                worker, options, suite, attempt_index, "started", started,
            ))
            if effect_ledger is not None:
                effect_ledger["durable_attempt_snapshots"].append(journal[-1])

        process = worker_process(
            actual_worker_arguments(options, name),
            launcher=launcher,
            on_started=retain_started,
        )
        journal.append(publish_attempt_snapshot(
            worker, options, suite, attempt_index, "completed", process,
        ))
        attempt_record["process"] = copy.deepcopy(process)
        if effect_ledger is not None:
            effect_ledger["durable_attempt_snapshots"].append(journal[-1])
            effect_ledger["phase"] = "worker-publication-verification"
        raw = base64.b64decode(process["stdout_base64"], validate=True)
        publication = worker.exact_json(raw, "complete original worker stdout")
        evidence = verify_streamed_suite(worker, publication, suite, options.label)
        actual_status = publication.get("status")
        mismatch_count = publication.get("mismatch_count")
        genuine = evidence["receipt_document"].get("genuine_original_suite")
        require(actual_status in ("PASS", "FAIL")
                and process["returncode"] == (0 if actual_status == "PASS" else 1)
                and process["timed_out"] is False
                and genuine in (True, False)
                and (actual_status != "PASS"
                     or genuine is True and mismatch_count == 0),
                "reject an unproven worker return code or suite classification")
        attempt_record["fully_observed"] = True
        if effect_ledger is not None:
            effect_ledger["completed_suite_count"] += 1
            effect_ledger["phase"] = "worker-fully-observed"
        return {
            "suite": name, "case_execution_denominator": count,
            "actual_worker_attempted": True,
            "actual_worker_started": True,
            "actual_worker_pid": process["pid"],
            "attempt_index": attempt_index,
            "status": actual_status,
            "genuine_original_suite": genuine,
            "mismatch_count": mismatch_count,
            "failure_class": (
                "PASS" if actual_status == "PASS"
                else "SEMANTIC MISMATCH" if genuine is True
                else "INFRASTRUCTURE FAILURE"
            ),
            "process": process,
            "durable_attempt_snapshots": journal,
            "suite_archive": evidence["archive"],
            "suite_receipt": evidence["receipt"],
            "uncompressed_bytes": evidence["uncompressed_bytes"],
            "uncompressed_sha256": evidence["uncompressed_sha256"],
            "all_original_records_and_mismatches_preserved": True,
        }
    except BaseException as error:
        attempt_record["first_failure"] = {
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
        }
        if isinstance(error, WorkerProcessFailure):
            process = copy.deepcopy(error.process)
        if type(process) is dict:
            attempt_record["process"] = copy.deepcopy(process)
            attempt_record["actual_worker_attempted"] = (
                process.get("attempted") is True
            )
            attempt_record["actual_worker_started"] = (
                process.get("started") is True
            )
            attempt_record["actual_worker_pid"] = process.get("pid")
        if journal:
            try:
                journal.append(publish_attempt_snapshot(
                    worker, options, suite, attempt_index, "failed",
                    process if process is not None else {
                        "attempted": False, "started": False, "pid": None,
                        "failure_phase": "pre-spawn",
                    },
                ))
                if effect_ledger is not None:
                    effect_ledger["durable_attempt_snapshots"].append(
                        journal[-1],
                    )
            except BaseException as journal_error:
                journal.append({
                    "status": "FAIL",
                    "failure_phase": "failure-snapshot-publication",
                    "error_type": type(journal_error).__qualname__,
                    "error_message": bounded_error(journal_error),
                })
        return {
            "suite": name, "case_execution_denominator": count,
            "actual_worker_attempted":
                type(process) is dict and process.get("attempted") is True,
            "actual_worker_started":
                type(process) is dict and process.get("started") is True,
            "actual_worker_pid":
                process.get("pid") if type(process) is dict else None,
            "attempt_index": attempt_index,
            "status": "FAIL", "genuine_original_suite": False,
            "mismatch_count": None,
            "failure_class": "INFRASTRUCTURE FAILURE",
            "process": process,
            "durable_attempt_snapshots": journal,
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "traceback": (
                traceback.format_exception(
                    type(error), error, error.__traceback__,
                )
                if include_traceback
                else [type(error).__qualname__ + ": " + bounded_error(error) + "\n"]
            ),
            "all_original_records_and_mismatches_preserved": False,
        }


def verify_unchanged_native(
    worker: types.ModuleType,
    original: Mapping[str, Any],
) -> dict[str, Any]:
    _, current = worker.read_owner(
        worker.NATIVE_RELATIVE, C15_NATIVE_SHA256,
        maximum=worker.MAX_BINARY_BYTES, size=163176,
    )
    require(
        type(original) is dict
        and all(original.get(key) == current.get(key)
                for key in ("relative", "sha256", "size_bytes", "device", "inode")),
        "never publish if any original live first-party native owner was changed",
    )
    return {
        "status": "PASS",
        "route": "NO NATIVE MUTATION; VERIFIED ORIGINAL INODE UNCHANGED",
        "family": FAMILY,
        "target": worker.NATIVE_RELATIVE,
        "native_owner": current,
        "native_activation_started": False,
        "native_promotion_started": False,
        "native_target_mutated": False,
    }


def publish_aggregate(
    worker: types.ModuleType,
    report: dict[str, Any],
    options: argparse.Namespace,
    effect_ledger: dict[str, Any],
) -> dict[str, Any]:
    effect_ledger["phase"] = "aggregate-serialization"
    effect_ledger["public_report_serialization_attempted"] = True
    compressed, expanded_sha, expanded_bytes = worker.stream_gzip(report)
    require(expanded_bytes <= MAX_PUBLIC_REPORT_BYTES,
            "retain the strict 32 MiB outer campaign report cap")
    stem = (worker.EVIDENCE_RELATIVE + "/frozen-p0-candidate-v10-c-"
            + worker.checked_label(options.label))
    if report["status"] == "FAIL":
        stem += "-failures"
    effect_ledger["phase"] = "aggregate-archive-publication"
    effect_ledger["archive_publication_attempted"] = True
    archive = worker.create_private_owner(stem + ".json.gz", compressed)
    effect_ledger["archive_owner"] = copy.deepcopy(archive)
    receipt_document = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "candidate_status": report["status"],
        "candidate_family": options.candidate, "label": options.label,
        "suite_count": SUITE_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "case_execution_denominator": CASE_DENOMINATOR,
        "completed_suite_count": report["completed_suite_count"],
        "attempted_suite_count": report["attempted_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_candidate_worker_pids": report["actual_candidate_worker_pids"],
        "archive": archive,
        "uncompressed_sha256": expanded_sha,
        "uncompressed_bytes": expanded_bytes,
        "all_original_suite_evidence_preserved":
        report["all_original_suite_evidence_preserved"],
        "restoration": report["restoration"],
        "original_producer_sha256": ORIGINAL_PRODUCER_SHA256,
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "corrected_public_cohort_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "c_pattern_equality_failure_waived": False,
        "historical_evidence_owner_count": HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    effect_ledger["phase"] = "aggregate-receipt-publication"
    effect_ledger["receipt_publication_attempted"] = True
    receipt = worker.create_private_owner(
        stem + "-publication-receipt.json", worker.canonical(receipt_document))
    effect_ledger["receipt_owner"] = copy.deepcopy(receipt)
    effect_ledger["publication_status"] = "PASS"
    effect_ledger["phase"] = "aggregate-published"
    return {
        "schema": SCHEMA + "-published-complete-candidate",
        "status": report["status"], "candidate_family": options.candidate,
        "label": options.label,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "completed_suite_count": report["completed_suite_count"],
        "attempted_suite_count": report["attempted_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_candidate_worker_pids": report["actual_candidate_worker_pids"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "archive": archive, "receipt": receipt,
        "restoration_status": report["restoration"]["status"],
        "all_original_suite_evidence_preserved":
        report["all_original_suite_evidence_preserved"],
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def run_actual_candidate(
    options: argparse.Namespace,
    effect_ledger: dict[str, Any],
) -> dict[str, Any]:
    require(type(effect_ledger) is dict
            and effect_ledger.get("schema")
            == SCHEMA + "-authorized-actual-effect-ledger",
            "install the durable truthful actual effect ledger before preflight")
    effect_ledger["phase"] = "worker-source-context-preflight"
    worker, _ = load_worker(options)
    first_worker_arguments = actual_worker_arguments(options, SUITES[0][0])
    worker_options = worker.parse_arguments(first_worker_arguments[4:])
    context = worker.verify_live_worker_context(worker_options)
    require(
        context.get("status") == "PASS"
        and context.get("v4_frozen_context_called_after_activation") is False
        and context.get("corrected_public_records_sha256")
        == CORRECTED_PUBLIC_RECORDS_SHA256,
        "authenticate corrected V4 and both real references before any candidate",
    )
    build = worker.authenticate_v15_build(worker_options)
    approval = worker.authenticate_live_c15_native(worker_options, build)
    effect_ledger["phase"] = "verified-live-c15-before-worker-launch"
    rows: list[dict[str, Any]] = []
    outer_failures: list[dict[str, Any]] = []
    for index, suite in enumerate(SUITES, start=1):
        try:
            row = observe_worker(
                options, worker, suite, attempt_index=index,
                effect_ledger=effect_ledger,
            )
        except BaseException as error:
            remembered = next((
                item for item in reversed(effect_ledger["worker_attempts"])
                if item.get("suite") == suite[0]
                and item.get("attempt_index") == index
            ), None)
            previous_process = (
                remembered.get("process")
                if type(remembered) is dict else None
            )
            first_failure = (
                remembered.get("first_failure")
                if type(remembered) is dict else None
            )
            row = {
                "suite": suite[0],
                "case_execution_denominator": suite[1],
                "attempt_index": index,
                "actual_worker_attempted": (
                    type(remembered) is dict
                    and remembered.get("actual_worker_attempted") is True
                ),
                "actual_worker_started": (
                    type(remembered) is dict
                    and remembered.get("actual_worker_started") is True
                ),
                "actual_worker_pid": (
                    remembered.get("actual_worker_pid")
                    if type(remembered) is dict else None
                ),
                "status": "FAIL",
                "genuine_original_suite": False,
                "mismatch_count": None,
                "failure_class": "INFRASTRUCTURE FAILURE",
                "failure_phase": "attempt-recording",
                "process": previous_process,
                "durable_attempt_snapshots": (
                    copy.deepcopy(remembered.get("durable_attempt_snapshots", []))
                    if type(remembered) is dict else []
                ),
                "first_failure": first_failure,
                "error_type": type(error).__qualname__,
                "error_message": bounded_error(error),
                "traceback": traceback.format_exception(
                    type(error), error, error.__traceback__,
                ),
                "all_original_records_and_mismatches_preserved": False,
            }
            outer_failures.append({
                "suite": suite[0],
                "error_type": type(error).__qualname__,
                "error_message": bounded_error(error),
            })
        rows.append(row)
    try:
        restoration = verify_unchanged_native(
            worker, approval["native_owner"],
        )
    except BaseException as error:
        restoration = {
            "status": "FAIL",
            "route": "ORIGINAL NATIVE IDENTITY COULD NOT BE VERIFIED",
            "native_activation_started": False,
            "native_promotion_started": False,
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__,
            ),
        }
        outer_failures.append({
            "suite": None,
            "failure_phase": "verify-unchanged-native",
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
        })
    passed = [row for row in rows if row.get("status") == "PASS"]
    passing_count = sum(row["case_execution_denominator"] for row in passed)
    accounting = campaign_accounting(rows)
    attempted = accounting["actual_worker_launch_attempt_count"]
    started_count = accounting["actual_candidate_workers"]
    completed = accounting["completed_suite_count"]
    unique_pids = accounting["actual_worker_pids_are_distinct"]
    infrastructure = accounting["infrastructure_failure_suites"]
    preserved = len(rows) == SUITE_COUNT and all(
        row.get("all_original_records_and_mismatches_preserved") is True
        for row in rows
    )
    status = (
        "PASS"
        if len(passed) == SUITE_COUNT
        and attempted == SUITE_COUNT
        and started_count == SUITE_COUNT
        and unique_pids
        and passing_count == CASE_DENOMINATOR
        and preserved
        and not infrastructure
        and not outer_failures
        and restoration.get("status") == "PASS"
        else "FAIL"
    )
    report = {
        "schema": SCHEMA + "-complete-original-candidate-evaluation",
        "status": status,
        "candidate_family": options.candidate,
        "label": options.label,
        "suite_count": SUITE_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "planned_suite_count": accounting["planned_suite_count"],
        "recorded_suite_row_count": accounting["recorded_suite_row_count"],
        "attempted_suite_count": attempted,
        "started_suite_count": started_count,
        "completed_suite_count": completed,
        "suite_results": rows,
        "verified_passing_case_count": passing_count,
        "semantic_mismatch_count": accounting["semantic_mismatch_count"],
        "observed_partial_semantic_mismatch_count":
            accounting["observed_partial_semantic_mismatch_count"],
        "semantic_mismatch_count_complete":
            accounting["semantic_mismatch_count_complete"],
        "infrastructure_failure_count":
            accounting["infrastructure_failure_count"],
        "infrastructure_failure_suites": infrastructure,
        "all_original_suite_evidence_preserved": preserved,
        "candidate_qualified": status == "PASS",
        "actual_worker_launch_attempt_count": attempted,
        "actual_candidate_workers": started_count,
        "actual_candidate_worker_pids":
            accounting["actual_candidate_worker_pids"],
        "actual_worker_pids_are_distinct": unique_pids,
        "original_producer_sha256": options.producer_source_sha256,
        "original_producer_protocol_sha256":
            options.producer_protocol_sha256,
        "original_producer_document_sha256":
            options.producer_document_sha256,
        "nested_producer_sha256": options.producer_source_sha256,
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "historical_public_records_sha256": HISTORICAL_PUBLIC_RECORDS_SHA256,
        "corrected_public_cohort_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "c_pattern_equality_failure_waived": False,
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "actual_v15_build_archive_sha256":
            build["archive_owner"]["sha256"],
        "actual_v15_build_receipt_sha256":
            build["receipt_owner"]["sha256"],
        "actual_v15_native_output_sha256": C15_NATIVE_SHA256,
        "runner_activates_native": False,
        "runner_mutates_native": False,
        "restoration": restoration,
        "outer_failures": outer_failures,
        "historical_evidence_owner_count":
            HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return publish_aggregate(worker, report, options, effect_ledger)


def parse_arguments(
    arguments: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=(FAMILY,))
    parser.add_argument("--label")
    parser.add_argument("--build-label")
    for name in (
        "source",
        "worker-source",
        "protocol",
        "document",
        "producer-source",
        "producer-protocol",
        "producer-document",
        "build-archive",
        "build-receipt",
        "native-engine",
        "native-bridge",
    ):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    pins = (
        "source_sha256",
        "worker_source_sha256",
        "protocol_sha256",
        "document_sha256",
        "producer_source_sha256",
        "producer_protocol_sha256",
        "producer_document_sha256",
    )
    actual = (
        "candidate",
        "label",
        "build_label",
        "build_archive_sha256",
        "build_receipt_sha256",
        "native_engine_sha256",
        "native_bridge_sha256",
    )
    if options.self_test:
        require(
            all(getattr(options, name) is None for name in (*pins, *actual)),
            "synthetic self-test cannot authorize V4 or candidate execution",
        )
        return options
    for name in pins:
        checked_digest(getattr(options, name), name)
    require(
        options.producer_source_sha256 == ORIGINAL_PRODUCER_SHA256
        and options.producer_protocol_sha256
        == ORIGINAL_PRODUCER_PROTOCOL_SHA256
        and options.producer_document_sha256
        == ORIGINAL_PRODUCER_DOCUMENT_SHA256,
        "reject legacy, missing, changed, or cross-worker corrected V4 source owners",
    )
    if options.verify_frozen_context:
        require(
            all(getattr(options, name) is None for name in actual),
            "read-only context cannot activate or run a candidate",
        )
        return options
    require(
        all(getattr(options, name) is not None for name in actual)
        and options.candidate == FAMILY,
        "fail closed unless every exact actual first-party C15 native and build owner is pinned",
    )
    for name in actual:
        if name.endswith("_sha256"):
            checked_digest(getattr(options, name), name)
    return options

def main(arguments: Sequence[str] | None = None) -> int:
    options: argparse.Namespace | None = None
    effect_ledger: dict[str, Any] | None = None
    try:
        runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = source_self_test()
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            effect_ledger = new_actual_effect_ledger(options)
            result = run_actual_candidate(options, effect_ledger)
        if effect_ledger is not None:
            effect_ledger["phase"] = "public-report-serialization"
            effect_ledger["public_report_serialization_attempted"] = True
        raw = bounded_public_report(result)
        if effect_ledger is not None:
            effect_ledger["phase"] = "public-report-write"
            effect_ledger["public_report_write_attempted"] = True
        sys.stdout.buffer.write(raw)
        if effect_ledger is not None:
            effect_ledger["phase"] = "public-report-flush"
            effect_ledger["public_report_flush_attempted"] = True
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        if options is not None and getattr(options, "run", False):
            if effect_ledger is None:
                effect_ledger = new_actual_effect_ledger(options)
            result = actual_entry_failure_result(error, effect_ledger)
        else:
            result = {
                "schema": SCHEMA + "-entry-failure", "status": "FAIL",
                "error_type": type(error).__qualname__,
                "error_message": bounded_error(error),
                "actual_candidate_workers": 0,
                "actual_reference_workers": 0,
                "actual_native_activations": 0,
                "actual_source_builds": 0,
                "hidden_cases_read": 0,
                "benchmark_files_read": 0,
                "clock_samples": 0,
                "timing_trials_run": 0,
                "performance": "NOT MEASURED",
                "memory": "NOT MEASURED",
                "holdout": "NOT OPENED",
                "candidate_qualified": False,
                "winner_selected": False,
            }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
