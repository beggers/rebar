#!/usr/bin/env python3
"""Show a frozen future Rust build recipe without claiming a native build."""

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
SELF = "tools/render_candidate_current_overview_v51.py"
OUTPUT = "docs/evidence/candidate-current-overview-v51"
SCHEMA = "rebar-candidate-current-overview-v51"
FEATURE_SCHEMA = "rebar-phase2-owned-rust-buffer-shape-source-build-v16-source-freeze"
FEATURE_STATUS = (
    "SOURCE FROZEN; COMBINED FIRST-PARTY RUST BRIDGE "
    "NOT BUILT OR MATCHING-TESTED"
)
V50 = {
    "source": (
        "tools/render_candidate_current_overview_v50.py",
        "4077fbf6703e98325c4b4eacea95d27608a3bb21a93143024094154385787f45",
        60235,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v50.inputs.json",
        "8506587243c98fa75a14dfc74cfc918772a74eadebc3f2728772d1d0d94bd726",
        560297,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v50.json",
        "60f0648be19016e5d8ebfa01f93c2c50c32aa4fb981fc0d518902b8b9985005e",
        1535160,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v50.svg",
        "a114a7b813c4c1fc470950639adc50ffb7118dd91a31d9f63dee6ba46e04f8b9",
        14209,
    ),
}
BUFFER = (
    "candidates/rust/variants/buffer_shape_v1/py_bridge.c",
    "29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3",
    180436,
)
PICKLE = {
    "variant": (
        "candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c",
        "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335",
        181004,
    ),
    "verifier": (
        "tools/apply_owned_rust_match_pickle_source_repair_v1.py",
        "85383f4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517",
        81784,
    ),
    "protocol": (
        "oracle/phase2/RUST-MATCH-PICKLE-SOURCE-REPAIR-V1.md",
        "fad29fdcd3956ae99f9db40afae33b51eb99fb743baf89540a4ee7aafb7ac1af",
        5105,
    ),
    "contract": (
        "oracle/phase2/rust-match-pickle-source-repair-v1.json",
        "5456535223cb029d41e8739696bde30b2b7127995fd0ef30286ff0488b1ed133",
        15276,
    ),
}
FEATURE_PATHS = {
    "source": "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py",
    "protocol": "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md",
    "contract": "oracle/phase2/rust-buffer-shape-source-build-v16.json",
}
FEATURE_FLAGS = {
    "source": "build_source",
    "protocol": "build_protocol",
    "contract": "build_contract",
}
RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-"
    "phase2-v13-rust-pattern-repr-original-p0-"
    "failures-publication-receipt.json",
    "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943",
    8450,
)
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]
PUBLIC_COUNTS = {
    "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1, "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22, "FAIL": 1, "NOT RUN": 3,
    "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1,
}


def load_v50() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
]:
    path, expected, size = V50["source"]
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
            raise ValueError("reject the wrong pushed V50 renderer owner")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(handle, min(262144, remaining))
            if not piece:
                raise ValueError("reject incomplete pushed V50 source bytes")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(handle, 1):
            raise ValueError("reject appended pushed V50 source bytes")
        raw = b"".join(pieces)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject pushed V50 graph replacement")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_pushed_combined_rust_source_graph_v50")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    v49, v48, v47, v46, v45, v44, v43, v42, v41, v40, base = (
        previous.load_v49()
    )
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v50"
        and previous.SELF == path
        and previous.RECEIPT == RECEIPT
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS,
        "load only the actually pushed V50 combined first-party Rust graph",
    )
    return previous, v49, v48, v47, v46, v45, v44, v43, v42, v41, v40, base


def walk(value: object):
    if type(value) is dict:
        yield value
        for child in value.values():
            yield from walk(child)
    elif type(value) is list:
        for child in value:
            yield from walk(child)


def contains_pin(value: object, owner: dict) -> bool:
    return any(
        item.get("path") == owner["path"]
        and item.get("sha256") == owner["sha256"]
        and item.get("bytes") == owner["bytes"]
        for item in walk(value)
    )


def validate_contract(base: types.ModuleType, contract: object,
                      owners: dict[str, dict]) -> None:
    base.need(type(contract) is dict,
              "reject the missing complete first-party future build recipe")
    assert isinstance(contract, dict)
    base.need(
        contract.get("schema") == FEATURE_SCHEMA
        and contract.get("version") == 16
        and contract.get("phase") == "CANDIDATES"
        and contract.get("status") == FEATURE_STATUS
        and contract.get("family") == "rust",
        "reject a stale, executed or non-Rust future native build recipe",
    )
    for role, name in (("source", "source"), ("protocol", "protocol")):
        base.need(
            contract.get(name) == {
                "path": owners[role]["path"],
                "sha256": owners[role]["sha256"],
            },
            "bind the exact independent future Rust build " + role,
        )
    current = contract.get("current_pushed_graph")
    base.need(
        type(current) is dict
        and current.get("version") == 50
        and current.get("authenticated_evidence_owner_lower_bound") == 176
        and current.get("authenticated_history_reference_lower_bound") == 181,
        "bind only the actual pushed V50 and its unchanged evidence counts",
    )
    assert isinstance(current, dict)
    for role, item in V50.items():
        base.need(contains_pin(current, base.pin(*item)),
                  "retain the complete immutable V50 graph " + role)
    for item in (BUFFER, PICKLE["variant"], RECEIPT):
        base.need(contains_pin(contract, base.pin(*item)),
                  "retain original buffer, combined bridge and real failure")
    future = contract.get("future_offline_native_build")
    base.need(type(future) is dict and future.get("build_status") == "NOT RUN",
              "never claim a recipe has actually built a native candidate")
    boundary = contract.get("phase_boundary")
    base.need(type(boundary) is dict,
              "require zero actual native-build and matching effects")
    assert isinstance(boundary, dict)
    for key in (
        "actual_archives_opened", "actual_archives_decompressed",
        "actual_benchmark_files_read", "actual_candidate_imports",
        "actual_candidate_workers_started", "actual_clock_samples",
        "actual_compiler_processes_started", "actual_hidden_cases_read",
        "actual_holdout_cases_read", "actual_native_activations",
        "actual_native_libraries_loaded", "actual_network_requests",
        "actual_reference_workers_started", "actual_source_builds_started",
        "actual_workspace_mutations", "timing_trials_run",
    ):
        base.need(boundary.get(key) == 0,
                  "reject an actually executed source-freeze action: " + key)
    base.need(
        boundary.get("candidate_correctness") == "NOT MEASURED"
        and boundary.get("candidate_matching") == "NOT RUN"
        and boundary.get("candidate_qualified") is False
        and boundary.get("holdout") == "NOT OPENED",
        "preserve unrun matching, unopened holdout and zero qualification",
    )


def make_feature_proof(base: types.ModuleType, owners: dict[str, dict],
                       contract: dict) -> dict:
    base.need(set(owners) == set(FEATURE_PATHS)
              and len({item.get("path") for item in owners.values()}) == 3
              and len({item.get("inode") for item in owners.values()}) == 3,
              "count exactly three distinct new Rust build-recipe owners")
    for role, path in FEATURE_PATHS.items():
        item = owners[role]
        base.need(
            type(item) is dict and item.get("path") == path
            and base.checked(item.get("sha256"), "future build " + role)
            == item.get("sha256")
            and type(item.get("bytes")) is int
            and 0 < item["bytes"] <= base.OWNER_LIMIT
            and item.get("device") == 2064
            and type(item.get("inode")) is int and item["inode"] > 0
            and item.get("mode") == "0600"
            and item.get("nlink") == 1
            and item.get("uid") == os.geteuid(),
            "reject substituted, incomplete or linked build " + role,
        )
    validate_contract(base, contract, owners)
    proof = {
        "schema": SCHEMA + "-authenticated-future-rust-build-source-freeze",
        "version": 16,
        "status": FEATURE_STATUS,
        "family": "rust",
        "same_existing_rust_family": True,
        "new_candidate_family_count": 0,
        "source_frozen": True,
        "source_owner_count": 3,
        "owners": copy.deepcopy(owners),
        "complete_contract": copy.deepcopy(contract),
        "actual_graph_predecessor_version": 50,
        "preserved_buffer_variant_sha256": BUFFER[1],
        "preserved_buffer_variant_bytes": BUFFER[2],
        "preserved_combined_variant_sha256": PICKLE["variant"][1],
        "preserved_combined_variant_bytes": PICKLE["variant"][2],
        "actual_v7_semantic_mismatch_count": 928,
        "actual_v7_explicitly_verified_passing_case_count": 8965,
        "actual_v7_candidate_workers": 13,
        "build_status": "NOT RUN",
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
        "authenticated_evidence_owner_lower_bound_before_freeze": 176,
        "authenticated_history_reference_lower_bound_before_freeze": 181,
        "new_exact_feature_owner_count": 3,
        "authenticated_evidence_owner_lower_bound_after_freeze": 179,
        "authenticated_history_reference_lower_bound_after_freeze": 184,
    }
    proof["complete_source_feature_binding_sha256"] = base.digest(
        base.canonical(proof),
    )
    validate_feature_proof(base, proof)
    return proof


def validate_feature_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject omitted V16 frozen build proof")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-future-rust-build-source-freeze",
        "version": 16,
        "status": FEATURE_STATUS,
        "family": "rust",
        "same_existing_rust_family": True,
        "new_candidate_family_count": 0,
        "source_frozen": True,
        "source_owner_count": 3,
        "actual_graph_predecessor_version": 50,
        "preserved_buffer_variant_sha256": BUFFER[1],
        "preserved_buffer_variant_bytes": BUFFER[2],
        "preserved_combined_variant_sha256": PICKLE["variant"][1],
        "preserved_combined_variant_bytes": PICKLE["variant"][2],
        "actual_v7_semantic_mismatch_count": 928,
        "actual_v7_explicitly_verified_passing_case_count": 8965,
        "actual_v7_candidate_workers": 13,
        "build_status": "NOT RUN",
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
        "authenticated_evidence_owner_lower_bound_before_freeze": 176,
        "authenticated_history_reference_lower_bound_before_freeze": 181,
        "new_exact_feature_owner_count": 3,
        "authenticated_evidence_owner_lower_bound_after_freeze": 179,
        "authenticated_history_reference_lower_bound_after_freeze": 184,
    }
    for key, value in expected.items():
        base.need(proof.get(key) == value,
                  "reject invented actual native-build action: " + key)
    owners = proof.get("owners")
    base.need(type(owners) is dict and set(owners) == set(FEATURE_PATHS),
              "retain exactly three separately authenticated recipe owners")
    assert isinstance(owners, dict)
    validate_contract(base, proof.get("complete_contract"), owners)
    body = {key: value for key, value in proof.items()
            if key != "complete_source_feature_binding_sha256"}
    base.need(proof.get("complete_source_feature_binding_sha256")
              == base.digest(base.canonical(body)),
              "bind all three complete source owners without running a build")


def authenticate_feature(base: types.ModuleType,
                         options: argparse.Namespace) -> dict:
    owners: dict[str, dict] = {}
    raw: dict[str, bytes] = {}
    for role, path in FEATURE_PATHS.items():
        flag = FEATURE_FLAGS[role]
        fingerprint = base.checked(getattr(options, flag + "_sha256"),
                                   "actual frozen build " + role)
        size = getattr(options, flag + "_bytes")
        base.need(type(size) is int and 0 < size <= base.OWNER_LIMIT,
                  "pin one exact future build source owner: " + role)
        raw[role], owners[role] = base.read_owner(path, fingerprint, size,
                                                  private=True)
    contract = base.document(raw["contract"],
                             "canonical complete future V16 build freeze")
    protocol = raw["protocol"].decode("utf-8").upper()
    base.need("RUST" in protocol and "NOT RUN" in protocol
              and "NOT MEASURED" in protocol,
              "describe the future offline build as not run or benchmarked")
    return make_feature_proof(base, owners, contract)


def v50_reproduction_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V50["source"][1],
        source_bytes=V50["source"][2],
        previous_source_sha256=previous.V49["source"][1],
        previous_inputs_sha256=previous.V49["inputs"][1],
        previous_summary_sha256=previous.V49["summary"][1],
        previous_svg_sha256=previous.V49["svg"][1],
        variant_source_sha256=PICKLE["variant"][1],
        variant_source_bytes=PICKLE["variant"][2],
        feature_verifier_sha256=PICKLE["verifier"][1],
        feature_verifier_bytes=PICKLE["verifier"][2],
        feature_protocol_sha256=PICKLE["protocol"][1],
        feature_protocol_bytes=PICKLE["protocol"][2],
        feature_contract_sha256=PICKLE["contract"][1],
        feature_contract_bytes=PICKLE["contract"][2],
    )


def authenticate_v50(previous: types.ModuleType,
                     v49: types.ModuleType, v48: types.ModuleType,
                     v47: types.ModuleType, v46: types.ModuleType,
                     v45: types.ModuleType, v44: types.ModuleType,
                     v43: types.ModuleType, v42: types.ModuleType,
                     v41: types.ModuleType, v40: types.ModuleType,
                     base: types.ModuleType,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    raw: dict[str, bytes] = {}
    for role, item in V50.items():
        base.need(base.checked(supplied.get(role), "actual V50 " + role)
                  == item[1],
                  "bind actual immediate pushed V50 history: " + role)
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete immutable V50 summary")
    inputs = base.document(raw["inputs"], "complete immutable V50 inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(v49, v48, v47, v46, v45, v44, v43, v42,
                               v41, v40, base, snapshot)
    reproduced_snapshot, pairs = previous.build(
        v49, v48, v47, v46, v45, v44, v43, v42, v41, v40, base,
        v50_reproduction_options(previous),
    )
    reproduced = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v50-summary"
        and old.get("version") == 50
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V50["source"])
        and old.get("inputs") == base.pin(*V50["inputs"])
        and old.get("svg") == base.pin(*V50["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v50-inputs"
        and inputs.get("version") == 50
        and inputs.get("renderer") == base.pin(*V50["source"])
        and snapshot == reproduced_snapshot
        and raw["inputs"] == reproduced[V50["inputs"][0]]
        and raw["summary"] == reproduced[V50["summary"][0]]
        and raw["svg"] == reproduced[V50["svg"][0]]
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("actually_tested_corrected_candidate_families") == ["rust"]
        and old.get("actually_tested_corrected_candidate_family_count") == 1
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("actually_runnable_candidate_family_count") == 0
        and old.get("qualified_candidate_count") == 0
        and old.get("authenticated_evidence_owner_lower_bound") == 176
        and old.get("authenticated_history_reference_lower_bound") == 181
        and old.get("rust_buffer_shape_v1_variant_source", {}).get("sha256")
        == BUFFER[1]
        and old.get("rust_match_pickle_v1_variant_source", {}).get("sha256")
        == PICKLE["variant"][1]
        and old.get("rust_match_pickle_v1_build_status") == "NOT BUILT"
        and old.get("rust_match_pickle_v1_matching_status") == "NOT RUN"
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "reproduce entire pushed V50 byte-for-byte and preserve unbuilt Rust",
    )
    return old, inputs, raw["svg"]


def feature_fields(proof: dict) -> dict:
    owners = proof["owners"]
    return {
        "rust_native_build_v16_source_freeze": copy.deepcopy(proof),
        "rust_native_build_v16_feature_status": FEATURE_STATUS,
        "rust_native_build_v16_family": "rust",
        "rust_native_build_v16_same_existing_rust_family": True,
        "rust_native_build_v16_new_candidate_family_count": 0,
        "rust_native_build_v16_source_frozen": True,
        "rust_native_build_v16_source": copy.deepcopy(owners["source"]),
        "rust_native_build_v16_protocol": copy.deepcopy(owners["protocol"]),
        "rust_native_build_v16_contract": copy.deepcopy(owners["contract"]),
        "rust_native_build_v16_exact_feature_owner_count": 3,
        "rust_native_build_v16_preserved_buffer_sha256": BUFFER[1],
        "rust_native_build_v16_preserved_combined_sha256": PICKLE["variant"][1],
        "rust_native_build_v16_build_status": "NOT RUN",
        "rust_native_build_v16_matching_status": "NOT RUN",
        "rust_native_build_v16_semantic_mismatch_count": "NOT MEASURED",
        "rust_native_build_v16_verified_passing_case_count": "NOT MEASURED",
        "rust_native_build_v16_repair_effectiveness": "NOT MEASURED",
        "rust_native_build_v16_verified_repaired_case_count": "NOT MEASURED",
        "rust_native_build_v16_failure_categories_proven_by_receipt": False,
        "rust_native_build_v16_candidate_workers_started": 0,
        "rust_native_build_v16_compiler_processes_started": 0,
        "rust_native_build_v16_native_libraries_loaded": 0,
        "rust_native_build_v16_archive_reads_by_graph": 0,
        "rust_native_build_v16_clock_samples": 0,
        "rust_native_build_v16_qualified": False,
        "actual_current_graph_predecessor_version": 50,
        "authenticated_evidence_owner_lower_bound": 179,
        "authenticated_history_reference_lower_bound": 184,
        "new_exact_source_feature_owner_count": 3,
    }


def validate_snapshot(previous: types.ModuleType,
                      v49: types.ModuleType, v48: types.ModuleType,
                      v47: types.ModuleType, v46: types.ModuleType,
                      v45: types.ModuleType, v44: types.ModuleType,
                      v43: types.ModuleType, v42: types.ModuleType,
                      v41: types.ModuleType, v40: types.ModuleType,
                      base: types.ModuleType, snapshot: object) -> None:
    base.need(type(snapshot) is dict, "reject missing frozen build graph")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_native_build_v16_source_freeze")
    validate_feature_proof(base, proof)
    assert isinstance(proof, dict)
    updates = feature_fields(proof)
    for key, value in updates.items():
        base.need(snapshot.get(key) == value,
                  "reject an invented offline Rust build action: " + key)
    replaced = snapshot.get("preserved_v50_replaced_snapshot_fields")
    base.need(type(replaced) is dict, "retain complete unchanged V50 evidence")
    assert isinstance(replaced, dict)
    old = copy.deepcopy(snapshot)
    old.pop("preserved_v50_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            old[key] = copy.deepcopy(replaced[key])
        else:
            old.pop(key, None)
    previous.validate_snapshot(v49, v48, v47, v46, v45, v44, v43,
                               v42, v41, v40, base, old)
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
        == BUFFER[1]
        and snapshot.get("rust_buffer_shape_v1_build_status") == "NOT BUILT"
        and snapshot.get("rust_match_pickle_v1_variant_source", {}).get("sha256")
        == PICKLE["variant"][1]
        and snapshot.get("rust_match_pickle_v1_build_status") == "NOT BUILT"
        and snapshot.get("rust_match_pickle_v1_matching_status") == "NOT RUN"
        and snapshot.get("actually_tested_corrected_candidate_families") == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count") == 1
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 179
        and snapshot.get("authenticated_history_reference_lower_bound") == 184
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
        "preserve failed Rust, three exact future owners, zero actual build",
    )


def make_svg(previous: types.ModuleType,
             v49: types.ModuleType, v48: types.ModuleType,
             v47: types.ModuleType, v46: types.ModuleType,
             v45: types.ModuleType, v44: types.ModuleType,
             v43: types.ModuleType, v42: types.ModuleType,
             v41: types.ModuleType, v40: types.ModuleType,
             base: types.ModuleType, snapshot: dict,
             old_svg: bytes, source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(previous, v49, v48, v47, v46, v45, v44, v43,
                      v42, v41, v40, base, snapshot)
    source_sha = base.checked(source_sha, "actual current V51 graph source")
    inputs_sha = base.checked(inputs_sha, "actual current V51 graph inputs")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v50-title", "v51-title")
    visible = visible.replace("v50-description", "v51-description")
    changes = (
        (
            "Rust differs on 928 checks and its two new ideas are untested</title>",
            "Rust differs on 928 checks; its future native build is not run</title>",
            "plain-language current Rust failure and genuinely future build",
        ),
        (
            "Two combined first-party buffer-handling and match-serialization "
            "ideas belong to the same Rust family. Both are source only: "
            "neither has been built or tested.",
            "The combined first-party buffer and match-serialization source "
            "belongs to the same Rust family. Its reproducible native-build "
            "recipe is frozen; the native build has not run.",
            "show the future recipe without inventing compiled native code",
        ),
        (
            "Four and only four new serialization source owners raise "
            "authenticated lower bounds from 172 and 177 to 176 and 181;",
            "Three and only three genuinely frozen native-build recipe owners "
            "raise authenticated lower bounds from 176 and 181 to 179 and 184;",
            "add exactly three real future build source owners",
        ),
        (
            "Two Rust ideas: SOURCE ONLY — NEITHER BUILT OR TESTED",
            "Rust build recipe frozen — NATIVE BUILD NOT YET RUN",
            "show the complete next step as a future native build",
        ),
        (
            "The new match-serialization variant extends the existing "
            "buffer variant. Both are the same Rust family, not a "
            "seventh replacement.",
            "The combined buffer-and-serialization source remains unbuilt. "
            "Its frozen recipe is the same Rust family, not a seventh "
            "replacement.",
            "preserve both source variants and never claim a native build",
        ),
        (
            "Four more source files; no invented result",
            "Three build-recipe files; no native build yet",
            "display the three-owner future recipe accurately",
        ),
        (
            "Exactly four more authenticated first-party source owners "
            "raise evidence lower bounds from 172 / 177 to 176 / 181.",
            "Exactly three authenticated future build-recipe owners "
            "raise evidence lower bounds from 176 / 181 to 179 / 184.",
            "increase lower bounds only for three real V16 source owners",
        ),
    )
    for before, after, label in changes:
        visible = v43.replace_once(base, visible, before, after, label)
    lines = visible.splitlines()
    marker = next(
        index for index, line in enumerate(lines)
        if line.startswith('<rect x="44" y="1858" width="1352"')
    )
    lines = lines[:marker]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="361" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact reproducible '
        'evidence</text>',
    ))
    owners = snapshot["rust_native_build_v16_source_freeze"]["owners"]
    rows = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V50 graph inputs SHA-256", V50["inputs"][1]),
        ("Historical V50 graph renderer SHA-256", V50["source"][1]),
        ("Historical V50 graph summary SHA-256", V50["summary"][1]),
        ("Historical V50 graph image SHA-256", V50["svg"][1]),
        ("Preserved first-party buffer variant SHA-256", BUFFER[1]),
        ("Preserved first-party unbuilt combined bridge SHA-256",
         PICKLE["variant"][1]),
        ("Preserved first-party match-serialization verifier SHA-256",
         PICKLE["verifier"][1]),
        ("Preserved first-party match-serialization protocol SHA-256",
         PICKLE["protocol"][1]),
        ("Preserved first-party match-serialization contract SHA-256",
         PICKLE["contract"][1]),
        ("First-party future native-build recipe source SHA-256",
         owners["source"]["sha256"]),
        ("First-party future native-build protocol SHA-256",
         owners["protocol"]["sha256"]),
        ("First-party future native-build contract SHA-256",
         owners["contract"]["sha256"]),
        ("Actual failed Rust V7 publication receipt SHA-256", RECEIPT[1]),
        ("Failure archive SHA-256 (receipt-attested; not opened)",
         v48.ARCHIVE[1]),
    )
    for index, (label, fingerprint) in enumerate(rows):
        lines.append(
            f'<text x="65" y="{1914 + index * 16}" class="foot">'
            f'{label}: {fingerprint}</text>'
        )
    lines.extend((
        '<text x="65" y="2180" class="small">The native build recipe '
        'is frozen only. No compiler or corrected candidate has run.</text>',
        '<text x="65" y="2204" class="small">Stable baseline: '
        'CPython 3.14.6. Hidden final comparison: unopened. Winner: none.</text>',
        '<!-- Native build not run. No archive, compiler, matching worker, '
        'native code, timing or holdout is accessed. -->',
        '</svg>',
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    current_inputs = ("Graph inputs SHA-256: " + inputs_sha).encode("ascii")
    current_source = ("Graph renderer SHA-256: " + source_sha).encode("ascii")
    old_inputs = (
        "Historical V50 graph inputs SHA-256: " + V50["inputs"][1]
    ).encode("ascii")
    old_source = (
        "Historical V50 graph renderer SHA-256: " + V50["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(current_inputs) == 1 and raw.count(current_source) == 1
        and raw.count(old_inputs) == 1 and raw.count(old_source) == 1
        and ("Graph inputs SHA-256: " + V50["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V50["source"][1]).encode("ascii")
        not in raw,
        "mark only true V51 graph inputs as current and pushed V50 historical",
    )
    lower = raw.lower()
    for phrase in (
        b'height="2250"', b"building a faster python re", b"928 differences",
        b"compatible replacements", b"not measured", b"4.2m unopened",
        b"13 real workers", b"8,965 explicitly verified",
        b"rust build recipe frozen", b"native build not yet run",
        b"same rust family", b"not a seventh replacement",
        b"31,237", b"signature checks", b"public-interface observations",
        b"large-input observations", b"17 pass", b"7 fail", b"22 pass",
        b"3 not run", b"2,147,483,648", b"1,036", b"1,087",
        b"1,230", b"1,262", b"1,764", b"2,172", b"179 / 184",
        b"not generated", b"not opened", b"does not prove a breakdown",
        b"winner: none", b"failure archive sha-256 (receipt-attested; not opened)",
    ):
        base.need(phrase in lower,
                  "retain a readable and truthful frozen-build chart: "
                  + repr(phrase))
    for falsehood in (
        b"native build passed", b"native build completed",
        b"compiled candidate", b"corrected candidate passed",
        b"rust candidate passed", b"rust replacement qualified",
        b"30,309 verified passes", b"30309 verified passes",
        b"variant tested", b"variant built", b"repair proven",
        b"896 repaired", b"672 repaired", b"224 repaired", b"32 repaired",
        b"seventh candidate family", b"winner selected", b"holdout opened",
        b"rust matching not run", b"faster than python",
    ):
        base.need(falsehood not in lower,
                  "reject invented native-build evidence: " + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "write exactly one final accessible V51 SVG linefeed")
    return raw


def build(previous: types.ModuleType,
          v49: types.ModuleType, v48: types.ModuleType,
          v47: types.ModuleType, v46: types.ModuleType,
          v45: types.ModuleType, v44: types.ModuleType,
          v43: types.ModuleType, v42: types.ModuleType,
          v41: types.ModuleType, v40: types.ModuleType,
          base: types.ModuleType, options: argparse.Namespace) -> tuple[
              dict, tuple[tuple[str, bytes], ...],
          ]:
    source_sha = base.checked(options.source_sha256, "exact future-build graph")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "require the exact independently supplied V51 source bytes")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                 private=True)
    old, old_inputs, old_svg = authenticate_v50(
        previous, v49, v48, v47, v46, v45, v44, v43, v42, v41,
        v40, base,
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
    snapshot["preserved_v50_replaced_snapshot_fields"] = {
        key: copy.deepcopy(prior[key]) for key in updates if key in prior
    }
    validate_snapshot(previous, v49, v48, v47, v46, v45, v44, v43,
                      v42, v41, v40, base, snapshot)
    predecessors = {role: base.pin(*pin) for role, pin in V50.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 51,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(previous, v49, v48, v47, v46, v45, v44, v43,
                   v42, v41, v40, base, snapshot, old_svg,
                   source_sha, base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "retain the reference and exactly six original first-party families")
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 179,
            "authenticated_history_reference_lower_bound": 184,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "native_build_v16_source_freeze": copy.deepcopy(proof),
                "native_build_v16_feature_status": FEATURE_STATUS,
                "native_build_v16_same_existing_rust_family": True,
                "native_build_v16_preserved_buffer_sha256": BUFFER[1],
                "native_build_v16_preserved_combined_sha256":
                    PICKLE["variant"][1],
                "native_build_v16_build_status": "NOT RUN",
                "native_build_v16_matching_status": "NOT RUN",
                "native_build_v16_repair_effectiveness": "NOT MEASURED",
                "native_build_v16_verified_repaired_case_count": "NOT MEASURED",
                "native_build_v16_failure_categories_proven_by_receipt": False,
                "native_build_v16_candidate_workers_started": 0,
                "native_build_v16_compiler_processes_started": 0,
                "native_build_v16_qualified": False,
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
        "version": 51,
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
              "keep all V51 native-recipe graph owners safely bounded")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_feature(base: types.ModuleType) -> dict:
    owners: dict[str, dict] = {}
    for index, (role, path) in enumerate(FEATURE_PATHS.items()):
        digest = hashlib.sha256(
            ("v51-native-recipe-synthetic-" + role).encode("ascii")
        ).hexdigest()
        owners[role] = base.synthetic_owner((path, digest, 350 + index),
                                           951001 + index)
    pins = {role: base.pin(*item) for role, item in V50.items()}
    contract = {
        "schema": FEATURE_SCHEMA,
        "version": 16,
        "phase": "CANDIDATES",
        "status": FEATURE_STATUS,
        "family": "rust",
        "source": {
            "path": owners["source"]["path"],
            "sha256": owners["source"]["sha256"],
        },
        "protocol": {
            "path": owners["protocol"]["path"],
            "sha256": owners["protocol"]["sha256"],
        },
        "current_pushed_graph": {
            "version": 50,
            "authenticated_evidence_owner_lower_bound": 176,
            "authenticated_history_reference_lower_bound": 181,
            **pins,
        },
        "preserved_corrected_python_reference": {
            "actual_v7_failure_receipt": base.pin(*RECEIPT),
        },
        "v49_buffer_shape_source_feature": {
            "variant": base.pin(*BUFFER),
        },
        "v50_combined_buffer_shape_and_pickle_source_feature": {
            "variant": base.pin(*PICKLE["variant"]),
        },
        "future_offline_native_build": {"build_status": "NOT RUN"},
        "phase_boundary": {
            **{
                key: 0 for key in (
                    "actual_archives_opened", "actual_archives_decompressed",
                    "actual_benchmark_files_read", "actual_candidate_imports",
                    "actual_candidate_workers_started", "actual_clock_samples",
                    "actual_compiler_processes_started", "actual_hidden_cases_read",
                    "actual_holdout_cases_read", "actual_native_activations",
                    "actual_native_libraries_loaded", "actual_network_requests",
                    "actual_reference_workers_started", "actual_source_builds_started",
                    "actual_workspace_mutations", "timing_trials_run",
                )
            },
            "candidate_correctness": "NOT MEASURED",
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
            "holdout": "NOT OPENED",
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
    raise base.GraphError("accepted forged V16 native-recipe evidence: "
                          + description)


def self_test(previous: types.ModuleType,
              v49: types.ModuleType, v48: types.ModuleType,
              v47: types.ModuleType, v46: types.ModuleType,
              v45: types.ModuleType, v44: types.ModuleType,
              v43: types.ModuleType, v42: types.ModuleType,
              v41: types.ModuleType, v40: types.ModuleType,
              base: types.ModuleType) -> dict:
    history = previous.self_test(v49, v48, v47, v46, v45, v44,
                                 v43, v42, v41, v40, base)
    base.need(
        history.get("status") == "PASS"
        and history.get("rejected_hostile_control_count") == 2434
        and history.get("actual_rust_v7_semantic_mismatch_count") == 928
        and history.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and history.get("actual_rust_v7_candidate_workers") == 13
        and history.get("reference_archive_gzip_inflation_count") == 0
        and history.get("matching_archive_gzip_inflation_count") == 0
        and history.get("source_build_archive_gzip_inflation_count_by_graph") == 0
        and history.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and history.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "retain every one of the 2,434 real V50 source-only hostile controls",
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
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v51")),
            ("filesystem", lambda: os.open("forbidden-v51", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v51")),
            ("write", lambda: os.mkdir("forbidden-v51")),
            ("process", lambda: subprocess.run(("forbidden-v51",))),
            ("process", lambda: subprocess.Popen(("forbidden-v51",))),
            ("process", lambda: os.execv("/forbidden-v51", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically prevent V51 source-only " + kind)
            else:
                raise base.GraphError("a forbidden V51 native action escaped")
        base.need(rejected >= 65,
                  "reject all forged native-recipe status and source ownership")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 51,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v50_hostile_controls": 2434,
            "new_v51_hostile_controls": rejected,
            "rejected_hostile_control_count": 2434 + rejected,
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
            "actual_current_graph_predecessor_version": 50,
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
            "rust_native_build_v16_feature_status": FEATURE_STATUS,
            "rust_native_build_v16_build_status": "NOT RUN",
            "rust_native_build_v16_matching_status": "NOT RUN",
            "rust_native_build_v16_repair_effectiveness": "NOT MEASURED",
            "rust_native_build_v16_new_candidate_family_count": 0,
            "rust_native_build_v16_preserved_buffer_sha256": BUFFER[1],
            "rust_native_build_v16_preserved_combined_sha256":
                PICKLE["variant"][1],
            "rust_native_build_v16_failure_categories_proven_by_receipt": False,
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
            "authenticated_evidence_owner_lower_bound": 179,
            "authenticated_history_reference_lower_bound": 184,
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
              "write only the three authorized V51 future-build graph assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete V51 future-build graph bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid() and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish a private and complete future-build graph owner")
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
    base.need(confirmed == raw, "re-authenticate complete exact V51 output")


def result(base: types.ModuleType, snapshot: dict, outputs: dict[str, bytes],
           source_sha: str, *, written: bool, suffix: str) -> dict:
    return {
        **copy.deepcopy(snapshot),
        "schema": SCHEMA + suffix,
        "version": 51,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 50,
        **{"previous_overview_" + role + "_sha256": pin[1]
           for role, pin in V50.items()},
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
        (previous, v49, v48, v47, v46, v45, v44,
         v43, v42, v41, v40, base) = load_v50()
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256"
                             for role in ("source", "inputs", "summary", "svg"))
            for flag in FEATURE_FLAGS.values():
                forbidden.extend((flag + "_sha256", flag + "_bytes"))
            forbidden.extend(("inputs_sha256", "summary_sha256", "svg_sha256"))
            base.need(all(getattr(options, key) is None for key in forbidden),
                      "synthetic-only V51 self-test cannot accept real owner pins")
            sys.stdout.buffer.write(base.canonical(self_test(
                previous, v49, v48, v47, v46, v45, v44,
                v43, v42, v41, v40, base,
            )))
            return 0
        snapshot, pairs = build(
            previous, v49, v48, v47, v46, v45, v44,
            v43, v42, v41, v40, base, options,
        )
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256, "exact current V51")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "publish only three authorized new V51 overview assets")
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )))
            return 0
        output_pins = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact complete V51 graph inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact complete V51 graph summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact accessible V51 graph image",
            ),
        }
        for path, fingerprint in output_pins.items():
            raw, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                     private=True)
            base.need(raw == outputs[path],
                      "reproduce every actual future-build graph output byte")
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source_sha,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V51 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V51 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
