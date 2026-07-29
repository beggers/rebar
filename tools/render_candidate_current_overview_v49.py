#!/usr/bin/env python3
"""Render the honest current results and a never-run Rust source variant."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v49.py"
OUTPUT = "docs/evidence/candidate-current-overview-v49"
SCHEMA = "rebar-candidate-current-overview-v49"
FEATURE_SCHEMA = "rebar-phase2-owned-rust-buffer-shape-source-repair-v1-source-freeze"
FEATURE_STATUS = (
    "SOURCE FROZEN; FIRST-PARTY RUST BUFFER-SHAPE VARIANT NOT BUILT OR RUN"
)
V48 = {
    "source": (
        "tools/render_candidate_current_overview_v48.py",
        "29604bd560dcba08f95ca8bcc792bf277c43a4680d94a82990fd341a1b0f6394",
        89718,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v48.inputs.json",
        "d1bc5998012a8f174788a4c28fad7fa1116078a3cbb859b0f952eb65777e33da",
        523944,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v48.json",
        "bfd591aebf6aea805c8f6a4b5665d87ceca6b2574513bb5cdfb8331b36176305",
        1428930,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v48.svg",
        "cf8955199d714854faeea4d5c0cabf4431010949a7b7d5ed81d5b65f14b74903",
        20331,
    ),
}
FEATURE_PATHS = {
    "variant": "candidates/rust/variants/buffer_shape_v1/py_bridge.c",
    "verifier": "tools/apply_owned_rust_buffer_shape_source_repair_v1.py",
    "protocol": "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-REPAIR-V1.md",
    "contract": "oracle/phase2/rust-buffer-shape-source-repair-v1.json",
}
FEATURE_FLAGS = {
    "variant": "variant_source",
    "verifier": "feature_verifier",
    "protocol": "feature_protocol",
    "contract": "feature_contract",
}
V13_BRIDGE = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
V13_ADAPTER = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-"
    "phase2-v13-rust-pattern-repr-original-p0-"
    "failures-publication-receipt.json",
    "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943",
    8450,
)
PUBLIC_COUNTS = {
    "PASS": 17,
    "FAIL": 7,
    "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1,
    "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22,
    "FAIL": 1,
    "NOT RUN": 3,
    "NOT ESTABLISHED": 2,
    "NOT MEASURED": 3,
    "NOT OPENED": 1,
}
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]


def load_v48() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType,
]:
    path, expected, size = V48["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject a substituted pushed V48 renderer")
        parts: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            if not piece:
                raise ValueError("reject a truncated pushed V48 renderer")
            parts.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended pushed V48 renderer bytes")
        raw = b"".join(parts)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != expected
            or (
                before.st_dev, before.st_ino, before.st_size,
                before.st_nlink, before.st_mtime_ns, before.st_ctime_ns,
            ) != (
                after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns, after.st_ctime_ns,
            )
        ):
            raise ValueError("reject V48 replacement during authentication")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_pushed_rust_failure_graph_v48")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    v47, v46, v45, v44, v43, v42, v41, v40, base = previous.load_v47()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v48"
        and previous.SELF == path
        and previous.RECEIPT == RECEIPT
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS,
        "load only the exact pushed V48 real Rust failure graph",
    )
    return previous, v47, v46, v45, v44, v43, v42, v41, v40, base


def walk_records(value: object):
    if type(value) is dict:
        yield value
        for child in value.values():
            yield from walk_records(child)
    elif type(value) is list:
        for child in value:
            yield from walk_records(child)


def has_pin(value: object, pin: dict) -> bool:
    return any(
        record.get("path") == pin["path"]
        and record.get("sha256") == pin["sha256"]
        and record.get("bytes") == pin["bytes"]
        for record in walk_records(value)
    )


def validate_contract(base: types.ModuleType, contract: object,
                      owners: dict[str, dict]) -> None:
    base.need(type(contract) is dict, "reject a missing Rust source contract")
    assert isinstance(contract, dict)
    base.need(
        contract.get("schema") == FEATURE_SCHEMA
        and contract.get("version") == 1
        and contract.get("phase") == "CANDIDATES"
        and contract.get("status") == FEATURE_STATUS
        and contract.get("family") == "rust",
        "reject a source freeze misrepresented as a new, built or tested family",
    )
    source_pin = {
        "path": owners["verifier"]["path"],
        "sha256": owners["verifier"]["sha256"],
    }
    protocol_pin = {
        "path": owners["protocol"]["path"],
        "sha256": owners["protocol"]["sha256"],
    }
    variant_pin = base.pin(
        owners["variant"]["path"], owners["variant"]["sha256"],
        owners["variant"]["bytes"],
    )
    base.need(
        contract.get("source") == source_pin
        and contract.get("protocol") == protocol_pin,
        "bind the exact independent first-party Rust source verifier and protocol",
    )
    variant = contract.get("candidate_variant")
    base.need(type(variant) is dict, "reject an omitted full Rust variant owner")
    assert isinstance(variant, dict)
    base.need(
        all(variant.get(key) == value for key, value in variant_pin.items())
        and (
            variant.get("derived_from_actual_v13_sha256") == V13_BRIDGE
            or variant.get("actual_corrected_bridge_sha256") == V13_BRIDGE
        )
        and variant.get("materialized") is True
        and variant.get("built") is False
        and variant.get("candidate_matching") == "NOT RUN",
        "bind the complete actual V13-derived Rust source without claiming a run",
    )
    overview = contract.get("current_v48_overview")
    base.need(
        type(overview) is dict
        and overview.get("version") == 48
        and overview.get("authenticated_evidence_owner_lower_bound") == 168
        and overview.get("authenticated_history_reference_lower_bound") == 173
        and overview.get("first_party_source_inventory_family_count") == 6
        and overview.get("frozen_corrected_runner_source_family_count") == 3
        and overview.get("qualified_candidate_count") == 0,
        "bind exact prior counts without claiming source readiness or a winner",
    )
    assert isinstance(overview, dict)
    preserved = contract.get("preserved_rust_owners")
    base.need(type(preserved) is dict,
              "bind separately frozen immutable Rust and V48 evidence")
    assert isinstance(preserved, dict)
    overview_roles = {
        "source": "current_v48_renderer",
        "inputs": "current_v48_inputs",
        "summary": "current_v48_summary",
        "svg": "current_v48_chart",
    }
    for role, item in V48.items():
        base.need(
            preserved.get(overview_roles[role]) == base.pin(*item),
            "reject substituted or stale V48 feature provenance: " + role,
        )
    adapter = contract.get("preserved_public_adapter")
    base.need(
        preserved.get("actual_v7_small_plaintext_receipt")
        == base.pin(*RECEIPT)
        and type(adapter) is dict
        and adapter.get("actual_corrected_adapter_sha256") == V13_ADAPTER
        and adapter.get("actual_corrected_adapter_bytes") == 31934
        and adapter.get("canonical_adapter_modified") is False
        and adapter.get("runtime_adapter_activated") is False,
        "bind the actual small V7 failure receipt and preserved V13 adapter",
    )
    diagnosis = contract.get("historically_reported_buffer_shape_diagnosis")
    base.need(
        type(diagnosis) is dict
        and diagnosis.get("repairs_verified") == "NOT MEASURED",
        "do not promote historical or prospective diagnosis to verified repair",
    )
    base.need(
        diagnosis.get("mutable_live_log_read") is False
        and diagnosis.get("case_histogram_rederived_by_this_source_freeze")
        is False
        and diagnosis.get("repair_effect") == "NOT MEASURED",
        "never read a mutable current log or infer failure categories from a receipt",
    )
    boundary = contract.get("phase_boundary")
    base.need(
        type(boundary) is dict
        and boundary.get("actual_archives_opened") == 0
        and boundary.get("actual_archives_decompressed") == 0
        and boundary.get("actual_candidate_workers_started") == 0
        and boundary.get("actual_native_libraries_loaded") == 0
        and boundary.get("actual_clock_samples") == 0
        and boundary.get("actual_hidden_cases_read") == 0
        and boundary.get("actual_holdout_cases_read") == 0
        and boundary.get("source_variant_materialized") is True
        and boundary.get("source_variant_built") is False
        and boundary.get("source_variant_candidate_matching") == "NOT RUN"
        and boundary.get("source_variant_candidate_correctness") == "NOT MEASURED"
        and boundary.get("holdout") == "NOT OPENED"
        and boundary.get("holdout_generated") is False
        and boundary.get("qualified_candidate_count") == 0
        and boundary.get("winner_selected") is False,
        "reject any native run, archive access, benchmark or hidden-case effect",
    )


def make_feature_proof(base: types.ModuleType, owners: dict[str, dict],
                       contract: dict) -> dict:
    base.need(
        set(owners) == set(FEATURE_PATHS)
        and len({owner.get("path") for owner in owners.values()}) == 4
        and len({owner.get("inode") for owner in owners.values()}) == 4,
        "count exactly four distinct real first-party source owners",
    )
    for role, path in FEATURE_PATHS.items():
        owner = owners[role]
        base.need(
            type(owner) is dict
            and owner.get("path") == path
            and base.checked(owner.get("sha256"), "Rust variant " + role)
            == owner.get("sha256")
            and type(owner.get("bytes")) is int
            and 0 < owner["bytes"] <= base.OWNER_LIMIT
            and owner.get("device") == 2064
            and type(owner.get("inode")) is int and owner["inode"] > 0
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and owner.get("uid") == os.geteuid(),
            "reject a linked, missing, forged or nonprivate Rust " + role,
        )
    validate_contract(base, contract, owners)
    proof = {
        "schema": SCHEMA + "-authenticated-rust-buffer-shape-source-freeze",
        "version": 1,
        "status": FEATURE_STATUS,
        "family": "rust",
        "same_existing_rust_family": True,
        "new_candidate_family_count": 0,
        "source_frozen": True,
        "source_owner_count": 4,
        "owners": copy.deepcopy(owners),
        "complete_contract": copy.deepcopy(contract),
        "actual_graph_predecessor_version": 48,
        "actual_v7_semantic_mismatch_count": 928,
        "actual_v7_explicitly_verified_passing_case_count": 8965,
        "actual_v7_candidate_workers": 13,
        "build_status": "NOT BUILT",
        "matching_status": "NOT RUN",
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "repair_effectiveness": "NOT MEASURED",
        "verified_repaired_case_count": "NOT MEASURED",
        "failure_category_counts_proven_by_small_receipt": False,
        "candidate_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "source_build_archives_opened": 0,
        "failure_archives_opened": 0,
        "failure_archives_inflated": 0,
        "holdout_opened": False,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "qualified": False,
        "winner_selected": False,
        "authenticated_evidence_owner_lower_bound_before_freeze": 168,
        "authenticated_history_reference_lower_bound_before_freeze": 173,
        "new_exact_feature_owner_count": 4,
        "authenticated_evidence_owner_lower_bound_after_freeze": 172,
        "authenticated_history_reference_lower_bound_after_freeze": 177,
    }
    proof["complete_source_feature_binding_sha256"] = base.digest(
        base.canonical(proof),
    )
    validate_feature_proof(base, proof)
    return proof


def validate_feature_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject missing source-only Rust proof")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-rust-buffer-shape-source-freeze",
        "version": 1,
        "status": FEATURE_STATUS,
        "family": "rust",
        "same_existing_rust_family": True,
        "new_candidate_family_count": 0,
        "source_frozen": True,
        "source_owner_count": 4,
        "actual_graph_predecessor_version": 48,
        "actual_v7_semantic_mismatch_count": 928,
        "actual_v7_explicitly_verified_passing_case_count": 8965,
        "actual_v7_candidate_workers": 13,
        "build_status": "NOT BUILT",
        "matching_status": "NOT RUN",
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "repair_effectiveness": "NOT MEASURED",
        "verified_repaired_case_count": "NOT MEASURED",
        "failure_category_counts_proven_by_small_receipt": False,
        "candidate_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "source_build_archives_opened": 0,
        "failure_archives_opened": 0,
        "failure_archives_inflated": 0,
        "holdout_opened": False,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "qualified": False,
        "winner_selected": False,
        "authenticated_evidence_owner_lower_bound_before_freeze": 168,
        "authenticated_history_reference_lower_bound_before_freeze": 173,
        "new_exact_feature_owner_count": 4,
        "authenticated_evidence_owner_lower_bound_after_freeze": 172,
        "authenticated_history_reference_lower_bound_after_freeze": 177,
    }
    for name, value in expected.items():
        base.need(proof.get(name) == value,
                  "reject an invented Rust repair, run or owner: " + name)
    owners = proof.get("owners")
    base.need(type(owners) is dict and set(owners) == set(FEATURE_PATHS),
              "reject a missing or invented source feature owner")
    assert isinstance(owners, dict)
    validate_contract(base, proof.get("complete_contract"), owners)
    body = {
        key: value for key, value in proof.items()
        if key != "complete_source_feature_binding_sha256"
    }
    base.need(
        proof.get("complete_source_feature_binding_sha256")
        == base.digest(base.canonical(body)),
        "bind all four feature owners without inflating outcome evidence",
    )


def authenticate_feature(base: types.ModuleType,
                         options: argparse.Namespace) -> dict:
    owners: dict[str, dict] = {}
    contents: dict[str, bytes] = {}
    for role, path in FEATURE_PATHS.items():
        flag = FEATURE_FLAGS[role]
        fingerprint = base.checked(
            getattr(options, flag + "_sha256"), "actual source feature " + role,
        )
        size = getattr(options, flag + "_bytes")
        base.need(type(size) is int and 0 < size <= base.OWNER_LIMIT,
                  "independently pin complete Rust source feature " + role)
        contents[role], owners[role] = base.read_owner(
            path, fingerprint, size, private=True,
        )
    contract = base.document(contents["contract"],
                             "complete first-party Rust source-freeze contract")
    protocol = contents["protocol"].decode("utf-8")
    base.need(
        "NOT BUILT" in protocol.upper()
        and "NOT MEASURED" in protocol.upper()
        and "RUST" in protocol.upper(),
        "require a human-readable first-party source-only Rust freeze",
    )
    return make_feature_proof(base, owners, contract)


def v48_failure_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        **{
            "campaign_" + role + "_sha256": pin[1]
            for role, pin in previous.CAMPAIGN.items()
        },
        receipt_sha256=previous.RECEIPT[1],
        receipt_bytes=previous.RECEIPT[2],
        receipt_inode=previous.RECEIPT_INODE,
        receipt_device=previous.DEVICE,
        archive_sha256=previous.ARCHIVE[1],
        archive_bytes=previous.ARCHIVE[2],
        archive_inode=previous.ARCHIVE_INODE,
        archive_device=previous.DEVICE,
        journal_sha256=previous.JOURNAL_SHA256,
    )


def authenticate_v48(
    previous: types.ModuleType, v47: types.ModuleType,
    v46: types.ModuleType, v45: types.ModuleType,
    v44: types.ModuleType, v43: types.ModuleType,
    v42: types.ModuleType, v41: types.ModuleType,
    v40: types.ModuleType, base: types.ModuleType,
    supplied: dict[str, str],
) -> tuple[dict, dict, bytes]:
    raw: dict[str, bytes] = {}
    for role, pin in V48.items():
        base.need(
            base.checked(supplied.get(role), "pushed V48 " + role) == pin[1],
            "require the actual exact current pushed V48 " + role,
        )
        raw[role], _ = base.read_owner(*pin, private=True)
    old = base.document(raw["summary"], "complete pushed V48 summary")
    inputs = base.document(raw["inputs"], "complete pushed V48 inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(v47, v46, v45, v44, v43, v42, v41, v40,
                               base, snapshot)
    old47, _, old47svg = previous.authenticate_v47(
        v47, v46, v45, v44, v43, v42, v41, v40, base,
        {role: item[1] for role, item in previous.V47.items()},
    )
    proof = previous.authenticate_result(base, v48_failure_options(previous))
    actual = previous.actual_current_rust_campaign(proof)
    base.need(
        old47.get("version") == 47
        and old.get("schema") == "rebar-candidate-current-overview-v48-summary"
        and old.get("version") == 48
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V48["source"])
        and old.get("inputs") == base.pin(*V48["inputs"])
        and old.get("svg") == base.pin(*V48["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v48-inputs"
        and inputs.get("version") == 48
        and inputs.get("renderer") == base.pin(*V48["source"])
        and raw["svg"] == previous.make_svg(
            v47, v46, v45, v44, v43, v42, v41, v40, base,
            snapshot, old47svg, V48["source"][1], V48["inputs"][1],
        )
        and snapshot.get("actual_rust_v7_campaign_failure") == proof
        and old.get("actual_rust_original_campaign") == actual
        and old.get("actual_complete_rust_campaign") == actual
        and old.get("current_complete_rust_campaign") == actual
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("actually_tested_corrected_candidate_families") == ["rust"]
        and old.get("actually_tested_corrected_candidate_family_count") == 1
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("actually_runnable_candidate_family_count") == 0
        and old.get("qualified_candidate_count") == 0
        and old.get("authenticated_evidence_owner_lower_bound") == 168
        and old.get("authenticated_history_reference_lower_bound") == 173
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "reproduce the whole pushed V48 real Rust failure before adding source",
    )
    return old, inputs, raw["svg"]


def feature_fields(proof: dict) -> dict:
    owners = proof["owners"]
    return {
        "rust_buffer_shape_v1_source_freeze": copy.deepcopy(proof),
        "rust_buffer_shape_v1_feature_status": FEATURE_STATUS,
        "rust_buffer_shape_v1_family": "rust",
        "rust_buffer_shape_v1_same_existing_rust_family": True,
        "rust_buffer_shape_v1_new_candidate_family_count": 0,
        "rust_buffer_shape_v1_source_frozen": True,
        "rust_buffer_shape_v1_variant_source": copy.deepcopy(owners["variant"]),
        "rust_buffer_shape_v1_verifier_source": copy.deepcopy(owners["verifier"]),
        "rust_buffer_shape_v1_protocol": copy.deepcopy(owners["protocol"]),
        "rust_buffer_shape_v1_contract": copy.deepcopy(owners["contract"]),
        "rust_buffer_shape_v1_exact_feature_owner_count": 4,
        "rust_buffer_shape_v1_build_status": "NOT BUILT",
        "rust_buffer_shape_v1_matching_status": "NOT RUN",
        "rust_buffer_shape_v1_semantic_mismatch_count": "NOT MEASURED",
        "rust_buffer_shape_v1_verified_passing_case_count": "NOT MEASURED",
        "rust_buffer_shape_v1_repair_effectiveness": "NOT MEASURED",
        "rust_buffer_shape_v1_verified_repaired_case_count": "NOT MEASURED",
        "rust_buffer_shape_v1_failure_categories_proven_by_receipt": False,
        "rust_buffer_shape_v1_candidate_workers_started": 0,
        "rust_buffer_shape_v1_compiler_processes_started": 0,
        "rust_buffer_shape_v1_native_libraries_loaded": 0,
        "rust_buffer_shape_v1_archive_reads_by_graph": 0,
        "rust_buffer_shape_v1_clock_samples": 0,
        "rust_buffer_shape_v1_qualified": False,
        "actual_current_graph_predecessor_version": 48,
        "authenticated_evidence_owner_lower_bound": 172,
        "authenticated_history_reference_lower_bound": 177,
        "new_exact_source_feature_owner_count": 4,
    }


def validate_snapshot(
    previous: types.ModuleType, v47: types.ModuleType,
    v46: types.ModuleType, v45: types.ModuleType,
    v44: types.ModuleType, v43: types.ModuleType,
    v42: types.ModuleType, v41: types.ModuleType,
    v40: types.ModuleType, base: types.ModuleType, snapshot: object,
) -> None:
    base.need(type(snapshot) is dict, "reject missing current V49 evidence")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_buffer_shape_v1_source_freeze")
    validate_feature_proof(base, proof)
    assert isinstance(proof, dict)
    updates = feature_fields(proof)
    for key, value in updates.items():
        base.need(snapshot.get(key) == value,
                  "reject altered Rust source-only evidence: " + key)
    replaced = snapshot.get("preserved_v48_replaced_snapshot_fields")
    base.need(type(replaced) is dict, "preserve all genuine V48 snapshot values")
    assert isinstance(replaced, dict)
    historical = copy.deepcopy(snapshot)
    historical.pop("preserved_v48_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            historical[key] = copy.deepcopy(replaced[key])
        else:
            historical.pop(key, None)
    previous.validate_snapshot(v47, v46, v45, v44, v43, v42, v41, v40,
                               base, historical)
    base.need(
        set(replaced).issubset(updates)
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and snapshot.get("large_input_source_case_matrix_count") == 32
        and snapshot.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and snapshot.get("large_input_upstream_original_case_count") == 2
        and snapshot.get("large_input_upstream_original_subject_bytes") == 2147483648
        and snapshot.get("large_input_actual_candidate_search_status") == "NOT RUN"
        and snapshot.get("large_input_actual_candidate_subn_status") == "NOT RUN"
        and snapshot.get("actual_rust_v7_semantic_status") == "FAIL"
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get("actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and snapshot.get("actual_rust_v7_candidate_workers") == 13
        and snapshot.get("actual_rust_worker_process_ids") == WORKERS
        and snapshot.get("actual_rust_original_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 928
        and snapshot.get("actual_complete_rust_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 928
        and snapshot.get("current_complete_rust_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 928
        and snapshot.get("historical_rust_v3_original_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 1087
        and snapshot.get("historical_rust_v4_original_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 1036
        and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
        and snapshot.get("c_v4_original_campaign_semantic_mismatch_count") == 1230
        and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count") == 2172
        and snapshot.get("zig_v3_original_campaign_semantic_mismatch_count") == 1764
        and snapshot.get("actually_tested_corrected_candidate_families") == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count") == 1
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 172
        and snapshot.get("authenticated_history_reference_lower_bound") == 177
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("source_build_archive_gzip_inflation_count_by_graph") == 0
        and snapshot.get("actual_clock_samples_by_graph") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "preserve real failed matching, separate case counts and the unopened holdout",
    )


def comparison_rows() -> tuple[tuple[str, str, str, str, str], ...]:
    return (
        ("Python", "Verified baseline", "Two independent reference processes agree",
         "BASELINE", "green"),
        ("Rust", "928 compatibility differences",
         "Actually tested; the new source idea has not been built",
         "NOT MEASURED", "orange"),
        ("C", "Not retested", "Earlier attempts: 1,262 and 1,230 differences",
         "NOT MEASURED", "amber"),
        ("Zig", "Not retested", "Earlier attempts: 2,172 and 1,764 differences",
         "NOT MEASURED", "amber"),
        ("C++", "Not tested", "First-party design; no frozen runnable test runner",
         "NOT MEASURED", "slate"),
        ("Go", "Not tested", "First-party design; no frozen runnable test runner",
         "NOT MEASURED", "slate"),
        ("Fortran", "Not tested", "First-party design; no frozen runnable test runner",
         "NOT MEASURED", "slate"),
    )


def make_svg(
    previous: types.ModuleType, v47: types.ModuleType,
    v46: types.ModuleType, v45: types.ModuleType,
    v44: types.ModuleType, v43: types.ModuleType,
    v42: types.ModuleType, v41: types.ModuleType,
    v40: types.ModuleType, base: types.ModuleType,
    snapshot: dict, source_sha: str, inputs_sha: str,
) -> bytes:
    validate_snapshot(previous, v47, v46, v45, v44, v43, v42, v41, v40,
                      base, snapshot)
    source_sha = base.checked(source_sha, "actual current V49 graph renderer")
    inputs_sha = base.checked(inputs_sha, "actual current V49 graph inputs")
    proof = snapshot["rust_buffer_shape_v1_source_freeze"]
    owners = proof["owners"]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" '
        'height="2250" viewBox="0 0 1440 2250" role="img" '
        'aria-labelledby="v49-title v49-description">',
        '<title id="v49-title">Building a faster Python re: no compatible '
        'replacement yet; Rust differs on 928 checks and its new idea is '
        'untested</title>',
        '<desc id="v49-description">The pinned Python 3.14.6 baseline was '
        'independently verified. The latest actual Rust replacement completed '
        '13 workers, failed 928 compatibility checks and explicitly verified '
        '8,965 passing observations; it is not compatible. A new first-party '
        'buffer-handling idea belongs to the same Rust family and is source '
        'only: it has not been built or tested. There are six replacement '
        'families, one actually tested family and zero currently runnable or '
        'qualified replacements. Speed, memory and repair effectiveness are '
        'not measured. The 31,237 original checks, 50 signature checks, '
        '32 public observations and 32 large-input observations are separate. '
        'The 4,194,304-case final comparison has not been generated or opened. '
        'Historical Rust, C and Zig failures are preserved. Four and only four '
        'real new source owners raise authenticated lower bounds to 172 and '
        '177; the small Rust failure receipt proves no failure-category '
        'breakdown.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        '&quot;Segoe UI&quot;,sans-serif}.title{font-size:32px;font-weight:780;'
        'fill:#162b49}.lead{font-size:16px;fill:#445773}.heading{font-size:20px;'
        'font-weight:760;fill:#162b49}.label{font-size:13px;font-weight:720;'
        'fill:#53667d}.value{font-size:23px;font-weight:800;fill:#162b49}'
        '.body{font-size:15px;fill:#41536a}.small{font-size:12px;fill:#53667d}'
        '.name{font-size:16px;font-weight:750;fill:#162b49}.green{fill:#087443}'
        '.orange{fill:#a84725}.amber{fill:#875a08}.slate{fill:#53667d}'
        '.foot{font-size:10px;fill:#445773}.strong{font-weight:760}</style>',
        '<rect width="1440" height="2250" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="55" class="title">Building a faster Python re</text>',
        '<text x="46" y="86" class="lead">The goal: match Python exactly, '
        'then measure whether any from-scratch replacement is actually faster.</text>',
    ]
    cards = (
        (44, "Python", "VERIFIED", "green", "Pinned stable reference"),
        (317, "Rust", "928 DIFFERENCES", "orange", "Actually tested; failed"),
        (590, "Compatible replacements", "0", "orange", "None is ready to use"),
        (863, "Speed versus Python", "NOT MEASURED", "slate", "No valid benchmark yet"),
        (1136, "Final comparison", "4.2m UNOPENED", "slate", "4,194,304 hidden checks"),
    )
    for x, label, value, tone, detail in cards:
        lines.extend((
            f'<rect x="{x}" y="108" width="260" height="112" rx="14" '
            'fill="#fff" stroke="#d8e2ed"/>',
            f'<text x="{x + 16}" y="136" class="label">{label}</text>',
            f'<text x="{x + 16}" y="170" class="value {tone}">{value}</text>',
            f'<text x="{x + 16}" y="198" class="small">{detail}</text>',
        ))
    lines.extend((
        '<rect x="44" y="237" width="1352" height="113" rx="15" '
        'fill="#fff1ed" stroke="#e6b5a9"/>',
        '<text x="65" y="269" class="heading orange">Rust was tested and '
        'is not compatible</text>',
        '<text x="67" y="298" class="body">13 real workers completed '
        'the frozen original comparison. Rust produced 928 differences and '
        '8,965 explicitly verified passes.</text>',
        '<text x="67" y="326" class="body">A successful evidence receipt '
        'means the failure was saved; it does not mean the replacement passed.</text>',
        '<rect x="44" y="364" width="1352" height="108" rx="15" '
        'fill="#edf4ff" stroke="#bfd0ee"/>',
        '<text x="65" y="398" class="heading">New Rust idea: SOURCE ONLY '
        '— NOT BUILT OR TESTED</text>',
        '<text x="67" y="427" class="body">A complete first-party '
        'buffer-handling variant is frozen as source. It is the same Rust '
        'family, not a seventh replacement.</text>',
        '<text x="67" y="452" class="small">Repair effectiveness, '
        'compatibility, speed and memory: NOT MEASURED.</text>',
        '<rect x="44" y="488" width="1352" height="437" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="523" class="heading">Overall: how each '
        'replacement compares with Python</text>',
        '<text x="67" y="548" class="small">One row per existing family. '
        'A source idea, historical run or saved receipt is not a passing result.</text>',
        '<text x="70" y="576" class="label">FAMILY</text>',
        '<text x="218" y="576" class="label">CURRENT RESULT</text>',
        '<text x="525" y="576" class="label">WHAT WE ACTUALLY KNOW</text>',
        '<text x="1220" y="576" class="label">SPEED</text>',
        '<line x1="65" y1="588" x2="1374" y2="588" stroke="#dae4ee"/>',
    ))
    for index, (family, outcome, detail, speed, tone) in enumerate(comparison_rows()):
        y = 617 + index * 42
        if index % 2:
            lines.append(
                f'<rect x="58" y="{y - 22}" width="1318" height="37" '
                'rx="7" fill="#f7f9fc"/>'
            )
        lines.extend((
            f'<text x="70" y="{y}" class="name">{family}</text>',
            f'<text x="218" y="{y}" class="body {tone} strong">'
            f'{outcome}</text>',
            f'<text x="525" y="{y}" class="body">{detail}</text>',
            f'<text x="1220" y="{y}" class="small {tone}">{speed}</text>',
        ))
    lines.extend((
        '<text x="67" y="909" class="small">One Rust family has '
        'actually been tested. Currently active: 0. Compatible: 0. '
        'No replacement has a measured speed.</text>',
        '<rect x="44" y="942" width="1352" height="155" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="977" class="heading">Keep the different '
        'checks separate</text>',
        '<text x="67" y="1004" class="small">These are different '
        'denominators; none is quietly added to another.</text>',
    ))
    counters = (
        (66, "31,237", "Original compatibility checks"),
        (404, "50", "Additional signature checks"),
        (742, "32", "Public-interface observations"),
        (1080, "32", "Large-input observations"),
    )
    for x, value, label in counters:
        lines.extend((
            f'<text x="{x}" y="1043" class="value">{value}</text>',
            f'<text x="{x}" y="1070" class="small">{label}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1114" width="1352" height="222" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1148" class="heading">Additional checks '
        'at a glance</text>',
        '<text x="67" y="1174" class="small">Observed source and '
        'interface conditions only; these are not replacement test passes.</text>',
        '<text x="68" y="1203" class="name">Public interface: 32</text>',
    ))
    public_segments = (
        (17, "#178552"), (7, "#ba593c"), (6, "#8090a4"),
        (1, "#bd9137"), (1, "#7668a5"),
    )
    x = 306
    for amount, colour in public_segments:
        width = amount * 28
        lines.append(
            f'<rect x="{x}" y="1188" width="{width}" height="19" '
            f'fill="{colour}"/>'
        )
        x += width
    lines.append(
        '<text x="68" y="1230" class="small">17 pass · 7 fail · '
        '6 not measured · 1 not established · 1 not opened</text>'
    )
    lines.append('<text x="68" y="1264" class="name">Large inputs: 32</text>')
    large_segments = (
        (22, "#178552"), (1, "#ba593c"), (3, "#6987ad"),
        (2, "#bd9137"), (3, "#8090a4"), (1, "#7668a5"),
    )
    x = 306
    for amount, colour in large_segments:
        width = amount * 28
        lines.append(
            f'<rect x="{x}" y="1249" width="{width}" height="19" '
            f'fill="{colour}"/>'
        )
        x += width
    lines.extend((
        '<text x="68" y="1291" class="small">22 pass · 1 fail · '
        '3 not run · 2 not established · 3 not measured · 1 not opened</text>',
        '<text x="68" y="1316" class="small">The two genuine '
        '2,147,483,648-byte Python tests have not been run by any replacement.</text>',
        '<rect x="44" y="1352" width="1352" height="175" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1387" class="heading">Previous failures '
        'remain visible</text>',
        '<text x="67" y="1420" class="body"><tspan class="strong">'
        'Rust:</tspan> current 928; historical 1,036 and 1,087.</text>',
        '<text x="67" y="1450" class="body"><tspan class="strong">'
        'C:</tspan> historical 1,230 and 1,262.</text>',
        '<text x="67" y="1480" class="body"><tspan class="strong">'
        'Zig:</tspan> historical 1,764 and 2,172.</text>',
        '<text x="67" y="1507" class="small">No historical result '
        'claims that the new source-only Rust idea has been tested.</text>',
        '<rect x="44" y="1544" width="1352" height="163" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1578" class="heading">What is still unproven</text>',
        '<text x="67" y="1608" class="body">Runtime independence: '
        'NOT ESTABLISHED. Speed, memory and uncertainty: NOT MEASURED.</text>',
        '<text x="67" y="1637" class="body">Final comparison: all '
        '4,194,304 hidden checks remain NOT GENERATED and NOT OPENED.</text>',
        '<text x="67" y="1666" class="small">No candidate, compiler, '
        'native library, benchmark, clock or compressed evidence is run by '
        'this graph.</text>',
        '<rect x="44" y="1723" width="1352" height="118" rx="16" '
        'fill="#edf4ff" stroke="#bfd0ee"/>',
        '<text x="64" y="1756" class="heading">Four real new '
        'source files; no invented result</text>',
        '<text x="67" y="1787" class="body">Exactly four separately '
        'authenticated first-party source owners raise evidence lower bounds '
        'from 168 / 173 to 172 / 177.</text>',
        '<text x="67" y="1814" class="small">The existing failure '
        'receipt does not prove a breakdown of individual failure categories.</text>',
        '<rect x="44" y="1858" width="1352" height="361" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1890" class="heading">Exact reproducible '
        'evidence</text>',
        f'<text x="65" y="1921" class="foot">Graph inputs SHA-256: '
        f'{inputs_sha}</text>',
        f'<text x="65" y="1941" class="foot">Graph renderer SHA-256: '
        f'{source_sha}</text>',
        f'<text x="65" y="1964" class="foot">Historical V48 graph inputs '
        f'SHA-256: {V48["inputs"][1]}</text>',
        f'<text x="65" y="1984" class="foot">Historical V48 graph renderer '
        f'SHA-256: {V48["source"][1]}</text>',
        f'<text x="65" y="2004" class="foot">Historical V48 graph summary '
        f'SHA-256: {V48["summary"][1]}</text>',
        f'<text x="65" y="2024" class="foot">Historical V48 graph image '
        f'SHA-256: {V48["svg"][1]}</text>',
    ))
    for index, (role, owner) in enumerate(owners.items()):
        label = {
            "variant": "First-party unbuilt Rust variant",
            "verifier": "First-party source-freeze verifier",
            "protocol": "First-party source-only protocol",
            "contract": "First-party source-only contract",
        }[role]
        y = 2048 + index * 20
        lines.append(
            f'<text x="65" y="{y}" class="foot">{label} SHA-256: '
            f'{owner["sha256"]}</text>'
        )
    lines.extend((
        f'<text x="65" y="2148" class="foot">Actual failed Rust V7 '
        f'publication receipt SHA-256: {RECEIPT[1]}</text>',
        f'<text x="65" y="2168" class="foot">Failure archive SHA-256 '
        f'(receipt-attested; not opened): {previous.ARCHIVE[1]}</text>',
        '<text x="65" y="2191" class="small">A saved failure is not '
        'a successful candidate. All source changes remain unbuilt and '
        'untested.</text>',
        '<text x="65" y="2212" class="small">Stable baseline: '
        'CPython 3.14.6. V43 is a historical source anchor only. '
        'Winner: none.</text>',
        '<!-- The Rust buffer-shape variant is first-party source only; '
        'no candidate, compiler, archive, timing or holdout is run. -->',
        '</svg>',
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    current_input = ("Graph inputs SHA-256: " + inputs_sha).encode("ascii")
    current_source = ("Graph renderer SHA-256: " + source_sha).encode("ascii")
    old_input = (
        "Historical V48 graph inputs SHA-256: " + V48["inputs"][1]
    ).encode("ascii")
    old_source = (
        "Historical V48 graph renderer SHA-256: " + V48["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(current_input) == 1
        and raw.count(current_source) == 1
        and raw.count(old_input) == 1
        and raw.count(old_source) == 1
        and ("Graph inputs SHA-256: " + V48["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V48["source"][1]).encode("ascii")
        not in raw,
        "display current V49 footers and explicitly historical pushed V48",
    )
    lower = raw.lower()
    for phrase in (
        b"building a faster python re", b"verified", b"928 differences",
        b"compatible replacements", b"not measured", b"4.2m unopened",
        b"4,194,304", b"13 real workers", b"8,965 explicitly verified",
        b"source only", b"not built or tested", b"same rust family",
        b"not a seventh replacement", b"31,237", b"signature checks",
        b"public-interface observations", b"large-input observations",
        b"17 pass", b"7 fail", b"22 pass", b"3 not run",
        b"2,147,483,648", b"1,036", b"1,087", b"1,230", b"1,262",
        b"1,764", b"2,172", b"172 / 177", b"not generated",
        b"not opened", b"does not prove a breakdown", b"winner: none",
        b"failure archive sha-256 (receipt-attested; not opened)",
        b"v43 is a historical source anchor only",
    ):
        base.need(phrase in lower,
                  "keep the complete plain-language truthful overview: "
                  + repr(phrase))
    for falsehood in (
        b"rust candidate passed", b"rust replacement qualified",
        b"30,309 verified passes", b"30309 verified passes",
        b"variant tested", b"variant compiled", b"variant built",
        b"repair proven", b"896 repaired", b"672 repaired", b"224 repaired",
        b"32 repaired", b"seventh candidate family", b"winner selected",
        b"2-gigabyte candidate passes", b"holdout opened",
        b"archive inflated by graph", b"rust matching not run",
    ):
        base.need(falsehood not in lower,
                  "reject a fabricated source-only experiment: "
                  + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish the complete accessible V49 SVG with one linefeed")
    return raw


def build(
    previous: types.ModuleType, v47: types.ModuleType,
    v46: types.ModuleType, v45: types.ModuleType,
    v44: types.ModuleType, v43: types.ModuleType,
    v42: types.ModuleType, v41: types.ModuleType,
    v40: types.ModuleType, base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_sha = base.checked(options.source_sha256, "exact V49 source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "independently supply the exact frozen V49 renderer size")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                 private=True)
    old, old_inputs, _old_svg = authenticate_v48(
        previous, v47, v46, v45, v44, v43, v42, v41, v40, base,
        {
            "source": options.previous_source_sha256,
            "inputs": options.previous_inputs_sha256,
            "summary": options.previous_summary_sha256,
            "svg": options.previous_svg_sha256,
        },
    )
    proof = authenticate_feature(base, options)
    updates = feature_fields(proof)
    prior = old["snapshot"]
    snapshot = copy.deepcopy(prior)
    snapshot.update(updates)
    snapshot["preserved_v48_replaced_snapshot_fields"] = {
        key: copy.deepcopy(prior[key]) for key in updates if key in prior
    }
    validate_snapshot(previous, v47, v46, v45, v44, v43, v42, v41, v40,
                      base, snapshot)
    predecessors = {role: base.pin(*pin) for role, pin in V48.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 49,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(previous, v47, v46, v45, v44, v43, v42, v41, v40,
                   base, snapshot, source_sha, base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve the Python baseline and exactly six replacement families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 172,
            "authenticated_history_reference_lower_bound": 177,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "buffer_shape_v1_source_freeze": copy.deepcopy(proof),
                "buffer_shape_v1_feature_status": FEATURE_STATUS,
                "buffer_shape_v1_same_existing_rust_family": True,
                "buffer_shape_v1_build_status": "NOT BUILT",
                "buffer_shape_v1_matching_status": "NOT RUN",
                "buffer_shape_v1_repair_effectiveness": "NOT MEASURED",
                "buffer_shape_v1_verified_repaired_case_count": "NOT MEASURED",
                "buffer_shape_v1_failure_categories_proven_by_receipt": False,
                "buffer_shape_v1_candidate_workers_started": 0,
                "buffer_shape_v1_qualified": False,
                "current_original_campaign_semantic_mismatch_count": 928,
                "current_original_campaign_verified_passing_case_count": 8965,
                "current_original_campaign_candidate_worker_count": 13,
                "actual_candidate_workers": 13,
                "v13_candidate_worker_count": 13,
                "v13_matching_test_status": "FAIL: 928 SEMANTIC MISMATCHES",
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 49,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(input_raw),
                           len(input_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessors,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(
        max(len(input_raw), len(summary_raw), len(svg)) <= base.OWNER_LIMIT,
        "bound the three complete V49 evidence assets",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_feature(base: types.ModuleType) -> dict:
    owners: dict[str, dict] = {}
    for index, (role, path) in enumerate(FEATURE_PATHS.items()):
        digest = hashlib.sha256(("v49-synthetic-" + role).encode()).hexdigest()
        owners[role] = base.synthetic_owner((path, digest, 149 + index),
                                           949001 + index)
    contract = {
        "schema": FEATURE_SCHEMA,
        "version": 1,
        "phase": "CANDIDATES",
        "status": FEATURE_STATUS,
        "family": "rust",
        "source": {
            "path": owners["verifier"]["path"],
            "sha256": owners["verifier"]["sha256"],
        },
        "protocol": {
            "path": owners["protocol"]["path"],
            "sha256": owners["protocol"]["sha256"],
        },
        "candidate_variant": {
            **base.pin(owners["variant"]["path"],
                       owners["variant"]["sha256"],
                       owners["variant"]["bytes"]),
            "derived_from_actual_v13_sha256": V13_BRIDGE,
            "materialized": True,
            "built": False,
            "candidate_matching": "NOT RUN",
        },
        "preserved_public_adapter": {
            "actual_corrected_adapter_sha256": V13_ADAPTER,
            "actual_corrected_adapter_bytes": 31934,
            "canonical_adapter_modified": False,
            "runtime_adapter_activated": False,
        },
        "current_v48_overview": {
            "version": 48,
            "authenticated_evidence_owner_lower_bound": 168,
            "authenticated_history_reference_lower_bound": 173,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "qualified_candidate_count": 0,
        },
        "preserved_rust_owners": {
            "current_v48_renderer": base.pin(*V48["source"]),
            "current_v48_inputs": base.pin(*V48["inputs"]),
            "current_v48_summary": base.pin(*V48["summary"]),
            "current_v48_chart": base.pin(*V48["svg"]),
            "actual_v7_small_plaintext_receipt": base.pin(*RECEIPT),
        },
        "historically_reported_buffer_shape_diagnosis": {
            "repairs_verified": "NOT MEASURED",
            "mutable_live_log_read": False,
            "case_histogram_rederived_by_this_source_freeze": False,
            "repair_effect": "NOT MEASURED",
        },
        "phase_boundary": {
            "actual_archives_opened": 0,
            "actual_archives_decompressed": 0,
            "actual_candidate_workers_started": 0,
            "actual_native_libraries_loaded": 0,
            "actual_clock_samples": 0,
            "actual_hidden_cases_read": 0,
            "actual_holdout_cases_read": 0,
            "source_variant_materialized": True,
            "source_variant_built": False,
            "source_variant_candidate_matching": "NOT RUN",
            "source_variant_candidate_correctness": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "holdout_generated": False,
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }
    return make_feature_proof(base, owners, contract)


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_feature_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged V49 source-freeze evidence: "
                          + description)


def self_test(
    previous: types.ModuleType, v47: types.ModuleType,
    v46: types.ModuleType, v45: types.ModuleType,
    v44: types.ModuleType, v43: types.ModuleType,
    v42: types.ModuleType, v41: types.ModuleType,
    v40: types.ModuleType, base: types.ModuleType,
) -> dict:
    historical = previous.self_test(v47, v46, v45, v44, v43, v42, v41,
                                    v40, base)
    base.need(
        historical.get("status") == "PASS"
        and historical.get("rejected_hostile_control_count") == 2260
        and historical.get("actual_rust_v7_semantic_mismatch_count") == 928
        and historical.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and historical.get("actual_rust_v7_candidate_workers") == 13
        and historical.get("reference_archive_gzip_inflation_count") == 0
        and historical.get("matching_archive_gzip_inflation_count") == 0
        and historical.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and historical.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and historical.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "preserve all 2,260 actual V48 hostile controls and truthful failure",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = synthetic_feature(base)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, key)
        for role, owner in proof["owners"].items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = v43.forged_value(base, value)
                rejected += reject_control(base, hostile,
                                           "owner:" + role + ":" + key)
        for key, value in proof["complete_contract"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_contract"][key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "contract:" + key)
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v49")),
            ("filesystem", lambda: os.open("forbidden-v49", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v49")),
            ("write", lambda: os.mkdir("forbidden-v49")),
            ("process", lambda: subprocess.run(("forbidden-v49",))),
            ("process", lambda: subprocess.Popen(("forbidden-v49",))),
            ("process", lambda: os.execv("/forbidden-v49", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically block V49 source-only " + kind)
            else:
                raise base.GraphError("a V49 forbidden physical effect escaped")
        base.need(rejected >= 80,
                  "reject forged owners, outcomes, statuses and source contracts")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 49,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v48_hostile_controls": 2260,
            "new_v49_hostile_controls": rejected,
            "rejected_hostile_control_count": 2260 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_receipts_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_restored_original_files_read_by_self_test": 0,
            "actual_feature_source_files_read_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "supplementary_signature_check_count": 50,
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts": copy.deepcopy(PUBLIC_COUNTS),
            "large_input_source_case_matrix_count": 32,
            "large_input_source_case_status_counts": copy.deepcopy(LARGE_COUNTS),
            "large_input_upstream_original_case_count": 2,
            "large_input_upstream_original_subject_bytes": 2147483648,
            "actual_current_graph_predecessor_version": 48,
            "actual_rust_v7_publication_status": "PASS",
            "actual_rust_v7_publication_pass_means": "DURABLE PUBLICATION ONLY",
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v7_distinct_worker_process_id_count": 13,
            "actual_rust_v7_infrastructure_failure_count": 0,
            "actual_rust_v7_failure_archive_opened_by_graph": False,
            "actual_rust_v7_failure_archive_inflated_by_graph": False,
            "rust_buffer_shape_v1_feature_status": FEATURE_STATUS,
            "rust_buffer_shape_v1_new_candidate_family_count": 0,
            "rust_buffer_shape_v1_build_status": "NOT BUILT",
            "rust_buffer_shape_v1_matching_status": "NOT RUN",
            "rust_buffer_shape_v1_repair_effectiveness": "NOT MEASURED",
            "rust_buffer_shape_v1_failure_categories_proven_by_receipt": False,
            "authenticated_evidence_owner_lower_bound": 172,
            "authenticated_history_reference_lower_bound": 177,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
            "actually_tested_corrected_candidate_families": ["rust"],
            "actually_tested_corrected_candidate_family_count": 1,
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
              and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "write only the three specifically authorized new V49 graph assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete V49 source-feature graph bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        observed = os.fstat(handle)
        base.need(observed.st_uid == os.geteuid() and observed.st_nlink == 1
                  and observed.st_size == len(raw)
                  and stat.S_IMODE(observed.st_mode) == 0o600,
                  "publish complete privately owned V49 source-feature evidence")
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(confirmed == raw, "re-authenticate exact complete V49 graph output")


def result(base: types.ModuleType, snapshot: dict,
           outputs: dict[str, bytes], source_sha: str,
           *, written: bool, suffix: str) -> dict:
    keys = (
        "full_case_denominator", "suite_count", "private_waiver_count",
        "supplementary_signature_check_count",
        "public_entrypoint_case_matrix_count",
        "public_entrypoint_case_matrix_sha256",
        "public_entrypoint_case_status_counts", "public_entrypoint_status",
        "large_input_upstream_original_case_count",
        "large_input_upstream_original_subject_bytes",
        "large_input_source_case_matrix_count",
        "large_input_source_case_matrix_sha256",
        "large_input_source_case_status_counts",
        "large_input_actual_candidate_search_status",
        "large_input_actual_candidate_subn_status",
        "actual_rust_original_campaign", "actual_complete_rust_campaign",
        "current_complete_rust_campaign", "current_rust_original_campaign",
        "actual_complete_rust_v7_campaign", "actual_rust_campaign",
        "historical_rust_v3_original_campaign",
        "historical_rust_v4_original_campaign",
        "historical_complete_rust_v3_campaign",
        "historical_complete_rust_v4_campaign",
        "historical_rust_v3_original_campaign_semantic_mismatch_count",
        "historical_rust_v4_original_campaign_semantic_mismatch_count",
        "rust_original_campaign_status",
        "rust_original_campaign_semantic_mismatch_count",
        "rust_original_campaign_verified_passing_case_count",
        "rust_original_campaign_candidate_worker_count",
        "rust_original_campaign_receipt_sha256",
        "rust_original_campaign_recovery_journal_sha256",
        "rust_recovery_journal_sha256", "actual_rust_recovery_journal_sha256",
        "actual_rust_publication_receipt_sha256",
        "actual_rust_attempted_suite_count", "actual_rust_started_suite_count",
        "actual_rust_completed_suite_count", "actual_rust_candidate_workers",
        "actual_rust_worker_process_ids", "actual_rust_infrastructure_failure_count",
        "actual_rust_semantic_mismatch_count",
        "actual_rust_verified_passing_case_count", "actual_rust_candidate_qualified",
        "actually_tested_corrected_candidate_families",
        "actually_tested_corrected_candidate_family_count",
        "currently_activated_candidate_families",
        "currently_activated_candidate_family_count",
        "actual_rust_v7_failure_receipt_sha256",
        "actual_rust_v7_failure_receipt_bytes",
        "actual_rust_v7_failure_receipt_inode",
        "actual_rust_v7_failure_archive_sha256_attested_by_receipt",
        "actual_rust_v7_failure_archive_bytes",
        "actual_rust_v7_failure_archive_inode",
        "actual_rust_v7_failure_archive_opened_by_graph",
        "actual_rust_v7_failure_archive_inflated_by_graph",
        "actual_rust_v7_failure_archive_sha256_recomputed_by_graph",
        "actual_rust_v7_recovery_journal_sha256_attested_by_receipt",
        "actual_rust_v7_recovery_journal_opened_by_graph",
        "actual_rust_v7_historical_source_freeze_anchor_version",
        "actual_rust_v7_historical_source_freeze_anchor_sha256",
        "actual_current_graph_predecessor_version",
        "actual_rust_v7_publication_status", "actual_rust_v7_publication_pass_means",
        "actual_rust_v7_semantic_status", "actual_rust_v7_candidate_qualified",
        "actual_rust_v7_case_execution_denominator", "actual_rust_v7_suite_count",
        "actual_rust_v7_attempted_suite_count", "actual_rust_v7_started_suite_count",
        "actual_rust_v7_completed_suite_count", "actual_rust_v7_candidate_workers",
        "actual_rust_v7_worker_process_ids",
        "actual_rust_v7_distinct_worker_process_id_count",
        "actual_rust_v7_infrastructure_failure_count",
        "actual_rust_v7_semantic_mismatch_count",
        "actual_rust_v7_explicitly_verified_passing_case_count",
        "actual_rust_v7_passing_cases_derived_by_subtraction",
        "actual_rust_v7_all_four_original_targets_restored",
        "actual_rust_v7_original_target_content_read_by_graph",
        "actual_rust_v7_source_build_archive_reads_by_graph",
        "rust_buffer_shape_v1_source_freeze",
        "rust_buffer_shape_v1_feature_status", "rust_buffer_shape_v1_family",
        "rust_buffer_shape_v1_same_existing_rust_family",
        "rust_buffer_shape_v1_new_candidate_family_count",
        "rust_buffer_shape_v1_source_frozen",
        "rust_buffer_shape_v1_variant_source",
        "rust_buffer_shape_v1_verifier_source",
        "rust_buffer_shape_v1_protocol", "rust_buffer_shape_v1_contract",
        "rust_buffer_shape_v1_exact_feature_owner_count",
        "rust_buffer_shape_v1_build_status", "rust_buffer_shape_v1_matching_status",
        "rust_buffer_shape_v1_semantic_mismatch_count",
        "rust_buffer_shape_v1_verified_passing_case_count",
        "rust_buffer_shape_v1_repair_effectiveness",
        "rust_buffer_shape_v1_verified_repaired_case_count",
        "rust_buffer_shape_v1_failure_categories_proven_by_receipt",
        "rust_buffer_shape_v1_candidate_workers_started",
        "rust_buffer_shape_v1_compiler_processes_started",
        "rust_buffer_shape_v1_native_libraries_loaded",
        "rust_buffer_shape_v1_archive_reads_by_graph",
        "rust_buffer_shape_v1_clock_samples", "rust_buffer_shape_v1_qualified",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
        "new_exact_source_feature_owner_count",
        "first_party_source_inventory_family_count",
        "frozen_corrected_runner_source_family_count",
        "frozen_corrected_runner_source_families",
        "actually_runnable_candidate_family_count",
        "actually_runnable_candidate_families", "qualified_candidate_count",
        "actual_candidate_imports_by_graph",
        "actual_candidate_workers_started_by_graph",
        "actual_reference_workers_started_by_graph",
        "actual_compiler_processes_started_by_graph",
        "actual_native_libraries_loaded_by_graph",
        "actual_large_subject_allocations_by_graph",
        "reference_archive_gzip_inflation_count",
        "matching_archive_gzip_inflation_count",
        "source_build_archive_gzip_inflation_count_by_graph",
        "actual_clock_samples_by_graph", "clock_samples",
        "hidden_cases_read", "timing_trials_run", "runtime_no_delegation",
        "performance", "memory", "confidence_intervals", "undefined_behavior",
        "final_comparison_planned_case_count", "final_comparison_cases_generated",
        "final_holdout_opened", "winner_selected",
    )
    return {
        "schema": SCHEMA + suffix,
        "version": 49,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 48,
        **{
            "previous_overview_" + role + "_sha256": item[1]
            for role, item in V48.items()
        },
        "outputs_written": written,
        **{key: copy.deepcopy(snapshot[key]) for key in keys},
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in ("source", "inputs", "summary", "svg"):
        parser.add_argument("--previous-" + role + "-sha256")
    for flag in FEATURE_FLAGS.values():
        parser.add_argument("--" + flag.replace("_", "-") + "-sha256")
        parser.add_argument("--" + flag.replace("_", "-") + "-bytes", type=int)
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v47, v46, v45, v44, v43, v42, v41, v40, base = load_v48()
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256"
                             for role in ("source", "inputs", "summary", "svg"))
            for flag in FEATURE_FLAGS.values():
                forbidden.extend((flag + "_sha256", flag + "_bytes"))
            forbidden.extend(("inputs_sha256", "summary_sha256", "svg_sha256"))
            base.need(all(getattr(options, name) is None for name in forbidden),
                      "synthetic-only V49 self-test cannot accept real owner pins")
            sys.stdout.buffer.write(base.canonical(self_test(
                previous, v47, v46, v45, v44, v43, v42, v41, v40, base,
            )))
            return 0
        snapshot, pairs = build(previous, v47, v46, v45, v44, v43, v42,
                                v41, v40, base, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256, "exact V49 source")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "publish only the three authorized fresh V49 graph assets")
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact frozen V49 graph inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact frozen V49 graph summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact frozen accessible V49 graph",
            ),
        }
        for path, fingerprint in expected.items():
            raw, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                     private=True)
            base.need(raw == outputs[path],
                      "reproduce every current V49 source-feature graph byte")
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source_sha,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V49 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V49 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
