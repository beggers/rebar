#!/usr/bin/env python3
"""Publish honest, complete, independently frozen Python-regex candidate results."""

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
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_v7.py"
WORKER_RELATIVE = "tools/run_frozen_p0_candidate_worker_v5.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V7.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v7.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-v7"
WORKER_SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v5"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
FAMILIES = ("rust", "c", "zig")
SOURCE_FAMILIES = ("rust", "c", "zig", "cpp", "go", "fortran")
BUILD_VERSIONS = {"rust": "2", "c": "2", "zig": "3"}
V2_ACTIVATION_SHA256 = "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218"
V2_ACTIVATION_PROTOCOL_SHA256 = "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529"
V4_BUILD_SOURCE_SHA256 = "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1"
V4_BUILD_PROTOCOL_SHA256 = "e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb"
V4_BUILD_DOCUMENT_SHA256 = "0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7"
V3_ACTIVATION_SHA256 = "39a170d5981e3484366eca223c0533366d92927975271fdb004fbce784b7a21e"
V3_ACTIVATION_PROTOCOL_SHA256 = "17656cd0ea3aa879cc5c69078460118f1e5e977f3e5c8d977c784954ea9f65bf"
V3_ACTIVATION_DOCUMENT_SHA256 = "87d2d34a142f620894b87b35f3216ede4a0374921a3dfacb9d8e209e3d3133fc"


class AggregateGateError(Exception):
    """A whole original candidate is incomplete, unsafe, or not compatible."""


class SourceOnlyEffect(AggregateGateError):
    """A purely synthetic frozen check attempted an external operation."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise AggregateGateError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")).encode("ascii")
                + b"\n")
    except (TypeError, ValueError, OverflowError, RecursionError,
            UnicodeError) as error:
        raise AggregateGateError("require exact bounded canonical evidence") from error


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require an exact independently frozen SHA-256: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "use only the genuine isolated CPython 3.14.6 and V7 aggregate")


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {name: 0 for name in (
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "source_builds", "native_promotions",
        "native_libraries_loaded", "interpreter_creations", "thread_starts",
        "network_requests", "clock_samples", "hidden_cases_read",
        "benchmark_files_read", "blocked_reads", "blocked_writes",
        "blocked_processes", "blocked_imports", "blocked_threads",
        "blocked_clocks", "blocked_promotions", "blocked_network",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[category] += 1
            raise SourceOnlyEffect("the synthetic V7 aggregate forbids " + name)

        installed.append((owner, name, original))
        setattr(owner, name, blocked)

    try:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (os, "read"), (os, "stat"), (os, "lstat"),
                            (Path, "open"), (Path, "read_bytes"),
                            (Path, "read_text")):
            install(owner, name, "blocked_reads")
        for owner, name in ((os, "write"), (os, "unlink"), (os, "remove"),
                            (os, "mkdir"), (os, "makedirs"), (os, "rename"),
                            (os, "fsync"), (Path, "write_bytes"),
                            (Path, "write_text"), (Path, "touch"),
                            (Path, "mkdir"), (Path, "unlink"),
                            (tempfile, "mkstemp"), (tempfile, "mkdtemp")):
            install(owner, name, "blocked_writes")
        install(os, "replace", "blocked_promotions")
        install(importlib, "import_module", "blocked_imports")
        install(subprocess, "Popen", "blocked_processes")
        install(subprocess, "run", "blocked_processes")
        install(threading.Thread, "start", "blocked_threads")
        install(socket, "create_connection", "blocked_network")
        install(socket.socket, "connect", "blocked_network")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            install(time, name, "blocked_clocks")
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-synthetic-source-contract",
        "phase": "CANDIDATES", "goal_sha256": GOAL_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "phase1_inventory_sha256": PHASE1_SHA256,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "currently_activatable_families": list(FAMILIES),
        "source_families": list(SOURCE_FAMILIES),
        "source_family_count": 6,
        "fully_runnable_p0_family_count": 3,
        "build_versions": dict(BUILD_VERSIONS),
        "v4_build_source_sha256": V4_BUILD_SOURCE_SHA256,
        "v4_build_protocol_sha256": V4_BUILD_PROTOCOL_SHA256,
        "v4_build_document_sha256": V4_BUILD_DOCUMENT_SHA256,
        "static_independent_family_count": 6,
        "static_independent_source_owner_count": 25,
        "external_regex_package_count": 0,
        "preserved_historical_candidate_artifact_count_including_restorations": 51,
        "preserved_historical_artifact_count_including_source_builds": 57,
        "preserved_historical_restoration_receipt_count": 3,
        "historical_verified_passing_case_counts":
        {"c": 7197, "rust": 7461, "zig": 3583},
        "historical_semantic_mismatch_counts":
        {"c": 2094, "rust": 2042, "zig": 1764},
        "historical_zig_interpreter_calls": 385,
        "historical_zig_interpreter_cleanup_failures": 3,
        "historical_zig_verified_passing_interpreter_cases": 0,
        "candidate_qualified_count": 0,
        "fully_qualified_candidate_count": 0,
        "nested_publication_sync_field": "file_fsync",
        "specialized_publication_sync_field": "file_fsync_completed",
        "worker_publication_sync_field": "file_fsync_completed",
        "publication_receipt_pass_qualifies_candidate": False,
        "v4_cpp_build_status": "PASS",
        "v4_cpp_independent_fresh_phase_count": 2,
        "v4_cpp_actual_process_count": 10,
        "v4_cpp_candidate_matching_cases": 0,
        "v4_go_build_status": "FAIL",
        "v4_go_publication_status": "PASS",
        "v4_go_actual_process_count": 4,
        "v4_go_independent_fresh_phase_count": 0,
        "v4_fortran_build_status": "FAIL",
        "v4_fortran_publication_status": "PASS",
        "v4_fortran_actual_process_count": 18,
        "v4_fortran_independent_fresh_phase_count": 2,
        "v4_fortran_engine_reproducible": False,
        "historical_v2_source_build_process_count": 39,
        "historical_v4_source_build_process_count": 32,
        "historical_v2_plus_v4_source_build_process_count": 71,
        "historical_v3_zig_source_build_process_count": 15,
        "historical_v2_plus_v3_plus_v4_source_build_process_count": 86,
        "process_id_uniqueness_claimed_across_independent_runs": False,
        "future_activation_source_sha256": V3_ACTIVATION_SHA256,
        "future_activation_protocol_sha256": V3_ACTIVATION_PROTOCOL_SHA256,
        "future_activation_document_sha256": V3_ACTIVATION_DOCUMENT_SHA256,
        "actual_v3_activations": 0,
        "future_family_matching_authorized": False,
        "maximum_specialized_input_bytes": 64 * 1024 * 1024,
        "maximum_nested_input_bytes": 48 * 1024 * 1024,
        "maximum_aggregate_output_bytes": MAX_REPORT_BYTES,
        "fresh_reference_workers_allowed": False,
        "external_regex_engines_allowed": False,
        "cross_family_engines_allowed": False,
        "fallback_allowed": False,
        "supplemental_cases_added_to_denominator": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout_opened": False,
        "winner_selected": False,
    }


def validate_synthetic_contract(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(synthetic_contract()),
            "reject any changed complete independently frozen V7 aggregate")
    return value


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, action: Callable[[], Any]) -> Any:
        try:
            value = action()
        except Exception as error:
            raise AggregateGateError("genuine V7 positive control failed: " + name) from error
        accepted.append(name)
        return value

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (AggregateGateError, SourceOnlyEffect, TypeError, ValueError,
                KeyError, UnicodeError, OverflowError, RecursionError, OSError):
            rejected.append(name)
            return
        raise AggregateGateError("hostile V7 aggregate control passed: " + name)

    with source_only_boundary() as effects:
        contract = accept("retain-complete-independent-v7-aggregate-contract",
                          lambda: validate_synthetic_contract(synthetic_contract()))
        accept("retain-all-thirteen-genuine-original-suites",
               lambda: require(contract["suite_count"] == 13,
                               "all thirteen independent original suites are mandatory"))
        accept("retain-all-31237-original-cases",
               lambda: require(contract["case_execution_denominator"] == 31237,
                               "never change the actual original denominator"))
        accept("retain-six-from-scratch-source-families",
               lambda: require(contract["static_independent_family_count"] == 6
                               and contract["static_independent_source_owner_count"] == 25
                               and contract["external_regex_package_count"] == 0,
                               "never count wrappers or external matching packages"))
        accept("retain-all-fifty-seven-historical-evidence-owners",
               lambda: require(contract["preserved_historical_candidate_artifact_count_including_restorations"] == 51
                               and contract["preserved_historical_artifact_count_including_source_builds"] == 57,
                               "preserve all actual candidate, restoration, and V4 build owners"))
        accept("never-call-passing-cases-qualified-candidates",
               lambda: require(contract["historical_verified_passing_case_counts"]["zig"] == 3583
                               and contract["fully_qualified_candidate_count"] == 0,
                               "partial matching never qualifies a complete candidate"))
        accept("retain-real-interpreter-failure-and-exact-owner-schema",
               lambda: require(contract["historical_zig_interpreter_calls"] == 385
                               and contract["historical_zig_interpreter_cleanup_failures"] == 3
                               and contract["historical_zig_verified_passing_interpreter_cases"] == 0
                               and contract["nested_publication_sync_field"] == "file_fsync",
                               "retain real failed calls without fabricating a pass"))
        accept("freeze-six-family-v3-without-inventing-activation",
               lambda: require(contract["future_activation_source_sha256"] == V3_ACTIVATION_SHA256
                               and contract["future_activation_protocol_sha256"] == V3_ACTIVATION_PROTOCOL_SHA256
                               and contract["future_activation_document_sha256"] == V3_ACTIVATION_DOCUMENT_SHA256
                               and contract["actual_v3_activations"] == 0
                               and contract["future_family_matching_authorized"] is False,
                               "a frozen V3 source is not a real candidate activation"))
        accept("distinguish-six-source-families-from-three-runnable-families",
               lambda: require(contract["source_family_count"] == 6
                               and contract["fully_runnable_p0_family_count"] == 3
                               and contract["fully_qualified_candidate_count"] == 0,
                               "never invent complete six-family original P0 producers"))
        accept("preserve-real-cpp-v4-build-without-matching",
               lambda: require(contract["v4_cpp_build_status"] == "PASS"
                               and contract["v4_cpp_independent_fresh_phase_count"] == 2
                               and contract["v4_cpp_actual_process_count"] == 10
                               and contract["v4_cpp_candidate_matching_cases"] == 0,
                               "an actual passing C++ build is not a matching candidate"))
        accept("preserve-real-go-v4-failure-with-successful-publication",
               lambda: require(contract["v4_go_build_status"] == "FAIL"
                               and contract["v4_go_publication_status"] == "PASS"
                               and contract["v4_go_actual_process_count"] == 4
                               and contract["v4_go_independent_fresh_phase_count"] == 0,
                               "never promote an actually failed Go build"))
        accept("preserve-real-fortran-v4-reproducibility-failure",
               lambda: require(contract["v4_fortran_build_status"] == "FAIL"
                               and contract["v4_fortran_publication_status"] == "PASS"
                               and contract["v4_fortran_actual_process_count"] == 18
                               and contract["v4_fortran_independent_fresh_phase_count"] == 2
                               and contract["v4_fortran_engine_reproducible"] is False,
                               "preserve both actually completed unequal Fortran phases"))
        accept("distinguish-v2-v3-and-v4-actual-process-denominators",
               lambda: require(contract["historical_v2_source_build_process_count"] == 39
                               and contract["historical_v4_source_build_process_count"] == 32
                               and contract["historical_v2_plus_v4_source_build_process_count"] == 71
                               and contract["historical_v3_zig_source_build_process_count"] == 15
                               and contract["historical_v2_plus_v3_plus_v4_source_build_process_count"] == 86
                               and contract["process_id_uniqueness_claimed_across_independent_runs"] is False,
                               "never count separately observed V3 Zig processes in the V2-plus-V4 total"))
        for field in contract:
            def mutate(field: str = field) -> Any:
                forged = synthetic_contract()
                value = forged[field]
                if type(value) is bool:
                    forged[field] = not value
                elif type(value) is int:
                    forged[field] = value + 1
                elif type(value) is dict:
                    forged[field] = {**value, "forged": True}
                elif type(value) is list:
                    forged[field] = value[:-1]
                else:
                    forged[field] = str(value) + "-forged"
                return validate_synthetic_contract(forged)
            reject("reject-changed-v7-aggregate-" + field, mutate)
        for name, action in (
            ("real-file-read", lambda: builtins.open("GOAL.md", "rb")),
            ("real-descriptor-read", lambda: os.open("GOAL.md", os.O_RDONLY)),
            ("real-candidate-process", lambda: subprocess.Popen([PINNED_PYTHON])),
            ("real-candidate-import", lambda: importlib.import_module("candidates")),
            ("real-clock", lambda: time.perf_counter()),
            ("real-native-promotion", lambda: os.replace("v7-a", "v7-b")),
            ("real-network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("real-temporary-file", lambda: tempfile.mkstemp()),
        ):
            reject("reject-" + name, action)
        reject("reject-integer-for-literal-true",
               lambda: require(1, "only exact true can satisfy a frozen gate"))
    for name in ("file_reads", "file_writes", "candidate_imports",
                 "candidate_workers", "reference_workers", "source_builds",
                 "native_promotions", "native_libraries_loaded",
                 "interpreter_creations", "thread_starts", "network_requests",
                 "clock_samples", "hidden_cases_read", "benchmark_files_read"):
        require(effects[name] == 0,
                "the synthetic V7 aggregate caused a real effect: " + name)
    return {"schema": SCHEMA + "-source-self-test", "status": "PASS",
            "synthetic": True, "accepted": accepted, "rejected": rejected,
            "accepted_count": len(accepted), "rejected_count": len(rejected),
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "preserved_historical_candidate_artifact_count_including_restorations": 51,
            "preserved_historical_artifact_count_including_source_builds": 57,
            "source_family_count": 6,
            "fully_runnable_p0_family_count": 3,
            "candidate_qualified_count": 0,
            "fully_qualified_candidate_count": 0,
            "source_only_effects": effects,
            "actual_candidate_workers": 0, "actual_reference_workers": 0,
            "actual_source_builds": 0, "actual_native_promotions": 0,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}


def read_exact_owned(relative: str, fingerprint: str) -> dict[str, Any]:
    checked_digest(fingerprint, relative)
    require(relative in {SOURCE_RELATIVE, WORKER_RELATIVE,
                         PROTOCOL_RELATIVE, DOCUMENT_RELATIVE},
            "read only the four predetermined independently frozen V7 owners")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories = flags | getattr(os, "O_DIRECTORY", 0)
    handles: list[int] = []
    try:
        parent = os.open(str(ROOT), directories)
        handles.append(parent)
        for part in relative.split("/")[:-1]:
            parent = os.open(part, directories, dir_fd=parent)
            handles.append(parent)
        basename = relative.split("/")[-1]
        descriptor = os.open(basename, flags, dir_fd=parent)
        handles.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= MAX_SOURCE_BYTES,
                "reject missing, replaced, symlinked, or oversized V7 source")
        recorded = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "reject truncated exact V7 frozen source")
            remaining -= len(block)
            recorded.update(block)
        require(os.read(descriptor, 1) == b"",
                "reject extra complete V7 frozen source bytes")
        after = os.fstat(descriptor)
        visible = os.stat(basename, dir_fd=parent, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and recorded.hexdigest() == fingerprint,
                "authenticate each unchanged complete exact V7 source inode")
        return {"relative": relative, "path": str(ROOT / relative),
                "sha256": fingerprint, "size_bytes": after.st_size,
                "device": after.st_dev, "inode": after.st_ino}
    finally:
        for descriptor in reversed(handles):
            os.close(descriptor)


def load_frozen_worker(options: argparse.Namespace) -> tuple[Any, dict[str, Any]]:
    verify_runtime()
    pins = ((SOURCE_RELATIVE, options.source_sha256),
            (WORKER_RELATIVE, options.worker_source_sha256),
            (PROTOCOL_RELATIVE, options.protocol_sha256),
            (DOCUMENT_RELATIVE, options.document_sha256))
    owners = {relative: read_exact_owned(relative, fingerprint)
              for relative, fingerprint in pins}
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    worker = importlib.import_module("tools.run_frozen_p0_candidate_worker_v5")
    require(getattr(worker, "SCHEMA", None) == WORKER_SCHEMA
            and os.path.abspath(str(worker.__file__)) == str(ROOT / WORKER_RELATIVE)
            and getattr(worker, "CASE_DENOMINATOR", None) == CASE_DENOMINATOR
            and getattr(worker, "SUITE_COUNT", None) == SUITE_COUNT,
            "import only the independently byte-pinned complete V5 worker")
    for relative, fingerprint in pins:
        read_exact_owned(relative, fingerprint)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "loading a frozen correctness worker cannot import a native candidate")
    return worker, owners


def context_worker_options(options: argparse.Namespace, worker: Any) -> Any:
    return worker.parse_arguments([
        "--verify-frozen-context", "--source-sha256", options.worker_source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--document-sha256", options.document_sha256])


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    require(options.candidate is None and options.label is None
            and options.build_version is None and options.build_label is None
            and options.activation_root is None and not options.owned_source_sha256,
            "a read-only aggregate cannot authorize native candidate matching")
    for name in ("build_source_sha256", "build_protocol_sha256",
                 "build_contract_sha256", "build_archive_sha256",
                 "build_receipt_sha256", "activation_source_sha256",
                 "activation_protocol_sha256", "activation_contract_sha256",
                 "activation_report_sha256", "activation_receipt_sha256",
                 "recovery_journal_sha256", "candidate_source_sha256",
                 "native_engine_sha256", "native_bridge_sha256"):
        require(getattr(options, name) is None,
                "read-only V7 verification cannot authorize native evidence: " + name)
    worker, owners = load_frozen_worker(options)
    result = worker.verify_frozen_context(context_worker_options(options, worker))
    require(type(result) is dict and result.get("status") == "PASS"
            and result.get("read_only") is True
            and result.get("suite_count") == SUITE_COUNT
            and result.get("case_execution_denominator") == CASE_DENOMINATOR
            and result.get("preserved_historical_candidate_artifact_count_including_restorations") == 51
            and result.get("preserved_historical_artifact_count_including_source_builds") == 57
            and result.get("preserved_historical_restoration_receipt_count") == 3
            and result.get("source_family_count") == 6
            and result.get("fully_runnable_p0_family_count") == 3
            and result.get("fully_qualified_candidate_count") == 0
            and result.get("actual_candidate_workers") == 0
            and result.get("actual_candidate_imports") == 0
            and result.get("actual_reference_workers") == 0
            and result.get("actual_source_builds") == 0
            and result.get("actual_native_promotions") == 0
            and result.get("actual_interpreters_created") == 0
            and result.get("clock_samples") == 0
            and result.get("benchmark_files_read") == 0
            and result.get("hidden_cases_read") == 0
            and result.get("performance") == "NOT MEASURED",
            "independently verify all genuine frozen candidate history without activity")
    zig = result["preserved_v6_zig_actual_campaign"]
    require(zig.get("status") == "FAIL" and zig.get("candidate_qualified") is False
            and zig.get("verified_passing_case_count") == 3583
            and zig.get("actual_semantic_mismatch_count") == 1764
            and zig.get("actual_case_interpreter_exec_calls") == 385
            and zig.get("actual_nested_verified_passing_case_count") == 0
            and zig.get("artifact_count_including_restoration") == 17,
            "never confuse actual passing Zig cases with a compatible replacement")
    history = result["preserved_v4_source_build_history"]
    require(history.get("artifact_count") == 6
            and history.get("actual_v3_activations") == 0
            and history["families"]["cpp"]["build_status"] == "PASS"
            and history["families"]["cpp"]["phase_count"] == 2
            and history["families"]["cpp"]["process_count"] == 10
            and history["families"]["cpp"]["candidate_matching_cases_executed"] == 0
            and history["families"]["go"]["build_status"] == "FAIL"
            and history["families"]["go"]["receipt_status"] == "PASS"
            and history["families"]["go"]["phase_count"] == 0
            and history["families"]["go"]["process_count"] == 4
            and history["families"]["fortran"]["build_status"] == "FAIL"
            and history["families"]["fortran"]["receipt_status"] == "PASS"
            and history["families"]["fortran"]["phase_count"] == 2
            and history["families"]["fortran"]["process_count"] == 18
            and history["families"]["fortran"]["first_engine_sha256"]
            != history["families"]["fortran"]["second_engine_sha256"],
            "preserve passing C++, real Go failure, and real nonreproducible Fortran")
    return {"schema": SCHEMA + "-read-only-frozen-context", "status": "PASS",
            "read_only": True, "frozen_v7_source_owners": owners,
            "full_case_worker_verification": result,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "preserved_historical_candidate_artifact_count_including_restorations": 51,
            "preserved_historical_artifact_count_including_source_builds": 57,
            "preserved_historical_restoration_receipt_count": 3,
            "source_family_count": 6,
            "fully_runnable_p0_family_count": 3,
            "candidate_qualified_count": 0,
            "fully_qualified_candidate_count": 0,
            "actual_candidate_workers": 0, "actual_candidate_imports": 0,
            "actual_reference_workers": 0, "actual_source_builds": 0,
            "actual_native_promotions": 0, "actual_interpreters_created": 0,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}


def actual_worker_arguments(options: argparse.Namespace) -> list[str]:
    names = (("candidate", options.candidate), ("label", options.label),
             ("build_version", options.build_version),
             ("build_label", options.build_label),
             ("source_sha256", options.worker_source_sha256),
             ("protocol_sha256", options.protocol_sha256),
             ("document_sha256", options.document_sha256),
             ("build_source_sha256", options.build_source_sha256),
             ("build_protocol_sha256", options.build_protocol_sha256),
             ("build_archive_sha256", options.build_archive_sha256),
             ("build_receipt_sha256", options.build_receipt_sha256),
             ("activation_root", options.activation_root),
             ("activation_source_sha256", options.activation_source_sha256),
             ("activation_protocol_sha256", options.activation_protocol_sha256),
             ("activation_report_sha256", options.activation_report_sha256),
             ("activation_receipt_sha256", options.activation_receipt_sha256),
             ("candidate_source_sha256", options.candidate_source_sha256),
             ("native_engine_sha256", options.native_engine_sha256),
             ("native_bridge_sha256", options.native_bridge_sha256))
    result = ["--run"]
    for name, value in names:
        require(type(value) is str and bool(value),
                "pin every real whole-candidate V7 authorization: " + name)
        result.extend(("--" + name.replace("_", "-"), value))
    if options.recovery_journal_sha256 is not None:
        result.extend(("--recovery-journal-sha256",
                       options.recovery_journal_sha256))
    if options.build_contract_sha256 is not None:
        result.extend(("--build-contract-sha256", options.build_contract_sha256))
    if options.activation_contract_sha256 is not None:
        result.extend(("--activation-contract-sha256",
                       options.activation_contract_sha256))
    for owner in options.owned_source_sha256:
        result.extend(("--owned-source-sha256", owner))
    return result


def authenticate_actual_worker_result(
    value: Any, process: Mapping[str, Any], options: argparse.Namespace,
    worker: Any, context: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(type(value) is dict
            and value.get("schema") == WORKER_SCHEMA + "-published-complete-candidate"
            and value.get("status") in {"PASS", "FAIL"}
            and value.get("candidate_family") == options.candidate
            and value.get("label") == options.label
            and value.get("suite_count") == SUITE_COUNT
            and value.get("case_execution_denominator") == CASE_DENOMINATOR
            and process.get("returncode") == (0 if value["status"] == "PASS" else 1),
            "authenticate the genuine complete V5 case-worker process")
    archive_path, receipt_path = worker.planned_worker_paths(
        options.candidate, options.label, failure=value["status"] == "FAIL")
    archive = worker.check_publication_shape(value.get("complete_archive"),
                                             kind="worker", relative=archive_path)
    receipt = worker.check_publication_shape(value.get("complete_publication_receipt"),
                                             kind="worker", relative=receipt_path)
    allowed = frozenset({*context["allowed_paths"], archive_path, receipt_path})
    original = context["v6_worker"]
    compressed, archive_owner = original.read_owned(
        archive_path, archive["sha256"], allowed=allowed,
        maximum=MAX_REPORT_BYTES)
    receipt_raw, receipt_owner = original.read_owned(
        receipt_path, receipt["sha256"], allowed=allowed,
        maximum=MAX_SOURCE_BYTES)
    require(len(compressed) == archive["bytes"]
            and len(receipt_raw) == receipt["bytes"]
            and archive_owner["device"] == archive["device"]
            and archive_owner["inode"] == archive["inode"]
            and receipt_owner["device"] == receipt["device"]
            and receipt_owner["inode"] == receipt["inode"],
            "retain the exact exclusive whole-worker archive and receipt inodes")
    plain = worker.bounded_gzip(compressed, archive_path, maximum=MAX_REPORT_BYTES)
    report = worker.decode_document(plain, archive_path, maximum=MAX_REPORT_BYTES)
    full_receipt = worker.decode_document(receipt_raw, receipt_path,
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
            and report.get("preserved_historical_candidate_artifact_count_including_restorations") == 51
            and report.get("preserved_historical_artifact_count_including_source_builds") == 57
            and report.get("source_family_count") == 6
            and report.get("fully_runnable_p0_family_count") == 3
            and type(suites) is list and len(suites) == SUITE_COUNT
            and [row.get("suite") for row in suites]
            == [suite.name for suite in worker.FROZEN_SUITES]
            and full_receipt.get("schema")
            == WORKER_SCHEMA + "-durable-publication-receipt"
            and full_receipt.get("status") == "PASS"
            and full_receipt.get("candidate_status") == report["status"]
            and full_receipt.get("archive") == archive
            and full_receipt.get("uncompressed_bytes") == len(plain)
            and full_receipt.get("uncompressed_sha256")
            == hashlib.sha256(plain).hexdigest(),
            "a full worker receipt proves publication, never candidate qualification")
    passing = [row for row in suites if row.get("status") == "PASS"]
    verified = sum(row.get("verified_passing_case_count", -1) for row in suites)
    mismatches = sum(row.get("mismatch_count", -1) for row in suites)
    qualified = len(passing) == SUITE_COUNT and verified == CASE_DENOMINATOR
    require(report.get("completed_candidate_suite_count") == len(passing)
            and report.get("verified_passing_case_count") == verified
            and report.get("qualified_candidate_case_executions") == verified
            and report.get("actual_semantic_mismatch_count") == mismatches
            and value.get("completed_candidate_suite_count") == len(passing)
            and value.get("verified_passing_case_count") == verified
            and value.get("qualified_candidate_case_executions") == verified
            and report.get("candidate_qualified") is qualified
            and value.get("candidate_qualified") is qualified
            and (report["status"] == "PASS") is qualified,
            "qualify a replacement only after every original frozen case passes")
    return report, archive_owner, receipt_owner


def run_actual_candidate(options: argparse.Namespace) -> dict[str, Any]:
    worker, owners = load_frozen_worker(options)
    worker_options = worker.parse_arguments(actual_worker_arguments(options))
    context = worker.authenticate_frozen_context(worker_options)
    if options.activation_source_sha256 == V3_ACTIVATION_SHA256:
        worker.authenticate_canonical_activation_v3(worker_options, context)
        raise AggregateGateError(
            "the independently authenticated six-family V3 activation cannot "
            "run " + options.candidate + ": the exact frozen original CPython, "
            "specialized, and subinterpreter P0 producers support only the "
            "real original three-family V2 activation routes; no candidate "
            "worker was started and no result was invented"
        )
    approval = context["v6_worker"].authenticate_canonical_activation(
        context["v6_options"], context)
    require(approval.get("family") == options.candidate
            and approval.get("build_version") == options.build_version,
            "require the actual independently source-built canonical candidate")
    for failure in (False, True):
        stem = ("oracle/phase2/evidence/frozen-p0-candidate-v7-"
                + options.candidate + "-" + options.label
                + ("-failures" if failure else ""))
        for relative in (stem + ".json.gz", stem + "-publication-receipt.json"):
            try:
                os.lstat(str(ROOT / relative))
            except FileNotFoundError:
                continue
            raise AggregateGateError("never overwrite existing V7 result: " + relative)
    worker.ensure_fresh_run_evidence(worker_options, context)
    report: dict[str, Any] = {
        "schema": SCHEMA + "-actual-complete-candidate", "status": "FAIL",
        "candidate_family": options.candidate, "label": options.label,
        "source_sha256": options.source_sha256,
        "worker_source_sha256": options.worker_source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "document_sha256": options.document_sha256,
        "build_version": options.build_version, "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "attempted_candidate_suite_count": 0,
        "completed_candidate_suite_count": 0,
        "verified_passing_case_count": 0,
        "qualified_candidate_case_executions": 0,
        "actual_semantic_mismatch_count": 0, "candidate_qualified": False,
        "all_suites": [], "worker_process": None,
        "worker_complete_archive": None,
        "worker_complete_publication_receipt": None,
        "failure": None, "frozen_v7_source_owners": owners,
        "corrected_canonical_activation": approval["canonical_activation"],
        "corrected_source_build": approval["source_build"],
        "six_family_static_independence": context["six_family_static_independence"],
        "preserved_v5_actual_campaigns": context["preserved_v5_campaigns"],
        "preserved_v6_zig_actual_campaign": context["preserved_v6_zig_campaign"],
        "preserved_v4_source_build_history": context["preserved_v4_build_history"],
        "preserved_historical_candidate_artifact_count_including_restorations": 51,
        "preserved_historical_artifact_count_including_source_builds": 57,
        "preserved_historical_restoration_receipt_count": 3,
        "source_family_count": 6,
        "fully_runnable_p0_family_count": 3,
        "supplemental_cases_added_to_phase1_denominator": False,
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    try:
        command = [PINNED_PYTHON, "-I", "-B", str(ROOT / WORKER_RELATIVE),
                   *actual_worker_arguments(options)]
        process = context["v6_worker"].encoded_process(command)
        report["worker_process"] = process
        require(process.get("timed_out") is False
                and process.get("returncode") in {0, 1}
                and context["v6_worker"].restore_stream(
                    process.get("stderr"), "whole V7 candidate worker stderr") == b"",
                "preserve actual whole-worker native crashes and stderr")
        actual = worker.decode_document(context["v6_worker"].restore_stream(
            process.get("stdout"), "whole V7 candidate worker stdout"),
            "complete actual V7 whole-worker result", maximum=MAX_REPORT_BYTES)
        proved, archive, receipt = authenticate_actual_worker_result(
            actual, process, options, worker, context)
        report.update({
            "status": proved["status"],
            "attempted_candidate_suite_count": proved["attempted_candidate_suite_count"],
            "completed_candidate_suite_count": proved["completed_candidate_suite_count"],
            "verified_passing_case_count": proved["verified_passing_case_count"],
            "qualified_candidate_case_executions":
            proved["qualified_candidate_case_executions"],
            "actual_semantic_mismatch_count": proved["actual_semantic_mismatch_count"],
            "candidate_qualified": proved["candidate_qualified"],
            "all_suites": proved["all_suites"],
            "worker_complete_archive": archive,
            "worker_complete_publication_receipt": receipt,
            "failure": None if proved["status"] == "PASS" else {
                "type": "ActualCandidateMismatch",
                "message": "one or more complete original Python regex suites failed",
                "failed_suite_count": SUITE_COUNT - proved["completed_candidate_suite_count"],
                "actual_semantic_mismatch_count": proved["actual_semantic_mismatch_count"],
                "all_failure_reasons": proved["all_failure_reasons"],
            },
        })
    except Exception as error:
        report["failure"] = {
            "type": type(error).__qualname__, "message": str(error),
            "traceback": traceback.format_exception(type(error), error,
                                                     error.__traceback__),
        }
    return worker.publish_actual_report(report, options,
                                        prefix="frozen-p0-candidate-v7-",
                                        schema=SCHEMA)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preserve every complete source-owned Python regex candidate.",
        allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=SOURCE_FAMILIES)
    parser.add_argument("--label")
    parser.add_argument("--build-version", choices=("2", "3", "4"))
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    for name in ("source", "worker-source", "protocol", "document",
                 "build-source", "build-protocol", "build-contract", "build-archive",
                 "build-receipt", "activation-source", "activation-protocol",
                 "activation-contract",
                 "activation-report", "activation-receipt", "recovery-journal",
                 "candidate-source", "native-engine", "native-bridge"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(not any(getattr(options, name) is not None for name in (
            "candidate", "label", "build_version", "build_label",
            "activation_root", "source_sha256", "worker_source_sha256",
            "protocol_sha256", "document_sha256", "build_source_sha256",
            "build_protocol_sha256", "build_contract_sha256",
            "build_archive_sha256", "build_receipt_sha256",
            "activation_source_sha256", "activation_protocol_sha256",
            "activation_contract_sha256", "activation_report_sha256",
            "activation_receipt_sha256", "recovery_journal_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256"))
            and not options.owned_source_sha256,
            "the synthetic V7 aggregate cannot authorize a real candidate")
        return options
    for name in ("source_sha256", "worker_source_sha256", "protocol_sha256",
                 "document_sha256", "build_source_sha256",
                 "build_protocol_sha256", "build_contract_sha256",
                 "build_archive_sha256",
                 "build_receipt_sha256", "activation_source_sha256",
                 "activation_protocol_sha256", "activation_contract_sha256",
                 "activation_report_sha256",
                 "activation_receipt_sha256", "recovery_journal_sha256",
                 "candidate_source_sha256", "native_engine_sha256",
                 "native_bridge_sha256"):
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    require(all(getattr(options, name) is not None for name in (
        "source_sha256", "worker_source_sha256", "protocol_sha256",
        "document_sha256")),
        "independently pin all four genuinely committed V7 aggregate owners")
    if options.verify_frozen_context:
        return options
    required = ("candidate", "label", "build_version", "build_label",
                "activation_root", "build_source_sha256",
                "build_protocol_sha256", "build_archive_sha256",
                "build_receipt_sha256", "activation_source_sha256",
                "activation_protocol_sha256", "activation_report_sha256",
                "activation_receipt_sha256", "candidate_source_sha256",
                "native_engine_sha256", "native_bridge_sha256")
    require(all(getattr(options, name) is not None for name in required)
            and bool(options.owned_source_sha256),
            "pin all actual candidate, source-build, native, and activation owners")
    if options.activation_source_sha256 == V3_ACTIVATION_SHA256:
        require(options.candidate in SOURCE_FAMILIES
                and options.build_version == "4"
                and options.activation_protocol_sha256 == V3_ACTIVATION_PROTOCOL_SHA256
                and options.activation_contract_sha256 == V3_ACTIVATION_DOCUMENT_SHA256
                and options.build_source_sha256 == V4_BUILD_SOURCE_SHA256
                and options.build_protocol_sha256 == V4_BUILD_PROTOCOL_SHA256
                and options.build_contract_sha256 == V4_BUILD_DOCUMENT_SHA256,
                "bind the exact genuinely frozen six-family V4 build and V3 activation")
    else:
        require(options.candidate in FAMILIES
                and BUILD_VERSIONS[options.candidate] == options.build_version
                and options.activation_source_sha256 == V2_ACTIVATION_SHA256
                and options.activation_protocol_sha256 == V2_ACTIVATION_PROTOCOL_SHA256
                and options.activation_contract_sha256 is None
                and options.build_contract_sha256 is None,
                "run only the actual original Rust, C, and Zig P0 producers")
    for item in options.owned_source_sha256:
        require(type(item) is str and item.count("=") == 1,
                "pin every genuinely independent owned source")
        relative, fingerprint = item.split("=", 1)
        require(bool(relative), "retain each independently owned source path")
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
        result = {"schema": SCHEMA + "-entry-failure", "status": "FAIL",
                  "error_type": type(error).__qualname__,
                  "error_message": str(error), "hidden_cases_read": 0,
                  "benchmark_files_read": 0, "clock_samples": 0,
                  "timing_trials_run": 0, "performance": "NOT MEASURED",
                  "final_holdout_authorized": False,
                  "candidate_qualified_for_hidden_benchmark": False,
                  "final_winner_selected": False}
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
