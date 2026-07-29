#!/usr/bin/env python3
"""Publish the actual incomplete Rust result without erasing any prior result."""

from __future__ import annotations

import argparse
import base64
import binascii
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v84.py"
OUTPUT = "docs/evidence/candidate-current-overview-v84"
SCHEMA = "rebar-candidate-current-overview-v84"
ACTUAL_KEY = "actual_rust_v15_original_campaign"
ACTUAL_POOL_SCHEMA = SCHEMA + "-lossless-complete-actual-outcome-pool-v1"
ACTUAL_REFERENCE_SCHEMA = SCHEMA + "-complete-actual-outcome-reference-v1"
V83 = {
    "source": (
        "tools/render_candidate_current_overview_v83.py",
        "0d9424fd52b73908e9e2cc46d7d01637fd8435e8ce34df6cce62d2006845c57c",
        66060,
        431615,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v83.inputs.json",
        "bf4a2c72bb530dbeb8ac5e1c5995a3f8fcc56412303eff80fff7f3f076b0d68d",
        1285630,
        431617,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v83.json",
        "4ac765869b885d93fe648b5bb71ce1fcdcbbc5d5a9b5eb0896f28a33209293fd",
        3690560,
        431618,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v83.svg",
        "71517916fc6cbab43ebb9039d7f8b9249d275e388a218eb00ba421b376376b77",
        5723,
        431620,
    ),
}
RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v15-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-"
    "original-p0-v15-failures-publication-receipt.json",
    "5b1cfdc72f88c3a847f65f5a06da77cd27557ca2c2306320b6c8d44a91e28578",
    18510,
    525117,
)
ARCHIVE_RELATIVE = (
    "repaired-rust-original-campaign-v15-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-"
    "original-p0-v15-failures.json.gz"
)
ARCHIVE_SHA256 = (
    "5a37a942a2404529f8e0aeb3f5d512d0433e2bf52333f11cfd72b5127440fa5f"
)
FIRST_STDERR_SHA256 = (
    "820507908b62a191e52be17c646e75c324b365b1c77682d5060c64f40bca156c"
)
FIRST_TRACEBACK_SHA256 = (
    "bdfd444430a78e04ce09047720c5758683408bfdd0681ad92f41b2932dc3a860"
)
EMPTY_STDOUT_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
ACTUAL_PIDS = (81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 187, 188, 189)
FAILURES = (
    (
        "original_bounded_v5",
        81,
        "820507908b62a191e52be17c646e75c324b365b1c77682d5060c64f40bca156c",
        4629,
    ),
    (
        "public_v3",
        82,
        "bb418c10be66975b613357e11367e2966be6aab4d477dee70ef3ba262fe92f12",
        5173,
    ),
    (
        "scanner_v3",
        83,
        "366f2d4167d727049f0d7222397f1f7c49b0805439e07af791428a01c8609ab7",
        4370,
    ),
    (
        "buffer_v3",
        84,
        "e9aa899ff9be8eb94c04b823bc281580ffaad715276824cc214f12af2fd949a3",
        4369,
    ),
    (
        "subinterpreter_v2",
        187,
        "94dd9926651280bd92dd9b0b85a5d5b9d8f88b4a9db2eb4419e9ab26246a03b8",
        4372,
    ),
)
STREAM_KEYS = frozenset({
    "available",
    "base64",
    "capture_limit_bytes",
    "captured_size_bytes",
    "category",
    "complete",
    "limit_bytes",
    "sha256",
    "size_bytes",
    "source_sha256",
    "source_size_bytes",
    "truncated",
})
TRACEBACK_KEYS = frozenset({
    "capture_limit_bytes",
    "captured_size_bytes",
    "complete",
    "source_sha256",
    "source_size_bytes",
    "text",
    "truncated",
})


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
            raise ValueError("reject substituted whole V84 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated whole V84 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject extended whole V84 owner: " + label)
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
            raise ValueError("reject changed whole V84 owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple[types.ModuleType, types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V83["source"], "whole independently pushed V83 graph")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v83")
    previous.__file__ = str(ROOT / V83["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v83"
        and previous.SELF == V83["source"][0]
        and len(chain) == 15,
        "load the exact whole pushed V83 registry and complete history chain",
    )
    return previous, v82, chain, base


def authenticate_previous(
    previous: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V83["source"][1],
        "source_bytes": V83["source"][2],
    }
    for role, item in previous.V82.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        pins["feature_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(v82, chain, base, argparse.Namespace(**pins))
    for role in ("inputs", "summary", "svg"):
        item = V83[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole committed V83 " + role),
            "reconstruct every byte of the exact committed V83 " + role,
        )
    old = base.document(assets[V83["summary"][0]], "whole committed V83 summary")
    inputs = base.document(assets[V83["inputs"][0]], "whole committed V83 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 83
        and inputs["version"] == 83
        and old["actual_current_graph_predecessor_version"] == 82
        and old["authenticated_evidence_owner_lower_bound"] == 270
        and old["authenticated_history_reference_lower_bound"] == 275
        and old["lossless_family_evidence_pool_entry_count"] == 9
        and old["lossless_family_references_per_family"] == 9
        and old["lossless_family_reconstruction_status"] == "PASS"
        and old["lossless_family_previous_byte_identity_status"] == "PASS"
        and old["rust_v12_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v13_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v14_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v15_original_campaign_candidate_matching"] == "NOT RUN"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["qualified_candidate_count"] == 0
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "retain the exact nine-proof baseline and three actual prior losses",
    )
    full_documents = {
        key: copy.deepcopy(old[key]) for key in previous.PROOF_KEYS
    }
    previous.validate_pool(
        base, old["lossless_family_evidence_pool"], full_documents
    )
    return old, inputs


def validate_stream(
    base: types.ModuleType,
    stream: object,
    *,
    category: str,
    expected_sha256: str,
    expected_bytes: int,
    expected_budget: int,
) -> bytes:
    base.need(
        type(stream) is dict
        and set(stream) == STREAM_KEYS
        and stream["category"] == category
        and stream["available"] is True
        and stream["complete"] is True
        and stream["truncated"] is False
        and stream["capture_limit_bytes"] == 65536
        and stream["limit_bytes"] == expected_budget
        and stream["sha256"] == expected_sha256
        and stream["source_sha256"] == expected_sha256
        and stream["size_bytes"] == expected_bytes
        and stream["source_size_bytes"] == expected_bytes
        and stream["captured_size_bytes"] == expected_bytes
        and type(stream["base64"]) is str,
        "require the entire actual public child stream: " + category,
    )
    assert isinstance(stream, dict)
    try:
        raw = base64.b64decode(stream["base64"], validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("reject invalid public child " + category) from error
    base.need(
        len(raw) == expected_bytes
        and hashlib.sha256(raw).hexdigest() == expected_sha256,
        "recompute every exact public actual child byte: " + category,
    )
    return raw


def validate_receipt(
    base: types.ModuleType,
    previous: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    old: dict,
    receipt: object,
) -> None:
    v81, v80, v79, v78, v77 = chain[:5]
    old_published = {
        "published_current_v80_" + role + "_sha256" for role in previous.V82
    }
    new_published = {
        "published_current_v82_" + role + "_sha256" for role in previous.V82
    }
    expected_keys = (v82.RECEIPT_KEYS - old_published) | new_published
    base.need(
        len(expected_keys) == 91
        and type(receipt) is dict
        and set(receipt) == expected_keys,
        "reject incomplete, extra, swapped, or provisional whole V15 outcome",
    )
    assert isinstance(receipt, dict)
    base.need(
        receipt["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v15-"
        "durable-publication-receipt"
        and receipt["status"] == "PASS"
        and receipt["publication_status"] == "PASS"
        and receipt["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and receipt["family"] == "rust"
        and receipt["label"]
        == "phase2-v19-rust-buffer-shape-root-provenance-original-p0-v15"
        and receipt["candidate_status"] == "FAIL"
        and receipt["candidate_qualified"] is False,
        "never mistake durable outcome publication for a compatible candidate",
    )
    base.need(
        all(
            receipt["campaign_" + role + "_sha256"] == item[1]
            for role, item in previous.FEATURE.items()
        )
        and receipt["original_v5_producer_version"] == 5
        and all(
            receipt["original_v5_producer_" + role + "_sha256"] == item[1]
            for role, item in v77.PRODUCER.items()
        ),
        "pin the genuine frozen native repair and complete original Python tests",
    )
    base.need(
        receipt["suite_count"] == 13
        and receipt["case_execution_denominator"] == 31237
        and receipt["attempted_suite_count"] == 13
        and receipt["started_suite_count"] == 13
        and receipt["actual_candidate_workers"] == 13
        and receipt["completed_suite_count"] == 8
        and receipt["infrastructure_failure_count"] == 5
        and receipt["started_suite_count"]
        == receipt["completed_suite_count"] + receipt["infrastructure_failure_count"]
        and receipt["semantic_mismatch_count"] == "NOT MEASURED"
        and receipt["verified_passing_case_count"] == 12942
        and receipt["all_original_observation_vectors_complete"] is False
        and receipt["named_private_waiver_count"] == 13,
        "retain the actual 8 completed groups, 12,942 checks, and five failures",
    )
    pids = receipt["actual_worker_process_ids"]
    base.need(
        type(pids) is list
        and pids == list(ACTUAL_PIDS)
        and len(set(pids)) == 13
        and receipt["distinct_worker_process_id_count"] == 13
        and receipt["duplicate_worker_process_id_count"] == 0
        and receipt["missing_worker_process_id_count"] == 0,
        "retain every actual unique worker instead of inventing completions",
    )
    base.need(
        all(
            receipt["published_current_v82_" + role + "_sha256"] == item[1]
            for role, item in previous.V82.items()
        )
        and receipt["current_overview_version"] == 82
        and receipt["historical_evidence_owner_count_before_publication"]
        == old["authenticated_evidence_owner_lower_bound"]
        and receipt["historical_authenticated_reference_count_before_publication"]
        == old["authenticated_history_reference_lower_bound"]
        and receipt["new_repository_evidence_owner_count"] == 2
        and receipt["resulting_repository_evidence_owner_count"]
        == old["authenticated_evidence_owner_lower_bound"] + 2
        and receipt["resulting_authenticated_reference_count"]
        == old["authenticated_history_reference_lower_bound"] + 2
        and receipt["resulting_repository_evidence_owner_count"] == 272
        and receipt["resulting_authenticated_reference_count"] == 277
        and receipt["preserved_previous_rust_semantic_mismatch_count"] == 1440
        and receipt["preserved_previous_rust_verified_passing_case_count"]
        == 14853,
        "derive 272/277 from exactly two genuine durable actual result owners",
    )
    contract = old["rust_v15_original_campaign_source_freeze"][
        "complete_feature_contract"
    ]
    previous.validate_contract(base, v82, chain, old, contract)
    for role in ("source", "protocol", "contract", "receipt"):
        base.need(
            receipt["actual_v19_build_" + role + "_sha256"]
            == contract["actual_v19_build_" + role + "_sha256"],
            "retain native build provenance exclusively from prior evidence: "
            + role,
        )
    base.need(
        receipt["actual_v19_build_archive_sha256"]
        == contract["actual_v19_build_archive_metadata_sha256"]
        and receipt["actual_v19_build_private_root"]
        == contract["actual_v19_private_build_root"]
        and receipt["actual_v19_build_private_root_device"]
        == contract["actual_v19_private_build_root_device"]
        and receipt["actual_v19_build_private_root_inode"]
        == contract["actual_v19_private_build_root_inode"]
        and receipt["actual_v19_compiler_process_count"]
        == contract["actual_v19_compiler_process_count"]
        and receipt["native_engine_sha256"]
        == contract["actual_v19_native_engine_sha256"]
        and receipt["native_engine_bytes"]
        == contract["actual_v19_native_engine_bytes"]
        and receipt["native_bridge_sha256"]
        == contract["actual_v19_native_bridge_sha256"]
        and receipt["native_bridge_bytes"]
        == contract["actual_v19_native_bridge_bytes"],
        "never open, load, stat, or recreate an actual private native build",
    )
    base.need(
        receipt["corrected_reference_records_sha256"]
        == contract["reference_records_sha256"]
        and receipt["corrected_reference_cache_records_sha256"]
        == contract["reference_cache_records_sha256"]
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
        "preserve full frozen references and actual authenticated owned sources",
    )
    capture = receipt["worker_failure_capture"]
    base.need(
        type(capture) is dict
        and set(capture) == v82.CAPTURE_KEYS
        and capture["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v15-"
        "complete-bounded-worker-failure-capture"
        and capture["actual_failure_count"] == 5
        and capture["all_failure_metadata_preserved"] is True
        and capture["diagnostic_stream_limit_bytes"] == 65536
        and capture["diagnostic_traceback_limit_bytes"] == 65536
        and capture["total_diagnostic_budget_bytes"] == 4194304
        and receipt["worker_failure_capture_count"] == 5
        and receipt["worker_failure_capture_complete"] is True
        and type(capture["suite_failure_summaries"]) is list
        and len(capture["suite_failure_summaries"]) == 5,
        "preserve all five complete bounded real failure summaries",
    )
    first = capture["first_worker_failure"]
    full_first_keys = v82.SUMMARY_KEYS | {"stdout", "stderr", "traceback"}
    base.need(
        type(first) is dict
        and set(first) == full_first_keys
        and first["suite"] == FAILURES[0][0]
        and first["pid"] == FAILURES[0][1]
        and first["returncode"] == 2
        and first["error_type"] == "CampaignError"
        and first["error_message"]
        == "CampaignError: require complete frozen JSON bytes: "
        "complete actual V15 original worker"
        and first["stderr_complete"] is True
        and first["stderr_size_bytes"] == 4629
        and first["stderr_sha256"] == FIRST_STDERR_SHA256
        and first["stdout_complete"] is True
        and first["stdout_size_bytes"] == 0
        and first["stdout_sha256"] == EMPTY_STDOUT_SHA256
        and first["traceback_complete"] is True
        and first["traceback_sha256"] == FIRST_TRACEBACK_SHA256,
        "authenticate the first complete actual public failing child",
    )
    stderr = validate_stream(
        base,
        first["stderr"],
        category="stderr",
        expected_sha256=FIRST_STDERR_SHA256,
        expected_bytes=4629,
        expected_budget=4194304,
    )
    stdout = validate_stream(
        base,
        first["stdout"],
        category="stdout",
        expected_sha256=EMPTY_STDOUT_SHA256,
        expected_bytes=0,
        expected_budget=33554432,
    )
    trace = first["traceback"]
    base.need(
        stdout == b""
        and type(trace) is dict
        and set(trace) == TRACEBACK_KEYS
        and trace["capture_limit_bytes"] == 65536
        and trace["captured_size_bytes"] == 837
        and trace["source_size_bytes"] == 837
        and trace["source_sha256"] == FIRST_TRACEBACK_SHA256
        and trace["complete"] is True
        and trace["truncated"] is False
        and type(trace["text"]) is str
        and len(trace["text"].encode("utf-8")) == 837
        and hashlib.sha256(trace["text"].encode("utf-8")).hexdigest()
        == FIRST_TRACEBACK_SHA256,
        "rehash complete real stdout and traceback from the public tiny receipt",
    )
    base.need(
        b"the guarded literal original upstream test failed" in stderr
        and b"Pattern.__del__" in stderr
        and b"free" in stderr
        and b"NoneType" in stderr,
        "retain the actual wrapped upstream failure and separately observed cleanup",
    )
    expected_first_summary = {
        key: copy.deepcopy(first[key]) for key in v82.SUMMARY_KEYS
    }
    base.need(
        capture["suite_failure_summaries"][0] == expected_first_summary,
        "retain the complete first summary without pretending it contains streams",
    )
    for summary, (suite, pid, fingerprint, size) in zip(
        capture["suite_failure_summaries"], FAILURES, strict=True
    ):
        base.need(
            type(summary) is dict
            and set(summary) == v82.SUMMARY_KEYS
            and summary["suite"] == suite
            and summary["pid"] == pid
            and summary["returncode"] == 2
            and summary["error_type"] == "CampaignError"
            and summary["error_message"] == first["error_message"]
            and summary["stderr_sha256"] == fingerprint
            and summary["stderr_size_bytes"] == size
            and summary["stderr_complete"] is True
            and summary["stdout_sha256"] == EMPTY_STDOUT_SHA256
            and summary["stdout_size_bytes"] == 0
            and summary["stdout_complete"] is True
            and summary["traceback_sha256"] == FIRST_TRACEBACK_SHA256
            and summary["traceback_complete"] is True,
            "reject missing or invented actual failure metadata: " + suite,
        )
    base.need(
        receipt["all_four_original_targets_restored"] is True
        and receipt["restoration_verified_before_publication"] is True
        and receipt["public_recovery_root"]
        == "/tmp/rebar-phase2-repaired-rust-original-campaign-v15-"
        "phase2-v19-rust-buffer-shape-root-provenance-original-p0"
        and receipt["recovery_journal_sha256"]
        == "984ea29000191e14c1e6aa28cde170079088762ebea06548da034c82c3106357"
        and receipt["power_failure_automatically_recovered"] is False
        and receipt["sigkill_automatically_recovered"] is False,
        "preserve actual restoration without asserting automatic crash recovery",
    )
    restored = receipt["restored_original_targets"]
    base.need(
        type(restored) is dict and set(restored) == set(v82.RESTORED),
        "retain exactly all four original first-party source and binary targets",
    )
    for role, (relative, digest, size, inode, mode) in v82.RESTORED.items():
        actual = restored[role]
        base.need(
            type(actual) is dict
            and set(actual) == v82.RESTORED_KEYS
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
            "reject an invented or replaced restored original owner: " + role,
        )
    archive = receipt["archive"]
    base.need(
        type(archive) is dict
        and set(archive) == v82.ARCHIVE_KEYS
        and archive["relative"] == ARCHIVE_RELATIVE
        and archive["path"]
        == str(ROOT / "oracle/phase2/evidence" / ARCHIVE_RELATIVE)
        and archive["sha256"] == ARCHIVE_SHA256
        and archive["size_bytes"] == 3398500
        and archive["device"] == 2064
        and archive["inode"] == 525116
        and archive["mode"] == 0o600
        and archive["exclusive_creation"] is True
        and archive["file_fsync_completed"] is True
        and archive["directory_fsync_completed"] is True
        and archive["same_inode_readback_verified"] is True
        and archive["streaming_readback_verified"] is True
        and archive["write_calls"] == 20,
        "retain compressed archive metadata solely from the unopened tiny receipt",
    )
    for key in (
        "actual_v19_build_archive_gzip_inflation_count",
        "actual_v19_build_archive_read_count",
        "benchmark_files_read",
        "clock_samples",
        "hidden_cases_read",
        "timing_trials_run",
    ):
        base.need(receipt[key] == 0, "reject forbidden actual measurement: " + key)
    base.need(
        receipt["group_atomic"] is False
        and receipt["holdout"] == "NOT OPENED"
        and receipt["performance"] == "NOT MEASURED"
        and receipt["memory"] == "NOT MEASURED"
        and receipt["undefined_behavior"] == "NOT MEASURED"
        and receipt["winner_selected"] is False,
        "never fabricate a safety guarantee, compatible engine, or speedup",
    )


def make_outcome(base: types.ModuleType, receipt: dict) -> dict:
    capture = receipt["worker_failure_capture"]
    first = capture["first_worker_failure"]
    return {
        "schema": SCHEMA + "-actual-rust-original-campaign-v15-outcome",
        "version": 15,
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
        "completed_suite_count": 8,
        "actual_candidate_worker_count": 13,
        "actual_worker_process_ids": copy.deepcopy(
            receipt["actual_worker_process_ids"]
        ),
        "distinct_worker_process_id_count": 13,
        "infrastructure_failure_count": 5,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": 12942,
        "all_original_observation_vectors_complete": False,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "complete_bounded_worker_failure_capture": copy.deepcopy(capture),
        "worker_failure_capture_count": 5,
        "worker_failure_capture_complete": True,
        "first_complete_public_child_stderr_sha256": first["stderr_sha256"],
        "first_complete_public_child_stderr_bytes": first["stderr_size_bytes"],
        "first_complete_public_child_traceback_sha256": first["traceback_sha256"],
        "first_complete_public_child_traceback_bytes": first["traceback"][
            "source_size_bytes"
        ],
        "first_complete_public_child_stderr_in_receipt": True,
        "first_complete_public_child_traceback_in_receipt": True,
        "literal_original_upstream_failure_reported": True,
        "pattern_destructor_none_free_cleanup_error_observed": True,
        "pattern_destructor_proven_underlying_failure_cause": False,
        "underlying_original_failure_cause": "NOT ESTABLISHED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_original_suite_pass": False,
        "candidate_whole_project_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def make_actual_pool(base: types.ModuleType, outcome: dict) -> dict:
    raw = base.canonical(outcome)
    digest = base.digest(raw)
    return {
        "schema": ACTUAL_POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "entries": {
            digest: {
                "proof_key": ACTUAL_KEY,
                "proof_schema": outcome["schema"],
                "canonical_sha256": digest,
                "canonical_bytes": len(raw),
                "complete_proof": copy.deepcopy(outcome),
            },
        },
    }


def validate_actual_pool(
    base: types.ModuleType,
    pool: object,
    outcome: dict,
) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {"schema", "version", "hash_algorithm", "entries"}
        and pool["schema"] == ACTUAL_POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and type(pool["entries"]) is dict
        and len(pool["entries"]) == 1,
        "require exactly one whole, independent, actual-outcome proof",
    )
    assert isinstance(pool, dict)
    digest, entry = next(iter(pool["entries"].items()))
    raw = base.canonical(outcome)
    base.need(
        base.checked(digest, "whole actual-outcome canonical proof")
        == base.digest(raw)
        and type(entry) is dict
        and set(entry)
        == {
            "proof_key",
            "proof_schema",
            "canonical_sha256",
            "canonical_bytes",
            "complete_proof",
        }
        and entry["proof_key"] == ACTUAL_KEY
        and entry["proof_schema"] == outcome["schema"]
        and entry["canonical_sha256"] == digest
        and entry["canonical_bytes"] == len(raw)
        and base.canonical(entry["complete_proof"]) == raw,
        "reject swapped, truncated, foreign, or duplicated complete actual proof",
    )


def make_actual_reference(base: types.ModuleType, pool: dict, outcome: dict) -> dict:
    validate_actual_pool(base, pool, outcome)
    raw = base.canonical(outcome)
    return {
        "schema": ACTUAL_REFERENCE_SCHEMA,
        "proof_key": ACTUAL_KEY,
        "sha256": base.digest(raw),
        "canonical_bytes": len(raw),
    }


def resolve_actual_reference(
    base: types.ModuleType,
    pool: dict,
    reference: object,
) -> dict:
    base.need(
        type(reference) is dict
        and set(reference) == {"schema", "proof_key", "sha256", "canonical_bytes"}
        and reference["schema"] == ACTUAL_REFERENCE_SCHEMA
        and reference["proof_key"] == ACTUAL_KEY
        and type(reference["canonical_bytes"]) is int
        and reference["canonical_bytes"] > 0,
        "reject a missing or cross-family complete actual-result reference",
    )
    assert isinstance(reference, dict)
    digest = base.checked(reference["sha256"], "complete actual-result reference")
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == ACTUAL_KEY
        and entry.get("canonical_sha256") == digest
        and entry.get("canonical_bytes") == reference["canonical_bytes"]
        and type(entry.get("complete_proof")) is dict,
        "reject an invented or incompletely bound actual family outcome",
    )
    raw = base.canonical(entry["complete_proof"])
    base.need(
        base.digest(raw) == digest
        and len(raw) == reference["canonical_bytes"]
        and entry["proof_schema"] == entry["complete_proof"].get("schema"),
        "reauthenticate all canonical bytes of the real family outcome",
    )
    return copy.deepcopy(entry["complete_proof"])


def make_changes(outcome: dict, receipt: dict) -> tuple[dict, dict]:
    rust = {
        "rust_v15_original_campaign_candidate_matching": "FAIL",
        "rust_v15_original_campaign_actual_worker_count": 13,
        "rust_v15_original_campaign_attempted_suite_count": 13,
        "rust_v15_original_campaign_started_suite_count": 13,
        "rust_v15_original_campaign_completed_suite_count": 8,
        "rust_v15_original_campaign_distinct_worker_count": 13,
        "rust_v15_original_campaign_infrastructure_failure_count": 5,
        "rust_v15_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v15_original_campaign_verified_passing_case_count": 12942,
        "rust_v15_original_campaign_complete_observation_vectors": False,
        "rust_v15_original_campaign_all_original_targets_restored": True,
        "rust_v15_original_campaign_publication_status": "PASS",
        "rust_v15_original_campaign_publication_pass_means":
            "DURABLE PUBLICATION ONLY",
        "rust_v15_original_campaign_runtime_no_delegation": "NOT ESTABLISHED",
        "rust_v15_original_campaign_candidate_qualified": False,
        "rust_v15_original_campaign_outcome_receipt_sha256": RECEIPT[1],
        "rust_v15_original_campaign_outcome_archive_sha256": ARCHIVE_SHA256,
        "rust_v15_original_campaign_outcome_archive_opened_by_graph": False,
        "rust_v15_original_campaign_outcome_archive_inflated_by_graph": False,
        "rust_v15_original_campaign_worker_failure_capture_attempts": 5,
        "rust_v15_original_campaign_worker_failure_capture_complete": True,
        "rust_v15_original_campaign_first_complete_public_child_stderr_sha256":
            FIRST_STDERR_SHA256,
        "rust_v15_original_campaign_first_complete_public_child_stderr_bytes":
            4629,
        "rust_v15_original_campaign_first_complete_public_child_traceback_sha256":
            FIRST_TRACEBACK_SHA256,
        "rust_v15_original_campaign_first_complete_public_child_traceback_bytes":
            837,
        "rust_v15_original_campaign_child_stderr_text_in_public_receipt": True,
        "rust_v15_original_campaign_child_traceback_text_in_public_receipt": True,
        "rust_v15_original_campaign_literal_upstream_test_failure_observed": True,
        "rust_v15_original_campaign_pattern_destructor_cleanup_error_observed":
            True,
        "rust_v15_original_campaign_pattern_destructor_proven_failure_cause":
            False,
        "rust_v15_original_campaign_underlying_original_failure_cause":
            "NOT ESTABLISHED",
    }
    changes = {
        "actual_current_graph_predecessor_version": 83,
        "authenticated_evidence_owner_lower_bound": receipt[
            "resulting_repository_evidence_owner_count"
        ],
        "authenticated_history_reference_lower_bound": receipt[
            "resulting_authenticated_reference_count"
        ],
        ACTUAL_KEY: copy.deepcopy(outcome),
        **copy.deepcopy(rust),
    }
    return changes, rust


def validate_families(
    base: types.ModuleType,
    previous: types.ModuleType,
    families: object,
    original_families: list,
    historical_pool: dict,
    actual_pool: dict,
    full_documents: dict,
    outcome: dict,
    rust_changes: dict,
) -> None:
    previous.validate_pool(base, historical_pool, full_documents)
    validate_actual_pool(base, actual_pool, outcome)
    base.need(
        type(families) is list
        and type(original_families) is list
        and len(families) == len(original_families) == 7
        and [row.get("family") for row in families if type(row) is dict]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain exactly the real Python baseline and six independent families",
    )
    for row, original in zip(families, original_families, strict=True):
        base.need(
            type(row) is dict
            and type(original) is dict
            and row["family"] == original["family"],
            "reject an omitted, invented, or reordered independent candidate",
        )
        if row["family"] == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "preserve the entire unmodified Python comparison baseline",
            )
            continue
        for key in previous.PROOF_KEYS:
            base.need(
                base.canonical(row[key]) == base.canonical(original[key])
                and base.canonical(
                    previous.resolve_reference(base, historical_pool, row[key], key)
                ) == base.canonical(full_documents[key]),
                "preserve all 54 exact prior digest references: "
                + row["family"]
                + ": "
                + key,
            )
        resolved = resolve_actual_reference(base, actual_pool, row.get(ACTUAL_KEY))
        base.need(
            base.canonical(resolved) == base.canonical(outcome),
            "bind the complete real result into " + row["family"],
        )
        expected = copy.deepcopy(original)
        expected["authenticated_evidence_owner_lower_bound"] = 272
        expected["authenticated_history_reference_lower_bound"] = 277
        expected[ACTUAL_KEY] = make_actual_reference(base, actual_pool, outcome)
        if row["family"] == "rust":
            expected.update(copy.deepcopy(rust_changes))
        base.need(
            base.canonical(row) == base.canonical(expected),
            "prove the exact full V84 compact family: " + row["family"],
        )
        restored = copy.deepcopy(row)
        restored.pop(ACTUAL_KEY)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if row["family"] == "rust":
            for key in rust_changes:
                if key in original:
                    restored[key] = copy.deepcopy(original[key])
                else:
                    restored.pop(key)
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore the entire pushed V83 family byte-for-byte: "
            + row["family"],
        )
        base.need(
            row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "never represent incomplete tests as a passing replacement: "
            + row["family"],
        )


def make_svg() -> bytes:
    rows = (
        ("Python re", "Original compatibility reference", "BASELINE", "#22c55e"),
        (
            "Rust",
            "12,942 verified checks; 8 of 13 groups completed",
            "5 GROUPS FAILED",
            "#fb7185",
        ),
        ("C", "1,230 previously observed differences", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "1,764 previously observed differences", "NOT COMPATIBLE", "#f59e0b"),
        ("C++", "2,308 differences; five startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Complete Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1230" height="724" viewBox="0 0 1230 724" role="img" aria-labelledby="title description">',
        '<title id="title">How six from-scratch regular-expression engines compare with Python</title>',
        '<desc id="description">Python is the original reference. The repaired Rust candidate genuinely started thirteen distinct workers, completed eight of thirteen test groups, and explicitly verified twelve thousand nine hundred forty-two of the thirty-one thousand two hundred thirty-seven original checks. Five groups had infrastructure failures, so complete semantic compatibility was not measured and Rust remains unqualified. The complete public first child output reported an original upstream test failure and also showed a pattern-destruction cleanup error; the cleanup observation is not evidence of the underlying failure cause. All six independent engines, every historical failure, and all original test evidence are retained. No performance result is available and the final holdout remains closed.</desc>',
        '<rect width="1230" height="724" rx="18" fill="#0b1220"/>',
        '<text x="34" y="48" fill="#f8fafc" font-size="26" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="81" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="104" x2="1196" y2="104" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 142 + 47 * index
        parts.extend((
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1178" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ))
    parts.extend((
        '<line x1="34" y1="462" x2="1196" y2="462" stroke="#334155"/>',
        '<text x="34" y="493" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate additional checks.</text>',
        '<text x="34" y="522" fill="#fcd34d" font-size="14" font-family="system-ui,sans-serif">Real corrected Rust run: 12,942 verified cases; 8/13 completed groups; 5 infrastructure failures.</text>',
        '<text x="34" y="550" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Actual first output reported an upstream test failure and separately showed a cleanup error.</text>',
        '<text x="34" y="578" fill="#fda4af" font-size="13" font-family="system-ui,sans-serif">Underlying cause and full compatibility: NOT ESTABLISHED. Completed groups are not claimed as passing groups.</text>',
        '<text x="34" y="606" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">All earlier failures, all original test results, and all six independent candidates remain visible.</text>',
        '<text x="34" y="634" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Speed, memory, and runtime independence: NOT MEASURED or NOT ESTABLISHED.</text>',
        '<text x="34" y="662" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Final 4,194,304-case comparison: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="701" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 84 · actual results, complete public diagnostics, and no selected winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def build(
    previous: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None and options.source_bytes is not None,
        "caller-pin the complete exact V84 actual-outcome graph source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole exact V84 source"),
        options.source_bytes,
        private=True,
    )
    for role, item in V83.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the complete committed V83 " + role,
        )
    base.need(
        options.receipt_sha256 == RECEIPT[1],
        "caller-pin the complete immutable actual V15 public tiny receipt",
    )
    old, previous_inputs = authenticate_previous(previous, v82, chain, base)
    receipt_raw = read_fixed(RECEIPT, "only complete actual public V15 receipt")
    receipt = base.document(receipt_raw, "whole canonical actual public V15 receipt")
    base.need(
        base.canonical(receipt) == receipt_raw,
        "reject malformed, partial, duplicate-key, or noncanonical real receipt",
    )
    validate_receipt(base, previous, v82, chain, old, receipt)
    outcome = make_outcome(base, receipt)
    actual_pool = make_actual_pool(base, outcome)
    validate_actual_pool(base, actual_pool, outcome)
    historical_pool = copy.deepcopy(old["lossless_family_evidence_pool"])
    full_documents = {
        key: copy.deepcopy(old[key]) for key in previous.PROOF_KEYS
    }
    previous.validate_pool(base, historical_pool, full_documents)
    base.need(
        base.canonical(historical_pool)
        == base.canonical(old["lossless_family_evidence_pool"]),
        "preserve every canonical byte of all nine previous complete proofs",
    )
    changes, rust_changes = make_changes(outcome, receipt)
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v83_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V83.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 84,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 272
        row["authenticated_history_reference_lower_bound"] = 277
        row[ACTUAL_KEY] = make_actual_reference(base, actual_pool, outcome)
        if row["family"] == "rust":
            row.update(copy.deepcopy(rust_changes))
    validate_families(
        base,
        previous,
        families,
        old["families"],
        historical_pool,
        actual_pool,
        full_documents,
        outcome,
        rust_changes,
    )
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 84,
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
        "lossless_family_evidence_pool": historical_pool,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_family_references_per_family": 9,
        "lossless_family_reconstruction_status": "PASS",
        "lossless_family_previous_byte_identity_status": "PASS",
        "lossless_actual_outcome_evidence_pool": actual_pool,
        "lossless_actual_outcome_evidence_pool_schema": ACTUAL_POOL_SCHEMA,
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_actual_outcome_references_per_family": 1,
        "lossless_actual_outcome_reconstruction_status": "PASS",
        "lossless_v83_family_previous_byte_identity_status": "PASS",
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
        "preserve every original full-suite vector and genuine mismatch witness",
    )
    for label, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        historical = layer["actual_complete_rust_campaign"]
        recorded = layer[ACTUAL_KEY]
        base.need(
            historical["complete_independently_authenticated_suite_results"]
            == suites
            and historical["earliest_genuine_mismatch_witnesses"] == witnesses
            and all(
                base.canonical(layer[key]) == base.canonical(full_documents[key])
                for key in previous.PROOF_KEYS
            )
            and base.canonical(recorded) == base.canonical(outcome)
            and base.canonical(recorded["complete_publication_receipt"])
            == receipt_raw
            and recorded["complete_bounded_worker_failure_capture"]
            == receipt["worker_failure_capture"]
            and layer["rust_v12_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v13_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v14_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v15_original_campaign_candidate_matching"] == "FAIL"
            and layer["rust_v15_original_campaign_actual_worker_count"] == 13
            and layer["rust_v15_original_campaign_completed_suite_count"] == 8
            and layer["rust_v15_original_campaign_infrastructure_failure_count"]
            == 5
            and layer["rust_v15_original_campaign_verified_passing_case_count"]
            == 12942
            and layer["rust_v15_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["rust_v15_original_campaign_candidate_qualified"] is False
            and layer["rust_v15_original_campaign_pattern_destructor_proven_failure_cause"]
            is False,
            "retain every full prior loss and all actual V15 public bytes in "
            + label,
        )
    base.need(
        base.canonical(summary["lossless_family_evidence_pool"])
        == base.canonical(old["lossless_family_evidence_pool"])
        and summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_rust_verified_passing_case_count"] == 14853
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_c_verified_passing_case_count"] == 7325
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["actual_zig_verified_passing_case_count"] == 3711
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["final_holdout_opened"] is False,
        "preserve all real history without claiming qualification or speed",
    )
    summary_raw = base.canonical(summary)
    assets = {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": summary_raw,
        OUTPUT + ".svg": svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
            "reject oversized or partial real-outcome evidence BEFORE writes: "
            + path,
        )
    return snapshot, assets


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only complete bounded exclusively created actual V84 evidence",
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
                "write every complete actual V84 graph byte",
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
            "authenticate the exclusive complete actual V84 graph owner",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "reauthenticate all actual V84 output bytes")


def self_test(
    previous: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(v82, chain, base)
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 83
        and prior["authenticated_evidence_owner_lower_bound"] == 270
        and prior["authenticated_history_reference_lower_bound"] == 275
        and prior["lossless_family_evidence_pool_entry_count"] == 9
        and prior["lossless_family_references_per_family"] == 9
        and prior["previous_v12_actual_rust_infrastructure_failure_count"] == 13
        and prior["previous_v13_actual_rust_infrastructure_failure_count"] == 13
        and prior["previous_v14_actual_rust_infrastructure_failure_count"] == 13
        and prior["actual_candidate_workers_started_by_graph"] == 0
        and prior["actual_compressed_evidence_owners_opened_by_graph"] == 0
        and prior["actual_clock_samples_by_graph"] == 0
        and prior["runtime_no_delegation"] == "NOT ESTABLISHED"
        and prior["qualified_candidate_count"] == 0
        and prior["final_holdout_opened"] is False,
        "inherit all 8,065 exact V83 hostile controls and all original losses",
    )
    old, _ = authenticate_previous(previous, v82, chain, base)
    raw = read_fixed(RECEIPT, "only complete actual V15 tiny public receipt")
    receipt = base.document(raw, "whole exact actual V15 public receipt")
    base.need(
        base.canonical(receipt) == raw,
        "reject a truncated or noncanonical actual public failure receipt",
    )
    validate_receipt(base, previous, v82, chain, old, receipt)
    outcome = make_outcome(base, receipt)
    actual_pool = make_actual_pool(base, outcome)
    historical_pool = copy.deepcopy(old["lossless_family_evidence_pool"])
    full_documents = {key: copy.deepcopy(old[key]) for key in previous.PROOF_KEYS}
    _, rust_changes = make_changes(outcome, receipt)
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 272
        row["authenticated_history_reference_lower_bound"] = 277
        row[ACTUAL_KEY] = make_actual_reference(base, actual_pool, outcome)
        if row["family"] == "rust":
            row.update(copy.deepcopy(rust_changes))
    validate_families(
        base,
        previous,
        families,
        old["families"],
        historical_pool,
        actual_pool,
        full_documents,
        outcome,
        rust_changes,
    )
    rejected = 0

    def reject(label: str, check: object) -> None:
        nonlocal rejected
        try:
            assert callable(check)
            check()
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted forged actual V84 evidence: " + label)

    for key in sorted(receipt):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        reject(
            "removed complete actual receipt key " + key,
            lambda candidate=forged: validate_receipt(
                base, previous, v82, chain, old, candidate
            ),
        )
    for key, value in (
        ("schema", "invented-durable-receipt"),
        ("publication_pass_means", "CANDIDATE PASS"),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("suite_count", 12),
        ("case_execution_denominator", 12942),
        ("attempted_suite_count", 8),
        ("started_suite_count", 8),
        ("actual_candidate_workers", 8),
        ("completed_suite_count", 13),
        ("infrastructure_failure_count", 0),
        ("semantic_mismatch_count", 0),
        ("verified_passing_case_count", 31237),
        ("all_original_observation_vectors_complete", True),
        ("distinct_worker_process_id_count", 8),
        ("duplicate_worker_process_id_count", 1),
        ("historical_evidence_owner_count_before_publication", 269),
        ("historical_authenticated_reference_count_before_publication", 274),
        ("new_repository_evidence_owner_count", 1),
        ("resulting_repository_evidence_owner_count", 273),
        ("resulting_authenticated_reference_count", 278),
        ("worker_failure_capture_count", 4),
        ("worker_failure_capture_complete", False),
        ("all_four_original_targets_restored", False),
        ("restoration_verified_before_publication", False),
        ("actual_v19_build_archive_read_count", 1),
        ("actual_v19_build_archive_gzip_inflation_count", 1),
        ("benchmark_files_read", 1),
        ("clock_samples", 1),
        ("hidden_cases_read", 1),
        ("timing_trials_run", 1),
        ("performance", "1.5x"),
        ("holdout", "OPENED"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = value
        reject(
            "fabricated actual result " + key,
            lambda candidate=forged: validate_receipt(
                base, previous, v82, chain, old, candidate
            ),
        )
    for key in (
        "campaign_source_sha256",
        "campaign_protocol_sha256",
        "campaign_contract_sha256",
        "original_v5_producer_source_sha256",
        "original_v5_producer_protocol_sha256",
        "original_v5_producer_contract_sha256",
        "published_current_v82_source_sha256",
        "published_current_v82_inputs_sha256",
        "published_current_v82_summary_sha256",
        "published_current_v82_svg_sha256",
        "actual_v19_build_source_sha256",
        "actual_v19_build_protocol_sha256",
        "actual_v19_build_contract_sha256",
        "actual_v19_build_receipt_sha256",
        "native_engine_sha256",
        "native_bridge_sha256",
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = "0" * 64
        reject(
            "substituted actual frozen source " + key,
            lambda candidate=forged: validate_receipt(
                base, previous, v82, chain, old, candidate
            ),
        )
    for index, (suite, _, _, _) in enumerate(FAILURES):
        for key, value in (
            ("suite", "invented_suite"),
            ("pid", 999),
            ("returncode", 0),
            ("stderr_sha256", "0" * 64),
            ("stderr_size_bytes", 1),
            ("stdout_sha256", "0" * 64),
            ("traceback_sha256", "0" * 64),
        ):
            forged = copy.deepcopy(receipt)
            forged["worker_failure_capture"]["suite_failure_summaries"][index][
                key
            ] = value
            reject(
                "altered actual failed child " + suite + ": " + key,
                lambda candidate=forged: validate_receipt(
                    base, previous, v82, chain, old, candidate
                ),
            )
    for category, key, value in (
        ("stderr", "base64", "AA=="),
        ("stderr", "sha256", "0" * 64),
        ("stderr", "size_bytes", 76),
        ("stderr", "complete", False),
        ("stderr", "truncated", True),
        ("stdout", "base64", "AA=="),
        ("stdout", "sha256", "0" * 64),
        ("traceback", "text", "invented traceback"),
        ("traceback", "source_sha256", "0" * 64),
        ("traceback", "complete", False),
    ):
        forged = copy.deepcopy(receipt)
        forged["worker_failure_capture"]["first_worker_failure"][category][
            key
        ] = value
        reject(
            "truncated actual complete public " + category + ": " + key,
            lambda candidate=forged: validate_receipt(
                base, previous, v82, chain, old, candidate
            ),
        )
    for role in v82.RESTORED:
        forged = copy.deepcopy(receipt)
        forged["restored_original_targets"].pop(role)
        reject(
            "removed recovered actual original owner " + role,
            lambda candidate=forged: validate_receipt(
                base, previous, v82, chain, old, candidate
            ),
        )
    for key, value in (
        ("sha256", "0" * 64),
        ("inode", 0),
        ("size_bytes", 0),
        ("relative", "invented.gz"),
        ("streaming_readback_verified", False),
    ):
        forged = copy.deepcopy(receipt)
        forged["archive"][key] = value
        reject(
            "fabricated unopened outcome archive metadata " + key,
            lambda candidate=forged: validate_receipt(
                base, previous, v82, chain, old, candidate
            ),
        )
    reject(
        "removed complete actual-outcome pool",
        lambda: validate_actual_pool(base, None, outcome),
    )
    digest = next(iter(actual_pool["entries"]))
    for key, value in (
        ("schema", "invented-actual-pool"),
        ("version", 2),
        ("hash_algorithm", "sha1"),
    ):
        forged_pool = copy.deepcopy(actual_pool)
        forged_pool[key] = value
        reject(
            "fabricated exact actual pool " + key,
            lambda candidate=forged_pool: validate_actual_pool(
                base, candidate, outcome
            ),
        )
    for key, value in (
        ("proof_key", "invented-outcome"),
        ("proof_schema", "invented-schema"),
        ("canonical_sha256", "0" * 64),
        ("canonical_bytes", 1),
    ):
        forged_pool = copy.deepcopy(actual_pool)
        forged_pool["entries"][digest][key] = value
        reject(
            "swapped canonical actual outcome " + key,
            lambda candidate=forged_pool: validate_actual_pool(
                base, candidate, outcome
            ),
        )
    for row in families:
        if row["family"] == "python":
            continue
        for key, value in (
            ("schema", "invented-reference"),
            ("proof_key", "invented-proof"),
            ("sha256", "0" * 64),
            ("canonical_bytes", 1),
        ):
            forged_reference = copy.deepcopy(row[ACTUAL_KEY])
            forged_reference[key] = value
            reject(
                "swapped family complete actual result "
                + row["family"]
                + ": "
                + key,
                lambda candidate=forged_reference: resolve_actual_reference(
                    base, actual_pool, candidate
                ),
            )
        forged_families = copy.deepcopy(families)
        forged_row = next(
            item for item in forged_families if item["family"] == row["family"]
        )
        forged_row[previous.PROOF_KEYS[0]]["sha256"] = "0" * 64
        reject(
            "erased original exact V83 family evidence " + row["family"],
            lambda candidate=forged_families: validate_families(
                base,
                previous,
                candidate,
                old["families"],
                historical_pool,
                actual_pool,
                full_documents,
                outcome,
                rust_changes,
            ),
        )
    base.need(
        rejected >= 200,
        "reject every missing real loss, forged stream, speed claim, or winner",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 84,
        "status": "PASS",
        "previous_overview_version": 83,
        "actual_current_graph_predecessor_version": 83,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ] + rejected,
        "authenticated_evidence_owner_lower_bound": 272,
        "authenticated_history_reference_lower_bound": 277,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_family_references_per_family": 9,
        "lossless_family_reconstruction_status": "PASS",
        "lossless_family_previous_byte_identity_status": "PASS",
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_actual_outcome_references_per_family": 1,
        "lossless_actual_outcome_reconstruction_status": "PASS",
        "lossless_v83_family_previous_byte_identity_status": "PASS",
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "previous_v12_actual_rust_infrastructure_failure_count": 13,
        "previous_v13_actual_rust_infrastructure_failure_count": 13,
        "previous_v14_actual_rust_infrastructure_failure_count": 13,
        "actual_v15_candidate_matching": "FAIL",
        "actual_v15_candidate_worker_count": 13,
        "actual_v15_completed_suite_count": 8,
        "actual_v15_infrastructure_failure_count": 5,
        "actual_v15_verified_passing_case_count": 12942,
        "actual_v15_semantic_mismatch_count": "NOT MEASURED",
        "actual_v15_first_public_stderr_sha256": FIRST_STDERR_SHA256,
        "actual_v15_first_public_stderr_bytes": 4629,
        "actual_v15_pattern_destructor_cleanup_error_observed": True,
        "actual_v15_pattern_destructor_proven_failure_cause": False,
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
    for role in V83:
        parser.add_argument("--previous-" + role + "-sha256")
    parser.add_argument("--receipt-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v82, chain, base = load_previous()
        if options.self_test:
            base.need(
                all(
                    getattr(options, key) is None
                    for key in (
                        "source_sha256",
                        "source_bytes",
                        "receipt_sha256",
                        "inputs_sha256",
                        "summary_sha256",
                        "svg_sha256",
                    )
                )
                and all(
                    getattr(options, "previous_" + role + "_sha256") is None
                    for role in V83
                ),
                "self-test never publishes, runs a candidate, or measures speed",
            )
            result = self_test(previous, v82, chain, base)
        else:
            _, assets = build(previous, v82, chain, base, options)
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject a fabricated or overwritten V84 outcome owner",
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
                            "whole read-only actual V84 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reconstruct every exact actual V84 output byte: " + role,
                    )
            result = {
                "schema": SCHEMA
                + ("-published" if options.render else "-read-only-frozen-context"),
                "version": 84,
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
                "receipt_sha256": RECEIPT[1],
                "previous_overview_version": 83,
                "actual_current_graph_predecessor_version": 83,
                "authenticated_evidence_owner_lower_bound": 272,
                "authenticated_history_reference_lower_bound": 277,
                "lossless_family_evidence_pool_entry_count": 9,
                "lossless_family_references_per_family": 9,
                "lossless_family_reconstruction_status": "PASS",
                "lossless_family_previous_byte_identity_status": "PASS",
                "lossless_actual_outcome_evidence_pool_entry_count": 1,
                "lossless_actual_outcome_references_per_family": 1,
                "lossless_actual_outcome_reconstruction_status": "PASS",
                "lossless_v83_family_previous_byte_identity_status": "PASS",
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "previous_v12_actual_rust_infrastructure_failure_count": 13,
                "previous_v13_actual_rust_infrastructure_failure_count": 13,
                "previous_v14_actual_rust_infrastructure_failure_count": 13,
                "actual_v15_candidate_matching": "FAIL",
                "actual_v15_candidate_worker_count": 13,
                "actual_v15_completed_suite_count": 8,
                "actual_v15_infrastructure_failure_count": 5,
                "actual_v15_verified_passing_case_count": 12942,
                "actual_v15_semantic_mismatch_count": "NOT MEASURED",
                "actual_v15_first_public_stderr_sha256": FIRST_STDERR_SHA256,
                "actual_v15_pattern_destructor_cleanup_error_observed": True,
                "actual_v15_pattern_destructor_proven_failure_cause": False,
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
        sys.stderr.write("current V84 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
