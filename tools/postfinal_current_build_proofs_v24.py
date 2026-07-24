#!/usr/bin/env python3
"""Bind complete original correctness to three audited from-scratch engines."""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import gzip
import hashlib
import importlib
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
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_current_build_proofs_v22 as failed


original = failed.original
legacy = failed.legacy
historical_v14 = failed.historical_v14
SCHEMA = "rebar-postfinal-current-build-proofs-v24"
SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v24.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V24.md"
PROTOCOL_SHA256 = (
    "f3ab4f5c3c697a6d39c109b743d949b980bfe0d79aeb6b58a0bc392a3f81e534"
)
V22_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v22.py"
V22_SOURCE_SHA256 = (
    "ba3062b5fe4aea944e89022266c8d9a7a035708bb30d736f074fc29ce7157e27"
)
V22_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V22.md"
V22_PROTOCOL_SHA256 = (
    "e06a24155ca95bf287a5dece90d1a385dad806de8512f177d3146c7bba7acc29"
)
V22_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-CURRENT-BUILD-V22-READONLY-INTEGRATION-PREFLIGHT-FAILURE.json"
)
V22_FAILURE_SHA256 = (
    "c6e765f142f25667dd0e7dab45ff16a60abcaae6e230ba05acc596a72d304b01"
)
V22_FAILURE_SCHEMA = (
    "rebar-postfinal-current-build-proof-v22-"
    "actual-read-only-integration-preflight-failure"
)
V21_SOURCE_RELATIVE = failed.V21_SOURCE_RELATIVE
V21_PROTOCOL_RELATIVE = failed.V21_PROTOCOL_RELATIVE
V21_SOURCE_SHA256 = (
    "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
)
V21_PROTOCOL_SHA256 = (
    "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
)
V21_BASE_REPORT_RELATIVE = failed.V21_BASE_REPORT_RELATIVE
V21_STRICT_REPORT_RELATIVE = failed.V21_STRICT_REPORT_RELATIVE
V21_SCHEMA = failed.V21_SCHEMA
V21_BASE_SCHEMA = failed.V21_BASE_SCHEMA
V21_STRICT_SCHEMA = failed.V21_STRICT_SCHEMA
V13_FAILURE_RELATIVE = failed.V13_FAILURE_RELATIVE
V13_FAILURE_SHA256 = failed.V13_FAILURE_SHA256
V15_FAILURE_RELATIVE = failed.V15_FAILURE_RELATIVE
V15_FAILURE_SHA256 = failed.V15_FAILURE_SHA256
V17_FAILURE_RELATIVE = failed.V17_FAILURE_RELATIVE
V17_FAILURE_SHA256 = failed.V17_FAILURE_SHA256
V19_FAILURE_RELATIVE = failed.V19_FAILURE_RELATIVE
V19_FAILURE_SHA256 = failed.V19_FAILURE_SHA256
V19_DURABLE_REPORT_SHA256 = failed.V19_DURABLE_REPORT_SHA256
V19_DURABLE_REPORT_BYTES = failed.V19_DURABLE_REPORT_BYTES
PIN_NAMES = tuple(failed.PIN_NAMES)
FAMILIES = tuple(failed.FAMILIES)
PURPOSES = tuple(failed.PURPOSES)
RECEIPT_FIELDS = (*failed.RECEIPT_FIELDS, "actual_write_calls")
TRUE_V13_FAILURE_STAGE = (
    "historical-zig-edge-authentication-before-any-new-native-owner-worker"
)
FAILED_V13_FAILURE_STAGE = "historical-zig-edge-preflight"
LOST_FAILED_BOUNDARY = "NOT PRESERVED BY THE FAILED CONTROLLER"


class ProofV24Error(AssertionError):
    """A genuine original, audited owner, or exact historical incident failed."""


class V24PublicationFailure(ProofV24Error):
    """Retain every actually completed exclusive-publication transition."""

    def __init__(
        self,
        message: str,
        *,
        stage: str,
        receipt: Mapping[str, Any],
        cause: BaseException,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.receipt = copy.deepcopy(dict(receipt))
        self.cause = cause


class ProofV24Failure(ProofV24Error):
    """Expose only a genuinely published failed-worker observation."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = copy.deepcopy(dict(evidence))


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ProofV24Error(message)


def verify_runtime_source_only() -> None:
    failed.verify_runtime_source_only()
    require(
        ROOT == original.ROOT
        and Path(__file__).resolve() == ROOT / SOURCE_RELATIVE
        and FAMILIES == ("rust", "vm", "zig")
        and tuple(original.FAMILIES) == FAMILIES
        and original.EDGE_CHECKS == 223198
        and original.EDGE_CATEGORIES == 49
        and original.DEEP_CHECKS == 393
        and original.DEEP_SEEDED_CASES == 64
        and sum(len(row["sources"]) for row in original.FAMILIES.values()) == 12
        and sum(len(row["native"]) for row in original.FAMILIES.values()) == 5
        and len(failed.RECEIPT_FIELDS) == 17
        and len(RECEIPT_FIELDS) == 18
        and len(set(RECEIPT_FIELDS)) == 18,
        "V24 requires the complete original 223198/49, 393/64, and 12/5 gates",
    )
    require(
        not any(
            name == "candidates"
            or name.startswith("candidates.")
            or name == "rebar"
            or name.startswith("rebar.")
            for name in sys.modules
        ),
        "a production candidate escaped into the V24 proof controller",
    )


def validate_parent_environment(environment: Mapping[str, Any]) -> dict[str, str]:
    return failed.validate_parent_environment(environment)


def worker_environment() -> dict[str, str]:
    return failed.worker_environment()


def checked_family(family: str) -> dict[str, Any]:
    require(
        type(family) is str and family in FAMILIES,
        "only an independently owned from-scratch Rust, C, or Zig engine is allowed",
    )
    return original.checked_family(family)


def validated_pins(supplied: Any) -> dict[str, str]:
    require(
        isinstance(supplied, Mapping) and set(supplied) == set(PIN_NAMES),
        "BLOCKED: supply four actual independently published V21 audit hashes",
    )
    result: dict[str, str] = {}
    for key in PIN_NAMES:
        value = supplied[key]
        require(
            original.valid_sha256(value),
            "BLOCKED: the independently published actual V21 "
            + key + " SHA-256 is required",
        )
        result[key] = value
    require(
        len(set(result.values())) == len(PIN_NAMES),
        "an independent audit source, protocol, or actual report hash was reused",
    )
    return result


def authenticate_controller() -> dict[str, str]:
    verify_runtime_source_only()
    prior = failed.authenticate_controller()
    require(
        prior.get("source_path") == V22_SOURCE_RELATIVE
        and prior.get("source_sha256") == V22_SOURCE_SHA256
        and prior.get("protocol_path") == V22_PROTOCOL_RELATIVE
        and prior.get("protocol_sha256") == V22_PROTOCOL_SHA256,
        "the genuine immutable failed V22 controller or protocol was replaced",
    )
    source = original.read_regular(
        ROOT / SOURCE_RELATIVE,
        "complete independently frozen V24 proof-controller source",
    )
    protocol = original.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": hashlib.sha256(protocol).hexdigest(),
        "frozen_failed_v22_source_path": V22_SOURCE_RELATIVE,
        "frozen_failed_v22_source_sha256": V22_SOURCE_SHA256,
        "frozen_failed_v22_protocol_path": V22_PROTOCOL_RELATIVE,
        "frozen_failed_v22_protocol_sha256": V22_PROTOCOL_SHA256,
        "frozen_failed_v22_incident_path": V22_FAILURE_RELATIVE,
        "frozen_failed_v22_incident_sha256": V22_FAILURE_SHA256,
        "frozen_failed_v22_qualifies_current_engine": False,
    }


def edge_target(family: str, passed: bool) -> Path:
    checked_family(family)
    require(type(passed) is bool, "an original edge requires its real result")
    result = "pass" if passed else "failures"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v24-qualified-" + result + ".json.gz"
    )


def edge_proof_target(family: str, passed: bool) -> Path:
    target = edge_target(family, passed)
    return target.parent / (target.name.removesuffix(".json.gz") + "-proof.json")


def deep_target(family: str, passed: bool) -> Path:
    metadata = checked_family(family)
    require(type(passed) is bool, "an original deep requires its real result")
    result = "PASS" if passed else "FAILURES"
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V24-" + result + ".json.gz"
    )


def deep_proof_target(family: str, passed: bool) -> Path:
    target = deep_target(family, passed)
    return target.parent / (target.name.removesuffix(".json.gz") + "-PROOF.json")


def failure_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool, "a real worker failure requires its actual mode")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V24-PRODUCER-CRASH.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v24-qualified-producer-crash.json.gz"
    )


def invalidated_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool, "a real invalidation requires its actual mode")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V24-"
            "INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v24-qualified-"
        "invalidated-after-owner-failure.json.gz"
    )


def expected_publication_target(
    family: str,
    *,
    deep: bool,
    passed: bool | None,
    purpose: str,
) -> Path:
    checked_family(family)
    require(
        type(deep) is bool and purpose in PURPOSES,
        "exclusive publication requires its exact family, mode, and purpose",
    )
    if purpose == "invalidated":
        return invalidated_target(family, deep=deep)
    if purpose == "failure":
        return failure_target(family, deep=deep)
    require(type(passed) is bool, "an original cannot invent its actual outcome")
    if purpose == "archive":
        return deep_target(family, passed) if deep else edge_target(family, passed)
    return deep_proof_target(family, passed) if deep else edge_proof_target(
        family,
        passed,
    )


def expected_v13_failure_summary() -> dict[str, Any]:
    result = copy.deepcopy(failed.expected_v13_failure_summary())
    require(
        len(result) == 26 and result.get("failed_stage") == FAILED_V13_FAILURE_STAGE,
        "the immutable failed V22 V13 differential changed",
    )
    result["failed_stage"] = TRUE_V13_FAILURE_STAGE
    return result


def expected_v15_failure_summary() -> dict[str, Any]:
    result = failed.expected_v15_failure_summary()
    require(len(result) == 28, "the complete authentic V15 failure was shortened")
    return result


def expected_v17_failure_summary() -> dict[str, Any]:
    result = failed.expected_v17_failure_summary()
    require(len(result) == 18, "the complete authentic V17 failure was shortened")
    return result


def expected_v19_failure_summary() -> dict[str, Any]:
    result = failed.expected_v19_failure_summary()
    require(len(result) == 36, "the complete authentic V19 failure was shortened")
    return result


def _v22_inline_source(pins: Mapping[str, str]) -> list[str]:
    root = json.dumps(str(ROOT), ensure_ascii=True)
    return [
        "import json,sys",
        "sys.path.insert(0," + root + ")",
        "from tools import postfinal_current_build_proofs_v22 as p",
        "from tools import postfinal_independent_engine_audit_v21 as a",
        'assert p.V21_SOURCE_SHA256=="' + V21_SOURCE_SHA256 + '"',
        'assert p.V21_PROTOCOL_SHA256=="' + V21_PROTOCOL_SHA256 + '"',
        'pins={"audit_source":p.V21_SOURCE_SHA256,'
        '"audit_protocol":p.V21_PROTOCOL_SHA256,'
        '"base_report":"' + pins["base_report"]
        + '","strict_report":"' + pins["strict_report"] + '"}',
        "rows=[]",
        "with a.read_only_history_boundary() as effects:",
        " for family in p.FAMILIES:",
        "  state=p.preflight(family,pins)",
        '  assert set(state)=={"v21","owner","v8","audits",'
        '"snapshot","history","preserved_incidents","controller",'
        '"parent_environment"}',
        '  assert state["v21"] is a and len(state["audits"])==11 '
        'and state["audits"]["pins"]==pins',
        '  graph=state["audits"]["graph"]',
        '  assert sum(len(z) for z in graph["source_sha256_by_family"].values())'
        '==12 and sum(len(z) for z in graph["native_sha256_by_family"].values())==5',
        '  for version,incident in (("v13","v13_first_owner_preflight_failure"),'
        '("v15","v15_first_owner_preflight_failure"),'
        '("v17","v17_first_owner_postflight_failure"),'
        '("v19","v19_first_owner_publication_failure")):',
        '   actual=state["audits"]["preserved_"+version+"_failure"]',
        '   assert actual==state["history"]["preserved_"+version+'
        '"_first_audit_failure"]==state["preserved_incidents"][incident]',
        '   assert state["preserved_incidents"]'
        '[incident+"_qualifies_current_engine"] is False',
        '  assert state["snapshot"]["family"]==family',
        '  assert not any(name=="candidates" or '
        'name.startswith("candidates.") for name in sys.modules)',
        '  rows.append({"family":family,"audit_roles":len(state["audits"]),'
        '"source_count":12,"native_binary_count":5,'
        '"authentic_preserved_failures":4})',
        ' assert [x["family"] for x in rows]==list(p.FAMILIES)',
        " assert all(value==0 for value in effects.values())",
        'print(json.dumps({"schema":'
        '"rebar-v22-root-all-family-zero-worker-actual-audit-integration-smoke",'
        '"status":"PASS","source_sha256":"' + V22_SOURCE_SHA256
        + '","protocol_sha256":"' + V22_PROTOCOL_SHA256
        + '","external_base_report_sha256":pins["base_report"],'
        '"external_strict_report_sha256":pins["strict_report"],'
        '"families":rows,"read_only_boundary_effects":effects,'
        '"production_original_edge_workers_started":0,'
        '"production_original_deep_workers_started":0,'
        '"performance":"NOT MEASURED","holdout":"NOT ACCESSED"},'
        'sort_keys=True))',
    ]


def _v22_traceback_lines() -> list[str]:
    absolute = str(ROOT / V22_SOURCE_RELATIVE)
    return [
        "Traceback (most recent call last):",
        '  File "<string>", line 11, in <module>',
        "    state=p.preflight(family,pins)",
        '  File "' + absolute + '", line 638, in preflight',
        "    preserved = validate_preserved_incidents(",
        "        v21,",
        "        audits,",
        "    )",
        '  File "' + absolute + '", line 556, in validate_preserved_incidents',
        "    validate_v13_failure_summary(actual_v13)",
        "    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^",
        '  File "' + absolute + '", line 497, in validate_v13_failure_summary',
        "    require(",
        "    ~~~~~~~^",
        "        isinstance(value, dict)",
        "        ^^^^^^^^^^^^^^^^^^^^^^^",
        "    ...<2 lines>...",
        '        "the genuine original failed V13 first invocation was forged",',
        "        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
        "    )",
        "    ^",
        '  File "' + absolute + '", line 156, in require',
        "    raise ProofV22Error(message)",
        "tools.postfinal_current_build_proofs_v22.ProofV22Error: "
        "the genuine original failed V13 first invocation was forged",
    ]


def expected_v22_failure_document(pins: Mapping[str, Any]) -> dict[str, Any]:
    actual = validated_pins(pins)
    require(
        actual["audit_source"] == V21_SOURCE_SHA256
        and actual["audit_protocol"] == V21_PROTOCOL_SHA256,
        "the actual first V22 incident requires the independently frozen V21 owner",
    )
    lines = _v22_inline_source(actual)
    traceback = _v22_traceback_lines()
    require(
        len(lines) == 25 and len(traceback) == 24,
        "the actual V22 first invocation source or combined traceback was shortened",
    )
    return {
        "schema": V22_FAILURE_SCHEMA,
        "status": "FAIL",
        "synthetic": False,
        "production_observations_invented": False,
        "qualifies_current_engine": False,
        "actual_invocation": {
            "executable": str(original.PINNED_EXECUTABLE),
            "python_flags": ["-I", "-B", "-c"],
            "environment": {
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "PYTHONPATH": str(ROOT),
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            },
            "exit_code": 1,
            "output_capture":
                "complete combined traceback; stdout and stderr were not separately captured",
            "actual_inline_python_source_lines": lines,
        },
        "frozen_failed_controller": {
            "source_path": V22_SOURCE_RELATIVE,
            "source_sha256": V22_SOURCE_SHA256,
            "protocol_path": V22_PROTOCOL_RELATIVE,
            "protocol_sha256": V22_PROTOCOL_SHA256,
        },
        "actual_passing_prerequisites": {
            "audit_source_sha256": actual["audit_source"],
            "audit_protocol_sha256": actual["audit_protocol"],
            "base_report_path": V21_BASE_REPORT_RELATIVE,
            "base_report_sha256": actual["base_report"],
            "strict_report_path": V21_STRICT_REPORT_RELATIVE,
            "strict_report_sha256": actual["strict_report"],
            "both_independent_ownership_audits_passed": True,
        },
        "failed_stage":
            "candidate-free authentication of the genuine historical V13 "
            "summary before the first original edge worker",
        "attempted_family": "rust",
        "families_not_reached": ["vm", "zig"],
        "actual_exception_type":
            "tools.postfinal_current_build_proofs_v22.ProofV22Error",
        "actual_exception_message":
            "the genuine original failed V13 first invocation was forged",
        "actual_combined_traceback_lines": traceback,
        "actual_combined_traceback_line_count": 24,
        "actual_historical_summary_mismatch": {
            "historical_version": "v13",
            "field": "failed_stage",
            "expected_field_count": 26,
            "actual_authenticated_field_count": 26,
            "missing_fields": [],
            "extra_fields": [],
            "v22_expected_value": FAILED_V13_FAILURE_STAGE,
            "actual_authenticated_v21_value": TRUE_V13_FAILURE_STAGE,
            "other_fields_match": True,
            "other_historical_summaries_exactly_match": ["v15", "v17", "v19"],
        },
        "actual_failed_invocation_boundary_counters": LOST_FAILED_BOUNDARY,
        "independent_follow_up_differential": {
            "status": "PASS",
            "validation_scope":
                "read-only authentication of the exact published V21 reports "
                "and all four historical summary shapes only",
            "read_only_boundary_effects": {
                "candidate_imports": 0,
                "clock_samples": 0,
                "filesystem_writes": 0,
                "native_workers_started": 0,
                "subprocesses_started": 0,
            },
        },
        "native_owner_workers_started": 0,
        "original_edge_workers_started": 0,
        "original_deep_workers_started": 0,
        "correctness_results_published": False,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def expected_v22_failure_summary(pins: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_path": V22_FAILURE_RELATIVE,
        "sha256": V22_FAILURE_SHA256,
        **expected_v22_failure_document(pins),
    }


def validate_v13_failure_summary(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict and value == expected_v13_failure_summary(),
        "the authentic complete V21 V13 failure or its actual stage was forged",
    )
    return value


def validate_v15_failure_summary(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and value == expected_v15_failure_summary()
        and failed.validate_v15_failure_summary(value) == value,
        "the authentic complete V15 failure was forged",
    )
    return value


def validate_v17_failure_summary(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and value == expected_v17_failure_summary()
        and failed.validate_v17_failure_summary(value) == value,
        "the authentic complete V17 three-owner failure was forged",
    )
    return value


def validate_v19_failure_summary(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and value == expected_v19_failure_summary()
        and failed.validate_v19_failure_summary(value) == value,
        "the authentic complete nonqualifying V19 publication failure was forged",
    )
    return value


def validate_v22_failure_document(
    document: Any,
    pins: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        type(document) is dict
        and document == expected_v22_failure_document(pins),
        "the complete actual V22 failed proof preflight was forged or falsely qualified",
    )
    return {
        "source_path": V22_FAILURE_RELATIVE,
        "sha256": V22_FAILURE_SHA256,
        **copy.deepcopy(document),
    }


def authenticate_v22_failure(pins: Mapping[str, Any]) -> dict[str, Any]:
    raw = original.authenticate_frozen(V22_FAILURE_RELATIVE, V22_FAILURE_SHA256)
    document = original.decode_json(
        raw,
        "complete strict unique-key actual pretty-byte V22 failed preflight",
    )
    return validate_v22_failure_document(document, pins)


def validate_current_graph(
    v21: Any,
    audits: Mapping[str, Any],
    *,
    recheck: bool,
) -> dict[str, Any]:
    require(
        isinstance(audits, Mapping)
        and set(audits) == {
            "base", "strict", "graph", "pins", "history", "owner",
            "preserved_zig_failure", "preserved_v13_failure",
            "preserved_v15_failure", "preserved_v17_failure",
            "preserved_v19_failure",
        },
        "the authentic independently owned V21 audit changed its exact 11 roles",
    )
    graph = audits["graph"]
    require(
        type(graph) is dict
        and set(graph) == {
            "source_count", "source_paths", "source_sha256_by_family",
            "native_binary_count", "native_sha256_by_family",
        }
        and graph.get("source_count") == 12
        and graph.get("native_binary_count") == 5
        and type(graph.get("source_paths")) is list
        and len(graph["source_paths"]) == 12
        and len(set(graph["source_paths"])) == 12
        and type(graph.get("source_sha256_by_family")) is dict
        and type(graph.get("native_sha256_by_family")) is dict
        and set(graph["source_sha256_by_family"]) == set(FAMILIES)
        and set(graph["native_sha256_by_family"]) == set(FAMILIES),
        "the current independently owned 12-source/five-native graph changed",
    )
    source_paths: list[str] = []
    for family in FAMILIES:
        metadata = checked_family(family)
        source = graph["source_sha256_by_family"][family]
        native = graph["native_sha256_by_family"][family]
        require(
            type(source) is dict
            and tuple(source) == metadata["sources"]
            and all(original.valid_sha256(value) for value in source.values())
            and type(native) is dict
            and set(native) == set(metadata["native"].values())
            and all(original.valid_sha256(value) for value in native.values())
            and tuple(v21.OWNED_SOURCE_PATHS[family]) == metadata["sources"]
            and dict(v21.OWNED_NATIVE_PATHS[family]) == metadata["native"],
            "a genuine from-scratch V21 semantic source or native ELF changed: "
            + family,
        )
        source_paths.extend(metadata["sources"])
    require(
        set(graph["source_paths"]) == set(source_paths)
        and sum(len(value) for value in graph["native_sha256_by_family"].values())
        == 5,
        "the exact independently owned current source/native graph was shortened",
    )
    require(type(recheck) is bool, "a graph recheck requires an explicit mode")
    if recheck:
        with v21.read_only_history_boundary() as effects:
            require(
                v21.read_only_current_graph() == graph,
                "a current audited from-scratch source or native binary changed",
            )
            require(
                isinstance(effects, Mapping)
                and all(value == 0 for value in effects.values()),
                "a source/native recheck started a worker or mutated state",
            )
    return graph


def validate_preserved_incidents(
    v21: Any,
    audits: Mapping[str, Any],
    pins: Mapping[str, Any],
) -> dict[str, Any]:
    history = audits["history"]
    actual_v13 = audits["preserved_v13_failure"]
    actual_v15 = audits["preserved_v15_failure"]
    actual_v17 = audits["preserved_v17_failure"]
    actual_v19 = audits["preserved_v19_failure"]
    require(
        v21.validate_preserved_history(history) == history
        and v21.validate_v13_first_failure_summary(actual_v13) == actual_v13
        and v21.validate_v15_first_failure_summary(actual_v15) == actual_v15
        and v21.validate_v17_first_failure_summary(actual_v17) == actual_v17
        and v21.validate_v19_first_failure_summary(actual_v19) == actual_v19
        and history.get("preserved_v13_first_audit_failure") == actual_v13
        and history.get("preserved_v15_first_audit_failure") == actual_v15
        and history.get("preserved_v17_first_audit_failure") == actual_v17
        and history.get("preserved_v19_first_audit_failure") == actual_v19,
        "the actual immutable V21 four-incident owner history was changed",
    )
    validate_v13_failure_summary(actual_v13)
    validate_v15_failure_summary(actual_v15)
    validate_v17_failure_summary(actual_v17)
    validate_v19_failure_summary(actual_v19)
    require(
        history.get("preserved_zig_failure") == audits["preserved_zig_failure"]
        and v21.validate_zig_failure_summary(audits["preserved_zig_failure"])
        == audits["preserved_zig_failure"],
        "the genuine historical 18-original/eight-seeded Zig failure was replaced",
    )
    actual_v22 = authenticate_v22_failure(pins)
    prior = historical_v14._validate_preserved_incidents({
        "history": history,
        "preserved_zig_failure": audits["preserved_zig_failure"],
    })
    return {
        **prior,
        "v13_first_owner_preflight_failure": copy.deepcopy(actual_v13),
        "v13_first_owner_preflight_failure_qualifies_current_engine": False,
        "v15_first_owner_preflight_failure": copy.deepcopy(actual_v15),
        "v15_first_owner_preflight_failure_qualifies_current_engine": False,
        "v17_first_owner_postflight_failure": copy.deepcopy(actual_v17),
        "v17_first_owner_postflight_failure_qualifies_current_engine": False,
        "v19_first_owner_publication_failure": copy.deepcopy(actual_v19),
        "v19_first_owner_publication_failure_qualifies_current_engine": False,
        "v22_first_proof_preflight_failure": copy.deepcopy(actual_v22),
        "v22_first_proof_preflight_failure_qualifies_current_engine": False,
        "historical_v10_graph_qualifies_current_engine": False,
    }


def preflight(family: str, pins: Mapping[str, Any]) -> dict[str, Any]:
    metadata = checked_family(family)
    actual = validated_pins(pins)
    require(
        actual["audit_source"] == V21_SOURCE_SHA256
        and actual["audit_protocol"] == V21_PROTOCOL_SHA256,
        "BLOCKED: use only the final independently frozen actual V21 owner",
    )
    verify_runtime_source_only()
    parent = validate_parent_environment(os.environ)
    controller = authenticate_controller()
    original.authenticate_frozen(V21_PROTOCOL_RELATIVE, actual["audit_protocol"])
    v21 = original.import_frozen(
        "tools.postfinal_independent_engine_audit_v21",
        V21_SOURCE_RELATIVE,
        actual["audit_source"],
    )
    require(
        v21.SCHEMA == V21_SCHEMA
        and v21.SOURCE_RELATIVE == V21_SOURCE_RELATIVE
        and v21.PROTOCOL_RELATIVE == V21_PROTOCOL_RELATIVE
        and v21.PROTOCOL_SHA256 == V21_PROTOCOL_SHA256
        and v21.BASE_REPORT_RELATIVE == V21_BASE_REPORT_RELATIVE
        and v21.STRICT_REPORT_RELATIVE == V21_STRICT_REPORT_RELATIVE
        and v21.BASE_SCHEMA == V21_BASE_SCHEMA
        and v21.STRICT_SCHEMA == V21_STRICT_SCHEMA
        and tuple(v21.CORE_FAMILIES) == FAMILIES,
        "the actual reviewed current V21 from-scratch native owner was replaced",
    )
    audits = v21.authenticate_qualified_audits(
        actual["base_report"],
        actual["strict_report"],
    )
    graph = validate_current_graph(v21, audits, recheck=True)
    require(
        audits["pins"] == actual
        and audits["base"].get("schema") == V21_BASE_SCHEMA
        and audits["base"].get("status") == "PASS"
        and audits["strict"].get("schema") == V21_STRICT_SCHEMA
        and audits["strict"].get("status") == "PASS",
        "both full actual independently published V21 reports must pass",
    )
    preserved = validate_preserved_incidents(v21, audits, actual)
    v8 = original.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        original.V8_PROOF_RELATIVE,
        original.V8_PROOF_SHA256,
    )
    snapshot = {
        "family": family,
        "module": metadata["module"],
        "source_sha256_by_path": dict(graph["source_sha256_by_family"][family]),
        "native_sha256_by_path": dict(graph["native_sha256_by_family"][family]),
    }
    verify_runtime_source_only()
    return {
        "v21": v21,
        "owner": audits["owner"],
        "v8": v8,
        "audits": audits,
        "snapshot": snapshot,
        "history": audits["history"],
        "preserved_incidents": preserved,
        "controller": controller,
        "parent_environment": parent,
    }


def audited_graph_provenance(state: Mapping[str, Any]) -> dict[str, Any]:
    graph = state["audits"]["graph"]
    source = {
        path: digest
        for family in FAMILIES
        for path, digest in graph["source_sha256_by_family"][family].items()
    }
    native = {
        path: digest
        for family in FAMILIES
        for path, digest in graph["native_sha256_by_family"][family].items()
    }
    require(
        len(source) == 12
        and len(native) == 5
        and all(original.valid_sha256(value) for value in (*source.values(), *native.values())),
        "the complete independent audited graph lost a real source or native ELF",
    )
    return {
        "all_family_audit_qualified": True,
        "all_family_source_sha256_by_path": source,
        "all_family_native_elf_sha256_by_path": native,
    }


def observe_owner(
    family: str,
    state: Mapping[str, Any],
    *,
    stage: str,
) -> dict[str, Any]:
    checked_family(family)
    require(
        stage in {
            "before-original-edge", "after-original-edge",
            "before-original-deep", "after-original-deep",
        },
        "an actual native owner requires its genuine before/after worker stage",
    )
    expected = dict(state["snapshot"]["native_sha256_by_path"])
    actual = state["v21"].run_native_worker(family, expected)
    validated = state["v21"].validate_native_owner(actual, family, expected)
    require(
        type(actual) is dict
        and (validated is actual or validated == actual)
        and actual.get("status") == "PASS"
        and actual.get("passed") is True
        and actual.get("family") == family
        and actual.get("native_binary_sha256") == expected
        and actual.get("genuine_matching_executed") is True
        and actual.get("regex_guard_count") == 13
        and actual.get("native_loader_guard_count") == 5
        and actual.get("match_repr_checks") == 2
        and actual.get("standard_pickle_check_count") == 16
        and actual.get("standard_pickle_failure_count") == 0
        and actual.get("external_regex_packages") == 0
        and actual.get("persistent_cross_engine_guard") is True
        and actual.get("benchmark_or_timing_executed") is False
        and actual.get("holdout_or_case_fixture_access") is False,
        "the actual independent native owner failed: " + family + ":" + stage,
    )
    return actual


def preflight_fresh_destinations(family: str, *, deep: bool) -> None:
    checked_family(family)
    require(type(deep) is bool, "fresh original paths need their exact mode")
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    destinations = (
        (deep_target(family, True), deep_target(family, False),
         deep_proof_target(family, True), deep_proof_target(family, False))
        if deep else
        (edge_target(family, True), edge_target(family, False),
         edge_proof_target(family, True), edge_proof_target(family, False))
    ) + (
        invalidated_target(family, deep=deep),
        failure_target(family, deep=deep),
    )
    require(
        len(destinations) == len(set(destinations))
        and all("current-build-v24" in item.name.lower() for item in destinations),
        "a V24 original reused historical evidence or another owner's proof",
    )
    for path in destinations:
        original.fresh_target(path, parent)


def normalize_publication_payload(payload: Any) -> tuple[bytes, dict[str, Any] | None]:
    document: dict[str, Any] | None = None
    if type(payload) is bytes:
        raw = payload
    elif type(payload) is dict:
        require(
            all(type(key) is str for key in payload),
            "a strict canonical V24 document cannot contain a nonstring key",
        )
        try:
            raw = original.canonical(payload)
        except (AssertionError, TypeError, ValueError, OverflowError, UnicodeError) as error:
            raise ProofV24Error("the exact V24 document is not finite canonical JSON") from error
        document = payload
    elif type(payload) is tuple:
        require(
            len(payload) == 2
            and type(payload[0]) is dict
            and type(payload[1]) is bytes
            and all(type(key) is str for key in payload[0]),
            "a normalized publication pair requires one exact object and bytes",
        )
        document, raw = payload
    else:
        raise ProofV24Error(
            "exclusive publication accepts only exact bytes, an object, or their pair"
        )
    require(
        type(raw) is bytes and 0 < len(raw) <= original.MAX_FILE_BYTES,
        "normalized canonical publication bytes must be complete and bounded",
    )
    if document is not None:
        decoded = original.decode_json(raw, "complete strict unique-key V24 canonical payload")
        try:
            canonical = original.canonical(document)
        except (AssertionError, TypeError, ValueError, OverflowError, UnicodeError) as error:
            raise ProofV24Error("the V24 document/bytes pair is not finite canonical JSON") from error
        require(
            decoded == document and canonical == raw and original.canonical(decoded) == raw,
            "an exact V24 JSON object and bytes failed their canonical round-trip",
        )
    return raw, document


def _empty_artifact(purpose: str) -> dict[str, Any]:
    require(purpose in PURPOSES, "a genuine publication invented an artifact role")
    return {
        "purpose": purpose,
        "path": None,
        "expected_bytes": None,
        "expected_sha256": None,
        "directory_opened": False,
        "directory_verified": False,
        "created": False,
        "bytes_written": 0,
        "actual_write_calls": [],
        "write_complete": False,
        "file_fsynced": False,
        "file_closed": False,
        "directory_fsynced": False,
        "directory_closed": False,
        "observed_sha256": None,
        "validated": False,
        "canonical_document_expected": False,
        "canonical_document_validated": False,
    }


def _validate_actual_write_calls(row: Mapping[str, Any], purpose: str) -> None:
    calls = row["actual_write_calls"]
    require(
        type(calls) is list,
        "an actual " + purpose + " write-call ledger must be an ordered private list",
    )
    if row["path"] is None:
        require(not calls,
                "an unattempted " + purpose + " invented an actual write syscall")
        return
    total = row["expected_bytes"]
    require(
        type(total) is int and 0 < total <= original.MAX_FILE_BYTES,
        "an actual " + purpose + " write ledger lost its bounded expected byte count",
    )
    remaining = total
    written = 0
    invalid_final = False
    for index, attempt in enumerate(calls):
        require(
            type(attempt) is dict
            and set(attempt) == {"requested_bytes", "returned_bytes"}
            and row["created"] is True
            and type(attempt["requested_bytes"]) is int
            and remaining > 0
            and attempt["requested_bytes"] == remaining,
            "an actual " + purpose + " write request forged its ordered continuation",
        )
        returned = attempt["returned_bytes"]
        if (
            type(returned) is not int
            or returned <= 0
            or returned > remaining
        ):
            require(
                (returned is None or type(returned) in (int, bool))
                and index + 1 == len(calls)
                and row["validated"] is False
                and row["write_complete"] is False
                and row["file_fsynced"] is False
                and row["directory_fsynced"] is False,
                "an actual " + purpose
                + " pending, zero, negative, oversized, or boolean write was retried",
            )
            invalid_final = True
            break
        written += returned
        remaining -= returned
    require(
        type(row["bytes_written"]) is int
        and row["bytes_written"] == written
        and row["write_complete"] is (remaining == 0)
        and (not calls or row["created"] is True)
        and (not row["validated"] or not invalid_final)
        and (not row["file_fsynced"] or remaining == 0),
        "an actual " + purpose + " ledger changed its valid prefix or completion",
    )


def new_publication_receipt(family: str, *, deep: bool) -> dict[str, Any]:
    checked_family(family)
    require(type(deep) is bool, "an actual receipt requires its genuine mode")
    return {
        "family": family,
        "deep": deep,
        "passed": None,
        "artifacts": {purpose: _empty_artifact(purpose) for purpose in PURPOSES},
    }


def validate_publication_receipt(
    receipt: Any,
    family: str,
    *,
    deep: bool,
    passed: bool | None = None,
    original_raw: bytes | None = None,
) -> dict[str, Any]:
    checked_family(family)
    require(
        type(receipt) is dict
        and set(receipt) == {"family", "deep", "passed", "artifacts"}
        and receipt["family"] == family
        and receipt["deep"] is deep
        and (receipt["passed"] is None or type(receipt["passed"]) is bool)
        and (passed is None or receipt["passed"] is passed)
        and type(receipt["artifacts"]) is dict
        and set(receipt["artifacts"]) == set(PURPOSES)
        and all(
            type(receipt["artifacts"][role]) is dict
            and type(receipt["artifacts"][role].get("actual_write_calls")) is list
            for role in PURPOSES
        ),
        "a complete actual syscall-accurate V24 publication receipt was forged",
    )
    require(
        len({
            id(receipt["artifacts"][role]["actual_write_calls"])
            for role in PURPOSES
        }) == len(PURPOSES),
        "independent actual artifact roles share or alias a write-call ledger",
    )
    for purpose in PURPOSES:
        row = receipt["artifacts"][purpose]
        require(
            type(row) is dict
            and set(row) == set(RECEIPT_FIELDS)
            and row.get("purpose") == purpose
            and all(
                type(row[key]) is bool
                for key in (
                    "directory_opened", "directory_verified", "created",
                    "write_complete", "file_fsynced", "file_closed",
                    "directory_fsynced", "directory_closed", "validated",
                    "canonical_document_expected", "canonical_document_validated",
                )
            )
            and type(row["bytes_written"]) is int
            and row["bytes_written"] >= 0,
            "an actual " + purpose + " syscall or canonical transition was forged",
        )
        if row["path"] is None:
            require(row == _empty_artifact(purpose),
                    "an unattempted artifact invented actual syscalls")
            _validate_actual_write_calls(row, purpose)
            continue
        target = expected_publication_target(
            family,
            deep=deep,
            passed=receipt["passed"],
            purpose=purpose,
        )
        require(
            row["path"] == target.relative_to(ROOT).as_posix()
            and type(row["expected_bytes"]) is int
            and 0 < row["expected_bytes"] <= original.MAX_FILE_BYTES
            and original.valid_sha256(row["expected_sha256"])
            and row["bytes_written"] <= row["expected_bytes"]
            and (row["observed_sha256"] is None
                 or original.valid_sha256(row["observed_sha256"]))
            and (not row["directory_verified"] or row["directory_opened"])
            and (not row["created"] or row["directory_verified"])
            and (row["bytes_written"] == 0 or row["created"])
            and (row["write_complete"]
                 == (row["bytes_written"] == row["expected_bytes"]))
            and (not row["file_fsynced"] or row["write_complete"])
            and (not row["file_closed"] or row["created"])
            and (not row["directory_fsynced"]
                 or (row["file_fsynced"] and row["file_closed"]))
            and (not row["directory_closed"] or row["directory_opened"])
            and (row["observed_sha256"] is None
                 or (row["directory_fsynced"] and row["directory_closed"]))
            and (not row["canonical_document_validated"]
                 or (row["canonical_document_expected"]
                     and row["observed_sha256"] == row["expected_sha256"]))
            and (row["validated"] == (
                row["observed_sha256"] == row["expected_sha256"]
                and row["directory_fsynced"]
                and row["directory_closed"]
                and (not row["canonical_document_expected"]
                     or row["canonical_document_validated"])
            )),
            "an actual " + purpose
            + " O_EXCL, write, fsync, close, or canonical reread was misrepresented",
        )
        _validate_actual_write_calls(row, purpose)
        if purpose == "proof":
            require(
                receipt["artifacts"]["archive"]["validated"],
                "a canonical owner proof preceded its complete durable original",
            )
        if purpose == "archive" and original_raw is not None:
            require(
                type(original_raw) is bytes
                and len(original_raw) == row["expected_bytes"]
                and hashlib.sha256(original_raw).hexdigest() == row["expected_sha256"],
                "a complete original receipt altered genuine worker bytes",
            )
    return receipt


class PublicationOps:
    """Own real descriptor-relative, no-follow, exclusive V24 publication."""

    synthetic = False

    def check_target(self, path: Path, parent: Path) -> None:
        original.fresh_target(path, parent)

    def open_directory(self, parent: Path) -> int:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        return os.open(parent, flags)

    def verify_directory(self, descriptor: int, parent: Path) -> None:
        observed = os.fstat(descriptor)
        expected = os.stat(parent, follow_symlinks=False)
        require(
            stat.S_ISDIR(observed.st_mode)
            and stat.S_ISDIR(expected.st_mode)
            and (observed.st_dev, observed.st_ino)
            == (expected.st_dev, expected.st_ino),
            "exclusive V24 publication lost its real nonsymlink directory identity",
        )

    def create(self, directory: int, name: str) -> int:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        return os.open(name, flags, 0o644, dir_fd=directory)

    def write(self, descriptor: int, payload: memoryview) -> int:
        return os.write(descriptor, payload)

    def fsync(self, descriptor: int, *, directory: bool) -> None:
        del directory
        os.fsync(descriptor)

    def close(self, descriptor: int, *, directory: bool) -> None:
        del directory
        os.close(descriptor)

    def read_regular(self, path: Path, label: str) -> bytes:
        return original.read_regular(path, label)


def publish_exclusive(
    receipt: dict[str, Any],
    family: str,
    *,
    deep: bool,
    passed: bool | None,
    purpose: str,
    path: Path,
    payload: Any,
    operations: PublicationOps | Any | None = None,
) -> str:
    checked_family(family)
    require(
        type(deep) is bool and purpose in PURPOSES and isinstance(path, Path),
        "an actual exclusive artifact requires its exact mode, role, and target",
    )
    raw, document = normalize_publication_payload(payload)
    validate_publication_receipt(receipt, family, deep=deep)
    if purpose in ("archive", "proof"):
        require(type(passed) is bool, "an actual original cannot invent its result")
        if receipt["passed"] is None:
            receipt["passed"] = passed
        require(receipt["passed"] is passed,
                "an actual owner proof changed its original worker outcome")
    target = expected_publication_target(
        family,
        deep=deep,
        passed=receipt["passed"],
        purpose=purpose,
    )
    require(path == target, "exclusive V24 publication escaped its fresh bound path")
    row = receipt["artifacts"][purpose]
    require(row == _empty_artifact(purpose),
            "an actual exclusive artifact was retried or overwritten")
    if purpose == "proof":
        require(receipt["artifacts"]["archive"]["validated"],
                "a current owner proof preceded its validated original")
    row.update({
        "path": path.relative_to(ROOT).as_posix(),
        "expected_bytes": len(raw),
        "expected_sha256": hashlib.sha256(raw).hexdigest(),
        "canonical_document_expected": document is not None,
    })
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    ops = PublicationOps() if operations is None else operations
    directory: int | None = None
    descriptor: int | None = None
    stage = "target-validation"
    failure: tuple[str, BaseException] | None = None
    try:
        ops.check_target(path, parent)
        stage = "directory-open"
        directory = ops.open_directory(parent)
        row["directory_opened"] = True
        stage = "directory-identity"
        ops.verify_directory(directory, parent)
        row["directory_verified"] = True
        stage = "exclusive-create"
        descriptor = ops.create(directory, path.name)
        row["created"] = True
        stage = "write"
        view = memoryview(raw)
        while row["bytes_written"] < len(raw):
            requested = len(raw) - row["bytes_written"]
            attempt = {
                "requested_bytes": requested,
                "returned_bytes": None,
            }
            row["actual_write_calls"].append(attempt)
            count = ops.write(descriptor, view[row["bytes_written"]:])
            attempt["returned_bytes"] = count
            require(
                type(count) is int
                and 0 < count <= requested,
                "an actual normalized V24 write returned zero, negative, "
                "oversized, or boolean bytes",
            )
            row["bytes_written"] += count
            if row["bytes_written"] == len(raw):
                row["write_complete"] = True
        stage = "file-fsync"
        ops.fsync(descriptor, directory=False)
        row["file_fsynced"] = True
        stage = "file-close"
        closing = descriptor
        descriptor = None
        ops.close(closing, directory=False)
        row["file_closed"] = True
        stage = "directory-fsync"
        ops.fsync(directory, directory=True)
        row["directory_fsynced"] = True
        stage = "directory-close"
        closing = directory
        directory = None
        ops.close(closing, directory=True)
        row["directory_closed"] = True
        stage = "readback"
        saved = ops.read_regular(path, "complete normalized exclusive V24 " + purpose)
        require(type(saved) is bytes, "an exclusive artifact lost its genuine bytes")
        row["observed_sha256"] = hashlib.sha256(saved).hexdigest()
        require(
            saved == raw and row["observed_sha256"] == row["expected_sha256"],
            "an actual exclusive V24 reread changed the complete original bytes",
        )
        if document is not None:
            stage = "canonical-readback"
            decoded = original.decode_json(saved, "complete strict canonical V24 owner proof")
            require(
                decoded == document and original.canonical(decoded) == saved,
                "an actual normalized V24 JSON proof failed canonical round-trip",
            )
            row["canonical_document_validated"] = True
        row["validated"] = True
    except (AssertionError, OSError, ValueError, TypeError, KeyError, UnicodeError) as error:
        failure = (stage, error)
    finally:
        for name, kind in (("descriptor", "file"), ("directory", "directory")):
            active = descriptor if name == "descriptor" else directory
            if active is None:
                continue
            if name == "descriptor":
                descriptor = None
            else:
                directory = None
            try:
                ops.close(active, directory=kind == "directory")
                row[kind + "_closed"] = True
            except (AssertionError, OSError, ValueError, TypeError, KeyError) as error:
                if failure is None:
                    failure = (kind + "-cleanup-close", error)
    if failure is not None:
        stage, cause = failure
        raise V24PublicationFailure(
            "actual normalized exclusive V24 " + purpose
            + " publication failed at " + stage,
            stage=stage,
            receipt=receipt,
            cause=cause,
        ) from cause
    validate_publication_receipt(
        receipt,
        family,
        deep=deep,
        passed=receipt["passed"],
        original_raw=raw if purpose == "archive" else None,
    )
    return row["expected_sha256"]


def failure_publication_fields(
    publication: Mapping[str, Any],
    family: str,
    *,
    deep: bool,
    original_raw: bytes | None,
) -> dict[str, Any]:
    receipt = validate_publication_receipt(
        publication,
        family,
        deep=deep,
        original_raw=original_raw,
    )
    archive = receipt["artifacts"]["archive"]
    proof = receipt["artifacts"]["proof"]
    return {
        "v24_original_archive_path": archive["path"],
        "v24_original_archive_expected_sha256": archive["expected_sha256"],
        "v24_original_archive_observed_sha256": archive["observed_sha256"],
        "v24_original_archive_created": archive["created"],
        "v24_original_archive_bytes_written": archive["bytes_written"],
        "v24_original_archive_actual_write_calls":
            copy.deepcopy(archive["actual_write_calls"]),
        "v24_original_archive_file_fsynced": archive["file_fsynced"],
        "v24_original_archive_directory_fsynced": archive["directory_fsynced"],
        "v24_original_archive_validated": archive["validated"],
        "v24_owner_proof_path": proof["path"],
        "v24_owner_proof_expected_sha256": proof["expected_sha256"],
        "v24_owner_proof_observed_sha256": proof["observed_sha256"],
        "v24_owner_proof_created": proof["created"],
        "v24_owner_proof_bytes_written": proof["bytes_written"],
        "v24_owner_proof_actual_write_calls":
            copy.deepcopy(proof["actual_write_calls"]),
        "v24_owner_proof_file_fsynced": proof["file_fsynced"],
        "v24_owner_proof_directory_fsynced": proof["directory_fsynced"],
        "v24_owner_proof_canonical_document_expected":
            proof["canonical_document_expected"],
        "v24_owner_proof_canonical_document_validated":
            proof["canonical_document_validated"],
        "v24_owner_proof_validated": proof["validated"],
        "v24_complete_syscall_publication_receipt": copy.deepcopy(receipt),
        "unpaired_v24_original_archive_qualifies": False,
    }


def build_durable_wrapper(
    family: str,
    state: Mapping[str, Any],
    *,
    deep: bool,
    passed: bool,
    original_report: Mapping[str, Any],
    archive_path: Path,
    archive_sha256: str,
    archive_bytes: int,
    owner_before: Mapping[str, Any],
    owner_after: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes],
    archive_receipt: Mapping[str, Any],
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = checked_family(family)
    require(
        type(deep) is bool
        and type(passed) is bool
        and isinstance(original_report, Mapping)
        and isinstance(producer, subprocess.CompletedProcess)
        and type(producer.returncode) is int
        and type(producer.stdout) is bytes
        and type(producer.stderr) is bytes
        and len(producer.stdout) <= original.MAX_CHILD_OUTPUT_BYTES
        and len(producer.stderr) <= original.MAX_CHILD_OUTPUT_BYTES
        and isinstance(archive_path, Path)
        and original.valid_sha256(archive_sha256)
        and type(archive_bytes) is int
        and 0 < archive_bytes <= original.MAX_FILE_BYTES
        and isinstance(archive_receipt, Mapping),
        "a durable V24 proof requires complete actual original worker observations",
    )
    target = deep_target(family, passed) if deep else edge_target(family, passed)
    proof = deep_proof_target(family, passed) if deep else edge_proof_target(
        family,
        passed,
    )
    require(
        archive_path == target
        and set(archive_receipt) == set(RECEIPT_FIELDS)
        and archive_receipt.get("purpose") == "archive"
        and archive_receipt.get("path") == target.relative_to(ROOT).as_posix()
        and archive_receipt.get("expected_bytes") == archive_bytes
        and archive_receipt.get("expected_sha256") == archive_sha256
        and archive_receipt.get("observed_sha256") == archive_sha256
        and archive_receipt.get("validated") is True
        and archive_receipt.get("file_fsynced") is True
        and archive_receipt.get("directory_fsynced") is True,
        "a current native-owner proof cannot qualify an unfinished actual archive",
    )
    _validate_actual_write_calls(archive_receipt, "archive")
    pins = validated_pins(state["audits"]["pins"])
    controller = state["controller"]
    mode = "qualified-deep" if deep else "qualified-edge"
    result: dict[str, Any] = {
        "schema": SCHEMA + "-" + mode + "-durable-proof",
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL",
        "mode": mode,
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "campaign_qualified": passed,
        "proof_path": proof.relative_to(ROOT).as_posix(),
        "original_archive_path": archive_path.relative_to(ROOT).as_posix(),
        "original_archive_sha256": archive_sha256,
        "original_archive_bytes": archive_bytes,
        "original_archive_publication_receipt": copy.deepcopy(dict(archive_receipt)),
        "publication_strategy":
            "v24-owned-normalized-canonical-directory-bound-syscall-receipts",
        "complete_original_producer_bytes_preserved": True,
        "original_archive_is_unmodified_original": True,
        "stdout_is_not_durable_proof": True,
        "original_worker_returncode": producer.returncode,
        "original_worker_stdout": original.observed_stream(producer.stdout, True),
        "original_worker_stderr": original.observed_stream(producer.stderr, True),
        "current_v21_native_owner_before": dict(owner_before),
        "current_v21_native_owner_after": dict(owner_after),
        "full_current_family_source_sha256":
            dict(state["snapshot"]["source_sha256_by_path"]),
        "full_current_family_native_elf_sha256":
            dict(state["snapshot"]["native_sha256_by_path"]),
        "all_family_audited_provenance": audited_graph_provenance(state),
        "actual_v21_audit_source_path": V21_SOURCE_RELATIVE,
        "actual_v21_audit_source_sha256": pins["audit_source"],
        "actual_v21_protocol_path": V21_PROTOCOL_RELATIVE,
        "actual_v21_protocol_sha256": pins["audit_protocol"],
        "actual_v21_base_report_path": V21_BASE_REPORT_RELATIVE,
        "actual_v21_base_report_sha256": pins["base_report"],
        "actual_v21_strict_report_path": V21_STRICT_REPORT_RELATIVE,
        "actual_v21_strict_report_sha256": pins["strict_report"],
        "actual_invoking_controller": "V24",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_refresh_protocol_path": controller["protocol_path"],
        "actual_refresh_protocol_sha256": controller["protocol_sha256"],
        "actual_verified_parent_environment":
            dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment": worker_environment(),
        "preserved_immutable_history": copy.deepcopy(state["history"]),
        "preserved_actual_failed_incidents":
            copy.deepcopy(state["preserved_incidents"]),
        "exclusive_creation": True,
        "canonical_document_bytes_normalized": True,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if deep:
        result.update({
            "seed": original.DEEP_SEED,
            "checks": original.DEEP_CHECKS,
            "seeded_case_count": original.DEEP_SEEDED_CASES,
            "reference_sha256": original.DEEP_REFERENCE_SHA256,
            "actual_sha256": original_report.get("candidate_sha256"),
            "public_mismatch_count": original_report.get("public_mismatch_count"),
            "public_mismatch_family_counts":
                original_report.get("public_mismatch_family_counts"),
            "qualified_edge":
                dict(qualified_edge) if isinstance(qualified_edge, Mapping) else None,
        })
    else:
        result.update({
            "seed": original.EDGE_SEED,
            "checks": original.EDGE_CHECKS,
            "category_count": original.EDGE_CATEGORIES,
            "reference_sha256": original.EDGE_REFERENCE_SHA256,
            "actual_sha256": original_report.get("actual_sha256"),
            "failure_count": original_report.get("failed"),
            "complete_failure_row_count": len(original_report.get("failures", [])),
        })
    return result


def validate_durable_wrapper(
    document: Any,
    family: str,
    state: Mapping[str, Any],
    *,
    deep: bool,
    passed: bool,
    original_report: Mapping[str, Any],
    archive_path: Path,
    archive_sha256: str,
    archive_bytes: int,
    owner_before: Mapping[str, Any],
    owner_after: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes],
    archive_receipt: Mapping[str, Any],
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    expected = build_durable_wrapper(
        family,
        state,
        deep=deep,
        passed=passed,
        original_report=original_report,
        archive_path=archive_path,
        archive_sha256=archive_sha256,
        archive_bytes=archive_bytes,
        owner_before=owner_before,
        owner_after=owner_after,
        producer=producer,
        archive_receipt=archive_receipt,
        qualified_edge=qualified_edge,
    )
    metadata = checked_family(family)
    require(
        type(document) is dict
        and document == expected
        and producer.returncode == int(not passed)
        and document["campaign_qualified"] is passed
        and document["candidate_module"] == metadata["module"]
        and document["stdout_is_not_durable_proof"] is True
        and document["production_observations_invented"] is False,
        "a canonical V24 owner proof changed genuine worker observations",
    )
    snapshot = state["snapshot"]
    require(
        snapshot.get("family") == family
        and snapshot.get("module") == metadata["module"]
        and set(snapshot.get("source_sha256_by_path", {})) == set(metadata["sources"])
        and set(snapshot.get("native_sha256_by_path", {}))
        == set(metadata["native"].values()),
        "a current owner proof omitted a complete independent semantic or native source",
    )
    for phase, observation in (("before", owner_before), ("after", owner_after)):
        validated = state["v21"].validate_native_owner(
            observation,
            family,
            dict(snapshot["native_sha256_by_path"]),
        )
        require(
            isinstance(observation, Mapping)
            and (validated is observation or validated == observation)
            and observation.get("status") == "PASS"
            and observation.get("family") == family,
            "an actually completed " + phase + " native owner was forged or omitted",
        )
    if deep:
        require(
            isinstance(qualified_edge, Mapping)
            and qualified_edge.get("status") == "PASS"
            and qualified_edge.get("campaign_qualified") is True
            and qualified_edge.get("archive_path")
            == edge_target(family, True).relative_to(ROOT).as_posix()
            and qualified_edge.get("proof_path")
            == edge_proof_target(family, True).relative_to(ROOT).as_posix()
            and original.valid_sha256(qualified_edge.get("archive_sha256"))
            and original.valid_sha256(qualified_edge.get("proof_sha256")),
            "a genuine deep worker requires its same-family actual passing V24 edge",
        )
    return document


def _recorded_producer(wrapper: Mapping[str, Any]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(
        args=["durably-recorded-original-v24-worker"],
        returncode=wrapper.get("original_worker_returncode"),
        stdout=original.restore_complete_stream(
            wrapper.get("original_worker_stdout"),
            "complete actual original V24 worker stdout",
        ),
        stderr=original.restore_complete_stream(
            wrapper.get("original_worker_stderr"),
            "complete actual original V24 worker stderr",
        ),
    )


def authenticate_qualified_edge(
    family: str,
    state: Mapping[str, Any],
    contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    checked_family(family)
    archive = edge_target(family, True)
    proof_path = edge_proof_target(family, True)
    raw = original.read_regular(archive, "complete unchanged original passing V24 edge")
    document, edge, passed = state["v8"].validate_original_edge(
        raw,
        archive,
        family,
        state["snapshot"],
        contract,
    )
    require(
        passed is True
        and edge.get("failed") == 0
        and edge.get("checks") == original.EDGE_CHECKS
        and edge.get("category_count") == original.EDGE_CATEGORIES,
        "the genuine complete original V24 edge failed its exact 223198/49 gate",
    )
    proof_raw = original.read_regular(
        proof_path,
        "complete canonical same-family V24 edge owner proof",
    )
    proof = original.decode_json(proof_raw, "complete strict canonical V24 edge proof")
    require(
        normalize_publication_payload((proof, proof_raw)) == (proof_raw, proof),
        "the complete same-family V24 edge owner proof changed canonical bytes",
    )
    process = _recorded_producer(proof)
    validate_durable_wrapper(
        proof,
        family,
        state,
        deep=False,
        passed=True,
        original_report=document,
        archive_path=archive,
        archive_sha256=hashlib.sha256(raw).hexdigest(),
        archive_bytes=len(raw),
        owner_before=proof.get("current_v21_native_owner_before"),
        owner_after=proof.get("current_v21_native_owner_after"),
        producer=process,
        archive_receipt=proof.get("original_archive_publication_receipt"),
    )
    return edge, {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": archive.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
    }, raw, proof_raw


def authenticate_qualified_deep(
    family: str,
    state: Mapping[str, Any],
    contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    edge, qualified_edge, _, _ = authenticate_qualified_edge(family, state, contract)
    archive = deep_target(family, True)
    proof_path = deep_proof_target(family, True)
    raw = original.read_regular(archive, "complete unchanged original passing V24 deep")
    document, passed = state["v8"].validate_deep(
        raw,
        family,
        edge,
        state["snapshot"],
        contract,
    )
    require(
        passed is True
        and document.get("status") == "PASS"
        and document.get("checks") == original.DEEP_CHECKS
        and document.get("seeded_case_count") == original.DEEP_SEEDED_CASES
        and document.get("public_mismatch_count") == 0
        and document.get("candidate_sha256") == original.DEEP_REFERENCE_SHA256,
        "the genuine original V24 deep failed its exact 393/64 contract",
    )
    proof_raw = original.read_regular(proof_path, "complete canonical passing V24 deep proof")
    proof = original.decode_json(proof_raw, "complete strict canonical V24 deep proof")
    require(
        normalize_publication_payload((proof, proof_raw)) == (proof_raw, proof),
        "the complete V24 deep proof changed its exact canonical bytes",
    )
    process = _recorded_producer(proof)
    validate_durable_wrapper(
        proof,
        family,
        state,
        deep=True,
        passed=True,
        original_report=document,
        archive_path=archive,
        archive_sha256=hashlib.sha256(raw).hexdigest(),
        archive_bytes=len(raw),
        owner_before=proof.get("current_v21_native_owner_before"),
        owner_after=proof.get("current_v21_native_owner_after"),
        producer=process,
        archive_receipt=proof.get("original_archive_publication_receipt"),
        qualified_edge=qualified_edge,
    )
    return document, {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": archive.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
        "qualified_edge": qualified_edge,
    }, raw, proof_raw


def _run_original(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    require(
        type(command) is list
        and all(type(value) is str for value in command)
        and len(command) >= 5
        and command[0] == str(original.PINNED_EXECUTABLE)
        and command[1:3] == ["-I", "-B"],
        "only a complete pinned isolated original CPython worker may execute",
    )
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        env=worker_environment(),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=1800,
    )
    require(
        isinstance(result, subprocess.CompletedProcess)
        and result.args == command
        and type(result.returncode) is int
        and type(result.stdout) is bytes
        and type(result.stderr) is bytes
        and len(result.stdout) <= original.MAX_CHILD_OUTPUT_BYTES
        and len(result.stderr) <= original.MAX_CHILD_OUTPUT_BYTES,
        "the complete original V24 worker lost its actual exit or full streams",
    )
    return result


def captured_native_owner_records(
    family: str,
    owner_before: Mapping[str, Any] | None,
    owner_after: Mapping[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    checked_family(family)
    result: dict[str, dict[str, Any]] = {}
    for phase, observed in (
        ("before-original-worker", owner_before),
        ("after-original-worker", owner_after),
    ):
        if observed is None:
            continue
        require(
            isinstance(observed, Mapping)
            and observed.get("status") == "PASS"
            and observed.get("family") == family
            and observed.get("genuine_matching_executed") is True,
            "refusing to invent a completed genuine V24 native owner: " + phase,
        )
        result[phase] = copy.deepcopy(dict(observed))
    return result


def _preserve_failure(
    family: str,
    state: Mapping[str, Any],
    *,
    deep: bool,
    error: BaseException,
    owner_before: Mapping[str, Any] | None,
    owner_after: Mapping[str, Any] | None,
    producer: subprocess.CompletedProcess[bytes] | None,
    completed_original: bytes | None,
    validated_original: bool | None,
    command: list[str] | None,
    publication: dict[str, Any],
) -> ProofV24Failure:
    metadata = checked_family(family)
    timed_out = isinstance(error, subprocess.TimeoutExpired)
    stdout = producer.stdout if producer is not None else getattr(error, "stdout", None)
    stderr = producer.stderr if producer is not None else getattr(error, "stderr", None)
    exit_code = producer.returncode if producer is not None else None
    invalidated_path: str | None = None
    invalidated_digest: str | None = None
    if completed_original is not None:
        require(
            type(completed_original) is bytes
            and 0 < len(completed_original) <= original.MAX_FILE_BYTES,
            "refusing to invent a complete actual original V24 observation",
        )
        target = invalidated_target(family, deep=deep)
        invalidated_digest = publish_exclusive(
            publication,
            family,
            deep=deep,
            passed=publication["passed"],
            purpose="invalidated",
            path=target,
            payload=completed_original,
        )
        invalidated_path = target.relative_to(ROOT).as_posix()
    fields = failure_publication_fields(
        publication,
        family,
        deep=deep,
        original_raw=completed_original,
    )
    pins = validated_pins(state["audits"]["pins"])
    controller = state["controller"]
    owners = captured_native_owner_records(family, owner_before, owner_after)
    document = {
        "schema": SCHEMA + "-original-producer-failure",
        "status": "FAIL",
        "result": "FAIL",
        "mode": "qualified-deep" if deep else "qualified-edge",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "actual_invoking_controller": "V24",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_refresh_protocol_path": controller["protocol_path"],
        "actual_refresh_protocol_sha256": controller["protocol_sha256"],
        "actual_failure_error_type": type(error).__name__,
        "actual_failure_error_message": str(error),
        "actual_publication_failure_stage":
            error.stage if isinstance(error, V24PublicationFailure) else None,
        "actual_child_exit_code": exit_code,
        "actual_child_signal":
            -exit_code if type(exit_code) is int and exit_code < 0 else None,
        "timed_out": timed_out,
        "timeout_seconds": 1800 if timed_out else None,
        "actual_original_worker_command": list(command) if command is not None else None,
        "actual_verified_parent_environment": dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment": worker_environment(),
        "stdout": original.observed_stream(stdout, not timed_out),
        "stderr": original.observed_stream(stderr, not timed_out),
        "current_v21_native_owner_before":
            dict(owner_before) if owner_before is not None else None,
        "current_v21_native_owner_after":
            dict(owner_after) if owner_after is not None else None,
        "actually_completed_native_owner_records": copy.deepcopy(owners),
        "actually_completed_native_owner_record_count": len(owners),
        "full_current_family_source_sha256":
            dict(state["snapshot"]["source_sha256_by_path"]),
        "full_current_family_native_elf_sha256":
            dict(state["snapshot"]["native_sha256_by_path"]),
        "all_family_audited_provenance": audited_graph_provenance(state),
        "actual_v21_audit_source_sha256": pins["audit_source"],
        "actual_v21_protocol_sha256": pins["audit_protocol"],
        "actual_v21_base_report_sha256": pins["base_report"],
        "actual_v21_strict_report_sha256": pins["strict_report"],
        "preserved_immutable_history": copy.deepcopy(state["history"]),
        "preserved_actual_failed_incidents": copy.deepcopy(state["preserved_incidents"]),
        "complete_original_observation_archive": completed_original is not None,
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_digest,
        "invalidated_complete_original_actual_status":
            None if completed_original is None else
            "NOT VALIDATED" if validated_original is None else
            "PASS" if validated_original else "FAIL",
        **fields,
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    canonical, exact = normalize_publication_payload(document)
    require(exact == document, "an actual V24 failure changed canonical observations")
    compressed = gzip.compress(canonical, compresslevel=9, mtime=0)
    decoded, restored = state["v8"].decode_archive(
        compressed,
        "complete actual canonical V24 native owner or original worker failure",
    )
    require(decoded == document and restored == canonical,
            "an actual canonical V24 failure lost genuine observations")
    target = failure_target(family, deep=deep)
    digest = publish_exclusive(
        publication,
        family,
        deep=deep,
        passed=publication["passed"],
        purpose="failure",
        path=target,
        payload=compressed,
    )
    return ProofV24Failure(
        "a genuine original V24 worker or independently owned native matcher failed",
        {
            "status": "FAIL",
            "candidate_family": metadata["contract_name"],
            "candidate_module": metadata["module"],
            "failure_evidence_path": target.relative_to(ROOT).as_posix(),
            "failure_evidence_sha256": digest,
            "invalidated_complete_original_evidence_path": invalidated_path,
            "invalidated_complete_original_evidence_sha256": invalidated_digest,
            "actual_child_exit_code": exit_code,
            "actually_completed_native_owner_records": copy.deepcopy(owners),
            "actually_completed_native_owner_record_count": len(owners),
            **failure_publication_fields(
                publication,
                family,
                deep=deep,
                original_raw=completed_original,
            ),
            "campaign_qualified": False,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        },
    )


def _publish_original_pair(
    family: str,
    state: Mapping[str, Any],
    *,
    deep: bool,
    passed: bool,
    report: Mapping[str, Any],
    raw: bytes,
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes],
    contract: Any,
    publication: dict[str, Any],
    qualified_edge: Mapping[str, Any] | None = None,
    edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    archive = deep_target(family, passed) if deep else edge_target(family, passed)
    proof = deep_proof_target(family, passed) if deep else edge_proof_target(
        family,
        passed,
    )
    archive_digest = publish_exclusive(
        publication,
        family,
        deep=deep,
        passed=passed,
        purpose="archive",
        path=archive,
        payload=raw,
    )
    complete = original.read_regular(archive, "complete genuine exclusive original V24 observations")
    require(
        complete == raw and hashlib.sha256(complete).hexdigest() == archive_digest,
        "an actual V24 original archive changed complete worker observations",
    )
    if deep:
        require(isinstance(edge, Mapping), "a genuine deep original requires its passing edge")
        verified, outcome = state["v8"].validate_deep(
            complete,
            family,
            dict(edge),
            state["snapshot"],
            contract,
        )
    else:
        verified, _, outcome = state["v8"].validate_original_edge(
            complete,
            archive,
            family,
            state["snapshot"],
            contract,
        )
    require(verified == report and outcome is passed,
            "a complete original V24 archive misrepresented its real outcome")
    archived = publication["artifacts"]["archive"]
    wrapper = build_durable_wrapper(
        family,
        state,
        deep=deep,
        passed=passed,
        original_report=verified,
        archive_path=archive,
        archive_sha256=archive_digest,
        archive_bytes=len(raw),
        owner_before=before,
        owner_after=after,
        producer=producer,
        archive_receipt=archived,
        qualified_edge=qualified_edge,
    )
    validate_durable_wrapper(
        wrapper,
        family,
        state,
        deep=deep,
        passed=passed,
        original_report=verified,
        archive_path=archive,
        archive_sha256=archive_digest,
        archive_bytes=len(raw),
        owner_before=before,
        owner_after=after,
        producer=producer,
        archive_receipt=archived,
        qualified_edge=qualified_edge,
    )
    proof_raw, document = normalize_publication_payload(wrapper)
    require(document == wrapper, "the V24 native-owner proof lost canonical observations")
    proof_digest = publish_exclusive(
        publication,
        family,
        deep=deep,
        passed=passed,
        purpose="proof",
        path=proof,
        payload=(wrapper, proof_raw),
    )
    saved = original.read_regular(proof, "complete canonical current-family V24 owner proof")
    decoded = original.decode_json(saved, "complete strict normalized V24 proof readback")
    require(
        normalize_publication_payload((decoded, saved)) == (proof_raw, wrapper)
        and hashlib.sha256(saved).hexdigest() == proof_digest
        and publication["artifacts"]["proof"]["canonical_document_expected"]
        and publication["artifacts"]["proof"]["canonical_document_validated"],
        "the complete normalized V24 owner proof failed actual canonical round-trip",
    )
    validate_durable_wrapper(
        decoded,
        family,
        state,
        deep=deep,
        passed=passed,
        original_report=verified,
        archive_path=archive,
        archive_sha256=archive_digest,
        archive_bytes=len(raw),
        owner_before=before,
        owner_after=after,
        producer=producer,
        archive_receipt=archived,
        qualified_edge=qualified_edge,
    )
    require(
        original.read_regular(archive, "complete final original V24 archive") == complete,
        "a normalized proof cannot certify subsequently changed original bytes",
    )
    validate_publication_receipt(
        publication,
        family,
        deep=deep,
        passed=passed,
        original_raw=raw,
    )
    return {
        "schema": SCHEMA + (
            "-qualified-deep-durable-summary" if deep else "-qualified-edge-durable-summary"
        ),
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL",
        "mode": "qualified-deep" if deep else "qualified-edge",
        "candidate_family": checked_family(family)["contract_name"],
        "candidate_module": checked_family(family)["module"],
        "campaign_qualified": passed,
        "checks": original.DEEP_CHECKS if deep else original.EDGE_CHECKS,
        "seeded_case_count": original.DEEP_SEEDED_CASES if deep else None,
        "category_count": None if deep else original.EDGE_CATEGORIES,
        "public_mismatch_count":
            verified.get("public_mismatch_count") if deep else verified.get("failed"),
        "original_archive_path": archive.relative_to(ROOT).as_posix(),
        "original_archive_sha256": archive_digest,
        "complete_owner_proof_path": proof.relative_to(ROOT).as_posix(),
        "complete_owner_proof_sha256": proof_digest,
        "complete_syscall_publication_receipt": copy.deepcopy(publication),
        "actual_v21_audit_source_sha256": state["audits"]["pins"]["audit_source"],
        "actual_v21_protocol_sha256": state["audits"]["pins"]["audit_protocol"],
        "actual_v21_base_report_sha256": state["audits"]["pins"]["base_report"],
        "actual_v21_strict_report_sha256": state["audits"]["pins"]["strict_report"],
        "canonical_document_bytes_normalized": True,
        "stdout_is_not_durable_proof": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def refresh_edge(family: str, pins: Mapping[str, Any]) -> dict[str, Any]:
    state = preflight(family, pins)
    preflight_fresh_destinations(family, deep=False)
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    process: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    receipt = new_publication_receipt(family, deep=False)
    try:
        before = observe_owner(family, state, stage="before-original-edge")
        validate_current_graph(state["v21"], state["audits"], recheck=True)
        with tempfile.TemporaryDirectory(
            prefix="rebar-v24-original-edge-" + family + "-",
            dir="/tmp",
        ) as directory:
            private = Path(directory).resolve()
            require(private.parent == Path("/tmp").resolve(),
                    "the original V24 edge escaped its exact isolated temporary root")
            temporary = private / "original-full-edge.json.gz"
            command = [
                str(original.PINNED_EXECUTABLE), "-I", "-B",
                str(ROOT / original.EDGE_SOURCE_RELATIVE),
                "--module", metadata["module"],
                "--seed", str(original.EDGE_SEED),
                "--seeded-cases", str(original.EDGE_SEEDED_CASES),
                "--unicode-stride", str(original.EDGE_UNICODE_STRIDE),
                "--output", str(temporary),
            ]
            process = _run_original(command)
            require(temporary.is_file() and not temporary.is_symlink(),
                    "the original V24 edge worker produced no real complete archive")
            raw = original.read_regular(temporary, "complete private original V24 edge")
            report, _, passed = state["v8"].validate_original_edge(
                raw,
                temporary,
                family,
                state["snapshot"],
                contract,
            )
            require(process.returncode == int(not passed),
                    "the original V24 edge concealed its actual complete exit")
            after = observe_owner(family, state, stage="after-original-edge")
            validate_current_graph(state["v21"], state["audits"], recheck=True)
            fresh = preflight(family, pins)
            require(
                fresh["snapshot"] == state["snapshot"]
                and fresh["audits"]["pins"] == state["audits"]["pins"]
                and fresh["audits"]["graph"] == state["audits"]["graph"]
                and fresh["history"] == state["history"]
                and fresh["preserved_incidents"] == state["preserved_incidents"],
                "an independently owned current native graph or one actual history changed",
            )
            return _publish_original_pair(
                family,
                state,
                deep=False,
                passed=passed,
                report=report,
                raw=raw,
                before=before,
                after=after,
                producer=process,
                contract=contract,
                publication=receipt,
            )
    except ProofV24Failure:
        raise
    except (
        AssertionError, OSError, ValueError, TypeError, KeyError,
        UnicodeError, subprocess.TimeoutExpired,
    ) as error:
        raise _preserve_failure(
            family,
            state,
            deep=False,
            error=error,
            owner_before=before,
            owner_after=after,
            producer=process,
            completed_original=raw,
            validated_original=passed,
            command=command,
            publication=receipt,
        ) from error


def refresh_deep(family: str, pins: Mapping[str, Any]) -> dict[str, Any]:
    state = preflight(family, pins)
    preflight_fresh_destinations(family, deep=True)
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    edge, qualified_edge, edge_raw, edge_proof_raw = authenticate_qualified_edge(
        family,
        state,
        contract,
    )
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    process: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    receipt = new_publication_receipt(family, deep=True)
    try:
        before = observe_owner(family, state, stage="before-original-deep")
        validate_current_graph(state["v21"], state["audits"], recheck=True)
        with tempfile.TemporaryDirectory(
            prefix="rebar-v24-original-deep-" + family + "-",
            dir="/tmp",
        ) as directory:
            private = Path(directory).resolve()
            require(private.parent == Path("/tmp").resolve(),
                    "the original V24 deep escaped its exact isolated temporary root")
            temporary = private / (
                "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
                + "-POSTFINAL-CURRENT-BUILD-V24-PRIVATE.json.gz"
            )
            command = [
                str(original.PINNED_EXECUTABLE), "-I", "-B", "-c",
                original.DEEP_LAUNCHER, str(ROOT), metadata["module"],
                str(edge_target(family, True)), str(temporary), str(private),
            ]
            process = _run_original(command)
            require(temporary.is_file() and not temporary.is_symlink(),
                    "the original V24 deep worker produced no real complete archive")
            raw = original.read_regular(temporary, "complete private original V24 deep")
            report, passed = state["v8"].validate_deep(
                raw,
                family,
                edge,
                state["snapshot"],
                contract,
            )
            require(process.returncode == int(not passed),
                    "the original V24 deep concealed its actual complete exit")
            after = observe_owner(family, state, stage="after-original-deep")
            validate_current_graph(state["v21"], state["audits"], recheck=True)
            fresh = preflight(family, pins)
            require(
                fresh["snapshot"] == state["snapshot"]
                and fresh["audits"]["pins"] == state["audits"]["pins"]
                and fresh["audits"]["graph"] == state["audits"]["graph"]
                and fresh["history"] == state["history"]
                and fresh["preserved_incidents"] == state["preserved_incidents"]
                and original.read_regular(
                    edge_target(family, True),
                    "complete unchanged independently passing actual V24 edge",
                ) == edge_raw
                and original.read_regular(
                    edge_proof_target(family, True),
                    "complete unchanged actual same-family V24 edge proof",
                ) == edge_proof_raw,
                "the qualifying edge, native graph, or one genuine history changed",
            )
            return _publish_original_pair(
                family,
                state,
                deep=True,
                passed=passed,
                report=report,
                raw=raw,
                before=before,
                after=after,
                producer=process,
                contract=contract,
                publication=receipt,
                qualified_edge=qualified_edge,
                edge=edge,
            )
    except ProofV24Failure:
        raise
    except (
        AssertionError, OSError, ValueError, TypeError, KeyError,
        UnicodeError, subprocess.TimeoutExpired,
    ) as error:
        raise _preserve_failure(
            family,
            state,
            deep=True,
            error=error,
            owner_before=before,
            owner_after=after,
            producer=process,
            completed_original=raw,
            validated_original=passed,
            command=command,
            publication=receipt,
        ) from error


class SyntheticPublicationOps(failed.SyntheticPublicationOps):
    """Reuse only a frozen, purely in-memory syscall double; never a publisher."""

    def write(self, descriptor: int, payload: memoryview) -> int:
        if self._fails("negative-write") or self._fails("boolean-write"):
            require(
                descriptor == self.file_fd
                and self.current_path is not None
                and isinstance(payload, memoryview)
                and len(payload) > 0,
                "an injected invalid return lost its real descriptor and requested bytes",
            )
            self.write_calls += 1
            if self._fails("negative-write"):
                return -1
            return True
        return super().write(descriptor, payload)


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (
        ProofV24Error,
        failed.ProofV22Error,
        failed.reviewed.ProofV20Error,
        failed.reviewed.reviewed.ProofV18Error,
        historical_v14.ProofV14Error,
        original.ProofV11Error,
        legacy.ProofV12Error,
        AssertionError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
        OverflowError,
    ):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def _poison(value: Any) -> Any:
    return failed._poison(value)


def _synthetic_state(
    family: str,
    source_digest: str,
    pins: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    prior, owner = failed._synthetic_state(
        family,
        original.synthetic_digest("source-only-v24-frozen-failed-v22-controller"),
        pins,
    )
    graph = copy.deepcopy(prior["audits"]["graph"])
    actual_v13 = expected_v13_failure_summary()
    actual_v15 = expected_v15_failure_summary()
    actual_v17 = expected_v17_failure_summary()
    actual_v19 = expected_v19_failure_summary()
    history = {
        **copy.deepcopy(prior["history"]),
        "preserved_v13_first_audit_failure": copy.deepcopy(actual_v13),
        "preserved_v15_first_audit_failure": copy.deepcopy(actual_v15),
        "preserved_v17_first_audit_failure": copy.deepcopy(actual_v17),
        "preserved_v19_first_audit_failure": copy.deepcopy(actual_v19),
    }

    class SourceOnlyV21:
        CORE_FAMILIES = FAMILIES
        OWNED_SOURCE_PATHS = {
            selected: original.FAMILIES[selected]["sources"]
            for selected in FAMILIES
        }
        OWNED_NATIVE_PATHS = {
            selected: original.FAMILIES[selected]["native"]
            for selected in FAMILIES
        }

        @staticmethod
        def validate_native_owner(
            record: Mapping[str, Any],
            selected: str,
            expected: Mapping[str, str],
        ) -> dict[str, Any]:
            return prior["v21"].validate_native_owner(record, selected, expected)

        @staticmethod
        @contextlib.contextmanager
        def read_only_history_boundary() -> Any:
            yield {
                "candidate_imports": 0,
                "native_workers_started": 0,
                "subprocesses_started": 0,
                "filesystem_writes": 0,
                "clock_samples": 0,
            }

        @staticmethod
        def read_only_current_graph() -> dict[str, Any]:
            return copy.deepcopy(graph)

    audits = {
        "base": {"schema": V21_BASE_SCHEMA, "status": "PASS"},
        "strict": {"schema": V21_STRICT_SCHEMA, "status": "PASS"},
        "graph": graph,
        "pins": dict(pins),
        "history": history,
        "preserved_zig_failure": history["preserved_zig_failure"],
        "preserved_v13_failure": actual_v13,
        "preserved_v15_failure": actual_v15,
        "preserved_v17_failure": actual_v17,
        "preserved_v19_failure": actual_v19,
        "owner": prior["owner"],
    }
    incidents = {
        **copy.deepcopy(prior["preserved_incidents"]),
        "v13_first_owner_preflight_failure": copy.deepcopy(actual_v13),
        "v13_first_owner_preflight_failure_qualifies_current_engine": False,
        "v15_first_owner_preflight_failure": copy.deepcopy(actual_v15),
        "v15_first_owner_preflight_failure_qualifies_current_engine": False,
        "v17_first_owner_postflight_failure": copy.deepcopy(actual_v17),
        "v17_first_owner_postflight_failure_qualifies_current_engine": False,
        "v19_first_owner_publication_failure": copy.deepcopy(actual_v19),
        "v19_first_owner_publication_failure_qualifies_current_engine": False,
        "v22_first_proof_preflight_failure": expected_v22_failure_summary(pins),
        "v22_first_proof_preflight_failure_qualifies_current_engine": False,
        "historical_v10_graph_qualifies_current_engine": False,
    }
    return {
        "v21": SourceOnlyV21,
        "owner": prior["owner"],
        "v8": None,
        "audits": audits,
        "snapshot": copy.deepcopy(prior["snapshot"]),
        "history": history,
        "preserved_incidents": incidents,
        "controller": {
            "source_path": SOURCE_RELATIVE,
            "source_sha256": source_digest,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": PROTOCOL_SHA256,
            "frozen_failed_v22_source_path": V22_SOURCE_RELATIVE,
            "frozen_failed_v22_source_sha256": V22_SOURCE_SHA256,
            "frozen_failed_v22_protocol_path": V22_PROTOCOL_RELATIVE,
            "frozen_failed_v22_protocol_sha256": V22_PROTOCOL_SHA256,
            "frozen_failed_v22_incident_path": V22_FAILURE_RELATIVE,
            "frozen_failed_v22_incident_sha256": V22_FAILURE_SHA256,
            "frozen_failed_v22_qualifies_current_engine": False,
        },
        "parent_environment": {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        },
    }, owner


def _synthetic_report(family: str, *, deep: bool, passed: bool) -> dict[str, Any]:
    return failed._synthetic_report(family, deep=deep, passed=passed)


def _check_fault_receipt(
    *,
    family: str,
    deep: bool,
    passed: bool,
    purpose: str,
    stage: str,
) -> bool:
    receipt = new_publication_receipt(family, deep=deep)
    ops = SyntheticPublicationOps(fail_purpose=purpose, fail_stage=stage)
    archive = (
        b"source-only-v24-complete-original:" + family.encode("ascii")
        + (b":deep" if deep else b":edge")
        + (b":pass" if passed else b":fail")
    )
    if purpose == "proof":
        publish_exclusive(
            receipt,
            family,
            deep=deep,
            passed=passed,
            purpose="archive",
            path=expected_publication_target(
                family,
                deep=deep,
                passed=passed,
                purpose="archive",
            ),
            payload=archive,
            operations=ops,
        )
    target = expected_publication_target(
        family,
        deep=deep,
        passed=passed,
        purpose=purpose,
    )
    if purpose != "proof":
        raw = archive
        payload: Any = raw
    else:
        document = {
            "schema": SCHEMA + "-synthetic-canonical-owner-proof",
            "family": family,
            "deep": deep,
            "passed": passed,
        }
        raw = original.canonical(document)
        payload = (document, raw)
    try:
        publish_exclusive(
            receipt,
            family,
            deep=deep,
            passed=passed,
            purpose=purpose,
            path=target,
            payload=payload,
            operations=ops,
        )
    except V24PublicationFailure as error:
        row = receipt["artifacts"][purpose]
        actual_passed = passed if purpose in ("archive", "proof") else None
        validate_publication_receipt(
            receipt,
            family,
            deep=deep,
            passed=actual_passed,
            original_raw=archive if purpose == "proof" else None,
        )
        require(
            error.receipt == receipt
            and error.stage in {
                "target-validation", "directory-open", "directory-identity",
                "exclusive-create", "write", "file-fsync", "file-close",
                "directory-fsync", "directory-close", "readback",
                "canonical-readback", "file-cleanup-close",
                "directory-cleanup-close",
            }
            and row["path"] == target.relative_to(ROOT).as_posix()
            and row["expected_sha256"] == hashlib.sha256(raw).hexdigest()
            and row["canonical_document_expected"] is (purpose == "proof"),
            "a failed actual V24 transition lost its exact normalized syscall receipt",
        )
        if stage in ("target-validation", "directory-open"):
            require(not row["directory_verified"] and not row["created"],
                    "a precreation failure invented a directory or exclusive file")
        elif stage in ("directory-identity", "exclusive-create"):
            require(not row["created"], "a failed O_EXCL invented an actual file")
        elif stage in (
            "write", "zero-write", "negative-write", "excess-write", "boolean-write",
        ):
            actual_return = row["actual_write_calls"][0]["returned_bytes"]
            require(
                row["created"] and row["bytes_written"] == 0
                and not row["file_fsynced"]
                and len(row["actual_write_calls"]) == 1
                and row["actual_write_calls"][0]["requested_bytes"] == len(raw)
                and (
                    (stage == "write" and actual_return is None)
                    or (stage == "zero-write"
                        and type(actual_return) is int and actual_return == 0)
                    or (stage == "negative-write"
                        and type(actual_return) is int and actual_return == -1)
                    or (stage == "excess-write"
                        and type(actual_return) is int
                        and actual_return == len(raw) + 1)
                    or (stage == "boolean-write" and actual_return is True)
                ),
                "a failed first write hid the real exclusively created empty artifact",
            )
        elif stage == "partial-write":
            require(
                row["created"] and row["bytes_written"] == 1
                and not row["write_complete"] and not row["file_fsynced"]
                and row["actual_write_calls"] == [
                    {"requested_bytes": len(raw), "returned_bytes": 1},
                    {"requested_bytes": len(raw) - 1, "returned_bytes": None},
                ],
                "an interrupted write lost its actually completed partial byte",
            )
        elif stage == "file-fsync":
            require(row["write_complete"] and not row["file_fsynced"],
                    "a failed file fsync claimed nonexistent actual durability")
        elif stage == "file-close":
            require(row["file_fsynced"] and not row["file_closed"]
                    and not row["directory_fsynced"],
                    "a failed actual file close was retried or falsely qualified")
        elif stage == "directory-fsync":
            require(row["file_fsynced"] and row["file_closed"]
                    and not row["directory_fsynced"] and not row["validated"],
                    "a failed parent fsync falsely qualified the artifact")
        elif stage == "directory-close":
            require(row["directory_fsynced"] and not row["directory_closed"]
                    and not row["validated"],
                    "a failed actual directory close was retried")
        elif stage == "readback":
            require(row["directory_fsynced"] and row["directory_closed"]
                    and row["observed_sha256"] is None and not row["validated"],
                    "a failed final reread invented actual proof bytes")
        elif stage == "readback-mismatch":
            require(row["directory_fsynced"] and row["directory_closed"]
                    and original.valid_sha256(row["observed_sha256"])
                    and row["observed_sha256"] != row["expected_sha256"]
                    and not row["validated"],
                    "an actually mismatching reread was falsely qualified")
        if purpose == "proof":
            require(receipt["artifacts"]["archive"]["validated"]
                    and not row["validated"],
                    "a failed owner proof retroactively qualified an unpaired archive")
        return True
    return False


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime_source_only()
    inherited = failed.candidate_free_self_test()
    require(
        inherited.get("status") == "PASS"
        and inherited.get("candidate_imports") == 0
        and inherited.get("subprocesses") == 0
        and inherited.get("file_writes") == 0
        and inherited.get("clock_samples") == 0
        and inherited.get("historical_evidence_reads") == 0
        and inherited.get("actual_audit_report_reads") == 0
        and inherited.get("holdout_reads") == 0
        and inherited.get("synthetic_results_qualify_candidates") is False
        and type(inherited.get("check_count")) is int
        and inherited["check_count"] >= 2200
        and isinstance(inherited.get("checks"), list)
        and len(inherited["checks"]) == inherited["check_count"],
        "the complete reviewed candidate-free V22/V20/V18/V14/V12/V11 boundary weakened",
    )
    source = original.read_regular(ROOT / SOURCE_RELATIVE, "complete source-only V24 controller")
    protocol = original.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    frozen_failed_source = original.authenticate_frozen(V22_SOURCE_RELATIVE, V22_SOURCE_SHA256)
    frozen_failed_protocol = original.authenticate_frozen(
        V22_PROTOCOL_RELATIVE,
        V22_PROTOCOL_SHA256,
    )
    source_digest = hashlib.sha256(source).hexdigest()
    tree = ast.parse(source.decode("utf-8"), filename=SOURCE_RELATIVE)
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        checks.append({"name": "v24:" + name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        checks.append(rejected("v24:" + name, action))

    pins = {
        "audit_source": V21_SOURCE_SHA256,
        "audit_protocol": V21_PROTOCOL_SHA256,
        "base_report": original.synthetic_digest("source-only-v24-runtime-base-report"),
        "strict_report": original.synthetic_digest("source-only-v24-runtime-strict-report"),
    }
    with original.source_only_boundary() as effects:
        accept("parse-complete-additive-current-controller", isinstance(tree, ast.Module))
        accept("bind-frozen-current-correctness-protocol",
               hashlib.sha256(protocol).hexdigest() == PROTOCOL_SHA256)
        accept("preserve-genuine-immutable-failed-v22-source",
               hashlib.sha256(frozen_failed_source).hexdigest() == V22_SOURCE_SHA256)
        accept("preserve-genuine-immutable-failed-v22-protocol",
               hashlib.sha256(frozen_failed_protocol).hexdigest() == V22_PROTOCOL_SHA256)
        accept("retain-all-original-223198-edge-checks-and-49-categories",
               original.EDGE_CHECKS == 223198 and original.EDGE_CATEGORIES == 49)
        accept("retain-all-original-393-deep-checks-and-64-seeds",
               original.DEEP_CHECKS == 393 and original.DEEP_SEEDED_CASES == 64)
        accept("retain-three-independent-twelve-source-five-native-families",
               FAMILIES == ("rust", "vm", "zig")
               and sum(len(original.FAMILIES[x]["sources"]) for x in FAMILIES) == 12
               and sum(len(original.FAMILIES[x]["native"]) for x in FAMILIES) == 5)
        accept("own-exact-18-field-write-ledger-without-mutating-failed-v22",
               len(failed.RECEIPT_FIELDS) == 17
               and RECEIPT_FIELDS == (*failed.RECEIPT_FIELDS, "actual_write_calls")
               and len(RECEIPT_FIELDS) == 18
               and len(set(RECEIPT_FIELDS)) == 18)
        accept("use-runtime-only-distinct-audit-report-pins",
               validated_pins(pins) == pins)
        accept("retain-actual-frozen-c6-failure-fingerprint",
               original.valid_sha256(V22_FAILURE_SHA256)
               and V22_FAILURE_RELATIVE.endswith(
                   "POSTFINAL-CURRENT-BUILD-V22-READONLY-INTEGRATION-PREFLIGHT-FAILURE.json"
               ))
        named = {
            item.name: item
            for item in tree.body
            if isinstance(item, (ast.FunctionDef, ast.ClassDef))
        }
        for role in (
            "normalize_publication_payload", "preflight", "validate_current_graph",
            "validate_preserved_incidents", "expected_v13_failure_summary",
            "validate_v13_failure_summary", "expected_v22_failure_document",
            "expected_v22_failure_summary", "validate_v22_failure_document",
            "authenticate_v22_failure", "observe_owner", "captured_native_owner_records",
            "build_durable_wrapper", "validate_durable_wrapper",
            "authenticate_qualified_edge", "authenticate_qualified_deep",
            "refresh_edge", "refresh_deep", "publish_exclusive",
        ):
            accept("retain-complete-independent-correctness-role:" + role,
                   isinstance(named.get(role), ast.FunctionDef))
        publisher = named.get("publish_exclusive")
        if isinstance(publisher, ast.FunctionDef):
            methods = {
                node.func.attr
                for node in ast.walk(publisher)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            for method in (
                "check_target", "open_directory", "verify_directory", "create",
                "write", "fsync", "close", "read_regular",
            ):
                accept("own-exact-exclusive-descriptor-syscall:" + method,
                       method in methods)
            accept(
                "normalize-canonical-document-before-exclusive-create",
                any(isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "normalize_publication_payload"
                    for node in ast.walk(publisher)),
            )
            attempts = [
                node for node in ast.walk(publisher)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append"
            ]
            writes = [
                node for node in ast.walk(publisher)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "write"
            ]
            observed_returns = [
                node for node in ast.walk(publisher)
                if isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "attempt"
                    and isinstance(target.slice, ast.Constant)
                    and target.slice.value == "returned_bytes"
                    for target in node.targets
                )
            ]
            accept(
                "record-requested-attempt-before-real-exclusive-write-syscall",
                len(attempts) == 1 and len(writes) == 1
                and attempts[0].lineno < writes[0].lineno,
            )
            accept(
                "preserve-returned-value-immediately-after-real-write-syscall",
                len(writes) == 1 and len(observed_returns) == 1
                and writes[0].lineno < observed_returns[0].lineno,
            )
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.attr in ("exclusive_publish", "publish_exclusive")):
                continue
            accept(
                "never-delegate-exclusive-publisher:"
                + str(node.lineno) + ":" + str(node.col_offset),
                node.func.value.id not in ("original", "legacy", "historical_v14", "failed"),
            )
        current = named.get("validate_current_graph")
        if isinstance(current, ast.FunctionDef):
            calls = {
                node.func.attr for node in ast.walk(current)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            accept("postflight-uses-only-real-read-only-current-graph",
                   "read_only_current_graph" in calls
                   and "snapshot_current_graph" not in calls)
            accept("postflight-enforces-the-genuine-no-worker-effect-boundary",
                   "read_only_history_boundary" in calls)
        owner_function = named.get("observe_owner")
        if isinstance(owner_function, ast.FunctionDef):
            accept(
                "preserve-complete-real-native-owner-before-postflight",
                not any(isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == "validate_current_graph"
                        for node in ast.walk(owner_function)),
            )
        for role in ("refresh_edge", "refresh_deep"):
            function = named.get(role)
            if not isinstance(function, ast.FunctionDef):
                continue
            owners = [
                node for node in ast.walk(function)
                if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name)
                        and target.id in ("before", "after")
                        for target in node.targets)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "observe_owner"
            ]
            postflights = [
                node for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "validate_current_graph"
            ]
            accept("retain-both-real-owners-before-every-pure-postflight:" + role,
                   len(owners) == 2 and len(postflights) >= 2)

        v22_document = expected_v22_failure_document(pins)
        v22_summary = expected_v22_failure_summary(pins)
        accept("retain-all-25-authentic-root-v22-failure-document-fields",
               type(v22_document) is dict and len(v22_document) == 25)
        accept("retain-all-27-normalized-authentic-root-v22-failure-fields",
               type(v22_summary) is dict and len(v22_summary) == 27
               and v22_summary == {"source_path": V22_FAILURE_RELATIVE,
                                   "sha256": V22_FAILURE_SHA256, **v22_document})
        accept("retain-every-one-of-the-25-actual-failed-inline-source-lines",
               len(v22_document["actual_invocation"]["actual_inline_python_source_lines"]) == 25)
        accept("retain-every-one-of-the-24-actual-combined-traceback-lines",
               len(v22_document["actual_combined_traceback_lines"]) == 24
               and v22_document["actual_combined_traceback_line_count"] == 24)
        accept("never-invent-missing-original-failed-invocation-effect-counters",
               v22_document["actual_failed_invocation_boundary_counters"]
               == LOST_FAILED_BOUNDARY)
        accept("retain-only-actually-measured-independent-five-zero-follow-up-effects",
               v22_document["independent_follow_up_differential"]
               ["read_only_boundary_effects"] == {
                   "candidate_imports": 0, "clock_samples": 0,
                   "filesystem_writes": 0, "native_workers_started": 0,
                   "subprocesses_started": 0,
               })
        accept("retain-actual-first-rust-failure-with-zero-owners-edge-and-deep-workers",
               v22_document["attempted_family"] == "rust"
               and v22_document["families_not_reached"] == ["vm", "zig"]
               and v22_document["native_owner_workers_started"] == 0
               and v22_document["original_edge_workers_started"] == 0
               and v22_document["original_deep_workers_started"] == 0)
        accept("never-retroactively-qualify-the-genuine-failed-v22-controller",
               v22_document["status"] == "FAIL"
               and v22_document["qualifies_current_engine"] is False
               and v22_document["production_observations_invented"] is False
               and v22_document["synthetic"] is False)
        accept("bind-actual-report-digests-only-to-runtime-supplied-audit-pins",
               v22_document["actual_passing_prerequisites"]["base_report_sha256"]
               == pins["base_report"]
               and v22_document["actual_passing_prerequisites"]["strict_report_sha256"]
               == pins["strict_report"])
        accept("validate-the-exact-source-only-full-v22-failure-document",
               validate_v22_failure_document(v22_document, pins) == v22_summary)
        for key in tuple(v22_document):
            altered = copy.deepcopy(v22_document)
            altered[key] = _poison(altered[key])
            reject("reject-forged-genuine-v22-root-failure-document:" + key,
                   lambda item=altered: validate_v22_failure_document(item, pins))
        for parent_key in (
            "actual_invocation", "frozen_failed_controller",
            "actual_passing_prerequisites", "actual_historical_summary_mismatch",
            "independent_follow_up_differential",
        ):
            for key in tuple(v22_document[parent_key]):
                altered = copy.deepcopy(v22_document)
                altered[parent_key][key] = _poison(altered[parent_key][key])
                reject("reject-forged-nested-authentic-v22-failure:"
                       + parent_key + ":" + key,
                       lambda item=altered: validate_v22_failure_document(item, pins))
        for key in tuple(v22_document["independent_follow_up_differential"]
                         ["read_only_boundary_effects"]):
            altered = copy.deepcopy(v22_document)
            altered["independent_follow_up_differential"][
                "read_only_boundary_effects"
            ][key] = 1
            reject("reject-invented-independent-v22-follow-up-effect:" + key,
                   lambda item=altered: validate_v22_failure_document(item, pins))
        for key in ("base_report", "strict_report"):
            forged = dict(pins)
            forged[key] = original.synthetic_digest("source-only-v24-forged-pin:" + key)
            reject("reject-v22-incident-bound-to-a-different-actual-report:" + key,
                   lambda other=forged: validate_v22_failure_document(v22_document, other))

        for version, expected, validator in (
            ("v13", expected_v13_failure_summary(), validate_v13_failure_summary),
            ("v15", expected_v15_failure_summary(), validate_v15_failure_summary),
            ("v17", expected_v17_failure_summary(), validate_v17_failure_summary),
            ("v19", expected_v19_failure_summary(), validate_v19_failure_summary),
        ):
            accept("retain-every-authentic-original-history-field:" + version,
                   validator(expected) == expected)
            for key in tuple(expected):
                forged = copy.deepcopy(expected)
                forged[key] = _poison(forged[key])
                reject("reject-forged-complete-historical-failure:"
                       + version + ":" + key,
                       lambda item=forged, validate=validator: validate(item))
        reject(
            "reject-the-immutable-failed-v22-short-v13-stage",
            lambda: validate_v13_failure_summary(failed.expected_v13_failure_summary()),
        )
        accept("require-actual-authenticated-long-26-field-v13-failure-stage",
               len(expected_v13_failure_summary()) == 26
               and expected_v13_failure_summary()["failed_stage"] == TRUE_V13_FAILURE_STAGE)
        accept("retain-all-28-18-and-36-real-v15-v17-v19-failure-fields",
               (len(expected_v15_failure_summary()),
                len(expected_v17_failure_summary()),
                len(expected_v19_failure_summary())) == (28, 18, 36))
        incident = expected_v19_failure_summary()
        accept("never-qualify-the-real-durable-but-failed-v19-base",
               incident["durable_report_sha256"] == V19_DURABLE_REPORT_SHA256
               and incident["durable_report_bytes"] == V19_DURABLE_REPORT_BYTES
               and incident["durable_embedded_document_status"] == "PASS"
               and incident["actual_controller_status"] == "FAIL"
               and incident["exit_code"] == 1
               and incident["embedded_pass_qualifies_current_engine"] is False
               and incident["canonical_reread_succeeded"] is False)
        accept("retain-all-eighteen-original-and-eight-seeded-zig-failures",
               historical_v14.validate_zig_pattern_mismatches(
                   historical_v14._synthetic_zig_failure_report()
               )["public_mismatch_family_counts"] == {
                   "public-method-introspection": 18,
                   "seeded/public-method-introspection": 8,
               })

        document = {
            "schema": SCHEMA + "-source-only-canonical-document",
            "status": "PASS",
            "nested": {"source_only": True, "ordered": [0, 1, 2]},
        }
        canonical = original.canonical(document)
        accept("normalize-complete-actual-original-bytes",
               normalize_publication_payload(b"source-only-v24-original")
               == (b"source-only-v24-original", None))
        accept("normalize-full-strict-canonical-json-object",
               normalize_publication_payload(document) == (canonical, document))
        accept("normalize-exact-canonical-document-and-bytes-tuple",
               normalize_publication_payload((document, canonical))
               == (canonical, document))
        malformed = (
            ("none", None), ("empty", b""), ("text", "not-bytes"),
            ("integer", 1), ("float", 1.0),
            ("bytearray", bytearray(b"x")), ("memoryview", memoryview(b"x")),
            ("list", [document, canonical]), ("empty-tuple", ()),
            ("short-tuple", (document,)),
            ("long-tuple", (document, canonical, canonical)),
            ("nonmapping-tuple", ("not-a-document", canonical)),
            ("nonbytes-tuple", (document, canonical.decode("ascii"))),
            ("mismatched-tuple", (document, canonical + b" ")),
            ("duplicate-json-keys", ({"value": 1}, b'{"value":1,"value":2}\n')),
            ("nonfinite-value", {"value": float("nan")}),
            ("nonstring-key", {1: "forbidden"}),
            ("nested-nonstring-key", {"nested": {1: "forbidden"}}),
        )
        for name, invalid in malformed:
            reject("reject-malformed-normalized-canonical-payload:" + name,
                   lambda value=invalid: normalize_publication_payload(value))
        reject("reject-oversized-normalized-original",
               lambda: normalize_publication_payload(
                   b"x" * (original.MAX_FILE_BYTES + 1)
               ))
        for key in PIN_NAMES:
            absent = dict(pins)
            del absent[key]
            reject("reject-missing-runtime-only-independent-audit-pin:" + key,
                   lambda value=absent: validated_pins(value))
            for label, invalid in (
                ("none", None), ("empty", ""), ("integer", 1),
                ("short", "a" * 63), ("long", "a" * 65),
                ("uppercase", "A" * 64), ("nonhex", "g" * 64),
            ):
                reject("reject-forged-runtime-only-audit-pin:" + key + ":" + label,
                       lambda value={**pins, key: invalid}: validated_pins(value))
            for other in PIN_NAMES:
                if key == other:
                    continue
                reject("reject-reused-independent-audit-fingerprint:"
                       + key + ":" + other,
                       lambda value={**pins, key: pins[other]}: validated_pins(value))

        stages = (
            "target-validation", "directory-open", "directory-identity",
            "exclusive-create", "write", "zero-write", "negative-write",
            "excess-write", "boolean-write", "partial-write", "file-fsync",
            "file-close", "directory-fsync", "directory-close", "readback",
            "readback-mismatch",
        )
        for family in FAMILIES:
            state, owner = _synthetic_state(family, source_digest, pins)
            accept("retain-exact-nine-key-current-preflight-state:" + family,
                   set(state) == {
                       "v21", "owner", "v8", "audits", "snapshot", "history",
                       "preserved_incidents", "controller", "parent_environment",
                   })
            accept("retain-exact-eleven-role-four-history-v21-audit:" + family,
                   len(state["audits"]) == 11
                   and state["audits"]["pins"] == pins)
            accept("prove-complete-effect-free-current-source-and-native-graph:" + family,
                   validate_current_graph(state["v21"], state["audits"], recheck=True)
                   == state["audits"]["graph"])
            accept("preserve-exact-fifth-genuine-v22-incident-outside-v21-history:" + family,
                   state["preserved_incidents"]["v22_first_proof_preflight_failure"]
                   == v22_summary
                   and state["preserved_incidents"]
                   ["v22_first_proof_preflight_failure_qualifies_current_engine"] is False
                   and "preserved_v22_failure" not in state["audits"]
                   and "preserved_v22_first_audit_failure" not in state["history"])
            for version, role, expected in (
                ("v13", "v13_first_owner_preflight_failure",
                 expected_v13_failure_summary()),
                ("v15", "v15_first_owner_preflight_failure",
                 expected_v15_failure_summary()),
                ("v17", "v17_first_owner_postflight_failure",
                 expected_v17_failure_summary()),
                ("v19", "v19_first_owner_publication_failure",
                 expected_v19_failure_summary()),
            ):
                accept("retain-exact-immutable-authenticated-history:"
                       + family + ":" + version,
                       state["audits"]["preserved_" + version + "_failure"]
                       == state["history"]["preserved_" + version + "_first_audit_failure"]
                       == state["preserved_incidents"][role] == expected
                       and state["preserved_incidents"]
                       [role + "_qualifies_current_engine"] is False)
            accept("never-invent-a-native-owner-before-it-ran:" + family,
                   captured_native_owner_records(family, None, None) == {})
            accept("retain-real-completed-owner-before-rechecking:" + family,
                   captured_native_owner_records(family, owner, None)
                   == {"before-original-worker": owner})
            accept("retain-both-actually-completed-native-owners:" + family,
                   captured_native_owner_records(family, owner, owner) == {
                       "before-original-worker": owner,
                       "after-original-worker": owner,
                   })
            for key in tuple(state["audits"]["graph"]):
                forged = copy.deepcopy(state["audits"])
                forged["graph"][key] = _poison(forged["graph"][key])
                reject("reject-forged-current-audited-graph:" + family + ":" + key,
                       lambda item=forged, selected=state["v21"]:
                           validate_current_graph(selected, item, recheck=False))
            for key in tuple(owner):
                forged = copy.deepcopy(owner)
                forged[key] = _poison(forged[key])
                reject("reject-forged-genuine-independent-owner:"
                       + family + ":" + key,
                       lambda item=forged, selected=family, native=state["v21"],
                       expected=dict(state["snapshot"]["native_sha256_by_path"]):
                           native.validate_native_owner(item, selected, expected))
            for deep in (False, True):
                mode = "deep" if deep else "edge"
                for passed in (False, True):
                    outcome = "pass" if passed else "fail"
                    label = family + ":" + mode + ":" + outcome
                    archive_raw = ("source-only-v24-original:" + label).encode("ascii")
                    proof_document = {
                        "schema": SCHEMA + "-synthetic-native-owner",
                        "family": family,
                        "deep": deep,
                        "passed": passed,
                        "source_only": True,
                    }
                    proof_raw = original.canonical(proof_document)
                    receipt = new_publication_receipt(family, deep=deep)
                    accept("validate-complete-empty-exclusive-receipt:" + label,
                           validate_publication_receipt(receipt, family, deep=deep)
                           == receipt
                           and len({
                               id(receipt["artifacts"][role]["actual_write_calls"])
                               for role in PURPOSES
                           }) == len(PURPOSES))
                    operations = SyntheticPublicationOps(
                        fail_purpose="archive",
                        fail_stage="partial-success",
                        partial_bytes=1,
                    )
                    archive_path = expected_publication_target(
                        family,
                        deep=deep,
                        passed=passed,
                        purpose="archive",
                    )
                    archive_digest = publish_exclusive(
                        receipt,
                        family,
                        deep=deep,
                        passed=passed,
                        purpose="archive",
                        path=archive_path,
                        payload=archive_raw,
                        operations=operations,
                    )
                    accept("retain-every-single-byte-normalized-original-write:" + label,
                           archive_digest == hashlib.sha256(archive_raw).hexdigest()
                           and receipt["artifacts"]["archive"]["bytes_written"]
                           == len(archive_raw)
                           and receipt["artifacts"]["archive"]["validated"] is True
                           and operations.write_calls == len(archive_raw)
                           and receipt["artifacts"]["archive"]["actual_write_calls"]
                           == [
                               {"requested_bytes": len(archive_raw) - index,
                                "returned_bytes": 1}
                               for index in range(len(archive_raw))
                           ])
                    report = _synthetic_report(family, deep=deep, passed=passed)
                    producer = subprocess.CompletedProcess(
                        args=["source-only-original-v24", family, mode],
                        returncode=int(not passed),
                        stdout=("source-only-v24-stdout:" + label).encode("ascii"),
                        stderr=("source-only-v24-stderr:" + label).encode("ascii"),
                    )
                    edge = {
                        "status": "PASS",
                        "campaign_qualified": True,
                        "archive_path": edge_target(family, True).relative_to(ROOT).as_posix(),
                        "archive_sha256": original.synthetic_digest(
                            "source-only-v24-edge:" + family
                        ),
                        "proof_path": edge_proof_target(family, True)
                        .relative_to(ROOT).as_posix(),
                        "proof_sha256": original.synthetic_digest(
                            "source-only-v24-edge-proof:" + family
                        ),
                    }
                    wrapper = build_durable_wrapper(
                        family,
                        state,
                        deep=deep,
                        passed=passed,
                        original_report=report,
                        archive_path=archive_path,
                        archive_sha256=archive_digest,
                        archive_bytes=len(archive_raw),
                        owner_before=owner,
                        owner_after=owner,
                        producer=producer,
                        archive_receipt=receipt["artifacts"]["archive"],
                        qualified_edge=edge if deep else None,
                    )
                    options: dict[str, Any] = {
                        "deep": deep,
                        "passed": passed,
                        "original_report": report,
                        "archive_path": archive_path,
                        "archive_sha256": archive_digest,
                        "archive_bytes": len(archive_raw),
                        "owner_before": owner,
                        "owner_after": owner,
                        "producer": producer,
                        "archive_receipt": receipt["artifacts"]["archive"],
                        "qualified_edge": edge if deep else None,
                    }
                    accept("validate-complete-current-original-owner-proof:" + label,
                           validate_durable_wrapper(wrapper, family, state, **options)
                           == wrapper
                           and wrapper["actual_invoking_controller"] == "V24"
                           and wrapper["campaign_qualified"] is passed)
                    for key in tuple(wrapper):
                        forged = copy.deepcopy(wrapper)
                        forged[key] = _poison(forged[key])
                        reject("reject-forged-complete-current-owner-proof:"
                               + label + ":" + key,
                               lambda item=forged, selected=family,
                               current=state, arguments=options:
                                   validate_durable_wrapper(
                                       item,
                                       selected,
                                       current,
                                       **arguments,
                                   ))
                    proof_path = expected_publication_target(
                        family,
                        deep=deep,
                        passed=passed,
                        purpose="proof",
                    )
                    proof_digest = publish_exclusive(
                        receipt,
                        family,
                        deep=deep,
                        passed=passed,
                        purpose="proof",
                        path=proof_path,
                        payload=(proof_document, proof_raw),
                        operations=operations,
                    )
                    accept("validate-complete-canonical-one-pair-publication:" + label,
                           proof_digest == hashlib.sha256(proof_raw).hexdigest()
                           and receipt["artifacts"]["archive"]["validated"] is True
                           and receipt["artifacts"]["proof"]["validated"] is True
                           and receipt["artifacts"]["proof"]
                           ["canonical_document_expected"] is True
                           and receipt["artifacts"]["proof"]
                           ["canonical_document_validated"] is True
                           and receipt["artifacts"]["proof"]["actual_write_calls"]
                           == [{
                               "requested_bytes": len(proof_raw),
                               "returned_bytes": len(proof_raw),
                           }])
                    accept("validate-all-exact-final-publication-transitions:" + label,
                           validate_publication_receipt(
                               receipt,
                               family,
                               deep=deep,
                               passed=passed,
                               original_raw=archive_raw,
                           ) == receipt)
                    for purpose in PURPOSES:
                        for field in RECEIPT_FIELDS:
                            forged = copy.deepcopy(receipt)
                            forged["artifacts"][purpose][field] = _poison(
                                forged["artifacts"][purpose][field]
                            )
                            reject("reject-forged-full-syscall-receipt:"
                                   + label + ":" + purpose + ":" + field,
                                   lambda item=forged, selected=family,
                                   isdeep=deep, outcome_passed=passed,
                                   complete=archive_raw:
                                       validate_publication_receipt(
                                           item,
                                           selected,
                                           deep=isdeep,
                                           passed=outcome_passed,
                                           original_raw=complete,
                                       ))
                    for purpose in ("archive", "proof"):
                        for index, call in enumerate(
                            receipt["artifacts"][purpose]["actual_write_calls"]
                        ):
                            for field in ("requested_bytes", "returned_bytes"):
                                forged = copy.deepcopy(receipt)
                                forged["artifacts"][purpose][
                                    "actual_write_calls"
                                ][index][field] = _poison(call[field])
                                reject(
                                    "reject-forged-actual-ordered-write-call:"
                                    + label + ":" + purpose + ":"
                                    + str(index) + ":" + field,
                                    lambda item=forged, selected=family,
                                    isdeep=deep, outcome_passed=passed,
                                    complete=archive_raw:
                                        validate_publication_receipt(
                                            item,
                                            selected,
                                            deep=isdeep,
                                            passed=outcome_passed,
                                            original_raw=complete,
                                        ),
                                )
                        forged = copy.deepcopy(receipt)
                        forged["artifacts"][purpose]["actual_write_calls"].append({
                            "requested_bytes": 1,
                            "returned_bytes": 1,
                        })
                        reject(
                            "reject-appended-actual-write-after-completion:"
                            + label + ":" + purpose,
                            lambda item=forged, selected=family, isdeep=deep,
                            outcome_passed=passed, complete=archive_raw:
                                validate_publication_receipt(
                                    item,
                                    selected,
                                    deep=isdeep,
                                    passed=outcome_passed,
                                    original_raw=complete,
                                ),
                        )
                    forged = copy.deepcopy(receipt)
                    forged["artifacts"]["proof"]["actual_write_calls"] = (
                        forged["artifacts"]["archive"]["actual_write_calls"]
                    )
                    reject(
                        "reject-cross-role-aliased-actual-write-ledgers:" + label,
                        lambda item=forged, selected=family, isdeep=deep,
                        outcome_passed=passed, complete=archive_raw:
                            validate_publication_receipt(
                                item,
                                selected,
                                deep=isdeep,
                                passed=outcome_passed,
                                original_raw=complete,
                            ),
                    )
                    for purpose in ("invalidated", "failure"):
                        side = new_publication_receipt(family, deep=deep)
                        side_raw = (
                            "source-only-v24-" + purpose + ":" + label
                        ).encode("ascii")
                        side_ops = SyntheticPublicationOps(
                            fail_purpose=purpose,
                            fail_stage="partial-success",
                            partial_bytes=1,
                        )
                        side_path = expected_publication_target(
                            family,
                            deep=deep,
                            passed=passed,
                            purpose=purpose,
                        )
                        side_digest = publish_exclusive(
                            side,
                            family,
                            deep=deep,
                            passed=passed,
                            purpose=purpose,
                            path=side_path,
                            payload=side_raw,
                            operations=side_ops,
                        )
                        accept(
                            "retain-every-real-ordered-diagnostic-write:"
                            + label + ":" + purpose,
                            side_digest == hashlib.sha256(side_raw).hexdigest()
                            and side["passed"] is None
                            and side["artifacts"][purpose]["validated"] is True
                            and side_ops.write_calls == len(side_raw)
                            and side["artifacts"][purpose]["actual_write_calls"]
                            == [
                                {"requested_bytes": len(side_raw) - index,
                                 "returned_bytes": 1}
                                for index in range(len(side_raw))
                            ]
                            and validate_publication_receipt(
                                side,
                                family,
                                deep=deep,
                            ) == side,
                        )
                        for field in RECEIPT_FIELDS:
                            forged_side = copy.deepcopy(side)
                            forged_side["artifacts"][purpose][field] = _poison(
                                forged_side["artifacts"][purpose][field]
                            )
                            reject(
                                "reject-forged-complete-diagnostic-write-receipt:"
                                + label + ":" + purpose + ":" + field,
                                lambda item=forged_side, selected=family,
                                isdeep=deep:
                                    validate_publication_receipt(
                                        item,
                                        selected,
                                        deep=isdeep,
                                    ),
                            )
                        for index, call in enumerate(
                            side["artifacts"][purpose]["actual_write_calls"]
                        ):
                            for field in ("requested_bytes", "returned_bytes"):
                                forged_side = copy.deepcopy(side)
                                forged_side["artifacts"][purpose][
                                    "actual_write_calls"
                                ][index][field] = _poison(call[field])
                                reject(
                                    "reject-forged-real-diagnostic-write-call:"
                                    + label + ":" + purpose + ":"
                                    + str(index) + ":" + field,
                                    lambda item=forged_side, selected=family,
                                    isdeep=deep:
                                        validate_publication_receipt(
                                            item,
                                            selected,
                                            deep=isdeep,
                                        ),
                                )
                    for purpose in PURPOSES:
                        for stage in stages:
                            accept("preserve-real-failed-exclusive-transition:"
                                   + label + ":" + purpose + ":" + stage,
                                   _check_fault_receipt(
                                       family=family,
                                       deep=deep,
                                       passed=passed,
                                       purpose=purpose,
                                       stage=stage,
                                   ))

        blocked: tuple[tuple[str, Callable[[], Any]], ...] = (
            ("fifth-actual-v22-preflight-failure",
             lambda: original.authenticate_frozen(V22_FAILURE_RELATIVE, V22_FAILURE_SHA256)),
            ("actual-v21-base-report",
             lambda: original.read_regular(ROOT / V21_BASE_REPORT_RELATIVE,
                                           "forbidden source-only actual V21 base")),
            ("actual-v21-strict-report",
             lambda: original.read_regular(ROOT / V21_STRICT_REPORT_RELATIVE,
                                           "forbidden source-only actual V21 strict")),
            ("actual-v13-failure",
             lambda: original.authenticate_frozen(V13_FAILURE_RELATIVE, V13_FAILURE_SHA256)),
            ("actual-v15-failure",
             lambda: original.authenticate_frozen(V15_FAILURE_RELATIVE, V15_FAILURE_SHA256)),
            ("actual-v17-failure",
             lambda: original.authenticate_frozen(V17_FAILURE_RELATIVE, V17_FAILURE_SHA256)),
            ("actual-v19-failure",
             lambda: original.authenticate_frozen(V19_FAILURE_RELATIVE, V19_FAILURE_SHA256)),
            ("actual-v24-edge",
             lambda: original.read_regular(edge_target("rust", True),
                                           "forbidden source-only actual V24 edge")),
            ("actual-v24-deep",
             lambda: original.read_regular(deep_target("zig", True),
                                           "forbidden source-only actual V24 deep")),
            ("production-rust", lambda: importlib.import_module("candidates.rust_candidate")),
            ("production-c", lambda: importlib.import_module("candidates.vm_candidate")),
            ("production-zig", lambda: importlib.import_module("candidates.zig_candidate")),
            ("external-engine", lambda: importlib.import_module("regex")),
            ("holdout", lambda: builtins.open(ROOT / "performance/holdout.json", "rb")),
            ("unrelated-read", lambda: builtins.open(ROOT / "README.md", "rb")),
            ("wall-clock", lambda: time.time()),
            ("performance-clock", lambda: time.perf_counter()),
            ("original-worker", lambda: subprocess.run(["forbidden-source-only-v24-original"])),
            ("native-worker", lambda: subprocess.Popen(["forbidden-source-only-v24-native"])),
            ("native-thread", lambda: threading.Thread(target=lambda: None).start()),
            ("native-process", lambda: multiprocessing.Process(target=lambda: None).start()),
            ("temporary-worker", lambda: tempfile.TemporaryDirectory()),
            ("actual-original-write", lambda: edge_target("rust", True).write_bytes(b"x")),
            ("actual-proof-write", lambda: deep_proof_target("zig", True).write_text("x")),
        )
        for label, action in blocked:
            reject("actively-enforce-complete-source-only-effect-boundary:" + label, action)
        accept("actively-block-all-real-native-and-third-party-candidate-imports",
               effects["candidate_import_attempts_blocked"] >= 4)
        accept("actively-block-all-five-actual-incidents-and-real-audit-evidence",
               effects["evidence_read_attempts_blocked"] >= 10)
        accept("actively-block-all-original-native-thread-and-process-workers",
               effects["worker_attempts_blocked"] >= 5)
        accept("actively-block-all-real-wall-and-performance-clock-samples",
               effects["clock_attempts_blocked"] >= 2)
        accept("actively-block-all-actual-original-and-proof-filesystem-writes",
               effects["write_attempts_blocked"] >= 2)
        accept("never-import-any-real-native-production-candidate",
               not any(name == "candidates" or name.startswith("candidates.")
                       or name == "rebar" or name.startswith("rebar.")
                       for name in sys.modules))
        accept("never-import-the-real-v21-owner-in-source-only-control-mode",
               "tools.postfinal_independent_engine_audit_v21" not in sys.modules)
        accept("retain-at-least-1000-independent-new-v24-source-controls",
               len(checks) >= 1000)
        require(
            len({row["name"] for row in checks}) == len(checks),
            "an actual independent V24 source-control name was reused",
        )
        failures = [row["name"] for row in checks if row["passed"] is not True]
        require(
            not failures,
            "an exact V24 native/five-history/canonical source control failed: "
            + ", ".join(failures[:12]),
        )
        observed = dict(effects)
    verify_runtime_source_only()
    inherited_checks = [
        {"name": "inherited-v22:" + row["name"], "passed": row["passed"]}
        for row in inherited["checks"]
    ]
    combined = [*inherited_checks, *checks]
    require(
        len({row["name"] for row in combined}) == len(combined)
        and all(row["passed"] is True for row in combined)
        and len(combined) >= 3200,
        "the complete inherited and independent V24 source-control denominator changed",
    )
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "check_count": len(combined),
        "checks": combined,
        "new_v24_check_count": len(checks),
        "inherited_v22_check_count": inherited["check_count"],
        "inherited_v20_check_count": inherited["inherited_v20_check_count"],
        "inherited_v18_check_count": inherited["inherited_v18_check_count"],
        "inherited_v14_check_count": inherited["inherited_v14_check_count"],
        "inherited_v12_check_count": inherited["inherited_v12_check_count"],
        "inherited_v11_check_count": inherited["inherited_v11_check_count"],
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "historical_evidence_reads": 0,
        "actual_audit_report_reads": 0,
        "holdout_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "actual_v24_controller_sha256": source_digest,
        "actual_v24_protocol_sha256": PROTOCOL_SHA256,
        "immutable_failed_v22_controller_sha256": V22_SOURCE_SHA256,
        "immutable_failed_v22_protocol_sha256": V22_PROTOCOL_SHA256,
        "immutable_failed_v22_incident_sha256": V22_FAILURE_SHA256,
        "immutable_failed_v22_qualifies_current_engine": False,
        "frozen_v21_controller_sha256": V21_SOURCE_SHA256,
        "frozen_v21_protocol_sha256": V21_PROTOCOL_SHA256,
        "future_v21_base_report_hash_guessed": False,
        "future_v21_strict_report_hash_guessed": False,
        "authentic_v13_failed_stage": TRUE_V13_FAILURE_STAGE,
        "authentic_v13_field_count": 26,
        "authentic_v15_field_count": 28,
        "authentic_v17_field_count": 18,
        "authentic_v19_field_count": 36,
        "authentic_v22_failure_document_field_count": 25,
        "authentic_v22_failure_summary_field_count": 27,
        "authentic_v22_inline_source_line_count": 25,
        "authentic_v22_combined_traceback_line_count": 24,
        "authentic_v22_failed_boundary_counters": LOST_FAILED_BOUNDARY,
        "actual_v13_first_preworker_failure_sha256": V13_FAILURE_SHA256,
        "actual_v15_first_preworker_failure_sha256": V15_FAILURE_SHA256,
        "actual_v17_first_postflight_failure_sha256": V17_FAILURE_SHA256,
        "actual_v19_first_publication_failure_sha256": V19_FAILURE_SHA256,
        "actual_v22_first_preflight_failure_sha256": V22_FAILURE_SHA256,
        "actual_v22_first_preflight_failure_qualifies_current_engine": False,
        "actual_v19_unqualified_durable_report_sha256": V19_DURABLE_REPORT_SHA256,
        "actual_v19_unqualified_durable_report_bytes": V19_DURABLE_REPORT_BYTES,
        "original_edge_checks": original.EDGE_CHECKS,
        "original_edge_categories": original.EDGE_CATEGORIES,
        "original_deep_checks": original.DEEP_CHECKS,
        "original_deep_seeded_cases": original.DEEP_SEEDED_CASES,
        "independent_family_count": len(FAMILIES),
        "complete_owned_source_count": 12,
        "complete_native_elf_count": 5,
        "immutable_failed_v22_receipt_field_count": len(failed.RECEIPT_FIELDS),
        "owned_v24_receipt_field_count": len(RECEIPT_FIELDS),
        "actual_per_write_syscall_ledger_required": True,
        "blocked_effect_attempts": observed,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--qualified-edge", action="store_true")
    mode.add_argument("--qualified-deep", action="store_true")
    parser.add_argument(
        "--module",
        choices=tuple(item["module"] for item in original.FAMILIES.values()),
    )
    parser.add_argument("--v21-audit-source-sha256")
    parser.add_argument("--v21-audit-protocol-sha256")
    parser.add_argument("--v21-base-report-sha256")
    parser.add_argument("--v21-strict-report-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(
            options.module is None
            and all(getattr(options, key) is None for key in (
                "v21_audit_source_sha256", "v21_audit_protocol_sha256",
                "v21_base_report_sha256", "v21_strict_report_sha256",
            )),
            "candidate-free V24 controls cannot read actual reports or run workers",
        )
        result = candidate_free_self_test()
    else:
        require(type(options.module) is str,
                "an original worker requires its exact independently owned family")
        family = next(
            name for name, metadata in original.FAMILIES.items()
            if metadata["module"] == options.module
        )
        pins = validated_pins({
            "audit_source": options.v21_audit_source_sha256,
            "audit_protocol": options.v21_audit_protocol_sha256,
            "base_report": options.v21_base_report_sha256,
            "strict_report": options.v21_strict_report_sha256,
        })
        result = refresh_edge(family, pins) if options.qualified_edge else refresh_deep(
            family,
            pins,
        )
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofV24Failure as error:
        print(json.dumps(error.evidence, ensure_ascii=True, allow_nan=False, sort_keys=True))
        raise SystemExit(1) from error
