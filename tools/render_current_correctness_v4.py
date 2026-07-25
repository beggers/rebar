#!/usr/bin/env python3
"""Reproducibly explain actual from-scratch regex correctness and failures."""

from __future__ import annotations

import argparse
import builtins
import contextlib
import copy
import hashlib
import html
import importlib
import io
import json
import multiprocessing
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import types
from typing import Any, Callable, Iterator


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "rebar-current-native-correctness-v4"
SOURCE_PATH = "tools/render_current_correctness_v4.py"
CHART_PATH = "docs/evidence/current-native-correctness-v4.svg"
MANIFEST_PATH = "docs/evidence/current-native-correctness-v4.json"
V3_SOURCE_PATH = "tools/render_current_correctness_v3.py"
V3_SOURCE_SHA256 = "91055db20abf1a0b60dedca7877dc4aefb8a31bc2ff1df8be1285cbed26eef34"
V15_SOURCE_PATH = "tools/postfinal_cpython_locale_oracle_v15.py"
V15_SOURCE_SHA256 = "12adb54e895ac0154b1b08ea96cd73b6cbfff4713c764058c5551fe6bba68c43"
V15_PROTOCOL_PATH = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V15.md"
V15_PROTOCOL_SHA256 = "d685374a6698056022aa2ef8a46f16bd3d2b8548aab2ac122a59bba7ac0e9f7a"
V6_REFERENCE_PATH = "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
V6_REFERENCE_SHA256 = "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
METHOD_MATRIX_SHA256 = "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
RUST_V15_FAILURE_PATH = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-rust-failures.json"
)
RUST_V15_FAILURE_SHA256 = "fcd83830b36afd94dee6b926764a6300eaf048d5fa81404563d7e8afea2482c2"
RUST_V15_FAILURE_BYTES = 17_338_567
RUST_V15_STDOUT_BYTES = 3_474_497
RUST_V15_STDOUT_SHA256 = "bb6ed67d4cf96c2bc1be9dd64779cb5219ac3cdcf909fd5efd93dbf6da8a55ac"
RESOURCE_PATH = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-rust-resource-preflight.json"
)
RESOURCE_SHA256 = "2847f9f69d32da9c00546b637bd01d3c4ca58001db0a51e284096dbbfd50690e"
INTEGRATION_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v15-readonly-native-bridge-integration-pass.json"
)
INTEGRATION_SHA256 = "f2f9c3673c23054dbf2dbc92138e68a5f31d68dea5c8cfce779874188b53c948"
FORENSIC_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v15-rust-readonly-failure-forensic.json"
)
FORENSIC_SHA256 = "4613b2421b3df30c5bebdbb4ae7c0d3530d80b70d5a627396aad2a25fefe85eb"
PRODUCTION_SUMMARY_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v15-rust-failures-production-summary.json"
)
PRODUCTION_SUMMARY_SHA256 = (
    "d923e4687be96751e11b334cf8a37c0744552d01592cbb665bc4ec0cf9432c10"
)
PRIVATE_DEBUG_METHOD = "ReTests.test_memory_leaks"
PRIVATE_DEBUG_REASON = "requires debug build"
PRIVATE_DEBUG_SKIP_KIND = "named-private-debug-condition"
PRIVATE_DEBUG_SOURCE_AST_SHA256 = (
    "840264aaf4bf27c06d29ac78664767327a8f4b90008c5db994c88542c692b389"
)
PICKLING_METHOD = "ReTests.test_pickling"
PICKLING_ERROR = "cannot import name '_compile' from 'candidates.rust_candidate'"
HARNESS_ERROR_MARKER = "stage07_blocked_regex"
FAMILIES = (("rust", "Rust"), ("vm", "C"), ("zig", "Zig"))
PUBLIC_METHODS = 152
METHOD_GUARDS = 304
MAX_INPUT_BYTES = 128 * 1024 * 1024


class ChartError(Exception):
    """The independently verified visualization evidence is incomplete."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ChartError(message)


def canonical(document: Any) -> bytes:
    return (json.dumps(document, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def _read_regular(relative: str) -> bytes:
    require(type(relative) is str and relative and "\\" not in relative,
            "only a frozen repository-relative correctness path is permitted")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts,
            "a bounded correctness path escaped the actual repository")
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_CLOEXEC", 0))
    descriptor = os.open(str(ROOT / path), flags)
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode)
                and 0 < information.st_size <= MAX_INPUT_BYTES,
                "a genuine frozen correctness artifact is not a bounded regular file")
        pieces: list[bytes] = []
        while True:
            piece = os.read(descriptor, 1024 * 1024)
            if not piece:
                break
            pieces.append(piece)
        raw = b"".join(pieces)
        require(len(raw) == information.st_size,
                "a real frozen correctness artifact changed during its read")
        return raw
    finally:
        os.close(descriptor)


def _checked_json(relative: str, expected: str,
                  expected_bytes: int | None = None) -> dict[str, Any]:
    raw = _read_regular(relative)
    require(hashlib.sha256(raw).hexdigest() == expected
            and (expected_bytes is None or len(raw) == expected_bytes),
            "an actual frozen correctness artifact changed: " + relative)
    try:
        document = json.loads(raw)
    except (ValueError, UnicodeError) as error:
        raise ChartError("an actual complete correctness artifact is not JSON") from error
    require(type(document) is dict,
            "an actual correctness artifact lost its complete JSON object")
    return document


def _frozen_module(path: str, expected: str, name: str) -> types.ModuleType:
    source = _read_regular(path)
    require(hashlib.sha256(source).hexdigest() == expected,
            "an independently frozen correctness validator changed: " + path)
    result = types.ModuleType(name)
    result.__file__ = str(ROOT / path)
    exec(compile(source, result.__file__, "exec", dont_inherit=True),
         result.__dict__)
    return result


def _validate_resource(resource: dict[str, Any]) -> None:
    require(resource.get("schema") == "rebar-root-v15-genuine-upstream-resource-preflight"
            and resource.get("status") == "PASS"
            and resource.get("source_sha256") == V15_SOURCE_SHA256
            and resource.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and resource.get("configured_original_memory_bytes") == 40 * 1024**3
            and resource.get("required_large_substitution_memory_bytes")
            == 18 * 2**31
            and resource.get("minimum_additional_safety_reserve_bytes")
            == 8 * 1024**3
            and type(resource.get("effective_available_memory_bytes")) is int
            and resource["effective_available_memory_bytes"]
            >= (18 * 2**31 + 8 * 1024**3)
            and resource.get("cpu_resource_enabled") is True
            and resource.get("fork_available") is True
            and resource.get("multiprocessing_extension_available") is True
            and resource.get("actual_single_memory_worker_lock_available") is True
            and resource.get("actual_candidate_workers") == 0
            and resource.get("actual_reference_workers") == 0
            and resource.get("candidate_imports") == 0
            and resource.get("performance") == "NOT MEASURED"
            and resource.get("holdout") == "NOT ACCESSED",
            "the genuine full-size, CPU, fork, or memory prerequisites changed")
    locales = resource.get("actual_fresh_private_locales")
    require(type(locales) is dict and locales.get("iso_8859_1_passed") is True
            and locales.get("utf_8_passed") is True
            and bool(locales.get("fresh_private_localedef")),
            "both genuinely generated private original locales are required")


def _validate_integration(integration: dict[str, Any]) -> None:
    require(integration.get("schema") ==
            "rebar-root-v15-all-family-read-only-native-bridge-and-candidate-safe-graph-integration"
            and integration.get("status") == "PASS"
            and integration.get("source_sha256") == V15_SOURCE_SHA256
            and integration.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and integration.get("actual_genuine_reference_roles") == 2
            and integration.get("actual_original_methods_per_reference") == 152
            and integration.get("actual_named_private_debug_skips_per_reference") == 1
            and integration.get("source_count") == 12
            and integration.get("native_binary_count") == 5
            and integration.get("candidate_safe_graph_source_files_rehashed") == 12
            and integration.get("candidate_safe_graph_native_binaries_rehashed") == 5
            and integration.get("candidate_safe_graph_verification_called") is True
            and integration.get("actual_candidate_workers") == 0
            and integration.get("actual_reference_workers") == 0
            and integration.get("actual_native_owner_workers") == 0
            and integration.get("stdlib_sre_permitted") is False
            and integration.get("all_matcher_descendants_permitted") is False
            and integration.get("historical_failure_qualifies_current_engine") is False
            and integration.get("performance") == "NOT MEASURED"
            and integration.get("holdout") == "NOT ACCESSED",
            "the exact genuine 12-source, five-native integration was weakened")
    effects = integration.get("read_only_boundary_effects")
    require(type(effects) is dict
            and set(effects) == {
                "native_workers_started", "subprocesses_started",
                "candidate_imports", "filesystem_writes", "clock_samples",
            }
            and all(value == 0 for value in effects.values()),
            "the independently published V15 integration was not genuinely read-only")
    families = integration.get("independent_families")
    require(type(families) is dict and set(families) == {"rust", "vm", "zig"},
            "a genuine independently owned engine was omitted from integration")


def _validate_v15_failure(
    report: dict[str, Any], *, frozen: Any,
    previous: dict[str, Any], v2: Any, v1: Any,
) -> dict[str, Any]:
    require(report.get("schema") ==
            "rebar-postfinal-cpython-full-public-locale-v15-actual-role-failure"
            and report.get("status") == "FAIL"
            and report.get("role") == "rust"
            and report.get("source_sha256") == V15_SOURCE_SHA256
            and report.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and report.get("immutable_v6_reference_sha256") == V6_REFERENCE_SHA256
            and report.get("actual_failure_destination") == RUST_V15_FAILURE_PATH
            and report.get("synthetic") is False
            and report.get("production_observations_invented") is False
            and report.get("performance") == "NOT MEASURED"
            and report.get("holdout") == "NOT ACCESSED",
            "the exact genuine complete V15 Rust failure was changed")
    details = report.get("details")
    require(type(details) is dict and details.get("returncode") == 2
            and details.get("complete_streams_available") is True
            and details.get("production_observations_invented") is False,
            "the once-only original complete candidate worker was not preserved")
    stdout = details.get("stdout")
    stderr = details.get("stderr")
    require(type(stdout) is dict
            and stdout.get("encoding") == "hex"
            and stdout.get("bytes") == RUST_V15_STDOUT_BYTES
            and stdout.get("sha256") == RUST_V15_STDOUT_SHA256
            and stdout.get("truncated") is False
            and type(stdout.get("complete_hex")) is str
            and type(stderr) is dict and stderr.get("encoding") == "hex"
            and stderr.get("bytes") == 0
            and stderr.get("sha256") == hashlib.sha256(b"").hexdigest()
            and stderr.get("truncated") is False
            and stderr.get("complete_hex") == "",
            "the genuine 3,474,497-byte worker stdout was concealed")
    try:
        complete_stdout = bytes.fromhex(stdout["complete_hex"])
        observed_worker = json.loads(complete_stdout)
    except (UnicodeError, ValueError) as error:
        raise ChartError("the complete real upstream worker stdout is invalid") from error
    require(len(complete_stdout) == RUST_V15_STDOUT_BYTES
            and hashlib.sha256(complete_stdout).hexdigest()
            == RUST_V15_STDOUT_SHA256
            and type(observed_worker) is dict
            and observed_worker == details.get("actual_worker_document")
            and observed_worker.get("schema") ==
            frozen.SCHEMA + "-actual-worker-failure"
            and observed_worker.get("status") == "FAIL"
            and observed_worker.get("role") == "rust",
            "the complete actual original V15 worker was fabricated or truncated")
    worker = details.get("actual_worker_failure_details")
    require(type(worker) is dict
            and observed_worker.get("details") == worker
            and worker.get("completed_original_method_count") == PUBLIC_METHODS
            and worker.get("actual_native_owner_method_guard_checks") == METHOD_GUARDS
            and worker.get("actual_cached_matcher_method_guard_checks") == METHOD_GUARDS
            and worker.get("production_observations_invented") is False
            and worker.get("performance") == "NOT MEASURED"
            and worker.get("holdout") == "NOT ACCESSED",
            "the actual complete 152-method/304-owner worker trace was omitted")
    records = worker.get("completed_original_method_records")
    require(type(records) is list and len(records) == PUBLIC_METHODS,
            "an actual original Python method was lost from the failure")
    reference = _checked_json(V6_REFERENCE_PATH, V6_REFERENCE_SHA256)
    matrix = v2._validate_matrix(reference, frozen, v1)
    actual_reference = reference["roles"]["reference_a"]["records"]
    passed = 0
    private = 0
    interference: list[dict[str, str]] = []
    candidate: list[dict[str, str]] = []
    for expected, actual in zip(actual_reference, records, strict=True):
        require(type(actual) is dict
                and actual.get("test") == expected.get("test")
                and actual.get("source_ast_sha256")
                == expected.get("source_ast_sha256"),
                "a genuinely original executed method changed source or order")
        state = actual.get("status")
        if state == "PASS":
            require(expected.get("status") == "PASS",
                    "a nonapplicable private original method became a pass")
            passed += 1
        elif state == "SKIP":
            require(expected.get("status") == "SKIP"
                    and actual.get("test") == PRIVATE_DEBUG_METHOD
                    and actual.get("reason") == PRIVATE_DEBUG_REASON
                    and actual.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                    and actual.get("source_ast_sha256")
                    == PRIVATE_DEBUG_SOURCE_AST_SHA256,
                    "the sole genuine original private-debug skip changed")
            private += 1
        elif state == "ERROR":
            require(expected.get("status") == "PASS"
                    and type(actual.get("reason")) is str
                    and bool(actual["reason"]),
                    "an original candidate failure lacks its real complete reason")
            reason = actual["reason"]
            observation = {
                "test": actual["test"],
                "reason_sha256": hashlib.sha256(reason.encode("utf-8")).hexdigest(),
                "source_ast_sha256": actual["source_ast_sha256"],
                "complete_reason_characters": len(reason),
            }
            if HARNESS_ERROR_MARKER in reason:
                require(actual["test"] != PICKLING_METHOD,
                        "the genuine `_compile` candidate gap was hidden as harness")
                observation["classification"] = (
                    "test-harness matcher-guard interference"
                )
                interference.append(observation)
            else:
                require(actual["test"] == PICKLING_METHOD
                        and PICKLING_ERROR in reason,
                        "an unexplained original candidate error was concealed")
                observation["classification"] = (
                    "from-scratch Rust private pickle hook missing"
                )
                candidate.append(observation)
        else:
            raise ChartError("an actual original method status was weakened")
    require(passed == 139 and len(interference) == 11
            and len(candidate) == 1 and private == 1
            and passed + len(interference) + len(candidate) + private
            == PUBLIC_METHODS,
            "the actual 139 pass, 11 harness error, 1 real candidate error, "
            "and 1 private skip denominator was changed")
    original_rows = previous.get("rows")
    edge = next((row for row in original_rows
                 if row.get("family") == "rust" and row.get("kind") == "original"),
                None)
    require(type(edge) is dict and type(edge.get("proof_path")) is str,
            "the independently authenticated current Rust owner proof is missing")
    edge_proof = _checked_json(edge["proof_path"], edge["proof_sha256"])
    expected_native = edge_proof.get("full_current_family_native_elf_sha256")
    require(type(expected_native) is dict and bool(expected_native),
            "the genuine complete owned Rust native ELF graph was substituted")
    native_trace = worker.get("actual_completed_native_method_owners")

    def verify_owner(owner: Any, family: str, expected: Any) -> dict[str, Any]:
        require(family == "rust" and expected == expected_native,
                "an actual method guard belongs to a different matching engine")
        v1._validate_owner(owner, "rust", "candidates.rust_candidate")
        require(owner.get("native_binary_sha256") == expected_native
                and owner.get("schema") ==
                "rebar-postfinal-from-scratch-audit-v10-native-owner-worker"
                and owner.get("match_repr_checks") == 2
                and owner.get("persistent_cross_engine_guard") is True,
                "an actual V15 method lost its complete owned binary guard")
        return owner

    frozen._validate_native_method_trace(
        "rust", matrix, native_trace, expected_native, verify_owner,
    )
    return {
        "family": "rust", "label": "Rust", "status": "FAIL",
        "completed_methods": PUBLIC_METHODS,
        "total_methods": PUBLIC_METHODS,
        "passed_methods": passed,
        "error_methods": len(interference) + len(candidate),
        "harness_interference_errors": len(interference),
        "genuine_candidate_errors": len(candidate),
        "named_private_debug_skips": private,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "full_official_suite_qualified": False,
        "harness_interference_error_records": interference,
        "genuine_candidate_error_records": candidate,
        "genuine_candidate_error_test": PICKLING_METHOD,
        "genuine_candidate_error": PICKLING_ERROR,
        "failure_path": RUST_V15_FAILURE_PATH,
        "failure_sha256": RUST_V15_FAILURE_SHA256,
        "failure_bytes": RUST_V15_FAILURE_BYTES,
        "actual_complete_worker_stdout_sha256": RUST_V15_STDOUT_SHA256,
        "actual_complete_worker_stdout_bytes": RUST_V15_STDOUT_BYTES,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def _validate_forensic_and_summary(
    forensic: dict[str, Any], summary: dict[str, Any],
    current: dict[str, Any], frozen: Any,
) -> dict[str, Any]:
    require(forensic.get("schema") ==
            "rebar-root-v15-genuine-rust-original-suite-read-only-failure-forensic"
            and forensic.get("status") == "PASS"
            and forensic.get("source_sha256") == V15_SOURCE_SHA256
            and forensic.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and forensic.get("actual_candidate_result") == "FAIL"
            and forensic.get("actual_failure_path") == RUST_V15_FAILURE_PATH
            and forensic.get("actual_failure_sha256") == RUST_V15_FAILURE_SHA256
            and forensic.get("actual_failure_bytes") == RUST_V15_FAILURE_BYTES
            and forensic.get("original_method_denominator") == PUBLIC_METHODS
            and forensic.get("actual_original_methods_completed") == PUBLIC_METHODS
            and forensic.get("actual_passing_original_methods") == 139
            and forensic.get("actual_error_original_methods") == 12
            and forensic.get("actual_harness_interference_errors") == 11
            and forensic.get("actual_required_original_test_candidate_gaps") == 1
            and forensic.get("actual_named_private_debug_skips") == 1
            and forensic.get("authentic_named_private_debug_skip_kind")
            == PRIVATE_DEBUG_SKIP_KIND
            and forensic.get("actual_native_owner_method_guard_checks") == METHOD_GUARDS
            and forensic.get("actual_cached_matcher_method_guard_checks") == METHOD_GUARDS
            and forensic.get("actual_worker_returncode") == 2
            and forensic.get("actual_worker_stdout_bytes") == RUST_V15_STDOUT_BYTES
            and forensic.get("actual_worker_stdout_sha256") == RUST_V15_STDOUT_SHA256
            and forensic.get("actual_worker_stdout_completely_preserved_inside_failure")
            is True
            and forensic.get("historical_failure_qualifies_current_engine") is False
            and forensic.get("production_observations_invented") is False
            and forensic.get("performance") == "NOT MEASURED"
            and forensic.get("holdout") == "NOT ACCESSED",
            "the independent actual 139/11/1/1 failure forensic was changed")
    effects = forensic.get("read_only_boundary_effects")
    require(type(effects) is dict
            and set(effects) == {"native_workers_started", "subprocesses_started",
                                 "candidate_imports", "filesystem_writes",
                                 "clock_samples"}
            and all(value == 0 for value in effects.values()),
            "the independently executed V15 failure forensic started a worker")
    require(summary.get("schema") ==
            "rebar-root-v15-rust-actual-complete-original-suite-production-summary"
            and summary.get("status") == "FAIL"
            and summary.get("role") == "rust"
            and summary.get("source_sha256") == V15_SOURCE_SHA256
            and summary.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and summary.get("actual_failure_path") == RUST_V15_FAILURE_PATH
            and summary.get("actual_failure_sha256") == RUST_V15_FAILURE_SHA256
            and summary.get("actual_failure_bytes") == RUST_V15_FAILURE_BYTES
            and summary.get("actual_controller_returncode") == 2
            and summary.get("actual_original_method_denominator") == PUBLIC_METHODS
            and summary.get("actual_original_methods_completed") == PUBLIC_METHODS
            and summary.get("actual_passing_original_methods") == 139
            and summary.get("actual_error_original_methods") == 12
            and summary.get("actual_harness_interference_errors") == 11
            and summary.get("actual_required_original_test_candidate_gaps") == 1
            and summary.get("actual_named_private_debug_skips") == 1
            and summary.get("actual_native_owner_method_guard_checks") == METHOD_GUARDS
            and summary.get("actual_cached_matcher_method_guard_checks") == METHOD_GUARDS
            and summary.get("actual_complete_original_worker_stdout_bytes")
            == RUST_V15_STDOUT_BYTES
            and summary.get("actual_complete_original_worker_stdout_sha256")
            == RUST_V15_STDOUT_SHA256
            and summary.get("actual_complete_original_worker_stdout_preserved_inside_failure")
            is True
            and summary.get("actual_read_only_failure_forensic_path") == FORENSIC_PATH
            and summary.get("actual_read_only_failure_forensic_sha256")
            == FORENSIC_SHA256
            and summary.get("actual_resource_preflight_path") == RESOURCE_PATH
            and summary.get("actual_resource_preflight_sha256") == RESOURCE_SHA256
            and summary.get("complete_canonical_failure_document_preserved") is True
            and summary.get("full_original_suite_candidate_qualified") is False
            and summary.get("production_observations_invented") is False
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("holdout") == "NOT ACCESSED",
            "the authentic complete V15 root-production summary was substituted")
    observed_failures = forensic.get("actual_nonpassing_original_methods")
    require(type(observed_failures) is list and len(observed_failures) == 12
            and summary.get("actual_nonpassing_original_methods")
            == observed_failures,
            "the independently preserved twelve failure observations disagree")
    expected = {
        observation["test"]: observation
        for observation in (
            *current["harness_interference_error_records"],
            *current["genuine_candidate_error_records"],
        )
    }
    require(len(expected) == 12,
            "an independently classified original failure was duplicated")
    actual_names: set[str] = set()
    for observed in observed_failures:
        require(type(observed) is dict and observed.get("status") == "ERROR",
                "the root forensic invented a nonfailing original method")
        name = observed.get("test")
        require(type(name) is str and name in expected and name not in actual_names,
                "an independently classified original error was omitted or repeated")
        genuine = expected[name]
        require(observed.get("classification") == genuine["classification"]
                and observed.get("complete_reason_sha256")
                == genuine["reason_sha256"]
                and observed.get("complete_reason_characters")
                == genuine["complete_reason_characters"]
                and observed.get("source_ast_sha256")
                == genuine["source_ast_sha256"]
                and type(observed.get("reason_preview")) is str,
                "an actual complete error reason or classification was forged")
        actual_names.add(name)
    original_receipt = forensic.get("actual_exclusive_publication_receipt")
    documented_receipt = summary.get("actual_failure_publication_receipt")
    require(original_receipt == documented_receipt,
            "the real exclusive failure syscall receipt was concealed or swapped")
    receipt = frozen._validate_publication_receipt(original_receipt)
    require(len(receipt) == 11
            and receipt.get("path") == RUST_V15_FAILURE_PATH
            and receipt.get("expected_payload_sha256") == RUST_V15_FAILURE_SHA256
            and receipt.get("expected_payload_bytes") == RUST_V15_FAILURE_BYTES
            and receipt.get("actual_payload_bytes_written")
            == RUST_V15_FAILURE_BYTES
            and receipt.get("actual_write_calls") == [{
                "requested_bytes": RUST_V15_FAILURE_BYTES,
                "returned_bytes": RUST_V15_FAILURE_BYTES,
            }]
            and receipt.get("actual_file_created") is True
            and receipt.get("actual_file_fsync") is True
            and receipt.get("actual_directory_fsync") is True
            and receipt.get("canonical_reread_succeeded") is True
            and receipt.get("fully_durable_publication") is True,
            "the actual 17,338,567-byte once-only durable receipt changed")
    return copy.deepcopy(receipt)


def _snapshot() -> tuple[dict[str, Any], list[dict[str, str]]]:
    legacy = _frozen_module(V3_SOURCE_PATH, V3_SOURCE_SHA256,
                            "_rebar_frozen_current_correctness_v3")
    frozen = _frozen_module(V15_SOURCE_PATH, V15_SOURCE_SHA256,
                            "_rebar_frozen_original_correctness_v15")
    protocol = _read_regular(V15_PROTOCOL_PATH)
    require(hashlib.sha256(protocol).hexdigest() == V15_PROTOCOL_SHA256
            and frozen.SCHEMA == "rebar-postfinal-cpython-full-public-locale-v15"
            and frozen.SOURCE_RELATIVE == V15_SOURCE_PATH
            and frozen.PROTOCOL_RELATIVE == V15_PROTOCOL_PATH
            and frozen.PROTOCOL_SHA256 == V15_PROTOCOL_SHA256
            and frozen.V6_REFERENCE_SHA256 == V6_REFERENCE_SHA256
            and frozen.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
            and tuple(frozen.FAMILIES) == tuple(name for name, _ in FAMILIES),
            "the actual frozen 152-method V15 controller was substituted")
    previous, inputs = legacy._snapshot()
    legacy._validate_snapshot(previous)
    prior_latest = previous["full_python_suite"][0]
    require(prior_latest.get("family") == "rust"
            and prior_latest.get("status") == "FAIL"
            and prior_latest.get("completed_methods") == 0
            and prior_latest.get("native_owner_guards") == 0
            and prior_latest.get("actual_error") ==
            "the V11 correctness controller must never import a candidate",
            "the actual third zero-test harness failure was concealed")
    resource = _checked_json(RESOURCE_PATH, RESOURCE_SHA256)
    _validate_resource(resource)
    integration = _checked_json(INTEGRATION_PATH, INTEGRATION_SHA256)
    _validate_integration(integration)
    v2 = legacy._frozen_module(legacy.V2_SOURCE_PATH,
                               legacy.V2_SOURCE_SHA256,
                               "_rebar_frozen_actual_correctness_v2_for_v4")
    v1 = v2._frozen_module(v2.V1_SOURCE_PATH, v2.V1_SOURCE_SHA256,
                           "_rebar_frozen_actual_correctness_v1_for_v4")
    failure = _checked_json(RUST_V15_FAILURE_PATH, RUST_V15_FAILURE_SHA256,
                            RUST_V15_FAILURE_BYTES)
    current = _validate_v15_failure(
        failure, frozen=frozen, previous=previous, v2=v2, v1=v1,
    )
    forensic = _checked_json(FORENSIC_PATH, FORENSIC_SHA256)
    summary = _checked_json(PRODUCTION_SUMMARY_PATH, PRODUCTION_SUMMARY_SHA256)
    actual_receipt = _validate_forensic_and_summary(
        forensic, summary, current, frozen,
    )
    current["actual_durable_failure_receipt_verified"] = True
    current["actual_exclusive_publication_receipt"] = actual_receipt
    current["actual_forensic_path"] = FORENSIC_PATH
    current["actual_forensic_sha256"] = FORENSIC_SHA256
    current["actual_production_summary_path"] = PRODUCTION_SUMMARY_PATH
    current["actual_production_summary_sha256"] = PRODUCTION_SUMMARY_SHA256
    result = copy.deepcopy(previous)
    result["historical_v14_rust_upstream_failure"] = copy.deepcopy(prior_latest)
    result["full_python_suite"] = [current,
                                    *copy.deepcopy(previous["full_python_suite"][1:])]
    result["official_suite_candidate_passes"] = sum(
        row.get("status") == "PASS" for row in result["full_python_suite"]
    )
    result["full_drop_in_compatibility"] = "NOT ESTABLISHED"
    result["current_actual_full_upstream_observation"] = {
        "passed_methods": 139, "harness_interference_errors": 11,
        "genuine_candidate_errors": 1, "private_debug_skips": 1,
        "completed_methods": PUBLIC_METHODS,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
    }
    identities = [copy.deepcopy(item) for item in inputs]
    identities.extend((
        {"purpose": "frozen-v3-actual-original-correctness-validator",
         "path": V3_SOURCE_PATH, "sha256": V3_SOURCE_SHA256},
        {"purpose": "frozen-v15-full-upstream-correctness-source",
         "path": V15_SOURCE_PATH, "sha256": V15_SOURCE_SHA256},
        {"purpose": "frozen-v15-full-upstream-correctness-protocol",
         "path": V15_PROTOCOL_PATH, "sha256": V15_PROTOCOL_SHA256},
        {"purpose": "v15-genuine-original-resource-preflight",
         "path": RESOURCE_PATH, "sha256": RESOURCE_SHA256},
        {"purpose": "v15-genuine-zero-worker-native-integration",
         "path": INTEGRATION_PATH, "sha256": INTEGRATION_SHA256},
        {"purpose": "v15-complete-genuine-152-method-rust-failure",
         "path": RUST_V15_FAILURE_PATH, "sha256": RUST_V15_FAILURE_SHA256},
        {"purpose": "v15-genuine-zero-worker-152-method-failure-forensic",
         "path": FORENSIC_PATH, "sha256": FORENSIC_SHA256},
        {"purpose": "v15-genuine-root-frozen-actual-production-summary",
         "path": PRODUCTION_SUMMARY_PATH,
         "sha256": PRODUCTION_SUMMARY_SHA256},
    ))
    identities.sort(key=lambda row: row["path"])
    require(len(identities) == 39
            and len({item["path"] for item in identities}) == 39,
            "the exact 39 frozen all-family original correctness inputs changed")
    return result, identities


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    require(type(snapshot) is dict and snapshot.get("candidate_count") == 3
            and snapshot.get("original_candidate_checks") == 669_594
            and snapshot.get("deeper_candidate_checks") == 1_179
            and snapshot.get("observed_original_or_deeper_mismatches") == 0
            and snapshot.get("full_drop_in_compatibility") == "NOT ESTABLISHED"
            and snapshot.get("performance") == "NOT MEASURED"
            and snapshot.get("holdout") == "NOT ACCESSED",
            "a frozen all-engine correctness denominator or speed was invented")
    rows = snapshot.get("rows")
    require(type(rows) is list and len(rows) == 6
            and all(type(row) is dict and row.get("status") == "PASS"
                    and row.get("mismatches") == 0
                    and row.get("passed") == row.get("total") for row in rows),
            "a genuinely complete original or deeper mismatch was concealed")
    for key, stage in (
        ("historical_v12_rust_upstream_failure", "V12"),
        ("historical_v13_rust_upstream_failure", "V13"),
        ("historical_v14_rust_upstream_failure", "V14"),
    ):
        previous = snapshot.get(key)
        require(type(previous) is dict and previous.get("family") == "rust"
                and previous.get("completed_methods") == 0,
                "a genuine zero-test harness failure was hidden: " + stage)
        if stage == "V12":
            require(previous.get("status") == "STOPPED BEFORE TESTS"
                    and previous.get("cause") == "test-harness bridge wiring",
                    "the genuine original missing-bridge failure was changed")
        elif stage == "V13":
            require(previous.get("status") == "FAIL"
                    and previous.get("native_owner_guards") == 0
                    and previous.get("actual_error") ==
                    "stage-07 blocked unowned matching import: re",
                    "the genuine matcher-isolation harness failure was changed")
        else:
            require(previous.get("status") == "FAIL"
                    and previous.get("native_owner_guards") == 0
                    and previous.get("actual_error") ==
                    "the V11 correctness controller must never import a candidate",
                    "the genuine original controller-isolation failure was changed")
    suites = snapshot.get("full_python_suite")
    require(type(suites) is list and len(suites) == 3
            and tuple(row.get("family") for row in suites)
            == tuple(family for family, _ in FAMILIES),
            "a real independent engine was removed or duplicated")
    passed = 0
    for row in suites:
        require(type(row) is dict and row.get("total_methods") == PUBLIC_METHODS
                and row.get("status") in {"PASS", "FAIL", "NOT RUN"},
                "an actual candidate full-suite status or denominator changed")
        if row["status"] == "PASS":
            require(row.get("completed_methods") == PUBLIC_METHODS
                    and row.get("passed_methods") == 151
                    and row.get("named_private_debug_skips") == 1
                    and row.get("native_owner_guards") == METHOD_GUARDS
                    and row.get("cached_matcher_guards") == METHOD_GUARDS
                    and row.get("full_official_suite_qualified") is True,
                    "an actual original-suite pass weakened a method or guard")
            passed += 1
        elif row["status"] == "FAIL" and row.get("family") == "rust":
            interference = row.get("harness_interference_error_records")
            candidate = row.get("genuine_candidate_error_records")
            require(row.get("completed_methods") == PUBLIC_METHODS
                    and row.get("passed_methods") == 139
                    and row.get("error_methods") == 12
                    and row.get("harness_interference_errors") == 11
                    and row.get("genuine_candidate_errors") == 1
                    and row.get("named_private_debug_skips") == 1
                    and row.get("native_owner_guards") == METHOD_GUARDS
                    and row.get("cached_matcher_guards") == METHOD_GUARDS
                    and row.get("genuine_candidate_error_test") == PICKLING_METHOD
                    and row.get("genuine_candidate_error") == PICKLING_ERROR
                    and type(interference) is list and len(interference) == 11
                    and type(candidate) is list and len(candidate) == 1
                    and candidate[0].get("test") == PICKLING_METHOD
                    and row.get("full_official_suite_qualified") is False,
                    "the real 139/11/1/1 Rust outcome was changed or falsely qualified")
        elif row["status"] == "FAIL":
            require(type(row.get("completed_methods")) is int
                    and 0 <= row["completed_methods"] <= PUBLIC_METHODS
                    and row.get("full_official_suite_qualified") is False,
                    "a failed original candidate was falsely qualified")
        else:
            require(row.get("completed_methods") is None
                    and row.get("native_owner_guards") is None
                    and row.get("full_official_suite_qualified") is False,
                    "an unexecuted original role was given invented results")
    require(snapshot.get("official_suite_candidate_passes") == passed,
            "the genuine all-candidate original pass denominator was changed")


def _text(x: int, y: int, value: str, style: str = "body") -> str:
    return (f'<text x="{x}" y="{y}" class="{style}">'
            + html.escape(value) + "</text>")


def render_svg(snapshot: dict[str, Any]) -> bytes:
    _validate_snapshot(snapshot)
    suites = snapshot["full_python_suite"]
    actual = suites[0]
    description = (
        "Three independently written Rust, C, and Zig engines passed all "
        "223,198 original and 393 deeper checks. Rust then genuinely ran all "
        "152 original Python methods: 139 passed, 11 failed because the test "
        "harness intercepted its own matching helpers, one exposed a real "
        "missing _compile required for pickling, and one real private-debug "
        "test was skipped. All 304 owner and matcher guards ran. "
        "C and Zig have not run the complete Python suite. Speed is not measured."
    )
    content = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1390" '
        'viewBox="0 0 1200 1390" role="img" aria-labelledby="title description">',
        '<title id="title">How close are we to replacing Python’s re?</title>',
        '<desc id="description">' + html.escape(description) + '</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        "'Segoe UI',sans-serif}.title{font-size:35px;font-weight:760;fill:#10223b}"
        '.subtitle{font-size:16px;fill:#43536b}.metric{font-size:30px;'
        'font-weight:750;fill:#10223b}.metric-label{font-size:13px;fill:#43536b}'
        '.heading{font-size:21px;font-weight:720;fill:#10223b}.body{font-size:'
        '15px;fill:#25364e}.small{font-size:13px;fill:#43536b}.strong{font-size:'
        '16px;font-weight:720;fill:#10223b}.pass{font-size:14px;font-weight:720;'
        'fill:#116139}.warning{font-size:14px;font-weight:720;fill:#8a4b08}'
        '.fail{font-size:14px;font-weight:720;fill:#aa2831}'
        '.pending{font-size:14px;font-weight:720;fill:#485870}.footer{font-size:'
        '15px;font-weight:650;fill:#25364e}</style>',
        '<rect width="1200" height="1390" rx="20" fill="#f5f8fc"/>',
        _text(54, 72, "How close are we to replacing Python’s re?", "title"),
        _text(56, 104,
              "From-scratch Rust, C and Zig · compared with pinned Python 3.14.6",
              "subtitle"),
    ]
    for x, metric, label in (
        (54, "3", "independent matching engines"),
        (338, "669,594", "original candidate-checks"),
        (622, "1,179", "deeper candidate-checks"),
        (906, "0", "original / deeper mismatches"),
    ):
        content.extend((
            f'<rect x="{x}" y="130" width="240" height="92" rx="14" '
            'fill="#ffffff" stroke="#dce5ef"/>',
            _text(x + 15, 173, metric, "metric"),
            _text(x + 15, 199, label, "metric-label"),
        ))
    content.extend((
        _text(56, 263, "Original correctness checks", "heading"),
        _text(56, 286,
              "The same 223,198 original cases for each engine · 49 categories",
              "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 304 + 44 * index
        content.extend((
            _text(67, y + 20, label, "strong"),
            f'<rect x="158" y="{y}" width="685" height="26" rx="7" '
            'fill="#17844e"/>',
            _text(861, y + 19, "223,198 / 223,198", "strong"),
            _text(1071, y + 19, "100%", "pass"),
        ))
    content.extend((
        _text(56, 472, "Deeper correctness checks", "heading"),
        _text(56, 494,
              "The same 393 difficult cases · including 64 fixed-seed cases",
              "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 510 + 44 * index
        content.extend((
            _text(67, y + 20, label, "strong"),
            f'<rect x="158" y="{y}" width="685" height="26" rx="7" '
            'fill="#17844e"/>',
            _text(861, y + 19, "393 / 393", "strong"),
            _text(1071, y + 19, "100%", "pass"),
        ))
    content.extend((
        _text(56, 678, "Actual complete Python compatibility test", "heading"),
        _text(56, 700,
              "Rust really ran all 152 original Python tests. "
              "Its 12 errors have two different causes.", "small"),
        '<rect x="54" y="720" width="1092" height="164" rx="13" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(73, 751, "Rust", "strong"),
        _text(144, 751, "NOT YET COMPATIBLE", "fail"),
    ))
    metrics = (
        (76, "139", "passed"),
        (288, "11", "test-harness interference"),
        (548, "1", "real missing _compile"),
        (824, "1", "genuine debug-only skip"),
    )
    for x, number, label in metrics:
        content.extend((_text(x, 799, number, "metric"),
                        _text(x, 821, label, "metric-label")))
    content.extend((
        _text(73, 858,
              "152 / 152 methods reached · 304 / 304 native-owner checks · "
              "304 / 304 matcher guards", "small"),
        _text(56, 920, "What the 12 errors actually mean", "heading"),
        '<rect x="54" y="937" width="1092" height="92" rx="11" '
        'fill="#fff8eb" stroke="#f2d199"/>',
        _text(72, 966,
              "11 errors: the test harness blocked the regex helpers "
              "used by Python’s warning and assertion checks.", "body"),
        _text(72, 990,
              "These are test-harness interference, not 11 proven matching "
              "incompatibilities.", "small"),
        '<rect x="54" y="1038" width="1092" height="74" rx="11" '
        'fill="#fff1f1" stroke="#ecc6c8"/>',
        _text(72, 1067,
              "1 genuine engine gap: Python’s original pickling test "
              "cannot import the required _compile.", "body"),
        _text(72, 1090,
              "This is a real drop-in compatibility failure that must be fixed.",
              "small"),
    ))
    pending = [row for row in suites if row.get("family") in ("vm", "zig")]
    require(len(pending) == 2,
            "both independent C and Zig full-suite results must stay visible")
    for index, row in enumerate(pending):
        x = (54, 615)[index]
        content.extend((
            f'<rect x="{x}" y="1128" width="530" height="65" rx="11" '
            'fill="#f1f4f9" stroke="#d9e1ec"/>',
            _text(x + 17, 1153, row["label"], "strong"),
            _text(x + 91, 1153, row["status"],
                  "pending" if row["status"] == "NOT RUN" else "warning"),
            _text(x + 17, 1175,
                  "Complete 152-method Python suite not qualified.", "small"),
        ))
    content.extend((
        _text(56, 1232, "Earlier Rust test-harness failures remain preserved",
              "heading"),
        _text(58, 1254,
              "1. Missing bridge wiring · 2. Anti-delegation import guard · "
              "3. Correctness-controller isolation", "small"),
        _text(58, 1275,
              "All three earlier runs stopped before their first Python test. "
              "None is counted as a matching failure.", "small"),
        '<rect x="54" y="1290" width="1092" height="67" rx="11" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(72, 1316,
              "Overall: no engine has yet passed the complete Python "
              "drop-in compatibility checks.", "footer"),
        _text(72, 1339,
              "Speed and memory: NOT MEASURED · final holdout: NOT ACCESSED.",
              "small"),
        '</svg>\n',
    ))
    require(actual.get("passed_methods") == 139
            and actual.get("error_methods") == 12
            and actual.get("harness_interference_errors") == 11
            and actual.get("genuine_candidate_errors") == 1
            and actual.get("named_private_debug_skips") == 1,
            "the chart changed a genuine full-upstream failure denominator")
    return "\n".join(content).encode("utf-8")


def _bundle() -> tuple[bytes, bytes, dict[str, Any]]:
    snapshot, identities = _snapshot()
    chart = render_svg(snapshot)
    manifest = {
        "schema": SCHEMA + "-manifest", "status": "PASS",
        "generator_path": SOURCE_PATH,
        "chart_path": CHART_PATH,
        "chart_sha256": hashlib.sha256(chart).hexdigest(),
        "chart_bytes": len(chart),
        "validated_input_count": len(identities),
        "validated_inputs": identities,
        "snapshot": snapshot,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return chart, canonical(manifest), manifest


def _exclusive_publish(name: str, payload: bytes, directory: int) -> str:
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = os.open(name, flags, 0o644, dir_fd=directory)
    except FileExistsError:
        descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        try:
            require(stat.S_ISREG(os.fstat(descriptor).st_mode),
                    "an existing current output is not a safe regular file")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            require(b"".join(chunks) == payload,
                    "refusing to replace distinct actual correctness results")
        finally:
            os.close(descriptor)
        return "EXISTING IDENTICAL"
    try:
        sent = 0
        while sent < len(payload):
            observed = os.write(descriptor, payload[sent:])
            require(type(observed) is int and observed > 0,
                    "an actual exclusive chart write failed")
            sent += observed
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.fsync(directory)
    return "EXCLUSIVELY CREATED"


def _write(chart: bytes, manifest: bytes) -> dict[str, str]:
    flags = (os.O_RDONLY | os.O_DIRECTORY
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    root = os.open(str(ROOT), flags)
    docs = -1
    evidence = -1
    try:
        docs = os.open("docs", flags, dir_fd=root)
        evidence = os.open("evidence", flags, dir_fd=docs)
        return {
            "chart": _exclusive_publish("current-native-correctness-v4.svg",
                                         chart, evidence),
            "manifest": _exclusive_publish("current-native-correctness-v4.json",
                                            manifest, evidence),
        }
    finally:
        if evidence != -1:
            os.close(evidence)
        if docs != -1:
            os.close(docs)
        os.close(root)


@contextlib.contextmanager
def _source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0, "file_writes": 0, "candidate_imports": 0,
        "workers": 0, "threads": 0, "clock_samples": 0,
        "holdout_cases_read": 0, "performance_fixtures_read": 0,
        "blocked_file_reads": 0, "blocked_file_writes": 0,
        "blocked_candidate_imports": 0, "blocked_workers": 0,
        "blocked_threads": 0, "blocked_clock_samples": 0,
    }
    previous: list[tuple[Any, str, Any]] = []

    def blocker(counter: str, message: str) -> Callable[..., Any]:
        def reject(*_args: Any, **_kwargs: Any) -> Any:
            effects[counter] += 1
            raise ChartError(message)
        return reject

    def patch(target: Any, attribute: str, substitute: Any) -> None:
        if hasattr(target, attribute):
            previous.append((target, attribute, getattr(target, attribute)))
            setattr(target, attribute, substitute)

    deny_read = blocker("blocked_file_reads", "synthetic controls cannot read")
    deny_write = blocker("blocked_file_writes", "synthetic controls cannot write")
    deny_import = blocker("blocked_candidate_imports", "synthetic controls cannot import")
    deny_worker = blocker("blocked_workers", "synthetic controls cannot run")
    deny_thread = blocker("blocked_threads", "synthetic controls cannot start threads")
    deny_clock = blocker("blocked_clock_samples", "synthetic controls cannot measure")
    try:
        patch(builtins, "open", deny_read)
        patch(io, "open", deny_read)
        for field in ("open", "read_bytes", "read_text", "exists", "stat",
                      "is_file", "is_dir", "glob", "rglob", "iterdir"):
            patch(Path, field, deny_read)
        for field in ("open", "stat", "lstat", "listdir", "scandir"):
            patch(os, field, deny_read)
        for field in ("write", "fsync", "mkdir", "makedirs", "unlink",
                      "remove", "rename", "replace"):
            patch(os, field, deny_write)
        patch(Path, "write_bytes", deny_write)
        patch(Path, "write_text", deny_write)
        patch(subprocess, "run", deny_worker)
        patch(subprocess, "Popen", deny_worker)
        patch(os, "fork", deny_worker)
        patch(multiprocessing.Process, "start", deny_worker)
        patch(threading.Thread, "start", deny_thread)
        for field in ("time", "time_ns", "monotonic", "monotonic_ns",
                      "perf_counter", "perf_counter_ns", "process_time",
                      "process_time_ns", "thread_time", "thread_time_ns"):
            patch(time, field, deny_clock)
        patch(importlib, "import_module", deny_import)
        patch(builtins, "__import__", deny_import)
        yield effects
    finally:
        for target, attribute, saved in reversed(previous):
            setattr(target, attribute, saved)


def _synthetic_snapshot() -> dict[str, Any]:
    records = [{"family": family, "label": label, "kind": kind,
                "status": "PASS", "passed": count, "total": count,
                "mismatches": 0}
               for kind, count in (("original", 223_198), ("deeper", 393))
               for family, label in FAMILIES]
    interference = [
        {"test": "synthetic_warning_" + str(index),
         "reason_sha256": hashlib.sha256(str(index).encode("ascii")).hexdigest()}
        for index in range(11)
    ]
    candidate = [{
        "test": PICKLING_METHOD,
        "reason_sha256": hashlib.sha256(PICKLING_ERROR.encode("ascii")).hexdigest(),
    }]
    rust = {
        "family": "rust", "label": "Rust", "status": "FAIL",
        "completed_methods": PUBLIC_METHODS, "total_methods": PUBLIC_METHODS,
        "passed_methods": 139, "error_methods": 12,
        "harness_interference_errors": 11, "genuine_candidate_errors": 1,
        "named_private_debug_skips": 1,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "full_official_suite_qualified": False,
        "harness_interference_error_records": interference,
        "genuine_candidate_error_records": candidate,
        "genuine_candidate_error_test": PICKLING_METHOD,
        "genuine_candidate_error": PICKLING_ERROR,
    }
    other = [
        {"family": name, "label": label, "status": "NOT RUN",
         "completed_methods": None, "total_methods": PUBLIC_METHODS,
         "native_owner_guards": None, "cached_matcher_guards": None,
         "full_official_suite_qualified": False}
        for name, label in FAMILIES[1:]
    ]
    return {
        "candidate_count": 3, "original_candidate_checks": 669_594,
        "deeper_candidate_checks": 1_179,
        "observed_original_or_deeper_mismatches": 0, "rows": records,
        "historical_v12_rust_upstream_failure": {
            "family": "rust", "status": "STOPPED BEFORE TESTS",
            "completed_methods": 0, "cause": "test-harness bridge wiring",
        },
        "historical_v13_rust_upstream_failure": {
            "family": "rust", "status": "FAIL", "completed_methods": 0,
            "native_owner_guards": 0,
            "actual_error": "stage-07 blocked unowned matching import: re",
        },
        "historical_v14_rust_upstream_failure": {
            "family": "rust", "status": "FAIL", "completed_methods": 0,
            "native_owner_guards": 0,
            "actual_error": "the V11 correctness controller must never import a candidate",
        },
        "full_python_suite": [rust, *other],
        "official_suite_candidate_passes": 0,
        "full_drop_in_compatibility": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def _self_test() -> dict[str, Any]:
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "visualization source controls cannot load matching engines")
    accepted = 0
    rejected = 0

    def reject(action: Callable[[], Any], description: str) -> None:
        nonlocal rejected
        try:
            action()
        except (ChartError, OSError, TypeError, ValueError, KeyError, ImportError):
            rejected += 1
        else:
            raise ChartError("accepted a fabricated source control: " + description)

    with _source_only_boundary() as effects:
        correct = _synthetic_snapshot()
        picture = render_svg(correct)
        require(picture == render_svg(copy.deepcopy(correct))
                and picture.startswith(b"<svg ")
                and picture.endswith(b"</svg>\n")
                and picture.count(b"223,198 / 223,198") == 3
                and picture.count(b"393 / 393") == 3
                and b"139" in picture and b"11" in picture
                and b"real missing _compile" in picture
                and b"test-harness interference" in picture
                and b"304 / 304 native-owner checks" in picture
                and picture.count(b">NOT RUN</text>") == 2
                and b"Missing bridge wiring" in picture
                and b"Anti-delegation import guard" in picture
                and b"Correctness-controller isolation" in picture
                and b"NOT MEASURED" in picture
                and b"NOT ACCESSED" in picture,
                "the exact 139/11/1/1 truthful synthetic chart was changed")
        accepted += 14
        for key, false in (
            ("candidate_count", 2),
            ("original_candidate_checks", 669_593),
            ("deeper_candidate_checks", 1_178),
            ("observed_original_or_deeper_mismatches", 1),
            ("official_suite_candidate_passes", 1),
            ("full_drop_in_compatibility", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "ACCESSED"),
        ):
            broken = copy.deepcopy(correct)
            broken[key] = false
            reject(lambda broken=broken: render_svg(broken), key)
        for index in range(6):
            for field, false in (("status", "FAIL"), ("mismatches", 1),
                                 ("passed", correct["rows"][index]["total"] - 1)):
                broken = copy.deepcopy(correct)
                broken["rows"][index][field] = false
                reject(lambda broken=broken: render_svg(broken),
                       "concealed original/deeper mismatch")
        for field, false in (
            ("passed_methods", 140),
            ("passed_methods", 151),
            ("passed_methods", 152),
            ("error_methods", 11),
            ("error_methods", 13),
            ("harness_interference_errors", 10),
            ("harness_interference_errors", 12),
            ("genuine_candidate_errors", 0),
            ("genuine_candidate_errors", 2),
            ("named_private_debug_skips", 0),
            ("named_private_debug_skips", 2),
            ("native_owner_guards", 303),
            ("cached_matcher_guards", 303),
            ("completed_methods", 151),
            ("total_methods", 151),
            ("full_official_suite_qualified", True),
            ("genuine_candidate_error_test", "invented matching failure"),
            ("genuine_candidate_error", "invented matching failure"),
        ):
            broken = copy.deepcopy(correct)
            broken["full_python_suite"][0][field] = false
            reject(lambda broken=broken: render_svg(broken),
                   "altered actual 139/11/1/1: " + field)
        for collection in ("harness_interference_error_records",
                           "genuine_candidate_error_records"):
            broken = copy.deepcopy(correct)
            broken["full_python_suite"][0][collection].pop()
            reject(lambda broken=broken: render_svg(broken),
                   "suppressed original failure classification")
        broken = copy.deepcopy(correct)
        broken["full_python_suite"][0]["genuine_candidate_error_records"][0]["test"] = (
            "ReTests.test_matching"
        )
        reject(lambda: render_svg(broken), "called a harness error a matching failure")
        for index in (1, 2):
            for field, false in (("status", "PASS"),
                                 ("completed_methods", PUBLIC_METHODS),
                                 ("native_owner_guards", METHOD_GUARDS),
                                 ("full_official_suite_qualified", True)):
                changed = copy.deepcopy(correct)
                changed["full_python_suite"][index][field] = false
                reject(lambda changed=changed: render_svg(changed),
                       "invented unexecuted independent engine")
        for stage in ("historical_v12_rust_upstream_failure",
                      "historical_v13_rust_upstream_failure",
                      "historical_v14_rust_upstream_failure"):
            for field, false in (("status", "PASS"), ("completed_methods", 152)):
                changed = copy.deepcopy(correct)
                changed[stage][field] = false
                reject(lambda changed=changed: render_svg(changed),
                       "suppressed actual zero-test setup failure")
        reject(lambda: builtins.open(RUST_V15_FAILURE_PATH, "rb"),
               "read the real 17-megabyte frozen failure")
        reject(lambda: os.open(RESOURCE_PATH, os.O_RDONLY),
               "open actual root-owned resource observations")
        reject(lambda: (ROOT / V15_SOURCE_PATH).read_bytes(),
               "read the actual frozen upstream controller")
        reject(lambda: (ROOT / "performance").exists(),
               "touch a benchmark or the holdout")
        reject(lambda: importlib.import_module("candidates.rust_candidate"),
               "import a matching candidate")
        reject(lambda: builtins.__import__("candidates.zig_candidate"),
               "builtin-import another matching candidate")
        reject(lambda: subprocess.run(["production-worker"]),
               "run a genuine candidate worker")
        reject(lambda: threading.Thread(target=lambda: None).start(),
               "start a background worker")
        reject(time.perf_counter, "measure a performance clock")
        reject(lambda: (ROOT / CHART_PATH).write_bytes(b"forged"),
               "create an unauthorized synthetic chart")
        require(all(effects[key] == 0 for key in (
            "file_reads", "file_writes", "candidate_imports", "workers",
            "threads", "clock_samples", "holdout_cases_read",
            "performance_fixtures_read",
        )), "source-only visualization controls caused actual production effects")
        require(effects["blocked_file_reads"] >= 4
                and effects["blocked_file_writes"] >= 1
                and effects["blocked_candidate_imports"] >= 2
                and effects["blocked_workers"] >= 1
                and effects["blocked_threads"] >= 1
                and effects["blocked_clock_samples"] >= 1,
                "genuine synthetic-source isolation did not reject unsafe actions")
        observed = dict(effects)
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "synthetic_only": True,
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "total_controls": accepted + rejected,
        "actual_v15_failure_reads": 0,
        "actual_candidates_qualified": 0,
        "frozen_v3_source_sha256": V3_SOURCE_SHA256,
        "frozen_v15_source_sha256": V15_SOURCE_SHA256,
        "frozen_v15_protocol_sha256": V15_PROTOCOL_SHA256,
        "effects": observed,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Visualize the actual frozen original Python regex outcomes."
    )
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--self-test", action="store_true")
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--write", action="store_true")
    selected = parser.parse_args(arguments)
    try:
        if selected.self_test:
            result = _self_test()
        else:
            picture, manifest, document = _bundle()
            if selected.write:
                publication = _write(picture, manifest)
            else:
                require(_read_regular(CHART_PATH) == picture
                        and _read_regular(MANIFEST_PATH) == manifest,
                        "the frozen V4 chart cannot be exactly regenerated")
                publication = {"chart": "VERIFIED", "manifest": "VERIFIED"}
            result = {
                "schema": SCHEMA + ("-write" if selected.write else "-check"),
                "status": "PASS", "chart_path": CHART_PATH,
                "chart_sha256": document["chart_sha256"],
                "manifest_path": MANIFEST_PATH,
                "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
                "validated_input_count": document["validated_input_count"],
                "actual_original_upstream_status": document["snapshot"][
                    "full_python_suite"
                ][0]["status"],
                "publication": publication,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            }
    except (ChartError, AssertionError, OSError, ValueError,
            TypeError, KeyError, MemoryError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-failure", "status": "FAIL",
            "actual_error_type": type(error).__name__, "reason": str(error),
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
              file=sys.stderr)
        return 2
    print(canonical(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
