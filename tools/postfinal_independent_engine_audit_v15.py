#!/usr/bin/env python3
"""Independently audit the actual current Rust, C, and Zig native engines."""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_current_build_proofs_v11 as v11
from tools import postfinal_current_build_proofs_v12 as v12
from tools import postfinal_from_scratch_audit_v10 as original_owner
from tools import postfinal_no_delegation_audit_v10 as original_strict
from tools import postfinal_independent_engine_audit_v13 as failed_v13


SCHEMA = "rebar-postfinal-independent-engine-audit-v15"
BASE_SCHEMA = "rebar-postfinal-from-scratch-audit-v15"
STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v15"
SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v15.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V15.md"
PROTOCOL_SHA256 = "d8e74273945f0047513e7a720183d8b2cd866cbb31911510a16bc64d5219c1f3"
BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V15.json"
BASE_FAILURE_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V15-FAILURES.json"
STRICT_REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V15.json"
STRICT_FAILURE_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V15-FAILURES.json"
V10_OWNER_SOURCE_SHA256 = "0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505"
V10_STRICT_SOURCE_SHA256 = "885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95"
V10_PROTOCOL_SHA256 = "902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6"
V11_SOURCE_SHA256 = "2895dd28b3dc69985cc0f6f8575398e8b8b10f58141f0612645a687478da9f04"
V12_SOURCE_SHA256 = "81a519fa4890d5a7f6901d58c9154711be116fd7de4b081c0c052d64db481b3f"
V12_PROTOCOL_SHA256 = "f74ccaf19f836f801de34aaf3228f9bcd14aabe88032ebee4dbe886247ec6b40"
V13_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v13.py"
V13_SOURCE_SHA256 = "4570798942ab884c1a760b9685ef1a67379febd1c0da81aa18eef221126758fe"
V13_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V13.md"
V13_PROTOCOL_SHA256 = "f325fe84dc4d14363e3dd4a6038866d8bc2aacd59625231f7dffc4c73257c0c3"
V13_FIRST_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V13-HISTORICAL-GRAPH-PREFLIGHT-FAILURE.json"
)
V13_FIRST_FAILURE_SHA256 = "465820b50be4d544199844d7bde4c5b8e58391828bdb1c716cc33c50ca6c964b"
V13_FIRST_FAILURE_SCHEMA = (
    "rebar-postfinal-independent-engine-audit-v13-actual-historical-graph-preflight-failure"
)
V13_FIRST_FAILURE_MESSAGE = "the ZIG native-bridge is stale or unproven"
ACTUAL_V10_BASE_REPORT_SHA256 = "589321a768e10c52f039a68acb211574ec884598771ede2152f91994cc69f353"
ACTUAL_V10_STRICT_REPORT_SHA256 = "d8f31dd480bdba530a454b38428a23ef347c6e3cce7796f8992d6e7767381f4b"
ZIG_INVALIDATED_RELATIVE = (
    "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-"
    "POSTFINAL-CURRENT-BUILD-V12-INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
)
ZIG_INVALIDATED_SHA256 = "d7f11c33a010406db1637e0715e72bfebdc13acf21118735b6b1f6e550927865"
ZIG_PRODUCER_FAILURE_RELATIVE = (
    "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-"
    "POSTFINAL-CURRENT-BUILD-V12-PRODUCER-CRASH.json.gz"
)
ZIG_PRODUCER_FAILURE_SHA256 = "5c3e07d9f11d5c8244d3d22fc94f287f4f0573423bf38e70b6abc383c96eca90"
ZIG_RETRY_FAILURE_RELATIVE = (
    "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-"
    "POSTFINAL-CURRENT-BUILD-V12-RETRY-FAIL-PROOF.json"
)
ZIG_RETRY_FAILURE_SHA256 = "b5deb6c3ce522fe0dbc3c4e723867ffe830520f0a47a0b72cc5b1d9a0a69ad9d"
CORE_FAMILIES = tuple(original_owner.CORE_FAMILIES)
OWNED_SOURCE_PATHS = dict(original_owner.OWNED_SOURCE_PATHS)
OWNED_NATIVE_PATHS = dict(original_owner.OWNED_NATIVE_PATHS)
MAX_REPORT_BYTES = original_owner.MAX_REPORT_BYTES
MAX_SOURCE_BYTES = original_owner.MAX_SOURCE_BYTES


class AuditV15Error(AssertionError):
    """Real current ownership, independent matching, or immutable history failed."""


class AuditV15PublicationFailure(AuditV15Error):
    """Retain only the actually observed exclusive-publication system calls."""

    def __init__(self, message: str, receipt: Mapping[str, Any]):
        super().__init__(message)
        self.receipt = dict(receipt)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV15Error(message)


def canonical(document: Mapping[str, Any]) -> bytes:
    require(isinstance(document, Mapping), "a complete V15 report must be a JSON object")
    return original_owner.core.canonical(document) + b"\n"


def verify_runtime_source_only() -> None:
    v11.verify_runtime()
    original_owner.verify_runtime()
    original_strict.verify_runtime()
    original_owner.core.ensure_candidate_free()
    require(ROOT == v11.ROOT == original_owner.ROOT == original_strict.ROOT
            and Path(__file__).resolve() == ROOT / SOURCE_RELATIVE
            and tuple(CORE_FAMILIES) == ("rust", "vm", "zig")
            and original_strict.independent is original_owner
            and original_owner.PROTOCOL_SHA256 == V10_PROTOCOL_SHA256
            and original_owner.PROTOCOL_RELATIVE
            == "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md"
            and len(OWNED_SOURCE_PATHS) == 3 and len(OWNED_NATIVE_PATHS) == 3
            and sum(map(len, OWNED_SOURCE_PATHS.values())) == 12
            and sum(map(len, OWNED_NATIVE_PATHS.values())) == 5,
            "V15 requires the genuine pinned isolated CPython and full V10 owner")


def validate_parent_environment(environment: Mapping[str, Any]) -> dict[str, str]:
    require(isinstance(environment, Mapping), "the real V15 parent environment is missing")
    expected = {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
    }
    for name, value in expected.items():
        require(type(environment.get(name)) is str
                and environment.get(name) == value,
                "V15 requires the exact real isolated parent environment: " + name)
    require(Path(expected["PYTHONPATH"]).resolve() == ROOT,
            "the genuine V15 parent root is not exact and canonical")
    return expected


def verify_production_runtime() -> dict[str, str]:
    verify_runtime_source_only()
    return validate_parent_environment(os.environ)


def authenticate_controller() -> dict[str, str]:
    verify_runtime_source_only()
    source = v11.read_regular(ROOT / SOURCE_RELATIVE, "exact actual frozen V15 audit source")
    v11.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    for relative, digest in (
        (original_owner.SOURCE_RELATIVE, V10_OWNER_SOURCE_SHA256),
        (original_strict.SOURCE_RELATIVE, V10_STRICT_SOURCE_SHA256),
        (original_owner.PROTOCOL_RELATIVE, V10_PROTOCOL_SHA256),
        (v11.SOURCE_RELATIVE, V11_SOURCE_SHA256),
        (v12.SOURCE_RELATIVE, V12_SOURCE_SHA256),
        (v12.PROTOCOL_RELATIVE, V12_PROTOCOL_SHA256),
        (V13_SOURCE_RELATIVE, V13_SOURCE_SHA256),
        (V13_PROTOCOL_RELATIVE, V13_PROTOCOL_SHA256),
        (v11.V8_PROOF_RELATIVE, v11.V8_PROOF_SHA256),
        (v11.EDGE_SOURCE_RELATIVE, v11.EDGE_SOURCE_SHA256),
        (v11.DEEP_SOURCE_RELATIVE, v11.DEEP_SOURCE_SHA256),
        (v11.DEEP_RUNNER_RELATIVE, v11.DEEP_RUNNER_SHA256),
        (v11.STAGE07_RELATIVE, v11.STAGE07_SHA256),
    ):
        v11.authenticate_frozen(relative, digest)
    require(Path(original_owner.__file__).resolve()
            == ROOT / original_owner.SOURCE_RELATIVE
            and Path(original_strict.__file__).resolve()
            == ROOT / original_strict.SOURCE_RELATIVE
            and Path(v11.__file__).resolve() == ROOT / v11.SOURCE_RELATIVE
            and Path(v12.__file__).resolve() == ROOT / v12.SOURCE_RELATIVE
            and Path(failed_v13.__file__).resolve() == ROOT / V13_SOURCE_RELATIVE,
            "the original failed V13 or genuine frozen native dependency was substituted")
    original_owner.validate_worker_source()
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": PROTOCOL_SHA256,
    }

def validate_native_owner(
    record: Any,
    family: str,
    expected_native: Mapping[str, str],
) -> dict[str, Any]:
    require(family in CORE_FAMILIES
            and isinstance(expected_native, Mapping)
            and set(expected_native) == set(OWNED_NATIVE_PATHS[family].values()),
            "the exact original independent V15 family/native owner is required")
    actual = original_owner.validate_worker(record, family, dict(expected_native))
    v11.validate_owner(original_owner, actual, family, expected_native)
    require(actual.get("schema") == original_owner.SCHEMA + "-native-owner-worker"
            and actual.get("match_repr_checks") == 2
            and actual.get("standard_pickle_check_count") == 16
            and actual.get("standard_pickle_failure_count") == 0
            and actual.get("regex_guard_count") == 13
            and actual.get("native_loader_guard_count") == 5
            and actual.get("persistent_cross_engine_guard") is True
            and actual.get("genuine_matching_executed") is True
            and actual.get("external_regex_packages") == 0
            and actual.get("benchmark_or_timing_executed") is False
            and actual.get("holdout_or_case_fixture_access") is False,
            "a real V15 native owner weakened matching, representation, or no-delegation")
    return actual


def run_native_worker(family: str, expected_native: Mapping[str, str]) -> dict[str, Any]:
    verify_production_runtime()
    require(family in CORE_FAMILIES
            and isinstance(expected_native, Mapping),
            "a genuine current V15 original native owner must select one real family")
    actual = original_owner.run_native_worker(family, dict(expected_native))
    original_owner.core.ensure_candidate_free()
    return validate_native_owner(actual, family, expected_native)


def full_graph(document: Mapping[str, Any]) -> dict[str, Any]:
    graph = original_owner.source_v6._validate_fresh_graph(document)
    source_by_family: dict[str, dict[str, str]] = {}
    families = document.get("families")
    require(isinstance(families, dict), "the actual V15 independent source graph is absent")
    for family in CORE_FAMILIES:
        row = families.get(family)
        require(isinstance(row, dict), "the exact current parser family is absent: " + family)
        public = row.get("python_source")
        native_sources = row.get("native_sources")
        require(isinstance(public, dict) and isinstance(native_sources, list),
                "a genuine current parser/compiler/executor was omitted: " + family)
        entries = [public, *native_sources]
        actual: dict[str, str] = {}
        for item in entries:
            require(isinstance(item, dict)
                    and type(item.get("file")) is str
                    and original_owner.core.valid_sha256(item.get("sha256"))
                    and item.get("passed") is True
                    and item.get("issues") == [],
                    "the actual current V15 owned source was replaced: " + family)
            actual[item["file"]] = item["sha256"]
        require(tuple(actual) == OWNED_SOURCE_PATHS[family],
                "an actual V15 complete owned family source was missing or reordered")
        source_by_family[family] = actual
    result = {
        "source_count": graph["source_count"],
        "source_paths": list(graph["source_paths"]),
        "source_sha256_by_family": source_by_family,
        "native_binary_count": graph["native_binary_count"],
        "native_sha256_by_family": copy.deepcopy(graph["native_sha256_by_family"]),
    }
    require(result["source_count"] == 12 and result["native_binary_count"] == 5
            and set(result["source_sha256_by_family"]) == set(CORE_FAMILIES)
            and set(result["native_sha256_by_family"]) == set(CORE_FAMILIES)
            and len(result["source_paths"]) == 12
            and len(set(result["source_paths"])) == 12
            and sum(map(len, result["native_sha256_by_family"].values())) == 5,
            "the genuine V15 all-family source/native denominator changed")
    for family in CORE_FAMILIES:
        require(set(result["native_sha256_by_family"][family])
                == set(OWNED_NATIVE_PATHS[family].values()),
                "a current independently mapped V15 family ELF was replaced")
    return result


def snapshot_current_graph() -> dict[str, Any]:
    verify_production_runtime()
    original_owner.core.ensure_candidate_free()
    with original_owner.source_v5.allow_owned_locale_ctype():
        current = original_owner.core.audit()
    original_owner.core.validate_v3_report(
        current, label="actual complete fresh V15 independent native source graph",
    )
    graph = full_graph(current)
    original_owner.core.ensure_candidate_free()
    return graph


def snapshot_current_report() -> tuple[dict[str, Any], dict[str, Any]]:
    verify_production_runtime()
    original_owner.core.ensure_candidate_free()
    with original_owner.source_v5.allow_owned_locale_ctype():
        current = original_owner.core.audit()
    original_owner.core.validate_v3_report(
        current, label="complete authentic V15 all-family static no-delegation proof",
    )
    graph = full_graph(current)
    original_owner.core.ensure_candidate_free()
    return current, graph


def validate_zig_failure_documents(
    crash: Any, invalidated: Any, retry: Any,
    original: Mapping[str, Any],
    *,
    passed: bool,
) -> dict[str, Any]:
    require(isinstance(crash, dict) and isinstance(invalidated, dict)
            and isinstance(retry, dict) and isinstance(original, Mapping)
            and passed is False and original == invalidated,
            "the preserved actual V12 Zig failure must remain a genuine original failure")
    crash_expected = {
        "schema": v12.SCHEMA + "-original-producer-failure",
        "status": "FAIL", "result": "FAIL", "mode": "qualified-deep",
        "candidate_family": "ZIG", "candidate_module": "candidates.zig_candidate",
        "actual_invoking_controller": "V12",
        "actual_invoking_controller_path": v12.SOURCE_RELATIVE,
        "actual_invoking_controller_sha256": V12_SOURCE_SHA256,
        "actual_retry_protocol_path": v12.PROTOCOL_RELATIVE,
        "actual_retry_protocol_sha256": V12_PROTOCOL_SHA256,
        "v11_executed_this_retry": False,
        "actual_child_exit_code": 1, "actual_child_signal": None,
        "timed_out": False,
        "complete_original_observation_archive": True,
        "invalidated_complete_original_evidence_path": ZIG_INVALIDATED_RELATIVE,
        "invalidated_complete_original_evidence_sha256": ZIG_INVALIDATED_SHA256,
        "invalidated_complete_original_actual_status": "FAIL",
        "actual_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "actual_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for name, expected in crash_expected.items():
        require(crash.get(name) == expected,
                "the complete genuine V12 Zig original failure was hidden: " + name)
    v11.restore_complete_stream(crash.get("stdout"), "actual failed V12 Zig worker stdout")
    v11.restore_complete_stream(crash.get("stderr"), "actual failed V12 Zig worker stderr")
    retry_expected = {
        "schema": v12.SCHEMA + "-qualified-deep-retry-failure-proof",
        "status": "FAIL", "result": "FAIL", "campaign_qualified": False,
        "actual_invoking_controller": "V12",
        "actual_invoking_controller_path": v12.SOURCE_RELATIVE,
        "actual_invoking_controller_sha256": V12_SOURCE_SHA256,
        "actual_retry_protocol_path": v12.PROTOCOL_RELATIVE,
        "actual_retry_protocol_sha256": V12_PROTOCOL_SHA256,
        "v11_executed_this_retry": False,
        "candidate_family": "ZIG", "candidate_module": "candidates.zig_candidate",
        "actual_failure_evidence_path": ZIG_PRODUCER_FAILURE_RELATIVE,
        "actual_failure_evidence_sha256": ZIG_PRODUCER_FAILURE_SHA256,
        "invalidated_complete_original_evidence_path": ZIG_INVALIDATED_RELATIVE,
        "invalidated_complete_original_evidence_sha256": ZIG_INVALIDATED_SHA256,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for name, expected in retry_expected.items():
        require(retry.get(name) == expected,
                "the separate truthful V12 Zig failure proof was hidden: " + name)
    require(retry.get("preserved_actual_first_v11_failure")
            == crash.get("preserved_actual_first_v11_failure"),
            "the real V12 Zig retry concealed the preserved first V11 failure")
    original_expected = {
        "schema": v12.DEEP_SCHEMA, "python": "3.14.6",
        "status": "FAIL", "seed": v11.DEEP_SEED,
        "seeded_case_count": v11.DEEP_SEEDED_CASES,
        "checks": v11.DEEP_CHECKS,
        "candidate_module": "candidates.zig_candidate",
        "candidate_family": "ZIG",
        "reference_a_sha256": v11.DEEP_REFERENCE_SHA256,
        "reference_b_sha256": v11.DEEP_REFERENCE_SHA256,
        "public_mismatch_count": 26,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for name, expected in original_expected.items():
        require(invalidated.get(name) == expected,
                "the original actual 393-case Zig failure was changed: " + name)
    failures = invalidated.get("public_mismatches")
    categories = invalidated.get("public_mismatch_family_counts")
    require(isinstance(failures, list) and len(failures) == 26
            and isinstance(categories, dict)
            and sorted(categories.values()) == [8, 18],
            "the genuine 18+8 complete Zig repr failures or denominator were concealed")
    return {
        "candidate_family": "ZIG",
        "candidate_module": "candidates.zig_candidate",
        "invalidated_path": ZIG_INVALIDATED_RELATIVE,
        "invalidated_sha256": ZIG_INVALIDATED_SHA256,
        "producer_failure_path": ZIG_PRODUCER_FAILURE_RELATIVE,
        "producer_failure_sha256": ZIG_PRODUCER_FAILURE_SHA256,
        "retry_failure_proof_path": ZIG_RETRY_FAILURE_RELATIVE,
        "retry_failure_proof_sha256": ZIG_RETRY_FAILURE_SHA256,
        "actual_child_exit_code": 1,
        "deep_checks": 393,
        "seeded_case_count": 64,
        "public_mismatch_count": 26,
        "public_mismatch_family_counts": dict(categories),
        "actual_candidate_observation_sha256": invalidated.get("candidate_sha256"),
        "actual_reference_observation_sha256": v11.DEEP_REFERENCE_SHA256,
        "first_v11_failure_sha256": v12.PRIOR_FAILURE_SHA256,
        "first_v11_invalidated_sha256": v12.PRIOR_INVALIDATED_SHA256,
        "qualifies_current_engine": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def validate_zig_failure_summary(summary: Any) -> dict[str, Any]:
    require(isinstance(summary, dict), "the three complete actual Zig failures are mandatory")
    expected = {
        "candidate_family": "ZIG",
        "candidate_module": "candidates.zig_candidate",
        "invalidated_path": ZIG_INVALIDATED_RELATIVE,
        "invalidated_sha256": ZIG_INVALIDATED_SHA256,
        "producer_failure_path": ZIG_PRODUCER_FAILURE_RELATIVE,
        "producer_failure_sha256": ZIG_PRODUCER_FAILURE_SHA256,
        "retry_failure_proof_path": ZIG_RETRY_FAILURE_RELATIVE,
        "retry_failure_proof_sha256": ZIG_RETRY_FAILURE_SHA256,
        "actual_child_exit_code": 1,
        "deep_checks": 393,
        "seeded_case_count": 64,
        "public_mismatch_count": 26,
        "actual_reference_observation_sha256": v11.DEEP_REFERENCE_SHA256,
        "first_v11_failure_sha256": v12.PRIOR_FAILURE_SHA256,
        "first_v11_invalidated_sha256": v12.PRIOR_INVALIDATED_SHA256,
        "qualifies_current_engine": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for name, value in expected.items():
        require(summary.get(name) == value,
                "a genuine preserved historical V12 Zig failure was forged: " + name)
    categories = summary.get("public_mismatch_family_counts")
    require(isinstance(categories, dict) and sorted(categories.values()) == [8, 18]
            and original_owner.core.valid_sha256(
                summary.get("actual_candidate_observation_sha256"),
            ),
            "the exact complete 18+8 Zig failures or actual observation hash was lost")
    return summary


def validate_v13_first_failure_document(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict),
            "the complete genuine first V13 historical-graph failure is mandatory")
    for name, expected in {
        "schema": V13_FIRST_FAILURE_SCHEMA,
        "status": "FAIL",
        "synthetic": False,
        "actual_exception_type": "AssertionError",
        "actual_exception_message": V13_FIRST_FAILURE_MESSAGE,
        "actual_native_owner_workers_started": 0,
        "current_build_qualified": False,
        "historical_failure_qualifies_current_build": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }.items():
        require(document.get(name) == expected,
                "the actual first V13 pre-worker failure was concealed: " + name)
    stage = document.get("failure_stage")
    require(isinstance(stage, str)
            and "historical" in stage and "edge" in stage,
            "the actual V13 historical Zig edge failure stage was falsified")
    invocation = document.get("actual_invocation")
    require(isinstance(invocation, dict)
            and invocation.get("exit_code") == 1
            and invocation.get("executable") == str(v11.PINNED_EXECUTABLE)
            and invocation.get("output_capture")
            == "complete combined command output; stdout and stderr were not separately captured",
            "the actual failed V13 isolated parent or merged output was invented")
    arguments = invocation.get("arguments")
    require(isinstance(arguments, list) and "--ownership-audit" in arguments
            and any(isinstance(value, str) and value.endswith(V13_SOURCE_RELATIVE)
                    for value in arguments),
            "the exact first real V13 ownership invocation was substituted")
    controller = document.get("controller")
    require(isinstance(controller, dict),
            "the actual failed V13 source and protocol provenance is missing")
    owner_source = controller.get("source_path", controller.get("audit_source_path"))
    owner_digest = controller.get("source_sha256", controller.get("audit_source_sha256"))
    protocol_path = controller.get("protocol_path", controller.get("audit_protocol_path"))
    protocol_digest = controller.get("protocol_sha256", controller.get("audit_protocol_sha256"))
    require(owner_source == V13_SOURCE_RELATIVE
            and owner_digest == V13_SOURCE_SHA256
            and protocol_path == V13_PROTOCOL_RELATIVE
            and protocol_digest == V13_PROTOCOL_SHA256,
            "the actual failed immutable V13 source/protocol identity was replaced")
    lines = document.get("complete_captured_combined_output_lines")
    require(isinstance(lines, list) and len(lines) == 34
            and all(isinstance(line, str) for line in lines)
            and any(V13_FIRST_FAILURE_MESSAGE in line for line in lines)
            and any("validate_edge_document" in line for line in lines)
            and any("authenticate_historical_audits" in line for line in lines),
            "the actual complete 34-line merged V13 traceback was lost or rewritten")
    for key in ("fresh_ownership_failure_report", "fresh_ownership_report",
                "fresh_strict_failure_report", "fresh_strict_report"):
        require(document.get(key) == "NOT CREATED",
                "the first V13 pre-worker failure invented ownership evidence: " + key)
    return {
        "failure_path": V13_FIRST_FAILURE_RELATIVE,
        "failure_sha256": V13_FIRST_FAILURE_SHA256,
        "failure_schema": V13_FIRST_FAILURE_SCHEMA,
        "status": "FAIL",
        "failed_stage": stage,
        "actual_error_type": "AssertionError",
        "actual_error_message": V13_FIRST_FAILURE_MESSAGE,
        "actual_exit_code": 1,
        "native_owner_workers_started": 0,
        "original_edge_worker_started": False,
        "synthetic": False,
        "qualifies_current_engine": False,
        "v13_source_path": V13_SOURCE_RELATIVE,
        "v13_source_sha256": V13_SOURCE_SHA256,
        "v13_protocol_path": V13_PROTOCOL_RELATIVE,
        "v13_protocol_sha256": V13_PROTOCOL_SHA256,
        "stdout_capture": "NOT CAPTURED",
        "stderr_capture": "NOT CAPTURED",
        "combined_traceback_line_count": 34,
        "combined_traceback_separately_captured": False,
        "fresh_ownership_report": "NOT CREATED",
        "fresh_ownership_failure_report": "NOT CREATED",
        "fresh_strict_report": "NOT CREATED",
        "fresh_strict_failure_report": "NOT CREATED",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def validate_v13_first_failure_summary(summary: Any) -> dict[str, Any]:
    require(isinstance(summary, dict),
            "the genuine actual V13 pre-worker failure cannot be omitted")
    for name, value in {
        "failure_path": V13_FIRST_FAILURE_RELATIVE,
        "failure_sha256": V13_FIRST_FAILURE_SHA256,
        "failure_schema": V13_FIRST_FAILURE_SCHEMA,
        "status": "FAIL",
        "actual_error_type": "AssertionError",
        "actual_error_message": V13_FIRST_FAILURE_MESSAGE,
        "actual_exit_code": 1,
        "native_owner_workers_started": 0,
        "original_edge_worker_started": False,
        "synthetic": False,
        "qualifies_current_engine": False,
        "v13_source_path": V13_SOURCE_RELATIVE,
        "v13_source_sha256": V13_SOURCE_SHA256,
        "v13_protocol_path": V13_PROTOCOL_RELATIVE,
        "v13_protocol_sha256": V13_PROTOCOL_SHA256,
        "stdout_capture": "NOT CAPTURED",
        "stderr_capture": "NOT CAPTURED",
        "combined_traceback_line_count": 34,
        "combined_traceback_separately_captured": False,
        "fresh_ownership_report": "NOT CREATED",
        "fresh_ownership_failure_report": "NOT CREATED",
        "fresh_strict_report": "NOT CREATED",
        "fresh_strict_failure_report": "NOT CREATED",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }.items():
        require(summary.get(name) == value,
                "the genuine actual first V13 failure was forged: " + name)
    stage = summary.get("failed_stage")
    require(isinstance(stage, str) and "historical" in stage and "edge" in stage,
            "the genuine V13 pre-worker stage was changed")
    return summary


def historical_edge_proof(
    document: Any,
    raw: bytes,
    path: Path,
    snapshot: Mapping[str, Any],
    contract: Any,
    v8: Any,
) -> dict[str, Any]:
    passed, failed = v8.validate_edge_shape(document, "zig", snapshot)
    require(passed is True and failed == 0
            and isinstance(raw, bytes)
            and isinstance(path, Path)
            and path == v11.edge_target("zig", True, True),
            "the original historical Zig edge is not a complete authentic passing archive")
    spec = contract.SPECS[v11.FAMILIES["zig"]["module"]]
    expected_paths = contract.expected_edge_paths(spec)
    fingerprints = dict(snapshot["source_sha256_by_path"])
    fingerprints.update(snapshot["native_sha256_by_path"])
    authorized: dict[str, tuple[str, str]] = {}
    for item in document.get("candidate_artifacts", ()):
        require(isinstance(item, dict)
                and set(item) == {"role", "path", "sha256"}
                and item["role"] in expected_paths
                and item["role"] not in authorized
                and expected_paths[item["role"]] == item["path"]
                and fingerprints.get(item["path"]) == item["sha256"],
                "an original historical Zig native artifact was not proven by the old graph")
        authorized[item["role"]] = (item["path"], item["sha256"])
    require(set(authorized) == set(expected_paths),
            "the archived historical Zig edge lost an actual original native role")
    embedded = document.get("embedded_frozen_oracles")
    expected_embedded = contract.frozen_embedded_oracles()
    require(isinstance(embedded, list)
            and len(embedded) == len(expected_embedded),
            "the historical original edge lost an authentic embedded frozen sub-oracle")
    found: set[str] = set()
    for item in embedded:
        require(isinstance(item, dict), "an archived original sub-oracle is malformed")
        name = item.get("name")
        require(name in expected_embedded and name not in found,
                "an archived original edge sub-oracle was replaced or repeated")
        for key, expected in expected_embedded[name].items():
            require(item.get(key) == expected,
                    "a genuine archived edge sub-oracle changed: " + name + ":" + key)
        require(isinstance(item.get("schema"), str) and bool(item["schema"]),
                "an original archived sub-oracle omitted its genuine schema")
        if name == "independent-parser-grammar":
            families = item.get("families")
            require(isinstance(families, list) and len(families) == 16
                    and len(set(families)) == 16
                    and all(isinstance(value, str) for value in families),
                    "the frozen original 16-family historical parser oracle was changed")
        found.add(name)
    complete = dict(authorized)
    for role, relative in spec.source_paths:
        require(relative in fingerprints,
                "a historically authenticated Zig semantic source was omitted")
        historical = (relative, fingerprints[relative])
        require(role not in complete or complete[role] == historical,
                "an archived Zig source role was swapped for the repaired live build")
        complete[role] = historical

    def serialize(items: Mapping[str, tuple[str, str]]) -> list[dict[str, str]]:
        return [
            {"role": role, "path": relative, "sha256": digest}
            for role, (relative, digest) in sorted(items.items())
        ]

    return {
        "schema": contract.EDGE_SCHEMA,
        "path": str(path.resolve()),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "script_sha256": contract.EDGE_SCRIPT_SHA256,
        "seed": contract.EDGE_SEED,
        "checks": contract.EDGE_CHECKS,
        "category_count": contract.EDGE_CATEGORIES,
        "reference_sha256": contract.EDGE_REFERENCE_SHA256,
        "candidate_sha256": contract.EDGE_REFERENCE_SHA256,
        "failed": 0,
        "module": spec.module,
        "family": spec.family,
        "candidate_artifacts": serialize(authorized),
        "production_artifacts": serialize(complete),
    }

def authenticate_historical_audits() -> dict[str, Any]:
    verify_production_runtime()
    controller = authenticate_controller()
    pins = v11.validated_report_pins(
        True, ACTUAL_V10_BASE_REPORT_SHA256, ACTUAL_V10_STRICT_REPORT_SHA256,
    )
    require(isinstance(pins, dict),
            "both actual complete immutable historical V10 report pins are mandatory")
    original = v11.audit_v11_reports(original_owner, original_strict, pins)
    v8 = v11.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        v11.V8_PROOF_RELATIVE, v11.V8_PROOF_SHA256,
    )
    preliminary = {"owner": original_owner, "v8": v8, "audits": original}
    first, _, _ = v12.authenticate_prior_incident(preliminary)
    old_history = v11.authenticate_history(v8, original_owner)
    old_graph = v11.audited_graph_provenance(preliminary)
    zig_paths = OWNED_SOURCE_PATHS["zig"]
    old_snapshot = {
        "family": "zig", "module": "candidates.zig_candidate",
        "source_sha256_by_path": {
            name: old_graph["all_family_source_sha256_by_path"][name]
            for name in zig_paths
        },
        "native_sha256_by_path": {
            name: old_graph["all_family_native_elf_sha256_by_path"][name]
            for name in OWNED_NATIVE_PATHS["zig"].values()
        },
    }
    historical_state = {
        "owner": original_owner, "strict": original_strict, "v8": v8,
        "audits": original, "history": old_history, "snapshot": old_snapshot,
    }
    contract = v8.load_contract()
    edge_path = v11.edge_target("zig", True, True)
    edge_raw = v11.read_regular(
        edge_path, "complete genuine historical pre-repair Zig edge archive",
    )
    edge_original, _ = v8.decode_archive(
        edge_raw, "complete original historically proven qualified V11 Zig edge",
    )
    edge = historical_edge_proof(
        edge_original, edge_raw, edge_path, old_snapshot, contract, v8,
    )
    wrapper_path = v11.edge_proof_target("zig", True, True)
    wrapper_raw = v11.read_regular(
        wrapper_path, "complete genuine historical V11 edge-native-owner wrapper",
    )
    wrapper = v11.decode_json(
        wrapper_raw, "complete canonical genuine historically proven V11 edge wrapper",
    )
    require(v11.canonical(wrapper) == wrapper_raw,
            "the real original historical V11 Zig edge owner proof is not canonical")
    archived_process = subprocess.CompletedProcess(
        args=["durably-recorded-original-v11-edge"],
        returncode=wrapper.get("original_worker_returncode"),
        stdout=v11.restore_complete_stream(
            wrapper.get("original_worker_stdout"),
            "genuine complete archived historical Zig edge original stdout",
        ),
        stderr=v11.restore_complete_stream(
            wrapper.get("original_worker_stderr"),
            "genuine complete archived historical Zig edge original stderr",
        ),
    )
    v11.validate_durable_wrapper(
        wrapper, "zig", historical_state, qualified=True, deep=False,
        passed=True, original=edge_original, archive_path=edge_path,
        archive_sha256=hashlib.sha256(edge_raw).hexdigest(),
        archive_bytes=len(edge_raw),
        owner_before=wrapper.get("corrected_v10_native_owner_before"),
        owner_after=wrapper.get("corrected_v10_native_owner_after"),
        producer=archived_process,
    )
    invalidated_raw = v11.authenticate_frozen(
        ZIG_INVALIDATED_RELATIVE, ZIG_INVALIDATED_SHA256,
    )
    invalidated, _ = v8.decode_archive(
        invalidated_raw, "actual compact original historically failed V12 Zig deep",
        compact=True,
    )
    decoded, passed = v8.validate_deep(
        invalidated_raw, "zig", edge, old_snapshot, contract,
    )
    require(decoded == invalidated and passed is False,
            "the genuine historical 393-case Zig failure changed its old snapshot")
    crash_raw = v11.authenticate_frozen(
        ZIG_PRODUCER_FAILURE_RELATIVE, ZIG_PRODUCER_FAILURE_SHA256,
    )
    crash, _ = v8.decode_archive(
        crash_raw, "complete actual pre-repair V12 Zig producer failure",
    )
    retry_raw = v11.authenticate_frozen(
        ZIG_RETRY_FAILURE_RELATIVE, ZIG_RETRY_FAILURE_SHA256,
    )
    retry = v11.decode_json(
        retry_raw, "genuine complete canonical separate V12 Zig failure proof",
    )
    require(v11.canonical(retry) == retry_raw,
            "the genuine preserved V12 Zig failure proof is not canonical")
    zig = validate_zig_failure_documents(
        crash, invalidated, retry, decoded, passed=passed,
    )
    require(crash.get("preserved_actual_first_v11_failure") == first,
            "the genuine first failed V11 parent was hidden from Zig history")
    actual_v13_raw = v11.authenticate_frozen(
        V13_FIRST_FAILURE_RELATIVE, V13_FIRST_FAILURE_SHA256,
    )
    actual_v13 = v11.decode_json(
        actual_v13_raw, "complete real preserved first V13 pre-worker failure",
    )
    require(actual_v13_raw in {
        v11.canonical(actual_v13),
        original_owner.core.canonical(actual_v13) + b"\n",
    }, "the complete genuine first V13 failure is not frozen canonical JSON")
    failure = validate_v13_first_failure_document(actual_v13)
    return {
        "controller": controller,
        "historical_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "historical_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "historical_v10_graph_qualifies_current_engine": False,
        "preserved_original_v11_failure": first,
        "preserved_immutable_original_history": old_history,
        "preserved_zig_failure": zig,
        "preserved_v13_first_audit_failure": failure,
    }

def validate_preserved_history(history: Any) -> dict[str, Any]:
    require(isinstance(history, dict), "a genuine V15 audit concealed preserved history")
    expected = {
        "historical_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "historical_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "historical_v10_graph_qualifies_current_engine": False,
    }
    for key, value in expected.items():
        require(history.get(key) == value,
                "a real V15 historical V10 audit was changed: " + key)
    first = history.get("preserved_original_v11_failure")
    require(isinstance(first, dict)
            and first.get("actual_v11_first_invocation_status") == "FAIL"
            and first.get("actual_v11_first_failure_sha256") == v12.PRIOR_FAILURE_SHA256
            and first.get("actual_v11_first_invalidated_original_sha256")
            == v12.PRIOR_INVALIDATED_SHA256
            and first.get("first_failure_retroactively_qualified") is False,
            "the actual first failed V11 invocation was hidden or qualified")
    original = history.get("preserved_immutable_original_history")
    require(isinstance(original, dict)
            and isinstance(original.get("historical_current_build_edge_failures"), dict)
            and set(original["historical_current_build_edge_failures"])
            == set(CORE_FAMILIES)
            and isinstance(original.get("genuine_v8_preimport_owner_failure"), dict)
            and original["genuine_v8_preimport_owner_failure"].get("status") == "FAIL"
            and isinstance(original.get("genuine_v9_cached_compiler_owner_failure"), dict)
            and original["genuine_v9_cached_compiler_owner_failure"].get("status") == "FAIL",
            "the real V8/V9/all-family historical native failures were concealed")
    validate_zig_failure_summary(history.get("preserved_zig_failure"))
    validate_v13_first_failure_summary(history.get("preserved_v13_first_audit_failure"))
    return history


def destination_name(value: Any) -> str:
    require(type(value) is str, "an exact exclusive V15 audit path must be textual")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts
            and "\\" not in value and "\x00" not in value
            and path.as_posix() == value
            and value in {
                BASE_REPORT_RELATIVE, BASE_FAILURE_RELATIVE,
                STRICT_REPORT_RELATIVE, STRICT_FAILURE_RELATIVE,
            }, "only the four exact separate exclusive V15 audit outputs are authorized")
    return value


def mode_destinations(strict: bool) -> tuple[Path, Path]:
    require(type(strict) is bool, "a genuine V15 audit mode must be boolean")
    selected = ((STRICT_REPORT_RELATIVE, STRICT_FAILURE_RELATIVE) if strict
                else (BASE_REPORT_RELATIVE, BASE_FAILURE_RELATIVE))
    return tuple(ROOT / destination_name(relative) for relative in selected)


def require_fresh_destinations(strict: bool) -> None:
    parent = ROOT / "candidates/audits"
    for target in mode_destinations(strict):
        v11.fresh_target(target, parent)


def summarize_controls(document: Mapping[str, Any]) -> dict[str, Any]:
    require(isinstance(document, Mapping)
            and document.get("status") == "PASS"
            and document.get("passed") is True
            and isinstance(document.get("check_count"), int)
            and document["check_count"] >= 150,
            "real V15 ownership requires genuine candidate-free poison controls")
    result = {
        "schema": document.get("schema"), "status": "PASS", "passed": True,
        "check_count": document["check_count"],
        "candidate_imports": document.get("candidate_imports"),
        "subprocesses": document.get("subprocesses"),
        "file_reads": document.get("file_reads"),
        "file_writes": document.get("file_writes"),
        "clock_samples": document.get("clock_samples"),
        "historical_evidence_reads": document.get("historical_evidence_reads", 0),
        "actual_audit_report_reads": document.get("actual_audit_report_reads", 0),
        "synthetic_results_qualify_candidates":
            document.get("synthetic_results_qualify_candidates"),
    }
    require(all(result[name] == 0 for name in (
        "candidate_imports", "subprocesses", "file_reads", "file_writes",
        "clock_samples", "historical_evidence_reads", "actual_audit_report_reads",
    )) and result["synthetic_results_qualify_candidates"] is False,
            "the V15 source-only native-owner boundary actually caused a production effect")
    return result


def validate_report_common(
    document: Any,
    *,
    strict: bool,
    digest: str,
    allow_failure: bool = False,
) -> dict[str, Any]:
    require(isinstance(document, dict)
            and original_owner.core.valid_sha256(digest)
            and hashlib.sha256(canonical(document)).hexdigest() == digest,
            "an actual independent V15 all-family report is not its exact canonical bytes")
    status = "FAIL" if allow_failure else "PASS"
    schema = STRICT_SCHEMA if strict else BASE_SCHEMA
    expected = {
        "schema": schema, "postfinal_schema": schema,
        "status": status, "result": status, "passed": not allow_failure,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "v10_native_owner_source_path": original_owner.SOURCE_RELATIVE,
        "v10_native_owner_source_sha256": V10_OWNER_SOURCE_SHA256,
        "v10_no_delegation_source_path": original_strict.SOURCE_RELATIVE,
        "v10_no_delegation_source_sha256": V10_STRICT_SOURCE_SHA256,
        "v10_native_ownership_protocol_path": original_owner.PROTOCOL_RELATIVE,
        "v10_native_ownership_protocol_sha256": V10_PROTOCOL_SHA256,
        "native_owner_worker_sha256": original_owner.NATIVE_OWNER_WORKER_SHA256,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "genuine_python_matching_guards_per_family": 13,
        "genuine_native_loader_guards_per_family": 5,
        "historical_v10_graph_qualifies_current_engine": False,
        "historical_zig_failure_qualifies_current_engine": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "a complete real V15 native audit was substituted: " + key)
    require(original_owner.core.valid_sha256(document.get("audit_source_sha256")),
            "an actual V15 source SHA cannot be predicted or omitted")
    graph = full_graph(document)
    require(document.get("verified_candidate_source_paths") == graph["source_paths"]
            and document.get("source_sha256_by_family")
            == graph["source_sha256_by_family"]
            and document.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "a genuine V15 report lost an exact current twelve-source/five-ELF map")
    workers = document.get("actual_native_owner_workers")
    require(isinstance(workers, dict),
            "a genuine V15 all-family report omitted complete actual native observations")
    if not allow_failure:
        require(set(workers) == set(CORE_FAMILIES)
                and document.get("completed_native_owner_worker_count") == 3
                and document.get("actual_native_owner_worker_failure") is None
                and document.get("verified_match_repr_checks") == 6
                and document.get("verified_standard_pickle_count") == 48
                and document.get("standard_pickle_failure_count") == 0,
                "a passing V15 audit omitted an actual independent native family")
    for family, record in workers.items():
        require(family in CORE_FAMILIES,
                "a genuine V15 owner report introduced a foreign candidate")
        validate_native_owner(record, family, graph["native_sha256_by_family"][family])
    history = validate_preserved_history(document.get("preserved_immutable_history"))
    require(document.get("preserved_zig_failure") == history["preserved_zig_failure"]
            and document.get("preserved_v13_failure")
            == history["preserved_v13_first_audit_failure"],
            "the V15 current audit hid a genuine archived Zig or first V13 failure")
    summarize_controls(document.get("postfinal_wrapper_self_test"))
    scope = document.get("postfinal_scope")
    require(isinstance(scope, dict)
            and scope.get("append_only") is True
            and scope.get("separate_pass_and_failure_destinations") is True
            and scope.get("actual_current_native_binary_count") == 5
            and scope.get("exact_current_owned_candidate_source_count") == 12
            and scope.get("actual_python_matching_guards_per_family") == 13
            and scope.get("actual_native_loader_guards_per_family") == 5
            and scope.get("exact_stage07_sentinel_checked_before_and_after") is True
            and scope.get("all_cached_matcher_descendants_poisoned_before_and_after")
            is True
            and scope.get("original_stage07_cached_alias_helper_used") is True
            and scope.get("persistent_cross_family_import_and_loader_guards") is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("historical_v10_audits_qualify_current_graph") is False
            and scope.get("historical_v12_zig_failure_qualifies_current_graph") is False
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            "an original cached matcher, external engine, loader, or history escape remains")
    destination = mode_destinations(strict)[1 if allow_failure else 0]
    require(scope.get("exclusive_report_path")
            == destination.relative_to(ROOT).as_posix(),
            "an actual V15 independent audit substituted its exclusive destination")
    return graph


def validate_base_report(document: Any, base_report_sha256: str) -> dict[str, Any]:
    graph = validate_report_common(document, strict=False, digest=base_report_sha256)
    require(document.get("strict_base_report_path") is None
            and document.get("strict_base_report_sha256") is None
            and document.get("independent_base_native_owner_workers") is None,
            "a fresh V15 ownership report cannot claim a future strict/base hash")
    return graph


def validate_strict_report(
    document: Any, base_report_sha256: str, strict_report_sha256: str,
) -> dict[str, Any]:
    require(original_owner.core.valid_sha256(base_report_sha256)
            and base_report_sha256 != strict_report_sha256,
            "V15 strict proof requires a distinct externally authenticated fresh base")
    graph = validate_report_common(document, strict=True, digest=strict_report_sha256)
    require(document.get("strict_base_report_path") == BASE_REPORT_RELATIVE
            and document.get("strict_base_report_sha256") == base_report_sha256,
            "the independent V15 strict worker did not bind the real current base")
    base_owners = document.get("independent_base_native_owner_workers")
    require(isinstance(base_owners, dict)
            and set(base_owners) == set(CORE_FAMILIES),
            "the real V15 strict report omitted its three genuine base owner workers")
    for family in CORE_FAMILIES:
        validate_native_owner(
            base_owners[family], family, graph["native_sha256_by_family"][family],
        )
    return graph


def read_canonical_report(relative: str, expected: str) -> tuple[dict[str, Any], bytes]:
    require(original_owner.core.valid_sha256(expected),
            "a real externally published V15 report SHA-256 is mandatory")
    raw = v11.authenticate_frozen(relative, expected)
    document = original_owner.core.decode_report(
        raw, label="complete actual canonical independently pinned V15 report",
    )
    require(canonical(document) == raw,
            "an actual exclusively published V15 audit lost canonical bytes")
    return document, raw


def authenticate_qualified_audits(
    base_digest: str, strict_digest: str,
) -> dict[str, Any]:
    verify_production_runtime()
    controller = authenticate_controller()
    require(original_owner.core.valid_sha256(base_digest)
            and original_owner.core.valid_sha256(strict_digest)
            and base_digest != strict_digest,
            "both distinct genuine fresh V15 report hashes must be supplied externally")
    base, _ = read_canonical_report(BASE_REPORT_RELATIVE, base_digest)
    base_graph = validate_base_report(base, base_digest)
    require(base.get("audit_source_sha256") == controller["source_sha256"],
            "the actual fresh V15 base was not produced by the frozen current source")
    strict, _ = read_canonical_report(STRICT_REPORT_RELATIVE, strict_digest)
    strict_graph = validate_strict_report(strict, base_digest, strict_digest)
    require(strict.get("audit_source_sha256") == controller["source_sha256"]
            and strict_graph == base_graph
            and strict.get("preserved_immutable_history")
            == base.get("preserved_immutable_history")
            and strict.get("independent_base_native_owner_workers")
            == base.get("actual_native_owner_workers"),
            "the independently executed V15 strict audit changed its exact complete base")
    actual = snapshot_current_graph()
    require(actual == base_graph,
            "a current independently owned source or native ELF changed after V15")
    return {
        "base": base, "strict": strict, "graph": actual,
        "pins": {
            "audit_source": controller["source_sha256"],
            "audit_protocol": controller["protocol_sha256"],
            "base_report": base_digest,
            "strict_report": strict_digest,
        },
        "history": base["preserved_immutable_history"],
        "preserved_zig_failure": base["preserved_zig_failure"],
        "preserved_v13_failure": base["preserved_v13_failure"],
        "owner": original_owner,
    }


def build_report(
    current: Mapping[str, Any],
    graph: Mapping[str, Any],
    history: Mapping[str, Any],
    controls: Mapping[str, Any],
    controller: Mapping[str, Any],
    *,
    strict: bool,
    observations: Mapping[str, Mapping[str, Any]],
    failure: Mapping[str, Any] | None,
    base_document: Mapping[str, Any] | None = None,
    base_digest: str | None = None,
) -> dict[str, Any]:
    require(isinstance(current, Mapping) and isinstance(graph, Mapping)
            and isinstance(observations, Mapping),
            "a V15 result must preserve real static graph and actual owner observations")
    passed = failure is None and set(observations) == set(CORE_FAMILIES)
    schema = STRICT_SCHEMA if strict else BASE_SCHEMA
    destination = mode_destinations(strict)[0 if passed else 1]
    result = dict(current)
    result.update({
        "schema": schema, "postfinal_schema": schema,
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL", "passed": passed,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": controller["source_sha256"],
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "v10_native_owner_source_path": original_owner.SOURCE_RELATIVE,
        "v10_native_owner_source_sha256": V10_OWNER_SOURCE_SHA256,
        "v10_no_delegation_source_path": original_strict.SOURCE_RELATIVE,
        "v10_no_delegation_source_sha256": V10_STRICT_SOURCE_SHA256,
        "v10_native_ownership_protocol_path": original_owner.PROTOCOL_RELATIVE,
        "v10_native_ownership_protocol_sha256": V10_PROTOCOL_SHA256,
        "native_owner_worker_sha256": original_owner.NATIVE_OWNER_WORKER_SHA256,
        "historical_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "historical_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "historical_v10_graph_qualifies_current_engine": False,
        "historical_zig_failure_qualifies_current_engine": False,
        "preserved_immutable_history": dict(history),
        "preserved_zig_failure": dict(history["preserved_zig_failure"]),
        "preserved_v13_failure": dict(history["preserved_v13_first_audit_failure"]),
        "postfinal_wrapper_self_test": summarize_controls(controls),
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": list(graph["source_paths"]),
        "source_sha256_by_family": copy.deepcopy(graph["source_sha256_by_family"]),
        "verified_native_role_count": 5,
        "native_sha256_by_family": copy.deepcopy(graph["native_sha256_by_family"]),
        "actual_native_owner_workers": {
            family: dict(record) for family, record in observations.items()
        },
        "actual_native_owner_worker_failure": dict(failure) if failure else None,
        "completed_native_owner_worker_count": len(observations),
        "unstarted_native_owner_families": [
            family for family in CORE_FAMILIES
            if family not in observations
            and (failure is None or family != failure.get("family"))
        ],
        "verified_match_repr_checks": sum(
            record.get("match_repr_checks", 0) for record in observations.values()
        ),
        "verified_standard_pickle_count": sum(
            record.get("standard_pickle_check_count", 0)
            for record in observations.values()
        ),
        "standard_pickle_failure_count": sum(
            record.get("standard_pickle_failure_count", 0)
            for record in observations.values()
        ),
        "genuine_python_matching_guards_per_family": 13,
        "genuine_native_loader_guards_per_family": 5,
        "strict_base_report_path": BASE_REPORT_RELATIVE if strict else None,
        "strict_base_report_sha256": base_digest if strict else None,
        "independent_base_native_owner_workers":
            copy.deepcopy(base_document.get("actual_native_owner_workers"))
            if strict and base_document is not None else None,
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": destination.relative_to(ROOT).as_posix(),
            "separate_pass_and_failure_destinations": True,
            "actual_current_native_binary_count": 5,
            "exact_current_owned_candidate_source_count": 12,
            "actual_python_matching_guards_per_family": 13,
            "actual_native_loader_guards_per_family": 5,
            "exact_stage07_sentinel_checked_before_and_after": True,
            "all_cached_matcher_descendants_poisoned_before_and_after": True,
            "original_stage07_cached_alias_helper_used": True,
            "persistent_cross_family_import_and_loader_guards": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "independently_executed_native_owner_workers": len(observations)
                + int(failure is not None
                      and failure.get("family") not in observations),
            "historical_v10_audits_qualify_current_graph": False,
            "historical_v12_zig_failure_qualifies_current_graph": False,
            "base_report_hash_supplied_externally": strict,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    })
    if passed:
        candidate_digest = hashlib.sha256(canonical(result)).hexdigest()
        if strict:
            validate_strict_report(result, str(base_digest), candidate_digest)
        else:
            validate_base_report(result, candidate_digest)
    return result


def validate_publication_receipt(
    receipt: Any,
    relative: str,
    digest: str,
    byte_count: int,
) -> dict[str, Any]:
    require(isinstance(receipt, dict)
            and destination_name(relative) == relative
            and original_owner.core.valid_sha256(digest)
            and type(byte_count) is int and 0 < byte_count <= MAX_REPORT_BYTES,
            "a real V15 exclusive publication receipt is incomplete")
    for key, expected in {
        "schema": SCHEMA + "-actual-exclusive-publication-receipt",
        "status": "PASS",
        "report_path": relative,
        "report_sha256": digest,
        "expected_bytes": byte_count,
        "actual_bytes_written": byte_count,
        "exclusive_create_succeeded": True,
        "file_fsync_succeeded": True,
        "parent_directory_fsync_succeeded": True,
        "canonical_reread_succeeded": True,
        "production_observations_invented": False,
    }.items():
        require(receipt.get(key) == expected,
                "a genuine V15 publication syscall receipt was forged: " + key)
    calls = receipt.get("actual_write_calls")
    require(isinstance(calls, list) and bool(calls)
            and all(isinstance(row, dict)
                    and type(row.get("requested_bytes")) is int
                    and type(row.get("returned_bytes")) is int
                    and 0 < row["returned_bytes"] <= row["requested_bytes"]
                    for row in calls)
            and sum(row["returned_bytes"] for row in calls) == byte_count,
            "an actual partial V15 write was omitted, invented, or miscounted")
    remaining = byte_count
    for call in calls:
        require(call["requested_bytes"] == remaining,
                "an actual V15 partial-write continuation was falsified")
        remaining -= call["returned_bytes"]
    require(remaining == 0,
            "the actual complete V15 syscall write receipt is truncated")
    return receipt


def write_report(
    report: Mapping[str, Any], *, strict: bool,
) -> tuple[str, str, dict[str, Any]]:
    require(isinstance(report, Mapping) and type(strict) is bool,
            "a genuine V15 append-only report requires its exact owner mode")
    passed = report.get("passed") is True
    target = mode_destinations(strict)[0 if passed else 1]
    parent = ROOT / "candidates/audits"
    v11.fresh_target(target, parent)
    raw = canonical(report)
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "the complete genuine V15 audit evidence exceeds its safe byte boundary")
    expected = hashlib.sha256(raw).hexdigest()
    relative = target.relative_to(ROOT).as_posix()
    receipt: dict[str, Any] = {
        "schema": SCHEMA + "-actual-exclusive-publication-receipt",
        "status": "NOT COMPLETED",
        "report_path": relative,
        "report_sha256": expected,
        "expected_bytes": len(raw),
        "actual_bytes_written": 0,
        "actual_write_calls": [],
        "exclusive_create_succeeded": False,
        "file_fsync_succeeded": False,
        "parent_directory_fsync_succeeded": False,
        "canonical_reread_succeeded": False,
        "production_observations_invented": False,
    }
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        directory = os.open(parent, flags)
        try:
            identity = os.fstat(directory)
            observed_parent = os.stat(parent, follow_symlinks=False)
            require(stat.S_ISDIR(identity.st_mode)
                    and (identity.st_dev, identity.st_ino)
                    == (observed_parent.st_dev, observed_parent.st_ino),
                    "the canonical exclusive V15 audit parent changed during publication")
            create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
            descriptor = os.open(target.name, create, 0o644, dir_fd=directory)
            receipt["exclusive_create_succeeded"] = True
            try:
                remaining = memoryview(raw)
                while remaining:
                    attempt = {"requested_bytes": len(remaining),
                               "returned_bytes": None}
                    receipt["actual_write_calls"].append(attempt)
                    written = os.write(descriptor, remaining)
                    attempt["returned_bytes"] = written
                    require(type(written) is int and 0 < written <= len(remaining),
                            "a genuine V15 syscall returned an unsafe partial write")
                    receipt["actual_bytes_written"] += written
                    remaining = remaining[written:]
                os.fsync(descriptor)
                receipt["file_fsync_succeeded"] = True
            finally:
                os.close(descriptor)
            os.fsync(directory)
            receipt["parent_directory_fsync_succeeded"] = True
        finally:
            os.close(directory)
        saved, saved_raw = read_canonical_report(relative, expected)
        require(saved == report and saved_raw == raw,
                "an exact exclusively published V15 all-family report was changed")
        receipt["canonical_reread_succeeded"] = True
        if passed:
            if strict:
                validate_strict_report(
                    saved, str(saved["strict_base_report_sha256"]), expected,
                )
            else:
                validate_base_report(saved, expected)
        receipt["status"] = "PASS"
        validate_publication_receipt(receipt, relative, expected, len(raw))
        return relative, expected, receipt
    except AuditV15PublicationFailure:
        raise
    except (AssertionError, OSError, TypeError, ValueError, KeyError) as error:
        receipt["status"] = "FAIL"
        receipt["actual_error_type"] = type(error).__name__
        receipt["actual_error_message"] = str(error)
        if isinstance(error, OSError):
            receipt["actual_errno"] = error.errno
        raise AuditV15PublicationFailure(
            "the exclusive V15 publication failed; actual syscall receipt retained",
            receipt,
        ) from error


def run_audit(*, strict: bool, base_report_sha256: str | None = None) -> dict[str, Any]:
    parent = verify_production_runtime()
    require(type(strict) is bool, "a genuine V15 audit must select one exact mode")
    if strict:
        require(original_owner.core.valid_sha256(base_report_sha256),
                "strict V15 ownership requires the actual external fresh V15 base SHA")
    else:
        require(base_report_sha256 is None,
                "a base V15 ownership audit cannot borrow a future strict report")
    controller = authenticate_controller()
    require_fresh_destinations(strict)
    base_document: dict[str, Any] | None = None
    if strict:
        base_document, _ = read_canonical_report(
            BASE_REPORT_RELATIVE, str(base_report_sha256),
        )
        base_graph = validate_base_report(base_document, str(base_report_sha256))
        require(base_document.get("audit_source_sha256") == controller["source_sha256"],
                "the externally pinned V15 base belongs to a different real controller")
    history = authenticate_historical_audits()
    require(history.get("controller") == controller
            and validate_parent_environment(os.environ) == parent,
            "the authentic V15 controller changed during historical validation")
    controls = candidate_free_self_test()
    current, graph = snapshot_current_report()
    if strict:
        require(graph == base_graph,
                "a real owned source or native ELF changed after the passing V15 base")
    observations: dict[str, dict[str, Any]] = {}
    failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            observations[family] = run_native_worker(
                family, graph["native_sha256_by_family"][family],
            )
        except original_owner.NativeWorkerFailure as error:
            failure = dict(error.evidence)
            break
        except (AssertionError, TypeError, ValueError, KeyError, OSError) as error:
            failure = {
                "schema": SCHEMA + "-actual-native-owner-validation-failure",
                "status": "FAIL", "family": family,
                "candidate_module": v11.FAMILIES[family]["module"],
                "actual_validation_error_type": type(error).__name__,
                "actual_validation_error_message": str(error),
                "production_observations_invented": False,
                "qualifies_current_engine": False,
            }
            break
    if failure is None:
        after = snapshot_current_graph()
        require(after == graph,
                "a genuine source or native ELF changed around actual V15 ownership")
    original_owner.core.ensure_candidate_free()
    report = build_report(
        current, graph, history, controls, controller,
        strict=strict, observations=observations, failure=failure,
        base_document=base_document, base_digest=base_report_sha256,
    )
    path, digest, publication_receipt = write_report(report, strict=strict)
    return {
        "schema": SCHEMA + "-durable-audit-summary",
        "status": report["status"], "result": report["result"],
        "passed": report["passed"],
        "mode": "strict-no-delegation" if strict else "independent-native-ownership",
        "report_path": path, "report_sha256": digest,
        "actual_exclusive_publication_receipt": publication_receipt,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": controller["source_sha256"],
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "strict_base_report_sha256": base_report_sha256,
        "verified_core_family_count": 3,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "completed_native_owner_worker_count":
            report["completed_native_owner_worker_count"],
        "preserved_zig_failure_sha256": ZIG_PRODUCER_FAILURE_SHA256,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (AuditV15Error, v11.ProofV11Error, original_owner.AuditV10Error,
            original_strict.AuditV10Error,
            original_owner.source_v6.AuditV6Error,
            original_owner.core.AuditV3Error,
            AssertionError, OSError, ValueError, TypeError, KeyError,
            UnicodeError):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def synthetic_v13_first_failure_document() -> dict[str, Any]:
    lines = ["source-only historical V13 traceback line " + str(index)
             for index in range(34)]
    lines[4] = "  authenticate_historical_audits()"
    lines[17] = "  contract.validate_edge_document(document, spec, archive, path)"
    lines[33] = "AssertionError: " + V13_FIRST_FAILURE_MESSAGE
    return {
        "schema": V13_FIRST_FAILURE_SCHEMA,
        "status": "FAIL", "synthetic": False,
        "actual_exception_type": "AssertionError",
        "actual_exception_message": V13_FIRST_FAILURE_MESSAGE,
        "actual_native_owner_workers_started": 0,
        "current_build_qualified": False,
        "historical_failure_qualifies_current_build": False,
        "failure_stage": "historical-zig-edge-preflight",
        "actual_invocation": {
            "arguments": [str(v11.PINNED_EXECUTABLE), "-I", "-B",
                          V13_SOURCE_RELATIVE, "--ownership-audit"],
            "executable": str(v11.PINNED_EXECUTABLE),
            "exit_code": 1,
            "output_capture":
                "complete combined command output; stdout and stderr "
                "were not separately captured",
        },
        "controller": {
            "source_path": V13_SOURCE_RELATIVE,
            "source_sha256": V13_SOURCE_SHA256,
            "protocol_path": V13_PROTOCOL_RELATIVE,
            "protocol_sha256": V13_PROTOCOL_SHA256,
        },
        "complete_captured_combined_output_lines": lines,
        "fresh_ownership_failure_report": "NOT CREATED",
        "fresh_ownership_report": "NOT CREATED",
        "fresh_strict_failure_report": "NOT CREATED",
        "fresh_strict_report": "NOT CREATED",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def synthetic_v13_first_failure_summary() -> dict[str, Any]:
    return {
        "failure_path": V13_FIRST_FAILURE_RELATIVE,
        "failure_sha256": V13_FIRST_FAILURE_SHA256,
        "failure_schema": V13_FIRST_FAILURE_SCHEMA,
        "status": "FAIL",
        "failed_stage": "historical-zig-edge-preflight",
        "actual_error_type": "AssertionError",
        "actual_error_message": V13_FIRST_FAILURE_MESSAGE,
        "actual_exit_code": 1,
        "native_owner_workers_started": 0,
        "original_edge_worker_started": False,
        "synthetic": False,
        "qualifies_current_engine": False,
        "v13_source_path": V13_SOURCE_RELATIVE,
        "v13_source_sha256": V13_SOURCE_SHA256,
        "v13_protocol_path": V13_PROTOCOL_RELATIVE,
        "v13_protocol_sha256": V13_PROTOCOL_SHA256,
        "stdout_capture": "NOT CAPTURED",
        "stderr_capture": "NOT CAPTURED",
        "combined_traceback_line_count": 34,
        "combined_traceback_separately_captured": False,
        "fresh_ownership_report": "NOT CREATED",
        "fresh_ownership_failure_report": "NOT CREATED",
        "fresh_strict_report": "NOT CREATED",
        "fresh_strict_failure_report": "NOT CREATED",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }

def synthetic_history() -> dict[str, Any]:
    categories = {"source-only-repr-pattern": 18, "source-only-repr-match": 8}
    zig = {
        "candidate_family": "ZIG", "candidate_module": "candidates.zig_candidate",
        "invalidated_path": ZIG_INVALIDATED_RELATIVE,
        "invalidated_sha256": ZIG_INVALIDATED_SHA256,
        "producer_failure_path": ZIG_PRODUCER_FAILURE_RELATIVE,
        "producer_failure_sha256": ZIG_PRODUCER_FAILURE_SHA256,
        "retry_failure_proof_path": ZIG_RETRY_FAILURE_RELATIVE,
        "retry_failure_proof_sha256": ZIG_RETRY_FAILURE_SHA256,
        "actual_child_exit_code": 1, "deep_checks": 393,
        "seeded_case_count": 64, "public_mismatch_count": 26,
        "public_mismatch_family_counts": categories,
        "actual_candidate_observation_sha256": v11.synthetic_digest("source-only-zig"),
        "actual_reference_observation_sha256": v11.DEEP_REFERENCE_SHA256,
        "first_v11_failure_sha256": v12.PRIOR_FAILURE_SHA256,
        "first_v11_invalidated_sha256": v12.PRIOR_INVALIDATED_SHA256,
        "qualifies_current_engine": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return {
        "historical_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "historical_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "historical_v10_graph_qualifies_current_engine": False,
        "preserved_original_v11_failure": {
            "actual_v11_first_invocation_status": "FAIL",
            "actual_v11_first_failure_sha256": v12.PRIOR_FAILURE_SHA256,
            "actual_v11_first_invalidated_original_sha256": v12.PRIOR_INVALIDATED_SHA256,
            "first_failure_retroactively_qualified": False,
        },
        "preserved_immutable_original_history": {
            "historical_current_build_edge_failures": {
                family: {"status": "FAIL", "qualifies_current_engine": False}
                for family in CORE_FAMILIES
            },
            "genuine_v8_preimport_owner_failure": {"status": "FAIL"},
            "genuine_v9_cached_compiler_owner_failure": {"status": "FAIL"},
        },
        "preserved_zig_failure": zig,
        "preserved_v13_first_audit_failure": synthetic_v13_first_failure_summary(),
    }


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime_source_only()
    inherited_owner = original_owner.candidate_free_self_test()
    inherited_strict = original_strict.candidate_free_self_test()
    inherited_failed_v13 = failed_v13.candidate_free_self_test()
    owner_summary = summarize_controls(inherited_owner)
    strict_summary = summarize_controls(inherited_strict)
    source = v11.read_regular(ROOT / SOURCE_RELATIVE, "source-only additive V15 controller")
    protocol = v11.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    actual_source_sha256 = hashlib.sha256(source).hexdigest()
    tree = ast.parse(source.decode("utf-8"), filename=SOURCE_RELATIVE)
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    with v11.source_only_boundary() as effects:
        accept("parse-exact-additive-v15-controller-source", isinstance(tree, ast.Module))
        accept("authenticate-exact-frozen-v15-protocol-source",
               hashlib.sha256(protocol).hexdigest() == PROTOCOL_SHA256)
        accept("authenticate-exact-future-independent-v15-source-without-prediction",
               original_owner.core.valid_sha256(actual_source_sha256))
        accept("preserve-authentic-complete-v10-native-owner-source-controls",
               owner_summary["check_count"] >= 150)
        accept("preserve-authentic-independent-v10-strict-source-controls",
               strict_summary["check_count"] >= 150)
        accept("retain-genuine-immutable-failed-v13-source-only-control-boundary",
               inherited_failed_v13.get("status") == "PASS"
               and inherited_failed_v13.get("check_count", 0) >= 150
               and inherited_failed_v13.get("candidate_imports") == 0
               and inherited_failed_v13.get("subprocesses") == 0
               and inherited_failed_v13.get("historical_evidence_reads") == 0
               and inherited_failed_v13.get("actual_audit_report_reads") == 0
               and inherited_failed_v13.get("synthetic_results_qualify_candidates") is False)
        for name, actual, expected in (
            ("v13-failed-source", V13_SOURCE_SHA256,
             "4570798942ab884c1a760b9685ef1a67379febd1c0da81aa18eef221126758fe"),
            ("v13-failed-protocol", V13_PROTOCOL_SHA256,
             "f325fe84dc4d14363e3dd4a6038866d8bc2aacd59625231f7dffc4c73257c0c3"),
            ("v13-actual-preworker-failure", V13_FIRST_FAILURE_SHA256,
             "465820b50be4d544199844d7bde4c5b8e58391828bdb1c716cc33c50ca6c964b"),
            ("v10-owner", V10_OWNER_SOURCE_SHA256,
             "0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505"),
            ("v10-strict", V10_STRICT_SOURCE_SHA256,
             "885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95"),
            ("v10-protocol", V10_PROTOCOL_SHA256,
             "902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6"),
            ("v10-actual-base", ACTUAL_V10_BASE_REPORT_SHA256,
             "589321a768e10c52f039a68acb211574ec884598771ede2152f91994cc69f353"),
            ("v10-actual-strict", ACTUAL_V10_STRICT_REPORT_SHA256,
             "d8f31dd480bdba530a454b38428a23ef347c6e3cce7796f8992d6e7767381f4b"),
            ("zig-actual-invalidated", ZIG_INVALIDATED_SHA256,
             "d7f11c33a010406db1637e0715e72bfebdc13acf21118735b6b1f6e550927865"),
            ("zig-actual-producer-failure", ZIG_PRODUCER_FAILURE_SHA256,
             "5c3e07d9f11d5c8244d3d22fc94f287f4f0573423bf38e70b6abc383c96eca90"),
            ("zig-actual-retry-failure-proof", ZIG_RETRY_FAILURE_SHA256,
             "b5deb6c3ce522fe0dbc3c4e723867ffe830520f0a47a0b72cc5b1d9a0a69ad9d"),
            ("first-v11-actual-crash", v12.PRIOR_FAILURE_SHA256,
             "360d430666bfae146eb9abc18cab2bcd9822096f78e6f21ed3b938bb50631c39"),
            ("first-v11-actual-invalidated", v12.PRIOR_INVALIDATED_SHA256,
             "9cc30b172575c83b399f680057a6d33ae952e44f920079c3d8c3b67566afb407"),
        ):
            accept("preserve-real-frozen-independent-history-without-evidence-read:" + name,
                   actual == expected and original_owner.core.valid_sha256(actual))
        environment = {
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        }
        accept("accept-only-the-complete-synthetic-isolated-parent-environment",
               validate_parent_environment(environment) == environment)
        for key in environment:
            changed = dict(environment)
            del changed[key]
            checks.append(rejected("reject-missing-genuine-production-parent-key:" + key,
                                   lambda row=changed: validate_parent_environment(row)))
            for label, value in (
                ("none", None), ("empty", ""), ("integer", 1),
                ("false", "false"), ("space", " "), ("other", "source-only-forged"),
            ):
                forged = {**environment, key: value}
                checks.append(rejected(
                    "reject-invalid-genuine-production-parent-key:" + key + ":" + label,
                    lambda row=forged: validate_parent_environment(row),
                ))
        for label, value in (
            ("relative", "."), ("trailing-separator", str(ROOT) + "/"),
            ("additional-root", str(ROOT) + os.pathsep + "/tmp"),
            ("temporary-root", "/tmp"),
            ("parent-alias", str(ROOT / ".." / ROOT.name)),
        ):
            checks.append(rejected(
                "reject-noncanonical-real-parent-pythonpath:" + label,
                lambda changed=value: validate_parent_environment({
                    **environment, "PYTHONPATH": changed,
                }),
            ))
        for family in CORE_FAMILIES:
            worker, native = original_owner.synthetic_worker(family)
            validated = validate_native_owner(copy.deepcopy(worker), family, native)
            accept("validate-complete-original-guarded-v10-native-owner:" + family,
                   validated["family"] == family)
            for field, replacement in (
                ("status", "FAIL"), ("result", "FAIL"), ("passed", False),
                ("family", "source-only-foreign-family"),
                ("candidate_module", "candidates.foreign_engine"),
                ("match_repr_checks", 1),
                ("standard_pickle_check_count", 15),
                ("standard_pickle_failure_count", 1),
                ("regex_guard_count", 12),
                ("native_loader_guard_count", 4),
                ("persistent_cross_engine_guard", False),
                ("genuine_matching_executed", False),
                ("external_regex_packages", 1),
                ("benchmark_or_timing_executed", True),
                ("holdout_or_case_fixture_access", True),
                ("schema", "forged-owner"),
                ("native_binary_sha256", {}),
                ("stage07_guard_sentinel", {}),
                ("stage07_matcher_descendant_guards", {}),
                ("regex_guard_observations", []),
                ("regex_guard_observations_after", []),
                ("native_loader_guard_observations", []),
                ("native_loader_guard_observations_after", []),
                ("standard_pickle_checks", []),
            ):
                forged = copy.deepcopy(worker)
                forged[field] = replacement
                checks.append(rejected(
                    "reject-foreign-or-weakened-actual-v10-native-owner:"
                    + family + ":" + field,
                    lambda row=forged, selected=family, actual=native:
                        validate_native_owner(row, selected, actual),
                ))
            for other in CORE_FAMILIES:
                if other != family:
                    checks.append(rejected(
                        "reject-cross-family-original-native-owner:"
                        + family + ":" + other,
                        lambda row=copy.deepcopy(worker), selected=other,
                        actual=native: validate_native_owner(row, selected, actual),
                    ))
        paths = (
            BASE_REPORT_RELATIVE, BASE_FAILURE_RELATIVE,
            STRICT_REPORT_RELATIVE, STRICT_FAILURE_RELATIVE,
        )
        for path in paths:
            accept("authorize-only-distinct-exclusive-v15-audit-destination:" + path,
                   destination_name(path) == path)
        for name, value in (
            ("old-v10-owner", original_owner.REPORT_RELATIVE),
            ("old-v10-owner-failure", original_owner.FAILURE_RELATIVE),
            ("old-v10-strict", original_strict.REPORT_RELATIVE),
            ("old-v10-strict-failure", original_strict.FAILURE_RELATIVE),
            ("actual-v12-zig-invalidated", ZIG_INVALIDATED_RELATIVE),
            ("actual-v12-zig-producer-failure", ZIG_PRODUCER_FAILURE_RELATIVE),
            ("actual-v12-zig-retry-failure", ZIG_RETRY_FAILURE_RELATIVE),
            ("holdout", "performance/private-holdout.json"),
            ("relative-parent", "../POSTFINAL-FROM-SCRATCH-AUDIT-V15.json"),
            ("absolute", "/tmp/POSTFINAL-FROM-SCRATCH-AUDIT-V15.json"),
            ("windows", "candidates\\audits\\forged.json"),
            ("nul", "candidates/audits/forged\x00.json"),
        ):
            checks.append(rejected("reject-foreign-or-occupied-v15-output:" + name,
                                   lambda target=value: destination_name(target)))
        history = synthetic_history()
        accept("retain-all-real-historical-failures-without-reading-any-evidence",
               validate_preserved_history(copy.deepcopy(history))
               ["historical_v10_graph_qualifies_current_engine"] is False)
        zig = history["preserved_zig_failure"]
        for key in tuple(zig):
            forged = copy.deepcopy(zig)
            forged[key] = None if forged[key] is not None else "source-only-forged"
            checks.append(rejected(
                "reject-forged-complete-genuine-v12-zig-failure:" + key,
                lambda row=forged: validate_zig_failure_summary(row),
            ))
        for key in (
            "historical_v10_base_report_sha256",
            "historical_v10_strict_report_sha256",
            "historical_v10_graph_qualifies_current_engine",
            "preserved_original_v11_failure",
            "preserved_immutable_original_history",
            "preserved_zig_failure",
            "preserved_v13_first_audit_failure",
        ):
            forged = copy.deepcopy(history)
            forged[key] = None if forged[key] is not None else "forged"
            checks.append(rejected("reject-forged-preserved-v15-immutable-history:" + key,
                                   lambda row=forged: validate_preserved_history(row)))
        synthetic = original_strict.synthetic_base({
            "base_source": V10_OWNER_SOURCE_SHA256,
            "base_report": v11.synthetic_digest("source-only-v15-legacy-base"),
        })
        graph = full_graph(synthetic)
        controller = {
            "source_path": SOURCE_RELATIVE,
            "source_sha256": actual_source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": PROTOCOL_SHA256,
        }
        workers = {
            family: original_owner.synthetic_worker(family)[0]
            for family in CORE_FAMILIES
        }
        synthetic_controls = {
            "schema": SCHEMA + "-self-test", "status": "PASS", "passed": True,
            "check_count": 150, "candidate_imports": 0, "subprocesses": 0,
            "file_reads": 0, "file_writes": 0, "clock_samples": 0,
            "historical_evidence_reads": 0, "actual_audit_report_reads": 0,
            "synthetic_results_qualify_candidates": False,
        }
        base_report = build_report(
            synthetic, graph, history, synthetic_controls, controller,
            strict=False, observations=workers, failure=None,
        )
        base_digest = hashlib.sha256(canonical(base_report)).hexdigest()
        accept("validate-entire-synthetic-all-family-v15-owner-report-without-production",
               validate_base_report(copy.deepcopy(base_report), base_digest) == graph)
        strict_report = build_report(
            synthetic, graph, history, synthetic_controls, controller,
            strict=True, observations=workers, failure=None,
            base_document=base_report, base_digest=base_digest,
        )
        strict_digest = hashlib.sha256(canonical(strict_report)).hexdigest()
        accept("validate-entire-synthetic-all-family-v15-strict-report-without-production",
               validate_strict_report(copy.deepcopy(strict_report), base_digest, strict_digest)
               == graph)
        for role, document, digest in (
            ("base", base_report, base_digest),
            ("strict", strict_report, strict_digest),
        ):
            security_fields = {
                "schema", "postfinal_schema", "status", "result", "passed",
                "audit_source_path", "audit_source_sha256", "audit_protocol_path",
                "audit_protocol_sha256", "v10_native_owner_source_path",
                "v10_native_owner_source_sha256", "v10_no_delegation_source_path",
                "v10_no_delegation_source_sha256", "v10_native_ownership_protocol_path",
                "v10_native_ownership_protocol_sha256", "native_owner_worker_sha256",
                "historical_v10_graph_qualifies_current_engine",
                "historical_zig_failure_qualifies_current_engine",
                "preserved_immutable_history", "preserved_zig_failure",
                "preserved_v13_failure",
                "postfinal_wrapper_self_test", "verified_core_family_count",
                "verified_distinct_pipeline_count", "verified_candidate_source_count",
                "verified_candidate_source_paths", "source_sha256_by_family",
                "verified_native_role_count", "native_sha256_by_family",
                "actual_native_owner_workers", "actual_native_owner_worker_failure",
                "completed_native_owner_worker_count", "verified_match_repr_checks",
                "verified_standard_pickle_count", "standard_pickle_failure_count",
                "genuine_python_matching_guards_per_family",
                "genuine_native_loader_guards_per_family", "strict_base_report_path",
                "strict_base_report_sha256", "independent_base_native_owner_workers",
                "postfinal_scope", "benchmark_or_timing_executed",
                "holdout_or_case_fixture_access", "performance", "holdout",
                "families", "native_elf_provenance", "manifest_provenance",
                "runtime_native_mapping_provenance",
            }
            for key in tuple(key for key in document if key in security_fields):
                forged = copy.deepcopy(document)
                forged[key] = None if forged[key] is not None else "source-only-forged"
                forged_digest = hashlib.sha256(canonical(forged)).hexdigest()
                action = (
                    (lambda row=forged, value=forged_digest:
                     validate_base_report(row, value)) if role == "base"
                    else (lambda row=forged, value=forged_digest:
                          validate_strict_report(row, base_digest, value))
                )
                checks.append(rejected(
                    "reject-recanonicalized-forged-complete-v15-report:" + role + ":" + key,
                    action,
                ))
            for label, bad in (
                ("missing", None), ("empty", ""), ("invalid", "invalid"),
                ("all-zero", "0" * 64),
                ("historical-v10-base", ACTUAL_V10_BASE_REPORT_SHA256),
                ("historical-v10-strict", ACTUAL_V10_STRICT_REPORT_SHA256),
                ("source-digest", actual_source_sha256),
                ("protocol-digest", PROTOCOL_SHA256),
            ):
                action = (
                    (lambda value=bad: validate_base_report(base_report, value))
                    if role == "base"
                    else (lambda value=bad:
                          validate_strict_report(strict_report, base_digest, value))
                )
                checks.append(rejected(
                    "reject-guessed-historical-or-false-v15-report-hash:"
                    + role + ":" + label,
                    action,
                ))
        for name in (
            "run_native_worker", "validate_worker", "_validate_fresh_graph",
            "audit", "audit_v11_reports", "authenticate_history",
            "validate_deep", "validate_edge_shape",
            "restore_complete_stream", "fresh_target",
        ):
            accept("require-original-independently-frozen-audit-primitive:" + name,
                   any(isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Attribute)
                       and node.func.attr == name for node in ast.walk(tree)))
        for name in (
            "postfinal_from_scratch_audit_v10",
            "postfinal_no_delegation_audit_v10",
            "postfinal_current_build_proofs_v11",
            "postfinal_current_build_proofs_v12",
            "postfinal_independent_engine_audit_v13",
        ):
            accept("retain-exact-original-frozen-independently-owned-module:" + name,
                   any(isinstance(node, ast.ImportFrom)
                       and any(item.name == name for item in node.names)
                       for node in ast.walk(tree)))
        for label, action in (
            ("builtin-candidate", lambda: builtins.__import__("candidates.rust_candidate")),
            ("builtin-third-party", lambda: builtins.__import__("regex")),
            ("importlib-candidate", lambda: importlib.import_module("candidates.zig_candidate")),
            ("importlib-third-party", lambda: importlib.import_module("pcre2")),
            ("actual-v10-owner-report",
             lambda: v11.read_regular(ROOT / original_owner.REPORT_RELATIVE,
                                      "forbidden actual V10 owner audit")),
            ("actual-v10-strict-report",
             lambda: v11.read_regular(ROOT / original_strict.REPORT_RELATIVE,
                                      "forbidden actual V10 strict audit")),
            ("actual-v13-first-preworker-failure",
             lambda: v11.read_regular(ROOT / V13_FIRST_FAILURE_RELATIVE,
                                      "forbidden genuine first V13 historical failure")),
            ("actual-zig-original-failure",
             lambda: v11.read_regular(ROOT / ZIG_INVALIDATED_RELATIVE,
                                      "forbidden actual original Zig failure")),
            ("actual-zig-producer-failure",
             lambda: v11.read_regular(ROOT / ZIG_PRODUCER_FAILURE_RELATIVE,
                                      "forbidden actual original Zig producer")),
            ("actual-zig-retry-proof",
             lambda: v11.read_regular(ROOT / ZIG_RETRY_FAILURE_RELATIVE,
                                      "forbidden actual Zig retry proof")),
            ("actual-future-v15-owner",
             lambda: v11.read_regular(ROOT / BASE_REPORT_RELATIVE,
                                      "forbidden real future V15 owner")),
            ("actual-future-v15-strict",
             lambda: v11.read_regular(ROOT / STRICT_REPORT_RELATIVE,
                                      "forbidden real future V15 strict")),
            ("holdout", lambda: builtins.open(ROOT / "performance/holdout.json", "rb")),
            ("unrelated", lambda: builtins.open(ROOT / "README.md", "rb")),
            ("worker", lambda: subprocess.run(["forbidden-v15-owner"])),
            ("temporary-directory", lambda: tempfile.TemporaryDirectory()),
            ("clock", lambda: time.perf_counter()),
            ("report-write", lambda: (ROOT / BASE_REPORT_RELATIVE).write_bytes(b"x")),
            ("candidate-write", lambda: (ROOT / "candidates/forbidden-v15").write_text("x")),
        ):
            checks.append(rejected("enforce-entire-genuine-v15-source-only-boundary:" + label,
                                   action))
        historical_document = synthetic_v13_first_failure_document()
        incident = synthetic_v13_first_failure_summary()
        accept("validate-entire-real-shape-first-v13-merged-34-line-traceback",
               validate_v13_first_failure_document(
                   copy.deepcopy(historical_document),
               ) == incident)
        for field in tuple(historical_document):
            forged_document = copy.deepcopy(historical_document)
            forged_document[field] = (
                None if forged_document[field] is not None
                else "source-only-forged-full-first-v13-traceback"
            )
            checks.append(rejected(
                "reject-forged-full-actual-v13-preworker-incident:" + field,
                lambda row=forged_document: validate_v13_first_failure_document(row),
            ))
        accept("validate-authentic-failed-v13-preworker-history-source-only",
               validate_v13_first_failure_summary(copy.deepcopy(incident))
               ["native_owner_workers_started"] == 0)
        for field in tuple(incident):
            forged = copy.deepcopy(incident)
            forged[field] = (
                None if forged[field] is not None
                else "source-only-forged-preworker-history"
            )
            checks.append(rejected(
                "reject-forged-complete-real-v13-first-preworker-failure:" + field,
                lambda row=forged: validate_v13_first_failure_summary(row),
            ))
        historical_fn = next(
            (node for node in tree.body
             if isinstance(node, ast.FunctionDef)
             and node.name == "authenticate_historical_audits"),
            None,
        )
        pure_edge_fn = next(
            (node for node in tree.body
             if isinstance(node, ast.FunctionDef)
             and node.name == "historical_edge_proof"),
            None,
        )
        accept("authenticate-historical-original-edge-with-exact-old-graph",
               isinstance(historical_fn, ast.FunctionDef)
               and isinstance(pure_edge_fn, ast.FunctionDef))
        for forbidden in (
            "validate_original_edge", "validate_edge_document",
            "authenticate_qualified_edge", "snapshot_family",
            "snapshot_current_graph", "run_native_worker", "sha256_path",
        ):
            accept("forbid-live-native-validation-during-historical-replay:" + forbidden,
                   isinstance(historical_fn, ast.FunctionDef)
                   and not any(
                       isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Attribute)
                       and node.func.attr == forbidden
                       for node in ast.walk(historical_fn)
                   )
                   and isinstance(pure_edge_fn, ast.FunctionDef)
                   and not any(
                       isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Attribute)
                       and node.func.attr == forbidden
                       for node in ast.walk(pure_edge_fn)
                   ))
        for required in (
            "validate_edge_shape", "frozen_embedded_oracles",
            "expected_edge_paths",
        ):
            accept("prove-old-graph-original-edge-with-genuine-frozen-shape:" + required,
                   isinstance(pure_edge_fn, ast.FunctionDef)
                   and any(
                       isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Attribute)
                       and node.func.attr == required
                       for node in ast.walk(pure_edge_fn)
                   ))
        synthetic_receipt = {
            "schema": SCHEMA + "-actual-exclusive-publication-receipt",
            "status": "PASS",
            "report_path": BASE_REPORT_RELATIVE,
            "report_sha256": base_digest,
            "expected_bytes": 17,
            "actual_bytes_written": 17,
            "actual_write_calls": [
                {"requested_bytes": 17, "returned_bytes": 6},
                {"requested_bytes": 11, "returned_bytes": 11},
            ],
            "exclusive_create_succeeded": True,
            "file_fsync_succeeded": True,
            "parent_directory_fsync_succeeded": True,
            "canonical_reread_succeeded": True,
            "production_observations_invented": False,
        }
        accept("validate-genuine-partial-write-continuation-source-only",
               validate_publication_receipt(
                   copy.deepcopy(synthetic_receipt),
                   BASE_REPORT_RELATIVE, base_digest, 17,
               ) == synthetic_receipt)
        for field in tuple(synthetic_receipt):
            forged_receipt = copy.deepcopy(synthetic_receipt)
            forged_receipt[field] = (
                None if forged_receipt[field] is not None
                else "source-only-forged-partial-write"
            )
            checks.append(rejected(
                "reject-fabricated-exclusive-write-fsync-receipt:" + field,
                lambda row=forged_receipt: validate_publication_receipt(
                    row, BASE_REPORT_RELATIVE, base_digest, 17,
                ),
            ))
        for index, key in (
            (0, "requested_bytes"), (0, "returned_bytes"),
            (1, "requested_bytes"), (1, "returned_bytes"),
        ):
            forged_receipt = copy.deepcopy(synthetic_receipt)
            forged_receipt["actual_write_calls"][index][key] = 0
            checks.append(rejected(
                "reject-fabricated-partial-write-syscall:"
                + str(index) + ":" + key,
                lambda row=forged_receipt: validate_publication_receipt(
                    row, BASE_REPORT_RELATIVE, base_digest, 17,
                ),
            ))
        accept("actively-block-candidate-and-external-engine-imports",
               effects["candidate_import_attempts_blocked"] >= 4)
        accept("actively-block-real-history-audit-holdout-and-candidate-reads",
               effects["evidence_read_attempts_blocked"] >= 8)
        accept("actively-block-genuine-process-and-worker-starts",
               effects["worker_attempts_blocked"] >= 2)
        accept("actively-block-genuine-real-filesystem-writes",
               effects["write_attempts_blocked"] >= 2)
        accept("actively-block-genuine-real-clock-sampling",
               effects["clock_attempts_blocked"] >= 1)
        accept("never-import-any-candidate-into-the-independent-audit-controller",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
        accept("retain-at-least-150-distinct-v15-actual-adversarial-source-controls",
               len(checks) >= 150)
        require(len({row["name"] for row in checks}) == len(checks),
                "the complete independent V15 source checks duplicated a denominator")
        failed_controls = [row["name"] for row in checks if not row["passed"]]
        require(not failed_controls,
                "a real current V15 native ownership or source-only poison escaped: "
                + ", ".join(failed_controls[:12]))
        observed = dict(effects)
    verify_runtime_source_only()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS",
        "result": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "v10_owner_control_count": inherited_owner["check_count"],
        "v10_strict_control_count": inherited_strict["check_count"],
        "failed_v13_control_count": inherited_failed_v13["check_count"],
        "preserved_v13_first_failure_sha256": V13_FIRST_FAILURE_SHA256,
        "historical_replay_uses_current_candidate_files": False,
        "historical_merged_stream_separately_captured": False,
        "candidate_imports": 0, "subprocesses": 0,
        "file_reads": 0, "file_writes": 0, "clock_samples": 0,
        "historical_evidence_reads": 0, "actual_audit_report_reads": 0,
        "holdout_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": actual_source_sha256,
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "actual_v10_owner_source_sha256": V10_OWNER_SOURCE_SHA256,
        "actual_v10_strict_source_sha256": V10_STRICT_SOURCE_SHA256,
        "actual_v10_ownership_protocol_sha256": V10_PROTOCOL_SHA256,
        "actual_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "actual_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "preserved_zig_invalidated_sha256": ZIG_INVALIDATED_SHA256,
        "preserved_zig_producer_failure_sha256": ZIG_PRODUCER_FAILURE_SHA256,
        "preserved_zig_retry_failure_sha256": ZIG_RETRY_FAILURE_SHA256,
        "independent_family_count": 3,
        "owned_source_count": 12, "owned_native_binary_count": 5,
        "actual_matching_guards_required_per_family": 13,
        "actual_native_loader_guards_required_per_family": 5,
        "genuine_pickle_checks_required_per_family": 16,
        "blocked_effect_attempts": observed,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--ownership-audit", action="store_true")
    modes.add_argument("--strict-audit", action="store_true")
    parser.add_argument("--base-report-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(options.base_report_sha256 is None,
                "a source-only V15 control must not consume an actual report digest")
        report = candidate_free_self_test()
    elif options.ownership_audit:
        require(options.base_report_sha256 is None,
                "a real V15 owner audit cannot borrow a strict report hash")
        report = run_audit(strict=False)
    else:
        require(options.strict_audit,
                "V15 allows only an independent genuine strict ownership audit")
        report = run_audit(strict=True, base_report_sha256=options.base_report_sha256)
    print(json.dumps(report, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditV15PublicationFailure as error:
        print(json.dumps({
            "schema": SCHEMA + "-actual-exclusive-publication-failure",
            "status": "FAIL",
            "actual_error_message": str(error),
            "actual_exclusive_publication_receipt": error.receipt,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")),
            file=sys.stderr, flush=True)
        raise SystemExit(1) from error
