#!/usr/bin/env python3
"""Report the real offline Rust build without claiming a compatibility run."""

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
SELF = "tools/render_candidate_current_overview_v52.py"
OUTPUT = "docs/evidence/candidate-current-overview-v52"
SCHEMA = "rebar-candidate-current-overview-v52"
V51 = {
    "source": (
        "tools/render_candidate_current_overview_v51.py",
        "2fc7a901aa8e94fae62793851643a7c776d0d2f16a01957cbeb14f1792f6ce4c",
        59206,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v51.inputs.json",
        "b86813b7078479a121584d1e6bf98985d94ee8f22f524e53b9cce2da2723f767",
        583232,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v51.json",
        "c76d08488bbd3dae80db3e0ee46fdabeabc218b0f03e6e02bce74a3b190799ef",
        1602914,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v51.svg",
        "76be0cfd9f3624a01be21738fb25075290a59319138af33af5a5029dc114efa5",
        14253,
    ),
}
BUILD = {
    "source": (
        "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py",
        "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a",
        134640,
    ),
    "protocol": (
        "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md",
        "315f0a24e64b50804565f86c6ca4187024c4a1db5a23ab2f57c8805ed37f51f5",
        6497,
    ),
    "contract": (
        "oracle/phase2/rust-buffer-shape-source-build-v16.json",
        "4f82f88da3329c6bacac2092af19d915d379f90101dcd9840366274355cc92b7",
        18260,
    ),
}
ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle.json.gz",
    "c24c0e1544003b231bac3e45601faabfd1c1e5c181d89fce7d660a2df4a29270",
    109671,
)
RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v16-rust-phase2-v16-rust-buffer-shape-"
    "pickle-publication-receipt.json",
    "c893812a1796cce056de5e2feff2289df34ff816158685730205996549e338cb",
    3459,
)
DEVICE = 2064
ARCHIVE_INODE = 524993
RECEIPT_INODE = 524994
EVIDENCE_DIRECTORY_INODE = 524459
BUFFER_SHA = "29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3"
COMBINED_SHA = "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335"
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]
PUBLIC_COUNTS = {
    "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1, "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22, "FAIL": 1, "NOT RUN": 3,
    "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1,
}


def load_v51() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType,
]:
    path, expected, size = V51["source"]
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
            raise ValueError("reject replaced actual pushed V51 graph source")
        parts: list[bytes] = []
        remaining = size
        while remaining:
            part = os.read(handle, min(262144, remaining))
            if not part:
                raise ValueError("reject truncated actual V51 graph source")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject trailing actual V51 graph source")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject replacement while loading pushed V51")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_pushed_frozen_native_recipe_graph_v51")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    v50, v49, v48, v47, v46, v45, v44, v43, v42, v41, v40, base = (
        previous.load_v50()
    )
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v51"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS,
        "authenticate exactly the real pushed V51 native-recipe renderer",
    )
    return (previous, v50, v49, v48, v47, v46, v45, v44,
            v43, v42, v41, v40, base)


def expected_archive() -> dict:
    return {
        "path": ARCHIVE[0],
        "sha256": ARCHIVE[1],
        "bytes": ARCHIVE[2],
        "device": DEVICE,
        "inode": ARCHIVE_INODE,
        "mode": "0600",
        "nlink": 1,
        "uid": os.geteuid(),
        "sha256_source": "ATTESTED BY SMALL DURABLE RECEIPT ONLY",
        "content_opened_by_graph": False,
        "content_read_by_graph": False,
        "content_sha256_recomputed_by_graph": False,
        "archive_inflated_by_graph": False,
    }


def validate_receipt(base: types.ModuleType, receipt: object) -> None:
    base.need(type(receipt) is dict,
              "reject missing actual small durable V16 build receipt")
    assert isinstance(receipt, dict)
    expected = {
        "schema":
            "rebar-phase2-owned-rust-buffer-shape-source-build-v16-"
            "durable-publication-receipt",
        "status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": "PASS",
        "family": "rust",
        "label": "phase2-v16-rust-buffer-shape-pickle",
        "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "archive_relative": ARCHIVE[0],
        "archive_sha256": ARCHIVE[1],
        "archive_bytes": ARCHIVE[2],
        "current_graph_version": 50,
        "prepublication_evidence_owner_lower_bound": 176,
        "prepublication_history_reference_lower_bound": 181,
        "new_actual_evidence_owner_count": 2,
        "evidence_owner_lower_bound_after_publication": 178,
        "history_reference_lower_bound_after_publication": 183,
        "global_evidence_owner_census": "NOT MEASURED",
        "global_history_reference_census": "NOT MEASURED",
        "historical_actual_rust_matching_status": "FAIL",
        "historical_actual_rust_mismatch_count": 928,
        "historical_actual_rust_verified_passing_case_count": 8965,
        "historical_actual_rust_candidate_workers": 13,
        "buffer_variant_sha256": BUFFER_SHA,
        "combined_bridge_sha256": COMBINED_SHA,
        "combined_bridge_bytes": 181004,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": 31934,
        "combined_bridge_overlay_apply_count": 2,
        "corrected_public_adapter_overlay_apply_count": 2,
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_processes_started": 0,
        "candidate_workers_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    for key, value in expected.items():
        base.need(receipt.get(key) == value,
                  "reject forged actual native-build receipt: " + key)
    archive = receipt.get("archive_publication")
    base.need(
        type(archive) is dict
        and archive.get("path") == str(ROOT / ARCHIVE[0])
        and archive.get("sha256") == ARCHIVE[1]
        and archive.get("bytes") == ARCHIVE[2]
        and archive.get("device") == DEVICE
        and archive.get("inode") == ARCHIVE_INODE
        and type(archive.get("write_calls")) is int
        and archive["write_calls"] > 0
        and archive.get("exclusive_creation") is True
        and archive.get("same_inode_readback_verified") is True
        and archive.get("file_fsync_completed") is True,
        "bind archive publication by the genuine small receipt only",
    )
    directory = receipt.get("archive_directory_fsync")
    base.need(
        type(directory) is dict
        and directory.get("completed") is True
        and directory.get("device") == DEVICE
        and directory.get("inode") == EVIDENCE_DIRECTORY_INODE,
        "require durable archive directory identity without opening archive",
    )
    for absent in (
        "publication_status", "actual_worker_process_ids",
        "worker_process_ids", "compiler_process_ids", "phase_count",
        "unique_process_count", "phases", "raw_elf_comparisons",
        "native_outputs", "compiled_engine_sha256", "compiled_bridge_sha256",
    ):
        base.need(absent not in receipt,
                  "never invent a native detail absent from the small receipt: "
                  + absent)


def archive_metadata(base: types.ModuleType) -> dict:
    observed = os.stat(str(ROOT / ARCHIVE[0]), follow_symlinks=False)
    base.need(
        stat.S_ISREG(observed.st_mode)
        and observed.st_uid == os.geteuid()
        and observed.st_dev == DEVICE
        and observed.st_ino == ARCHIVE_INODE
        and observed.st_nlink == 1
        and observed.st_size == ARCHIVE[2]
        and stat.S_IMODE(observed.st_mode) == 0o600,
        "authenticate durable build archive by metadata only; never open it",
    )
    directory = os.stat(str(ROOT / Path(ARCHIVE[0]).parent),
                        follow_symlinks=False)
    base.need(stat.S_ISDIR(directory.st_mode)
              and directory.st_dev == DEVICE
              and directory.st_ino == EVIDENCE_DIRECTORY_INODE,
              "confirm only actual durable evidence directory metadata")
    return expected_archive()


def make_build_proof(base: types.ModuleType, receipt_owner: dict,
                     receipt: dict, archive: dict) -> dict:
    validate_receipt(base, receipt)
    base.need(archive == expected_archive(),
              "bind only archive lstat and receipt-attested content digest")
    proof = {
        "schema": SCHEMA + "-authenticated-actual-offline-native-build",
        "version": 16,
        "receipt": copy.deepcopy(receipt_owner),
        "complete_durable_publication_receipt": copy.deepcopy(receipt),
        "archive_metadata_only": copy.deepcopy(archive),
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": "PASS",
        "family": "rust",
        "actual_compiler_process_count": 28,
        "expected_actual_compiler_process_count": 28,
        "compiler_unique_pid_vector_present_in_small_receipt": False,
        "independent_phase_vector_present_in_small_receipt": False,
        "binary_output_hashes_present_in_small_receipt": False,
        "two_byte_identical_phases_provenance":
            "AUTHENTICATED FROZEN SUCCESS BRANCH; NOT A SMALL RECEIPT FIELD",
        "preserved_buffer_variant_sha256": BUFFER_SHA,
        "combined_bridge_source_sha256": COMBINED_SHA,
        "combined_bridge_source_bytes": 181004,
        "combined_bridge_is_native_output_digest": False,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": 31934,
        "combined_bridge_overlay_apply_count": 2,
        "corrected_public_adapter_overlay_apply_count": 2,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded_by_graph": 0,
        "archive_opened_by_graph": False,
        "archive_read_by_graph": False,
        "archive_sha256_recomputed_by_graph": False,
        "archive_inflated_by_graph": False,
        "actual_graph_predecessor_version": 51,
        "historical_receipt_source_graph_version": 50,
        "historical_receipt_prepublication_evidence_lower_bound": 176,
        "historical_receipt_prepublication_history_lower_bound": 181,
        "historical_receipt_resulting_evidence_lower_bound": 178,
        "historical_receipt_resulting_history_lower_bound": 183,
        "actual_current_prepublication_evidence_lower_bound": 179,
        "actual_current_prepublication_history_lower_bound": 184,
        "new_exact_durable_build_owner_count": 2,
        "actual_current_evidence_owner_lower_bound_after_publication": 181,
        "actual_current_history_reference_lower_bound_after_publication": 186,
        "actual_rust_v7_semantic_mismatch_count": 928,
        "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
        "actual_rust_v7_candidate_workers": 13,
        "actual_clock_samples_by_graph": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_actual_native_build_binding_sha256"] = base.digest(
        base.canonical(proof),
    )
    validate_build_proof(base, proof)
    return proof


def validate_build_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject absent actual V16 build evidence")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-actual-offline-native-build",
        "version": 16,
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": "PASS",
        "family": "rust",
        "actual_compiler_process_count": 28,
        "expected_actual_compiler_process_count": 28,
        "compiler_unique_pid_vector_present_in_small_receipt": False,
        "independent_phase_vector_present_in_small_receipt": False,
        "binary_output_hashes_present_in_small_receipt": False,
        "two_byte_identical_phases_provenance":
            "AUTHENTICATED FROZEN SUCCESS BRANCH; NOT A SMALL RECEIPT FIELD",
        "preserved_buffer_variant_sha256": BUFFER_SHA,
        "combined_bridge_source_sha256": COMBINED_SHA,
        "combined_bridge_source_bytes": 181004,
        "combined_bridge_is_native_output_digest": False,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": 31934,
        "combined_bridge_overlay_apply_count": 2,
        "corrected_public_adapter_overlay_apply_count": 2,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded_by_graph": 0,
        "archive_opened_by_graph": False,
        "archive_read_by_graph": False,
        "archive_sha256_recomputed_by_graph": False,
        "archive_inflated_by_graph": False,
        "actual_graph_predecessor_version": 51,
        "historical_receipt_source_graph_version": 50,
        "historical_receipt_prepublication_evidence_lower_bound": 176,
        "historical_receipt_prepublication_history_lower_bound": 181,
        "historical_receipt_resulting_evidence_lower_bound": 178,
        "historical_receipt_resulting_history_lower_bound": 183,
        "actual_current_prepublication_evidence_lower_bound": 179,
        "actual_current_prepublication_history_lower_bound": 184,
        "new_exact_durable_build_owner_count": 2,
        "actual_current_evidence_owner_lower_bound_after_publication": 181,
        "actual_current_history_reference_lower_bound_after_publication": 186,
        "actual_rust_v7_semantic_mismatch_count": 928,
        "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
        "actual_rust_v7_candidate_workers": 13,
        "actual_clock_samples_by_graph": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    for key, value in expected.items():
        base.need(proof.get(key) == value,
                  "reject invented actual build or candidate result: " + key)
    owner = proof.get("receipt")
    base.need(
        type(owner) is dict
        and owner.get("path") == RECEIPT[0]
        and owner.get("sha256") == RECEIPT[1]
        and owner.get("bytes") == RECEIPT[2]
        and owner.get("device") == DEVICE
        and owner.get("inode") == RECEIPT_INODE
        and owner.get("mode") == "0600"
        and owner.get("nlink") == 1
        and owner.get("uid") == os.geteuid(),
        "bind the exact small real build receipt without touching an archive",
    )
    validate_receipt(base, proof.get("complete_durable_publication_receipt"))
    base.need(proof.get("archive_metadata_only") == expected_archive(),
              "retain archive metadata only and never read its content")
    body = {key: value for key, value in proof.items()
            if key != "complete_actual_native_build_binding_sha256"}
    base.need(proof.get("complete_actual_native_build_binding_sha256")
              == base.digest(base.canonical(body)),
              "bind real build and independent historic/current accounting")


def authenticate_result(base: types.ModuleType,
                        options: argparse.Namespace) -> dict:
    base.need(
        base.checked(options.receipt_sha256, "actual durable small build receipt")
        == RECEIPT[1]
        and options.receipt_bytes == RECEIPT[2]
        and options.receipt_device == DEVICE
        and options.receipt_inode == RECEIPT_INODE
        and base.checked(options.archive_sha256, "receipt-attested build archive")
        == ARCHIVE[1]
        and options.archive_bytes == ARCHIVE[2]
        and options.archive_device == DEVICE
        and options.archive_inode == ARCHIVE_INODE,
        "pin the genuine two durable build owners without opening the archive",
    )
    raw, receipt_owner = base.read_owner(*RECEIPT, private=True)
    receipt = base.document(raw, "actual complete small native build receipt")
    return make_build_proof(base, receipt_owner, receipt,
                            archive_metadata(base))


def v51_reproduction_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V51["source"][1],
        source_bytes=V51["source"][2],
        previous_source_sha256=previous.V50["source"][1],
        previous_inputs_sha256=previous.V50["inputs"][1],
        previous_summary_sha256=previous.V50["summary"][1],
        previous_svg_sha256=previous.V50["svg"][1],
        build_source_sha256=BUILD["source"][1],
        build_source_bytes=BUILD["source"][2],
        build_protocol_sha256=BUILD["protocol"][1],
        build_protocol_bytes=BUILD["protocol"][2],
        build_contract_sha256=BUILD["contract"][1],
        build_contract_bytes=BUILD["contract"][2],
    )


def authenticate_v51(previous: types.ModuleType,
                     v50: types.ModuleType, v49: types.ModuleType,
                     v48: types.ModuleType, v47: types.ModuleType,
                     v46: types.ModuleType, v45: types.ModuleType,
                     v44: types.ModuleType, v43: types.ModuleType,
                     v42: types.ModuleType, v41: types.ModuleType,
                     v40: types.ModuleType, base: types.ModuleType,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    raw: dict[str, bytes] = {}
    for role, item in V51.items():
        base.need(base.checked(supplied.get(role), "actual V51 " + role)
                  == item[1],
                  "require only genuine pushed V51 predecessor " + role)
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete current V51 graph summary")
    inputs = base.document(raw["inputs"], "complete current V51 graph inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(v50, v49, v48, v47, v46, v45, v44,
                               v43, v42, v41, v40, base, snapshot)
    reconstructed, pairs = previous.build(
        v50, v49, v48, v47, v46, v45, v44, v43, v42, v41, v40,
        base, v51_reproduction_options(previous),
    )
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v51-summary"
        and old.get("version") == 51
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V51["source"])
        and old.get("inputs") == base.pin(*V51["inputs"])
        and old.get("svg") == base.pin(*V51["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v51-inputs"
        and inputs.get("version") == 51
        and inputs.get("renderer") == base.pin(*V51["source"])
        and snapshot == reconstructed
        and raw["inputs"] == expected[V51["inputs"][0]]
        and raw["summary"] == expected[V51["summary"][0]]
        and raw["svg"] == expected[V51["svg"][0]]
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("actually_tested_corrected_candidate_families") == ["rust"]
        and old.get("actually_tested_corrected_candidate_family_count") == 1
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("actually_runnable_candidate_family_count") == 0
        and old.get("qualified_candidate_count") == 0
        and old.get("authenticated_evidence_owner_lower_bound") == 179
        and old.get("authenticated_history_reference_lower_bound") == 184
        and old.get("rust_buffer_shape_v1_variant_source", {}).get("sha256")
        == BUFFER_SHA
        and old.get("rust_match_pickle_v1_variant_source", {}).get("sha256")
        == COMBINED_SHA
        and old.get("rust_native_build_v16_build_status") == "NOT RUN"
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "reproduce the complete pushed V51 graph and distinguish future build",
    )
    return old, inputs, raw["svg"]


def result_fields(proof: dict) -> dict:
    receipt = proof["receipt"]
    return {
        "actual_rust_v16_native_build": copy.deepcopy(proof),
        "actual_rust_v16_build_status": "PASS",
        "actual_rust_v16_publication_status": "PASS",
        "actual_rust_v16_publication_pass_means": "DURABLE PUBLICATION ONLY",
        "actual_rust_v16_build_family": "rust",
        "actual_rust_v16_new_candidate_family_count": 0,
        "actual_rust_v16_expected_compiler_process_count": 28,
        "actual_rust_v16_compiler_process_count": 28,
        "actual_rust_v16_compiler_pid_vector_present_in_receipt": False,
        "actual_rust_v16_phase_vector_present_in_receipt": False,
        "actual_rust_v16_native_artifact_digests_present_in_receipt": False,
        "actual_rust_v16_two_phase_reproducibility_source":
            "AUTHENTICATED FROZEN SUCCESS BRANCH; NOT A SMALL RECEIPT FIELD",
        "actual_rust_v16_receipt": copy.deepcopy(receipt),
        "actual_rust_v16_receipt_sha256": RECEIPT[1],
        "actual_rust_v16_receipt_bytes": RECEIPT[2],
        "actual_rust_v16_receipt_inode": RECEIPT_INODE,
        "actual_rust_v16_archive_sha256_attested_by_receipt": ARCHIVE[1],
        "actual_rust_v16_archive_bytes": ARCHIVE[2],
        "actual_rust_v16_archive_inode": ARCHIVE_INODE,
        "actual_rust_v16_archive_opened_by_graph": False,
        "actual_rust_v16_archive_inflated_by_graph": False,
        "actual_rust_v16_archive_sha256_recomputed_by_graph": False,
        "actual_rust_v16_combined_bridge_source_sha256": COMBINED_SHA,
        "actual_rust_v16_combined_bridge_source_bytes": 181004,
        "actual_rust_v16_combined_bridge_is_native_binary_digest": False,
        "actual_rust_v16_corrected_public_adapter_sha256": ADAPTER_SHA,
        "actual_rust_v16_corrected_public_adapter_bytes": 31934,
        "actual_rust_v16_combined_bridge_overlay_apply_count": 2,
        "actual_rust_v16_corrected_public_adapter_overlay_apply_count": 2,
        "actual_rust_v16_candidate_matching_status": "NOT RUN",
        "actual_rust_v16_candidate_correctness": "NOT MEASURED",
        "actual_rust_v16_candidate_qualified": False,
        "actual_rust_v16_candidate_workers_started": 0,
        "actual_rust_v16_candidate_processes_started": 0,
        "actual_rust_v16_historical_receipt_source_graph_version": 50,
        "actual_rust_v16_historical_receipt_prepublication_evidence_lower_bound":
            176,
        "actual_rust_v16_historical_receipt_prepublication_history_lower_bound":
            181,
        "actual_rust_v16_historical_receipt_resulting_evidence_lower_bound": 178,
        "actual_rust_v16_historical_receipt_resulting_history_lower_bound": 183,
        "actual_rust_v16_current_prepublication_evidence_lower_bound": 179,
        "actual_rust_v16_current_prepublication_history_lower_bound": 184,
        "actual_rust_v16_new_durable_owner_count": 2,
        "actual_current_graph_predecessor_version": 51,
        "authenticated_evidence_owner_lower_bound": 181,
        "authenticated_history_reference_lower_bound": 186,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(previous: types.ModuleType,
                      v50: types.ModuleType, v49: types.ModuleType,
                      v48: types.ModuleType, v47: types.ModuleType,
                      v46: types.ModuleType, v45: types.ModuleType,
                      v44: types.ModuleType, v43: types.ModuleType,
                      v42: types.ModuleType, v41: types.ModuleType,
                      v40: types.ModuleType, base: types.ModuleType,
                      snapshot: object) -> None:
    base.need(type(snapshot) is dict, "reject omitted actual build snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("actual_rust_v16_native_build")
    validate_build_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(snapshot.get(key) == value,
                  "reject an invented build or outcome field: " + key)
    replaced = snapshot.get("preserved_v51_replaced_snapshot_fields")
    base.need(type(replaced) is dict, "preserve every complete actual V51 field")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v51_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(v50, v49, v48, v47, v46, v45, v44,
                               v43, v42, v41, v40, base, history)
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
        == BUFFER_SHA
        and snapshot.get("rust_match_pickle_v1_variant_source", {}).get("sha256")
        == COMBINED_SHA
        and snapshot.get("actually_tested_corrected_candidate_families") == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count") == 1
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 181
        and snapshot.get("authenticated_history_reference_lower_bound") == 186
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
        "preserve actual matching failure, 28-process build and actual bounds",
    )


def make_svg(previous: types.ModuleType,
             v50: types.ModuleType, v49: types.ModuleType,
             v48: types.ModuleType, v47: types.ModuleType,
             v46: types.ModuleType, v45: types.ModuleType,
             v44: types.ModuleType, v43: types.ModuleType,
             v42: types.ModuleType, v41: types.ModuleType,
             v40: types.ModuleType, base: types.ModuleType,
             snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(previous, v50, v49, v48, v47, v46, v45, v44,
                      v43, v42, v41, v40, base, snapshot)
    source_sha = base.checked(source_sha, "actual V52 renderer footer")
    inputs_sha = base.checked(inputs_sha, "actual V52 graph inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v51-title", "v52-title")
    visible = visible.replace("v51-description", "v52-description")
    changes = (
        (
            "Rust differs on 928 checks; its future native build is not run</title>",
            "Rust native build passes; full compatibility is not yet proved</title>",
            "show actual completed build separately from matching",
        ),
        (
            "Its reproducible native-build recipe is frozen; "
            "the native build has not run.",
            "Its offline native build passed and recorded 28 successful "
            "compiler operations. The rebuilt candidate has not been "
            "matching-tested.",
            "attribute 28 operations to the actual durable build receipt only",
        ),
        (
            "Three and only three genuinely frozen native-build recipe owners "
            "raise authenticated lower bounds from 176 and 181 to 179 and 184;",
            "Two and only two genuine durable build-result owners raise "
            "actual current lower bounds from 179 and 184 to 181 and 186;",
            "distinguish the actual V51 floor from historical receipt counts",
        ),
        (
            "Rust build recipe frozen — NATIVE BUILD NOT YET RUN",
            "Rust native build: PASS — candidate matching NOT RUN",
            "show genuine build success without claiming candidate correctness",
        ),
        (
            "The combined buffer-and-serialization source remains unbuilt. "
            "Its frozen recipe is the same Rust family, not a seventh "
            "replacement.",
            "The combined first-party Rust bridge was successfully built "
            "offline. Matching is NOT RUN; it is the same Rust family, "
            "not a seventh replacement.",
            "show a successful build and honestly untested candidate",
        ),
        (
            "Actually tested; both new source ideas remain unbuilt",
            "Old matching failed; rebuilt candidate not matching-tested",
            "preserve the current real failed Rust result and separate rebuilt status",
        ),
        (
            "Three build-recipe files; no native build yet",
            "Actual offline native build passed; matching still not run",
            "display the one real build experiment and remaining correctness gate",
        ),
        (
            "Exactly three authenticated future build-recipe owners "
            "raise evidence lower bounds from 176 / 181 to 179 / 184.",
            "Exactly two new durable build-result owners raise actual "
            "current lower bounds from 179 / 184 to 181 / 186.",
            "count only the real archive and separately durable small receipt",
        ),
    )
    for before, after, explanation in changes:
        visible = v43.replace_once(base, visible, before, after, explanation)
    lines = visible.splitlines()
    index = next(
        i for i, line in enumerate(lines)
        if line.startswith('<rect x="44" y="1858" width="1352"')
    )
    lines = lines[:index]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="361" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact reproducible '
        'build evidence</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V51 graph inputs SHA-256", V51["inputs"][1]),
        ("Historical V51 graph renderer SHA-256", V51["source"][1]),
        ("Historical V51 graph summary SHA-256", V51["summary"][1]),
        ("Historical V51 graph image SHA-256", V51["svg"][1]),
        ("Preserved first-party buffer source SHA-256", BUFFER_SHA),
        ("Preserved combined first-party source SHA-256", COMBINED_SHA),
        ("Frozen V16 native-build source SHA-256", BUILD["source"][1]),
        ("Frozen V16 native-build protocol SHA-256", BUILD["protocol"][1]),
        ("Frozen V16 native-build contract SHA-256", BUILD["contract"][1]),
        ("Actual durable build publication receipt SHA-256", RECEIPT[1]),
        ("Actual build archive SHA-256 (receipt-attested; not opened)",
         ARCHIVE[1]),
    )
    for i, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + i * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2167" class="small">28 compiler operations '
        'are recorded. Phase identity and native binary hashes are not '
        'contained in the small receipt.</text>',
        '<text x="65" y="2187" class="small">Historical receipt '
        'lower bounds 178 / 183 are not the actual current 181 / 186.</text>',
        '<text x="65" y="2207" class="small">Candidate matching: '
        'NOT RUN. Holdout: unopened. Winning faster replacement: none.</text>',
        '<!-- Build PASS only. No archive content, candidate matching, '
        'native loading, timing or hidden holdout is accessed by this graph. -->',
        '</svg>',
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    current_inputs = ("Graph inputs SHA-256: " + inputs_sha).encode("ascii")
    current_source = ("Graph renderer SHA-256: " + source_sha).encode("ascii")
    old_inputs = (
        "Historical V51 graph inputs SHA-256: " + V51["inputs"][1]
    ).encode("ascii")
    old_source = (
        "Historical V51 graph renderer SHA-256: " + V51["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(current_inputs) == 1 and raw.count(current_source) == 1
        and raw.count(old_inputs) == 1 and raw.count(old_source) == 1
        and ("Graph inputs SHA-256: " + V51["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V51["source"][1]).encode("ascii")
        not in raw,
        "preserve exact actual V52 inputs and explicitly historical V51 footer",
    )
    lower = raw.lower()
    for phrase in (
        b'height="2250"', b"building a faster python re", b"928 differences",
        b"compatible replacements", b"not measured", b"4.2m unopened",
        b"13 real workers", b"8,965 explicitly verified",
        b"rust native build: pass", b"candidate matching not run",
        b"28 compiler operations", b"same rust family",
        b"not a seventh replacement", b"31,237", b"signature checks",
        b"public-interface observations", b"large-input observations",
        b"17 pass", b"7 fail", b"22 pass", b"3 not run",
        b"2,147,483,648", b"1,036", b"1,087", b"1,230", b"1,262",
        b"1,764", b"2,172", b"181 / 186", b"178 / 183",
        b"not generated", b"not opened", b"does not prove a breakdown",
        b"winning faster replacement: none",
        b"receipt-attested; not opened",
    ):
        base.need(phrase in lower,
                  "preserve true plain-language native-build result: "
                  + repr(phrase))
    for falsehood in (
        b"candidate matching passed", b"corrected candidate passed",
        b"rust replacement qualified", b"28 unique compiler pids",
        b"phase vector in receipt", b"native binary digest in receipt",
        b"30,309 verified passes", b"30309 verified passes",
        b"896 repaired", b"672 repaired", b"224 repaired", b"32 repaired",
        b"seventh candidate family", b"winner selected", b"holdout opened",
        b"faster than python", b"archive inflated by graph",
    ):
        base.need(falsehood not in lower,
                  "reject invented native-build or matching evidence: "
                  + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish actual V52 graph with one exact linefeed")
    return raw


def build(previous: types.ModuleType,
          v50: types.ModuleType, v49: types.ModuleType,
          v48: types.ModuleType, v47: types.ModuleType,
          v46: types.ModuleType, v45: types.ModuleType,
          v44: types.ModuleType, v43: types.ModuleType,
          v42: types.ModuleType, v41: types.ModuleType,
          v40: types.ModuleType, base: types.ModuleType,
          options: argparse.Namespace) -> tuple[
              dict, tuple[tuple[str, bytes], ...],
          ]:
    source_sha = base.checked(options.source_sha256, "exact current V52 source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "pin exact independently owned actual V52 renderer bytes")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                 private=True)
    old, inputs, old_svg = authenticate_v51(
        previous, v50, v49, v48, v47, v46, v45, v44,
        v43, v42, v41, v40, base,
        {
            "source": options.previous_source_sha256,
            "inputs": options.previous_inputs_sha256,
            "summary": options.previous_summary_sha256,
            "svg": options.previous_svg_sha256,
        },
    )
    proof = authenticate_result(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v51_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key]) for key in updates if key in original
    }
    validate_snapshot(previous, v50, v49, v48, v47, v46, v45, v44,
                      v43, v42, v41, v40, base, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V51.items()}
    next_inputs = copy.deepcopy(inputs)
    next_inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 52,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessor,
        **updates,
    })
    input_raw = base.canonical(next_inputs)
    svg = make_svg(previous, v50, v49, v48, v47, v46, v45, v44,
                   v43, v42, v41, v40, base, snapshot, old_svg,
                   source_sha, base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "preserve actual Python plus precisely six independent families")
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 181,
            "authenticated_history_reference_lower_bound": 186,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "actual_v16_native_build": copy.deepcopy(proof),
                "actual_v16_build_status": "PASS",
                "actual_v16_publication_pass_means":
                    "DURABLE PUBLICATION ONLY",
                "actual_v16_compiler_process_count": 28,
                "actual_v16_expected_compiler_process_count": 28,
                "actual_v16_unique_pid_vector_in_receipt": False,
                "actual_v16_phase_vector_in_receipt": False,
                "actual_v16_native_hashes_in_receipt": False,
                "actual_v16_combined_bridge_source_sha256": COMBINED_SHA,
                "actual_v16_combined_bridge_source_bytes": 181004,
                "actual_v16_combined_bridge_is_native_binary_digest": False,
                "actual_v16_candidate_matching_status": "NOT RUN",
                "actual_v16_candidate_correctness": "NOT MEASURED",
                "actual_v16_candidate_workers_started": 0,
                "actual_v16_candidate_qualified": False,
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
        "version": 52,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(input_raw),
                           len(input_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(max(len(input_raw), len(summary_raw), len(svg)) <= base.OWNER_LIMIT,
              "bound the complete real V52 archive-free graph owners")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_receipt() -> dict:
    return {
        "schema":
            "rebar-phase2-owned-rust-buffer-shape-source-build-v16-"
            "durable-publication-receipt",
        "status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": "PASS",
        "family": "rust",
        "label": "phase2-v16-rust-buffer-shape-pickle",
        "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "archive_relative": ARCHIVE[0],
        "archive_sha256": ARCHIVE[1],
        "archive_bytes": ARCHIVE[2],
        "archive_publication": {
            "path": str(ROOT / ARCHIVE[0]),
            "sha256": ARCHIVE[1],
            "bytes": ARCHIVE[2],
            "device": DEVICE,
            "inode": ARCHIVE_INODE,
            "write_calls": 1,
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
        },
        "archive_directory_fsync": {
            "completed": True,
            "device": DEVICE,
            "inode": EVIDENCE_DIRECTORY_INODE,
        },
        "current_graph_version": 50,
        "prepublication_evidence_owner_lower_bound": 176,
        "prepublication_history_reference_lower_bound": 181,
        "new_actual_evidence_owner_count": 2,
        "evidence_owner_lower_bound_after_publication": 178,
        "history_reference_lower_bound_after_publication": 183,
        "global_evidence_owner_census": "NOT MEASURED",
        "global_history_reference_census": "NOT MEASURED",
        "historical_actual_rust_matching_status": "FAIL",
        "historical_actual_rust_mismatch_count": 928,
        "historical_actual_rust_verified_passing_case_count": 8965,
        "historical_actual_rust_candidate_workers": 13,
        "buffer_variant_sha256": BUFFER_SHA,
        "combined_bridge_sha256": COMBINED_SHA,
        "combined_bridge_bytes": 181004,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": 31934,
        "combined_bridge_overlay_apply_count": 2,
        "corrected_public_adapter_overlay_apply_count": 2,
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_processes_started": 0,
        "candidate_workers_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_build_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged V16 actual build evidence: "
                          + description)


def self_test(previous: types.ModuleType,
              v50: types.ModuleType, v49: types.ModuleType,
              v48: types.ModuleType, v47: types.ModuleType,
              v46: types.ModuleType, v45: types.ModuleType,
              v44: types.ModuleType, v43: types.ModuleType,
              v42: types.ModuleType, v41: types.ModuleType,
              v40: types.ModuleType, base: types.ModuleType) -> dict:
    prior = previous.self_test(v50, v49, v48, v47, v46, v45, v44,
                               v43, v42, v41, v40, base)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 2517
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and prior.get("actual_rust_v7_candidate_workers") == 13
        and prior.get("source_build_archive_gzip_inflation_count_by_graph") == 0
        and prior.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "preserve all 2,517 immutable V51 source-only hostility controls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owner = base.synthetic_owner(RECEIPT, RECEIPT_INODE)
        proof = make_build_proof(base, owner, synthetic_receipt(),
                                 expected_archive())
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, key)
        for key, value in proof["receipt"].items():
            hostile = copy.deepcopy(proof)
            hostile["receipt"][key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "owner:" + key)
        for key, value in proof["complete_durable_publication_receipt"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_durable_publication_receipt"][key] = (
                v43.forged_value(base, value)
            )
            rejected += reject_control(base, hostile, "receipt:" + key)
        for key, value in proof["archive_metadata_only"].items():
            hostile = copy.deepcopy(proof)
            hostile["archive_metadata_only"][key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "archive-stat:" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v52")),
            ("filesystem", lambda: os.open("forbidden-v52", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v52")),
            ("write", lambda: os.mkdir("forbidden-v52")),
            ("process", lambda: subprocess.run(("forbidden-v52",))),
            ("process", lambda: subprocess.Popen(("forbidden-v52",))),
            ("process", lambda: os.execv("/forbidden-v52", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically prevent actual V52 graph " + kind)
            else:
                raise base.GraphError("a forbidden V52 physical action escaped")
        base.need(rejected >= 120,
                  "reject all forged archive, receipt, outcomes and bounds")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 52,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v51_hostile_controls": 2517,
            "new_v52_hostile_controls": rejected,
            "rejected_hostile_control_count": 2517 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_receipts_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_receipts_read_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
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
            "actual_current_graph_predecessor_version": 51,
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v7_distinct_worker_process_id_count": 13,
            "actual_rust_v7_infrastructure_failure_count": 0,
            "actual_rust_v16_build_status": "PASS",
            "actual_rust_v16_compiler_process_count": 28,
            "actual_rust_v16_candidate_matching_status": "NOT RUN",
            "actual_rust_v16_candidate_correctness": "NOT MEASURED",
            "actual_rust_v16_candidate_workers_started": 0,
            "actual_rust_v16_archive_opened_by_graph": False,
            "actual_rust_v16_archive_inflated_by_graph": False,
            "actual_rust_v16_archive_sha256_recomputed_by_graph": False,
            "actual_rust_v16_historical_receipt_resulting_evidence_lower_bound":
                178,
            "actual_rust_v16_historical_receipt_resulting_history_lower_bound":
                183,
            "authenticated_evidence_owner_lower_bound": 181,
            "authenticated_history_reference_lower_bound": 186,
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
              "publish only three newly authorized real V52 graph outputs")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete actual V52 graph output")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid() and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish an owner-only complete V52 graph asset")
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
    base.need(confirmed == raw, "re-authenticate complete actual V52 output")


def result(base: types.ModuleType, snapshot: dict, outputs: dict[str, bytes],
           source_sha: str, *, written: bool, suffix: str) -> dict:
    return {
        **copy.deepcopy(snapshot),
        "schema": SCHEMA + suffix,
        "version": 52,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 51,
        **{"previous_overview_" + key + "_sha256": value[1]
           for key, value in V51.items()},
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
    for role in ("receipt", "archive"):
        parser.add_argument("--" + role + "-sha256")
        parser.add_argument("--" + role + "-bytes", type=int)
        parser.add_argument("--" + role + "-inode", type=int)
        parser.add_argument("--" + role + "-device", type=int)
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        (previous, v50, v49, v48, v47, v46, v45,
         v44, v43, v42, v41, v40, base) = load_v51()
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256"
                             for role in ("source", "inputs", "summary", "svg"))
            for role in ("receipt", "archive"):
                forbidden.extend(role + "_" + field
                                 for field in ("sha256", "bytes", "inode", "device"))
            forbidden.extend(("inputs_sha256", "summary_sha256", "svg_sha256"))
            base.need(all(getattr(options, name) is None for name in forbidden),
                      "synthetic-only V52 self-test cannot accept real owner pins")
            sys.stdout.buffer.write(base.canonical(self_test(
                previous, v50, v49, v48, v47, v46, v45,
                v44, v43, v42, v41, v40, base,
            )))
            return 0
        snapshot, pairs = build(
            previous, v50, v49, v48, v47, v46, v45,
            v44, v43, v42, v41, v40, base, options,
        )
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256, "exact actual V52")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "publish only the three authorized actual V52 assets")
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )))
            return 0
        outputs_expected = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact actual V52 graph inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact actual V52 graph summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact accessible V52 graph chart",
            ),
        }
        for path, fingerprint in outputs_expected.items():
            raw, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                     private=True)
            base.need(raw == outputs[path],
                      "reproduce every actual archive-free build graph byte")
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source_sha,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V52 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V52 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
