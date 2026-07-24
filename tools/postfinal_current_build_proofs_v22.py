#!/usr/bin/env python3
"""Bind unchanged complete original correctness to independently proven V21."""

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

from tools import postfinal_current_build_proofs_v20 as reviewed


original = reviewed.original
legacy = reviewed.legacy
historical_v14 = reviewed.historical_v14
SCHEMA = "rebar-postfinal-current-build-proofs-v22"
SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v22.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V22.md"
PROTOCOL_SHA256 = (
    "e06a24155ca95bf287a5dece90d1a385dad806de8512f177d3146c7bba7acc29"
)
V20_SOURCE_SHA256 = (
    "1bef4ab40a55c38d196287175cfb94397eeffa62a50ffbdf84f297e66abadff4"
)
V20_PROTOCOL_SHA256 = (
    "52aea4b4ef48d8a8d1b72ccce447c1a9c620d1133adb9ce97986f6c1b503a4f0"
)
V21_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v21.py"
V21_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V21.md"
)
V21_SOURCE_SHA256 = (
    "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
)
V21_PROTOCOL_SHA256 = (
    "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
)
V21_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21.json"
)
V21_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21.json"
)
V21_SCHEMA = "rebar-postfinal-independent-engine-audit-v21"
V21_BASE_SCHEMA = "rebar-postfinal-from-scratch-audit-v21"
V21_STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v21"
PIN_NAMES = ("audit_source", "audit_protocol", "base_report", "strict_report")
FAMILIES = ("rust", "vm", "zig")
PURPOSES = ("archive", "proof", "invalidated", "failure")
RECEIPT_FIELDS = (
    *reviewed.RECEIPT_FIELDS,
    "canonical_document_expected",
    "canonical_document_validated",
)
V13_FAILURE_RELATIVE = reviewed.V13_FAILURE_RELATIVE
V13_FAILURE_SHA256 = reviewed.V13_FAILURE_SHA256
V15_FAILURE_RELATIVE = reviewed.V15_FAILURE_RELATIVE
V15_FAILURE_SHA256 = reviewed.V15_FAILURE_SHA256
V17_FAILURE_RELATIVE = reviewed.V17_FAILURE_RELATIVE
V17_FAILURE_SHA256 = reviewed.V17_FAILURE_SHA256
V19_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V19-PUBLICATION-FAILURE.json"
)
V19_FAILURE_SHA256 = (
    "6d4d73c153bcf1995db78fb4b90ce2851bdece3b13748c75ae045bd1081af390"
)
V19_FAILURE_SCHEMA = (
    "rebar-postfinal-independent-engine-audit-v19-"
    "actual-exclusive-publication-first-failure"
)
V19_DURABLE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V19.json"
)
V19_DURABLE_REPORT_SHA256 = (
    "e46484d4a8b389fde66131ac3f8c2db94b1a95ebbf35760f1602117e8c9f23c6"
)
V19_DURABLE_REPORT_BYTES = 161316
V19_OUTER_FAILURE_MESSAGE = (
    "the exclusive V19 publication failed; actual syscall receipt retained"
)
V19_INNER_FAILURE_MESSAGE = (
    "an exact exclusively published V19 all-family report was changed"
)
V19_EMPTY_STDERR_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
V19_WORKER_STDOUT = {
    "rust": (
        12108,
        "13f647d66cc48354f41ca643b5ff18d94bdccf86cb525aded821e16859b865ce",
    ),
    "vm": (
        11990,
        "82b444dccee6b61c5b9e41fa25d08cd5e086bb35946a01a6c4b25a473780cf38",
    ),
    "zig": (
        12096,
        "573c8b30a67657b63431f56c8e8f81826db09ffa39b0c70f19928d1d685a0b33",
    ),
}


class ProofV22Error(AssertionError):
    """Actual current ownership, original observations, or publication failed."""


class V22PublicationFailure(ProofV22Error):
    """Retain actual normalized bytes and every genuine syscall transition."""

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


class ProofV22Failure(ProofV22Error):
    """Expose only genuine independently preserved actual worker failures."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = copy.deepcopy(dict(evidence))


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ProofV22Error(message)


def verify_runtime_source_only() -> None:
    reviewed.verify_runtime_source_only()
    require(
        ROOT == original.ROOT
        and Path(__file__).resolve() == ROOT / SOURCE_RELATIVE
        and tuple(original.FAMILIES) == FAMILIES
        and original.EDGE_CHECKS == 223198
        and original.EDGE_CATEGORIES == 49
        and original.DEEP_CHECKS == 393
        and original.DEEP_SEEDED_CASES == 64
        and sum(len(item["sources"]) for item in original.FAMILIES.values()) == 12
        and sum(len(item["native"]) for item in original.FAMILIES.values()) == 5,
        "V22 requires all actual original 223198/49, 393/64 and 12/5 checks",
    )
    require(
        not any(
            name == "candidates"
            or name.startswith("candidates.")
            or name == "rebar"
            or name.startswith("rebar.")
            for name in sys.modules
        ),
        "a production candidate escaped into the V22 correctness controller",
    )


def validate_parent_environment(environment: Mapping[str, Any]) -> dict[str, str]:
    return reviewed.validate_parent_environment(environment)


def worker_environment() -> dict[str, str]:
    return reviewed.worker_environment()


def checked_family(family: str) -> dict[str, Any]:
    require(
        type(family) is str and family in FAMILIES,
        "only a genuine independently owned Rust, C, or Zig engine is allowed",
    )
    return original.checked_family(family)


def validated_pins(supplied: Any) -> dict[str, str]:
    require(
        isinstance(supplied, Mapping) and set(supplied) == set(PIN_NAMES),
        "BLOCKED: supply four actual independently published V21 audit hashes",
    )
    pins: dict[str, str] = {}
    for key in PIN_NAMES:
        value = supplied[key]
        require(
            original.valid_sha256(value),
            "BLOCKED: the actual independently published V21 "
            + key + " SHA-256 is required",
        )
        pins[key] = value
    require(
        len(set(pins.values())) == len(PIN_NAMES),
        "an actual V21 source, protocol, or independent report hash was reused",
    )
    return pins


def authenticate_controller() -> dict[str, str]:
    verify_runtime_source_only()
    prior = reviewed.authenticate_controller()
    require(
        prior.get("source_path") == reviewed.SOURCE_RELATIVE
        and prior.get("source_sha256") == V20_SOURCE_SHA256
        and prior.get("protocol_path") == reviewed.PROTOCOL_RELATIVE
        and prior.get("protocol_sha256") == V20_PROTOCOL_SHA256,
        "the immutable reviewed V20/V18/V14/V12/V11 source was changed",
    )
    source = original.read_regular(
        ROOT / SOURCE_RELATIVE,
        "complete independently frozen current V22 proof controller",
    )
    protocol = original.authenticate_frozen(
        PROTOCOL_RELATIVE,
        PROTOCOL_SHA256,
    )
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": hashlib.sha256(protocol).hexdigest(),
        "frozen_v20_source_path": reviewed.SOURCE_RELATIVE,
        "frozen_v20_source_sha256": V20_SOURCE_SHA256,
        "frozen_v20_protocol_path": reviewed.PROTOCOL_RELATIVE,
        "frozen_v20_protocol_sha256": V20_PROTOCOL_SHA256,
    }


def edge_target(family: str, passed: bool) -> Path:
    checked_family(family)
    require(type(passed) is bool,
            "a genuine complete original edge result must be boolean")
    result = "pass" if passed else "failures"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v22-qualified-" + result + ".json.gz"
    )


def edge_proof_target(family: str, passed: bool) -> Path:
    path = edge_target(family, passed)
    return path.parent / (
        path.name.removesuffix(".json.gz") + "-proof.json"
    )


def deep_target(family: str, passed: bool) -> Path:
    metadata = checked_family(family)
    require(type(passed) is bool,
            "a genuine complete original deep result must be boolean")
    result = "PASS" if passed else "FAILURES"
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V22-" + result + ".json.gz"
    )


def deep_proof_target(family: str, passed: bool) -> Path:
    path = deep_target(family, passed)
    return path.parent / (
        path.name.removesuffix(".json.gz") + "-PROOF.json"
    )


def failure_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool,
            "a genuine original worker failure needs its actual mode")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V22-PRODUCER-CRASH.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v22-qualified-producer-crash.json.gz"
    )


def invalidated_target(family: str, *, deep: bool) -> Path:
    metadata = checked_family(family)
    require(type(deep) is bool,
            "a genuine original invalidation needs its actual mode")
    if deep:
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V22-"
            "INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
        )
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v22-qualified-"
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
        "a V22 publication requires its actual family, mode, and purpose",
    )
    if purpose == "invalidated":
        return invalidated_target(family, deep=deep)
    if purpose == "failure":
        return failure_target(family, deep=deep)
    require(type(passed) is bool,
            "an original archive or owner proof cannot invent its result")
    if purpose == "archive":
        return deep_target(family, passed) if deep else edge_target(family, passed)
    return (
        deep_proof_target(family, passed)
        if deep else edge_proof_target(family, passed)
    )


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
        "the independently proven V21 audit omitted a current or history role",
    )
    graph = audits["graph"]
    require(
        isinstance(graph, dict)
        and set(graph) == {
            "source_count", "source_paths", "source_sha256_by_family",
            "native_binary_count", "native_sha256_by_family",
        }
        and graph.get("source_count") == 12
        and graph.get("native_binary_count") == 5
        and isinstance(graph.get("source_paths"), list)
        and len(graph["source_paths"]) == 12
        and len(set(graph["source_paths"])) == 12
        and isinstance(graph.get("source_sha256_by_family"), dict)
        and isinstance(graph.get("native_sha256_by_family"), dict)
        and set(graph["source_sha256_by_family"]) == set(FAMILIES)
        and set(graph["native_sha256_by_family"]) == set(FAMILIES),
        "the real V21 independently owned 12-source/five-native graph changed",
    )
    source_paths: list[str] = []
    for family in FAMILIES:
        metadata = checked_family(family)
        source = graph["source_sha256_by_family"][family]
        native = graph["native_sha256_by_family"][family]
        require(
            isinstance(source, dict)
            and tuple(source) == metadata["sources"]
            and all(original.valid_sha256(item) for item in source.values())
            and isinstance(native, dict)
            and set(native) == set(metadata["native"].values())
            and all(original.valid_sha256(item) for item in native.values())
            and tuple(v21.OWNED_SOURCE_PATHS[family]) == metadata["sources"]
            and dict(v21.OWNED_NATIVE_PATHS[family]) == metadata["native"],
            "a genuine independently owned V21 source or native ELF changed: "
            + family,
        )
        source_paths.extend(metadata["sources"])
    require(
        set(graph["source_paths"]) == set(source_paths)
        and sum(
            len(item)
            for item in graph["native_sha256_by_family"].values()
        ) == 5,
        "the actual current 12-source/five-native owner graph was shortened",
    )
    require(type(recheck) is bool,
            "a current read-only native source graph requires an explicit mode")
    if recheck:
        with v21.read_only_history_boundary() as effects:
            require(
                v21.read_only_current_graph() == graph,
                "an actual current V21 source or native binary changed",
            )
            require(
                isinstance(effects, Mapping)
                and all(value == 0 for value in effects.values()),
                "a V22 graph recheck started a worker or mutated state",
            )
    return graph


def expected_v13_failure_summary() -> dict[str, Any]:
    return reviewed.expected_v13_failure_summary()


def expected_v15_failure_summary() -> dict[str, Any]:
    return reviewed.expected_v15_failure_summary()


def expected_v17_failure_summary() -> dict[str, Any]:
    return reviewed.expected_v17_failure_summary()


def expected_v19_failure_summary() -> dict[str, Any]:
    workers = {
        family: {
            "actual_returncode": 0,
            "original_stdout_bytes": size,
            "original_stdout_sha256": digest,
            "complete_original_stdout_verified": True,
            "original_stderr_bytes": 0,
            "original_stderr_sha256": V19_EMPTY_STDERR_SHA256,
            "complete_original_stderr_verified": True,
            "matcher_guards": 13,
            "native_loader_guards": 5,
            "standard_pickle_checks": 16,
            "standard_pickle_failures": 0,
            "external_regex_packages": 0,
        }
        for family, (size, digest) in V19_WORKER_STDOUT.items()
    }
    return {
        "source_path": V19_FAILURE_RELATIVE,
        "sha256": V19_FAILURE_SHA256,
        "schema": V19_FAILURE_SCHEMA,
        "status": "FAIL",
        "exit_code": 1,
        "invocation_count": 1,
        "actual_error_message": V19_OUTER_FAILURE_MESSAGE,
        "actual_inner_error_message": V19_INNER_FAILURE_MESSAGE,
        "v19_source_path": reviewed.V19_SOURCE_RELATIVE,
        "v19_source_sha256": reviewed.V19_SOURCE_SHA256,
        "v19_protocol_path": reviewed.V19_PROTOCOL_RELATIVE,
        "v19_protocol_sha256": reviewed.V19_PROTOCOL_SHA256,
        "durable_report_path": V19_DURABLE_REPORT_RELATIVE,
        "durable_report_sha256": V19_DURABLE_REPORT_SHA256,
        "durable_report_bytes": V19_DURABLE_REPORT_BYTES,
        "durable_embedded_document_status": "PASS",
        "actual_controller_status": "FAIL",
        "canonical_report_bytes_independently_verified": True,
        "embedded_pass_qualifies_current_engine": False,
        "historical_failure_qualifies_current_build": False,
        "completed_native_owner_worker_count": 3,
        "complete_actual_native_owner_streams_preserved": True,
        "actual_original_native_owner_workers": workers,
        "exclusive_create_succeeded": True,
        "actual_bytes_written": V19_DURABLE_REPORT_BYTES,
        "file_fsync_succeeded": True,
        "parent_directory_fsync_succeeded": True,
        "canonical_reread_succeeded": False,
        "actual_write_calls": [{
            "requested_bytes": V19_DURABLE_REPORT_BYTES,
            "returned_bytes": V19_DURABLE_REPORT_BYTES,
        }],
        "original_non_roundtripping_in_memory_value":
            "NOT PRESERVED BY THE FAILED CONTROLLER",
        "fresh_v19_ownership_failure_report": False,
        "fresh_v19_strict_report": False,
        "fresh_v19_strict_failure_report": False,
        "strict_audit": "NOT RUN",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def validate_v13_failure_summary(value: Any) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and value == expected_v13_failure_summary()
        and reviewed.validate_v13_failure_summary(value) == value,
        "the genuine original failed V13 first invocation was forged",
    )
    return value


def validate_v15_failure_summary(value: Any) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and value == expected_v15_failure_summary()
        and reviewed.validate_v15_failure_summary(value) == value,
        "the genuine original failed V15 first invocation was forged",
    )
    return value


def validate_v17_failure_summary(value: Any) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and value == expected_v17_failure_summary()
        and reviewed.validate_v17_failure_summary(value) == value,
        "the genuine V17 three-worker failure was forged or falsely qualified",
    )
    return value


def validate_v19_failure_summary(value: Any) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and value == expected_v19_failure_summary(),
        "the genuine V19 canonical readback failure was forged or qualified",
    )
    return value


def validate_preserved_incidents(
    v21: Any,
    audits: Mapping[str, Any],
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
        "an actual V13/V15/V17/V19 historical owner failure was omitted",
    )
    validate_v13_failure_summary(actual_v13)
    validate_v15_failure_summary(actual_v15)
    validate_v17_failure_summary(actual_v17)
    validate_v19_failure_summary(actual_v19)
    require(
        history.get("preserved_zig_failure") == audits["preserved_zig_failure"]
        and v21.validate_zig_failure_summary(
            audits["preserved_zig_failure"],
        ) == audits["preserved_zig_failure"],
        "the genuine 26-case original historical Zig failure was replaced",
    )
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
        "historical_v10_graph_qualifies_current_engine": False,
    }


def preflight(family: str, pins: Mapping[str, Any]) -> dict[str, Any]:
    metadata = checked_family(family)
    actual = validated_pins(pins)
    require(
        original.valid_sha256(V21_SOURCE_SHA256)
        and original.valid_sha256(V21_PROTOCOL_SHA256)
        and actual["audit_source"] == V21_SOURCE_SHA256
        and actual["audit_protocol"] == V21_PROTOCOL_SHA256,
        "BLOCKED: use only the final independently reviewed actual V21 source "
        "and protocol; never guess an unreleased fingerprint",
    )
    verify_runtime_source_only()
    parent = validate_parent_environment(os.environ)
    controller = authenticate_controller()
    original.authenticate_frozen(
        V21_PROTOCOL_RELATIVE,
        actual["audit_protocol"],
    )
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
        and v21.PROTOCOL_SHA256 == actual["audit_protocol"]
        and v21.BASE_REPORT_RELATIVE == V21_BASE_REPORT_RELATIVE
        and v21.STRICT_REPORT_RELATIVE == V21_STRICT_REPORT_RELATIVE
        and v21.BASE_SCHEMA == V21_BASE_SCHEMA
        and v21.STRICT_SCHEMA == V21_STRICT_SCHEMA
        and tuple(v21.CORE_FAMILIES) == FAMILIES,
        "the independently reviewed actual current V21 native owner was replaced",
    )
    audits = v21.authenticate_qualified_audits(
        actual["base_report"],
        actual["strict_report"],
    )
    graph = validate_current_graph(
        v21,
        audits,
        recheck=True,
    )
    require(
        audits["pins"] == actual
        and audits["base"].get("schema") == V21_BASE_SCHEMA
        and audits["base"].get("status") == "PASS"
        and audits["strict"].get("schema") == V21_STRICT_SCHEMA
        and audits["strict"].get("status") == "PASS",
        "actual independent full V21 base and strict audit reports must pass",
    )
    preserved = validate_preserved_incidents(
        v21,
        audits,
    )
    v8 = original.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        original.V8_PROOF_RELATIVE,
        original.V8_PROOF_SHA256,
    )
    snapshot = {
        "family": family,
        "module": metadata["module"],
        "source_sha256_by_path":
            dict(graph["source_sha256_by_family"][family]),
        "native_sha256_by_path":
            dict(graph["native_sha256_by_family"][family]),
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
        and all(
            original.valid_sha256(value)
            for value in (*source.values(), *native.values())
        ),
        "the full independently proven V21 graph lost actual current binaries",
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
        "an actual independent V21 native owner requires its real stage",
    )
    expected = dict(state["snapshot"]["native_sha256_by_path"])
    actual = state["v21"].run_native_worker(
        family,
        expected,
    )
    validated = state["v21"].validate_native_owner(
        actual,
        family,
        expected,
    )
    require(
        isinstance(actual, dict)
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
        "the actual independent V21 before/after native owner failed: "
        + family + ":" + stage,
    )
    return actual


def preflight_fresh_destinations(family: str, *, deep: bool) -> None:
    checked_family(family)
    require(type(deep) is bool,
            "an actual full V22 original requires its explicit mode")
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
        and all(
            "current-build-v22" in destination.name.lower()
            for destination in destinations
        ),
        "V22 reused a historical original, engine, result, or owner proof",
    )
    for destination in destinations:
        original.fresh_target(destination, parent)


def normalize_publication_payload(
    payload: Any,
) -> tuple[bytes, dict[str, Any] | None]:
    document: dict[str, Any] | None = None
    if type(payload) is bytes:
        raw = payload
    elif type(payload) is dict:
        require(
            all(type(key) is str for key in payload),
            "an exact canonical V22 document cannot contain non-string keys",
        )
        try:
            raw = original.canonical(payload)
        except (
            AssertionError,
            TypeError,
            ValueError,
            OverflowError,
            UnicodeError,
        ) as error:
            raise ProofV22Error(
                "the exact complete V22 document is not canonical JSON",
            ) from error
        document = payload
    elif type(payload) is tuple:
        require(
            len(payload) == 2
            and type(payload[0]) is dict
            and type(payload[1]) is bytes
            and all(type(key) is str for key in payload[0]),
            "an exact V22 publication pair requires one document and raw bytes",
        )
        document, raw = payload
    else:
        raise ProofV22Error(
            "a V22 publisher accepts only raw bytes, a JSON object, "
            "or its exact document-and-bytes tuple",
        )
    require(
        type(raw) is bytes
        and 0 < len(raw) <= original.MAX_FILE_BYTES,
        "exact exclusive V22 canonical bytes must be complete and bounded",
    )
    if document is not None:
        restored = original.decode_json(
            raw,
            "complete strict unique-key canonical V22 publication payload",
        )
        try:
            canonical = original.canonical(document)
        except (
            AssertionError,
            TypeError,
            ValueError,
            OverflowError,
            UnicodeError,
        ) as error:
            raise ProofV22Error(
                "the exact V22 publication pair contains noncanonical JSON",
            ) from error
        require(
            restored == document
            and canonical == raw
            and original.canonical(restored) == raw,
            "an exclusive V22 canonical document and bytes do not round-trip",
        )
    return raw, document


def _empty_artifact(purpose: str) -> dict[str, Any]:
    require(purpose in PURPOSES,
            "a truthful V22 publication receipt invented an artifact role")
    return {
        "purpose": purpose,
        "path": None,
        "expected_bytes": None,
        "expected_sha256": None,
        "directory_opened": False,
        "directory_verified": False,
        "created": False,
        "bytes_written": 0,
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


def new_publication_receipt(family: str, *, deep: bool) -> dict[str, Any]:
    checked_family(family)
    require(type(deep) is bool,
            "an actual V22 original receipt requires its exact mode")
    return {
        "family": family,
        "deep": deep,
        "passed": None,
        "artifacts": {
            purpose: _empty_artifact(purpose)
            for purpose in PURPOSES
        },
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
        and set(receipt) == {"family", "deep", "passed", "artifacts"}
        and receipt["family"] == family
        and receipt["deep"] is deep
        and (receipt["passed"] is None or type(receipt["passed"]) is bool)
        and (passed is None or receipt["passed"] is passed)
        and isinstance(receipt["artifacts"], dict)
        and set(receipt["artifacts"]) == set(PURPOSES),
        "the complete actual syscall-accurate V22 receipt was falsified",
    )
    for purpose in PURPOSES:
        row = receipt["artifacts"][purpose]
        require(
            isinstance(row, dict)
            and set(row) == set(RECEIPT_FIELDS)
            and row.get("purpose") == purpose
            and all(
                type(row[key]) is bool
                for key in (
                    "directory_opened", "directory_verified", "created",
                    "write_complete", "file_fsynced", "file_closed",
                    "directory_fsynced", "directory_closed", "validated",
                    "canonical_document_expected",
                    "canonical_document_validated",
                )
            )
            and type(row["bytes_written"]) is int
            and row["bytes_written"] >= 0,
            "an actual V22 " + purpose + " syscall transition was forged",
        )
        if row["path"] is None:
            require(
                row["expected_bytes"] is None
                and row["expected_sha256"] is None
                and row["observed_sha256"] is None
                and row["bytes_written"] == 0
                and not any(
                    row[key]
                    for key in (
                        "directory_opened", "directory_verified", "created",
                        "write_complete", "file_fsynced", "file_closed",
                        "directory_fsynced", "directory_closed", "validated",
                        "canonical_document_expected",
                        "canonical_document_validated",
                    )
                ),
                "an unattempted V22 " + purpose + " claimed a real syscall",
            )
            continue
        expected = expected_publication_target(
            family,
            deep=deep,
            passed=receipt["passed"],
            purpose=purpose,
        )
        require(
            row["path"] == expected.relative_to(ROOT).as_posix()
            and type(row["expected_bytes"]) is int
            and 0 < row["expected_bytes"] <= original.MAX_FILE_BYTES
            and original.valid_sha256(row["expected_sha256"])
            and row["bytes_written"] <= row["expected_bytes"]
            and (
                row["observed_sha256"] is None
                or original.valid_sha256(row["observed_sha256"])
            )
            and (not row["directory_verified"] or row["directory_opened"])
            and (not row["created"] or row["directory_verified"])
            and (row["bytes_written"] == 0 or row["created"])
            and (
                row["write_complete"]
                == (row["bytes_written"] == row["expected_bytes"])
            )
            and (not row["file_fsynced"] or row["write_complete"])
            and (not row["file_closed"] or row["created"])
            and (
                not row["directory_fsynced"]
                or (row["file_fsynced"] and row["file_closed"])
            )
            and (not row["directory_closed"] or row["directory_opened"])
            and (
                row["observed_sha256"] is None
                or (row["directory_fsynced"] and row["directory_closed"])
            )
            and (
                not row["canonical_document_validated"]
                or (
                    row["canonical_document_expected"]
                    and row["observed_sha256"] == row["expected_sha256"]
                )
            )
            and (
                row["validated"] == (
                    row["observed_sha256"] == row["expected_sha256"]
                    and row["directory_fsynced"]
                    and row["directory_closed"]
                    and (
                        not row["canonical_document_expected"]
                        or row["canonical_document_validated"]
                    )
                )
            ),
            "a V22 " + purpose
            + " create, write, fsync, or canonical readback was misrepresented",
        )
        if purpose == "proof":
            require(
                receipt["artifacts"]["archive"]["validated"],
                "a canonical V22 proof started before its durable real archive",
            )
        if purpose == "archive" and original_raw is not None:
            require(
                type(original_raw) is bytes
                and len(original_raw) == row["expected_bytes"]
                and hashlib.sha256(original_raw).hexdigest()
                == row["expected_sha256"],
                "a complete original V22 receipt altered genuine worker bytes",
            )
    return receipt


class PublicationOps:
    """Own the real descriptor-relative, no-follow V22 exclusive publisher."""

    synthetic = False

    def check_target(self, path: Path, parent: Path) -> None:
        original.fresh_target(path, parent)

    def open_directory(self, parent: Path) -> int:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        flags |= getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        return os.open(parent, flags)

    def verify_directory(self, descriptor: int, parent: Path) -> None:
        observed = os.fstat(descriptor)
        expected = os.stat(parent, follow_symlinks=False)
        require(
            stat.S_ISDIR(observed.st_mode)
            and stat.S_ISDIR(expected.st_mode)
            and (observed.st_dev, observed.st_ino)
            == (expected.st_dev, expected.st_ino),
            "exclusive V22 publication lost its real directory identity",
        )

    def create(self, directory: int, name: str) -> int:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0)
        flags |= getattr(os, "O_CLOEXEC", 0)
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
        type(deep) is bool
        and purpose in PURPOSES
        and isinstance(path, Path),
        "an exclusive V22 artifact requires an actual exact mode and path",
    )
    raw, document = normalize_publication_payload(payload)
    validate_publication_receipt(
        receipt,
        family,
        deep=deep,
    )
    if purpose in ("archive", "proof"):
        require(type(passed) is bool,
                "a canonical V22 original cannot invent its actual outcome")
        if receipt["passed"] is None:
            receipt["passed"] = passed
        require(
            receipt["passed"] is passed,
            "a real original and owner proof changed their actual result",
        )
    expected = expected_publication_target(
        family,
        deep=deep,
        passed=receipt["passed"],
        purpose=purpose,
    )
    require(
        path == expected,
        "canonical exclusive V22 evidence escaped its exact target",
    )
    row = receipt["artifacts"][purpose]
    require(
        row == _empty_artifact(purpose),
        "a normalized exclusive V22 artifact was retried or overwritten",
    )
    if purpose == "proof":
        require(
            receipt["artifacts"]["archive"]["validated"],
            "an owner proof cannot precede its complete validated original",
        )
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
            count = ops.write(
                descriptor,
                view[row["bytes_written"]:],
            )
            require(
                type(count) is int
                and 0 < count <= len(raw) - row["bytes_written"],
                "a normalized V22 write returned zero or excessive bytes",
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
        saved = ops.read_regular(
            path,
            "complete normalized canonical exclusive V22 " + purpose,
        )
        require(
            type(saved) is bytes,
            "an exclusively published V22 artifact lost its genuine full bytes",
        )
        row["observed_sha256"] = hashlib.sha256(saved).hexdigest()
        require(
            saved == raw
            and row["observed_sha256"] == row["expected_sha256"],
            "a real normalized V22 reread changed complete canonical bytes",
        )
        if document is not None:
            stage = "canonical-readback"
            decoded = original.decode_json(
                saved,
                "complete strict canonical published V22 document",
            )
            require(
                decoded == document
                and original.canonical(decoded) == saved,
                "normalized V22 canonical document reread did not round-trip",
            )
            row["canonical_document_validated"] = True
        row["validated"] = True
    except (
        AssertionError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
    ) as error:
        failure = (stage, error)
    finally:
        for name, kind in (
            ("descriptor", "file"),
            ("directory", "directory"),
        ):
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
            except (
                AssertionError,
                OSError,
                ValueError,
                TypeError,
                KeyError,
            ) as error:
                if failure is None:
                    failure = (kind + "-cleanup-close", error)
    if failure is not None:
        stage, cause = failure
        raise V22PublicationFailure(
            "normalized exclusive V22 " + purpose
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
    checked = validate_publication_receipt(
        publication,
        family,
        deep=deep,
        original_raw=original_raw,
    )
    archive = checked["artifacts"]["archive"]
    proof = checked["artifacts"]["proof"]
    return {
        "v22_original_archive_path": archive["path"],
        "v22_original_archive_expected_sha256": archive["expected_sha256"],
        "v22_original_archive_observed_sha256": archive["observed_sha256"],
        "v22_original_archive_created": archive["created"],
        "v22_original_archive_bytes_written": archive["bytes_written"],
        "v22_original_archive_file_fsynced": archive["file_fsynced"],
        "v22_original_archive_directory_fsynced":
            archive["directory_fsynced"],
        "v22_original_archive_validated": archive["validated"],
        "v22_owner_proof_path": proof["path"],
        "v22_owner_proof_expected_sha256": proof["expected_sha256"],
        "v22_owner_proof_observed_sha256": proof["observed_sha256"],
        "v22_owner_proof_created": proof["created"],
        "v22_owner_proof_bytes_written": proof["bytes_written"],
        "v22_owner_proof_file_fsynced": proof["file_fsynced"],
        "v22_owner_proof_directory_fsynced":
            proof["directory_fsynced"],
        "v22_owner_proof_canonical_document_expected":
            proof["canonical_document_expected"],
        "v22_owner_proof_canonical_document_validated":
            proof["canonical_document_validated"],
        "v22_owner_proof_validated": proof["validated"],
        "v22_complete_syscall_publication_receipt":
            copy.deepcopy(checked),
        "unpaired_v22_original_archive_qualifies": False,
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
        and isinstance(producer.returncode, int)
        and type(producer.stdout) is bytes
        and type(producer.stderr) is bytes
        and len(producer.stdout) <= original.MAX_CHILD_OUTPUT_BYTES
        and len(producer.stderr) <= original.MAX_CHILD_OUTPUT_BYTES
        and isinstance(archive_path, Path)
        and original.valid_sha256(archive_sha256)
        and type(archive_bytes) is int
        and 0 < archive_bytes <= original.MAX_FILE_BYTES
        and isinstance(archive_receipt, Mapping),
        "a canonical V22 proof requires actual complete original observations",
    )
    target = deep_target(family, passed) if deep else edge_target(family, passed)
    proof = (
        deep_proof_target(family, passed)
        if deep else edge_proof_target(family, passed)
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
        "a canonical V22 proof cannot qualify an unfinished real archive",
    )
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
        "original_archive_publication_receipt":
            copy.deepcopy(dict(archive_receipt)),
        "publication_strategy":
            "v22-owned-normalized-canonical-directory-bound-syscall-receipts",
        "complete_original_producer_bytes_preserved": True,
        "original_archive_is_unmodified_original": True,
        "stdout_is_not_durable_proof": True,
        "original_worker_returncode": producer.returncode,
        "original_worker_stdout": original.observed_stream(
            producer.stdout,
            True,
        ),
        "original_worker_stderr": original.observed_stream(
            producer.stderr,
            True,
        ),
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
        "actual_invoking_controller": "V22",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_refresh_protocol_path": controller["protocol_path"],
        "actual_refresh_protocol_sha256": controller["protocol_sha256"],
        "actual_verified_parent_environment":
            dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment":
            worker_environment(),
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
            "public_mismatch_count":
                original_report.get("public_mismatch_count"),
            "public_mismatch_family_counts":
                original_report.get("public_mismatch_family_counts"),
            "qualified_edge": (
                dict(qualified_edge)
                if isinstance(qualified_edge, Mapping)
                else None
            ),
        })
    else:
        result.update({
            "seed": original.EDGE_SEED,
            "checks": original.EDGE_CHECKS,
            "category_count": original.EDGE_CATEGORIES,
            "reference_sha256": original.EDGE_REFERENCE_SHA256,
            "actual_sha256": original_report.get("actual_sha256"),
            "failure_count": original_report.get("failed"),
            "complete_failure_row_count":
                len(original_report.get("failures", [])),
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
        isinstance(document, dict)
        and document == expected
        and producer.returncode == int(not passed)
        and document["campaign_qualified"] is passed
        and document["candidate_module"] == metadata["module"]
        and document["stdout_is_not_durable_proof"] is True
        and document["production_observations_invented"] is False,
        "a canonical V22 proof changed actual owner or worker observations",
    )
    snapshot = state["snapshot"]
    require(
        snapshot.get("family") == family
        and snapshot.get("module") == metadata["module"]
        and set(snapshot.get("source_sha256_by_path", {}))
        == set(metadata["sources"])
        and set(snapshot.get("native_sha256_by_path", {}))
        == set(metadata["native"].values()),
        "a canonical V22 proof omitted a complete native or semantic source",
    )
    for phase, observation in (
        ("before", owner_before),
        ("after", owner_after),
    ):
        validated = state["v21"].validate_native_owner(
            observation,
            family,
            dict(snapshot["native_sha256_by_path"]),
        )
        require(
            isinstance(observation, Mapping)
            and (
                validated is observation
                or validated == observation
            )
            and observation.get("status") == "PASS"
            and observation.get("family") == family,
            "the actually completed V21 " + phase
            + " native owner was omitted",
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
            and original.valid_sha256(
                qualified_edge.get("archive_sha256"),
            )
            and original.valid_sha256(
                qualified_edge.get("proof_sha256"),
            ),
            "an actual V22 deep result requires its passing full V22 edge",
        )
    return document


def _recorded_producer(
    wrapper: Mapping[str, Any],
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(
        args=["durably-recorded-original-v22-worker"],
        returncode=wrapper.get("original_worker_returncode"),
        stdout=original.restore_complete_stream(
            wrapper.get("original_worker_stdout"),
            "complete actual frozen V22 original worker stdout",
        ),
        stderr=original.restore_complete_stream(
            wrapper.get("original_worker_stderr"),
            "complete actual frozen V22 original worker stderr",
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
    raw = original.read_regular(
        archive,
        "complete unchanged genuine passing V22 original edge",
    )
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
        "the complete original V22 edge did not pass every 223198/49 check",
    )
    proof_raw = original.read_regular(
        proof_path,
        "complete actual normalized V22 edge current-owner proof",
    )
    proof = original.decode_json(
        proof_raw,
        "complete strict canonical current-family V22 edge proof",
    )
    require(
        normalize_publication_payload(
            (proof, proof_raw),
        ) == (proof_raw, proof),
        "the complete V22 edge owner proof is not its canonical original bytes",
    )
    producer = _recorded_producer(proof)
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
        producer=producer,
        archive_receipt=proof.get("original_archive_publication_receipt"),
    )
    descriptor = {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": archive.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
    }
    return edge, descriptor, raw, proof_raw


def authenticate_qualified_deep(
    family: str,
    state: Mapping[str, Any],
    contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    edge, qualified_edge, _, _ = authenticate_qualified_edge(
        family,
        state,
        contract,
    )
    archive = deep_target(family, True)
    proof_path = deep_proof_target(family, True)
    raw = original.read_regular(
        archive,
        "complete unchanged original passing V22 deep observations",
    )
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
        and document.get("candidate_sha256")
        == original.DEEP_REFERENCE_SHA256,
        "the actual unchanged V22 original deep failed its 393/64 gate",
    )
    proof_raw = original.read_regular(
        proof_path,
        "complete canonical current-family passing V22 deep owner proof",
    )
    proof = original.decode_json(
        proof_raw,
        "complete strict canonical passing V22 deep owner proof",
    )
    require(
        normalize_publication_payload(
            (proof, proof_raw),
        ) == (proof_raw, proof),
        "the complete deep V22 proof changed exact canonical bytes",
    )
    producer = _recorded_producer(proof)
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
        producer=producer,
        archive_receipt=proof.get("original_archive_publication_receipt"),
        qualified_edge=qualified_edge,
    )
    descriptor = {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": archive.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
        "qualified_edge": qualified_edge,
    }
    return document, descriptor, raw, proof_raw


def _run_original(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    require(
        isinstance(command, list)
        and all(type(value) is str for value in command)
        and len(command) >= 5
        and command[0] == str(original.PINNED_EXECUTABLE)
        and command[1:3] == ["-I", "-B"],
        "only the complete pinned isolated original CPython worker may execute",
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
        and isinstance(result.returncode, int)
        and type(result.stdout) is bytes
        and type(result.stderr) is bytes
        and len(result.stdout) <= original.MAX_CHILD_OUTPUT_BYTES
        and len(result.stderr) <= original.MAX_CHILD_OUTPUT_BYTES,
        "the full original V22 worker lost actual exit or complete streams",
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
            "refusing to invent a genuine V22 native owner: " + phase,
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
) -> ProofV22Failure:
    metadata = checked_family(family)
    timed_out = isinstance(error, subprocess.TimeoutExpired)
    stdout = (
        producer.stdout
        if producer is not None
        else getattr(error, "stdout", None)
    )
    stderr = (
        producer.stderr
        if producer is not None
        else getattr(error, "stderr", None)
    )
    exit_code = producer.returncode if producer is not None else None
    invalidated_path: str | None = None
    invalidated_digest: str | None = None
    if completed_original is not None:
        require(
            type(completed_original) is bytes
            and 0 < len(completed_original) <= original.MAX_FILE_BYTES,
            "refusing to invent a real complete V22 original observation",
        )
        target = invalidated_target(
            family,
            deep=deep,
        )
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
    owners = captured_native_owner_records(
        family,
        owner_before,
        owner_after,
    )
    failure = {
        "schema": SCHEMA + "-original-producer-failure",
        "status": "FAIL",
        "result": "FAIL",
        "mode": "qualified-deep" if deep else "qualified-edge",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "actual_invoking_controller": "V22",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_refresh_protocol_path": controller["protocol_path"],
        "actual_refresh_protocol_sha256": controller["protocol_sha256"],
        "actual_failure_error_type": type(error).__name__,
        "actual_failure_error_message": str(error),
        "actual_publication_failure_stage": (
            error.stage
            if isinstance(error, V22PublicationFailure)
            else None
        ),
        "actual_child_exit_code": exit_code,
        "actual_child_signal": (
            -exit_code
            if isinstance(exit_code, int) and exit_code < 0
            else None
        ),
        "timed_out": timed_out,
        "timeout_seconds": 1800 if timed_out else None,
        "actual_original_worker_command": (
            list(command)
            if command is not None
            else None
        ),
        "actual_verified_parent_environment":
            dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment":
            worker_environment(),
        "stdout": original.observed_stream(
            stdout,
            not timed_out,
        ),
        "stderr": original.observed_stream(
            stderr,
            not timed_out,
        ),
        "current_v21_native_owner_before": (
            dict(owner_before)
            if owner_before is not None
            else None
        ),
        "current_v21_native_owner_after": (
            dict(owner_after)
            if owner_after is not None
            else None
        ),
        "actually_completed_native_owner_records":
            copy.deepcopy(owners),
        "actually_completed_native_owner_record_count":
            len(owners),
        "full_current_family_source_sha256":
            dict(state["snapshot"]["source_sha256_by_path"]),
        "full_current_family_native_elf_sha256":
            dict(state["snapshot"]["native_sha256_by_path"]),
        "all_family_audited_provenance":
            audited_graph_provenance(state),
        "actual_v21_audit_source_sha256": pins["audit_source"],
        "actual_v21_protocol_sha256": pins["audit_protocol"],
        "actual_v21_base_report_sha256": pins["base_report"],
        "actual_v21_strict_report_sha256": pins["strict_report"],
        "preserved_immutable_history": copy.deepcopy(state["history"]),
        "preserved_actual_failed_incidents":
            copy.deepcopy(state["preserved_incidents"]),
        "complete_original_observation_archive":
            completed_original is not None,
        "invalidated_complete_original_evidence_path":
            invalidated_path,
        "invalidated_complete_original_evidence_sha256":
            invalidated_digest,
        "invalidated_complete_original_actual_status": (
            None
            if completed_original is None
            else "NOT VALIDATED"
            if validated_original is None
            else "PASS"
            if validated_original
            else "FAIL"
        ),
        **fields,
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    normalized, document = normalize_publication_payload(
        failure,
    )
    require(
        document == failure,
        "a genuine V22 failure changed its canonical document",
    )
    compressed = gzip.compress(
        normalized,
        compresslevel=9,
        mtime=0,
    )
    restored, payload = state["v8"].decode_archive(
        compressed,
        "complete actual canonical original V22 owner or worker failure",
    )
    require(
        restored == failure
        and payload == normalized,
        "a genuine canonical V22 failure lost actual observations",
    )
    target = failure_target(
        family,
        deep=deep,
    )
    digest = publish_exclusive(
        publication,
        family,
        deep=deep,
        passed=publication["passed"],
        purpose="failure",
        path=target,
        payload=compressed,
    )
    return ProofV22Failure(
        "a genuine original V22 worker or independent native owner failed",
        {
            "status": "FAIL",
            "candidate_family": metadata["contract_name"],
            "candidate_module": metadata["module"],
            "failure_evidence_path":
                target.relative_to(ROOT).as_posix(),
            "failure_evidence_sha256": digest,
            "invalidated_complete_original_evidence_path":
                invalidated_path,
            "invalidated_complete_original_evidence_sha256":
                invalidated_digest,
            "actual_child_exit_code": exit_code,
            "actually_completed_native_owner_records":
                copy.deepcopy(owners),
            "actually_completed_native_owner_record_count":
                len(owners),
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
    archive = (
        deep_target(family, passed)
        if deep
        else edge_target(family, passed)
    )
    proof = (
        deep_proof_target(family, passed)
        if deep
        else edge_proof_target(family, passed)
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
    complete = original.read_regular(
        archive,
        "complete genuine exclusive original V22 correctness observations",
    )
    require(
        complete == raw
        and hashlib.sha256(complete).hexdigest() == archive_digest,
        "an actual V22 original archive changed complete worker observations",
    )
    if deep:
        require(
            isinstance(edge, Mapping),
            "an actual V22 original deep requires its passing actual edge",
        )
        verified, result = state["v8"].validate_deep(
            complete,
            family,
            dict(edge),
            state["snapshot"],
            contract,
        )
    else:
        verified, _, result = state["v8"].validate_original_edge(
            complete,
            archive,
            family,
            state["snapshot"],
            contract,
        )
    require(
        verified == report
        and result is passed,
        "a complete V22 original misrepresented its real correctness outcome",
    )
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
    proof_raw, document = normalize_publication_payload(
        wrapper,
    )
    require(
        document == wrapper,
        "the actual V22 native-owner proof lost its canonical document",
    )
    proof_digest = publish_exclusive(
        publication,
        family,
        deep=deep,
        passed=passed,
        purpose="proof",
        path=proof,
        payload=(wrapper, proof_raw),
    )
    saved = original.read_regular(
        proof,
        "complete actual normalized canonical V22 owner proof",
    )
    decoded = original.decode_json(
        saved,
        "complete strict normalized canonical V22 owner proof",
    )
    require(
        normalize_publication_payload(
            (decoded, saved),
        ) == (proof_raw, wrapper)
        and hashlib.sha256(saved).hexdigest() == proof_digest
        and publication["artifacts"]["proof"][
            "canonical_document_expected"
        ] is True
        and publication["artifacts"]["proof"][
            "canonical_document_validated"
        ] is True,
        "the complete canonical V22 owner proof failed actual round-trip",
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
        original.read_regular(
            archive,
            "complete final independently verified original V22 archive",
        ) == complete,
        "a normalized canonical V22 proof cannot certify a changed archive",
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
            "-qualified-deep-durable-summary"
            if deep
            else "-qualified-edge-durable-summary"
        ),
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL",
        "mode": "qualified-deep" if deep else "qualified-edge",
        "candidate_family": checked_family(family)["contract_name"],
        "candidate_module": checked_family(family)["module"],
        "campaign_qualified": passed,
        "checks":
            original.DEEP_CHECKS if deep else original.EDGE_CHECKS,
        "seeded_case_count":
            original.DEEP_SEEDED_CASES if deep else None,
        "category_count":
            None if deep else original.EDGE_CATEGORIES,
        "public_mismatch_count": (
            verified.get("public_mismatch_count")
            if deep
            else verified.get("failed")
        ),
        "original_archive_path":
            archive.relative_to(ROOT).as_posix(),
        "original_archive_sha256": archive_digest,
        "complete_owner_proof_path":
            proof.relative_to(ROOT).as_posix(),
        "complete_owner_proof_sha256": proof_digest,
        "complete_syscall_publication_receipt":
            copy.deepcopy(publication),
        "actual_v21_audit_source_sha256":
            state["audits"]["pins"]["audit_source"],
        "actual_v21_protocol_sha256":
            state["audits"]["pins"]["audit_protocol"],
        "actual_v21_base_report_sha256":
            state["audits"]["pins"]["base_report"],
        "actual_v21_strict_report_sha256":
            state["audits"]["pins"]["strict_report"],
        "canonical_document_bytes_normalized": True,
        "stdout_is_not_durable_proof": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def refresh_edge(family: str, pins: Mapping[str, Any]) -> dict[str, Any]:
    state = preflight(
        family,
        pins,
    )
    preflight_fresh_destinations(
        family,
        deep=False,
    )
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    process: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    receipt = new_publication_receipt(
        family,
        deep=False,
    )
    try:
        before = observe_owner(
            family,
            state,
            stage="before-original-edge",
        )
        validate_current_graph(
            state["v21"],
            state["audits"],
            recheck=True,
        )
        with tempfile.TemporaryDirectory(
            prefix="rebar-v22-original-edge-" + family + "-",
            dir="/tmp",
        ) as directory:
            private = Path(directory).resolve()
            require(
                private.parent == Path("/tmp").resolve(),
                "the complete original V22 edge escaped its isolated root",
            )
            temporary = private / "original-full-edge.json.gz"
            command = [
                str(original.PINNED_EXECUTABLE),
                "-I",
                "-B",
                str(ROOT / original.EDGE_SOURCE_RELATIVE),
                "--module",
                metadata["module"],
                "--seed",
                str(original.EDGE_SEED),
                "--seeded-cases",
                str(original.EDGE_SEEDED_CASES),
                "--unicode-stride",
                str(original.EDGE_UNICODE_STRIDE),
                "--output",
                str(temporary),
            ]
            process = _run_original(command)
            require(
                temporary.is_file() and not temporary.is_symlink(),
                "the original V22 edge worker produced no genuine archive",
            )
            raw = original.read_regular(
                temporary,
                "complete real private unchanged original V22 edge",
            )
            document, _, passed = state["v8"].validate_original_edge(
                raw,
                temporary,
                family,
                state["snapshot"],
                contract,
            )
            require(
                process.returncode == int(not passed),
                "the complete original V22 edge misrepresented its actual exit",
            )
            after = observe_owner(
                family,
                state,
                stage="after-original-edge",
            )
            validate_current_graph(
                state["v21"],
                state["audits"],
                recheck=True,
            )
            fresh = preflight(
                family,
                pins,
            )
            require(
                fresh["snapshot"] == state["snapshot"]
                and fresh["audits"]["pins"] == state["audits"]["pins"]
                and fresh["audits"]["graph"] == state["audits"]["graph"]
                and fresh["history"] == state["history"]
                and fresh["preserved_incidents"]
                == state["preserved_incidents"],
                "a genuine V21 current owner, binary, or real history changed",
            )
            return _publish_original_pair(
                family,
                state,
                deep=False,
                passed=passed,
                report=document,
                raw=raw,
                before=before,
                after=after,
                producer=process,
                contract=contract,
                publication=receipt,
            )
    except ProofV22Failure:
        raise
    except (
        AssertionError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
        subprocess.TimeoutExpired,
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
    state = preflight(
        family,
        pins,
    )
    preflight_fresh_destinations(
        family,
        deep=True,
    )
    metadata = checked_family(family)
    contract = state["v8"].load_contract()
    edge, qualified_edge, edge_raw, edge_proof_raw = (
        authenticate_qualified_edge(
            family,
            state,
            contract,
        )
    )
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    process: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    receipt = new_publication_receipt(
        family,
        deep=True,
    )
    try:
        before = observe_owner(
            family,
            state,
            stage="before-original-deep",
        )
        validate_current_graph(
            state["v21"],
            state["audits"],
            recheck=True,
        )
        with tempfile.TemporaryDirectory(
            prefix="rebar-v22-original-deep-" + family + "-",
            dir="/tmp",
        ) as directory:
            private = Path(directory).resolve()
            require(
                private.parent == Path("/tmp").resolve(),
                "the genuine original V22 deep escaped its private root",
            )
            temporary = private / (
                "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
                + "-POSTFINAL-CURRENT-BUILD-V22-PRIVATE.json.gz"
            )
            command = [
                str(original.PINNED_EXECUTABLE),
                "-I",
                "-B",
                "-c",
                original.DEEP_LAUNCHER,
                str(ROOT),
                metadata["module"],
                str(edge_target(family, True)),
                str(temporary),
                str(private),
            ]
            process = _run_original(command)
            require(
                temporary.is_file() and not temporary.is_symlink(),
                "the genuine original V22 deep worker produced no archive",
            )
            raw = original.read_regular(
                temporary,
                "complete private unchanged original V22 deep",
            )
            document, passed = state["v8"].validate_deep(
                raw,
                family,
                edge,
                state["snapshot"],
                contract,
            )
            require(
                process.returncode == int(not passed),
                "the genuine complete V22 deep worker concealed a failure",
            )
            after = observe_owner(
                family,
                state,
                stage="after-original-deep",
            )
            validate_current_graph(
                state["v21"],
                state["audits"],
                recheck=True,
            )
            fresh = preflight(
                family,
                pins,
            )
            require(
                fresh["snapshot"] == state["snapshot"]
                and fresh["audits"]["pins"] == state["audits"]["pins"]
                and fresh["audits"]["graph"] == state["audits"]["graph"]
                and fresh["history"] == state["history"]
                and fresh["preserved_incidents"]
                == state["preserved_incidents"]
                and original.read_regular(
                    edge_target(
                        family,
                        True,
                    ),
                    "complete independently rechecked actual V22 edge",
                ) == edge_raw
                and original.read_regular(
                    edge_proof_target(
                        family,
                        True,
                    ),
                    "complete independently rechecked V22 edge proof",
                ) == edge_proof_raw,
                "a genuine V22 edge, V21 current ELF, or real history changed",
            )
            return _publish_original_pair(
                family,
                state,
                deep=True,
                passed=passed,
                report=document,
                raw=raw,
                before=before,
                after=after,
                producer=process,
                contract=contract,
                publication=receipt,
                qualified_edge=qualified_edge,
                edge=edge,
            )
    except ProofV22Failure:
        raise
    except (
        AssertionError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
        subprocess.TimeoutExpired,
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


class SyntheticPublicationOps(reviewed.SyntheticPublicationOps):
    """Reuse only frozen pure-memory syscall doubles, never a real publisher."""


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (
        ProofV22Error,
        reviewed.ProofV20Error,
        reviewed.reviewed.ProofV18Error,
        historical_v14.ProofV14Error,
        original.ProofV11Error,
        legacy.ProofV12Error,
        AssertionError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
    ):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def _synthetic_state(
    family: str,
    source_digest: str,
    pins: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    prior, owner = reviewed._synthetic_state(
        family,
        original.synthetic_digest(
            "source-only-v22-immutable-reviewed-v20-source",
        ),
        pins,
    )
    graph = copy.deepcopy(prior["audits"]["graph"])

    class SourceOnlyV21:
        CORE_FAMILIES = FAMILIES
        OWNED_SOURCE_PATHS = {
            key: original.FAMILIES[key]["sources"]
            for key in FAMILIES
        }
        OWNED_NATIVE_PATHS = {
            key: original.FAMILIES[key]["native"]
            for key in FAMILIES
        }

        @staticmethod
        def validate_native_owner(
            record: Mapping[str, Any],
            selected: str,
            expected: Mapping[str, str],
        ) -> dict[str, Any]:
            return prior["v19"].validate_native_owner(
                record,
                selected,
                expected,
            )

        @staticmethod
        @contextlib.contextmanager
        def read_only_history_boundary() -> Any:
            yield {
                "candidate_imports": 0,
                "native_workers_started": 0,
                "subprocesses_started": 0,
                "filesystem_writes": 0,
                "clock_samples": 0,
                "holdout_reads": 0,
            }

        @staticmethod
        def read_only_current_graph() -> dict[str, Any]:
            return copy.deepcopy(graph)

    actual_v13 = expected_v13_failure_summary()
    actual_v15 = expected_v15_failure_summary()
    actual_v17 = expected_v17_failure_summary()
    actual_v19 = expected_v19_failure_summary()
    history = {
        **prior["history"],
        "preserved_v13_first_audit_failure":
            copy.deepcopy(actual_v13),
        "preserved_v15_first_audit_failure":
            copy.deepcopy(actual_v15),
        "preserved_v17_first_audit_failure":
            copy.deepcopy(actual_v17),
        "preserved_v19_first_audit_failure":
            copy.deepcopy(actual_v19),
    }
    audits = {
        "base": {"schema": V21_BASE_SCHEMA, "status": "PASS"},
        "strict": {"schema": V21_STRICT_SCHEMA, "status": "PASS"},
        "graph": graph,
        "pins": dict(pins),
        "history": history,
        "preserved_zig_failure":
            history["preserved_zig_failure"],
        "preserved_v13_failure": actual_v13,
        "preserved_v15_failure": actual_v15,
        "preserved_v17_failure": actual_v17,
        "preserved_v19_failure": actual_v19,
        "owner": prior["owner"],
    }
    incidents = {
        **prior["preserved_incidents"],
        "v19_first_owner_publication_failure":
            copy.deepcopy(actual_v19),
        "v19_first_owner_publication_failure_qualifies_current_engine":
            False,
    }
    return {
        "v21": SourceOnlyV21,
        "owner": prior["owner"],
        "v8": None,
        "audits": audits,
        "snapshot": prior["snapshot"],
        "history": history,
        "preserved_incidents": incidents,
        "controller": {
            "source_path": SOURCE_RELATIVE,
            "source_sha256": source_digest,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": PROTOCOL_SHA256,
            "frozen_v20_source_path": reviewed.SOURCE_RELATIVE,
            "frozen_v20_source_sha256": V20_SOURCE_SHA256,
            "frozen_v20_protocol_path": reviewed.PROTOCOL_RELATIVE,
            "frozen_v20_protocol_sha256": V20_PROTOCOL_SHA256,
        },
        "parent_environment": {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        },
    }, owner


def _poison(value: Any) -> Any:
    return reviewed._poison(value)


def _synthetic_report(
    family: str,
    *,
    deep: bool,
    passed: bool,
) -> dict[str, Any]:
    return reviewed._synthetic_report(
        family,
        deep=deep,
        passed=passed,
    )


def _check_fault_receipt(
    *,
    family: str,
    deep: bool,
    passed: bool,
    purpose: str,
    stage: str,
) -> bool:
    receipt = new_publication_receipt(
        family,
        deep=deep,
    )
    ops = SyntheticPublicationOps(
        fail_purpose=purpose,
        fail_stage=stage,
    )
    archive = (
        b"source-only-v22-complete-original:"
        + family.encode("ascii")
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
    if purpose == "archive":
        expected_raw = archive
        payload: Any = archive
    else:
        document = {
            "schema": SCHEMA + "-synthetic-source-only-proof",
            "family": family,
            "deep": deep,
            "passed": passed,
        }
        expected_raw = original.canonical(document)
        payload = (document, expected_raw)
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
    except V22PublicationFailure as failure:
        row = receipt["artifacts"][purpose]
        validate_publication_receipt(
            receipt,
            family,
            deep=deep,
            passed=passed,
            original_raw=archive if purpose == "proof" else None,
        )
        require(
            failure.receipt == receipt
            and failure.stage in {
                "target-validation", "directory-open", "directory-identity",
                "exclusive-create", "write", "file-fsync", "file-close",
                "directory-fsync", "directory-close", "readback",
                "canonical-readback", "file-cleanup-close",
                "directory-cleanup-close",
            }
            and row["path"] == target.relative_to(ROOT).as_posix()
            and row["expected_sha256"]
            == hashlib.sha256(expected_raw).hexdigest()
            and row["canonical_document_expected"] is (purpose == "proof"),
            "a normalized V22 actual failure lost its true exact syscall receipt",
        )
        if stage in ("target-validation", "directory-open"):
            require(
                not row["directory_verified"]
                and not row["created"],
                "a pre-creation failure invented a directory or file",
            )
        elif stage in ("directory-identity", "exclusive-create"):
            require(
                not row["created"],
                "a failed O_EXCL or directory identity fabricated a file",
            )
        elif stage in ("write", "zero-write", "excess-write"):
            require(
                row["created"]
                and row["bytes_written"] == 0
                and not row["file_fsynced"],
                "failure after O_EXCL hid an actually created empty file",
            )
        elif stage == "partial-write":
            require(
                row["created"]
                and row["bytes_written"] == 1
                and not row["write_complete"]
                and not row["file_fsynced"],
                "an interrupted V22 partial write lost actual bytes",
            )
        elif stage == "file-fsync":
            require(
                row["created"]
                and row["write_complete"]
                and not row["file_fsynced"]
                and not row["directory_fsynced"],
                "a failed V22 file fsync falsely claimed durability",
            )
        elif stage == "file-close":
            require(
                row["file_fsynced"]
                and not row["file_closed"]
                and not row["directory_fsynced"],
                "an actually failed V22 file close was retried",
            )
        elif stage == "directory-fsync":
            require(
                row["file_fsynced"]
                and row["file_closed"]
                and not row["directory_fsynced"]
                and not row["validated"],
                "failed directory fsync falsely qualified a V22 original",
            )
        elif stage == "directory-close":
            require(
                row["directory_fsynced"]
                and not row["directory_closed"]
                and not row["validated"],
                "a failed V22 directory close was retried or qualified",
            )
        elif stage == "readback":
            require(
                row["directory_fsynced"]
                and row["directory_closed"]
                and row["observed_sha256"] is None
                and not row["canonical_document_validated"]
                and not row["validated"],
                "a failed canonical V22 reread invented observed bytes",
            )
        elif stage == "readback-mismatch":
            require(
                row["directory_fsynced"]
                and row["directory_closed"]
                and original.valid_sha256(row["observed_sha256"])
                and row["observed_sha256"] != row["expected_sha256"]
                and not row["canonical_document_validated"]
                and not row["validated"],
                "a genuinely mismatching V22 readback was falsely qualified",
            )
        if purpose == "proof":
            require(
                receipt["artifacts"]["archive"]["validated"]
                and not row["validated"],
                "a failed canonical V22 proof qualified an unpaired archive",
            )
        return True
    return False


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime_source_only()
    inherited = reviewed.candidate_free_self_test()
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
        and inherited["check_count"] >= 2000,
        "the full reviewed V20/V18/V14/V12/V11 source boundary was weakened",
    )
    source = original.read_regular(
        ROOT / SOURCE_RELATIVE,
        "complete additive candidate-free current V22 source",
    )
    protocol = original.authenticate_frozen(
        PROTOCOL_RELATIVE,
        PROTOCOL_SHA256,
    )
    old_source = original.authenticate_frozen(
        reviewed.SOURCE_RELATIVE,
        V20_SOURCE_SHA256,
    )
    old_protocol = original.authenticate_frozen(
        reviewed.PROTOCOL_RELATIVE,
        V20_PROTOCOL_SHA256,
    )
    digest = hashlib.sha256(source).hexdigest()
    tree = ast.parse(
        source.decode("utf-8"),
        filename=SOURCE_RELATIVE,
    )
    controls: list[dict[str, Any]] = []

    def accept(name: str, passed: Any) -> None:
        controls.append({"name": name, "passed": bool(passed)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        controls.append(rejected(name, action))

    with original.source_only_boundary() as effects:
        accept(
            "parse-complete-independent-additive-v22-source",
            isinstance(tree, ast.Module),
        )
        accept(
            "verify-exact-frozen-additive-v22-protocol",
            hashlib.sha256(protocol).hexdigest() == PROTOCOL_SHA256,
        )
        accept(
            "preserve-exact-dual-reviewed-v20-controller",
            hashlib.sha256(old_source).hexdigest() == V20_SOURCE_SHA256,
        )
        accept(
            "preserve-exact-dual-reviewed-v20-protocol",
            hashlib.sha256(old_protocol).hexdigest() == V20_PROTOCOL_SHA256,
        )
        accept(
            "pin-only-actual-root-reviewed-v21-source",
            V21_SOURCE_SHA256
            == "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
            and original.valid_sha256(V21_SOURCE_SHA256),
        )
        accept(
            "pin-only-actual-root-reviewed-v21-protocol",
            V21_PROTOCOL_SHA256
            == "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
            and original.valid_sha256(V21_PROTOCOL_SHA256),
        )
        accept(
            "do-not-import-a-real-v21-owner-in-source-controls",
            "tools.postfinal_independent_engine_audit_v21"
            not in sys.modules,
        )
        accept(
            "preserve-all-original-223198-check-49-category-edge-cases",
            original.EDGE_CHECKS == 223198
            and original.EDGE_CATEGORIES == 49,
        )
        accept(
            "preserve-all-original-393-check-64-seed-deep-cases",
            original.DEEP_CHECKS == 393
            and original.DEEP_SEEDED_CASES == 64,
        )
        accept(
            "preserve-three-original-twelve-source-five-native-engines",
            FAMILIES == ("rust", "vm", "zig")
            and sum(
                len(original.FAMILIES[key]["sources"])
                for key in FAMILIES
            ) == 12
            and sum(
                len(original.FAMILIES[key]["native"])
                for key in FAMILIES
            ) == 5,
        )
        named = {
            item.name: item
            for item in tree.body
            if isinstance(item, (ast.FunctionDef, ast.ClassDef))
        }
        publisher = named.get("publish_exclusive")
        accept(
            "own-real-normalized-canonical-directory-bound-publisher",
            isinstance(publisher, ast.FunctionDef),
        )
        if isinstance(publisher, ast.FunctionDef):
            used = {
                node.func.attr
                for node in ast.walk(publisher)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
            }
            for operation in (
                "check_target",
                "open_directory",
                "verify_directory",
                "create",
                "write",
                "fsync",
                "close",
                "read_regular",
            ):
                accept(
                    "require-normalized-owned-exclusive-syscall:"
                    + operation,
                    operation in used,
                )
            accept(
                "normalize-document-bytes-before-exclusive-publication",
                any(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "normalize_publication_payload"
                    for node in ast.walk(publisher)
                ),
            )
        for role in (
            "normalize_publication_payload",
            "preflight",
            "validate_current_graph",
            "validate_preserved_incidents",
            "observe_owner",
            "captured_native_owner_records",
            "build_durable_wrapper",
            "validate_durable_wrapper",
            "authenticate_qualified_edge",
            "authenticate_qualified_deep",
            "refresh_edge",
            "refresh_deep",
        ):
            accept(
                "retain-complete-canonical-correctness-role:" + role,
                isinstance(named.get(role), ast.FunctionDef),
            )
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in (
                "exclusive_publish",
                "publish_exclusive",
            ):
                continue
            if not isinstance(node.func.value, ast.Name):
                continue
            accept(
                "reject-delegated-historical-exclusive-publisher:"
                + str(node.lineno) + ":" + str(node.col_offset),
                node.func.value.id not in (
                    "original",
                    "legacy",
                    "historical_v14",
                    "reviewed",
                ),
            )
        owner = named.get("observe_owner")
        if isinstance(owner, ast.FunctionDef):
            accept(
                "capture-owner-before-any-postflight-native-source-check",
                not any(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "validate_current_graph"
                    for node in ast.walk(owner)
                ),
            )
        current = named.get("validate_current_graph")
        if isinstance(current, ast.FunctionDef):
            calls = {
                node.func.attr
                for node in ast.walk(current)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
            }
            accept(
                "postflight-uses-only-effect-free-read-only-native-graph",
                "read_only_current_graph" in calls
                and "snapshot_current_graph" not in calls,
            )
            accept(
                "enforce-full-no-worker-postflight-read-only-boundary",
                "read_only_history_boundary" in calls,
            )
        for name in (
            "refresh_edge",
            "refresh_deep",
        ):
            function = named.get(name)
            if not isinstance(function, ast.FunctionDef):
                continue
            retained = [
                node
                for node in ast.walk(function)
                if isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name)
                    and target.id in ("before", "after")
                    for target in node.targets
                )
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "observe_owner"
            ]
            postflights = [
                node
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "validate_current_graph"
            ]
            accept(
                "retain-both-real-owners-before-pure-postflight:" + name,
                len(retained) == 2
                and len(postflights) >= 2,
            )
        document = {
            "schema": SCHEMA + "-synthetic-canonical-document",
            "status": "PASS",
            "nested": {
                "source_only": True,
                "ordered": [0, 1, 2],
            },
        }
        canonical = original.canonical(document)
        accept(
            "normalize-actual-complete-raw-original-bytes",
            normalize_publication_payload(
                b"source-only-v22-original",
            ) == (
                b"source-only-v22-original",
                None,
            ),
        )
        accept(
            "normalize-complete-strict-canonical-document",
            normalize_publication_payload(document)
            == (canonical, document),
        )
        accept(
            "normalize-complete-exact-document-and-bytes-tuple",
            normalize_publication_payload(
                (document, canonical),
            ) == (canonical, document),
        )
        malformed: tuple[tuple[str, Any], ...] = (
            ("none", None),
            ("empty-bytes", b""),
            ("text", "not-bytes"),
            ("integer", 1),
            ("float", 1.0),
            ("bytearray", bytearray(b"x")),
            ("memoryview", memoryview(b"x")),
            ("list", [document, canonical]),
            ("empty-tuple", ()),
            ("short-tuple", (document,)),
            ("long-tuple", (document, canonical, canonical)),
            ("nonmapping-tuple-document", ("not-a-document", canonical)),
            ("nonbytes-tuple-payload", (document, canonical.decode("ascii"))),
            ("mismatched-tuple-bytes", (document, canonical + b" ")),
            (
                "duplicate-json-keys",
                ({"value": 1}, b"{\"value\":1,\"value\":2}\n"),
            ),
            (
                "nonfinite-canonical-value",
                {"value": float("nan")},
            ),
            ("nonstring-canonical-key", {1: "forbidden"}),
            (
                "nested-nonstring-canonical-key",
                {"nested": {1: "forbidden"}},
            ),
        )
        for name, invalid in malformed:
            reject(
                "reject-malformed-normalized-canonical-payload:" + name,
                lambda payload=invalid:
                    normalize_publication_payload(payload),
            )
        reject(
            "reject-oversized-normalized-canonical-original",
            lambda: normalize_publication_payload(
                b"x" * (original.MAX_FILE_BYTES + 1),
            ),
        )
        pins = {
            name: original.synthetic_digest(
                "source-only-v22-external-v21-pin:" + name,
            )
            for name in PIN_NAMES
        }
        accept(
            "accept-exact-four-external-synthetic-v21-audit-pins",
            validated_pins(pins) == pins,
        )
        for key in PIN_NAMES:
            absent = dict(pins)
            del absent[key]
            reject(
                "reject-missing-actual-external-v21-pin:" + key,
                lambda value=absent: validated_pins(value),
            )
            for label, changed in (
                ("none", None),
                ("empty", ""),
                ("integer", 1),
                ("short", "a" * 63),
                ("long", "a" * 65),
                ("uppercase", "A" * 64),
                ("nonhex", "g" * 64),
            ):
                reject(
                    "reject-forged-external-v21-pin:"
                    + key + ":" + label,
                    lambda value={**pins, key: changed}:
                        validated_pins(value),
                )
            for other in PIN_NAMES:
                if key == other:
                    continue
                reject(
                    "reject-reused-real-source-or-report-fingerprint:"
                    + key + ":" + other,
                    lambda value={**pins, key: pins[other]}:
                        validated_pins(value),
                )
        for value in (
            None,
            [],
            (),
            "guessed-audit-pins",
            1,
            {},
        ):
            reject(
                "reject-nonmapping-v21-report-pins:" + type(value).__name__,
                lambda item=value: validated_pins(item),
            )
        reject(
            "reject-unauthorized-fifth-v21-report-pin",
            lambda: validated_pins({
                **pins,
                "other_candidate": original.synthetic_digest(
                    "source-only-v22-other-candidate",
                ),
            }),
        )
        for version, expected, validator in (
            (
                "v13",
                expected_v13_failure_summary(),
                validate_v13_failure_summary,
            ),
            (
                "v15",
                expected_v15_failure_summary(),
                validate_v15_failure_summary,
            ),
            (
                "v17",
                expected_v17_failure_summary(),
                validate_v17_failure_summary,
            ),
            (
                "v19",
                expected_v19_failure_summary(),
                validate_v19_failure_summary,
            ),
        ):
            accept(
                "retain-complete-genuine-original-audit-failure:" + version,
                validator(expected) == expected,
            )
            for field in tuple(expected):
                altered = copy.deepcopy(expected)
                altered[field] = _poison(altered[field])
                reject(
                    "reject-forged-actual-original-audit-failure:"
                    + version + ":" + field,
                    lambda value=altered, selected=validator:
                        selected(value),
                )
        incident = expected_v19_failure_summary()
        accept(
            "never-qualify-durable-internally-passing-v19-base",
            incident["durable_report_sha256"]
            == V19_DURABLE_REPORT_SHA256
            and incident["durable_report_bytes"] == 161316
            and incident["durable_embedded_document_status"] == "PASS"
            and incident["actual_controller_status"] == "FAIL"
            and incident["exit_code"] == 1
            and incident["embedded_pass_qualifies_current_engine"]
            is False
            and incident["canonical_reread_succeeded"] is False,
        )
        accept(
            "retain-all-three-real-v19-owner-streams",
            incident["completed_native_owner_worker_count"] == 3
            and incident["complete_actual_native_owner_streams_preserved"]
            is True
            and set(incident["actual_original_native_owner_workers"])
            == set(FAMILIES),
        )
        accept(
            "retain-all-eighteen-plus-eight-real-zig-representation-failures",
            historical_v14.validate_zig_pattern_mismatches(
                historical_v14._synthetic_zig_failure_report(),
            )["public_mismatch_family_counts"] == {
                "public-method-introspection": 18,
                "seeded/public-method-introspection": 8,
            },
        )
        parent = {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        }
        accept(
            "preserve-exact-real-isolated-original-parent",
            validate_parent_environment(parent) == parent,
        )
        accept(
            "preserve-exact-five-key-original-worker-environment",
            worker_environment() == {
                **parent,
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            },
        )
        for key in parent:
            changed = dict(parent)
            changed[key] = _poison(changed[key])
            reject(
                "reject-forged-original-worker-parent:" + key,
                lambda item=changed:
                    validate_parent_environment(item),
            )
        stages = (
            "target-validation",
            "directory-open",
            "directory-identity",
            "exclusive-create",
            "write",
            "zero-write",
            "excess-write",
            "partial-write",
            "file-fsync",
            "file-close",
            "directory-fsync",
            "directory-close",
            "readback",
            "readback-mismatch",
        )
        for family in FAMILIES:
            state, owner = _synthetic_state(
                family,
                digest,
                pins,
            )
            accept(
                "prove-full-synthetic-effect-free-current-graph:" + family,
                validate_current_graph(
                    state["v21"],
                    state["audits"],
                    recheck=True,
                ) == state["audits"]["graph"],
            )
            accept(
                "preserve-four-actual-immutable-audit-failures:" + family,
                state["preserved_incidents"][
                    "v13_first_owner_preflight_failure"
                ] == expected_v13_failure_summary()
                and state["preserved_incidents"][
                    "v15_first_owner_preflight_failure"
                ] == expected_v15_failure_summary()
                and state["preserved_incidents"][
                    "v17_first_owner_postflight_failure"
                ] == expected_v17_failure_summary()
                and state["preserved_incidents"][
                    "v19_first_owner_publication_failure"
                ] == expected_v19_failure_summary(),
            )
            accept(
                "preserve-actual-zero-completed-native-owners:" + family,
                captured_native_owner_records(
                    family,
                    None,
                    None,
                ) == {},
            )
            accept(
                "retain-actual-preflight-native-owner-before-recheck:"
                + family,
                captured_native_owner_records(
                    family,
                    owner,
                    None,
                ) == {
                    "before-original-worker": owner,
                },
            )
            accept(
                "retain-both-real-native-owners-before-recheck:"
                + family,
                captured_native_owner_records(
                    family,
                    owner,
                    owner,
                ) == {
                    "before-original-worker": owner,
                    "after-original-worker": owner,
                },
            )
            for key in tuple(state["audits"]["graph"]):
                altered = copy.deepcopy(state["audits"])
                altered["graph"][key] = _poison(
                    altered["graph"][key],
                )
                reject(
                    "reject-forged-complete-current-v21-graph:"
                    + family + ":" + key,
                    lambda value=altered, current=state["v21"]:
                        validate_current_graph(
                            current,
                            value,
                            recheck=False,
                        ),
                )
            for key in tuple(owner):
                altered_owner = copy.deepcopy(owner)
                altered_owner[key] = _poison(altered_owner[key])
                reject(
                    "reject-forged-genuine-current-native-owner:"
                    + family + ":" + key,
                    lambda value=altered_owner,
                    selected=family,
                    current=state["v21"],
                    binaries=dict(
                        state["snapshot"]["native_sha256_by_path"],
                    ):
                        current.validate_native_owner(
                            value,
                            selected,
                            binaries,
                        ),
                )
            for deep in (
                False,
                True,
            ):
                mode = "deep" if deep else "edge"
                for passed in (
                    False,
                    True,
                ):
                    outcome = "pass" if passed else "fail"
                    label = family + ":" + mode + ":" + outcome
                    archive_raw = (
                        "source-only-complete-v22-original:" + label
                    ).encode("ascii")
                    proof_document = {
                        "schema": SCHEMA + "-synthetic-native-owner",
                        "family": family,
                        "mode": mode,
                        "passed": passed,
                        "source_only": True,
                    }
                    proof_raw = original.canonical(proof_document)
                    receipt = new_publication_receipt(
                        family,
                        deep=deep,
                    )
                    accept(
                        "validate-empty-normalized-exclusive-receipt:" + label,
                        validate_publication_receipt(
                            receipt,
                            family,
                            deep=deep,
                        ) == receipt,
                    )
                    operations = SyntheticPublicationOps(
                        fail_purpose="archive",
                        fail_stage="partial-success",
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
                    accept(
                        "retain-every-real-single-byte-original-write:" + label,
                        archive_digest
                        == hashlib.sha256(archive_raw).hexdigest()
                        and receipt["artifacts"]["archive"][
                            "bytes_written"
                        ] == len(archive_raw)
                        and receipt["artifacts"]["archive"][
                            "canonical_document_expected"
                        ] is False
                        and receipt["artifacts"]["archive"][
                            "validated"
                        ] is True
                        and operations.write_calls == len(archive_raw),
                    )
                    report = _synthetic_report(
                        family,
                        deep=deep,
                        passed=passed,
                    )
                    process = subprocess.CompletedProcess(
                        args=[
                            "source-only-original-v22",
                            family,
                            mode,
                        ],
                        returncode=int(not passed),
                        stdout=(
                            "source-only-v22-genuine-stdout:" + label
                        ).encode("ascii"),
                        stderr=(
                            "source-only-v22-genuine-stderr:" + label
                        ).encode("ascii"),
                    )
                    edge = {
                        "status": "PASS",
                        "campaign_qualified": True,
                        "archive_path":
                            edge_target(
                                family,
                                True,
                            ).relative_to(ROOT).as_posix(),
                        "archive_sha256":
                            original.synthetic_digest(
                                "source-only-v22-passing-edge:" + family,
                            ),
                        "proof_path":
                            edge_proof_target(
                                family,
                                True,
                            ).relative_to(ROOT).as_posix(),
                        "proof_sha256":
                            original.synthetic_digest(
                                "source-only-v22-passing-proof:" + family,
                            ),
                    }
                    archived = receipt["artifacts"]["archive"]
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
                        producer=process,
                        archive_receipt=archived,
                        qualified_edge=edge if deep else None,
                    )
                    validate_durable_wrapper(
                        wrapper,
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
                        producer=process,
                        archive_receipt=archived,
                        qualified_edge=edge if deep else None,
                    )
                    accept(
                        "validate-full-canonical-current-owner-proof:"
                        + label,
                        wrapper["actual_invoking_controller"] == "V22"
                        and wrapper["campaign_qualified"] is passed,
                    )
                    for key in tuple(wrapper):
                        altered = copy.deepcopy(wrapper)
                        altered[key] = _poison(altered[key])
                        reject(
                            "reject-forged-complete-normalized-owner-proof:"
                            + label + ":" + key,
                            lambda document=altered,
                            selected=family,
                            saved=state,
                            selected_deep=deep,
                            selected_passed=passed,
                            selected_report=report,
                            selected_archive=archive_path,
                            selected_digest=archive_digest,
                            selected_raw=archive_raw,
                            selected_owner=owner,
                            selected_process=process,
                            selected_receipt=copy.deepcopy(archived),
                            selected_edge=edge if deep else None:
                                validate_durable_wrapper(
                                    document,
                                    selected,
                                    saved,
                                    deep=selected_deep,
                                    passed=selected_passed,
                                    original_report=selected_report,
                                    archive_path=selected_archive,
                                    archive_sha256=selected_digest,
                                    archive_bytes=len(selected_raw),
                                    owner_before=selected_owner,
                                    owner_after=selected_owner,
                                    producer=selected_process,
                                    archive_receipt=selected_receipt,
                                    qualified_edge=selected_edge,
                                ),
                        )
                    operations.fail_purpose = "proof"
                    operations.fail_stage = "partial-success"
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
                    accept(
                        "prove-exact-normalized-canonical-proof-pair:"
                        + label,
                        proof_digest
                        == hashlib.sha256(proof_raw).hexdigest()
                        and receipt["artifacts"]["archive"][
                            "validated"
                        ] is True
                        and receipt["artifacts"]["proof"][
                            "canonical_document_expected"
                        ] is True
                        and receipt["artifacts"]["proof"][
                            "canonical_document_validated"
                        ] is True
                        and receipt["artifacts"]["proof"][
                            "validated"
                        ] is True,
                    )
                    fields = failure_publication_fields(
                        receipt,
                        family,
                        deep=deep,
                        original_raw=archive_raw,
                    )
                    accept(
                        "preserve-complete-normalized-native-owner-receipts:"
                        + label,
                        fields["v22_original_archive_validated"]
                        and fields["v22_owner_proof_validated"]
                        and fields[
                            "v22_owner_proof_canonical_document_validated"
                        ]
                        and not fields[
                            "unpaired_v22_original_archive_qualifies"
                        ],
                    )
                    for purpose in PURPOSES:
                        for key in RECEIPT_FIELDS:
                            poisoned = copy.deepcopy(receipt)
                            poisoned["artifacts"][purpose][key] = _poison(
                                poisoned["artifacts"][purpose][key],
                            )
                            reject(
                                "reject-forged-canonical-partial-syscall:"
                                + label + ":" + purpose + ":" + key,
                                lambda item=poisoned,
                                selected=family,
                                selected_deep=deep,
                                selected_passed=passed,
                                selected_raw=archive_raw:
                                    validate_publication_receipt(
                                        item,
                                        selected,
                                        deep=selected_deep,
                                        passed=selected_passed,
                                        original_raw=selected_raw,
                                    ),
                            )
                    for purpose in (
                        "archive",
                        "proof",
                    ):
                        for stage in stages:
                            accept(
                                "retain-actual-normalized-failed-syscall:"
                                + label + ":" + purpose + ":" + stage,
                                _check_fault_receipt(
                                    family=family,
                                    deep=deep,
                                    passed=passed,
                                    purpose=purpose,
                                    stage=stage,
                                ),
                            )
                    unpaired = new_publication_receipt(
                        family,
                        deep=deep,
                    )
                    reject(
                        "reject-normalized-proof-before-actual-original:"
                        + label,
                        lambda item=unpaired,
                        selected=family,
                        selected_deep=deep,
                        selected_passed=passed,
                        target=proof_path,
                        selected_document=proof_document,
                        selected_raw=proof_raw:
                            publish_exclusive(
                                item,
                                selected,
                                deep=selected_deep,
                                passed=selected_passed,
                                purpose="proof",
                                path=target,
                                payload=(
                                    selected_document,
                                    selected_raw,
                                ),
                                operations=SyntheticPublicationOps(),
                            ),
                    )
                    reject(
                        "reject-repeated-canonical-original-publication:"
                        + label,
                        lambda item=receipt,
                        selected=family,
                        selected_deep=deep,
                        selected_passed=passed,
                        target=archive_path,
                        payload=archive_raw,
                        selected_ops=operations:
                            publish_exclusive(
                                item,
                                selected,
                                deep=selected_deep,
                                passed=selected_passed,
                                purpose="archive",
                                path=target,
                                payload=payload,
                                operations=selected_ops,
                            ),
                    )
        blocked = (
            (
                "actual-v21-source",
                lambda: original.read_regular(
                    ROOT / V21_SOURCE_RELATIVE,
                    "forbidden actual source-only V21 controller",
                ),
            ),
            (
                "actual-v21-base",
                lambda: original.read_regular(
                    ROOT / V21_BASE_REPORT_RELATIVE,
                    "forbidden actual source-only V21 base report",
                ),
            ),
            (
                "actual-v21-strict",
                lambda: original.read_regular(
                    ROOT / V21_STRICT_REPORT_RELATIVE,
                    "forbidden actual source-only V21 strict report",
                ),
            ),
            (
                "actual-v13-failure",
                lambda: original.read_regular(
                    ROOT / V13_FAILURE_RELATIVE,
                    "forbidden actual V13 source-only failure",
                ),
            ),
            (
                "actual-v15-failure",
                lambda: original.read_regular(
                    ROOT / V15_FAILURE_RELATIVE,
                    "forbidden actual V15 source-only failure",
                ),
            ),
            (
                "actual-v17-failure",
                lambda: original.read_regular(
                    ROOT / V17_FAILURE_RELATIVE,
                    "forbidden actual V17 source-only failure",
                ),
            ),
            (
                "actual-v19-failure",
                lambda: original.read_regular(
                    ROOT / V19_FAILURE_RELATIVE,
                    "forbidden actual V19 source-only failure",
                ),
            ),
            (
                "actual-v19-unqualified-base",
                lambda: original.read_regular(
                    ROOT / V19_DURABLE_REPORT_RELATIVE,
                    "forbidden actual source-only failed e464 base",
                ),
            ),
            (
                "actual-v22-edge",
                lambda: original.read_regular(
                    edge_target(
                        "rust",
                        True,
                    ),
                    "forbidden actual source-only V22 original edge",
                ),
            ),
            (
                "actual-v22-deep",
                lambda: original.read_regular(
                    deep_target(
                        "zig",
                        True,
                    ),
                    "forbidden actual source-only V22 original deep",
                ),
            ),
            (
                "production-rust",
                lambda: importlib.import_module(
                    "candidates.rust_candidate",
                ),
            ),
            (
                "production-c",
                lambda: importlib.import_module(
                    "candidates.vm_candidate",
                ),
            ),
            (
                "production-zig",
                lambda: importlib.import_module(
                    "candidates.zig_candidate",
                ),
            ),
            (
                "external-engine",
                lambda: importlib.import_module(
                    "regex",
                ),
            ),
            (
                "holdout-read",
                lambda: builtins.open(
                    ROOT / "performance/holdout.json",
                    "rb",
                ),
            ),
            (
                "unrelated-read",
                lambda: builtins.open(
                    ROOT / "README.md",
                    "rb",
                ),
            ),
            ("wall-clock", lambda: time.time()),
            ("performance-clock", lambda: time.perf_counter()),
            (
                "original-worker",
                lambda: subprocess.run(
                    ["forbidden-source-only-v22-original"],
                ),
            ),
            (
                "native-worker",
                lambda: subprocess.Popen(
                    ["forbidden-source-only-v22-native"],
                ),
            ),
            (
                "native-thread",
                lambda: threading.Thread(
                    target=lambda: None,
                ).start(),
            ),
            (
                "native-process",
                lambda: multiprocessing.Process(
                    target=lambda: None,
                ).start(),
            ),
            (
                "temporary-worker",
                lambda: tempfile.TemporaryDirectory(),
            ),
            (
                "actual-original-write",
                lambda: edge_target(
                    "rust",
                    True,
                ).write_bytes(b"forbidden"),
            ),
            (
                "actual-proof-write",
                lambda: deep_proof_target(
                    "zig",
                    True,
                ).write_text("forbidden"),
            ),
        )
        for name, action in blocked:
            reject(
                "actively-enforce-full-candidate-free-v22-boundary:" + name,
                action,
            )
        accept(
            "actually-block-all-real-candidate-and-third-party-imports",
            effects["candidate_import_attempts_blocked"] >= 4,
        )
        accept(
            "actually-block-all-four-real-failures-and-audit-evidence",
            effects["evidence_read_attempts_blocked"] >= 10,
        )
        accept(
            "actually-block-all-original-native-and-process-workers",
            effects["worker_attempts_blocked"] >= 5,
        )
        accept(
            "actually-block-all-wall-and-performance-clock-samples",
            effects["clock_attempts_blocked"] >= 2,
        )
        accept(
            "actually-block-all-canonical-original-and-proof-writes",
            effects["write_attempts_blocked"] >= 2,
        )
        accept(
            "never-import-any-actual-production-candidate",
            not any(
                name == "candidates"
                or name.startswith("candidates.")
                or name == "rebar"
                or name.startswith("rebar.")
                for name in sys.modules
            ),
        )
        accept(
            "never-import-the-real-v21-owner-in-source-mode",
            "tools.postfinal_independent_engine_audit_v21"
            not in sys.modules,
        )
        accept(
            "retain-at-least-2200-independent-v22-source-controls",
            len(controls) >= 2200,
        )
        require(
            len({row["name"] for row in controls}) == len(controls),
            "a complete V22 source-only control denominator was repeated",
        )
        failed = [
            row["name"]
            for row in controls
            if not row["passed"]
        ]
        require(
            not failed,
            "a genuine V22 canonical/owner/failure source control failed: "
            + ", ".join(failed[:12]),
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
        "inherited_v20_check_count": inherited["check_count"],
        "inherited_v18_check_count":
            inherited["inherited_v18_check_count"],
        "inherited_v14_check_count":
            inherited["inherited_v14_check_count"],
        "inherited_v12_check_count":
            inherited["inherited_v12_check_count"],
        "inherited_v11_check_count":
            inherited["inherited_v11_check_count"],
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "historical_evidence_reads": 0,
        "actual_audit_report_reads": 0,
        "holdout_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "actual_v22_controller_sha256": digest,
        "actual_v22_protocol_sha256": PROTOCOL_SHA256,
        "immutable_v20_controller_sha256":
            V20_SOURCE_SHA256,
        "immutable_v20_protocol_sha256":
            V20_PROTOCOL_SHA256,
        "frozen_v21_controller_sha256":
            V21_SOURCE_SHA256,
        "frozen_v21_protocol_sha256":
            V21_PROTOCOL_SHA256,
        "future_v21_base_report_hash_guessed": False,
        "future_v21_strict_report_hash_guessed": False,
        "actual_v13_first_preworker_failure_sha256":
            V13_FAILURE_SHA256,
        "actual_v13_first_preworker_failure_qualifies_current_engine":
            False,
        "actual_v15_first_preworker_failure_sha256":
            V15_FAILURE_SHA256,
        "actual_v15_first_preworker_failure_qualifies_current_engine":
            False,
        "actual_v17_first_postflight_failure_sha256":
            V17_FAILURE_SHA256,
        "actual_v17_first_postflight_failure_qualifies_current_engine":
            False,
        "actual_v19_first_publication_failure_sha256":
            V19_FAILURE_SHA256,
        "actual_v19_first_publication_failure_qualifies_current_engine":
            False,
        "actual_v19_unqualified_durable_report_sha256":
            V19_DURABLE_REPORT_SHA256,
        "actual_v19_unqualified_durable_report_bytes":
            V19_DURABLE_REPORT_BYTES,
        "original_edge_checks":
            original.EDGE_CHECKS,
        "original_edge_categories":
            original.EDGE_CATEGORIES,
        "original_deep_checks":
            original.DEEP_CHECKS,
        "original_deep_seeded_cases":
            original.DEEP_SEEDED_CASES,
        "independent_family_count":
            len(FAMILIES),
        "complete_owned_source_count":
            12,
        "complete_native_elf_count":
            5,
        "blocked_effect_attempts":
            observed,
        "performance":
            "NOT MEASURED",
        "holdout":
            "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    mode = parser.add_mutually_exclusive_group(
        required=True,
    )
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--qualified-edge", action="store_true")
    mode.add_argument("--qualified-deep", action="store_true")
    parser.add_argument(
        "--module",
        choices=tuple(
            item["module"]
            for item in original.FAMILIES.values()
        ),
    )
    parser.add_argument("--v21-audit-source-sha256")
    parser.add_argument("--v21-audit-protocol-sha256")
    parser.add_argument("--v21-base-report-sha256")
    parser.add_argument("--v21-strict-report-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(
        sys.argv[1:]
        if arguments is None
        else arguments,
    )
    if options.self_test:
        require(
            options.module is None
            and all(
                getattr(options, key) is None
                for key in (
                    "v21_audit_source_sha256",
                    "v21_audit_protocol_sha256",
                    "v21_base_report_sha256",
                    "v21_strict_report_sha256",
                )
            ),
            "candidate-free V22 controls cannot read reports or run workers",
        )
        result = candidate_free_self_test()
    else:
        require(
            isinstance(options.module, str),
            "a complete original V22 worker requires its exact candidate family",
        )
        family = next(
            name
            for name, item in original.FAMILIES.items()
            if item["module"] == options.module
        )
        pins = validated_pins({
            "audit_source":
                options.v21_audit_source_sha256,
            "audit_protocol":
                options.v21_audit_protocol_sha256,
            "base_report":
                options.v21_base_report_sha256,
            "strict_report":
                options.v21_strict_report_sha256,
        })
        result = (
            refresh_edge(
                family,
                pins,
            )
            if options.qualified_edge
            else refresh_deep(
                family,
                pins,
            )
        )
    print(json.dumps(
        result,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
    ))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofV22Failure as failure:
        print(json.dumps(
            {
                "schema": SCHEMA + "-actual-worker-failure",
                **failure.evidence,
            },
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
        ))
        raise SystemExit(2) from failure
