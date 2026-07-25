#!/usr/bin/env python3
"""Bind original CPython correctness to genuine current V23 native ownership."""

from __future__ import annotations

import argparse
import ast
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_current_build_proofs_v24 as historical


original = historical.original
SCHEMA = "rebar-postfinal-current-build-proofs-v26"
SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v26.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V26.md"
PROTOCOL_SHA256 = (
    "71e28127d019aa94a05c18f1c33492ee296f81bdf54bb35b4911ef75fc3041a6"
)
V23_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v23.py"
V23_SOURCE_SHA256 = (
    "a565cff78306e9d21a97fbb301e087db7371273bc4079533517492788f70b1cc"
)
V23_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V23.md"
)
V23_PROTOCOL_SHA256 = (
    "8b3da77ba5a659d72c940cd595726b1d9b000ed7db1fac5027745c37d504f6bd"
)
V23_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V23.json"
)
V23_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V23.json"
)
V23_ROOT_INTEGRATION_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V23-ROOT-READONLY-INTEGRATION-PASS.json"
)
V23_ROOT_INTEGRATION_SHA256 = (
    "c50e4e5c7ecf9bb5fe09278dd21d9bdd1cf9c705208d7f72e2cbefcfdd4776d6"
)
V22_SOURCE_SHA256 = (
    "ba3062b5fe4aea944e89022266c8d9a7a035708bb30d736f074fc29ce7157e27"
)
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
HISTORICAL_V21_PINS = {
    "audit_source":
        "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d",
    "audit_protocol":
        "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f",
    "base_report":
        "4c1de720abb53a5baee56c36a09039e48137e83b2db103cb0d6e77866b496ce4",
    "strict_report":
        "6e742e2e10cde837cb4c39ffe6d1ab12634d672924e109a727e9a558ad22194d",
}
HISTORICAL_PIN_NAMES = tuple(historical.PIN_NAMES)
PIN_NAMES = (
    "audit_source",
    "audit_protocol",
    "base_report",
    "base_receipt",
    "strict_report",
    "strict_receipt",
)
FAMILIES = tuple(historical.FAMILIES)
PURPOSES = tuple(historical.PURPOSES)
RECEIPT_FIELDS = tuple(historical.RECEIPT_FIELDS)
TRUE_V13_FAILURE_STAGE = (
    "historical-zig-edge-authentication-before-any-new-native-owner-worker"
)
LOST_FAILED_BOUNDARY = "NOT PRESERVED BY THE FAILED CONTROLLER"
READ_ONLY_EFFECTS = frozenset({
    "candidate_imports",
    "native_workers_started",
    "subprocesses_started",
    "filesystem_writes",
    "clock_samples",
})


class ProofV26Error(AssertionError):
    """The actual current audit, original correctness, or history failed."""


class V26PublicationFailure(ProofV26Error):
    """Preserve every completed and pending actual publication transition."""

    def __init__(
        self, message: str, *, stage: str,
        receipt: Mapping[str, Any], cause: BaseException,
        actual_cleanup_failures: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.receipt = copy.deepcopy(dict(receipt))
        self.cause = cause
        self.actual_primary_failure = {
            "stage": stage,
            "actual_error_type": type(cause).__name__,
            "actual_error_message": str(cause),
        }
        self.actual_cleanup_failures = copy.deepcopy(
            [] if actual_cleanup_failures is None else actual_cleanup_failures
        )


class ProofV26Failure(ProofV26Error):
    """Carry an actual durable failure without manufacturing observations."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = copy.deepcopy(dict(evidence))


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ProofV26Error(message)


def verify_runtime_source_only() -> None:
    historical.verify_runtime_source_only()
    require(
        ROOT == original.ROOT
        and Path(__file__).resolve() == ROOT / SOURCE_RELATIVE
        and FAMILIES == ("rust", "vm", "zig")
        and tuple(original.FAMILIES) == FAMILIES
        and tuple(HISTORICAL_PIN_NAMES) == (
            "audit_source", "audit_protocol", "base_report", "strict_report"
        )
        and tuple(PIN_NAMES) == (
            "audit_source", "audit_protocol", "base_report", "base_receipt",
            "strict_report", "strict_receipt",
        )
        and len(RECEIPT_FIELDS) == len(set(RECEIPT_FIELDS)) == 18
        and RECEIPT_FIELDS.count("actual_write_calls") == 1
        and original.EDGE_CHECKS == 223198
        and original.EDGE_CATEGORIES == 49
        and original.DEEP_CHECKS == 393
        and original.DEEP_SEEDED_CASES == 64
        and sum(len(row["sources"]) for row in original.FAMILIES.values()) == 12
        and sum(len(row["native"]) for row in original.FAMILIES.values()) == 5,
        "V26 requires three families, the complete original oracle, and 18 unique receipt fields",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            or name == "rebar" or name.startswith("rebar.")
            for name in sys.modules
        ),
        "a production candidate escaped into the candidate-free V26 controller",
    )


def checked_family(family: str) -> dict[str, Any]:
    require(type(family) is str and family in FAMILIES,
            "V26 requires the actual independently owned Rust, C, or Zig family")
    return original.checked_family(family)


def validated_pins(supplied: Any) -> dict[str, str]:
    require(isinstance(supplied, Mapping) and set(supplied) == set(PIN_NAMES),
            "BLOCKED: supply six genuine and distinct V23 ownership and artifact SHA-256 values")
    pins: dict[str, str] = {}
    for key in PIN_NAMES:
        value = supplied[key]
        require(original.valid_sha256(value),
                "BLOCKED: supply the actual independently published V23 " + key)
        pins[key] = value
    require(len(set(pins.values())) == len(PIN_NAMES) == 6,
            "V23 source, protocol, both reports, and both receipt digests must all differ")
    require(pins["audit_source"] == V23_SOURCE_SHA256
            and pins["audit_protocol"] == V23_PROTOCOL_SHA256,
            "current ownership requires the independently frozen V23 source and protocol")
    require(all(pins[role] not in HISTORICAL_V21_PINS.values()
                for role in ("base_report", "base_receipt",
                             "strict_report", "strict_receipt")),
            "a historical V21 report or receipt cannot qualify the current V23 graph")
    return pins


def authenticate_controller() -> dict[str, str]:
    verify_runtime_source_only()
    previous = historical.authenticate_controller()
    require(
        previous.get("source_path") == historical.SOURCE_RELATIVE
        and previous.get("source_sha256")
        == "92b1f082196592e578a5fa6e09b63637c6a1304c04875e5816938ed4fc28eb52"
        and previous.get("protocol_path") == historical.PROTOCOL_RELATIVE
        and previous.get("protocol_sha256") == historical.PROTOCOL_SHA256,
        "the independently reviewed immutable V24 proof source or protocol changed",
    )
    source = original.read_regular(ROOT / SOURCE_RELATIVE,
                                   "complete actual V26 proof-controller source")
    protocol = original.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": hashlib.sha256(protocol).hexdigest(),
    }


def edge_target(family: str, passed: bool) -> Path:
    checked_family(family)
    require(type(passed) is bool, "an original edge requires its observed outcome")
    result = "pass" if passed else "failures"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v26-qualified-" + result + ".json.gz"
    )


def edge_proof_target(family: str, passed: bool) -> Path:
    target = edge_target(family, passed)
    return target.parent / (target.name.removesuffix(".json.gz") + "-proof.json")


def deep_target(family: str, passed: bool) -> Path:
    metadata = checked_family(family)
    require(type(passed) is bool, "an original deep report requires its observed outcome")
    result = "PASS" if passed else "FAILURES"
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V26-" + result + ".json.gz"
    )


def deep_proof_target(family: str, passed: bool) -> Path:
    target = deep_target(family, passed)
    return target.parent / (target.name.removesuffix(".json.gz") + "-PROOF.json")


def failure_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool, "a genuine producer failure requires its actual mode")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V26-PRODUCER-CRASH.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v26-qualified-producer-crash.json.gz"
    )


def invalidated_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool, "a genuine invalidated original needs its actual mode")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V26-INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v26-qualified-"
        "invalidated-after-owner-failure.json.gz"
    )


def expected_publication_target(
    family: str, *, deep: bool, passed: bool | None, purpose: str,
) -> Path:
    checked_family(family)
    require(type(deep) is bool and purpose in PURPOSES,
            "publication requires its exact current family, mode, and artifact role")
    if purpose == "invalidated":
        return invalidated_target(family, deep=deep)
    if purpose == "failure":
        return failure_target(family, deep=deep)
    require(type(passed) is bool,
            "an original archive or proof cannot invent its actual result")
    if purpose == "archive":
        return deep_target(family, passed) if deep else edge_target(family, passed)
    return deep_proof_target(family, passed) if deep else edge_proof_target(
        family, passed
    )


def preflight_fresh_destinations(family: str, *, deep: bool) -> None:
    checked_family(family)
    require(type(deep) is bool, "fresh original paths require their exact mode")
    targets = (
        (deep_target(family, True), deep_target(family, False),
         deep_proof_target(family, True), deep_proof_target(family, False))
        if deep else
        (edge_target(family, True), edge_target(family, False),
         edge_proof_target(family, True), edge_proof_target(family, False))
    ) + (failure_target(family, deep=deep), invalidated_target(family, deep=deep))
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    require(len(targets) == len(set(targets)) == 6
            and all("current-build-v26" in target.name.lower() for target in targets),
            "V26 must preflight six distinct fresh current-build paths")
    for target in targets:
        original.fresh_target(target, parent)


def _load_v23() -> Any:
    return original.import_frozen(
        "tools.postfinal_independent_engine_audit_v23",
        V23_SOURCE_RELATIVE,
        V23_SOURCE_SHA256,
    )


def _expected_v23_root_integration() -> dict[str, Any]:
    descriptors = [
        {"descriptor": 4, "operation": "open", "role": "parent", "status": "PASS"},
        {"descriptor": 5, "operation": "open", "role": "writer", "status": "PASS"},
        {"descriptor": 5, "operation": "close", "role": "writer", "status": "PASS"},
        {"descriptor": 5, "operation": "open", "role": "reader", "status": "PASS"},
        {"descriptor": 5, "operation": "close", "role": "reader", "status": "PASS"},
        {"descriptor": 4, "operation": "close", "role": "parent", "status": "PASS"},
    ]
    return {
        "actual_candidate_workers": 0,
        "actual_native_owner_workers": 0,
        "actual_read_only_descriptor_events": descriptors,
        "actual_reference_workers": 0,
        "actual_v23_audits_run": 0,
        "all_original_method_count": 165,
        "all_v23_report_and_receipt_destinations_fresh": True,
        "applicable_public_method_count": 152,
        "genuine_reference_roles": 2,
        "historical_failure_qualifies_current_engine": False,
        "historical_v21_base_report_sha256": HISTORICAL_V21_PINS["base_report"],
        "historical_v21_graph_qualifies_current_engine": False,
        "historical_v21_protocol_sha256": HISTORICAL_V21_PINS["audit_protocol"],
        "historical_v21_source_sha256": HISTORICAL_V21_PINS["audit_source"],
        "historical_v21_strict_report_sha256": HISTORICAL_V21_PINS["strict_report"],
        "holdout": "NOT ACCESSED",
        "independent_families": list(FAMILIES),
        "kernel_reused_writer_descriptor_for_reader": True,
        "named_private_class_waiver_count": 2,
        "named_private_method_waiver_count": 13,
        "native_binary_count": 5,
        "performance": "NOT MEASURED",
        "production_observations_invented": False,
        "protocol_sha256": V23_PROTOCOL_SHA256,
        "public_method_waivers": [],
        "read_only_boundary_effects": {key: 0 for key in sorted(READ_ONLY_EFFECTS)},
        "reference_named_debug_skips_per_role": 1,
        "reference_passes_per_role": 151,
        "reference_skip_kind": "named-private-debug-condition",
        "schema":
            "rebar-root-v23-independent-engine-audit-"
            "read-only-history-and-real-descriptor-integration",
        "source_count": 12,
        "source_sha256": V23_SOURCE_SHA256,
        "status": "PASS",
        "v15_actual_original_cached_matcher_checks": 304,
        "v15_actual_original_debug_skips": 1,
        "v15_actual_original_failure_bytes": 17338567,
        "v15_actual_original_failure_passing_methods": 139,
        "v15_actual_original_failure_sha256":
            "fcd83830b36afd94dee6b926764a6300eaf048d5fa81404563d7e8afea2482c2",
        "v15_actual_original_harness_errors": 11,
        "v15_actual_original_native_owner_checks": 304,
        "v15_actual_original_required_engine_gaps": 1,
        "v15_historical_ownership_failure_sha256":
            "a3695f1fd847e9ad882783d18c519b551d7791c5327f55964e202a31ade818ff",
        "v6_reference_sha256":
            "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf",
    }


def _validate_v23_root_integration(document: Any) -> dict[str, Any]:
    expected = _expected_v23_root_integration()
    require(type(document) is dict and len(document) == len(expected) == 43
            and document == expected,
            "the authentic frozen V23 root read-only integration or one observation changed")
    events = document["actual_read_only_descriptor_events"]
    require(type(events) is list and len(events) == 6
            and [(event["operation"], event["role"]) for event in events] == [
                ("open", "parent"), ("open", "writer"), ("close", "writer"),
                ("open", "reader"), ("close", "reader"), ("close", "parent"),
            ]
            and events[1]["descriptor"] == events[2]["descriptor"]
            == events[3]["descriptor"] == events[4]["descriptor"]
            and events[0]["descriptor"] == events[5]["descriptor"]
            and set(document["read_only_boundary_effects"]) == READ_ONLY_EFFECTS
            and all(type(value) is int and value == 0
                    for value in document["read_only_boundary_effects"].values())
            and document["actual_v23_audits_run"] == 0
            and document["actual_native_owner_workers"] == 0
            and document["historical_v21_graph_qualifies_current_engine"] is False
            and document["historical_failure_qualifies_current_engine"] is False
            and document["v15_actual_original_failure_sha256"]
            != document["v15_historical_ownership_failure_sha256"],
            "a read-only integration invented audits, lost descriptors, or qualified history")
    return document


def _validate_v23_producer_bytes(
    v23: Any, document: Any, raw: Any, label: str,
) -> bytes:
    require(isinstance(document, Mapping)
            and type(raw) is bytes and 0 < len(raw) <= original.MAX_FILE_BYTES
            and type(label) is str and bool(label),
            "genuine V23 evidence requires one bounded complete document and byte stream")
    encoded = v23.canonical(document)
    require(type(encoded) is bytes and encoded == raw
            and original.decode_json(raw, label) == dict(document),
            "the " + label + " was not produced in the exact frozen V23 canonical dialect")
    return raw


def _authenticate_v23_root_integration(v23: Any) -> dict[str, Any]:
    raw = original.authenticate_frozen(
        V23_ROOT_INTEGRATION_RELATIVE, V23_ROOT_INTEGRATION_SHA256
    )
    document = original.decode_json(
        raw, "actual pinned complete canonical V23 root read-only integration"
    )
    _validate_v23_producer_bytes(
        v23, document, raw,
        "actual frozen V23 root read-only integration",
    )
    return _validate_v23_root_integration(document)


def _read_only_v23_graph(v23: Any, expected: Mapping[str, Any]) -> dict[str, Any]:
    with v23.historical_v21.read_only_history_boundary() as effects:
        actual = v23.read_only_current_graph()
    require(isinstance(effects, Mapping)
            and set(effects) == READ_ONLY_EFFECTS
            and all(type(value) is int and value == 0 for value in effects.values()),
            "a current-graph recheck imported a candidate, started work, wrote, or timed")
    require(isinstance(actual, dict) and actual == expected,
            "an actual currently owned V23 source or native ELF changed")
    return actual


def _authenticate_v23_reports(supplied: Mapping[str, Any]) -> dict[str, Any]:
    pins = validated_pins(supplied)
    v23 = _load_v23()
    controller = v23.authenticate_controller()
    require(controller == {
        "source_path": V23_SOURCE_RELATIVE,
        "source_sha256": V23_SOURCE_SHA256,
        "protocol_path": V23_PROTOCOL_RELATIVE,
        "protocol_sha256": V23_PROTOCOL_SHA256,
    }, "the genuine independently frozen V23 ownership controller changed")
    root_integration = _authenticate_v23_root_integration(v23)
    require(tuple(v23.CORE_FAMILIES) == FAMILIES
            and v23.BASE_REPORT_RELATIVE == V23_BASE_REPORT_RELATIVE
            and v23.STRICT_REPORT_RELATIVE == V23_STRICT_REPORT_RELATIVE,
            "the frozen current owner changed its complete three-family report contract")
    reports: dict[str, dict[str, Any]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    graphs: dict[str, dict[str, Any]] = {}
    for role, receipt_role, relative, receipt_relative, strict in (
        ("base_report", "base_receipt", v23.BASE_REPORT_RELATIVE,
         v23.BASE_RECEIPT_RELATIVE, False),
        ("strict_report", "strict_receipt", v23.STRICT_REPORT_RELATIVE,
         v23.STRICT_RECEIPT_RELATIVE, True),
    ):
        raw = original.authenticate_frozen(relative, pins[role])
        document = original.decode_json(raw, "complete actual canonical V23 " + role)
        _validate_v23_producer_bytes(
            v23, document, raw, "complete actual independently pinned V23 " + role
        )
        receipt_raw = original.authenticate_frozen(
            receipt_relative, pins[receipt_role]
        )
        receipt = original.decode_json(
            receipt_raw, "strict unique-key actual V23 " + role + " publication receipt"
        )
        _validate_v23_producer_bytes(
            v23, receipt, receipt_raw,
            "complete actual independently pinned V23 " + receipt_role,
        )
        v23.validate_publication_receipt(receipt, relative, pins[role], len(raw))
        graph = v23.validate_report(
            document,
            pins[role],
            strict=strict,
            base_digest=pins["base_report"] if strict else None,
        )
        require(document.get("audit_source_sha256") == pins["audit_source"]
                and document.get("audit_protocol_sha256") == pins["audit_protocol"],
                "the real V23 report does not bind its independently frozen controller")
        reports[role] = document
        receipts[role] = receipt
        graphs[role] = graph
    require(graphs["base_report"] == graphs["strict_report"],
            "the actual base and strict V23 audits observed different current graphs")
    require(
        reports["strict_report"].get("independent_base_native_owner_workers")
        == reports["base_report"].get("actual_native_owner_workers"),
        "the strict V23 audit substituted the exact externally pinned base owners",
    )
    for role in ("base_report", "strict_report"):
        workers = reports[role].get("actual_native_owner_workers")
        processes = reports[role].get("actual_native_owner_processes")
        require(type(workers) is dict and type(processes) is dict
                and set(workers) == set(processes) == set(FAMILIES),
                "a genuine V23 audit lost one real independent owner or process")
        for family in FAMILIES:
            expected_native = graphs[role]["native_sha256_by_family"][family]
            require(v23.validate_native_owner(
                workers[family], family, expected_native
            ) == workers[family]
                    and v23.validate_native_worker_transcript(
                        processes[family], workers[family], family, expected_native
                    ) == processes[family],
                    "a genuine V23 audit lost an actual complete owner transcript: "
                    + role + ":" + family)
    graph = _read_only_v23_graph(v23, graphs["base_report"])
    base_history = v23.validate_preserved_history(
        reports["base_report"].get("preserved_immutable_history")
    )
    strict_history = v23.validate_preserved_history(
        reports["strict_report"].get("preserved_immutable_history")
    )
    require(base_history == strict_history,
            "the actual current ownership reports disagree about preserved history")
    require(set(graph.get("source_sha256_by_family", {})) == set(FAMILIES)
            and set(graph.get("native_sha256_by_family", {})) == set(FAMILIES)
            and graph.get("source_count") == 12
            and graph.get("native_binary_count") == 5,
            "V23 must authenticate all twelve current sources and five native ELFs")
    return {
        "v23": v23,
        "pins": pins,
        "controller": controller,
        "root_integration": root_integration,
        "base": reports["base_report"],
        "strict": reports["strict_report"],
        "base_receipt": receipts["base_report"],
        "strict_receipt": receipts["strict_report"],
        "graph": graph,
        "history": base_history,
    }


def _authenticate_historical_v22_failure() -> dict[str, Any]:
    require(historical.V22_SOURCE_SHA256 == V22_SOURCE_SHA256
            and historical.V22_PROTOCOL_SHA256 == V22_PROTOCOL_SHA256
            and historical.V22_FAILURE_RELATIVE == V22_FAILURE_RELATIVE
            and historical.V22_FAILURE_SHA256 == V22_FAILURE_SHA256,
            "the authentic independently frozen failed V22 source, protocol, or file changed")
    raw = original.authenticate_frozen(V22_FAILURE_RELATIVE, V22_FAILURE_SHA256)
    document = original.decode_json(
        raw, "actual frozen pretty-printed historical V22 preflight failure"
    )
    expected = historical.expected_v22_failure_document(HISTORICAL_V21_PINS)
    require(type(document) is dict and len(document) == len(expected) == 25,
            "the genuine historical V22 first failure lost one of its 25 fields")
    result = historical.validate_v22_failure_document(
        document, HISTORICAL_V21_PINS
    )
    require(len(result) == 27
            and result.get("qualifies_current_engine") is False
            and document.get("actual_failed_invocation_boundary_counters")
            == LOST_FAILED_BOUNDARY
            and len(document.get("actual_combined_traceback_lines", [])) == 24
            and len(document.get("actual_invocation", {}).get(
                "actual_inline_python_source_lines", []
            )) == 25,
            "V26 rewrote, canonically reserialized, or falsely qualified the V22 failure")
    return result


def _validate_historical_incidents(v23: Any, history: Mapping[str, Any]) -> dict[str, Any]:
    validated = v23.validate_preserved_history(history)
    archived = v23.historical_v21.validate_preserved_history(
        validated.get("preserved_v21_immutable_history")
    )
    incidents: dict[str, Any] = {}
    for version, key, validator, count in (
        ("v13", "preserved_v13_first_audit_failure",
         historical.validate_v13_failure_summary, 26),
        ("v15", "preserved_v15_first_audit_failure",
         historical.validate_v15_failure_summary, 28),
        ("v17", "preserved_v17_first_audit_failure",
         historical.validate_v17_failure_summary, 18),
        ("v19", "preserved_v19_first_audit_failure",
         historical.validate_v19_failure_summary, 36),
    ):
        observed = archived.get(key)
        require(type(observed) is dict and len(observed) == count,
                "the genuine historical " + version + " first failure was shortened")
        require(validator(observed) == observed,
                "the genuine historical " + version + " first failure was substituted")
        incidents[version + "_first_owner_failure"] = copy.deepcopy(observed)
        incidents[version + "_first_owner_failure_qualifies_current_engine"] = False
    require(incidents["v13_first_owner_failure"].get("failed_stage")
            == TRUE_V13_FAILURE_STAGE,
            "the actual first V13 failure was replaced by the old mistaken stage")
    incidents["v22_first_proof_preflight_failure"] = (
        _authenticate_historical_v22_failure()
    )
    incidents["v22_first_proof_preflight_failure_qualifies_current_engine"] = False
    incidents["historical_v21_graph_qualifies_current_engine"] = False
    return incidents


def preflight(family: str, supplied: Mapping[str, Any]) -> dict[str, Any]:
    metadata = checked_family(family)
    controller = authenticate_controller()
    parent = historical.validate_parent_environment(os.environ)
    audits = _authenticate_v23_reports(supplied)
    graph = audits["graph"]
    require(tuple(audits["v23"].OWNED_SOURCE_PATHS[family])
            == metadata["sources"]
            and dict(audits["v23"].OWNED_NATIVE_PATHS[family])
            == metadata["native"],
            "the current V23 ownership audit changed the independent family contract")
    snapshot = {
        "family": family,
        "module": metadata["module"],
        "source_sha256_by_path": dict(graph["source_sha256_by_family"][family]),
        "native_sha256_by_path": dict(graph["native_sha256_by_family"][family]),
    }
    require(set(snapshot["source_sha256_by_path"]) == set(metadata["sources"])
            and set(snapshot["native_sha256_by_path"])
            == set(metadata["native"].values()),
            "the actual current family source or native FFI graph was incomplete")
    preserved = _validate_historical_incidents(audits["v23"], audits["history"])
    v8 = original.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        original.V8_PROOF_RELATIVE,
        original.V8_PROOF_SHA256,
    )
    verify_runtime_source_only()
    return {
        "v23": audits["v23"],
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
    require(len(source) == 12 and len(native) == 5
            and all(original.valid_sha256(value)
                    for value in (*source.values(), *native.values())),
            "an actual audited V23 graph omitted one owned source or native ELF")
    return {
        "all_family_audit_qualified": True,
        "all_family_source_sha256_by_path": source,
        "all_family_native_elf_sha256_by_path": native,
    }


def observe_owner(
    family: str, state: Mapping[str, Any], *, stage: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    checked_family(family)
    require(stage in {
        "before-original-edge", "after-original-edge",
        "before-original-deep", "after-original-deep",
    }, "an actual V23 native owner requires its genuine before/after worker stage")
    expected = dict(state["snapshot"]["native_sha256_by_path"])
    v23 = state["v23"]
    actual, transcript = v23.run_native_worker_with_transcript(family, expected)
    owner = v23.validate_native_owner(actual, family, expected)
    observed = v23.validate_native_worker_transcript(
        transcript, actual, family, expected
    )
    require(owner == actual and observed == transcript
            and actual.get("status") == "PASS"
            and actual.get("passed") is True
            and actual.get("family") == family
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
            "the complete actual same-family V23 native owner or transcript failed")
    return copy.deepcopy(actual), copy.deepcopy(transcript)


def normalize_publication_payload(payload: Any) -> tuple[bytes, dict[str, Any] | None]:
    document: dict[str, Any] | None = None
    if type(payload) is bytes:
        raw = payload
    elif type(payload) is dict:
        require(all(type(key) is str for key in payload),
                "a canonical V26 proof requires strictly string object keys")
        try:
            raw = original.canonical(payload)
        except (AssertionError, TypeError, ValueError, OverflowError, UnicodeError) as error:
            raise ProofV26Error("the V26 proof is not finite canonical JSON") from error
        document = payload
    elif type(payload) is tuple:
        require(len(payload) == 2
                and type(payload[0]) is dict and type(payload[1]) is bytes
                and all(type(key) is str for key in payload[0]),
                "a normalized V26 proof requires one exact object-and-bytes pair")
        document, raw = payload
    else:
        raise ProofV26Error("V26 accepts only bounded bytes, an object, or their exact pair")
    require(type(raw) is bytes and 0 < len(raw) <= original.MAX_FILE_BYTES,
            "canonical V26 publication requires complete bounded actual bytes")
    if document is not None:
        decoded = original.decode_json(raw, "complete strict unique-key canonical V26 proof")
        try:
            encoded = original.canonical(document)
        except (AssertionError, TypeError, ValueError, OverflowError, UnicodeError) as error:
            raise ProofV26Error("the V26 object-and-bytes pair is not canonical") from error
        require(decoded == document and encoded == raw
                and original.canonical(decoded) == raw,
                "a complete canonical V26 document failed its strict byte round trip")
    return raw, document


def _empty_artifact(purpose: str) -> dict[str, Any]:
    require(purpose in PURPOSES, "an actual V26 publication invented an artifact role")
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
    require(type(calls) is list,
            "an actual " + purpose + " write ledger must be an ordered private list")
    if row["path"] is None:
        require(not calls, "an unattempted " + purpose + " invented a write syscall")
        return
    expected = row["expected_bytes"]
    require(type(expected) is int and 0 < expected <= original.MAX_FILE_BYTES,
            "an actual " + purpose + " ledger lost its bounded expected byte count")
    remaining = expected
    written = 0
    invalid_final = False
    for index, call in enumerate(calls):
        require(type(call) is dict
                and set(call) == {"requested_bytes", "returned_bytes"}
                and row["created"] is True
                and type(call["requested_bytes"]) is int
                and remaining > 0
                and call["requested_bytes"] == remaining,
                "an actual " + purpose + " write forged its ordered partial continuation")
        returned = call["returned_bytes"]
        if type(returned) is not int or returned <= 0 or returned > remaining:
            require((returned is None or type(returned) in (int, bool))
                    and index + 1 == len(calls)
                    and row["validated"] is False
                    and row["write_complete"] is False
                    and row["file_fsynced"] is False
                    and row["directory_fsynced"] is False,
                    "a pending or invalid actual " + purpose + " write was silently retried")
            invalid_final = True
            break
        written += returned
        remaining -= returned
    require(type(row["bytes_written"]) is int
            and row["bytes_written"] == written
            and row["write_complete"] is (remaining == 0)
            and (not calls or row["created"] is True)
            and (not row["validated"] or not invalid_final)
            and (not row["file_fsynced"] or remaining == 0),
            "an actual " + purpose + " ledger changed its valid prefix or completion")


def new_publication_receipt(family: str, *, deep: bool) -> dict[str, Any]:
    checked_family(family)
    require(type(deep) is bool, "a genuine actual receipt needs its explicit mode")
    return {
        "family": family,
        "deep": deep,
        "passed": None,
        "artifacts": {purpose: _empty_artifact(purpose) for purpose in PURPOSES},
    }


def validate_publication_receipt(
    receipt: Any, family: str, *, deep: bool,
    passed: bool | None = None, original_raw: bytes | None = None,
) -> dict[str, Any]:
    checked_family(family)
    require(type(receipt) is dict
            and set(receipt) == {"family", "deep", "passed", "artifacts"}
            and receipt["family"] == family and receipt["deep"] is deep
            and (receipt["passed"] is None or type(receipt["passed"]) is bool)
            and (passed is None or receipt["passed"] is passed)
            and type(receipt["artifacts"]) is dict
            and set(receipt["artifacts"]) == set(PURPOSES)
            and all(type(receipt["artifacts"][role]) is dict
                    and type(receipt["artifacts"][role].get("actual_write_calls")) is list
                    for role in PURPOSES),
            "a complete actual 18-field V26 publication receipt was forged")
    require(len({id(receipt["artifacts"][role]["actual_write_calls"])
                 for role in PURPOSES}) == len(PURPOSES),
            "independent artifact purposes alias an actual write-call ledger")
    for purpose in PURPOSES:
        row = receipt["artifacts"][purpose]
        require(type(row) is dict and set(row) == set(RECEIPT_FIELDS)
                and row.get("purpose") == purpose
                and all(type(row[key]) is bool for key in (
                    "directory_opened", "directory_verified", "created",
                    "write_complete", "file_fsynced", "file_closed",
                    "directory_fsynced", "directory_closed", "validated",
                    "canonical_document_expected", "canonical_document_validated",
                ))
                and type(row["bytes_written"]) is int and row["bytes_written"] >= 0,
                "an actual " + purpose + " syscall transition or canonical bit was forged")
        if row["path"] is None:
            require(row == _empty_artifact(purpose),
                    "an unattempted artifact invented real filesystem observations")
            _validate_actual_write_calls(row, purpose)
            continue
        target = expected_publication_target(
            family, deep=deep, passed=receipt["passed"], purpose=purpose
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
            and row["write_complete"]
            == (row["bytes_written"] == row["expected_bytes"])
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
            and (purpose != "proof" or row["canonical_document_expected"] is True)
            and (purpose != "proof" or not row["validated"]
                 or row["canonical_document_validated"] is True)
            and row["validated"] == (
                row["observed_sha256"] == row["expected_sha256"]
                and row["directory_fsynced"] and row["directory_closed"]
                and (not row["canonical_document_expected"]
                     or row["canonical_document_validated"])
            ),
            "an actual " + purpose + " create, write, fsync, close, or reread was forged",
        )
        _validate_actual_write_calls(row, purpose)
        if purpose == "proof":
            require(receipt["artifacts"]["archive"]["validated"],
                    "a canonical V26 owner proof preceded its complete durable original")
        if purpose == "archive" and original_raw is not None:
            require(type(original_raw) is bytes
                    and len(original_raw) == row["expected_bytes"]
                    and hashlib.sha256(original_raw).hexdigest()
                    == row["expected_sha256"],
                    "a genuine archive receipt changed actual original worker bytes")
    return receipt


class PublicationOps:
    """Own real, descriptor-relative, exclusive V26 publication."""

    synthetic = False

    def check_target(self, path: Path, parent: Path) -> None:
        original.fresh_target(path, parent)

    def open_directory(self, parent: Path) -> int:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        return os.open(parent, flags)

    def verify_directory(self, descriptor: int, parent: Path) -> None:
        actual = os.fstat(descriptor)
        expected = os.stat(parent, follow_symlinks=False)
        require(stat.S_ISDIR(actual.st_mode) and stat.S_ISDIR(expected.st_mode)
                and (actual.st_dev, actual.st_ino)
                == (expected.st_dev, expected.st_ino),
                "actual V26 publication lost its real nonsymlink directory identity")

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
    receipt: dict[str, Any], family: str, *, deep: bool, passed: bool | None,
    purpose: str, path: Path, payload: Any,
    operations: PublicationOps | Any | None = None,
) -> str:
    checked_family(family)
    require(type(deep) is bool and purpose in PURPOSES and isinstance(path, Path),
            "V26 exclusive publication needs its exact mode, artifact role, and path")
    raw, document = normalize_publication_payload(payload)
    if purpose == "proof":
        require(document is not None,
                "a V26 owner proof must be a finite strict canonical JSON document")
    validate_publication_receipt(receipt, family, deep=deep)
    if purpose in ("archive", "proof"):
        require(type(passed) is bool, "an actual original cannot invent its observed result")
        if receipt["passed"] is None:
            receipt["passed"] = passed
        require(receipt["passed"] is passed,
                "an actual proof changed its original worker outcome")
    target = expected_publication_target(
        family, deep=deep, passed=receipt["passed"], purpose=purpose
    )
    require(path == target, "exclusive V26 publication escaped its frozen output path")
    row = receipt["artifacts"][purpose]
    require(row == _empty_artifact(purpose),
            "an actual exclusive V26 artifact was retried or overwritten")
    if purpose == "proof":
        require(receipt["artifacts"]["archive"]["validated"],
                "a current owner proof preceded its actual validated original")
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
    cleanup_failures: list[dict[str, Any]] = []
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
            attempt = {"requested_bytes": requested, "returned_bytes": None}
            row["actual_write_calls"].append(attempt)
            returned = ops.write(descriptor, view[row["bytes_written"]:])
            attempt["returned_bytes"] = returned
            require(type(returned) is int and 0 < returned <= requested,
                    "an actual V26 write returned zero, negative, oversized, or boolean bytes")
            row["bytes_written"] += returned
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
        saved = ops.read_regular(path, "complete actual exclusive V26 " + purpose)
        require(type(saved) is bytes,
                "an exclusively published V26 artifact lost its actual complete bytes")
        row["observed_sha256"] = hashlib.sha256(saved).hexdigest()
        require(saved == raw and row["observed_sha256"] == row["expected_sha256"],
                "an actual V26 reread changed complete exclusively published bytes")
        if document is not None:
            stage = "canonical-readback"
            decoded = original.decode_json(saved, "complete strict canonical V26 owner proof")
            require(decoded == document and original.canonical(decoded) == saved,
                    "an actual normalized V26 owner proof failed canonical reread")
            row["canonical_document_validated"] = True
        row["validated"] = True
    except (AssertionError, OSError, ValueError, TypeError, KeyError, UnicodeError) as error:
        failure = (stage, error)
    finally:
        for name, role in (("descriptor", "file"), ("directory", "directory")):
            active = descriptor if name == "descriptor" else directory
            if active is None:
                continue
            if name == "descriptor":
                descriptor = None
            else:
                directory = None
            try:
                ops.close(active, directory=role == "directory")
                row[role + "_closed"] = True
            except (AssertionError, OSError, ValueError, TypeError, KeyError) as error:
                cleanup_stage = role + "-cleanup-close"
                cleanup_failures.append({
                    "stage": cleanup_stage,
                    "actual_error_type": type(error).__name__,
                    "actual_error_message": str(error),
                })
                if failure is None:
                    failure = (cleanup_stage, error)
    if failure is not None:
        stage, cause = failure
        raise V26PublicationFailure(
            "actual exclusive V26 " + purpose + " publication failed at " + stage,
            stage=stage,
            receipt=receipt,
            cause=cause,
            actual_cleanup_failures=cleanup_failures,
        ) from cause
    validate_publication_receipt(
        receipt, family, deep=deep, passed=receipt["passed"],
        original_raw=raw if purpose == "archive" else None,
    )
    return row["expected_sha256"]


def failure_publication_fields(
    publication: Mapping[str, Any], family: str, *, deep: bool,
    original_raw: bytes | None,
) -> dict[str, Any]:
    receipt = validate_publication_receipt(
        publication, family, deep=deep, original_raw=original_raw
    )
    result: dict[str, Any] = {}
    for purpose, prefix in (("archive", "v26_original_archive"),
                            ("proof", "v26_owner_proof")):
        row = receipt["artifacts"][purpose]
        for source, suffix in (
            ("path", "path"), ("expected_sha256", "expected_sha256"),
            ("observed_sha256", "observed_sha256"), ("created", "created"),
            ("bytes_written", "bytes_written"),
            ("actual_write_calls", "actual_write_calls"),
            ("file_fsynced", "file_fsynced"),
            ("directory_fsynced", "directory_fsynced"), ("validated", "validated"),
        ):
            result[prefix + "_" + suffix] = copy.deepcopy(row[source])
        if purpose == "proof":
            for field in ("canonical_document_expected", "canonical_document_validated"):
                result[prefix + "_" + field] = row[field]
    result["v26_complete_syscall_publication_receipt"] = copy.deepcopy(receipt)
    result["unpaired_v26_original_archive_qualifies"] = False
    return result


def build_durable_wrapper(
    family: str, state: Mapping[str, Any], *, deep: bool, passed: bool,
    original_report: Mapping[str, Any], archive_path: Path, archive_sha256: str,
    archive_bytes: int, owner_before: Mapping[str, Any],
    owner_before_transcript: Mapping[str, Any], owner_after: Mapping[str, Any],
    owner_after_transcript: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes], archive_receipt: Mapping[str, Any],
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = checked_family(family)
    require(type(deep) is bool and type(passed) is bool
            and isinstance(original_report, Mapping)
            and isinstance(producer, subprocess.CompletedProcess)
            and type(producer.returncode) is int
            and type(producer.stdout) is bytes and type(producer.stderr) is bytes
            and len(producer.stdout) <= original.MAX_CHILD_OUTPUT_BYTES
            and len(producer.stderr) <= original.MAX_CHILD_OUTPUT_BYTES
            and isinstance(archive_path, Path)
            and original.valid_sha256(archive_sha256)
            and type(archive_bytes) is int and 0 < archive_bytes <= original.MAX_FILE_BYTES
            and isinstance(archive_receipt, Mapping),
            "a V26 owner proof requires complete actual original worker observations")
    target = deep_target(family, passed) if deep else edge_target(family, passed)
    proof = deep_proof_target(family, passed) if deep else edge_proof_target(family, passed)
    require(archive_path == target and set(archive_receipt) == set(RECEIPT_FIELDS)
            and archive_receipt.get("purpose") == "archive"
            and archive_receipt.get("path") == target.relative_to(ROOT).as_posix()
            and archive_receipt.get("expected_bytes") == archive_bytes
            and archive_receipt.get("expected_sha256") == archive_sha256
            and archive_receipt.get("observed_sha256") == archive_sha256
            and archive_receipt.get("validated") is True
            and archive_receipt.get("file_fsynced") is True
            and archive_receipt.get("directory_fsynced") is True,
            "a V26 owner proof cannot qualify an incomplete actual original archive")
    _validate_actual_write_calls(archive_receipt, "archive")
    pins = validated_pins(state["audits"]["pins"])
    v23 = state["v23"]
    expected_native = dict(state["snapshot"]["native_sha256_by_path"])
    for record, transcript in (
        (owner_before, owner_before_transcript),
        (owner_after, owner_after_transcript),
    ):
        require(v23.validate_native_owner(record, family, expected_native) == record
                and v23.validate_native_worker_transcript(
                    transcript, record, family, expected_native
                ) == transcript,
                "a durable V26 proof omitted an actual complete V23 owner transcript")
    mode = "qualified-deep" if deep else "qualified-edge"
    controller = state["controller"]
    result: dict[str, Any] = {
        "schema": SCHEMA + "-" + mode + "-durable-proof",
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL",
        "mode": mode,
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "campaign_qualified": passed,
        "proof_path": proof.relative_to(ROOT).as_posix(),
        "original_archive_path": target.relative_to(ROOT).as_posix(),
        "original_archive_sha256": archive_sha256,
        "original_archive_bytes": archive_bytes,
        "original_archive_publication_receipt": copy.deepcopy(dict(archive_receipt)),
        "publication_strategy":
            "v26-owned-normalized-canonical-directory-bound-syscall-receipts",
        "complete_original_producer_bytes_preserved": True,
        "original_archive_is_unmodified_original": True,
        "stdout_is_not_durable_proof": True,
        "original_worker_returncode": producer.returncode,
        "original_worker_stdout": original.observed_stream(producer.stdout, True),
        "original_worker_stderr": original.observed_stream(producer.stderr, True),
        "current_v23_native_owner_before": copy.deepcopy(dict(owner_before)),
        "current_v23_native_owner_before_process":
            copy.deepcopy(dict(owner_before_transcript)),
        "current_v23_native_owner_after": copy.deepcopy(dict(owner_after)),
        "current_v23_native_owner_after_process":
            copy.deepcopy(dict(owner_after_transcript)),
        "full_current_family_source_sha256":
            dict(state["snapshot"]["source_sha256_by_path"]),
        "full_current_family_native_elf_sha256":
            dict(state["snapshot"]["native_sha256_by_path"]),
        "all_family_audited_provenance": audited_graph_provenance(state),
        "actual_v23_audit_source_path": V23_SOURCE_RELATIVE,
        "actual_v23_audit_source_sha256": pins["audit_source"],
        "actual_v23_protocol_path": V23_PROTOCOL_RELATIVE,
        "actual_v23_protocol_sha256": pins["audit_protocol"],
        "actual_v23_base_report_path": V23_BASE_REPORT_RELATIVE,
        "actual_v23_base_report_sha256": pins["base_report"],
        "actual_v23_base_receipt_path": state["v23"].BASE_RECEIPT_RELATIVE,
        "actual_v23_base_receipt_sha256": pins["base_receipt"],
        "actual_v23_strict_report_path": V23_STRICT_REPORT_RELATIVE,
        "actual_v23_strict_report_sha256": pins["strict_report"],
        "actual_v23_strict_receipt_path": state["v23"].STRICT_RECEIPT_RELATIVE,
        "actual_v23_strict_receipt_sha256": pins["strict_receipt"],
        "actual_invoking_controller": "V26",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_refresh_protocol_path": controller["protocol_path"],
        "actual_refresh_protocol_sha256": controller["protocol_sha256"],
        "actual_verified_parent_environment": dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment": historical.worker_environment(),
        "preserved_immutable_history": copy.deepcopy(state["history"]),
        "preserved_actual_failed_incidents": copy.deepcopy(state["preserved_incidents"]),
        "exclusive_creation": True,
        "canonical_document_bytes_normalized": True,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if deep:
        require(isinstance(qualified_edge, Mapping),
                "a genuine current deep proof requires its actual passing V26 edge")
        result.update({
            "seed": original.DEEP_SEED,
            "checks": original.DEEP_CHECKS,
            "seeded_case_count": original.DEEP_SEEDED_CASES,
            "reference_sha256": original.DEEP_REFERENCE_SHA256,
            "actual_sha256": original_report.get("candidate_sha256"),
            "public_mismatch_count": original_report.get("public_mismatch_count"),
            "public_mismatch_family_counts":
                original_report.get("public_mismatch_family_counts"),
            "qualified_edge": copy.deepcopy(dict(qualified_edge)),
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
    document: Any, family: str, state: Mapping[str, Any], *, deep: bool,
    passed: bool, original_report: Mapping[str, Any], archive_path: Path,
    archive_sha256: str, archive_bytes: int, owner_before: Mapping[str, Any],
    owner_before_transcript: Mapping[str, Any], owner_after: Mapping[str, Any],
    owner_after_transcript: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes], archive_receipt: Mapping[str, Any],
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    expected = build_durable_wrapper(
        family, state, deep=deep, passed=passed, original_report=original_report,
        archive_path=archive_path, archive_sha256=archive_sha256,
        archive_bytes=archive_bytes, owner_before=owner_before,
        owner_before_transcript=owner_before_transcript, owner_after=owner_after,
        owner_after_transcript=owner_after_transcript, producer=producer,
        archive_receipt=archive_receipt, qualified_edge=qualified_edge,
    )
    require(type(document) is dict and document == expected
            and producer.returncode == int(not passed)
            and document["campaign_qualified"] is passed
            and document["candidate_module"] == checked_family(family)["module"]
            and document["stdout_is_not_durable_proof"] is True
            and document["production_observations_invented"] is False,
            "a V26 durable owner proof changed actual original worker observations")
    if deep:
        require(isinstance(qualified_edge, Mapping)
                and qualified_edge.get("status") == "PASS"
                and qualified_edge.get("campaign_qualified") is True
                and qualified_edge.get("archive_path")
                == edge_target(family, True).relative_to(ROOT).as_posix()
                and qualified_edge.get("proof_path")
                == edge_proof_target(family, True).relative_to(ROOT).as_posix()
                and original.valid_sha256(qualified_edge.get("archive_sha256"))
                and original.valid_sha256(qualified_edge.get("proof_sha256")),
                "a current deep worker lacks its genuine same-family passing V26 edge")
    return document


def _recorded_producer(wrapper: Mapping[str, Any]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(
        args=["durably-recorded-original-v26-worker"],
        returncode=wrapper.get("original_worker_returncode"),
        stdout=original.restore_complete_stream(
            wrapper.get("original_worker_stdout"), "complete actual original V26 worker stdout"
        ),
        stderr=original.restore_complete_stream(
            wrapper.get("original_worker_stderr"), "complete actual original V26 worker stderr"
        ),
    )


def authenticate_qualified_edge(
    family: str, state: Mapping[str, Any], contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    archive = edge_target(family, True)
    proof_path = edge_proof_target(family, True)
    raw = original.read_regular(archive, "complete unchanged actual passing V26 edge")
    report, edge, passed = state["v8"].validate_original_edge(
        raw, archive, family, state["snapshot"], contract
    )
    require(passed is True and edge.get("failed") == 0
            and edge.get("checks") == original.EDGE_CHECKS
            and edge.get("category_count") == original.EDGE_CATEGORIES,
            "the actual complete V26 edge failed the frozen 223198/49 correctness gate")
    proof_raw = original.read_regular(
        proof_path, "complete unchanged canonical passing same-family V26 owner proof"
    )
    proof = original.decode_json(proof_raw, "complete strict passing canonical V26 edge proof")
    require(normalize_publication_payload((proof, proof_raw)) == (proof_raw, proof),
            "the complete same-family passing V26 proof changed its canonical bytes")
    validate_durable_wrapper(
        proof, family, state, deep=False, passed=True, original_report=report,
        archive_path=archive, archive_sha256=hashlib.sha256(raw).hexdigest(),
        archive_bytes=len(raw), owner_before=proof.get("current_v23_native_owner_before"),
        owner_before_transcript=proof.get("current_v23_native_owner_before_process"),
        owner_after=proof.get("current_v23_native_owner_after"),
        owner_after_transcript=proof.get("current_v23_native_owner_after_process"),
        producer=_recorded_producer(proof),
        archive_receipt=proof.get("original_archive_publication_receipt"),
    )
    return edge, {
        "status": "PASS", "campaign_qualified": True,
        "archive_path": archive.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
    }, raw, proof_raw


def authenticate_qualified_deep(
    family: str, state: Mapping[str, Any], contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    edge, qualified_edge, _, _ = authenticate_qualified_edge(family, state, contract)
    archive = deep_target(family, True)
    proof_path = deep_proof_target(family, True)
    raw = original.read_regular(archive, "complete unchanged passing actual V26 deep report")
    report, passed = state["v8"].validate_deep(
        raw, family, edge, state["snapshot"], contract
    )
    require(passed is True and report.get("status") == "PASS"
            and report.get("checks") == original.DEEP_CHECKS
            and report.get("seeded_case_count") == original.DEEP_SEEDED_CASES
            and report.get("public_mismatch_count") == 0
            and report.get("candidate_sha256") == original.DEEP_REFERENCE_SHA256,
            "the actual V26 deep report failed the complete frozen 393/64 contract")
    proof_raw = original.read_regular(
        proof_path, "complete unchanged strict canonical same-family V26 deep proof"
    )
    proof = original.decode_json(proof_raw, "complete strict canonical passing V26 deep proof")
    require(normalize_publication_payload((proof, proof_raw)) == (proof_raw, proof),
            "the complete passing V26 deep proof changed its canonical bytes")
    validate_durable_wrapper(
        proof, family, state, deep=True, passed=True, original_report=report,
        archive_path=archive, archive_sha256=hashlib.sha256(raw).hexdigest(),
        archive_bytes=len(raw), owner_before=proof.get("current_v23_native_owner_before"),
        owner_before_transcript=proof.get("current_v23_native_owner_before_process"),
        owner_after=proof.get("current_v23_native_owner_after"),
        owner_after_transcript=proof.get("current_v23_native_owner_after_process"),
        producer=_recorded_producer(proof),
        archive_receipt=proof.get("original_archive_publication_receipt"),
        qualified_edge=qualified_edge,
    )
    return report, {
        "status": "PASS", "campaign_qualified": True,
        "archive_path": archive.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
        "qualified_edge": qualified_edge,
    }, raw, proof_raw


def _run_original(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    require(type(command) is list and all(type(value) is str for value in command)
            and len(command) >= 5
            and command[0] == str(original.PINNED_EXECUTABLE)
            and command[1:3] == ["-I", "-B"],
            "only a pinned isolated original CPython correctness worker may execute")
    result = subprocess.run(
        command, cwd=str(ROOT), env=historical.worker_environment(),
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=1800,
    )
    require(isinstance(result, subprocess.CompletedProcess) and result.args == command
            and type(result.returncode) is int
            and type(result.stdout) is bytes and type(result.stderr) is bytes
            and len(result.stdout) <= original.MAX_CHILD_OUTPUT_BYTES
            and len(result.stderr) <= original.MAX_CHILD_OUTPUT_BYTES,
            "the actual original V26 worker lost its complete exit, stdout, or stderr")
    return result


def captured_native_owner_records(
    family: str, owner_before: Mapping[str, Any] | None,
    owner_before_transcript: Mapping[str, Any] | None,
    owner_after: Mapping[str, Any] | None,
    owner_after_transcript: Mapping[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    checked_family(family)
    records: dict[str, dict[str, Any]] = {}
    for phase, owner, transcript in (
        ("before-original-worker", owner_before, owner_before_transcript),
        ("after-original-worker", owner_after, owner_after_transcript),
    ):
        require((owner is None) == (transcript is None),
                "a genuine completed native owner lost its actual process transcript")
        if owner is None:
            continue
        require(isinstance(owner, Mapping) and isinstance(transcript, Mapping)
                and owner.get("status") == "PASS"
                and owner.get("family") == family
                and owner.get("genuine_matching_executed") is True,
                "refusing to invent an actually completed V23 native owner: " + phase)
        records[phase] = {
            "owner": copy.deepcopy(dict(owner)),
            "process": copy.deepcopy(dict(transcript)),
        }
    return records


def _preserve_failure(
    family: str, state: Mapping[str, Any], *, deep: bool, error: BaseException,
    owner_before: Mapping[str, Any] | None,
    owner_before_transcript: Mapping[str, Any] | None,
    owner_after: Mapping[str, Any] | None,
    owner_after_transcript: Mapping[str, Any] | None,
    producer: subprocess.CompletedProcess[bytes] | None,
    completed_original: bytes | None, validated_original: bool | None,
    command: list[str] | None, publication: dict[str, Any],
) -> ProofV26Failure:
    metadata = checked_family(family)
    timed_out = isinstance(error, subprocess.TimeoutExpired)
    stdout = producer.stdout if producer is not None else getattr(error, "stdout", None)
    stderr = producer.stderr if producer is not None else getattr(error, "stderr", None)
    exit_code = producer.returncode if producer is not None else None
    invalidated_path: str | None = None
    invalidated_digest: str | None = None
    if completed_original is not None:
        require(type(completed_original) is bytes
                and 0 < len(completed_original) <= original.MAX_FILE_BYTES,
                "refusing to manufacture a complete actual V26 original observation")
        target = invalidated_target(family, deep=deep)
        invalidated_digest = publish_exclusive(
            publication, family, deep=deep, passed=publication["passed"],
            purpose="invalidated", path=target, payload=completed_original,
        )
        invalidated_path = target.relative_to(ROOT).as_posix()
    owners = captured_native_owner_records(
        family, owner_before, owner_before_transcript,
        owner_after, owner_after_transcript,
    )
    controller = state["controller"]
    pins = validated_pins(state["audits"]["pins"])
    document = {
        "schema": SCHEMA + "-original-producer-failure",
        "status": "FAIL", "result": "FAIL",
        "mode": "qualified-deep" if deep else "qualified-edge",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "actual_invoking_controller": "V26",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_refresh_protocol_path": controller["protocol_path"],
        "actual_refresh_protocol_sha256": controller["protocol_sha256"],
        "actual_failure_error_type": type(error).__name__,
        "actual_failure_error_message": str(error),
        "actual_publication_failure_stage":
            error.stage if isinstance(error, V26PublicationFailure) else None,
        "actual_publication_primary_failure":
            copy.deepcopy(error.actual_primary_failure)
            if isinstance(error, V26PublicationFailure) else None,
        "actual_publication_cleanup_failures":
            copy.deepcopy(error.actual_cleanup_failures)
            if isinstance(error, V26PublicationFailure) else [],
        "actual_child_exit_code": exit_code,
        "actual_child_signal":
            -exit_code if type(exit_code) is int and exit_code < 0 else None,
        "timed_out": timed_out,
        "timeout_seconds": 1800 if timed_out else None,
        "actual_original_worker_command": list(command) if command is not None else None,
        "actual_verified_parent_environment": dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment": historical.worker_environment(),
        "stdout": original.observed_stream(stdout, not timed_out),
        "stderr": original.observed_stream(stderr, not timed_out),
        "current_v23_native_owner_before":
            copy.deepcopy(dict(owner_before)) if owner_before is not None else None,
        "current_v23_native_owner_before_process":
            copy.deepcopy(dict(owner_before_transcript))
            if owner_before_transcript is not None else None,
        "current_v23_native_owner_after":
            copy.deepcopy(dict(owner_after)) if owner_after is not None else None,
        "current_v23_native_owner_after_process":
            copy.deepcopy(dict(owner_after_transcript))
            if owner_after_transcript is not None else None,
        "actually_completed_native_owner_records": copy.deepcopy(owners),
        "actually_completed_native_owner_record_count": len(owners),
        "full_current_family_source_sha256":
            dict(state["snapshot"]["source_sha256_by_path"]),
        "full_current_family_native_elf_sha256":
            dict(state["snapshot"]["native_sha256_by_path"]),
        "all_family_audited_provenance": audited_graph_provenance(state),
        "actual_v23_audit_source_path": V23_SOURCE_RELATIVE,
        "actual_v23_audit_source_sha256": pins["audit_source"],
        "actual_v23_protocol_path": V23_PROTOCOL_RELATIVE,
        "actual_v23_protocol_sha256": pins["audit_protocol"],
        "actual_v23_base_report_path": V23_BASE_REPORT_RELATIVE,
        "actual_v23_base_report_sha256": pins["base_report"],
        "actual_v23_base_receipt_path": state["v23"].BASE_RECEIPT_RELATIVE,
        "actual_v23_base_receipt_sha256": pins["base_receipt"],
        "actual_v23_strict_report_path": V23_STRICT_REPORT_RELATIVE,
        "actual_v23_strict_report_sha256": pins["strict_report"],
        "actual_v23_strict_receipt_path": state["v23"].STRICT_RECEIPT_RELATIVE,
        "actual_v23_strict_receipt_sha256": pins["strict_receipt"],
        "preserved_immutable_history": copy.deepcopy(state["history"]),
        "preserved_actual_failed_incidents": copy.deepcopy(state["preserved_incidents"]),
        "complete_original_observation_archive": completed_original is not None,
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_digest,
        "invalidated_complete_original_actual_status":
            None if completed_original is None else
            "NOT VALIDATED" if validated_original is None else
            "PASS" if validated_original else "FAIL",
        **failure_publication_fields(
            publication, family, deep=deep, original_raw=completed_original
        ),
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    canonical, exact = normalize_publication_payload(document)
    require(exact == document,
            "an actual V26 failure changed its complete canonical observed evidence")
    compressed = gzip.compress(canonical, compresslevel=9, mtime=0)
    decoded, restored = state["v8"].decode_archive(
        compressed, "complete actual canonical V26 owner or original-worker failure"
    )
    require(decoded == document and restored == canonical,
            "actual V26 failure evidence lost or invented completed observations")
    target = failure_target(family, deep=deep)
    digest = publish_exclusive(
        publication, family, deep=deep, passed=publication["passed"],
        purpose="failure", path=target, payload=compressed,
    )
    return ProofV26Failure(
        "a genuine current V23 native owner or original V26 correctness worker failed",
        {
            "schema": SCHEMA + "-actual-producer-failure-summary",
            "status": "FAIL", "result": "FAIL",
            "candidate_family": metadata["contract_name"],
            "candidate_module": metadata["module"],
            "failure_evidence_path": target.relative_to(ROOT).as_posix(),
            "failure_evidence_sha256": digest,
            "invalidated_complete_original_evidence_path": invalidated_path,
            "invalidated_complete_original_evidence_sha256": invalidated_digest,
            "actual_child_exit_code": exit_code,
            "actual_publication_primary_failure":
                copy.deepcopy(error.actual_primary_failure)
                if isinstance(error, V26PublicationFailure) else None,
            "actual_publication_cleanup_failures":
                copy.deepcopy(error.actual_cleanup_failures)
                if isinstance(error, V26PublicationFailure) else [],
            "actually_completed_native_owner_records": copy.deepcopy(owners),
            "actually_completed_native_owner_record_count": len(owners),
            **failure_publication_fields(
                publication, family, deep=deep, original_raw=completed_original
            ),
            "campaign_qualified": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        },
    )


def _publish_original_pair(
    family: str, state: Mapping[str, Any], *, deep: bool, passed: bool,
    report: Mapping[str, Any], raw: bytes,
    before: Mapping[str, Any], before_transcript: Mapping[str, Any],
    after: Mapping[str, Any], after_transcript: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes], contract: Any,
    publication: dict[str, Any], qualified_edge: Mapping[str, Any] | None = None,
    edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= original.MAX_FILE_BYTES,
            "an actual current original archive must preserve complete worker bytes")
    archive = deep_target(family, passed) if deep else edge_target(family, passed)
    proof = deep_proof_target(family, passed) if deep else edge_proof_target(family, passed)
    archive_digest = publish_exclusive(
        publication, family, deep=deep, passed=passed,
        purpose="archive", path=archive, payload=raw,
    )
    complete = original.read_regular(archive, "complete exclusively published V26 original")
    require(complete == raw and hashlib.sha256(complete).hexdigest() == archive_digest,
            "a complete original V26 archive changed before proof qualification")
    if deep:
        require(isinstance(edge, Mapping) and isinstance(qualified_edge, Mapping),
                "a deep correctness archive requires its actual qualified V26 edge")
        verified, result = state["v8"].validate_deep(
            complete, family, edge, state["snapshot"], contract
        )
    else:
        verified, _, result = state["v8"].validate_original_edge(
            complete, archive, family, state["snapshot"], contract
        )
    require(verified == report and result is passed,
            "a complete original V26 archive misrepresented its actual correctness")
    archived = publication["artifacts"]["archive"]
    wrapper = build_durable_wrapper(
        family, state, deep=deep, passed=passed, original_report=verified,
        archive_path=archive, archive_sha256=archive_digest,
        archive_bytes=len(raw), owner_before=before,
        owner_before_transcript=before_transcript,
        owner_after=after, owner_after_transcript=after_transcript,
        producer=producer, archive_receipt=archived, qualified_edge=qualified_edge,
    )
    validate_durable_wrapper(
        wrapper, family, state, deep=deep, passed=passed,
        original_report=verified, archive_path=archive,
        archive_sha256=archive_digest, archive_bytes=len(raw),
        owner_before=before, owner_before_transcript=before_transcript,
        owner_after=after, owner_after_transcript=after_transcript,
        producer=producer, archive_receipt=archived, qualified_edge=qualified_edge,
    )
    proof_raw, canonical = normalize_publication_payload(wrapper)
    require(canonical == wrapper, "the complete actual V26 owner proof lost canonical bytes")
    proof_digest = publish_exclusive(
        publication, family, deep=deep, passed=passed,
        purpose="proof", path=proof, payload=(wrapper, proof_raw),
    )
    saved = original.read_regular(proof, "complete normalized canonical actual V26 owner proof")
    decoded = original.decode_json(saved, "complete strict canonical durable V26 owner proof")
    require(normalize_publication_payload((decoded, saved)) == (proof_raw, wrapper)
            and hashlib.sha256(saved).hexdigest() == proof_digest
            and publication["artifacts"]["proof"]["canonical_document_expected"]
            and publication["artifacts"]["proof"]["canonical_document_validated"],
            "the complete current V26 proof failed its actual strict canonical reread")
    validate_durable_wrapper(
        decoded, family, state, deep=deep, passed=passed,
        original_report=verified, archive_path=archive,
        archive_sha256=archive_digest, archive_bytes=len(raw),
        owner_before=before, owner_before_transcript=before_transcript,
        owner_after=after, owner_after_transcript=after_transcript,
        producer=producer, archive_receipt=archived, qualified_edge=qualified_edge,
    )
    require(original.read_regular(archive, "complete unchanged final V26 original") == raw,
            "a durable owner proof cannot certify a subsequently changed original")
    validate_publication_receipt(
        publication, family, deep=deep, passed=passed, original_raw=raw
    )
    pins = validated_pins(state["audits"]["pins"])
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
        "actual_v23_audit_source_sha256": pins["audit_source"],
        "actual_v23_protocol_sha256": pins["audit_protocol"],
        "actual_v23_base_report_sha256": pins["base_report"],
        "actual_v23_base_receipt_sha256": pins["base_receipt"],
        "actual_v23_strict_report_sha256": pins["strict_report"],
        "actual_v23_strict_receipt_sha256": pins["strict_receipt"],
        "canonical_document_bytes_normalized": True,
        "stdout_is_not_durable_proof": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def _recheck_state(family: str, pins: Mapping[str, str], state: Mapping[str, Any]) -> None:
    fresh = preflight(family, pins)
    require(fresh["snapshot"] == state["snapshot"]
            and fresh["audits"]["pins"] == state["audits"]["pins"]
            and fresh["audits"]["graph"] == state["audits"]["graph"]
            and fresh["audits"]["base"] == state["audits"]["base"]
            and fresh["audits"]["strict"] == state["audits"]["strict"]
            and fresh["audits"]["base_receipt"] == state["audits"]["base_receipt"]
            and fresh["audits"]["strict_receipt"] == state["audits"]["strict_receipt"]
            and fresh["history"] == state["history"]
            and fresh["preserved_incidents"] == state["preserved_incidents"],
            "the actual V23 reports, native graph, publication receipts, or history changed")


def refresh_edge(family: str, supplied: Mapping[str, Any]) -> dict[str, Any]:
    state = preflight(family, supplied)
    preflight_fresh_destinations(family, deep=False)
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    before: dict[str, Any] | None = None
    before_transcript: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    after_transcript: dict[str, Any] | None = None
    process: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    receipt = new_publication_receipt(family, deep=False)
    try:
        before, before_transcript = observe_owner(
            family, state, stage="before-original-edge"
        )
        _read_only_v23_graph(state["v23"], state["audits"]["graph"])
        with tempfile.TemporaryDirectory(
            prefix="rebar-v26-original-edge-" + family + "-", dir="/tmp"
        ) as directory:
            private = Path(directory).resolve()
            require(private.parent == Path("/tmp").resolve(),
                    "the original V26 edge escaped its actual isolated temporary root")
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
                    "the original V26 edge worker produced no complete genuine archive")
            raw = original.read_regular(temporary, "complete private original V26 edge")
            report, _, passed = state["v8"].validate_original_edge(
                raw, temporary, family, state["snapshot"], contract
            )
            require(process.returncode == int(not passed),
                    "the original V26 edge concealed its actual complete exit")
            after, after_transcript = observe_owner(
                family, state, stage="after-original-edge"
            )
            _read_only_v23_graph(state["v23"], state["audits"]["graph"])
            _recheck_state(family, validated_pins(supplied), state)
            return _publish_original_pair(
                family, state, deep=False, passed=passed, report=report,
                raw=raw, before=before, before_transcript=before_transcript,
                after=after, after_transcript=after_transcript,
                producer=process, contract=contract, publication=receipt,
            )
    except ProofV26Failure:
        raise
    except (AssertionError, OSError, ValueError, TypeError, KeyError,
            UnicodeError, subprocess.TimeoutExpired) as error:
        raise _preserve_failure(
            family, state, deep=False, error=error,
            owner_before=before, owner_before_transcript=before_transcript,
            owner_after=after, owner_after_transcript=after_transcript,
            producer=process, completed_original=raw,
            validated_original=passed, command=command, publication=receipt,
        ) from error


def refresh_deep(family: str, supplied: Mapping[str, Any]) -> dict[str, Any]:
    state = preflight(family, supplied)
    preflight_fresh_destinations(family, deep=True)
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    edge, qualified_edge, edge_raw, edge_proof_raw = authenticate_qualified_edge(
        family, state, contract
    )
    before: dict[str, Any] | None = None
    before_transcript: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    after_transcript: dict[str, Any] | None = None
    process: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    receipt = new_publication_receipt(family, deep=True)
    try:
        before, before_transcript = observe_owner(
            family, state, stage="before-original-deep"
        )
        _read_only_v23_graph(state["v23"], state["audits"]["graph"])
        with tempfile.TemporaryDirectory(
            prefix="rebar-v26-original-deep-" + family + "-", dir="/tmp"
        ) as directory:
            private = Path(directory).resolve()
            require(private.parent == Path("/tmp").resolve(),
                    "the original V26 deep escaped its exact isolated temporary root")
            temporary = private / (
                "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
                + "-POSTFINAL-CURRENT-BUILD-V26-PRIVATE.json.gz"
            )
            command = [
                str(original.PINNED_EXECUTABLE), "-I", "-B", "-c",
                original.DEEP_LAUNCHER, str(ROOT), metadata["module"],
                str(edge_target(family, True)), str(temporary), str(private),
            ]
            process = _run_original(command)
            require(temporary.is_file() and not temporary.is_symlink(),
                    "the original V26 deep worker produced no complete actual archive")
            raw = original.read_regular(temporary, "complete private original V26 deep")
            report, passed = state["v8"].validate_deep(
                raw, family, edge, state["snapshot"], contract
            )
            require(process.returncode == int(not passed),
                    "the original V26 deep concealed its genuine complete exit")
            after, after_transcript = observe_owner(
                family, state, stage="after-original-deep"
            )
            _read_only_v23_graph(state["v23"], state["audits"]["graph"])
            _recheck_state(family, validated_pins(supplied), state)
            require(original.read_regular(
                edge_target(family, True), "complete unchanged actual V26 qualifying edge"
            ) == edge_raw and original.read_regular(
                edge_proof_target(family, True),
                "complete unchanged canonical actual V26 qualifying edge proof",
            ) == edge_proof_raw,
                    "the qualifying same-family V26 edge changed during the deep worker")
            return _publish_original_pair(
                family, state, deep=True, passed=passed, report=report,
                raw=raw, before=before, before_transcript=before_transcript,
                after=after, after_transcript=after_transcript,
                producer=process, contract=contract, publication=receipt,
                qualified_edge=qualified_edge, edge=edge,
            )
    except ProofV26Failure:
        raise
    except (AssertionError, OSError, ValueError, TypeError, KeyError,
            UnicodeError, subprocess.TimeoutExpired) as error:
        raise _preserve_failure(
            family, state, deep=True, error=error,
            owner_before=before, owner_before_transcript=before_transcript,
            owner_after=after, owner_after_transcript=after_transcript,
            producer=process, completed_original=raw,
            validated_original=passed, command=command, publication=receipt,
        ) from error


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (AssertionError, OSError, ValueError, TypeError, KeyError,
            UnicodeError, OverflowError):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def _poison(value: Any) -> Any:
    return historical._poison(value)


class SyntheticPublicationOps(historical.SyntheticPublicationOps):
    """Keep all injected publication and cleanup effects entirely in memory."""

    def __init__(
        self, *, fail_purpose: str | None = None,
        fail_stage: str | None = None, partial_bytes: int = 1,
        cleanup_fail_stages: tuple[str, ...] = (),
    ) -> None:
        super().__init__(
            fail_purpose=fail_purpose, fail_stage=fail_stage,
            partial_bytes=partial_bytes,
        )
        require(type(cleanup_fail_stages) is tuple
                and len(set(cleanup_fail_stages)) == len(cleanup_fail_stages)
                and set(cleanup_fail_stages)
                <= {"file-close", "directory-close"},
                "synthetic cleanup requires exact independent descriptor roles")
        self.cleanup_fail_stages = cleanup_fail_stages

    def close(self, descriptor: int, *, directory: bool) -> None:
        role = "directory-close" if directory else "file-close"
        if (self.current_purpose == self.fail_purpose
                and role in self.cleanup_fail_stages):
            require(descriptor == (
                self.directory_fd if directory else self.file_fd
            ), "synthetic cleanup cannot invent or retry a descriptor")
            raise OSError("source-only genuine " + role + " cleanup failed")
        super().close(descriptor, directory=directory)


def _synthetic_publication(
    family: str, *, deep: bool, passed: bool, partial: bool,
) -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    receipt = new_publication_receipt(family, deep=deep)
    operations = SyntheticPublicationOps(
        fail_purpose="archive" if partial else None,
        fail_stage="partial-success" if partial else None,
        partial_bytes=1,
    )
    archive = original.canonical({
        "source_only": True, "family": family, "deep": deep, "passed": passed
    })
    archive_path = deep_target(family, passed) if deep else edge_target(family, passed)
    publish_exclusive(
        receipt, family, deep=deep, passed=passed, purpose="archive",
        path=archive_path, payload=archive, operations=operations,
    )
    proof = {
        "schema": SCHEMA + "-synthetic-source-only-never-qualifies",
        "family": family, "deep": deep, "passed": passed,
        "synthetic": True, "campaign_qualified": False,
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
    }
    proof_path = deep_proof_target(family, passed) if deep else edge_proof_target(
        family, passed
    )
    publish_exclusive(
        receipt, family, deep=deep, passed=passed, purpose="proof",
        path=proof_path, payload=proof, operations=operations,
    )
    return receipt, archive, proof


def _check_fault_receipt(
    family: str, *, deep: bool, passed: bool, purpose: str, stage: str,
    cleanup_fail_stages: tuple[str, ...] = (),
) -> bool:
    receipt = new_publication_receipt(family, deep=deep)
    operations = SyntheticPublicationOps(
        fail_purpose=purpose, fail_stage=stage, partial_bytes=1,
        cleanup_fail_stages=cleanup_fail_stages,
    )
    payload = original.canonical({
        "source_only": True, "family": family,
        "deep": deep, "purpose": purpose, "passed": passed,
    })
    if purpose == "proof":
        archive_path = expected_publication_target(
            family, deep=deep, passed=passed, purpose="archive"
        )
        publish_exclusive(
            receipt, family, deep=deep, passed=passed,
            purpose="archive", path=archive_path,
            payload=b"source-only-V26-original", operations=operations,
        )
    target = expected_publication_target(
        family, deep=deep,
        passed=passed if purpose in ("archive", "proof") else None,
        purpose=purpose,
    )
    try:
        publish_exclusive(
            receipt, family, deep=deep,
            passed=passed if purpose in ("archive", "proof") else None,
            purpose=purpose, path=target,
            payload=(original.decode_json(payload, "source-only strict V26 proof"), payload)
            if purpose == "proof" else payload,
            operations=operations,
        )
    except V26PublicationFailure as failure:
        require(failure.stage in {
            "target-validation", "directory-open", "directory-identity",
            "exclusive-create", "write", "file-fsync", "file-close",
            "directory-fsync", "directory-close", "readback", "canonical-readback",
            "file-cleanup-close", "directory-cleanup-close",
        }, "a synthetic V26 failure invented its actual first publication stage")
        require(failure.actual_primary_failure == {
            "stage": failure.stage,
            "actual_error_type": type(failure.cause).__name__,
            "actual_error_message": str(failure.cause),
        }, "a synthetic V26 failure changed its genuine first primary error")
        if cleanup_fail_stages:
            require(failure.stage == stage
                    and [row["stage"] for row in failure.actual_cleanup_failures]
                    == [role.removesuffix("-close") + "-cleanup-close"
                        for role in cleanup_fail_stages]
                    and all(type(row) is dict
                            and set(row) == {
                                "stage", "actual_error_type", "actual_error_message"
                            }
                            and row["actual_error_type"] == "OSError"
                            for row in failure.actual_cleanup_failures),
                    "a genuine V26 primary failure lost ordered descriptor cleanup errors")
        validate_publication_receipt(failure.receipt, family, deep=deep)
        return not failure.receipt["artifacts"][purpose]["validated"]
    return False


def _reject_raw_owner_proof_without_effects(
    family: str, *, deep: bool, passed: bool, payload: Any,
) -> bool:
    receipt = new_publication_receipt(family, deep=deep)
    operations = SyntheticPublicationOps()
    archive_path = expected_publication_target(
        family, deep=deep, passed=passed, purpose="archive"
    )
    archive = original.canonical({
        "source_only": True, "family": family,
        "deep": deep, "passed": passed,
    })
    publish_exclusive(
        receipt, family, deep=deep, passed=passed, purpose="archive",
        path=archive_path, payload=archive, operations=operations,
    )
    before = copy.deepcopy(receipt)
    before_files = {path: bytes(raw) for path, raw in operations.files.items()}
    proof_path = expected_publication_target(
        family, deep=deep, passed=passed, purpose="proof"
    )
    try:
        publish_exclusive(
            receipt, family, deep=deep, passed=passed,
            purpose="proof", path=proof_path,
            payload=payload, operations=operations,
        )
    except (AssertionError, OSError, ValueError, TypeError, KeyError,
            UnicodeError, OverflowError):
        return (
            receipt == before
            and {path: bytes(raw) for path, raw in operations.files.items()}
            == before_files
            and receipt["artifacts"]["proof"] == _empty_artifact("proof")
            and proof_path.relative_to(ROOT).as_posix() not in operations.files
        )
    return False


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime_source_only()
    inherited = historical.candidate_free_self_test()
    require(inherited.get("status") == "PASS"
            and inherited.get("candidate_imports") == 0
            and inherited.get("subprocesses") == 0
            and inherited.get("file_writes") == 0
            and inherited.get("clock_samples") == 0
            and inherited.get("historical_evidence_reads") == 0
            and inherited.get("actual_audit_report_reads") == 0
            and inherited.get("holdout_reads") == 0
            and inherited.get("synthetic_results_qualify_candidates") is False
            and type(inherited.get("check_count")) is int
            and inherited["check_count"] == 8330
            and type(inherited.get("checks")) is list
            and len(inherited["checks"]) == inherited["check_count"],
            "the 8,330 independently reviewed candidate-free V24 controls weakened")
    source = original.read_regular(ROOT / SOURCE_RELATIVE,
                                   "complete candidate-free V26 controller source")
    protocol = original.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    v23_source = original.authenticate_frozen(V23_SOURCE_RELATIVE, V23_SOURCE_SHA256)
    v23_protocol = original.authenticate_frozen(V23_PROTOCOL_RELATIVE, V23_PROTOCOL_SHA256)
    frozen_v22_source = original.authenticate_frozen(
        historical.V22_SOURCE_RELATIVE, V22_SOURCE_SHA256
    )
    frozen_v22_protocol = original.authenticate_frozen(
        historical.V22_PROTOCOL_RELATIVE, V22_PROTOCOL_SHA256
    )
    tree = ast.parse(source.decode("utf-8"), filename=SOURCE_RELATIVE)
    source_digest = hashlib.sha256(source).hexdigest()
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        checks.append({"name": "v26:" + name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        checks.append(rejected("v26:" + name, action))

    class SourceOnlyV23Canonical:
        """Model the frozen producer dialect without importing a live owner."""

        @staticmethod
        def canonical(document: Mapping[str, Any]) -> bytes:
            require(isinstance(document, Mapping),
                    "source-only V23 canonicalization requires one complete document")
            return (
                json.dumps(
                    dict(document), ensure_ascii=True, allow_nan=False,
                    sort_keys=True, separators=(",", ":"),
                ) + "\n"
            ).encode("ascii")

    fresh_pins = {
        "audit_source": V23_SOURCE_SHA256,
        "audit_protocol": V23_PROTOCOL_SHA256,
        "base_report": original.synthetic_digest("source-only-v26-fresh-v23-base-report"),
        "base_receipt": original.synthetic_digest("source-only-v26-fresh-v23-base-receipt"),
        "strict_report": original.synthetic_digest("source-only-v26-fresh-v23-strict-report"),
        "strict_receipt": original.synthetic_digest("source-only-v26-fresh-v23-strict-receipt"),
    }
    with original.source_only_boundary() as effects:
        accept("parse-complete-additive-current-controller", isinstance(tree, ast.Module))
        accept("bind-exact-independently-frozen-v26-protocol",
               hashlib.sha256(protocol).hexdigest() == PROTOCOL_SHA256)
        accept("bind-exact-independent-current-v23-source",
               hashlib.sha256(v23_source).hexdigest() == V23_SOURCE_SHA256)
        accept("bind-exact-independent-current-v23-protocol",
               hashlib.sha256(v23_protocol).hexdigest() == V23_PROTOCOL_SHA256)
        accept("preserve-exact-failed-v22-source-without-reading-evidence",
               hashlib.sha256(frozen_v22_source).hexdigest() == V22_SOURCE_SHA256)
        accept("preserve-exact-failed-v22-protocol-without-reading-evidence",
               hashlib.sha256(frozen_v22_protocol).hexdigest() == V22_PROTOCOL_SHA256)
        accept("preserve-all-8330-prior-candidate-free-controls",
               inherited["check_count"] == 8330)
        accept("preserve-original-complete-223198-edge-checks-in-49-categories",
               original.EDGE_CHECKS == 223198 and original.EDGE_CATEGORIES == 49)
        accept("preserve-original-complete-393-deep-checks-and-64-seeds",
               original.DEEP_CHECKS == 393 and original.DEEP_SEEDED_CASES == 64)
        accept("preserve-three-independent-twelve-source-five-native-families",
               FAMILIES == ("rust", "vm", "zig")
               and sum(len(original.FAMILIES[x]["sources"]) for x in FAMILIES) == 12
               and sum(len(original.FAMILIES[x]["native"]) for x in FAMILIES) == 5)
        accept("own-exactly-18-distinct-receipt-fields-and-one-write-ledger",
               len(RECEIPT_FIELDS) == len(set(RECEIPT_FIELDS)) == 18
               and RECEIPT_FIELDS.count("actual_write_calls") == 1
               and RECEIPT_FIELDS == tuple(historical.RECEIPT_FIELDS))
        accept("accept-only-six-distinct-fresh-v23-runtime-pins",
               validated_pins(fresh_pins) == fresh_pins)
        for key in PIN_NAMES:
            missing = dict(fresh_pins)
            del missing[key]
            reject("reject-each-missing-current-v23-report-or-receipt-pin:" + key,
                   lambda item=missing: validated_pins(item))
            replay = dict(fresh_pins)
            replay[key] = fresh_pins["audit_source"]
            if key != "audit_source":
                reject("reject-each-replayed-current-v23-report-or-receipt-pin:" + key,
                       lambda item=replay: validated_pins(item))
        for index, first in enumerate(PIN_NAMES):
            for second in PIN_NAMES[index + 1:]:
                swapped = dict(fresh_pins)
                swapped[first], swapped[second] = swapped[second], swapped[first]
                reject("reject-swapped-source-report-or-receipt-pins:"
                       + first + ":" + second,
                       lambda item=swapped: require(
                           validated_pins(item) == fresh_pins,
                           "a genuine current V23 artifact changed its pinned role",
                       ))
        expected_root = _expected_v23_root_integration()
        compact_root = SourceOnlyV23Canonical.canonical(expected_root)
        pretty_root = original.canonical(expected_root)
        accept("recover-exact-real-root-sha-without-reading-real-historical-evidence",
               hashlib.sha256(compact_root).hexdigest() == V23_ROOT_INTEGRATION_SHA256)
        accept("distinguish-generating-v23-compact-dialect-from-inherited-pretty-dialect",
               compact_root != pretty_root)
        accept("accept-exact-generating-v23-root-bytes-without-importing-v23",
               _validate_v23_producer_bytes(
                   SourceOnlyV23Canonical, expected_root, compact_root,
                   "source-only frozen V23 root integration",
               ) == compact_root)
        for role, document in (
            ("root-integration", expected_root),
            ("base-report", {"schema": "source-only-v23-base-report", "role": "base"}),
            ("base-receipt", {"schema": "source-only-v23-base-receipt", "role": "base"}),
            ("strict-report", {"schema": "source-only-v23-strict-report", "role": "strict"}),
            ("strict-receipt", {"schema": "source-only-v23-strict-receipt", "role": "strict"}),
        ):
            compact = SourceOnlyV23Canonical.canonical(document)
            accept("accept-only-exact-generating-v23-canonical-bytes:" + role,
                   _validate_v23_producer_bytes(
                       SourceOnlyV23Canonical, document, compact,
                       "source-only genuine V23 " + role,
                   ) == compact)
            for suffix, forged in (
                ("inherited-pretty-v11", original.canonical(document)),
                ("missing-required-newline", compact[:-1]),
                ("double-newline", compact + b"\n"),
                ("trailing-space", compact + b" "),
                ("trailing-carriage-return", compact + b"\r"),
                ("trailing-nul", compact + b"\x00"),
            ):
                reject("reject-wrong-generating-v23-canonical-dialect:"
                       + role + ":" + suffix,
                       lambda raw=forged, item=document, name=role:
                           _validate_v23_producer_bytes(
                               SourceOnlyV23Canonical, item, raw,
                               "source-only genuine V23 " + name,
                           ))
        accept("validate-all-43-genuine-root-integration-fields-without-reading-evidence",
               len(expected_root) == 43
               and _validate_v23_root_integration(expected_root) == expected_root)
        for key, value in expected_root.items():
            forged = copy.deepcopy(expected_root)
            forged[key] = _poison(value)
            reject("reject-each-forged-frozen-v23-read-only-integration-field:" + key,
                   lambda item=forged: _validate_v23_root_integration(item))
        for index, event in enumerate(expected_root["actual_read_only_descriptor_events"]):
            for field in event:
                forged = copy.deepcopy(expected_root)
                forged["actual_read_only_descriptor_events"][index][field] = (
                    _poison(event[field])
                )
                reject("reject-forged-read-only-owner-descriptor-event:"
                       + str(index) + ":" + field,
                       lambda item=forged: _validate_v23_root_integration(item))
        for key, value in expected_root["read_only_boundary_effects"].items():
            forged = copy.deepcopy(expected_root)
            forged["read_only_boundary_effects"][key] = _poison(value)
            reject("reject-forged-read-only-zero-effect:" + key,
                   lambda item=forged: _validate_v23_root_integration(item))
        accept("retain-four-different-genuine-historical-v21-pins",
               set(HISTORICAL_V21_PINS) == set(HISTORICAL_PIN_NAMES)
               and len(set(HISTORICAL_V21_PINS.values())) == 4
               and all(original.valid_sha256(x) for x in HISTORICAL_V21_PINS.values()))
        reject("reject-historical-v21-pins-as-current-v23-ownership",
               lambda: validated_pins(HISTORICAL_V21_PINS))
        for key in PIN_NAMES:
            forged = dict(fresh_pins)
            forged[key] = _poison(forged[key])
            reject("reject-each-forged-current-v23-runtime-pin:" + key,
                   lambda item=forged: validated_pins(item))
        for historical_role in (
            "base_report", "base_receipt", "strict_report", "strict_receipt"
        ):
            for old_digest in HISTORICAL_V21_PINS.values():
                forged = dict(fresh_pins)
                forged[historical_role] = old_digest
                reject("reject-historical-report-as-fresh-v23:"
                       + historical_role + ":" + old_digest[:12],
                       lambda item=forged: validated_pins(item))
        expected_v22 = historical.expected_v22_failure_document(HISTORICAL_V21_PINS)
        summary_v22 = historical.validate_v22_failure_document(
            expected_v22, HISTORICAL_V21_PINS
        )
        accept("preserve-exact-25-field-v22-historical-failure-synthetically",
               len(expected_v22) == 25 and len(summary_v22) == 27)
        accept("never-invent-the-failed-v22-invocation-boundary",
               expected_v22.get("actual_failed_invocation_boundary_counters")
               == LOST_FAILED_BOUNDARY)
        accept("preserve-genuine-25-source-lines-and-24-combined-traceback-lines",
               len(expected_v22.get("actual_invocation", {}).get(
                   "actual_inline_python_source_lines", []
               )) == 25
               and len(expected_v22.get("actual_combined_traceback_lines", [])) == 24)
        reject("never-authenticate-old-v22-failure-with-fresh-v23-pins",
               lambda: historical.expected_v22_failure_document(fresh_pins))
        reject("never-validate-old-v22-failure-with-fresh-v23-pins",
               lambda: historical.validate_v22_failure_document(expected_v22, fresh_pins))
        for version, expected, count in (
            ("v13", historical.expected_v13_failure_summary(), 26),
            ("v15", historical.expected_v15_failure_summary(), 28),
            ("v17", historical.expected_v17_failure_summary(), 18),
            ("v19", historical.expected_v19_failure_summary(), 36),
        ):
            accept("preserve-complete-actual-" + version + "-historical-field-count",
                   type(expected) is dict and len(expected) == count)
        accept("preserve-actual-historical-v13-first-failed-stage",
               historical.expected_v13_failure_summary().get("failed_stage")
               == TRUE_V13_FAILURE_STAGE)
        declarations = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))
        }
        for role in (
            "validated_pins", "authenticate_controller", "_authenticate_v23_reports",
            "_validate_v23_producer_bytes",
            "_expected_v23_root_integration", "_validate_v23_root_integration",
            "_authenticate_v23_root_integration",
            "_authenticate_historical_v22_failure", "_validate_historical_incidents",
            "_read_only_v23_graph", "preflight", "observe_owner",
            "normalize_publication_payload", "_validate_actual_write_calls",
            "new_publication_receipt", "validate_publication_receipt",
            "PublicationOps", "SyntheticPublicationOps", "publish_exclusive",
            "build_durable_wrapper",
            "validate_durable_wrapper", "authenticate_qualified_edge",
            "authenticate_qualified_deep", "_preserve_failure",
            "refresh_edge", "refresh_deep", "candidate_free_self_test",
        ):
            accept("retain-independently-owned-current-proof-role:" + role,
                   role in declarations)
        publisher = declarations.get("publish_exclusive")
        publisher_calls = [
            node for node in ast.walk(publisher)
            if isinstance(node, ast.Call)
        ] if isinstance(publisher, ast.FunctionDef) else []
        accept("own-real-v26-publisher-without-calling-any-prior-publisher",
               isinstance(publisher, ast.FunctionDef)
               and not any(isinstance(node.func, ast.Attribute)
                           and node.func.attr == "publish_exclusive"
                           for node in publisher_calls))
        publish_source = ast.get_source_segment(source.decode("utf-8"), publisher) \
            if isinstance(publisher, ast.FunctionDef) else ""
        accept("record-pending-actual-write-before-attempting-syscall",
               bool(publish_source)
               and publish_source.find('row["actual_write_calls"].append(attempt)')
               < publish_source.find("returned = ops.write("))
        accept("source-only-never-imports-live-v23-owner",
               "tools.postfinal_independent_engine_audit_v23" not in sys.modules)
        for invalid in (None, True, False, 0, 1, "{}", [], (), ({},), b"",
                        ({"ok": True}, b"{}"), {1: "not-a-string-key"}):
            reject("reject-noncanonical-publication:" + repr(invalid),
                   lambda value=invalid: normalize_publication_payload(value))
        canonical_document = {"source_only": True, "qualifies": False, "version": 26}
        canonical_raw = original.canonical(canonical_document)
        accept("accept-complete-strict-canonical-object-and-exact-bytes",
               normalize_publication_payload((canonical_document, canonical_raw))
               == (canonical_raw, canonical_document))
        for family in FAMILIES:
            for deep in (False, True):
                label = family + ":" + ("deep" if deep else "edge")
                empty = new_publication_receipt(family, deep=deep)
                accept("validate-four-independent-empty-artifact-receipts:" + label,
                       validate_publication_receipt(empty, family, deep=deep) == empty)
                accept("never-alias-empty-artifact-write-ledgers:" + label,
                       len({id(empty["artifacts"][p]["actual_write_calls"])
                            for p in PURPOSES}) == len(PURPOSES))
                for purpose in PURPOSES:
                    for field in RECEIPT_FIELDS:
                        forged = copy.deepcopy(empty)
                        forged["artifacts"][purpose][field] = _poison(
                            forged["artifacts"][purpose][field]
                        )
                        reject("reject-forged-empty-18-field-receipt:"
                               + label + ":" + purpose + ":" + field,
                               lambda item=forged, chosen=family, isdeep=deep:
                                   validate_publication_receipt(
                                       item, chosen, deep=isdeep
                                   ))
                forged_alias = copy.deepcopy(empty)
                forged_alias["artifacts"]["proof"]["actual_write_calls"] = (
                    forged_alias["artifacts"]["archive"]["actual_write_calls"]
                )
                reject("reject-shared-actual-write-ledger:" + label,
                       lambda item=forged_alias, chosen=family, isdeep=deep:
                           validate_publication_receipt(item, chosen, deep=isdeep))
                for passed in (False, True):
                    result_label = label + ":" + ("pass" if passed else "fail")
                    for payload_name, payload in (
                        ("non-json-bytes", b"not-json"),
                        ("raw-canonical-json-bytes", original.canonical({"ok": True})),
                        ("raw-noncanonical-json-bytes", b'{ "ok" : true }'),
                        ("noncanonical-object-and-bytes", ({"ok": True}, b"{}")),
                    ):
                        accept("reject-raw-owner-proof-before-any-open-or-write:"
                               + result_label + ":" + payload_name,
                               _reject_raw_owner_proof_without_effects(
                                   family, deep=deep, passed=passed, payload=payload,
                               ))
                    for partial in (False, True):
                        receipt, archive, proof = _synthetic_publication(
                            family, deep=deep, passed=passed, partial=partial
                        )
                        accept("validate-complete-in-memory-publication:"
                               + result_label + (":partial" if partial else ":whole"),
                               validate_publication_receipt(
                                   receipt, family, deep=deep,
                                   passed=passed, original_raw=archive,
                               ) == receipt
                               and proof["campaign_qualified"] is False
                               and receipt["artifacts"]["proof"]["validated"] is True
                               and (not partial
                                    or len(receipt["artifacts"]["archive"]
                                           ["actual_write_calls"]) > 1))
                        for purpose in PURPOSES:
                            for field in RECEIPT_FIELDS:
                                forged = copy.deepcopy(receipt)
                                forged["artifacts"][purpose][field] = _poison(
                                    forged["artifacts"][purpose][field]
                                )
                                reject("reject-forged-complete-18-field-receipt:"
                                       + result_label
                                       + (":partial:" if partial else ":whole:")
                                       + purpose + ":" + field,
                                       lambda item=forged, chosen=family,
                                           isdeep=deep, outcome=passed, raw=archive:
                                               validate_publication_receipt(
                                                   item, chosen, deep=isdeep,
                                                   passed=outcome, original_raw=raw,
                                               ))
                        for purpose in ("archive", "proof"):
                            calls = receipt["artifacts"][purpose]["actual_write_calls"]
                            for index, call in enumerate(calls):
                                for field in ("requested_bytes", "returned_bytes"):
                                    forged = copy.deepcopy(receipt)
                                    forged["artifacts"][purpose]["actual_write_calls"] \
                                        [index][field] = _poison(call[field])
                                    reject("reject-forged-ordered-write-call:"
                                           + result_label
                                           + (":partial:" if partial else ":whole:")
                                           + purpose + ":" + str(index) + ":" + field,
                                           lambda item=forged, chosen=family,
                                               isdeep=deep, outcome=passed,
                                               raw=archive:
                                                   validate_publication_receipt(
                                                       item, chosen, deep=isdeep,
                                                       passed=outcome,
                                                       original_raw=raw,
                                                   ))
                    for purpose in PURPOSES:
                        for stage in (
                            "target-validation", "directory-open", "directory-identity",
                            "exclusive-create", "write", "zero-write", "negative-write",
                            "boolean-write", "excess-write", "partial-write",
                            "file-fsync", "file-close", "directory-fsync",
                            "directory-close", "readback",
                        ):
                            accept("reject-actual-first-publication-fault:"
                                   + result_label + ":" + purpose + ":" + stage,
                                   _check_fault_receipt(
                                       family, deep=deep, passed=passed,
                                       purpose=purpose, stage=stage,
                                   ))
                        for cleanup_stages in (
                            ("file-close",),
                            ("directory-close",),
                            ("file-close", "directory-close"),
                        ):
                            accept("preserve-first-write-error-and-every-cleanup-error:"
                                   + result_label + ":" + purpose + ":"
                                   + "+".join(cleanup_stages),
                                   _check_fault_receipt(
                                       family, deep=deep, passed=passed,
                                       purpose=purpose, stage="write",
                                       cleanup_fail_stages=cleanup_stages,
                                   ))
    require(isinstance(effects, Mapping)
            and all(type(value) is int and value == 0 for value in effects.values()),
            "source-only V26 controls accessed a candidate, report, worker, clock, or holdout")
    prior_checks = copy.deepcopy(inherited["checks"])
    all_checks = prior_checks + checks
    names = [row.get("name") for row in all_checks]
    failed = [row for row in all_checks if row.get("passed") is not True]
    require(len(names) == len(set(names)) and not failed,
            "a candidate-free inherited or independent V26 control failed or duplicated: "
            + json.dumps({
                "failed": [row.get("name") for row in failed[:12]],
                "duplicate_names": len(names) - len(set(names)),
            }, ensure_ascii=True, sort_keys=True))
    verify_runtime_source_only()
    return {
        "schema": SCHEMA + "-candidate-free-self-test",
        "status": "PASS", "result": "PASS",
        "check_count": len(all_checks),
        "checks": all_checks,
        "inherited_v24_check_count": inherited["check_count"],
        "independent_v26_check_count": len(checks),
        "candidate_imports": 0,
        "subprocesses": 0,
        "native_workers_started": 0,
        "original_edge_workers_started": 0,
        "original_deep_workers_started": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "historical_evidence_reads": 0,
        "actual_audit_report_reads": 0,
        "holdout_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "actual_v26_controller_sha256": source_digest,
        "actual_v26_protocol_sha256": PROTOCOL_SHA256,
        "actual_current_v23_audit_source_sha256": V23_SOURCE_SHA256,
        "actual_current_v23_protocol_sha256": V23_PROTOCOL_SHA256,
        "future_v23_base_report_hash_guessed": False,
        "future_v23_base_receipt_hash_guessed": False,
        "future_v23_strict_report_hash_guessed": False,
        "future_v23_strict_receipt_hash_guessed": False,
        "historical_v21_qualifies_current_engine": False,
        "immutable_failed_v22_controller_sha256": V22_SOURCE_SHA256,
        "immutable_failed_v22_protocol_sha256": V22_PROTOCOL_SHA256,
        "immutable_failed_v22_incident_sha256": V22_FAILURE_SHA256,
        "immutable_failed_v22_qualifies_current_engine": False,
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
        "original_edge_checks": original.EDGE_CHECKS,
        "original_edge_categories": original.EDGE_CATEGORIES,
        "original_deep_checks": original.DEEP_CHECKS,
        "original_deep_seeded_cases": original.DEEP_SEEDED_CASES,
        "independent_family_count": len(FAMILIES),
        "complete_owned_source_count": 12,
        "complete_native_elf_count": 5,
        "owned_v26_receipt_field_count": len(RECEIPT_FIELDS),
        "actual_per_write_syscall_ledger_required": True,
        "blocked_effect_attempts": dict(effects),
        "v23_root_read_only_integration_qualifies_candidates": False,
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
        "--module", choices=tuple(row["module"] for row in original.FAMILIES.values())
    )
    parser.add_argument("--v23-audit-source-sha256")
    parser.add_argument("--v23-audit-protocol-sha256")
    parser.add_argument("--v23-base-report-sha256")
    parser.add_argument("--v23-base-receipt-sha256")
    parser.add_argument("--v23-strict-report-sha256")
    parser.add_argument("--v23-strict-receipt-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(options.module is None and all(
            getattr(options, key) is None for key in (
                "v23_audit_source_sha256", "v23_audit_protocol_sha256",
                "v23_base_report_sha256", "v23_base_receipt_sha256",
                "v23_strict_report_sha256", "v23_strict_receipt_sha256",
            )
        ), "candidate-free V26 controls cannot access ownership reports or run workers")
        result = candidate_free_self_test()
    else:
        require(type(options.module) is str,
                "an original worker requires its exact independently owned candidate")
        family = next(name for name, row in original.FAMILIES.items()
                      if row["module"] == options.module)
        pins = validated_pins({
            "audit_source": options.v23_audit_source_sha256,
            "audit_protocol": options.v23_audit_protocol_sha256,
            "base_report": options.v23_base_report_sha256,
            "base_receipt": options.v23_base_receipt_sha256,
            "strict_report": options.v23_strict_report_sha256,
            "strict_receipt": options.v23_strict_receipt_sha256,
        })
        result = (refresh_edge(family, pins) if options.qualified_edge
                  else refresh_deep(family, pins))
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofV26Failure as error:
        print(json.dumps(error.evidence, ensure_ascii=True,
                         allow_nan=False, sort_keys=True))
        raise SystemExit(1) from error
