#!/usr/bin/env python3
"""Freeze one losslessly recorded, original repaired-C correctness suite."""

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
from typing import Any, Iterator, Mapping, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_worker_v7.py"
RUNNER_RELATIVE = "tools/run_frozen_p0_candidate_v9.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v9.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v7"
RUNNER_SCHEMA = "rebar-frozen-python-re-p0-candidate-v9"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
ORIGINAL_PRODUCER = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v3.py",
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
    ),
    "document": (
        "oracle/phase2/six-family-p0-producer-v3.json",
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
    ),
}
AUDITABLE_PREDECESSORS = {
    "worker_v6": {
        "path": "tools/run_frozen_p0_candidate_worker_v6.py",
        "sha256":
            "4fbe0885e78797ca9c46d81477229252fb7e2e85801cfe35304457cd39d141c1",
    },
    "runner_v8": {
        "path": "tools/run_frozen_p0_candidate_v8.py",
        "sha256":
            "3081c956f5933e03b42ca2d33c9801c58cde6a05ff332b9ef6560e00afc73b60",
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
    "source": ("tools/reproduce_owned_native_source_build_v8.py",
               "afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4"),
    "protocol": ("oracle/phase2/NATIVE-SOURCE-BUILD-V8.md",
                 "376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2"),
    "document": ("oracle/phase2/native-source-build-v8.json",
                 "7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b"),
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
V21_OWNERS = {
    "source": (
        "tools/render_candidate_current_overview_v21.py",
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v21.inputs.json",
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v21.json",
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v21.svg",
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
    ),
}
PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT = 30

ADAPTER_RELATIVE = "candidates/vm_candidate.py"
ADAPTER_SHA256 = "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
ADAPTER_BYTES = 60707
ORIGINAL_C_RELATIVE = "candidates/_vm_native.c"
ORIGINAL_C_SHA256 = "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
ORIGINAL_C_BYTES = 218185
DERIVED_C_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
DERIVED_C_BYTES = 218308
NATIVE_RELATIVE = "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
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
            "run only the isolated, pinned CPython 3.14.6 V6 worker")


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
    )}
    originals: list[tuple[Any, str, Any]] = []

    def block(owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def forbidden(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyEffect("source-only V6 worker forbids " + name)

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
        "reject changed V21 103-owner, 108-reference, 30-failure history",
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
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "original_c_source_bytes": ORIGINAL_C_BYTES,
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "derived_c_source_bytes": DERIVED_C_BYTES,
        "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "original_producer_protocol_sha256": ORIGINAL_PRODUCER["protocol"][1],
        "original_producer_document_sha256": ORIGINAL_PRODUCER["document"][1],
        "nested_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "expected_v8_build_process_count": 14,
        "expected_actual_original_worker_count": 13,
        "maximum_public_report_bytes": MAX_PUBLIC_REPORT_BYTES,
        "suite_ids": [name for name, _count in SUITES],
        "suite_case_counts": [count for _name, count in SUITES],
        "auditable_predecessors": copy.deepcopy(AUDITABLE_PREDECESSORS),
        "history": {
            "authoritative_counted_evidence_owner_count": 103,
            "authenticated_digest_addressed_history_paths": 108,
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
        "reject changed V3 producer, V21 history, original cases, or boundary",
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
            ("expected_v8_build_process_count", 13),
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
        )
        for counter, probe in probes:
            before = effects[counter]
            _expect_synthetic_rejection(probe)
            require(effects[counter] == before + 1,
                    "verify every blocked V7 source-only external effect")
            rejected += 1
        require(rejected >= 160,
                "require substantial V3/V21/nested/role source-only controls")
        measured = dict(effects)
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_synthetic_controls": 2,
        "rejected_hostile_controls": rejected,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
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
        checked_digest(options.producer_source_sha256, "V3 producer source")
        == ORIGINAL_PRODUCER["source"][1]
        and checked_digest(
            options.producer_protocol_sha256,
            "V3 producer protocol",
        ) == ORIGINAL_PRODUCER["protocol"][1]
        and checked_digest(
            options.producer_document_sha256,
            "V3 producer document",
        ) == ORIGINAL_PRODUCER["document"][1],
        "require all three caller-pinned exact corrected original V3 owners",
    )
    for name, (relative, expected) in sorted(ORIGINAL_PRODUCER.items()):
        supplied = getattr(options, "producer_" + name + "_sha256")
        require(supplied == expected,
                "reject V1, V2, missing, or substituted V3 owner: " + name)
        read_owner(relative, expected)
    module = frozen_module(
        ORIGINAL_PRODUCER["source"][0],
        options.producer_source_sha256,
        "_rebar_frozen_original_six_family_producer_v3_for_worker_v7",
    )
    require(
        module.SCHEMA == "rebar-owned-six-family-original-p0-producer-v3"
        and module.SOURCE_RELATIVE == ORIGINAL_PRODUCER["source"][0]
        and module.PROTOCOL_RELATIVE == ORIGINAL_PRODUCER["protocol"][0]
        and module.DOCUMENT_RELATIVE == ORIGINAL_PRODUCER["document"][0]
        and module.SUITE_COUNT == SUITE_COUNT
        and module.CASE_DENOMINATOR == CASE_DENOMINATOR
        and module.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
        and module.PRESERVED_EVIDENCE_OWNER_COUNT
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and module.PRESERVED_REFERENCE_PATH_COUNT
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and module.PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and [(item.name, item.case_count) for item in module.SUITES]
        == list(SUITES),
        "require the complete genuine corrected V3 original-suite evaluator",
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
        "independently pinned corrected original V3 source contract",
        canonical_required=True,
    )
    module.validate_protocol_document(producer_document)
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
        "bind complete campaign and every nested worker to the same V3 pins",
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
        "freeze the genuine original 128-case V3 nested bootstrap lifecycle",
    )
    return {
        "schema": "rebar-frozen-python-re-p0-candidate-protocol-v9",
        "version": 9,
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
        "first_party_source_repair": mapped_owners(REPAIR),
        "first_party_native_build_v8": mapped_owners(BUILD),
        "verified_native_activation_v5": mapped_owners(ACTIVATION_V5),
        "published_overview_v21": mapped_owners(V21_OWNERS),
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
            "expected_v8_compiler_process_count": 14,
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
            "reference_role_decoder": "EXACT CORRECTED ORIGINAL V3",
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


def _read_v21_history(
    producer_context: Mapping[str, Any],
) -> dict[str, Any]:
    evidence = producer_context.get("v21_history")
    require(
        type(evidence) is dict
        and evidence.get("actual_evidence_owner_count")
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and evidence.get("authenticated_reference_path_count")
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and evidence.get("new_repaired_c_campaign_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and evidence.get("repaired_c_infrastructure_failure_count") == 13
        and evidence.get("repaired_c_verified_passing_case_count") == 0
        and evidence.get("repaired_c_original_native_restored") is True
        and evidence.get("repaired_c_matching") == "NOT MEASURED",
        "authenticate the complete original V21 103/108/30 evidence history",
    )
    summary_raw, _ = read_owner(
        V21_OWNERS["summary"][0],
        V21_OWNERS["summary"][1],
    )
    summary = exact_json(summary_raw, "genuine complete canonical V21 graph")
    snapshot = summary.get("snapshot")
    go = snapshot.get("go_v2_full_original_campaign") if type(snapshot) is dict else None
    require(
        summary.get("schema") == "rebar-candidate-current-overview-v21-summary"
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
        and go.get("restoration_status") == "PASS",
        "preserve complete V21 ownership and every genuine historical Go loss",
    )
    history = {
        "authoritative_counted_evidence_owner_count":
            evidence["actual_evidence_owner_count"],
        "authenticated_digest_addressed_history_paths":
            evidence["authenticated_reference_path_count"],
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
    require_activation_pins()
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
        REPAIR,
        BUILD,
        ACTIVATION_V5,
        V21_OWNERS,
    ):
        for relative, fingerprint in mapping.values():
            _, owners[relative] = read_owner(relative, fingerprint)
    for record in AUDITABLE_PREDECESSORS.values():
        _, owners[record["path"]] = read_owner(
            record["path"],
            record["sha256"],
        )
    return owners


def _verify_v3_pre_activation(
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
        == "rebar-owned-six-family-original-p0-producer-v3-read-only-frozen-context"
        and context.get("status") == "PASS"
        and context.get("read_only") is True
        and context.get("suite_count") == SUITE_COUNT
        and context.get("case_execution_denominator") == CASE_DENOMINATOR
        and context.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and context.get("source_family_count") == SOURCE_FAMILY_COUNT
        and context.get("source_owner_count") == SOURCE_OWNER_COUNT
        and context.get("total_distinct_historical_evidence_owner_count")
        == HISTORICAL_EVIDENCE_OWNER_COUNT
        and context.get("total_authenticated_historical_reference_path_count")
        == HISTORICAL_AUTHENTICATED_REFERENCE_COUNT
        and context.get("new_repaired_c_campaign_evidence_owner_count")
        == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
        and context.get("actual_candidate_workers") == 0
        and context.get("actual_reference_workers") == 0
        and context.get("actual_source_builds") == 0
        and context.get("actual_native_activations") == 0
        and context.get("clock_samples") == 0
        and context.get("holdout") == "NOT OPENED",
        "authenticate V3 full source context only before C native promotion",
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
    contract = exact_json(protocol_raw, "exact canonical V9 original protocol")
    require(
        canonical(contract)
        == canonical(expected_protocol_document(options, producer)),
        "reject changed V9 original suite, V3 digest, or V21 source contract",
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
        "v3_frozen_context_called_after_activation": False,
    }


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    owners = _verify_source_owners(options, include_document=True)
    producer = load_original_evaluator(options)
    context = _verify_v3_pre_activation(options, producer)
    history = _read_v21_history(context)
    raw, _ = read_owner(
        DOCUMENT_RELATIVE,
        options.document_sha256,
    )
    contract = exact_json(raw, "exact canonical V9 original candidate protocol")
    require(
        canonical(contract)
        == canonical(expected_protocol_document(options, producer)),
        "reject any changed original V3 route, case, history, or owner",
    )
    repair = frozen_module(
        REPAIR["source"][0],
        REPAIR["source"][1],
        "_rebar_frozen_repaired_c_source_v1_for_worker_v7",
    )
    _repair_contract, derived = repair.verify_context(
        REPAIR["source"][1],
        REPAIR["protocol"][1],
        REPAIR["document"][1],
    )
    require(
        type(derived) is bytes
        and len(derived) == DERIVED_C_BYTES
        and digest(derived) == DERIVED_C_SHA256,
        "preserve the exact independently frozen first-party C repair",
    )
    build = frozen_module(
        BUILD["source"][0],
        BUILD["source"][1],
        "_rebar_frozen_repaired_c_native_build_v8_for_worker_v7",
    )
    build_context = build.verify_context({
        "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["document"][1],
    })
    require(
        type(build_context) is dict
        and build_context.get("status") == "PASS"
        and build_context.get("family") == FAMILY
        and build_context.get("native_builds_started") == 0
        and build_context.get("compiler_processes_started") == 0,
        "authenticate the frozen exact repaired C V8 source-build protocol",
    )
    activation = frozen_module(
        ACTIVATION_V5["source"][0],
        ACTIVATION_V5["source"][1],
        "_rebar_frozen_verified_native_activation_v5_context_for_worker_v7",
    )
    activation_context = activation.verify_frozen_context({
        "activation_source_sha256": ACTIVATION_V5["source"][1],
        "activation_protocol_sha256": ACTIVATION_V5["protocol"][1],
        "activation_contract_sha256": ACTIVATION_V5["document"][1],
        "build_source_sha256": BUILD["source"][1],
        "build_protocol_sha256": BUILD["protocol"][1],
        "build_contract_sha256": BUILD["document"][1],
    })
    require(
        type(activation_context) is dict
        and activation_context.get("status") == "PASS"
        and activation_context.get("family") == FAMILY
        and activation_context.get("read_only") is True,
        "verify only the separately frozen original C V5 activation policy",
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
        "v3_frozen_context_verified_before_activation": True,
    }


def render_frozen_contract(options: argparse.Namespace) -> dict[str, Any]:
    _verify_source_owners(options, include_document=False)
    producer = load_original_evaluator(options)
    v3 = _verify_v3_pre_activation(options, producer)
    _read_v21_history(v3)
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
    stem = EVIDENCE_RELATIVE + "/frozen-p0-candidate-worker-v7-c-" + label + "-" + suite
    return stem + ".json.gz", stem + "-publication-receipt.json"


def authenticate_v8_build(options: argparse.Namespace) -> dict[str, Any]:
    checked_label(options.build_label, "build label")
    archive_name = (EVIDENCE_RELATIVE + "/native-source-build-v8-c-"
                    + options.build_label + ".json.gz")
    receipt_name = (EVIDENCE_RELATIVE + "/native-source-build-v8-c-"
                    + options.build_label + "-publication-receipt.json")
    raw, archive_owner = read_owner(
        archive_name, options.build_archive_sha256,
        maximum=64 * 1024 * 1024, private=True)
    receipt_raw, receipt_owner = read_owner(
        receipt_name, options.build_receipt_sha256,
        maximum=MAX_SOURCE_BYTES, private=True)
    require((archive_owner["device"], archive_owner["inode"])
            != (receipt_owner["device"], receipt_owner["inode"]),
            "require genuinely distinct repaired C build evidence owners")
    receipt = exact_json(receipt_raw, "repaired C build receipt")
    require(receipt.get("schema")
            == "rebar-phase2-owned-native-source-build-v8-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == options.build_label
            and receipt.get("source_sha256") == BUILD["source"][1]
            and receipt.get("protocol_sha256") == BUILD["protocol"][1]
            and receipt.get("contract_sha256") == BUILD["document"][1]
            and receipt.get("phase1_manifest_sha256") == PHASE1_SHA256
            and receipt.get("archive_relative") == archive_name
            and receipt.get("archive_sha256") == archive_owner["sha256"]
            and receipt.get("archive_bytes") == archive_owner["size_bytes"]
            and receipt.get("original_source_sha256") == ORIGINAL_C_SHA256
            and receipt.get("derived_source_sha256") == DERIVED_C_SHA256
            and receipt.get("derived_source_apply_count") == 2
            and receipt.get("expected_v8_compiler_process_count") == 14
            and receipt.get("actual_v8_compiler_process_count") == 14
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("winner_selected") is False,
            "reject an unbuilt, failed, borrowed or unproven repaired-C build")
    inflated = gzip.decompress(raw)
    require(len(inflated) <= 48 * 1024 * 1024
            and len(inflated) == receipt.get("uncompressed_bytes")
            and digest(inflated) == receipt.get("uncompressed_sha256"),
            "reject a truncated or forged exact V8 source-build report")
    report = exact_json(inflated, "actual complete repaired C build")
    require(report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("phase_count") == 2
            and report.get("actual_v8_compiler_process_count") == 14
            and report.get("derived_source_sha256") == DERIVED_C_SHA256
            and report.get("derived_source_apply_count") == 2,
            "require two genuinely compiled and reproduced repaired-C phases")
    return {"archive_owner": archive_owner, "receipt_owner": receipt_owner,
            "receipt": receipt, "report": report}


def authenticate_v5_activation(options: argparse.Namespace,
                               build: Mapping[str, Any]) -> dict[str, Any]:
    require_activation_pins()
    activation = frozen_module(
        ACTIVATION_V5["source"][0], ACTIVATION_V5["source"][1],
        "_rebar_frozen_verified_native_activation_v5_for_c_p0")
    require(getattr(activation, "SCHEMA", None)
            == "rebar-phase2-verified-native-activation-v5",
            "reject every legacy V2, V3, or V4 native activator")
    root = options.activation_root
    require(type(root) is str and os.path.isabs(root)
            and root.startswith("/tmp/rebar-phase2-native-activation-v5-c-"),
            "require only the coordinator-pinned genuine private C V5 activation")
    require(options.activation_source_sha256 == ACTIVATION_V5["source"][1]
            and options.activation_protocol_sha256 == ACTIVATION_V5["protocol"][1]
            and options.activation_contract_sha256 == ACTIVATION_V5["document"][1],
            "reject mismatched or missing V5 activation source pins")
    activation.verify_frozen_context({
        "activation_source_sha256": ACTIVATION_V5["source"][1],
        "activation_protocol_sha256": ACTIVATION_V5["protocol"][1],
        "activation_contract_sha256": ACTIVATION_V5["document"][1],
        "build_source_sha256": BUILD["source"][1],
        "build_protocol_sha256": BUILD["protocol"][1],
        "build_contract_sha256": BUILD["document"][1],
    })
    report_raw, activation_report = activation.read_owned(
        root, "activation-report.json", options.activation_report_sha256,
        maximum=MAX_SOURCE_BYTES, private=True)
    receipt_raw, activation_receipt = activation.read_owned(
        root, "activation-receipt.json", options.activation_receipt_sha256,
        maximum=MAX_SOURCE_BYTES, private=True)
    journal_raw, recovery_journal = activation.read_owned(
        root, "recovery-journal.json", options.recovery_journal_sha256,
        maximum=MAX_SOURCE_BYTES, private=True)
    report = activation.strict_document(
        report_raw, "genuine V5 C activation report", canonical_required=True)
    receipt = activation.strict_document(
        receipt_raw, "genuine V5 C activation receipt", canonical_required=True)
    journal = activation.strict_document(
        journal_raw, "genuine V5 C recovery journal", canonical_required=True)
    require(report.get("schema") == activation.SCHEMA + "-actual-activation"
            and report.get("status") == "PASS"
            and report.get("version") == 5
            and report.get("family") == FAMILY
            and report.get("activation_root") == root
            and report.get("group_atomic") is False
            and receipt.get("schema")
            == activation.SCHEMA + "-durable-activation-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("activation_root") == root
            and journal.get("schema") == activation.SCHEMA + "-recovery-journal"
            and journal.get("status") == "PREPARED"
            and journal.get("family") == FAMILY
            and journal.get("activation_root") == root
            and journal.get("target") == NATIVE_RELATIVE
            and journal.get("expected_promoted_sha256")
            == options.native_engine_sha256
            and journal.get("activation_source_sha256")
            == ACTIVATION_V5["source"][1]
            and journal.get("activation_protocol_sha256")
            == ACTIVATION_V5["protocol"][1]
            and journal.get("activation_contract_sha256")
            == ACTIVATION_V5["document"][1]
            and journal.get("build_source_sha256") == BUILD["source"][1]
            and journal.get("build_protocol_sha256") == BUILD["protocol"][1]
            and journal.get("build_contract_sha256") == BUILD["document"][1]
            and journal.get("build_archive_sha256")
            == build["archive_owner"]["sha256"]
            and journal.get("build_receipt_sha256")
            == build["receipt_owner"]["sha256"],
            "reject an absent, legacy, cross-build, or forged V5 live activation")
    require(activation.exact_owner_pair(
        activation_report, receipt.get("activation_report"))
        and activation.exact_owner_pair(
            recovery_journal, report.get("recovery_journal"))
        and activation.exact_owner_pair(
            recovery_journal, receipt.get("recovery_journal")),
        "bind both durable activation owners to the same actual V5 recovery journal")
    native_raw, native = read_owner(
        NATIVE_RELATIVE, options.native_engine_sha256,
        maximum=MAX_BINARY_BYTES)
    require(len(native_raw) == native["size_bytes"]
            and options.native_bridge_sha256 == options.native_engine_sha256,
            "require one actual combined repaired-C native engine and bridge")
    reproduction = build["report"].get("reproducibility")
    require(type(reproduction) is dict
            and reproduction.get("byte_identical") is True
            and reproduction.get("independent_fresh_phase_count") == 2
            and reproduction.get("derived_source_sha256") == DERIVED_C_SHA256,
            "reject a nonreproducible private repaired-C native extension")
    output = reproduction.get("native_outputs", {}).get("extension")
    require(type(output) is dict
            and output.get("sha256") == options.native_engine_sha256
            and output.get("size_bytes") == native["size_bytes"],
            "bind the live repaired-C extension to both real V8 build phases")
    activation_native = {**native, "bytes": native["size_bytes"]}
    require(activation.exact_owner_pair(activation_native, report.get("target"))
            and activation.exact_owner_pair(activation_native,
                                             receipt.get("target")),
            "bind the currently live C inode to its authentic V5 report and receipt")
    return {"module": activation, "root": root,
            "native_owner": native, "build": build,
            "activation_report": activation_report,
            "activation_receipt": activation_receipt,
            "recovery_journal": recovery_journal}


def observe_original_suite(options: argparse.Namespace) -> dict[str, Any]:
    context = verify_live_worker_context(options)
    build = authenticate_v8_build(options)
    approval = authenticate_v5_activation(options, build)
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
    observed["verified_v8_build_archive_sha256"] = build["archive_owner"]["sha256"]
    observed["verified_v8_build_receipt_sha256"] = build["receipt_owner"]["sha256"]
    observed["verified_v5_activation_source_sha256"] = ACTIVATION_V5["source"][1]
    observed["verified_v5_activation_report_sha256"] = options.activation_report_sha256
    observed["verified_v5_activation_receipt_sha256"] = options.activation_receipt_sha256
    observed["verified_v5_recovery_journal_sha256"] = options.recovery_journal_sha256
    observed["nested_producer_sha256"] = options.producer_source_sha256
    observed["historical_evidence_owner_count"] = HISTORICAL_EVIDENCE_OWNER_COUNT
    observed["historical_authenticated_reference_count"] = (
        HISTORICAL_AUTHENTICATED_REFERENCE_COUNT)
    observed["phase_one_case_execution_denominator"] = CASE_DENOMINATOR
    observed["supplemental_cases_added_to_phase_one"] = False
    observed["candidate_qualified"] = False
    observed["winner_selected"] = False
    return observed


def publish_suite(report: dict[str, Any], options: argparse.Namespace) -> dict[str, Any]:
    compressed, expanded_sha, expanded_size = stream_gzip(report)
    archive_name, receipt_name = suite_evidence_names(options.suite, options.label)
    archive = create_private_owner(archive_name, compressed)
    receipt_document = {
        "schema": SCHEMA + "-durable-suite-publication-receipt",
        "status": "PASS", "candidate_status": report["status"],
        "candidate_family": FAMILY, "label": options.label,
        "suite": options.suite,
        "case_execution_denominator": report["case_execution_denominator"],
        "phase_one_case_execution_denominator": CASE_DENOMINATOR,
        "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "original_c_source_sha256": ORIGINAL_C_SHA256,
        "derived_c_source_sha256": DERIVED_C_SHA256,
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
    receipt = create_private_owner(receipt_name, canonical(receipt_document))
    return {
        "schema": SCHEMA + "-published-original-suite",
        "status": report["status"],
        "candidate_family": FAMILY, "label": options.label,
        "suite": options.suite,
        "case_execution_denominator": report["case_execution_denominator"],
        "mismatch_count": report.get("mismatch_count"),
        "archive": archive, "receipt": receipt,
        "uncompressed_sha256": expanded_sha,
        "uncompressed_bytes": expanded_size,
        "all_original_records_and_mismatches_preserved": True,
        "original_producer_sha256": ORIGINAL_PRODUCER["source"][1],
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_qualified": False,
        "winner_selected": False,
    }


def run_actual_suite(options: argparse.Namespace) -> dict[str, Any]:
    try:
        report = observe_original_suite(options)
    except BaseException as error:
        details = getattr(error, "details", None)
        count = dict(SUITES)[options.suite]
        report = {
            "schema": SCHEMA + "-complete-original-suite-failure",
            "status": "FAIL", "suite": options.suite,
            "candidate_family": FAMILY,
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
    return publish_suite(report, options)


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
    parser.add_argument("--activation-root")
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
        "reject absent, legacy, substituted, or inconsistent V3 producer pins",
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
        "pin the actual genuine C V8 build and live V5 activation completely",
    )
    checked_label(options.label)
    checked_label(options.build_label, "build label")
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
        elif options.render_contract:
            result = render_frozen_contract(options)
            raw = canonical(result)
            require(
                len(raw) <= MAX_PUBLIC_REPORT_BYTES,
                "bound the complete immutable V9 source contract",
            )
            sys.stdout.buffer.write(raw)
            sys.stdout.buffer.flush()
            return 0
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            result = run_actual_suite(options)
        raw = canonical(result)
        require(
            len(raw) <= MAX_PUBLIC_REPORT_BYTES,
            "never truncate or hide an original C worker summary",
        )
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
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
