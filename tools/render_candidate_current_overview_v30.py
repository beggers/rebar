#!/usr/bin/env python3
"""Show genuine improved C, Rust, and Zig failures without inventing speed."""
from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import threading
import time
import types


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_candidate_current_overview_v30.py"
OUTPUT = "docs/evidence/candidate-current-overview-v30"
SCHEMA = "rebar-candidate-current-overview-v30"
LIMIT = 8 * 1024 * 1024
V29 = {
    "source": ("tools/render_candidate_current_overview_v29.py", "788ea53f59b77a1670d4617ab1dde21aef0a5b5e2528a48a46b0e2315ac03c27", 65559),
    "inputs": ("docs/evidence/candidate-current-overview-v29.inputs.json", "f6d306dfc08b89604d9d89896a899049c1ba03b0ebfe674ebba036cc80898894", 52975),
    "summary": ("docs/evidence/candidate-current-overview-v29.json", "48eaf71facc4e7bba79e6b8c6c2ad45ed56eaeecf553afd82e8fe402c0aa6160", 260569),
    "svg": ("docs/evidence/candidate-current-overview-v29.svg", "58725ecef05a1adf01d6c354512bf7101c212bf87f63c40cfdd9e225267f91ff", 17253),
}
C_ARCHIVE = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures.json.gz",
    "8515dfecc873eaea60d0f945e1081ff59a65bda39802e65605198617462a1c9d",
    5767499,
    2064,
    524640,
)
C_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json",
    "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9",
    3482,
    2064,
    524641,
)
C_PLAIN_SHA = "efe58c1a6ce325d262c757aef91b59b5a2709617dcc24bb76ac5888e7408e213"
C_PLAIN_BYTES = 193291659
C_JOURNAL = "5844213bb1a986766ac5036e3de3e1795295540709710bc87c6383f08cdb23bd"
C_ORIGINAL = (
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd",
    149976,
    2064,
    430300,
    0o755,
)
C_BUILD_NATIVE = "aed6e9c2fbe31ee3798c74bc6fe896494f1a3bfed41ff25dcfef6905e7b8e610"
RUST_JOURNAL = "b28862fc1433af8c2897299cf6d64fb672f452f011c68fe887714dc09b60ea65"


class GraphError(Exception):
    """An actual owner, matching result, or no-delegation boundary failed."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only authenticated bounded owner bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V30 evidence") from error


def checked(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value), "pin " + label)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6) and sys.flags.isolated == 1 and sys.dont_write_bytecode is True and os.path.realpath(sys.executable) == PYTHON, "require exact isolated stable CPython 3.14.6")


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        out: dict[str, object] = {}
        for key, value in items:
            need(key not in out, "reject duplicate JSON key in " + label)
            out[key] = value
        return out
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(GraphError("reject nonfinite JSON in " + label)))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed JSON in " + label) from error
    need(type(obj) is dict and canonical(obj) == raw, "require canonical " + label)
    return obj


def read_owner(path: str, fingerprint: str, size: int | None = None, *, private: bool = False, device: int | None = None, inode: int | None = None) -> tuple[bytes, dict]:
    need(type(path) is str and bool(path) and not path.startswith("/") and ".." not in Path(path).parts, "require exact relative evidence owner")
    checked(fingerprint, path)
    fd = os.open(str(ROOT / path), os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 <= before.st_size <= LIMIT and (size is None or before.st_size == size) and (not private or stat.S_IMODE(before.st_mode) == 0o600) and (device is None or before.st_dev == device) and (inode is None or before.st_ino == inode), "reject substituted, linked, excessive, or altered owner " + path)
        remaining = before.st_size
        parts: list[bytes] = []
        while remaining:
            chunk = os.read(fd, min(remaining, 1024 * 1024))
            need(bool(chunk), "reject truncated actual owner " + path)
            parts.append(chunk)
            remaining -= len(chunk)
        need(os.read(fd, 1) == b"", "reject owner with trailing bytes " + path)
        raw = b"".join(parts)
        after = os.fstat(fd)
        need((before.st_dev, before.st_ino, before.st_size, before.st_nlink) == (after.st_dev, after.st_ino, after.st_size, after.st_nlink) and digest(raw) == fingerprint, "reject actual owner changed during hash " + path)
        return raw, {"path": path, "sha256": fingerprint, "bytes": len(raw), "device": after.st_dev, "inode": after.st_ino, "mode": f"{stat.S_IMODE(after.st_mode):04o}", "nlink": after.st_nlink, "uid": after.st_uid}
    finally:
        os.close(fd)


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT, "bound frozen graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def load_v29() -> types.ModuleType:
    raw, _ = read_owner(*V29["source"])
    old = types.ModuleType("_rebar_exact_v29_for_actual_c_original_matching_v30")
    old.__file__ = str(ROOT / V29["source"][0])
    old.__package__ = ""
    exec(compile(raw, old.__file__, "exec", dont_inherit=True), old.__dict__)
    need(old.SCHEMA == "rebar-candidate-current-overview-v29" and old.SELF == V29["source"][0], "authenticate exact committed V29 renderer")
    return old


def authenticate_v29() -> tuple[types.ModuleType, dict, dict, dict[str, str]]:
    old = load_v29()
    _v28, v28, _v28_inputs, refs = old.authenticate_v28()
    build, added = old.authenticate_c15(old.C_ARCHIVE[1], old.C_RECEIPT[1], v28, refs)
    need(len(refs) == 150 and len(added) == 2 and not (set(refs) & set(added)), "reproduce true V29 actual C15 source evidence")
    refs = dict(refs)
    refs.update(added)
    need(len(refs) == 152, "derive 152 actual V29 references")
    owners: dict[str, bytes] = {}
    for key, fixed in sorted(V29.items()):
        owners[key], _ = read_owner(*fixed)
    summary = document(owners["summary"], "exact actual V29 summary")
    inputs = document(owners["inputs"], "exact actual V29 inputs")
    snap = summary.get("snapshot")
    need(type(snap) is dict, "retain complete actual V29 snapshot")
    old.validate(snap)
    need(summary.get("schema") == old.SCHEMA + "-summary" and summary.get("status") == "PASS" and summary.get("repository_evidence_owner_count") == 147 and summary.get("authenticated_digest_addressed_history_paths") == 152 and summary.get("full_case_denominator") == 31237 and summary.get("suite_count") == 13 and summary.get("private_waiver_count") == 13 and summary.get("qualified_candidate_count") == 0 and summary.get("actual_c_v15_source_build") == build and summary.get("c_v15_source_build_status") == "PASS" and summary.get("c_v15_source_build_candidate_correctness") == "NOT MEASURED" and summary.get("c_v15_source_build_process_count") == 14 and summary.get("c_v15_source_build_source_apply_count") == 2 and summary.get("c_v15_native_output_sha256") == C_BUILD_NATIVE and summary.get("rust_original_campaign_status") == "FAIL" and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087 and summary.get("rust_original_campaign_verified_passing_case_count") == 7438 and summary.get("rust_original_campaign_recovery_journal_sha256") == RUST_JOURNAL and summary.get("zig_original_campaign_status") == "FAIL" and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172 and summary.get("zig_original_campaign_verified_passing_case_count") == 2847 and summary.get("c_repaired_semantic_mismatch_count") == 1262 and summary.get("c_repaired_verified_passing_case_count") == 7325 and inputs.get("repository_evidence_owner_count") == 147 and inputs.get("all_digest_addressed_history_path_count") == 152 and owners["svg"] == old.make_svg(snap, V29["source"][1], V29["inputs"][1]), "independently recreate all four V29 owners and real C build and matching history")
    return old, summary, inputs, refs


def authenticate_c_original(archive_sha: str, receipt_sha: str, previous: dict, refs: dict[str, str]) -> tuple[dict, dict[str, str]]:
    need(checked(archive_sha, "actual original C failure archive") == C_ARCHIVE[1] and checked(receipt_sha, "actual original C failure receipt") == C_RECEIPT[1], "caller-pin actual matching failure archive and independent receipt")
    compressed, archive = read_owner(C_ARCHIVE[0], archive_sha, C_ARCHIVE[2], private=True, device=C_ARCHIVE[3], inode=C_ARCHIVE[4])
    receipt_raw, owner = read_owner(C_RECEIPT[0], receipt_sha, C_RECEIPT[2], private=True, device=C_RECEIPT[3], inode=C_RECEIPT[4])
    need((archive["device"], archive["inode"]) != (owner["device"], owner["inode"]) and archive["uid"] == owner["uid"] == 1000 and archive["path"] not in refs and owner["path"] not in refs and compressed[:3] == b"\x1f\x8b\x08" and struct.unpack("<I", compressed[4:8])[0] == 0 and struct.unpack("<I", compressed[-4:])[0] == C_PLAIN_BYTES, "authenticate exact compressed failure bytes and distinct receipt without inflating 193 MB")
    receipt = document(receipt_raw, "actual complete original C V4 durable failure receipt")
    published = receipt.get("archive")
    need(type(published) is dict and receipt.get("schema") == "rebar-owned-repaired-c-original-campaign-v4-durable-publication-receipt" and receipt.get("status") == "PASS" and receipt.get("publication_status") == "PASS" and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY" and receipt.get("candidate_status") == "FAIL" and receipt.get("family") == "c" and receipt.get("label") == "phase2-v15-c-pickle-original-p0" and receipt.get("archive_relative") == C_ARCHIVE[0] and receipt.get("archive_sha256") == archive["sha256"] and receipt.get("archive_bytes") == archive["bytes"] and published.get("path") == str(ROOT / C_ARCHIVE[0]) and published.get("relative") == C_ARCHIVE[0].rsplit("/", 1)[-1] and published.get("sha256") == archive["sha256"] and published.get("size_bytes") == archive["bytes"] and published.get("device") == archive["device"] and published.get("inode") == archive["inode"] and published.get("mode") == 0o600 and published.get("exclusive_creation") is True and published.get("file_fsync_completed") is True and published.get("directory_fsync_completed") is True and published.get("same_inode_readback_verified") is True and published.get("streaming_readback_verified") is True and type(published.get("write_calls")) is int and published["write_calls"] > 0, "separate durable publication PASS from actual complete C matching FAIL")
    old_build = previous["actual_c_v15_source_build"]
    need(receipt.get("suite_count") == 13 and receipt.get("completed_suite_count") == 13 and receipt.get("case_execution_denominator") == 31237 and receipt.get("named_private_waiver_count") == 13 and receipt.get("actual_candidate_workers") == 13 and receipt.get("semantic_mismatch_count") == 1230 and receipt.get("verified_passing_case_count") == 7325 and receipt.get("infrastructure_failure_count") == 0 and receipt.get("candidate_execution_failure_count") == 0 and receipt.get("candidate_qualified") is False and receipt.get("repository_evidence_owner_count_before_publication") == 147 and receipt.get("authenticated_reference_count_before_publication") == 152 and receipt.get("actual_c15_build_archive_sha256") == old_build["archive"]["sha256"] and receipt.get("actual_c15_build_receipt_sha256") == old_build["receipt"]["sha256"], "require all 13 real original C workers and exact observed 1,230 mismatches")
    need(receipt.get("uncompressed_bytes") == C_PLAIN_BYTES and receipt.get("uncompressed_sha256") == C_PLAIN_SHA and type(receipt.get("uncompressed_chunk_count")) is int and receipt["uncompressed_chunk_count"] > 0 and receipt.get("exact_original_native_restored") is True and receipt.get("restoration_verified_before_publication") is True and receipt.get("recovery_journal_sha256") == C_JOURNAL and receipt.get("original_source_targets_modified") == 0 and receipt.get("source_family_spec_rebound") is False and receipt.get("legacy_original_producer_controller_invoked") is False and receipt.get("legacy_publisher_family_dispatch_invoked") is False, "authenticate receipt-only journal-backed C original restoration without reading native or source targets")
    restored = receipt.get("restored_original_native")
    path, fingerprint, size, device, inode, mode = C_ORIGINAL
    historical = previous["snapshot"].get("existing_canonical_c_native_target")
    need(type(restored) is dict and type(historical) is dict and restored.get("relative") == path and restored.get("path") == str(ROOT / path) and restored.get("sha256") == fingerprint and restored.get("size_bytes") == size and restored.get("bytes") == size and restored.get("device") == device and restored.get("inode") == inode and restored.get("mode") == mode and restored.get("nlink") == 1 and restored.get("uid") == 1000 and historical.get("path") == path and historical.get("sha256") == fingerprint and historical.get("bytes") == size and historical.get("device") == device and historical.get("inode") == inode and historical.get("mode") == mode and historical.get("nlink") == 1, "match actual restored native identity to frozen V29 without touching canonical native")
    need(receipt.get("hidden_cases_read") == 0 and receipt.get("benchmark_files_read") == 0 and receipt.get("clock_samples") == 0 and receipt.get("timing_trials_run") == 0 and receipt.get("performance") == "NOT MEASURED" and receipt.get("memory") == "NOT MEASURED" and receipt.get("holdout") == "NOT OPENED" and receipt.get("winner_selected") is False, "reject timing, benchmark access, hidden holdout, or premature winner")
    added = {archive["path"]: archive["sha256"], owner["path"]: owner["sha256"]}
    need(len(added) == 2 and not (set(added) & set(refs)), "derive exactly two new and independent C original failure evidence owners")
    proof = {
        "schema": SCHEMA + "-authenticated-complete-c-matching-failure",
        "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
        "publication_status": "PASS", "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "family": "c", "label": receipt["label"], "archive": archive, "receipt": owner,
        "publication_receipt": receipt, "suite_count": 13, "completed_suite_count": 13,
        "case_execution_denominator": 31237, "private_waiver_count": 13,
        "actual_candidate_workers": 13, "semantic_mismatch_count": 1230,
        "verified_passing_case_count": 7325, "infrastructure_failure_count": 0,
        "candidate_execution_failure_count": 0, "candidate_qualified": False,
        "individual_c_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "historical_c_semantic_mismatch_count": 1262,
        "historical_c_verified_passing_case_count": 7325,
        "semantic_mismatch_reduction": 32,
        "additional_verified_passing_case_count": 0,
        "uncompressed_archive_sha256": C_PLAIN_SHA,
        "uncompressed_archive_bytes": C_PLAIN_BYTES,
        "uncompressed_archive_opened_by_graph": False,
        "uncompressed_archive_bytes_read_by_graph": 0,
        "recovery_journal_sha256": C_JOURNAL,
        "exact_original_native_restored": True,
        "restored_original_native": copy.deepcopy(restored),
        "original_native_inspected_by_graph": False,
        "restoration_verified_before_publication": True,
        "original_source_targets_modified": 0,
        "legacy_original_producer_controller_invoked": False,
        "legacy_publisher_family_dispatch_invoked": False,
        "new_repository_evidence_owner_count": 2,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, added


def validate(snapshot: object) -> None:
    need(type(snapshot) is dict and snapshot.get("full_case_denominator") == 31237 and snapshot.get("suite_count") == 13 and snapshot.get("baseline_passed") == 31237 and snapshot.get("frozen_independent_engine_family_count") == 6 and snapshot.get("qualified_candidate_count") == 0 and snapshot.get("preserved_v29_repository_evidence_owner_count") == 147 and snapshot.get("preserved_v29_digest_addressed_history_path_count") == 152 and snapshot.get("new_c_original_campaign_repository_evidence_owner_count") == 2 and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 149 and snapshot.get("all_digest_addressed_history_path_count") == 154, "derive 147+2 evidence owners and 152+2 references without qualifying a candidate")
    older = snapshot.get("c_v10_repaired_original_campaign")
    need(type(older) is dict and older.get("status") == "FAIL" and older.get("actual_candidate_workers") == 13 and older.get("semantic_mismatch_count") == 1262 and older.get("verified_passing_case_count") == 7325 and older.get("completed_suite_count") == 13 and older.get("infrastructure_failure_count") == 0 and type(older.get("suite_results")) is list and len(older["suite_results"]) == 13, "retain all actual historical C matching groups; never call them new C rows")
    rust = snapshot.get("rust_v3_original_campaign")
    need(type(rust) is dict and rust.get("status") == "FAIL" and rust.get("publication_status") == "PASS" and rust.get("publication_pass_means") == "DURABLE FAILURE PUBLICATION ONLY" and rust.get("actual_candidate_workers") == 13 and rust.get("completed_suite_count") == 13 and rust.get("semantic_mismatch_count") == 1087 and rust.get("verified_passing_case_count") == 7438 and rust.get("infrastructure_failure_count") == 0 and rust.get("candidate_qualified") is False and rust.get("recovery_journal_sha256") == RUST_JOURNAL and rust.get("all_four_original_targets_restored") is True and rust.get("uncompressed_archive_opened_by_graph") is False and rust.get("uncompressed_archive_bytes_read_by_graph") == 0, "preserve actual full Rust failure and independent recovery")
    zig = snapshot.get("zig_v2_original_campaign")
    early = snapshot.get("zig_original_campaign_preflight_failure")
    need(type(zig) is dict and zig.get("status") == "FAIL" and zig.get("actual_candidate_workers") == 13 and zig.get("semantic_mismatch_count") == 2172 and zig.get("verified_passing_case_count") == 2847 and zig.get("infrastructure_failure_count") == 0 and type(early) is dict and early.get("status") == "FAIL" and early.get("actual_candidate_workers") == 0 and early.get("actual_matching_case_execution_count") == 0, "preserve both full Zig failure and first zero-worker preflight")
    source = snapshot.get("c_v15_actual_source_build")
    need(type(source) is dict and source.get("status") == "PASS" and source.get("build_status") == "PASS" and source.get("candidate_correctness") == "NOT MEASURED" and source.get("phase_count") == 2 and source.get("source_apply_count") == 2 and source.get("actual_compiler_process_count") == 14 and source.get("actual_unique_process_id_count") == 14 and source.get("native_outputs_byte_identical") is True and source.get("native_output_sha256") == C_BUILD_NATIVE and source.get("candidate_qualified") is False and source.get("prebuilt_artifact_count") == 0 and source.get("external_regex_dependency_count") == 0 and source.get("cross_family_dependency_count") == 0, "preserve actual first-party 14-process C source build separately from new C matching")
    proof = snapshot.get("c_v4_original_campaign")
    need(type(proof) is dict and proof.get("schema") == SCHEMA + "-authenticated-complete-c-matching-failure" and proof.get("status") == "FAIL" and proof.get("failure_class") == "SEMANTIC MISMATCH" and proof.get("publication_status") == "PASS" and proof.get("publication_pass_means") == "DURABLE FAILURE PUBLICATION ONLY" and proof.get("family") == "c" and proof.get("suite_count") == 13 and proof.get("completed_suite_count") == 13 and proof.get("case_execution_denominator") == 31237 and proof.get("private_waiver_count") == 13 and proof.get("actual_candidate_workers") == 13 and proof.get("semantic_mismatch_count") == 1230 and proof.get("verified_passing_case_count") == 7325 and proof.get("infrastructure_failure_count") == 0 and proof.get("candidate_execution_failure_count") == 0 and proof.get("candidate_qualified") is False and proof.get("individual_c_suite_mismatches") == "NOT PRESENT IN DURABLE RECEIPT", "require genuine complete original C FAIL without inventing group counts")
    need(proof.get("historical_c_semantic_mismatch_count") == 1262 and proof.get("historical_c_verified_passing_case_count") == 7325 and proof.get("semantic_mismatch_reduction") == 32 and proof.get("additional_verified_passing_case_count") == 0 and proof.get("uncompressed_archive_sha256") == C_PLAIN_SHA and proof.get("uncompressed_archive_bytes") == C_PLAIN_BYTES and proof.get("uncompressed_archive_opened_by_graph") is False and proof.get("uncompressed_archive_bytes_read_by_graph") == 0, "show 32 fewer differences without fabricating extra passing checks or decompressing 193 MB")
    need(proof.get("recovery_journal_sha256") == C_JOURNAL and proof.get("exact_original_native_restored") is True and proof.get("original_native_inspected_by_graph") is False and proof.get("restoration_verified_before_publication") is True and proof.get("original_source_targets_modified") == 0 and proof.get("legacy_original_producer_controller_invoked") is False and proof.get("legacy_publisher_family_dispatch_invoked") is False and proof.get("new_repository_evidence_owner_count") == 2, "retain journal-backed restored original without native target access")
    archive, receipt = proof.get("archive"), proof.get("receipt")
    need(type(archive) is dict and archive.get("sha256") == C_ARCHIVE[1] and archive.get("bytes") == C_ARCHIVE[2] and archive.get("device") == C_ARCHIVE[3] and archive.get("inode") == C_ARCHIVE[4] and archive.get("mode") == "0600" and archive.get("nlink") == 1 and type(receipt) is dict and receipt.get("sha256") == C_RECEIPT[1] and receipt.get("bytes") == C_RECEIPT[2] and receipt.get("device") == C_RECEIPT[3] and receipt.get("inode") == C_RECEIPT[4] and receipt.get("mode") == "0600" and receipt.get("nlink") == 1 and (archive.get("device"), archive.get("inode")) != (receipt.get("device"), receipt.get("inode")), "bind distinct exact complete matching failure archive and receipt")
    restored = proof.get("restored_original_native")
    path, fingerprint, size, device, inode, mode = C_ORIGINAL
    need(type(restored) is dict and restored.get("relative") == path and restored.get("path") == str(ROOT / path) and restored.get("sha256") == fingerprint and restored.get("size_bytes") == size and restored.get("bytes") == size and restored.get("device") == device and restored.get("inode") == inode and restored.get("mode") == mode and restored.get("nlink") == 1 and restored.get("uid") == 1000, "verify only receipt-recorded exact restored original C identity")
    published = proof.get("publication_receipt")
    need(type(published) is dict and published.get("status") == "PASS" and published.get("publication_status") == "PASS" and published.get("candidate_status") == "FAIL" and published.get("publication_pass_means") == "DURABLE PUBLICATION ONLY" and published.get("semantic_mismatch_count") == 1230 and published.get("verified_passing_case_count") == 7325, "never misrepresent receipt publication PASS as candidate compatibility")
    need(snapshot.get("c_v4_original_campaign_status") == "FAIL" and snapshot.get("c_v4_original_campaign_actual_candidate_workers") == 13 and snapshot.get("c_v4_original_campaign_semantic_mismatch_count") == 1230 and snapshot.get("c_v4_original_campaign_verified_passing_case_count") == 7325 and snapshot.get("c_v4_original_campaign_infrastructure_failure_count") == 0 and snapshot.get("c_v4_original_campaign_candidate_qualified") is False and snapshot.get("c_v4_semantic_mismatch_reduction") == 32 and snapshot.get("c_v4_additional_verified_passing_cases") == 0, "keep actual new and historical C outcomes separate")
    need(snapshot.get("performance") == "NOT MEASURED" and snapshot.get("memory") == "NOT MEASURED" and snapshot.get("confidence_intervals") == "NOT MEASURED" and snapshot.get("hidden_cases_read") == 0 and snapshot.get("performance_files_read") == 0 and snapshot.get("clock_samples") == 0 and snapshot.get("timing_trials_run") == 0 and snapshot.get("final_comparison_planned_case_count") == 4194304 and snapshot.get("final_comparison_cases_generated") is False and snapshot.get("final_holdout_opened") is False and snapshot.get("winner_selected") is False, "reject fabricated speed, confidence, memory, holdout access, or winner")


def xml(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "V30 renderer")
    checked(inputs, "V30 graph inputs")
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1940" viewBox="0 0 1440 1940" role="img" aria-labelledby="v30-title v30-description">',
        '<title id="v30-title">Building a faster Python re: the new C engine improves but no replacement passes all tests</title>',
        '<desc id="v30-description">All 31,237 original Python checks pass. The genuinely rebuilt C replacement completed all 13 original matching test groups with 1,230 differences, 32 fewer than the previous C result of 1,262, but still has 7,325 verified passing checks and is not compatible. Actual 13-worker Rust and Zig tests have 1,087 and 2,172 differences. An earlier Zig setup started zero matching workers. The independent C source really built twice in 14 processes. The durable receipt says publication passed, not candidate matching. There are 149 distinct evidence owners and 154 references. No large C, Rust, or Zig matching failure archive is decompressed. Speed, memory, uncertainty, and undefined behavior are not measured; no replacement is qualified, and the 4,194,304-case holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:28px;font-weight:760;fill:#16324f}.heading{font-size:21px;font-weight:740;fill:#16324f}.body{font-size:14px;fill:#42556c}.name{font-size:15px;font-weight:720;fill:#16324f}.pass{font-size:13px;font-weight:750;fill:#00794c}.fail{font-size:13px;font-weight:740;fill:#a15e00}.pending{font-size:13px;font-weight:740;fill:#53667b}.big{font-size:20px;font-weight:760;fill:#16324f}.small{font-size:12px;fill:#42556c}.foot{font-size:10px;fill:#53667b}</style>',
        '<rect width="1440" height="1940" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="56" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="46" y="85" class="body">New C: 1,230 differences, 32 fewer than before. Still not compatible. Speed is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0", "compatible replacements"),
        ("1,230", "new C differences"),
        ("32 fewer", "than previous C"),
        ("1,087", "Rust differences"),
        ("2,172", "Zig differences"),
        ("149 / 154", "evidence / references"),
    )
    for index, (value, label) in enumerate(cards):
        x = 44 + index * 195
        out.extend((f'<rect x="{x}" y="101" width="184" height="86" rx="11" fill="#fff" stroke="#dae4ee"/>', f'<text x="{x + 10}" y="137" class="big">{xml(value)}</text>', f'<text x="{x + 10}" y="164" class="small">{xml(label)}</text>'))
    out.extend((
        '<rect x="44" y="205" width="1352" height="561" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="242" class="heading">1. Do the replacements match Python?</text>',
        '<text x="65" y="266" class="body">All C, Rust, and Zig matching outcomes below come from actual completed 13-worker original tests.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 frozen original checks pass.", "pass"),
        ("C — newly rebuilt and actually tested", "NOT COMPATIBLE", "13 workers; 1,230 differences; 7,325 verified passes; 0 worker failures.", "fail"),
        ("C — previous actually tested version", "NOT COMPATIBLE", "13 workers; 1,262 differences; the same 7,325 verified passes.", "fail"),
        ("Rust — actually tested", "NOT COMPATIBLE", "13 workers; 1,087 differences; 7,438 verified passes; 0 worker failures.", "fail"),
        ("Zig — actually tested", "NOT COMPATIBLE", "13 workers; 2,172 differences; 2,847 verified passes; 0 worker failures.", "fail"),
        ("Zig — earlier setup attempt", "SETUP STOPPED; 0 TESTS", "A separate earlier failure started no matching workers.", "fail"),
        ("C — reproducible source build", "BUILD PASSED; MATCHING STILL FAILED", "Two real source builds; 14 real processes; byte-identical first-party binaries.", "pending"),
        ("All final speed and memory comparisons", "NOT MEASURED", "No qualified replacement, fair speed comparison, ranking, or winner.", "pending"),
    )
    for index, (name, status, detail, kind) in enumerate(rows):
        y = 283 + index * 56
        out.extend((f'<rect x="63" y="{y}" width="1314" height="49" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>', f'<text x="79" y="{y + 19}" class="name">{xml(name)}</text>', f'<text x="1358" y="{y + 19}" class="{kind}" text-anchor="end">{xml(status)}</text>', f'<text x="80" y="{y + 38}" class="small">{xml(detail)}</text>'))
    out.extend((
        '<text x="65" y="750" class="body">The new C receipt contains totals, not individual test-group counts. Missing new group results are not invented.</text>',
        '<rect x="44" y="783" width="1352" height="438" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="821" class="heading">2. What did the previous C test show in each group?</text>',
        '<text x="65" y="845" class="body">These are the 13 recorded groups for the older C result of 1,262 differences, not the new 1,230-result run.</text>',
        '<text x="80" y="869" class="small">HISTORICAL ORIGINAL PYTHON TEST GROUP</text>',
        '<text x="1040" y="869" class="small" text-anchor="end">CHECKS</text>',
        '<text x="1355" y="869" class="small" text-anchor="end">PREVIOUS C RESULT ONLY</text>',
    ))
    for index, row in enumerate(snapshot["c_v10_repaired_original_campaign"]["suite_results"]):
        y = 877 + index * 23
        shade = "#f8fafd" if index % 2 == 0 else "#ffffff"
        value = "PASSED" if row["mismatch_count"] == 0 else f'{row["mismatch_count"]:,} DIFFERENCES'
        kind = "pass" if row["mismatch_count"] == 0 else "fail"
        out.extend((f'<rect x="64" y="{y}" width="1312" height="22" rx="4" fill="{shade}"/>', f'<text x="80" y="{y + 16}" class="small">{xml(row["display_name"])}</text>', f'<text x="1040" y="{y + 16}" class="small" text-anchor="end">{row["case_execution_denominator"]:,}</text>', f'<text x="1355" y="{y + 16}" class="{kind}" text-anchor="end">{xml(value)}</text>'))
    out.extend((
        '<rect x="44" y="1238" width="1352" height="497" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1276" class="heading">3. Is the new C result a win?</text>',
        '<text x="66" y="1305" class="body">No. The C replacement still differs from Python on 1,230 observed checks.</text>',
        '<text x="66" y="1332" class="body">The 32-difference reduction is real; the verified passing count stays at 7,325, not 7,357.</text>',
        '<text x="66" y="1359" class="body">All 13 matching groups completed; no matching or worker crash was recorded.</text>',
        '<text x="66" y="1386" class="body">Publication PASS only confirms that the C FAIL was safely recorded.</text>',
        '<text x="66" y="1413" class="body">The original C native file was restored to its exact recorded inode and fingerprint.</text>',
        '<text x="66" y="1440" class="body">The earlier two-phase C source build remains genuinely reproducible and first-party.</text>',
        '<text x="66" y="1467" class="body">147 previous evidence owners + one actual C failure archive + one receipt = 149 owners; 154 references.</text>',
        '<text x="66" y="1494" class="body">The large C, Rust, and Zig matching failure archives stay compressed.</text>',
        '<text x="66" y="1521" class="body">Speed, memory, confidence intervals, and undefined behavior: NOT MEASURED.</text>',
        '<text x="66" y="1548" class="body">The 4,194,304-case final comparison is not generated and has not been opened.</text>',
        '<text x="66" y="1575" class="body">There is no compatible replacement, final comparison, ranking, or winner.</text>',
        f'<text x="66" y="1615" class="small">Actual restored C recovery journal: {xml(C_JOURNAL)}</text>',
        f'<text x="66" y="1639" class="small">Actual C source-build output: {xml(C_BUILD_NATIVE)}</text>',
        f'<text x="47" y="1780" class="foot">Inputs SHA-256: {xml(inputs)}</text>',
        f'<text x="47" y="1803" class="foot">Renderer SHA-256: {xml(source)}</text>',
        f'<text x="47" y="1826" class="foot">Actual C matching failure archive: {xml(C_ARCHIVE[1])}</text>',
        f'<text x="47" y="1849" class="foot">Actual distinct C matching publication receipt: {xml(C_RECEIPT[1])}</text>',
        '</svg>',
    ))
    return ("\n".join(out) + "\n").encode("utf-8")


def build(source: str, archive: str, receipt: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked(source, "V30 source")
    own, _ = read_owner(SELF, source)
    _v29, old, old_inputs, refs = authenticate_v29()
    actual, added = authenticate_c_original(archive, receipt, old, refs)
    need(len(refs) == 152 and len(added) == 2 and not (set(added) & set(refs)), "derive new C evidence only after independently reproducing all V29 references")
    combined = dict(refs)
    combined.update(added)
    owners = old["repository_evidence_owner_count"] + len(added)
    need(owners == 149 and len(combined) == 154, "derive true 149 owners and 154 references")
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({"preserved_v29_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v29_digest_addressed_history_path_count": len(refs), "new_c_original_campaign_repository_evidence_owner_count": len(added), "all_actual_candidate_and_native_evidence_owner_count": owners, "all_digest_addressed_history_path_count": len(combined), "c_v4_original_campaign": copy.deepcopy(actual), "c_v4_original_campaign_status": "FAIL", "c_v4_original_campaign_actual_candidate_workers": 13, "c_v4_original_campaign_semantic_mismatch_count": 1230, "c_v4_original_campaign_verified_passing_case_count": 7325, "c_v4_original_campaign_infrastructure_failure_count": 0, "c_v4_original_campaign_candidate_qualified": False, "c_v4_semantic_mismatch_reduction": 32, "c_v4_additional_verified_passing_cases": 0})
    validate(snapshot)
    prior = {key: pin(*fixed) for key, fixed in sorted(V29.items())}
    manifest = copy.deepcopy(old_inputs)
    manifest.update({"schema": SCHEMA + "-inputs", "version": 30, "python": "3.14.6", "renderer": pin(SELF, source, len(own)), "previous_overview": prior, "actual_complete_c_v4_campaign": copy.deepcopy(actual), "historical_complete_c_campaign": copy.deepcopy(snapshot["c_v10_repaired_original_campaign"]), "current_complete_c_campaign": copy.deepcopy(actual), "actual_complete_zig_campaign": copy.deepcopy(snapshot["zig_v2_original_campaign"]), "actual_complete_rust_campaign": copy.deepcopy(snapshot["rust_v3_original_campaign"]), "historical_zig_preflight_failure": copy.deepcopy(snapshot["zig_original_campaign_preflight_failure"]), "actual_c_v15_source_build": copy.deepcopy(snapshot["c_v15_actual_source_build"]), "preserved_v29_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v29_digest_addressed_history_path_count": len(refs), "new_c_original_campaign_repository_evidence_owner_count": len(added), "repository_evidence_owner_count": owners, "all_digest_addressed_history_path_count": len(combined), "candidate_qualified_count": 0, "c_original_campaign_status": "FAIL", "c_original_campaign_candidate_worker_count": 13, "c_original_campaign_semantic_mismatch_count": 1230, "c_original_campaign_verified_passing_case_count": 7325, "c_original_campaign_infrastructure_failure_count": 0, "c_original_campaign_recovery_journal_sha256": C_JOURNAL, "historical_c_semantic_mismatch_count": 1262, "c_semantic_mismatch_reduction": 32, "c_additional_verified_passing_cases": 0, "individual_c_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "uncompressed_c_matching_archive_opened_by_graph": False, "uncompressed_c_matching_archive_bytes_read_by_graph": 0, "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "uncompressed_zig_archive_opened_by_graph": False, "uncompressed_zig_archive_bytes_read_by_graph": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False})
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source, digest(manifest_raw))
    families = copy.deepcopy(old["families"])
    count = 0
    for family in families:
        if family.get("family") == "c":
            count += 1
            family.update({"historical_v10_repaired_original_campaign": copy.deepcopy(snapshot["c_v10_repaired_original_campaign"]), "current_v4_original_campaign": copy.deepcopy(actual), "current_v4_original_campaign_status": "FAIL", "current_v4_original_campaign_candidate_worker_count": 13, "current_v4_original_campaign_semantic_mismatch_count": 1230, "current_v4_original_campaign_verified_passing_case_count": 7325, "current_v4_original_campaign_infrastructure_failure_count": 0, "current_v4_original_campaign_candidate_qualified": False, "current_v4_semantic_mismatch_reduction": 32, "qualified": False})
    need(count == 1, "retain exactly one independently owned C engine family")
    summary = copy.deepcopy(old)
    summary.update({"schema": SCHEMA + "-summary", "status": "PASS", "python": "3.14.6", "source": pin(SELF, source, len(own)), "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw), len(manifest_raw)), "svg": pin(OUTPUT + ".svg", digest(image), len(image)), "previous_overview": prior, "snapshot": snapshot, "families": families, "preserved_v29_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v29_authenticated_reference_path_count": len(refs), "new_c_original_campaign_repository_evidence_owner_count": len(added), "repository_evidence_owner_count": owners, "authenticated_digest_addressed_history_paths": len(combined), "qualified_candidate_count": 0, "actual_c_v4_original_campaign": copy.deepcopy(actual), "c_original_campaign_status": "FAIL", "c_original_campaign_candidate_worker_count": 13, "c_original_campaign_completed_suite_count": 13, "c_original_campaign_case_execution_denominator": 31237, "c_original_campaign_semantic_mismatch_count": 1230, "c_original_campaign_verified_passing_case_count": 7325, "c_original_campaign_infrastructure_failure_count": 0, "c_original_campaign_execution_failure_count": 0, "c_original_campaign_candidate_qualified": False, "c_original_campaign_receipt_status": "PASS", "c_original_campaign_receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "c_original_campaign_recovery_journal_sha256": C_JOURNAL, "c_original_campaign_exact_original_native_restored": True, "individual_c_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "historical_c_semantic_mismatch_count": 1262, "historical_c_verified_passing_case_count": 7325, "c_semantic_mismatch_reduction": 32, "c_additional_verified_passing_cases": 0, "uncompressed_c_matching_archive_opened_by_graph": False, "uncompressed_c_matching_archive_bytes_read_by_graph": 0, "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "uncompressed_zig_archive_opened_by_graph": False, "uncompressed_zig_archive_bytes_read_by_graph": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False})
    return snapshot, ((OUTPUT + ".inputs.json", manifest_raw), (OUTPUT + ".json", canonical(summary)), (OUTPUT + ".svg", image))


class Wall:
    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, obj: object, name: str) -> None:
        previous = getattr(obj, name, None)
        if previous is None:
            return
        def deny(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GraphError("V30 source-only side effect blocked: " + name)
        self.saved.append((obj, name, previous))
        setattr(obj, name, deny)

    def __enter__(self) -> Wall:
        groups = ((builtins, ("open",)), (os, ("open", "read", "write", "stat", "lstat", "unlink", "remove", "rename", "replace", "mkdir", "makedirs", "system", "fork", "posix_spawn")), (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text", "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")), (subprocess, ("run", "Popen", "call", "check_call", "check_output")), (socket, ("socket", "create_connection")), (importlib, ("import_module",)), (tempfile, ("mkdtemp", "mkstemp")), (threading.Thread, ("start",)), (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "sleep")))
        for obj, names in groups:
            for name in names:
                self.install(obj, name)
        return self

    def __exit__(self, _kind: object, _error: object, _trace: object) -> None:
        for obj, name, previous in reversed(self.saved):
            setattr(obj, name, previous)


def synthetic() -> dict:
    rows = [{"suite": f"historic-{i}", "display_name": f"Previous test group {i + 1}", "case_execution_denominator": 2000, "mismatch_count": 1262 if i == 0 else 0} for i in range(13)]
    historical = {"status": "FAIL", "actual_candidate_workers": 13, "semantic_mismatch_count": 1262, "verified_passing_case_count": 7325, "completed_suite_count": 13, "infrastructure_failure_count": 0, "suite_results": rows}
    rust = {"status": "FAIL", "publication_status": "PASS", "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "actual_candidate_workers": 13, "completed_suite_count": 13, "semantic_mismatch_count": 1087, "verified_passing_case_count": 7438, "infrastructure_failure_count": 0, "candidate_qualified": False, "recovery_journal_sha256": RUST_JOURNAL, "all_four_original_targets_restored": True, "uncompressed_archive_opened_by_graph": False, "uncompressed_archive_bytes_read_by_graph": 0}
    zig = {"status": "FAIL", "actual_candidate_workers": 13, "semantic_mismatch_count": 2172, "verified_passing_case_count": 2847, "infrastructure_failure_count": 0}
    early = {"status": "FAIL", "actual_candidate_workers": 0, "actual_matching_case_execution_count": 0}
    source = {"status": "PASS", "build_status": "PASS", "candidate_correctness": "NOT MEASURED", "phase_count": 2, "source_apply_count": 2, "actual_compiler_process_count": 14, "actual_unique_process_id_count": 14, "native_outputs_byte_identical": True, "native_output_sha256": C_BUILD_NATIVE, "candidate_qualified": False, "prebuilt_artifact_count": 0, "external_regex_dependency_count": 0, "cross_family_dependency_count": 0}
    archive = {"sha256": C_ARCHIVE[1], "bytes": C_ARCHIVE[2], "device": C_ARCHIVE[3], "inode": C_ARCHIVE[4], "mode": "0600", "nlink": 1}
    receipt_owner = {"sha256": C_RECEIPT[1], "bytes": C_RECEIPT[2], "device": C_RECEIPT[3], "inode": C_RECEIPT[4], "mode": "0600", "nlink": 1}
    path, fingerprint, size, device, inode, mode = C_ORIGINAL
    restored = {"relative": path, "path": str(ROOT / path), "sha256": fingerprint, "size_bytes": size, "bytes": size, "device": device, "inode": inode, "mode": mode, "nlink": 1, "uid": 1000}
    published = {"status": "PASS", "publication_status": "PASS", "publication_pass_means": "DURABLE PUBLICATION ONLY", "candidate_status": "FAIL", "semantic_mismatch_count": 1230, "verified_passing_case_count": 7325}
    proof = {"schema": SCHEMA + "-authenticated-complete-c-matching-failure", "status": "FAIL", "failure_class": "SEMANTIC MISMATCH", "publication_status": "PASS", "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "family": "c", "suite_count": 13, "completed_suite_count": 13, "case_execution_denominator": 31237, "private_waiver_count": 13, "actual_candidate_workers": 13, "semantic_mismatch_count": 1230, "verified_passing_case_count": 7325, "infrastructure_failure_count": 0, "candidate_execution_failure_count": 0, "candidate_qualified": False, "individual_c_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "historical_c_semantic_mismatch_count": 1262, "historical_c_verified_passing_case_count": 7325, "semantic_mismatch_reduction": 32, "additional_verified_passing_case_count": 0, "uncompressed_archive_sha256": C_PLAIN_SHA, "uncompressed_archive_bytes": C_PLAIN_BYTES, "uncompressed_archive_opened_by_graph": False, "uncompressed_archive_bytes_read_by_graph": 0, "recovery_journal_sha256": C_JOURNAL, "exact_original_native_restored": True, "restored_original_native": restored, "original_native_inspected_by_graph": False, "restoration_verified_before_publication": True, "original_source_targets_modified": 0, "legacy_original_producer_controller_invoked": False, "legacy_publisher_family_dispatch_invoked": False, "new_repository_evidence_owner_count": 2, "archive": archive, "receipt": receipt_owner, "publication_receipt": published}
    return {"full_case_denominator": 31237, "suite_count": 13, "baseline_passed": 31237, "frozen_independent_engine_family_count": 6, "qualified_candidate_count": 0, "preserved_v29_repository_evidence_owner_count": 147, "preserved_v29_digest_addressed_history_path_count": 152, "new_c_original_campaign_repository_evidence_owner_count": 2, "all_actual_candidate_and_native_evidence_owner_count": 149, "all_digest_addressed_history_path_count": 154, "c_v10_repaired_original_campaign": historical, "rust_v3_original_campaign": rust, "zig_v2_original_campaign": zig, "zig_original_campaign_preflight_failure": early, "c_v15_actual_source_build": source, "c_v4_original_campaign": proof, "c_v4_original_campaign_status": "FAIL", "c_v4_original_campaign_actual_candidate_workers": 13, "c_v4_original_campaign_semantic_mismatch_count": 1230, "c_v4_original_campaign_verified_passing_case_count": 7325, "c_v4_original_campaign_infrastructure_failure_count": 0, "c_v4_original_campaign_candidate_qualified": False, "c_v4_semantic_mismatch_reduction": 32, "c_v4_additional_verified_passing_cases": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "hidden_cases_read": 0, "performance_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}


def self_test() -> dict:
    runtime()
    with Wall() as wall:
        base = synthetic()
        validate(base)
        rejected = 0
        changed = {"full_case_denominator": 31236, "suite_count": 12, "baseline_passed": 0, "frozen_independent_engine_family_count": 5, "qualified_candidate_count": 1, "preserved_v29_repository_evidence_owner_count": 146, "preserved_v29_digest_addressed_history_path_count": 151, "new_c_original_campaign_repository_evidence_owner_count": 1, "all_actual_candidate_and_native_evidence_owner_count": 148, "all_digest_addressed_history_path_count": 153, "c_v4_original_campaign_status": "PASS", "c_v4_original_campaign_actual_candidate_workers": 12, "c_v4_original_campaign_semantic_mismatch_count": 0, "c_v4_original_campaign_verified_passing_case_count": 7357, "c_v4_original_campaign_infrastructure_failure_count": 1, "c_v4_original_campaign_candidate_qualified": True, "c_v4_semantic_mismatch_reduction": 1230, "c_v4_additional_verified_passing_cases": 32, "performance": "2x faster", "memory": "zero", "confidence_intervals": "95%", "hidden_cases_read": 1, "performance_files_read": 1, "clock_samples": 1, "timing_trials_run": 1, "final_comparison_planned_case_count": 4194303, "final_comparison_cases_generated": True, "final_holdout_opened": True, "winner_selected": True}
        for key, forged in changed.items():
            bad = copy.deepcopy(base)
            bad[key] = forged
            try:
                validate(bad)
            except (GraphError, KeyError, TypeError, ValueError):
                rejected += 1
            else:
                raise GraphError("accepted forged actual V30 field " + key)
        hostile = {"status": "PASS", "failure_class": "PASS", "publication_status": "FAIL", "publication_pass_means": "CANDIDATE PASSED", "family": "rust", "suite_count": 12, "completed_suite_count": 12, "case_execution_denominator": 31236, "private_waiver_count": 12, "actual_candidate_workers": 12, "semantic_mismatch_count": 0, "verified_passing_case_count": 7357, "infrastructure_failure_count": 1, "candidate_execution_failure_count": 1, "candidate_qualified": True, "individual_c_suite_mismatches": "invented", "historical_c_semantic_mismatch_count": 1230, "historical_c_verified_passing_case_count": 7357, "semantic_mismatch_reduction": 0, "additional_verified_passing_case_count": 32, "uncompressed_archive_sha256": "0" * 64, "uncompressed_archive_bytes": C_PLAIN_BYTES - 1, "uncompressed_archive_opened_by_graph": True, "uncompressed_archive_bytes_read_by_graph": C_PLAIN_BYTES, "recovery_journal_sha256": "0" * 64, "exact_original_native_restored": False, "original_native_inspected_by_graph": True, "restoration_verified_before_publication": False, "original_source_targets_modified": 1, "legacy_original_producer_controller_invoked": True, "legacy_publisher_family_dispatch_invoked": True, "new_repository_evidence_owner_count": 1}
        for key, forged in hostile.items():
            bad = copy.deepcopy(base)
            bad["c_v4_original_campaign"][key] = forged
            try:
                validate(bad)
            except (GraphError, KeyError, TypeError, ValueError):
                rejected += 1
            else:
                raise GraphError("accepted forged actual C failure proof " + key)
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (b"31,237", b"149 / 154", b"1,230", b"1,262", b"32 fewer", b"1,087", b"2,172", b"7,438", b"2,847", b"7,325", b"NOT MEASURED", b"SETUP STOPPED; 0 TESTS", b"missing new group results are not invented", b"not been opened"):
            need(phrase.lower() in picture.lower(), "graph invents group results, extra passes, timing, or outcomes")
        effects = (lambda: builtins.open("forbidden-v30"), lambda: os.open("forbidden-v30", os.O_RDONLY), lambda: os.stat("forbidden-v30-native"), lambda: subprocess.run(("forbidden-v30",)), lambda: importlib.import_module("candidates.vm_candidate"), lambda: socket.socket(), lambda: tempfile.mkdtemp(), lambda: time.perf_counter(), lambda: threading.Thread(target=lambda: None).start())
        for action in effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("source-only side effect not blocked")
        need(wall.blocked == len(effects), "require physically blocked synthetic source-only effects")
        return {"schema": SCHEMA + "-source-only-self-test", "status": "PASS", "version": 30, "synthetic_only": True, "rejected_hostile_control_count": rejected, "blocked_effect_count": wall.blocked, "full_case_denominator": 31237, "suite_count": 13, "repository_evidence_owner_count": 149, "authenticated_digest_addressed_history_paths": 154, "qualified_candidate_count": 0, "c_candidate_status": "FAIL", "c_candidate_workers": 13, "c_semantic_mismatch_count": 1230, "c_verified_passing_case_count": 7325, "c_infrastructure_failure_count": 0, "c_historical_semantic_mismatch_count": 1262, "c_mismatch_reduction": 32, "c_additional_verified_passing_case_count": 0, "c_recovery_journal_sha256": C_JOURNAL, "actual_rust_semantic_mismatch_count": 1087, "actual_zig_semantic_mismatch_count": 2172, "historical_zig_preflight_candidate_workers": 0, "c_source_build_process_count": 14, "c_source_build_phase_count": 2, "actual_candidate_workers_started_by_graph": 0, "canonical_target_reads": 0, "canonical_target_stats": 0, "uncompressed_c_matching_archive_bytes_read": 0, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_zig_archive_bytes_read": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "workspace_mutations": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}


def publish(path: str, raw: bytes) -> None:
    need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"} and type(raw) is bytes and 0 < len(raw) <= LIMIT, "write only one exclusively created actual V30 owner")
    fd = os.open(str(ROOT / path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    try:
        written = 0
        while written < len(raw):
            count = os.write(fd, raw[written:])
            need(type(count) is int and count > 0, "reject incomplete exclusive V30 owner")
            written += count
        os.fsync(fd)
        state = os.fstat(fd)
        need(state.st_size == len(raw) and state.st_nlink == 1 and stat.S_IMODE(state.st_mode) == 0o600, "reject altered published V30 owner")
    finally:
        os.close(fd)


def result(source: str, archive: str, receipt: str, outputs: dict[str, bytes], written: bool, suffix: str) -> dict:
    return {"schema": SCHEMA + suffix, "version": 30, "status": "PASS", "source_sha256": source, "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]), "summary_sha256": digest(outputs[OUTPUT + ".json"]), "svg_sha256": digest(outputs[OUTPUT + ".svg"]), "actual_c_original_failure_archive_sha256": archive, "actual_c_original_failure_receipt_sha256": receipt, "suite_count": 13, "full_case_denominator": 31237, "private_waiver_count": 13, "qualified_candidate_count": 0, "preserved_v29_repository_evidence_owner_count": 147, "preserved_v29_authenticated_reference_count": 152, "new_actual_c_original_campaign_evidence_owner_count": 2, "repository_evidence_owner_count": 149, "authenticated_digest_addressed_history_paths": 154, "c_matching_status": "FAIL", "c_publication_status": "PASS", "c_publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "actual_c_candidate_workers": 13, "actual_c_completed_suite_count": 13, "actual_c_semantic_mismatch_count": 1230, "actual_c_verified_passing_case_count": 7325, "actual_c_infrastructure_failure_count": 0, "actual_c_candidate_execution_failure_count": 0, "c_candidate_qualified": False, "historical_c_semantic_mismatch_count": 1262, "c_semantic_mismatch_reduction": 32, "c_additional_verified_passing_case_count": 0, "c_recovery_journal_sha256": C_JOURNAL, "exact_original_c_native_restored": True, "c_source_build_phase_count": 2, "c_source_build_process_count": 14, "c_source_build_native_output_sha256": C_BUILD_NATIVE, "actual_rust_candidate_workers": 13, "actual_rust_semantic_mismatch_count": 1087, "actual_rust_verified_passing_case_count": 7438, "actual_zig_candidate_workers": 13, "actual_zig_semantic_mismatch_count": 2172, "actual_zig_verified_passing_case_count": 2847, "historical_zig_preflight_candidate_workers": 0, "individual_c_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "outputs_written": written, "actual_candidate_workers_started_by_graph": 0, "actual_candidate_imports": 0, "actual_native_activations": 0, "canonical_target_reads": 0, "canonical_target_stats": 0, "uncompressed_c_matching_archive_opened": False, "uncompressed_c_matching_archive_bytes_read": 0, "uncompressed_rust_archive_opened": False, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_zig_archive_opened": False, "uncompressed_zig_archive_bytes_read": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    for name in ("--source-sha256", "--campaign-archive-sha256", "--campaign-receipt-sha256", "--inputs-sha256", "--summary-sha256", "--svg-sha256"):
        parser.add_argument(name)
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(all(getattr(args, name) is None for name in ("source_sha256", "campaign_archive_sha256", "campaign_receipt_sha256", "inputs_sha256", "summary_sha256", "svg_sha256")), "source-only synthetic test never accepts real evidence")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "V30 source")
        archive = checked(args.campaign_archive_sha256, "actual C failure archive")
        receipt = checked(args.campaign_receipt_sha256, "actual C failure receipt")
        _snapshot, values = build(source, archive, receipt)
        outputs = dict(values)
        if args.render:
            need(args.inputs_sha256 is None and args.summary_sha256 is None and args.svg_sha256 is None, "reject output hash substitution in once-only publication")
            for path, raw in values:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, True, "-published")))
            return 0
        frozen = {OUTPUT + ".inputs.json": checked(args.inputs_sha256, "V30 frozen inputs"), OUTPUT + ".json": checked(args.summary_sha256, "V30 frozen summary"), OUTPUT + ".svg": checked(args.svg_sha256, "V30 frozen graph")}
        for path, fingerprint in frozen.items():
            raw, _ = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(raw == outputs[path], "independently recreate frozen actual V30 owner")
        sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, False, "-read-only-frozen-context")))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError, KeyError, AttributeError, struct.error) as error:
        sys.stderr.write("current V30 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
