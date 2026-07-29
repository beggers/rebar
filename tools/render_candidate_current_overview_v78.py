#!/usr/bin/env python3
"""Reproduce the actual failed first-party Rust run without hiding any loss."""

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
SELF = "tools/render_candidate_current_overview_v78.py"
OUTPUT = "docs/evidence/candidate-current-overview-v78"
SCHEMA = "rebar-candidate-current-overview-v78"
V77 = {
    "source": (
        "tools/render_candidate_current_overview_v77.py",
        "c0114a8ff0c4234a02e8df38c126ab3d242afeed626bc5654e12b18886e920dd",
        43873,
        431424,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v77.inputs.json",
        "18a1118afed337294ca445a51be24d410e8007b962857c412f0ba589747c026e",
        1197447,
        431425,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v77.json",
        "66e6ad03ca0b42dc971751adbc3a7caa91810602538600cf475b6b7fd14bc66d",
        3570569,
        431426,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v77.svg",
        "8e438ab789f6a3ac683fde2a7faa7138e58e0567aa6b08134bea0cd805788996",
        4826,
        431430,
    ),
}
RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v12-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-"
    "original-p0-v12-failures-publication-receipt.json",
    "6537561a46fe6b7ab294126628fa5d82c34f03c3d0bac6455112dae3eea11658",
    6744,
    524989,
)
ARCHIVE_RELATIVE = (
    "repaired-rust-original-campaign-v12-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-"
    "original-p0-v12-failures.json.gz"
)
ARCHIVE_SHA256 = (
    "5efdfc734b65402ff629f90eac9ae045f2bd4c9837a169566f092e59eb1f150a"
)
RECEIPT_KEYS = frozenset({
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
    "published_current_v76_inputs_sha256",
    "published_current_v76_source_sha256",
    "published_current_v76_summary_sha256",
    "published_current_v76_svg_sha256",
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
ARCHIVE_KEYS = frozenset({
    "device",
    "directory_fsync_completed",
    "exclusive_creation",
    "file_fsync_completed",
    "inode",
    "mode",
    "path",
    "relative",
    "same_inode_readback_verified",
    "sha256",
    "size_bytes",
    "streaming_readback_verified",
    "write_calls",
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
            raise ValueError("reject substituted complete owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject extended complete owner: " + label)
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
    raw = read_fixed(V77["source"], "actually pushed complete V77 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v77")
    previous.__file__ = str(ROOT / V77["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v76, v75, v74, v73, v72, v71, v70, v69, modules, base = (
        previous.load_previous()
    )
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v77"
        and previous.SELF == V77["source"][0],
        "authenticate only the actually pushed whole V77 predecessor",
    )
    return (
        previous, v76, v75, v74, v73, v72, v71, v70, v69, modules, base
    )


def authenticate_previous(
    previous: types.ModuleType,
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
        "source_sha256": V77["source"][1],
        "source_bytes": V77["source"][2],
    }
    for role, item in previous.V76.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        pins["feature_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v76, v75, v74, v73, v72, v71, v70, v69, modules, base,
        argparse.Namespace(**pins),
    )
    for role in ("inputs", "summary", "svg"):
        item = V77[role]
        base.need(
            assets[item[0]] == read_fixed(item, "actual complete V77 " + role),
            "reproduce the actual pushed complete V77 " + role,
        )
    old = base.document(assets[V77["summary"][0]], "complete actual V77")
    inputs = base.document(assets[V77["inputs"][0]], "complete V77 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 77
        and old["actual_current_graph_predecessor_version"] == 76
        and old["authenticated_evidence_owner_lower_bound"] == 255
        and old["authenticated_history_reference_lower_bound"] == 260
        and old["rust_v12_original_campaign_candidate_matching"] == "NOT RUN"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["qualified_candidate_count"] == 0
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "preserve the genuine unrun predecessor without inventing any pass",
    )
    return old, inputs


def validate_receipt(
    base: types.ModuleType,
    previous: types.ModuleType,
    receipt: object,
) -> None:
    base.need(
        type(receipt) is dict and set(receipt) == RECEIPT_KEYS,
        "reject omitted, added, or substituted actual Rust outcome fields",
    )
    assert isinstance(receipt, dict)
    base.need(
        receipt["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v12-"
        "durable-publication-receipt"
        and receipt["status"] == "PASS"
        and receipt["publication_status"] == "PASS"
        and receipt["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and receipt["family"] == "rust"
        and receipt["label"]
        == "phase2-v19-rust-buffer-shape-root-provenance-original-p0-v12"
        and receipt["candidate_status"] == "FAIL"
        and receipt["candidate_qualified"] is False,
        "distinguish durable evidence publication from an actually failing engine",
    )
    base.need(
        receipt["suite_count"] == 13
        and receipt["case_execution_denominator"] == 31237
        and receipt["actual_candidate_workers"] == 13
        and receipt["attempted_suite_count"] == 13
        and receipt["started_suite_count"] == 13
        and receipt["completed_suite_count"] == 0
        and receipt["infrastructure_failure_count"] == 13
        and receipt["semantic_mismatch_count"] == "NOT MEASURED"
        and receipt["verified_passing_case_count"] == 0
        and receipt["all_original_observation_vectors_complete"] is False
        and receipt["actual_worker_process_ids"] == list(range(81, 94))
        and receipt["distinct_worker_process_id_count"] == 13
        and receipt["duplicate_worker_process_id_count"] == 0
        and receipt["missing_worker_process_id_count"] == 0
        and receipt["named_private_waiver_count"] == 13,
        "preserve all 13 genuine startup failures without claiming measured matches",
    )
    base.need(
        receipt["campaign_source_sha256"] == previous.FEATURE["source"][1]
        and receipt["campaign_protocol_sha256"]
        == previous.FEATURE["protocol"][1]
        and receipt["campaign_contract_sha256"]
        == previous.FEATURE["contract"][1]
        and receipt["original_v5_producer_version"] == 5
        and receipt["original_v5_producer_source_sha256"]
        == previous.PRODUCER["source"][1]
        and receipt["original_v5_producer_protocol_sha256"]
        == previous.PRODUCER["protocol"][1]
        and receipt["original_v5_producer_contract_sha256"]
        == previous.PRODUCER["contract"][1],
        "bind the real V12 run to the full unchanged first-party V5 oracle",
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
        "authenticate actual independent V19 provenance using receipts alone",
    )
    base.need(
        receipt["published_current_v76_source_sha256"]
        == previous.V76["source"][1]
        and receipt["published_current_v76_inputs_sha256"]
        == previous.V76["inputs"][1]
        and receipt["published_current_v76_summary_sha256"]
        == previous.V76["summary"][1]
        and receipt["published_current_v76_svg_sha256"]
        == previous.V76["svg"][1]
        and receipt["current_overview_version"] == 76
        and receipt["historical_evidence_owner_count_before_publication"]
        == 255
        and receipt["historical_authenticated_reference_count_before_publication"]
        == 260
        and receipt["new_repository_evidence_owner_count"] == 2
        and receipt["resulting_repository_evidence_owner_count"] == 257
        and receipt["resulting_authenticated_reference_count"] == 262
        and receipt["preserved_previous_rust_semantic_mismatch_count"] == 1440
        and receipt["preserved_previous_rust_verified_passing_case_count"]
        == 14853,
        "retain both durable new owners and the previous real Rust observations",
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
        "preserve both independent original references and real source identities",
    )
    base.need(
        receipt["all_four_original_targets_restored"] is True
        and receipt["restoration_verified_before_publication"] is True
        and receipt["public_recovery_root"]
        == "/tmp/rebar-phase2-repaired-rust-original-campaign-v12-"
        "phase2-v19-rust-buffer-shape-root-provenance-original-p0"
        and receipt["recovery_journal_sha256"]
        == "c099c02079d813ed63c8139b432426ce40e7611f410bd68191ab4ef1a566aed1"
        and receipt["power_failure_automatically_recovered"] is False
        and receipt["sigkill_automatically_recovered"] is False,
        "prove the exact actually reported restoration without inventing crash safety",
    )
    restored = receipt["restored_original_targets"]
    base.need(
        type(restored) is dict and set(restored) == set(RESTORED),
        "require every exact original native role without reading candidate files",
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
            "reject a fabricated original recovery role: " + role,
        )
    archive = receipt["archive"]
    base.need(
        type(archive) is dict
        and set(archive) == ARCHIVE_KEYS
        and archive["relative"] == ARCHIVE_RELATIVE
        and archive["path"]
        == str(ROOT / "oracle/phase2/evidence" / ARCHIVE_RELATIVE)
        and archive["sha256"] == ARCHIVE_SHA256
        and archive["size_bytes"] == 3140
        and archive["device"] == 2064
        and archive["inode"] == 524988
        and archive["mode"] == 0o600
        and archive["exclusive_creation"] is True
        and archive["file_fsync_completed"] is True
        and archive["directory_fsync_completed"] is True
        and archive["same_inode_readback_verified"] is True
        and archive["streaming_readback_verified"] is True
        and archive["write_calls"] == 9
        and receipt["uncompressed_sha256"]
        == "525c720396e9599191c34cafd2a527c5fa9bbf18a681ffebf1b2d5d1c5e3ab71"
        and receipt["uncompressed_bytes"] == 13639
        and receipt["uncompressed_chunk_count"] == 1483,
        "authenticate archive metadata from the tiny receipt without opening it",
    )
    for key in (
        "actual_v19_build_archive_gzip_inflation_count",
        "actual_v19_build_archive_read_count",
        "benchmark_files_read",
        "clock_samples",
        "hidden_cases_read",
        "timing_trials_run",
    ):
        base.need(receipt[key] == 0, "reject forbidden actual run effect: " + key)
    base.need(
        receipt["group_atomic"] is False
        and receipt["holdout"] == "NOT OPENED"
        and receipt["performance"] == "NOT MEASURED"
        and receipt["memory"] == "NOT MEASURED"
        and receipt["undefined_behavior"] == "NOT MEASURED"
        and receipt["winner_selected"] is False,
        "never invent measured correctness, speed, memory, or an opened holdout",
    )


def make_svg() -> bytes:
    rows = (
        ("Python re", "All original reference checks pass", "BASELINE", "#22c55e"),
        (
            "Rust",
            "Retest: 13 worker failures; 1,440 earlier differences",
            "RETEST FAILED",
            "#fb7185",
        ),
        ("C", "1,230 earlier differences; corrected build passes", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "1,764 earlier differences; scanner fix not retested", "NOT COMPATIBLE", "#f59e0b"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility has not been tested", "NOT TESTED", "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="644" viewBox="0 0 1120 644" role="img" aria-labelledby="title description">',
        '<title id="title">Python and six independently written regular-expression engines</title>',
        '<desc id="description">The actual Rust retest started all thirteen workers, but all failed before matching. Historical compatibility failures are preserved. No engine is qualified, no speed is measured, and the expanded holdout is unopened.</desc>',
        '<rect width="1120" height="644" rx="18" fill="#0b1220"/>',
        '<text x="34" y="48" fill="#f8fafc" font-size="26" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="81" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="104" x2="1086" y2="104" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 142 + 47 * index
        parts.extend((
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1068" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ))
    parts.extend((
        '<line x1="34" y1="462" x2="1086" y2="462" stroke="#334155"/>',
        '<text x="34" y="493" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate extra checks.</text>',
        '<text x="34" y="521" fill="#fda4af" font-size="14" font-family="system-ui,sans-serif">Actual Rust retest: 13 workers started; 13 startup failures; 0 test groups completed.</text>',
        '<text x="34" y="549" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">New Rust matching: NOT MEASURED. Its earlier 1,440 differences remain on record.</text>',
        '<text x="34" y="577" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Original engine files restored. No Python matcher or external regex fallback is permitted.</text>',
        '<text x="34" y="605" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final 4,194,304-case speed test: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="630" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 78 · real Rust failure preserved · no measured winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def build(
    previous: types.ModuleType,
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
        "require the complete caller-pinned actual-outcome graph source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "complete actual-outcome graph"),
        options.source_bytes,
        private=True,
    )
    for role, item in V77.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the exact actually pushed V77 " + role,
        )
    base.need(
        options.receipt_sha256 == RECEIPT[1],
        "caller-pin the exact whole durable actual-failure receipt",
    )
    receipt_raw = read_fixed(RECEIPT, "tiny complete actual Rust failure receipt")
    receipt = base.document(receipt_raw, "tiny canonical Rust failure receipt")
    base.need(
        base.canonical(receipt) == receipt_raw,
        "reject duplicate-key, partial, or noncanonical actual failure evidence",
    )
    validate_receipt(base, previous, receipt)
    old, previous_inputs = authenticate_previous(
        previous, v76, v75, v74, v73, v72, v71, v70, v69, modules, base,
    )
    v5 = old["clean_original_producer_v5_source_freeze"][
        "complete_feature_contract"
    ]
    v2 = old["candidate_runtime_independence_v2_source_freeze"][
        "complete_feature_contract"
    ]
    v12_source = old["rust_v12_original_campaign_source_freeze"]
    v12 = v12_source["complete_feature_contract"]
    previous.validate_contract(base, v12)
    base.need(
        receipt["campaign_source_sha256"] == v12["source_sha256"]
        and receipt["campaign_protocol_sha256"] == v12["protocol_sha256"]
        and receipt["original_v5_producer_source_sha256"]
        == v12["corrected_original_producer_source_sha256"]
        and receipt["original_v5_producer_contract_sha256"]
        == v12["corrected_original_producer_contract_sha256"]
        and v12["runtime_non_delegation"] == "NOT ESTABLISHED",
        "join the actual outcome to the entire independent V12, V5, and guard",
    )
    proof = {
        "schema": SCHEMA + "-actual-rust-original-campaign-v12-outcome",
        "version": 12,
        "complete_publication_receipt": copy.deepcopy(receipt),
        "receipt_owner": base.synthetic_owner(RECEIPT[:3], RECEIPT[3]),
        "archive_metadata_from_receipt_only": copy.deepcopy(receipt["archive"]),
        "archive_opened_by_graph": False,
        "archive_inflated_by_graph": False,
        "archive_digest_recomputed_by_graph": False,
        "candidate_status": "FAIL",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "completed_suite_count": 0,
        "actual_candidate_worker_count": 13,
        "actual_worker_process_ids": list(range(81, 94)),
        "distinct_worker_process_id_count": 13,
        "infrastructure_failure_count": 13,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": 0,
        "all_original_observation_vectors_complete": False,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "failure_details_in_public_receipt": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    changes = {
        "actual_current_graph_predecessor_version": 77,
        "authenticated_evidence_owner_lower_bound": 257,
        "authenticated_history_reference_lower_bound": 262,
        "actual_rust_v12_original_campaign": proof,
        "rust_v12_original_campaign_candidate_matching":
            "FAIL; 13 WORKER STARTUP FAILURES",
        "rust_v12_original_campaign_actual_worker_count": 13,
        "rust_v12_original_campaign_attempted_suite_count": 13,
        "rust_v12_original_campaign_started_suite_count": 13,
        "rust_v12_original_campaign_completed_suite_count": 0,
        "rust_v12_original_campaign_distinct_worker_count": 13,
        "rust_v12_original_campaign_infrastructure_failure_count": 13,
        "rust_v12_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v12_original_campaign_verified_passing_case_count": 0,
        "rust_v12_original_campaign_complete_observation_vectors": False,
        "rust_v12_original_campaign_all_original_targets_restored": True,
        "rust_v12_original_campaign_publication_status": "PASS",
        "rust_v12_original_campaign_publication_pass_means":
            "DURABLE PUBLICATION ONLY",
        "rust_v12_original_campaign_runtime_no_delegation": "NOT ESTABLISHED",
        "rust_v12_original_campaign_candidate_qualified": False,
        "rust_v12_original_campaign_failure_receipt_sha256": RECEIPT[1],
        "rust_v12_original_campaign_failure_archive_sha256": ARCHIVE_SHA256,
        "rust_v12_original_campaign_failure_archive_opened_by_graph": False,
        "rust_v12_original_campaign_failure_archive_inflated_by_graph": False,
        "rust_v12_original_campaign_failure_details_in_public_receipt": False,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v77_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V77.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 78,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve the baseline and every independently written engine family",
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
            ] == v2,
            "preserve complete original oracle and anti-delegation proof for "
            + row["family"],
        )
        row["authenticated_evidence_owner_lower_bound"] = 257
        row["authenticated_history_reference_lower_bound"] = 262
        row["rust_v12_original_campaign_source_freeze"] = (
            copy.deepcopy(v12_source)
        )
        row["actual_rust_v12_original_campaign"] = copy.deepcopy(proof)
        if row["family"] == "rust":
            for key, value in changes.items():
                if key.startswith("rust_v12_original_campaign_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 78,
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
    historical = old["actual_complete_rust_campaign"]
    suites = historical["complete_independently_authenticated_suite_results"]
    witnesses = historical["earliest_genuine_mismatch_witnesses"]
    base.need(
        len(suites) == 13 and len(witnesses) == 6,
        "retain all actual historical original workers and mismatch witnesses",
    )
    for name, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        observed = layer["actual_complete_rust_campaign"]
        base.need(
            observed["complete_independently_authenticated_suite_results"]
            == suites
            and observed["earliest_genuine_mismatch_witnesses"] == witnesses
            and layer["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ] == v5
            and layer["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ] == v2
            and layer["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v12
            and layer["actual_rust_v12_original_campaign"][
                "complete_publication_receipt"
            ] == receipt
            and layer["rust_v12_original_campaign_actual_worker_count"] == 13
            and layer["rust_v12_original_campaign_completed_suite_count"] == 0
            and layer["rust_v12_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v12_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["rust_v12_original_campaign_runtime_no_delegation"]
            == "NOT ESTABLISHED",
            "preserve whole outcome, history, oracle, and safety proof in " + name,
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
            ] == receipt
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "preserve all complete first-party evidence in " + row["family"],
        )
    rust = next(row for row in families if row["family"] == "rust")
    base.need(
        rust["rust_v12_original_campaign_actual_worker_count"] == 13
        and rust["rust_v12_original_campaign_completed_suite_count"] == 0
        and rust["rust_v12_original_campaign_infrastructure_failure_count"]
        == 13
        and rust["rust_v12_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_rust_verified_passing_case_count"] == 14853
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_c_verified_passing_case_count"] == 7325
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["actual_zig_verified_passing_case_count"] == 3711
        and summary["rust_native_build_v19_status"] == "PASS"
        and summary["rust_native_build_v19_actual_compiler_process_count"] == 28
        and summary["qualified_candidate_count"] == 0
        and summary["final_holdout_opened"] is False
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED",
        "preserve old measured failures and report the new real failure honestly",
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
        "publish only the three exact complete truthful actual-outcome graphs",
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
                "write every complete actual-outcome graph byte",
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
            "require an exact exclusively created actual-outcome evidence owner",
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
    base.need(
        confirmed == raw,
        "reauthenticate the exclusively written truthful actual-outcome graph",
    )


def self_test(
    previous: types.ModuleType,
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
        v76, v75, v74, v73, v72, v71, v70, v69, modules, base
    )
    base.need(
        prior["status"] == "PASS"
        and prior["actual_current_graph_predecessor_version"] == 76
        and prior["authenticated_evidence_owner_lower_bound"] == 255
        and prior["authenticated_history_reference_lower_bound"] == 260
        and prior["candidate_matching"] == "NOT RUN"
        and prior["runtime_no_delegation"] == "NOT ESTABLISHED",
        "inherit every independent predecessor source and anti-delegation gate",
    )
    raw = read_fixed(RECEIPT, "actual tiny public full Rust failure receipt")
    receipt = base.document(raw, "actual tiny full canonical failure receipt")
    base.need(
        base.canonical(receipt) == raw,
        "reject noncanonical or incomplete actual Rust failure receipt",
    )
    validate_receipt(base, previous, receipt)
    cases: list[tuple[str, object]] = [("missing complete actual receipt", None)]
    for key in sorted(receipt):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        cases.append(("removed actual published outcome field " + key, forged))
    for name, wrong in (
        ("status", "FAIL"),
        ("publication_status", "FAIL"),
        ("publication_pass_means", "CANDIDATE PASS"),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("suite_count", 12),
        ("case_execution_denominator", 31236),
        ("actual_candidate_workers", 12),
        ("attempted_suite_count", 12),
        ("started_suite_count", 12),
        ("completed_suite_count", 13),
        ("infrastructure_failure_count", 0),
        ("semantic_mismatch_count", 0),
        ("semantic_mismatch_count", "PASS"),
        ("verified_passing_case_count", 31237),
        ("all_original_observation_vectors_complete", True),
        ("distinct_worker_process_id_count", 12),
        ("duplicate_worker_process_id_count", 1),
        ("missing_worker_process_id_count", 1),
        ("all_four_original_targets_restored", False),
        ("restoration_verified_before_publication", False),
        ("new_repository_evidence_owner_count", 1),
        ("resulting_repository_evidence_owner_count", 256),
        ("resulting_authenticated_reference_count", 261),
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
        ("memory", "MEASURED"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(receipt)
        forged[name] = wrong
        cases.append(("fabricated actual run outcome " + name, forged))
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
        "recovery_journal_sha256",
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = "0" * 64
        cases.append(("substituted actual complete provenance " + key, forged))
    for role in RESTORED:
        forged = copy.deepcopy(receipt)
        forged["restored_original_targets"].pop(role)
        cases.append(("removed actual restored original role " + role, forged))
    for name, wrong in (
        ("sha256", "0" * 64),
        ("inode", 524989),
        ("size_bytes", 0),
        ("relative", "fabricated.json.gz"),
        ("streaming_readback_verified", False),
        ("exclusive_creation", False),
    ):
        forged = copy.deepcopy(receipt)
        forged["archive"][name] = wrong
        cases.append(("fabricated unread archive metadata " + name, forged))
    for pid in (81, 87, 93):
        forged = copy.deepcopy(receipt)
        forged["actual_worker_process_ids"].remove(pid)
        cases.append(("omitted actual failed worker " + str(pid), forged))
    rejected = 0
    for label, forged in cases:
        try:
            validate_receipt(base, previous, forged)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted fabricated actual Rust result: " + label)
    base.need(
        rejected == len(cases) and rejected >= 125,
        "reject every fabricated pass, omitted failure, weak proof, or holdout",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 78,
        "status": "PASS",
        "previous_overview_version": 77,
        "actual_current_graph_predecessor_version": 77,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": (
            prior["rejected_hostile_control_count"] + rejected
        ),
        "authenticated_evidence_owner_lower_bound": 257,
        "authenticated_history_reference_lower_bound": 262,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "actual_rust_candidate_worker_count_from_receipt": 13,
        "actual_rust_completed_suite_count_from_receipt": 0,
        "actual_rust_infrastructure_failure_count_from_receipt": 13,
        "actual_rust_semantic_mismatch_count_from_receipt": "NOT MEASURED",
        "actual_rust_verified_passing_case_count_from_receipt": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_compressed_evidence_inflations_by_graph": 0,
        "actual_private_build_root_opens_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "candidate_matching": "FAIL; 13 WORKER STARTUP FAILURES",
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
    for role in V77:
        parser.add_argument("--previous-" + role + "-sha256")
    parser.add_argument("--receipt-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v76, v75, v74, v73, v72, v71, v70, v69, modules, base = (
            load_previous()
        )
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
                    for role in V77
                ),
                "source self-test never authorizes graph output or candidate work",
            )
            result = self_test(
                previous, v76, v75, v74, v73, v72, v71, v70, v69, modules,
                base,
            )
        else:
            _, assets = build(
                previous, v76, v75, v74, v73, v72, v71, v70, v69, modules,
                base, options,
            )
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject invented actual-outcome output identities",
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
                            "complete actual-outcome " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reproduce the complete exact actual-outcome " + role,
                    )
            result = {
                "schema": SCHEMA + (
                    "-published" if options.render
                    else "-read-only-frozen-context"
                ),
                "version": 78,
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
                "previous_overview_version": 77,
                "actual_current_graph_predecessor_version": 77,
                "authenticated_evidence_owner_lower_bound": 257,
                "authenticated_history_reference_lower_bound": 262,
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "actual_rust_candidate_worker_count_from_receipt": 13,
                "actual_rust_completed_suite_count_from_receipt": 0,
                "actual_rust_infrastructure_failure_count_from_receipt": 13,
                "actual_rust_semantic_mismatch_count_from_receipt":
                    "NOT MEASURED",
                "actual_candidate_workers_started_by_graph": 0,
                "actual_compiler_processes_started_by_graph": 0,
                "actual_compressed_evidence_owners_opened_by_graph": 0,
                "actual_compressed_evidence_inflations_by_graph": 0,
                "actual_private_build_root_opens_by_graph": 0,
                "actual_clock_samples_by_graph": 0,
                "actual_hidden_cases_read_by_graph": 0,
                "candidate_matching": "FAIL; 13 WORKER STARTUP FAILURES",
                "runtime_no_delegation": "NOT ESTABLISHED",
                "qualified_candidate_count": 0,
                "final_holdout_opened": False,
                "performance": "NOT MEASURED",
                "outputs_written": bool(options.render),
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V78 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
