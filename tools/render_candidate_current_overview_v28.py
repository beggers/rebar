#!/usr/bin/env python3
"""Show both genuine full-suite Rust and Zig failures, without timing or inflation."""
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
SELF = "tools/render_candidate_current_overview_v28.py"
OUTPUT = "docs/evidence/candidate-current-overview-v28"
SCHEMA = "rebar-candidate-current-overview-v28"
LIMIT = 8 * 1024 * 1024
JOURNAL = "b28862fc1433af8c2897299cf6d64fb672f452f011c68fe887714dc09b60ea65"
V27 = {
    "source": ("tools/render_candidate_current_overview_v27.py", "0df3ed1efbbacd862597e7aac1652eb37ee84c12adf8b79b836a298418925eba", 78380),
    "inputs": ("docs/evidence/candidate-current-overview-v27.inputs.json", "c48ff1d86d6b9b40ff6f8651ae5cbedf1b17889e5420c27ca77ee03168b80897", 43722),
    "summary": ("docs/evidence/candidate-current-overview-v27.json", "e9a3adfa76acc8b551228708865a756b9ec8fc3ba5447280ac655fe78f8f5ab4", 208790),
    "svg": ("docs/evidence/candidate-current-overview-v27.svg", "f50791d54c0aaf743b03054b330957941d077874fa676ca1388b8314266870c3", 13270),
}
CAMPAIGN = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v3.py", "23819da6e6bb1ce8b27144a5d974b4bb0ecac845c844cb6fadae2ba01b2ef3d2", 89825),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V3.md", "c29edb7751045da17cce2052e028b92530d8eab5ba6b8adafc21135a746f7883", 5766),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v3.json", "ab4b424570254201865394330e025850b4626dfe2eaacd4ec82f41d2e99b0980", 10992),
}
ARCHIVE = ("oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures.json.gz", "3ac7736c127d13d3fad579c4ab9974c6a83612b4253f7921ed3e44269f3a82ad", 5710284, 2064, 524624)
RECEIPT = ("oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures-publication-receipt.json", "97f0b8c47823b20cd04740e3fe2883189cc648d49769015800c0998e6698c281", 4447, 2064, 524625)
PLAIN_SHA = "261e3392ca54e5ac3fe67a7d0fc7ae3639b64858a7697f0cc06f180939c8cc48"
PLAIN_SIZE = 192335385
LABEL = "phase2-v11-rust-dual-overlay-original-p0"
ORIGINALS = {
    "adapter": ("candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 2064, 428100, 0o600),
    "bridge": ("candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15", 144992, 2064, 430629, 0o755),
    "bridge_source": ("candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 2064, 419054, 0o600),
    "engine": ("candidates/_rust_engine.so", "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4", 660440, 2064, 430563, 0o755),
}

class GraphError(Exception):
    pass

def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)

def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only bounded actual owner bytes")
    return hashlib.sha256(raw).hexdigest()

def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V28 evidence") from error

def checked(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value), "pin " + label)
    return value

def runtime() -> None:
    need(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6) and sys.flags.isolated == 1 and sys.dont_write_bytecode is True and os.path.realpath(sys.executable) == PYTHON, "require exact isolated CPython 3.14.6")

def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        out: dict[str, object] = {}
        for key, value in items:
            need(key not in out, "reject duplicate JSON " + label)
            out[key] = value
        return out
    try:
        out = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(GraphError("reject nonfinite JSON " + label)))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed JSON " + label) from error
    need(type(out) is dict and canonical(out) == raw, "require canonical " + label)
    return out

def read_owner(path: str, fingerprint: str, size: int | None = None, *, private: bool = False, device: int | None = None, inode: int | None = None) -> tuple[bytes, dict]:
    need(type(path) is str and bool(path) and not path.startswith("/") and ".." not in Path(path).parts, "require exact relative owner")
    checked(fingerprint, path)
    fd = os.open(str(ROOT / path), os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 <= before.st_size <= LIMIT and (size is None or before.st_size == size) and (not private or stat.S_IMODE(before.st_mode) == 0o600) and (device is None or before.st_dev == device) and (inode is None or before.st_ino == inode), "reject altered or linked owner " + path)
        remaining = before.st_size
        pieces: list[bytes] = []
        while remaining:
            part = os.read(fd, min(remaining, 1024 * 1024))
            need(bool(part), "reject truncated owner " + path)
            pieces.append(part)
            remaining -= len(part)
        need(os.read(fd, 1) == b"", "reject trailing owner bytes " + path)
        raw = b"".join(pieces)
        after = os.fstat(fd)
        need((before.st_dev, before.st_ino, before.st_size, before.st_nlink) == (after.st_dev, after.st_ino, after.st_size, after.st_nlink) and digest(raw) == fingerprint, "reject changed owner digest " + path)
        return raw, {"path": path, "sha256": fingerprint, "bytes": len(raw), "device": after.st_dev, "inode": after.st_ino, "mode": f"{stat.S_IMODE(after.st_mode):04o}", "nlink": after.st_nlink, "uid": after.st_uid}
    finally:
        os.close(fd)

def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT, "bound graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}

def load_previous() -> types.ModuleType:
    raw, _ = read_owner(*V27["source"])
    m = types.ModuleType("_rebar_frozen_v27_for_exact_v28")
    m.__file__ = str(ROOT / V27["source"][0])
    m.__package__ = ""
    exec(compile(raw, m.__file__, "exec", dont_inherit=True), m.__dict__)
    need(m.SCHEMA == "rebar-candidate-current-overview-v27" and m.SELF == V27["source"][0], "authenticate immutable actual V27 renderer")
    return m

def authenticate_v27() -> tuple[types.ModuleType, dict, dict, dict[str, str]]:
    p = load_previous()
    _v26, _old, _inputs, refs = p.authenticate_v26()
    zig, added = p.authenticate_actual_campaign(p.ACTUAL_ARCHIVE[1], p.ACTUAL_RECEIPT[1], refs)
    need(len(refs) == 146 and len(added) == 2 and not (set(refs) & set(added)), "preserve genuine V26 and actual 13-worker Zig owners")
    refs = dict(refs)
    refs.update(added)
    need(len(refs) == 148, "derive all actual V27 references")
    old: dict[str, bytes] = {}
    for key, frozen in sorted(V27.items()):
        old[key], _ = read_owner(*frozen)
    summary = document(old["summary"], "actual V27 summary")
    inputs = document(old["inputs"], "actual V27 inputs")
    snap = summary.get("snapshot")
    need(type(snap) is dict, "preserve full actual V27 snapshot")
    p.validate_snapshot(snap)
    need(summary.get("schema") == p.SCHEMA + "-summary" and summary.get("status") == "PASS" and summary.get("repository_evidence_owner_count") == 143 and summary.get("authenticated_digest_addressed_history_paths") == 148 and summary.get("full_case_denominator") == 31237 and summary.get("suite_count") == 13 and summary.get("private_waiver_count") == 13 and summary.get("qualified_candidate_count") == 0 and summary.get("zig_original_campaign_status") == "FAIL" and summary.get("zig_original_campaign_candidate_worker_count") == 13 and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172 and summary.get("zig_original_campaign_verified_passing_case_count") == 2847 and summary.get("zig_original_campaign_infrastructure_failure_count") == 0 and summary.get("rust_historical_semantic_mismatch_count") == 2042 and summary.get("rust_dual_overlay_repaired_matching_test_status") == "NOT MEASURED" and inputs.get("repository_evidence_owner_count") == 143 and inputs.get("all_digest_addressed_history_path_count") == 148 and snap.get("zig_v2_original_campaign") == zig and old["svg"] == p.make_svg(snap, V27["source"][1], V27["inputs"][1]), "reproduce all four actual V27 owners and genuine Zig FAIL")
    return p, summary, inputs, refs

def authenticate_rust(archive_sha: str, receipt_sha: str, refs: dict[str, str]) -> tuple[dict, dict[str, str]]:
    need(checked(archive_sha, "actual Rust archive") == ARCHIVE[1] and checked(receipt_sha, "actual Rust receipt") == RECEIPT[1], "caller-pin both genuine Rust outcome owners")
    for key, frozen in sorted(CAMPAIGN.items()):
        raw, _ = read_owner(*frozen)
        if key == "contract":
            d = document(raw, "pushed recoverable Rust V3 contract")
            need(d.get("schema") == "rebar-owned-repaired-rust-original-campaign-v3-recoverable-source-freeze" and d.get("version") == 3 and d.get("family") == "rust" and d.get("phase") == "CANDIDATES" and d.get("status") == "SOURCE FROZEN; RECOVERABLE RUST CANDIDATE NOT RUN", "preserve exact Rust source-freeze status separately from actual failure")
    compressed, ao = read_owner(ARCHIVE[0], archive_sha, ARCHIVE[2], private=True, device=ARCHIVE[3], inode=ARCHIVE[4])
    rr, ro = read_owner(RECEIPT[0], receipt_sha, RECEIPT[2], private=True, device=RECEIPT[3], inode=RECEIPT[4])
    need((ao["device"], ao["inode"]) != (ro["device"], ro["inode"]) and ao["uid"] == ro["uid"] == 1000 and ao["path"] not in refs and ro["path"] not in refs and compressed[:3] == b"\x1f\x8b\x08" and struct.unpack("<I", compressed[4:8])[0] == 0 and struct.unpack("<I", compressed[-4:])[0] == PLAIN_SIZE, "verify only bounded canonical gzip bytes; never inflate actual 192 MB")
    r = document(rr, "actual Rust durable failure receipt")
    a = r.get("archive")
    need(type(a) is dict and r.get("schema") == "rebar-owned-repaired-rust-original-campaign-v3-durable-publication-receipt" and r.get("status") == "PASS" and r.get("candidate_status") == "FAIL" and r.get("family") == "rust" and r.get("label") == LABEL and r.get("campaign_source_sha256") == CAMPAIGN["source"][1] and r.get("campaign_protocol_sha256") == CAMPAIGN["protocol"][1] and r.get("campaign_contract_sha256") == CAMPAIGN["contract"][1] and a.get("path") == str(ROOT / ARCHIVE[0]) and a.get("relative") == ARCHIVE[0].rsplit("/", 1)[-1] and a.get("sha256") == ao["sha256"] and a.get("size_bytes") == ao["bytes"] and a.get("device") == ao["device"] and a.get("inode") == ao["inode"] and a.get("mode") == 0o600 and a.get("exclusive_creation") is True and a.get("file_fsync_completed") is True and a.get("directory_fsync_completed") is True and a.get("same_inode_readback_verified") is True and a.get("streaming_readback_verified") is True and type(a.get("write_calls")) is int and a["write_calls"] > 0 and r.get("uncompressed_bytes") == PLAIN_SIZE and r.get("uncompressed_sha256") == PLAIN_SHA and type(r.get("uncompressed_chunk_count")) is int and r["uncompressed_chunk_count"] > 0, "authenticate actual bounded Rust archive and distinct durable receipt")
    need(r.get("suite_count") == 13 and r.get("completed_suite_count") == 13 and r.get("case_execution_denominator") == 31237 and r.get("named_private_waiver_count") == 13 and r.get("actual_candidate_workers") == 13 and r.get("semantic_mismatch_count") == 1087 and r.get("verified_passing_case_count") == 7438 and r.get("infrastructure_failure_count") == 0 and r.get("candidate_qualified") is False and r.get("all_four_original_targets_restored") is True and r.get("restoration_verified_before_publication") is True and r.get("recovery_journal_sha256") == JOURNAL and r.get("group_atomic") is False and r.get("v2_unsafe_activation_invoked") is False and r.get("v2_unsafe_controller_invoked") is False and r.get("power_failure_automatically_recovered") is False and r.get("sigkill_automatically_recovered") is False and r.get("published_v27_evidence_owner_count") == 143 and r.get("published_v27_authenticated_reference_count") == 148 and r.get("actual_zig_original_semantic_mismatch_count") == 2172 and r.get("actual_zig_original_verified_passing_case_count") == 2847 and r.get("hidden_cases_read") == 0 and r.get("benchmark_files_read") == 0 and r.get("clock_samples") == 0 and r.get("timing_trials_run") == 0 and r.get("performance") == "NOT MEASURED" and r.get("memory") == "NOT MEASURED" and r.get("holdout") == "NOT OPENED" and r.get("winner_selected") is False, "preserve actual 13-worker Rust 1,087 mismatch and genuine preactivation recovery")
    restored = r.get("restored_original_targets")
    need(type(restored) is dict and set(restored) == set(ORIGINALS), "preserve four distinct actual restored Rust original identities")
    for role, (path, fp, count, device, inode, mode) in ORIGINALS.items():
        o = restored[role]
        need(type(o) is dict and o.get("relative") == path and o.get("path") == str(ROOT / path) and o.get("sha256") == fp and o.get("size_bytes") == count and o.get("bytes") == count and o.get("device") == device and o.get("inode") == inode and o.get("mode") == mode and o.get("nlink") == 1 and o.get("uid") == 1000, "verify receipt-only restored Rust " + role + " without reading a native target")
    added = {ao["path"]: ao["sha256"], ro["path"]: ro["sha256"]}
    need(len(added) == 2 and not (set(refs) & set(added)), "count two distinct actual Rust campaign owners")
    proof = {"schema": SCHEMA + "-authenticated-complete-rust-matching-failure", "status": "FAIL", "failure_class": "SEMANTIC MISMATCH", "publication_status": "PASS", "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "family": "rust", "label": LABEL, "archive": ao, "receipt": ro, "publication_receipt": r, "suite_count": 13, "completed_suite_count": 13, "case_execution_denominator": 31237, "private_waiver_count": 13, "actual_candidate_workers": 13, "semantic_mismatch_count": 1087, "verified_passing_case_count": 7438, "infrastructure_failure_count": 0, "candidate_qualified": False, "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "uncompressed_archive_sha256": PLAIN_SHA, "uncompressed_archive_bytes": PLAIN_SIZE, "uncompressed_archive_opened_by_graph": False, "uncompressed_archive_bytes_read_by_graph": 0, "recovery_journal_sha256": JOURNAL, "all_four_original_targets_restored": True, "restored_original_targets": copy.deepcopy(restored), "original_targets_inspected_by_graph": False, "restoration_verified_before_publication": True, "group_atomic": False, "v2_unsafe_activation_invoked": False, "v2_unsafe_controller_invoked": False, "power_failure_automatically_recovered": False, "sigkill_automatically_recovered": False, "new_repository_evidence_owner_count": 2, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}
    return proof, added

def validate(snapshot: object) -> None:
    need(type(snapshot) is dict and snapshot.get("full_case_denominator") == 31237 and snapshot.get("suite_count") == 13 and snapshot.get("baseline_passed") == 31237 and snapshot.get("frozen_independent_engine_family_count") == 6 and snapshot.get("qualified_candidate_count") == 0 and snapshot.get("preserved_v27_repository_evidence_owner_count") == 143 and snapshot.get("preserved_v27_digest_addressed_history_path_count") == 148 and snapshot.get("new_rust_original_campaign_repository_evidence_owner_count") == 2 and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 145 and snapshot.get("all_digest_addressed_history_path_count") == 150, "preserve 31,237 and derive distinct 143+2/148+2")
    c = snapshot.get("c_v10_repaired_original_campaign")
    need(type(c) is dict and c.get("actual_candidate_workers") == 13 and c.get("semantic_mismatch_count") == 1262 and c.get("verified_passing_case_count") == 7325 and c.get("completed_suite_count") == 13 and c.get("infrastructure_failure_count") == 0 and type(c.get("suite_results")) is list and len(c["suite_results"]) == 13, "preserve all actual C matching failures")
    old = snapshot.get("zig_original_campaign_preflight_failure")
    need(type(old) is dict and old.get("status") == "FAIL" and old.get("actual_candidate_workers") == 0 and old.get("actual_matching_case_execution_count") == 0, "retain separate real zero-worker Zig preflight")
    zig = snapshot.get("zig_v2_original_campaign")
    need(type(zig) is dict and zig.get("status") == "FAIL" and zig.get("actual_candidate_workers") == 13 and zig.get("semantic_mismatch_count") == 2172 and zig.get("verified_passing_case_count") == 2847 and zig.get("infrastructure_failure_count") == 0 and snapshot.get("zig_scanner_repaired_matching_status") == "FAIL: 2,172 SEMANTIC MISMATCHES", "preserve complete actual repaired Zig failure")
    rust = snapshot.get("rust_v3_original_campaign")
    need(type(rust) is dict and rust.get("schema") == SCHEMA + "-authenticated-complete-rust-matching-failure" and rust.get("status") == "FAIL" and rust.get("failure_class") == "SEMANTIC MISMATCH" and rust.get("publication_status") == "PASS" and rust.get("publication_pass_means") == "DURABLE FAILURE PUBLICATION ONLY" and rust.get("actual_candidate_workers") == 13 and rust.get("completed_suite_count") == 13 and rust.get("case_execution_denominator") == 31237 and rust.get("semantic_mismatch_count") == 1087 and rust.get("verified_passing_case_count") == 7438 and rust.get("infrastructure_failure_count") == 0 and rust.get("candidate_qualified") is False and rust.get("individual_rust_suite_mismatches") == "NOT PRESENT IN DURABLE RECEIPT" and rust.get("uncompressed_archive_bytes") == PLAIN_SIZE and rust.get("uncompressed_archive_sha256") == PLAIN_SHA and rust.get("uncompressed_archive_opened_by_graph") is False and rust.get("uncompressed_archive_bytes_read_by_graph") == 0 and rust.get("recovery_journal_sha256") == JOURNAL and rust.get("all_four_original_targets_restored") is True and rust.get("original_targets_inspected_by_graph") is False and rust.get("restoration_verified_before_publication") is True and rust.get("group_atomic") is False and rust.get("power_failure_automatically_recovered") is False and rust.get("sigkill_automatically_recovered") is False and rust.get("new_repository_evidence_owner_count") == 2, "require exact actual Rust matching failure, receipt distinction and four-target recovery")
    ao, ro = rust.get("archive"), rust.get("receipt")
    need(type(ao) is dict and type(ro) is dict and ao.get("sha256") == ARCHIVE[1] and ao.get("bytes") == ARCHIVE[2] and ao.get("inode") == ARCHIVE[4] and ao.get("mode") == "0600" and ao.get("nlink") == 1 and ro.get("sha256") == RECEIPT[1] and ro.get("bytes") == RECEIPT[2] and ro.get("inode") == RECEIPT[4] and ro.get("mode") == "0600" and ro.get("nlink") == 1 and (ao.get("device"), ao.get("inode")) != (ro.get("device"), ro.get("inode")), "authenticate distinct genuine Rust archive and receipt")
    receipt = rust.get("publication_receipt")
    need(type(receipt) is dict and receipt.get("status") == "PASS" and receipt.get("candidate_status") == "FAIL" and receipt.get("semantic_mismatch_count") == 1087, "never present Rust publication PASS as candidate PASS")
    need(snapshot.get("rust_v3_original_campaign_status") == "FAIL" and snapshot.get("rust_v3_original_campaign_actual_candidate_workers") == 13 and snapshot.get("rust_v3_original_campaign_semantic_mismatch_count") == 1087 and snapshot.get("rust_v3_original_campaign_verified_passing_case_count") == 7438 and snapshot.get("rust_v3_original_campaign_infrastructure_failure_count") == 0 and snapshot.get("rust_dual_overlay_repaired_matching_status") == "FAIL: 1,087 SEMANTIC MISMATCHES" and snapshot.get("rust_dual_overlay_repaired_candidate_worker_count") == 13 and snapshot.get("rust_dual_overlay_repaired_candidate_qualified") is False and snapshot.get("rust_actual_semantic_mismatch_count") == 2042 and snapshot.get("zig_actual_semantic_mismatch_count") == 1764 and snapshot.get("repaired_c_semantic_mismatch_count") == 1262 and snapshot.get("rust_dual_overlay_repaired_build_process_count") == 28 and snapshot.get("zig_scanner_repaired_build_process_count") == 26, "retain prior Rust2042, Zig1764 and actual new Rust1087/Zig2172/C1262")
    need(snapshot.get("performance") == "NOT MEASURED" and snapshot.get("memory") == "NOT MEASURED" and snapshot.get("confidence_intervals") == "NOT MEASURED" and snapshot.get("hidden_cases_read") == 0 and snapshot.get("performance_files_read") == 0 and snapshot.get("clock_samples") == 0 and snapshot.get("timing_trials_run") == 0 and snapshot.get("final_comparison_planned_case_count") == 4194304 and snapshot.get("final_comparison_cases_generated") is False and snapshot.get("final_holdout_opened") is False and snapshot.get("winner_selected") is False, "never invent speed, memory, holdout, or winner")

def xml(x: object) -> str:
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def make_svg(s: dict, source: str, inputs: str) -> bytes:
    validate(s)
    checked(source, "V28 source")
    checked(inputs, "V28 inputs")
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1910" viewBox="0 0 1440 1910" role="img" aria-labelledby="v28-title v28-description">', '<title id="v28-title">Building a faster Python re: complete Rust, Zig, and C tests all expose differences</title>', '<desc id="v28-description">Python passes all 31,237 original checks. Each independently built Rust, Zig, and C candidate ran all 13 original test workers. Repaired Rust has 1,087 matching differences and 7,438 verified passing checks. Repaired Zig has 2,172 differences and 2,847 verified passing checks. C has 1,262 differences and 7,325 verified passing checks. No candidate is fully compatible. A separate earlier Zig preflight failure started zero workers. All four original Rust targets were restored against the preactivation recovery journal. The published archive receipts preserve failing candidate results; receipt PASS is not candidate PASS. The 145 actual evidence owners and 150 signed references retain all historical failures. Large archives are not decompressed. Speed, memory, and confidence have not been measured; the 4,194,304-case holdout remains unopened.</desc>', '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:30px;font-weight:760;fill:#16324f}.heading{font-size:22px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:16px;font-weight:720;fill:#16324f}.pass{font-size:14px;font-weight:750;fill:#00794c}.fail{font-size:14px;font-weight:740;fill:#a15e00}.pending{font-size:14px;font-weight:740;fill:#53667b}.big{font-size:23px;font-weight:760;fill:#16324f}.small{font-size:13px;fill:#42556c}.foot{font-size:11px;fill:#53667b}</style>', '<rect width="1440" height="1910" rx="22" fill="#f4f7fb"/>', '<text x="44" y="61" class="title">Can we build a faster replacement for Python re?</text>', '<text x="46" y="91" class="body">Rust, Zig, and C each ran the full test. All differ from Python. Speed is NOT MEASURED.</text>']
    cards = (("31,237", "original Python checks"), ("0", "compatible replacements"), ("1,087", "actual Rust differences"), ("2,172", "actual Zig differences"), ("1,262", "actual C differences"), ("145 / 150", "evidence / references"))
    for i, (value, label) in enumerate(cards):
        x = 44 + i * 226
        out += [f'<rect x="{x}" y="111" width="216" height="96" rx="12" fill="#fff" stroke="#dae4ee"/>', f'<text x="{x + 11}" y="151" class="big">{xml(value)}</text>', f'<text x="{x + 11}" y="181" class="small">{xml(label)}</text>']
    out += ['<rect x="44" y="224" width="1352" height="791" rx="15" fill="#fff" stroke="#dae4ee"/>', '<text x="64" y="262" class="heading">1. Does each replacement work like Python?</text>', '<text x="65" y="287" class="body">All reported current Rust, Zig, and C results come from 13 real original matching workers.</text>']
    rows = (("Python re — reference", "PASSED", "All 31,237 original Python checks pass.", "pass"), ("Rust — newly repaired engine", "NOT COMPATIBLE", "13 actual workers; 1,087 matching differences; 7,438 verified passing checks; 0 worker failures.", "fail"), ("Zig — newly repaired engine", "NOT COMPATIBLE", "13 actual workers; 2,172 matching differences; 2,847 verified passing checks; 0 worker failures.", "fail"), ("C — latest repaired engine", "NOT COMPATIBLE", "13 actual workers; 1,262 matching differences; 7,325 verified passing checks.", "fail"), ("Zig — first setup attempt", "SETUP STOPPED; 0 TESTS", "Separate earlier controller failure; no matching workers were started.", "fail"), ("Rust — previously tested engine", "NOT COMPATIBLE", "7,461 verified passing checks; 2,042 historical matching differences.", "fail"), ("Zig — previously tested engine", "NOT COMPATIBLE", "3,583 verified passing checks; 1,764 historical matching differences.", "fail"), ("C — earlier tested engine", "NOT COMPATIBLE", "7,197 verified passing checks; 2,094 historical matching differences.", "fail"), ("C++", "NOT COMPATIBLE", "128 verified passing checks; 2,308 differences and 5 earlier worker failures.", "fail"), ("Go", "NOT COMPATIBLE", "128 verified passing checks; 4,518 differences and 4 earlier worker failures.", "fail"), ("Fortran", "NOT READY", "Independent build attempts differ; no compatible matching engine is established.", "pending"))
    for i, (name, status, detail, kind) in enumerate(rows):
        y = 305 + i * 61
        out += [f'<rect x="63" y="{y}" width="1314" height="54" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>', f'<text x="79" y="{y + 21}" class="name">{xml(name)}</text>', f'<text x="1358" y="{y + 21}" class="{kind}" text-anchor="end">{xml(status)}</text>', f'<text x="81" y="{y + 42}" class="small">{xml(detail)}</text>']
    out += ['<text x="65" y="998" class="body">Rust and Zig per-group counts are not in the durable receipts; missing results are not invented.</text>', '<rect x="44" y="1032" width="1352" height="464" rx="15" fill="#fff" stroke="#dae4ee"/>', '<text x="64" y="1070" class="heading">2. Which actual C test groups still differ?</text>', '<text x="65" y="1095" class="body">All 13 independently recorded C groups are retained. Large Rust and Zig archives are not decompressed.</text>', '<text x="80" y="1118" class="small">ORIGINAL PYTHON TEST GROUP</text>', '<text x="1040" y="1118" class="small" text-anchor="end">CHECKS</text>', '<text x="1355" y="1118" class="small" text-anchor="end">C RESULT</text>']
    for i, row in enumerate(s["c_v10_repaired_original_campaign"]["suite_results"]):
        y = 1128 + i * 25
        value = "PASSED" if row["mismatch_count"] == 0 else f'{row["mismatch_count"]:,} DIFFERENCES'
        kind = "pass" if row["mismatch_count"] == 0 else "fail"
        out += [f'<rect x="64" y="{y}" width="1312" height="23" rx="4" fill="{"#f8fafd" if i % 2 == 0 else "#ffffff"}"/>', f'<text x="80" y="{y + 17}" class="small">{xml(row["display_name"])}</text>', f'<text x="1040" y="{y + 17}" class="small" text-anchor="end">{row["case_execution_denominator"]:,}</text>', f'<text x="1355" y="{y + 17}" class="{kind}" text-anchor="end">{xml(value)}</text>']
    out += ['<rect x="44" y="1513" width="1352" height="279" rx="15" fill="#fff" stroke="#dae4ee"/>', '<text x="64" y="1551" class="heading">3. Is any replacement faster?</text>', '<text x="66" y="1582" class="body">NOT MEASURED. No replacement has passed every original Python compatibility check.</text>', '<text x="66" y="1611" class="body">There is no speed or memory comparison, confidence interval, ranking, or winner.</text>', '<text x="66" y="1640" class="body">The 4,194,304-case final comparison is not generated and has not been opened.</text>', '<text x="66" y="1669" class="body">143 verified previous files + real Rust failure archive + distinct receipt = 145 evidence files; 150 references.</text>', '<text x="66" y="1698" class="body">Receipt PASS means the Rust FAIL was safely published, not that its matching passed.</text>', '<text x="66" y="1727" class="body">All four original Rust files were restored against the announced preactivation journal.</text>', '<text x="66" y="1756" class="body">Neither large Rust or Zig archive is inflated by graph verification.</text>', f'<text x="47" y="1820" class="foot">Inputs SHA-256: {xml(inputs)}</text>', f'<text x="47" y="1842" class="foot">Renderer SHA-256: {xml(source)}</text>', f'<text x="47" y="1864" class="foot">Actual Rust matching failure archive: {xml(ARCHIVE[1])}</text>', '</svg>']
    return ("\n".join(out) + "\n").encode("utf-8")

def build(source: str, archive: str, receipt: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked(source, "V28 source")
    raw, _ = read_owner(SELF, source)
    prev, old, inputs, refs = authenticate_v27()
    proof, added = authenticate_rust(archive, receipt, refs)
    need(len(refs) == 148 and len(added) == 2 and not (set(refs) & set(added)), "derive genuine Rust campaign evidence only")
    combined = dict(refs)
    combined.update(added)
    total = old["repository_evidence_owner_count"] + len(added)
    need(total == 145 and len(combined) == 150, "derive actual 143+2 and 148+2")
    prev.validate_snapshot(old["snapshot"])
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({"preserved_v27_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v27_digest_addressed_history_path_count": len(refs), "new_rust_original_campaign_repository_evidence_owner_count": len(added), "all_actual_candidate_and_native_evidence_owner_count": total, "all_digest_addressed_history_path_count": len(combined), "rust_v3_original_campaign": copy.deepcopy(proof), "rust_v3_original_campaign_status": "FAIL", "rust_v3_original_campaign_actual_candidate_workers": 13, "rust_v3_original_campaign_semantic_mismatch_count": 1087, "rust_v3_original_campaign_verified_passing_case_count": 7438, "rust_v3_original_campaign_infrastructure_failure_count": 0, "rust_dual_overlay_repaired_matching_status": "FAIL: 1,087 SEMANTIC MISMATCHES", "rust_dual_overlay_repaired_candidate_worker_count": 13, "rust_dual_overlay_repaired_candidate_qualified": False})
    validate(snapshot)
    previous = {key: pin(*frozen) for key, frozen in sorted(V27.items())}
    campaign = {key: pin(*frozen) for key, frozen in sorted(CAMPAIGN.items())}
    manifest = {"schema": SCHEMA + "-inputs", "version": 28, "python": "3.14.6", "renderer": pin(SELF, source, len(raw)), "previous_overview": previous, "original_correctness_manifest": copy.deepcopy(inputs["original_correctness_manifest"]), "original_source_freeze": copy.deepcopy(inputs["original_source_freeze"]), "current_complete_c_campaign": copy.deepcopy(snapshot["c_v10_repaired_original_campaign"]), "actual_complete_zig_campaign": copy.deepcopy(snapshot["zig_v2_original_campaign"]), "actual_complete_rust_campaign": copy.deepcopy(proof), "historical_zig_preflight_failure": copy.deepcopy(snapshot["zig_original_campaign_preflight_failure"]), "actual_rust_original_campaign_source_freeze": campaign, "full_case_denominator": 31237, "suite_count": 13, "private_waiver_count": 13, "candidate_families": copy.deepcopy(inputs["candidate_families"]), "candidate_qualified_count": 0, "preserved_v27_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v27_digest_addressed_history_path_count": len(refs), "new_rust_original_campaign_repository_evidence_owner_count": len(added), "repository_evidence_owner_count": total, "all_digest_addressed_history_path_count": len(combined), "actual_rust_candidate_workers": 13, "actual_rust_semantic_mismatch_count": 1087, "actual_rust_verified_passing_case_count": 7438, "actual_rust_infrastructure_failure_count": 0, "actual_zig_semantic_mismatch_count": 2172, "actual_zig_candidate_workers": 13, "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "uncompressed_zig_archive_opened_by_graph": False, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}
    mr = canonical(manifest)
    image = make_svg(snapshot, source, digest(mr))
    families = copy.deepcopy(old["families"])
    count = 0
    for family in families:
        if family.get("family") == "rust":
            count += 1
            family.update({"current_dual_overlay_repaired_build_status": "PASS", "current_dual_overlay_repaired_matching_test_status": "FAIL: 1,087 SEMANTIC MISMATCHES", "current_dual_overlay_repaired_candidate_worker_count": 13, "current_v3_original_campaign": copy.deepcopy(proof), "current_original_campaign_status": "FAIL", "current_original_campaign_candidate_worker_count": 13, "current_original_campaign_semantic_mismatch_count": 1087, "current_original_campaign_verified_passing_case_count": 7438, "current_original_campaign_infrastructure_failure_count": 0, "qualified": False})
    need(count == 1, "retain exactly one independent first-party Rust engine family")
    summary = {"schema": SCHEMA + "-summary", "status": "PASS", "python": "3.14.6", "source": pin(SELF, source, len(raw)), "inputs": pin(OUTPUT + ".inputs.json", digest(mr), len(mr)), "svg": pin(OUTPUT + ".svg", digest(image), len(image)), "previous_overview": previous, "actual_rust_original_campaign_source_freeze": campaign, "snapshot": snapshot, "families": families, "full_case_denominator": 31237, "suite_count": 13, "private_waiver_count": 13, "preserved_v27_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v27_authenticated_reference_path_count": len(refs), "new_rust_original_campaign_repository_evidence_owner_count": len(added), "repository_evidence_owner_count": total, "authenticated_digest_addressed_history_paths": len(combined), "qualified_candidate_count": 0, "actual_rust_original_campaign": copy.deepcopy(proof), "rust_original_campaign_status": "FAIL", "rust_original_campaign_candidate_worker_count": 13, "rust_original_campaign_completed_suite_count": 13, "rust_original_campaign_case_execution_denominator": 31237, "rust_original_campaign_semantic_mismatch_count": 1087, "rust_original_campaign_verified_passing_case_count": 7438, "rust_original_campaign_infrastructure_failure_count": 0, "rust_original_campaign_all_four_original_targets_restored": True, "rust_original_campaign_recovery_journal_sha256": JOURNAL, "rust_original_campaign_receipt_status": "PASS", "rust_original_campaign_receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "historical_zig_preflight_failure": copy.deepcopy(snapshot["zig_original_campaign_preflight_failure"]), "actual_zig_original_campaign": copy.deepcopy(snapshot["zig_v2_original_campaign"]), "zig_original_campaign_status": "FAIL", "zig_original_campaign_candidate_worker_count": 13, "zig_original_campaign_completed_suite_count": 13, "zig_original_campaign_semantic_mismatch_count": 2172, "zig_original_campaign_verified_passing_case_count": 2847, "zig_original_campaign_infrastructure_failure_count": 0, "zig_individual_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "uncompressed_zig_archive_opened_by_graph": False, "c_repaired_matching_test_status": "FAIL: 1,262 SEMANTIC MISMATCHES", "c_repaired_verified_passing_case_count": 7325, "c_repaired_semantic_mismatch_count": 1262, "c_repaired_infrastructure_failure_count": 0, "c_repaired_completed_suite_count": 13, "c_repaired_candidate_worker_count": 13, "rust_dual_overlay_repaired_build_status": "PASS", "rust_dual_overlay_repaired_build_process_count": 28, "rust_dual_overlay_repaired_matching_test_status": "FAIL: 1,087 SEMANTIC MISMATCHES", "rust_dual_overlay_repaired_candidate_worker_count": 13, "rust_dual_overlay_repaired_candidate_qualified": False, "rust_historical_semantic_mismatch_count": 2042, "rust_historical_verified_passing_case_count": 7461, "zig_scanner_repaired_build_status": "PASS", "zig_scanner_repaired_build_process_count": 26, "zig_scanner_repaired_matching_test_status": "FAIL: 2,172 SEMANTIC MISMATCHES", "zig_scanner_repaired_candidate_worker_count": 13, "zig_historical_semantic_mismatch_count": 1764, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}
    return snapshot, ((OUTPUT + ".inputs.json", mr), (OUTPUT + ".json", canonical(summary)), (OUTPUT + ".svg", image))

class Wall:
    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0
    def install(self, obj: object, name: str) -> None:
        original = getattr(obj, name, None)
        if original is None:
            return
        def deny(*_a: object, **_kw: object) -> object:
            self.blocked += 1
            raise GraphError("V28 source-only effect blocked: " + name)
        self.saved.append((obj, name, original))
        setattr(obj, name, deny)
    def __enter__(self) -> Wall:
        for obj, names in ((builtins, ("open",)), (os, ("open", "read", "write", "stat", "lstat", "unlink", "remove", "rename", "replace", "mkdir", "makedirs", "system", "fork", "posix_spawn")), (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text", "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")), (subprocess, ("run", "Popen", "call", "check_call", "check_output")), (socket, ("socket", "create_connection")), (importlib, ("import_module",)), (tempfile, ("mkdtemp", "mkstemp")), (threading.Thread, ("start",)), (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "sleep"))):
            for name in names:
                self.install(obj, name)
        return self
    def __exit__(self, _a: object, _b: object, _c: object) -> None:
        for obj, name, original in reversed(self.saved):
            setattr(obj, name, original)

def synthetic() -> dict:
    rows = [{"suite": f"case-{i}", "display_name": f"Group {i + 1}", "case_execution_denominator": 151, "mismatch_count": 0} for i in range(13)]
    c = {"status": "FAIL", "actual_candidate_workers": 13, "semantic_mismatch_count": 1262, "verified_passing_case_count": 7325, "completed_suite_count": 13, "infrastructure_failure_count": 0, "suite_results": rows}
    old = {"status": "FAIL", "actual_candidate_workers": 0, "actual_matching_case_execution_count": 0}
    zig = {"status": "FAIL", "actual_candidate_workers": 13, "semantic_mismatch_count": 2172, "verified_passing_case_count": 2847, "infrastructure_failure_count": 0}
    ao = {"sha256": ARCHIVE[1], "bytes": ARCHIVE[2], "inode": ARCHIVE[4], "device": ARCHIVE[3], "mode": "0600", "nlink": 1}
    ro = {"sha256": RECEIPT[1], "bytes": RECEIPT[2], "inode": RECEIPT[4], "device": RECEIPT[3], "mode": "0600", "nlink": 1}
    rust = {"schema": SCHEMA + "-authenticated-complete-rust-matching-failure", "status": "FAIL", "failure_class": "SEMANTIC MISMATCH", "publication_status": "PASS", "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "actual_candidate_workers": 13, "completed_suite_count": 13, "case_execution_denominator": 31237, "semantic_mismatch_count": 1087, "verified_passing_case_count": 7438, "infrastructure_failure_count": 0, "candidate_qualified": False, "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT", "uncompressed_archive_bytes": PLAIN_SIZE, "uncompressed_archive_sha256": PLAIN_SHA, "uncompressed_archive_opened_by_graph": False, "uncompressed_archive_bytes_read_by_graph": 0, "recovery_journal_sha256": JOURNAL, "all_four_original_targets_restored": True, "original_targets_inspected_by_graph": False, "restoration_verified_before_publication": True, "group_atomic": False, "power_failure_automatically_recovered": False, "sigkill_automatically_recovered": False, "new_repository_evidence_owner_count": 2, "archive": ao, "receipt": ro, "publication_receipt": {"status": "PASS", "candidate_status": "FAIL", "semantic_mismatch_count": 1087}}
    return {"full_case_denominator": 31237, "suite_count": 13, "baseline_passed": 31237, "frozen_independent_engine_family_count": 6, "qualified_candidate_count": 0, "preserved_v27_repository_evidence_owner_count": 143, "preserved_v27_digest_addressed_history_path_count": 148, "new_rust_original_campaign_repository_evidence_owner_count": 2, "all_actual_candidate_and_native_evidence_owner_count": 145, "all_digest_addressed_history_path_count": 150, "c_v10_repaired_original_campaign": c, "zig_original_campaign_preflight_failure": old, "zig_v2_original_campaign": zig, "zig_scanner_repaired_matching_status": "FAIL: 2,172 SEMANTIC MISMATCHES", "rust_v3_original_campaign": rust, "rust_v3_original_campaign_status": "FAIL", "rust_v3_original_campaign_actual_candidate_workers": 13, "rust_v3_original_campaign_semantic_mismatch_count": 1087, "rust_v3_original_campaign_verified_passing_case_count": 7438, "rust_v3_original_campaign_infrastructure_failure_count": 0, "rust_dual_overlay_repaired_matching_status": "FAIL: 1,087 SEMANTIC MISMATCHES", "rust_dual_overlay_repaired_candidate_worker_count": 13, "rust_dual_overlay_repaired_candidate_qualified": False, "rust_actual_semantic_mismatch_count": 2042, "zig_actual_semantic_mismatch_count": 1764, "repaired_c_semantic_mismatch_count": 1262, "rust_dual_overlay_repaired_build_process_count": 28, "zig_scanner_repaired_build_process_count": 26, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "hidden_cases_read": 0, "performance_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}

def self_test() -> dict:
    runtime()
    with Wall() as wall:
        base = synthetic()
        validate(base)
        rejected = 0
        changed = {"full_case_denominator": 31236, "suite_count": 12, "baseline_passed": 0, "frozen_independent_engine_family_count": 5, "qualified_candidate_count": 1, "preserved_v27_repository_evidence_owner_count": 142, "preserved_v27_digest_addressed_history_path_count": 147, "new_rust_original_campaign_repository_evidence_owner_count": 1, "all_actual_candidate_and_native_evidence_owner_count": 144, "all_digest_addressed_history_path_count": 149, "rust_v3_original_campaign_status": "PASS", "rust_v3_original_campaign_actual_candidate_workers": 0, "rust_v3_original_campaign_semantic_mismatch_count": 0, "rust_v3_original_campaign_verified_passing_case_count": 31237, "rust_v3_original_campaign_infrastructure_failure_count": 1, "rust_dual_overlay_repaired_matching_status": "PASS", "rust_dual_overlay_repaired_candidate_worker_count": 0, "rust_dual_overlay_repaired_candidate_qualified": True, "rust_actual_semantic_mismatch_count": 0, "zig_actual_semantic_mismatch_count": 0, "repaired_c_semantic_mismatch_count": 0, "rust_dual_overlay_repaired_build_process_count": 27, "zig_scanner_repaired_build_process_count": 25, "performance": "2x faster", "memory": "zero", "confidence_intervals": "95%", "hidden_cases_read": 1, "performance_files_read": 1, "clock_samples": 1, "timing_trials_run": 1, "final_comparison_planned_case_count": 4194303, "final_comparison_cases_generated": True, "final_holdout_opened": True, "winner_selected": True}
        for key, forged in changed.items():
            bad = copy.deepcopy(base)
            bad[key] = forged
            try:
                validate(bad)
            except (GraphError, KeyError, TypeError, ValueError):
                rejected += 1
            else:
                raise GraphError("acceptance of altered V28 result: " + key)
        hostile = {"status": "PASS", "failure_class": "PASS", "publication_status": "FAIL", "publication_pass_means": "CANDIDATE PASSED", "actual_candidate_workers": 0, "completed_suite_count": 12, "case_execution_denominator": 31236, "semantic_mismatch_count": 0, "verified_passing_case_count": 31237, "infrastructure_failure_count": 1, "candidate_qualified": True, "individual_rust_suite_mismatches": "invented", "uncompressed_archive_bytes": PLAIN_SIZE - 1, "uncompressed_archive_sha256": "0" * 64, "uncompressed_archive_opened_by_graph": True, "uncompressed_archive_bytes_read_by_graph": PLAIN_SIZE, "recovery_journal_sha256": "0" * 64, "all_four_original_targets_restored": False, "original_targets_inspected_by_graph": True, "restoration_verified_before_publication": False, "group_atomic": True, "power_failure_automatically_recovered": True, "sigkill_automatically_recovered": True, "new_repository_evidence_owner_count": 1}
        for key, forged in hostile.items():
            bad = copy.deepcopy(base)
            bad["rust_v3_original_campaign"][key] = forged
            try:
                validate(bad)
            except (GraphError, KeyError, TypeError, ValueError):
                rejected += 1
            else:
                raise GraphError("accepted forged actual Rust proof " + key)
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (b"1,087", b"7,438", b"2,172", b"2,847", b"1,262", b"31,237", b"145 / 150", b"13 actual workers", b"NOT MEASURED", b"SETUP STOPPED; 0 TESTS", b"not decompressed", b"not invented"):
            need(phrase.lower() in picture.lower(), "graph omits actual result or invents group detail")
        effects = (lambda: builtins.open("forbidden-v28"), lambda: os.open("forbidden-v28", os.O_RDONLY), lambda: os.stat("forbidden-v28-native"), lambda: subprocess.run(("forbidden-v28",)), lambda: importlib.import_module("candidates.rust_candidate"), lambda: socket.socket(), lambda: tempfile.mkdtemp(), lambda: time.perf_counter(), lambda: threading.Thread(target=lambda: None).start())
        for effect in effects:
            try:
                effect()
            except GraphError:
                continue
            raise GraphError("source-only side effect not blocked")
        need(wall.blocked == len(effects), "require physical source-only boundary")
        return {"schema": SCHEMA + "-source-only-self-test", "status": "PASS", "version": 28, "synthetic_only": True, "rejected_hostile_control_count": rejected, "blocked_effect_count": wall.blocked, "full_case_denominator": 31237, "suite_count": 13, "repository_evidence_owner_count": 145, "authenticated_digest_addressed_history_paths": 150, "actual_rust_candidate_workers": 13, "actual_rust_semantic_mismatch_count": 1087, "actual_rust_verified_passing_case_count": 7438, "actual_rust_infrastructure_failure_count": 0, "actual_zig_candidate_workers": 13, "actual_zig_semantic_mismatch_count": 2172, "historical_zig_preflight_candidate_workers": 0, "actual_c_semantic_mismatch_count": 1262, "journal_sha256": JOURNAL, "uncompressed_rust_archive_opened": False, "uncompressed_rust_archive_bytes_read": 0, "actual_candidate_workers_started_by_graph": 0, "canonical_target_reads": 0, "canonical_target_stats": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "workspace_mutations": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}

def publish(path: str, raw: bytes) -> None:
    need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"} and type(raw) is bytes and 0 < len(raw) <= LIMIT, "publish only bounded new V28 owner")
    fd = os.open(str(ROOT / path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    try:
        pos = 0
        while pos < len(raw):
            n = os.write(fd, raw[pos:])
            need(type(n) is int and n > 0, "reject incomplete exclusive graph")
            pos += n
        os.fsync(fd)
        s = os.fstat(fd)
        need(s.st_size == len(raw) and s.st_nlink == 1 and stat.S_IMODE(s.st_mode) == 0o600, "reject changed V28 output")
    finally:
        os.close(fd)

def result(source: str, archive: str, receipt: str, outputs: dict[str, bytes], written: bool, suffix: str) -> dict:
    return {"schema": SCHEMA + suffix, "version": 28, "status": "PASS", "source_sha256": source, "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]), "summary_sha256": digest(outputs[OUTPUT + ".json"]), "svg_sha256": digest(outputs[OUTPUT + ".svg"]), "actual_rust_campaign_archive_sha256": archive, "actual_rust_campaign_receipt_sha256": receipt, "suite_count": 13, "full_case_denominator": 31237, "private_waiver_count": 13, "qualified_candidate_count": 0, "preserved_v27_repository_evidence_owner_count": 143, "preserved_v27_authenticated_reference_count": 148, "new_actual_rust_campaign_evidence_owner_count": 2, "repository_evidence_owner_count": 145, "authenticated_digest_addressed_history_paths": 150, "rust_matching_status": "FAIL", "actual_rust_candidate_workers": 13, "actual_rust_semantic_mismatch_count": 1087, "actual_rust_verified_passing_case_count": 7438, "actual_rust_infrastructure_failure_count": 0, "rust_recovery_journal_sha256": JOURNAL, "all_four_original_rust_targets_restored": True, "rust_receipt_status": "PASS", "rust_receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "actual_zig_candidate_workers": 13, "actual_zig_semantic_mismatch_count": 2172, "actual_zig_verified_passing_case_count": 2847, "historical_zig_preflight_candidate_workers": 0, "actual_c_semantic_mismatch_count": 1262, "actual_c_candidate_workers": 13, "uncompressed_rust_archive_opened": False, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_zig_archive_opened": False, "outputs_written": written, "actual_candidate_workers_started_by_graph": 0, "actual_candidate_imports": 0, "actual_native_activations": 0, "canonical_target_reads": 0, "canonical_target_stats": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}

def main(args: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test", action="store_true")
    g.add_argument("--render", action="store_true")
    g.add_argument("--verify-frozen-context", action="store_true")
    for name in ("--source-sha256", "--campaign-archive-sha256", "--campaign-receipt-sha256", "--inputs-sha256", "--summary-sha256", "--svg-sha256"):
        p.add_argument(name)
    a = p.parse_args(args)
    try:
        runtime()
        if a.self_test:
            need(all(getattr(a, n) is None for n in ("source_sha256", "campaign_archive_sha256", "campaign_receipt_sha256", "inputs_sha256", "summary_sha256", "svg_sha256")), "synthetic mode cannot authorize actual evidence or matching")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        s, ar, rr = checked(a.source_sha256, "V28 source"), checked(a.campaign_archive_sha256, "actual Rust archive"), checked(a.campaign_receipt_sha256, "actual Rust receipt")
        _snapshot, values = build(s, ar, rr)
        outputs = dict(values)
        if a.render:
            need(a.inputs_sha256 is None and a.summary_sha256 is None and a.svg_sha256 is None, "reject substituted render pins")
            for path, raw in values:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(s, ar, rr, outputs, True, "-published")))
            return 0
        frozen = {OUTPUT + ".inputs.json": checked(a.inputs_sha256, "V28 inputs"), OUTPUT + ".json": checked(a.summary_sha256, "V28 summary"), OUTPUT + ".svg": checked(a.svg_sha256, "V28 SVG")}
        for path, fingerprint in frozen.items():
            raw, _ = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(raw == outputs[path], "independently reproduce every V28 owner")
        sys.stdout.buffer.write(canonical(result(s, ar, rr, outputs, False, "-read-only-frozen-context")))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError, KeyError, AttributeError, struct.error) as error:
        sys.stderr.write("current V28 overview rejected: " + str(error) + "\n")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
