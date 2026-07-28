#!/usr/bin/env python3
"""Bridge the frozen V9 aggregate to its genuine frozen V7 worker options.

This is test infrastructure, not a regular-expression implementation.  It
preserves the original V9 code object, worker processes, original CPython
suites, evidence, native recovery, and result schema.  Its source-only and
frozen-context modes never run a candidate.
"""

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
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_frozen_p0_v9_live_context_adapter_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-V9-LIVE-CONTEXT-ADAPTER-V1.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-v9-live-context-adapter-v1.json"
SCHEMA = "rebar-owned-frozen-p0-v9-live-context-adapter-v1"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_FAILURE_ARCHIVE_BYTES = 128 * 1024
MAX_ERROR_BYTES = 64 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024

SUITES: tuple[tuple[str, int], ...] = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
SUITE_COUNT = 13
CASE_DENOMINATOR = 31237
PRIVATE_WAIVER_COUNT = 13
SOURCE_FAMILY_COUNT = 6
SOURCE_OWNER_COUNT = 25
V21_EVIDENCE_OWNER_COUNT = 103
V21_REFERENCE_PATH_COUNT = 108
PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT = 30
APPENDED_FAILURE_OWNER_COUNT = 2
TOTAL_EVIDENCE_OWNER_COUNT = 105
TOTAL_REFERENCE_PATH_COUNT = 110

GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
)
PHASE_ONE = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
V9 = {
    "runner": (
        "tools/run_frozen_p0_candidate_v9.py",
        "1511dac06dab5ce319b4dd09cb6f8c5a12160c48cc0dbbdfa7e7fe3f0d426702",
        43680,
    ),
    "worker": (
        "tools/run_frozen_p0_candidate_worker_v7.py",
        "855c59acdc0b5270493ece8fc39548a89e0febf94d6b186ac9f0e5a50754f68f",
        79184,
    ),
    "protocol": (
        "oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md",
        "afbb933eb022efaca7cb9604bc1614d3d2de7e3faf33f446234f725cd331771f",
        4413,
    ),
    "document": (
        "oracle/phase2/p0-candidate-protocol-v9.json",
        "a9609b0576aab4e0ea7ff6f9ae2a466c0d77d0af134a7f0bddf83ed01f61d631",
        13869,
    ),
}
V3 = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v3.py",
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
        195555,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
        5522,
    ),
    "document": (
        "oracle/phase2/six-family-p0-producer-v3.json",
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
        26909,
    ),
}
V21 = {
    "source": (
        "tools/render_candidate_current_overview_v21.py",
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
        75566,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v21.inputs.json",
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
        14631,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v21.json",
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
        96376,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v21.svg",
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
        8074,
    ),
}
V22 = {
    "source": (
        "tools/render_candidate_current_overview_v22.py",
        "a07bf3d6e6d8dc28c206218f14e2ed6f6089e31c66dbab2961979409b30fc955",
        59289,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v22.inputs.json",
        "6843292a1f1d62d4635be4737a1565554cee8ec9f359506bc95a94cb80af7b58",
        16526,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v22.json",
        "5dc6229696e5aba546c38e3d1d1bd4ce422a892a57ec562ccea8cb75cbbfb21f",
        100772,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v22.svg",
        "7314d28286b90ee8161c02fee175904ba2ddd2c67dd78163f93b04fef2d0a26c",
        7898,
    ),
}
FAILED_CONTROLLER_V2 = {
    "source": (
        "tools/run_owned_repaired_c_original_campaign_v2.py",
        "047eb7acb5a9febd8172f386061a20de5f17be36e9798d55c1c1e30e813594ab",
        78193,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V2.md",
        "bd89b3e09b1268a65475ad992b2858e2167368a82ee97d1b90b1fa36b32438b0",
        3475,
    ),
    "document": (
        "oracle/phase2/repaired-c-original-campaign-v2.json",
        "b3c16de03165b5e95529923a2475c73c51fce9a48a871aa61804b97fcca782de",
        14075,
    ),
}
APPENDED_FAILURE = {
    "archive": (
        "oracle/phase2/evidence/"
        "repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures.json.gz",
        "a37a70f7ab9e4dcc72b176ca51fb1bfe8514d906431e8f02f269871a8b946810",
        2496,
    ),
    "receipt": (
        "oracle/phase2/evidence/"
        "repaired-c-original-campaign-v2-c-phase2-v9-original-p0-"
        "failures-publication-receipt.json",
        "8a16520de9ac80aac1a6ea6d9a6cec3778379d35a611a52a2bca692685645c81",
        934,
    ),
}
APPENDED_FAILURE_UNCOMPRESSED_SHA256 = (
    "5aa8b513eec30c7ab13bc4b638a5b5026a6f03821f8cd411f6ea3201b0813cfd"
)
APPENDED_FAILURE_UNCOMPRESSED_BYTES = 5941
APPENDED_FAILURE_CHILD_STDOUT_SHA256 = (
    "93899f2cfc24a638785af66e683ca2f0866488be9cfbcdc2ffdd73be1b8e3f65"
)
APPENDED_FAILURE_ERROR = (
    "'Namespace' object has no attribute 'runner_source_sha256'"
)
CONTROLLER_V3_PATHS = {
    "source": "tools/run_owned_repaired_c_original_campaign_v3.py",
    "protocol": "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V3.md",
    "document": "oracle/phase2/repaired-c-original-campaign-v3.json",
}
V9_RUNNER_SCHEMA = "rebar-frozen-python-re-p0-candidate-v9"
V7_WORKER_SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v7"


class AdapterError(Exception):
    """Reject substitution, incomplete history, or unsafe live execution."""


class SourceOnlyEffect(AdapterError):
    """Source-only verification attempted an external operation."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise AdapterError(message)


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "require an exact SHA-256 owner: " + label,
    )
    return value


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete bytes only")
    return hashlib.sha256(raw).hexdigest()


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
        raise AdapterError("reject invalid or noncanonical adapter evidence") from error


def bounded_error(error: BaseException) -> str:
    raw = str(error).encode("utf-8", "backslashreplace")
    if len(raw) > MAX_ERROR_BYTES:
        raw = raw[:MAX_ERROR_BYTES] + b" [error summary truncated]"
    return raw.decode("utf-8", "replace")


def strict_document(
    raw: bytes,
    label: str,
    *,
    canonical_required: bool = False,
) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw), "require complete JSON bytes: " + label)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "reject duplicate JSON keys: " + label)
            result[key] = value
        return result

    def constant(value: str) -> Any:
        raise AdapterError("reject nonfinite JSON constants: " + label + ": " + value)

    try:
        document = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=pairs,
            parse_constant=constant,
        )
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise AdapterError("reject malformed JSON: " + label) from error
    require(type(document) is dict, "require one JSON object: " + label)
    if canonical_required:
        require(raw == canonical(document), "reject noncanonical JSON: " + label)
    return document


def runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "use only isolated, bytecode-free, pinned CPython and the exact adapter",
    )


def read_owner(
    relative: str,
    expected_sha256: str,
    *,
    expected_bytes: int | None = None,
    private: bool = False,
    maximum: int = MAX_SOURCE_BYTES,
) -> tuple[bytes, dict[str, Any]]:
    require(
        type(relative) is str
        and bool(relative)
        and not os.path.isabs(relative)
        and ".." not in Path(relative).parts
        and "\\" not in relative,
        "reject an escaped or substituted adapter owner",
    )
    checked_digest(expected_sha256, relative)
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(str(ROOT / relative), flags)
    try:
        information = os.fstat(descriptor)
        require(
            stat.S_ISREG(information.st_mode)
            and information.st_nlink == 1
            and 0 < information.st_size <= maximum,
            "require one complete, independently owned file: " + relative,
        )
        if expected_bytes is not None:
            require(
                type(expected_bytes) is int
                and information.st_size == expected_bytes,
                "reject changed source or evidence size: " + relative,
            )
        if private:
            require(
                stat.S_IMODE(information.st_mode) == 0o600,
                "require exact private 0600 failure evidence: " + relative,
            )
        remaining = information.st_size
        chunks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(block), "reject a truncated owner: " + relative)
            chunks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject trailing owner bytes: " + relative)
        raw = b"".join(chunks)
        require(
            digest(raw) == expected_sha256,
            "reject an unpinned or substituted owner: " + relative,
        )
        owner = {
            "relative": relative,
            "sha256": expected_sha256,
            "size_bytes": information.st_size,
            "device": information.st_dev,
            "inode": information.st_ino,
            "mode": stat.S_IMODE(information.st_mode),
        }
        return raw, owner
    finally:
        os.close(descriptor)


def mapped(owners: dict[str, tuple[str, str, int]]) -> dict[str, dict[str, Any]]:
    return {
        role: {"path": relative, "sha256": fingerprint, "size_bytes": size}
        for role, (relative, fingerprint, size) in owners.items()
    }


def expected_machine_contract(options: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "pinned_runtime": {
            "implementation": "cpython",
            "version": "3.14.6",
            "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
            "isolated": True,
            "bytecode_writes": False,
        },
        "adapter": {
            "source": {
                "path": SOURCE_RELATIVE,
                "sha256": options.adapter_source_sha256,
            },
            "protocol": {
                "path": PROTOCOL_RELATIVE,
                "sha256": options.adapter_protocol_sha256,
            },
            "contract": {"path": DOCUMENT_RELATIVE},
        },
        "goal": {"path": GOAL[0], "sha256": GOAL[1], "size_bytes": GOAL[2]},
        "phase_one": {
            "path": PHASE_ONE[0],
            "sha256": PHASE_ONE[1],
            "size_bytes": PHASE_ONE[2],
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        },
        "immutable_v9": mapped(V9),
        "immutable_v3_original_evaluator": mapped(V3),
        "preserved_v21_overview": mapped(V21),
        "current_v22_overview": mapped(V22),
        "preserved_failed_v2_controller": mapped(FAILED_CONTROLLER_V2),
        "preserved_failed_v2_evidence": {
            **mapped(APPENDED_FAILURE),
            "archive_uncompressed_sha256": APPENDED_FAILURE_UNCOMPRESSED_SHA256,
            "archive_uncompressed_bytes": APPENDED_FAILURE_UNCOMPRESSED_BYTES,
            "aggregate_child_stdout_sha256": APPENDED_FAILURE_CHILD_STDOUT_SHA256,
            "aggregate_child_error_type": "AttributeError",
            "aggregate_child_error_message": APPENDED_FAILURE_ERROR,
            "candidate_workers_started": 0,
            "completed_original_suites": 0,
            "semantic_mismatches": "NOT MEASURED",
            "original_native_restored": True,
        },
        "history": {
            "preserved_v21_evidence_owner_count": V21_EVIDENCE_OWNER_COUNT,
            "preserved_v21_authenticated_reference_path_count": V21_REFERENCE_PATH_COUNT,
            "preserved_original_failed_campaign_owner_count":
                PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
            "appended_failed_v2_evidence_owner_count": APPENDED_FAILURE_OWNER_COUNT,
            "total_distinct_evidence_owner_count": TOTAL_EVIDENCE_OWNER_COUNT,
            "total_authenticated_reference_path_count": TOTAL_REFERENCE_PATH_COUNT,
        },
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "original_suites": [
            {"id": name, "case_execution_count": count} for name, count in SUITES
        ],
        "live_bridge": {
            "immutable_original_runner_code_object": True,
            "immutable_original_runner_global_dictionary": True,
            "single_authenticated_worker_load": True,
            "worker_argument_source": "immutable V9 actual_worker_arguments",
            "verified_process_prefix_length": 4,
            "worker_argument_parser": "immutable V7 parse_arguments",
            "live_context_uses_genuine_v7_namespace": True,
            "frozen_context_after_activation": False,
            "original_suite_worker_count": SUITE_COUNT,
            "original_v9_publication_schema_preserved": True,
            "original_v9_restoration_and_finally_preserved": True,
            "candidate_matching_engine_modified": False,
            "candidate_matching_delegation_added": False,
            "external_regex_package_allowed": False,
            "stdlib_regex_engine_allowed": False,
        },
        "required_future_crash_safe_controller": {
            "source_path": CONTROLLER_V3_PATHS["source"],
            "protocol_path": CONTROLLER_V3_PATHS["protocol"],
            "contract_path": CONTROLLER_V3_PATHS["document"],
            "independent_caller_pins_required_for_run": True,
            "outer_recovery_required": True,
            "original_native_restored_before_publication": True,
        },
        "phase_boundary": {
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
        },
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        key: 0
        for key in (
            "file_reads",
            "file_writes",
            "candidate_workers",
            "reference_workers",
            "source_builds",
            "native_activations",
            "candidate_imports",
            "interpreter_creations",
            "network_requests",
            "clock_samples",
            "hidden_cases_read",
            "benchmark_files_read",
            "blocked_reads",
            "blocked_writes",
            "blocked_processes",
            "blocked_imports",
            "blocked_threads",
            "blocked_network",
            "blocked_clocks",
        )
    }
    originals: list[tuple[Any, str, Any]] = []

    def block(owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def reject(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyEffect("source-only adapter forbids " + name)

        originals.append((owner, name, original))
        setattr(owner, name, reject)

    try:
        for owner, name in (
            (builtins, "open"),
            (io, "open"),
            (os, "open"),
            (os, "read"),
            (os, "stat"),
            (Path, "open"),
            (Path, "read_bytes"),
            (Path, "read_text"),
        ):
            block(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"),
            (os, "unlink"),
            (os, "replace"),
            (os, "rename"),
            (os, "fsync"),
            (os, "mkdir"),
            (Path, "write_bytes"),
            (Path, "write_text"),
            (tempfile, "mkdtemp"),
            (tempfile, "mkstemp"),
        ):
            block(owner, name, "blocked_writes")
        block(importlib, "import_module", "blocked_imports")
        block(subprocess, "Popen", "blocked_processes")
        block(subprocess, "run", "blocked_processes")
        block(threading.Thread, "start", "blocked_threads")
        block(socket, "create_connection", "blocked_network")
        block(socket.socket, "connect", "blocked_network")
        for name in (
            "time",
            "time_ns",
            "monotonic",
            "monotonic_ns",
            "perf_counter",
            "perf_counter_ns",
            "process_time",
            "process_time_ns",
            "thread_time",
            "thread_time_ns",
        ):
            block(time, name, "blocked_clocks")
        yield effects
    finally:
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)


def synthetic_options() -> argparse.Namespace:
    return argparse.Namespace(
        adapter_source_sha256="a" * 64,
        adapter_protocol_sha256="b" * 64,
        adapter_contract_sha256="c" * 64,
    )


def validate_synthetic_contract(value: Any) -> dict[str, Any]:
    expected = expected_machine_contract(synthetic_options())
    require(
        type(value) is dict and canonical(value) == canonical(expected),
        "reject changed original cases, source owners, failed history, or bridge",
    )
    require(
        len(SUITES) == SUITE_COUNT
        and len({name for name, _ in SUITES}) == SUITE_COUNT
        and sum(count for _, count in SUITES) == CASE_DENOMINATOR
        and TOTAL_EVIDENCE_OWNER_COUNT
        == V21_EVIDENCE_OWNER_COUNT + APPENDED_FAILURE_OWNER_COUNT
        and TOTAL_REFERENCE_PATH_COUNT
        == V21_REFERENCE_PATH_COUNT + APPENDED_FAILURE_OWNER_COUNT,
        "preserve every original suite and independently appended failure owner",
    )
    return value


class AuthenticatedLiveWorker:
    """Expose one genuine worker; bridge only its live-context namespace."""

    __slots__ = ("_worker", "_aggregate_options", "_worker_options", "_calls")

    def __init__(
        self,
        worker: types.ModuleType,
        aggregate_options: argparse.Namespace,
        worker_options: argparse.Namespace,
    ) -> None:
        self._worker = worker
        self._aggregate_options = aggregate_options
        self._worker_options = worker_options
        self._calls = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._worker, name)

    def verify_live_worker_context(self, options: argparse.Namespace) -> dict[str, Any]:
        require(
            options is self._aggregate_options,
            "reject a substituted or repeated aggregate-to-worker namespace",
        )
        require(self._calls == 0, "verify the genuine live worker exactly once")
        self._calls += 1
        result = self._worker.verify_live_worker_context(self._worker_options)
        require(
            type(result) is dict
            and result.get("status") == "PASS"
            and result.get("schema") == V7_WORKER_SCHEMA + "-live-worker-source-context"
            and result.get("suite_count") == SUITE_COUNT
            and result.get("case_execution_denominator") == CASE_DENOMINATOR
            and result.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and result.get("original_producer_sha256") == V3["source"][1]
            and result.get("nested_producer_sha256") == V3["source"][1]
            and result.get("historical_evidence_owner_count") == V21_EVIDENCE_OWNER_COUNT
            and result.get("historical_authenticated_reference_count")
            == V21_REFERENCE_PATH_COUNT
            and result.get("preserved_failed_campaign_evidence_owner_count")
            == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
            and result.get("v3_frozen_context_called_after_activation") is False
            and result.get("actual_candidate_workers") == 0
            and result.get("actual_reference_workers") == 0
            and result.get("actual_source_builds") == 0
            and result.get("actual_native_activations") == 0
            and result.get("hidden_cases_read") == 0
            and result.get("clock_samples") == 0
            and result.get("performance") == "NOT MEASURED"
            and result.get("holdout") == "NOT OPENED",
            "require the complete original V7 live-only context and V3 owner",
        )
        return result


def validate_original_runner(base: types.ModuleType) -> None:
    require(
        isinstance(base, types.ModuleType)
        and getattr(base, "SCHEMA", None) == V9_RUNNER_SCHEMA
        and getattr(base, "WORKER_SCHEMA", None) == V7_WORKER_SCHEMA
        and getattr(base, "SOURCE_RELATIVE", None) == V9["runner"][0]
        and getattr(base, "WORKER_RELATIVE", None) == V9["worker"][0]
        and getattr(base, "PINNED_PYTHON", None) == PINNED_PYTHON
        and tuple(getattr(base, "SUITES", ())) == SUITES
        and getattr(base, "SUITE_COUNT", None) == SUITE_COUNT
        and getattr(base, "CASE_DENOMINATOR", None) == CASE_DENOMINATOR
        and getattr(base, "PRIVATE_WAIVER_COUNT", None) == PRIVATE_WAIVER_COUNT
        and getattr(base, "SOURCE_FAMILY_COUNT", None) == SOURCE_FAMILY_COUNT
        and getattr(base, "SOURCE_OWNER_COUNT", None) == SOURCE_OWNER_COUNT
        and getattr(base, "HISTORICAL_EVIDENCE_OWNER_COUNT", None)
        == V21_EVIDENCE_OWNER_COUNT
        and getattr(base, "HISTORICAL_AUTHENTICATED_REFERENCE_COUNT", None)
        == V21_REFERENCE_PATH_COUNT
        and getattr(base, "PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT", None)
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and getattr(base, "ORIGINAL_PRODUCER_SHA256", None) == V3["source"][1]
        and getattr(base, "ORIGINAL_PRODUCER_PROTOCOL_SHA256", None)
        == V3["protocol"][1]
        and getattr(base, "ORIGINAL_PRODUCER_DOCUMENT_SHA256", None)
        == V3["document"][1]
        and callable(getattr(base, "load_worker", None))
        and callable(getattr(base, "actual_worker_arguments", None))
        and isinstance(getattr(base, "run_actual_candidate", None), types.FunctionType),
        "reject changed immutable V9 code, V7 worker, V3 evaluator, or original suites",
    )


def validate_original_run_options(options: argparse.Namespace) -> None:
    require(
        isinstance(options, argparse.Namespace)
        and getattr(options, "run", None) is True
        and getattr(options, "candidate", None) == "c"
        and getattr(options, "source_sha256", None) == V9["runner"][1]
        and getattr(options, "worker_source_sha256", None) == V9["worker"][1]
        and getattr(options, "protocol_sha256", None) == V9["protocol"][1]
        and getattr(options, "document_sha256", None) == V9["document"][1]
        and getattr(options, "producer_source_sha256", None) == V3["source"][1]
        and getattr(options, "producer_protocol_sha256", None) == V3["protocol"][1]
        and getattr(options, "producer_document_sha256", None) == V3["document"][1],
        "preserve exact independent original V9, V7, and V3 runtime pins",
    )


def execute_immutable_original_run(
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict[str, Any]:
    validate_original_runner(base)
    validate_original_run_options(options)
    genuine_worker, worker_owner = base.load_worker(options)
    require(
        isinstance(genuine_worker, types.ModuleType)
        and genuine_worker.SCHEMA == V7_WORKER_SCHEMA
        and genuine_worker.RUNNER_SCHEMA == V9_RUNNER_SCHEMA
        and genuine_worker.SOURCE_RELATIVE == V9["worker"][0]
        and genuine_worker.RUNNER_RELATIVE == V9["runner"][0]
        and tuple(genuine_worker.SUITES) == SUITES
        and genuine_worker.CASE_DENOMINATOR == CASE_DENOMINATOR
        and type(worker_owner) is dict
        and worker_owner.get("relative") == V9["worker"][0]
        and worker_owner.get("sha256") == V9["worker"][1]
        and worker_owner.get("size_bytes") == V9["worker"][2],
        "load the exact original V7 worker once under its independent source pin",
    )
    arguments = base.actual_worker_arguments(options, SUITES[0][0])
    require(
        type(arguments) is list
        and len(arguments) > 4
        and arguments[:4]
        == [PINNED_PYTHON, "-I", "-B", str(ROOT / V9["worker"][0])],
        "preserve the genuine pinned isolated four-argument worker process prefix",
    )
    worker_options = genuine_worker.parse_arguments(arguments[4:])
    require(
        isinstance(worker_options, argparse.Namespace)
        and worker_options.run is True
        and worker_options.candidate == "c"
        and worker_options.suite == SUITES[0][0]
        and worker_options.source_sha256 == V9["worker"][1]
        and worker_options.runner_source_sha256 == V9["runner"][1]
        and worker_options.protocol_sha256 == V9["protocol"][1]
        and worker_options.document_sha256 == V9["document"][1]
        and worker_options.producer_source_sha256 == V3["source"][1]
        and worker_options.producer_protocol_sha256 == V3["protocol"][1]
        and worker_options.producer_document_sha256 == V3["document"][1]
        and worker_options.label == options.label
        and worker_options.build_label == options.build_label
        and worker_options.activation_root == options.activation_root,
        "derive the complete authentic V7 namespace from unchanged V9 worker arguments",
    )
    proxy = AuthenticatedLiveWorker(genuine_worker, options, worker_options)
    loader_calls = 0

    def authenticated_once_loader(received: argparse.Namespace) -> tuple[Any, Any]:
        nonlocal loader_calls
        require(received is options, "reject a substituted aggregate namespace")
        require(loader_calls == 0, "never load or substitute a second V7 worker")
        loader_calls += 1
        return proxy, worker_owner

    original = base.run_actual_candidate
    immutable_globals = original.__globals__
    previous_loader = immutable_globals.get("load_worker")
    copied_globals = dict(immutable_globals)
    copied_globals["load_worker"] = authenticated_once_loader
    bridged = types.FunctionType(
        original.__code__,
        copied_globals,
        original.__name__,
        original.__defaults__,
        original.__closure__,
    )
    bridged.__kwdefaults__ = original.__kwdefaults__
    require(
        bridged.__code__ is original.__code__
        and bridged.__defaults__ is original.__defaults__
        and bridged.__closure__ is original.__closure__
        and bridged.__globals__ is not immutable_globals
        and bridged.__globals__["load_worker"] is authenticated_once_loader
        and immutable_globals.get("load_worker") is previous_loader
        and base.run_actual_candidate is original,
        "execute only the unchanged, immutable original V9 aggregate code object",
    )
    result = bridged(options)
    require(
        loader_calls == 1
        and proxy._calls == 1
        and immutable_globals.get("load_worker") is previous_loader
        and base.run_actual_candidate is original,
        "verify one bridged live context without changing original runner globals",
    )
    return result


def _synthetic_original_run(options: argparse.Namespace) -> dict[str, Any]:
    worker, owner = globals()["load_worker"](options)
    context = worker.verify_live_worker_context(options)
    return {"status": "PASS", "context": context, "owner": owner}


def synthetic_runner() -> tuple[types.ModuleType, argparse.Namespace, dict[str, Any]]:
    state: dict[str, Any] = {"loads": 0, "contexts": 0, "parses": 0}
    options = argparse.Namespace(
        run=True,
        candidate="c",
        suite=None,
        label="synthetic-original-only",
        build_label="synthetic-build-only",
        activation_root="/tmp/rebar-phase2-native-activation-v5-c-synthetic",
        source_sha256=V9["runner"][1],
        worker_source_sha256=V9["worker"][1],
        protocol_sha256=V9["protocol"][1],
        document_sha256=V9["document"][1],
        producer_source_sha256=V3["source"][1],
        producer_protocol_sha256=V3["protocol"][1],
        producer_document_sha256=V3["document"][1],
    )
    worker = types.ModuleType("_synthetic_frozen_v7_worker_only")
    worker.SCHEMA = V7_WORKER_SCHEMA
    worker.RUNNER_SCHEMA = V9_RUNNER_SCHEMA
    worker.SOURCE_RELATIVE = V9["worker"][0]
    worker.RUNNER_RELATIVE = V9["runner"][0]
    worker.SUITES = SUITES
    worker.CASE_DENOMINATOR = CASE_DENOMINATOR

    def parse_worker(arguments: Sequence[str]) -> argparse.Namespace:
        state["parses"] += 1
        require(
            list(arguments)
            == [
                "--run",
                "--candidate",
                "c",
                "--suite",
                SUITES[0][0],
            ],
            "reject synthetic changed immutable worker arguments",
        )
        return argparse.Namespace(
            run=True,
            candidate="c",
            suite=SUITES[0][0],
            label=options.label,
            build_label=options.build_label,
            activation_root=options.activation_root,
            source_sha256=V9["worker"][1],
            runner_source_sha256=V9["runner"][1],
            protocol_sha256=V9["protocol"][1],
            document_sha256=V9["document"][1],
            producer_source_sha256=V3["source"][1],
            producer_protocol_sha256=V3["protocol"][1],
            producer_document_sha256=V3["document"][1],
        )

    def verify_live(received: argparse.Namespace) -> dict[str, Any]:
        state["contexts"] += 1
        require(
            received.runner_source_sha256 == V9["runner"][1]
            and received.source_sha256 == V9["worker"][1],
            "reject an aggregate namespace passed directly to the genuine worker",
        )
        return {
            "schema": V7_WORKER_SCHEMA + "-live-worker-source-context",
            "status": "PASS",
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "original_producer_sha256": V3["source"][1],
            "nested_producer_sha256": V3["source"][1],
            "historical_evidence_owner_count": V21_EVIDENCE_OWNER_COUNT,
            "historical_authenticated_reference_count": V21_REFERENCE_PATH_COUNT,
            "preserved_failed_campaign_evidence_owner_count":
                PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
            "v3_frozen_context_called_after_activation": False,
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }

    worker.parse_arguments = parse_worker
    worker.verify_live_worker_context = verify_live
    owner = {
        "relative": V9["worker"][0],
        "sha256": V9["worker"][1],
        "size_bytes": V9["worker"][2],
    }

    def load_synthetic(received: argparse.Namespace) -> tuple[types.ModuleType, dict[str, Any]]:
        require(received is options, "reject changed synthetic aggregate options")
        state["loads"] += 1
        return worker, owner

    def original_arguments(received: argparse.Namespace, suite: str) -> list[str]:
        require(received is options and suite == SUITES[0][0], "reject a changed suite")
        return [
            PINNED_PYTHON,
            "-I",
            "-B",
            str(ROOT / V9["worker"][0]),
            "--run",
            "--candidate",
            "c",
            "--suite",
            SUITES[0][0],
        ]

    runner = types.ModuleType("_synthetic_frozen_v9_runner_only")
    runner.SCHEMA = V9_RUNNER_SCHEMA
    runner.WORKER_SCHEMA = V7_WORKER_SCHEMA
    runner.SOURCE_RELATIVE = V9["runner"][0]
    runner.WORKER_RELATIVE = V9["worker"][0]
    runner.PINNED_PYTHON = PINNED_PYTHON
    runner.SUITES = SUITES
    runner.SUITE_COUNT = SUITE_COUNT
    runner.CASE_DENOMINATOR = CASE_DENOMINATOR
    runner.PRIVATE_WAIVER_COUNT = PRIVATE_WAIVER_COUNT
    runner.SOURCE_FAMILY_COUNT = SOURCE_FAMILY_COUNT
    runner.SOURCE_OWNER_COUNT = SOURCE_OWNER_COUNT
    runner.HISTORICAL_EVIDENCE_OWNER_COUNT = V21_EVIDENCE_OWNER_COUNT
    runner.HISTORICAL_AUTHENTICATED_REFERENCE_COUNT = V21_REFERENCE_PATH_COUNT
    runner.PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT = PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
    runner.ORIGINAL_PRODUCER_SHA256 = V3["source"][1]
    runner.ORIGINAL_PRODUCER_PROTOCOL_SHA256 = V3["protocol"][1]
    runner.ORIGINAL_PRODUCER_DOCUMENT_SHA256 = V3["document"][1]
    runner.load_worker = load_synthetic
    runner.actual_worker_arguments = original_arguments
    runner.run_actual_candidate = _synthetic_original_run
    return runner, options, state


def source_self_test() -> dict[str, Any]:
    accepted = 0
    rejected = 0
    with source_only_boundary() as effects:
        contract = validate_synthetic_contract(
            expected_machine_contract(synthetic_options())
        )
        accepted += 1
        top_changes: tuple[tuple[str, Any], ...] = (
            ("schema", SCHEMA),
            ("version", 2),
            ("source_family_count", 5),
            ("source_owner_count", 24),
            ("suite_count", 12),
            ("case_execution_denominator", 31236),
            ("named_private_waiver_count", 12),
        )
        nested_changes: tuple[tuple[str, str, Any], ...] = (
            ("pinned_runtime", "version", "3.14.7"),
            ("pinned_runtime", "isolated", False),
            ("pinned_runtime", "bytecode_writes", True),
            ("phase_one", "case_execution_denominator", 31236),
            ("phase_one", "suite_count", 12),
            ("phase_one", "named_private_waiver_count", 12),
            ("history", "preserved_v21_evidence_owner_count", 102),
            ("history", "preserved_v21_authenticated_reference_path_count", 107),
            ("history", "preserved_original_failed_campaign_owner_count", 29),
            ("history", "appended_failed_v2_evidence_owner_count", 1),
            ("history", "total_distinct_evidence_owner_count", 104),
            ("history", "total_authenticated_reference_path_count", 109),
            ("preserved_failed_v2_evidence", "candidate_workers_started", 1),
            ("preserved_failed_v2_evidence", "completed_original_suites", 1),
            ("preserved_failed_v2_evidence", "semantic_mismatches", 0),
            ("preserved_failed_v2_evidence", "original_native_restored", False),
            ("preserved_failed_v2_evidence", "aggregate_child_error_type", "ValueError"),
            ("preserved_failed_v2_evidence", "aggregate_child_error_message", "forged"),
            ("live_bridge", "immutable_original_runner_code_object", False),
            ("live_bridge", "immutable_original_runner_global_dictionary", False),
            ("live_bridge", "single_authenticated_worker_load", False),
            ("live_bridge", "verified_process_prefix_length", 3),
            ("live_bridge", "live_context_uses_genuine_v7_namespace", False),
            ("live_bridge", "frozen_context_after_activation", True),
            ("live_bridge", "original_suite_worker_count", 12),
            ("live_bridge", "original_v9_publication_schema_preserved", False),
            ("live_bridge", "original_v9_restoration_and_finally_preserved", False),
            ("live_bridge", "candidate_matching_engine_modified", True),
            ("live_bridge", "candidate_matching_delegation_added", True),
            ("live_bridge", "external_regex_package_allowed", True),
            ("live_bridge", "stdlib_regex_engine_allowed", True),
            ("required_future_crash_safe_controller",
             "independent_caller_pins_required_for_run", False),
            ("required_future_crash_safe_controller", "outer_recovery_required", False),
            ("required_future_crash_safe_controller",
             "original_native_restored_before_publication", False),
            ("phase_boundary", "actual_candidate_workers", 1),
            ("phase_boundary", "actual_reference_workers", 1),
            ("phase_boundary", "actual_native_activations", 1),
            ("phase_boundary", "actual_source_builds", 1),
            ("phase_boundary", "actual_candidate_imports", 1),
            ("phase_boundary", "hidden_cases_read", 1),
            ("phase_boundary", "benchmark_files_read", 1),
            ("phase_boundary", "clock_samples", 1),
            ("phase_boundary", "timing_trials_run", 1),
            ("phase_boundary", "performance", "PASS"),
            ("phase_boundary", "memory", "PASS"),
            ("phase_boundary", "holdout", "OPEN"),
            ("phase_boundary", "candidate_qualified_count", 1),
            ("phase_boundary", "winner_selected", True),
        )
        for key, forged in top_changes:
            changed = copy.deepcopy(contract)
            changed[key] = forged
            try:
                validate_synthetic_contract(changed)
            except AdapterError:
                rejected += 1
            else:
                raise AdapterError("accepted a changed source contract: " + key)
        for section, key, forged in nested_changes:
            changed = copy.deepcopy(contract)
            changed[section][key] = forged
            try:
                validate_synthetic_contract(changed)
            except AdapterError:
                rejected += 1
            else:
                raise AdapterError("accepted a changed contract: " + section + "." + key)
        for index, (name, _) in enumerate(SUITES):
            changed = copy.deepcopy(contract)
            changed["original_suites"][index]["id"] = name + "-forged"
            try:
                validate_synthetic_contract(changed)
            except AdapterError:
                rejected += 1
            else:
                raise AdapterError("accepted a changed or omitted original suite")
        for section in (
            "immutable_v9",
            "immutable_v3_original_evaluator",
            "preserved_v21_overview",
            "current_v22_overview",
            "preserved_failed_v2_controller",
        ):
            for role in contract[section]:
                changed = copy.deepcopy(contract)
                changed[section][role]["sha256"] = "0" * 64
                try:
                    validate_synthetic_contract(changed)
                except AdapterError:
                    rejected += 1
                else:
                    raise AdapterError("accepted substituted owner: " + section + "." + role)
        for role in ("archive", "receipt"):
            changed = copy.deepcopy(contract)
            changed["preserved_failed_v2_evidence"][role]["sha256"] = "0" * 64
            try:
                validate_synthetic_contract(changed)
            except AdapterError:
                rejected += 1
            else:
                raise AdapterError("accepted an omitted real V2 failure owner")
        for bad in (None, "", "g" * 64, "a" * 63, "a" * 65, 1):
            try:
                checked_digest(bad, "synthetic source owner")
            except AdapterError:
                rejected += 1
            else:
                raise AdapterError("accepted an invalid source-owner digest")
        base, options, state = synthetic_runner()
        original = base.run_actual_candidate
        original_globals = original.__globals__
        previous_loader = original_globals.get("load_worker")
        result = execute_immutable_original_run(base, options)
        require(
            result.get("status") == "PASS"
            and state == {"loads": 1, "contexts": 1, "parses": 1}
            and base.run_actual_candidate is original
            and original.__globals__ is original_globals
            and original_globals.get("load_worker") is previous_loader,
            "prove exact V9 code-object and global preservation using synthetic data",
        )
        accepted += 5
        runner_attacks: tuple[tuple[str, Any], ...] = (
            ("SCHEMA", "forged-v9"),
            ("WORKER_SCHEMA", "forged-v7"),
            ("SOURCE_RELATIVE", "tools/forged.py"),
            ("WORKER_RELATIVE", "tools/forged_worker.py"),
            ("PINNED_PYTHON", "/tmp/forged-python"),
            ("SUITES", SUITES[:-1]),
            ("SUITE_COUNT", 12),
            ("CASE_DENOMINATOR", 31236),
            ("PRIVATE_WAIVER_COUNT", 12),
            ("SOURCE_FAMILY_COUNT", 5),
            ("SOURCE_OWNER_COUNT", 24),
            ("HISTORICAL_EVIDENCE_OWNER_COUNT", 102),
            ("HISTORICAL_AUTHENTICATED_REFERENCE_COUNT", 107),
            ("PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT", 29),
            ("ORIGINAL_PRODUCER_SHA256", "0" * 64),
            ("ORIGINAL_PRODUCER_PROTOCOL_SHA256", "0" * 64),
            ("ORIGINAL_PRODUCER_DOCUMENT_SHA256", "0" * 64),
        )
        for key, forged in runner_attacks:
            fake, fake_options, _ = synthetic_runner()
            setattr(fake, key, forged)
            try:
                execute_immutable_original_run(fake, fake_options)
            except (AdapterError, TypeError, AttributeError, ValueError):
                rejected += 1
            else:
                raise AdapterError("accepted a substituted original runner: " + key)
        for key, forged in (
            ("run", False),
            ("candidate", "rust"),
            ("source_sha256", "0" * 64),
            ("worker_source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("document_sha256", "0" * 64),
            ("producer_source_sha256", "0" * 64),
            ("producer_protocol_sha256", "0" * 64),
            ("producer_document_sha256", "0" * 64),
        ):
            fake, fake_options, _ = synthetic_runner()
            setattr(fake_options, key, forged)
            try:
                execute_immutable_original_run(fake, fake_options)
            except (AdapterError, TypeError, AttributeError, ValueError):
                rejected += 1
            else:
                raise AdapterError("accepted substituted genuine worker pins: " + key)
        probes = (
            ("blocked_reads", lambda: builtins.open("/tmp/rebar-adapter-forbidden", "rb")),
            ("blocked_reads", lambda: os.open("/tmp/rebar-adapter-forbidden", os.O_RDONLY)),
            ("blocked_writes", lambda: os.write(-1, b"forbidden")),
            ("blocked_processes", lambda: subprocess.run(("forbidden-v9-adapter",))),
            ("blocked_imports", lambda: importlib.import_module("candidates.vm_candidate")),
            ("blocked_threads", lambda: threading.Thread(target=lambda: None).start()),
            ("blocked_network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("blocked_clocks", lambda: time.perf_counter_ns()),
        )
        for counter, probe in probes:
            before = effects[counter]
            try:
                probe()
            except SourceOnlyEffect:
                require(effects[counter] == before + 1, "verify the exact blocked effect")
                rejected += 1
            else:
                raise AdapterError("failed to block a source-only operation")
        require(rejected >= 100, "require substantial independent hostile adapter controls")
        observed = dict(effects)
    require(
        all(
            observed[key] == 0
            for key in (
                "file_reads",
                "file_writes",
                "candidate_workers",
                "reference_workers",
                "source_builds",
                "native_activations",
                "candidate_imports",
                "interpreter_creations",
                "network_requests",
                "clock_samples",
                "hidden_cases_read",
                "benchmark_files_read",
            )
        ),
        "source-only controls must not perform any real external effect",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "preserved_v21_evidence_owner_count": V21_EVIDENCE_OWNER_COUNT,
        "preserved_v21_authenticated_reference_path_count": V21_REFERENCE_PATH_COUNT,
        "preserved_original_failed_campaign_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "appended_failed_v2_evidence_owner_count": APPENDED_FAILURE_OWNER_COUNT,
        "historical_evidence_owner_count": TOTAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count": TOTAL_REFERENCE_PATH_COUNT,
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


def verify_appended_failure() -> dict[str, Any]:
    compressed, archive_owner = read_owner(
        *APPENDED_FAILURE["archive"][:2],
        expected_bytes=APPENDED_FAILURE["archive"][2],
        private=True,
        maximum=MAX_FAILURE_ARCHIVE_BYTES,
    )
    receipt_raw, receipt_owner = read_owner(
        *APPENDED_FAILURE["receipt"][:2],
        expected_bytes=APPENDED_FAILURE["receipt"][2],
        private=True,
        maximum=MAX_FAILURE_ARCHIVE_BYTES,
    )
    require(
        (archive_owner["device"], archive_owner["inode"])
        != (receipt_owner["device"], receipt_owner["inode"]),
        "preserve distinct independently owned V2 failure archive and receipt",
    )
    receipt = strict_document(receipt_raw, "authentic V2 failure receipt", canonical_required=True)
    receipt_archive = receipt.get("archive")
    require(
        receipt.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v2-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("family") == "c"
        and receipt.get("label") == "phase2-v9-original-p0"
        and receipt.get("suite_count") == SUITE_COUNT
        and receipt.get("case_execution_denominator") == CASE_DENOMINATOR
        and receipt.get("historical_evidence_owner_count") == V21_EVIDENCE_OWNER_COUNT
        and receipt.get("historical_authenticated_reference_count")
        == V21_REFERENCE_PATH_COUNT
        and receipt.get("original_native_restored") is True
        and receipt.get("uncompressed_sha256")
        == APPENDED_FAILURE_UNCOMPRESSED_SHA256
        and receipt.get("uncompressed_bytes") == APPENDED_FAILURE_UNCOMPRESSED_BYTES
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False
        and type(receipt_archive) is dict
        and receipt_archive.get("relative") == APPENDED_FAILURE["archive"][0]
        and receipt_archive.get("sha256") == archive_owner["sha256"]
        and receipt_archive.get("size_bytes") == archive_owner["size_bytes"]
        and receipt_archive.get("device") == archive_owner["device"]
        and receipt_archive.get("inode") == archive_owner["inode"]
        and receipt_archive.get("mode") == 0o600
        and receipt_archive.get("exclusive_creation") is True
        and receipt_archive.get("file_fsync_completed") is True
        and receipt_archive.get("directory_fsync_completed") is True
        and receipt_archive.get("same_inode_readback_verified") is True,
        "never turn successful publication of a failed V2 campaign into matching evidence",
    )
    try:
        expanded = gzip.decompress(compressed)
    except (OSError, EOFError, zlib.error) as error:
        raise AdapterError("reject corrupt or incomplete V2 failure evidence") from error
    require(
        len(expanded) == APPENDED_FAILURE_UNCOMPRESSED_BYTES
        and digest(expanded) == APPENDED_FAILURE_UNCOMPRESSED_SHA256,
        "authenticate every byte of the genuine V2 infrastructure failure",
    )
    report = strict_document(expanded, "genuine complete V2 failure report")
    failure = report.get("failure")
    process = failure.get("actual_aggregate_process") if type(failure) is dict else None
    require(
        report.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v2-actual-recovered-campaign"
        and report.get("status") == "FAIL"
        and report.get("family") == "c"
        and report.get("label") == "phase2-v9-original-p0"
        and report.get("suite_count") == SUITE_COUNT
        and report.get("case_execution_denominator") == CASE_DENOMINATOR
        and report.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and report.get("completed_suite_count") == "NOT MEASURED"
        and report.get("verified_passing_case_count") == "NOT MEASURED"
        and report.get("semantic_mismatch_count") == "NOT MEASURED"
        and report.get("infrastructure_failure_count") == 1
        and report.get("all_original_suite_evidence_preserved") is False
        and report.get("candidate_qualified") is False
        and report.get("original_native_restored") is True
        and report.get("original_producer_sha256") == V3["source"][1]
        and report.get("original_producer_protocol_sha256") == V3["protocol"][1]
        and report.get("original_producer_document_sha256") == V3["document"][1]
        and report.get("historical_evidence_owner_count") == V21_EVIDENCE_OWNER_COUNT
        and report.get("historical_authenticated_reference_count")
        == V21_REFERENCE_PATH_COUNT
        and report.get("preserved_failed_campaign_evidence_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and report.get("hidden_cases_read") == 0
        and report.get("benchmark_files_read") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("performance") == "NOT MEASURED"
        and report.get("memory") == "NOT MEASURED"
        and report.get("holdout") == "NOT OPENED"
        and report.get("winner_selected") is False
        and type(failure) is dict
        and failure.get("error_type") == "CampaignError"
        and type(process) is dict
        and process.get("actual_aggregate_processes") == 1
        and process.get("returncode") == 1
        and process.get("timed_out") is False
        and process.get("stderr_bytes") == 0
        and process.get("stderr_base64") == ""
        and process.get("stdout_sha256") == APPENDED_FAILURE_CHILD_STDOUT_SHA256,
        "preserve the one genuine pre-worker V2 infrastructure failure exactly",
    )
    try:
        child_raw = base64.b64decode(process["stdout_base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise AdapterError("reject substituted V9 child failure output") from error
    require(
        len(child_raw) == process.get("stdout_bytes")
        and digest(child_raw) == APPENDED_FAILURE_CHILD_STDOUT_SHA256,
        "authenticate complete unchanged V9 child failure output",
    )
    child = strict_document(child_raw, "genuine V9 child entry failure")
    require(
        child.get("schema") == V9_RUNNER_SCHEMA + "-entry-failure"
        and child.get("status") == "FAIL"
        and child.get("error_type") == "AttributeError"
        and child.get("error_message") == APPENDED_FAILURE_ERROR
        and child.get("actual_candidate_workers") == 0
        and child.get("actual_reference_workers") == 0
        and child.get("actual_native_activations") == 0
        and child.get("actual_source_builds") == 0
        and child.get("hidden_cases_read") == 0
        and child.get("benchmark_files_read") == 0
        and child.get("clock_samples") == 0
        and child.get("timing_trials_run") == 0
        and child.get("performance") == "NOT MEASURED"
        and child.get("memory") == "NOT MEASURED"
        and child.get("holdout") == "NOT OPENED"
        and child.get("candidate_qualified") is False
        and child.get("winner_selected") is False,
        "distinguish the actual V9 Namespace failure from any semantic match result",
    )
    recovery = report.get("recovery")
    require(
        type(recovery) is dict
        and recovery.get("route") == "existing-authenticated-restoration-receipt"
        and type(recovery.get("report")) is dict
        and recovery["report"].get("status") == "PASS"
        and recovery["report"].get("original_inode_preserved") is True,
        "preserve the genuine completed original-native recovery",
    )
    return {
        "archive": archive_owner,
        "receipt": receipt_owner,
        "archive_uncompressed_sha256": APPENDED_FAILURE_UNCOMPRESSED_SHA256,
        "archive_uncompressed_bytes": APPENDED_FAILURE_UNCOMPRESSED_BYTES,
        "actual_aggregate_processes": 1,
        "actual_candidate_workers": 0,
        "completed_suite_count": "NOT MEASURED",
        "semantic_mismatch_count": "NOT MEASURED",
        "infrastructure_failure_count": 1,
        "original_native_restored": True,
        "candidate_status": "FAIL",
    }


def load_original_runner() -> tuple[types.ModuleType, dict[str, Any]]:
    raw, owner = read_owner(
        *V9["runner"][:2], expected_bytes=V9["runner"][2]
    )
    module = types.ModuleType("_rebar_immutable_p0_v9_for_live_context_adapter_v1")
    module.__file__ = str(ROOT / V9["runner"][0])
    sys.modules[module.__name__] = module
    try:
        exec(compile(raw, module.__file__, "exec"), module.__dict__)
        validate_original_runner(module)
        require(
            module.run_actual_candidate.__code__.co_filename == module.__file__,
            "require the actual unchanged source-owned V9 aggregate code object",
        )
    except BaseException:
        sys.modules.pop(module.__name__, None)
        raise
    return module, owner


def verify_source_contract(options: argparse.Namespace) -> dict[str, dict[str, Any]]:
    owners: dict[str, dict[str, Any]] = {}
    for relative, fingerprint in (
        (SOURCE_RELATIVE, options.adapter_source_sha256),
        (PROTOCOL_RELATIVE, options.adapter_protocol_sha256),
        (DOCUMENT_RELATIVE, options.adapter_contract_sha256),
    ):
        raw, owner = read_owner(relative, fingerprint)
        owners[relative] = owner
        if relative == DOCUMENT_RELATIVE:
            document = strict_document(raw, "frozen live-context adapter machine contract")
            require(
                canonical(document) == canonical(expected_machine_contract(options)),
                "reject changed immutable V9 bridge, original P0, or 105-owner history",
            )
    return owners


def verify_static_history() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    owners: dict[str, dict[str, Any]] = {}
    for relative, fingerprint, size in (
        GOAL,
        PHASE_ONE,
        *V9.values(),
        *V3.values(),
        *V21.values(),
        *V22.values(),
        *FAILED_CONTROLLER_V2.values(),
    ):
        _, owner = read_owner(relative, fingerprint, expected_bytes=size)
        owners[relative] = owner
    phase_raw, _ = read_owner(*PHASE_ONE[:2], expected_bytes=PHASE_ONE[2])
    phase = strict_document(phase_raw, "unchanged original CPython P0 manifest")
    denominator = phase.get("denominator")
    require(
        phase.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and type(denominator) is dict
        and denominator.get("final_required_case_execution_denominator")
        == CASE_DENOMINATOR
        and denominator.get("available_frozen_vector_case_executions")
        == CASE_DENOMINATOR
        and tuple(denominator.get("counted_suite_ids", ()))
        == tuple(name for name, _ in SUITES)
        and denominator.get("private_upstream_methods_outside_public_denominator")
        == PRIVATE_WAIVER_COUNT
        and type(phase.get("suites")) is list
        and len(phase["suites"]) == SUITE_COUNT
        and tuple((item.get("id"), item.get("case_execution_count"))
                  for item in phase["suites"])
        == SUITES,
        "never weaken, replace, omit, or recount an original P0 case",
    )
    inputs_raw, _ = read_owner(*V21["inputs"][:2], expected_bytes=V21["inputs"][2])
    inputs = strict_document(inputs_raw, "original V21 overview input")
    require(
        inputs.get("schema") == "rebar-candidate-current-overview-v21-inputs"
        and inputs.get("version") == 21
        and inputs.get("suite_count") == SUITE_COUNT
        and inputs.get("full_case_denominator") == CASE_DENOMINATOR
        and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and inputs.get("repository_evidence_owner_count") == V21_EVIDENCE_OWNER_COUNT
        and inputs.get("all_digest_addressed_history_path_count")
        == V21_REFERENCE_PATH_COUNT
        and inputs.get("new_repaired_c_campaign_repository_evidence_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and inputs.get("candidate_qualified_count") == 0
        and inputs.get("performance") == "NOT MEASURED"
        and inputs.get("memory") == "NOT MEASURED"
        and inputs.get("final_holdout_opened") is False
        and inputs.get("winner_selected") is False,
        "preserve the complete genuine 103-owner and 108-reference V21 history",
    )
    v9_raw, _ = read_owner(*V9["document"][:2], expected_bytes=V9["document"][2])
    v9 = strict_document(v9_raw, "complete unchanged V9 machine contract")
    published = v9.get("published_history")
    original_evaluator = v9.get("original_evaluator")
    require(
        v9.get("schema") == "rebar-frozen-python-re-p0-candidate-protocol-v9"
        and v9.get("version") == 9
        and v9.get("suite_count") == SUITE_COUNT
        and v9.get("case_execution_denominator") == CASE_DENOMINATOR
        and v9.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and v9.get("source_family_count") == SOURCE_FAMILY_COUNT
        and v9.get("source_owner_count") == SOURCE_OWNER_COUNT
        and type(v9.get("original_suites")) is list
        and tuple(
            (record.get("id"), record.get("case_execution_count"))
            for record in v9["original_suites"]
        ) == SUITES
        and type(published) is dict
        and published.get("authoritative_counted_evidence_owner_count")
        == V21_EVIDENCE_OWNER_COUNT
        and published.get("authenticated_digest_addressed_history_paths")
        == V21_REFERENCE_PATH_COUNT
        and published.get("preserved_failed_campaign_evidence_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and type(original_evaluator) is dict
        and all(
            type(original_evaluator.get(role)) is dict
            and original_evaluator[role].get("path") == V3[role][0]
            and original_evaluator[role].get("sha256") == V3[role][1]
            for role in ("source", "protocol", "document")
        )
        and type(v9.get("runner")) is dict
        and v9["runner"].get("path") == V9["runner"][0]
        and v9["runner"].get("sha256") == V9["runner"][1]
        and type(v9.get("worker")) is dict
        and v9["worker"].get("path") == V9["worker"][0]
        and v9["worker"].get("sha256") == V9["worker"][1],
        "directly authenticate every original V9 suite and V3 owner without recursion",
    )
    current_raw, _ = read_owner(
        *V22["inputs"][:2], expected_bytes=V22["inputs"][2]
    )
    current = strict_document(current_raw, "complete current V22 overview input")
    corrected = current.get("corrected_c_original_campaign")
    require(
        current.get("schema") == "rebar-candidate-current-overview-v22-inputs"
        and current.get("version") == 22
        and current.get("suite_count") == SUITE_COUNT
        and current.get("full_case_denominator") == CASE_DENOMINATOR
        and current.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and current.get("repository_evidence_owner_count")
        == TOTAL_EVIDENCE_OWNER_COUNT
        and current.get("all_digest_addressed_history_path_count")
        == TOTAL_REFERENCE_PATH_COUNT
        and current.get("preserved_v21_repository_evidence_owner_count")
        == V21_EVIDENCE_OWNER_COUNT
        and current.get("preserved_v21_digest_addressed_history_path_count")
        == V21_REFERENCE_PATH_COUNT
        and current.get("new_corrected_c_campaign_repository_evidence_owner_count")
        == APPENDED_FAILURE_OWNER_COUNT
        and current.get("candidate_qualified_count") == 0
        and current.get("performance") == "NOT MEASURED"
        and current.get("memory") == "NOT MEASURED"
        and current.get("undefined_behavior") == "NOT MEASURED"
        and current.get("final_holdout_opened") is False
        and current.get("winner_selected") is False
        and type(corrected) is dict
        and corrected.get("status") == "FAIL"
        and corrected.get("actual_aggregate_process_count") == 1
        and corrected.get("actual_candidate_workers") == 0
        and corrected.get("completed_suite_count") == "NOT MEASURED"
        and corrected.get("semantic_mismatch_count") == "NOT MEASURED"
        and corrected.get("infrastructure_failure_count") == 1
        and corrected.get("infrastructure_failure_type") == "AttributeError"
        and corrected.get("infrastructure_failure_message") == APPENDED_FAILURE_ERROR
        and corrected.get("actual_v9_stdout_sha256")
        == APPENDED_FAILURE_CHILD_STDOUT_SHA256
        and corrected.get("new_repository_evidence_owner_count")
        == APPENDED_FAILURE_OWNER_COUNT
        and corrected.get("original_canonical_native_restored") is True
        and type(corrected.get("archive")) is dict
        and corrected["archive"].get("path") == APPENDED_FAILURE["archive"][0]
        and corrected["archive"].get("sha256") == APPENDED_FAILURE["archive"][1]
        and type(corrected.get("receipt")) is dict
        and corrected["receipt"].get("path") == APPENDED_FAILURE["receipt"][0]
        and corrected["receipt"].get("sha256") == APPENDED_FAILURE["receipt"][1],
        "directly authenticate current V22 and every unchanged real V2 failure owner",
    )
    summary_raw, _ = read_owner(
        *V22["summary"][:2], expected_bytes=V22["summary"][2]
    )
    summary = strict_document(summary_raw, "current V22 machine-readable overview")
    require(
        summary.get("schema") == "rebar-candidate-current-overview-v22-summary"
        and summary.get("status") == "PASS"
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("full_case_denominator") == CASE_DENOMINATOR
        and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and summary.get("repository_evidence_owner_count")
        == TOTAL_EVIDENCE_OWNER_COUNT
        and summary.get("authenticated_digest_addressed_history_paths")
        == TOTAL_REFERENCE_PATH_COUNT
        and summary.get("preserved_v21_repository_evidence_owner_count")
        == V21_EVIDENCE_OWNER_COUNT
        and summary.get("preserved_v21_authenticated_reference_path_count")
        == V21_REFERENCE_PATH_COUNT
        and summary.get("new_corrected_c_campaign_repository_evidence_owner_count")
        == APPENDED_FAILURE_OWNER_COUNT
        and summary.get("c_repaired_candidate_worker_count") == 0
        and summary.get("c_repaired_completed_suite_count") == "NOT MEASURED"
        and summary.get("c_repaired_verified_passing_case_count") == "NOT MEASURED"
        and summary.get("c_repaired_semantic_mismatch_count") == "NOT MEASURED"
        and summary.get("c_repaired_infrastructure_failure_count") == 1
        and summary.get("c_repaired_original_campaign_status") == "FAIL"
        and summary.get("original_canonical_native_restored") is True
        and summary.get("qualified_candidate_count") == 0
        and summary.get("clock_samples") == 0
        and summary.get("hidden_cases_read") == 0
        and summary.get("timing_trials_run") == 0
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("memory") == "NOT MEASURED"
        and summary.get("undefined_behavior") == "NOT MEASURED"
        and summary.get("final_holdout_opened") is False
        and summary.get("winner_selected") is False,
        "reject a misleading, incomplete, measured, or substituted current V22 overview",
    )
    failure = verify_appended_failure()
    return owners, failure, {
        "schema": summary["schema"],
        "status": summary["status"],
        "source_sha256": V22["source"][1],
        "inputs_sha256": V22["inputs"][1],
        "summary_sha256": V22["summary"][1],
        "svg_sha256": V22["svg"][1],
        "historical_evidence_owner_count": TOTAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count": TOTAL_REFERENCE_PATH_COUNT,
    }


def original_v9_context_arguments() -> list[str]:
    return [
        "--verify-frozen-context",
        "--source-sha256",
        V9["runner"][1],
        "--worker-source-sha256",
        V9["worker"][1],
        "--protocol-sha256",
        V9["protocol"][1],
        "--document-sha256",
        V9["document"][1],
        "--producer-source-sha256",
        V3["source"][1],
        "--producer-protocol-sha256",
        V3["protocol"][1],
        "--producer-document-sha256",
        V3["document"][1],
    ]


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    runtime()
    adapter_owners = verify_source_contract(options)
    historical_owners, appended_failure, current_overview = verify_static_history()
    runner, runner_owner = load_original_runner()
    original_options = runner.parse_arguments(original_v9_context_arguments())
    worker, worker_owner = runner.load_worker(original_options)
    worker_options = runner.worker_context_options(original_options, worker)
    require(
        isinstance(worker, types.ModuleType)
        and worker.SCHEMA == V7_WORKER_SCHEMA
        and worker.RUNNER_SCHEMA == V9_RUNNER_SCHEMA
        and worker.SOURCE_RELATIVE == V9["worker"][0]
        and worker.RUNNER_RELATIVE == V9["runner"][0]
        and tuple(worker.SUITES) == SUITES
        and worker.CASE_DENOMINATOR == CASE_DENOMINATOR
        and type(worker_owner) is dict
        and worker_owner.get("relative") == V9["worker"][0]
        and worker_owner.get("sha256") == V9["worker"][1]
        and worker_owner.get("size_bytes") == V9["worker"][2]
        and isinstance(worker_options, argparse.Namespace)
        and worker_options.verify_frozen_context is True
        and worker_options.source_sha256 == V9["worker"][1]
        and worker_options.runner_source_sha256 == V9["runner"][1]
        and worker_options.protocol_sha256 == V9["protocol"][1]
        and worker_options.document_sha256 == V9["document"][1]
        and worker_options.producer_source_sha256 == V3["source"][1]
        and worker_options.producer_protocol_sha256 == V3["protocol"][1]
        and worker_options.producer_document_sha256 == V3["document"][1]
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "directly authenticate both genuine worker namespaces without recursive context",
    )
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "read_only": True,
        "adapter_source_owners": adapter_owners,
        "immutable_original_runner_owner": runner_owner,
        "immutable_original_worker_owner": worker_owner,
        "authenticated_static_history_owners": historical_owners,
        "preserved_appended_v2_failure": appended_failure,
        "authenticated_current_v22_overview": current_overview,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "preserved_v21_evidence_owner_count": V21_EVIDENCE_OWNER_COUNT,
        "preserved_v21_authenticated_reference_path_count": V21_REFERENCE_PATH_COUNT,
        "preserved_original_failed_campaign_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "appended_failed_v2_evidence_owner_count": APPENDED_FAILURE_OWNER_COUNT,
        "historical_evidence_owner_count": TOTAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count": TOTAL_REFERENCE_PATH_COUNT,
        "v3_original_source_authenticated_before_activation": True,
        "recursive_v3_frozen_context_called": False,
        "recursive_v9_frozen_context_called": False,
        "v3_frozen_context_called_after_activation": False,
        "immutable_original_v9_schema": V9_RUNNER_SCHEMA,
        "immutable_original_worker_schema": V7_WORKER_SCHEMA,
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


def original_v9_run_arguments(options: argparse.Namespace) -> list[str]:
    arguments = [
        "--run",
        "--candidate",
        options.candidate,
        "--label",
        options.label,
        "--build-label",
        options.build_label,
        "--activation-root",
        options.activation_root,
    ]
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
        field = name.replace("-", "_") + "_sha256"
        arguments.extend(("--" + name + "-sha256", checked_digest(getattr(options, field), field)))
    return arguments


def authenticate_future_controller(options: argparse.Namespace) -> dict[str, Any]:
    owners: dict[str, dict[str, Any]] = {}
    for role in ("source", "protocol", "document"):
        field = "controller_" + role + "_sha256"
        raw, owner = read_owner(CONTROLLER_V3_PATHS[role], getattr(options, field))
        owners[role] = owner
        if role == "document":
            document = strict_document(raw, "separately frozen future crash-safe V3 controller")
            require(
                document.get("schema")
                == "rebar-owned-repaired-c-original-campaign-v3-source-freeze"
                and document.get("suite_count") == SUITE_COUNT
                and document.get("case_execution_denominator") == CASE_DENOMINATOR
                and document.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT,
                "require the complete separately frozen, fail-safe V3 outer controller",
            )
    return owners


def run_actual_candidate(options: argparse.Namespace) -> dict[str, Any]:
    runtime()
    verify_source_contract(options)
    verify_static_history()
    authenticate_future_controller(options)
    runner, _ = load_original_runner()
    original_options = runner.parse_arguments(original_v9_run_arguments(options))
    result = execute_immutable_original_run(runner, original_options)
    require(
        type(result) is dict
        and result.get("schema") == V9_RUNNER_SCHEMA + "-published-complete-candidate"
        and result.get("status") in ("PASS", "FAIL")
        and result.get("candidate_family") == "c"
        and result.get("label") == original_options.label
        and result.get("suite_count") == SUITE_COUNT
        and result.get("case_execution_denominator") == CASE_DENOMINATOR
        and result.get("completed_suite_count") == SUITE_COUNT
        and result.get("restoration_status") == "PASS"
        and result.get("performance") == "NOT MEASURED"
        and result.get("memory") == "NOT MEASURED"
        and result.get("holdout") == "NOT OPENED"
        and result.get("winner_selected") is False,
        "publish only an unchanged complete original V9 aggregate after restoration",
    )
    return result


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=("c",))
    parser.add_argument("--label")
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    for name in (
        "adapter-source",
        "adapter-protocol",
        "adapter-contract",
        "controller-source",
        "controller-protocol",
        "controller-document",
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
    own = (
        "adapter_source_sha256",
        "adapter_protocol_sha256",
        "adapter_contract_sha256",
    )
    controller = (
        "controller_source_sha256",
        "controller_protocol_sha256",
        "controller_document_sha256",
    )
    base_pins = (
        "source_sha256",
        "worker_source_sha256",
        "protocol_sha256",
        "document_sha256",
        "producer_source_sha256",
        "producer_protocol_sha256",
        "producer_document_sha256",
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
    actual = ("candidate", "label", "build_label", "activation_root")
    if options.self_test:
        require(
            all(getattr(options, name) is None for name in (*own, *controller, *base_pins, *actual)),
            "synthetic source-only tests cannot authorize a controller or candidate",
        )
        return options
    for name in own:
        checked_digest(getattr(options, name), name)
    if options.verify_frozen_context:
        require(
            all(getattr(options, name) is None for name in (*controller, *base_pins, *actual)),
            "pre-activation frozen context cannot select or execute a candidate",
        )
        return options
    require(
        all(getattr(options, name) is not None for name in (*controller, *base_pins, *actual))
        and options.candidate == "c",
        "run only beneath an independently frozen crash-safe V3 controller and live V5 pins",
    )
    for name in (*controller, *base_pins):
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
        require(len(raw) <= MAX_REPORT_BYTES, "bound every complete adapter result")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        result = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__
            ),
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "historical_evidence_owner_count": TOTAL_EVIDENCE_OWNER_COUNT,
            "historical_authenticated_reference_count": TOTAL_REFERENCE_PATH_COUNT,
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
        raw = canonical(result)
        if len(raw) > MAX_REPORT_BYTES:
            result["traceback"] = ["complete traceback exceeded report limit"]
            raw = canonical(result)
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
