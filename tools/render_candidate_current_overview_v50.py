#!/usr/bin/env python3
"""Show the unchanged Rust result and two unbuilt, first-party source ideas."""

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
SELF = "tools/render_candidate_current_overview_v50.py"
OUTPUT = "docs/evidence/candidate-current-overview-v50"
SCHEMA = "rebar-candidate-current-overview-v50"
FEATURE_SCHEMA = "rebar-phase2-owned-rust-match-pickle-source-repair-v1-source-freeze"
FEATURE_STATUS = (
    "SOURCE FROZEN; FIRST-PARTY RUST BUFFER-SHAPE-AND-MATCH-PICKLE "
    "VARIANT NOT BUILT OR RUN"
)
V49 = {
    "source": (
        "tools/render_candidate_current_overview_v49.py",
        "03ae29acb80817de9cfbd512e919702cea1a761f2bfa69c638b4644f179304b0",
        74565,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v49.inputs.json",
        "0d78d45480bfd701024b733d33c43651a6ae29c760ac8f88c9404ee061d5bc76",
        540049,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v49.json",
        "1b5dad9574883e45b6bad5b2c9ec69f59a77e2ab079d7ed23a226280a4a4f4a4",
        1475826,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v49.svg",
        "761d1303e617827b79f0dd3ee24ab062d1282ea5cf568c4ca89c65a8ae19b75c",
        13490,
    ),
}
BUFFER = {
    "variant": (
        "candidates/rust/variants/buffer_shape_v1/py_bridge.c",
        "29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3",
        180436,
    ),
    "verifier": (
        "tools/apply_owned_rust_buffer_shape_source_repair_v1.py",
        "9c2a3642f2cda9fc85fd391baf4e0d57b25117f444d3a831592e8b62de3a627b",
        64345,
    ),
    "protocol": (
        "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-REPAIR-V1.md",
        "67ba62acc8e51a6868404ea3faeb1aaaacb1d053cc1c915bef0c397edf5ac408",
        5033,
    ),
    "contract": (
        "oracle/phase2/rust-buffer-shape-source-repair-v1.json",
        "ffa76d1724396fae5816cf96e0ae2104bcce8fc5eb246b8306d4441db0fe4a1b",
        11454,
    ),
}
FEATURE_PATHS = {
    "variant": "candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c",
    "verifier": "tools/apply_owned_rust_match_pickle_source_repair_v1.py",
    "protocol": "oracle/phase2/RUST-MATCH-PICKLE-SOURCE-REPAIR-V1.md",
    "contract": "oracle/phase2/rust-match-pickle-source-repair-v1.json",
}
FEATURE_FLAGS = {
    "variant": "variant_source",
    "verifier": "feature_verifier",
    "protocol": "feature_protocol",
    "contract": "feature_contract",
}
RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-"
    "phase2-v13-rust-pattern-repr-original-p0-"
    "failures-publication-receipt.json",
    "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943",
    8450,
)
V13_BRIDGE = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]
PUBLIC_COUNTS = {
    "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1, "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22, "FAIL": 1, "NOT RUN": 3,
    "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1,
}


def load_v49() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType,
]:
    path, expected, size = V49["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(handle)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject a nonprivate pushed V49 graph renderer")
        parts: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(handle, min(262144, remaining))
            if not piece:
                raise ValueError("reject truncated pushed V49 source bytes")
            parts.append(piece)
            remaining -= len(piece)
        if os.read(handle, 1):
            raise ValueError("reject appended pushed V49 source bytes")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject V49 graph replacement during authentication")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_pushed_compact_rust_buffer_graph_v49")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    v48, v47, v46, v45, v44, v43, v42, v41, v40, base = previous.load_v48()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v49"
        and previous.SELF == path
        and previous.RECEIPT == RECEIPT
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS,
        "load only actually pushed V49 and its unchanged six-family history",
    )
    return previous, v48, v47, v46, v45, v44, v43, v42, v41, v40, base


def walk(value: object):
    if type(value) is dict:
        yield value
        for child in value.values():
            yield from walk(child)
    elif type(value) is list:
        for child in value:
            yield from walk(child)


def contains_pin(value: object, pin: dict) -> bool:
    return any(
        record.get("path") == pin["path"]
        and record.get("sha256") == pin["sha256"]
        and record.get("bytes") == pin["bytes"]
        for record in walk(value)
    )


def validate_contract(base: types.ModuleType, contract: object,
                      owners: dict[str, dict]) -> None:
    base.need(type(contract) is dict, "reject missing Rust pickle source freeze")
    assert isinstance(contract, dict)
    base.need(
        contract.get("schema") == FEATURE_SCHEMA
        and contract.get("version") == 1
        and contract.get("phase") == "CANDIDATES"
        and contract.get("status") == FEATURE_STATUS
        and contract.get("family") == "rust",
        "reject an invented candidate family, executed variant or stale source",
    )
    for role, key in (("verifier", "source"), ("protocol", "protocol")):
        base.need(
            contract.get(key) == {
                "path": owners[role]["path"],
                "sha256": owners[role]["sha256"],
            },
            "bind the exact independent Rust serialization " + role,
        )
    variant = contract.get("candidate_variant")
    base.need(type(variant) is dict,
              "reject an omitted complete combined first-party Rust variant")
    assert isinstance(variant, dict)
    expected_variant = base.pin(
        owners["variant"]["path"], owners["variant"]["sha256"],
        owners["variant"]["bytes"],
    )
    base.need(
        all(variant.get(key) == value for key, value in expected_variant.items())
        and variant.get("buffer_shape_origin_sha256") == BUFFER["variant"][1]
        and variant.get("actual_corrected_bridge_sha256") == V13_BRIDGE
        and variant.get("materialized") is True
        and variant.get("built") is False
        and variant.get("candidate_matching") == "NOT RUN"
        and variant.get("same_existing_rust_family") is True
        and variant.get("adds_candidate_family") is False
        and variant.get("correctness") == "NOT MEASURED",
        "require combined buffer and pickle source without claiming any run",
    )
    overview = contract.get("current_v49_overview")
    base.need(
        type(overview) is dict
        and overview.get("version") == 49
        and overview.get("authenticated_evidence_owner_lower_bound") == 172
        and overview.get("authenticated_history_reference_lower_bound") == 177
        and overview.get("first_party_source_inventory_family_count") == 6
        and overview.get("frozen_corrected_runner_source_family_count") == 3
        and overview.get("qualified_candidate_count") == 0,
        "anchor the real pushed V49 and preserve all original six families",
    )
    preserved = contract.get("preserved_rust_owners")
    base.need(type(preserved) is dict,
              "preserve immutable V49, real failure and first buffer owners")
    assert isinstance(preserved, dict)
    for role, pin in V49.items():
        base.need(
            contains_pin(preserved, base.pin(*pin)),
            "preserve exact actual pushed V49 " + role,
        )
    for role, pin in BUFFER.items():
        base.need(
            contains_pin(preserved, base.pin(*pin)),
            "preserve the unchanged committed first Rust buffer " + role,
        )
    base.need(contains_pin(preserved, base.pin(*RECEIPT)),
              "retain the one actual V7 small durable failure receipt")
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
        "reject compilation, matching, native execution, archive or holdout work",
    )


def make_feature_proof(base: types.ModuleType, owners: dict[str, dict],
                       contract: dict) -> dict:
    base.need(
        set(owners) == set(FEATURE_PATHS)
        and len({item.get("path") for item in owners.values()}) == 4
        and len({item.get("inode") for item in owners.values()}) == 4,
        "count exactly four truly separate new Rust serialization owners",
    )
    for role, path in FEATURE_PATHS.items():
        owner = owners[role]
        base.need(
            type(owner) is dict
            and owner.get("path") == path
            and base.checked(owner.get("sha256"), "source-only pickle " + role)
            == owner.get("sha256")
            and type(owner.get("bytes")) is int
            and 0 < owner["bytes"] <= base.OWNER_LIMIT
            and owner.get("device") == 2064
            and type(owner.get("inode")) is int and owner["inode"] > 0
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and owner.get("uid") == os.geteuid(),
            "reject a substituted or nonprivate source-only owner: " + role,
        )
    validate_contract(base, contract, owners)
    proof = {
        "schema": SCHEMA + "-authenticated-rust-match-pickle-source-freeze",
        "version": 1,
        "status": FEATURE_STATUS,
        "family": "rust",
        "same_existing_rust_family": True,
        "new_candidate_family_count": 0,
        "source_frozen": True,
        "source_owner_count": 4,
        "owners": copy.deepcopy(owners),
        "complete_contract": copy.deepcopy(contract),
        "buffer_shape_origin_sha256": BUFFER["variant"][1],
        "preserved_buffer_variant_bytes": BUFFER["variant"][2],
        "actual_graph_predecessor_version": 49,
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
        "authenticated_evidence_owner_lower_bound_before_freeze": 172,
        "authenticated_history_reference_lower_bound_before_freeze": 177,
        "new_exact_feature_owner_count": 4,
        "authenticated_evidence_owner_lower_bound_after_freeze": 176,
        "authenticated_history_reference_lower_bound_after_freeze": 181,
    }
    proof["complete_source_feature_binding_sha256"] = base.digest(
        base.canonical(proof),
    )
    validate_feature_proof(base, proof)
    return proof


def validate_feature_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject missing source-only pickle evidence")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-rust-match-pickle-source-freeze",
        "version": 1,
        "status": FEATURE_STATUS,
        "family": "rust",
        "same_existing_rust_family": True,
        "new_candidate_family_count": 0,
        "source_frozen": True,
        "source_owner_count": 4,
        "buffer_shape_origin_sha256": BUFFER["variant"][1],
        "preserved_buffer_variant_bytes": BUFFER["variant"][2],
        "actual_graph_predecessor_version": 49,
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
        "authenticated_evidence_owner_lower_bound_before_freeze": 172,
        "authenticated_history_reference_lower_bound_before_freeze": 177,
        "new_exact_feature_owner_count": 4,
        "authenticated_evidence_owner_lower_bound_after_freeze": 176,
        "authenticated_history_reference_lower_bound_after_freeze": 181,
    }
    for key, value in expected.items():
        base.need(proof.get(key) == value,
                  "reject invented serialization results or source effects: " + key)
    owners = proof.get("owners")
    base.need(type(owners) is dict and set(owners) == set(FEATURE_PATHS),
              "retain exactly four independent serialization source owners")
    assert isinstance(owners, dict)
    validate_contract(base, proof.get("complete_contract"), owners)
    body = {key: value for key, value in proof.items()
            if key != "complete_source_feature_binding_sha256"}
    base.need(proof.get("complete_source_feature_binding_sha256")
              == base.digest(base.canonical(body)),
              "bind every exact source owner without inventing a matching run")


def authenticate_feature(base: types.ModuleType,
                         options: argparse.Namespace) -> dict:
    owners: dict[str, dict] = {}
    raw: dict[str, bytes] = {}
    for role, path in FEATURE_PATHS.items():
        flag = FEATURE_FLAGS[role]
        fingerprint = base.checked(getattr(options, flag + "_sha256"),
                                   "actual source-only pickle " + role)
        size = getattr(options, flag + "_bytes")
        base.need(type(size) is int and 0 < size <= base.OWNER_LIMIT,
                  "require complete independently pinned source " + role)
        raw[role], owners[role] = base.read_owner(path, fingerprint, size,
                                                  private=True)
    contract = base.document(raw["contract"],
                             "canonical complete match-pickle source freeze")
    protocol = raw["protocol"].decode("utf-8").upper()
    base.need("RUST" in protocol and "NOT BUILT" in protocol
              and "NOT MEASURED" in protocol,
              "require a first-party explicitly unbuilt serialization protocol")
    return make_feature_proof(base, owners, contract)


def buffer_options() -> argparse.Namespace:
    return argparse.Namespace(
        variant_source_sha256=BUFFER["variant"][1],
        variant_source_bytes=BUFFER["variant"][2],
        feature_verifier_sha256=BUFFER["verifier"][1],
        feature_verifier_bytes=BUFFER["verifier"][2],
        feature_protocol_sha256=BUFFER["protocol"][1],
        feature_protocol_bytes=BUFFER["protocol"][2],
        feature_contract_sha256=BUFFER["contract"][1],
        feature_contract_bytes=BUFFER["contract"][2],
    )


def v49_reproduction_options(previous: types.ModuleType) -> argparse.Namespace:
    values = vars(buffer_options())
    values.update({
        "source_sha256": V49["source"][1],
        "source_bytes": V49["source"][2],
        "previous_source_sha256": previous.V48["source"][1],
        "previous_inputs_sha256": previous.V48["inputs"][1],
        "previous_summary_sha256": previous.V48["summary"][1],
        "previous_svg_sha256": previous.V48["svg"][1],
    })
    return argparse.Namespace(**values)


def authenticate_v49(previous: types.ModuleType,
                     v48: types.ModuleType, v47: types.ModuleType,
                     v46: types.ModuleType, v45: types.ModuleType,
                     v44: types.ModuleType, v43: types.ModuleType,
                     v42: types.ModuleType, v41: types.ModuleType,
                     v40: types.ModuleType, base: types.ModuleType,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    raw: dict[str, bytes] = {}
    for role, item in V49.items():
        base.need(base.checked(supplied.get(role), "pushed V49 " + role)
                  == item[1],
                  "require the actual immutable current pushed V49 " + role)
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete immutable V49 summary")
    inputs = base.document(raw["inputs"], "complete immutable V49 inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(v48, v47, v46, v45, v44, v43, v42, v41,
                               v40, base, snapshot)
    reproduced_snapshot, reproduced_pairs = previous.build(
        v48, v47, v46, v45, v44, v43, v42, v41, v40, base,
        v49_reproduction_options(previous),
    )
    reproduced = dict(reproduced_pairs)
    buffer = reproduced_snapshot["rust_buffer_shape_v1_source_freeze"]
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v49-summary"
        and old.get("version") == 49
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V49["source"])
        and old.get("inputs") == base.pin(*V49["inputs"])
        and old.get("svg") == base.pin(*V49["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v49-inputs"
        and inputs.get("version") == 49
        and inputs.get("renderer") == base.pin(*V49["source"])
        and snapshot == reproduced_snapshot
        and snapshot.get("rust_buffer_shape_v1_source_freeze") == buffer
        and raw["inputs"] == reproduced[V49["inputs"][0]]
        and raw["summary"] == reproduced[V49["summary"][0]]
        and raw["svg"] == reproduced[V49["svg"][0]]
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("actually_tested_corrected_candidate_families") == ["rust"]
        and old.get("actually_tested_corrected_candidate_family_count") == 1
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("actually_runnable_candidate_family_count") == 0
        and old.get("qualified_candidate_count") == 0
        and old.get("authenticated_evidence_owner_lower_bound") == 172
        and old.get("authenticated_history_reference_lower_bound") == 177
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "regenerate complete actual V49, real buffer proof and original Rust failure",
    )
    return old, inputs, raw["svg"]


def feature_fields(proof: dict) -> dict:
    owners = proof["owners"]
    return {
        "rust_match_pickle_v1_source_freeze": copy.deepcopy(proof),
        "rust_match_pickle_v1_feature_status": FEATURE_STATUS,
        "rust_match_pickle_v1_family": "rust",
        "rust_match_pickle_v1_same_existing_rust_family": True,
        "rust_match_pickle_v1_new_candidate_family_count": 0,
        "rust_match_pickle_v1_source_frozen": True,
        "rust_match_pickle_v1_buffer_shape_origin_sha256": BUFFER["variant"][1],
        "rust_match_pickle_v1_preserved_buffer_variant_bytes": BUFFER["variant"][2],
        "rust_match_pickle_v1_variant_source": copy.deepcopy(owners["variant"]),
        "rust_match_pickle_v1_verifier_source": copy.deepcopy(owners["verifier"]),
        "rust_match_pickle_v1_protocol": copy.deepcopy(owners["protocol"]),
        "rust_match_pickle_v1_contract": copy.deepcopy(owners["contract"]),
        "rust_match_pickle_v1_exact_feature_owner_count": 4,
        "rust_match_pickle_v1_build_status": "NOT BUILT",
        "rust_match_pickle_v1_matching_status": "NOT RUN",
        "rust_match_pickle_v1_semantic_mismatch_count": "NOT MEASURED",
        "rust_match_pickle_v1_verified_passing_case_count": "NOT MEASURED",
        "rust_match_pickle_v1_repair_effectiveness": "NOT MEASURED",
        "rust_match_pickle_v1_verified_repaired_case_count": "NOT MEASURED",
        "rust_match_pickle_v1_failure_categories_proven_by_receipt": False,
        "rust_match_pickle_v1_candidate_workers_started": 0,
        "rust_match_pickle_v1_compiler_processes_started": 0,
        "rust_match_pickle_v1_native_libraries_loaded": 0,
        "rust_match_pickle_v1_archive_reads_by_graph": 0,
        "rust_match_pickle_v1_clock_samples": 0,
        "rust_match_pickle_v1_qualified": False,
        "actual_current_graph_predecessor_version": 49,
        "authenticated_evidence_owner_lower_bound": 176,
        "authenticated_history_reference_lower_bound": 181,
        "new_exact_source_feature_owner_count": 4,
    }


def validate_snapshot(previous: types.ModuleType,
                      v48: types.ModuleType, v47: types.ModuleType,
                      v46: types.ModuleType, v45: types.ModuleType,
                      v44: types.ModuleType, v43: types.ModuleType,
                      v42: types.ModuleType, v41: types.ModuleType,
                      v40: types.ModuleType, base: types.ModuleType,
                      snapshot: object) -> None:
    base.need(type(snapshot) is dict, "reject missing combined Rust evidence")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_match_pickle_v1_source_freeze")
    validate_feature_proof(base, proof)
    assert isinstance(proof, dict)
    updates = feature_fields(proof)
    for key, value in updates.items():
        base.need(snapshot.get(key) == value,
                  "reject invented serialization source matching: " + key)
    replaced = snapshot.get("preserved_v49_replaced_snapshot_fields")
    base.need(type(replaced) is dict, "preserve all complete V49 source evidence")
    assert isinstance(replaced, dict)
    old = copy.deepcopy(snapshot)
    old.pop("preserved_v49_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            old[key] = copy.deepcopy(replaced[key])
        else:
            old.pop(key, None)
    previous.validate_snapshot(v48, v47, v46, v45, v44, v43, v42, v41,
                               v40, base, old)
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
        and snapshot.get("rust_buffer_shape_v1_variant_source", {}).get("sha256")
        == BUFFER["variant"][1]
        and snapshot.get("rust_buffer_shape_v1_build_status") == "NOT BUILT"
        and snapshot.get("rust_buffer_shape_v1_matching_status") == "NOT RUN"
        and snapshot.get("rust_buffer_shape_v1_repair_effectiveness")
        == "NOT MEASURED"
        and snapshot.get("actually_tested_corrected_candidate_families") == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count") == 1
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 176
        and snapshot.get("authenticated_history_reference_lower_bound") == 181
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
        "preserve both source variants, failed matching and all separate matrices",
    )


def make_svg(previous: types.ModuleType,
             v48: types.ModuleType, v47: types.ModuleType,
             v46: types.ModuleType, v45: types.ModuleType,
             v44: types.ModuleType, v43: types.ModuleType,
             v42: types.ModuleType, v41: types.ModuleType,
             v40: types.ModuleType, base: types.ModuleType,
             snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(previous, v48, v47, v46, v45, v44, v43, v42, v41,
                      v40, base, snapshot)
    source_sha = base.checked(source_sha, "actual V50 graph renderer")
    inputs_sha = base.checked(inputs_sha, "actual V50 graph inputs")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v49-title", "v50-title")
    visible = visible.replace("v49-description", "v50-description")
    changes = (
        (
            "Rust differs on 928 checks and its new idea is untested</title>",
            "Rust differs on 928 checks and its two new ideas are untested</title>",
            "keep the actual Rust failure while displaying both source-only ideas",
        ),
        (
            "A new first-party buffer-handling idea belongs to the same Rust "
            "family and is source only: it has not been built or tested.",
            "Two combined first-party buffer-handling and match-serialization "
            "ideas belong to the same Rust family. Both are source only: "
            "neither has been built or tested.",
            "honestly describe both first-party unbuilt Rust source variants",
        ),
        (
            "Four and only four real new source owners raise authenticated "
            "lower bounds to 172 and 177;",
            "Four and only four new serialization source owners raise "
            "authenticated lower bounds from 172 and 177 to 176 and 181;",
            "increase owner lower bounds only for four genuine new owners",
        ),
        (
            "New Rust idea: SOURCE ONLY — NOT BUILT OR TESTED",
            "Two Rust ideas: SOURCE ONLY — NEITHER BUILT OR TESTED",
            "show both unbuilt source ideas in one existing Rust family",
        ),
        (
            "A complete first-party buffer-handling variant is frozen as "
            "source. It is the same Rust family, not a seventh replacement.",
            "The new match-serialization variant extends the existing "
            "buffer variant. Both are the same Rust family, not a "
            "seventh replacement.",
            "show that serialization composes on the preserved buffer source",
        ),
        (
            "Actually tested; the new source idea has not been built",
            "Actually tested; both new source ideas remain unbuilt",
            "preserve a clear one-row-per-family current comparison",
        ),
        (
            "Four real new source files; no invented result",
            "Four more source files; no invented result",
            "distinguish the new serialization owners from the prior buffer",
        ),
        (
            "Exactly four separately authenticated first-party source "
            "owners raise evidence lower bounds from 168 / 173 to 172 / 177.",
            "Exactly four more authenticated first-party source owners "
            "raise evidence lower bounds from 172 / 177 to 176 / 181.",
            "account only for the four actual new serialization source owners",
        ),
    )
    for before, after, label in changes:
        visible = v43.replace_once(base, visible, before, after, label)
    lines = visible.splitlines()
    start = next(
        index for index, line in enumerate(lines)
        if line.startswith('<rect x="44" y="1858" width="1352"')
    )
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="361" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact reproducible '
        'evidence</text>',
    ))
    proof = snapshot["rust_match_pickle_v1_source_freeze"]
    owners = proof["owners"]
    entries = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V49 graph inputs SHA-256", V49["inputs"][1]),
        ("Historical V49 graph renderer SHA-256", V49["source"][1]),
        ("Historical V49 graph summary SHA-256", V49["summary"][1]),
        ("Historical V49 graph image SHA-256", V49["svg"][1]),
        ("Preserved first-party buffer variant SHA-256", BUFFER["variant"][1]),
        ("Preserved first-party buffer verifier SHA-256", BUFFER["verifier"][1]),
        ("Preserved first-party buffer protocol SHA-256", BUFFER["protocol"][1]),
        ("Preserved first-party buffer contract SHA-256", BUFFER["contract"][1]),
        ("First-party unbuilt buffer-and-pickle variant SHA-256",
         owners["variant"]["sha256"]),
        ("First-party serialization source verifier SHA-256",
         owners["verifier"]["sha256"]),
        ("First-party serialization source protocol SHA-256",
         owners["protocol"]["sha256"]),
        ("First-party serialization source contract SHA-256",
         owners["contract"]["sha256"]),
        ("Actual failed Rust V7 publication receipt SHA-256", RECEIPT[1]),
        ("Failure archive SHA-256 (receipt-attested; not opened)",
         v48.ARCHIVE[1]),
    )
    for index, (label, fingerprint) in enumerate(entries):
        y = 1914 + index * 16
        lines.append(
            f'<text x="65" y="{y}" class="foot">{label}: '
            f'{fingerprint}</text>'
        )
    lines.extend((
        '<text x="65" y="2180" class="small">Both Rust variants are '
        'first-party source only. Neither has been built, run or '
        'qualified.</text>',
        '<text x="65" y="2204" class="small">Stable baseline: '
        'CPython 3.14.6. Hidden final comparison: unopened. Winner: none.</text>',
        '<!-- Both combined Rust source variants remain unbuilt and untested; '
        'no archive, compiler, timing, native code or holdout is run. -->',
        '</svg>',
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    current_inputs = ("Graph inputs SHA-256: " + inputs_sha).encode("ascii")
    current_source = ("Graph renderer SHA-256: " + source_sha).encode("ascii")
    old_inputs = (
        "Historical V49 graph inputs SHA-256: " + V49["inputs"][1]
    ).encode("ascii")
    old_source = (
        "Historical V49 graph renderer SHA-256: " + V49["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(current_inputs) == 1 and raw.count(current_source) == 1
        and raw.count(old_inputs) == 1 and raw.count(old_source) == 1
        and ("Graph inputs SHA-256: " + V49["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V49["source"][1]).encode("ascii")
        not in raw,
        "show exact current V50 footers and explicitly historical pushed V49",
    )
    lower = raw.lower()
    for phrase in (
        b'height="2250"', b"building a faster python re", b"928 differences",
        b"compatible replacements", b"not measured", b"4.2m unopened",
        b"13 real workers", b"8,965 explicitly verified", b"two rust ideas",
        b"source only", b"neither built or tested", b"same rust family",
        b"not a seventh replacement", b"match-serialization",
        b"31,237", b"signature checks", b"public-interface observations",
        b"large-input observations", b"17 pass", b"7 fail", b"22 pass",
        b"3 not run", b"2,147,483,648", b"1,036", b"1,087",
        b"1,230", b"1,262", b"1,764", b"2,172", b"176 / 181",
        b"not generated", b"not opened", b"does not prove a breakdown",
        b"winner: none", b"failure archive sha-256 (receipt-attested; not opened)",
    ):
        base.need(phrase in lower,
                  "retain the complete accessible measured V50 headline: "
                  + repr(phrase))
    for falsehood in (
        b"rust candidate passed", b"rust replacement qualified",
        b"30,309 verified passes", b"30309 verified passes",
        b"variant tested", b"variant built", b"repair proven",
        b"896 repaired", b"672 repaired", b"224 repaired", b"32 repaired",
        b"seventh candidate family", b"winner selected", b"holdout opened",
        b"rust matching not run", b"faster than python",
    ):
        base.need(falsehood not in lower,
                  "reject fabricated Rust match-serialization claims: "
                  + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "render one exact final V50 SVG linefeed")
    return raw


def build(previous: types.ModuleType,
          v48: types.ModuleType, v47: types.ModuleType,
          v46: types.ModuleType, v45: types.ModuleType,
          v44: types.ModuleType, v43: types.ModuleType,
          v42: types.ModuleType, v41: types.ModuleType,
          v40: types.ModuleType, base: types.ModuleType,
          options: argparse.Namespace) -> tuple[
              dict, tuple[tuple[str, bytes], ...],
          ]:
    source_sha = base.checked(options.source_sha256, "exact frozen V50 source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "require the externally supplied exact V50 source size")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                 private=True)
    old, old_inputs, old_svg = authenticate_v49(
        previous, v48, v47, v46, v45, v44, v43, v42, v41, v40, base,
        {
            "source": options.previous_source_sha256,
            "inputs": options.previous_inputs_sha256,
            "summary": options.previous_summary_sha256,
            "svg": options.previous_svg_sha256,
        },
    )
    proof = authenticate_feature(base, options)
    updates = feature_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v49_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key]) for key in updates if key in original
    }
    validate_snapshot(previous, v48, v47, v46, v45, v44, v43, v42, v41,
                      v40, base, snapshot)
    predecessors = {role: base.pin(*pin) for role, pin in V49.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 50,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(previous, v48, v47, v46, v45, v44, v43, v42,
                   v41, v40, base, snapshot, old_svg,
                   source_sha, base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "preserve the baseline plus exactly six replacement families")
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 176,
            "authenticated_history_reference_lower_bound": 181,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "match_pickle_v1_source_freeze": copy.deepcopy(proof),
                "match_pickle_v1_feature_status": FEATURE_STATUS,
                "match_pickle_v1_same_existing_rust_family": True,
                "match_pickle_v1_buffer_shape_origin_sha256":
                    BUFFER["variant"][1],
                "match_pickle_v1_build_status": "NOT BUILT",
                "match_pickle_v1_matching_status": "NOT RUN",
                "match_pickle_v1_repair_effectiveness": "NOT MEASURED",
                "match_pickle_v1_verified_repaired_case_count": "NOT MEASURED",
                "match_pickle_v1_failure_categories_proven_by_receipt": False,
                "match_pickle_v1_candidate_workers_started": 0,
                "match_pickle_v1_qualified": False,
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
        "version": 50,
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
    base.need(max(len(input_raw), len(summary_raw), len(svg)) <= base.OWNER_LIMIT,
              "bound each complete source-only V50 graph evidence owner")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_feature(base: types.ModuleType) -> dict:
    owners: dict[str, dict] = {}
    for index, (role, path) in enumerate(FEATURE_PATHS.items()):
        fingerprint = hashlib.sha256(
            ("v50-match-pickle-synthetic-" + role).encode("ascii")
        ).hexdigest()
        owners[role] = base.synthetic_owner((path, fingerprint, 250 + index),
                                           950001 + index)
    preserved = {
        "current_v49_" + role: base.pin(*pin)
        for role, pin in V49.items()
    }
    preserved.update({
        "preserved_buffer_" + role: base.pin(*pin)
        for role, pin in BUFFER.items()
    })
    preserved["actual_v7_small_plaintext_receipt"] = base.pin(*RECEIPT)
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
            "buffer_shape_origin_sha256": BUFFER["variant"][1],
            "actual_corrected_bridge_sha256": V13_BRIDGE,
            "materialized": True,
            "built": False,
            "candidate_matching": "NOT RUN",
            "same_existing_rust_family": True,
            "adds_candidate_family": False,
            "correctness": "NOT MEASURED",
        },
        "preserved_rust_owners": preserved,
        "current_v49_overview": {
            "version": 49,
            "authenticated_evidence_owner_lower_bound": 172,
            "authenticated_history_reference_lower_bound": 177,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "qualified_candidate_count": 0,
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
    raise base.GraphError("accepted forged serialization evidence: " + description)


def self_test(previous: types.ModuleType,
              v48: types.ModuleType, v47: types.ModuleType,
              v46: types.ModuleType, v45: types.ModuleType,
              v44: types.ModuleType, v43: types.ModuleType,
              v42: types.ModuleType, v41: types.ModuleType,
              v40: types.ModuleType, base: types.ModuleType) -> dict:
    history = previous.self_test(v48, v47, v46, v45, v44, v43,
                                 v42, v41, v40, base)
    base.need(
        history.get("status") == "PASS"
        and history.get("rejected_hostile_control_count") == 2347
        and history.get("actual_rust_v7_semantic_mismatch_count") == 928
        and history.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and history.get("actual_rust_v7_candidate_workers") == 13
        and history.get("reference_archive_gzip_inflation_count") == 0
        and history.get("matching_archive_gzip_inflation_count") == 0
        and history.get("source_build_archive_gzip_inflation_count_by_graph") == 0
        and history.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and history.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "retain all 2,347 actual source-only V49 hostility controls",
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
            ("filesystem", lambda: builtins.open("forbidden-v50")),
            ("filesystem", lambda: os.open("forbidden-v50", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v50")),
            ("write", lambda: os.mkdir("forbidden-v50")),
            ("process", lambda: subprocess.run(("forbidden-v50",))),
            ("process", lambda: subprocess.Popen(("forbidden-v50",))),
            ("process", lambda: os.execv("/forbidden-v50", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically block V50 source-only " + kind)
            else:
                raise base.GraphError("a V50 forbidden external effect escaped")
        base.need(rejected >= 80,
                  "reject all forged combined source ownership and execution claims")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 50,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v49_hostile_controls": 2347,
            "new_v50_hostile_controls": rejected,
            "rejected_hostile_control_count": 2347 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_receipts_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_feature_source_files_read_by_self_test": 0,
            "actual_restored_original_files_read_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_current_graph_predecessor_version": 49,
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v7_distinct_worker_process_id_count": 13,
            "actual_rust_v7_infrastructure_failure_count": 0,
            "actual_rust_v7_publication_status": "PASS",
            "actual_rust_v7_publication_pass_means": "DURABLE PUBLICATION ONLY",
            "actual_rust_v7_failure_archive_opened_by_graph": False,
            "actual_rust_v7_failure_archive_inflated_by_graph": False,
            "rust_match_pickle_v1_feature_status": FEATURE_STATUS,
            "rust_match_pickle_v1_build_status": "NOT BUILT",
            "rust_match_pickle_v1_matching_status": "NOT RUN",
            "rust_match_pickle_v1_repair_effectiveness": "NOT MEASURED",
            "rust_match_pickle_v1_new_candidate_family_count": 0,
            "rust_match_pickle_v1_buffer_shape_origin_sha256":
                BUFFER["variant"][1],
            "rust_match_pickle_v1_failure_categories_proven_by_receipt": False,
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
            "authenticated_evidence_owner_lower_bound": 176,
            "authenticated_history_reference_lower_bound": 181,
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
              "publish only three newly authorized V50 source-feature graph assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete independently owned V50 graph bytes")
            remaining = remaining[count:]
        os.fsync(descriptor)
        observed = os.fstat(descriptor)
        base.need(observed.st_uid == os.geteuid()
                  and observed.st_nlink == 1
                  and observed.st_size == len(raw)
                  and stat.S_IMODE(observed.st_mode) == 0o600,
                  "publish a complete private exact V50 graph owner")
    finally:
        os.close(descriptor)
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
    base.need(confirmed == raw, "re-authenticate every exact V50 graph byte")


def result(base: types.ModuleType, snapshot: dict, outputs: dict[str, bytes],
           source_sha: str, *, written: bool, suffix: str) -> dict:
    return {
        **copy.deepcopy(snapshot),
        "schema": SCHEMA + suffix,
        "version": 50,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 49,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V49.items()},
        "outputs_written": written,
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
        previous, v48, v47, v46, v45, v44, v43, v42, v41, v40, base = load_v49()
        if options.self_test:
            names = ["source_sha256", "source_bytes"]
            names.extend("previous_" + role + "_sha256"
                         for role in ("source", "inputs", "summary", "svg"))
            for flag in FEATURE_FLAGS.values():
                names.extend((flag + "_sha256", flag + "_bytes"))
            names.extend(("inputs_sha256", "summary_sha256", "svg_sha256"))
            base.need(all(getattr(options, name) is None for name in names),
                      "synthetic-only V50 self-test cannot accept real owner pins")
            sys.stdout.buffer.write(base.canonical(self_test(
                previous, v48, v47, v46, v45, v44, v43, v42, v41, v40, base,
            )))
            return 0
        snapshot, pairs = build(previous, v48, v47, v46, v45, v44,
                                v43, v42, v41, v40, base, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256, "exact V50 renderer")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "publish only the three newly authorized V50 graph outputs")
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )))
            return 0
        pins = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact V50 graph inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact V50 graph summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact V50 accessible graph image",
            ),
        }
        for path, fingerprint in pins.items():
            raw, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                     private=True)
            base.need(raw == outputs[path],
                      "reproduce every frozen V50 source-only graph byte")
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source_sha,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V50 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V50 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
