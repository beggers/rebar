#!/usr/bin/env python3
"""Show the real failed Rust run without opening its compressed evidence."""

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
SELF = "tools/render_candidate_current_overview_v48.py"
OUTPUT = "docs/evidence/candidate-current-overview-v48"
SCHEMA = "rebar-candidate-current-overview-v48"
V47 = {
    "source": (
        "tools/render_candidate_current_overview_v47.py",
        "6deb2ffa07d50c1db2526afbea997bce3ebc1e518f569e4c8e3296c1351e5b43",
        81068,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v47.inputs.json",
        "e68b649124623525120af790d01939ea75adee6ac249d38a55b5a6d57fd72dbf",
        416821,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v47.json",
        "64fd1ad62eeb6c43748a4da19a66f869c93d3eafd9202375032c6214d79df05a",
        1144901,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v47.svg",
        "0c39d603f9bfeb2d2a2be41654653368405b25da9910b1fe18854350c4338b3c",
        18610,
    ),
}
CAMPAIGN = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        505616,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md",
        "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840",
        8433,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v7.json",
        "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5",
        46385,
    ),
}
ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v7-rust-"
    "phase2-v13-rust-pattern-repr-original-p0-failures.json.gz",
    "4112b4e6372f4f94d59eece2e514bda21001f0828d686162e18b631911fc2c99",
    3668825,
)
RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v7-rust-"
    "phase2-v13-rust-pattern-repr-original-p0-"
    "failures-publication-receipt.json",
    "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943",
    8450,
)
DEVICE = 2064
ARCHIVE_INODE = 524937
RECEIPT_INODE = 524938
JOURNAL_SHA256 = (
    "034c10076147677c775674643f06c3c1362f0ace47c45bc40fd4fe11df4ec843"
)
PUBLIC_STATUS = "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER"
PUBLIC_MATRIX_SHA256 = (
    "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
)
PUBLIC_COUNTS = {
    "PASS": 17,
    "FAIL": 7,
    "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1,
    "NOT OPENED": 1,
}
LARGE_MATRIX_SHA256 = (
    "a105aea287d093ff977819dda8971f592c3ed396eabd3133e5c52838ce8e2f65"
)
LARGE_COUNTS = {
    "PASS": 22,
    "FAIL": 1,
    "NOT RUN": 3,
    "NOT ESTABLISHED": 2,
    "NOT MEASURED": 3,
    "NOT OPENED": 1,
}
WORKER_PROCESS_IDS = (81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198)
HISTORICAL_V43 = {
    "source": "3b3647a2090fd98e89ea421b2d2a3018983e1014adecf9f0b30731b54ca51e8b",
    "inputs": "394fb27e12b9a48fbd8bdd353930084891c09118e0cfa49fc90f596124e15017",
    "summary": "1c5ea146e6d40f0e81f2fe274f2a1a50fe01efdd074ca7ea5b36cca420d16bf0",
    "svg": "bee43e78aa59a806927a50e1e807181c62a3f6497d75add1834de2c75fdc546b",
}
RESTORED_TARGETS = (
    (
        "adapter", "candidates/rust_candidate.py",
        "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        31151, 428100, 0o600,
    ),
    (
        "bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
        144992, 430629, 0o755,
    ),
    (
        "bridge_source", "candidates/rust/py_bridge.c",
        "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        175676, 419054, 0o600,
    ),
    (
        "engine", "candidates/_rust_engine.so",
        "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
        660440, 430563, 0o755,
    ),
)


def load_v47() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType,
]:
    path, fingerprint, size = V47["source"]
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
            raise ValueError("reject a nonprivate or substituted pushed V47")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            if not piece:
                raise ValueError("reject a truncated pushed V47 source")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended pushed V47 renderer bytes")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (
                before.st_dev, before.st_ino, before.st_size,
                before.st_nlink, before.st_mtime_ns,
            ) != (
                after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns,
            )
        ):
            raise ValueError("reject replacement during V47 authentication")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_pushed_real_rust_history_v47")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v46, v45, v44, v43, v42, v41, v40, base = previous.load_v46()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v47"
        and previous.SELF == path
        and previous.PUBLIC_STATUS == PUBLIC_STATUS
        and previous.LARGE_MATRIX_SHA256 == LARGE_MATRIX_SHA256,
        "load only the exact main-branch pushed V47 giant-input renderer",
    )
    return previous, v46, v45, v44, v43, v42, v41, v40, base


def expected_restored_targets(base: types.ModuleType) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for role, relative, fingerprint, size, inode, mode in RESTORED_TARGETS:
        base.checked(fingerprint, "exact restored original Rust " + role)
        base.need(role not in result, "reject a duplicate restored Rust target")
        result[role] = {
            "bytes": size,
            "device": DEVICE,
            "inode": inode,
            "mode": mode,
            "nlink": 1,
            "path": str(ROOT / relative),
            "relative": relative,
            "sha256": fingerprint,
            "size_bytes": size,
            "uid": os.geteuid(),
        }
    base.need(len(result) == 4, "retain all four exact restored Rust originals")
    return result


def expected_receipt_archive() -> dict:
    return {
        "device": DEVICE,
        "directory_fsync_completed": True,
        "exclusive_creation": True,
        "file_fsync_completed": True,
        "inode": ARCHIVE_INODE,
        "mode": 0o600,
        "path": str(ROOT / ARCHIVE[0]),
        "relative": Path(ARCHIVE[0]).name,
        "same_inode_readback_verified": True,
        "sha256": ARCHIVE[1],
        "size_bytes": ARCHIVE[2],
        "streaming_readback_verified": True,
        "write_calls": 20,
    }


def expected_receipt(base: types.ModuleType) -> dict:
    return {
        "schema":
            "rebar-owned-repaired-rust-original-campaign-v7-"
            "durable-publication-receipt",
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "family": "rust",
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "current_overview_version": 43,
        "published_current_v43_source_sha256": HISTORICAL_V43["source"],
        "published_current_v43_inputs_sha256": HISTORICAL_V43["inputs"],
        "published_current_v43_summary_sha256": HISTORICAL_V43["summary"],
        "published_current_v43_svg_sha256": HISTORICAL_V43["svg"],
        "campaign_source_sha256": CAMPAIGN["source"][1],
        "campaign_protocol_sha256": CAMPAIGN["protocol"][1],
        "campaign_contract_sha256": CAMPAIGN["contract"][1],
        "suite_count": 13,
        "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "completed_suite_count": 13,
        "actual_candidate_workers": 13,
        "infrastructure_failure_count": 0,
        "semantic_mismatch_count": 928,
        "verified_passing_case_count": 8965,
        "actual_worker_process_ids": list(WORKER_PROCESS_IDS),
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "restored_original_targets": expected_restored_targets(base),
        "archive": expected_receipt_archive(),
        "uncompressed_sha256":
            "86f903168ef0d7e07a07c8a4341a146313cdd9d87b4c326316e0a89744aeb41b",
        "uncompressed_bytes": 5295588,
        "uncompressed_chunk_count": 6266,
        "recovery_journal_sha256": JOURNAL_SHA256,
        "historical_evidence_owner_count_before_publication": 166,
        "historical_authenticated_reference_count_before_publication": 171,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": 168,
        "resulting_authenticated_reference_count": 173,
        "actual_v13_build_archive_sha256":
            "c201c014f55a51454baab77d2148dc39d6024bae3273242d6eb1f1b43f419f6a",
        "actual_v13_build_receipt_sha256":
            "4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805",
        "actual_v6_preflight_failure_sha256":
            "88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7",
        "actual_v6_preflight_observation_sha256":
            "51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6",
        "native_engine_sha256":
            "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
        "native_bridge_sha256":
            "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54",
        "corrected_reference_receipt_sha256":
            "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966",
        "corrected_reference_records_sha256":
            "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "corrected_reference_cache_records_sha256":
            "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "corrected_reference_process_ids": [81, 82],
        "corrected_reference_case_count": 6912,
        "candidate_run_uses_both_complete_reference_vectors": True,
        "all_original_observation_vectors_complete": True,
        "group_atomic": False,
        "power_failure_automatically_recovered": False,
        "sigkill_automatically_recovered": False,
        "v2_unsafe_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v9_c_only_runner_invoked": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "timing_trials_run": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "winner_selected": False,
    }


def validate_receipt(base: types.ModuleType, actual: object) -> None:
    base.need(type(actual) is dict, "reject missing real Rust failure receipt")
    assert isinstance(actual, dict)
    for name, value in expected_receipt(base).items():
        base.need(
            actual.get(name) == value,
            "reject substituted actual Rust failure receipt field: " + name,
        )
    worker_ids = actual["actual_worker_process_ids"]
    base.need(
        type(worker_ids) is list
        and len(worker_ids) == 13
        and len(set(worker_ids)) == 13
        and all(type(value) is int and value > 0 for value in worker_ids)
        and actual["verified_passing_case_count"]
        != actual["case_execution_denominator"] - actual["semantic_mismatch_count"],
        "authenticate all 13 real worker PIDs and never invent complement passes",
    )


def expected_archive_metadata(base: types.ModuleType) -> dict:
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


def live_archive_metadata(base: types.ModuleType) -> dict:
    observed = os.stat(str(ROOT / ARCHIVE[0]), follow_symlinks=False)
    base.need(
        stat.S_ISREG(observed.st_mode)
        and observed.st_uid == os.geteuid()
        and observed.st_dev == DEVICE
        and observed.st_ino == ARCHIVE_INODE
        and observed.st_nlink == 1
        and observed.st_size == ARCHIVE[2]
        and stat.S_IMODE(observed.st_mode) == 0o600,
        "authenticate compressed failure metadata without opening the archive",
    )
    return expected_archive_metadata(base)


def live_restored_targets(base: types.ModuleType) -> dict:
    expected = expected_restored_targets(base)
    for role, relative, _fingerprint, size, inode, mode in RESTORED_TARGETS:
        observed = os.stat(str(ROOT / relative), follow_symlinks=False)
        base.need(
            stat.S_ISREG(observed.st_mode)
            and observed.st_uid == os.geteuid()
            and observed.st_dev == DEVICE
            and observed.st_ino == inode
            and observed.st_nlink == 1
            and observed.st_size == size
            and stat.S_IMODE(observed.st_mode) == mode,
            "verify the restored original Rust inode without reading " + role,
        )
    return expected


def make_result_proof(base: types.ModuleType, receipt_owner: dict,
                      receipt: dict, archive_metadata: dict,
                      restored_targets: dict) -> dict:
    validate_receipt(base, receipt)
    base.need(
        archive_metadata == expected_archive_metadata(base)
        and restored_targets == expected_restored_targets(base),
        "preserve metadata-only archive and four restored original inodes",
    )
    proof = {
        "schema": SCHEMA + "-authenticated-actual-rust-v7-failure",
        "version": 1,
        "receipt": receipt_owner,
        "complete_durable_publication_receipt": copy.deepcopy(receipt),
        "failure_archive_metadata_only": copy.deepcopy(archive_metadata),
        "restored_original_targets_metadata_only":
            copy.deepcopy(restored_targets),
        "historical_rust_v7_source_freeze_anchor_version": 43,
        "historical_rust_v7_source_freeze_anchor_sha256":
            copy.deepcopy(HISTORICAL_V43),
        "actual_graph_predecessor_version": 47,
        "campaign_source_sha256": CAMPAIGN["source"][1],
        "campaign_protocol_sha256": CAMPAIGN["protocol"][1],
        "campaign_contract_sha256": CAMPAIGN["contract"][1],
        "journal_sha256_attested_by_receipt": JOURNAL_SHA256,
        "journal_opened_by_graph": False,
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_semantic_status": "FAIL",
        "candidate_qualified": False,
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "completed_suite_count": 13,
        "actual_candidate_workers": 13,
        "actual_worker_process_ids": list(WORKER_PROCESS_IDS),
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "infrastructure_failure_count": 0,
        "semantic_mismatch_count": 928,
        "explicitly_verified_passing_case_count": 8965,
        "passing_cases_derived_by_subtraction": False,
        "all_four_original_targets_restored": True,
        "original_target_content_read_by_graph": False,
        "actual_evidence_owner_lower_bound_before_publication": 166,
        "actual_history_reference_lower_bound_before_publication": 171,
        "new_exact_result_owner_count": 2,
        "actual_evidence_owner_lower_bound_after_publication": 168,
        "actual_history_reference_lower_bound_after_publication": 173,
        "actual_failure_archives_opened_by_graph": 0,
        "actual_failure_archives_inflated_by_graph": 0,
        "actual_reference_archives_opened_by_graph": 0,
        "actual_source_build_archives_opened_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_large_subject_allocations_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_actual_rust_v7_failure_binding_sha256"] = base.digest(
        base.canonical(proof),
    )
    validate_result_proof(base, proof)
    return proof


def validate_result_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject missing actual Rust failure proof")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-actual-rust-v7-failure",
        "version": 1,
        "historical_rust_v7_source_freeze_anchor_version": 43,
        "historical_rust_v7_source_freeze_anchor_sha256": HISTORICAL_V43,
        "actual_graph_predecessor_version": 47,
        "campaign_source_sha256": CAMPAIGN["source"][1],
        "campaign_protocol_sha256": CAMPAIGN["protocol"][1],
        "campaign_contract_sha256": CAMPAIGN["contract"][1],
        "journal_sha256_attested_by_receipt": JOURNAL_SHA256,
        "journal_opened_by_graph": False,
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_semantic_status": "FAIL",
        "candidate_qualified": False,
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "completed_suite_count": 13,
        "actual_candidate_workers": 13,
        "actual_worker_process_ids": list(WORKER_PROCESS_IDS),
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "infrastructure_failure_count": 0,
        "semantic_mismatch_count": 928,
        "explicitly_verified_passing_case_count": 8965,
        "passing_cases_derived_by_subtraction": False,
        "all_four_original_targets_restored": True,
        "original_target_content_read_by_graph": False,
        "actual_evidence_owner_lower_bound_before_publication": 166,
        "actual_history_reference_lower_bound_before_publication": 171,
        "new_exact_result_owner_count": 2,
        "actual_evidence_owner_lower_bound_after_publication": 168,
        "actual_history_reference_lower_bound_after_publication": 173,
        "actual_failure_archives_opened_by_graph": 0,
        "actual_failure_archives_inflated_by_graph": 0,
        "actual_reference_archives_opened_by_graph": 0,
        "actual_source_build_archives_opened_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_large_subject_allocations_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    for name, value in expected.items():
        base.need(
            proof.get(name) == value,
            "reject invented Rust success or source effect: " + name,
        )
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
        "bind the actual one small private durable publication receipt",
    )
    validate_receipt(base, proof.get("complete_durable_publication_receipt"))
    base.need(
        proof.get("failure_archive_metadata_only")
        == expected_archive_metadata(base)
        and proof.get("restored_original_targets_metadata_only")
        == expected_restored_targets(base),
        "retain metadata-only evidence without reading a gzip or native file",
    )
    body = {
        key: value for key, value in proof.items()
        if key != "complete_actual_rust_v7_failure_binding_sha256"
    }
    base.need(
        proof.get("complete_actual_rust_v7_failure_binding_sha256")
        == base.digest(base.canonical(body)),
        "bind the complete actual Rust failure, original inodes and real result",
    )


def authenticate_result(base: types.ModuleType,
                        options: argparse.Namespace) -> dict:
    for role, pin in CAMPAIGN.items():
        provided = getattr(options, "campaign_" + role + "_sha256")
        base.need(
            base.checked(provided, "exact V7 campaign " + role) == pin[1],
            "require the independently frozen V7 campaign " + role,
        )
    base.need(
        base.checked(options.receipt_sha256, "actual small failure receipt")
        == RECEIPT[1]
        and options.receipt_bytes == RECEIPT[2]
        and options.receipt_inode == RECEIPT_INODE
        and options.receipt_device == DEVICE
        and base.checked(options.archive_sha256, "receipt-attested archive")
        == ARCHIVE[1]
        and options.archive_bytes == ARCHIVE[2]
        and options.archive_inode == ARCHIVE_INODE
        and options.archive_device == DEVICE
        and base.checked(options.journal_sha256, "receipt-attested journal")
        == JOURNAL_SHA256,
        "bind exact failure and journal metadata without opening either archive",
    )
    raw, receipt_owner = base.read_owner(*RECEIPT, private=True)
    receipt = base.document(
        raw, "complete exact actual small Rust durable-publication receipt",
        exact=False,
    )
    archive = live_archive_metadata(base)
    restored = live_restored_targets(base)
    return make_result_proof(base, receipt_owner, receipt, archive, restored)


def authenticate_v47(previous: types.ModuleType,
                     v46: types.ModuleType, v45: types.ModuleType,
                     v44: types.ModuleType, v43: types.ModuleType,
                     v42: types.ModuleType, v41: types.ModuleType,
                     v40: types.ModuleType, base: types.ModuleType,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    raw: dict[str, bytes] = {}
    for role, pin in V47.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V47 " + role)
            == pin[1],
            "require the actually current pushed V47 graph " + role,
        )
        raw[role], _ = base.read_owner(*pin, private=True)
    old = base.document(raw["summary"], "complete pushed V47 summary")
    old_inputs = base.document(raw["inputs"], "complete pushed V47 inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(
        v46, v45, v44, v43, v42, v41, v40, base, snapshot,
    )
    old46, _old46_inputs, old46svg = previous.authenticate_v46(
        v46, v45, v44, v43, v42, v41, v40, base,
        {role: pin[1] for role, pin in previous.V46.items()},
    )
    base.need(
        old46.get("version") == 46
        and old.get("schema") ==
        "rebar-candidate-current-overview-v47-summary"
        and old.get("version") == 47
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V47["source"])
        and old.get("inputs") == base.pin(*V47["inputs"])
        and old.get("svg") == base.pin(*V47["svg"])
        and old_inputs.get("schema") ==
        "rebar-candidate-current-overview-v47-inputs"
        and old_inputs.get("version") == 47
        and old_inputs.get("renderer") == base.pin(*V47["source"])
        and raw["svg"] == previous.make_svg(
            v46, v45, v44, v43, v42, v41, v40, base,
            snapshot, old46svg, V47["source"][1], V47["inputs"][1],
        )
        and old.get("public_entrypoint_status") == PUBLIC_STATUS
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("frozen_corrected_runner_source_family_count") == 3
        and old.get("actually_runnable_candidate_family_count") == 0
        and old.get("authenticated_evidence_owner_lower_bound") == 166
        and old.get("authenticated_history_reference_lower_bound") == 171,
        "regenerate actual V47 predecessor; reject calling historical V43 current",
    )
    return old, old_inputs, raw["svg"]


def actual_current_rust_campaign(proof: dict) -> dict:
    receipt = proof["complete_durable_publication_receipt"]
    return {
        "schema":
            "rebar-candidate-current-overview-v48-authenticated-"
            "actual-rust-v7-matching-failure",
        "version": 7,
        "status": "FAIL",
        "candidate_status": "FAIL",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": "rust",
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "source": {
            "path": CAMPAIGN["source"][0],
            "sha256": CAMPAIGN["source"][1],
            "bytes": CAMPAIGN["source"][2],
        },
        "protocol": {
            "path": CAMPAIGN["protocol"][0],
            "sha256": CAMPAIGN["protocol"][1],
            "bytes": CAMPAIGN["protocol"][2],
        },
        "contract": {
            "path": CAMPAIGN["contract"][0],
            "sha256": CAMPAIGN["contract"][1],
            "bytes": CAMPAIGN["contract"][2],
        },
        "publication_receipt_owner": copy.deepcopy(proof["receipt"]),
        "publication_receipt": copy.deepcopy(receipt),
        "publication_receipt_sha256": RECEIPT[1],
        "archive": copy.deepcopy(proof["failure_archive_metadata_only"]),
        "failure_archive_opened_by_graph": False,
        "failure_archive_inflated_by_graph": False,
        "failure_archive_sha256_recomputed_by_graph": False,
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "completed_suite_count": 13,
        "actual_candidate_workers": 13,
        "actual_worker_process_ids": list(WORKER_PROCESS_IDS),
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "infrastructure_failure_count": 0,
        "semantic_mismatch_count": 928,
        "verified_passing_case_count": 8965,
        "verified_passing_cases_derived_by_subtraction": False,
        "candidate_qualified": False,
        "failure_class": "SEMANTIC MISMATCH",
        "corrected_bridge_source_sha256":
            receipt["corrected_bridge_source_sha256"],
        "corrected_public_adapter_sha256":
            receipt["corrected_public_adapter_sha256"],
        "native_engine_sha256": receipt["native_engine_sha256"],
        "native_bridge_sha256": receipt["native_bridge_sha256"],
        "recovery_journal_sha256": JOURNAL_SHA256,
        "journal_opened_by_graph": False,
        "all_four_original_targets_restored": True,
        "restored_original_targets":
            copy.deepcopy(proof["restored_original_targets_metadata_only"]),
        "original_target_content_read_by_graph": False,
        "historical_source_freeze_anchor_version": 43,
        "actual_graph_predecessor_version": 47,
        "resulting_repository_evidence_owner_lower_bound": 168,
        "resulting_authenticated_reference_lower_bound": 173,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def preserved_historical_rust_campaigns(
    base: types.ModuleType,
    v3: object,
    v4: object,
) -> dict:
    base.need(
        type(v3) is dict and type(v4) is dict,
        "preserve complete explicitly historical Rust V3 and V4 campaigns",
    )
    assert isinstance(v3, dict) and isinstance(v4, dict)
    base.need(
        v3.get("schema") ==
        "rebar-candidate-current-overview-v28-authenticated-"
        "complete-rust-matching-failure"
        and v3.get("label") == "phase2-v11-rust-dual-overlay-original-p0"
        and v3.get("status") == "FAIL"
        and v3.get("semantic_mismatch_count") == 1087
        and v3.get("verified_passing_case_count") == 7438
        and v3.get("actual_candidate_workers") == 13
        and v3.get("recovery_journal_sha256") ==
        "b28862fc1433af8c2897299cf6d64fb672f452f011c68fe887714dc09b60ea65"
        and v4.get("schema") ==
        "rebar-candidate-current-overview-v32-authenticated-"
        "complete-rust-v4-matching-failure"
        and v4.get("label") == "phase2-v12-rust-flag-original-p0"
        and v4.get("status") == "FAIL"
        and v4.get("semantic_mismatch_count") == 1036
        and v4.get("verified_passing_case_count") == 8965
        and v4.get("actual_candidate_workers") == 13
        and v4.get("recovery_journal_sha256") ==
        "726e81e5d2ee255e1f46d3029290ae9486fbd23711c9a45a691d091d088f3278",
        "never silently drop, rename as current or alter actual V3/V4 failures",
    )
    return {
        "historical_rust_v3_original_campaign": copy.deepcopy(v3),
        "historical_rust_v4_original_campaign": copy.deepcopy(v4),
        "historical_complete_rust_v3_campaign": copy.deepcopy(v3),
        "historical_complete_rust_v4_campaign": copy.deepcopy(v4),
        "actual_complete_rust_v4_campaign": copy.deepcopy(v4),
        "historical_rust_v3_original_campaign_status": "FAIL",
        "historical_rust_v3_original_campaign_semantic_mismatch_count": 1087,
        "historical_rust_v3_original_campaign_verified_passing_case_count": 7438,
        "historical_rust_v3_original_campaign_recovery_journal_sha256":
            "b28862fc1433af8c2897299cf6d64fb672f452f011c68fe887714dc09b60ea65",
        "historical_rust_v4_original_campaign_status": "FAIL",
        "historical_rust_v4_original_campaign_semantic_mismatch_count": 1036,
        "historical_rust_v4_original_campaign_verified_passing_case_count": 8965,
        "historical_rust_v4_original_campaign_recovery_journal_sha256":
            "726e81e5d2ee255e1f46d3029290ae9486fbd23711c9a45a691d091d088f3278",
        "historical_rust_v6_preflight_status": "FAIL",
        "historical_rust_v6_preflight_failure_class":
            "PRE-ACTIVATION HISTORICAL HELPER FINGERPRINT MISMATCH",
        "historical_rust_v6_preflight_failure_evidence_sha256":
            "88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7",
        "historical_rust_v6_preflight_observed_effects_sha256":
            "51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6",
        "historical_rust_v6_preflight_attempted_suite_count": 0,
        "historical_rust_v6_preflight_started_suite_count": 0,
        "historical_rust_v6_preflight_completed_suite_count": 0,
        "historical_rust_v6_preflight_candidate_workers": 0,
        "historical_rust_v6_source_build_archive_read_count": 1,
        "historical_rust_v6_source_build_archive_gzip_inflation_count": 1,
    }


def result_fields(proof: dict) -> dict:
    actual = actual_current_rust_campaign(proof)
    return {
        "actual_rust_v7_campaign_failure": copy.deepcopy(proof),
        "actual_rust_original_campaign": copy.deepcopy(actual),
        "actual_complete_rust_campaign": copy.deepcopy(actual),
        "current_complete_rust_campaign": copy.deepcopy(actual),
        "current_rust_original_campaign": copy.deepcopy(actual),
        "actual_complete_rust_v7_campaign": copy.deepcopy(actual),
        "actual_rust_campaign": copy.deepcopy(actual),
        "rust_original_campaign_status": "FAIL",
        "rust_original_campaign_semantic_mismatch_count": 928,
        "rust_original_campaign_verified_passing_case_count": 8965,
        "rust_original_campaign_candidate_worker_count": 13,
        "rust_original_campaign_case_execution_denominator": 31237,
        "rust_original_campaign_completed_suite_count": 13,
        "rust_original_campaign_infrastructure_failure_count": 0,
        "rust_original_campaign_candidate_qualified": False,
        "rust_original_campaign_all_four_original_targets_restored": True,
        "rust_original_campaign_receipt_status": "PASS",
        "rust_original_campaign_receipt_pass_means":
            "DURABLE PUBLICATION ONLY",
        "rust_original_campaign_receipt_sha256": RECEIPT[1],
        "rust_original_campaign_recovery_journal_sha256": JOURNAL_SHA256,
        "rust_recovery_journal_sha256": JOURNAL_SHA256,
        "recovery_journal_sha256": JOURNAL_SHA256,
        "actual_rust_recovery_journal_sha256": JOURNAL_SHA256,
        "actual_rust_failure_evidence_sha256": RECEIPT[1],
        "actual_rust_observed_effects_sha256": RECEIPT[1],
        "actual_rust_publication_receipt_sha256": RECEIPT[1],
        "actual_rust_failure_class": "SEMANTIC MISMATCH",
        "actual_rust_error_type": "SEMANTIC MISMATCH",
        "actual_rust_error_message":
            "928 semantic mismatches across 13 complete original suites",
        "actual_rust_controller_status": "FAIL",
        "actual_rust_attempted_suite_count": 13,
        "actual_rust_started_suite_count": 13,
        "actual_rust_completed_suite_count": 13,
        "actual_rust_candidate_workers": 13,
        "actual_rust_worker_process_ids": list(WORKER_PROCESS_IDS),
        "actual_rust_distinct_worker_process_id_count": 13,
        "actual_rust_infrastructure_failure_count": 0,
        "actual_rust_semantic_mismatch_count": 928,
        "actual_rust_verified_passing_case_count": 8965,
        "actual_rust_candidate_qualified": False,
        "rust_verified_passing_case_executions": 8965,
        "rust_v13_matching_test_status": "FAIL: 928 SEMANTIC MISMATCHES",
        "rust_v13_candidate_correctness": "FAIL",
        "rust_v13_candidate_worker_count": 13,
        "rust_v13_source_build_candidate_qualified": False,
        "candidate_matching_status": "FAIL",
        "candidate_run_under_corrected_reference": "FAIL",
        "actually_tested_corrected_candidate_families": ["rust"],
        "actually_tested_corrected_candidate_family_count": 1,
        "currently_activated_candidate_families": [],
        "currently_activated_candidate_family_count": 0,
        "currently_runnable_candidate_families": [],
        "currently_runnable_candidate_family_count": 0,
        "actual_rust_v7_campaign_source_sha256": CAMPAIGN["source"][1],
        "actual_rust_v7_campaign_protocol_sha256": CAMPAIGN["protocol"][1],
        "actual_rust_v7_campaign_contract_sha256": CAMPAIGN["contract"][1],
        "actual_rust_v7_failure_receipt_sha256": RECEIPT[1],
        "actual_rust_v7_failure_receipt_bytes": RECEIPT[2],
        "actual_rust_v7_failure_receipt_inode": RECEIPT_INODE,
        "actual_rust_v7_failure_archive_sha256_attested_by_receipt": ARCHIVE[1],
        "actual_rust_v7_failure_archive_bytes": ARCHIVE[2],
        "actual_rust_v7_failure_archive_inode": ARCHIVE_INODE,
        "actual_rust_v7_failure_archive_opened_by_graph": False,
        "actual_rust_v7_failure_archive_inflated_by_graph": False,
        "actual_rust_v7_failure_archive_sha256_recomputed_by_graph": False,
        "actual_rust_v7_recovery_journal_sha256_attested_by_receipt":
            JOURNAL_SHA256,
        "actual_rust_v7_recovery_journal_opened_by_graph": False,
        "actual_rust_v7_historical_source_freeze_anchor_version": 43,
        "actual_rust_v7_historical_source_freeze_anchor_sha256":
            copy.deepcopy(HISTORICAL_V43),
        "actual_current_graph_predecessor_version": 47,
        "actual_rust_v7_publication_status": "PASS",
        "actual_rust_v7_publication_pass_means": "DURABLE PUBLICATION ONLY",
        "actual_rust_v7_semantic_status": "FAIL",
        "actual_rust_v7_candidate_qualified": False,
        "actual_rust_v7_case_execution_denominator": 31237,
        "actual_rust_v7_suite_count": 13,
        "actual_rust_v7_attempted_suite_count": 13,
        "actual_rust_v7_started_suite_count": 13,
        "actual_rust_v7_completed_suite_count": 13,
        "actual_rust_v7_candidate_workers": 13,
        "actual_rust_v7_worker_process_ids": list(WORKER_PROCESS_IDS),
        "actual_rust_v7_distinct_worker_process_id_count": 13,
        "actual_rust_v7_infrastructure_failure_count": 0,
        "actual_rust_v7_semantic_mismatch_count": 928,
        "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
        "actual_rust_v7_passing_cases_derived_by_subtraction": False,
        "actual_rust_v7_all_four_original_targets_restored": True,
        "actual_rust_v7_original_target_content_read_by_graph": False,
        "actual_rust_v7_new_exact_result_owner_count": 2,
        "actual_rust_v7_source_build_archive_read_count_by_controller": 1,
        "actual_rust_v7_source_build_archive_reads_by_graph": 0,
        "corrected_rust_v7_candidate_matching_status": "FAIL",
        "corrected_rust_v7_actual_candidate_workers": 13,
        "corrected_rust_v7_semantic_mismatch_count": 928,
        "corrected_rust_v7_verified_passing_case_count": 8965,
        "corrected_rust_v7_current_evidence_owner_lower_bound": 168,
        "corrected_rust_v7_current_history_reference_lower_bound": 173,
        "corrected_rust_matching_status": "FAIL",
        "corrected_rust_candidate_qualified": False,
        "authenticated_evidence_owner_lower_bound": 168,
        "authenticated_history_reference_lower_bound": 173,
        "exact_whole_repository_evidence_owner_count": "NOT ESTABLISHED",
        "exact_whole_repository_reference_count": "NOT ESTABLISHED",
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_large_subject_allocations_by_graph": 0,
        "actual_host_memory_queries_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
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
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(previous: types.ModuleType,
                      v46: types.ModuleType, v45: types.ModuleType,
                      v44: types.ModuleType, v43: types.ModuleType,
                      v42: types.ModuleType, v41: types.ModuleType,
                      v40: types.ModuleType, base: types.ModuleType,
                      snapshot: object) -> None:
    base.need(type(snapshot) is dict, "reject missing actual Rust graph result")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("actual_rust_v7_campaign_failure")
    validate_result_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    updates.update(preserved_historical_rust_campaigns(
        base,
        snapshot.get("historical_rust_v3_original_campaign"),
        snapshot.get("historical_rust_v4_original_campaign"),
    ))
    for key, value in updates.items():
        base.need(
            snapshot.get(key) == value,
            "reject an invented Rust outcome or archive effect: " + key,
        )
    replaced = snapshot.get("preserved_v47_replaced_snapshot_fields")
    base.need(type(replaced) is dict, "retain all actual pushed V47 values")
    assert isinstance(replaced, dict)
    historical = copy.deepcopy(snapshot)
    historical.pop("preserved_v47_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            historical[key] = copy.deepcopy(replaced[key])
        else:
            historical.pop(key, None)
    previous.validate_snapshot(
        v46, v45, v44, v43, v42, v41, v40, base, historical,
    )
    base.need(
        set(replaced).issubset(updates)
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_matrix_sha256")
        == PUBLIC_MATRIX_SHA256
        and snapshot.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and snapshot.get("public_entrypoint_status") == PUBLIC_STATUS
        and snapshot.get("large_input_upstream_original_case_count") == 2
        and snapshot.get("large_input_upstream_original_subject_bytes")
        == 2147483648
        and snapshot.get("large_input_source_case_matrix_count") == 32
        and snapshot.get("large_input_source_case_matrix_sha256")
        == LARGE_MATRIX_SHA256
        and snapshot.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and snapshot.get("large_input_actual_candidate_search_status")
        == "NOT RUN"
        and snapshot.get("large_input_actual_candidate_subn_status")
        == "NOT RUN"
        and snapshot.get("rust_v3_original_campaign_semantic_mismatch_count")
        == 1087
        and snapshot.get("rust_v4_original_campaign_semantic_mismatch_count")
        == 1036
        and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
        and snapshot.get("c_v4_original_campaign_semantic_mismatch_count")
        == 1230
        and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count")
        == 2172
        and snapshot.get("zig_v3_original_campaign_semantic_mismatch_count")
        == 1764
        and snapshot.get("actual_rust_v7_semantic_status") == "FAIL"
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and snapshot.get("actual_rust_v7_candidate_workers") == 13
        and snapshot.get("actual_rust_original_campaign")
        == actual_current_rust_campaign(proof)
        and snapshot.get("actual_complete_rust_campaign")
        == actual_current_rust_campaign(proof)
        and snapshot.get("current_complete_rust_campaign")
        == actual_current_rust_campaign(proof)
        and snapshot.get("rust_original_campaign_semantic_mismatch_count")
        == 928
        and snapshot.get("actual_rust_semantic_mismatch_count") == 928
        and snapshot.get("actual_rust_candidate_workers") == 13
        and snapshot.get("actual_rust_worker_process_ids")
        == list(WORKER_PROCESS_IDS)
        and snapshot.get("rust_recovery_journal_sha256") == JOURNAL_SHA256
        and snapshot.get("rust_original_campaign_recovery_journal_sha256")
        == JOURNAL_SHA256
        and snapshot.get("rust_original_campaign_receipt_sha256") == RECEIPT[1]
        and snapshot.get("actually_tested_corrected_candidate_families")
        == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
        == 1
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 168
        and snapshot.get("authenticated_history_reference_lower_bound") == 173
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("actual_rust_source_build_archive_read_count") == 1
        and snapshot.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False,
        "preserve actual 928 failures, all histories and separate case matrices",
    )


def make_svg(previous: types.ModuleType,
             v46: types.ModuleType, v45: types.ModuleType,
             v44: types.ModuleType, v43: types.ModuleType,
             v42: types.ModuleType, v41: types.ModuleType,
             v40: types.ModuleType, base: types.ModuleType,
             snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(
        previous, v46, v45, v44, v43, v42, v41, v40, base, snapshot,
    )
    source_sha = base.checked(source_sha, "actual current V48 renderer footer")
    inputs_sha = base.checked(inputs_sha, "actual current V48 inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v47-title", "v48-title")
    visible = visible.replace("v47-description", "v48-description")
    replacements = (
        (
            "real 2-gigabyte tests frozen; no replacement is yet compatible "
            "or faster</title>",
            "Rust fails 928 real compatibility checks; no replacement is "
            "yet compatible or faster</title>",
            "plain-language honest real Rust semantic-failure headline",
        ),
        (
            "C, Rust and Zig have independently frozen first-party runner "
            "sources, but zero candidates are actually runnable or qualified.",
            "The actual first-party Rust replacement completed all 13 "
            "real test suites and failed 928 checks; 8,965 passing "
            "observations were explicitly verified. A PASS receipt only "
            "means this failure was durably saved. C, Rust and Zig have "
            "independent source runners, but zero candidates are currently "
            "runnable or qualified.",
            "explain actual Rust failure separately from receipt publication",
        ),
        (
            "THREE FIRST-PARTY RUNNERS PREPARED; ZERO USABLE OR "
            "QUALIFIED REPLACEMENTS",
            "ONE RUST FAMILY TESTED; THREE RUNNERS PREPARED; "
            "ZERO QUALIFIED REPLACEMENTS",
            "distinguish one genuinely tested family from zero active winners",
        ),
        (
            "C, Rust and Zig test-runner sources are frozen. No candidate, "
            "native engine or Zig compiler has been started.",
            "Rust genuinely ran and failed; C and Zig runner sources are "
            "frozen but untested. No candidate is currently activated.",
            "reject the stale claim that no Rust candidate ever started",
        ),
        (
            "Actual build: 108,985 compressed bytes → 760,477 verified "
            "bytes. Matching/reference archives: 0. Candidate workers: 0.",
            "Historical V6 build: 108,985 compressed bytes → 760,477 "
            "verified bytes. Historical V6 candidate workers: 0.",
            "mark the zero-worker build explicitly historical V6",
        ),
        (
            "One real Rust preflight failed. C remains untested; "
            "the other four remain source-only. No matching worker started.",
            "Historical V6 preflight failed; actual V7 completed 13 "
            "workers. C remains untested; no other family was rerun.",
            "remove the false implication that no real Rust worker started",
        ),
        (
            "A separately frozen V7 helper fix passes all-worker and "
            "recovery source-only tests; no V7 candidate, C, Zig, Go, C++ "
            "or Fortran has been run.",
            "The corrected V7 Rust candidate genuinely completed 13 suites "
            "and failed 928 checks; C, Zig, Go, C++ and Fortran have not "
            "been rerun.",
            "remove the inherited false claim that the actual V7 run never ran",
        ),
        (
            "The actual V6 Rust controller failed before any of 31,237 "
            "tests. The new V7 fix is source-tested only; C has not run.",
            "The historical V6 preflight failed before testing. The later "
            "V7 run completed 13 suites and failed; C remains untested.",
            "distinguish the preserved V6 preflight from actual V7 execution",
        ),
        (
            "RUST V7 ALL-WORKER AND RECOVERY FIX SOURCE-TESTED ONLY "
            "— ZERO CANDIDATE WORKERS",
            "ACTUAL RUST V7: 13 WORKERS COMPLETED; 928 MISMATCHES; "
            "CANDIDATE FAILED",
            "replace the obsolete zero-worker V7 source-freeze banner",
        ),
        (
            "All 13 real worker paths and recovery are source-tested; "
            "the actual V6 failure and its omitted build-archive read "
            "remain preserved.",
            "Thirteen distinct workers completed 13 suites; 8,965 passes "
            "are explicitly verified. V6 failure and archive history "
            "remain preserved.",
            "show actual candidate workers rather than source-test paths",
        ),
        (
            "RUST SOURCE RUNNER FAILED BEFORE ACTIVATION; ZERO "
            "CANDIDATES RUNNABLE",
            "RUST V7 EXECUTED AND FAILED; ZERO CURRENTLY RUNNABLE "
            "CANDIDATES",
            "separate genuine completed execution from live activation",
        ),
        (
            "Three frozen first-party runner sources; six source designs; "
            "zero runnable or qualified replacements. Rust matching and "
            "speed are not measured.",
            "Three first-party runner sources; Rust matching failed 928 "
            "checks. No candidate is currently runnable or qualified; "
            "speed is not measured.",
            "remove the obsolete claim that real Rust matching is unmeasured",
        ),
        (
            "C, Rust and Zig matching NOT RUN; C++, Go and Fortran "
            "runner sources NOT FROZEN.",
            "Rust matching FAIL (928); C and Zig NOT RUN; C++, Go and "
            "Fortran runner sources NOT FROZEN.",
            "show exactly which candidate actually ran and failed",
        ),
        (
            "1. Overall: three test runners; zero usable replacements",
            "1. Overall: Rust tested and failed; zero usable replacements",
            "make the actual baseline-versus-candidate result easy to read",
        ),
        (
            "Rust — actual preflight failed; historical failures preserved",
            "Rust — complete new 13-worker run failed; older results preserved",
            "show a real completed Rust matching campaign",
        ),
        (
            "PREFLIGHT FAILED; ZERO TEST WORKERS",
            "FAIL — 928 DIFFERENCES; 13 COMPLETED WORKERS",
            "distinguish actual V7 matching failure from historical V6 preflight",
        ),
        (
            "0 new workers; 1,036 and 1,087 historical differences; "
            "current result NOT MEASURED",
            "928 current differences; 8,965 explicitly verified passes; "
            "older differences: 1,036 and 1,087",
            "show exactly actual verified passes without subtraction",
        ),
        (
            "1,230 historical differences; 7,325 historical passes",
            "1,230 and 1,262 historical differences; 7,325 "
            "explicitly historical passes",
            "visibly preserve both independent historical C failures",
        ),
        (
            "≥166 / 171",
            "≥168 / 173",
            "raise authenticated lower bounds only after two real new owners",
        ),
        (
            "Two new exact failure-observation owners raise the authenticated "
            "lower bounds from 164/169 to at least 166/171.",
            "Two real Rust failure-result owners raise authenticated lower "
            "bounds from 166/171 to at least 168/173.",
            "preserve an honest evidence lower bound rather than a full census",
        ),
        (
            'height="3280" viewBox="0 0 1440 3280"',
            'height="3510" viewBox="0 0 1440 3510"',
            "make room for the completed Rust result and graph provenance",
        ),
        (
            '<rect width="1440" height="3280" rx="22"',
            '<rect width="1440" height="3510" rx="22"',
            "extend the readable background over actual source history",
        ),
    )
    for before, after, label in replacements:
        visible = v43.replace_once(base, visible, before, after, label)
    visible = v43.replace_once(
        base, visible,
        "Graph inputs SHA-256: " + V47["inputs"][1],
        "Graph inputs SHA-256: " + inputs_sha,
        "label only the exact current V48 graph-input digest",
    )
    visible = v43.replace_once(
        base, visible,
        "Graph renderer SHA-256: " + V47["source"][1],
        "Graph renderer SHA-256: " + source_sha,
        "label only the exact current V48 renderer digest",
    )
    lines = [v42.move_y(line, 170) for line in visible.splitlines()]
    insertion = next(
        index + 1 for index, line in enumerate(lines)
        if "The historical V6 preflight failed before testing." in line
    )
    lines[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="155" rx="14" '
        'fill="#fff1ed" stroke="#e6b3a6"/>',
        '<text x="65" y="335" class="warning">ACTUAL RUST RUN FAILED '
        '— 13 REAL WORKERS; 928 VERIFIED DIFFERENCES</text>',
        '<text x="67" y="362" class="body">All 13 suites ran against '
        '31,237 frozen cases. Publication PASS means the failure was '
        'saved; Rust is not qualified.</text>',
        '<rect x="68" y="377" width="1073" height="19" rx="5" '
        'fill="#268256"/>',
        '<rect x="1141" y="377" width="111" height="19" rx="5" '
        'fill="#bf5a43"/>',
        '<text x="68" y="416" class="small">8,965 explicitly verified '
        'passes</text>',
        '<text x="388" y="416" class="small">928 actual mismatches</text>',
        '<text x="693" y="416" class="small">Unreported passes are not '
        'invented by subtraction.</text>',
        '<text x="67" y="443" class="body">V43 is only the historical '
        'Rust source-freeze anchor; V47 is the actual preceding graph. '
        'All four originals are restored.</text>',
    ]
    historical = next(
        index for index, line in enumerate(lines)
        if line.startswith("<!-- Zig source correction is frozen only;")
    )
    lines[historical:historical] = [
        '<text x="47" y="3410" class="foot">Historical V47 graph '
        'inputs SHA-256: ' + V47["inputs"][1] + '</text>',
        '<text x="47" y="3432" class="foot">Historical V47 graph '
        'renderer SHA-256: ' + V47["source"][1] + '</text>',
        '<text x="47" y="3454" class="foot">Actual Rust failure '
        'receipt SHA-256: ' + RECEIPT[1] + '</text>',
        '<text x="47" y="3476" class="foot">Failure archive SHA-256 '
        '(receipt-attested; not opened): ' + ARCHIVE[1] + '</text>',
    ]
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    actual_input = ("Graph inputs SHA-256: " + inputs_sha).encode("ascii")
    actual_source = ("Graph renderer SHA-256: " + source_sha).encode("ascii")
    historical_input = (
        "Historical V47 graph inputs SHA-256: " + V47["inputs"][1]
    ).encode("ascii")
    historical_source = (
        "Historical V47 graph renderer SHA-256: " + V47["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(actual_input) == 1
        and raw.count(actual_source) == 1
        and raw.count(historical_input) == 1
        and raw.count(historical_source) == 1
        and (
            "Graph inputs SHA-256: " + V47["inputs"][1]
        ).encode("ascii") not in raw
        and (
            "Graph renderer SHA-256: " + V47["source"][1]
        ).encode("ascii") not in raw,
        "display current V48 graph footer and explicitly historical V47",
    )
    lower = raw.lower()
    for phrase in (
        b"rust fails 928 real compatibility checks",
        b"actual rust run failed",
        b"13 real workers",
        b"one rust family tested",
        b"928 verified differences",
        b"31,237 frozen cases",
        b"publication pass means the failure was saved",
        b"rust is not qualified",
        b"8,965 explicitly verified passes",
        b"928 actual mismatches",
        b"not invented by subtraction",
        b"v43 is only the historical",
        b"v47 is the actual preceding graph",
        b"all four originals are restored",
        b"1,036",
        b"1,087",
        b"1,230",
        b"1,262",
        b"1,764",
        b"2,172",
        b"168 / 173",
        b"two real 2-gigabyte python tests frozen",
        b"2,147,483,648",
        b"5,147",
        b"22 source checks pass",
        b"3 not run",
        b"17 source observations pass",
        b"7 actual public checks fail",
        b"4,194,304",
        b"not opened",
    ):
        base.need(
            phrase.lower() in lower,
            "reject missing actual Rust result or original history: "
            + repr(phrase),
        )
    for falsehood in (
        b"rust candidate passed",
        b"rust replacement qualified",
        b"30,309 verified passes",
        b"30309 verified passes",
        b"publication proves candidate correctness",
        b"v43 is the current graph",
        b"archive inflated by graph",
        b"no v7 candidate",
        b"new v7 fix is source-tested only",
        b"rust v7 all-worker and recovery fix source-tested only",
        b"rust matching and speed are not measured",
        b"c, rust and zig matching not run",
        b"no candidate, native engine or zig compiler has been started",
        b"no matching worker started",
        b"2-gigabyte candidate passes",
        b"winner selected",
    ):
        base.need(falsehood not in lower, "reject invented Rust experiment")
    base.need(
        raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
        "render exactly one final V48 SVG linefeed",
    )
    return raw


def build(previous: types.ModuleType,
          v46: types.ModuleType, v45: types.ModuleType,
          v44: types.ModuleType, v43: types.ModuleType,
          v42: types.ModuleType, v41: types.ModuleType,
          v40: types.ModuleType, base: types.ModuleType,
          options: argparse.Namespace) -> tuple[
              dict, tuple[tuple[str, bytes], ...],
          ]:
    source_sha = base.checked(options.source_sha256, "exact V48 graph source")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "require the independently supplied exact V48 source bytes",
    )
    own_raw, _ = base.read_owner(
        SELF, source_sha, options.source_bytes, private=True,
    )
    old, old_inputs, old_svg = authenticate_v47(
        previous, v46, v45, v44, v43, v42, v41, v40, base,
        {
            "source": options.previous_source_sha256,
            "inputs": options.previous_inputs_sha256,
            "summary": options.previous_summary_sha256,
            "svg": options.previous_svg_sha256,
        },
    )
    proof = authenticate_result(base, options)
    prior_snapshot = old["snapshot"]
    updates = result_fields(proof)
    updates.update(preserved_historical_rust_campaigns(
        base,
        old_inputs.get("actual_complete_rust_campaign"),
        old.get("actual_rust_original_campaign"),
    ))
    snapshot = copy.deepcopy(prior_snapshot)
    snapshot.update(updates)
    snapshot["preserved_v47_replaced_snapshot_fields"] = {
        key: copy.deepcopy(prior_snapshot[key])
        for key in updates if key in prior_snapshot
    }
    validate_snapshot(
        previous, v46, v45, v44, v43, v42, v41, v40, base, snapshot,
    )
    predecessors = {role: base.pin(*pin) for role, pin in V47.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 48,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(
        previous, v46, v45, v44, v43, v42, v41, v40, base,
        snapshot, old_svg, source_sha, base.digest(input_raw),
    )
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve Python and every independent first-party replacement",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 168,
            "authenticated_history_reference_lower_bound": 173,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            for key in list(row):
                if key.startswith("current_v4_"):
                    row["historical_v4_" + key[len("current_v4_"):]] = (
                        row.pop(key)
                    )
                elif key.startswith("current_dual_overlay_"):
                    row["historical_v3_" + key[len("current_"):]] = (
                        row.pop(key)
                    )
                elif key.startswith("current_original_campaign_"):
                    row["historical_v3_original_campaign_" +
                        key[len("current_original_campaign_"):]] = row[key]
            row.update({
                "corrected_runner_status":
                    "V7 ACTUALLY RUN; 13 COMPLETE WORKERS; "
                    "928 MISMATCHES; FAIL",
                "candidate_matching_status": "FAIL",
                "corrected_rust_matching_status": "FAIL",
                "corrected_rust_v7_candidate_matching_status": "FAIL",
                "corrected_rust_v7_actual_candidate_workers": 13,
                "actual_v7_candidate_workers": 13,
                "actual_v7_semantic_mismatch_count": 928,
                "actual_v7_explicitly_verified_passing_case_count": 8965,
                "actual_v7_infrastructure_failure_count": 0,
                "actual_v7_publication_status": "PASS",
                "actual_v7_publication_pass_means":
                    "DURABLE PUBLICATION ONLY",
                "actual_candidate_workers": 13,
                "actual_semantic_mismatch_count": 928,
                "actual_preflight_status": "PASS",
                "actual_infrastructure_failure_count": 0,
                "actual_worker_process_ids": list(WORKER_PROCESS_IDS),
                "actual_original_campaign":
                    actual_current_rust_campaign(proof),
                "current_original_campaign_status": "FAIL",
                "current_original_campaign_semantic_mismatch_count": 928,
                "current_original_campaign_verified_passing_case_count": 8965,
                "current_original_campaign_candidate_worker_count": 13,
                "current_original_campaign_infrastructure_failure_count": 0,
                "current_original_campaign_recovery_journal_sha256":
                    JOURNAL_SHA256,
                "current_original_campaign_publication_receipt_sha256":
                    RECEIPT[1],
                "candidate_run_under_corrected_reference": "FAIL",
                "candidate_case_producer_status":
                    "ACTUAL RUST V7 COMPLETE; 13 WORKERS; "
                    "928 SEMANTIC MISMATCHES; FAIL",
                "candidate_matching_block_reason":
                    "The actual Rust V7 candidate completed all 13 frozen "
                    "suites, produced 928 semantic mismatches, and was "
                    "restored. C and Zig have not been rerun.",
                "matching_block_reason":
                    "Rust V7 was actually tested and failed 928 checks. "
                    "No family is currently activated or correctness-qualified.",
                "v13_candidate_worker_count": 13,
                "v13_matching_test_status": "FAIL: 928 SEMANTIC MISMATCHES",
                "qualified": False,
                "runtime_no_delegation": "NOT ESTABLISHED",
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 48,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessors,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(
        len(input_raw) <= base.OWNER_LIMIT
        and len(summary_raw) <= base.OWNER_LIMIT
        and len(svg) <= base.OWNER_LIMIT,
        "bound each complete actual V48 output without hiding real outcomes",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_proof(base: types.ModuleType) -> dict:
    return make_result_proof(
        base,
        base.synthetic_owner(RECEIPT, RECEIPT_INODE),
        expected_receipt(base),
        expected_archive_metadata(base),
        expected_restored_targets(base),
    )


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_result_proof(base, proof)
    except (
        base.GraphError, TypeError, ValueError, KeyError,
        AttributeError, RecursionError,
    ):
        return 1
    raise base.GraphError("accepted forged Rust failure evidence: " + description)


def self_test(previous: types.ModuleType,
              v46: types.ModuleType, v45: types.ModuleType,
              v44: types.ModuleType, v43: types.ModuleType,
              v42: types.ModuleType, v41: types.ModuleType,
              v40: types.ModuleType, base: types.ModuleType) -> dict:
    history = previous.self_test(
        v46, v45, v44, v43, v42, v41, v40, base,
    )
    base.need(
        history.get("status") == "PASS"
        and history.get("rejected_hostile_control_count") == 2068
        and history.get("reference_archive_gzip_inflation_count") == 0
        and history.get("matching_archive_gzip_inflation_count") == 0
        and history.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and history.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and history.get("frozen_corrected_runner_source_family_count") == 3
        and history.get("actually_runnable_candidate_family_count") == 0,
        "retain all 2,068 immutable V47 source-only hostility controls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = synthetic_proof(base)
        for name, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[name] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, name)
        for name, value in proof["receipt"].items():
            hostile = copy.deepcopy(proof)
            hostile["receipt"][name] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "receipt-owner:" + name)
        receipt = proof["complete_durable_publication_receipt"]
        for name, value in receipt.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_durable_publication_receipt"][name] = (
                v43.forged_value(base, value)
            )
            rejected += reject_control(base, hostile, "actual-receipt:" + name)
        for name, value in proof["failure_archive_metadata_only"].items():
            hostile = copy.deepcopy(proof)
            hostile["failure_archive_metadata_only"][name] = (
                v43.forged_value(base, value)
            )
            rejected += reject_control(base, hostile, "archive-metadata:" + name)
        for role, record in proof["restored_original_targets_metadata_only"].items():
            for name, value in record.items():
                hostile = copy.deepcopy(proof)
                hostile["restored_original_targets_metadata_only"][role][name] = (
                    v43.forged_value(base, value)
                )
                rejected += reject_control(
                    base, hostile, "restored:" + role + ":" + name,
                )
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v48")),
            ("filesystem", lambda: os.open("forbidden-v48", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v48")),
            ("write", lambda: os.mkdir("forbidden-v48")),
            ("process", lambda: subprocess.run(("forbidden-v48",))),
            ("process", lambda: subprocess.Popen(("forbidden-v48",))),
            ("process", lambda: os.execv("/forbidden-v48", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically block actual V48 source-only " + kind,
                )
            else:
                raise base.GraphError("a forbidden V48 physical effect escaped")
        base.need(
            rejected >= 140,
            "reject all forged semantics, publication, archive and restorations",
        )
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 48,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v47_hostile_controls":
                history["rejected_hostile_control_count"],
            "new_v48_hostile_controls": rejected,
            "rejected_hostile_control_count":
                history["rejected_hostile_control_count"] + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_receipts_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_restored_original_files_read_by_self_test": 0,
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
            "public_entrypoint_status": PUBLIC_STATUS,
            "large_input_source_case_matrix_count": 32,
            "large_input_source_case_status_counts": copy.deepcopy(LARGE_COUNTS),
            "large_input_upstream_original_case_count": 2,
            "large_input_upstream_original_subject_bytes": 2147483648,
            "actual_rust_v7_historical_source_freeze_anchor_version": 43,
            "actual_current_graph_predecessor_version": 47,
            "actual_rust_v7_publication_status": "PASS",
            "actual_rust_v7_publication_pass_means":
                "DURABLE PUBLICATION ONLY",
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v7_distinct_worker_process_id_count": 13,
            "actual_rust_v7_infrastructure_failure_count": 0,
            "actual_rust_v7_failure_archive_opened_by_graph": False,
            "actual_rust_v7_failure_archive_inflated_by_graph": False,
            "authenticated_evidence_owner_lower_bound": 168,
            "authenticated_history_reference_lower_bound": 173,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
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
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg",
        }
        and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
        "write only the three specifically authorized new V48 graph assets",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(descriptor, remaining)
            base.need(
                type(written) is int and written > 0,
                "reject incomplete actual V48 result graph bytes",
            )
            remaining = remaining[written:]
        os.fsync(descriptor)
        observed = os.fstat(descriptor)
        base.need(
            observed.st_uid == os.geteuid()
            and observed.st_nlink == 1
            and observed.st_size == len(raw)
            and stat.S_IMODE(observed.st_mode) == 0o600,
            "publish complete privately owned V48 graph evidence",
        )
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
    base.need(confirmed == raw, "re-authenticate complete V48 graph output")


def result(base: types.ModuleType, snapshot: dict,
           outputs: dict[str, bytes], source_sha: str,
           *, written: bool, suffix: str) -> dict:
    fields = (
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
        "actual_rust_v7_campaign_source_sha256",
        "actual_rust_v7_campaign_protocol_sha256",
        "actual_rust_v7_campaign_contract_sha256",
        "actual_rust_original_campaign",
        "actual_complete_rust_campaign",
        "current_complete_rust_campaign",
        "current_rust_original_campaign",
        "actual_complete_rust_v7_campaign",
        "actual_rust_campaign",
        "historical_rust_v3_original_campaign",
        "historical_rust_v4_original_campaign",
        "historical_complete_rust_v3_campaign",
        "historical_complete_rust_v4_campaign",
        "historical_rust_v3_original_campaign_semantic_mismatch_count",
        "historical_rust_v4_original_campaign_semantic_mismatch_count",
        "historical_rust_v6_preflight_status",
        "historical_rust_v6_preflight_failure_evidence_sha256",
        "rust_original_campaign_status",
        "rust_original_campaign_semantic_mismatch_count",
        "rust_original_campaign_verified_passing_case_count",
        "rust_original_campaign_candidate_worker_count",
        "rust_original_campaign_receipt_sha256",
        "rust_original_campaign_recovery_journal_sha256",
        "rust_recovery_journal_sha256",
        "actual_rust_recovery_journal_sha256",
        "actual_rust_failure_evidence_sha256",
        "actual_rust_publication_receipt_sha256",
        "actual_rust_attempted_suite_count",
        "actual_rust_started_suite_count",
        "actual_rust_completed_suite_count",
        "actual_rust_candidate_workers",
        "actual_rust_worker_process_ids",
        "actual_rust_infrastructure_failure_count",
        "actual_rust_semantic_mismatch_count",
        "actual_rust_verified_passing_case_count",
        "actual_rust_candidate_qualified",
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
        "actual_rust_v7_publication_status",
        "actual_rust_v7_publication_pass_means",
        "actual_rust_v7_semantic_status",
        "actual_rust_v7_candidate_qualified",
        "actual_rust_v7_case_execution_denominator",
        "actual_rust_v7_suite_count",
        "actual_rust_v7_attempted_suite_count",
        "actual_rust_v7_started_suite_count",
        "actual_rust_v7_completed_suite_count",
        "actual_rust_v7_candidate_workers",
        "actual_rust_v7_worker_process_ids",
        "actual_rust_v7_distinct_worker_process_id_count",
        "actual_rust_v7_infrastructure_failure_count",
        "actual_rust_v7_semantic_mismatch_count",
        "actual_rust_v7_explicitly_verified_passing_case_count",
        "actual_rust_v7_passing_cases_derived_by_subtraction",
        "actual_rust_v7_all_four_original_targets_restored",
        "actual_rust_v7_original_target_content_read_by_graph",
        "actual_rust_v7_new_exact_result_owner_count",
        "actual_rust_v7_source_build_archive_read_count_by_controller",
        "actual_rust_v7_source_build_archive_reads_by_graph",
        "corrected_rust_v7_candidate_matching_status",
        "corrected_rust_v7_actual_candidate_workers",
        "corrected_rust_v7_semantic_mismatch_count",
        "corrected_rust_v7_verified_passing_case_count",
        "corrected_rust_v7_current_evidence_owner_lower_bound",
        "corrected_rust_v7_current_history_reference_lower_bound",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
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
        "hidden_cases_read", "timing_trials_run",
        "runtime_no_delegation", "performance", "memory",
        "confidence_intervals", "undefined_behavior",
        "final_comparison_planned_case_count",
        "final_comparison_cases_generated", "final_holdout_opened",
        "winner_selected",
    )
    return {
        "schema": SCHEMA + suffix,
        "version": 48,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 47,
        **{
            "previous_overview_" + role + "_sha256": pin[1]
            for role, pin in V47.items()
        },
        "outputs_written": written,
        **{key: copy.deepcopy(snapshot[key]) for key in fields},
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--previous-source-sha256")
    parser.add_argument("--previous-inputs-sha256")
    parser.add_argument("--previous-summary-sha256")
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--campaign-source-sha256")
    parser.add_argument("--campaign-protocol-sha256")
    parser.add_argument("--campaign-contract-sha256")
    parser.add_argument("--receipt-sha256")
    parser.add_argument("--receipt-bytes", type=int)
    parser.add_argument("--receipt-inode", type=int)
    parser.add_argument("--receipt-device", type=int)
    parser.add_argument("--archive-sha256")
    parser.add_argument("--archive-bytes", type=int)
    parser.add_argument("--archive-inode", type=int)
    parser.add_argument("--archive-device", type=int)
    parser.add_argument("--journal-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v46, v45, v44, v43, v42, v41, v40, base = load_v47()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256", "source_bytes",
                        "previous_source_sha256", "previous_inputs_sha256",
                        "previous_summary_sha256", "previous_svg_sha256",
                        "campaign_source_sha256", "campaign_protocol_sha256",
                        "campaign_contract_sha256", "receipt_sha256",
                        "receipt_bytes", "receipt_inode", "receipt_device",
                        "archive_sha256", "archive_bytes", "archive_inode",
                        "archive_device", "journal_sha256",
                        "inputs_sha256", "summary_sha256", "svg_sha256",
                    )
                ),
                "synthetic-only V48 self-test cannot accept real owner pins",
            )
            sys.stdout.buffer.write(base.canonical(self_test(
                previous, v46, v45, v44, v43, v42, v41, v40, base,
            )))
            return 0
        snapshot, pairs = build(
            previous, v46, v45, v44, v43, v42, v41, v40, base, options,
        )
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256, "exact V48 source")
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "publish only the three authorized fresh actual V48 graph files",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact actual Rust V48 graph inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact actual Rust V48 graph summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact accessible actual Rust V48 graph",
            ),
        }
        for path, fingerprint in expected.items():
            raw, _ = base.read_owner(
                path, fingerprint, len(outputs[path]), private=True,
            )
            base.need(
                raw == outputs[path],
                "reproduce every actual failed-Rust V48 graph output byte",
            )
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source_sha,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError,
    ) as error:
        sys.stderr.write("current V48 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V48 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
