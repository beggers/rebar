#!/usr/bin/env python3
"""Show the real fully executed Rust failure without opening its report."""

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
SELF = "tools/render_candidate_current_overview_v58.py"
OUTPUT = "docs/evidence/candidate-current-overview-v58"
SCHEMA = "rebar-candidate-current-overview-v58"
V57 = {
    "source": ("tools/render_candidate_current_overview_v57.py",
               "40ff10a3b34ef9a82b9680def680328556713b2f755c5e25cf7a77e401f3d8a7",
               85869),
    "inputs": ("docs/evidence/candidate-current-overview-v57.inputs.json",
               "3ffcb566a674178e055fc17d2811254967780c4160bdd99eb226ebe97d38a69e",
               703030),
    "summary": ("docs/evidence/candidate-current-overview-v57.json",
                "a54b936503ea8524f4cdd7d6c2ef37ef9c7042cec114267e4e1ec0da60ed8b30",
                1953999),
    "svg": ("docs/evidence/candidate-current-overview-v57.svg",
            "ff884fccc3da9ace71f12cb7a4a09313fffd4b1b421cd71394ff71b0a17ca038",
            14268),
}


RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-"
    "shape-pickle-original-p0-v10-failures-publication-receipt.json",
    "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2",
    6708,
)
FORENSIC = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-"
    "shape-pickle-original-p0-v10-failures-forensic-summary.json",
    "6e04771a48b4a460ad58ac9795ef91a697a33fa0aeae4671c9b3c9b35e4820cd",
    24701,
)
DEVICE = 2064
RECEIPT_INODE = 525044
FORENSIC_INODE = 525045
ARCHIVE_SHA = "4be5a40ca3cdb0323eeb613a80c8eb22509dcbc21423156abbf0961fef19405e"
ARCHIVE_UNCOMPRESSED_SHA = (
    "9e077ed42b0d092d0a53a640561a32ce4e4ab15d53ac2fa5c22d19c2664d4893"
)
RUNNER_SOURCE = "038870e88e9dfbe2f9d97892fb98558787d1142bb94559e3060023c8e562a81c"
RUNNER_PROTOCOL = "cf425c2517f7fa066a30a340b830d8782e0000872efa3eaf00c764ce45ef0659"
RUNNER_CONTRACT = "57c36f414d052e798fc1f9ccfcd10aeddd5f6571d95679a995c6935d86f3dda7"
BUILD_ARCHIVE_SHA = "c24c0e1544003b231bac3e45601faabfd1c1e5c181d89fce7d660a2df4a29270"
PUSHED_HEAD = "070b6eb7ab8ae42d995ccd2f9aa39862dabde993"

PUBLIC_COUNTS = {"PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
                 "NOT ESTABLISHED": 1, "NOT OPENED": 1}
LARGE_COUNTS = {"PASS": 22, "FAIL": 1, "NOT RUN": 3,
                "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1}
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]


def load_v57() -> tuple:
    path, fingerprint, size = V57["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(handle)
        if (not stat.S_ISREG(before.st_mode)
                or before.st_uid != os.geteuid()
                or before.st_nlink != 1
                or stat.S_IMODE(before.st_mode) != 0o600
                or before.st_size != size):
            raise ValueError("reject substituted pushed V57 graph renderer")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated pushed V57 graph renderer")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended pushed V57 graph renderer")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed pushed V57 graph renderer")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_actual_pushed_source_graph_v57")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v56()
    base = prior_modules[-1]
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v57"
              and previous.SELF == path
              and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
              and previous.LARGE_COUNTS == LARGE_COUNTS,
              "authenticate only the exact actually pushed V57 graph source")
    return previous, prior_modules, base





def validate_owner(base: types.ModuleType, owner: object,
                   item: tuple[str, str, int], inode: int,
                   description: str) -> None:
    base.need(
        type(owner) is dict
        and owner.get("path") == item[0]
        and owner.get("sha256") == item[1]
        and owner.get("bytes") == item[2]
        and owner.get("device") == DEVICE
        and owner.get("inode") == inode
        and owner.get("mode") == "0600"
        and owner.get("nlink") == 1
        and owner.get("uid") == os.geteuid(),
        "authenticate only a released bounded plaintext " + description,
    )





def v57_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V57["source"][1],
        source_bytes=V57["source"][2],
        previous_source_sha256=previous.V56["source"][1],
        previous_inputs_sha256=previous.V56["inputs"][1],
        previous_summary_sha256=previous.V56["summary"][1],
        previous_svg_sha256=previous.V56["svg"][1],
        runner_source_sha256=previous.V10["source"][1],
        runner_source_bytes=previous.V10["source"][2],
        runner_protocol_sha256=previous.V10["protocol"][1],
        runner_protocol_bytes=previous.V10["protocol"][2],
        runner_contract_sha256=previous.V10["contract"][1],
        runner_contract_bytes=previous.V10["contract"][2],
    )

def authenticate_v57(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V57.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V57 " + role)
            == item[1],
            "reject substituted actually pushed V57 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete actual pushed V57 summary")
    inputs = base.document(raw["inputs"], "complete actual pushed V57 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(
        prior_modules, v57_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v57-summary"
        and old.get("version") == 57
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V57["source"])
        and old.get("inputs") == base.pin(*V57["inputs"])
        and old.get("svg") == base.pin(*V57["svg"])
        and inputs.get("schema") ==
            "rebar-candidate-current-overview-v57-inputs"
        and inputs.get("version") == 57
        and inputs.get("renderer") == base.pin(*V57["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V57["inputs"][0]]
        and raw["summary"] == expected[V57["summary"][0]]
        and raw["svg"] == expected[V57["svg"][0]]
        and old.get("authenticated_evidence_owner_lower_bound") == 194
        and old.get("authenticated_history_reference_lower_bound") == 199
        and old.get("actual_rust_v16_build_status") == "PASS"
        and old.get("actual_rust_v16_compiler_process_count") == 28
        and old.get("actual_rust_v8_controller_status") == "FAIL"
        and old.get("actual_rust_v8_matching_status") == "NOT RUN"
        and old.get("actual_rust_v8_candidate_workers") == 0
        and old.get("actual_rust_v8_build_archive_reads_by_controller") == 1
        and old.get("actual_rust_v9_controller_status") == "FAIL"
        and old.get("actual_rust_v9_matching_status") == "NOT RUN"
        and old.get("actual_rust_v9_candidate_workers") == 0
        and old.get("actual_rust_v9_attempted_suite_count") == 0
        and old.get("actual_rust_v9_started_suite_count") == 0
        and old.get("actual_rust_v9_completed_suite_count") == 0
        and old.get("actual_rust_v9_fully_observed_suite_count") == 0
        and old.get("actual_rust_v9_recorded_original_inner_exception")
        == "accept only one exact owner-only Rust campaign root"
        and old.get(
            "actual_rust_v9_recorded_original_inner_exception_placeholder_count"
        ) == 13
        and old.get("actual_rust_v9_synthetic_failed_worker_placeholder_count")
        == 13
        and old.get("actual_rust_v9_synthetic_placeholders_are_observed_workers")
        is False
        and old.get("actual_rust_v9_placeholder_worker_flags_are_real_attempts")
        is False
        and old.get("actual_rust_v9_recovery_roots_created") == 1
        and old.get("actual_rust_v9_recovery_journals_created") == 0
        and old.get("actual_rust_v9_original_targets_restored_by_recovery")
        is False
        and old.get("actual_rust_v9_build_archive_reads_by_controller") == 1
        and old.get("actual_rust_v9_build_archive_inflations_by_controller")
        == 1
        and old.get("actual_rust_v9_build_archive_read_by_graph") is False
        and old.get("rust_original_campaign_v10_source_freeze_status")
        == "SOURCE FROZEN; NOT RUN"
        and old.get("rust_original_campaign_v10_matching_status") == "NOT RUN"
        and old.get("rust_original_campaign_v10_candidate_workers_started") == 0
        and old.get("rust_original_campaign_v10_source_owner_count") == 3
        and old.get("actual_rust_v7_semantic_status") == "FAIL"
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("qualified_candidate_count") == 0
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce actual pushed V57 and genuine V8/V9 results without archives",
    )
    return old, inputs, raw["svg"]


def attested_archive_expectations() -> dict:
    relative = (
        "repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-"
        "shape-pickle-original-p0-v10-failures.json.gz"
    )
    return {
        "device": DEVICE, "directory_fsync_completed": True,
        "exclusive_creation": True, "file_fsync_completed": True,
        "inode": 525043, "mode": 0o600,
        "path": str(ROOT / "oracle/phase2/evidence" / relative),
        "relative": relative, "same_inode_readback_verified": True,
        "sha256": ARCHIVE_SHA, "size_bytes": 3746528,
        "streaming_readback_verified": True, "write_calls": 20,
    }


def restored_target_expectations() -> dict:
    rows = (
        ("adapter", "candidates/rust_candidate.py", 31151, 428100, 0o600,
         "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"),
        ("bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
         144992, 430629, 0o755,
         "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15"),
        ("bridge_source", "candidates/rust/py_bridge.c", 175676, 419054,
         0o600,
         "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b"),
        ("engine", "candidates/_rust_engine.so", 660440, 430563, 0o755,
         "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4"),
    )
    return {
        role: {
            "bytes": size, "device": DEVICE, "inode": inode, "mode": mode,
            "nlink": 1, "path": str(ROOT / relative), "relative": relative,
            "sha256": fingerprint, "size_bytes": size, "uid": os.geteuid(),
        }
        for role, relative, size, inode, mode, fingerprint in rows
    }


def receipt_expectations() -> dict:
    return {
        "actual_candidate_workers": 13,
        "actual_v16_build_archive_gzip_inflation_count": 1,
        "actual_v16_build_archive_read_count": 1,
        "actual_v16_build_archive_sha256": BUILD_ARCHIVE_SHA,
        "actual_v16_build_contract_sha256":
            "4f82f88da3329c6bacac2092af19d915d379f90101dcd9840366274355cc92b7",
        "actual_v16_build_private_root":
            "/tmp/rebar-phase2-native-build-v9-rust-4l03jkq2",
        "actual_v16_build_private_root_device": 2049,
        "actual_v16_build_private_root_inode": 11673028,
        "actual_v16_build_protocol_sha256":
            "315f0a24e64b50804565f86c6ca4187024c4a1db5a23ab2f57c8805ed37f51f5",
        "actual_v16_build_receipt_sha256":
            "c893812a1796cce056de5e2feff2289df34ff816158685730205996549e338cb",
        "actual_v16_build_source_sha256":
            "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a",
        "actual_v16_compiler_process_count": 28,
        "actual_worker_process_ids": copy.deepcopy(WORKERS),
        "all_four_original_targets_restored": True,
        "all_original_observation_vectors_complete": True,
        "archive": attested_archive_expectations(),
        "attempted_suite_count": 13, "benchmark_files_read": 0,
        "campaign_contract_sha256": RUNNER_CONTRACT,
        "campaign_protocol_sha256": RUNNER_PROTOCOL,
        "campaign_source_sha256": RUNNER_SOURCE,
        "candidate_qualified": False,
        "candidate_run_uses_both_complete_reference_vectors": True,
        "candidate_status": "FAIL", "case_execution_denominator": 31237,
        "clock_samples": 0,
        "combined_bridge_source_bytes": 181004,
        "combined_bridge_source_sha256":
            "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335",
        "completed_suite_count": 13,
        "corrected_public_adapter_bytes": 31934,
        "corrected_public_adapter_sha256":
            "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e",
        "corrected_reference_cache_records_sha256":
            "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "corrected_reference_case_count": 6912,
        "corrected_reference_process_ids": [81, 82],
        "corrected_reference_receipt_sha256":
            "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966",
        "corrected_reference_records_sha256":
            "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "current_overview_version": 56,
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0, "family": "rust",
        "group_atomic": False, "hidden_cases_read": 0,
        "historical_authenticated_reference_count_before_publication": 199,
        "historical_evidence_owner_count_before_publication": 194,
        "holdout": "NOT OPENED", "infrastructure_failure_count": 0,
        "label": "phase2-v16-rust-buffer-shape-pickle-original-p0-v10",
        "memory": "NOT MEASURED", "missing_worker_process_id_count": 0,
        "named_private_waiver_count": 13,
        "native_bridge_bytes": 148832,
        "native_bridge_sha256":
            "324b811bfb3567d7f530d0a316a337897f84529defe83544e31ae34407b83e04",
        "native_engine_bytes": 658344,
        "native_engine_sha256":
            "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
        "new_repository_evidence_owner_count": 2,
        "original_v4_producer_contract_sha256":
            "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
        "original_v4_producer_protocol_sha256":
            "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
        "original_v4_producer_source_sha256":
            "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        "original_v4_producer_version": 4,
        "performance": "NOT MEASURED",
        "power_failure_automatically_recovered": False,
        "preserved_previous_rust_semantic_mismatch_count": 928,
        "preserved_previous_rust_verified_passing_case_count": 8965,
        "public_recovery_root":
            "/tmp/rebar-phase2-repaired-rust-original-campaign-v10-"
            "phase2-v16-rust-buffer-shape-pickle-original-p0",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "publication_status": "PASS",
        "published_current_v56_inputs_sha256":
            "63446b32a01b2a731ed8f6ddf4ffbb7077fa1bc1ede3ad081012ba7a0611b554",
        "published_current_v56_source_sha256":
            "991dee73be4c847eab8ebeaf27e04992d38310e8b0bcb97b4a6405ccc149b8a2",
        "published_current_v56_summary_sha256":
            "cceb572a6daf4683fd01bd758cbc4206b2dfc5b5eb8f5c45bd2de07b9934c1fe",
        "published_current_v56_svg_sha256":
            "7ea80defb808389c1b00f58731e0b74b3958c72e2814368d94b9ef44e6a1a5b1",
        "recovery_journal_sha256":
            "2de6ab4aa443fe528c52c4c71d1b688c908b8c8e80eaf4adb2d196d6757c32ef",
        "restoration_verified_before_publication": True,
        "restored_original_targets": restored_target_expectations(),
        "resulting_authenticated_reference_count": 201,
        "resulting_repository_evidence_owner_count": 196,
        "schema":
            "rebar-owned-repaired-rust-original-campaign-v10-"
            "durable-publication-receipt",
        "semantic_mismatch_count": 1440,
        "sigkill_automatically_recovered": False,
        "started_suite_count": 13, "status": "PASS", "suite_count": 13,
        "timing_trials_run": 0, "uncompressed_bytes": 5385134,
        "uncompressed_chunk_count": 4647,
        "uncompressed_sha256": ARCHIVE_UNCOMPRESSED_SHA,
        "undefined_behavior": "NOT MEASURED",
        "verified_passing_case_count": 14853, "winner_selected": False,
    }



FORENSIC_EXPECTATIONS = {
    "schema": "rebar-owned-repaired-rust-original-campaign-v10-failures-forensic-summary-v1",
    "version": 1,
    "status": "PASS",
    "analysis_status": "PASS",
    "analysis_pass_means": "INDEPENDENT AUTHENTICATION OF A FAILED CANDIDATE ONLY; NOT A PASSING CANDIDATE",
    "family": "rust",
    "label": "phase2-v16-rust-buffer-shape-pickle-original-p0-v10",
    "candidate_status": "FAIL",
    "candidate_qualified": False,
    "frozen_runner": {
        "source": {
            "path": "tools/run_owned_repaired_rust_original_campaign_v10.py",
            "sha256": "038870e88e9dfbe2f9d97892fb98558787d1142bb94559e3060023c8e562a81c",
            "bytes": 211733,
        },
        "protocol": {
            "path": "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V10.md",
            "sha256": "cf425c2517f7fa066a30a340b830d8782e0000872efa3eaf00c764ce45ef0659",
            "bytes": 16618,
        },
        "contract": {
            "path": "oracle/phase2/repaired-rust-original-campaign-v10.json",
            "sha256": "57c36f414d052e798fc1f9ccfcd10aeddd5f6571d95679a995c6935d86f3dda7",
            "bytes": 17426,
        },
        "authenticated_graph_version": 56,
    },
    "failure_archive": {
        "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures.json.gz",
        "sha256": "4be5a40ca3cdb0323eeb613a80c8eb22509dcbc21423156abbf0961fef19405e",
        "bytes": 3746528,
        "device": 2064,
        "inode": 525043,
        "mode": "0600",
        "nlink": 1,
        "uncompressed_sha256": "9e077ed42b0d092d0a53a640561a32ce4e4ab15d53ac2fa5c22d19c2664d4893",
        "uncompressed_bytes": 5385134,
        "independent_forensic_archive_open_count": 1,
        "independent_forensic_archive_inflation_count": 1,
        "compressed_hash_authenticated_in_the_same_open": True,
        "all_13_embedded_worker_stdout_streams_authenticated": True,
        "all_13_embedded_original_observation_streams_authenticated": True,
        "any_other_archive_opened": False,
    },
    "durable_publication_receipt": {
        "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-publication-receipt.json",
        "sha256": "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2",
        "bytes": 6708,
        "device": 2064,
        "inode": 525044,
        "mode": "0600",
        "nlink": 1,
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL",
    },
    "frozen_original_v4_producer": {
        "version": 4,
        "source_sha256": "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        "protocol_sha256": "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
        "contract_sha256": "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
        "reference_records_sha256": "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "reference_cache_records_sha256": "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "reference_process_ids": [
            81,
            82,
        ],
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "new_or_withdrawn_private_waiver_count": 0,
    },
    "suite_results": [
        {
            "suite": "original_bounded_v5",
            "case_execution_denominator": 151,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 151,
            "failure_class": "PASS",
            "actual_worker_process_id": 81,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 152,
            "debug_build_skip_count": 1,
            "reference_records_sha256": "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276",
            "complete_original_observation_sha256": "2362b2425b556c9fd8994e26b11e573bcabd5774d848e709be59d5813cca3f0e",
        },
        {
            "suite": "public_v3",
            "case_execution_denominator": 864,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 864,
            "failure_class": "PASS",
            "actual_worker_process_id": 87,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 864,
            "reference_records_sha256": "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
            "complete_original_observation_sha256": "3d2dfe7c7839b97bcdfba8ca7f14fed5693796155b2cfc70280a95426d0bf017",
        },
        {
            "suite": "scanner_v3",
            "case_execution_denominator": 1024,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 1024,
            "failure_class": "PASS",
            "actual_worker_process_id": 88,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 1024,
            "reference_records_sha256": "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
            "complete_original_observation_sha256": "29f6dd8a0374e4678d6afdc82e9830cc5e670b5de33279229c9cdd2d640f61d8",
        },
        {
            "suite": "buffer_v3",
            "case_execution_denominator": 768,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 768,
            "failure_class": "PASS",
            "actual_worker_process_id": 89,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 768,
            "reference_records_sha256": "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
            "complete_original_observation_sha256": "3e5eb6aa9468cfbb1f108aa301d62463c5c46ff6e70d7f171e3e2bba875c6c64",
        },
        {
            "suite": "managed_v1",
            "case_execution_denominator": 1024,
            "semantic_mismatch_count": 16,
            "explicitly_verified_passing_case_count": 0,
            "failure_class": "SEMANTIC MISMATCH",
            "actual_worker_process_id": 90,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 1024,
            "reference_records_sha256": "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
            "complete_original_observation_sha256": "7fa929d3a5bc86b57551d7a3b2d5a2e09b68b9c78abb2990b6f8be08bb4f92e9",
        },
        {
            "suite": "scanner_verbose_v1",
            "case_execution_denominator": 2854,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 2854,
            "failure_class": "PASS",
            "actual_worker_process_id": 91,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 2854,
            "reference_records_sha256": "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
            "complete_original_observation_sha256": "6cf713c798b38b37b6952091031e3a0a16b07d57c0e4a72c3c90b92ee31e232b",
        },
        {
            "suite": "public_types_v1",
            "case_execution_denominator": 6912,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 6912,
            "failure_class": "PASS",
            "actual_worker_process_id": 92,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 6912,
            "reference_records_sha256": "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
            "complete_original_observation_sha256": "0d2a072f778559e34ed721c2b39773b5f72943be7698ffb286fcb1868f180a32",
        },
        {
            "suite": "substitution_v2",
            "case_execution_denominator": 5120,
            "semantic_mismatch_count": 368,
            "explicitly_verified_passing_case_count": 0,
            "failure_class": "SEMANTIC MISMATCH",
            "actual_worker_process_id": 93,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 5120,
            "reference_records_sha256": "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
            "complete_original_observation_sha256": "20a175a2ff4e3303f22535cfd3d5b63642deda1957ba27f6599da7f12e58a737",
        },
        {
            "suite": "shape_v2",
            "case_execution_denominator": 10240,
            "semantic_mismatch_count": 1056,
            "explicitly_verified_passing_case_count": 0,
            "failure_class": "SEMANTIC MISMATCH",
            "actual_worker_process_id": 94,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 10240,
            "reference_records_sha256": "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
            "complete_original_observation_sha256": "25e4359d03f4af1759d558b2ce9731ea6fab120427d44c3ee408aebb7fbb0ab8",
        },
        {
            "suite": "public_surface_v19",
            "case_execution_denominator": 1376,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 1376,
            "failure_class": "PASS",
            "actual_worker_process_id": 95,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 1376,
            "reference_records_sha256": "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
            "complete_original_observation_sha256": "d3241f96436f0c3663a47236900b5b5d172e89f5605f5069cc6ac08ae6ab9a08",
        },
        {
            "suite": "subinterpreter_v2",
            "case_execution_denominator": 128,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 128,
            "failure_class": "PASS",
            "actual_worker_process_id": 196,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 128,
            "reference_records_sha256": "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
            "complete_original_observation_sha256": "1fbaffcf7c2f4759a3b36646a1e00421c048bd7dec097c48b05960ca75f38266",
        },
        {
            "suite": "pep688_v4",
            "case_execution_denominator": 264,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 264,
            "failure_class": "PASS",
            "actual_worker_process_id": 197,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 264,
            "reference_records_sha256": "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8",
            "complete_original_observation_sha256": "005156dd7f52ae471ba86d5ec379d3a5e69a83a1675821ff05ba1f85950ae65f",
        },
        {
            "suite": "threaded_pattern_v1",
            "case_execution_denominator": 512,
            "semantic_mismatch_count": 0,
            "explicitly_verified_passing_case_count": 512,
            "failure_class": "PASS",
            "actual_worker_process_id": 198,
            "actual_worker_started": True,
            "fully_observed": True,
            "candidate_record_count": 512,
            "reference_records_sha256": "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81",
            "complete_original_observation_sha256": "fce2d433447c8a4615989fdd6ad0395d1d243699497025f8d2dfd806b4f8ca90",
        },
    ],
    "actual_result_totals": {
        "suite_count": 13,
        "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "completed_suite_count": 13,
        "actual_candidate_workers": 13,
        "actual_worker_process_ids": [
            81,
            87,
            88,
            89,
            90,
            91,
            92,
            93,
            94,
            95,
            196,
            197,
            198,
        ],
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "all_original_observation_vectors_complete": True,
        "missing_original_case_observations": 0,
        "semantic_mismatch_count": 1440,
        "verified_passing_case_count": 14853,
        "verified_passing_cases_derived_by_subtraction": False,
        "records_from_fully_observed_failed_suites_are_counted_as_passing": False,
        "infrastructure_failure_count": 0,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
    },
    "historical_comparison": {
        "previous_actual_rust_semantic_mismatch_count": 928,
        "previous_actual_rust_explicitly_verified_passing_case_count": 8965,
        "new_actual_rust_semantic_mismatch_count": 1440,
        "new_actual_rust_explicitly_verified_passing_case_count": 14853,
        "semantic_mismatch_regression": 512,
        "per_suite_regression": [
            {
                "suite": "managed_v1",
                "previous_mismatches": 0,
                "current_mismatches": 16,
                "difference": 16,
            },
            {
                "suite": "public_types_v1",
                "previous_mismatches": 32,
                "current_mismatches": 0,
                "difference": -32,
            },
            {
                "suite": "substitution_v2",
                "previous_mismatches": 224,
                "current_mismatches": 368,
                "difference": 144,
            },
            {
                "suite": "shape_v2",
                "previous_mismatches": 672,
                "current_mismatches": 1056,
                "difference": 384,
            },
        ],
        "regression_derived_from_complete_mismatch_vectors": True,
        "passing_cases_derived_by_subtraction": False,
    },
    "first_party_semantic_root_cause": {
        "source_path": "candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c",
        "source_sha256": "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335",
        "source_bytes": 181004,
        "function": "rust_substitute_core",
        "function_line": 3546,
        "first_subject_open_line": 3558,
        "premature_snapshot_line": 3566,
        "premature_original_subject_release_line": 3573,
        "snapshot_subject_reopen_line": 3574,
        "failure_interval": "3557-3579",
        "summary": "A noncallback exporting subject is acquired once, immediately copied into a bytes snapshot, released and reopened as bytes. The first-party engine then substitutes against the snapshot instead of maintaining CPython's real exporter acquire/release lifetime and nested outer/inner event order.",
        "affected_genuine_suite_mismatches": {
            "managed_v1": 16,
            "substitution_v2": 368,
            "shape_v2": 1056,
        },
        "observed_high_frequency_difference_paths": [
            {
                "suite": "shape_v2",
                "path": "outcome.events[3].role",
                "mismatch_record_count": 1024,
            },
            {
                "suite": "shape_v2",
                "path": "outcome.events[3].nested_hex",
                "mismatch_record_count": 896,
            },
            {
                "suite": "shape_v2",
                "path": "outcome.events[4].role",
                "mismatch_record_count": 768,
            },
            {
                "suite": "shape_v2",
                "path": "outcome.events.length",
                "mismatch_record_count": 736,
            },
            {
                "suite": "substitution_v2",
                "path": "outcome.events.length",
                "mismatch_record_count": 272,
            },
            {
                "suite": "substitution_v2",
                "path": "outcome.events[3].backing_after_hex",
                "mismatch_record_count": 240,
            },
        ],
        "recommended_next_independent_source_chunk": "Freeze a new append-only first-party bridge variant that preserves the real exporting subject through substitution, reproduces CPython's per-match reentrant acquire/release and nested subject/replacement order, and independently tests normal, callback, error, zero-length and shape-changing exporter cleanup without changing the frozen original oracle.",
    },
    "earliest_genuine_mismatch_witnesses": [
        {
            "suite": "managed_v1",
            "case": "managed-buffer-lifetime.v1.0453",
            "group": "pep688-subject-acquire-release",
            "stage": "sub",
            "backing_hex": "616c706861343220626574613720213463623765376166",
            "expected_events_complete": True,
            "actual_events_complete": True,
            "expected_events": [
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 0,
                    "active_after": 1,
                    "flags": 0,
                    "backing_before_hex": "616c706861343220626574613720213463623765376166",
                    "backing_after_hex": "616c706861343220626574613720213463623765376166",
                },
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 2,
                    "flags": 0,
                    "backing_before_hex": "616c706861343220626574613720213463623765376166",
                    "backing_after_hex": "616c706861343220626574613720213463623765376166",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 2,
                    "active_after": 1,
                    "flags": None,
                    "backing_before_hex": "616c706861343220626574613720213463623765376166",
                    "backing_after_hex": "616c706861343220626574613720213463623765376166",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 0,
                    "flags": None,
                    "backing_before_hex": "616c706861343220626574613720213463623765376166",
                    "backing_after_hex": "616c706861343220626574613720213463623765376166",
                },
            ],
            "actual_events": [
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 0,
                    "active_after": 1,
                    "flags": 0,
                    "backing_before_hex": "616c706861343220626574613720213463623765376166",
                    "backing_after_hex": "616c706861343220626574613720213463623765376166",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 0,
                    "flags": None,
                    "backing_before_hex": "616c706861343220626574613720213463623765376166",
                    "backing_after_hex": "616c706861343220626574613720213463623765376166",
                },
            ],
            "return_value_matches_reference": True,
        },
        {
            "suite": "managed_v1",
            "case": "managed-buffer-lifetime.v1.0454",
            "group": "pep688-subject-acquire-release",
            "stage": "subn",
            "backing_hex": "616c706861343220626574613720216634623439393637",
            "expected_events_complete": True,
            "actual_events_complete": True,
            "expected_events": [
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 0,
                    "active_after": 1,
                    "flags": 0,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 2,
                    "flags": 0,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 2,
                    "active_after": 1,
                    "flags": None,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 2,
                    "flags": 0,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 2,
                    "active_after": 1,
                    "flags": None,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 0,
                    "flags": None,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
            ],
            "actual_events": [
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 0,
                    "active_after": 1,
                    "flags": 0,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 0,
                    "flags": None,
                    "backing_before_hex": "616c706861343220626574613720216634623439393637",
                    "backing_after_hex": "616c706861343220626574613720216634623439393637",
                },
            ],
            "return_value_matches_reference": True,
        },
        {
            "suite": "substitution_v2",
            "case": "substitution-buffer-semantics.v1.03521",
            "api": "module.subn",
            "cohort": "pep688-stable-subject",
            "backing_hex": "616c70686134322062657461372067616d6d613320666264363361623864306330",
            "expected_events_complete": False,
            "expected_events": "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION",
            "expected_event_count": 35,
            "actual_events_complete": True,
            "actual_events": [
                {
                    "event": "phase",
                    "name": "materialize-start",
                },
                {
                    "event": "phase",
                    "name": "materialize-complete",
                },
                {
                    "event": "phase",
                    "name": "operation-start",
                },
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 0,
                    "active_after": 1,
                    "flags": 0,
                    "backing_before_hex": "616c70686134322062657461372067616d6d613320666264363361623864306330",
                    "backing_after_hex": "616c70686134322062657461372067616d6d613320666264363361623864306330",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 0,
                    "flags": None,
                    "backing_before_hex": "616c70686134322062657461372067616d6d613320666264363361623864306330",
                    "backing_after_hex": "616c70686134322062657461372067616d6d613320666264363361623864306330",
                },
                {
                    "event": "phase",
                    "name": "operation-return",
                },
                {
                    "event": "phase",
                    "name": "cleanup-complete",
                },
            ],
            "return_value_matches_reference": True,
        },
        {
            "suite": "substitution_v2",
            "case": "substitution-buffer-semantics.v1.03522",
            "api": "pattern.sub",
            "cohort": "pep688-stable-subject",
            "backing_hex": "616c70686134322062657461372067616d6d613320343636326531633632373136",
            "expected_events_complete": False,
            "expected_events": "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION",
            "expected_event_count": 27,
            "actual_events_complete": True,
            "actual_events": [
                {
                    "event": "phase",
                    "name": "materialize-start",
                },
                {
                    "event": "phase",
                    "name": "materialize-complete",
                },
                {
                    "event": "phase",
                    "name": "operation-start",
                },
                {
                    "event": "acquire",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 0,
                    "active_after": 1,
                    "flags": 0,
                    "backing_before_hex": "616c70686134322062657461372067616d6d613320343636326531633632373136",
                    "backing_after_hex": "616c70686134322062657461372067616d6d613320343636326531633632373136",
                },
                {
                    "event": "release",
                    "role": "subject",
                    "behavior": "stable",
                    "active_before": 1,
                    "active_after": 0,
                    "flags": None,
                    "backing_before_hex": "616c70686134322062657461372067616d6d613320343636326531633632373136",
                    "backing_after_hex": "616c70686134322062657461372067616d6d613320343636326531633632373136",
                },
                {
                    "event": "phase",
                    "name": "operation-return",
                },
                {
                    "event": "phase",
                    "name": "cleanup-complete",
                },
            ],
            "return_value_matches_reference": True,
        },
        {
            "suite": "shape_v2",
            "case": "shape-changing-buffer-semantics.v1.00020",
            "api": "module.sub",
            "cohort": "outer-zero-nested-zero",
            "expected_events_complete": False,
            "actual_events_complete": False,
            "expected_events": "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION",
            "actual_events": "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION",
            "expected_event_count": 13,
            "actual_event_count": 13,
            "authenticated_difference_paths": [
                "outcome.events[3].role",
                "outcome.events[4].role",
                "outcome.events[5].role",
                "outcome.events[6].role",
                "outcome.events[7].role",
                "outcome.events[8].role",
                "outcome.events[9].role",
                "outcome.events[10].role",
            ],
            "return_value_matches_reference": True,
        },
        {
            "suite": "shape_v2",
            "case": "shape-changing-buffer-semantics.v1.00021",
            "api": "module.subn",
            "cohort": "outer-zero-nested-zero",
            "expected_events_complete": False,
            "actual_events_complete": False,
            "expected_events": "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION",
            "actual_events": "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION",
            "expected_event_count": 17,
            "actual_event_count": 17,
            "authenticated_difference_paths": [
                "outcome.events[3].role",
                "outcome.events[4].role",
                "outcome.events[5].role",
                "outcome.events[6].role",
                "outcome.events[7].role",
                "outcome.events[8].role",
                "outcome.events[9].role",
                "outcome.events[10].role",
            ],
            "return_value_matches_reference": True,
        },
    ],
    "recovery_and_boundary_effects": {
        "actual_v16_build_archive_read_count": 1,
        "actual_v16_build_archive_gzip_inflation_count": 1,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "actual_reference_workers_started": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
    },
    "phase_history": [
        {
            "phase": "rust-original-campaign-v7",
            "candidate_status": "FAIL",
            "actual_semantic_mismatch_count": 928,
            "explicitly_verified_passing_case_count": 8965,
            "suite_count": 13,
            "verified_passing_cases_derived_by_subtraction": False,
        },
        {
            "phase": "rust-original-campaign-v8",
            "candidate_status": "NOT RUN",
            "controller_status": "FAIL BEFORE CANDIDATE ACTIVATION",
            "actual_candidate_workers": 0,
        },
        {
            "phase": "rust-original-campaign-v9",
            "candidate_status": "NOT RUN",
            "controller_status": "FAIL BEFORE CANDIDATE ACTIVATION",
            "actual_candidate_workers": 0,
            "recorded_inner_error": "accept only one exact owner-only Rust campaign root",
        },
        {
            "phase": "rust-original-campaign-v10",
            "candidate_status": "FAIL",
            "actual_semantic_mismatch_count": 1440,
            "explicitly_verified_passing_case_count": 14853,
            "suite_count": 13,
            "actual_candidate_workers": 13,
            "verified_passing_cases_derived_by_subtraction": False,
        },
    ],
    "authenticated_evidence_owner_lower_bound_before_publication": 194,
    "authenticated_history_reference_lower_bound_before_publication": 199,
    "new_actual_candidate_evidence_owner_count": 2,
    "new_independent_forensic_summary_owner_count": 1,
    "new_actual_evidence_owner_count": 3,
    "resulting_authenticated_evidence_owner_lower_bound": 197,
    "resulting_authenticated_history_reference_lower_bound": 202,
    "global_evidence_owner_census": "NOT MEASURED",
    "from_scratch_candidate_family_count": 6,
    "qualified_candidate_count": 0,
    "runtime_non_delegation": "NOT ESTABLISHED",
    "performance": "NOT MEASURED",
    "memory": "NOT MEASURED",
    "confidence_intervals": "NOT MEASURED",
    "undefined_behavior": "NOT MEASURED",
    "holdout": "NOT OPENED",
    "winner_selected": False,
}


def forensic_expectations() -> dict:
    return copy.deepcopy(FORENSIC_EXPECTATIONS)


def validate_forensic_summary(base: types.ModuleType, forensic: object,
                              receipt: dict) -> None:
    base.need(type(forensic) is dict,
              "reject missing complete independently derived forensics")
    assert isinstance(forensic, dict)
    expected = forensic_expectations()
    base.need(set(forensic) == set(expected),
              "reject erased or invented independent forensic fields")
    for key, value in expected.items():
        base.need(type(forensic.get(key)) is type(value)
                  and forensic[key] == value,
                  "reject forged complete V10 forensics: " + key)
    rows = forensic["suite_results"]
    totals = forensic["actual_result_totals"]
    witnesses = forensic["earliest_genuine_mismatch_witnesses"]
    base.need(
        type(rows) is list and len(rows) == 13
        and type(witnesses) is list and len(witnesses) == 6
        and [row["actual_worker_process_id"] for row in rows] == WORKERS
        and len({row["actual_worker_process_id"] for row in rows}) == 13
        and all(row["actual_worker_started"] is True
                and row["fully_observed"] is True for row in rows)
        and sum(row["case_execution_denominator"] for row in rows) == 31237
        and sum(row["semantic_mismatch_count"] for row in rows) == 1440
        and sum(row["explicitly_verified_passing_case_count"]
                for row in rows) == 14853
        and all(row["explicitly_verified_passing_case_count"] == 0
                for row in rows
                if row["failure_class"] == "SEMANTIC MISMATCH")
        and totals["semantic_mismatch_count"] == 1440
        and totals["verified_passing_case_count"] == 14853
        and totals["verified_passing_cases_derived_by_subtraction"] is False
        and totals[
            "records_from_fully_observed_failed_suites_are_counted_as_passing"
        ] is False
        and totals["infrastructure_failure_count"] == 0
        and forensic["candidate_status"] == "FAIL"
        and forensic["candidate_qualified"] is False
        and forensic["status"] == "PASS"
        and forensic["analysis_status"] == "PASS"
        and forensic["analysis_pass_means"]
            == "INDEPENDENT AUTHENTICATION OF A FAILED CANDIDATE ONLY; "
               "NOT A PASSING CANDIDATE"
        and forensic["durable_publication_receipt"]["sha256"] == RECEIPT[1]
        and forensic["durable_publication_receipt"]["candidate_status"]
            == receipt["candidate_status"]
        and forensic["failure_archive"]["sha256"] == ARCHIVE_SHA
        and forensic["failure_archive"]["uncompressed_sha256"]
            == ARCHIVE_UNCOMPRESSED_SHA
        and forensic["historical_comparison"][
            "semantic_mismatch_regression"] == 512
        and forensic["resulting_authenticated_evidence_owner_lower_bound"]
            == 197
        and forensic[
            "resulting_authenticated_history_reference_lower_bound"] == 202,
        "authenticate every suite, worker, witness and honest owner floor",
    )

def validate_receipt(base: types.ModuleType, receipt: object) -> None:
    base.need(type(receipt) is dict, "reject missing actual small V10 receipt")
    assert isinstance(receipt, dict)
    expected = receipt_expectations()
    base.need(set(receipt) == set(expected),
              "reject erased or invented actual V10 receipt fields")
    for key, value in expected.items():
        base.need(type(receipt.get(key)) is type(value)
                  and receipt[key] == value,
                  "reject forged actual durable V10 receipt: " + key)
    base.need(receipt["status"] == "PASS"
              and receipt["publication_pass_means"]
              == "DURABLE PUBLICATION ONLY"
              and receipt["candidate_status"] == "FAIL"
              and receipt["candidate_qualified"] is False,
              "never confuse durable publication with candidate correctness")



def make_campaign_proof(base: types.ModuleType, owner: dict,
                        receipt: dict, forensic_owner: dict,
                        forensic: dict) -> dict:
    validate_owner(base, owner, RECEIPT, RECEIPT_INODE,
                   "real V10 durable-publication receipt")
    validate_receipt(base, receipt)
    validate_owner(base, forensic_owner, FORENSIC, FORENSIC_INODE,
                   "complete independently derived V10 forensic summary")
    validate_forensic_summary(base, forensic, receipt)
    failed = {
        row["suite"]: {
            "semantic_mismatch_count": row["semantic_mismatch_count"],
            "case_execution_denominator": row["case_execution_denominator"],
            "verified_passing_case_count":
                row["explicitly_verified_passing_case_count"],
        }
        for row in forensic["suite_results"]
        if row["failure_class"] == "SEMANTIC MISMATCH"
    }
    return {
        "schema": SCHEMA + "-authenticated-actual-rust-v10-campaign",
        "version": 10, "status": "FAIL",
        "failure_class": "SEMANTIC MISMATCH", "family": "rust",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "receipt_owner": copy.deepcopy(owner),
        "publication_receipt": copy.deepcopy(receipt),
        "publication_receipt_sha256": RECEIPT[1],
        "forensic_summary_owner": copy.deepcopy(forensic_owner),
        "forensic_summary_sha256": FORENSIC[1],
        "forensic_analysis_status": "PASS",
        "forensic_analysis_pass_means":
            "INDEPENDENT AUTHENTICATION OF A FAILED CANDIDATE ONLY; "
            "NOT A PASSING CANDIDATE",
        "complete_independent_forensic_summary": copy.deepcopy(forensic),
        "complete_independently_authenticated_suite_results":
            copy.deepcopy(forensic["suite_results"]),
        "earliest_genuine_mismatch_witnesses":
            copy.deepcopy(forensic["earliest_genuine_mismatch_witnesses"]),
        "first_party_semantic_root_cause":
            copy.deepcopy(forensic["first_party_semantic_root_cause"]),
        "independently_authenticated_historical_comparison":
            copy.deepcopy(forensic["historical_comparison"]),
        "archive": {
            **copy.deepcopy(receipt["archive"]),
            "sha256_source":
                "ATTESTED BY SMALL RECEIPT AND INDEPENDENT FORENSIC SUMMARY",
            "content_opened_by_graph": False,
            "content_read_by_graph": False,
            "archive_inflated_by_graph": False,
            "content_sha256_recomputed_by_graph": False,
        },
        "case_execution_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13, "semantic_mismatch_count": 1440,
        "verified_passing_case_count": 14853,
        "verified_passing_cases_derived_by_subtraction": False,
        "preserved_previous_rust_semantic_mismatch_count": 928,
        "preserved_previous_rust_verified_passing_case_count": 8965,
        "semantic_mismatch_regression_against_v7": 512,
        "actual_candidate_workers": 13,
        "actual_worker_process_ids": copy.deepcopy(WORKERS),
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "attempted_suite_count": 13, "started_suite_count": 13,
        "completed_suite_count": 13, "infrastructure_failure_count": 0,
        "all_original_observation_vectors_complete": True,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "restored_original_targets":
            copy.deepcopy(receipt["restored_original_targets"]),
        "independently_authenticated_failure_cohort_breakdown": {
            "attestation":
                "COMPLETE AUTHENTICATED FORENSIC SUMMARY; "
                "NOT SMALL RECEIPT ALONE",
            "archive_opened_by_graph": False,
            **failed,
            "failed_cohort_case_denominator": 16384,
            "failed_cohort_verified_passing_case_count": 0,
            "all_passing_cohort_verified_passing_case_count": 14853,
        },
        "historical_predecessor_version": 57,
        "historical_prepublication_evidence_owner_lower_bound": 194,
        "historical_prepublication_reference_lower_bound": 199,
        "new_repository_evidence_owner_count": 3,
        "resulting_repository_evidence_owner_lower_bound": 197,
        "resulting_authenticated_reference_lower_bound": 202,
        "benchmark_files_read_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "failure_archive_opened_by_graph": False,
        "failure_archive_inflated_by_graph": False,
        "failure_archive_sha256_recomputed_by_graph": False,
        "source_build_archive_opened_by_graph": False,
        "source_build_archive_inflated_by_graph": False,
        "original_target_content_read_by_graph": False,
        "journal_opened_by_graph": False,
        "clock_samples": 0, "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_campaign_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject missing actual V10 result")
    assert isinstance(proof, dict)
    owner = proof.get("receipt_owner")
    receipt = proof.get("publication_receipt")
    forensic_owner = proof.get("forensic_summary_owner")
    forensic = proof.get("complete_independent_forensic_summary")
    base.need(type(owner) is dict and type(receipt) is dict
              and type(forensic_owner) is dict and type(forensic) is dict,
              "bind actual failure to both independent bounded owners")
    assert (isinstance(owner, dict) and isinstance(receipt, dict)
            and isinstance(forensic_owner, dict)
            and isinstance(forensic, dict))
    expected = make_campaign_proof(base, owner, receipt,
                                   forensic_owner, forensic)
    base.need(set(proof) == set(expected),
              "reject erased or invented complete actual campaign proof")
    for key, value in expected.items():
        base.need(type(proof.get(key)) is type(value) and proof[key] == value,
                  "reject forged complete forensic campaign proof: " + key)


def authenticate_actual_campaign(base: types.ModuleType,
                                 options: argparse.Namespace) -> dict:
    base.need(base.checked(options.receipt_sha256,
                           "exact small actual V10 publication receipt")
              == RECEIPT[1],
              "reject substituted actual V10 publication receipt")
    base.need(type(options.receipt_bytes) is int
              and options.receipt_bytes == RECEIPT[2]
              and type(options.receipt_inode) is int
              and options.receipt_inode == RECEIPT_INODE
              and type(options.receipt_device) is int
              and options.receipt_device == DEVICE,
              "require exact actual V10 receipt owner")
    base.need(base.checked(options.forensic_sha256,
                           "exact independent forensic summary")
              == FORENSIC[1],
              "reject substituted independent V10 forensic summary")
    base.need(type(options.forensic_bytes) is int
              and options.forensic_bytes == FORENSIC[2]
              and type(options.forensic_inode) is int
              and options.forensic_inode == FORENSIC_INODE
              and type(options.forensic_device) is int
              and options.forensic_device == DEVICE,
              "require exact independent V10 forensic summary owner")
    raw, owner = base.read_owner(*RECEIPT, private=True)
    receipt = base.document(raw, "complete small actual V10 receipt")
    forensic_raw, forensic_owner = base.read_owner(*FORENSIC, private=True)
    forensic = base.document(
        forensic_raw, "complete independently derived V10 forensics",
        exact=False,
    )
    return make_campaign_proof(base, owner, receipt,
                               forensic_owner, forensic)

def synthetic_receipt() -> dict:
    return receipt_expectations()


def result_fields(proof: dict) -> dict:
    return {
        "actual_rust_v10_campaign": copy.deepcopy(proof),
        "actual_rust_original_campaign": copy.deepcopy(proof),
        "actual_complete_rust_campaign": copy.deepcopy(proof),
        "current_complete_rust_campaign": copy.deepcopy(proof),
        "actual_rust_v10_controller_status": "PASS",
        "actual_rust_v10_matching_status": "FAIL",
        "actual_rust_v10_candidate_correctness": "FAIL",
        "actual_rust_v10_candidate_status": "FAIL",
        "actual_rust_v10_publication_status": "PASS",
        "actual_rust_v10_publication_pass_means":
            "DURABLE PUBLICATION ONLY",
        "actual_rust_v10_publication_receipt_owner":
            copy.deepcopy(proof["receipt_owner"]),
        "actual_rust_v10_publication_receipt_sha256": RECEIPT[1],
        "actual_rust_v10_forensic_summary_owner":
            copy.deepcopy(proof["forensic_summary_owner"]),
        "actual_rust_v10_forensic_summary_sha256": FORENSIC[1],
        "actual_rust_v10_forensic_analysis_status": "PASS",
        "actual_rust_v10_forensic_analysis_pass_means":
            "INDEPENDENT AUTHENTICATION OF A FAILED CANDIDATE ONLY; "
            "NOT A PASSING CANDIDATE",
        "actual_rust_v10_complete_independently_authenticated_suite_results":
            copy.deepcopy(
                proof["complete_independently_authenticated_suite_results"]),
        "actual_rust_v10_earliest_genuine_mismatch_witnesses":
            copy.deepcopy(proof["earliest_genuine_mismatch_witnesses"]),
        "actual_rust_v10_first_party_semantic_root_cause":
            copy.deepcopy(proof["first_party_semantic_root_cause"]),
        "actual_rust_v10_independently_authenticated_historical_comparison":
            copy.deepcopy(
                proof["independently_authenticated_historical_comparison"]),
        "actual_rust_v10_semantic_mismatch_count": 1440,
        "actual_rust_v10_verified_passing_case_count": 14853,
        "actual_rust_v10_verified_passing_cases_derived_by_subtraction":
            False,
        "actual_rust_v10_semantic_mismatch_regression_against_v7": 512,
        "actual_rust_v10_candidate_qualified": False,
        "actual_rust_v10_candidate_workers": 13,
        "actual_rust_v10_worker_process_ids": copy.deepcopy(WORKERS),
        "actual_rust_worker_process_ids": copy.deepcopy(WORKERS),
        "actual_rust_v10_distinct_worker_process_id_count": 13,
        "actual_rust_v10_duplicate_worker_process_id_count": 0,
        "actual_rust_v10_missing_worker_process_id_count": 0,
        "actual_rust_v10_attempted_suite_count": 13,
        "actual_rust_v10_started_suite_count": 13,
        "actual_rust_v10_completed_suite_count": 13,
        "actual_rust_v10_fully_observed_suite_count": 13,
        "actual_rust_v10_infrastructure_failure_count": 0,
        "actual_rust_v10_synthetic_failed_worker_placeholder_count": 0,
        "actual_rust_v10_synthetic_placeholders_are_observed_workers":
            False,
        "actual_rust_v10_placeholder_worker_flags_are_real_attempts":
            False,
        "actual_rust_v10_all_original_observation_vectors_complete": True,
        "actual_rust_v10_all_four_original_targets_restored": True,
        "actual_rust_v10_restoration_verified_before_publication": True,
        "actual_rust_v10_restored_original_targets":
            copy.deepcopy(proof["restored_original_targets"]),
        "actual_rust_v10_independently_authenticated_failure_cohort_breakdown":
            copy.deepcopy(proof["independently_authenticated_failure_cohort_breakdown"]),
        "actual_rust_v10_failure_archive":
            copy.deepcopy(proof["archive"]),
        "actual_rust_v10_failure_archive_read_by_graph": False,
        "actual_rust_v10_failure_archive_inflated_by_graph": False,
        "actual_rust_v10_failure_archive_sha256_recomputed_by_graph":
            False,
        "actual_rust_v10_build_archive_reads_by_controller": 1,
        "actual_rust_v10_build_archive_inflations_by_controller": 1,
        "actual_rust_v10_build_archive_read_by_graph": False,
        "actual_rust_v10_build_archive_inflated_by_graph": False,
        "actual_rust_v10_build_archive_sha256_recomputed_by_graph": False,
        "actual_rust_v10_current_prepublication_evidence_lower_bound":
            194,
        "actual_rust_v10_current_prepublication_history_lower_bound":
            199,
        "actual_rust_v10_new_outcome_owner_count": 3,
        "actual_current_graph_predecessor_version": 57,
        "authenticated_evidence_owner_lower_bound": 197,
        "authenticated_history_reference_lower_bound": 202,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
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


def validate_snapshot(modules: tuple, snapshot: object) -> None:
    previous, prior_modules, base = modules
    base.need(type(snapshot) is dict, "reject missing full actual V58 snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("actual_rust_v10_campaign")
    validate_campaign_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(type(snapshot.get(key)) is type(value)
                  and snapshot[key] == value,
                  "reject invented actual V10 campaign outcome: " + key)
    replaced = snapshot.get("preserved_v57_replaced_snapshot_fields")
    base.need(type(replaced) is dict and set(replaced).issubset(updates),
              "preserve every replaced authenticated V57 snapshot field")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v57_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(prior_modules, history)
    base.need(
        snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_status_counts")
            == PUBLIC_COUNTS
        and snapshot.get("large_input_source_case_matrix_count") == 32
        and snapshot.get("large_input_source_case_status_counts")
            == LARGE_COUNTS
        and snapshot.get("large_input_upstream_original_case_count") == 2
        and snapshot.get("large_input_upstream_original_subject_bytes")
            == 2147483648
        and snapshot.get("actual_rust_v16_build_status") == "PASS"
        and snapshot.get("actual_rust_v16_compiler_process_count") == 28
        and snapshot.get(
            "actual_rust_v16_compiler_pid_vector_present_in_receipt")
            is False
        and snapshot.get(
            "actual_rust_v16_phase_vector_present_in_receipt") is False
        and snapshot.get(
            "actual_rust_v16_native_artifact_digests_present_in_receipt")
            is False
        and snapshot.get("actual_rust_v7_semantic_status") == "FAIL"
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get(
            "actual_rust_v7_explicitly_verified_passing_case_count")
            == 8965
        and snapshot.get("actual_rust_v7_candidate_workers") == 13
        and snapshot.get("actual_rust_v8_controller_status") == "FAIL"
        and snapshot.get("actual_rust_v8_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v8_candidate_workers") == 0
        and snapshot.get("actual_rust_v9_controller_status") == "FAIL"
        and snapshot.get("actual_rust_v9_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v9_candidate_workers") == 0
        and snapshot.get("actual_rust_v10_controller_status") == "PASS"
        and snapshot.get("actual_rust_v10_matching_status") == "FAIL"
        and snapshot.get("actual_rust_v10_semantic_mismatch_count") == 1440
        and snapshot.get(
            "actual_rust_v10_verified_passing_case_count") == 14853
        and snapshot.get(
            "actual_rust_v10_semantic_mismatch_regression_against_v7")
            == 512
        and snapshot.get("actual_rust_v10_candidate_workers") == 13
        and snapshot.get("actual_rust_v10_attempted_suite_count") == 13
        and snapshot.get("actual_rust_v10_started_suite_count") == 13
        and snapshot.get("actual_rust_v10_completed_suite_count") == 13
        and snapshot.get("actual_rust_v10_fully_observed_suite_count")
            == 13
        and snapshot.get("actual_rust_v10_infrastructure_failure_count")
            == 0
        and snapshot.get(
            "actual_rust_v10_synthetic_failed_worker_placeholder_count")
            == 0
        and snapshot.get("actual_rust_original_campaign", {}).get(
            "semantic_mismatch_count") == 1440
        and snapshot.get("actual_complete_rust_campaign", {}).get(
            "semantic_mismatch_count") == 1440
        and snapshot.get("current_complete_rust_campaign", {}).get(
            "semantic_mismatch_count") == 1440
        and snapshot.get("historical_rust_v3_original_campaign", {}).get(
            "semantic_mismatch_count") == 1087
        and snapshot.get("historical_rust_v4_original_campaign", {}).get(
            "semantic_mismatch_count") == 1036
        and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
        and snapshot.get(
            "c_v4_original_campaign_semantic_mismatch_count") == 1230
        and snapshot.get(
            "zig_v2_original_campaign_semantic_mismatch_count") == 2172
        and snapshot.get(
            "zig_v3_original_campaign_semantic_mismatch_count") == 1764
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("actually_tested_corrected_candidate_families")
            == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
            == 1
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 197
        and snapshot.get(
            "authenticated_history_reference_lower_bound") == 202
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("actual_native_libraries_loaded_by_graph") == 0
        and snapshot.get(
            "source_build_archive_gzip_inflation_count_by_graph") == 0
        and snapshot.get("actual_clock_samples_by_graph") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("winner_selected") is False,
        "preserve complete actual failed V10 matching and all honest history",
    )


def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    v43 = prior_modules[1][1][1][1][9]
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact actual V58 graph renderer")
    inputs_sha = base.checked(inputs_sha, "exact actual V58 graph inputs")
    visible = old_svg.decode("utf-8").replace(
        "v57-title", "v58-title").replace(
        "v57-description", "v58-description")
    lines = visible.splitlines()
    base.need(len(lines) > 10
              and lines[1].startswith('<title id="v58-title">')
              and lines[2].startswith('<desc id="v58-description">'),
              "preserve exact pushed V57 accessible graph structure")
    lines[1] = (
        '<title id="v58-title">Building a faster Python re: no '
        'compatible replacement yet; latest full Rust test found '
        '1,440 differences</title>'
    )
    lines[2] = (
        '<desc id="v58-description">Pinned Python 3.14.6 remains the '
        'verified baseline. The corrected Rust V10 campaign actually ran '
        'all 13 real workers across the frozen 31,237 original cases. It '
        'failed 1,440 compatibility checks and explicitly verified 14,853 '
        'passing cases; that is 512 more failures than the preceding '
        '928-failure result. Independently authenticated failed cohorts are managed 16, '
        'substitution 368 and shape 1,056; those failed cohorts have zero '
        'explicitly verified passes. The small durable receipt proves '
        'publication only, never candidate success, and the graph does not '
        'open the compressed report. All four original targets were '
        'restored. Six first-party replacement families remain, with zero '
        'compatible candidates. V8 and V9 really failed before starting '
        'workers; V9 synthetic records remain synthetic. Additional 50 '
        'signature checks, 32 public-interface observations and 32 '
        'large-input observations have separate denominators. The '
        '4,194,304-case holdout is not generated and not opened. Speed, '
        'memory and uncertainty are NOT MEASURED; runtime independence is '
        'NOT ESTABLISHED. Exactly three independently authenticated evidence owners raise '
        'authenticated evidence and reference floors from 194 / 199 to '
        '197 / 202.</desc>'
    )
    visible = "\n".join(lines)
    replacements = (
        ('<text x="333" y="170" class="value orange">928 DIFFERENCES</text>',
         '<text x="333" y="170" class="value orange">1,440 DIFFERENCES</text>',
         "show the actual latest 1,440-mismatch Rust result"),
        ('13 real workers completed the frozen original comparison. Rust '
         'produced 928 differences and 8,965 explicitly verified passes.',
         '13 real workers completed all 31,237 cases: 1,440 differences '
         'and 14,853 explicitly verified passes; 512 more failures.',
         "show real workers, actual mismatches, verified passes and regression"),
        ('<text x="65" y="398" class="heading">Two Rust test runners '
         'failed; corrected follow-up frozen</text>',
         '<text x="65" y="398" class="heading">Latest corrected Rust '
         'test ran and failed</text>',
         "report actually executed V10 rather than old source freeze"),
        ('The native build passed. V8 and V9 stopped before matching. '
         'V10 is source frozen, NOT RUN. Real new workers: 0.',
         'Native build passed; V8/V9 stopped. V10 ran 13 genuine workers '
         'and failed; all four original targets restored.',
         "distinguish historical no-worker failures from 13 real V10 workers"),
        ('Repair effectiveness, compatibility, speed and memory: '
         'NOT MEASURED.',
         'Compatibility: FAIL. Speed, memory and uncertainty: '
         'NOT MEASURED.',
         "never claim an unmeasured actual correctness outcome"),
        ('<text x="218" y="659" class="body orange strong">928 '
         'compatibility differences</text>',
         '<text x="218" y="659" class="body orange strong">1,440 '
         'compatibility differences</text>',
         "keep current Rust row on actual V10 failures"),
        ('V7 failed; V8/V9 stopped; corrected V10 not yet run',
         'V10: 1,440 failures; 14,853 verified passes; 512 more than V7',
         "show the actual full comparison against old V7"),
        ('<tspan class="strong">Rust:</tspan> current 928; historical '
         '1,036 and 1,087.',
         '<tspan class="strong">Rust:</tspan> current 1,440; historical '
         '928, 1,036 and 1,087.',
         "preserve the previous 928 result as history, not the latest result"),
        ('No historical result claims that the new source-only Rust '
         'idea has been tested.',
         'Independently authenticated failures: managed 16; substitution 368; shape '
         '1,056. Failed suites do not imply passes.',
         "label cohort observations as independently authenticated, not receipt-proved"),
        ('<text x="64" y="1756" class="heading">Corrected V10 full-suite '
         'test frozen; not yet run</text>',
         '<text x="64" y="1756" class="heading">Corrected V10 actually '
         'ran: FAIL, 512 more differences</text>',
         "publish actual corrected full-suite result"),
        ('Exactly three new V10 source files raise actual current lower '
         'bounds from 191 / 196 to 194 / 199.',
         'Exactly three V10 evidence owners raise actual current lower '
         'bounds from 194 / 199 to 197 / 202.',
         "count the actual receipt and receipt-attested compressed owner"),
        ('The existing failure receipt does not prove a breakdown of '
         'individual failure categories.',
         'Cohorts are INDEPENDENTLY AUTHENTICATED; the small receipt does not itself '
         'prove their breakdown.',
         "never attribute root-only cohort observations to the small receipt"),
    )
    for before, after, why in replacements:
        visible = v43.replace_once(base, visible, before, after, why)
    lines = visible.splitlines()
    start = next(
        (index for index, line in enumerate(lines)
         if line.startswith('<rect x="44" y="1858" width="1352"')),
        None,
    )
    base.need(type(start) is int,
              "replace exactly the bounded prior graph evidence footer")
    assert isinstance(start, int)
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="381" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact evidence for the '
        'latest failed real test</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V57 graph inputs SHA-256", V57["inputs"][1]),
        ("Historical V57 graph renderer SHA-256", V57["source"][1]),
        ("Historical V57 graph summary SHA-256", V57["summary"][1]),
        ("Historical V57 graph image SHA-256", V57["svg"][1]),
        ("Small actual V10 durable receipt SHA-256", RECEIPT[1]),
        ("Complete independent V10 forensic summary SHA-256", FORENSIC[1]),
        ("V10 compressed report SHA-256 (receipt-attested; not opened by "
         "this graph)", ARCHIVE_SHA),
        ("Actually executed V10 runner source SHA-256", RUNNER_SOURCE),
        ("Actually executed V10 runner protocol SHA-256", RUNNER_PROTOCOL),
        ("Actually executed V10 runner contract SHA-256", RUNNER_CONTRACT),
        ("Recorded V16 build archive SHA-256 (not opened by this graph)",
         BUILD_ARCHIVE_SHA),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + index * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2145" class="small">Independently authenticated cohorts: '
        'managed 16 / 1,024; substitution 368 / 5,120; shape 1,056 / '
        '10,240. Failed cohorts: zero verified passes.</text>',
        '<text x="65" y="2163" class="small">13 real workers; 13 '
        'completed suites; 14,853 explicitly verified passes; 1,440 '
        'mismatches; 512 more failures than V7.</text>',
        '<text x="65" y="2186" class="small">Publication PASS means '
        'DURABLE PUBLICATION ONLY. Candidate correctness: FAIL. '
        'All four original targets restored.</text>',
        '<text x="65" y="2209" class="small">V8/V9 no-worker history '
        'preserved. Holdout NOT OPENED. Speed and memory NOT MEASURED. '
        'Compatible replacements: 0.</text>',
        '<!-- Graph reads only the authenticated 6,708-byte V10 receipt and '
        '24,701-byte independently derived forensic summary; '
        'it never opens, stats, hashes, inflates or enumerates the '
        'compressed report, candidates, native libraries, recovery roots, '
        'clocks, benchmarks or holdout. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in footers:
        base.need(
            raw.count((label + ": " + value).encode("ascii")) == 1,
            "bind one exact actual or explicitly historical V58 footer: "
            + label,
        )
    lower = raw.lower()
    for phrase in (
            b'height="2250"', b"building a faster python re",
            b"1,440 differences", b"14,853 explicitly verified",
            b"512 more", b"13 real workers", b"31,237",
            b"managed 16", b"substitution 368", b"shape 1,056",
            b"independently authenticated", b"failed cohorts: zero verified passes",
            b"all four original targets restored", b"4.2m unopened",
            b"not measured", b"not established", b"not opened",
            b"not opened by this graph", b"durable publication only",
            b"candidate correctness: fail", b"194 / 199", b"197 / 202",
            b"signature checks", b"public-interface observations",
            b"large-input observations", b"17 pass", b"7 fail",
            b"22 pass", b"3 not run", b"2,147,483,648",
            b"928", b"1,087", b"1,036", b"1,262", b"1,230",
            b"2,172", b"1,764", b"not generated"):
        base.need(phrase in lower,
                  "preserve complete honest actual V10 graph: "
                  + repr(phrase))
    for falsehood in (
            b"v10 not yet run", b"v10 is source frozen, not run",
            b"v10 matching passed", b"candidate correctness: pass",
            b"rust candidate qualified", b"winner selected",
            b"holdout opened", b"faster than python",
            b"failure categories proved by receipt",
            b"16,384 verified passes", b"29,797 verified passes"):
        base.need(falsehood not in lower,
                  "reject fabricated actual V10 success: "
                  + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish truthful actual V58 chart with one exact linefeed")
    return raw


def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact independent actual V58 graph source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound exact independently owned actual V58 graph source")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                private=True)
    old, old_inputs, old_svg = authenticate_v57(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V57},
    )
    proof = authenticate_actual_campaign(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v57_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V57.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs", "version": 58, "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessor,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(modules, snapshot, old_svg, source_sha,
                   base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve baseline Python and exactly six from-scratch families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 197,
            "authenticated_history_reference_lower_bound": 202,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "actual_v10_campaign": copy.deepcopy(proof),
                "actual_v10_controller_status": "PASS",
                "actual_v10_matching_status": "FAIL",
                "actual_v10_candidate_correctness": "FAIL",
                "actual_v10_candidate_status": "FAIL",
                "actual_v10_publication_status": "PASS",
                "actual_v10_publication_pass_means":
                    "DURABLE PUBLICATION ONLY",
                "actual_v10_semantic_mismatch_count": 1440,
                "actual_v10_verified_passing_case_count": 14853,
                "actual_v10_verified_passing_cases_derived_by_subtraction":
                    False,
                "actual_v10_semantic_mismatch_regression_against_v7": 512,
                "actual_v10_candidate_workers": 13,
                "actual_v10_worker_process_ids": copy.deepcopy(WORKERS),
                "actual_v10_attempted_suite_count": 13,
                "actual_v10_started_suite_count": 13,
                "actual_v10_completed_suite_count": 13,
                "actual_v10_fully_observed_suite_count": 13,
                "actual_v10_infrastructure_failure_count": 0,
                "actual_v10_synthetic_failed_worker_placeholder_count": 0,
                "actual_v10_synthetic_placeholders_are_observed_workers":
                    False,
                "actual_v10_all_four_original_targets_restored": True,
                "actual_v10_restoration_verified_before_publication": True,
                "actual_v10_independently_authenticated_failure_cohort_breakdown":
                    copy.deepcopy(
                        proof["independently_authenticated_failure_cohort_breakdown"]),
                "actual_v10_controller_build_archive_reads": 1,
                "actual_v10_controller_build_archive_inflations": 1,
                "actual_v10_build_archive_read_by_graph": False,
                "actual_v10_failure_archive_read_by_graph": False,
                "actual_v10_candidate_qualified": False,
                "actual_v8_controller_status": "FAIL",
                "actual_v8_matching_status": "NOT RUN",
                "actual_v8_candidate_workers": 0,
                "actual_v16_build_status": "PASS",
                "actual_v16_compiler_process_count": 28,
                "actual_v16_unique_pid_vector_in_receipt": False,
                "actual_v16_phase_vector_in_receipt": False,
                "current_original_campaign_semantic_mismatch_count": 1440,
                "current_original_campaign_verified_passing_case_count":
                    14853,
                "current_original_campaign_candidate_worker_count": 13,
                "actual_candidate_workers": 13,
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 58, "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json",
                           base.digest(input_raw), len(input_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot, "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(max(len(input_raw), len(summary_raw), len(svg))
              <= base.OWNER_LIMIT,
              "bound exactly three complete authorized V58 graph outputs")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_campaign_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged actual V10 result: " + description)


def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 3920
        and prior.get("actual_rust_v16_build_status") == "PASS"
        and prior.get("actual_rust_v16_compiler_process_count") == 28
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get(
            "actual_rust_v7_explicitly_verified_passing_case_count")
            == 8965
        and prior.get("actual_rust_v7_candidate_workers") == 13
        and prior.get("actual_rust_v9_controller_status") == "FAIL"
        and prior.get("actual_rust_v9_matching_status") == "NOT RUN"
        and prior.get("actual_rust_v9_candidate_workers") == 0
        and prior.get(
            "actual_rust_v9_synthetic_failed_worker_placeholder_count")
            == 13
        and prior.get(
            "actual_rust_v9_synthetic_placeholders_are_observed_workers")
            is False
        and prior.get("actual_rust_v8_controller_status") == "FAIL"
        and prior.get("actual_rust_v8_matching_status") == "NOT RUN"
        and prior.get("actual_rust_v8_candidate_workers") == 0
        and prior.get("rust_original_campaign_v10_matching_status")
            == "NOT RUN"
        and prior.get("authenticated_evidence_owner_lower_bound") == 194
        and prior.get("authenticated_history_reference_lower_bound")
            == 199
        and prior.get("public_entrypoint_case_status_counts")
            == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts")
            == LARGE_COUNTS,
        "preserve all 3,920 authenticated V57 source-only controls",
    )
    v43 = prior_modules[1][1][1][1][9]
    rejected = 0
    with base.SourceOnlyWall() as wall:
        receipt = synthetic_receipt()
        owner = base.synthetic_owner(RECEIPT, RECEIPT_INODE)
        forensic_owner = base.synthetic_owner(FORENSIC, FORENSIC_INODE)
        forensic = forensic_expectations()
        proof = make_campaign_proof(base, owner, receipt,
                                   forensic_owner, forensic)
        validate_campaign_proof(base, proof)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for key, value in proof["receipt_owner"].items():
            hostile = copy.deepcopy(proof)
            hostile["receipt_owner"][key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "receipt-owner:" + key)
        for key, value in proof["publication_receipt"].items():
            hostile = copy.deepcopy(proof)
            hostile["publication_receipt"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "receipt:" + key)
        for key, value in proof["publication_receipt"]["archive"].items():
            hostile = copy.deepcopy(proof)
            hostile["publication_receipt"]["archive"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile,
                                       "receipt-archive:" + key)
        for role, row in (
                proof["publication_receipt"][
                    "restored_original_targets"].items()):
            for key, value in row.items():
                hostile = copy.deepcopy(proof)
                hostile["publication_receipt"][
                    "restored_original_targets"][role][key] = (
                        v43.forged_value(base, value))
                rejected += reject_control(
                    base, hostile, "restored-target:" + role + ":" + key)
        for key, value in proof["forensic_summary_owner"].items():
            hostile = copy.deepcopy(proof)
            hostile["forensic_summary_owner"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile,
                                       "forensic-owner:" + key)
        complete = proof["complete_independent_forensic_summary"]
        for key, value in complete.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_independent_forensic_summary"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "forensic:" + key)
        for index, row in enumerate(complete["suite_results"]):
            for key, value in row.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_forensic_summary"][
                    "suite_results"][index][key] = (
                        v43.forged_value(base, value))
                rejected += reject_control(
                    base, hostile, "forensic-suite:"
                    + str(index) + ":" + key)
        for index, witness in enumerate(
                complete["earliest_genuine_mismatch_witnesses"]):
            for key, value in witness.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_forensic_summary"][
                    "earliest_genuine_mismatch_witnesses"][index][key] = (
                        v43.forged_value(base, value))
                rejected += reject_control(
                    base, hostile, "forensic-witness:"
                    + str(index) + ":" + key)
            for section in ("expected_events", "actual_events"):
                rows = witness.get(section)
                if type(rows) is not list:
                    continue
                for row_index, event in enumerate(rows):
                    for key, value in event.items():
                        hostile = copy.deepcopy(proof)
                        hostile["complete_independent_forensic_summary"][
                            "earliest_genuine_mismatch_witnesses"][
                                index][section][row_index][key] = (
                                    v43.forged_value(base, value))
                        rejected += reject_control(
                            base, hostile, "forensic-witness-event:"
                            + str(index) + ":" + section + ":"
                            + str(row_index) + ":" + key)
        for section in (
                "actual_result_totals", "historical_comparison",
                "first_party_semantic_root_cause",
                "failure_archive", "durable_publication_receipt",
                "recovery_and_boundary_effects"):
            for key, value in complete[section].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_forensic_summary"][
                    section][key] = v43.forged_value(base, value)
                rejected += reject_control(
                    base, hostile, "forensic:" + section + ":" + key)
        for key, value in proof["archive"].items():
            hostile = copy.deepcopy(proof)
            hostile["archive"][key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile,
                                       "proof-archive:" + key)
        cohorts = proof["independently_authenticated_failure_cohort_breakdown"]
        for key, value in cohorts.items():
            hostile = copy.deepcopy(proof)
            hostile["independently_authenticated_failure_cohort_breakdown"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "cohort:" + key)
        for role in ("managed_v1", "substitution_v2", "shape_v2"):
            for key, value in cohorts[role].items():
                hostile = copy.deepcopy(proof)
                hostile["independently_authenticated_failure_cohort_breakdown"][
                    role][key] = v43.forged_value(base, value)
                rejected += reject_control(
                    base, hostile, "cohort:" + role + ":" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v58")),
            ("filesystem", lambda: os.open("forbidden-v58", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v58")),
            ("write", lambda: os.mkdir("forbidden-v58")),
            ("process", lambda: subprocess.run(("forbidden-v58",))),
            ("process", lambda: subprocess.Popen(("forbidden-v58",))),
            ("process", lambda: os.execv("/forbidden-v58", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically forbid V58 self-test " + kind)
            else:
                raise base.GraphError("forbidden V58 self-test effect")
        base.need(rejected >= 500,
                  "reject forged receipts, workers, archive and cohorts")
        return {
            "schema": SCHEMA + "-source-only-self-test", "version": 58,
            "status": "PASS", "synthetic_only": True,
            "previous_v57_hostile_controls": 3920,
            "new_v58_hostile_controls": rejected,
            "rejected_hostile_control_count": 3920 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_receipt_owners_read_by_self_test": 0,
            "actual_forensic_summary_owners_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_receipts_read_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
            "actual_frozen_v10_source_files_read_by_self_test": 0,
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
            "actual_current_graph_predecessor_version": 57,
            "actual_rust_v16_build_status": "PASS",
            "actual_rust_v16_compiler_process_count": 28,
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v8_controller_status": "FAIL",
            "actual_rust_v8_matching_status": "NOT RUN",
            "actual_rust_v8_candidate_workers": 0,
            "actual_rust_v9_controller_status": "FAIL",
            "actual_rust_v9_matching_status": "NOT RUN",
            "actual_rust_v9_candidate_workers": 0,
            "actual_rust_v9_synthetic_failed_worker_placeholder_count":
                13,
            "actual_rust_v9_synthetic_placeholders_are_observed_workers":
                False,
            "actual_rust_v10_controller_status": "PASS",
            "actual_rust_v10_matching_status": "FAIL",
            "actual_rust_v10_semantic_mismatch_count": 1440,
            "actual_rust_v10_verified_passing_case_count": 14853,
            "actual_rust_v10_verified_passing_cases_derived_by_subtraction":
                False,
            "actual_rust_v10_semantic_mismatch_regression_against_v7": 512,
            "actual_rust_v10_candidate_workers": 13,
            "actual_rust_v10_attempted_suite_count": 13,
            "actual_rust_v10_started_suite_count": 13,
            "actual_rust_v10_completed_suite_count": 13,
            "actual_rust_v10_fully_observed_suite_count": 13,
            "actual_rust_v10_infrastructure_failure_count": 0,
            "actual_rust_v10_synthetic_failed_worker_placeholder_count": 0,
            "actual_rust_v10_synthetic_placeholders_are_observed_workers":
                False,
            "actual_rust_v10_all_four_original_targets_restored": True,
            "actual_rust_v10_restoration_verified_before_publication":
                True,
            "actual_rust_v10_publication_status": "PASS",
            "actual_rust_v10_forensic_analysis_status": "PASS",
            "actual_rust_v10_forensic_summary_sha256": FORENSIC[1],
            "actual_rust_v10_publication_pass_means":
                "DURABLE PUBLICATION ONLY",
            "actual_rust_v10_candidate_status": "FAIL",
            "actual_rust_v10_candidate_qualified": False,
            "actual_rust_v10_failure_archive_read_by_graph": False,
            "actual_rust_v10_failure_archive_inflated_by_graph": False,
            "actual_rust_v10_failure_archive_sha256_recomputed_by_graph":
                False,
            "authenticated_evidence_owner_lower_bound": 197,
            "authenticated_history_reference_lower_bound": 202,
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "supplementary_signature_check_count": 50,
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts":
                copy.deepcopy(PUBLIC_COUNTS),
            "large_input_source_case_matrix_count": 32,
            "large_input_source_case_status_counts":
                copy.deepcopy(LARGE_COUNTS),
            "large_input_upstream_original_case_count": 2,
            "large_input_upstream_original_subject_bytes": 2147483648,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "actually_tested_corrected_candidate_families": ["rust"],
            "actually_tested_corrected_candidate_family_count": 1,
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }

def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json",
                       OUTPUT + ".svg"}
              and type(raw) is bytes
              and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only the three authorized actual V58 graph outputs")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact authorized V58 graph byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid() and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish one private complete independently owned V58 asset")
    finally:
        os.close(handle)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(str(ROOT / Path(path).parent), flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(path, base.digest(raw), len(raw),
                                  private=True)
    base.need(confirmed == raw, "re-authenticate complete V58 graph output")



def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    fields = (
        "actual_rust_v16_build_status",
        "actual_rust_v16_compiler_process_count",
        "actual_rust_v7_semantic_status",
        "actual_rust_v7_semantic_mismatch_count",
        "actual_rust_v7_explicitly_verified_passing_case_count",
        "actual_rust_v7_candidate_workers",
        "actual_rust_v8_controller_status",
        "actual_rust_v8_matching_status",
        "actual_rust_v8_candidate_workers",
        "actual_rust_v9_controller_status",
        "actual_rust_v9_matching_status",
        "actual_rust_v9_candidate_workers",
        "actual_rust_v9_synthetic_failed_worker_placeholder_count",
        "actual_rust_v9_synthetic_placeholders_are_observed_workers",
        "actual_rust_v10_controller_status",
        "actual_rust_v10_matching_status",
        "actual_rust_v10_candidate_correctness",
        "actual_rust_v10_candidate_status",
        "actual_rust_v10_publication_status",
        "actual_rust_v10_publication_pass_means",
        "actual_rust_v10_publication_receipt_sha256",
        "actual_rust_v10_forensic_summary_sha256",
        "actual_rust_v10_forensic_analysis_status",
        "actual_rust_v10_forensic_analysis_pass_means",
        "actual_rust_v10_complete_independently_authenticated_suite_results",
        "actual_rust_v10_earliest_genuine_mismatch_witnesses",
        "actual_rust_v10_first_party_semantic_root_cause",
        "actual_rust_v10_independently_authenticated_historical_comparison",
        "actual_rust_v10_semantic_mismatch_count",
        "actual_rust_v10_verified_passing_case_count",
        "actual_rust_v10_verified_passing_cases_derived_by_subtraction",
        "actual_rust_v10_semantic_mismatch_regression_against_v7",
        "actual_rust_v10_candidate_qualified",
        "actual_rust_v10_candidate_workers",
        "actual_rust_v10_worker_process_ids",
        "actual_rust_v10_distinct_worker_process_id_count",
        "actual_rust_v10_duplicate_worker_process_id_count",
        "actual_rust_v10_missing_worker_process_id_count",
        "actual_rust_v10_attempted_suite_count",
        "actual_rust_v10_started_suite_count",
        "actual_rust_v10_completed_suite_count",
        "actual_rust_v10_fully_observed_suite_count",
        "actual_rust_v10_infrastructure_failure_count",
        "actual_rust_v10_synthetic_failed_worker_placeholder_count",
        "actual_rust_v10_synthetic_placeholders_are_observed_workers",
        "actual_rust_v10_all_four_original_targets_restored",
        "actual_rust_v10_restoration_verified_before_publication",
        "actual_rust_v10_independently_authenticated_failure_cohort_breakdown",
        "actual_rust_v10_failure_archive_read_by_graph",
        "actual_rust_v10_failure_archive_inflated_by_graph",
        "actual_rust_v10_failure_archive_sha256_recomputed_by_graph",
        "actual_rust_v10_build_archive_reads_by_controller",
        "actual_rust_v10_build_archive_inflations_by_controller",
        "actual_rust_v10_build_archive_read_by_graph",
        "actual_rust_v10_current_prepublication_evidence_lower_bound",
        "actual_rust_v10_current_prepublication_history_lower_bound",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
        "first_party_source_inventory_family_count",
        "actually_tested_corrected_candidate_families",
        "actually_runnable_candidate_family_count",
        "qualified_candidate_count",
        "final_comparison_planned_case_count",
        "final_comparison_cases_generated",
        "final_holdout_opened",
        "runtime_no_delegation",
        "performance", "memory", "confidence_intervals",
        "undefined_behavior", "winner_selected",
    )
    return {
        "schema": SCHEMA + suffix, "version": 58, "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 57,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V57.items()},
        **{key: copy.deepcopy(snapshot[key]) for key in fields},
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
    for role in V57:
        parser.add_argument("--previous-" + role + "-sha256")
    parser.add_argument("--receipt-sha256")
    parser.add_argument("--receipt-bytes", type=int)
    parser.add_argument("--receipt-inode", type=int)
    parser.add_argument("--receipt-device", type=int)
    parser.add_argument("--forensic-sha256")
    parser.add_argument("--forensic-bytes", type=int)
    parser.add_argument("--forensic-inode", type=int)
    parser.add_argument("--forensic-device", type=int)
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v57()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256" for role in V57)
            forbidden.extend(
                ("receipt_sha256", "receipt_bytes", "receipt_inode",
                 "receipt_device", "forensic_sha256", "forensic_bytes",
                 "forensic_inode", "forensic_device",
                 "inputs_sha256", "summary_sha256",
                 "svg_sha256")
            )
            base.need(all(getattr(options, name) is None
                          for name in forbidden),
                      "source-only graph receives no actual outcome pins")
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256,
                                  "actual complete V58 graph source")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render only three root-authorized V58 assets")
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published")
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "actual exact V58 graph inputs"),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "actual exact V58 graph summary"),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "actual exact V58 graph chart"),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True)
                base.need(raw == outputs[path],
                          "reproduce one actual V58 graph asset: " + path)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context")
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V58 overview rejected: "
                         + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V58 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise

if __name__ == "__main__":
    raise SystemExit(main())
