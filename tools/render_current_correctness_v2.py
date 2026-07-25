#!/usr/bin/env python3
"""Render only authenticated, current, from-scratch regex correctness."""

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
import tempfile
import threading
import time
import types
from typing import Any, Callable, Iterator


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "rebar-current-native-correctness-v2"
SOURCE_PATH = "tools/render_current_correctness_v2.py"
CHART_PATH = "docs/evidence/current-native-correctness-v2.svg"
MANIFEST_PATH = "docs/evidence/current-native-correctness-v2.json"
V1_SOURCE_PATH = "tools/render_current_correctness_v1.py"
V1_SOURCE_SHA256 = "2fa6365890ebea5de98194a204866351caea29a631f2b13a8c7050049e0f64a8"
V13_SOURCE_PATH = "tools/postfinal_cpython_locale_oracle_v13.py"
V13_SOURCE_SHA256 = "5f9ca285ba617308dead53b97a6d6c707bd4371b7cad79345da8b99223260015"
V13_PROTOCOL_PATH = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V13.md"
V13_PROTOCOL_SHA256 = "7ab886971b63faddecb56f4403a582d48903fbb228bc0fccdca80c46f5c4c0dc"
V6_REFERENCE_SHA256 = "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
METHOD_MATRIX_SHA256 = "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
PRIVATE_DEBUG_METHOD = "ReTests.test_memory_leaks"
PRIVATE_DEBUG_REASON = "requires debug build"
PRIVATE_DEBUG_SKIP_KIND = "named-private-debug-condition"
PRIVATE_DEBUG_SOURCE_AST_SHA256 = (
    "840264aaf4bf27c06d29ac78664767327a8f4b90008c5db994c88542c692b389"
)
RUST_V13_FAILURE_SHA256 = (
    "18f572e44382130fe6ae29a05bb4c063fccf95d92fc305c9548cb1a63ac01844"
)
RUST_V13_FAILURE_SUMMARY_SHA256 = (
    "7ae58265f0b845b9f50b30fcb7c7c75018cbcb40d49d240760373a517c2b46c1"
)
RUST_V13_SETUP_ERROR = "stage-07 blocked unowned matching import: re"
FAMILIES = (("rust", "Rust"), ("vm", "C"), ("zig", "Zig"))
PUBLIC_METHODS = 152
METHOD_GUARDS = 304
MAX_INPUT_BYTES = 128 * 1024 * 1024
V13_PREFIX = "oracle/cpython-3.14.6/evidence/postfinal-locale-v13-"


class ChartError(Exception):
    """A current result has not been completely and independently proved."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ChartError(message)


def canonical(document: Any) -> bytes:
    return (
        json.dumps(document, ensure_ascii=True, allow_nan=False,
                   sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")


def _read_regular(relative: str, *, optional: bool = False) -> bytes | None:
    require(type(relative) is str and relative and "\\" not in relative,
            "only a predeclared repository-relative correctness input is permitted")
    parsed = Path(relative)
    require(not parsed.is_absolute() and ".." not in parsed.parts,
            "correctness evidence must not escape its repository")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = os.open(str(ROOT / parsed), flags)
    except FileNotFoundError:
        if optional:
            return None
        raise
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode)
                and 0 < information.st_size <= MAX_INPUT_BYTES,
                "a correctness input is not a bounded, genuine regular file")
        pieces: list[bytes] = []
        while True:
            piece = os.read(descriptor, 1024 * 1024)
            if not piece:
                break
            pieces.append(piece)
        result = b"".join(pieces)
        require(len(result) == information.st_size,
                "a bounded correctness input changed while being read")
        return result
    finally:
        os.close(descriptor)


def _read_json(relative: str, *, optional: bool = False) -> tuple[dict[str, Any], str] | None:
    raw = _read_regular(relative, optional=optional)
    if raw is None:
        return None
    try:
        document = json.loads(raw)
    except (UnicodeError, ValueError) as error:
        raise ChartError("a frozen correctness input is not valid JSON: " + relative) from error
    require(type(document) is dict,
            "a frozen correctness input must be a complete JSON object")
    return document, hashlib.sha256(raw).hexdigest()


def _frozen_module(relative: str, expected: str, name: str) -> types.ModuleType:
    raw = _read_regular(relative)
    require(raw is not None and hashlib.sha256(raw).hexdigest() == expected,
            "a frozen correctness validator has changed: " + relative)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    code = compile(raw, module.__file__, "exec", dont_inherit=True)
    exec(code, module.__dict__)
    return module


def _validate_matrix(
    reference: dict[str, Any], frozen: Any, legacy: Any,
) -> list[dict[str, Any]]:
    legacy._validate_reference(reference)
    require(reference.get("schema") ==
            "rebar-postfinal-cpython-full-public-locale-v6-self-oracle"
            and reference.get("status") == "PASS"
            and reference.get("synthetic") is False
            and reference.get("python") == "3.14.6"
            and reference.get("source_path") == frozen.V6_SOURCE_RELATIVE
            and reference.get("source_sha256") == frozen.V6_SOURCE_SHA256
            and reference.get("protocol_path") == frozen.V6_PROTOCOL_RELATIVE
            and reference.get("protocol_sha256") == frozen.V6_PROTOCOL_SHA256
            and reference.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
            and reference.get("actual_independent_reference_count") == 2
            and reference.get("reference_candidate_imports") == 0
            and reference.get("reference_candidate_audits_read") == 0
            and reference.get("reference_candidate_proofs_read") == 0
            and reference.get("reference_holdout_cases_read") == 0
            and reference.get("performance") == "NOT MEASURED"
            and reference.get("holdout") == "NOT ACCESSED",
            "the actual frozen double original reference was substituted")
    roles = reference.get("roles")
    require(type(roles) is dict
            and tuple(roles) == ("reference_a", "reference_b"),
            "the two original pinned Python reference runs are mandatory")
    vectors: list[list[dict[str, Any]]] = []
    for label in ("reference_a", "reference_b"):
        role = roles[label]
        require(type(role) is dict and role.get("applicable") == 151
                and role.get("passed") == 151
                and role.get("named_private_debug_skips") == 1
                and type(role.get("records")) is list
                and len(role["records"]) == PUBLIC_METHODS,
                "a real two-process Python role lost an original method")
        vector: list[dict[str, Any]] = []
        private_skip_count = 0
        for record in role["records"]:
            require(type(record) is dict and type(record.get("test")) is str
                    and type(record.get("source_ast_sha256")) is str
                    and len(record["source_ast_sha256"]) == 64,
                    "an actual original reference method lost its source identity")
            if record.get("status") == "SKIP":
                require(record.get("test") == PRIVATE_DEBUG_METHOD
                        and record.get("reason") == PRIVATE_DEBUG_REASON
                        and record.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                        and record.get("source_ast_sha256") ==
                        PRIVATE_DEBUG_SOURCE_AST_SHA256,
                        "the authentic named private-debug skip was substituted")
                private_skip_count += 1
            else:
                require(record.get("status") == "PASS",
                        "an original Python reference method was not successful")
            vector.append({
                "test": record["test"],
                "source_ast_sha256": record["source_ast_sha256"],
                "status": record["status"],
                "skip_kind": record.get("skip_kind"),
                "reason": record.get("reason"),
            })
        require(private_skip_count == 1,
                "the original reference concealed a real public skip")
        vectors.append(vector)
    require(vectors[0] == vectors[1],
            "the two genuinely independent original reference vectors disagree")
    expected_vector_sha256 = hashlib.sha256(json.dumps(
        vectors[0], ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii")).hexdigest()
    require(reference.get("reference_status_vector_sha256")
            == expected_vector_sha256,
            "the actual complete original status vector was reordered or changed")
    return [{"test": record["test"]} for record in vectors[0]]


def _validate_qualified_pair(
    qualification: Any, family: str, rows: list[dict[str, Any]],
) -> dict[str, Any]:
    expected = {
        row["kind"]: row for row in rows if row.get("family") == family
    }
    require(set(expected) == {"original", "deeper"}
            and type(qualification) is dict
            and qualification.get("family") == family
            and qualification.get("candidate_module") ==
            "candidates." + ("vm_candidate" if family == "vm"
                             else family + "_candidate")
            and qualification.get("edge_checks") == 223_198
            and qualification.get("edge_categories") == 49
            and qualification.get("deep_checks") == 393
            and qualification.get("deep_seeded_cases") == 64
            and qualification.get("edge_archive_sha256") ==
            expected["original"]["archive_sha256"]
            and qualification.get("edge_proof_sha256") ==
            expected["original"]["proof_sha256"]
            and qualification.get("deep_archive_sha256") ==
            expected["deeper"]["archive_sha256"]
            and qualification.get("deep_proof_sha256") ==
            expected["deeper"]["proof_sha256"]
            and qualification.get("all_family_audit_qualified") is True
            and qualification.get("campaign_qualified") is True
            and qualification.get("performance") == "NOT MEASURED"
            and qualification.get("holdout") == "NOT ACCESSED",
            "an upstream result was not bound to its real same-family proofs")
    native = qualification.get("native_sha256_by_path")
    require(type(native) is dict and bool(native)
            and all(type(path) is str and type(value) is str
                    and len(value) == 64 for path, value in native.items()),
            "the actual upstream native binary graph was omitted")
    return native


def _validate_success(
    family: str,
    label: str,
    report: dict[str, Any],
    report_sha256: str,
    sidecar: dict[str, Any],
    sidecar_sha256: str,
    *,
    matrix: list[dict[str, Any]],
    reference: dict[str, Any],
    rows: list[dict[str, Any]],
    frozen: Any,
    legacy: Any,
) -> dict[str, Any]:
    path = V13_PREFIX + family + ".json"
    receipt_path = V13_PREFIX + family + "-publication-receipt.json"
    require(report.get("schema") == frozen.SCHEMA + "-actual-" + family + "-role"
            and report.get("status") == "PASS"
            and report.get("source_path") == V13_SOURCE_PATH
            and report.get("source_sha256") == V13_SOURCE_SHA256
            and report.get("protocol_path") == V13_PROTOCOL_PATH
            and report.get("protocol_sha256") == V13_PROTOCOL_SHA256
            and report.get("reference_sha256") == V6_REFERENCE_SHA256
            and report.get("immutable_v6_reference_sha256") == V6_REFERENCE_SHA256
            and report.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
            and report.get("synthetic") is False
            and report.get("performance") == "NOT MEASURED"
            and report.get("holdout") == "NOT ACCESSED",
            "a complete official upstream result has not actually been frozen")
    require(sidecar.get("schema") ==
            frozen.SCHEMA + "-actual-durable-success-publication-receipt"
            and sidecar.get("status") == "PASS"
            and sidecar.get("report_path") == path
            and sidecar.get("report_sha256") == report_sha256
            and sidecar.get("production_observations_invented") is False
            and sidecar.get("performance") == "NOT MEASURED"
            and sidecar.get("holdout") == "NOT ACCESSED",
            "the independently durable upstream result receipt is missing")
    receipt = frozen._validate_publication_receipt(
        sidecar.get("actual_exclusive_publication_receipt")
    )
    require(receipt.get("path") == path
            and receipt.get("expected_payload_sha256") == report_sha256
            and receipt.get("actual_file_created") is True
            and receipt.get("actual_file_fsync") is True
            and receipt.get("actual_directory_fsync") is True
            and receipt.get("fully_durable_publication") is True
            and receipt.get("canonical_reread_succeeded") is True,
            "the original upstream result was not actually durably published")
    actual_roles = report.get("roles")
    require(type(actual_roles) is dict and set(actual_roles) == {family},
            "an upstream report omitted or substituted its exact candidate")
    role = actual_roles[family]
    require(type(role) is dict and role.get("applicable") == 151
            and role.get("passed") == 151
            and role.get("named_private_debug_skips") == 1
            and type(role.get("records")) is list
            and len(role["records"]) == PUBLIC_METHODS
            and role.get("actual_cached_matcher_method_guard_checks") == METHOD_GUARDS
            and role.get("actual_native_owner_method_guard_checks") == METHOD_GUARDS,
            "an official upstream result omitted a real original method or guard")
    expected_records = reference["roles"]["reference_a"]["records"]
    private_skips = 0
    for expected, observed in zip(expected_records, role["records"], strict=True):
        require(type(observed) is dict
                and observed.get("test") == expected.get("test")
                and observed.get("source_ast_sha256")
                == expected.get("source_ast_sha256")
                and observed.get("status") == expected.get("status"),
                "an original upstream method changed order, outcome, or identity")
        if observed.get("status") == "SKIP":
            require(observed.get("test") == PRIVATE_DEBUG_METHOD
                    and observed.get("reason") == PRIVATE_DEBUG_REASON
                    and observed.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                    and observed.get("source_ast_sha256")
                    == PRIVATE_DEBUG_SOURCE_AST_SHA256,
                    "an unapproved original upstream method was skipped")
            private_skips += 1
        else:
            require(observed.get("status") == "PASS",
                    "an actual failing upstream method was displayed as passing")
    require(private_skips == 1,
            "the exact sole private-debug upstream skip must remain explicit")
    guards = report.get("actual_native_method_owners")
    require(report.get("actual_native_owner_method_guard_checks") == METHOD_GUARDS
            and report.get("actual_inline_cached_matcher_method_guard_checks")
            == METHOD_GUARDS and type(guards) is list
            and len(guards) == METHOD_GUARDS,
            "an original method lost a before-or-after native/matcher guard")
    native = _validate_qualified_pair(
        report.get("qualified_family_proof"), family, rows,
    )
    module = "candidates." + ("vm_candidate" if family == "vm"
                              else family + "_candidate")

    def validate_owner(observed: Any, owner_family: str,
                       expected_native: Any) -> dict[str, Any]:
        require(owner_family == family and expected_native == native,
                "a real upstream owner belongs to another native engine")
        legacy._validate_owner(observed, family, module)
        require(observed.get("native_binary_sha256") == native
                and observed.get("schema") ==
                "rebar-postfinal-from-scratch-audit-v10-native-owner-worker"
                and observed.get("match_repr_checks") == 2
                and observed.get("persistent_cross_engine_guard") is True,
                "a real per-method owner lost its exact binary or no-delegation guard")
        return observed

    frozen._validate_native_method_trace(family, matrix, guards, native,
                                        validate_owner)
    return {
        "family": family, "label": label, "status": "PASS",
        "completed_methods": PUBLIC_METHODS, "total_methods": PUBLIC_METHODS,
        "passed_methods": 151, "named_private_debug_skips": 1,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "full_official_suite_qualified": True,
        "report_path": path, "report_sha256": report_sha256,
        "receipt_path": receipt_path, "receipt_sha256": sidecar_sha256,
    }


def _failure_progress(details: Any) -> dict[str, Any]:
    require(type(details) is dict,
            "an actual failed upstream worker must preserve its original details")
    stack: list[dict[str, Any]] = [details]
    candidates: list[dict[str, Any]] = []
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        records = current.get("completed_original_method_records")
        if records is None:
            records = current.get("actual_completed_original_method_records")
        count = current.get("completed_original_method_count")
        if count is None:
            count = current.get("actual_completed_original_method_count")
        if type(records) is list and type(count) is int:
            require(len(records) == count and 0 <= count <= PUBLIC_METHODS,
                    "a failed upstream run invented or concealed completed tests")
            candidates.append(current)
        for name in ("actual_worker_failure_details", "actual_nested_worker_failure",
                     "actual_worker_document", "complete_actual_original_worker",
                     "details"):
            nested = current.get(name)
            if type(nested) is dict:
                stack.append(nested)
    require(bool(candidates),
            "a failed upstream run does not prove how many tests actually ran")
    chosen = max(candidates, key=lambda row: row.get(
        "completed_original_method_count",
        row.get("actual_completed_original_method_count", -1),
    ))
    count = chosen.get("completed_original_method_count")
    if count is None:
        count = chosen["actual_completed_original_method_count"]
    owners = chosen.get("actual_completed_native_method_owners")
    if owners is None:
        owners = chosen.get("actual_native_method_owners", [])
    require(type(owners) is list and len(owners) <= METHOD_GUARDS,
            "a failed upstream run invented completed native owners")
    observed_owner_count = chosen.get("actual_native_owner_method_guard_checks")
    if observed_owner_count is not None:
        require(type(observed_owner_count) is int
                and observed_owner_count == len(owners),
                "a failed upstream run changed its actual native-owner count")
    matcher_count = chosen.get("actual_cached_matcher_method_guard_checks", 0)
    require(type(matcher_count) is int and 0 <= matcher_count <= METHOD_GUARDS,
            "a failed upstream run invented matcher-guard observations")
    actual_error = chosen.get("actual_error")
    require(type(actual_error) is str and 0 < len(actual_error) <= 2048,
            "a failed original worker concealed its actual captured cause")
    if actual_error == RUST_V13_SETUP_ERROR:
        require(count == 0 and len(owners) == 0 and matcher_count == 0,
                "the genuine anti-delegation setup failure occurred before all tests")
        classification = "test-harness anti-delegation setup"
    else:
        classification = "failed upstream run; compatibility not qualified"
    return {
        "completed_methods": count, "native_owner_guards": len(owners),
        "cached_matcher_guards": matcher_count,
        "actual_error": actual_error,
        "failure_classification": classification,
    }


def _validate_failure(
    family: str, label: str, document: dict[str, Any], digest: str,
    production_summary: tuple[dict[str, Any], str] | None,
    frozen: Any,
) -> dict[str, Any]:
    path = V13_PREFIX + family + "-failures.json"
    require(document.get("schema") ==
            "rebar-postfinal-cpython-full-public-locale-v13-actual-role-failure"
            and document.get("status") == "FAIL"
            and document.get("role") == family
            and document.get("source_sha256") == V13_SOURCE_SHA256
            and document.get("protocol_sha256") == V13_PROTOCOL_SHA256
            and document.get("immutable_v6_reference_sha256") == V6_REFERENCE_SHA256
            and document.get("actual_failure_destination") == path
            and document.get("synthetic") is False
            and document.get("production_observations_invented") is False
            and document.get("performance") == "NOT MEASURED"
            and document.get("holdout") == "NOT ACCESSED",
            "a genuine frozen, current upstream failure was replaced or hidden")
    progress = _failure_progress(document.get("details"))
    result = {
        "family": family, "label": label, "status": "FAIL",
        "total_methods": PUBLIC_METHODS, **progress,
        "full_official_suite_qualified": False,
        "failure_path": path, "failure_sha256": digest,
    }
    if family == "rust":
        require(digest == RUST_V13_FAILURE_SHA256
                and progress["actual_error"] == RUST_V13_SETUP_ERROR,
                "the independently preserved first Rust setup failure was changed")
        require(production_summary is not None,
                "the exact complete original Rust failure stdout was omitted")
    if production_summary is not None:
        captured, captured_sha256 = production_summary
        summary_path = V13_PREFIX + family + "-failures-production-summary.json"
        require(captured.get("schema") == document["schema"]
                and captured.get("status") == "FAIL"
                and captured.get("role") == family
                and captured.get("source_sha256") == V13_SOURCE_SHA256
                and captured.get("protocol_sha256") == V13_PROTOCOL_SHA256
                and captured.get("immutable_v6_reference_sha256")
                == V6_REFERENCE_SHA256
                and captured.get("synthetic") is False
                and captured.get("production_observations_invented") is False
                and captured.get("performance") == "NOT MEASURED"
                and captured.get("holdout") == "NOT ACCESSED"
                and captured.get("details") == document["details"],
                "the complete original failed controller capture was substituted")
        publications = captured.get("actual_exclusively_preserved_failure_reports")
        require(type(publications) is list and len(publications) == 1,
                "the actual first failed-role publication was hidden or replayed")
        publication = publications[0]
        require(type(publication) is dict
                and publication.get("path") == path
                and publication.get("sha256") == digest,
                "the real failed-role publication was replaced")
        receipt = frozen._validate_publication_receipt(
            publication.get("actual_exclusive_publication_receipt"),
        )
        require(receipt.get("path") == path
                and receipt.get("expected_payload_sha256") == digest
                and receipt.get("actual_file_created") is True
                and receipt.get("actual_file_fsync") is True
                and receipt.get("actual_directory_fsync") is True
                and receipt.get("fully_durable_publication") is True
                and receipt.get("canonical_reread_succeeded") is True,
                "the genuine 11-field failed-role durable receipt was concealed")
        if family == "rust":
            require(captured_sha256 == RUST_V13_FAILURE_SUMMARY_SHA256
                    and receipt.get("expected_payload_bytes") == 9479
                    and receipt.get("actual_payload_bytes_written") == 9479
                    and captured.get("details", {}).get("returncode") == 2,
                    "the exact first Rust setup failure or real receipt changed")
        result.update({
            "failure_summary_path": summary_path,
            "failure_summary_sha256": captured_sha256,
            "actual_durable_failure_receipt_verified": True,
        })
    return result


def _discover_role(
    family: str, label: str, *, matrix: list[dict[str, Any]],
    reference: dict[str, Any], rows: list[dict[str, Any]],
    frozen: Any, legacy: Any, identities: list[dict[str, str]],
) -> dict[str, Any]:
    pass_path = V13_PREFIX + family + ".json"
    fail_path = V13_PREFIX + family + "-failures.json"
    receipt_path = V13_PREFIX + family + "-publication-receipt.json"
    failure_summary_path = V13_PREFIX + family + "-failures-production-summary.json"
    actual_pass = _read_json(pass_path, optional=True)
    actual_failure = _read_json(fail_path, optional=True)
    actual_receipt = _read_json(receipt_path, optional=True)
    actual_failure_summary = _read_json(failure_summary_path, optional=True)
    require(not (actual_pass is not None and actual_failure is not None),
            "a real upstream candidate cannot simultaneously pass and fail")
    if actual_pass is not None:
        require(actual_receipt is not None,
                "a real passing upstream report lacks its durable receipt")
        require(actual_failure_summary is None,
                "a passing upstream role cannot conceal a new failed invocation")
        report, digest = actual_pass
        sidecar, sidecar_digest = actual_receipt
        result = _validate_success(
            family, label, report, digest, sidecar, sidecar_digest,
            matrix=matrix, reference=reference, rows=rows,
            frozen=frozen, legacy=legacy,
        )
        identities.extend((
            {"purpose": family + "-full-upstream-result", "path": pass_path,
             "sha256": digest},
            {"purpose": family + "-full-upstream-durable-receipt",
             "path": receipt_path, "sha256": sidecar_digest},
        ))
        return result
    if actual_failure is not None:
        require(actual_receipt is None,
                "a failed upstream role cannot own a passing success receipt")
        failure, digest = actual_failure
        result = _validate_failure(family, label, failure, digest,
                                   actual_failure_summary, frozen)
        identities.append({"purpose": family + "-actual-upstream-failure",
                           "path": fail_path, "sha256": digest})
        if actual_failure_summary is not None:
            identities.append({
                "purpose": family + "-complete-upstream-failure-capture",
                "path": failure_summary_path,
                "sha256": actual_failure_summary[1],
            })
        return result
    require(actual_receipt is None,
            "an unexecuted upstream role cannot have a success receipt")
    require(actual_failure_summary is None,
            "an unexecuted upstream role cannot have a failure capture")
    return {
        "family": family, "label": label, "status": "NOT RUN",
        "completed_methods": None, "total_methods": PUBLIC_METHODS,
        "native_owner_guards": None, "cached_matcher_guards": None,
        "full_official_suite_qualified": False,
    }


def _snapshot() -> tuple[dict[str, Any], list[dict[str, str]]]:
    legacy = _frozen_module(V1_SOURCE_PATH, V1_SOURCE_SHA256,
                            "_rebar_frozen_current_correctness_v1")
    frozen = _frozen_module(V13_SOURCE_PATH, V13_SOURCE_SHA256,
                            "_rebar_frozen_full_upstream_v13")
    protocol = _read_regular(V13_PROTOCOL_PATH)
    require(protocol is not None
            and hashlib.sha256(protocol).hexdigest() == V13_PROTOCOL_SHA256
            and frozen.SCHEMA == "rebar-postfinal-cpython-full-public-locale-v13"
            and frozen.SOURCE_RELATIVE == V13_SOURCE_PATH
            and frozen.PROTOCOL_RELATIVE == V13_PROTOCOL_PATH
            and frozen.PROTOCOL_SHA256 == V13_PROTOCOL_SHA256
            and frozen.V6_REFERENCE_SHA256 == V6_REFERENCE_SHA256
            and frozen.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
            and frozen.PUBLIC_METHODS == PUBLIC_METHODS
            and tuple(frozen.FAMILIES) == tuple(name for name, _ in FAMILIES),
            "the complete frozen original upstream validator was substituted")
    snapshot, identities = legacy._load_snapshot()
    reference = legacy._checked_json(legacy.REFERENCE_PATH,
                                     legacy.REFERENCE_SHA256)
    matrix = _validate_matrix(reference, frozen, legacy)
    identities = [copy.deepcopy(item) for item in identities]
    identities.extend((
        {"purpose": "frozen-v1-original-evidence-validator",
         "path": V1_SOURCE_PATH, "sha256": V1_SOURCE_SHA256},
        {"purpose": "frozen-current-full-upstream-validator",
         "path": V13_SOURCE_PATH, "sha256": V13_SOURCE_SHA256},
        {"purpose": "frozen-current-full-upstream-protocol",
         "path": V13_PROTOCOL_PATH, "sha256": V13_PROTOCOL_SHA256},
    ))
    historical = copy.deepcopy(snapshot["full_python_suite"][0])
    require(historical.get("family") == "rust"
            and historical.get("status") == "STOPPED BEFORE TESTS"
            and historical.get("completed_methods") == 0
            and historical.get("cause") == "test-harness bridge wiring",
            "the actual immutable historical first harness failure was concealed")
    snapshot = copy.deepcopy(snapshot)
    snapshot["historical_v12_rust_upstream_failure"] = historical
    snapshot["full_python_suite"] = [
        _discover_role(
            family, label, matrix=matrix, reference=reference,
            rows=snapshot["rows"], frozen=frozen, legacy=legacy,
            identities=identities,
        )
        for family, label in FAMILIES
    ]
    snapshot["official_suite_candidate_passes"] = sum(
        row["status"] == "PASS" for row in snapshot["full_python_suite"]
    )
    snapshot["full_drop_in_compatibility"] = "NOT ESTABLISHED"
    return snapshot, sorted(identities, key=lambda item: item["path"])


def _text(x: int, y: int, value: str, css: str = "body") -> str:
    return (f'<text x="{x}" y="{y}" class="{css}">'
            + html.escape(value) + "</text>")


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    require(snapshot.get("candidate_count") == 3
            and snapshot.get("original_candidate_checks") == 669_594
            and snapshot.get("deeper_candidate_checks") == 1_179
            and snapshot.get("observed_original_or_deeper_mismatches") == 0
            and snapshot.get("full_drop_in_compatibility") == "NOT ESTABLISHED"
            and snapshot.get("performance") == "NOT MEASURED"
            and snapshot.get("holdout") == "NOT ACCESSED",
            "a chart invented candidate coverage, compatibility, or performance")
    rows = snapshot.get("rows")
    require(type(rows) is list and len(rows) == 6
            and all(type(row) is dict and row.get("status") == "PASS"
                    and row.get("passed") == row.get("total")
                    and row.get("mismatches") == 0 for row in rows),
            "a chart concealed an original or deeper candidate mismatch")
    history = snapshot.get("historical_v12_rust_upstream_failure")
    require(type(history) is dict and history.get("family") == "rust"
            and history.get("status") == "STOPPED BEFORE TESTS"
            and history.get("completed_methods") == 0
            and history.get("cause") == "test-harness bridge wiring",
            "the actual historical harness failure was hidden or relabeled")
    suite = snapshot.get("full_python_suite")
    require(type(suite) is list and len(suite) == 3
            and tuple(row.get("family") for row in suite)
            == tuple(name for name, _ in FAMILIES),
            "a current candidate family is missing or counted twice")
    passed = 0
    for row in suite:
        require(type(row) is dict and row.get("total_methods") == PUBLIC_METHODS
                and row.get("status") in {"PASS", "FAIL", "NOT RUN"},
                "an upstream result invented a new denominator or status")
        if row["status"] == "PASS":
            require(row.get("full_official_suite_qualified") is True
                    and row.get("completed_methods") == PUBLIC_METHODS
                    and row.get("passed_methods") == 151
                    and row.get("named_private_debug_skips") == 1
                    and row.get("native_owner_guards") == METHOD_GUARDS
                    and row.get("cached_matcher_guards") == METHOD_GUARDS,
                    "an upstream pass lost its actual 152 methods or 304 guards")
            passed += 1
        elif row["status"] == "FAIL":
            require(row.get("full_official_suite_qualified") is False
                    and type(row.get("completed_methods")) is int
                    and 0 <= row["completed_methods"] <= PUBLIC_METHODS
                    and type(row.get("native_owner_guards")) is int
                    and 0 <= row["native_owner_guards"] <= METHOD_GUARDS,
                    "a failed current role was displayed as fully qualified")
            if row.get("failure_classification") == (
                    "test-harness anti-delegation setup"):
                require(row.get("family") == "rust"
                        and row.get("actual_error") == RUST_V13_SETUP_ERROR
                        and row.get("completed_methods") == 0
                        and row.get("native_owner_guards") == 0
                        and row.get("cached_matcher_guards") == 0,
                        "a pre-test anti-delegation failure was falsely relabeled")
        else:
            require(row.get("full_official_suite_qualified") is False
                    and row.get("completed_methods") is None
                    and row.get("native_owner_guards") is None,
                    "an unexecuted candidate was given invented observations")
    require(snapshot.get("official_suite_candidate_passes") == passed,
            "the full-upstream headline changed its actual all-family count")


def render_svg(snapshot: dict[str, Any]) -> bytes:
    _validate_snapshot(snapshot)
    passed = snapshot["official_suite_candidate_passes"]
    suite = snapshot["full_python_suite"]
    description = (
        "Three independently written Rust, C and Zig engines each passed all "
        "223,198 original and 393 deeper correctness checks. "
        + str(passed) + " of 3 engines have passed all 152 original Python "
        "test methods, including 151 passes and one genuine debug-only skip. "
        "The first historical Rust harness failure remains preserved. "
        "Speed and memory are not measured."
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" '
        'viewBox="0 0 1200 1200" role="img" aria-labelledby="title description">',
        '<title id="title">How close are we to replacing Python’s re?</title>',
        '<desc id="description">' + html.escape(description) + '</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        "'Segoe UI',sans-serif}.title{font-size:36px;font-weight:760;fill:#10223b}"
        '.subtitle{font-size:16px;fill:#43536b}.metric{font-size:31px;'
        'font-weight:750;fill:#10223b}.metric-label{font-size:14px;fill:#43536b}'
        '.heading{font-size:22px;font-weight:720;fill:#10223b}.body{font-size:'
        '15px;fill:#25364e}.small{font-size:13px;fill:#43536b}.strong{font-size:'
        '16px;font-weight:720;fill:#10223b}.pass{font-size:14px;font-weight:720;'
        'fill:#116139}.warning{font-size:14px;font-weight:720;fill:#8a4b08}'
        '.pending{font-size:14px;font-weight:720;fill:#485870}.footer{font-size:'
        '15px;font-weight:650;fill:#25364e}</style>',
        '<rect width="1200" height="1200" rx="20" fill="#f5f8fc"/>',
        _text(54, 74, "How close are we to replacing Python’s re?", "title"),
        _text(56, 106,
              "Current from-scratch engines · fairly checked against Python 3.14.6",
              "subtitle"),
    ]
    cards = ((54, "3", "independent engines"),
             (338, "669,594", "original candidate-checks"),
             (622, "1,179", "deeper candidate-checks"),
             (906, "0", "observed mismatches"))
    for x, value, label in cards:
        parts.extend((
            f'<rect x="{x}" y="135" width="240" height="95" rx="14" '
            'fill="#ffffff" stroke="#dce5ef"/>',
            _text(x + 17, 176, value, "metric"),
            _text(x + 17, 205, label, "metric-label"),
        ))
    parts.extend((_text(56, 272, "Original correctness checks", "heading"),
                  _text(56, 295,
                        "The same 223,198 cases for every engine · 49 categories",
                        "small")))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 316 + index * 47
        parts.extend((
            _text(66, y + 21, label, "strong"),
            f'<rect x="158" y="{y}" width="690" height="27" rx="8" '
            'fill="#17844e"/>',
            _text(863, y + 20, "223,198 / 223,198", "strong"),
            _text(1075, y + 20, "100%", "pass"),
        ))
    parts.extend((_text(56, 500, "Deeper correctness checks", "heading"),
                  _text(56, 523,
                        "The same 393 difficult cases · including 64 fixed-seed cases",
                        "small")))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 544 + index * 47
        parts.extend((
            _text(66, y + 21, label, "strong"),
            f'<rect x="158" y="{y}" width="690" height="27" rx="8" '
            'fill="#17844e"/>',
            _text(863, y + 20, "393 / 393", "strong"),
            _text(1075, y + 20, "100%", "pass"),
        ))
    parts.extend((
        _text(56, 726, "Current complete Python test suite", "heading"),
        _text(56, 748,
              "Each pass must cover 152 original methods and 304 independent "
              "native-owner checks.", "small"),
    ))
    for index, row in enumerate(suite):
        x = (54, 437, 820)[index]
        status = row["status"]
        if status == "PASS":
            fill, stroke, css = "#edf8f1", "#badeca", "pass"
            count = "151 passed + 1 debug-only skip"
            detail = "304 / 304 independent owner checks"
        elif status == "FAIL":
            fill, stroke, css = "#fff8eb", "#f2d199", "warning"
            count = (f'{row["completed_methods"]} / 152 tests; '
                     f'{row["native_owner_guards"]} / 304 owners')
            if row.get("failure_classification") == (
                    "test-harness anti-delegation setup"):
                status = "SETUP FAILED BEFORE TESTS"
                detail = "Anti-delegation setup; not a regex mismatch"
            else:
                detail = "Original upstream suite not qualified"
        else:
            fill, stroke, css = "#f1f4f9", "#d9e1ec", "pending"
            count = "152 original tests not yet run"
            detail = "No compatibility result claimed"
        parts.extend((
            f'<rect x="{x}" y="767" width="326" height="124" rx="13" '
            f'fill="{fill}" stroke="{stroke}"/>',
            _text(x + 17, 797, row["label"], "strong"),
            _text(x + 17, 821, status, css),
            _text(x + 17, 848, count, "body"),
            _text(x + 17, 873, detail, "small"),
        ))
    parts.extend((
        _text(56, 936,
              "Preserved test-harness failures — not proven regex mismatches",
              "heading"),
        '<rect x="54" y="951" width="1092" height="73" rx="12" '
        'fill="#fff8eb" stroke="#f2d199"/>',
        _text(72, 979,
              "Earlier Rust attempt: missing bridge wiring; 0 / 152 original "
              "Python tests reached.", "body"),
        _text(72, 1002,
              ("Current Rust attempt: anti-delegation setup stopped before the "
               "first test; 0 / 152 reached."
               if any(row.get("failure_classification") ==
                      "test-harness anti-delegation setup" for row in suite)
               else "That earlier harness failure remains preserved and is "
               "never counted as a current result."),
              "small"),
        '<rect x="54" y="1047" width="1092" height="106" rx="12" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(72, 1078,
              f"Overall: {passed} / 3 engines have passed the complete original "
              "Python test suite.", "footer"),
        _text(72, 1104,
              "Full drop-in compatibility is NOT ESTABLISHED until every frozen "
              "public check also passes.", "small"),
        _text(72, 1129,
              "Speed and memory: NOT MEASURED · final holdout: NOT ACCESSED.",
              "small"),
        '</svg>\n',
    ))
    return "\n".join(parts).encode("utf-8")


def _bundle() -> tuple[bytes, bytes, dict[str, Any]]:
    snapshot, inputs = _snapshot()
    svg = render_svg(snapshot)
    manifest = {
        "schema": SCHEMA + "-manifest", "status": "PASS",
        "generator_path": SOURCE_PATH,
        "chart_path": CHART_PATH,
        "chart_sha256": hashlib.sha256(svg).hexdigest(),
        "chart_bytes": len(svg),
        "validated_input_count": len(inputs),
        "validated_inputs": inputs,
        "snapshot": snapshot,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return svg, canonical(manifest), manifest


def _exclusive_publish(name: str, payload: bytes, directory: int) -> str:
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = os.open(name, flags, 0o644, dir_fd=directory)
    except FileExistsError:
        descriptor = os.open(
            name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory,
        )
        try:
            require(stat.S_ISREG(os.fstat(descriptor).st_mode),
                    "an existing chart is not a safe regular file")
            pieces: list[bytes] = []
            while True:
                piece = os.read(descriptor, 1024 * 1024)
                if not piece:
                    break
                pieces.append(piece)
            require(b"".join(pieces) == payload,
                    "refusing to overwrite a different existing V2 chart")
        finally:
            os.close(descriptor)
        return "EXISTING IDENTICAL"
    try:
        sent = 0
        while sent < len(payload):
            count = os.write(descriptor, payload[sent:])
            require(type(count) is int and count > 0,
                    "a genuine exclusive V2 chart write failed")
            sent += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.fsync(directory)
    return "EXCLUSIVELY CREATED"


def _write(svg: bytes, manifest: bytes) -> dict[str, str]:
    flags = (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    root = os.open(str(ROOT), flags)
    docs = -1
    evidence = -1
    try:
        docs = os.open("docs", flags, dir_fd=root)
        evidence = os.open("evidence", flags, dir_fd=docs)
        return {
            "chart": _exclusive_publish("current-native-correctness-v2.svg",
                                         svg, evidence),
            "manifest": _exclusive_publish("current-native-correctness-v2.json",
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
    restored: list[tuple[Any, str, Any]] = []

    def deny(counter: str, reason: str) -> Callable[..., Any]:
        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            effects[counter] += 1
            raise ChartError(reason)
        return blocked

    def patch(owner: Any, field: str, replacement: Any) -> None:
        if hasattr(owner, field):
            restored.append((owner, field, getattr(owner, field)))
            setattr(owner, field, replacement)

    reject_read = deny("blocked_file_reads", "synthetic controls cannot read evidence")
    reject_write = deny("blocked_file_writes", "synthetic controls cannot write")
    reject_import = deny("blocked_candidate_imports", "synthetic controls cannot import")
    reject_worker = deny("blocked_workers", "synthetic controls cannot start workers")
    reject_thread = deny("blocked_threads", "synthetic controls cannot start threads")
    reject_clock = deny("blocked_clock_samples", "synthetic controls cannot time")
    try:
        patch(builtins, "open", reject_read)
        patch(io, "open", reject_read)
        for name in ("open", "read_bytes", "read_text", "exists", "stat",
                     "is_file", "is_dir", "glob", "rglob", "iterdir"):
            patch(Path, name, reject_read)
        for name in ("open", "stat", "lstat", "listdir", "scandir"):
            patch(os, name, reject_read)
        for name in ("write", "fsync", "mkdir", "makedirs", "replace",
                     "rename", "remove", "unlink"):
            patch(os, name, reject_write)
        for name in ("write_bytes", "write_text"):
            patch(Path, name, reject_write)
        patch(subprocess, "run", reject_worker)
        patch(subprocess, "Popen", reject_worker)
        patch(os, "fork", reject_worker)
        patch(multiprocessing.Process, "start", reject_worker)
        patch(threading.Thread, "start", reject_thread)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            patch(time, name, reject_clock)
        patch(importlib, "import_module", reject_import)
        patch(builtins, "__import__", reject_import)
        yield effects
    finally:
        for owner, field, previous in reversed(restored):
            setattr(owner, field, previous)


def _synthetic_snapshot(statuses: tuple[str, str, str]) -> dict[str, Any]:
    rows = []
    for kind, count in (("original", 223_198), ("deeper", 393)):
        for family, label in FAMILIES:
            rows.append({"family": family, "label": label, "kind": kind,
                         "status": "PASS", "passed": count,
                         "total": count, "mismatches": 0})
    current: list[dict[str, Any]] = []
    for (family, label), status in zip(FAMILIES, statuses, strict=True):
        if status == "PASS":
            current.append({
                "family": family, "label": label, "status": "PASS",
                "completed_methods": PUBLIC_METHODS,
                "total_methods": PUBLIC_METHODS, "passed_methods": 151,
                "named_private_debug_skips": 1,
                "native_owner_guards": METHOD_GUARDS,
                "cached_matcher_guards": METHOD_GUARDS,
                "full_official_suite_qualified": True,
            })
        elif status == "FAIL":
            current.append({
                "family": family, "label": label, "status": "FAIL",
                "completed_methods": 17, "total_methods": PUBLIC_METHODS,
                "native_owner_guards": 35, "cached_matcher_guards": 35,
                "full_official_suite_qualified": False,
            })
        else:
            current.append({
                "family": family, "label": label, "status": "NOT RUN",
                "completed_methods": None, "total_methods": PUBLIC_METHODS,
                "native_owner_guards": None, "cached_matcher_guards": None,
                "full_official_suite_qualified": False,
            })
    return {
        "candidate_count": 3, "original_candidate_checks": 669_594,
        "deeper_candidate_checks": 1_179,
        "observed_original_or_deeper_mismatches": 0, "rows": rows,
        "historical_v12_rust_upstream_failure": {
            "family": "rust", "status": "STOPPED BEFORE TESTS",
            "completed_methods": 0, "cause": "test-harness bridge wiring",
        },
        "full_python_suite": current,
        "official_suite_candidate_passes": sum(value == "PASS" for value in statuses),
        "full_drop_in_compatibility": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def _self_test() -> dict[str, Any]:
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "candidate-free visualization controls cannot import an engine")
    accepted = 0
    rejected = 0

    def reject(action: Callable[[], Any], description: str) -> None:
        nonlocal rejected
        try:
            action()
        except (ChartError, OSError, ValueError, TypeError, KeyError, ImportError):
            rejected += 1
        else:
            raise ChartError("accepted invalid candidate-free control: " + description)

    with _source_only_boundary() as effects:
        for statuses in (
            ("NOT RUN", "NOT RUN", "NOT RUN"),
            ("PASS", "NOT RUN", "NOT RUN"),
            ("PASS", "PASS", "NOT RUN"),
            ("PASS", "PASS", "PASS"),
            ("FAIL", "NOT RUN", "NOT RUN"),
            ("PASS", "FAIL", "NOT RUN"),
            ("PASS", "PASS", "FAIL"),
        ):
            synthetic = _synthetic_snapshot(statuses)
            image = render_svg(synthetic)
            require(image == render_svg(copy.deepcopy(synthetic))
                    and image.startswith(b"<svg ")
                    and image.endswith(b"</svg>\n")
                    and b"669,594" in image and b"1,179" in image
                    and image.count(b"223,198 / 223,198") == 3
                    and image.count(b"393 / 393") == 3
                    and b"Preserved test-harness failures" in image
                    and b"NOT MEASURED" in image
                    and b"NOT ACCESSED" in image,
                    "a synthetic all-family chart is not faithful or deterministic")
            accepted += 1
        setup_failure = _synthetic_snapshot(("FAIL", "NOT RUN", "NOT RUN"))
        setup_failure["full_python_suite"][0].update({
            "completed_methods": 0, "native_owner_guards": 0,
            "cached_matcher_guards": 0,
            "actual_error": RUST_V13_SETUP_ERROR,
            "failure_classification": "test-harness anti-delegation setup",
        })
        setup_image = render_svg(setup_failure)
        require(b"SETUP FAILED BEFORE TESTS" in setup_image
                and b"Anti-delegation setup; not a regex mismatch" in setup_image
                and b"Earlier Rust attempt: missing bridge wiring" in setup_image
                and b"Current Rust attempt: anti-delegation setup" in setup_image
                and b"0 / 152 tests; 0 / 304 owners" in setup_image,
                "the two independently preserved Rust setup failures were concealed")
        accepted += 1
        for field, forged in (("actual_error", "invented regex mismatch"),
                              ("completed_methods", 1),
                              ("native_owner_guards", 1),
                              ("cached_matcher_guards", 1)):
            changed = copy.deepcopy(setup_failure)
            changed["full_python_suite"][0][field] = forged
            reject(lambda changed=changed: render_svg(changed),
                   "fabricated anti-delegation setup failure " + field)
        valid = _synthetic_snapshot(("PASS", "NOT RUN", "NOT RUN"))
        for key, forged in (
            ("candidate_count", 2),
            ("original_candidate_checks", 669_593),
            ("deeper_candidate_checks", 1_178),
            ("observed_original_or_deeper_mismatches", 1),
            ("official_suite_candidate_passes", 3),
            ("full_drop_in_compatibility", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "ACCESSED"),
        ):
            changed = copy.deepcopy(valid)
            changed[key] = forged
            reject(lambda changed=changed: render_svg(changed), key)
        for index in range(6):
            for field, forged in (("status", "FAIL"), ("mismatches", 1),
                                  ("passed", valid["rows"][index]["total"] - 1)):
                changed = copy.deepcopy(valid)
                changed["rows"][index][field] = forged
                reject(lambda changed=changed: render_svg(changed),
                       "concealed original or deeper mismatch")
        for field, forged in (
            ("completed_methods", 151), ("passed_methods", 152),
            ("named_private_debug_skips", 0), ("native_owner_guards", 303),
            ("cached_matcher_guards", 303),
            ("full_official_suite_qualified", False),
            ("total_methods", 151),
        ):
            changed = copy.deepcopy(valid)
            changed["full_python_suite"][0][field] = forged
            reject(lambda changed=changed: render_svg(changed), field)
        for index in (1, 2):
            for field, forged in (("status", "PASS"),
                                  ("completed_methods", 152),
                                  ("native_owner_guards", 304),
                                  ("full_official_suite_qualified", True)):
                changed = copy.deepcopy(valid)
                changed["full_python_suite"][index][field] = forged
                reject(lambda changed=changed: render_svg(changed),
                       "invented unexecuted role " + field)
        for field, forged in (("status", "PASS"),
                              ("completed_methods", 152),
                              ("cause", "regex incompatibility")):
            changed = copy.deepcopy(valid)
            changed["historical_v12_rust_upstream_failure"][field] = forged
            reject(lambda changed=changed: render_svg(changed),
                   "concealed historical harness failure " + field)
        reject(lambda: builtins.open(V13_PREFIX + "rust.json", "rb"),
               "read actual in-progress original evidence")
        reject(lambda: os.open(V13_PREFIX + "rust.json", os.O_RDONLY),
               "descriptor-read actual in-progress evidence")
        reject(lambda: (ROOT / V13_SOURCE_PATH).read_bytes(),
               "read actual upstream controller during synthetic controls")
        reject(lambda: (ROOT / "performance").exists(),
               "inspect actual performance or holdout")
        reject(lambda: importlib.import_module("candidates.rust_candidate"),
               "import a candidate")
        reject(lambda: builtins.__import__("candidates.zig_candidate"),
               "builtin-import a candidate")
        reject(lambda: subprocess.run(["a-production-worker"]),
               "execute a production worker")
        reject(lambda: threading.Thread(target=lambda: None).start(),
               "start a background worker")
        reject(time.perf_counter, "sample a performance clock")
        reject(lambda: (ROOT / CHART_PATH).write_bytes(b"fabricated"),
               "publish an unauthorized synthetic chart")
        actual_effect_keys = (
            "file_reads", "file_writes", "candidate_imports", "workers",
            "threads", "clock_samples", "holdout_cases_read",
            "performance_fixtures_read",
        )
        require(all(effects[key] == 0 for key in actual_effect_keys),
                "a candidate-free synthetic chart had an actual external effect")
        require(effects["blocked_file_reads"] >= 4
                and effects["blocked_file_writes"] >= 1
                and effects["blocked_candidate_imports"] >= 2
                and effects["blocked_workers"] >= 1
                and effects["blocked_threads"] >= 1
                and effects["blocked_clock_samples"] >= 1,
                "the source-only chart boundary did not actually block production")
        preserved = dict(effects)
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "synthetic_only": True, "accepted_controls": accepted,
        "rejected_controls": rejected, "total_controls": accepted + rejected,
        "actual_v13_results_read": 0, "actual_candidate_results_qualified": 0,
        "frozen_v1_source_sha256": V1_SOURCE_SHA256,
        "frozen_v13_source_sha256": V13_SOURCE_SHA256,
        "frozen_v13_protocol_sha256": V13_PROTOCOL_SHA256,
        "effects": preserved,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the complete authenticated current regex correctness chart."
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
            svg, manifest, document = _bundle()
            if options.write:
                publication = _write(svg, manifest)
            else:
                chart = _read_regular(CHART_PATH)
                receipt = _read_regular(MANIFEST_PATH)
                require(chart == svg and receipt == manifest,
                        "the existing V2 chart and manifest cannot be reproduced")
                publication = {"chart": "VERIFIED", "manifest": "VERIFIED"}
            result = {
                "schema": SCHEMA + ("-write" if options.write else "-check"),
                "status": "PASS", "chart_path": CHART_PATH,
                "chart_sha256": document["chart_sha256"],
                "manifest_path": MANIFEST_PATH,
                "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
                "validated_input_count": document["validated_input_count"],
                "full_upstream_candidate_passes": document["snapshot"][
                    "official_suite_candidate_passes"
                ],
                "publication": publication,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            }
    except (ChartError, OSError, AssertionError, ValueError, TypeError,
            KeyError, MemoryError) as error:
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
