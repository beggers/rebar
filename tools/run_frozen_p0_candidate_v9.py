#!/usr/bin/env python3
"""Freeze a complete, original, recoverable repaired-C correctness campaign."""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
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
from typing import Any, Iterator, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_v9.py"
WORKER_RELATIVE = "tools/run_frozen_p0_candidate_worker_v7.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v9.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-v9"
WORKER_SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v7"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ORIGINAL_PRODUCER_SHA256 = "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c"
ORIGINAL_PRODUCER_PROTOCOL_SHA256 = "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76"
ORIGINAL_PRODUCER_DOCUMENT_SHA256 = "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1"
PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT = 30
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
ORIGINAL_C_SHA256 = "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
DERIVED_C_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
FAMILY = "c"
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
HISTORICAL_EVIDENCE_OWNER_COUNT = 103
HISTORICAL_AUTHENTICATED_REFERENCE_COUNT = 108
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
            "run only isolated pinned CPython and the genuine V8 aggregate")


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {key: 0 for key in (
        "file_reads", "file_writes", "candidate_workers", "reference_workers",
        "source_builds", "native_activations", "candidate_imports",
        "interpreter_creations", "network_requests", "clock_samples",
        "hidden_cases_read", "benchmark_files_read", "blocked_reads",
        "blocked_writes", "blocked_processes", "blocked_imports",
        "blocked_threads", "blocked_network", "blocked_clocks",
    )}
    originals: list[tuple[Any, str, Any]] = []

    def block(owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def reject(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyEffect("source-only V8 aggregate forbids " + name)

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
        "expected_v8_build_process_count": 14,
        "expected_actual_original_worker_count": 13,
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
            ("original_producer_sha256", "0" * 64),
            ("nested_producer_sha256", "0" * 64),
            ("original_c_source_sha256", DERIVED_C_SHA256),
            ("derived_c_source_sha256", ORIGINAL_C_SHA256),
            ("historical_evidence_owner_count", 76),
            ("historical_authenticated_reference_count", 71),
            ("maximum_public_report_bytes", MAX_PUBLIC_REPORT_BYTES + 1),
            ("expected_v8_build_process_count", 13),
            ("expected_actual_original_worker_count", 12),
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
            ("blocked_reads", lambda: builtins.open("/tmp/rebar-v8-forbidden", "rb")),
            ("blocked_reads", lambda: os.open("/tmp/rebar-v8-forbidden", os.O_RDONLY)),
            ("blocked_writes", lambda: os.write(-1, b"forbidden")),
            ("blocked_processes", lambda: subprocess.run(("forbidden-v8-worker",))),
            ("blocked_imports", lambda: importlib.import_module("candidates.vm_candidate")),
            ("blocked_threads", lambda: threading.Thread(target=lambda: None).start()),
            ("blocked_network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("blocked_clocks", lambda: time.perf_counter_ns()),
        )
        for counter, probe in probes:
            previous = effects[counter]
            try:
                probe()
            except SourceOnlyEffect:
                require(effects[counter] == previous + 1,
                        "authenticate the exact blocked V8 source-only effect")
                rejected += 1
            else:
                raise AggregateGateError("failed to block a source-only operation")
        require(rejected >= 50,
                "require substantial hostile complete-campaign controls")
        observed = dict(effects)
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "synthetic_only": True,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
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
            "require the exact independently owned genuine V7 suite worker",
        )
        chunks: list[bytes] = []
        remaining = information.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(block), "reject a truncated V7 source worker")
            chunks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject concealed V7 source worker bytes")
        raw = b"".join(chunks)
        require(
            digest(raw) == options.worker_source_sha256,
            "reject an unpinned, changed, historical, or substituted worker",
        )
    finally:
        os.close(descriptor)
    module = types.ModuleType(
        "_rebar_frozen_p0_candidate_worker_v7_for_v9",
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
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "reject legacy evaluator, wrong V7 source, altered routes, or history",
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
        and context.get("v3_frozen_context_verified_before_activation")
        is True
        and context.get("actual_candidate_workers") == 0
        and context.get("actual_native_activations") == 0
        and context.get("actual_source_builds") == 0
        and context.get("hidden_cases_read") == 0
        and context.get("clock_samples") == 0
        and context.get("performance") == "NOT MEASURED"
        and context.get("holdout") == "NOT OPENED",
        "reject active context, lost V3 pins, or incomplete V21/P0 history",
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
        "--activation-root",
        options.activation_root,
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
        "activation-source",
        "activation-protocol",
        "activation-contract",
        "activation-report",
        "activation-receipt",
        "recovery-journal",
        "native-engine",
        "native-bridge",
    ):
        value = getattr(options, name.replace("-", "_") + "_sha256")
        arguments.extend((
            "--" + name + "-sha256",
            checked_digest(value, name),
        ))
    return arguments

def worker_process(arguments: list[str]) -> dict[str, Any]:
    child = subprocess.Popen(arguments, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = child.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        stdout, stderr = child.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes,
            "preserve both complete original child streams")
    stdout_overflow = len(stdout) > MAX_CHILD_STDOUT_BYTES
    stderr_overflow = len(stderr) > MAX_CHILD_STDERR_BYTES
    require(not stdout_overflow and not stderr_overflow,
            "reject oversized streams without reporting a partial child record")
    return {
        "returncode": child.returncode,
        "timed_out": timed_out,
        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
        "stdout_bytes": len(stdout), "stdout_sha256": digest(stdout),
        "stdout_overflow": False,
        "stderr_base64": base64.b64encode(stderr).decode("ascii"),
        "stderr_bytes": len(stderr), "stderr_sha256": digest(stderr),
        "stderr_overflow": False,
    }


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


def observe_worker(options: argparse.Namespace, worker: types.ModuleType,
                   suite: tuple[str, int]) -> dict[str, Any]:
    name, count = suite
    process: dict[str, Any] | None = None
    try:
        process = worker_process(actual_worker_arguments(options, name))
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
        return {
            "suite": name, "case_execution_denominator": count,
            "actual_worker_started": True,
            "status": actual_status,
            "genuine_original_suite": genuine,
            "mismatch_count": mismatch_count,
            "failure_class": (
                "PASS" if actual_status == "PASS"
                else "SEMANTIC MISMATCH" if genuine is True
                else "INFRASTRUCTURE FAILURE"
            ),
            "process": process,
            "suite_archive": evidence["archive"],
            "suite_receipt": evidence["receipt"],
            "uncompressed_bytes": evidence["uncompressed_bytes"],
            "uncompressed_sha256": evidence["uncompressed_sha256"],
            "all_original_records_and_mismatches_preserved": True,
        }
    except BaseException as error:
        return {
            "suite": name, "case_execution_denominator": count,
            "actual_worker_started": process is not None,
            "status": "FAIL", "genuine_original_suite": False,
            "mismatch_count": None,
            "failure_class": "INFRASTRUCTURE FAILURE",
            "process": process,
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
            "all_original_records_and_mismatches_preserved": False,
        }


def recover_activation(options: argparse.Namespace,
                       worker: types.ModuleType) -> dict[str, Any]:
    activation = worker.frozen_module(
        worker.ACTIVATION_V5["source"][0],
        worker.ACTIVATION_V5["source"][1],
        "_rebar_frozen_repaired_c_v5_final_recovery_for_v8")
    arguments = {
        "mode": "restore", "family": FAMILY,
        "activation_root": options.activation_root,
        "recovery_journal_sha256": options.recovery_journal_sha256,
        "activation_source_sha256": worker.ACTIVATION_V5["source"][1],
        "activation_protocol_sha256": worker.ACTIVATION_V5["protocol"][1],
        "activation_contract_sha256": worker.ACTIVATION_V5["document"][1],
        "build_source_sha256": worker.BUILD["source"][1],
        "build_protocol_sha256": worker.BUILD["protocol"][1],
        "build_contract_sha256": worker.BUILD["document"][1],
    }
    recovered = activation.recover(arguments)
    require(type(recovered) is dict
            and recovered.get("schema") == activation.SCHEMA + "-actual-restoration"
            and recovered.get("status") == "PASS"
            and recovered.get("version") == 5
            and recovered.get("family") == FAMILY
            and recovered.get("route") == "journal-backed-restore"
            and recovered.get("activation_root") == options.activation_root
            and recovered.get("target") == worker.NATIVE_RELATIVE
            and recovered.get("group_atomic") is False,
            "never qualify or publish without genuine exact V5 restoration")
    return recovered


def publish_aggregate(worker: types.ModuleType, report: dict[str, Any],
                      options: argparse.Namespace) -> dict[str, Any]:
    compressed, expanded_sha, expanded_bytes = worker.stream_gzip(report)
    require(expanded_bytes <= MAX_PUBLIC_REPORT_BYTES,
            "retain the strict 32 MiB outer campaign report cap")
    stem = (worker.EVIDENCE_RELATIVE + "/frozen-p0-candidate-v9-c-"
            + worker.checked_label(options.label))
    if report["status"] == "FAIL":
        stem += "-failures"
    archive = worker.create_private_owner(stem + ".json.gz", compressed)
    receipt_document = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "candidate_status": report["status"],
        "candidate_family": FAMILY, "label": options.label,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "completed_suite_count": report["completed_suite_count"],
        "archive": archive,
        "uncompressed_sha256": expanded_sha,
        "uncompressed_bytes": expanded_bytes,
        "all_original_suite_evidence_preserved":
        report["all_original_suite_evidence_preserved"],
        "restoration": report["restoration"],
        "original_producer_sha256": ORIGINAL_PRODUCER_SHA256,
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "historical_evidence_owner_count": HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    receipt = worker.create_private_owner(
        stem + "-publication-receipt.json", worker.canonical(receipt_document))
    return {
        "schema": SCHEMA + "-published-complete-candidate",
        "status": report["status"], "candidate_family": FAMILY,
        "label": options.label,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "completed_suite_count": report["completed_suite_count"],
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


def run_actual_candidate(options: argparse.Namespace) -> dict[str, Any]:
    worker, _ = load_worker(options)
    context = worker.verify_live_worker_context(options)
    require(context.get("status") == "PASS",
            "require caller-pinned V3 source and actual V5 live-only context")
    build = worker.authenticate_v8_build(options)
    activation = worker.authenticate_v5_activation(options, build)
    rows: list[dict[str, Any]] = []
    restoration: dict[str, Any] | None = None
    outer_failure: dict[str, Any] | None = None
    try:
        for suite in SUITES:
            rows.append(observe_worker(options, worker, suite))
    except BaseException as error:
        outer_failure = {
            "type": type(error).__qualname__, "message": bounded_error(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
        }
    finally:
        if activation:
            restoration = recover_activation(options, worker)
    require(restoration is not None and restoration.get("status") == "PASS",
            "restore the exact canonical original C state before publication")
    passed = [row for row in rows if row.get("status") == "PASS"]
    passing_count = sum(row["case_execution_denominator"] for row in passed)
    mismatches = sum(row["mismatch_count"] for row in rows
                     if row.get("genuine_original_suite") is True
                     and type(row.get("mismatch_count")) is int)
    infrastructure = [row["suite"] for row in rows
                      if row.get("failure_class") == "INFRASTRUCTURE FAILURE"]
    preserved = len(rows) == SUITE_COUNT and all(
        row.get("all_original_records_and_mismatches_preserved") is True
        for row in rows
    )
    status = ("PASS" if len(passed) == SUITE_COUNT
              and passing_count == CASE_DENOMINATOR
              and preserved and outer_failure is None else "FAIL")
    report = {
        "schema": SCHEMA + "-complete-original-candidate-evaluation",
        "status": status, "candidate_family": FAMILY, "label": options.label,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "completed_suite_count": len(rows),
        "suite_results": rows,
        "verified_passing_case_count": passing_count,
        "semantic_mismatch_count": mismatches,
        "infrastructure_failure_count": len(infrastructure),
        "infrastructure_failure_suites": infrastructure,
        "all_original_suite_evidence_preserved": preserved,
        "candidate_qualified": status == "PASS",
        "actual_candidate_workers": sum(
            row.get("actual_worker_started") is True for row in rows
        ),
        "original_producer_sha256": options.producer_source_sha256,
        "original_producer_protocol_sha256":
            options.producer_protocol_sha256,
        "original_producer_document_sha256":
            options.producer_document_sha256,
        "nested_producer_sha256": options.producer_source_sha256,
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "actual_v8_build_archive_sha256": build["archive_owner"]["sha256"],
        "actual_v8_build_receipt_sha256": build["receipt_owner"]["sha256"],
        "v5_activation": {
            "root": activation["root"],
            "source_sha256": worker.ACTIVATION_V5["source"][1],
            "report": activation["activation_report"],
            "receipt": activation["activation_receipt"],
            "journal": activation["recovery_journal"],
        },
        "restoration": restoration,
        "outer_failure": outer_failure,
        "historical_evidence_owner_count": HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return publish_aggregate(worker, report, options)


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
    parser.add_argument("--activation-root")
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
        "activation-source",
        "activation-protocol",
        "activation-contract",
        "activation-report",
        "activation-receipt",
        "recovery-journal",
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
        "activation_root",
        "build_archive_sha256",
        "build_receipt_sha256",
        "activation_source_sha256",
        "activation_protocol_sha256",
        "activation_contract_sha256",
        "activation_report_sha256",
        "activation_receipt_sha256",
        "recovery_journal_sha256",
        "native_engine_sha256",
        "native_bridge_sha256",
    )
    if options.self_test:
        require(
            all(getattr(options, name) is None for name in (*pins, *actual)),
            "synthetic self-test cannot authorize V3 or candidate execution",
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
        "reject legacy, missing, changed, or cross-worker V3 source owners",
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
        "independently pin every live V5 owner and actual V8 C build",
    )
    for name in actual:
        if name.endswith("_sha256"):
            checked_digest(getattr(options, name), name)
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
            result = run_actual_candidate(options)
        raw = canonical(result)
        require(len(raw) <= MAX_PUBLIC_REPORT_BYTES,
                "never publish an unbounded outer correctness report")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
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
