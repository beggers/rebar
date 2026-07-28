#!/usr/bin/env python3
"""Show the real full-suite Zig failure without inventing speed or suite rows."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import importlib
import io
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
SELF = "tools/render_candidate_current_overview_v27.py"
OUTPUT = "docs/evidence/candidate-current-overview-v27"
SCHEMA = "rebar-candidate-current-overview-v27"
MAX_OWNER = 8 * 1024 * 1024
V26 = {
    "source": ("tools/render_candidate_current_overview_v26.py",
               "55c36e916f0da8b9ef7b6992724d1d1f98161e834f4d2d21729663d9671a3982", 80805),
    "inputs": ("docs/evidence/candidate-current-overview-v26.inputs.json",
               "c29e8df08d9b5a03eaad283b625465ba6638f19f69d7d3ab4ea5512e83c37685", 36434),
    "summary": ("docs/evidence/candidate-current-overview-v26.json",
                "8ebf2ccb74ae2cf62196a1507f94bd39ff4b103122c450865121306accf71f48", 186394),
    "svg": ("docs/evidence/candidate-current-overview-v26.svg",
            "52b42c7ceccf45f80777d94820a812c7f8e0f790fba03a57aef28c11573dd9cc", 12936),
}
CAMPAIGN = {
    "source": ("tools/run_owned_repaired_zig_original_campaign_v2.py",
               "a9f62061f709583c60a4d0b72ba1150931132a66b80b6eed1081e017fd389795", 141031),
    "protocol": ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V2.md",
                 "fe17a8fc4e5fb5638ff92caa6e1b6d625e93dfb27ced02ba7b1490b830356db3", 6075),
    "contract": ("oracle/phase2/repaired-zig-original-campaign-v2.json",
                 "0112748e8dbca769625ea2643643fad81ced069e20ed87a458bebe0a922d2851", 15015),
}
ACTUAL_ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz",
    "583d63c92240cec78c861893407003466a5f754b099719aabfc8eaf4f14fbbf8",
    5870948, 2064, 524614,
)
ACTUAL_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-"
    "failures-publication-receipt.json",
    "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba",
    4534, 2064, 524615,
)
EXPANDED_SHA256 = "c6bb2272f13595fc65a4d83feed12f10412706819962b0c18ba96c2ee01d68ce"
EXPANDED_BYTES = 198178404
LABEL = "phase2-v11-zig-scanner-original-p0"
SUITES = (
    ("original_bounded_v5", 151, 0, "Core Python behavior"),
    ("public_v3", 864, 0, "Everyday public methods"),
    ("scanner_v3", 1024, 0, "Scanning and callbacks"),
    ("buffer_v3", 768, 0, "Buffers and memory views"),
    ("managed_v1", 1024, 0, "Buffer lifetime"),
    ("scanner_verbose_v1", 2854, 0, "Verbose patterns"),
    ("public_types_v1", 6912, 248, "Public types and serialization"),
    ("substitution_v2", 5120, 224, "Substitutions"),
    ("shape_v2", 10240, 672, "Result shapes"),
    ("public_surface_v19", 1376, 114, "Full public interface"),
    ("subinterpreter_v2", 128, 0, "Subinterpreters"),
    ("pep688_v4", 264, 4, "Python buffer exporters"),
    ("threaded_pattern_v1", 512, 0, "Patterns across threads"),
)
ORIGINALS = {
    "bridge": ("candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
               "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b",
               134112, 2064, 431274),
    "engine": ("candidates/_zig_probe.so",
               "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
               478432, 2064, 431260),
}


class GraphError(Exception):
    """The actual original matching result or its history is not authenticated."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only bounded exact original evidence bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise GraphError("reject noncanonical V27 evidence") from error


def checked_digest(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(part in "0123456789abcdef" for part in value),
         "independently pin the exact SHA-256 of " + label)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON,
         "use only exact isolated, bytecode-free CPython 3.14.6")


def document(raw: bytes, label: str) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        output: dict[str, object] = {}
        for key, value in pairs:
            need(key not in output, "reject duplicate JSON keys in " + label)
            output[key] = value
        return output

    def no_constant(value: str) -> object:
        raise GraphError("reject nonfinite JSON in " + label + ": " + value)

    try:
        output = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                            parse_constant=no_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed JSON in " + label) from error
    need(type(output) is dict and canonical(output) == raw,
         "require exact canonical published JSON for " + label)
    return output


def read_owner(path: str, fingerprint: str, size: int | None = None,
               *, private: bool = False, device: int | None = None,
               inode: int | None = None) -> tuple[bytes, dict]:
    need(type(path) is str and bool(path) and not path.startswith("/")
         and ".." not in Path(path).parts,
         "read only an explicitly frozen relative evidence owner")
    checked_digest(fingerprint, path)
    descriptor = os.open(str(ROOT / path),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        first = os.fstat(descriptor)
        need(stat.S_ISREG(first.st_mode)
             and first.st_nlink == 1 and 0 <= first.st_size <= MAX_OWNER
             and (size is None or first.st_size == size)
             and (not private or stat.S_IMODE(first.st_mode) == 0o600)
             and (device is None or first.st_dev == device)
             and (inode is None or first.st_ino == inode),
             "reject absent, linked, nonprivate, oversized, or changed owner " + path)
        remaining = first.st_size
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            need(bool(block), "reject a truncated actual evidence owner " + path)
            blocks.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"",
             "reject hidden additional evidence bytes " + path)
        raw = b"".join(blocks)
        last = os.fstat(descriptor)
        need((first.st_dev, first.st_ino, first.st_size, first.st_nlink)
             == (last.st_dev, last.st_ino, last.st_size, last.st_nlink)
             and digest(raw) == fingerprint,
             "reject changed owner identity or an actual evidence digest mismatch " + path)
        return raw, {
            "path": path, "sha256": fingerprint, "bytes": len(raw),
            "device": last.st_dev, "inode": last.st_ino,
            "mode": f"{stat.S_IMODE(last.st_mode):04o}",
            "nlink": last.st_nlink, "uid": last.st_uid,
        }
    finally:
        os.close(descriptor)


def pin(path: str, fingerprint: str, count: int) -> dict:
    checked_digest(fingerprint, path)
    need(type(count) is int and 0 <= count <= MAX_OWNER,
         "bound every actual graph, source, and receipt owner")
    return {"path": path, "sha256": fingerprint, "bytes": count}


def load_module(owner: tuple[str, str, int], name: str) -> types.ModuleType:
    raw, _proof = read_owner(owner[0], owner[1], owner[2])
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / owner[0])
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    return module


def authenticate_v26() -> tuple[types.ModuleType, dict, dict, dict[str, str]]:
    previous = load_module(V26["source"], "_rebar_exact_candidate_overview_v26_for_v27")
    need(previous.SCHEMA == "rebar-candidate-current-overview-v26"
         and previous.SELF == V26["source"][0]
         and tuple(previous.SUITES) == SUITES,
         "load only the exact independently published V26 renderer and original suites")
    _v25, _v25_summary, _v25_inputs, references = previous.authenticate_v25()
    need(len(references) == 144,
         "retain every independently authenticated historical V25 reference")
    preflight, additions = previous.authenticate_failure(
        previous.FAILURE_ARCHIVE[1], previous.FAILURE_RECEIPT[1], references,
    )
    need(len(additions) == 2 and not (set(references) & set(additions)),
         "retain both genuinely distinct original zero-worker failure owners")
    references = dict(references)
    references.update(additions)
    need(len(references) == 146,
         "derive all genuine V26 authenticated history references")
    owners: dict[str, bytes] = {}
    for key, frozen in sorted(V26.items()):
        owners[key], _record = read_owner(frozen[0], frozen[1], frozen[2])
    summary = document(owners["summary"], "actual published V26 summary")
    inputs = document(owners["inputs"], "actual published V26 inputs")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict,
         "retain the full released V26 actual-result snapshot")
    previous.validate_snapshot(snapshot)
    need(summary.get("schema") == previous.SCHEMA + "-summary"
         and summary.get("status") == "PASS"
         and summary.get("repository_evidence_owner_count") == 141
         and summary.get("authenticated_digest_addressed_history_paths") == 146
         and summary.get("full_case_denominator") == 31237
         and summary.get("suite_count") == 13
         and summary.get("private_waiver_count") == 13
         and summary.get("qualified_candidate_count") == 0
         and summary.get("performance") == "NOT MEASURED"
         and summary.get("memory") == "NOT MEASURED"
         and summary.get("final_holdout_opened") is False
         and type(summary.get("families")) is list
         and len(summary["families"]) == 7
         and inputs.get("schema") == previous.SCHEMA + "-inputs"
         and inputs.get("repository_evidence_owner_count") == 141
         and inputs.get("all_digest_addressed_history_path_count") == 146
         and snapshot.get("zig_original_campaign_preflight_failure") == preflight
         and owners["svg"] == previous.make_svg(
             snapshot, V26["source"][1], V26["inputs"][1]),
         "independently reproduce all four actual V26 owners and retained first failure")
    return previous, summary, inputs, references


def authenticate_actual_campaign(archive_sha: str, receipt_sha: str,
                                 references: dict[str, str]) -> tuple[dict, dict[str, str]]:
    need(checked_digest(archive_sha, "actual full Zig matching failure archive")
         == ACTUAL_ARCHIVE[1]
         and checked_digest(receipt_sha, "actual full Zig matching failure receipt")
         == ACTUAL_RECEIPT[1],
         "independently caller-pin the two real corrected original Zig result owners")
    for key, frozen in sorted(CAMPAIGN.items()):
        raw, _owner = read_owner(frozen[0], frozen[1], frozen[2])
        if key == "contract":
            contract = document(raw, "genuine pushed corrected Zig campaign contract")
            need(contract.get("schema")
                 == "rebar-owned-repaired-zig-original-campaign-v2-source-freeze"
                 and contract.get("version") == 2
                 and contract.get("family") == "zig"
                 and contract.get("phase") == "CANDIDATES"
                 and contract.get("status")
                 == "SOURCE FROZEN; V2 ZIG CANDIDATE NOT YET RUN",
                 "retain the exact genuine corrected original campaign source freeze")
    compressed, archive_owner = read_owner(
        ACTUAL_ARCHIVE[0], archive_sha, ACTUAL_ARCHIVE[2], private=True,
        device=ACTUAL_ARCHIVE[3], inode=ACTUAL_ARCHIVE[4],
    )
    receipt_raw, receipt_owner = read_owner(
        ACTUAL_RECEIPT[0], receipt_sha, ACTUAL_RECEIPT[2], private=True,
        device=ACTUAL_RECEIPT[3], inode=ACTUAL_RECEIPT[4],
    )
    need((archive_owner["device"], archive_owner["inode"])
         != (receipt_owner["device"], receipt_owner["inode"])
         and archive_owner["uid"] == receipt_owner["uid"] == 1000
         and archive_owner["path"] not in references
         and receipt_owner["path"] not in references
         and len(compressed) >= 18
         and compressed[:3] == b"\x1f\x8b\x08"
         and struct.unpack("<I", compressed[4:8])[0] == 0
         and struct.unpack("<I", compressed[-4:])[0] == EXPANDED_BYTES,
         "authenticate distinct canonical compressed owners without inflating 198 MB")
    receipt = document(receipt_raw, "actual independently durable Zig matching receipt")
    recorded = receipt.get("archive")
    need(type(recorded) is dict
         and receipt.get("schema")
         == "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt"
         and receipt.get("status") == "PASS"
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("family") == "zig"
         and receipt.get("label") == LABEL
         and receipt.get("campaign_source_sha256") == CAMPAIGN["source"][1]
         and receipt.get("campaign_protocol_sha256") == CAMPAIGN["protocol"][1]
         and receipt.get("campaign_contract_sha256") == CAMPAIGN["contract"][1]
         and recorded.get("path") == str(ROOT / ACTUAL_ARCHIVE[0])
         and recorded.get("relative") == ACTUAL_ARCHIVE[0].rsplit("/", 1)[-1]
         and recorded.get("sha256") == archive_owner["sha256"]
         and recorded.get("size_bytes") == archive_owner["bytes"]
         and recorded.get("device") == archive_owner["device"]
         and recorded.get("inode") == archive_owner["inode"]
         and recorded.get("mode") == 0o600
         and recorded.get("exclusive_creation") is True
         and recorded.get("file_fsync_completed") is True
         and recorded.get("directory_fsync_completed") is True
         and recorded.get("same_inode_readback_verified") is True
         and recorded.get("streaming_readback_verified") is True
         and type(recorded.get("write_calls")) is int
         and recorded["write_calls"] > 0
         and receipt.get("uncompressed_bytes") == EXPANDED_BYTES
         and receipt.get("uncompressed_sha256") == EXPANDED_SHA256
         and type(receipt.get("uncompressed_chunk_count")) is int
         and receipt["uncompressed_chunk_count"] > 0,
         "bind the bounded real gzip to the exact durable complete matching-failure receipt")
    need(receipt.get("suite_count") == 13
         and receipt.get("completed_suite_count") == 13
         and receipt.get("case_execution_denominator") == 31237
         and receipt.get("named_private_waiver_count") == 13
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("semantic_mismatch_count") == 2172
         and receipt.get("verified_passing_case_count") == 2847
         and receipt.get("infrastructure_failure_count") == 0
         and receipt.get("all_original_suite_streams_retained") is True
         and receipt.get("candidate_qualified") is False
         and receipt.get("original_native_restored") is True
         and receipt.get("restoration_verified_before_publication") is True
         and receipt.get("group_atomic") is False
         and receipt.get("actual_first_v1_attempt_status") == "FAIL"
         and receipt.get("actual_first_v1_candidate_workers") == 0
         and receipt.get("actual_first_v1_matching_case_execution_count") == 0
         and receipt.get("actual_first_v1_receipt_pass_means")
         == "DURABLE FAILURE PUBLICATION ONLY"
         and receipt.get("published_v26_evidence_owner_count") == 141
         and receipt.get("published_v26_authenticated_reference_count") == 146
         and receipt.get("historical_v25_evidence_owner_count") == 139
         and receipt.get("historical_v25_authenticated_reference_count") == 144
         and receipt.get("actual_c_semantic_mismatch_count") == 1262
         and receipt.get("actual_rust_compiler_process_count") == 28
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("benchmark_files_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("memory") == "NOT MEASURED"
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("winner_selected") is False,
         "require actual 13 Zig workers and 2,172 differences, never a receipt-as-pass")
    first_archive = receipt.get("actual_first_v1_failure_archive")
    first_receipt = receipt.get("actual_first_v1_failure_receipt")
    need(type(first_archive) is dict and type(first_receipt) is dict
         and first_archive.get("sha256")
         == "1cb38eb48a2d3305ea98d5103a27ce6ae758137168f68df07a408dec3d055a37"
         and first_receipt.get("sha256")
         == "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23",
         "preserve the distinct genuinely archived earlier zero-worker setup failure")
    restored = receipt.get("restored_original_targets")
    need(type(restored) is dict and set(restored) == {"bridge", "engine"},
         "retain both actual restored original Zig native identities")
    for role, (path, fingerprint, count, device, inode) in ORIGINALS.items():
        owner = restored[role]
        need(type(owner) is dict and owner.get("relative") == path
             and owner.get("path") == str(ROOT / path)
             and owner.get("sha256") == fingerprint
             and owner.get("size_bytes") == count
             and owner.get("device") == device
             and owner.get("inode") == inode
             and owner.get("mode") == 0o700
             and owner.get("nlink") == 1 and owner.get("uid") == 1000,
             "authenticate receipt-preserved original Zig " + role
             + " without opening its native target")
    additions = {
        archive_owner["path"]: archive_owner["sha256"],
        receipt_owner["path"]: receipt_owner["sha256"],
    }
    need(len(additions) == 2 and not (set(references) & set(additions)),
         "count only two truly new digest-addressed full-campaign evidence owners")
    proof = {
        "schema": SCHEMA + "-authenticated-complete-zig-matching-failure",
        "status": "FAIL",
        "failure_class": "SEMANTIC MISMATCH",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "family": "zig", "label": LABEL,
        "archive": archive_owner, "receipt": receipt_owner,
        "publication_receipt": receipt,
        "suite_count": 13, "completed_suite_count": 13,
        "case_execution_denominator": 31237,
        "private_waiver_count": 13,
        "actual_candidate_workers": 13,
        "semantic_mismatch_count": 2172,
        "verified_passing_case_count": 2847,
        "infrastructure_failure_count": 0,
        "all_original_suite_streams_retained": True,
        "individual_zig_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "uncompressed_archive_sha256": EXPANDED_SHA256,
        "uncompressed_archive_bytes": EXPANDED_BYTES,
        "uncompressed_archive_opened_by_graph": False,
        "uncompressed_archive_bytes_read_by_graph": 0,
        "original_native_restored": True,
        "original_native_targets_inspected_by_graph": False,
        "restored_original_targets": copy.deepcopy(restored),
        "restoration_order": ["bridge", "engine"],
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "candidate_qualified": False,
        "new_repository_evidence_owner_count": len(additions),
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, additions


def validate_proof(proof: object) -> None:
    need(type(proof) is dict
         and proof.get("schema") == SCHEMA + "-authenticated-complete-zig-matching-failure"
         and proof.get("status") == "FAIL"
         and proof.get("failure_class") == "SEMANTIC MISMATCH"
         and proof.get("publication_status") == "PASS"
         and proof.get("publication_pass_means") == "DURABLE FAILURE PUBLICATION ONLY"
         and proof.get("family") == "zig" and proof.get("label") == LABEL
         and proof.get("suite_count") == 13
         and proof.get("completed_suite_count") == 13
         and proof.get("case_execution_denominator") == 31237
         and proof.get("private_waiver_count") == 13
         and proof.get("actual_candidate_workers") == 13
         and proof.get("semantic_mismatch_count") == 2172
         and proof.get("verified_passing_case_count") == 2847
         and proof.get("infrastructure_failure_count") == 0
         and proof.get("all_original_suite_streams_retained") is True
         and proof.get("individual_zig_suite_mismatches")
         == "NOT PRESENT IN DURABLE RECEIPT"
         and proof.get("uncompressed_archive_sha256") == EXPANDED_SHA256
         and proof.get("uncompressed_archive_bytes") == EXPANDED_BYTES
         and proof.get("uncompressed_archive_opened_by_graph") is False
         and proof.get("uncompressed_archive_bytes_read_by_graph") == 0
         and proof.get("original_native_restored") is True
         and proof.get("original_native_targets_inspected_by_graph") is False
         and proof.get("restoration_order") == ["bridge", "engine"]
         and proof.get("restoration_verified_before_publication") is True
         and proof.get("group_atomic") is False
         and proof.get("candidate_qualified") is False
         and proof.get("new_repository_evidence_owner_count") == 2
         and proof.get("performance") == "NOT MEASURED"
         and proof.get("memory") == "NOT MEASURED"
         and proof.get("undefined_behavior") == "NOT MEASURED"
         and proof.get("holdout") == "NOT OPENED"
         and proof.get("winner_selected") is False,
         "retain a real 13-worker Zig mismatch, never an invented pass or inflated archive")
    archive, receipt = proof.get("archive"), proof.get("receipt")
    need(type(archive) is dict and type(receipt) is dict
         and archive.get("path") == ACTUAL_ARCHIVE[0]
         and archive.get("sha256") == ACTUAL_ARCHIVE[1]
         and archive.get("bytes") == ACTUAL_ARCHIVE[2]
         and archive.get("device") == ACTUAL_ARCHIVE[3]
         and archive.get("inode") == ACTUAL_ARCHIVE[4]
         and archive.get("mode") == "0600"
         and archive.get("nlink") == 1 and archive.get("uid") == 1000
         and receipt.get("path") == ACTUAL_RECEIPT[0]
         and receipt.get("sha256") == ACTUAL_RECEIPT[1]
         and receipt.get("bytes") == ACTUAL_RECEIPT[2]
         and receipt.get("device") == ACTUAL_RECEIPT[3]
         and receipt.get("inode") == ACTUAL_RECEIPT[4]
         and receipt.get("mode") == "0600"
         and receipt.get("nlink") == 1 and receipt.get("uid") == 1000
         and (archive["device"], archive["inode"])
         != (receipt["device"], receipt["inode"]),
         "reject missing, linked, substituted, nonprivate, or duplicate campaign owners")
    recorded = proof.get("publication_receipt")
    need(type(recorded) is dict and recorded.get("status") == "PASS"
         and recorded.get("candidate_status") == "FAIL"
         and recorded.get("actual_candidate_workers") == 13
         and recorded.get("semantic_mismatch_count") == 2172
         and recorded.get("verified_passing_case_count") == 2847
         and recorded.get("infrastructure_failure_count") == 0,
         "never count a durable publication receipt as a candidate correctness pass")


def validate_snapshot(snapshot: object) -> None:
    need(type(snapshot) is dict
         and snapshot.get("full_case_denominator") == 31237
         and snapshot.get("suite_count") == 13
         and tuple(snapshot.get("suite_ids", ()))
         == tuple(name for name, _count, _loss, _display in SUITES)
         and snapshot.get("baseline_passed") == 31237
         and snapshot.get("frozen_independent_engine_family_count") == 6
         and snapshot.get("qualified_candidate_count") == 0
         and snapshot.get("preserved_v26_repository_evidence_owner_count") == 141
         and snapshot.get("preserved_v26_digest_addressed_history_path_count") == 146
         and snapshot.get("new_zig_original_campaign_repository_evidence_owner_count") == 2
         and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 143
         and snapshot.get("all_digest_addressed_history_path_count") == 148,
         "derive actual 141+2/146+2 while preserving all original Python checks")
    c = snapshot.get("c_v10_repaired_original_campaign")
    need(type(c) is dict and c.get("status") == "FAIL"
         and c.get("actual_candidate_workers") == 13
         and c.get("completed_suite_count") == 13
         and c.get("fully_passing_suite_count") == 8
         and c.get("observed_matching_case_count") == 31237
         and c.get("verified_passing_case_count") == 7325
         and c.get("semantic_mismatch_count") == 1262
         and c.get("infrastructure_failure_count") == 0
         and c.get("all_original_suite_evidence_preserved") is True
         and c.get("original_canonical_native_restored") is True
         and c.get("qualified") is False,
         "retain the complete measured C campaign and all 1,262 genuine losses")
    rows = c.get("suite_results")
    need(type(rows) is list and len(rows) == 13,
         "retain all thirteen independently recorded C case-group results")
    for row, (name, count, losses, display) in zip(rows, SUITES, strict=True):
        need(type(row) is dict and row.get("suite") == name
             and row.get("display_name") == display
             and row.get("case_execution_denominator") == count
             and row.get("mismatch_count") == losses
             and row.get("status") == ("PASS" if losses == 0 else "FAIL")
             and row.get("actual_worker_started") is True
             and row.get("all_original_records_and_mismatches_preserved") is True,
             "reject a changed original C result: " + name)
    old = snapshot.get("zig_original_campaign_preflight_failure")
    need(type(old) is dict and old.get("status") == "FAIL"
         and old.get("failure_class") == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
         and old.get("actual_candidate_workers") == 0
         and old.get("actual_matching_case_execution_count") == 0
         and old.get("candidate_correctness") == "NOT MEASURED"
         and snapshot.get("zig_original_campaign_attempt_count") == 1
         and snapshot.get("zig_original_campaign_controller_exit_status") == 1
         and snapshot.get("zig_original_campaign_controller_process_id") == "NOT RECORDED"
         and snapshot.get("zig_original_campaign_actual_candidate_worker_count") == 0
         and snapshot.get("zig_original_campaign_actual_matching_case_count") == 0,
         "retain the separate earlier actual zero-worker Zig setup failure")
    validate_proof(snapshot.get("zig_v2_original_campaign"))
    need(snapshot.get("zig_v2_original_campaign_status") == "FAIL"
         and snapshot.get("zig_v2_original_campaign_failure_class") == "SEMANTIC MISMATCH"
         and snapshot.get("zig_v2_original_campaign_actual_candidate_workers") == 13
         and snapshot.get("zig_v2_original_campaign_completed_suite_count") == 13
         and snapshot.get("zig_v2_original_campaign_case_execution_denominator") == 31237
         and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count") == 2172
         and snapshot.get("zig_v2_original_campaign_verified_passing_case_count") == 2847
         and snapshot.get("zig_v2_original_campaign_infrastructure_failure_count") == 0
         and snapshot.get("zig_v2_original_campaign_original_targets_restored") is True
         and snapshot.get("zig_scanner_repaired_matching_status")
         == "FAIL: 2,172 SEMANTIC MISMATCHES"
         and snapshot.get("zig_scanner_repaired_candidate_worker_count") == 13
         and snapshot.get("zig_scanner_repaired_candidate_qualified") is False,
         "report the genuine complete repaired Zig mismatch, not an untested candidate")
    need(snapshot.get("c_actual_semantic_mismatch_count") == 2094
         and snapshot.get("c_verified_passing_case_executions") == 7197
         and snapshot.get("rust_actual_semantic_mismatch_count") == 2042
         and snapshot.get("rust_verified_passing_case_executions") == 7461
         and snapshot.get("zig_actual_semantic_mismatch_count") == 1764
         and snapshot.get("zig_verified_passing_case_executions") == 3583
         and type(snapshot.get("cpp_full_original_campaign")) is dict
         and snapshot["cpp_full_original_campaign"].get("semantic_mismatch_count") == 2308
         and type(snapshot.get("go_v2_full_original_campaign")) is dict
         and snapshot["go_v2_full_original_campaign"].get("semantic_mismatch_count") == 4518
         and snapshot.get("zig_scanner_repaired_build_status") == "PASS"
         and snapshot.get("zig_scanner_repaired_build_process_count") == 26
         and snapshot.get("zig_scanner_repaired_source_apply_count") == 2
         and snapshot.get("zig_scanner_repaired_reproducibility") == "PASS"
         and snapshot.get("rust_dual_overlay_repaired_build_status") == "PASS"
         and snapshot.get("rust_dual_overlay_repaired_build_process_count") == 28
         and snapshot.get("rust_dual_overlay_repaired_bridge_source_apply_count") == 2
         and snapshot.get("rust_dual_overlay_repaired_public_source_apply_count") == 2
         and snapshot.get("rust_dual_overlay_repaired_reproducibility") == "PASS"
         and snapshot.get("rust_dual_overlay_repaired_matching_status") == "NOT MEASURED"
         and snapshot.get("rust_dual_overlay_repaired_candidate_worker_count") == 0
         and snapshot.get("rust_dual_overlay_repaired_candidate_qualified") is False
         and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
         and snapshot.get("repaired_c_verified_passing_case_count") == 7325
         and snapshot.get("repaired_c_actual_candidate_worker_count") == 13,
         "preserve every old language-family loss and honest untested repaired Rust")
    need(snapshot.get("performance") == "NOT MEASURED"
         and snapshot.get("memory") == "NOT MEASURED"
         and snapshot.get("confidence_intervals") == "NOT MEASURED"
         and snapshot.get("hidden_cases_read") == 0
         and snapshot.get("performance_files_read") == 0
         and snapshot.get("clock_samples") == 0
         and snapshot.get("timing_trials_run") == 0
         and snapshot.get("final_comparison_planned_case_count") == 4194304
         and snapshot.get("final_comparison_cases_generated") is False
         and snapshot.get("final_holdout_opened") is False
         and snapshot.get("winner_selected") is False,
         "never infer speed, ranking, confidence, or a winner from matching evidence")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def make_svg(snapshot: dict, source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(snapshot)
    checked_digest(source_sha, "frozen V27 renderer")
    checked_digest(inputs_sha, "frozen V27 inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1970" viewBox="0 0 1440 1970" role="img" aria-labelledby="v27-title v27-description">',
        '<title id="v27-title">Building a faster Python re: the repaired Zig engine fails the complete matching test</title>',
        '<desc id="v27-description">Python passes all 31,237 original checks. The independently built repaired Zig engine really ran all 13 original test workers and produced 2,172 recorded matching differences, 2,847 verified passing checks, and zero worker infrastructure failures. Its exact original native bridge and engine were restored. Its earlier separate setup failure started zero workers. The C engine has 1,262 recorded differences. The independently repaired Rust engine built successfully but has not yet run the matching tests. All 143 genuine evidence files and 148 authenticated references are retained. No external regular-expression engine is used and no replacement is fully compatible. Speed, memory, undefined behavior, confidence intervals, and rankings have not been measured; the 4,194,304-case holdout remains unopened. The large actual matching archive is authenticated without decompressing it.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:31px;font-weight:760;fill:#16324f}.heading{font-size:22px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:16px;font-weight:720;fill:#16324f}.pass{font-size:14px;font-weight:750;fill:#00794c}.fail{font-size:14px;font-weight:740;fill:#a15e00}.pending{font-size:14px;font-weight:740;fill:#53667b}.big{font-size:23px;font-weight:760;fill:#16324f}.small{font-size:13px;fill:#42556c}.foot{font-size:11px;fill:#53667b}</style>',
        '<rect width="1440" height="1970" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="61" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="46" y="91" class="body">The repaired Zig engine really ran the full test: 2,172 matching differences. Speed is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0", "compatible replacements"),
        ("2,172", "measured Zig differences"),
        ("1,262", "measured C differences"),
        ("NOT MEASURED", "speed versus Python"),
        ("143 / 148", "evidence files / references"),
    )
    for index, (value, label) in enumerate(cards):
        x = 44 + index * 226
        lines.extend((
            f'<rect x="{x}" y="111" width="216" height="96" rx="12" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 11}" y="151" class="big">{xml(value)}</text>',
            f'<text x="{x + 11}" y="181" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="224" width="1352" height="791" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="262" class="heading">1. Does each replacement work like Python?</text>',
        '<text x="65" y="287" class="body">Only an actual complete matching run counts. Preserving a failure does not turn it into a pass.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original Python checks pass.", "pass"),
        ("Zig — newly repaired engine", "NOT COMPATIBLE", "13 actual workers; 2,172 measured differences; 2,847 verified passing checks; 0 worker failures.", "fail"),
        ("C — latest repaired engine", "NOT COMPATIBLE", "13 actual workers; 1,262 measured differences; 7,325 verified passing checks.", "fail"),
        ("Rust — newly repaired engine", "BUILT; MATCHING NOT MEASURED", "28 genuine first-party build and inspection steps; the repaired matcher has not been tested.", "pending"),
        ("Zig — first setup attempt", "SETUP STOPPED; 0 TESTS", "Separate earlier controller failure; no candidate activated and no matching worker started.", "fail"),
        ("Rust — previously tested engine", "NOT COMPATIBLE", "7,461 verified passing checks; 2,042 recorded matching differences.", "fail"),
        ("Zig — previously tested engine", "NOT COMPATIBLE", "3,583 verified passing checks; 1,764 recorded matching differences.", "fail"),
        ("C — earlier tested engine", "NOT COMPATIBLE", "7,197 verified passing checks; 2,094 recorded matching differences.", "fail"),
        ("C++", "NOT COMPATIBLE", "128 verified passing checks; 2,308 recorded differences and 5 earlier worker failures.", "fail"),
        ("Go", "NOT COMPATIBLE", "128 verified passing checks; 4,518 recorded differences and 4 earlier worker failures.", "fail"),
        ("Fortran", "NOT READY", "Its independent build attempts differ; no compatible matching engine is established.", "pending"),
    )
    for index, (name, outcome, detail, category) in enumerate(rows):
        y = 305 + index * 61
        lines.extend((
            f'<rect x="63" y="{y}" width="1314" height="54" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="79" y="{y + 21}" class="name">{xml(name)}</text>',
            f'<text x="1358" y="{y + 21}" class="{category}" text-anchor="end">{xml(outcome)}</text>',
            f'<text x="81" y="{y + 42}" class="small">{xml(detail)}</text>',
        ))
    lines.append('<text x="65" y="999" class="body">All Zig worker streams are archived. Per-group Zig difference counts are not in the receipt and are not invented.</text>')
    lines.extend((
        '<rect x="44" y="1032" width="1352" height="514" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1070" class="heading">2. Which complete C test groups still differ?</text>',
        '<text x="65" y="1095" class="body">These are actual recorded C group results. The separate complete Zig archive is not decompressed by this graph.</text>',
        '<text x="80" y="1119" class="small">ORIGINAL PYTHON TEST GROUP</text>',
        '<text x="1040" y="1119" class="small" text-anchor="end">CHECKS</text>',
        '<text x="1355" y="1119" class="small" text-anchor="end">C RESULT</text>',
    ))
    for index, row in enumerate(snapshot["c_v10_repaired_original_campaign"]["suite_results"]):
        y = 1130 + index * 28
        background = "#f8fafd" if index % 2 == 0 else "#ffffff"
        answer = ("PASSED" if row["mismatch_count"] == 0
                  else f'{row["mismatch_count"]:,} DIFFERENCES')
        category = "pass" if row["mismatch_count"] == 0 else "fail"
        lines.extend((
            f'<rect x="64" y="{y}" width="1312" height="25" rx="4" fill="{background}"/>',
            f'<text x="80" y="{y + 18}" class="small">{xml(row["display_name"])}</text>',
            f'<text x="1040" y="{y + 18}" class="small" text-anchor="end">{row["case_execution_denominator"]:,}</text>',
            f'<text x="1355" y="{y + 18}" class="{category}" text-anchor="end">{xml(answer)}</text>',
        ))
    lines.extend((
        '<text x="66" y="1514" class="body">C: 8 complete groups passed and 5 contain all 1,262 recorded differences.</text>',
        '<rect x="44" y="1563" width="1352" height="292" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1601" class="heading">3. Is any replacement faster?</text>',
        '<text x="66" y="1632" class="body">NOT MEASURED. No replacement has passed every original Python compatibility check.</text>',
        '<text x="66" y="1661" class="body">There is no speed or memory comparison, confidence interval, performance ranking, or winner.</text>',
        '<text x="66" y="1690" class="body">The expanded 4,194,304-case final comparison is not generated and has not been opened.</text>',
        '<text x="66" y="1719" class="body">Evidence: 141 verified historical files + the real 13-worker Zig archive and distinct receipt = 143 files.</text>',
        '<text x="66" y="1748" class="body">All 148 authenticated references retain both different Zig failures and every earlier candidate loss.</text>',
        '<text x="66" y="1777" class="body">Zig receipt PASS means the 2,172-difference FAIL was durably preserved, not that Zig passed.</text>',
        '<text x="66" y="1806" class="body">Both original Zig native inodes were restored before the result was published.</text>',
        f'<text x="47" y="1884" class="foot">Inputs SHA-256: {xml(inputs_sha)}</text>',
        f'<text x="47" y="1906" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="47" y="1928" class="foot">Actual complete Zig failure archive: {xml(ACTUAL_ARCHIVE[1])}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(source_sha: str, archive_sha: str,
          receipt_sha: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked_digest(source_sha, "exact V27 renderer source")
    source_raw, _source_owner = read_owner(SELF, source_sha)
    previous, old_summary, old_inputs, references = authenticate_v26()
    proof, additions = authenticate_actual_campaign(archive_sha, receipt_sha, references)
    need(len(references) == 146 and len(additions) == 2
         and not (set(references) & set(additions)),
         "derive exact V27 history only from independently distinct genuine owners")
    all_references = dict(references)
    all_references.update(additions)
    owner_count = old_summary["repository_evidence_owner_count"] + len(additions)
    need(owner_count == 143 and len(all_references) == 148,
         "independently derive actual evidence totals 141+2 and 146+2")
    old_snapshot = old_summary["snapshot"]
    previous.validate_snapshot(old_snapshot)
    snapshot = copy.deepcopy(old_snapshot)
    snapshot.update({
        "preserved_v26_repository_evidence_owner_count":
            old_summary["repository_evidence_owner_count"],
        "preserved_v26_digest_addressed_history_path_count": len(references),
        "new_zig_original_campaign_repository_evidence_owner_count": len(additions),
        "all_actual_candidate_and_native_evidence_owner_count": owner_count,
        "all_digest_addressed_history_path_count": len(all_references),
        "zig_v2_original_campaign": copy.deepcopy(proof),
        "zig_v2_original_campaign_status": "FAIL",
        "zig_v2_original_campaign_failure_class": "SEMANTIC MISMATCH",
        "zig_v2_original_campaign_actual_candidate_workers": 13,
        "zig_v2_original_campaign_completed_suite_count": 13,
        "zig_v2_original_campaign_case_execution_denominator": 31237,
        "zig_v2_original_campaign_semantic_mismatch_count": 2172,
        "zig_v2_original_campaign_verified_passing_case_count": 2847,
        "zig_v2_original_campaign_infrastructure_failure_count": 0,
        "zig_v2_original_campaign_original_targets_restored": True,
        "zig_scanner_repaired_matching_status": "FAIL: 2,172 SEMANTIC MISMATCHES",
        "zig_scanner_repaired_candidate_worker_count": 13,
        "zig_scanner_repaired_candidate_qualified": False,
    })
    validate_snapshot(snapshot)
    previous_pins = {
        key: pin(path, fingerprint, size)
        for key, (path, fingerprint, size) in sorted(V26.items())
    }
    campaign_pins = {
        key: pin(path, fingerprint, size)
        for key, (path, fingerprint, size) in sorted(CAMPAIGN.items())
    }
    manifest = {
        "schema": SCHEMA + "-inputs", "version": 27, "python": "3.14.6",
        "renderer": pin(SELF, source_sha, len(source_raw)),
        "previous_overview": previous_pins,
        "original_correctness_manifest":
            copy.deepcopy(old_inputs["original_correctness_manifest"]),
        "original_source_freeze": copy.deepcopy(old_inputs["original_source_freeze"]),
        "current_complete_c_campaign":
            copy.deepcopy(snapshot["c_v10_repaired_original_campaign"]),
        "current_repaired_zig_source_build":
            copy.deepcopy(snapshot["zig_v11_scanner_repaired_source_build"]),
        "current_repaired_rust_source_build":
            copy.deepcopy(snapshot["rust_v11_dual_overlay_repaired_source_build"]),
        "historical_zig_preflight_failure":
            copy.deepcopy(snapshot["zig_original_campaign_preflight_failure"]),
        "actual_zig_original_campaign_source_freeze": campaign_pins,
        "actual_zig_complete_original_campaign": copy.deepcopy(proof),
        "full_case_denominator": 31237,
        "suite_count": 13, "private_waiver_count": 13,
        "candidate_families": copy.deepcopy(old_inputs["candidate_families"]),
        "candidate_qualified_count": 0,
        "preserved_v26_repository_evidence_owner_count":
            old_summary["repository_evidence_owner_count"],
        "preserved_v26_digest_addressed_history_path_count": len(references),
        "new_zig_original_campaign_repository_evidence_owner_count": len(additions),
        "repository_evidence_owner_count": owner_count,
        "all_digest_addressed_history_path_count": len(all_references),
        "actual_zig_candidate_workers": 13,
        "actual_zig_completed_suite_count": 13,
        "actual_zig_semantic_mismatch_count": 2172,
        "actual_zig_verified_passing_case_count": 2847,
        "actual_zig_infrastructure_failure_count": 0,
        "zig_matching_test_status": "FAIL: 2,172 SEMANTIC MISMATCHES",
        "uncompressed_zig_archive_opened_by_graph": False,
        "uncompressed_zig_archive_bytes_read_by_graph": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }
    manifest_raw = canonical(manifest)
    manifest_sha = digest(manifest_raw)
    picture = make_svg(snapshot, source_sha, manifest_sha)
    families = copy.deepcopy(old_summary["families"])
    zig_count = 0
    for family in families:
        if family.get("family") == "zig":
            zig_count += 1
            family["current_scanner_repaired_matching_test_status"] = (
                "FAIL: 2,172 SEMANTIC MISMATCHES")
            family["current_scanner_repaired_candidate_worker_count"] = 13
            family["current_original_campaign_v2"] = copy.deepcopy(proof)
            family["current_original_campaign_matching_test_status"] = (
                "FAIL: 2,172 SEMANTIC MISMATCHES")
            family["current_original_campaign_matching_case_count"] = 31237
            family["current_original_campaign_candidate_worker_count"] = 13
            family["current_original_campaign_semantic_mismatch_count"] = 2172
            family["current_original_campaign_verified_passing_case_count"] = 2847
            family["current_original_campaign_infrastructure_failure_count"] = 0
            family["current_original_campaign_original_targets_unchanged"] = True
            family["qualified"] = False
    need(zig_count == 1,
         "retain exactly one independent from-scratch Zig matching engine family")
    summary = {
        "schema": SCHEMA + "-summary", "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_sha, len(source_raw)),
        "inputs": pin(OUTPUT + ".inputs.json", manifest_sha, len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(picture), len(picture)),
        "previous_overview": previous_pins,
        "actual_zig_original_campaign_source_freeze": campaign_pins,
        "snapshot": snapshot, "families": families,
        "full_case_denominator": 31237,
        "suite_count": 13, "private_waiver_count": 13,
        "preserved_v26_repository_evidence_owner_count":
            old_summary["repository_evidence_owner_count"],
        "preserved_v26_authenticated_reference_path_count": len(references),
        "new_zig_original_campaign_repository_evidence_owner_count": len(additions),
        "repository_evidence_owner_count": owner_count,
        "authenticated_digest_addressed_history_paths": len(all_references),
        "qualified_candidate_count": 0,
        "historical_zig_preflight_failure":
            copy.deepcopy(snapshot["zig_original_campaign_preflight_failure"]),
        "actual_zig_original_campaign": copy.deepcopy(proof),
        "zig_original_campaign_status": "FAIL",
        "zig_original_campaign_failure_class": "SEMANTIC MISMATCH",
        "zig_original_campaign_candidate_worker_count": 13,
        "zig_original_campaign_completed_suite_count": 13,
        "zig_original_campaign_case_execution_denominator": 31237,
        "zig_original_campaign_semantic_mismatch_count": 2172,
        "zig_original_campaign_verified_passing_case_count": 2847,
        "zig_original_campaign_infrastructure_failure_count": 0,
        "zig_original_campaign_original_targets_restored": True,
        "zig_original_campaign_receipt_status": "PASS",
        "zig_original_campaign_receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "zig_individual_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "uncompressed_zig_archive_opened_by_graph": False,
        "uncompressed_zig_archive_bytes_read_by_graph": 0,
        "c_repaired_build_status": "PASS",
        "c_repaired_matching_test_status": "FAIL: 1,262 SEMANTIC MISMATCHES",
        "c_repaired_observed_matching_case_count": 31237,
        "c_repaired_verified_passing_case_count": 7325,
        "c_repaired_semantic_mismatch_count": 1262,
        "c_repaired_infrastructure_failure_count": 0,
        "c_repaired_completed_suite_count": 13,
        "c_repaired_candidate_worker_count": 13,
        "c_repaired_fully_passing_suite_count": 8,
        "c_repaired_original_campaign_status": "FAIL",
        "c_repaired_native_promoted": False,
        "original_canonical_native_restored": True,
        "zig_scanner_repaired_build_status": "PASS",
        "zig_scanner_repaired_build_process_count": 26,
        "zig_scanner_repaired_source_apply_count": 2,
        "zig_scanner_repaired_reproducibility": "PASS",
        "zig_scanner_repaired_matching_test_status":
            "FAIL: 2,172 SEMANTIC MISMATCHES",
        "zig_scanner_repaired_candidate_worker_count": 13,
        "zig_scanner_repaired_candidate_qualified": False,
        "zig_historical_semantic_mismatch_count": 1764,
        "rust_dual_overlay_repaired_build_status": "PASS",
        "rust_dual_overlay_repaired_build_process_count": 28,
        "rust_dual_overlay_repaired_bridge_source_apply_count": 2,
        "rust_dual_overlay_repaired_public_source_apply_count": 2,
        "rust_dual_overlay_repaired_reproducibility": "PASS",
        "rust_dual_overlay_repaired_matching_test_status": "NOT MEASURED",
        "rust_dual_overlay_repaired_candidate_worker_count": 0,
        "rust_dual_overlay_repaired_candidate_qualified": False,
        "rust_historical_semantic_mismatch_count": 2042,
        "rust_historical_verified_passing_case_count": 7461,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    return snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", picture),
    )


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def block(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GraphError("V27 source-only effect blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, block)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)), (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir", "makedirs",
                  "unlink", "remove", "rename", "replace", "system", "fork",
                  "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text",
                    "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object,
                 _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_proof() -> dict:
    archive = {
        "path": ACTUAL_ARCHIVE[0], "sha256": ACTUAL_ARCHIVE[1],
        "bytes": ACTUAL_ARCHIVE[2], "device": ACTUAL_ARCHIVE[3],
        "inode": ACTUAL_ARCHIVE[4], "mode": "0600", "nlink": 1, "uid": 1000,
    }
    receipt = {
        "path": ACTUAL_RECEIPT[0], "sha256": ACTUAL_RECEIPT[1],
        "bytes": ACTUAL_RECEIPT[2], "device": ACTUAL_RECEIPT[3],
        "inode": ACTUAL_RECEIPT[4], "mode": "0600", "nlink": 1, "uid": 1000,
    }
    report = {
        "status": "PASS", "candidate_status": "FAIL",
        "actual_candidate_workers": 13,
        "semantic_mismatch_count": 2172,
        "verified_passing_case_count": 2847,
        "infrastructure_failure_count": 0,
    }
    return {
        "schema": SCHEMA + "-authenticated-complete-zig-matching-failure",
        "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "family": "zig", "label": LABEL,
        "archive": archive, "receipt": receipt, "publication_receipt": report,
        "suite_count": 13, "completed_suite_count": 13,
        "case_execution_denominator": 31237, "private_waiver_count": 13,
        "actual_candidate_workers": 13,
        "semantic_mismatch_count": 2172,
        "verified_passing_case_count": 2847,
        "infrastructure_failure_count": 0,
        "all_original_suite_streams_retained": True,
        "individual_zig_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "uncompressed_archive_sha256": EXPANDED_SHA256,
        "uncompressed_archive_bytes": EXPANDED_BYTES,
        "uncompressed_archive_opened_by_graph": False,
        "uncompressed_archive_bytes_read_by_graph": 0,
        "original_native_restored": True,
        "original_native_targets_inspected_by_graph": False,
        "restored_original_targets": {},
        "restoration_order": ["bridge", "engine"],
        "restoration_verified_before_publication": True,
        "group_atomic": False, "candidate_qualified": False,
        "new_repository_evidence_owner_count": 2,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def synthetic_snapshot() -> dict:
    rows = [{
        "suite": name, "display_name": display,
        "status": "PASS" if losses == 0 else "FAIL",
        "case_execution_denominator": count, "mismatch_count": losses,
        "actual_worker_started": True,
        "all_original_records_and_mismatches_preserved": True,
    } for name, count, losses, display in SUITES]
    c = {
        "status": "FAIL", "actual_candidate_workers": 13,
        "completed_suite_count": 13, "fully_passing_suite_count": 8,
        "observed_matching_case_count": 31237,
        "verified_passing_case_count": 7325,
        "semantic_mismatch_count": 1262,
        "infrastructure_failure_count": 0,
        "all_original_suite_evidence_preserved": True,
        "original_canonical_native_restored": True,
        "qualified": False, "suite_results": rows,
    }
    preflight = {
        "status": "FAIL",
        "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "actual_candidate_workers": 0,
        "actual_matching_case_execution_count": 0,
        "candidate_correctness": "NOT MEASURED",
    }
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "suite_ids": [name for name, _count, _loss, _display in SUITES],
        "baseline_passed": 31237, "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v26_repository_evidence_owner_count": 141,
        "preserved_v26_digest_addressed_history_path_count": 146,
        "new_zig_original_campaign_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 143,
        "all_digest_addressed_history_path_count": 148,
        "c_v10_repaired_original_campaign": c,
        "zig_original_campaign_preflight_failure": preflight,
        "zig_original_campaign_attempt_count": 1,
        "zig_original_campaign_controller_exit_status": 1,
        "zig_original_campaign_controller_process_id": "NOT RECORDED",
        "zig_original_campaign_actual_candidate_worker_count": 0,
        "zig_original_campaign_actual_matching_case_count": 0,
        "zig_v2_original_campaign": synthetic_proof(),
        "zig_v2_original_campaign_status": "FAIL",
        "zig_v2_original_campaign_failure_class": "SEMANTIC MISMATCH",
        "zig_v2_original_campaign_actual_candidate_workers": 13,
        "zig_v2_original_campaign_completed_suite_count": 13,
        "zig_v2_original_campaign_case_execution_denominator": 31237,
        "zig_v2_original_campaign_semantic_mismatch_count": 2172,
        "zig_v2_original_campaign_verified_passing_case_count": 2847,
        "zig_v2_original_campaign_infrastructure_failure_count": 0,
        "zig_v2_original_campaign_original_targets_restored": True,
        "zig_scanner_repaired_matching_status": "FAIL: 2,172 SEMANTIC MISMATCHES",
        "zig_scanner_repaired_candidate_worker_count": 13,
        "zig_scanner_repaired_candidate_qualified": False,
        "c_actual_semantic_mismatch_count": 2094,
        "c_verified_passing_case_executions": 7197,
        "rust_actual_semantic_mismatch_count": 2042,
        "rust_verified_passing_case_executions": 7461,
        "zig_actual_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_executions": 3583,
        "cpp_full_original_campaign": {"semantic_mismatch_count": 2308},
        "go_v2_full_original_campaign": {"semantic_mismatch_count": 4518},
        "zig_scanner_repaired_build_status": "PASS",
        "zig_scanner_repaired_build_process_count": 26,
        "zig_scanner_repaired_source_apply_count": 2,
        "zig_scanner_repaired_reproducibility": "PASS",
        "rust_dual_overlay_repaired_build_status": "PASS",
        "rust_dual_overlay_repaired_build_process_count": 28,
        "rust_dual_overlay_repaired_bridge_source_apply_count": 2,
        "rust_dual_overlay_repaired_public_source_apply_count": 2,
        "rust_dual_overlay_repaired_reproducibility": "PASS",
        "rust_dual_overlay_repaired_matching_status": "NOT MEASURED",
        "rust_dual_overlay_repaired_candidate_worker_count": 0,
        "rust_dual_overlay_repaired_candidate_qualified": False,
        "repaired_c_semantic_mismatch_count": 1262,
        "repaired_c_verified_passing_case_count": 7325,
        "repaired_c_actual_candidate_worker_count": 13,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def self_test() -> dict:
    runtime()
    with SourceOnlyWall() as wall:
        base = synthetic_snapshot()
        validate_snapshot(base)
        rejected = 0

        def reject(value: dict) -> None:
            nonlocal rejected
            try:
                validate_snapshot(value)
            except (GraphError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise GraphError("accepting altered V27 history or matching results is forbidden")

        changes = {
            "full_case_denominator": 31236, "suite_count": 12,
            "baseline_passed": 31236, "frozen_independent_engine_family_count": 5,
            "qualified_candidate_count": 1,
            "preserved_v26_repository_evidence_owner_count": 140,
            "preserved_v26_digest_addressed_history_path_count": 145,
            "new_zig_original_campaign_repository_evidence_owner_count": 1,
            "all_actual_candidate_and_native_evidence_owner_count": 142,
            "all_digest_addressed_history_path_count": 147,
            "zig_original_campaign_attempt_count": 0,
            "zig_original_campaign_controller_exit_status": 0,
            "zig_original_campaign_controller_process_id": 12345,
            "zig_original_campaign_actual_candidate_worker_count": 13,
            "zig_original_campaign_actual_matching_case_count": 31237,
            "zig_v2_original_campaign_status": "PASS",
            "zig_v2_original_campaign_failure_class": "PASS",
            "zig_v2_original_campaign_actual_candidate_workers": 0,
            "zig_v2_original_campaign_completed_suite_count": 12,
            "zig_v2_original_campaign_case_execution_denominator": 31236,
            "zig_v2_original_campaign_semantic_mismatch_count": 0,
            "zig_v2_original_campaign_verified_passing_case_count": 31237,
            "zig_v2_original_campaign_infrastructure_failure_count": 1,
            "zig_v2_original_campaign_original_targets_restored": False,
            "zig_scanner_repaired_matching_status": "PASS",
            "zig_scanner_repaired_candidate_worker_count": 0,
            "zig_scanner_repaired_candidate_qualified": True,
            "c_actual_semantic_mismatch_count": 0,
            "c_verified_passing_case_executions": 31237,
            "rust_actual_semantic_mismatch_count": 0,
            "rust_verified_passing_case_executions": 31237,
            "zig_actual_semantic_mismatch_count": 0,
            "zig_verified_passing_case_executions": 31237,
            "zig_scanner_repaired_build_status": "FAIL",
            "zig_scanner_repaired_build_process_count": 25,
            "zig_scanner_repaired_source_apply_count": 1,
            "zig_scanner_repaired_reproducibility": "FAIL",
            "rust_dual_overlay_repaired_build_status": "FAIL",
            "rust_dual_overlay_repaired_build_process_count": 27,
            "rust_dual_overlay_repaired_bridge_source_apply_count": 1,
            "rust_dual_overlay_repaired_public_source_apply_count": 1,
            "rust_dual_overlay_repaired_reproducibility": "FAIL",
            "rust_dual_overlay_repaired_matching_status": "PASS",
            "rust_dual_overlay_repaired_candidate_worker_count": 1,
            "rust_dual_overlay_repaired_candidate_qualified": True,
            "repaired_c_semantic_mismatch_count": 0,
            "repaired_c_verified_passing_case_count": 31237,
            "repaired_c_actual_candidate_worker_count": 12,
            "performance": "1.5x faster", "memory": "0 bytes",
            "confidence_intervals": "95%",
            "hidden_cases_read": 1, "performance_files_read": 1,
            "clock_samples": 1, "timing_trials_run": 1,
            "final_comparison_planned_case_count": 4194303,
            "final_comparison_cases_generated": True,
            "final_holdout_opened": True, "winner_selected": True,
        }
        for key, value in changes.items():
            altered = copy.deepcopy(base)
            altered[key] = value
            reject(altered)
        proof_changes = {
            "schema": "forged", "status": "PASS",
            "failure_class": "PASS", "publication_status": "FAIL",
            "publication_pass_means": "CANDIDATE PASS",
            "family": "rust", "label": "forged",
            "suite_count": 12, "completed_suite_count": 12,
            "case_execution_denominator": 31236, "private_waiver_count": 12,
            "actual_candidate_workers": 0,
            "semantic_mismatch_count": 0,
            "verified_passing_case_count": 31237,
            "infrastructure_failure_count": 1,
            "all_original_suite_streams_retained": False,
            "individual_zig_suite_mismatches": "invented",
            "uncompressed_archive_sha256": "0" * 64,
            "uncompressed_archive_bytes": EXPANDED_BYTES - 1,
            "uncompressed_archive_opened_by_graph": True,
            "uncompressed_archive_bytes_read_by_graph": EXPANDED_BYTES,
            "original_native_restored": False,
            "original_native_targets_inspected_by_graph": True,
            "restoration_order": ["engine", "bridge"],
            "restoration_verified_before_publication": False,
            "group_atomic": True, "candidate_qualified": True,
            "new_repository_evidence_owner_count": 1,
            "performance": "1.5x faster", "memory": "0 bytes",
            "undefined_behavior": "PASS", "holdout": "OPENED",
            "winner_selected": True,
        }
        for key, value in proof_changes.items():
            altered = copy.deepcopy(base)
            altered["zig_v2_original_campaign"][key] = value
            reject(altered)
        for role, key, value in (
            ("archive", "sha256", "0" * 64),
            ("archive", "inode", ACTUAL_RECEIPT[4]),
            ("archive", "mode", "0644"),
            ("archive", "nlink", 2),
            ("receipt", "sha256", "0" * 64),
            ("receipt", "inode", ACTUAL_ARCHIVE[4]),
            ("receipt", "mode", "0644"),
            ("receipt", "nlink", 2),
        ):
            altered = copy.deepcopy(base)
            altered["zig_v2_original_campaign"][role][key] = value
            reject(altered)
        for index in range(len(SUITES)):
            altered = copy.deepcopy(base)
            altered["c_v10_repaired_original_campaign"]["suite_results"][index]["mismatch_count"] += 1
            reject(altered)
        for family in ("cpp_full_original_campaign", "go_v2_full_original_campaign"):
            altered = copy.deepcopy(base)
            altered[family]["semantic_mismatch_count"] = 0
            reject(altered)
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"2,172", b"1,262", b"2,847", b"31,237", b"143 / 148",
            b"13 actual workers", b"NOT COMPATIBLE", b"NOT MEASURED",
            b"SETUP STOPPED; 0 TESTS", b"2,042", b"1,764", b"2,308", b"4,518",
            b"not invented", b"not decompressed",
        ):
            need(phrase.lower() in picture.lower(),
                 "the accessible chart hides an actual mismatch or invents suite rows")
        effects = (
            lambda: builtins.open("forbidden-v27-owner"),
            lambda: io.open("forbidden-v27-owner"),
            lambda: os.open("forbidden-v27-owner", os.O_RDONLY),
            lambda: os.stat("forbidden-v27-native"),
            lambda: subprocess.run(("forbidden-v27-worker",)),
            lambda: importlib.import_module("candidates.zig_candidate"),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for effect in effects:
            try:
                effect()
            except GraphError:
                continue
            raise GraphError("a real V27 synthetic source-only effect was not blocked")
        need(wall.blocked == len(effects),
             "physically block files, candidates, processes, clocks and network")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 27, "status": "PASS", "synthetic_only": True,
            "accepted_control_count": 1,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "suite_count": 13, "full_case_denominator": 31237,
            "preserved_v26_evidence_owner_count": 141,
            "preserved_v26_authenticated_reference_count": 146,
            "new_actual_campaign_evidence_owner_count": 2,
            "repository_evidence_owner_count": 143,
            "authenticated_digest_addressed_history_paths": 148,
            "actual_zig_candidate_workers": 13,
            "actual_zig_completed_suite_count": 13,
            "actual_zig_semantic_mismatch_count": 2172,
            "actual_zig_verified_passing_case_count": 2847,
            "actual_zig_infrastructure_failure_count": 0,
            "historical_zig_preflight_candidate_workers": 0,
            "current_c_semantic_mismatch_count": 1262,
            "current_c_verified_passing_case_count": 7325,
            "historical_rust_semantic_mismatch_count": 2042,
            "historical_zig_semantic_mismatch_count": 1764,
            "individual_zig_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
            "uncompressed_zig_archive_opened": False,
            "uncompressed_zig_archive_bytes_read": 0,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_native_activations": 0,
            "canonical_target_reads": 0,
            "canonical_target_stats": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "workspace_mutations": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
            "synthetic_svg_sha256": digest(picture),
        }


def publish_output(path: str, raw: bytes) -> None:
    need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
         and type(raw) is bytes and 0 < len(raw) <= MAX_OWNER,
         "publish only one of the three exact bounded new V27 graph outputs")
    descriptor = os.open(
        str(ROOT / path),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
        0o600,
    )
    try:
        position = 0
        while position < len(raw):
            count = os.write(descriptor, raw[position:])
            need(type(count) is int and count > 0,
                 "reject an incomplete exclusively created V27 graph")
            position += count
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        need(stat.S_ISREG(owner.st_mode)
             and owner.st_size == len(raw) and owner.st_nlink == 1
             and stat.S_IMODE(owner.st_mode) == 0o600,
             "reject linked, truncated, or nonprivate V27 graph output")
    finally:
        os.close(descriptor)


def result(source_sha: str, archive_sha: str, receipt_sha: str,
           outputs: dict[str, bytes], *, written: bool, kind: str) -> dict:
    return {
        "schema": SCHEMA + kind, "version": 27, "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_zig_campaign_archive_sha256": archive_sha,
        "actual_zig_campaign_receipt_sha256": receipt_sha,
        "suite_count": 13, "full_case_denominator": 31237,
        "private_waiver_count": 13, "candidate_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v26_repository_evidence_owner_count": 141,
        "preserved_v26_authenticated_reference_count": 146,
        "new_actual_campaign_evidence_owner_count": 2,
        "repository_evidence_owner_count": 143,
        "authenticated_digest_addressed_history_paths": 148,
        "zig_matching_status": "FAIL",
        "zig_failure_class": "SEMANTIC MISMATCH",
        "actual_zig_candidate_workers": 13,
        "actual_zig_completed_suite_count": 13,
        "actual_zig_semantic_mismatch_count": 2172,
        "actual_zig_verified_passing_case_count": 2847,
        "actual_zig_infrastructure_failure_count": 0,
        "zig_original_native_targets_restored": True,
        "zig_receipt_status": "PASS",
        "zig_receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "historical_zig_preflight_failure_status": "FAIL",
        "historical_zig_preflight_candidate_workers": 0,
        "zig_individual_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "uncompressed_zig_archive_opened": False,
        "uncompressed_zig_archive_bytes_read": 0,
        "zig_repaired_build_process_count": 26,
        "historical_zig_semantic_mismatch_count": 1764,
        "rust_repaired_build_process_count": 28,
        "rust_repaired_matching_test_status": "NOT MEASURED",
        "historical_rust_semantic_mismatch_count": 2042,
        "current_c_candidate_worker_count": 13,
        "current_c_verified_passing_case_count": 7325,
        "current_c_semantic_mismatch_count": 1262,
        "current_c_infrastructure_failure_count": 0,
        "outputs_written": written,
        "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers": 0, "actual_source_builds": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--campaign-archive-sha256")
    parser.add_argument("--campaign-receipt-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        runtime()
        if options.self_test:
            need(all(getattr(options, field) is None for field in (
                "source_sha256", "campaign_archive_sha256",
                "campaign_receipt_sha256", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            )), "synthetic self-tests cannot authorize evidence, rendering, or matching")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source_sha = checked_digest(options.source_sha256, "V27 renderer source")
        archive_sha = checked_digest(options.campaign_archive_sha256,
                                     "actual 13-worker Zig failure archive")
        receipt_sha = checked_digest(options.campaign_receipt_sha256,
                                     "actual distinct Zig failure receipt")
        _snapshot, rows = build(source_sha, archive_sha, receipt_sha)
        outputs = dict(rows)
        if options.render:
            need(options.inputs_sha256 is None
                 and options.summary_sha256 is None
                 and options.svg_sha256 is None,
                 "once-only exclusive rendering rejects substituted output pins")
            for path, raw in rows:
                publish_output(path, raw)
            sys.stdout.buffer.write(canonical(result(
                source_sha, archive_sha, receipt_sha, outputs,
                written=True, kind="-published",
            )))
            return 0
        pinned = {
            OUTPUT + ".inputs.json": checked_digest(
                options.inputs_sha256, "published V27 graph inputs"),
            OUTPUT + ".json": checked_digest(
                options.summary_sha256, "published V27 graph summary"),
            OUTPUT + ".svg": checked_digest(
                options.svg_sha256, "published accessible V27 graph"),
        }
        for path, fingerprint in pinned.items():
            raw, _owner = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(raw == outputs[path],
                 "independently reproduce every exact published V27 graph owner")
        sys.stdout.buffer.write(canonical(result(
            source_sha, archive_sha, receipt_sha, outputs,
            written=False, kind="-read-only-frozen-context",
        )))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            KeyError, AttributeError, struct.error) as error:
        sys.stderr.write("current V27 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
