#!/usr/bin/env python3
"""Publish only the genuine result of the guarded, repaired Rust campaign."""

from __future__ import annotations

import argparse
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v80.py"
OUTPUT = "docs/evidence/candidate-current-overview-v80"
SCHEMA = "rebar-candidate-current-overview-v80"
V79 = {
    "source": (
        "tools/render_candidate_current_overview_v79.py",
        "b8842b64072747b5a78f6104fd9dabf31e7d9d03b96f9165783786638e8d4dca",
        55696,
        431505,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v79.inputs.json",
        "27c192d9d4f9757c4f2a19a552a2bea25b6253334b5f28399113fe2b73d422a4",
        1218955,
        431507,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v79.json",
        "608ffddb23d7b4f74c69f72b6d377bf4ee3f5a9ef617e78fb931594b05f6d1a8",
        3777178,
        431508,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v79.svg",
        "d51062fe987e0be10665f6f935a635e17dc00c43cd11ce6abe31a300cd7a7b73",
        5341,
        431509,
    ),
}
RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v13-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-"
    "original-p0-v13-failures-publication-receipt.json",
    "6f990183501953c42af374a896fad6b64f909514c731cb9de4fb37faf4d3bf86",
    6744,
    525049,
)
RECEIPT_KEYS: frozenset[str] = frozenset({
    "actual_candidate_workers",
    "actual_v19_build_archive_gzip_inflation_count",
    "actual_v19_build_archive_read_count",
    "actual_v19_build_archive_sha256",
    "actual_v19_build_contract_sha256",
    "actual_v19_build_private_root",
    "actual_v19_build_private_root_device",
    "actual_v19_build_private_root_inode",
    "actual_v19_build_protocol_sha256",
    "actual_v19_build_receipt_sha256",
    "actual_v19_build_source_sha256",
    "actual_v19_compiler_process_count",
    "actual_worker_process_ids",
    "all_four_original_targets_restored",
    "all_original_observation_vectors_complete",
    "archive",
    "attempted_suite_count",
    "benchmark_files_read",
    "campaign_contract_sha256",
    "campaign_protocol_sha256",
    "campaign_source_sha256",
    "candidate_qualified",
    "candidate_run_uses_both_complete_reference_vectors",
    "candidate_status",
    "case_execution_denominator",
    "clock_samples",
    "combined_bridge_source_bytes",
    "combined_bridge_source_sha256",
    "completed_suite_count",
    "corrected_public_adapter_bytes",
    "corrected_public_adapter_sha256",
    "corrected_reference_cache_records_sha256",
    "corrected_reference_case_count",
    "corrected_reference_process_ids",
    "corrected_reference_receipt_sha256",
    "corrected_reference_records_sha256",
    "current_overview_version",
    "distinct_worker_process_id_count",
    "duplicate_worker_process_id_count",
    "family",
    "group_atomic",
    "hidden_cases_read",
    "historical_authenticated_reference_count_before_publication",
    "historical_evidence_owner_count_before_publication",
    "holdout",
    "infrastructure_failure_count",
    "label",
    "memory",
    "missing_worker_process_id_count",
    "named_private_waiver_count",
    "native_bridge_bytes",
    "native_bridge_sha256",
    "native_engine_bytes",
    "native_engine_sha256",
    "new_repository_evidence_owner_count",
    "original_v5_producer_contract_sha256",
    "original_v5_producer_protocol_sha256",
    "original_v5_producer_source_sha256",
    "original_v5_producer_version",
    "performance",
    "power_failure_automatically_recovered",
    "preserved_previous_rust_semantic_mismatch_count",
    "preserved_previous_rust_verified_passing_case_count",
    "public_recovery_root",
    "publication_pass_means",
    "publication_status",
    "published_current_v78_inputs_sha256",
    "published_current_v78_source_sha256",
    "published_current_v78_summary_sha256",
    "published_current_v78_svg_sha256",
    "recovery_journal_sha256",
    "restoration_verified_before_publication",
    "restored_original_targets",
    "resulting_authenticated_reference_count",
    "resulting_repository_evidence_owner_count",
    "schema",
    "semantic_mismatch_count",
    "sigkill_automatically_recovered",
    "started_suite_count",
    "status",
    "suite_count",
    "timing_trials_run",
    "uncompressed_bytes",
    "uncompressed_chunk_count",
    "uncompressed_sha256",
    "undefined_behavior",
    "verified_passing_case_count",
    "winner_selected",
})
ARCHIVE_RELATIVE = (
    "repaired-rust-original-campaign-v13-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-"
    "original-p0-v13-failures.json.gz"
)
ARCHIVE_SHA256 = (
    "e54521842f0faa955052ab0336022a39b9d9f2f3f0d763f0328758ea6be743d3"
)
ARCHIVE_KEYS = frozenset({
    "device", "directory_fsync_completed", "exclusive_creation",
    "file_fsync_completed", "inode", "mode", "path", "relative",
    "same_inode_readback_verified", "sha256", "size_bytes",
    "streaming_readback_verified", "write_calls",
})
RESTORED_KEYS = frozenset({
    "bytes", "device", "inode", "mode", "nlink", "path", "relative",
    "sha256", "size_bytes", "uid",
})
RESTORED = {
    "bridge_source": (
        "candidates/rust/py_bridge.c",
        "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        175676,
        419054,
        0o600,
    ),
    "adapter": (
        "candidates/rust_candidate.py",
        "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        31151,
        428100,
        0o600,
    ),
    "engine": (
        "candidates/_rust_engine.so",
        "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
        660440,
        430563,
        0o755,
    ),
    "bridge": (
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
        144992,
        430629,
        0o755,
    ),
}


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(descriptor)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted exact owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated exact owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject extended exact owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_nlink,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_nlink,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("reject changed complete owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple:
    raw = read_fixed(V79["source"], "actually pushed complete V79 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v79")
    previous.__file__ = str(ROOT / V79["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v78, v77, v76, v75, v74, v73, v72, v71, v70, v69, modules, base = (
        previous.load_previous()
    )
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v79"
        and previous.SELF == V79["source"][0],
        "authenticate only the actual pushed V79 guarded-startup source graph",
    )
    return (
        previous, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69,
        modules, base,
    )


def authenticate_previous(
    previous: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    v76: types.ModuleType,
    v75: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V79["source"][1],
        "source_bytes": V79["source"][2],
    }
    for role, item in previous.V78.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        pins["feature_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v78, v77, v76, v75, v74, v73, v72, v71, v70, v69, modules, base,
        argparse.Namespace(**pins),
    )
    for role in ("inputs", "summary", "svg"):
        item = V79[role]
        base.need(
            assets[item[0]] == read_fixed(item, "actual complete V79 " + role),
            "reproduce the actual pushed complete V79 " + role,
        )
    old = base.document(assets[V79["summary"][0]], "complete actual V79")
    inputs = base.document(assets[V79["inputs"][0]], "complete V79 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 79
        and old["actual_current_graph_predecessor_version"] == 78
        and old["authenticated_evidence_owner_lower_bound"] == 260
        and old["authenticated_history_reference_lower_bound"] == 265
        and old["rust_v12_original_campaign_actual_worker_count"] == 13
        and old["rust_v12_original_campaign_completed_suite_count"] == 0
        and old["rust_v12_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v12_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old["rust_v13_original_campaign_candidate_matching"] == "NOT RUN"
        and old["rust_v13_original_campaign_actual_worker_count"] == 0
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["qualified_candidate_count"] == 0
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "preserve full prior failure and genuine not-yet-run corrected source",
    )
    return old, inputs


def validate_receipt(
    base: types.ModuleType,
    previous: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    receipt: object,
) -> None:
    base.need(
        len(RECEIPT_KEYS) >= 75
        and type(receipt) is dict
        and set(receipt) == RECEIPT_KEYS,
        "reject provisional, omitted, added, or fabricated V13 result evidence",
    )
    assert isinstance(receipt, dict)
    base.need(
        receipt["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v13-"
        "durable-publication-receipt"
        and receipt["status"] == "PASS"
        and receipt["publication_status"] == "PASS"
        and receipt["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and receipt["family"] == "rust"
        and receipt["label"]
        == "phase2-v19-rust-buffer-shape-root-provenance-original-p0-v13"
        and receipt["candidate_status"] in ("PASS", "FAIL"),
        "distinguish durable result publication from the actual candidate result",
    )
    base.need(
        receipt["campaign_source_sha256"] == previous.FEATURE["source"][1]
        and receipt["campaign_protocol_sha256"]
        == previous.FEATURE["protocol"][1]
        and receipt["campaign_contract_sha256"]
        == previous.FEATURE["contract"][1]
        and receipt["original_v5_producer_version"] == 5
        and receipt["original_v5_producer_source_sha256"]
        == v77.PRODUCER["source"][1]
        and receipt["original_v5_producer_protocol_sha256"]
        == v77.PRODUCER["protocol"][1]
        and receipt["original_v5_producer_contract_sha256"]
        == v77.PRODUCER["contract"][1],
        "authenticate the exact V13 corrected worker and whole original V5 suite",
    )
    base.need(
        receipt["suite_count"] == 13
        and receipt["case_execution_denominator"] == 31237
        and receipt["attempted_suite_count"] == 13
        and type(receipt["started_suite_count"]) is int
        and 0 <= receipt["started_suite_count"] <= 13
        and type(receipt["completed_suite_count"]) is int
        and 0 <= receipt["completed_suite_count"]
        <= receipt["started_suite_count"]
        and type(receipt["actual_candidate_workers"]) is int
        and receipt["actual_candidate_workers"]
        == receipt["started_suite_count"]
        and type(receipt["infrastructure_failure_count"]) is int
        and 0 <= receipt["infrastructure_failure_count"] <= 13
        and receipt["infrastructure_failure_count"]
        == receipt["started_suite_count"] - receipt["completed_suite_count"]
        and type(receipt["verified_passing_case_count"]) is int
        and 0 <= receipt["verified_passing_case_count"] <= 31237
        and receipt["named_private_waiver_count"] == 13,
        "preserve every attempted, genuinely observed, and failed original worker",
    )
    process_ids = receipt["actual_worker_process_ids"]
    base.need(
        type(process_ids) is list
        and len(process_ids) == receipt["actual_candidate_workers"]
        and all(type(pid) is int and pid > 0 for pid in process_ids)
        and len(set(process_ids)) == len(process_ids)
        and receipt["distinct_worker_process_id_count"] == len(process_ids)
        and receipt["duplicate_worker_process_id_count"] == 0
        and receipt["missing_worker_process_id_count"] == 0,
        "require each actual independent worker without invented process IDs",
    )
    base.need(
        receipt["candidate_status"] == "FAIL"
        and receipt["candidate_qualified"] is False
        and receipt["attempted_suite_count"] == 13
        and receipt["started_suite_count"] == 13
        and receipt["actual_candidate_workers"] == 13
        and receipt["actual_worker_process_ids"] == list(range(81, 94))
        and receipt["completed_suite_count"] == 0
        and receipt["infrastructure_failure_count"] == 13
        and receipt["semantic_mismatch_count"] == "NOT MEASURED"
        and receipt["verified_passing_case_count"] == 0
        and receipt["all_original_observation_vectors_complete"] is False,
        "preserve all 13 actual failed V13 workers without inventing matching",
    )
    mismatches = receipt["semantic_mismatch_count"]
    complete = receipt["completed_suite_count"] == 13
    observed_vectors = receipt["all_original_observation_vectors_complete"]
    base.need(
        type(observed_vectors) is bool
        and (
            (complete and observed_vectors is True
             and type(mismatches) is int and 0 <= mismatches <= 31237
             and receipt["verified_passing_case_count"] + mismatches == 31237)
            or (not complete and observed_vectors is False
                and (mismatches == "NOT MEASURED"
                     or type(mismatches) is int))
        ),
        "never fabricate observations, mismatches, or unexecuted passing cases",
    )
    original_pass = (
        complete and receipt["infrastructure_failure_count"] == 0
        and mismatches == 0
        and receipt["verified_passing_case_count"] == 31237
    )
    base.need(
        type(receipt["candidate_qualified"]) is bool
        and receipt["candidate_qualified"] is original_pass
        and receipt["candidate_status"] == ("PASS" if original_pass else "FAIL"),
        "do not confuse an original-suite result with whole-project qualification",
    )
    base.need(
        receipt["actual_v19_build_source_sha256"]
        == "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c"
        and receipt["actual_v19_build_protocol_sha256"]
        == "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5"
        and receipt["actual_v19_build_contract_sha256"]
        == "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46"
        and receipt["actual_v19_build_receipt_sha256"]
        == "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc"
        and receipt["actual_v19_build_archive_sha256"]
        == "c4e3971fc207af50081d920a98d29dc06b5bdce07c5e1fb19e3e6fdf99a1c1bb"
        and receipt["actual_v19_build_private_root"]
        == "/tmp/rebar-phase2-native-build-v9-rust-9m_y1apm"
        and receipt["actual_v19_build_private_root_device"] == 2049
        and receipt["actual_v19_build_private_root_inode"] == 11673243
        and receipt["actual_v19_compiler_process_count"] == 28
        and receipt["native_engine_sha256"]
        == "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
        and receipt["native_engine_bytes"] == 658344
        and receipt["native_bridge_sha256"]
        == "7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4"
        and receipt["native_bridge_bytes"] == 148832,
        "authenticate the actual first-party V19 engine only by small receipts",
    )
    base.need(
        receipt["published_current_v78_source_sha256"]
        == previous.V78["source"][1]
        and receipt["published_current_v78_inputs_sha256"]
        == previous.V78["inputs"][1]
        and receipt["published_current_v78_summary_sha256"]
        == previous.V78["summary"][1]
        and receipt["published_current_v78_svg_sha256"]
        == previous.V78["svg"][1]
        and receipt["current_overview_version"] == 78
        and receipt["historical_evidence_owner_count_before_publication"]
        == 260
        and receipt["historical_authenticated_reference_count_before_publication"]
        == 265
        and receipt["new_repository_evidence_owner_count"] == 2
        and receipt["resulting_repository_evidence_owner_count"] == 262
        and receipt["resulting_authenticated_reference_count"] == 267
        and receipt["preserved_previous_rust_semantic_mismatch_count"] == 1440
        and receipt["preserved_previous_rust_verified_passing_case_count"]
        == 14853,
        "retain the genuine predecessor, two real owners, and historical losses",
    )
    base.need(
        receipt["corrected_reference_records_sha256"]
        == "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
        and receipt["corrected_reference_cache_records_sha256"]
        == "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
        and receipt["corrected_reference_case_count"] == 6912
        and receipt["corrected_reference_process_ids"] == [81, 82]
        and receipt["corrected_reference_receipt_sha256"]
        == "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966"
        and receipt["candidate_run_uses_both_complete_reference_vectors"] is True
        and receipt["combined_bridge_source_sha256"]
        == "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
        and receipt["combined_bridge_source_bytes"] == 179961
        and receipt["corrected_public_adapter_sha256"]
        == "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
        and receipt["corrected_public_adapter_bytes"] == 31934,
        "retain both independent original references and corrected owned adapter",
    )
    base.need(
        receipt["all_four_original_targets_restored"] is True
        and receipt["restoration_verified_before_publication"] is True
        and receipt["public_recovery_root"]
        == "/tmp/rebar-phase2-repaired-rust-original-campaign-v13-"
        "phase2-v19-rust-buffer-shape-root-provenance-original-p0"
        and type(receipt["recovery_journal_sha256"]) is str
        and receipt["recovery_journal_sha256"]
        == "960baff700da119d910c39bfaf18ae9a92df96bee87060b08664817957a3b5cd"
        and receipt["power_failure_automatically_recovered"] is False
        and receipt["sigkill_automatically_recovered"] is False,
        "authenticate exact ordinary restoration without inventing crash recovery",
    )
    restored = receipt["restored_original_targets"]
    base.need(
        type(restored) is dict and set(restored) == set(RESTORED),
        "require all four original exact roles without reading candidate files",
    )
    for role, expected in RESTORED.items():
        relative, digest, size, inode, mode = expected
        actual = restored[role]
        base.need(
            type(actual) is dict
            and set(actual) == RESTORED_KEYS
            and actual["relative"] == relative
            and actual["path"] == str(ROOT / relative)
            and actual["sha256"] == digest
            and actual["bytes"] == size
            and actual["size_bytes"] == size
            and actual["device"] == 2064
            and actual["inode"] == inode
            and actual["mode"] == mode
            and actual["nlink"] == 1
            and actual["uid"] == os.geteuid(),
            "reject altered exact restored original " + role,
        )
    archive = receipt["archive"]
    base.need(
        type(archive) is dict
        and set(archive) == ARCHIVE_KEYS
        and archive["relative"] == ARCHIVE_RELATIVE
        and archive["path"]
        == str(ROOT / "oracle/phase2/evidence" / archive["relative"])
        and archive["sha256"] == ARCHIVE_SHA256
        and archive["size_bytes"] == 3141
        and archive["device"] == 2064
        and archive["inode"] == 525048
        and archive["mode"] == 0o600
        and archive["exclusive_creation"] is True
        and archive["file_fsync_completed"] is True
        and archive["directory_fsync_completed"] is True
        and archive["same_inode_readback_verified"] is True
        and archive["streaming_readback_verified"] is True
        and archive["write_calls"] == 9
        and type(receipt["uncompressed_sha256"]) is str
        and len(receipt["uncompressed_sha256"]) == 64
        and type(receipt["uncompressed_bytes"]) is int
        and receipt["uncompressed_bytes"] > 0
        and type(receipt["uncompressed_chunk_count"]) is int
        and receipt["uncompressed_chunk_count"] > 0,
        "bind archive metadata exclusively to the complete tiny public receipt",
    )
    for key in (
        "actual_v19_build_archive_gzip_inflation_count",
        "actual_v19_build_archive_read_count",
        "benchmark_files_read",
        "clock_samples",
        "hidden_cases_read",
        "timing_trials_run",
    ):
        base.need(receipt[key] == 0, "reject forbidden result effect: " + key)
    base.need(
        receipt["group_atomic"] is False
        and receipt["holdout"] == "NOT OPENED"
        and receipt["performance"] == "NOT MEASURED"
        and receipt["memory"] == "NOT MEASURED"
        and receipt["undefined_behavior"] == "NOT MEASURED"
        and receipt["winner_selected"] is False,
        "never fabricate atomic recovery, speed, memory, or opened holdout",
    )


def make_svg(receipt: dict) -> bytes:
    completed = receipt["completed_suite_count"]
    failures = receipt["infrastructure_failure_count"]
    mismatches = receipt["semantic_mismatch_count"]
    if receipt["candidate_status"] == "PASS":
        rust_detail = "31,237 original checks passed; full qualification pending"
        rust_status = "ORIGINAL TESTS PASS"
        rust_colour = "#22c55e"
    elif completed == 0:
        rust_detail = f"Retest: {failures} worker failures; no test groups completed"
        rust_status = "RETEST FAILED"
        rust_colour = "#fb7185"
    else:
        rust_detail = (
            f"Retest: {completed}/13 groups; {mismatches} differences; "
            f"{failures} worker failures"
        )
        rust_status = "NOT COMPATIBLE"
        rust_colour = "#fb7185"
    rows = (
        ("Python re", "All original reference checks pass", "BASELINE", "#22c55e"),
        ("Rust", rust_detail, rust_status, rust_colour),
        ("C", "1,230 earlier differences; corrected build passes", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "1,764 earlier differences; scanner fix not retested", "NOT COMPATIBLE", "#f59e0b"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility has not been tested", "NOT TESTED", "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="670" viewBox="0 0 1160 670" role="img" aria-labelledby="title description">',
        '<title id="title">Python and six independently written regular-expression engines</title>',
        '<desc id="description">The real repaired Rust result is taken only from an authenticated tiny public receipt. All earlier compatibility failures remain visible. Final replacement qualification, speed, and the expanded holdout are not claimed.</desc>',
        '<rect width="1160" height="670" rx="18" fill="#0b1220"/>',
        '<text x="34" y="48" fill="#f8fafc" font-size="26" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="81" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully qualified · speed NOT MEASURED</text>',
        '<line x1="34" y1="104" x2="1126" y2="104" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 142 + 47 * index
        parts.extend((
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1108" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ))
    result_line = (
        f'Actual repaired Rust: {completed}/13 test groups completed; '
        f'{failures} worker failures; differences: {mismatches}.'
    )
    parts.extend((
        '<line x1="34" y1="462" x2="1126" y2="462" stroke="#334155"/>',
        '<text x="34" y="493" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate extra checks.</text>',
        f'<text x="34" y="521" fill="{rust_colour}" font-size="14" font-family="system-ui,sans-serif">{result_line}</text>',
        '<text x="34" y="549" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Earlier Rust run: 13 startup failures; 1,440 historical differences preserved.</text>',
        '<text x="34" y="577" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Original engine files restored. No Python or external regex fallback is permitted.</text>',
        '<text x="34" y="605" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Full replacement qualification, speed, and memory: NOT MEASURED.</text>',
        '<text x="34" y="633" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final 4,194,304-case speed test: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="660" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 80 · actual corrected result only · no selected winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def build(
    previous: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    v76: types.ModuleType,
    v75: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None and options.source_bytes is not None,
        "require the exact caller-pinned actual-result graph source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "complete actual-result graph"),
        options.source_bytes,
        private=True,
    )
    for role, item in V79.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the whole actually pushed V79 " + role,
        )
    base.need(
        options.receipt_sha256 == RECEIPT[1],
        "caller-pin the whole actual corrected Rust outcome receipt",
    )
    receipt_raw = read_fixed(RECEIPT, "complete tiny real V13 result receipt")
    receipt = base.document(receipt_raw, "whole actual V13 result receipt")
    base.need(
        base.canonical(receipt) == receipt_raw,
        "reject noncanonical, partial, or duplicate-key actual result evidence",
    )
    validate_receipt(base, previous, v78, v77, receipt)
    old, previous_inputs = authenticate_previous(
        previous, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69,
        modules, base,
    )
    v5 = old["clean_original_producer_v5_source_freeze"][
        "complete_feature_contract"
    ]
    v2 = old["candidate_runtime_independence_v2_source_freeze"][
        "complete_feature_contract"
    ]
    v12 = old["rust_v12_original_campaign_source_freeze"][
        "complete_feature_contract"
    ]
    v13 = old["rust_v13_original_campaign_source_freeze"][
        "complete_feature_contract"
    ]
    previous.validate_contract(base, v78, v77, v13)
    prior_failure = old["actual_rust_v12_original_campaign"]
    prior_receipt = prior_failure["complete_publication_receipt"]
    v78.validate_receipt(base, v77, prior_receipt)
    base.need(
        receipt["campaign_source_sha256"] == v13["source_sha256"]
        and receipt["campaign_protocol_sha256"] == v13["protocol_sha256"]
        and receipt["original_v5_producer_source_sha256"]
        == v13["corrected_original_producer_source_sha256"]
        and v13["runtime_non_delegation"] == "NOT ESTABLISHED",
        "bind only the actual complete corrected runner and unchanged guard",
    )
    original_pass = receipt["candidate_status"] == "PASS"
    outcome = {
        "schema": SCHEMA + "-actual-rust-original-campaign-v13-outcome",
        "version": 13,
        "complete_publication_receipt": copy.deepcopy(receipt),
        "receipt_owner": base.synthetic_owner(RECEIPT[:3], RECEIPT[3]),
        "archive_metadata_from_receipt_only": copy.deepcopy(receipt["archive"]),
        "archive_opened_by_graph": False,
        "archive_inflated_by_graph": False,
        "archive_digest_recomputed_by_graph": False,
        "candidate_status": receipt["candidate_status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "attempted_suite_count": receipt["attempted_suite_count"],
        "started_suite_count": receipt["started_suite_count"],
        "completed_suite_count": receipt["completed_suite_count"],
        "actual_candidate_worker_count": receipt["actual_candidate_workers"],
        "actual_worker_process_ids": copy.deepcopy(
            receipt["actual_worker_process_ids"]
        ),
        "distinct_worker_process_id_count":
            receipt["distinct_worker_process_id_count"],
        "infrastructure_failure_count": receipt["infrastructure_failure_count"],
        "semantic_mismatch_count": receipt["semantic_mismatch_count"],
        "verified_passing_case_count": receipt["verified_passing_case_count"],
        "all_original_observation_vectors_complete":
            receipt["all_original_observation_vectors_complete"],
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "failure_details_in_public_receipt": False,
        "runtime_guard_attested_in_public_receipt": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_original_suite_pass": original_pass,
        "candidate_whole_project_qualified": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    changes = {
        "actual_current_graph_predecessor_version": 79,
        "authenticated_evidence_owner_lower_bound": 262,
        "authenticated_history_reference_lower_bound": 267,
        "actual_rust_v13_original_campaign": outcome,
        "rust_v13_original_campaign_candidate_matching":
            receipt["candidate_status"],
        "rust_v13_original_campaign_actual_worker_count":
            receipt["actual_candidate_workers"],
        "rust_v13_original_campaign_attempted_suite_count":
            receipt["attempted_suite_count"],
        "rust_v13_original_campaign_started_suite_count":
            receipt["started_suite_count"],
        "rust_v13_original_campaign_completed_suite_count":
            receipt["completed_suite_count"],
        "rust_v13_original_campaign_distinct_worker_count":
            receipt["distinct_worker_process_id_count"],
        "rust_v13_original_campaign_infrastructure_failure_count":
            receipt["infrastructure_failure_count"],
        "rust_v13_original_campaign_semantic_mismatch_count":
            receipt["semantic_mismatch_count"],
        "rust_v13_original_campaign_verified_passing_case_count":
            receipt["verified_passing_case_count"],
        "rust_v13_original_campaign_complete_observation_vectors":
            receipt["all_original_observation_vectors_complete"],
        "rust_v13_original_campaign_all_original_targets_restored": True,
        "rust_v13_original_campaign_publication_status": "PASS",
        "rust_v13_original_campaign_publication_pass_means":
            "DURABLE PUBLICATION ONLY",
        "rust_v13_original_campaign_runtime_no_delegation":
            "NOT ESTABLISHED",
        "rust_v13_original_campaign_original_suite_pass": original_pass,
        "rust_v13_original_campaign_candidate_qualified": False,
        "rust_v13_original_campaign_outcome_receipt_sha256": RECEIPT[1],
        "rust_v13_original_campaign_outcome_archive_sha256":
            receipt["archive"]["sha256"],
        "rust_v13_original_campaign_outcome_archive_opened_by_graph": False,
        "rust_v13_original_campaign_outcome_archive_inflated_by_graph": False,
        "rust_v13_original_campaign_runtime_guard_attested_in_receipt": False,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v79_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V79.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 80,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    input_raw = base.canonical(inputs)
    svg_raw = make_svg(receipt)
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve the reference and six independently written engine families",
    )
    for row in families:
        if row["family"] == "python":
            continue
        base.need(
            row["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ] == v5
            and row["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ] == v2
            and row["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v12
            and row["actual_rust_v12_original_campaign"][
                "complete_publication_receipt"
            ] == prior_receipt
            and row["rust_v13_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v13,
            "preserve every complete prior proof and actual loss in "
            + row["family"],
        )
        row["authenticated_evidence_owner_lower_bound"] = 262
        row["authenticated_history_reference_lower_bound"] = 267
        row["actual_rust_v13_original_campaign"] = copy.deepcopy(outcome)
        if row["family"] == "rust":
            for key, value in changes.items():
                if key.startswith("rust_v13_original_campaign_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 80,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **copy.deepcopy(changes),
    })
    suites = old["actual_complete_rust_campaign"][
        "complete_independently_authenticated_suite_results"
    ]
    witnesses = old["actual_complete_rust_campaign"][
        "earliest_genuine_mismatch_witnesses"
    ]
    base.need(
        len(suites) == 13 and len(witnesses) == 6,
        "retain all previously actually observed original suites and witnesses",
    )
    for name, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        old_campaign = layer["actual_complete_rust_campaign"]
        base.need(
            old_campaign["complete_independently_authenticated_suite_results"]
            == suites
            and old_campaign["earliest_genuine_mismatch_witnesses"] == witnesses
            and layer["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ] == v5
            and layer["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ] == v2
            and layer["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v12
            and layer["rust_v13_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v13
            and layer["actual_rust_v12_original_campaign"][
                "complete_publication_receipt"
            ] == prior_receipt
            and layer["rust_v12_original_campaign_actual_worker_count"] == 13
            and layer["rust_v12_original_campaign_completed_suite_count"] == 0
            and layer["rust_v12_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v12_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["actual_rust_v13_original_campaign"][
                "complete_publication_receipt"
            ] == receipt
            and layer["rust_v13_original_campaign_actual_worker_count"]
            == receipt["actual_candidate_workers"]
            and layer["rust_v13_original_campaign_completed_suite_count"]
            == receipt["completed_suite_count"]
            and layer["rust_v13_original_campaign_infrastructure_failure_count"]
            == receipt["infrastructure_failure_count"]
            and layer["rust_v13_original_campaign_semantic_mismatch_count"]
            == receipt["semantic_mismatch_count"]
            and layer["rust_v13_original_campaign_runtime_no_delegation"]
            == "NOT ESTABLISHED",
            "preserve complete historical and actual corrected results in " + name,
        )
    for row in families:
        if row["family"] == "python":
            continue
        base.need(
            row["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ] == v5
            and row["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ] == v2
            and row["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v12
            and row["rust_v13_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v13
            and row["actual_rust_v12_original_campaign"][
                "complete_publication_receipt"
            ] == prior_receipt
            and row["actual_rust_v13_original_campaign"][
                "complete_publication_receipt"
            ] == receipt
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "preserve all complete proof and both actual outcomes in "
            + row["family"],
        )
    base.need(
        summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_rust_verified_passing_case_count"] == 14853
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_c_verified_passing_case_count"] == 7325
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["actual_zig_verified_passing_case_count"] == 3711
        and summary["qualified_candidate_count"] == 0
        and summary["final_holdout_opened"] is False
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED",
        "never promote a single original run into whole-project qualification",
    )
    return snapshot, {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": base.canonical(summary),
        OUTPUT + ".svg": svg_raw,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"
        }
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish exactly three complete real-campaign graph owners",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(
                type(count) is int and count > 0,
                "write every complete real-campaign graph byte",
            )
            remaining = remaining[count:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "require an exact exclusively written real-outcome graph owner",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(
        path, base.digest(raw), len(raw), private=True
    )
    base.need(confirmed == raw, "reauthenticate the whole genuine result graph")


def self_test(
    previous: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    v76: types.ModuleType,
    v75: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(
        v78, v77, v76, v75, v74, v73, v72, v71, v70, v69, modules, base,
    )
    base.need(
        prior["status"] == "PASS"
        and prior["actual_current_graph_predecessor_version"] == 78
        and prior["authenticated_evidence_owner_lower_bound"] == 260
        and prior["authenticated_history_reference_lower_bound"] == 265
        and prior["previous_actual_rust_candidate_worker_count"] == 13
        and prior["previous_actual_rust_completed_suite_count"] == 0
        and prior["previous_actual_rust_infrastructure_failure_count"] == 13
        and prior["previous_actual_rust_semantic_mismatch_count"]
        == "NOT MEASURED"
        and prior["actual_corrected_candidate_workers_started"] == 0
        and prior["runtime_no_delegation"] == "NOT ESTABLISHED",
        "inherit complete frozen correction and all previously observed failures",
    )
    raw = read_fixed(RECEIPT, "whole tiny actual V13 correctness result")
    receipt = base.document(raw, "whole canonical actual V13 result")
    base.need(base.canonical(receipt) == raw, "reject noncanonical real outcome")
    validate_receipt(base, previous, v78, v77, receipt)
    cases: list[tuple[str, object]] = [("missing entire actual outcome", None)]
    for key in sorted(receipt):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        cases.append(("removed actual correctness outcome " + key, forged))
    for name, wrong in (
        ("status", "FAIL"),
        ("publication_status", "FAIL"),
        ("publication_pass_means", "CANDIDATE PASS"),
        ("suite_count", 12),
        ("case_execution_denominator", 31236),
        ("attempted_suite_count", 12),
        ("actual_candidate_workers", 14),
        ("duplicate_worker_process_id_count", 1),
        ("missing_worker_process_id_count", 1),
        ("all_four_original_targets_restored", False),
        ("restoration_verified_before_publication", False),
        ("new_repository_evidence_owner_count", 1),
        ("resulting_repository_evidence_owner_count", 261),
        ("resulting_authenticated_reference_count", 266),
        ("preserved_previous_rust_semantic_mismatch_count", 0),
        ("preserved_previous_rust_verified_passing_case_count", 31237),
        ("actual_v19_build_archive_read_count", 1),
        ("actual_v19_build_archive_gzip_inflation_count", 1),
        ("benchmark_files_read", 1),
        ("clock_samples", 1),
        ("hidden_cases_read", 1),
        ("timing_trials_run", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(receipt)
        forged[name] = wrong
        cases.append(("fabricated actual result or forbidden effect " + name, forged))
    for key in (
        "campaign_source_sha256",
        "campaign_protocol_sha256",
        "campaign_contract_sha256",
        "original_v5_producer_source_sha256",
        "original_v5_producer_protocol_sha256",
        "original_v5_producer_contract_sha256",
        "actual_v19_build_source_sha256",
        "actual_v19_build_protocol_sha256",
        "actual_v19_build_contract_sha256",
        "actual_v19_build_receipt_sha256",
        "native_engine_sha256",
        "native_bridge_sha256",
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = "0" * 64
        cases.append(("substituted actual first-party provenance " + key, forged))
    for role in RESTORED:
        forged = copy.deepcopy(receipt)
        forged["restored_original_targets"].pop(role)
        cases.append(("removed exact restored original role " + role, forged))
    for name, wrong in (
        ("sha256", "0" * 64),
        ("inode", 0),
        ("size_bytes", 0),
        ("relative", "fabricated.json.gz"),
        ("streaming_readback_verified", False),
        ("exclusive_creation", False),
    ):
        forged = copy.deepcopy(receipt)
        forged["archive"][name] = wrong
        cases.append(("fabricated unread archive metadata " + name, forged))
    candidate_forged = copy.deepcopy(receipt)
    candidate_forged["candidate_status"] = (
        "FAIL" if receipt["candidate_status"] == "PASS" else "PASS"
    )
    cases.append(("flipped genuine actual candidate verdict", candidate_forged))
    qualification_forged = copy.deepcopy(receipt)
    qualification_forged["candidate_qualified"] = (
        not receipt["candidate_qualified"]
    )
    cases.append(("flipped original-suite qualification", qualification_forged))
    for pid in receipt["actual_worker_process_ids"][:3]:
        forged = copy.deepcopy(receipt)
        forged["actual_worker_process_ids"].remove(pid)
        cases.append(("omitted genuine actual corrected worker " + str(pid), forged))
    rejected = 0
    for label, forged in cases:
        try:
            validate_receipt(base, previous, v78, v77, forged)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted fabricated actual V13 result: " + label)
    base.need(
        rejected == len(cases) and rejected >= 120,
        "reject every fabricated pass, hidden loss, false guard, and open holdout",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 80,
        "status": "PASS",
        "previous_overview_version": 79,
        "actual_current_graph_predecessor_version": 79,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": (
            prior["rejected_hostile_control_count"] + rejected
        ),
        "authenticated_evidence_owner_lower_bound": 262,
        "authenticated_history_reference_lower_bound": 267,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "previous_actual_rust_candidate_worker_count": 13,
        "previous_actual_rust_infrastructure_failure_count": 13,
        "actual_corrected_rust_candidate_worker_count_from_receipt":
            receipt["actual_candidate_workers"],
        "actual_corrected_rust_completed_suite_count_from_receipt":
            receipt["completed_suite_count"],
        "actual_corrected_rust_infrastructure_failure_count_from_receipt":
            receipt["infrastructure_failure_count"],
        "actual_corrected_rust_semantic_mismatch_count_from_receipt":
            receipt["semantic_mismatch_count"],
        "actual_corrected_rust_candidate_status_from_receipt":
            receipt["candidate_status"],
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_compressed_evidence_inflations_by_graph": 0,
        "actual_private_build_root_opens_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V79:
        parser.add_argument("--previous-" + role + "-sha256")
    parser.add_argument("--receipt-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        (
            previous, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69,
            modules, base,
        ) = load_previous()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256", "source_bytes", "receipt_sha256",
                        "inputs_sha256", "summary_sha256", "svg_sha256",
                    )
                )
                and all(
                    getattr(options, "previous_" + role + "_sha256") is None
                    for role in V79
                ),
                "source self-test cannot authorize result publication or workers",
            )
            result = self_test(
                previous, v78, v77, v76, v75, v74, v73, v72, v71, v70,
                v69, modules, base,
            )
        else:
            _, assets = build(
                previous, v78, v77, v76, v75, v74, v73, v72, v71, v70,
                v69, modules, base, options,
            )
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject invented complete actual-result output identities",
                )
                for path, raw in assets.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (
                    ("inputs", ".inputs.json"),
                    ("summary", ".json"),
                    ("svg", ".svg"),
                ):
                    path = OUTPUT + suffix
                    actual, _ = base.read_owner(
                        path,
                        base.checked(
                            getattr(options, role + "_sha256"),
                            "complete actual V80 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reproduce the complete frozen actual-result " + role,
                    )
            result = {
                "schema": SCHEMA + (
                    "-published" if options.render
                    else "-read-only-frozen-context"
                ),
                "version": 80,
                "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{
                    role + "_sha256": base.digest(raw)
                    for role, raw in (
                        ("inputs", assets[OUTPUT + ".inputs.json"]),
                        ("summary", assets[OUTPUT + ".json"]),
                        ("svg", assets[OUTPUT + ".svg"]),
                    )
                },
                "failure_receipt_sha256": RECEIPT[1],
                "previous_overview_version": 79,
                "actual_current_graph_predecessor_version": 79,
                "authenticated_evidence_owner_lower_bound": 262,
                "authenticated_history_reference_lower_bound": 267,
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "actual_candidate_workers_started_by_graph": 0,
                "actual_compiler_processes_started_by_graph": 0,
                "actual_compressed_evidence_owners_opened_by_graph": 0,
                "actual_compressed_evidence_inflations_by_graph": 0,
                "actual_private_build_root_opens_by_graph": 0,
                "actual_clock_samples_by_graph": 0,
                "actual_hidden_cases_read_by_graph": 0,
                "runtime_no_delegation": "NOT ESTABLISHED",
                "qualified_candidate_count": 0,
                "final_holdout_opened": False,
                "performance": "NOT MEASURED",
                "outputs_written": bool(options.render),
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V80 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
