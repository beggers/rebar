#!/usr/bin/env python3
"""Show the actual corrected Rust result without inventing speed or tests."""

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
SELF = "tools/render_candidate_current_overview_v32.py"
OUTPUT = "docs/evidence/candidate-current-overview-v32"
SCHEMA = "rebar-candidate-current-overview-v32"
LIMIT = 8 * 1024 * 1024
V31 = {
    "source": (
        "tools/render_candidate_current_overview_v31.py",
        "daea5423d47bc84ec0ff503c14bae17ecdff392a60db14c5c66c575e978de588",
        75072,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v31.inputs.json",
        "25f1ef2cdf7f3443f5924b9c9814c4f0864148ebdf243c92a1df12d1c5754900",
        80376,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v31.json",
        "6d6f8fa23022b9198255cd0836961d4f78cd2d4c5d4041734a82a1d9f9d2ec90",
        314023,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v31.svg",
        "23f89b7983d5154d9275dcfa029bfe2a5599ad339c80675efb7c5eabda587d1a",
        12509,
    ),
}
CAMPAIGN_SOURCE = (
    "tools/run_owned_repaired_rust_original_campaign_v4.py",
    "7d63b397deddd5c23af075754fcb50f7b3bdfb44390269383aae7903d46b4dd0",
    176358,
)
CAMPAIGN_PROTOCOL = (
    "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V4.md",
    "5296b7ed7c3ba37ce4e299924e9e9edae849bebcd0e92e828977ae9ac6c9e26b",
    7725,
)
CAMPAIGN_CONTRACT = (
    "oracle/phase2/repaired-rust-original-campaign-v4.json",
    "26e86429e1e437fc791401197fb8c6dd9cf399bb025bd027af5f9c2554d6f60b",
    14361,
)
ARCHIVE = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures.json.gz",
    "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f",
    3663299,
    2064,
    524655,
)
RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json",
    "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3",
    4674,
    2064,
    524656,
)
BUILD_ARCHIVE = "840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d"
BUILD_RECEIPT = "1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f"
PUBLIC_DERIVED = "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
BRIDGE_DERIVED = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
RECOVERY_JOURNAL = "726e81e5d2ee255e1f46d3029290ae9486fbd23711c9a45a691d091d088f3278"
PLAIN_SHA = "a7b2dfbe5d1a8ddf8b1c3de48c24085d43260084c4a48e4a8394f1cc5b66600b"
PLAIN_BYTES = 5280314


class GraphError(Exception):
    """Reject an invented candidate result, evidence owner, or measurement."""


def need(condition: object, reason: str) -> None:
    if condition is not True:
        raise GraphError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only authentic bounded first-party bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V32 evidence") from error


def checked(value: object, label: str) -> str:
    need(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "pin the exact lowercase SHA-256 for " + label,
    )
    return value


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "require exact isolated stable CPython 3.14.6",
    )


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        result: dict[str, object] = {}
        for key, value in items:
            need(key not in result, "reject duplicate JSON keys in " + label)
            result[key] = value
        return result

    try:
        result = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("reject nonfinite JSON in " + label)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed JSON in " + label) from error
    need(type(result) is dict and canonical(result) == raw, "require canonical " + label)
    return result


def read_owner(
    path: str, fingerprint: str, size: int, *, private: bool = False,
    device: int | None = None, inode: int | None = None,
) -> tuple[bytes, dict]:
    need(
        type(path) is str and bool(path) and not path.startswith("/")
        and ".." not in Path(path).parts and "." not in Path(path).parts,
        "reject an absolute, escaped, or substituted first-party owner",
    )
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT, "bound exact owner " + path)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories: list[int] = []
    handle: int | None = None
    try:
        directories.append(os.open(str(ROOT), directory_flags))
        parts = Path(path).parts
        for part in parts[:-1]:
            directories.append(os.open(part, directory_flags, dir_fd=directories[-1]))
        handle = os.open(parts[-1], file_flags, dir_fd=directories[-1])
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid() and before.st_nlink == 1
            and before.st_size == size
            and (not private or stat.S_IMODE(before.st_mode) == 0o600)
            and (device is None or before.st_dev == device)
            and (inode is None or before.st_ino == inode),
            "reject a foreign, linked, unprivate, or replaced owner " + path,
        )
        remaining = size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            need(bool(piece), "reject incomplete actual owner " + path)
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(handle, 1) == b"", "reject trailing bytes in " + path)
        raw = b"".join(pieces)
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_size, after.st_nlink)
            and digest(raw) == fingerprint,
            "reject an exact owner modified during independent authentication " + path,
        )
        return raw, {
            "path": path, "sha256": fingerprint, "bytes": size,
            "device": after.st_dev, "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "uid": after.st_uid, "nlink": after.st_nlink,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for descriptor in reversed(directories):
            os.close(descriptor)


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT, "bound an actual graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def load_v31() -> types.ModuleType:
    raw, _ = read_owner(*V31["source"])
    previous = types.ModuleType("_rebar_exact_v31_for_corrected_rust_matching_v32")
    previous.__file__ = str(ROOT / V31["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    need(
        previous.SCHEMA == "rebar-candidate-current-overview-v31"
        and previous.SELF == V31["source"][0],
        "load only the independently pinned actual V31 graph renderer",
    )
    return previous


def authenticate_v31() -> tuple[dict, dict, dict[str, str]]:
    old = load_v31()
    previous, _, refs = old.authenticate_v30()
    build_proof, added = old.authenticate_rust_v12(
        old.RUST_ARCHIVE[1], old.RUST_RECEIPT[1], refs,
    )
    need(
        len(refs) == 154 and len(added) == 2
        and not (set(refs) & set(added)),
        "independently reconstruct exact V31 actual build evidence",
    )
    refs = {**refs, **added}
    need(len(refs) == 156, "retain all genuine 156 V31 history references")
    inputs_raw, _ = read_owner(*V31["inputs"], private=True)
    summary_raw, _ = read_owner(*V31["summary"], private=True)
    svg_raw, _ = read_owner(*V31["svg"], private=True)
    inputs = document(inputs_raw, "actual published V31 inputs")
    summary = document(summary_raw, "actual published V31 summary")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "preserve the full actual V31 snapshot")
    old.validate(snapshot)
    need(
        summary.get("schema") == old.SCHEMA + "-summary"
        and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count") == 151
        and summary.get("authenticated_digest_addressed_history_paths") == 156
        and summary.get("suite_count") == 13
        and summary.get("full_case_denominator") == 31237
        and summary.get("private_waiver_count") == 13
        and summary.get("qualified_candidate_count") == 0
        and summary.get("actual_rust_v12_corrected_source_build") == build_proof
        and summary.get("rust_original_campaign_status") == "FAIL"
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087
        and summary.get("rust_original_campaign_verified_passing_case_count") == 7438
        and summary.get("c_original_campaign_status") == "FAIL"
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_status") == "FAIL"
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
        and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
        and inputs.get("repository_evidence_owner_count") == 151
        and inputs.get("all_digest_addressed_history_path_count") == 156
        and svg_raw == old.make_svg(snapshot, V31["source"][1], V31["inputs"][1]),
        "reproduce all four genuine V31 owners and every existing actual matching result",
    )
    return summary, inputs, refs


def authenticate_rust_v4(
    archive_pin: str, receipt_pin: str, previous: dict, refs: dict[str, str],
) -> tuple[dict, dict[str, str]]:
    need(
        checked(archive_pin, "actual complete Rust V4 matching failure") == ARCHIVE[1]
        and checked(receipt_pin, "actual Rust V4 durable failure receipt") == RECEIPT[1],
        "caller-pin both actual complete Rust matching evidence owners",
    )
    compressed, archive = read_owner(
        ARCHIVE[0], ARCHIVE[1], ARCHIVE[2], private=True,
        device=ARCHIVE[3], inode=ARCHIVE[4],
    )
    receipt_raw, receipt_owner = read_owner(
        RECEIPT[0], RECEIPT[1], RECEIPT[2], private=True,
        device=RECEIPT[3], inode=RECEIPT[4],
    )
    need(
        (archive["device"], archive["inode"])
        != (receipt_owner["device"], receipt_owner["inode"])
        and archive["path"] not in refs
        and receipt_owner["path"] not in refs
        and compressed[:3] == b"\x1f\x8b\x08"
        and struct.unpack("<I", compressed[4:8])[0] == 0
        and struct.unpack("<I", compressed[-4:])[0] == PLAIN_BYTES,
        "authenticate the complete compressed actual matching failure without inflation",
    )
    receipt = document(receipt_raw, "genuine Rust V4 durable matching-failure receipt")
    published = receipt.get("archive")
    need(
        type(published) is dict
        and receipt.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_qualified") is False
        and receipt.get("family") == "rust"
        and receipt.get("label") == "phase2-v12-rust-flag-original-p0"
        and published.get("path") == str(ROOT / ARCHIVE[0])
        and published.get("relative") == ARCHIVE[0].rsplit("/", 1)[-1]
        and published.get("sha256") == archive["sha256"]
        and published.get("size_bytes") == archive["bytes"]
        and published.get("device") == archive["device"]
        and published.get("inode") == archive["inode"]
        and published.get("mode") == 0o600
        and published.get("exclusive_creation") is True
        and published.get("file_fsync_completed") is True
        and published.get("directory_fsync_completed") is True
        and published.get("same_inode_readback_verified") is True
        and published.get("streaming_readback_verified") is True
        and type(published.get("write_calls")) is int
        and published["write_calls"] > 0,
        "a durable receipt PASS proves publication only; the Rust candidate really FAILED",
    )
    need(
        receipt.get("campaign_source_sha256") == CAMPAIGN_SOURCE[1]
        and receipt.get("campaign_protocol_sha256") == CAMPAIGN_PROTOCOL[1]
        and receipt.get("campaign_contract_sha256") == CAMPAIGN_CONTRACT[1]
        and receipt.get("actual_v12_build_archive_sha256") == BUILD_ARCHIVE
        and receipt.get("actual_v12_build_receipt_sha256") == BUILD_RECEIPT
        and receipt.get("corrected_public_adapter_sha256") == PUBLIC_DERIVED
        and receipt.get("corrected_bridge_source_sha256") == BRIDGE_DERIVED
        and receipt.get("suite_count") == 13
        and receipt.get("completed_suite_count") == 13
        and receipt.get("case_execution_denominator") == 31237
        and receipt.get("named_private_waiver_count") == 13
        and receipt.get("actual_candidate_workers") == 13
        and receipt.get("semantic_mismatch_count") == 1036
        and receipt.get("verified_passing_case_count") == 8965
        and receipt.get("infrastructure_failure_count") == 0
        and receipt.get("historical_evidence_owner_count_before_publication") == 151
        and receipt.get("historical_authenticated_reference_count_before_publication") == 156
        and receipt.get("new_repository_evidence_owner_count") == 2
        and receipt.get("resulting_repository_evidence_owner_count") == 153
        and receipt.get("resulting_authenticated_reference_count") == 158,
        "require all 13 actually completed corrected Rust workers and exact observed results",
    )
    need(
        receipt.get("uncompressed_sha256") == PLAIN_SHA
        and receipt.get("uncompressed_bytes") == PLAIN_BYTES
        and type(receipt.get("uncompressed_chunk_count")) is int
        and receipt["uncompressed_chunk_count"] > 0
        and receipt.get("recovery_journal_sha256") == RECOVERY_JOURNAL
        and receipt.get("restoration_verified_before_publication") is True
        and receipt.get("all_four_original_targets_restored") is True
        and receipt.get("v2_unsafe_activation_invoked") is False
        and receipt.get("v2_unsafe_controller_invoked") is False
        and receipt.get("v7_zig_only_activation_invoked") is False
        and receipt.get("v9_c_only_runner_invoked") is False
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "require complete journal-backed restoration; never inflate matching or open holdout",
    )
    _, campaign_source = read_owner(*CAMPAIGN_SOURCE)
    _, campaign_protocol = read_owner(*CAMPAIGN_PROTOCOL)
    contract_raw, campaign_contract = read_owner(*CAMPAIGN_CONTRACT)
    frozen = document(contract_raw, "exact frozen corrected Rust V4 original-campaign contract")
    oracle = frozen.get("original_oracle")
    build = frozen.get("actual_corrected_v12_build")
    accounting = frozen.get("current_historical_accounting")
    restoration = frozen.get("four_original_target_owners")
    need(
        frozen.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v4-recoverable-source-freeze"
        and frozen.get("version") == 4
        and frozen.get("family") == "rust"
        and frozen.get("campaign_label") == receipt["label"]
        and frozen.get("source")
        == {"path": CAMPAIGN_SOURCE[0], "sha256": CAMPAIGN_SOURCE[1]}
        and frozen.get("protocol")
        == {"path": CAMPAIGN_PROTOCOL[0], "sha256": CAMPAIGN_PROTOCOL[1]}
        and type(oracle) is dict
        and oracle.get("suite_count") == 13
        and oracle.get("case_execution_denominator") == 31237
        and oracle.get("named_private_waiver_count") == 13
        and len(oracle.get("source_ordered_suites", [])) == 13
        and oracle.get("reference_worker_started") is False
        and oracle.get("candidate_wrapper_allowed") is False
        and oracle.get("cross_family_matching_allowed") is False
        and oracle.get("external_regex_dependency_allowed") is False
        and oracle.get("stdlib_re_fallback_allowed") is False,
        "bind the corrected candidate to the entire unchanged original P0 oracle",
    )
    need(
        type(build) is dict and build.get("build_status") == "PASS"
        and build.get("build_version") == 12
        and build.get("build_label") == receipt["label"]
        and build.get("compiler_process_count") == 28
        and build.get("phase_count") == 2
        and build.get("corrected_public_overlay_apply_count") == 2
        and build.get("bridge_overlay_apply_count") == 2
        and build.get("owners", {}).get("archive", {}).get("sha256") == BUILD_ARCHIVE
        and build.get("owners", {}).get("receipt", {}).get("sha256") == BUILD_RECEIPT
        and build.get("corrected_public_adapter", {}).get("sha256") == PUBLIC_DERIVED
        and build.get("corrected_bridge_source", {}).get("sha256") == BRIDGE_DERIVED
        and type(accounting) is dict
        and accounting.get("actual_evidence_owner_count_before_new_campaign") == 151
        and accounting.get("actual_authenticated_reference_count_before_new_campaign") == 156,
        "bind matching to the genuine corrected V12 source build rather than a historical engine",
    )
    previous_build = previous.get("actual_rust_v12_corrected_source_build")
    need(
        type(previous_build) is dict
        and previous_build.get("archive", {}).get("sha256") == BUILD_ARCHIVE
        and previous_build.get("receipt", {}).get("sha256") == BUILD_RECEIPT
        and previous_build.get("corrected_public_adapter_sha256") == PUBLIC_DERIVED
        and previous_build.get("corrected_bridge_source_sha256") == BRIDGE_DERIVED
        and previous_build.get("native_roles", {}).get("engine", {}).get("sha256")
        == receipt.get("native_engine_sha256")
        and previous_build.get("native_roles", {}).get("bridge", {}).get("sha256")
        == receipt.get("native_bridge_sha256"),
        "reject substituted V11 build evidence or a different actually tested Rust native role",
    )
    restored = receipt.get("restored_original_targets")
    need(
        type(restoration) is list and len(restoration) == 4
        and type(restored) is dict
        and set(restored) == {"bridge_source", "adapter", "engine", "bridge"},
        "preserve exactly four genuine original canonical owner identities",
    )
    expected_restoration: dict[str, dict] = {}
    for item in restoration:
        need(type(item) is dict and type(item.get("role")) is str,
             "reject malformed frozen Rust restoration roles")
        role, original = item["role"], item.get("original")
        need(role in restored and type(original) is dict,
             "reject missing frozen original Rust restoration evidence")
        current = restored[role]
        need(
            type(current) is dict
            and current.get("relative") == original.get("relative")
            and current.get("path") == str(ROOT / original["relative"])
            and current.get("sha256") == original.get("sha256")
            and current.get("bytes") == original.get("bytes")
            and current.get("size_bytes") == original.get("bytes")
            and current.get("device") == original.get("device")
            and current.get("inode") == original.get("inode")
            and current.get("mode") == original.get("mode")
            and current.get("uid") == original.get("uid") == os.geteuid()
            and current.get("nlink") == original.get("nlink") == 1,
            "authenticate every receipt-recorded restored inode without reading canonical targets",
        )
        expected_restoration[role] = copy.deepcopy(current)
    added = {archive["path"]: archive["sha256"], receipt_owner["path"]: receipt_owner["sha256"]}
    need(len(added) == 2 and not (set(added) & set(refs)),
         "derive exactly two new actual Rust matching evidence owners")
    proof = {
        "schema": SCHEMA + "-authenticated-complete-rust-v4-matching-failure",
        "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "family": "rust", "label": receipt["label"],
        "source": campaign_source, "protocol": campaign_protocol,
        "contract": campaign_contract,
        "archive": archive, "receipt": receipt_owner,
        "publication_receipt": receipt,
        "suite_count": 13, "completed_suite_count": 13,
        "case_execution_denominator": 31237,
        "private_waiver_count": 13, "actual_candidate_workers": 13,
        "semantic_mismatch_count": 1036,
        "verified_passing_case_count": 8965,
        "infrastructure_failure_count": 0,
        "candidate_qualified": False,
        "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "historical_rust_semantic_mismatch_count": 1087,
        "historical_rust_verified_passing_case_count": 7438,
        "semantic_mismatch_reduction": 51,
        "additional_verified_passing_case_count": 1527,
        "actual_v12_build_archive_sha256": BUILD_ARCHIVE,
        "actual_v12_build_receipt_sha256": BUILD_RECEIPT,
        "corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "corrected_bridge_source_sha256": BRIDGE_DERIVED,
        "native_engine_sha256": receipt["native_engine_sha256"],
        "native_bridge_sha256": receipt["native_bridge_sha256"],
        "recovery_journal_sha256": RECOVERY_JOURNAL,
        "restored_original_targets": expected_restoration,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "original_canonical_targets_inspected_by_graph": False,
        "historical_evidence_owner_count_before_publication": 151,
        "historical_authenticated_reference_count_before_publication": 156,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": 153,
        "resulting_authenticated_reference_count": 158,
        "uncompressed_archive_sha256": PLAIN_SHA,
        "uncompressed_archive_bytes": PLAIN_BYTES,
        "uncompressed_archive_opened_by_graph": False,
        "uncompressed_archive_bytes_read_by_graph": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return proof, added


def validate(snapshot: object) -> None:
    need(
        type(snapshot) is dict
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("baseline_passed") == 31237
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("preserved_v31_repository_evidence_owner_count") == 151
        and snapshot.get("preserved_v31_digest_addressed_history_path_count") == 156
        and snapshot.get("new_rust_v4_original_campaign_repository_evidence_owner_count") == 2
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 153
        and snapshot.get("all_digest_addressed_history_path_count") == 158,
        "derive exactly 151 + 2 genuine evidence owners and 156 + 2 references",
    )
    previous = snapshot.get("rust_v3_original_campaign")
    need(
        type(previous) is dict and previous.get("status") == "FAIL"
        and previous.get("actual_candidate_workers") == 13
        and previous.get("completed_suite_count") == 13
        and previous.get("semantic_mismatch_count") == 1087
        and previous.get("verified_passing_case_count") == 7438
        and previous.get("infrastructure_failure_count") == 0
        and previous.get("candidate_qualified") is False,
        "preserve the genuine older Rust result as history, never as the new current result",
    )
    for name, mismatches, passes in (
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
    ):
        candidate = snapshot.get(name)
        need(
            type(candidate) is dict and candidate.get("status") == "FAIL"
            and candidate.get("actual_candidate_workers") == 13
            and candidate.get("completed_suite_count") == 13
            and candidate.get("semantic_mismatch_count") == mismatches
            and candidate.get("verified_passing_case_count") == passes
            and candidate.get("infrastructure_failure_count") == 0
            and candidate.get("candidate_qualified") is False,
            "retain every current actually completed non-Rust matching failure " + name,
        )
    old_c = snapshot.get("c_v10_repaired_original_campaign")
    need(
        type(old_c) is dict and old_c.get("status") == "FAIL"
        and old_c.get("semantic_mismatch_count") == 1262
        and old_c.get("verified_passing_case_count") == 7325
        and type(old_c.get("suite_results")) is list
        and len(old_c["suite_results"]) == 13,
        "do not invent individual new Rust groups from earlier C records",
    )
    actual = snapshot.get("rust_v4_original_campaign")
    need(
        type(actual) is dict
        and actual.get("schema") == SCHEMA + "-authenticated-complete-rust-v4-matching-failure"
        and actual.get("status") == "FAIL"
        and actual.get("failure_class") == "SEMANTIC MISMATCH"
        and actual.get("publication_status") == "PASS"
        and actual.get("publication_pass_means") == "DURABLE FAILURE PUBLICATION ONLY"
        and actual.get("family") == "rust"
        and actual.get("label") == "phase2-v12-rust-flag-original-p0"
        and actual.get("suite_count") == 13
        and actual.get("completed_suite_count") == 13
        and actual.get("case_execution_denominator") == 31237
        and actual.get("private_waiver_count") == 13
        and actual.get("actual_candidate_workers") == 13
        and actual.get("semantic_mismatch_count") == 1036
        and actual.get("verified_passing_case_count") == 8965
        and actual.get("infrastructure_failure_count") == 0
        and actual.get("candidate_qualified") is False
        and actual.get("individual_rust_suite_mismatches")
        == "NOT PRESENT IN DURABLE RECEIPT"
        and actual.get("historical_rust_semantic_mismatch_count") == 1087
        and actual.get("historical_rust_verified_passing_case_count") == 7438
        and actual.get("semantic_mismatch_reduction") == 51
        and actual.get("additional_verified_passing_case_count") == 1527,
        "report the real corrected Rust matching loss and exactly measured improvements",
    )
    archive, receipt = actual.get("archive"), actual.get("receipt")
    need(
        type(archive) is dict and archive.get("path") == ARCHIVE[0]
        and archive.get("sha256") == ARCHIVE[1]
        and archive.get("bytes") == ARCHIVE[2]
        and archive.get("device") == ARCHIVE[3]
        and archive.get("inode") == ARCHIVE[4]
        and archive.get("mode") == "0600" and archive.get("nlink") == 1
        and type(receipt) is dict and receipt.get("path") == RECEIPT[0]
        and receipt.get("sha256") == RECEIPT[1]
        and receipt.get("bytes") == RECEIPT[2]
        and receipt.get("device") == RECEIPT[3]
        and receipt.get("inode") == RECEIPT[4]
        and receipt.get("mode") == "0600" and receipt.get("nlink") == 1
        and (archive["device"], archive["inode"])
        != (receipt["device"], receipt["inode"]),
        "bind two genuinely distinct durable actual Rust failure evidence owners",
    )
    publication = actual.get("publication_receipt")
    need(
        type(publication) is dict
        and publication.get("status") == "PASS"
        and publication.get("publication_status") == "PASS"
        and publication.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and publication.get("candidate_status") == "FAIL"
        and publication.get("candidate_qualified") is False
        and publication.get("semantic_mismatch_count") == 1036
        and publication.get("verified_passing_case_count") == 8965,
        "never confuse durable failure publication PASS with a compatible replacement",
    )
    need(
        actual.get("actual_v12_build_archive_sha256") == BUILD_ARCHIVE
        and actual.get("actual_v12_build_receipt_sha256") == BUILD_RECEIPT
        and actual.get("corrected_public_adapter_sha256") == PUBLIC_DERIVED
        and actual.get("corrected_bridge_source_sha256") == BRIDGE_DERIVED
        and actual.get("recovery_journal_sha256") == RECOVERY_JOURNAL
        and type(actual.get("restored_original_targets")) is dict
        and set(actual["restored_original_targets"])
        == {"bridge_source", "adapter", "engine", "bridge"}
        and actual.get("all_four_original_targets_restored") is True
        and actual.get("restoration_verified_before_publication") is True
        and actual.get("original_canonical_targets_inspected_by_graph") is False
        and actual.get("historical_evidence_owner_count_before_publication") == 151
        and actual.get("historical_authenticated_reference_count_before_publication") == 156
        and actual.get("new_repository_evidence_owner_count") == 2
        and actual.get("resulting_repository_evidence_owner_count") == 153
        and actual.get("resulting_authenticated_reference_count") == 158,
        "verify the real corrected build, original recovery, and exact owner accounting",
    )
    need(
        actual.get("uncompressed_archive_sha256") == PLAIN_SHA
        and actual.get("uncompressed_archive_bytes") == PLAIN_BYTES
        and actual.get("uncompressed_archive_opened_by_graph") is False
        and actual.get("uncompressed_archive_bytes_read_by_graph") == 0
        and actual.get("benchmark_files_read") == 0
        and actual.get("hidden_cases_read") == 0
        and actual.get("clock_samples") == 0
        and actual.get("timing_trials_run") == 0
        and actual.get("performance") == "NOT MEASURED"
        and actual.get("memory") == "NOT MEASURED"
        and actual.get("holdout") == "NOT OPENED"
        and actual.get("winner_selected") is False,
        "reject matching-archive inflation, hidden cases, speed, timing, or a winner",
    )
    need(
        snapshot.get("rust_v4_original_campaign_status") == "FAIL"
        and snapshot.get("rust_v4_original_campaign_actual_candidate_workers") == 13
        and snapshot.get("rust_v4_original_campaign_semantic_mismatch_count") == 1036
        and snapshot.get("rust_v4_original_campaign_verified_passing_case_count") == 8965
        and snapshot.get("rust_v4_original_campaign_infrastructure_failure_count") == 0
        and snapshot.get("rust_v4_original_campaign_candidate_qualified") is False
        and snapshot.get("rust_v4_semantic_mismatch_reduction") == 51
        and snapshot.get("rust_v4_additional_verified_passing_cases") == 1527
        and snapshot.get("additional_signature_frozen_case_count") == 50
        and snapshot.get("additional_signature_reference_status") == "NOT RUN"
        and snapshot.get("additional_signature_reference_cases_executed") == 0
        and snapshot.get("zig_v2_source_freeze_status") == "SOURCE FROZEN"
        and snapshot.get("zig_v2_new_matching_test_status") == "NOT MEASURED"
        and snapshot.get("zig_v2_new_candidate_workers") == 0,
        "do not count planned signature references or frozen Zig source as real tests",
    )
    need(
        snapshot.get("performance") == "NOT MEASURED"
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
        "reject an invented benchmark, opened holdout, changed denominator, or winner",
    )


def xml(value: object) -> str:
    return (
        str(value).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
    )


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "actual V32 renderer")
    checked(inputs, "actual V32 graph inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1910" viewBox="0 0 1440 1910" role="img" aria-labelledby="v32-title v32-description">',
        '<title id="v32-title">Building a faster Python re: new Rust improves but is still not compatible</title>',
        '<desc id="v32-description">The corrected Rust replacement completed all 13 original matching test groups and recorded 1,036 differences and 8,965 verified passing checks. That is 51 fewer differences and 1,527 more verified passes than the previous fully tested Rust result of 1,087 differences and 7,438 passes. It is still not compatible. Current C and Zig have 1,230 and 2,172 differences. All 31,237 original Python reference checks pass. Exactly 153 evidence files and 158 references are authenticated. Fifty additional proposed signature checks have not been run; a new Zig source freeze has not been tested. Speed, memory, and confidence are not measured. The 4,194,304-case holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:27px;font-weight:760;fill:#16324f}.heading{font-size:20px;font-weight:740;fill:#16324f}.body{font-size:14px;fill:#42556c}.name{font-size:15px;font-weight:720;fill:#16324f}.pass{font-size:13px;font-weight:750;fill:#00794c}.fail{font-size:13px;font-weight:740;fill:#a15e00}.pending{font-size:13px;font-weight:740;fill:#53667b}.big{font-size:20px;font-weight:760;fill:#16324f}.small{font-size:12px;fill:#42556c}.foot{font-size:10px;fill:#53667b}</style>',
        '<rect width="1440" height="1910" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="54" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="46" y="81" class="body">New Rust: 1,036 differences, 51 fewer than before. Still not compatible. Speed is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0", "compatible replacements"),
        ("1,036", "new Rust differences"),
        ("51 fewer", "than previous Rust"),
        ("+1,527", "verified Rust passes"),
        ("1,230 / 2,172", "C / Zig differences"),
        ("153 / 158", "evidence / references"),
    )
    for index, (number, label) in enumerate(cards):
        x = 44 + 195 * index
        lines.extend((
            f'<rect x="{x}" y="98" width="184" height="82" rx="11" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 10}" y="132" class="big">{xml(number)}</text>',
            f'<text x="{x + 10}" y="158" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="197" width="1352" height="683" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="232" class="heading">1. Which versions actually match Python?</text>',
        '<text x="65" y="257" class="body">Matching results below come from completed original test runs; a published failure is not a passing candidate.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original Python reference checks pass.", "pass"),
        ("Rust — newly corrected and actually tested", "NOT COMPATIBLE", "13 workers; 1,036 differences; 8,965 verified passes; 0 worker failures.", "fail"),
        ("Rust — previous actually tested version", "NOT COMPATIBLE", "13 workers; 1,087 differences; 7,438 verified passes; kept as historical evidence.", "fail"),
        ("C — fully tested current version", "NOT COMPATIBLE", "13 workers; 1,230 differences; 7,325 verified passes.", "fail"),
        ("Zig — fully tested current version", "NOT COMPATIBLE", "13 workers; 2,172 differences; 2,847 verified passes.", "fail"),
        ("Rust — independently reproduced source build", "BUILD PASSED; MATCHING FAILED", "Two private source-build phases; 28 observed compiler and inspection processes.", "pending"),
        ("Additional Python signature checks", "REFERENCE NOT RUN", "50 frozen proposed checks; 0 reference executions; not added to the 31,237 denominator.", "pending"),
        ("Zig — next source version", "SOURCE FROZEN; NOT TESTED", "Source preparation does not create a build, candidate result, or matching worker.", "pending"),
        ("Speed, memory, and final comparison", "NOT MEASURED", "No compatible replacement, fair speed comparison, confidence interval, or winner.", "pending"),
        ("Final hidden holdout", "NOT OPENED", "All 4,194,304 planned final comparison cases remain ungenerated and sealed.", "pending"),
    )
    for index, (name, status, detail, kind) in enumerate(rows):
        y = 273 + index * 55
        lines.extend((
            f'<rect x="63" y="{y}" width="1314" height="49" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="79" y="{y + 19}" class="name">{xml(name)}</text>',
            f'<text x="1358" y="{y + 19}" class="{kind}" text-anchor="end">{xml(status)}</text>',
            f'<text x="80" y="{y + 38}" class="small">{xml(detail)}</text>',
        ))
    lines.append('<text x="65" y="852" class="body">The new Rust receipt contains complete totals, not individual new test-group results. Missing group rows are never invented.</text>')
    lines.extend((
        '<rect x="44" y="898" width="1352" height="410" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="934" class="heading">2. What did the previously recorded C test show?</text>',
        '<text x="65" y="958" class="body">These 13 recorded rows belong only to the historical C run with 1,262 differences.</text>',
        '<text x="80" y="982" class="small">HISTORICAL ORIGINAL PYTHON TEST GROUP</text>',
        '<text x="1040" y="982" class="small" text-anchor="end">CHECKS</text>',
        '<text x="1355" y="982" class="small" text-anchor="end">HISTORICAL C RESULT ONLY</text>',
    ))
    for index, row in enumerate(snapshot["c_v10_repaired_original_campaign"]["suite_results"]):
        need(type(row) is dict, "preserve each original historical C group")
        count, differences = row.get("case_execution_denominator"), row.get("mismatch_count")
        label = row.get("display_name", row.get("suite"))
        need(
            type(label) is str and bool(label)
            and type(count) is int and count >= 0
            and type(differences) is int and differences >= 0,
            "reject an invented historical original matching test group",
        )
        y = 990 + index * 22
        colour = "#f8fafd" if index % 2 == 0 else "#ffffff"
        result = "PASSED" if differences == 0 else f"{differences:,} DIFFERENCES"
        kind = "pass" if differences == 0 else "fail"
        lines.extend((
            f'<rect x="64" y="{y}" width="1312" height="21" rx="4" fill="{colour}"/>',
            f'<text x="80" y="{y + 15}" class="small">{xml(label)}</text>',
            f'<text x="1040" y="{y + 15}" class="small" text-anchor="end">{count:,}</text>',
            f'<text x="1355" y="{y + 15}" class="{kind}" text-anchor="end">{xml(result)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1325" width="1352" height="464" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1361" class="heading">3. Is the corrected Rust result a win?</text>',
    ))
    notes = (
        "No. Its real result is 1,036 differences, so it is not a compatible Python re replacement.",
        "The measured reduction is exactly 1,087 − 1,036 = 51 differences.",
        "Verified passing checks increase from 7,438 to 8,965: 1,527 actual additional passes.",
        "All 13 original matching workers completed; no infrastructure failure was recorded.",
        "Receipt PASS means the actual Rust FAIL was safely recorded; it never means matching passed.",
        "All four original Rust source and native file identities were restored before publication.",
        "151 previous evidence owners + one genuine Rust failure archive + one receipt = 153; 158 references.",
        "The matching-failure archives remain compressed; no original candidate target is inspected.",
        "The 50 additional signature checks are frozen only: their reference has NOT RUN.",
        "The next Zig source is frozen only: matching is NOT MEASURED.",
        "Speed, memory, confidence intervals, and undefined behavior remain NOT MEASURED.",
        "The 4,194,304-case final holdout is sealed; no replacement or winner is qualified.",
    )
    for index, note in enumerate(notes):
        lines.append(f'<text x="66" y="{1393 + index * 27}" class="body">{xml(note)}</text>')
    lines.extend((
        f'<text x="47" y="1810" class="foot">Inputs SHA-256: {xml(inputs)}</text>',
        f'<text x="47" y="1830" class="foot">Renderer SHA-256: {xml(source)}</text>',
        f'<text x="47" y="1850" class="foot">Actual Rust matching failure archive: {xml(ARCHIVE[1])}</text>',
        f'<text x="47" y="1870" class="foot">Actual distinct Rust failure publication receipt: {xml(RECEIPT[1])}</text>',
        f'<text x="47" y="1890" class="foot">Actual original-target recovery journal: {xml(RECOVERY_JOURNAL)}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(source_sha: str, archive_sha: str, receipt_sha: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_sha = checked(source_sha, "actual V32 graph renderer")
    own, _ = read_owner(SELF, source_sha, os.path.getsize(ROOT / SELF))
    previous, old_inputs, references = authenticate_v31()
    actual, added = authenticate_rust_v4(archive_sha, receipt_sha, previous, references)
    need(
        len(references) == 156 and len(added) == 2
        and not (set(references) & set(added)),
        "authenticate the corrected Rust failure only after reproducing all V31 history",
    )
    combined = {**references, **added}
    count = previous["repository_evidence_owner_count"] + len(added)
    need(count == 153 and len(combined) == 158, "derive actual 153 owners and 158 references")
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update({
        "preserved_v31_repository_evidence_owner_count": 151,
        "preserved_v31_digest_addressed_history_path_count": 156,
        "new_rust_v4_original_campaign_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": len(combined),
        "rust_v4_original_campaign": copy.deepcopy(actual),
        "rust_v4_original_campaign_status": "FAIL",
        "rust_v4_original_campaign_actual_candidate_workers": 13,
        "rust_v4_original_campaign_semantic_mismatch_count": 1036,
        "rust_v4_original_campaign_verified_passing_case_count": 8965,
        "rust_v4_original_campaign_infrastructure_failure_count": 0,
        "rust_v4_original_campaign_candidate_qualified": False,
        "rust_v4_semantic_mismatch_reduction": 51,
        "rust_v4_additional_verified_passing_cases": 1527,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "zig_v2_source_freeze_status": "SOURCE FROZEN",
        "zig_v2_new_matching_test_status": "NOT MEASURED",
        "zig_v2_new_candidate_workers": 0,
    })
    validate(snapshot)
    prior = {name: pin(*value) for name, value in V31.items()}
    manifest = copy.deepcopy(old_inputs)
    manifest.update({
        "schema": SCHEMA + "-inputs", "version": 32,
        "python": "3.14.6", "renderer": pin(SELF, source_sha, len(own)),
        "previous_overview": prior,
        "actual_complete_rust_v4_campaign": copy.deepcopy(actual),
        "current_complete_rust_campaign": copy.deepcopy(actual),
        "historical_complete_rust_v3_campaign":
            copy.deepcopy(snapshot["rust_v3_original_campaign"]),
        "current_complete_c_campaign": copy.deepcopy(snapshot["c_v4_original_campaign"]),
        "actual_complete_zig_campaign": copy.deepcopy(snapshot["zig_v2_original_campaign"]),
        "preserved_v31_repository_evidence_owner_count": 151,
        "preserved_v31_digest_addressed_history_path_count": 156,
        "new_rust_v4_original_campaign_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": len(combined),
        "candidate_qualified_count": 0,
        "actual_rust_candidate_workers": 13,
        "actual_rust_semantic_mismatch_count": 1036,
        "actual_rust_verified_passing_case_count": 8965,
        "rust_original_campaign_status": "FAIL",
        "rust_original_campaign_candidate_worker_count": 13,
        "rust_original_campaign_semantic_mismatch_count": 1036,
        "rust_original_campaign_verified_passing_case_count": 8965,
        "historical_rust_semantic_mismatch_count": 1087,
        "historical_rust_verified_passing_case_count": 7438,
        "rust_semantic_mismatch_reduction": 51,
        "rust_additional_verified_passing_cases": 1527,
        "rust_recovery_journal_sha256": RECOVERY_JOURNAL,
        "all_four_original_rust_targets_restored": True,
        "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "zig_v2_source_freeze_status": "SOURCE FROZEN",
        "zig_v2_new_matching_test_status": "NOT MEASURED",
        "zig_v2_new_candidate_workers": 0,
        "uncompressed_new_rust_matching_archive_opened_by_graph": False,
        "uncompressed_new_rust_matching_archive_bytes_read_by_graph": 0,
    })
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source_sha, digest(manifest_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") == "rust":
            family.update({
                "historical_v3_original_campaign":
                    copy.deepcopy(snapshot["rust_v3_original_campaign"]),
                "current_v4_original_campaign": copy.deepcopy(actual),
                "current_v4_original_campaign_status": "FAIL",
                "current_v4_original_campaign_candidate_worker_count": 13,
                "current_v4_original_campaign_semantic_mismatch_count": 1036,
                "current_v4_original_campaign_verified_passing_case_count": 8965,
                "current_v4_semantic_mismatch_reduction": 51,
                "current_v4_additional_verified_passing_cases": 1527,
                "qualified": False,
            })
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 32, "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_sha, len(own)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw), len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(image), len(image)),
        "previous_overview": prior,
        "snapshot": snapshot, "families": families,
        "preserved_v31_repository_evidence_owner_count": 151,
        "preserved_v31_authenticated_reference_path_count": 156,
        "new_rust_v4_original_campaign_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "authenticated_digest_addressed_history_paths": len(combined),
        "qualified_candidate_count": 0,
        "actual_rust_v4_original_campaign": copy.deepcopy(actual),
        "actual_rust_original_campaign": copy.deepcopy(actual),
        "historical_rust_v3_original_campaign":
            copy.deepcopy(snapshot["rust_v3_original_campaign"]),
        "rust_original_campaign_status": "FAIL",
        "rust_original_campaign_candidate_worker_count": 13,
        "rust_original_campaign_completed_suite_count": 13,
        "rust_original_campaign_case_execution_denominator": 31237,
        "rust_original_campaign_semantic_mismatch_count": 1036,
        "rust_original_campaign_verified_passing_case_count": 8965,
        "rust_original_campaign_infrastructure_failure_count": 0,
        "rust_original_campaign_candidate_qualified": False,
        "rust_original_campaign_receipt_status": "PASS",
        "rust_original_campaign_receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "rust_original_campaign_recovery_journal_sha256": RECOVERY_JOURNAL,
        "rust_original_campaign_all_four_original_targets_restored": True,
        "historical_rust_semantic_mismatch_count": 1087,
        "historical_rust_verified_passing_case_count": 7438,
        "rust_semantic_mismatch_reduction": 51,
        "rust_additional_verified_passing_cases": 1527,
        "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "zig_v2_source_freeze_status": "SOURCE FROZEN",
        "zig_v2_new_matching_test_status": "NOT MEASURED",
        "zig_v2_new_candidate_workers": 0,
        "uncompressed_new_rust_matching_archive_opened_by_graph": False,
        "uncompressed_new_rust_matching_archive_bytes_read_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", image),
    )


class Wall:
    """Physically stop every real operation during synthetic controls."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def __enter__(self) -> Wall:
        def forbid(name: str):
            def blocked(*_args: object, **_kwargs: object) -> object:
                self.blocked += 1
                raise GraphError("V32 source-only effect blocked: " + name)
            return blocked

        groups = (
            (builtins, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "unlink", "remove", "rename", "replace", "mkdir", "makedirs", "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text", "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                if hasattr(owner, name):
                    self.saved.append((owner, name, getattr(owner, name)))
                    setattr(owner, name, forbid(name))
        return self

    def __exit__(self, *_errors: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic() -> dict:
    campaign = lambda differences, passes: {
        "status": "FAIL", "actual_candidate_workers": 13,
        "completed_suite_count": 13, "semantic_mismatch_count": differences,
        "verified_passing_case_count": passes,
        "infrastructure_failure_count": 0, "candidate_qualified": False,
    }
    rows = [
        {"suite": f"history-{index}",
         "display_name": f"Historical original group {index + 1}",
         "case_execution_denominator": 2000,
         "mismatch_count": 1262 if index == 0 else 0}
        for index in range(13)
    ]
    archive = {
        "path": ARCHIVE[0], "sha256": ARCHIVE[1], "bytes": ARCHIVE[2],
        "device": ARCHIVE[3], "inode": ARCHIVE[4],
        "mode": "0600", "nlink": 1,
    }
    receipt_owner = {
        "path": RECEIPT[0], "sha256": RECEIPT[1], "bytes": RECEIPT[2],
        "device": RECEIPT[3], "inode": RECEIPT[4],
        "mode": "0600", "nlink": 1,
    }
    published = {
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "semantic_mismatch_count": 1036, "verified_passing_case_count": 8965,
    }
    proof = {
        "schema": SCHEMA + "-authenticated-complete-rust-v4-matching-failure",
        "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "family": "rust", "label": "phase2-v12-rust-flag-original-p0",
        "suite_count": 13, "completed_suite_count": 13,
        "case_execution_denominator": 31237, "private_waiver_count": 13,
        "actual_candidate_workers": 13, "semantic_mismatch_count": 1036,
        "verified_passing_case_count": 8965,
        "infrastructure_failure_count": 0, "candidate_qualified": False,
        "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "historical_rust_semantic_mismatch_count": 1087,
        "historical_rust_verified_passing_case_count": 7438,
        "semantic_mismatch_reduction": 51,
        "additional_verified_passing_case_count": 1527,
        "archive": archive, "receipt": receipt_owner,
        "publication_receipt": published,
        "actual_v12_build_archive_sha256": BUILD_ARCHIVE,
        "actual_v12_build_receipt_sha256": BUILD_RECEIPT,
        "corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "corrected_bridge_source_sha256": BRIDGE_DERIVED,
        "recovery_journal_sha256": RECOVERY_JOURNAL,
        "restored_original_targets": {
            "bridge_source": {}, "adapter": {}, "engine": {}, "bridge": {},
        },
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "original_canonical_targets_inspected_by_graph": False,
        "historical_evidence_owner_count_before_publication": 151,
        "historical_authenticated_reference_count_before_publication": 156,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": 153,
        "resulting_authenticated_reference_count": 158,
        "uncompressed_archive_sha256": PLAIN_SHA,
        "uncompressed_archive_bytes": PLAIN_BYTES,
        "uncompressed_archive_opened_by_graph": False,
        "uncompressed_archive_bytes_read_by_graph": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "baseline_passed": 31237, "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v31_repository_evidence_owner_count": 151,
        "preserved_v31_digest_addressed_history_path_count": 156,
        "new_rust_v4_original_campaign_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 153,
        "all_digest_addressed_history_path_count": 158,
        "rust_v3_original_campaign": campaign(1087, 7438),
        "c_v4_original_campaign": campaign(1230, 7325),
        "zig_v2_original_campaign": campaign(2172, 2847),
        "c_v10_repaired_original_campaign": {
            **campaign(1262, 7325), "suite_results": rows,
        },
        "rust_v4_original_campaign": proof,
        "rust_v4_original_campaign_status": "FAIL",
        "rust_v4_original_campaign_actual_candidate_workers": 13,
        "rust_v4_original_campaign_semantic_mismatch_count": 1036,
        "rust_v4_original_campaign_verified_passing_case_count": 8965,
        "rust_v4_original_campaign_infrastructure_failure_count": 0,
        "rust_v4_original_campaign_candidate_qualified": False,
        "rust_v4_semantic_mismatch_reduction": 51,
        "rust_v4_additional_verified_passing_cases": 1527,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "zig_v2_source_freeze_status": "SOURCE FROZEN",
        "zig_v2_new_matching_test_status": "NOT MEASURED",
        "zig_v2_new_candidate_workers": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED", "hidden_cases_read": 0,
        "performance_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def forged(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        if value == "FAIL":
            return "PASS"
        if value in ("NOT MEASURED", "NOT RUN"):
            return "MEASURED"
        return value + "-forged"
    if type(value) is dict:
        return {}
    if type(value) is list:
        return value[:-1]
    return "forged"


def self_test() -> dict:
    runtime()
    with Wall() as wall:
        base = synthetic()
        validate(base)
        rejected = 0

        def reject(attack: dict, label: str) -> None:
            nonlocal rejected
            try:
                validate(attack)
            except (GraphError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise GraphError("accepted hostile V32 evidence: " + label)

        top = (
            "full_case_denominator", "suite_count", "baseline_passed",
            "frozen_independent_engine_family_count", "qualified_candidate_count",
            "preserved_v31_repository_evidence_owner_count",
            "preserved_v31_digest_addressed_history_path_count",
            "new_rust_v4_original_campaign_repository_evidence_owner_count",
            "all_actual_candidate_and_native_evidence_owner_count",
            "all_digest_addressed_history_path_count",
            "rust_v4_original_campaign_status",
            "rust_v4_original_campaign_actual_candidate_workers",
            "rust_v4_original_campaign_semantic_mismatch_count",
            "rust_v4_original_campaign_verified_passing_case_count",
            "rust_v4_original_campaign_infrastructure_failure_count",
            "rust_v4_original_campaign_candidate_qualified",
            "rust_v4_semantic_mismatch_reduction",
            "rust_v4_additional_verified_passing_cases",
            "additional_signature_frozen_case_count",
            "additional_signature_reference_status",
            "additional_signature_reference_cases_executed",
            "zig_v2_source_freeze_status", "zig_v2_new_matching_test_status",
            "zig_v2_new_candidate_workers", "performance", "memory",
            "confidence_intervals", "hidden_cases_read", "performance_files_read",
            "clock_samples", "timing_trials_run",
            "final_comparison_planned_case_count", "final_comparison_cases_generated",
            "final_holdout_opened", "winner_selected",
        )
        for key in top:
            attack = copy.deepcopy(base)
            attack[key] = forged(attack[key])
            reject(attack, "top-" + key)
        for family in (
            "rust_v3_original_campaign", "c_v4_original_campaign",
            "zig_v2_original_campaign",
        ):
            for key in base[family]:
                attack = copy.deepcopy(base)
                attack[family][key] = forged(attack[family][key])
                reject(attack, family + "-" + key)
        actual = base["rust_v4_original_campaign"]
        for key in actual:
            attack = copy.deepcopy(base)
            attack["rust_v4_original_campaign"][key] = forged(actual[key])
            reject(attack, "actual-rust-v4-" + key)
        for name in ("archive", "receipt", "publication_receipt"):
            for key, value in actual[name].items():
                attack = copy.deepcopy(base)
                attack["rust_v4_original_campaign"][name][key] = forged(value)
                reject(attack, name + "-" + key)
        alias = copy.deepcopy(base)
        alias["rust_v4_original_campaign"]["receipt"]["device"] = ARCHIVE[3]
        alias["rust_v4_original_campaign"]["receipt"]["inode"] = ARCHIVE[4]
        reject(alias, "aliased-archive-receipt-inodes")
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"31,237", b"153 / 158", b"1,036", b"8,965", b"1,087",
            b"7,438", b"51 fewer", b"+1,527", b"1,230", b"7,325",
            b"2,172", b"2,847", b"NOT COMPATIBLE", b"REFERENCE NOT RUN",
            b"SOURCE FROZEN; NOT TESTED", b"NOT MEASURED", b"4,194,304",
            b"still not compatible", b"historical", b"remain compressed",
        ):
            need(phrase.lower() in picture.lower(),
                 "reject a graph inventing compatibility, matching, or speed")
        effects = (
            lambda: builtins.open("forbidden-v32"),
            lambda: os.open("forbidden-v32", os.O_RDONLY),
            lambda: os.stat("forbidden-v32-native"),
            lambda: subprocess.run(("forbidden-v32",)),
            lambda: importlib.import_module("candidates.rust_candidate"),
            lambda: socket.socket(), lambda: tempfile.mkdtemp(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for action in effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("a V32 source-only external effect was not blocked")
        need(wall.blocked == len(effects), "block all nine actual external-effect probes")
        need(rejected >= 120, "exercise actual failure, archive, owner, and holdout forgery")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "status": "PASS", "version": 32, "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "suite_count": 13, "full_case_denominator": 31237,
            "private_waiver_count": 13, "qualified_candidate_count": 0,
            "preserved_v31_repository_evidence_owner_count": 151,
            "preserved_v31_authenticated_reference_count": 156,
            "new_rust_v4_matching_evidence_owner_count": 2,
            "repository_evidence_owner_count": 153,
            "authenticated_digest_addressed_history_paths": 158,
            "rust_candidate_status": "FAIL", "rust_candidate_workers": 13,
            "rust_semantic_mismatch_count": 1036,
            "rust_verified_passing_case_count": 8965,
            "historical_rust_semantic_mismatch_count": 1087,
            "historical_rust_verified_passing_case_count": 7438,
            "rust_semantic_mismatch_reduction": 51,
            "rust_additional_verified_passing_cases": 1527,
            "c_semantic_mismatch_count": 1230,
            "c_verified_passing_case_count": 7325,
            "zig_semantic_mismatch_count": 2172,
            "zig_verified_passing_case_count": 2847,
            "additional_signature_frozen_case_count": 50,
            "additional_signature_reference_status": "NOT RUN",
            "additional_signature_reference_cases_executed": 0,
            "zig_v2_matching_test_status": "NOT MEASURED",
            "zig_v2_new_candidate_workers": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_candidate_imports": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_activations": 0,
            "canonical_target_reads": 0, "canonical_target_stats": 0,
            "uncompressed_c_matching_archive_bytes_read": 0,
            "uncompressed_rust_matching_archive_bytes_read": 0,
            "uncompressed_zig_matching_archive_bytes_read": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "workspace_mutations": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(
        path in allowed and type(raw) is bytes and 0 < len(raw) <= LIMIT,
        "publish only the three exclusively reserved authentic V32 graph files",
    )
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        view = memoryview(raw)
        while view:
            count = os.write(descriptor, view)
            need(type(count) is int and count > 0, "reject incomplete V32 publication")
            view = view[count:]
        os.fsync(descriptor)
        state = os.fstat(descriptor)
        need(
            state.st_uid == os.geteuid() and state.st_nlink == 1
            and state.st_size == len(raw)
            and stat.S_IMODE(state.st_mode) == 0o600,
            "reject an altered, foreign, linked, or unprivate V32 graph owner",
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
    observed, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(observed == raw, "re-read the exact exclusively published V32 graph owner")


def result(
    source: str, archive: str, receipt: str,
    outputs: dict[str, bytes], written: bool, suffix: str,
) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 32, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_rust_v4_matching_failure_archive_sha256": archive,
        "actual_rust_v4_matching_failure_receipt_sha256": receipt,
        "suite_count": 13, "full_case_denominator": 31237,
        "private_waiver_count": 13, "qualified_candidate_count": 0,
        "preserved_v31_repository_evidence_owner_count": 151,
        "preserved_v31_authenticated_reference_count": 156,
        "new_actual_rust_v4_matching_evidence_owner_count": 2,
        "repository_evidence_owner_count": 153,
        "authenticated_digest_addressed_history_paths": 158,
        "rust_matching_status": "FAIL", "rust_candidate_workers": 13,
        "rust_completed_suite_count": 13,
        "rust_semantic_mismatch_count": 1036,
        "rust_verified_passing_case_count": 8965,
        "rust_infrastructure_failure_count": 0,
        "historical_rust_semantic_mismatch_count": 1087,
        "historical_rust_verified_passing_case_count": 7438,
        "rust_semantic_mismatch_reduction": 51,
        "rust_additional_verified_passing_cases": 1527,
        "rust_publication_status": "PASS",
        "rust_publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "rust_recovery_journal_sha256": RECOVERY_JOURNAL,
        "all_four_original_rust_targets_restored": True,
        "c_matching_status": "FAIL", "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_matching_status": "FAIL", "zig_semantic_mismatch_count": 2172,
        "zig_verified_passing_case_count": 2847,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "zig_v2_source_freeze_status": "SOURCE FROZEN",
        "zig_v2_new_matching_test_status": "NOT MEASURED",
        "zig_v2_new_candidate_workers": 0,
        "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "outputs_written": written,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "uncompressed_c_matching_archive_opened": False,
        "uncompressed_c_matching_archive_bytes_read": 0,
        "uncompressed_rust_matching_archive_opened": False,
        "uncompressed_rust_matching_archive_bytes_read": 0,
        "uncompressed_zig_matching_archive_opened": False,
        "uncompressed_zig_matching_archive_bytes_read": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED",
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
    for name in (
        "--source-sha256", "--campaign-archive-sha256",
        "--campaign-receipt-sha256", "--inputs-sha256",
        "--summary-sha256", "--svg-sha256",
    ):
        parser.add_argument(name)
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(
                all(getattr(args, name) is None for name in (
                    "source_sha256", "campaign_archive_sha256",
                    "campaign_receipt_sha256", "inputs_sha256",
                    "summary_sha256", "svg_sha256",
                )),
                "synthetic source-only controls never accept real evidence or publication",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "actual V32 renderer")
        archive = checked(args.campaign_archive_sha256, "actual Rust matching failure archive")
        receipt = checked(args.campaign_receipt_sha256, "actual Rust matching failure receipt")
        _snapshot, pairs = build(source, archive, receipt)
        outputs = dict(pairs)
        if args.render:
            need(
                args.inputs_sha256 is None and args.summary_sha256 is None
                and args.svg_sha256 is None,
                "render exclusively generated V32 outputs exactly once",
            )
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, True, "-published")))
            return 0
        fixed = {
            OUTPUT + ".inputs.json": checked(args.inputs_sha256, "frozen V32 inputs"),
            OUTPUT + ".json": checked(args.summary_sha256, "frozen V32 summary"),
            OUTPUT + ".svg": checked(args.svg_sha256, "frozen V32 SVG"),
        }
        for path, fingerprint in fixed.items():
            observed, _ = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(observed == outputs[path], "independently reproduce the exact committed V32 graph")
        sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, False, "-read-only-frozen-context")))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError, KeyError,
            AttributeError, struct.error) as error:
        sys.stderr.write("current V32 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
