#!/usr/bin/env python3
"""Run one original P0 suite against the pinned first-party C candidate only.

Source-only commands never load candidates, read compressed evidence, or run
benchmarks.  Matching uses the corrected, independently published Python 3.14.6
reference and a separately authenticated first-party engine.
"""

from __future__ import annotations

import argparse
import _ctypes
import _imp
import _io
import _posixsubprocess
import _socket
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
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_worker_v8.py"
RUNNER_RELATIVE = "tools/run_frozen_p0_candidate_v10.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v10.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v8"
RUNNER_SCHEMA = "rebar-frozen-python-re-p0-candidate-v10"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
ORIGINAL_PRODUCER = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v4.py",
        "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md",
        "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
    ),
    "document": (
        "oracle/phase2/six-family-p0-producer-v4.json",
        "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
    ),
}
AUDITABLE_PREDECESSORS = {
    "worker_v7": {
        "path": "tools/run_frozen_p0_candidate_worker_v7.py",
        "sha256":
            "855c59acdc0b5270493ece8fc39548a89e0febf94d6b186ac9f0e5a50754f68f",
    },
    "runner_v9": {
        "path": "tools/run_frozen_p0_candidate_v9.py",
        "sha256":
            "1511dac06dab5ce319b4dd09cb6f8c5a12160c48cc0dbbdfa7e7fe3f0d426702",
    },
}

REPAIR = {
    "source": ("tools/apply_owned_first_party_source_repair_v1.py",
               "c04bbc8e7bc45bdbe1fb9eb93942286f5b32b39aef554db15b8b1acd9cc8cd99"),
    "protocol": ("oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md",
                 "1a2e83caaca5cb43fc82445c2a4fc3097bc3d51bdfc568783b8815797b8c63f5"),
    "document": ("oracle/phase2/first-party-source-repair-v1.json",
                 "8f1a5676bbef5f2ef560d03fef910bf4ed3a4df029ecc0c638e3fa971206dab5"),
}
BUILD = {
    "source": ("tools/reproduce_owned_c_pickle_source_build_v15.py",
               "91bc1985ac1edad757a3b027840db3f08aa97a781df1542e33b39d39f04aa7d8"),
    "protocol": ("oracle/phase2/C-PICKLE-SOURCE-BUILD-V15.md",
                 "fab2219a4c4a0cf78acfe8adbb039aba591a450409d9cc75347d552d9d0e4727"),
    "document": ("oracle/phase2/c-pickle-source-build-v15.json",
                 "7fb1409eb228deb034626efb9b5bb1781c1cd139343d18e87acdac6deab97285"),
}
# Actual or read-only verification is allowed only after the independently
# reviewed V5 source freeze itself has been committed and published.
ACTIVATION_V5 = {
    "source": ("tools/activate_verified_native_candidate_v5.py",
               "bdfcb93e4ac3f436474cf82725165c92b61c8982efff0bf113900cbce3e8aff5"),
    "protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V5.md",
                 "4693558f9796a0fbf38326fda3a86b2cf19348598b21eab60610df6ee7f241bc"),
    "document": ("oracle/phase2/verified-native-activation-v5.json",
                 "a580c6b745c867a69f1f017506c1feec8310aa3070bfd58abd006740b01948da"),
}
V39_OWNERS = {
    "source": (
        "tools/render_candidate_current_overview_v39.py",
        "8adb7202644da2d19a4d2f50fe191de8d84007ce9b654a427a61fb4ea883c6b5",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v39.inputs.json",
        "22e740d2f7a22e4bd485c5d6e83204bfd2c529f1b87dd041d4ed604849b69d6b",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v39.json",
        "d25c486e36d82069c718f82a1f6281295d539606dcd72a0a6c2c295f5a4e4ca6",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v39.svg",
        "eecc366a7e14e3bee67a801cbf4b07e848af3659a82cc0715a90525c05652a9a",
    ),
}
V40_OWNERS = {
    "source": (
        "tools/render_candidate_current_overview_v40.py",
        "15dc12f2d6a3c329d326f8d5b53bd2b1db7e82d01bb7c55e1178bd4ec0587c14",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v40.inputs.json",
        "a05ee04da984b618781bc31fe0deba6d1daf7c44256d7804e539ddd1392a2ffd",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v40.json",
        "5e9f2216fc2a0ab4742d36a1aa49c422880a8ae17e3e1534da9b362ca0eeda92",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v40.svg",
        "7e9189fb06410903b9f5d851648893e7984b8ecd1ba7d42c73329c1f985857e3",
    ),
}
CORRECTED_REFERENCE_OWNERS = {
    "source": ("tools/verify_owned_public_type_reference_context_v1.py",
               "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc"),
    "protocol": ("oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md",
                 "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018"),
    "document": ("oracle/phase1/p0-public-type-reference-context-v1.json",
                 "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b"),
    "receipt": (
        "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json",
        "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966",
    ),
}
CORRECTED_PUBLIC_RECORDS_SHA256 = "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
HISTORICAL_PUBLIC_RECORDS_SHA256 = "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
CORRECTED_PUBLIC_COHORT_RECORDS_SHA256 = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256 = "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
CORRECTED_PUBLIC_COHORT_CASE_COUNT = 96
CORRECTED_PUBLIC_REFERENCE_PIDS = (81, 82)
C15_BUILD_LABEL = "phase2-v15-c-pickle-original-p0"
C15_NATIVE_SHA256 = "aed6e9c2fbe31ee3798c74bc6fe896494f1a3bfed41ff25dcfef6905e7b8e610"
C15_BUILD_ARCHIVE_SHA256 = "7e95decc5937b76b2f1aa86706663a57edcea8d3a705ad9b3710c4ec2b61a4de"
C15_BUILD_RECEIPT_RELATIVE = "oracle/phase2/evidence/native-source-build-v15-c-phase2-v15-c-pickle-original-p0-publication-receipt.json"
C15_BUILD_RECEIPT_SHA256 = "ad196290f8f08b1547ffefc02bd1cdaff52557f792b8a32ea93c67f6ee857643"
PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT = 30

ADAPTER_RELATIVE = "candidates/vm_candidate.py"
ADAPTER_SHA256 = "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
ADAPTER_BYTES = 60707
ORIGINAL_C_RELATIVE = "candidates/_vm_native.c"
ORIGINAL_C_SHA256 = "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
ORIGINAL_C_BYTES = 218185
DERIVED_C_SHA256 = "8b35fba5b565ae18c5b9c180bec1dfbfb46b75bf3db7421626da4a73cdda2b94"
DERIVED_C_BYTES = 219227
NATIVE_RELATIVE = "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
FAMILY = "c"
FAMILY_NAMES = ("rust", "c", "zig", "cpp", "go", "fortran")
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
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_COMPRESSED_SUITE_BYTES = 128 * 1024 * 1024
MAX_UNCOMPRESSED_SUITE_BYTES = 2 * 1024 * 1024 * 1024
MAX_PUBLIC_REPORT_BYTES = 32 * 1024 * 1024
MAX_LABEL_BYTES = 48
MAX_ERROR_BYTES = 64 * 1024


class CandidateGateError(Exception):
    """Reject incomplete, substituted, or unsafe candidate evidence."""


class SourceOnlyEffect(CandidateGateError):
    """A source-only check attempted a prohibited external effect."""


def new_worker_effect_ledger(options: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-authorized-actual-effect-ledger",
        "mode": "AUTHORIZED ACTUAL CANDIDATE SUITE",
        "candidate_family": options.candidate,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "label": options.label,
        "suite": options.suite,
        "phase": "before-candidate-preflight",
        "actual_candidate_workers": 0,
        "actual_worker_process_id": None,
        "candidate_observation_attempted": False,
        "candidate_observation_completed": False,
        "actual_reference_workers": 0,
        "actual_native_activations": 0,
        "actual_native_promotions": 0,
        "actual_native_library_loads": "NOT MEASURED",
        "actual_source_builds": 0,
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


def worker_entry_failure_result(
    error: BaseException,
    ledger: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(ledger) is dict
            and ledger.get("schema")
            == SCHEMA + "-authorized-actual-effect-ledger"
            and ledger.get("mode") == "AUTHORIZED ACTUAL CANDIDATE SUITE",
            "never represent a started candidate worker as a source-only failure")
    retained = copy.deepcopy(dict(ledger))
    retained["effect_ledger_schema"] = retained.pop("schema")
    if any(retained.get(name) is True for name in (
        "archive_publication_attempted", "receipt_publication_attempted",
        "public_report_serialization_attempted", "public_report_write_attempted",
        "public_report_flush_attempted",
    )):
        retained["publication_status"] = "FAIL"
    return {
        **retained,
        "schema": SCHEMA + "-entry-failure",
        "status": "FAIL",
        "semantic_mismatch_count": "NOT MEASURED",
        "all_original_records_and_mismatches_preserved": False,
        "source_only_zero_effects_claimed": False,
        "candidate_qualified": False,
        "error_type": type(error).__qualname__,
        "error_message": bounded_error(error),
        "winner_selected": False,
    }


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CandidateGateError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete bytes only")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(part in "0123456789abcdef" for part in value),
            "require an exact independent SHA-256: " + name)
    return value


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CandidateGateError("reject noncanonical or invalid evidence") from error


def bounded_public_report(
    value: Any,
    maximum: int = MAX_PUBLIC_REPORT_BYTES,
) -> bytes:
    require(type(maximum) is int and maximum > 0,
            "require a positive caller-visible candidate report bound")
    raw = canonical(value)
    require(len(raw) <= maximum,
            "never truncate or publish an oversized actual candidate report")
    return raw


def bounded_error(error: BaseException) -> str:
    raw = str(error).encode("utf-8", "backslashreplace")
    if len(raw) > MAX_ERROR_BYTES:
        raw = raw[:MAX_ERROR_BYTES] + b" [error summary truncated]"
    return raw.decode("utf-8", "replace")


def exact_json(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(type(key) is str and key not in result,
                    "reject a duplicate key in " + label)
            result[key] = value
        return result

    def nonfinite(value: str) -> Any:
        raise CandidateGateError("reject nonfinite JSON in " + label)

    try:
        result = json.loads(raw, object_pairs_hook=pairs,
                            parse_constant=nonfinite)
    except (ValueError, UnicodeError, TypeError) as error:
        raise CandidateGateError("reject malformed JSON in " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "require complete canonical JSON in " + label)
    return result


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value)
            and "\\" not in value and "\x00" not in value,
            "require a safe, exact relative owner")
    pieces = value.split("/")
    require(all(piece not in ("", ".", "..") for piece in pieces),
            "reject an absolute, linked, or escaping owner")
    return value


def checked_label(value: Any, label: str = "label") -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
            and all(part.isascii() and (part.isalnum() or part in "-_")
                    for part in value),
            "require an exact bounded safe " + label)
    return value


def runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only the isolated, pinned CPython 3.14.6 V8 worker")


def read_owner(relative: str, expected: str, *, maximum: int = MAX_SOURCE_BYTES,
               size: int | None = None,
               private: bool = False) -> tuple[bytes, dict[str, Any]]:
    relative = checked_relative(relative)
    checked_digest(expected, relative)
    require(type(maximum) is int and maximum > 0,
            "require a positive exact owner bound")
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
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum,
                "reject an absent, substituted, linked, or oversized owner: " + relative)
        if private:
            require(stat.S_IMODE(before.st_mode) == 0o600,
                    "require a genuine owner-only evidence file: " + relative)
        if size is not None:
            require(before.st_size == size, "reject altered owner bytes: " + relative)
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(part) is bytes and bool(part),
                    "reject truncated original evidence: " + relative)
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "reject concealed owner bytes: " + relative)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size)
                and digest(raw) == expected,
                "reject changed exact evidence: " + relative)
        return raw, {
            "relative": relative, "sha256": expected,
            "size_bytes": after.st_size, "device": after.st_dev,
            "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def frozen_module(relative: str, expected: str, name: str) -> types.ModuleType:
    raw, _ = read_owner(relative, expected)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {key: 0 for key in (
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "source_builds", "native_activations",
        "native_promotions", "native_libraries_loaded", "interpreter_creations",
        "threads_started", "network_requests", "clock_samples",
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
        original = getattr(owner, name)

        def forbidden(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyEffect("source-only V8 worker forbids " + name)

        originals.append((owner, name, original))
        setattr(owner, name, forbidden)

    try:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (os, "read"), (os, "stat"), (os, "lstat"),
                            (Path, "open"), (Path, "read_bytes"),
                            (Path, "read_text")):
            block(owner, name, "blocked_reads")
        for owner, name in ((os, "write"), (os, "unlink"), (os, "remove"),
                            (os, "mkdir"), (os, "makedirs"), (os, "replace"),
                            (os, "rename"), (os, "fsync"),
                            (Path, "write_bytes"), (Path, "write_text"),
                            (Path, "touch"), (tempfile, "mkstemp"),
                            (tempfile, "mkdtemp")):
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
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)


def validate_history(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and value.get("authoritative_counted_evidence_owner_count")
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and value.get("authenticated_digest_addressed_history_paths")
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and value.get("preserved_failed_campaign_evidence_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and value.get("previous_repaired_c_infrastructure_failure_count") == 13
        and value.get("previous_repaired_c_verified_passing_case_count") == 0
        and value.get("previous_repaired_c_original_native_restored") is True
        and value.get("go_full_campaign_status") == "FAIL"
        and value.get("go_full_campaign_suite_count") == 13
        and value.get("go_full_campaign_semantic_mismatch_count") == 4518
        and value.get("go_full_campaign_infrastructure_failure_count") == 4
        and value.get("go_restoration_status") == "PASS"
        and value.get("qualified_candidate_count") == 0,
        "reject changed V40 current 164-owner, 169-reference, 30-failure history",
    )
    return value


def synthetic_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-source-freeze",
        "family": FAMILY,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "original_c_source_bytes": ORIGINAL_C_BYTES,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "derived_c_source_bytes": DERIVED_C_BYTES,
        "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "original_producer_protocol_sha256": ORIGINAL_PRODUCER["protocol"][1],
        "original_producer_document_sha256": ORIGINAL_PRODUCER["document"][1],
        "nested_producer_sha256": ORIGINAL_PRODUCER["source"][1],
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
        "current_overview_v40_sha256": V40_OWNERS["summary"][1],
        "preserved_overview_v39_sha256": V39_OWNERS["summary"][1],
        "current_c15_native_sha256": C15_NATIVE_SHA256,
        "maximum_public_report_bytes": MAX_PUBLIC_REPORT_BYTES,
        "suite_ids": [name for name, _count in SUITES],
        "suite_case_counts": [count for _name, count in SUITES],
        "auditable_predecessors": copy.deepcopy(AUDITABLE_PREDECESSORS),
        "history": {
            "authoritative_counted_evidence_owner_count":
                HISTORICAL_EVIDENCE_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths":
                HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
            "preserved_failed_campaign_evidence_owner_count": 30,
            "previous_repaired_c_infrastructure_failure_count": 13,
            "previous_repaired_c_verified_passing_case_count": 0,
            "previous_repaired_c_original_native_restored": True,
            "go_full_campaign_status": "FAIL",
            "go_full_campaign_suite_count": 13,
            "go_full_campaign_semantic_mismatch_count": 4518,
            "go_full_campaign_infrastructure_failure_count": 4,
            "go_restoration_status": "PASS",
            "qualified_candidate_count": 0,
        },
        "candidate_qualified_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_synthetic(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and canonical(value) == canonical(synthetic_contract()),
        "reject changed V4 producer, current V40, preserved V39, original cases, or boundary",
    )
    validate_history(value["history"])
    require(
        len(SUITES) == SUITE_COUNT
        and len({name for name, _count in SUITES}) == SUITE_COUNT
        and sum(count for _name, count in SUITES) == CASE_DENOMINATOR,
        "preserve all thirteen original suites and exactly 31,237 cases",
    )
    return value


def _synthetic_role(record: Any) -> dict[str, Any]:
    require(
        type(record) is dict
        and record.get("role") in ("candidate", "reference")
        and record.get("status") in ("PASS", "FAIL")
        and type(record.get("mismatch_count")) is int
        and record["mismatch_count"] >= 0
        and type(record.get("all_mismatches")) is list
        and len(record["all_mismatches"]) == record["mismatch_count"]
        and type(record.get("all_original_records_preserved")) is bool
        and record["all_original_records_preserved"] is True
        and (record["status"] == "PASS") is (record["mismatch_count"] == 0),
        "reject an inverted role, false PASS, omitted records, or mismatch loss",
    )
    return record


def _expect_synthetic_rejection(function: Any, *values: Any) -> None:
    try:
        function(*values)
    except (CandidateGateError, ValueError, TypeError, KeyError):
        return
    raise CandidateGateError("accepted an adversarial V7 source-only control")


def synthetic_worker_entry_fault_controls() -> dict[str, int]:
    accepted = rejected = 0
    options = argparse.Namespace(
        candidate=FAMILY,
        label="synthetic-worker-entry",
        suite=SUITES[0][0],
    )
    for phase in (
        "canonical-serialization",
        "oversized-report",
        "archive-publication",
        "receipt-publication",
        "public-write",
        "public-flush",
    ):
        ledger = new_worker_effect_ledger(options)
        ledger.update({
            "phase": phase,
            "actual_candidate_workers": 1,
            "actual_worker_process_id": 9101,
            "candidate_observation_attempted": True,
            "actual_native_activations": 1,
            "actual_native_promotions": 1,
            "actual_source_builds": 1,
            "actual_reference_workers": 2,
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
        except (CandidateGateError, OSError) as error:
            failure = worker_entry_failure_result(error, ledger)
            require(failure.get("status") == "FAIL"
                    and failure.get("actual_candidate_workers") == 1
                    and failure.get("actual_worker_process_id") == 9101
                    and failure.get("actual_native_activations") == 1
                    and failure.get("actual_native_promotions") == 1
                    and failure.get("actual_source_builds") == 1
                    and failure.get("actual_reference_workers") == 2
                    and failure.get("phase") == phase
                    and failure.get("publication_status") == "FAIL"
                    and failure.get("semantic_mismatch_count") == "NOT MEASURED"
                    and failure.get("source_only_zero_effects_claimed") is False,
                    "never erase actual worker effects after " + phase)
            rejected += 1
        else:
            raise CandidateGateError("accepted a synthetic worker entry fault")
    accepted += 1
    return {"accepted": accepted, "rejected": rejected}


def source_self_test() -> dict[str, Any]:
    rejected = 0
    with source_only_boundary() as effects:
        document = validate_synthetic(synthetic_contract())
        for name, changed in (
            ("schema", SCHEMA),
            ("family", "rust"),
            ("suite_count", 12),
            ("case_execution_denominator", 31236),
            ("named_private_waiver_count", 12),
            ("source_family_count", 5),
            ("source_owner_count", 24),
            ("runnable_candidate_family_count", 0),
            ("runnable_candidate_family_count", 6),
            ("runnable_candidate_families", ["rust"]),
            ("runnable_candidate_families", list(FAMILY_NAMES)),
            ("six_family_inventory_is_source_only", False),
            ("original_c_source_sha256", DERIVED_C_SHA256),
            ("derived_c_source_sha256", ORIGINAL_C_SHA256),
            ("original_c_source_bytes", DERIVED_C_BYTES),
            ("derived_c_source_bytes", ORIGINAL_C_BYTES),
            ("original_producer_sha256", "0" * 64),
            ("original_producer_sha256",
             "36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33"),
            ("original_producer_protocol_sha256", "0" * 64),
            ("original_producer_document_sha256", "0" * 64),
            ("nested_producer_sha256", "0" * 64),
            ("expected_v15_build_process_count", 13),
            ("expected_actual_original_worker_count", 12),
            ("maximum_public_report_bytes", MAX_PUBLIC_REPORT_BYTES + 1),
            ("candidate_qualified_count", 1),
            ("candidate_correctness", "PASS"),
            ("actual_candidate_workers", 1),
            ("actual_reference_workers", 1),
            ("actual_source_builds", 1),
            ("actual_native_activations", 1),
            ("performance", "PASS"),
            ("memory", "PASS"),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("holdout", "OPEN"),
            ("winner_selected", True),
        ):
            changed_document = copy.deepcopy(document)
            changed_document[name] = changed
            _expect_synthetic_rejection(validate_synthetic, changed_document)
            rejected += 1
        for key, changed in (
            ("authoritative_counted_evidence_owner_count", 71),
            ("authoritative_counted_evidence_owner_count", 108),
            ("authenticated_digest_addressed_history_paths", 76),
            ("authenticated_digest_addressed_history_paths", 103),
            ("preserved_failed_campaign_evidence_owner_count", 29),
            ("previous_repaired_c_infrastructure_failure_count", 12),
            ("previous_repaired_c_verified_passing_case_count", 1),
            ("previous_repaired_c_original_native_restored", False),
            ("go_full_campaign_status", "PASS"),
            ("go_full_campaign_suite_count", 12),
            ("go_full_campaign_semantic_mismatch_count", 4517),
            ("go_full_campaign_infrastructure_failure_count", 3),
            ("go_restoration_status", "FAIL"),
            ("qualified_candidate_count", 1),
        ):
            changed_document = copy.deepcopy(document)
            changed_document["history"][key] = changed
            _expect_synthetic_rejection(validate_synthetic, changed_document)
            rejected += 1
        for index, (name, count) in enumerate(SUITES):
            for field, changed in (
                ("suite_ids", name + "-forged"),
                ("suite_case_counts", count + 1),
            ):
                altered = copy.deepcopy(document)
                altered[field][index] = changed
                _expect_synthetic_rejection(validate_synthetic, altered)
                rejected += 1
        valid_role = {
            "role": "candidate",
            "status": "PASS",
            "mismatch_count": 0,
            "all_mismatches": [],
            "all_original_records_preserved": True,
        }
        _synthetic_role(valid_role)
        for key, value in (
            ("role", "external"),
            ("role", None),
            ("status", "OK"),
            ("status", "FAIL"),
            ("mismatch_count", 1),
            ("mismatch_count", -1),
            ("mismatch_count", True),
            ("all_mismatches", [{"lost": True}]),
            ("all_mismatches", None),
            ("all_original_records_preserved", False),
        ):
            altered = copy.deepcopy(valid_role)
            altered[key] = value
            _expect_synthetic_rejection(_synthetic_role, altered)
            rejected += 1
        for raw in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n', b"[]\n"):
            _expect_synthetic_rejection(exact_json, raw, "synthetic")
            rejected += 1
        for bad in (
            "", "/escape", "../escape", "a//b", "a/../b", "a\\b",
        ):
            _expect_synthetic_rejection(checked_relative, bad)
            rejected += 1
        for bad in (
            None, "", "g" * 64, "a" * 63, "a" * 65, 1,
        ):
            _expect_synthetic_rejection(checked_digest, bad, "synthetic")
            rejected += 1
        for key, value in copy.deepcopy(document).items():
            if key in ("schema", "family", "suite_ids", "suite_case_counts",
                       "auditable_predecessors", "history"):
                continue
            for forged in (None, [], {}):
                altered = copy.deepcopy(document)
                altered[key] = forged
                _expect_synthetic_rejection(validate_synthetic, altered)
                rejected += 1
        probes = (
            ("blocked_reads",
             lambda: builtins.open("/tmp/rebar-v7-worker-forbidden", "rb")),
            ("blocked_reads",
             lambda: os.open("/tmp/rebar-v7-worker-forbidden", os.O_RDONLY)),
            ("blocked_writes", lambda: os.write(-1, b"forbidden")),
            ("blocked_processes",
             lambda: subprocess.run(("forbidden-v7-worker",))),
            ("blocked_imports",
             lambda: importlib.import_module("candidates.vm_candidate")),
            ("blocked_threads",
             lambda: threading.Thread(target=lambda: None).start()),
            ("blocked_network",
             lambda: socket.create_connection(("127.0.0.1", 1))),
            ("blocked_clocks", lambda: time.perf_counter_ns()),
            ("blocked_reads", lambda: _io.open("/tmp/rebar-v8-worker-forbidden", "rb")),
            ("blocked_processes", lambda: _posixsubprocess.fork_exec()),
            ("blocked_threads", lambda: _thread.start_new_thread(lambda: None, ())),
            ("blocked_native_loads", lambda: _ctypes.dlopen("forbidden-v8.so")),
            ("blocked_native_loads", lambda: ctypes.CDLL("forbidden-v8.so")),
            ("blocked_low_level_imports", lambda: _imp.create_dynamic(None)),
            ("blocked_decompression", lambda: zlib.decompress(b"forbidden")),
            ("blocked_decompression", lambda: gzip.decompress(b"forbidden")),
        )
        for counter, probe in probes:
            before = effects[counter]
            _expect_synthetic_rejection(probe)
            require(effects[counter] == before + 1,
                    "verify every blocked V7 source-only external effect")
            rejected += 1
        entry_faults = synthetic_worker_entry_fault_controls()
        rejected += entry_faults["rejected"]
        require(rejected >= 160,
                "require substantial V3/V21/nested/role source-only controls")
        measured = dict(effects)
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_synthetic_controls": 2 + entry_faults["accepted"],
        "rejected_hostile_controls": rejected,
        "synthetic_entry_fault_controls": entry_faults,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "historical_evidence_owner_count": HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "nested_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "source_only_effects": measured,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_native_activations": 0,
        "actual_source_builds": 0,
        "actual_reference_workers": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified_count": 0,
        "winner_selected": False,
    }

def require_activation_pins() -> None:
    for name, (relative, fingerprint) in ACTIVATION_V5.items():
        checked_relative(relative)
        checked_digest(fingerprint, "coordinator-released V5 " + name)


def load_original_evaluator(options: argparse.Namespace) -> types.ModuleType:
    require(
        checked_digest(options.producer_source_sha256, "V4 producer source")
        == ORIGINAL_PRODUCER["source"][1]
        and checked_digest(
            options.producer_protocol_sha256,
            "V4 producer protocol",
        ) == ORIGINAL_PRODUCER["protocol"][1]
        and checked_digest(
            options.producer_document_sha256,
            "V4 producer document",
        ) == ORIGINAL_PRODUCER["document"][1],
        "require all three caller-pinned exact corrected original V4 owners",
    )
    for name, (relative, expected) in sorted(ORIGINAL_PRODUCER.items()):
        supplied = getattr(options, "producer_" + name + "_sha256")
        require(supplied == expected,
                "reject obsolete, missing, or substituted V4 owner: " + name)
        read_owner(relative, expected)
    module = frozen_module(
        ORIGINAL_PRODUCER["source"][0],
        options.producer_source_sha256,
        "_rebar_frozen_original_six_family_producer_v4_for_worker_v8",
    )
    require(
        module.SCHEMA == "rebar-owned-six-family-original-p0-producer-v4"
        and module.SOURCE_RELATIVE == ORIGINAL_PRODUCER["source"][0]
        and module.PROTOCOL_RELATIVE == ORIGINAL_PRODUCER["protocol"][0]
        and module.DOCUMENT_RELATIVE == ORIGINAL_PRODUCER["document"][0]
        and module.SUITE_COUNT == SUITE_COUNT
        and module.CASE_DENOMINATOR == CASE_DENOMINATOR
        and module.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
        and module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and module.CURRENT_REFERENCE_LOWER_BOUND
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and module.PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and [(item.name, item.case_count) for item in module.SUITES]
        == list(SUITES)
        and module.CORRECTED_PUBLIC_RECORDS_SHA256
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and module.HISTORICAL_PUBLIC_RECORDS_SHA256
        == HISTORICAL_PUBLIC_RECORDS_SHA256
        and module.CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and module.CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256
        == CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256
        and module.CORRECTED_PUBLIC_COHORT_CASE_COUNT
        == CORRECTED_PUBLIC_COHORT_CASE_COUNT
        and tuple(module.CORRECTED_PUBLIC_REFERENCE_PIDS)
        == CORRECTED_PUBLIC_REFERENCE_PIDS
        and tuple(module.FAMILIES) == FAMILY_NAMES,
        "require all six genuine V4 first-party families and the corrected Python reference",
    )
    spec = module.family_spec(FAMILY)
    require(
        spec.name == FAMILY
        and spec.combined_native is True
        and tuple(spec.source_owners) == (
            (ADAPTER_RELATIVE, ADAPTER_SHA256, ADAPTER_BYTES),
            (ORIGINAL_C_RELATIVE, ORIGINAL_C_SHA256, ORIGINAL_C_BYTES),
        ),
        "never substitute derived private bytes for the original C source spec",
    )
    document_raw, _ = read_owner(
        ORIGINAL_PRODUCER["document"][0],
        options.producer_document_sha256,
    )
    producer_document = module.decode_document(
        document_raw,
        "independently pinned corrected original V4 source contract",
        canonical_required=True,
    )
    module.validate_protocol_document(producer_document)
    require(
        producer_document.get("corrected_candidate_context_public_type_reference", {})
        .get("records_sha256") == CORRECTED_PUBLIC_RECORDS_SHA256
        and producer_document.get("corrected_candidate_context_public_type_reference", {})
        .get("cache_records_sha256") == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and producer_document.get("corrected_candidate_context_public_type_reference", {})
        .get("c_pattern_equality_failure_waived") is False,
        "never match against the historical script-context vector or waive C equality",
    )
    return module


def mapped_owners(mapping: Mapping[str, tuple[str, str]]) -> dict[str, Any]:
    return {
        name: {"path": relative, "sha256": fingerprint}
        for name, (relative, fingerprint) in sorted(mapping.items())
    }


def expected_protocol_document(
    options: argparse.Namespace,
    producer: types.ModuleType,
) -> dict[str, Any]:
    require(
        options.producer_source_sha256 == ORIGINAL_PRODUCER["source"][1]
        and options.producer_protocol_sha256
        == ORIGINAL_PRODUCER["protocol"][1]
        and options.producer_document_sha256
        == ORIGINAL_PRODUCER["document"][1],
        "bind complete campaign and every nested worker to the same V4 pins",
    )
    producer_contract = producer.protocol_document()
    nested = producer_contract.get("successful_nested_lifecycle")
    require(
        type(nested) is dict
        and nested.get("actual_case_interpreter_exec_calls") == 394
        and nested.get("actual_initialization_interpreter_exec_calls") == 11
        and nested.get("actual_guard_cleanup_interpreter_exec_calls") == 11
        and nested.get("actual_interpreters_created") == 11
        and nested.get("actual_interpreters_destroyed") == 11
        and nested.get("counted_case_count") == 128
        and nested.get("source_relative") == producer.NESTED_ORIGINAL_RELATIVE
        and nested.get("source_sha256") == producer.NESTED_ORIGINAL_SHA256
        and nested.get("historical_v3_relative") == producer.NESTED_V3_RELATIVE
        and nested.get("historical_v3_sha256") == producer.NESTED_V3_SHA256,
        "freeze the genuine original 128-case, 394-call nested bootstrap lifecycle",
    )
    return {
        "schema": "rebar-frozen-python-re-p0-candidate-protocol-v10",
        "version": 10,
        "goal": {"path": "GOAL.md", "sha256": GOAL_SHA256},
        "pinned_runtime": {
            "implementation": "cpython",
            "version": "3.14.6",
            "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
            "isolated": True,
            "bytecode_writes": False,
        },
        "phase_one": {
            "path": PHASE1_RELATIVE,
            "sha256": PHASE1_SHA256,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        },
        "worker": {
            "path": SOURCE_RELATIVE,
            "sha256": options.source_sha256,
        },
        "runner": {
            "path": RUNNER_RELATIVE,
            "sha256": options.runner_source_sha256,
        },
        "protocol": {
            "path": PROTOCOL_RELATIVE,
            "sha256": options.protocol_sha256,
        },
        "auditable_predecessors": copy.deepcopy(AUDITABLE_PREDECESSORS),
        "original_evaluator": mapped_owners(ORIGINAL_PRODUCER),
        "caller_pinned_original_producer": {
            "source_sha256": options.producer_source_sha256,
            "protocol_sha256": options.producer_protocol_sha256,
            "document_sha256": options.producer_document_sha256,
            "outer_worker_and_nested_digests_identical": True,
            "legacy_v1_fallback": "FORBIDDEN",
            "pre_activation_frozen_context_only": True,
            "live_worker_reverifies_frozen_source_and_actual_activation": True,
        },
        "first_party_native_build_v15": mapped_owners(BUILD),
        "published_current_overview_v40": mapped_owners(V40_OWNERS),
        "preserved_overview_v39": mapped_owners(V39_OWNERS),
        "corrected_candidate_context_reference_owners":
            mapped_owners(CORRECTED_REFERENCE_OWNERS),
        "corrected_candidate_context_reference": {
            "records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
            "historical_script_context_records_sha256":
                HISTORICAL_PUBLIC_RECORDS_SHA256,
            "cache_cohort_records_sha256":
                CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
            "cache_cohort_case_ids_sha256":
                CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256,
            "cache_cohort_case_count": CORRECTED_PUBLIC_COHORT_CASE_COUNT,
            "actual_independent_reference_pids":
                list(CORRECTED_PUBLIC_REFERENCE_PIDS),
            "c_pattern_equality_failure_waived": False,
            "source_context_reads_reference_archive": False,
            "source_context_inflates_reference_archive": False,
        },
        "source_inventory_families": [
            producer.owner_protocol(producer.family_spec(name))
            for name in FAMILY_NAMES
        ],
        "source_inventory_family_count": SOURCE_FAMILY_COUNT,
        "source_inventory_owner_count": SOURCE_OWNER_COUNT,
        "six_family_inventory_is_source_only": True,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "candidate_execution_scope": "C-ONLY; VERIFIED C15 NATIVE REQUIRED",
        "candidate_family": {
            "name": FAMILY,
            "adapter": {
                "path": ADAPTER_RELATIVE,
                "sha256": ADAPTER_SHA256,
                "size_bytes": ADAPTER_BYTES,
            },
            "original_source": {
                "path": ORIGINAL_C_RELATIVE,
                "sha256": ORIGINAL_C_SHA256,
                "size_bytes": ORIGINAL_C_BYTES,
            },
            "separately_derived_private_source": {
                "sha256": DERIVED_C_SHA256,
                "size_bytes": DERIVED_C_BYTES,
            },
            "original_family_spec_unchanged": True,
            "stdlib_engine_delegation_allowed": False,
            "external_regex_engine_allowed": False,
            "shared_candidate_engine_allowed": False,
        },
        "original_suites": [
            producer.suite_protocol(suite)
            for suite in producer.SUITES
        ],
        "successful_original_nested_lifecycle": copy.deepcopy(nested),
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "published_history": synthetic_contract()["history"],
        "evidence_protocol": {
            "independent_original_suite_workers": SUITE_COUNT,
            "expected_v15_compiler_process_count": 14,
            "fresh_reproducible_build_phase_count": 2,
            "private_evidence_mode_octal": "0600",
            "private_native_mode_octal": "0700",
            "separate_archive_and_receipt_owners": True,
            "deterministic_gzip_mtime": 0,
            "maximum_public_report_bytes": MAX_PUBLIC_REPORT_BYTES,
            "maximum_uncompressed_suite_bytes": MAX_UNCOMPRESSED_SUITE_BYTES,
            "original_target_restored_before_publication": True,
            "complete_stdout_and_stderr_required": True,
            "complete_original_mismatch_records_required": True,
            "reference_role_decoder": "EXACT CORRECTED CANDIDATE-CONTEXT V4",
            "worker_attempt_count": SUITE_COUNT,
            "failed_start_is_not_a_started_process": True,
            "started_worker_pid_preserved_on_timeout_and_overflow": True,
            "complete_stream_size_and_sha256_preserved_on_overflow": True,
            "pre_spawn_attempt_journal_is_fsync_durable": True,
            "no_candidate_regex_delegation": True,
        },
        "phase_boundary": {
            "candidate_qualified_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "clock_samples": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        },
    }


def _read_v40_history(
    producer_context: Mapping[str, Any],
) -> dict[str, Any]:
    evidence = producer_context.get("v21_history")
    require(
        type(evidence) is dict
        and evidence.get("actual_evidence_owner_count")
        == 103
        and evidence.get("authenticated_reference_path_count")
        == 108
        and evidence.get("new_repaired_c_campaign_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and evidence.get("repaired_c_infrastructure_failure_count") == 13
        and evidence.get("repaired_c_verified_passing_case_count") == 0
        and evidence.get("repaired_c_original_native_restored") is True
        and evidence.get("repaired_c_matching") == "NOT MEASURED",
        "preserve the historical V21 failures without mislabelling them as the current graph",
    )
    inputs_raw, _ = read_owner(
        V40_OWNERS["inputs"][0],
        V40_OWNERS["inputs"][1],
    )
    inputs = exact_json(inputs_raw, "the actual canonical V40 graph inputs")
    previous = inputs.get("previous_overview")
    require(
        inputs.get("schema") == "rebar-candidate-current-overview-v40-inputs"
        and type(previous) is dict
        and all(
            type(previous.get(name)) is dict
            and previous[name].get("path") == relative
            and previous[name].get("sha256") == fingerprint
            for name, (relative, fingerprint) in V39_OWNERS.items()
        ),
        "bind the current V40 graph to all four genuine preserved V39 owners",
    )
    summary_raw, _ = read_owner(
        V40_OWNERS["summary"][0],
        V40_OWNERS["summary"][1],
    )
    summary = exact_json(summary_raw, "genuine complete canonical V40 graph")
    snapshot = summary.get("snapshot")
    go = snapshot.get("go_v2_full_original_campaign") if type(snapshot) is dict else None
    corrected = summary.get("actual_corrected_two_reference")
    c15 = summary.get("actual_c_v15_source_build")
    require(
        summary.get("schema") == "rebar-candidate-current-overview-v40-summary"
        and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count")
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and summary.get("authenticated_digest_addressed_history_paths")
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and summary.get("full_case_denominator") == CASE_DENOMINATOR
        and summary.get("suite_count") == SUITE_COUNT
        and type(go) is dict
        and go.get("status") == "FAIL"
        and go.get("completed_suite_count") == SUITE_COUNT
        and go.get("semantic_mismatch_count") == 4518
        and go.get("infrastructure_failure_count") == 4
        and go.get("restoration_status") == "PASS"
        and type(corrected) is dict
        and corrected.get("reference_status") == "PASS"
        and corrected.get("full_reference_records_sha256")
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and corrected.get("cache_records_sha256")
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and corrected.get("actual_distinct_reference_process_ids")
        == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and summary.get("c_pattern_equality_failure_waived") is False
        and type(c15) is dict
        and c15.get("status") == "PASS"
        and c15.get("build_status") == "PASS"
        and c15.get("native_output_sha256") == C15_NATIVE_SHA256
        and c15.get("derived_source_sha256") == DERIVED_C_SHA256
        and c15.get("actual_compiler_process_count") == 14
        and c15.get("candidate_correctness") == "NOT MEASURED"
        and c15.get("candidate_processes_started") == 0
        and type(c15.get("receipt")) is dict
        and c15["receipt"].get("sha256") == C15_BUILD_RECEIPT_SHA256
        and summary.get("all_candidate_matching_blocked") is True
        and summary.get("candidate_case_producer_corrected_v4_status")
        == "SOURCE FROZEN; CANDIDATES NOT RUN"
        and summary.get("performance") == "NOT MEASURED",
        "authenticate current V40, preserved V39, both corrected references, C15 and every loss",
    )
    history = {
        "authoritative_counted_evidence_owner_count":
            summary["repository_evidence_owner_count"],
        "authenticated_digest_addressed_history_paths":
            summary["authenticated_digest_addressed_history_paths"],
        "preserved_failed_campaign_evidence_owner_count":
            evidence["new_repaired_c_campaign_owner_count"],
        "previous_repaired_c_infrastructure_failure_count":
            evidence["repaired_c_infrastructure_failure_count"],
        "previous_repaired_c_verified_passing_case_count":
            evidence["repaired_c_verified_passing_case_count"],
        "previous_repaired_c_original_native_restored":
            evidence["repaired_c_original_native_restored"],
        "go_full_campaign_status": go["status"],
        "go_full_campaign_suite_count": go["completed_suite_count"],
        "go_full_campaign_semantic_mismatch_count":
            go["semantic_mismatch_count"],
        "go_full_campaign_infrastructure_failure_count":
            go["infrastructure_failure_count"],
        "go_restoration_status": go["restoration_status"],
        "qualified_candidate_count": snapshot.get("qualified_candidate_count"),
    }
    return validate_history(history)


def _verify_source_owners(
    options: argparse.Namespace,
    *,
    include_document: bool,
) -> dict[str, dict[str, Any]]:
    runtime()
    owners: dict[str, dict[str, Any]] = {}
    required: list[tuple[str, str]] = [
        (SOURCE_RELATIVE, options.source_sha256),
        (RUNNER_RELATIVE, options.runner_source_sha256),
        (PROTOCOL_RELATIVE, options.protocol_sha256),
        ("GOAL.md", GOAL_SHA256),
        (PHASE1_RELATIVE, PHASE1_SHA256),
    ]
    if include_document:
        required.append((DOCUMENT_RELATIVE, options.document_sha256))
    for relative, fingerprint in required:
        _, owners[relative] = read_owner(relative, fingerprint)
    for relative, fingerprint, size in (
        (ADAPTER_RELATIVE, ADAPTER_SHA256, ADAPTER_BYTES),
        (ORIGINAL_C_RELATIVE, ORIGINAL_C_SHA256, ORIGINAL_C_BYTES),
    ):
        _, owners[relative] = read_owner(relative, fingerprint, size=size)
    for mapping in (
        ORIGINAL_PRODUCER,
        BUILD,
        V40_OWNERS,
        V39_OWNERS,
        CORRECTED_REFERENCE_OWNERS,
    ):
        for relative, fingerprint in mapping.values():
            _, owners[relative] = read_owner(relative, fingerprint)
    _, owners[C15_BUILD_RECEIPT_RELATIVE] = read_owner(
        C15_BUILD_RECEIPT_RELATIVE, C15_BUILD_RECEIPT_SHA256,
        size=4052, private=True,
    )
    for record in AUDITABLE_PREDECESSORS.values():
        _, owners[record["path"]] = read_owner(
            record["path"],
            record["sha256"],
        )
    return owners


def _verify_v4_pre_activation(
    options: argparse.Namespace,
    producer: types.ModuleType,
) -> dict[str, Any]:
    source = producer.parse_arguments([
        "--verify-frozen-context",
        "--source-sha256", options.producer_source_sha256,
        "--protocol-sha256", options.producer_protocol_sha256,
        "--document-sha256", options.producer_document_sha256,
    ])
    context = producer.verify_frozen_context(source)
    require(
        type(context) is dict
        and context.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v4-read-only-frozen-context"
        and context.get("status") == "PASS"
        and context.get("read_only") is True
        and context.get("suite_count") == SUITE_COUNT
        and context.get("case_execution_denominator") == CASE_DENOMINATOR
        and context.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and context.get("source_family_count") == SOURCE_FAMILY_COUNT
        and context.get("source_owner_count") == SOURCE_OWNER_COUNT
        and context.get("authenticated_evidence_owner_lower_bound")
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and context.get("authenticated_history_reference_lower_bound")
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and context.get("new_repaired_c_campaign_evidence_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and context.get("actual_candidate_workers") == 0
        and context.get("actual_reference_workers") == 0
        and context.get("actual_source_builds") == 0
        and context.get("actual_native_activations") == 0
        and context.get("corrected_public_reference_status") == "PASS"
        and context.get("corrected_public_reference_records_sha256")
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and context.get("historical_public_reference_records_sha256")
        == HISTORICAL_PUBLIC_RECORDS_SHA256
        and context.get("corrected_public_reference_process_ids")
        == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and context.get("corrected_public_reference_cache_records_sha256")
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and context.get("corrected_public_reference_cache_case_count")
        == CORRECTED_PUBLIC_COHORT_CASE_COUNT
        and context.get("reference_archive_bytes_read") == 0
        and context.get("reference_archives_decompressed") == 0
        and context.get("c_pattern_equality_failure_waived") is False
        and context.get("clock_samples") == 0
        and context.get("holdout") == "NOT OPENED",
        "authenticate all six V4 owners and the actual corrected reference before any candidate import",
    )
    return context


def verify_live_worker_context(
    options: argparse.Namespace,
) -> dict[str, Any]:
    owners = _verify_source_owners(options, include_document=True)
    producer = load_original_evaluator(options)
    protocol_raw, _ = read_owner(
        DOCUMENT_RELATIVE,
        options.document_sha256,
    )
    contract = exact_json(protocol_raw, "exact canonical V10 original protocol")
    require(
        canonical(contract)
        == canonical(expected_protocol_document(options, producer)),
        "reject changed V10 suites, V4 reference, current V40, or C15 build contract",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "authenticate the genuine live worker before candidate import",
    )
    return {
        "schema": SCHEMA + "-live-worker-source-context",
        "status": "PASS",
        "read_only": True,
        "frozen_owners": owners,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "original_producer_sha256": options.producer_source_sha256,
        "nested_producer_sha256": options.producer_source_sha256,
        "historical_evidence_owner_count":
            HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "v4_frozen_context_called_after_activation": False,
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "corrected_public_cohort_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "reference_archive_bytes_read": 0,
        "reference_archives_decompressed": 0,
    }


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    owners = _verify_source_owners(options, include_document=True)
    producer = load_original_evaluator(options)
    context = _verify_v4_pre_activation(options, producer)
    history = _read_v40_history(context)
    raw, _ = read_owner(
        DOCUMENT_RELATIVE,
        options.document_sha256,
    )
    contract = exact_json(raw, "exact canonical V10 original candidate protocol")
    require(
        canonical(contract)
        == canonical(expected_protocol_document(options, producer)),
        "reject any changed V4 route, corrected case, current V40, or first-party owner",
    )
    c15_receipt_raw, _ = read_owner(
        C15_BUILD_RECEIPT_RELATIVE, C15_BUILD_RECEIPT_SHA256,
        size=4052, private=True,
    )
    c15_receipt = exact_json(c15_receipt_raw, "the real first-party C15 build receipt")
    require(
        c15_receipt.get("schema")
        == "rebar-phase2-owned-c-pickle-source-build-v15-durable-publication-receipt"
        and c15_receipt.get("status") == "PASS"
        and c15_receipt.get("build_status") == "PASS"
        and c15_receipt.get("family") == FAMILY
        and c15_receipt.get("source_sha256") == BUILD["source"][1]
        and c15_receipt.get("protocol_sha256") == BUILD["protocol"][1]
        and c15_receipt.get("contract_sha256") == BUILD["document"][1]
        and c15_receipt.get("archive_sha256") == C15_BUILD_ARCHIVE_SHA256
        and c15_receipt.get("v2_derived_source_sha256") == DERIVED_C_SHA256
        and c15_receipt.get("v2_derived_source_bytes") == DERIVED_C_BYTES
        and c15_receipt.get("actual_compiler_process_count") == 14
        and c15_receipt.get("candidate_correctness") == "NOT MEASURED"
        and c15_receipt.get("candidate_processes_started") == 0
        and c15_receipt.get("performance") == "NOT MEASURED"
        and c15_receipt.get("holdout") == "NOT OPENED",
        "verify the actual C15 build without opening its archive or claiming matching",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "source context cannot import or activate a candidate",
    )
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "read_only": True,
        "frozen_owners": owners,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "original_producer_sha256": options.producer_source_sha256,
        "original_producer_protocol_sha256":
            options.producer_protocol_sha256,
        "original_producer_document_sha256":
            options.producer_document_sha256,
        "nested_producer_sha256": options.producer_source_sha256,
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "historical_evidence_owner_count":
            HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "preserved_history": history,
        "original_suite_count_verified": len(producer.SUITES),
        "successful_original_nested_lifecycle":
            context["successful_nested_lifecycle"],
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "historical_public_records_sha256": HISTORICAL_PUBLIC_RECORDS_SHA256,
        "corrected_public_cohort_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "corrected_public_cohort_case_ids_sha256":
            CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256,
        "corrected_public_cohort_case_count":
            CORRECTED_PUBLIC_COHORT_CASE_COUNT,
        "corrected_public_reference_pids":
            list(CORRECTED_PUBLIC_REFERENCE_PIDS),
        "c_pattern_equality_failure_waived": False,
        "current_overview_v40_sha256": V40_OWNERS["summary"][1],
        "preserved_overview_v39_sha256": V39_OWNERS["summary"][1],
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
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified_count": 0,
        "winner_selected": False,
        "v4_frozen_context_verified_before_activation": True,
    }


def render_frozen_contract(options: argparse.Namespace) -> dict[str, Any]:
    _verify_source_owners(options, include_document=False)
    producer = load_original_evaluator(options)
    v4 = _verify_v4_pre_activation(options, producer)
    _read_v40_history(v4)
    return expected_protocol_document(options, producer)

def stream_gzip(document: dict[str, Any]) -> tuple[bytes, str, int]:
    encoder = json.JSONEncoder(ensure_ascii=True, allow_nan=False,
                               sort_keys=True, separators=(",", ":"))
    plain_hash = hashlib.sha256()
    plain_size = 0
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=compressed, mode="wb",
                       compresslevel=9, mtime=0) as archive:
        for text in encoder.iterencode(document):
            raw = text.encode("ascii")
            plain_size += len(raw)
            require(plain_size <= MAX_UNCOMPRESSED_SUITE_BYTES,
                    "preserve the complete suite without report truncation")
            plain_hash.update(raw)
            archive.write(raw)
        plain_size += 1
        require(plain_size <= MAX_UNCOMPRESSED_SUITE_BYTES,
                "reject an unbounded complete suite record")
        plain_hash.update(b"\n")
        archive.write(b"\n")
    value = compressed.getvalue()
    require(0 < len(value) <= MAX_COMPRESSED_SUITE_BYTES,
            "reject a partial or unbounded original suite archive")
    return value, plain_hash.hexdigest(), plain_size


def create_private_owner(relative: str, raw: bytes) -> dict[str, Any]:
    relative = checked_relative(relative)
    require(relative.startswith(EVIDENCE_RELATIVE + "/"),
            "create only a predetermined private suite-evidence owner")
    require(type(raw) is bytes and bool(raw), "reject an empty suite owner")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
    path = ROOT / relative
    descriptor = os.open(str(path), flags, 0o600)
    try:
        cursor = 0
        while cursor < len(raw):
            written = os.write(descriptor, raw[cursor:])
            require(type(written) is int and written > 0,
                    "reject a short private suite-evidence write")
            cursor += written
        os.fsync(descriptor)
        recorded = os.fstat(descriptor)
        require(stat.S_ISREG(recorded.st_mode)
                and stat.S_IMODE(recorded.st_mode) == 0o600
                and recorded.st_size == len(raw),
                "require one complete private original suite-evidence owner")
    finally:
        os.close(descriptor)
    _, owner = read_owner(relative, digest(raw),
                          maximum=max(len(raw), 1), size=len(raw), private=True)
    directory_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_NOFOLLOW", 0)
                       | getattr(os, "O_CLOEXEC", 0))
    directory = os.open(str(ROOT / EVIDENCE_RELATIVE), directory_flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    owner["exclusive_creation"] = True
    owner["file_fsync_completed"] = True
    owner["directory_fsync_completed"] = True
    owner["same_inode_readback_verified"] = True
    return owner


def suite_evidence_names(suite: str, label: str) -> tuple[str, str]:
    require(suite in {name for name, _ in SUITES},
            "reject a nonoriginal repaired-C suite")
    label = checked_label(label)
    stem = EVIDENCE_RELATIVE + "/frozen-p0-candidate-worker-v8-c-" + label + "-" + suite
    return stem + ".json.gz", stem + "-publication-receipt.json"


def authenticate_v15_build(options: argparse.Namespace) -> dict[str, Any]:
    require(
        options.candidate == FAMILY
        and checked_label(options.build_label, "build label") == C15_BUILD_LABEL
        and options.build_archive_sha256 == C15_BUILD_ARCHIVE_SHA256
        and options.build_receipt_sha256 == C15_BUILD_RECEIPT_SHA256
        and options.native_engine_sha256 == C15_NATIVE_SHA256
        and options.native_bridge_sha256 == C15_NATIVE_SHA256,
        "fail closed unless the exact independently reproduced first-party C15 build is pinned",
    )
    archive_name = (
        EVIDENCE_RELATIVE
        + "/native-source-build-v15-c-" + C15_BUILD_LABEL + ".json.gz"
    )
    _, archive_owner = read_owner(
        archive_name, C15_BUILD_ARCHIVE_SHA256,
        maximum=64 * 1024 * 1024, size=41716, private=True,
    )
    receipt_raw, receipt_owner = read_owner(
        C15_BUILD_RECEIPT_RELATIVE, C15_BUILD_RECEIPT_SHA256,
        maximum=MAX_SOURCE_BYTES, size=4052, private=True,
    )
    receipt = exact_json(receipt_raw, "the exact first-party C15 build receipt")
    require(
        (archive_owner["device"], archive_owner["inode"])
        != (receipt_owner["device"], receipt_owner["inode"])
        and receipt.get("schema")
        == "rebar-phase2-owned-c-pickle-source-build-v15-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == FAMILY
        and receipt.get("label") == C15_BUILD_LABEL
        and receipt.get("source_sha256") == BUILD["source"][1]
        and receipt.get("protocol_sha256") == BUILD["protocol"][1]
        and receipt.get("contract_sha256") == BUILD["document"][1]
        and receipt.get("archive_relative") == archive_name
        and receipt.get("archive_sha256") == archive_owner["sha256"]
        and receipt.get("archive_bytes") == archive_owner["size_bytes"]
        and receipt.get("original_source_sha256") == ORIGINAL_C_SHA256
        and receipt.get("v2_derived_source_sha256") == DERIVED_C_SHA256
        and receipt.get("v2_derived_source_bytes") == DERIVED_C_BYTES
        and receipt.get("actual_source_apply_count") == 2
        and receipt.get("expected_compiler_process_count") == 14
        and receipt.get("actual_compiler_process_count") == 14
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "never substitute obsolete V8, external engines, or build PASS for candidate correctness",
    )
    return {
        "archive_owner": archive_owner,
        "receipt_owner": receipt_owner,
        "receipt": receipt,
        "build_version": 15,
        "build_archive_decompressed": False,
        "build_report_uncompressed_bytes_read": 0,
    }


def authenticate_live_c15_native(
    options: argparse.Namespace,
    build: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        build.get("build_version") == 15
        and options.candidate == FAMILY
        and options.native_engine_sha256 == C15_NATIVE_SHA256
        and options.native_bridge_sha256 == C15_NATIVE_SHA256,
        "require the actual pinned C15 first-party engine and combined Python bridge",
    )
    native_raw, native = read_owner(
        NATIVE_RELATIVE, C15_NATIVE_SHA256,
        maximum=MAX_BINARY_BYTES, size=163176,
    )
    require(
        len(native_raw) == 163176
        and native["sha256"] == C15_NATIVE_SHA256,
        "fail closed until an independently recovered C15 target has actually been activated",
    )
    return {
        "native_owner": native,
        "native_output_sha256": C15_NATIVE_SHA256,
        "native_output_bytes": 163176,
        "build": {
            "version": 15,
            "archive_sha256": build["archive_owner"]["sha256"],
            "receipt_sha256": build["receipt_owner"]["sha256"],
        },
        "runner_activates_native": False,
        "runner_mutates_native": False,
        "external_regex_dependency_count": 0,
    }


def observe_original_suite(options: argparse.Namespace) -> dict[str, Any]:
    context = verify_live_worker_context(options)
    require(context.get("v4_frozen_context_called_after_activation") is False,
            "authenticate corrected V4 source before inspecting a live first-party engine")
    build = authenticate_v15_build(options)
    approval = authenticate_live_c15_native(options, build)
    producer = load_original_evaluator(options)
    suite = producer.suite_spec(options.suite)
    spec = producer.family_spec(FAMILY)
    source_pins = {
        ADAPTER_RELATIVE: ADAPTER_SHA256,
        ORIGINAL_C_RELATIVE: ORIGINAL_C_SHA256,
    }
    pins = {"source": ADAPTER_SHA256,
            "native_engine": approval["native_owner"]["sha256"],
            "native_bridge": approval["native_owner"]["sha256"]}
    if suite.name == "original_bounded_v5":
        observed = producer.observe_original_upstream(suite, spec, pins,
                                                      source_pins)
    elif suite.name == "subinterpreter_v2":
        observed = producer.observe_subinterpreters(
            suite, spec, pins, source_pins,
            producer_sha256=options.producer_source_sha256)
    else:
        phase1_raw, _ = read_owner(PHASE1_RELATIVE, PHASE1_SHA256)
        phase1 = exact_json(phase1_raw, "unchanged original P0 manifest")
        observed = producer.observe_direct_suite(suite, spec, pins,
                                                 source_pins, phase1)
    require(type(observed) is dict and observed.get("suite") == suite.name
            and observed.get("candidate_family") == FAMILY
            and observed.get("case_execution_denominator") == suite.case_count
            and observed.get("actual_candidate_case_count") == suite.case_count
            and observed.get("actual_candidate_workers") == 1
            and observed.get("status") in ("PASS", "FAIL")
            and type(observed.get("mismatch_count")) is int
            and observed["mismatch_count"] >= 0
            and type(observed.get("all_mismatches")) is list
            and len(observed["all_mismatches"]) == observed["mismatch_count"]
            and (observed.get("status") == "PASS")
            is (observed["mismatch_count"] == 0)
            and observed.get("performance") == "NOT MEASURED"
            and observed.get("holdout") == "NOT OPENED"
            and observed.get("hidden_cases_read") == 0
            and observed.get("clock_samples") == 0,
            "retain the unchanged complete original suite observation")
    records = observed.get("candidate_records")
    if suite.name == "original_bounded_v5":
        require(type(records) is list and len(records) == 152
                and observed.get("actual_public_record_count") == 152
                and observed.get("actual_debug_skip_count") == 1
                and observed.get("named_private_waiver_count")
                == PRIVATE_WAIVER_COUNT
                and len(observed.get("named_private_waivers", []))
                == PRIVATE_WAIVER_COUNT,
                "preserve all original public methods, waivers, and debug skip")
    else:
        require(type(records) is list and len(records) == suite.case_count,
                "never omit an original candidate case or its complete record")
    if suite.name == "subinterpreter_v2" and observed["status"] == "PASS":
        require(observed.get("actual_case_interpreter_exec_calls") == 394
                and observed.get("actual_initialization_interpreter_exec_calls")
                == 11
                and observed.get("actual_guard_cleanup_interpreter_exec_calls")
                == 11
                and observed.get("actual_interpreters_created") == 11
                and observed.get("actual_interpreters_destroyed") == 11
                and observed.get("all_real_pipes_read_to_eof") is True
                and observed.get("all_real_pipe_descriptors_closed") is True
                and observed.get("interpreter_live_set_restored") is True
                and observed.get("locale_restored") is True,
                "require the complete original 128-case, 394-call interpreter lifecycle")
    observed["genuine_original_suite"] = True
    observed["original_producer_sha256"] = options.producer_source_sha256
    observed["original_c_source_sha256"] = ORIGINAL_C_SHA256
    observed["derived_c_source_sha256"] = DERIVED_C_SHA256
    observed["verified_v15_build_archive_sha256"] = build["archive_owner"]["sha256"]
    observed["verified_v15_build_receipt_sha256"] = build["receipt_owner"]["sha256"]
    observed["verified_v15_native_output_sha256"] = C15_NATIVE_SHA256
    observed["runner_activates_native"] = False
    observed["runner_mutates_native"] = False
    observed["corrected_public_records_sha256"] = CORRECTED_PUBLIC_RECORDS_SHA256
    observed["corrected_public_cohort_records_sha256"] = (
        CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
    )
    observed["c_pattern_equality_failure_waived"] = False
    observed["runnable_candidate_family_count"] = 1
    observed["runnable_candidate_families"] = [FAMILY]
    observed["six_family_inventory_is_source_only"] = True
    observed["nested_producer_sha256"] = options.producer_source_sha256
    observed["historical_evidence_owner_count"] = HISTORICAL_EVIDENCE_OWNER_COUNT
    observed["historical_authenticated_reference_count"] = (
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT)
    observed["phase_one_case_execution_denominator"] = CASE_DENOMINATOR
    observed["supplemental_cases_added_to_phase_one"] = False
    observed["candidate_qualified"] = False
    observed["winner_selected"] = False
    return observed


def publish_suite(
    report: dict[str, Any],
    options: argparse.Namespace,
    effect_ledger: dict[str, Any],
) -> dict[str, Any]:
    effect_ledger["phase"] = "suite-report-serialization"
    effect_ledger["public_report_serialization_attempted"] = True
    compressed, expanded_sha, expanded_size = stream_gzip(report)
    archive_name, receipt_name = suite_evidence_names(options.suite, options.label)
    effect_ledger["phase"] = "suite-archive-publication"
    effect_ledger["archive_publication_attempted"] = True
    archive = create_private_owner(archive_name, compressed)
    effect_ledger["archive_owner"] = copy.deepcopy(archive)
    receipt_document = {
        "schema": SCHEMA + "-durable-suite-publication-receipt",
        "status": "PASS", "candidate_status": report["status"],
        "candidate_family": options.candidate, "label": options.label,
        "suite": options.suite,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "case_execution_denominator": report["case_execution_denominator"],
        "phase_one_case_execution_denominator": CASE_DENOMINATOR,
        "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "corrected_public_cohort_records_sha256":
            CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "c_pattern_equality_failure_waived": False,
        "archive": archive, "uncompressed_sha256": expanded_sha,
        "uncompressed_bytes": expanded_size,
        "mismatch_count": report.get("mismatch_count"),
        "genuine_original_suite": report.get("genuine_original_suite", True),
        "all_original_records_and_mismatches_preserved": True,
        "historical_evidence_owner_count": HISTORICAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_qualified": False, "winner_selected": False,
    }
    effect_ledger["phase"] = "suite-receipt-publication"
    effect_ledger["receipt_publication_attempted"] = True
    receipt = create_private_owner(receipt_name, canonical(receipt_document))
    effect_ledger["receipt_owner"] = copy.deepcopy(receipt)
    effect_ledger["publication_status"] = "PASS"
    effect_ledger["phase"] = "suite-published"
    return {
        "schema": SCHEMA + "-published-original-suite",
        "status": report["status"],
        "candidate_family": options.candidate, "label": options.label,
        "suite": options.suite,
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": [FAMILY],
        "six_family_inventory_is_source_only": True,
        "case_execution_denominator": report["case_execution_denominator"],
        "mismatch_count": report.get("mismatch_count"),
        "archive": archive, "receipt": receipt,
        "uncompressed_sha256": expanded_sha,
        "uncompressed_bytes": expanded_size,
        "all_original_records_and_mismatches_preserved": True,
        "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "corrected_public_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_qualified": False,
        "winner_selected": False,
    }


def run_actual_suite(
    options: argparse.Namespace,
    effect_ledger: dict[str, Any],
) -> dict[str, Any]:
    require(type(effect_ledger) is dict
            and effect_ledger.get("schema")
            == SCHEMA + "-authorized-actual-effect-ledger",
            "install the truthful worker effect ledger before any candidate observation")
    effect_ledger["phase"] = "candidate-worker-started"
    effect_ledger["actual_candidate_workers"] = 1
    effect_ledger["actual_worker_process_id"] = os.getpid()
    effect_ledger["candidate_observation_attempted"] = True
    try:
        report = observe_original_suite(options)
        effect_ledger["candidate_observation_completed"] = True
    except BaseException as error:
        details = getattr(error, "details", None)
        count = dict(SUITES)[options.suite]
        report = {
            "schema": SCHEMA + "-complete-original-suite-failure",
            "status": "FAIL", "suite": options.suite,
            "candidate_family": options.candidate,
            "runnable_candidate_family_count": 1,
            "runnable_candidate_families": [FAMILY],
            "six_family_inventory_is_source_only": True,
            "case_execution_denominator": count,
            "genuine_original_suite": False,
            "mismatch_count": None,
            "actual_failure": details if type(details) is dict else None,
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
            "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
            "original_c_source_sha256": ORIGINAL_C_SHA256,
            "derived_c_source_sha256": DERIVED_C_SHA256,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "performance": "NOT MEASURED",
            "memory": "NOT MEASURED", "holdout": "NOT OPENED",
            "candidate_qualified": False, "winner_selected": False,
        }
    return publish_suite(report, options, effect_ledger)


def parse_arguments(
    arguments: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=(FAMILY,))
    parser.add_argument("--suite", choices=tuple(name for name, _ in SUITES))
    parser.add_argument("--label")
    parser.add_argument("--build-label")
    for name in (
        "source",
        "runner-source",
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
        "runner_source_sha256",
        "protocol_sha256",
        "document_sha256",
        "producer_source_sha256",
        "producer_protocol_sha256",
        "producer_document_sha256",
    )
    actual = (
        "candidate",
        "suite",
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
            "source-only controls cannot authorize a producer or candidate",
        )
        return options
    base = (
        "source_sha256",
        "runner_source_sha256",
        "protocol_sha256",
        "producer_source_sha256",
        "producer_protocol_sha256",
        "producer_document_sha256",
    )
    for name in base:
        checked_digest(getattr(options, name), name)
    require(
        options.producer_source_sha256 == ORIGINAL_PRODUCER["source"][1]
        and options.producer_protocol_sha256 == ORIGINAL_PRODUCER["protocol"][1]
        and options.producer_document_sha256 == ORIGINAL_PRODUCER["document"][1],
        "reject absent, legacy, substituted, or inconsistent corrected V4 producer pins",
    )
    if options.render_contract:
        require(
            options.document_sha256 is None
            and all(getattr(options, name) is None for name in actual),
            "read-only contract rendering cannot run or activate a candidate",
        )
        return options
    checked_digest(options.document_sha256, "document_sha256")
    if options.verify_frozen_context:
        require(
            all(getattr(options, name) is None for name in actual),
            "source verification cannot select, promote, or run a candidate",
        )
        return options
    require(
        all(getattr(options, name) is not None for name in actual)
        and options.candidate == FAMILY,
        "fail closed until every exact genuine first-party C15 build and native owner is pinned",
    )
    checked_label(options.label)
    checked_label(options.build_label, "build label")
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
        elif options.render_contract:
            result = render_frozen_contract(options)
            raw = canonical(result)
            require(
                len(raw) <= MAX_PUBLIC_REPORT_BYTES,
                "bound the complete immutable corrected V10 source contract",
            )
            sys.stdout.buffer.write(raw)
            sys.stdout.buffer.flush()
            return 0
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            effect_ledger = new_worker_effect_ledger(options)
            result = run_actual_suite(options, effect_ledger)
        if effect_ledger is not None:
            effect_ledger["phase"] = "public-worker-report-serialization"
            effect_ledger["public_report_serialization_attempted"] = True
        raw = bounded_public_report(result)
        if effect_ledger is not None:
            effect_ledger["phase"] = "public-worker-report-write"
            effect_ledger["public_report_write_attempted"] = True
        sys.stdout.buffer.write(raw)
        if effect_ledger is not None:
            effect_ledger["phase"] = "public-worker-report-flush"
            effect_ledger["public_report_flush_attempted"] = True
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        if options is not None and getattr(options, "run", False):
            if effect_ledger is None:
                effect_ledger = new_worker_effect_ledger(options)
            result = worker_entry_failure_result(error, effect_ledger)
        else:
            result = {
                "schema": SCHEMA + "-entry-failure",
                "status": "FAIL",
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
