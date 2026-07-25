#!/usr/bin/env python3
"""Show the independently verified progress toward replacing Python's re."""

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
SCHEMA = "rebar-current-native-correctness-v6"
SOURCE_PATH = "tools/render_current_correctness_v6.py"
CHART_PATH = "docs/evidence/current-native-correctness-v6.svg"
MANIFEST_PATH = "docs/evidence/current-native-correctness-v6.json"

V5_SOURCE_PATH = "tools/render_current_correctness_v5.py"
V5_SOURCE_SHA256 = (
    "2c5bf47ca620d95c3e390a5bd882ee69f41d93cfce7dbdbdded60b435fba9d5c"
)
V5_MANIFEST_PATH = "docs/evidence/current-native-correctness-v5.json"
V5_MANIFEST_SHA256 = (
    "60ef85b37d552af65c8bbe588b38969a51078e74e9b15d9407244cd67c794cab"
)
V16_SOURCE_PATH = "tools/postfinal_cpython_locale_oracle_v16.py"
V16_SOURCE_SHA256 = (
    "aebd9f12728ded830256daefcc52ed4531882598f70c41ac95108f0f322d5d66"
)
V16_PROTOCOL_PATH = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V16.md"
V16_PROTOCOL_SHA256 = (
    "88d6c8491bd910a1525125fe68af98fbaa9b71ddffaa3b7ce9539fd9a312376a"
)
REFERENCE_PATH = "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
REFERENCE_SHA256 = (
    "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
)
METHOD_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
RUST_V16_FAILURE_PATH = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v16-rust-failures.json"
)
RUST_V16_FAILURE_SHA256 = (
    "64220920e6fe852bc769205503776ccb73e27301e8decc847b2727a6e6454a91"
)
RUST_V16_FAILURE_BYTES = 17_298_371
RUST_V16_WORKER_STDOUT_BYTES = 3_464_448
RUST_V16_WORKER_STDOUT_SHA256 = (
    "c3d83fc4d08b7d3cf440801996647c00be757369566930f55dff679e52062015"
)
V16_RESOURCE_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v16-rust-resource-preflight.json"
)
V16_RESOURCE_SHA256 = (
    "7f46a9f543cdf80b93984c2017b29474de031b239751588b64051d5f8d949c79"
)
V16_FORENSIC_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v16-rust-readonly-failure-forensic.json"
)
V16_FORENSIC_SHA256 = (
    "9cf9d98499d980db42368d7e508c68001da9e4020437976bb9216aa384e5f845"
)
V16_PRODUCTION_SUMMARY_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v16-rust-failures-production-summary.json"
)
V16_PRODUCTION_SUMMARY_SHA256 = (
    "0ab38d67769888093e2988c1551b4719f28f9f724b421d3b1be83016a6cc45a4"
)

ALL_ORIGINAL_METHODS = 165
PUBLIC_METHODS = 152
PRIVATE_WAIVER_CLASSES = 2
PRIVATE_WAIVER_METHODS = 13
RUNNABLE_REFERENCE_METHODS = 151
METHOD_GUARDS = 304
ORIGINAL_CASES_PER_FAMILY = 223_198
DEEP_CASES_PER_FAMILY = 393
FAMILIES = (("rust", "Rust"), ("vm", "C"), ("zig", "Zig"))
NAMED_PRIVATE_CLASS_WAIVERS = {
    "DebugTests": {
        "methods": 4,
        "reason": "CPython-only textual disassembly of private matching opcodes",
    },
    "ImplementationTest": {
        "methods": 9,
        "reason": (
            "private CPython regex compiler, _sre, type internals, and "
            "deprecated private implementation modules"
        ),
    },
}
PRIVATE_DEBUG_METHOD = "ReTests.test_memory_leaks"
PRIVATE_DEBUG_REASON = "requires debug build"
PRIVATE_DEBUG_SKIP_KIND = "named-private-debug-condition"
PRIVATE_DEBUG_SOURCE_AST_SHA256 = (
    "840264aaf4bf27c06d29ac78664767327a8f4b90008c5db994c88542c692b389"
)
PICKLING_METHOD = "ReTests.test_pickling"
PICKLING_ERROR = "cannot import name '_compile' from 'candidates.rust_candidate'"
PICKLING_SOURCE_AST_SHA256 = (
    "67cff16be2924b023b058b55a2eedc56131e7261f78410ff59ccf3ecba7ef3c0"
)
PICKLING_REASON_SHA256 = (
    "934616163a04e76cf83532a94b397d571fb1e0679772a88ae6b3b236131e2a6e"
)
PICKLING_REASON_CHARACTERS = 359
HARNESS_ERROR_MARKER = "stage07_blocked_regex"
MAX_INPUT_BYTES = 128 * 1024 * 1024
NOT_PRESERVED = "NOT PRESERVED"


class ChartError(Exception):
    """A real compatibility result was missing, changed, or overstated."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ChartError(message)


def canonical(document: Any) -> bytes:
    return (
        json.dumps(
            document, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def _valid_sha256(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _read_regular(relative: str) -> bytes:
    require(
        type(relative) is str and bool(relative) and "\\" not in relative,
        "only an exact frozen relative correctness input may be read",
    )
    target = Path(relative)
    require(
        not target.is_absolute() and ".." not in target.parts,
        "a frozen correctness input escaped the repository",
    )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(str(ROOT / target), flags)
    try:
        information = os.fstat(descriptor)
        require(
            stat.S_ISREG(information.st_mode)
            and 0 < information.st_size <= MAX_INPUT_BYTES,
            "a frozen correctness input is not a bounded regular file",
        )
        parts: list[bytes] = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            parts.append(block)
        result = b"".join(parts)
        require(
            len(result) == information.st_size,
            "an actual frozen correctness input changed during its read",
        )
        return result
    finally:
        os.close(descriptor)


def _checked_json(
    relative: str, expected: str, expected_bytes: int | None = None,
) -> dict[str, Any]:
    require(_valid_sha256(expected), "an actual frozen evidence hash is required")
    raw = _read_regular(relative)
    require(
        hashlib.sha256(raw).hexdigest() == expected
        and (expected_bytes is None or len(raw) == expected_bytes),
        "an actual frozen correctness artifact was changed: " + relative,
    )
    try:
        document = json.loads(raw)
    except (UnicodeError, ValueError) as error:
        raise ChartError("an actual frozen correctness input is not JSON") from error
    require(type(document) is dict, "actual correctness evidence is not an object")
    canonical_document = canonical(document)
    require(
        raw == canonical_document or raw == canonical_document[:-1],
        "a frozen correctness artifact is not exactly canonical: " + relative,
    )
    return document


def _frozen_module(relative: str, expected: str, name: str) -> types.ModuleType:
    require(_valid_sha256(expected), "an exact frozen controller hash is required")
    source = _read_regular(relative)
    require(
        hashlib.sha256(source).hexdigest() == expected,
        "an independently frozen correctness controller changed: " + relative,
    )
    result = types.ModuleType(name)
    result.__file__ = str(ROOT / relative)
    exec(compile(source, result.__file__, "exec", dont_inherit=True), result.__dict__)
    return result


def _validate_resource(resource: dict[str, Any]) -> None:
    require(
        resource.get("schema")
        == "rebar-root-v16-genuine-upstream-resource-preflight"
        and resource.get("status") == "PASS"
        and resource.get("role") == "rust"
        and resource.get("source_sha256") == V16_SOURCE_SHA256
        and resource.get("protocol_sha256") == V16_PROTOCOL_SHA256
        and resource.get("configured_original_memory_bytes") == 40 * 1024**3
        and resource.get("required_large_substitution_memory_bytes") == 18 * 2**31
        and resource.get("minimum_additional_safety_reserve_bytes") == 8 * 1024**3
        and type(resource.get("effective_available_memory_bytes")) is int
        and resource["effective_available_memory_bytes"]
        >= resource["required_large_substitution_memory_bytes"]
        + resource["minimum_additional_safety_reserve_bytes"]
        and resource.get("cpu_resource_enabled") is True
        and resource.get("fork_available") is True
        and resource.get("multiprocessing_extension_available") is True
        and resource.get("actual_fork_process_exited_cleanly") is True
        and resource.get("actual_single_memory_worker_lock_available") is True
        and resource.get("actual_candidate_workers") == 0
        and resource.get("actual_reference_workers") == 0
        and resource.get("candidate_imports") == 0
        and resource.get("performance") == "NOT MEASURED"
        and resource.get("holdout") == "NOT ACCESSED",
        "the real V16 original-test memory or isolation preflight changed",
    )
    locales = resource.get("actual_fresh_private_locales")
    require(
        type(locales) is dict
        and locales.get("fresh_private_localedef") is True
        and locales.get("iso_8859_1_passed") is True
        and locales.get("utf_8_passed") is True,
        "the two genuine private original-test locales were not verified",
    )


def _validate_v16_failure(
    report: dict[str, Any], *, frozen: Any,
    previous: dict[str, Any], v2: Any, v1: Any,
) -> dict[str, Any]:
    require(
        report.get("schema")
        == "rebar-postfinal-cpython-full-public-locale-v16-actual-role-failure"
        and report.get("status") == "FAIL"
        and report.get("role") == "rust"
        and report.get("source_sha256") == V16_SOURCE_SHA256
        and report.get("protocol_sha256") == V16_PROTOCOL_SHA256
        and report.get("immutable_v6_reference_sha256") == REFERENCE_SHA256
        and report.get("actual_failure_destination") == RUST_V16_FAILURE_PATH
        and report.get("synthetic") is False
        and report.get("production_observations_invented") is False
        and report.get("performance") == "NOT MEASURED"
        and report.get("holdout") == "NOT ACCESSED",
        "the frozen full original V16 Rust failure was changed or overstated",
    )
    details = report.get("details")
    require(
        type(details) is dict
        and details.get("returncode") == 2
        and details.get("signal") is None
        and details.get("complete_streams_available") is True
        and details.get("actual_native_owner_method_guard_checks") == METHOD_GUARDS
        and details.get("actual_completed_candidate_roles") == {}
        and details.get("actual_fully_durable_role_publications") == []
        and details.get("production_observations_invented") is False,
        "the actual complete isolated candidate-worker result was substituted",
    )
    stdout = details.get("stdout")
    stderr = details.get("stderr")
    require(
        type(stdout) is dict
        and stdout.get("encoding") == "hex"
        and stdout.get("bytes") == RUST_V16_WORKER_STDOUT_BYTES
        and stdout.get("sha256") == RUST_V16_WORKER_STDOUT_SHA256
        and stdout.get("truncated") is False
        and type(stdout.get("complete_hex")) is str
        and type(stderr) is dict
        and stderr.get("encoding") == "hex"
        and stderr.get("bytes") == 0
        and stderr.get("sha256") == hashlib.sha256(b"").hexdigest()
        and stderr.get("truncated") is False
        and stderr.get("complete_hex") == "",
        "the preserved inner candidate-worker streams are incomplete or changed",
    )
    try:
        complete_stdout = bytes.fromhex(stdout["complete_hex"])
        observed_worker = json.loads(complete_stdout)
    except (UnicodeError, ValueError) as error:
        raise ChartError("the genuine complete inner worker stdout is invalid") from error
    require(
        len(complete_stdout) == RUST_V16_WORKER_STDOUT_BYTES
        and hashlib.sha256(complete_stdout).hexdigest()
        == RUST_V16_WORKER_STDOUT_SHA256
        and type(observed_worker) is dict
        and complete_stdout == frozen.canonical(observed_worker) + b"\n"
        and observed_worker == details.get("actual_worker_document")
        and observed_worker.get("schema") == frozen.SCHEMA + "-actual-worker-failure"
        and observed_worker.get("status") == "FAIL"
        and observed_worker.get("role") == "rust"
        and observed_worker.get("production_observations_invented") is False
        and observed_worker.get("performance") == "NOT MEASURED"
        and observed_worker.get("holdout") == "NOT ACCESSED",
        "the actual inner original-suite worker was truncated or fabricated",
    )
    worker = details.get("actual_worker_failure_details")
    require(
        type(worker) is dict
        and observed_worker.get("details") == worker
        and worker.get("completed_original_method_count") == PUBLIC_METHODS
        and worker.get("actual_native_owner_method_guard_checks") == METHOD_GUARDS
        and worker.get("actual_cached_matcher_method_guard_checks") == METHOD_GUARDS
        and worker.get("production_observations_invented") is False
        and worker.get("performance") == "NOT MEASURED"
        and worker.get("holdout") == "NOT ACCESSED",
        "the complete original 152-method, 304/304-guard trace was omitted",
    )
    records = worker.get("completed_original_method_records")
    require(
        type(records) is list and len(records) == PUBLIC_METHODS,
        "an original Python method was omitted from the actual V16 worker",
    )
    reference = _checked_json(REFERENCE_PATH, REFERENCE_SHA256)
    matrix = v2._validate_matrix(reference, frozen, v1)
    baseline = reference["roles"]["reference_a"]["records"]
    passed = 0
    debug_skips = 0
    genuine_errors: list[dict[str, Any]] = []
    for expected, actual in zip(baseline, records, strict=True):
        require(
            type(actual) is dict
            and actual.get("test") == expected.get("test")
            and actual.get("source_ast_sha256")
            == expected.get("source_ast_sha256"),
            "an executed original Python method changed its source or order",
        )
        state = actual.get("status")
        if state == "PASS":
            require(
                expected.get("status") == "PASS",
                "a debug-only original baseline skip was relabeled as a pass",
            )
            passed += 1
        elif state == "SKIP":
            require(
                expected.get("status") == "SKIP"
                and actual.get("test") == PRIVATE_DEBUG_METHOD
                and actual.get("reason") == PRIVATE_DEBUG_REASON
                and actual.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                and actual.get("source_ast_sha256")
                == PRIVATE_DEBUG_SOURCE_AST_SHA256,
                "the one authentic in-scope debug-build skip was fabricated",
            )
            debug_skips += 1
        elif state == "ERROR":
            reason = actual.get("reason")
            require(
                expected.get("status") == "PASS"
                and actual.get("test") == PICKLING_METHOD
                and actual.get("source_ast_sha256")
                == PICKLING_SOURCE_AST_SHA256
                and type(reason) is str
                and PICKLING_ERROR in reason
                and HARNESS_ERROR_MARKER not in reason
                and len(reason) == PICKLING_REASON_CHARACTERS
                and hashlib.sha256(reason.encode("utf-8")).hexdigest()
                == PICKLING_REASON_SHA256,
                "an unexplained error or test-harness failure was hidden",
            )
            genuine_errors.append({
                "test": actual["test"],
                "classification": "from-scratch Rust private pickle hook missing",
                "reason_sha256": PICKLING_REASON_SHA256,
                "complete_reason_characters": PICKLING_REASON_CHARACTERS,
                "source_ast_sha256": PICKLING_SOURCE_AST_SHA256,
            })
        else:
            raise ChartError("an original Python method status was weakened")
    require(
        passed == 150 and len(genuine_errors) == 1 and debug_skips == 1
        and passed + len(genuine_errors) + debug_skips == PUBLIC_METHODS,
        "the real 150-pass, one-gap, one-debug-skip result was misrepresented",
    )
    original_rows = previous.get("rows")
    require(type(original_rows) is list, "the original owner evidence was omitted")
    edge = next(
        (
            row for row in original_rows
            if row.get("family") == "rust" and row.get("kind") == "original"
        ),
        None,
    )
    require(
        type(edge) is dict
        and type(edge.get("proof_path")) is str
        and _valid_sha256(edge.get("proof_sha256")),
        "the independently verified from-scratch Rust owner proof is missing",
    )
    # This already-frozen V24 historical proof is pretty-printed, not a new
    # canonical V16 artifact; reauthenticate it with its frozen V1 validator.
    edge_proof = v1._checked_json(edge["proof_path"], edge["proof_sha256"])
    expected_native = edge_proof.get("full_current_family_native_elf_sha256")
    require(
        type(expected_native) is dict and bool(expected_native),
        "the genuine same-family native matching binaries were substituted",
    )

    def verify_owner(owner: Any, family: str, expected: Any) -> dict[str, Any]:
        require(
            family == "rust" and expected == expected_native,
            "an original method borrowed another candidate's matching engine",
        )
        v1._validate_owner(owner, "rust", "candidates.rust_candidate")
        require(
            owner.get("native_binary_sha256") == expected_native
            and owner.get("schema")
            == "rebar-postfinal-from-scratch-audit-v10-native-owner-worker"
            and owner.get("match_repr_checks") == 2
            and owner.get("persistent_cross_engine_guard") is True,
            "an original method lost its genuine independently owned engine",
        )
        return owner

    frozen._validate_native_method_trace(
        "rust", matrix, worker.get("actual_completed_native_method_owners"),
        expected_native, verify_owner,
    )
    return {
        "family": "rust",
        "label": "Rust",
        "status": "FAIL",
        "completed_methods": PUBLIC_METHODS,
        "total_methods": PUBLIC_METHODS,
        "passed_methods": passed,
        "error_methods": 1,
        "harness_interference_errors": 0,
        "harness_interference_error_records": [],
        "genuine_candidate_errors": 1,
        "genuine_candidate_error_records": genuine_errors,
        "genuine_candidate_error_test": PICKLING_METHOD,
        "genuine_candidate_error": PICKLING_ERROR,
        "named_private_debug_skips": debug_skips,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "full_official_suite_qualified": False,
        "failure_path": RUST_V16_FAILURE_PATH,
        "failure_sha256": RUST_V16_FAILURE_SHA256,
        "failure_bytes": RUST_V16_FAILURE_BYTES,
        "actual_inner_worker_returncode": 2,
        "actual_complete_inner_worker_stdout_bytes": RUST_V16_WORKER_STDOUT_BYTES,
        "actual_complete_inner_worker_stdout_sha256": RUST_V16_WORKER_STDOUT_SHA256,
        "outer_controller_stderr": NOT_PRESERVED,
        "outer_controller_publication_receipt": NOT_PRESERVED,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _zero_boundary_effects(effects: Any) -> bool:
    return (
        type(effects) is dict
        and set(effects) == {
            "native_workers_started", "subprocesses_started", "candidate_imports",
            "filesystem_writes", "clock_samples",
        }
        and all(type(value) is int and value == 0 for value in effects.values())
    )


def _validate_forensic_and_summary(
    forensic: dict[str, Any], summary: dict[str, Any], current: dict[str, Any],
) -> None:
    for label, document in (("forensic", forensic), ("summary", summary)):
        require(
            type(document) is dict
            and document.get("role") == "rust"
            and document.get("source_sha256") == V16_SOURCE_SHA256
            and document.get("protocol_sha256") == V16_PROTOCOL_SHA256
            and document.get("immutable_v6_reference_sha256") == REFERENCE_SHA256
            and document.get("python") == "3.14.6"
            and document.get("original_method_count") == ALL_ORIGINAL_METHODS
            and document.get("public_method_count") == PUBLIC_METHODS
            and document.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
            and document.get("named_private_waiver_method_count")
            == PRIVATE_WAIVER_METHODS
            and document.get("named_private_class_waivers")
            == NAMED_PRIVATE_CLASS_WAIVERS
            and document.get("public_method_waivers") == []
            and document.get("actual_failure_path") == RUST_V16_FAILURE_PATH
            and document.get("actual_failure_sha256") == RUST_V16_FAILURE_SHA256
            and document.get("actual_failure_bytes") == RUST_V16_FAILURE_BYTES
            and document.get("actual_original_method_denominator") == PUBLIC_METHODS
            and document.get("actual_original_methods_completed") == PUBLIC_METHODS
            and document.get("actual_passing_original_methods") == 150
            and document.get("actual_error_original_methods") == 1
            and document.get("actual_harness_interference_errors") == 0
            and document.get("actual_required_original_test_candidate_gaps") == 1
            and document.get("actual_named_private_debug_skips") == 1
            and document.get("authentic_named_private_debug_skip_kind")
            == PRIVATE_DEBUG_SKIP_KIND
            and document.get("actual_native_owner_method_guard_checks")
            == METHOD_GUARDS
            and document.get("actual_cached_matcher_method_guard_checks")
            == METHOD_GUARDS
            and document.get("actual_original_worker_returncode") == 2
            and document.get("actual_complete_original_worker_stdout_bytes")
            == RUST_V16_WORKER_STDOUT_BYTES
            and document.get("actual_complete_original_worker_stdout_sha256")
            == RUST_V16_WORKER_STDOUT_SHA256
            and document.get(
                "actual_complete_original_worker_stdout_preserved_inside_failure"
            ) is True
            and document.get("actual_complete_original_worker_stderr_bytes") == 0
            and document.get("actual_complete_original_worker_stderr_sha256")
            == hashlib.sha256(b"").hexdigest()
            and document.get("actual_controller_complete_outer_stream_preserved")
            is False
            and document.get(
                "actual_controller_durable_publication_receipt_preserved"
            ) is False
            and "actual_controller_returncode" not in document
            and "actual_failure_publication_receipt" not in document
            and "actual_exclusive_publication_receipt" not in document
            and document.get("actual_current_independent_family_count") == 3
            and document.get("actual_current_owned_source_count") == 12
            and document.get("actual_current_owned_native_binary_count") == 5
            and document.get("audit_source_sha256")
            == "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
            and document.get("audit_protocol_sha256")
            == "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
            and document.get("actual_v21_base_report_sha256")
            == "4c1de720abb53a5baee56c36a09039e48137e83b2db103cb0d6e77866b496ce4"
            and document.get("actual_v21_strict_report_sha256")
            == "6e742e2e10cde837cb4c39ffe6d1ab12634d672924e109a727e9a558ad22194d"
            and document.get("preserved_v15_actual_failure_sha256")
            == "fcd83830b36afd94dee6b926764a6300eaf048d5fa81404563d7e8afea2482c2"
            and document.get("preserved_v15_actual_pass_count") == 139
            and document.get("preserved_v15_actual_error_count") == 12
            and document.get("preserved_v15_actual_skip_count") == 1
            and document.get("resource_preflight_path") == V16_RESOURCE_PATH
            and document.get("resource_preflight_sha256") == V16_RESOURCE_SHA256
            and document.get("complete_canonical_failure_document_preserved") is True
            and document.get("full_original_suite_candidate_qualified") is False
            and document.get("production_observations_invented") is False
            and document.get("performance") == "NOT MEASURED"
            and document.get("holdout") == "NOT ACCESSED",
            "the actual root-authenticated V16 original observation changed: "
            + label,
        )
    require(
        forensic.get("schema")
        == "rebar-root-v16-genuine-rust-original-suite-read-only-failure-forensic"
        and forensic.get("status") == "PASS"
        and forensic.get("actual_candidate_result") == "FAIL"
        and forensic.get("historical_failure_qualifies_current_engine") is False
        and _zero_boundary_effects(forensic.get("read_only_boundary_effects")),
        "the independently observed genuine read-only V16 forensic was changed",
    )
    require(
        summary.get("schema")
        == "rebar-root-v16-rust-actual-complete-original-suite-production-summary"
        and summary.get("status") == "FAIL"
        and summary.get("summary_provenance")
        == (
            "Independently reconstructed from the complete preserved candidate "
            "failure; the outer controller stream and durable publication "
            "receipt were not preserved."
        ),
        "the actual completed V16 original-suite production summary was changed",
    )
    observations = forensic.get("actual_nonpassing_original_methods")
    require(
        type(observations) is list and len(observations) == 1
        and summary.get("actual_nonpassing_original_methods") == observations,
        "the sole actual missing Rust pickling requirement was hidden or repeated",
    )
    observation = observations[0]
    expected = current["genuine_candidate_error_records"][0]
    require(
        type(observation) is dict
        and set(observation) == {
            "test", "classification", "complete_reason_sha256",
            "source_ast_sha256",
        }
        and observation.get("test") == PICKLING_METHOD
        and observation.get("classification") == expected["classification"]
        and observation.get("complete_reason_sha256") == PICKLING_REASON_SHA256
        and observation.get("source_ast_sha256") == PICKLING_SOURCE_AST_SHA256,
        "the one authentic complete original pickling failure was misclassified",
    )


def _snapshot() -> tuple[dict[str, Any], list[dict[str, str]]]:
    require(
        _valid_sha256(V16_FORENSIC_SHA256)
        and _valid_sha256(V16_PRODUCTION_SUMMARY_SHA256),
        "BLOCKED: independently publish and freeze both actual V16 forensic pins",
    )
    legacy = _frozen_module(
        V5_SOURCE_PATH, V5_SOURCE_SHA256, "_rebar_frozen_current_correctness_v5",
    )
    frozen = _frozen_module(
        V16_SOURCE_PATH, V16_SOURCE_SHA256, "_rebar_frozen_original_correctness_v16",
    )
    protocol = _read_regular(V16_PROTOCOL_PATH)
    require(
        hashlib.sha256(protocol).hexdigest() == V16_PROTOCOL_SHA256
        and legacy.SCHEMA == "rebar-current-native-correctness-v5"
        and legacy.SOURCE_PATH == V5_SOURCE_PATH
        and legacy.REFERENCE_PATH == REFERENCE_PATH
        and legacy.REFERENCE_SHA256 == REFERENCE_SHA256
        and legacy.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
        and frozen.SCHEMA == "rebar-postfinal-cpython-full-public-locale-v16"
        and frozen.SOURCE_RELATIVE == V16_SOURCE_PATH
        and frozen.PROTOCOL_RELATIVE == V16_PROTOCOL_PATH
        and frozen.PROTOCOL_SHA256 == V16_PROTOCOL_SHA256
        and frozen.V6_REFERENCE_SHA256 == REFERENCE_SHA256
        and frozen.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
        and tuple(frozen.FAMILIES) == tuple(family for family, _ in FAMILIES),
        "a frozen baseline, original-suite controller, or protocol was replaced",
    )
    previous, inherited = legacy._snapshot()
    legacy._validate_snapshot(previous)
    require(
        len(inherited) == 40
        and len({entry["path"] for entry in inherited}) == 40,
        "the genuine 40-input prior all-history correctness proof changed",
    )
    prior_manifest = _checked_json(V5_MANIFEST_PATH, V5_MANIFEST_SHA256)
    prior_chart = legacy.render_svg(previous)
    require(
        prior_manifest.get("schema") == "rebar-current-native-correctness-v5-manifest"
        and prior_manifest.get("status") == "PASS"
        and prior_manifest.get("generator_path") == V5_SOURCE_PATH
        and prior_manifest.get("chart_path")
        == "docs/evidence/current-native-correctness-v5.svg"
        and prior_manifest.get("chart_bytes") == len(prior_chart)
        and prior_manifest.get("chart_sha256")
        == hashlib.sha256(prior_chart).hexdigest()
        and prior_manifest.get("validated_input_count") == 40
        and prior_manifest.get("validated_inputs") == inherited
        and prior_manifest.get("snapshot") == previous
        and prior_manifest.get("production_observations_invented") is False
        and prior_manifest.get("performance") == "NOT MEASURED"
        and prior_manifest.get("holdout") == "NOT ACCESSED",
        "the genuine prior V5 chart, complete 40-input manifest, or history changed",
    )
    prior_rust = previous["full_python_suite"][0]
    require(
        prior_rust.get("passed_methods") == 139
        and prior_rust.get("harness_interference_errors") == 11
        and prior_rust.get("genuine_candidate_errors") == 1
        and prior_rust.get("named_private_debug_skips") == 1
        and prior_rust.get("actual_durable_failure_receipt_verified") is True,
        "the genuine previous 139/11/1/1 Rust attempt was concealed",
    )
    resource = _checked_json(V16_RESOURCE_PATH, V16_RESOURCE_SHA256)
    _validate_resource(resource)
    v4 = legacy._frozen_module(
        legacy.V4_SOURCE_PATH, legacy.V4_SOURCE_SHA256,
        "_rebar_frozen_current_correctness_v4_for_v6",
    )
    v3 = v4._frozen_module(
        v4.V3_SOURCE_PATH, v4.V3_SOURCE_SHA256,
        "_rebar_frozen_current_correctness_v3_for_v6",
    )
    v2 = v3._frozen_module(
        v3.V2_SOURCE_PATH, v3.V2_SOURCE_SHA256,
        "_rebar_frozen_current_correctness_v2_for_v6",
    )
    v1 = v2._frozen_module(
        v2.V1_SOURCE_PATH, v2.V1_SOURCE_SHA256,
        "_rebar_frozen_current_correctness_v1_for_v6",
    )
    failure = _checked_json(
        RUST_V16_FAILURE_PATH, RUST_V16_FAILURE_SHA256, RUST_V16_FAILURE_BYTES,
    )
    current = _validate_v16_failure(
        failure, frozen=frozen, previous=previous, v2=v2, v1=v1,
    )
    forensic = _checked_json(V16_FORENSIC_PATH, V16_FORENSIC_SHA256)
    summary = _checked_json(
        V16_PRODUCTION_SUMMARY_PATH, V16_PRODUCTION_SUMMARY_SHA256,
    )
    _validate_forensic_and_summary(forensic, summary, current)
    current.update({
        "actual_forensic_path": V16_FORENSIC_PATH,
        "actual_forensic_sha256": V16_FORENSIC_SHA256,
        "actual_production_summary_path": V16_PRODUCTION_SUMMARY_PATH,
        "actual_production_summary_sha256": V16_PRODUCTION_SUMMARY_SHA256,
    })
    result = copy.deepcopy(previous)
    result["historical_v15_rust_upstream_failure"] = copy.deepcopy(prior_rust)
    result["full_python_suite"] = [
        current, *copy.deepcopy(previous["full_python_suite"][1:]),
    ]
    result["official_suite_candidate_passes"] = 0
    result["full_drop_in_compatibility"] = "NOT ESTABLISHED"
    result["current_actual_full_upstream_observation"] = {
        "passed_methods": 150,
        "harness_interference_errors": 0,
        "genuine_candidate_errors": 1,
        "private_debug_skips": 1,
        "completed_methods": PUBLIC_METHODS,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "outer_controller_stderr": NOT_PRESERVED,
        "outer_controller_publication_receipt": NOT_PRESERVED,
    }
    identities = [copy.deepcopy(entry) for entry in inherited]
    identities.extend((
        {
            "purpose": "frozen-v5-complete-original-correctness-and-history",
            "path": V5_SOURCE_PATH, "sha256": V5_SOURCE_SHA256,
        },
        {
            "purpose": "frozen-v5-canonical-complete-40-input-chart-manifest",
            "path": V5_MANIFEST_PATH, "sha256": V5_MANIFEST_SHA256,
        },
        {
            "purpose": "frozen-v16-complete-original-correctness-controller",
            "path": V16_SOURCE_PATH, "sha256": V16_SOURCE_SHA256,
        },
        {
            "purpose": "frozen-v16-complete-original-correctness-protocol",
            "path": V16_PROTOCOL_PATH, "sha256": V16_PROTOCOL_SHA256,
        },
        {
            "purpose": "genuine-v16-original-resource-and-private-locale-preflight",
            "path": V16_RESOURCE_PATH, "sha256": V16_RESOURCE_SHA256,
        },
        {
            "purpose": "genuine-v16-complete-152-method-rust-failure",
            "path": RUST_V16_FAILURE_PATH, "sha256": RUST_V16_FAILURE_SHA256,
        },
        {
            "purpose": "independent-v16-zero-worker-original-failure-forensic",
            "path": V16_FORENSIC_PATH, "sha256": V16_FORENSIC_SHA256,
        },
        {
            "purpose": "independent-v16-actual-original-production-summary",
            "path": V16_PRODUCTION_SUMMARY_PATH,
            "sha256": V16_PRODUCTION_SUMMARY_SHA256,
        },
    ))
    identities.sort(key=lambda entry: entry["path"])
    require(
        len(identities) == 48
        and len({entry["path"] for entry in identities}) == 48
        and all(_valid_sha256(entry.get("sha256")) for entry in identities),
        "the 48 exact, unique, independently frozen correctness inputs changed",
    )
    _validate_snapshot(result)
    return result, identities


def _validate_historical_v15(history: Any) -> None:
    require(
        type(history) is dict
        and history.get("family") == "rust"
        and history.get("label") == "Rust"
        and history.get("status") == "FAIL"
        and history.get("completed_methods") == PUBLIC_METHODS
        and history.get("total_methods") == PUBLIC_METHODS
        and history.get("passed_methods") == 139
        and history.get("error_methods") == 12
        and history.get("harness_interference_errors") == 11
        and history.get("genuine_candidate_errors") == 1
        and history.get("named_private_debug_skips") == 1
        and history.get("native_owner_guards") == METHOD_GUARDS
        and history.get("cached_matcher_guards") == METHOD_GUARDS
        and history.get("genuine_candidate_error_test") == PICKLING_METHOD
        and history.get("genuine_candidate_error") == PICKLING_ERROR
        and history.get("full_official_suite_qualified") is False
        and 139 + 11 + 1 + 1 == PUBLIC_METHODS,
        "the genuine previous 139-pass, 11-harness-error Rust attempt was hidden",
    )
    interference = history.get("harness_interference_error_records")
    gaps = history.get("genuine_candidate_error_records")
    require(
        type(interference) is list and len(interference) == 11
        and type(gaps) is list and len(gaps) == 1
        and gaps[0].get("test") == PICKLING_METHOD
        and gaps[0].get("classification")
        == "from-scratch Rust private pickle hook missing"
        and _valid_sha256(gaps[0].get("reason_sha256")),
        "a real previous test-harness failure or pickling gap was concealed",
    )
    names: set[str] = set()
    for record in interference:
        require(
            type(record) is dict
            and type(record.get("test")) is str
            and record["test"] != PICKLING_METHOD
            and record["test"] not in names
            and record.get("classification")
            == "test-harness matcher-guard interference"
            and _valid_sha256(record.get("reason_sha256")),
            "a genuine previous harness error was forged or relabeled",
        )
        names.add(record["test"])


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    require(
        type(snapshot) is dict
        and snapshot.get("candidate_count") == 3
        and snapshot.get("original_candidate_checks") == 3 * ORIGINAL_CASES_PER_FAMILY
        and snapshot.get("deeper_candidate_checks") == 3 * DEEP_CASES_PER_FAMILY
        and snapshot.get("observed_original_or_deeper_mismatches") == 0
        and snapshot.get("official_suite_candidate_passes") == 0
        and snapshot.get("full_drop_in_compatibility") == "NOT ESTABLISHED"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("holdout") == "NOT ACCESSED",
        "an engine, original-suite qualification, speed, or holdout was invented",
    )
    rows = snapshot.get("rows")
    require(type(rows) is list and len(rows) == 6, "a compatibility row was hidden")
    expected_rows = [
        (family, label, kind, count)
        for kind, count in (
            ("original", ORIGINAL_CASES_PER_FAMILY),
            ("deeper", DEEP_CASES_PER_FAMILY),
        )
        for family, label in FAMILIES
    ]
    for actual, (family, label, kind, count) in zip(rows, expected_rows, strict=True):
        require(
            type(actual) is dict
            and actual.get("family") == family
            and actual.get("label") == label
            and actual.get("kind") == kind
            and actual.get("status") == "PASS"
            and actual.get("passed") == count
            and actual.get("total") == count
            and actual.get("mismatches") == 0,
            "a complete original or deeper zero-mismatch result was changed",
        )
    scope = snapshot.get("original_python_test_scope")
    require(
        type(scope) is dict
        and scope.get("baseline") == "CPython 3.14.6 re"
        and scope.get("original_source_method_count") == ALL_ORIGINAL_METHODS
        and scope.get("applicable_public_method_count") == PUBLIC_METHODS
        and scope.get("named_private_class_waiver_count") == PRIVATE_WAIVER_CLASSES
        and scope.get("named_private_method_waiver_count") == PRIVATE_WAIVER_METHODS
        and scope.get("named_private_class_waivers") == NAMED_PRIVATE_CLASS_WAIVERS
        and scope.get("public_method_waivers") == []
        and scope.get("independent_reference_count") == 2
        and scope.get("reference_runnable_pass_count") == RUNNABLE_REFERENCE_METHODS
        and scope.get("reference_named_private_debug_skip_count") == 1
        and scope.get("reference_path") == REFERENCE_PATH
        and scope.get("reference_sha256") == REFERENCE_SHA256
        and scope.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
        and _valid_sha256(scope.get("reference_status_vector_sha256")),
        "the real 165-method original Python scope or private waivers changed",
    )
    baseline = scope.get("reference_roles")
    require(
        type(baseline) is list and len(baseline) == 2
        and tuple(role.get("role") for role in baseline)
        == ("reference_a", "reference_b"),
        "the two independent actual original Python baseline runs disappeared",
    )
    for role in baseline:
        debug = role.get("debug_skip")
        require(
            role.get("public_method_records") == PUBLIC_METHODS
            and role.get("passed") == RUNNABLE_REFERENCE_METHODS
            and role.get("named_private_debug_skips") == 1
            and type(debug) is dict
            and debug.get("test") == PRIVATE_DEBUG_METHOD
            and debug.get("reason") == PRIVATE_DEBUG_REASON
            and debug.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
            and debug.get("source_ast_sha256") == PRIVATE_DEBUG_SOURCE_AST_SHA256,
            "a genuine baseline public method or debug-build skip was forged",
        )
    for key, version in (
        ("historical_v12_rust_upstream_failure", "V12"),
        ("historical_v13_rust_upstream_failure", "V13"),
        ("historical_v14_rust_upstream_failure", "V14"),
    ):
        history = snapshot.get(key)
        require(
            type(history) is dict
            and history.get("family") == "rust"
            and history.get("completed_methods") == 0,
            "an actual original zero-test setup failure was hidden: " + version,
        )
        if version == "V12":
            require(
                history.get("status") == "STOPPED BEFORE TESTS"
                and history.get("cause") == "test-harness bridge wiring",
                "the actual V12 missing-bridge failure was concealed",
            )
        elif version == "V13":
            require(
                history.get("status") == "FAIL"
                and history.get("native_owner_guards") == 0
                and history.get("actual_error")
                == "stage-07 blocked unowned matching import: re",
                "the actual V13 anti-delegation setup failure was concealed",
            )
        else:
            require(
                history.get("status") == "FAIL"
                and history.get("native_owner_guards") == 0
                and history.get("actual_error")
                == "the V11 correctness controller must never import a candidate",
                "the actual V14 candidate-free setup failure was concealed",
            )
    _validate_historical_v15(snapshot.get("historical_v15_rust_upstream_failure"))
    suites = snapshot.get("full_python_suite")
    require(
        type(suites) is list and len(suites) == 3
        and tuple(role.get("family") for role in suites)
        == tuple(family for family, _ in FAMILIES),
        "an independently owned original-suite candidate was omitted",
    )
    rust = suites[0]
    gaps = rust.get("genuine_candidate_error_records")
    require(
        rust.get("label") == "Rust"
        and rust.get("status") == "FAIL"
        and rust.get("completed_methods") == PUBLIC_METHODS
        and rust.get("total_methods") == PUBLIC_METHODS
        and rust.get("passed_methods") == 150
        and rust.get("error_methods") == 1
        and rust.get("harness_interference_errors") == 0
        and rust.get("harness_interference_error_records") == []
        and rust.get("genuine_candidate_errors") == 1
        and rust.get("named_private_debug_skips") == 1
        and rust.get("native_owner_guards") == METHOD_GUARDS
        and rust.get("cached_matcher_guards") == METHOD_GUARDS
        and rust.get("genuine_candidate_error_test") == PICKLING_METHOD
        and rust.get("genuine_candidate_error") == PICKLING_ERROR
        and rust.get("full_official_suite_qualified") is False
        and rust.get("outer_controller_stderr") == NOT_PRESERVED
        and rust.get("outer_controller_publication_receipt") == NOT_PRESERVED
        and 150 + 1 + 1 == PUBLIC_METHODS
        and type(gaps) is list and len(gaps) == 1,
        "the real 150-pass, zero-harness-error original Rust result was forged",
    )
    gap = gaps[0]
    require(
        type(gap) is dict
        and gap.get("test") == PICKLING_METHOD
        and gap.get("classification")
        == "from-scratch Rust private pickle hook missing"
        and gap.get("reason_sha256") == PICKLING_REASON_SHA256
        and gap.get("source_ast_sha256") == PICKLING_SOURCE_AST_SHA256
        and gap.get("complete_reason_characters") == PICKLING_REASON_CHARACTERS,
        "the actual complete missing Rust pickling-hook evidence was concealed",
    )
    for (family, label), role in zip(FAMILIES[1:], suites[1:], strict=True):
        require(
            role.get("family") == family
            and role.get("label") == label
            and role.get("status") == "NOT RUN"
            and role.get("completed_methods") is None
            and role.get("total_methods") == PUBLIC_METHODS
            and role.get("native_owner_guards") is None
            and role.get("cached_matcher_guards") is None
            and role.get("full_official_suite_qualified") is False,
            "an unexecuted C or Zig original Python test was invented",
        )
    current = snapshot.get("current_actual_full_upstream_observation")
    require(
        type(current) is dict
        and current.get("passed_methods") == 150
        and current.get("harness_interference_errors") == 0
        and current.get("genuine_candidate_errors") == 1
        and current.get("private_debug_skips") == 1
        and current.get("completed_methods") == PUBLIC_METHODS
        and current.get("native_owner_guards") == METHOD_GUARDS
        and current.get("cached_matcher_guards") == METHOD_GUARDS
        and current.get("outer_controller_stderr") == NOT_PRESERVED
        and current.get("outer_controller_publication_receipt") == NOT_PRESERVED,
        "the current original-test observation or missing outer evidence changed",
    )


def _text(x: int, y: int, value: str, style: str = "body") -> str:
    return (
        f'<text x="{x}" y="{y}" class="{style}">'
        + html.escape(value)
        + "</text>"
    )


def render_svg(snapshot: dict[str, Any]) -> bytes:
    _validate_snapshot(snapshot)
    description = (
        "Three from-scratch regular-expression engines are compared against "
        "Python 3.14.6. All three pass 223,198 broad cases and 393 deeper "
        "cases. The original Python test source has 165 methods: 152 public "
        "records and 13 explicitly waived private methods in two named "
        "classes. Two separate Python baseline runs each pass 151 runnable "
        "methods and share one genuine debug-only skip. The latest Rust "
        "attempt passes 150 methods, reports one real missing pickling "
        "helper, records the same debug skip, and has zero test-harness "
        "errors. C and Zig have not yet run these original tests. All 304 "
        "native-owner checks and 304 cached-matcher checks ran. An earlier "
        "Rust attempt had 139 passes, 11 test-harness errors, the same one "
        "real gap, and the same one debug skip; three earlier setup failures "
        "are preserved. The outer controller's stderr and publication "
        "receipt were not preserved. Speed and memory are not measured; the "
        "holdout remains sealed. No engine is yet a qualified replacement."
    )
    result = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1560" '
        'viewBox="0 0 1200 1560" role="img" aria-labelledby="title description">',
        '<title id="title">Can these engines replace Python’s re?</title>',
        '<desc id="description">' + html.escape(description) + "</desc>",
        "<style>"
        "text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"
        "'Segoe UI',sans-serif}.title{font-size:34px;font-weight:760;fill:#10223b}"
        ".subtitle{font-size:15px;fill:#43536b}.metric{font-size:30px;"
        "font-weight:760;fill:#10223b}.metric-label{font-size:13px;fill:#43536b}"
        ".heading{font-size:20px;font-weight:730;fill:#10223b}.body{font-size:"
        "15px;fill:#25364e}.small{font-size:13px;fill:#43536b}.strong{font-size:"
        "16px;font-weight:720;fill:#10223b}.pass{font-size:14px;font-weight:720;"
        "fill:#116139}.fail{font-size:14px;font-weight:720;fill:#aa2831}"
        ".pending{font-size:14px;font-weight:720;fill:#485870}.footer{font-size:"
        "15px;font-weight:680;fill:#25364e}</style>",
        '<rect width="1200" height="1560" rx="20" fill="#f5f8fc"/>',
        _text(54, 70, "Can these engines replace Python’s re?", "title"),
        _text(
            56, 102,
            "Three independently built engines · honest comparison with Python 3.14.6",
            "subtitle",
        ),
    ]
    cards = (
        (54, "3", "from-scratch engines"),
        (338, "150 / 151", "Rust runnable tests passed"),
        (622, "1", "real compatibility gap"),
        (906, "0", "qualified replacements"),
    )
    for x, count, label in cards:
        result.extend((
            f'<rect x="{x}" y="130" width="240" height="92" rx="13" '
            'fill="#ffffff" stroke="#dce5ef"/>',
            _text(x + 15, 171, count, "metric"),
            _text(x + 15, 199, label, "metric-label"),
        ))
    result.extend((
        _text(56, 264, "The original Python tests: what really happened", "heading"),
        _text(
            56, 286,
            "Both Python runs pass 151 runnable methods; one identical "
            "debug-build-only test is skipped.",
            "small",
        ),
        '<rect x="54" y="301" width="1092" height="186" rx="12" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(73, 331, "Python baseline", "strong"),
        '<rect x="225" y="314" width="690" height="23" rx="7" '
        'fill="#16854f"/>',
        _text(932, 331, "151 / 151", "strong"),
        _text(1057, 331, "PASS", "pass"),
        _text(73, 374, "Rust", "strong"),
        '<rect x="225" y="357" width="690" height="23" rx="7" '
        'fill="#e5eaf1"/>',
        '<rect x="225" y="357" width="685" height="23" rx="7" '
        'fill="#16854f"/>',
        '<rect x="909" y="357" width="6" height="23" rx="2" '
        'fill="#ca424b"/>',
        _text(932, 374, "150 / 151", "strong"),
        _text(1057, 374, "1 GAP", "fail"),
        _text(73, 418, "C", "strong"),
        '<rect x="225" y="401" width="690" height="23" rx="7" '
        'fill="#e5eaf1"/>',
        _text(932, 418, "NOT RUN", "pending"),
        _text(73, 457, "Zig", "strong"),
        '<rect x="225" y="440" width="690" height="23" rx="7" '
        'fill="#e5eaf1"/>',
        _text(932, 457, "NOT RUN", "pending"),
    ))
    result.extend((
        _text(56, 528, "Every original Rust result is accounted for", "heading"),
        '<rect x="54" y="544" width="1092" height="137" rx="12" '
        'fill="#ffffff" stroke="#dce5ef"/>',
    ))
    for x, count, label in (
        (76, "150", "passing original methods"),
        (348, "0", "test-harness errors"),
        (600, "1", "real missing _compile"),
        (866, "1", "debug-only skip"),
    ):
        result.extend((
            _text(x, 588, count, "metric"),
            _text(x, 613, label, "metric-label"),
        ))
    result.extend((
        _text(
            75, 650,
            "150 passes + 0 harness errors + 1 real candidate error + "
            "1 genuine debug-only skip = 152",
            "small",
        ),
        _text(56, 724, "What remains to fix", "heading"),
        '<rect x="54" y="739" width="1092" height="91" rx="11" '
        'fill="#fff1f1" stroke="#ecc6c8"/>',
        _text(
            72, 769,
            "Python’s pickling test needs the _compile helper. "
            "The from-scratch Rust engine does not expose it.",
            "body",
        ),
        _text(
            72, 798,
            "This is a real remaining drop-in incompatibility, "
            "not a failed matching comparison.",
            "small",
        ),
        _text(56, 873, "The larger compatibility checks", "heading"),
        _text(
            56, 895,
            "These broad checks are useful, but are not the original "
            "Python test suite shown above.",
            "small",
        ),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 914 + 40 * index
        result.extend((
            _text(66, y + 18, label, "strong"),
            f'<rect x="158" y="{y}" width="574" height="24" rx="7" '
            'fill="#16854f"/>',
            _text(746, y + 18, "223,198 / 223,198", "strong"),
            _text(1000, y + 18, "PASS", "pass"),
        ))
    result.extend((
        _text(56, 1071, "Additional difficult cases", "heading"),
        _text(56, 1092, "The same 393 fixed cases for each independent engine.", "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 1107 + 38 * index
        result.extend((
            _text(66, y + 18, label, "strong"),
            f'<rect x="158" y="{y}" width="574" height="23" rx="7" '
            'fill="#16854f"/>',
            _text(746, y + 18, "393 / 393", "strong"),
            _text(1000, y + 18, "PASS", "pass"),
        ))
    result.extend((
        _text(56, 1258, "How the Python-test scope is counted", "heading"),
        '<rect x="54" y="1272" width="1092" height="96" rx="11" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(
            72, 1300,
            "165 original methods = 152 public records + 13 private tests "
            "in 2 named classes. No public test is waived.",
            "body",
        ),
        _text(
            72, 1326,
            "DebugTests: 4 private matching-opcode tests · "
            "ImplementationTest: 9 private compiler and implementation tests.",
            "small",
        ),
        _text(
            72, 1349,
            "304 native-owner checks + 304 cached-matcher checks "
            "verify the engine remained its own.",
            "small",
        ),
        _text(56, 1407, "Earlier attempts are not hidden", "heading"),
        _text(
            57, 1429,
            "Previous Rust attempt: 139 passes + 11 harness errors + "
            "1 real gap + 1 debug skip.",
            "small",
        ),
        _text(
            57, 1450,
            "Three earlier setup failures: missing bridge wiring · "
            "anti-delegation import guard · isolated controller guard.",
            "small",
        ),
        '<rect x="54" y="1464" width="1092" height="77" rx="11" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(
            72, 1489,
            "Overall: no engine has yet passed every required original Python test.",
            "footer",
        ),
        _text(
            72, 1511,
            "Speed and memory: NOT MEASURED · holdout: NOT ACCESSED.",
            "small",
        ),
        _text(
            72, 1530,
            "Outer controller stderr and publication receipt: NOT PRESERVED.",
            "small",
        ),
        "</svg>\n",
    ))
    return "\n".join(result).encode("utf-8")


def _bundle() -> tuple[bytes, bytes, dict[str, Any]]:
    snapshot, identities = _snapshot()
    svg = render_svg(snapshot)
    manifest = {
        "schema": SCHEMA + "-manifest",
        "status": "PASS",
        "generator_path": SOURCE_PATH,
        "chart_path": CHART_PATH,
        "chart_sha256": hashlib.sha256(svg).hexdigest(),
        "chart_bytes": len(svg),
        "validated_input_count": len(identities),
        "validated_inputs": identities,
        "snapshot": snapshot,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    return svg, canonical(manifest), manifest


def _exclusive_publish(name: str, payload: bytes, directory: int) -> str:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, 0o644, dir_fd=directory)
    except FileExistsError:
        read_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        read_flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(name, read_flags, dir_fd=directory)
        try:
            require(
                stat.S_ISREG(os.fstat(descriptor).st_mode),
                "an existing V6 chart artifact is not a real regular file",
            )
            blocks: list[bytes] = []
            while True:
                block = os.read(descriptor, 1024 * 1024)
                if not block:
                    break
                blocks.append(block)
            require(
                b"".join(blocks) == payload,
                "refusing to overwrite a different actual V6 correctness result",
            )
        finally:
            os.close(descriptor)
        return "EXISTING IDENTICAL"
    try:
        completed = 0
        while completed < len(payload):
            observed = os.write(descriptor, payload[completed:])
            require(
                type(observed) is int and observed > 0,
                "an exclusive V6 chart publication was incomplete",
            )
            completed += observed
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.fsync(directory)
    return "EXCLUSIVELY CREATED"


def _write(svg: bytes, manifest: bytes) -> dict[str, str]:
    flags = os.O_RDONLY | os.O_DIRECTORY
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    repository = os.open(str(ROOT), flags)
    docs = -1
    evidence = -1
    try:
        docs = os.open("docs", flags, dir_fd=repository)
        evidence = os.open("evidence", flags, dir_fd=docs)
        return {
            "chart": _exclusive_publish(
                "current-native-correctness-v6.svg", svg, evidence,
            ),
            "manifest": _exclusive_publish(
                "current-native-correctness-v6.json", manifest, evidence,
            ),
        }
    finally:
        if evidence != -1:
            os.close(evidence)
        if docs != -1:
            os.close(docs)
        os.close(repository)


@contextlib.contextmanager
def _source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0,
        "file_writes": 0,
        "candidate_imports": 0,
        "workers": 0,
        "threads": 0,
        "clock_samples": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "blocked_file_reads": 0,
        "blocked_file_writes": 0,
        "blocked_candidate_imports": 0,
        "blocked_workers": 0,
        "blocked_threads": 0,
        "blocked_clock_samples": 0,
    }
    restore: list[tuple[Any, str, Any]] = []

    def deny(counter: str, reason: str) -> Callable[..., Any]:
        def rejected(*_args: Any, **_kwargs: Any) -> Any:
            effects[counter] += 1
            raise ChartError(reason)

        return rejected

    def patch(owner: Any, name: str, substitute: Any) -> None:
        if hasattr(owner, name):
            restore.append((owner, name, getattr(owner, name)))
            setattr(owner, name, substitute)

    stop_read = deny("blocked_file_reads", "source-only controls cannot read")
    stop_write = deny("blocked_file_writes", "source-only controls cannot write")
    stop_import = deny(
        "blocked_candidate_imports", "source-only controls cannot import",
    )
    stop_worker = deny("blocked_workers", "source-only controls cannot run workers")
    stop_thread = deny("blocked_threads", "source-only controls cannot start threads")
    stop_clock = deny("blocked_clock_samples", "source-only controls cannot time")
    try:
        patch(builtins, "open", stop_read)
        patch(io, "open", stop_read)
        for name in (
            "open", "read_bytes", "read_text", "exists", "stat", "is_file",
            "is_dir", "iterdir", "glob", "rglob",
        ):
            patch(Path, name, stop_read)
        for name in ("open", "stat", "lstat", "scandir", "listdir"):
            patch(os, name, stop_read)
        for name in (
            "write", "fsync", "mkdir", "makedirs", "remove", "unlink",
            "rename", "replace",
        ):
            patch(os, name, stop_write)
        patch(Path, "write_bytes", stop_write)
        patch(Path, "write_text", stop_write)
        patch(subprocess, "run", stop_worker)
        patch(subprocess, "Popen", stop_worker)
        patch(os, "fork", stop_worker)
        patch(multiprocessing.Process, "start", stop_worker)
        patch(threading.Thread, "start", stop_thread)
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
            "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
            "thread_time_ns",
        ):
            patch(time, name, stop_clock)
        patch(importlib, "import_module", stop_import)
        patch(builtins, "__import__", stop_import)
        yield effects
    finally:
        for owner, name, saved in reversed(restore):
            setattr(owner, name, saved)


def _synthetic_snapshot() -> dict[str, Any]:
    rows = [
        {
            "family": family,
            "label": label,
            "kind": kind,
            "status": "PASS",
            "passed": count,
            "total": count,
            "mismatches": 0,
        }
        for kind, count in (
            ("original", ORIGINAL_CASES_PER_FAMILY),
            ("deeper", DEEP_CASES_PER_FAMILY),
        )
        for family, label in FAMILIES
    ]
    debug = {
        "test": PRIVATE_DEBUG_METHOD,
        "reason": PRIVATE_DEBUG_REASON,
        "skip_kind": PRIVATE_DEBUG_SKIP_KIND,
        "source_ast_sha256": PRIVATE_DEBUG_SOURCE_AST_SHA256,
    }
    references = [
        {
            "role": name,
            "public_method_records": PUBLIC_METHODS,
            "passed": RUNNABLE_REFERENCE_METHODS,
            "named_private_debug_skips": 1,
            "debug_skip": copy.deepcopy(debug),
        }
        for name in ("reference_a", "reference_b")
    ]
    scope = {
        "baseline": "CPython 3.14.6 re",
        "original_source_method_count": ALL_ORIGINAL_METHODS,
        "applicable_public_method_count": PUBLIC_METHODS,
        "named_private_class_waiver_count": PRIVATE_WAIVER_CLASSES,
        "named_private_method_waiver_count": PRIVATE_WAIVER_METHODS,
        "named_private_class_waivers": copy.deepcopy(NAMED_PRIVATE_CLASS_WAIVERS),
        "public_method_waivers": [],
        "independent_reference_count": 2,
        "reference_runnable_pass_count": RUNNABLE_REFERENCE_METHODS,
        "reference_named_private_debug_skip_count": 1,
        "reference_roles": references,
        "reference_status_vector_sha256": hashlib.sha256(
            b"synthetic-only-not-an-actual-baseline",
        ).hexdigest(),
        "reference_path": REFERENCE_PATH,
        "reference_sha256": REFERENCE_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
    }
    gap = {
        "test": PICKLING_METHOD,
        "classification": "from-scratch Rust private pickle hook missing",
        "reason_sha256": PICKLING_REASON_SHA256,
        "complete_reason_characters": PICKLING_REASON_CHARACTERS,
        "source_ast_sha256": PICKLING_SOURCE_AST_SHA256,
    }
    rust = {
        "family": "rust",
        "label": "Rust",
        "status": "FAIL",
        "completed_methods": PUBLIC_METHODS,
        "total_methods": PUBLIC_METHODS,
        "passed_methods": 150,
        "error_methods": 1,
        "harness_interference_errors": 0,
        "harness_interference_error_records": [],
        "genuine_candidate_errors": 1,
        "genuine_candidate_error_records": [copy.deepcopy(gap)],
        "genuine_candidate_error_test": PICKLING_METHOD,
        "genuine_candidate_error": PICKLING_ERROR,
        "named_private_debug_skips": 1,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "full_official_suite_qualified": False,
        "outer_controller_stderr": NOT_PRESERVED,
        "outer_controller_publication_receipt": NOT_PRESERVED,
    }
    prior_interference = [
        {
            "test": "synthetic_warning_" + str(number),
            "reason_sha256": hashlib.sha256(str(number).encode("ascii")).hexdigest(),
            "classification": "test-harness matcher-guard interference",
        }
        for number in range(11)
    ]
    prior_gap = {
        "test": PICKLING_METHOD,
        "reason_sha256": hashlib.sha256(
            b"synthetic-only-prior-pickling-observation",
        ).hexdigest(),
        "classification": "from-scratch Rust private pickle hook missing",
    }
    historical_v15 = {
        "family": "rust",
        "label": "Rust",
        "status": "FAIL",
        "completed_methods": PUBLIC_METHODS,
        "total_methods": PUBLIC_METHODS,
        "passed_methods": 139,
        "error_methods": 12,
        "harness_interference_errors": 11,
        "harness_interference_error_records": prior_interference,
        "genuine_candidate_errors": 1,
        "genuine_candidate_error_records": [prior_gap],
        "genuine_candidate_error_test": PICKLING_METHOD,
        "genuine_candidate_error": PICKLING_ERROR,
        "named_private_debug_skips": 1,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "full_official_suite_qualified": False,
    }
    pending = [
        {
            "family": family,
            "label": label,
            "status": "NOT RUN",
            "completed_methods": None,
            "total_methods": PUBLIC_METHODS,
            "native_owner_guards": None,
            "cached_matcher_guards": None,
            "full_official_suite_qualified": False,
        }
        for family, label in FAMILIES[1:]
    ]
    return {
        "candidate_count": 3,
        "original_candidate_checks": 3 * ORIGINAL_CASES_PER_FAMILY,
        "deeper_candidate_checks": 3 * DEEP_CASES_PER_FAMILY,
        "observed_original_or_deeper_mismatches": 0,
        "official_suite_candidate_passes": 0,
        "full_drop_in_compatibility": "NOT ESTABLISHED",
        "rows": rows,
        "original_python_test_scope": scope,
        "full_python_suite": [rust, *pending],
        "historical_v12_rust_upstream_failure": {
            "family": "rust",
            "status": "STOPPED BEFORE TESTS",
            "completed_methods": 0,
            "cause": "test-harness bridge wiring",
        },
        "historical_v13_rust_upstream_failure": {
            "family": "rust",
            "status": "FAIL",
            "completed_methods": 0,
            "native_owner_guards": 0,
            "actual_error": "stage-07 blocked unowned matching import: re",
        },
        "historical_v14_rust_upstream_failure": {
            "family": "rust",
            "status": "FAIL",
            "completed_methods": 0,
            "native_owner_guards": 0,
            "actual_error": (
                "the V11 correctness controller must never import a candidate"
            ),
        },
        "historical_v15_rust_upstream_failure": historical_v15,
        "current_actual_full_upstream_observation": {
            "passed_methods": 150,
            "harness_interference_errors": 0,
            "genuine_candidate_errors": 1,
            "private_debug_skips": 1,
            "completed_methods": PUBLIC_METHODS,
            "native_owner_guards": METHOD_GUARDS,
            "cached_matcher_guards": METHOD_GUARDS,
            "outer_controller_stderr": NOT_PRESERVED,
            "outer_controller_publication_receipt": NOT_PRESERVED,
        },
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _self_test() -> dict[str, Any]:
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "source-only chart controls cannot import any matching candidate",
    )
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(
            not any(check["name"] == name for check in checks),
            "a source-only acceptance control was counted twice",
        )
        require(condition is True, "a source-only acceptance failed: " + name)
        checks.append({"name": name, "kind": "accepted", "passed": True})

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(
            not any(check["name"] == name for check in checks),
            "a source-only rejection control was counted twice",
        )
        try:
            action()
        except (
            ChartError, OSError, AssertionError, TypeError, ValueError,
            KeyError, ImportError,
        ):
            checks.append({"name": name, "kind": "rejected", "passed": True})
        else:
            raise ChartError("an unsafe synthetic chart was accepted: " + name)

    with _source_only_boundary() as effects:
        snapshot = _synthetic_snapshot()
        picture = render_svg(snapshot)
        accept("render-source-only-synthetic-chart", picture.startswith(b"<svg "))
        accept("render-byte-identical-on-repeat", picture == render_svg(snapshot))
        accept(
            "render-byte-identical-deep-copy",
            picture == render_svg(copy.deepcopy(snapshot)),
        )
        accept("terminate-real-svg-element", picture.endswith(b"</svg>\n"))
        accept("provide-accessible-chart-title", b'<title id="title">' in picture)
        accept("provide-accessible-chart-description", b'<desc id="description">' in picture)
        accept("name-pinned-python-release", b"Python 3.14.6" in picture)
        accept("show-three-independent-engines", b"Three independently built engines" in picture)
        accept("show-full-original-source-denominator", b"165 original methods" in picture)
        accept("show-152-original-public-records", b"152 public records" in picture)
        accept("show-exactly-13-private-method-waivers", b"13 private tests" in picture)
        accept("show-exactly-two-named-waiver-classes", b"2 named classes" in picture)
        accept("name-four-private-debug-tests", b"DebugTests: 4" in picture)
        accept("name-nine-private-implementation-tests", b"ImplementationTest: 9" in picture)
        accept("refuse-every-public-method-waiver", b"No public test is waived" in picture)
        accept("show-real-151-runnable-baseline", b"151 / 151" in picture)
        accept("show-real-150-runnable-rust-passes", picture.count(b"150 / 151") >= 2)
        accept("show-the-real-one-gap", b"real compatibility gap" in picture)
        accept("show-zero-remaining-harness-errors", b"test-harness errors" in picture)
        accept("show-authentic-debug-only-skip", b"debug-build-only" in picture)
        accept("show-exact-complete-152-method-equation", (
            b"150 passes + 0 harness errors + 1 real candidate error" in picture
        ))
        accept("show-genuine-missing-pickle-helper", b"real missing _compile" in picture)
        accept("show-all-three-original-case-denominators", (
            picture.count(b"223,198 / 223,198") == 3
        ))
        accept("show-all-three-deeper-case-denominators", (
            picture.count(b"393 / 393") == 3
        ))
        accept("separate-broad-checks-from-original-suite", (
            b"not the original Python test suite" in picture
        ))
        accept("show-c-and-zig-as-not-run", picture.count(b">NOT RUN</text>") == 2)
        accept("show-both-authentic-304-engine-guards", (
            b"304 native-owner checks + 304 cached-matcher checks" in picture
        ))
        accept("retain-real-prior-139-rust-passes", b"139 passes" in picture)
        accept("retain-real-prior-eleven-harness-errors", b"11 harness errors" in picture)
        accept("retain-real-missing-bridge-history", b"missing bridge wiring" in picture)
        accept("retain-real-anti-delegation-history", b"anti-delegation import guard" in picture)
        accept("retain-real-isolated-controller-history", b"isolated controller guard" in picture)
        accept("show-zero-qualified-replacement-engines", b"qualified replacements" in picture)
        accept("disclose-unpreserved-outer-stderr", (
            b"Outer controller stderr and publication receipt: NOT PRESERVED" in picture
        ))
        accept("keep-speed-and-memory-unmeasured", b"Speed and memory: NOT MEASURED" in picture)
        accept("keep-final-holdout-sealed", b"holdout: NOT ACCESSED" in picture)

        for key, value in (
            ("candidate_count", 2),
            ("candidate_count", 4),
            ("original_candidate_checks", 669_593),
            ("deeper_candidate_checks", 1_178),
            ("observed_original_or_deeper_mismatches", 1),
            ("official_suite_candidate_passes", 1),
            ("full_drop_in_compatibility", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "ACCESSED"),
        ):
            changed = copy.deepcopy(snapshot)
            changed[key] = value
            reject(
                "reject-fabricated-overall:" + key + ":" + str(value),
                lambda changed=changed: render_svg(changed),
            )
        for index in range(6):
            for key, value in (
                ("status", "FAIL"),
                ("mismatches", 1),
                ("passed", snapshot["rows"][index]["total"] - 1),
                ("total", snapshot["rows"][index]["total"] + 1),
                ("family", "borrowed_engine"),
                ("kind", "invented_suite"),
            ):
                changed = copy.deepcopy(snapshot)
                changed["rows"][index][key] = value
                reject(
                    "reject-fabricated-broad-or-deep-row:"
                    + str(index) + ":" + key,
                    lambda changed=changed: render_svg(changed),
                )
        for key, value in (
            ("baseline", "invented baseline"),
            ("original_source_method_count", 164),
            ("original_source_method_count", 166),
            ("applicable_public_method_count", 151),
            ("applicable_public_method_count", 153),
            ("named_private_class_waiver_count", 1),
            ("named_private_class_waiver_count", 3),
            ("named_private_method_waiver_count", 12),
            ("named_private_method_waiver_count", 14),
            ("independent_reference_count", 1),
            ("independent_reference_count", 3),
            ("reference_runnable_pass_count", 150),
            ("reference_runnable_pass_count", 152),
            ("reference_named_private_debug_skip_count", 0),
            ("reference_named_private_debug_skip_count", 2),
            ("reference_path", "invented-reference.json"),
            ("reference_sha256", "a" * 64),
            ("reference_status_vector_sha256", "not-a-hash"),
            ("public_method_matrix_sha256", "b" * 64),
        ):
            changed = copy.deepcopy(snapshot)
            changed["original_python_test_scope"][key] = value
            reject(
                "reject-forged-original-suite-scope:" + key + ":" + str(value),
                lambda changed=changed: render_svg(changed),
            )
        changed = copy.deepcopy(snapshot)
        changed["original_python_test_scope"]["public_method_waivers"] = [
            {"test": "invented public waiver"},
        ]
        reject("reject-any-public-method-waiver", lambda: render_svg(changed))
        for class_name in ("DebugTests", "ImplementationTest"):
            for mutation in ("missing", "methods", "reason"):
                changed = copy.deepcopy(snapshot)
                waivers = changed["original_python_test_scope"][
                    "named_private_class_waivers"
                ]
                if mutation == "missing":
                    waivers.pop(class_name)
                elif mutation == "methods":
                    waivers[class_name]["methods"] += 1
                else:
                    waivers[class_name]["reason"] = "invented private waiver"
                reject(
                    "reject-forged-private-class:" + class_name + ":" + mutation,
                    lambda changed=changed: render_svg(changed),
                )
        for index in (0, 1):
            for key, value in (
                ("role", "invented_reference"),
                ("public_method_records", 151),
                ("public_method_records", 153),
                ("passed", 150),
                ("passed", 152),
                ("named_private_debug_skips", 0),
                ("named_private_debug_skips", 2),
            ):
                changed = copy.deepcopy(snapshot)
                changed["original_python_test_scope"]["reference_roles"][index][
                    key
                ] = value
                reject(
                    "reject-forged-independent-baseline:"
                    + str(index) + ":" + key + ":" + str(value),
                    lambda changed=changed: render_svg(changed),
                )
            for key, value in (
                ("test", "ReTests.test_invented_skip"),
                ("reason", "invented debug skip"),
                ("skip_kind", "invented waiver"),
                ("source_ast_sha256", "a" * 64),
            ):
                changed = copy.deepcopy(snapshot)
                changed["original_python_test_scope"]["reference_roles"][index][
                    "debug_skip"
                ][key] = value
                reject(
                    "reject-forged-baseline-debug-skip:"
                    + str(index) + ":" + key,
                    lambda changed=changed: render_svg(changed),
                )
        for key, value in (
            ("family", "borrowed_engine"),
            ("label", "invented engine"),
            ("status", "PASS"),
            ("completed_methods", 151),
            ("completed_methods", 153),
            ("total_methods", 151),
            ("total_methods", 165),
            ("passed_methods", 139),
            ("passed_methods", 149),
            ("passed_methods", 151),
            ("error_methods", 0),
            ("error_methods", 2),
            ("harness_interference_errors", 1),
            ("genuine_candidate_errors", 0),
            ("genuine_candidate_errors", 2),
            ("named_private_debug_skips", 0),
            ("named_private_debug_skips", 2),
            ("native_owner_guards", 303),
            ("native_owner_guards", 305),
            ("cached_matcher_guards", 303),
            ("cached_matcher_guards", 305),
            ("full_official_suite_qualified", True),
            ("genuine_candidate_error_test", "ReTests.test_matching"),
            ("genuine_candidate_error", "invented matching failure"),
            ("outer_controller_stderr", "PRESERVED"),
            ("outer_controller_publication_receipt", "PRESERVED"),
        ):
            changed = copy.deepcopy(snapshot)
            changed["full_python_suite"][0][key] = value
            reject(
                "reject-forged-current-rust-result:" + key + ":" + str(value),
                lambda changed=changed: render_svg(changed),
            )
        changed = copy.deepcopy(snapshot)
        changed["full_python_suite"][0][
            "harness_interference_error_records"
        ].append({"test": "invented harness error"})
        reject("reject-invented-current-harness-interference", (
            lambda: render_svg(changed)
        ))
        changed = copy.deepcopy(snapshot)
        changed["full_python_suite"][0]["genuine_candidate_error_records"].pop()
        reject("reject-concealed-real-current-pickling-error", (
            lambda: render_svg(changed)
        ))
        for key, value in (
            ("test", "ReTests.test_matching"),
            ("classification", "test-harness matcher-guard interference"),
            ("reason_sha256", "a" * 64),
            ("complete_reason_characters", PICKLING_REASON_CHARACTERS - 1),
            ("source_ast_sha256", "b" * 64),
        ):
            changed = copy.deepcopy(snapshot)
            changed["full_python_suite"][0][
                "genuine_candidate_error_records"
            ][0][key] = value
            reject(
                "reject-forged-complete-real-pickling-error:" + key,
                lambda changed=changed: render_svg(changed),
            )
        for index in (1, 2):
            for key, value in (
                ("status", "PASS"),
                ("completed_methods", PUBLIC_METHODS),
                ("total_methods", PUBLIC_METHODS - 1),
                ("native_owner_guards", METHOD_GUARDS),
                ("cached_matcher_guards", METHOD_GUARDS),
                ("full_official_suite_qualified", True),
                ("family", "invented_engine"),
                ("label", "invented engine"),
            ):
                changed = copy.deepcopy(snapshot)
                changed["full_python_suite"][index][key] = value
                reject(
                    "reject-invented-unrun-independent-engine:"
                    + str(index) + ":" + key,
                    lambda changed=changed: render_svg(changed),
                )
        for key, value in (
            ("status", "PASS"),
            ("completed_methods", 0),
            ("total_methods", 151),
            ("passed_methods", 138),
            ("passed_methods", 140),
            ("passed_methods", 150),
            ("error_methods", 11),
            ("error_methods", 13),
            ("harness_interference_errors", 0),
            ("harness_interference_errors", 10),
            ("harness_interference_errors", 12),
            ("genuine_candidate_errors", 0),
            ("genuine_candidate_errors", 2),
            ("named_private_debug_skips", 0),
            ("native_owner_guards", 303),
            ("cached_matcher_guards", 303),
            ("full_official_suite_qualified", True),
            ("genuine_candidate_error_test", "ReTests.test_matching"),
            ("genuine_candidate_error", "invented matching failure"),
        ):
            changed = copy.deepcopy(snapshot)
            changed["historical_v15_rust_upstream_failure"][key] = value
            reject(
                "reject-concealed-prior-v15-rust-result:"
                + key + ":" + str(value),
                lambda changed=changed: render_svg(changed),
            )
        for field in (
            "harness_interference_error_records", "genuine_candidate_error_records",
        ):
            changed = copy.deepcopy(snapshot)
            changed["historical_v15_rust_upstream_failure"][field].pop()
            reject(
                "reject-suppressed-prior-v15-error:" + field,
                lambda changed=changed: render_svg(changed),
            )
        changed = copy.deepcopy(snapshot)
        changed["historical_v15_rust_upstream_failure"][
            "harness_interference_error_records"
        ][0]["classification"] = "genuine candidate matching failure"
        reject("reject-relabelled-prior-harness-error", (
            lambda: render_svg(changed)
        ))
        for key in (
            "historical_v12_rust_upstream_failure",
            "historical_v13_rust_upstream_failure",
            "historical_v14_rust_upstream_failure",
        ):
            for field, value in (
                ("family", "borrowed_engine"),
                ("status", "PASS"),
                ("completed_methods", PUBLIC_METHODS),
            ):
                changed = copy.deepcopy(snapshot)
                changed[key][field] = value
                reject(
                    "reject-concealed-prior-setup-failure:"
                    + key + ":" + field,
                    lambda changed=changed: render_svg(changed),
                )
        for key, value in (
            ("passed_methods", 149),
            ("passed_methods", 151),
            ("harness_interference_errors", 1),
            ("genuine_candidate_errors", 0),
            ("private_debug_skips", 0),
            ("completed_methods", 151),
            ("native_owner_guards", 303),
            ("cached_matcher_guards", 303),
            ("outer_controller_stderr", "PRESERVED"),
            ("outer_controller_publication_receipt", "PRESERVED"),
        ):
            changed = copy.deepcopy(snapshot)
            changed["current_actual_full_upstream_observation"][key] = value
            reject(
                "reject-forged-current-observation:" + key + ":" + str(value),
                lambda changed=changed: render_svg(changed),
            )
        reject("reject-frozen-original-reference-read", (
            lambda: builtins.open(REFERENCE_PATH, "rb")
        ))
        reject("reject-frozen-prior-chart-source-read", (
            lambda: os.open(V5_SOURCE_PATH, os.O_RDONLY)
        ))
        reject("reject-frozen-current-oracle-source-read", (
            lambda: (ROOT / V16_SOURCE_PATH).read_bytes()
        ))
        reject("reject-frozen-actual-v16-failure-read", (
            lambda: (ROOT / RUST_V16_FAILURE_PATH).read_bytes()
        ))
        reject("reject-any-performance-or-holdout-inspection", (
            lambda: (ROOT / "performance").exists()
        ))
        reject("reject-direct-candidate-import", (
            lambda: importlib.import_module("candidates.rust_candidate")
        ))
        reject("reject-builtin-cross-engine-candidate-import", (
            lambda: builtins.__import__("candidates.zig_candidate")
        ))
        reject("reject-unrequested-original-candidate-worker", (
            lambda: subprocess.run(["production-candidate-worker"])
        ))
        reject("reject-unrequested-background-worker", (
            lambda: threading.Thread(target=lambda: None).start()
        ))
        reject("reject-hidden-performance-clock", time.perf_counter)
        reject("reject-unauthorized-chart-publication", (
            lambda: (ROOT / CHART_PATH).write_bytes(b"fabricated")
        ))
        for effect in (
            "file_reads", "file_writes", "candidate_imports", "workers",
            "threads", "clock_samples", "holdout_cases_read",
            "performance_fixtures_read",
        ):
            accept(
                "perform-zero-actual-source-effects:" + effect,
                effects[effect] == 0,
            )
        for effect, minimum in (
            ("blocked_file_reads", 5),
            ("blocked_file_writes", 1),
            ("blocked_candidate_imports", 2),
            ("blocked_workers", 1),
            ("blocked_threads", 1),
            ("blocked_clock_samples", 1),
        ):
            accept(
                "actually-enforce-source-boundary:" + effect,
                effects[effect] >= minimum,
            )
        require(
            len(checks) >= 180,
            "at least 180 independently genuine source-only controls are required",
        )
        preserved_effects = dict(effects)
    accepted = sum(check["kind"] == "accepted" for check in checks)
    rejected = sum(check["kind"] == "rejected" for check in checks)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "total_controls": len(checks),
        "actual_evidence_reads": 0,
        "actual_candidates_qualified": 0,
        "frozen_v5_source_sha256": V5_SOURCE_SHA256,
        "frozen_v5_manifest_sha256": V5_MANIFEST_SHA256,
        "frozen_v16_source_sha256": V16_SOURCE_SHA256,
        "frozen_v16_protocol_sha256": V16_PROTOCOL_SHA256,
        "effects": preserved_effects,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Visualize honestly verified Python regex replacement progress.",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            result = _self_test()
        else:
            svg, manifest_bytes, manifest = _bundle()
            if options.write:
                publication = _write(svg, manifest_bytes)
            else:
                require(
                    _read_regular(CHART_PATH) == svg
                    and _read_regular(MANIFEST_PATH) == manifest_bytes,
                    "the V6 chart and manifest are not exactly reproducible",
                )
                publication = {"chart": "VERIFIED", "manifest": "VERIFIED"}
            result = {
                "schema": SCHEMA + ("-write" if options.write else "-check"),
                "status": "PASS",
                "chart_path": CHART_PATH,
                "chart_sha256": manifest["chart_sha256"],
                "manifest_path": MANIFEST_PATH,
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "validated_input_count": manifest["validated_input_count"],
                "publication": publication,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            }
    except (
        ChartError, AssertionError, OSError, ValueError, TypeError,
        KeyError, MemoryError,
    ) as error:
        print(
            json.dumps(
                {
                    "schema": SCHEMA + "-failure",
                    "status": "FAIL",
                    "actual_error_type": type(error).__name__,
                    "reason": str(error),
                    "performance": "NOT MEASURED",
                    "holdout": "NOT ACCESSED",
                },
                ensure_ascii=True, sort_keys=True, separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2
    print(canonical(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
