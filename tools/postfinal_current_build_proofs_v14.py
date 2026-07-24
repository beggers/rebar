#!/usr/bin/env python3
"""Qualify unchanged original suites against a genuinely current V13 owner."""

from __future__ import annotations

import argparse
import ast
import builtins
import collections
import copy
import gzip
import hashlib
import importlib
import json
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_current_build_proofs_v12 as legacy


original = legacy.v11
SCHEMA = "rebar-postfinal-current-build-proofs-v14"
SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v14.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V14.md"
PROTOCOL_SHA256 = (
    "4391186888a28a730fba946e82d1e38835d4e464f4a85bc526061d43183c197e"
)
V12_SOURCE_SHA256 = (
    "81a519fa4890d5a7f6901d58c9154711be116fd7de4b081c0c052d64db481b3f"
)
V13_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v13.py"
V13_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V13.md"
)
V13_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V13.json"
)
V13_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V13.json"
)
V13_BASE_SCHEMA = "rebar-postfinal-from-scratch-audit-v13"
V13_STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v13"
PIN_NAMES = ("audit_source", "audit_protocol", "base_report", "strict_report")
FAMILIES = ("rust", "vm", "zig")
ZIG_FAILURE_RELATIVE = (
    "candidates/audits/"
    "RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V12-PRODUCER-CRASH.json.gz"
)
ZIG_FAILURE_SHA256 = (
    "5c3e07d9f11d5c8244d3d22fc94f287f4f0573423bf38e70b6abc383c96eca90"
)
ZIG_FAILURE_PROOF_RELATIVE = (
    "candidates/audits/"
    "RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V12-"
    "RETRY-FAIL-PROOF.json"
)
ZIG_FAILURE_PROOF_SHA256 = (
    "b5deb6c3ce522fe0dbc3c4e723867ffe830520f0a47a0b72cc5b1d9a0a69ad9d"
)
ZIG_INVALIDATED_RELATIVE = (
    "candidates/audits/"
    "RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V12-"
    "INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
)
ZIG_INVALIDATED_SHA256 = (
    "d7f11c33a010406db1637e0715e72bfebdc13acf21118735b6b1f6e550927865"
)
ZIG_FAILURE_COUNTS = {
    "public-method-introspection": 18,
    "seeded/public-method-introspection": 8,
}


class ProofV14Error(AssertionError):
    """A real V14 owner, original observation, or immutable proof failed."""


class ProofV14Failure(ProofV14Error):
    """Expose the exact separately retained real producer failure."""

    def __init__(self, message: str, evidence: Mapping[str, Any]):
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ProofV14Error(message)


def verify_runtime_source_only() -> None:
    legacy.verify_runtime_source_only()
    require(
        ROOT == original.ROOT
        and Path(__file__).resolve() == ROOT / SOURCE_RELATIVE
        and tuple(original.FAMILIES) == FAMILIES
        and original.EDGE_CHECKS == 223198
        and original.EDGE_CATEGORIES == 49
        and original.DEEP_CHECKS == 393
        and original.DEEP_SEEDED_CASES == 64
        and sum(len(row["sources"]) for row in original.FAMILIES.values()) == 12
        and sum(len(row["native"]) for row in original.FAMILIES.values()) == 5,
        "V14 requires the complete immutable original 3-family 12-source/5-ELF contract",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            or name == "rebar" or name.startswith("rebar.")
            for name in sys.modules
        ),
        "a production candidate escaped into the V14 proof controller",
    )


def validate_parent_environment(environment: Mapping[str, Any]) -> dict[str, str]:
    return legacy.validate_parent_environment(environment)


def worker_environment() -> dict[str, str]:
    return legacy.worker_environment()


def checked_family(family: str) -> dict[str, Any]:
    require(type(family) is str and family in FAMILIES,
            "only an independently owned Rust, C, or Zig family is permitted")
    return original.checked_family(family)


def validated_pins(supplied: Any) -> dict[str, str]:
    require(
        isinstance(supplied, Mapping) and set(supplied) == set(PIN_NAMES),
        "BLOCKED: independently publish all four genuine V13 source, protocol, "
        "base-report, and strict-report fingerprints",
    )
    pins: dict[str, str] = {}
    for name in PIN_NAMES:
        value = supplied[name]
        require(
            original.valid_sha256(value),
            "BLOCKED: the independently published actual V13 " + name
            + " SHA-256 is required",
        )
        pins[name] = value
    require(
        len(set(pins.values())) == len(PIN_NAMES),
        "an actual V13 source, protocol, or report cannot reuse another fingerprint",
    )
    return pins


def authenticate_controller() -> dict[str, str]:
    verify_runtime_source_only()
    source = original.read_regular(
        ROOT / SOURCE_RELATIVE, "complete actual immutable V14 controller",
    )
    protocol = original.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    original.authenticate_frozen(legacy.SOURCE_RELATIVE, V12_SOURCE_SHA256)
    original.authenticate_frozen(legacy.PROTOCOL_RELATIVE, legacy.PROTOCOL_SHA256)
    original.authenticate_frozen(
        original.SOURCE_RELATIVE, legacy.V11_SOURCE_SHA256,
    )
    original.authenticate_frozen(
        original.PROTOCOL_RELATIVE, legacy.V11_PROTOCOL_SHA256,
    )
    original.authenticate_frozen(
        original.V8_PROOF_RELATIVE, original.V8_PROOF_SHA256,
    )
    for relative in (
        original.EDGE_SOURCE_RELATIVE, original.DEEP_SOURCE_RELATIVE,
        original.DEEP_RUNNER_RELATIVE, original.STAGE07_RELATIVE,
    ):
        original.authenticate_frozen(relative, original.FROZEN_INPUTS[relative])
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": hashlib.sha256(protocol).hexdigest(),
        "original_v11_source_path": original.SOURCE_RELATIVE,
        "original_v11_source_sha256": legacy.V11_SOURCE_SHA256,
        "original_v11_protocol_path": original.PROTOCOL_RELATIVE,
        "original_v11_protocol_sha256": legacy.V11_PROTOCOL_SHA256,
        "original_v12_source_path": legacy.SOURCE_RELATIVE,
        "original_v12_source_sha256": V12_SOURCE_SHA256,
        "original_v12_protocol_path": legacy.PROTOCOL_RELATIVE,
        "original_v12_protocol_sha256": legacy.PROTOCOL_SHA256,
    }


def edge_target(family: str, passed: bool) -> Path:
    checked_family(family)
    require(type(passed) is bool, "a genuine edge outcome must be boolean")
    result = "pass" if passed else "failures"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v14-qualified-" + result + ".json.gz"
    )


def edge_proof_target(family: str, passed: bool) -> Path:
    target = edge_target(family, passed)
    return target.parent / (
        target.name.removesuffix(".json.gz") + "-proof.json"
    )


def deep_target(family: str, passed: bool) -> Path:
    metadata = checked_family(family)
    require(type(passed) is bool, "a genuine deep outcome must be boolean")
    result = "PASS" if passed else "FAILURES"
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V14-" + result + ".json.gz"
    )


def deep_proof_target(family: str, passed: bool) -> Path:
    target = deep_target(family, passed)
    return target.parent / (
        target.name.removesuffix(".json.gz") + "-PROOF.json"
    )


def failure_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool, "a genuine failure stage must be boolean")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V14-PRODUCER-CRASH.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v14-qualified-producer-crash.json.gz"
    )


def invalidated_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool, "an original invalidation stage must be boolean")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V14-"
            "INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v14-qualified-"
        "invalidated-after-owner-failure.json.gz"
    )


def _contains(value: Any, wanted: str, remaining: int = 4096) -> bool:
    require(remaining > 0, "a historical provenance object exceeded its bound")
    if isinstance(value, str):
        return value == wanted
    if isinstance(value, Mapping):
        return any(_contains(item, wanted, remaining - 1)
                   for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains(item, wanted, remaining - 1) for item in value)
    return False


def validate_zig_pattern_mismatches(report: Any) -> dict[str, Any]:
    require(
        isinstance(report, Mapping)
        and report.get("status") == "FAIL"
        and report.get("candidate_family") == "ZIG"
        and report.get("candidate_module") == "candidates.zig_candidate"
        and report.get("checks") == original.DEEP_CHECKS
        and report.get("seeded_case_count") == original.DEEP_SEEDED_CASES
        and report.get("reference_a_sha256") == original.DEEP_REFERENCE_SHA256
        and report.get("reference_b_sha256") == original.DEEP_REFERENCE_SHA256
        and report.get("public_mismatch_count") == 26
        and report.get("public_mismatch_family_counts") == ZIG_FAILURE_COUNTS,
        "the authentic failed Zig original lost its exact 393/64 and 18+8 "
        "public method-introspection denominator",
    )
    rows = report.get("public_mismatches")
    require(
        isinstance(rows, list) and len(rows) == 26
        and all(isinstance(row, Mapping) for row in rows),
        "all 26 genuine original Zig public observations must be retained",
    )
    observed = collections.Counter()
    identifiers: set[str] = set()
    for row in rows:
        identity = row.get("id")
        family = row.get("family")
        expected = row.get("expected")
        actual = row.get("actual")
        require(
            isinstance(identity, str) and identity not in identifiers
            and family in ZIG_FAILURE_COUNTS
            and isinstance(expected, Mapping)
            and isinstance(actual, Mapping),
            "a real original Zig public mismatch was omitted or reclassified",
        )
        identifiers.add(identity)
        observed[family] += 1
        require(
            identity.startswith(
                "seeded/"
                if family == "seeded/public-method-introspection"
                else "public-method-introspection/"
            ),
            "a genuine original or seeded Zig mismatch changed its case identity",
        )
        expected_fields = dict(expected)
        actual_fields = dict(actual)
        expected_repr = expected_fields.pop("repr", None)
        actual_repr = actual_fields.pop("repr", None)
        require(
            expected_fields == actual_fields
            and isinstance(expected_repr, Mapping)
            and isinstance(actual_repr, Mapping)
            and expected_repr.get("status") == "value"
            and actual_repr.get("status") == "value"
            and isinstance(expected_repr.get("value"), str)
            and isinstance(actual_repr.get("value"), str)
            and "re.Pattern" in expected_repr["value"]
            and "Pattern" in actual_repr["value"]
            and "re.Pattern" not in actual_repr["value"],
            "the genuine CPython re.Pattern versus Zig Pattern public "
            "method representation was changed: " + identity,
        )
    require(
        dict(sorted(observed.items())) == ZIG_FAILURE_COUNTS,
        "the actual 18 original and eight seeded Zig failures were reclassified",
    )
    return {
        "public_mismatch_count": 26,
        "public_mismatch_family_counts": dict(ZIG_FAILURE_COUNTS),
        "reference_pattern_name": "re.Pattern",
        "candidate_pattern_name": "Pattern",
        "all_original_representation_mismatches_verified": True,
    }


def validate_current_graph(
    v13: Any, audits: Mapping[str, Any], *, recheck: bool,
) -> dict[str, Any]:
    require(
        isinstance(audits, Mapping)
        and set(audits) == {
            "base", "strict", "graph", "pins", "history",
            "preserved_zig_failure", "owner",
        },
        "the genuinely independent V13 audit omitted a complete ownership role",
    )
    graph = audits["graph"]
    require(
        isinstance(graph, dict)
        and graph.get("source_count") == 12
        and graph.get("native_binary_count") == 5
        and isinstance(graph.get("source_paths"), list)
        and len(graph["source_paths"]) == 12
        and len(set(graph["source_paths"])) == 12
        and isinstance(graph.get("source_sha256_by_family"), dict)
        and isinstance(graph.get("native_sha256_by_family"), dict)
        and set(graph["source_sha256_by_family"]) == set(FAMILIES)
        and set(graph["native_sha256_by_family"]) == set(FAMILIES),
        "the real V13 ownership audit dropped an independent source or native ELF",
    )
    for family in FAMILIES:
        metadata = checked_family(family)
        sources = graph["source_sha256_by_family"][family]
        native = graph["native_sha256_by_family"][family]
        require(
            isinstance(sources, dict)
            and set(sources) == set(metadata["sources"])
            and all(original.valid_sha256(value)
                    for value in sources.values())
            and isinstance(native, dict)
            and set(native) == set(metadata["native"].values())
            and all(original.valid_sha256(value)
                    for value in native.values())
            and tuple(v13.OWNED_SOURCE_PATHS[family]) == metadata["sources"]
            and dict(v13.OWNED_NATIVE_PATHS[family]) == metadata["native"],
            "the fresh complete V13 owned source/ELF graph changed: " + family,
        )
    expected_paths = [
        path for family in FAMILIES
        for path in checked_family(family)["sources"]
    ]
    require(set(graph["source_paths"]) == set(expected_paths),
            "the current actual V13 graph lost an owned matching source")
    require(type(recheck) is bool, "a real graph recheck must be explicit")
    if recheck:
        require(
            v13.snapshot_current_graph() == graph,
            "a current candidate source or mapped native ELF changed after V13",
        )
    return graph


def _validate_preserved_incidents(audits: Mapping[str, Any]) -> dict[str, Any]:
    history = audits["history"]
    preserved = audits["preserved_zig_failure"]
    require(isinstance(history, Mapping),
            "the genuine V13 owner omitted complete immutable failure history")
    require(
        isinstance(preserved, Mapping)
        and preserved.get("invalidated_path") == ZIG_INVALIDATED_RELATIVE
        and preserved.get("invalidated_sha256") == ZIG_INVALIDATED_SHA256
        and preserved.get("producer_failure_path") == ZIG_FAILURE_RELATIVE
        and preserved.get("producer_failure_sha256") == ZIG_FAILURE_SHA256
        and preserved.get("retry_failure_proof_path")
        == ZIG_FAILURE_PROOF_RELATIVE
        and preserved.get("retry_failure_proof_sha256")
        == ZIG_FAILURE_PROOF_SHA256
        and preserved.get("actual_child_exit_code") == 1
        and preserved.get("deep_checks") == original.DEEP_CHECKS
        and preserved.get("seeded_case_count") == original.DEEP_SEEDED_CASES
        and preserved.get("public_mismatch_count") == 26
        and preserved.get("public_mismatch_family_counts")
        == ZIG_FAILURE_COUNTS
        and preserved.get("actual_reference_observation_sha256")
        == original.DEEP_REFERENCE_SHA256
        and original.valid_sha256(
            preserved.get("actual_candidate_observation_sha256")
        )
        and preserved.get("candidate_family") == "ZIG"
        and preserved.get("qualifies_current_engine") is False,
        "the genuinely failed V12 Zig original was omitted or falsely qualified",
    )
    require(
        _contains(history, legacy.PRIOR_FAILURE_SHA256)
        and _contains(history, legacy.PRIOR_INVALIDATED_SHA256),
        "the real failed and invalidated first V11 Rust invocation was concealed",
    )
    return {
        "v11_rust_first_failure_sha256": legacy.PRIOR_FAILURE_SHA256,
        "v11_rust_invalidated_original_sha256":
            legacy.PRIOR_INVALIDATED_SHA256,
        "v11_rust_first_failure_qualifies_current_build": False,
        "v12_zig_producer_failure_sha256": ZIG_FAILURE_SHA256,
        "v12_zig_failure_proof_sha256": ZIG_FAILURE_PROOF_SHA256,
        "v12_zig_invalidated_original_sha256": ZIG_INVALIDATED_SHA256,
        "v12_zig_public_mismatch_count": 26,
        "v12_zig_public_mismatch_family_counts": dict(ZIG_FAILURE_COUNTS),
        "v12_zig_reference_pattern_name": "re.Pattern",
        "v12_zig_candidate_pattern_name": "Pattern",
        "v12_zig_failure_qualifies_current_build": False,
    }


def authenticate_preserved_zig_failure(
    v13: Any,
    v8: Any,
    audits: Mapping[str, Any],
) -> dict[str, Any]:
    historical_owner = original.import_frozen(
        "tools.postfinal_from_scratch_audit_v10",
        original.V10_BASE_SOURCE_RELATIVE,
        original.V10_BASE_SOURCE_SHA256,
    )
    historical_strict = original.import_frozen(
        "tools.postfinal_no_delegation_audit_v10",
        original.V10_STRICT_SOURCE_RELATIVE,
        original.V10_STRICT_SOURCE_SHA256,
    )
    require(
        historical_owner is audits["owner"]
        and historical_strict.independent is historical_owner,
        "the genuine original V10 historical owner was replaced",
    )
    historical_pins = original.validated_report_pins(
        True,
        legacy.ACTUAL_V10_BASE_REPORT_SHA256,
        legacy.ACTUAL_V10_STRICT_REPORT_SHA256,
    )
    require(isinstance(historical_pins, dict),
            "both real historical V10 audit fingerprints are mandatory")
    historical_audits = original.audit_v11_reports(
        historical_owner, historical_strict, historical_pins,
    )
    preliminary = {
        "owner": historical_owner,
        "v8": v8,
        "audits": historical_audits,
    }
    first, _, _ = legacy.authenticate_prior_incident(preliminary)
    history = original.authenticate_history(v8, historical_owner)
    historical_graph = original.audited_graph_provenance(preliminary)
    metadata = checked_family("zig")
    historical_snapshot = {
        "family": "zig",
        "module": metadata["module"],
        "source_sha256_by_path": {
            path: historical_graph["all_family_source_sha256_by_path"][path]
            for path in metadata["sources"]
        },
        "native_sha256_by_path": {
            path: historical_graph["all_family_native_elf_sha256_by_path"][path]
            for path in metadata["native"].values()
        },
    }
    historical_state = {
        **preliminary,
        "strict": historical_strict,
        "history": history,
        "snapshot": historical_snapshot,
    }
    contract = v8.load_contract()
    edge, _, historical_edge_raw, _ = legacy.authenticate_qualified_edge(
        "zig", historical_state, contract,
    )
    _, independently_validated_edge, edge_passed = (
        v8.validate_original_edge(
            historical_edge_raw,
            original.edge_target("zig", True, True),
            "zig",
            historical_snapshot,
            contract,
        )
    )
    require(
        edge_passed is True and independently_validated_edge == edge,
        "the preserved original Zig failure lost its genuine historical edge",
    )
    invalidated_raw = original.authenticate_frozen(
        ZIG_INVALIDATED_RELATIVE, ZIG_INVALIDATED_SHA256,
    )
    invalidated, _ = v8.decode_archive(
        invalidated_raw,
        "complete unchanged original V12 Zig failed observations",
        compact=True,
    )
    independently_validated, passed = v8.validate_deep(
        invalidated_raw, "zig", edge, historical_snapshot, contract,
    )
    require(
        passed is False and independently_validated == invalidated,
        "the actual unchanged 393-case historical Zig failure did not validate",
    )
    representation = validate_zig_pattern_mismatches(
        independently_validated,
    )
    crash_raw = original.authenticate_frozen(
        ZIG_FAILURE_RELATIVE, ZIG_FAILURE_SHA256,
    )
    crash, crash_payload = v8.decode_archive(
        crash_raw,
        "complete canonical genuine original V12 Zig producer failure",
    )
    require(
        original.canonical(crash) == crash_payload,
        "the complete historical Zig crash lost its exact canonical bytes",
    )
    retry_raw = original.authenticate_frozen(
        ZIG_FAILURE_PROOF_RELATIVE, ZIG_FAILURE_PROOF_SHA256,
    )
    retry = original.decode_json(
        retry_raw, "complete exact genuine V12 Zig failed retry proof",
    )
    require(
        original.canonical(retry) == retry_raw,
        "the complete historical Zig failure proof lost its canonical bytes",
    )
    summary = v13.validate_zig_failure_documents(
        crash, invalidated, retry, independently_validated, passed=False,
    )
    require(
        summary == audits["preserved_zig_failure"]
        and crash.get("preserved_actual_first_v11_failure") == first
        and summary.get("public_mismatch_family_counts")
        == representation["public_mismatch_family_counts"],
        "the fresh V13 audit replaced the actual original Zig or Rust failure",
    )
    return {
        **_validate_preserved_incidents(audits),
        "v12_zig_original_representation_proof": representation,
    }


def preflight(family: str, pins: Mapping[str, Any]) -> dict[str, Any]:
    metadata = checked_family(family)
    values = validated_pins(pins)
    verify_runtime_source_only()
    parent = validate_parent_environment(os.environ)
    controller = authenticate_controller()
    original.authenticate_frozen(V13_PROTOCOL_RELATIVE,
                                 values["audit_protocol"])
    v13 = original.import_frozen(
        "tools.postfinal_independent_engine_audit_v13",
        V13_SOURCE_RELATIVE, values["audit_source"],
    )
    require(
        v13.SOURCE_RELATIVE == V13_SOURCE_RELATIVE
        and v13.PROTOCOL_RELATIVE == V13_PROTOCOL_RELATIVE
        and v13.PROTOCOL_SHA256 == values["audit_protocol"]
        and v13.BASE_SCHEMA == V13_BASE_SCHEMA
        and v13.STRICT_SCHEMA == V13_STRICT_SCHEMA
        and tuple(v13.CORE_FAMILIES) == FAMILIES,
        "the actual independently frozen dual-mode V13 owner was substituted",
    )
    audits = v13.authenticate_qualified_audits(
        values["base_report"], values["strict_report"],
    )
    graph = validate_current_graph(v13, audits, recheck=True)
    require(
        audits["pins"] == values,
        "the actual V13 source, protocol, or reports changed after validation",
    )
    require(
        isinstance(audits["base"], Mapping)
        and audits["base"].get("schema") == V13_BASE_SCHEMA
        and audits["base"].get("status") == "PASS"
        and isinstance(audits["strict"], Mapping)
        and audits["strict"].get("schema") == V13_STRICT_SCHEMA
        and audits["strict"].get("status") == "PASS",
        "the exact actual independent current V13 base and strict reports failed",
    )
    v8 = original.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        original.V8_PROOF_RELATIVE, original.V8_PROOF_SHA256,
    )
    preserved = authenticate_preserved_zig_failure(v13, v8, audits)
    snapshot = {
        "family": family,
        "module": metadata["module"],
        "source_sha256_by_path":
            dict(graph["source_sha256_by_family"][family]),
        "native_sha256_by_path":
            dict(graph["native_sha256_by_family"][family]),
    }
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "a production candidate escaped into the actual V14 proof controller",
    )
    return {
        "v13": v13,
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
        len(source) == 12 and len(native) == 5,
        "a complete V14 owner proof omitted an independent source or native ELF",
    )
    return {
        "all_family_audit_qualified": True,
        "all_family_source_sha256_by_path": source,
        "all_family_native_elf_sha256_by_path": native,
    }


def observe_owner(
    family: str, state: Mapping[str, Any], *, stage: str,
) -> dict[str, Any]:
    checked_family(family)
    require(
        stage in {
            "before-original-edge", "after-original-edge",
            "before-original-deep", "after-original-deep",
        },
        "only a real before/after native-owner stage can be observed",
    )
    expected = dict(state["snapshot"]["native_sha256_by_path"])
    v13 = state["v13"]
    record = v13.run_native_worker(family, expected)
    validated = v13.validate_native_owner(record, family, expected)
    require(
        isinstance(record, dict)
        and (validated is record or validated == record)
        and record.get("status") == "PASS"
        and record.get("passed") is True
        and record.get("family") == family
        and record.get("native_binary_sha256") == expected
        and record.get("genuine_matching_executed") is True
        and record.get("regex_guard_count") == 13
        and record.get("native_loader_guard_count") == 5
        and record.get("external_regex_packages") == 0
        and record.get("persistent_cross_engine_guard") is True
        and record.get("benchmark_or_timing_executed") is False
        and record.get("holdout_or_case_fixture_access") is False,
        "the genuine fresh V13 native owner failed: " + family + ":" + stage,
    )
    return record


def preflight_fresh_destinations(family: str, *, deep: bool) -> None:
    checked_family(family)
    require(type(deep) is bool, "an original proof stage must be explicit")
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    targets = (
        (deep_target(family, True), deep_target(family, False),
         deep_proof_target(family, True), deep_proof_target(family, False))
        if deep else
        (edge_target(family, True), edge_target(family, False),
         edge_proof_target(family, True), edge_proof_target(family, False))
    ) + (
        failure_target(family, deep=deep),
        invalidated_target(family, deep=deep),
    )
    require(
        len(targets) == len(set(targets))
        and all("current-build-v14" in target.name.lower()
                for target in targets)
        and all(
            target != ROOT / relative
            for target in targets
            for relative in (
                legacy.PRIOR_FAILURE_RELATIVE,
                legacy.PRIOR_INVALIDATED_RELATIVE,
                ZIG_FAILURE_RELATIVE,
                ZIG_FAILURE_PROOF_RELATIVE,
                ZIG_INVALIDATED_RELATIVE,
            )
        ),
        "V14 reused a historical result, family, outcome, or evidence destination",
    )
    for target in targets:
        original.fresh_target(target, parent)


def new_publication_receipt(
    family: str,
    *,
    deep: bool,
) -> dict[str, Any]:
    checked_family(family)
    require(type(deep) is bool,
            "a genuine publication receipt requires one exact original stage")
    return {
        "family": family,
        "deep": deep,
        "passed": None,
        "archive_published": False,
        "archive_path": None,
        "archive_sha256": None,
        "proof_published": False,
        "proof_path": None,
        "proof_sha256": None,
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
        isinstance(receipt, dict)
        and set(receipt) == {
            "family", "deep", "passed",
            "archive_published", "archive_path", "archive_sha256",
            "proof_published", "proof_path", "proof_sha256",
        }
        and receipt["family"] == family
        and receipt["deep"] is deep
        and type(receipt["archive_published"]) is bool
        and type(receipt["proof_published"]) is bool
        and (receipt["passed"] is None
             or type(receipt["passed"]) is bool)
        and not (receipt["proof_published"]
                 and not receipt["archive_published"]),
        "a genuine V14 partial-publication receipt was omitted or forged",
    )
    require(
        passed is None or receipt["passed"] is passed,
        "a partial V14 publication changed its actual original result",
    )
    if not receipt["archive_published"]:
        require(
            receipt["archive_path"] is None
            and receipt["archive_sha256"] is None
            and not receipt["proof_published"],
            "an unpublished V14 original cannot claim an archive or proof",
        )
    else:
        actual_passed = receipt["passed"]
        require(
            type(actual_passed) is bool,
            "a real published V14 original lost its actual pass/fail outcome",
        )
        expected = (
            deep_target(family, actual_passed)
            if deep else edge_target(family, actual_passed)
        )
        require(
            receipt["archive_path"] == expected.relative_to(ROOT).as_posix()
            and original.valid_sha256(receipt["archive_sha256"]),
            "a genuinely published V14 original lost its exact path or hash",
        )
        if original_raw is not None:
            require(
                isinstance(original_raw, bytes)
                and hashlib.sha256(original_raw).hexdigest()
                == receipt["archive_sha256"],
                "the actual published V14 original bytes changed",
            )
    if not receipt["proof_published"]:
        require(
            receipt["proof_path"] is None
            and receipt["proof_sha256"] is None,
            "an unpublished V14 owner proof cannot claim a path or hash",
        )
    else:
        actual_passed = receipt["passed"]
        require(
            type(actual_passed) is bool,
            "a real published V14 owner proof lost its actual original result",
        )
        expected = (
            deep_proof_target(family, actual_passed)
            if deep else edge_proof_target(family, actual_passed)
        )
        require(
            receipt["proof_path"] == expected.relative_to(ROOT).as_posix()
            and original.valid_sha256(receipt["proof_sha256"]),
            "a genuinely published V14 owner proof lost its exact path or hash",
        )
    return receipt


def record_exclusive_publication(
    receipt: dict[str, Any],
    family: str,
    *,
    deep: bool,
    passed: bool,
    proof: bool,
    path: Path,
    raw: bytes,
    publisher: Callable[..., str] | None = None,
) -> str:
    checked_family(family)
    require(
        type(deep) is bool and type(passed) is bool and type(proof) is bool
        and isinstance(path, Path)
        and isinstance(raw, bytes)
        and 0 < len(raw) <= original.MAX_FILE_BYTES,
        "a genuine exclusive V14 publication must preserve complete bytes",
    )
    validate_publication_receipt(receipt, family, deep=deep)
    if receipt["passed"] is None:
        receipt["passed"] = passed
    require(
        receipt["passed"] is passed
        and receipt["archive_published"] is proof
        and receipt["proof_published"] is False,
        "a V14 publication was reordered, repeated, or falsely paired",
    )
    target = (
        (deep_proof_target(family, passed)
         if proof else deep_target(family, passed))
        if deep else
        (edge_proof_target(family, passed)
         if proof else edge_target(family, passed))
    )
    require(path == target,
            "a real V14 publication changed its exact family or destination")
    publish = original.exclusive_publish if publisher is None else publisher
    digest = publish(path, raw, deep=deep)
    if proof:
        receipt.update({
            "proof_published": True,
            "proof_path": path.relative_to(ROOT).as_posix(),
            "proof_sha256": digest,
        })
    else:
        receipt.update({
            "archive_published": True,
            "archive_path": path.relative_to(ROOT).as_posix(),
            "archive_sha256": digest,
        })
    validate_publication_receipt(
        receipt, family, deep=deep, passed=passed,
        original_raw=raw if not proof else None,
    )
    require(
        hashlib.sha256(raw).hexdigest() == digest,
        "an exclusively published V14 artifact lost its actual complete hash",
    )
    return digest


def failure_publication_fields(
    publication: Mapping[str, Any],
    family: str,
    *,
    deep: bool,
    original_raw: bytes | None,
) -> dict[str, Any]:
    checked = validate_publication_receipt(
        publication, family, deep=deep, original_raw=original_raw,
    )
    return {
        "v14_original_archive_was_exclusively_published":
            checked["archive_published"],
        "v14_original_archive_path": checked["archive_path"],
        "v14_original_archive_sha256": checked["archive_sha256"],
        "v14_owner_proof_was_exclusively_published":
            checked["proof_published"],
        "v14_owner_proof_path": checked["proof_path"],
        "v14_owner_proof_sha256": checked["proof_sha256"],
        "unpaired_v14_original_archive_qualifies": False,
    }


def build_durable_wrapper(
    family: str,
    state: Mapping[str, Any],
    *,
    deep: bool,
    passed: bool,
    original_report: Mapping[str, Any] | None = None,
    original: Mapping[str, Any] | None = None,
    archive_path: Path,
    archive_sha256: str,
    archive_bytes: int,
    owner_before: Mapping[str, Any],
    owner_after: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes],
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = checked_family(family)
    require(
        type(deep) is bool and type(passed) is bool
        and isinstance(producer, subprocess.CompletedProcess)
        and isinstance(producer.returncode, int)
        and isinstance(producer.stdout, bytes)
        and isinstance(producer.stderr, bytes)
        and len(producer.stdout) <= globals()["original"].MAX_CHILD_OUTPUT_BYTES
        and len(producer.stderr) <= globals()["original"].MAX_CHILD_OUTPUT_BYTES
        and isinstance(archive_path, Path)
        and globals()["original"].valid_sha256(archive_sha256)
        and type(archive_bytes) is int
        and 0 < archive_bytes <= globals()["original"].MAX_FILE_BYTES,
        "a V14 original archive requires complete real producer bytes",
    )
    report = original_report if original_report is not None else original
    require(isinstance(report, Mapping),
            "the complete unchanged original V14 observations are missing")
    pins = validated_pins(state["audits"]["pins"])
    mode = "qualified-deep" if deep else "qualified-edge"
    target = deep_target(family, passed) if deep else edge_target(family, passed)
    proof = (
        deep_proof_target(family, passed)
        if deep else edge_proof_target(family, passed)
    )
    require(archive_path == target,
            "a V14 wrapper changed its exact original archive destination")
    controller = state["controller"]
    document: dict[str, Any] = {
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
        "complete_original_producer_bytes_preserved": True,
        "original_archive_is_unmodified_original": True,
        "stdout_is_not_durable_proof": True,
        "original_worker_returncode": producer.returncode,
        "original_worker_stdout":
            globals()["original"].observed_stream(producer.stdout, True),
        "original_worker_stderr":
            globals()["original"].observed_stream(producer.stderr, True),
        "current_v13_native_owner_before": dict(owner_before),
        "current_v13_native_owner_after": dict(owner_after),
        "full_current_family_source_sha256":
            dict(state["snapshot"]["source_sha256_by_path"]),
        "full_current_family_native_elf_sha256":
            dict(state["snapshot"]["native_sha256_by_path"]),
        "all_family_audited_provenance": audited_graph_provenance(state),
        "actual_v13_audit_source_path": V13_SOURCE_RELATIVE,
        "actual_v13_audit_source_sha256": pins["audit_source"],
        "actual_v13_protocol_path": V13_PROTOCOL_RELATIVE,
        "actual_v13_protocol_sha256": pins["audit_protocol"],
        "actual_v13_base_report_path": V13_BASE_REPORT_RELATIVE,
        "actual_v13_base_report_sha256": pins["base_report"],
        "actual_v13_strict_report_path": V13_STRICT_REPORT_RELATIVE,
        "actual_v13_strict_report_sha256": pins["strict_report"],
        "actual_invoking_controller": "V14",
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
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    frozen = globals()["original"]
    if deep:
        document.update({
            "seed": frozen.DEEP_SEED,
            "checks": frozen.DEEP_CHECKS,
            "seeded_case_count": frozen.DEEP_SEEDED_CASES,
            "reference_sha256": frozen.DEEP_REFERENCE_SHA256,
            "actual_sha256": report.get("candidate_sha256"),
            "public_mismatch_count": report.get("public_mismatch_count"),
            "public_mismatch_family_counts":
                report.get("public_mismatch_family_counts"),
            "qualified_edge": (
                dict(qualified_edge)
                if isinstance(qualified_edge, Mapping) else None
            ),
        })
    else:
        document.update({
            "seed": frozen.EDGE_SEED,
            "checks": frozen.EDGE_CHECKS,
            "category_count": frozen.EDGE_CATEGORIES,
            "reference_sha256": frozen.EDGE_REFERENCE_SHA256,
            "actual_sha256": report.get("actual_sha256"),
            "failure_count": report.get("failed"),
            "complete_failure_row_count": len(report.get("failures", [])),
        })
    return document


def validate_durable_wrapper(
    document: Any,
    family: str,
    state: Mapping[str, Any],
    *,
    deep: bool,
    passed: bool,
    original_report: Mapping[str, Any] | None = None,
    original: Mapping[str, Any] | None = None,
    archive_path: Path,
    archive_sha256: str,
    archive_bytes: int,
    owner_before: Mapping[str, Any],
    owner_after: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes],
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = checked_family(family)
    expected = build_durable_wrapper(
        family, state, deep=deep, passed=passed,
        original_report=original_report, original=original,
        archive_path=archive_path, archive_sha256=archive_sha256,
        archive_bytes=archive_bytes, owner_before=owner_before,
        owner_after=owner_after, producer=producer,
        qualified_edge=qualified_edge,
    )
    require(
        isinstance(document, dict) and document == expected,
        "the complete immutable V14 owner proof changed original observations, "
        "current V13 ownership, the genuine producer, or actual audit pins",
    )
    require(
        producer.returncode == int(not passed)
        and document["campaign_qualified"] is passed
        and document["candidate_module"] == metadata["module"]
        and document["stdout_is_not_durable_proof"] is True
        and document["production_observations_invented"] is False,
        "a real V14 mismatch, failure, diagnostic, or stdout was falsely qualified",
    )
    snapshot = state["snapshot"]
    require(
        snapshot.get("family") == family
        and snapshot.get("module") == metadata["module"]
        and set(snapshot.get("source_sha256_by_path", {}))
        == set(metadata["sources"])
        and set(snapshot.get("native_sha256_by_path", {}))
        == set(metadata["native"].values()),
        "the complete V14 owner proof omitted a current family source or ELF",
    )
    v13 = state["v13"]
    expected_native = dict(snapshot["native_sha256_by_path"])
    for phase, record in (
        ("before", owner_before), ("after", owner_after),
    ):
        validated = v13.validate_native_owner(
            record, family, expected_native,
        )
        require(
            isinstance(record, Mapping)
            and (validated is record or validated == record)
            and record.get("status") == "PASS"
            and record.get("family") == family,
            "a genuine independent V13 " + phase
            + " matching owner was omitted or forged",
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
            and globals()["original"].valid_sha256(
                qualified_edge.get("archive_sha256"))
            and globals()["original"].valid_sha256(
                qualified_edge.get("proof_sha256")),
            "deep V14 qualification requires its own complete passing V14 edge pair",
        )
    return document


def _recorded_producer(wrapper: Mapping[str, Any]) -> (
    subprocess.CompletedProcess[bytes]
):
    return subprocess.CompletedProcess(
        args=["durably-recorded-original-v14-worker"],
        returncode=wrapper.get("original_worker_returncode"),
        stdout=original.restore_complete_stream(
            wrapper.get("original_worker_stdout"),
            "complete immutable V14 original stdout",
        ),
        stderr=original.restore_complete_stream(
            wrapper.get("original_worker_stderr"),
            "complete immutable V14 original stderr",
        ),
    )


def authenticate_qualified_edge(
    family: str, state: Mapping[str, Any], contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    checked_family(family)
    archive_path = edge_target(family, True)
    proof_path = edge_proof_target(family, True)
    raw = original.read_regular(
        archive_path, "complete current-family original passing V14 edge",
    )
    document, edge, passed = state["v8"].validate_original_edge(
        raw, archive_path, family, state["snapshot"], contract,
    )
    require(
        passed is True and edge.get("failed") == 0
        and edge.get("checks") == original.EDGE_CHECKS
        and edge.get("category_count") == original.EDGE_CATEGORIES,
        "the actual original V14 edge did not pass all 223,198/49 checks",
    )
    proof_raw = original.read_regular(
        proof_path, "complete actual passing V14 edge owner proof",
    )
    proof = original.decode_json(proof_raw, "complete canonical V14 edge proof")
    require(original.canonical(proof) == proof_raw,
            "the complete V14 edge proof lost its exact canonical bytes")
    producer = _recorded_producer(proof)
    validate_durable_wrapper(
        proof, family, state, deep=False, passed=True,
        original_report=document, archive_path=archive_path,
        archive_sha256=hashlib.sha256(raw).hexdigest(),
        archive_bytes=len(raw),
        owner_before=proof.get("current_v13_native_owner_before"),
        owner_after=proof.get("current_v13_native_owner_after"),
        producer=producer,
    )
    summary = {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": archive_path.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
    }
    return edge, summary, raw, proof_raw


def authenticate_qualified_deep(
    family: str, state: Mapping[str, Any], contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    edge, qualified_edge, _, _ = authenticate_qualified_edge(
        family, state, contract,
    )
    archive_path = deep_target(family, True)
    proof_path = deep_proof_target(family, True)
    raw = original.read_regular(
        archive_path, "complete actual original passing V14 deep contract",
    )
    document, passed = state["v8"].validate_deep(
        raw, family, edge, state["snapshot"], contract,
    )
    require(
        passed is True and document.get("status") == "PASS"
        and document.get("checks") == original.DEEP_CHECKS
        and document.get("seeded_case_count") == original.DEEP_SEEDED_CASES
        and document.get("public_mismatch_count") == 0
        and document.get("candidate_sha256") == original.DEEP_REFERENCE_SHA256,
        "the unchanged complete original V14 393/64-case deep gate did not pass",
    )
    proof_raw = original.read_regular(
        proof_path, "complete actual original V14 deep owner proof",
    )
    proof = original.decode_json(proof_raw, "complete canonical V14 deep proof")
    require(original.canonical(proof) == proof_raw,
            "the complete V14 deep proof lost its actual canonical bytes")
    producer = _recorded_producer(proof)
    validate_durable_wrapper(
        proof, family, state, deep=True, passed=True,
        original_report=document, archive_path=archive_path,
        archive_sha256=hashlib.sha256(raw).hexdigest(),
        archive_bytes=len(raw),
        owner_before=proof.get("current_v13_native_owner_before"),
        owner_after=proof.get("current_v13_native_owner_after"),
        producer=producer, qualified_edge=qualified_edge,
    )
    summary = {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": archive_path.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
        "qualified_edge": qualified_edge,
    }
    return document, summary, raw, proof_raw


def _run_original(
    command: list[str],
) -> subprocess.CompletedProcess[bytes]:
    require(
        isinstance(command, list)
        and all(type(value) is str for value in command)
        and len(command) >= 5
        and command[0] == str(original.PINNED_EXECUTABLE)
        and command[1:3] == ["-I", "-B"],
        "only the unchanged pinned isolated original worker may execute",
    )
    producer = subprocess.run(
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
        isinstance(producer, subprocess.CompletedProcess)
        and producer.args == command
        and isinstance(producer.returncode, int)
        and isinstance(producer.stdout, bytes)
        and isinstance(producer.stderr, bytes)
        and len(producer.stdout) <= original.MAX_CHILD_OUTPUT_BYTES
        and len(producer.stderr) <= original.MAX_CHILD_OUTPUT_BYTES,
        "the original V14 worker lost its genuine bounded return or streams",
    )
    return producer


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
) -> ProofV14Failure:
    metadata = checked_family(family)
    timeout = isinstance(error, subprocess.TimeoutExpired)
    stdout = producer.stdout if producer is not None else getattr(error, "stdout", None)
    stderr = producer.stderr if producer is not None else getattr(error, "stderr", None)
    returncode = producer.returncode if producer is not None else None
    invalidated_path: str | None = None
    invalidated_sha256: str | None = None
    invalidated_status: str | None = None
    if completed_original is not None:
        require(
            isinstance(completed_original, bytes)
            and 0 < len(completed_original) <= original.MAX_FILE_BYTES,
            "refusing to manufacture a completed genuine V14 original archive",
        )
        invalidated = invalidated_target(family, deep=deep)
        invalidated_sha256 = original.exclusive_publish(
            invalidated, completed_original, deep=deep,
        )
        invalidated_path = invalidated.relative_to(ROOT).as_posix()
        invalidated_status = (
            "NOT VALIDATED" if validated_original is None
            else "PASS" if validated_original else "FAIL"
        )
    pins = validated_pins(state["audits"]["pins"])
    controller = state["controller"]
    publication_fields = failure_publication_fields(
        publication, family, deep=deep,
        original_raw=completed_original,
    )
    document = {
        "schema": SCHEMA + "-original-producer-failure",
        "status": "FAIL",
        "result": "FAIL",
        "mode": "qualified-deep" if deep else "qualified-edge",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "actual_invoking_controller": "V14",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_refresh_protocol_path": controller["protocol_path"],
        "actual_refresh_protocol_sha256": controller["protocol_sha256"],
        "actual_failure_error_type": type(error).__name__,
        "actual_failure_error_message": str(error),
        "actual_child_exit_code": returncode,
        "actual_child_signal": (
            -returncode if isinstance(returncode, int) and returncode < 0
            else None
        ),
        "timed_out": timeout,
        "timeout_seconds": 1800 if timeout else None,
        "actual_original_worker_command": (
            list(command) if command is not None else None
        ),
        "actual_verified_parent_environment":
            dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment": worker_environment(),
        "stdout": original.observed_stream(stdout, not timeout),
        "stderr": original.observed_stream(stderr, not timeout),
        "current_v13_native_owner_before": (
            dict(owner_before) if owner_before is not None else None
        ),
        "current_v13_native_owner_after": (
            dict(owner_after) if owner_after is not None else None
        ),
        "full_current_family_source_sha256":
            dict(state["snapshot"]["source_sha256_by_path"]),
        "full_current_family_native_elf_sha256":
            dict(state["snapshot"]["native_sha256_by_path"]),
        "all_family_audited_provenance": audited_graph_provenance(state),
        "actual_v13_audit_source_sha256": pins["audit_source"],
        "actual_v13_protocol_sha256": pins["audit_protocol"],
        "actual_v13_base_report_sha256": pins["base_report"],
        "actual_v13_strict_report_sha256": pins["strict_report"],
        "preserved_immutable_history": copy.deepcopy(state["history"]),
        "preserved_actual_failed_incidents":
            copy.deepcopy(state["preserved_incidents"]),
        "complete_original_observation_archive":
            completed_original is not None,
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_sha256,
        "invalidated_complete_original_actual_status": invalidated_status,
        **publication_fields,
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    payload = original.canonical(document)
    require(len(payload) <= original.MAX_FILE_BYTES,
            "the complete genuine V14 failure exceeded its frozen safe bound")
    raw = gzip.compress(payload, compresslevel=9, mtime=0)
    restored, actual_payload = state["v8"].decode_archive(
        raw, "complete original V14 producer or native-owner failure",
    )
    require(restored == document and actual_payload == payload,
            "the genuine V14 failure lost its full canonical evidence")
    path = failure_target(family, deep=deep)
    digest = original.exclusive_publish(path, raw, deep=deep)
    return ProofV14Failure(
        "the genuine original V14 worker or independent owner failed",
        {
            "status": "FAIL",
            "candidate_family": metadata["contract_name"],
            "candidate_module": metadata["module"],
            "failure_evidence_path": path.relative_to(ROOT).as_posix(),
            "failure_evidence_sha256": digest,
            "invalidated_complete_original_evidence_path": invalidated_path,
            "invalidated_complete_original_evidence_sha256":
                invalidated_sha256,
            "actual_child_exit_code": returncode,
            **publication_fields,
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
    archive_path = (
        deep_target(family, passed) if deep
        else edge_target(family, passed)
    )
    proof_path = (
        deep_proof_target(family, passed) if deep
        else edge_proof_target(family, passed)
    )
    archive_sha256 = record_exclusive_publication(
        publication, family, deep=deep, passed=passed,
        proof=False, path=archive_path, raw=raw,
    )
    preserved = original.read_regular(
        archive_path, "complete actual exclusively published V14 original",
    )
    require(
        preserved == raw and hashlib.sha256(preserved).hexdigest() == archive_sha256,
        "exclusive V14 publication changed genuine original observations",
    )
    if deep:
        require(isinstance(edge, Mapping),
                "a genuine deep original requires its current passing edge")
        final, final_passed = state["v8"].validate_deep(
            preserved, family, dict(edge), state["snapshot"], contract,
        )
    else:
        final, _, final_passed = state["v8"].validate_original_edge(
            preserved, archive_path, family, state["snapshot"], contract,
        )
    require(
        final == report and final_passed is passed,
        "the exclusive original V14 result changed or misrepresented a failure",
    )
    wrapper = build_durable_wrapper(
        family, state, deep=deep, passed=passed,
        original_report=final, archive_path=archive_path,
        archive_sha256=archive_sha256, archive_bytes=len(raw),
        owner_before=before, owner_after=after,
        producer=producer, qualified_edge=qualified_edge,
    )
    validate_durable_wrapper(
        wrapper, family, state, deep=deep, passed=passed,
        original_report=final, archive_path=archive_path,
        archive_sha256=archive_sha256, archive_bytes=len(raw),
        owner_before=before, owner_after=after,
        producer=producer, qualified_edge=qualified_edge,
    )
    wrapper_raw = original.canonical(wrapper)
    proof_sha256 = record_exclusive_publication(
        publication, family, deep=deep, passed=passed,
        proof=True, path=proof_path, raw=wrapper_raw,
    )
    actual_raw = original.read_regular(
        proof_path, "complete actual exclusively published V14 owner proof",
    )
    actual = original.decode_json(
        actual_raw, "complete canonical actual V14 archive-and-owner proof",
    )
    require(
        actual_raw == wrapper_raw
        and hashlib.sha256(actual_raw).hexdigest() == proof_sha256
        and original.canonical(actual) == actual_raw,
        "exclusive V14 owner evidence lost complete canonical original bytes",
    )
    validate_durable_wrapper(
        actual, family, state, deep=deep, passed=passed,
        original_report=final, archive_path=archive_path,
        archive_sha256=archive_sha256, archive_bytes=len(raw),
        owner_before=before, owner_after=after,
        producer=producer, qualified_edge=qualified_edge,
    )
    require(
        original.read_regular(
            archive_path, "complete rechecked immutable original V14 archive",
        ) == preserved,
        "a real V14 owner proof cannot qualify an altered original archive",
    )
    return {
        "schema": SCHEMA + (
            "-qualified-deep-durable-summary"
            if deep else "-qualified-edge-durable-summary"
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
        "public_mismatch_count": (
            final.get("public_mismatch_count") if deep else final.get("failed")
        ),
        "original_archive_path": archive_path.relative_to(ROOT).as_posix(),
        "original_archive_sha256": archive_sha256,
        "complete_owner_proof_path": proof_path.relative_to(ROOT).as_posix(),
        "complete_owner_proof_sha256": proof_sha256,
        "actual_v13_audit_source_sha256":
            state["audits"]["pins"]["audit_source"],
        "actual_v13_protocol_sha256":
            state["audits"]["pins"]["audit_protocol"],
        "actual_v13_base_report_sha256":
            state["audits"]["pins"]["base_report"],
        "actual_v13_strict_report_sha256":
            state["audits"]["pins"]["strict_report"],
        "stdout_is_not_durable_proof": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def refresh_edge(
    family: str, pins: Mapping[str, Any],
) -> dict[str, Any]:
    state = preflight(family, pins)
    preflight_fresh_destinations(family, deep=False)
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    producer: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    publication = new_publication_receipt(family, deep=False)
    try:
        before = observe_owner(
            family, state, stage="before-original-edge",
        )
        require(
            validate_current_graph(
                state["v13"], state["audits"], recheck=True,
            ) == state["audits"]["graph"],
            "the genuine V14 edge graph changed after its native owner",
        )
        with tempfile.TemporaryDirectory(
            prefix="rebar-v14-original-edge-" + family + "-", dir="/tmp",
        ) as directory:
            private = Path(directory).resolve()
            require(private.parent == Path("/tmp").resolve(),
                    "the genuine original V14 edge escaped its private root")
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
            producer = _run_original(command)
            require(
                temporary.is_file() and not temporary.is_symlink(),
                "the real original V14 edge returned no complete archive",
            )
            raw = original.read_regular(
                temporary, "complete actual original temporary V14 edge",
            )
            document, _, passed = state["v8"].validate_original_edge(
                raw, temporary, family, state["snapshot"], contract,
            )
            require(
                producer.returncode == int(not passed),
                "the genuine original V14 edge misrepresented its child status",
            )
            after = observe_owner(
                family, state, stage="after-original-edge",
            )
            refreshed = preflight(family, pins)
            require(
                refreshed["snapshot"] == state["snapshot"]
                and refreshed["audits"]["pins"] == state["audits"]["pins"]
                and refreshed["audits"]["graph"] == state["audits"]["graph"]
                and refreshed["history"] == state["history"]
                and refreshed["preserved_incidents"]
                == state["preserved_incidents"],
                "the actual V13 reports, current candidate, or history changed",
            )
            result = _publish_original_pair(
                family, state, deep=False, passed=passed,
                report=document, raw=raw, before=before, after=after,
                producer=producer, contract=contract,
                publication=publication,
            )
            return result
    except ProofV14Failure:
        raise
    except (
        AssertionError, OSError, ValueError, TypeError, KeyError,
        UnicodeError, subprocess.TimeoutExpired,
    ) as error:
        raise _preserve_failure(
            family, state, deep=False, error=error,
            owner_before=before, owner_after=after, producer=producer,
            completed_original=raw, validated_original=passed,
            command=command, publication=publication,
        ) from error


def refresh_deep(
    family: str, pins: Mapping[str, Any],
) -> dict[str, Any]:
    state = preflight(family, pins)
    preflight_fresh_destinations(family, deep=True)
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    edge, qualified_edge, edge_raw, edge_proof_raw = (
        authenticate_qualified_edge(family, state, contract)
    )
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    producer: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    publication = new_publication_receipt(family, deep=True)
    try:
        before = observe_owner(
            family, state, stage="before-original-deep",
        )
        require(
            validate_current_graph(
                state["v13"], state["audits"], recheck=True,
            ) == state["audits"]["graph"],
            "the current V13 owner changed before its original V14 deep worker",
        )
        with tempfile.TemporaryDirectory(
            prefix="rebar-v14-original-deep-" + family + "-", dir="/tmp",
        ) as directory:
            private = Path(directory).resolve()
            require(private.parent == Path("/tmp").resolve(),
                    "the original V14 deep worker escaped its private root")
            temporary = private / (
                "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
                + "-POSTFINAL-CURRENT-BUILD-V14-PRIVATE.json.gz"
            )
            command = [
                str(original.PINNED_EXECUTABLE), "-I", "-B", "-c",
                original.DEEP_LAUNCHER, str(ROOT), metadata["module"],
                str(edge_target(family, True)), str(temporary), str(private),
            ]
            producer = _run_original(command)
            require(
                temporary.is_file() and not temporary.is_symlink(),
                "the unchanged genuine V14 deep worker produced no archive",
            )
            raw = original.read_regular(
                temporary, "complete original actual temporary V14 deep",
            )
            document, passed = state["v8"].validate_deep(
                raw, family, edge, state["snapshot"], contract,
            )
            require(
                producer.returncode == int(not passed),
                "the complete original V14 deep worker concealed a real failure",
            )
            after = observe_owner(
                family, state, stage="after-original-deep",
            )
            refreshed = preflight(family, pins)
            require(
                refreshed["snapshot"] == state["snapshot"]
                and refreshed["audits"]["pins"] == state["audits"]["pins"]
                and refreshed["audits"]["graph"] == state["audits"]["graph"]
                and refreshed["history"] == state["history"]
                and refreshed["preserved_incidents"]
                == state["preserved_incidents"]
                and original.read_regular(
                    edge_target(family, True),
                    "complete rechecked original passing V14 edge",
                ) == edge_raw
                and original.read_regular(
                    edge_proof_target(family, True),
                    "complete rechecked V14 edge owner proof",
                ) == edge_proof_raw,
                "a real V14 original edge, current source, native ELF, "
                "V13 audit, or failure history changed",
            )
            result = _publish_original_pair(
                family, state, deep=True, passed=passed,
                report=document, raw=raw, before=before, after=after,
                producer=producer, contract=contract,
                publication=publication,
                qualified_edge=qualified_edge, edge=edge,
            )
            return result
    except ProofV14Failure:
        raise
    except (
        AssertionError, OSError, ValueError, TypeError, KeyError,
        UnicodeError, subprocess.TimeoutExpired,
    ) as error:
        raise _preserve_failure(
            family, state, deep=True, error=error,
            owner_before=before, owner_after=after, producer=producer,
            completed_original=raw, validated_original=passed,
            command=command, publication=publication,
        ) from error


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (
        ProofV14Error, original.ProofV11Error, legacy.ProofV12Error,
        AssertionError, OSError, ValueError, TypeError, KeyError, UnicodeError,
    ):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def _synthetic_source_state(
    family: str,
    source_sha256: str,
    synthetic_pins: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    pairs = {
        name: original.synthetic_durable_state(name, qualified=True)
        for name in FAMILIES
    }
    graph_sources = {
        name: pair[0]["snapshot"]["source_sha256_by_path"]
        for name, pair in pairs.items()
    }
    graph_native = {
        name: pair[0]["snapshot"]["native_sha256_by_path"]
        for name, pair in pairs.items()
    }
    graph = {
        "source_count": 12,
        "source_paths": [
            path for name in FAMILIES
            for path in original.FAMILIES[name]["sources"]
        ],
        "source_sha256_by_family": copy.deepcopy(graph_sources),
        "native_binary_count": 5,
        "native_sha256_by_family": copy.deepcopy(graph_native),
    }

    class SourceOnlyV13:
        CORE_FAMILIES = FAMILIES
        OWNED_SOURCE_PATHS = {
            name: original.FAMILIES[name]["sources"] for name in FAMILIES
        }
        OWNED_NATIVE_PATHS = {
            name: original.FAMILIES[name]["native"] for name in FAMILIES
        }

        @staticmethod
        def validate_native_owner(
            record: Mapping[str, Any],
            selected: str,
            expected: Mapping[str, str],
        ) -> dict[str, Any]:
            source_owner = pairs[selected][0]["owner"]
            return original.validate_owner(
                source_owner, record, selected, expected,
            )

        @staticmethod
        def snapshot_current_graph() -> dict[str, Any]:
            return copy.deepcopy(graph)

    saved, record = pairs[family]
    preserved = {
        "invalidated_path": ZIG_INVALIDATED_RELATIVE,
        "invalidated_sha256": ZIG_INVALIDATED_SHA256,
        "producer_failure_path": ZIG_FAILURE_RELATIVE,
        "producer_failure_sha256": ZIG_FAILURE_SHA256,
        "retry_failure_proof_path": ZIG_FAILURE_PROOF_RELATIVE,
        "retry_failure_proof_sha256": ZIG_FAILURE_PROOF_SHA256,
        "actual_child_exit_code": 1,
        "deep_checks": 393,
        "seeded_case_count": 64,
        "public_mismatch_count": 26,
        "public_mismatch_family_counts": dict(ZIG_FAILURE_COUNTS),
        "actual_reference_observation_sha256":
            original.DEEP_REFERENCE_SHA256,
        "actual_candidate_observation_sha256":
            original.synthetic_digest("v14-source-only-zig-observations"),
        "candidate_family": "ZIG",
        "qualifies_current_engine": False,
    }
    history = {
        "source_only": True,
        "first_rust_failure_sha256": legacy.PRIOR_FAILURE_SHA256,
        "first_rust_invalidated_sha256": legacy.PRIOR_INVALIDATED_SHA256,
    }
    audits = {
        "base": {"schema": V13_BASE_SCHEMA, "status": "PASS"},
        "strict": {"schema": V13_STRICT_SCHEMA, "status": "PASS"},
        "graph": graph,
        "pins": dict(synthetic_pins),
        "history": history,
        "preserved_zig_failure": preserved,
        "owner": saved["owner"],
    }
    return {
        "v13": SourceOnlyV13,
        "owner": saved["owner"],
        "v8": None,
        "audits": audits,
        "snapshot": saved["snapshot"],
        "history": history,
        "preserved_incidents": _validate_preserved_incidents(audits),
        "controller": {
            "source_path": SOURCE_RELATIVE,
            "source_sha256": source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": PROTOCOL_SHA256,
        },
        "parent_environment": {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        },
    }, record


def _synthetic_zig_failure_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for family, count in ZIG_FAILURE_COUNTS.items():
        for number in range(count):
            identity = (
                "seeded/" + format(number, "03d")
                + "/public-method-introspection/pattern-class/source-only-"
                + str(number)
                if family == "seeded/public-method-introspection"
                else "public-method-introspection/pattern-class/source-only-"
                + str(number)
            )
            common = {
                "name": "source-only-pattern-method-" + str(number),
                "callable": True,
            }
            rows.append({
                "id": identity,
                "family": family,
                "expected": {
                    **common,
                    "repr": {
                        "status": "value",
                        "value": "<method of re.Pattern objects>",
                    },
                },
                "actual": {
                    **common,
                    "repr": {
                        "status": "value",
                        "value": "<method of Pattern objects>",
                    },
                },
            })
    return {
        "status": "FAIL",
        "candidate_family": "ZIG",
        "candidate_module": "candidates.zig_candidate",
        "checks": original.DEEP_CHECKS,
        "seeded_case_count": original.DEEP_SEEDED_CASES,
        "reference_a_sha256": original.DEEP_REFERENCE_SHA256,
        "reference_b_sha256": original.DEEP_REFERENCE_SHA256,
        "public_mismatch_count": 26,
        "public_mismatch_family_counts": dict(ZIG_FAILURE_COUNTS),
        "public_mismatches": rows,
    }


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime_source_only()
    inherited = legacy.candidate_free_self_test()
    require(
        inherited.get("status") == "PASS"
        and inherited.get("candidate_imports") == 0
        and inherited.get("subprocesses") == 0
        and inherited.get("file_writes") == 0
        and inherited.get("clock_samples") == 0
        and inherited.get("historical_evidence_reads") == 0
        and inherited.get("actual_audit_report_reads") == 0
        and inherited.get("synthetic_results_qualify_candidates") is False
        and type(inherited.get("check_count")) is int
        and inherited["check_count"] >= 150,
        "the frozen original V12/V11 candidate-free boundary was weakened",
    )
    source_raw = original.read_regular(
        ROOT / SOURCE_RELATIVE, "complete V14 source-only controller",
    )
    protocol_raw = original.authenticate_frozen(
        PROTOCOL_RELATIVE, PROTOCOL_SHA256,
    )
    tree = ast.parse(source_raw.decode("utf-8"), filename=SOURCE_RELATIVE)
    source_sha256 = hashlib.sha256(source_raw).hexdigest()
    controls: list[dict[str, Any]] = []

    def accept(name: str, value: Any) -> None:
        controls.append({"name": name, "passed": bool(value)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        controls.append(rejected(name, action))

    with original.source_only_boundary() as effects:
        accept("parse-complete-fresh-additive-v14-source",
               isinstance(tree, ast.Module))
        accept("authenticate-exact-frozen-v14-protocol",
               hashlib.sha256(protocol_raw).hexdigest() == PROTOCOL_SHA256)
        accept("authenticate-exact-current-v14-controller",
               original.valid_sha256(source_sha256))
        accept("preserve-exact-single-dual-mode-v13-source",
               V13_SOURCE_RELATIVE
               == "tools/postfinal_independent_engine_audit_v13.py")
        accept("preserve-exact-single-dual-mode-v13-protocol",
               V13_PROTOCOL_RELATIVE
               == "oracle/cpython-3.14.6/"
                  "POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V13.md")
        accept("require-exact-four-independently-published-v13-pins",
               PIN_NAMES == (
                   "audit_source", "audit_protocol",
                   "base_report", "strict_report",
               ))
        accept("preserve-complete-original-edge-denominator",
               original.EDGE_CHECKS == 223198
               and original.EDGE_CATEGORIES == 49)
        accept("preserve-complete-original-deep-denominator",
               original.DEEP_CHECKS == 393
               and original.DEEP_SEEDED_CASES == 64)
        accept("preserve-all-three-independently-owned-families",
               FAMILIES == ("rust", "vm", "zig"))
        accept("preserve-all-twelve-original-owned-sources",
               sum(len(x["sources"])
                   for x in original.FAMILIES.values()) == 12)
        accept("preserve-all-five-independent-native-elf-files",
               sum(len(x["native"])
                   for x in original.FAMILIES.values()) == 5)
        for label, actual in (
            ("real-first-v11-rust-failure", legacy.PRIOR_FAILURE_SHA256),
            ("real-first-v11-rust-invalidated", legacy.PRIOR_INVALIDATED_SHA256),
            ("real-v12-zig-producer-failure", ZIG_FAILURE_SHA256),
            ("real-v12-zig-complete-failed-proof", ZIG_FAILURE_PROOF_SHA256),
            ("real-v12-zig-complete-failed-original", ZIG_INVALIDATED_SHA256),
        ):
            accept("preserve-independently-pinned-history:" + label,
                   original.valid_sha256(actual))
        required_calls = (
            "authenticate_qualified_audits",
            "snapshot_current_graph",
            "run_native_worker",
            "validate_native_owner",
            "validate_original_edge",
            "validate_deep",
            "exclusive_publish",
            "fresh_target",
            "restore_complete_stream",
            "source_only_boundary",
        )
        for name in required_calls:
            accept(
                "require-genuine-original-frozen-primitive:" + name,
                any(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == name
                    for node in ast.walk(tree)
                ),
            )
        prohibited_modules = {
            ".".join(("tools", "postfinal_from_scratch_audit_v13")),
            ".".join(("tools", "postfinal_no_delegation_audit_v13")),
        }
        for module in prohibited_modules:
            accept(
                "reject-nonexistent-dual-v13-controller:" + module,
                not any(
                    isinstance(node, ast.Constant)
                    and node.value == module
                    for node in ast.walk(tree)
                ),
            )
        pins = {
            name: original.synthetic_digest("v14-source-only-pin:" + name)
            for name in PIN_NAMES
        }
        accept("accept-four-distinct-source-only-v13-pins",
               validated_pins(pins) == pins)
        for key in PIN_NAMES:
            absent = dict(pins)
            del absent[key]
            reject(
                "reject-missing-actual-v13-pin:" + key,
                lambda value=absent: validated_pins(value),
            )
            for kind, changed in (
                ("none", None), ("empty", ""), ("integer", 1),
                ("short", "a" * 63), ("long", "a" * 65),
                ("uppercase", "A" * 64), ("nonhex", "g" * 64),
            ):
                broken = {**pins, key: changed}
                reject(
                    "reject-malformed-v13-pin:" + key + ":" + kind,
                    lambda value=broken: validated_pins(value),
                )
            for other in PIN_NAMES:
                if other != key:
                    repeated = {**pins, key: pins[other]}
                    reject(
                        "reject-reused-v13-source-or-report:"
                        + key + ":" + other,
                        lambda value=repeated: validated_pins(value),
                    )
        for value in (None, [], (), "fake", 1, {}):
            reject(
                "reject-nonmapping-v13-proof-pins:"
                + type(value).__name__,
                lambda item=value: validated_pins(item),
            )
        reject(
            "reject-additional-v13-proof-pin",
            lambda: validated_pins({**pins, "other_candidate": "a" * 64}),
        )
        parent = {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        }
        accept("accept-exact-source-only-parent", validate_parent_environment(
            parent,
        ) == parent)
        accept("retain-exact-five-key-real-original-worker-environment",
               set(worker_environment())
               == legacy.EXPLICIT_WORKER_ENVIRONMENT_KEYS)
        for key in parent:
            absent = dict(parent)
            del absent[key]
            reject(
                "reject-missing-real-parent:" + key,
                lambda value=absent: validate_parent_environment(value),
            )
            for name, value in (
                ("none", None), ("empty", ""), ("space", " "),
                ("integer", 1), ("changed", "wrong-v14-source-only-parent"),
            ):
                invalid = {**parent, key: value}
                reject(
                    "reject-invalid-real-parent:" + key + ":" + name,
                    lambda item=invalid: validate_parent_environment(item),
                )
        zig_original = _synthetic_zig_failure_report()
        verified_repr = validate_zig_pattern_mismatches(zig_original)
        accept(
            "validate-all-26-original-source-only-zig-pattern-representations",
            verified_repr == {
                "public_mismatch_count": 26,
                "public_mismatch_family_counts": dict(ZIG_FAILURE_COUNTS),
                "reference_pattern_name": "re.Pattern",
                "candidate_pattern_name": "Pattern",
                "all_original_representation_mismatches_verified": True,
            },
        )
        for key in (
            "status", "candidate_family", "candidate_module", "checks",
            "seeded_case_count", "reference_a_sha256",
            "reference_b_sha256", "public_mismatch_count",
            "public_mismatch_family_counts", "public_mismatches",
        ):
            poisoned = copy.deepcopy(zig_original)
            poisoned[key] = (
                None if poisoned[key] is not None else "source-only-poison"
            )
            reject(
                "reject-poisoned-complete-historical-zig-original:" + key,
                lambda value=poisoned: validate_zig_pattern_mismatches(value),
            )
        for family, expected in ZIG_FAILURE_COUNTS.items():
            for label, changed in (
                ("missing", None),
                ("under-count", expected - 1),
                ("over-count", expected + 1),
                ("string-count", str(expected)),
            ):
                poisoned = copy.deepcopy(zig_original)
                if changed is None:
                    del poisoned["public_mismatch_family_counts"][family]
                else:
                    poisoned["public_mismatch_family_counts"][family] = changed
                reject(
                    "reject-hidden-or-reclassified-zig-family:"
                    + family + ":" + label,
                    lambda value=poisoned:
                        validate_zig_pattern_mismatches(value),
                )
        for index in range(26):
            for label in (
                "missing-reference-repr",
                "missing-candidate-repr",
                "reclassified-family",
                "changed-nonrepr-observation",
                "duplicate-original-id",
            ):
                poisoned = copy.deepcopy(zig_original)
                row = poisoned["public_mismatches"][index]
                if label == "missing-reference-repr":
                    row["expected"]["repr"]["value"] = (
                        "<method of Pattern objects>"
                    )
                elif label == "missing-candidate-repr":
                    row["actual"]["repr"]["value"] = (
                        "<method of re.Pattern objects>"
                    )
                elif label == "reclassified-family":
                    row["family"] = "concealed-original-introspection"
                elif label == "changed-nonrepr-observation":
                    row["actual"]["callable"] = False
                else:
                    row["id"] = poisoned["public_mismatches"][
                        (index + 1) % 26
                    ]["id"]
                reject(
                    "reject-poisoned-individual-zig-public-repr:"
                    + str(index) + ":" + label,
                    lambda value=poisoned:
                        validate_zig_pattern_mismatches(value),
                )
        for family in FAMILIES:
            metadata = checked_family(family)
            accept(
                "preserve-complete-current-owned-source-denominator:" + family,
                len(metadata["sources"])
                == {"rust": 7, "vm": 2, "zig": 3}[family],
            )
            accept(
                "preserve-complete-current-native-elf-denominator:" + family,
                len(metadata["native"])
                == {"rust": 2, "vm": 1, "zig": 2}[family],
            )
            destinations = (
                edge_target(family, True), edge_target(family, False),
                edge_proof_target(family, True),
                edge_proof_target(family, False),
                failure_target(family, deep=False),
                invalidated_target(family, deep=False),
                deep_target(family, True), deep_target(family, False),
                deep_proof_target(family, True),
                deep_proof_target(family, False),
                failure_target(family, deep=True),
                invalidated_target(family, deep=True),
            )
            accept(
                "separate-all-twelve-additive-v14-destinations:" + family,
                len(set(destinations)) == 12,
            )
            for index, target in enumerate(destinations):
                accept(
                    "preserve-exclusive-version14-family-target:"
                    + family + ":" + str(index),
                    target.is_absolute()
                    and target.parent in {
                        ROOT / "candidates/evidence",
                        ROOT / "candidates/audits",
                    }
                    and "current-build-v14" in target.name.lower()
                    and target not in {
                        ROOT / legacy.PRIOR_FAILURE_RELATIVE,
                        ROOT / legacy.PRIOR_INVALIDATED_RELATIVE,
                        ROOT / ZIG_FAILURE_RELATIVE,
                        ROOT / ZIG_FAILURE_PROOF_RELATIVE,
                        ROOT / ZIG_INVALIDATED_RELATIVE,
                    },
                )
            state, record = _synthetic_source_state(
                family, source_sha256, pins,
            )
            accept(
                "validate-source-only-complete-current-v13-graph:" + family,
                validate_current_graph(
                    state["v13"], state["audits"], recheck=True,
                ) == state["audits"]["graph"],
            )
            accept(
                "validate-preserved-rust-and-zig-failures-without-reads:"
                + family,
                _validate_preserved_incidents(state["audits"])
                == state["preserved_incidents"],
            )
            for key in tuple(state["audits"]["preserved_zig_failure"]):
                changed_audits = copy.deepcopy(state["audits"])
                value = changed_audits["preserved_zig_failure"][key]
                changed_audits["preserved_zig_failure"][key] = (
                    None if value is not None else "source-only-history-poison"
                )
                reject(
                    "reject-tampered-complete-genuine-zig-history:"
                    + family + ":" + key,
                    lambda value=changed_audits:
                        _validate_preserved_incidents(value),
                )
            for deep in (False, True):
                mode = "deep" if deep else "edge"
                qualified = {
                    "status": "PASS", "campaign_qualified": True,
                    "archive_path": edge_target(family, True)
                        .relative_to(ROOT).as_posix(),
                    "archive_sha256":
                        original.synthetic_digest("v14-edge:" + family),
                    "proof_path": edge_proof_target(family, True)
                        .relative_to(ROOT).as_posix(),
                    "proof_sha256":
                        original.synthetic_digest("v14-edge-proof:" + family),
                }
                for passed in (False, True):
                    outcome = "pass" if passed else "fail"
                    report = ({
                        "candidate_sha256": (
                            original.DEEP_REFERENCE_SHA256 if passed
                            else original.synthetic_digest(
                                "v14-deep-real-failure:" + family,
                            )
                        ),
                        "public_mismatch_count": 0 if passed else 1,
                        "public_mismatch_family_counts": (
                            {} if passed else {"synthetic-source-only": 1}
                        ),
                    } if deep else {
                        "actual_sha256": (
                            original.EDGE_REFERENCE_SHA256 if passed
                            else original.synthetic_digest(
                                "v14-edge-real-failure:" + family,
                            )
                        ),
                        "failed": 0 if passed else 1,
                        "failures": [] if passed else [
                            {"source_only": True},
                        ],
                    })
                    raw = (
                        "source-only-original-v14:"
                        + family + ":" + mode + ":" + outcome
                    ).encode("ascii")
                    producer = subprocess.CompletedProcess(
                        args=["source-only-original-v14", family, mode],
                        returncode=int(not passed),
                        stdout=(
                            "source-only-stdout:" + family + ":" + mode
                        ).encode("ascii"),
                        stderr=b"",
                    )
                    archive = (
                        deep_target(family, passed)
                        if deep else edge_target(family, passed)
                    )
                    proof_path = (
                        deep_proof_target(family, passed)
                        if deep else edge_proof_target(family, passed)
                    )
                    publication = new_publication_receipt(
                        family, deep=deep,
                    )

                    def synthetic_publish(
                        path: Path,
                        payload: bytes,
                        *,
                        deep: bool,
                    ) -> str:
                        require(
                            isinstance(path, Path)
                            and isinstance(payload, bytes)
                            and type(deep) is bool,
                            "the source-only fake publisher lost its contract",
                        )
                        return hashlib.sha256(payload).hexdigest()

                    archive_digest = record_exclusive_publication(
                        publication, family, deep=deep, passed=passed,
                        proof=False, path=archive, raw=raw,
                        publisher=synthetic_publish,
                    )
                    partial_fields = failure_publication_fields(
                        publication, family, deep=deep, original_raw=raw,
                    )
                    accept(
                        "retain-archive-only-partial-publication:"
                        + family + ":" + mode + ":" + outcome,
                        partial_fields == {
                            "v14_original_archive_was_exclusively_published":
                                True,
                            "v14_original_archive_path":
                                archive.relative_to(ROOT).as_posix(),
                            "v14_original_archive_sha256": archive_digest,
                            "v14_owner_proof_was_exclusively_published":
                                False,
                            "v14_owner_proof_path": None,
                            "v14_owner_proof_sha256": None,
                            "unpaired_v14_original_archive_qualifies": False,
                        },
                    )

                    def failed_synthetic_publish(
                        path: Path,
                        payload: bytes,
                        *,
                        deep: bool,
                    ) -> str:
                        del path, payload, deep
                        raise ProofV14Error(
                            "source-only exact owner-proof publication failure"
                        )

                    archive_only = copy.deepcopy(publication)
                    reject(
                        "preserve-archive-receipt-when-proof-publisher-fails:"
                        + family + ":" + mode + ":" + outcome,
                        lambda saved=publication, selected=family,
                        selected_deep=deep, selected_passed=passed,
                        target=proof_path:
                            record_exclusive_publication(
                                saved, selected,
                                deep=selected_deep,
                                passed=selected_passed,
                                proof=True,
                                path=target,
                                raw=b"source-only-proof-publication-failure",
                                publisher=failed_synthetic_publish,
                            ),
                    )
                    accept(
                        "retain-truthful-archive-after-proof-write-failure:"
                        + family + ":" + mode + ":" + outcome,
                        publication == archive_only
                        and failure_publication_fields(
                            publication, family,
                            deep=deep, original_raw=raw,
                        ) == partial_fields,
                    )
                    for key in tuple(publication):
                        poisoned = copy.deepcopy(publication)
                        value = poisoned[key]
                        poisoned[key] = (
                            None if value is not None
                            else "source-only-partial-receipt-poison"
                        )
                        reject(
                            "reject-tampered-archive-only-receipt:"
                            + family + ":" + mode + ":" + outcome + ":" + key,
                            lambda item=poisoned, selected=family,
                            selected_deep=deep, saved_raw=raw:
                                failure_publication_fields(
                                    item, selected, deep=selected_deep,
                                    original_raw=saved_raw,
                                ),
                        )
                    proof_raw = (
                        "source-only-proof:" + family
                        + ":" + mode + ":" + outcome
                    ).encode("ascii")
                    proof_digest = record_exclusive_publication(
                        publication, family, deep=deep, passed=passed,
                        proof=True, path=proof_path, raw=proof_raw,
                        publisher=synthetic_publish,
                    )
                    complete_fields = failure_publication_fields(
                        publication, family,
                        deep=deep, original_raw=raw,
                    )
                    accept(
                        "retain-both-publications-after-post-proof-failure:"
                        + family + ":" + mode + ":" + outcome,
                        complete_fields == {
                            "v14_original_archive_was_exclusively_published":
                                True,
                            "v14_original_archive_path":
                                archive.relative_to(ROOT).as_posix(),
                            "v14_original_archive_sha256": archive_digest,
                            "v14_owner_proof_was_exclusively_published":
                                True,
                            "v14_owner_proof_path":
                                proof_path.relative_to(ROOT).as_posix(),
                            "v14_owner_proof_sha256": proof_digest,
                            "unpaired_v14_original_archive_qualifies": False,
                        },
                    )
                    reject(
                        "simulate-post-proof-integrity-failure:"
                        + family + ":" + mode + ":" + outcome,
                        lambda: require(
                            False,
                            "source-only post-proof integrity failure",
                        ),
                    )
                    accept(
                        "retain-both-truthful-receipts-after-post-validation:"
                        + family + ":" + mode + ":" + outcome,
                        failure_publication_fields(
                            publication, family,
                            deep=deep, original_raw=raw,
                        ) == complete_fields,
                    )
                    for key in tuple(publication):
                        poisoned = copy.deepcopy(publication)
                        value = poisoned[key]
                        poisoned[key] = (
                            None if value is not None
                            else "source-only-complete-receipt-poison"
                        )
                        reject(
                            "reject-tampered-both-published-receipt:"
                            + family + ":" + mode + ":" + outcome + ":" + key,
                            lambda item=poisoned, selected=family,
                            selected_deep=deep, saved_raw=raw:
                                failure_publication_fields(
                                    item, selected, deep=selected_deep,
                                    original_raw=saved_raw,
                                ),
                        )
                    wrapper = build_durable_wrapper(
                        family, state, deep=deep, passed=passed,
                        original_report=report,
                        archive_path=archive,
                        archive_sha256=hashlib.sha256(raw).hexdigest(),
                        archive_bytes=len(raw),
                        owner_before=record, owner_after=record,
                        producer=producer,
                        qualified_edge=qualified if deep else None,
                    )
                    validate_durable_wrapper(
                        wrapper, family, state, deep=deep, passed=passed,
                        original_report=report,
                        archive_path=archive,
                        archive_sha256=hashlib.sha256(raw).hexdigest(),
                        archive_bytes=len(raw),
                        owner_before=record, owner_after=record,
                        producer=producer,
                        qualified_edge=qualified if deep else None,
                    )
                    accept(
                        "validate-complete-source-only-original-owner:"
                        + family + ":" + mode + ":" + outcome,
                        wrapper["campaign_qualified"] is passed
                        and wrapper["actual_invoking_controller"] == "V14",
                    )
                    for key in tuple(wrapper):
                        changed = copy.deepcopy(wrapper)
                        value = changed[key]
                        changed[key] = (
                            None if value is not None
                            else "tampered-source-only-v14-proof"
                        )
                        reject(
                            "reject-tampered-full-durable-proof:"
                            + family + ":" + mode + ":" + outcome + ":" + key,
                            lambda document=changed, selected=family,
                            saved=state, selected_deep=deep,
                            selected_passed=passed, saved_report=report,
                            saved_path=archive,
                            saved_digest=hashlib.sha256(raw).hexdigest(),
                            saved_size=len(raw), saved_owner=record,
                            saved_process=producer,
                            saved_edge=qualified if deep else None:
                                validate_durable_wrapper(
                                    document, selected, saved,
                                    deep=selected_deep,
                                    passed=selected_passed,
                                    original_report=saved_report,
                                    archive_path=saved_path,
                                    archive_sha256=saved_digest,
                                    archive_bytes=saved_size,
                                    owner_before=saved_owner,
                                    owner_after=saved_owner,
                                    producer=saved_process,
                                    qualified_edge=saved_edge,
                                ),
                        )
            for broken in (None, {}, "rust", 1, []):
                reject(
                    "reject-substituted-all-family-owner-state:"
                    + family + ":" + type(broken).__name__,
                    lambda value=broken, saved=state:
                        validate_current_graph(saved["v13"], value, recheck=False),
                )
        for invalid in (None, "RUST", "c", "external", "", 1):
            reject(
                "reject-unowned-or-renamed-candidate:" + repr(invalid),
                lambda value=invalid: checked_family(value),
            )
        blocked = (
            ("candidate-import",
             lambda: builtins.__import__("candidates.rust_candidate")),
            ("foreign-engine-import",
             lambda: builtins.__import__("regex")),
            ("cross-candidate-import",
             lambda: importlib.import_module("candidates.zig_candidate")),
            ("external-engine-import",
             lambda: importlib.import_module("pcre2")),
            ("actual-v13-base-report",
             lambda: original.read_regular(
                 ROOT / V13_BASE_REPORT_RELATIVE,
                 "forbidden actual source-only V13 base",
             )),
            ("actual-v13-strict-report",
             lambda: original.read_regular(
                 ROOT / V13_STRICT_REPORT_RELATIVE,
                 "forbidden actual source-only V13 strict report",
             )),
            ("actual-v11-rust-first-failure",
             lambda: original.read_regular(
                 ROOT / legacy.PRIOR_FAILURE_RELATIVE,
                 "forbidden actual source-only Rust failure",
             )),
            ("actual-v12-zig-failure",
             lambda: original.read_regular(
                 ROOT / ZIG_FAILURE_RELATIVE,
                 "forbidden actual source-only Zig failure",
             )),
            ("actual-v14-edge",
             lambda: original.read_regular(
                 edge_target("rust", True),
                 "forbidden actual source-only V14 edge",
             )),
            ("actual-v14-deep",
             lambda: original.read_regular(
                 deep_target("zig", True),
                 "forbidden actual source-only V14 deep",
             )),
            ("holdout-read",
             lambda: builtins.open(
                 ROOT / "performance/holdout.json", "rb",
             )),
            ("unrelated-read",
             lambda: builtins.open(ROOT / "README.md", "rb")),
            ("wall-clock", lambda: time.time()),
            ("performance-clock", lambda: time.perf_counter()),
            ("original-subprocess",
             lambda: subprocess.run(["forbidden-v14-original-worker"])),
            ("native-owner-subprocess",
             lambda: subprocess.Popen(["forbidden-v14-native-owner"])),
            ("native-owner-thread",
             lambda: threading.Thread(target=lambda: None).start()),
            ("private-temporary-worker",
             lambda: tempfile.TemporaryDirectory()),
            ("v14-evidence-write",
             lambda: edge_proof_target("rust", True).write_bytes(b"forbidden")),
            ("v14-candidate-write",
             lambda: (ROOT / "candidates/forbidden-v14").write_text("x")),
        )
        for name, action in blocked:
            reject("actively-enforce-source-only-v14-boundary:" + name, action)
        accept(
            "actively-block-all-candidate-and-third-party-imports",
            effects["candidate_import_attempts_blocked"] >= 4,
        )
        accept(
            "actively-block-all-report-history-holdout-and-evidence-reads",
            effects["evidence_read_attempts_blocked"] >= 7,
        )
        accept(
            "actively-block-all-original-and-native-worker-processes",
            effects["worker_attempts_blocked"] >= 4,
        )
        accept(
            "actively-block-all-wall-and-benchmark-clocks",
            effects["clock_attempts_blocked"] >= 2,
        )
        accept(
            "actively-block-all-evidence-and-candidate-filesystem-writes",
            effects["write_attempts_blocked"] >= 2,
        )
        accept(
            "never-import-any-real-production-candidate",
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
        )
        accept(
            "never-import-absent-future-v13-during-source-only-controls",
            "tools.postfinal_independent_engine_audit_v13"
            not in sys.modules,
        )
        accept("retain-at-least-500-independent-v14-source-controls",
               len(controls) >= 500)
        require(
            len({entry["name"] for entry in controls}) == len(controls),
            "the independent V14 source-only control denominator was duplicated",
        )
        failed_controls = [
            entry["name"] for entry in controls if not entry["passed"]
        ]
        require(
            not failed_controls,
            "a genuine V14 source-only ownership, archive, or isolation control "
            "failed: " + ", ".join(failed_controls[:12]),
        )
        observed = dict(effects)
    verify_runtime_source_only()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "check_count": len(controls),
        "checks": controls,
        "inherited_v12_check_count": inherited["check_count"],
        "inherited_v12_source_only_status": inherited["status"],
        "inherited_v11_check_count": inherited["inherited_v11_check_count"],
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "historical_evidence_reads": 0,
        "actual_audit_report_reads": 0,
        "holdout_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "actual_v14_controller_sha256": source_sha256,
        "actual_v14_protocol_sha256": PROTOCOL_SHA256,
        "future_v13_source_hash_guessed": False,
        "future_v13_report_hash_guessed": False,
        "actual_first_v11_rust_failure_sha256":
            legacy.PRIOR_FAILURE_SHA256,
        "actual_first_v11_rust_invalidated_sha256":
            legacy.PRIOR_INVALIDATED_SHA256,
        "actual_v12_zig_failure_sha256": ZIG_FAILURE_SHA256,
        "actual_v12_zig_failure_proof_sha256": ZIG_FAILURE_PROOF_SHA256,
        "actual_v12_zig_invalidated_sha256": ZIG_INVALIDATED_SHA256,
        "original_edge_checks": original.EDGE_CHECKS,
        "original_edge_categories": original.EDGE_CATEGORIES,
        "original_deep_checks": original.DEEP_CHECKS,
        "original_deep_seeded_cases": original.DEEP_SEEDED_CASES,
        "independent_family_count": len(FAMILIES),
        "complete_owned_source_count": 12,
        "complete_native_elf_count": 5,
        "blocked_effect_attempts": observed,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--qualified-edge", action="store_true")
    modes.add_argument("--qualified-deep", action="store_true")
    parser.add_argument(
        "--module",
        choices=tuple(
            metadata["module"]
            for metadata in original.FAMILIES.values()
        ),
    )
    parser.add_argument("--v13-audit-source-sha256")
    parser.add_argument("--v13-audit-protocol-sha256")
    parser.add_argument("--v13-base-report-sha256")
    parser.add_argument("--v13-strict-report-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(
        sys.argv[1:] if arguments is None else arguments,
    )
    if options.self_test:
        require(
            options.module is None
            and all(getattr(options, name) is None for name in (
                "v13_audit_source_sha256",
                "v13_audit_protocol_sha256",
                "v13_base_report_sha256",
                "v13_strict_report_sha256",
            )),
            "a source-only V14 control cannot consume real candidate or audit pins",
        )
        result = candidate_free_self_test()
    else:
        require(
            isinstance(options.module, str),
            "an original V14 qualification requires its exact candidate family",
        )
        family = next(
            name for name, metadata in original.FAMILIES.items()
            if metadata["module"] == options.module
        )
        pins = validated_pins({
            "audit_source": options.v13_audit_source_sha256,
            "audit_protocol": options.v13_audit_protocol_sha256,
            "base_report": options.v13_base_report_sha256,
            "strict_report": options.v13_strict_report_sha256,
        })
        result = (
            refresh_edge(family, pins)
            if options.qualified_edge else refresh_deep(family, pins)
        )
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofV14Failure as failure:
        print(json.dumps(
            {
                "schema": SCHEMA + "-actual-worker-failure",
                **failure.evidence,
            },
            ensure_ascii=True, allow_nan=False, sort_keys=True,
        ))
        raise SystemExit(2) from failure
