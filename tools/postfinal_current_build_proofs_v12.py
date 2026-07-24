#!/usr/bin/env python3
"""Recover genuine V11-format deep proofs with separately honest V12 provenance."""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import gzip
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_current_build_proofs_v11 as v11


SCHEMA = "rebar-postfinal-current-build-proofs-v12"
SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v12.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V12.md"
PROTOCOL_SHA256 = "f74ccaf19f836f801de34aaf3228f9bcd14aabe88032ebee4dbe886247ec6b40"
V11_SOURCE_SHA256 = "2895dd28b3dc69985cc0f6f8575398e8b8b10f58141f0612645a687478da9f04"
V11_PROTOCOL_SHA256 = "334405521f2f945cc58cabf246cf8f784e8a6a5be7091a20587b0daf428412af"
ACTUAL_V10_BASE_REPORT_SHA256 = "589321a768e10c52f039a68acb211574ec884598771ede2152f91994cc69f353"
ACTUAL_V10_STRICT_REPORT_SHA256 = "d8f31dd480bdba530a454b38428a23ef347c6e3cce7796f8992d6e7767381f4b"
PRIOR_FAILURE_RELATIVE = (
    "candidates/audits/"
    "RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V11-PRODUCER-CRASH.json.gz"
)
PRIOR_FAILURE_SHA256 = "360d430666bfae146eb9abc18cab2bcd9822096f78e6f21ed3b938bb50631c39"
PRIOR_INVALIDATED_RELATIVE = (
    "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-"
    "POSTFINAL-CURRENT-BUILD-V11-INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
)
PRIOR_INVALIDATED_SHA256 = "9cc30b172575c83b399f680057a6d33ae952e44f920079c3d8c3b67566afb407"
DEEP_SCHEMA = "rebar-rust-v8-deep-public-contract-v1"
EXPLICIT_WORKER_ENVIRONMENT_KEYS = frozenset({
    "PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED", "PYTHONPATH", "LC_ALL", "PATH",
})


class ProofV12Error(AssertionError):
    """A genuine, additive V12 retry cannot be safely or truthfully qualified."""


class ProofV12Failure(ProofV12Error):
    def __init__(self, message: str, evidence: Mapping[str, Any]):
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ProofV12Error(message)


def validate_parent_environment(environment: Mapping[str, Any]) -> dict[str, str]:
    require(isinstance(environment, Mapping),
            "the actual V12 parent environment is missing")
    expected = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
    }
    for key, value in expected.items():
        require(type(environment.get(key)) is str
                and environment.get(key) == value,
                "V12 requires the exact parent environment: " + key)
    require(os.path.isabs(expected["PYTHONPATH"])
            and Path(expected["PYTHONPATH"]).resolve() == ROOT,
            "the V12 parent PYTHONPATH is not the exact canonical project root")
    return expected


def verify_runtime_source_only() -> None:
    v11.verify_runtime()
    require(ROOT == v11.ROOT
            and SOURCE_RELATIVE == "tools/postfinal_current_build_proofs_v12.py"
            and PROTOCOL_RELATIVE
            == "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V12.md"
            and v11.PINNED_EXECUTABLE.resolve()
            == Path(sys.executable).resolve(),
            "V12 requires the real pinned isolated CPython 3.14.6 controller")


def verify_parent_retry_environment() -> dict[str, str]:
    verify_runtime_source_only()
    return validate_parent_environment(os.environ)


def worker_environment() -> dict[str, str]:
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }
    require(set(environment) == EXPLICIT_WORKER_ENVIRONMENT_KEYS
            and validate_parent_environment(environment)
            == {key: environment[key] for key in (
                "PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED", "PYTHONPATH",
            )},
            "V12 must construct the exact original-worker environment explicitly")
    return environment


def retry_proof_target(family: str, passed: bool) -> Path:
    metadata = v11.checked_family(family)
    require(type(passed) is bool, "the real V12 retry result must be boolean")
    result = "PASS" if passed else "FAIL"
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V12-RETRY-" + result + "-PROOF.json"
    )


def retry_failure_target(family: str) -> Path:
    metadata = v11.checked_family(family)
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V12-PRODUCER-CRASH.json.gz"
    )


def retry_invalidated_target(family: str) -> Path:
    metadata = v11.checked_family(family)
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V12-INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
    )


def authenticate_controller() -> dict[str, str]:
    verify_runtime_source_only()
    source = v11.read_regular(ROOT / SOURCE_RELATIVE, "actual immutable V12 controller")
    protocol = v11.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    v11.authenticate_frozen(v11.SOURCE_RELATIVE, V11_SOURCE_SHA256)
    v11.authenticate_frozen(v11.PROTOCOL_RELATIVE, V11_PROTOCOL_SHA256)
    require(v11.REFRESH_PROTOCOL_SHA256 == V11_PROTOCOL_SHA256,
            "the immutable V11 controller changed its actual V11 protocol")
    require(v11.DEEP_CHECKS == 393 and v11.DEEP_SEEDED_CASES == 64
            and v11.EDGE_CHECKS == 223198 and v11.EDGE_CATEGORIES == 49
            and len(v11.FAMILIES) == 3
            and sum(len(row["sources"]) for row in v11.FAMILIES.values()) == 12
            and sum(len(row["native"]) for row in v11.FAMILIES.values()) == 5,
            "V12 changed a frozen original denominator or independent family")
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": hashlib.sha256(protocol).hexdigest(),
        "v11_format_source_path": v11.SOURCE_RELATIVE,
        "v11_format_source_sha256": V11_SOURCE_SHA256,
        "v11_format_protocol_path": v11.PROTOCOL_RELATIVE,
        "v11_format_protocol_sha256": V11_PROTOCOL_SHA256,
    }


def validate_prior_incident_documents(
    failure: Any,
    invalidated: Any,
    state: Mapping[str, Any],
) -> dict[str, Any]:
    require(isinstance(failure, dict) and isinstance(invalidated, dict),
            "both exact actual first V11 failure documents are required")
    expected = {
        "schema": v11.SCHEMA + "-original-producer-failure",
        "status": "FAIL", "result": "FAIL", "mode": "qualified-deep",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "actual_failure_reason": "post-original-integrity-failure",
        "actual_child_exit_code": 0,
        "actual_child_signal": None,
        "timed_out": False,
        "actual_integrity_error_type": "AssertionError",
        "actual_integrity_error_message": "PYTHONDONTWRITEBYTECODE=1 is mandatory",
        "complete_original_observation_archive": True,
        "original_correctness_observations": "INVALIDATED",
        "invalidated_complete_original_evidence_path": PRIOR_INVALIDATED_RELATIVE,
        "invalidated_complete_original_evidence_sha256": PRIOR_INVALIDATED_SHA256,
        "invalidated_complete_original_actual_status": "NOT VALIDATED",
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "production_observations_invented": False,
        "refresh_protocol_path": v11.PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": V11_PROTOCOL_SHA256,
        "actual_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "actual_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for key, value in expected.items():
        require(failure.get(key) == value,
                "the actual failed first V11 invocation was concealed: " + key)
    actual_stdout = v11.restore_complete_stream(
        failure.get("stdout"), "actual complete first V11 deep worker stdout",
    )
    actual_stderr = v11.restore_complete_stream(
        failure.get("stderr"), "actual complete first V11 deep worker stderr",
    )
    require(bool(actual_stdout) and not actual_stderr,
            "the real first V11 child streams or successful exit were replaced")
    graph = v11.audited_graph_provenance(state)
    require(graph.get("all_family_audit_qualified") is True
            and len(graph.get("all_family_source_sha256_by_path", {})) == 12
            and len(graph.get("all_family_native_elf_sha256_by_path", {})) == 5
            and failure.get("all_family_audited_provenance") == graph,
            "the genuine first V11 failure lost the real 12-source/five-ELF graph")
    rust = v11.checked_family("rust")
    expected_sources = {
        path: graph["all_family_source_sha256_by_path"][path]
        for path in rust["sources"]
    }
    expected_native = {
        path: graph["all_family_native_elf_sha256_by_path"][path]
        for path in rust["native"].values()
    }
    require(failure.get("full_current_family_source_sha256") == expected_sources
            and failure.get("full_current_family_native_elf_sha256")
            == expected_native,
            "the actual first V11 Rust failure changed its real seven-source/two-ELF owner")
    v11.validate_owner(
        state["owner"], failure.get("native_owner_before"), "rust", expected_native,
    )
    original_expected = {
        "schema": DEEP_SCHEMA, "python": "3.14.6",
        "status": "PASS", "seed": v11.DEEP_SEED,
        "seeded_case_count": v11.DEEP_SEEDED_CASES,
        "checks": v11.DEEP_CHECKS,
        "candidate_module": rust["module"], "candidate_family": "RUST",
        "reference_a_sha256": v11.DEEP_REFERENCE_SHA256,
        "reference_b_sha256": v11.DEEP_REFERENCE_SHA256,
        "candidate_sha256": v11.DEEP_REFERENCE_SHA256,
        "public_mismatches": [], "public_mismatch_count": 0,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for key, value in original_expected.items():
        require(invalidated.get(key) == value,
                "the complete invalidated first V11 original changed: " + key)
    require(isinstance(invalidated.get("candidate"), dict)
            and invalidated["candidate"].get("observation_sha256")
            == v11.DEEP_REFERENCE_SHA256,
            "the actual first V11 candidate observations were concealed")
    return {
        "actual_v11_controller_path": v11.SOURCE_RELATIVE,
        "actual_v11_controller_sha256": V11_SOURCE_SHA256,
        "actual_v11_protocol_path": v11.PROTOCOL_RELATIVE,
        "actual_v11_protocol_sha256": V11_PROTOCOL_SHA256,
        "actual_v11_first_invocation_status": "FAIL",
        "actual_v11_first_invocation_qualified": False,
        "actual_v11_first_failure_path": PRIOR_FAILURE_RELATIVE,
        "actual_v11_first_failure_sha256": PRIOR_FAILURE_SHA256,
        "actual_v11_first_invalidated_original_path": PRIOR_INVALIDATED_RELATIVE,
        "actual_v11_first_invalidated_original_sha256": PRIOR_INVALIDATED_SHA256,
        "actual_v11_first_failure_reason": expected["actual_failure_reason"],
        "actual_v11_first_failure_error_type": "AssertionError",
        "actual_v11_first_failure_error_message":
            "PYTHONDONTWRITEBYTECODE=1 is mandatory",
        "actual_v11_first_child_exit_code": 0,
        "actual_v11_first_child_stdout": failure["stdout"],
        "actual_v11_first_child_stderr": failure["stderr"],
        "actual_v11_first_original_checks": v11.DEEP_CHECKS,
        "actual_v11_first_original_seeded_cases": v11.DEEP_SEEDED_CASES,
        "actual_v11_first_original_candidate_sha256": v11.DEEP_REFERENCE_SHA256,
        "actual_v11_first_original_was_invalidated": True,
        "first_failure_retroactively_qualified": False,
    }


def authenticate_prior_incident(state: Mapping[str, Any]) -> tuple[
    dict[str, Any], dict[str, Any], bytes,
]:
    v8 = state["v8"]
    failure_raw = v11.authenticate_frozen(PRIOR_FAILURE_RELATIVE, PRIOR_FAILURE_SHA256)
    failure, _ = v8.decode_archive(
        failure_raw, "complete actual failed first V11 original producer",
    )
    invalidated_raw = v11.authenticate_frozen(
        PRIOR_INVALIDATED_RELATIVE, PRIOR_INVALIDATED_SHA256,
    )
    invalidated, _ = v8.decode_archive(
        invalidated_raw,
        "complete actual compact invalidated first V11 original",
        compact=True,
    )
    return (
        validate_prior_incident_documents(failure, invalidated, state),
        invalidated,
        invalidated_raw,
    )


def preflight(family: str, base_digest: Any, strict_digest: Any) -> dict[str, Any]:
    parent = verify_parent_retry_environment()
    metadata = v11.checked_family(family)
    controller = authenticate_controller()
    require(base_digest == ACTUAL_V10_BASE_REPORT_SHA256
            and strict_digest == ACTUAL_V10_STRICT_REPORT_SHA256,
            "V12 requires both independently supplied exact actual V10 reports")
    pins = v11.validated_report_pins(True, base_digest, strict_digest)
    require(isinstance(pins, dict), "both genuine passing V10 audit pins are mandatory")
    for relative, digest in v11.FROZEN_INPUTS.items():
        if not relative.startswith("candidates/") and "/evidence/" not in relative:
            v11.authenticate_frozen(relative, digest)
    v11.authenticate_frozen(
        v11.V10_OWNERSHIP_PROTOCOL_RELATIVE, v11.V10_OWNERSHIP_PROTOCOL_SHA256,
    )
    v8 = v11.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        v11.V8_PROOF_RELATIVE, v11.V8_PROOF_SHA256,
    )
    owner = v11.import_frozen(
        "tools.postfinal_from_scratch_audit_v10",
        v11.V10_BASE_SOURCE_RELATIVE, v11.V10_BASE_SOURCE_SHA256,
    )
    strict = v11.import_frozen(
        "tools.postfinal_no_delegation_audit_v10",
        v11.V10_STRICT_SOURCE_RELATIVE, v11.V10_STRICT_SOURCE_SHA256,
    )
    require(tuple(owner.CORE_FAMILIES) == tuple(v11.FAMILIES)
            and strict.independent is owner
            and owner.PROTOCOL_RELATIVE == v11.V10_OWNERSHIP_PROTOCOL_RELATIVE
            and owner.PROTOCOL_SHA256 == v11.V10_OWNERSHIP_PROTOCOL_SHA256,
            "a real corrected V10 owner or strict validator was substituted")
    for name, detail in v11.FAMILIES.items():
        require(tuple(owner.OWNED_SOURCE_PATHS[name]) == detail["sources"]
                and dict(owner.OWNED_NATIVE_PATHS[name]) == detail["native"],
                "the genuine all-family V10 source/native graph changed: " + name)
    audits = v11.audit_v11_reports(owner, strict, pins)
    preliminary = {"owner": owner, "v8": v8, "audits": audits}
    incident, invalidated, invalidated_raw = authenticate_prior_incident(preliminary)
    history = v11.authenticate_history(v8, owner)
    snapshot = v11.snapshot_family(family)
    graph = v11.audited_graph_provenance(preliminary)
    require(snapshot["source_sha256_by_path"] == {
        path: graph["all_family_source_sha256_by_path"][path]
        for path in metadata["sources"]
    } and snapshot["native_sha256_by_path"] == {
        path: graph["all_family_native_elf_sha256_by_path"][path]
        for path in metadata["native"].values()
    }, "the independently audited real V12 candidate changed after both V10 audits")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the V12 proof controller must never import a production candidate")
    return {
        "owner": owner, "strict": strict, "v8": v8,
        "history": history, "snapshot": snapshot, "audits": audits,
        "parent_environment": parent, "controller": controller,
        "prior_incident": incident,
        "prior_invalidated_original": invalidated,
        "prior_invalidated_original_raw": invalidated_raw,
    }


def authenticate_qualified_edge(
    family: str, state: Mapping[str, Any], contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    original_path = v11.edge_target(family, True, True)
    proof_path = v11.edge_proof_target(family, True, True)
    original_raw = v11.read_regular(original_path, "actual original qualified V11 edge")
    original, edge, passed = state["v8"].validate_original_edge(
        original_raw, original_path, family, state["snapshot"], contract,
    )
    require(passed and edge.get("failed") == 0
            and edge.get("checks") == v11.EDGE_CHECKS
            and edge.get("category_count") == v11.EDGE_CATEGORIES,
            "a V12 deep retry requires all 223,198 genuinely passing original edge checks")
    proof_raw = v11.read_regular(proof_path, "actual complete qualified V11 edge owner proof")
    proof = v11.decode_json(proof_raw, "canonical actual V11 edge archive-and-owner proof")
    require(v11.canonical(proof) == proof_raw,
            "the genuinely qualified V11 edge owner proof is not canonical")
    recorded = subprocess.CompletedProcess(
        args=["durably-recorded-original-v11-edge"],
        returncode=proof.get("original_worker_returncode"),
        stdout=v11.restore_complete_stream(
            proof.get("original_worker_stdout"), "actual original qualified V11 edge stdout",
        ),
        stderr=v11.restore_complete_stream(
            proof.get("original_worker_stderr"), "actual original qualified V11 edge stderr",
        ),
    )
    archive_sha256 = hashlib.sha256(original_raw).hexdigest()
    proof_sha256 = hashlib.sha256(proof_raw).hexdigest()
    v11.validate_durable_wrapper(
        proof, family, state, qualified=True, deep=False, passed=True,
        original=original, archive_path=original_path,
        archive_sha256=archive_sha256, archive_bytes=len(original_raw),
        owner_before=proof.get("corrected_v10_native_owner_before"),
        owner_after=proof.get("corrected_v10_native_owner_after"),
        producer=recorded,
    )
    qualified = {
        "status": "PASS", "campaign_qualified": True,
        "archive_path": original_path.relative_to(ROOT).as_posix(),
        "archive_sha256": archive_sha256,
        "proof_path": proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": proof_sha256,
    }
    return edge, qualified, original_raw, proof_raw


def preflight_fresh_destinations(family: str) -> None:
    parent = ROOT / "candidates/audits"
    destinations = (
        v11.deep_target(family, True),
        v11.deep_proof_target(family, True),
        retry_proof_target(family, True),
        retry_proof_target(family, False),
        retry_failure_target(family),
        retry_invalidated_target(family),
    )
    require(len(set(destinations)) == len(destinations),
            "V12 reused an immutable pass, failure, or provenance destination")
    require(all(path != ROOT / PRIOR_FAILURE_RELATIVE
                and path != ROOT / PRIOR_INVALIDATED_RELATIVE
                for path in destinations),
            "V12 must never overwrite or retry an actual first V11 failure")
    for path in destinations:
        v11.fresh_target(path, parent)


def validate_original_process(
    producer: subprocess.CompletedProcess[bytes],
    command: list[str],
) -> subprocess.CompletedProcess[bytes]:
    require(isinstance(producer, subprocess.CompletedProcess)
            and producer.args == command
            and isinstance(producer.returncode, int)
            and isinstance(producer.stdout, bytes)
            and isinstance(producer.stderr, bytes)
            and len(producer.stdout) <= v11.MAX_CHILD_OUTPUT_BYTES
            and len(producer.stderr) <= v11.MAX_CHILD_OUTPUT_BYTES,
            "the actual V12 original deep worker or complete streams are not genuine")
    return producer


def build_retry_proof(
    family: str,
    state: Mapping[str, Any],
    *,
    original: Mapping[str, Any],
    original_raw: bytes,
    wrapper: Mapping[str, Any],
    wrapper_raw: bytes,
    owner_before: Mapping[str, Any],
    owner_after: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes],
    command: list[str],
    qualified_edge: Mapping[str, Any],
) -> dict[str, Any]:
    metadata = v11.checked_family(family)
    validate_original_process(producer, command)
    require(isinstance(original, Mapping) and isinstance(original_raw, bytes)
            and isinstance(wrapper, Mapping) and isinstance(wrapper_raw, bytes)
            and producer.returncode == 0,
            "the honest V12 retry proof requires a real complete passing original")
    controller = state["controller"]
    return {
        "schema": SCHEMA + "-qualified-deep-retry-durable-proof",
        "status": "PASS", "result": "PASS", "mode": "qualified-deep",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "campaign_qualified": True,
        "actual_invoking_controller": "V12",
        "actual_invoking_controller_path": controller["source_path"],
        "actual_invoking_controller_sha256": controller["source_sha256"],
        "actual_retry_protocol_path": controller["protocol_path"],
        "actual_retry_protocol_sha256": controller["protocol_sha256"],
        "v11_executed_this_retry": False,
        "v11_format_controller_path": controller["v11_format_source_path"],
        "v11_format_controller_sha256": controller["v11_format_source_sha256"],
        "v11_format_protocol_path": controller["v11_format_protocol_path"],
        "v11_format_protocol_sha256": controller["v11_format_protocol_sha256"],
        "immutable_v11_format_builder_used": True,
        "immutable_v11_format_validator_used": True,
        "unchanged_original_v8_deep_validator_used": True,
        "actual_verified_parent_environment": dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment": worker_environment(),
        "actual_original_worker_command": list(command),
        "actual_original_worker_returncode": producer.returncode,
        "actual_original_worker_stdout": v11.observed_stream(producer.stdout, True),
        "actual_original_worker_stderr": v11.observed_stream(producer.stderr, True),
        "qualified_original_v11_edge": dict(qualified_edge),
        "complete_original_deep_checks": v11.DEEP_CHECKS,
        "complete_original_deep_seeded_cases": v11.DEEP_SEEDED_CASES,
        "complete_original_deep_reference_sha256": v11.DEEP_REFERENCE_SHA256,
        "complete_original_deep_candidate_sha256": original.get("candidate_sha256"),
        "complete_original_deep_public_mismatch_count":
            original.get("public_mismatch_count"),
        "original_v11_format_archive_path":
            v11.deep_target(family, True).relative_to(ROOT).as_posix(),
        "original_v11_format_archive_sha256": hashlib.sha256(original_raw).hexdigest(),
        "original_v11_format_archive_bytes": len(original_raw),
        "original_v11_format_owner_proof_path":
            v11.deep_proof_target(family, True).relative_to(ROOT).as_posix(),
        "original_v11_format_owner_proof_sha256": hashlib.sha256(wrapper_raw).hexdigest(),
        "original_v11_format_owner_proof_bytes": len(wrapper_raw),
        "original_v11_format_owner_proof_schema": wrapper.get("schema"),
        "corrected_v10_native_owner_before": dict(owner_before),
        "corrected_v10_native_owner_after": dict(owner_after),
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "all_family_audited_provenance": v11.audited_graph_provenance(state),
        "actual_v10_base_report_sha256": state["audits"]["pins"]["base_report"],
        "actual_v10_strict_report_sha256": state["audits"]["pins"]["strict_report"],
        "preserved_immutable_history": state["history"],
        "preserved_actual_first_v11_failure": dict(state["prior_incident"]),
        "retry_proof_path": retry_proof_target(family, True).relative_to(ROOT).as_posix(),
        "complete_original_producer_bytes_preserved": True,
        "stdout_is_not_durable_proof": True,
        "production_observations_invented": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def validate_retry_proof(
    document: Any,
    family: str,
    state: Mapping[str, Any],
    *,
    original: Mapping[str, Any],
    original_raw: bytes,
    wrapper: Mapping[str, Any],
    wrapper_raw: bytes,
    owner_before: Mapping[str, Any],
    owner_after: Mapping[str, Any],
    producer: subprocess.CompletedProcess[bytes],
    command: list[str],
    qualified_edge: Mapping[str, Any],
) -> dict[str, Any]:
    require(isinstance(document, dict),
            "the separate complete genuine V12 invocation proof is mandatory")
    expected = build_retry_proof(
        family, state, original=original, original_raw=original_raw,
        wrapper=wrapper, wrapper_raw=wrapper_raw,
        owner_before=owner_before, owner_after=owner_after,
        producer=producer, command=command, qualified_edge=qualified_edge,
    )
    require(document == expected,
            "the V12 retry changed its real controller, failure, owner, original, or provenance")
    require(document["actual_invoking_controller"] == "V12"
            and document["v11_executed_this_retry"] is False,
            "V12 misrepresented the actual immutable V11 first invocation")
    require(document["preserved_actual_first_v11_failure"]
            == state["prior_incident"]
            and document["preserved_actual_first_v11_failure"]
            .get("actual_v11_first_invocation_status") == "FAIL"
            and document["preserved_actual_first_v11_failure"]
            .get("first_failure_retroactively_qualified") is False
            and document["complete_original_deep_checks"] == 393
            and document["complete_original_deep_seeded_cases"] == 64
            and document["complete_original_deep_public_mismatch_count"] == 0
            and document["complete_original_deep_candidate_sha256"]
            == v11.DEEP_REFERENCE_SHA256
            and document["actual_v10_base_report_sha256"]
            == ACTUAL_V10_BASE_REPORT_SHA256
            and document["actual_v10_strict_report_sha256"]
            == ACTUAL_V10_STRICT_REPORT_SHA256,
            "the separate V12 provenance concealed real failed history or genuine correctness")
    for stream, actual in (
        (document["actual_original_worker_stdout"], producer.stdout),
        (document["actual_original_worker_stderr"], producer.stderr),
    ):
        require(v11.restore_complete_stream(stream, "complete genuine V12 retry stream")
                == actual,
                "the separate V12 proof concealed actual original worker bytes")
    v11.validate_owner(state["owner"], owner_before, family,
                       state["snapshot"]["native_sha256_by_path"])
    v11.validate_owner(state["owner"], owner_after, family,
                       state["snapshot"]["native_sha256_by_path"])
    return document


def preserve_retry_failure(
    family: str,
    state: Mapping[str, Any],
    *,
    error: BaseException,
    owner_before: Mapping[str, Any] | None,
    owner_after: Mapping[str, Any] | None,
    producer: subprocess.CompletedProcess[bytes] | None,
    completed_original: bytes | None,
    validated_original: bool | None,
    command: list[str] | None,
    published_archive: bool,
    published_wrapper: bool,
) -> ProofV12Failure:
    metadata = v11.checked_family(family)
    timed_out = isinstance(error, subprocess.TimeoutExpired)
    if producer is None:
        stdout = getattr(error, "stdout", None)
        stderr = getattr(error, "stderr", None)
        returncode = None
    else:
        stdout, stderr, returncode = producer.stdout, producer.stderr, producer.returncode
    invalidated_path = invalidated_digest = invalidated_status = None
    if completed_original is not None:
        require(isinstance(completed_original, bytes)
                and 0 < len(completed_original) <= v11.MAX_FILE_BYTES,
                "refusing to invent a completed genuine V12 original archive")
        invalidated = retry_invalidated_target(family)
        invalidated_digest = v11.exclusive_publish(
            invalidated, completed_original, deep=True,
        )
        invalidated_path = invalidated.relative_to(ROOT).as_posix()
        invalidated_status = (
            "NOT VALIDATED" if validated_original is None
            else "PASS" if validated_original else "FAIL"
        )
    actual_owner_failure = getattr(error, "evidence", None)
    document = {
        "schema": SCHEMA + "-original-producer-failure",
        "status": "FAIL", "result": "FAIL", "mode": "qualified-deep",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "actual_invoking_controller": "V12",
        "actual_invoking_controller_path": state["controller"]["source_path"],
        "actual_invoking_controller_sha256": state["controller"]["source_sha256"],
        "actual_retry_protocol_path": PROTOCOL_RELATIVE,
        "actual_retry_protocol_sha256": PROTOCOL_SHA256,
        "v11_executed_this_retry": False,
        "actual_failure_error_type": type(error).__name__,
        "actual_failure_error_message": str(error),
        "actual_child_exit_code": returncode,
        "actual_child_signal": -returncode
            if isinstance(returncode, int) and returncode < 0 else None,
        "timed_out": timed_out,
        "timeout_seconds": 1800 if timed_out else None,
        "actual_original_worker_command": list(command) if command is not None else None,
        "actual_verified_parent_environment": dict(state["parent_environment"]),
        "actual_explicit_original_worker_environment": worker_environment(),
        "stdout": v11.observed_stream(stdout, not timed_out),
        "stderr": v11.observed_stream(stderr, not timed_out),
        "native_owner_before": dict(owner_before) if owner_before is not None else None,
        "native_owner_after": dict(owner_after) if owner_after is not None else None,
        "actual_native_owner_failure":
            dict(actual_owner_failure) if isinstance(actual_owner_failure, Mapping)
            else None,
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "all_family_audited_provenance": v11.audited_graph_provenance(state),
        "actual_v10_base_report_sha256": state["audits"]["pins"]["base_report"],
        "actual_v10_strict_report_sha256": state["audits"]["pins"]["strict_report"],
        "preserved_immutable_history": state["history"],
        "preserved_actual_first_v11_failure": dict(state["prior_incident"]),
        "complete_original_observation_archive": completed_original is not None,
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_digest,
        "invalidated_complete_original_actual_status": invalidated_status,
        "v11_format_archive_was_exclusively_published": published_archive,
        "v11_format_owner_proof_was_exclusively_published": published_wrapper,
        "unpaired_v11_format_archive_qualifies": False,
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    payload = v11.canonical(document)
    require(len(payload) <= v11.MAX_FILE_BYTES,
            "the genuine V12 failure exceeded its complete safe archive boundary")
    raw = gzip.compress(payload, compresslevel=9, mtime=0)
    decoded, restored = state["v8"].decode_archive(
        raw, "complete original additive V12 failure",
    )
    require(decoded == document and restored == payload,
            "the genuine additive V12 failure changed its actual complete evidence")
    target = retry_failure_target(family)
    digest = v11.exclusive_publish(target, raw, deep=True)
    failure_proof = {
        "schema": SCHEMA + "-qualified-deep-retry-failure-proof",
        "status": "FAIL", "result": "FAIL", "campaign_qualified": False,
        "actual_invoking_controller": "V12",
        "actual_invoking_controller_path": SOURCE_RELATIVE,
        "actual_invoking_controller_sha256": state["controller"]["source_sha256"],
        "actual_retry_protocol_path": PROTOCOL_RELATIVE,
        "actual_retry_protocol_sha256": PROTOCOL_SHA256,
        "v11_executed_this_retry": False,
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "actual_failure_evidence_path": target.relative_to(ROOT).as_posix(),
        "actual_failure_evidence_sha256": digest,
        "actual_failure_error_type": type(error).__name__,
        "actual_failure_error_message": str(error),
        "preserved_actual_first_v11_failure": dict(state["prior_incident"]),
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_digest,
        "v11_format_archive_was_exclusively_published": published_archive,
        "v11_format_owner_proof_was_exclusively_published": published_wrapper,
        "unpaired_v11_format_archive_qualifies": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    proof_path = retry_proof_target(family, False)
    proof_digest = v11.exclusive_publish(
        proof_path, v11.canonical(failure_proof), deep=True,
    )
    return ProofV12Failure(
        "the genuine V12 retry failed; complete additive failure evidence is retained",
        {
            "status": "FAIL", "candidate_family": metadata["contract_name"],
            "candidate_module": metadata["module"],
            "actual_invoking_controller": "V12",
            "actual_failure_evidence_path": target.relative_to(ROOT).as_posix(),
            "actual_failure_evidence_sha256": digest,
            "actual_retry_failure_proof_path": proof_path.relative_to(ROOT).as_posix(),
            "actual_retry_failure_proof_sha256": proof_digest,
            "invalidated_complete_original_evidence_path": invalidated_path,
            "invalidated_complete_original_evidence_sha256": invalidated_digest,
            "campaign_qualified": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        },
    )


def refresh_qualified_deep(
    family: str, base_digest: str, strict_digest: str,
) -> dict[str, Any]:
    state = preflight(family, base_digest, strict_digest)
    v8 = state["v8"]
    contract = v8.load_contract()
    if family == "rust":
        rust_state = state
    else:
        rust_snapshot = v11.snapshot_family("rust")
        graph = v11.audited_graph_provenance(state)
        require(rust_snapshot["source_sha256_by_path"] == {
            path: graph["all_family_source_sha256_by_path"][path]
            for path in v11.FAMILIES["rust"]["sources"]
        } and rust_snapshot["native_sha256_by_path"] == {
            path: graph["all_family_native_elf_sha256_by_path"][path]
            for path in v11.FAMILIES["rust"]["native"].values()
        }, "the preserved real first V11 Rust failure changed its audited native owner")
        rust_state = {**state, "snapshot": rust_snapshot}
    rust_edge, _, _, _ = authenticate_qualified_edge("rust", rust_state, contract)
    prior_original, prior_passed = v8.validate_deep(
        state["prior_invalidated_original_raw"], "rust", rust_edge,
        rust_state["snapshot"], contract,
    )
    require(prior_passed and prior_original == state["prior_invalidated_original"]
            and prior_original.get("public_mismatch_count") == 0,
            "the actual complete invalidated first V11 deep archive was substituted")
    if family == "rust":
        edge, qualified_edge, edge_raw, edge_proof_raw = authenticate_qualified_edge(
            family, state, contract,
        )
    else:
        edge, qualified_edge, edge_raw, edge_proof_raw = authenticate_qualified_edge(
            family, state, contract,
        )
    preflight_fresh_destinations(family)
    before: dict[str, Any] | None = None
    after_owner: dict[str, Any] | None = None
    producer: subprocess.CompletedProcess[bytes] | None = None
    raw: bytes | None = None
    passed: bool | None = None
    command: list[str] | None = None
    published_archive = False
    published_wrapper = False
    try:
        before = v11.validate_owner(
            state["owner"],
            state["owner"].run_native_worker(
                family, dict(state["snapshot"]["native_sha256_by_path"]),
            ),
            family, state["snapshot"]["native_sha256_by_path"],
        )
        require(v11.snapshot_family(family) == state["snapshot"],
                "the real native owner changed before the genuine V12 deep worker")
        with tempfile.TemporaryDirectory(
            prefix="rebar-v12-original-deep-" + family + "-", dir="/tmp",
        ) as directory:
            private = Path(directory).resolve()
            require(private.parent == Path("/tmp").resolve(),
                    "the actual V12 original worker escaped its private direct /tmp root")
            temporary = private / (
                "RUST-V8-DEEP-CONTRACT-" + v11.FAMILIES[family]["contract_name"]
                + "-POSTFINAL-CURRENT-BUILD-V12-PRIVATE.json.gz"
            )
            command = [
                str(v11.PINNED_EXECUTABLE), "-I", "-B", "-c", v11.DEEP_LAUNCHER,
                str(ROOT), v11.FAMILIES[family]["module"],
                str(v11.edge_target(family, True, True)),
                str(temporary), str(private),
            ]
            producer = subprocess.run(
                command, cwd=str(ROOT), env=worker_environment(),
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=False, timeout=1800,
            )
            validate_original_process(producer, command)
            require(temporary.is_file() and not temporary.is_symlink(),
                    "the genuine V12 deep worker produced no complete original archive")
            raw = v11.read_regular(temporary, "complete original private V12 deep archive")
            original, passed = v8.validate_deep(
                raw, family, edge, state["snapshot"], contract,
            )
            require(passed is True and producer.returncode == 0
                    and original.get("public_mismatch_count") == 0
                    and original.get("candidate_sha256") == v11.DEEP_REFERENCE_SHA256,
                    "the genuine V12 deep retry did not pass all 393 original checks")
            after_owner = v11.validate_owner(
                state["owner"],
                state["owner"].run_native_worker(
                    family, dict(state["snapshot"]["native_sha256_by_path"]),
                ),
                family, state["snapshot"]["native_sha256_by_path"],
            )
            after = preflight(family, base_digest, strict_digest)
            require(after["controller"] == state["controller"]
                    and after["parent_environment"] == state["parent_environment"]
                    and after["snapshot"] == state["snapshot"]
                    and after["history"] == state["history"]
                    and after["audits"]["pins"] == state["audits"]["pins"]
                    and after["audits"]["graph"] == state["audits"]["graph"]
                    and after["prior_incident"] == state["prior_incident"]
                    and after["prior_invalidated_original"]
                    == state["prior_invalidated_original"]
                    and after["prior_invalidated_original_raw"]
                    == state["prior_invalidated_original_raw"]
                    and v11.read_regular(v11.edge_target(family, True, True),
                                         "rechecked original qualified V11 edge")
                    == edge_raw
                    and v11.read_regular(v11.edge_proof_target(family, True, True),
                                         "rechecked original V11 edge owner proof")
                    == edge_proof_raw,
                    "an actual audit, original incident, source, ELF, owner or edge changed")
            original_target = v11.deep_target(family, True)
            wrapper_target = v11.deep_proof_target(family, True)
            original_digest = hashlib.sha256(raw).hexdigest()
            wrapper = v11.build_durable_wrapper(
                family, state, qualified=True, deep=True, passed=True,
                original=original, archive_path=original_target,
                archive_sha256=original_digest, archive_bytes=len(raw),
                owner_before=before, owner_after=after_owner,
                producer=producer, qualified_edge=qualified_edge,
            )
            v11.validate_durable_wrapper(
                wrapper, family, state, qualified=True, deep=True, passed=True,
                original=original, archive_path=original_target,
                archive_sha256=original_digest, archive_bytes=len(raw),
                owner_before=before, owner_after=after_owner,
                producer=producer, qualified_edge=qualified_edge,
            )
            wrapper_raw = v11.canonical(wrapper)
            proof = build_retry_proof(
                family, state, original=original, original_raw=raw,
                wrapper=wrapper, wrapper_raw=wrapper_raw,
                owner_before=before, owner_after=after_owner,
                producer=producer, command=command, qualified_edge=qualified_edge,
            )
            validate_retry_proof(
                proof, family, state, original=original, original_raw=raw,
                wrapper=wrapper, wrapper_raw=wrapper_raw,
                owner_before=before, owner_after=after_owner,
                producer=producer, command=command, qualified_edge=qualified_edge,
            )
            preflight_fresh_destinations(family)
            archive_digest = v11.exclusive_publish(original_target, raw, deep=True)
            published_archive = True
            preserved = v11.read_regular(original_target, "exclusive V11-format original V12 deep")
            final, final_passed = v8.validate_deep(
                preserved, family, edge, state["snapshot"], contract,
            )
            require(preserved == raw and archive_digest == original_digest
                    and final == original and final_passed,
                    "exclusive V11-format original bytes changed or did not qualify")
            wrapper_digest = v11.exclusive_publish(wrapper_target, wrapper_raw, deep=True)
            published_wrapper = True
            preserved_wrapper = v11.read_regular(
                wrapper_target, "exclusive canonical immutable V11-format owner proof",
            )
            actual_wrapper = v11.decode_json(
                preserved_wrapper, "complete actual canonical V11-format owner proof",
            )
            require(preserved_wrapper == wrapper_raw
                    and hashlib.sha256(preserved_wrapper).hexdigest() == wrapper_digest
                    and v11.canonical(actual_wrapper) == preserved_wrapper,
                    "the immutable exclusive V11-format proof lost exact owner provenance")
            v11.validate_durable_wrapper(
                actual_wrapper, family, state, qualified=True, deep=True, passed=True,
                original=final, archive_path=original_target,
                archive_sha256=archive_digest, archive_bytes=len(preserved),
                owner_before=before, owner_after=after_owner,
                producer=producer, qualified_edge=qualified_edge,
            )
            require(v11.read_regular(original_target, "rechecked actual V11-format deep")
                    == preserved,
                    "the exclusively proven V11-format archive was changed")
            proof_raw = v11.canonical(proof)
            proof_path = retry_proof_target(family, True)
            proof_digest = v11.exclusive_publish(proof_path, proof_raw, deep=True)
            final_proof_raw = v11.read_regular(
                proof_path, "separate complete honest exclusive V12 retry provenance",
            )
            final_proof = v11.decode_json(
                final_proof_raw, "complete canonical actual V12 retry provenance",
            )
            require(final_proof_raw == proof_raw
                    and hashlib.sha256(final_proof_raw).hexdigest() == proof_digest
                    and v11.canonical(final_proof) == final_proof_raw,
                    "the separately exclusive truthful V12 invocation proof changed")
            validate_retry_proof(
                final_proof, family, state,
                original=final, original_raw=preserved,
                wrapper=actual_wrapper, wrapper_raw=preserved_wrapper,
                owner_before=before, owner_after=after_owner,
                producer=producer, command=command, qualified_edge=qualified_edge,
            )
            require(v11.read_regular(original_target, "final paired V11-format original")
                    == preserved
                    and v11.read_regular(wrapper_target, "final paired V11-format owner")
                    == preserved_wrapper,
                    "a genuine qualification requires all three unchanged real proofs")
            return {
                "schema": SCHEMA + "-qualified-deep-durable-summary",
                "status": "PASS", "result": "PASS", "mode": "qualified-deep",
                "candidate_family": v11.FAMILIES[family]["contract_name"],
                "candidate_module": v11.FAMILIES[family]["module"],
                "actual_invoking_controller": "V12",
                "v11_executed_this_retry": False,
                "actual_v11_first_invocation_status": "FAIL",
                "campaign_qualified": True, "checks": v11.DEEP_CHECKS,
                "original_v11_format_archive_path":
                    original_target.relative_to(ROOT).as_posix(),
                "original_v11_format_archive_sha256": archive_digest,
                "original_v11_format_owner_proof_path":
                    wrapper_target.relative_to(ROOT).as_posix(),
                "original_v11_format_owner_proof_sha256": wrapper_digest,
                "actual_v12_retry_proof_path": proof_path.relative_to(ROOT).as_posix(),
                "actual_v12_retry_proof_sha256": proof_digest,
                "stdout_is_not_durable_proof": True,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            }
    except ProofV12Failure:
        raise
    except (AssertionError, OSError, ValueError, TypeError, KeyError,
            UnicodeError, subprocess.TimeoutExpired) as error:
        raise preserve_retry_failure(
            family, state, error=error,
            owner_before=before, owner_after=after_owner, producer=producer,
            completed_original=raw, validated_original=passed,
            command=command, published_archive=published_archive,
            published_wrapper=published_wrapper,
        ) from error


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (ProofV12Error, v11.ProofV11Error, AssertionError,
            OSError, ValueError, TypeError, KeyError, UnicodeError):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def synthetic_prior_incident(
    state: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    owner, owner_record, _ = v11.synthetic_owner("rust")
    del owner
    graph = v11.audited_graph_provenance(state)
    metadata = v11.FAMILIES["rust"]
    invalidated = {
        "schema": DEEP_SCHEMA, "python": "3.14.6", "status": "PASS",
        "seed": v11.DEEP_SEED,
        "seeded_case_count": v11.DEEP_SEEDED_CASES,
        "checks": v11.DEEP_CHECKS,
        "candidate_module": metadata["module"], "candidate_family": "RUST",
        "reference_a_sha256": v11.DEEP_REFERENCE_SHA256,
        "reference_b_sha256": v11.DEEP_REFERENCE_SHA256,
        "candidate_sha256": v11.DEEP_REFERENCE_SHA256,
        "candidate": {"observation_sha256": v11.DEEP_REFERENCE_SHA256},
        "public_mismatches": [], "public_mismatch_count": 0,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    failure = {
        "schema": v11.SCHEMA + "-original-producer-failure",
        "status": "FAIL", "result": "FAIL", "mode": "qualified-deep",
        "candidate_family": "RUST", "candidate_module": metadata["module"],
        "actual_failure_reason": "post-original-integrity-failure",
        "actual_child_exit_code": 0, "actual_child_signal": None,
        "timed_out": False,
        "actual_integrity_error_type": "AssertionError",
        "actual_integrity_error_message": "PYTHONDONTWRITEBYTECODE=1 is mandatory",
        "complete_original_observation_archive": True,
        "original_correctness_observations": "INVALIDATED",
        "invalidated_complete_original_evidence_path": PRIOR_INVALIDATED_RELATIVE,
        "invalidated_complete_original_evidence_sha256": PRIOR_INVALIDATED_SHA256,
        "invalidated_complete_original_actual_status": "NOT VALIDATED",
        "passing_evidence_published": False, "campaign_qualified": False,
        "production_observations_invented": False,
        "refresh_protocol_path": v11.PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": V11_PROTOCOL_SHA256,
        "actual_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "actual_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "stdout": v11.observed_stream(b"synthetic-source-only-original-output", True),
        "stderr": v11.observed_stream(b"", True),
        "native_owner_before": owner_record,
        "full_current_family_source_sha256": {
            path: graph["all_family_source_sha256_by_path"][path]
            for path in metadata["sources"]
        },
        "full_current_family_native_elf_sha256": {
            path: graph["all_family_native_elf_sha256_by_path"][path]
            for path in metadata["native"].values()
        },
        "all_family_audited_provenance": graph,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    summary = validate_prior_incident_documents(failure, invalidated, state)
    return failure, invalidated, summary


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime_source_only()
    inherited = v11.candidate_free_self_test()
    require(inherited.get("status") == "PASS"
            and inherited.get("candidate_imports") == 0
            and inherited.get("subprocesses") == 0
            and inherited.get("file_writes") == 0
            and inherited.get("clock_samples") == 0
            and inherited.get("historical_evidence_reads") == 0
            and inherited.get("actual_audit_report_reads") == 0
            and inherited.get("synthetic_results_qualify_candidates") is False
            and isinstance(inherited.get("check_count"), int)
            and inherited["check_count"] >= 150,
            "the original frozen V11 candidate-free boundary was weakened")
    source_raw = v11.read_regular(ROOT / SOURCE_RELATIVE,
                                   "additive candidate-free V12 controller source")
    protocol_raw = v11.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    source_tree = ast.parse(source_raw.decode("utf-8"), filename=SOURCE_RELATIVE)
    source_sha256 = hashlib.sha256(source_raw).hexdigest()
    controls: list[dict[str, Any]] = []

    def accept(label: str, condition: Any) -> None:
        controls.append({"name": label, "passed": bool(condition)})

    with v11.source_only_boundary() as effects:
        accept("parse-additive-v12-controller-without-production-execution",
               isinstance(source_tree, ast.Module))
        accept("authenticate-exact-frozen-v12-protocol",
               hashlib.sha256(protocol_raw).hexdigest() == PROTOCOL_SHA256)
        accept("authenticate-exact-current-v12-controller-bytes",
               v11.valid_sha256(source_sha256))
        accept("preserve-original-v11-source-pin", v11.valid_sha256(V11_SOURCE_SHA256))
        accept("preserve-original-v11-protocol-pin",
               V11_PROTOCOL_SHA256 == v11.REFRESH_PROTOCOL_SHA256)
        accept("preserve-first-genuine-v11-failure-pin",
               v11.valid_sha256(PRIOR_FAILURE_SHA256))
        accept("preserve-first-genuine-v11-invalidated-original-pin",
               v11.valid_sha256(PRIOR_INVALIDATED_SHA256))
        accept("preserve-actual-v10-base-audit-pin",
               v11.valid_sha256(ACTUAL_V10_BASE_REPORT_SHA256))
        accept("preserve-actual-v10-strict-audit-pin",
               v11.valid_sha256(ACTUAL_V10_STRICT_REPORT_SHA256))
        accept("preserve-three-genuine-independent-native-families",
               tuple(v11.FAMILIES) == ("rust", "vm", "zig"))
        accept("preserve-all-twelve-audited-owned-family-sources",
               sum(len(row["sources"]) for row in v11.FAMILIES.values()) == 12)
        accept("preserve-all-five-independently-owned-native-elf-files",
               sum(len(row["native"]) for row in v11.FAMILIES.values()) == 5)
        accept("preserve-all-223198-original-edge-correctness-observations",
               v11.EDGE_CHECKS == 223198)
        accept("preserve-all-49-original-edge-correctness-categories",
               v11.EDGE_CATEGORIES == 49)
        accept("preserve-all-393-original-independent-deep-observations",
               v11.DEEP_CHECKS == 393)
        accept("preserve-all-64-original-seeded-deep-observations",
               v11.DEEP_SEEDED_CASES == 64)
        environment = {
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        }
        accept("accept-exact-source-only-synthetic-parent-environment",
               validate_parent_environment(environment) == environment)
        accept("construct-exact-five-key-explicit-original-worker-environment",
               set(worker_environment()) == EXPLICIT_WORKER_ENVIRONMENT_KEYS)
        for key in environment:
            absent = dict(environment)
            del absent[key]
            controls.append(rejected("reject-missing-required-parent-value:" + key,
                                     lambda value=absent: validate_parent_environment(value)))
            for label, changed in (
                ("none", None), ("empty", ""), ("space", " "),
                ("integer", 1), ("false", "false"),
                ("different", "wrong-source-only-value"),
            ):
                broken = {**environment, key: changed}
                controls.append(rejected(
                    "reject-invalid-parent-value:" + key + ":" + label,
                    lambda value=broken: validate_parent_environment(value),
                ))
        for label, value in (
            ("relative", "."),
            ("relative-workspace", "home/dev-user/src/rebar"),
            ("trailing-separator", str(ROOT) + "/"),
            ("extra-search-path", str(ROOT) + os.pathsep + "/tmp"),
            ("parent-alias", str(ROOT / ".." / ROOT.name)),
            ("temporary-root", "/tmp"),
        ):
            controls.append(rejected(
                "reject-nonexact-parent-pythonpath:" + label,
                lambda changed=value: validate_parent_environment({
                    **environment, "PYTHONPATH": changed,
                }),
            ))
        forbidden = {
            "preflight_targets", "run_original", "refresh_deep", "observe_owner",
            "preserve_producer_failure", "preserve_owner_failure",
            "retain_invalidated_original",
        }
        for name in sorted(forbidden):
            accept("never-call-original-v11-failure-or-retry-publisher:" + name,
                   not any(isinstance(node, ast.Call)
                           and isinstance(node.func, ast.Attribute)
                           and node.func.attr == name
                           for node in ast.walk(source_tree)))
        for name in (
            "validate_deep", "validate_original_edge", "audit_v11_reports",
            "authenticate_history", "build_durable_wrapper",
            "validate_durable_wrapper", "run_native_worker", "exclusive_publish",
            "restore_complete_stream", "fresh_target",
        ):
            accept("require-authentic-frozen-original-proof-primitive:" + name,
                   any(isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Attribute)
                       and node.func.attr == name
                       for node in ast.walk(source_tree)))
        for family in v11.FAMILIES:
            metadata = v11.FAMILIES[family]
            expected_v11 = (
                "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
                + "-POSTFINAL-CURRENT-BUILD-V11-PASS"
            )
            accept("retain-exact-frozen-v18-original-v11-archive:" + family,
                   v11.deep_target(family, True).name == expected_v11 + ".json.gz")
            accept("retain-exact-frozen-v18-original-v11-owner-proof:" + family,
                   v11.deep_proof_target(family, True).name
                   == expected_v11 + "-PROOF.json")
            targets = (
                v11.deep_target(family, True), v11.deep_proof_target(family, True),
                retry_proof_target(family, True), retry_proof_target(family, False),
                retry_failure_target(family), retry_invalidated_target(family),
            )
            accept("separate-all-six-original-and-additive-retry-targets:" + family,
                   len(set(targets)) == 6)
            for index, target in enumerate(targets):
                accept("retain-canonical-family-audit-target:"
                       + family + ":" + str(index),
                       target.parent == ROOT / "candidates/audits"
                       and target.is_absolute()
                       and target != ROOT / PRIOR_FAILURE_RELATIVE
                       and target != ROOT / PRIOR_INVALIDATED_RELATIVE)
            accept("retain-distinct-passing-and-failing-v12-retry-proofs:" + family,
                   retry_proof_target(family, True) != retry_proof_target(family, False))
            accept("retain-complete-owned-family-source-denominator:" + family,
                   len(metadata["sources"]) == {"rust": 7, "vm": 2, "zig": 3}[family])
            accept("retain-complete-owned-family-native-denominator:" + family,
                   len(metadata["native"]) == {"rust": 2, "vm": 1, "zig": 2}[family])
        rust_state, _ = v11.synthetic_durable_state("rust", qualified=True)
        failure, invalidated, incident = synthetic_prior_incident(rust_state)
        accept("validate-synthetic-original-v11-failure-without-reading-archives",
               incident["actual_v11_first_invocation_status"] == "FAIL"
               and incident["actual_v11_first_original_was_invalidated"] is True
               and incident["first_failure_retroactively_qualified"] is False)
        for key in tuple(failure):
            tampered = copy.deepcopy(failure)
            value = tampered[key]
            tampered[key] = (
                None if value is not None
                else "source-only-invalidated-failure-substitution"
            )
            controls.append(rejected(
                "reject-tampered-genuine-v11-first-failure:" + key,
                lambda value=tampered: validate_prior_incident_documents(
                    value, invalidated, rust_state,
                ),
            ))
        for key in tuple(invalidated):
            tampered = copy.deepcopy(invalidated)
            value = tampered[key]
            tampered[key] = (
                None if value is not None
                else "source-only-invalidated-original-substitution"
            )
            controls.append(rejected(
                "reject-tampered-complete-invalidated-first-v11-original:" + key,
                lambda value=tampered: validate_prior_incident_documents(
                    failure, value, rust_state,
                ),
            ))
        for family in v11.FAMILIES:
            state, record = v11.synthetic_durable_state(family, qualified=True)
            state["controller"] = {
                "source_path": SOURCE_RELATIVE, "source_sha256": source_sha256,
                "protocol_path": PROTOCOL_RELATIVE,
                "protocol_sha256": PROTOCOL_SHA256,
                "v11_format_source_path": v11.SOURCE_RELATIVE,
                "v11_format_source_sha256": V11_SOURCE_SHA256,
                "v11_format_protocol_path": v11.PROTOCOL_RELATIVE,
                "v11_format_protocol_sha256": V11_PROTOCOL_SHA256,
            }
            state["parent_environment"] = dict(environment)
            state["prior_incident"] = incident
            state["audits"]["pins"]["base_report"] = ACTUAL_V10_BASE_REPORT_SHA256
            state["audits"]["pins"]["strict_report"] = ACTUAL_V10_STRICT_REPORT_SHA256
            edge = {
                "status": "PASS", "campaign_qualified": True,
                "archive_path": v11.edge_target(family, True, True)
                    .relative_to(ROOT).as_posix(),
                "archive_sha256": v11.synthetic_digest("source-only-edge:" + family),
                "proof_path": v11.edge_proof_target(family, True, True)
                    .relative_to(ROOT).as_posix(),
                "proof_sha256": v11.synthetic_digest("source-only-edge-proof:" + family),
            }
            original = {
                "candidate_sha256": v11.DEEP_REFERENCE_SHA256,
                "public_mismatch_count": 0,
                "public_mismatch_family_counts": {},
            }
            raw = ("source-only-synthetic-original:" + family).encode("ascii")
            command = ["source-only-original-controller", family]
            producer = subprocess.CompletedProcess(
                args=command, returncode=0,
                stdout=("synthetic-original-stdout:" + family).encode("ascii"),
                stderr=b"",
            )
            wrapper = v11.build_durable_wrapper(
                family, state, qualified=True, deep=True, passed=True,
                original=original, archive_path=v11.deep_target(family, True),
                archive_sha256=hashlib.sha256(raw).hexdigest(),
                archive_bytes=len(raw), owner_before=record, owner_after=record,
                producer=producer, qualified_edge=edge,
            )
            v11.validate_durable_wrapper(
                wrapper, family, state, qualified=True, deep=True, passed=True,
                original=original, archive_path=v11.deep_target(family, True),
                archive_sha256=hashlib.sha256(raw).hexdigest(),
                archive_bytes=len(raw), owner_before=record, owner_after=record,
                producer=producer, qualified_edge=edge,
            )
            wrapper_raw = v11.canonical(wrapper)
            proof = build_retry_proof(
                family, state, original=original, original_raw=raw,
                wrapper=wrapper, wrapper_raw=wrapper_raw,
                owner_before=record, owner_after=record,
                producer=producer, command=command, qualified_edge=edge,
            )
            validate_retry_proof(
                proof, family, state, original=original, original_raw=raw,
                wrapper=wrapper, wrapper_raw=wrapper_raw,
                owner_before=record, owner_after=record,
                producer=producer, command=command, qualified_edge=edge,
            )
            accept("validate-synthetic-v11-format-and-honest-v12-proof:" + family,
                   proof["actual_invoking_controller"] == "V12"
                   and proof["v11_executed_this_retry"] is False
                   and proof["preserved_actual_first_v11_failure"]
                       ["actual_v11_first_invocation_status"] == "FAIL")
            for key in tuple(proof):
                tampered = copy.deepcopy(proof)
                value = tampered[key]
                tampered[key] = (
                    None if value is not None
                    else "source-only-v12-proof-substitution"
                )
                controls.append(rejected(
                    "reject-tampered-honest-separate-v12-retry-proof:"
                    + family + ":" + key,
                    lambda value=tampered, selected=family,
                    saved_state=state, saved_original=original, saved_raw=raw,
                    saved_wrapper=wrapper, saved_wrapper_raw=wrapper_raw,
                    saved_record=record, saved_producer=producer,
                    saved_command=command, saved_edge=edge:
                        validate_retry_proof(
                            value, selected, saved_state,
                            original=saved_original, original_raw=saved_raw,
                            wrapper=saved_wrapper, wrapper_raw=saved_wrapper_raw,
                            owner_before=saved_record, owner_after=saved_record,
                            producer=saved_producer, command=saved_command,
                            qualified_edge=saved_edge,
                        ),
                ))
        for name, action in (
            ("candidate-import", lambda: builtins.__import__("candidates.rust_candidate")),
            ("foreign-engine-import", lambda: builtins.__import__("regex")),
            ("candidate-importlib", lambda: importlib.import_module("candidates.zig_candidate")),
            ("foreign-engine-importlib", lambda: importlib.import_module("pcre2")),
            ("actual-first-v11-failure-read",
             lambda: v11.read_regular(ROOT / PRIOR_FAILURE_RELATIVE, "forbidden first failure")),
            ("actual-first-v11-invalidated-read",
             lambda: v11.read_regular(ROOT / PRIOR_INVALIDATED_RELATIVE,
                                      "forbidden original first failure")),
            ("actual-v10-base-report-read",
             lambda: v11.read_regular(ROOT / v11.V10_BASE_REPORT_RELATIVE,
                                      "forbidden actual base audit")),
            ("actual-v10-strict-report-read",
             lambda: v11.read_regular(ROOT / v11.V10_STRICT_REPORT_RELATIVE,
                                      "forbidden actual strict audit")),
            ("actual-v11-edge-read",
             lambda: v11.read_regular(v11.edge_target("rust", True, True),
                                      "forbidden actual original edge")),
            ("actual-v11-deep-read",
             lambda: v11.read_regular(v11.deep_target("rust", True),
                                      "forbidden actual deep proof")),
            ("holdout-read", lambda: builtins.open(ROOT / "performance/holdout.json", "rb")),
            ("unrelated-read", lambda: builtins.open(ROOT / "README.md", "rb")),
            ("clock-sample", lambda: time.perf_counter()),
            ("original-worker", lambda: subprocess.run(["forbidden-v12-worker"])),
            ("private-worker-directory", lambda: tempfile.TemporaryDirectory()),
            ("evidence-write", lambda: retry_proof_target("rust", True).write_bytes(b"x")),
            ("candidate-write", lambda: (ROOT / "candidates/v12-forbidden").write_text("x")),
            ("preflight-without-required-parent",
             lambda: validate_parent_environment({})),
        ):
            controls.append(rejected("enforce-candidate-free-v12-boundary:" + name, action))
        accept("block-all-source-only-candidate-or-foreign-engine-imports",
               effects["candidate_import_attempts_blocked"] >= 4)
        accept("block-all-source-only-production-and-evidence-reads",
               effects["evidence_read_attempts_blocked"] >= 6)
        accept("block-all-source-only-worker-or-subprocess-attempts",
               effects["worker_attempts_blocked"] >= 2)
        accept("block-all-source-only-clock-sampling-attempts",
               effects["clock_attempts_blocked"] >= 1)
        accept("block-all-source-only-filesystem-write-attempts",
               effects["write_attempts_blocked"] >= 2)
        accept("never-import-any-production-candidate-during-source-controls",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
        accept("retain-at-least-150-distinct-real-v12-source-only-controls",
               len(controls) >= 150)
        require(len({row["name"] for row in controls}) == len(controls),
                "the V12 source-only controls silently duplicated their denominator")
        require(all(row["passed"] for row in controls),
                "a genuine V12 source-only environment, provenance, or isolation control failed")
        observed = dict(effects)
    verify_runtime_source_only()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS",
        "result": "PASS", "passed": True,
        "check_count": len(controls), "checks": controls,
        "inherited_v11_check_count": inherited["check_count"],
        "inherited_v11_source_only_status": inherited["status"],
        "candidate_imports": 0, "subprocesses": 0,
        "file_writes": 0, "clock_samples": 0,
        "historical_evidence_reads": 0, "actual_audit_report_reads": 0,
        "holdout_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "actual_v12_controller_sha256": source_sha256,
        "actual_v12_protocol_sha256": PROTOCOL_SHA256,
        "actual_v11_format_source_sha256": V11_SOURCE_SHA256,
        "actual_v11_format_protocol_sha256": V11_PROTOCOL_SHA256,
        "actual_first_v11_failure_sha256": PRIOR_FAILURE_SHA256,
        "actual_first_v11_invalidated_original_sha256": PRIOR_INVALIDATED_SHA256,
        "actual_v10_base_report_sha256": ACTUAL_V10_BASE_REPORT_SHA256,
        "actual_v10_strict_report_sha256": ACTUAL_V10_STRICT_REPORT_SHA256,
        "original_edge_checks": v11.EDGE_CHECKS,
        "original_edge_categories": v11.EDGE_CATEGORIES,
        "original_deep_checks": v11.DEEP_CHECKS,
        "original_deep_seeded_cases": v11.DEEP_SEEDED_CASES,
        "independent_family_count": len(v11.FAMILIES),
        "complete_owned_source_count":
            sum(len(row["sources"]) for row in v11.FAMILIES.values()),
        "complete_native_elf_count":
            sum(len(row["native"]) for row in v11.FAMILIES.values()),
        "self_test_requires_actual_parent_retry_environment": False,
        "v11_first_failure_retroactively_qualified": False,
        "stdout_or_unpaired_archive_qualifies": False,
        "blocked_effect_attempts": observed,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--qualified-deep", action="store_true")
    parser.add_argument("--module", choices=tuple(
        value["module"] for value in v11.FAMILIES.values()
    ))
    parser.add_argument("--base-report-sha256")
    parser.add_argument("--strict-report-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(options.module is None and options.base_report_sha256 is None
                and options.strict_report_sha256 is None,
                "candidate-free V12 controls cannot select a candidate or actual report")
        report = candidate_free_self_test()
    else:
        require(options.qualified_deep and options.module is not None,
                "V12 authorizes only one real original qualified family deep retry")
        verify_parent_retry_environment()
        family = next(name for name, row in v11.FAMILIES.items()
                      if row["module"] == options.module)
        report = refresh_qualified_deep(
            family, options.base_report_sha256, options.strict_report_sha256,
        )
    print(json.dumps(report, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofV12Failure as error:
        print(json.dumps({
            "schema": SCHEMA + "-preserved-failure", "status": "FAIL",
            "message": str(error), "evidence": error.evidence,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")),
            file=sys.stderr, flush=True)
        raise SystemExit(1) from error
